---

# 400. FastAPI for AI APIs
# हिंदी में: AI APIs के लिए FastAPI (streaming, timeout, rate limit)

---

## 🔵 Simple Definition (English)
Serving an AI model or LLM through FastAPI means wrapping slow, costly calls in async endpoints with validation, streaming, timeouts, concurrency limits and per-key rate limits. FastAPI keeps the server responsive while the model thinks.

## 🔵 सरल परिभाषा (Hindi)
AI model या LLM को FastAPI से serve करने का मतलब है धीमे और महँगे calls को async endpoints में रखना, साथ में validation, streaming, timeout, concurrency limit और per-key rate limit लगाना। Model के सोचते समय भी server responsive रहता है।

---

## 🔴 Problem it Solves
LLM calls take 2 to 30 seconds and cost money per token. A naive sync endpoint blocks workers, users wait for the full answer before seeing anything, one slow call hangs the request forever, and one abusive client burns your whole budget. AI APIs need streaming, timeouts, backpressure and rate limits that ordinary CRUD APIs often skip.

## 🔴 यह क्यों बना? (Hindi)
LLM call में 2 से 30 सेकंड लगते हैं और हर token का पैसा लगता है। साधारण sync endpoint workers को block करता है, user को पूरा जवाब आने तक कुछ दिखता नहीं, एक धीमा call request को हमेशा लटका सकता है, और एक गलत client आपका पूरा budget खत्म कर सकता है। AI APIs में streaming, timeout, backpressure और rate limit ज़रूरी हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends POST /chat with a validated Pydantic body
Step 2 → Dependencies run: API key check, rate limit, get shared LLM client
Step 3 → Endpoint is `async def`, so awaiting the LLM does not block other requests
Step 4 → asyncio.wait_for adds a hard timeout (504 on expiry)
Step 5 → A Semaphore caps how many LLM calls run at once (backpressure)
Step 6 → For streaming, StreamingResponse sends tokens as Server-Sent Events
Step 7 → Lifespan creates the client once at startup and closes it at shutdown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client validated Pydantic body के साथ POST /chat भेजता है
Step 2 → Dependencies चलती हैं: API key check, rate limit, shared LLM client
Step 3 → Endpoint `async def` है, इसलिए LLM का इंतज़ार बाकी requests को block नहीं करता
Step 4 → asyncio.wait_for hard timeout लगाता है (समय पूरा होने पर 504)
Step 5 → Semaphore एक साथ चलने वाले LLM calls की संख्या सीमित करता है
Step 6 → Streaming में StreamingResponse tokens को Server-Sent Events से भेजता है
Step 7 → Lifespan startup पर client एक बार बनाता है और shutdown पर बंद करता है
```

---

## 🟡 Real World Example
A chatbot backend for a Swiggy-like app streams the reply word by word so the UI feels instant, like ChatGPT. A RAG search API for internal docs limits each API key to a number of calls per minute and returns 504 if the model is slow. An image-captioning service runs the heavy model in a worker and keeps the web API light.

## 🟡 Real Example Hindi mein
Swiggy जैसे app का chatbot backend जवाब को शब्द-शब्द streaming से भेजता है ताकि UI ChatGPT की तरह तुरंत चलता दिखे। Internal docs की RAG search API हर API key को प्रति मिनट सीमित calls देती है और model धीमा हो तो 504 लौटाती है। Image-captioning service भारी model को worker में चलाती है और web API हल्की रखती है।

---

## 💻 Code Example — Basic
```python
# Basic: chat endpoint + SSE streaming, tested in-process (pip install fastapi httpx)
import asyncio  # for sleep(0) to yield control
import json  # to build SSE payloads
from typing import AsyncIterator  # type for async generators
from fastapi import FastAPI, HTTPException  # app and errors
from fastapi.responses import StreamingResponse  # streaming body
from fastapi.testclient import TestClient  # in-process test client
from pydantic import BaseModel, Field  # validation models

app: FastAPI = FastAPI()  # create the app


