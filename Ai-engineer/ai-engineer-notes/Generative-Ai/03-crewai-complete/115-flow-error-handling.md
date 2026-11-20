---

# 115. Flow Error Handling
# हिंदी में: Flow में Error Handling (गलतियों को संभालना)
# Framework: CrewAI
# Already Known: No

> Verified against crewai 1.15.41 (offline, fake LLM). Observed: an unhandled exception inside a Flow step fails the flow and `kickoff()` re-raises the original exception.

---

## 🔵 Simple Definition (2-3 lines)
Flow error handling means deciding what happens when a step raises: retry it, fall back to a safe answer, route to a "failed" branch, or surface a clean error to the API caller. You do it with `try/except` inside steps, a retry helper, a router that reads `self.state.error`, and a catch around `kickoff`.

## 🔵 सरल परिभाषा (Hindi)
Flow error handling का मतलब है तय करना कि जब कोई step exception फेंके तो क्या हो: दोबारा try करो, सुरक्षित fallback दो, "failed" branch पर भेजो, या API caller को साफ़ error दो। यह step के अंदर `try/except`, retry helper, `self.state.error` पढ़ने वाले router और `kickoff` के चारों ओर catch से होता है।

---

## 🔴 Problem it Solves
LLM calls fail: rate limits, timeouts, malformed output, tool errors. If a Flow has no handling, one flaky call kills the whole request, wastes tokens already spent and returns a stack trace. Worse, retrying blindly can double-charge tokens or repeat side effects (sending an email twice).

## 🔴 यह क्यों बना? (Hindi)
LLM calls फेल होती हैं: rate limit, timeout, गलत format का output, tool error। अगर Flow में handling नहीं है तो एक कमज़ोर call पूरा request गिरा देती है, पहले खर्च हुए tokens बेकार जाते हैं और user को stack trace मिलता है। अंधाधुंध retry से tokens दोगुने खर्च हो सकते हैं या side effect दोहराए जा सकते हैं (email दो बार जाना)।

---

## 🟢 How it Works

```
Step 1 → Wrap the risky call (crew.kickoff) in try/except inside the step
Step 2 → Retry only transient errors (timeout, 429) with exponential backoff
Step 3 → On final failure: set self.state.error, do NOT re-raise
Step 4 → @router reads state.error -> returns "failed" or "ok"
Step 5 → "failed" branch: fallback answer / queue for manual / alert
Step 6 → Outside: try/except around flow.kickoff for unexpected crashes
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → जोखिम वाली call (crew.kickoff) को step के अंदर try/except में रखो
Step 2 → सिर्फ़ अस्थायी errors (timeout, 429) पर exponential backoff से retry करो
Step 3 → आख़िरी बार फेल हो तो self.state.error भरो, दोबारा raise मत करो
Step 4 → @router state.error देखकर "failed" या "ok" लौटाए
Step 5 → "failed" branch: fallback जवाब / manual queue / alert
Step 6 → बाहर: अनपेक्षित crash के लिए flow.kickoff पर try/except
```

---

## 🟡 Real World Example
**Tariff Agent**: the LLM provider returns a 429 during peak hours. The Flow retries twice with backoff; if still failing it returns the last known rate-table answer flagged `degraded=True` and queues the item for later reprocessing, instead of returning HTTP 500 to the customs broker.

## 🟡 Real Example Hindi mein
**Tariff Agent**: peak समय पर LLM provider 429 लौटाता है। Flow backoff के साथ दो बार retry करता है; फिर भी फेल हो तो rate-table वाला पुराना जवाब `degraded=True` के साथ देता है और item को बाद में दोबारा चलाने के लिए queue में डालता है, customs broker को HTTP 500 नहीं देता।

---

## 💻 Code Example — Basic
```python
# Run directly: python flow_errors_basic.py (offline)
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
from pydantic import BaseModel                         # typed state
from crewai import Flow                                # Flow base class
from crewai.flow.flow import listen, start, router     # decorators


class S(BaseModel):                                    # state with an error slot
    ok: bool = False                                   # did the risky step succeed
    error: str = ""                                    # error text if it failed
    answer: str = ""                                   # final answer


class SafeFlow(Flow[S]):
    @start()
    def risky(self) -> None:
        try:                                           # protect the risky call
            raise TimeoutError("llm timeout")          # simulate a provider failure
        except TimeoutError as e:                      # catch only what we expect
            self.state.error = f"{type(e).__name__}: {e}"  # remember, do not crash

    @router(risky)                                     # choose path from state
    def check(self) -> str:
        return "failed" if self.state.error else "ok"

    @listen("ok")
    def good(self) -> str:
        return "normal answer"

    @listen("failed")
    def fallback(self) -> str:
        self.state.answer = "fallback: HS 6109.10 (degraded)"  # safe default
        return self.state.answer


print(SafeFlow().kickoff())                            # -> fallback: HS 6109.10 (degraded)

class Crashy(Flow[S]):                                 # NO handling inside
    @start()
    def boom(self) -> None:
        raise ValueError("boom")

try:
    Crashy().kickoff()                                 # exception surfaces here
except ValueError as e:                                # catch at the boundary
    print("caught", type(e).__name__, e)               # -> caught ValueError boom
```
Ran offline: prints the fallback line and `caught ValueError boom` (CrewAI also prints a red "Flow Failed" panel to the console).

