---

# 88. Crew — Complete Guide
# हिंदी में: Crew - पूरी गाइड (agents + tasks + process को जोड़ने वाली class)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline with a fake `BaseLLM` subclass; I listed `Crew.model_fields` from the installed package). Real LLM calls: not run - needs an API key.

## 🔵 Simple Definition (2-3 lines)
A `Crew` is the object that holds your agents, your tasks and the process (sequential or hierarchical), then runs them with `kickoff()`.
It also owns shared settings: memory, callbacks, rate limit, logging, planning, usage metrics.

## 🔵 सरल परिभाषा (Hindi)
`Crew` वह object है जो आपके agents, tasks और process (sequential या hierarchical) को पकड़कर `kickoff()` से चलाता है।
Shared settings भी इसी के पास होती हैं: memory, callbacks, rate limit, logging, planning, usage metrics।

---

## 🔴 Problem it Solves
Agents and tasks alone do nothing. Somebody must decide the order, pass outputs between tasks, count tokens, stop runaway loops, and give one entry point to your API. Doing this by hand means writing your own orchestrator for every project.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ agents और tasks अपने आप कुछ नहीं करते। किसी को order तय करना, tasks के बीच output पहुँचाना, tokens गिनना, बेकाबू loops रोकना और API के लिए एक entry point देना पड़ता है। हाथ से करने पर हर project में अपना orchestrator लिखना पड़ता है।

---

## 🟢 How it Works

```
Step 1 -> Build Agents (role, goal, backstory, llm, tools)
Step 2 -> Build Tasks (description, expected_output, agent, context)
Step 3 -> Crew(agents=[...], tasks=[...], process=Process.sequential)
Step 4 -> crew.kickoff(inputs={...})   # before_kickoff_callbacks run first
Step 5 -> tasks run in order (or manager delegates), callbacks fire
Step 6 -> after_kickoff_callbacks, then CrewOutput is returned
```

Main `Crew` fields I saw in `Crew.model_fields` (1.15.41): `agents`, `tasks`, `process`, `verbose`, `memory`, `embedder`, `manager_llm`, `manager_agent`, `planning`, `planning_llm`, `max_rpm`, `cache`, `step_callback`, `task_callback`, `before_kickoff_callbacks`, `after_kickoff_callbacks`, `output_log_file`, `knowledge_sources`, `stream`, `usage_metrics`, `name`, `id`.

Run methods that exist: `kickoff`, `kickoff_async`, `akickoff`, `kickoff_for_each`, `kickoff_for_each_async`, `akickoff_for_each`.
Confirmed by running: `kickoff_for_each(inputs=[{...},{...}])` returned one `CrewOutput` per input; a `before_kickoff` callback receives the inputs dict and must return it (I upper-cased `item` there).

## 🟢 कैसे काम करता है? (Hindi)
1. Agents बनाइए, फिर Tasks बनाइए।
2. `Crew(agents=..., tasks=..., process=...)` से जोड़िए।
3. `kickoff(inputs=...)` पहले `before_kickoff_callbacks` चलाता है (वे inputs dict लेकर वही लौटाते हैं)।
4. Tasks क्रम से चलते हैं (या manager बाँटता है), callbacks fire होते हैं।
5. आखिर में `after_kickoff_callbacks` और फिर `CrewOutput` वापस आता है।
6. कई inputs के लिए `kickoff_for_each` हर input पर एक `CrewOutput` देता है।

---

## 🟡 Real World Example
Tariff Agent crew: Classifier agent -> Duty Researcher agent -> Report Writer agent. The API calls `crew.akickoff(inputs={"item": ...})`, logs `result.token_usage`, and applies `max_rpm=30` so the provider is not flooded.

## 🟡 Real Example Hindi mein
Tariff Agent crew: Classifier agent -> Duty Researcher agent -> Report Writer agent। API `crew.akickoff(inputs={"item": ...})` call करती है, `result.token_usage` log करती है, और `max_rpm=30` लगाती है ताकि provider पर बोझ न पड़े।

---

