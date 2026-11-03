
---

# 532. Design: Multi-tenant AI API
# हिंदी में: Design: Multi-tenant AI API

---

## 🔵 Simple Definition (English)
A multi-tenant AI API is one platform that serves many customers (tenants) from shared infrastructure while keeping each tenant's data, limits, cost and configuration separate. The hard parts are isolation (no data leaks), fairness (no noisy neighbour), metering (who used how many tokens) and per-tenant customisation.

## 🔵 सरल परिभाषा (Hindi)
Multi-tenant AI API एक platform है जो कई customers (tenants) को shared infrastructure से serve करता है, पर हर tenant का data, limits, cost और configuration अलग रखता है। कठिन हिस्से हैं: isolation (data leak नहीं), fairness (noisy neighbour नहीं), metering (किसने कितने tokens use किए) और per-tenant customisation।

---

## 🔴 Problem it Solves
- One deployment per customer is too costly and slow to operate.
- Sharing without controls causes data leaks, one heavy tenant slowing everyone, and unclear billing.
- LLM providers enforce account-level rate limits, so one tenant can exhaust the quota for all.

## 🔴 यह क्यों बना? (Hindi)
- हर customer के लिए अलग deployment बहुत महँगा और चलाने में धीमा है।
- Controls के बिना sharing से data leak, एक भारी tenant से सबका धीमा होना, और अस्पष्ट billing होती है।
- LLM providers account-level rate limits लगाते हैं, इसलिए एक tenant सबका quota खत्म कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Authenticate: API key or JWT -> tenant_id + plan (free/pro/enterprise)
Step 2 → Resolve tenant config: model allow-list, prompt template, limits, region, features
Step 3 → Enforce quotas: requests/min, tokens/day, concurrent requests (fail with 429 + Retry-After)
Step 4 → Isolate data: tenant_id in every query, cache key, memory key, log line
Step 5 → Fair scheduling: per-tenant queues or weighted fair share so one tenant cannot starve others
Step 6 → Call the LLM through a shared gateway (pooled keys, retries, fallbacks, provider rate-limit aware)
Step 7 → Meter: record input/output tokens per tenant per request (usage events)
Step 8 → Bill and report: aggregate usage, invoices, dashboards, alerts at 80% of quota
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Authenticate: API key या JWT -> tenant_id + plan (free/pro/enterprise)
Step 2 → Tenant config निकालो: model allow-list, prompt template, limits, region, features
Step 3 → Quotas लागू करो: requests/min, tokens/day, concurrent requests (429 + Retry-After)
Step 4 → Data isolate करो: हर query, cache key, memory key, log line में tenant_id
Step 5 → Fair scheduling: per-tenant queues या weighted fair share ताकि एक tenant बाकियों को भूखा न रखे
Step 6 → Shared gateway से LLM call (pooled keys, retries, fallbacks, provider rate-limit aware)
Step 7 → Metering: हर request पर tenant के input/output tokens record करो (usage events)
Step 8 → Bill और report: usage aggregate, invoices, dashboards, quota के 80% पर alert
```

---

## 🟡 Real World Example
**Tariff Classification System as a platform**: Customs brokers, freight forwarders and an importer's in-house team each use the same API. Broker A is on the "pro" plan (1M tokens/day, may use the larger model); a small importer is on "free" (50K tokens/day, small model only). Each tenant has its own vector namespace of past rulings, its own prompt addendum ("use our internal product naming"), and its own monthly usage report. When Broker A runs a big batch job, a weighted queue ensures the small importer's interactive queries still finish in under 3 seconds.

**Zomato-style AI**: A restaurant-assistant API serves thousands of restaurants; each restaurant's menu is a separate namespace and each has a monthly token cap.

## 🟡 Real Example Hindi mein
**Tariff Classification System को platform की तरह**: Customs brokers, freight forwarders और एक importer की in-house team सब एक ही API use करते हैं। Broker A "pro" plan पर है (1M tokens/day, बड़ा model allowed); छोटा importer "free" पर (50K tokens/day, सिर्फ छोटा model)। हर tenant का अपना vector namespace (पुराने rulings), अपना prompt addendum ("हमारे internal product नाम use करो") और अपनी monthly usage report है। जब Broker A बड़ा batch job चलाता है, weighted queue यह पक्का करती है कि छोटे importer की interactive queries 3 सेकंड में पूरी हों।

**Zomato-style AI**: Restaurant-assistant API हज़ारों restaurants को serve करती है; हर restaurant का menu अलग namespace है और हर एक का monthly token cap है।

---

## 💻 Code Example — Basic
```python
# Basic: per-tenant token-bucket rate limiter (pure Python)
import time                                            # clock
from dataclasses import dataclass, field               # state per tenant

