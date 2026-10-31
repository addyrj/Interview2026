---

# 434. Cost Tracking per Request
# हिंदी में: हर Request की Cost Tracking

---

## 🔵 Simple Definition (English)
Cost tracking per request means computing the dollar cost of every LLM call from the token usage returned by the API (`input_tokens x input_price + output_tokens x output_price`), then tagging it with user, feature, model and prompt version so you can see who and what spends money.

## 🔵 सरल परिभाषा (Hindi)
Cost tracking per request का मतलब है API से मिले token usage से हर LLM call की dollar cost निकालना (`input_tokens x input_price + output_tokens x output_price`) और उसे user, feature, model और prompt version के साथ tag करना ताकि पता चले कौन और क्या पैसा खर्च कर रहा है।

---

## 🔴 Problem it Solves
- The monthly provider invoice is one big number; it cannot tell you which feature or customer caused the spike.
- Agents and retries multiply calls; one user request may trigger 8 LLM calls.
- Without per-request cost you cannot set pricing, quotas or budgets, or prove ROI.

## 🔴 यह क्यों बना? (Hindi)
- Monthly invoice एक बड़ा number है, यह नहीं बताता कि किस feature या customer ने spike किया।
- Agents और retries calls को गुणा कर देते हैं; एक user request पर 8 LLM calls हो सकती हैं।
- Per-request cost के बिना pricing, quota, budget और ROI तय नहीं हो सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a price table: model -> (input $/1M, output $/1M, cached-input $/1M)
Step 2 → After each call read response.usage (prompt_tokens, completion_tokens, cached tokens)
Step 3 → cost = in*price_in + out*price_out (+ cached discount)
Step 4 → Add cost to the request context (contextvar) so ALL calls in one request sum up
Step 5 → Log/emit: {request_id, user_id, feature, model, tokens, cost}
Step 6 → Aggregate in a DB/metrics: cost by user, feature, day
Step 7 → Enforce budgets: per-user daily cap, alert at 80%, hard stop at 100%
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Price table रखो: model -> (input $/1M, output $/1M, cached $/1M)
Step 2 → हर call के बाद response.usage पढ़ो
Step 3 → cost = in*price_in + out*price_out (+ cached discount)
Step 4 → Cost को request context (contextvar) में जोड़ो ताकि एक request की सारी calls जुड़ें
Step 5 → Log/emit: {request_id, user_id, feature, model, tokens, cost}
Step 6 → DB/metrics में aggregate: user, feature, दिन के हिसाब से
Step 7 → Budget लागू करो: per-user daily cap, 80% पर alert, 100% पर stop
```

---

## 🟡 Real World Example
**Tariff Classification System**: One classification = query rewrite (small), classify (main), validation (small). Cost ledger shows the average request costs $0.0009, but the `bulk-upload` feature costs $0.012 per row because it sends the full chapter text each time. Customer "ACME-Logistics" uses 62% of total spend. The team moves bulk upload to the Batch API (50% cheaper) and sets a daily quota per customer.

**Zomato-style**: cost per conversation (all turns) vs revenue per order, so the assistant is justified only if it improves conversion.

## 🟡 Real Example Hindi mein
**Tariff System**: एक classification = query rewrite (छोटा), classify (मुख्य), validation (छोटा)। Ledger दिखाता है औसत request $0.0009 की है, पर `bulk-upload` feature में प्रति row $0.012 है क्योंकि हर बार पूरा chapter भेजा जाता है। Customer "ACME-Logistics" कुल खर्च का 62% लेता है। Team bulk upload को Batch API (50% सस्ता) पर ले जाती है और per-customer daily quota लगाती है।

---

## 💻 Code Example — Basic
A cost calculator and per-request ledger in pure Python (run directly).

```python
# Compute cost per request and aggregate by feature
from dataclasses import dataclass                      # data container
from collections import defaultdict                    # grouping

PRICES: dict[str, tuple[float, float]] = {             # model -> (input, output) USD per 1M tokens
    "gpt-4o-mini": (0.15, 0.60),                       # example prices; check provider page
    "gpt-4o": (2.50, 10.00),
}


def cost_usd(model: str, in_tok: int, out_tok: int) -> float:
    if model not in PRICES:                            # unknown model: fail loudly, not silently 0
        raise KeyError(f"no price for model {model}")
    pin, pout = PRICES[model]                          # unpack prices
    return (in_tok * pin + out_tok * pout) / 1_000_000 # tokens -> dollars


@dataclass
class Entry:                                           # one ledger row
    request_id: str
    feature: str
    model: str
    in_tok: int
    out_tok: int

    @property
    def cost(self) -> float:                           # computed field
        return cost_usd(self.model, self.in_tok, self.out_tok)


