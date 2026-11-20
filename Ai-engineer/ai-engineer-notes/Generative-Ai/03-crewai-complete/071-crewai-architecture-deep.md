---

# 71. CrewAI — Architecture Deep
# हिंदी में: CrewAI का architecture गहराई से
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
CrewAI is a Python framework where you describe a team: Agents (who), Tasks (what) and a Crew (the team plus a Process that decides the order). `crew.kickoff()` runs the tasks and returns a `CrewOutput`.

## 🔵 सरल परिभाषा (Hindi)
CrewAI एक Python framework है जिसमें आप एक team describe करते हैं: Agents (कौन), Tasks (क्या) और Crew (team + Process जो order तय करता है)। `crew.kickoff()` tasks चलाता है और `CrewOutput` लौटाता है।

---

## 🔴 Problem it Solves
Hand-written multi-agent loops mix prompts, tool calls, retries and data passing in one tangled script. Without a structure you cannot reuse an agent, reorder tasks, or see which step cost tokens.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे multi-agent loops में prompts, tool calls, retries और data passing सब एक उलझी script में मिल जाते हैं। Structure के बिना आप agent दोबारा इस्तेमाल नहीं कर सकते, tasks का order नहीं बदल सकते और यह नहीं देख सकते कि किस step ने कितने tokens खाए।

---

## 🟢 How it Works

```
Step 1 -> Define Agents (role, goal, backstory, llm, tools)
Step 2 -> Define Tasks (description, expected_output, agent, context)
Step 3 -> Assemble Crew(agents, tasks, process)
Step 4 -> kickoff(inputs) fills {placeholders} in every description
Step 5 -> Process runs tasks (sequential: in list order; hierarchical: manager LLM delegates)
Step 6 -> Each task = agent's ReAct loop (think -> tool -> observe) until Final Answer
Step 7 -> Task outputs are stored and passed as context to later tasks
Step 8 -> CrewOutput(raw, tasks_output, token_usage) returned
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Agents define करें (role, goal, backstory, llm, tools)
Step 2 -> Tasks define करें (description, expected_output, agent, context)
Step 3 -> Crew(agents, tasks, process) बनाएँ
Step 4 -> kickoff(inputs) हर description के {placeholders} भरता है
Step 5 -> Process tasks चलाता है (sequential: list के क्रम में; hierarchical: manager LLM बाँटता है)
Step 6 -> हर task = agent का ReAct loop (सोचो -> tool -> observe) Final Answer तक
Step 7 -> Task outputs सहेजे जाते हैं और आगे के tasks को context बनकर जाते हैं
Step 8 -> CrewOutput(raw, tasks_output, token_usage) लौटता है
```

---

## 🟡 Real World Example
**Tariff Agent**: a Tariff Analyst agent finds the duty for an HS code, then a Writer agent turns it into a customs brief. Two agents, two tasks, `Process.sequential`; the analyst's output becomes the writer's context automatically (we observed this in an offline run).

**Other**: research crew (researcher + editor), support triage crew, code-review crew.

## 🟡 Real Example Hindi mein
**Tariff Agent**: Tariff Analyst agent किसी HS code की duty निकालता है, फिर Writer agent उसे customs brief बना देता है। दो agents, दो tasks, `Process.sequential`; analyst का output अपने-आप writer का context बन जाता है (offline run में हमने यह देखा)।

**और उदाहरण**: research crew (researcher + editor), support triage crew, code-review crew।

---

