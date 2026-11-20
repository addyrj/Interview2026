---

# 32. SDK vs LangGraph vs CrewAI
# हिंदी में: OpenAI Agents SDK बनाम LangGraph बनाम CrewAI
# Framework: All
# Already Known: No

---

> Verified against openai-agents 0.24.0, langgraph 1.2.22, langchain-core 1.8.0 (Python 3.13, fastapi 0.163.0). Both code examples were run offline (scripted model for the SDK, plain nodes for LangGraph). CrewAI and AutoGen were NOT installed for this note: statements about them are conceptual and marked "not run - verify against current docs".

---

## 🔵 Simple Definition (2-3 lines)
These three frameworks answer "how do I structure an agent app?" differently. The OpenAI Agents SDK gives you a loop with handoffs (small API). LangGraph makes you draw an explicit graph with shared state and checkpoints (maximum control). CrewAI models a team of role-playing agents working on tasks (fast to prototype pipelines).

## 🔵 सरल परिभाषा (Hindi)
ये तीनों frameworks "agent app का ढाँचा कैसे बनाएँ?" का अलग-अलग जवाब देते हैं। OpenAI Agents SDK handoffs वाला loop देता है (छोटा API)। LangGraph आपसे साफ़ graph, shared state और checkpoints बनवाता है (सबसे ज़्यादा control)। CrewAI role वाले agents की team और tasks का मॉडल देता है (pipeline जल्दी prototype करने के लिए)।

---

## 🔴 Problem it Solves
Teams pick a framework by hype, then discover mid-project that it does not fit: no durable state when they need pause/resume, too much ceremony for a simple tool agent, or an opaque "crew" they cannot debug. A clear decision rule avoids a rewrite.

## 🔴 यह क्यों बना? (Hindi)
Teams hype देखकर framework चुनती हैं, फिर बीच project में पता चलता है कि वह फिट नहीं: pause/resume चाहिए तो durable state नहीं, simple tool agent के लिए बहुत ceremony, या ऐसी "crew" जिसे debug नहीं किया जा सकता। साफ़ निर्णय-नियम rewrite से बचाता है।

---

## 🟢 How it Works

```
Decision walk-through
Step 1 -> Does the flow need durable state, pause/resume, human edits to state?
          YES -> LangGraph (checkpointer + interrupts)
Step 2 -> Is it "one assistant + a few specialists + tools"?
          YES -> OpenAI Agents SDK (agents + handoffs + guardrails)
Step 3 -> Is it a fixed pipeline of role-based steps (researcher -> writer -> editor)?
          YES -> CrewAI (agents + tasks + crew)   [not run - verify]
Step 4 -> Open-ended multi-agent conversation / group chat?
          YES -> AutoGen teams                      [not run - verify]
Step 5 -> Unsure -> build the SAME task in two, run a fixed eval set, compare
          accuracy, latency, tokens, lines of code, debuggability
```

## 🟢 कैसे काम करता है? (Hindi)

```
निर्णय की प्रक्रिया
Step 1 -> क्या durable state, pause/resume, state में human edit चाहिए?
          हाँ -> LangGraph (checkpointer + interrupts)
Step 2 -> क्या "एक assistant + कुछ specialists + tools" है?
          हाँ -> OpenAI Agents SDK (agents + handoffs + guardrails)
Step 3 -> क्या role-based steps की तय pipeline है (researcher -> writer -> editor)?
          हाँ -> CrewAI (agents + tasks + crew)   [चलाया नहीं - docs से जाँचें]
Step 4 -> क्या खुली multi-agent बातचीत / group chat है?
          हाँ -> AutoGen teams                    [चलाया नहीं - docs से जाँचें]
Step 5 -> तय नहीं -> वही task दो में बनाएँ, fixed eval set चलाएँ, accuracy,
          latency, tokens, code की लाइनें और debuggability की तुलना करें
```

**What we verified (not opinion):** the same Tariff task below is about 20 lines in the SDK (one tool, one agent) and about 25 lines in LangGraph (state schema, two nodes, three edges, checkpointer). LangGraph gave us `get_state(config).values` after the run, which is the checkpoint; the SDK result gives `new_items`, `raw_responses` and `to_input_list()` instead. LangGraph's extra lines buy durability and explicit control, the SDK's fewer lines buy speed of writing.

