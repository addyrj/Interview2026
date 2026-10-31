---

# 431. Phoenix (Arize) Tracing
# हिंदी में: Phoenix (Arize) Tracing

---

## 🔵 Simple Definition (English)
Arize Phoenix is an open-source tool for tracing and evaluating LLM apps. It runs locally (a notebook or a Docker container) and receives traces in the OpenTelemetry format using the OpenInference conventions. You instrument OpenAI, LangChain or LlamaIndex with one line, then explore traces, embeddings and evals in a web UI.

## 🔵 सरल परिभाषा (Hindi)
Arize Phoenix LLM apps को trace और evaluate करने वाला open-source tool है। यह local (notebook या Docker) चलता है और OpenTelemetry format में traces लेता है (OpenInference conventions)। OpenAI, LangChain या LlamaIndex को एक line से instrument करो और web UI में traces, embeddings और evals देखो।

---

## 🔴 Problem it Solves
- Teams want tracing without sending data to a vendor cloud and without writing manual instrumentation for every library.
- During development in a notebook you want instant visual feedback, not a deployed platform.
- Proprietary trace formats lock you in; OTel-based traces can be exported anywhere.

## 🔴 यह क्यों बना? (Hindi)
- Teams को बिना vendor cloud और बिना हर library के लिए manual instrumentation के tracing चाहिए।
- Development में notebook के अंदर तुरंत visual feedback चाहिए।
- Proprietary format lock-in करता है; OTel traces कहीं भी भेजे जा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start Phoenix server (px.launch_app() or: docker run arizephoenix/phoenix)
Step 2 → Register a tracer provider: phoenix.otel.register(project_name=..., endpoint=...)
Step 3 → Auto-instrument libraries: OpenAIInstrumentor().instrument(tracer_provider=...)
Step 4 → Your normal code runs; instrumentors wrap library calls and emit OTel spans
Step 5 → Spans carry OpenInference attributes (llm.model_name, token counts, input/output)
Step 6 → Spans are exported to Phoenix via OTLP (HTTP or gRPC)
Step 7 → UI: trace tree, latency, token counts, evals, retrieval relevance, embedding drift view
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Phoenix server चालू करो (px.launch_app() या Docker)
Step 2 → Tracer provider register करो: phoenix.otel.register(project_name=...)
Step 3 → Libraries auto-instrument करो: OpenAIInstrumentor().instrument(...)
Step 4 → आपका normal code चलता है; instrumentors library calls को wrap करके OTel spans भेजते हैं
Step 5 → Spans में OpenInference attributes होते हैं (model name, token count, input/output)
Step 6 → Spans OTLP से Phoenix को export होते हैं
Step 7 → UI में trace tree, latency, tokens, evals, retrieval relevance और embedding drift दिखते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A developer iterates on the RAG pipeline in a Jupyter notebook. Phoenix runs in the same notebook. After running 20 test products, the trace table shows retrieval spans with low relevance for "lithium battery" queries, and one LLM span with 3,800 input tokens (the whole chapter was stuffed in the prompt). The developer fixes chunking before ever deploying.

**Zomato-style**: the search-assistant team runs Phoenix in staging to spot slow tool calls (restaurant API) vs slow LLM calls.

## 🟡 Real Example Hindi mein
**Tariff System**: Developer Jupyter notebook में RAG pipeline सुधार रहा है और Phoenix उसी notebook में चल रहा है। 20 test products चलाने पर trace table दिखाती है कि "lithium battery" queries में retrieval relevance कम है और एक LLM span में 3,800 input tokens हैं (पूरा chapter prompt में डाल दिया)। Deploy से पहले ही chunking ठीक हो जाती है।

---

## 💻 Code Example — Basic
Phoenix needs an extra install, so this basic version shows the OpenInference-style span attributes using only the standard library. Run it directly.

```python
# Build OpenInference-like span dicts by hand to understand what Phoenix receives
import json                                   # to pretty print spans
import time                                   # latency measurement
from typing import Any                        # type hints

SPANS: list[dict[str, Any]] = []              # exported spans (stand-in for OTLP exporter)


def llm_span(model: str, prompt: str, fake_answer: str) -> str:
    start = time.time()                       # start timestamp
    time.sleep(0.01)                          # pretend the model is thinking
    in_tok = len(prompt.split())              # crude token count (words)
    out_tok = len(fake_answer.split())        # crude output token count
    SPANS.append({                            # record span with OpenInference attribute names
        "name": "ChatCompletion",
        "openinference.span.kind": "LLM",
        "llm.model_name": model,
        "input.value": prompt,
        "output.value": fake_answer,
        "llm.token_count.prompt": in_tok,
        "llm.token_count.completion": out_tok,
        "latency_ms": round((time.time() - start) * 1000, 1),
    })
    return fake_answer                        # return the answer like a normal call


llm_span("gpt-4o-mini", "HS code for Bluetooth speaker?", "8518.22")   # one call
print(json.dumps(SPANS, indent=2, ensure_ascii=False))                 # show captured data
```

