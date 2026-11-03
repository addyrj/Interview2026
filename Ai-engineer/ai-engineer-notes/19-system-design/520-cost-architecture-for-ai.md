---

# 520. Cost Architecture for AI
# हिंदी में: AI के लिए Cost Architecture

---

## 🔵 Simple Definition (English)
Cost architecture means designing the system so every LLM call is cheap by default: small models first, caching, short prompts, capped outputs, budgets and metering. Cost is treated as a design requirement, like latency, not as a surprise on the invoice.

## 🔵 सरल परिभाषा (Hindi)
Cost architecture का मतलब system ऐसे design करना कि हर LLM call by default सस्ती हो: पहले छोटे model, caching, छोटे prompts, output cap, budgets और metering। Cost एक design requirement है, invoice का surprise नहीं।

---

## 🔴 Problem it Solves
Prototype costs look tiny ($5/day) but scale linearly or worse: agents loop, retries re-send prompts, long chat histories get re-sent every turn, and one big tenant can burn the whole budget. Without metering you cannot tell which feature or customer costs what, and a bug can cost thousands overnight.

## 🔴 यह क्यों बना? (Hindi)
Prototype की cost छोटी लगती है ($5/day) पर scale पर बहुत बढ़ती है: agents loop करते हैं, retries prompt दोबारा भेजते हैं, chat history हर turn पर दोबारा जाती है, और एक बड़ा tenant पूरा budget जला सकता है। Metering के बिना पता नहीं चलता कौन-सा feature या customer कितना खर्च करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Meter: record input/output/cached tokens and cost per request, per tenant, per feature
Step 2 → Budget: set daily/monthly caps per tenant and globally; check before each call
Step 3 → Cache: exact-match cache, then semantic cache, then provider prompt cache
Step 4 → Route: send easy requests to a small model, hard ones to a large model
Step 5 → Shrink: trim prompts, retrieve fewer chunks, summarise history, cap max_tokens
Step 6 → Batch: non-urgent work uses batch APIs (cheaper, higher latency)
Step 7 → Alert: anomaly alerts on spend per hour; kill switch when a cap is hit
Step 8 → Review: weekly cost-per-successful-task report, tune thresholds
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Meter: हर request, tenant, feature के हिसाब से tokens और cost record करो
Step 2 → Budget: tenant और global daily/monthly cap; हर call से पहले check
Step 3 → Cache: exact-match, फिर semantic cache, फिर provider prompt cache
Step 4 → Route: आसान requests छोटे model को, कठिन बड़े model को
Step 5 → Shrink: prompt trim, कम chunks, history summary, max_tokens cap
Step 6 → Batch: non-urgent काम batch API से (सस्ता, ज़्यादा latency)
Step 7 → Alert: spend anomaly पर alert; cap hit होने पर kill switch
Step 8 → Review: हर हफ्ते cost-per-successful-task देखकर tuning
```

---

## 🟡 Real World Example
**Tariff Classification System**: 1M classifications per month. Naive design: every request goes to a large model with a 3,000-token prompt. Cost-aware design: (1) exact cache for repeated product descriptions (about 30% hits), (2) small model handles clear cases with confidence above 0.9 (about 60% of the rest), (3) large model only for ambiguous items, (4) the long static tariff instructions are placed in a cacheable prompt prefix. The monthly bill falls by roughly 80% in this illustrative model.

**Zomato-style**: Review summaries are generated once per restaurant per day, not per page view.

## 🟡 Real Example Hindi mein
**Tariff System**: महीने में 1M classifications। Naive design: हर request बड़े model को 3,000-token prompt के साथ। Cost-aware design: (1) repeated descriptions के लिए exact cache (~30% hits), (2) साफ cases छोटे model से (confidence 0.9 से ऊपर), (3) सिर्फ ambiguous items बड़े model को, (4) लंबी static instructions cacheable prefix में। इस illustrative हिसाब में bill लगभग 80% घटता है।
**Zomato-style**: Review summary restaurant के लिए दिन में एक बार बनती है, हर page view पर नहीं।

---

## 💻 Code Example — Basic
```python
# Cost calculator and budget guard (pure Python, runs offline)
# Prices are ILLUSTRATIVE (USD per 1M tokens); always read the provider's current price page
PRICES: dict[str, dict[str, float]] = {
    "small": {"input": 0.15, "output": 0.60},    # cheap model tier
    "large": {"input": 3.00, "output": 15.00},   # expensive model tier
}

