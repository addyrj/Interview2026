---

# 91. Hierarchical Process
# हिंदी में: Hierarchical Process (manager agent काम बाँटता है)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline). I scripted a fake manager that emitted a "Delegate work to coworker" action, and a fake worker answered it. Real model behaviour (how well a real LLM plans) is not verified - needs an API key.

## 🔵 Simple Definition (2-3 lines)
With `Process.hierarchical`, CrewAI creates (or uses) a manager agent. The manager reads the task, delegates pieces to your worker agents, checks their answers and returns the final result.
You must give it `manager_llm` or `manager_agent`.

## 🔵 सरल परिभाषा (Hindi)
`Process.hierarchical` में CrewAI एक manager agent बनाता है (या आपका दिया हुआ इस्तेमाल करता है)। Manager task पढ़कर टुकड़े आपके worker agents को सौंपता है, उनके जवाब जाँचता है और final result देता है।
इसके लिए `manager_llm` या `manager_agent` देना ज़रूरी है।

---

## 🔴 Problem it Solves
For open-ended goals you do not know the steps in advance, and you do not know which worker is right. A fixed sequence either wastes calls or misses steps. A manager can plan, delegate, and re-delegate when a result is weak.

## 🔴 यह क्यों बना? (Hindi)
खुले लक्ष्यों में आपको पहले से कदम नहीं पता होते, और यह भी नहीं कि कौन-सा worker सही रहेगा। तय sequence या तो calls बर्बाद करता है या कदम छोड़ देता है। Manager योजना बना सकता है, काम बाँट सकता है, और कमज़ोर नतीजे पर दोबारा सौंप सकता है।

---

## 🟢 How it Works

```
Step 1 -> Crew(process=hierarchical, manager_llm=... or manager_agent=...)
Step 2 -> Manager reads the task description + expected_output
Step 3 -> Manager calls its delegation tool: "Delegate work to coworker"
Step 4 -> Worker agent runs that sub-task (own LLM call, own tools)
Step 5 -> Worker answer goes back to the manager
Step 6 -> Manager may delegate again, or "Ask question to coworker"
Step 7 -> Manager writes the final answer -> CrewOutput.raw
```

What I verified by running:
- Scripted manager reply: `Action: Delegate work to coworker` with JSON `{"task": ..., "context": ..., "coworker": "Duty Researcher"}`. The worker's prompt then showed `Current Task: Find duty for steel` with the instruction "Your best answer to your coworker asking you this". Manager LLM was called 2 times, worker 1 time. Final output was the manager's final text.
- `manager_llm=<llm>` works. `manager_agent=Agent(...)` (I set `allow_delegation=True`) also works.
- Without either, Crew creation fails with a clear validation error.
- Worker agents in a hierarchical crew keep `allow_delegation=False` in my examples so only the manager delegates.

## 🟢 कैसे काम करता है? (Hindi)
1. `Crew(process=hierarchical, manager_llm=... या manager_agent=...)`।
2. Manager task पढ़ता है और अपने delegation tool "Delegate work to coworker" को call करता है।
3. Worker agent वह sub-task चलाता है, और जवाब manager को लौटता है।
4. Manager ज़रूरत पड़ने पर फिर सौंपता है या coworker से सवाल पूछता है।
5. अंत में manager final answer लिखता है।
6. मेरे offline test में scripted manager ने delegate किया: manager LLM 2 बार चला, worker 1 बार।
7. असली LLM की planning quality जाँची नहीं गई।

---

## 🟡 Real World Example
Tariff Agent: "Can I import used medical devices from Germany and what is the landed cost?" Manager delegates: Classifier (HS code), Regulations Researcher (licences), Duty Researcher (rate), Logistics Analyst (freight). It merges answers into one report and asks a worker to redo a weak part.

## 🟡 Real Example Hindi mein
Tariff Agent: "क्या मैं जर्मनी से used medical devices मँगवा सकता हूँ और landed cost क्या होगी?" Manager बाँटता है: Classifier (HS code), Regulations Researcher (licences), Duty Researcher (rate), Logistics Analyst (freight)। फिर सब जोड़कर एक report बनाता है, और कमज़ोर हिस्सा दोबारा करवाता है।

---

