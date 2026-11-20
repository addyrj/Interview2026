---

# 117. Planning with LLM
# हिंदी में: Planning के लिए अलग LLM चुनना और PlanningConfig
# Framework: CrewAI
# Already Known: No

> Verified against crewai 1.15.41. Crew-level `planning_llm` was RUN offline with a fake LLM and the planner call was confirmed to go to the planner model. Agent-level `PlanningConfig` was introspected (field names/defaults) and constructed, but NOT run: a naive fake LLM made the agent-level planning loop hang in my test, so run it only against a real model.

---

## 🔵 Simple Definition (2-3 lines)
"Planning with LLM" means choosing which model writes the plan. The planner can be a different (often cheaper or stronger) model than the agents that do the work: `Crew(planning=True, planning_llm=...)`. Newer versions also let one agent plan its own steps with `Agent(planning_config=PlanningConfig(...))`.

## 🔵 सरल परिभाषा (Hindi)
"Planning with LLM" का मतलब है यह चुनना कि योजना कौन सा model लिखे। Planner काम करने वाले agents से अलग (अक्सर सस्ता या ज़्यादा मज़बूत) model हो सकता है: `Crew(planning=True, planning_llm=...)`। नए versions में एक agent अपने steps खुद भी plan कर सकता है: `Agent(planning_config=PlanningConfig(...))`।

---

## 🔴 Problem it Solves
Using the same expensive model for planning and execution wastes money; using a weak model for planning gives vague plans. Different tasks also need different planning depth: a one-line lookup needs none, a 6-step customs investigation needs a lot. You need knobs for model choice, effort and step limits.

## 🔴 यह क्यों बना? (Hindi)
Planning और execution दोनों में एक ही महँगा model लगाना पैसे की बर्बादी है; planning में कमज़ोर model लगाने से अस्पष्ट योजना मिलती है। अलग tasks को अलग गहराई की planning चाहिए: एक लाइन की lookup को कुछ नहीं, 6-step customs जाँच को बहुत। इसलिए model चुनने, effort और step limit के नियंत्रण चाहिए।

---

## 🟢 How it Works

```
Crew level:
Step 1 → Crew(planning=True, planning_llm="provider/model" or a BaseLLM)
Step 2 → CrewPlanner(tasks, planning_agent_llm=planning_llm) is built
Step 3 → Planner model returns structured plans; agents use their own LLM

Agent level (PlanningConfig fields, verified by introspection):
Step 4 → reasoning_effort: "low" | "medium" (default) | "high"
Step 5 → max_steps, max_replans, max_step_iterations, step_timeout, max_attempts
Step 6 → llm: model for planning; plan_prompt/refine_prompt/system_prompt overrides
```

## 🟢 कैसे काम करता है? (Hindi)

```
Crew level:
Step 1 → Crew(planning=True, planning_llm="provider/model" या BaseLLM)
Step 2 → CrewPlanner(tasks, planning_agent_llm=planning_llm) बनता है
Step 3 → Planner model structured plans देता है; agents अपना LLM इस्तेमाल करते हैं

Agent level (PlanningConfig fields, introspection से जाँचे हुए):
Step 4 → reasoning_effort: "low" | "medium" (default) | "high"
Step 5 → max_steps, max_replans, max_step_iterations, step_timeout, max_attempts
Step 6 → llm: planning का model; plan_prompt/refine_prompt/system_prompt बदलने के लिए
```

---

## 🟡 Real World Example
**Tariff Agent**: planner = a mid-size model (cheap, good at outlining); executor agents = a strong model only for the classification step. For an urgent "high-value shipment" request you flip `reasoning_effort="high"` so the agent observes each step and replans on surprises (for example, a missing material composition).

## 🟡 Real Example Hindi mein
**Tariff Agent**: planner = मध्यम आकार का सस्ता model (रूपरेखा बनाने में ठीक); executor agents = सिर्फ़ classification step पर मज़बूत model। "ज़्यादा मूल्य वाली shipment" के लिए `reasoning_effort="high"` करते हैं ताकि agent हर step देखे और अनपेक्षित बात (जैसे material composition का न मिलना) पर दोबारा योजना बनाए।

---

