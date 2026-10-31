---

# 265. LangChain Streaming
# हिंदी में: LangChain Streaming (Tokens को live भेजना)

---

## 🔵 Simple Definition (English)
Streaming means the LLM answer arrives in small pieces (chunks) while it is still being generated, instead of one big block at the end. In LangChain every Runnable has `.stream()` / `.astream()` for chunks, and `.astream_events()` for fine-grained events (tokens, tool calls, retriever results) from inside a whole chain.

## 🔵 सरल परिभाषा (Hindi)
Streaming का मतलब है कि LLM का answer छोटे-छोटे हिस्सों (chunks) में तभी आना शुरू हो जाता है जब वह generate हो रहा होता है — पूरा answer बनने का इंतज़ार नहीं करना पड़ता। LangChain में हर Runnable पर `.stream()` / `.astream()` होता है, और पूरी chain के अंदर के events (tokens, tool calls, retriever results) के लिए `.astream_events()` होता है।

---

## 🔴 Problem it Solves
A normal `.invoke()` call waits for the full answer. For a long tariff explanation this can take 8-15 seconds of blank screen. Users think the app is frozen and leave. Also, in a chain (prompt -> LLM -> parser) you want partial output to flow through every step, not wait at each step.

Streaming fixes **perceived latency**: the first token appears in ~300-500 ms (time-to-first-token, TTFT), even if the total time is the same.

## 🔴 यह क्यों बना? (Hindi)
सामान्य `.invoke()` पूरा answer आने तक रुकता है। Tariff की लंबी explanation में 8-15 सेकंड तक screen खाली रहती है। User को लगता है app hang हो गया। Streaming से पहला token ~300-500 ms में दिखने लगता है (TTFT), भले ही total time वही हो। Chain के हर step से partial output आगे बहता रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You build a chain with LCEL:  prompt | llm | StrOutputParser()
Step 2 → You call chain.astream(input) instead of chain.ainvoke(input)
Step 3 → The chat model asks the provider for stream=True (SSE / chunked HTTP)
Step 4 → Provider sends token deltas -> model yields AIMessageChunk objects
Step 5 → Parser (StrOutputParser) is a streaming transform: chunk in -> str chunk out
Step 6 → Your code does `async for chunk in ...` and forwards each piece (SSE/WebSocket)
Step 7 → AIMessageChunks can be added (+) to rebuild the full message and usage
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LCEL से chain बनाओ:  prompt | llm | StrOutputParser()
Step 2 → chain.ainvoke() की जगह chain.astream() call करो
Step 3 → Chat model provider से stream=True माँगता है (SSE / chunked HTTP)
Step 4 → Provider token deltas भेजता है -> model AIMessageChunk yield करता है
Step 5 → Parser हर chunk को आगे transform करता है (chunk in -> str chunk out)
Step 6 → आपका code `async for chunk in ...` से हर piece user को भेजता है
Step 7 → AIMessageChunk को जोड़कर (+) पूरा message बनाया जा सकता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer asks "Classify wireless earbuds with a charging case and explain the duty rate." The explanation is ~400 tokens. With streaming, the UI shows "Wireless earbuds fall under HS 8518.30 ..." word by word, so the officer starts reading at once. If the officer sees the answer going in the wrong direction, they can cancel the request and save the remaining output tokens.

**Zomato-style**: A "What should I order?" assistant streams the recommendation, so the screen feels alive. **Amazon-style**: A product Q&A bot streams the answer while the review search is still finishing (using `astream_events` to show "Searching reviews..." status).

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "Charging case वाले wireless earbuds classify करो और duty rate बताओ।" Explanation ~400 tokens की है। Streaming से UI में "Wireless earbuds HS 8518.30 में आते हैं ..." शब्द-दर-शब्द दिखता है, officer तुरंत पढ़ना शुरू कर देता है। अगर answer गलत दिशा में जा रहा है तो request cancel करके बचे हुए output tokens का पैसा बचा सकता है।

**Zomato-style**: "क्या order करूँ?" assistant recommendation stream करता है। **Amazon-style**: Product Q&A bot review search चलते-चलते "Searching reviews..." status दिखाता है (`astream_events` से)।

---