## 💻 Code Example — Basic
```python
# arch_basic.py - the 4 building blocks of CrewAI: Agent, Task, Crew, Process
from crewai import Agent, Task, Crew, Process, LLM   # core CrewAI classes

llm = LLM(model="gpt-4o-mini")                       # model string; needs OPENAI_API_KEY at real run time

analyst = Agent(                                     # WHO does the work
    role="Tariff Analyst",                           # job title, goes into the system prompt
    goal="Find the correct customs duty for an HS code",  # what success means
    backstory="Ten years in customs classification.",     # persona / style
    llm=llm,                                         # brain of this agent
)
task = Task(                                         # WHAT must be done
    description="Find the duty rate for HS code {hs_code}.",  # {hs_code} filled by kickoff inputs
    expected_output="One sentence with the duty percent.",     # shape of the answer
    agent=analyst,                                   # who owns this task
)
crew = Crew(                                         # the team = agents + tasks + process
    agents=[analyst],                                # all agents in the crew
    tasks=[task],                                    # ordered task list
    process=Process.sequential,                      # run tasks one after another
)
result = crew.kickoff(inputs={"hs_code": "8517"})    # run; returns CrewOutput
print(result.raw)                                    # final text of the LAST task
print(len(result.tasks_output))                      # one TaskOutput per task
```
Verified: ran offline with a scripted fake LLM; `result.raw` returned the last task's text and `len(result.tasks_output)` was 1. Not run with a real model - needs an API key.

## 💻 Code Example — Advanced
```python
# arch_api.py - build a Crew per request and expose it through FastAPI
from crewai import Agent, Task, Crew, Process, LLM   # CrewAI core
from fastapi import FastAPI, HTTPException           # web framework
from pydantic import BaseModel, Field                # request validation

app = FastAPI()                                      # ASGI app
llm = LLM(model="gpt-4o-mini")                       # shared LLM config (stateless, safe to share)

class RateRequest(BaseModel):                        # typed request body
    hs_code: str = Field(min_length=4, max_length=10)  # reject junk early (saves tokens)

def build_crew() -> Crew:                            # factory: agents hold per-run state, so build fresh
    agent = Agent(role="Tariff Analyst", goal="Find duty rates",
                  backstory="Customs expert.", llm=llm, max_iter=5)  # cap loop
    task = Task(description="Duty rate for HS {hs_code}?",
                expected_output="One sentence.", agent=agent)
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)

@app.post("/rate")                                   # async endpoint
async def rate(req: RateRequest) -> dict[str, object]:   # typed response
    try:
        out = await build_crew().kickoff_async(inputs={"hs_code": req.hs_code})  # non-blocking run
    except Exception as exc:                         # LLM/network/tool failure
        raise HTTPException(status_code=502, detail=f"crew failed: {type(exc).__name__}") from exc
    usage = out.token_usage                          # UsageMetrics (real numbers only with a real LLM)
    return {"answer": out.raw, "total_tokens": usage.total_tokens,
            "tasks": len(out.tasks_output)}          # return answer + cost signal
```
Verified with FastAPI `TestClient` (HTTP 200, `total_tokens` is 0 because the LLM was the offline fake). Build the crew per request: agents keep run state and an executor, so sharing one Agent across concurrent requests is unsafe (we hit `Executor is already running` when two async tasks shared an agent).

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Core unit | Graph of nodes + state | Agent + Task + Crew | Agent + tools + handoffs | Chat agents / teams |
| Control flow | Explicit edges, loops, conditionals | Process (sequential / hierarchical) + Flows | Runner loop + handoffs | Team chat patterns |
| State | Typed state, checkpointers | Task outputs as context, optional memory | Run context / sessions | Message history |
| Learning curve | Higher, most control | Lowest to start | Low | Medium |
| Best for | Complex stateful workflows | Role-based pipelines | Simple tool agents | Conversational multi-agent |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Treating the Crew as stateless and sharing one global Agent between requests.
✅ Correct: Build agents/crew per request via a factory; share only the LLM config.

❌ Mistake 2: Assuming `Process.sequential` needs no `agent` on tasks.
✅ Correct: Every task needs an `agent` in sequential mode; we saw a validation error `Agent is missing in the task` otherwise. Only hierarchical lets the manager assign.

❌ Mistake 3: Reading `result.raw` as every task's output.
✅ Correct: `raw` is the last task's output; use `result.tasks_output` for each task.

---

