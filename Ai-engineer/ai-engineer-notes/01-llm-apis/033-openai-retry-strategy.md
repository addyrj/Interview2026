---

# 033. OpenAI API — Retry Strategy
# हिंदी में: OpenAI API — Retry Strategy

---

## 🔵 Simple Definition (English)
A retry strategy decides when and how to repeat a failed API call. The standard recipe is: retry only transient errors, wait longer after each failure (**exponential backoff**), add randomness (**jitter**) so clients do not retry at the same moment, and stop after a limited number of attempts or a total time budget.

## 🔵 सरल परिभाषा (Hindi)
Retry strategy तय करती है कि fail हुई API call को कब और कैसे दोहराना है। Standard तरीका: सिर्फ़ transient errors retry करो, हर failure के बाद ज़्यादा इंतज़ार करो (**exponential backoff**), randomness जोड़ो (**jitter**) ताकि सब clients एक ही पल पर retry न करें, और सीमित attempts या कुल time budget के बाद रुक जाओ।

---

## 🔴 Problem it Solves
Temporary failures (429, 5xx, network blips) are normal. No retry means users see errors that would have disappeared in a second. Naive instant retries are worse: thousands of clients retry together and keep the service overloaded (a "thundering herd"). Backoff with jitter spreads the load and gives the service time to recover.

## 🔴 यह क्यों बना? (Hindi)
Temporary failures (429, 5xx, network blips) सामान्य हैं। Retry न हो तो users को ऐसे errors दिखते हैं जो एक सेकंड में चले जाते। Naive instant retries और बुरे हैं: हज़ारों clients एक साथ retry करके service को overloaded रखते हैं ("thundering herd")। Jitter वाला backoff load फैलाता है और service को ठीक होने का समय देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call the API
Step 2 → On success: return
Step 3 → On error: is it retryable? (429 rate limit, 5xx, timeout, connection)
Step 4 → If not retryable (400, 401, 403, quota): raise immediately
Step 5 → Compute wait = min(cap, base * 2^attempt)
Step 6 → Add jitter: sleep a random time in [0, wait] ("full jitter")
Step 7 → If server sent Retry-After, wait at least that long
Step 8 → Stop after max attempts or total deadline; then fallback or raise
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → API call करो
Step 2 → सफल हो तो return
Step 3 → Error पर: क्या retryable है? (429 rate limit, 5xx, timeout, connection)
Step 4 → Retryable नहीं (400, 401, 403, quota): तुरंत raise करो
Step 5 → wait = min(cap, base * 2^attempt) निकालो
Step 6 → Jitter जोड़ो: [0, wait] में random देर सोओ ("full jitter")
Step 7 → Server ने Retry-After भेजा हो तो कम से कम उतना रुको
Step 8 → Max attempts या कुल deadline के बाद रुको; फिर fallback या raise
```

---

## 🟡 Real World Example
**Tariff Classification System**: A nightly import classifies 20,000 items. Around 2 percent of calls hit 429/503. With backoff + jitter, almost all succeed on the second or third try, and the job finishes without manual reruns. Failed items after 4 attempts go to a "dead letter" table for review, and the job continues.

**Amazon-style AI**: Product-description generation uses a retry budget so that retries never exceed 10 percent of normal traffic.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Nightly import 20,000 items classify करता है। लगभग 2 प्रतिशत calls 429/503 पाती हैं। Backoff + jitter से लगभग सभी दूसरे या तीसरे try में सफल हो जाती हैं और job बिना manual rerun के पूरी होती है। 4 attempts के बाद भी fail हुए items review के लिए "dead letter" table में जाते हैं और job चलती रहती है।

**Amazon-style AI**: Product-description generation में retry budget है ताकि retries सामान्य traffic के 10 प्रतिशत से ज़्यादा न हों।

---

## 💻 Code Example — Basic
```python
# Hand-written exponential backoff with full jitter. Runs offline with a flaky fake function.
import random                                    # for jitter
import time                                      # for sleep
from typing import Callable, TypeVar             # type hints

T = TypeVar("T")                                 # return type of the wrapped function

class TransientError(Exception):
    """Stands in for RateLimitError / 5xx."""

def retry(fn: Callable[[], T], attempts: int = 5, base: float = 0.1, cap: float = 2.0) -> T:
    for attempt in range(attempts):              # 0, 1, 2, ...
        try:
            return fn()                          # success -> return result
        except TransientError as exc:            # only retry transient failures
            if attempt == attempts - 1:          # last attempt used up
                raise                            # give up and surface the error
            wait = min(cap, base * (2 ** attempt))      # exponential: 0.1, 0.2, 0.4, ...
            sleep_for = random.uniform(0, wait)         # full jitter
            print(f"attempt {attempt + 1} failed ({exc}); sleeping {sleep_for:.2f}s")
            time.sleep(sleep_for)                # wait before the next try
    raise RuntimeError("unreachable")            # keeps type checkers happy

