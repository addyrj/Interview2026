---

# 320. Nodes in LangGraph
# हिंदी में: LangGraph में Nodes

---

## 🔵 Simple Definition (English)
A node is a function (sync or async) in a LangGraph graph that receives the current state and returns a partial state update. It is where real work happens: calling an LLM, running a tool, querying a database, or applying business rules. You register it with `graph.add_node("name", fn)`.

## 🔵 सरल परिभाषा (Hindi)
Node LangGraph graph का एक function (sync या async) है जो current state लेता है और partial state update लौटाता है। असली काम यहीं होता है: LLM call, tool चलाना, database query, या business rules। इसे `graph.add_node("name", fn)` से register करते हैं।

---

## 🔴 Problem it Solves
Big agent scripts become one huge function that is hard to test, retry or resume. Nodes split the workflow into small, named, single-purpose steps. Each can be unit tested, retried on its own, traced in LangSmith and checkpointed after it runs.

## 🔴 यह क्यों बना? (Hindi)
बड़े agent scripts एक विशाल function बन जाते हैं जिसे test, retry या resume करना कठिन है। Nodes workflow को छोटे, नामित, single-purpose steps में बाँटते हैं। हर node अलग से unit test, retry, LangSmith में trace और run के बाद checkpoint हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function: def node(state: State) -> dict
Step 2 → Optionally accept config: def node(state, config: RunnableConfig)
Step 3 → builder.add_node("classify", node)  (name defaults to function name)
Step 4 → Connect with edges (add_edge / add_conditional_edges)
Step 5 → At run time LangGraph passes the current state into the node
Step 6 → Node returns {"key": value} (only keys it changes)
Step 7 → LangGraph applies reducers, checkpoints, then picks the next node
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → function लिखो: def node(state: State) -> dict
Step 2 → चाहें तो config लो: def node(state, config: RunnableConfig)
Step 3 → builder.add_node("classify", node)  (नाम न दें तो function का नाम)
Step 4 → Edges से जोड़ो (add_edge / add_conditional_edges)
Step 5 → Run में LangGraph current state node को देता है
Step 6 → Node {"key": value} लौटाता है (सिर्फ़ बदली keys)
Step 7 → LangGraph reducers लगाता है, checkpoint करता है, अगला node चुनता है
```

---

## 🟡 Real World Example
**Tariff Classification System** nodes: `normalize_text` (clean product description), `retrieve_candidates` (vector search), `llm_classify` (LLM picks HS code with reasoning), `validate_code` (check code exists in the official schedule), `human_review` (pause for officer). Each is small. If `validate_code` fails you can fix and re-test only that node.

**Amazon AI**: nodes `detect_intent`, `lookup_order`, `draft_reply`, `safety_check`.

## 🟡 Real Example Hindi mein
**Tariff System** के nodes: `normalize_text` (product description साफ़ करना), `retrieve_candidates` (vector search), `llm_classify` (LLM reasoning के साथ HS code चुनता है), `validate_code` (code official schedule में है या नहीं), `human_review` (officer के लिए pause)। हर node छोटा है। `validate_code` fail हो तो सिर्फ़ उसे ठीक करके test करें।

**Amazon AI**: nodes `detect_intent`, `lookup_order`, `draft_reply`, `safety_check`।

---

## 💻 Code Example — Basic
```python
# Basic: nodes are just functions state -> partial update; run a tiny pipeline by hand (offline)
from typing import Any, Callable, TypedDict               # typing

class State(TypedDict, total=False):                      # total=False: keys may be missing early on
    product_text: str
    cleaned: str
    hs_code: str
    valid: bool

def normalize_text(state: State) -> dict[str, Any]:
    """Node 1: clean the text."""
    return {"cleaned": " ".join(state["product_text"].lower().split())}

def classify(state: State) -> dict[str, Any]:
    """Node 2: pretend LLM classification."""
    return {"hs_code": "851830" if "earbuds" in state["cleaned"] else "999999"}