class ChatRequest(BaseModel):  # request body
    prompt: str = Field(min_length=1, max_length=200)  # reject empty or huge prompts
    stream: bool = False  # optional flag


class ChatResponse(BaseModel):  # response body
    answer: str  # model text
    tokens: int  # rough word count


async def fake_llm_stream(prompt: str) -> AsyncIterator[str]:  # pretend LLM yielding tokens
    for word in f"Echo: {prompt}".split():  # one word at a time
        await asyncio.sleep(0)  # let other requests run
        yield word + " "  # one token


@app.post("/chat", response_model=ChatResponse)  # normal JSON endpoint
async def chat(req: ChatRequest) -> ChatResponse:  # async so we never block the loop
    if "forbidden" in req.prompt:  # simple safety rule
        raise HTTPException(status_code=400, detail="blocked")  # client error
    text: str = "".join([c async for c in fake_llm_stream(req.prompt)]).strip()  # collect tokens
    return ChatResponse(answer=text, tokens=len(text.split()))  # typed response


@app.post("/chat/stream")  # streaming endpoint
async def chat_stream(req: ChatRequest) -> StreamingResponse:  # returns a stream
    async def sse() -> AsyncIterator[str]:  # generator of SSE lines
        async for chunk in fake_llm_stream(req.prompt):  # for each token
            yield f"data: {json.dumps({'token': chunk})}\n\n"  # SSE frame format
        yield "data: [DONE]\n\n"  # tell the client we finished
    return StreamingResponse(sse(), media_type="text/event-stream")  # SSE content type


c: TestClient = TestClient(app)  # test without starting a server
r = c.post("/chat", json={"prompt": "hello world"})  # normal call
print(r.status_code, r.json())  # status and body
# Output: 200 {'answer': 'Echo: hello world', 'tokens': 3}
r = c.post("/chat", json={"prompt": ""})  # fails validation
print(r.status_code, r.json()["detail"][0]["type"])  # 422 with reason
# Output: 422 string_too_short
r = c.post("/chat", json={"prompt": "forbidden"})  # blocked prompt
print(r.status_code, r.json())  # our 400
# Output: 400 {'detail': 'blocked'}
r = c.post("/chat/stream", json={"prompt": "hi there"})  # streaming call
print(r.headers["content-type"])  # event stream type
# Output: text/event-stream; charset=utf-8
print(r.text)  # all frames joined
# Output:
# data: {"token": "Echo: "}
#
# data: {"token": "hi "}
#
# data: {"token": "there "}
#
# data: [DONE]
```

## 💻 Code Example — Advanced
```python
# Production style: lifespan client, semaphore, timeout (504), per-key rate limit (429)
import asyncio  # semaphore and wait_for
from contextlib import asynccontextmanager  # for lifespan
from typing import AsyncIterator, Dict  # type hints
from fastapi import Depends, FastAPI, Header, HTTPException  # framework pieces
from fastapi.testclient import TestClient  # test client
from pydantic import BaseModel, Field  # models


class LLMClient:  # one shared client for all requests
    def __init__(self, max_concurrent: int = 2) -> None:  # limit parallel calls
        self.sem: asyncio.Semaphore = asyncio.Semaphore(max_concurrent)  # backpressure

    async def complete(self, prompt: str, delay: float = 0.0) -> str:  # fake model call
        async with self.sem:  # wait here if too many calls are running
            await asyncio.sleep(delay)  # simulate model latency
            return f"answer to: {prompt}"  # fake answer


@asynccontextmanager  # lifespan replaces on_event startup/shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # runs once per process
    app.state.llm = LLMClient(max_concurrent=2)  # create at startup
    yield  # app serves requests here
    app.state.llm = None  # cleanup at shutdown (close real clients here)


app: FastAPI = FastAPI(lifespan=lifespan)  # attach lifespan
CALLS: Dict[str, int] = {}  # in-memory counter (use Redis in production)


def get_llm() -> LLMClient:  # dependency returning the shared client
    return app.state.llm  # created in lifespan


