
---

# 456. Streaming + Caching
# हिंदी में: Streaming + Caching

---

## 🔵 Simple Definition (English)
Streaming sends the answer to the user token by token as the LLM generates it. Caching stores finished answers. Combining them means: on a **miss**, stream to the user while collecting chunks, then save the full text to cache when the stream ends; on a **hit**, replay the cached text as a stream so the client behaves the same way.

## 🔵 सरल परिभाषा (Hindi)
Streaming में LLM के generate करते ही answer token-by-token user को जाता है। Caching पूरे answers store करती है। दोनों मिलाने का मतलब: **miss** पर user को stream करते हुए chunks इकट्ठा करो और stream ख़त्म होने पर पूरा text cache में रखो; **hit** पर cached text को stream की तरह replay करो ताकि client का behaviour एक जैसा रहे।

---

## 🔴 Problem it Solves
A normal cache stores a complete response, but streaming has no complete response until the end. Naive code either skips caching for streamed calls (wasting money) or caches partial text when the user disconnects (serving truncated answers later). Also, a cache hit returned as one big JSON breaks front-ends that expect Server-Sent Events.

## 🔴 यह क्यों बना? (Hindi)
Normal cache पूरा response store करता है, पर streaming में अंत तक पूरा response नहीं होता। Naive code या तो streamed calls को cache ही नहीं करता (पैसा बर्बाद) या user के disconnect होने पर अधूरा text cache कर देता है (बाद में कटे हुए answers)। साथ ही hit पर एक बड़ा JSON लौटाने से SSE expect करने वाला front-end टूट जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives with stream=true
Step 2 → Look up the cache with the normalised key
Step 3 → HIT: replay stored text in small chunks (optional tiny delay) as SSE
Step 4 → MISS: open LLM stream, forward every chunk to the user immediately
Step 5 → Meanwhile append each chunk to a buffer
Step 6 → Stream finished normally (finish_reason == "stop") → write buffer to cache
Step 7 → Stream cancelled / errored / "length" cutoff → do NOT cache
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → stream=true के साथ request आती है
Step 2 → Normalised key से cache देखो
Step 3 → HIT: stored text को छोटे chunks में SSE की तरह replay करो
Step 4 → MISS: LLM stream खोलो, हर chunk तुरंत user को भेजो
Step 5 → साथ-साथ chunks को buffer में जोड़ते जाओ
Step 6 → Stream सही से ख़त्म हो (finish_reason == "stop") तो buffer cache में लिखो
Step 7 → Cancel / error / "length" cutoff हो तो cache मत करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The chat UI shows the explanation word by word. The first user's question streams from the LLM (3 seconds) and is cached at the end. The next ten importers asking the same thing get the answer replayed in ~100 ms, still animated like a stream. **Zomato-style**: a support bot's "refund policy" answer is replayed from cache, so no tokens are spent.

## 🟡 Real Example Hindi mein
**Tariff System**: Chat UI में explanation शब्द-दर-शब्द दिखती है। पहले user का question LLM से stream होता है (3 sec) और अंत में cache हो जाता है। अगले दस importers को वही answer ~100 ms में replay मिलता है, फिर भी stream जैसा animate होकर। **Zomato-style**: "refund policy" का answer cache से replay होता है, tokens खर्च नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: stream a fake LLM and cache the full text at the end (pure Python)
from typing import Iterator                                # type for generators

cache: dict[str, str] = {}                                 # key -> full answer

def fake_llm_stream(q: str) -> Iterator[str]:
    for word in f"HS code for {q} is 8517.13".split():      # pretend tokens
        yield word + " "                                   # emit one chunk at a time

def stream_with_cache(q: str) -> Iterator[str]:
    if q in cache:                                         # HIT path
        for word in cache[q].split():                      # replay stored text
            yield word + " "
        return                                             # stop here
    buffer: list[str] = []                                 # collect chunks
    for chunk in fake_llm_stream(q):                       # MISS path
        buffer.append(chunk)                               # remember chunk
        yield chunk                                        # forward immediately
    cache[q] = "".join(buffer).strip()                     # save only after a complete stream

