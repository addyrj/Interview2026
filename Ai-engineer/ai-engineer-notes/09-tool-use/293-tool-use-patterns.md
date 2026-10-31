---

# 293. Tool Use Patterns
# हिंदी में: Tool Use Patterns (tools इस्तेमाल करने के तरीके)

---

## 🔵 Simple Definition (English)
Tool use patterns are repeatable designs for how an LLM and tools work together: single call, parallel calls, sequential chain, router/dispatcher, human-in-the-loop approval, and agent loop. Picking the right pattern controls cost, speed and reliability.

## 🔵 सरल परिभाषा (Hindi)
Tool use patterns वे दोहराए जाने वाले designs हैं कि LLM और tools साथ कैसे काम करें: single call, parallel calls, sequential chain, router/dispatcher, human approval और agent loop। सही pattern चुनने से cost, speed और reliability तय होती है।

---

## 🔴 Problem it Solves
Beginners put every tool in one agent loop and hope. That causes slow answers (sequential when parallel is possible), high cost (many LLM rounds), and unpredictability (the model chooses a bad order). Named patterns give a vocabulary and a checklist for design reviews.

## 🔴 यह क्यों बना? (Hindi)
नए लोग सारे tools एक agent loop में डालकर उम्मीद करते हैं। नतीजा: धीमे जवाब (parallel हो सकता था पर sequential), ज़्यादा cost (कई LLM rounds), और अनिश्चितता। Named patterns से design review के लिए साझा भाषा और checklist मिलती है।

---

## 🟢 How it Works — Step by Step

```
Pattern 1  SINGLE CALL      user -> LLM -> 1 tool -> LLM -> answer
Pattern 2  PARALLEL CALLS   LLM returns N independent tool_calls -> run with gather -> LLM
Pattern 3  SEQUENTIAL CHAIN output of tool A is input of tool B (fixed order in code)
Pattern 4  ROUTER           cheap classifier picks ONE tool/branch, no loop
Pattern 5  AGENT LOOP       LLM decides next tool each round until done (max N rounds)
Pattern 6  HUMAN APPROVAL   risky tool pauses until a human clicks approve
Pattern 7  TOOL-AS-AGENT    a tool internally runs its own sub-agent/LLM
```

## 🟢 कैसे काम करता है? (Hindi)

```
Pattern 1  SINGLE CALL      user -> LLM -> 1 tool -> LLM -> जवाब
Pattern 2  PARALLEL CALLS   LLM N independent tool_calls देता है -> gather -> LLM
Pattern 3  SEQUENTIAL CHAIN tool A का output tool B का input (code में fixed क्रम)
Pattern 4  ROUTER           सस्ता classifier एक tool/branch चुनता है, loop नहीं
Pattern 5  AGENT LOOP       हर round में LLM अगला tool चुनता है, max N rounds
Pattern 6  HUMAN APPROVAL   risky tool पर इंसान के approve तक रुकना
Pattern 7  TOOL-AS-AGENT    tool अंदर अपना sub-agent/LLM चलाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**:
- Parallel: for a shipment of 3 items, call `get_tariff_rate` three times at once.
- Sequential chain: `get_exchange_rate` -> `calculator` (duty on INR value). The order is fixed, so code it, do not ask the LLM.
- Router: "Is this a classification or a rate question?" decides which pipeline runs.
- Human approval: filing a customs declaration needs a broker's click.

**Zomato AI**: parallel `search_restaurants` + `get_user_preferences`, then sequential `place_order` after user confirms.

## 🟡 Real Example Hindi mein
**Tariff System**: 3 items वाले shipment के लिए तीन `get_tariff_rate` एक साथ (parallel)। `get_exchange_rate` -> `calculator` का क्रम fixed है, इसलिए code में लिखो। Customs declaration file करने से पहले broker का approval ज़रूरी।

**Zomato AI**: `search_restaurants` + `get_user_preferences` parallel; user के confirm के बाद ही `place_order`।

---

## 💻 Code Example — Basic
```python
# Patterns without any LLM: sequential vs parallel vs router (runs offline)
import asyncio                                  # for parallel execution
import time

async def get_rate(hs: str) -> float:
    await asyncio.sleep(0.2)                    # pretend 200 ms API call
    return {"8517.12": 18.0, "6403.99": 25.0, "8471.30": 0.0}.get(hs, 10.0)

async def sequential(codes: list[str]) -> list[float]:
    """Slow: waits for each call."""
    return [await get_rate(c) for c in codes]