def cost_usd(model: str, in_tok: int, out_tok: int) -> float:
    """Return the dollar cost of one call."""
    p = PRICES[model]                                   # look up the price row
    return in_tok * p["input"] / 1e6 + out_tok * p["output"] / 1e6   # tokens x price

class Budget:
    """Very small daily budget guard."""
    def __init__(self, limit_usd: float) -> None:
        self.limit = limit_usd                          # allowed spend
        self.spent = 0.0                                # spend so far

    def charge(self, amount: float) -> None:
        """Add spend or raise if the cap would be crossed."""
        if self.spent + amount > self.limit:            # would exceed the cap?
            raise RuntimeError("budget exceeded")       # block the call
        self.spent += amount                            # record the spend

b = Budget(limit_usd=0.01)                              # one cent budget for the demo
for i in range(100):                                    # try many calls
    c = cost_usd("small", 800, 100)                     # 800 in + 100 out tokens
    try:
        b.charge(c)                                     # pay for the call
    except RuntimeError as e:                           # budget hit
        print(f"stopped at call {i}: {e}; spent=${b.spent:.5f}")
        break                                           # stop calling the model
print("large vs small for same call:", round(cost_usd("large", 800, 100) / cost_usd("small", 800, 100), 1), "x")
```

## 💻 Code Example — Advanced
```python
# Cost-aware gateway: cache -> router -> budget -> metering (async, with errors)
import asyncio                                           # async runtime
import hashlib                                           # stable cache keys
from collections import defaultdict                      # per-tenant counters
from dataclasses import dataclass                        # result type
from typing import Awaitable, Callable                   # type hints

PRICES = {"small": (0.15, 0.60), "large": (3.00, 15.00)}   # illustrative $/1M (in, out)

@dataclass
class LLMReply:
    """Reply with usage so we can meter it."""
    text: str                                            # answer
    in_tok: int                                          # prompt tokens
    out_tok: int                                         # completion tokens
    confidence: float                                    # self-reported or classifier score

LLMFn = Callable[[str, str], Awaitable[LLMReply]]        # (model, prompt) -> reply

class BudgetExceeded(Exception):
    """Raised when a tenant is over its cap."""

class CostGateway:
    def __init__(self, llm: LLMFn, daily_cap: float = 5.0, threshold: float = 0.9) -> None:
        self.llm = llm                                   # underlying model caller
        self.cache: dict[str, str] = {}                  # exact-match cache (use Redis in prod)
        self.spend: dict[str, float] = defaultdict(float)   # tenant -> dollars today
        self.cap = daily_cap                             # per-tenant cap
        self.threshold = threshold                       # escalate below this confidence
        self.hits = 0                                    # cache hits
        self.calls = 0                                   # total requests

    @staticmethod
    def key(prompt: str) -> str:
        """Normalise and hash the prompt for the cache key."""
        return hashlib.sha256(prompt.strip().lower().encode()).hexdigest()

    def _bill(self, tenant: str, model: str, r: LLMReply) -> None:
        """Compute and record the cost of a reply."""
        pin, pout = PRICES[model]                        # price row
        self.spend[tenant] += r.in_tok * pin / 1e6 + r.out_tok * pout / 1e6   # add dollars

    async def ask(self, tenant: str, prompt: str) -> str:
        """Answer using the cheapest path that is good enough."""
        self.calls += 1                                  # count requests
        k = self.key(prompt)                             # cache key
        if k in self.cache:                              # free answer
            self.hits += 1
            return self.cache[k]
        if self.spend[tenant] >= self.cap:               # budget check BEFORE spending
            raise BudgetExceeded(tenant)
        try:
            r = await self.llm("small", prompt)          # try the cheap model first
            self._bill(tenant, "small", r)               # meter it
            if r.confidence < self.threshold:            # not sure? escalate
                r = await self.llm("large", prompt)      # pay more only when needed
                self._bill(tenant, "large", r)
        except asyncio.TimeoutError:                     # provider slow
            raise
        self.cache[k] = r.text                           # store for next time
        return r.text

