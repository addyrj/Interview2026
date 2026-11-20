---

# 80. Task — Complete Guide
# हिंदी में: Task — पूरी गाइड
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
A `Task` is one assignment: a `description`, an `expected_output`, an `agent` (owner) and optional extras such as `context`, `tools`, `output_pydantic`, `guardrail`, `async_execution`, `human_input` and `output_file`. A Crew runs a list of tasks.

## 🔵 सरल परिभाषा (Hindi)
`Task` एक assignment है: `description`, `expected_output`, `agent` (मालिक) और optional extras जैसे `context`, `tools`, `output_pydantic`, `guardrail`, `async_execution`, `human_input`, `output_file`। Crew tasks की list चलाता है।

---

## 🔴 Problem it Solves
Agents without well-defined tasks wander. Tasks define scope, acceptance criteria, data flow and output format, so work is testable and results are machine-readable.

## 🔴 यह क्यों बना? (Hindi)
साफ़ परिभाषित tasks के बिना agents भटकते हैं। Task scope, acceptance criteria, data flow और output format तय करता है, ताकि काम testable हो और नतीजे machine-readable हों।

---

## 🟢 How it Works

```
Step 1 -> Crew picks the next task (list order in sequential)
Step 2 -> description + expected_output + context are rendered into the agent prompt
Step 3 -> Agent runs its ReAct loop
Step 4 -> Output parsed to Pydantic/JSON if requested
Step 5 -> Guardrail checks it; failure feeds the error back and retries (guardrail_max_retries, default 3)
Step 6 -> TaskOutput stored; optional callback / output_file
Step 7 -> Next task gets this output as context
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Crew अगला task चुनता है (sequential में list क्रम)
Step 2 -> description + expected_output + context agent prompt में जाते हैं
Step 3 -> Agent अपना ReAct loop चलाता है
Step 4 -> माँगा हो तो output Pydantic/JSON में parse होता है
Step 5 -> Guardrail जाँचता है; fail पर error वापस भेजकर retry (guardrail_max_retries, default 3)
Step 6 -> TaskOutput सहेजा जाता है; optional callback / output_file
Step 7 -> अगले task को यह output context में मिलता है
```

---

## 🟡 Real World Example
**Tariff Agent**: Task 'find duty for HS {hs}' with `output_pydantic=DutyAnswer` and a guardrail that rejects percents outside 0-100. In an offline run the Pydantic object was parsed correctly (`hs_code='8517' duty_percent=0.0`).

## 🟡 Real Example Hindi mein
**Tariff Agent**: Task 'HS {hs} की duty निकालो' जिसमें `output_pydantic=DutyAnswer` और एक guardrail है जो 0-100 के बाहर का percent reject करता है। Offline run में Pydantic object सही parse हुआ (`hs_code='8517' duty_percent=0.0`)।

---

## 💻 Code Example — Basic
```python
# task_basic.py - a Task with the fields you use daily
from pydantic import BaseModel                       # structured output schema
from crewai import Agent, Task, Crew, LLM            # core

class DutyAnswer(BaseModel):                         # what we want back
    hs_code: str                                     # echoed code
    duty_percent: float                              # rate

agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))
task = Task(
    description="Find the duty for HS code {hs}.",   # instructions
    expected_output="JSON with hs_code and duty_percent.",   # acceptance criteria
    agent=agent,                                     # owner
    output_pydantic=DutyAnswer,                      # parse + validate the answer
    output_file="duty.json",                         # also save to disk (relative to cwd)
)
res = Crew(agents=[agent], tasks=[task]).kickoff(inputs={"hs": "8517"})
print(res.pydantic)                                  # DutyAnswer instance (or None if parsing failed)
```
Verified offline with a scripted fake LLM that replied with JSON; `res.pydantic` was a `DutyAnswer`. `output_file="duty.json"` writes to the current directory when it runs, so point it somewhere intended. Real model JSON compliance: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# task_api.py - Task with guardrail + retries, structured response, FastAPI
from typing import Any                               # typing
from pydantic import BaseModel                       # schema
from crewai import Agent, Task, Crew, LLM            # core
from crewai.tasks.task_output import TaskOutput      # type of the guardrail argument
from fastapi import FastAPI, HTTPException           # web

app = FastAPI()                                      # app

class DutyAnswer(BaseModel):                         # response model
    hs_code: str                                     # code
    duty_percent: float                              # rate

def must_have_percent(out: TaskOutput) -> tuple[bool, Any]:   # guardrail: (ok, result_or_error)
    if out.pydantic is None:                         # parsing failed
        return False, "Return valid JSON with hs_code and duty_percent"   # error text goes back to the agent
    if not 0 <= out.pydantic.duty_percent <= 100:    # sanity range
        return False, "duty_percent must be between 0 and 100"
    return True, out                                 # accept

class Q(BaseModel):                                  # body
    hs: str                                          # input

