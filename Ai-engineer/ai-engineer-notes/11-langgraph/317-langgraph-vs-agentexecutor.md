---

# 317. LangGraph vs AgentExecutor
# हिंदी में: LangGraph बनाम AgentExecutor

---

## 🔵 Simple Definition (English)
`AgentExecutor` is LangChain's older, built-in agent loop: call the model, run tools, repeat. It is a black box with a few settings. LangGraph exposes that same loop as a **graph you control**: you see and edit every node, edge and state key. LangChain now recommends LangGraph (for example `create_react_agent`) for new agents.

## 🔵 सरल परिभाषा (Hindi)
`AgentExecutor` LangChain का पुराना built-in agent loop है: model call करो, tools चलाओ, दोहराओ। यह black box है और इसकी settings कम हैं। LangGraph वही loop **graph** के रूप में देता है जिसे आप control करते हैं: हर node, edge और state key दिखती और बदली जा सकती है। नए agents के लिए LangChain अब LangGraph (जैसे `create_react_agent`) की सलाह देता है।

---

## 🔴 Problem it Solves
AgentExecutor made simple agents easy, but when you needed a custom step (approval, validation, a forced tool order, parallel work, saving progress) you had to hack callbacks or subclass. It could not pause and resume, had little state beyond the scratchpad, and its flow was hidden. LangGraph fixes this with explicit control flow and persistence.

## 🔴 यह क्यों बना? (Hindi)
AgentExecutor से सरल agents आसान थे, पर custom step (approval, validation, tools का तय क्रम, parallel काम, progress save) चाहिए तो callbacks hack करने या subclass बनाने पड़ते थे। यह pause/resume नहीं कर सकता था, state सीमित थी और flow छिपा था। LangGraph स्पष्ट control flow और persistence देकर यह हल करता है।

---

## 🟢 How it Works — Step by Step

```
AgentExecutor:
 Step 1 → agent = create_tool_calling_agent(llm, tools, prompt)
 Step 2 → AgentExecutor(agent, tools, max_iterations, handle_parsing_errors)
 Step 3 → Loop inside (hidden): LLM → tool → LLM ... until finish
 Step 4 → Output: {"output": ...}; intermediate_steps if requested

LangGraph:
 Step 1 → State has messages (with add_messages reducer)
 Step 2 → Node "agent" calls LLM with tools; node "tools" runs tool calls
 Step 3 → Conditional edge: tool_calls present → "tools", else END
 Step 4 → Edge "tools" → "agent" (the loop is visible)
 Step 5 → You may add nodes anywhere (validate, approve, summarise)
 Step 6 → compile(checkpointer) → pause, resume, stream, time travel
```

## 🟢 कैसे काम करता है? (Hindi)

```
AgentExecutor:
 Step 1 → create_tool_calling_agent(llm, tools, prompt)
 Step 2 → AgentExecutor(agent, tools, max_iterations, ...)
 Step 3 → अंदर (छिपा) loop: LLM → tool → LLM ... finish तक
 Step 4 → Output: {"output": ...}

LangGraph:
 Step 1 → State में messages (add_messages reducer के साथ)
 Step 2 → "agent" node LLM चलाता है, "tools" node tool calls चलाता है
 Step 3 → Conditional edge: tool_calls हों तो "tools", वरना END
 Step 4 → "tools" → "agent" edge (loop दिखता है)
 Step 5 → कहीं भी नए nodes जोड़ो (validate, approve, summarise)
 Step 6 → compile(checkpointer) → pause, resume, stream
```

---

## 🟡 Real World Example
**Tariff Classification System**: With AgentExecutor the team had `search_hs_code`, `get_duty_rate`. Then compliance demanded: "validate the HS code format before any duty lookup, and a human must approve if confidence < 0.8". In AgentExecutor this meant hacking inside tools. In LangGraph they added a `validate` node and an `approve` node, with a conditional edge. No hack needed.

**Amazon-style**: a support agent that must always run a fraud check before refunds.

## 🟡 Real Example Hindi mein
**Tariff System**: AgentExecutor में `search_hs_code`, `get_duty_rate` थे। फिर compliance ने कहा: "duty lookup से पहले HS code format validate हो, और confidence < 0.8 पर इंसान approve करे।" AgentExecutor में tools के अंदर hack करना पड़ता। LangGraph में `validate` और `approve` nodes plus conditional edge जोड़ दिए।
**Amazon**: refund से पहले हमेशा fraud check चलाने वाला support agent।

---

