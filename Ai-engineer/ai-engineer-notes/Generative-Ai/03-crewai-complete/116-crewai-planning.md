---

# 116. CrewAI Planning
# हिंदी में: CrewAI Planning (काम शुरू करने से पहले योजना बनाना)
# Framework: CrewAI
# Already Known: No

> Verified against crewai 1.15.41 (offline, fake LLM). Observed: with `planning=True` the planner makes ONE structured LLM call (`PlannerTaskPydanticOutput`) and the plan text is appended to each task description.

---

## 🔵 Simple Definition (2-3 lines)
Planning is a step that runs before the crew's tasks. A planner LLM reads all tasks and the agents, writes a short step-by-step plan for each task, and that plan is added to the task description. The agents then follow the plan. Turn it on with `Crew(planning=True)`.

## 🔵 सरल परिभाषा (Hindi)
Planning crew के tasks से पहले चलने वाला step है। एक planner LLM सारे tasks और agents पढ़कर हर task के लिए छोटी step-by-step योजना लिखता है, और वह योजना task के description में जुड़ जाती है। फिर agents उसी योजना पर चलते हैं। इसे `Crew(planning=True)` से चालू करते हैं।

---

## 🔴 Problem it Solves
Agents that jump straight into a task often wander: wrong tool first, repeated searches, missed requirements. For multi-task crews the second agent may not know what the first should produce. A plan gives a shared outline, which usually reduces wasted iterations on complex tasks.

## 🔴 यह क्यों बना? (Hindi)
Agents सीधे काम में कूदते हैं तो भटक जाते हैं: गलत tool पहले, बार-बार वही search, ज़रूरतें छूट जाना। कई tasks वाली crew में दूसरे agent को पता ही नहीं होता कि पहले से क्या उम्मीद है। Plan एक साझा रूपरेखा देता है, जिससे जटिल tasks में बेकार iterations अक्सर कम होते हैं।

---

## 🟢 How it Works

```
Step 1 → Crew(planning=True, planning_llm=<model>)
Step 2 → crew.kickoff() -> before task 1, CrewPlanner is created
Step 3 → Planner gets task descriptions + expected outputs + agent roles
Step 4 → ONE LLM call returns structured plans (task_number, task, plan)
Step 5 → Each plan text is appended to that task's description
Step 6 → Normal execution: agents see "description + plan" as the prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Crew(planning=True, planning_llm=<model>)
Step 2 → crew.kickoff() -> task 1 से पहले CrewPlanner बनता है
Step 3 → Planner को task descriptions + expected outputs + agent roles मिलते हैं
Step 4 → एक LLM call structured plans लौटाती है (task_number, task, plan)
Step 5 → हर plan का text उस task के description में जुड़ जाता है
Step 6 → सामान्य execution: agents को "description + plan" prompt की तरह दिखता है
```

---

## 🟡 Real World Example
**Tariff Agent**: tasks = (1) extract product attributes, (2) classify HS code, (3) compute landed cost. The planner writes: "1) list material, use, origin; 2) match heading using attributes, check notes; 3) apply duty table + freight". The classifier agent now knows to check section notes instead of guessing from the product name.

## 🟡 Real Example Hindi mein
**Tariff Agent**: tasks = (1) product attributes निकालो, (2) HS code तय करो, (3) landed cost निकालो। Planner लिखता है: "1) material, use, origin सूचीबद्ध करो; 2) attributes से heading मिलाओ, notes जाँचो; 3) duty table + freight लगाओ"। अब classifier agent नाम देखकर अंदाज़ा लगाने की जगह section notes जाँचता है।

---

