---

# 86. Task callback
# हिंदी में: Task callback (task खत्म होते ही चलने वाला function)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline with a fake LLM based on `BaseLLM`). Real LLM calls: not run - needs an API key.

## 🔵 Simple Definition (2-3 lines)
`Task(callback=fn)` registers a Python function that CrewAI calls once when that task finishes. The function receives the `TaskOutput` of the task.
Use it for side effects: log, notify, save metrics, push to a queue.

## 🔵 सरल परिभाषा (Hindi)
`Task(callback=fn)` एक Python function register करता है जिसे वह task खत्म होने पर CrewAI एक बार call करता है। Function को उस task का `TaskOutput` मिलता है।
इसे side effects के लिए इस्तेमाल करें: log, notification, metrics, queue में भेजना।

---

## 🔴 Problem it Solves
Without a callback you only know the result after the whole crew ends. For a 5-task crew you cannot report "step 2 done" to a UI, store partial results, or alert on a bad intermediate answer. Polling or wrapping every task by hand is messy.

## 🔴 यह क्यों बना? (Hindi)
Callback के बिना पूरा crew खत्म होने के बाद ही result पता चलता है। 5-task वाले crew में आप UI को "step 2 पूरा" नहीं बता सकते, आंशिक results store नहीं कर सकते, और बीच के खराब answer पर alert नहीं दे सकते। हर task को हाथ से wrap करना गंदा तरीका है।

---

## 🟢 How it Works

```
Step 1 -> Task A runs (agent + LLM + tools)
Step 2 -> Task A produces TaskOutput (raw, pydantic, json_dict, agent, ...)
Step 3 -> CrewAI calls task_a.callback(task_output)
Step 4 -> Your function logs / stores / notifies
Step 5 -> Task B starts (callback exceptions are YOUR responsibility to catch)
```

What I confirmed by running 1.15.41:
- `callback` receives a `TaskOutput`; `o.raw` is the final text.
- In my run with one task, the order was: `before_kickoff` -> tool/step events -> task callback -> `after_kickoff`.
- `Crew(task_callback=fn)` is a separate crew-level hook that fires for every task; `Task(callback=fn)` is only for one task.
- pydantic warns that a lambda callback cannot be saved in a checkpoint. Prefer module-level named functions.

## 🟢 कैसे काम करता है? (Hindi)
1. Task A चलता है और `TaskOutput` बनाता है।
2. CrewAI `task_a.callback(task_output)` call करता है।
3. आपका function log या store करता है।
4. फिर Task B शुरू होता है।
5. `Task(callback=...)` सिर्फ एक task के लिए है; `Crew(task_callback=...)` हर task के बाद चलता है।
6. Lambda की जगह नाम वाला module-level function रखें (checkpoint warning से बचने के लिए)।

---

## 🟡 Real World Example
Tariff Agent pipeline: Task 1 classifies the HS code, Task 2 fetches duty, Task 3 writes the report. A callback on Task 1 stores the HS code in the database and sends a "classified" event to the UI over websocket. A callback on Task 3 sends an email with the report.

## 🟡 Real Example Hindi mein
Tariff Agent pipeline: Task 1 HS code तय करता है, Task 2 duty निकालता है, Task 3 report लिखता है। Task 1 के callback में HS code database में जाता है और UI को websocket से "classified" event जाता है। Task 3 के callback में report की email चली जाती है।

---

## 💻 Code Example — Basic
```python
# basic_task_callback.py  (verified offline with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # core classes
from crewai.tasks.task_output import TaskOutput  # type of the callback argument

LLM_NAME = "gpt-4o-mini"  # model string (needs OPENAI_API_KEY for a real run)

events: list[str] = []  # simple in-memory event log


def on_classified(output: TaskOutput) -> None:  # named function, not a lambda
    events.append(f"classified: {output.raw[:60]}")  # store first 60 chars
    print("callback fired, chars:", len(output.raw))  # visible proof


agent = Agent(  # one worker agent
    role="HS Code Classifier",  # role
    goal="Pick the best HS code for the item",  # goal
    backstory="Customs broker with many years of experience.",  # backstory
    llm=LLM_NAME,  # model
    allow_delegation=False,  # no delegation
)

task = Task(  # the task that owns the callback
    description="Classify {item} into an HS code.",  # prompt
    expected_output="HS code with one-line reason.",  # output contract
    agent=agent,  # owner
    callback=on_classified,  # called once when this task finishes
)

crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)  # assemble

if __name__ == "__main__":  # script entry
    result = crew.kickoff(inputs={"item": "steel"})  # run
    print(result.raw)  # final answer
    print(events)  # what the callback recorded
```

