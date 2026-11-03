---

# 533. Design: Real-time AI Chat
# हिंदी में: Real-time AI Chat का System Design

---

## 🔵 Simple Definition (English)
A real-time AI chat system lets a user talk to an LLM and see the answer appear token by token, like typing. It needs a persistent connection (WebSocket or Server-Sent Events), conversation memory, and a streaming LLM call. The goal is low "time to first token", not just low total time.

## 🔵 सरल परिभाषा (Hindi)
Real-time AI chat system में user LLM से बात करता है और जवाब token-by-token स्क्रीन पर आता है, जैसे कोई type कर रहा हो। इसके लिए persistent connection (WebSocket या SSE), conversation memory और streaming LLM call चाहिए। लक्ष्य "time to first token" कम रखना है, सिर्फ total time नहीं।

---

## 🔴 Problem it Solves
A normal HTTP request waits for the full answer. An LLM can take 5-20 seconds to finish, so the user stares at a blank screen and thinks the app is broken. Also, chat needs history, many users at once, and the ability to cancel a reply midway.

## 🔴 यह क्यों बना? (Hindi)
Normal HTTP request पूरा जवाब बनने तक रुकता है। LLM को 5-20 seconds लग सकते हैं, user खाली screen देखता रहता है। Chat को history, एक साथ कई users, और बीच में reply cancel करने की सुविधा भी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client opens WebSocket /ws/chat/{session_id} (auth token in query/header)
Step 2 → Server loads last N messages of the session from Redis
Step 3 → Server trims history to a token budget (system prompt + history + new msg)
Step 4 → Server calls the LLM with stream=True
Step 5 → Each chunk is pushed to the client the moment it arrives
Step 6 → On "done", the full reply is saved to Redis / DB and token usage is logged
Step 7 → If the client disconnects or sends "stop", the LLM stream is cancelled
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Client WebSocket खोलता है (auth token के साथ)
Step 2 → Server Redis से session के पिछले N messages लोड करता है
Step 3 → History को token budget में trim करता है
Step 4 → LLM को stream=True के साथ call करता है
Step 5 → हर chunk आते ही client को push होता है
Step 6 → पूरा reply Redis/DB में save होता है, token usage log होता है
Step 7 → Client disconnect या "stop" पर LLM stream cancel हो जाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer chats: "What HS code fits a lithium power bank?" The assistant streams the reasoning ("Checking Chapter 85...") so the officer sees progress within 300 ms. Follow-up "and if it is 10000 mAh?" works because the session history is kept.
**Zomato-style**: A food chatbot streams "Here are 3 biryani places near you..." while the restaurant search tool runs in parallel.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer पूछता है "Lithium power bank का HS code क्या होगा?" Assistant reasoning stream करता है ("Chapter 85 check कर रहा हूँ...") तो officer को 300 ms में progress दिखता है। अगला सवाल "10000 mAh हो तो?" भी चलता है क्योंकि session history saved है।
**Zomato-style**: Food chatbot "यहाँ 3 biryani places हैं..." stream करता है जबकि restaurant search tool साथ में चल रहा होता है।

---

## 💻 Code Example — Basic
```python
# Basic: simulate token streaming with an async generator (no API key, pure Python)
import asyncio                                   # asyncio gives us async/await
from typing import AsyncIterator                 # type hint for async generators


async def fake_llm_stream(prompt: str) -> AsyncIterator[str]:
    """Pretend LLM: yields one word at a time."""
    answer = f"HS code for '{prompt}' is likely 8507.60 (Li-ion batteries)."  # canned answer
    for word in answer.split():                  # loop over words
        await asyncio.sleep(0.05)                # simulate network/model delay
        yield word + " "                         # send one chunk


async def main() -> None:
    """Consume the stream and print as it arrives."""
    async for chunk in fake_llm_stream("power bank"):   # receive chunks one by one
        print(chunk, end="", flush=True)                 # print without newline
    print()                                              # final newline


asyncio.run(main())                              # start the event loop
```