## 💻 Code Example — Basic
```python
# Basic streaming with LangChain Core -- runs OFFLINE (fake model, no API key)
# pip install langchain-core
import asyncio                                                    # to run the async version
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # fake LLM for testing
from langchain_core.messages import AIMessage                     # message type the fake model returns
from langchain_core.output_parsers import StrOutputParser         # turns AIMessageChunk -> str
from langchain_core.prompts import ChatPromptTemplate             # builds the prompt

# Fake model: it "streams" the text word by word (like a real LLM would token by token)
fake_text = "Wireless earbuds are classified under HS 8518.30 with 0 percent duty."  # the canned answer
llm = GenericFakeChatModel(messages=iter([AIMessage(content=fake_text)] * 2))  # allow 2 calls (sync + async)

# Build an LCEL chain: prompt | model | parser
prompt = ChatPromptTemplate.from_messages([("user", "Classify: {product}")])   # one template variable
chain = prompt | llm | StrOutputParser()                          # the pipe operator creates a RunnableSequence

# --- Sync streaming ---
print("SYNC  : ", end="")                                         # label, no newline
for chunk in chain.stream({"product": "wireless earbuds"}):       # chain.stream yields str pieces
    print(chunk, end="|", flush=True)                             # show chunk boundaries with a bar
print()                                                           # final newline

# --- Async streaming ---
async def main() -> None:                                         # async entry point
    print("ASYNC : ", end="")                                     # label
    async for chunk in chain.astream({"product": "wireless earbuds"}):  # astream = non-blocking version
        print(chunk, end="|", flush=True)                         # print each piece immediately
    print()                                                       # final newline

asyncio.run(main())                                               # run the coroutine
```

## 💻 Code Example — Advanced
```python
# Production: streaming chain with timeout, error handling, token usage and astream_events
# pip install langchain-openai langchain-core
import asyncio                                                    # async runtime and timeouts
import logging                                                    # structured logging
from typing import AsyncIterator                                  # type hint for async generators

from langchain_core.messages import AIMessageChunk                # chunk type (supports + operator)
from langchain_core.output_parsers import StrOutputParser         # str parser (streaming transform)
from langchain_core.prompts import ChatPromptTemplate             # prompt template
from langchain_openai import ChatOpenAI                           # OpenAI chat model wrapper

logger = logging.getLogger("tariff.stream")                       # module logger

SYSTEM = "You are a customs tariff expert. Give HS code, then a short reason."  # fixed system prompt

prompt = ChatPromptTemplate.from_messages(                        # prompt with system + user
    [("system", SYSTEM), ("user", "Product: {product}")]
)
llm = ChatOpenAI(                                                 # real model
    model="gpt-4o-mini",                                          # cheap and fast
    temperature=0,                                                # deterministic for classification
    max_tokens=300,                                               # cap output cost
    timeout=30,                                                   # network timeout (seconds)
    max_retries=2,                                                # retry transient failures
    stream_usage=True,                                            # ask provider for usage in the stream
)
chain = prompt | llm                                              # keep AIMessageChunk (needed for usage)


async def stream_classification(product: str) -> AsyncIterator[str]:
    """Yield text pieces of the answer; log token usage at the end."""
    final: AIMessageChunk | None = None                           # will hold the merged message
    try:
        async with asyncio.timeout(45):                           # hard cap for the whole stream (py3.11+)
            async for chunk in chain.astream({"product": product}):  # each chunk is an AIMessageChunk
                final = chunk if final is None else final + chunk # merge chunks with +
                if chunk.content:                                 # skip empty keep-alive chunks
                    yield str(chunk.content)                      # forward text to the caller
    except asyncio.TimeoutError:                                  # whole stream took too long
        logger.error("stream timeout for %s", product)            # log it
        yield "\n[Error: timeout, please retry]"                  # tell the client politely
    except asyncio.CancelledError:                                # client disconnected
        logger.info("client cancelled stream")                    # not an error, just log
        raise                                                     # ALWAYS re-raise CancelledError
    except Exception as exc:                                      # provider/network error
        logger.exception("stream failed: %s", exc)                # log with traceback
        yield "\n[Error: classification failed]"                  # safe message for the client
    finally:
        if final is not None and final.usage_metadata:            # usage appears on the merged chunk
            logger.info("usage=%s", final.usage_metadata)         # input/output/total tokens


async def stream_with_status(product: str) -> AsyncIterator[dict[str, str]]:
    """astream_events: get token events AND lifecycle events of the chain."""
    full_chain = prompt | llm | StrOutputParser()                 # chain with parser
    async for event in full_chain.astream_events({"product": product}, version="v2"):  # v2 is current
        kind: str = event["event"]                                # event type name
        if kind == "on_chat_model_start":                         # model began
            yield {"type": "status", "data": "thinking"}          # show a status in the UI
        elif kind == "on_chat_model_stream":                      # a token arrived
            token = event["data"]["chunk"].content                # AIMessageChunk.content
            if token:                                             # ignore empty
                yield {"type": "token", "data": str(token)}       # forward token
        elif kind == "on_chain_end" and event["name"] == "RunnableSequence":  # whole chain done
            yield {"type": "done", "data": ""}                    # signal end
```

---

## 🟠 FastAPI Integration
FastAPI returns a `StreamingResponse` with `media_type="text/event-stream"` (Server-Sent Events). Each LangChain chunk becomes one SSE line `data: ...\n\n`. The browser reads it with `EventSource` or `fetch` + reader.

