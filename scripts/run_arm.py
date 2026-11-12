# run_arm.py - moved from build_logs/_run_arm.py
# (c) 2026 AlloAgent-v2 contributors. Run via:
# docker run --rm -v '<HOME>\Documents\CPSC\AlloAgent-v2':/workspace -v '<HOME>\Documents\CPSC\AlloAgent-v2'\data\clinvar:/data/clinvar:ro -v'<HOME>\Documents\CPSC\AlloAgent-v2'\data\alphamissense:/data/alphamissense:ro -w /workspace -e REQUIRE_REAL_DATA=1 -e RUN_REAL_NETWORK=1 -e ALLOAGENT_ENV_SOURCE=<path-to-.env.extracted> alloagent-dev:v4 python /workspace/run_arm.py

"""Run an arm of the AlloAgent-v2 test suite in the Docker
container.

Mirrors scripts/run_tests_container.{sh,ps1} but uses Python for
path handling (avoids bash-on-Windows path-translation issues).
Reads MINIMAX_*/BIOMNI_* variables from $ALLOAGENT_ENV_SOURCE
into a temp file OUTSIDE the repository, then runs the existing
pytest command via docker run --env-file. The temp file lives in
the OS temp dir (default $TEMP/alloagent_runner/), has owner-only
permissions (best-effort icacls on Windows), and is ALWAYS
deleted via a context manager's try/finally on every exit path.

Args:
  --arm         "alloagent" or "baseline" (changes the image's
                workspace contents; for baseline, the caller
                must have already swapped the workspace contents
                to the baseline branch).
  --image       Docker image tag (default alloagent-dev:v4).
  --env-source  Path to host .env file (defaults to
                $ALLOAGENT_ENV_SOURCE or
                C:<HOME>/Documents/CPSC/Biolab/.env.extracted).
  --log         Output log path (default
                build_logs/_run_<arm>_v4_reb.log).
"""
from __future__ import annotations

import argparse
import os
import sys
import shutil
import subprocess
import tempfile
import time
import urllib.parse
from contextlib import contextmanager
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home, home_dir  # noqa: E402
from typing import Iterator

DEFAULT_ENV = str(expand_home(r"<HOME>\Documents\CPSC\Biolab\.env.extracted"))
REPO = expand_home(r"<HOME>\Documents\CPSC\AlloAgent-v2")
BIOLAB_UNIX_ROOT = "/c" + str(home_dir()).replace("\\", "/")

# Where the runner writes its temporary env-file. MUST be OUTSIDE
# the repository so a stray run cannot leak credentials into the
# repo tree. Override in tests via monkeypatch.
_HOST_TMP_DIR = Path(tempfile.gettempdir()) / "alloagent_runner"


def extract_env(source: Path, allow_prefixes=("MINIMAX_", "BIOMNI_")) -> dict:
    """Read source, return only keys matching the allow prefixes."""
    out: dict[str, str] = {}
    if not source.is_file():
        return out
    for raw in source.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if not (key.startswith(allow_prefixes)):
            continue
        # Strip surrounding quotes.
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        out[key] = val
    return out


