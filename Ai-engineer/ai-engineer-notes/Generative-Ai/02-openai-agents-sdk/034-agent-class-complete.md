---

# 34. Agent Class — Complete
# हिंदी में: Agent Class पूरी जानकारी
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Field list taken from `dataclasses.fields(Agent)` in the installed package. Code run offline with `agents.testing.ScriptedModel`. Real-model runs are not run, they need `OPENAI_API_KEY`.

---

## 🔵 Simple Definition (2-3 lines)
`Agent` is a configuration object: a name, instructions (the system prompt), a model, tools, optional handoffs, guardrails, an output type, model settings and hooks. It does not run anything by itself; `Runner` runs it.

## 🔵 सरल परिभाषा (Hindi)
`Agent` एक configuration object है: नाम, instructions (system prompt), model, tools, वैकल्पिक handoffs, guardrails, output type, model settings और hooks। यह खुद कुछ नहीं चलाता; इसे `Runner` चलाता है।

---

## 🔴 Problem it Solves
Without one object that bundles prompt, tools and policy, every call site passes loose dicts, and each place forgets something (a guardrail, a temperature, a turn limit). `Agent` makes the whole behaviour one reusable, testable, cloneable value.

## 🔴 यह क्यों बना? (Hindi)
अगर prompt, tools और policy एक object में न हों, तो हर जगह अलग dict जाते हैं और कहीं न कहीं कुछ छूट जाता है (guardrail, temperature, turn limit)। `Agent` पूरे behaviour को एक दोबारा इस्तेमाल होने वाली, test हो सकने वाली और clone हो सकने वाली value बना देता है।

---

## 🟢 How it Works

```
Agent fields (verified in 0.24.0):
  name                 -> required, appears in traces / handoff tool name
  instructions         -> str OR function(context, agent) -> str   (system prompt)
  prompt               -> reference to a stored prompt template (advanced)
  handoff_description  -> what other agents see when choosing to hand off to this one
  tools                -> list of function tools / hosted tools / agent.as_tool()
  mcp_servers, mcp_config -> MCP tools (topics 15-17)
  handoffs             -> agents (or handoff() objects) this agent can delegate to
  model                -> model name string or a Model object
  model_settings       -> ModelSettings(temperature, max_tokens, tool_choice, ...)
  input_guardrails / output_guardrails -> checks (topics 41-43)
  output_type          -> pydantic model / dataclass / TypedDict -> structured final_output
  hooks                -> AgentHooks: on_start, on_end, on_tool_start, on_tool_end, on_handoff, on_llm_start, on_llm_end
  tool_use_behavior    -> "run_llm_again" | "stop_on_first_tool" | {"stop_at_tool_names": [...]} | function
  reset_tool_choice    -> avoid tool-call loops when tool_choice is forced
Methods: clone(**changes), as_tool(...), get_system_prompt(ctx), get_all_tools(ctx)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Agent के fields (0.24.0 में verified):
  name                 -> ज़रूरी, traces और handoff tool के नाम में दिखता है
  instructions         -> str या function(context, agent) -> str   (system prompt)
  prompt               -> stored prompt template का reference (advanced)
  handoff_description  -> दूसरे agents को दिखता है कि इस agent को कब चुनना है
  tools                -> function tools / hosted tools / agent.as_tool()
  mcp_servers, mcp_config -> MCP tools
  handoffs             -> वे agents जिन्हें यह काम सौंप सकता है
  model                -> model का नाम (string) या Model object
  model_settings       -> ModelSettings(temperature, max_tokens, tool_choice, ...)
  input_guardrails / output_guardrails -> जाँच
  output_type          -> pydantic model आदि -> structured final_output
  hooks                -> AgentHooks: on_start, on_end, on_tool_start, on_tool_end ...
  tool_use_behavior    -> tool के बाद क्या हो: LLM फिर चले या सीधे रुक जाए
  reset_tool_choice    -> forced tool_choice से tool-call loop रोकने के लिए
Methods: clone(**changes), as_tool(...), get_system_prompt(ctx), get_all_tools(ctx)
```

**Verified details:**
- `instructions` can be a function `(RunContextWrapper, Agent) -> str`; we ran it and the model received `You are Tariff Agent. Customer tier: gold. Answer in JSON.`
- The local `context=` object passed to `Runner.run` is given to tools, hooks and instruction functions, but it is NOT sent to the model.
- `clone()` returns a new agent with changed fields and leaves the original untouched (verified).
- `tool_use_behavior` was run with a scripted model: `"run_llm_again"` made 2 model calls and returned the LLM text; `"stop_on_first_tool"` and `{"stop_at_tool_names": [...]}` made 1 model call and returned the tool output directly (see third snippet below).
- `Agent` is generic over the context type: `Agent[ReqCtx]`.

