---

# 334. Supervisor Pattern
# हिंदी में: Supervisor Pattern (निगरानी करने वाला पैटर्न)

---

## 🔵 Simple Definition (English)
In the supervisor pattern one central agent (the supervisor) looks at the current state and decides which worker agent should act next, or whether the job is finished. Workers never talk to each other directly; after each worker finishes, control returns to the supervisor. It works like a manager assigning tasks to a team.

## 🔵 सरल परिभाषा (Hindi)
Supervisor pattern में एक central agent (supervisor) current state देखकर तय करता है कि अगला worker agent कौन सा काम करेगा, या काम पूरा हो गया है या नहीं। Workers आपस में सीधे बात नहीं करते; हर worker के बाद control वापस supervisor के पास आता है। यह एक manager की तरह है जो team को काम बाँटता है।

---

## 🔴 Problem it Solves
A fixed pipeline (A then B then C) cannot adapt: some tariff requests need only the classifier, others need classifier + legal check + duty calculation. Letting agents call each other freely becomes chaotic. A supervisor gives one place that owns routing decisions, stops loops, and decides "done", which makes behaviour easier to reason about, log and test.

## 🔴 यह क्यों बना? (Hindi)
Fixed pipeline (A फिर B फिर C) adapt नहीं कर सकती: कुछ tariff requests को सिर्फ classifier चाहिए, कुछ को classifier + legal check + duty calculation। Agents को आपस में खुलकर call करने देना chaos बन जाता है। Supervisor routing का एक ही मालिक है: वह loops रोकता है और "done" तय करता है, जिससे behaviour समझना, log करना और test करना आसान होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → START → supervisor node
Step 2 → Supervisor reads state (task, what each worker already produced)
Step 3 → Supervisor returns next = one of {"classifier","duty_calc","legal", FINISH}
Step 4 → Command(goto=next) (or a conditional edge) runs that worker
Step 5 → Worker writes its result to state and ALWAYS returns to the supervisor
Step 6 → Loop continues until supervisor returns FINISH -> END
Step 7 → Guard: step counter + recursion_limit stop endless delegation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → START → supervisor node
Step 2 → Supervisor state पढ़ता है (task, हर worker ने क्या बनाया)
Step 3 → Supervisor next return करता है: {"classifier","duty_calc","legal", FINISH} में से एक
Step 4 → Command(goto=next) (या conditional edge) उस worker को चलाता है
Step 5 → Worker result state में लिखता है और हमेशा supervisor के पास लौटता है
Step 6 → Supervisor FINISH देने तक loop चलता है -> END
Step 7 → Guard: step counter + recursion_limit endless delegation रोकते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: the supervisor sees a request "Total landed cost of 100 Bluetooth speakers from China". It first sends it to `classifier` (HS code), then to `duty_calc` (rate x value), then decides `FINISH`. For "What is the HS code of a speaker?" it calls only `classifier` and finishes. **Zomato AI**: supervisor routes between `menu_agent`, `order_agent` and `refund_agent` depending on the chat.

## 🟡 Real Example Hindi mein
**Tariff System**: Supervisor को request मिलती है "China से 100 Bluetooth speakers की total landed cost"। पहले `classifier` (HS code), फिर `duty_calc` (rate x value), फिर `FINISH`। "Speaker का HS code क्या है?" पर सिर्फ `classifier` चलता है और काम खत्म। **Zomato AI**: Supervisor chat के हिसाब से `menu_agent`, `order_agent` और `refund_agent` के बीच route करता है।

---

## 💻 Code Example — Basic
```python
# Supervisor + 2 workers, rule-based supervisor so it runs offline (pip install langgraph)
from typing import Literal, TypedDict  # typing

from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.types import Command  # lets a node update state AND choose the next node


class State(TypedDict):  # shared state
    task: str  # user request
    hs_code: str  # classifier output
    duty: float  # duty_calc output


def supervisor(state: State) -> Command[Literal["classifier", "duty_calc", "__end__"]]:  # the manager
    if not state["hs_code"]:  # nothing classified yet
        return Command(goto="classifier")  # delegate to classifier
    if "cost" in state["task"] and not state["duty"]:  # needs duty and not done
        return Command(goto="duty_calc")  # delegate to duty_calc
    return Command(goto=END)  # all needed work finished


def classifier(state: State) -> Command[Literal["supervisor"]]:  # worker 1
    return Command(goto="supervisor", update={"hs_code": "8518.22"})  # report back to supervisor


def duty_calc(state: State) -> Command[Literal["supervisor"]]:  # worker 2
    return Command(goto="supervisor", update={"duty": 18.0})  # 18 percent (fake)


builder = StateGraph(State)  # builder
builder.add_node("supervisor", supervisor)  # node
builder.add_node("classifier", classifier)  # node
builder.add_node("duty_calc", duty_calc)  # node
builder.add_edge(START, "supervisor")  # always start at the manager
graph = builder.compile()  # no other edges needed: Command(goto) defines them

print(graph.invoke({"task": "HS code of speaker", "hs_code": "", "duty": 0.0}))  # only classifier ran
print(graph.invoke({"task": "landed cost of speaker", "hs_code": "", "duty": 0.0}))  # classifier + duty_calc
```

