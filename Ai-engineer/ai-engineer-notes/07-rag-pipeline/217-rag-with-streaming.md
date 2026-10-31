---

# 217. RAG with Streaming
# हिंदी में: RAG with Streaming

---

## 🔵 Simple Definition (English)
Streaming sends the LLM answer to the user piece by piece as it is generated, instead of waiting for the full text. In RAG, retrieval runs first (fast), then generation streams. The user sees the first words in under a second.

## 🔵 सरल परिभाषा (Hindi)
Streaming में LLM का answer पूरा बनने का इंतज़ार किए बिना टुकड़ों में user तक भेजा जाता है। RAG में पहले retrieval चलता है (तेज़), फिर generation stream होती है। User को पहले शब्द एक सेकंड से कम में दिखते हैं।

---

## 🔴 Problem it Solves
A RAG request has retrieval (~100-300 ms), reranking (~100-300 ms) and generation (2-10 s for a long answer). Waiting for everything feels slow. Streaming cuts "time to first token" and makes the app feel fast, even though total time is the same.

## 🔴 यह क्यों बना? (Hindi)
RAG request में retrieval (~100-300 ms), reranking (~100-300 ms) और generation (लंबे answer के लिए 2-10 s) लगते हैं। सब खत्म होने तक इंतज़ार धीमा लगता है। Streaming "पहले token तक का समय" घटाती है और total time वही रहने पर भी app तेज़ लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client opens POST /ask/stream (SSE: text/event-stream)
Step 2 → Server retrieves + reranks (non-streamed, must finish first)
Step 3 → Server sends an early event: {"type":"sources", ...}
Step 4 → Server calls the LLM with stream=True
Step 5 → For each chunk (delta) → yield "data: {...}\n\n" to the client
Step 6 → At the end send {"type":"done","usage":...}
Step 7 → Client appends deltas to the UI; handles disconnects and errors
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Client POST /ask/stream खोलता है (SSE: text/event-stream)
Step 2 → Server retrieve + rerank करता है (stream नहीं, पहले पूरा होना ज़रूरी)
Step 3 → Server पहले एक event भेजता है: {"type":"sources", ...}
Step 4 → Server LLM को stream=True से call करता है
Step 5 → हर chunk (delta) पर "data: {...}\n\n" client को yield करो
Step 6 → आख़िर में {"type":"done","usage":...} भेजो
Step 7 → Client UI में deltas जोड़ता है; disconnect व errors संभालता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: An officer asks about a complex product. Sources (3 tariff pages) appear instantly in the side panel, then the explanation types out. If the user sees a wrong source early they can cancel, saving tokens. **Zomato**: support bot answers start immediately. **Amazon**: "Ask about this product" streams the answer as reviews are summarised.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer complex product के बारे में पूछता है। Side panel में 3 tariff pages (sources) तुरंत दिखते हैं, फिर explanation टाइप होती है। शुरू में गलत source दिखे तो user cancel कर सकता है और tokens बचते हैं। **Zomato**: support bot का answer तुरंत शुरू। **Amazon**: "इस product के बारे में पूछें" reviews summarise करते हुए stream करता है।

---

## 💻 Code Example — Basic
```python
# Pure Python generator simulating token streaming (no API key). Shows the SSE format too.
import json  # encode events
import time  # simulate delay
from typing import Iterator  # type hints


def fake_llm_stream(prompt: str) -> Iterator[str]:
    """Yield words one by one like an LLM stream."""
    for word in "Smartphones fall under HS 8517.13 [S1].".split():  # canned answer
        time.sleep(0.01)  # tiny delay to mimic generation
        yield word + " "  # one delta


def sse(event: dict) -> str:
    """Format a dict as a Server-Sent Event line."""
    return f"data: {json.dumps(event)}\n\n"  # SSE requires blank line


def rag_stream(question: str) -> Iterator[str]:
    sources = [{"id": "S1", "title": "Customs Tariff 2024"}]  # pretend retrieval result
    yield sse({"type": "sources", "sources": sources})  # send sources first
    count = 0  # delta counter
    for delta in fake_llm_stream(question):  # stream generation
        count += 1  # count
        yield sse({"type": "delta", "text": delta})  # send piece
    yield sse({"type": "done", "deltas": count})  # finish


if __name__ == "__main__":
    for event in rag_stream("HS code for smartphone?"):  # consume stream
        print(event, end="")  # print raw SSE text
```

## 💻 Code Example — Advanced
```python
# Production: async OpenAI streaming with usage, error events and timeout. Yields SSE strings.
import asyncio  # timeout handling
import json  # encode
import logging  # logs
from typing import AsyncIterator  # typing

from openai import AsyncOpenAI  # openai>=1

logger = logging.getLogger("rag_stream")  # logger
client = AsyncOpenAI()  # env key


def sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"  # keep Hindi readable


async def stream_answer(question: str, chunks: list[str]) -> AsyncIterator[str]:
    """Stream: sources -> deltas -> done. Errors become an error event, not a crashed connection."""
    ctx = "\n".join(f"[S{i}] {c}" for i, c in enumerate(chunks, 1))  # labelled context
    yield sse({"type": "sources", "count": len(chunks)})  # early feedback
    try:  # streaming call
        stream = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=500, stream=True,  # stream on
            stream_options={"include_usage": True},  # last chunk carries usage
            messages=[
                {"role": "system", "content": "Answer only from the context. Cite [S#]."},
                {"role": "user", "content": f"<context>\n{ctx}\n</context>\nQuestion: {question}"},
            ],
        )
        usage = None  # filled at the end
        async for part in stream:  # each streamed chunk
            if part.usage:  # final usage chunk (choices empty)
                usage = {"prompt": part.usage.prompt_tokens, "completion": part.usage.completion_tokens}
            if part.choices and part.choices[0].delta.content:  # has text
                yield sse({"type": "delta", "text": part.choices[0].delta.content})  # forward
        yield sse({"type": "done", "usage": usage})  # finish event
    except asyncio.CancelledError:  # client disconnected
        logger.info("client disconnected, stream cancelled")  # log
        raise  # propagate so resources are freed
    except Exception as exc:  # API failure mid-stream
        logger.error("stream failed: %s", exc)  # log
        yield sse({"type": "error", "message": "generation failed"})  # tell the client
```

