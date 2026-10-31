---

# 315. Agent Best Practices
# हिंदी में: Agent Best Practices (सर्वोत्तम तरीके)

---

## 🔵 Simple Definition (English)
Agent best practices are proven rules for building agents that are reliable, cheap and safe: start simple, write clear tools, bound loops, validate everything, trace and evaluate, and add humans for risky steps. The goal is predictable behaviour, not maximum autonomy.

## 🔵 सरल परिभाषा (Hindi)
Agent best practices वे आज़माए हुए नियम हैं जिनसे agent भरोसेमंद, सस्ता और सुरक्षित बनता है: सरल से शुरू करो, tools साफ़ लिखो, loops सीमित रखो, सब validate करो, trace और evaluate करो, और risky steps में इंसान रखो। लक्ष्य अनुमानित व्यवहार है, अधिकतम autonomy नहीं।

---

## 🔴 Problem it Solves
Teams often build a big autonomous agent first, then discover it is slow, costly, flaky and hard to debug. Each extra step multiplies failure risk and cost. Best practices prevent over-engineering and give a path from prototype to production.

## 🔴 यह क्यों बना? (Hindi)
Teams पहले बड़ा autonomous agent बनाती हैं, फिर पता चलता है कि वह धीमा, महँगा, अस्थिर और debug करने में कठिन है। हर अतिरिक्त step failure और cost बढ़ाता है। Best practices over-engineering रोकते हैं और prototype से production तक का रास्ता देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start with the simplest thing: one prompt → chain → workflow → agent
Step 2 → Use an agent only when the path is truly unknown in advance
Step 3 → Design few, clear tools (good names, descriptions, typed params)
Step 4 → Bound everything: max_steps, token budget, timeouts, retries
Step 5 → Validate outputs with schemas; return errors to the model as text
Step 6 → Add memory only as needed (trim + summarise)
Step 7 → Security: least privilege, untrusted data handling, approval for risk
Step 8 → Observe (traces, cost) and evaluate (golden set) before each release
Step 9 → Ship gradually: shadow mode → human review → partial automation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → सबसे सरल से शुरू: prompt → chain → workflow → agent
Step 2 → Agent तभी जब रास्ता पहले से पता न हो
Step 3 → कम और साफ़ tools (अच्छे नाम, description, typed params)
Step 4 → सब सीमित: max_steps, token budget, timeout, retries
Step 5 → Schema से output validate; errors model को text में लौटाओ
Step 6 → Memory ज़रूरत भर (trim + summary)
Step 7 → Security: least privilege, untrusted data, risky पर approval
Step 8 → हर release से पहले trace/cost देखो और golden set से evaluate करो
Step 9 → धीरे-धीरे ship: shadow mode → human review → आंशिक automation
```

---

## 🟡 Real World Example
**Tariff Classification System**: Version 1 was a single prompt with RAG (fast, 82% accurate). The team added a fixed LangGraph workflow: retrieve, classify, validate format, look up duty. Only items with confidence below 0.8 go to a free-form agent with 3 tools, and then to a human broker. Result: 94% accuracy, an average of 2.3 LLM calls, and most requests never touch the expensive agent.

**Zomato-style**: simple intents (order status) use a fixed flow; only unusual complaints use an agent.

## 🟡 Real Example Hindi mein
**Tariff System**: Version 1 एक prompt + RAG था (तेज़, 82% सही)। फिर fixed LangGraph workflow जोड़ा: retrieve, classify, format validate, duty lookup। सिर्फ 0.8 से कम confidence वाले items 3 tools वाले free agent और फिर human broker तक जाते हैं। नतीजा: 94% accuracy, औसत 2.3 LLM calls, और ज़्यादातर requests महँगे agent तक पहुँचती ही नहीं।
**Zomato**: सरल intents (order status) fixed flow से; असामान्य शिकायतों पर ही agent।

---

## 💻 Code Example — Basic
```python
# Basic: a checklist-driven "agent config" that enforces limits (offline).
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AgentConfig:
    max_steps: int = 6                         # hard step cap
    max_tokens: int = 20_000                   # total token budget per request
    timeout_s: float = 30.0                    # wall-clock limit
    allowed_tools: tuple[str, ...] = ("search_hs_code", "get_duty_rate")   # small toolset
    require_approval: tuple[str, ...] = ("submit_filing",)                  # risky tools