LEDGER = [                                             # sample calls
    Entry("r1", "classify", "gpt-4o-mini", 420, 12),
    Entry("r2", "bulk-upload", "gpt-4o", 6000, 40),
    Entry("r3", "classify", "gpt-4o-mini", 450, 14),
]

by_feature: dict[str, float] = defaultdict(float)      # feature -> total cost
for e in LEDGER:
    by_feature[e.feature] += e.cost                    # sum

for feature, total in by_feature.items():
    print(f"{feature}: ${total:.6f}")
```

## 💻 Code Example — Advanced
Request-scoped cost accumulator with `contextvars`, budget guard, async OpenAI wrapper.

```python
# Production cost tracking: sums every LLM call inside one request, enforces a per-user budget
import contextvars                                             # request-scoped state
import logging                                                 # structured logs
from dataclasses import dataclass, field                       # containers
from decimal import Decimal                                    # money should not use float drift
from typing import Optional                                    # hints

from openai import AsyncOpenAI                                 # client

log = logging.getLogger("cost")                                # logger
client = AsyncOpenAI()                                         # openai client

PRICE = {"gpt-4o-mini": (Decimal("0.15"), Decimal("0.60"))}   # $/1M tokens (in, out)


@dataclass
class RequestCost:                                             # accumulates within one request
    request_id: str
    user_id: str
    total: Decimal = Decimal(0)                                # running dollars
    calls: list[dict] = field(default_factory=list)            # per-call detail


_current: contextvars.ContextVar[Optional[RequestCost]] = contextvars.ContextVar("cost", default=None)
SPENT_TODAY: dict[str, Decimal] = {}                           # replace with Redis in production
DAILY_CAP = Decimal("1.00")                                    # $1 per user per day


class BudgetExceeded(Exception):                               # custom error -> HTTP 429
    pass


async def tracked_chat(model: str, messages: list[dict], **kw) -> str:
    rc = _current.get()                                        # active request, may be None
    if rc and SPENT_TODAY.get(rc.user_id, Decimal(0)) >= DAILY_CAP:
        raise BudgetExceeded(rc.user_id)                       # stop BEFORE spending more
    resp = await client.chat.completions.create(model=model, messages=messages, **kw)
    u = resp.usage                                             # usage can be None for some streams
    if u and model in PRICE:                                   # compute only if known
        pin, pout = PRICE[model]
        c = (Decimal(u.prompt_tokens) * pin + Decimal(u.completion_tokens) * pout) / Decimal(1_000_000)
        if rc:
            rc.total += c                                      # add to request total
            rc.calls.append({"model": model, "in": u.prompt_tokens, "out": u.completion_tokens, "usd": str(c)})
            SPENT_TODAY[rc.user_id] = SPENT_TODAY.get(rc.user_id, Decimal(0)) + c
    else:
        log.warning("missing usage or price for %s", model)    # never hide missing data
    return resp.choices[0].message.content or ""


def start_request(request_id: str, user_id: str) -> RequestCost:
    rc = RequestCost(request_id, user_id)                      # new accumulator
    _current.set(rc)                                           # bind to this async context
    return rc
```

---

## 🟠 FastAPI Integration
Middleware-style dependency starts the accumulator and returns cost in a response header.

```python
# FastAPI: attach request cost to response header and enforce budget
import uuid                                                    # request ids
from fastapi import FastAPI, Header, HTTPException, Response   # framework
from pydantic import BaseModel

from cost_mod import start_request, tracked_chat, BudgetExceeded   # from advanced example

app = FastAPI()


class Req(BaseModel):
    product: str


@app.post("/classify")
async def classify(req: Req, response: Response, x_user_id: str = Header(default="anon")) -> dict:
    rc = start_request(uuid.uuid4().hex, x_user_id)            # begin cost scope
    try:
        code = await tracked_chat("gpt-4o-mini",
                                  [{"role": "user", "content": f"HS code for {req.product}"}],
                                  max_tokens=40)
    except BudgetExceeded:
        raise HTTPException(status_code=429, detail="daily budget reached")
    response.headers["X-LLM-Cost-USD"] = f"{rc.total:.6f}"     # visible to client/logs
    return {"hs_code": code, "calls": len(rc.calls)}
```

---

## 🔗 LangChain / LangGraph Connection
Use `usage_metadata` from the message, or a callback, to charge each node. In LangGraph, put the cost in graph state so you can see cost per node.

```python
# LangChain: cost from usage_metadata
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
msg = llm.invoke("HS code for speaker")
um = msg.usage_metadata or {}                                   # {"input_tokens":..,"output_tokens":..,"total_tokens":..}
usd = (um.get("input_tokens", 0) * 0.15 + um.get("output_tokens", 0) * 0.60) / 1e6
print(usd)