## 💻 Code Example — Advanced
```python
# advanced_task_callback.py  (FastAPI + async + safe callback + type hints)
from __future__ import annotations  # modern annotations

import logging  # structured logs
import time  # measure elapsed time
from typing import Callable  # type of callback factory result

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel  # request/response models
from crewai import Agent, Task, Crew, Process  # CrewAI core
from crewai.tasks.task_output import TaskOutput  # callback arg type

LLM_NAME = "gpt-4o-mini"  # replace with your model
log = logging.getLogger("tariff")  # app logger
app = FastAPI(title="Tariff API with callbacks")  # ASGI app


class Req(BaseModel):  # request body
    item: str  # product to analyse


class Res(BaseModel):  # response body
    answer: str  # final text
    steps: list[str]  # what callbacks observed
    total_tokens: int  # usage


def make_callback(sink: list[str], name: str) -> Callable[[TaskOutput], None]:  # closure factory
    started: float = time.perf_counter()  # when this request started

    def _cb(output: TaskOutput) -> None:  # the real callback
        try:  # a callback must never crash the crew
            elapsed: float = time.perf_counter() - started  # seconds since start
            sink.append(f"{name} done in {elapsed:.2f}s, {len(output.raw)} chars")  # record
            log.info("task %s finished", name)  # log it
        except Exception:  # swallow and log, do not break the run
            log.exception("callback failed for %s", name)  # keep stack trace

    return _cb  # hand the closure to Task


def build_crew(sink: list[str]) -> Crew:  # per-request crew
    a: Agent = Agent(role="Classifier", goal="Classify", backstory="Broker.",  # agent 1
                     llm=LLM_NAME, allow_delegation=False)  # no delegation
    b: Agent = Agent(role="Writer", goal="Write", backstory="Analyst.",  # agent 2
                     llm=LLM_NAME, allow_delegation=False)  # no delegation
    t1: Task = Task(description="Classify {item}.", expected_output="HS code.",  # task 1
                    agent=a, callback=make_callback(sink, "classify"))  # own callback
    t2: Task = Task(description="Write a one-paragraph duty note for {item}.",  # task 2
                    expected_output="One paragraph.", agent=b, context=[t1],  # uses t1 output
                    callback=make_callback(sink, "write"))  # own callback
    return Crew(agents=[a, b], tasks=[t1, t2], process=Process.sequential)  # assemble


@app.post("/analyse", response_model=Res)  # route
async def analyse(req: Req) -> Res:  # async handler
    steps: list[str] = []  # request-local sink (no global state)
    crew: Crew = build_crew(steps)  # new crew
    try:
        out = await crew.akickoff(inputs={"item": req.item})  # async run
    except Exception as exc:  # provider/network errors
        raise HTTPException(502, f"crew failed: {exc}") from exc  # map error
    return Res(answer=out.raw, steps=steps, total_tokens=out.token_usage.total_tokens)  # reply
```
Not run with a real model. Run offline with a fake LLM through FastAPI `TestClient`: both callbacks fired and the response listed two steps.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Per-step hook | Code inside a node, or `stream()` events | `Task(callback=fn)` | `RunHooks` / lifecycle hooks | Event/message stream, handlers |
| Hook gets | State | `TaskOutput` | Context + agent/tool info | Message |
| Crew-wide hook | Graph-level callbacks | `Crew(task_callback=...)` | Run-level hooks | Termination/handlers |
| Sync or async | Both | Plain function (sync) | Async methods | Async |
| Failure isolation | Your try/except | Your try/except | Your try/except | Your try/except |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Doing slow I/O (email, HTTP) directly in the callback, blocking the run.
✅ Correct: Push to a queue or background task; keep the callback fast.

