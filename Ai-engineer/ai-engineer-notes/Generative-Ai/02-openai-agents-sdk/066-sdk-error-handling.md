---

# 66. SDK Error Handling
# हिंदी में: SDK में Error Handling
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real API failures (rate limits 429, network timeouts, 5xx from OpenAI) were NOT reproduced - they need a real endpoint; only the SDK-level failure modes were run.

---

## 🔵 Simple Definition (2-3 lines)
An agent run can fail in four distinct ways: a tool raises, the loop never ends (`MaxTurnsExceeded`), the model produces something invalid like a non-existent tool (`ModelBehaviorError`), or a tool hangs. Each needs a different response: tell the model, give a safe final answer, retry, or return an HTTP error.

## 🔵 सरल परिभाषा (Hindi)
Agent run चार अलग तरीकों से fail हो सकता है: tool exception दे, loop कभी खत्म न हो (`MaxTurnsExceeded`), model अमान्य चीज़ बनाए जैसे अस्तित्वहीन tool (`ModelBehaviorError`), या tool अटक जाए। हर एक का जवाब अलग है: model को बताना, सुरक्षित final answer देना, retry करना, या HTTP error लौटाना।

---

## 🔴 Problem it Solves
Without a plan, one flaky tool crashes the request with a 500, a confused model loops until you burn tokens, and a hanging API holds the connection open forever. Users see stack traces, and you pay for runs that never succeed.

## 🔴 यह क्यों बना? (Hindi)
योजना के बिना, एक अस्थिर tool पूरी request को 500 से गिरा देता है, भ्रमित model तब तक loop करता है जब तक tokens जल न जाएँ, और अटकी API connection को हमेशा खुला रखती है। Users को stack traces दिखते हैं और आप ऐसे runs का पैसा देते हैं जो कभी सफल नहीं होते।

---

## 🟢 How it Works

```
Failure                         Default behaviour (0.24.0, observed in b66)        Your lever
1 tool raises ValueError        SDK sends "An error occurred while running         failure_error_function=
                                the tool. Please try again." to the LLM;           None => re-raise (wrapped
                                run continues                                      as UserError)
2 tool hangs                    waits forever unless you set a timeout             @function_tool(timeout=0.2,
                                                                                   timeout_behavior="error_as_result")
3 loop never ends               raises MaxTurnsExceeded("Max turns (2) exceeded")  max_turns=, error_handlers=
                                                                                   {"max_turns": fn}
4 model calls unknown tool      raises ModelBehaviorError                          catch + retry with backoff
                                ("Tool nope not found in agent A")
base class of SDK errors: AgentsException  (catch last, map to 500)
```

## 🟢 कैसे काम करता है? (Hindi)

```
विफलता                          Default व्यवहार (0.24.0, b66 में देखा)              आपका lever
1 tool ValueError raise करे     SDK LLM को "An error occurred while running        failure_error_function=
                                the tool. Please try again." भेजता है;             None => फिर से raise
                                run चलता रहता है                                   (UserError में लपेटकर)
2 tool अटक जाए                 timeout न दें तो हमेशा इंतज़ार                      @function_tool(timeout=0.2,
                                                                                   timeout_behavior="error_as_result")
3 loop खत्म न हो                MaxTurnsExceeded("Max turns (2) exceeded")         max_turns=, error_handlers=
                                                                                   {"max_turns": fn}
4 model अज्ञात tool बुलाए       ModelBehaviorError                                 पकड़ें + backoff के साथ retry
                                ("Tool nope not found in agent A")
सभी SDK errors का base class: AgentsException (आख़िर में पकड़ें, 500 map करें)
```

**Verified outputs (basic sample):**
```
1: sorry, try later | An error occurred while running the tool. Please try again.
2: UserError - Error running tool strict: db down
3: Max turns (2) exceeded
4: Tool nope not found in agent A
```
Advanced sample outputs: `timeout 200 {'answer': 'Service slow; try later.'}`, `loop 200 {'answer': 'I could not finish in time; a human will follow up.'}`, `ghost 502 {'detail': 'model error: Tool ghost not found in agent A'}`.

