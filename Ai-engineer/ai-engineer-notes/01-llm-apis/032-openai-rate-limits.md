---

# 032. OpenAI API — Rate Limits
# हिंदी में: OpenAI API — Rate Limits

---

## 🔵 Simple Definition (English)
A rate limit is the maximum amount of API usage OpenAI allows in a time window. The main ones are **RPM** (requests per minute) and **TPM** (tokens per minute), and there may be daily limits too. Limits depend on your usage tier and model, and they apply per organisation/project, not per server. Exceeding them returns HTTP 429.

## 🔵 सरल परिभाषा (Hindi)
Rate limit वो अधिकतम API usage है जो OpenAI एक time window में allow करता है। मुख्य हैं **RPM** (requests per minute) और **TPM** (tokens per minute), और daily limits भी हो सकती हैं। Limits आपके usage tier और model पर निर्भर करती हैं और organisation/project पर लागू होती हैं, हर server पर अलग नहीं। पार करने पर HTTP 429 मिलता है।

---

## 🔴 Problem it Solves
Without limits, one customer (or a buggy loop) could use all the GPUs and slow everyone else. Limits protect fairness and stability. For you, the problem is the reverse: your app must stay under those limits or users get errors during peak traffic.

## 🔴 यह क्यों बना? (Hindi)
Limits के बिना एक customer (या buggy loop) सारे GPUs इस्तेमाल करके बाकी सबको धीमा कर सकता है। Limits fairness और stability बचाती हैं। आपके लिए समस्या उल्टी है: आपके app को इन limits के नीचे रहना होगा वरना peak traffic में users को errors मिलेंगे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Each request is counted against RPM
Step 2 → Its tokens (input + requested max_tokens estimate, then actual) count against TPM
Step 3 → Server compares usage in the current window with your tier limit
Step 4 → Under limit: normal response with rate-limit headers
Step 5 → Over limit: HTTP 429 RateLimitError (may include a Retry-After hint)
Step 6 → Headers x-ratelimit-remaining-requests / -tokens and x-ratelimit-reset-* show your budget
Step 7 → Your client waits (backoff) or slows down (limiter) and retries
Step 8 → Higher usage tiers raise limits automatically as you spend more over time
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर request RPM में गिनी जाती है
Step 2 → उसके tokens (input + max_tokens का अनुमान, फिर असली) TPM में गिने जाते हैं
Step 3 → Server मौजूदा window का usage आपकी tier limit से compare करता है
Step 4 → Limit के नीचे: rate-limit headers के साथ normal response
Step 5 → Limit के ऊपर: HTTP 429 RateLimitError (Retry-After hint हो सकता है)
Step 6 → Headers x-ratelimit-remaining-requests / -tokens और x-ratelimit-reset-* आपका बचा budget बताते हैं
Step 7 → आपका client इंतज़ार (backoff) या धीमा (limiter) होकर retry करता है
Step 8 → ज़्यादा spend करने पर usage tier और limits अपने आप बढ़ती हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Suppose your tier allows 500 RPM and 200,000 TPM. A batch of 2,000 classifications at 900 tokens each is 1.8M tokens, so the TPM limit (not RPM) is the bottleneck: at least 9 minutes. Sending everything at once gives instant 429s. A limiter that spends at most 180K tokens per minute finishes cleanly. (Numbers are illustrative; check your own limits page.)

**Zomato AI**: At dinner peak, a global token-bucket in Redis shares the limit across all API pods.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: मान लो आपके tier में 500 RPM और 200,000 TPM है। 900 tokens वाली 2,000 classifications का batch 1.8M tokens है, इसलिए bottleneck TPM है (RPM नहीं): कम से कम 9 मिनट। सब एक साथ भेजो तो तुरंत 429 मिलेगा। जो limiter प्रति मिनट 180K tokens से ज़्यादा खर्च नहीं करता वो साफ़ तरीके से पूरा कर देता है। (Numbers उदाहरण हैं; अपनी limits page पर देखो।)

**Zomato AI**: Dinner peak पर Redis में global token-bucket सभी API pods के बीच limit बाँटता है।

---

## 💻 Code Example — Basic
```python
# Pure Python token-bucket limiter demo (no API key needed)
import time                                      # clock
from typing import Optional                      # type hints

class TokenBucket:
    """Allows `rate` units per second with a burst up to `capacity`."""

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = rate                         # refill speed (units per second)
        self.capacity = capacity                 # bucket size
        self.tokens = capacity                   # start full
        self.last = time.monotonic()             # last refill time

    def try_take(self, amount: float = 1.0) -> bool:
        now = time.monotonic()                   # current time
        # Refill based on time passed, but never above capacity
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now                          # remember time
        if self.tokens >= amount:                # enough budget?
            self.tokens -= amount                # spend it
            return True                          # allowed
        return False                             # must wait

# 2 requests per second, burst of 2
bucket = TokenBucket(rate=2.0, capacity=2.0)
for i in range(6):                               # try 6 rapid requests
    print(i, "allowed" if bucket.try_take() else "blocked")   # first 2 pass, rest blocked
time.sleep(1.0)                                  # wait for refill
print("after 1s:", "allowed" if bucket.try_take() else "blocked")

# Reading real headers (needs API key):
# raw = client.chat.completions.with_raw_response.create(...)
# print(raw.headers.get("x-ratelimit-remaining-requests"))
# completion = raw.parse()      # the normal response object
```

