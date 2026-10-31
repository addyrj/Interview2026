---

# 330. Interrupt + Resume
# हिंदी में: Interrupt + Resume (रुकना और दोबारा चलाना)

---

## 🔵 Simple Definition (English)
`interrupt(value)` stops a LangGraph run at that line, saves the state, and hands `value` to the caller. Later, `graph.invoke(Command(resume=answer), config)` restarts the paused node, and the same `interrupt()` call now returns `answer`. Static breakpoints (`interrupt_before` / `interrupt_after`) pause around a whole node and are resumed with `invoke(None, config)`.

## 🔵 सरल परिभाषा (Hindi)
`interrupt(value)` LangGraph run को उसी line पर रोकता है, state save करता है और `value` caller को देता है। बाद में `graph.invoke(Command(resume=answer), config)` रुके node को दोबारा चलाता है, और वही `interrupt()` अब `answer` return करता है। Static breakpoints (`interrupt_before` / `interrupt_after`) पूरे node के आस-पास रुकते हैं और `invoke(None, config)` से आगे चलते हैं।

---

## 🔴 Problem it Solves
Python cannot freeze a function in the middle and continue after two days; a normal `input()` blocks the whole process. A web server cannot hold a thread for two days. We need a way to stop, free all resources, and later continue exactly where we left. Interrupt + resume turns "wait for a human" into "save a checkpoint and exit", which is cheap and scalable.

## 🔴 यह क्यों बना? (Hindi)
Python function को बीच में freeze करके दो दिन बाद आगे नहीं चला सकता; `input()` पूरा process block कर देता है। Web server दो दिन तक thread पकड़कर नहीं रख सकता। हमें ऐसा तरीका चाहिए जो रुके, सारे resources छोड़े और बाद में ठीक वहीं से चले। Interrupt + resume "इंसान का इंतज़ार" को "checkpoint save करके बाहर निकलो" में बदल देता है, जो सस्ता और scalable है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Graph compiled with a checkpointer; call uses a thread_id
Step 2 → Node executes normally until it reaches interrupt(payload)
Step 3 → LangGraph raises an internal GraphInterrupt, saves the checkpoint (node marked as pending)
Step 4 → invoke() returns; result contains "__interrupt__" = [Interrupt(value=payload, id=...)]
Step 5 → get_state(cfg).next == ("node_name",)  -> the graph is waiting
Step 6 → Later: invoke(Command(resume=answer), cfg)
Step 7 → The pending node is RE-RUN FROM ITS FIRST LINE
Step 8 → The k-th interrupt() call in that node returns the k-th stored resume value (matched by order);
         a new interrupt() with no stored value pauses again
Step 9 → Node finishes -> graph continues to the next node
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Graph checkpointer के साथ compile; call में thread_id
Step 2 → Node सामान्य चलता है जब तक interrupt(payload) न आ जाए
Step 3 → LangGraph internal GraphInterrupt उठाता है, checkpoint save करता है (node pending मार्क)
Step 4 → invoke() लौटता है; result में "__interrupt__" = [Interrupt(value=payload, id=...)]
Step 5 → get_state(cfg).next == ("node_name",)  -> graph इंतज़ार में है
Step 6 → बाद में: invoke(Command(resume=answer), cfg)
Step 7 → Pending node अपनी पहली line से दोबारा चलता है
Step 8 → उस node में k-वाँ interrupt() k-वाँ saved resume value लौटाता है (क्रम से match);
         जिस नए interrupt() की value नहीं है वह फिर से रुकता है
Step 9 → Node पूरा होने पर graph अगले node पर जाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A node needs two things from the officer: (1) confirm the product category, (2) confirm the country of origin. It calls `interrupt()` twice. The first resume answers the first question and the graph pauses again on the second. A separate "pre-filing" breakpoint (`interrupt_before=["file_declaration"]`) lets a supervisor inspect and even edit the final state with `update_state` before filing.

**Zomato-style**: A support bot asks a restaurant manager "accept refund?" and waits until the manager answers from their phone.

## 🟡 Real Example Hindi mein
**Tariff System**: एक node को officer से दो बातें चाहिए: (1) product category confirm, (2) country of origin confirm। वह दो बार `interrupt()` call करता है। पहला resume पहले सवाल का जवाब देता है और graph दूसरे सवाल पर फिर रुकता है। अलग "pre-filing" breakpoint (`interrupt_before=["file_declaration"]`) से supervisor filing से पहले final state देख और `update_state` से बदल भी सकता है।

**Zomato-style**: Support bot restaurant manager से "refund accept करें?" पूछकर तब तक रुकता है जब तक manager फ़ोन से जवाब न दे।

---