## 💻 Code Example — Advanced
```python
# LLM-style supervisor with validated structured decision, step cap, async, error handling
import asyncio  # async
from typing import Literal, TypedDict  # typing

from pydantic import BaseModel  # validates the supervisor decision (pydantic v2)
from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.types import Command  # routing + update

Worker = Literal["classifier", "duty_calc", "FINISH"]  # allowed choices
MAX_STEPS = 6  # hard cap on delegations


class Decision(BaseModel):  # what the supervisor LLM must return
    next: Worker
    reason: str


class State(TypedDict):  # state
    task: str
    hs_code: str
    duty: float
    steps: int
    log: list[str]


async def fake_llm_decide(state: State) -> dict:  # stand-in for llm.with_structured_output(Decision)
    await asyncio.sleep(0)  # simulates latency
    if not state["hs_code"]:
        return {"next": "classifier", "reason": "need HS code"}
    if "cost" in state["task"] and not state["duty"]:
        return {"next": "duty_calc", "reason": "need duty"}
    return {"next": "FINISH", "reason": "done"}


async def supervisor(state: State) -> Command[Literal["classifier", "duty_calc", "__end__"]]:  # manager
    if state["steps"] >= MAX_STEPS:  # guard against endless delegation
        return Command(goto=END, update={"log": state["log"] + ["step cap hit"]})
    try:
        decision = Decision.model_validate(await fake_llm_decide(state))  # validate LLM output
    except Exception as exc:  # malformed output -> fail safe
        return Command(goto=END, update={"log": state["log"] + [f"bad decision: {exc}"]})
    goto = END if decision.next == "FINISH" else decision.next  # map FINISH to END
    return Command(goto=goto, update={"steps": state["steps"] + 1, "log": state["log"] + [decision.reason]})


async def classifier(state: State) -> Command[Literal["supervisor"]]:  # worker
    return Command(goto="supervisor", update={"hs_code": "8518.22"})


async def duty_calc(state: State) -> Command[Literal["supervisor"]]:  # worker
    return Command(goto="supervisor", update={"duty": 18.0})


builder = StateGraph(State)  # builder
builder.add_node("supervisor", supervisor)  # node
builder.add_node("classifier", classifier)  # node
builder.add_node("duty_calc", duty_calc)  # node
builder.add_edge(START, "supervisor")  # entry
graph = builder.compile()  # compile


async def main() -> None:
    out = await graph.ainvoke({"task": "landed cost of speaker", "hs_code": "", "duty": 0.0, "steps": 0, "log": []})
    print(out["hs_code"], out["duty"], out["log"])  # 8518.22 18.0 ['need HS code', 'need duty', 'done']


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Stream worker progress to the client with Server-Sent Events so users see "classifying... calculating duty..." while the supervisor loops.

```python
import json  # to serialise events

from fastapi import FastAPI  # web
from fastapi.responses import StreamingResponse  # SSE style streaming
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Req(BaseModel):  # body
    task: str


@app.post("/supervised")
async def supervised(req: Req) -> StreamingResponse:  # route
    async def events():  # async generator for the response body
        init = {"task": req.task, "hs_code": "", "duty": 0.0, "steps": 0, "log": []}  # initial state
        async for chunk in graph.astream(init, stream_mode="updates"):  # one chunk per node run
            yield f"data: {json.dumps(chunk, default=str)}\n\n"  # SSE frame
    return StreamingResponse(events(), media_type="text/event-stream")  # stream to client
```

---

## 🔗 LangChain / LangGraph Connection
The real supervisor is an LLM with structured output (a Pydantic `Decision` or a tool-call). The `langgraph-supervisor` package offers `create_supervisor([agent1, agent2], model=llm, prompt=...)` that builds this graph and handles handoff tools for you. Workers can be `create_react_agent` agents. Hand-building it (as above) shows what that helper does.

```python
from typing import Literal  # types
from pydantic import BaseModel  # schema
from langchain_openai import ChatOpenAI  # model


class Decision(BaseModel):  # supervisor output
    next: Literal["classifier", "duty_calc", "FINISH"]


supervisor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Decision)  # structured router


def decide(task: str, hs_code: str, duty: float) -> str:  # prompt with only the needed facts
    prompt = f"Task: {task}\nhs_code_done: {bool(hs_code)}\nduty_done: {bool(duty)}\nPick next worker or FINISH."
    return supervisor_llm.invoke(prompt).next  # one small call per hop
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending the whole message history to the supervisor on every hop
✅ Correct: Give it a compact summary of what is done and what is pending.

