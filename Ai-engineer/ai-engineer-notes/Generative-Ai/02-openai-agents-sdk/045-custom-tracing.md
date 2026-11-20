---

# 45. Custom Tracing
# हिंदी में: Custom Tracing (अपना processor, अपने spans)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline (processor, custom span, BatchTraceProcessor with a JSONL exporter, `flush_traces`). Sending spans to a real third-party backend (Langfuse, Datadog, OTLP collector) was NOT run - it needs that service.

---

## 🔵 Simple Definition (2-3 lines)
Custom tracing means two things: (1) adding your own spans with `custom_span(...)` / `function_span(...)` / `trace(...)` around non-agent work, and (2) writing a `TracingProcessor` (or a `TracingExporter` used by `BatchTraceProcessor`) to send traces to your own store.

## 🔵 सरल परिभाषा (Hindi)
Custom tracing के दो हिस्से हैं: (1) agent के बाहर के काम के चारों ओर अपने spans (`custom_span`, `function_span`, `trace`) लगाना, और (2) अपना `TracingProcessor` (या `BatchTraceProcessor` वाला `TracingExporter`) लिखना ताकि traces आपके अपने store में जाएँ।

---

## 🔴 Problem it Solves
The default exporter sends data to one vendor and only knows about agent steps. Real systems also run retrieval, database calls and business rules, and teams need traces in their existing stack (Datadog, Langfuse, ELK, a Postgres table) with PII removed. Custom tracing fills those gaps without changing agent code.

## 🔴 यह क्यों बना? (Hindi)
Default exporter डेटा एक vendor को भेजता है और सिर्फ़ agent के steps जानता है। असली system में retrieval, database calls और business rules भी चलते हैं, और teams को अपने मौजूदा stack (Datadog, Langfuse, ELK, Postgres table) में, PII हटाकर, traces चाहिए। Custom tracing बिना agent code बदले यह कमी भरता है।

---

## 🟢 How it Works

```
Step 1 -> Subclass TracingProcessor (5 methods):
          on_trace_start / on_trace_end / on_span_start / on_span_end
          / shutdown / force_flush
Step 2 -> Register it:
          add_trace_processor(p)   -> keep default exporter + yours
          set_trace_processors([p])-> replace everything
Step 3 -> Wrap your own work: with custom_span("name", {data}):
Step 4 -> For production, do NOT do I/O in on_span_end.
          Use BatchTraceProcessor(exporter) -> background thread
Step 5 -> exporter.export(items): scrub PII, serialise item.export()
Step 6 -> flush_traces() / processor.shutdown() on exit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> TracingProcessor की subclass बनाओ:
          on_trace_start / on_trace_end / on_span_start / on_span_end
          / shutdown / force_flush
Step 2 -> Register करो:
          add_trace_processor(p)   -> default exporter + आपका
          set_trace_processors([p])-> सब बदल देता है
Step 3 -> अपना काम लपेटो: with custom_span("name", {data}):
Step 4 -> Production में on_span_end में I/O मत करो।
          BatchTraceProcessor(exporter) -> background thread
Step 5 -> exporter.export(items): PII हटाओ, item.export() serialise करो
Step 6 -> बंद होते समय flush_traces() / processor.shutdown()
```

**Names verified in 0.24.0:** `TracingProcessor`, `add_trace_processor`, `set_trace_processors`, `custom_span`, `function_span`, `trace`, `flush_traces`, and in `agents.tracing.processors`: `BatchTraceProcessor`, `BackendSpanExporter`, `ConsoleSpanExporter`, `TracingExporter`. `BatchTraceProcessor(exporter, max_queue_size=8192, max_batch_size=128, schedule_delay=5.0, export_trigger_ratio=0.7)`.

**What an exported item looks like:** `item.export()` returns a dict with `object` ('trace' or 'trace.span'), ids, `span_data` (type plus fields). We use it to write JSON lines. Do not rely on the exact field set across SDK versions - treat it as semi-stable and test after upgrades.

**Span helpers:** `custom_span(name, data)` for any step; `function_span(name, input, output)` if you want a tool-like span for non-tool code; spans created inside a trace/agent run attach to the current parent automatically via context variables.

