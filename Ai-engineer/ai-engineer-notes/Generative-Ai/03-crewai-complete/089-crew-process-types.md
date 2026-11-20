---

# 89. Crew process types
# हिंदी में: Crew के process types (sequential बनाम hierarchical)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline with a fake `BaseLLM`). `list(Process)` printed exactly two values. Real LLM calls: not run - needs an API key.

## 🔵 Simple Definition (2-3 lines)
`Process` decides how a crew executes its tasks. There are two in this version: `Process.sequential` (tasks run in the order you list them) and `Process.hierarchical` (a manager agent decides who does what).
You pass it as `Crew(process=...)`.

## 🔵 सरल परिभाषा (Hindi)
`Process` तय करता है कि crew अपने tasks कैसे चलाएगा। इस version में दो हैं: `Process.sequential` (tasks उसी क्रम में चलते हैं जिसमें आपने लिखे) और `Process.hierarchical` (एक manager agent तय करता है कि कौन क्या करेगा)।
इसे `Crew(process=...)` में दिया जाता है।

---

## 🔴 Problem it Solves
Different problems need different control. A fixed pipeline (classify -> fetch -> write) wants predictable order and low cost. An open-ended request ("prepare a compliance plan") wants a planner that splits and assigns work. One control style cannot serve both well.

## 🔴 यह क्यों बना? (Hindi)
अलग समस्याओं को अलग control चाहिए। तय pipeline (classify -> fetch -> write) को predictable order और कम cost चाहिए। खुले अनुरोध ("compliance plan तैयार करो") को ऐसा planner चाहिए जो काम बाँटे। एक ही control style दोनों को ठीक से नहीं सँभाल सकता।

---

## 🟢 How it Works

```
SEQUENTIAL                         HIERARCHICAL
Task1 -> Task2 -> Task3            Manager (manager_llm / manager_agent)
each task needs its own agent        |-- delegates Task A -> Worker 1
output of N is context for N+1       |-- reviews result, delegates Task B -> Worker 2
no manager, fewer LLM calls          '-- validates and returns final output
```

Facts I confirmed by running:
- `list(Process)` gives `[sequential, hierarchical]`.
- Hierarchical without `manager_llm` or `manager_agent` fails: "Attribute `manager_llm` or `manager_agent` is required when using hierarchical process."
- Sequential with a task that has no agent fails: "Agent is missing in the task ...".
- Hierarchical with `manager_llm` set builds fine, and tasks may or may not name an agent (the manager picks if none is named).
- With a fake LLM the hierarchical run returned the manager model's text; a real delegation run needs a real function-calling LLM, so delegation quality itself is not verified.

## 🟢 कैसे काम करता है? (Hindi)
1. Sequential: Task1 -> Task2 -> Task3। हर task का अपना agent होना ज़रूरी है, और पिछला output अगले का context बनता है। Manager नहीं, इसलिए LLM calls कम।
2. Hierarchical: manager (`manager_llm` या `manager_agent`) काम बाँटता है, नतीजे जाँचता है और final answer देता है।
3. Hierarchical में manager न दें तो error आता है; sequential में task का agent न हो तो error आता है (दोनों मैंने चलाकर देखे)।
4. Delegation की असली गुणवत्ता real LLM के बिना जाँची नहीं गई।

---

## 🟡 Real World Example
Tariff Agent. Sequential: "classify HS code -> fetch duty -> write note" for a known flow, cheap and repeatable. Hierarchical: user asks "Can I import used medical devices from Germany to India and what will it cost?" The manager splits it into classification, licence check, duty and logistics, and assigns workers.

## 🟡 Real Example Hindi mein
Tariff Agent। Sequential: जाना-पहचाना flow "HS code तय करो -> duty निकालो -> note लिखो" - सस्ता और दोहराने योग्य। Hierarchical: user पूछता है "क्या मैं जर्मनी से used medical devices भारत मँगवा सकता हूँ और खर्च कितना होगा?" Manager इसे classification, licence check, duty और logistics में तोड़कर workers को देता है।

---