print("".join(stream_with_cache("iphone")))                # first call: miss
print("".join(stream_with_cache("iphone")))                # second call: hit
```

## 💻 Code Example — Advanced
```python
# Production: async streaming cache with safe write-back and error handling
import asyncio                                             # sleep for replay pacing
from typing import AsyncIterator, Optional                 # async generator types
from openai import AsyncOpenAI                             # OpenAI async client

client = AsyncOpenAI()                                     # shared client

async def replay(text: str, chunk_chars: int = 24) -> AsyncIterator[str]:
    for i in range(0, len(text), chunk_chars):             # slice the cached text
        yield text[i : i + chunk_chars]                    # emit a small chunk
        await asyncio.sleep(0.005)                         # tiny pause so UI animates

async def stream_cached(
    key: str,
    prompt: str,
    cache_get,                                             # async (key) -> Optional[str]
    cache_set,                                             # async (key, text) -> None
) -> AsyncIterator[str]:
    try:
        cached: Optional[str] = await cache_get(key)       # try cache first
    except Exception:
        cached = None                                      # cache down = miss
    if cached is not None:
        async for piece in replay(cached):                 # HIT: replay
            yield piece
        return
    buffer: list[str] = []                                 # collects the full answer
    finished_ok = False                                    # only cache clean endings
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True,                                   # ask for streaming
            max_tokens=400,
        )
        async for event in stream:                         # each event has a delta
            if not event.choices:                          # usage-only chunks have no choices
                continue
            choice = event.choices[0]
            if choice.delta.content:                       # some deltas are empty
                buffer.append(choice.delta.content)        # remember
                yield choice.delta.content                 # forward immediately
            if choice.finish_reason == "stop":             # natural end
                finished_ok = True
    except asyncio.CancelledError:                         # client disconnected
        raise                                              # do not cache partial text
    except Exception:
        yield "\n[error: please retry]"                    # tell the user, do not cache
        return
    if finished_ok:                                        # only complete answers
        try:
            await cache_set(key, "".join(buffer))          # write-back
        except Exception:
            pass                                           # ignore cache write errors
```

---

## 🟠 FastAPI Integration
Return a `StreamingResponse` with `text/event-stream`. Both hit and miss use the same generator.

```python
from fastapi import FastAPI                                # framework
from fastapi.responses import StreamingResponse            # streaming helper
from pydantic import BaseModel                             # schema

app = FastAPI()
mem: dict[str, str] = {}                                   # demo cache; use Redis in production

async def get_(k: str) -> Optional[str]:
    return mem.get(k)                                      # lookup

async def set_(k: str, v: str) -> None:
    mem[k] = v                                             # store

class Q(BaseModel):
    question: str                                          # user text