def validate_code(state: State) -> dict[str, Any]:
    """Node 3: check against the official list."""
    official = {"851830", "640399"}
    return {"valid": state["hs_code"] in official}

NODES: list[Callable[[State], dict[str, Any]]] = [normalize_text, classify, validate_code]

state: State = {"product_text": "  Wireless   EARBUDS "}
for node in NODES:                                        # LangGraph does this loop + merge for you
    try:
        update = node(state)                              # node returns only what it changes
    except KeyError as exc:                               # a missing key = bug in node ordering
        print(f"{node.__name__} failed: missing {exc}")
        break
    state.update(update)                                  # merge (no reducers here)
    print(f"{node.__name__:15} -> {update}")
print(state)
```

## 💻 Code Example — Advanced
```python
# Production: sync + async nodes, config access, retry policy, error-as-state, LLM node
import asyncio                                            # async runtime
import logging                                            # logs
from typing import Annotated, Any, TypedDict              # typing
import operator                                           # reducer
from langchain_core.runnables import RunnableConfig       # per-run config
from langchain_openai import ChatOpenAI                   # LLM
from langgraph.graph import StateGraph, START, END        # graph
from langgraph.types import RetryPolicy                   # retries per node

logger = logging.getLogger("nodes")

class State(TypedDict, total=False):
    product_text: str
    candidates: list[str]
    hs_code: str | None
    errors: Annotated[list[str], operator.add]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def retrieve_candidates(state: State) -> dict[str, Any]:
    """Async I/O node: may fail transiently, so we give it a RetryPolicy below."""
    await asyncio.sleep(0)
    return {"candidates": ["851830", "851762"]}

async def llm_classify(state: State, config: RunnableConfig) -> dict[str, Any]:
    """LLM node: reads per-request settings from config['configurable']."""
    tenant = (config.get("configurable") or {}).get("tenant_id", "default")
    prompt = (f"Product: {state['product_text']}\nCandidates: {state['candidates']}\n"
              "Reply with ONLY the best HS code.")
    try:
        msg = await llm.ainvoke(prompt, config=config)      # pass config so tracing/callbacks link up
    except Exception as exc:                                # keep the graph alive; record the error
        logger.exception("llm_classify failed for tenant=%s", tenant)
        return {"hs_code": None, "errors": [f"llm_classify: {exc}"]}
    code = str(msg.content).strip()
    return {"hs_code": code if code in state["candidates"] else None}   # reject hallucinated codes

def finalize(state: State) -> dict[str, Any]:
    """Sync node is fine for pure CPU work."""
    return {} if state.get("hs_code") else {"errors": ["no valid HS code"]}

builder = StateGraph(State)
builder.add_node("retrieve", retrieve_candidates, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node("classify", llm_classify)
builder.add_node("finalize", finalize)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "classify")
builder.add_edge("classify", "finalize")
builder.add_edge("finalize", END)
graph = builder.compile()

if __name__ == "__main__":
    out = asyncio.run(graph.ainvoke({"product_text": "wireless earbuds"},
                                    {"configurable": {"tenant_id": "acme"}}))   # needs OPENAI_API_KEY
    print(out)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                               # framework
from pydantic import BaseModel

app = FastAPI()

class Req(BaseModel):
    product_text: str
    tenant_id: str = "default"

@app.post("/classify")
async def classify_route(req: Req) -> dict[str, Any]:
    out = await graph.ainvoke({"product_text": req.product_text},
                              {"configurable": {"tenant_id": req.tenant_id}})   # per-request config to nodes
    status = "ok" if out.get("hs_code") else "needs_review"   # errors-as-state become an API status
    return {"status": status, "hs_code": out.get("hs_code"), "errors": out.get("errors", [])}
