---

# 091. Retry on Invalid Output
# हिंदी में: Invalid Output पर Retry

---

## 🔵 Simple Definition (English)
Retry on invalid output means: when the LLM's answer fails validation, call it again with feedback about what was wrong, up to a small limit. There are two kinds of retries: **validation retries** (the model's content was bad, so show it the error) and **transient retries** (network or rate-limit errors, so wait with backoff and resend).

## 🔵 सरल परिभाषा (Hindi)
Invalid output पर retry का मतलब: जब LLM का जवाब validation में fail हो, तो गलती का feedback देकर उसे दोबारा call करो, एक छोटी limit तक। Retries दो तरह के हैं: **validation retries** (content गलत था, इसलिए error दिखाओ) और **transient retries** (network/rate-limit errors, इसलिए backoff के साथ रुककर दोबारा भेजो)।

---

## 🔴 Problem it Solves
LLMs are probabilistic: even with a good prompt, one in fifty answers may fail. Failing the user request for each is bad UX; looping forever is bad for cost. A bounded retry with feedback gives high success at controlled cost.

## 🔴 यह क्यों बना? (Hindi)
LLMs probabilistic हैं: अच्छे prompt के बाद भी पचास में से एक जवाब fail हो सकता है। हर fail पर user request गिरा देना बुरा UX है; अनंत loop cost के लिए बुरा। Feedback के साथ bounded retry कम cost पर ऊँची success देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call the LLM
Step 2 → Parse + validate the answer
Step 3 → If valid -> return
Step 4 → If invalid -> build feedback: previous answer + exact error
Step 5 → Append feedback to messages, attempt += 1
Step 6 → If attempt > max_retries -> stop (fallback / human review / error)
Step 7 → Transient API errors: exponential backoff (1s, 2s, 4s + jitter) and resend
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM को call करो
Step 2 → जवाब parse + validate करो
Step 3 → Valid हो तो return
Step 4 → Invalid हो तो feedback बनाओ: पिछला जवाब + सही error
Step 5 → Feedback messages में जोड़ो, attempt += 1
Step 6 → attempt > max_retries हो तो रुको (fallback / human review / error)
Step 7 → Transient API errors: exponential backoff (1s, 2s, 4s + jitter) और दोबारा भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: On a batch of 10,000 products, 3% return unknown HS codes. The retry loop sends: "HS code 8518.99 does not exist. Valid chapters: 8517, 8518, 8471. Try again." 90% of those pass on attempt 2; the remaining go to the human review queue instead of blocking the batch.

**Amazon-style**: Rate limit (HTTP 429) during a sale spike is handled by backoff, not by failing orders.

## 🟡 Real Example Hindi mein
**Tariff System**: 10,000 products के batch में 3% unknown HS codes लौटाते हैं। Retry loop भेजता है: "HS code 8518.99 मौजूद नहीं है। Valid chapters: 8517, 8518, 8471। फिर कोशिश करो।" उनमें से 90% attempt 2 में पास हो जाते हैं; बाकी human review queue में जाते हैं, batch नहीं रुकता।

**Amazon-style**: Sale spike में rate limit (HTTP 429) backoff से संभलता है, orders fail नहीं होते।

---

