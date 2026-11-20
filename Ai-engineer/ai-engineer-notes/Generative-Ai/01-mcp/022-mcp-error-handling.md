---

# 22. MCP Error Handling
# हिंदी में: MCP में Error Handling
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0, `fastapi` 0.163.0, `langchain-mcp-adapters` 0.3.2. Ran locally (stdio and in-memory transports): tool exceptions, argument-validation errors, unknown tool, per-call timeout, unknown resource, a retry/backoff wrapper, and a FastAPI route mapping failure kinds to HTTP codes. Real LLM recovery behaviour (does the model fix its own input?): not run - needs a live model.

---

## 🔵 Simple Definition (2-3 lines)
MCP has two error layers. **Tool errors**: the call worked at protocol level but the tool failed - the result has `isError=True` and text the model can read. **Protocol errors**: JSON-RPC errors (invalid params -32602, method not found -32601, internal -32603) or client-side timeouts, raised in Python as `McpError`. Handle each differently.

## 🔵 सरल परिभाषा (Hindi)
MCP में errors की दो परतें हैं। **Tool errors**: call protocol स्तर पर सफल रही पर tool fail हुआ - result में `isError=True` और ऐसा text होता है जिसे model पढ़ सकता है। **Protocol errors**: JSON-RPC errors (invalid params -32602, method not found -32601, internal -32603) या client-side timeouts, जो Python में `McpError` की तरह उठते हैं। दोनों को अलग तरह से संभालें।

---

## 🔴 Problem it Solves
Without a clear model, a bad HS code crashes the whole agent request with a 500, or a hanging server freezes the user forever, or the agent retries a non-idempotent call and double-submits a filing. Good handling gives the model recoverable messages and gives the system timeouts, safe retries and clear status codes.

## 🔴 यह क्यों बना? (Hindi)
स्पष्ट model के बिना गलत HS code पूरे agent request को 500 से गिरा देता है, hang हुआ server user को हमेशा के लिए रोक देता है, या agent non-idempotent call दोहराकर filing दो बार भेज देता है। सही handling model को सुधारने योग्य संदेश देती है और system को timeouts, सुरक्षित retries और स्पष्ट status codes।

---

## 🟢 How it Works

```
What we observed (mcp 1.30.0):
tool raises ValueError      -> result.isError=True, text "Error executing tool X: unknown HS code x"
wrong arg type              -> isError=True, text "1 validation error for ...Arguments ... float_parsing"
unknown tool name           -> isError=True, text "Unknown tool: nope"
call exceeds timeout        -> McpError, error.code=408 "Timed out while waiting for response..."
unknown resource            -> McpError "Unknown resource: x://y" (code 0 in this SDK version)
Constants: INVALID_PARAMS=-32602  METHOD_NOT_FOUND=-32601  INTERNAL_ERROR=-32603

Recovery flow:
Step 1 -> call_tool with timeout
Step 2 -> McpError timeout -> retry with backoff ONLY if idempotent
Step 3 -> isError=True -> retry if transient, else give text to the model
Step 4 -> give up -> typed Outcome -> HTTP 422 / 504 / 502
```

## 🟢 कैसे काम करता है? (Hindi)

```
जो हमने देखा (mcp 1.30.0):
tool ने ValueError उठाया   -> result.isError=True, text "Error executing tool X: unknown HS code x"
गलत arg type                -> isError=True, text "1 validation error for ...Arguments ... float_parsing"
अज्ञात tool नाम            -> isError=True, text "Unknown tool: nope"
call timeout से ज़्यादा      -> McpError, error.code=408 "Timed out while waiting for response..."
अज्ञात resource             -> McpError "Unknown resource: x://y" (इस SDK version में code 0)
Constants: INVALID_PARAMS=-32602  METHOD_NOT_FOUND=-32601  INTERNAL_ERROR=-32603

Recovery flow:
Step 1 -> timeout के साथ call_tool
Step 2 -> McpError timeout -> backoff के साथ retry सिर्फ़ तब जब idempotent हो
Step 3 -> isError=True -> transient हो तो retry, वरना text model को दें
Step 4 -> हार मानें -> typed Outcome -> HTTP 422 / 504 / 502
```

---

## 🟡 Real World Example
**Tariff Agent**: the model passes `"6109-10"` instead of `"6109.10"`. The tool returns an error text "unknown HS code"; the model reads it, retries with the right format. When the upstream tariff database is slow, the client times out after a set limit and the API returns 504 instead of hanging.

## 🟡 Real Example Hindi mein
**Tariff Agent**: model `"6109.10"` की जगह `"6109-10"` भेजता है। Tool "unknown HS code" error text लौटाता है; model उसे पढ़कर सही format से दोबारा कोशिश करता है। Upstream tariff database धीमा हो तो client तय सीमा के बाद timeout करता है और API hang होने की जगह 504 देती है।