## 💻 Code Example — Advanced
```python
# Production: async limiter for RPM + TPM, header awareness, 429 handling
import asyncio                                           # async tools
import logging                                           # logs
import time                                              # clock
from typing import Optional                              # type hints

import openai                                            # error classes
from openai import AsyncOpenAI                           # client

logger = logging.getLogger(__name__)                     # logger
client = AsyncOpenAI(max_retries=0, timeout=30.0)        # we handle 429s ourselves


class AsyncRateLimiter:
    """Simple sliding-window limiter for requests and tokens per minute."""

    def __init__(self, rpm: int, tpm: int) -> None:
        self.rpm, self.tpm = rpm, tpm                    # limits
        self.events: list[tuple[float, int]] = []        # (timestamp, tokens)
        self.lock = asyncio.Lock()                       # one waiter checks at a time

    async def acquire(self, tokens: int) -> None:
        while True:
            async with self.lock:
                now = time.monotonic()
                self.events = [(t, k) for t, k in self.events if now - t < 60]   # last minute
                used_tokens = sum(k for _, k in self.events)
                if len(self.events) < self.rpm and used_tokens + tokens <= self.tpm:
                    self.events.append((now, tokens))    # reserve budget
                    return
                oldest = self.events[0][0] if self.events else now
                wait = max(0.05, 60 - (now - oldest))    # time until oldest expires
            await asyncio.sleep(min(wait, 1.0))          # wait outside the lock


limiter = AsyncRateLimiter(rpm=400, tpm=150_000)         # leave ~20% headroom


async def limited_chat(prompt: str, est_tokens: int = 1000) -> Optional[str]:
    await limiter.acquire(est_tokens)                    # block until budget available
    try:
        raw = await client.chat.completions.with_raw_response.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        remaining = raw.headers.get("x-ratelimit-remaining-tokens")   # observe budget
        logger.info("remaining tokens this window: %s", remaining)
        return raw.parse().choices[0].message.content    # parse into the usual object
    except openai.RateLimitError as exc:
        retry_after = exc.response.headers.get("retry-after")   # hint from server
        logger.warning("429, retry-after=%s", retry_after)
        await asyncio.sleep(float(retry_after) if retry_after else 5.0)
        return None                                      # caller may retry
    except openai.APIError as exc:
        logger.error("api error: %s", exc)
        return None


if __name__ == "__main__":
    print(asyncio.run(limited_chat("HS code for a laptop?")))
```

---

## 🟠 FastAPI Integration
Protect both OpenAI and your own API: limit your clients, and queue or shed load when upstream is saturated.

```python
import asyncio                                         # semaphore
from fastapi import FastAPI, HTTPException             # framework
from pydantic import BaseModel                         # models
import openai                                          # errors
from openai import AsyncOpenAI                         # client

app = FastAPI()                                        # app
client = AsyncOpenAI(max_retries=3, timeout=30.0)      # SDK backoff on 429
UPSTREAM = asyncio.Semaphore(10)                       # max 10 concurrent upstream calls


class Q(BaseModel):
    text: str


@app.post("/ask")
async def ask(q: Q) -> dict:
    # Shed load quickly instead of piling up requests when we are saturated
    if UPSTREAM.locked():
        raise HTTPException(status_code=429, detail="Server busy",
                            headers={"Retry-After": "3"})
    async with UPSTREAM:                               # take a slot
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": q.text}],
                max_tokens=150)
        except openai.RateLimitError:
            raise HTTPException(status_code=503, detail="AI is busy, try again",
                                headers={"Retry-After": "10"})
    return {"answer": r.choices[0].message.content}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships `InMemoryRateLimiter` (in `langchain_core.rate_limiters`) that you pass to a chat model; it limits requests per second. `abatch(..., config={"max_concurrency": N})` limits parallelism. LangGraph nodes inherit these through the models they call.

```python
from langchain_core.rate_limiters import InMemoryRateLimiter   # built-in limiter
from langchain_openai import ChatOpenAI                        # wrapper

