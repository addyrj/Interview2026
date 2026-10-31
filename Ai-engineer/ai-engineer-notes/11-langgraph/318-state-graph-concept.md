---

# 318. State Graph Concept
# हिंदी में: State Graph की अवधारणा

---

## 🔵 Simple Definition (English)
A **StateGraph** is a workflow where many functions (nodes) share one **state** object. Each node reads the state and returns changes. The graph engine merges those changes (using reducers), then follows edges to decide the next node. Think of it as a flowchart where all boxes read and write the same notebook.

## 🔵 सरल परिभाषा (Hindi)
**StateGraph** एक workflow है जिसमें कई functions (nodes) एक साझा **state** इस्तेमाल करते हैं। हर node state पढ़ता है और बदलाव लौटाता है। Graph engine उन बदलावों को (reducers से) merge करता है, फिर edges से अगला node तय करता है। इसे ऐसे समझो: flowchart जिसके सारे डिब्बे एक ही notebook में पढ़ते-लिखते हैं।

---

## 🔴 Problem it Solves
In plain code you pass values from function to function by hand, and loops/branches get tangled. A state graph gives one clear place for data, clear rules for how updates merge, and a clear map of control flow. That makes it easy to checkpoint ("save the notebook"), resume, debug (see state after each node) and visualise.

## 🔴 यह क्यों बना? (Hindi)
सामान्य code में values हाथ से function-दर-function पास करनी पड़ती हैं और loops/branches उलझ जाते हैं। State graph डेटा के लिए एक साफ़ जगह, updates merge करने के साफ़ नियम और control flow का नक्शा देता है। इससे checkpoint ("notebook save"), resume, debug (हर node के बाद state देखना) और visualise आसान होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define State (schema) and optional reducers per key
Step 2 → Build graph: add_node, add_edge, add_conditional_edges
Step 3 → compile() validates the graph (unknown nodes, unreachable parts)
Step 4 → invoke(input): input becomes the initial state
Step 5 → "Superstep": run the ready node(s); each returns a partial update
Step 6 → Reducers merge updates into state (default: overwrite; or append, etc.)
Step 7 → Follow edges / router to pick the next node(s)
Step 8 → Stop at END (or recursion_limit); return the final state
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State (schema) और चाहें तो हर key का reducer तय करो
Step 2 → add_node, add_edge, add_conditional_edges से graph बनाओ
Step 3 → compile() graph जाँचता है (अज्ञात nodes, unreachable हिस्से)
Step 4 → invoke(input): input शुरुआती state बनता है
Step 5 → "Superstep": तैयार node(s) चलते हैं; हर एक आंशिक update लौटाता है
Step 6 → Reducers updates को state में merge करते हैं (default: overwrite)
Step 7 → Edges / router से अगला node चुनो
Step 8 → END पर (या recursion_limit पर) रुको; अंतिम state लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: State = `{product, candidates, chosen_code, notes, attempts}`. Node `retrieve` fills `candidates`; node `classify` sets `chosen_code`; node `explain` appends to `notes`. If two parallel nodes (`legal_check`, `risk_check`) both add notes, the `notes` key uses an append reducer so neither overwrites the other.

**Zomato-style**: state holds cart, address, and applied coupons; nodes update only their part.

## 🟡 Real Example Hindi mein
**Tariff System**: State = `{product, candidates, chosen_code, notes, attempts}`। `retrieve` node `candidates` भरता है; `classify` `chosen_code` तय करता है; `explain` `notes` में जोड़ता है। दो parallel nodes (`legal_check`, `risk_check`) दोनों notes जोड़ें तो `notes` पर append reducer होता है ताकि कोई किसी को overwrite न करे।
**Zomato**: state में cart, address, coupons; हर node अपना हिस्सा ही बदलता है।

---

