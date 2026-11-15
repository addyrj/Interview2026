---

# Q235. Server-sent events (SSE)
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Implement a Server-Sent Events endpoint `/events` that pushes `tick` events with ids and then an `end` event. Format frames correctly (`id:`, `event:`, `data:` + blank line) and show how to stop when the client disconnects.

---

## 💡 Quick Concept (2 lines only)
SSE = one-way server->browser stream over plain HTTP with `Content-Type: text/event-stream`. Each message is text lines ending with a BLANK line; browsers use `EventSource` and auto-reconnect.
हिंदी: SSE में server अकेले browser को events भेजता है; हर event के बाद खाली line ज़रूरी है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # simulated delay
import json  # encode data
from collections.abc import AsyncIterator  # type
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # SSE is a streaming response
from fastapi.testclient import TestClient  # client

app = FastAPI()  # app

def sse(data: dict, event: str | None = None, id_: int | None = None) -> str:  # format one SSE frame
    out = ""  # build text
    if id_ is not None:  # optional id (for Last-Event-ID resume)
        out += f"id: {id_}\n"  # id line
    if event:  # optional event name
        out += f"event: {event}\n"  # event line
    out += f"data: {json.dumps(data)}\n\n"  # data line + BLANK LINE ends the frame
    return out  # frame text

async def ticker(n: int) -> AsyncIterator[str]:  # event source
    for i in range(1, n + 1):  # n ticks
        await asyncio.sleep(0.01)  # simulated wait for new data
        yield sse({"tick": i}, event="tick", id_=i)  # push one event
    yield sse({"done": True}, event="end")  # final event

@app.get("/events")  # route
async def events(n: int = 2) -> StreamingResponse:  # handler
    return StreamingResponse(  # SSE = streaming with special type
        ticker(n), media_type="text/event-stream",  # required content type
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # stop proxies buffering
    )

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
r = client.get("/events", params={"n": 2})  # read whole stream (it ends)
print(r.headers["content-type"])  # Expected: text/event-stream; charset=utf-8
print(r.text)  # Expected: 3 frames (see below)
# id: 1
# event: tick
# data: {"tick": 1}
#
# id: 2
# event: tick
# data: {"tick": 2}
#
# event: end
# data: {"done": true}

# Parse like a browser EventSource would:
frames = [f for f in r.text.split("\n\n") if f]  # frames end with blank line
events = [dict(line.split(": ", 1) for line in f.splitlines()) for f in frames]  # key: value lines
print([e["event"] for e in events])  # Expected: ['tick', 'tick', 'end']
```

---

## 🔍 Why This Works (3 lines max)
It is just a `StreamingResponse` with the right media type and frame format. The blank line (`\n\n`) ends a frame; `id:` lets the browser resume with `Last-Event-ID`. `no-cache` and `X-Accel-Buffering: no` stop proxies from buffering the stream.
हिंदी: SSE असल में `StreamingResponse` + सही format है; `\n\n` से frame खत्म होता है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: detect client disconnect while streaming ----
from fastapi import Request  # to ask if client left

app2 = FastAPI()  # app

@app2.get("/live")  # route
async def live(request: Request) -> StreamingResponse:  # handler
    async def gen() -> AsyncIterator[str]:  # generator
        for i in range(100):  # long stream
            if await request.is_disconnected():  # client gone? stop work
                break  # avoid leaking the task
            yield sse({"i": i})  # push
            await asyncio.sleep(0.01)  # wait
    return StreamingResponse(gen(), media_type="text/event-stream")  # response

with TestClient(app2).stream("GET", "/live") as s:  # open stream
    first = next(s.iter_lines())  # read just first line, then close
    print(first)  # Expected: data: {"i": 0}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting the blank line -> the browser never dispatches the event
yield f"data: {payload}\n"
# ✅ Correct: end every frame with TWO newlines
yield f"data: {payload}\n\n"

# ❌ Wrong: wrong media_type ("text/plain") -> EventSource refuses to connect
# ❌ Wrong: infinite loop that never checks request.is_disconnected() -> leaks work after the client leaves
```

---

## 🎯 Interview Tip (1 line)
Say: "SSE for one-way live updates (progress, LLM tokens); WebSockets only when I need two-way; SSE is simpler and reconnects automatically."

---

## 🔗 Related Questions
→ Q227 (WebSocket) | Q234 (streaming) | Q220 (async generators) | Q213 (polling)