## 💻 Code Example — Basic
```python
# Run directly: python planning_basic.py (offline, fake LLM answers the structured plan call)
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
os.environ["CREWAI_TESTING"] = "true"                  # quieter demo run
from typing import Any                                 # type hint
from crewai import Agent, Task, Crew, BaseLLM          # core classes


class FakeLLM(BaseLLM):                                # offline LLM
    def __init__(self) -> None:
        super().__init__(model="fake")

    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        if response_model is not None:                 # the planner asks for structured output
            return response_model.model_validate({     # return a valid plan object as JSON
                "list_of_plans_per_task": [
                    {"task_number": 1, "task": "Classify",
                     "plan": "1) read item 2) pick HS heading"}]}).model_dump_json()
        return "Thought: ok\nFinal Answer: HS 6109.10"  # normal ReAct answer

    def supports_function_calling(self) -> bool:
        return False


agent = Agent(role="Analyst", goal="HS code", backstory="expert",
              llm=FakeLLM(), allow_delegation=False)   # worker agent
task = Task(description="Classify", expected_output="HS code", agent=agent)  # one task
crew = Crew(agents=[agent], tasks=[task], tracing=False,
            planning=True, planning_llm=FakeLLM())     # planning ON + which LLM plans
result = crew.kickoff()                                # planner runs first, then the task
print(result.raw)                                      # -> HS 6109.10
print(task.description)                                # description now ends with the plan
```
Ran offline: prints `HS 6109.10` and `Classify1) read item 2) pick HS heading` (the plan is appended directly to the description). With a real LLM, plan quality and token use vary.

## 💻 Code Example — Advanced
```python
# Production-style: planning on/off by complexity, FastAPI, async, timing + error handling
import asyncio                                         # async + timeout
import os                                              # env switches
import time                                            # latency measurement
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
os.environ["CREWAI_TESTING"] = "true"                  # quieter demo
from typing import Any                                 # typing
from fastapi import FastAPI, HTTPException             # API
from fastapi.testclient import TestClient              # offline test
from pydantic import BaseModel                         # models
from crewai import Agent, Task, Crew, BaseLLM          # CrewAI core


class FakeLLM(BaseLLM):                                # same offline model
    def __init__(self) -> None:
        super().__init__(model="fake")
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        if response_model is not None:
            return response_model.model_validate({"list_of_plans_per_task": [
                {"task_number": 1, "task": "t", "plan": "1) attributes 2) heading"}]}).model_dump_json()
        return "Thought: ok\nFinal Answer: HS 6109.10"
    def supports_function_calling(self) -> bool:
        return False


def build_crew(item: str, complex_case: bool) -> Crew:  # factory: fresh crew per request
    agent = Agent(role="Analyst", goal=f"HS code for {item}", backstory="expert",
                  llm=FakeLLM(), allow_delegation=False, max_iter=5)  # cap loops
    task = Task(description="Classify {item}", expected_output="HS code", agent=agent)
    return Crew(agents=[agent], tasks=[task], tracing=False,
                planning=complex_case,                 # pay for planning only when it helps
                planning_llm=FakeLLM() if complex_case else None)


app = FastAPI()


class Req(BaseModel):
    item: str
    complex_case: bool = False                         # caller/classifier decides


@app.post("/classify")
async def classify(req: Req) -> dict[str, Any]:
    t0 = time.perf_counter()                           # start timer
    try:
        out = await asyncio.wait_for(
            build_crew(req.item, req.complex_case).kickoff_async(inputs={"item": req.item}), 90)
    except asyncio.TimeoutError:
        raise HTTPException(504, "timeout")
    except Exception as e:
        raise HTTPException(502, f"crew failed: {type(e).__name__}")
    return {"answer": out.raw, "planned": req.complex_case,
            "tokens": out.token_usage.total_tokens,    # 0 with the fake model
            "seconds": round(time.perf_counter() - t0, 3)}


with TestClient(app) as c:
    print(c.post("/classify", json={"item": "shirt", "complex_case": True}).json())
    print(c.post("/classify", json={"item": "shirt", "complex_case": False}).json())
```
Ran offline; both calls return `HS 6109.10` (tokens are 0 only because the fake LLM reports none).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Built-in planner | No (build a planner node) | Yes: `Crew(planning=True)` | No (prompt it yourself) | Magentic-One orchestrator plans (extension) |
| Plan format | Your state schema | Text appended to task description | Your own | Ledger in orchestrator |
| Re-planning | You code the loop | Agent-level `planning_config` exists (see 117) | You code it | Orchestrator re-plans |
| Extra LLM calls | You control | +1 call per kickoff (crew level) | You control | Several |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Enabling planning for trivial single-task crews.
✅ Correct: Use it for multi-step tasks; for simple ones it only adds tokens and latency.

