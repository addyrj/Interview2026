---

# 365. Multi-Agent Best Practices
# हिंदी में: Multi-Agent Best Practices

---

## 🔵 Simple Definition (English)
Multi-agent best practices are the rules that make agent teams **reliable, affordable and debuggable**: start simple, give each agent one clear job, use typed shared state, limit loops, scope tools, validate with code, keep humans in high-risk steps, trace everything, and evaluate before shipping.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent best practices वे नियम हैं जो agent teams को **भरोसेमंद, किफ़ायती और debug करने योग्य** बनाते हैं: सरल से शुरू करो, हर agent को एक साफ़ काम दो, typed shared state इस्तेमाल करो, loops सीमित रखो, tools का दायरा तय करो, code से validate करो, जोखिम वाले steps में human रखो, सब कुछ trace करो और ship करने से पहले evaluate करो।

---

## 🔴 Problem it Solves
Teams of agents are easy to demo and hard to run in production. Typical failures: too many agents for a simple task, endless chatter, runaway cost, hidden errors passed from agent to agent, unclear ownership, and no way to know what went wrong. Best practices turn a fragile demo into a dependable service.

## 🔴 यह क्यों बना? (Hindi)
Agent teams का demo आसान है, production में चलाना कठिन। आम विफलताएँ: सरल task के लिए बहुत सारे agents, अंतहीन बातचीत, बेकाबू cost, agent से agent तक फैलती छिपी गलतियाँ, अस्पष्ट ज़िम्मेदारी और गड़बड़ी समझने का कोई तरीका नहीं। Best practices नाज़ुक demo को भरोसेमंद service बनाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prove a single agent (or a plain chain) is not enough first
Step 2 → Split by responsibility: one job, one prompt, one toolset per agent
Step 3 → Choose the simplest topology: pipeline > supervisor > network
Step 4 → Use typed shared state with reducers; pass fields, not transcripts
Step 5 → Bound everything: max steps, retries, tokens, time
Step 6 → Add deterministic validators and human approval for risky actions
Step 7 → Trace each run (ids, tokens, latency per agent); log decisions
Step 8 → Evaluate on a golden set, then roll out gradually and monitor
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले साबित करो कि अकेला agent (या सादी chain) काफ़ी नहीं है
Step 2 → ज़िम्मेदारी से बाँटो: एक काम, एक prompt, एक toolset प्रति agent
Step 3 → सबसे सरल topology चुनो: pipeline > supervisor > network
Step 4 → Reducers वाली typed shared state; transcripts नहीं, fields पास करो
Step 5 → सब कुछ सीमित करो: max steps, retries, tokens, समय
Step 6 → Deterministic validators और जोखिम वाली actions पर human approval
Step 7 → हर run trace करो (ids, tokens, प्रति agent latency); फैसले log करो
Step 8 → Golden set पर evaluate करो, फिर धीरे-धीरे rollout और निगरानी
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team started with 6 agents. After evaluation, two were merged (the "reader" and "extractor") and the "summariser" was replaced by a template. Result: 3 agents (Classifier, Validator-as-code, Reporter), accuracy unchanged, cost down 55 percent, p95 latency down from 22 s to 9 s. High-duty shipments always pass through a human approval node. Every run has a trace id linking all agent calls.

**Zomato-style**: Instead of one agent per micro-task, group "search + rank" in one agent, keep "payment" separate and permission-gated.

## 🟡 Real Example Hindi mein
**Tariff System**: Team 6 agents से शुरू हुई। Evaluation के बाद दो मिला दिए गए ("reader" और "extractor") और "summariser" की जगह template आ गया। नतीजा: 3 agents (Classifier, code के रूप में Validator, Reporter), accuracy वही, cost 55 प्रतिशत कम, p95 latency 22 s से 9 s। ज़्यादा duty वाली shipments हमेशा human approval node से गुज़रती हैं। हर run का trace id सभी agent calls को जोड़ता है।

**Zomato-style**: हर छोटे काम के लिए अलग agent की जगह "search + rank" एक agent में रखो, "payment" को अलग और permission-gated रखो।

---