**Mixing is legal:** an SDK agent can be wrapped as a LangGraph node (just call `Runner.run` inside a node), so you can keep LangGraph for orchestration and use the SDK for a tool-agent step. Test it before promising it.

---

## 🟡 Real World Example
**Tariff Agent.** Version A (SDK): one agent with a rate-lookup tool and a Billing Agent handoff, deployed behind FastAPI in a day. Version B (LangGraph): the customs workflow "classify goods -> look up duty -> human review -> file declaration" needs a pause for a human officer, possibly for days, so state is checkpointed to a database and resumed by thread id. Version C (CrewAI): "researcher gathers regulations, analyst drafts summary, editor polishes" as a nightly report job.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Version A (SDK): एक agent जिसमें rate-lookup tool और Billing Agent का handoff है, FastAPI के पीछे एक दिन में deploy। Version B (LangGraph): customs workflow "सामान classify -> duty खोजो -> human review -> declaration दाखिल" में human officer के लिए रुकना पड़ता है, शायद दिनों तक, इसलिए state database में checkpoint होती है और thread id से resume। Version C (CrewAI): "researcher नियम जुटाए, analyst सारांश लिखे, editor सुधारे" रात का report job।

---

## 💻 Code Example — Basic
The same Tariff lookup in the SDK and in LangGraph, side by side. Runs offline.

```python
# Basic: same task, two frameworks (runs offline)
from typing import TypedDict                             # LangGraph state schema
from agents import Agent, Runner, function_tool, set_tracing_disabled  # OpenAI Agents SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # offline fake LLM
from langgraph.graph import StateGraph, START, END       # LangGraph graph builder
from langgraph.checkpoint.memory import InMemorySaver    # in-memory checkpointer

set_tracing_disabled(True)                               # no key -> skip trace export
RATES: dict[str, str] = {"6109": "12%"}                  # shared fake tariff table

# ---------- A) OpenAI Agents SDK ----------
@function_tool                                           # expose function as an LLM tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return RATES.get(hs_code, "unknown")

sdk_model = ScriptedModel([                              # stands in for the real LLM
    [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
    [assistant_message("Duty is 12%.")],
])
sdk_agent = Agent(name="Tariff", instructions="Be brief.", tools=[get_tariff_rate], model=sdk_model)
sdk_result = Runner.run_sync(sdk_agent, "Duty for 6109?")  # the SDK owns the loop
print("SDK       :", sdk_result.final_output)

# ---------- B) LangGraph ----------
class State(TypedDict):                                  # explicit shared state schema
    hs_code: str
    rate: str
    answer: str

def lookup(s: State) -> dict[str, str]:                  # node 1: returns a partial state update
    return {"rate": RATES.get(s["hs_code"], "unknown")}

def answer(s: State) -> dict[str, str]:                  # node 2: builds the answer from state
    return {"answer": f"Duty is {s['rate']}."}

builder = StateGraph(State)                              # start building the graph
builder.add_node("lookup", lookup)                       # register node 1
builder.add_node("answer", answer)                       # register node 2
builder.add_edge(START, "lookup")                        # explicit edges: YOU define the flow
builder.add_edge("lookup", "answer")
builder.add_edge("answer", END)
graph = builder.compile(checkpointer=InMemorySaver())    # checkpointer = durable state
cfg = {"configurable": {"thread_id": "t1"}}              # thread id = which saved conversation
out = graph.invoke({"hs_code": "6109"}, cfg)             # run the graph
print("LangGraph :", out["answer"])
print("checkpoint:", graph.get_state(cfg).values["rate"])  # state is queryable after the run
```

## 💻 Code Example — Advanced
One FastAPI service exposing both implementations behind `/sdk` and `/graph`, async, typed, with error handling. Runs offline via `TestClient`. Not run here: real model calls (need a key) and CrewAI (not installed).

