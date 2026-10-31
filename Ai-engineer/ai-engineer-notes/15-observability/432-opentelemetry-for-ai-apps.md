---

# 432. OpenTelemetry for AI Apps
# हिंदी में: AI Apps के लिए OpenTelemetry

---

## 🔵 Simple Definition (English)
OpenTelemetry (OTel) is a vendor-neutral standard and SDK for producing **traces, metrics and logs**. For AI apps you wrap LLM calls, retrieval and tools in spans, record token and latency metrics, and export everything to any backend (Jaeger, Grafana, Datadog, Phoenix, Langfuse) using the OTLP protocol.

## 🔵 सरल परिभाषा (Hindi)
OpenTelemetry (OTel) **traces, metrics और logs** बनाने का vendor-neutral standard और SDK है। AI apps में LLM calls, retrieval और tools को spans में wrap करते हैं, tokens और latency के metrics रखते हैं, और OTLP protocol से किसी भी backend (Jaeger, Grafana, Datadog, Phoenix) को भेजते हैं।

---

## 🔴 Problem it Solves
- Every observability vendor had its own SDK; switching meant rewriting instrumentation.
- AI apps are part of a bigger system (API gateway, DB, vector store, queue). You need ONE trace that crosses all of them, not an LLM-only island.
- Teams need LLM-specific attributes (model, tokens) in the same standard format as HTTP and DB spans.

## 🔴 यह क्यों बना? (Hindi)
- हर vendor का अपना SDK था, बदलने पर instrumentation दोबारा लिखना पड़ता था।
- AI app बड़े system का हिस्सा है (gateway, DB, vector store, queue)। एक ही trace चाहिए जो सबको पार करे।
- LLM attributes (model, tokens) उसी standard format में चाहिए जिसमें HTTP और DB spans हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Resource (service.name="tariff-api", version, environment)
Step 2 → Create TracerProvider + SpanProcessor (Batch) + Exporter (OTLP)
Step 3 → Code calls tracer.start_as_current_span("name") -> span with start/end time
Step 4 → Add attributes: gen_ai.request.model, gen_ai.usage.input_tokens, ...
Step 5 → Context propagation: trace_id/span_id travel in the traceparent HTTP header
Step 6 → Metrics: counters and histograms (tokens, latency, errors) via MeterProvider
Step 7 → Exporter ships data to an OTel Collector -> backend(s) of your choice
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Resource बनाओ (service.name="tariff-api", version, environment)
Step 2 → TracerProvider + BatchSpanProcessor + OTLP Exporter बनाओ
Step 3 → Code में tracer.start_as_current_span("name") से span बनता है
Step 4 → Attributes जोड़ो: gen_ai.request.model, gen_ai.usage.input_tokens आदि
Step 5 → Context propagation: trace_id/span_id traceparent header में चलते हैं
Step 6 → Metrics: counter और histogram (tokens, latency, errors) MeterProvider से
Step 7 → Exporter data को OTel Collector के ज़रिए पसंद के backend को भेजता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Request path is Gateway -> FastAPI -> Redis cache -> Qdrant -> OpenAI. With OTel, one trace shows: gateway 5 ms, Redis miss 2 ms, Qdrant 180 ms, OpenAI 900 ms. A spike in p95 is traced to Qdrant, not to the LLM, which an LLM-only tool would not show.

**Amazon-style**: a "product Q&A" service exports a histogram `llm.latency` by model, and an SRE alert fires when p95 > 3 s.

## 🟡 Real Example Hindi mein
**Tariff System**: Request path: Gateway -> FastAPI -> Redis cache -> Qdrant -> OpenAI। OTel से एक trace में दिखता है: gateway 5 ms, Redis miss 2 ms, Qdrant 180 ms, OpenAI 900 ms। p95 spike Qdrant से आया, LLM से नहीं, यह LLM-only tool नहीं दिखाता।

---

## 💻 Code Example — Basic
Uses only the OTel SDK with a console exporter (`pip install opentelemetry-sdk`). Prints spans to the terminal.

```python
# Minimal OpenTelemetry tracing with console output
from opentelemetry import trace                                        # API to get a tracer
from opentelemetry.sdk.resources import Resource                       # describes this service
from opentelemetry.sdk.trace import TracerProvider                     # SDK provider
from opentelemetry.sdk.trace.export import (                           # exporters/processors
    ConsoleSpanExporter, SimpleSpanProcessor,
)

resource = Resource.create({"service.name": "tariff-api"})             # service identity
provider = TracerProvider(resource=resource)                           # create provider
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))  # print each span at once
trace.set_tracer_provider(provider)                                    # register globally
tracer = trace.get_tracer("tariff.demo")                               # tracer for this module


def fake_llm(prompt: str) -> str:                                      # pretend LLM
    with tracer.start_as_current_span("llm.call") as span:             # child span
        span.set_attribute("gen_ai.request.model", "gpt-4o-mini")      # model attribute
        span.set_attribute("gen_ai.usage.input_tokens", len(prompt.split()))  # crude tokens
        return "8518.22"                                               # fixed answer


with tracer.start_as_current_span("classify_request"):                 # root span
    print(fake_llm("HS code for Bluetooth speaker"))                   # nested call
```