```

---

## 🔗 LangChain / LangGraph Connection
A node can be any callable or a LangChain Runnable (a chain `prompt | llm | parser` can be added directly as a node). Prebuilt nodes: `ToolNode` runs tool calls found in the last AIMessage. Node return values can also be a `Command(update=..., goto=...)` to update state and route in one step.

```python
from langgraph.prebuilt import ToolNode
tool_node = ToolNode([])      # pass your @tool functions here
# builder.add_node("tools", tool_node)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning the whole state or non-dict values
✅ Correct: Return only changed keys as a dict.

```python
# Wrong
def node(state): return "851830"
# Right
def node(state): return {"hs_code": "851830"}
```

❌ Mistake 2: Raising exceptions for expected failures, killing the whole run
✅ Correct: Catch, write the error into state, and let a router decide.

```python
# Wrong
def validate(state): raise ValueError("bad code")
# Right
def validate(state): return {"errors": ["bad code"], "valid": False}
```

---

## 🧠 Tricky Interview Question
**Q**: "Your graph is retried after a crash and the 'send_email' node sends the email twice. How do nodes and checkpoints relate to this?"

**Answer**: Checkpoints are saved after each node (superstep). If the process crashes after the email API call but before the checkpoint is written, on resume the node runs again, so side effects can repeat. Make side-effect nodes idempotent: use an idempotency key (for example order id) with the email provider, or record "email_sent" in a database before and check it, and put the side effect in its own node so only that small step is retried.

---

## ⚫ Interview Questions + Answers

Q1: What does a node receive and return?
A1: It receives the current state and returns a dict of updates for some keys.

Q2: Can nodes be async?
A2: Yes. Use `async def` and `graph.ainvoke`/`astream`. Sync nodes work too.

Q3: How do you give a node access to request-specific settings?
A3: Add a `config: RunnableConfig` parameter and read `config["configurable"]`.

Q4: How do you retry a flaky node?
A4: `add_node("name", fn, retry_policy=RetryPolicy(max_attempts=3))`. It retries on transient exceptions with backoff.

Q5: (Hard) How do you decide node granularity?
A5: One node per unit that you want to retry, trace, test, pause (human-in-the-loop) or run in parallel independently. Too coarse hides failures and loses resumability; too fine adds overhead and checkpoint cost. Isolate side effects and LLM calls into their own nodes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Each step has a distinct responsibility or failure mode
- You need checkpointing, tracing or human review between steps

❌ Avoid when:
- Splitting trivial one-liners into separate nodes (adds overhead)

---

## 📊 Visual Diagram
```
 START
   |
 [normalize_text] --{cleaned}--> [retrieve_candidates] --{candidates}-->
 [llm_classify]   --{hs_code}--> [validate_code]       --{valid}-->  END
     each box:  fn(state) -> partial update   (checkpoint after each)
```

---

## 💰 Cost Impact
- Only LLM nodes consume tokens; keep non-LLM logic (cleaning, validation, routing) in plain Python nodes so you do not pay for tokens there.
- Use a cheap model in simple nodes and a stronger one only in the hard node.
- Build each node's prompt from only the needed state keys. Retries on LLM nodes repeat their token cost, so retry only transient errors.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Node | Function doing one step | एक step करने वाला function |
| add_node | Register node in graph | Graph में node जोड़ना |
| Partial update | Dict of changed keys | बदली हुई keys का dict |
| RetryPolicy | Auto retry settings | अपने-आप retry की सेटिंग |
| RunnableConfig | Per-run settings | Run की अलग सेटिंग्स |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |

---

## ⚡ 3-Line Summary
English: A node is a function from state to partial state update, the unit of work in LangGraph. Keep nodes small, make side effects idempotent, and record expected errors in state. Only LLM nodes cost tokens.
Hindi: Node state से partial state update तक का function है, LangGraph में काम की इकाई। Nodes छोटे रखें, side effects को idempotent बनाएँ, और अपेक्षित errors state में लिखें। सिर्फ़ LLM nodes tokens खर्च करते हैं।

---

## ➡️ Next Topic
**321. Edges in LangGraph** — connecting nodes with fixed and conditional routes.