async def parallel(codes: list[str]) -> list[float]:
    """Fast: all calls at the same time."""
    return list(await asyncio.gather(*(get_rate(c) for c in codes)))

def router(question: str) -> str:
    """Cheap rule-based router: choose ONE branch without an agent loop."""
    q = question.lower()
    if "rate" in q or "duty" in q:
        return "rate_lookup"
    if "classify" in q or "hs code" in q:
        return "classification"
    return "general_chat"

async def main() -> None:
    codes = ["8517.12", "6403.99", "8471.30"]
    t = time.perf_counter(); await sequential(codes)
    print(f"sequential: {time.perf_counter() - t:.2f}s")     # about 0.6s
    t = time.perf_counter(); await parallel(codes)
    print(f"parallel:   {time.perf_counter() - t:.2f}s")     # about 0.2s
    print(router("What is the duty on phones?"))             # rate_lookup

asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# Production: parallel tool_calls + human-approval gate + hard round cap
import asyncio, json
from typing import Any, Awaitable, Callable
from openai import AsyncOpenAI

client = AsyncOpenAI()
ToolFn = Callable[..., Awaitable[dict[str, Any]]]

async def get_rate(hs_code: str) -> dict[str, Any]:
    return {"ok": True, "hs_code": hs_code, "duty_pct": 18.0}

async def file_declaration(shipment_id: str) -> dict[str, Any]:
    return {"ok": True, "filed": shipment_id}              # irreversible action

READ_TOOLS: dict[str, ToolFn] = {"get_rate": get_rate}
RISKY_TOOLS: dict[str, ToolFn] = {"file_declaration": file_declaration}   # needs approval

async def request_approval(name: str, args: dict[str, Any]) -> bool:
    """Real system: store a pending task, notify a human, await their decision."""
    print(f"APPROVAL NEEDED: {name}({args})")
    return False                                            # default deny in this demo

async def run_one(call: Any) -> dict[str, Any]:
    """Execute a single tool call with the right policy."""
    name = call.function.name
    try:
        args = json.loads(call.function.arguments)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid JSON arguments"}
    if name in READ_TOOLS:
        return await READ_TOOLS[name](**args)
    if name in RISKY_TOOLS:
        if not await request_approval(name, args):          # human-in-the-loop gate
            return {"ok": False, "error": "approval denied or pending"}
        return await RISKY_TOOLS[name](**args)
    return {"ok": False, "error": f"unknown tool {name}"}

async def agent(question: str, tools_schema: list[dict[str, Any]], max_rounds: int = 4) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(max_rounds):                             # agent-loop pattern with a cap
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools_schema,
            parallel_tool_calls=True,                       # allow several calls in one turn
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg)
        results = await asyncio.gather(*(run_one(c) for c in msg.tool_calls))   # parallel pattern
        for call, res in zip(msg.tool_calls, results):
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(res)})
    return "Reached round limit."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()
PENDING: dict[str, dict] = {}                              # demo store; use Redis/DB in production

class Q(BaseModel):
    question: str

@app.post("/agent")
async def run_agent(q: Q) -> dict:
    """Agent-loop pattern behind one endpoint."""
    return {"answer": await agent(q.question, tools_schema=[])}

@app.post("/approvals/{task_id}/approve")
async def approve(task_id: str) -> dict:
    """Human-approval pattern: a separate endpoint resumes the paused action."""
    task = PENDING.pop(task_id, None)
    if not task:
        raise HTTPException(status_code=404, detail="no such task")
    return {"result": await RISKY_TOOLS[task["name"]](**task["args"])}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langgraph.graph import StateGraph, START, END

# Parallel pattern in LCEL:
parallel = RunnableParallel(
    rate=RunnableLambda(lambda x: 18.0),
    fx=RunnableLambda(lambda x: 83.2),
)
print(parallel.invoke("8517.12"))          # {'rate': 18.0, 'fx': 83.2}

