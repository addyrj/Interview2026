---

# 53. Tool Choice Strategy
# हिंदी में: Tool Choice Strategy (कौन सा tool, कब)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model. I recorded the `tool_choice` the model was actually sent on each turn: `['required', None]` for the default reset behaviour and `['required', 'required']` with `reset_tool_choice=False`.

---

## 🔵 Simple Definition (2-3 lines)
Tool choice strategy is how you control whether and which tool the model calls. Three levers: `ModelSettings(tool_choice=...)` (`'auto'`, `'required'`, `'none'`, or a specific tool name), `Agent.reset_tool_choice` (what happens after a tool ran), and `tool_use_behavior` (what happens with the tool output).

## 🔵 सरल परिभाषा (Hindi)
Tool choice strategy यह नियंत्रित करती है कि model tool call करे या नहीं और कौन सा करे। तीन lever: `ModelSettings(tool_choice=...)` (`'auto'`, `'required'`, `'none'` या किसी tool का नाम), `Agent.reset_tool_choice` (tool चलने के बाद क्या हो), और `tool_use_behavior` (tool output का क्या हो)।

---

## 🔴 Problem it Solves
By default the model decides alone, so it may answer from memory instead of calling your database tool, or call the wrong tool, or loop. Pipelines that must always look something up, or must never use tools in a step, need explicit control. But forcing a tool naively causes infinite loops because the model is forced again after every result.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से model खुद तय करता है, इसलिए वह database tool बुलाने के बजाय याददाश्त से जवाब दे सकता है, गलत tool बुला सकता है, या loop में फँस सकता है। जिन pipelines को हमेशा lookup करना है, या किसी step में tools कभी नहीं चाहिए, उन्हें स्पष्ट नियंत्रण चाहिए। पर tool को बिना सोचे force करने से infinite loop बनता है क्योंकि हर result के बाद model फिर से force होता है।

---

## 🟢 How it Works

```
Step 1 -> tool_choice="auto"      model decides (default)
          tool_choice="required"  model MUST call some tool
          tool_choice="none"      model MUST NOT call tools
          tool_choice="hs_duty"   model MUST call that tool
Step 2 -> Turn 1 sent with your tool_choice
Step 3 -> Tool runs, result appended
Step 4 -> reset_tool_choice=True (default): next turn is sent
          WITHOUT the forced choice (we saw None) -> agent can stop
          reset_tool_choice=False: forced again -> loop risk
Step 5 -> tool_use_behavior decides if the tool output is final
          ("stop_on_first_tool", StopAtTools, custom fn) or the
          LLM runs again (default)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> tool_choice="auto"      model खुद तय करे (default)
          tool_choice="required"  model को कोई tool बुलाना ही होगा
          tool_choice="none"      model tools नहीं बुला सकता
          tool_choice="hs_duty"   model को वही tool बुलाना होगा
Step 2 -> Turn 1 आपके tool_choice के साथ जाता है
Step 3 -> Tool चलता है, result जुड़ता है
Step 4 -> reset_tool_choice=True (default): अगला turn forced choice
          के बिना जाता है (हमने None देखा) -> agent रुक सकता है
          reset_tool_choice=False: फिर forced -> loop का खतरा
Step 5 -> tool_use_behavior तय करता है कि tool output ही final है
          ("stop_on_first_tool", StopAtTools, custom fn) या
          LLM फिर चले (default)
```

**Verified in 0.24.0:** `ToolChoice = Literal['auto','required','none'] | str | MCPToolChoice | None`; `Agent(reset_tool_choice=True)` is the default; `tool_use_behavior` accepts `'run_llm_again'`, `'stop_on_first_tool'`, `StopAtTools(stop_at_tool_names=[...])` or a function.

**Observed:** with `tool_choice='required'` the recorded calls were `['required', None]`: the SDK reset the choice after the tool ran. With `reset_tool_choice=False` it was `['required', 'required']`; with a real model that would force another tool call every turn until `max_turns`.

