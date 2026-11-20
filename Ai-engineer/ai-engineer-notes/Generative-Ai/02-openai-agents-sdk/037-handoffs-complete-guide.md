---

# 37. Handoffs — Complete Guide
# हिंदी में: Handoffs पूरी गाइड
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0). All code ran offline with `agents.testing.ScriptedModel`, so the routing decisions are scripted, not made by a real LLM. Whether a real model picks the right specialist depends on your instructions and `handoff_description`; that is not run here (needs `OPENAI_API_KEY`).

---

## 🔵 Simple Definition (2-3 lines)
A handoff lets one agent transfer the whole conversation to another agent. In the SDK it appears to the model as a tool named `transfer_to_<agent_name>`; when the model calls it, the `Runner` switches the current agent and keeps running with the new agent's instructions, tools and model.

## 🔵 सरल परिभाषा (Hindi)
Handoff में एक agent पूरी बातचीत दूसरे agent को सौंप देता है। SDK में model को यह `transfer_to_<agent_name>` नाम के tool जैसा दिखता है; model उसे call करे तो `Runner` current agent बदल देता है और नए agent के instructions, tools और model के साथ आगे चलता है।

---

## 🔴 Problem it Solves
One giant agent with 25 tools and a 3,000-token prompt picks wrong tools, costs more per turn and is hard to test. Splitting into specialists (tariff, billing, tech) fixes that, but then something must decide who answers. Handoffs are that routing mechanism.

## 🔴 यह क्यों बना? (Hindi)
25 tools और 3,000-token prompt वाला एक बड़ा agent गलत tools चुनता है, हर turn महँगा पड़ता है और test करना मुश्किल होता है। Specialists (tariff, billing, tech) में बाँटने से यह हल होता है, पर फिर तय करने वाला चाहिए कि जवाब कौन देगा। Handoffs वही routing तंत्र हैं।

---

## 🟢 How it Works

```
Step 1 -> triage = Agent(handoffs=[tariff_agent, billing_agent])
Step 2 -> SDK adds one tool per target:  transfer_to_tariff_agent, transfer_to_billing_agent
          (name = "transfer_to_" + agent name lowercased with underscores; verified)
Step 3 -> Runner.run(triage, "Duty on HS 6109?")
Step 4 -> triage model calls transfer_to_tariff_agent
Step 5 -> SDK records HandoffCallItem + HandoffOutputItem and sets current agent = Tariff Agent
Step 6 -> Tariff Agent continues the SAME run with ITS instructions, tools, model
Step 7 -> final output; result.last_agent == Tariff Agent
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> triage = Agent(handoffs=[tariff_agent, billing_agent])
Step 2 -> SDK हर target के लिए एक tool जोड़ता है: transfer_to_tariff_agent, transfer_to_billing_agent
          (नाम = "transfer_to_" + agent का नाम lowercase और underscores के साथ; verified)
Step 3 -> Runner.run(triage, "Duty on HS 6109?")
Step 4 -> triage model transfer_to_tariff_agent call करता है
Step 5 -> SDK HandoffCallItem + HandoffOutputItem दर्ज करता है और current agent = Tariff Agent
Step 6 -> Tariff Agent उसी run को अपने instructions, tools, model से आगे चलाता है
Step 7 -> final output; result.last_agent == Tariff Agent
```

**Verified facts (0.24.0):**
- Tool name for `Agent(name="Tariff Agent")` is `transfer_to_tariff_agent`. Calling a wrong name (`transfer_to_nobody`) raised `ModelBehaviorError` (`Tool ... not found in agent ...`), which our FastAPI example maps to HTTP 502.
- Default tool description: `Handoff to the Tariff Agent agent to handle the request.` plus the target's `handoff_description` when set.
- Run items on a handoff: `HandoffCallItem`, `HandoffOutputItem`, then the specialist's own items (`ToolCallItem`, `ToolCallOutputItem`, `MessageOutputItem`).
- By default (0.24.0) the specialist receives the full prior items (user message, handoff call, handoff output). With `RunConfig(nest_handoff_history=True)` the history is collapsed into one assistant message wrapped in `<CONVERSATION HISTORY>`; with `False` it is the same as the default (see third snippet).
- A handoff is a one-way transfer: the specialist answers the user. If you want the specialist's result back to the caller, use `Agent.as_tool()` instead (topic 57, agents as tools).
- The next `Runner.run` starts again from the agent you pass in. To stay with the specialist across requests, start the next run with `result.last_agent`.

