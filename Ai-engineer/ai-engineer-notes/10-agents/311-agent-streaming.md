---

# 311. Agent Streaming
# हिंदी में: Agent Streaming (live output भेजना)

---

## 🔵 Simple Definition (English)
Agent streaming sends output to the user while the agent is still working, instead of waiting for the full answer. You can stream LLM tokens as they are generated and also stream progress events such as "searching HS code..." or "calling tool X".

## 🔵 सरल परिभाषा (Hindi)
Agent streaming में agent काम करते हुए ही user को output भेजता रहता है, पूरा जवाब बनने का इंतज़ार नहीं करता। LLM के tokens बनते ही stream हो सकते हैं, और progress events भी, जैसे "HS code खोज रहा हूँ..." या "tool X चल रहा है"।

---

## 🔴 Problem it Solves
A multi-step agent can take 10-30 seconds. A blank screen feels broken and users leave or click again (duplicate requests). Streaming shows life immediately (time to first token under a second) and builds trust by showing what the agent is doing.

## 🔴 यह क्यों बना? (Hindi)
Multi-step agent को 10-30 सेकंड लग सकते हैं। खाली screen देखकर user को लगता है कुछ टूट गया और वह दोबारा click करता है। Streaming तुरंत दिखाती है कि काम चल रहा है और agent क्या कर रहा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client opens a streaming connection (SSE or WebSocket)
Step 2 → Server starts the agent and iterates over its event stream
Step 3 → Each event is typed: token / tool_start / tool_end / final / error
Step 4 → Server formats it (SSE: "data: {json}\n\n") and flushes immediately
Step 5 → Client appends tokens to the UI and shows tool status badges
Step 6 → On finish send a "done" event with usage; close the stream
Step 7 → If client disconnects, cancel the agent to stop paying for tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Client streaming connection (SSE या WebSocket) खोलता है
Step 2 → Server agent चलाता है और उसके events पर iterate करता है
Step 3 → हर event का type होता है: token / tool_start / tool_end / final / error
Step 4 → Server उसे SSE format में तुरंत flush करता है
Step 5 → Client tokens जोड़ता है और tool status दिखाता है
Step 6 → अंत में usage के साथ "done" event भेजकर stream बंद
Step 7 → Client disconnect हो तो agent रोक दो ताकि tokens बर्बाद न हों
```

---

## 🟡 Real World Example
**Tariff Classification System**: The officer asks for a classification. The UI immediately shows "Searching tariff database...", then "Found 3 candidates", then the reasoning text appears word by word, and finally the HS code card. The officer can start reading while the agent is still writing.

**Zomato-style**: "Finding restaurants... checking delivery time... here are 5 options" appears step by step.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer classification माँगता है। UI तुरंत दिखाता है "Tariff database में खोज रहा हूँ...", फिर "3 candidates मिले", फिर reasoning शब्द-शब्द आती है, अंत में HS code card। Agent के लिखते समय ही officer पढ़ना शुरू कर सकता है।
**Zomato**: "Restaurants खोज रहा हूँ... delivery time देख रहा हूँ... ये रहे 5 options" step by step।

---

## 💻 Code Example — Basic
```python
# Basic: stream events from a fake agent using a generator (offline).
import time                                      # simulate delay
from typing import Iterator                      # generator type

def fake_agent(question: str) -> Iterator[dict[str, str]]:
    yield {"type": "tool_start", "data": "search_hs_code"}   # progress event
    time.sleep(0.1)                              # tool "runs"
    yield {"type": "tool_end", "data": "8518.22"}            # tool finished
    for word in f"The HS code for '{question}' is 8518.22.".split():   # stream words
        time.sleep(0.02)                         # token delay
        yield {"type": "token", "data": word + " "}          # one token
    yield {"type": "done", "data": ""}           # end marker

if __name__ == "__main__":
    for event in fake_agent("bluetooth speaker"):            # consume events live
        if event["type"] == "token":
            print(event["data"], end="", flush=True)         # print without newline
        else:
            print(f"\n[{event['type']}] {event['data']}")    # show status events
    print()
```

## 💻 Code Example — Advanced
```python
# Production: async generator -> SSE with cancellation, errors and usage.
import asyncio                                   # async
import json                                      # serialise events
import logging
from typing import Any, AsyncIterator

log = logging.getLogger("stream")

def sse(event: str, data: dict[str, Any]) -> str:
    # SSE wire format: "event: name\ndata: {json}\n\n" (blank line ends the message)
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def agent_events(question: str) -> AsyncIterator[tuple[str, dict[str, Any]]]:
    yield "status", {"message": "Searching tariff database"}      # progress
    await asyncio.sleep(0.1)                                      # tool latency
    yield "tool", {"name": "search_hs_code", "result": "8518.22"}
    text = f"HS code for {question} is 8518.22 with high confidence."
    for word in text.split():                                     # token stream
        await asyncio.sleep(0.02)
        yield "token", {"text": word + " "}
    yield "usage", {"input_tokens": 420, "output_tokens": 35}

async def sse_stream(question: str) -> AsyncIterator[str]:
    try:
        async for name, data in agent_events(question):           # iterate agent events
            yield sse(name, data)                                 # forward to client
        yield sse("done", {})                                     # terminator
    except asyncio.CancelledError:                                # client disconnected
        log.info("client left, agent cancelled")
        raise                                                     # must re-raise
    except Exception as exc:                                      # stream cannot change status code
        log.exception("stream failed")
        yield sse("error", {"message": "internal error"})         # report in-band, hide details

