---

# 319. State — TypedDict
# हिंदी में: State — TypedDict

---

## 🔵 Simple Definition (English)
In LangGraph, the State is the shared data object that flows through the graph. The most common way to define it is a Python `TypedDict`: each key is a channel (like `messages`, `hs_code`, `confidence`). Nodes read the state and return partial updates. Each key can have a reducer (for example `add_messages` or `operator.add`) that says how to merge updates instead of overwriting.

## 🔵 सरल परिभाषा (Hindi)
LangGraph में State वह साझा data object है जो graph में बहता है। इसे define करने का सबसे आम तरीका Python `TypedDict` है: हर key एक channel है (जैसे `messages`, `hs_code`, `confidence`)। Nodes state पढ़ते हैं और partial updates लौटाते हैं। हर key पर reducer (जैसे `add_messages` या `operator.add`) लग सकता है जो बताता है कि update को overwrite की जगह कैसे merge करना है।

---

## 🔴 Problem it Solves
A multi-step workflow needs shared memory: what the user asked, what each step found, what to do next. Passing many function arguments around is messy, and parallel steps writing the same list would overwrite each other. A typed state plus reducers gives one clear contract and safe merging.

## 🔴 यह क्यों बना? (Hindi)
Multi-step workflow को साझा memory चाहिए: user ने क्या पूछा, हर step ने क्या पाया, आगे क्या करना है। कई function arguments घुमाना messy है, और एक ही list लिखने वाले parallel steps एक-दूसरे को overwrite कर देंगे। Typed state और reducers एक साफ़ contract और सुरक्षित merging देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define class State(TypedDict) with keys and types
Step 2 → Optionally annotate keys with reducers: Annotated[list, operator.add]
Step 3 → graph = StateGraph(State)
Step 4 → Caller invokes graph with an initial (partial) state
Step 5 → Each node receives the full current state, returns {"key": new_value}
Step 6 → LangGraph merges: no reducer -> overwrite; reducer -> combine(old, new)
Step 7 → Final state is returned (and checkpointed if a checkpointer is set)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → class State(TypedDict) में keys और types define करो
Step 2 → चाहें तो keys पर reducer लगाओ: Annotated[list, operator.add]
Step 3 → graph = StateGraph(State)
Step 4 → Caller शुरुआती (partial) state के साथ graph invoke करता है
Step 5 → हर node पूरी current state पाता है, {"key": new_value} लौटाता है
Step 6 → LangGraph merge करता है: reducer नहीं -> overwrite; reducer -> combine(old, new)
Step 7 → Final state लौटती है (checkpointer हो तो checkpoint भी होती है)
```

---

## 🟡 Real World Example
**Tariff Classification System**: State keys: `product_text: str`, `candidates: list[str]` (reducer: append), `hs_code: str | None`, `confidence: float`, `needs_review: bool`, `messages` (chat). Node `retrieve` appends candidates; node `classify` sets `hs_code` and `confidence`; a router sends low confidence to human review. Every node sees the same state, so debugging is easy: print the state after each step.

**Zomato AI**: state holds `cart`, `address`, `payment_status`.

## 🟡 Real Example Hindi mein
**Tariff System**: State keys: `product_text: str`, `candidates: list[str]` (reducer: append), `hs_code: str | None`, `confidence: float`, `needs_review: bool`, `messages` (chat)। Node `retrieve` candidates जोड़ता है; node `classify` `hs_code` और `confidence` set करता है; router कम confidence को human review भेजता है। हर node वही state देखता है, इसलिए debugging आसान है: हर step के बाद state print करो।

**Zomato AI**: state में `cart`, `address`, `payment_status`।

---

## 💻 Code Example — Basic
```python
# Basic: simulate how LangGraph merges TypedDict state with reducers (pure Python, offline)
import operator                                         # operator.add concatenates lists
from typing import Annotated, Any, TypedDict, get_type_hints   # typing tools

class State(TypedDict):
    product_text: str                                   # no reducer -> overwrite
    candidates: Annotated[list[str], operator.add]      # reducer -> append
    hs_code: str | None                                 # no reducer -> overwrite
    confidence: float

