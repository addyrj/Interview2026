---

# 36. Runner.run() vs run_sync() vs run_streamed()
# हिंदी में: Runner.run() बनाम run_sync() बनाम run_streamed()
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, openai 3.51.0 types). All code ran offline with `agents.testing.ScriptedModel`. A scripted model emits the whole answer as ONE text delta; a real model emits many small deltas, so real streaming timing is not shown here (needs `OPENAI_API_KEY`).

---

## 🔵 Simple Definition (2-3 lines)
`Runner.run()` is an async coroutine (await it, get a `RunResult`). `Runner.run_sync()` is a blocking wrapper for plain scripts. `Runner.run_streamed()` returns immediately with a streaming result and you iterate `stream_events()` to get tokens and progress while the run executes.

## 🔵 सरल परिभाषा (Hindi)
`Runner.run()` async coroutine है (await करें, `RunResult` मिलता है)। `Runner.run_sync()` साधारण scripts के लिए blocking wrapper है। `Runner.run_streamed()` तुरंत एक streaming result लौटाता है और आप `stream_events()` पर iterate करके run के दौरान ही tokens और progress पाते हैं।

---

## 🔴 Problem it Solves
Picking the wrong entry point causes real bugs: `run_sync` in an async FastAPI handler crashes (or blocks the event loop), and `run` makes users stare at a blank screen for 10 seconds when a chat UI should show tokens as they arrive. Three entry points cover scripts, async servers and live UIs.

## 🔴 यह क्यों बना? (Hindi)
गलत entry point चुनने से असली bugs आते हैं: async FastAPI handler में `run_sync` crash होता है (या event loop block करता है), और `run` से user 10 सेकंड खाली screen देखता है जबकि chat UI में tokens आते हुए दिखने चाहिए। तीन entry points scripts, async servers और live UI तीनों को कवर करते हैं।

---

## 🟢 How it Works

```
run_sync(agent, input, ...)      -> blocks the thread -> RunResult
run(agent, input, ...)           -> await            -> RunResult
run_streamed(agent, input, ...)  -> returns RunResultStreaming at once (do NOT await)
      |
      +-- async for event in result.stream_events():
            raw_response_event       (data: openai ResponseTextDeltaEvent -> .delta = text chunk)
            run_item_stream_event    (name: tool_called | tool_output | message_output_created | handoff_requested ...)
            agent_updated_stream_event (a handoff changed the current agent)
      +-- after the loop: result.final_output, result.is_complete, usage ...
      +-- result.cancel() to stop early
```

## 🟢 कैसे काम करता है? (Hindi)

```
run_sync(agent, input, ...)      -> thread block करता है -> RunResult
run(agent, input, ...)           -> await करें           -> RunResult
run_streamed(agent, input, ...)  -> तुरंत RunResultStreaming लौटाता है (await नहीं करना)
      |
      +-- async for event in result.stream_events():
            raw_response_event       (data: ResponseTextDeltaEvent -> .delta = text टुकड़ा)
            run_item_stream_event    (name: tool_called | tool_output | message_output_created ...)
            agent_updated_stream_event (handoff से current agent बदला)
      +-- loop के बाद: result.final_output, result.is_complete, usage ...
      +-- जल्दी रोकने के लिए result.cancel()
```

**Verified facts (0.24.0):**
- All three accept the same main arguments (`context`, `max_turns=10`, `hooks`, `run_config`, `session`, ...), read from `inspect.signature`.
- `run_sync` inside a running event loop raised `RuntimeError: AgentRunner.run_sync() cannot be called when an event loop is already running` (we ran it).
- `run_streamed` is a normal (non-async) function; its result has `stream_events()`, `cancel()`, `is_complete`, `final_output` and `to_input_list()`.
- In our run the event order was: `agent_updated_stream_event`, then `raw_response_event`s (`response.created`, `response.output_text.delta`, ... `response.completed`), then `run_item_stream_event` (`message_output_created`). With a tool call the item events were `tool_called`, `tool_output`, `message_output_created`.
- Exceptions such as `MaxTurnsExceeded` are raised while you iterate `stream_events()`, so put try/except around the loop, not around the `run_streamed(...)` call.