calls = {"n": 0}                                 # counter to make fake function flaky

def flaky() -> str:
    calls["n"] += 1                              # count calls
    if calls["n"] < 3:                           # fail the first two times
        raise TransientError("503")
    return "HS 8517"                             # then succeed

print(retry(flaky))                              # prints two failures then HS 8517

# Real SDK: OpenAI(max_retries=3) already does this for 408/409/429/5xx and connection errors.
```

## 💻 Code Example — Advanced
```python
# Production: tenacity retry (sync + async), honours Retry-After, only transient errors
# pip install tenacity openai
import asyncio                                           # async runner
import logging                                           # logs
from typing import Optional                              # type hints

import openai                                            # error classes
from openai import AsyncOpenAI, OpenAI                   # clients
from tenacity import (                                   # retry toolkit
    before_sleep_log, retry, retry_if_exception, stop_after_attempt,
    stop_after_delay, wait_random_exponential,
)

logger = logging.getLogger(__name__)                     # logger
sync_client = OpenAI(max_retries=0, timeout=30.0)        # disable SDK retries: tenacity owns them
async_client = AsyncOpenAI(max_retries=0, timeout=30.0)


def is_transient(exc: BaseException) -> bool:
    if isinstance(exc, openai.RateLimitError):
        # insufficient_quota is a 429 that retrying cannot fix
        return getattr(exc, "code", None) != "insufficient_quota"
    return isinstance(exc, (openai.APIConnectionError, openai.InternalServerError))


retry_policy = dict(
    retry=retry_if_exception(is_transient),              # only transient errors
    wait=wait_random_exponential(multiplier=1, max=30),  # exponential backoff with jitter
    stop=(stop_after_attempt(5) | stop_after_delay(60)), # attempts OR total time budget
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,                                        # raise the real error at the end
)


@retry(**retry_policy)
def classify_sync(product: str) -> Optional[str]:
    r = sync_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"HS code digits only: {product}"}],
        max_tokens=20,
    )
    return r.choices[0].message.content


@retry(**retry_policy)                                   # tenacity supports async functions too
async def classify_async(product: str) -> Optional[str]:
    r = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"HS code digits only: {product}"}],
        max_tokens=20,
    )
    return r.choices[0].message.content


async def main() -> None:
    try:
        print(await classify_async("power bank"))
    except openai.APIError as exc:                       # after retries are exhausted
        logger.error("giving up: %s", exc)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
In a user-facing request, keep the total retry time short (a few seconds). For long jobs, push to a background task or queue and retry there with a longer budget.

```python
import openai                                         # errors
from fastapi import BackgroundTasks, FastAPI, HTTPException   # framework
from pydantic import BaseModel                        # models
from openai import AsyncOpenAI                        # client

app = FastAPI()                                       # app
# Request path: short budget (2 retries, 10 s timeout)
fast_client = AsyncOpenAI(max_retries=2, timeout=10.0)
# Background path: longer budget
slow_client = AsyncOpenAI(max_retries=6, timeout=60.0)


class Item(BaseModel):
    product: str


async def deep_classify(product: str) -> None:
    # Long retry budget is fine here because no user is waiting
    r = await slow_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"HS code digits only: {product}"}],
        max_tokens=20)
    print("saved", product, r.choices[0].message.content)   # replace with DB write


@app.post("/classify")
async def classify(item: Item, bg: BackgroundTasks) -> dict:
    try:
        r = await fast_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"HS code digits only: {item.product}"}],
            max_tokens=20)
        return {"hs": r.choices[0].message.content}
    except (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError):
        bg.add_task(deep_classify, item.product)       # retry later in the background
        raise HTTPException(status_code=202, detail="Queued, check back soon")
```

---

## 🔗 LangChain / LangGraph Connection
Three layers exist: the model's own `max_retries`, `Runnable.with_retry()` (tenacity-based, with `wait_exponential_jitter`), and `with_fallbacks()` for switching models. In LangGraph, a node can have a retry policy.

```python
from langchain_openai import ChatOpenAI                  # wrapper
import openai                                            # error types

llm = ChatOpenAI(model="gpt-4o-mini", max_retries=0)     # disable inner retries to avoid stacking

retrying = llm.with_retry(
    retry_if_exception_type=(openai.RateLimitError, openai.APIConnectionError),
    wait_exponential_jitter=True,       # backoff with jitter
    stop_after_attempt=4,               # max attempts
)
backup = ChatOpenAI(model="gpt-4o", max_retries=0)
chain = retrying.with_fallbacks([backup])                # after retries fail, use backup
# chain.invoke("HS code for a laptop?")

# LangGraph: builder.add_node("classify", fn, retry=RetryPolicy(max_attempts=4))
# (argument name differs by version; check docs of your installed langgraph)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying immediately with no delay
✅ Correct: Backoff with jitter.

```python
# Wrong — hammers the API
for _ in range(10):
    try: return call()
    except Exception: continue
