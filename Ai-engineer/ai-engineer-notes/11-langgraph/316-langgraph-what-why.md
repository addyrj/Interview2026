---

# 316. LangGraph — What + Why
# हिंदी में: LangGraph — क्या है और क्यों

---

## 🔵 Simple Definition (English)
LangGraph is a library for building LLM applications as a **graph**: nodes (Python functions) that read and update a shared **state**, connected by edges (including conditional ones). It supports loops, branching, persistence (checkpoints), human approval and streaming. It is built by the LangChain team and works with or without LangChain.

## 🔵 सरल परिभाषा (Hindi)
LangGraph LLM applications को **graph** की तरह बनाने की library है: nodes (Python functions) जो साझा **state** पढ़ते और बदलते हैं, और edges (conditional भी) उन्हें जोड़ती हैं। इसमें loops, branching, persistence (checkpoints), human approval और streaming मिलते हैं। इसे LangChain team ने बनाया है और यह LangChain के साथ या बिना चल सकता है।

---

## 🔴 Problem it Solves
Simple chains run in a straight line (A then B then C). Real agents need loops ("try again until valid"), branches ("if low confidence, ask a human"), memory across turns, and the ability to pause and resume. Hand-written `while` loops get messy and cannot be saved, resumed or visualised. LangGraph makes control flow explicit and durable.

## 🔴 यह क्यों बना? (Hindi)
सरल chains सीधी रेखा में चलती हैं (A फिर B फिर C)। असली agents को loops ("valid होने तक दोबारा कोशिश"), branches ("कम confidence पर इंसान से पूछो"), बातचीत के बीच memory, और रुकने-चालू होने की क्षमता चाहिए। हाथ से लिखे `while` loops उलझ जाते हैं और save/resume/visualise नहीं हो सकते। LangGraph control flow को स्पष्ट और टिकाऊ बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a State schema (TypedDict / pydantic)
Step 2 → Write nodes: functions (state) -> partial state update
Step 3 → Create StateGraph(State) and add_node(name, fn)
Step 4 → Connect: add_edge(A, B) and add_conditional_edges(A, router)
Step 5 → Set start (START) and end (END)
Step 6 → compile(checkpointer=...) -> runnable app
Step 7 → invoke / stream with config {"configurable": {"thread_id": ...}}
Step 8 → Engine runs node → merges update into state → picks next node → repeat
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State schema बनाओ (TypedDict / pydantic)
Step 2 → Nodes लिखो: functions (state) -> आंशिक state update
Step 3 → StateGraph(State) बनाओ और add_node करो
Step 4 → add_edge और add_conditional_edges से जोड़ो
Step 5 → START और END तय करो
Step 6 → compile(checkpointer=...) से runnable app मिलता है
Step 7 → thread_id वाले config के साथ invoke / stream करो
Step 8 → Engine node चलाता है → update state में merge → अगला node चुनता है → दोहराता है
```

---

## 🟡 Real World Example
**Tariff Classification System** as a graph: `retrieve` (find tariff chunks) → `classify` (LLM proposes HS code) → `validate` (format and rule checks). If invalid, loop back to `classify` with the error (max 3 times). If confidence is low, go to `human_review`. Otherwise go to `duty_lookup` and END. The state carries product, chunks, code, confidence, attempts.

**Zomato-style**: understand request → search → if no results, relax filters and search again → confirm → order.

## 🟡 Real Example Hindi mein
**Tariff System** graph के रूप में: `retrieve` → `classify` (LLM HS code सुझाता है) → `validate`। Invalid हो तो error के साथ `classify` पर वापस (अधिकतम 3 बार)। Confidence कम हो तो `human_review`। वरना `duty_lookup` और END। State में product, chunks, code, confidence, attempts रहते हैं।
**Zomato**: request समझो → खोजो → नतीजा न मिले तो filters ढीले करके दोबारा खोजो → confirm → order।

---

## 💻 Code Example — Basic
```python
# Basic LangGraph: classify -> validate with a retry loop. No LLM needed (offline).
# pip install langgraph
from typing import TypedDict                      # state schema type
from langgraph.graph import StateGraph, START, END   # graph builder + markers

class State(TypedDict):                           # shared state of the graph
    product: str                                  # input
    code: str                                     # proposed HS code
    attempts: int                                 # loop counter

