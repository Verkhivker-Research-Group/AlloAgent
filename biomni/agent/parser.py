"""Helpers for parsing the model's response in the biomni agent's `generate` node.

This module is intentionally dependency-free (no langchain, no biomni.* imports)
so it can be unit-tested without instantiating the full agent stack.
"""

import re as _re

#: Default limit on consecutive no-tag responses before forcing end-of-run.
DEFAULT_NO_TAG_LIMIT = 5


def _strip_think(msg):
    """Remove all <think>...</think> blocks from the model's response.

    Returns the input unchanged if it is not a string.
    """
    if not isinstance(msg, str):
        return msg
    return _re.sub(r"<think>.*?</think>", "", msg, flags=_re.DOTALL)


def _autoclose_tags(msg):
    """Repair incomplete XML tags by pairing them.

    The legacy `biomni.agent.a1` parser only added a missing closing tag
    (`</execute>` / `</solution>`). When the model emitted the closing tag
    without the matching opener (e.g. "...</execute></solution>") the legacy
    parser left the message malformed and routed it to `generate`. This helper
    completes the pair by inserting the missing opener just before the closer.

    The auto-pairing is keyed on tags seen OUTSIDE any <think> block so that a
    <execute> or <solution> token mentioned in the model's reasoning does not
    fool the repair.
    """
    if not isinstance(msg, str):
        return msg
    stripped = _strip_think(msg)
    if "<execute>" in stripped and "</execute>" not in stripped:
        msg = msg + "</execute>"
    elif "</execute>" in stripped and "<execute>" not in stripped:
        msg = msg.replace("</execute>", "<execute>\n</execute>", 1)
    if "<solution>" in stripped and "</solution>" not in stripped:
        msg = msg + "</solution>"
    if "<think>" in msg and "</think>" not in msg:
        msg = msg + "</think>"
    return msg


def _has_closed_solution_outside_think(msg):
    """True iff a complete <solution>...</solution> pair exists OUTSIDE <think> blocks.

    Bug (a) in the upstream parser: the raw `re.search(<solution>...</solution>)`
    call could match a `<solution>` tag quoted inside a <think>...</think> block.
    Stripping the think block first prevents that false positive.
    """
    stripped = _strip_think(msg)
    return _re.search(r"<solution>(.*?)</solution>", stripped, _re.DOTALL) is not None


def _has_execute_block_outside_think(msg):
    """True iff a complete <execute>...</execute> pair exists OUTSIDE <think> blocks."""
    stripped = _strip_think(msg)
    return _re.search(r"<execute>(.*?)</execute>", stripped, _re.DOTALL) is not None


def _next_step(msg, no_tag_limit=DEFAULT_NO_TAG_LIMIT):
    """Decide what to do with the model's response.

    Returns one of:
        - "end"      : a complete <solution>...</solution> pair exists outside <think>
        - "execute"  : an <execute>...</execute> pair exists outside <think>
        - "generate" : neither: ask the model to re-emit a tagged response

    The caller is responsible for counting consecutive "generate" results and
    forcing "end" once `no_tag_limit` is reached (this function does not enforce
    the limit itself; it only takes the parameter for API symmetry).
    """
    if _has_closed_solution_outside_think(msg):
        return "end"
    if _has_execute_block_outside_think(msg):
        return "execute"
    return "generate"


def _next_step_with_repair(msg, no_tag_limit=DEFAULT_NO_TAG_LIMIT):
    """Apply the autoclose-tag repair first, then run `_next_step`.

    Mirrors the legacy `biomni.agent.a1` behavior where incomplete tags were
    paired before the parser ran. Use this entry point from the agent's
    `generate` node so that responses missing the opening `<execute>` (but
    containing the closer) still route to `execute`.
    """
    return _next_step(_autoclose_tags(msg), no_tag_limit=no_tag_limit)