## 💻 Code Example — Basic
```python
# basic_process_types.py  (verified offline with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # core classes

LLM_NAME = "gpt-4o-mini"  # worker model string (real run needs a key)

classifier = Agent(role="Classifier", goal="Find HS code", backstory="Broker.",  # worker 1
                   llm=LLM_NAME, allow_delegation=False)  # no delegation
writer = Agent(role="Writer", goal="Write a short note", backstory="Analyst.",  # worker 2
               llm=LLM_NAME, allow_delegation=False)  # no delegation

t1 = Task(description="HS code for {item}.", expected_output="Code.", agent=classifier)  # task 1
t2 = Task(description="Duty note for {item}.", expected_output="2 lines.",  # task 2
          agent=writer, context=[t1])  # uses t1 output

sequential_crew = Crew(  # fixed pipeline
    agents=[classifier, writer],  # workers
    tasks=[t1, t2],  # order matters
    process=Process.sequential,  # run in order
)

# Hierarchical: tasks do not need an agent; a manager assigns them.
t3 = Task(description="Prepare a compliance plan for importing {item}.",  # open-ended task
          expected_output="A short plan.")  # no agent given
hier_crew = Crew(  # manager-led crew
    agents=[classifier, writer],  # worker pool
    tasks=[t3],  # tasks for the manager to split/assign
    process=Process.hierarchical,  # manager mode
    manager_llm=LLM_NAME,  # REQUIRED: the manager's model (or use manager_agent)
)

if __name__ == "__main__":  # script entry
    print(sequential_crew.kickoff(inputs={"item": "steel"}).raw)  # run pipeline
    print(hier_crew.kickoff(inputs={"item": "steel"}).raw)  # run manager mode
```

## 💻 Code Example — Advanced
```python
# advanced_process_types.py  (FastAPI + async + chooses process by request)
from __future__ import annotations  # modern annotations

from typing import Literal  # restrict the mode value

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel  # schemas
from crewai import Agent, Task, Crew, Process  # CrewAI

LLM_NAME = "gpt-4o-mini"  # worker model
MANAGER_LLM = "gpt-4o-mini"  # use a stronger model for the manager in production
app = FastAPI(title="Process-aware Tariff API")  # ASGI app


class Req(BaseModel):  # request
    question: str  # user's question
    mode: Literal["sequential", "hierarchical"] = "sequential"  # chosen process


class Res(BaseModel):  # response
    mode: str  # which process ran
    answer: str  # final text
    total_tokens: int  # usage


def workers() -> list[Agent]:  # build worker agents
    return [  # list of two workers
        Agent(role="Classifier", goal="Classify items", backstory="Broker.",  # worker 1
              llm=LLM_NAME, allow_delegation=False, max_iter=4),  # capped
        Agent(role="Writer", goal="Write notes", backstory="Analyst.",  # worker 2
              llm=LLM_NAME, allow_delegation=False, max_iter=4),  # capped
    ]


def build(mode: str) -> Crew:  # choose structure by mode
    ws = workers()  # fresh workers
    if mode == "sequential":  # fixed pipeline
        t1 = Task(description="Classify: {q}", expected_output="HS code.", agent=ws[0])  # step 1
        t2 = Task(description="Write note for: {q}", expected_output="2 lines.",  # step 2
                  agent=ws[1], context=[t1])  # uses step 1
        return Crew(agents=ws, tasks=[t1, t2], process=Process.sequential, max_rpm=30)  # assemble
    t = Task(description="Answer fully: {q}", expected_output="Clear answer.")  # manager-assigned
    return Crew(agents=ws, tasks=[t], process=Process.hierarchical,  # manager mode
                manager_llm=MANAGER_LLM, max_rpm=30)  # manager needs a model


@app.post("/ask", response_model=Res)  # route
async def ask(req: Req) -> Res:  # async handler
    try:
        crew = build(req.mode)  # may raise on invalid config
        out = await crew.akickoff(inputs={"q": req.question})  # async run
    except ValueError as exc:  # config validation problems
        raise HTTPException(400, str(exc)) from exc  # client error
    except Exception as exc:  # runtime/provider failure
        raise HTTPException(502, f"crew failed: {exc}") from exc  # upstream error
    return Res(mode=req.mode, answer=out.raw, total_tokens=out.token_usage.total_tokens)  # reply
```
Not run with a real model. Offline: `TestClient` with a fake LLM returned 200 for the sequential mode. The hierarchical branch built and ran with the fake manager text, but real delegation is not verified.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Fixed pipeline | Linear edges | `Process.sequential` | Chain of `Runner.run` calls | RoundRobinGroupChat |
| Manager/planner | Supervisor node you design | `Process.hierarchical` + `manager_llm` | Triage agent with handoffs | SelectorGroupChat (LLM picks speaker) |
| Custom routing | Conditional edges (full control) | Limited to two processes | Handoff rules | Selector function |
| Cost predictability | High (you design it) | Sequential high, hierarchical lower | Medium | Medium |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using hierarchical for a fixed pipeline "because it sounds smarter".
✅ Correct: Sequential is cheaper, faster and more predictable when the steps are known.

