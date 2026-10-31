---

# 349. Supervisor Architecture
# हिंदी में: Supervisor Architecture

---

## 🔵 Simple Definition (English)
In a supervisor architecture one central agent (the supervisor) looks at the task and the current state, then picks which worker agent runs next. Workers do their job and report back to the supervisor. The supervisor decides when the work is finished.

## 🔵 सरल परिभाषा (Hindi)
Supervisor architecture में एक central agent (supervisor) task और state देखकर तय करता है कि अगला worker agent कौन चलेगा। Workers काम करके supervisor को report करते हैं। काम कब पूरा हुआ, यह supervisor तय करता है।

---

## 🔴 Problem it Solves
- Fixed pipelines (A then B then C) cannot handle tasks that need different paths.
- Without a controller, agents do not know who should act next.
- Decisions about routing are spread across many agents and become hard to debug.
- One central place makes limits, logging and guardrails easy.

## 🔴 यह क्यों बना? (Hindi)
- Fixed pipelines (A फिर B फिर C) अलग-अलग paths वाले tasks नहीं संभाल सकतीं।
- Controller के बिना agents को पता नहीं कि अगला कौन करे।
- Routing के decisions कई agents में बिखर जाते हैं, debug मुश्किल।
- एक central जगह से limits, logging और guardrails आसान हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User task enters the supervisor
Step 2 → Supervisor reads state and chooses: worker name OR FINISH
Step 3 → Chosen worker runs with its own prompt and tools
Step 4 → Worker writes result to state and returns control to supervisor
Step 5 → Supervisor re-reads state, decides again
Step 6 → Loop continues until FINISH or max steps
Step 7 → Supervisor composes the final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User task supervisor के पास आता है
Step 2 → Supervisor state पढ़कर चुनता है: worker का नाम या FINISH
Step 3 → चुना हुआ worker अपने prompt और tools से चलता है
Step 4 → Worker result state में लिखकर supervisor को control लौटाता है
Step 5 → Supervisor state फिर पढ़कर दोबारा तय करता है
Step 6 → FINISH या max steps तक loop चलता है
Step 7 → Supervisor final answer बनाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: the supervisor sees "classify a leather wallet and tell me the duty". It calls `researcher` (find candidate codes), then `classifier` (choose one), then `duty_agent` (look up the rate), then `FINISH`. For a simple "what is the duty for 6109.10?" it skips straight to `duty_agent`.

**Amazon**: a customer-care supervisor routes to order, returns or payment agents. **Zomato**: support supervisor routes to refund or delivery-tracking worker.

## 🟡 Real Example Hindi mein
**Tariff System**: supervisor को "leather wallet classify करो और duty बताओ" मिलता है। वह पहले `researcher`, फिर `classifier`, फिर `duty_agent`, फिर `FINISH`। सिर्फ "6109.10 की duty?" पर वह सीधे `duty_agent` को बुलाता है।

**Amazon**: customer-care supervisor order, returns या payment agents को route करता है।

---

## 💻 Code Example — Basic
```python
# Rule-based supervisor (the LLM decision is replaced by simple rules so it runs offline)
from typing import Callable  # type hints

State = dict[str, str]  # shared state is a dict of strings


def researcher(s: State) -> State:  # worker 1
    return {**s, "candidates": "6109.10, 6110.20"}  # adds candidates


def classifier(s: State) -> State:  # worker 2
    return {**s, "code": s["candidates"].split(",")[0]}  # picks the first


def duty_agent(s: State) -> State:  # worker 3
    return {**s, "duty": "12%"}  # fake duty


WORKERS: dict[str, Callable[[State], State]] = {  # registry
    "researcher": researcher, "classifier": classifier, "duty_agent": duty_agent,
}


def supervisor(s: State) -> str:  # decides the next step
    if "candidates" not in s:  # nothing found yet
        return "researcher"
    if "code" not in s:  # code not chosen yet
        return "classifier"
    if "duty" not in s:  # duty missing
        return "duty_agent"
    return "FINISH"  # everything done


state: State = {"task": "cotton t-shirt"}  # initial state
for _ in range(10):  # max-step guard
    nxt = supervisor(state)  # ask supervisor
    if nxt == "FINISH":  # stop condition
        break
    state = WORKERS[nxt](state)  # run worker
print(state)  # final state
```

## 💻 Code Example — Advanced
```python
# LLM-style supervisor with structured decision, validation, retries and a step budget
import asyncio  # async runtime
from typing import Literal  # restricted choices
from pydantic import BaseModel, ValidationError  # validation

Choice = Literal["researcher", "classifier", "duty_agent", "FINISH"]  # valid routes


class Decision(BaseModel):
    next: Choice  # chosen worker
    reason: str  # short explanation for logs


async def mock_supervisor_llm(state: dict) -> str:  # fake LLM returning JSON text
    await asyncio.sleep(0.01)  # latency
    if "candidates" not in state:
        return '{"next": "researcher", "reason": "need candidates"}'
    if "code" not in state:
        return '{"next": "classifier", "reason": "pick code"}'
    if "duty" not in state:
        return '{"next": "duty_agent", "reason": "need rate"}'
    return '{"next": "FINISH", "reason": "done"}'


async def decide(state: dict, retries: int = 2) -> Decision:
    for attempt in range(retries + 1):  # retry on bad JSON
        raw = await mock_supervisor_llm(state)  # call the model
        try:
            return Decision.model_validate_json(raw)  # parse + validate
        except ValidationError:
            if attempt == retries:  # no more tries
                raise
    raise RuntimeError("unreachable")


async def run_worker(name: str, state: dict) -> dict:  # worker dispatcher
    await asyncio.sleep(0.01)
    updates = {"researcher": {"candidates": "6109.10"}, "classifier": {"code": "6109.10"},
               "duty_agent": {"duty": "12%"}}
    return {**state, **updates[name]}


async def run(task: str, max_steps: int = 8) -> dict:
    state: dict = {"task": task}  # start state
    for step in range(max_steps):  # hard limit prevents infinite loops
        d = await decide(state)  # supervisor decision
        print(f"step {step}: {d.next} ({d.reason})")  # trace
        if d.next == "FINISH":
            return state
        state = await run_worker(d.next, state)  # run chosen worker
    raise RuntimeError("max steps exceeded")  # safety stop


if __name__ == "__main__":
    print(asyncio.run(run("cotton t-shirt")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    task: str  # user task


@app.post("/supervised")
async def supervised(req: Req) -> dict:
    try:  # call the supervisor loop (shown above as run())
        state = {"task": req.task, "code": "6109.10", "duty": "12%"}  # mocked result
    except RuntimeError as exc:  # e.g. max steps exceeded
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    return {"result": state, "steps": 3}  # include number of steps for monitoring
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph's supervisor pattern uses a node that returns `Command(goto=worker)`. There is also the prebuilt package `langgraph-supervisor` (`create_supervisor`), but the explicit graph below is easy to understand and control.

```python
from typing import TypedDict, Literal  # types
from langgraph.graph import StateGraph, START, END  # graph
from langgraph.types import Command  # routing