---

## 🟠 FastAPI Integration
Use `StreamingResponse` with `text/event-stream`. Disable proxy buffering (for Nginx, `X-Accel-Buffering: no`).

```python
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    question: str  # question


@app.post("/ask/stream")  # route
async def ask_stream(req: Req) -> StreamingResponse:
    chunks = ["Smartphones HS 8517.13 duty 20 percent."]  # from retrieval + rerank (done BEFORE streaming)
    return StreamingResponse(
        stream_answer(req.question, chunks),  # async generator
        media_type="text/event-stream",  # SSE
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # no buffering
    )
```

---

## 🔗 LangChain / LangGraph Connection
LCEL chains stream with `astream`. LangGraph can stream node updates or LLM tokens with `astream(..., stream_mode="messages")` (tokens) or `"updates"` (state per node).

```python
# chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
# async for token in chain.astream({"context": ctx, "question": q}):   # token strings
#     yield sse({"type": "delta", "text": token})
#
# LangGraph:
# async for msg, meta in graph.astream({"question": q}, stream_mode="messages"):
#     if meta["langgraph_node"] == "generate":   # only the answer node
#         yield sse({"type": "delta", "text": msg.content})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running blocking retrieval code inside the async generator
✅ Correct: Use async retrieval or `asyncio.to_thread`.

```python
# Wrong: blocks the event loop, all other users freeze
docs = sync_vector_search(q)

# Right
docs = await asyncio.to_thread(sync_vector_search, q)
```

❌ Mistake 2: Validating the answer only after streaming
✅ Correct: Streamed text cannot be taken back; validate inputs/sources before, and mark the final answer in the `done` event.

```python
# Wrong: stream, then discover the answer cited a fake source
# Right: ground via prompts + restrict ids; send final verification result in the done event
yield sse({"type": "done", "citations_valid": all(i in valid for i in used_ids)})
```

---

## 🧠 Tricky Interview Question
**Q**: "With streaming, how do you apply an output guardrail (for example block PII or unsafe text) when the first words are already on the user's screen?"

**Answer**: You cannot unsend tokens. Options: (1) buffer in small windows (sentence level), check each, then release; (2) run input guardrails and context filtering before generation; (3) use a fast streaming moderation check on rolling text and cut the stream with a "retracted" event the UI can handle; (4) for high-risk flows, do not stream, return after validation. Choose based on risk versus perceived latency.

---

## ⚫ Interview Questions + Answers

Q1: What is the main benefit of streaming?
A1: Lower time-to-first-token, so the app feels faster.

Q2: Which HTTP technique is common for LLM streaming?
A2: Server-Sent Events (SSE) using `text/event-stream`; WebSockets are an alternative.

Q3: Can retrieval be streamed?
A3: Not usually; retrieval and reranking must finish first. Only generation streams. You can send sources early to improve UX.

Q4: How do you get token usage when streaming with OpenAI?
A4: Set `stream_options={"include_usage": True}`; the final chunk includes usage.

Q5: What problems appear in production streaming and how do you solve them?
A5: Proxy buffering (set no-buffer headers), client disconnects (handle CancelledError and stop the LLM call), mid-stream errors (send an error event), timeouts (heartbeat comments), load balancer idle limits, and measuring TTFT separately from total latency. Also add retry on the client with last-event-id when needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs with long answers
- Time-to-first-token matters
- Users may cancel early

❌ Avoid when:
- Backend-to-backend JSON calls
- Output must be validated fully before display
- Short answers (little gain)

---

## 📊 Visual Diagram
```
 t=0ms    request ───────────────►
 t=250ms  retrieve+rerank done
 t=260ms  ◄── event: sources
 t=600ms  ◄── delta "Smartphones "
 t=650ms  ◄── delta "fall under "
 t=700ms  ◄── delta "HS 8517.13 [S1]"
 t=2400ms ◄── event: done {usage}

 Without streaming: nothing until t=2400ms
```

---

## 💰 Cost Impact
- Streaming does not change token cost; same input and output tokens.
- It can save money: if users cancel early, you can abort and stop paying for further output tokens.
- Include usage with `include_usage` for accurate billing logs.
- Optimise: `max_tokens` cap, abort the upstream call on client disconnect, keep answers concise.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Send output in pieces | टुकड़ों में output भेजना |
| SSE | One-way server push over HTTP | Server से client को लगातार data |
| TTFT | Time to first token | पहले token तक का समय |
| Delta | A small piece of text | text का छोटा टुकड़ा |
| Backpressure | Slow client holds data back | धीमे client का दबाव |

---

## ⚡ 3-Line Summary
English: In RAG, retrieve first, then stream the generation to cut time to first token. Use SSE with sources first, deltas next, and a done event with usage. Handle disconnects and mid-stream errors.
Hindi: RAG में पहले retrieve करो, फिर generation stream करो ताकि पहला token जल्दी दिखे। SSE में पहले sources, फिर deltas और आख़िर में usage वाला done event भेजो। Disconnect और mid-stream errors संभालो।

---

## ➡️ Next Topic
**218. RAG with FastAPI** — putting the whole RAG pipeline behind a production-ready API.
