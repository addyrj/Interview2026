---

# 323. Entry Point + END
# हिंदी में: Entry Point + END (शुरुआत और अंत)

---

## 🔵 Simple Definition (English)
Every LangGraph graph needs a place to start and a way to stop. `START` is a special virtual node: an edge from `START` to a node makes that node the entry point. `END` is a special virtual node: an edge to `END` finishes the run and returns the final state. `set_entry_point("x")` and `set_finish_point("x")` are older shortcuts for the same thing.

## 🔵 सरल परिभाषा (Hindi)
हर LangGraph graph को शुरू होने की जगह और रुकने का तरीका चाहिए। `START` एक special virtual node है: `START` से किसी node तक edge बनाने पर वह node entry point बन जाता है। `END` भी special virtual node है: `END` तक edge आने पर run खत्म होता है और final state return होती है। `set_entry_point("x")` और `set_finish_point("x")` इसी के पुराने shortcuts हैं।

---

## 🔴 Problem it Solves
A graph is just nodes and edges; the engine must know which node runs first and when the work is complete. Without explicit start/end the compiler cannot validate the graph (orphan nodes, dead ends, nodes that can never finish), and a loop could run forever. Early versions used string constants and magic names; `START`/`END` make it explicit, importable and checkable.

## 🔴 यह क्यों बना? (Hindi)
Graph सिर्फ nodes और edges हैं; engine को पता होना चाहिए कि पहले कौन सा node चलेगा और काम कब पूरा होगा। Explicit start/end के बिना compiler graph validate नहीं कर सकता (orphan nodes, dead ends, कभी खत्म न होने वाले nodes) और loop हमेशा चल सकता है। `START`/`END` इसे explicit और checkable बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → builder.add_edge(START, "first") declares the entry node
Step 2 → compile() validates: entry exists, every node is reachable, every path can reach END
Step 3 → invoke(input) writes input into state and runs the entry node
Step 4 → Each node returns a partial update; edges decide the next node
Step 5 → When an edge points to END the run stops
Step 6 → invoke returns the final state (stream yields it step by step)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → builder.add_edge(START, "first") entry node तय करता है
Step 2 → compile() check करता है: entry मौजूद है, हर node reachable है, हर path END तक पहुँच सकता है
Step 3 → invoke(input) input को state में लिखता है और entry node चलाता है
Step 4 → हर node partial update return करता है; edges अगला node तय करते हैं
Step 5 → जब edge END की तरफ जाए, run रुक जाता है
Step 6 → invoke final state return करता है (stream step-by-step देता है)
```

---

## 🟡 Real World Example
**Tariff Classification System**: START goes to `validate_input` (reject empty product text). If invalid, a conditional edge goes straight to END with an error message (a cheap early exit, zero LLM tokens). If valid, the flow continues to `classify` then `answer` then END. So the graph has two end paths. **Amazon AI**: a support bot graph starts at `detect_language`; a "spam" message ends immediately.

## 🟡 Real Example Hindi mein
**Tariff System**: START से `validate_input` चलता है (खाली product text reject)। Invalid हो तो conditional edge सीधे error message के साथ END पर जाता है (सस्ता early exit, LLM tokens शून्य)। Valid हो तो `classify` फिर `answer` फिर END। यानी graph के दो end paths हैं। **Amazon AI**: support bot `detect_language` से शुरू होता है; "spam" message तुरंत खत्म हो जाता है।

---

## 💻 Code Example — Basic
```python
# Entry point and END - runs offline (pip install langgraph)
from typing import TypedDict  # state typing

from langgraph.graph import END, START, StateGraph  # START and END are the special nodes


class State(TypedDict):  # shared state
    product: str  # input text
    result: str  # output text


def validate(state: State) -> dict[str, str]:  # first node
    ok = bool(state["product"].strip())  # empty check
    return {"result": "ok" if ok else "invalid"}  # store verdict


def answer(state: State) -> dict[str, str]:  # last node
    return {"result": f"HS code for {state['product']}: 8517.13"}  # fake answer


