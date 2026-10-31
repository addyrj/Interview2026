---

# 310. Agent Error Handling
# हिंदी में: Agent में Error Handling

---

## 🔵 Simple Definition (English)
Agent error handling means planning for everything that can fail: the LLM API (rate limit, timeout), the tools (bad input, network), the model's output (invalid JSON, wrong tool) and the loop itself (infinite cycles). The agent should retry, fall back, or fail safely with a clear message, never crash or loop forever.

## 🔵 सरल परिभाषा (Hindi)
Agent error handling का मतलब है हर संभावित failure के लिए तैयारी: LLM API (rate limit, timeout), tools (गलत input, network), model का output (गलत JSON, गलत tool) और loop (अनंत चक्र)। Agent को retry करना, fallback लेना या साफ़ message के साथ सुरक्षित तरीके से fail होना चाहिए; crash या अनंत loop नहीं।

---

## 🔴 Problem it Solves
An agent chains many calls, so failure chance multiplies. If each step succeeds 95% of the time, a 6-step run succeeds only about 74%. Unhandled errors cause 500 responses, half-finished actions, duplicate charges, or runaway loops that burn tokens.

## 🔴 यह क्यों बना? (Hindi)
Agent कई calls जोड़ता है, इसलिए failure की संभावना गुणा होती है। हर step 95% सफल हो तो 6 steps में सिर्फ ~74% सफलता। Unhandled errors से 500 response, अधूरे actions, दोहरी charging या tokens जलाने वाले loops होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify the error: transient (429, timeout) vs permanent (400, bad args)
Step 2 → Transient → retry with exponential backoff + jitter (bounded)
Step 3 → Tool error → return error TEXT to the model so it can self-correct
Step 4 → Invalid model output → validate (pydantic), re-ask with the error message
Step 5 → Still failing → fallback (cheaper model, other provider, cached answer)
Step 6 → Loop guard: max_steps, max_tokens budget, repeated-call detection
Step 7 → Give up gracefully: partial result + clear error + log + alert
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Error को बाँटो: transient (429, timeout) या permanent (400)
Step 2 → Transient हो तो exponential backoff + jitter से सीमित retry
Step 3 → Tool error को text बनाकर model को लौटाओ ताकि वह खुद सुधारे
Step 4 → Output गलत हो तो validate करो और error बताकर दोबारा पूछो
Step 5 → फिर भी fail हो तो fallback (सस्ता model, दूसरा provider, cache)
Step 6 → Loop guard: max_steps, token budget, दोहराई calls की पहचान
Step 7 → अंत में आराम से हार मानो: partial result + साफ़ error + alert
```

---

## 🟡 Real World Example
**Tariff Classification System**: The rate-lookup service times out. The agent retries twice with backoff. Still down, so it returns "HS code found (8518.22), duty rate temporarily unavailable" instead of failing the whole request. Separately, if the LLM returns an HS code like "85.18" (invalid format), validation rejects it and the agent asks again with the format rule.

**Zomato-style**: payment gateway fails, so the agent offers cash on delivery rather than an error page.

## 🟡 Real Example Hindi mein
**Tariff System**: Rate-lookup service timeout हो जाती है। Agent backoff के साथ दो बार retry करता है। फिर भी down हो तो पूरा request fail करने की बजाय "HS code मिला (8518.22), duty rate अभी उपलब्ध नहीं" लौटाता है। LLM ने "85.18" जैसा invalid code दिया तो validation उसे reject करके format rule के साथ दोबारा पूछता है।
**Zomato**: Payment fail हो तो error page की जगह cash on delivery का विकल्प।

---

## 💻 Code Example — Basic
```python
# Basic: retry with backoff + tool error returned as text + loop guard (offline).
import random                                   # jitter
import time                                     # sleep
from typing import Callable, TypeVar            # typing

T = TypeVar("T")

class TransientError(Exception):                # retryable error type
    pass

def retry(fn: Callable[[], T], attempts: int = 3, base: float = 0.1) -> T:
    for i in range(attempts):                   # bounded attempts
        try:
            return fn()                         # success -> return
        except TransientError:                  # only retry transient errors
            if i == attempts - 1:               # last attempt -> give up
                raise
            time.sleep(base * (2 ** i) + random.random() * 0.05)   # backoff + jitter
    raise RuntimeError("unreachable")           # for type checkers

calls = {"n": 0}                                # fake flaky service state

