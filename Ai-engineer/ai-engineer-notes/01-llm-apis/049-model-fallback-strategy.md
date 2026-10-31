---

# 049. Model Fallback Strategy
# हिंदी में: Model Fallback Strategy

---

## 🔵 Simple Definition (English)
A fallback strategy is a plan for what your app does when the main LLM call fails or is too slow: retry, switch to a backup model or provider, return a cached or safe answer. It keeps your product working during outages, rate limits and timeouts.

## 🔵 सरल परिभाषा (Hindi)
Fallback strategy एक plan है कि main LLM call fail या बहुत slow हो तो app क्या करेगी: retry, backup model/provider पर switch, या cached/safe जवाब। यह outages, rate limits और timeouts में भी product को चलता रखती है।

---

## 🔴 Problem it Solves
- Every provider has outages, 429 rate limits, 5xx errors and slow periods.
- Without a plan, one failed call becomes a user-facing error page.
- Retrying blindly can make an outage worse (retry storms).
- A single-model design is a single point of failure.

## 🔴 यह क्यों बना? (Hindi)
- हर provider में outages, 429 rate limits, 5xx errors और slow periods आते हैं।
- Plan न हो तो एक failed call user को error page दिखा देती है।
- अंधाधुंध retry outage को और बिगाड़ सकता है (retry storm)।
- Single-model design में एक ही जगह failure का खतरा रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify errors: retryable (429, 500, 503, timeout) vs not (400, 401, bad request)
Step 2 → Retry the same model with exponential backoff + jitter (2-3 attempts)
Step 3 → If still failing, switch to fallback model (same provider, smaller/other model)
Step 4 → If provider is down, switch to another provider
Step 5 → If all fail, return cache, a rule-based answer, or a graceful message
Step 6 → Use a circuit breaker: after N failures stop calling the bad model for a while
Step 7 → Log every fallback event with reason, model and latency
Step 8 → Test fallbacks regularly (chaos test); watch for quality differences
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Errors बाँटो: retryable (429, 500, 503, timeout) vs non-retryable (400, 401, bad request)
Step 2 → Same model पर exponential backoff + jitter के साथ retry (2-3 बार)
Step 3 → फिर भी fail हो तो fallback model (उसी provider का छोटा/दूसरा model)
Step 4 → Provider down हो तो दूसरे provider पर switch
Step 5 → सब fail हों तो cache, rule-based जवाब या सुंदर error message
Step 6 → Circuit breaker: N failures के बाद कुछ समय तक उस model को call मत करो
Step 7 → हर fallback event log करो (reason, model, latency)
Step 8 → Fallbacks को regularly test करो; quality का फ़र्क देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Primary: `gpt-4o`. If it returns 429 or 503 twice, fall back to `gpt-4o-mini`; if the provider is down, use a second provider; if everything fails, return the last cached classification for that product or mark the item "needs manual review". Customs filings never block on an AI outage.

**Zomato-style**: During dinner peak the main model hits rate limits; the support bot switches to a smaller model and keeps answering instead of showing errors.

## 🟡 Real Example Hindi mein
**Tariff System**: Primary: `gpt-4o`। अगर दो बार 429 या 503 आए तो `gpt-4o-mini` पर fallback; provider ही down हो तो दूसरा provider; सब fail हो तो उस product का आखिरी cached classification या "manual review चाहिए" mark। Customs filing AI outage की वजह से रुकती नहीं।

**Zomato-style**: Dinner peak में main model पर rate limit लगता है; support bot छोटे model पर switch होकर जवाब देता रहता है, error नहीं दिखाता।

---

## 💻 Code Example — Basic
```python
# Basic: try models in order; fake LLM so it runs offline
import random  # for fake failures

class LLMError(Exception):
    """Fake error raised by the mock model."""

def fake_call(model: str, prompt: str) -> str:
    # Pretend the big model is down, the small one works
    if model == "big-model":
        raise LLMError("503 service unavailable")  # simulate outage
    return f"[{model}] answer to: {prompt}"  # simulate success

def ask_with_fallback(prompt: str, models: list[str]) -> str:
    last_error: Exception | None = None  # remember last failure
    for model in models:  # try each model in order
        try:
            return fake_call(model, prompt)  # success -> return immediately
        except LLMError as exc:  # failure -> try next model
            print(f"{model} failed: {exc}")  # log the failure
            last_error = exc
    raise RuntimeError("All models failed") from last_error  # nothing worked

print(ask_with_fallback("HS code for earbuds?", ["big-model", "small-model"]))
```