**Connect to what you know:** `run` ~ `ainvoke`, `run_sync` ~ `invoke`, `run_streamed` ~ `astream_events`. Same rule as LangGraph: use the async versions in FastAPI.

---

## 🟡 Real World Example
**Tariff Agent.** `/ask` (JSON API used by other services) uses `await Runner.run`. The customs portal chat UI uses `/stream` with `run_streamed`, showing "looking up tariff..." when the tool is called and then the answer tokens. A nightly batch script that classifies 500 items uses `run_sync` (or `asyncio.gather` over `run`).

**Customer Support:** streaming is the default for chat widgets.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `/ask` (दूसरी services के लिए JSON API) `await Runner.run` इस्तेमाल करता है। Customs portal का chat UI `run_streamed` वाला `/stream` इस्तेमाल करता है: tool call होते ही "looking up tariff..." और फिर answer के tokens दिखते हैं। रात का batch script जो 500 items classify करता है `run_sync` (या `run` पर `asyncio.gather`) इस्तेमाल करता है।

**Customer Support:** chat widgets के लिए streaming default है।

---

## 💻 Code Example — Basic
All three entry points on the same agent, plus the classic `run_sync`-inside-async error. Runs offline.

```python
# Basic: the three Runner entry points side by side (runs offline)
import asyncio                                           # needed for run() and run_streamed()
from agents import Agent, Runner, function_tool, set_tracing_disabled  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def make_agent() -> Agent:                               # fresh scripted model per run (script is consumed)
    model = ScriptedModel([[function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
                           [assistant_message("HS 6109 duty is 12%.")]])
    return Agent(name="Tariff Agent", instructions="Be brief.", tools=[get_tariff_rate], model=model)

# 1) run_sync: blocking, for scripts, CLIs, tests (NOT inside an async function)
r1 = Runner.run_sync(make_agent(), "Duty for HS 6109?")  # returns RunResult
print("run_sync     :", r1.final_output)

async def main() -> None:
    # 2) run: async coroutine, the default choice inside FastAPI
    r2 = await Runner.run(make_agent(), "Duty for HS 6109?")  # awaitable, returns RunResult
    print("run          :", r2.final_output)

    # 3) run_streamed: returns IMMEDIATELY; you consume events while the run executes
    streamed = Runner.run_streamed(make_agent(), "Duty for HS 6109?")  # note: NOT awaited
    seen: list[str] = []                                 # collect event type names
    async for event in streamed.stream_events():         # async iterator of stream events
        if event.type == "run_item_stream_event":        # a whole item finished (tool call, output, message)
            seen.append(event.name)                      # e.g. tool_called, tool_output, message_output_created
    print("run_streamed :", streamed.final_output, "| item events:", seen)
    print("is_complete  :", streamed.is_complete)        # True after the stream is fully consumed

asyncio.run(main())                                      # start the event loop for the async parts

async def wrong() -> None:
    try:
        Runner.run_sync(make_agent(), "x")               # calling run_sync from inside a running loop
    except RuntimeError as exc:                          # the SDK refuses
        print("run_sync inside async ->", str(exc)[:70])

asyncio.run(wrong())                                     # shows the classic FastAPI mistake
```

## 💻 Code Example — Advanced
FastAPI with a JSON endpoint (`run`) and an SSE endpoint (`run_streamed`): token events, status events, usage in the final event, error events, `cancel()` in `finally`. Runs offline via `TestClient`. Real browsers or `curl -N` against `uvicorn` were not run here.