def merge(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Mimic LangGraph channel update: use reducer if present, else overwrite."""
    hints = get_type_hints(State, include_extras=True)  # keeps Annotated metadata
    new_state = dict(state)
    for key, value in update.items():
        if key not in hints:                            # LangGraph also rejects unknown keys
            raise KeyError(f"unknown state key: {key}")
        meta = getattr(hints[key], "__metadata__", ())  # reducer lives in Annotated metadata
        reducer = meta[0] if meta else None
        new_state[key] = reducer(state.get(key, []), value) if reducer else value
    return new_state

state: dict[str, Any] = {"product_text": "wireless earbuds", "candidates": [], "hs_code": None, "confidence": 0.0}
state = merge(state, {"candidates": ["851830"]})        # node A
state = merge(state, {"candidates": ["851762"]})        # node B (appended, not overwritten)
state = merge(state, {"hs_code": "851830", "confidence": 0.91})   # node C overwrites scalars
print(state)
try:
    merge(state, {"colour": "red"})                     # typo/unknown key
except KeyError as exc:
    print("error:", exc)
```

## 💻 Code Example — Advanced
```python
# Production: StateGraph with TypedDict state, reducers, input/output schemas, async nodes
import asyncio                                           # async runtime
import operator                                          # list append reducer
from typing import Annotated, Any, TypedDict             # typing
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END       # pip install langgraph
from langgraph.graph.message import add_messages         # smart reducer for chat messages

class InputState(TypedDict):
    product_text: str                                    # what the API accepts

class OutputState(TypedDict):
    hs_code: str | None                                  # what the API returns
    confidence: float

class State(InputState, OutputState):
    messages: Annotated[list[AnyMessage], add_messages]  # merges by message id, appends new
    candidates: Annotated[list[str], operator.add]       # appended across nodes
    errors: Annotated[list[str], operator.add]           # collect errors safely

async def retrieve(state: State) -> dict[str, Any]:
    """Node 1: find candidate HS codes (pretend vector search)."""
    await asyncio.sleep(0)
    return {"candidates": ["851830", "851762"]}          # partial update

async def classify(state: State) -> dict[str, Any]:
    """Node 2: pick the best candidate."""
    try:
        if not state["candidates"]:
            raise ValueError("no candidates")
        return {"hs_code": state["candidates"][0], "confidence": 0.9}
    except ValueError as exc:
        return {"hs_code": None, "confidence": 0.0, "errors": [str(exc)]}

builder = StateGraph(State, input=InputState, output=OutputState)   # explicit I/O schemas
builder.add_node("retrieve", retrieve)
builder.add_node("classify", classify)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "classify")
builder.add_edge("classify", END)
graph = builder.compile()

async def main() -> None:
    result = await graph.ainvoke({"product_text": "wireless earbuds"})
    print(result)       # only OutputState keys: {'hs_code': '851830', 'confidence': 0.9}

if __name__ == "__main__":
    asyncio.run(main())
```

Note: newer langgraph releases also accept the keywords `input_schema=` / `output_schema=`; if your installed version complains about `input=`/`output=`, check its docs for the exact name. (Not run here: langgraph was not installed.)

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException               # framework
from pydantic import BaseModel

app = FastAPI()

class ClassifyReq(BaseModel):
    product_text: str

class ClassifyRes(BaseModel):
    hs_code: str | None
    confidence: float

@app.post("/classify", response_model=ClassifyRes)
async def classify_route(req: ClassifyReq) -> ClassifyRes:
    try:
        out = await graph.ainvoke({"product_text": req.product_text})   # state in -> state out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return ClassifyRes(**out)                            # output schema matches API model
```

---

## 🔗 LangChain / LangGraph Connection
`MessagesState` is a ready-made TypedDict with `messages: Annotated[list[AnyMessage], add_messages]`. Extend it with your own keys. State can also be a dataclass or Pydantic model if you need runtime validation (a bit more overhead).

```python
from langgraph.graph import MessagesState
class TariffState(MessagesState):                        # inherits messages + reducer
    hs_code: str | None
    confidence: float
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A list key without a reducer when several nodes (or parallel branches) write it
✅ Correct: Add `Annotated[list, operator.add]`.

```python
# Wrong - second write replaces the first; parallel writes may raise InvalidUpdateError
class State(TypedDict):
    candidates: list[str]
# Right
class State(TypedDict):
    candidates: Annotated[list[str], operator.add]
```

❌ Mistake 2: Mutating state in place and returning nothing
✅ Correct: Return a dict of updates.

```python
# Wrong
def node(state):
    state["hs_code"] = "8518"       # not how LangGraph records updates
# Right
def node(state) -> dict:
    return {"hs_code": "8518"}
```

---

## 🧠 Tricky Interview Question
**Q**: "Two parallel nodes both return `{"messages": [...]}`. One graph keeps both, another loses data or errors. What is different?"

**Answer**: Whether the `messages` key has a reducer. With `Annotated[list, add_messages]` (or `operator.add`) the updates are merged. Without a reducer, parallel writes to one key conflict (LangGraph raises `InvalidUpdateError`) and in sequential flows the last write wins. Define reducers on any key that more than one node writes, and keep the update order-independent (appending is safe; overwriting is not).

---

## ⚫ Interview Questions + Answers

Q1: What is State in LangGraph?
A1: The shared, typed data passed between nodes; nodes return partial updates that LangGraph merges.

Q2: Why TypedDict and not a plain dict?
A2: TypedDict documents keys and types for editors and for LangGraph to build channels. It has no runtime validation, though.

Q3: What does a reducer do?
A3: It defines how to combine the old value and a new update for a key, such as appending to a list. Without it, the new value overwrites.

Q4: What is `add_messages`?
A4: A reducer for chat messages: appends new messages and replaces ones with the same id; also converts tuples/dicts to message objects.

Q5: (Hard) When would you choose Pydantic state over TypedDict?
A5: When you need runtime validation of node outputs and defaults, for example untrusted tool data. Costs: slightly more overhead and stricter errors. You can keep TypedDict for internal state and validate API input/output with Pydantic at the FastAPI boundary.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any LangGraph graph (state is mandatory)
- You want clear contracts between nodes

❌ Avoid when:
- Putting huge blobs (full documents, files) in state; store them elsewhere and keep references/IDs, because state is checkpointed and copied

---

## 📊 Visual Diagram
```
 State (TypedDict)
 +--------------------------------------------+
 | product_text : str                         |
 | candidates   : list[str]   (reducer: +)    |
 | hs_code      : str | None                  |
 | confidence   : float                       |
 +--------------------------------------------+
      |               ^
      v               | partial update {"candidates": [...]}
   [retrieve] ---> merge ---> [classify] ---> merge ---> END
```

---

## 💰 Cost Impact
- State itself is free, but whatever you put in `messages` is sent to the LLM every call. Large state in prompts means large token bills.
- Keep non-LLM fields (scores, flags, IDs) out of prompts; build each prompt from only the keys needed.
- Checkpointing large states increases storage and latency. Trim `messages` (e.g. `trim_messages`) and store big documents externally.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Shared graph data | Graph का साझा data |
| TypedDict | Typed dictionary schema | Typed dictionary schema |
| Channel | One key of the state | State की एक key |
| Reducer | Merge function for updates | Updates जोड़ने का function |
| add_messages | Chat message reducer | Chat messages का reducer |
| Partial update | Only changed keys returned | सिर्फ़ बदली keys लौटाना |

---

## ⚡ 3-Line Summary
English: LangGraph State is a typed shared object, usually a TypedDict, that nodes read and update. Reducers decide whether updates overwrite or merge. Keep it small, and only send needed parts to the LLM.
Hindi: LangGraph State एक typed साझा object है, आमतौर पर TypedDict, जिसे nodes पढ़ते और update करते हैं। Reducers तय करते हैं कि update overwrite होगा या merge। इसे छोटा रखें और LLM को सिर्फ़ ज़रूरी हिस्से भेजें।

---

## ➡️ Next Topic
**320. Nodes in LangGraph** — the functions that read state and return updates.