**Connect to what you know:** a handoff ~ a conditional edge from a router node to a specialist node in LangGraph, except the model chooses the edge by calling a tool. CrewAI's delegation returns control to the caller; SDK handoffs do not.

---

## 🟡 Real World Example
**Tariff Agent + friends.** The customs portal has a Triage Agent that only routes. "What is the duty on HS 6109?" goes to the Tariff Agent (has `get_tariff_rate`). "Where is my refund?" goes to the Billing Agent. Each specialist has a short prompt and 2 to 3 tools, so each model call is cheaper and more accurate than one mega-agent.

**Customer Support / Research:** same pattern: triage, then a specialist.

## 🟡 Real Example Hindi mein
**Tariff Agent और साथी।** Customs portal में एक Triage Agent है जो सिर्फ routing करता है। "HS 6109 पर duty क्या है?" Tariff Agent के पास जाता है (उसके पास `get_tariff_rate` है)। "मेरा refund कहाँ है?" Billing Agent के पास जाता है। हर specialist का prompt छोटा और 2-3 tools होते हैं, इसलिए हर model call एक बड़े agent से सस्ती और सटीक होती है।

**Customer Support / Research:** यही pattern: triage फिर specialist।

---

## 💻 Code Example — Basic
Triage hands off to the Tariff Agent. Runs offline.

```python
# Basic: a triage agent hands off to a specialist (runs offline)
from agents import Agent, Runner, function_tool, set_tracing_disabled  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

tariff_model = ScriptedModel([                           # the specialist's scripted turns
    [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="t1")],
    [assistant_message("HS 6109 duty is 12%.")],
])
tariff_agent = Agent(
    name="Tariff Agent",                                 # becomes part of the handoff tool name
    handoff_description="Answers customs duty and HS code questions",  # shown to the triage model
    instructions="Use the tool to answer duty questions.",
    tools=[get_tariff_rate],
    model=tariff_model,
)
billing_agent = Agent(name="Billing Agent", handoff_description="Invoices and refunds",
                      instructions="Help with billing.", model=ScriptedModel([]))  # unused here

triage_model = ScriptedModel([                           # triage decides to transfer
    [function_call("transfer_to_tariff_agent", {}, call_id="h1")],  # a handoff is just a special tool call
])
triage = Agent(
    name="Triage Agent",
    instructions="Route the user to the right specialist.",
    handoffs=[tariff_agent, billing_agent],              # agents it may transfer to
    model=triage_model,
)

# each agent keeps its own model; the SDK switches to the specialist model after the handoff
result = Runner.run_sync(triage, "What is the duty on cotton t-shirts, HS 6109?")
print("final_output :", result.final_output)             # HS 6109 duty is 12%.
print("last_agent   :", result.last_agent.name)          # Tariff Agent took over
print("triage saw handoff tools:", [h.tool_name for h in triage_model.first_call.handoffs])  # transfer_to_...
print("items        :", [type(i).__name__ for i in result.new_items])  # HandoffCallItem, HandoffOutputItem, ...
```

## 💻 Code Example — Advanced
FastAPI chat with triage plus two specialists, a session per conversation, hop audit trail, `max_turns` guard and error mapping. Runs offline via `TestClient` (the `route_to` field exists only to script the fake triage model; remove it with a real model).

