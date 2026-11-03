---

# 593. Build Cost Tracker
# हिंदी में: Cost Tracker बनाना

---

## 🔵 Simple Definition (English)
A cost tracker records every LLM call (model, input tokens, output tokens, cached tokens), converts it to dollars using a price table, and enforces budgets per user or team. It answers: "who spent how much, on which model?"

## 🔵 सरल परिभाषा (Hindi)
Cost tracker हर LLM call (model, input tokens, output tokens, cached tokens) record करता है, price table से dollars में convert करता है, और हर user/team का budget enforce करता है। यह बताता है: "किसने, किस model पर, कितना खर्च किया?"

---

## 🔴 Problem it Solves
LLM bills grow silently. One buggy loop or one heavy user can burn the monthly budget in a day. Provider dashboards show only totals, not per-feature or per-user spend. Without tracking you cannot do chargeback, alerts, or rate limits by cost.

## 🔴 यह क्यों बना? (Hindi)
LLM का bill चुपचाप बढ़ता है। एक buggy loop या एक heavy user पूरे महीने का budget एक दिन में खत्म कर सकता है। Provider dashboard सिर्फ total दिखाता है, per-user या per-feature नहीं। Tracking के बिना alerts और budget limits नहीं लग सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → LLM call finishes; read usage (input, output, cached tokens) from response
Step 2 → Look up price per 1M tokens for that model
Step 3 → cost = fresh_in*p_in + cached*p_cache + out*p_out
Step 4 → Lock, check user's budget, add to running total (atomic)
Step 5 → Store a UsageRecord (user, model, tokens, cost, timestamp)
Step 6 → Report: group by user / model / feature; alert on thresholds
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM call खत्म होने पर response से usage पढ़ो
Step 2 → उस model का price per 1M tokens देखो
Step 3 → cost = fresh_in*p_in + cached*p_cache + out*p_out
Step 4 → Lock लगाओ, user का budget check करो, total में जोड़ो
Step 5 → UsageRecord save करो
Step 6 → Report बनाओ और threshold पर alert भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs brokers upload invoices; each classification call uses ~2,000 input and ~300 output tokens. The tracker tags each call with `broker_id` and gives each broker a daily budget. When a broker's bulk upload hits the limit, the API returns HTTP 429 instead of silently running up the bill.

**Zomato/Amazon style**: a support-bot team is charged back per chat session; large-model calls for refund disputes are tracked separately from small-model FAQ calls.

## 🟡 Real Example Hindi mein
**Tariff System**: Brokers invoices upload करते हैं; हर call में ~2,000 input और ~300 output tokens लगते हैं। Tracker हर call पर `broker_id` tag करता है और daily budget लगाता है। Limit पूरी होने पर API HTTP 429 देती है।

**Zomato/Amazon**: Support bot की हर chat session का cost team को charge होता है; refund disputes के large-model calls अलग track होते हैं।

---

## 💻 Code Example — Basic
Full solution: `main.py` (runs offline, prices are illustrative).

```python
# Pure-Python cost formula (prices are illustrative USD per 1M tokens)
PRICE_IN: float = 0.15            # price per 1M input tokens
PRICE_OUT: float = 0.60           # price per 1M output tokens


def cost(inp: int, out: int) -> float:
    """Return dollars for one call."""
    if inp < 0 or out < 0:                      # reject impossible values
        raise ValueError("tokens must be >= 0")
    return (inp * PRICE_IN + out * PRICE_OUT) / 1_000_000  # scale to per-token


print(f"{cost(500, 200):.6f}")                  # 0.000195 (500*0.15+200*0.60)/1e6
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
blocked: amit would exceed $0.0010
{'amit': {'small-model': 0.000195}, 'zomato-svc': {'large-model': 0.00945}}
```
Key parts in `main.py`:
```python
# Core of CostTracker.record (excerpt; see main.py for the whole file)
async def record(self, user: str, model: str, inp: int, out: int, cached: int = 0):
    cost = self.compute_cost(model, inp, out, cached)   # validate + price
    async with self._lock:                              # atomic check-and-add
        limit = self.budgets.get(user)                  # per-user limit
        if limit is not None and self._spent[user] + cost > limit:
            raise BudgetExceeded(f"{user} would exceed ${limit:.4f}")
        self._spent[user] += cost                       # update running total
```

---

## 🟠 FastAPI Integration
Wrap the LLM call, read `usage`, record it, and map `BudgetExceeded` to HTTP 429.