def flaky_rate_lookup() -> str:
    calls["n"] += 1                             # count calls
    if calls["n"] < 3:                          # fail twice
        raise TransientError("timeout")
    return "12.5%"                              # succeed on 3rd

def safe_tool(fn: Callable[[], str]) -> str:
    try:
        return retry(fn)                        # retry transient failures
    except TransientError:
        return "TOOL_ERROR: service unavailable, try again later"   # model-readable text
    except Exception as exc:                    # unknown bug
        return f"TOOL_ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    print(safe_tool(flaky_rate_lookup))         # 12.5% after retries
```

## 💻 Code Example — Advanced
```python
# Production: async retries, validation re-ask, fallback model, budget guard.
import asyncio                                  # async
import json                                     # parse output
import logging
import random
from typing import Awaitable, Callable
from pydantic import BaseModel, Field, ValidationError   # pydantic v2

log = logging.getLogger("agent.errors")

class Classification(BaseModel):                # strict output contract
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")   # e.g. 8518.22
    confidence: float = Field(ge=0, le=1)

class BudgetExceeded(Exception):
    pass

class Budget:                                   # token + step guard
    def __init__(self, max_tokens: int, max_steps: int) -> None:
        self.max_tokens, self.max_steps = max_tokens, max_steps
        self.tokens = self.steps = 0
    def charge(self, tokens: int) -> None:
        self.tokens += tokens; self.steps += 1
        if self.tokens > self.max_tokens or self.steps > self.max_steps:
            raise BudgetExceeded(f"tokens={self.tokens} steps={self.steps}")

LLM = Callable[[str, str], Awaitable[tuple[str, int]]]   # (model, prompt) -> (text, tokens)

async def call_with_retry(llm: LLM, model: str, prompt: str, attempts: int = 3) -> tuple[str, int]:
    for i in range(attempts):
        try:
            return await asyncio.wait_for(llm(model, prompt), timeout=20)   # per-call timeout
        except (asyncio.TimeoutError, ConnectionError) as exc:               # transient
            log.warning("attempt %d failed: %s", i + 1, exc)
            await asyncio.sleep(0.2 * 2 ** i + random.random() * 0.1)        # backoff
    raise ConnectionError("LLM unavailable after retries")

async def classify(llm: LLM, product: str, budget: Budget) -> Classification:
    prompt = f'Return JSON {{"hs_code":"NNNN.NN","confidence":0-1}} for: {product}'
    for model in ("primary-model", "fallback-model"):         # fallback chain
        for _ in range(2):                                     # re-ask on invalid output
            try:
                text, tokens = await call_with_retry(llm, model, prompt)
                budget.charge(tokens)                          # enforce budget
                return Classification.model_validate(json.loads(text))   # validate
            except (json.JSONDecodeError, ValidationError) as exc:
                prompt += f"\nYour last answer was invalid: {exc}. Fix it."   # self-correct
            except ConnectionError:
                break                                          # go to next model
    raise RuntimeError("classification failed on all models")

async def fake_llm(model: str, prompt: str) -> tuple[str, int]:   # offline demo
    if model == "primary-model":
        raise ConnectionError("down")
    return '{"hs_code": "8518.22", "confidence": 0.9}', 120

async def main() -> None:
    result = await classify(fake_llm, "bluetooth speaker", Budget(2000, 5))
    print(result)                                          # fallback model used

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException      # framework
from pydantic import BaseModel

app = FastAPI()

class Req(BaseModel):
    product: str

@app.post("/classify")
async def classify_route(req: Req) -> dict:
    try:
        res = await classify(fake_llm, req.product, Budget(2000, 5))   # from above
        return res.model_dump()
    except BudgetExceeded:
        raise HTTPException(429, "Request exceeded its token/step budget")   # client problem/limit
    except ConnectionError:
        raise HTTPException(503, "Model providers unavailable, retry later")  # temporary
    except RuntimeError as exc:
        raise HTTPException(502, str(exc))                                    # bad upstream result