## 💻 Code Example — Basic
```python
# basic_hierarchical.py  (verified offline: builds and runs with a fake LLM, crewai 1.15.41)
from crewai import Agent, Task, Crew, Process  # core classes

LLM_NAME = "gpt-4o-mini"  # worker model string; real run needs OPENAI_API_KEY

classifier = Agent(  # worker 1
    role="HS Classifier",  # role
    goal="Classify products into HS codes",  # goal
    backstory="Customs broker.",  # backstory
    llm=LLM_NAME,  # model
    allow_delegation=False,  # workers do not delegate further
)
duty = Agent(  # worker 2
    role="Duty Researcher",  # role
    goal="Find duty rates for an HS code",  # goal
    backstory="Tariff schedule specialist.",  # backstory
    llm=LLM_NAME,  # model
    allow_delegation=False,  # workers do not delegate further
)

task = Task(  # ONE open-ended task; the manager splits it
    description="Prepare an import duty briefing for {item}.",  # prompt
    expected_output="A short briefing with HS code and duty rate.",  # acceptance criteria
)  # no agent= here: the manager chooses

crew = Crew(  # manager-led crew
    agents=[classifier, duty],  # worker pool (do NOT add the manager here)
    tasks=[task],  # tasks for the manager
    process=Process.hierarchical,  # manager mode
    manager_llm=LLM_NAME,  # REQUIRED unless manager_agent is given
    max_rpm=30,  # throttle LLM calls
)

if __name__ == "__main__":  # script entry
    out = crew.kickoff(inputs={"item": "steel"})  # run
    print(out.raw)  # manager's final answer
    print(out.token_usage)  # usage includes manager calls
```

## 💻 Code Example — Advanced
```python
# advanced_hierarchical.py  (FastAPI + async + custom manager_agent + budget guard)
from __future__ import annotations  # modern annotations

import asyncio  # timeout

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel, Field  # schemas
from crewai import Agent, Task, Crew, Process  # CrewAI

LLM_NAME = "gpt-4o-mini"  # workers: cheap model
MANAGER_LLM = "gpt-4o"  # manager: stronger model (verify availability and price)
MAX_TOKENS_BUDGET = 60_000  # per-request soft budget (tune with real usage)
app = FastAPI(title="Hierarchical Tariff API")  # ASGI app


class Req(BaseModel):  # request
    question: str = Field(..., min_length=5, max_length=500)  # user question


class Res(BaseModel):  # response
    answer: str  # final text
    total_tokens: int  # usage
    over_budget: bool  # flag for monitoring


def build() -> Crew:  # per-request crew
    workers = [  # worker agents
        Agent(role="HS Classifier", goal="Classify items", backstory="Broker.",  # worker 1
              llm=LLM_NAME, allow_delegation=False, max_iter=4),  # capped
        Agent(role="Duty Researcher", goal="Find duty", backstory="Analyst.",  # worker 2
              llm=LLM_NAME, allow_delegation=False, max_iter=4),  # capped
    ]
    manager = Agent(  # custom manager gives control over its prompt
        role="Tariff Manager",  # role
        goal="Produce a correct, complete import briefing by delegating",  # goal
        backstory="Senior trade-compliance lead who verifies worker output.",  # backstory
        llm=MANAGER_LLM,  # manager's own model
        allow_delegation=True,  # manager must be able to delegate
        max_iter=6,  # cap manager loops
    )
    task = Task(description="Answer: {q}", expected_output="Clear briefing, cite the HS code.")  # open task
    return Crew(  # assemble
        agents=workers, tasks=[task],  # workers + task
        process=Process.hierarchical, manager_agent=manager,  # manager mode with custom agent
        max_rpm=30,  # throttle
    )


@app.post("/brief", response_model=Res)  # route
async def brief(req: Req) -> Res:  # async handler
    crew: Crew = build()  # fresh crew
    try:
        out = await asyncio.wait_for(crew.akickoff(inputs={"q": req.question}), 120)  # hard timeout
    except asyncio.TimeoutError as exc:  # too slow (manager loops?)
        raise HTTPException(504, "manager timed out") from exc  # gateway timeout
    except Exception as exc:  # provider errors etc.
        raise HTTPException(502, f"crew failed: {exc}") from exc  # bad gateway
    used: int = out.token_usage.total_tokens  # tokens used
    return Res(answer=out.raw, total_tokens=used, over_budget=used > MAX_TOKENS_BUDGET)  # reply
```
Not run with a real model. Offline: FastAPI `TestClient` with the fake LLM returned 200. The 60,000 budget is an arbitrary placeholder, not a measured value.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Manager pattern | Supervisor node + conditional edges | `Process.hierarchical` | Triage agent + handoffs / agents-as-tools | SelectorGroupChat or custom manager |
| Control over routing | Full (code) | Prompt-based (LLM decides) | Prompt + handoff rules | Selector prompt/function |
| Manager config | Any node | `manager_llm` / `manager_agent` | Any agent | Selector model client |
| Predictability | High if designed | Lower (LLM-driven) | Medium | Medium |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Adding the manager agent to `agents=[...]` as well.
✅ Correct: Keep `manager_agent` separate from the worker list.

