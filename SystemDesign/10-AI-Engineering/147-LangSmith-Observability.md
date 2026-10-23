# 147. LangSmith Observability
# हिंदी में: LLM Observability (LangSmith और दूसरे tools) — हर AI request के अंदर क्या हुआ यह देखना: कौन-सा prompt गया, क्या retrieve हुआ, कौन-से tools चले, कितने tokens/पैसे/समय लगे, कहाँ fail हुआ, यूज़र ने 👍 दिया या 👎 — traces, metrics, feedback, datasets और prompt versions

---

## 🔵 Simple Definition (English)
**LLM observability** is the ability to see and analyze what your AI application does on every request:
- **traces** of each step (LLM calls, retrieval, reranking, tool calls, agent loops), with inputs, outputs, latency, token usage, cost and errors
- aggregated **metrics** and **user feedback**
- linking traces to **datasets, evaluations and prompt versions**
**LangSmith** (from the LangChain team) is a hosted (and self-hostable for enterprise) platform providing:
- **Tracing**: nested runs and spans, automatic for LangChain/LangGraph, via `@traceable` or SDK wrappers for plain code
- **Monitoring dashboards**: latency, tokens, cost, error rates, feedback scores
- **Feedback** capture (user 👍/👎, scores) attached to runs
- **Datasets and experiments**: offline evals comparing versions (Topic 146), **online evaluators** on production traces, and **annotation queues** for human review
- **Prompt hub/versioning** and a playground
Alternatives and complements: **Langfuse** (open-source, self-hostable, good for data residency), **Arize Phoenix**, **Helicone**, **Datadog/New Relic LLM observability**, and **OpenTelemetry GenAI semantic conventions** for vendor-neutral tracing.

## 🔵 सरल परिभाषा (Hindi)
LLM observability = हर request पर AI ऐप ने क्या किया यह देखना और समझना: हर कदम (LLM call, retrieval, rerank, tools, agent loop) का trace — input, output, समय, tokens, ख़र्च, errors; मिले-जुले metrics; यूज़र का feedback; और traces को datasets, evals, prompt versions से जोड़ना।
LangSmith (LangChain टीम) — tracing (LangChain/LangGraph में अपने-आप, बाक़ी code में `@traceable`/wrappers), dashboards (latency, tokens, ख़र्च, errors, feedback), feedback, datasets/experiments, production traces पर online evaluators, इंसानी जाँच की queues, prompt versions; विकल्प: Langfuse (open-source, अपने server पर — डेटा भारत में), Arize Phoenix, Helicone, Datadog, OpenTelemetry।

---

## 🔴 Problem it Solves
LLM apps fail in **non-obvious, non-deterministic** ways that normal APM can't explain:
- "The bot told a customer their refund was approved when it wasn't". Which prompt version? Which retrieved chunk? Did a tool return an error the model ignored?
- Latency jumped from 2 s to 9 s. Is it the reranker, a slow tool, the model provider, or an agent looping 6 times?
- The bill doubled this week. Which feature, tenant or prompt change caused it?
- Quality dropped after a document update or model change. Which segment (Hindi queries, the Instamart product line)?
- Product teams need examples of failures to improve prompts and datasets.
Without step-level traces, debugging means guessing. Observability provides **root-cause analysis, cost attribution, quality monitoring and a data flywheel** (production failures become eval cases).

## 🔴 यह क्यों बना? (Hindi)
LLM ऐप ऐसे तरीकों से fail होते हैं जो सामान्य APM नहीं समझा सकता: "bot ने कहा refund मंज़ूर, पर हुआ नहीं" — कौन-सा prompt version, कौन-सा chunk, कोई tool error जिसे model ने अनदेखा किया?; latency 2 से 9 सेकंड — reranker, धीमा tool, provider, या agent 6 बार घूमा?; बिल दोगुना — कौन-सा feature/ग्राहक/prompt?; document या model बदलने के बाद गुणवत्ता गिरी — कौन-सा segment (हिंदी, Instamart)?
Step-level traces के बिना debugging अंदाज़ा है; observability = मूल कारण, ख़र्च का हिसाब, गुणवत्ता निगरानी, और production की ग़लतियाँ eval cases बनें (data flywheel)।

---

## 🟢 How it Works — Step by Step

### Anatomy of an LLM trace

