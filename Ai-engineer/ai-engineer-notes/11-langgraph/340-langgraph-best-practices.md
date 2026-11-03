
---

# 340. LangGraph Best Practices
# हिंदी में: LangGraph की Best Practices

---

## 🔵 Simple Definition (English)
LangGraph best practices are habits that keep agent graphs reliable: small typed state, single-purpose nodes, explicit routing, loop limits, checkpointing, retries with timeouts, and tests that run without calling a real LLM. A graph is code, so treat it like production software.

## 🔵 सरल परिभाषा (Hindi)
LangGraph best practices वे आदतें हैं जो agent graphs को भरोसेमंद रखती हैं: छोटा typed state, एक काम वाले nodes, साफ़ routing, loop limits, checkpointing, timeout के साथ retries और ऐसे tests जो असली LLM के बिना चलें। Graph भी code है, उसे production software की तरह लो।

---

## 🔴 Problem it Solves
Demo graphs break in production: state grows without bound, a router loops forever, one failed tool call kills the run, nobody can tell which node cost the money, and changes cannot be tested. Best practices prevent infinite loops, runaway token cost and silent wrong answers.

## 🔴 यह क्यों बना? (Hindi)
Demo graphs production में टूटते हैं: state बेतहाशा बढ़ता है, router अनंत loop में फँसता है, एक tool fail होने पर पूरा run मर जाता है, पता नहीं कौन सा node पैसे खा रहा है। Best practices infinite loops, बढ़ते token cost और चुपचाप गलत answers रोकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Design state first: TypedDict with only what nodes must share
Step 2 → One node = one job (retrieve, classify, validate); keep nodes small
Step 3 → Nodes return partial updates (dict), never mutate state in place
Step 4 → Use reducers (e.g. add_messages, operator.add) for lists that accumulate
Step 5 → Routers are pure functions returning node names; cover every branch + END
Step 6 → Cap loops: counters in state + recursion_limit in config
Step 7 → Wrap LLM/tool calls with timeout, retry and fallback
Step 8 → Add a checkpointer (SQLite/Postgres in prod) and thread_id per user session
Step 9 → Unit-test nodes and routers with fake LLMs; trace real runs in LangSmith
Step 10 → Version the graph; keep prompts in config, not hard-coded
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले state design करो: सिर्फ वही fields जो nodes share करते हैं
Step 2 → एक node = एक काम (retrieve, classify, validate)
Step 3 → Nodes partial update (dict) लौटाएँ, state in-place न बदलें
Step 4 → जो lists जमा होती हैं उनके लिए reducers (add_messages, operator.add)
Step 5 → Routers pure functions हों, हर branch + END cover हो
Step 6 → Loops सीमित करो: state में counter + config में recursion_limit
Step 7 → LLM/tool calls पर timeout, retry और fallback
Step 8 → Production में SQLite/Postgres checkpointer और हर user session के लिए thread_id
Step 9 → Fake LLM से nodes/routers का unit test; LangSmith में असली runs trace करो
Step 10 → Graph version करो; prompts config में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: graph = `retrieve_rules -> classify -> validate_code -> (ok) finish | (invalid, attempts<2) classify | (else) human_review`. Best practices applied: `attempts` counter in state caps retries at 2, `validate_code` checks the 8-digit format with a regex (no LLM), `thread_id` equals the case id so reviewers can resume, and node tests use a fake classifier.

**Zomato AI**: support graph with an `escalate` node so after 2 failed answers a human agent takes over rather than looping.

## 🟡 Real Example Hindi mein
**Tariff System**: graph = `retrieve_rules -> classify -> validate_code -> (ok) finish | (invalid और attempts<2) classify | (वरना) human_review`। State का `attempts` counter retries को 2 तक रोकता है, `validate_code` regex से 8-digit format जाँचता है (LLM नहीं), `thread_id` = case id ताकि reviewer resume कर सके।

**Zomato AI**: 2 failed answers के बाद `escalate` node से human agent को सौंपना, loop नहीं।

---

