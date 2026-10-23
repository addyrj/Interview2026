# 153. Cost Optimization (Tokens)
# हिंदी में: Token Cost Optimization — LLM का बिल घटाना बिना गुणवत्ता गिराए: सही model चुनना (routing/cascade), prompt और context छोटा करना, जवाब की लंबाई सीमित, caching, batch API, बेकार calls हटाना, और ख़र्च को feature/ग्राहक के हिसाब से नापना

---

## 🔵 Simple Definition (English)
LLM cost is driven by **tokens × price per token**, summed over every call:
`cost ≈ Σ (input_tokens × input_price + output_tokens × output_price)`, minus discounts for cached input and batch processing.
**Cost optimization** reduces tokens, price per token or number of calls while keeping quality within targets. The main levers:
1. **Model selection and routing**: use the smallest model that passes evals for each task. **Cascade**: try a cheap model first and escalate only if confidence is low.
2. **Fewer calls**: deterministic code or workflows instead of LLM calls where possible, early exits and bounded agent steps.
3. **Smaller prompts**: concise system prompts, fewer or dynamic few-shot examples, trimmed or summarized history, top-k reranked context instead of 20 chunks, compact tool definitions and results.
4. **Shorter outputs**: `max_tokens`, "answer in ≤ 3 sentences", structured output instead of prose.
5. **Caching**: provider prompt caching for stable prefixes, plus exact and semantic response caches (Topic 148).
6. **Batch APIs** for offline workloads (typically ~50% cheaper).
7. **Fine-tuning or distillation** to a small model for high-volume narrow tasks, or **self-hosting** at a steady high volume.
8. **Governance**: per-feature and per-tenant budgets, quotas, cost dashboards and anomaly alerts.

## 🔵 सरल परिभाषा (Hindi)
LLM का ख़र्च = हर call में (input tokens × input क़ीमत + output tokens × output क़ीमत) का जोड़, cached input और batch पर छूट घटाकर। Cost optimization = गुणवत्ता लक्ष्य में रखते हुए tokens, प्रति-token क़ीमत या calls की संख्या घटाना।
तरीके: (1) हर काम के लिए सबसे छोटा model जो evals पास करे, cascade (पहले सस्ता, ज़रूरत पर बड़ा); (2) कम calls — जहाँ हो सके code/workflow, agent के कदम सीमित; (3) छोटे prompts — छोटा system prompt, कम उदाहरण, history का सारांश, 20 की जगह top 4–5 chunks; (4) छोटे जवाब — max_tokens, "3 वाक्यों में"; (5) caching; (6) offline काम के लिए batch API (~50% सस्ता); (7) भारी मात्रा के संकीर्ण काम के लिए fine-tuned/distilled छोटा model या self-hosting; (8) feature/ग्राहक budgets, quotas, dashboards, alerts।

---

## 🔴 Problem it Solves
AI features can quietly become one of the largest infrastructure line items:
- A support bot sending a 6k-token prompt per turn at lakhs of turns per day costs lakhs of rupees daily.
- An agent that loops 8 times with growing context multiplies costs 10×.
- Developers default to the largest model for everything ("just use the best one").
- Logging, evals and LLM-judge pipelines double the token bill unnoticed.
- **Indian unit economics**: human support costs per ticket are lower in India than in many markets, so an AI conversation must be **very cheap** (often a few rupees or less) to make business sense. Vernacular text can also cost **more tokens** per message.
Optimization keeps **cost per successful outcome** (per resolved conversation or classified ticket) below the value created, making AI features sustainable at Indian scale.