## 💻 Code Example — Basic
```python
# Run directly: python planner_llm_basic.py (offline). Shows the planner model gets the plan call.
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
os.environ["CREWAI_TESTING"] = "true"                  # quieter
from typing import Any                                 # typing
from crewai import Agent, Task, Crew, BaseLLM          # core

CALLS: list[tuple[str, str]] = []                      # (model name, kind) log


class FakeLLM(BaseLLM):                                # offline LLM with a visible name
    def __init__(self, name: str) -> None:
        super().__init__(model=name)

    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        CALLS.append((self.model, "structured" if response_model else "text"))  # record
        if response_model is not None:                 # planner request
            return response_model.model_validate({"list_of_plans_per_task": [
                {"task_number": 1, "task": "Classify", "plan": "1) attributes 2) heading"}]}).model_dump_json()
        return "Thought: ok\nFinal Answer: HS 6109.10"

    def supports_function_calling(self) -> bool:
        return False


agent = Agent(role="Analyst", goal="HS", backstory="expert",
              llm=FakeLLM("executor-strong"), allow_delegation=False)  # executes the task
task = Task(description="Classify", expected_output="HS code", agent=agent)
crew = Crew(agents=[agent], tasks=[task], tracing=False, planning=True,
            planning_llm=FakeLLM("planner-cheap"))     # different model plans
print(crew.kickoff().raw)                              # -> HS 6109.10
print(CALLS)                                           # planner-cheap structured, executor-strong text
```
Ran offline; the call log shows `('planner-cheap', 'structured')` followed by `('executor-strong', 'text')`.

## 💻 Code Example — Advanced
```python
# Production-style: choose planner model + effort by request tier, behind FastAPI.
# Crew-level path is RUN offline. The agent-level PlanningConfig is only CONSTRUCTED here
# (not run: needs a real model, see note at top).
import asyncio                                         # async + timeout
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
os.environ["CREWAI_TESTING"] = "true"                  # quieter
from typing import Any, Literal                        # typing
from fastapi import FastAPI, HTTPException             # API
from fastapi.testclient import TestClient              # offline test
from pydantic import BaseModel                         # models
from crewai import Agent, Task, Crew, BaseLLM          # core
from crewai.agent.planning_config import PlanningConfig  # per-agent planning knobs

Tier = Literal["fast", "careful"]                      # request tiers


class FakeLLM(BaseLLM):
    def __init__(self, name: str = "fake") -> None:
        super().__init__(model=name)
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        if response_model is not None:
            return response_model.model_validate({"list_of_plans_per_task": [
                {"task_number": 1, "task": "t", "plan": "1) a 2) b"}]}).model_dump_json()
        return "Thought: ok\nFinal Answer: HS 6109.10"
    def supports_function_calling(self) -> bool:
        return False


def planning_config_for(tier: Tier) -> PlanningConfig:  # agent-level config (constructed only)
    effort: Literal["low", "medium", "high"] = "high" if tier == "careful" else "low"
    return PlanningConfig(reasoning_effort=effort,     # observe/replan depth
                          max_steps=6 if tier == "careful" else 3,   # plan length cap
                          max_replans=2 if tier == "careful" else 0, # replan budget
                          step_timeout=60)             # seconds per step (verify unit in docs)


def build(item: str, tier: Tier) -> Crew:
    agent = Agent(role="Analyst", goal=f"HS for {item}", backstory="expert",
                  llm=FakeLLM("executor"), allow_delegation=False, max_iter=6)
    task = Task(description="Classify {item}", expected_output="HS code", agent=agent)
    return Crew(agents=[agent], tasks=[task], tracing=False,
                planning=(tier == "careful"),          # crew-level planning only for careful
                planning_llm=FakeLLM("planner") if tier == "careful" else None)


app = FastAPI()


class Req(BaseModel):
    item: str
    tier: Tier = "fast"


@app.post("/classify")
async def classify(req: Req) -> dict[str, Any]:
    try:
        out = await asyncio.wait_for(build(req.item, req.tier).kickoff_async(
            inputs={"item": req.item}), 120)
    except asyncio.TimeoutError:
        raise HTTPException(504, "timeout")
    except Exception as e:
        raise HTTPException(502, f"failed: {type(e).__name__}")
    return {"answer": out.raw, "tier": req.tier, "tokens": out.token_usage.total_tokens}


cfg = planning_config_for("careful")                   # prove the config object builds
print(cfg.reasoning_effort, cfg.max_steps, cfg.max_replans)
with TestClient(app) as c:
    print(c.post("/classify", json={"item": "shirt", "tier": "careful"}).json())
    print(c.post("/classify", json={"item": "shirt", "tier": "fast"}).json())
```
Ran offline (config construction + crew-level planning via the API). Agent-level `planning_config` execution: **not run — needs a real LLM**. Token usage prints 0 because the fake LLM reports none.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Planner model choice | Any model in a planner node | `planning_llm` (crew) / `PlanningConfig.llm` (agent) | Separate planner `Agent` with its own `model` | Orchestrator's own `model_client` |
| Effort control | You code it | `reasoning_effort` low/medium/high | `ModelSettings` / reasoning params | Orchestrator limits (e.g. max stalls) |
| Replan limit | Loop counter in state | `max_replans` | Loop in your code | Orchestrator re-plan limit |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Same big model for plan and execution on every request.
✅ Correct: Use a cheaper `planning_llm`; keep the strong model for the hard step.