## 💻 Code Example — Basic
```python
# basic_crew.py  (verified offline with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # building blocks

LLM_NAME = "gpt-4o-mini"  # model string; real run needs OPENAI_API_KEY

classifier = Agent(  # agent 1
    role="HS Classifier",  # role
    goal="Pick the HS code",  # goal
    backstory="Customs broker.",  # backstory
    llm=LLM_NAME,  # model
    allow_delegation=False,  # no delegation
)
writer = Agent(  # agent 2
    role="Report Writer",  # role
    goal="Write a clear duty note",  # goal
    backstory="Technical writer for trade teams.",  # backstory
    llm=LLM_NAME,  # model
    allow_delegation=False,  # no delegation
)

classify = Task(  # task 1
    description="Give the HS code for {item}.",  # prompt
    expected_output="HS code and reason.",  # contract
    agent=classifier,  # owner
)
write = Task(  # task 2
    description="Write a 3-line duty note for {item} using the HS code.",  # prompt
    expected_output="3 lines.",  # contract
    agent=writer,  # owner
    context=[classify],  # needs task 1 output
)

crew = Crew(  # the orchestrator
    name="tariff-crew",  # readable name for logs
    agents=[classifier, writer],  # who can work
    tasks=[classify, write],  # what to do, in order
    process=Process.sequential,  # one after another
    max_rpm=30,  # at most 30 LLM requests per minute
    verbose=False,  # keep logs quiet
)

if __name__ == "__main__":  # script entry
    out = crew.kickoff(inputs={"item": "steel"})  # run
    print(out.raw)  # final answer (last task)
    print(len(out.tasks_output), "task outputs")  # one per task
    print(out.token_usage.total_tokens)  # total tokens used
```

## 💻 Code Example — Advanced
```python
# advanced_crew.py  (FastAPI + async + batching + hooks + error handling)
from __future__ import annotations  # modern annotations

import asyncio  # semaphore + gather
import logging  # logs

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel, Field  # schemas
from crewai import Agent, Task, Crew, Process  # CrewAI core

LLM_NAME = "gpt-4o-mini"  # replace with your model
log = logging.getLogger("crew")  # logger
app = FastAPI(title="Crew API")  # ASGI app
LIMIT = asyncio.Semaphore(3)  # at most 3 crews running at once


class Req(BaseModel):  # request
    items: list[str] = Field(..., min_length=1, max_length=20)  # up to 20 products


class ItemResult(BaseModel):  # one result
    item: str  # product
    answer: str | None  # text if success
    error: str | None  # message if failed


def normalise(inputs: dict) -> dict:  # before_kickoff hook: clean inputs
    inputs["item"] = str(inputs.get("item", "")).strip().lower()  # trim + lowercase
    return inputs  # MUST return the dict


def make_crew() -> Crew:  # fresh crew per call (agents hold state)
    agent = Agent(role="Duty Analyst", goal="Give duty facts", backstory="Broker.",  # agent
                  llm=LLM_NAME, allow_delegation=False, max_iter=5)  # cap iterations
    task = Task(description="Duty summary for {item}.", expected_output="2 lines.",  # task
                agent=agent)  # owner
    return Crew(  # assemble
        agents=[agent], tasks=[task], process=Process.sequential,  # basics
        max_rpm=30,  # rate limit
        before_kickoff_callbacks=[normalise],  # input hook
        after_kickoff_callbacks=[lambda out: out],  # output hook (must return output)
    )


async def one(item: str) -> ItemResult:  # run a single item safely
    async with LIMIT:  # concurrency control
        try:
            out = await make_crew().akickoff(inputs={"item": item})  # async run
            return ItemResult(item=item, answer=out.raw, error=None)  # success
        except Exception as exc:  # isolate failures per item
            log.exception("item failed: %s", item)  # log with stack
            return ItemResult(item=item, answer=None, error=str(exc))  # failure row


@app.post("/batch", response_model=list[ItemResult])  # route
async def batch(req: Req) -> list[ItemResult]:  # async handler
    results = await asyncio.gather(*(one(i) for i in req.items))  # parallel with limit
    if all(r.error for r in results):  # everything failed => upstream problem
        raise HTTPException(502, "all items failed")  # signal outage
    return list(results)  # partial success is fine
```
Not run with a real model. Offline run: FastAPI `TestClient` with the fake LLM returned results for two items.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Orchestrator object | `StateGraph` compiled graph | `Crew` | `Runner` + handoffs | `Team` (e.g. RoundRobinGroupChat) |
| Control flow | Explicit edges, conditions | `Process` (sequential/hierarchical) | Handoffs/agents-as-tools | Team type + termination |
| Batch helper | `batch()` | `kickoff_for_each` | You loop/gather | You loop/gather |
| Rate limit | Manual | `max_rpm` | Manual | Manual |
| Usage metrics | Via callbacks/LangSmith | `usage_metrics`, `output.token_usage` | `result.usage`-style fields | Model client usage |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Reusing one global `Crew` for all requests.
✅ Correct: Build a fresh crew per request (or per worker) so state, callbacks and files are not mixed.