@app.post("/stream")
async def stream_answer(body: Q) -> StreamingResponse:
    key = body.question.lower().strip()                    # simple normalised key
    async def sse() -> AsyncIterator[str]:
        async for piece in stream_cached(key, body.question, get_, set_):
            yield f"data: {piece}\n\n"                     # SSE framing
        yield "data: [DONE]\n\n"                           # end marker
    return StreamingResponse(sse(), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's LLM cache works with `invoke` but streaming bypasses it on many chat models (check your version). A reliable pattern is your own cache layer around `astream`, or LangGraph's `astream_events`, collecting chunks and writing at the end.

```python
from langchain_openai import ChatOpenAI                    # chat model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)       # deterministic for caching

async def cached_astream(key: str, question: str):
    if (hit := await get_(key)) is not None:               # check cache
        yield hit                                          # replay (could chunk it)
        return
    parts: list[str] = []                                  # collect chunks
    async for chunk in llm.astream(question):              # stream from LangChain
        parts.append(str(chunk.content))                   # chunk.content is text
        yield str(chunk.content)                           # forward
    await set_(key, "".join(parts))                        # cache once complete
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching partial text after disconnect
```python
# Wrong — write-back in a finally block caches truncated answers:
try:
    async for c in stream: yield c
finally:
    await cache_set(key, "".join(buf))

# Correct — write only when finish_reason == "stop" (see advanced example)
```

❌ Mistake 2: Returning a hit as one JSON blob to a streaming client
```python
# Wrong — front-end waits for SSE events, gets JSON, breaks
return {"answer": cached}

# Correct — replay cached text as SSE chunks with the same format
```

❌ Mistake 3: Blocking the stream while writing cache
```python
# Wrong — await slow cache write before sending the last chunk
# Correct — send all chunks first, write after (or use asyncio.create_task)
```

---

## 🧠 Tricky Interview Question
**Q**: "Two users send the same new question at the same moment. Both miss and both call the LLM. How do you avoid paying twice, even with streaming?"

**Answer**: Use **request coalescing** (single-flight). The first request takes a lock (e.g. Redis `SET key NX` with a short expiry) and streams from the LLM, publishing chunks to a channel (Redis Streams / pub-sub) as well. The second request sees the lock and subscribes to the same chunk stream instead of calling the LLM. When the first finishes it writes the cache and releases the lock. Handle failures: lock expiry so a crashed leader does not block followers forever.

---

## ⚫ Interview Questions + Answers

Q1: Why not cache each token chunk?
A1: Chunks are meaningless alone and would cost many writes. Cache the final joined text under one key.

Q2: How do you make a cache hit "feel" like streaming?
A2: Replay the stored text in small chunks over SSE, optionally with a tiny delay, using the same event format as live streaming.

Q3: When should you skip writing to cache after a stream?
A3: If it was cancelled, errored, hit `max_tokens` (`finish_reason == "length"`), or was blocked by a content filter.

Q4: How do you get token usage with streaming?
A4: With OpenAI use `stream_options={"include_usage": True}`; the final chunk carries usage. Store it with the cache entry for cost reports.

Q5: (Hard) How would you run output guardrails with streaming + caching?
A5: Options: (a) buffer and validate in sentence-sized windows before forwarding, (b) stream optimistically but validate the full text before caching, so unsafe text is never served from cache, and (c) mark entries with a guardrail version. Never cache unvalidated output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UX needs low time-to-first-token and repeated questions are common
- Answers are long (replay saves many output tokens)

❌ Avoid when:
- Responses are unique/personalised each time
- Answers need per-request moderation that you cannot do before caching

---

## 📊 Visual Diagram
```
                 ┌── HIT ──► replay chunks ──► client (SSE)
 request ─► cache┤
                 └── MISS ─► LLM stream ──┬─► client (SSE)
                                          └─► buffer
                                               │ finish_reason == "stop"
                                               ▼
                                          cache.set(key, full_text)
```

---

## 💰 Cost Impact
- Streaming itself costs the same tokens as non-streaming; caching removes the cost on hits (no input or output tokens).
- Long answers benefit most: 300 output tokens avoided per hit. Output tokens are usually priced several times higher than input tokens (illustrative: 4x).
- Optimise: set `max_tokens`, request coalescing to avoid duplicate in-flight calls, and cache only complete, validated answers.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Send tokens as generated | token-by-token भेजना |
| SSE | Server-Sent Events over HTTP | server से event stream |
| Write-back | Save to cache after producing | बाद में cache में लिखना |
| finish_reason | Why generation ended | generation रुकने का कारण |
| Replay | Re-send cached text as stream | cached text को stream जैसा भेजना |
| Request coalescing | Share one in-flight call | एक call सबके लिए |

---

## ⚡ 3-Line Summary
English: On a miss, stream and buffer, then cache only complete, clean answers. On a hit, replay the text as a stream so clients behave the same. Use coalescing to avoid duplicate concurrent calls.
Hindi: Miss पर stream करो और buffer करो, फिर सिर्फ़ पूरे और सही answers cache करो। Hit पर text को stream की तरह replay करो ताकि client वैसे ही चले। एक साथ आई duplicate calls से बचने के लिए coalescing use करो।

---

## ➡️ Next Topic
**457. Multi-tenant Caching** — keeping each customer's cached answers isolated and safe.