## 💻 Code Example — Basic
```python
# Basic: two interrupts in ONE node, resumed one by one (offline)
from typing import TypedDict                              # type hints

from langgraph.checkpoint.memory import MemorySaver       # saver is required
from langgraph.graph import END, START, StateGraph       # graph API
from langgraph.types import Command, interrupt            # pause / resume


class State(TypedDict, total=False):                      # state
    category: str                                         # answer 1
    origin: str                                           # answer 2
    summary: str                                          # final text


def collect(state: State) -> dict:                        # node with two questions
    category = interrupt("Confirm product category")      # 1st pause -> returns answer 1 on resume
    origin = interrupt("Confirm country of origin")       # 2nd pause -> returns answer 2 on resume
    return {"category": category, "origin": origin,       # store both answers
            "summary": f"{category} from {origin}"}       # combined text


builder = StateGraph(State)                               # build graph
builder.add_node("collect", collect)                      # node
builder.add_edge(START, "collect")                        # start
builder.add_edge("collect", END)                          # end
app = builder.compile(checkpointer=MemorySaver())         # compile with checkpointer

cfg = {"configurable": {"thread_id": "case-1"}}           # thread id

r1 = app.invoke({}, cfg)                                  # runs until first interrupt
print("Q1:", r1["__interrupt__"][0].value)                # Confirm product category
print("waiting at:", app.get_state(cfg).next)             # ('collect',)

r2 = app.invoke(Command(resume="Smartphone"), cfg)        # answer 1 -> pauses at second interrupt
print("Q2:", r2["__interrupt__"][0].value)                # Confirm country of origin

r3 = app.invoke(Command(resume="Vietnam"), cfg)           # answer 2 -> finishes
print(r3["summary"])                                      # Smartphone from Vietnam
```

## 💻 Code Example — Advanced
```python
# Production style: static breakpoint + inspect/edit state + streaming + async + error handling
import asyncio                                            # async runtime
import logging                                            # logs
from typing import Any, TypedDict                         # type hints

from langgraph.checkpoint.memory import MemorySaver       # use Postgres/Redis in production
from langgraph.graph import END, START, StateGraph       # graph API
from langgraph.types import Command, interrupt           # pause / resume

logger = logging.getLogger("tariff.interrupt")            # logger


class State(TypedDict, total=False):                      # state
    product: str                                          # input
    hs_code: str                                          # code
    duty_rate: float                                      # percent
    filed: bool                                           # final flag


async def classify(state: State) -> dict[str, Any]:       # LLM-like node
    await asyncio.sleep(0)                                # placeholder for `await llm.ainvoke(...)`
    return {"hs_code": "8517.13", "duty_rate": 20.0}      # fake result


async def ask_officer(state: State) -> dict[str, Any]:    # dynamic interrupt
    answer: dict[str, Any] = interrupt({                  # pause, send context
        "hs_code": state["hs_code"], "duty_rate": state["duty_rate"]})
    if not isinstance(answer, dict):                      # defend against wrong resume shape
        raise ValueError("resume value must be a dict")   # fail loudly
    return {"hs_code": answer.get("hs_code", state["hs_code"])}   # accept optional override


async def file_declaration(state: State) -> dict[str, Any]:   # dangerous step
    await asyncio.sleep(0)                                # placeholder for real filing API
    return {"filed": True}                                # mark filed


def build():                                              # factory
    b = StateGraph(State)                                 # builder
    b.add_node("classify", classify)                      # node
    b.add_node("ask_officer", ask_officer)                # node
    b.add_node("file_declaration", file_declaration)      # node
    b.add_edge(START, "classify")                         # edges
    b.add_edge("classify", "ask_officer")
    b.add_edge("ask_officer", "file_declaration")
    b.add_edge("file_declaration", END)
    return b.compile(
        checkpointer=MemorySaver(),                       # needed for any pause
        interrupt_before=["file_declaration"],            # static breakpoint: supervisor check
    )


async def main() -> None:                                 # demo
    app = build()                                         # graph
    cfg = {"configurable": {"thread_id": "case-5"}}       # thread

    await app.ainvoke({"product": "phone"}, cfg)          # stops at dynamic interrupt in ask_officer
    await app.ainvoke(Command(resume={"hs_code": "8517.62"}), cfg)   # officer overrides code
    snap = await app.aget_state(cfg)                      # now stopped BEFORE file_declaration
    print("next:", snap.next, "code:", snap.values["hs_code"])   # ('file_declaration',) 8517.62

    await app.aupdate_state(cfg, {"duty_rate": 10.0})     # supervisor edits state while paused
    try:                                                  # resume with None = "just continue"
        async for chunk in app.astream(None, cfg, stream_mode="updates"):   # stream node updates
            print(chunk)                                  # {'file_declaration': {'filed': True}}
    except Exception:                                     # any node failure
        logger.exception("resume failed")                 # log it; state is still checkpointed
        raise                                             # surface the error


if __name__ == "__main__":                                # entry
    asyncio.run(main())                                   # run
```