## 💻 Code Example — Basic
```python
# A tiny "guardrail runner" that enforces budgets for any agent pipeline (runs offline)
from dataclasses import dataclass, field  # state container
from typing import Callable  # function type

@dataclass
class Budget:
    max_steps: int = 6        # hard cap on agent steps
    max_tokens: int = 8000    # hard cap on total tokens

@dataclass
class RunState:
    data: dict[str, object] = field(default_factory=dict)  # shared typed-ish state
    steps: int = 0                                         # steps used
    tokens: int = 0                                        # tokens used
    trace: list[str] = field(default_factory=list)         # audit trail

# An agent is a function: state -> (partial update, tokens used)
Agent = Callable[[RunState], tuple[dict[str, object], int]]

def run_pipeline(agents: list[tuple[str, Agent]], budget: Budget) -> RunState:
    st = RunState()
    for name, agent in agents:
        if st.steps >= budget.max_steps:                 # step guard
            st.trace.append("STOP: max_steps"); break
        update, used = agent(st)                         # run one agent
        st.steps += 1
        st.tokens += used
        st.data.update(update)                           # merge partial update
        st.trace.append(f"{name}: +{used} tokens")       # log
        if st.tokens > budget.max_tokens:                # token guard
            st.trace.append("STOP: max_tokens"); break
    return st

def classifier(s: RunState) -> tuple[dict[str, object], int]: return {"hs_code": "8518.30"}, 900
def validator(s: RunState) -> tuple[dict[str, object], int]: return {"valid": s.data["hs_code"] in {"8518.30"}}, 0  # code, no tokens
def reporter(s: RunState) -> tuple[dict[str, object], int]: return {"report": f"HS {s.data['hs_code']} valid={s.data['valid']}"}, 300

if __name__ == "__main__":
    out = run_pipeline([("classifier", classifier), ("validator", validator), ("reporter", reporter)], Budget())
    print(out.data); print(out.trace)
```

## 💻 Code Example — Advanced
```python
# Async pipeline with timeouts, retries, circuit breaker, human gate and trace ids
import asyncio  # async runtime
import uuid  # trace ids

class CircuitOpen(Exception):
    pass

class Breaker:
    """Stops calling a failing agent after N consecutive errors."""
    def __init__(self, limit: int = 3) -> None:
        self.fails, self.limit = 0, limit
    def check(self) -> None:
        if self.fails >= self.limit:
            raise CircuitOpen("too many failures")
    def ok(self) -> None: self.fails = 0
    def bad(self) -> None: self.fails += 1

async def call_agent(name: str, fn, state: dict, breaker: Breaker, timeout: float = 20, retries: int = 2) -> dict:
    breaker.check()  # fail fast when the dependency is down
    for i in range(retries + 1):
        try:
            res = await asyncio.wait_for(fn(state), timeout)  # per-agent timeout
            breaker.ok()
            return res
        except asyncio.TimeoutError:
            breaker.bad()
            await asyncio.sleep(0.05 * 2 ** i)  # exponential backoff
    raise TimeoutError(f"{name} timed out")

async def classifier(s: dict) -> dict:
    await asyncio.sleep(0); return {"hs_code": "8518.30", "confidence": 0.7}

async def run(description: str) -> dict:
    trace_id = str(uuid.uuid4())  # one id across all calls
    state: dict = {"description": description, "trace_id": trace_id}
    breaker = Breaker()
    try:
        state.update(await call_agent("classifier", classifier, state, breaker))
        state["needs_human"] = state["confidence"] < 0.85  # human gate
    except (CircuitOpen, TimeoutError) as exc:
        state["error"] = str(exc); state["needs_human"] = True  # fail safe, not fail silent
    return state

if __name__ == "__main__":
    print(asyncio.run(run("headphones")))
```

---

## 🟠 FastAPI Integration
Make the API return trace id, cost and a "needs_human" flag. Apply a global timeout and request-level limits.

```python
import asyncio  # timeout
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # models

app = FastAPI()

class In(BaseModel):
    description: str = Field(min_length=3, max_length=2000)  # validate input size to cap tokens

@app.post("/classify")
async def classify(body: In) -> dict:
    try:
        state = await asyncio.wait_for(run(body.description), timeout=45)  # whole-run timeout
    except asyncio.TimeoutError:
        raise HTTPException(504, "agent team timed out")
    return {"trace_id": state["trace_id"], "hs_code": state.get("hs_code"), "needs_human": state["needs_human"]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langgraph.graph import StateGraph, START, END  # graph
from langgraph.checkpoint.memory import MemorySaver  # swap for a DB saver in production

# Best practices expressed in LangGraph:
# 1. typed state + reducers      -> TypedDict with Annotated fields
# 2. bounded loops               -> recursion_limit in config
# 3. human gate                  -> interrupt() in a node
# 4. durability and resume       -> checkpointer + thread_id
# 5. tracing                     -> LangSmith (LANGSMITH_TRACING=true) tags every node call

graph = builder.compile(checkpointer=MemorySaver())  # builder defined as in earlier topics
result = graph.invoke(
    {"description": "headphones"},
    config={"configurable": {"thread_id": "shipment-42"}, "recursion_limit": 15, "tags": ["tariff", "v2"]},
)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Too many agents for a simple task
✅ Correct: start with one agent or a chain; split only when evaluation proves the benefit.

```python
# Wrong: 6 agents to classify one product, each re-reading the full context
# Right: 1 classifier + a deterministic validator + a template report
```

❌ Mistake 2: Trusting agent output without validation
✅ Correct: schema checks, tariff-table lookups, human approval for high risk.

```python
# Wrong
file_declaration(agent_output)
# Right
if validate(agent_output) and not needs_human(agent_output):
    file_declaration(agent_output)