**Names:** hosted tools can be forced by name too (`'file_search'`, `'web_search'`, as the SDK maps them). A function tool is forced by its function name.

**Provider note:** how strictly a provider honours `tool_choice` differs (some ignore `required` for some models). Test on your model; I could not test real providers.

**Hindi नोट:** याद रखने की बात: `tool_choice` = "model क्या बुला सकता है", `tool_use_behavior` = "tool के बाद क्या होगा"। दोनों अलग lever हैं।

---

## 🟡 Real World Example
**Tariff Agent.** A compliance pipeline must always read the official duty table: `tool_choice='required'` plus `tool_use_behavior='stop_on_first_tool'` so the DB value is the answer with one LLM call. A later 'explain in plain English' step uses `tool_choice='none'`. An 'escalate' tool uses `StopAtTools` so the run stops when a human handoff is raised.

**Customer Support Agent:** force a `lookup_order` call on the first turn only.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Compliance pipeline को हमेशा official duty table पढ़नी है: `tool_choice='required'` और `tool_use_behavior='stop_on_first_tool'`, ताकि DB की value ही जवाब बने और सिर्फ़ एक LLM call लगे। बाद का 'सरल भाषा में समझाओ' step `tool_choice='none'` इस्तेमाल करता है। 'escalate' tool `StopAtTools` से run रोकता है जब human handoff उठता है।

**Customer Support Agent:** सिर्फ़ पहले turn में `lookup_order` को force करो।

---

## 💻 Code Example — Basic
Runs offline. Prints the `tool_choice` actually sent to the model on each turn for three configurations; no invented numbers.

```python
# Basic: tool_choice values and what the model is sent on each turn (offline)
import asyncio                                           # async runner
from agents import Agent, Runner, ModelSettings, function_tool  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

async def run_with(choice, reset: bool = True) -> list:
    model = ScriptedModel([[function_call("hs_duty", {"code": "6109.10"}, call_id="c")],  # turn 1: tool call
                           [assistant_message("20%")]])                                  # turn 2: final text
    agent = Agent(name="Tariff Agent", instructions="x", model=model, tools=[hs_duty],
                  model_settings=ModelSettings(tool_choice=choice),  # "auto" | "required" | "none" | "<tool name>" | None
                  reset_tool_choice=reset)               # after a tool call, reset to auto-ish so the agent can stop
    await Runner.run(agent, "q")
    return [c.model_settings.tool_choice for c in model.calls]   # what each model call was sent

async def main() -> None:
    print("tool_choice='required'          ->", await run_with("required"))
    print("tool_choice='hs_duty'           ->", await run_with("hs_duty"))
    print("reset_tool_choice=False         ->", await run_with("required", reset=False))  # would loop forever with a real model!

asyncio.run(main())
```

## 💻 Code Example — Advanced
Three modes behind FastAPI: forced lookup with stop-on-first-tool, tools forbidden, and auto with `StopAtTools`. `max_turns` guards against loops. Offline.

