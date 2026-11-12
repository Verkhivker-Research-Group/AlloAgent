# The AlloAgent demo frontend

A local web page that runs the AlloAgent agent and shows its steps live.
It is meant for a local screen recording: no authentication, no settings
page, no history, no database.

## Start it

```bash
docker run --rm -it -p 8765:8765 \
    --env-file .env \
    -v "$(pwd):/workspace" \
    -w /workspace \
    alloagent-eval:v6 \
    -c "pip install -q --no-warn-script-location fastapi uvicorn && /opt/conda/envs/alloagent_e1/bin/python frontend/server.py"
```

It prints the URL it serves on (`http://localhost:8765`). The `.env` is
the file with your provider key - `BIOMNI_CUSTOM_API_KEY`, `BIOMNI_LLM`,
`BIOMNI_SOURCE`, `BIOMNI_CUSTOM_BASE_URL` (see `.env.example`).

## The files

| file | what it is |
| --- | --- |
| `config.py` | the settings, and `DEMO_PROMPT`: the prompt the "Try this example" button puts into the chat box |
| `server.py` | the server: the page, the streaming endpoint, the recorder that catches every tool call |
| `static/index.html` | the page itself - the styles and the script live in the file |

## Notes

- The agent runs in the container; the page shows every tool it calls as a
  card that expands to the inputs and the output, and the final answer as
  formatted text under the cards.
- A prompt that needs the structure cache needs it mounted:
  add `-v <path-to-the-cache>:/data/structures:ro` to the run command.
- `ALLOAGENT_DEMO_PROMPT` overrides `DEMO_PROMPT` without a code change.
