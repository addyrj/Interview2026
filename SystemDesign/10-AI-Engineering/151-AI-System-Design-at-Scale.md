# 151. AI System Design at Scale
# हिंदी में: बड़े पैमाने पर AI System Design — करोड़ों यूज़र्स के लिए production AI सहायक (जैसे food-delivery का support bot) का पूरा डिज़ाइन: ज़रूरतें, tokens/ख़र्च का अनुमान, architecture (LLM gateway, RAG, tools, memory, guardrails), latency budget, भरोसा, निगरानी, evals और इंसान को सौंपना

---

## 🔵 Simple Definition (English)
**AI system design at scale** means designing a production LLM-powered system that is **useful, safe, reliable, fast and affordable** for millions of users. It combines classic distributed-systems design (Topics 01–126) with AI-specific concerns:
- **Token-based capacity and cost planning**: tokens per request, tokens per minute rate limits, GPU throughput if self-hosting.
- An **LLM gateway** for routing, fallbacks, quotas, caching and logging across providers and models.
- **Retrieval infrastructure** (ingestion pipelines, vector and keyword indexes) and **tool services** with strict authz.
- **Orchestration** (workflows and agents with bounded loops), **memory**, and **guardrails** (input, tool, output).
- **Evaluation and observability** (offline evals in CI, online judges, traces, feedback) as first-class components.
- **Human-in-the-loop** and handoff to human agents, plus **compliance** (data residency, DPDP, audit).
- **Rollout safety**: shadow mode, A/B tests, feature flags, kill switches.
The interview version: "Design an AI customer-support assistant for Swiggy/Zomato/Flipkart", "Design ChatGPT", "Design a chat-with-your-documents SaaS" or "Design an AI coding assistant".

## 🔵 सरल परिभाषा (Hindi)
बड़े पैमाने पर AI system design = करोड़ों यूज़र्स के लिए ऐसा LLM system जो काम का, सुरक्षित, भरोसेमंद, तेज़ और किफ़ायती हो — पुराने distributed systems design के साथ AI की ख़ास बातें: tokens के हिसाब से capacity और ख़र्च (प्रति request tokens, provider की tokens/मिनट सीमा, अपने GPU हों तो throughput); LLM gateway (routing, fallback, quotas, cache, logging); retrieval (ingestion, vector/keyword index) और सख़्त अनुमति वाले tools; workflows/agents (सीमित loops), memory, guardrails; evals और observability; इंसान को सौंपना; compliance (डेटा भारत में, DPDP, audit); सुरक्षित rollout (shadow, A/B, flags, kill switch)।
इंटरव्यू: "Swiggy/Flipkart का AI support assistant डिज़ाइन करो", "ChatGPT डिज़ाइन करो", "chat-with-docs SaaS"।

---

## 🔴 Problem it Solves
A demo assistant that works for 10 users breaks at millions:
- **Cost explodes**: 5k-token prompts × lakhs of conversations per day becomes lakhs of rupees daily without caching, routing and token discipline.
- **Rate limits and outages**: provider tokens-per-minute caps are hit on IPL nights or sale days, and a single provider incident takes the feature down.
- **Latency**: chained calls (rewrite → retrieve → rerank → generate → guard) take 10 s without budgets, streaming and parallelism.
- **Quality and safety drift**: policies change, documents go stale, models get upgraded and injection attempts grow.
- **Accountability**: wrong refund promises, PII leaks and regulatory exposure.
- **Operational reality**: human agents need context-rich handoffs, and ops need dashboards and kill switches.
Designing at scale means **planning capacity in tokens, building layered reliability and safety, and making evaluation and observability part of the architecture**.

