---

# 84. Task context
# हिंदी में: Task का context
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`Task.context` is a list of other tasks whose outputs are given to this task as input. In a sequential crew the previous task's output is passed by default; setting `context` makes the links explicit (fan-in), and `context=[]` disables inherited context.

## 🔵 सरल परिभाषा (Hindi)
`Task.context` दूसरे tasks की list है जिनके outputs इस task को input के रूप में दिए जाते हैं। Sequential crew में पिछले task का output default रूप से जाता है; `context` सेट करने से links स्पष्ट (fan-in) होते हैं और `context=[]` inherited context बंद कर देता है।

---

## 🔴 Problem it Solves
Pipelines need data to flow: researcher findings must reach the writer. Pasting outputs by hand is brittle, and passing everything wastes tokens. Context gives explicit, minimal data flow.

## 🔴 यह क्यों बना? (Hindi)
Pipelines में data बहना चाहिए: researcher के findings writer तक पहुँचें। हाथ से paste करना कमज़ोर है और सब कुछ भेजना tokens बर्बाद करता है। Context स्पष्ट और न्यूनतम data flow देता है।

---

## 🟢 How it Works

```
Step 1 -> Upstream task finishes; TaskOutput is stored
Step 2 -> Downstream task lists upstream tasks in context=[...]
Step 3 -> With async_execution=True, upstream tasks run in parallel
Step 4 -> Downstream waits until all context tasks are done
Step 5 -> Their outputs are added to the downstream prompt
Step 6 -> Downstream agent merges and answers
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Upstream task पूरा होता है; TaskOutput सहेजा जाता है
Step 2 -> Downstream task context=[...] में upstream tasks लिखता है
Step 3 -> async_execution=True हो तो upstream tasks parallel चलते हैं
Step 4 -> Downstream सभी context tasks पूरे होने तक रुकता है
Step 5 -> उनके outputs downstream prompt में जुड़ते हैं
Step 6 -> Downstream agent मिलाकर जवाब देता है
```

---

## 🟡 Real World Example
**Tariff Agent**: `rate` and `risk` tasks run in parallel (separate agents) and a Writer's `brief` task takes `context=[rate, risk]`. Offline we observed: the merge task ran last and returned all three outputs in `tasks_output`; without `context` the previous output still flowed (it appeared in the prompt), and with `context=[]` it did not.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `rate` और `risk` tasks अलग agents के साथ parallel चलते हैं और Writer का `brief` task `context=[rate, risk]` लेता है। Offline देखा: merge task आख़िर में चला और `tasks_output` में तीनों outputs आए; `context` के बिना भी पिछला output prompt में पहुँचा, और `context=[]` पर नहीं पहुँचा।

---

## 💻 Code Example — Basic
```python
# context_basic.py - Task.context: explicit upstream outputs; async tasks fan-in
from crewai import Agent, Task, Crew, LLM            # core

llm = LLM(model="gpt-4o-mini")                       # shared
a1 = Agent(role="Rate Finder", goal="Find rate", backstory="Fast.", llm=llm)
a2 = Agent(role="Risk Checker", goal="Find risks", backstory="Wary.", llm=llm)   # separate agent: async tasks cannot share one executor
a3 = Agent(role="Writer", goal="Merge", backstory="Clear.", llm=llm)

rate = Task(description="Duty for HS {hs}.", expected_output="Rate.", agent=a1, async_execution=True)
risk = Task(description="Compliance risks for HS {hs}.", expected_output="Risks.", agent=a2, async_execution=True)
brief = Task(description="Merge rate and risks into a brief.", expected_output="Brief.", agent=a3,
             context=[rate, risk])                   # waits for both, receives both outputs
print(Crew(agents=[a1, a2, a3], tasks=[rate, risk, brief]).kickoff(inputs={"hs": "8517"}).raw)
```
Verified offline with a scripted fake LLM (printed the merged result). Using the same agent for both parallel tasks failed with `RuntimeError: Executor is already running`, which is why the example uses three agents.