## 💻 Code Example — Basic
```python
# Basic: bounded retry with feedback and exponential backoff. Pure Python, offline.
import random                                       # jitter
import time                                         # sleep for backoff
from typing import Callable                         # type hint

class RetryExhausted(RuntimeError):
    """All attempts failed."""

def retry_with_feedback(
    call: Callable[[list[str]], str],               # takes conversation, returns answer
    validate: Callable[[str], str],                 # raises ValueError if bad
    max_retries: int = 3,
) -> str:
    messages: list[str] = ["Classify: wireless earbuds"]   # initial prompt
    last_error = ""                                 # remember last error
    for attempt in range(max_retries + 1):          # first try + retries
        try:
            answer = call(messages)                 # LLM call (may raise ConnectionError)
        except ConnectionError as exc:              # transient error -> backoff
            delay = (2 ** attempt) * 0.01 + random.random() * 0.01   # tiny delay for demo
            print(f"transient error, sleeping {delay:.3f}s")
            time.sleep(delay)
            continue                                # resend same messages
        try:
            return validate(answer)                 # success path
        except ValueError as exc:                   # content error -> give feedback
            last_error = str(exc)
            print(f"attempt {attempt}: {last_error}")
            messages.append(f"Previous answer {answer!r} invalid: {last_error}")
    raise RetryExhausted(f"gave up: {last_error}")

# Demo fakes: network error first, then wrong code, then right code.
script = iter([ConnectionError("timeout"), "8518.99", "8518.30"])
def fake_call(messages: list[str]) -> str:
    item = next(script)                             # next scripted event
    if isinstance(item, Exception):
        raise item                                  # simulate failure
    return item

def fake_validate(answer: str) -> str:
    if answer not in {"8518.30", "8517.13"}:
        raise ValueError(f"{answer} not in tariff table")
    return answer

print(retry_with_feedback(fake_call, fake_validate))   # prints events then 8518.30
```

