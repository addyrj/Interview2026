---

# 58. Orchestrator Pattern
# हिंदी में: Orchestrator Pattern (एक planner, कई specialists)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts printed below come from the fake model (10 in / 5 out per call), not from a real LLM.

---

## 🔵 Simple Definition (2-3 lines)
In the orchestrator pattern one planner agent receives the user goal, breaks it into steps, calls specialist agents (as tools) in the right order, and writes the final answer. The specialists never talk to the user.

## 🔵 सरल परिभाषा (Hindi)
Orchestrator pattern में एक planner agent user का goal लेता है, उसे steps में बाँटता है, specialist agents को (tools की तरह) सही क्रम में call करता है और final answer खुद लिखता है। Specialists सीधे user से बात नहीं करते।

---

## 🔴 Problem it Solves
One big agent with every tool and every instruction becomes slow, expensive and unreliable: the prompt is huge, the model picks the wrong tool, and you cannot test parts separately. A hand-written pipeline is rigid when the next step depends on the previous result.

## 🔴 यह क्यों बना? (Hindi)
हर tool और हर instruction वाला एक बड़ा agent धीमा, महँगा और अविश्वसनीय हो जाता है: prompt बहुत बड़ा, model ग़लत tool चुनता है और हिस्सों को अलग से test नहीं कर सकते। हाथ से लिखी pipeline तब कठोर होती है जब अगला step पिछले result पर निर्भर हो।

---

## 🟢 How it Works

```
Step 1 -> Define small specialists (HSClassifier, DutyCalculator)
Step 2 -> Expose each with .as_tool(name, description)
Step 3 -> Orchestrator instructions = the PLAN
          ("1) classify 2) calculate 3) answer. Never skip steps.")
Step 4 -> Turn 1: LLM calls classify   -> result back
Step 5 -> Turn 2: LLM calls calculate  (uses result of step 4)
Step 6 -> Turn 3: LLM writes the final answer (or typed output)
Step 7 -> Guard: max_turns, shared context, audit trail
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> छोटे specialists बनाओ (HSClassifier, DutyCalculator)
Step 2 -> हर एक को .as_tool(name, description) से expose करो
Step 3 -> Orchestrator की instructions = PLAN
          ("1) classify 2) calculate 3) answer. कोई step मत छोड़ो।")
Step 4 -> Turn 1: LLM classify call करता है -> result वापस
Step 5 -> Turn 2: LLM calculate call करता है (step 4 का result इस्तेमाल)
Step 6 -> Turn 3: LLM final answer (या typed output) लिखता है
Step 7 -> सुरक्षा: max_turns, shared context, audit trail
```

**What we observed (offline run):** the orchestrator made exactly 3 model turns, and `result.new_items` held `ToolCallItem, ToolCallOutputItem, ToolCallItem, ToolCallOutputItem, MessageOutputItem` - that item list is your free execution trace.

**Two ways to write the plan:** (a) LLM-driven: plan lives in the instructions, the model chooses order (flexible, can skip steps); (b) code-driven: you call `Runner.run` for each specialist yourself in Python (deterministic, no LLM planning cost). Use (b) when the order never changes.

**Hindi नोट:** Orchestrator = "manager + checklist"। अगर क्रम हमेशा एक जैसा है तो LLM से plan बनवाने की ज़रूरत नहीं - सीधे Python में एक के बाद एक `Runner.run` चलाओ। LLM-orchestrator तब चुनो जब अगला step पिछले नतीजे पर निर्भर हो।

---

## 🟡 Real World Example
**Tariff Agent.** `TariffOrchestrator` for 'Duty on a 1000 USD cotton t-shirt?': calls `classify` (returns HS 6109.10), then `calculate` with the HS code and value, then replies with a typed `TariffResult` (hs_code, duty_usd). A shared context object records every step for the compliance audit.

**Research Agent:** orchestrator calls `searcher`, `summariser`, `fact_checker` in turn.

## 🟡 Real Example Hindi mein
**Tariff Agent.** 'Duty on a 1000 USD cotton t-shirt?' के लिए `TariffOrchestrator` पहले `classify` (HS 6109.10), फिर HS code और value के साथ `calculate` call करता है और अंत में typed `TariffResult` (hs_code, duty_usd) लौटाता है। Shared context हर step को compliance audit के लिए दर्ज करता है।

**Research Agent:** orchestrator बारी-बारी `searcher`, `summariser`, `fact_checker` को call करता है।

---

## 💻 Code Example — Basic
Runs offline. The orchestrator has no tools of its own - only two specialist agents exposed as tools.

