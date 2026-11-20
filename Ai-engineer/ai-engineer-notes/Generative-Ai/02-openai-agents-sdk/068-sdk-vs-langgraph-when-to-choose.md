---

# 68. SDK vs LangGraph — When to Choose
# हिंदी में: OpenAI Agents SDK बनाम LangGraph - कब क्या चुनें
# Framework: OpenAI SDK, LangGraph
# Already Known: No

---

> Verified against openai-agents 0.24.0, langgraph 1.2.22 (langgraph-checkpoint 4.3.2), fastapi 0.163.0 (Python 3.13.3). Both samples were run offline: the SDK half with a scripted model (`fake.py`, listing in note #57), the LangGraph half with plain Python nodes (no LLM at all). Real model calls were NOT run - they need OPENAI_API_KEY. This is a design comparison, so the verdicts are judgement, not benchmarks; no latency or cost numbers are claimed.

---

## 🔵 Simple Definition (2-3 lines)
The OpenAI Agents SDK is a small, model-driven toolkit: you declare agents, tools and handoffs, and the LLM decides the path at runtime. LangGraph is an explicit state machine: you draw nodes and edges, keep typed state and get checkpoints, interrupts and replay. Choose by how much control and durability the workflow needs.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Agents SDK एक छोटा, model-driven toolkit है: आप agents, tools और handoffs घोषित करते हैं और रास्ता LLM runtime पर तय करता है। LangGraph एक स्पष्ट state machine है: आप nodes और edges बनाते हैं, typed state रखते हैं और checkpoints, interrupts व replay पाते हैं। चुनाव इस पर निर्भर है कि workflow को कितना control और स्थायित्व चाहिए।

---

## 🔴 Problem it Solves
Teams pick a framework by hype, then hit a wall: a graph for a simple Q&A bot is boilerplate, while a plain agent loop cannot pause for a human approval and resume tomorrow. A clear decision rule avoids a rewrite after three months.

## 🔴 यह क्यों बना? (Hindi)
Teams hype देखकर framework चुनती हैं और फिर दीवार से टकराती हैं: साधारण Q&A bot के लिए graph बेवजह boilerplate है, जबकि सादा agent loop मानव approval के लिए रुककर कल दोबारा शुरू नहीं हो सकता। स्पष्ट निर्णय-नियम तीन महीने बाद rewrite से बचाता है।

---

## 🟢 How it Works

```
                      SDK                           LangGraph
Who picks the path?   LLM (handoff = tool call)     Your code (edges) or LLM inside a node
State                 run context + session items   Typed state (TypedDict/Pydantic) per step
Pause / resume        You build it                  interrupt() + checkpointer + thread_id
Loop control          max_turns                     recursion_limit, explicit cycles
Time travel / replay  traces for viewing            checkpoints can be re-run from a step
Boilerplate           low (a few objects)           higher (nodes, edges, state schema)
Best at               fast conversational agents    long-running, auditable workflows
```

## 🟢 कैसे काम करता है? (Hindi)

```
                      SDK                           LangGraph
रास्ता कौन चुने?       LLM (handoff = tool call)     आपका code (edges) या node में LLM
State                 run context + session items   हर step पर typed state
Pause / resume        आपको खुद बनाना है             interrupt() + checkpointer + thread_id
Loop नियंत्रण          max_turns                     recursion_limit, स्पष्ट cycles
Time travel / replay  traces सिर्फ़ देखने के लिए      checkpoints से किसी step से दोबारा चलाना
Boilerplate           कम (कुछ objects)               ज़्यादा (nodes, edges, state schema)
सबसे अच्छा            तेज़ conversational agents    लंबे, auditable workflows
```

**Observed outputs (verified):**
- Basic: `SDK      : Rates: 20%` and `LangGraph: Rates: 20%` - same routing job, different mechanism: the SDK router is a scripted *model* picking `transfer_to_rates`; the LangGraph router is an ordinary Python function `route(state)`.
- Advanced: `{'paused': True, 'ask': {'ask': 'Approve filing for duty=200.00?'}}` then `{'result': 'duty=200.00 filed'}` then `{'answer': 'done'}`. The graph paused at `interrupt()`, the state survived in the checkpointer (`MemorySaver`, in-memory; use a Postgres/SQLite saver in production) and resumed with `Command(resume=True)`.

**Is it either/or? No.** The SDK also has `needs_approval` on function tools (visible in the 0.24.0 `function_tool` signature) for human approval and a session store for history, so approval flows are possible; I did not run that path here. The difference is how much durable-workflow machinery comes built in versus built by you. You can also call an SDK agent from inside a LangGraph node.

**Hindi नोट:** इंटरव्यू में "कौन बेहतर?" का सही जवाब है "यह निर्भर करता है", पर तीन सवालों के साथ: (1) क्या रास्ता पहले से पता है? (2) क्या workflow घंटों/दिनों तक रुककर मानव का इंतज़ार करता है? (3) क्या हर step का audit और replay चाहिए? तीनों "हाँ" हों तो LangGraph; नहीं तो SDK से शुरू करें।

---

## 🟡 Real World Example
**Tariff Agent.** Version 1: a chat assistant that looks up duty rates and hands off to Legal - SDK, about 40 lines, shipped in a day. Version 2: a filing workflow (compute duty, wait for a customs officer to approve, file, notify) that may wait two days - LangGraph with a Postgres checkpointer, because the approval must survive deploys and restarts.

**Customer Support Agent:** the front-line chat is SDK handoffs; the refund approval pipeline behind it is a graph.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Version 1: duty rates खोजने और Legal को handoff करने वाला chat assistant - SDK, लगभग 40 पंक्तियाँ, एक दिन में shipped। Version 2: filing workflow (duty compute, customs officer की approval का इंतज़ार, filing, notification) जो दो दिन रुक सकता है - LangGraph और Postgres checkpointer, क्योंकि approval को deploys और restarts में बचे रहना है।

**Customer Support Agent:** front-line chat SDK handoffs है; उसके पीछे refund approval pipeline एक graph है।

---

## 💻 Code Example — Basic
The same routing job in both frameworks, offline.

```python
# Basic: the SAME routing job in the OpenAI Agents SDK and in LangGraph (both offline).
# verified against openai-agents 0.24.0 and langgraph 1.2.22
import asyncio
from typing import Literal, TypedDict
from agents import Agent, Runner, set_tracing_disabled
from langgraph.graph import END, START, StateGraph
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

# ---- SDK: the MODEL decides the route (handoff is a tool call) ----
legal = Agent(name="Legal", instructions="Legal answers.", model=ScriptedModel([[text("Legal: see Section 12")]]))
rates = Agent(name="Rates", instructions="Rate answers.", model=ScriptedModel([[text("Rates: 20%")]]))
triage = Agent(name="Triage", instructions="Route to Legal or Rates.", handoffs=[legal, rates],
               model=ScriptedModel([[tool_call("transfer_to_rates", "{}")]]))
print("SDK      :", asyncio.run(Runner.run(triage, "duty on shirts?")).final_output)

# ---- LangGraph: YOUR CODE decides the route (explicit edges) ----
class State(TypedDict):
    question: str
    answer: str

def route(state: State) -> Literal["legal", "rates"]:             # routing function = ordinary Python (an LLM could be called here)
    return "legal" if "ban" in state["question"] else "rates"

graph = StateGraph(State)
graph.add_node("legal", lambda s: {"answer": "Legal: see Section 12"})
graph.add_node("rates", lambda s: {"answer": "Rates: 20%"})
graph.add_conditional_edges(START, route)                         # explicit, inspectable branching
graph.add_edge("legal", END)
graph.add_edge("rates", END)
app = graph.compile()
print("LangGraph:", app.invoke({"question": "duty on shirts?", "answer": ""})["answer"])
```

## 💻 Code Example — Advanced
What LangGraph adds: a checkpointed workflow that pauses for approval and resumes later, exposed through FastAPI, next to a plain SDK endpoint.

```python
# Advanced: what LangGraph adds - checkpointed state + human approval (interrupt/resume) - vs a plain SDK run.
# verified against langgraph 1.2.22 + fastapi 0.163.0 (TestClient), openai-agents 0.24.0 for the SDK half
from typing import TypedDict
from fastapi import FastAPI
from langgraph.checkpoint.memory import MemorySaver               # swap for a Postgres/SQLite saver in production
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from agents import Agent, Runner, set_tracing_disabled
from fake import ScriptedModel, text

set_tracing_disabled(True)

class S(TypedDict):
    amount: float
    approved: bool
    result: str

def compute(s: S) -> dict:
    return {"result": f"duty={s['amount'] * 0.2:.2f}"}            # deterministic node (no LLM)

def approval(s: S) -> dict:
    ok = interrupt({"ask": f"Approve filing for {s['result']}?"})   # PAUSES the graph; state saved in the checkpointer
    return {"approved": bool(ok)}

def file_it(s: S) -> dict:
    return {"result": s["result"] + (" filed" if s["approved"] else " rejected")}

g = StateGraph(S)
for name, fn in [("compute", compute), ("approval", approval), ("file_it", file_it)]:
    g.add_node(name, fn)
g.add_edge(START, "compute"); g.add_edge("compute", "approval"); g.add_edge("approval", "file_it"); g.add_edge("file_it", END)
graph = g.compile(checkpointer=MemorySaver())

app = FastAPI()

@app.post("/lg/start/{thread}")
def start(thread: str, amount: float) -> dict:
    cfg = {"configurable": {"thread_id": thread}}                 # thread id = durable conversation key
    out = graph.invoke({"amount": amount, "approved": False, "result": ""}, cfg)
    return {"paused": "__interrupt__" in out, "ask": out["__interrupt__"][0].value if "__interrupt__" in out else None}

@app.post("/lg/resume/{thread}")
def resume(thread: str, approve: bool) -> dict:
    out = graph.invoke(Command(resume=approve), {"configurable": {"thread_id": thread}})   # continues where it stopped
    return {"result": out["result"]}

@app.post("/sdk")
async def sdk() -> dict:                                          # SDK: one request = one run; pause/resume is YOUR job
    res = await Runner.run(Agent(name="A", instructions="x", model=ScriptedModel([[text("done")]])), "go")
    return {"answer": res.final_output}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    c = TestClient(app)
    print(c.post("/lg/start/t1", params={"amount": 1000}).json())
    print(c.post("/lg/resume/t1", params={"approve": True}).json())
    print(c.post("/sdk").json())
```

Note `MemorySaver` loses state on restart; durability needs a persistent checkpointer (not run here).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Control style | Explicit graph (nodes/edges) | Roles + tasks (sequential/hierarchical) | Model-driven agents + handoffs | Conversational teams (round robin, selector, swarm) |
| Durable pause/resume | Built in (checkpointer, `interrupt`) | Limited | Build with sessions/approval | State save/load |
| Learning curve | Higher | Low-medium | Low | Medium |
| Best for | Auditable long workflows | Quick role-based pipelines | Fast single/multi-agent chat apps | Multi-agent conversations/research |

_OpenAI SDK and LangGraph columns verified in the installed versions above; CrewAI and AutoGen columns are from general knowledge (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Choosing LangGraph for a simple single-agent chatbot.
✅ Correct: Start with the SDK (or a plain loop); adopt a graph when you need checkpoints, branching you must audit, or long pauses.

❌ Mistake 2: Expecting an SDK run to survive a server restart.
✅ Correct: A run lives in process memory. Persist what you need (sessions, your own state) or use a checkpointed framework.

❌ Mistake 3: Using the LLM to route when the rule is deterministic ("amount > 10k -> manager").
✅ Correct: Put deterministic rules in code (graph edge or plain `if`); keep the LLM for fuzzy judgement.

❌ Mistake 4: Using `MemorySaver` in production.
✅ Correct: Use a database-backed checkpointer.

---

## 🧠 Tricky Interview Question
Your SDK-based support agent works, but compliance now requires: human approval before refunds above a threshold, a full audit of every step, and the ability to resume a conversation after a week. Do you rewrite in LangGraph?

**Answer:** Not necessarily. First list what is missing: approval (SDK tools support `needs_approval` - verify the interrupt/resume flow for your version), durable state (persist sessions in a database and store run state yourself), audit (hooks and tracing already give step records). If you would be hand-building a state machine, checkpointing and replay, that is the signal to move that workflow - not the whole app - to LangGraph, and keep the conversational front-end as an SDK agent calling the graph via an API or tool. Decide on the cost of ownership: building durable pause/resume yourself versus learning and adopting a graph.

---

## ⚫ Interview Questions + Answers

**Q1:** Who decides the next step in the SDK and in LangGraph?

**A1:** In the SDK the LLM decides (tool calls and handoffs). In LangGraph your edges decide, and a node may call an LLM to choose a branch.

**Q2:** What does LangGraph's checkpointer give you?

**A2:** Saved state per `thread_id` after each step, enabling pause/resume with `interrupt`, replay from earlier steps and recovery after restarts.

**Q3:** When is the SDK clearly the better pick?

**A3:** Fast chat-style agents with tools and handoffs, small teams, minimal boilerplate, tight OpenAI integration and built-in tracing.

**Q4:** Can you combine them?

**A4:** Yes. Call an SDK agent inside a LangGraph node, or expose a graph as a tool/API that an SDK agent calls.

**Q5:** System design: customs filing with a 2-day approval.

**A5:** LangGraph with a Postgres checkpointer: nodes compute -> validate -> `interrupt` for officer -> file -> notify. FastAPI start/resume endpoints keyed by `thread_id`, a webhook on approval, idempotent filing, audit via checkpoints, and an SDK agent for the user-facing Q&A.

---

## 💰 Cost Impact
Neither framework changes per-token price. Cost differences come from design: model-driven routing spends an extra LLM turn per handoff, while code-driven routing spends none. Graph checkpoints add storage and I/O, not tokens. Use deterministic edges for rules, small models for routing, and cap turns. Prices approximate, from public pricing at time of writing - verify.

---

## 🔷 When to Use
✅ Use SDK when:
- Conversational agent with tools and a few handoffs
- Speed of delivery and low boilerplate matter
- The path can be left to the model

✅ Use LangGraph when:
- Long-running workflows with human approval
- You need checkpoints, replay and audit per step
- Branching rules must be explicit and testable

❌ Avoid when:
- A graph for a one-tool bot, or an SDK loop for multi-day workflows

---

## 📊 Visual Diagram
```
 SDK                                   LangGraph
 ---                                   ---------
 user -> Triage(LLM)                   START -> route(state)  [python/LLM]
          | transfer_to_x                         |          |
          v                                       v          v
        Agent X -> answer                      legal       rates
                                                  \         /
 state: in-memory run                              END
 pause/resume: you build               compute -> approval --interrupt--> (wait)
                                            ^ checkpointer(thread_id) | Command(resume)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model-driven | LLM picks next step | LLM अगला कदम चुनता है |
| Checkpointer | Saves graph state per step | हर step पर state सहेजता है |
| interrupt | Pause for external input | बाहरी input के लिए रुकना |
| thread_id | Key of a durable conversation | durable बातचीत की key |
| Conditional edge | Branch chosen by a function | function द्वारा चुनी शाखा |
| Human-in-the-loop | Person approves a step | इंसान step को मंज़ूर करता है |

---

## ⚡ 3-Line Summary
English: SDK = small and model-driven; LangGraph = explicit graph with checkpoints and interrupts.
Choose by path predictability, need for durable pause/resume, and audit requirements.
They combine well: SDK for the chat front, LangGraph for the long workflow.

Hindi: SDK = छोटा और model-driven; LangGraph = checkpoints और interrupts वाला स्पष्ट graph।
रास्ते की अनुमेयता, durable pause/resume की ज़रूरत और audit आवश्यकताओं से चुनें।
दोनों साथ चलते हैं: chat front के लिए SDK, लंबे workflow के लिए LangGraph।

---

## ➡️ Next Topic
**#69 SDK Pricing + Cost** - turning `Usage` into money, per-request budgets and the levers that cut spend.

---
