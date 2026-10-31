---

# 029. OpenAI API — Streaming
# हिंदी में: OpenAI API — Streaming

---

## 🔵 Simple Definition (English)
Streaming means the API sends the answer in small pieces (chunks) as the model generates it, instead of waiting for the full answer. You pass `stream=True` and loop over the chunks. The user sees the first words in under a second, which feels much faster.

## 🔵 सरल परिभाषा (Hindi)
Streaming में API पूरा जवाब बनने का इंतज़ार किए बिना, model के generate करते ही छोटे-छोटे टुकड़े (chunks) भेजती है। आप `stream=True` देते हैं और chunks पर loop चलाते हैं। User को पहले शब्द एक सेकंड से भी कम में दिखते हैं, जिससे app बहुत तेज़ लगता है।

---

## 🔴 Problem it Solves
A 500-token answer can take 8-10 seconds. With normal calls the user stares at a spinner for the whole time. Streaming improves **time to first token** (TTFT), not total generation time, and it lets users stop early or start reading right away.

## 🔴 यह क्यों बना? (Hindi)
500 tokens का जवाब 8-10 seconds ले सकता है। Normal call में user पूरे समय spinner देखता है। Streaming **time to first token** (TTFT) सुधारती है, कुल generation time नहीं, और user जल्दी पढ़ना शुरू कर सकता है या बीच में रोक सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call create(..., stream=True)
Step 2 → Server opens an HTTP connection using Server-Sent Events (SSE)
Step 3 → Each generated token (or few tokens) is sent as a chunk
Step 4 → chunk.choices[0].delta.content holds the new text (can be None)
Step 5 → Your code prints/forwards it and builds the full text
Step 6 → Last chunk has finish_reason ("stop" or "length")
Step 7 → With stream_options={"include_usage": True} a final chunk carries usage
Step 8 → Connection closes; you store the full text and token counts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → create(..., stream=True) call करो
Step 2 → Server Server-Sent Events (SSE) से HTTP connection खुला रखता है
Step 3 → हर generated token (या कुछ tokens) chunk में आता है
Step 4 → chunk.choices[0].delta.content में नया text होता है (None हो सकता है)
Step 5 → आपका code उसे print/forward करता है और पूरा text जोड़ता जाता है
Step 6 → आख़िरी chunk में finish_reason होता है ("stop" या "length")
Step 7 → stream_options={"include_usage": True} से आख़िरी chunk में usage आता है
Step 8 → Connection बंद; आप पूरा text और token counts save करते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: The officer asks for the reasoning behind an HS code. The explanation is 300 tokens. With streaming, the first sentence appears in about 0.5 s, so the officer starts reading while the rest arrives. The backend still saves the complete text and token usage for audit.

**Zomato AI**: The chat assistant types out the recommendation like a person, which feels responsive even on slow mobile networks.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Officer HS code का reasoning माँगता है। Explanation 300 tokens की है। Streaming से पहला वाक्य लगभग 0.5 s में दिखता है, officer पढ़ना शुरू कर देता है और बाकी साथ-साथ आता रहता है। Backend audit के लिए पूरा text और token usage save करता है।

**Zomato AI**: Chat assistant recommendation इंसान की तरह type करता दिखता है, जिससे slow mobile network पर भी app responsive लगता है।

---

## 💻 Code Example — Basic
```python
# Basic streaming (needs OPENAI_API_KEY)
from openai import OpenAI                        # sync client

client = OpenAI()                                # reads key from env

stream = client.chat.completions.create(
    model="gpt-4o-mini",                         # model
    messages=[{"role": "user", "content": "Explain HS codes in 3 short lines."}],
    stream=True,                                 # ask for chunks
    stream_options={"include_usage": True},      # get token usage in the last chunk
)

parts: list[str] = []                            # collect text pieces
usage = None                                     # will hold token usage

for chunk in stream:                             # each chunk arrives as generated
    if chunk.usage is not None:                  # final usage-only chunk (choices is empty)
        usage = chunk.usage                      # save usage
    if not chunk.choices:                        # skip chunks without choices
        continue
    delta = chunk.choices[0].delta.content       # new text, may be None
    if delta:                                    # only handle real text
        print(delta, end="", flush=True)         # show immediately
        parts.append(delta)                      # keep for later

print()                                          # newline at the end
full_text = "".join(parts)                       # complete answer
print("chars:", len(full_text), "| usage:", usage)
```