```python
# Advanced: FastAPI exposing SDK and LangGraph versions of the Tariff Agent (offline)
from typing import TypedDict                             # state schema
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # request/response schemas
from agents import (Agent, Runner, function_tool, set_tracing_disabled,
                    MaxTurnsExceeded)                    # SDK parts
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model
from langgraph.graph import StateGraph, START, END       # LangGraph
from langgraph.checkpoint.memory import InMemorySaver    # checkpointer

set_tracing_disabled(True)                               # skip trace export (no key)
RATES: dict[str, str] = {"6109": "12%"}                  # fake data source

class Ask(BaseModel):                                    # request
    hs_code: str
    thread_id: str = "default"

class Reply(BaseModel):                                  # response
    answer: str
    engine: str                                          # which framework answered

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return RATES.get(hs_code, "unknown")

class State(TypedDict):
    hs_code: str
    rate: str
    answer: str

def build_graph():                                       # compile once at startup
    g = StateGraph(State)
    g.add_node("lookup", lambda s: {"rate": RATES.get(s["hs_code"], "unknown")})
    g.add_node("answer", lambda s: {"answer": f"Duty is {s['rate']}."})
    g.add_edge(START, "lookup"); g.add_edge("lookup", "answer"); g.add_edge("answer", END)
    return g.compile(checkpointer=InMemorySaver())       # production: Postgres/Redis saver

def build_sdk_agent() -> Agent:                          # scripted model replaces the LLM here
    model = ScriptedModel([
        [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
        [assistant_message("Duty is 12%.")],
    ])
    return Agent(name="Tariff", instructions="Be brief.", tools=[get_tariff_rate], model=model)

def create_app() -> FastAPI:
    app = FastAPI()
    graph = build_graph()                                # reused across requests

    @app.post("/sdk", response_model=Reply)              # SDK route
    async def sdk(body: Ask) -> Reply:
        try:
            r = await Runner.run(build_sdk_agent(), f"Duty for {body.hs_code}?", max_turns=4)
        except MaxTurnsExceeded:                         # loop guard
            raise HTTPException(504, "max turns exceeded")
        return Reply(answer=str(r.final_output), engine="openai-agents-sdk")

    @app.post("/graph", response_model=Reply)            # LangGraph route
    async def graph_route(body: Ask) -> Reply:
        cfg = {"configurable": {"thread_id": body.thread_id}}  # per-conversation state
        out = await graph.ainvoke({"hs_code": body.hs_code}, cfg)  # async invoke
        return Reply(answer=out["answer"], engine="langgraph")

    return app

if __name__ == "__main__":
    c = TestClient(create_app())                         # no uvicorn needed
    print(c.post("/sdk", json={"hs_code": "6109"}).json())
    print(c.post("/graph", json={"hs_code": "6109", "thread_id": "u1"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Mental model | State machine / graph | Team of role agents + tasks | Agent loop + handoffs | Conversing agents in teams |
| State and persistence | Checkpointers, thread ids, time travel (verified: `get_state`) | Memory features (not run - verify) | Item history, `Session` (no graph state) | Team state save/load (not run - verify) |
| Human-in-the-loop | First-class interrupts | Human input on tasks (verify) | Tool approvals, guardrails | UserProxy / handoff to user (verify) |
| Learning curve | Steeper | Gentle | Gentlest | Medium |
| Control over flow | Maximum, explicit | Process types | You write Python around it | Team type decides |
| Tracing | LangSmith | Integrations | Built-in | OpenTelemetry/logging |
| Lock-in | LangChain ecosystem | CrewAI conventions | Light, OpenAI-friendly defaults | Microsoft ecosystem |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Choosing a framework from a blog's feature table without building a spike.
✅ Correct: Build the same 1-day spike in two frameworks and compare on your own eval set.

❌ Mistake 2: Using LangGraph for a 3-step tool agent, or the SDK for a multi-day approval workflow.
✅ Correct: Match the tool to the shape: durable long flows -> LangGraph; small assistants -> SDK.

❌ Mistake 3: Claiming "CrewAI is slower/faster" without numbers.
✅ Correct: Measure latency and tokens on your workload; never quote a number you did not measure.

❌ Mistake 4: Locking business logic inside framework-specific classes.
✅ Correct: Keep tools and domain logic as plain functions; the framework only wires them.

---

## 🧠 Tricky Interview Question
"Why not just use one framework for everything?"

**Answer:** Because their sweet spots differ and mixing is cheap if you keep seams clean. Domain logic lives in plain functions (rate lookup, validation). A LangGraph node can call `Runner.run` of an SDK agent when one step is a tool-using specialist, and an SDK agent can expose a graph as a tool. The cost of mixing is two sets of observability and two mental models, so only mix where the benefit is clear: for example durable approval workflow in LangGraph (state, interrupts) with SDK agents as steps. If the team is small and the flow is simple, standardising on one framework is the better call.

---

## ⚫ Interview Questions + Answers

**Q1:** One-line difference between the SDK and LangGraph?

**A1:** The SDK gives you an agent loop with handoffs; LangGraph gives you an explicit state graph with checkpoints.

**Q2:** When would you refuse to use the SDK?

**A2:** When I need durable pause/resume across days, deterministic branching I can unit-test node by node, or time-travel debugging.

**Q3:** How do you compare frameworks fairly?

**A3:** Same task, same model, same eval set; measure accuracy, p50/p95 latency, tokens per run, lines of code and time to debug a failure.

**Q4:** Can you use an SDK agent inside LangGraph?

**A4:** Yes: call `await Runner.run(agent, ...)` inside an async node and write `final_output` into state. Watch for double tracing and state duplication.

**Q5:** Design a framework choice for a customs platform with chat, approvals and nightly reports.

**A5:** Chat assistant: SDK (triage + tariff + billing agents). Approval workflow: LangGraph with Postgres checkpointer and interrupts. Nightly report: a simple sequential pipeline (CrewAI or plain LangGraph). Shared tools as plain functions, one eval set, one gateway for models.

---

## 💰 Cost Impact
**Formula (approximate):** tokens depend on prompts and history more than on the framework. Frameworks differ in hidden overhead: handoff instructions, tool schemas, role/backstory prompts, and the number of model calls per task.

Typical ranges (approximate, from public pricing at time of writing, verify): do not trust published benchmark numbers; count `usage.total_tokens` per task for each candidate. **Tips:** disable verbose role prompts you do not need, keep tool schemas small, cache identical lookups, and compare cost per successful task, not cost per call.

---

## 🔷 When to Use
✅ Use the SDK when:
- Few agents, few tools, fast delivery, built-in tracing wanted

✅ Use LangGraph when:
- Durable state, human approval pauses, complex branching/loops

✅ Use CrewAI when:
- Role-based sequential pipelines you want to prototype quickly (verify fit)

❌ Avoid when:
- Picking any framework without a spike and an eval set

---

## 📊 Visual Diagram
```
                 +--------------------------+
                 |  What is the task shape? |
                 +------------+-------------+
        durable/branching      |        assistant + specialists
        approvals, days   +----+----+         tools, quick ship
              +-----------+         +-----------+
              v                                  v
        +-----------+                   +----------------+
        | LangGraph |                   | OpenAI Agents  |
        | state+ckpt|                   | SDK + handoffs |
        +-----------+                   +----------------+
              \  fixed role pipeline / group chat  /
               +--> CrewAI / AutoGen (not run - verify)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StateGraph | LangGraph builder for nodes, edges, state | LangGraph का graph builder |
| Checkpointer | Saves graph state per thread | state सहेजने वाला |
| Handoff | SDK mechanism to delegate to another agent | दूसरे agent को सौंपना |
| Crew | CrewAI team of agents and tasks | CrewAI की agents की टीम |
| Spike | Short experiment to compare options | छोटा प्रयोग तुलना के लिए |
| Eval set | Fixed test questions with expected outcomes | तय परीक्षा-प्रश्नों का सेट |

---

## ⚡ 3-Line Summary
English: SDK = small loop with handoffs, LangGraph = explicit durable graph, CrewAI = role-based crews.
Choose by task shape (durability, branching, pipeline), not by popularity.
Prove the choice with a same-task spike and a fixed eval set.

Hindi: SDK = handoffs वाला छोटा loop, LangGraph = साफ़ durable graph, CrewAI = role वाली crews।
चुनाव task के आकार (durability, branching, pipeline) से करें, लोकप्रियता से नहीं।
वही task दो में बनाकर और fixed eval set चलाकर चुनाव सिद्ध करें।

---

## ➡️ Next Topic
**#33 Installing + Setup** - before writing real agents we set up a clean environment: package name, Python version, API key handling and verifying the install.

---
