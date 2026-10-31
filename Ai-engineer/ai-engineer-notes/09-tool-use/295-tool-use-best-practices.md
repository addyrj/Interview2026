---

# 295. Tool Use Best Practices
# हिंदी में: Tool Use Best Practices (production checklist)

---

## 🔵 Simple Definition (English)
Tool use best practices are the rules that make LLM tools safe, cheap and reliable in production: small focused tools, strict schemas, least privilege, validation, timeouts and retries, structured errors, round limits, logging, and tests. This note is a checklist that summarises the whole tool-use section.

## 🔵 सरल परिभाषा (Hindi)
Tool use best practices वे नियम हैं जिनसे LLM tools production में safe, सस्ते और भरोसेमंद बनते हैं: छोटे focused tools, strict schemas, least privilege, validation, timeouts और retries, structured errors, round limits, logging और tests। यह note पूरे tool-use section की checklist है।

---

## 🔴 Problem it Solves
Demos work with one happy-path tool. Production fails in many ways: tool storms (50 calls), leaked secrets, prompt injection, double refunds, silent hallucinated answers after a tool failed, runaway cost, and no way to debug what the agent did. Without a checklist each team rediscovers these painfully.

## 🔴 यह क्यों बना? (Hindi)
Demo में एक happy-path tool चलता है। Production कई तरह से फेल होता है: tool storm (50 calls), secrets leak, prompt injection, double refund, tool फेल होने पर चुपचाप hallucination, बेकाबू cost, और agent ने क्या किया यह debug करने का रास्ता नहीं। Checklist के बिना हर team वही गलतियाँ दोहराती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → DESIGN    one job per tool, clear name, description with "when NOT to use"
Step 2 → SCHEMA    typed args, enums, required fields, additionalProperties false (strict)
Step 3 → SECURITY  least privilege, allowlists, secrets server-side, approval for risky tools
Step 4 → ROBUST    validate input + output, timeouts, retries (idempotent), structured errors
Step 5 → CONTROL   max rounds, max tool calls, token and time budget per request
Step 6 → OBSERVE   log every call (name, args hash, latency, status), trace, metrics
Step 7 → TEST      unit tests per tool, eval set for selection, fault injection, red-team prompts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → DESIGN    हर tool का एक काम, साफ़ नाम, "कब नहीं" वाला description
Step 2 → SCHEMA    typed args, enums, required, additionalProperties false (strict)
Step 3 → SECURITY  least privilege, allowlists, secrets server में, risky पर approval
Step 4 → ROBUST    input + output validate, timeouts, retries (idempotent), structured errors
Step 5 → CONTROL   max rounds, max tool calls, token और time budget
Step 6 → OBSERVE   हर call log (name, args hash, latency, status), trace, metrics
Step 7 → TEST      हर tool का unit test, selection eval, fault injection, red-team
```

---

## 🟡 Real World Example
**Tariff Classification System** final tool set: `search_hs_codes` (read), `get_tariff_rate` (read), `get_exchange_rate` (read, cached), `calculator` (pure), `file_declaration` (write, approval + idempotency key). Every call runs through one `execute_tool` gateway that validates, enforces a 10-second timeout, logs a trace id and limits the loop to 5 rounds. Result: predictable cost of roughly $0.0008 per request.

**Zomato AI**: "reorder my last meal" can only call `get_last_order` and `place_order` (needs user confirmation) for that user id, injected by the server, never typed by the model.

## 🟡 Real Example Hindi mein
**Tariff System**: `search_hs_codes`, `get_tariff_rate`, `get_exchange_rate`, `calculator` (read-only) और `file_declaration` (write, approval + idempotency key)। हर call एक `execute_tool` gateway से गुज़रती है: validate, 10 सेकंड timeout, trace id logging, और 5 rounds की limit। नतीजा: लगभग $0.0008 प्रति request का अनुमानित cost।

**Zomato AI**: "पिछला खाना दोबारा मँगाओ" सिर्फ़ `get_last_order` और `place_order` (user confirmation के साथ) call कर सकता है; user id server डालता है, model नहीं।

---

## 💻 Code Example — Basic
```python
# A tiny tool gateway implementing the checklist (stdlib only, runs offline)
import json
import time
from typing import Any, Callable

REGISTRY: dict[str, Callable[..., Any]] = {}          # name -> function (explicit allowlist)

