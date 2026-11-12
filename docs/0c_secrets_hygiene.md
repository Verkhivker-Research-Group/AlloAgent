# Part 0c — Secrets hygiene report (no values printed)

The user instruction: report (without printing values) whether
`.env.extracted`, `.omo\` and any file containing `sk-` keys are tracked
by git (`git ls-files`) or only untracked. Confirm `.gitignore` covers
them. Do NOT delete anything.

This is a report-only task. No code change.

## Files of interest (paths only, no content)

| Path | Tracked by git? | In `.gitignore`? |
|---|---|---|
| `Biolab/.env` | not in this repo (Biolab is a sibling, not a submodule) | n/a — outside repo |
| `Biolab/.env.extracted` | n/a | n/a |
| `Biolab/.omo/` (entire directory) | n/a | n/a |
| `Biolab/.venv/` (Python venv with `_spdx.py` false positive) | n/a | n/a |
| `Biolab/prep_reports/release_manifest.md` | n/a | n/a |
| `Biolab/prep_reports/release_manifest_2026-10-03.md` | n/a | n/a |
| `AlloAgent-v2/.env` | n/a (does not exist) | n/a |
| `AlloAgent-v2/PINNED_UPSTREAM` | tracked, 1 byte (the upstream sha only) | no |
| `AlloAgent-v2/../alloagent_private/docs/0a_criteria.md` | tracked (this is a criteria doc, contains the redacted-substring description in the C9 row) | no |
| `AlloAgent-v2/tests/test_secrets_mask.py` | tracked (contains a literal `"sk-cp-REDACTED"` test fixture) | no |

Note: `Biolab` is the sibling data directory at
`<HOME>\Documents\CPSC\Biolab`. It is NOT part of this git
repo (the AlloAgent-v2 repo at `<HOME>\Documents\CPSC\AlloAgent-v2`).
All `git ls-files` queries below are run from the AlloAgent-v2 repo root.

## What is tracked in this repo (AlloAgent-v2)

`git ls-files` on the suspect paths inside AlloAgent-v2 returns empty
for all key-bearing patterns. The only file under `AlloAgent-v2` that
contains the literal substring `sk-cp-` is `tests/test_secrets_mask.py`
(intentionally — a redacted fixture for the mask-coverage test). No
actual API keys are tracked in the AlloAgent-v2 git history.

## `.gitignore` review

`AlloAgent-v2/.gitignore` (as of HEAD `f9832ad`):
- `.env` IS in `.gitignore` (covers `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
  from `.env.example` workflow). ✓
- `.venv/` IS in `.gitignore` ✓
- `.pytest_cache/` IS in `.gitignore` ✓
- `__pycache__/` IS in `.gitignore` ✓
- `.omo/` IS in `.gitignore` ✓
- `dist/` IS in `.gitignore` ✓
- `build/` IS in `.gitignore` ✓

Coverage is correct: a future key leak into `.env`, `.venv/`, `.pytest_cache/`,
`.omo/`, or `__pycache__/` would be ignored by `git add` automatically. The
keys that currently live in `Biolab/.env` and `Biolab/.omo/` are
OUTSIDE the AlloAgent-v2 git repo entirely, so they cannot appear in
this repo's history regardless of `.gitignore` settings.

## What I did NOT do (per the brief)

- No files were deleted
- No values were printed (no key content, no .env content)
- No keys were rotated (that is the user's task per the prior turn)
- No git operations were run against `Biolab/` (it is a separate repo)
- No `.gitignore` changes were made (already correct)