@dataclass
class Bucket:
    capacity: float                                    # max burst
    refill_per_sec: float                              # steady rate
    tokens: float = 0.0                                # current tokens
    last: float = field(default_factory=time.monotonic)  # last refill time

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()                         # current time
        elapsed = now - self.last                      # seconds since last call
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)  # refill
        self.last = now
        if self.tokens >= cost:                        # enough capacity?
            self.tokens -= cost                        # spend it
            return True
        return False                                   # rate limited

PLANS = {"free": (5, 1.0), "pro": (50, 20.0)}          # (burst, per-second) examples
buckets: dict[str, Bucket] = {}                        # tenant -> bucket

def check(tenant: str, plan: str) -> bool:
    burst, rate = PLANS[plan]
    b = buckets.setdefault(tenant, Bucket(burst, rate, tokens=burst))  # create on first use
    return b.allow()

if __name__ == "__main__":
    print([check("small-importer", "free") for _ in range(8)])  # first 5 True, rest False
    print([check("broker-a", "pro") for _ in range(8)])         # all True
```

## 💻 Code Example — Advanced
```python
# Advanced: async tenant gateway: quota, concurrency cap, metering, isolation
import asyncio                                         # async primitives
import time                                            # timestamps
from collections import defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class TenantConfig:
    tenant_id: str
    daily_token_quota: int                             # tokens per day
    max_concurrent: int                                # in-flight requests
    models: tuple[str, ...]                            # allowed models

class QuotaExceeded(Exception):
    """Maps to HTTP 429."""

class Gateway:
    def __init__(self, configs: dict[str, TenantConfig]) -> None:
        self.configs = configs                         # tenant -> config
        self.used: defaultdict[str, int] = defaultdict(int)       # tokens used today
        self.sems = {t: asyncio.Semaphore(c.max_concurrent) for t, c in configs.items()}
        self.usage_events: list[dict[str, object]] = []           # would go to a queue/DB

    async def _llm(self, model: str, prompt: str) -> tuple[str, int, int]:
        await asyncio.sleep(0.01)                      # mock provider call
        return "8507.60", len(prompt) // 4 + 10, 12    # (text, in_tokens, out_tokens)

    async def complete(self, tenant_id: str, model: str, prompt: str) -> str:
        cfg = self.configs.get(tenant_id)
        if cfg is None:
            raise PermissionError("unknown tenant")    # fail closed
        if model not in cfg.models:
            raise PermissionError("model not allowed for plan")
        if self.used[tenant_id] >= cfg.daily_token_quota:
            raise QuotaExceeded(tenant_id)             # budget check before spending
        async with self.sems[tenant_id]:               # per-tenant concurrency cap
            try:
                text, tin, tout = await asyncio.wait_for(self._llm(model, prompt), timeout=30)
            except asyncio.TimeoutError:
                raise TimeoutError("upstream timeout")
        self.used[tenant_id] += tin + tout             # meter actual usage
        self.usage_events.append({"tenant": tenant_id, "model": model,
                                  "in": tin, "out": tout, "ts": time.time()})
        return text

async def main() -> None:
    gw = Gateway({"a": TenantConfig("a", 100, 2, ("small", "large")),
                  "b": TenantConfig("b", 30, 1, ("small",))})
    print(await gw.complete("a", "large", "HS code for battery packs"))
    try:
        await gw.complete("b", "large", "x")           # not allowed on b's plan
    except PermissionError as exc:
        print("denied:", exc)
    for _ in range(3):                                 # b burns its small quota
        try:
            print(await gw.complete("b", "small", "HS code for a very long product text " * 2))
        except QuotaExceeded:
            print("quota exceeded for b")
    print("usage:", dict(gw.used))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Core pieces: an auth dependency that returns `TenantConfig`, error handlers mapping `QuotaExceeded` to 429, and middleware or response headers exposing remaining quota.