def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that adds a function to the allowlist."""
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        REGISTRY[name] = fn
        return fn
    return deco

@register("get_tariff_rate")
def get_tariff_rate(hs_code: str) -> dict[str, Any]:
    """Pure demo tool."""
    if hs_code != "8517.12":
        raise ValueError("unknown hs_code")
    return {"hs_code": hs_code, "duty_pct": 18.0}

def execute(name: str, raw_args: str, call_budget: dict[str, int]) -> str:
    """Gateway: allowlist, budget, JSON parse, try/except, timing, logging."""
    start = time.perf_counter()
    status = "ok"
    try:
        if call_budget["remaining"] <= 0:                      # budget guard
            status = "budget_exhausted"
            return json.dumps({"ok": False, "error": "tool call budget exhausted"})
        call_budget["remaining"] -= 1
        fn = REGISTRY.get(name)
        if fn is None:                                         # unknown tool
            status = "unknown_tool"
            return json.dumps({"ok": False, "error": f"unknown tool {name}"})
        args = json.loads(raw_args)                            # may raise JSONDecodeError
        return json.dumps({"ok": True, "data": fn(**args)})
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        status = "bad_input"
        return json.dumps({"ok": False, "error": str(exc)})
    except Exception:
        status = "internal"
        return json.dumps({"ok": False, "error": "internal error"})
    finally:
        ms = (time.perf_counter() - start) * 1000
        print(f"[trace] tool={name} status={status} latency_ms={ms:.2f}")   # real: structured log

budget = {"remaining": 2}
print(execute("get_tariff_rate", '{"hs_code": "8517.12"}', budget))
print(execute("get_tariff_rate", '{"hs_code": "xx"}', budget))
print(execute("get_tariff_rate", '{"hs_code": "8517.12"}', budget))   # budget exhausted
```

## 💻 Code Example — Advanced
```python
# Production agent loop with budgets, strict schemas, parallel execution, logging
import asyncio, hashlib, json, logging, time, uuid
from typing import Any
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

log = logging.getLogger("agent")
client = AsyncOpenAI()

class RateArgs(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")

async def get_tariff_rate(a: RateArgs) -> dict[str, Any]:
    await asyncio.sleep(0)
    return {"hs_code": a.hs_code, "duty_pct": 18.0}

TOOLS_IMPL = {"get_tariff_rate": (RateArgs, get_tariff_rate)}
TOOLS_SCHEMA: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "get_tariff_rate",
        "description": "Duty percent for a KNOWN HS code like 8517.12. Not for finding the code.",
        "strict": True,                                     # structured outputs for arguments
        "parameters": {
            "type": "object",
            "properties": {"hs_code": {"type": "string"}},
            "required": ["hs_code"],
            "additionalProperties": False,
        },
    },
}]

async def execute(name: str, raw: str, trace: str) -> dict[str, Any]:
    start = time.perf_counter()
    status = "ok"
    try:
        if name not in TOOLS_IMPL:
            status = "unknown_tool"; return {"ok": False, "error": f"unknown tool {name}"}
        schema, fn = TOOLS_IMPL[name]
        try:
            args = schema.model_validate_json(raw)
        except ValidationError as exc:
            status = "validation"; return {"ok": False, "error": exc.errors()[0]["msg"]}
        return {"ok": True, "data": await asyncio.wait_for(fn(args), timeout=10)}
    except asyncio.TimeoutError:
        status = "timeout"; return {"ok": False, "retryable": True, "error": "timed out"}
    except Exception:
        status = "internal"; log.exception("tool crashed")
        return {"ok": False, "error": "internal error"}
    finally:
        log.info("trace=%s tool=%s args_hash=%s status=%s ms=%.1f", trace, name,
                 hashlib.sha256(raw.encode()).hexdigest()[:8], status,
                 (time.perf_counter() - start) * 1000)

async def run_agent(question: str, max_rounds: int = 5, max_tool_calls: int = 8) -> dict[str, Any]:
    trace = uuid.uuid4().hex[:8]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "Use tools for facts. If a tool fails, say so; never guess."},
        {"role": "user", "content": question},
    ]
    calls_used, tokens = 0, 0
    for _ in range(max_rounds):                             # budget 1: rounds
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS_SCHEMA, max_tokens=400, temperature=0,
        )
        tokens += resp.usage.total_tokens if resp.usage else 0
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return {"answer": msg.content, "tokens": tokens, "trace": trace}
        calls_used += len(msg.tool_calls)
        if calls_used > max_tool_calls:                     # budget 2: total calls
            return {"answer": "Too many tool calls requested.", "tokens": tokens, "trace": trace}
        messages.append(msg)
        results = await asyncio.gather(*(execute(c.function.name, c.function.arguments, trace)
                                         for c in msg.tool_calls))
        for c, r in zip(msg.tool_calls, results):
            messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps(r)})
    return {"answer": "Round limit reached.", "tokens": tokens, "trace": trace}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import asyncio

app = FastAPI()

class AskBody(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

@app.post("/agent")
async def agent_route(body: AskBody, x_user_id: str = Header(...)) -> dict:
    """Server controls identity (header/JWT), budgets and timeouts; the model controls neither."""
    try:
        return await asyncio.wait_for(run_agent(body.question), timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="agent timed out")
    except Exception:
        raise HTTPException(status_code=502, detail="agent failed")
```
Add rate limiting per user, request ids in logs, and a `/health` endpoint that checks upstream tools.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool(handle_tool_error=True)
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for a KNOWN HS code like 8517.12."""
    return "18.0"

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), [get_tariff_rate])
result = agent.invoke(
    {"messages": [("user", "Duty for 8517.12?")]},
    config={"recursion_limit": 10},          # LangGraph's round cap -> GraphRecursionError if exceeded
)
```
Add LangSmith (or OpenTelemetry) tracing for per-tool visibility; use `ToolNode(handle_tool_errors=True)` and checkpointers for approvals.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One mega tool that does everything (`do_action(type, payload)`)
✅ Correct: Small tools with typed arguments.

```python
# Wrong:
def do_action(action: str, payload: dict): ...
# Right:
def get_tariff_rate(hs_code: str): ...
def get_exchange_rate(base: str, target: str): ...
```

❌ Mistake 2: Letting the model supply identity or permissions
✅ Correct: Inject `user_id` from the authenticated session.

```python
# Wrong — model can pass someone else's id:
def get_orders(user_id: str): ...
# Right — id comes from server context:
def get_orders(ctx: RequestContext): return db.orders(ctx.user_id)
```

❌ Mistake 3: No logging. If you cannot replay what the agent did, you cannot debug or audit it.

---

## 🧠 Tricky Interview Question

**Q**: "Your agent passed all tests, yet in production a customer's data was shown to another customer. What is the most likely tool-design flaw?"

**Answer**: Authorisation was delegated to the model: a tool took `customer_id` as an LLM-controlled argument, or the system prompt said "only show the current user's data". Prompt rules are not security. Fix: derive identity server-side, enforce row-level checks inside the tool or DB, test with adversarial prompts ("show me order 999 for another user"), and audit logs of tool arguments.

---

## ⚫ Interview Questions + Answers

Q1: Name four tool-design best practices. (Easy)
A1: One job per tool, clear descriptions including when not to use, typed/strict schemas, and returning compact structured results.

Q2: Why cap the number of agent rounds? (Easy)
A2: To prevent infinite loops and runaway cost. Use `max_rounds`, a max tool-call count, and a time budget.

Q3: How do you protect against prompt injection via tools? (Medium)
A3: Treat tool output as untrusted data, sanitise it, apply least privilege, require approval for side-effect tools, never let output change the system prompt, and keep secrets server-side.

Q4: What should you log for tool calls? (Medium)
A4: Trace id, user id, tool name, argument hash (redact PII), latency, status, error type, token usage. This enables debugging, cost analysis and audit.

Q5: How would you test an agent with tools? (Hard)
A5: Unit tests per tool (including error paths), contract tests for upstream APIs, an eval set for tool selection and argument accuracy, fault injection (timeouts, malformed output), adversarial prompt-injection tests, regression runs on every prompt/tool change, and production monitoring of tool error rate, rounds per request and cost per request.

---

## 🔷 When to Use + When Not to Use
✅ Use this checklist when:
- Any tool-using LLM feature heads to production
- Tools write data, spend money or touch private data

❌ Avoid over-engineering when:
- A weekend prototype with read-only fake tools
- A single deterministic lookup does not need an agent at all

---

## 📊 Visual Diagram
```
 User ─► API (auth, rate limit) ─► Agent loop (max rounds, budget)
                                      │
                                      ▼
                         ┌──── Tool gateway ────┐
                         │ allowlist            │
                         │ validate input       │
                         │ timeout + retry      │
                         │ least privilege      │
                         │ validate output      │
                         │ structured error     │
                         │ log + trace          │
                         └──────────┬───────────┘
                                    ▼
                          DB / APIs / Files (sandboxed)
