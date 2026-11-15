---

# 322. Server-Sent Events
# हिंदी में: Server-Sent Events (SSE) - server से browser को live stream

---

## 🔵 Simple Definition (English)
Server-Sent Events (SSE) is a plain HTTP response that never ends: the server keeps the connection open and sends text events (`data: ...`) whenever it wants. The browser reads them with `EventSource`. It is one-way: server to client.

## 🔵 सरल परिभाषा (Hindi)
Server-Sent Events (SSE) ऐसा सादा HTTP response है जो खत्म नहीं होता: server connection खुला रखकर जब चाहे text events (`data: ...`) भेजता है। Browser इन्हें `EventSource` से पढ़ता है। यह एक-तरफ़ा है: server से client।

---

## 🔴 Problem it Solves
Many live features only need the server to push: job progress bars, notifications, ChatGPT-style token streaming. WebSockets are heavier (custom protocol, manual reconnect). SSE works over normal HTTP, passes through proxies easily and the browser reconnects automatically.

## 🔴 यह क्यों बना? (Hindi)
कई live features में सिर्फ़ server को push करना होता है: job progress bar, notifications, ChatGPT जैसी token streaming। WebSocket भारी है (अलग protocol, manual reconnect)। SSE सादे HTTP पर चलता है, proxies से आसानी से निकलता है और browser अपने आप reconnect करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser: `new EventSource('/events')` sends GET
Step 2 → Server replies `Content-Type: text/event-stream` and keeps the response open
Step 3 → Server yields frames: optional `id:`, `event:`, then `data:` lines, ended by a blank line (`\n\n`)
Step 4 → Browser fires `onmessage` (or a named event listener) per frame
Step 5 → Connection drops → browser reconnects and sends `Last-Event-ID`
Step 6 → Server resumes after that id
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser: `new EventSource('/events')` GET भेजता है
Step 2 → Server `Content-Type: text/event-stream` के साथ response खुला रखता है
Step 3 → Server frames yield करता है: `id:`, `event:`, `data:` lines, और अंत में खाली line (`\n\n`)
Step 4 → हर frame पर browser `onmessage` (या named listener) चलाता है
Step 5 → Connection टूटे तो browser reconnect करता है और `Last-Event-ID` भेजता है
Step 6 → Server उसी id के बाद से आगे भेजता है
```

---

## 🟡 Real World Example
A report-export page shows live progress (`33%... 66%... done`) from a long job. An LLM chat endpoint streams tokens to the UI as they are generated. A Flipkart-style order page receives status changes (packed, shipped, out for delivery) without refresh.

## 🟡 Real Example Hindi mein
Report-export page लंबे job का live progress (`33%... 66%... done`) दिखाता है। LLM chat endpoint tokens बनते ही UI पर stream करता है। Flipkart जैसा order page बिना refresh के status बदलाव (packed, shipped, out for delivery) पाता है।

---

## 💻 Code Example — Basic
Stream three events with `StreamingResponse` and an async generator.

```python
# Basic Server-Sent Events using StreamingResponse - every line commented
import asyncio  # for sleep
from collections.abc import AsyncIterator  # type hint for async generator
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # streaming body
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # app


async def ticker() -> AsyncIterator[str]:  # async generator of SSE frames
    for i in range(3):  # three events
        yield f"data: tick {i}\n\n"  # SSE frame ends with a blank line
        await asyncio.sleep(0)  # yield control (use a real delay in prod)


@app.get("/events")  # SSE endpoint
async def events() -> StreamingResponse:  # return a stream
    return StreamingResponse(ticker(), media_type="text/event-stream")  # right content type


