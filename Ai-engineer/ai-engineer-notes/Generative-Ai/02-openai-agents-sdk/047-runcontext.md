---

# 47. RunContext
# हिंदी में: RunContext (RunContextWrapper के अंदर क्या है)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline. Token numbers in the examples are SCRIPTED values I put into the fake model's `Usage`, not real measurements. The hook that raised an error showed that the SDK wraps it in `UserError` (the original is on `__cause__`).

---

## 🔵 Simple Definition (2-3 lines)
`RunContextWrapper` is the object the SDK passes to your tools, hooks, guardrails and dynamic instructions. It holds your own `context`, the running `usage` (requests and tokens), the `turn_input` for the current turn, and (for tools) a richer `ToolContext` with `tool_name` and `tool_call_id`.

## 🔵 सरल परिभाषा (Hindi)
`RunContextWrapper` वह object है जो SDK आपके tools, hooks, guardrails और dynamic instructions को देता है। इसमें आपका अपना `context`, चलता हुआ `usage` (requests और tokens), मौजूदा turn का `turn_input`, और tools के लिए अधिक जानकारी वाला `ToolContext` (`tool_name`, `tool_call_id`) होता है।

---

## 🔴 Problem it Solves
Cross-cutting concerns (token budgets, audit logs, per-tool metrics, correlation ids) need run-level information in places where you are not holding the result object yet. Without the wrapper you would thread counters through every function or patch the model client. The wrapper gives one live, shared view of the run.

## 🔴 यह क्यों बना? (Hindi)
Token budget, audit log, per-tool metrics और correlation id जैसे cross-cutting काम को run-level जानकारी चाहिए, उन जगहों पर जहाँ result object अभी आपके पास नहीं है। Wrapper के बिना आपको हर function में counters पास करने पड़ते या model client को patch करना पड़ता। Wrapper run का एक live, shared view देता है।

---

## 🟢 How it Works

```
Step 1 -> Runner creates ONE RunContextWrapper per run
          (context=your object, usage=Usage())
Step 2 -> After every model call the SDK adds that call's tokens
          to wrapper.usage
Step 3 -> Tools get a ToolContext (subclass of the wrapper):
          + tool_name, tool_call_id (and tool_arguments)
Step 4 -> Hooks (RunHooks/AgentHooks) and guardrails get the
          same wrapper -> read usage, write to context
Step 5 -> After the run: result.context_wrapper.usage
          = total requests / input / output / total tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Runner हर run के लिए एक RunContextWrapper बनाता है
          (context=आपका object, usage=Usage())
Step 2 -> हर model call के बाद SDK उसके tokens
          wrapper.usage में जोड़ता है
Step 3 -> Tools को ToolContext मिलता है (wrapper की subclass):
          + tool_name, tool_call_id (और tool_arguments)
Step 4 -> Hooks (RunHooks/AgentHooks) और guardrails को वही
          wrapper मिलता है -> usage पढ़ो, context में लिखो
Step 5 -> Run के बाद: result.context_wrapper.usage
          = कुल requests / input / output / total tokens
```

**Fields verified in 0.24.0:** `RunContextWrapper(context, usage, turn_input, tool_input, ...)`. In a tool we saw `type(ctx).__name__ == 'ToolContext'`, with `tool_name='probe'` and `tool_call_id='call-1'`.

**`Usage` fields:** `requests`, `input_tokens`, `output_tokens`, `total_tokens`, plus `input_tokens_details` and `output_tokens_details` (cached and reasoning tokens). With a real model these come from the provider response. The scripted model reports zero unless you supply a `Usage`.

**Hook signatures verified:** `RunHooks.on_tool_start(context, agent, tool)` and `on_tool_end(context, agent, tool, result)` are async and receive the wrapper.

**Gotcha:** an exception raised inside a hook or tool is wrapped by the SDK in `UserError`; catch `UserError` and inspect `exc.__cause__`.

**Hindi नोट:** `ctx.context` आपका object है, `ctx.usage` SDK का। Token budget enforce करना हो तो `on_tool_start` या `on_llm_end` जैसे hook में `ctx.usage.total_tokens` देखो।

---