---

## 🟠 FastAPI Integration
Model each paused graph as a "task" with states `running`, `waiting`, `done`. `GET /cases/{id}` reads `get_state` and returns the interrupt payload, `POST /cases/{id}/resume` sends `Command(resume=...)`. The check on `snap.interrupts` stops stray or duplicate resumes.

```python
# FastAPI: inspect and resume paused graphs
from typing import Any, TypedDict                                  # type hints

from fastapi import FastAPI, HTTPException                         # web framework
from langgraph.checkpoint.memory import MemorySaver                # shared saver in production
from langgraph.graph import END, START, StateGraph                # graph API
from langgraph.types import Command, interrupt                     # pause/resume
from pydantic import BaseModel                                     # models


class S(TypedDict, total=False):                                   # state
    q: str                                                         # question
    answer: str                                                    # final answer


def ask(s: S) -> dict:                                             # node with interrupt
    return {"answer": interrupt({"need": "country_of_origin", "q": s["q"]})}   # waits for a value


b = StateGraph(S)                                                  # build
b.add_node("ask", ask)                                             # node
b.add_edge(START, "ask")                                           # start
b.add_edge("ask", END)                                             # end
graph = b.compile(checkpointer=MemorySaver())                      # compile

app = FastAPI(title="Resume API")                                  # API


class StartIn(BaseModel):                                          # body
    case_id: str                                                   # thread id
    q: str                                                         # question


class ResumeIn(BaseModel):                                         # body
    value: Any                                                     # any JSON resume value


@app.post("/cases")                                                # start
async def start(body: StartIn) -> dict[str, Any]:                  # handler
    cfg = {"configurable": {"thread_id": body.case_id}}            # config
    await graph.ainvoke({"q": body.q}, cfg)                        # runs to the interrupt
    return {"case_id": body.case_id, "status": "waiting"}          # waiting for a human


@app.get("/cases/{case_id}")                                       # inspect
async def status(case_id: str) -> dict[str, Any]:                  # handler
    snap = await graph.aget_state({"configurable": {"thread_id": case_id}})   # read state
    if snap.interrupts:                                            # paused
        return {"status": "waiting", "prompt": snap.interrupts[0].value}   # what to show the human
    return {"status": "done" if snap.values else "unknown", "values": snap.values}   # finished


@app.post("/cases/{case_id}/resume")                               # resume
async def resume(case_id: str, body: ResumeIn) -> dict[str, Any]:  # handler
    cfg = {"configurable": {"thread_id": case_id}}                 # config
    snap = await graph.aget_state(cfg)                             # check state first
    if not snap.interrupts:                                        # nothing to resume
        raise HTTPException(409, "case is not waiting")            # conflict
    out = await graph.ainvoke(Command(resume=body.value), cfg)     # resume
    return {"status": "done", "values": out}                       # final values
```

---

## 🔗 LangChain / LangGraph Connection
Interrupts work in any node, including inside tools called by `create_react_agent`, inside subgraphs (the parent also pauses), and with the LangGraph API server / Studio, which shows pending interrupts and lets you resume from the UI. `graph.update_state(cfg, values, as_node="name")` edits state as if a node had produced it, which is how you "rewrite history" before resuming. Time travel: pick an older checkpoint from `get_state_history` and invoke with that `checkpoint_id` to fork a new run.

```python
# Time travel: fork from an earlier checkpoint
history = list(app.get_state_history(cfg))                  # newest first
old = history[2]                                            # choose an older snapshot
app.update_state(old.config, {"hs_code": "9999.00"})        # edit and create a fork
app.invoke(None, old.config)                                # replay from that point
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrapping `interrupt()` in a broad `try/except`
✅ Correct: `interrupt()` works by raising a special exception. Catching `Exception` swallows the pause.

```python
# Wrong
try:
    ans = interrupt("approve?")
except Exception:            # swallows GraphInterrupt -> graph never pauses
    ans = None

# Right — keep interrupt outside try, or catch specific errors only
ans = interrupt("approve?")
try:
    process(ans)
except ValueError:
    ...
```

❌ Mistake 2: Changing the order or number of interrupts between pause and resume (e.g. with `if random()`)
✅ Correct: resume values are matched by call order, so keep interrupt calls deterministic.

```python
# Wrong
if random.random() > 0.5:
    a = interrupt("Q-A")
b = interrupt("Q-B")      # answers can be mapped to the wrong question

# Right — condition on saved state, not on randomness or time
if state["needs_a"]:
    a = interrupt("Q-A")