builder = StateGraph(State)  # create builder
builder.add_node("validate", validate)  # add node
builder.add_node("answer", answer)  # add node

builder.add_edge(START, "validate")  # modern way to set the entry point
builder.add_edge("validate", "answer")  # normal edge
builder.add_edge("answer", END)  # modern way to finish

# Older equivalent (still works):
#   builder.set_entry_point("validate")
#   builder.set_finish_point("answer")

graph = builder.compile()  # compile validates start/end wiring
print(graph.invoke({"product": "phone", "result": ""}))  # {'product': 'phone', 'result': 'HS code ...'}
```

## 💻 Code Example — Advanced
```python
# Multiple END paths, early exit, validation error handling, async
import asyncio  # async runner
from typing import Literal, TypedDict  # typing

from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # state
    product: str  # input
    error: str  # non-empty means failure
    hs_code: str  # output


async def validate(state: State) -> dict[str, str]:  # entry node
    text = state["product"].strip()  # clean input
    if len(text) < 3:  # too short to classify
        return {"error": "product text too short"}  # early failure
    return {"error": ""}  # all good


async def classify(state: State) -> dict[str, str]:  # does the real work
    await asyncio.sleep(0)  # stands in for an LLM call
    return {"hs_code": "8517.13"}  # result


def after_validate(state: State) -> Literal["classify", "__end__"]:  # router; "__end__" is the value of END
    return END if state["error"] else "classify"  # END = early exit


builder = StateGraph(State)  # builder
builder.add_node("validate", validate)  # node
builder.add_node("classify", classify)  # node
builder.add_edge(START, "validate")  # entry
builder.add_conditional_edges("validate", after_validate)  # END is a legal target of a router
builder.add_edge("classify", END)  # second way to end
graph = builder.compile()  # compile


async def run(product: str) -> State:  # helper with error handling
    try:
        return await graph.ainvoke({"product": product, "error": "", "hs_code": ""})  # run graph
    except Exception as exc:  # never leak raw stack traces to callers
        return {"product": product, "error": f"graph failed: {exc}", "hs_code": ""}


async def main() -> None:
    print(await run("x"))  # ends early at validate (no classify call)
    print(await run("smartphone"))  # reaches classify


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Map the graph's two end states to HTTP codes: success returns 200, `error` in final state returns 422. The API stays thin.

```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class In(BaseModel):  # body
    product: str


@app.post("/classify")
async def classify_endpoint(body: In) -> dict[str, str]:  # typed route
    final = await run(body.product)  # run() from the Advanced example
    if final["error"]:  # graph ended through the early-exit path
        raise HTTPException(status_code=422, detail=final["error"])  # client error
    return {"hs_code": final["hs_code"]}  # success path
```

---

## 🔗 LangChain / LangGraph Connection
`START`/`END` are LangGraph-only concepts (classic LangChain chains are linear, so they need no start/end). When a compiled graph is used as a node inside another graph (subgraph), its own `START` and `END` are the sub-graph's boundaries. `MessagesState` graphs usually end with the LLM's final `AIMessage` as the last message.

```python
from langgraph.graph import END, START, MessagesState, StateGraph  # prebuilt message state


def echo(state: MessagesState) -> dict:  # simple node
    return {"messages": [("ai", "done")]}  # add an AI message


g = StateGraph(MessagesState)  # graph with messages key
g.add_node("echo", echo)  # node
g.add_edge(START, "echo")  # entry
g.add_edge("echo", END)  # exit
print(g.compile().invoke({"messages": [("user", "hi")]})["messages"][-1].content)  # "done"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the entry edge
✅ Correct: Always connect `START` to the first node.

```python
# Wrong - compile() raises: graph must have an entrypoint
builder.add_node("validate", validate)
graph = builder.compile()