## 💻 Code Example — Advanced
```python
# Production-style: retry with backoff + failed branch + FastAPI + usage tracking
import asyncio                                         # async sleep/timeout
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
from typing import Any, Awaitable, Callable, TypeVar   # typing helpers
from fastapi import FastAPI, HTTPException             # API layer
from fastapi.testclient import TestClient              # offline test
from pydantic import BaseModel                         # models
from crewai import Agent, Task, Crew, BaseLLM, Flow   # CrewAI core
from crewai.flow.flow import listen, start, router     # decorators

T = TypeVar("T")                                       # generic return type
CURRENT_LLM: list[Any] = []                            # demo hook: which LLM the flow uses


class TransientError(Exception):                       # errors worth retrying
    pass


async def retry(fn: Callable[[], Awaitable[T]], attempts: int = 3, base: float = 0.01) -> T:
    last: Exception | None = None                      # remember last failure
    for i in range(attempts):                          # bounded loop, never infinite
        try:
            return await fn()                          # success -> return
        except TransientError as e:                    # only retry transient errors
            last = e
            await asyncio.sleep(base * (2 ** i))       # exponential backoff
    assert last is not None
    raise last                                         # give up with the real error


class FlakyLLM(BaseLLM):                               # fails twice, then works
    def __init__(self) -> None:
        super().__init__(model="fake"); self.n = 0
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        self.n += 1
        if self.n <= 2:
            raise TransientError("429 rate limited")   # simulated provider error
        return "Thought: ok\nFinal Answer: HS 6109.10"
    def supports_function_calling(self) -> bool:
        return False


class S(BaseModel):
    item: str = ""
    hs_code: str = ""
    error: str = ""
    degraded: bool = False
    attempts_used: int = 0


class TariffFlow(Flow[S]):
    @start()
    async def classify(self) -> None:
        async def once() -> str:                       # one attempt = one crew run
            self.state.attempts_used += 1
            agent = Agent(role="A", goal="HS", backstory="x", llm=CURRENT_LLM[0],
                          allow_delegation=False, max_retry_limit=0)  # we retry ourselves
            task = Task(description="Classify {item}", expected_output="HS", agent=agent)
            crew = Crew(agents=[agent], tasks=[task], tracing=False)
            try:
                out = await crew.kickoff_async(inputs={"item": self.state.item})
            except TransientError:
                raise
            except Exception as e:                     # CrewAI may wrap provider errors
                if "429" in str(e):
                    raise TransientError(str(e)) from e
                raise
            return out.raw
        try:
            self.state.hs_code = await retry(once)     # retried call
        except Exception as e:                         # final failure -> record, don't crash
            self.state.error = f"{type(e).__name__}: {e}"

    @router(classify)
    def gate(self) -> str:
        return "failed" if self.state.error else "ok"

    @listen("ok")
    def on_ok(self) -> dict[str, Any]:
        return {"hs": self.state.hs_code, "degraded": False, "attempts": self.state.attempts_used}

    @listen("failed")
    def on_failed(self) -> dict[str, Any]:
        self.state.degraded = True                     # tell the caller it is a fallback
        return {"hs": "6109.10", "degraded": True, "error": self.state.error}


app = FastAPI()


class Req(BaseModel):
    item: str


@app.post("/tariff")
async def tariff(req: Req) -> dict[str, Any]:
    CURRENT_LLM[:] = [FlakyLLM()]                      # demo: fresh flaky model per request
    try:
        return await asyncio.wait_for(TariffFlow().kickoff_async(inputs={"item": req.item}), 60)
    except asyncio.TimeoutError:
        raise HTTPException(504, "timeout")
    except Exception as e:
        raise HTTPException(502, f"flow failed: {type(e).__name__}")


with TestClient(app) as c:
    print(c.post("/tariff", json={"item": "shirt"}).json())
```
Ran offline. Printed `{'hs': 'HS 6109.10', 'degraded': False, 'attempts': 1}`. Interesting observation on crewai 1.15.41: although the fake LLM raised twice, our `retry()` counted only 1 attempt, meaning CrewAI's own agent executor already retried the failing LLM call internally (the `max_retry_limit=0` setting did not stop that). So do not assume your outer retry is the only retry layer: measure, and avoid stacking retries (retries multiply token cost because each one re-sends the whole prompt). The failed-branch path (`on_failed`) was not exercised by this run; the basic example exercises the same router pattern.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Node-level retry | `RetryPolicy` on nodes | Own helper / `max_retry_limit` on Agent | Own helper / `ModelSettings` retries | Own helper |
| Error branch | Conditional edge on error state | `@router` on `state.error` | Python `try/except` | Termination / custom |
| Checkpoint & resume | Checkpointer | `@persist` + `resume` | Sessions | Save/load state |
| Guardrails on output | Custom nodes | Task `guardrail` | Output guardrails | Custom |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `except Exception: pass` — silently swallowing errors.
✅ Correct: Record `state.error`, log with a request id, and route to a fallback branch.