---

## 💻 Code Example — Basic
```python
# basic_errors.py - see all error shapes over stdio (ran; server = tariff_server.py from note 015)
import asyncio, sys                                         # stdlib
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # stdio transport

async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()                            # handshake
            e = await s.call_tool("get_tariff_rate", {"hs_code": "x"})      # tool raises ValueError
            print(e.isError, e.content[0].text)             # True  Error executing tool get_tariff_rate: unknown HS code x
            e = await s.call_tool("calc_duty", {"value_usd": "abc", "rate_percent": 1})   # bad type
            print(e.isError, e.content[0].text[:60])        # True  Error executing tool calc_duty: 1 validation error ...
            e = await s.call_tool("nope", {})               # unknown tool
            print(e.isError, e.content[0].text)             # True  Unknown tool: nope
asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# resilient_call.py - classify MCP failures and retry only what is safe (ran in-memory)
import asyncio                                              # async runtime
from dataclasses import dataclass                           # tiny result type
from datetime import timedelta                              # per-call timeout type
from mcp import ClientSession                               # client session
from mcp.server.fastmcp import FastMCP                      # server (in-memory test)
from mcp.shared.exceptions import McpError                  # protocol-level error
from mcp.shared.memory import create_connected_server_and_client_session as connect   # no subprocess needed

server = FastMCP("flaky")                                   # demo server with failure modes
calls = {"n": 0}                                            # counts attempts of the flaky tool

@server.tool()
async def flaky_rate(hs_code: str) -> str:                  # fails twice, then works (transient failure)
    """Rate lookup that fails twice before succeeding."""
    calls["n"] += 1
    if calls["n"] < 3:
        raise RuntimeError("upstream busy")                 # becomes isError=True
    return "20%"

@server.tool()
async def slow() -> str:                                    # exceeds the client timeout
    """Sleeps 3s."""
    await asyncio.sleep(3)
    return "late"

@dataclass
class Outcome:                                              # what the agent loop receives
    ok: bool
    text: str
    kind: str                                               # "ok" | "tool_error" | "timeout" | "protocol"

async def safe_call(s: ClientSession, name: str, args: dict, *, retries: int = 3,
                    timeout_s: float = 1.0, idempotent: bool = True) -> Outcome:
    for attempt in range(1, retries + 1):
        try:
            res = await s.call_tool(name, args, read_timeout_seconds=timedelta(seconds=timeout_s))
        except McpError as e:                               # timeouts and JSON-RPC errors raise
            kind = "timeout" if e.error.code == 408 else "protocol"
            if kind == "timeout" and idempotent and attempt < retries:
                await asyncio.sleep(0.1 * 2 ** attempt)     # exponential backoff
                continue
            return Outcome(False, e.error.message, kind)
        text = res.content[0].text if res.content else ""
        if not res.isError:
            return Outcome(True, text, "ok")
        if idempotent and attempt < retries:                # tool errors: retry only if safe
            await asyncio.sleep(0.1 * 2 ** attempt)
            continue
        return Outcome(False, text, "tool_error")           # let the MODEL see this text and adapt
    return Outcome(False, "retries exhausted", "tool_error")
```

```python
# error_api.py - map MCP failure kinds to HTTP status codes (ran with TestClient)
from contextlib import asynccontextmanager                  # lifespan
from typing import Any, AsyncIterator                       # hints
from fastapi import FastAPI, HTTPException                  # web layer
from mcp.shared.memory import create_connected_server_and_client_session as connect
from resilient_call import server, safe_call                # helpers from the block above

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with connect(server) as s:                        # in-memory here; stdio/HTTP session in production
        app.state.session = s
        yield

app = FastAPI(lifespan=lifespan)
STATUS = {"tool_error": 422, "timeout": 504, "protocol": 502}   # kind -> HTTP status

@app.get("/rate/{hs}")
async def rate(hs: str) -> dict[str, Any]:
    out = await safe_call(app.state.session, "flaky_rate", {"hs_code": hs}, retries=3)
    if not out.ok:
        raise HTTPException(STATUS[out.kind], out.text)
    return {"rate": out.text}

@app.get("/slow")
async def slow() -> dict[str, Any]:
    out = await safe_call(app.state.session, "slow", {}, retries=1, timeout_s=0.2)
    if not out.ok:
        raise HTTPException(STATUS[out.kind], out.text)
    return {"ok": True}
```
Observed: `flaky_rate` succeeded on the 3rd attempt (`Outcome(ok=True, text='20%')`, attempts: 3); `slow` returned `kind='timeout'` ("Timed out ... Waited 0.3 seconds"); a missing tool returned `kind='tool_error'` "Unknown tool: does_not_exist"; the API returned `200 {'rate': '20%'}` and `504` for `/slow`. Note: after a client timeout the server may still be running the tool - that is why non-idempotent calls must not be auto-retried. Token usage: error text goes back into the model's context, so keep messages short and actionable. Async: all awaited.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Tool error to model | adapter returns error text (`handle_tool_errors=True`, verified) | verify docs | `failure_error_function` param (verified name) | verify |
| Raise to your code | set `handle_tool_errors=False` | verify | set failure function to raise (check docs) | verify |
| Timeouts | session/client timeouts | verify | `client_session_timeout_seconds` (verified param) | verify |
| Retries | interceptor or tenacity | verify | `max_retry_attempts`, `retry_backoff_seconds_base` on HTTP server (verified) | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Letting a tool exception propagate as a stack trace to the model.
✅ Correct: Raise clear short errors ("valid format is NNNN.NN"); no secrets or stack traces.

