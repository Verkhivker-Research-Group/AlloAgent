"""Host-pytest shim for the T9 regression tests.

The `biomni/tool/__init__.py` module imports `langchain_core` at
module-load time, which is present in the container's
`alloagent_e1` conda env but NOT in the host's plain CPython.
The T9 wrapper itself (`biomni/tool/get_clinvar_variants.py`)
does not use langchain_core; it only needs `biomni.tool._blocklist`
and `biomni.tool._netcall`. This shim stubs the langchain_core
namespace so the host pytest can import `biomni.tool` and run
the T9 regression tests without requiring the container image.

This is a TEST-ENVIRONMENT workaround (a conftest for host runs),
NOT a test-time fix to the wrapper or to the tests. The canonical
test runs in the container via `scripts/run_tests_container.sh`
where langchain_core is in the image; the host run is for
verifying the wrapper fix when the docker daemon is unavailable.
"""
from __future__ import annotations

import importlib.util
import sys
import types


def _install_langchain_stub() -> None:
    # ONLY stub when the real langchain_core is not importable. In the
    # container the conda env `alloagent_e1` has langchain_core already
    # installed; this conftest is loaded as `tests/_host_only_conftest.py`
    # for the **host-only** verification run (when the Docker daemon
    # is unavailable). Guarding on a probe of the real module
    # prevents the stub from shadowing the real langchain_core in the
    # container, which would break the canonical pytest run.
    if importlib.util.find_spec("langchain_core") is not None:
        return
    pkg = types.ModuleType("langchain_core")
    pkg.__path__ = []  # mark as package
    sys.modules["langchain_core"] = pkg

    sub = types.ModuleType("langchain_core.callbacks")
    class _BaseCallbackHandler:
        def __init__(self, *a, **kw):
            pass
    sub.BaseCallbackHandler = _BaseCallbackHandler
    sys.modules["langchain_core.callbacks"] = sub
    pkg.callbacks = sub

    sub2 = types.ModuleType("langchain_core.messages.base")
    def _get_msg_title_repr(*a, **kw):
        return ""
    sub2.get_msg_title_repr = _get_msg_title_repr
    sys.modules["langchain_core.messages.base"] = sub2
    pkg.messages = types.ModuleType("langchain_core.messages")
    pkg.messages.base = sub2
    sys.modules["langchain_core.messages"] = pkg.messages

    sub3 = types.ModuleType("langchain_core.tools")
    class _StructuredTool:
        def __init__(self, *a, **kw):
            pass
    sub3.StructuredTool = _StructuredTool
    sys.modules["langchain_core.tools"] = sub3
    pkg.tools = sub3

    sub4 = types.ModuleType("langchain_core.utils.interactive_env")
    def _is_interactive_env(*a, **kw):
        return False
    sub4.is_interactive_env = _is_interactive_env
    sys.modules["langchain_core.utils.interactive_env"] = sub4
    pkg.utils = types.ModuleType("langchain_core.utils")
    pkg.utils.interactive_env = sub4
    sys.modules["langchain_core.utils"] = pkg.utils


_install_langchain_stub()