@app.post("/duty", response_model=DutyAnswer)        # typed response
async def duty(q: Q) -> DutyAnswer:                  # endpoint
    agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))
    task = Task(description="Duty for HS {hs}.", expected_output="JSON hs_code, duty_percent",
                agent=agent, output_pydantic=DutyAnswer,
                guardrail=must_have_percent, guardrail_max_retries=2)   # at most 2 corrective retries
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # includes guardrail exhaustion
        raise HTTPException(502, type(exc).__name__) from exc
    if out.pydantic is None:                         # still unparsed
        raise HTTPException(502, "model did not return valid JSON")
    return out.pydantic                              # FastAPI serialises it
```
Verified with `TestClient` (HTTP 200 with the validated model). In an offline test a guardrail that failed once and passed on the second reply caused exactly 2 LLM calls. Note the guardrail logging hook uses `inspect.getsource`, so guardrails must live in a real source file, not `exec`/REPL (we hit `OSError: could not get source code` otherwise).

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Unit of work | Node function | `Task` | Agent run / tool | Message turn / task to team |
| Output schema | Typed state / structured output | `output_pydantic`, `output_json` | `output_type` | Structured output on client |
| Validation hook | Conditional edges / nodes | `guardrail` + retries | Output guardrails | Custom termination / checks |
| Human review | `interrupt` | `human_input=True` | Approval via guardrails/hooks (check docs) | UserProxy agent |
| Parallelism | Parallel branches | `async_execution=True` | Parallel runs in your code | Concurrent agents |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Task with no `expected_output` detail.
✅ Correct: Describe the format and acceptance criteria precisely.

❌ Mistake 2: Using one agent for two `async_execution` tasks.
✅ Correct: Give each parallel task its own agent; sharing one raised `Executor is already running` in our test.

❌ Mistake 3: Assuming `output_pydantic` guarantees valid JSON.
✅ Correct: It parses; the model can still fail. Add a guardrail and handle `None`.

---

## 🧠 Tricky Interview Question
Your task's `output_pydantic` is None sometimes. What do you do?

Answer: Treat it as expected failure. Read `TaskOutput.raw` to see what the model returned (prose around JSON, trailing text, wrong types). Tighten `expected_output` with an explicit JSON example, lower temperature, add a guardrail returning `(False, 'Return only valid JSON with hs_code and duty_percent')` so CrewAI retries with that feedback (up to `guardrail_max_retries`), and in your API return 502 with a clear message when it is still None. Log failures to improve prompts.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which fields are required on a Task?
A1: `description` and `expected_output`; in sequential mode also an `agent`.

Q2: [Medium] What does `context` do?
A2: Lists upstream tasks whose outputs are fed to this task. Without `context`, sequential tasks still receive previous outputs; `context=[]` disables that (observed).

Q3: [Hard] How does a guardrail work?
A3: A function `(TaskOutput) -> (bool, result_or_error)`. On False the error text is sent back to the agent and the task retries up to `guardrail_max_retries` (default 3).

Q4: [Hard] `async_execution` pitfalls?
A4: Parallel tasks need separate agents, a later task with `context` waits for them, and error handling must tolerate partial failure.

Q5: [System Design] Design a validated multi-step document pipeline?
A5: Tasks with Pydantic outputs, guardrails per step, context links, per-task callbacks for metrics, idempotent job IDs, retries with backoff, human_input only for risky steps, and result persistence.

---

## 💰 Cost Impact
Formula: cost per task = iterations x prompt tokens. Prompt = agent persona + task description + expected_output + context + tools. Guardrail retries re-run the task, so each retry roughly adds another full task cost: worst case (1 + guardrail_max_retries) x task cost. Tips: precise expected_output reduces retries; pass only needed context.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Every Crew step
- You need typed, validated outputs

❌ Avoid when:
- Giant multipurpose tasks (split them)
- Guardrails with unreachable criteria (infinite retries until cap)

---

## 📊 Visual Diagram
```
  description + expected_output + context
                   |
                   v
             [ Agent ReAct loop ]
                   |
            raw text -> output_pydantic parse
                   |
             guardrail(ok?) --no--> error fed back, retry (<= guardrail_max_retries)
                   | yes
                   v
   TaskOutput --> callback / output_file --> next task context
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Task | One unit of work | कार्य |
| expected_output | Acceptance criteria / format | अपेक्षित आउटपुट |
| context | Upstream outputs fed in | संदर्भ |
| Guardrail | Validator with retry | गार्डरेल |
| output_pydantic | Parse result into a model | पाइडैंटिक आउटपुट |
| async_execution | Run without blocking next tasks | असिंक्रोनस |

---

## ⚡ 3-Line Summary
English: A Task = description + expected_output + owner + optional context, guardrail and typed output. Guardrails retry with feedback and multiply cost. Parallel tasks need separate agents.
Hindi: Task = description + expected_output + मालिक + optional context, guardrail और typed output। Guardrail feedback के साथ retry करता है और cost बढ़ाता है। Parallel tasks को अलग agents चाहिए।

---

## ➡️ Next Topic
**081. Task description** - writing the instruction text that drives the agent.

---