```python
# Advanced: FastAPI with both a normal endpoint (run) and an SSE streaming endpoint (run_streamed) (runs offline)
import json                                              # SSE payloads
from typing import AsyncIterator                         # generator type
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.responses import StreamingResponse          # server-sent events
from fastapi.testclient import TestClient                # in-process client
from openai.types.responses import ResponseTextDeltaEvent  # raw event carrying a text chunk
from agents import (Agent, Runner, MaxTurnsExceeded, AgentsException,
                    function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

@function_tool
async def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def make_agent() -> Agent:                               # new scripted model per request
    model = ScriptedModel([[function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
                           [assistant_message("HS 6109 duty is 12%.")]])
    return Agent(name="Tariff Agent", instructions="Be brief.", tools=[get_tariff_rate], model=model)

app = FastAPI()

@app.get("/ask")                                         # non-streaming: simplest, best for JSON APIs
async def ask(q: str) -> dict[str, object]:
    try:
        r = await Runner.run(make_agent(), q, max_turns=4)  # await the whole run
    except MaxTurnsExceeded:
        raise HTTPException(504, "max turns exceeded")
    return {"answer": r.final_output, "tokens": r.context_wrapper.usage.total_tokens}

def sse(event: str, data: dict[str, object]) -> str:     # format one server-sent event
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

async def event_stream(q: str) -> AsyncIterator[str]:    # generator FastAPI iterates
    streamed = Runner.run_streamed(make_agent(), q, max_turns=4)  # returns immediately, run happens in background
    try:
        async for ev in streamed.stream_events():        # consume events as they arrive
            if ev.type == "raw_response_event" and isinstance(ev.data, ResponseTextDeltaEvent):
                yield sse("token", {"text": ev.data.delta})  # text chunk for the UI
            elif ev.type == "run_item_stream_event" and ev.name == "tool_called":
                yield sse("status", {"msg": "looking up tariff..."})  # progress hint
        yield sse("done", {"tokens": streamed.context_wrapper.usage.total_tokens})  # usage after completion
    except MaxTurnsExceeded:                             # errors surface while iterating, not before
        yield sse("error", {"detail": "max turns exceeded"})
    except AgentsException as exc:                       # any other SDK failure
        yield sse("error", {"detail": type(exc).__name__})
    finally:
        streamed.cancel()                                # stop background work if the client disconnected

@app.get("/stream")                                      # streaming endpoint
async def stream(q: str) -> StreamingResponse:
    return StreamingResponse(event_stream(q), media_type="text/event-stream")

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.get("/ask", params={"q": "HS 6109?"}).json())  # one JSON answer
    print(c.get("/stream", params={"q": "HS 6109?"}).text)  # SSE: status, token, done
```

Observed output of the streaming endpoint: a `status` event, one `token` event (scripted model sends the whole text at once), then `done` with `tokens: 0` (scripted model reports 0 usage).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Blocking run | `graph.invoke` | `crew.kickoff()` | `Runner.run_sync` | `asyncio.run(agent.run(...))` |
| Async run | `graph.ainvoke` | `crew.kickoff_async()` | `await Runner.run` | `await agent.run(...)` |
| Streaming | `astream` / `astream_events` | Limited, event listeners | `Runner.run_streamed` + `stream_events()` | `run_stream()` |
| Token deltas | `stream_mode="messages"` | Not first-class | `raw_response_event` text deltas | `ModelClientStreamingChunkEvent` (when enabled) |
| Cancel | Cancel the task | Cancel the task | `streamed.cancel()` | Cancellation token |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `Runner.run_sync` inside `async def` (FastAPI handler).
✅ Correct: `await Runner.run(...)`. We verified `run_sync` raises `RuntimeError` there.

❌ Mistake 2: `await Runner.run_streamed(...)`.
✅ Correct: `run_streamed` is not awaited; iterate `result.stream_events()`.

❌ Mistake 3: Reading `final_output` before consuming the stream.
✅ Correct: Fully iterate `stream_events()` first, then read `final_output` and usage.

❌ Mistake 4: try/except around `run_streamed(...)` only.
✅ Correct: Errors appear during iteration; wrap the `async for`.

❌ Mistake 5: Not cancelling when the client disconnects.
✅ Correct: Call `streamed.cancel()` in `finally` so you stop paying for tokens nobody reads.

---

## 🧠 Tricky Interview Question
Your streaming endpoint shows the answer fast but your cost dashboard shows many runs consuming tokens after users closed the tab. Why?

**Answer:** `run_streamed` starts the run as a background task. If the HTTP client disconnects and your generator is simply abandoned, the agent loop can keep calling the model and tools. Always wrap the iteration in `try/finally` and call `streamed.cancel()`, and make the generator react to disconnects (FastAPI cancels the generator task on disconnect, so `finally` runs). Add `max_turns` and a timeout as a second safety net, and record usage per run to verify the leak is gone.

