---

# 355. Planner + Executor Pattern
# हिंदी में: Planner + Executor Pattern

---

## 🔵 Simple Definition (English)
One agent (the **Planner**) breaks a big goal into an ordered list of small steps. Another agent (the **Executor**) carries out each step with tools. After steps finish, the planner can **re-plan** if something failed. Planning and doing are separated.

## 🔵 सरल परिभाषा (Hindi)
एक agent (**Planner**) बड़े लक्ष्य को छोटे steps की क्रमबद्ध सूची में बाँटता है। दूसरा agent (**Executor**) tools की मदद से हर step करता है। Steps पूरे होने के बाद कुछ fail हो तो planner **re-plan** कर सकता है। सोचना और करना अलग रखे जाते हैं।

---

## 🔴 Problem it Solves
A ReAct agent decides one step at a time. On long tasks it forgets the goal, repeats actions and uses a big expensive model for every tiny step. There is no visible plan to review. Planner + Executor creates a plan once (strong model), then runs simple steps (cheap model), and gives you a plan you can inspect or approve.

## 🔴 यह क्यों बना? (Hindi)
ReAct agent एक बार में एक step सोचता है। लंबे tasks में वह लक्ष्य भूल जाता है, actions दोहराता है और हर छोटे step के लिए बड़ा महँगा model चलाता है। Review करने लायक कोई plan नहीं दिखता। Planner + Executor एक बार plan बनाता है (strong model), फिर सरल steps चलाता है (सस्ता model), और आपको जाँचने या approve करने के लिए plan देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User goal arrives: "Classify this shipment and compute duty"
Step 2 → Planner (strong LLM) writes plan: [step1, step2, step3]
Step 3 → Executor takes step 1, calls the right tool, stores result
Step 4 → Result is appended to "past_steps" in shared state
Step 5 → Replanner checks: goal done? plan still valid?
Step 6 → If not done -> update the remaining plan, go to Step 3
Step 7 → If done -> produce final answer
Step 8 → Hard cap on steps to prevent endless loops
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User का goal आता है: "इस shipment को classify करो और duty निकालो"
Step 2 → Planner (strong LLM) plan लिखता है: [step1, step2, step3]
Step 3 → Executor step 1 लेता है, सही tool बुलाता है, result रखता है
Step 4 → Result shared state की "past_steps" में जुड़ता है
Step 5 → Replanner जाँचता है: goal पूरा? plan अब भी सही?
Step 6 → पूरा नहीं -> बचा plan अपडेट करो, Step 3 पर जाओ
Step 7 → पूरा -> final answer बनाओ
Step 8 → अनंत loop रोकने के लिए steps की hard limit
```

---

## 🟡 Real World Example
**Tariff Classification System**: Goal: "Import 500 Bluetooth speakers from Vietnam, give landed cost." Planner output: (1) classify HS code, (2) fetch duty rate for that code and origin, (3) check Vietnam FTA eligibility, (4) compute total landed cost. Executor runs each with tools (`classify_hs`, `get_duty`, `check_fta`, `calculator`). If step 3 shows FTA needs a certificate of origin, the replanner adds step "request certificate".

**Zomato-style**: "Plan a dinner for 8 people under Rs 4000": planner splits into find restaurants, check menus, check budget, place order.

## 🟡 Real Example Hindi mein
**Tariff System**: Goal: "वियतनाम से 500 Bluetooth speakers import करो, landed cost बताओ।" Planner का output: (1) HS code classify, (2) उस code और origin की duty rate, (3) Vietnam FTA eligibility, (4) कुल landed cost। Executor हर step tools (`classify_hs`, `get_duty`, `check_fta`, `calculator`) से चलाता है। Step 3 में पता चले कि FTA के लिए certificate of origin चाहिए तो replanner नया step "certificate माँगो" जोड़ देता है।

**Zomato-style**: "8 लोगों का dinner Rs 4000 में plan करो": planner restaurants खोजना, menu देखना, budget जाँचना, order करना में बाँटता है।

---

## 💻 Code Example — Basic
```python
# Planner + Executor in plain Python with mock LLM and tools (runs offline)
from typing import Callable  # for tool type hints

# Tools the executor may call: name -> function
def classify_hs(x: str) -> str: return "8518.22"               # fake HS lookup
def get_duty(code: str) -> float: return 0.20                    # fake duty rate (20 percent)
def landed_cost(value: float, duty: float) -> float: return value * (1 + duty)  # simple formula

TOOLS: dict[str, Callable[..., object]] = {"classify": classify_hs, "duty": get_duty, "cost": landed_cost}  # registry