## 🔴 यह क्यों बना? (Hindi)
AI features चुपचाप सबसे बड़े infrastructure ख़र्च बन सकते हैं: हर turn पर 6k tokens × रोज़ लाखों turns = रोज़ लाखों रुपये; 8 बार घूमने वाला agent बढ़ते context के साथ 10 गुना ख़र्च; developers हर काम के लिए सबसे बड़ा model; logging, evals और LLM-judge pipelines बिना ध्यान दिए बिल दोगुना कर देती हैं।
भारत में इंसानी support का प्रति ticket ख़र्च कम है, इसलिए AI बातचीत बहुत सस्ती होनी चाहिए (अक्सर कुछ रुपये या कम); और हिंदी/क्षेत्रीय text में प्रति message ज़्यादा tokens लगते हैं। Optimization "प्रति सफल नतीजा ख़र्च" को बनाए गए मूल्य से नीचे रखता है।

---

## 🟢 How it Works — Step by Step

### Where the tokens go (typical RAG support turn)

```
System prompt           1,200 tok  ← cacheable (stable)      → prompt caching, trim verbosity
Tool definitions          800 tok  ← cacheable                → fewer/shorter tool descriptions per route
Few-shot examples         900 tok  ← cacheable                → fewer examples or dynamic selection
Retrieved chunks        2,400 tok  ← per request              → rerank to top 4, shorter chunks, dedupe
Conversation history    1,000 tok  ← grows each turn          → window + running summary
User message               60 tok
OUTPUT                    300 tok  ← most expensive per token  → concise style, max_tokens, structured
Total ≈ 6.3k input + 300 output per turn; × turns/day × price = daily bill
```

### Lever 1: routing & cascades

```
Router (tiny/fast model or rules) → intent:
  FAQ / status / simple classification → small model (or no LLM: template + tool data)
  normal support answer → mid model
  complex multi-step/agentic or escalated → large model
Cascade: small model answers + self-reported confidence/validator → if low or validation fails → large model
Measure: % traffic per tier, quality per tier (evals), cost per resolved conversation
```

### Lever 2: avoid calls entirely

```
Deterministic workflows for known paths (refund status = tool call + template, no LLM needed)
Regex/rules for trivial intents ("hi", "thanks"), cached FAQ answers, UI buttons instead of free text
Early exits: abstain when retrieval empty; don't run judges on every request (sample 5%)
Agent step limits & loop detection (Topic 141); don't re-run the same tool/LLM call
```

### Lever 3–4: prompt & output diet

```
Rewrite system prompts for brevity (keep reasons, cut repetition); version & eval after trimming
Move static content into cacheable prefix; per-route prompts (don't send payment rules to FAQ route)
Context: top-k after rerank (4–6), chunk size tuned, remove boilerplate, compress tool results to needed fields
History: last N turns + summary; drop resolved sub-threads
Output: "≤ 3 sentences", bullet format, JSON fields only; set max_tokens; stop sequences
Language: concise replies in Hindi/regional languages matter more (more tokens per word)
```

### Lever 5–7: caching, batch, smaller models

```
Prompt caching (stable prefix) → large input discounts on repeated prefixes (Topic 148)
Response/semantic cache for FAQs, esp. during sale spikes
Batch APIs for offline jobs: summaries, tagging, evals, embeddings backfills (≈ 50% off, hours latency)
Fine-tune/distill a small model for high-volume narrow tasks (ticket tagging, extraction) (Topic 150)
Self-host open models when volume is high & steady and residency matters (GPU utilization must be high
  to beat API prices — include ops cost)
```

### Lever 8: governance

```
Cost attribution: tokens & ₹ per request tagged by feature, tenant, route, model, prompt version
Budgets: per tenant/plan quotas (free plan: 20 AI chats/day), per-request max tokens, per-agent step budgets
Alerts: daily spend vs budget, anomaly (sudden 3× tokens/request), loops, prompt size regressions in CI
Unit economics: cost per resolved conversation vs human-handled cost; review monthly
```