---

## ⚫ Interview Questions + Answers

**Q1:** Which of the three do you use inside a FastAPI `async def` endpoint?

**A1:** `await Runner.run(...)` for JSON responses, or `Runner.run_streamed(...)` for streaming. Never `run_sync`.

**Q2:** Is `run_sync` just `asyncio.run(Runner.run(...))`?

**A2:** Conceptually a blocking wrapper over the async run; it needs no running event loop and raises `RuntimeError` if one is running (verified).

**Q3:** How do you get tokens as they are generated?

**A3:** `Runner.run_streamed`, then `async for event in result.stream_events()` and filter `raw_response_event` whose `data` is a `ResponseTextDeltaEvent`; use `event.data.delta`.

**Q4:** Where do errors surface when streaming?

**A4:** While iterating `stream_events()` (for example `MaxTurnsExceeded`, guardrail tripwires), so handle them around the loop and send an error event to the client.

**Q5:** Design a chat backend that streams, survives disconnects and reports cost.

**A5:** SSE endpoint with `run_streamed`, per-conversation session, `max_turns` + timeout, `finally: cancel()`, status events for tool calls, a final `done` event with usage from `context_wrapper.usage`, metrics on time-to-first-token and total latency, and a semaphore to limit concurrent streams per process.

---

## 💰 Cost Impact
Streaming does not change token cost, it changes perceived latency. The cost risk is abandoned runs (see the tricky question). `run_sync` in a threadpool or blocked event loop wastes server capacity rather than tokens. Approximate, from public pricing at time of writing, verify: cost depends on model and turns; read `result.context_wrapper.usage` after the run (after full consumption for streams).

**Tips:** cancel abandoned streams, cap `max_turns`, stream only where a human is waiting, use plain `run` for machine-to-machine calls.

---

## 🔷 When to Use
✅ Use when:
- `run`: async servers, batch jobs with `asyncio.gather`, service-to-service APIs
- `run_sync`: scripts, CLIs, notebooks without a running loop, simple tests
- `run_streamed`: chat UIs, long research runs where you show progress

❌ Avoid when:
- `run_sync` in any async context
- `run_streamed` for non-interactive jobs (extra complexity for no benefit)

---

## 📊 Visual Diagram
```
 script/CLI -----> run_sync -----------------+
 FastAPI JSON ---> await run ----------------+--> loop --> RunResult
 FastAPI SSE ----> run_streamed --+          |
                                  |  background task runs the same loop
                                  v
              stream_events(): raw_response_event (token deltas)
                               run_item_stream_event (tool_called, tool_output, message)
                               agent_updated_stream_event (handoff)
                                  |
                       client sees tokens  -->  disconnect? -> cancel()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| coroutine | Async function you must `await` | async function जिसे await करना होता है |
| blocking | Holds the thread until done | thread को रोके रखना |
| stream_events | Async iterator of run events | run events का async iterator |
| ResponseTextDeltaEvent | Raw event with a text chunk | text टुकड़े वाला event |
| SSE | Server-sent events over HTTP | HTTP पर server से events |
| cancel() | Stop a streamed run early | streamed run जल्दी रोकना |

---

## ⚡ 3-Line Summary
English: Use `await Runner.run` in async servers, `run_sync` only in plain scripts, `run_streamed` for live UIs.
`run_streamed` is not awaited; iterate `stream_events()` and handle errors there.
Always `cancel()` abandoned streams to avoid wasted tokens.

Hindi: Async servers में `await Runner.run`, सिर्फ साधारण scripts में `run_sync`, live UI के लिए `run_streamed`।
`run_streamed` को await नहीं करते; `stream_events()` पर iterate करें और errors वहीं संभालें।
छोड़ी हुई streams को हमेशा `cancel()` करें ताकि tokens बेकार न जाएँ।

---

## ➡️ Next Topic
**#37 Handoffs, Complete Guide** - runs are single-agent so far; handoffs let one agent transfer the conversation to a specialist, the core multi-agent idea of this SDK.

---