# LangGraph: node returns {"cost": state["cost"] + usd} so state accumulates per run.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Counting only successful calls, or forgetting retries
✅ Correct: record every attempt; failed streamed calls may still be billed for tokens generated.

```python
# Wrong: cost recorded only inside the success path of a retry loop
# Right: record in a finally block / each attempt
```

❌ Mistake 2: Hard-coded stale prices
✅ Correct: price table in config with an "effective date"; unknown model raises.

```python
# Wrong
cost = tokens * 0.00001
# Right
cost = cost_usd(model, in_tok, out_tok)   # table lookup, KeyError if model unknown
```

---

## 🧠 Tricky Interview Question
**Q**: "Your computed cost is 20% lower than the provider invoice. Why?"

**Answer**: Common gaps: (1) retries and timeouts not logged, (2) streaming calls where usage was not requested (`stream_options={"include_usage": True}`), (3) hidden tokens such as reasoning tokens (billed as output) or tool/function definitions counted in input, (4) image/audio tokens, (5) embedding, moderation and eval-judge calls not tracked, (6) outdated price table, (7) calls from notebooks or other services using the same key. Reconcile daily by key/project and alert on drift above 5%.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): Where do I get token counts?
A1: From `response.usage` (`prompt_tokens`, `completion_tokens`). Use tiktoken only for estimates before the call.

Q2 (Easy): Why are output tokens priced higher?
A2: Generating each token requires a sequential forward pass, while input tokens are processed in parallel, so output costs more compute.

Q3 (Medium): How do you attribute cost to a user when an agent makes many calls?
A3: Put a request/run id and user id in a contextvar at the entry point; every LLM wrapper adds its cost to that context. Persist one ledger row per call plus a roll-up per request.

Q4 (Medium): How do you handle streaming?
A4: Pass `stream_options={"include_usage": True}`; the final chunk contains usage. Without it, estimate with tiktoken and mark the record as estimated.

Q5 (Hard): Design a multi-tenant chargeback system.
A5: Each call writes an immutable event (tenant, feature, model, tokens, price version) to a queue; a consumer aggregates into per-tenant daily tables. Use a price-version table so historical cost does not change when prices change. Enforce real-time soft quotas with Redis counters, reconcile nightly against provider usage APIs, and expose a dashboard plus invoices.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-user product, agents, or any meaningful spend
- You need budgets, quotas, chargeback or unit economics

❌ Avoid when:
- Personal script with few calls (provider dashboard is enough)
- Do not block the request path on slow cost DB writes; emit events asynchronously

---

## 📊 Visual Diagram
```
 Request r1 (user=u7, feature=classify)
 ├─ rewrite  gpt-4o-mini  in=120  out=20  $0.000030
 ├─ classify gpt-4o-mini  in=420  out=12  $0.000070
 └─ validate gpt-4o-mini  in=200  out=10  $0.000036
                                  ───────────────
                       request total $0.000136
                              │
                              ▼
                  ledger ─> daily per-user sum ─> budget check (cap $1/day)
```

---

## 💰 Cost Impact
- Tracking adds no tokens; the ledger is a few bytes per call.
- Typical savings found: long system prompts (cache them), oversized context (retrieve less), wrong model tier (route easy queries to a mini model), retries (fix timeouts), bulk work (Batch API at about 50% discount).
- Example: 100k requests/day x $0.0009 = $90/day; cutting 400 input tokens from each request on gpt-4o-mini saves about $6/day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ledger | Record of every cost event | हर खर्च का record |
| Price table | Model to price mapping | Model की कीमतों की table |
| Chargeback | Billing teams/tenants for usage | Usage के हिसाब से बिल |
| Quota | Max allowed usage | अधिकतम अनुमत usage |
| Reasoning tokens | Hidden thinking tokens billed as output | Output में गिने छुपे tokens |
| Reconciliation | Matching your data with invoice | Invoice से मिलान |
| Unit economics | Cost per unit of value | प्रति unit लागत |

---

## ⚡ 3-Line Summary
English: Compute cost from `usage` tokens and a versioned price table, and sum every call per request with a contextvar. Tag by user, feature and model, enforce budgets, and reconcile with the invoice. Include retries, streaming, hidden tokens and judge calls.
Hindi: `usage` tokens और versioned price table से cost निकालो और contextvar से हर request की सारी calls जोड़ो। User, feature, model से tag करो, budget लागू करो और invoice से मिलान करो। Retries, streaming, hidden tokens और judge calls भी गिनो।

---

## ➡️ Next Topic
**435. Latency Tracking** — measuring TTFT, total and per-step latency, and finding the slow step.
