---

# 566. Cost Monitoring in Production
# हिंदी में: Production में Cost Monitoring

---

## 🔵 Simple Definition (English)
Cost monitoring means tracking what every LLM call costs (tokens x price), attributing it to a user, tenant, or feature, and alerting or blocking when spending exceeds a budget. It turns a surprise monthly bill into a real-time number.

## 🔵 सरल परिभाषा (Hindi)
Cost monitoring का मतलब हर LLM call की cost (tokens x price) track करना, उसे user, tenant या feature से जोड़ना, और budget पार होने पर alert या block करना। इससे महीने के अंत का surprise bill real-time number बन जाता है।

---

## 🔴 Problem it Solves
LLM billing is usage-based and invisible inside code. A retry loop, a huge prompt, an agent stuck in a loop, or one abusive user can burn thousands of dollars in a day. Provider dashboards show only totals, not "which feature or customer". Finance asks "why did cost triple?" and nobody can answer.

## 🔴 यह क्यों बना? (Hindi)
LLM billing usage-based है और code के अंदर दिखता नहीं। Retry loop, बहुत बड़ा prompt, loop में फँसा agent या एक abusive user एक दिन में हज़ारों डॉलर जला सकता है। Provider dashboard सिर्फ total दिखाता है, "कौन सा feature/customer" नहीं। Finance पूछे "cost तीन गुना क्यों?" तो जवाब नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → After each LLM call, read usage (prompt_tokens, completion_tokens) from the response
Step 2 → Look up the model's price table (per 1M tokens, input and output separately)
Step 3 → cost = in_tokens * in_price/1e6 + out_tokens * out_price/1e6
Step 4 → Tag with dimensions: tenant, user, feature, model, prompt_version
Step 5 → Store/aggregate (Redis counters, Prometheus, warehouse table)
Step 6 → Compare with budgets (per user/day, per tenant/month, global/day)
Step 7 → Soft limit = alert; hard limit = degrade (cheaper model) or block (HTTP 429)
Step 8 → Weekly review: top cost drivers, optimisation backlog
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर LLM call के बाद response से usage (prompt_tokens, completion_tokens) पढ़ो
Step 2 → Model की price table देखो (per 1M tokens, input और output अलग)
Step 3 → cost = in_tokens * in_price/1e6 + out_tokens * out_price/1e6
Step 4 → Tags जोड़ो: tenant, user, feature, model, prompt_version
Step 5 → Store/aggregate करो (Redis counters, Prometheus, warehouse table)
Step 6 → Budgets से compare करो (per user/day, per tenant/month, global/day)
Step 7 → Soft limit = alert; hard limit = सस्ता model या block (HTTP 429)
Step 8 → हर हफ्ते top cost drivers देखो और optimisation करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Cost per classification averages $0.0004. One customer uploads 40,000 items overnight with a huge system prompt, and cost per tenant jumps 50x. The per-tenant daily budget alert fires at 80%; at 100% the API switches that tenant to a cheaper model and queues the rest for batch processing at lower cost.

**Amazon-style**: Product-review summaries are tagged by feature; cost monitoring shows 70% of spend comes from re-summarising unchanged reviews, which caching removes.

## 🟡 Real Example Hindi mein
**Tariff System**: औसत cost प्रति classification $0.0004 है। एक customer रात भर 40,000 items बड़े system prompt के साथ upload करता है और उस tenant की cost 50x हो जाती है। Per-tenant daily budget का 80% पर alert आता है; 100% पर API उस tenant को सस्ते model पर डालती है और बाकी को सस्ते batch processing के लिए queue करती है।

**Amazon-style**: Product-review summaries feature से tag हैं; cost monitoring दिखाती है कि 70% खर्च बिना बदले reviews को दोबारा summarise करने से है, जिसे caching हटा देती है।

---

