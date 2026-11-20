---

# 39. Handoff with Context
# हिंदी में: Context के साथ Handoff
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). All code ran offline with `agents.testing.ScriptedModel` (the router's arguments are scripted, not produced by a real LLM). Real-model behaviour (whether the model fills `reason` and `priority` sensibly) is not run, it needs `OPENAI_API_KEY`.

---

## 🔵 Simple Definition (2-3 lines)
"Context" in a handoff means two different things. (1) Structured data the router model sends along with the transfer (`input_type` + `on_handoff`). (2) The conversation history the next agent receives (`input_filter`, `nest_handoff_history`). Separately, the local run `context=` object is shared with every callback and tool but never sent to the model.

## 🔵 सरल परिभाषा (Hindi)
Handoff में "context" के दो अलग मतलब हैं। (1) router model transfer के साथ जो structured data भेजता है (`input_type` + `on_handoff`)। (2) अगले agent को मिलने वाला conversation history (`input_filter`, `nest_handoff_history`)। इनसे अलग, local run `context=` object हर callback और tool के साथ साझा होता है पर model को कभी नहीं भेजा जाता।

---

## 🔴 Problem it Solves
A plain handoff only says "go to Senior Support". The specialist then has to re-derive why (reason, priority, order id) from the raw history, which wastes tokens and loses facts. You may also want to hide earlier tool noise or sensitive turns from the next agent. Handoff context solves both.

## 🔴 यह क्यों बना? (Hindi)
सादा handoff सिर्फ कहता है "Senior Support के पास जाओ"। फिर specialist को कारण (reason, priority, order id) कच्चे history से फिर निकालना पड़ता है, जिसमें tokens लगते हैं और बातें छूट जाती हैं। आप शायद पिछले tool noise या संवेदनशील turns को अगले agent से छुपाना भी चाहें। Handoff context दोनों हल करता है।

---

## 🟢 How it Works

```
Step 1 -> class Escalation(BaseModel): reason: str; priority: Literal["low","high"]
Step 2 -> handoff(specialist, input_type=Escalation, on_handoff=cb, input_filter=f)
Step 3 -> the handoff tool's JSON schema now has properties {reason, priority}
Step 4 -> router model calls escalate({"reason": "...", "priority": "high"})
Step 5 -> SDK validates the JSON against Escalation (invalid -> error, no transfer)
Step 6 -> cb(ctx, escalation) runs -> store it in ctx.context (local, trusted)
Step 7 -> input_filter(HandoffInputData) edits the history -> specialist receives it
Step 8 -> specialist's tools read ctx.context.escalation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> class Escalation(BaseModel): reason: str; priority: Literal["low","high"]
Step 2 -> handoff(specialist, input_type=Escalation, on_handoff=cb, input_filter=f)
Step 3 -> handoff tool के JSON schema में अब {reason, priority} properties होंगी
Step 4 -> router model escalate({"reason": "...", "priority": "high"}) call करता है
Step 5 -> SDK JSON को Escalation के विरुद्ध validate करता है (गलत -> error, transfer नहीं)
Step 6 -> cb(ctx, escalation) चलता है -> उसे ctx.context में रखें (local, भरोसेमंद)
Step 7 -> input_filter(HandoffInputData) history बदलता है -> specialist को वही मिलता है
Step 8 -> specialist के tools ctx.context.escalation पढ़ते हैं
```

**Verified facts (0.24.0):**
- With `input_type=EscalationData` the handoff's `input_json_schema` had properties `priority` and `reason` (printed from `triage.handoffs[0].input_json_schema`). The callback signature becomes `(ctx, data)`; without `input_type` it is `(ctx)`.
- The data reached the callback and was stored in the typed context (`{'reason': 'refund delayed 30 days', 'priority': 'high'}`), and a specialist tool (`open_ticket`) read it back.
- A `Literal["low", "high"]` field rejected `"urgent"`: the run ended with an `AgentsException` subclass that our endpoint mapped to HTTP 502 (no transfer happened).
- `handoff_filters.remove_all_tools` is available in `agents.extensions.handoff_filters` (module also has `nest_handoff_history`, `default_handoff_history_mapper`). With that filter the specialist received only `[{"role": "user", "content": "My refund is 30 days late!!"}]`; the handoff call/output items were removed.
- `HandoffInputData` has fields `input_history`, `pre_handoff_items`, `new_items`, `run_context`, `input_items`; a custom `input_filter` receives one and must return one.
- The model does NOT automatically get the handoff arguments in the specialist's prompt; they go to your callback. If the specialist's model should see them, put them into context-aware instructions (instructions function) or into the history yourself.
- Callbacks can be `async def` (we ran an async callback).

**Connect to what you know:** `input_type` ~ passing typed parameters in a LangGraph `Command(goto=..., update={...})`; `input_filter` ~ trimming messages before the next node (`trim_messages`).

---

## 🟡 Real World Example
**Customer Support with Tariff Agent.** Triage detects an angry customer with a delayed refund and calls `escalate({"reason": "refund 30 days late", "priority": "high"})`. The callback stores it in the request context and writes an audit line. The Senior Support agent's `open_ticket` tool uses `ctx.context.escalation` to create the ticket without asking the user again. An `input_filter` strips tool noise (internal lookups) from the history the senior agent sees.

## 🟡 Real Example Hindi mein
**Tariff Agent वाला Customer Support।** Triage देखता है कि customer नाराज़ है और refund लेट है, तो `escalate({"reason": "refund 30 days late", "priority": "high"})` call करता है। Callback उसे request context में रखता है और audit line लिखता है। Senior Support agent का `open_ticket` tool `ctx.context.escalation` से ticket बना देता है, user से दोबारा पूछे बिना। `input_filter` internal lookups जैसे tool noise को history से हटा देता है।

---

## 💻 Code Example — Basic
`input_type` + `on_handoff` + `input_filter` with a typed context. Runs offline.

```python
# Basic: pass structured data with a handoff (input_type + on_handoff) and filter history (runs offline)
import json                                              # inspect what the specialist receives
from dataclasses import dataclass, field                 # typed run context
from pydantic import BaseModel                           # schema the router model must fill
from agents import (Agent, Runner, RunContextWrapper, handoff, HandoffInputData,
                    set_tracing_disabled)                # SDK pieces
from agents.extensions import handoff_filters            # ready-made history filters
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

class EscalationData(BaseModel):                         # becomes the JSON schema of the handoff tool
    reason: str                                          # why the router is transferring
    priority: str                                        # "low" | "high"

@dataclass
class Ctx:                                               # local context shared with callbacks and tools
    escalations: list[EscalationData] = field(default_factory=list)

def on_escalate(ctx: RunContextWrapper[Ctx], data: EscalationData) -> None:  # receives the parsed model input
    ctx.context.escalations.append(data)                 # store it where the specialist's tools can read it

specialist_model = ScriptedModel([[assistant_message("Escalated with high priority.")]])
specialist = Agent[Ctx](name="Senior Support", instructions="Handle escalations.", model=specialist_model)

def drop_tool_noise(data: HandoffInputData) -> HandoffInputData:  # custom input_filter example
    return handoff_filters.remove_all_tools(data)        # drop tool calls/outputs from the history

triage = Agent[Ctx](
    name="Triage Agent", instructions="Escalate angry customers.",
    handoffs=[handoff(
        specialist,
        tool_name_override="escalate",                   # clear router-facing name
        on_handoff=on_escalate,                          # (ctx, input) because input_type is set
        input_type=EscalationData,                       # model must send {reason, priority}
        input_filter=drop_tool_noise,                    # runs before the specialist sees the history
    )],
    model=ScriptedModel([[function_call("escalate", {"reason": "refund delayed 30 days", "priority": "high"}, call_id="h1")]]),
)

ctx = Ctx()                                              # fresh context for this run
result = Runner.run_sync(triage, "My refund is 30 days late!!", context=ctx)
print("answer           :", result.final_output)         # Escalated with high priority.
print("stored in context:", ctx.escalations[0].model_dump())  # {'reason': ..., 'priority': 'high'}
schema = triage.handoffs[0].input_json_schema            # what the router model had to fill
print("handoff schema   :", json.dumps(schema["properties"], sort_keys=True))
print("specialist input :", json.dumps(specialist_model.first_call.input, default=str)[:200])  # history it saw
```

## 💻 Code Example — Advanced
FastAPI: async `on_handoff`, `Literal` validation, a specialist tool reading the handoff data, per-request context, audit list, error mapping (502 for invalid handoff arguments, 504 for loops). Runs offline via `TestClient`; `router_args` exists only to script the fake router.

```python
# Advanced: handoff context in FastAPI: typed handoff data -> specialist tool reads it (runs offline)
from dataclasses import dataclass, field                 # request-scoped context
from typing import Literal                               # constrain priority values
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel, ValidationError          # schemas + validation errors
from agents import (Agent, Runner, RunContextWrapper, handoff, function_tool, MaxTurnsExceeded,
                    AgentsException, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

class Escalation(BaseModel):                             # structured data the router must provide
    reason: str
    priority: Literal["low", "high"]                     # invalid values are rejected by validation

@dataclass
class Ctx:                                               # trusted, local state (never shown to the model)
    user_id: str
    escalation: Escalation | None = None                 # filled by the handoff callback
    audit: list[str] = field(default_factory=list)

async def on_escalate(ctx: RunContextWrapper[Ctx], data: Escalation) -> None:  # async callbacks are allowed
    ctx.context.escalation = data                        # make the data available to tools
    ctx.context.audit.append(f"escalate user={ctx.context.user_id} priority={data.priority}")

@function_tool
async def open_ticket(ctx: RunContextWrapper[Ctx]) -> str:  # specialist tool reads the handoff data
    esc = ctx.context.escalation                         # set by on_escalate
    if esc is None:                                      # defensive: tool called without an escalation
        return "no escalation data"
    return f"ticket opened for {ctx.context.user_id}: {esc.reason} ({esc.priority})"

def build(router_args: dict[str, str]) -> Agent[Ctx]:    # router_args scripts the fake triage model
    senior = Agent[Ctx](name="Senior Support", instructions="Open a ticket, then confirm.",
                        tools=[open_ticket],
                        model=ScriptedModel([[function_call("open_ticket", {}, call_id="t1")],
                                             [assistant_message("Ticket opened, we will call you.")]]))
    return Agent[Ctx](name="Triage Agent", instructions="Escalate unhappy customers.",
                      handoffs=[handoff(senior, tool_name_override="escalate",
                                        input_type=Escalation, on_handoff=on_escalate)],
                      model=ScriptedModel([[function_call("escalate", router_args, call_id="h1")]]))

class In(BaseModel):
    user_id: str
    message: str
    router_args: dict[str, str]                          # demo only: what the scripted router "decides"

class Out(BaseModel):
    answer: str
    escalation: Escalation | None
    audit: list[str]

app = FastAPI()

@app.post("/chat", response_model=Out)
async def chat(body: In) -> Out:
    ctx = Ctx(user_id=body.user_id)                      # new context per request
    try:
        result = await Runner.run(build(body.router_args), body.message, context=ctx, max_turns=5)
    except MaxTurnsExceeded:
        raise HTTPException(504, "too many hops")
    except AgentsException as exc:                       # includes ModelBehaviorError for bad handoff arguments
        raise HTTPException(502, type(exc).__name__)
    return Out(answer=str(result.final_output), escalation=ctx.escalation, audit=ctx.audit)

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    ok = {"user_id": "u1", "message": "refund late!", "router_args": {"reason": "refund 30 days late", "priority": "high"}}
    print(c.post("/chat", json=ok).json())               # data flowed router -> callback -> tool
    bad = {**ok, "router_args": {"reason": "x", "priority": "urgent"}}  # priority outside the Literal
    print(c.post("/chat", json=bad).status_code)         # 502: invalid handoff input rejected
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Pass data on transfer | `Command(goto, update=...)` | Task context / output of previous task | `handoff(input_type=..., on_handoff=...)` | Handoff message content |
| Validated schema | State schema (pydantic/TypedDict) | `output_pydantic` | Pydantic `input_type` validated by SDK | Message types |
| Trim history for next agent | Reducers / `trim_messages` | Task `context` selection | `input_filter`, `nest_handoff_history` | Model context (buffered/unbounded) |
| Shared local state | Graph state | Crew memory | Run `context=` object | Team state |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using `input_type` and expecting the specialist's model to automatically see the data.
✅ Correct: The data goes to `on_handoff`; store it in context and surface it through instructions or tools.

❌ Mistake 2: Writing the callback as `(ctx)` when `input_type` is set (or `(ctx, data)` when it is not).
✅ Correct: Match the signature: `(ctx, data)` with `input_type`, `(ctx)` without.

❌ Mistake 3: Free-text `priority: str` fields.
✅ Correct: Use `Literal[...]`/enums so bad values fail validation instead of reaching your logic.

❌ Mistake 4: Filtering history by string matching on item text.
✅ Correct: Use the provided filters (`remove_all_tools`) or write a filter that works on item types.

❌ Mistake 5: Putting secrets into handoff arguments.
✅ Correct: The model produces them and they are logged in traces; keep secrets in the local context.

---

## 🧠 Tricky Interview Question
The Senior Support agent keeps re-asking "what is your issue?" even though triage already knew. You added `input_type` with `reason`. It still asks. Why, and how do you fix it?

**Answer:** `input_type` data is delivered to the `on_handoff` callback, it is not appended to the specialist's prompt. Fix: in the callback store `Escalation` in the context, then give the specialist dynamic instructions (a function `(ctx, agent) -> str` that returns text such as `Known issue: <reason from ctx.context.escalation>`) or a tool that reads it. Alternatively keep the history (default) so the original user message is visible; do not filter it away. Test with a scripted model asserting the specialist's `system_instructions` contain the reason.

---

## ⚫ Interview Questions + Answers

**Q1:** How does a handoff carry structured data?

**A1:** `handoff(agent, input_type=MyModel, on_handoff=cb)`: the model fills the schema when calling the transfer tool, the SDK validates it, and `cb(ctx, data)` receives it.

**Q2:** What is the difference between handoff `input_type` data and run `context=`?

**A2:** `input_type` data is produced by the model at transfer time. Run `context=` is your own local object, set before the run, never sent to the model, shared by callbacks, tools and hooks.

**Q3:** How do you change the history the next agent sees?

**A3:** `input_filter` (a function taking and returning `HandoffInputData`), for example `handoff_filters.remove_all_tools`, or `nest_handoff_history` to collapse it into one summary message.

**Q4:** What happens if the model sends invalid handoff data?

**A4:** Validation fails, the transfer does not happen and an `AgentsException` subclass is raised (we mapped it to 502). Use `Literal`/enums and catch the error.

**Q5:** Design context passing for a three-step escalation chain (triage, L1, L2).

**A5:** Typed context holds `Escalation`, customer id and audit list; each handoff has its own `input_type`; callbacks append to audit; instructions functions inject known facts; filters remove tool noise and PII before L2; token budget measured per hop; tests with scripted models assert what each agent received.

---

## 💰 Cost Impact
Handoff arguments are a few extra output tokens at the router. The bigger lever is history: by default the next agent receives all prior items, so every later model call carries them. Filtering or nesting history reduces input tokens on every subsequent call. Approximate, from public pricing at time of writing, verify; measure `usage` with and without the filter.

**Tips:** pass compact structured facts, drop tool outputs you do not need, nest long histories, keep instructions short.

---

## 🔷 When to Use
✅ Use when:
- The next agent needs facts the router already extracted
- You need validated, typed handoff arguments (priority, ids)
- You must hide tool noise or sensitive turns from the next agent

❌ Avoid when:
- A plain transfer is enough (adds schema tokens and failure modes)
- The data is secret (use local context instead of model-produced arguments)

---

## 📊 Visual Diagram
```
 user: "refund 30 days late!!"
   |
 Triage Agent --call--> escalate({"reason": "...", "priority": "high"})
   |                         |
   |            validate against Escalation (Literal)  --bad--> AgentsException (502)
   |                         | ok
   |             on_handoff(ctx, data) --> ctx.context.escalation = data  (local state)
   |                         |
   |            input_filter(HandoffInputData) --> trimmed history
   v                         v
 Senior Support Agent: instructions/tools read ctx.context.escalation
   |
 final answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| input_type | Pydantic schema the router fills at handoff | handoff पर router जो schema भरता है |
| on_handoff | Callback with context (and data) | transfer पर चलने वाला callback |
| input_filter | Function that edits the next agent's history | अगले agent का history बदलने वाला function |
| HandoffInputData | Object passed to an input filter | filter को मिलने वाला डेटा object |
| run context | Local object shared with tools/hooks | local साझा object |
| nest_handoff_history | Collapse history into one message | history को एक संदेश में समेटना |

---

## ⚡ 3-Line Summary
English: `input_type` + `on_handoff` carries validated structured data from router to your code.
`input_filter` / `nest_handoff_history` control what history the next agent sees.
The data does not reach the specialist's prompt unless you put it there.

Hindi: `input_type` + `on_handoff` router से आपके code तक validated structured data पहुँचाते हैं।
`input_filter` / `nest_handoff_history` तय करते हैं कि अगला agent कौन-सा history देखे।
Data specialist के prompt में तब तक नहीं जाता जब तक आप खुद न डालें।

---

## ➡️ Next Topic
**#40 Recommended Handoffs** - the official prompt prefix, naming and topology recommendations that make routing reliable in practice.

---