## 🔴 यह क्यों बना? (Hindi)
10 यूज़र्स वाला demo करोड़ों पर टूटता है: 5k tokens के prompts × रोज़ लाखों बातचीत = बिना caching/routing के रोज़ लाखों रुपये; IPL रात या sale पर provider की tokens/मिनट सीमा और एक provider बंद तो feature बंद; rewrite → retrieve → rerank → generate → guard की कड़ी बिना budget/streaming के 10 सेकंड; नीतियाँ/documents/models बदलने और injection बढ़ने से गुणवत्ता/सुरक्षा का खिसकना; ग़लत refund वादे, PII leak, नियम; इंसानी agents को पूरे संदर्भ के साथ handoff और ops को dashboards/kill switch चाहिए।
बड़े पैमाने का design = tokens में capacity, परतों में भरोसा और सुरक्षा, और evals/observability architecture का हिस्सा।

---

## 🟢 How it Works — Step by Step (Interview Design: AI support assistant for a food-delivery app)

### 1. Requirements

```
Functional: chat in app/web (English, Hindi, Hinglish); answer policy/how-to (RAG with citations);
  user-specific help via tools (order status, refund status, raise refund within limits, cancel order);
  multi-turn memory; escalate to human agent with summary; feedback 👍/👎; agent-assist mode for human agents
Non-functional: p95 time-to-first-token ≤ 1.5 s, full answer ≤ 5 s; availability 99.9%; groundedness ≥ 0.9;
  correct escalations; PII protection; data residency in India; cost ≤ ₹1 per conversation (target)
Scale: 20M MAU, 5% contact support monthly → 1M conversations/month (+ 3× on sale/rain days)
```

### 2. Back-of-the-envelope (tokens & cost)

```
Conversations/day ≈ 1M / 30 ≈ 33k (peak day 100k); turns/conversation ≈ 5 → 165k turns/day (peak 500k)
Peak QPS ≈ 500k / (8 busy hours × 3600) ≈ 17 turns/s (burst ×3 → ~50/s)
Tokens per turn: input ≈ 4,000 (system 1.2k + tools 0.8k + sources 1.5k + history 0.5k), output ≈ 250
Daily (normal): input 165k × 4k = 660M tokens; output 165k × 250 ≈ 41M tokens
Cost model (ILLUSTRATIVE prices, check current pricing): mid-tier model $3/M input, $15/M output
  → input $1,980 + output $620 ≈ $2,600/day (~₹2.2 lakh/day) → too high vs ₹1/conversation target (₹33k/day)
Optimizations:
  - prompt caching for static 2k-token prefix (system + tools): ~50% of input at ~10% price → input −45%
  - route 60% simple turns (status, FAQ) to small fast model (~1/10 price) or deterministic workflows
  - exact/semantic cache for FAQ (20–30% hit on sale days)
  - trim sources to top 4 chunks, summarize history
  → typically 5–10× cheaper → within budget; re-estimate with real prices & traffic
Rate limits: peak input tokens/min ≈ 50 turns/s × 4k × 60 = 12M TPM → request provider tier, spread across
  models/providers, queue non-urgent work (summaries) via batch API
```

### 3. High-level architecture

```
 Clients (RN app / Next.js web / agent console)
        │ HTTPS + SSE/WebSocket (streaming)
        ▼
 API Gateway (auth, rate limits per user/tenant, WAF) ──► Conversation Service (sessions, history, feedback)
        │
        ▼
 Orchestrator (LangGraph / workflow engine)
   ├─ Input Guard (PII redaction, abuse/injection classifier, scope)           [Topic 149]
   ├─ Router (intent: FAQ | ORDER | PAYMENT | ESCALATE | CHIT-CHAT)            [cheap model]
   ├─ Workflows: deterministic paths (refund status = tool + template reply)
   ├─ Agent loop (bounded) with Tools ──► Tool Gateway ──► Orders / Payments / Refund services
   │                                          (authz from session, limits, confirmations, idempotency)
   ├─ RAG: Retrieval Service (hybrid search + rerank) ──► Vector/Keyword index (pgvector/OpenSearch, Mumbai)
   ├─ Memory Service (user facts, episodes)                                    [Topic 145]
   └─ Output Guard (grounding/citations, commitments, PII, moderation)
        │
        ▼
 LLM Gateway: model aliases, routing (small/mid/large), provider fallback, timeouts/retries, quotas,
   exact/semantic cache, prompt-cache-friendly assembly, token & cost metering, logging (redacted)
        │                       │
   Hosted LLM APIs         Self-hosted open/fine-tuned models (vLLM GPU pool, autoscaling) [optional]
 Async: Ingestion pipeline (CMS → chunk → embed → index), batch jobs (conversation summaries, QA scoring),
        Kafka events → analytics warehouse
 Platform: Observability (traces/metrics: LangSmith/Langfuse/OTel), Eval service (offline CI + online judges),
        Feature flags/experiments, Human handoff (agent desk with AI summary), Audit & compliance store
```

