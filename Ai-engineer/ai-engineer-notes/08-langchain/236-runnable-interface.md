---

# 236. Runnable Interface
# हिंदी में: Runnable Interface

---

## 🔵 Simple Definition (English)
`Runnable` is LangChain's base interface: any object with `invoke`, `ainvoke`, `stream`, `astream`, `batch`, `abatch` methods. Prompts, models, parsers, retrievers, tools and whole chains are all Runnables, so they can be combined the same way.

## 🔵 सरल परिभाषा (Hindi)
`Runnable` LangChain का base interface है: ऐसा object जिसमें `invoke`, `ainvoke`, `stream`, `astream`, `batch`, `abatch` methods हों। Prompts, models, parsers, retrievers, tools और पूरी chains सब Runnable हैं, इसलिए सब एक ही तरह जुड़ते हैं।

---

## 🔴 Problem it Solves
Before, each component had its own method (`predict`, `run`, `get_relevant_documents`, `__call__`), so you could not compose them uniformly or get streaming/async consistently. A single contract gives one way to call, stream, batch, retry, trace and compose anything.

## 🔴 यह क्यों बना? (Hindi)
पहले हर component की अपनी method थी (`predict`, `run`, `get_relevant_documents`, `__call__`), इसलिए एक जैसा compose करना और streaming/async पाना कठिन था। एक contract से call, stream, batch, retry, trace और compose सब एक ही तरीके से होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runnable defines: InputType, OutputType, invoke(input, config)
Step 2 → Defaults: ainvoke (runs invoke in executor), batch (thread pool), stream (one chunk)
Step 3 → Components override for real behavior (models stream tokens)
Step 4 → config (RunnableConfig): callbacks, tags, metadata, max_concurrency
Step 5 → Combinators: pipe |, bind(), with_config(), with_retry(), with_fallbacks()
Step 6 → Introspection: input_schema, output_schema, get_graph()
Step 7 → Custom: RunnableLambda, @chain, or subclass Runnable
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Runnable तय करता है: InputType, OutputType, invoke(input, config)
Step 2 → Defaults: ainvoke (executor में invoke), batch (thread pool), stream (एक chunk)
Step 3 → असली components override करते हैं (models tokens stream करते हैं)
Step 4 → config: callbacks, tags, metadata, max_concurrency
Step 5 → Combinators: |, bind(), with_config(), with_retry(), with_fallbacks()
Step 6 → Introspection: input_schema, output_schema, get_graph()
Step 7 → Custom: RunnableLambda, @chain, या Runnable subclass
```

---

## 🟡 Real World Example
**Tariff Classification System**: a custom `HSCodeValidator` Runnable takes the model's JSON and checks the code against the official list. Because it is a Runnable, `chain = prompt | llm | parser | HSCodeValidator()` gets async, batch and tracing for free, and appears as its own step in LangSmith. **Amazon-style**: a `PriceLookup` Runnable calling an internal service.

## 🟡 Real Example Hindi mein
**Tariff System**: कस्टम `HSCodeValidator` Runnable model के JSON को लेकर official सूची से code जाँचता है। क्योंकि यह Runnable है, `chain = prompt | llm | parser | HSCodeValidator()` में async, batch और tracing मुफ्त मिलते हैं, और LangSmith में अलग step दिखता है।

---

## 💻 Code Example — Basic
```python
# Runs offline: implementing and using a custom Runnable
from typing import Any
from langchain_core.runnables import Runnable, RunnableConfig

VALID: set[str] = {"8518.30", "8517.13"}  # tiny official list

class HSCodeValidator(Runnable[dict, dict]):
    """Takes {'hs_code': str} and adds 'valid': bool."""
    def invoke(self, input: dict, config: RunnableConfig | None = None, **kwargs: Any) -> dict:
        code = str(input.get("hs_code", "")).strip()  # read code safely
        return {**input, "valid": code in VALID}  # add flag, keep rest

v = HSCodeValidator()
print(v.invoke({"hs_code": "8518.30"}))  # {'hs_code': '8518.30', 'valid': True}
print(v.batch([{"hs_code": "0000.00"}, {"hs_code": "8517.13"}]))  # batch provided free
print(list(v.stream({"hs_code": "8517.13"})))  # stream provided free (one chunk)
import asyncio
print(asyncio.run(v.ainvoke({"hs_code": "1"})))  # async provided free
```

## 💻 Code Example — Advanced
```python
# Custom async Runnable with true async IO, config propagation and error handling
import asyncio
from typing import Any
import httpx
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda

class DutyRateLookup(Runnable[dict, dict]):
    """Calls an internal duty-rate service. Real async + sync fallbacks."""
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def invoke(self, input: dict, config: RunnableConfig | None = None, **kwargs: Any) -> dict:
        return asyncio.run(self.ainvoke(input, config))  # simple sync wrapper (not inside a running loop)

    async def ainvoke(self, input: dict, config: RunnableConfig | None = None, **kwargs: Any) -> dict:
        code = input["hs_code"]
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(f"{self.base_url}/duty/{code}")  # non-blocking IO
                r.raise_for_status()  # 4xx/5xx -> exception
                return {**input, "duty": r.json()}
        except httpx.HTTPError as exc:
            return {**input, "duty": None, "error": f"lookup failed: {exc}"}  # degrade gracefully