```python
# Basic: orchestrator pattern - one planner agent coordinates two specialists exposed as tools.
# verified against openai-agents 0.24.0 (offline, scripted model)
import asyncio                                                    # run the async Runner
from agents import Agent, Runner, set_tracing_disabled            # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline scripted model

set_tracing_disabled(True)                                        # tracing needs an API key; disable offline

classifier = Agent(name="HSClassifier", instructions="Return the HS code.",
                   model=ScriptedModel([[text("6109.10")]]))      # specialist 1: product -> HS code
calculator = Agent(name="DutyCalculator", instructions="Compute duty.",
                   model=ScriptedModel([[text("Duty = 20% of 1000 = 200")]]))  # specialist 2: HS code -> amount

# Orchestrator script: call classifier, then calculator, then write the final answer.
orch_model = ScriptedModel([
    [tool_call("classify", '{"input":"cotton t-shirt"}')],        # step 1
    [tool_call("calculate", '{"input":"6109.10 value 1000"}')],   # step 2 (decided after seeing step 1)
    [text("Shirt = 6109.10, duty 200 USD.")],                     # step 3: final answer
])
orchestrator = Agent(
    name="TariffOrchestrator",
    instructions="1) classify 2) calculate 3) answer. Never skip steps.",
    model=orch_model,
    tools=[classifier.as_tool("classify", "Product -> HS code"),   # each specialist is a tool
           calculator.as_tool("calculate", "HS code + value -> duty")],
)

result = asyncio.run(Runner.run(orchestrator, "Duty on a 1000 USD cotton t-shirt?"))
print(result.final_output)                                        # Shirt = 6109.10, duty 200 USD.
print([type(i).__name__ for i in result.new_items])               # trail: call, output, call, output, message
print(orch_model.calls)                                           # 3 model turns by the orchestrator
```

Expected output: `Shirt = 6109.10, duty 200 USD.`, the 5 item names above, and `3` (model turns). Note: `from fake import ...` is the helper listed in note #57.

## 💻 Code Example — Advanced
FastAPI service: orchestrator with function tools, a typed shared context (`TariffCtx`, not sent to the LLM) for the audit trail, structured `output_type`, error mapping. Output: `{'result': {'hs_code': '6109.10', 'duty_usd': 200.0}, 'steps': ['classify:cotton shirt', 'duty:6109.10'], 'total_tokens': 45}`.