**Connect to what you know:** `Agent` ~ `create_react_agent(model, tools, prompt, response_format)` in LangGraph, but it is a plain object, not a compiled graph. `output_type` ~ `with_structured_output`.

---

## 🟡 Real World Example
**Tariff Agent.** One `Agent` with a dynamic system prompt (customer tier from request context), a `get_tariff_rate` tool, `output_type=TariffAnswer` so the frontend always gets `{hs_code, duty_percent}`, `model_settings` with `temperature=0` for consistent legal-ish answers, and audit hooks that log every tool call for compliance.

**Customer Support:** `handoff_description` tells the triage agent "Billing Agent: invoices and refunds".

## 🟡 Real Example Hindi mein
**Tariff Agent.** एक `Agent` जिसमें dynamic system prompt (request context से customer tier), `get_tariff_rate` tool, `output_type=TariffAnswer` (ताकि frontend को हमेशा `{hs_code, duty_percent}` मिले), consistent जवाबों के लिए `temperature=0`, और compliance के लिए हर tool call log करने वाले audit hooks।

**Customer Support:** `handoff_description` triage agent को बताता है "Billing Agent: invoices और refunds"।

---

## 💻 Code Example — Basic
All main fields on one agent, plus `clone`. Runs offline; the scripted model returns JSON matching `output_type`.

```python
# Basic: every important Agent field in one Tariff Agent (runs offline)
from pydantic import BaseModel                           # schema for structured output
from agents import (Agent, Runner, RunContextWrapper, ModelSettings,
                    function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline fake model

set_tracing_disabled(True)                               # no key in this demo

class TariffAnswer(BaseModel):                           # output_type: forces structured JSON output
    hs_code: str
    duty_percent: float
    note: str

@function_tool                                           # a tool the agent may call
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def dynamic_instructions(ctx: RunContextWrapper[dict], agent: Agent[dict]) -> str:
    # instructions can be a function: it sees the run context and the agent
    return f"You are {agent.name}. Customer tier: {ctx.context['tier']}. Answer in JSON."

model = ScriptedModel([[assistant_message(               # scripted model returns JSON matching TariffAnswer
    '{"hs_code": "6109", "duty_percent": 12.0, "note": "cotton t-shirts"}')]])

agent = Agent[dict](                                     # Agent is generic over the context type
    name="Tariff Agent",                                 # required, shows in traces and handoff names
    instructions=dynamic_instructions,                   # str, or function(context, agent) -> str
    handoff_description="Answers customs duty questions",  # what OTHER agents see when handing off to this one
    tools=[get_tariff_rate],                             # callable tools
    model=model,                                         # production: a model name string
    model_settings=ModelSettings(temperature=0, max_tokens=300),  # sampling and limits
    output_type=TariffAnswer,                            # final_output becomes a TariffAnswer object
    tool_use_behavior="run_llm_again",                   # default: tool result goes back to the model
)

result = Runner.run_sync(agent, "Duty for HS 6109?", context={"tier": "gold"})  # context is NOT sent to the model
out: TariffAnswer = result.final_output                  # already parsed and validated
print(type(out).__name__, out.duty_percent)              # TariffAnswer 12.0
call = model.first_call                                  # ScriptedModel records what the model was sent
print("model saw instr:", call.system_instructions)      # dynamic instructions, already filled in
print("model saw tools:", [t.name for t in call.tools])  # ['get_tariff_rate']
print("model saw temperature:", call.model_settings.temperature)  # 0.0

cheap = agent.clone(name="Tariff Agent (cheap)", model_settings=ModelSettings(temperature=0.2))  # copy with changes
print(cheap.name, "| original untouched:", agent.name)  # clone does not mutate the original
```

## 💻 Code Example — Advanced
Typed context, `AgentHooks` audit trail, structured output validation, FastAPI, async, error handling (`ModelBehaviorError`, `MaxTurnsExceeded`), token usage. Runs offline via `TestClient`.