```python
# FastAPI + LangChain streaming over SSE
import json                                                       # to encode chunks safely
from fastapi import FastAPI, Request                              # web framework
from fastapi.responses import StreamingResponse                   # streaming HTTP response
from pydantic import BaseModel, Field                             # request validation (v2)
from langchain_core.output_parsers import StrOutputParser         # str parser
from langchain_core.prompts import ChatPromptTemplate             # prompt
from langchain_openai import ChatOpenAI                           # model

app = FastAPI()                                                   # app instance
chain = (                                                         # built once, reused per request
    ChatPromptTemplate.from_messages([("user", "HS code and reason for: {product}")])
    | ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)
    | StrOutputParser()
)


class ClassifyRequest(BaseModel):                                 # input schema
    product: str = Field(min_length=2, max_length=500)            # reject empty/huge input


@app.post("/classify/stream")                                     # POST route
async def classify_stream(body: ClassifyRequest, request: Request) -> StreamingResponse:
    async def event_gen():                                        # async generator of SSE lines
        try:
            async for piece in chain.astream({"product": body.product}):  # LangChain chunks
                if await request.is_disconnected():               # client closed the tab
                    break                                         # stop -> stop paying for tokens
                yield f"data: {json.dumps({'token': piece})}\n\n" # SSE frame (JSON-encoded)
            yield "data: [DONE]\n\n"                              # end marker
        except Exception:                                         # never leak a stack trace
            yield f"data: {json.dumps({'error': 'internal'})}\n\n"  # error frame
    return StreamingResponse(                                     # wrap generator
        event_gen(),
        media_type="text/event-stream",                           # SSE content type
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # stop nginx buffering
    )
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `.stream`, `.astream`, `.astream_events` exist on every Runnable. Streaming works through the whole chain only if each step can transform streams (prompts, models, `StrOutputParser`, `JsonOutputParser` do; a plain Python function wrapped in `RunnableLambda` does NOT stream - it waits for the full input unless it is a generator).

LangGraph: `graph.astream(input, stream_mode=...)` with modes `"values"` (full state after each step), `"updates"` (only the changed part per node), `"messages"` (LLM tokens from any node), `"custom"` (your own events).

```python
# LangGraph streaming: tokens from inside nodes + node updates
from langgraph.graph import StateGraph, START, END                # graph builder
from typing import TypedDict                                      # state type

class State(TypedDict):                                           # graph state
    product: str                                                  # input
    answer: str                                                   # output

async def classify(state: State) -> dict[str, str]:               # one node
    msg = await llm.ainvoke(f"HS code for {state['product']}")    # llm from above
    return {"answer": str(msg.content)}                           # partial state update

g = StateGraph(State)                                             # create graph
g.add_node("classify", classify)                                  # add node
g.add_edge(START, "classify")                                     # start -> node
g.add_edge("classify", END)                                       # node -> end
app_graph = g.compile()                                           # compile

async def run() -> None:
    # stream_mode="messages" yields (message_chunk, metadata) as tokens are generated
    async for chunk, meta in app_graph.astream({"product": "earbuds"}, stream_mode="messages"):
        print(chunk.content, end="", flush=True)                  # print token live
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `ainvoke` inside the generator, so nothing is streamed
```python
# Wrong -- waits for the full answer, then sends it as ONE chunk
async def gen():
    result = await chain.ainvoke({"product": p})   # blocks until complete
    yield result                                   # user saw nothing for 10 seconds

# Right -- iterate astream
async def gen():
    async for piece in chain.astream({"product": p}):
        yield piece
```

❌ Mistake 2: Using a plain `RunnableLambda` after the model and wondering why streaming stopped
```python
# Wrong -- lambda receives the FULL input, so the stream is buffered
chain = prompt | llm | StrOutputParser() | RunnableLambda(lambda s: s.upper())

# Right -- make it a generator transform so chunks flow through
def upper_stream(chunks):                          # takes an iterator of chunks
    for c in chunks:                               # handle each chunk
        yield c.upper()                            # emit immediately
chain = prompt | llm | StrOutputParser() | RunnableGenerator(upper_stream)
```

❌ Mistake 3: Swallowing `CancelledError` or ignoring client disconnect (tokens keep being generated and billed). Always re-raise `CancelledError` and check `request.is_disconnected()`.

---

## 🧠 Tricky Interview Question

**Q**: "Your streaming endpoint works locally, but in production behind nginx the user still sees the whole answer at once at the end. The code is correct. What is wrong?"