## 💻 Code Example — Advanced
```python
# Production style: WebSocket chat with session memory, token budget, cancel, error handling
import asyncio                                           # for cancellation and sleep
import json                                              # JSON frames over WebSocket
import os                                                # read API key
from typing import AsyncIterator                         # type hints

from fastapi import FastAPI, WebSocket, WebSocketDisconnect   # FastAPI WebSocket support

app = FastAPI()                                          # create the app
SESSIONS: dict[str, list[dict[str, str]]] = {}           # in-memory store (use Redis in prod)
MAX_HISTORY_CHARS = 8000                                 # crude budget (use tiktoken in prod)


def trim_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep newest messages that fit the budget."""
    kept: list[dict[str, str]] = []                      # result list
    used = 0                                             # characters used so far
    for msg in reversed(history):                        # walk from newest to oldest
        used += len(msg["content"])                      # add this message size
        if used > MAX_HISTORY_CHARS:                     # over budget?
            break                                        # stop adding older messages
        kept.append(msg)                                 # keep it
    return list(reversed(kept))                          # restore chronological order


async def llm_stream(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    """Stream from OpenAI if key exists, else a mock."""
    if not os.getenv("OPENAI_API_KEY"):                  # offline mode
        for w in "Mock reply for offline testing.".split():   # fake words
            await asyncio.sleep(0.02)                    # fake delay
            yield w + " "                                # fake chunk
        return                                           # finish
    from openai import AsyncOpenAI                       # import only when needed
    client = AsyncOpenAI()                               # async client
    stream = await client.chat.completions.create(       # open streaming request
        model="gpt-4o-mini", messages=messages, stream=True)   # model is illustrative
    async for event in stream:                           # iterate events
        delta = event.choices[0].delta.content           # new text piece (may be None)
        if delta:                                        # skip empty events
            yield delta                                  # forward to caller


@app.websocket("/ws/chat/{session_id}")
async def chat(ws: WebSocket, session_id: str) -> None:
    """One WebSocket per user session."""
    await ws.accept()                                    # complete the handshake
    history = SESSIONS.setdefault(session_id, [])        # get or create session
    try:
        while True:                                      # keep serving messages
            text = (await ws.receive_text()).strip()     # wait for the user message
            if not text:                                 # ignore empty input
                continue
            history.append({"role": "user", "content": text})   # save user message
            messages = [{"role": "system", "content": "You are a tariff assistant."}] + trim_history(history)
            reply = ""                                   # collect full reply
            try:
                async for chunk in llm_stream(messages): # stream tokens
                    reply += chunk                       # accumulate
                    await ws.send_text(json.dumps({"type": "token", "data": chunk}))   # push
                history.append({"role": "assistant", "content": reply})   # save reply
                await ws.send_text(json.dumps({"type": "done"}))          # signal end
            except Exception as exc:                     # LLM or network failure
                await ws.send_text(json.dumps({"type": "error", "data": str(exc)}))   # tell client
    except WebSocketDisconnect:                          # client left
        pass                                             # nothing to clean in this sketch
```

---

## 🟠 FastAPI Integration
WebSocket is best for two-way chat (stop button, typing indicator). Server-Sent Events (SSE) via `StreamingResponse` is simpler, works through most proxies, and is enough when the client only listens.

```python
# SSE endpoint: simple one-way streaming
from fastapi import FastAPI                              # framework
from fastapi.responses import StreamingResponse          # streaming response class
import asyncio                                           # sleep for demo

app = FastAPI()                                          # app instance


async def event_gen(q: str):                             # generator yielding SSE frames
    for w in f"Answer for {q}".split():                  # demo words
        await asyncio.sleep(0.05)                        # demo delay
        yield f"data: {w}\n\n"                           # SSE format: 'data: ...' + blank line
    yield "data: [DONE]\n\n"                             # end marker


@app.get("/chat/sse")
async def chat_sse(q: str) -> StreamingResponse:         # query param q
    return StreamingResponse(event_gen(q), media_type="text/event-stream")   # stream it
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models expose `astream`, which yields message chunks. LangGraph can stream per-node updates with `astream(..., stream_mode="messages")`, and a checkpointer stores conversation state per `thread_id`.

```python
# LangChain streaming (needs OPENAI_API_KEY)
from langchain_openai import ChatOpenAI                  # chat model wrapper

llm = ChatOpenAI(model="gpt-4o-mini")                    # illustrative model name


async def stream_answer(q: str) -> None:
    async for chunk in llm.astream(q):                   # async token stream
        print(chunk.content, end="", flush=True)         # print each piece
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Blocking call inside the async handler
✅ Correct: use the async client and `await`.

