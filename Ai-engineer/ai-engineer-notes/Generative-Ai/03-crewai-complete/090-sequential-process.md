---

# 90. Sequential Process
# हिंदी में: Sequential Process (tasks एक के बाद एक)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline with a fake `BaseLLM` that prints the prompt it receives). Real LLM calls: not run - needs an API key.

## 🔵 Simple Definition (2-3 lines)
In `Process.sequential` the crew runs tasks in the exact order of the `tasks` list. Each task must have an agent, and the output of earlier tasks flows into later ones as context.
The last task's output becomes `CrewOutput.raw`.

## 🔵 सरल परिभाषा (Hindi)
`Process.sequential` में crew `tasks` list के ठीक क्रम में tasks चलाता है। हर task का एक agent होना ज़रूरी है, और पहले वाले tasks के output अगले tasks को context के रूप में मिलते हैं।
आखिरी task का output ही `CrewOutput.raw` बनता है।

---

## 🔴 Problem it Solves
Many agent jobs are plain pipelines. You want predictable behaviour, low cost, easy debugging and no extra "manager" LLM. Sequential gives that: step 2 always runs after step 1, with step 1's result in front of it.

## 🔴 यह क्यों बना? (Hindi)
बहुत से agent jobs सीधी pipeline होते हैं। आपको predictable व्यवहार, कम cost, आसान debugging और कोई अतिरिक्त "manager" LLM नहीं चाहिए। Sequential यही देता है: step 2 हमेशा step 1 के बाद चलता है और उसके सामने step 1 का result होता है।

---

## 🟢 How it Works

```
Step 1 -> Task 1 prompt = description + expected_output
Step 2 -> Task 1 output saved as TaskOutput
Step 3 -> Task 2 prompt = its description + "context" (previous output)
Step 4 -> If task has context=[...], ONLY those tasks' outputs are passed
Step 5 -> ... repeat; last output = CrewOutput.raw
Step 6 -> tasks_output keeps every task's output in order
```

What the fake LLM printed for the prompts (3 tasks A -> B -> C; C had `context=[A]`):
- Task A prompt had no "context" block.
- Task B (no explicit `context`) received A's output automatically ("This is the context you're working with: HS7208").
- Task C (explicit `context=[A]`) received ONLY A's output, not B's. So explicit `context` overrides the default "previous output" behaviour.
- Validation: a sequential task with no `agent` fails with "Agent is missing in the task".

## 🟢 कैसे काम करता है? (Hindi)
1. Task 1 अपने description और expected_output से चलता है।
2. उसका output `TaskOutput` में रखा जाता है।
3. Task 2 को अपने prompt के साथ पिछला output context के रूप में मिलता है (मैंने prompt print करके देखा)।
4. अगर task में `context=[...]` दिया है तो सिर्फ वही outputs जाते हैं (मेरे test में C को सिर्फ A मिला, B नहीं)।
5. आखिरी task का output final result है; `tasks_output` में सब outputs क्रम से रहते हैं।
6. Task में agent न हो तो validation error आता है।

---

## 🟡 Real World Example
Tariff Agent: (1) classify item to HS code, (2) fetch duty rate for that code, (3) write a customer note that needs BOTH the HS code and the rate, so Task 3 uses `context=[t1, t2]`. Research Agent: search -> summarise -> critique -> rewrite.

## 🟡 Real Example Hindi mein
Tariff Agent: (1) item का HS code तय करो, (2) उस code की duty निकालो, (3) customer note लिखो जिसे HS code और rate दोनों चाहिए, इसलिए Task 3 में `context=[t1, t2]`। Research Agent: search -> summary -> critique -> rewrite।

---