```python
# Advanced: Agent with hooks, tool_use_behavior and structured output behind FastAPI (runs offline)
from dataclasses import dataclass, field                 # request-scoped context object
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, AgentHooks, RunContextWrapper, Runner, Tool, ModelBehaviorError,
                    MaxTurnsExceeded, function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key here

@dataclass
class ReqCtx:                                            # local context: passed to tools/hooks, never to the LLM
    user_id: str
    tool_calls: list[str] = field(default_factory=list)  # audit trail filled by hooks

class TariffAnswer(BaseModel):                           # structured output contract
    hs_code: str
    duty_percent: float

class AuditHooks(AgentHooks[ReqCtx]):                    # per-agent lifecycle callbacks
    async def on_tool_start(self, context: RunContextWrapper[ReqCtx], agent: Agent[ReqCtx], tool: Tool) -> None:
        context.context.tool_calls.append(tool.name)     # record which tool ran (audit/metrics)

@function_tool
async def get_tariff_rate(ctx: RunContextWrapper[ReqCtx], hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")       # tool can read ctx.context.user_id for authorization

def build_agent(script: list) -> Agent[ReqCtx]:          # factory: script replaced by a real model in prod
    return Agent[ReqCtx](
        name="Tariff Agent",
        instructions="Look up the rate, then answer as JSON.",
        tools=[get_tariff_rate],
        output_type=TariffAnswer,                        # SDK validates the final JSON against this
        hooks=AuditHooks(),                              # attach the callbacks
        model=ScriptedModel(script),
    )

class Out(BaseModel):                                    # API response
    answer: TariffAnswer
    tools_used: list[str]
    total_tokens: int

app = FastAPI()                                          # one app, script chosen per request for the demo

@app.get("/duty/{hs_code}", response_model=Out)
async def duty(hs_code: str, bad_json: bool = False) -> Out:
    final = "not json" if bad_json else f'{{"hs_code": "{hs_code}", "duty_percent": 12.0}}'  # simulate model output
    agent = build_agent([[function_call("get_tariff_rate", {"hs_code": hs_code}, call_id="c1")],
                         [assistant_message(final)]])
    ctx = ReqCtx(user_id="u1")                           # fresh context per request (no shared state)
    try:
        result = await Runner.run(agent, f"Duty for {hs_code}?", context=ctx, max_turns=4)
    except ModelBehaviorError as exc:                    # model returned output that fails output_type
        raise HTTPException(502, f"bad model output: {type(exc).__name__}")
    except MaxTurnsExceeded:                             # loop guard
        raise HTTPException(504, "max turns exceeded")
    return Out(answer=result.final_output, tools_used=ctx.tool_calls,
               total_tokens=result.context_wrapper.usage.total_tokens)  # 0 with a scripted model

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.get("/duty/6109").json())                    # structured answer + audit trail
    print(c.get("/duty/6109", params={"bad_json": True}).status_code)  # 502 from invalid output
```

Third snippet: `tool_use_behavior` compared (runs offline).

```python
# tool_use_behavior compared: let the LLM rewrite, or stop at the tool result (runs offline)
from agents import Agent, Runner, function_tool, set_tracing_disabled  # SDK pieces
from agents.testing import ScriptedModel, function_call, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

@function_tool                                           # simple lookup tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return "12%"                                         # fixed answer for the demo

for tub in ["run_llm_again", "stop_on_first_tool", {"stop_at_tool_names": ["get_tariff_rate"]}]:
    model = ScriptedModel([                              # fresh script per run
        [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c")],  # turn 1: call the tool
        [assistant_message("LLM wrote this")],           # turn 2: only used if the loop continues
    ])
    agent = Agent(name="A", tools=[get_tariff_rate], model=model, tool_use_behavior=tub)  # behaviour under test
    r = Runner.run_sync(agent, "x")                      # run to completion
    print(tub, "->", r.final_output, "| model calls:", len(r.raw_responses))  # compare outputs and cost
```

Observed output: `run_llm_again` returned `LLM wrote this` with 2 model calls; the two stop variants returned `12%` with 1 model call.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Agent object | Node function or `create_react_agent` result | `Agent(role, goal, backstory)` | `Agent(name, instructions, ...)` | `AssistantAgent(name, model_client, ...)` |
| System prompt | Prompt/messages in node | role + goal + backstory | `instructions` (str or function) | `system_message` |
| Structured output | `with_structured_output`, `response_format` | `output_pydantic` on Task | `output_type` | `output_content_type` |
| Dynamic prompt | Build inside node | Template variables | Instructions function with context | Build when creating agent |
| Lifecycle callbacks | Callbacks / stream events | Callbacks, event listeners | `AgentHooks`, `RunHooks` | Message/event stream |
| Copy with changes | Rebuild | Rebuild | `agent.clone(**kw)` | Rebuild |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Sharing one mutable object (list/dict) as context across requests.
✅ Correct: Create a fresh context per `Runner.run` call, as in the advanced example.

❌ Mistake 2: Putting secrets or user data in `instructions` for every user and caching the agent.
✅ Correct: Use an instructions function reading the per-run context, or build the agent per request via a factory.

❌ Mistake 3: Expecting `context=` to reach the model.
✅ Correct: It is local only. To show data to the model, put it in the input or in instructions.

❌ Mistake 4: Setting `output_type` and not handling invalid output.
✅ Correct: Catch `ModelBehaviorError` (we verified it is raised for non-JSON when `output_type` is set) and return a 502 or retry.

❌ Mistake 5: Forcing `tool_choice` without thinking about loops.
✅ Correct: Keep `reset_tool_choice` default (True) or use `tool_use_behavior="stop_on_first_tool"` deliberately.

---

