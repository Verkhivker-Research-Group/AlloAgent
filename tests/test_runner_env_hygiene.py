"""Runner hygiene tests.

Verify that scripts/run_arm.py:
  - Writes the temporary env-file OUTSIDE the repository
    (in the OS temp dir, not under the repo tree).
  - Cleans up the env-file on normal exit and on exception.
  - Does not leave any .env files inside the repo even if the
    docker subprocess raises.
  - Excludes scripts/.run/ via .dockerignore.
  - Extracts only MINIMAX_*/BIOMNI_* keys from the source.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import run_arm  # noqa: E402


@pytest.fixture(autouse=True)
def _neutralise_windows_acl(monkeypatch):
    """Avoid touching real ACLs in tests (icacls is slow + needs admin)."""
    monkeypatch.setattr(run_arm, "_restrict_windows_acl", lambda p: None)


def test_default_host_tmp_dir_is_outside_repo():
    try:
        run_arm._HOST_TMP_DIR.relative_to(REPO)
    except ValueError:
        return
    pytest.fail(
        f"_HOST_TMP_DIR must live outside the repo; was {run_arm._HOST_TMP_DIR}"
    )


def test_env_file_cleaned_on_normal_exit(tmp_path):
    host_tmp = tmp_path / "host_tmp"
    with run_arm._env_file(
        "alloagent", {"MINIMAX_API_KEY": "x"}, host_tmp_dir=host_tmp
    ) as p:
        assert p.exists()
        assert "scripts" not in p.parts or ".run" not in p.parts
        try:
            p.relative_to(REPO)
        except ValueError:
            pass
        else:
            pytest.fail(f"env-file is inside the repo: {p}")
    assert not p.exists()


def test_env_file_cleaned_on_exception(tmp_path):
    host_tmp = tmp_path / "host_tmp"
    saved_path = None
    with pytest.raises(RuntimeError):
        with run_arm._env_file(
            "alloagent", {"MINIMAX_API_KEY": "x"}, host_tmp_dir=host_tmp
        ) as p:
            saved_path = p
            assert p.exists()
            raise RuntimeError("simulated failure")
    assert saved_path is not None
    assert not saved_path.exists()


def test_env_file_is_owner_only_filename(tmp_path):
    """mkstemp guarantees a unique, race-safe name with prefix alloagent_env_."""
    host_tmp = tmp_path / "host_tmp"
    with run_arm._env_file(
        "alloagent", {"MINIMAX_API_KEY": "x"}, host_tmp_dir=host_tmp
    ) as p:
        assert p.name.startswith("alloagent_env_alloagent_")
        assert p.suffix == ".env"


def test_no_env_leftover_in_repo_when_docker_run_raises(
    tmp_path, monkeypatch
):
    """If docker run raises, the _env_file context manager still cleans up;
    no .env file may appear anywhere inside the repo."""
    fake_env = tmp_path / ".env"
    fake_env.write_text("MINIMAX_API_KEY=test\n", encoding="utf-8")

    def fake_run(*args, **kwargs):
        raise RuntimeError("simulated docker failure")

    monkeypatch.setattr(run_arm.subprocess, "run", fake_run)

    log_path = tmp_path / "log.txt"
    with pytest.raises(RuntimeError):
        run_arm.main([
            "--arm", "alloagent",
            "--image", "alloagent-dev:v4",
            "--env-source", str(fake_env),
            "--log", str(log_path),
        ])

    forbidden = REPO / "scripts" / ".run"
    if forbidden.exists():
        leaked = [p for p in forbidden.iterdir() if p.suffix == ".env"]
        assert not leaked, f"env-files leaked under repo: {leaked}"
    leaked_root = [p for p in REPO.glob("*.env") if p.is_file()]
    assert not leaked_root, f"env-files leaked into repo root: {leaked_root}"


def test_no_env_leftover_in_repo_when_docker_returns_nonzero(
    tmp_path, monkeypatch
):
    """Even when docker exits cleanly with a nonzero exit code, no
    env-file remains anywhere under the repo."""
    fake_env = tmp_path / ".env"
    fake_env.write_text("MINIMAX_API_KEY=test\n", encoding="utf-8")

    class FakeProc:
        returncode = 5

    monkeypatch.setattr(
        run_arm.subprocess,
        "run",
        lambda *args, **kwargs: FakeProc(),
    )

    log_path = tmp_path / "log.txt"
    rc = run_arm.main([
        "--arm", "alloagent",
        "--image", "alloagent-dev:v4",
        "--env-source", str(fake_env),
        "--log", str(log_path),
    ])
    assert rc == 5

    forbidden = REPO / "scripts" / ".run"
    if forbidden.exists():
        leaked = [p for p in forbidden.iterdir() if p.suffix == ".env"]
        assert not leaked, f"env-files leaked under repo: {leaked}"


def test_extract_env_filters_by_prefix(tmp_path):
    src = tmp_path / ".env"
    src.write_text(
        "MINIMAX_API_KEY=secret1\n"
        "BIOMNI_API_KEY=secret2\n"
        "OTHER_KEY=ignored\n"
        "# comment\n"
        "=orphan\n"
        "MINIMAX_FOO=bar\n",
        encoding="utf-8",
    )
    out = run_arm.extract_env(src)
    assert set(out.keys()) == {"MINIMAX_API_KEY", "BIOMNI_API_KEY", "MINIMAX_FOO"}
    assert "OTHER_KEY" not in out


def test_extract_env_strips_quotes(tmp_path):
    src = tmp_path / ".env"
    src.write_text(
        'MINIMAX_API_KEY="quoted_value"\n'
        "BIOMNI_KEY='single_quoted'\n",
        encoding="utf-8",
    )
    out = run_arm.extract_env(src)
    assert out["MINIMAX_API_KEY"] == "quoted_value"
    assert out["BIOMNI_KEY"] == "single_quoted"


def test_extract_env_missing_file_returns_empty(tmp_path):
    out = run_arm.extract_env(tmp_path / "nope.env")
    assert out == {}


def test_dockerignore_excludes_scripts_run():
    """Excluding scripts/.run/ from .dockerignore stops anyone who
    accidentally recreates the in-repo scratch dir from baking env-files
    into a built image."""
    di = REPO / ".dockerignore"
    assert di.exists(), "no .dockerignore found at repo root"
    text = di.read_text(encoding="utf-8")
    lines = {
        line.strip().rstrip("/")
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    assert "scripts/.run" in lines, (
        f".dockerignore must exclude scripts/.run; got lines: {sorted(lines)}"
    )