---

# 332. Subgraphs
# हिंदी में: Subgraphs (Graph के अंदर Graph)

---

## 🔵 Simple Definition (English)
A subgraph is a compiled LangGraph graph used as a node inside another (parent) graph. It hides a group of nodes behind one name, can be tested alone, and can be reused in many parents. There are two ways to connect it: (1) pass the compiled subgraph directly to `add_node` when parent and child share state keys, or (2) call it from a normal function node when the schemas are different, converting state in and out.

## 🔵 सरल परिभाषा (Hindi)
Subgraph एक compiled LangGraph graph है जो दूसरे (parent) graph के अंदर node की तरह use होता है। यह nodes के समूह को एक नाम के पीछे छुपाता है, अकेले test हो सकता है, और कई parents में दोबारा use हो सकता है। जोड़ने के दो तरीके हैं: (1) parent और child की state keys साझा हों तो compiled subgraph को सीधे `add_node` में दो, (2) schemas अलग हों तो normal function node से call करो और state को अंदर-बाहर convert करो।

---

## 🔴 Problem it Solves
One big graph with 30 nodes is hard to read, test and share between teams. The same "classify then validate" logic is copied into three workflows. State keys of different teams collide. Subgraphs give modularity: each team owns a graph with a clear input/output, and the parent only wires them together.

## 🔴 यह क्यों बना? (Hindi)
30 nodes वाला एक बड़ा graph पढ़ना, test करना और teams में share करना मुश्किल है। वही "classify फिर validate" logic तीन workflows में copy हो जाता है। अलग teams की state keys टकराती हैं। Subgraphs modularity देते हैं: हर team का graph साफ़ input/output के साथ होता है और parent सिर्फ़ उन्हें जोड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build the child: StateGraph(ChildState) ... .compile()    (no checkpointer needed)
Step 2 → Case A (shared keys): parent.add_node("classify", child_compiled)
Step 3 → Case B (different schema): def call_child(parent_state): map in -> child.invoke -> map out
Step 4 → Compile ONLY the parent with the checkpointer; it is passed down to the child automatically
Step 5 → Run: parent reaches node "classify" -> runs the whole child graph inside
Step 6 → Child returns its final state; keys that exist in the parent schema are written to the parent
Step 7 → Streaming: stream(..., subgraphs=True) shows events with a namespace like ("classify:<id>",)
Step 8 → interrupt() inside the child pauses the whole run; resume works through the parent thread_id
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Child बनाओ: StateGraph(ChildState) ... .compile()    (checkpointer ज़रूरी नहीं)
Step 2 → Case A (shared keys): parent.add_node("classify", child_compiled)
Step 3 → Case B (अलग schema): def call_child(parent_state): input map -> child.invoke -> output map
Step 4 → सिर्फ़ parent को checkpointer के साथ compile करो; वह child तक अपने आप पहुँचता है
Step 5 → Run: parent "classify" node पर पहुँचकर अंदर पूरा child graph चलाता है
Step 6 → Child अपनी final state लौटाता है; जो keys parent schema में हैं वे parent में लिखी जाती हैं
Step 7 → Streaming: stream(..., subgraphs=True) namespace जैसे ("classify:<id>",) के साथ events दिखाता है
Step 8 → Child के अंदर interrupt() पूरे run को रोकता है; resume parent के thread_id से होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three subgraphs: `classification_sg` (retrieve similar codes, LLM picks, validate format), `valuation_sg` (customs value, currency conversion), `compliance_sg` (sanctions, licences). The parent graph `shipment_flow` runs classification, then valuation and compliance in parallel, then a final report node. The classification team can test and deploy their subgraph independently, and the export-tariff workflow reuses the same subgraph.

**Amazon-style**: A "returns" subgraph (check policy, generate label, refund) reused by order-support and seller-support parent graphs.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन subgraphs: `classification_sg` (मिलते-जुलते codes खोजो, LLM चुने, format validate), `valuation_sg` (customs value, currency conversion), `compliance_sg` (sanctions, licences)। Parent graph `shipment_flow` पहले classification, फिर valuation और compliance parallel, फिर final report node चलाता है। Classification team अपना subgraph अलग test और deploy कर सकती है, और export-tariff workflow वही subgraph दोबारा use करता है।

**Amazon-style**: "Returns" subgraph (policy जाँच, label बनाना, refund) order-support और seller-support दोनों parent graphs में दोबारा use होता है।

---