### 4. Request flow & latency budget (p95)

```
Auth + guard (parallel with history/memory fetch)     100 ms
Router (small model, short prompt)                    250 ms
Retrieval (hybrid) + rerank  ║  tool calls (parallel)  300 ms
Generation TTFT (mid model, cached prefix)            700 ms   → user sees text at ~1.35 s
Streaming rest of answer                              1–2 s
Output guard: streaming-compatible checks on chunks; final citation/commitment check before "done"
Fallbacks: if generation > 8 s or provider error → retry on alternate model; if all fail → canned helpful
           reply + human handoff
```

### 5. Reliability & scale patterns

```
- Stateless orchestrator pods behind LB; conversation state in Redis/Postgres (checkpoints)
- Per-tenant/user quotas and token budgets; priority queues (live chats > background summaries)
- Provider diversity: ≥ 2 models/providers tested with the same prompts; circuit breakers per provider
- Degraded modes (feature flags): disable agentic paths → RAG-only → FAQ-only → human-only
- Backpressure: queue + "high demand" message during spikes; pre-scale before known events (IPL, sales)
- Idempotent tools; exactly-once effects for refunds/cancellations
- Self-hosting decision: high, steady volume + residency + fine-tuned small models → vLLM GPU pool with
  continuous batching; otherwise hosted APIs (simpler, better frontier quality)
```

### 6. Quality, safety & governance loop

```
Offline: eval suites (RAG faithfulness, tool-call correctness, safety red-team, Hindi/Hinglish quality) gate
  every prompt/model/index change
Online: sampled LLM judges, user feedback, escalation & recontact rates, CSAT vs human baseline
Shadow mode → 5% A/B → ramp with guardrail metrics (wrong refunds, complaints, cost/conversation)
Human handoff: summary + extracted facts + actions taken → agent desk; agents' corrections feed datasets
Compliance: data in India (Mumbai region), PII redaction, retention policies, audit logs of tool actions,
  DPDP consent; vendor DPAs; model cards & incident response
```

## 🟢 कैसे काम करता है? (Hindi)
1. ज़रूरतें: English/हिंदी/Hinglish chat, citations वाला RAG, tools (order status, refund status, सीमा में refund, cancel), याद, सारांश के साथ इंसान को सौंपना, feedback; TTFT p95 ≤ 1.5 s, 99.9% उपलब्धता, groundedness ≥ 0.9, डेटा भारत में, ₹1/बातचीत लक्ष्य; पैमाना — 2 करोड़ MAU, 5% → महीने में 10 लाख बातचीत।
2. अनुमान: रोज़ ~1.65 लाख turns (peak 5 लाख), peak ~17–50 turns/s; हर turn ~4k input + 250 output tokens → रोज़ 66 करोड़ input tokens; उदाहरण क़ीमतों पर ~₹2.2 लाख/दिन — लक्ष्य से बहुत ऊपर; इसलिए prompt caching, 60% सरल turns छोटे model/workflow को, FAQ cache, कम sources, सारांश — 5–10 गुना सस्ता; peak पर ~1.2 करोड़ tokens/मिनट — provider tier, कई models, batch API।
3. Architecture: clients → API gateway (auth, rate limit) → conversation service → orchestrator (input guard, router, deterministic workflows, सीमित agent loop + tool gateway, RAG service — hybrid + rerank, Mumbai index, memory, output guard) → LLM gateway (aliases, routing, fallback, quotas, cache, metering) → hosted APIs या अपना vLLM GPU pool; साथ में ingestion, batch jobs, Kafka → analytics, observability, eval service, flags, human desk, audit।
4. Latency budget: guard + history साथ 100 ms, router 250 ms, retrieval/rerank और tools साथ-साथ 300 ms, TTFT 700 ms → ~1.35 s पर पहला text, फिर streaming; 8 सेकंड या error पर दूसरा model, सब fail तो सधा जवाब + इंसान।
5. भरोसा और गुणवत्ता: stateless pods, Redis/Postgres में state, quotas और priority queues, ≥2 providers + circuit breakers, degraded modes (agent बंद → सिर्फ़ RAG → FAQ → सिर्फ़ इंसान), events से पहले pre-scale, idempotent tools; offline evals हर बदलाव पर, online judges/feedback, shadow → 5% A/B → धीरे बढ़ाओ, इंसानी सुधार dataset में, डेटा भारत में और DPDP।

