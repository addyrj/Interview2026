---

# 83. Task agent assignment
# हिंदी में: Task को agent सौंपना
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
Each task is assigned to an agent through `Task(agent=...)`. In `Process.sequential` every task needs an agent. In `Process.hierarchical` you may leave `agent` empty and a manager (`manager_llm` or `manager_agent`) delegates to workers.

## 🔵 सरल परिभाषा (Hindi)
हर task `Task(agent=...)` से किसी agent को सौंपा जाता है। `Process.sequential` में हर task को agent चाहिए। `Process.hierarchical` में `agent` खाली छोड़ सकते हैं और manager (`manager_llm` या `manager_agent`) workers को काम बाँटता है।

---

## 🔴 Problem it Solves
Work needs the right specialist. Poor assignment gives a writer a research job or overloads one agent with too many tools and a bloated prompt.

## 🔴 यह क्यों बना? (Hindi)
काम सही specialist को मिलना चाहिए। ग़लत assignment से writer को research का काम मिलता है या एक agent पर बहुत ज़्यादा tools और भारी prompt आ जाता है।

---

## 🟢 How it Works

```
Step 1 -> List the skills each task needs
Step 2 -> Create specialist agents with focused tools
Step 3 -> Sequential: set Task(agent=...) explicitly
Step 4 -> Hierarchical: omit agent, set manager_llm / manager_agent
Step 5 -> Manager plans, delegates, reviews (extra LLM calls)
Step 6 -> Validate configuration at build time (missing agent -> error)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> हर task को कौन-सी skills चाहिए, लिखें
Step 2 -> focused tools वाले specialist agents बनाएँ
Step 3 -> Sequential: Task(agent=...) स्पष्ट सेट करें
Step 4 -> Hierarchical: agent छोड़ें, manager_llm / manager_agent सेट करें
Step 5 -> Manager योजना बनाता है, बाँटता है, review करता है (अतिरिक्त LLM calls)
Step 6 -> Build समय पर configuration validate करें (agent न हो -> error)
```

---

## 🟡 Real World Example
**Tariff Agent**: Researcher owns 'find duty', Writer owns 'write brief'. In an offline test, a sequential crew containing a task with no agent failed at construction with `Agent is missing in the task`, which is exactly the early error you want.

## 🟡 Real Example Hindi mein
**Tariff Agent**: Researcher 'duty निकालो' का मालिक, Writer 'brief लिखो' का। Offline test में बिना agent वाले task के साथ sequential crew बनते समय ही `Agent is missing in the task` से fail हुआ - यही early error आप चाहते हैं।

---

## 💻 Code Example — Basic
```python
# assignment_basic.py - sequential needs task.agent; hierarchical lets a manager assign
from crewai import Agent, Task, Crew, Process, LLM   # core

llm = LLM(model="gpt-4o-mini")                       # shared model
researcher = Agent(role="Researcher", goal="Find tariff facts", backstory="Thorough.", llm=llm)
writer = Agent(role="Writer", goal="Write a brief", backstory="Concise.", llm=llm)

t1 = Task(description="Find duty for HS {hs}.", expected_output="Facts.", agent=researcher)   # explicit owner
t2 = Task(description="Write a 2-line brief.", expected_output="Brief.", agent=writer, context=[t1])
seq = Crew(agents=[researcher, writer], tasks=[t1, t2], process=Process.sequential)   # each task has an agent

t3 = Task(description="Produce a duty brief for HS {hs}.", expected_output="Brief.")   # NO agent
hier = Crew(agents=[researcher, writer], tasks=[t3], process=Process.hierarchical,
            manager_llm=llm)                         # manager decides who does it
print(seq.process, hier.process)
```
Verified: both crews were constructed offline (printed `Process.sequential Process.hierarchical`). The hierarchical crew was built but not executed; running it needs a real manager LLM.

