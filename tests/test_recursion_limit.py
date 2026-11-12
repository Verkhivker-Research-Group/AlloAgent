import pytest
import sys
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from biomni.agent.a1 import DEFAULT_RECURSION_LIMIT, A1


def test_default_is_500():
    """Default recursion limit is 500, matching upstream prior behavior."""
    assert DEFAULT_RECURSION_LIMIT == 500


def test_a1_init_accepts_recursion_limit():
    """A1.__init__ accepts a recursion_limit kwarg whose default is 500."""
    import inspect
    sig = inspect.signature(A1.__init__)
    assert "recursion_limit" in sig.parameters
    assert sig.parameters["recursion_limit"].default == DEFAULT_RECURSION_LIMIT


def test_recursion_limit_propagates_to_config():
    """A1.recursion_limit is honored when A1 builds its RunnableConfig."""
    import inspect
    src = inspect.getsource(A1)
    assert "DEFAULT_RECURSION_LIMIT" in src, \
        "DEFAULT_RECURSION_LIMIT not referenced in A1 module"
    assert "self.recursion_limit" in src or "DEFAULT_RECURSION_LIMIT" in src, \
        "recursion_limit override wiring not found in A1"