## 💻 Code Example — Basic
```python
# Pure Python (no langgraph needed): the "state + nodes + router + loop cap" pattern in miniature
import re  # regex for code validation
from typing import TypedDict  # typed state

class State(TypedDict):
    desc: str       # product description
    code: str       # candidate HS code
    attempts: int   # how many classify attempts so far

def classify(s: State) -> dict:
    """Fake classifier: bad on first try, good on second (to show the retry loop)."""
    code = "8518.3" if s["attempts"] == 0 else "8518.30"  # first answer is malformed
    return {"code": code, "attempts": s["attempts"] + 1}  # partial update, not in-place mutation

def validate(s: State) -> dict:
    return {}  # validation only inspects state; routing happens in the router

def route(s: State) -> str:
    """Router: pure function returning the next node name."""
    if re.fullmatch(r"\d{4}\.\d{2}", s["code"]):  # looks like a valid 6-digit HS code
        return "finish"  # accept
    if s["attempts"] < 2:  # still have retry budget
        return "classify"  # try again
    return "human_review"  # give up safely

state: State = {"desc": "headphones", "code": "", "attempts": 0}  # initial state
node = "classify"  # entry point
for _ in range(10):  # hard loop cap (like recursion_limit)
    if node == "classify":  # run classify node
        state |= classify(state)  # merge partial update
        node = route(state)  # decide next
    else:  # finish or human_review
        break  # leave loop
print(node, state)  # finish {'desc': 'headphones', 'code': '8518.30', 'attempts': 2}
```

## 💻 Code Example — Advanced
```python
# Production-style LangGraph: typed state, reducer, retry cap, checkpointer, timeout, async nodes
# pip install langgraph langchain-openai   (real LLM needs OPENAI_API_KEY)
import asyncio  # timeouts
import logging  # logs
import operator  # list reducer
import re  # validation
from typing import Annotated, Literal, TypedDict  # typing helpers

from langgraph.checkpoint.memory import MemorySaver  # in-memory checkpointer (use Postgres/SQLite in prod)
from langgraph.graph import END, StateGraph  # graph API

log = logging.getLogger("tariff")  # logger

class S(TypedDict):
    desc: str                                   # input
    code: str                                   # candidate code
    attempts: int                               # retry counter
    errors: Annotated[list[str], operator.add]  # reducer: appended, never overwritten

async def call_llm(desc: str) -> str:
    """Placeholder LLM call; swap for ChatOpenAI(...).ainvoke."""
    await asyncio.sleep(0)  # pretend IO
    return "8518.30"  # stub answer

async def classify(s: S) -> dict:
    """Classify with timeout; record errors instead of crashing."""
    try:
        code = await asyncio.wait_for(call_llm(s["desc"]), timeout=20)  # never hang forever
        return {"code": code, "attempts": s["attempts"] + 1}  # partial update
    except (asyncio.TimeoutError, Exception) as exc:  # LLM/network errors
        log.warning("classify failed: %s", exc)  # log it
        return {"attempts": s["attempts"] + 1, "errors": [str(exc)]}  # reducer appends

def route(s: S) -> Literal["finish", "classify", "human_review"]:
    """Pure router: valid -> finish; retry twice; then a human."""
    if re.fullmatch(r"\d{4}\.\d{2}", s.get("code", "")):  # valid format
        return "finish"
    return "classify" if s["attempts"] < 2 else "human_review"  # bounded retry

async def finish(s: S) -> dict: return {}  # terminal success node
async def human_review(s: S) -> dict: return {"errors": ["needs human"]}  # terminal fallback node

g = StateGraph(S)  # create graph
g.add_node("classify", classify)  # node
g.add_node("finish", finish)  # node
g.add_node("human_review", human_review)  # node
g.set_entry_point("classify")  # start
g.add_conditional_edges("classify", route)  # routing after classify
g.add_edge("finish", END)  # end
g.add_edge("human_review", END)  # end
app = g.compile(checkpointer=MemorySaver())  # compile with persistence

async def main() -> None:
    cfg = {"configurable": {"thread_id": "case-42"}, "recursion_limit": 10}  # per-case thread + loop cap
    out = await app.ainvoke({"desc": "headphones", "code": "", "attempts": 0, "errors": []}, cfg)  # run
    print(out)  # final state

if __name__ == "__main__":
    asyncio.run(main())  # needs langgraph installed
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from langgraph.errors import GraphRecursionError  # raised when recursion_limit is hit
from pydantic import BaseModel  # schema

app = FastAPI()  # api app
# graph_app is the compiled graph from the previous section (import it in real code)

class Req(BaseModel):
    case_id: str  # used as thread_id
    description: str  # product text

@app.post("/classify")
async def classify(req: Req) -> dict:
    """Run the graph with a per-case thread and a hard loop cap."""
    cfg = {"configurable": {"thread_id": req.case_id}, "recursion_limit": 10}  # config
    try:
        out = await graph_app.ainvoke({"desc": req.description, "code": "", "attempts": 0, "errors": []}, cfg)  # noqa: F821
    except GraphRecursionError:  # loop did not end in time
        raise HTTPException(status_code=508, detail="graph looped too long")  # clear error
    return {"code": out["code"], "errors": out["errors"]}  # response
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph nodes usually call LangChain components (chat models, retrievers, tools). Use `with_structured_output` to get typed results from the model, and `.with_retry()` / `.with_fallbacks()` on runnables to add resilience inside a node.

```python
from langchain_openai import ChatOpenAI  # chat model
from pydantic import BaseModel  # structured schema

