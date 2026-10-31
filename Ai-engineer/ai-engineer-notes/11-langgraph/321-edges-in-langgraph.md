---

# 321. Edges in LangGraph
# हिंदी में: LangGraph में Edges

---

## 🔵 Simple Definition (English)
Edges define which node runs after which. A normal edge (`add_edge("a", "b")`) always goes from a to b. A conditional edge (`add_conditional_edges("a", router)`) calls a router function that looks at the state and returns the name of the next node (or several). `START` and `END` are special markers for the entry and exit of the graph.

## 🔵 सरल परिभाषा (Hindi)
Edges तय करते हैं कि किस node के बाद कौन सा node चलेगा। Normal edge (`add_edge("a", "b")`) हमेशा a से b जाता है। Conditional edge (`add_conditional_edges("a", router)`) router function बुलाता है जो state देखकर अगले node का नाम (या कई नाम) लौटाता है। `START` और `END` graph के entry और exit के विशेष markers हैं।

---

## 🔴 Problem it Solves
Real workflows branch: "if confidence is high, finish; otherwise ask a human", or "if the model wants tools, run tools, then loop back". Hard-coding this with nested if/else inside one function is brittle. Edges make control flow explicit, visual, and easy to change without touching node logic.

## 🔴 यह क्यों बना? (Hindi)
असली workflows में branching होती है: "confidence ज़्यादा हो तो खत्म, वरना human से पूछो", या "model tools चाहे तो tools चलाओ, फिर loop में वापस जाओ"। एक function में nested if/else से यह fragile हो जाता है। Edges control flow को साफ़, दिखने योग्य और node logic बदले बिना बदलने योग्य बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → add_edge(START, "retrieve")           entry point
Step 2 → add_edge("retrieve", "classify")      fixed route
Step 3 → add_conditional_edges("classify", router, {"high": "finish", "low": "human_review"})
Step 4 → Runtime: node "classify" finishes, state is updated
Step 5 → router(state) returns a label such as "low"
Step 6 → LangGraph maps the label to a node ("human_review") and runs it
Step 7 → Path ends when a node connects to END (or no more edges)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → add_edge(START, "retrieve")           entry point
Step 2 → add_edge("retrieve", "classify")      fixed route
Step 3 → add_conditional_edges("classify", router, {"high": "finish", "low": "human_review"})
Step 4 → Runtime: node "classify" खत्म होता है, state update होती है
Step 5 → router(state) "low" जैसा label लौटाता है
Step 6 → LangGraph label को node ("human_review") से map करके चलाता है
Step 7 → Path तब खत्म होता है जब node END से जुड़े (या कोई edge न बचे)
```

---

## 🟡 Real World Example
**Tariff Classification System**: after `llm_classify`, the router checks `confidence`: >= 0.85 goes to `auto_approve`; between 0.5 and 0.85 goes to `retrieve_more` (loop back for more evidence, max 2 times); below 0.5 goes to `human_review`. Changing thresholds touches only the router, not the nodes.

**Amazon AI**: router sends "refund > 5000" to a manager approval node and the rest to auto refund.

## 🟡 Real Example Hindi mein
**Tariff System**: `llm_classify` के बाद router `confidence` देखता है: >= 0.85 -> `auto_approve`; 0.5 से 0.85 -> `retrieve_more` (और सबूत के लिए वापस loop, अधिकतम 2 बार); 0.5 से कम -> `human_review`। Thresholds बदलने के लिए सिर्फ़ router बदलता है, nodes नहीं।

**Amazon AI**: router "refund > 5000" को manager approval node भेजता है, बाकी auto refund।

---

## 💻 Code Example — Basic
```python
# Basic: a mini graph runner showing fixed and conditional edges (pure Python, offline)
from typing import Any, Callable                           # typing

START, END = "__start__", "__end__"                        # same idea as LangGraph markers

State = dict[str, Any]
nodes: dict[str, Callable[[State], State]] = {
    "classify":     lambda s: {"confidence": 0.62, "hs_code": "851830"},
    "retrieve_more": lambda s: {"confidence": s["confidence"] + 0.3, "tries": s.get("tries", 0) + 1},
    "auto_approve": lambda s: {"status": "approved"},
    "human_review": lambda s: {"status": "needs_review"},
}

