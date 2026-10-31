---

# 290. Tool Error Handling
# हिंदी में: Tool Error Handling (tool फेल हो तो क्या करें)

---

## 🔵 Simple Definition (English)
Tool error handling means catching every failure inside a tool (bad arguments, timeouts, missing data, crashes) and returning a clear, structured error message to the LLM instead of crashing the request. The model can then fix its arguments, try another tool, or tell the user honestly.

## 🔵 सरल परिभाषा (Hindi)
Tool error handling का मतलब है tool के अंदर हर failure (गलत arguments, timeout, data न मिलना, crash) को पकड़ना और request crash करने की जगह LLM को साफ़, structured error message लौटाना। Model फिर arguments ठीक कर सकता है, दूसरा tool चुन सकता है या user को सच बता सकता है।

---

## 🔴 Problem it Solves
Without handling, one exception in a tool returns a 500 to the user, loses the conversation, and wastes tokens already spent. Worse, a silent failure (empty string) makes the LLM hallucinate: "The duty is 12%" when the DB call actually failed. LLMs also generate invalid JSON or wrong types for arguments regularly.

## 🔴 यह क्यों बना? (Hindi)
Handling के बिना tool की एक exception user को 500 देती है, conversation खो जाती है और खर्च हुए tokens बेकार जाते हैं। Silent failure (खाली string) से LLM hallucinate करता है: DB fail हुआ पर वह कहता है "duty 12% है"। LLM अक्सर गलत JSON या types भी बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → LLM emits tool_call with a JSON string of arguments
Step 2 → Parse JSON (catch JSONDecodeError) and validate with pydantic
Step 3 → Unknown tool name? -> return {"ok": false, "error": "unknown tool"}
Step 4 → Run the tool inside try/except with a timeout
Step 5 → Classify the error: user_error / retryable / fatal
Step 6 → Return a SHORT structured error (no stack trace, no secrets)
Step 7 → LLM reads the error and corrects itself or explains; cap the loop
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM arguments का JSON string भेजता है
Step 2 → JSON parse (JSONDecodeError पकड़ो) और pydantic से validate
Step 3 → Unknown tool? -> {"ok": false, "error": "unknown tool"} लौटाओ
Step 4 → Tool को try/except और timeout के अंदर चलाओ
Step 5 → Error classify करो: user_error / retryable / fatal
Step 6 → छोटा structured error लौटाओ (stack trace या secrets नहीं)
Step 7 → LLM error पढ़कर खुद सुधारता है या समझाता है; loop cap रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model calls `get_tariff_rate(hs_code="85171")` (5 digits, invalid). The tool returns `{"ok": false, "error_type": "validation", "error": "hs_code must look like 8517.12", "hint": "use 4+2 digits"}`. The model repairs it to `8517.12` and succeeds on the next round. Without this, the user sees "Internal Server Error".

**Zomato AI**: Restaurant API is down; the tool returns `{"retryable": true}`; the assistant says "I could not check the menu right now, please try again" instead of inventing dishes.

## 🟡 Real Example Hindi mein
**Tariff System**: Model `get_tariff_rate(hs_code="85171")` call करता है (invalid)। Tool लौटाता है `{"ok": false, "error": "hs_code must look like 8517.12"}`। Model खुद सुधारकर `8517.12` भेजता है और सफल होता है। वरना user को "Internal Server Error" दिखता।

**Zomato AI**: Restaurant API down है; tool `{"retryable": true}` लौटाता है; assistant कहता है "अभी menu check नहीं हो पाया", dishes गढ़ता नहीं।

---

## 💻 Code Example — Basic
```python
# Basic tool error handling decorator (pure Python, runs offline)
import json
import functools
from typing import Any, Callable

def safe_tool(func: Callable[..., Any]) -> Callable[..., str]:
    """Wrap a tool so it ALWAYS returns a JSON string, never raises."""
    @functools.wraps(func)                       # keep the original name/docstring
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            result = func(*args, **kwargs)       # run the real tool
            return json.dumps({"ok": True, "data": result})
        except ValueError as exc:                # caller (LLM) made a mistake: fixable
            return json.dumps({"ok": False, "error_type": "validation", "error": str(exc)})
        except TimeoutError:                     # transient: may succeed later
            return json.dumps({"ok": False, "error_type": "timeout", "retryable": True,
                               "error": "service timed out"})
        except Exception as exc:                 # unknown bug: log details, hide internals
            print(f"[tool-bug] {type(exc).__name__}: {exc}")    # real code: logger.exception
            return json.dumps({"ok": False, "error_type": "internal",
                               "error": "tool failed unexpectedly"})
    return wrapper

@safe_tool
def get_tariff_rate(hs_code: str) -> dict[str, Any]:
    """Return duty for an HS code like 8517.12."""
    if len(hs_code) != 7 or hs_code[4] != ".":
        raise ValueError("hs_code must look like 8517.12")
    rates = {"8517.12": 18.0}
    if hs_code not in rates:
        raise ValueError(f"no rate found for {hs_code}")
    return {"hs_code": hs_code, "duty_pct": rates[hs_code]}

print(get_tariff_rate("8517.12"))   # ok
print(get_tariff_rate("85171"))     # validation error with a hint
print(get_tariff_rate("9999.99"))   # not found
```