## 💻 Code Example — Advanced
Traces + metrics, OTLP export, error handling, async (`pip install opentelemetry-sdk opentelemetry-exporter-otlp openai`).

```python
# Production OTel setup for an AI service: OTLP traces + token/latency metrics
import asyncio                                                         # async demo
import time                                                            # latency
from typing import Any                                                 # type hints

from opentelemetry import trace, metrics                               # APIs
from opentelemetry.sdk.resources import Resource                       # resource
from opentelemetry.sdk.trace import TracerProvider                     # tracing SDK
from opentelemetry.sdk.trace.export import BatchSpanProcessor          # async batching
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider                    # metrics SDK
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.trace import Status, StatusCode                     # error status
from openai import AsyncOpenAI                                         # LLM client

res = Resource.create({"service.name": "tariff-api", "deployment.environment": "prod"})

tp = TracerProvider(resource=res)                                      # tracer provider
tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))          # default http://localhost:4318
trace.set_tracer_provider(tp)                                          # global

reader = PeriodicExportingMetricReader(OTLPMetricExporter(), export_interval_millis=15_000)
metrics.set_meter_provider(MeterProvider(resource=res, metric_readers=[reader]))

tracer = trace.get_tracer("tariff")                                    # tracer
meter = metrics.get_meter("tariff")                                    # meter
token_counter = meter.create_counter("llm.tokens", unit="token")       # total tokens
latency_hist = meter.create_histogram("llm.latency", unit="ms")        # latency distribution
error_counter = meter.create_counter("llm.errors")                     # error count

client = AsyncOpenAI()                                                 # OpenAI client


async def classify(product: str, model: str = "gpt-4o-mini") -> str:
    start = time.perf_counter()                                        # timer
    attrs: dict[str, Any] = {"gen_ai.request.model": model}            # metric labels (low cardinality!)
    with tracer.start_as_current_span("llm.classify") as span:         # span
        span.set_attribute("gen_ai.request.model", model)
        try:
            r = await client.chat.completions.create(
                model=model, temperature=0, max_tokens=40,
                messages=[{"role": "user", "content": f"HS code for {product}"}],
            )
            u = r.usage                                                # token usage (may be None)
            if u:
                span.set_attribute("gen_ai.usage.input_tokens", u.prompt_tokens)
                span.set_attribute("gen_ai.usage.output_tokens", u.completion_tokens)
                token_counter.add(u.total_tokens, attrs)               # metric
            return r.choices[0].message.content or ""
        except Exception as exc:
            span.record_exception(exc)                                 # stack trace on span
            span.set_status(Status(StatusCode.ERROR))                  # mark failed
            error_counter.add(1, {**attrs, "error.type": type(exc).__name__})
            raise
        finally:
            latency_hist.record((time.perf_counter() - start) * 1000, attrs)


if __name__ == "__main__":
    print(asyncio.run(classify("Bluetooth speaker")))
    tp.shutdown()                                                      # flush spans
```

---

## 🟠 FastAPI Integration
`FastAPIInstrumentor` creates the root span and extracts incoming `traceparent`, so the trace continues from the caller.

```python
# FastAPI auto-instrumentation + custom child span
from fastapi import FastAPI                                            # framework
from pydantic import BaseModel                                         # validation
from opentelemetry import trace                                        # API
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # pip install opentelemetry-instrumentation-fastapi
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # outgoing calls (OpenAI uses httpx)

app = FastAPI()                                                        # app
FastAPIInstrumentor.instrument_app(app)                                # HTTP server spans
HTTPXClientInstrumentor().instrument()                                 # HTTP client spans (propagates traceparent)
tracer = trace.get_tracer("tariff.api")                                # tracer


class Req(BaseModel):
    product: str


@app.post("/classify")
async def classify_route(req: Req) -> dict[str, str]:
    with tracer.start_as_current_span("business.validate"):            # custom span under request span
        if not req.product.strip():
            return {"hs_code": ""}
    return {"hs_code": "8518.22"}                                      # replace with real call
```

---

## 🔗 LangChain / LangGraph Connection
LangChain emits to OTel through OpenInference or OpenLLMetry instrumentors; the spans then flow through your normal provider.

