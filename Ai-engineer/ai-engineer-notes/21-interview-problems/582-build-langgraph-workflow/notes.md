---

# 582. Build LangGraph Workflow
# हिंदी में: LangGraph Workflow बनाना

---

## 🔵 Simple Definition (English)
LangGraph models an LLM app as a graph: a shared State, Nodes (functions that update state) and Edges (fixed or conditional transitions). Because the flow is explicit, you get loops, branching, retries, persistence and human-in-the-loop without hiding logic inside prompts.

## 🔵 सरल परिभाषा (Hindi)
LangGraph LLM app को graph की तरह बनाता है: साझा State, Nodes (state अपडेट करने वाले functions) और Edges (fixed या conditional transitions)। Flow साफ़ दिखता है, इसलिए loops, branching, retries, persistence और human-in-the-loop बिना prompt में logic छुपाए मिलते हैं।

---

## 🔴 Problem it Solves
Simple chains are linear. Real workflows need "if confidence is low, retry or ask a human", loops with limits, parallel branches and resumable state after a crash. Free-form agents are flexible but unpredictable. A graph gives control with flexibility.

## 🔴 यह क्यों बना? (Hindi)
सरल chains सीधी रेखा में चलती हैं। असली workflow में चाहिए "confidence कम हो तो retry या human से पूछो", सीमा वाले loops, parallel branches और crash के बाद resume। Free-form agents लचीले पर अनिश्चित होते हैं। Graph control और flexibility दोनों देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define State (TypedDict / pydantic) shared by all nodes
Step 2 → Write nodes: fn(state) -> partial update dict
Step 3 → add_node(name, fn) for each
Step 4 → add_edge for fixed moves; add_conditional_edges(router) for branching
Step 5 → set entry point / START and END
Step 6 → compile() (optionally with a checkpointer)
Step 7 → invoke(initial_state) runs until END; updates are merged each step
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State define करो (TypedDict / pydantic), सब nodes साझा करते हैं
Step 2 → Nodes लिखो: fn(state) -> partial update dict
Step 3 → हर एक के लिए add_node(name, fn)
Step 4 → Fixed चाल के लिए add_edge; branching के लिए add_conditional_edges(router)
Step 5 → START / entry और END तय करो
Step 6 → compile() (चाहें तो checkpointer के साथ)
Step 7 → invoke(initial_state) END तक चलता है; हर step में updates merge होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: node `classify` returns an HS code with confidence. Router: confidence below 0.8 and fewer than 3 attempts goes back to `classify` (with more context); otherwise go to `review`. In `main.py` the second attempt reaches 0.9 and ends. **Zomato-style**: order flow with nodes `validate_cart`, `payment`, `assign_rider` and conditional failure paths. **Amazon-style**: return-request flow with a human approval node.

## 🟡 Real Example Hindi mein
**Tariff System**: `classify` node HS code और confidence देता है। Router: confidence 0.8 से कम और attempts 3 से कम हो तो फिर `classify`; वरना `review`। `main.py` में दूसरी कोशिश पर 0.9 आता है और flow खत्म होता है। **Zomato**: `validate_cart`, `payment`, `assign_rider` nodes और failure paths। **Amazon**: return flow में human approval node।

---

## 💻 Code Example — Basic
`main.py` includes a mini graph engine (offline) and `build_langgraph()` with the real library (used only if installed).

```python
# Basic: nodes as functions, a router deciding the next node
state = {"conf": 0.5, "tries": 0}  # shared state

def classify(s: dict) -> dict:  # node
    return {"conf": 0.9, "tries": s["tries"] + 1}  # pretend retry improves confidence

def route(s: dict) -> str:  # conditional edge
    return "classify" if s["conf"] < 0.8 and s["tries"] < 3 else "end"  # loop or stop

node = "classify"  # entry
while node != "end":  # run the graph
    state = {**state, **classify(state)}  # merge node update into state
    node = route(state)  # decide next
print(state)  # {'conf': 0.9, 'tries': 1}
```

## 💻 Code Example — Advanced
`main.py`: `State` TypedDict, `Graph` runner with a `max_steps` guard (raises `RuntimeError` on cycles), async `arun`. Real LangGraph version with persistence (illustrative):