```
Trace: POST /api/help/ask  (user=hash, tenant=42, lang=hi, prompt=support_v7, app=1.14.0)   3.2 s, ₹0.31
 ├─ guard_input                          12 ms
 ├─ condense_query (claude-haiku-5-5)    280 ms   in 410 tok / out 22 tok
 ├─ hybrid_search                        64 ms    vec 50 + bm25 50 → 40 fused
 ├─ rerank (cohere rerank-v3.5)          190 ms   top6 scores [0.91, 0.84, …]
 ├─ generate (claude-sonnet-5-5)         2.5 s    TTFT 720 ms, in 3,120 / out 186 tok, stop=end_turn
 │    inputs: system v7, sources S1..S6  outputs: answer + citations [S1][S3]
 ├─ validate_citations                   2 ms     ok
 └─ feedback (later): 👎 "wrong timeline" → linked to this trace → annotation queue
```

### What to capture (and what not)

```
Capture: request/trace id, user (hashed) & tenant, feature/route, model & params, prompt template id +
  version, rendered prompt (redacted), retrieved doc ids + scores, tool calls (name/args/result/status),
  tokens (input/output/cached), cost, latency (TTFT, total, per step), stop reason, errors/retries,
  guardrail decisions, final output, user feedback, app version, experiment/flag variant
Redact/avoid: phone numbers, addresses, card/UPI ids, OTPs, PII in free text → mask before export;
  sampling for full payloads; access controls & retention limits; self-host (Langfuse/LangSmith enterprise)
  when data must stay in India
```

### Dashboards & alerts

```
Quality: feedback rate & 👍 ratio, online-judge groundedness, "I don't know" rate, escalation-to-agent rate
Performance: p50/p95 latency & TTFT per step/model, tool error rates, agent steps per task, loop terminations
Cost: tokens & ₹ per request/feature/tenant/model, cache hit rate (prompt cache, semantic cache)
Reliability: provider 429/5xx/overloaded rates, fallback usage, timeouts
Alerts: cost/day > budget, groundedness drop > X%, p95 > SLO, tool error spike, sudden refusal increase
```

### The improvement flywheel

```
Production traces → filter (👎, low judge score, escalations) → annotation queue (human labels the correct
behaviour) → add to eval dataset → change prompt/retrieval/model → offline experiment vs baseline (Topic 146)
→ deploy behind flag → online monitoring → repeat
```

### Vendor-neutral option: OpenTelemetry

```
OTel GenAI semantic conventions define span attributes for LLM calls (model, tokens, operation…)
→ send to any backend (Jaeger, Grafana Tempo, Datadog, Langfuse/Phoenix via OTLP)
→ unify LLM spans with existing service traces (Topic 102) — one trace from API gateway to vector DB to LLM
```

## 🟢 कैसे काम करता है? (Hindi)
1. एक trace में हर कदम का span: guard, सवाल साफ़ करना (haiku, tokens), hybrid search (कितने उम्मीदवार), rerank (scores), generate (sonnet — TTFT, tokens, stop reason, कौन-सा prompt version, कौन-से sources), citations जाँच, और बाद में आया 👎 feedback उसी trace से जुड़ा।
2. Capture: trace id, hashed user, tenant, feature, model, prompt version, retrieved ids + scores, tool calls, tokens, ख़र्च, latency, errors, guardrail फ़ैसले, output, feedback, app version, experiment; मत भेजो: phone, पता, card/UPI id, OTP — पहले mask; डेटा भारत में चाहिए तो self-host (Langfuse/LangSmith enterprise)।
3. Dashboards: गुणवत्ता (👍 अनुपात, groundedness, "पता नहीं" दर, escalation), performance (p95, TTFT, tool errors, agent steps), ख़र्च (₹ प्रति request/feature/tenant, cache hit), भरोसा (429/5xx, fallback); alerts — budget पार, groundedness गिरी, p95 SLO से ऊपर।
4. Flywheel: production traces → 👎/कम score/escalation वाले छाँटो → इंसान सही व्यवहार label करे → eval dataset में → prompt/retrieval/model बदलो → offline तुलना → flag के पीछे deploy → फिर निगरानी।
5. Vendor-neutral: OpenTelemetry के GenAI conventions से LLM spans किसी भी backend (Jaeger, Tempo, Datadog, Langfuse) पर — API gateway से vector DB से LLM तक एक ही trace।

---

## 🟡 Real World Example

**LangSmith (2023 onward)** — widely adopted by teams using LangChain and LangGraph and by teams on plain SDKs (via `@traceable` and wrappers) for tracing, evals and monitoring. LangChain has published customer case studies of production assistants (e.g., in fintech and support) that use LangGraph plus LangSmith for debugging and evaluation.

**Langfuse (open source)** — popular with teams needing self-hosting and data residency (EU/India), offering tracing, prompt management, evals and cost tracking, with OpenTelemetry support.

**OpenTelemetry GenAI conventions** — the OTel community standardized attributes for generative-AI spans, so platforms like Datadog, Grafana and Honeycomb can display LLM calls alongside service traces. This matters for enterprises with existing observability stacks.