```

---

## 🧠 Tricky Interview Question
**Q**: "Leadership wants 'more agents for more intelligence'. How do you respond?"

**Answer**: More agents add cost, latency, and failure surface (each hand-off can lose information). Intelligence comes from better context, tools and evaluation, not agent count. Show a benchmark: baseline single agent vs team, with accuracy, cost and p95. Add agents only for clear reasons: different tools or permissions, parallelism, independent verification, or separate context windows.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] When should you not use multiple agents?
A1: When a single prompt, chain or tool-using agent already meets quality. Extra agents add cost and failure points.

Q2: [Easy] Why trace every run?
A2: To debug failures, attribute cost, audit decisions and build evaluation datasets from real traffic.

Q3: [Medium] How do you keep costs under control?
A3: Cheap models for simple agents, minimal context per agent, step and token budgets, caching, deterministic code instead of LLM where possible.

Q4: [Medium] How do you make agent teams safe?
A4: Least-privilege tools, validators, human approval for risky actions, idempotent writes, prompt-injection defences, and audit logs.

Q5: [Hard] How do you roll out a new multi-agent version?
A5: Offline eval on a golden set, shadow mode on live traffic, canary to a small percent, compare metrics (accuracy, escalation rate, cost, latency), automatic rollback, and continuous sampling for human review.

---

## 🔷 When to Use + When Not to Use
✅ Use these practices when:
- Any agent system moves toward production
- Multiple teams edit prompts and tools

❌ Avoid over-engineering when:
- A weekend prototype or one-off script

---

## 📊 Visual Diagram
```
  Request -> [Input validation + budget]
                  |
        +---------v----------+      trace_id on every call
        |  Supervisor/Graph  |----------------------------+
        +----+-----+-----+---+                            |
             v     v     v                                v
        [Agent][Agent][Agent]  <- one job, own tools  [Tracing / Eval]
             \     |     /
        typed shared state + reducers
                  |
        [Deterministic validator] --fail--> [Human approval]
                  |ok
               Response (answer, cost, needs_human)
```

---

## 💰 Cost Impact
- Cost scales with agents x turns x context size. Each unnecessary agent adds a full prompt.
- Typical savings from the practices: merge agents (30-50 percent), field-based context (up to 80 percent of input tokens), cheap models for easy steps (10-30x per call), validators in code (zero tokens).
- Set per-run budgets and alert when the p95 cost per run rises.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Topology | How agents are connected | Agents के जुड़ने का ढाँचा |
| Circuit breaker | Stops calls to a failing part | विफल हिस्से को बुलाना रोकना |
| Guardrail | Rule that limits behaviour | व्यवहार सीमित करने वाला नियम |
| Shadow mode | Run new version silently beside old | नया version चुपचाप पुराने के साथ चलाना |
| Canary | Small-traffic rollout | थोड़े traffic पर rollout |
| Trace id | Id linking all calls of one run | एक run की सभी calls जोड़ने वाली id |

---

## ⚡ 3-Line Summary
English: Start simple, give agents single responsibilities, share typed state, and bound steps, tokens and time. Validate in code, gate risky actions with humans, trace everything and evaluate before rollout. More agents is not more intelligence.
Hindi: सरल से शुरू करो, agents को एक-एक ज़िम्मेदारी दो, typed state शेयर करो और steps, tokens व समय सीमित रखो। Code से validate करो, जोखिम वाली actions पर human रखो, सब कुछ trace करो और rollout से पहले evaluate करो। ज़्यादा agents का मतलब ज़्यादा बुद्धिमानी नहीं है।

---

## ➡️ Next Topic
**366. Memory in AI Apps — Types** — moving from agent teams to how AI apps remember in general.
