---

# 583. Build Multi-Agent System
# हिंदी में: Multi-Agent System बनाना

---

## 🔵 Simple Definition (English)
A multi-agent system splits a job between specialised agents (classifier, duty calculator, compliance checker). A supervisor decides who runs next, passes results through shared state, and combines the output. Each agent has a small prompt, few tools and one clear responsibility.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent system काम को specialised agents (classifier, duty calculator, compliance checker) में बाँटता है। Supervisor तय करता है कौन अगला चलेगा, शेयर्ड state से results आगे देता है और अंत में output जोड़ता है। हर agent का prompt छोटा, tools कम और ज़िम्मेदारी एक होती है।

---

## 🔴 Problem it Solves
One giant agent with 30 tools and a 3,000-token prompt gets confused, picks wrong tools and is hard to test. Splitting by role improves accuracy, lets you use different models per role, and allows independent agents to run in parallel.

## 🔴 यह क्यों बना? (Hindi)
30 tools और 3,000-token prompt वाला एक बड़ा agent confuse होता है, गलत tools चुनता है और test करना कठिन है। Role के हिसाब से बाँटने से accuracy बढ़ती है, हर role पर अलग model चल सकता है और independent agents parallel चल सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define agents with one job each + their prerequisites
Step 2 → Create shared state (blackboard): request, results, log
Step 3 → Supervisor finds agents whose prerequisites are satisfied
Step 4 → Run ready agents in parallel (asyncio.gather)
Step 5 → Merge results into state; isolate failures per agent
Step 6 → Repeat until nothing is ready or max_rounds
Step 7 → Return combined results (+ log for tracing)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर agent का एक काम और उसकी prerequisites तय करो
Step 2 → Shared state बनाओ: request, results, log
Step 3 → Supervisor वे agents ढूँढता है जिनकी prerequisites पूरी हैं
Step 4 → Ready agents parallel चलाओ (asyncio.gather)
Step 5 → Results state में merge करो; failure को अलग रखो
Step 6 → कुछ ready न हो या max_rounds तक दोहराओ
Step 7 → जोड़ा हुआ result लौटाओ (+ tracing के लिए log)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Classifier gives the HS code. Then Duty agent and Compliance agent run in parallel because both only need the code (see the two rounds in `main.py`). The supervisor returns `{hs_code, duty_usd, needs_license}`. **Zomato-style**: menu agent, delivery-time agent and offers agent answer in parallel. **Amazon-style**: pricing, inventory and shipping agents behind one assistant.

## 🟡 Real Example Hindi mein
**Tariff System**: Classifier HS code देता है। फिर Duty agent और Compliance agent parallel चलते हैं क्योंकि दोनों को सिर्फ code चाहिए (`main.py` में दो rounds)। Supervisor `{hs_code, duty_usd, needs_license}` लौटाता है। **Zomato**: menu, delivery-time और offers agents parallel जवाब देते हैं। **Amazon**: pricing, inventory, shipping agents एक assistant के पीछे।

---

## 💻 Code Example — Basic
Full solution: `main.py` (prerequisite-driven supervisor, three async workers).

```python
import asyncio  # async runtime

async def classifier(state: dict) -> None:  # worker 1
    state["hs"] = "8517.13"  # write result into shared state

async def duty(state: dict) -> None:  # worker 2 needs hs
    state["duty"] = 200.0 if state["hs"] == "8517.13" else 0.0  # compute

async def main() -> None:  # tiny supervisor
    state: dict = {}  # shared state
    await classifier(state)  # step 1
    await duty(state)  # step 2 depends on step 1
    print(state)  # {'hs': '8517.13', 'duty': 200.0}

asyncio.run(main())  # run
```

## 💻 Code Example — Advanced
`main.py` runs ready agents with `asyncio.gather(..., return_exceptions=True)` so one failing worker does not crash the others, records a log per round, and bounds rounds. With an LLM supervisor (illustrative):

