---

# 61. Forcing Tool Use
# हिंदी में: Tool Use को ज़बरदस्ती करवाना
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts shown come from the fake model (10 in / 5 out per call), not from a real LLM.

---

## 🔵 Simple Definition (2-3 lines)
Two separate controls exist. `ModelSettings(tool_choice=...)` tells the MODEL which tool it must call ('required', 'auto', 'none' or a tool name). `tool_use_behavior` tells the SDK what to do AFTER the tool ran ('run_llm_again' default, 'stop_on_first_tool', `{'stop_at_tool_names': [...]}` or your own function).

## 🔵 सरल परिभाषा (Hindi)
दो अलग controls हैं। `ModelSettings(tool_choice=...)` MODEL को बताता है कि कौन सा tool call करना ही है ('required', 'auto', 'none' या tool का नाम)। `tool_use_behavior` SDK को बताता है कि tool चलने के BAAD क्या करना है ('run_llm_again' default, 'stop_on_first_tool', `{'stop_at_tool_names': [...]}` या आपका अपना function)।

---

## 🔴 Problem it Solves
By default the model may answer from memory instead of calling your authoritative tool (a made-up duty rate), and even after a tool call the SDK sends the result to the LLM again, spending a second call just to rephrase a value you already trust. Forcing fixes correctness; stopping fixes cost and latency.

## 🔴 यह क्यों बना? (Hindi)
Default में model आपके authoritative tool को call करने की जगह याददाश्त से जवाब दे सकता है (गढ़ा हुआ duty rate), और tool call के बाद भी SDK result को फिर LLM को भेजता है, यानी जो value आप पर भरोसेमंद है उसे दोहराने के लिए दूसरी call लगती है। Forcing से correctness सुधरती है; stopping से cost और latency।

---

## 🟢 How it Works

```
tool_choice (model side, ModelSettings)
  "auto"      model decides            (default)
  "required"  must call SOME tool this turn
  "none"      must NOT call tools
  "<name>"    must call THAT tool

tool_use_behavior (SDK side, Agent)
  "run_llm_again"                  tool result -> LLM -> answer (default)
  "stop_on_first_tool"             first tool output = final output
  {"stop_at_tool_names": [...]}    stop only for these tools
  function(ctx, results)           return ToolsToFinalOutputResult

reset_tool_choice=True (default): after a tool call tool_choice
  resets to auto, otherwise "required" would loop forever
```

## 🟢 कैसे काम करता है? (Hindi)

```
tool_choice (model की तरफ़, ModelSettings)
  "auto"      model तय करता है            (default)
  "required"  इस turn में कोई न कोई tool call करना ही है
  "none"      tool call नहीं करना
  "<name>"    वही tool call करना है

tool_use_behavior (SDK की तरफ़, Agent)
  "run_llm_again"                  tool result -> LLM -> answer (default)
  "stop_on_first_tool"             पहले tool का output ही final output
  {"stop_at_tool_names": [...]}    सिर्फ़ इन tools पर रुको
  function(ctx, results)           ToolsToFinalOutputResult लौटाओ

reset_tool_choice=True (default): tool call के बाद tool_choice वापस
  auto हो जाता है, वरना "required" अनंत loop बना देता
```

**Verified (b61):** with `tool_choice="required"` the settings the model received were `['required', None]` - first turn forced, second turn reset (None = auto). With `tool_choice="get_tariff_rate"` plus `tool_use_behavior="stop_on_first_tool"` the final output was the raw tool string `20%` and the model was called exactly once. `Agent(...).reset_tool_choice` defaults to `True`.

**Advanced (a61):** a function `finish_on_lookup(ctx, results)` returns `ToolsToFinalOutputResult(is_final_output=True, final_output=...)` only when the authoritative `lookup_duty` tool ran; for a chatty `explain` tool it returns `is_final_output=False` so the LLM still polishes the answer. The endpoint reported `llm_calls: 1`.

**Hindi नोट:** याद रखने का तरीका: `tool_choice` = "model को हुक्म", `tool_use_behavior` = "SDK की आदत"। `required` + `reset_tool_choice=False` = अनंत loop का नुस्खा (max_turns पर `MaxTurnsExceeded`)। Structured output (`output_type`) वाले agent में tool-stop सावधानी से इस्तेमाल करें, क्योंकि output tool के string से मेल खाना चाहिए।

---

## 🟡 Real World Example
**Tariff Agent.** Duty rates must never come from the model's memory. Force `tool_choice='required'` so the model always calls `get_tariff_rate`, and use a stop function so the typed `Duty(hs_code, percent)` returned by `lookup_duty` becomes the API response directly, skipping the summarising LLM call.

**Customer Support Agent:** force `lookup_order` for any message containing an order id.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Duty rates कभी model की याददाश्त से नहीं आने चाहिए। `tool_choice='required'` से model हमेशा `get_tariff_rate` call करेगा, और stop function से `lookup_duty` का typed `Duty(hs_code, percent)` सीधे API response बन जाता है, summarise करने वाली LLM call बच जाती है।