## 💻 Code Example — Basic
```python
# basic_sequential.py  (verified offline with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # core classes

LLM_NAME = "gpt-4o-mini"  # model string; real run needs OPENAI_API_KEY


def agent(role: str) -> Agent:  # helper to cut repetition
    return Agent(role=role, goal=f"Do {role} work", backstory="Trade expert.",  # fields
                 llm=LLM_NAME, allow_delegation=False)  # no delegation


classifier, fetcher, writer = agent("Classifier"), agent("Duty Fetcher"), agent("Writer")  # 3 agents

t1 = Task(description="HS code for {item}.", expected_output="HS code.", agent=classifier)  # step 1
t2 = Task(description="Duty rate for that HS code.", expected_output="Rate.", agent=fetcher)  # step 2 (auto context = t1)
t3 = Task(  # step 3
    description="Write a customer note for {item}.",  # prompt
    expected_output="3 lines.",  # contract
    agent=writer,  # owner
    context=[t1, t2],  # explicit: needs BOTH outputs
)

crew = Crew(  # pipeline
    agents=[classifier, fetcher, writer],  # all workers
    tasks=[t1, t2, t3],  # order = execution order
    process=Process.sequential,  # explicit (also the default)
)

if __name__ == "__main__":  # script entry
    out = crew.kickoff(inputs={"item": "steel"})  # run
    for i, t in enumerate(out.tasks_output, 1):  # every task result
        print(i, t.agent, "->", t.raw[:50])  # which agent, what text
    print("FINAL:", out.raw)  # last task output
```

## 💻 Code Example — Advanced
```python
# advanced_sequential.py  (FastAPI + async + per-step timing + error handling)
from __future__ import annotations  # modern annotations

import time  # timing

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel, Field  # schemas
from crewai import Agent, Task, Crew, Process  # CrewAI
from crewai.tasks.task_output import TaskOutput  # callback argument type

LLM_NAME = "gpt-4o-mini"  # replace with your model
app = FastAPI(title="Sequential Tariff Pipeline")  # ASGI app


class Req(BaseModel):  # request
    item: str = Field(..., min_length=2, max_length=80)  # product name


class Step(BaseModel):  # one step report
    agent: str  # who did it
    seconds: float  # time since previous step
    preview: str  # first chars of output


class Res(BaseModel):  # response
    final: str  # last task output
    steps: list[Step]  # per-step details
    total_tokens: int  # usage


def build(steps: list[Step]) -> Crew:  # per-request crew with timing callbacks
    last: list[float] = [time.perf_counter()]  # mutable "previous timestamp"

    def record(o: TaskOutput) -> None:  # callback for every task
        now: float = time.perf_counter()  # current time
        steps.append(Step(agent=str(o.agent), seconds=round(now - last[0], 3),  # build row
                          preview=o.raw[:60]))  # short preview
        last[0] = now  # move marker

    def ag(role: str) -> Agent:  # small factory
        return Agent(role=role, goal=f"{role} work", backstory="Expert.",  # fields
                     llm=LLM_NAME, allow_delegation=False, max_iter=4)  # cap loops

    a, b, c = ag("Classifier"), ag("Duty Fetcher"), ag("Writer")  # agents
    t1 = Task(description="HS code for {item}.", expected_output="Code.", agent=a)  # step 1
    t2 = Task(description="Duty for that code.", expected_output="Rate.", agent=b)  # step 2
    t3 = Task(description="Customer note for {item}.", expected_output="3 lines.",  # step 3
              agent=c, context=[t1, t2])  # both outputs
    return Crew(agents=[a, b, c], tasks=[t1, t2, t3], process=Process.sequential,  # assemble
                task_callback=record, max_rpm=30)  # crew-level callback for every task


@app.post("/pipeline", response_model=Res)  # route
async def pipeline(req: Req) -> Res:  # async handler
    steps: list[Step] = []  # request-local list
    try:
        out = await build(steps).akickoff(inputs={"item": req.item})  # async run
    except Exception as exc:  # provider/validation failure
        raise HTTPException(502, f"pipeline failed: {exc}") from exc  # map to HTTP
    return Res(final=out.raw, steps=steps, total_tokens=out.token_usage.total_tokens)  # reply
```
Not run with a real model. Offline via `TestClient` with a fake LLM: 200 with three step rows.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Pipeline | Nodes + edges | `Process.sequential` | Chain of runs / handoffs | RoundRobinGroupChat / manual |
| Passing data | Shared state | Auto previous output or `context=[...]` | Your variables | Chat history |
| Resume after crash | Checkpointer | Checkpoint support exists but verify for your use | Your code | Save/load state |
| Error in step N | Retry node / edges | Exception propagates from `kickoff` | Exception from `Runner.run` | Exception from `run` |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Assuming Task 3 sees Task 1 and Task 2 without `context`.
✅ Correct: Without explicit `context` it gets the previous output; list all needed tasks in `context=[...]`.

