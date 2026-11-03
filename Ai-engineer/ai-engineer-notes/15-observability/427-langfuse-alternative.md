
# 427. Langfuse — Alternative
# हिंदी में: Langfuse — LangSmith का विकल्प

---

## 🔵 Simple Definition (English)
Langfuse is an open-source LLM observability platform (traces, prompt management, evaluations, cost and latency dashboards). You can self-host it or use the cloud version. It is a popular alternative to LangSmith and works with any framework, not only LangChain.

## 🔵 सरल परिभाषा (Hindi)
Langfuse एक open-source LLM observability platform है (traces, prompt management, evaluations, cost और latency dashboards)। इसे self-host कर सकते हैं या cloud version use कर सकते हैं। यह LangSmith का लोकप्रिय विकल्प है और सिर्फ़ LangChain नहीं, किसी भी framework के साथ चलता है।

---

## 🔴 Problem it Solves
LangSmith is hosted and tied closely to the LangChain ecosystem. Some teams need data to stay inside their own network (customs, finance, health), want open-source code they can inspect, want to avoid vendor lock-in, or use many frameworks (plain OpenAI SDK, LlamaIndex, custom agents). Langfuse offers the same core observability with self-hosting and framework-neutral SDKs.

## 🔴 यह क्यों बना? (Hindi)
LangSmith hosted है और LangChain ecosystem से जुड़ा है। कुछ teams को data अपने network में रखना होता है (customs, finance, health), open-source code चाहिए, vendor lock-in से बचना है, या वे कई frameworks (plain OpenAI SDK, LlamaIndex, custom agents) use करते हैं। Langfuse वही core observability self-hosting और framework-neutral SDKs के साथ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Your app calls an LLM inside an instrumented function (decorator, wrapper or callback)
Step 2 → SDK records a trace: input, output, latency, model, token usage, nested spans
Step 3 → SDK batches events and sends them asynchronously to the Langfuse server
Step 4 → Server stores traces in its database (self-hosted: Postgres/ClickHouse stack)
Step 5 → UI shows traces, sessions, users, cost and latency dashboards
Step 6 → You attach scores (user feedback, LLM-as-judge) and build datasets from traces
Step 7 → Prompts are versioned in Langfuse and fetched at runtime
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App instrumented function के अंदर LLM call करता है (decorator, wrapper या callback)
Step 2 → SDK trace record करता है: input, output, latency, model, token usage, nested spans
Step 3 → SDK events को batch करके asynchronously Langfuse server भेजता है
Step 4 → Server traces अपने database में रखता है (self-hosted: Postgres/ClickHouse stack)
Step 5 → UI में traces, sessions, users, cost और latency dashboards दिखते हैं
Step 6 → Scores (user feedback, LLM-as-judge) जोड़ो और traces से datasets बनाओ
Step 7 → Prompts Langfuse में version होते हैं और runtime पर fetch होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs policy forbids sending importer data to third-party SaaS. The team self-hosts Langfuse in its VPC. Every classification request becomes a trace with spans for retrieval, reranking and the LLM call. Officers' corrections are logged as scores, and wrong-HS-code traces become a regression dataset.

**Amazon-style catalogue**: Different teams use different frameworks; Langfuse gives a single dashboard with cost per team via tags and user ids.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs policy importer data को third-party SaaS में भेजने नहीं देती। Team Langfuse अपने VPC में self-host करती है। हर classification request एक trace बनता है जिसमें retrieval, reranking और LLM call के spans होते हैं। Officers की corrections scores की तरह log होती हैं और ग़लत HS-code वाले traces regression dataset बनते हैं।

**Amazon-style catalogue**: अलग teams अलग frameworks use करती हैं; Langfuse tags और user ids से team-wise cost के साथ एक dashboard देता है।

---

## 💻 Code Example — Basic
```python
# Pure-Python mini tracer that mimics what Langfuse records (runs without any install)
import time  # measure latency
import uuid  # trace ids
from typing import Any, Callable  # type hints

TRACES: list[dict[str, Any]] = []  # in-memory store


def observe(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that records input, output and latency of a function call."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()  # start timer
        result = fn(*args, **kwargs)  # call the real function
        TRACES.append({
            "id": str(uuid.uuid4()),  # unique id
            "name": fn.__name__,  # span name
            "input": args,  # captured input
            "output": result,  # captured output
            "latency_ms": round((time.perf_counter() - start) * 1000, 3),  # elapsed ms
        })
        return result  # return normal result
    return wrapper  # return decorated function


@observe  # record every call
def classify(text: str) -> str:
    return "8518.30" if "earbud" in text.lower() else "unknown"  # fake classifier


if __name__ == "__main__":
    print(classify("Wireless earbuds"))  # run once
    print(TRACES[0]["name"], TRACES[0]["latency_ms"], "ms")  # show trace summary
```

## 💻 Code Example — Advanced
```python
# Real Langfuse usage (Python SDK v3 style). SDK names change between major versions: check docs.
# pip install langfuse openai ; env: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
import asyncio  # async version
import logging  # logging

from langfuse import get_client, observe  # v3 imports (v2 used langfuse.decorators)

logger = logging.getLogger("tariff.obs")  # logger


@observe(name="retrieve")  # nested span for retrieval
def retrieve(query: str) -> list[str]:
    return ["Heading 8518: microphones, headphones, earphones"]  # fake retrieval


@observe(name="classify-hs-code")  # top-level trace
def classify(query: str) -> str:
    docs = retrieve(query)  # child span
    langfuse = get_client()  # client for adding metadata
    langfuse.update_current_trace(user_id="importer-42", tags=["tariff", "prod"])  # searchable fields
    # answer = llm_call(query, docs)  # real LLM call would go here (e.g. wrapped OpenAI client)
    return "8518.30" if docs else "unknown"  # placeholder result


async def classify_async(query: str) -> str:
    """Async wrapper; the decorator also supports async def functions."""
    try:
        return await asyncio.to_thread(classify, query)  # run sync traced function in thread
    except Exception as exc:  # never let tracing break the business flow
        logger.error("classification failed: %s", exc)  # log error
        raise  # propagate
    finally:
        get_client().flush()  # ensure events are sent in short-lived processes
```
Token usage: Langfuse captures `usage` (input/output tokens) from supported SDK integrations and computes cost from model price tables; for custom calls you pass usage yourself.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # web framework
from langfuse import observe  # tracing decorator (v3)
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Req(BaseModel):
    description: str  # product text