```python
# Wrong - supervisor reads 8,000 tokens each hop
decision = supervisor_llm.invoke(state["messages"])

# Right - 100 tokens of facts
facts = f"hs_code_done={bool(state['hs_code'])}, duty_done={bool(state['duty'])}"
decision = supervisor_llm.invoke(f"{state['task']}\n{facts}")
```

❌ Mistake 2: Workers that do not return to the supervisor
✅ Correct: Every worker ends with `Command(goto="supervisor")` (or an edge back).

```python
# Wrong - classifier goes to END; duty_calc never gets a chance
def classifier(state): return Command(goto=END, update={...})

# Right
def classifier(state): return Command(goto="supervisor", update={...})
```

---

## 🧠 Tricky Interview Question

**Q**: "The supervisor keeps calling `classifier` again and again though the code is already in state. Why, and how do you fix it?"

**Answer**: The supervisor's prompt or state view does not show that the classifier already finished (for example, the worker's result was written to a field the supervisor never reads, or the history is truncated). LLM supervisors also repeat actions when "done" criteria are vague. Fixes: (1) give the supervisor explicit status flags (`hs_code_done: true`), (2) use structured output with an enum and explain each worker's output in the prompt, (3) add deterministic guards before the LLM (if `hs_code` exists, remove `classifier` from the options), (4) cap steps and detect repeated choices. The root cause is information design, not the pattern.

---

## ⚫ Interview Questions + Answers

Q1: What does the supervisor do? (Easy)
A1: It decides which worker acts next (or FINISH) based on state, and receives control back after each worker.

Q2: How is it different from a fixed pipeline? (Easy)
A2: A pipeline always runs the same sequence. A supervisor chooses dynamically, can skip workers, repeat them or stop early.

Q3: What is `Command` and why is it used here? (Medium)
A3: `Command(goto=..., update=...)` lets a node update state and choose the next node in one return value, so the supervisor and workers do not need pre-declared conditional edges.

Q4: Drawbacks of the supervisor pattern? (Medium)
A4: Extra LLM call per hop (cost and latency), single point of failure/bottleneck, supervisor prompt can become complex, and workers cannot collaborate directly.

Q5: How would you scale the pattern to 20 specialised workers? (Hard)
A5: Use hierarchical supervisors: a top supervisor picks a team (tariff, legal, logistics), and each team has its own sub-supervisor in a sub-graph with 3-5 workers. This keeps each routing prompt small and accurate. Add rule-based pre-routing for obvious cases, cache decisions, and log routing accuracy on an eval set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks vary and need different worker combinations
- You want central control, logging and guardrails
- Workers are independent specialists

❌ Avoid when:
- A fixed sequence is enough (use a pipeline)
- Workers need rich peer-to-peer collaboration (consider swarm)
- Latency is critical and the extra routing call hurts

---

## 📊 Visual Diagram
```
                 ┌──────────────┐
      START ───► │  SUPERVISOR  │ ◄────────────┐
                 └──┬────┬────┬─┘              │
          classifier│    │duty_calc            │ (each worker
                    ▼    ▼    │FINISH          │  returns here)
              [classifier] [duty_calc]          │
                    └────┴──────────────────────┘
                                │
                                ▼
                               END
```

---

## 💰 Cost Impact
- Each hop costs one supervisor call (~200 input tokens + ~20 output with a compact prompt) plus the worker's own call. A request needing 2 workers = 3 supervisor calls (before each worker and one to finish).
- With `gpt-4o-mini`, 3 routing calls of ~220 tokens cost about $0.0001. With a long message history (3,000 tokens per hop) it becomes 15x more.
- Optimise: compact status prompt, rule-based shortcuts, small model for the supervisor, structured output (short answers), and step caps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Supervisor | Central agent that routes work | काम बाँटने वाला central agent |
| Worker | Specialist agent doing a task | विशेषज्ञ worker |
| Command | Return value: update state + goto | State update + अगला node |
| FINISH | Supervisor decision to stop | रुकने का फैसला |
| Hierarchical | Supervisors managing supervisors | Supervisor के ऊपर supervisor |
| Delegation | Handing a task to a worker | काम सौंपना |

---

## ⚡ 3-Line Summary
English: A supervisor agent picks the next worker (or FINISH) using the shared state, and every worker reports back to it. This gives central control over dynamic workflows. Keep its prompt compact, validate its output and cap the steps.
Hindi: Supervisor agent shared state देखकर अगला worker (या FINISH) चुनता है और हर worker उसी के पास लौटता है। इससे dynamic workflows पर central control मिलता है। उसका prompt छोटा रखो, output validate करो और steps सीमित करो।

---

## ➡️ Next Topic
**335. Swarm Pattern** — no central manager; agents hand control directly to each other.