## 💻 Code Example — Advanced
Real Phoenix setup (`pip install arize-phoenix-otel openinference-instrumentation-openai openai`). Start the server first: `python -m phoenix.server.main serve` (UI at http://localhost:6006).

```python
# Production-style Phoenix tracing with OpenAI auto-instrumentation + custom spans
import asyncio                                                    # async demo
import os                                                         # env config
from typing import Any                                            # type hints

from phoenix.otel import register                                 # Phoenix OTel helper
from openinference.instrumentation.openai import OpenAIInstrumentor  # OpenAI auto-instrumentation
from openai import AsyncOpenAI                                    # async client
from opentelemetry import trace                                   # OTel API for custom spans
from opentelemetry.trace import Status, StatusCode                # to mark errors

tracer_provider = register(                                       # configure exporter + provider
    project_name="tariff-classifier",                             # groups traces in UI
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)  # every OpenAI call is now traced

tracer = trace.get_tracer("tariff")                               # tracer for manual spans
client = AsyncOpenAI()                                            # normal client, no wrapper needed


async def classify(product: str) -> str:
    with tracer.start_as_current_span("classify_product") as span:   # parent span (root)
        span.set_attribute("openinference.span.kind", "CHAIN")       # type for Phoenix UI
        span.set_attribute("input.value", product)                   # record input
        try:
            resp = await client.chat.completions.create(             # auto-traced child span
                model="gpt-4o-mini", temperature=0, max_tokens=40,
                messages=[{"role": "user", "content": f"HS code for: {product}. Code only."}],
            )
            answer = resp.choices[0].message.content or ""          # may be None
            span.set_attribute("output.value", answer)               # record output
            return answer
        except Exception as exc:                                     # mark failure in trace
            span.record_exception(exc)                               # attach stack trace
            span.set_status(Status(StatusCode.ERROR, str(exc)))      # red span in UI
            raise


if __name__ == "__main__":
    print(asyncio.run(classify("Bluetooth speaker")))                # run once
```

---

## 🟠 FastAPI Integration
Instrument once at startup (module import), not per request. Optionally use `opentelemetry-instrumentation-fastapi` so the HTTP request becomes the root span.

```python
# FastAPI + Phoenix: HTTP span is the parent of the LLM span
from fastapi import FastAPI, HTTPException                         # framework
from pydantic import BaseModel                                     # validation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # HTTP spans

from tariff_phoenix import classify                                # function from advanced example

app = FastAPI()                                                    # app
FastAPIInstrumentor.instrument_app(app)                            # each request -> root span


class Req(BaseModel):                                              # input model
    product: str


@app.post("/classify")                                             # route
async def route(req: Req) -> dict[str, str]:
    try:
        return {"hs_code": await classify(req.product)}           # LLM span nests under HTTP span
    except Exception as exc:                                       # map to 502
        raise HTTPException(status_code=502, detail="upstream error") from exc
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has its own instrumentor, which also covers LangGraph because it builds on LangChain runnables.

```python
# Trace a LangChain / LangGraph app in Phoenix
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

provider = register(project_name="tariff-langchain")        # tracer provider
LangChainInstrumentor().instrument(tracer_provider=provider)  # all chains/graphs traced globally

chain = ChatPromptTemplate.from_template("HS code for {p}") | ChatOpenAI(model="gpt-4o-mini")
print(chain.invoke({"p": "Bluetooth speaker"}).content)      # no callbacks needed
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Instrumenting after the client was imported/used in a way that bypasses it, or instrumenting per request
✅ Correct: instrument once at process start, before first use.

```python
# Wrong: inside the handler, creates duplicate spans each request
@app.post("/x")
async def x():
    OpenAIInstrumentor().instrument()

# Right: at module import
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

❌ Mistake 2: Leaving the local Phoenix open to the internet in production
✅ Correct: put it behind auth/VPN, or use a managed/authenticated deployment; set an API key header.

```python
# Wrong: collector endpoint public, anybody can read prompts (PII)
# Right: private network + auth
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.environ['PHOENIX_API_KEY']}"
```

---

## 🧠 Tricky Interview Question
**Q**: "You use Phoenix and also Datadog. Do you need two instrumentations?"

**Answer**: No. Both consume OpenTelemetry. Phoenix uses OpenInference semantic attributes (LLM-specific) on top of OTel. You can configure two span processors/exporters on the same tracer provider, sending the same spans to Phoenix (LLM-aware view) and to an OTel collector that forwards to Datadog (infrastructure view). Watch out for payload size and PII in prompt attributes going to the general APM.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is Phoenix?
A1: An open-source LLM observability and evaluation tool from Arize that accepts OpenTelemetry traces and shows them in a local UI.

Q2 (Easy): What is OpenInference?
A2: A set of semantic conventions and instrumentors that define LLM-specific span attributes (model name, token counts, retrieved documents) on top of OTel.

Q3 (Medium): Phoenix vs Langfuse?
A3: Phoenix is OTel-native, strong in notebooks, retrieval and embedding analysis. Langfuse has a richer production platform: prompt management, datasets, users/sessions, cost dashboards, and a hosted cloud. Many teams use Phoenix in dev and Langfuse in prod, or either with OTel.

Q4 (Medium): How do you add a custom span for a non-LLM step like HS code validation?
A4: Use `tracer.start_as_current_span("validate")`, set `openinference.span.kind` (e.g. TOOL or CHAIN), attach input/output attributes, and record exceptions.

Q5 (Hard): Spans from a Celery worker do not connect to the API request trace. Why?
A5: Context propagation is missing. Trace context lives in contextvars and does not cross process boundaries. Inject the W3C `traceparent` header into the task message with `propagate.inject` and extract it in the worker (`propagate.extract`) before starting spans.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Developing RAG in notebooks and inspecting retrieval quality
- You want vendor-neutral OTel traces and local/self-hosted data
- You use many frameworks (OpenAI, LangChain, LlamaIndex) and want auto-instrumentation

❌ Avoid when:
- You need built-in prompt management and user feedback workflow out of the box (Langfuse fits better)
- You cannot secure the Phoenix server and prompts contain PII

---

## 📊 Visual Diagram
```
 App code ──> Instrumentors (OpenAI / LangChain)
                 │  OTel spans + OpenInference attributes
                 ▼
          TracerProvider ──OTLP──> Phoenix collector ──> UI
                 │                                        ├─ trace tree
                 └──(optional)──> OTel Collector ──> APM  ├─ evals
                                                          └─ embeddings view