# Right
@retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(5))
def call(): ...
```

❌ Mistake 2: Retrying non-idempotent side effects together with the LLM call
✅ Correct: Retry only the LLM call; do database writes or emails after success, or use idempotency keys.

❌ Mistake 3: Stacking retry layers (SDK x tenacity x LangChain x gateway)
✅ Correct: One owner for retries. Set `max_retries=0` on the others. Three layers of 3 attempts means up to 27 calls.

❌ Mistake 4: No total deadline
✅ Correct: Use `stop_after_delay` so a request cannot hang for minutes.

---

## 🧠 Tricky Interview Question

**Q**: "OpenAI is partially down. Your service retries 5 times per request and the outage gets worse for everyone, including you. Why, and what is the fix?"

**Answer**: Retries multiply load: 5 attempts means up to 6x traffic exactly when the dependency is weakest ("retry storm"). Fixes: exponential backoff with jitter, a **retry budget** (for example, retries limited to 10 percent of calls), a **circuit breaker** that stops calls for a cool-down period after consecutive failures, fast fallback (alternate model/provider, cache, non-LLM path), and shedding load with 503 + Retry-After. Retries are for rare blips, not for sustained outages.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is exponential backoff?
A1: Waiting longer after each failure, for example 1s, 2s, 4s, 8s, usually with a cap.

Q2: [Easy] Why add jitter?
A2: Random delay prevents many clients from retrying simultaneously.

Q3: [Medium] Does the OpenAI SDK retry by default?
A3: Yes. It retries connection errors, 408, 409, 429, and 5xx, 2 times by default, with backoff. Configure via `max_retries` on the client or per request using `client.with_options(max_retries=...)`.

Q4: [Medium] Which errors must never be retried?
A4: 400 (bad request), 401, 403, 404, and `insufficient_quota`. They need a code or config fix.

Q5: [Hard] What are idempotency concerns with retrying LLM calls?
A5: A timed-out request may still have completed and been billed, so a retry can duplicate cost and any side effects (tool calls, writes). Keep side effects outside the retry loop or use idempotency keys, make tool calls safe to repeat, and log request ids to detect duplicates.

---

## 🔷 When to Use + When Not to Use
✅ Use retries when:
- Failures are transient and calls are safe to repeat

❌ Avoid when:
- Error is permanent (400/401/quota)
- The system is overloaded (use circuit breaker, shed load)
- The call has non-idempotent side effects

---

## 📊 Visual Diagram
```
attempt 1 --fail--> wait rand(0..0.5s)
attempt 2 --fail--> wait rand(0..1s)
attempt 3 --fail--> wait rand(0..2s)
attempt 4 --fail--> wait rand(0..4s)
attempt 5 --fail--> give up -> fallback / dead letter

Without jitter:  |||||||||  (all clients retry at the same instant)
With jitter:     | | || |  | |  (load is spread out)
```

---

## 💰 Cost Impact
- Retries on timeouts can double-bill, since the first request may have completed server-side.
- Retries on 429/5xx that never started generating usually cost nothing in tokens but add latency and load.
- Optimise: set sensible timeouts, cap attempts and total time, set `max_tokens`, track retry rate as a metric (alert above a few percent), and add a circuit breaker and fallback to cheaper models.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exponential backoff | Wait doubles each retry | हर retry पर इंतज़ार दोगुना |
| Jitter | Random extra delay | Random अतिरिक्त देरी |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |
| Circuit breaker | Stops calls after repeated failures | बार-बार failure पर calls रोकना |
| Retry budget | Cap on total retries | कुल retries की सीमा |
| Dead letter | Place for permanently failed items | लगातार fail items की जगह |
| Thundering herd | Everyone retries together | सब एक साथ retry करें |

---

## ⚡ 3-Line Summary
English: Retry only transient errors, using exponential backoff with jitter and limits on attempts and total time. Keep one retry layer, protect side effects, and add a circuit breaker and fallback for real outages. The OpenAI SDK already retries twice by default.
Hindi: सिर्फ़ transient errors retry करो, exponential backoff + jitter के साथ और attempts व कुल समय की सीमा के साथ। Retry की एक ही layer रखो, side effects बचाओ, और असली outage के लिए circuit breaker व fallback जोड़ो। OpenAI SDK डिफ़ॉल्ट रूप से पहले से 2 बार retry करता है।

---

## ➡️ Next Topic
**034. Claude (Anthropic) API** — the Messages API from Anthropic, a second major provider to know.