**Hindi नोट:** Default में tool का error model को text के रूप में जाता है ताकि वह खुद सुधार करे (दूसरे arguments, माफ़ी)। यह अच्छा है, पर इसका मतलब है कि error छिपा रहता है; अपने logs में tool errors ज़रूर गिनें (hook `on_tool_end` में result की जाँच)। असली API errors (429, 5xx, network) अलग परत हैं: उन्हें client-level retry और backoff से संभालें।

---

## 🟡 Real World Example
**Tariff Agent.** The customs API is slow. With `timeout=0.2, timeout_behavior="error_as_result"` the tool returns an error message to the LLM, which answers "Service slow; try later" instead of hanging. If the model keeps calling tools forever, `error_handlers={"max_turns": on_max_turns}` replaces the exception with "a human will follow up". If the model invents a tool, the API retries, then returns 502.

**Customer Support Agent:** refund tool uses `failure_error_function=None` so a payment failure is never hidden from the model; your code catches it and opens a ticket.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Customs API धीमी है। `timeout=0.2, timeout_behavior="error_as_result"` के साथ tool LLM को error संदेश लौटाता है और LLM अटकने की बजाय "Service slow; try later" कहता है। अगर model अनंत tool calls करे, तो `error_handlers={"max_turns": on_max_turns}` exception की जगह "a human will follow up" देता है। अगर model कोई नकली tool गढ़ दे, तो API retry करती है और फिर 502 लौटाती है।

**Customer Support Agent:** refund tool `failure_error_function=None` रखता है ताकि payment failure कभी छिपे नहीं; आपका code उसे पकड़कर ticket खोलता है।

---

## 💻 Code Example — Basic
Shows all four failure modes in one script (offline).

```python
# Basic: the 4 failure modes of an SDK run and how each surfaces (offline).
# verified against openai-agents 0.24.0
import asyncio
from agents import Agent, MaxTurnsExceeded, ModelBehaviorError, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
def flaky(x: str) -> str:
    """Always raises."""
    raise ValueError("db down")                                   # default: SDK turns this into a message for the LLM

@function_tool(failure_error_function=None)                       # None => do NOT swallow, re-raise instead
def strict(x: str) -> str:
    """Always raises, loudly."""
    raise ValueError("db down")

def run(model: ScriptedModel, tools: list, **kw):                 # helper
    return Runner.run(Agent(name="A", instructions="x", model=model, tools=tools), "q", **kw)

async def main() -> None:
    # 1) tool exception -> text observation, run continues
    r = await run(ScriptedModel([[tool_call("flaky", '{"x":"a"}')], [text("sorry, try later")]]), [flaky])
    print("1:", r.final_output, "|", r.new_items[1].output)       # model saw: 'An error occurred while running the tool...'
    # 2) failure_error_function=None -> exception reaches YOUR code (wrapped in UserError)
    try: await run(ScriptedModel([[tool_call("strict", '{"x":"a"}')], [text("x")]]), [strict])
    except Exception as e: print("2:", type(e).__name__, "-", e)
    # 3) loop never ends -> MaxTurnsExceeded
    try: await run(ScriptedModel([[tool_call("flaky", '{"x":"a"}')]]), [flaky], max_turns=2)
    except MaxTurnsExceeded as e: print("3:", e)
    # 4) model calls a tool that does not exist -> ModelBehaviorError
    try: await run(ScriptedModel([[tool_call("nope", "{}")]]), [])
    except ModelBehaviorError as e: print("4:", e)

asyncio.run(main())
```

## 💻 Code Example — Advanced
FastAPI: tool timeout, graceful max-turns handler, retry with jittered backoff for `ModelBehaviorError`, and exception-to-HTTP mapping.