```python
# Wrong: sync client blocks the event loop, all users freeze
# reply = OpenAI().chat.completions.create(...)
# Right: AsyncOpenAI with stream=True
# stream = await AsyncOpenAI().chat.completions.create(..., stream=True)
```

❌ Mistake 2: Unlimited history sent every turn
✅ Correct: trim or summarize old messages, otherwise cost and latency grow every turn.

❌ Mistake 3: Not stopping the LLM when the client disconnects
✅ Correct: catch `WebSocketDisconnect` and cancel the task, so you stop paying for unused tokens.

---

## 🧠 Tricky Interview Question
**Q**: "You run 4 server instances behind a load balancer. A user's second message lands on a different instance. The chat loses context. How do you fix it?"

**Answer**: In-memory history is per process. Move session state to a shared store (Redis keyed by session_id), so any instance can serve any turn. For WebSocket, the connection itself is sticky to one instance, but reconnects can land elsewhere, so state must be external. Use Redis pub/sub if one instance needs to push to a socket held by another.

---

## ⚫ Interview Questions + Answers

Q1: WebSocket vs SSE for chat?
A1: WebSocket is two-way (stop, typing events). SSE is one-way server to client, simpler, auto-reconnect, works with plain HTTP. Many LLM apps use SSE for tokens plus a normal POST for sending messages.

Q2: What is time to first token (TTFT)?
A2: Time from sending the request to seeing the first token. It drives perceived speed. Streaming reduces perceived latency even if total time is the same.

Q3: How do you keep conversation history within the context window?
A3: Count tokens, keep a sliding window of recent messages, and summarize older ones. Always keep the system prompt. Reserve room for the reply (`max_tokens`).

Q4: How do you scale WebSocket servers?
A4: Make servers stateless (state in Redis), use a load balancer that supports WebSocket upgrade, set idle timeouts and heartbeats (ping/pong), and autoscale on number of open connections.

Q5: (Hard) Design for 100k concurrent chat users with rate limiting and cost control.
A5: Gateway with auth and per-user token bucket rate limit; stateless chat pods autoscaled on connections; Redis for sessions; a queue/semaphore to cap concurrent LLM calls per provider limits; fallback model on 429; usage metering per user from `usage` fields; cancel streams on disconnect; observability (TTFT, tokens, error rate).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers are long and users wait for them
- Conversational follow-ups matter
- You want stop/regenerate controls

❌ Avoid when:
- Output is short structured JSON (streaming partial JSON is awkward)
- Batch/offline jobs, where a normal request is simpler

---

## 📊 Visual Diagram
```
 Browser ──WS/SSE──▶ Load Balancer ──▶ Chat Pod (FastAPI)
    ▲                                     │   │
    │ tokens                              │   └─▶ Redis (session history)
    └─────────────────────────────────────┤
                                          ▼
                                   LLM API (stream)
                                          │
                                   Usage log / metrics
```

---

## 💰 Cost Impact
Every turn re-sends history, so input tokens grow roughly linearly per turn and total cost grows roughly quadratically over a long chat. Example (illustrative): 20 turns, 300 new tokens per turn, no trimming means turn 20 sends about 6,000 input tokens.
Optimize: sliding window plus summary, prompt caching for the fixed system prompt (provider feature), `max_tokens` cap, small model for easy turns, cancel on disconnect. Streaming itself does not change price.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Two-way persistent connection | दो-तरफा स्थायी connection |
| SSE | Server-Sent Events, one-way stream | Server से client one-way stream |
| TTFT | Time to first token | पहला token आने का समय |
| Session | One conversation's state | एक बातचीत की state |
| Backpressure | Slow consumer slows producer | धीमे client के कारण producer रुकना |
| Heartbeat | Periodic ping to keep connection alive | Connection जिंदा रखने का ping |

---

## ⚡ 3-Line Summary
English: Real-time chat streams tokens over WebSocket or SSE for low perceived latency. Keep state in Redis so any pod can serve any turn. Trim history and cancel on disconnect to control cost.
Hindi: Real-time chat में tokens WebSocket या SSE पर stream होते हैं ताकि user को जल्दी जवाब दिखे। State Redis में रखो ताकि कोई भी pod serve कर सके। History trim करो और disconnect पर cancel करो ताकि cost कम रहे।

---

## ➡️ Next Topic
**534. Design: Document QA System**: chat over uploaded documents using RAG, adding ingestion and retrieval to what we built here.
