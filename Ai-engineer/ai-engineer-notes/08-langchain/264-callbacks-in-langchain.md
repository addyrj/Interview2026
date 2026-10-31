---

# 264. Callbacks in LangChain
# हिंदी में: LangChain में Callbacks

---

## 🔵 Simple Definition (English)
Callbacks are hooks that LangChain calls at key moments (LLM start, LLM end, token, tool start, chain error, ...). You write a handler class with methods like `on_llm_end` and pass it in `config={"callbacks": [handler]}`. Use them for logging, metrics, token counting, streaming and tracing, without changing your chain.

## 🔵 सरल परिभाषा (Hindi)
Callbacks वो hooks हैं जिन्हें LangChain ज़रूरी मौकों पर बुलाता है (LLM शुरू, LLM ख़त्म, token, tool शुरू, chain error, ...)। आप `on_llm_end` जैसे methods वाली handler class लिखते हैं और `config={"callbacks": [handler]}` में देते हैं। Chain बदले बिना logging, metrics, token counting, streaming और tracing के लिए काम आते हैं।

---

## 🔴 Problem it Solves
- You cannot see what happens inside a chain: which prompt was sent, how many tokens, how long.
- Adding print or logging inside each step clutters the code.
- Streaming tokens to a UI needs a hook on every new token.
- Production needs metrics and error alerts per call.

## 🔴 यह क्यों बना? (Hindi)
- Chain के अंदर क्या हो रहा है पता नहीं चलता: कौन सा prompt गया, कितने tokens, कितना समय।
- हर step में print/logging डालने से code गंदा होता है।
- UI पर tokens stream करने के लिए हर नए token पर hook चाहिए।
- Production को हर call के metrics और error alerts चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Subclass BaseCallbackHandler (sync) or AsyncCallbackHandler (async)
Step 2 → Implement only the events you care about: on_llm_start, on_llm_end, on_llm_new_token,
         on_chain_start/end, on_tool_start/end, on_retriever_end, on_*_error
Step 3 → Pass at call time: chain.invoke(x, config={"callbacks": [MyHandler()]})
Step 4 → LangChain propagates the handler to every child step (prompt, retriever, LLM)
Step 5 → Each event hands you data: prompts, response, token usage, run_id
Step 6 → Log, count, push to metrics, or stream to the client
Step 7 → Constructor-level callbacks only apply to that object; request-level ones apply to the whole run
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → BaseCallbackHandler (sync) या AsyncCallbackHandler (async) को subclass करो
Step 2 → सिर्फ़ ज़रूरी events लिखो: on_llm_start, on_llm_end, on_llm_new_token,
         on_chain_start/end, on_tool_start/end, on_retriever_end, on_*_error
Step 3 → Call के समय दो: chain.invoke(x, config={"callbacks": [MyHandler()]})
Step 4 → LangChain handler को हर child step (prompt, retriever, LLM) तक पहुँचाता है
Step 5 → हर event में data मिलता है: prompts, response, token usage, run_id
Step 6 → Log करो, गिनो, metrics भेजो, या client को stream करो
Step 7 → Constructor के callbacks सिर्फ़ उसी object पर; request-level पूरे run पर लागू होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A `CostTracker` callback sums `prompt_tokens` and `completion_tokens` after every LLM call and writes them to a metrics store per customer, so you can bill and spot expensive queries. A `LatencyLogger` records how long retrieval took vs generation.
**Zomato AI**: a streaming callback pushes each token to the chat UI via WebSocket.

## 🟡 Real Example Hindi mein
**Tariff System**: `CostTracker` callback हर LLM call के बाद `prompt_tokens` और `completion_tokens` जोड़ता है और customer के हिसाब से metrics store में लिखता है, ताकि billing हो सके और महंगी queries पकड़ी जाएँ। `LatencyLogger` retrieval और generation का समय अलग-अलग लिखता है।
**Zomato AI**: streaming callback हर token WebSocket से chat UI पर भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic: the callback pattern in pure Python (runnable): a function that fires events to handlers
import time
from typing import Any, Dict, List, Protocol

class Handler(Protocol):
    def on_start(self, prompt: str) -> None: ...
    def on_end(self, output: str, usage: Dict[str, int]) -> None: ...

class Logger:
    """Prints events and measures time."""
    def __init__(self) -> None:
        self.t0 = 0.0
    def on_start(self, prompt: str) -> None:
        self.t0 = time.perf_counter()                     # start timer
        print(f"[start] prompt chars={len(prompt)}")
    def on_end(self, output: str, usage: Dict[str, int]) -> None:
        ms = (time.perf_counter() - self.t0) * 1000       # elapsed time
        print(f"[end] {ms:.1f} ms, tokens={usage}")

