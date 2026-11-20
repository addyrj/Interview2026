---

# 87. Task async_execution
# हिंदी में: Task async_execution (tasks को parallel चलाना)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline with a fake LLM that sleeps 1 second per call). Real LLM calls: not run - needs an API key.

## 🔵 Simple Definition (2-3 lines)
`Task(async_execution=True)` lets that task run in the background while the crew moves on to the next task. A later task that lists it in `context=[...]` waits for its result.
It is the CrewAI way to run independent tasks in parallel.

## 🔵 सरल परिभाषा (Hindi)
`Task(async_execution=True)` उस task को background में चलाता है और crew अगले task पर आगे बढ़ जाता है। जो बाद वाला task उसे `context=[...]` में रखता है, वह उसका result आने तक रुकता है।
यह independent tasks को parallel चलाने का CrewAI तरीका है।

---

## 🔴 Problem it Solves
A sequential crew runs Task 1, then Task 2, then Task 3, even when 1 and 2 do not depend on each other. If each takes 10 seconds of LLM time, you wait 30 seconds instead of about 20. For a tariff report that needs "duty rate" and "import restrictions" from separate sources, this is wasted time.

## 🔴 यह क्यों बना? (Hindi)
Sequential crew Task 1, फिर Task 2, फिर Task 3 चलाता है, भले ही 1 और 2 एक-दूसरे पर निर्भर न हों। हर task में 10 सेकंड लगें तो 20 की जगह 30 सेकंड इंतज़ार करना पड़ता है। Tariff report में "duty rate" और "import restrictions" अलग sources से चाहिए, तो यह वक्त की बर्बादी है।

---

## 🟢 How it Works

```
Step 1 -> Task A (async_execution=True) starts in a worker thread
Step 2 -> Task B (async_execution=True) starts immediately, does not wait for A
Step 3 -> Task C (sync, context=[A, B]) waits until A and B finish
Step 4 -> C gets both outputs as context and writes the final answer
Step 5 -> CrewOutput.tasks_output keeps the order A, B, C
```

What I measured/confirmed (fake LLM, 1 s per call):
- All three sync: about 3.1 s. A and B async + C sync: about 2.1 s. So parallel saved one call time.
- `tasks_output` stayed in order `['A', 'B', 'C']`.
- A crew whose LAST task is async fails validation: "The crew must end with at most one asynchronous task" (in my run, three async tasks in a row, the last one included, were rejected). Keep the final task synchronous.
- Do not confuse this with `await crew.akickoff()` / `kickoff_async()`: those make the whole crew awaitable from asyncio code; `async_execution` makes individual tasks parallel inside one crew. You can use both.

## 🟢 कैसे काम करता है? (Hindi)
1. Task A (`async_execution=True`) एक अलग thread में शुरू होता है।
2. Task B भी तुरंत शुरू होता है, A का इंतज़ार नहीं करता।
3. Task C (sync, `context=[A, B]`) तब तक रुकता है जब तक A और B खत्म न हों।
4. C को दोनों outputs context में मिलते हैं।
5. मेरे test में 3 sync tasks लगभग 3.1 s लगे, और A-B async होने पर लगभग 2.1 s।
6. आखिरी task async नहीं रखना; वरना crew validation error देता है।
7. `akickoff()` पूरे crew को asyncio में awaitable बनाता है; `async_execution` crew के अंदर tasks को parallel करता है - दोनों साथ चल सकते हैं।

---

## 🟡 Real World Example
Tariff Agent: Task A "fetch duty rate", Task B "fetch import restrictions / licences" run in parallel (different tools). Task C "compose compliance report" has `context=[A, B]`. Research Agent: three searches in parallel, one writer at the end.

## 🟡 Real Example Hindi mein
Tariff Agent: Task A "duty rate लाओ" और Task B "import restrictions / licences लाओ" parallel चलते हैं (अलग tools)। Task C "compliance report बनाओ" में `context=[A, B]` है। Research Agent: तीन searches parallel, आखिर में एक writer।

---