```python
from fastapi import FastAPI, HTTPException
from main import CostTracker, BudgetExceeded            # our module

app = FastAPI()
tracker = CostTracker(budgets={"broker-1": 5.0})        # USD per user


@app.post("/classify")
async def classify(user: str, text: str) -> dict:
    # Pretend LLM call; real code reads response.usage.* instead
    inp, out = len(text) // 4, 50
    try:
        rec = await tracker.record(user, "small-model", inp, out)
    except BudgetExceeded as e:                         # over budget -> 429
        raise HTTPException(status_code=429, detail=str(e))
    except KeyError as e:                               # unknown model -> 500
        raise HTTPException(status_code=500, detail=str(e))
    return {"cost_usd": rec.cost_usd}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain callbacks expose token usage per call; hook the tracker into `on_llm_end`.

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class CostCallback(BaseCallbackHandler):
    def __init__(self, user: str) -> None:
        self.user = user                                 # who to bill
        self.calls: list[dict] = []                      # collect usage

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        usage = (response.llm_output or {}).get("token_usage", {})  # provider-dependent
        self.calls.append({"user": self.user, **usage})  # later feed to tracker
```
In LangGraph, attach the callback via `config={"callbacks": [CostCallback("u1")]}` so every node is counted.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Check budget and update it in two separate steps (race condition).
✅ Correct: do check-and-add inside one lock (or one atomic Redis `INCRBYFLOAT`).

```python
# Wrong: two concurrent requests both pass the check
if spent[user] + cost <= limit:
    await call_llm()
    spent[user] += cost
# Right: reserve first inside a lock, then call, then reconcile
```

❌ Mistake 2: Billing cached tokens at the full input price.
✅ Correct: price cached tokens separately (cache reads are cheaper at most providers).

❌ Mistake 3: Hard-coding prices forever. Keep prices in config and store the price version with each record.

---

## 🧠 Tricky Interview Question
**Q**: "Your tracker shows $100/day but the provider invoice says $140. Why?"

**Answer**: Typical gaps: (1) retries and failed/timeout calls that still consumed tokens but never reached your recorder; (2) streaming calls where usage was not read at the end; (3) hidden tokens (reasoning/thinking tokens, tool schemas, system prompts) not in your estimates; (4) stale price table; (5) other services sharing the API key. Fix: record from the provider's reported `usage`, log in a `finally`, and reconcile daily against the invoice.

---

## ⚫ Interview Questions + Answers

Q1: Why track input and output tokens separately?
A1: They have different prices; output tokens usually cost several times more than input.

Q2: What is a UsageRecord for?
A2: An immutable audit row: who, which model, tokens, cost, time. Reports and alerts are built from these rows.

Q3: How would you enforce a monthly budget across many app servers?
A3: Keep the counter in shared storage (Redis `INCRBYFLOAT` with a monthly key and TTL), not in process memory.

Q4: How do you handle cost when a request streams?
A4: Request usage in the final stream chunk (provider option) or count tokens yourself; record in `finally` so cancelled streams are still billed.

Q5 (Hard): Design pre-call cost control so a user cannot overspend even with concurrent requests.
A5: Estimate worst-case cost before the call (input tokens + `max_tokens` x output price), atomically reserve it from the budget, make the call, then refund the difference with the actual usage. This prevents overshoot at the cost of temporarily locking some budget.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-user or multi-tenant LLM apps
- Chargeback to teams, free-tier limits
- Production systems with a real budget

❌ Avoid when:
- One-off notebook experiments (provider dashboard is enough)

---

## 📊 Visual Diagram
```
 Request ──► LLM call ──► usage(in,out,cached)
                              │
                              ▼
                   ┌────────────────────┐
                   │  price table       │
                   └─────────┬──────────┘
                             ▼
              ┌──── lock ── budget check ────┐
              │ ok                  exceeded │
              ▼                              ▼
        UsageRecord store             BudgetExceeded → HTTP 429
              │
              ▼
     reports / alerts / dashboards
```

---

## 💰 Cost Impact
The tracker itself costs almost nothing (microseconds, no tokens). Its value: finding savings. Typical findings: one endpoint with a long system prompt (use prompt caching), a large model used where a small one works (route), unbounded outputs (set `max_tokens`). Example from `main.py`: 500 in + 200 out on the small model costs $0.000195; 2,000 in (1,500 cached) + 500 out on the large model costs $0.00945 (illustrative prices).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Usage record | One row per LLM call | हर call की entry |
| Budget | Spending limit | खर्च की सीमा |
| Chargeback | Billing teams for their usage | Team से usage का पैसा लेना |
| Cached tokens | Input reused from cache, cheaper | Cache से आए सस्ते tokens |
| Atomic | Done as one indivisible step | एक साथ पूरा होने वाला step |

---

## ⚡ 3-Line Summary
English: Record usage from every call, convert with a price table, and enforce budgets atomically. Track by user, model and feature to find savings. Reconcile with the provider invoice.
Hindi: हर call का usage record करो और price table से cost निकालो। Budget atomically enforce करो। User, model, feature के हिसाब से track करके बचत खोजो और invoice से मिलान करो।

---

## ➡️ Next Topic
**594. Build Token Counter** — the cost tracker needs accurate token counts before the call; next we build a counter with tiktoken and a fallback.
