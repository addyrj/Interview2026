---

# 44. Tracing in SDK
# हिंदी में: SDK में Tracing (हर agent run का record)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Span types and RunConfig fields were checked in the installed package; both code samples were run offline. Exporting to the OpenAI traces dashboard was NOT run - it needs a real OPENAI_API_KEY (without one the SDK logs 'OPENAI_API_KEY is not set, skipping trace export').

---

## 🔵 Simple Definition (2-3 lines)
Tracing is built into the Agents SDK and on by default. Every `Runner.run` becomes a **trace** (one workflow) made of **spans** (timed steps: agent, LLM generation, function tool, guardrail, handoff, MCP list-tools, custom). You get a full tree of what the agent did without writing logging code.

## 🔵 सरल परिभाषा (Hindi)
Tracing Agents SDK में built-in है और default रूप से चालू रहती है। हर `Runner.run` एक **trace** (एक workflow) बनता है जिसमें कई **spans** (समय नापे गए steps: agent, LLM generation, function tool, guardrail, handoff, MCP list-tools, custom) होते हैं। बिना logging code लिखे आपको पूरा tree मिल जाता है कि agent ने क्या किया।

---

## 🔴 Problem it Solves
An agent run is non-deterministic: the model picks tools, retries, hands off. When it gives a wrong answer or costs 10x more than expected, print statements do not tell you which turn, which tool argument or which handoff caused it. Tracing records the exact sequence, inputs, outputs and durations so you can replay the failure mentally.

## 🔴 यह क्यों बना? (Hindi)
Agent run non-deterministic होता है: model खुद tools चुनता है, retry करता है, handoff करता है। गलत जवाब आए या खर्च 10 गुना हो जाए तो print से पता नहीं चलता कि कौन सा turn, कौन सा tool argument या कौन सा handoff ज़िम्मेदार था। Tracing सही क्रम, inputs, outputs और durations रिकॉर्ड करती है ताकि आप गलती की जड़ तक पहुँच सकें।

---

## 🟢 How it Works

```
Step 1 -> Runner.run() starts (opens a trace if none is active)
Step 2 -> Trace name = RunConfig.workflow_name (default "Agent workflow")
Step 3 -> Spans nest automatically:
          Task/Agent span
            +- Turn span
                 +- Generation span (LLM request/response)
                 +- Function span   (each tool call)
                 +- Guardrail / Handoff / MCP spans
Step 4 -> Each span ends -> sent to registered TracingProcessor(s)
Step 5 -> Default processor batches and exports to OpenAI backend
          (needs an OpenAI API key; otherwise skipped)
Step 6 -> You view the tree in the dashboard or your own backend
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Runner.run() शुरू (कोई trace active न हो तो नया खुलता है)
Step 2 -> Trace का नाम = RunConfig.workflow_name (default "Agent workflow")
Step 3 -> Spans अपने-आप nest होते हैं:
          Task/Agent span
            +- Turn span
                 +- Generation span (LLM request/response)
                 +- Function span   (हर tool call)
                 +- Guardrail / Handoff / MCP spans
Step 4 -> हर span खत्म होने पर registered TracingProcessor को जाता है
Step 5 -> Default processor batch करके OpenAI backend को export करता है
          (OpenAI API key चाहिए; वरना skip)
Step 6 -> आप dashboard या अपने backend में tree देखते हैं
```

**Knobs that exist in `RunConfig` (verified in 0.24.0):** `workflow_name`, `trace_id`, `group_id`, `trace_metadata`, `tracing_disabled`, `trace_include_sensitive_data`, and `tracing`. Use `group_id` to link all turns of one chat, `trace_metadata` for tenant/user-tier tags.

**Turning it off:** `RunConfig(tracing_disabled=True)` for one run, `set_tracing_disabled(True)` globally, or environment variable `OPENAI_AGENTS_DISABLE_TRACING=1` (read once at first use). Use `trace_include_sensitive_data=False` (or env `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA`) to keep prompts and tool inputs/outputs out of spans while keeping timings.

**Important gotchas:** (1) if you wrap calls in your own `with trace("name")`, that trace wins and `RunConfig.workflow_name` is ignored (we saw the outer name in the exported trace). (2) Inside one `with trace(...)` several `Runner.run` calls share one trace id - good for multi-run workflows. (3) Tracing export is a separate network path; if it fails it must not break your request, so keep it off the critical path.