def preflight(cfg: AgentConfig) -> list[str]:
    problems: list[str] = []                   # collect issues
    if cfg.max_steps > 10:
        problems.append("max_steps too high; agents rarely need >10")
    if cfg.max_tokens > 200_000:
        problems.append("token budget too high")
    if len(cfg.allowed_tools) > 10:
        problems.append("too many tools; route or split agents")
    if "submit_filing" not in cfg.require_approval:
        problems.append("irreversible action without approval")
    return problems

if __name__ == "__main__":
    print(preflight(AgentConfig()) or "config OK")
    print(preflight(AgentConfig(max_steps=50, require_approval=())))
```

## 💻 Code Example — Advanced
```python
# Production skeleton: router -> cheap path -> agent fallback, with budget, timeout, validation, tracing.
import asyncio
import logging
import time
from typing import Any, Awaitable, Callable
from pydantic import BaseModel, Field, ValidationError

log = logging.getLogger("agent")

class Answer(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")
    confidence: float = Field(ge=0, le=1)
    source: str                                   # "workflow" | "agent" | "human"

class BudgetError(Exception):
    pass

class Budget:
    def __init__(self, tokens: int, steps: int) -> None:
        self.tokens_left, self.steps_left = tokens, steps
    def spend(self, tokens: int) -> None:
        self.tokens_left -= tokens
        self.steps_left -= 1
        if self.tokens_left < 0 or self.steps_left < 0:
            raise BudgetError("budget exhausted")

Step = Callable[[str, Budget], Awaitable[dict[str, Any]]]

async def classify(product: str, workflow: Step, agent: Step, threshold: float = 0.8,
                   timeout: float = 30.0) -> Answer:
    budget = Budget(tokens=20_000, steps=8)         # per-request limits
    start = time.perf_counter()
    try:
        async with asyncio.timeout(timeout):         # Python 3.11+: overall deadline
            raw = await workflow(product, budget)    # 1) cheap deterministic path first
            if raw["confidence"] < threshold:        # 2) escalate only when unsure
                raw = await agent(product, budget)
            ans = Answer(**raw)                      # 3) validate output contract
            if ans.confidence < threshold:           # 4) still unsure -> human queue
                ans.source = "human"
            return ans
    except (TimeoutError, BudgetError, ValidationError) as exc:
        log.warning("degrading: %r", exc)            # 5) safe failure
        return Answer(hs_code="0000.00", confidence=0.0, source="human")
    finally:
        log.info("done in %.0f ms, tokens_left=%d", (time.perf_counter() - start) * 1000, budget.tokens_left)

async def wf(p: str, b: Budget) -> dict[str, Any]:
    b.spend(500)
    return {"hs_code": "8518.22", "confidence": 0.6, "source": "workflow"}

async def ag(p: str, b: Budget) -> dict[str, Any]:
    b.spend(3000)
    return {"hs_code": "8518.22", "confidence": 0.92, "source": "agent"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(asyncio.run(classify("bluetooth speaker", wf, ag)))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

app = FastAPI()

class Req(BaseModel):
    product: str = Field(min_length=2, max_length=300)

@app.post("/classify", response_model=Answer)
async def classify_route(req: Req, idempotency_key: str | None = Header(default=None)) -> Answer:
    # Best practices at the edge: validated input, idempotency key, bounded work, typed output.
    try:
        return await classify(req.product, wf, ag)   # from Advanced
    except Exception:
        log.exception("classify failed")
        raise HTTPException(503, "temporarily unavailable")   # no internal details to client

@app.get("/healthz")
async def health() -> dict:
    return {"ok": True}                               # liveness for orchestrators
```

---

## 🔗 LangChain / LangGraph Connection
Use LangGraph for the "workflow first, agent when needed" pattern: explicit nodes and conditional edges, a checkpointer, a recursion limit and `interrupt` for approval.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    product: str
    confidence: float
    code: str

def workflow(s: S) -> S:
    return {"code": "8518.22", "confidence": 0.6}

def agent(s: S) -> S:
    return {"code": "8518.22", "confidence": 0.92}

def route(s: S) -> str:
    return "agent" if s["confidence"] < 0.8 else END      # escalate only when unsure

g = StateGraph(S)
g.add_node("workflow", workflow); g.add_node("agent", agent)
g.add_edge(START, "workflow")
g.add_conditional_edges("workflow", route)
g.add_edge("agent", END)
app_graph = g.compile()
print(app_graph.invoke({"product": "speaker", "confidence": 0.0, "code": ""}, {"recursion_limit": 10}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using an agent for a fixed process.
✅ Correct: use a workflow; it is cheaper, faster and testable.

```python
# Wrong: agent decides to "search then lookup" every single time
# Right: deterministic pipeline
code = search(product); duty = lookup(code)
```

❌ Mistake 2: Vague tools with overlapping purposes ("search", "find", "lookup").
✅ Correct: few tools with clear names, descriptions, examples and typed params.

❌ Mistake 3: Shipping without evals and traces.
✅ Correct: golden set, CI gate, trace ids, cost dashboards.

❌ Mistake 4: Unlimited loops and tokens.
✅ Correct: step, token and time budgets with graceful degradation.

---

## 🧠 Tricky Interview Question
**Q**: "Your manager wants a fully autonomous agent for customs filing. What do you recommend?"

**Answer**: Build in stages. Start with a deterministic workflow and RAG, measure accuracy on a golden set. Add an agent only for the uncertain slice. Keep a human approval step for the irreversible filing, at least until measured error rate and its cost are below an agreed threshold. Autonomy should be earned by metrics, not assumed. State the trade-off: fewer humans means higher speed but higher risk, so tie the decision to numbers (accuracy, cost per error, review time).

---

## ⚫ Interview Questions + Answers

Q1: When should you use an agent instead of a workflow?
A1: When the number and order of steps depends on the input and cannot be written down in advance. Otherwise use a workflow.

Q2: Name three tool design tips.
A2: Clear name and description, typed parameters with constraints, and readable error messages. Keep the toolset small and return concise outputs.

Q3: What limits should every agent have?
A3: Max steps, token budget, timeouts, retry caps, rate limits and a safe fallback.

Q4: How do you reduce agent cost?
A4: Route simple cases to cheaper models or workflows, cache, trim memory, shorten tool outputs, use prompt caching, and cap steps.

Q5: (Hard) How do you roll out an agent safely?
A5: Offline evals first, then shadow mode (agent runs, humans decide), then human-approves-all, then auto for high-confidence cases with sampling audits. Monitor traces, cost, error and feedback; keep a kill switch and rollback; version prompts and tools.

---

## 🔷 When to Use + When Not to Use
✅ Use an agent when:
- Steps depend on intermediate results
- Many possible tools and unpredictable questions
- Errors are recoverable or reviewable

❌ Avoid an agent when:
- A fixed pipeline solves it
- Latency or cost is tight
- Actions are irreversible without review

---

## 📊 Visual Diagram
```
Complexity ladder (climb only when needed)

 1. Single prompt  ──►  2. Prompt + RAG  ──►  3. Chain/Workflow (LangGraph)
                                                    │ uncertain cases
                                                    ▼
                                           4. Agent (few tools, bounded)
                                                    │ risky / low confidence
                                                    ▼
                                           5. Human approval

 Around all levels: validation · budgets · tracing · evals · security
```

---

## 💰 Cost Impact
Each extra LLM step adds roughly the full prompt again. A 5-step agent can cost 5-10x a single call and take 5x longer. Best-practice routing (workflow for 80% of traffic, agent for the hard 20%) often cuts average cost by more than half. Use small models for routing and extraction, a larger one only for hard reasoning, enable prompt caching for long static prompts, and track cost per successful task, not per call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | Fixed, coded steps | तय क्रम के steps |
| Agent | LLM picks next step | LLM अगला step चुनता है |
| Budget | Limit on tokens/steps/time | tokens/steps/समय की सीमा |
| Shadow mode | Run silently, compare with humans | चुपचाप चलाकर तुलना |
| Kill switch | Instant off button | तुरंत बंद करने का बटन |
| Graceful degradation | Safe reduced behaviour on failure | विफलता पर सुरक्षित सीमित व्यवहार |

---

## ⚡ 3-Line Summary
English: Start simple, use agents only for unpredictable paths, and keep tools few and clear. Bound loops, validate outputs, secure tools, trace and evaluate before release. Roll out gradually with humans on risky steps.
Hindi: सरल से शुरू करो, agent सिर्फ अनिश्चित रास्तों के लिए और tools कम व साफ़ रखो। Loops सीमित करो, output validate करो, tools सुरक्षित रखो, release से पहले trace और evaluate करो। धीरे-धीरे rollout करो और risky steps में इंसान रखो।

---

## ➡️ Next Topic
**316. LangGraph — What + Why** — the framework that makes the "workflow plus agent" pattern explicit and controllable.