async def demo() -> None:
    async def llm(model: str, prompt: str) -> LLMReply:  # fake model
        await asyncio.sleep(0)                           # yield to loop
        conf = 0.95 if "phone" in prompt else 0.5        # phones are easy
        return LLMReply("8517.13", 700, 50, conf if model == "small" else 0.99)
    gw = CostGateway(llm)                                # build gateway
    for p in ["smart phone", "smart phone", "odd widget"]:   # one repeat
        await gw.ask("acme", p)
    print(f"hit_rate={gw.hits/gw.calls:.0%} spend=${gw.spend['acme']:.6f}")

if __name__ == "__main__":
    asyncio.run(demo())                                  # run
```

---

## 🟠 FastAPI Integration
Put cost control in one place: a dependency or middleware that identifies the tenant, checks the budget, calls the gateway, and returns usage headers. Expose `/usage` for dashboards.

```python
# FastAPI: tenant budget check, metering and usage endpoint
from fastapi import FastAPI, Header, HTTPException, Response   # framework pieces
from pydantic import BaseModel                                 # validation

app = FastAPI()                                                # app
gateway = CostGateway(llm=my_llm_call, daily_cap=5.0)          # my_llm_call = your async function (see above)

class Q(BaseModel):
    prompt: str                                                # user text

@app.post("/ask")
async def ask(q: Q, resp: Response, x_tenant: str = Header(...)) -> dict[str, str]:
    """Answer within the tenant's budget."""
    try:
        text = await gateway.ask(x_tenant, q.prompt)           # cache/route/budget inside
    except BudgetExceeded:                                     # over cap
        raise HTTPException(status_code=429, detail="Daily AI budget reached")
    resp.headers["X-Spend-Today"] = f"{gateway.spend[x_tenant]:.4f}"   # transparent metering
    return {"answer": text}

@app.get("/usage/{tenant}")
async def usage(tenant: str) -> dict[str, float]:
    """Return current spend for dashboards."""
    return {"spend_usd": round(gateway.spend[tenant], 6), "cap_usd": gateway.cap}
```

---

## 🔗 LangChain / LangGraph Connection
Use callbacks to meter tokens in every chain or graph node (`usage_metadata` on AIMessage in current LangChain versions, or `get_openai_callback` for OpenAI). In LangGraph set a `recursion_limit` and keep a running cost in graph state so an agent loop stops when the budget is gone. LangChain's `InMemoryCache` / `set_llm_cache` gives exact-match LLM caching.

```python
# LangChain: read usage from the message and cache identical prompts
from langchain_openai import ChatOpenAI                       # model wrapper
from langchain_core.caches import InMemoryCache               # simple cache
from langchain_core.globals import set_llm_cache              # enable global cache

set_llm_cache(InMemoryCache())                                # identical prompts now cost $0
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=150)         # cap output tokens

async def classify(text: str) -> tuple[str, int]:
    msg = await llm.ainvoke(f"HS code for: {text}")           # call model
    usage = msg.usage_metadata or {}                          # token counts if provided
    return msg.content, usage.get("total_tokens", 0)          # answer + tokens

# LangGraph: stop loops with config={"recursion_limit": 10} when invoking the graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending the full chat history every turn
✅ Correct: Summarise old turns and keep only the last few.

```python
# Wrong — input tokens grow every turn (quadratic total cost)
messages = all_previous_messages + [new_user_message]

# Right — rolling window + summary
messages = [summary_msg] + all_previous_messages[-4:] + [new_user_message]
```

❌ Mistake 2: Always using the biggest model and no output cap
✅ Correct: Route by difficulty and set `max_tokens`.

```python
# Wrong
r = await client.chat.completions.create(model="big-model", messages=msgs)

# Right
model = "small-model" if is_easy(msgs) else "big-model"
r = await client.chat.completions.create(model=model, messages=msgs, max_tokens=200)
```

---

## 🧠 Tricky Interview Question

**Q**: "You cut cost per call by 70% using a smaller model, but the monthly bill went up. Why?"

**Answer**: The metric must be cost per successful task, not per call. A smaller model may fail more often, causing retries, escalation to the big model (you pay both), longer prompts with more few-shot examples, or human rework. Cheaper calls also encourage more usage (Jevons effect). Measure end-to-end: accuracy, retries, escalation rate, tokens per task, and total spend per tenant. Set an evaluation gate so the cheaper path must meet a quality bar.