❌ Mistake 2: Hierarchical without `manager_llm`/`manager_agent`.
✅ Correct: Provide one; a stronger model is wise for the manager.

❌ Mistake 3: Sequential tasks with no `agent=`.
✅ Correct: Give every task an agent (validation error otherwise).

---

## 🧠 Tricky Interview Question
Your hierarchical crew produces good answers but costs 3x the sequential one and sometimes loops. Why and what do you do?

Answer: The manager adds LLM calls for planning, delegation and review, and every delegated sub-task repeats context. Loops happen when the manager keeps re-delegating. Fix: put hard `max_iter`, specify clear `expected_output` so the manager can accept results, reduce the worker pool, move the predictable part to a sequential sub-crew, and only keep hierarchical for the truly open-ended top level. Measure `token_usage` before and after.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Name the process types.
A1: `sequential` and `hierarchical`.

Q2: [Medium] What does hierarchical require?
A2: `manager_llm` or `manager_agent`.

Q3: [Hard] When would you choose sequential over hierarchical?
A3: Known steps, cost/latency sensitive, need reproducibility and easy debugging.

Q4: [Hard] How do you get branching logic that CrewAI processes do not offer?
A4: Use CrewAI Flows (separate topic) or put the branching in your own Python and call different crews, or use LangGraph for graph control.

Q5: [System Design] Design an agent that handles both simple and complex tariff questions.
A5: Classify the question first (cheap model). Simple -> sequential 2-task crew. Complex -> hierarchical crew with manager. Log tokens per route, set budget limits, fall back to human review when the manager exceeds iterations.

---

## 💰 Cost Impact
Sequential cost is about the sum of the task calls. Hierarchical adds manager planning/review calls, so expect more total tokens for the same job (measure with `result.token_usage`; I do not give a fixed multiplier because it depends on the task). Tips: cheap worker model, stronger but rarely-called manager, short outputs, `max_iter`, `max_rpm`. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- Sequential: stable pipeline, SLA, cost control.
- Hierarchical: open-ended goals needing planning and delegation.

❌ Avoid when:
- Hierarchical for simple tasks.
- Sequential when you really need dynamic re-planning.

---

## 📊 Visual Diagram
```
 Sequential                        Hierarchical
 [Task1]->[Task2]->[Task3]         +-------------+
  A        B        C              |  Manager    |<--- manager_llm / manager_agent
                                   +--+----+-----+
                                      |    |   delegate / review
                                  +---v-+ +v----+
                                  |Wkr 1| |Wkr 2|
                                  +-----+ +-----+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Process | Execution strategy of a crew | crew चलाने की रणनीति |
| sequential | Tasks in listed order | सूची के क्रम में tasks |
| hierarchical | Manager delegates work | manager काम बाँटता है |
| manager_llm | Model for the manager | manager का model |
| manager_agent | Custom manager Agent | अपना बनाया manager Agent |
| delegation | Handing a task to another agent | दूसरे agent को काम सौंपना |

---

## ⚡ 3-Line Summary
English: CrewAI has two processes: sequential (fixed order) and hierarchical (manager delegates).
Hierarchical needs a manager model and costs more calls.
Choose sequential whenever the steps are known.

Hindi: CrewAI में दो process हैं: sequential (तय क्रम) और hierarchical (manager बाँटता है)।
Hierarchical को manager model चाहिए और उसमें calls ज़्यादा लगती हैं।
कदम पहले से पता हों तो sequential चुनें।

---

## ➡️ Next Topic
**#90 Sequential Process** - a deeper look at how outputs flow from task to task and how `context` shapes it.

---
