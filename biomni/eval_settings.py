"""Committed evaluation settings for AlloAgent.

Do not edit casually. This is the eval config committed to the repo so
that .env-on-the-host or per-run overrides can be distinguished from
the project's intended baseline.

These are the planned default settings for the AlloAgent evaluation
runs; subject to confirmation in the upcoming pilot.

The values are sourced from MiniMax recommended defaults. Override
them per-run via environment variables (typically only when running
the smoke check or a deliberate single-shot parameter sweep):

  BIOMNI_LLM, BIOMNI_SOURCE, BIOMNI_CUSTOM_BASE_URL, BIOMNI_CUSTOM_API_KEY,
  BIOMNI_TEMPERATURE, BIOMNI_TOP_P,
  BIOMNI_PATH / BIOMNI_DATA_PATH, BIOMNI_TIMEOUT_SECONDS,
  BIOMNI_USE_TOOL_RETRIEVER, BIOMNI_COMMERCIAL_MODE,
  BIOMNI_PROTOCOLS_IO_ACCESS_TOKEN.

For the user's "do not edit .env" rule, BIOMNI_TEMPERATURE / BIOMNI_TOP_P
should NOT be set in the .env file; this module provides the fallback
defaults the eval is meant to use.
"""

TEMPERATURE = 1.0
TOP_P = 0.95
USE_TOOL_RETRIEVER = False
DB_TOOL_TEMPERATURE = 0.0
