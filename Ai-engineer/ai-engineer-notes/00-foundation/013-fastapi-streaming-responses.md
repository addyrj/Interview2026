---

# 013. FastAPI Streaming Responses
# हिंदी में: FastAPI Streaming Responses

---

## 🔵 Simple Definition (English)
Streaming sends the response in pieces while it is still being produced, instead of waiting for the full answer. For LLMs this means the user sees words appear one by one (like ChatGPT). In FastAPI you return a `StreamingResponse` wrapping a generator, commonly using Server-Sent Events (SSE).

## 🔵 सरल परिभाषा (Hindi)
Streaming में response पूरा बनने का इंतज़ार किए बिना टुकड़ों में भेजा जाता है। LLM के लिए इसका मतलब है कि user को शब्द एक-एक करके दिखते हैं (ChatGPT की तरह)। FastAPI में generator को `StreamingResponse` में लपेटकर return करते हैं, अक्सर Server-Sent Events (SSE) के रूप में।

---

## 🔴 Problem it Solves
An LLM may take 8-20 seconds to finish a long answer. Waiting for all of it feels broken and risks gateway timeouts. Streaming gives the first token in about 300-800 ms (time to first token), so the app feels instant, and the user can stop early.

## 🔴 यह क्यों बना? (Hindi)
एक लंबा LLM answer पूरा होने में 8-20 second लग सकते हैं। पूरा इंतज़ार करना टूटा हुआ लगता है और gateway timeout का ख़तरा होता है। Streaming से पहला token लगभग 300-800 ms में मिल जाता है (time to first token), app तुरंत चलता लगता है, और user बीच में रोक भी सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client opens a request (fetch with a stream reader, or EventSource for GET)
Step 2 → Route calls the LLM with stream=True; the provider sends chunks as they are generated
Step 3 → Route is an async generator: `async for chunk in llm_stream: yield format(chunk)`
Step 4 → FastAPI wraps it: StreamingResponse(gen(), media_type="text/event-stream")
Step 5 → Headers (status 200) go out immediately; each yield is flushed to the client
Step 6 → SSE format per message: "data: <text>\n\n"; end with a "[DONE]" marker
Step 7 → On client disconnect, generator is cancelled; close the upstream stream to stop paying
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Client request खोलता है (stream reader वाला fetch, या GET के लिए EventSource)
Step 2 → Route LLM को stream=True से call करता है; provider chunks बनते ही भेजता है
Step 3 → Route एक async generator है: `async for chunk in llm_stream: yield format(chunk)`
Step 4 → FastAPI उसे लपेटता है: StreamingResponse(gen(), media_type="text/event-stream")
Step 5 → Headers (status 200) तुरंत निकलते हैं; हर yield client को flush होता है
Step 6 → हर SSE message का format: "data: <text>\n\n"; अंत में "[DONE]" marker
Step 7 → Client disconnect पर generator cancel होता है; upstream stream बंद करो ताकि पैसा न लगे
```

---

## 🟡 Real World Example
**Tariff Classification System**: An officer asks "Explain why a rugged tablet falls under 8471 and not 8517". The explanation is long, so the UI streams it token by token. A final SSE event carries the structured result (HS code, confidence) and token usage so the UI can show cost.

**Zomato AI**: The chat assistant streams the answer ("Here are 3 spicy veg places near you...") so the diner reads while the rest is generated.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "Rugged tablet 8471 में क्यों आता है, 8517 में क्यों नहीं"। Explanation लंबा है, इसलिए UI उसे token-दर-token stream करता है। आख़िरी SSE event में structured result (HS code, confidence) और token usage आता है ताकि UI cost दिखा सके।

**Zomato AI**: Chat assistant जवाब stream करता है ("आपके पास 3 तीखे veg places...") ताकि बाकी बनते समय diner पढ़ता रहे।

---

## 💻 Code Example — Basic
```python
# Basic streaming - needs fastapi + httpx
import asyncio  # async sleep
from collections.abc import AsyncIterator  # type

from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # tests

app = FastAPI()  # app


