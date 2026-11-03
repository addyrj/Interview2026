---

# 575. Build Streaming Chat API
# हिंदी में: Streaming Chat API बनाना

---

## 🔵 Simple Definition (English)
A streaming chat API sends the model's answer to the client piece by piece as it is generated, instead of waiting for the whole answer. The common transport is Server-Sent Events (SSE): a long-lived HTTP response with `text/event-stream` frames.

## 🔵 सरल परिभाषा (Hindi)
Streaming chat API model का जवाब बनते-बनते टुकड़ों में client को भेजती है, पूरे जवाब का इंतज़ार नहीं करती। आम transport Server-Sent Events (SSE) है: `text/event-stream` frames वाला लंबा HTTP response।

---

## 🔴 Problem it Solves
A 300-token answer can take 5-10 seconds. Waiting for all of it feels broken. Streaming shows the first word in well under a second (time to first token), improving perceived speed. It also lets you stop generation when the user leaves, saving tokens. Challenges: errors after headers are sent, timeouts, proxy buffering, disconnects.

## 🔴 यह क्यों बना? (Hindi)
300-token का जवाब 5-10 सेकंड ले सकता है; पूरा इंतज़ार करना खराब लगता है। Streaming पहला शब्द एक सेकंड से कम में दिखाती है (time to first token), जिससे app तेज़ लगता है। User चला जाए तो generation रोककर tokens भी बचते हैं। चुनौतियाँ: headers जाने के बाद errors, timeouts, proxy buffering, disconnects।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client POSTs the message and keeps the connection open
Step 2 → Server calls the LLM with stream=True
Step 3 → Provider yields small chunks (deltas) as tokens are produced
Step 4 → Server wraps each chunk as an SSE frame: "event: token\ndata: {...}\n\n"
Step 5 → Server checks client disconnect and timeouts between chunks
Step 6 → On normal end send "event: done"; on failure send "event: error" (status code already 200)
Step 7 → Close upstream stream; proxies must not buffer (X-Accel-Buffering: no)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client message POST करता है और connection खुला रखता है
Step 2 → Server LLM को stream=True से call करता है
Step 3 → Provider tokens बनते ही छोटे chunks (deltas) देता है
Step 4 → Server हर chunk को SSE frame में लपेटता है: "event: token\ndata: {...}\n\n"
Step 5 → Chunks के बीच client disconnect और timeouts check होते हैं
Step 6 → सामान्य अंत पर "event: done"; गलती पर "event: error" (status code पहले ही 200)
Step 7 → Upstream stream बंद करो; proxies buffer न करें
```

---

## 🟡 Real World Example
**Tariff Classification System**: An officer asks for a long explanation of HS 8517 duty rules. Words appear immediately, and if the officer closes the tab, the server detects the disconnect and stops the model call, so unused tokens are not generated.

**Zomato-style**: A "what should I eat" assistant types out suggestions live.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer HS 8517 के duty नियमों की लंबी व्याख्या माँगता है। शब्द तुरंत दिखने लगते हैं और tab बंद करने पर server disconnect पहचानकर model call रोक देता है, इसलिए बेकार tokens generate नहीं होते।

---

## 💻 Code Example — Basic
Full file: `main.py`. I ran `python main.py` (offline mock): it printed nine `event: token` frames (one per word) and a final `event: done | data: {"chunks": 9}`. The FastAPI route was not executed here (FastAPI not installed).

```python
# Minimal SSE generator (from main.py)
import json  # payload encoding

def sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"     # one SSE frame ends with a blank line

async def stream_words(text: str):
    for word in text.split():
        yield sse("token", {"text": word + " "})               # send each word as a frame
    yield sse("done", {})                                      # signal completion
```

## 💻 Code Example — Advanced
`sse_events` in `main.py` adds: manual iteration with `asyncio.wait_for` (first-token timeout 15 s, idle timeout 30 s), a client-disconnect check via `request.is_disconnected`, in-band `error` events for mid-stream failures, and closing the upstream generator in `finally`. `openai_stream` uses `AsyncOpenAI` with `stream=True` and yields `delta.content`.

```python
# Excerpt: disconnect + timeout handling (main.py)
if is_disconnected is not None and await is_disconnected():
    break                                    # stop paying for tokens when the client is gone
try:
    piece = await asyncio.wait_for(source.__anext__(), timeout=timeout)   # bounded wait for next chunk
except asyncio.TimeoutError:
    yield sse("error", {"detail": "model timeout"})                       # tell the client, then end
    break
```

---

## 🟠 FastAPI Integration
```python
@app.post("/chat/stream")
async def chat_stream(body: ChatIn, request: Request) -> StreamingResponse:
    return StreamingResponse(
        sse_events(body.message, request.is_disconnected),     # async generator
        media_type="text/event-stream",                        # SSE
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},   # disable Nginx buffering
    )