def fake_llm_call(prompt: str, handlers: List[Any]) -> str:
    for h in handlers:
        h.on_start(prompt)                                # fire "start" event
    output = "HS 8518.22"                                 # pretend model output
    usage = {"prompt_tokens": len(prompt) // 4, "completion_tokens": 5}
    for h in handlers:
        h.on_end(output, usage)                           # fire "end" event
    return output

if __name__ == "__main__":
    print(fake_llm_call("HS code for a Bluetooth speaker?", [Logger()]))
    # Real LangChain: handler = BaseCallbackHandler subclass; chain.invoke(x, config={"callbacks": [handler]})
```

## 💻 Code Example — Advanced
```python
# Production callbacks: token/cost tracker + latency + error log + async streaming
import asyncio
import logging
import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

log = logging.getLogger("tariff.llm")

class CostTracker(BaseCallbackHandler):
    """Counts tokens and time for every LLM call in a run."""
    PRICE_IN, PRICE_OUT = 0.15 / 1_000_000, 0.60 / 1_000_000    # gpt-4o-mini per token

    def __init__(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self._starts: dict[UUID, float] = {}

    def on_chat_model_start(self, serialized: dict[str, Any], messages: list, *,
                            run_id: UUID, **kwargs: Any) -> None:
        self._starts[run_id] = time.perf_counter()              # chat models fire this event

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        usage = (response.llm_output or {}).get("token_usage", {})   # present for OpenAI models
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        started = self._starts.pop(run_id, None)
        if started is not None:
            log.info("llm call took %.0f ms", (time.perf_counter() - started) * 1000)

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        log.error("llm error: %s", type(error).__name__)         # alert hook

    @property
    def cost_usd(self) -> float:
        return self.prompt_tokens * self.PRICE_IN + self.completion_tokens * self.PRICE_OUT

class TokenStreamer(AsyncCallbackHandler):
    """Async handler: forwards each new token to a queue (for WebSocket/SSE)."""
    def __init__(self, queue: "asyncio.Queue[str | None]") -> None:
        self.queue = queue
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.queue.put(token)
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        await self.queue.put(None)                               # sentinel: stream finished

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=200)
chain = ChatPromptTemplate.from_template("HS code for: {product}") | llm | StrOutputParser()

async def run(product: str) -> None:
    tracker = CostTracker()
    try:
        text = await chain.ainvoke({"product": product}, config={"callbacks": [tracker]})
        print(text, f"| tokens in/out: {tracker.prompt_tokens}/{tracker.completion_tokens}",
              f"| cost ${tracker.cost_usd:.6f}")
    except Exception as exc:                                     # handler errors never hide this
        print("failed:", type(exc).__name__)

if __name__ == "__main__":
    asyncio.run(run("Bluetooth speaker"))   # needs OPENAI_API_KEY (token_usage depends on provider)
```

---

## 🟠 FastAPI Integration
Create a new handler per request (handlers hold per-request state), and pass it through `config`. Stream tokens with a queue.

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()
stream_llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)       # streaming=True fires on_llm_new_token
stream_chain = ChatPromptTemplate.from_template("HS code for: {product}") | stream_llm | StrOutputParser()

class Q(BaseModel):
    product: str

@app.post("/classify/stream")
async def classify_stream(q: Q) -> StreamingResponse:
    queue: asyncio.Queue[str | None] = asyncio.Queue()
    task = asyncio.create_task(                                   # run the chain in the background
        stream_chain.ainvoke({"product": q.product}, config={"callbacks": [TokenStreamer(queue)]})
    )

    async def gen():
        while (tok := await queue.get()) is not None:             # until the sentinel
            yield f"data: {tok}\n\n"
        await task                                                # surface exceptions, if any

    return StreamingResponse(gen(), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
Callbacks are the foundation of **LangSmith tracing** (a tracer is just a callback handler) and `get_openai_callback()`. In LangGraph, pass `config={"callbacks": [...]}` to `graph.invoke` and it reaches every node and LLM call. LangChain also exposes `astream_events` for event streaming without writing a handler.

```python
async def show_tokens() -> None:
    async for event in chain.astream_events({"product": "speaker"}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="")       # tokens without a custom handler
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A sync handler doing slow I/O inside an async chain (blocks the event loop).
✅ Correct: Use `AsyncCallbackHandler`, or offload to a thread/queue.

```python
# Wrong: blocking HTTP call inside a callback
def on_llm_end(self, response, **kwargs): requests.post(METRICS_URL, json=...)
# Right: async handler
async def on_llm_end(self, response, **kwargs): await http.post(METRICS_URL, json=...)
```

❌ Mistake 2: One shared handler instance across requests (token counts get mixed up).
✅ Correct: Create a handler per request.

❌ Mistake 3: Putting callbacks only in the constructor (`ChatOpenAI(callbacks=[h])`) and expecting chain-level events.
✅ Correct: Pass callbacks in `config` at run time to capture the whole chain.

---

## 🧠 Tricky Interview Question
**Q**: "Your handler's `on_llm_start` never fires with a ChatOpenAI model, though it worked with an old completion LLM. Why?"

**Answer**: Chat models fire `on_chat_model_start` (it receives messages, not prompt strings). If a handler implements only `on_llm_start`, LangChain's default `on_chat_model_start` raises `NotImplementedError` and then falls back to `on_llm_start` with stringified messages, which can hide the difference; so implement `on_chat_model_start` explicitly. Also check: sync vs async handler in an async chain, callbacks passed at run time via `config`, and for token usage that the provider returns it (for streaming OpenAI, usage may need `stream_usage=True`).

---

## ⚫ Interview Questions + Answers

Q1: What is a callback in LangChain?
A1: A handler object with methods that LangChain invokes on events (LLM start/end, tokens, tools, chain errors).

Q2: How do you attach callbacks to a chain?
A2: Pass `config={"callbacks": [handler]}` at invoke time (request-scoped), or set `callbacks=[...]` on an object (object-scoped).

Q3: Difference between `BaseCallbackHandler` and `AsyncCallbackHandler`?
A3: Sync handlers run synchronously (in a thread executor in async chains); async handlers have `async def` methods and are awaited without blocking the loop.

Q4: How can you count tokens and cost per request?
A4: A callback reading `LLMResult.llm_output["token_usage"]` (or `usage_metadata` on messages), summed per request; `get_openai_callback()` does this for OpenAI. Persist it with user or tenant id.

Q5: Design observability for a RAG service with callbacks.
A5: A per-request handler collects: retriever latency and doc count (`on_retriever_end`), LLM latency and tokens (`on_llm_end`), errors (`on_*_error`), and the final answer. Push to metrics (Prometheus) and structured logs with a request id; use LangSmith for traces; sample prompts to avoid logging PII; alert on error rate, p95 latency and cost per request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logging, metrics, token counting
- Streaming tokens to UI
- Debugging and tracing chain internals

❌ Avoid when:
- You need to change the data in the chain (use a Runnable step instead)
- Heavy blocking work inside handlers

---

## 📊 Visual Diagram
```
 chain.invoke(input, config={"callbacks":[handler]})
        │
        ├─ on_chain_start ─────────────► handler
        ├─ on_retriever_start/end ─────► handler
        ├─ on_chat_model_start ────────► handler
        ├─ on_llm_new_token (x N) ─────► handler ──► WebSocket / SSE
        ├─ on_llm_end (usage) ─────────► handler ──► metrics / cost
        ├─ on_*_error ─────────────────► handler ──► alert
        └─ on_chain_end ───────────────► handler
```

---

## 💰 Cost Impact
- Callbacks themselves cost no tokens. They show you the tokens: prompt_tokens, completion_tokens per call.
- Use them to find expensive steps: e.g., a RAG request with 1500 input tokens where 1200 is context.
- Optimise based on data: lower `k`, shorten the system prompt, route easy queries to a cheaper model, add budgets (raise an error when a user exceeds a daily token cap) in the handler.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback handler | Object receiving events | Events पाने वाला object |
| on_llm_end | Fires when the LLM finishes | LLM ख़त्म होने पर चलता है |
| on_llm_new_token | Fires for each streamed token | हर streamed token पर |
| run_id | Unique id for a run | Run की अनोखी id |
| LangSmith | Tracing/eval platform | Tracing और eval platform |
| astream_events | Event stream API | Events का stream API |

---

## ⚡ 3-Line Summary
English: Callbacks let you hook into LangChain events for logging, token counting, streaming, and tracing without changing chain code. Pass request-scoped handlers via config and use async handlers in async apps. Track tokens and latency to control cost.
Hindi: Callbacks से chain का code बदले बिना LangChain events पर logging, token counting, streaming और tracing की जा सकती है। Handlers को config से request-scope में दो और async apps में async handlers लगाओ। Cost काबू में रखने के लिए tokens और latency track करो।

---

## ➡️ Next Topic
**265. LangChain Streaming**: stream tokens and events to users for faster-feeling responses.