```

---

## 💰 Cost Impact
- Phoenix is free and self-hosted; you pay only for infrastructure. Tracing adds no LLM tokens.
- It exposes `llm.token_count.prompt` and `completion`, so you can spot a 3,800-token prompt and cut it. Trimming input from 3,800 to 900 tokens on gpt-4o-mini saves roughly $0.00044 per call, which is $440 per million calls.
- Reduce telemetry cost: sample traces, truncate long `input.value` payloads, and set retention.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Phoenix | Arize open-source LLM observability | Arize का open-source tool |
| OpenTelemetry | Vendor-neutral telemetry standard | Telemetry का standard |
| OpenInference | LLM attribute conventions for OTel | LLM के लिए OTel attributes |
| Instrumentor | Auto-wraps a library to emit spans | Library को auto-trace करने वाला |
| OTLP | Protocol to export spans | Spans भेजने का protocol |
| Span kind | LLM, CHAIN, TOOL, RETRIEVER | Span का प्रकार |
| Project | Group of traces in UI | Traces का group |

---

## ⚡ 3-Line Summary
English: Phoenix is an OTel-native, open-source tracing and eval tool. Register a tracer provider, call the instrumentor once, and every OpenAI or LangChain call is traced. Great for notebooks and retrieval debugging; secure it in production.
Hindi: Phoenix OTel-native open-source tracing और eval tool है। Tracer provider register करो, instrumentor एक बार call करो, और हर OpenAI/LangChain call trace हो जाती है। Notebook और retrieval debugging के लिए बढ़िया; production में सुरक्षित रखो।

---

## ➡️ Next Topic
**432. OpenTelemetry for AI Apps** — the standard underneath Phoenix; learn traces, metrics, logs and context propagation directly.
