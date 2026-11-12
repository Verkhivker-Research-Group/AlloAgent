"""The AlloAgent demo frontend: one page, one streaming endpoint.

The agent runs in a worker thread; its steps are pushed to a queue and
the browser receives them as server-sent events.  Every tool the agent
calls is captured and sent as a card.

    python frontend/server.py

Prints the URL it serves on.
"""
from __future__ import annotations

import asyncio
import contextlib
import functools
import io
import json
import queue
import re
import threading
import time
from pathlib import Path

import markdown
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

import config

HERE = Path(__file__).resolve().parent
app = FastAPI(title="AlloAgent demo frontend")

_agent = None
_agent_lock = threading.Lock()


# --------------------------------------------------------------------------
# the agent
# --------------------------------------------------------------------------
def _build_agent():
    """The AlloAgent agent: the 45 exposed tools, the configured model."""
    from biomni.agent import A1

    agent = A1(
        path=config.DATA_PATH,
        llm=config.LLM,
        source=config.SOURCE,
        base_url=config.BASE_URL,
        api_key=config.API_KEY or "EMPTY",
        timeout_seconds=config.TIMEOUT_SECONDS,
        # The demo does not need the upstream data lake, so nothing is
        # downloaded for it.
        expected_data_lake_files=[],
        use_tool_retriever=False,
    )
    try:
        from biomni.tool._registration import apply_exposed_tools

        apply_exposed_tools(agent)
    except Exception:  # noqa: BLE001 - the demo runs with whatever is there
        pass
    return agent


def _get_agent():
    global _agent
    with _agent_lock:
        if _agent is None:
            _agent = _build_agent()
    return _agent


def _jsonable(value, _depth=0):
    """Make a tool output safe for JSON: dataframes become rows, numpy
    scalars become numbers, anything else becomes text."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if _depth > 6:
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v, _depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v, _depth + 1) for v in value]
    if hasattr(value, "to_dict") and hasattr(value, "columns"):
        try:  # a pandas DataFrame
            return {"__table__": _jsonable(value.to_dict(orient="records"), _depth + 1)}
        except Exception:  # noqa: BLE001
            pass
    if hasattr(value, "item") and hasattr(value, "dtype"):
        try:  # a numpy scalar
            return value.item()
        except Exception:  # noqa: BLE001
            pass
    return str(value)


def _clip(value):
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) > config.MAX_OUTPUT_CHARS:
        text = text[:config.MAX_OUTPUT_CHARS] + " ... (truncated)"
    return value


def _instrument(agent, events):
    """Wrap the agent's tools so every call is reported.

    The agent reaches a tool by importing it inside its Python REPL, so
    the wrapper goes onto the module attribute: the import inside the
    REPL then picks the wrapper up.
    """
    import importlib

    def wrapper(name, fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            inputs = {"args": list(args), "kwargs": kwargs}
            started = time.perf_counter()
            try:
                output = fn(*args, **kwargs)
            except Exception as error:  # noqa: BLE001
                events.put({
                    "type": "tool",
                    "name": name,
                    "inputs": _jsonable(inputs),
                    "error": f"{type(error).__name__}: {error}",
                    "seconds": round(time.perf_counter() - started, 2),
                })
                raise
            events.put({
                "type": "tool",
                "name": name,
                "inputs": _jsonable(inputs),
                "output": _clip(_jsonable(output)),
                "seconds": round(time.perf_counter() - started, 2),
            })
            return output

        inner._alloagent_wrapped = True
        return inner

    for module_name, apis in getattr(agent, "module2api", {}).items():
        try:
            module = importlib.import_module(module_name)
        except Exception:  # noqa: BLE001
            continue
        for api in apis:
            name = api.get("name")
            fn = getattr(module, name, None)
            if not callable(fn) or getattr(fn, "_alloagent_wrapped", False):
                continue
            setattr(module, name, wrapper(name, fn))

    for name, fn in list(getattr(agent, "_custom_functions", {}).items()):
        agent._custom_functions[name] = wrapper(name, fn)


def _final_answer(content):
    """The body of the last ``<solution>`` block: the answer of the run,
    without the reasoning and without the protocol blocks."""
    best = ""
    for match in re.finditer(re.escape("<solution>"), content):
        start = match.end()
        end = content.find("</solution>", start)
        body = content[start:end] if end >= 0 else content[start:]
        if len(body.strip()) > len(best.strip()):
            best = body
    answer = best.strip()
    if len(re.findall(r"[A-Za-z0-9]", answer)) < 20:
        answer = content.strip()
    answer = re.sub(r"(?is)<think>.*?</think>", "", answer)
    answer = re.sub(r"(?is)<execute>.*?</execute>", "", answer)
    return answer.strip() or content.strip()


def _run(prompt, events):
    """Run the agent and push its progress into the queue."""
    try:
        events.put({"type": "status", "text": "Preparing the agent..."})
        agent = _get_agent()
        _instrument(agent, events)
        events.put({"type": "status", "text": "Working on it..."})
        with contextlib.redirect_stdout(io.StringIO()):
            _, answer = agent.go(prompt)
        events.put({"type": "final", "html": _render(_final_answer(answer or ""))})
    except Exception as error:  # noqa: BLE001
        events.put({"type": "error", "message": f"{type(error).__name__}: {error}"})
    finally:
        events.put(None)


def _render(text):
    """The final answer as markdown."""
    html = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "nl2br"]
    )
    html = re.sub(r"(?is)<script.*?</script>", "", html)
    html = re.sub(r"(?i)\son\w+\s*=\s*\"[^\"]*\"", "", html)
    return html


# --------------------------------------------------------------------------
# the endpoints
# --------------------------------------------------------------------------
@app.get("/")
def index():
    return FileResponse(HERE / "static" / "index.html")


@app.get("/api/example")
def example():
    return {"prompt": config.DEMO_PROMPT}


@app.post("/api/run")
async def run(payload: dict):
    prompt = (payload or {}).get("prompt", "").strip()
    if not prompt:
        return JSONResponse({"error": "the prompt is empty"}, status_code=400)

    events: queue.Queue = queue.Queue()
    threading.Thread(target=_run, args=(prompt, events), daemon=True).start()

    async def stream():
        while True:
            try:
                event = await asyncio.to_thread(events.get, True, 1.0)
            except queue.Empty:
                yield ": ping\n\n"
                continue
            if event is None:
                break
            yield "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn

    print(f"AlloAgent frontend: http://localhost:{config.PORT}", flush=True)
    uvicorn.run(app, host=config.HOST, port=config.PORT, log_level="warning")