## 💻 Code Example — Basic
```python
# Basic: state, reducer and two nodes (offline). pip install langgraph
import operator                                        # operator.add appends lists
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    product: str                                       # overwritten by default
    notes: Annotated[list[str], operator.add]          # reducer: new list is APPENDED
    code: str

def retrieve(state: State) -> dict:
    return {"notes": [f"retrieved docs for {state['product']}"]}   # appended, not replaced

def classify(state: State) -> dict:
    return {"code": "8518.22", "notes": ["classified"]}            # both keys updated

g = StateGraph(State)
g.add_node("retrieve", retrieve)
g.add_node("classify", classify)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "classify")
g.add_edge("classify", END)
app = g.compile()

if __name__ == "__main__":
    final = app.invoke({"product": "speaker", "notes": [], "code": ""})
    print(final)       # notes has BOTH entries because of the reducer
    for step in app.stream({"product": "speaker", "notes": [], "code": ""}, stream_mode="values"):
        print(step)    # full state after each step
```

## 💻 Code Example — Advanced
```python
# Advanced: parallel branches, custom reducer, input/output schemas, async, error capture.
import asyncio
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

def merge_scores(old: dict[str, float], new: dict[str, float]) -> dict[str, float]:
    return {**(old or {}), **new}                       # custom reducer: merge dicts

class InputState(TypedDict):                            # what callers must send
    product: str

class OutputState(TypedDict):                           # what callers receive
    decision: str

class State(InputState, OutputState):                   # full internal state
    scores: Annotated[dict[str, float], merge_scores]   # parallel nodes write here
    errors: Annotated[list[str], lambda a, b: (a or []) + b]

async def legal_check(state: State) -> dict:
    await asyncio.sleep(0.01)
    return {"scores": {"legal": 0.9}}

async def risk_check(state: State) -> dict:
    try:
        await asyncio.sleep(0.01)
        if "weapon" in state["product"]:
            raise ValueError("restricted product")
        return {"scores": {"risk": 0.8}}
    except Exception as exc:
        return {"scores": {"risk": 0.0}, "errors": [repr(exc)]}   # capture, do not crash

async def decide(state: State) -> dict:                 # join node: runs after both branches
    avg = sum(state["scores"].values()) / len(state["scores"])
    return {"decision": "approve" if avg > 0.7 and not state.get("errors") else "review"}

g = StateGraph(State, input=InputState, output=OutputState)   # schemas (keyword names vary by version: input/input_schema)
g.add_node("legal_check", legal_check)
g.add_node("risk_check", risk_check)
g.add_node("decide", decide)
g.add_edge(START, "legal_check")                         # fan-out: two edges from START
g.add_edge(START, "risk_check")
g.add_edge(["legal_check", "risk_check"], "decide")      # fan-in: wait for both
g.add_edge("decide", END)
app = g.compile()

async def main() -> None:
    print(await app.ainvoke({"product": "speaker"}))     # {'decision': 'approve'}
    print(await app.ainvoke({"product": "weapon part"})) # {'decision': 'review'}

if __name__ == "__main__":
    asyncio.run(main())
```
Note: constructor keyword names for input/output schemas changed across LangGraph versions (`input`/`output` older, `input_schema`/`output_schema` newer). Check your installed version; if unsure, omit them and use one State.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

api = FastAPI()

class Req(BaseModel):
    product: str

@api.post("/assess")
async def assess(req: Req) -> dict:
    return await app.ainvoke({"product": req.product})    # state in, final output out

@api.post("/assess/debug")
async def assess_debug(req: Req) -> list[dict]:
    steps = []
    async for s in app.astream({"product": req.product}, stream_mode="updates"):
        steps.append(s)                                    # per-node updates for debugging
    return steps
```
Pydantic request models validate user input before it becomes graph state; do not pass raw request dicts into state.

---

## 🔗 LangChain / LangGraph Connection
The prebuilt `MessagesState` is a ready State with one key, `messages`, using the `add_messages` reducer. Extend it:

```python
from langgraph.graph import MessagesState, StateGraph

class AgentState(MessagesState):          # inherits messages + add_messages reducer
    hs_code: str                          # extra key
    confidence: float