```python
# pip install langgraph  (API names current as of recent versions; verify in docs)
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class S(TypedDict, total=False):  # state schema
    conf: float  # confidence
    tries: int  # attempts

def classify(s: S) -> S:  # node
    return {"conf": 0.9, "tries": s.get("tries", 0) + 1}  # partial update

def route(s: S) -> str:  # router
    return "classify" if s["conf"] < 0.8 and s["tries"] < 3 else END  # loop or finish

g = StateGraph(S)  # builder
g.add_node("classify", classify)  # register node
g.add_edge(START, "classify")  # entry edge
g.add_conditional_edges("classify", route)  # branching
app = g.compile(checkpointer=MemorySaver())  # state saved per thread_id
# app.invoke({"tries": 0}, config={"configurable": {"thread_id": "t1"}})
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import build  # mini engine; swap for compiled LangGraph app in prod

app = FastAPI()  # app
graph = build()  # compile once at startup (reuse across requests)

class In(BaseModel):  # request
    product: str  # product name

@app.post("/classify")  # route
async def classify(body: In) -> dict:  # handler
    try:  # guard cycles
        state = await graph.arun({"product": body.product})  # run workflow
    except RuntimeError as exc:  # exceeded steps
        raise HTTPException(500, str(exc))  # server error
    return state  # JSON state
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph is part of the LangChain ecosystem. Nodes can be any Runnable (an LLM call, a retriever, a tool). Prebuilt `create_react_agent` is itself a two-node graph. Checkpointers give memory and resume; `interrupt` supports human approval; `stream` yields per-node updates.

```python
# Illustrative: stream node-by-node updates
# for update in app.stream({"tries": 0}, config={"configurable": {"thread_id": "t1"}}):
#     print(update)  # {'classify': {...}}
print("stream() gives per-node updates for progress UIs and debugging")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Cycle without a limit
✅ Correct: Count attempts in state and bound the router.

```python
# Wrong: always loops if conf stays low
def route_bad(s: dict) -> str:
    return "classify" if s["conf"] < 0.8 else "end"
# Right
def route_ok(s: dict) -> str:
    return "classify" if s["conf"] < 0.8 and s["tries"] < 3 else "end"
```

❌ Mistake 2: Node mutates state in place / returns whole state
✅ Correct: Return only the changed keys.

```python
# Wrong: s["x"] = 1; return s   (hidden side effects, breaks reducers)
# Right:
def node(s: dict) -> dict:
    return {"x": 1}
```

---

## 🧠 Tricky Interview Question
**Q**: "Two parallel nodes both write `sources` to state. Results randomly overwrite each other. Why?"

**Answer**: Without a reducer, the last write wins. In LangGraph you annotate the key with a reducer (e.g. `Annotated[list, operator.add]`) so parallel updates are merged. The lesson: parallel branches need explicit merge semantics.

---

## ⚫ Interview Questions + Answers

Q1: What are the three core pieces of LangGraph? (Easy)
A1: State, nodes and edges.

Q2: Why a graph instead of a chain? (Easy)
A2: Graphs allow loops, branches and retries; chains are linear.

Q3: What is a checkpointer? (Medium)
A3: It saves state after each step per thread_id, enabling memory, resuming after failure and time-travel debugging.

Q4: How do you add human approval? (Medium)
A4: Pause with an interrupt before a risky node, persist state, show it to a human, then resume with their decision.

Q5: When would you choose LangGraph over a free-form agent? (Hard)
A5: When you need predictable control, compliance and auditability: known stages, bounded retries, human checkpoints, testable nodes. Use agents inside a single node when you want flexibility but keep the outer flow deterministic.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-step flows with branching, retry or approval
- Need persistence, streaming and observability

❌ Avoid when:
- One LLM call is enough
- Team cannot maintain the added abstraction

---

## 📊 Visual Diagram
```
 START ─► classify ──conf>=0.8──► review ─► END
             ▲  │
             └──┘ conf<0.8 and tries<3
        (shared State flows through every node)
```

---

## 💰 Cost Impact
Each LLM node costs tokens; loops multiply them. Example (illustrative): a 2-retry loop triples the classify cost. Optimise: cap retries, use cheap models for routing nodes, run deterministic checks (regex, DB lookup) as non-LLM nodes, cache node outputs, and pass only needed state fields into prompts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Shared data | साझा डेटा |
| Node | Function that updates state | State बदलने वाला function |
| Edge | Transition | एक node से दूसरे पर जाना |
| Conditional edge | Router picks next | Router तय करता है आगे क्या |
| Reducer | Merge rule for updates | Updates जोड़ने का नियम |
| Checkpointer | Persists state | State save करना |

---

## ⚡ 3-Line Summary
English: LangGraph = State + Nodes + Edges. Conditional edges give loops and branches; checkpointers give memory and resume. Always bound loops.
Hindi: LangGraph = State + Nodes + Edges। Conditional edges से loops और branches मिलते हैं; checkpointer से memory और resume। Loops हमेशा सीमित रखो।

---

## ➡️ Next Topic
**583. Build Multi-Agent System** — several specialised agents coordinated by a supervisor.