**Customer Support Agent:** जिस message में order id हो उसके लिए `lookup_order` को force करो।

---

## 💻 Code Example — Basic
Runs offline. The scripted model records the `ModelSettings` the SDK sent, so we can prove the `required` then reset behaviour.

```python
# Basic: forcing tool use - tool_choice (what the MODEL must do) vs tool_use_behavior (what the SDK does AFTER a tool).
# verified against openai-agents 0.24.0 (offline; the scripted model records the settings the SDK sent it)
import asyncio
from agents import Agent, ModelSettings, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

CALL = [tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')]    # what a compliant model would emit

async def main() -> None:
    # 1) tool_choice="required": model must call SOME tool this turn; default tool_use_behavior runs the LLM again.
    m1 = ScriptedModel([CALL, [text("Rate is 20%")]])
    a1 = Agent(name="A1", instructions="x", tools=[get_tariff_rate], model=m1,
               model_settings=ModelSettings(tool_choice="required"))
    r1 = await Runner.run(a1, "q")
    print(r1.final_output, [s.tool_choice for s in m1.seen_settings])   # Rate is 20% ['required', None]  <- reset after use

    # 2) force ONE named tool + stop right after it: tool output becomes the final answer, no 2nd LLM call.
    m2 = ScriptedModel([CALL, [text("never reached")]])
    a2 = Agent(name="A2", instructions="x", tools=[get_tariff_rate], model=m2, tool_use_behavior="stop_on_first_tool",
               model_settings=ModelSettings(tool_choice="get_tariff_rate"))
    r2 = await Runner.run(a2, "q")
    print(r2.final_output, m2.calls)                              # 20% 1

    # 3) reset_tool_choice=False keeps forcing every turn (risk: infinite loop until max_turns).
    print(Agent(name="A3", instructions="x").reset_tool_choice)   # True is the default

asyncio.run(main())
```

Expected output: `Rate is 20% ['required', None]`, `20% 1`, `True`.

## 💻 Code Example — Advanced
FastAPI: custom `tool_use_behavior` function that stops only for the authoritative tool, `tool_choice='required'` and `parallel_tool_calls=False`. Output: `{'duty': {'hs_code': '6109.10', 'percent': 20.0}, 'llm_calls': 1}` then the agent name `X`.