# Router / conditional edges in LangGraph:
# graph.add_conditional_edges("router", route_fn, {"rate": "rate_node", "classify": "classify_node"})
# Human approval: compile with a checkpointer and interrupt_before=["file_declaration"]
```
LangGraph is the natural home for these patterns: nodes = steps, conditional edges = routers, `interrupt_before` = human approval, checkpointer = pause/resume.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using an agent loop for a fixed workflow
✅ Correct: Write the sequence in code when the order never changes.

```python
# Wrong — LLM decides order every time (slow, flaky, costly):
agent.run("get rate, convert currency, compute duty")
# Right — deterministic chain, LLM only writes the final text:
rate = await get_rate(hs); fx = await get_fx(); duty = calc(rate, fx)
```

❌ Mistake 2: Running independent calls sequentially
✅ Correct: `asyncio.gather` for parallel tool calls.

```python
# Wrong:
for c in calls: results.append(await run_one(c))
# Right:
results = await asyncio.gather(*(run_one(c) for c in calls))
```

❌ Mistake 3: Letting the model execute irreversible tools (delete, pay, file) without approval.

---

## 🧠 Tricky Interview Question

**Q**: "Parallel tool calls made your latency 3x better, but some answers are now wrong. Why?"

**Answer**: The calls were not actually independent. If call B needs the output of call A (exchange rate before duty calculation), running them together makes the model guess B's arguments. Parallelism is only safe for independent calls. Fix: separate dependent steps into rounds (or code them as a chain), have the model plan dependencies explicitly, and add tests where a step depends on a previous result.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a workflow and an agent? (Easy)
A1: A workflow follows a path defined in code. An agent lets the LLM decide the next step. Use workflows when steps are known; agents when they are not.

Q2: What are parallel tool calls? (Easy)
A2: The model returns several `tool_calls` in one response. You execute them concurrently and send all results back in one go. It saves latency and LLM rounds.

Q3: When would you use a router pattern? (Medium)
A3: When each request needs exactly one specialised path (rates vs classification vs FAQ). A cheap model or rules pick the branch; there is no multi-step loop, so cost and latency are low.

Q4: How do you add human approval to an agent? (Medium)
A4: Mark risky tools; before executing, persist the pending action and notify a human; resume after approval. In LangGraph use a checkpointer with `interrupt_before` on that node.

Q5: Design the tool pattern for "classify 500 items in a shipment". (Hard)
A5: Do not run one giant agent loop. Chunk items, process batches in parallel with a concurrency limit (`asyncio.Semaphore`), use a deterministic per-item pipeline (retrieve candidates, LLM picks, validate), a router for ambiguous items to a stronger model, human review queue for low-confidence results, idempotent writes, and progress tracking via a job id.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single call: one lookup
- Parallel: independent lookups
- Chain in code: fixed multi-step process
- Router: clearly separate request types
- Agent loop: open-ended tasks
- Approval: irreversible or costly actions

❌ Avoid when:
- Agent loop for tasks a script can do
- Parallel for dependent steps
- Any pattern without a round or time limit

---

## 📊 Visual Diagram
```
SINGLE      LLM ─► T ─► LLM
PARALLEL    LLM ─► [T1 | T2 | T3] ─► LLM
CHAIN       T1 ─► T2 ─► T3 ─► LLM (order in code)
ROUTER      Q ─► classifier ─┬─► branch A
                             └─► branch B
AGENT LOOP  LLM ─► T ─► LLM ─► T ─► ... ─► answer (max N)
APPROVAL    LLM ─► [risky T] ─► human ✓ ─► execute
```

---

## 💰 Cost Impact
LLM rounds drive cost, because each round re-sends the growing history. Single/chain/router: 1-2 LLM calls. Agent loop with 5 rounds on a 2K-token context is about 10K+ input tokens. Parallel tool calls cut rounds (3 lookups in 1 round instead of 3).

Optimize: prefer workflows for fixed paths, parallel for independent calls, a small model for routing, round caps, and prompt caching for the static system prompt and tool schemas.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parallel tool calls | Several calls in one model turn | एक साथ कई tool calls |
| Router | Picks one branch | रास्ता चुनने वाला |
| Chain | Fixed sequence of steps | तय क्रम के steps |
| Agent loop | LLM decides each next step | LLM हर बार अगला step चुनता है |
| Human-in-the-loop | Human approves actions | इंसान की मंज़ूरी |
| Semaphore | Limits concurrency | एक साथ चलने की सीमा |

---

## ⚡ 3-Line Summary
English: Choose a tool pattern deliberately: single, parallel, chain, router, agent loop or human approval. Use deterministic code for fixed paths and agents only for open-ended work. Always cap rounds and gate risky actions.
Hindi: Tool pattern सोच-समझकर चुनो: single, parallel, chain, router, agent loop या human approval। Fixed paths के लिए deterministic code, open-ended काम के लिए ही agent। Rounds की limit रखो और risky actions पर approval लगाओ।

---

## ➡️ Next Topic
**294. Tool Selection Strategy** — how the LLM chooses among many tools and how to help it choose correctly.