## 🧠 Tricky Interview Question
You want the Tariff Agent to return the raw tool result as the final answer (no extra LLM call to rephrase it) to save cost. How, and what do you lose?

**Answer:** Set `tool_use_behavior="stop_on_first_tool"` (or `{"stop_at_tool_names": ["get_tariff_rate"]}` to only stop for that tool). We verified it gives 1 model call instead of 2 and `final_output` is the tool's return value. You lose the LLM's ability to explain, combine several tool results or recover from an error message, and `output_type` no longer constrains the answer (the tool output is the answer), so the tool itself must return the final shape. Use it for lookup-only endpoints; keep the default when the model must reason over results.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the minimum needed to create an `Agent`?

**A1:** Only `name`. Instructions, tools and model are optional (verified we can construct `Agent(name="x")`). In practice you add instructions and tools.

**Q2:** What can `instructions` be?

**A2:** A string or a function `(RunContextWrapper, Agent) -> str` (sync or async), used for per-run dynamic prompts.

**Q3:** What does `output_type` do and what if the model breaks it?

**A3:** It makes the SDK request structured output and parse/validate the final answer into that type. Invalid output raises `ModelBehaviorError`, which you catch and map to an error response or a retry.

**Q4:** Difference between `AgentHooks` and `RunHooks`?

**A4:** `AgentHooks` attach to one agent (`hooks=` on the agent); `RunHooks` are passed to `Runner.run(hooks=...)` and see all agents in the run. Use run hooks for global metrics, agent hooks for agent-specific audit.

**Q5:** Design the Agent configuration for a regulated Tariff service.

**A5:** `temperature=0`, `output_type` with a strict pydantic model, instructions function injecting tenant rules, input and output guardrails, `AgentHooks` writing an audit log (tool name, user id, trace id), `tool_use_behavior="stop_on_first_tool"` for pure lookups, `max_turns` set on `Runner.run`, agent built by a factory so tests inject a `ScriptedModel`.

---

## 💰 Cost Impact
The agent config drives tokens: long `instructions` and many tool schemas are sent on every model call; `output_type` adds a schema to the request; each extra turn resends the history. Formula (approximate): tokens ~ turns x (instructions + tool schemas + history) + outputs. `max_tokens` in `ModelSettings` caps output; `stop_on_first_tool` removes one whole model call. Prices vary (approximate, from public pricing at time of writing, verify).

**Tips:** keep instructions short, few well-described tools, `temperature=0` for fewer retries, `stop_on_first_tool` for lookups, cheaper model for simple agents, use `clone` to make a cheap variant for triage.

---

## 🔷 When to Use
✅ Use when:
- You want a reusable, testable unit of prompt + tools + policy
- You need structured outputs (`output_type`) or lifecycle hooks
- Different tenants/tiers need slightly different agents (use `clone` or an instructions function)

❌ Avoid when:
- One agent has 20+ tools and a huge prompt (split into specialists with handoffs)
- You need durable multi-step state (use LangGraph for that part)

---

## 📊 Visual Diagram
```
                    +-------------------------- Agent ---------------------------+
 context (local) -->| name | instructions(fn/str) | model + model_settings        |
                    | tools | handoffs | input/output guardrails                 |
                    | output_type | hooks | tool_use_behavior                    |
                    +---------------------------+--------------------------------+
                                                |
                                  Runner.run(agent, input, context, max_turns)
                                                |
                       model call -> tool? -> hooks.on_tool_start/end -> model call
                                                |
                             final_output (str or output_type object)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| instructions | System prompt (str or function) | system prompt |
| output_type | Type the final answer must match | final answer का ढाँचा |
| ModelSettings | Temperature, max_tokens, tool_choice... | model के sampling settings |
| AgentHooks | Lifecycle callbacks for one agent | एक agent के callbacks |
| tool_use_behavior | What happens after a tool returns | tool के बाद का व्यवहार |
| clone | Copy an agent with changed fields | बदलाव के साथ agent की copy |
| context | Local run object, not sent to the model | local object, model को नहीं जाता |

---

## ⚡ 3-Line Summary
English: `Agent` bundles name, instructions, model, tools, handoffs, guardrails, output type and hooks.
Instructions can be a function of the run context; `clone` makes variants.
`tool_use_behavior` and `output_type` control how the loop ends and what you get back.

Hindi: `Agent` में name, instructions, model, tools, handoffs, guardrails, output type और hooks एक साथ होते हैं।
Instructions run context का function हो सकता है; `clone` से variants बनते हैं।
`tool_use_behavior` और `output_type` तय करते हैं कि loop कैसे खत्म हो और क्या मिले।

---

## ➡️ Next Topic
**#35 Runner Class, Complete** - the agent is just config; the `Runner` runs the loop. We cover its parameters (`context`, `max_turns`, `run_config`, `session`, `hooks`) and the `RunResult` object.

---