```python
# Advanced: retries with backoff, a graceful max-turns handler, tool timeouts and HTTP error mapping.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import asyncio, random
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import (Agent, AgentsException, MaxTurnsExceeded, ModelBehaviorError, RunErrorHandlerInput,
                    RunErrorHandlerResult, Runner, function_tool, set_tracing_disabled)
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool(timeout=0.2, timeout_behavior="error_as_result")   # slow tool -> message to the LLM instead of hanging
async def customs_api(hs_code: str) -> str:
    """Call the (slow) customs service."""
    await asyncio.sleep(2)                                        # simulated hang
    return "never"

def on_max_turns(data: RunErrorHandlerInput[None]) -> RunErrorHandlerResult:
    # Called instead of raising MaxTurnsExceeded; we choose a safe final answer.
    return RunErrorHandlerResult(final_output="I could not finish in time; a human will follow up.")

async def run_with_retry(agent: Agent, prompt: str, attempts: int = 3) -> Any:
    for i in range(attempts):
        try:
            return await Runner.run(agent, prompt, max_turns=2, error_handlers={"max_turns": on_max_turns})
        except ModelBehaviorError:                                # transient bad output: retry with jittered backoff
            if i == attempts - 1:
                raise
            await asyncio.sleep(min(2 ** i, 5) * random.uniform(0.5, 1.0) * 0.01)   # tiny delay in the demo
    raise RuntimeError("unreachable")

class Q(BaseModel):
    question: str
    mode: str = "timeout"

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    if q.mode == "timeout":                                       # tool times out -> LLM explains gracefully
        m = ScriptedModel([[tool_call("customs_api", '{"hs_code":"1"}')], [text("Service slow; try later.")]])
    elif q.mode == "loop":                                        # never finishes -> handler supplies the answer
        m = ScriptedModel([[tool_call("customs_api", '{"hs_code":"1"}')]])
    else:                                                         # model hallucinates a tool -> 502 after retries
        m = ScriptedModel([[tool_call("ghost", "{}")]])
    try:
        res = await run_with_retry(Agent(name="A", instructions="x", model=m, tools=[customs_api]), q.question)
    except ModelBehaviorError as e:
        raise HTTPException(502, f"model error: {e}")
    except MaxTurnsExceeded:
        raise HTTPException(504, "too many turns")
    except AgentsException as e:                                  # base class of all SDK errors
        raise HTTPException(500, f"agent error: {type(e).__name__}")
    return {"answer": str(res.final_output)}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    c = TestClient(app)
    for mode in ("timeout", "loop", "ghost"):
        r = c.post("/ask", json={"question": "x", "mode": mode}); print(mode, r.status_code, r.json())
```

Important: the retry in the sample re-runs the whole agent. Real tools with side effects (payments) must be idempotent or the retry will repeat them. The `ghost` mode retried 3 times against the same scripted model; in production a retry only helps if the failure is random.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Tool error to model | ToolNode can return error as ToolMessage | Agent retries / reports tool errors | Default text observation; `failure_error_function` | Tool error returned as result message |
| Loop limit | `recursion_limit` -> GraphRecursionError | `max_iter` on agent | `max_turns` -> `MaxTurnsExceeded` | Termination conditions / `max_turns` |
| Graceful limit handler | Catch the error | Max iter fallback answer | `error_handlers={"max_turns": fn}` | Termination message |
| Tool timeout | Your code / node timeout | Your code | `@function_tool(timeout=...)` | Your code / cancellation token |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Assuming a raising tool crashes the run.
✅ Correct: By default the SDK hides it from your code and tells the model; add logging/hook checks or set `failure_error_function=None` for must-not-hide tools.

❌ Mistake 2: No `max_turns` and no handler.
✅ Correct: Set `max_turns` per endpoint and return a safe fallback via `error_handlers` or map `MaxTurnsExceeded` to 504.

❌ Mistake 3: Retrying the whole run for non-idempotent actions.
✅ Correct: Make side-effect tools idempotent (idempotency key) or retry only the LLM step, not the tool.

❌ Mistake 4: Catching bare `Exception` first.
✅ Correct: Catch specific SDK errors first, then `AgentsException`, and let programming bugs surface.

---

## 🧠 Tricky Interview Question
A payment tool timed out with `error_as_result`. The model answered "Payment failed, please retry" and the user retried, but the customer was charged twice. What went wrong?

