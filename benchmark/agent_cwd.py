"""The agent's working directory: one per run, and the canary that proves it.

The benchmark runs of 2026-10-28 and 2026-10-29 mounted **one** host
directory as the agent's working directory (``/agent_cwd``) for every run
of both arms, so a run's agent could read the files another run wrote.
The runner now gives every run its own directory
(``scripts/run_arm.py``) and removes it with the run.

This module holds the two rules and the canary:

``make_agent_cwd``
    a fresh, empty directory per run, or the shared one when the caller
    asks for it (the development runs share it to keep the pybiomart
    cache).
``cleanup_agent_cwd``
    the per-run directory is removed with the run; the shared one is
    never removed.
``canary``
    the check that the isolation holds: a container writes a canary file
    into the working directory it is given, and a second container,
    given a **different** working directory, must not see it.  The
    negative control runs the second container against the **same**
    directory, where the canary **must** be visible - otherwise the
    check would pass for the wrong reason.

The canary needs the image; it never modifies it, and it writes only
into throw-away directories of its own.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

CANARY_NAME = "alloagent_canary.txt"
CONTAINER_PYTHON = "/opt/conda/envs/alloagent_e1/bin/python"


def make_agent_cwd(shared: bool, label: str = "run") -> Path:
    """The working directory of a run: fresh per run, or the shared one."""
    if shared:
        path = Path(tempfile.gettempdir()) / "alloagent_agent_cwd"
        path.mkdir(parents=True, exist_ok=True)
        return path
    safe = "".join(char if char.isalnum() or char in "-_" else "_" for char in label)
    return Path(tempfile.mkdtemp(prefix=f"alloagent_agent_cwd_{safe}_"))


def cleanup_agent_cwd(path: Path, shared: bool) -> None:
    """Remove the per-run working directory; never the shared one."""
    if shared:
        return
    shutil.rmtree(path, ignore_errors=True)


def _write_canary(directory: Path) -> None:
    script = (
        "import pathlib,sys;"
        f"p=pathlib.Path('/agent_cwd/{CANARY_NAME}');"
        "p.write_text('canary');"
        "print('wrote', p);"
        "sys.stdout.flush()"
    )
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--entrypoint",
            CONTAINER_PYTHON,
            "-v",
            f"{directory.as_posix()}:/agent_cwd",
            "alloagent-eval:v6",
            "-c",
            script,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _list_working_directory(directory: Path) -> list[str]:
    script = (
        "import os,sys;"
        "print('\\n'.join(sorted(os.listdir('/agent_cwd'))));"
        "sys.stdout.flush()"
    )
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--entrypoint",
            CONTAINER_PYTHON,
            "-v",
            f"{directory.as_posix()}:/agent_cwd",
            "alloagent-eval:v6",
            "-c",
            script,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def canary(image: str = "alloagent-eval:v6") -> dict:
    """Prove that two runs do not share the agent's working directory.

    The check has three parts, and the negative control comes first: the
    canary **must** be visible in the directory that wrote it, otherwise
    the check would pass for the wrong reason.  Then the canary must not
    be visible to a second run of the **other** arm, nor to a second run
    of the **same** arm, and neither of them may see a sibling run's
    folder (the mount is the run's own directory and nothing else).
    """
    writer = make_agent_cwd(shared=False, label="canary_writer")
    other_arm = make_agent_cwd(shared=False, label="canary_other_arm")
    same_arm = make_agent_cwd(shared=False, label="canary_same_arm")
    try:
        _write_canary(writer)
        control = _list_working_directory(writer)
        other = _list_working_directory(other_arm)
        same = _list_working_directory(same_arm)
        return {
            "canary": CANARY_NAME,
            "visible_in_the_writing_directory": CANARY_NAME in control,
            "visible_in_another_directory": CANARY_NAME in other,
            "visible_in_the_same_arm_directory": CANARY_NAME in same,
            "the_other_directory_is_empty": not other,
            "the_same_arm_directory_is_empty": not same,
            "a_sibling_folder_is_visible": any(
                name.startswith("alloagent_agent_cwd_canary_") for name in other + same
            ),
            "passed": (
                CANARY_NAME in control
                and CANARY_NAME not in other
                and CANARY_NAME not in same
                and not other
                and not same
            ),
        }
    finally:
        for path in (writer, other_arm, same_arm):
            cleanup_agent_cwd(path, shared=False)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--image", default="alloagent-eval:v6")
    parser.add_argument("--out", help="the evidence as JSON")
    args = parser.parse_args()
    result = canary(args.image)
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        print("FAILED: the agent working directory is shared between runs")
        return 1
    print("the agent working directory is per run: the canary is not visible to another run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