def router(s: State) -> str:
    """Conditional edge: decide the next node from state."""
    if s["confidence"] >= 0.85:
        return "auto_approve"
    if s["confidence"] >= 0.5 and s.get("tries", 0) < 2:   # allow limited loop-back
        return "retrieve_more"
    return "human_review"

fixed_edges: dict[str, str] = {START: "classify", "auto_approve": END, "human_review": END}
conditional: dict[str, Callable[[State], str]] = {"classify": router, "retrieve_more": router}

def run(state: State, max_steps: int = 10) -> State:
    current = fixed_edges[START]
    for _ in range(max_steps):                              # guard like recursion_limit
        state.update(nodes[current](state))                 # run node, merge update
        print(f"ran {current:14} state={state}")
        nxt = conditional[current](state) if current in conditional else fixed_edges[current]
        if nxt == END:
            return state
        current = nxt
    raise RuntimeError("step limit hit")

print(run({"product_text": "wireless earbuds"}))
```

## 💻 Code Example — Advanced
```python
# Production: LangGraph conditional edges with Literal routing, loop guard, parallel fan-out, async
import asyncio                                              # async runtime
import operator                                             # reducer
from typing import Annotated, Any, Literal, TypedDict       # typing
from langgraph.graph import StateGraph, START, END          # pip install langgraph

class State(TypedDict, total=False):
    product_text: str
    confidence: float
    hs_code: str | None
    tries: int
    status: str
    notes: Annotated[list[str], operator.add]               # parallel branches append safely

async def classify(state: State) -> dict[str, Any]:
    await asyncio.sleep(0)
    return {"confidence": 0.62, "hs_code": "851830"}

async def retrieve_more(state: State) -> dict[str, Any]:
    return {"confidence": state.get("confidence", 0) + 0.3, "tries": state.get("tries", 0) + 1}

async def auto_approve(state: State) -> dict[str, Any]:
    return {"status": "approved"}

async def human_review(state: State) -> dict[str, Any]:
    return {"status": "needs_review"}

def route_after_classify(state: State) -> Literal["auto_approve", "retrieve_more", "human_review"]:
    """Router with Literal return type: LangGraph can draw edges from it without a mapping dict."""
    conf = state.get("confidence", 0.0)
    if conf >= 0.85:
        return "auto_approve"
    if conf >= 0.5 and state.get("tries", 0) < 2:           # loop guard in the router itself
        return "retrieve_more"
    return "human_review"

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("retrieve_more", retrieve_more)
builder.add_node("auto_approve", auto_approve)
builder.add_node("human_review", human_review)

builder.add_edge(START, "classify")                         # normal edge: entry
builder.add_conditional_edges("classify", route_after_classify)        # conditional edge
builder.add_conditional_edges("retrieve_more", route_after_classify)   # loop back through the router
builder.add_edge("auto_approve", END)
builder.add_edge("human_review", END)
graph = builder.compile()

async def main() -> None:
    try:
        out = await graph.ainvoke({"product_text": "wireless earbuds"}, {"recursion_limit": 15})
        print(out)       # classify(0.62) -> retrieve_more(0.92) -> auto_approve
    except Exception as exc:                                # e.g. GraphRecursionError
        print("graph failed:", type(exc).__name__)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                 # framework
from pydantic import BaseModel

app = FastAPI()

class Req(BaseModel):
    product_text: str

@app.post("/classify")
async def classify_route(req: Req) -> dict[str, Any]:
    out = await graph.ainvoke({"product_text": req.product_text}, {"recursion_limit": 15})
    # The path the graph took is visible in state, so the API can tell clients what happened
    return {"status": out.get("status"), "hs_code": out.get("hs_code"), "confidence": out.get("confidence")}
```

---

## 🔗 LangChain / LangGraph Connection
The classic agent loop is two edges: `agent -> (conditional) tools or END`, and `tools -> agent`. LangGraph ships `tools_condition` for the conditional part: it returns `"tools"` if the last AIMessage has tool calls, else `END`.

```python
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# builder = StateGraph(MessagesState)
# builder.add_node("agent", call_model)
# builder.add_node("tools", ToolNode(tools))
# builder.add_edge(START, "agent")
# builder.add_conditional_edges("agent", tools_condition)   # "tools" or END
# builder.add_edge("tools", "agent")                         # loop back
```

Also: `Send` objects return from a conditional edge to fan out work in parallel (map-reduce), and a node may return `Command(goto="node", update={...})` to route and update state together.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A loop with no exit guard (the router can always choose the loop)
✅ Correct: Count tries in state and cap them, plus set `recursion_limit`.

```python
# Wrong
def router(s): return "retrieve_more" if s["confidence"] < 0.85 else "auto_approve"
# Right
def router(s):
    if s["confidence"] >= 0.85: return "auto_approve"
    return "retrieve_more" if s.get("tries", 0) < 2 else "human_review"