**Answer:** A timeout is not a failure of the remote action - the charge may have completed after your timeout fired. Converting the timeout to a friendly text hid an unknown state, and a retry created a second charge. Fixes: idempotency keys on the payment API, a status-check tool ("did charge X succeed?") the agent must call before retrying, `needs_approval` for payment tools, and a timeout policy that returns "unknown, verifying" not "failed". For write tools prefer `timeout_behavior` that raises so your code decides, plus reconciliation.

---

## ⚫ Interview Questions + Answers

**Q1:** What happens by default when a function tool raises?

**A1:** The SDK sends a generic error message to the model as the tool output and the run continues.

**Q2:** How do you get the exception in your own code?

**A2:** Set `failure_error_function=None` on the tool; the error is raised (wrapped as `UserError` in our run).

**Q3:** How do you stop infinite loops cheaply?

**A3:** `max_turns` plus a `max_turns` error handler returning a safe answer; also log the trace to see why the loop happened.

**Q4:** What is `ModelBehaviorError` and is retrying useful?

**A4:** The model did something invalid (unknown tool, malformed arguments/output). A retry can help since sampling is random, but also fix the prompt/tool names; cap attempts and use backoff.

**Q5:** System design: error handling policy for a payments + support agent.

**A5:** Read tools: timeouts + error-as-result. Write tools: idempotency keys, raise on timeout, reconcile. Turn limits per endpoint. Retries only for read paths. Map errors to 4xx/5xx, alert on rate of ModelBehaviorError and timeouts, track tool error counts in hooks (#63), and keep a human-escalation fallback.

---

## 💰 Cost Impact
Failures cost tokens: each loop turn re-sends the whole history, so a 10-turn runaway pays the growing input ten times. `max_turns` is your cost cap. Retrying a run doubles its cost; retry only on transient failures. Tool timeouts shorten the time you hold connections but also leave the model with an error message turn (one more LLM call). Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Any production endpoint (always set limits and mappings)
- Tools call flaky or slow external services
- You need graceful degradation instead of 500s

❌ Avoid when:
- Retrying non-idempotent writes blindly
- Swallowing all exceptions and returning 200
- Hiding errors from the model when it needs them to adapt

---

## 📊 Visual Diagram
```
 Runner.run(agent, input, max_turns=N)
     |
     +-- tool raises ------> default: error text -> LLM (run continues)
     |                       failure_error_function=None -> raise UserError
     +-- tool slow --------> timeout -> error_as_result -> LLM explains
     +-- unknown tool -----> ModelBehaviorError -> retry/backoff -> 502
     +-- loop too long ----> MaxTurnsExceeded -> handler / 504
     v
  AgentsException (catch-all) -> 500
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MaxTurnsExceeded | Loop limit reached | loop सीमा पूरी |
| ModelBehaviorError | Model produced invalid action | model ने अमान्य क्रिया की |
| failure_error_function | Controls tool error handling | tool error संभालने का नियंत्रण |
| error_as_result | Turn error into tool output | error को tool output बनाना |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |
| Backoff | Growing wait between retries | retries के बीच बढ़ता इंतज़ार |

---

## ⚡ 3-Line Summary
English: Four failures: tool raises, tool hangs, loop never ends, model invents a tool.
Defaults hide tool errors from your code, so set timeouts, max_turns and handlers deliberately.
Retry only idempotent, transient failures and map the rest to clear HTTP codes.

Hindi: चार विफलताएँ: tool raise करे, tool अटके, loop खत्म न हो, model नकली tool गढ़े।
Defaults tool errors को आपके code से छिपाते हैं, इसलिए timeouts, max_turns और handlers सोच-समझकर रखें।
सिर्फ़ idempotent, अस्थायी विफलताओं पर retry करें और बाकी को साफ़ HTTP codes में बदलें।

---

## ➡️ Next Topic
**#67 SDK Testing** - how to test all of this offline with scripted models, pytest and FastAPI dependency overrides.

---