## 💻 Code Example — Advanced
```python
# Production: pydantic validation + error taxonomy + async timeout + dispatcher
import asyncio, json, logging
from typing import Any, Awaitable, Callable
from pydantic import BaseModel, Field, ValidationError, field_validator

log = logging.getLogger("tools")

class ToolError(Exception):
    """Base class: carries a type and a retryable flag the LLM can read."""
    error_type = "tool_error"
    retryable = False

class NotFoundError(ToolError):
    error_type = "not_found"

class UpstreamError(ToolError):
    error_type = "upstream"
    retryable = True                              # worth trying again

class RateArgs(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")   # pydantic v2 uses `pattern`

    @field_validator("hs_code")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()

async def get_rate(args: RateArgs) -> dict[str, Any]:
    """Real tool body: may raise ToolError subclasses."""
    await asyncio.sleep(0.01)                     # pretend DB call
    if args.hs_code == "0000.00":
        raise NotFoundError(f"no tariff for {args.hs_code}")
    return {"hs_code": args.hs_code, "duty_pct": 18.0}

TOOLS: dict[str, tuple[type[BaseModel], Callable[[Any], Awaitable[dict[str, Any]]]]] = {
    "get_rate": (RateArgs, get_rate),
}

async def execute_tool(name: str, raw_args: str, timeout: float = 5.0) -> dict[str, Any]:
    """Single choke point: every tool call goes through here."""
    if name not in TOOLS:
        return {"ok": False, "error_type": "unknown_tool", "error": f"no tool {name!r}",
                "available": list(TOOLS)}         # help the model pick a valid tool
    schema, fn = TOOLS[name]
    try:
        args = schema.model_validate_json(raw_args)        # parses JSON + validates
    except ValidationError as exc:
        first = exc.errors()[0]                            # keep error message short
        return {"ok": False, "error_type": "validation",
                "error": f"{'.'.join(map(str, first['loc']))}: {first['msg']}"}
    try:
        data = await asyncio.wait_for(fn(args), timeout=timeout)
        return {"ok": True, "data": data}
    except asyncio.TimeoutError:
        return {"ok": False, "error_type": "timeout", "retryable": True, "error": "timed out"}
    except ToolError as exc:
        return {"ok": False, "error_type": exc.error_type, "retryable": exc.retryable, "error": str(exc)}
    except Exception:
        log.exception("unexpected tool failure: %s", name)   # full trace goes to logs only
        return {"ok": False, "error_type": "internal", "error": "unexpected failure"}

async def demo() -> None:
    print(await execute_tool("get_rate", '{"hs_code": "8517.12"}'))
    print(await execute_tool("get_rate", '{"hs_code": "85171"}'))
    print(await execute_tool("get_rate", 'not json'))
    print(await execute_tool("get_rate", '{"hs_code": "0000.00"}'))
    print(await execute_tool("nope", "{}"))

if __name__ == "__main__":
    asyncio.run(demo())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class ToolRequest(BaseModel):
    name: str
    arguments: str                                # raw JSON string like the LLM sends it

@app.post("/tools/execute")
async def run_tool(req: ToolRequest) -> dict:
    """Tools never raise: HTTP 200 with ok=false lets the agent loop continue."""
    return await execute_tool(req.name, req.arguments)

@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception) -> JSONResponse:
    """Last line of defence for non-tool code: hide internals from clients."""
    return JSONResponse(status_code=500, content={"detail": "internal error"})
```
Design choice: tool failures are normal data for the agent (HTTP 200, `ok: false`); infrastructure failures (DB for your own app down) are HTTP 5xx.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool, ToolException

@tool(handle_tool_error=True)                    # ToolException message goes back to the LLM
def get_tariff_rate(hs_code: str) -> str:
    """Return duty for an HS code like 8517.12."""
    if len(hs_code) != 7:
        raise ToolException("hs_code must look like 8517.12")   # becomes the observation
    return "18.0"