## 💻 Code Example — Basic
```python
# Basic: the SAME agent loop written by hand as a graph (fake LLM, offline).
# pip install langgraph
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages          # reducer: append messages

class State(TypedDict):
    messages: Annotated[list[dict], add_messages]         # add_messages merges new messages

def fake_llm(messages: list[dict]) -> dict:               # stands in for the model
    if not any(m.get("role") == "tool" for m in messages):
        return {"role": "assistant", "content": "", "tool_calls": [{"name": "lookup", "args": {"p": "speaker"}}]}
    return {"role": "assistant", "content": "HS code is 8518.22"}

def agent(state: State) -> dict:                          # node: think
    return {"messages": [fake_llm(state["messages"])]}

def tools(state: State) -> dict:                          # node: act
    call = state["messages"][-1]["tool_calls"][0]         # last assistant message has the call
    return {"messages": [{"role": "tool", "content": "8518.22"}]}

def should_continue(state: State) -> str:                 # router (the old "is finished?" check)
    return "tools" if state["messages"][-1].get("tool_calls") else END

g = StateGraph(State)
g.add_node("agent", agent); g.add_node("tools", tools)
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue)
g.add_edge("tools", "agent")                              # the loop, now visible
app = g.compile()

if __name__ == "__main__":
    out = app.invoke({"messages": [{"role": "user", "content": "HS code for speaker?"}]})
    print(out["messages"][-1].content)
```

## 💻 Code Example — Advanced
```python
# Migration: AgentExecutor (old) vs create_react_agent (new) + extra validation node.
import asyncio
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

@tool
def get_duty_rate(hs_code: str, country: str) -> str:
    """Return the import duty percent for an HS code and ISO country code."""
    return "12.5%"

TOOLS = [get_duty_rate]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(TOOLS)   # model that can request tools

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

async def agent_node(state: State) -> dict:
    try:
        return {"messages": [await llm.ainvoke(state["messages"])]}
    except Exception as exc:                                  # surface failure as a message
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content=f"LLM error: {exc}")]}

async def guard_node(state: State) -> dict:
    # Custom step impossible in plain AgentExecutor: inspect tool calls BEFORE they run.
    last = state["messages"][-1]
    bad = [c for c in getattr(last, "tool_calls", []) if c["name"] == "get_duty_rate"
           and len(str(c["args"].get("hs_code", ""))) != 7]
    if bad:
        return {"messages": [ToolMessage(content="Invalid hs_code format, expected NNNN.NN",
                                         tool_call_id=bad[0]["id"])]}
    return {}

def route(state: State) -> str:
    last = state["messages"][-1]
    if isinstance(last, ToolMessage):                          # guard rejected -> let model retry
        return "agent"
    return "tools" if getattr(last, "tool_calls", None) else END

g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("guard", guard_node)
g.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", lambda s: "guard" if getattr(s["messages"][-1], "tool_calls", None) else END)
g.add_conditional_edges("guard", route)
g.add_edge("tools", "agent")
app = g.compile(checkpointer=MemorySaver())

# OLD way, for comparison (deprecated style):
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# executor = AgentExecutor(agent=create_tool_calling_agent(llm, TOOLS, prompt), tools=TOOLS, max_iterations=6)
# NEW shortcut: from langgraph.prebuilt import create_react_agent; agent = create_react_agent(llm_without_bind, TOOLS)

async def main() -> None:
    cfg = {"configurable": {"thread_id": "t1"}, "recursion_limit": 12}
    out = await app.ainvoke({"messages": [("user", "Duty for 8518.22 from CN?")]}, cfg)
    print(out["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

api = FastAPI()

class Q(BaseModel):
    question: str
    thread_id: str

@api.post("/agent")
async def run_agent(q: Q) -> dict:
    cfg = {"configurable": {"thread_id": q.thread_id}, "recursion_limit": 12}
    out = await app.ainvoke({"messages": [("user", q.question)]}, cfg)   # graph from Advanced
    return {"answer": out["messages"][-1].content}

# With AgentExecutor the equivalent was: await executor.ainvoke({"input": q.question})
# and you had to pass chat_history yourself. LangGraph keeps it per thread_id.
```

---

## 🔗 LangChain / LangGraph Connection
The migration is mostly mechanical:

| AgentExecutor | LangGraph |
|---|---|
| `max_iterations=6` | `recursion_limit` in config |
| `handle_parsing_errors=True` | `ToolNode(handle_tool_errors=True)` |
| `chat_history` input | `checkpointer` + `thread_id` |
| `agent_scratchpad` | `messages` in state |
| `return_intermediate_steps` | `stream_mode="updates"` or read `messages` |
| callbacks hacks | extra nodes / interrupts |

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Starting new projects on AgentExecutor.
✅ Correct: use `create_react_agent` or a custom StateGraph.