## 💻 Code Example — Basic
```python
# Basic: a compiled subgraph used as a node (shared keys). Offline.
from typing import TypedDict                             # type hints

from langgraph.checkpoint.memory import MemorySaver      # parent-level memory
from langgraph.graph import END, START, StateGraph      # graph API


class ClassState(TypedDict, total=False):                # child schema (keys also exist in parent)
    product: str                                         # input
    hs_code: str                                         # output 1
    reason: str                                          # output 2


def retrieve(state: ClassState) -> dict:                 # child node 1
    return {"hs_code": "8517.13"}                        # fake retrieval + pick


def explain(state: ClassState) -> dict:                  # child node 2
    return {"reason": f"{state['product']} matches {state['hs_code']}"}   # fake explanation


child_builder = StateGraph(ClassState)                   # build the CHILD graph
child_builder.add_node("retrieve", retrieve)             # node
child_builder.add_node("explain", explain)               # node
child_builder.add_edge(START, "retrieve")                # wiring
child_builder.add_edge("retrieve", "explain")
child_builder.add_edge("explain", END)
classification_sg = child_builder.compile()              # compiled child (no checkpointer here)


class ParentState(TypedDict, total=False):               # parent schema (superset of child keys)
    product: str                                         # shared key
    hs_code: str                                         # shared key
    reason: str                                          # shared key
    report: str                                          # parent-only key


def report(state: ParentState) -> dict:                  # parent node after the child
    return {"report": f"[{state['hs_code']}] {state['reason']}"}   # final text


parent = StateGraph(ParentState)                         # build the PARENT graph
parent.add_node("classification", classification_sg)    # compiled child graph IS the node
parent.add_node("report", report)                        # normal node
parent.add_edge(START, "classification")                 # wiring
parent.add_edge("classification", "report")
parent.add_edge("report", END)
app = parent.compile(checkpointer=MemorySaver())         # only the parent needs the checkpointer

out = app.invoke({"product": "smartphone"}, {"configurable": {"thread_id": "t1"}})   # run
print(out["report"])                                     # [8517.13] smartphone matches 8517.13
```

## 💻 Code Example — Advanced
```python
# Production style: DIFFERENT schemas, wrapper node with mapping, async, error handling, streaming
import asyncio                                           # async runtime
import logging                                           # logs
from typing import Any, TypedDict                        # type hints

from langgraph.graph import END, START, StateGraph      # graph API

logger = logging.getLogger("tariff.subgraph")            # logger


# ---- Child graph with its OWN private schema (input/output separated) ----
class ValuationIn(TypedDict):                            # what the child accepts
    amount: float                                        # invoice amount
    currency: str                                        # currency code


class ValuationOut(TypedDict):                           # what the child returns
    value_inr: float                                     # customs value in INR


class ValuationState(ValuationIn, ValuationOut, total=False):   # full internal state
    rate: float                                          # private working key (not exposed)


async def fetch_rate(state: ValuationState) -> dict[str, Any]:   # child node 1
    await asyncio.sleep(0)                               # placeholder for a real FX API call
    rates = {"USD": 83.0, "EUR": 90.0, "INR": 1.0}       # fake rates
    if state["currency"] not in rates:                   # validate
        raise ValueError(f"unsupported currency {state['currency']}")   # explicit error
    return {"rate": rates[state["currency"]]}            # store private rate


async def convert(state: ValuationState) -> dict[str, Any]:   # child node 2
    return {"value_inr": round(state["amount"] * state["rate"], 2)}   # compute


vb = StateGraph(ValuationState, input_schema=ValuationIn, output_schema=ValuationOut)   # typed IO
vb.add_node("fetch_rate", fetch_rate)                    # node
vb.add_node("convert", convert)                          # node
vb.add_edge(START, "fetch_rate")                         # wiring
vb.add_edge("fetch_rate", "convert")
vb.add_edge("convert", END)
valuation_sg = vb.compile()                              # compiled child


# ---- Parent graph with a different schema ----
class ShipmentState(TypedDict, total=False):             # parent schema
    invoice_amount: float                                # parent naming
    invoice_currency: str                                # parent naming
    customs_value_inr: float                             # result
    error: str                                           # error info


async def call_valuation(state: ShipmentState) -> dict[str, Any]:   # WRAPPER node: maps state in/out
    try:                                                 # a failing child must not crash the parent
        res = await valuation_sg.ainvoke({               # map parent -> child input
            "amount": state["invoice_amount"], "currency": state["invoice_currency"]})
        return {"customs_value_inr": res["value_inr"]}   # map child output -> parent key
    except ValueError as exc:                            # business error from the child
        logger.warning("valuation failed: %s", exc)      # log
        return {"error": str(exc)}                       # keep the flow alive with an error flag


pb = StateGraph(ShipmentState)                           # parent builder
pb.add_node("valuation", call_valuation)                 # wrapper node
pb.add_edge(START, "valuation")                          # wiring
pb.add_edge("valuation", END)
app = pb.compile()                                       # compile parent


async def main() -> None:                                # demo
    ok = await app.ainvoke({"invoice_amount": 1000.0, "invoice_currency": "USD"})
    print(ok["customs_value_inr"])                       # 83000.0
    bad = await app.ainvoke({"invoice_amount": 5.0, "invoice_currency": "XYZ"})
    print(bad["error"])                                  # unsupported currency XYZ


if __name__ == "__main__":                               # entry
    asyncio.run(main())                                  # run
```