❌ Mistake 2: Retrying a write after timeout.
✅ Correct: Use idempotency keys or do not retry; check state first.

❌ Mistake 3: No timeout on `call_tool`.
✅ Correct: Always set one; a hung server should not hang the user.

❌ Mistake 4: Treating `isError` as an exception.
✅ Correct: It is a normal result; check it (`res.isError`) every time.

---

## 🧠 Tricky Interview Question
"A `file_filing` tool times out after 30s. You retry and the customs office receives two filings. What went wrong and how do you design it?"

Answer: A client timeout does not cancel the server's work, so the first call may have succeeded. Retrying a non-idempotent tool duplicates it. Design: add an `idempotency_key` argument the server de-duplicates on, make the tool return a job id and use a separate `get_status` tool (async job pattern), report progress for long calls, and only auto-retry idempotent reads.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you detect a failed tool call?
A1: `result.isError` is True and `content` holds error text.

Q2: [Medium] Tool error vs protocol error?
A2: Tool error = tool ran and failed, the model should see it. Protocol error = request itself invalid or timed out (`McpError`); usually handled by your code.

Q3: [Hard] What happens to arguments of the wrong type?
A3: FastMCP validates with pydantic; we saw `isError=True` with a "validation error ... float_parsing" message, so the model can correct itself.

Q4: [Hard] How do you stop infinite retry loops by the model?
A4: Cap turns/iterations, count identical failing calls in an interceptor, and return escalating hints or abort.

Q5: [System Design] Fault-tolerant MCP client fleet.
A5: Per-server circuit breaker, timeouts, jittered backoff for idempotent calls, health checks, fallback servers, structured error kinds mapped to HTTP codes, and metrics per tool (error rate, p95 latency).

---

## 💰 Cost Impact
Each failed attempt the model sees costs input and output tokens for the extra turn (a retry loop multiplies the per-turn cost; no fixed number claimed). Cheaper handling: retry transient errors in code (zero tokens) before involving the model, keep error messages concise, cap iterations, and fail fast on permanent errors.

---

## 🔷 When to Use
✅ Use the retry wrapper when:
- Calls are idempotent reads over a network

❌ Avoid auto-retry when:
- The tool writes, pays or files without an idempotency key

---

## 📊 Visual Diagram
```
 call_tool(timeout) -+-> result.isError=False ---------> OK
                     |
                     +-> result.isError=True  -> transient & idempotent? -> backoff -> retry
                     |                         \-> else: text to the MODEL (self-correct) / 422
                     +-> McpError 408 timeout -> idempotent? retry : 504
                     +-> McpError other       -> 502
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| isError | Tool failure flag in result | result में tool विफलता का flag |
| McpError | Protocol-level exception | protocol स्तर का exception |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |
| Backoff | Growing wait between retries | retries के बीच बढ़ता इंतज़ार |
| Circuit breaker | Stops calling a failing server | विफल server को बुलाना रोकना |

---

## ⚡ 3-Line Summary
English: Tool failures arrive as `isError` results; protocol problems and timeouts raise `McpError`. Retry only idempotent calls, with timeouts and backoff. Map failure kinds to clear HTTP codes.
Hindi: Tool failures `isError` result की तरह आते हैं; protocol समस्याएँ और timeouts `McpError` उठाते हैं। सिर्फ़ idempotent calls को timeouts और backoff के साथ retry करें। Failure के प्रकार को साफ़ HTTP codes से जोड़ें।

---

## ➡️ Next Topic
**023. MCP Versioning** - protocol version negotiation, server versions and keeping clients compatible.

---