```python
# Wrong (legacy)
executor = AgentExecutor(agent=agent, tools=tools)
# Right
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)
```

❌ Mistake 2: Mapping `max_iterations` to a node counter that is never checked.
✅ Correct: use `recursion_limit` (counts supersteps, roughly 2 per tool round) and catch `GraphRecursionError`.

❌ Mistake 3: Forgetting the `add_messages` reducer, so new messages overwrite old ones.
✅ Correct: `Annotated[list[AnyMessage], add_messages]`.

---

## 🧠 Tricky Interview Question
**Q**: "You set `recursion_limit=6` in LangGraph and your agent with 3 tool rounds fails with GraphRecursionError. Why, since AgentExecutor with `max_iterations=6` worked?"

**Answer**: `recursion_limit` counts graph **steps** (supersteps), not agent iterations. One tool round = `agent` step + `tools` step, plus the final agent step. 3 rounds need about 7+ steps. Set it higher (about 2 x desired iterations + 1), and treat the error as a normal outcome to catch and handle.

---

## ⚫ Interview Questions + Answers

Q1: Why did LangChain move agents to LangGraph?
A1: Control, persistence and extensibility: explicit state and edges, checkpoints, human-in-the-loop, streaming and easier customisation.

Q2: What replaces `agent_scratchpad`?
A2: The `messages` list in state (AI messages with tool calls and tool messages).

Q3: Can I still use LangChain tools and models in LangGraph?
A3: Yes. Tools, prompts, retrievers and chat models are used inside nodes.

Q4: What does `tools_condition` do?
A4: A prebuilt router that returns `"tools"` if the last AI message has tool calls, otherwise `END`.

Q5: (Hard) How do you add approval before a specific tool only?
A5: Add a gate node between `agent` and `tools` that checks `tool_calls` names; for risky ones call `interrupt()`, resume with the human's decision, and either forward to `tools` or inject a rejection `ToolMessage`. With AgentExecutor you would wrap the tool itself, which is awkward and cannot pause.

---

## 🔷 When to Use + When Not to Use
✅ Use LangGraph when:
- You need custom steps, approval, persistence, streaming
- Building new agents or multi-agent systems

⚠️ AgentExecutor is acceptable only when:
- Maintaining legacy code until migration

---

## 📊 Visual Diagram
```
AgentExecutor (black box)          LangGraph (open box)
┌───────────────────────┐          START
│  LLM ⇄ tools loop     │            │
│  (you cannot touch)   │            ▼
└───────────────────────┘        ┌─agent─┐◄──────────┐
   input ─► output               └───┬───┘            │
                                     │tool_calls?      │
                                  guard/approve        │
                                     ▼                 │
                                  ┌tools┐──────────────┘
                                  └─────┘   no tool_calls → END
```

---

## 💰 Cost Impact
Both resend the whole message history on each loop, so token cost per loop is similar. LangGraph helps reduce cost because you can insert a trimming/summarising node, route easy cases without the LLM, add a guard that prevents wasted tool-retry loops, and stop at an exact step limit. Checkpointing allows resuming after failure without re-running earlier (already paid) steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AgentExecutor | Legacy LangChain agent loop | पुराना LangChain agent loop |
| create_react_agent | LangGraph prebuilt agent | LangGraph का तैयार agent |
| ToolNode | Node that executes tool calls | Tool calls चलाने वाला node |
| tools_condition | Router: tools or END | Tools या END चुनने वाला router |
| add_messages | Reducer that appends messages | Messages जोड़ने वाला reducer |
| scratchpad | Old name for intermediate steps | बीच के steps की जगह |

---

## ⚡ 3-Line Summary
English: AgentExecutor hides the agent loop; LangGraph exposes it as a graph you can customise, pause, persist and stream. Migrate with `create_react_agent` or a custom StateGraph. Map `max_iterations` to `recursion_limit`.
Hindi: AgentExecutor agent loop छिपाता है; LangGraph उसे graph बनाकर customise, pause, persist और stream करने देता है। `create_react_agent` या custom StateGraph से migrate करो। `max_iterations` की जगह `recursion_limit` इस्तेमाल करो।

---

## ➡️ Next Topic
**318. State Graph Concept** — how the StateGraph model (state, nodes, edges, reducers) works in detail.