limiter = InMemoryRateLimiter(
    requests_per_second=5,        # about 300 requests per minute
    check_every_n_seconds=0.1,    # how often to check for free capacity
    max_bucket_size=10,           # allowed burst
)
llm = ChatOpenAI(model="gpt-4o-mini", rate_limiter=limiter, max_retries=3)
# llm.batch(prompts, config={"max_concurrency": 5})   # also caps parallelism
# Note: this limits requests, not tokens; for TPM use a custom limiter or a gateway.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Only thinking about RPM
✅ Correct: Long prompts hit TPM first.

```python
# Wrong — 100 requests x 10,000 tokens looks fine for RPM but is 1M tokens
await asyncio.gather(*(call(big_prompt) for _ in range(100)))
# Right — budget tokens too
await limiter.acquire(tokens=10_000)
```

❌ Mistake 2: Retrying instantly in a tight loop
✅ Correct: Honour `Retry-After` and use exponential backoff with jitter.

❌ Mistake 3: Ignoring `max_tokens`
✅ Correct: Large `max_tokens` can reserve more of your TPM budget; set realistic values.

❌ Mistake 4: One key shared by dev, test, and prod
✅ Correct: Use separate projects/keys so tests cannot starve production.

---

## 🧠 Tricky Interview Question

**Q**: "You run 10 pods, each with a limiter set to the full account limit of 500 RPM. You still see 429s. Why?"

**Answer**: Limits are account-wide (per organisation/project), but each pod thinks it owns the whole budget, so the sum is 5,000 RPM. Fix: divide the budget per pod, or better, use a shared distributed limiter (Redis token bucket) or a central gateway/queue (for example LiteLLM proxy). Also reserve headroom for spikes and other services using the same key, and watch the `x-ratelimit-*` headers to calibrate.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are RPM and TPM?
A1: Requests per minute and tokens per minute, the main rate limits.

Q2: [Easy] What HTTP code signals a rate limit?
A2: 429 Too Many Requests (`openai.RateLimitError`).

Q3: [Medium] How do you read your remaining budget?
A3: From response headers such as `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, and the matching `x-ratelimit-reset-*` fields, using `with_raw_response`.

Q4: [Medium] How can you process 100K documents without hitting limits?
A4: Use the Batch API (separate, higher limits, about 50 percent cheaper, completes within 24 hours), or a throttled worker queue with token-aware limiting.

Q5: [Hard] Design a rate limiter shared across many services.
A5: A central gateway or Redis-based token bucket with separate counters for RPM and TPM, priority queues (interactive over batch), per-tenant fairness quotas, backpressure to callers via 429 with Retry-After, metrics on queue wait time, and dynamic adjustment from response headers.

---

## 🔷 When to Use + When Not to Use
✅ Build explicit limiting when:
- Batch jobs, many pods, bursty traffic, multi-tenant apps

❌ Do not over-engineer when:
- Low traffic internal tool; SDK `max_retries` is enough

---

## 📊 Visual Diagram
```
Clients --> [ your limiter: token bucket (RPM + TPM) ] --> OpenAI
                 | allowed -> call
                 | blocked -> wait / queue
OpenAI --429 + Retry-After--> backoff --> retry

Headers per response:
 x-ratelimit-limit-requests / -tokens
 x-ratelimit-remaining-requests / -tokens
 x-ratelimit-reset-requests / -tokens
```

---

## 💰 Cost Impact
- Hitting limits does not cost tokens directly (rejected calls are not generated), but it wastes latency and causes retry storms.
- Rate limits cap throughput; to scale you may need a higher usage tier (spend-based) or the Batch API, which has separate limits and a discount.
- Optimise: cache repeated queries, shrink prompts (fewer TPM), set tight `max_tokens`, route simple tasks to cheaper models with their own limits, and spread load with fallbacks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RPM | Requests per minute | प्रति मिनट requests |
| TPM | Tokens per minute | प्रति मिनट tokens |
| 429 | Too Many Requests | बहुत ज़्यादा requests |
| Retry-After | Server hint on wait time | इंतज़ार का server hint |
| Token bucket | Refilling budget algorithm | रिफिल होने वाला budget algorithm |
| Backpressure | Telling callers to slow down | Callers को धीमा होने को कहना |
| Usage tier | Spend-based limit level | Spend पर आधारित limit स्तर |

---

## ⚡ 3-Line Summary
English: Rate limits (RPM, TPM) are account-wide, and exceeding them gives HTTP 429. Use a token-aware limiter, honour Retry-After, read the rate-limit headers, and share the budget across pods. For huge offline jobs use the Batch API.
Hindi: Rate limits (RPM, TPM) पूरे account पर लागू होती हैं और पार करने पर HTTP 429 मिलता है। Token-aware limiter use करो, Retry-After मानो, rate-limit headers पढ़ो और budget सभी pods में बाँटो। बड़े offline jobs के लिए Batch API लो।

---

## ➡️ Next Topic
**033. OpenAI API — Retry Strategy** — exponential backoff, jitter, and tenacity in practice.