b = interrupt("Q-B")
```

❌ Mistake 3: Resuming with `invoke(new_input)` instead of `Command(resume=...)`
✅ Correct: a dict input starts a new run from START. Use `Command(resume=...)` to continue, or `None` after a static breakpoint.

---

## 🧠 Tricky Interview Question

**Q**: "Your node calls the LLM, then `interrupt()`, then writes to a database. After resume, you see two LLM charges for the same case. Why, and how do you fix it?"

**Answer**: On resume, LangGraph re-executes the interrupted node from its first line, so the LLM call before `interrupt()` runs again. The cost doubles and the second answer may even differ from what the human reviewed. Split the work: `classify` node (LLM, result saved in state) then a separate `review` node with only `interrupt()`, then a `write` node. A node that finished is checkpointed and never re-runs. Alternatively keep the LLM result in state and skip calling when it already exists.

---

## ⚫ Interview Questions + Answers

Q1: What does `interrupt()` return the first time? (Easy)
A1: It does not return; it pauses the graph and sends its argument to the caller in `__interrupt__`. On resume it returns the resume value.

Q2: How do you resume a paused graph? (Easy)
A2: Call `invoke` (or `stream`) with `Command(resume=value)` and the same `thread_id`. For static breakpoints call with `None` as input.

Q3: What is the difference between `interrupt_before` and `interrupt_after`? (Medium)
A3: `interrupt_before=["x"]` stops just before node x runs (good for approvals). `interrupt_after=["x"]` stops after x finished and its output is saved (good for reviewing output). Both are set in `compile()` or at run time, and need a checkpointer.

Q4: How can you see what a paused graph is waiting for? (Medium)
A4: `graph.get_state(cfg)` returns a `StateSnapshot`. `.next` has the waiting nodes, `.interrupts` has the interrupt payloads, `.tasks` has details per task, and `.values` is the current state.

Q5: Explain re-execution semantics and how they affect design. (Hard)
A5: Resume re-runs the whole interrupted node, replaying earlier `interrupt()` calls with their saved answers. Therefore code before an interrupt must be idempotent or cheap; side effects go in later nodes; interrupt order must be deterministic; and nodes should be small, one responsibility each. For parallel branches that interrupt at the same time you resume with a mapping of interrupt id to value, so each branch gets its own answer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need approvals, clarifications or data from a human mid-run
- You want to inspect or edit state before a risky node
- Runs can last hours or days

❌ Avoid when:
- A simple conditional edge can decide automatically
- You only need to ask the user before the graph starts (ask in the API instead)
- Node has expensive non-idempotent work before the pause (restructure first)

---

## 📊 Visual Diagram
```
 invoke(input)                      invoke(Command(resume="A"))
      │                                        │
      ▼                                        ▼
 ┌─ node ────────────────┐            ┌─ node (RE-RUN from top) ─┐
 │ x = compute()         │            │ x = compute()  (again!)  │
 │ a = interrupt("Q?") ──┼─► PAUSE    │ a = interrupt("Q?") ─► "A"│
 │ y = use(a)            │   saved    │ y = use(a)               │
 └───────────────────────┘            └──────────────────────────┘
   result["__interrupt__"]                    continues to next node
   get_state().next == ("node",)
```

---

## 💰 Cost Impact
Paused graphs use no LLM tokens and almost no compute. The hidden cost is re-execution: any LLM call placed before `interrupt()` in the same node is paid again on resume. Example: a 2,000-input/300-output gpt-4o-mini call costs about $0.00048; with 100K cases per day re-running it on resume wastes about $48 per day. Optimise: isolate the LLM call in its own node before the interrupt node, store results in state, and set retention rules for old paused threads so the checkpoint store does not grow forever.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| interrupt() | Pause inside a node | Node के अंदर pause |
| Command(resume=) | Send the answer and continue | जवाब देकर आगे चलाना |
| interrupt_before/after | Static breakpoints on nodes | Node के पहले/बाद में रुकना |
| StateSnapshot | Result of get_state() | State की तस्वीर |
| update_state | Edit saved state manually | Saved state को बदलना |
| Time travel | Re-run from an old checkpoint | पुराने checkpoint से दोबारा चलाना |
| Re-execution | Node restarts from line 1 on resume | Resume पर node फिर शुरू से चलता है |

---

## ⚡ 3-Line Summary
English: `interrupt(payload)` pauses and saves; `Command(resume=value)` makes the same call return `value` and continues. On resume the node re-runs from its first line, so keep pre-interrupt code idempotent and interrupt order deterministic. Static breakpoints with `update_state` let you inspect and edit before a risky node.
Hindi: `interrupt(payload)` रोकता और save करता है; `Command(resume=value)` वही call `value` लौटाकर आगे चलाता है। Resume पर node पहली line से दोबारा चलता है, इसलिए interrupt से पहले का code idempotent और interrupt का क्रम तय रखो। Static breakpoints और `update_state` से risky node से पहले state देख और बदल सकते हैं।

---

## ➡️ Next Topic
**331. Parallel Execution in LangGraph** — run several nodes at the same time (fan-out / fan-in) to cut latency.