def rate_limit(x_api_key: str = Header(...)) -> str:  # dependency: required header
    CALLS[x_api_key] = CALLS.get(x_api_key, 0) + 1  # count this call
    if CALLS[x_api_key] > 2:  # allow only 2 calls per key in this demo
        raise HTTPException(status_code=429, detail="rate limit exceeded")  # too many
    return x_api_key  # pass key on


class Ask(BaseModel):  # request body
    prompt: str = Field(min_length=1)  # non-empty
    delay: float = Field(0.0, ge=0, le=5)  # demo knob to simulate slowness


@app.post("/ask")  # endpoint
async def ask(body: Ask, llm: LLMClient = Depends(get_llm), key: str = Depends(rate_limit)) -> Dict[str, str]:
    try:  # guard the slow call
        text: str = await asyncio.wait_for(llm.complete(body.prompt, body.delay), timeout=0.1)  # hard timeout
    except asyncio.TimeoutError:  # model too slow
        raise HTTPException(status_code=504, detail="LLM timed out")  # gateway timeout
    return {"answer": text}  # success


with TestClient(app) as c:  # "with" runs the lifespan
    h = {"X-API-Key": "k1"}  # fake key
    print(c.post("/ask", json={"prompt": "hi"}, headers=h).json())  # call 1 ok
    # Output: {'answer': 'answer to: hi'}
    print(c.post("/ask", json={"prompt": "slow", "delay": 1}, headers=h).status_code)  # call 2 slow
    # Output: 504
    r = c.post("/ask", json={"prompt": "again"}, headers=h)  # call 3 exceeds the limit
    print(r.status_code, r.json())  # 429
    # Output: 429 {'detail': 'rate limit exceeded'}
    print(c.post("/ask", json={"prompt": "x"}).status_code)  # missing header
    # Output: 422
```

---

## 🟠 JavaScript vs Python Comparison
Express/Next.js streaming and FastAPI streaming are the same idea: write chunks to the response as they are produced.

```python
# Python (FastAPI)
@app.get("/stream")  # route
async def stream() -> StreamingResponse:  # async handler
    async def gen():  # async generator
        for i in range(3):  # three chunks
            yield f"data: {i}\n\n"  # SSE frame
    return StreamingResponse(gen(), media_type="text/event-stream")  # send
```
```javascript
// JavaScript (Express)
app.get("/stream", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");  // SSE header
  for (let i = 0; i < 3; i++) res.write(`data: ${i}\n\n`);  // write chunks
  res.end();  // finish
});
```

Key differences: Node is single-threaded async by default; in FastAPI `def` endpoints run in a thread pool but `async def` runs on the event loop, so a blocking call inside `async def` freezes everything. Both use `await` for I/O.

---

## 🟠 FastAPI Connection
This topic is the FastAPI connection. Typical production layout: routers per feature, Pydantic models for I/O, dependencies for auth and rate limits, lifespan for shared clients, background tasks or a queue (Celery, ARQ) for jobs longer than the HTTP timeout, and Gunicorn with Uvicorn workers behind Nginx (disable proxy buffering for SSE).

```python
# Long job pattern: return 202 immediately, work in the background
from fastapi import BackgroundTasks, FastAPI  # tools
from typing import Dict  # type hint

app = FastAPI()  # app
RESULTS: Dict[str, str] = {}  # job store (use Redis/DB in production)


def run_job(job_id: str, prompt: str) -> None:  # runs after the response is sent
    RESULTS[job_id] = f"done: {prompt}"  # save result


@app.post("/jobs/{job_id}", status_code=202)  # accepted, not finished
def create(job_id: str, prompt: str, bg: BackgroundTasks) -> Dict[str, str]:
    bg.add_task(run_job, job_id, prompt)  # schedule work
    return {"status": "queued"}  # reply right away
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
✅ Correct: use an async client, or a plain `def` endpoint / `run_in_threadpool`

```python
# Wrong - freezes the whole event loop for every user
# async def ask(): return requests.post(LLM_URL).json()

# Right - httpx.AsyncClient, awaited
# async def ask(): return (await client.post(LLM_URL)).json()
```