**Answer**: A reverse proxy or CDN is **buffering** the response. nginx buffers upstream responses by default, so SSE frames are collected and released together. Fix: set header `X-Accel-Buffering: no` (or `proxy_buffering off;`), send `Cache-Control: no-cache`, disable gzip for `text/event-stream`, and make sure the load balancer idle timeout is longer than your longest answer. Also check that no middleware (e.g. `GZipMiddleware`) wraps the stream. The LangChain code is not the problem - the transport is.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `.invoke()` and `.stream()`?
A1: `.invoke()` returns the full result once. `.stream()` returns an iterator of chunks as they are produced. Total time is similar, but time-to-first-token is much lower with streaming.

Q2: What do `astream` and `stream` return for a chat model?
A2: `AIMessageChunk` objects. With `StrOutputParser` at the end of the chain they become plain `str` pieces. `AIMessageChunk` objects can be added with `+` to rebuild the full message.

Q3: When do you use `astream_events` instead of `astream`?
A3: When you need events from inside the chain: which step started/ended, tokens from a specific model, retriever documents, tool calls. `astream` only gives the final output stream of the last step. Use `version="v2"` and filter by `event` and `name`/tags.

Q4: How do you get token usage while streaming?
A4: With OpenAI set `stream_usage=True` on `ChatOpenAI` (or `stream_options={"include_usage": True}`). The last chunk carries `usage_metadata`; merge chunks with `+` and read `final.usage_metadata`. Without it, streaming responses report no usage and your cost tracking is blind.

Q5 (Hard): How would you stream structured JSON output (a tariff record) so the UI can render fields as they arrive?
A5: Use `JsonOutputParser` (or `PydanticOutputParser` with partial parsing) - it emits progressively larger partial dicts as the JSON grows. Alternatively use a provider's structured output with `.astream` and merge partials. Send only the diff to the client, validate the final object with Pydantic once at the end, and treat partial objects as untrusted (fields may be missing or cut). Never act on a partial result (e.g. write to DB) before the final validated one.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A human is reading the answer (chat UI, assistant, copilot)
- Answers are long (over ~100 tokens)
- You want a cancel button to save tokens
- You want progress/status events in a multi-step chain

❌ Avoid when:
- Machine-to-machine call that needs the full JSON anyway (use `ainvoke` or `abatch`)
- You must validate the entire output before showing it (moderation, compliance review)
- Batch jobs (streaming adds overhead, no benefit)

---

## 📊 Visual Diagram
```
 Browser        FastAPI              LangChain chain            LLM provider
    │  POST /stream │                       │                        │
    │──────────────►│  chain.astream()      │                        │
    │               │──────────────────────►│  stream=True           │
    │               │                       │───────────────────────►│
    │  data: Wire   │◄── "Wire" ────────────│◄── delta "Wire" ───────│
    │◄──────────────│                       │                        │
    │  data: less   │◄── "less" ────────────│◄── delta "less" ───────│
    │◄──────────────│                       │                        │
    │  data: [DONE] │◄── end ───────────────│◄── finish + usage ─────│
    │◄──────────────│                       │                        │
 First token ≈ 0.4 s   (without streaming: first byte at ≈ 9 s)
```

---

## 💰 Cost Impact
Streaming itself costs **nothing extra** - same input and output tokens. Savings come from behaviour:
- **Cancel early**: stop on client disconnect -> do not pay for the unread rest (can save 20-40% of output tokens on chat UIs).
- **`max_tokens`** cap protects against runaway answers.
- Usage is **not reported by default while streaming** - enable `stream_usage=True` or you cannot track cost.
- Example: 400 output tokens on gpt-4o-mini = 400 x $0.60 / 1M = $0.00024. If 30% of users cancel after half, you save ~$0.000036 per request - at 1M requests/month about $36.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Output delivered piece by piece | Output टुकड़ों में मिलना |
| Chunk | One piece of a streamed answer | Stream का एक हिस्सा |
| TTFT | Time to first token | पहला token आने का समय |
| SSE | Server-Sent Events, one-way HTTP stream | Server से client को one-way stream |
| AIMessageChunk | Streamed message piece, can be added with + | Message का chunk |
| astream_events | Stream of internal chain events | Chain के अंदर के events |
| Backpressure/buffering | Proxy holds data before sending | Data रुक जाना / buffer होना |

---

## ⚡ 3-Line Summary
English: Streaming sends the answer in chunks, so the first token shows in under a second. Use `astream` for output chunks and `astream_events` for internal events; wire it to FastAPI with SSE. Enable `stream_usage`, handle disconnects, and watch out for proxy buffering.
Hindi: Streaming में answer chunks में आता है, इसलिए पहला token एक सेकंड से पहले दिख जाता है। Output के लिए `astream` और internal events के लिए `astream_events` use करो, FastAPI में SSE से जोड़ो। `stream_usage` on रखो, client disconnect handle करो, और proxy buffering से सावधान रहो।

---

## ➡️ Next Topic
**266. LangChain Async** - `ainvoke`, `abatch`, concurrency limits and how to run many chain calls in parallel without blocking the event loop.