**Cost incidents** — teams commonly discover runaway costs (an agent loop, an accidental 100k-token prompt, a missing cache) only through per-request token dashboards. That's why cost per feature and tenant is a first-class observability metric.

## 🟡 Real Example Hindi में
LangSmith (2023 से) LangChain/LangGraph और सीधे SDK वाली टीमों (`@traceable`, wrappers) में tracing, evals और निगरानी के लिए लोकप्रिय — LangChain ने fintech/support जैसे production assistants के case studies छापे हैं; Langfuse (open-source) self-hosting और डेटा भारत/EU में रखने वाली टीमों में लोकप्रिय।
OpenTelemetry के GenAI conventions से Datadog/Grafana में LLM calls बाक़ी services के traces के साथ दिखते हैं; बेकाबू ख़र्च (agent loop, 1 लाख tokens का prompt, cache ग़ायब) अक्सर per-request token dashboards से ही पकड़ा जाता है।

---

## 🟠 My Stack Example

### Enable LangSmith tracing (env) + trace plain Python code with @traceable
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=ls_...           # from secrets manager in prod
export LANGSMITH_PROJECT=quickbite-help-prod
```
```python
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic
import anthropic

client = wrap_anthropic(anthropic.Anthropic())                # LLM calls auto-traced with tokens/latency

@traceable(run_type="retriever", name="hybrid_search")
def hybrid_search_traced(query: str, tenant_id: int):
    return hybrid_search_sync(query, tenant_id)

@traceable(name="help_answer", tags=["support", "rag"])
def answer(question: str, user):
    docs = hybrid_search_traced(question, user.tenant_id)
    resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=500, system=SUPPORT_SYSTEM_V7,
                                  messages=build_messages(docs, redact_pii(question)))
    return resp.content[0].text

# Attach metadata (prompt version, tenant, lang) for filtering in the UI
answer_with_meta = traceable(answer, metadata={"prompt_version": "support_v7", "app_version": "1.14.0"})
```

### Record user feedback against the trace
```python
from langsmith import Client
ls = Client()
@app.post("/api/feedback")
async def feedback(body: Feedback, user=Depends(current_user)):
    ls.create_feedback(run_id=body.run_id, key="user_rating", score=1 if body.thumbs_up else 0, comment=body.comment)
    return {"ok": True}
# Return run_id to the client with each answer (e.g., from langsmith run tree / response headers)
```

### Self-hosted alternative: Langfuse with OpenTelemetry-style decorators (Python sketch)
```python
from langfuse import observe, get_client        # Langfuse SDK v3; self-host on your infra (e.g., AWS Mumbai)
langfuse = get_client()

@observe(name="help_answer")
def answer(question, user):
    langfuse.update_current_trace(user_id=hash_id(user.id), tags=["support"], metadata={"tenant": user.tenant_id})
    ...
```

### Cost & latency metrics into your existing stack (Prometheus)
```python
from prometheus_client import Counter, Histogram
LLM_TOKENS = Counter("llm_tokens_total", "Tokens", ["feature", "model", "kind"])
LLM_COST = Counter("llm_cost_inr_total", "Cost in INR", ["feature", "tenant"])
LLM_LATENCY = Histogram("llm_latency_seconds", "LLM latency", ["feature", "model"])

def record_usage(feature, tenant, model, usage, seconds):
    LLM_TOKENS.labels(feature, model, "input").inc(usage.input_tokens)
    LLM_TOKENS.labels(feature, model, "output").inc(usage.output_tokens)
    LLM_COST.labels(feature, tenant).inc(price_inr(model, usage))
    LLM_LATENCY.labels(feature, model).observe(seconds)
