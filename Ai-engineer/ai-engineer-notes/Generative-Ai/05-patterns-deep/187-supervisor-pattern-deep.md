---

# 187. Supervisor Pattern — Deep
# हिंदी में: Supervisor Pattern (निगरानी करने वाला मुख्य Agent) — विस्तार से
# Framework: All
# Already Known: No

> Verified offline with fake supervisor and workers (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
In the Supervisor pattern one central agent owns the goal. It repeatedly decides which worker agent should act next, reads the worker's result, and decides again, until it says FINISH. Workers do not talk to each other; all communication goes through the supervisor.

## 🔵 सरल परिभाषा (Hindi)
Supervisor pattern में एक केंद्रीय agent लक्ष्य का मालिक होता है। वह बार-बार तय करता है कि अगला काम कौन-सा worker करे, उसका नतीजा पढ़ता है और फिर तय करता है, जब तक वह FINISH न कहे। Workers आपस में बात नहीं करते; सारा संवाद supervisor के ज़रिए होता है।

---

## 🔴 Problem it Solves
A router (note 186) makes one decision and leaves. Real tasks need several steps: classify, then compute duty, then check compliance, then write the answer. Letting agents call each other freely creates tangled flows. A supervisor gives one place for planning, ordering, budgets, logging and stop conditions.

## 🔴 यह क्यों बना? (Hindi)
Router (नोट 186) एक बार फ़ैसला करके चला जाता है। असली काम कई steps का होता है: classify, फिर duty निकालो, फिर compliance जाँचो, फिर जवाब लिखो। Agents को आपस में खुली छूट देने से उलझा flow बनता है। Supervisor planning, क्रम, budget, logging और stop conditions के लिए एक ही जगह देता है।

---

## 🟢 How it Works

```
Step 1 → Supervisor receives goal + state (results so far)
Step 2 → Supervisor picks next: one of {classifier, duty, compliance, FINISH}
Step 3 → The chosen worker runs with only what it needs; returns a result
Step 4 → Result is written into shared state
Step 5 → Back to Step 2 (supervisor re-decides with the new state)
Step 6 → FINISH → supervisor composes the final answer
Step 7 → Guards: max_steps, no repeated worker with same input, token budget
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Supervisor को goal + अब तक का state मिलता है
Step 2 → Supervisor अगला चुनता है: {classifier, duty, compliance, FINISH} में से एक
Step 3 → चुना गया worker सिर्फ़ ज़रूरी input के साथ चलता है और result लौटाता है
Step 4 → Result shared state में लिखा जाता है
Step 5 → फिर Step 2 पर वापसी (नए state के साथ supervisor दोबारा तय करता है)
Step 6 → FINISH → supervisor अंतिम जवाब बनाता है
Step 7 → Guards: max_steps, एक ही input पर वही worker दोबारा नहीं, token budget
```

---

## 🟡 Real World Example
**Tariff Agent**: Goal: "Import cost of 100 Bluetooth speakers from China to India". Supervisor calls the classifier (HS 8518.22), then the duty agent (rate), then the compliance agent (BIS certification needed), then FINISH with a combined answer. If compliance returns "restricted", the supervisor can stop early and skip the cost calculation.

## 🟡 Real Example Hindi mein
**Tariff Agent**: Goal: "चीन से India में 100 Bluetooth speakers का import cost"। Supervisor पहले classifier (HS 8518.22), फिर duty agent (rate), फिर compliance agent (BIS certification चाहिए) को बुलाता है, और फिर संयुक्त जवाब के साथ FINISH। Compliance "restricted" लौटाए तो supervisor जल्दी रुककर cost गणना छोड़ सकता है।

---

## 💻 Code Example — Basic
```python
# Basic supervisor loop: rule-based "LLM" picks the next worker. Runs offline.
from typing import Callable                       # handler type

State = dict[str, str]                            # shared state: worker name -> result


def classifier(s: State) -> str:                  # worker 1 (fake)
    return "8518.22"


def duty(s: State) -> str:                        # worker 2 needs classifier output
    return f"7.5% for {s['classifier']}"


def compliance(s: State) -> str:                  # worker 3 (fake)
    return "BIS certificate required"


WORKERS: dict[str, Callable[[State], str]] = {    # registry the supervisor can call
    "classifier": classifier, "duty": duty, "compliance": compliance,
}


def supervisor_decide(s: State) -> str:           # stands in for an LLM deciding next step
    for name in ("classifier", "duty", "compliance"):  # fixed order here for the demo
        if name not in s:                         # first worker not yet done
            return name
    return "FINISH"                               # everything done


def run(goal: str, max_steps: int = 6) -> str:
    state: State = {}                             # empty shared state
    for _ in range(max_steps):                    # guard: bounded steps
        nxt = supervisor_decide(state)            # supervisor chooses
        if nxt == "FINISH":                       # done
            break
        state[nxt] = WORKERS[nxt](state)          # worker runs, result stored
        print(f"called {nxt} -> {state[nxt]}")    # observability
    return f"{goal}: {state}"                     # final composed answer


if __name__ == "__main__":
    print(run("import 100 speakers"))
```

## 💻 Code Example — Advanced
```python
# Advanced: async supervisor with pydantic-validated decisions, worker timeout,
# repeat-call guard, early exit on "restricted", FastAPI endpoint. Offline.
import asyncio                                    # async + timeout
from typing import Literal                        # closed set of choices
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # offline client
from pydantic import BaseModel                    # validation

Next = Literal["classifier", "duty", "compliance", "FINISH"]


class Decision(BaseModel):                        # supervisor output contract
    next: Next
    reason: str


class Req(BaseModel):
    goal: str
    restricted: bool = False                      # lets the demo trigger early exit


async def decide(state: dict[str, str]) -> Decision:  # fake async LLM supervisor
    await asyncio.sleep(0)
    if "classifier" not in state:
        return Decision(next="classifier", reason="need HS code first")
    if state.get("compliance", "").startswith("RESTRICTED"):
        return Decision(next="FINISH", reason="restricted: stop early")
    if "compliance" not in state:
        return Decision(next="compliance", reason="check legality before cost")
    if "duty" not in state and not state["compliance"].startswith("RESTRICTED"):
        return Decision(next="duty", reason="compute duty")
    return Decision(next="FINISH", reason="all done")


async def worker(name: str, state: dict[str, str], restricted: bool) -> str:
    await asyncio.sleep(0)                        # simulate I/O
    if name == "classifier":
        return "8518.22"
    if name == "compliance":
        return "RESTRICTED" if restricted else "OK, BIS needed"
    return f"7.5% for {state['classifier']}"      # duty


app = FastAPI()


@app.post("/run")
async def run(req: Req) -> dict:
    state: dict[str, str] = {}                    # shared state
    called: list[str] = []                        # audit trail
    for step in range(8):                         # hard cap on supervisor turns
        d = await decide(state)                   # supervisor decides
        if d.next == "FINISH":
            return {"state": state, "steps": called, "stop_reason": d.reason}
        if d.next in state:                       # repeat-call guard (no loops on same worker)
            return {"state": state, "steps": called, "stop_reason": "repeat guard"}
        try:
            state[d.next] = await asyncio.wait_for(   # per-worker timeout
                worker(d.next, state, req.restricted), 5.0)
        except asyncio.TimeoutError:              # degrade, do not hang
            state[d.next] = "TIMEOUT"
        called.append(d.next)
    return {"state": state, "steps": called, "stop_reason": "max steps"}


if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/run", json={"goal": "import speakers"}).json())
    print(c.post("/run", json={"goal": "import speakers", "restricted": True}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Supervisor form | Supervisor node + conditional edges to worker nodes (loop back) | Hierarchical process with a manager agent | Orchestrator agent that calls other agents as tools | Orchestrating agent in a team, or a selector picking the next speaker |
| Worker isolation | Separate nodes/subgraphs | Separate agents | Separate agents | Separate agents |
| Control over order | Explicit | Manager-decided | Orchestrator-decided | Selector-decided |
| Stop conditions | Router + recursion limit | Your guards / max iterations | `max_turns` + your guards | Termination conditions |
| Best for | Auditable multi-step flows | Role-based crews | Agents-as-tools orchestration | Conversational teams |

---

## ⚠️ Common Mistakes
❌ Mistake 1: The supervisor sees every worker's full transcript, so context grows each step.
✅ Correct: Store compact results in state; give workers and the supervisor only what they need.

❌ Mistake 2: No guard against calling the same worker repeatedly.
✅ Correct: Track calls, cap steps, and stop on repeats.

❌ Mistake 3: Supervisor does the work itself and also delegates.
✅ Correct: Keep it to planning and delegation; workers do execution.

❌ Mistake 4: Free-text decisions ("maybe call duty?").
✅ Correct: Enum-constrained decision validated by schema.

---

## 🧠 Tricky Interview Question
Your supervisor system is accurate but the supervisor becomes a bottleneck: every step needs a supervisor LLM call, latency is 6 s, and cost is high. How do you improve it without losing control?

Answer: Not every step needs LLM reasoning. (1) Encode known dependencies as a static graph or plan (classifier then duty), and use the LLM supervisor only for branches that need judgment. (2) Run independent workers in parallel in one supervisor turn. (3) Use a small model for supervisor decisions and a larger one only for the final synthesis. (4) Cache decisions for repeated state patterns. (5) Stream partial results to the user. This turns the supervisor from a per-step LLM into a hybrid: deterministic workflow with an LLM at decision points.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What is a supervisor agent?
A1: A central agent that decides which worker acts next, collects results, and decides when the task is finished.

Q2: (Medium) Supervisor vs router?
A2: A router decides once and hands off. A supervisor stays in control across many steps and can call several workers in sequence or parallel.

Q3: (Hard) What are the failure modes?
A3: Bottleneck and single point of failure, endless delegation loops, context bloat, wrong worker choice early causing cascading errors, and cost from per-step LLM calls. Mitigate with step caps, compact state, validation of decisions and a hybrid static plan.

Q4: (Hard) Flat supervisor vs hierarchical supervisors?
A4: Flat: one supervisor with all workers, simple but crowded when there are many. Hierarchical: top supervisor delegates to team supervisors (research team, tariff team); each has few workers and a small prompt, but adds latency and complexity.

Q5: (System Design) Design a supervisor system for tariff, compliance and shipping cost with audit requirements.
A5: Supervisor with typed state and an enum decision; every decision and worker call is logged with inputs and outputs for audit; checkpoint state after each step for resume; per-worker timeouts and retries; early exit on legal blocks; human-in-the-loop approval before any irreversible action; budget limits for steps and tokens.

---

## 💰 Cost Impact
- Token formula (approximate): `total ≈ Σ over steps (supervisor_prompt + state) + Σ worker calls`. Supervisor prompt grows as state grows, so cost is superlinear if you do not compact state.
- Tips: small model for decisions, compact state summaries, static plan for fixed dependencies, parallel independent workers, cap steps, cache.
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Tasks need several different specialists in a dynamic order
- You need central logging, budgets and stop conditions
- Order depends on intermediate results

❌ Avoid when:
- The steps are fixed (use a pipeline, note 192)
- A single decision is enough (use a router, note 186)
- Latency budget cannot afford per-step LLM decisions

---

## 📊 Visual Diagram
```
                  +----------------+
   goal --------> |   Supervisor   | <----------------------+
                  +----------------+                        |
                   |      |      |   next = worker          | result
                   v      v      v                          |
             +--------+ +------+ +-----------+              |
             |Classify| | Duty | | Compliance|--------------+
             +--------+ +------+ +-----------+
                   next = FINISH  --> final answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Supervisor | Central coordinator | पर्यवेक्षक |
| Worker | Specialist doing a task | कार्यकर्ता agent |
| Delegation | Handing a subtask over | कार्य सौंपना |
| Shared state | Data all steps read/write | साझा state |
| FINISH | Stop signal | समाप्ति संकेत |
| Hierarchical | Supervisors of supervisors | स्तरीय संरचना |

---

## ⚡ 3-Line Summary
English: A supervisor owns the goal, picks the next worker each turn, and decides when to finish.
Workers talk only through it, giving one place for control, logging and budgets.
Guard with step caps and compact state; use static plans where steps are fixed.

Hindi: Supervisor लक्ष्य का मालिक है, हर बार अगला worker चुनता है और तय करता है कब रुकना है।
Workers सिर्फ़ उसी के ज़रिए बात करते हैं, इसलिए control, logging और budget एक जगह रहते हैं।
Step cap और compact state लगाओ; जहाँ steps तय हैं वहाँ static plan रखो।

---

## ➡️ Next Topic
188. Swarm Pattern (Deep): remove the central boss; agents hand work to each other directly.

---