## 💻 Code Example — Basic
```python
# Basic cost tracker with budget (pure Python, runs directly)
from collections import defaultdict              # per-key totals

# Illustrative prices in USD per 1M tokens (check the provider's pricing page for real values)
PRICES: dict[str, tuple[float, float]] = {
    "small-model": (0.15, 0.60),                 # (input, output)
    "large-model": (3.00, 15.00),
}


def call_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    if model not in PRICES:                      # fail loudly on unknown model
        raise KeyError(f"no price for {model}")
    p_in, p_out = PRICES[model]                  # unpack prices
    return tokens_in * p_in / 1_000_000 + tokens_out * p_out / 1_000_000


class CostTracker:
    def __init__(self, daily_budget_usd: float) -> None:
        self.budget = daily_budget_usd                       # allowed spend
        self.spent: dict[str, float] = defaultdict(float)    # tenant -> spend

    def record(self, tenant: str, model: str, tin: int, tout: int) -> float:
        cost = call_cost(model, tin, tout)                   # compute cost
        self.spent[tenant] += cost                           # accumulate
        return cost

    def status(self, tenant: str) -> str:
        used = self.spent[tenant] / self.budget              # fraction of budget
        if used >= 1.0:
            return "BLOCK"                                   # hard limit
        if used >= 0.8:
            return "WARN"                                    # soft limit
        return "OK"


t = CostTracker(daily_budget_usd=0.01)                       # tiny budget for demo
for _ in range(30):                                          # simulate calls
    t.record("acme", "small-model", 500, 120)                # ~ $0.000147 each
print(round(t.spent["acme"], 6), t.status("acme"))           # prints total and status
```

## 💻 Code Example — Advanced
```python
# Production style: async Redis-backed budgets, atomic increments, model downgrade
from __future__ import annotations
import datetime as dt                            # date keys per day
import logging                                   # logging
from dataclasses import dataclass                # price container

import redis.asyncio as redis                    # real async Redis client (pip install redis)

log = logging.getLogger("cost")


@dataclass(frozen=True)
class Price:
    inp: float                                   # USD per 1M input tokens
    out: float                                   # USD per 1M output tokens


PRICES = {"small-model": Price(0.15, 0.60), "large-model": Price(3.0, 15.0)}   # illustrative


class BudgetExceeded(Exception):
    """Raised when a tenant has used its hard budget."""


class CostGuard:
    def __init__(self, r: redis.Redis, daily_budget_usd: float) -> None:
        self.r = r                               # redis connection
        self.budget = daily_budget_usd           # per tenant per day

    @staticmethod
    def _key(tenant: str) -> str:
        return f"cost:{tenant}:{dt.date.today().isoformat()}"   # one counter per day

    async def spent(self, tenant: str) -> float:
        raw = await self.r.get(self._key(tenant))               # may be None
        return float(raw) if raw else 0.0

    async def choose_model(self, tenant: str, wanted: str) -> str:
        """Before the call: block, downgrade, or allow."""
        used = await self.spent(tenant)
        if used >= self.budget:
            raise BudgetExceeded(tenant)                        # hard stop
        if used >= 0.8 * self.budget and wanted == "large-model":
            log.warning("downgrading %s to small-model", tenant)
            return "small-model"                                # degrade gracefully
        return wanted

    async def record(self, tenant: str, model: str, tin: int, tout: int) -> float:
        p = PRICES[model]                                       # KeyError = config bug
        cost = tin * p.inp / 1e6 + tout * p.out / 1e6
        key = self._key(tenant)
        await self.r.incrbyfloat(key, cost)                     # atomic across replicas
        await self.r.expire(key, 3 * 24 * 3600)                 # keep 3 days
        return cost
```

---

## 🟠 FastAPI Integration
Check the budget before the call, record real usage after it, and return cost in the response. Map `BudgetExceeded` to HTTP 429.

```python
from fastapi import FastAPI, HTTPException, Header      # framework

app = FastAPI()
guard = CostGuard(redis.from_url("redis://localhost:6379"), daily_budget_usd=5.0)


@app.post("/classify")
async def classify(item: str, x_tenant: str = Header(...)) -> dict:
    try:
        model = await guard.choose_model(x_tenant, "large-model")   # may downgrade
    except BudgetExceeded:
        raise HTTPException(status_code=429, detail="daily AI budget exhausted")
    # resp = await client.chat.completions.create(model=..., messages=[...])
    tin, tout = 600, 80                                            # use resp.usage in real code
    cost = await guard.record(x_tenant, model, tin, tout)          # record actual usage
    return {"model": model, "cost_usd": round(cost, 6)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain exposes `usage_metadata` on `AIMessage` (input_tokens, output_tokens) for supporting providers; LangSmith aggregates cost per run and per tag. In LangGraph, sum usage over all nodes of one run: a single user request may trigger 5-10 LLM calls, so budget at the request (graph run) level and also set `recursion_limit` to cap runaway loops.

```python
msg = await llm.ainvoke("HS code for laptop?")              # llm = ChatOpenAI(...)
usage = msg.usage_metadata or {}                             # {"input_tokens":..,"output_tokens":..}
await guard.record("acme", "small-model",
                   usage.get("input_tokens", 0), usage.get("output_tokens", 0))