❌ Mistake 2: Setting both crew-level and agent-level planning without understanding the extra calls.
✅ Correct: Pick one level per use case and count the LLM calls it adds.

❌ Mistake 3: Trusting config names from blog posts (they change between versions).
✅ Correct: Introspect `PlanningConfig.model_fields` in your installed version.

---

## 🧠 Tricky Interview Question
Planning improves accuracy in your offline eval but hurts in production. Why?

Answer: Production inputs are messier and tool calls fail more often; a rigid plan written before seeing tool results can send the agent down a wrong path. Higher `reasoning_effort` with observation and replanning helps, but costs latency and tokens. Also check prompt-length growth and timeouts. Evaluate on production-like traces, not clean test inputs.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which parameter picks the planner model for a crew?
A1: `planning_llm`.

Q2: [Medium] Can the planner model differ from the agents' model?
A2: Yes; agents use their own `llm`. The planner only writes the plan text.

Q3: [Hard] What do `reasoning_effort` levels mean in `PlanningConfig`?
A3: Per the installed field description: low skips per-step observation LLM calls (fastest), medium observes and replans only on step failure, high runs the full observation pipeline with replanning and early goal detection (most adaptive, slowest).

Q4: [Hard] How do you control planning cost?
A4: Cheaper planner, `max_steps`, low effort, tier-based enabling, and monitoring tokens per run.

Q5: [System Design] Design adaptive planning for a research agent platform.
A5: Router scores complexity; simple -> no planning; medium -> crew-level plan; complex -> agent-level high effort with replans and a hard budget on tokens/time; log plans and outcomes to tune thresholds.

---

## 💰 Cost Impact
- Crew-level: +1 planner call per kickoff. Agent-level: extra calls per step depending on effort (high adds observation LLM calls per step).
- Formula: `cost = planner_calls x planner_price + executor_calls x executor_price`.
- Tips: cheap planner, `reasoning_effort="low"` by default, cap `max_steps` and `max_replans`. Token counts vary by model; read `CrewOutput.token_usage` in your own runs.

---

## 🔷 When to Use
✅ Use when:
- Tasks are long-horizon and plan quality matters
- You want a cheap planner and a strong executor

❌ Avoid when:
- Simple lookups
- Strict latency SLAs without budget for extra calls

---

## 📊 Visual Diagram
```
 request -> tier router
              |
   fast ------+------ careful
    |                    |
 no planning     planner LLM (cheap) --plan--> task description
    |                    |
    +--> executor LLM (strong) <-----------+
                         |
                      answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `planning_llm` | Model that writes the plan | योजना लिखने वाला model |
| `PlanningConfig` | Agent-level planning options | agent स्तर के planning विकल्प |
| `reasoning_effort` | Depth of observe/replan | सोच/पुनर्योजना की गहराई |
| Replan | Revise plan after a surprise | अनपेक्षित पर योजना बदलना |
| Executor | Model doing the task | काम करने वाला model |

---

## ⚡ 3-Line Summary
English: Choose the planner model separately with `planning_llm`. Use `PlanningConfig` for per-agent effort and step limits. Always measure extra tokens.
Hindi: `planning_llm` से planner model अलग चुनो। हर agent के effort और step सीमा के लिए `PlanningConfig` इस्तेमाल करो। extra tokens हमेशा नापो।

---

## ➡️ Next Topic
**118. CrewAI Training** — teaching agents from human feedback so results improve across runs.

---
