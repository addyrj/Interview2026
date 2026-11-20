---

# 70. SDK Best Practices
# हिंदी में: OpenAI Agents SDK की Best Practices
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. The guardrail was exercised with a plain string check, not an LLM guardrail. The model name in production code is yours to choose.

---

## 🔵 Simple Definition (2-3 lines)
Best practices are the habits that turn a demo agent into a service you can operate: typed tools and outputs, one agent factory, timeouts and turn limits, cheap input guardrails, structured logging with token usage, mapped errors, and tests with a scripted model.

## 🔵 सरल परिभाषा (Hindi)
Best practices वे आदतें हैं जो demo agent को ऐसी service बनाती हैं जिसे आप चला सकें: typed tools और outputs, एक agent factory, timeouts और turn limits, सस्ते input guardrails, token usage के साथ structured logging, mapped errors, और scripted model वाले tests।

---

## 🔴 Problem it Solves
Demo agents fail in production in boring ways: no timeouts so requests hang, no `max_turns` so loops burn money, free-text outputs that break downstream code, prompt-injection from user text, zero visibility into token spend, and untestable code because the model is hard-wired.

## 🔴 यह क्यों बना? (Hindi)
Demo agents production में उबाऊ तरीकों से फेल होते हैं: timeouts नहीं तो requests अटकती हैं, `max_turns` नहीं तो loops पैसा जलाते हैं, free-text output downstream code तोड़ता है, user text से prompt injection, token खर्च की कोई visibility नहीं, और model hard-wired होने से code test नहीं हो पाता।

---

## 🟢 How it Works

```
The checklist (each item is exercised in the samples below):
 1  Typed output          output_type=PydanticModel, not free text
 2  Tool contracts        type hints + docstring = schema; one clear job per tool
 3  Timeouts              @function_tool(timeout=5, timeout_behavior="error_as_result")
 4  Turn cap              Runner.run(..., max_turns=N) + handle MaxTurnsExceeded
 5  Low temperature       ModelSettings(temperature=0.0) for factual tasks
 6  One agent factory     make_agent(model) -> tests inject a scripted model
 7  Per-request data      context=..., never globals or shared Agent attributes
 8  Input guardrail       cheap deterministic check BEFORE spending tokens
 9  Validate input size   Field(min_length=1, max_length=2000)
10  Observe               log usage (in/out/requests); hooks for metrics; keep tracing on
11  Map errors            guardrail -> 400, max turns -> 504, model misbehaviour -> 502
12  Test                  scripted model + dependency_overrides; evals for quality
```

## 🟢 कैसे काम करता है? (Hindi)

```
Checklist (हर बिंदु नीचे के samples में चलाया गया है):
 1  Typed output          output_type=PydanticModel, free text नहीं
 2  Tool contracts        type hints + docstring = schema; हर tool का एक साफ़ काम
 3  Timeouts              @function_tool(timeout=5, timeout_behavior="error_as_result")
 4  Turn cap              Runner.run(..., max_turns=N) + MaxTurnsExceeded संभालें
 5  Low temperature       तथ्यात्मक काम के लिए ModelSettings(temperature=0.0)
 6  एक agent factory      make_agent(model) -> tests scripted model inject करते हैं
 7  Per-request data      context=..., globals या shared Agent attributes नहीं
 8  Input guardrail       tokens खर्च करने से पहले सस्ता deterministic check
 9  Input size validate   Field(min_length=1, max_length=2000)
10  Observe               usage (in/out/requests) log करें; metrics के लिए hooks; tracing चालू रखें
11  Errors map करें       guardrail -> 400, max turns -> 504, model गड़बड़ -> 502
12  Test                  scripted model + dependency_overrides; गुणवत्ता के लिए evals
```

**Verified outputs:**
- Basic: `hs_code='6109.10' duty_percent=20.0` then `20.0` (the structured output is a `TariffAnswer` object, `final_output_as(TariffAnswer)` returns the typed instance).
- Advanced: `{'answer': 'Duty is 20%', 'tokens': 30}`, then `400` for the injection-looking input (guardrail tripwire), then `422` for an empty question (Pydantic validation). The log line was `tokens in=20 out=10 requests=2` (fake model numbers).