```python
# Advanced: choose tool_choice per request, stop after the tool, avoid infinite loops (offline, FastAPI)
from fastapi import FastAPI, HTTPException               # web
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schema
from agents import (Agent, Runner, ModelSettings, function_tool,
                    MaxTurnsExceeded, StopAtTools)       # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

@function_tool
def escalate(reason: str) -> str:
    """Hand the case to a human officer."""
    return f"ticket opened: {reason}"

def build(model, mode: str) -> Agent:
    if mode == "must_lookup":                            # structured pipeline: always call a tool, then stop
        return Agent(name="Tariff Agent", instructions="x", model=model, tools=[hs_duty],
                     model_settings=ModelSettings(tool_choice="required"),
                     tool_use_behavior="stop_on_first_tool")      # tool output IS the final output
    if mode == "no_tools":                               # e.g. a summarisation turn: forbid tools
        return Agent(name="Tariff Agent", instructions="x", model=model, tools=[hs_duty],
                     model_settings=ModelSettings(tool_choice="none"))
    return Agent(name="Tariff Agent", instructions="x", model=model, tools=[hs_duty, escalate],
                 model_settings=ModelSettings(tool_choice="auto"),
                 tool_use_behavior=StopAtTools(stop_at_tool_names=["escalate"]))  # stop when escalate is called

app = FastAPI()

class Ask(BaseModel):
    question: str
    mode: str = "auto"

@app.post("/ask")
async def ask(b: Ask) -> dict:
    if b.mode == "must_lookup":
        steps = [[function_call("hs_duty", {"code": "6109.10"}, call_id="1")]]
    elif b.mode == "no_tools":
        steps = [[assistant_message("Plain answer.")]]
    else:
        steps = [[function_call("escalate", {"reason": "unclear code"}, call_id="1")]]
    model = ScriptedModel(steps)
    try:
        res = await Runner.run(build(model, b.mode), b.question, max_turns=3)   # max_turns guards a forced-tool loop
    except MaxTurnsExceeded as exc:
        raise HTTPException(status_code=504, detail="agent looped") from exc
    return {"output": res.final_output, "choice_sent": model.calls[0].model_settings.tool_choice, "llm_calls": len(model.calls)}

if __name__ == "__main__":
    c = TestClient(app)
    for m in ("must_lookup", "no_tools", "auto"):
        print(m, c.post("/ask", json={"question": "q", "mode": m}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Force a tool | Bind model with `tool_choice` | Task `tools` list; agent decides | `ModelSettings(tool_choice=name)` | Model client `tool_choice` param |
| Forbid tools for a step | Bind without tools | Agent without tools | `tool_choice='none'` | Agent with no tools |
| Stop after a tool | Conditional edge to END | Task output from tool | `tool_use_behavior` (`stop_on_first_tool`, `StopAtTools`) | `reflect_on_tool_use=False` |
| Loop protection | `recursion_limit` | `max_iter` | `max_turns` + `reset_tool_choice` | `max_tool_iterations` |
| Per-turn control | Edges/nodes | Task order | Dynamic `model_settings`, hooks | Custom agent logic |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Setting `tool_choice='required'` and `reset_tool_choice=False`.
✅ Correct: Keep the reset default or use `stop_on_first_tool`; otherwise the agent loops until `max_turns`.

❌ Mistake 2: Confusing `tool_choice` with `tool_use_behavior`.
✅ Correct: The first controls the model's call; the second controls what happens with the output.

❌ Mistake 3: Forcing a tool by a name that does not match.
✅ Correct: Use the exact function name (or hosted name like `web_search`).

❌ Mistake 4: Relying on the prompt alone to force lookups.
✅ Correct: Use `required`/named choice for hard guarantees; prompts are suggestions.

❌ Mistake 5: Assuming every provider honours `required`.
✅ Correct: Test on your provider/model and add an assertion on the trace.

---

## 🧠 Tricky Interview Question
You set `tool_choice='required'` on an agent with one tool and a user says 'hi'. The run burns 10 turns and ends with MaxTurnsExceeded. Explain and fix.

**Answer:** `required` forces a tool call even when none is sensible. With `reset_tool_choice=False` (or a provider/wrapper that keeps re-sending the forced choice, or `run_llm_again` with a model that keeps calling tools) the model calls the tool every turn and never produces a final message, so the loop hits `max_turns`. Fixes: (1) only force when the request truly needs the tool (classify first or use a router agent); (2) keep `reset_tool_choice=True` so the second turn is sent as auto; (3) use `tool_use_behavior='stop_on_first_tool'` when the tool's output is the answer; (4) give the model a no-op/`final_answer` tool as an explicit exit; (5) keep `max_turns` low and alert on MaxTurnsExceeded; (6) assert on traces in tests. We reproduced the choice sequence offline: `['required', None]` vs `['required', 'required']`.

---

## ⚫ Interview Questions + Answers

**Q1:** What values can `tool_choice` take?

**A1:** `'auto'`, `'required'`, `'none'`, a specific tool name, or an MCP tool choice object; `None` leaves it to the provider default.

**Q2:** What does `reset_tool_choice` do?

**A2:** After a tool call the SDK stops forcing the choice (default True), preventing infinite forced tool loops. We saw the second call sent with `None`.

**Q3:** `stop_on_first_tool` vs `StopAtTools`?

**A3:** First: the first tool output becomes the final output. StopAtTools: stop only when one of the named tools is called.

**Q4:** How do you guarantee a lookup always happens before answering?

**A4:** `tool_choice='required'` (or the tool name) on turn one with the reset default, and optionally `stop_on_first_tool` when the output is the answer.

**Q5:** Design a router + executor using these controls.

**A5:** Router agent with `tool_choice='required'` and tools representing routes (stop at route tool via `StopAtTools`); executor agents per route with `auto`; a final formatter with `tool_choice='none'`; `max_turns` per stage; traces assert the expected tool sequence; evals for misrouting.

---

## 💰 Cost Impact
Forcing and stopping are cost tools. `stop_on_first_tool` saves one full LLM call (the model would otherwise re-read the whole history to rephrase the tool output). `tool_choice='none'` avoids tool-schema work and surprise calls in formatting steps. Forced loops are the expensive failure: each extra turn re-sends the growing history, so keep `max_turns` low. Approximate effect only; measure with `result.context_wrapper.usage` in your own traffic.

---

## 🔷 When to Use
✅ Use when:
- Pipelines that must always call a specific tool
- Steps that must not use tools
- Stopping when a tool output is the answer
- Router patterns with terminal tools

❌ Avoid when:
- Forcing tools for open conversation
- Forcing without reset or stop behaviour
- Relying on prompts for hard guarantees

---

## 📊 Visual Diagram
```
  ModelSettings(tool_choice=?)
     auto | required | none | "<tool name>"
              |
              v
  Turn 1 --> LLM --(tool call)--> tool runs --> output
                                                  |
                      reset_tool_choice=True ---> Turn 2 sent as AUTO (None)
                      reset_tool_choice=False --> Turn 2 forced again (loop!)
                                                  |
                       tool_use_behavior:         v
                   run_llm_again (default) --> LLM writes final answer
                   stop_on_first_tool     --> tool output IS final
                   StopAtTools([...])     --> stop if that tool was called
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_choice | Setting that forces/forbids tools | tools को force/मना करने वाली setting |
| reset_tool_choice | Stop forcing after a tool runs | tool चलने के बाद force बंद करना |
| tool_use_behavior | What to do with tool outputs | tool outputs का क्या करना है |
| StopAtTools | Stop when named tools are called | नामित tools बुलाने पर रुकना |
| max_turns | Cap on model turns per run | एक run में model turns की सीमा |

---

## ⚡ 3-Line Summary
English: `tool_choice` controls whether and which tool the model calls; `tool_use_behavior` controls what happens after.
The SDK resets forced choices after a tool call by default to avoid loops.
Combine forcing with stop behaviour and `max_turns` for deterministic pipelines.

Hindi: `tool_choice` तय करता है कि model कौन सा tool बुलाए; `tool_use_behavior` तय करता है कि उसके बाद क्या हो।
SDK loops से बचने के लिए default रूप से forced choice को tool call के बाद reset कर देता है।
Deterministic pipelines के लिए forcing के साथ stop behaviour और `max_turns` जोड़ें।

---

## ➡️ Next Topic
**#54 Streaming in SDK** - tools and choices are set; now we make the experience feel instant by streaming tokens and progress events to the user.

---
