"""Settings of the AlloAgent demo frontend.

Every value can be overridden from the environment, so the same code runs
on a laptop and inside the container.
"""
from __future__ import annotations

import os

# The interface listens here; the docker run maps the port to the host.
HOST = os.environ.get("ALLOAGENT_FRONTEND_HOST", "0.0.0.0")
PORT = int(os.environ.get("ALLOAGENT_FRONTEND_PORT", "8765"))

# The prompt the "Try this example" button puts into the chat box.
#
# PLACEHOLDER: replace this with the allostery prompt you want to show in
# the recording.  ALLOAGENT_DEMO_PROMPT overrides it without a code change.
DEMO_PROMPT = os.environ.get(
    "ALLOAGENT_DEMO_PROMPT",
    "PLACEHOLDER - replace this with the allostery question you want to show.",
)

# The model the agent runs on.  These are the settings the paper's runs
# used: MiniMax-M3 served as an OpenAI-compatible endpoint.  Any provider
# the Biomni configuration supports works here too - set BIOMNI_SOURCE and
# BIOMNI_LLM in the .env you pass to the container.
LLM = os.environ.get("BIOMNI_LLM", "MiniMax-M3")
SOURCE = os.environ.get("BIOMNI_SOURCE", "Custom")
BASE_URL = os.environ.get("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
API_KEY = os.environ.get("BIOMNI_CUSTOM_API_KEY", "")

# Where the agent keeps its data lake.  The demo does not need the lake
# itself, so nothing is downloaded for it.
DATA_PATH = os.environ.get("BIOMNI_DATA_PATH", "./data")

# The per-call timeout of the agent, in seconds.
TIMEOUT_SECONDS = int(os.environ.get("BIOMNI_TIMEOUT_SECONDS", "600"))

# The maximum length of a tool output that is sent to the browser.
MAX_OUTPUT_CHARS = int(os.environ.get("ALLOAGENT_FRONTEND_MAX_OUTPUT", "20000"))