```python
# Advanced: multi-specialist handoffs behind FastAPI, sticky agent per conversation (runs offline)
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Runner, SQLiteSession, MaxTurnsExceeded, AgentsException,
                    function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

class ChatIn(BaseModel):
    conversation_id: str
    message: str
    route_to: str                                        # demo only: which specialist the scripted triage picks

class ChatOut(BaseModel):
    answer: str
    handled_by: str                                      # name of the agent that produced the answer
    handoffs: list[str]                                  # handoff tool calls seen in this run
    total_tokens: int

@function_tool
async def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def build_agents(route_to: str) -> Agent:                # scripted models replace real ones in tests
    tariff = Agent(name="Tariff Agent", handoff_description="Customs duty and HS codes",
                   instructions="Answer duty questions with the tool.", tools=[get_tariff_rate],
                   model=ScriptedModel([[function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="t1")],
                                        [assistant_message("HS 6109 duty is 12%.")]]))
    billing = Agent(name="Billing Agent", handoff_description="Invoices and refunds",
                    instructions="Help with invoices.",
                    model=ScriptedModel([[assistant_message("Your refund is being processed.")]]))
    triage = Agent(name="Triage Agent", instructions="Route to the right specialist.",
                   handoffs=[tariff, billing],           # agents -> auto tool names transfer_to_<name>
                   model=ScriptedModel([[function_call(f"transfer_to_{route_to}", {}, call_id="h1")]]))
    return triage

app = FastAPI()
sessions: dict[str, SQLiteSession] = {}                  # demo store; use a shared store in production

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn) -> ChatOut:
    session = sessions.setdefault(body.conversation_id, SQLiteSession(body.conversation_id))
    try:
        result = await Runner.run(build_agents(body.route_to), body.message, session=session, max_turns=6)
    except MaxTurnsExceeded:                             # ping-pong between agents would end here
        raise HTTPException(504, "too many agent hops")
    except AgentsException as exc:                       # e.g. model called a tool that does not exist
        raise HTTPException(502, type(exc).__name__)
    hops = [i.raw_item.name for i in result.new_items if type(i).__name__ == "HandoffCallItem"]  # audit trail
    return ChatOut(answer=str(result.final_output), handled_by=result.last_agent.name,
                   handoffs=hops, total_tokens=result.context_wrapper.usage.total_tokens)

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.post("/chat", json={"conversation_id": "a", "message": "Duty HS 6109?", "route_to": "tariff_agent"}).json())
    print(c.post("/chat", json={"conversation_id": "b", "message": "Refund please", "route_to": "billing_agent"}).json())
    print(c.post("/chat", json={"conversation_id": "c", "message": "x", "route_to": "nobody"}).status_code)  # 502
```

Third snippet: what the specialist receives after a handoff (history behaviour).