❌ Mistake 2: Using a global list as sink in a web API; requests mix their events.
✅ Correct: Create the sink and the callback per request (closure factory as above).

❌ Mistake 3: Raising an exception inside the callback.
✅ Correct: Wrap in try/except and log; a monitoring hook must not kill the business flow.

---

## 🧠 Tricky Interview Question
A callback on Task 2 sends the report by email. Sometimes the customer gets two emails. Why?

Answer: Retries. If a guardrail fails, or the whole crew is retried by your API layer or a queue (at-least-once delivery), the task runs again and the callback fires again. A callback is a notification of an attempt, not an exactly-once guarantee. Fix with an idempotency key (request id + task name) stored before sending, and send the email from the final successful path of your own code if exactly-once matters.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What argument does a task callback receive?
A1: A `TaskOutput` (raw text, optional pydantic/json, the agent, summary).

Q2: [Medium] Task callback vs `Crew(task_callback)` vs `step_callback`?
A2: Task callback: one task, once at finish. Crew `task_callback`: every task finish. `step_callback`: every agent step (tool result, agent action) - in my run it saw `ToolResult` and `AgentAction` objects.

Q3: [Hard] How do you keep callback state per request in FastAPI?
A3: Build the crew and a closure callback inside the request handler; never share a module-level list.

Q4: [Hard] Can a callback change the task output?
A4: Treat it as read-only observation. To validate or modify output use `guardrail` (it can reject and trigger a retry).

Q5: [System Design] Stream progress ("step 2 of 5 done") to a browser.
A5: Each task callback puts an event into an `asyncio.Queue` (or Redis stream) keyed by job id. A SSE/websocket endpoint reads that queue. The crew runs with `akickoff` in a background task. Add heartbeat, timeout and a final "done" event with token usage.

---

## 💰 Cost Impact
The callback itself costs no tokens. It helps cost control: log `output.raw` size and `crew.usage_metrics`/`result.token_usage` per task to find the expensive step. Approximate formula: cost = input_tokens x input_price + output_tokens x output_price per task, summed. Prices change - verify on the provider page. Tip: alert from a callback when a task output exceeds a size you expect.

## 🔷 When to Use
✅ Use when:
- You need progress, logging, metrics, or notifications per task.
- You persist intermediate results.

❌ Avoid when:
- You need to validate/transform output (use guardrail or `output_pydantic`).
- The work is slow and blocking (offload it).

---

## 📊 Visual Diagram
```
 Task 1 --LLM--> TaskOutput --> callback_1(output) --> log / DB / UI event
   |                                   (must not raise)
   v
 Task 2 --LLM--> TaskOutput --> callback_2(output) --> email / queue
   |
   v
 CrewOutput (raw, tasks_output, token_usage)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| callback | Function called on an event | event पर बुलाया जाने वाला function |
| TaskOutput | Result object of a task | task का result object |
| step_callback | Hook per agent step | हर agent step का hook |
| closure | Function that remembers outer variables | बाहरी variables याद रखने वाला function |
| idempotency | Same action twice has same effect | दो बार चलाने पर भी एक जैसा असर |
| side effect | Action outside the return value | return value से बाहर का असर |

---

## ⚡ 3-Line Summary
English: A task callback runs once when its task finishes and receives `TaskOutput`.
Keep it fast, exception-safe and request-local.
For validation use guardrails, not callbacks.

Hindi: Task callback task खत्म होने पर एक बार चलता है और `TaskOutput` पाता है।
इसे तेज़, exception-safe और request-local रखें।
Validation के लिए callback नहीं, guardrail इस्तेमाल करें।

---

## ➡️ Next Topic
**#87 Task async_execution** - callbacks tell you when a task is done; next we run independent tasks in parallel so the crew finishes sooner.

---