def planner(goal: str) -> list[str]:
    # A real planner is an LLM call that returns JSON steps
    return ["classify", "duty", "cost"]  # fixed plan for the demo

def executor(step: str, memory: dict[str, object]) -> object:
    # Executes ONE step using results stored in memory
    if step == "classify":
        return TOOLS["classify"]("bluetooth speaker")  # returns HS code
    if step == "duty":
        return TOOLS["duty"](memory["classify"])  # uses previous result
    if step == "cost":
        return TOOLS["cost"](1000.0, memory["duty"])  # final calculation
    raise ValueError(f"unknown step {step}")  # unknown steps are errors

def run(goal: str, max_steps: int = 10) -> dict[str, object]:
    memory: dict[str, object] = {}  # shared results
    plan = planner(goal)  # plan once
    for i, step in enumerate(plan):  # execute in order
        if i >= max_steps:  # safety cap
            break
        memory[step] = executor(step, memory)  # store each result
    return memory

if __name__ == "__main__":
    print(run("landed cost of bluetooth speakers"))  # {'classify': '8518.22', 'duty': 0.2, 'cost': 1200.0}
```

## 💻 Code Example — Advanced
```python
# Async planner/executor with replanning, retries and token accounting
import asyncio  # async runtime
from dataclasses import dataclass, field  # state container

@dataclass
class PEState:
    goal: str                                              # user goal
    plan: list[str] = field(default_factory=list)          # remaining steps
    past: list[tuple[str, str]] = field(default_factory=list)  # (step, result)
    tokens: int = 0                                        # running estimate
    final: str = ""                                        # final answer

async def plan_llm(goal: str, past: list[tuple[str, str]]) -> list[str]:
    await asyncio.sleep(0)  # fake latency
    done = {s for s, _ in past}  # steps already executed
    full = ["classify", "duty", "fta_check", "cost"]  # what the model "decides"
    return [s for s in full if s not in done]  # replan = remaining steps

async def run_step(step: str) -> str:
    await asyncio.sleep(0)  # fake tool latency
    if step == "fta_check":
        return "certificate_of_origin_required"  # surprise that forces a replan
    return f"{step}:ok"

async def pe_agent(goal: str, max_steps: int = 8) -> PEState:
    st = PEState(goal=goal)  # new state
    try:
        st.plan = await plan_llm(goal, st.past)  # initial plan
        st.tokens += 400  # planner tokens
        steps = 0
        while st.plan and steps < max_steps:  # bounded loop
            step = st.plan.pop(0)  # next step
            res = await run_step(step)  # execute (cheap)
            st.past.append((step, res))  # record
            st.tokens += 150  # executor tokens
            steps += 1
            if "required" in res:  # something unexpected
                st.plan = await plan_llm(goal, st.past)  # replan
                st.tokens += 300  # replanner tokens
        st.final = "; ".join(f"{s}={r}" for s, r in st.past)  # summarise
    except Exception as exc:  # fail safe
        st.final = f"failed: {exc}"
    return st

if __name__ == "__main__":
    out = asyncio.run(pe_agent("landed cost for speakers"))
    print(out.final, out.tokens)