## 💻 Code Example — Advanced
```python
# Production async streaming helper: timeout, partial-result safety, usage capture
import asyncio                                           # async tools
import logging                                           # logs
from dataclasses import dataclass, field                 # result container
from typing import AsyncIterator, Optional               # type hints

from openai import APIConnectionError, APIStatusError, AsyncOpenAI   # client + errors

logger = logging.getLogger(__name__)                     # logger
client = AsyncOpenAI(timeout=60.0, max_retries=2)        # shared client


@dataclass
class StreamResult:
    text: str = ""                                       # accumulated text
    prompt_tokens: Optional[int] = None                  # filled at the end
    completion_tokens: Optional[int] = None              # filled at the end
    finished: bool = False                               # True if finish_reason arrived


async def stream_answer(prompt: str, result: StreamResult) -> AsyncIterator[str]:
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=400,
        )
        async for chunk in stream:                       # async iteration over chunks
            if chunk.usage:                              # usage chunk at the end
                result.prompt_tokens = chunk.usage.prompt_tokens
                result.completion_tokens = chunk.usage.completion_tokens
            if not chunk.choices:                        # nothing else to read
                continue
            choice = chunk.choices[0]
            if choice.delta.content:                     # new text
                result.text += choice.delta.content      # keep full copy
                yield choice.delta.content               # forward to caller
            if choice.finish_reason:                     # generation ended
                result.finished = True
    except (APIConnectionError, APIStatusError) as exc:  # network or HTTP error mid-stream
        logger.error("stream broke after %d chars: %s", len(result.text), exc)
        yield "\n[stream interrupted]"                   # tell the user, keep partial text


async def main() -> None:
    res = StreamResult()
    async for piece in stream_answer("Why do tariffs have HS codes?", res):
        print(piece, end="", flush=True)
    print("\n", res.prompt_tokens, res.completion_tokens, res.finished)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Use `StreamingResponse` with the SSE media type. The browser reads it with `EventSource` or `fetch`.

```python
from fastapi import FastAPI                          # framework
from fastapi.responses import StreamingResponse      # streaming response
from pydantic import BaseModel                       # models
from openai import AsyncOpenAI                       # async client

app = FastAPI()                                      # app
client = AsyncOpenAI()                               # shared client


class Ask(BaseModel):
    question: str                                    # user question


async def sse_events(question: str):
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        stream=True,
    )
    try:
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content.replace("\n", "\\n")   # keep SSE lines valid
                yield f"data: {text}\n\n"                                    # SSE format
        yield "data: [DONE]\n\n"                                             # end marker
    except Exception:
        yield "event: error\ndata: upstream failure\n\n"                     # tell the client


