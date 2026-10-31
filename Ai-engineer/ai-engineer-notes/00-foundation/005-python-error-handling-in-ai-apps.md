---

# 005. Python Error Handling in AI Apps
# हिंदी में: AI Apps में Python Error Handling

---

## 🔵 Simple Definition (English)
Error handling means expecting failures and responding in a planned way: `try/except/else/finally`, custom exceptions, retries, timeouts and fallbacks. LLM apps fail often: rate limits (429), timeouts, bad JSON, context too long, empty answers. Good handling keeps the app alive and the user informed.

## 🔵 सरल परिभाषा (Hindi)
Error handling का मतलब failures की पहले से उम्मीद करके planned तरीके से जवाब देना: `try/except/else/finally`, custom exceptions, retries, timeouts और fallbacks। LLM apps अक्सर fail होते हैं: rate limit (429), timeout, गलत JSON, context बहुत लंबा, खाली answer। सही handling से app चलता रहता है और user को पता रहता है।

---

## 🔴 Problem it Solves
An unhandled exception becomes a 500 error and a lost request, and a blind retry loop can burn money. LLM APIs are remote and probabilistic: the same call can succeed, fail with 503, or return invalid JSON. You need to know which errors to retry, which to show to the user, and which to log.

## 🔴 यह क्यों बना? (Hindi)
Unhandled exception 500 error बन जाता है और request खो जाती है; अंधा retry loop पैसे जला सकता है। LLM APIs remote और probabilistic हैं: वही call सफल हो सकती है, 503 दे सकती है, या गलत JSON लौटा सकती है। तय करना पड़ता है कि किसे retry करें, किसे user को दिखाएँ, किसे सिर्फ़ log करें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap risky call in try/except catching SPECIFIC exceptions (never bare `except:`)
Step 2 → Classify the error: transient (429, 5xx, timeout) vs permanent (400, 401, context too long)
Step 3 → Transient: retry with exponential backoff + jitter, with a max attempt count
Step 4 → Permanent: do not retry; convert to a clear custom exception or HTTP 4xx
Step 5 → Validate the LLM output (JSON/Pydantic); on failure retry once with the error in the prompt
Step 6 → If still failing: fallback (cheaper model, rules, cached answer) or a graceful message
Step 7 → `finally` releases resources; always log with request id (never log secrets)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Risky call को try/except में रखो, SPECIFIC exceptions पकड़ो (bare `except:` कभी नहीं)
Step 2 → Error classify करो: transient (429, 5xx, timeout) या permanent (400, 401, context too long)
Step 3 → Transient: exponential backoff + jitter के साथ retry, max attempts तय
Step 4 → Permanent: retry नहीं; साफ़ custom exception या HTTP 4xx में बदलो
Step 5 → LLM output validate करो (JSON/Pydantic); fail हो तो error बताकर एक बार retry
Step 6 → फिर भी fail: fallback (सस्ता model, rules, cached answer) या सरल message
Step 7 → `finally` में resources छोड़ो; request id के साथ log करो (secrets कभी नहीं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: GPT returns HS code JSON. Cases: (1) 429 rate limit, so back off and retry; (2) JSON is truncated because `max_tokens` was too small, so retry with a larger limit once; (3) description is 200K tokens, a permanent error, so return 413 asking the user to upload fewer pages; (4) LLM is down, so use the rule-based classifier and mark the result `source="rules"`.

**Zomato AI**: If the recommendation LLM times out after 3 seconds, show the normal ranked list instead of an error page.

## 🟡 Real Example Hindi mein
**Tariff System**: GPT HS code JSON देता है। Cases: (1) 429 पर backoff के साथ retry; (2) `max_tokens` कम होने से JSON कटा हुआ, तो बड़े limit से एक बार retry; (3) description 200K tokens की, यह permanent error है, user से कम pages upload करने को कहो (413); (4) LLM down हो तो rule-based classifier और result पर `source="rules"`।

**Zomato AI**: Recommendation LLM 3 second में जवाब न दे तो error page की जगह normal ranked list दिखाओ।

---

## 💻 Code Example — Basic
```python
# Basic error handling - pure Python, runs directly
import json  # to parse LLM-like JSON text


def parse_llm_json(raw: str) -> dict:  # parse model output safely
    try:  # risky operation
        data = json.loads(raw)  # may raise JSONDecodeError
    except json.JSONDecodeError as exc:  # catch only the specific error
        print(f"bad json: {exc.msg}")  # report what went wrong
        return {}  # safe default
    else:  # runs only when no exception happened
        print("json ok")  # success path
        return data  # return parsed data
    finally:  # always runs
        print("parse attempt finished")  # cleanup/logging point


print(parse_llm_json('{"hs_code": "8517"}'))  # valid JSON
print(parse_llm_json('{"hs_code": "85'))  # truncated JSON (like max_tokens cut it)

try:  # demo of raising our own error
    raise ValueError("context too long")  # permanent error example
except ValueError as err:  # catch it
    print("handled:", err)  # handled: context too long
```

## 💻 Code Example — Advanced
```python
# Production: custom exceptions, backoff with jitter, timeout, validation retry, fallback
import asyncio  # async runtime
import json  # parse JSON
import random  # jitter
from pydantic import BaseModel, ValidationError  # validate output


class AIError(Exception):  # base class for all our errors
    """Base error for the AI layer."""


class TransientLLMError(AIError):  # worth retrying
    """429, 5xx, timeouts."""


class PermanentLLMError(AIError):  # not worth retrying
    """400, context too long, bad key."""


class Tariff(BaseModel):  # expected output
    hs_code: str  # code
    confidence: float  # score


calls = {"n": 0}  # demo counter


async def fake_llm(prompt: str) -> str:  # simulated flaky provider
    calls["n"] += 1  # count calls
    if calls["n"] == 1:  # first call fails
        raise TransientLLMError("429 rate limited")  # transient
    if calls["n"] == 2:  # second returns broken JSON
        return '{"hs_code": "8517", "confid'  # truncated
    return json.dumps({"hs_code": "8517.13", "confidence": 0.8})  # third is fine


async def call_with_retry(prompt: str, attempts: int = 4) -> str:  # retry only transient errors
    for attempt in range(1, attempts + 1):  # loop attempts
        try:  # protect call
            return await asyncio.wait_for(fake_llm(prompt), timeout=5)  # enforce timeout
        except (TransientLLMError, asyncio.TimeoutError) as exc:  # retryable
            if attempt == attempts:  # no attempts left
                raise TransientLLMError(f"gave up: {exc}") from exc  # chain the cause
            delay = min(8.0, 0.1 * 2 ** attempt) + random.uniform(0, 0.1)  # backoff + jitter
            await asyncio.sleep(delay)  # wait without blocking loop
        # PermanentLLMError is NOT caught here, so it propagates immediately
    raise AssertionError("unreachable")  # type checker helper


async def classify(description: str) -> Tariff:  # full pipeline
    prompt = f"Return JSON hs_code, confidence for: {description}"  # base prompt
    for validation_try in range(2):  # allow one correction round
        raw = await call_with_retry(prompt)  # network layer with retries
        try:  # validate the content
            return Tariff.model_validate_json(raw)  # parse + validate
        except ValidationError as exc:  # invalid output
            prompt += f"\nPrevious output was invalid: {exc.errors()[0]['type']}. Return valid JSON only."  # feedback
    raise PermanentLLMError("model kept returning invalid JSON")  # give up


async def safe_classify(description: str) -> dict:  # top-level with fallback
    try:  # try the LLM path
        result = await classify(description)  # may raise
        return {"source": "llm", **result.model_dump()}  # success
    except AIError as exc:  # any of our known errors
        print(f"fallback because: {exc}")  # log reason
        return {"source": "rules", "hs_code": "0000", "confidence": 0.0}  # degrade gracefully


async def main() -> None:  # demo
    print(await safe_classify("Android phone"))  # shows retry + validation retry + success
    print("llm calls:", calls["n"])  # 3


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Map internal errors to correct HTTP status codes with `exception_handler`, so clients get clean JSON and your logs show the cause.

```python
# FastAPI: convert AI errors into HTTP responses
from fastapi import FastAPI, Request  # framework
from fastapi.responses import JSONResponse  # custom response

app = FastAPI()  # app


class TransientLLMError(Exception): ...  # temporary provider problem
class ContextTooLongError(Exception): ...  # input too big


@app.exception_handler(TransientLLMError)  # register handler
async def transient_handler(request: Request, exc: TransientLLMError) -> JSONResponse:  # handler
    return JSONResponse(status_code=503, content={"detail": "AI service busy, retry soon"},
                        headers={"Retry-After": "5"})  # tell client when to retry


@app.exception_handler(ContextTooLongError)  # another handler
async def too_long_handler(request: Request, exc: ContextTooLongError) -> JSONResponse:  # handler
    return JSONResponse(status_code=413, content={"detail": "Document too large"})  # client error


@app.get("/boom")  # demo route
async def boom() -> dict:  # raises to show handler
    raise TransientLLMError("429 from provider")  # becomes a 503 JSON response
```

---

## 🔗 LangChain / LangGraph Connection
Runnables have built-in resilience: `.with_retry()` retries on exceptions with backoff, `.with_fallbacks([...])` switches to another model/chain when one fails. Output parsers raise `OutputParserException`; LangGraph lets you route to an error-handling node.

```python
# LangChain retry + fallback (needs API keys to actually run)
from langchain_openai import ChatOpenAI  # primary model

primary = ChatOpenAI(model="gpt-4o", timeout=10, max_retries=0)  # we handle retries ourselves
cheap = ChatOpenAI(model="gpt-4o-mini", timeout=10)  # fallback model

resilient = primary.with_retry(stop_after_attempt=3, wait_exponential_jitter=True).with_fallbacks([cheap])  # layered
# result = resilient.invoke("HS code for a laptop")  # retries 3x, then falls back to mini
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Bare `except:` / `except Exception: pass`
✅ Correct: catch specific errors and log.

```python
# Wrong: hides bugs, even KeyboardInterrupt with bare except
try:
    call_llm()
except:
    pass

# Right
try:
    call_llm()
except TimeoutError as exc:
    logger.warning("llm timeout: %s", exc)
    raise
```

❌ Mistake 2: Retrying everything forever
✅ Correct: retry only transient errors, with a max count and backoff.

```python
# Wrong: infinite loop, repeats a 400 error and burns tokens
while True:
    try:
        return call()
    except Exception:
        continue

# Right: bounded, backoff, specific
for i in range(3):
    try:
        return call()
    except RateLimitError:
        time.sleep(2 ** i)
```

❌ Mistake 3: Returning raw exception text (may include API keys or prompts) to users. Return a safe message and log the details server-side.

---

## 🧠 Tricky Interview Question

**Q**: "After a provider outage, your retries made things worse and your bill spiked. What went wrong?"

**Answer**: Many clients retried at the same moment with fixed delays (thundering herd), hammering the provider, and some retries re-sent full large prompts that the provider had already started billing. Fixes: exponential backoff with jitter; a retry budget (max attempts plus a global cap); a circuit breaker that stops calls for 30 seconds after N failures; honour the `Retry-After` header; idempotent request design; and fallback to cache or a cheaper model so users are not blocked.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `except Exception` and a bare `except`? (Easy)
A1: Bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, which you almost never want. `except Exception` is better but still broad. Prefer specific exceptions.

Q2: What do `else` and `finally` do in try blocks? (Easy)
A2: `else` runs only if no exception happened; `finally` always runs, for cleanup such as closing connections or releasing a semaphore.

Q3: Which LLM errors should be retried? (Medium)
A3: Retry rate limits (429), server errors (500/502/503), timeouts and connection resets. Do not retry 400 (bad request), 401/403 (auth), or context-length errors; they fail the same way every time. Invalid JSON can be retried once with feedback.

Q4: What is a circuit breaker? (Medium)
A4: A guard that counts consecutive failures; after a threshold it "opens" and fails fast (or uses the fallback) for a cooldown period, then lets one trial request through ("half-open"). It protects the provider and keeps your latency low during outages.

Q5: Design error handling for a streaming LLM response in FastAPI. (Hard)
A5: Once streaming starts, the HTTP status 200 is already sent, so you cannot change it. Catch exceptions inside the generator and send an `error` event in the stream (for SSE: `event: error`), then close it. Before streaming, do cheap validations (token count, auth) to return real 4xx codes. Use `try/finally` to close the upstream request if the client disconnects (check `request.is_disconnected()`), so you stop paying for tokens nobody reads.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any call to an external API (LLM, vector DB, Redis, Postgres)
- Parsing or validating LLM output
- You can offer a fallback or a clear message

❌ Avoid when:
- You would swallow errors silently just to make logs quiet
- Retrying non-idempotent actions (such as sending an email tool call) without a safeguard
- Catching `Exception` high up and returning 200 with an empty answer

---

## 📊 Visual Diagram
```
 request
    │
    ▼
 call LLM ──ok──> validate JSON ──ok──> return
    │                  │ invalid
    │ error            └─> retry once with feedback ──fail──┐
    ▼                                                       │
 transient? ──yes──> backoff+jitter ──> retry (max N) ──fail┤
    │ no (400/401/too long)                                  │
    ▼                                                        ▼
 clear 4xx error                                   fallback (rules / cheap model / cache)
```

---

## 💰 Cost Impact
Every failed or invalid response may still cost tokens, and each retry resends the prompt. A 2,000-token prompt retried 3 times costs 8,000 input tokens for one answer. Reduce waste by: not retrying permanent errors, capping attempts, retrying invalid JSON once only, setting adequate `max_tokens` (a truncated JSON is a wasted call), using structured output to cut invalid responses, and a circuit breaker during outages. Fallback to rules is free. Example: a 5 percent invalid-output rate on 100K calls at 700 tokens wastes 3.5M tokens, about $0.5/day on gpt-4o-mini input pricing, but far more on larger models.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exception | Runtime error object | runtime error object |
| Transient error | Temporary, retry may work | अस्थायी error |
| Permanent error | Retry will not help | स्थायी error |
| Backoff | Growing delay between retries | बढ़ता इंतज़ार |
| Jitter | Random delay to avoid sync | random देरी |
| Circuit breaker | Stops calls after repeated failure | बार-बार fail पर calls रोकना |
| Fallback | Backup plan | वैकल्पिक तरीका |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Catch specific exceptions, retry only transient failures with backoff and jitter, and validate LLM output. Always have a fallback and map errors to correct HTTP codes. Retries cost tokens, so cap them.
Hindi: Specific exceptions पकड़ो, सिर्फ़ transient failures को backoff और jitter से retry करो, और LLM output validate करो। हमेशा fallback रखो और errors को सही HTTP codes से map करो। Retries में tokens लगते हैं, इसलिए सीमा रखो।

---

## ➡️ Next Topic
**006. Python List Comprehensions + Generators for Data Processing** — after handling errors, we process large tariff datasets efficiently without loading everything in memory.