❌ Mistake 2: Retrying non-idempotent steps (send email, charge card).
✅ Correct: Retry only pure/idempotent steps; add idempotency keys for side effects.

❌ Mistake 3: Naming a handler the same as the label it listens to (`@listen("failed") def failed(...)`). CrewAI 1.15.41 rejects this with a ValidationError ("references the handler name ... infinite loop").
✅ Correct: Name handlers differently from labels (`on_failed`, `on_ok`).

❌ Mistake 4: Infinite or very large retry loops.
✅ Correct: Cap attempts, add backoff and jitter, and cap total time with `asyncio.wait_for`.

---

## 🧠 Tricky Interview Question
A Flow step succeeded on the LLM call but your DB write failed. On retry the LLM runs again and you pay twice. How do you avoid it?

Answer: Split the steps: step A (LLM) stores its result in `self.state` (and persist it with `@persist`); step B (DB write) retries separately using the stored result. With persistence you can also `resume` from the failed step instead of re-running the crew. Add an idempotency key to the DB write.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What happens to `flow.kickoff()` if a step raises?
A1: The flow is marked failed and the original exception propagates to the caller (observed on 1.15.41). Catch it at the boundary.

Q2: [Medium] Which errors should be retried?
A2: Transient ones: timeouts, 429, 5xx. Not validation errors or bad prompts.

Q3: [Hard] How do you keep token cost under control while retrying?
A3: Cap attempts, shrink the prompt on retry, cache successful sub-results in state, and switch to a cheaper model on the last attempt.

Q4: [Hard] Where do guardrails fit?
A4: A Task `guardrail` callable validates the output and triggers a regeneration (bounded by `guardrail_max_retries`) before the Flow ever sees bad data.

Q5: [System Design] Design failure handling for a batch of 10,000 classification jobs.
A5: Queue each job, per-job try/except, dead-letter queue after N tries, persisted flow state for resume, circuit breaker on provider errors, metrics on error rate and token spend.

---

## 💰 Cost Impact
- Each retry resends the full prompt: cost multiplies by the number of attempts in the failing case. Formula: `expected_cost = base_cost x (1 + p_fail + p_fail^2 ...)`.
- Tips: fail fast on non-transient errors, cap retries (2-3), cache partial results in state, degrade to a rule-based fallback instead of a 4th LLM call. Concrete token numbers depend on your model; measure them.

---

## 🔷 When to Use
✅ Use when:
- Any production Flow that calls LLMs or tools
- You need graceful degradation and clear API errors

❌ Avoid when:
- Quick local experiments (let it crash, read the trace)
- Retrying side-effecting steps without idempotency

---

## 📊 Visual Diagram
```
 classify (try/except + retry x3)
     |                  \
   success             fail (state.error set)
     |                    |
   @router ---- "ok" ---> answer
     \------- "failed" --> fallback (degraded=True) + queue/alert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transient error | Temporary, retry may work | अस्थायी error |
| Backoff | Growing wait between retries | retry के बीच बढ़ता इंतज़ार |
| Idempotent | Safe to repeat | दोहराने पर भी सुरक्षित |
| Fallback | Safe alternative result | सुरक्षित विकल्प |
| Degraded | Reduced-quality response | घटी हुई गुणवत्ता का जवाब |

---

## ⚡ 3-Line Summary
English: Catch inside steps, retry only transient errors with backoff, record `state.error` and route to a failed branch. Never swallow errors silently. Retries cost tokens, so cap them.
Hindi: Step के अंदर catch करो, सिर्फ़ अस्थायी errors पर backoff से retry करो, `state.error` भरकर failed branch पर भेजो। errors चुपचाप मत दबाओ। Retry में tokens लगते हैं, इसलिए सीमा रखो।

---

## ➡️ Next Topic
**116. CrewAI Planning** — before running tasks, a planner can write a step-by-step plan, reducing wasted tool calls and errors.

---