# Compose with others + attach config (tags show in traces):
pipeline = RunnableLambda(lambda x: x) | DutyRateLookup("http://duty.internal")
configured = pipeline.with_config({"tags": ["tariff", "duty"], "run_name": "duty_lookup"})
# results = await configured.abatch(inputs, config={"max_concurrency": 10})
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class In(BaseModel):
    hs_code: str

@app.post("/duty")
async def duty(body: In) -> dict:
    # Any Runnable can be exposed: same call pattern regardless of what's inside
    return await configured.ainvoke(body.model_dump())

# Inspect schemas for docs/validation:
# configured.input_schema.model_json_schema()
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph nodes accept Runnables; `Runnable.astream_events()` produces fine-grained events (tokens, tool starts) that UIs consume. `bind_tools`, `with_structured_output` return new Runnables. `RunnableConfig` carries callbacks and `configurable` fields (e.g., thread_id for LangGraph checkpointers).

```python
# graph.add_node("duty", DutyRateLookup("http://duty.internal"))
# config = {"configurable": {"thread_id": "user-42"}}   # LangGraph uses RunnableConfig
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to forward `config`
```python
# Wrong: inside a custom Runnable, calling child.invoke(x)   # loses tracing/callbacks
# Right
child.invoke(x, config)    # propagate config so traces nest and callbacks fire
```

❌ Mistake 2: Using `asyncio.run` inside a running event loop
```python
# Wrong: invoke() calling asyncio.run(...) when called from FastAPI route -> RuntimeError
# Right: call ainvoke() from async code; keep sync invoke for scripts
```

---

## 🧠 Tricky Interview Question
**Q**: "Your custom Runnable only implements `invoke`. In FastAPI you use `ainvoke` and throughput is poor. Why?"

**Answer**: The default `ainvoke` runs `invoke` in a thread-pool executor, so blocking IO consumes threads and the pool saturates. Implement a native `async def ainvoke` with an async client (httpx/aiohttp) so IO is non-blocking on the event loop.

---

## ⚫ Interview Questions + Answers

Q1: Name core Runnable methods. (Easy)
A1: invoke, ainvoke, stream, astream, batch, abatch (plus astream_events).

Q2: Is a chain a Runnable? (Easy)
A2: Yes. `prompt | llm` returns a RunnableSequence, itself a Runnable.

Q3: What is RunnableConfig? (Medium)
A3: A dict controlling a run: callbacks, tags, metadata, run_name, max_concurrency, recursion_limit, configurable.

Q4: `bind` vs `with_config`? (Medium)
A4: `bind(**kwargs)` presets call arguments to the underlying model/tool (e.g., stop=..., tools); `with_config` presets RunnableConfig (tags, callbacks).

Q5: How do you build a streaming custom Runnable? (Hard)
A5: Implement `transform`/`astream` that yields chunks, or use a generator function wrapped by `RunnableGenerator`. Downstream parsers that support streaming then process partial output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Wrapping custom logic so it composes, traces and streams like built-ins

❌ Avoid when:
- A one-off helper that never sits in a chain: just call a function

---

## 📊 Visual Diagram
```
               ┌───────────── Runnable[In, Out] ─────────────┐
               │ invoke  ainvoke  stream  astream  batch ... │
               └──────────────────────────────────────────────┘
   ▲        ▲        ▲        ▲         ▲          ▲
 Prompt   ChatModel Parser Retriever   Tool     Chain (a | b)
```

---

## 💰 Cost Impact
The interface itself costs nothing, but its defaults matter: `batch` runs concurrently and can trigger rate limits (set `max_concurrency`), retries resend prompts, and `astream_events` adds overhead but no tokens. Wrapping deterministic checks (validators) as Runnables avoids unnecessary LLM calls.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runnable | Common interface | साझा interface |
| invoke | Run once | एक बार चलाओ |
| stream | Yield chunks | टुकड़ों में output |
| batch | Run many inputs | कई inputs एक साथ |
| RunnableConfig | Run settings | Run की settings |

---

## ⚡ 3-Line Summary
English: Runnable is the universal interface with invoke, stream and batch (sync and async). Every LangChain component and chain implements it, which is why they compose. Implement native async for real concurrency.
Hindi: Runnable सबसे common interface है जिसमें invoke, stream, batch (sync और async) हैं। हर LangChain component और chain इसे implement करता है, इसलिए सब जुड़ते हैं। असली concurrency के लिए native async लिखो।

---

## ➡️ Next Topic
**237. Pipe Operator (|)** — how `|` builds RunnableSequence and what it really does.