## 💻 Code Example — Basic
```python
# basic_async_execution.py  (verified offline with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # core classes

LLM_NAME = "gpt-4o-mini"  # model string; real run needs OPENAI_API_KEY


def make_agent(role: str) -> Agent:  # small factory to avoid repetition
    return Agent(  # build an agent
        role=role,  # role text
        goal=f"Do the {role} job well",  # goal text
        backstory="Experienced trade-compliance specialist.",  # backstory
        llm=LLM_NAME,  # model
        allow_delegation=False,  # no delegation
    )


duty_agent = make_agent("Duty Researcher")  # agent 1
rules_agent = make_agent("Restrictions Researcher")  # agent 2
writer = make_agent("Compliance Writer")  # agent 3

duty = Task(  # independent task 1
    description="Find the import duty for {item}.",  # prompt
    expected_output="Duty rate and legal basis.",  # contract
    agent=duty_agent,  # owner
    async_execution=True,  # run in background
)
rules = Task(  # independent task 2
    description="Find import restrictions or licences for {item}.",  # prompt
    expected_output="List of restrictions.",  # contract
    agent=rules_agent,  # owner
    async_execution=True,  # run in background, in parallel with duty
)
report = Task(  # final dependent task
    description="Write one compliance summary for {item}.",  # prompt
    expected_output="Short summary paragraph.",  # contract
    agent=writer,  # owner
    context=[duty, rules],  # waits for both async tasks
)  # NOTE: the last task stays synchronous

crew = Crew(  # assemble
    agents=[duty_agent, rules_agent, writer],  # all agents
    tasks=[duty, rules, report],  # order matters for context
    process=Process.sequential,  # sequential process, async tasks overlap
)

if __name__ == "__main__":  # script entry
    out = crew.kickoff(inputs={"item": "steel"})  # run
    print([t.raw for t in out.tasks_output])  # outputs in task order
    print(out.token_usage)  # token metrics
```

## 💻 Code Example — Advanced
```python
# advanced_async_execution.py  (FastAPI + asyncio + timeout + error handling)
from __future__ import annotations  # modern annotations

import asyncio  # for wait_for timeout
import time  # latency measurement

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel, Field  # validation
from crewai import Agent, Task, Crew, Process  # CrewAI

LLM_NAME = "gpt-4o-mini"  # replace with your model
TIMEOUT_S: float = 90.0  # hard limit per request
app = FastAPI(title="Parallel Tariff Crew")  # ASGI app


class Req(BaseModel):  # request schema
    item: str = Field(..., min_length=2, max_length=80)  # product


class Res(BaseModel):  # response schema
    summary: str  # final text
    parts: list[str]  # outputs of all tasks
    seconds: float  # wall time
    total_tokens: int  # token usage


def build_crew() -> Crew:  # build per request, no shared mutable state
    def agent(role: str) -> Agent:  # helper
        return Agent(role=role, goal=f"Do {role}", backstory="Trade expert.",  # fields
                     llm=LLM_NAME, allow_delegation=False, max_iter=4)  # cap loops
    a, b, c = agent("Duty"), agent("Restrictions"), agent("Writer")  # three agents
    t1 = Task(description="Duty for {item}.", expected_output="Rate.",  # parallel task 1
              agent=a, async_execution=True)  # background
    t2 = Task(description="Restrictions for {item}.", expected_output="List.",  # parallel task 2
              agent=b, async_execution=True)  # background
    t3 = Task(description="Summarise for {item}.", expected_output="Paragraph.",  # final
              agent=c, context=[t1, t2])  # waits for t1, t2
    return Crew(agents=[a, b, c], tasks=[t1, t2, t3], process=Process.sequential)  # assemble


@app.post("/compliance", response_model=Res)  # route
async def compliance(req: Req) -> Res:  # async handler (does not block event loop)
    start: float = time.perf_counter()  # start timer
    crew: Crew = build_crew()  # new crew
    try:
        out = await asyncio.wait_for(  # enforce timeout
            crew.akickoff(inputs={"item": req.item}), timeout=TIMEOUT_S)  # async kickoff
    except asyncio.TimeoutError as exc:  # too slow
        raise HTTPException(504, "crew timed out") from exc  # gateway timeout
    except Exception as exc:  # any other failure
        raise HTTPException(502, f"crew failed: {exc}") from exc  # bad gateway
    return Res(  # reply
        summary=out.raw,  # final answer
        parts=[t.raw for t in out.tasks_output],  # every task output
        seconds=round(time.perf_counter() - start, 2),  # elapsed seconds
        total_tokens=out.token_usage.total_tokens,  # usage
    )
```
Not run with a real model. Run via FastAPI `TestClient` with a fake LLM: HTTP 200 and three task outputs returned.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Parallel steps | Fan-out edges / `Send` | `Task(async_execution=True)` | `asyncio.gather` on `Runner.run` | `asyncio.gather` on agents, or group chat |
| Join point | Reducer / join node | Task `context=[...]` | Your code after gather | Your code / next agent |
| Whole-run async | `ainvoke` | `akickoff()` / `kickoff_async()` | `Runner.run` (async) | `await team.run()` |
| Guardrail on structure | Graph schema | Crew must not end with async tasks | None | None |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Marking the last task async.
✅ Correct: Keep the final task synchronous (validation rejects it otherwise).