❌ Mistake 2: Setting `allow_delegation=True` on all workers; they delegate among themselves, cost explodes.
✅ Correct: Only the manager delegates.

❌ Mistake 3: Vague `expected_output`. The manager cannot judge when a worker answer is good enough.
✅ Correct: Write concrete acceptance criteria.

---

## 🧠 Tricky Interview Question
A hierarchical crew sometimes returns an answer that no worker produced. Why?

Answer: The manager is an LLM and may answer from its own knowledge instead of delegating (in my offline test the manager returned its own final text after the worker reply). If you require grounded facts, make the manager's goal say it must delegate for facts, give workers tools (search, DB), require citations in `expected_output`, add a guardrail that checks for a source field, and log which tool calls happened (via `step_callback`). If correctness is critical, use a sequential pipeline where tool use is guaranteed.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What do you need for hierarchical?
A1: `process=Process.hierarchical` plus `manager_llm` or `manager_agent`.

Q2: [Medium] `manager_llm` vs `manager_agent`?
A2: `manager_llm` lets CrewAI build a default manager; `manager_agent` gives your own role/goal/backstory/tools.

Q3: [Hard] How does the manager actually delegate?
A3: Through built-in tools such as "Delegate work to coworker" and "Ask question to coworker", where the manager names the coworker role, task and context.

Q4: [Hard] Why can it cost more?
A4: Extra manager calls for planning, delegation and review, plus context repeated in each delegated prompt.

Q5: [System Design] Make a hierarchical crew safe for production.
A5: Per-request crew, iteration caps, timeout, token budget alarm, tool allow-lists per worker, structured final output, guardrails, tracing of delegation steps, fallback to sequential or human review.

---

## 💰 Cost Impact
Expect more calls than a comparable sequential crew: manager planning + each delegation + manager review. Exact numbers depend on the task - measure with `result.token_usage` and compare. Optimisation: cheap workers, strong manager only if needed, `max_iter`, short `expected_output`, cache tool results, and route simple questions to a sequential crew. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- The task is open-ended and the steps are unknown.
- Several specialist workers might be needed.

❌ Avoid when:
- A known pipeline exists (sequential is cheaper).
- You need strict reproducibility.

---

## 📊 Visual Diagram
```
 task: "Import briefing for steel"
              |
              v
      +----------------+  Delegate work to coworker   +------------------+
      | Manager        |----------------------------->| HS Classifier    |
      | (manager_llm / |<-----------------------------| (worker)         |
      |  manager_agent)|  Delegate ...                +------------------+
      |                |----------------------------->| Duty Researcher  |
      |                |<-----------------------------| (worker)         |
      +-------+--------+                              +------------------+
              |  final answer
              v
        CrewOutput.raw
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| manager | Agent that plans and delegates | योजना बनाने व काम बाँटने वाला agent |
| worker | Agent that does sub-tasks | उप-काम करने वाला agent |
| delegation | Passing work to a coworker | coworker को काम देना |
| manager_llm | Model for default manager | default manager का model |
| manager_agent | Your own manager Agent | आपका अपना manager |
| acceptance criteria | What counts as good output | अच्छे output की कसौटी |

---

## ⚡ 3-Line Summary
English: Hierarchical process adds a manager agent that delegates work to workers.
It needs `manager_llm` or `manager_agent`, and it costs more calls.
Use it for open-ended goals, not for known pipelines.

Hindi: Hierarchical process में एक manager agent workers को काम बाँटता है।
इसके लिए `manager_llm` या `manager_agent` चाहिए और calls ज़्यादा लगती हैं।
खुले लक्ष्यों के लिए इस्तेमाल करें, तय pipeline के लिए नहीं।

---

## ➡️ Next Topic
**#92 Crew memory** - managers and workers forget everything between runs unless memory is on; next we see how crew memory stores and recalls information.

---