```python
# FastAPI multi-tenant endpoint
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()
CONFIGS = {"key-a": TenantConfig("a", 1_000_000, 10, ("small", "large"))}  # from DB in prod
gw = Gateway({c.tenant_id: c for c in CONFIGS.values()})

async def tenant(x_api_key: str = Header(default="")) -> TenantConfig:
    cfg = CONFIGS.get(x_api_key)                       # prod: hashed keys in a DB, constant-time lookup
    if cfg is None:
        raise HTTPException(status_code=401, detail="invalid api key")
    return cfg

@app.exception_handler(QuotaExceeded)
async def quota_handler(request: Request, exc: QuotaExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "quota exceeded"},
                        headers={"Retry-After": "3600"})   # tell clients when to retry

@app.post("/v1/classify")
async def classify(q: str, cfg: TenantConfig = Depends(tenant)) -> dict[str, object]:
    text = await gw.complete(cfg.tenant_id, "small", q)
    return {"answer": text, "tokens_used_today": gw.used[cfg.tenant_id],
            "quota": cfg.daily_token_quota}            # transparent usage
```
In production keep counters in Redis (atomic `INCRBY` with expiry) so all API replicas share the same quota state.

---

## 🔗 LangChain / LangGraph Connection
- Build per-tenant chains by injecting tenant config: prompt addendum, retriever namespace filter, allowed tools.
- Pass `tenant_id` in `config={"configurable": {...}, "metadata": {...}, "tags": [...]}` so LangSmith traces can be filtered and costs attributed per tenant.
- LangGraph checkpointers and memory must use a thread id that includes the tenant (for example `f"{tenant_id}:{session_id}"`) to avoid cross-tenant memory.

```python
# LangChain: tenant-scoped retriever and tracing metadata (illustrative)
# retriever = vectorstore.as_retriever(search_kwargs={"filter": {"tenant_id": cfg.tenant_id}})
# result = await chain.ainvoke({"q": q}, config={
#     "metadata": {"tenant_id": cfg.tenant_id}, "tags": [f"plan:{plan}"]})
# graph.ainvoke(state, config={"configurable": {"thread_id": f"{cfg.tenant_id}:{session_id}"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A global cache key without the tenant
```python
# Wrong: tenant B can get tenant A's cached answer
key = hash(question)
# Right: isolate by tenant (and prompt version)
key = hash((tenant_id, prompt_version, question))
```

❌ Mistake 2: One global rate limit
✅ Correct: Per-tenant limits plus a global protective limit. Otherwise one tenant exhausts the provider quota for all.

❌ Mistake 3: Counting tokens from your own estimate only
✅ Correct: Meter from the provider's `usage` field (actual tokens), and reconcile with the provider's bill.

---

## 🧠 Tricky Interview Question

**Q**: "Tenant A sends a 2,000-document batch at 9 am. Tenant B's chat latency goes from 2s to 40s, though both are under their daily quota. Why, and how do you fix it?"

**Answer**: This is the noisy-neighbour problem: shared worker pool or shared provider rate limit, with a FIFO queue where A's batch sits ahead of B's interactive requests. Daily quotas do not control burst or concurrency. Fixes: (1) separate queues and priority classes: interactive vs batch; (2) weighted fair queuing or per-tenant concurrency caps; (3) route batch work to the provider's batch API or off-peak workers; (4) per-tenant requests-per-minute and tokens-per-minute limits, not just daily; (5) reserve capacity for interactive traffic; (6) autoscale workers on queue depth per class.

---

## ⚫ Interview Questions + Answers

Q1: What is a tenant?
A1: A customer organisation (or account) using your platform. Its data, users, limits and billing are separate from other tenants.

Q2: Name three ways to isolate tenant data in a vector DB.
A2: Metadata filter on a shared collection (cheapest, relies on correct filtering), a namespace or partition per tenant, or a separate collection or cluster per tenant (strongest isolation, highest cost).

Q3: Why return HTTP 429 with `Retry-After`?
A3: 429 means too many requests. `Retry-After` tells well-behaved clients when to retry, avoiding retry storms.

Q4: How do you bill per tenant?
A4: Record a usage event per request (tenant, model, input tokens, output tokens, timestamp) from the provider's usage data, aggregate by period, apply price per model and plan, and expose dashboards and alerts.

Q5 (Hard): An enterprise tenant demands dedicated capacity and data residency. How do you extend the design?
A5: Introduce tenant tiers with a routing layer ("cells" or deployment stamps): shared cell for standard tenants, dedicated cells (own vector DB, workers, optionally own LLM keys or a region-pinned endpoint) for enterprise. The control plane (tenant registry, auth, billing) stays global or per region; the data plane runs per cell. A tenant-to-cell map in the gateway routes requests. This limits blast radius, supports residency, and allows per-tenant scaling, at the cost of more operational complexity.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You serve many customers with similar needs and want low unit cost
- You need per-customer quotas, config and billing

❌ Avoid (use single-tenant or dedicated cells) when:
- Strict regulatory isolation, or customers demand their own infrastructure
- A single huge tenant dominates the load

---

## 📊 Visual Diagram
```
 Tenants:   A (pro)      B (free)     C (enterprise)
              \            |             /
               v           v            v
          +--------------------------------------+
          | API Gateway: auth -> tenant_id, plan |
          | rate limit (RPM/TPM) | quota | 429   |
          +-------------------+------------------+
                              v
          +--------------------------------------+
          | Fair scheduler: queues per tenant/   |
          | class (interactive | batch)          |
          +---------+----------------+-----------+
                    v                v
          Shared workers        Dedicated cell (C)
          (cache key, memory,   own vector DB / keys
           vector filter all    / region
           include tenant_id)
                    |
                    v
           LLM gateway (pooled keys, retries, fallback)
                    |
                    v
           Usage events (tenant, in/out tokens) -> billing + dashboards