---

## 🟡 Real World Example

**Klarna AI assistant (2024)** — Klarna reported that in its first month its OpenAI-powered assistant handled about two-thirds of customer-service chats (described as the work of hundreds of agents), with resolution times dropping from minutes to under two minutes. Later reporting (2025) noted Klarna re-emphasizing human support for quality. It's a well-known case of both the scale benefits and the need for human balance.

**ChatGPT scale** — serving hundreds of millions of weekly users required massive GPU fleets, aggressive capacity management (waitlists and rate limits early on), streaming, model routing and global infrastructure, the canonical "AI at scale" example.

**Air India "AI.g" (2023)** — Air India launched a generative-AI virtual agent handling large volumes of customer queries in multiple languages. It's an Indian enterprise example of an AI front line with human escalation.

**Indian consumer apps** — Zomato (Zomato AI), Swiggy (AI-powered search and support features), Flipkart (the Flippi shopping assistant) and banks have rolled out AI assistants. The common architectural themes are RAG over catalogs and policies, tool integrations with order systems, vernacular support, cost control at massive scale, and escalation to human agents.

## 🟡 Real Example Hindi में
Klarna (2024) ने बताया कि पहले महीने में उसके AI assistant ने लगभग दो-तिहाई customer service chats संभाले (सैकड़ों agents के बराबर), समाधान का समय मिनटों से 2 मिनट से कम; बाद में (2025) गुणवत्ता के लिए इंसानी support पर फिर ज़ोर — पैमाने का फ़ायदा और इंसानी संतुलन दोनों का सबक।
ChatGPT के करोड़ों साप्ताहिक यूज़र्स के लिए भारी GPU, capacity प्रबंधन, streaming, routing; Air India का "AI.g" (2023) कई भाषाओं में सवाल संभालता है; Zomato AI, Swiggy, Flipkart (Flippi), बैंक — catalog/नीति पर RAG, order systems से tools, vernacular, बड़े पैमाने पर ख़र्च नियंत्रण और इंसान को सौंपना।

---

## 🟠 My Stack Example

### Capacity & cost calculator (keep in your design doc)
```python
def daily_cost(turns_per_day, in_tok, out_tok, price_in_per_m, price_out_per_m,
               cached_frac=0.0, cache_read_discount=0.9, routed_small_frac=0.0, small_price_ratio=0.1):
    eff_in_price = price_in_per_m * ((1 - cached_frac) + cached_frac * (1 - cache_read_discount))
    big = (1 - routed_small_frac); small = routed_small_frac * small_price_ratio
    in_cost = turns_per_day * in_tok / 1e6 * eff_in_price * (big + small)
    out_cost = turns_per_day * out_tok / 1e6 * price_out_per_m * (big + small)
    return round(in_cost + out_cost, 2)

base = daily_cost(165_000, 4000, 250, 3, 15)                                         # ≈ 2,600 USD/day (illustrative)
optimized = daily_cost(165_000, 2800, 200, 3, 15, cached_frac=0.6, routed_small_frac=0.6)
print(base, optimized)                                                               # compare; plug in real prices
```

