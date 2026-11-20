---

# 54. Streaming in SDK
# हिंदी में: SDK में Streaming (जवाब आते ही दिखाना)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model and FastAPI TestClient. The scripted model sends each message as ONE text delta; a real model sends many small deltas, so the visual token-by-token effect was not reproduced. Real network streaming, proxies and client-disconnect behaviour were not tested.

---

## 🔵 Simple Definition (2-3 lines)
Streaming means getting output while the agent is still working. `Runner.run_streamed(...)` returns immediately with a `RunResultStreaming`; you iterate `result.stream_events()` to receive text deltas, tool calls and agent changes as they happen, instead of waiting for `Runner.run` to finish.

## 🔵 सरल परिभाषा (Hindi)
Streaming का मतलब है agent के काम करते-करते ही output पाना। `Runner.run_streamed(...)` तुरंत एक `RunResultStreaming` लौटाता है; आप `result.stream_events()` पर iterate करके text deltas, tool calls और agent बदलाव उसी समय पाते हैं, `Runner.run` के खत्म होने का इंतज़ार किए बिना।

---

## 🔴 Problem it Solves
An agent run with several tool calls can take many seconds. Users staring at a blank screen assume it is broken, and you cannot show progress such as 'looking up duty...'. Streaming cuts perceived latency (time to first token) and enables live progress, cancellation and early display.

## 🔴 यह क्यों बना? (Hindi)
कई tool calls वाला agent run कई सेकंड ले सकता है। खाली screen देखते users सोचते हैं कि system टूट गया है, और आप 'duty खोज रहा हूँ...' जैसा progress नहीं दिखा सकते। Streaming perceived latency (पहले token का समय) घटाती है और live progress, cancellation और जल्दी display संभव करती है।

---

## 🟢 How it Works

```
Step 1 -> result = Runner.run_streamed(agent, input)   (not awaited)
Step 2 -> SDK starts the run in a background task
Step 3 -> async for event in result.stream_events():
            raw_response_event   -> provider deltas (text chunks)
            run_item_stream_event-> tool called / output / message
            agent_updated_...    -> handoff to another agent
Step 4 -> Forward chosen events (SSE / WebSocket) to the client
Step 5 -> Loop ends when the run finishes
Step 6 -> result.final_output / usage are now available
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> result = Runner.run_streamed(agent, input)   (await नहीं)
Step 2 -> SDK run को background task में शुरू करता है
Step 3 -> async for event in result.stream_events():
            raw_response_event   -> provider deltas (text chunks)
            run_item_stream_event-> tool called / output / message
            agent_updated_...    -> दूसरे agent को handoff
Step 4 -> चुने हुए events client को भेजो (SSE / WebSocket)
Step 5 -> Run खत्म होने पर loop खत्म
Step 6 -> अब result.final_output / usage उपलब्ध हैं
```

**Verified in 0.24.0:** `Runner.run_streamed(starting_agent, input, context=None, max_turns=10, hooks=None, run_config=None, ..., session=None)` returns `RunResultStreaming`. It is a normal (non-async) call; the work runs in the background and you must consume `stream_events()`.

**Text deltas:** a `raw_response_event` whose `data` is `ResponseTextDeltaEvent` carries `.delta` (the new text). Filter on `isinstance` because there are ~20 other raw event kinds (we saw 23 raw events for a two-turn run).

**Errors:** exceptions (`MaxTurnsExceeded`, guardrail tripwires, model errors) are raised while you iterate. In a streaming HTTP response the status line is already sent, so convert them to an `error` event in the stream (we did that in the advanced sample).

**FastAPI SSE:** return `StreamingResponse(gen(), media_type='text/event-stream')`. Behind nginx/ALB disable response buffering and send periodic keep-alives; I did not test proxies.

**Hindi नोट:** Streaming सिर्फ़ UX नहीं है: यह cancellation (user ने tab बंद किया तो tokens का खर्च रोकना) के लिए भी ज़रूरी है।

---

## 🟡 Real World Example
**Tariff Agent chat UI.** The user asks about 6109.10. The UI immediately shows 'Looking up duty...' when the `tool_called` event arrives, then streams the final sentence word by word. If the user closes the tab, the server cancels the run so no more tokens are billed.

**Research Agent:** stream progress per source while the long report is built.

## 🟡 Real Example Hindi mein
**Tariff Agent chat UI.** User 6109.10 के बारे में पूछता है। `tool_called` event आते ही UI 'Duty खोज रहा हूँ...' दिखाता है, फिर final वाक्य शब्द-दर-शब्द stream होता है। User tab बंद कर दे तो server run cancel कर देता है ताकि आगे tokens का बिल न बने।

**Research Agent:** लंबी report बनते समय हर source का progress stream करो।