❌ Mistake 2: Forgetting `planning_llm`, so the planner uses a default model you did not budget for.
✅ Correct: Set `planning_llm` explicitly (a cheaper model often works for planning).

❌ Mistake 3: Assuming the plan is enforced.
✅ Correct: The plan is just extra prompt text. Validate outputs with `expected_output` and guardrails.

---

## 🧠 Tricky Interview Question
You enabled planning and cost went up 25% but quality did not change. Why, and what do you do?

Answer: Planning adds one LLM call and longer task prompts for every task, so token cost rises. If tasks are already well specified (clear `description` and `expected_output`), the plan duplicates information. Measure quality on a fixed test set with and without planning, enable it only for complex or ambiguous requests, and use a small model for planning.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you enable planning in CrewAI?
A1: `Crew(..., planning=True, planning_llm=...)`.

Q2: [Medium] Where does the plan go?
A2: The planner returns structured plans; each plan is appended to the matching task's description before execution.

Q3: [Hard] Is planning the same as hierarchical process?
A3: No. Planning writes a plan once up front. Hierarchical process uses a manager agent that delegates and reviews during execution.

Q4: [Hard] How would you measure whether planning helps?
A4: A/B on a labelled set: accuracy/pass rate, tokens per run, latency, iteration counts. Keep it only where the gain justifies the extra cost.

Q5: [System Design] Design a service that decides per request whether to plan.
A5: A cheap router (rules or a small model) scores complexity (number of sub-questions, tools needed); complex -> `planning=True` with a mid model; simple -> no planning. Log the choice and outcome to tune the threshold.

---

## 💰 Cost Impact
- Extra cost = one planner call (input = all task descriptions + agent info; output = a plan per task) plus longer prompts for every later LLM call because the plan text is added to each task description.
- Formula: `extra_tokens ~= planner_in + planner_out + (plan_tokens x number_of_LLM_calls_in_task)`.
- Tips: cheaper `planning_llm`, short plans, enable only for complex requests. Exact numbers depend on your model; measure with `result.token_usage`.

---

## 🔷 When to Use
✅ Use when:
- Multi-task crews with dependencies
- Ambiguous or long-horizon requests
- Agents tend to skip steps or pick wrong tools

❌ Avoid when:
- One simple task with a clear prompt
- Tight latency or cost budgets

---

## 📊 Visual Diagram
```
 crew.kickoff()
      |
      v
 +-----------------+   1 structured LLM call
 |   CrewPlanner   | ------------------------> plans[]
 +-----------------+
      | append plan text to each task.description
      v
 Task 1 (Agent A) -> Task 2 (Agent B) -> ... -> CrewOutput
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Planning | Plan written before execution | निष्पादन से पहले योजना |
| `planning_llm` | Model used by the planner | planner का model |
| Plan | Step list per task | हर task की step सूची |
| Hierarchical | Manager-delegation process | manager द्वारा काम बाँटना |
| expected_output | Required result description | अपेक्षित परिणाम का वर्णन |

---

## ⚡ 3-Line Summary
English: `planning=True` adds a planner call whose plan is appended to each task. It helps complex multi-step crews but costs extra tokens. Set `planning_llm` and enable it selectively.
Hindi: `planning=True` एक planner call जोड़ता है जिसकी योजना हर task में जुड़ती है। यह जटिल multi-step crews में मदद करता है पर extra tokens लेता है। `planning_llm` तय करो और ज़रूरत पर ही चालू करो।

---

## ➡️ Next Topic
**117. Planning with LLM** — choosing the planning model and using the newer per-agent `PlanningConfig` controls.

---