async def fake_llm_stream(prompt: str) -> AsyncIterator[str]:  # pretends to stream tokens
    for token in ["Smart", "phones", " fall", " under", " 8517."]:  # tokens
        await asyncio.sleep(0.05)  # generation delay
        yield token  # one token at a time


async def sse(prompt: str) -> AsyncIterator[str]:  # wrap tokens in SSE format
    async for token in fake_llm_stream(prompt):  # iterate tokens
        yield f"data: {token}\n\n"  # SSE message ends with blank line
    yield "data: [DONE]\n\n"  # end marker


@app.get("/stream")  # route
async def stream(q: str) -> StreamingResponse:  # returns a streaming response
    return StreamingResponse(sse(q), media_type="text/event-stream")  # starts sending immediately


client = TestClient(app)  # client
with client.stream("GET", "/stream?q=phone") as r:  # read stream incrementally
    for line in r.iter_lines():  # each line as it arrives
        if line:  # skip blank separators
            print(line)  # data: Smart ... data: [DONE]
```

## 💻 Code Example — Advanced
```python
# Production SSE: JSON events, usage event at the end, error event, disconnect handling, headers
import asyncio  # async tools
import json  # event payloads
from collections.abc import AsyncIterator  # type

from fastapi import FastAPI, HTTPException, Request  # tools
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel, Field  # models


class ChatIn(BaseModel):  # input
    question: str = Field(min_length=3, max_length=1000)  # bounded input = bounded tokens


class FakeUpstream:  # mimics an LLM stream with usage at the end
    closed = False  # tracks cleanup

    async def __aiter__(self) -> AsyncIterator[str]:  # async iteration
        for tok in ["Rugged ", "tablets ", "are ", "computers."]:  # tokens
            await asyncio.sleep(0.02)  # delay
            if tok.startswith("FAIL"):  # failure simulation hook
                raise ConnectionError("upstream reset")  # error mid-stream
            yield tok  # token

    async def aclose(self) -> None:  # release the connection
        self.closed = True  # mark


def event(name: str, data: dict) -> str:  # build one SSE event
    return f"event: {name}\ndata: {json.dumps(data)}\n\n"  # named event with JSON payload


async def generate(request: Request, body: ChatIn) -> AsyncIterator[str]:  # the streaming generator
    upstream = FakeUpstream()  # open the LLM stream
    tokens = 0  # count output chunks (approximate tokens)
    try:  # protect streaming
        async for tok in upstream:  # read tokens
            if await request.is_disconnected():  # client left?
                break  # stop, do not keep paying for tokens
            tokens += 1  # count
            yield event("token", {"text": tok})  # send token event
        yield event("done", {"output_tokens": tokens, "hs_code": "8471"})  # final structured event
    except ConnectionError as exc:  # failure after streaming started (status is already 200)
        yield event("error", {"message": "upstream failed", "detail": str(exc)[:50]})  # tell client in-band
    finally:  # always executes, even on cancel
        await upstream.aclose()  # close upstream stream


app = FastAPI()  # app


@app.post("/chat/stream")  # route
async def chat_stream(request: Request, body: ChatIn) -> StreamingResponse:  # POST streaming
    if "blocked" in body.question:  # pre-flight validation (can still return a real 4xx)
        raise HTTPException(status_code=400, detail="blocked by policy")  # before streaming starts
    return StreamingResponse(
        generate(request, body),  # generator
        media_type="text/event-stream",  # SSE
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # stop proxies from buffering (nginx)
    )  # response


if __name__ == "__main__":  # demo
    c = TestClient(app)  # client
    with c.stream("POST", "/chat/stream", json={"question": "why 8471?"}) as r:  # stream request
        print(r.status_code, r.headers["content-type"])  # 200 text/event-stream; charset=utf-8
        print(r.read().decode())  # all events
    print(c.post("/chat/stream", json={"question": "blocked content"}).status_code)  # 400 before streaming
```

---

## 🟠 FastAPI Integration
FastAPI offers `StreamingResponse` (any sync or async generator). For SSE you can also use the `sse-starlette` package. With the OpenAI SDK, use `AsyncOpenAI` with `stream=True` and `stream_options={"include_usage": True}`, so the last chunk carries `usage`.

```python
# Real OpenAI streaming through FastAPI (needs OPENAI_API_KEY)
from collections.abc import AsyncIterator  # type
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming
from openai import AsyncOpenAI  # async client