```python
# What does the specialist receive after a handoff? Compare nest_handoff_history settings (runs offline)
import json                                              # print the items the model received
from agents import Agent, Runner, RunConfig, set_tracing_disabled  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

for nest in [None, True, False]:                         # None = SDK default
    specialist_model = ScriptedModel([[assistant_message("ok")]])  # records what it is sent
    specialist = Agent(name="T", model=specialist_model)  # tool name becomes transfer_to_t
    triage = Agent(name="Tr", handoffs=[specialist],     # hand off to the specialist
                   model=ScriptedModel([[function_call("transfer_to_t", {}, call_id="h")]]))
    cfg = RunConfig(nest_handoff_history=nest) if nest is not None else None  # only set when testing True/False
    Runner.run_sync(triage, "hello there", run_config=cfg)  # run once
    received = specialist_model.first_call.input         # items the specialist model actually saw
    print(nest, "->", json.dumps(received, default=str)[:260])  # first 260 chars is enough to compare
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Routing mechanism | Conditional edges / `Command(goto=...)` | Manager agent delegation | Handoff = tool `transfer_to_<name>` | `Swarm` handoffs, selector in group chats |
| Who decides | Your router function or the LLM | Manager LLM | The current agent's LLM | Selector / agent message |
| Control after transfer | You define edges | Returns to delegator | Specialist owns the conversation | Depends on team type |
| Shared history | Shared state | Task context | Full items by default, optional nesting | Shared team message thread |
| Cycle guard | `recursion_limit` | `max_iter` | `max_turns` | Termination conditions |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Giving every agent handoffs to every other agent (a full mesh).
✅ Correct: Use a hub-and-spoke: triage to specialists, specialists answer or return via a defined path; cap with `max_turns`.

❌ Mistake 2: Vague agent names and no `handoff_description`.
✅ Correct: Clear names and a one-line `handoff_description` such as "Customs duty and HS codes": this is what the routing model reads.

❌ Mistake 3: Using a handoff when you need the answer back.
✅ Correct: Use `agent.as_tool()` (the sub-agent returns text to the caller) or run agents in code.

❌ Mistake 4: Assuming the specialist stays active on the next request.
✅ Correct: Store `result.last_agent` (by name) per conversation and start the next run there, or always start at triage.

❌ Mistake 5: Not handling `ModelBehaviorError` / `MaxTurnsExceeded`.
✅ Correct: Map them to 502/504 as in the advanced example.

---

## 🧠 Tricky Interview Question
Users complain: after getting a tariff answer, their follow-up "and for kids sizes?" is sent to the Billing Agent. Why?

**Answer:** Each `Runner.run` starts at the agent you pass. If every request starts at triage, triage must re-route the follow-up with no hint of the previous specialist; with a vague follow-up the routing model can guess wrong. Fixes: (1) persist `result.last_agent.name` per conversation and start there (and give specialists a way to hand back to triage), (2) keep session history so triage sees the earlier turns, (3) sharpen `handoff_description`s, (4) add an eval set of ambiguous follow-ups and track routing accuracy.

---

## ⚫ Interview Questions + Answers

**Q1:** How does the model see a handoff?

**A1:** As a tool named `transfer_to_<agent_name>` (for example `transfer_to_tariff_agent`) with no arguments by default.

**Q2:** What does the specialist receive by default?

**A2:** In 0.24.0 the prior items (user message, handoff call, handoff output). `RunConfig(nest_handoff_history=True)` summarises that into one message.

**Q3:** Handoff versus agent-as-tool?

**A3:** Handoff transfers control; the specialist answers the user and the run ends with `last_agent` = specialist. Agent-as-tool keeps the caller in control: the sub-agent's output returns as a tool result and the caller continues.

**Q4:** How do you stop agents bouncing the user between each other?

**A4:** `max_turns`, hub-and-spoke topology, clear `handoff_description`s, and tests with ambiguous inputs. Catch `MaxTurnsExceeded`.

**Q5:** Design a support system with 5 specialists.

**A5:** Triage agent with `handoffs` to 5 specialists (short prompts, 2 to 4 tools each), input guardrail on triage, output guardrail on specialists, session per conversation, sticky `last_agent`, trace `group_id` per conversation, metrics for routing distribution, handoff count per run, fallback to a human on repeated failures.

---

## 💰 Cost Impact
A handoff adds at least one extra model call (the triage call that returns the handoff) plus the specialist's calls. Each later call carries the history. Approximate, from public pricing at time of writing, verify: triage can use a small, cheap model because it only routes; specialists with short prompts and few tool schemas cost less per call than one mega-agent.

**Tips:** cheap model for triage, `nest_handoff_history=True` to shrink history, short specialist prompts, avoid mesh topologies, measure tokens per run with `usage`.

---

## 🔷 When to Use
✅ Use when:
- Distinct domains need distinct prompts/tools (tariff, billing, tech)
- You want the specialist to own the rest of the conversation
- A single agent has too many tools

❌ Avoid when:
- You need the sub-agent's result back to combine with others (use `as_tool`)
- The routing is deterministic (an `if` in Python is cheaper and more reliable)

---

## 📊 Visual Diagram
```
 user --> Runner.run(triage)
            |
      Triage Agent  (tools: transfer_to_tariff_agent, transfer_to_billing_agent)
            |  model calls transfer_to_tariff_agent
            v
   HandoffCallItem + HandoffOutputItem   (current agent := Tariff Agent)
            |
      Tariff Agent (own instructions, get_tariff_rate, own model)
            |  tool -> answer
            v
   final_output, last_agent = Tariff Agent
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| handoff | Transfer of the conversation to another agent | बातचीत दूसरे agent को सौंपना |
| triage agent | Agent that only routes | सिर्फ routing करने वाला agent |
| handoff_description | One-line hint for when to pick this agent | कब चुनना है इसका संकेत |
| last_agent | Agent that produced the final answer | आखिरी जवाब देने वाला agent |
| nest_handoff_history | Collapse previous items into one summary message | पिछला history एक संदेश में समेटना |
| hub-and-spoke | One router, many specialists | एक router, कई specialists |

---

## ⚡ 3-Line Summary
English: A handoff is a `transfer_to_<name>` tool that switches the current agent inside one run.
The specialist owns the conversation; use `as_tool` if you need the answer back.
Guard with `max_turns`, clear descriptions and hub-and-spoke design.

Hindi: Handoff एक `transfer_to_<name>` tool है जो एक ही run में current agent बदल देता है।
Specialist बातचीत संभालता है; जवाब वापस चाहिए तो `as_tool` इस्तेमाल करें।
`max_turns`, साफ descriptions और hub-and-spoke design से सुरक्षित रखें।

---

## ➡️ Next Topic
**#38 Handoff to Agent** - the simplest form in detail: passing agents directly in `handoffs=[...]`, the generated tool names and descriptions, and testing the routing.

---
