"""The shared path helpers.

The committed records name the home directory with the ``<HOME>``
placeholder, so that the repository carries no personal path.  The code that
opens a record directory expands it with :func:`expand_home`; the directory
it stands for is ``$ALLOAGENT_HOME`` when that is set and the user's home
directory otherwise.
"""
from __future__ import annotations

import os
from pathlib import Path

HOME_PLACEHOLDER = "<HOME>"


def home_dir() -> Path:
    """The directory the ``<HOME>`` placeholder stands for."""
    override = os.environ.get("ALLOAGENT_HOME")
    return Path(override) if override else Path.home()


def expand_home(path) -> Path:
    """A path whose leading ``<HOME>`` stands for the home directory."""
    parts = Path(str(path)).parts
    if parts and parts[0] == HOME_PLACEHOLDER:
        return home_dir().joinpath(*parts[1:])
    return Path(str(path))