app = FastAPI()  # app
client = AsyncOpenAI()  # one shared client


async def tokens(question: str) -> AsyncIterator[str]:  # generator
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",  # cheap model
        messages=[{"role": "user", "content": question}],  # prompt
        stream=True,  # ask for streaming
        stream_options={"include_usage": True},  # final chunk includes token usage
        max_tokens=400,  # cap output cost
    )  # returns an async iterator of chunks
    async for chunk in stream:  # iterate chunks
        if chunk.choices and chunk.choices[0].delta.content:  # a text piece
            yield f"data: {chunk.choices[0].delta.content}\n\n"  # forward it
        if chunk.usage:  # last chunk
            yield f"event: usage\ndata: {chunk.usage.total_tokens}\n\n"  # send usage


@app.get("/ask")  # route
async def ask(q: str) -> StreamingResponse:  # handler
    return StreamingResponse(tokens(q), media_type="text/event-stream")  # stream
```

---

## 🔗 LangChain / LangGraph Connection
`chain.astream(input)` yields message chunks; `astream_events` (version="v2") yields fine-grained events (tokens, tool calls, node start/end). LangGraph's `graph.astream(state, stream_mode="messages")` streams tokens from inside nodes, and `stream_mode="updates"` streams each node's state change.

```python
# LangChain streaming into SSE (needs API key)
from collections.abc import AsyncIterator  # type
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

app = FastAPI()  # app
chain = ChatPromptTemplate.from_template("Explain HS code for {item}") | ChatOpenAI(model="gpt-4o-mini")  # chain


async def gen(item: str) -> AsyncIterator[str]:  # generator
    async for chunk in chain.astream({"item": item}):  # each chunk is an AIMessageChunk
        yield f"data: {chunk.content}\n\n"  # forward text
    yield "data: [DONE]\n\n"  # end


@app.get("/explain")  # route
async def explain(item: str) -> StreamingResponse:  # handler
    return StreamingResponse(gen(item), media_type="text/event-stream")  # stream
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a blocking generator or sync SDK
✅ Correct: async generator with async client.

```python
# Wrong: sync stream inside async route blocks the loop between chunks
def gen():
    for chunk in sync_client.chat.completions.create(..., stream=True):
        yield chunk
# Right
async def gen():
    stream = await async_client.chat.completions.create(..., stream=True)
    async for chunk in stream:
        yield chunk
```

❌ Mistake 2: Proxy buffering (nginx, some CDNs) holds the stream until the end
✅ Correct: send `X-Accel-Buffering: no`, `Cache-Control: no-cache` and configure the proxy.