```

---

## 💰 Cost Impact
- Multi-tenancy lowers fixed cost per customer, but LLM tokens are the variable cost and must be metered per tenant or you cannot price correctly.
- Example (illustrative): a tenant sends 200K requests per month at 2,500 tokens each = 500M tokens. If your blended cost is about $0.5 per 1M tokens, that is about $250 per month; price the plan above that with margin.
- Controls that save money: plan-based model allow-lists (small model for free), per-tenant caching, max_tokens caps, batch APIs for offline jobs, and quota alerts at 80%.
- Watch hidden costs: per-tenant namespaces can increase vector DB overhead; many tiny tenants may justify shared collections with filters.
- Prices vary by provider and model; use real current pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tenant | One customer account | एक customer account |
| Noisy neighbour | One tenant slowing others | एक tenant से बाकियों का धीमा होना |
| Quota | Usage allowance | Usage की सीमा |
| Token bucket | Rate limit algorithm allowing bursts | Burst देने वाला rate limit algorithm |
| Metering | Measuring usage per tenant | Tenant के हिसाब से usage नापना |
| Namespace | Logical data partition | Data का तार्किक हिस्सा |
| Cell | Independent deployment unit | स्वतंत्र deployment इकाई |

---

## ⚡ 3-Line Summary
English: A multi-tenant AI API shares infrastructure but isolates data (tenant id in every query, cache key and memory), limits usage (RPM, TPM, concurrency, quotas) and meters tokens per tenant. Use fair scheduling to stop noisy neighbours. Offer dedicated cells for enterprise needs.
Hindi: Multi-tenant AI API infrastructure share करती है पर data isolate करती है (हर query, cache key और memory में tenant id), usage सीमित करती है (RPM, TPM, concurrency, quotas) और tenant के हिसाब से tokens नापती है। Noisy neighbours रोकने के लिए fair scheduling use करो। Enterprise ज़रूरतों के लिए dedicated cells दो।

---

## ➡️ Next Topic
**543. Multi-Stage Build for AI** — the deployment section begins: smaller, safer Docker images for AI services.