### LLM gateway: routing + fallback + quotas + metering (Node, simplified)
```js
const ROUTES = {
  router:   [{ p: 'anthropic', m: 'claude-haiku-5-5', timeoutMs: 3000 }],
  answer:   [{ p: 'anthropic', m: 'claude-sonnet-5-5', timeoutMs: 15000 }, { p: 'openai', m: process.env.OPENAI_FALLBACK_MODEL, timeoutMs: 15000 }],
  complex:  [{ p: 'anthropic', m: 'claude-opus-5-5', timeoutMs: 30000 }, { p: 'anthropic', m: 'claude-sonnet-5-5', timeoutMs: 15000 }],
};
export async function llm(route, req, ctx) {
  await quotas.consume(ctx.tenantId, estimateTokens(req));                        // per-tenant token budget
  const cached = await cache.get(route, req, ctx); if (cached) return cached;
  for (const t of ROUTES[route]) {
    if (breakers.isOpen(t.p, t.m)) continue;
    try {
      const res = await withTimeout(providers[t.p].complete(t.m, req), t.timeoutMs);
      breakers.success(t.p, t.m);
      meter.record({ ...ctx, route, model: t.m, usage: res.usage });              // tokens, ₹, latency
      await cache.maybeSet(route, req, ctx, res);
      return res;
    } catch (e) { breakers.failure(t.p, t.m, e); }
  }
  throw new Error('ALL_MODELS_FAILED');
}
```

### Degraded-mode flags (kill switches)
```python
MODE = flags.get("support_ai_mode", default="full")      # full | rag_only | faq_only | human_only
async def handle_turn(user, msg):
    if MODE == "human_only": return await handoff(user, msg, reason="AI disabled")
    intent = await route_intent(msg)
    if MODE in ("faq_only", "rag_only") and intent in ("ORDER", "PAYMENT"): return await handoff(user, msg, reason="agentic disabled")
    if MODE == "faq_only": return await faq_answer(msg)
    return await full_pipeline(user, msg, intent)
```

### Human handoff payload (agent desk gets full context)
```json
{ "conversation_id": "c_9f2", "user_id_hash": "u_7a1", "lang": "hinglish",
  "summary": "Customer's order #4521 arrived without raita; requested refund ₹40. Policy allows auto-refund up to ₹500, but customer had 3 refunds in 30 days → review required.",
  "facts": { "order_id": "4521", "missing_item": "raita", "amount_paise": 4000, "recent_refunds_30d": 3 },
  "actions_taken": ["get_order_status", "propose_refund (blocked: limit)"], "sentiment": "upset", "priority": "normal" }
```