```

---

## 🟠 FastAPI Integration
Return the plan before executing so a UI (or an approver) can see it. Offer `plan` and `execute` endpoints for human approval.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()
PLANS: dict[str, list[str]] = {}  # in production use Redis or a DB

class GoalIn(BaseModel):
    goal: str  # user goal

@app.post("/agent/plan")
async def make_plan(body: GoalIn) -> dict:
    plan = await plan_llm(body.goal, [])  # planner only
    pid = str(len(PLANS) + 1)  # simple id
    PLANS[pid] = plan  # store for approval
    return {"plan_id": pid, "plan": plan}

@app.post("/agent/execute/{plan_id}")
async def execute(plan_id: str) -> dict:
    plan = PLANS.get(plan_id)  # find approved plan
    if plan is None:
        raise HTTPException(404, "plan not found")  # clear error
    results = [(s, await run_step(s)) for s in plan]  # run steps in order
    return {"results": results}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import Annotated, TypedDict  # state typing
import operator  # reducer to append lists
from langgraph.graph import StateGraph, START, END  # graph API

class PlanState(TypedDict):
    input: str                                          # goal
    plan: list[str]                                     # remaining steps
    past_steps: Annotated[list[tuple[str, str]], operator.add]  # reducer: append only
    response: str                                       # final answer

def plan_step(s: PlanState) -> dict:
    steps = planner_chain.invoke({"goal": s["input"]})  # LCEL: prompt | gpt-4o | structured plan
    return {"plan": steps}

def execute_step(s: PlanState) -> dict:
    task = s["plan"][0]                                  # next task
    result = executor_agent.invoke({"messages": [("user", task)]})  # e.g. create_react_agent with tools
    return {"past_steps": [(task, result["messages"][-1].content)], "plan": s["plan"][1:]}

def replan_step(s: PlanState) -> dict:
    if not s["plan"]:                                    # nothing left -> answer
        return {"response": summarizer_chain.invoke({"past": s["past_steps"]})}
    return {}                                            # keep going

def should_end(s: PlanState) -> str:
    return "end" if s.get("response") else "execute"

g = StateGraph(PlanState)
g.add_node("planner", plan_step)
g.add_node("executor", execute_step)
g.add_node("replan", replan_step)
g.add_edge(START, "planner")
g.add_edge("planner", "executor")
g.add_edge("executor", "replan")
g.add_conditional_edges("replan", should_end, {"end": END, "execute": "executor"})
app_graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No step limit
✅ Correct: cap steps and cap replans.

```python
# Wrong
while plan: run(plan.pop(0))   # replanner can add steps forever
# Right
while plan and steps < MAX_STEPS: ...
```

❌ Mistake 2: Executor receives the whole plan and history
✅ Correct: give the executor only its current step plus the results it needs.

```python
# Wrong: huge context every step
executor.invoke({"plan": plan, "history": all_history})
# Right
executor.invoke({"task": step, "inputs": needed_results})
```

---

## 🧠 Tricky Interview Question
**Q**: "Plan has 6 steps, step 3 fails. Should you retry, replan, or abort?"

**Answer**: Classify the failure. Transient (timeout, 429): retry with backoff, no replan. Wrong input or missing data: replan with the error as context. Policy or impossible goal: abort and tell the user. Keep a replan budget (for example 2) and make steps idempotent so retries are safe. Never let the executor silently skip a failed step, later steps depend on it.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the two roles?
A1: Planner makes the ordered steps; Executor performs one step at a time using tools.

Q2: [Easy] Why is it cheaper than pure ReAct?
A2: The big model plans once; a smaller model executes simple steps with short context.

Q3: [Medium] What is a replanner?
A3: A node that looks at completed steps and results and either finishes or rewrites the remaining plan.

Q4: [Medium] Static plan vs dynamic plan?
A4: Static is predictable and cheap but breaks on surprises. Dynamic (replanning) adapts but costs more tokens and needs loop limits.

Q5: [Hard] How do you evaluate a planner?
A5: Score plan validity (every step maps to a tool), completeness, minimality (no useless steps), and final task success on a test set. Track steps per task, replan rate, and cost per success.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks need 3+ dependent steps
- You want an inspectable or approvable plan
- Planner needs a strong model but steps are simple

❌ Avoid when:
- One tool call solves it
- Steps cannot be known in advance and every result changes direction (use ReAct)

---

## 📊 Visual Diagram
```
 Goal -> [Planner] -> plan: [s1, s2, s3]
                         |
                    +----v-----+   result   +-----------+
                    | Executor | ---------> | past_steps|
                    +----^-----+            +-----+-----+
                         |  remaining plan       |
                    [Replanner] <----------------+
                         |
                  done? -> Final answer
```

---

## 💰 Cost Impact
- Planner: 1 call on a strong model (about 500 tokens in, 200 out).
- Executor: N short calls on a cheap model (about 150 tokens each).
- Replanner: extra call only on surprises.
- Optimise: strong model only for planning, small model for execution, pass only needed results, cap steps and replans, cache plans for repeated goals (like "landed cost").

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Planner | Creates the step list | Steps की सूची बनाने वाला |
| Executor | Runs one step with tools | एक step चलाने वाला |
| Replanner | Updates plan after results | Results के बाद plan बदलने वाला |
| past_steps | History of finished steps | पूरे हुए steps का इतिहास |
| Idempotent | Safe to repeat | दोहराने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
English: A planner writes the steps, an executor performs them, a replanner fixes the plan after surprises. It saves cost and gives an inspectable plan. Always cap steps and replans.
Hindi: Planner steps लिखता है, executor उन्हें करता है, replanner surprise के बाद plan ठीक करता है। इससे cost बचती है और plan देखा जा सकता है। Steps और replans हमेशा सीमित रखो।

---

## ➡️ Next Topic
**356. Critic + Generator Pattern** — one agent writes, another reviews, improving quality through feedback loops.