---

## 💻 Code Example — Basic
Runs offline. Prints text as it arrives (one delta with the scripted model) and shows `final_output` and `is_complete` after the stream.

```python
# Basic: Runner.run_streamed - print text as it arrives (offline; ScriptedModel emits the text as one delta)
import asyncio                                           # async runner
from openai.types.responses import ResponseTextDeltaEvent  # raw event that carries a text chunk
from agents import Agent, Runner                         # SDK
from agents.testing import ScriptedModel, assistant_message  # fake LLM

async def main() -> None:
    model = ScriptedModel([[assistant_message("The duty on cotton t-shirts (6109.10) is 20 percent.")]])
    agent = Agent(name="Tariff Agent", instructions="Answer briefly.", model=model)
    result = Runner.run_streamed(agent, "Duty on cotton t-shirts?")   # NOT awaited: returns immediately, work runs in background
    async for event in result.stream_events():           # consume events as they are produced
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)  # token/chunk by token/chunk (a real model sends many small deltas)
    print()                                              # newline after the stream ends
    print("final_output:", result.final_output)          # only valid after the stream is fully consumed
    print("is_complete:", result.is_complete)

asyncio.run(main())
```

## 💻 Code Example — Advanced
Server-Sent Events endpoint: token, tool and done events; an `error` event when `MaxTurnsExceeded` is raised mid-stream; disconnect check that cancels the run. Offline with TestClient (disconnect path not exercised).