```
Also: `StructuredTool(handle_validation_error=True)` for argument errors, `AgentExecutor(handle_parsing_errors=True)` for malformed agent output, and LangGraph's `ToolNode(tools, handle_tool_errors=True)` which converts exceptions into `ToolMessage` errors the model can read.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting exceptions escape
✅ Correct: Return structured errors.

```python
# Wrong — the whole request dies:
def tool(x: str) -> str:
    return str(1 / int(x))
# Right:
def tool(x: str) -> str:
    try:
        return str(1 / int(x))
    except (ValueError, ZeroDivisionError) as exc:
        return f"error: {exc}"
```

❌ Mistake 2: Returning an empty string or "None" on failure
✅ Correct: Say clearly that it failed. Silence makes the model invent an answer.

```python
# Wrong:
return ""
# Right:
return json.dumps({"ok": False, "error": "database unavailable"})
```

❌ Mistake 3: Returning full stack traces or connection strings. They waste tokens and leak secrets.

---

## 🧠 Tricky Interview Question

**Q**: "Your tool returns an error and the LLM retries the same bad call 10 times, burning tokens. What went wrong and how do you fix it?"

**Answer**: The error message was not actionable and nothing bounded the loop. Fix: (1) make errors specific with a hint ("hs_code must look like 8517.12, got 85171"), (2) include `retryable` so the model knows when not to retry, (3) enforce a max-iterations cap, (4) detect identical repeated calls and break with a final message, (5) track per-tool failure counts and stop after N.

---

## ⚫ Interview Questions + Answers

Q1: Why return errors instead of raising? (Easy)
A1: The LLM can read an error and self-correct or explain it. A raised exception crashes the request and loses context.

Q2: What should an error payload contain? (Easy)
A2: `ok=false`, `error_type`, a short human-readable message, optionally a `hint` and `retryable`. No stack traces or secrets.

Q3: How do you handle invalid JSON arguments from the model? (Medium)
A3: Catch `JSONDecodeError`/pydantic `ValidationError`, return the validation message, and let the model retry. Using strict structured outputs reduces these failures.

Q4: Tool error vs infrastructure error? (Medium)
A4: Tool errors (bad args, not found) are part of the agent's conversation, returned as data. Infrastructure errors in your own service (cannot reach your LLM provider) are HTTP errors with logging and alerts.

Q5: Design error handling for an agent with 20 tools. (Hard)
A5: One `execute_tool` choke point with pydantic validation, timeout, error taxonomy, structured results; per-tool circuit breakers; max iterations; repeated-call detection; observability (tool name, latency, error_type metrics, traces); fallback tools or graceful degradation message; tests with fault injection.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always, for every production tool

❌ Avoid when:
- Swallowing errors silently. Never hide a failure from the model or from logs.
- Catching exceptions so broadly that bugs go unnoticed (always log the unexpected ones)

---

## 📊 Visual Diagram
```
 tool_call(name, raw_json)
        │
        ▼
  known tool? ──no──► {"error_type":"unknown_tool"}
        │yes
        ▼
  parse + validate ──fail──► {"error_type":"validation","error":"..."}
        │ok
        ▼
  run with timeout ──timeout──► {"retryable": true}
        │ ──ToolError──► {"error_type":"not_found",...}
        │ ──bug──► log trace, {"error_type":"internal"}
        ▼
   {"ok": true, "data": ...}
        │
        ▼
   LLM reads result/error -> fixes, retries (capped) or explains
```

---

## 💰 Cost Impact
Each failed round trip re-sends the full history: a 2K-token conversation with 3 failed retries costs about 6K extra input tokens. Long error messages add more. Good errors reduce rounds (self-correction in 1 try).

Optimize: validate before calling external services, keep errors under 50 tokens, include hints, cap iterations, and cache negative results ("no rate for X") so the same failure is not re-queried.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured error | Error as JSON with fields | JSON रूप में error |
| Retryable | Might succeed if tried again | दोबारा कोशिश लायक |
| Validation error | Arguments fail schema checks | Arguments गलत |
| Observation | Tool result fed back to model | Tool का नतीजा |
| Choke point | Single place all calls pass through | एक ही जगह जहाँ से सब गुज़रे |
| Graceful degradation | Reduced but safe behaviour on failure | Failure में भी सुरक्षित जवाब |

---

## ⚡ 3-Line Summary
English: Tools must never crash the agent; catch errors and return short structured payloads with type, hint and retryable. Validate arguments with pydantic, use timeouts and cap the loop. Good errors let the LLM self-correct and save tokens.
Hindi: Tools agent को crash न करें; errors पकड़कर छोटा structured payload (type, hint, retryable) लौटाओ। Pydantic से validate, timeout और loop cap लगाओ। अच्छे errors से LLM खुद सुधरता है और tokens बचते हैं।

---

## ➡️ Next Topic
**291. Tool Retry Logic** — when and how to retry failed tools with backoff and idempotency.