# Grafana alert: sum(rate(llm_cost_inr_total[1h])) * 24 > daily_budget
```

### PII redaction before traces leave your network
```python
import re
PATTERNS = [(re.compile(r"\b[6-9]\d{9}\b"), "<PHONE>"), (re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b"), "<EMAIL>"),
            (re.compile(r"\b[\w.-]+@(ok\w+|ybl|paytm|upi)\b"), "<UPI_ID>"), (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "<AADHAAR?>")]
def redact_pii(text: str) -> str:
    for p, repl in PATTERNS: text = p.sub(repl, text)
    return text
```

---

## ⚫ Interview Questions + Answers

**Q1: What should you trace in an LLM application?**
A1: Every step of the request as nested spans: input guardrails, query rewriting, retrieval (query, filters, doc IDs and scores), reranking, each LLM call (model, parameters, prompt template and version, rendered prompt with redaction, output, tokens including cached, cost, TTFT, latency, stop reason), tool calls (name, arguments, results, errors), agent iterations, output validation and guardrail decisions, plus request context (hashed user, tenant, feature, app version, experiment variant). Attach user feedback and evaluation scores to the trace so failures can be investigated and turned into eval cases.

**Q2: How do you debug a wrong answer from a RAG assistant in production?**
A2: Find the trace (via the feedback link or request ID) and inspect it step by step. Was the query rewritten correctly? Did retrieval return the right documents (check IDs, scores, filters, outdated docs)? Did reranking drop the right chunk? Did the prompt version or model change recently? Did the model cite sources that don't support the claim (generation issue)? Did a tool fail silently? Reproduce in a playground with the same inputs, fix the root cause (data, retrieval, prompt or model), add the case to the eval set, and verify with an offline experiment before redeploying.

**Q3: How do you track and control LLM costs?**
A3: Record token usage and computed cost per call, tagged by feature, tenant, user tier, model and prompt version. Build dashboards and budgets with alerts on daily spend and anomalies (sudden token spikes, agent loops), monitor cache hit rates, and attribute costs back to product features. Combine with controls: per-tenant quotas, max tokens, step limits, model routing, caching and batch APIs (Topic 153).

**Q4: How do you handle privacy in LLM observability?**
A4: Minimize and protect what's captured. Redact PII (phones, emails, UPI IDs, addresses, OTPs) before sending traces to third-party platforms, hash user IDs, sample full payloads, restrict access with RBAC, set retention limits, and encrypt data. Consider self-hosted observability (Langfuse, or self-hosted LangSmith for enterprise) when regulations or contracts require data to stay in India. Document what's logged in privacy notices and honour deletion requests.

**Q5: LangSmith vs OpenTelemetry-based observability?**
A5: LangSmith is purpose-built for LLM apps. It gives rich, automatic tracing for LangChain and LangGraph, prompt and response views, datasets and experiments, online evaluators, annotation queues and feedback, which accelerates the quality workflow. OpenTelemetry with GenAI semantic conventions is vendor-neutral, integrates LLM spans into existing distributed tracing and APM (Datadog, Grafana) and avoids lock-in, but evaluation and dataset features come from other tools. Many teams use both: OTel for infrastructure-wide traces, plus an LLM platform (LangSmith or Langfuse) for evals and prompt iteration.

---

## 🔷 Trade-offs
✅ Rich step-level traces: fast debugging & cost attribution — ❌ data volume, privacy risk, overhead.
✅ Hosted platforms: quick start — ❌ data residency/compliance concerns; self-host: control — ❌ ops effort.
✅ Full payload capture: best debugging — ❌ PII exposure → redact & sample.
✅ OTel standards: vendor-neutral — ❌ fewer built-in eval features.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Observability | Seeing system internals from outputs | अंदर क्या हुआ देखना |
| Trace / span | Request path / step in it | request का रास्ता / कदम |
| Run (LangSmith) | Traced unit of work | trace हुआ काम |
| TTFT | Time to first token | पहला token आने का समय |
| Token cost | Spend per call | प्रति call ख़र्च |
| Feedback | User/judge scores on outputs | जवाब पर राय |
| Annotation queue | Human review workflow | इंसानी जाँच की कतार |
| Prompt versioning | Track prompt changes | prompt के versions |
| PII redaction | Mask personal data | निजी डेटा छुपाना |
| OTel GenAI conventions | Standard LLM span attributes | LLM spans का मानक |

---

## ⚡ 3-Line Summary
**English:**
1. Trace every step (guard, rewrite, retrieval, rerank, LLM, tools, validation) with prompts, ids, tokens, cost, latency, errors and context (tenant, prompt version, variant).
2. Dashboards & alerts for quality (feedback, groundedness, escalations), performance (p95, TTFT), cost (₹ per feature/tenant) and reliability; feed failures into eval datasets.
3. Use LangSmith/Langfuse (self-host for residency) and/or OpenTelemetry; redact PII, sample payloads, control access and retention.

**Hindi:**
1. हर कदम का trace — prompts, ids, tokens, ख़र्च, latency, errors, tenant और prompt version के साथ।
2. गुणवत्ता, performance, ख़र्च और भरोसे के dashboards/alerts; ग़लतियाँ eval dataset में।
3. LangSmith/Langfuse (डेटा भारत में चाहिए तो self-host) या OpenTelemetry; PII छुपाओ, sampling, access और retention नियंत्रण।

---

## ➡️ Next Topic Suggestion
**148. LLM Caching** — Observability often reveals the same questions and prompt prefixes repeating. Next: exact, semantic and provider prompt caching, plus retrieval caching, to cut latency and cost.
