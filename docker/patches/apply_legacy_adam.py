#!/usr/bin/env python3
"""Build-time patch for PocketMiner and AE-PocketMiner.

Rewrites ``tf.keras.optimizers.Adam`` to
``tf.keras.optimizers.legacy.Adam`` in every ``.py`` file under
the repo roots passed on the command line. This is the **only**
build-time patch needed for the two repos to import and restore
their TF 1.x checkpoints under TF 2.15.

The previous Dockerfile tried to match
``tensorflow.keras.optimizers.Adam`` (no leading ``tf.``) which
never matched; the actual code uses the ``tf.keras`` form (verified
by ``grep -rn 'tf.keras.optimizers.Adam' src/`` against the cloned
repos at the pinned commits).

The script is idempotent: re-running it on already-patched files
is a no-op.

Usage:
    python apply_legacy_adam.py <repo_dir> [<repo_dir> ...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Match the exact ``tf.keras.optimizers.Adam`` token and rewrite to
# the legacy form. The regex is anchored on the word boundary on the
# right so we don't accidentally match ``tf.keras.optimizers.Adamax``.
PATTERN = re.compile(r"\btf\.keras\.optimizers\.Adam\b")
REPLACEMENT = "tf.keras.optimizers.legacy.Adam"


def patch_file(path: Path) -> tuple[bool, int]:
    """Patch a single file. Returns (changed, n_replacements)."""
    text = path.read_text(encoding="utf-8")
    new_text, n = PATTERN.subn(REPLACEMENT, text)
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        return True, n
    return False, 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: apply_legacy_adam.py <repo_dir> [<repo_dir> ...]", file=sys.stderr)
        return 2
    total_files = 0
    total_replacements = 0
    for root in argv:
        root_path = Path(root)
        for py_file in sorted(root_path.rglob("*.py")):
            changed, n = patch_file(py_file)
            if changed:
                rel = py_file.relative_to(root_path)
                print(f"  patched {root_path.name}/{rel}: {n} replacement(s)")
                total_files += 1
                total_replacements += n
    print(
        f"legacy-Adam patch: {total_files} file(s) changed, "
        f"{total_replacements} replacement(s) total"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