# Right
builder.add_edge(START, "validate")
graph = builder.compile()
```

❌ Mistake 2: A branch with no path to END (dead end or endless cycle)
✅ Correct: Every node must eventually reach END, including error branches.

```python
# Wrong - "human_review" has no outgoing edge, run state is undefined
builder.add_node("human_review", human_review)

# Right
builder.add_edge("human_review", END)
```

---

## 🧠 Tricky Interview Question

**Q**: "A node has no outgoing edge and is not connected to END. Does the graph stop gracefully?"

**Answer**: In current LangGraph a node with no outgoing edges simply finishes the run when it executes (nothing is scheduled next), so it may work, but this is bad practice: the drawing is ambiguous, compile-time validation cannot prove termination, and `Command(goto=...)` nodes are special because their targets are not visible as edges. Always add explicit `add_edge(node, END)` (or declare `Command[Literal[...]]` return types) so the intent is clear and graph drawings are correct. Also remember that reaching END ends only when no other parallel branches are still running.

---

## ⚫ Interview Questions + Answers

Q1: What are START and END in LangGraph? (Easy)
A1: Special virtual nodes imported from `langgraph.graph`. An edge from `START` marks the entry node; an edge to `END` marks completion.

Q2: Are `set_entry_point` and `add_edge(START, ...)` different? (Easy)
A2: No, they are equivalent. `add_edge(START, "x")` is the modern, preferred style, and it also allows multiple entry nodes (parallel start).

Q3: Can a graph have more than one END path? (Medium)
A3: Yes. Any number of nodes or routers can point to END (success, validation failure, escalation). The final state returned depends on which path ran, so make state fields optional or defaulted.

Q4: How do you implement an early exit that saves tokens? (Medium)
A4: Put cheap deterministic checks first (empty input, blocked topic, cache hit) and add a conditional edge that returns END on failure. The expensive LLM nodes never run.

Q5: How would you guarantee a graph with loops terminates? (Hard)
A5: Combine three controls: (1) an explicit counter in state and a router that sends to END/escalation after N tries, (2) `recursion_limit` in the run config (default 25) which raises `GraphRecursionError`, (3) timeouts at node/API level. Add tests that force the worst case (classifier always unsure) and assert the graph ends.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always: every graph has START and END
- You want multiple outcomes (success, rejected, escalated) with clear end paths
- You want cheap early exits before costly LLM nodes

❌ Avoid when:
- Using `set_entry_point` in new code (prefer `add_edge(START, ...)`)
- Leaving error branches unfinished

---

## 📊 Visual Diagram
```
START ──► [validate] ──ok──► [classify] ──► END
              │
              └──error──────────────────► END   (early exit, 0 LLM tokens)
```

---

## 💰 Cost Impact
- An early exit before the LLM saves 100% of that request's tokens. If 8% of tariff requests are empty/garbage and a normal call costs ~1,200 tokens, validation saves about 96 tokens per request on average (8% of the bill).
- START/END themselves cost nothing; they are not LLM calls.
- Optimise: validate, deduplicate and cache before the first LLM node; return cached results through a short END path.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| START | Virtual entry node | शुरुआती virtual node |
| END | Virtual terminal node | अंतिम virtual node |
| Entry point | First node that runs | पहला node |
| Finish point | Node that connects to END | आखिरी node |
| Early exit | Ending before costly steps | जल्दी बाहर निकलना |
| Final state | State returned at END | अंत की state |

---

## ⚡ 3-Line Summary
English: `START` marks where a graph begins and `END` where it stops; compile() checks the wiring. Use several END paths for success, failure and escalation. Put cheap checks first and exit early to save tokens.
Hindi: `START` बताता है graph कहाँ शुरू होगा और `END` कहाँ रुकेगा; compile() wiring check करता है। Success, failure और escalation के लिए कई END paths रखो। सस्ते checks पहले रखो और जल्दी exit करके tokens बचाओ।

---

## ➡️ Next Topic
**324. StateGraph vs MessageGraph** — custom state schemas vs the older message-list-only graph, and why `StateGraph` + `MessagesState` replaced it.