## 💻 Code Example — Advanced
```python
# context_api.py - fan-out/fan-in crew behind FastAPI, returning every task output
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app
llm = LLM(model="gpt-4o-mini")                       # shared

class Q(BaseModel):                                  # body
    hs: str                                          # input

@app.post("/brief")                                  # endpoint
async def brief(q: Q) -> dict[str, object]:          # typed
    finder = Agent(role="Rate Finder", goal="Find rate", backstory="Fast.", llm=llm)
    checker = Agent(role="Risk Checker", goal="Find risks", backstory="Wary.", llm=llm)
    writer = Agent(role="Writer", goal="Merge", backstory="Clear.", llm=llm)
    t1 = Task(description="Duty for HS {hs}.", expected_output="Rate.", agent=finder, async_execution=True)
    t2 = Task(description="Risks for HS {hs}.", expected_output="Risks.", agent=checker, async_execution=True)
    t3 = Task(description="Merge into a brief.", expected_output="Brief.", agent=writer, context=[t1, t2])
    try:
        out = await Crew(agents=[finder, checker, writer], tasks=[t1, t2, t3]).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"brief": out.raw, "parts": [t.raw for t in out.tasks_output]}   # all intermediate outputs
```
Verified with `TestClient` (HTTP 200; `parts` listed three task outputs). Parallel tasks can fail independently, so in production handle partial failures and set per-task timeouts. Not benchmarked: real latency gains from parallelism depend on the provider.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Data flow | Shared state, edges | `context=[tasks]` + default previous output | Handoff / tool outputs | Shared message history |
| Fan-out / fan-in | Parallel branches + reducer | `async_execution` + `context` | Parallel runs in your code | Group chat / concurrent agents |
| Selectivity | You select state keys | Choose which tasks feed in | Pass explicit values | Whole history by default |
| Hidden cost | State size | Upstream text re-sent in prompt | Context passed manually | History grows |
| Disable inherited | Not applicable | `context=[]` | n/a | n/a |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Passing every upstream output to every task.
✅ Correct: List only needed tasks in `context` to save tokens.

❌ Mistake 2: Parallel tasks sharing one agent.
✅ Correct: Use separate agents for `async_execution=True` tasks.

❌ Mistake 3: Assuming `context` carries structured objects.
✅ Correct: Context is text of outputs; for structure use `output_pydantic` and serialise intentionally.

---

## 🧠 Tricky Interview Question
The final brief omits information from the first task even though context is set. Debug it.

Answer: Check in order: (1) was the first task's output actually produced (`result.tasks_output[0]`); (2) is it in the prompt (log messages with a recording fake LLM or tracing); (3) did truncation occur due to context window limits (`respect_context_window=True` summarises when overflowing) and drop details; (4) is `expected_output` of the last task asking for it; (5) did an upstream async task fail silently. Fix by shrinking upstream outputs to structured essentials instead of long prose.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is `context` for?
A1: To feed outputs of selected tasks into this task as input.

Q2: [Medium] Does a sequential task see the previous output without `context`?
A2: Yes by default (we observed it in the prompt); `context=[]` stops it.

Q3: [Hard] How does `async_execution` interact with context?
A3: Async upstream tasks run concurrently; a downstream task listing them in `context` waits for all of them. Each concurrent task needs its own agent.

Q4: [Hard] How do you control token cost of context?
A4: Make upstream outputs short and structured, pass only needed tasks, summarise, and use cheaper models for intermediate tasks.

Q5: [System Design] Design a fan-out/fan-in research crew for 8 sources?
A5: 8 collector tasks (async, separate agents, timeouts), a merge task with context=[all], partial-failure policy, dedup guardrail, token budget per collector, and result schema.

---

## 💰 Cost Impact
Formula: downstream prompt tokens = own prompt + sum of context outputs. With 3 upstream outputs of 400 tokens each, the merge task adds about 1,200 input tokens per iteration (approximate example) and is resent each loop. Parallel async tasks cost the same tokens as sequential but can reduce wall-clock time. Tips: compress upstream outputs.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Merging parallel research results
- Explicit pipelines with known dependencies

❌ Avoid when:
- Huge raw outputs as context (summarise first)
- Sharing one agent among async tasks

---

## 📊 Visual Diagram
```
  [Task rate (A1) async] ----\
                               >--> [Task brief (A3)]  context=[rate, risk]
  [Task risk (A2) async] ----/            |
                                          v
                              CrewOutput.tasks_output = [rate, risk, brief]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| context | Upstream tasks feeding a task | संदर्भ |
| Fan-out | Splitting into parallel tasks | फैलाव |
| Fan-in | Merging parallel results | संगम |
| async_execution | Non-blocking task run | असिंक्रोनस निष्पादन |
| Partial failure | Some parallel tasks fail | आंशिक विफलता |
| Context window | Max tokens the model sees | कॉन्टेक्स्ट विंडो |

---

## ⚡ 3-Line Summary
English: Task.context makes data flow explicit and enables fan-in after parallel tasks. Sequential tasks inherit the previous output unless context=[]. Parallel tasks need separate agents; compress outputs to save tokens.
Hindi: Task.context data flow को स्पष्ट बनाता है और parallel tasks के बाद fan-in देता है। Sequential tasks पिछला output inherit करते हैं जब तक context=[] न हो। Parallel tasks को अलग agents चाहिए; tokens बचाने को outputs छोटे रखें।

---

## ➡️ Next Topic
**085. Task output_file** - saving task results to files for downstream use.

---