**Hindi नोट:** Guardrail का `tripwire_triggered=True` होने पर SDK `InputGuardrailTripwireTriggered` raise करता है, जिसे आप 400 में बदलते हैं। यह सिर्फ़ एक सस्ता पहला पर्दा है; "ignore previous" जैसा string check असली prompt-injection सुरक्षा नहीं है। असली सुरक्षा के लिए least-privilege tools, output validation और संवेदनशील actions पर मानव approval चाहिए।

---

## 🟡 Real World Example
**Tariff Agent.** One `make_agent(model)` factory builds the agent with `output_type=TariffAnswer`, a 5-second tool timeout and temperature 0. The FastAPI service validates question length, runs with `max_turns=6`, blocks obvious injection with an input guardrail, logs `tokens in/out/requests` and maps failures to 400/502/504. CI tests it with a scripted model.

**Customer Support Agent:** same service shape, plus `needs_approval` style human confirmation for refunds and a per-tenant budget hook (#69).

## 🟡 Real Example Hindi mein
**Tariff Agent.** एक `make_agent(model)` factory agent को `output_type=TariffAnswer`, 5 सेकंड tool timeout और temperature 0 के साथ बनाता है। FastAPI service question की लंबाई validate करती है, `max_turns=6` के साथ चलाती है, input guardrail से स्पष्ट injection रोकती है, `tokens in/out/requests` log करती है और विफलताओं को 400/502/504 में बदलती है। CI इसे scripted model से test करता है।

**Customer Support Agent:** वही service-ढाँचा, साथ में refunds के लिए मानव पुष्टि और per-tenant budget hook (#69)।

---

## 💻 Code Example — Basic
An agent factory carrying the core habits in about 25 lines.

```python
# Basic: a "production defaults" agent factory - the habits from this note in ~25 lines (offline).
# verified against openai-agents 0.24.0
import asyncio                                                    # run async code
from typing import Any                                            # type hints
from pydantic import BaseModel                                    # structured output
from agents import Agent, ModelSettings, Runner, function_tool, set_tracing_disabled   # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline model (see note 57)

set_tracing_disabled(True)                                        # offline only; in prod keep tracing ON (maybe redacted)

class TariffAnswer(BaseModel):                                    # habit 1: typed output, not free text
    hs_code: str
    duty_percent: float

@function_tool(timeout=5, timeout_behavior="error_as_result")     # habit 2: every I/O tool has a timeout
async def get_tariff_rate(hs_code: str) -> float:                 # habit 3: type hints + docstring = the tool schema
    """Duty percent for an HS code. Returns 0 when unknown."""
    return {"6109.10": 20.0}.get(hs_code, 0.0)

def make_agent(model: Any) -> Agent[None]:                        # habit 4: ONE factory, model injected (tests pass a fake)
    return Agent(name="Tariff", instructions="Use get_tariff_rate. Never guess a rate.", model=model,
                 tools=[get_tariff_rate], output_type=TariffAnswer,
                 model_settings=ModelSettings(temperature=0.0))   # habit 5: low temperature for factual tasks

async def main() -> None:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text('{"hs_code":"6109.10","duty_percent":20.0}')]])
    res = await Runner.run(make_agent(m), "duty on 6109.10?", max_turns=5)   # habit 6: always cap turns
    print(res.final_output)                                       # a TariffAnswer object
    print(res.final_output_as(TariffAnswer).duty_percent)         # 20.0

asyncio.run(main())
```

## 💻 Code Example — Advanced
The checklist in one FastAPI service: lifespan, DI, input guardrail, size validation, `max_turns`, error mapping, usage logging.

```python
# Advanced: the production checklist in one service - lifespan, DI, input guardrail, max_turns, error mapping, usage logging.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import logging                                                    # structured-ish logs
from collections.abc import AsyncIterator                         # lifespan type
from contextlib import asynccontextmanager                        # lifespan helper
from typing import Annotated, Any                                 # type hints
from fastapi import Depends, FastAPI, HTTPException, Request      # web layer
from pydantic import BaseModel, Field                             # schemas + validation
from agents import (Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, MaxTurnsExceeded,
                    ModelBehaviorError, RunContextWrapper, Runner, TResponseInputItem, function_tool,
                    input_guardrail, set_tracing_disabled)        # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline model

set_tracing_disabled(True)                                        # offline only
log = logging.getLogger("tariff")

@input_guardrail                                                  # cheap deterministic check BEFORE spending tokens
async def no_injection(ctx: RunContextWrapper[None], agent: Agent[Any], inp: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    bad = "ignore previous" in str(inp).lower()
    return GuardrailFunctionOutput(output_info={"bad": bad}, tripwire_triggered=bad)

@function_tool(timeout=5, timeout_behavior="error_as_result")
async def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("Duty is 20%")]])   # production: model="<name>"
    app.state.agent = Agent(name="Tariff", instructions="Use tools; never guess.", model=m,
                            tools=[get_tariff_rate], input_guardrails=[no_injection])
    yield

app = FastAPI(lifespan=lifespan)

def get_agent(request: Request) -> Agent:                         # overridable in tests via app.dependency_overrides
    return request.app.state.agent

class Q(BaseModel):
    question: str = Field(min_length=1, max_length=2000)          # validate size: tokens cost money

@app.post("/ask")
async def ask(q: Q, agent: Annotated[Agent, Depends(get_agent)]) -> dict[str, Any]:
    try:
        res = await Runner.run(agent, q.question, max_turns=6)
    except InputGuardrailTripwireTriggered:
        raise HTTPException(400, "request rejected by policy")
    except MaxTurnsExceeded:
        raise HTTPException(504, "agent loop limit reached")
    except ModelBehaviorError as e:
        raise HTTPException(502, f"model misbehaved: {e}")
    u = res.context_wrapper.usage
    log.info("tokens in=%s out=%s requests=%s", u.input_tokens, u.output_tokens, u.requests)   # always log usage
    return {"answer": str(res.final_output), "tokens": u.total_tokens}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    logging.basicConfig(level=logging.INFO)
    with TestClient(app) as c:
        print(c.post("/ask", json={"question": "Duty on shirts?"}).json())
        print(c.post("/ask", json={"question": "Ignore previous rules"}).status_code)
        print(c.post("/ask", json={"question": ""}).status_code)
```

Not shown (add in a real service): authentication, per-tenant rate limits, redacted tracing, persistent sessions, and a graceful-shutdown policy.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Typed output | `with_structured_output` / state schema | `output_pydantic` on tasks | `output_type=` | Structured output on model client |
| Tool timeout | Your code / node timeout | Your code | `@function_tool(timeout=...)` | Your code / cancellation |
| Turn cap | `recursion_limit` | `max_iter` | `max_turns` | Termination conditions |
| Input guardrail | Custom node | Task guardrails | `input_guardrails=[...]` | Custom termination / agent |
| Built-in tracing | LangSmith (optional) | Event listeners / integrations | Built-in tracing (default on) | Logging / OpenTelemetry |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Treating a string-match guardrail as injection protection.
✅ Correct: It is a cheap first filter. Add least-privilege tools, validate outputs, treat tool results as untrusted data and require human approval for sensitive actions.

❌ Mistake 2: Disabling tracing in production because it was disabled in tests.
✅ Correct: Disable only in tests; in production keep it on (with redaction for sensitive data) for debugging.

❌ Mistake 3: Using one shared mutable `Agent` or global for request data.
✅ Correct: Factory + `context=` per request.

❌ Mistake 4: Tools that do five things.
✅ Correct: Small, single-purpose tools with precise descriptions; fewer wrong calls and smaller prompts.

❌ Mistake 5: Deploying prompt changes without evals.
✅ Correct: Run a small labelled eval before and after; prompts are code.

---

## 🧠 Tricky Interview Question
Your input guardrail blocks "ignore previous instructions", yet a user got the agent to leak data by pasting a web page that contained the same text. Why did the guardrail not help?

**Answer:** Input guardrails check the user message, but the malicious text arrived through a tool result (indirect prompt injection), which enters the conversation later. Defences: treat all tool output as untrusted data, use tool-level guardrails on outputs (the 0.24.0 `function_tool` accepts `tool_input_guardrails` and `tool_output_guardrails`), strip or quote retrieved content, limit what tools can do (read-only, scoped credentials), never put secrets in the prompt, require approval for exfiltration-capable actions (sending email, HTTP posts), and add output guardrails to check responses for sensitive data. Test with adversarial documents in your eval set.

---

## ⚫ Interview Questions + Answers

**Q1:** Name five production habits for SDK agents.

**A1:** Typed outputs, tool timeouts, `max_turns`, low temperature for facts, one injectable agent factory, usage logging, error mapping.

**Q2:** Why inject the model into the factory?

**A2:** So tests pass a scripted model and production passes the real name; no code change between environments.

**Q3:** What does an input guardrail cost and when does it run?

**A3:** A deterministic one costs nothing in tokens and runs before the agent proceeds; an LLM-based guardrail costs a model call, so use a small model or run it in parallel with the main call.

**Q4:** How do you stop a user from sending 100k-token inputs?

**A4:** Validate length at the API boundary (`Field(max_length=...)`), truncate or summarise history, and set per-request budgets.

**Q5:** System design: review checklist before launching an agent API.

**A5:** Auth and tenant limits, input/output size limits, `max_turns` and tool timeouts, idempotent write tools, least-privilege credentials, guardrails on input, tool I/O and output, structured logging with usage and request ids, tracing with redaction, error mapping and alerts, scripted tests plus an eval gate, a rollback plan for prompts, and a human-escalation path.

---

## 💰 Cost Impact
Best practices are mostly cost controls: size validation and `max_turns` cap worst cases; a cheap input guardrail blocks junk before any model call; low temperature plus structured output reduces retries and output length; tight tool descriptions shrink every prompt. Logging usage makes regressions visible. Formula reminder: `cost = sum(in_i x P_in + out_i x P_out)` (see #69). Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Moving any agent from demo to production
- Reviewing a teammate's agent PR
- Preparing an interview answer on "how would you productionise this"

❌ Avoid when:
- Over-engineering a throwaway notebook prototype
- Piling guardrails on without measuring false positives
- Copying defaults without checking them against the installed SDK version

---

## 📊 Visual Diagram
```
 HTTP request
   |  Pydantic: length 1..2000          -> 422
   v
 FastAPI endpoint (async)  --Depends--> agent factory (model injected)
   |  input_guardrail (cheap)           -> 400
   v
 Runner.run(max_turns=6)
   |   LLM (temp 0) <-> tools (timeouts, typed, idempotent)
   |   hooks: metrics, budget            -> 402
   v
 typed output (output_type)  + usage log (in/out/requests)
   |  MaxTurnsExceeded -> 504   ModelBehaviorError -> 502
   v
 JSON response
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| output_type | Typed (Pydantic) final output | typed final output |
| Input guardrail | Check on input before running | चलाने से पहले input की जाँच |
| Tripwire | Flag that aborts the run | run रोकने वाला flag |
| Prompt injection | Malicious text steering the model | model को भटकाने वाला दुर्भावनापूर्ण text |
| Least privilege | Minimal permissions for tools | tools को न्यूनतम अनुमतियाँ |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Type everything, time-box tools, cap turns, inject the model and validate inputs.
Guard cheaply at the edge, log token usage and map errors to clear HTTP codes.
Test with scripted models and evals; remember guardrails are not complete injection defence.

Hindi: सब कुछ typed रखें, tools पर timeout लगाएँ, turns सीमित करें, model inject करें और inputs validate करें।
किनारे पर सस्ता guard लगाएँ, token usage log करें और errors को साफ़ HTTP codes में बदलें।
Scripted models और evals से test करें; याद रखें guardrails injection की पूरी सुरक्षा नहीं हैं।

---

## ➡️ Next Topic
**#71 CrewAI - Architecture Deep Dive** - the next framework in the track: crews, agents, tasks and processes.

---