**Hindi नोट:** Third-party integrations (Langfuse, Logfire आदि) इसी `TracingProcessor` interface पर बने हैं। इसलिए अपना processor समझना interview में सबसे काम की चीज़ है। हमेशा `BatchTraceProcessor` से export करें ताकि request path में network call न हो।

---

## 🟡 Real World Example
**Tariff Agent platform.** Compliance requires that every HS-code decision be stored for 7 years with the user id, but customer invoice text must be redacted. You add a `BatchTraceProcessor` with an exporter that writes redacted JSON lines to object storage, and a `custom_span('load_hs_codes')` so slow CSV loads are visible. The default OpenAI exporter is kept for engineering debugging only (`add_trace_processor`).

**Customer Support Agent:** export spans to Datadog with ticket id as a tag.

## 🟡 Real Example Hindi mein
**Tariff Agent platform.** Compliance चाहता है कि हर HS-code निर्णय user id के साथ 7 साल रखा जाए, पर customer invoice text redact हो। आप `BatchTraceProcessor` वाला exporter लगाते हैं जो redacted JSON lines object storage में लिखता है, और `custom_span('load_hs_codes')` जोड़ते हैं ताकि धीमा CSV load दिखे। Default OpenAI exporter सिर्फ़ engineering debugging के लिए `add_trace_processor` से रखा जाता है।

**Customer Support Agent:** spans को Datadog में ticket id tag के साथ भेजो।

---

## 💻 Code Example — Basic
Runs offline. Collects spans into a list and prints them, including a custom span with your own data. Real elapsed time is measured, not invented.

```python
# Basic: write your own TracingProcessor + custom span, send spans to a list (offline)
import asyncio                                           # async runner
import time                                              # measure duration
from typing import Any                                   # type hints
from agents import (Agent, Runner, TracingProcessor, Span, Trace, custom_span,
                    set_trace_processors, trace)         # tracing building blocks
from agents.testing import ScriptedModel, assistant_message  # fake LLM

class ListProcessor(TracingProcessor):                   # your "exporter": could be Kafka, DB, OTEL...
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []             # collected span rows
    def on_trace_start(self, t: Trace) -> None: pass
    def on_trace_end(self, t: Trace) -> None: pass
    def on_span_start(self, span: Span[Any]) -> None: pass
    def on_span_end(self, span: Span[Any]) -> None:      # called once per finished span
        self.rows.append({
            "type": type(span.span_data).__name__,       # e.g. CustomSpanData, AgentSpanData
            "name": getattr(span.span_data, "name", None),
            "data": getattr(span.span_data, "data", None),  # only custom spans carry .data
            "trace_id": span.trace_id,                   # join key across spans
            "parent": span.parent_id,                    # builds the tree
        })
    def shutdown(self) -> None: pass
    def force_flush(self) -> None: pass

async def main() -> None:
    proc = ListProcessor()
    set_trace_processors([proc])                         # REPLACES default exporter; add_trace_processor() would ADD
    agent = Agent(name="Tariff Agent", instructions="x",
                  model=ScriptedModel([[assistant_message("Duty 20%")]]))
    with trace("tariff-batch"):                          # parent trace
        t0 = time.perf_counter()                         # start timer
        with custom_span("load_hs_codes", {"source": "local-csv"}):  # your own step in the tree
            codes = ["6109.10", "6203.42"]               # pretend we loaded these
        await Runner.run(agent, f"Duty for {codes[0]}?")
        print("elapsed_ms ~", round((time.perf_counter() - t0) * 1000, 1))  # real measured value, not invented
    for row in proc.rows:                                # inspect what we captured
        print(row["type"], row["name"], row["data"])

asyncio.run(main())
```

## 💻 Code Example — Advanced
FastAPI lifespan installs a `BatchTraceProcessor` with a JSONL exporter that redacts `input`/`output`, flushes on shutdown, and `flush_traces()` for short-lived runs. Offline; writes to a temp file.