❌ Mistake 2: Giving `context=[t1]` to a task and then wondering why it ignores t2's data.
✅ Correct: Explicit context overrides default (I observed this); include every required task.

❌ Mistake 3: Putting tasks in the wrong order in the list.
✅ Correct: List order is the run order.

---

## 🧠 Tricky Interview Question
Task 3 writes a note that contradicts the duty rate fetched in Task 2. Prompts look fine. What is the likely bug?

Answer: Task 3 had `context=[t1]` only, so Task 2's output never reached it (explicit context replaces the default previous-output context). The writer guessed. Fix: `context=[t1, t2]`. Also add a guardrail or structured output (`output_pydantic`) so the rate is a typed field, and add a test that prints the prompt of each task to confirm what context was sent.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] In what order do tasks run in sequential mode?
A1: The order of the `tasks` list.

Q2: [Medium] How does Task 2 get Task 1's output?
A2: By default as context; or explicitly with `context=[t1]`.

Q3: [Hard] What happens if a task has explicit context?
A3: Only those tasks' outputs are passed (confirmed by prompt inspection in 1.15.41).

Q4: [Hard] How do you run two independent steps faster inside a sequential crew?
A4: `async_execution=True` on both, then a synchronous task with `context=[both]`.

Q5: [System Design] Add retries and resume to a 6-step pipeline.
A5: Wrap each step in a typed output (`output_pydantic`), persist after each task callback, use idempotency keys, and on retry skip steps already stored (or split into separate crews per stage); add timeouts and a dead-letter queue.

---

## 💰 Cost Impact
Each task is at least one LLM call (more with tools). Later tasks carry earlier outputs in their prompt, so input tokens grow along the pipeline. I cannot give exact token numbers without a real model; measure with `result.token_usage`. Tips: ask early tasks for short structured outputs, pass only needed tasks via `context`, cheap model for mechanical steps, set `max_iter`. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- Known linear workflow.
- You want predictable cost and debugging.

❌ Avoid when:
- You need loops, branching or dynamic planning (hierarchical, Flows, LangGraph).
- Steps are independent and latency matters (add async tasks).

---

## 📊 Visual Diagram
```
 inputs
   |
   v
 [Task1: Classifier] --out1--> [Task2: Fetcher] --out2--+
        |                                               |
        +-------------------out1------------------------+--> [Task3: Writer, context=[t1,t2]]
                                                              |
                                                              v
                                                       CrewOutput.raw (last task)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| sequential | One task after another | एक के बाद एक task |
| context | Earlier outputs given to a task | पिछले outputs जो task को मिलते हैं |
| tasks_output | List of all task results | सभी task results की list |
| pipeline | Chain of steps | कदमों की श्रृंखला |
| task_callback | Crew-level hook per task | हर task पर crew-level hook |
| explicit context | Chosen list of tasks | चुनी हुई tasks की सूची |

---

## ⚡ 3-Line Summary
English: Sequential runs tasks in list order and every task needs an agent.
Previous output is passed by default; explicit `context=[...]` replaces that default.
It is cheapest and easiest to debug.

Hindi: Sequential tasks को list के क्रम में चलाता है और हर task को agent चाहिए।
पिछला output default में मिलता है; explicit `context=[...]` उस default की जगह ले लेता है।
यह सबसे सस्ता और debug करने में आसान है।

---

## ➡️ Next Topic
**#91 Hierarchical Process** - when the steps are not known upfront, a manager agent plans and delegates.

---