client: TestClient = TestClient(app)  # client
r = client.get("/events")  # read whole stream
print(r.headers["content-type"])  # SSE content type
# Output: text/event-stream; charset=utf-8
print(repr(r.text))  # raw frames
# Output: 'data: tick 0\n\ndata: tick 1\n\ndata: tick 2\n\n'
```

## 💻 Code Example — Advanced
Production frames: id + event name + JSON, resume with `Last-Event-ID`, no-cache and proxy buffering headers.

```python
# Production style: SSE with event names, ids, JSON and cache-control headers
import asyncio  # sleep
import json  # JSON payloads
from collections.abc import AsyncIterator  # type hint
from fastapi import FastAPI, Header  # Header reads Last-Event-ID
from fastapi.responses import StreamingResponse  # stream
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # app


def sse(event: str, data: dict, event_id: int) -> str:  # build one frame
    return f"id: {event_id}\nevent: {event}\ndata: {json.dumps(data)}\n\n"  # SSE text format


async def job_progress(start_after: int) -> AsyncIterator[str]:  # stream a job
    for step in range(start_after + 1, 4):  # resume after last seen id
        yield sse("progress", {"percent": step * 33}, step)  # progress event
        await asyncio.sleep(0)  # non-blocking pause
    yield sse("done", {"ok": True}, 4)  # final event


@app.get("/jobs/{job_id}/stream")  # SSE route
async def stream(job_id: int, last_event_id: int = Header(0)) -> StreamingResponse:  # header Last-Event-ID
    headers: dict[str, str] = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}  # stop proxy buffering
    return StreamingResponse(job_progress(last_event_id), media_type="text/event-stream", headers=headers)  # stream


client: TestClient = TestClient(app)  # client
print(client.get("/jobs/1/stream").text)  # full stream
# Output: 4 frames: ids 1,2,3 (event: progress, percent 33/66/99) then id 4 (event: done)
print(client.get("/jobs/1/stream", headers={"Last-Event-ID": "2"}).text)  # reconnect after id 2
# Output: only 2 frames: id 3 (progress, 99) and id 4 (done)
```

---

## 🟠 JavaScript vs Python Comparison

```python
@app.get("/events")
async def events():
    async def gen():
        for i in range(3):
            yield f"data: tick {i}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(gen(), media_type="text/event-stream")
```

```javascript
// Express
app.get('/events', (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' });
  let i = 0;
  const t = setInterval(() => res.write(`data: tick ${i++}\n\n`), 1000);
  req.on('close', () => clearInterval(t));
});
// browser: new EventSource('/events').onmessage = e => console.log(e.data);
```

Both write text frames to an open response. Express uses `res.write` plus manual cleanup on `close`; FastAPI uses a generator, and Starlette stops iterating when the client disconnects. The browser `EventSource` code is identical.

---

## 🟠 FastAPI Connection
FastAPI streams with `StreamingResponse` and `text/event-stream` (recent FastAPI versions, e.g. 0.162 used here, also ship `fastapi.sse.EventSourceResponse` + `ServerSentEvent`, which formats frames for you; the manual way below works on every version). `EventSource` cannot send custom headers or POST, so for POST chat streaming use `fetch` + reader. Behind nginx set `X-Accel-Buffering: no` / `proxy_buffering off`.

```python
import asyncio
from collections.abc import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app: FastAPI = FastAPI()


async def tokens(request: Request) -> AsyncIterator[str]:
    for word in ["Hello", "from", "the", "LLM"]:
        if await request.is_disconnected():  # stop if the user left
            break
        yield f"data: {word}\n\n"
        await asyncio.sleep(0.1)
    yield "event: done\ndata: end\n\n"


@app.get("/chat/stream")
async def chat_stream(request: Request) -> StreamingResponse:
    return StreamingResponse(tokens(request), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

Newer helper (FastAPI 0.162, verified; output was `'event: tick\ndata: {"n": 1}\nid: 1\n\ndata: {"n": 2}\n\n'`):

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app: FastAPI = FastAPI()


@app.get("/e", response_class=EventSourceResponse)
async def e() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data={"n": 1}, event="tick", id="1")  # explicit fields
    yield {"n": 2}  # plain objects become data: frames
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing the blank line after a frame
```python
yield 'data: hello\n'  # frame never completes
```
✅ Correct:
```python
yield 'data: hello\n\n'  # two newlines end the frame
```