```python
# LangChain -> OTel spans (uses the global TracerProvider configured above)
from openinference.instrumentation.langchain import LangChainInstrumentor
from langchain_openai import ChatOpenAI

LangChainInstrumentor().instrument()                  # picks up global tracer provider
llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("HS code for speaker").content)      # chain + LLM spans appear in your backend
# LangGraph nodes are runnables too, so each node becomes a span automatically.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: High-cardinality metric labels
✅ Correct: put user_id and prompt text on spans, not on metrics.

```python
# Wrong: a new time series per user -> metrics backend explodes
latency_hist.record(ms, {"user_id": user_id})
# Right: low-cardinality labels only
latency_hist.record(ms, {"gen_ai.request.model": model})
```

❌ Mistake 2: SimpleSpanProcessor in production
✅ Correct: BatchSpanProcessor so export does not block requests.

```python
# Wrong: exports synchronously on every span end
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
# Right
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
```

---

## 🧠 Tricky Interview Question
**Q**: "Your trace for a chat request breaks into two separate traces when the API calls a background worker. How do you keep one trace?"

**Answer**: Context is stored in `contextvars` and does not cross network or process boundaries. Serialize it with `propagate.inject(carrier)` (adds `traceparent`) into the HTTP header or queue message, then in the worker call `propagate.extract(carrier)` and start spans with that context. For `asyncio.create_task` inside one process, contextvars are copied automatically, so no extra work is needed.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What are the three OTel signals?
A1: Traces (request flow), metrics (numeric aggregates over time), logs (event records). They can be correlated by trace_id.

Q2 (Easy): What is OTLP?
A2: OpenTelemetry Protocol, the standard wire format (HTTP or gRPC) for sending telemetry to a collector or backend.

Q3 (Medium): Why use an OTel Collector?
A3: It decouples apps from backends: apps send OTLP to the collector, which batches, filters PII, samples, and fans out to multiple vendors. Changing vendor needs only a collector config change.

Q4 (Medium): What are GenAI semantic conventions?
A4: Standard attribute names such as `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`. They make LLM spans portable across tools. (They are still evolving, so pin versions.)

Q5 (Hard): How would you sample traces for an LLM app where errors and slow requests matter most?
A5: Head sampling decides at the start, so it cannot know the outcome. Use tail sampling in the Collector: keep 100% of traces with errors or latency above threshold, and 5-10% of the rest. Cost: the collector must buffer spans until the trace completes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already run OTel for microservices and want LLM calls inside the same trace
- You want freedom to change backend vendors
- You need metrics + traces + logs correlated

❌ Avoid when:
- A small prototype where one LLM-specific tool (Langfuse) with zero config is faster
- Team has no capacity to operate a collector and backend

---

## 📊 Visual Diagram
```
 Client ──traceparent──> FastAPI ──> Redis ──> Qdrant ──> OpenAI
                            │          │         │          │
                            └────── spans (same trace_id) ──┘
                                        │ OTLP
                                        ▼
                               OTel Collector (batch, sample, redact)
                              ┌─────────┼───────────┐
                              ▼         ▼           ▼
                           Jaeger    Grafana     Phoenix/Datadog
```

---

## 💰 Cost Impact
- OTel SDK is free; cost is the backend (storage per span/GB) and collector compute.
- It adds no LLM tokens, but it records them: with the `llm.tokens` counter and model label you can compute spend per model.
- Optimise: tail-sample, drop large prompt attributes (or hash them), keep metrics low-cardinality, and set retention (for example 7 days for traces, 90 for metrics).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Span | One timed operation | एक timed operation |
| Trace | Tree of spans for one request | एक request के spans का tree |
| Metric | Aggregated number over time | समय के साथ aggregated number |
| OTLP | OTel export protocol | Export protocol |
| Collector | Proxy that processes telemetry | Telemetry process करने वाला proxy |
| Propagation | Passing trace context between services | Services के बीच trace context भेजना |
| Cardinality | Number of unique label values | Label की unique values की संख्या |

---

## ⚡ 3-Line Summary
English: OpenTelemetry is the vendor-neutral standard for traces, metrics and logs. For AI apps, add spans with GenAI attributes, token and latency metrics, and propagate context across services. Use the Collector for sampling, redaction and vendor choice.
Hindi: OpenTelemetry traces, metrics और logs का vendor-neutral standard है। AI apps में GenAI attributes वाले spans, token और latency metrics लगाओ और services के बीच context propagate करो। Sampling, redaction और vendor चुनने के लिए Collector use करो।

---

## ➡️ Next Topic
**433. AI Observability Metrics** — which numbers to actually measure (latency, tokens, cost, quality, errors) and how to define SLOs.