@app.post("/ask-stream")
async def ask_stream(body: Ask) -> StreamingResponse:
    return StreamingResponse(sse_events(body.question), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `llm.stream()` and `llm.astream()` yield `AIMessageChunk` objects. LangGraph: `graph.astream(..., stream_mode="messages")` streams LLM tokens from inside nodes, and `stream_mode="updates"` streams per-node state updates.

```python
import asyncio
from langchain_openai import ChatOpenAI              # wrapper

llm = ChatOpenAI(model="gpt-4o-mini")                # model

async def main() -> None:
    async for chunk in llm.astream("Explain HS codes in 2 lines."):
        print(chunk.content, end="", flush=True)     # chunk is an AIMessageChunk
    print()

# asyncio.run(main())    # needs OPENAI_API_KEY

# LangGraph:
# async for msg, meta in graph.astream(inputs, stream_mode="messages"):
#     print(msg.content, end="")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `delta.content` is always a string
✅ Correct: It can be `None` (first and last chunks).

```python
# Wrong — crashes or prints "None"
print(chunk.choices[0].delta.content)
# Right
text = chunk.choices[0].delta.content
if text:
    print(text, end="")
```

❌ Mistake 2: Forgetting usage when streaming
✅ Correct: Pass `stream_options={"include_usage": True}`; otherwise you get no token counts and cost tracking breaks.

❌ Mistake 3: Streaming when you need to validate JSON first
✅ Correct: Do not stream partial JSON to users; buffer, parse, validate, then respond (or use structured outputs without streaming).

---

## 🧠 Tricky Interview Question

**Q**: "Streaming works locally, but behind nginx or a load balancer users see the whole answer at once after 10 seconds. Why?"

**Answer**: A proxy is buffering the response. Disable buffering (`proxy_buffering off` or send the `X-Accel-Buffering: no` header), avoid gzip middleware that buffers, keep idle timeouts above the generation time, and flush chunks. Also check that the client reads the stream incrementally (not `await response.text()`). Streaming is end to end: server, proxy, CDN, and browser all must pass bytes through.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `stream=True` do?
A1: The API returns chunks as they are generated instead of one final response.

Q2: [Easy] Does streaming make generation faster?
A2: No. Total time is similar; time to first token improves, so it feels faster.

Q3: [Medium] How do you get token usage while streaming?
A3: Set `stream_options={"include_usage": True}`; a final chunk with empty `choices` contains `usage`.

Q4: [Medium] What protocol is used and how do you serve it from FastAPI?
A4: Server-Sent Events over HTTP. Return `StreamingResponse(generator, media_type="text/event-stream")`.

Q5: [Hard] How do you handle a stream that fails halfway?
A5: Keep the partial text, log the failure, surface a clear "interrupted" message, and either retry from scratch (idempotent, costs again) or ask the model to continue using the partial text as an assistant message prefix. Never silently present partial output as complete. Check `finish_reason` to know if the answer ended naturally.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs and long answers
- User-facing latency matters

❌ Avoid when:
- Machine-to-machine calls (classification label only)
- You must validate full output (JSON, safety filters) before showing it
- Very short answers where it adds complexity for no gain

---

## 📊 Visual Diagram
```
Non-stream:  [ wait ............ 8s ............ ][ full answer ]
Stream:      [0.5s][The][ HS][ code][ is][ ...][ done ]
                ^ first token         total time similar

Browser <--SSE-- FastAPI StreamingResponse <--chunks-- OpenAI
                      |
              proxy must NOT buffer
```

---

## 💰 Cost Impact
- Same token pricing as non-streaming; streaming does not add cost.
- Risk: if the user cancels, generation may already be billed for tokens produced; closing the connection early can stop further tokens, so wire cancel buttons to abort the request.
- Without `include_usage` you lose accurate billing data, so always enable it.
- Optimise: set `max_tokens`, request concise answers, and stream only for human-facing paths.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Chunks sent as generated | Generate होते ही chunks |
| Chunk | One small piece of output | Output का छोटा टुकड़ा |
| delta | The new content in a chunk | Chunk में नया content |
| TTFT | Time to first token | पहले token तक का समय |
| SSE | Server-Sent Events protocol | Server से events भेजने का protocol |
| Buffering | Holding data before sending | भेजने से पहले data रोकना |

---

## ⚡ 3-Line Summary
English: Streaming returns the answer in chunks with `stream=True`, improving time to first token. Handle `None` deltas, request usage with `include_usage`, and make sure proxies do not buffer. Serve it from FastAPI with `StreamingResponse`.
Hindi: `stream=True` से जवाब chunks में आता है, जिससे पहला token जल्दी दिखता है। `None` deltas संभालो, `include_usage` से usage माँगो और proxies को buffer करने से रोको। FastAPI में `StreamingResponse` से serve करो।

---

## ➡️ Next Topic
**030. OpenAI API — Token Usage + Cost** — track and control what each call costs.