```

❌ Mistake 2: Router returns a label that does not exist
✅ Correct: Use `Literal` types or a mapping dict, and test every branch.

```python
# Wrong
def router(s): return "manual"            # no such node -> runtime error
# Right
def router(s) -> Literal["auto_approve", "human_review"]:
    return "human_review"
```

---

## 🧠 Tricky Interview Question
**Q**: "A node has two normal edges leaving it (`a -> b` and `a -> c`). Is that a branch (either b or c)? What if you want an either/or?"

**Answer**: Two normal edges from one node means a fan-out: BOTH b and c run in the next superstep (in parallel). It is not an if/else. For either/or, use `add_conditional_edges` with a router returning one target. Because b and c may write the same state key, the key needs a reducer, and if a later node depends on both, LangGraph waits for all incoming branches in that superstep (use `add_edge(["b","c"], "join")` to wait for both explicitly).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `add_edge` and `add_conditional_edges`?
A1: `add_edge` is a fixed route. `add_conditional_edges` calls a function on the state to choose the next node(s) at run time.

Q2: What are START and END?
A2: Special nodes: START is the graph entry (connect it to the first node); END marks the finish.

Q3: How does a ReAct agent loop use edges?
A3: `agent -> tools_condition -> tools or END`, then `tools -> agent`. The loop continues until the model makes no tool calls.

Q4: How do you prevent infinite loops?
A4: Count iterations in state and branch away after a limit, and set `recursion_limit` in the config; catch `GraphRecursionError`.

Q5: (Hard) How would you implement parallel research with a join?
A5: A conditional edge returns multiple `Send("research", {...})` objects (one per sub-question); each run writes results into a list key with an `operator.add` reducer; a following node (the join) runs after all finish and summarises. Control concurrency and cost with a cap on the number of Sends.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Branching, looping or approval flows
- You want visible, testable control flow

❌ Avoid when:
- A strictly linear 2-step chain (plain LCEL `|` is simpler)
- Routing logic needs the LLM itself; keep router functions cheap and deterministic where you can

---

## 📊 Visual Diagram
```
 START
   |
 [classify]
   |  (conditional edge: router(state))
   +--- conf >= 0.85 ----------------> [auto_approve] ---> END
   +--- 0.5..0.85 and tries < 2 -----> [retrieve_more] --+
   |                                                      |
   |       <-----------(back to router)-------------------+
   +--- otherwise --------------------> [human_review] ---> END
```

---

## 💰 Cost Impact
- Edges are free (plain Python), but they decide how many LLM nodes run. A loop-back edge multiplies tokens by the number of passes.
- Prefer deterministic routers (thresholds, flags) over an LLM router; an LLM router adds a paid call per decision.
- Put cheap checks first (cache hit, rules) to skip expensive nodes, cap loops (2-3 passes), and route low-value cases to a smaller model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Edge | Connection between nodes | Nodes के बीच कड़ी |
| Conditional edge | Route chosen by function | Function द्वारा चुना गया रास्ता |
| Router | Function returning next node | अगला node बताने वाला function |
| START / END | Entry / exit markers | शुरुआत / अंत के markers |
| Fan-out | One node to many parallel nodes | एक से कई parallel nodes |
| tools_condition | Prebuilt tools-or-end router | Tools या END चुनने वाला router |

---

## ⚡ 3-Line Summary
English: Edges connect nodes; normal edges are fixed, conditional edges use a router function on the state. Loops need a guard (tries counter and recursion_limit). Deterministic routers keep both cost and behaviour predictable.
Hindi: Edges nodes को जोड़ते हैं; normal edges तय होते हैं, conditional edges state पर router function चलाते हैं। Loops में guard चाहिए (tries counter और recursion_limit)। Deterministic routers cost और व्यवहार दोनों अनुमान योग्य रखते हैं।

---

## ➡️ Next Topic
**322. Conditional Edges (deep dive)** — routing patterns, `Command`, and `Send` for dynamic fan-out.