```python
# Advanced: Server-Sent Events endpoint with FastAPI, error event, client-disconnect cancel (offline)
import json                                              # SSE payloads
from typing import AsyncIterator                         # generator type
from fastapi import FastAPI, Request                     # web + disconnect detection
from fastapi.responses import StreamingResponse          # streaming body
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schema
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, function_tool, MaxTurnsExceeded, AgentsException  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

def sse(event: str, data: dict) -> str:                  # format one SSE frame
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

app = FastAPI()

class Ask(BaseModel):
    question: str
    fail: bool = False

@app.post("/stream")
async def stream(b: Ask, request: Request) -> StreamingResponse:
    steps = [[function_call("hs_duty", {"code": "6109.10"}, call_id="1")], [assistant_message("Duty is 20%.")]]
    if b.fail:                                           # simulate a model that never stops calling tools
        steps = [[function_call("hs_duty", {"code": "x"}, call_id=str(i))] for i in range(5)]
    agent = Agent(name="Tariff Agent", instructions="x", model=ScriptedModel(steps), tools=[hs_duty])
    result = Runner.run_streamed(agent, b.question, max_turns=2)

    async def gen() -> AsyncIterator[str]:
        try:
            async for ev in result.stream_events():
                if await request.is_disconnected():      # client left: stop paying for tokens
                    result.cancel()                      # then keep draining (see docs note)
                    continue
                if ev.type == "raw_response_event" and isinstance(ev.data, ResponseTextDeltaEvent):
                    yield sse("token", {"text": ev.data.delta})
                elif ev.type == "run_item_stream_event" and ev.name == "tool_called":
                    yield sse("tool", {"name": getattr(ev.item.raw_item, "name", "?")})
            yield sse("done", {"final": result.final_output})
        except MaxTurnsExceeded:                         # errors surface as exceptions INSIDE the stream, after headers are sent
            yield sse("error", {"reason": "max_turns"})
        except AgentsException as exc:
            yield sse("error", {"reason": type(exc).__name__})
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/stream", json={"question": "q"}).text)
    print(c.post("/stream", json={"question": "q", "fail": True}).text)
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Stream API | `graph.astream(stream_mode=...)`, `astream_events` | `kickoff` with streaming flag/step callbacks (limited) | `Runner.run_streamed` + `stream_events()` | `run_stream`, `on_messages_stream` |
| Token-level text | `messages` / events modes | Limited | `ResponseTextDeltaEvent` in raw events | `ModelClientStreamingChunkEvent` |
| Tool/progress events | `updates`/`events` modes | Callbacks | `run_item_stream_event` (tool_called...) | Tool-call events in the stream |
| Cancellation | Cancel the task | Limited | `result.cancel(mode=...)` | `CancellationToken` |
| Errors during stream | Raised in iteration | Raised | Raised in iteration | Raised in iteration |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Awaiting `Runner.run_streamed(...)`.
✅ Correct: It is not a coroutine; call it, then `async for` over `stream_events()`.

❌ Mistake 2: Reading `final_output` before the stream is consumed.
✅ Correct: It is only set after you drain `stream_events()`.

❌ Mistake 3: Raising HTTPException inside the stream generator.
✅ Correct: Headers are already sent; emit an error event instead.

❌ Mistake 4: Forwarding every raw event to the browser.
✅ Correct: Filter to text deltas and the few progress events you need.

❌ Mistake 5: Not stopping the run when the client disconnects.
✅ Correct: Check `request.is_disconnected()` and call `result.cancel()`, then keep draining.

---

## 🧠 Tricky Interview Question
Your streaming endpoint works locally but in production users only see the whole answer at the end, as if streaming were off. The agent code is correct. What do you check?

**Answer:** That is almost always buffering outside the SDK. Check in order: (1) reverse proxy (nginx `proxy_buffering off`, `X-Accel-Buffering: no`), cloud load balancer or CDN buffering; (2) gzip middleware that buffers small chunks; (3) the response `Content-Type` (`text/event-stream`) and no `Content-Length`; (4) the client: `fetch` with a stream reader or EventSource (a plain `await res.json()` waits for everything); (5) server worker type: sync WSGI workers or a framework layer that collects the generator; (6) very small deltas needing a flush, so send periodic keep-alive comments; (7) verify with `curl -N` straight to the app, then through each hop. If `curl -N` to the app shows chunks, the SDK is fine and a hop is buffering.

---

## ⚫ Interview Questions + Answers

**Q1:** Difference between `Runner.run` and `Runner.run_streamed`?

**A1:** `run` awaits the whole run and returns a result; `run_streamed` returns immediately and you consume events; the result fields fill in as it completes.

**Q2:** How do you get just the text tokens?

**A2:** Filter `raw_response_event` where `event.data` is a `ResponseTextDeltaEvent` and print `.delta`.

**Q3:** How are errors surfaced when streaming?

**A3:** As exceptions raised during `stream_events()` iteration (`MaxTurnsExceeded`, guardrail tripwires...); in HTTP convert them to an error event.

**Q4:** How do you stop work when the user leaves?

**A4:** Detect disconnect, call `result.cancel()` (or `mode='after_turn'`) and keep consuming events so cleanup completes.

**Q5:** Design streaming chat for 10k concurrent users.

**A5:** Async workers, SSE or WebSocket gateway with buffering disabled, per-user rate limits, bounded queues, cancellation on disconnect, keep-alives, backpressure handling, `max_turns` and timeouts, sticky sessions only if needed, and metrics for time-to-first-token.

---

## 💰 Cost Impact
Streaming does not change token cost; it changes perceived latency and lets you stop early. Cancelling a run when users leave avoids paying for output nobody reads (output tokens are typically the more expensive side; approximate, from public pricing at time of writing, verify). Connection costs are on your side: open connections per user, proxy timeouts and memory for queues. I measured no latencies because the model was scripted.

---

## 🔷 When to Use
✅ Use when:
- Chat UIs and long multi-tool runs
- You want live progress and cancellation
- Time-to-first-token matters

❌ Avoid when:
- Batch/background jobs nobody watches (`Runner.run` is simpler)
- Clients that cannot consume streams
- Infrastructure that buffers responses and cannot be changed

---

## 📊 Visual Diagram
```
  client <==SSE/WebSocket==  FastAPI generator
                                  |
                      async for ev in result.stream_events()
                                  |
        +-------------------------+--------------------------+
        | raw_response_event  run_item_stream_event  agent_updated |
        | (text delta)        (tool_called, output)   (handoff)    |
        +-------------------------+--------------------------+
                                  |
   Runner.run_streamed(agent) --> background run loop
                                  |  LLM <-> tools (turn 1..N)
                                  v
                    result.final_output (after drain)
   client disconnects --> result.cancel()  (keep draining)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| run_streamed | Starts a run you consume as a stream | stream की तरह consume होने वाला run |
| RunResultStreaming | Result object for streaming runs | streaming runs का result object |
| Text delta | Small new piece of generated text | generated text का छोटा नया टुकड़ा |
| SSE | Server-Sent Events over HTTP | HTTP पर Server-Sent Events |
| Time to first token | Delay before first output appears | पहला output दिखने तक की देरी |

---

## ⚡ 3-Line Summary
English: `Runner.run_streamed` returns at once and `stream_events()` yields text deltas, tool events and handoffs live.
Filter events, turn errors into stream events and cancel when the client leaves.
Check proxies first when streaming seems to work only locally.

Hindi: `Runner.run_streamed` तुरंत लौटता है और `stream_events()` text deltas, tool events और handoffs live देता है।
Events filter करें, errors को stream events बनाएँ और client के जाने पर cancel करें।
जब streaming सिर्फ़ local में चले तो पहले proxies जाँचें।

---

## ➡️ Next Topic
**#55 stream_events()** - a deeper look at the iterator itself: ordering, what is available after it ends, cancellation modes and exception behaviour.

---