## 🧠 Tricky Interview Question
Your crew has 3 tasks but the final answer ignores the first task's data. Where do you look?

Answer: First check `Task.context`. In sequential mode earlier outputs flow into later tasks by default, but if someone set `context=[]` that link is cut (we observed the earlier output was absent from the prompt with `context=[]` and present without it). Second, inspect `result.tasks_output` to confirm task 1 produced real data. Third, check `expected_output` of task 1: a vague contract gives vague data. Finally log the prompt the LLM saw (via `step_callback` or tracing) rather than guessing.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the main building blocks of CrewAI?
A1: Agent (role/goal/backstory/tools), Task (description/expected_output/agent), Crew (agents+tasks+process), and Process (sequential or hierarchical). `kickoff()` runs it.

Q2: [Medium] What does `kickoff(inputs=...)` do?
A2: It interpolates `{placeholders}` in agent and task text with the inputs dict and starts execution, returning a `CrewOutput`.

Q3: [Hard] Sequential vs hierarchical process?
A3: Sequential runs tasks in list order, each with its own agent. Hierarchical adds a manager (`manager_llm` or `manager_agent`) that delegates tasks to workers; it costs extra LLM calls for the manager's planning and review.

Q4: [Hard] How do you stop a crew burning tokens?
A4: Set `max_iter` per agent, `max_execution_time`, `max_rpm`, keep descriptions tight, use cheaper models for simple agents, and read `token_usage` after runs.

Q5: [System Design] Design a CrewAI service for 50 req/sec.
A5: Stateless FastAPI workers, a crew factory per request, `kickoff_async`, a queue for long runs, per-request timeouts, rate limit on LLM provider (`max_rpm`), tracing, result store keyed by job id, and a model tier router.

---

## 💰 Cost Impact
Formula: tokens per run = sum over tasks of (iterations x (system prompt + task prompt + context + tool schemas + scratchpad growth)). Each ReAct iteration is one LLM call, and the scratchpad grows each loop, so cost is roughly quadratic in iterations. Tips: lower `max_iter`, pass only needed context, use a small model for simple tasks.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Role-based pipelines with clear hand-offs
- Fast prototypes of multi-agent workflows
- Teams that want declarative agent/task definitions

❌ Avoid when:
- You need fine-grained graph control, checkpoints and cycles (use LangGraph)
- A single prompt solves the task (extra agents only add cost)

---

## 📊 Visual Diagram
```
  kickoff(inputs)
        |
        v
 +--------------+   process=sequential
 |    CREW      |----------------------+
 +--------------+                      v
   agents[]  tasks[]          +-------------------+
      |         |             | Task 1 (Analyst)  |--ReAct loop-->LLM<->Tools
      |         |             +---------+---------+
      |         |                       | output = context
      |         |             +---------v---------+
      |         +-----------> | Task 2 (Writer)   |--ReAct loop-->LLM
      |                       +---------+---------+
      v                                 v
  token_usage  <-------------  CrewOutput(raw, tasks_output)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM-driven worker with a persona and tools | एजेंट |
| Task | One unit of work with expected output | काम / टास्क |
| Crew | Team of agents + tasks + process | टीम |
| Process | Execution order strategy | प्रक्रिया / क्रम |
| kickoff | Method that starts the crew | शुरू करना |
| CrewOutput | Result object (raw, tasks_output, token_usage) | क्रू का नतीजा |

---

## ⚡ 3-Line Summary
English: CrewAI = Agents (who) + Tasks (what) + Crew (team) + Process (order). `kickoff` runs ReAct loops per task and passes outputs forward. Build crews per request and watch token_usage.
Hindi: CrewAI = Agents (कौन) + Tasks (क्या) + Crew (team) + Process (क्रम)। `kickoff` हर task का ReAct loop चलाता है और outputs आगे भेजता है। हर request पर crew नया बनाइए और token_usage देखिए।

---

## ➡️ Next Topic
**072. CrewAI vs LangGraph vs SDK** - to decide which framework fits a given problem before you build.

---