@observe(name="api-classify")  # each request = one trace
async def handle(description: str) -> dict:
    return {"hs_code": "8518.30"}  # placeholder business logic


@app.post("/classify")
async def classify(req: Req) -> dict:
    return await handle(req.description)  # traced call
```
In production call `get_client().flush()` on shutdown (lifespan) so the last events are not lost.

---

## 🔗 LangChain / LangGraph Connection
Langfuse provides a LangChain callback handler that traces chains and LangGraph runs automatically.

```python
from langfuse.langchain import CallbackHandler  # v3 location (v2: langfuse.callback)
from langchain_openai import ChatOpenAI  # LLM

handler = CallbackHandler()  # reads keys from env
llm = ChatOpenAI(model="gpt-4o-mini")  # model
llm.invoke("HS code for a smartphone?", config={"callbacks": [handler]})  # traced
# LangGraph: graph.invoke(input, config={"callbacks": [handler]})  # same handler works
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not flushing in serverless or scripts, so traces never show
✅ Correct: Call flush (or shutdown) before the process exits.
```python
# Wrong: script ends, background batch not sent
classify("earbuds")
# Right
classify("earbuds")
get_client().flush()
```

❌ Mistake 2: Logging raw personal data into traces
✅ Correct: Mask PII before it reaches the trace (Langfuse SDK supports masking functions; check docs).
```python
# Wrong: trace contains importer tax id
# Right: redact first
def redact(text: str) -> str:
    return text.replace("GSTIN12345", "[REDACTED]")  # simple illustration
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Langfuse dashboard shows cost per trace as $0 for a self-hosted model. Is the model free?"

**Answer**: No. Langfuse computes cost from token usage times a model price entry. If the model name is not in its price table (or no usage is reported), cost is empty or zero. Your real cost is GPU time. Define a custom model definition with your effective per-token price (GPU cost divided by tokens served) so dashboards reflect reality.

---

## ⚫ Interview Questions + Answers

Q1: What is Langfuse?
A1: An open-source LLM engineering platform for tracing, evals, prompt management and cost monitoring.

Q2: Why choose Langfuse over LangSmith?
A2: Self-hosting for data control, open-source, framework neutrality and no lock-in. LangSmith may offer tighter LangChain integration.

Q3: What is a trace vs a span?
A3: A trace is one end-to-end request; spans are the steps inside it (retrieval, LLM call, tool call).

Q4: How are scores used?
A4: Scores attach numbers or labels to traces (user thumbs, LLM-judge, human review). They drive dashboards, alerts and dataset building.

Q5: How would you roll Langfuse out for 20 services safely?
A5: Standardise a tracing wrapper library, enforce PII masking, set sampling for high-volume paths, tag by service/env/version, use separate projects per environment, load-test the self-hosted stack, and add alerts on error rate, latency and cost. Ensure tracing failures never break requests (async batching, timeouts).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data residency or compliance requires self-hosting
- Many frameworks or languages are in use
- You want open-source and prompt management

❌ Avoid when:
- You are all-in on LangChain and happy with LangSmith
- You have no capacity to operate a self-hosted stack (use the cloud plan then)

---

## 📊 Visual Diagram
```
 App code --(decorator / callback)--> Langfuse SDK (async batch)
                                            |
                                            v
                                   Langfuse server (self-host or cloud)
                                            |
              +-----------+-----------+-----+------+
              v           v           v            v
           Traces     Dashboards   Scores     Prompt versions
        (spans, tokens) (cost,latency) (evals)   + datasets
```

---

## 💰 Cost Impact
Langfuse itself adds no LLM tokens. Cloud plans bill by usage tiers (check current pricing); self-hosting costs infrastructure and ops time. It reduces your LLM bill indirectly: cost dashboards show expensive prompts, users and models.

Optimise: sample low-value traces, avoid logging huge payloads (truncate documents), set retention limits, and use the cost-per-user view to find heavy users or runaway loops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Observability | See inside your system | System के अंदर देखना |
| Trace | One full request record | पूरी request का record |
| Span | One step in a trace | Trace का एक step |
| Score | Quality rating on a trace | Trace पर quality rating |
| Self-hosting | Run it on your servers | अपने servers पर चलाना |
| Session | Group of related traces | जुड़े traces का group |
| Flush | Send pending events now | बचे events अभी भेजना |

---

## ⚡ 3-Line Summary
English: Langfuse is an open-source, self-hostable alternative to LangSmith for traces, evals and prompt management. It is framework neutral and good for data-residency needs. Mask PII and flush events before exit.
Hindi: Langfuse LangSmith का open-source, self-host होने वाला विकल्प है: traces, evals और prompt management के लिए। यह framework neutral है और data-residency ज़रूरतों के लिए अच्छा है। PII mask करो और exit से पहले events flush करो।

---

## ➡️ Next Topic
**428. Langfuse Setup** — creating keys, installing the SDK, and sending your first trace.