```
Test with `curl -N` (the `-N` flag disables curl buffering). Browser `EventSource` only supports GET, so for POST use `fetch` with a stream reader. Behind Nginx also set `proxy_buffering off` and a long `proxy_read_timeout`; behind an ALB raise the idle timeout above 60 s.

---

## 🔗 LangChain / LangGraph Connection
LangChain Runnables expose `astream` (text chunks) and `astream_events` (detailed events including tool calls). LangGraph supports `astream` with `stream_mode` options such as `"messages"` and `"updates"` (check current docs). Feed those async iterators into the same `sse_events` wrapper.

```python
# LangChain: stream a chain's output into SSE (illustrative)
# async for chunk in chain.astream({"question": q}):
#     yield sse("token", {"text": chunk})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raising HTTPException after streaming started
✅ Correct: Headers (200) are already sent, so send an in-band `error` event.
```python
# Wrong
async def gen():
    yield "partial"
    raise HTTPException(500)        # too late: client sees a broken stream
# Right
    yield sse("error", {"detail": "upstream failed"})
```

❌ Mistake 2: Ignoring client disconnects
✅ Correct: Check `is_disconnected` and close the upstream stream.
```python
# Wrong: keep generating 300 tokens for nobody (you still pay)
# Right: if await request.is_disconnected(): break   # then aclose() the provider stream
```

---

## 🧠 Tricky Interview Question
**Q**: "Streaming works locally but in production the answer arrives all at once after 10 seconds. Why?"

**Answer**: Something between client and app is buffering. Common causes: Nginx `proxy_buffering on` (disable it or send `X-Accel-Buffering: no`), gzip compression middleware buffering small chunks, a CDN or API gateway that buffers responses, or a sync generator blocking the event loop. Verify with `curl -N` against the app directly, then through each hop. Also ensure the generator is async and yields frequently.

---

## ⚫ Interview Questions + Answers

Q1: What is SSE?
A1: A one-way, text-based streaming protocol over HTTP; each event is lines like `data: ...` ending with a blank line.

Q2: SSE vs WebSocket?
A2: SSE is one-way server-to-client over plain HTTP with auto-reconnect; WebSocket is two-way and heavier. Chat token streaming usually needs only SSE.

Q3: What is time to first token (TTFT)?
A3: Delay until the first token arrives; the main driver of perceived responsiveness.

Q4: How do you handle errors mid-stream?
A4: Status is already 200, so emit an `error` event, close the stream, and let the client show a retry option; log server-side.

Q5: How do you count tokens and cost when streaming?
A5: With OpenAI, request usage in the final chunk (`stream_options={"include_usage": True}`, verify in current docs) or count with a tokenizer; accumulate the text server-side to log and bill; on disconnect, record partial usage.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs with long answers
- Perceived latency matters

❌ Avoid when:
- Machine-to-machine calls needing a complete JSON object (stream only if the consumer can handle partial data)
- Structured output that must be validated as a whole before display

---

## 📊 Visual Diagram
```
 Client ──POST──► FastAPI ──stream=True──► LLM provider
   ▲                 │  ◄── delta ── delta ── delta ──┘
   │   event: token │
   ◄────────────────┤  (check disconnect + timeouts between chunks)
   │   event: token │
   ◄────────────────┤
   │   event: done  │
   ◄────────────────┘      Nginx: proxy_buffering off
```

---

## 💰 Cost Impact
Streaming does not change per-token price; it changes wasted tokens and perceived latency. If 15% of users close the tab halfway and you stop generation on disconnect, you save roughly 7% of output tokens versus letting every call finish (illustrative arithmetic). Also set `max_tokens`, record usage per request, and make the system prompt cacheable where the provider supports prompt caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSE | Server-Sent Events stream | Server से events का stream |
| TTFT | Time to first token | पहले token तक का समय |
| Delta | Small piece of output | आउटपुट का छोटा टुकड़ा |
| Backpressure | Slow consumer limits producer | धीमा consumer producer को रोकता है |
| Buffering | Proxy holds data before sending | Proxy का data रोककर रखना |
| Disconnect | Client closes connection | Client का connection बंद करना |

---

## ⚡ 3-Line Summary
English: Stream tokens as SSE frames from an async generator wrapped in `StreamingResponse`. Add timeouts, disconnect checks and in-band error events, and disable proxy buffering. Streaming improves perceived speed and can save tokens when users leave.
Hindi: Async generator से tokens को SSE frames में `StreamingResponse` के ज़रिये stream करें। Timeouts, disconnect checks और in-band error events जोड़ें और proxy buffering बंद करें। Streaming से app तेज़ लगता है और user के जाने पर tokens बचते हैं।

---

## ➡️ Next Topic
**576. Build Structured Output API** — make the model return validated JSON instead of free text.