## 🟢 कैसे काम करता है? (Hindi)
1. Tokens कहाँ जाते हैं: system prompt 1,200 + tools 800 + उदाहरण 900 (ये तीनों स्थिर — cache लायक) + retrieved chunks 2,400 + history 1,000 + सवाल 60 + output 300 (सबसे महँगा प्रति token) → हर turn ~6.3k input; × रोज़ के turns × क़ीमत = बिल।
2. Routing/cascade: FAQ/status/सरल → छोटा model या बिना LLM (template + tool डेटा), आम जवाब → mid model, जटिल/agent → बड़ा; cascade — पहले छोटा, confidence या जाँच कम तो बड़ा; हर tier का traffic, गुणवत्ता, प्रति हल बातचीत ख़र्च नापो।
3. Calls ही हटाओ: refund status जैसे तय रास्ते पर tool + template, "hi/thanks" के लिए नियम, FAQ cache, बटन; retrieval ख़ाली तो जल्दी "पता नहीं", judges सिर्फ़ 5% पर, agent के कदम सीमित।
4. Prompt/output डाइट: छोटा system prompt (कारण रखो, दोहराव हटाओ), स्थिर हिस्सा cache prefix में, हर route का अलग prompt, rerank के बाद 4–6 chunks, tool नतीजों में सिर्फ़ ज़रूरी fields, history = आख़िरी N + सारांश, "3 वाक्यों में", max_tokens; हिंदी में छोटे जवाब और ज़रूरी।
5. Caching, batch API (offline काम ~50% सस्ता), संकीर्ण भारी काम के लिए fine-tuned/distilled छोटा model, स्थिर भारी मात्रा पर self-host (GPU का पूरा इस्तेमाल हो तभी सस्ता); governance — feature/tenant/route/model के हिसाब से ₹, quotas, alerts, CI में prompt आकार की जाँच, और AI बनाम इंसान का प्रति हल ख़र्च।

---

## 🟡 Real World Example

**Provider discounts** — Anthropic (Message Batches) and OpenAI (Batch API) offer roughly 50% discounts for asynchronous batch jobs. Prompt caching cuts cost on repeated long prefixes substantially (Anthropic cites up to 90% cost reduction for long prompts). These are some of the easiest wins.

**Model tiers** — providers ship families at different price points (e.g., Claude Haiku/Sonnet/Opus). Production systems commonly route most traffic to small or mid tiers and reserve the top tier for hard cases, often achieving multi-fold savings with minimal quality loss on evals.

**Distillation and fine-tuning for volume** — companies with high-volume classification and extraction (support tagging, catalog attribute extraction for e-commerce sellers) commonly fine-tune or distill smaller models, reducing per-item cost and latency dramatically versus prompting a large model.

**Indian unit economics** — Indian SaaS and consumer companies evaluate AI support against relatively low human costs per ticket. Teams typically target very low per-conversation AI costs through routing, workflows for common intents, caching and concise vernacular responses before scaling to millions of users.

## 🟡 Real Example Hindi में
Anthropic (Message Batches) और OpenAI (Batch API) async batch पर ~50% छूट देते हैं; prompt caching लंबे दोहराए prefixes पर ख़र्च बहुत घटाता है (Anthropic के अनुसार 90% तक) — सबसे आसान फ़ायदे; Haiku/Sonnet/Opus जैसे tiers में ज़्यादातर traffic छोटे/मध्यम पर और कठिन cases बड़े पर — evals पर कम गिरावट के साथ कई गुना बचत।
भारी मात्रा वाले classification/extraction (support tagging, sellers के catalog attributes) के लिए fine-tuned/distilled छोटे models — प्रति item ख़र्च और देर बहुत कम; भारतीय कंपनियाँ AI support को कम इंसानी प्रति-ticket ख़र्च से तौलती हैं — routing, workflows, caching और छोटे vernacular जवाबों से बहुत कम प्रति-बातचीत ख़र्च का लक्ष्य।

---

## 🟠 My Stack Example

### Cascade: small model first, escalate on low confidence or failed validation
```python
class Draft(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    needs_escalation: bool

async def cascade_answer(question, sources):
    small = await structured_call("claude-haiku-5-5", CASCADE_SYSTEM, render(question, sources), Draft)
    if small.confidence == "high" and not small.needs_escalation and not validate_against_sources(small.answer, sources):
        metrics.inc("cascade_tier", {"tier": "small"}); return small.answer
    metrics.inc("cascade_tier", {"tier": "mid"})
    return await generate_answer(question, sources, model="claude-sonnet-5-5")   # escalate (~minority of traffic)
# validate_against_sources returns a list of issues (empty = OK) — e.g., citation & numeric checks (Topic 152)
```