## 💻 Code Example — Advanced
```python
# Production-style: async fallback chain with backoff, jitter, circuit breaker, cache
import asyncio  # sleep and timeouts
import random  # jitter
import time  # circuit breaker timing
from dataclasses import dataclass, field  # state
from openai import (AsyncOpenAI, APIConnectionError, APIStatusError,
                    APITimeoutError, RateLimitError)  # openai>=1 exceptions

client = AsyncOpenAI(max_retries=0, timeout=15.0)  # we do retries ourselves

RETRYABLE = (RateLimitError, APITimeoutError, APIConnectionError)  # safe to retry

@dataclass
class Breaker:
    failures: int = 0  # consecutive failures
    open_until: float = 0.0  # time until which the model is skipped

    def allow(self) -> bool:
        return time.monotonic() >= self.open_until  # closed or cooled down

    def record(self, ok: bool) -> None:
        if ok:
            self.failures = 0  # reset
        else:
            self.failures += 1  # count
            if self.failures >= 3:  # trip breaker
                self.open_until = time.monotonic() + 30  # skip for 30 s

@dataclass
class FallbackLLM:
    chain: list[str] = field(default_factory=lambda: ["gpt-4o", "gpt-4o-mini"])
    breakers: dict[str, Breaker] = field(default_factory=dict)
    cache: dict[str, str] = field(default_factory=dict)  # last good answers

    async def _one(self, model: str, prompt: str) -> str:
        resp = await client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=200)
        return resp.choices[0].message.content or ""

    async def ask(self, prompt: str) -> tuple[str, str]:
        for model in self.chain:  # walk the chain
            br = self.breakers.setdefault(model, Breaker())
            if not br.allow():  # breaker open: skip
                continue
            for attempt in range(3):  # retries on same model
                try:
                    text = await self._one(model, prompt)  # call
                    br.record(True)
                    self.cache[prompt] = text  # remember good answer
                    return text, model
                except RETRYABLE:
                    br.record(False)
                    # exponential backoff with jitter: 0.5, 1, 2 s (+ random)
                    await asyncio.sleep(0.5 * 2 ** attempt + random.random() * 0.3)
                except APIStatusError as exc:
                    br.record(False)
                    if exc.status_code >= 500:  # server error: retry
                        await asyncio.sleep(0.5 * 2 ** attempt)
                    else:  # 4xx (not 429): retrying will not help, try next model
                        break
        if prompt in self.cache:  # last resort 1: stale cache
            return self.cache[prompt], "cache"
        return "NEEDS_MANUAL_REVIEW", "none"  # last resort 2: safe default
```

---

## 🟠 FastAPI Integration
Return which model answered and whether it was a fallback, so dashboards and clients can react (for example show a "reduced accuracy" badge).

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
llm = FallbackLLM()  # one shared instance keeps breaker state

class Q(BaseModel):
    text: str  # product text

@app.post("/classify")
async def classify(q: Q) -> dict:
    answer, model = await llm.ask(f"HS code for: {q.text}")  # never raises for provider errors
    return {
        "answer": answer,
        "model": model,
        "degraded": model != llm.chain[0],  # True when fallback was used
        "needs_review": answer == "NEEDS_MANUAL_REVIEW",
    }
```

---

## 🔗 LangChain / LangGraph Connection
LangChain Runnables have `.with_fallbacks([...])` and `.with_retry(...)`. In LangGraph, model your fallback as conditional edges: on error, route to a "fallback" node.

```python
from langchain_openai import ChatOpenAI  # OpenAI models
from langchain_core.output_parsers import StrOutputParser  # parser

primary = ChatOpenAI(model="gpt-4o", timeout=15, max_retries=0).with_retry(
    stop_after_attempt=2)  # retry primary twice