```python
# LLM supervisor picks next agent via structured output (illustrative, mocked here)
from typing import Literal
from pydantic import BaseModel

class Route(BaseModel):  # structured routing decision
    next: Literal["classifier", "duty", "compliance", "FINISH"]  # allowed values only

def supervisor(state: dict, llm_route) -> str:  # llm_route: callable returning Route
    decision: Route = llm_route(state)  # model chooses next worker
    return decision.next  # validated enum prevents invented agent names

print(supervisor({}, lambda s: Route(next="classifier")))  # classifier
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel
from main import supervisor  # coroutine from main.py

app = FastAPI()  # app

class In(BaseModel):  # request
    product: str  # product text
    value_usd: float  # declared value

@app.post("/assess")  # route
async def assess(body: In) -> dict:  # handler
    state = await supervisor(body.model_dump())  # run agents
    return {"results": state.results, "trace": state.log}  # include trace
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph supports multi-agent via supervisor graphs (a router node plus worker nodes), handoffs between agents (`Command(goto=...)`), and subgraphs. The `langgraph-supervisor` package offers a ready-made helper (check current docs). Each worker can itself be a `create_react_agent`.

```python
# Illustrative shape only
# supervisor_node -> conditional edge -> [classifier_node | duty_node | compliance_node] -> back to supervisor
print("workers return to the supervisor; supervisor returns FINISH to end")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Splitting into agents when one prompt suffices
✅ Correct: Start with one agent or a pipeline; split only when accuracy or tooling demands it.

```python
# Wrong: 5 agents for a one-step lookup (5x latency and cost)
agents = ["a", "b", "c", "d", "e"]
# Right: one function
def lookup(p: str) -> str:
    return "8517.13"
```

❌ Mistake 2: Agents talking forever
✅ Correct: Cap rounds and detect repeats.

```python
# Wrong
# while True: supervisor.step()
# Right
for round_no in range(5):
    pass
```

---

## 🧠 Tricky Interview Question
**Q**: "Your multi-agent system is 4x slower and 3x costlier than the single agent, with no accuracy gain. What went wrong?"

**Answer**: Coordination overhead: every handoff re-sends context, the supervisor LLM adds calls, and agents were chained sequentially though independent. Fix: run independent agents in parallel, pass only the needed state, use rules (not an LLM) for obvious routing, use smaller models for workers, and benchmark single-agent vs multi-agent on a golden set before adopting the complexity.

---

## ⚫ Interview Questions + Answers

Q1: What is a supervisor agent? (Easy)
A1: A coordinator that routes tasks to worker agents and decides when the job is done.

Q2: Why give each agent few tools? (Easy)
A2: Fewer choices means better tool selection, shorter prompts and easier testing.

Q3: Shared state vs message passing? (Medium)
A3: Shared state (blackboard) is simple and auditable; message passing isolates agents and suits distributed systems but needs protocol design.

Q4: How do you handle a failed worker? (Medium)
A4: Isolate errors (`return_exceptions=True`), retry with backoff, fall back to a default or a human, and mark the result partial rather than failing everything.

Q5: How do you evaluate a multi-agent system? (Hard)
A5: Evaluate end-to-end on a golden set, then per agent (unit tests with fixed inputs), track trajectory metrics (steps, tool errors), cost and latency per request, and run ablations (single vs multi-agent) to prove the split helps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Distinct skills, tools or models per subtask
- Independent subtasks can run in parallel

❌ Avoid when:
- Task is simple or strictly sequential
- You cannot trace and test each agent

---

## 📊 Visual Diagram
```
            ┌────────────┐
 request ──►│ Supervisor │◄──────────────┐
            └─────┬──────┘               │
        ready?    │                      │ results
     ┌────────────┼────────────┐         │
     ▼            ▼            ▼         │
 Classifier     Duty      Compliance ────┘
 (HS code)   (needs HS)   (needs HS)
        shared state: request + results + log
```

---

## 💰 Cost Impact
Each agent call and each supervisor decision costs tokens, and handoffs repeat context. Example (illustrative): supervisor 400 + three workers of 600 each is about 2,200 tokens versus 900 for a single focused call. Optimise: rule-based routing, parallel workers, trimmed context per agent, cheap models for simple roles, caching deterministic agents.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Supervisor | Routes work | काम बाँटने वाला |
| Worker agent | Specialised agent | विशेष agent |
| Blackboard | Shared state | साझा state |
| Handoff | Pass control | नियंत्रण सौंपना |
| Fan-out | Run in parallel | एक साथ चलाना |
| Trajectory | Sequence of steps | Steps का क्रम |

---

## ⚡ 3-Line Summary
English: Split work into small specialised agents coordinated by a supervisor. Run independent agents in parallel and isolate failures. Prove the split beats a single agent before keeping it.
Hindi: काम को छोटे specialised agents में बाँटो, supervisor समन्वय करे। Independent agents parallel चलाओ और failures अलग रखो। रखने से पहले साबित करो कि split single agent से बेहतर है।

---

## ➡️ Next Topic
**584. Build Document Q&A System** — grounded answers with citations from your own documents.