```python
# Advanced: orchestrator with shared typed context, structured final output, FastAPI + audit trail.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
from dataclasses import dataclass, field                          # mutable request context
from typing import Any                                            # type hints
from fastapi import FastAPI, HTTPException                        # web layer
from pydantic import BaseModel                                    # schemas
from agents import (Agent, RunContextWrapper, Runner, function_tool, set_tracing_disabled,
                    MaxTurnsExceeded, ModelBehaviorError)         # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline model

set_tracing_disabled(True)

@dataclass
class TariffCtx:                                                  # shared state; NOT sent to the LLM
    user_id: str
    steps: list[str] = field(default_factory=list)                # audit trail filled by tools

class TariffResult(BaseModel):                                    # structured output of the orchestrator
    hs_code: str
    duty_usd: float

@function_tool
async def classify(ctx: RunContextWrapper[TariffCtx], product: str) -> str:   # async tool, receives context
    """Map a product description to an HS code."""
    ctx.context.steps.append(f"classify:{product}")               # audit
    return "6109.10"

@function_tool
async def duty(ctx: RunContextWrapper[TariffCtx], hs_code: str, value_usd: float) -> float:
    """Compute duty in USD for the HS code and goods value."""
    ctx.context.steps.append(f"duty:{hs_code}")                   # audit
    return round(value_usd * 0.20, 2)                             # 20% demo rate

def build(model: Any) -> Agent[TariffCtx]:                        # factory: tests inject a fake model
    return Agent[TariffCtx](name="Orchestrator", instructions="classify then duty; return TariffResult.",
                            model=model, tools=[classify, duty], output_type=TariffResult)

class Req(BaseModel):
    product: str
    value_usd: float

class Resp(BaseModel):
    result: TariffResult
    steps: list[str]
    total_tokens: int

app = FastAPI()

@app.post("/tariff", response_model=Resp)
async def tariff(req: Req) -> Resp:
    model = ScriptedModel([                                       # offline script; production: model="gpt-..." string
        [tool_call("classify", '{"product":"%s"}' % req.product)],
        [tool_call("duty", '{"hs_code":"6109.10","value_usd":%s}' % req.value_usd)],
        [text('{"hs_code":"6109.10","duty_usd":%s}' % round(req.value_usd * 0.2, 2))],
    ])
    ctx = TariffCtx(user_id="u1")                                 # one context per request
    try:
        res = await Runner.run(build(model), f"{req.product} worth {req.value_usd}", context=ctx, max_turns=6)
    except MaxTurnsExceeded:
        raise HTTPException(504, "too many agent turns")
    except ModelBehaviorError as e:                               # also raised for output that fails the schema
        raise HTTPException(502, f"bad model output: {e}")
    return Resp(result=res.final_output_as(TariffResult), steps=ctx.steps,
                total_tokens=res.context_wrapper.usage.total_tokens)

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/tariff", json={"product": "cotton shirt", "value_usd": 1000}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Orchestrator | Supervisor node / explicit graph edges | Hierarchical process with manager agent | Orchestrator agent + `as_tool` specialists | `SelectorGroupChat` / orchestrator agent in a team |
| Who decides next step | Your routing code or an LLM node | Manager LLM | The orchestrator LLM (or your Python) | Selector LLM / termination rules |
| Deterministic mode | Yes (plain edges) | Sequential process | Yes - call Runner.run in code | Round-robin team |
| State between steps | Typed graph state + checkpointer | Task outputs/context | Run context + result items | Team message thread |
| Boilerplate | Most | Medium | Least | Medium |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: Putting the plan only in the user prompt.
✅ Correct: Put the plan in the orchestrator's `instructions` so it is applied on every run.

❌ Mistake: Letting specialists see and answer the user directly.
✅ Correct: Use as_tool so only the orchestrator writes the final answer.

❌ Mistake: No `max_turns`, so a confused planner loops forever.
✅ Correct: Always pass `max_turns` and map `MaxTurnsExceeded` to an HTTP 504.

❌ Mistake: Trusting the LLM to compute money.
✅ Correct: Do arithmetic in a function tool (as `duty` does), not in the model.

---

## 🧠 Tricky Interview Question
Your orchestrator sometimes skips the `classify` step and guesses an HS code. How do you make the plan reliable?

**Answer:** LLM planners follow instructions probabilistically. Options, strongest first: (1) make the order code-driven - call classify, then calculate in Python (deterministic); (2) keep it LLM-driven but make `duty` require the HS code from `classify` (validate in the tool, raise or return an error string if the code is not in an allow-list the classify tool produced via context); (3) use `tool_choice` / `tool_use_behavior` to force the first tool (see #61); (4) add an output guardrail that rejects answers whose steps list lacks `classify`; (5) evaluate with scripted tests asserting the call order. Pick (1) when the order is fixed; the LLM adds nothing there.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the orchestrator pattern?

**A1:** One planner agent coordinates specialists exposed as tools and writes the final answer.

**Q2:** Orchestrator vs handoff chain?

**A2:** Orchestrator keeps control and merges results; handoff chain passes control along and the last agent answers.

**Q3:** How do you share state between steps without sending it to the LLM?

**A3:** Use the run `context` (a dataclass); tools read/write it through `RunContextWrapper`. It is not in the prompt.

**Q4:** When is a code-driven orchestrator better?

**A4:** When the order is fixed: it is cheaper (no planning tokens), deterministic and easier to test.

**Q5:** Design: orchestrator for 8 specialists with SLA 5 s.

**A5:** Run independent specialists in parallel (#59), small fast models for specialists, per-tool timeouts, `max_turns`, cache classify results, fallback answer on timeout, and trace every step. Keep the orchestrator prompt to routing rules only.

---

## 💰 Cost Impact
Cost = orchestrator turns + every specialist run. In the offline sample: 3 orchestrator turns plus 2 specialist runs. Real runs resend the growing history each orchestrator turn, so input tokens grow per turn. Tips: short specialist outputs, cheaper model for specialists, code-driven order where possible, `max_turns`. Figures are formulas only; prices are approximate - verify on the current price list.

---

## 🔷 When to Use
✅ Use when:
- Steps depend on earlier results
- Different specialists need different tools or models
- You need one voice and one audit trail for the final answer

❌ Avoid when:
- The steps are fixed and independent (use plain Python / parallel runs)
- One tool call solves it
- Strict latency with many sequential LLM turns

---

## 📊 Visual Diagram
```
  User goal
     |
     v
 +--------------------+
 | Orchestrator (LLM) |  plan in instructions
 +--------------------+
   | 1 classify     ^ result
   v                |
 +--------------+   |
 | HSClassifier |---+
 +--------------+
   | 2 calculate    ^ result
   v                |
 +----------------+ |
 | DutyCalculator |-+
 +----------------+
   |
   v 3 final answer (typed) -> User
 shared context: steps = [classify, duty]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Orchestrator | Planner that coordinates specialists | specialists का coordinator |
| Specialist | Small focused agent | छोटा focused agent |
| Plan | Ordered steps in instructions | instructions में क्रमबद्ध steps |
| Run context | Typed shared object not sent to LLM | LLM को न भेजा जाने वाला shared object |
| new_items | Items produced by the run | run में बने items |
| max_turns | Loop limit | loop की सीमा |

---

## ⚡ 3-Line Summary
English: An orchestrator agent plans and calls specialist agents as tools, then writes one final answer.
Use a shared context for audit and a typed output for reliability.
If the order never changes, drive it from Python instead of the LLM.

Hindi: Orchestrator agent plan बनाकर specialist agents को tools की तरह call करता है और एक final answer लिखता है।
Audit के लिए shared context और भरोसे के लिए typed output इस्तेमाल करें।
अगर क्रम कभी नहीं बदलता तो LLM की जगह Python से चलाएँ।

---

## ➡️ Next Topic
**#59 Parallelism in SDK** - orchestrators are slow when specialists run one after another; next we run independent agents and tools concurrently.

---