### Token budget enforcement per request (context assembly)
```python
def assemble_context(system, tools, history, chunks, question, budget=4500):
    used = count_tokens(system) + count_tokens(tools) + count_tokens(question) + 300   # reserve for output
    hist = summarize_if_needed(history, max_tokens=600)                                 # window + summary
    used += count_tokens(hist)
    picked = []
    for c in chunks:                                                                     # already reranked, best first
        t = count_tokens(c.text)
        if used + t > budget: break
        picked.append(c); used += t
    return hist, picked                                                                  # log 'used' per request → dashboards
```

### Per-route prompts & tools (don't send everything everywhere)
```python
ROUTE_CONFIG = {
  "FAQ":     {"model": "claude-haiku-5-5",  "system": FAQ_SYSTEM_SHORT, "tools": [],                 "max_tokens": 200},
  "ORDER":   {"model": "claude-sonnet-5-5", "system": ORDER_SYSTEM,     "tools": ORDER_TOOLS,        "max_tokens": 300},
  "PAYMENT": {"model": "claude-sonnet-5-5", "system": PAYMENT_SYSTEM,   "tools": PAYMENT_TOOLS,      "max_tokens": 300},
  "COMPLEX": {"model": "claude-opus-5-5",   "system": COMPLEX_SYSTEM,   "tools": ALL_SUPPORT_TOOLS,  "max_tokens": 600},
}
```

### Offline jobs via Message Batches (≈ half price)
```python
reqs = [{"custom_id": f"sum-{c.id}", "params": {"model": "claude-haiku-5-5", "max_tokens": 120,
         "messages": [{"role": "user", "content": f"Summarize this support chat in 2 lines for the agent CRM:\n{c.transcript}"}]}}
        for c in yesterdays_conversations]
batch = client.messages.batches.create(requests=reqs)       # results within hours; store in CRM
```

### Budgets & alerts (tenant quotas + anomaly detection)
```python
async def enforce_budget(tenant_id, est_tokens):
    spent = await redis.incrby(f"tok:{tenant_id}:{today()}", est_tokens)
    if spent > PLAN_LIMITS[tenant_plan(tenant_id)]:
        raise QuotaExceeded("Daily AI limit reached for your plan")

# SQL: daily cost by feature, with tokens/request trend to catch prompt bloat
# SELECT feature, model, sum(cost_inr), avg(input_tokens) FROM llm_calls WHERE ts > now()-'1 day' GROUP BY 1,2 ORDER BY 3 DESC;
```