---

## ⚫ Interview Questions + Answers

Q1: What are the main cost drivers of an LLM app? (Easy)
A1: Input tokens, output tokens (usually pricier), number of calls per task (agents, retries), model choice, and embeddings/vector storage. Output tokens often cost several times input tokens.

Q2: Name three quick ways to reduce cost. (Easy)
A2: Use a smaller model where possible, cache repeated requests, and shorten prompts / cap `max_tokens`.

Q3: Explain prompt caching vs semantic caching. (Medium)
A3: Provider prompt caching reuses the already processed static prefix of a prompt at a discount, so put stable content first. Semantic caching is your own layer: embed the query and return a stored answer when similarity is above a threshold. It saves the whole call but risks wrong hits, so tune the threshold and exclude personalised queries.

Q4: How do you do per-tenant cost attribution? (Medium)
A4: Tag each request with tenant and feature, record tokens and price per call in a metrics store, aggregate by tag, and expose dashboards and alerts. Use trace IDs to join multi-call workflows into one task cost.

Q5: Design a cost control plane for 500 tenants with different plans. (Hard)
A5: Gateway in front of all LLM calls: auth, plan lookup, token and dollar budgets in Redis with atomic counters, per-plan model allowlists, rate limits, cache, router with fallbacks, and usage events streamed to a warehouse. Add soft limits (warn at 80%), hard limits (block), overage billing, anomaly detection, and a global kill switch. Reserve budget before long jobs and reconcile with actual usage afterwards.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Volume is high or growing
- Multiple tenants or features share one provider account
- Agents or loops can multiply calls

❌ Avoid when:
- Over-optimising a prototype with a few hundred calls a month
- Cost savings would hurt a safety-critical accuracy requirement (measure first)

---

## 📊 Visual Diagram
```
Request ─▶ [Auth+Tenant] ─▶ [Budget OK?] ──no──▶ 429
                                 │yes
                                 ▼
                          [Exact cache] ──hit──▶ answer ($0)
                                 │miss
                                 ▼
                          [Semantic cache] ─hit─▶ answer (~$0)
                                 │miss
                                 ▼
                          [Router] ─easy─▶ small model ──low conf──┐
                                 └─hard─▶ large model ◀────────────┘
                                 │
                                 ▼
                          [Meter tokens/$] ─▶ dashboard + alerts
```

---

## 💰 Cost Impact
Illustrative example (prices are examples, check current pricing): 1M requests/month, 700 input + 100 output tokens each.
- All large ($3 / $15 per 1M): 700M x $3 + 100M x $15 = $2,100 + $1,500 = $3,600.
- All small ($0.15 / $0.60): $105 + $60 = $165.
- Mixed: 30% cache hits ($0), 70% of requests reach models; of those 85% stay on small and 15% escalate (pay both): about 0.7 x ($165 + 0.15 x $3,600) = about $495. Roughly 86% lower than all-large.
Optimisations: caching, routing, prompt trimming, `max_tokens`, batch API for offline work, provider prompt caching for static prefixes, and structured short outputs (a code instead of a paragraph).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metering | Recording usage and cost | Usage और cost record करना |
| Budget cap | Max allowed spend | अधिकतम खर्च सीमा |
| Model routing | Pick model by difficulty | Difficulty के हिसाब से model चुनना |
| Prompt caching | Discount for reused prompt prefix | Reuse हुए prefix पर छूट |
| Semantic cache | Cache by meaning similarity | Meaning के आधार पर cache |
| Escalation | Retry with a bigger model | बड़े model पर दोबारा भेजना |
| Cost per task | Total spend per successful result | हर सफल काम की कुल cost |

---

## ⚡ 3-Line Summary
English: Design cost in from day one: meter every call, set budgets, cache, route to small models first, and cap tokens. Judge success by cost per successful task, not cost per call. Add alerts and a kill switch so bugs cannot drain the budget.
Hindi: Cost को शुरू से design करो: हर call meter करो, budget लगाओ, cache करो, पहले छोटा model और tokens cap। Success cost per successful task से नापो, cost per call से नहीं। Alerts और kill switch रखो ताकि bug budget न जला दे।

---

## ➡️ Next Topic
**521. Latency Budget Design** — cost and speed trade off; next we split a response-time target across each pipeline step.