❌ Mistake 2: Using a blocking sleep in an async generator
```python
async def gen():
    time.sleep(1)  # blocks every request
    yield 'data: x\n\n'
```
✅ Correct:
```python
async def gen():
    await asyncio.sleep(1)
    yield 'data: x\n\n'
```

❌ Mistake 3: Proxy buffering hides the stream
```python
# nginx default buffers: client sees nothing until the end
```
✅ Correct:
```python
# headers X-Accel-Buffering: no  /  nginx: proxy_buffering off;
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()

def gen():
    yield "data: a\n"
    yield "data: b\n\n"

@app.get("/")
def root():
    return StreamingResponse(gen(), media_type="text/event-stream")

print(repr(TestClient(app).get("/").text))
```

**Answer**:
```
'data: a\ndata: b\n\n'
```
The first yield ends with one `\n`, so it is NOT a complete frame. A browser joins consecutive `data:` lines into a single event whose data is `a\nb`. Only a blank line (`\n\n`) dispatches the event.

---

## ⚫ Interview Questions + Answers

Q1: SSE vs WebSocket?
A1: SSE: one-way, plain HTTP, auto-reconnect, text only. WebSocket: two-way, binary, manual reconnect. Use SSE for notifications/progress/token streams.

Q2: How does reconnection work?
A2: The browser reconnects automatically and sends `Last-Event-ID` with the last `id:` it saw. The server can resume from there.

Q3: Can EventSource send POST or auth headers?
A3: No, only GET and cookies. Use query tokens, cookies, or `fetch()` with a stream reader instead.

Q4: Why do my events arrive all at once?
A4: A proxy or gzip middleware is buffering. Disable buffering (`X-Accel-Buffering: no`) and avoid compressing the stream.

Q5: Why is the media type `text/event-stream`?
A5: It tells the browser to parse the body as SSE frames and keep the connection open.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Progress bars, notifications, live feeds (server to client)
- LLM token streaming
- You want simple infra and auto-reconnect

❌ Avoid when:
- Two-way real-time (use WebSocket)
- Binary data
- Clients that must send custom headers with EventSource

---

## 📊 Visual Diagram

```
Browser                       FastAPI
 EventSource GET /events ----> StreamingResponse(gen)
                    <--- id: 1\nevent: progress\ndata: {...}\n\n
                    <--- id: 2 ...                (connection stays open)
 (drop) -- reconnect, Last-Event-ID: 2 -->  resume from id 3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSE | Server-Sent Events, one-way stream | server से client तक एक-तरफ़ा stream |
| EventSource | Browser SSE client | browser का SSE client |
| Frame | One event ended by blank line | खाली line से खत्म एक event |
| Last-Event-ID | Resume header | आगे से शुरू करने वाला header |
| StreamingResponse | Send body in pieces | टुकड़ों में body भेजना |
| Buffering | Proxy holding data back | proxy का data रोकना |

---

## ⚡ 3-Line Summary
English: SSE keeps an HTTP response open and pushes `data:` frames ended by a blank line. It is one-way, auto-reconnects and suits progress, notifications and LLM streaming. Disable proxy buffering.
Hindi: SSE HTTP response खुला रखकर `data:` frames भेजता है जो खाली line से खत्म होते हैं। यह एक-तरफ़ा है, अपने आप reconnect होता है और progress, notifications व LLM streaming के लिए सही है। Proxy buffering बंद रखें।

---

## ➡️ Next Topic
**323. Lifespan Events (startup + shutdown)** — open and close DB pools and clients once per app.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. The `fa_code` chat-stream snippet and the browser EventSource side were not run; the generator frames were checked via TestClient.