def classify(state: State) -> dict:               # node 1: "LLM" proposes a code
    attempts = state["attempts"] + 1              # count attempt
    code = "85.18" if attempts == 1 else "8518.22"   # first try is badly formatted
    return {"code": code, "attempts": attempts}   # partial update merged into state

def validate(state: State) -> dict:               # node 2: pass-through (check is in router)
    return {}                                     # no state change

def route(state: State) -> str:                   # conditional edge decides next node
    valid = len(state["code"]) == 7 and "." in state["code"]   # simple format check
    if valid or state["attempts"] >= 3:           # stop when valid or too many tries
        return END
    return "classify"                             # otherwise loop back

g = StateGraph(State)                             # create graph
g.add_node("classify", classify)                  # register nodes
g.add_node("validate", validate)
g.add_edge(START, "classify")                     # start -> classify
g.add_edge("classify", "validate")                # classify -> validate
g.add_conditional_edges("validate", route)        # validate -> router decides
app = g.compile()                                 # build runnable

if __name__ == "__main__":
    print(app.invoke({"product": "speaker", "code": "", "attempts": 0}))
    # expected: code '8518.22', attempts 2
```

## 💻 Code Example — Advanced
```python
# Production-style: async nodes, LLM call with error handling, checkpointer, streaming, HITL branch.
import asyncio
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver      # use a DB checkpointer in production

class State(TypedDict, total=False):                     # total=False: keys may be missing early
    product: str
    chunks: list[str]
    code: str
    confidence: float
    attempts: int
    error: str | None
    status: str

async def retrieve(state: State) -> State:               # async node (I/O)
    await asyncio.sleep(0)                               # pretend vector search
    return {"chunks": ["8518: microphones, loudspeakers..."], "attempts": 0}

async def classify(state: State) -> State:
    attempts = state.get("attempts", 0) + 1
    try:
        # Replace with: await llm.ainvoke(...) using structured output
        code, conf = ("8518.22", 0.9) if attempts > 1 else ("85.18", 0.5)
        return {"code": code, "confidence": conf, "attempts": attempts, "error": None}
    except Exception as exc:                              # never crash the graph
        return {"attempts": attempts, "error": repr(exc), "confidence": 0.0}

async def validate(state: State) -> State:
    ok = bool(state.get("code")) and len(state["code"]) == 7
    return {"error": None if ok else "bad format"}

def route(state: State) -> Literal["classify", "human_review", "finish"]:
    if state.get("error") and state.get("attempts", 0) < 3:
        return "classify"                                 # retry loop
    if state.get("error") or state.get("confidence", 0) < 0.8:
        return "human_review"                             # escalate
    return "finish"

async def human_review(state: State) -> State:
    return {"status": "needs_human"}

async def finish(state: State) -> State:
    return {"status": "done"}

g = StateGraph(State)
for name, fn in [("retrieve", retrieve), ("classify", classify), ("validate", validate),
                 ("human_review", human_review), ("finish", finish)]:
    g.add_node(name, fn)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "classify")
g.add_edge("classify", "validate")
g.add_conditional_edges("validate", route)
g.add_edge("human_review", END)
g.add_edge("finish", END)
app = g.compile(checkpointer=MemorySaver())

async def main() -> None:
    cfg = {"configurable": {"thread_id": "case-1"}, "recursion_limit": 15}
    async for update in app.astream({"product": "speaker"}, cfg, stream_mode="updates"):
        print(update)                                     # one dict per node execution

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

api = FastAPI()

class Req(BaseModel):
    product: str
    thread_id: str

@api.post("/classify")
async def classify_route(req: Req) -> dict:
    cfg = {"configurable": {"thread_id": req.thread_id}, "recursion_limit": 15}
    try:
        result = await app.ainvoke({"product": req.product}, cfg)   # compiled graph from above
    except Exception as exc:                                         # includes GraphRecursionError
        raise HTTPException(502, f"workflow failed: {type(exc).__name__}")
    return {"code": result.get("code"), "status": result.get("status")}