### CI check: fail PR if a prompt grows too much
```python
def test_prompt_size_budget():
    for name, prompt in ALL_PROMPTS.items():
        assert count_tokens(prompt) <= PROMPT_BUDGETS[name], f"{name} exceeds token budget"
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the biggest levers for reducing LLM cost?**
A1: Model routing and cascades (the smallest model that passes evals per task), avoiding calls via deterministic workflows and caching, shrinking input (concise and cacheable system prompts, fewer examples, per-route tools, reranked top-k context, summarized history), capping output length and preferring structured output, provider prompt caching for stable prefixes, response and semantic caching for repeated questions, batch APIs for offline work, bounded agent loops, and fine-tuning or distilling small models for high-volume narrow tasks. Governance (attribution, budgets, alerts) makes it sustainable.

**Q2: How do you design a model cascade?**
A2: Route each request first to a cheap, fast model, with a prompt that also produces a confidence signal or passes deterministic validators (schema, citations, numeric checks). Accept the small model's answer when confidence is high and validation passes, otherwise escalate to a larger model, possibly with the small model's draft as context. Tune escalation thresholds on an eval set to hit quality targets, and monitor the escalation rate, quality per tier and total cost per resolved request.

**Q3: How do you control costs in agentic systems?**
A3: Bound steps, time and tokens per task, detect loops, and keep context compact (summaries and tool-result digests rather than full outputs). Give agents only route-relevant tools, use cheaper models for sub-agents and routine steps, run deterministic workflows for known sub-paths, cache tool results within a task, and cap parallel fan-out in multi-agent setups. Attribute costs per agent and task, and alert on anomalies like unusually long trajectories.

**Q4: When does self-hosting an open model save money?**
A4: When volume is high and steady enough to keep GPUs highly utilized, a smaller open or fine-tuned model meets quality for the task, and you have MLOps capacity for serving (vLLM with continuous batching, autoscaling, monitoring) or residency requirements. Compare the total cost (GPU instances, utilization, engineering and on-call time, model upgrades) per million tokens against API prices including discounts. For spiky or low volume, or tasks needing frontier quality, hosted APIs are usually cheaper and simpler.

**Q5: How do you make sure cost cuts don't hurt quality?**
A5: Treat every optimization like a change to production quality: run it against the eval suite (task accuracy, faithfulness, safety, language quality) and compare with the baseline. Roll out gradually behind flags with online quality metrics (feedback, escalations, recontact rate), and track cost per successful outcome rather than raw cost. Keep the ability to route hard segments back to stronger models. Cheaper models or shorter prompts often fail on specific segments (Hindi, rare intents), so check per-segment metrics.

---

## 🔷 Trade-offs
✅ Smaller models/routing: big savings — ❌ quality risk on hard segments (needs evals & escalation).
✅ Aggressive context trimming: fewer tokens — ❌ may drop needed evidence → more "I don't know".
✅ Batch APIs: ~50% cheaper — ❌ async latency (hours).
✅ Self-hosting: low marginal cost at scale — ❌ fixed GPU & ops cost, utilization risk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Input/output tokens | Billed prompt/response tokens | बिल होने वाले tokens |
| Model routing | Choosing model per task | काम के हिसाब से model |
| Cascade | Cheap first, escalate if needed | पहले सस्ता, फिर बड़ा |
| Context budget | Max input tokens per request | input की सीमा |
| Prompt caching | Discounted repeated prefixes | दोहराए prefix पर छूट |
| Batch API | Async discounted processing | सस्ता async काम |
| Distillation | Small model mimics large | छोटा model बड़े जैसा |
| Cost attribution | Spend per feature/tenant | ख़र्च किसका |
| Unit economics | Cost per successful outcome | प्रति सफल नतीजा ख़र्च |
| Quota | Usage limit per tenant/plan | उपयोग की सीमा |

---

## ⚡ 3-Line Summary
**English:**
1. Cost = tokens × price per call; cut tokens (lean, per-route, cached prompts; reranked top-k; summarized history; short outputs) and calls (workflows, caching, early exits, bounded agents).
2. Cut price: route/cascade to smaller models, prompt caching, batch APIs, fine-tuned/distilled small models, self-host only at high steady volume.
3. Govern: attribute ₹ per feature/tenant, budgets & quotas, anomaly alerts, CI prompt-size checks — and verify quality with evals per segment.

**Hindi:**
1. ख़र्च = tokens × क़ीमत; tokens घटाओ (छोटे, route के हिसाब से, cache वाले prompts; top-k chunks; सारांश; छोटे जवाब) और calls घटाओ।
2. क़ीमत घटाओ: छोटे models पर routing/cascade, prompt caching, batch API, fine-tuned छोटा model, स्थिर भारी मात्रा पर self-host।
3. नियंत्रण: feature/tenant के हिसाब से ₹, quotas, alerts, CI में prompt आकार — और evals से गुणवत्ता की जाँच।

---

## ➡️ Next Topic Suggestion
**154. Streaming Responses** — Users judge AI speed by how fast the first words appear. Next: streaming tokens end to end (provider SSE → backend → web and React Native clients), cancellation, and streaming with tools and guardrails.