---

## 🟠 FastAPI Integration
Compile subgraphs and the parent at import time (they are immutable and safe to share). Expose the parent through the API and optionally expose each subgraph on its own route for testing. With `subgraphs=True` you can stream progress of inner steps.

```python
# FastAPI: parent graph with a subgraph, plus a streaming progress endpoint
import json                                                     # NDJSON
from typing import TypedDict                                    # type hints

from fastapi import FastAPI                                     # web framework
from fastapi.responses import StreamingResponse                 # streaming
from langgraph.graph import END, START, StateGraph            # graph API
from pydantic import BaseModel                                  # models


class S(TypedDict, total=False):                                # shared state
    product: str                                                # input
    hs_code: str                                                # output
    report: str                                                 # parent output


def pick(s: S) -> dict: return {"hs_code": "8517.13"}           # child node
cb = StateGraph(S)                                              # child graph
cb.add_node("pick", pick)
cb.add_edge(START, "pick")
cb.add_edge("pick", END)
child = cb.compile()                                            # compiled child


def report(s: S) -> dict: return {"report": f"{s['product']} -> {s['hs_code']}"}   # parent node
pb = StateGraph(S)                                              # parent graph
pb.add_node("child", child)                                     # subgraph as node
pb.add_node("report", report)
pb.add_edge(START, "child")
pb.add_edge("child", "report")
pb.add_edge("report", END)
graph = pb.compile()                                            # compile once at import

app = FastAPI(title="Subgraph API")                             # app


class In(BaseModel):                                            # body
    product: str                                                # text


@app.post("/run")                                               # normal call
async def run(body: In) -> dict[str, str]:                       # handler
    out = await graph.ainvoke({"product": body.product})        # run
    return {"report": out["report"]}                            # response


@app.post("/run/stream")                                        # progress stream
async def run_stream(body: In) -> StreamingResponse:             # handler
    async def gen():                                            # generator
        async for ns, chunk in graph.astream({"product": body.product},
                                             stream_mode="updates", subgraphs=True):
            yield json.dumps({"path": list(ns), "update": chunk}) + "\n"   # ns shows nesting
    return StreamingResponse(gen(), media_type="application/x-ndjson")   # stream
```

---

## 🔗 LangChain / LangGraph Connection
Subgraphs are the base for multi-agent systems: each agent is a graph (often `create_react_agent`) used as a node of a supervisor graph. A compiled graph is itself a LangChain `Runnable`, so it also works inside LCEL chains and can be called with `invoke/ainvoke/stream`. In LangGraph Studio subgraphs can be expanded ("x-ray") to see inner nodes: `graph.get_graph(xray=True)`.

```python
# Use a prebuilt agent as a subgraph node (needs API key to run)
from langchain_openai import ChatOpenAI                      # model
from langgraph.prebuilt import create_react_agent            # prebuilt compiled graph

researcher = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[])   # compiled graph
# parent.add_node("researcher", researcher)   # works because "messages" is a shared key
print(researcher.get_graph(xray=True).draw_mermaid()[:60])   # inspect inner structure
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a subgraph with a different schema directly to `add_node`
✅ Correct: no shared keys means no data flows. Use a wrapper function that maps state.

```python
# Wrong — parent keys: invoice_amount; child keys: amount (no overlap, child gets nothing)
parent.add_node("valuation", valuation_sg)

# Right
async def call_valuation(state):
    res = await valuation_sg.ainvoke({"amount": state["invoice_amount"], "currency": "USD"})
    return {"customs_value_inr": res["value_inr"]}
