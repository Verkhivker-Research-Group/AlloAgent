"""The shared helpers of the benchmark launch.

This module is deliberately dependency-free and import-safe both on the
host (the driver) and inside the container (the per-run harness), so the
two sides cannot disagree about what a run record has to carry or about
what a provider error means.

Three things live here:

1. **The benchmark files and their hashes.** The three benchmark inputs
   (the prompt table, the validated checklists and the restricted
   prompt set) are read from a launch checkout that is mounted
   read-only, never from a copy baked into the image. Their sha256 are
   computed here and carried in every run record, so a record says
   exactly which inputs produced it.

2. **The provider-error classification.** A quota-exhausted or a
   rate-limit answer is a *pause*, not a failed attempt: the driver
   stops launching new runs, waits, and resumes. The distinction is
   made on the text of the provider's answer (the status code alone is
   not enough: a 429 carries a body that says whether the daily quota
   is gone or the request rate was too high).

3. **The record provenance contract.** Every run record has to carry
   the launch tag, the commit, the image digest, the three benchmark
   hashes and a clean working tree. `validate_record_provenance` is the
   single implementation of that contract; the guard test and the
   driver both call it.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable, Mapping

# The three benchmark inputs, by their file name inside the benchmark
# directory. Their order is fixed: it is the order the hashes are
# written in.
BENCHMARK_FILES: tuple[str, ...] = (
    "benchmark_draft.json",
    "checklists.json",
    "restricted_prompt_set.json",
)

# The launch manifest keys that every run record has to carry.
REQUIRED_MANIFEST_KEYS: tuple[str, ...] = (
    "launch_tag",
    "commit",
    "image_digest",
    "benchmark_sha256",
)


def sha256_file(path: Path | str) -> str:
    """The sha256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_for_dir(benchmark_dir: Path | str) -> dict[str, str]:
    """The sha256 of the three benchmark inputs in `benchmark_dir`.

    The keys are the file names; the order follows BENCHMARK_FILES.
    """
    base = Path(benchmark_dir)
    out: dict[str, str] = {}
    for name in BENCHMARK_FILES:
        path = base / name
        if not path.is_file():
            raise FileNotFoundError(f"the benchmark input is missing: {path}")
        out[name] = sha256_file(path)
    return out


def build_launch_manifest(
    *,
    launch_tag: str,
    commit: str,
    image_digest: str,
    benchmark_sha256: Mapping[str, str],
) -> dict:
    """The provenance block every run record has to carry."""
    return {
        "launch_tag": launch_tag,
        "commit": commit,
        "image_digest": image_digest,
        "benchmark_sha256": dict(benchmark_sha256),
    }


# ---------------------------------------------------------------------------
# The provider errors
# ---------------------------------------------------------------------------

# The provider says that the daily quota is gone. These are a pause
# until the reset, and a run that was interrupted by one of them is
# repeated from scratch.
QUOTA_EXHAUSTED_PATTERNS: tuple[str, ...] = (
    "insufficient_quota",
    "quota_exhausted",
    "quota exhausted",
    "exceeded your current quota",
    "quota exceeded",
    "daily limit reached",
    "insufficient balance",
    "insufficient_balance",
    "no quota remaining",
    "out of quota",
)

# The provider says that the request rate was too high. These are a
# short pause and a reason to lower the parallelism.
RATE_LIMIT_PATTERNS: tuple[str, ...] = (
    "rate limit",
    "rate_limit",
    "ratelimit",
    "too many requests",
    "request rate",
    "slow down",
)


def classify_provider_error(text: str | None) -> str | None:
    """Classify a provider answer.

    Returns "quota_exhausted", "rate_limit" or None (not a provider
    quota error). The quota check comes first: a 429 whose body says
    the quota is exhausted is a quota pause, not a rate-limit pause.
    """
    if not text:
        return None
    lowered = str(text).lower()
    for pattern in QUOTA_EXHAUSTED_PATTERNS:
        if pattern in lowered:
            return "quota_exhausted"
    for pattern in RATE_LIMIT_PATTERNS:
        if pattern in lowered:
            return "rate_limit"
    # A bare HTTP 429 with no recognizable body is a rate limit.
    if re.search(r"\b429\b", lowered):
        return "rate_limit"
    return None


def classify_provider_response(status_code: int | None, body: str | None) -> str | None:
    """Classify a provider answer that came with an HTTP status."""
    if status_code == 429:
        kind = classify_provider_error(body)
        # A 429 whose body says the quota is exhausted stays a quota
        # pause; otherwise it is a rate limit.
        return kind if kind == "quota_exhausted" else "rate_limit"
    return classify_provider_error(body)


def is_quota_error(text: str | None) -> bool:
    """True when the text carries a quota error of either kind."""
    return classify_provider_error(text) is not None


# ---------------------------------------------------------------------------
# The record provenance contract
# ---------------------------------------------------------------------------

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate_record_provenance(record: Mapping) -> list[str]:
    """The problems of a run record, as a list of strings.

    An empty list means the record satisfies the contract: it carries
    the launch tag, the commit, the image digest, the sha256 of the
    three benchmark inputs, and a clean working tree.
    """
    problems: list[str] = []
    manifest = record.get("launch_manifest")
    if not isinstance(manifest, Mapping):
        return ["the record carries no launch_manifest"]

    tag = manifest.get("launch_tag")
    if not tag or not str(tag).strip():
        problems.append("the launch manifest has no launch_tag")

    commit = manifest.get("commit")
    if not commit or not str(commit).strip():
        problems.append("the launch manifest has no commit")

    digest = manifest.get("image_digest")
    if not digest or not str(digest).startswith("sha256:"):
        problems.append("the launch manifest has no image digest (sha256:...)")

    hashes = manifest.get("benchmark_sha256")
    if not isinstance(hashes, Mapping):
        problems.append("the launch manifest has no benchmark_sha256 map")
    else:
        for name in BENCHMARK_FILES:
            value = hashes.get(name)
            if not value:
                problems.append(f"the launch manifest has no sha256 for {name}")
            elif not _HEX64.match(str(value)):
                problems.append(f"the sha256 for {name} is not a sha256: {value!r}")

    dirty = record.get("git_dirty")
    if dirty is None:
        problems.append("the record has no dirty flag")
    elif bool(dirty):
        problems.append("the record was produced by a dirty working tree")

    return problems


def format_problems(problems: Iterable[str]) -> str:
    """The problems as one human-readable line."""
    return "; ".join(problems)