class Result(BaseModel):
    hs_code: str  # code
    needs_review: bool  # flag

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # deterministic
safe = llm.with_structured_output(Result).with_retry(stop_after_attempt=2)  # typed output + retry
# result = await safe.ainvoke("Classify: bluetooth headphones")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unbounded retry loop
✅ Correct: Counter in state plus recursion_limit.
```python
# Wrong: g.add_conditional_edges("classify", lambda s: "classify" if bad(s) else END)
# Right: route() checks s["attempts"] < 2, else goes to human_review
```

❌ Mistake 2: Overwriting a list that should accumulate
✅ Correct: Use a reducer.
```python
# Wrong: class S(TypedDict): messages: list   # each node replaces the list
# Right: messages: Annotated[list, add_messages]   # or operator.add
```

❌ Mistake 3: Putting the whole document in state and in every checkpoint
✅ Correct: Store ids/paths in state and fetch big text inside the node.

---

## 🧠 Tricky Interview Question

**Q**: "Your graph worked in testing but in production the same user sometimes sees another user's conversation. What went wrong?"

**Answer**: The `thread_id` is not unique per user/session (for example a constant or a shared default), so the checkpointer loads the same saved state for different users. Fix: derive `thread_id` from an authenticated user id plus conversation id, never from client-controlled shared values; use a persistent checkpointer scoped by that id and add an authorisation check before resuming a thread.

---

## ⚫ Interview Questions + Answers

Q1: Why use a TypedDict for state?
A1: It documents the shape, helps type checking and keeps nodes agreeing on keys.

Q2: What is a reducer?
A2: A function that tells LangGraph how to merge a node's update into a key, for example appending to a list instead of replacing it.

Q3: How do you prevent infinite loops?
A3: Bound retries with a counter in state, route to a fallback after the limit, and set `recursion_limit` in the run config as a safety net.

Q4: How do you test a graph without paying for LLM calls?
A4: Inject fake LLM functions or runnables, test routers as pure functions, and assert on state transitions. Run a small real-LLM suite separately.

Q5: How would you make a long-running graph survive a server restart?
A5: Compile with a durable checkpointer (SQLite or Postgres saver), use a stable `thread_id`, make nodes idempotent so replays do not duplicate side effects (payments, emails), and resume with `ainvoke(None, config)` after an interrupt or crash.

---

## 🔷 When to Use + When Not to Use
✅ Use these practices when:
- The graph has loops, tools, human review, or multiple users

❌ Avoid over-engineering when:
- A single LLM call or a simple chain solves the task

---

## 📊 Visual Diagram
```
 START ─► classify ──► route()
              ▲          │ valid            ─► finish ─► END
              │          │ invalid, tries<2 ─┐
              └──────────┘                   │
                         │ invalid, tries>=2 ─► human_review ─► END
 state: {desc, code, attempts, errors[+]}   checkpoint after every node (thread_id)
```

---

## 💰 Cost Impact
Every node that calls an LLM adds tokens, and loops multiply them: a 3-step graph with 2 retries can cost up to 6 LLM calls per request. Bound retries and use `recursion_limit`. Keep state small because it can be re-sent into prompts and is stored in each checkpoint. Use a cheap model (e.g. gpt-4o-mini) for classification nodes and a stronger model only for review. Use deterministic nodes (regex validation) instead of LLM checks. Example: 600 input + 100 output tokens per call at illustrative prices of $0.15 / $0.60 per 1M is about $0.00015 per call, so 3 calls is about $0.00045; capping retries limits the worst case.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Shared data of the graph | Graph का साझा data |
| Node | Function that updates state | State बदलने वाला function |
| Router | Chooses the next node | अगला node चुनने वाला |
| Reducer | How updates are merged | Updates जोड़ने का तरीका |
| Checkpointer | Saves state per step | हर step पर state सहेजना |
| thread_id | Session key for state | Session की पहचान |
| recursion_limit | Max steps safety cap | अधिकतम steps की सीमा |

---

## ⚡ 3-Line Summary
English: Keep state small and typed, nodes single-purpose, routers pure, and loops bounded. Use reducers, checkpointers with unique thread ids, and timeouts with retries. Test with fake LLMs and trace real runs.
Hindi: State छोटा और typed रखो, nodes एक काम वाले, routers pure और loops सीमित। Reducers, unique thread id वाला checkpointer, timeouts और retries इस्तेमाल करो। Fake LLM से test करो और असली runs trace करो।

---

## ➡️ Next Topic
**341. LangGraph Studio** — a visual tool to run, inspect and debug these graphs step by step.