backup = ChatOpenAI(model="gpt-4o-mini", timeout=15)  # cheaper backup
llm = primary.with_fallbacks([backup])  # use backup if primary raises
chain = llm | StrOutputParser()  # LCEL chain
# print(chain.invoke("HS code for earbuds?"))
# Cross-provider: backup = ChatAnthropic(...) from langchain_anthropic
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying every error immediately
✅ Correct: Retry only retryable errors, with exponential backoff and jitter.

```python
# Wrong: while True: try: call() except Exception: continue   # retry storm
# Right: for attempt in range(3): ... await asyncio.sleep(0.5 * 2**attempt + jitter)
```

❌ Mistake 2: Fallback model with different output format
✅ Correct: Validate output with a schema on both models.

```python
# Wrong: fallback returns prose, parser expects JSON -> crash
# Right: parse with pydantic after every model; if invalid -> next fallback / review
```

---

## 🧠 Tricky Interview Question
**Q**: "Your fallback to a cheaper model works, but a week later you notice accuracy fell 8% and nobody was alerted. How do you prevent this?"

**Answer**: Fallbacks hide failures. Log and metric every fallback (rate by reason and model), alert if the fallback rate crosses a threshold, tag responses as degraded, run evals on the fallback model too, and sample fallback outputs for human review. Also review whether the primary is failing too often (capacity, rate limits, timeouts too tight).

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which errors should you retry?
A1: Transient ones: 429 rate limit, 5xx server errors, timeouts and connection errors. Not 400/401/403 or content-policy errors.

Q2: [Easy] What is exponential backoff?
A2: Waiting longer after each failed attempt (0.5s, 1s, 2s...). Add random jitter so many clients do not retry at the same moment.

Q3: [Medium] What is a circuit breaker?
A3: A guard that stops calling a failing service after repeated failures for a cool-down period, then tests it again. It avoids wasting time and making an outage worse.

Q4: [Medium] Same-provider fallback or cross-provider fallback?
A4: Same-provider (another model) helps with model-specific rate limits and cost; cross-provider protects against provider-wide outages but needs prompt/format compatibility and extra keys, contracts and privacy review.

Q5: [Hard] How do you design fallback for a streaming chat?
A5: Fail fast on time to first token (for example 3 s). If failure happens before any token, switch models silently. If it happens mid-stream, you cannot cleanly splice; either show an error with a retry button, or buffer a short prefix server-side before sending. Keep the conversation state outside the model so the next turn works on any model.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Production features users depend on
- You face rate limits or strict SLAs
- Costly failures (legal, financial workflows)

❌ Avoid when:
- A quick prototype
- Backup model gives unsafe or much lower quality and a clear error is better

---

## 📊 Visual Diagram
```
request
   |
   v
[primary model] --ok--> answer
   | 429/5xx/timeout
   v
retry x2 (backoff + jitter) --ok--> answer
   | still failing
   v
[backup model] --ok--> answer (mark degraded)
   | failing
   v
[other provider] --ok--> answer (mark degraded)
   | failing
   v
cache / rules / "manual review"
   (circuit breaker skips known-bad models)
```

---

## 💰 Cost Impact
- Failed calls usually are not billed, but timeouts and partial streams may be. Retries on long prompts waste time and sometimes tokens.
- Falling back from a large to a small model reduces cost; falling back from small to large raises cost: put cheaper models later in the chain unless quality needs otherwise.
- Optimise: cap retries, use circuit breakers to avoid pointless calls, serve cache for repeats, monitor fallback rate and token usage per model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fallback | Backup path when main fails | मुख्य fail हो तो backup |
| Backoff | Increasing wait between retries | Retry के बीच बढ़ता इंतज़ार |
| Jitter | Random extra delay | Random अतिरिक्त देरी |
| Circuit breaker | Stops calls to failing service | Failing service को call रोकना |
| Degraded mode | Reduced quality service | कम quality पर चलना |
| Idempotent | Safe to repeat | दोबारा करना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Plan for failure: retry transient errors with backoff, then switch models or providers, then use cache or manual review. Use circuit breakers and log every fallback. Validate output formats on every model.
Hindi: Failure के लिए plan बनाओ: transient errors पर backoff के साथ retry, फिर model/provider बदलो, फिर cache या manual review। Circuit breaker लगाओ और हर fallback log करो। हर model का output format validate करो।

---

## ➡️ Next Topic
**050. LLM API Best Practices** — a checklist that ties together everything in this section.