# graph.ainvoke(state, config={"recursion_limit": 10})       # cap agent loops (limits cost)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Estimating cost from prompt length only, ignoring output tokens (output is often 3-5x pricier per token).
✅ Correct: use `usage` from the response, with separate input and output prices.

```python
# Wrong
cost = len(prompt) / 4 * 0.15 / 1e6
# Right
cost = u.prompt_tokens * 0.15 / 1e6 + u.completion_tokens * 0.60 / 1e6   # illustrative prices
```

❌ Mistake 2: Only a global budget. One tenant can eat it all.
✅ Correct: budgets per tenant/user plus a global kill switch.

❌ Mistake 3: Ignoring hidden costs: retries, embeddings, reranker calls, judge calls, and agent loops.

---

## 🧠 Tricky Interview Question
**Q**: "Your per-request cost looks flat, but the monthly bill doubled. Why?"

**Answer**: Volume or hidden multipliers. Check: retries (failures billed too in some cases), agent loops producing more calls per request, a background job (re-embedding, evals) not tagged to a feature, cache hit rate falling (prompt prefix changed), longer conversation histories (cost per turn grows with context), and output length growth. Track cost per business event (per classification, per resolved ticket) and per feature, not just per call.

---

## ⚫ Interview Questions + Answers

Q1: How is LLM API cost calculated?
A1: input_tokens x input price + output_tokens x output price, usually per 1M tokens. Some providers discount cached input tokens.

Q2: Where do you get token counts in production?
A2: From the provider response `usage` field (authoritative). Use a tokenizer such as tiktoken only for pre-call estimates.

Q3: What dimensions should costs be tagged with?
A3: Tenant, user, feature/endpoint, model, prompt version, environment, and request ID.

Q4: How do you enforce a budget without breaking user experience?
A4: Soft limit alerts first, then graceful degradation (cheaper model, shorter outputs, cached answers, queue for batch), and only then hard block with a clear message.

Q5: (Hard) Design a cost-control system for a multi-tenant AI SaaS.
A5: Gateway that counts tokens per tenant in Redis (atomic), pre-checks budgets using estimated tokens, post-records actual usage, supports plan-based quotas, anomaly detection (spend 3x of the 7-day average), per-feature dashboards, automatic model routing by difficulty, and monthly invoices built from the usage table. Include idempotency so retries do not double-count.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Usage-based AI features, multi-tenant products, agents, or any uncapped input

❌ Avoid when:
- Tiny internal tool with a fixed provider-side spending cap (a simple cap may be enough)

---

## 📊 Visual Diagram
```
 Request ─► Pre-check budget ──block──► 429
               │ ok / downgrade
               ▼
            LLM call ─► usage {in: 600, out: 80}
               │
               ▼
      cost = in*p_in + out*p_out
               │
   ┌───────────┼─────────────┐
   ▼           ▼             ▼
 Redis      Prometheus    Warehouse
 (budget)   (dashboard)   (billing, analysis)
               │
               ▼
        Alert at 80% / Block at 100%
```

---

## 💰 Cost Impact
- Monitoring prevents runaway spend. Illustrative: an agent loop of 50 calls x 4,000 tokens on a large model could cost far more than a single call; a budget cap stops it.
- Optimise: route easy queries to small models, cache repeated answers, trim prompts, set `max_tokens`, use provider prompt caching for stable prefixes, use batch APIs for non-urgent work, cap agent steps.
- Always keep price tables in config, versioned, since prices change. Prices shown here are illustrative.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Usage | Token counts returned by API | API से मिले token counts |
| Budget | Max allowed spend | अधिकतम खर्च सीमा |
| Soft limit | Warning threshold | चेतावनी सीमा |
| Hard limit | Blocking threshold | रोकने वाली सीमा |
| Attribution | Assigning cost to tenant/feature | Cost को tenant/feature से जोड़ना |
| Downgrade | Switch to cheaper model | सस्ते model पर जाना |

---

## ⚡ 3-Line Summary
English: Compute cost from real token usage, tag it by tenant and feature, and store it in fast counters. Enforce soft and hard budgets with graceful degradation before blocking. Watch hidden multipliers: retries, agent loops, long histories.
Hindi: असली token usage से cost निकालो, tenant और feature से tag करो और तेज़ counters में रखो। Block करने से पहले soft/hard budgets और सस्ते model पर degrade करो। छुपे multipliers देखो: retries, agent loops, लंबी history।

---

## ➡️ Next Topic
**567. Rate Limiting AI API** — protect both your budget and the provider quota by limiting requests and tokens per user.