## 🟡 Real World Example
**Tariff Agent.** A finance team wants a hard token budget per request. A `RunHooks` subclass checks `context.usage.total_tokens` before each tool call and aborts the run with HTTP 429 when the budget is exceeded. The same hook appends `tool_start/tool_end` lines to an audit list in the context.

**Research Agent:** log `tool_call_id` with every external API call so you can correlate with provider logs.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Finance team हर request पर hard token budget चाहती है। एक `RunHooks` subclass हर tool call से पहले `context.usage.total_tokens` जाँचती है और budget पार होते ही run रोककर HTTP 429 देती है। वही hook context की audit list में `tool_start/tool_end` लाइनें जोड़ता है।

**Research Agent:** हर external API call के साथ `tool_call_id` log करो ताकि provider logs से मिलान हो सके।

---

## 💻 Code Example — Basic
Runs offline. The tool prints what is inside the wrapper; token numbers are SCRIPTED (100/10 and 150/5), so the totals shown are just their sums.

```python
# Basic: inspect RunContextWrapper inside a tool and after the run (offline)
import asyncio                                           # async runner
from dataclasses import dataclass                        # context type
from agents import Agent, Runner, RunContextWrapper, function_tool  # SDK
from agents.tool_context import ToolContext              # richer wrapper handed to tools
from agents.testing import ScriptedModel, ModelStep, assistant_message, function_call  # fake LLM
from agents import Usage                                 # token usage object

@dataclass
class Ctx:
    user: str

seen: dict = {}                                          # collect what the tool saw

@function_tool
def probe(ctx: RunContextWrapper[Ctx]) -> str:           # SDK actually passes a ToolContext (subclass)
    """Probe the run context."""
    seen["type"] = type(ctx).__name__                    # ToolContext
    seen["context"] = ctx.context                        # our own object
    seen["usage_requests"] = ctx.usage.requests          # usage so far (live, shared across the run)
    seen["has_turn_input"] = bool(ctx.turn_input)        # items sent on this turn
    seen["tool_name"] = getattr(ctx, "tool_name", None)  # only on ToolContext
    seen["tool_call_id"] = getattr(ctx, "tool_call_id", None)
    return "ok"

async def main() -> None:
    model = ScriptedModel([
        ModelStep(output=[function_call("probe", {}, call_id="call-1")],
                  usage=Usage(requests=1, input_tokens=100, output_tokens=10, total_tokens=110)),  # SCRIPTED numbers, not real
        ModelStep(output=[assistant_message("done")],
                  usage=Usage(requests=1, input_tokens=150, output_tokens=5, total_tokens=155)),
    ])
    agent = Agent[Ctx](name="Tariff Agent", instructions="x", model=model, tools=[probe])
    res = await Runner.run(agent, "go", context=Ctx(user="u-1"))
    print("seen in tool:", seen)
    u = res.context_wrapper.usage                        # final usage after the run
    print("usage after run:", u.requests, u.input_tokens, u.output_tokens, u.total_tokens)  # sums of the SCRIPTED values
    print("same context object:", res.context_wrapper.context.user)

asyncio.run(main())
```

## 💻 Code Example — Advanced
A token-budget guard implemented as `RunHooks`, behind FastAPI. Returns 429 when the live usage passes the budget. Scripted token numbers, offline.