```python
# Advanced: custom tool_use_behavior function + StopAtTools, behind FastAPI (offline model).
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import json
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from agents import (Agent, FunctionToolResult, ModelSettings, RunContextWrapper, Runner,
                    ToolsToFinalOutputResult, function_tool, set_tracing_disabled)
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

class Duty(BaseModel):                                            # typed final output produced BY A TOOL, not by the LLM
    hs_code: str
    percent: float

@function_tool
def lookup_duty(hs_code: str) -> Duty:                            # structured tool result
    """Authoritative duty lookup."""
    return Duty(hs_code=hs_code, percent=20.0)

@function_tool
def explain(topic: str) -> str:                                   # a "chatty" tool whose output the LLM should still polish
    """Explain a customs topic in plain words."""
    return f"{topic}: duty is a tax on imported goods."

def finish_on_lookup(ctx: RunContextWrapper[Any], results: list[FunctionToolResult]) -> ToolsToFinalOutputResult:
    for r in results:                                             # inspect every tool result of this turn
        if r.tool.name == "lookup_duty":                          # authoritative tool => skip the LLM, save a call + tokens
            return ToolsToFinalOutputResult(is_final_output=True, final_output=r.output.model_dump_json())
    return ToolsToFinalOutputResult(is_final_output=False)        # otherwise let the LLM run again

def build(model: Any) -> Agent[None]:
    return Agent(name="Tariff", instructions="Use tools.", model=model, tools=[lookup_duty, explain],
                 tool_use_behavior=finish_on_lookup,              # alternatives: "stop_on_first_tool", {"stop_at_tool_names": [...]}
                 model_settings=ModelSettings(tool_choice="required", parallel_tool_calls=False))

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/duty")
async def duty(q: Q) -> dict[str, Any]:
    m = ScriptedModel([[tool_call("lookup_duty", '{"hs_code":"6109.10"}')], [text("unused")]])   # offline script
    res = await Runner.run(build(m), q.question, max_turns=3)
    return {"duty": json.loads(res.final_output), "llm_calls": m.calls}   # 1 call: the LLM never summarised

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/duty", json={"question": "duty on 6109.10"}).json())
    # also valid, simplest form: tool_use_behavior={"stop_at_tool_names": ["lookup_duty"]}
    print(Agent(name="X", instructions="y", tools=[lookup_duty], tool_use_behavior={"stop_at_tool_names": ["lookup_duty"]}).name)
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Force a tool call | `bind_tools(tool_choice=...)` on the model | Not a direct setting (agent reasons) | `ModelSettings(tool_choice=...)` | `tool_choice` via model client create args |
| Stop after tool | Edge from tool node to END | `result_as_answer=True` on a tool | `tool_use_behavior` | `reflect_on_tool_use=False` (AssistantAgent) |
| Per-tool stop | Conditional edge | Per tool flag | `stop_at_tool_names` / function | Per agent setting |
| Prevent infinite forcing | recursion_limit | max_iter | `reset_tool_choice` + `max_turns` | max tool iterations |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: Setting `tool_choice='required'` and `reset_tool_choice=False`.
✅ Correct: Keep the default reset, or the model must call a tool every turn until `MaxTurnsExceeded`.

❌ Mistake: Using `stop_on_first_tool` when the tool returns raw JSON the user should not see.
✅ Correct: Return a clean string, use a stop function that formats it, or let the LLM run again.

❌ Mistake: Thinking `tool_choice` controls the SDK flow.
✅ Correct: It only constrains the model; `tool_use_behavior` controls what the SDK does after the tool.

❌ Mistake: Forcing a tool for every turn of a chat (greetings too).
✅ Correct: Force only when the request needs it (route first) or use 'auto' with strong instructions.

---

## 🧠 Tricky Interview Question
`tool_choice='required'` is set, yet the run ends with MaxTurnsExceeded. Why?

**Answer:** With `required` the model must emit a tool call on every turn it is forced. The SDK resets the choice after a tool call by default (`reset_tool_choice=True`) to avoid exactly this, so check: (1) did someone set `reset_tool_choice=False`, (2) is the tool failing and the model retrying the same call each turn (error text goes back as an observation; look at tool errors), (3) are there several tools and `tool_use_behavior` never stops, so the model keeps calling tools, (4) a provider that ignores the reset on a custom model wrapper. Fix: leave defaults, make the error visible, add a stop function, and set a realistic `max_turns`.

---

## ⚫ Interview Questions + Answers

**Q1:** tool_choice vs tool_use_behavior?

**A1:** tool_choice constrains the model's tool call; tool_use_behavior decides what the SDK does with the tool result.

**Q2:** How do you force one specific tool?

**A2:** `ModelSettings(tool_choice="<tool name>")`.

**Q3:** How do you skip the second LLM call?

**A3:** `tool_use_behavior="stop_on_first_tool"` or `{"stop_at_tool_names": [...]}` or a custom function.

**Q4:** Why does the SDK reset tool_choice?

**A4:** Otherwise a forced tool would be called forever.

**Q5:** Design: a compliance flow where the answer must come from a DB tool, never the model.

**A5:** Force the tool, return a typed object from it, stop on that tool with a function returning its JSON, add an output guardrail as a second check, test with a scripted model that tries to answer without the tool, and log tool outputs for audit.

---

## 💰 Cost Impact
Stopping after the tool removes one LLM call (the 'rephrase' call): the advanced sample made 1 model call instead of 2. Formula: saved tokens ~ (history + tool result) as input plus the answer as output of the skipped call. Forcing adds no tokens by itself. Real savings depend on prompt size - measure with `context_wrapper.usage`. Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Facts must come from a tool, not memory
- Tool result is already the final answer (typed lookup)
- You want lower latency and fewer tokens

❌ Avoid when:
- The answer needs reasoning over several tool results
- You use `required` with chit-chat inputs
- You turned off reset_tool_choice

---

## 📊 Visual Diagram
```
  user question
      |
      v
  LLM  --(tool_choice="required")--> tool call get_tariff_rate
                                         |
                       tool_use_behavior? v
        run_llm_again: result -> LLM -> text answer   (2 LLM calls)
        stop_on_first_tool / function: result IS final output (1 LLM call)
  after the tool call: tool_choice resets to auto (reset_tool_choice=True)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_choice | Model-side tool constraint | model पर tool की पाबंदी |
| tool_use_behavior | SDK behaviour after tools | tool के बाद SDK का व्यवहार |
| StopAtTools | Stop for named tools | चुने हुए tools पर रुकना |
| ToolsToFinalOutputResult | Return type of stop function | stop function का return type |
| reset_tool_choice | Reset to auto after a call | call के बाद auto पर लौटना |
| Authoritative tool | Source of truth | भरोसेमंद स्रोत |

---

## ⚡ 3-Line Summary
English: `tool_choice` forces the model to call a tool; `tool_use_behavior` decides whether the SDK stops after it.
Force + stop makes answers correct and saves one LLM call.
Keep `reset_tool_choice` on to avoid infinite loops.

Hindi: `tool_choice` model को tool call करने पर मजबूर करता है; `tool_use_behavior` तय करता है कि SDK उसके बाद रुके या नहीं।
Force + stop से जवाब सही रहते हैं और एक LLM call बचती है।
अनंत loops से बचने के लिए `reset_tool_choice` चालू रखें।

---

## ➡️ Next Topic
**#62 Lifecycle Hooks** - to see when each LLM call, tool call and handoff happens (for metrics and audit) we use `RunHooks` and `AgentHooks`.

---
