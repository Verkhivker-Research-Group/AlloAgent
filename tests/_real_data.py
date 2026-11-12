"""REQUIRE_REAL_DATA=1 helper for tests that depend on real Biolab
fixtures.

When REQUIRE_REAL_DATA=1 is set in the environment:

  * missing dataset files FAIL the affected test (not skip);
  * empty parametrize rows (no qualifiers in the biolab CSV / no
    positive controls) FAIL the test.

When REQUIRE_REAL_DATA is not set:

  * missing files SKIP the test (the historical behavior);
  * empty parametrize rows skip the tests too (zero tests
    collected -- pytest reports the module as collected with
    no items).

This module is intentionally tiny so the dependency surface stays
small. The flag is read at import time and at call time.
"""
from __future__ import annotations

import os


def require_real_data() -> bool:
    return os.environ.get("REQUIRE_REAL_DATA") == "1"


def require_real_data_or_fail(path, message=None):
    """Raise FileNotFoundError (not pytest.skip) when REQUIRE_REAL_DATA=1
    and `path` does not exist.

    When REQUIRE_REAL_DATA is not set and `path` is missing, return
    False (the caller should call pytest.skip).
    """
    import os

    exists = os.path.exists(path)
    if exists:
        return True
    if require_real_data():
        raise FileNotFoundError(
            message
            or f"REQUIRE_REAL_DATA=1 but dataset is missing at {path}"
        )
    return False


def require_non_empty_or_fail(items, name):
    """Raise AssertionError (not pytest.skip) when REQUIRE_REAL_DATA=1
    and `items` is empty.

    When REQUIRE_REAL_DATA is not set and `items` is empty, return
    False (the caller should call pytest.skip).
    """
    if items:
        return True
    if require_real_data():
        raise AssertionError(
            f"REQUIRE_REAL_DATA=1 but no qualifying rows for {name}"
        )
    return False