g = StateGraph(AgentState)
```
LangChain runnables run inside nodes; the graph state is how their outputs get shared.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two parallel nodes writing the same key without a reducer.
✅ Correct: add a reducer (append/merge); otherwise LangGraph raises `InvalidUpdateError`.

```python
# Wrong
notes: list[str]
# Right
notes: Annotated[list[str], operator.add]
```

❌ Mistake 2: Putting huge objects (full PDFs, embeddings) in state, which is checkpointed every step.
✅ Correct: store ids/references; keep the big data in a DB or object store.

❌ Mistake 3: Returning the full state from nodes.
✅ Correct: return only changed keys.

---

## 🧠 Tricky Interview Question
**Q**: "Two parallel nodes both return `{'count': 1}`. Final state `count` is 1, not 2. What happened?"

**Answer**: The default reducer overwrites. (If both ran in the same step with no reducer LangGraph typically raises an error for concurrent updates.) To sum, define `count: Annotated[int, operator.add]`. Reducers define how concurrent updates combine, so design them deliberately for any key that several nodes touch.

---

## ⚫ Interview Questions + Answers

Q1: What is state in LangGraph?
A1: A shared schema (TypedDict, dataclass or pydantic model) holding all data nodes read and update.

Q2: What is a reducer?
A2: A function `(old, new) -> merged` attached to a key with `Annotated`. It controls how updates combine; default is overwrite.

Q3: What is a superstep?
A3: One round where all currently-ready nodes run (in parallel) and their updates are applied together before the next round.

Q4: What does `compile()` do?
A4: Validates the graph and returns a runnable app, optionally with a checkpointer and interrupt settings.

Q5: (Hard) Why use separate input and output schemas?
A5: To keep the public API small and safe: callers send only required inputs and see only final outputs, while internal keys (scores, errors, scratch data) stay hidden. It also prevents leaking intermediate data to clients.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several steps share data
- Parallel branches must merge results
- You want to checkpoint and debug state per step

❌ Avoid when:
- Single function can do the job
- You would store massive blobs in state

---

## 📊 Visual Diagram
```
            ┌──────────────── STATE ────────────────┐
            │ product │ scores{} │ notes[] │ decision│
            └───▲──────────▲──────────▲─────────▲───┘
   read/write   │          │          │         │
START ─┬─► legal_check ────┘          │         │
       └─► risk_check ────────────────┘         │
                 └──── join ───► decide ──────────┘ ─► END
Reducers: scores = merge dicts · notes = append · decision = overwrite
```

---

## 💰 Cost Impact
State size matters: if you pass the whole state (long notes, chunks) into every LLM prompt, tokens grow with every node. Build each prompt from only the keys that node needs. Large state also costs checkpoint storage and serialisation time. Parallel branches reduce latency but not tokens, since each LLM branch is still billed. Summarise or drop old keys when they are no longer needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StateGraph | Graph over shared state | साझा state पर graph |
| Reducer | Rule to merge updates | Updates merge करने का नियम |
| Superstep | One round of node execution | Nodes के चलने का एक दौर |
| Fan-out / fan-in | Split into branches / join them | शाखाओं में बँटना / वापस जुड़ना |
| MessagesState | Prebuilt chat state | Chat के लिए तैयार state |
| Annotated | Python typing to attach reducer | Reducer जोड़ने की typing |

---

## ⚡ 3-Line Summary
English: A StateGraph shares one state among nodes; nodes return partial updates that reducers merge. Edges and routers choose the next node, supersteps allow parallelism. Keep state small and give shared keys reducers.
Hindi: StateGraph में सभी nodes एक state साझा करते हैं; nodes आंशिक updates लौटाते हैं जिन्हें reducers merge करते हैं। Edges/routers अगला node चुनते हैं और supersteps से parallelism मिलती है। State छोटी रखो और साझा keys पर reducers लगाओ।

---

## ➡️ Next Topic
**319. State — TypedDict** — how to define the state schema well: TypedDict vs dataclass vs pydantic.