**Hindi सार:** trace = पूरा workflow, span = उसका एक timed हिस्सा। Sensitive data (customer prompts) बाहर नहीं भेजना हो तो `trace_include_sensitive_data=False` रखें। अपना `with trace(...)` लगाया तो वही नाम चलेगा, `workflow_name` नहीं।

---

## 🟡 Real World Example
**Tariff Agent debugging.** A broker says 'the duty answer was 8% but should be 20%'. You open the trace by `group_id=session-42`: Turn 1 Generation chose `search_hs_codes`; the Function span shows it returned HS 6109.90 (wrong); Turn 2 called `get_tariff_rate('6109.90')` -> 8%. Root cause: the search tool, not the LLM. You fix the tool and add a regression test.

**Research Agent:** trace shows 14 turns of web-search; you add `max_turns` and a better stop rule.

## 🟡 Real Example Hindi mein
**Tariff Agent debugging.** Broker कहता है 'duty 8% बताई, होनी 20% थी'। आप `group_id=session-42` से trace खोलते हैं: Turn 1 Generation ने `search_hs_codes` चुना; Function span दिखाता है कि वह HS 6109.90 (गलत) लौटा; Turn 2 में `get_tariff_rate('6109.90')` -> 8%। जड़ search tool में थी, LLM में नहीं। Tool ठीक करके regression test जोड़ दिया।

**Research Agent:** trace में web-search के 14 turns दिखे; आपने `max_turns` और बेहतर stop rule जोड़ा।

---

## 💻 Code Example — Basic
Runs offline. A tiny processor prints the span tree so you see what the SDK records. `emit_traces=True` makes the scripted model emit generation spans like a real model would.

```python
# Basic: see the trace tree the SDK builds for one Tariff Agent run (offline)
import asyncio                                           # async runner
from typing import Any                                   # type hints
from agents import (Agent, Runner, RunConfig, TracingProcessor, Span, Trace,
                    function_tool, set_trace_processors, trace)      # tracing API
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

class PrintProcessor(TracingProcessor):                  # receives every trace/span event
    def on_trace_start(self, t: Trace) -> None: print("TRACE START:", t.name)
    def on_trace_end(self, t: Trace) -> None: print("TRACE END  :", t.name)
    def on_span_start(self, span: Span[Any]) -> None: pass
    def on_span_end(self, span: Span[Any]) -> None:      # print one line per finished span
        d = span.span_data                               # typed payload of the span
        print("  span:", type(d).__name__, getattr(d, "name", ""))
    def shutdown(self) -> None: pass                     # required by the interface
    def force_flush(self) -> None: pass                  # required by the interface

@function_tool                                           # becomes a FunctionSpanData when called
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty percent for an HS code."""
    return "20"

async def main() -> None:
    set_trace_processors([PrintProcessor()])             # replace default exporter (no network)
    model = ScriptedModel([[function_call("get_tariff_rate", {"hs_code": "6109.10"}, call_id="c1")],
                           [assistant_message("Duty is 20 percent.")]], emit_traces=True)
    agent = Agent(name="Tariff Agent", instructions="Use tools.", model=model, tools=[get_tariff_rate])
    cfg = RunConfig(workflow_name="tariff-lookup",       # name shown in the trace list
                    group_id="session-42",               # link many runs of one chat
                    trace_metadata={"tenant": "acme"})   # searchable tags
    r = await Runner.run(agent, "Duty on cotton t-shirts?", run_config=cfg)  # SDK opens the trace itself
    print("answer:", r.final_output)
    model.extend([[assistant_message("A1")], [assistant_message("A2")]])  # queue two more scripted replies
    with trace("two-step-workflow"):                     # manual trace: both runs below share ONE trace
        await Runner.run(agent, "first question")        # becomes a child of the manual trace
        await Runner.run(agent, "second question")       # same trace id for both runs

asyncio.run(main())
```

## 💻 Code Example — Advanced
FastAPI: per-request trace with group id (chat session), tenant metadata, a custom span and sensitive-data off. Runs offline via TestClient; swap `ScriptedModel` for a real model name in production (not run here).