## 💻 Code Example — Advanced
```python
# Production: async retries with tenacity-free manual backoff, error feedback, usage tracking.
import asyncio
import random
from typing import Optional
from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI(max_retries=0)                    # we manage retries ourselves

class TariffResult(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")
    confidence: float = Field(ge=0, le=1)

VALID = {"8518.30", "8517.13"}

async def classify(product: str, max_validation_retries: int = 2,
                   max_transient_retries: int = 4) -> Optional[TariffResult]:
    messages = [{"role": "system", "content": "Return HS classification."},
                {"role": "user", "content": product}]
    total_tokens = 0                                   # cost tracking across attempts
    validation_attempts = 0
    transient_attempts = 0
    while True:
        try:
            completion = await client.beta.chat.completions.parse(
                model="gpt-4o-mini", messages=messages,
                response_format=TariffResult, max_tokens=150, temperature=0)
        except (RateLimitError, APIConnectionError) as exc:     # transient
            transient_attempts += 1
            if transient_attempts > max_transient_retries:
                print("transient retries exhausted:", exc)
                return None
            delay = min(30, 2 ** transient_attempts) + random.random()   # backoff + jitter
            await asyncio.sleep(delay)
            continue
        except APIStatusError as exc:                  # 4xx/5xx non-retryable (e.g. 400, 401)
            print("fatal API error:", exc.status_code)
            return None
        except ValidationError as exc:                 # parse() raised on bad content
            error_text = str(exc.errors()[0]["msg"])
        else:
            total_tokens += completion.usage.total_tokens if completion.usage else 0
            result = completion.choices[0].message.parsed
            if result is not None and result.hs_code in VALID:
                print("total tokens used:", total_tokens)
                return result
            error_text = f"code {getattr(result, 'hs_code', None)} not in {sorted(VALID)}"
        validation_attempts += 1                       # content failed
        if validation_attempts > max_validation_retries:
            print("validation retries exhausted:", error_text)
            return None
        messages.append({"role": "user", "content": f"Invalid: {error_text}. Try again."})

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/classify", response_model=TariffResult)
async def classify_route(product: str) -> TariffResult:
    result = await classify(product)                   # retries inside
    if result is None:
        # 503 for upstream exhaustion, queue for human review in a real system
        raise HTTPException(status_code=503, detail="Classification unavailable, queued for review")
    return result
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", max_retries=2)      # transient retries (HTTP errors)
chain = llm.with_structured_output(TariffResult).with_retry(   # Runnable retry wrapper
    stop_after_attempt=3, wait_exponential_jitter=True)
# Note: .with_retry retries on exceptions, but it does NOT add error feedback to the prompt.
# For feedback loops use a LangGraph cycle: classify -> validate -> (retry? classify : END)
# with a counter in state to stop after N attempts.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying with the identical prompt at temperature 0
✅ Correct: Add the error feedback (or change temperature slightly).

```python
# Wrong: same messages again -> same wrong answer
# Right: messages.append({"role": "user", "content": f"Invalid: {error}. Fix it."})
```

❌ Mistake 2: Unbounded `while True` retry loop
✅ Correct: Count attempts and set a fallback.

```python
# Wrong: while not valid: result = llm()
# Right: for attempt in range(max_retries + 1): ...  else: send_to_human_review()
```

---

## 🧠 Tricky Interview Question

**Q**: "Your retry loop has max_retries=5 and a prompt of 3,000 tokens. A bad deploy makes 40% of outputs invalid. What happens to cost, and how would you protect against it?"

**Answer**: Each retry resends the growing conversation (3,000 + previous answers + errors), so a failing request may cost 5-6x. With 40% failing, total cost can rise 2-3x within minutes. Protections: low retry caps (2), a circuit breaker that stops retrying when failure rate exceeds a threshold, budget alerts, caching, a cheaper fallback or human queue, and canary deploys with eval gates.

---

## ⚫ Interview Questions + Answers

Q1: Why add the error message when retrying?
A1: So the model knows what to fix; blind retries often repeat the same mistake.

Q2: What is exponential backoff?
A2: Waiting longer after each failure (1s, 2s, 4s...), usually with random jitter, so clients do not hammer a struggling API together.

Q3: Which errors should be retried?
A3: Timeouts, connection errors, 429 and 5xx. Not 400 (bad request) or 401/403.

Q4: How many validation retries are sensible?
A4: 1-3. Success rate gains flatten quickly while cost grows.

Q5: Design a retry strategy for 1M requests/day.
A5: Separate transient vs validation retries; backoff with jitter; per-request token budget; global circuit breaker; idempotency keys; metrics on retry rate and cost per success; fallback model/human queue; dead-letter queue for permanent failures; and replay failed items off-peak with the Batch API for 50% savings.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Failures are random or fixable with feedback
- A request failing is costly to the user

❌ Avoid when:
- The error is deterministic (bad schema) — fix the root cause
- Latency budget is tiny (real-time voice)

---

## 📊 Visual Diagram
```
 call LLM ─► validate ─► OK ─────────────► return
    ▲           │ bad
    │           ▼
    │     add error to messages
    │           │ attempt <= max?
    └───────────┤ yes
                │ no
                ▼
        fallback / human review

 API error (429/5xx): wait 1s,2s,4s (+jitter) ─► resend same request
```

---

## 💰 Cost Impact
Each validation retry costs a full call plus extra tokens for the previous answer and error. Expected cost = base × (1 + failure_rate × avg_retries × growth). Transient retries on 429/5xx usually cost nothing because the failed call is not billed.
Optimise: reduce failure rate first (Enum, better descriptions), cap retries at 2, cheaper model for retries, circuit breaker, log cost per success.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Retry | Try again after failure | फिर कोशिश |
| Exponential backoff | Doubling wait time | बढ़ता इंतज़ार |
| Jitter | Random delay added | रैंडम देरी |
| Circuit breaker | Stop calls when failing a lot | ज़्यादा fail पर रोकना |
| Idempotency | Safe to repeat | दोहराना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Retry invalid LLM output with error feedback and a small cap. Handle transient API errors separately with backoff and jitter. Watch cost because retries resend the whole conversation.
Hindi: Invalid LLM output पर error feedback और छोटी limit के साथ retry करो। Transient API errors को backoff और jitter से अलग संभालो। Cost पर नज़र रखो क्योंकि retry पूरी conversation दोबारा भेजता है।

---

## ➡️ Next Topic
**092. Nested Structured Output** — objects inside objects, such as an invoice with line items.