parent.add_node("valuation", call_valuation)
```

❌ Mistake 2: Compiling the child with its own checkpointer too
✅ Correct: let the parent's checkpointer propagate. Separate checkpointers can break interrupts and resume.

```python
# Wrong
child = child_builder.compile(checkpointer=MemorySaver())
# Right
child = child_builder.compile()                 # parent passes its checkpointer down
app = parent_builder.compile(checkpointer=MemorySaver())
```

❌ Mistake 3: Reducer conflicts between parent and child keys of the same name
✅ Correct: use the same reducer annotation (e.g. `operator.add`) on the shared key in both schemas.

---

## 🧠 Tricky Interview Question

**Q**: "A subgraph with `interrupt()` is called from a wrapper function (`child.invoke(...)` inside a parent node). On resume the child restarts from its first node, not from the interrupt. Why, and how to avoid this?"

**Answer**: When you call the child manually inside a function, the child is just a function call; the parent node is the unit LangGraph checkpoints. On resume the parent node runs again from the top and calls `child.invoke` again, and the child starts a fresh run (unless it has its own persistent thread). When the compiled subgraph is added directly with `add_node` (or called with the parent's config so it inherits the checkpointer), LangGraph tracks the child's checkpoints under a namespace and can resume inside it. Fix: add the subgraph as a node when schemas allow, or add a small transform node before and after it (instead of a wrapper), or pass the same `config` into the child call so it shares the parent's thread context. Also keep the code before the child call idempotent.

---

## ⚫ Interview Questions + Answers

Q1: What is a subgraph? (Easy)
A1: A compiled graph used as a node in another graph, for modularity and reuse.

Q2: How do you attach a subgraph? (Easy)
A2: If parent and child share state keys, `parent.add_node("name", compiled_child)`. If schemas differ, write a function node that converts parent state to child input, calls the child, and converts the output back.

Q3: Which graph gets the checkpointer? (Medium)
A3: Only the top-level parent in `compile(checkpointer=...)`. It is automatically propagated to subgraphs, so they appear as namespaced checkpoints and support interrupts and time travel.

Q4: How do you see what happens inside a subgraph while streaming? (Medium)
A4: Pass `subgraphs=True` to `stream`/`astream`. Each event then comes as `(namespace, chunk)` where namespace such as `("classification:<task_id>",)` tells you which subgraph produced it.

Q5: When should you NOT split into subgraphs, and how do you keep them maintainable in a large team? (Hard)
A5: Do not split tiny graphs; overhead and indirection hurt readability. Split when a part has a clear contract, separate ownership, reuse or independent tests. Keep contracts explicit with `input_schema`/`output_schema`, version subgraphs as Python packages, avoid hidden shared keys, write unit tests per subgraph with fake LLMs, and set tracing metadata (tags, run names) so LangSmith traces show the nesting. Watch checkpoint size, because every subgraph state is stored.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A group of nodes has one clear job and is reused
- Different teams own different parts
- You build multi-agent systems (one subgraph per agent)

❌ Avoid when:
- The graph has fewer than about 6 nodes and no reuse
- Parent and child need constant two-way state sharing
- You cannot define clear input and output contracts

---

## 📊 Visual Diagram
```
 PARENT: shipment_flow (checkpointer lives here)
 ┌──────────────────────────────────────────────────────────┐
 │  START ─► [ classification ] ─► [ report ] ─► END        │
 │                │                                          │
 │   ┌────────────▼─────────────┐                           │
 │   │ SUBGRAPH classification  │  (own nodes, own schema)  │
 │   │  START ─► retrieve ─►    │                           │
 │   │           explain ─► END │                           │
 │   └──────────────────────────┘                           │
 └──────────────────────────────────────────────────────────┘
  shared keys flow in/out automatically; different keys need a wrapper node
```

---

## 💰 Cost Impact
Subgraphs themselves add no tokens; cost equals the sum of all LLM nodes inside. Hidden costs: (1) bigger checkpoints because each level stores state, (2) duplicated context if every subgraph re-sends the same long documents, (3) deeper traces in LangSmith. Optimise: pass only the needed keys with `input_schema`, store large documents once in the parent (or in an external store) and give subgraphs IDs, and use a cheap model inside classification subgraphs and a stronger model only in the final report.

Example: classification (900 in + 150 out tokens) plus validation (400 in + 50 out) on gpt-4o-mini is about $0.00026 per shipment line.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Subgraph | Graph used as a node | Node की तरह use होने वाला graph |
| Parent graph | Graph that contains subgraphs | बड़ा graph जिसमें subgraphs हैं |
| Shared keys | State keys present in both schemas | दोनों schemas की common keys |
| Wrapper node | Function that maps state in/out | State convert करने वाला function |
| input_schema / output_schema | Public contract of a graph | Graph का public input/output |
| Namespace | Path of a subgraph in events | Events में subgraph का path |
| x-ray | Draw inner subgraph structure | अंदर की structure दिखाना |

---

## ⚡ 3-Line Summary
English: A subgraph is a compiled graph used as a node, giving modularity and reuse. Add it directly when state keys are shared, or use a wrapper node to map state when schemas differ. Only the parent gets the checkpointer, and `subgraphs=True` streams inner events.
Hindi: Subgraph compiled graph है जो node की तरह use होता है, जिससे modularity और reuse मिलता है। State keys साझा हों तो सीधे add करो, schemas अलग हों तो wrapper node से state map करो। Checkpointer सिर्फ़ parent को मिलता है, और `subgraphs=True` से अंदर के events stream होते हैं।

---

## ➡️ Next Topic
**333. Multi-Agent with LangGraph** — use several specialised agents (each often a subgraph) that cooperate on one task.