async def main() -> None:
    async for chunk in sse_stream("bluetooth speaker"):           # demo consumer
        print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Request             # framework
from fastapi.responses import StreamingResponse  # streaming body
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/agent/stream")
async def stream(q: Q, request: Request) -> StreamingResponse:
    async def gen():
        async for chunk in sse_stream(q.question):    # from Advanced example
            if await request.is_disconnected():       # stop if the browser closed
                break
            yield chunk
    return StreamingResponse(
        gen(), media_type="text/event-stream",        # SSE content type
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # stop proxy buffering
    )
```
Behind nginx or a CDN, disable buffering, otherwise the user sees everything at the end.

---

## 🔗 LangChain / LangGraph Connection
```python
# LangGraph: stream_mode controls what you get.
#  "messages" -> LLM tokens, "updates" -> per-node state changes, "values" -> full state
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[])

async def run() -> None:
    async for chunk, meta in agent.astream(
        {"messages": [("user", "Explain HS codes briefly")]},
        stream_mode="messages",                 # yields (message_chunk, metadata)
    ):
        print(chunk.content, end="", flush=True)

# LangChain runnables: astream_events(version="v2") gives on_chat_model_stream, on_tool_start, on_tool_end
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Streaming only the final LLM call and showing nothing during tools.
✅ Correct: also emit `tool_start` / `tool_end` events.

```python
# Wrong: silent for 15s while tools run
return await agent.ainvoke(...)
# Right: iterate events with astream / astream_events
async for event in agent.astream(..., stream_mode="updates"): ...
```

❌ Mistake 2: Proxy buffering swallows chunks.
✅ Correct: `X-Accel-Buffering: no` and flush.

❌ Mistake 3: Not cancelling the agent when the client leaves.
✅ Correct: check `request.is_disconnected()` and handle `CancelledError`.

---

## 🧠 Tricky Interview Question
**Q**: "You stream tokens to the user, but the response later fails a guardrail (contains PII). The user already saw it. What now?"

**Answer**: Streaming sends unverified text. Options: (1) run guardrails on the input and use constrained prompts so output is safe by design, (2) buffer a small window (sentence level) and check before sending, (3) stream only low-risk parts (status, tool progress) and send the final answer after the check, (4) send a "retract" event so the UI removes the text. For regulated outputs, trade some latency for safety and do not stream raw model text.

---

## ⚫ Interview Questions + Answers

Q1: SSE vs WebSocket?
A1: SSE is one-way server to client over HTTP, simple, auto-reconnect, good for LLM text. WebSocket is two-way, useful for interactive/voice apps, but needs more infra.

Q2: What is time to first token (TTFT)?
A2: The delay before the first token arrives. Streaming lowers perceived latency even if total time stays the same.

Q3: What do `stream_mode="updates"` and `"messages"` return in LangGraph?
A3: `updates` returns each node's state update after the node finishes; `messages` returns LLM token chunks with metadata as they are generated.

Q4: How do you get token usage when streaming?
A4: With OpenAI use `stream_options={"include_usage": True}` to get a final usage chunk; Anthropic sends usage in `message_start` and `message_delta` events.

Q5: (Hard) How do you stream tool-call arguments safely?
A5: Tool-call arguments arrive as partial JSON fragments. Accumulate by `index`/id and parse only when complete; never execute on partial JSON. For parallel calls keep separate buffers, and show only the tool name in the UI until arguments are complete.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UI, long answers, multi-step agents
- You want visible progress and lower perceived latency

❌ Avoid when:
- Batch or background jobs (no human watching)
- Output must be validated as a whole (strict JSON)
- Clients or proxies cannot handle streaming

---

## 📊 Visual Diagram
```
Agent (LLM + tools)
   │ events: status → tool → token token token → usage → done
   ▼
Async generator ──► SSE formatter ──► HTTP chunked response ──► Browser
                                                      ▲
                      client disconnects ─────────────┘ → cancel agent
```

---

## 💰 Cost Impact
Streaming itself does not change token price. It can save money indirectly: if the user stops or leaves, you cancel generation and avoid paying for the rest of the output. Usage data arrives at the end (OpenAI needs `include_usage`), so log it from the final chunk. Extra cost is only server connections held open; use async servers so thousands of streams are cheap.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSE | Server-Sent Events, one-way stream | Server से client को एकतरफा stream |
| TTFT | Time to first token | पहला token आने तक का समय |
| Chunk | Small piece of output | आउटपुट का छोटा टुकड़ा |
| Async generator | `async def` with `yield` | yield वाला async function |
| Backpressure | Slow consumer limits producer | धीमा consumer, producer को रोकता है |
| Buffering | Proxy holds data before sending | Proxy का डेटा रोककर रखना |

---

## ⚡ 3-Line Summary
English: Stream both tokens and step events so users see progress while the agent works. Use async generators with SSE in FastAPI, disable proxy buffering, and cancel work on disconnect. Remember streamed text is unverified, so guardrails need care.
Hindi: Tokens और step events दोनों stream करो ताकि user को progress दिखे। FastAPI में async generator और SSE इस्तेमाल करो, proxy buffering बंद रखो, और disconnect पर काम रोक दो। Streamed text verify नहीं होता, इसलिए guardrails सोच-समझकर लगाओ।

---

## ➡️ Next Topic
**312. Agent Observability** — tracing every step, token and cost so you can debug what the agent did.