## 💻 Code Example — Advanced
```python
# assignment_api.py - choose the owner per request; fail fast on unknown roles
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app
llm = LLM(model="gpt-4o-mini")                       # shared

def agents() -> dict[str, Agent]:                    # fresh agents per request
    return {
        "analyst": Agent(role="Tariff Analyst", goal="Exact duty", backstory="Strict.", llm=llm),
        "writer": Agent(role="Brief Writer", goal="Short brief", backstory="Concise.", llm=llm),
    }

class Req(BaseModel):                                # body
    hs: str                                          # input
    owner: str = "analyst"                           # which agent owns the task

@app.post("/assign")                                 # endpoint
async def assign(req: Req) -> dict[str, str]:        # typed
    pool = agents()                                  # build pool
    if req.owner not in pool:                        # validate owner
        raise HTTPException(422, f"owner must be one of {sorted(pool)}")
    task = Task(description="Duty brief for HS {hs}.", expected_output="Two lines.", agent=pool[req.owner])
    try:
        out = await Crew(agents=list(pool.values()), tasks=[task]).kickoff_async(inputs={"hs": req.hs})
    except Exception as exc:                         # failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"owner": req.owner, "answer": out.raw}
```
Verified with `TestClient` (HTTP 200). Owner is validated against the pool before building the task (422 on unknown owner), agents are created fresh per request.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Who does the step | Node you route to | `Task(agent=...)` | Agent you run / handoff target | Selector / speaker choice |
| Dynamic routing | Conditional edges (code) | Hierarchical manager (LLM) | Handoffs (LLM decides) | Selector group chat (LLM) |
| Config validation | Compile-time graph checks | Crew validates missing agents | Runtime | Runtime |
| Cost of routing | Zero if code-based | Manager LLM calls | Handoff tool call | Selector LLM calls |
| Predictability | High | High (sequential) / lower (hierarchical) | Medium | Medium |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using hierarchical for a fixed pipeline.
✅ Correct: Use sequential when the order is known; hierarchical adds manager cost and variance.

❌ Mistake 2: One mega-agent owning all tasks.
✅ Correct: Specialise agents; limit tools per agent.

❌ Mistake 3: Forgetting `manager_llm` in hierarchical.
✅ Correct: Provide `manager_llm` or `manager_agent`; test the config.

---

## 🧠 Tricky Interview Question
Hierarchical crew keeps giving tasks to the wrong worker. What do you check?

Answer: The manager routes using each worker's role/goal/backstory, so look there first: overlapping or vague roles confuse it. Make roles distinct, put tool-specific hints in goals, reduce worker count, and give the manager a stronger model. If routing is actually deterministic (task type -> agent), switch to sequential with explicit `agent=` or route in your own code before the crew; it is cheaper and predictable.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you assign a task to an agent?
A1: `Task(agent=my_agent, ...)`.

Q2: [Medium] When can `agent` be omitted?
A2: In hierarchical process where the manager assigns; in sequential mode CrewAI raises a validation error.

Q3: [Hard] Cost of hierarchical?
A3: Extra manager LLM calls for planning, delegation and review, plus larger prompts; variance in routing.

Q4: [Hard] Sequential vs routing in code?
A4: If the router is a simple rule, do it in code and keep crews sequential: deterministic and cheaper.

Q5: [System Design] Design a pool of specialist agents for 10 task types?
A5: Registry mapping task type -> agent factory, per-agent tool allow-lists, deterministic router with LLM fallback, agents built per request, metrics per agent, and evals for misrouting.

---

## 💰 Cost Impact
Formula: sequential cost = sum of task costs; hierarchical cost = sum of task costs + manager planning/review calls (each with growing context). Extra manager overhead is workload-dependent; measure it on your tasks. Tips: deterministic routing in code, cheaper model for simple workers.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Clear specialist roles
- Fixed pipelines (sequential)

❌ Avoid when:
- Hierarchical when routing is a simple rule
- Agents with overlapping roles

---

## 📊 Visual Diagram
```
  SEQUENTIAL                         HIERARCHICAL
  Task1(agent=A) -> Task2(agent=B)   Task(no agent) --> [Manager LLM]
                                                         |plan/delegate
                                              +----------+----------+
                                              v                     v
                                         Worker A              Worker B
                                              \__________review____/
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Assignment | Linking a task to an agent | सौंपना |
| Manager | LLM that delegates in hierarchical mode | प्रबंधक |
| Worker | Agent executing delegated tasks | कार्यकर्ता |
| Specialist | Agent with narrow skills | विशेषज्ञ |
| Routing | Choosing which agent acts | रूटिंग |
| Validation | Checking config before run | जाँच |

---

## ⚡ 3-Line Summary
English: Sequential needs task.agent; hierarchical lets a manager delegate at extra cost. Prefer explicit assignment or code routing when the mapping is known. Validate at build time.
Hindi: Sequential में task.agent ज़रूरी है; hierarchical में manager अतिरिक्त cost पर बाँटता है। मैपिंग पता हो तो स्पष्ट assignment या code routing चुनें। Build समय पर validate करें।

---

## ➡️ Next Topic
**084. Task context** - passing one task's output to another.

---