❌ Mistake 2: New HTTP client per request, no timeout
✅ Correct: create the client once in lifespan and always set a timeout

```python
# Wrong: async with httpx.AsyncClient() as c: ... (new pool each request, default 5s)
# Right: app.state.http = httpx.AsyncClient(timeout=30) in lifespan; aclose() on shutdown
```

❌ Mistake 3: In-memory rate limits with many workers
✅ Correct: store counters in Redis; each worker has its own memory

```python
# Wrong: CALLS = {}   # each of 4 Gunicorn workers keeps its own count
# Right: Redis INCR key with EXPIRE (or slowapi / API gateway limits)
```

---

## 🧠 Tricky Interview Question

**Q**: Two requests hit this endpoint at the same time. How long do both take in total?

```python
import time
from fastapi import FastAPI
app = FastAPI()

@app.get("/a")
async def a():
    time.sleep(2)
    return "a"

@app.get("/b")
def b():
    time.sleep(2)
    return "b"
```

**Answer**: Two simultaneous calls to `/a` take about 4 seconds (serial) because `time.sleep` blocks the event loop inside `async def`. Two simultaneous calls to `/b` take about 2 seconds, because FastAPI runs plain `def` endpoints in a thread pool. Fix `/a` with `await asyncio.sleep(2)`. The same trap appears when someone calls `requests` or a sync SDK inside an async endpoint.

---

## ⚫ Interview Questions + Answers

Q1: SSE or WebSocket for LLM streaming?
A1: SSE is simpler: one-way server to client over plain HTTP, auto-reconnect in browsers, works with proxies. WebSocket is two-way and fits voice or live collaboration.

Q2: Why a Semaphore?
A2: It limits concurrent model calls so you do not hit provider rate limits or run out of GPU memory. Excess requests wait instead of failing.

Q3: Where do I load a big ML model?
A3: In `lifespan` (once per worker), store it on `app.state`. Never load inside the endpoint. With N workers you hold N copies in memory.

Q4: How do you handle slow jobs (over 30 seconds)?
A4: Return 202 with a job id, process in a queue worker (Celery, ARQ), and let the client poll or use webhooks/SSE.

Q5: What status codes matter?
A5: 422 bad input (automatic), 429 rate limit, 504 upstream timeout, 502 bad upstream reply, 503 overloaded.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You expose LLM, RAG or model inference over HTTP
- You need streaming, validation and OpenAPI docs together
- Mostly I/O waiting (calling provider APIs)

❌ Avoid when:
- Heavy CPU/GPU inference inside the web process (use a model server such as vLLM/Triton or a worker queue)
- A simple batch job with no HTTP need

---

## 📊 Visual Diagram

```
Client ──► Nginx ──► Uvicorn worker (FastAPI)
                        │ Depends: auth -> rate limit -> llm client
                        ▼
                 Semaphore (max N) ──► wait_for(timeout) ──► LLM provider
                        │
              SSE chunks "data: ...\n\n" streamed back to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSE | One-way stream of text events over HTTP | Server से client को लगातार events |
| Lifespan | Startup and shutdown hook | Startup/shutdown का hook |
| Semaphore | Limits concurrent tasks | एक साथ चलने वाले काम की सीमा |
| Backpressure | Make callers wait when overloaded | भार ज़्यादा हो तो इंतज़ार कराना |
| 429 | Too many requests | बहुत ज़्यादा requests |
| 504 | Upstream timed out | Upstream समय पर नहीं आया |

---

## ⚡ 3-Line Summary
English: Serve AI with async endpoints, Pydantic validation, SSE streaming, timeouts, semaphores and rate limits. Load heavy clients once in lifespan and never block the event loop. Move long jobs to a queue.
Hindi: AI को async endpoints, Pydantic validation, SSE streaming, timeout, semaphore और rate limit के साथ serve करें। भारी clients lifespan में एक बार load करें और event loop को कभी block न करें। लंबे jobs queue में भेजें।

---

## ➡️ Next Topic
**401. Python Performance Issues** — find and fix the common slowdowns in Python code.