❌ Mistake 2: `before_kickoff_callbacks` that forget to `return inputs`.
✅ Correct: Always return the (modified) dict.

❌ Mistake 3: No `max_iter`/`max_rpm`; one bad prompt loops and burns money.
✅ Correct: Set `max_iter` on agents and `max_rpm` on the crew, plus a request timeout.

---

## 🧠 Tricky Interview Question
Your crew takes 40 s and the HTTP gateway times out at 30 s. The client retries and you pay twice. Redesign.

Answer: Make the endpoint asynchronous at the product level: return `202 + job_id` immediately, run `akickoff` in a worker, store the result, and let the client poll or subscribe. Add idempotency key so retries return the same job. Add `max_iter`, per-task timeout (`asyncio.wait_for`) and cache identical inputs. Making the crew faster (parallel tasks, smaller model) is a bonus, not the fix.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the required parts of a Crew?
A1: `agents` and `tasks` (plus a `process`, default sequential).

Q2: [Medium] `kickoff` vs `kickoff_for_each` vs `akickoff`?
A2: One run / one run per input dict / awaitable run for asyncio apps.

Q3: [Hard] Where do you put cross-cutting logic?
A3: `before_kickoff_callbacks` (input cleaning, auth checks), `after_kickoff_callbacks` (post-process), `task_callback`/`step_callback` (observability), `max_rpm` (throttling).

Q4: [Hard] Is a Crew thread-safe and reusable?
A4: Do not assume so; build per request. Agents and tasks keep runtime state (output, retries).

Q5: [System Design] Multi-tenant tariff service on CrewAI.
A5: API gateway -> queue -> worker pool, each worker builds a crew per job with tenant-specific tools/credentials; tenant-scoped memory/storage; per-tenant rate limits and token budgets from `token_usage`; tracing; DLQ for failures.

---

## 💰 Cost Impact
Cost = sum over every LLM call in every task (+ manager calls if hierarchical, + memory/embedding calls if memory is on). Token numbers per run are not fixed; read `result.token_usage` (prompt, completion, total) and log it per request. Tips: smaller model for simple tasks, `max_iter`, `max_rpm`, short `expected_output`, cache tool results, avoid `verbose` in production logs. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- Role-based multi-agent workflows with clear task order.
- You want built-in memory, callbacks, delegation.

❌ Avoid when:
- You need arbitrary loops/branches with checkpoints (LangGraph is stronger).
- A single agent with tools is enough.

---

## 📊 Visual Diagram
```
 inputs --> before_kickoff_callbacks --> [ Crew ]
                                          |  process: sequential | hierarchical
                                          |  max_rpm, memory, planning
                              +-----------+-----------+
                              v                       v
                         Task 1 (Agent A)  --->  Task 2 (Agent B)
                              |  step_callback / task_callback
                              v
 CrewOutput <-- after_kickoff_callbacks <-- final TaskOutput
   (raw, tasks_output, token_usage)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Crew | Team + tasks + process | agents, tasks और process की टीम |
| kickoff | Start the run | run शुरू करना |
| max_rpm | Max LLM requests per minute | प्रति मिनट अधिकतम requests |
| before_kickoff | Hook before run, edits inputs | run से पहले का hook |
| usage_metrics | Token counters for the crew | crew के token गिनतीकार |
| kickoff_for_each | Run once per input item | हर input पर एक बार run |

---

## ⚡ 3-Line Summary
English: `Crew` wires agents, tasks and process and runs them with `kickoff`/`akickoff`.
It also provides hooks, rate limits, memory and usage metrics.
Build a fresh crew per request and always cap iterations and RPM.

Hindi: `Crew` agents, tasks और process को जोड़कर `kickoff`/`akickoff` से चलाता है।
इसमें hooks, rate limit, memory और usage metrics भी मिलते हैं।
हर request पर नया crew बनाइए और iterations व RPM हमेशा सीमित रखिए।

---

## ➡️ Next Topic
**#89 Crew process types** - the `process` field decides who controls the order: fixed sequence or a manager agent.

---