```python
# Advanced: batch exporter -> JSON lines, PII scrubbing, FastAPI lifespan flush (offline, writes to a temp file)
import json                                              # serialise spans
import tempfile                                          # demo output location
from contextlib import asynccontextmanager               # FastAPI lifespan
from pathlib import Path                                 # file handling
from typing import Any                                   # type hints
from fastapi import FastAPI                              # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schema
from agents import Agent, Runner, flush_traces, set_trace_processors   # SDK
from agents.tracing.processors import BatchTraceProcessor, TracingExporter  # batching helpers
from agents.testing import ScriptedModel, assistant_message            # fake LLM

OUT = Path(tempfile.mkdtemp()) / "spans.jsonl"           # demo file; use object storage / OTLP in prod

class JsonlExporter(TracingExporter):                    # BatchTraceProcessor calls export() with batches
    def export(self, items: list[Any]) -> None:
        with OUT.open("a") as f:
            for it in items:
                d = it.export()                          # dict the SDK would send to its backend
                if not d:
                    continue
                d = json.loads(json.dumps(d))            # deep copy
                span_data = d.get("span_data") or {}
                for key in ("input", "output"):          # scrub payloads before they leave the process
                    if key in span_data:
                        span_data[key] = "[redacted]"
                f.write(json.dumps(d) + "\n")

@asynccontextmanager
async def lifespan(app: FastAPI):                        # startup/shutdown hook
    proc = BatchTraceProcessor(JsonlExporter(), max_batch_size=64, schedule_delay=1.0)  # batch + background thread
    set_trace_processors([proc])                         # install once per process
    yield                                                # app serves requests here
    proc.shutdown()                                      # flush the queue on shutdown (no lost spans)

app = FastAPI(lifespan=lifespan)

class AskIn(BaseModel):
    question: str

@app.post("/ask")
async def ask(body: AskIn) -> dict[str, str]:
    agent = Agent(name="Tariff Agent", instructions="x", model=ScriptedModel([[assistant_message("Duty 20%")]]))
    r = await Runner.run(agent, body.question)
    return {"answer": str(r.final_output)}

if __name__ == "__main__":
    with TestClient(app) as c:                           # `with` triggers lifespan startup/shutdown
        print(c.post("/ask", json={"question": "Duty?"}).json())
        flush_traces()                                   # force export now (tests, short scripts, serverless)
    lines = OUT.read_text().splitlines()
    print(len(lines), "records;", sorted({json.loads(l).get("object") for l in lines}))
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Custom exporter API | Callback handlers / LangSmith client | Event listeners / telemetry hooks | `TracingProcessor` + `BatchTraceProcessor` | OTel tracer provider / event logger |
| Add own span | `@traceable` / callbacks | manual logging | `custom_span(...)` | OTel spans / logging |
| Keep default + add yours | n/a | n/a | `add_trace_processor` (replace: `set_trace_processors`) | n/a |
| Batching built in | LangSmith client batches | depends on integration | `BatchTraceProcessor` | OTel BatchSpanProcessor |
| Ecosystem integrations | LangSmith, many | AgentOps, Langfuse etc. | Langfuse, Logfire, others via processor | OTel-compatible backends |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Doing HTTP/DB writes directly inside `on_span_end`.
✅ Correct: Queue and export in a background `BatchTraceProcessor`; keep callbacks O(1).

❌ Mistake 2: Using `set_trace_processors` and silently losing the default dashboard.
✅ Correct: Use `add_trace_processor` when you want both.

❌ Mistake 3: Forgetting to flush in scripts/serverless, so the last spans vanish.
✅ Correct: Call `flush_traces()` or `processor.shutdown()` before exit.

❌ Mistake 4: Assuming `span.span_data.data` exists on every span.
✅ Correct: Only custom spans carry `.data`; use `getattr(..., None)` or `span.export()`.

---

## 🧠 Tricky Interview Question
You add a custom processor and a teammate says traces for requests under load are missing the final spans. Where do you look?

**Answer:** Missing tail spans usually mean unflushed batches or a full queue. Check: (1) is `shutdown()`/`flush_traces()` called on process exit or by the serverless runtime before freeze, (2) `max_queue_size` too small so items are dropped under burst, (3) `schedule_delay` large and the worker killed before it fires, (4) your exporter raising an exception that drops the batch (wrap in try/except and log), (5) multiple workers each with their own queue (gunicorn forks) - install the processor per worker after the fork, in lifespan, not at import time. Add a counter for dropped/failed exports so the problem is visible instead of silent.

---

## ⚫ Interview Questions + Answers

**Q1:** How do you add your own span?

**A1:** `with custom_span('name', {'k': 'v'}):` inside an active trace or agent run; it nests under the current parent automatically.

**Q2:** `add_trace_processor` vs `set_trace_processors`?

**A2:** Add appends to the default processors; set replaces the whole list (default exporter removed).

**Q3:** Why use BatchTraceProcessor instead of writing in on_span_end?

**A3:** It batches and exports in a background thread, keeping network/disk I/O out of the request path.

**Q4:** How would you redact PII before export?

**A4:** Scrub in the exporter or processor (drop `input`/`output` fields, regex fields), and disable sensitive data capture with RunConfig for the whole run.

**Q5:** Design trace export for 50 tenants with different retention rules.

**A5:** Tag traces with tenant in metadata, route in the exporter by tenant to separate buckets/tables with per-tenant retention, redact per tenant policy, encrypt at rest, sample low-tier tenants, and run an export-failure counter plus replay queue so compliance data is never lost.

---

## 💰 Cost Impact
No LLM tokens. Costs: exporter CPU, network egress, storage. Rough formula: storage ~ spans_per_run x bytes_per_span x runs. Full prompts/tool results dominate bytes, so redacting or truncating them is the biggest saving. Sample (for example keep 100% of errors and 5% of successes) for high-volume tenants. Any bytes-per-span figure must be measured from your own exports (we did not measure one here).

---

## 🔷 When to Use
✅ Use when:
- Existing observability stack must receive agent traces
- PII/retention rules require control over what is stored
- You need spans for non-agent code (retrieval, DB, business rules)
- Multi-region or multi-tenant routing of trace data

❌ Avoid when:
- Prototype scripts where default tracing is enough
- Writing synchronous exporters in the hot path
- Storing raw prompts with PII just because it is easy

---

## 📊 Visual Diagram
```
  agent run / your code
        |
        |  custom_span("load_hs_codes")   <- your steps
        v
  SDK span events
        |
        v
 +-----------------------+   add_trace_processor      +------------------+
 | TracingProcessor #1   |--------------------------->| default exporter |
 | (BatchTraceProcessor) |                            +------------------+
 +-----------------------+
        | queue (max_queue_size)
        v  background thread, batch of max_batch_size
 +-----------------------+
 | TracingExporter       |  scrub PII -> item.export() -> JSONL / OTLP / DB
 +-----------------------+
        |
   flush_traces() / shutdown()  (on exit)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TracingProcessor | Interface receiving trace/span events | trace/span events का interface |
| BatchTraceProcessor | Queues and exports in background | background में batch export |
| TracingExporter | Class with export(items) | export(items) वाली class |
| custom_span | Your own span with data | अपना span, अपने data के साथ |
| flush_traces | Force export now | अभी export करवाओ |
| Redaction | Removing sensitive fields | संवेदनशील fields हटाना |

---

## ⚡ 3-Line Summary
English: Add your own spans with `custom_span` and your own sink with a `TracingProcessor`.
Use `BatchTraceProcessor` plus an exporter so I/O stays off the request path, and flush on shutdown.
Redact PII in the exporter and choose add vs set processors deliberately.

Hindi: `custom_span` से अपने spans और `TracingProcessor` से अपना sink जोड़ें।
I/O को request path से बाहर रखने के लिए `BatchTraceProcessor` + exporter लें और बंद होते समय flush करें।
Exporter में PII हटाएँ और add बनाम set processors सोच-समझकर चुनें।

---

## ➡️ Next Topic
**#46 Context Object** - tracing showed what happened inside a run; next we see how to pass your own data (user, DB handle, settings) into every tool and guardrail via the run context.

---