```
Map errors to the right HTTP code: 4xx for caller mistakes, 429 for limits, 502/503 for upstream failures. Never leak stack traces or API keys.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI                   # models
from langchain_core.runnables import RunnableLambda       # wrap functions

primary = ChatOpenAI(model="gpt-4o", max_retries=2, timeout=20)         # built-in retries
backup = ChatOpenAI(model="gpt-4o-mini", max_retries=2, timeout=20)
llm = primary.with_fallbacks([backup])                    # automatic fallback on exception

# Retry any runnable with backoff:
flaky = RunnableLambda(lambda x: x).with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
```
LangGraph: set `recursion_limit` in the config (`{"recursion_limit": 25}`) to stop runaway loops; it raises `GraphRecursionError`, which you should catch. Prebuilt `ToolNode` can return tool errors as messages (`handle_tool_errors=True`) so the model sees them.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Retrying everything, including 400 errors.
✅ Correct: retry only transient errors (429, 5xx, timeouts).

```python
# Wrong
except Exception: retry()
# Right
except (RateLimitError, APITimeoutError): retry()
```

❌ Mistake 2: Raising a tool exception that kills the whole run.
✅ Correct: catch and return `TOOL_ERROR: ...` so the model can adjust.

❌ Mistake 3: Retrying a non-idempotent action (charge, email).
✅ Correct: use idempotency keys or do not auto-retry.

---

## 🧠 Tricky Interview Question
**Q**: "Your agent retries on failure, but a customer was charged twice. Why?"

**Answer**: The first call to the payment tool actually succeeded, but the response timed out, so the retry charged again. Timeouts mean "unknown outcome", not "failed". Fix with an idempotency key (same key on retry, so the provider returns the original result), check state before retrying, and do not auto-retry side-effect tools without that protection.

---

## ⚫ Interview Questions + Answers

Q1: Which errors should be retried?
A1: Transient ones: rate limits (429), server errors (5xx), timeouts and connection resets. Not 400/401/403 or validation errors.

Q2: What is exponential backoff with jitter?
A2: Wait longer after each failure (0.2s, 0.4s, 0.8s...) plus random noise so many clients do not retry at the same moment.

Q3: How do you handle invalid JSON from the LLM?
A3: Use structured output / tool calling where possible, validate with pydantic, and if invalid, re-ask with the validation error, limited to 1-2 tries.

Q4: How do you prevent infinite agent loops?
A4: `max_steps`, LangGraph `recursion_limit`, token budget, and detection of repeated identical tool calls.

Q5: (Hard) Design a fallback strategy across providers with different tool formats.
A5: Put an abstraction layer (LangChain `with_fallbacks` or LiteLLM) so tools are defined once. Order by quality/cost, use circuit breakers to skip a provider that keeps failing, test the fallback model with the same eval set, normalise outputs through the same pydantic schema, and log which model answered.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always in production; every external call can fail
- Tools have side effects
- Costs must be bounded

❌ Avoid when:
- Over-retrying makes outages worse (retry storms); cap attempts
- Hiding errors silently; always log and surface them

---

## 📊 Visual Diagram
```
 call ──► ok? ──yes──► continue
           │no
           ▼
   transient? ──yes──► backoff+jitter ──► retry (max N)
           │no                               │ still failing
           ▼                                 ▼
  return TOOL_ERROR to model ◄────── fallback model/provider
           │                                 │ all failed
           ▼                                 ▼
   model self-corrects              partial result + alert
   (budget / step guard around everything)
```

---

## 💰 Cost Impact
Retries and re-asks cost tokens. A re-ask resends the whole prompt plus the error text. Failed calls that time out may still be billed on the provider side. Optimise: limit retries to 2-3, use structured output to avoid invalid JSON, enforce a per-request token budget, use cheaper fallback models, and cache successful results so a retry of the whole request is not re-billed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transient error | Temporary failure | अस्थायी error |
| Backoff | Growing wait between retries | Retry के बीच बढ़ती प्रतीक्षा |
| Jitter | Random delay noise | यादृच्छिक देरी |
| Fallback | Backup model/path | बैकअप विकल्प |
| Idempotency key | Makes repeats safe | दोहराव को सुरक्षित बनाने वाली key |
| Circuit breaker | Stops calling a failing service | खराब service को बंद रखना |

---

## ⚡ 3-Line Summary
English: Classify errors, retry only transient ones with backoff, and return tool errors to the model as text. Validate outputs, fall back to another model, and guard loops with step and token budgets. Never retry side effects without idempotency.
Hindi: Errors को बाँटो, सिर्फ transient errors को backoff के साथ retry करो और tool errors model को text में लौटाओ। Output validate करो, fallback model रखो, और step/token budget से loop रोको। Side effects को idempotency के बिना retry मत करो।

---

## ➡️ Next Topic
**311. Agent Streaming** — sending tokens and step updates to the user live, so errors and waits feel smaller.
