---

# 567. Rate Limiting AI API
# हिंदी में: AI API में Rate Limiting

---

## 🔵 Simple Definition (English)
Rate limiting caps how many requests (or tokens) a client can use in a time window. For AI APIs there are two sides: limiting your own users so they cannot abuse you, and respecting the provider's limits (RPM and TPM) so you do not get HTTP 429 errors.

## 🔵 सरल परिभाषा (Hindi)
Rate limiting तय करती है कि एक client एक time window में कितनी requests (या tokens) कर सकता है। AI API में दो पहलू हैं: अपने users को सीमित करना ताकि वे abuse न करें, और provider की limits (RPM और TPM) का सम्मान करना ताकि HTTP 429 errors न आएं।

---

## 🔴 Problem it Solves
One noisy user or a buggy client script can send thousands of requests, draining your budget and consuming the provider quota, so every other customer gets errors. LLM calls are slow and expensive, so even modest traffic spikes hurt. Plain request counts are also unfair: one request with 50K tokens costs far more than ten small ones, so token-based limits matter.

## 🔴 यह क्यों बना? (Hindi)
एक शोर करने वाला user या buggy client script हज़ारों requests भेजकर आपका budget खत्म कर सकता है और provider quota खा सकता है, जिससे बाकी customers को errors मिलते हैं। LLM calls धीमी और महंगी हैं, इसलिए छोटा traffic spike भी नुकसान करता है। सिर्फ request count unfair है: 50K tokens की एक request दस छोटी requests से ज़्यादा महंगी है, इसलिए token-based limits ज़रूरी हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the caller (API key, user ID, tenant, IP)
Step 2 → Choose an algorithm: fixed window, sliding window, or token bucket
Step 3 → Keep counters in a shared store (Redis) so all replicas agree
Step 4 → Before the LLM call: check requests/min AND estimated tokens/min
Step 5 → Allowed: proceed, then correct the token count with actual usage
Step 6 → Denied: return HTTP 429 with Retry-After header
Step 7 → Outbound: when the provider returns 429, retry with exponential backoff + jitter
Step 8 → Queue or shed low-priority work when near the provider's limit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Caller पहचानो (API key, user ID, tenant, IP)
Step 2 → Algorithm चुनो: fixed window, sliding window या token bucket
Step 3 → Counters shared store (Redis) में रखो ताकि सब replicas एक राय रखें
Step 4 → LLM call से पहले: requests/min और अनुमानित tokens/min दोनों जाँचो
Step 5 → Allowed: आगे बढ़ो, फिर actual usage से token count सही करो
Step 6 → Denied: HTTP 429 और Retry-After header लौटाओ
Step 7 → Outbound: provider 429 दे तो exponential backoff + jitter से retry
Step 8 → Provider limit के पास हो तो low-priority काम queue या shed करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Free-tier customers get 10 requests/min and 20K tokens/min; paid customers get 100/min. A customer's script loops on a failing call and sends 5,000 requests in a minute: after 10, they receive 429 with `Retry-After: 30`. Meanwhile the internal bulk-classification job respects the provider's TPM by using a shared token bucket so interactive users are never starved.

**Zomato-style**: During IPL-night peaks the chat assistant sheds non-essential requests (promos) first and keeps order-help requests flowing.

## 🟡 Real Example Hindi mein
**Tariff System**: Free-tier customers को 10 requests/min और 20K tokens/min मिलते हैं; paid को 100/min। एक customer की script fail होती call पर loop करके एक मिनट में 5,000 requests भेजती है: 10 के बाद उसे `Retry-After: 30` के साथ 429 मिलता है। इस बीच internal bulk-classification job shared token bucket से provider का TPM मानती है ताकि interactive users भूखे न रहें।

**Zomato-style**: IPL की रात के peak में chat assistant गैर-ज़रूरी requests (promos) पहले छोड़ता है और order-help requests चालू रखता है।

---

## 💻 Code Example — Basic
```python
# Basic token-bucket rate limiter (pure Python, runs directly)
import time                                      # clock


class TokenBucket:
    def __init__(self, capacity: float, refill_per_sec: float) -> None:
        self.capacity = capacity                 # max burst size
        self.refill = refill_per_sec             # tokens added per second
        self.tokens = capacity                   # start full
        self.last = time.monotonic()             # last refill time

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()                   # current time
        elapsed = now - self.last                # seconds since last call
        self.last = now                          # update stamp
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill)  # refill
        if self.tokens >= cost:                  # enough budget?
            self.tokens -= cost                  # spend it
            return True                          # allowed
        return False                             # denied


bucket = TokenBucket(capacity=5, refill_per_sec=1)   # burst 5, then 1 per second
results = [bucket.allow() for _ in range(8)]          # 8 instant calls
print(results)                                        # first 5 True, rest False
time.sleep(1.1)                                       # wait for a refill
print(bucket.allow())                                 # True again
```