❌ Mistake 2: Making dependent tasks async and not listing context.
✅ Correct: If C needs A and B, put `context=[A, B]`; otherwise C may not see their output.

❌ Mistake 3: Expecting 10x speedup. Provider rate limits (RPM/TPM) throttle you.
✅ Correct: Parallelise a few independent tasks, set `max_rpm`, and handle 429 with retries.

---

## 🧠 Tricky Interview Question
You mark all tasks `async_execution=True` for speed and the crew will not even start. Why, and what is the right design?

Answer: A crew must end with at most one async task. More important: tasks that depend on earlier outputs must wait. Make independent research tasks async, then end with one synchronous aggregation task that has `context=[...]` of all of them. Also check that parallel tool calls are thread-safe (shared HTTP clients, DB sessions) and that rate limits allow it.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `async_execution=True` do?
A1: Runs that task in the background so the crew can start the next task.

Q2: [Medium] How does a later task use the async results?
A2: Through `context=[task_a, task_b]`; CrewAI waits for them.

Q3: [Hard] Difference between `async_execution` and `akickoff`?
A3: `async_execution` parallelises tasks inside one crew. `akickoff`/`kickoff_async` lets your async program await a whole crew without blocking the event loop.

Q4: [Hard] What are the risks of parallel tasks?
A4: Rate limits, non-thread-safe tools, nondeterministic ordering of logs/callbacks, harder debugging, bigger burst of cost.

Q5: [System Design] Run 50 product lookups per request.
A5: Do not put 50 tasks in one crew. Fan out with `asyncio.Semaphore(5)` and one small crew per item (`akickoff`), collect with `gather(return_exceptions=True)`, cache by item, and return partial results with per-item errors.

---

## 💰 Cost Impact
Parallel execution does NOT reduce tokens; it reduces latency. Total cost is the same sum of all task prompts and completions (verify prices on the provider page - they change). It can raise peak spend per second and hit rate limits. The final aggregation task reads the earlier outputs as context, so its input tokens grow with their size - ask the parallel tasks for short, structured outputs.

## 🔷 When to Use
✅ Use when:
- Tasks are independent (different sources/tools).
- Latency matters more than burst load.

❌ Avoid when:
- Task B needs A's result.
- Tools or clients are not thread-safe.
- You are close to the provider rate limit.

---

## 📊 Visual Diagram
```
            +--------------------+
  start --> | Task A (async)     |--\
     |      +--------------------+   \
     |                                 +--> Task C (sync, context=[A,B]) --> CrewOutput
     |      +--------------------+   /
     +----> | Task B (async)     |--/
            +--------------------+
   time: |----- max(A,B) -----|--- C ---|     (sequential would be A + B + C)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| async_execution | Run task in background | task को background में चलाना |
| context | Earlier tasks whose output is passed in | पिछले tasks जिनका output मिलता है |
| akickoff | Awaitable crew run | await होने वाला crew run |
| fan-out / join | Split work, then merge | काम बाँटना, फिर जोड़ना |
| rate limit | Provider cap on requests/tokens | provider की request/token सीमा |
| latency | Time to answer | जवाब आने में लगा समय |

---

## ⚡ 3-Line Summary
English: `async_execution=True` runs independent tasks in parallel inside a crew.
Join them with `context=[...]` in a final synchronous task; the crew cannot end with an async task.
It cuts latency, not tokens.

Hindi: `async_execution=True` crew के अंदर independent tasks को parallel चलाता है।
उन्हें आखिरी synchronous task में `context=[...]` से जोड़ें; crew async task पर खत्म नहीं हो सकता।
यह latency घटाता है, tokens नहीं।

---

## ➡️ Next Topic
**#88 Crew - Complete Guide** - now that you know tasks, we look at the `Crew` object that wires agents, tasks, process, memory and callbacks together.

---