```python
# Advanced: read RunContextWrapper in hooks + dynamic instructions, enforce a token budget (offline, FastAPI)
from dataclasses import dataclass                        # context
from fastapi import FastAPI, HTTPException               # web
from fastapi.testclient import TestClient                # in-process test client
from pydantic import BaseModel                           # schema
from agents import (Agent, Runner, RunContextWrapper, RunHooks, Tool, Usage,
                    function_tool, MaxTurnsExceeded, UserError)  # SDK
from agents.testing import ScriptedModel, ModelStep, assistant_message, function_call  # fake LLM

@dataclass
class Ctx:
    user: str
    budget_tokens: int                                   # hard cap for this run
    events: list[str]                                    # log of hook events

class BudgetError(Exception):                            # our own failure type
    pass

class BudgetHooks(RunHooks[Ctx]):                        # lifecycle callbacks get the same RunContextWrapper
    async def on_tool_start(self, context: RunContextWrapper[Ctx], agent: Agent[Ctx], tool: Tool) -> None:
        used = context.usage.total_tokens                # live usage so far
        context.context.events.append(f"tool_start {tool.name} used={used}")
        if used > context.context.budget_tokens:         # stop BEFORE running another tool
            raise BudgetError(f"used {used} > budget {context.context.budget_tokens}")
    async def on_tool_end(self, context: RunContextWrapper[Ctx], agent: Agent[Ctx], tool: Tool, result: str) -> None:
        context.context.events.append(f"tool_end {tool.name}")

@function_tool
def duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

def make_model() -> ScriptedModel:                       # scripted usage numbers (NOT real measurements)
    return ScriptedModel([
        ModelStep(output=[function_call("duty", {"code": "6109.10"}, call_id="a")],
                  usage=Usage(requests=1, input_tokens=400, output_tokens=20, total_tokens=420)),
        ModelStep(output=[function_call("duty", {"code": "6203.42"}, call_id="b")],
                  usage=Usage(requests=1, input_tokens=500, output_tokens=20, total_tokens=520)),
        ModelStep(output=[assistant_message("Both 20%.")],
                  usage=Usage(requests=1, input_tokens=600, output_tokens=10, total_tokens=610)),
    ])

app = FastAPI()

class Ask(BaseModel):
    question: str
    budget_tokens: int = 5000

@app.post("/ask")
async def ask(body: Ask) -> dict:
    ctx = Ctx(user="u-1", budget_tokens=body.budget_tokens, events=[])  # per-request context
    agent = Agent[Ctx](name="Tariff Agent", instructions="x", model=make_model(), tools=[duty])
    try:
        res = await Runner.run(agent, body.question, context=ctx, hooks=BudgetHooks(), max_turns=6)
    except UserError as exc:                             # SDK wraps an exception raised inside a hook/tool in UserError
        if isinstance(exc.__cause__, BudgetError):       # the original error is kept on __cause__
            raise HTTPException(status_code=429, detail=str(exc.__cause__)) from exc
        raise HTTPException(status_code=500, detail="tool or hook failed") from exc
    except MaxTurnsExceeded as exc:
        raise HTTPException(status_code=504, detail="too many turns") from exc
    u = res.context_wrapper.usage                        # read final usage from the wrapper
    return {"answer": res.final_output, "total_tokens": u.total_tokens, "events": ctx.events}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/ask", json={"question": "q", "budget_tokens": 5000}).json())
    r = c.post("/ask", json={"question": "q", "budget_tokens": 500})   # small budget: 1st tool ok (420), 2nd refused (940)
    print(r.status_code, r.json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Run-level usage object | `usage_metadata` on messages; callbacks | `crew.usage_metrics` after kickoff | `ctx.usage` live, `result.context_wrapper.usage` after | `RequestUsage` on model results / client counters |
| Lifecycle hooks | Callbacks / stream modes | Task/step callbacks, event bus | `RunHooks` and `AgentHooks` | Message/event handlers |
| Tool call id in tool | In tool call message | Limited | `ToolContext.tool_call_id` | In function call content |
| Live budget check | In a node via state | Via callbacks | In hook via `ctx.usage` | Termination conditions (e.g. max tokens/messages) |
| Error wrapping | Raised as is | Raised as is | Hook/tool errors wrapped in `UserError` | Raised as is |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Reading `result.usage` that does not exist on the result.
✅ Correct: Use `result.context_wrapper.usage` (verified), or `ctx.usage` inside hooks.

❌ Mistake 2: Trusting usage numbers with a mock/fake model.
✅ Correct: A scripted model reports zero unless you give it `Usage`; only provider responses give real numbers.

❌ Mistake 3: Catching your custom exception from a hook directly.
✅ Correct: The SDK wraps it in `UserError`; catch that and test `exc.__cause__`.

❌ Mistake 4: Doing slow I/O inside hooks that run on every tool call.
✅ Correct: Keep hooks O(1); push events to a queue.

---

## 🧠 Tricky Interview Question
You enforce a token budget in `on_tool_start`. A request still overshoots the budget by 2x. How is that possible and what do you change?

**Answer:** The check runs before a tool starts, but tokens are spent by the model calls between tools, and one large model call (long history or big tool outputs) can exceed the budget before the next check. Also parallel tool calls can all pass the check at the same moment. Fixes: check in `on_llm_end`/after each response too; keep a pre-call estimate (reject when history alone is near the limit); cap `max_turns`; truncate tool outputs; set `ModelSettings(max_tokens=...)` to bound a single response; and treat the budget as a soft limit plus a hard stop on the next check. Always report the real total from `result.context_wrapper.usage` for billing.

---

## ⚫ Interview Questions + Answers

**Q1:** What does `RunContextWrapper` hold?

**A1:** Your `context`, the live `usage`, `turn_input`, optional `tool_input`; tools receive the `ToolContext` subclass with `tool_name` and `tool_call_id`.

**Q2:** Where do you read total tokens after a run?

**A2:** `result.context_wrapper.usage.total_tokens` (also `input_tokens`, `output_tokens`, `requests`).

**Q3:** How do you stop a run mid-way on a budget?

**A3:** Raise from a hook (`on_tool_start`) and catch `UserError` around `Runner.run`, inspecting `__cause__`; or use `max_turns`.

**Q4:** How are usage numbers tested offline?

**A4:** Give the scripted model `Usage(...)` per step and assert on `context_wrapper.usage`. They are fake numbers used only to test your logic.

**Q5:** Design a per-tenant quota system on top of this.

**A5:** Put tenant id and quota in the context; a `RunHooks` reads `ctx.usage`; after the run add `usage.total_tokens` to a Redis/DB counter with atomic increments; pre-check remaining quota before starting; return 429 with reset time; sample-audit against provider billing.

---

## 💰 Cost Impact
The wrapper is free; it is how you MEASURE cost. Formula: run_cost ~ (input_tokens x input_price + output_tokens x output_price) / 1e6, using `result.context_wrapper.usage`. Input tokens grow each turn because history and tool outputs are re-sent, so cost per run is roughly quadratic in turns for long tool loops. Use prompt caching, shorter tool outputs and `max_turns`. Prices: approximate, from public pricing at time of writing, verify before budgeting.

---

## 🔷 When to Use
✅ Use when:
- Enforce budgets, quotas, or rate limits per run
- Audit logs with tool name and call id
- Per-run metrics shipped to your dashboards
- Dynamic instructions that depend on run state

❌ Avoid when:
- Heavy synchronous work inside hooks
- Treating usage from a fake model as real
- Using it to carry data the LLM must see

---

## 📊 Visual Diagram
```
  Runner.run(..., context=ctx)
        |
        v
  RunContextWrapper
  +------------------------------+
  | context   -> your object     |
  | usage     -> requests/tokens | <- updated after each model call
  | turn_input-> items this turn |
  +------------------------------+
        |            |             |
        v            v             v
     tools      RunHooks      guardrails
  (ToolContext:  on_tool_start  (read the same
   +tool_name,   on_tool_end     wrapper)
   +tool_call_id)
        |
        v
  result.context_wrapper.usage  (final totals)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RunContextWrapper | Object carrying context + usage | context + usage वाला object |
| ToolContext | Wrapper subclass given to tools | tools को मिलने वाली wrapper subclass |
| Usage | Request and token counters | requests और tokens के counters |
| RunHooks | Lifecycle callbacks for a run | run के lifecycle callbacks |
| UserError | SDK error that wraps hook/tool failures | hook/tool failure को लपेटने वाला SDK error |

---

## ⚡ 3-Line Summary
English: `RunContextWrapper` gives tools and hooks your context plus live token usage and tool call details.
Use it for budgets, audit logs and metrics, and read the final totals from `result.context_wrapper.usage`.
Errors raised in hooks or tools come out wrapped in `UserError`.

Hindi: `RunContextWrapper` tools और hooks को आपका context, live token usage और tool call की जानकारी देता है।
Budgets, audit logs और metrics के लिए इस्तेमाल करें, और अंतिम totals `result.context_wrapper.usage` से पढ़ें।
Hooks या tools में उठे errors `UserError` में लिपटकर बाहर आते हैं।

---

## ➡️ Next Topic
**#48 Tools in SDK** - with context and run state understood, we look at the full menu of tool types an agent can use: function tools, hosted tools, agents-as-tools and MCP.

---