## 💻 Code Example — Advanced
```python
# Production style: Redis sliding-window limiter for requests AND tokens (async),
# plus outbound retry with exponential backoff + jitter for provider 429s.
from __future__ import annotations
import asyncio                                   # sleep + async
import random                                    # jitter
import time                                      # timestamps
import uuid                                      # unique member ids
from dataclasses import dataclass                # result container
from typing import Awaitable, Callable, TypeVar  # generics for retry helper

import redis.asyncio as redis                    # pip install redis

T = TypeVar("T")


@dataclass
class Decision:
    allowed: bool                                # pass or block
    retry_after: int                             # seconds to wait if blocked


class SlidingWindowLimiter:
    def __init__(self, r: redis.Redis, limit: int, window_s: int = 60) -> None:
        self.r, self.limit, self.window = r, limit, window_s

    async def check(self, key: str, weight: int = 1) -> Decision:
        now = time.time()                                        # now in seconds
        zkey = f"rl:{key}"                                       # sorted set per caller
        pipe = self.r.pipeline()                                 # batch commands
        pipe.zremrangebyscore(zkey, 0, now - self.window)        # drop old entries
        pipe.zrange(zkey, 0, -1)                                 # read remaining members
        _, members = await pipe.execute()
        used = sum(int(m.decode().split(":")[0]) for m in members)   # weight stored in member
        if used + weight > self.limit:
            return Decision(False, self.window)                  # coarse retry hint
        await self.r.zadd(zkey, {f"{weight}:{uuid.uuid4()}": now})   # record this use
        await self.r.expire(zkey, self.window)                   # auto cleanup
        return Decision(True, 0)
    # Note: for strict atomicity under high concurrency, move this into a Lua script.


class ProviderRateLimited(Exception):
    """Raised by your LLM wrapper when the provider returns HTTP 429."""


async def with_backoff(fn: Callable[[], Awaitable[T]], retries: int = 5,
                       base: float = 0.5, cap: float = 20.0) -> T:
    for attempt in range(retries):
        try:
            return await fn()                                    # try the call
        except ProviderRateLimited:
            if attempt == retries - 1:
                raise                                            # out of retries
            delay = min(cap, base * 2 ** attempt)                # exponential growth
            await asyncio.sleep(random.uniform(0, delay))        # full jitter
    raise RuntimeError("unreachable")
```

---

## 🟠 FastAPI Integration
Use a dependency so every route is protected. Limit both requests and estimated tokens, and send `Retry-After`.

```python
from fastapi import Depends, FastAPI, Header, HTTPException   # framework

app = FastAPI()
r = redis.from_url("redis://localhost:6379")
req_limiter = SlidingWindowLimiter(r, limit=10, window_s=60)        # 10 requests/min
tok_limiter = SlidingWindowLimiter(r, limit=20_000, window_s=60)    # 20K tokens/min


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)                  # rough estimate; use tiktoken in real code


async def limit_guard(question: str, x_api_key: str = Header(...)) -> None:
    d1 = await req_limiter.check(f"req:{x_api_key}")
    d2 = await tok_limiter.check(f"tok:{x_api_key}", weight=estimate_tokens(question) + 300)
    if not (d1.allowed and d2.allowed):
        raise HTTPException(status_code=429, detail="rate limit exceeded",
                            headers={"Retry-After": str(max(d1.retry_after, d2.retry_after))})


@app.post("/classify", dependencies=[Depends(limit_guard)])
async def classify(question: str) -> dict:
    # answer = await with_backoff(lambda: call_llm(question))
    return {"answer": "stub"}
```
(Ready-made option: the `slowapi` package for per-route request limits.)

---

## 🔗 LangChain / LangGraph Connection
LangChain ships `InMemoryRateLimiter` (in `langchain_core.rate_limiters`) that you pass to chat models via `rate_limiter=` to stay under the provider's requests-per-second. Models also have `max_retries` for backoff on 429. In LangGraph, bound parallel fan-out with `max_concurrency` in the run config so one graph run cannot flood the provider.