class S(TypedDict, total=False):
    task: str  # input
    code: str  # result from classifier


def supervisor(s: S) -> Command[Literal["classifier", "__end__"]]:
    if "code" not in s:  # work not done
        return Command(goto="classifier")  # route to worker
    return Command(goto=END)  # finish


def classifier(s: S) -> Command[Literal["supervisor"]]:
    return Command(update={"code": "6109.10"}, goto="supervisor")  # report back


g = StateGraph(S)  # build graph
g.add_node("supervisor", supervisor)  # node
g.add_node("classifier", classifier)  # node
g.add_edge(START, "supervisor")  # entry
print(g.compile().invoke({"task": "t-shirt"}))  # run
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No step limit.
✅ Correct: Always cap steps.

```python
# Wrong
# while True: state = WORKERS[supervisor(state)](state)
# Right
for _ in range(8):  # cap
    pass
```

❌ Mistake 2: Free-text routing decisions.
✅ Correct: Constrain to an enum.

```python
# Wrong: "I think the researcher should go next, maybe"
# Right: Literal["researcher","classifier","FINISH"] validated by pydantic
```

---

## 🧠 Tricky Interview Question
**Q**: "Your supervisor is the bottleneck: every worker call needs two supervisor LLM calls and latency doubled. What can you do?"

**Answer**: Replace LLM routing with deterministic rules where the path is predictable (state-based `if` checks, as in the basic example). Use a small model for routing, run independent workers in parallel (fan-out), let workers hand off directly when the next step is obvious, and cache routing decisions for repeated task patterns. Keep the LLM supervisor only for ambiguous cases.

---

## ⚫ Interview Questions + Answers

Q1: What does a supervisor do?
A1: It chooses which worker runs next and when to finish, based on the task and current state.

Q2: Why add a max-steps limit?
A2: To stop infinite loops and runaway cost when workers and supervisor keep bouncing.

Q3: How is a supervisor different from a fixed chain?
A3: A chain has a fixed order; the supervisor decides dynamically, can skip or repeat steps.

Q4: Weakness of a supervisor design?
A4: Single point of failure and extra LLM calls (latency/cost); the supervisor prompt can become complicated as workers grow.

Q5: Supervisor has 25 workers and routing accuracy drops. What now?
A5: Make it hierarchical: group workers into teams with team supervisors, or add a retrieval step that shows only top-k relevant workers' descriptions. Evaluate routing accuracy on a labelled set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks need dynamic paths
- You want one place for guardrails and logging

❌ Avoid when:
- The path is always the same (use a chain)
- Latency is critical and routing is predictable

---

## 📊 Visual Diagram
```
              ┌──────────────┐
   task ────► │  SUPERVISOR  │ ◄──────────┐
              └──┬────┬────┬─┘            │ results
        ┌────────┘    │    └────────┐     │
   ┌────▼────┐  ┌─────▼────┐  ┌─────▼───┐ │
   │Researcher│ │Classifier│  │Duty agent│─┘
   └──────────┘ └──────────┘  └─────────┘
             FINISH ──► final answer
```

---

## 💰 Cost Impact
Each loop costs one supervisor call plus one worker call. A task with 4 workers needs about 5 supervisor calls. Use a cheap model (gpt-4o-mini) for the supervisor, short worker descriptions in its prompt, rule-based shortcuts, and keep the state sent to the supervisor small (summaries, not full outputs).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Supervisor | Central routing agent | केंद्रीय routing agent |
| Worker | Agent that does a task | काम करने वाला agent |
| FINISH | Stop signal | रुकने का signal |
| Routing | Choosing next agent | अगला agent चुनना |
| Step budget | Max loop count | अधिकतम loop सीमा |
| Command | LangGraph route+update | LangGraph का route+update object |

---

## ⚡ 3-Line Summary
English: A supervisor picks the next worker and decides when to finish. It gives dynamic paths and central control, but adds LLM calls. Always use enums for decisions and a max-step limit.
Hindi: Supervisor अगला worker चुनता है और तय करता है कब रुकना है। इससे dynamic paths और central control मिलता है, पर LLM calls बढ़ती हैं। Decisions के लिए enum और max-step limit ज़रूर रखो।

---

## ➡️ Next Topic
**350. Hierarchical Agents** — supervisors of supervisors, for large systems with many workers.