```
Compile the graph once at startup (module level), not on every request. Use the request's `thread_id` for conversation or case persistence.

---

## 🔗 LangChain / LangGraph Connection
LangGraph nodes can call LangChain runnables (prompts, models, retrievers, tools). LangChain's old `AgentExecutor` is replaced by LangGraph prebuilt agents.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

chain = ChatPromptTemplate.from_template("HS code for: {product}") | ChatOpenAI(model="gpt-4o-mini")

async def classify_with_llm(state: dict) -> dict:
    msg = await chain.ainvoke({"product": state["product"]})   # LCEL chain inside a node
    return {"code": msg.content}

# Prebuilt: from langgraph.prebuilt import create_react_agent  (a ready-made agent graph)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A node mutates and returns the whole state or forgets to return updates.
✅ Correct: return only the keys you changed (a dict).

```python
# Wrong
def node(state): state["code"] = "x"      # mutation, nothing returned
# Right
def node(state): return {"code": "x"}
```

❌ Mistake 2: A loop with no exit.
✅ Correct: attempts counter and `recursion_limit`.

❌ Mistake 3: Using LangGraph for a simple one-shot prompt.
✅ Correct: use a plain chain; graphs pay off when you have loops, branches or persistence.

---

## 🧠 Tricky Interview Question
**Q**: "What is the difference between LangGraph and LangChain chains (LCEL)?"

**Answer**: LCEL composes steps into mostly linear, acyclic pipelines (`prompt | model | parser`). LangGraph models a **stateful graph** that can contain cycles, conditional routing, parallel branches, persistent checkpoints, interrupts and time travel. They work together: chains are great *inside* nodes, LangGraph orchestrates the control flow *between* nodes. Use LCEL for straight pipelines, LangGraph when behaviour depends on state or you need loops, memory or human approval.

---

## ⚫ Interview Questions + Answers

Q1: What are the core building blocks of LangGraph?
A1: State, nodes, edges (normal and conditional), `START`/`END`, and `compile()` (optionally with a checkpointer).

Q2: What does a node return?
A2: A dict of state updates. LangGraph merges it into the state (using reducers per key when defined).

Q3: Why is LangGraph called "durable"?
A3: With a checkpointer it saves state after each step, so runs can resume after failure, pause for humans and be replayed by thread.

Q4: Is LangGraph only for agents?
A4: No. It orchestrates any multi-step workflow, with or without LLMs.

Q5: (Hard) How would you run parallel branches and merge results?
A5: Add edges from one node to several nodes; they run in the same superstep. Use a reducer on shared keys (for example `Annotated[list, operator.add]`) so each branch's output is appended rather than overwritten. Then edge all branches to a join node.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Loops, branches, retries or multi-agent flows
- Human approval, pause/resume, long-running jobs
- Need state persistence and streaming

❌ Avoid when:
- One prompt or a straight chain is enough
- Team needs minimal dependencies for a trivial script

---

## 📊 Visual Diagram
```
START ─► retrieve ─► classify ─► validate ──(router)──┐
                        ▲                              │
                        └──── error & attempts<3 ──────┤
                                                       ├─ low confidence ─► human_review ─► END
                                                       └─ ok ─► finish ─► END
State (shared): product · chunks · code · confidence · attempts · error
```

---

## 💰 Cost Impact
The graph itself is free (plain Python). Cost comes from the LLM nodes: loops multiply calls, so always cap attempts. Explicit graphs help control cost because you decide exactly where LLMs are used, can route easy cases around expensive nodes, and can use small models per node. Checkpoint storage has a small database cost. Retries inside loops resend the prompt, so keep state passed to prompts short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Graph | Nodes connected by edges | Nodes और edges का जाल |
| State | Shared data passed between nodes | Nodes के बीच साझा डेटा |
| Node | Function that updates state | State बदलने वाला function |
| Edge | Link to the next node | अगले node का लिंक |
| Checkpointer | Saves state per step | हर step पर state सहेजना |
| thread_id | Key for a conversation/run | बातचीत/run की key |
| recursion_limit | Max steps safety cap | अधिकतम steps की सीमा |

---

## ⚡ 3-Line Summary
English: LangGraph builds LLM apps as stateful graphs with nodes, edges, loops and branches. It adds persistence, human approval and streaming that plain chains lack. Use it when control flow depends on state.
Hindi: LangGraph LLM apps को nodes, edges, loops और branches वाले stateful graph की तरह बनाता है। इसमें persistence, human approval और streaming मिलती है जो साधारण chains में नहीं। जब control flow state पर निर्भर हो तब इसे इस्तेमाल करो।

---

## ➡️ Next Topic
**317. LangGraph vs AgentExecutor** — why the older LangChain agent loop was replaced and how to migrate.