```python
# Advanced: FastAPI service that tags every request's trace and can opt out of sensitive data (offline)
import uuid                                              # per-request ids
from typing import Any                                   # type hints
from fastapi import FastAPI, Header                      # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Runner, RunConfig, TracingProcessor, Span, Trace,
                    set_trace_processors, trace, custom_span)        # tracing API
from agents.testing import ScriptedModel, assistant_message          # fake LLM

SEEN: list[dict[str, Any]] = []                          # tiny in-memory "trace store" for the demo

class Collect(TracingProcessor):                         # swap for an OTEL/Langfuse exporter in prod
    def on_trace_start(self, t: Trace) -> None:
        SEEN.append(t.export() or {})                    # export() = the dict that would be sent to a backend
    def on_trace_end(self, t: Trace) -> None: pass
    def on_span_start(self, span: Span[Any]) -> None: pass
    def on_span_end(self, span: Span[Any]) -> None: pass
    def shutdown(self) -> None: pass
    def force_flush(self) -> None: pass

set_trace_processors([Collect()])                        # process-wide; do this once at startup

class AskIn(BaseModel):
    question: str

def build_agent() -> Agent:                              # one agent per call keeps the demo stateless
    model = ScriptedModel([[assistant_message("Duty is 20 percent.")]])
    return Agent(name="Tariff Agent", instructions="Answer duty questions.", model=model)

app = FastAPI()

@app.post("/ask")
async def ask(body: AskIn, x_session_id: str | None = Header(default=None),
              x_tenant: str = Header(default="unknown")) -> dict[str, Any]:
    request_id = uuid.uuid4().hex[:8]                    # correlate logs and traces
    cfg = RunConfig(
        workflow_name="tariff-api",                      # constant: easy to filter in the dashboard
        group_id=x_session_id,                           # all turns of one chat share a group
        trace_metadata={"tenant": x_tenant, "request_id": request_id},  # metadata values are strings
        trace_include_sensitive_data=False,              # keep prompts/tool I/O out of exported spans
    )
    with trace("tariff-api-request", group_id=x_session_id,
               metadata={"tenant": x_tenant, "request_id": request_id}):  # one parent trace; RunConfig.workflow_name is ignored inside it
        with custom_span("preprocess", {"len": len(body.question)}):  # your own timed step
            q = body.question.strip()
        result = await Runner.run(build_agent(), q, run_config=cfg, max_turns=4)
    return {"answer": str(result.final_output), "request_id": request_id}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/ask", json={"question": " Duty? "}, headers={"x-session-id": "s1", "x-tenant": "acme"}).json())
    print(SEEN)                                          # shows the trace names / group ids recorded
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Built-in tracing | Via LangSmith (needs setup/env) | Telemetry + 3rd-party (AgentOps, Langfuse) | Built-in, on by default (spans for agent/LLM/tool/guardrail/handoff) | OpenTelemetry support in newer versions; logging events |
| Default backend | LangSmith | None/optional | OpenAI traces dashboard | None (bring your own) |
| Custom exporter | Callbacks / LangSmith | Listeners / integrations | `TracingProcessor`, `set_trace_processors` | OTel exporters |
| Group runs into a session | thread/metadata | manual | `group_id` | manual |
| Redact sensitive data | manual | manual | `trace_include_sensitive_data=False` | manual |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Assuming traces appear in a dashboard with no API key.
✅ Correct: The default exporter needs an OpenAI key; with none, spans are skipped. Add your own processor if you want local/other storage.

❌ Mistake 2: Calling `set_trace_processors` and forgetting it removes the default exporter.
✅ Correct: Use `add_trace_processor` to keep the default and add yours; use `set_trace_processors` to fully replace.

❌ Mistake 3: Logging full customer prompts and tool results into traces.
✅ Correct: Set `trace_include_sensitive_data=False` for regulated data and redact in your own processor.

❌ Mistake 4: Setting `workflow_name` in RunConfig but also wrapping in `with trace('x')` and wondering why the name differs.
✅ Correct: Pick one: either let the SDK open the trace (RunConfig) or open your own with `trace(...)`.

---

## 🧠 Tricky Interview Question
Your FastAPI service handles 500 req/s with background tracing export. After a deploy, p99 latency doubles but only when the OpenAI traces endpoint is slow. What is happening and how do you fix it?

**Answer:** Spans are queued in a batch processor and exported from a background worker, so normal export slowness should not block requests. Check whether (a) a custom synchronous processor does network I/O inside `on_span_end` (it runs in the request path), (b) the queue is full and the processor drops or blocks, or (c) you called `flush_traces()` inside the request handler. Fix: do I/O only in a `BatchTraceProcessor` exporter (background), keep `on_span_end` O(1), size `max_queue_size`, call `flush_traces()` only at shutdown or in short-lived workers, and consider sampling or `trace_include_sensitive_data=False` to cut payload size. Verify with a load test; do not guess.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the difference between a trace and a span?

**A1:** A trace is one end-to-end workflow; a span is a timed operation inside it (agent, generation, function, guardrail, handoff, custom). Spans form a tree under one trace id.

**Q2:** Is tracing on by default?

**A2:** Yes. It can be disabled per run, globally, or via `OPENAI_AGENTS_DISABLE_TRACING`. Export to the OpenAI backend requires an API key.

**Q3:** How do you link all turns of a chat?

**A3:** Set the same `group_id` (for example the session id) in `RunConfig` or `trace(...)`.

**Q4:** How do you keep PII out of traces?

**A4:** `trace_include_sensitive_data=False`, plus redaction in a custom processor, plus not putting PII into `trace_metadata`.

**Q5:** Design observability for a multi-agent FastAPI service.

**A5:** One trace per request with `group_id=session`, metadata for tenant/version, custom spans around non-agent steps (retrieval, DB), a batch exporter to your store (OTLP/Langfuse), PII redaction, alerts on error spans and turn counts, dashboards for tokens per workflow, and sampling for high-volume tenants.

---

## 💰 Cost Impact
Tracing itself costs no LLM tokens. Costs are: (1) network/CPU for export (batching keeps it small), (2) storage of spans, which can be large when full prompts/tool outputs are included, (3) engineer time saved. **Use traces to cut LLM cost:** sort traces by `usage.total_tokens`, find workflows with many turns, and fix the tools or prompts that cause loops. Token numbers must come from your own traces/usage objects; any per-run figures in articles are approximate and model-dependent - verify.

---

## 🔷 When to Use
✅ Use when:
- Any multi-turn or multi-tool agent, from day one
- Debugging wrong answers, loops and unexpected spend
- Auditing which tools ran for which tenant
- Evaluating prompt/model changes by comparing traces

❌ Avoid when:
- Exporting raw prompts with PII to a third-party backend without review
- Doing synchronous network I/O inside a processor callback
- Relying on traces as the only audit log for compliance (store your own immutable log)

---

## 📊 Visual Diagram
```
Runner.run()
   |
   v
 TRACE "tariff-api"  (group_id = session-42, metadata = tenant)
   |
   +-- AGENT span: Tariff Agent
   |      +-- TURN 1
   |      |     +-- GENERATION span  (LLM: chose tool)
   |      |     +-- FUNCTION span    (get_tariff_rate)
   |      +-- TURN 2
   |            +-- GENERATION span  (final answer)
   +-- CUSTOM span: preprocess
   |
   v  each span end
 TracingProcessor(s) --> batch --> exporter --> dashboard / your DB
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | One end-to-end workflow record | पूरे workflow का record |
| Span | Timed step inside a trace | trace का एक timed हिस्सा |
| workflow_name | Human name of the trace | trace का नाम |
| group_id | Links traces of one conversation | एक बातचीत के traces जोड़ता है |
| TracingProcessor | Receives trace/span events | trace/span events लेने वाला |
| Sensitive data flag | Include/exclude prompts and tool I/O | prompts/tool I/O शामिल करना या नहीं |

---

## ⚡ 3-Line Summary
English: Tracing is on by default: each run is a trace of nested spans (agent, generation, function, guardrail, handoff).
Tag traces with `workflow_name`, `group_id` and metadata, and keep PII out with `trace_include_sensitive_data=False`.
Export needs an OpenAI key unless you install your own processor.

Hindi: Tracing default रूप से चालू है: हर run nested spans (agent, generation, function, guardrail, handoff) वाला trace बनता है।
`workflow_name`, `group_id` और metadata से traces को tag करें, और PII रोकने के लिए `trace_include_sensitive_data=False` रखें।
Export के लिए OpenAI key चाहिए, वरना अपना processor लगाएँ।

---

## ➡️ Next Topic
**#45 Custom Tracing** - write your own `TracingProcessor`, add custom spans and send traces to your own backend instead of (or in addition to) the OpenAI dashboard.

---