### Shadow mode before launch
```python
async def handle_with_shadow(user, msg):
    human_reply = await human_agent_flow(user, msg)                       # current production path
    asyncio.create_task(shadow_ai(user, msg, compare_to=human_reply))     # AI runs silently; judged offline vs human
    return human_reply
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you estimate capacity and cost for an LLM feature?**
A1: Start from usage: users, conversations per user, turns per conversation and peak factors. That gives turns per second at peak. Estimate tokens per turn (system prompt, tools, retrieved context, history and output) and multiply to get tokens per day and tokens per minute at peak. Apply prices per input and output token (with cache discounts) to get cost per day and per conversation, and compare with the budget and the provider's rate limits. Then design optimizations (prompt caching, model routing, response caching, context trimming, batch APIs) and re-estimate. If self-hosting, translate tokens per second into GPU count using benchmarked throughput.

**Q2: What's an LLM gateway and why is it central at scale?**
A2: It's an internal service between your apps and model providers that standardizes requests and responses and hosts cross-cutting concerns: model aliases and routing (cheap vs capable models), retries, timeouts and provider fallback with circuit breakers, per-tenant quotas and rate limiting, response and semantic caching, prompt-cache-friendly assembly, token and cost metering and attribution, logging with PII redaction, guardrail hooks and A/B experiments on models. It decouples product code from vendors and gives one control point for reliability, cost and compliance.

**Q3: How do you keep latency low in a multi-step AI pipeline?**
A3: Set a per-stage latency budget. Run independent steps in parallel (guards, history fetch, retrieval and tool calls), use small fast models for routing and rewriting, and skip steps when unnecessary (no rewrite without history). Keep retrieval fast (ANN, filters, caches), limit context size, use prompt caching for static prefixes, stream the generation for early time-to-first-token, apply streaming-compatible guardrails, set timeouts with fallbacks, and pre-warm capacity before known spikes. Monitor p95 per stage.

**Q4: How would you make the system resilient to provider outages or rate limits?**
A4: Support at least two models or providers validated with the same prompts and evals, behind a gateway with circuit breakers and automatic failover. Apply per-tenant quotas and priority queues so live chats beat background jobs, push bulk work to batch APIs, and negotiate higher rate-limit tiers before events. Define degraded modes via feature flags (agentic off, then RAG-only, then FAQ-only, then human handoff), cache common answers, and alert on error-rate spikes. Optionally self-host a smaller fine-tuned model as an always-available fallback for core intents.

**Q5: How do you launch and govern an AI assistant safely?**
A5: Gate changes with offline evals (faithfulness, tool correctness, safety red-team, multilingual quality). Run in shadow mode against human agents, then a small A/B rollout with guardrail metrics (wrong commitments, complaint rate, escalation, CSAT, cost) before ramping. Keep humans in the loop for high-impact actions, with smooth handoff summaries. Monitor online with sampled judges and feedback, and keep kill switches and degraded modes. Ensure compliance: data residency, PII redaction, retention, audit logs of actions, DPDP consent and vendor agreements. Feed corrections back into eval datasets continuously.

---

## 🔷 Trade-offs
✅ Hosted frontier models: best quality, no GPU ops — ❌ cost per token, rate limits, residency concerns.
✅ Self-hosted fine-tuned small models: cost & control at steady volume — ❌ GPU capacity planning, MLOps.
✅ Agentic flexibility: handles complex cases — ❌ latency, cost, variance → bounded agents + workflows.
✅ Aggressive automation: lower support cost — ❌ quality/brand risk → human handoff, guardrail metrics.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token budget | Tokens allowed per request/tenant | tokens की सीमा |
| TPM | Tokens per minute (rate limit) | प्रति मिनट tokens |
| LLM gateway | Central model access layer | models की केंद्रीय परत |
| Model routing | Choose model per request | हर request का model चुनना |
| Degraded mode | Reduced functionality fallback | कम सुविधा वाला मोड |
| Shadow mode | AI runs silently for comparison | चुपचाप तुलना के लिए चलाना |
| Human handoff | Transfer to human agent | इंसानी agent को सौंपना |
| Latency budget | Time allowed per stage | हर चरण का समय |
| Continuous batching | GPU serving optimization | GPU पर batch में serve |
| Data residency | Data kept in a region | डेटा किसी देश में रखना |

---

## ⚡ 3-Line Summary
**English:**
1. Plan in tokens: users → turns/s → tokens/turn → tokens/day & TPM → cost; then cut cost with prompt caching, routing, response caching and context trimming.
2. Architecture: gateway → conversation svc → orchestrator (guards, router, workflows, bounded agents, RAG, tools, memory) → LLM gateway (routing, fallback, quotas, cache, metering) → providers/self-hosted.
3. Reliability & governance: latency budgets + streaming, multi-provider failover, degraded modes, evals in CI + online judges, shadow/A-B rollouts, human handoff, residency & audit.

**Hindi:**
1. Tokens में योजना: यूज़र → turns/s → tokens → ख़र्च; फिर caching, routing और छोटे context से ख़र्च घटाओ।
2. Architecture: gateway → conversation → orchestrator (guards, router, workflows, सीमित agents, RAG, tools, memory) → LLM gateway → providers।
3. भरोसा: latency budget + streaming, कई providers, degraded modes, evals, shadow/A-B rollout, इंसान को सौंपना, डेटा भारत में और audit।

---

## ➡️ Next Topic Suggestion
**152. Hallucination Handling** — At scale, even a 2% hallucination rate is thousands of wrong answers a day. Next: why models hallucinate and the layered techniques to detect, prevent and contain it.