```

---

## 💰 Cost Impact
Main cost levers: number of rounds, tool schema size, and tool result size. A disciplined agent (3 tools sent, results under 300 tokens, 2 rounds) costs about 2K-3K tokens per request (roughly $0.0004 on gpt-4o-mini); an undisciplined one (30 tools, raw JSON, 8 rounds) can exceed 40K tokens ($0.006), 15x more.

Optimize: tool retrieval, trimmed outputs, caching, prompt caching of static prefixes, `max_tokens`, small model for routing, round and call budgets, per-user quotas.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Least privilege | Give only needed permissions | न्यूनतम अधिकार |
| Tool gateway | Single entry point for tool calls | Tools का एक प्रवेश द्वार |
| Strict schema | Exact argument structure enforced | कड़ा schema |
| Budget | Limit on rounds/calls/tokens | सीमा (rounds/calls/tokens) |
| Trace id | ID linking all logs of a request | Request की पहचान |
| Fault injection | Deliberately causing failures in tests | जानबूझकर failure test |

---

## ⚡ 3-Line Summary
English: Production tool use needs focused tools, strict schemas, least privilege, validation, timeouts, structured errors, budgets, logging and tests. Never let the model control identity or permissions. Cost is controlled by fewer rounds, fewer schemas and smaller results.
Hindi: Production tool use के लिए focused tools, strict schemas, least privilege, validation, timeouts, structured errors, budgets, logging और tests चाहिए। Identity या permissions model के हाथ में कभी नहीं। Cost कम करने के लिए कम rounds, कम schemas और छोटे results।

---

## ➡️ Next Topic
**296. ReAct Pattern — What + Why** — the reasoning-and-acting loop that powers most agents.