```python
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI

limiter = InMemoryRateLimiter(requests_per_second=2, max_bucket_size=5)   # outbound throttle
llm = ChatOpenAI(model="gpt-4o-mini", rate_limiter=limiter, max_retries=3)
# await graph.ainvoke(state, config={"max_concurrency": 4})
```
(It limits requests, not tokens, and is per process; use Redis for multi-replica limits.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Per-process in-memory counters with many replicas (each replica allows the full limit).
✅ Correct: shared Redis counters.

```python
# Wrong
counts: dict[str, int] = {}            # lives in one process only
# Right
await r.incr(f"rl:{key}")              # shared across replicas
```

❌ Mistake 2: Limiting requests only, not tokens. One huge prompt bypasses the intent.
✅ Correct: limit both; charge by estimated tokens and fix with actual usage.

❌ Mistake 3: Retrying immediately in a tight loop on 429 (retry storm).
✅ Correct: exponential backoff with jitter and a retry cap; honour the provider's `Retry-After` when present.

---

## 🧠 Tricky Interview Question
**Q**: "You limit users to 10 req/min, but the provider still returns 429 during peaks. Why?"

**Answer**: Your per-user limits do not bound the aggregate. 1,000 users x 10 req/min = 10,000 req/min, above the provider's organisation limit (and TPM is often hit before RPM). You need a global limiter (outbound) in front of the provider plus a queue with priorities, backoff with jitter, multiple provider keys/regions or fallback models, and capacity planning. Also streaming and long outputs hold tokens-per-minute budget longer than expected.

---

## ⚫ Interview Questions + Answers

Q1: Why do AI APIs need rate limits?
A1: To control cost, prevent abuse, keep fairness among users, and stay within provider quotas.

Q2: What do RPM and TPM mean?
A2: Requests per minute and tokens per minute: the two limits most LLM providers enforce.

Q3: Compare fixed window, sliding window, and token bucket.
A3: Fixed window is simple but allows bursts at window edges (2x). Sliding window is smoother but costs more memory. Token bucket allows controlled bursts and a steady refill rate, which is the common choice.

Q4: What HTTP status and headers do you return when limited?
A4: 429 Too Many Requests with `Retry-After`, and often `X-RateLimit-Limit/Remaining/Reset` headers.

Q5: (Hard) How do you rate limit tokens when output length is unknown before the call?
A5: Reserve an estimate (prompt tokens + `max_tokens`) up front, then refund or charge the difference after the response using actual usage. Setting `max_tokens` bounds the worst case. For streaming, account as chunks arrive or on completion.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public or multi-tenant APIs, expensive models, bulk jobs sharing quota with interactive users

❌ Avoid when:
- Single trusted internal user with a provider-side cap already (still add backoff for 429s)

---

## 📊 Visual Diagram
```
 Client ─► [Limiter: Redis]  ── over limit ──► 429 + Retry-After
              │ ok
              ▼
        [Priority queue] ─► [Outbound throttle] ─► Provider
                                   ▲                  │
                                   └─ 429? backoff ◄──┘

 Token bucket:  capacity 5 ▓▓▓▓▓   each call takes 1
                refill 1/s  ░ ─► ▓   burst allowed, then steady rate
```

---

## 💰 Cost Impact
- Rate limits cap worst-case spend: 10 req/min x 1,000 tokens x 60 x 24 = about 14.4M tokens/day per key (illustrative). Without a limit, one script can multiply that by 100.
- Optimise: set `max_tokens`, tier plans by quota, cache duplicates before counting them against limits, queue bulk jobs to off-peak/batch APIs (typically cheaper).
- Retries cost tokens too if the provider counted the failed request; cap retries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RPM / TPM | Requests / tokens per minute | प्रति मिनट requests / tokens |
| Token bucket | Refilling budget algorithm | Refill होने वाला budget algorithm |
| 429 | Too Many Requests status | बहुत ज़्यादा requests status |
| Backoff | Wait longer after each failure | हर failure पर ज़्यादा इंतज़ार |
| Jitter | Random delay to avoid sync retries | Random delay |
| Load shedding | Dropping low-priority work | कम ज़रूरी काम छोड़ना |

---

## ⚡ 3-Line Summary
English: Limit both requests and tokens per caller using shared Redis counters, and return 429 with Retry-After. Also throttle outbound calls and retry provider 429s with exponential backoff and jitter. Per-user limits alone do not protect the global provider quota.
Hindi: Shared Redis counters से हर caller के requests और tokens दोनों limit करो और Retry-After के साथ 429 दो। Outbound calls भी throttle करो और provider 429 पर exponential backoff + jitter से retry करो। सिर्फ per-user limits global provider quota नहीं बचाते।

---

## ➡️ Next Topic
**568. AI API Security** — authentication, prompt injection, data leakage, and abuse prevention for your AI endpoints.