```python
# Wrong: default headers, user still sees everything at once in production
StreamingResponse(gen(), media_type="text/event-stream")
# Right
StreamingResponse(gen(), media_type="text/event-stream",
                  headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

❌ Mistake 3: Ignoring client disconnects, so the server keeps generating (and billing) tokens nobody reads. Check `request.is_disconnected()` and close the upstream in `finally`.

---

## 🧠 Tricky Interview Question

**Q**: "Streaming works on localhost but in production the answer appears all at once after 10 seconds. Nothing is wrong in the code. Why?"

**Answer**: Something between the app and the browser is buffering: nginx (`proxy_buffering on`), a CDN, a load balancer, or gzip compression middleware that waits to compress. Fix: disable buffering for that route (`X-Accel-Buffering: no` or `proxy_buffering off`), turn off compression for `text/event-stream`, make sure HTTP/1.1 keep-alive or HTTP/2 is used, and send periodic heartbeat comments (`: ping\n\n`) so idle connections are not closed by timeouts.

---

## ⚫ Interview Questions + Answers

Q1: Why stream LLM responses? (Easy)
A1: It reduces perceived latency (first token in under a second), avoids timeouts on long answers and lets users cancel early.

Q2: What is SSE? (Easy)
A2: Server-Sent Events: a one-way text stream over HTTP with media type `text/event-stream`, where each message is `data: ...` followed by a blank line. Browsers have `EventSource`, which only supports GET; for POST use `fetch` with a stream reader.

Q3: SSE vs WebSocket? (Medium)
A3: SSE is one-directional (server to client), simple, works over normal HTTP and auto-reconnects. WebSocket is bidirectional and needs a different protocol and infrastructure. For chat answers SSE is usually enough; use WebSocket for interactive voice or collaborative features.

Q4: How do you get token usage when streaming? (Medium)
A4: With OpenAI set `stream_options={"include_usage": True}`; the final chunk contains `usage`. Otherwise count output tokens yourself using tiktoken on the accumulated text. Anthropic's stream returns usage in `message_start` and `message_delta` events. LangChain exposes `usage_metadata` on the final chunk for supported providers.

Q5: How do you handle errors, retries and cancellation in a streaming endpoint? (Hard)
A5: Validate everything (auth, size, budget) before the stream starts so errors can still be 4xx. After start, catch exceptions in the generator and emit an `error` event, then close. Do not auto-retry mid-stream (it would duplicate text); if you retry, only before the first token. Detect disconnects (`request.is_disconnected()` or `asyncio.CancelledError`) and close the provider stream in `finally` to stop billing. Support resume by event ids (`Last-Event-ID`) only if you persist partial output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat or long-form generation for people
- Showing progress of agent steps
- Answers longer than a few seconds

❌ Avoid when:
- Machine-to-machine calls that need the full JSON (parse after complete)
- Structured output must be validated as a whole before use
- Infrastructure cannot pass streams (buffering proxies you cannot configure)

---

## 📊 Visual Diagram
```
 Browser            FastAPI                    LLM provider
   │ POST /chat/stream │                            │
   │──────────────────►│ create(stream=True) ──────►│
   │                   │◄──── chunk "Rugged " ──────│
   │◄─ data: Rugged ───│                            │
   │                   │◄──── chunk "tablets " ─────│
   │◄─ data: tablets ──│                            │
   │       ...         │◄──── usage chunk ──────────│
   │◄─ event: done ────│                            │
   │ (disconnect) ✕    │── aclose() upstream ──────►│  (stop billing)
```

---

## 💰 Cost Impact
Streaming itself costs the same tokens as non-streaming, but it affects spend in two ways. Good: users can stop early, and you can abort the upstream on disconnect, saving the remaining output tokens (output tokens usually cost 3-5x input). Bad: forgetting to close upstream streams keeps billing for unread output. Always set `max_tokens`. Example: with 100K streams a day, 10 percent aborted halfway at 400 average output tokens saves 100K x 0.1 x 200 = 2M output tokens, about $1.2/day on gpt-4o-mini ($0.60 per 1M output).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Send data in pieces | टुकड़ों में भेजना |
| SSE | Server-Sent Events text stream | server से text stream |
| TTFT | Time to first token | पहले token तक समय |
| StreamingResponse | FastAPI streaming response class | streaming response class |
| Async generator | `async def` with `yield` | `yield` वाला async function |
| Buffering | Holding data before sending | भेजने से पहले रोकना |
| Heartbeat | Periodic ping to keep alive | connection ज़िंदा रखने का ping |
| Backpressure | Slow consumer slows producer | धीमा consumer producer को धीमा करे |

---

## ⚡ 3-Line Summary
English: Streaming sends LLM tokens to the client as they are generated, giving a fast first token. Use an async generator with `StreamingResponse` and SSE, validate before streaming, and send errors as events. Stop upstream calls on disconnect to avoid paying for unread tokens.
Hindi: Streaming में LLM tokens बनते ही client को भेजे जाते हैं, इसलिए पहला token जल्दी मिलता है। Async generator के साथ `StreamingResponse` और SSE use करो, streaming से पहले validate करो, और errors को events के रूप में भेजो। Disconnect पर upstream बंद करो ताकि unread tokens का पैसा न लगे।

---

## ➡️ Next Topic
**014. FastAPI + PostgreSQL (asyncpg)** — after streaming answers, we persist requests, results and usage in a real database.