def _restrict_windows_acl(path: Path) -> None:
    if os.name != "nt":
        return
    username = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if not username:
        return
    try:
        subprocess.run(
            ["icacls", str(path),
             "/inheritance:r",
             "/grant:r", f"{username}:F"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


@contextmanager
def _env_file(arm: str, env_vars: dict, host_tmp_dir: Path | None = None) -> Iterator[Path]:
    if host_tmp_dir is None:
        host_tmp_dir = _HOST_TMP_DIR
    host_tmp_dir.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(
        prefix=f"alloagent_env_{arm}_",
        suffix=".env",
        dir=str(host_tmp_dir),
    )
    tmp_env_path = Path(name)
    _restrict_windows_acl(tmp_env_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for k, v in env_vars.items():
                fh.write(f"{k}={v}\n")
        yield tmp_env_path
    finally:
        try:
            os.unlink(tmp_env_path)
        except FileNotFoundError:
            pass


def _image_has_egress_script(image: str) -> bool:
    """Does the image carry the in-container egress script?

    The v6 image carries no /egress.sh and no iptables, so the
    restricted egress is enforced by the internal docker network and the
    egress proxy. The check costs one short docker call per run.
    """
    result = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "/bin/sh", image,
         "-c", "test -f /egress.sh && echo yes || echo no"],
        capture_output=True, text=True, timeout=120,
    )
    return "yes" in (result.stdout or "")


def runs_binds(docker_args: list[str]) -> list[str]:
    """The binds that expose /runs inside the container."""
    return [arg for arg in docker_args if ":/runs" in arg]


def redact_arg(arg: str) -> str:
    """A docker argument with anything that looks like a secret masked."""
    lowered = arg.lower()
    if any(word in lowered for word in ("key", "token", "secret", "password", "bearer")):
        head, sep, _ = arg.partition("=")
        return head + sep + "***" if sep else "***"
    return arg


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--arm", required=True, choices=("alloagent", "baseline"))
    p.add_argument("--image", default="alloagent-dev:v4")
    p.add_argument("--env-source", default=os.environ.get("ALLOAGENT_ENV_SOURCE") or DEFAULT_ENV)
    p.add_argument("--log",
                   default=None,
                   help="Path for full stdout/stderr log")
    p.add_argument("--workspace", default=str(REPO),
                   help="Path to mount as /workspace (caller-prepped)")
    p.add_argument("--data-root", default=None,
                   help="Directory holding the data/ tree to mount at "
                        "/data/* (default: <workspace>/data). The baseline "
                        "arm uses a separate workspace but the same data.")
    p.add_argument("--run-real-network", default="1")
    p.add_argument(
        "--egress",
        choices=("open", "restricted"),
        default="open",
        help=(
            "'open' is the normal network. 'restricted' lets the container "
            "reach ONLY the LLM endpoint host: the container gets NET_ADMIN, "
            "an iptables OUTPUT policy is applied by "
            "scripts/restricted_egress.sh, and the local structure cache is "
            "mounted read-only."
        ),
    )
    p.add_argument(
        "--structure-cache",
        default=None,
        help=(
            "A host directory with the benchmark structures, mounted "
            "read-only at /data/structures in BOTH arms."
        ),
    )
    p.add_argument(
        "--dev-prompts",
        action="store_true",
        help=(
            "Run the arm D development prompts (scripts/run_dev_prompts.py) "
            "in the container instead of the test suite. Same env-file "
            "hygiene and same mounts, so no second code path can leak "
            "credentials."
        ),
    )
    p.add_argument(
        "--dev-prompts-out",
        default="/workspace/build_logs/dev_runs",
        help="Where the per-run JSONs are written (container path).",
    )
    p.add_argument(
        "--dev-prompts-script",
        default=None,
        help=(
            "Host path of the dev-prompt launcher to mount at "
            "/workspace/scripts/run_dev_prompts.py.  The baseline arm "
            "has no scripts/ directory, so the launcher is mounted in "
            "from this repository; it is the harness, not part of the "
            "arm's code."
        ),
    )
    p.add_argument(
        "--dev-prompts-prompts",
        default=None,
        help=(
            "Host path of the prompt table to mount at "
            "/harness/dev_prompts.md.  The baseline arm has no "
            "docs/dev_prompts.md, so the same table is mounted in."
        ),
    )
    p.add_argument(
        "--dev-prompts-data-path",
        default="/workspace/data",
        help=(
            "Data-lake path handed to the agent.  The baseline arm's "
            "A1 calls os.makedirs() on it, so it must not exist yet."
        ),
    )
    p.add_argument(
        "--no-data-mounts",
        action="store_true",
        help=(
            "Do not mount the data directories (the /data/* trees and the "
            "Biolab data lake).  Used for the capability gate: the baseline "
            "arm must not see the local curated data."
        ),
    )
    p.add_argument(
        "--workspace-read-only",
        action="store_true",
        help=(
            "Mount the arm's workspace read-only.  The baseline workspace "
            "was damaged by the agents of the earlier runs (53 tracked "
            "files deleted), and a damaged workspace breaks the next run "
            "before it starts.  The working directory of the run is the "
            "per-run /agent_cwd, so the agent does not need to write into "
            "the workspace."
        ),
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print the docker command and exit without starting the "
            "container.  The /runs binds are checked first: exactly one is "
            "allowed, so a run can never see another run's records."
        ),
    )
    p.add_argument(
        "--run-dir",
        default=None,
        help=(
            "A host directory OUTSIDE the repository where the run records, "
            "the answer texts and the traces are written.  In a benchmark "
            "run only the record directory of this run is mounted, read-write, "
            "at /runs/<arm>/<prompt_id>_r<repeat>, so the records of the two "
            "arms and of the sibling runs land in the same host directory "
            "without being visible to the other runs."
        ),
    )
    p.add_argument(
        "--no-pocketminer-env",
        action="store_true",
        help=(
            "Hide /opt/conda/envs/pocketminer_env behind an empty mount, so "
            "the arm cannot run the PocketMiner model at all."
        ),
    )
    p.add_argument(
        "--no-gpu-envs",
        action="store_true",
        help=(
            "Hide the GPU tool envs (/opt/conda/envs/boltz2_env and "
            "/opt/conda/envs/bioemu_env) behind empty mounts, so the arm "
            "cannot run Boltz-2 or BioEmu at all."
        ),
    )
    p.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        default=[],
        help=(
            "Extra arguments appended after the pytest command line "
            "(e.g. --pytest-args tests/test_B1_get_chembl_bioactivity.py -k "
            "regression). Lets a development run target a single affected "
            "test file while still going through this runner's env-file "
            "hygiene, so no second code path can leak credentials."
        ),
    )
    p.add_argument(
        "--benchmark",
        action="store_true",
        help=(
            "Run ONE benchmark prompt in the container (the benchmark "
            "harness, benchmark/run_benchmark.py) instead of the test suite."
        ),
    )
    p.add_argument(
        "--benchmark-script",
        default=None,
        help=(
            "Host path of the benchmark harness. It is mounted read-only "
            "at /harness/run_benchmark.py. The harness is the launcher, "
            "not part of the arm's code, so it is mounted in from the "
            "launch checkout for both arms."
        ),
    )
    p.add_argument(
        "--benchmark-module",
        default=None,
        help=(
            "Host path of benchmark/benchmark_launch.py, the shared helper "
            "module of the launch. It is mounted read-only at "
            "/harness/benchmark_launch.py next to the harness."
        ),
    )
    p.add_argument(
        "--benchmark-dir",
        default=None,
        help=(
            "Host path of the launch checkout's benchmark directory. It is "
            "mounted READ-ONLY at /launch/benchmark, so the prompt table, "
            "the checklists and the restricted prompt set are read from "
            "the checkout and never from a copy baked into the image."
        ),
    )
    p.add_argument(
        "--benchmark-prompt-id",
        default=None,
        help="the id of the prompt to run (one container runs one prompt)",
    )
    p.add_argument(
        "--benchmark-repeat",
        type=int,
        default=1,
        help="the repeat index of the run (the record directory is "
             "<prompt_id>_r<repeat>)",
    )
    p.add_argument(
        "--benchmark-prompt-source",
        choices=("benchmark", "file"),
        default="benchmark",
        help=(
            "'benchmark' reads the prompt from the mounted benchmark "
            "directory; 'file' reads it from --benchmark-prompt-file (used "
            "by the pipeline smoke, which runs a development prompt)."
        ),
    )
    p.add_argument(
        "--benchmark-prompt-file",
        default=None,
        help=(
            "Host path of a JSON list of {id, prompt} rows, mounted "
            "read-only at /harness/prompts.json."
        ),
    )
    p.add_argument(
        "--benchmark-out",
        default=None,
        help=(
            "The container path the records are written to (default "
            "/runs/<arm> when --run-dir is given)."
        ),
    )
    p.add_argument(
        "--benchmark-data-path",
        default="/agent_cwd/data",
        help=(
            "The data-lake path handed to the agent in the benchmark mode. "
            "It must NOT be inside the mounted checkout: the agent creates "
            "it, and a file created in the checkout would dirty the launch "
            "commit."
        ),
    )
    p.add_argument(
        "--shared-agent-cwd",
        action="store_true",
        help=(
            "Mount ONE host directory as the agent's working directory for "
            "every run, instead of a fresh directory per run.  The shared "
            "directory is what the development runs used, and it keeps the "
            "pybiomart sqlite cache between runs.  It MUST NOT be used for "
            "a benchmark: a shared working directory lets one run read the "
            "files another run wrote, which breaks the arm isolation (the "
            "baseline arm read the curated ChEMBL records the alloagent arm "
            "had downloaded, through this directory)."
        ),
    )
    p.add_argument(
        "--egress-upstream-timeout-s",
        type=float,
        default=60.0,
        help=(
            "How long the egress proxy waits for the upstream connect to "
            "the LLM host. The provider throttles, and a throttled "
            "provider can delay the connect; a short timeout turned a "
            "slow provider into a connection error in the agent."
        ),
    )
    p.add_argument(
        "--egress-upstream-retries",
        type=int,
        default=3,
        help="How many times the egress proxy retries the upstream connect.",
    )
    p.add_argument(
        "--launch-tag",
        default=None,
        help="the launch tag the record has to carry",
    )
    p.add_argument(
        "--image-digest",
        default=None,
        help="the sha256 digest of the image, as docker reports it "
             "(sha256:...)",
    )
    p.add_argument(
        "--container-name",
        default=None,
        help=(
            "The name of the container.  The driver gives every run its own "
            "name, so a run that reaches the wall-clock cap can be killed "
            "by name."
        ),
    )
    p.add_argument(
        "--quota-probe",
        action="store_true",
        help=(
            "Make one minimal request to the provider to measure the quota "
            "and the rate-limit headers, then exit.  The key is read from "
            "the env file through the same env-file mechanism as a run, "
            "and the probe never prints it."
        ),
    )
    p.add_argument(
        "--quota-probe-script",
        default=None,
        help=(
            "Host path of the probe script "
            "(scripts/minimax_quota_check.py by default)."
        ),
    )
    p.add_argument(
        "--expected-sha256",
        default=None,
        help=(
            "A JSON object: the benchmark file name -> its expected "
            "sha256. The harness recomputes the hashes of the mounted "
            "files and refuses to run on a mismatch."
        ),
    )
    args = p.parse_args(argv)

    env_src = Path(args.env_source)
    env_vars = extract_env(env_src)
    print(f"[{time.strftime('%H:%M:%S')}] extracted {len(env_vars)} var(s) from {env_src}")
    for k in sorted(env_vars):
        v = env_vars[k]
        masked = f"<set, {len(v)} chars>" if v else "<empty>"
        print(f"  - {k}: {masked}")
    if args.run_real_network == "1" and "MINIMAX_API_KEY" not in env_vars:
        print("ERROR: RUN_REAL_NETWORK=1 but MINIMAX_API_KEY absent; aborting")
        return 3

    log_path = Path(args.log) if args.log else (REPO / "build_logs" / f"_run_{args.arm}_v4_reb.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with _env_file(args.arm, env_vars) as tmp_env_path:
        host_env_file = tmp_env_path.as_posix()

        if args.quota_probe:
            probe = (
                Path(args.quota_probe_script)
                if args.quota_probe_script
                else (Path(__file__).resolve().parents[1] / "scripts"
                      / "minimax_quota_check.py")
            )
            if not probe.is_file():
                print(f"ERROR: the quota probe script is missing: {probe}")
                return 2
            docker_args = [
                "docker", "run", "--rm",
                "--env-file", host_env_file,
                "-v", f"{probe.as_posix()}:/harness/minimax_quota_check.py:ro",
                "--entrypoint", "/opt/conda/envs/alloagent_e1/bin/python",
                args.image,
                "/harness/minimax_quota_check.py",
            ]
            print(f"[{time.strftime('%H:%M:%S')}] the quota probe (one request)")
            result = subprocess.run(
                docker_args, capture_output=True, text=True, timeout=300
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print(f"[{time.strftime('%H:%M:%S')}] the quota probe exited with "
                  f"{result.returncode}")
            return result.returncode

        biolab = expand_home(r"<HOME>\Documents\CPSC\Biolab")
        repo_root = Path(args.workspace)
        scored = biolab / "eval_ablation" / "scoring" / "scored_runs.csv"
        nullruns = biolab / "prep_reports" / "investigation" / "null_runs.csv"
        results = biolab / "results"
        blocklist = biolab / "prep_reports" / "benchmark_blocklist.tsv"
        data_root = Path(args.data_root) if args.data_root else repo_root / "data"
        data_alphamissense = data_root / "alphamissense"
        data_clinvar = data_root / "clinvar"
        data_cryptobench = data_root / "cryptobench"
        data_chembl = data_root / "chembl"
        # Biolab data lake (BioLiP pickles, CovInDB). Read-only, no
        # secrets. The ported allosteric/biolip tools read from here.
        biolab_data = biolab / "data" / "biomni_data"

        # The agent's code-execution node writes relative paths into the
        # working directory, so the working directory is kept outside the
        # repository.  It is a host-mounted directory: a container-local
        # one loses the pybiomart sqlite cache between runs (the suite
        # then takes twice as long), and docker creates a missing -w
        # directory as root, which the agent (appuser) cannot write to.
        # PYTHONPATH keeps /workspace importable (the tests import
        # `tests._real_data`).
        #
        # The directory is FRESH FOR EVERY RUN unless --shared-agent-cwd
        # is given.  A shared working directory is an isolation defect:
        # the agent of one run can read the files another run wrote, so
        # the baseline arm read the curated ChEMBL records that the
        # alloagent arm had downloaded in the same scenario (the run of
        # 2026-10-29, the restricted scenario).  The development runs may
        # share it (it keeps the pybiomart cache); a benchmark must not.
        if args.shared_agent_cwd:
            agent_cwd = Path(tempfile.gettempdir()) / "alloagent_agent_cwd"
            agent_cwd.mkdir(parents=True, exist_ok=True)
        else:
            label = args.arm
            if args.benchmark_prompt_id:
                label = f"{label}_{args.benchmark_prompt_id}_r{args.benchmark_repeat}"
            agent_cwd = Path(
                tempfile.mkdtemp(prefix=f"alloagent_agent_cwd_{label}_")
            )
        if not args.shared_agent_cwd and any(agent_cwd.iterdir()):
            print(f"ERROR: the per-run working directory is not empty: {agent_cwd}; aborting")
            return 2

        docker_args = [
            "docker", "run", "--rm",
            "--env-file", host_env_file,
            "-e", "REQUIRE_REAL_DATA=1",
            "-e", f"RUN_REAL_NETWORK={args.run_real_network}",
            "-e", "TMPDIR=/tmp",
            "-e", "HOME=/tmp",
            # The agent's code-execution node writes relative paths into
            # the working directory, so the working directory is kept
            # outside the repository; PYTHONPATH keeps /workspace
            # importable (the tests import `tests._real_data`).  /tmp is
            # used because docker creates a missing -w directory as
            # root, and the agent runs as appuser: it has to be able to
            # write there (pybiomart creates its sqlite cache in the
            # working directory at import time).
            "-e", "PYTHONPATH=/workspace",
            "-w", "/agent_cwd",
            "-v", f"{agent_cwd.as_posix()}:/agent_cwd",
            "-v", f"{args.workspace}:/workspace" + (":ro" if args.workspace_read_only else ""),
        ]

        if args.container_name:
            docker_args += ["--name", args.container_name]

        if args.no_data_mounts:
            docker_args += ["-e", "REQUIRE_REAL_DATA=0"]
        else:
            docker_args += [
                "-v", f"{scored}:/Biolab/eval_ablation/scoring/scored_runs.csv:ro",
                "-v", f"{nullruns}:/Biolab/prep_reports/investigation/null_runs.csv:ro",
                "-v", f"{results}:/Biolab/results:ro",
                "-v", f"{blocklist}:/workspace/Biolab/prep_reports/benchmark_blocklist.tsv:ro",
                "-v", f"{data_alphamissense}:/data/alphamissense:ro",
                "-v", f"{data_clinvar}:/data/clinvar:ro",
                "-v", f"{data_cryptobench}:/data/cryptobench:ro",
                "-v", f"{data_chembl}:/data/chembl:ro",
                "-v", f"{biolab_data}:/biolab_data:ro",
            ]

        if args.no_pocketminer_env:
            empty_env = Path(tempfile.gettempdir()) / "alloagent_empty_pocketminer_env"
            empty_env.mkdir(parents=True, exist_ok=True)
            # The weights are a FILE in the image, so they need an empty
            # file over them, not a directory.
            empty_file = Path(tempfile.gettempdir()) / "alloagent_empty_pocketminer_weights.sha256"
            empty_file.write_text("", encoding="utf-8")
            docker_args += [
                "-v", f"{empty_env.as_posix()}:/opt/conda/envs/pocketminer_env",
                # The model itself and the weights are hidden too: an
                # empty env stops the model from being run, but the
                # checkpoints would still be readable and copyable.
                "-v", f"{empty_env.as_posix()}:/opt/pocketminer",
                "-v", f"{empty_env.as_posix()}:/opt/ae-pocketminer",
                "-v", f"{empty_file.as_posix()}:/opt/pocketminer_weights.sha256",
            ]

        if args.no_gpu_envs:
            empty_gpu = Path(tempfile.gettempdir()) / "alloagent_empty_gpu_envs"
            empty_gpu.mkdir(parents=True, exist_ok=True)
            docker_args += [
                "-v", f"{empty_gpu.as_posix()}:/opt/conda/envs/boltz2_env",
                "-v", f"{empty_gpu.as_posix()}:/opt/conda/envs/bioemu_env",
            ]

        if args.structure_cache:
            cache = Path(args.structure_cache)
            if not cache.is_dir():
                print(f"ERROR: --structure-cache {cache} is not a directory; aborting")
                return 2
            docker_args += ["-v", f"{cache.as_posix()}:/data/structures:ro"]

        if args.run_dir:
            run_dir = Path(args.run_dir)
            if not run_dir.is_absolute() and not run_dir.is_dir():
                print(f"ERROR: --run-dir {run_dir} does not exist; create it first")
                return 2
            run_dir.mkdir(parents=True, exist_ok=True)
            if args.benchmark_prompt_id:
                # The record directory name comes from run_benchmark.py
                # (`<prompt_id>_r<repeat>` under `--benchmark-out`); only
                # this run's own directory may be visible inside the
                # container, never the other arm's records.
                record_name = f"{args.benchmark_prompt_id}_r{args.benchmark_repeat}"
                own_dir = run_dir / args.arm / record_name
                own_dir.mkdir(parents=True, exist_ok=True)
                docker_args += [
                    "-v",
                    f"{own_dir.as_posix()}:/runs/{args.arm}/{record_name}",
                ]
            else:
                docker_args += ["-v", f"{run_dir.as_posix()}:/runs"]
            dev_prompts_out = f"/runs/{args.arm}"
        else:
            dev_prompts_out = args.dev_prompts_out

        if args.egress == "restricted":
            egress_script = Path(__file__).resolve().parent / "egress_proxy.py"
            llm_base = os.environ.get(
                "BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1"
            )
            llm_host = urllib.parse.urlparse(llm_base).hostname or "api.minimax.io"
            llm_port = urllib.parse.urlparse(llm_base).port or 443
            network = "alloagent_egress_net"
            # The proxy container name carries the pid: the restricted
            # scenario runs several containers in parallel and they must
            # not fight over one proxy.
            proxy_name = f"alloagent_egress_proxy_{os.getpid()}"
            proxy_port = 8877
            subprocess.run(
                ["docker", "network", "create", "--internal", network],
                capture_output=True, text=True,
            )
            subprocess.run(
                ["docker", "rm", "-f", proxy_name], capture_output=True, text=True
            )
            subprocess.run(
                [
                    "docker", "run", "-d", "--name", proxy_name,
                    "--network", network, "--network", "bridge",
                    "-v", f"{egress_script.as_posix()}:/egress_proxy.py:ro",
                    "-e", f"ALLOAGENT_EGRESS_UPSTREAM_TIMEOUT_S={args.egress_upstream_timeout_s}",
                    "-e", f"ALLOAGENT_EGRESS_UPSTREAM_RETRIES={args.egress_upstream_retries}",
                    "--entrypoint", "/opt/conda/envs/alloagent_e1/bin/python",
                    args.image,
                    "/egress_proxy.py",
                    str(proxy_port), f"{llm_host}:{llm_port}",
                ],
                check=True,
            )
            docker_args += [
                "--network", network,
                "-e", f"HTTP_PROXY=http://{proxy_name}:{proxy_port}",
                "-e", f"HTTPS_PROXY=http://{proxy_name}:{proxy_port}",
                "-e", "NO_PROXY=",
            ]
            restricted_command = True
        else:
            restricted_command = False

        launcher = "/workspace/scripts/run_dev_prompts.py"
        prompts_file = "/workspace/docs/dev_prompts.md"
        if args.dev_prompts and args.dev_prompts_script:
            docker_args += [
                "-v",
                f"{Path(args.dev_prompts_script).as_posix()}:/harness/run_dev_prompts.py:ro",
            ]
            launcher = "/harness/run_dev_prompts.py"
        if args.dev_prompts and args.dev_prompts_prompts:
            docker_args += [
                "-v",
                f"{Path(args.dev_prompts_prompts).as_posix()}:/harness/dev_prompts.md:ro",
            ]
            prompts_file = "/harness/dev_prompts.md"

        # The benchmark mode: the harness and its shared module are
        # mounted read-only from the launch checkout, and the benchmark
        # inputs are mounted read-only too. Nothing of the launch comes
        # from the image.
        benchmark_out = args.benchmark_out
        if args.benchmark:
            if not (args.benchmark_script and args.benchmark_dir
                    and args.benchmark_prompt_id and args.launch_tag
                    and args.image_digest and args.expected_sha256):
                print("ERROR: --benchmark needs --benchmark-script, "
                      "--benchmark-module, --benchmark-dir, "
                      "--benchmark-prompt-id, --launch-tag, --image-digest "
                      "and --expected-sha256; aborting")
                return 2
            for host_path, container_path in (
                (args.benchmark_script, "/harness/run_benchmark.py"),
                (args.benchmark_module, "/harness/benchmark_launch.py"),
            ):
                if host_path:
                    docker_args += [
                        "-v", f"{Path(host_path).as_posix()}:{container_path}:ro",
                    ]
            docker_args += [
                "-v", f"{Path(args.benchmark_dir).as_posix()}:/launch/benchmark:ro",
            ]
            if args.benchmark_prompt_file:
                docker_args += [
                    "-v",
                    f"{Path(args.benchmark_prompt_file).as_posix()}:/harness/prompts.json:ro",
                ]
            if benchmark_out is None:
                benchmark_out = dev_prompts_out

        docker_args += [
            # The image's entrypoint is /bin/sh (inherited from the base
            # images the GPU envs were committed from), which would run
            # the python binary as a shell script; set it explicitly.
            "--entrypoint", "/opt/conda/envs/alloagent_e1/bin/python",
            args.image,
        ]

        command: list[str] = []
        if args.benchmark:
            command += [
                "/harness/run_benchmark.py",
                "--benchmark-dir", "/launch/benchmark",
                "--prompt-id", args.benchmark_prompt_id,
                "--repeat", str(args.benchmark_repeat),
                "--out", benchmark_out,
                "--launch-tag", args.launch_tag,
                "--image-digest", args.image_digest,
                "--expected-sha256", args.expected_sha256,
                "--workspace", "/workspace",
                "--data-path", args.benchmark_data_path,
            ]
            if args.benchmark_prompt_source == "file":
                command += [
                    "--prompt-source", "file",
                    "--prompt-file", "/harness/prompts.json",
                ]
        elif args.dev_prompts:
            command += [
                launcher,
                "--prompts", prompts_file,
                "--out", dev_prompts_out,
                "--data-path", args.dev_prompts_data_path,
            ]
        else:
            command += [
                "-m", "pytest", "/workspace/tests/",
                "--no-header", "-q", "-p", "no:cacheprovider",
            ] + list(args.pytest_args)

        if restricted_command and _image_has_egress_script(args.image):
            docker_args += ["/egress.sh"] + command
        else:
            if restricted_command:
                print("WARNING: the image carries no /egress.sh and no "
                      "iptables; the restricted egress is enforced by the "
                      "internal docker network and the egress proxy alone. "
                      "scripts/egress_gate.py measures that isolation.")
            docker_args += command

        binds = runs_binds(docker_args)
        if len(binds) != 1:
            print(f"ERROR: the container must have exactly one /runs bind, "
                  f"found {len(binds)}: {binds}")
            return 2
        if args.dry_run:
            print("[dry-run] the docker command (the secrets are masked):")
            for arg in list(docker_args) + list(command):
                print("    ", redact_arg(arg))
            return 0

        try:
            with log_path.open("w", encoding="utf-8") as logf:
                logf.write(f"# runner args:\n{docker_args}\n\n")
                print(f"[{time.strftime('%H:%M:%S')}] launching docker run, log -> {log_path}")
                t0 = time.time()
                proc = subprocess.run(docker_args, stdout=logf, stderr=subprocess.STDOUT, text=True)
                elapsed = time.time() - t0
                logf.write(f"\n# pytest+docker elapsed: {elapsed:.2f}s ; exit={proc.returncode}\n")
                print(f"[{time.strftime('%H:%M:%S')}] pytest exit code: {proc.returncode}, elapsed {elapsed:.1f}s")
                return proc.returncode
        finally:
            if restricted_command:
                subprocess.run(["docker", "rm", "-f", proxy_name],
                               capture_output=True, text=True)
            if not args.shared_agent_cwd:
                # The per-run working directory is removed with the run: it
                # is a scratch area, and the run's evidence is the record
                # the runner wrote (run.json, summary.json, answer.txt,
                # trace.txt) in the run directory.
                shutil.rmtree(agent_cwd, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
