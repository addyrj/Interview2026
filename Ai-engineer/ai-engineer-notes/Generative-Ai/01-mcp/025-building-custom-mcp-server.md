---

# 25. Building Custom MCP Server
# हिंदी में: अपना Custom MCP Server बनाना
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0 (`FastMCP`), `fastapi` 0.163.0, `pydantic` 2.14.3. Ran locally: the stdio server with lifespan context, structured output, annotations, progress, log messages, resource template and prompt (called by a real MCP client); and the FastAPI-mounted stateless HTTP version (`initialize` and `tools/call` via `TestClient`). Not run: real LLM use, Kubernetes/cloud deployment, a real database pool (the "DB" is a dict).

---

## 🔵 Simple Definition (2-3 lines)
A custom MCP server wraps **your** business capability (not a generic one) as typed tools, resources and prompts. With `FastMCP`, a decorated Python function becomes a tool: the signature gives the JSON schema, the docstring becomes the description, and the return type can become a structured output schema.

## 🔵 सरल परिभाषा (Hindi)
Custom MCP server **आपकी** business capability (generic नहीं) को typed tools, resources और prompts की तरह देता है। `FastMCP` में decorator लगा Python function tool बन जाता है: signature से JSON schema, docstring से description, और return type से structured output schema बनता है।

---

## 🔴 Problem it Solves
Generic servers ("run any SQL", "read any file") are too powerful and give vague tools. The Tariff team wants exactly `quote(hs_code, value_usd)` with validation, auditing and a stable contract. A custom server gives narrow, safe, well-described tools reusable by every agent framework.

## 🔴 यह क्यों बना? (Hindi)
Generic servers ("कोई भी SQL चलाओ", "कोई भी file पढ़ो") बहुत शक्तिशाली और धुंधले tools देते हैं। Tariff team को ठीक `quote(hs_code, value_usd)` चाहिए - validation, auditing और स्थिर contract के साथ। Custom server संकीर्ण, सुरक्षित, अच्छी तरह वर्णित tools देता है जो हर agent framework में काम आते हैं।

---

## 🟢 How it Works

```
Step 1 -> mcp = FastMCP("name", instructions=..., lifespan=...)
Step 2 -> @mcp.tool()      -> function -> tool (schema from type hints, description from docstring)
Step 3 -> return a pydantic model -> outputSchema + structuredContent in the result
Step 4 -> @mcp.resource("uri://{param}") -> readable data;  @mcp.prompt() -> reusable template
Step 5 -> lifespan yields shared resources (DB pool) -> tools read them via ctx.request_context.lifespan_context
Step 6 -> ctx.info(...) / ctx.report_progress(...) -> log + progress messages to the client
Step 7 -> mcp.run() (stdio)  OR  mount mcp.streamable_http_app() in FastAPI (HTTP)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> mcp = FastMCP("name", instructions=..., lifespan=...)
Step 2 -> @mcp.tool()      -> function -> tool (type hints से schema, docstring से description)
Step 3 -> pydantic model लौटाएँ -> outputSchema + result में structuredContent
Step 4 -> @mcp.resource("uri://{param}") -> पढ़ने योग्य data;  @mcp.prompt() -> reusable template
Step 5 -> lifespan साझा resources (DB pool) देता है -> tools उन्हें ctx.request_context.lifespan_context से पढ़ते हैं
Step 6 -> ctx.info(...) / ctx.report_progress(...) -> client को log + progress संदेश
Step 7 -> mcp.run() (stdio)  या  mcp.streamable_http_app() को FastAPI में mount करें (HTTP)
```

---

## 🟡 Real World Example
**Tariff Agent**: `quote` reads rates from a pool created at startup, validates inputs, reports progress for long lookups, returns a typed `Duty`. The same server is launched over stdio by developers and deployed as stateless HTTP behind Kubernetes for production agents.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `quote` startup पर बने pool से rates पढ़ता है, inputs validate करता है, लंबी lookups पर progress बताता है और typed `Duty` लौटाता है। वही server developers के लिए stdio से चलता है और production agents के लिए Kubernetes के पीछे stateless HTTP की तरह deploy होता है।

---

## 💻 Code Example — Basic
```python
# basic_server.py - smallest useful custom server (same shape as tariff_server.py in note 015; ran)
from mcp.server.fastmcp import FastMCP                      # high-level server API

mcp = FastMCP("tariff")                                     # server name clients will see
RATES: dict[str, float] = {"6109.10": 20.0, "7318.15": 10.0}  # demo data

@mcp.tool()                                                 # turns the function into a tool
def get_tariff_rate(hs_code: str) -> str:                   # type hints -> JSON schema
    """Return duty percent for an HS code."""               # docstring -> description the model reads
    if hs_code not in RATES:                                # validate untrusted input
        raise ValueError(f"unknown HS code {hs_code}")      # -> result with isError=True
    return f"{RATES[hs_code]}%"                             # text result

if __name__ == "__main__":
    mcp.run()                                               # stdio transport by default
```

## 💻 Code Example — Advanced
```python
# tariff_custom_server.py - narrow, typed, production-shaped server (ran over stdio)
import logging                                              # logs -> stderr (safe for stdio)
from contextlib import asynccontextmanager                  # lifespan helper
from dataclasses import dataclass                           # app context
from typing import AsyncIterator                            # hints
from pydantic import BaseModel, Field                       # structured output model
from mcp.server.fastmcp import Context, FastMCP             # server + per-request context
from mcp.types import ToolAnnotations                       # client hints

log = logging.getLogger("tariff")                           # module logger

@dataclass
class AppCtx:                                               # shared resources created at startup
    rates: dict[str, float]                                 # real code: DB pool / HTTP client

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppCtx]:
    log.info("starting")                                    # e.g. open DB pool here
    try:
        yield AppCtx(rates={"6109.10": 20.0, "7318.15": 10.0})
    finally:
        log.info("stopped")                                 # close pool here

mcp = FastMCP("tariff-custom", instructions="Duty quotes for HS codes.", lifespan=lifespan)

class Duty(BaseModel):                                      # output schema -> clients can validate
    hs_code: str
    rate_percent: float = Field(ge=0, le=100)
    duty_usd: float

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))   # hints only
async def quote(hs_code: str, value_usd: float, ctx: Context) -> Duty:
    """Quote duty for an HS code and goods value in USD."""
    app: AppCtx = ctx.request_context.lifespan_context      # shared resources
    await ctx.info(f"quote {hs_code}")                      # log message sent to the client
    await ctx.report_progress(1, 2)                         # progress notification
    rate = app.rates.get(hs_code)
    if rate is None:
        raise ValueError(f"unknown HS code {hs_code}; expected format NNNN.NN")   # actionable error
    if value_usd < 0:
        raise ValueError("value_usd must be >= 0")
    await ctx.report_progress(2, 2)
    return Duty(hs_code=hs_code, rate_percent=rate, duty_usd=value_usd * rate / 100)

@mcp.resource("tariff://rate/{hs_code}")                    # read-only data addressed by URI template
def rate_resource(hs_code: str) -> str:
    """Rate as plain text."""
    return f"{hs_code}: see quote tool"                     # kept trivial in this demo

@mcp.prompt()                                               # reusable prompt template
def classify(product: str) -> str:
    return f"Classify this product into an HS code and justify: {product}"

if __name__ == "__main__":
    mcp.run()                                               # stdio; or mcp.run(transport="streamable-http")
```

```python
# gateway.py - mount the server inside FastAPI as stateless HTTP (ran with TestClient)
import contextlib                                           # lifespan helper
from fastapi import FastAPI                                 # web app
from tariff_custom_server import mcp                        # the server above

mcp.settings.stateless_http = True                          # any replica can serve any request
mcp.settings.json_response = True                           # plain JSON replies

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():                   # MCP needs its task group running
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")                                         # k8s probe
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.mount("/tariff", mcp.streamable_http_app())            # MCP endpoint: POST /tariff/mcp
```
Observed with a real MCP client over stdio: initialize returned the `instructions`; the tool listed `readOnlyHint=True` and output properties `['hs_code', 'rate_percent', 'duty_usd']`; `quote` returned `structuredContent {'hs_code': '6109.10', 'rate_percent': 20.0, 'duty_usd': 100.0}` for value 500 with progress 1/2 and 2/2 and a server log message; a bad HS code returned `isError=True` "unknown HS code bad; expected format NNNN.NN"; the resource template `tariff://rate/{hs_code}` and the `classify` prompt worked. Through the FastAPI mount, `initialize` and `tools/call` returned 200 with `{'hs_code': '6109.10', 'rate_percent': 20.0, 'duty_usd': 20.0}` for value 100 (TestClient needs `base_url="http://localhost:8000"` because Host/Origin protection rejects `testserver`). **Gotcha observed:** in stateless mode the server `lifespan` logged "starting"/"stopped" for every request - do not open a heavy DB pool there; create it in the FastAPI lifespan instead and share it. Token usage: clear descriptions and structured output cost tokens once per turn, so keep both short. Error handling: raise precise exceptions; they become `isError` results. Async: tools are `async`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Consumes this server | `MultiServerMCPClient` (verified, note 016) | verify docs | `MCPServerStdio/StreamableHttp` (verified, note 018) | verify |
| Defines tools in-process instead | `@tool` | `@tool` / BaseTool | `@function_tool` | function tools |
| Tool contract source | MCP schemas | MCP or class schemas | MCP or Python signature | verify |
| Reuse across frameworks | yes via MCP | yes via MCP | yes via MCP | yes via MCP |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `print()` for debugging in a stdio server.
✅ Correct: Use `logging` (stderr); stdout carries the protocol.

❌ Mistake 2: Vague docstrings like "gets stuff".
✅ Correct: Say what, inputs with format examples, what it returns, and when not to use it.

❌ Mistake 3: Tools that return huge blobs.
✅ Correct: Paginate, summarise, cap size; return structured fields the model needs.

❌ Mistake 4: Creating heavy resources inside the server lifespan on stateless HTTP.
✅ Correct: Own them in the web app lifespan; stateless mode re-runs the server lifespan per request (observed).

---

## 🧠 Tricky Interview Question
"Your custom server works over stdio but returns 421 'Invalid Host header' when tested with a normal HTTP client in CI. Why?"

Answer: FastMCP enables DNS-rebinding protection by default for a localhost-bound server and only allows `localhost`/`127.0.0.1` Host values with the configured port. A test client sending `Host: testserver` (or an internal service name behind a proxy) is rejected. Fix: use the right host:port in tests, or configure `TransportSecuritySettings(allowed_hosts=[...], allowed_origins=[...])` for your real hostnames - never just disable protection on a public service without adding authentication.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How does a Python function become a tool?
A1: `@mcp.tool()`: signature -> input schema, docstring -> description, return annotation -> optional output schema.

Q2: [Medium] Tool vs resource vs prompt?
A2: Tool = action the model invokes. Resource = data the host/app can read by URI. Prompt = reusable template chosen by the user/host.

Q3: [Hard] How do you share a DB pool across tool calls?
A3: Create it in `lifespan`, yield it as context, read via `ctx.request_context.lifespan_context` (stdio/stateful). For stateless HTTP, create it in the web app lifespan (the MCP lifespan reran per request in our test).

Q4: [Hard] How do you report progress on a long tool?
A4: `await ctx.report_progress(done, total)`; the client passes a `progress_callback` to `call_tool` (observed 1/2, 2/2).

Q5: [System Design] Ship the Tariff server to production.
A5: Stateless Streamable HTTP in FastAPI, OAuth at the gateway, DB pool in app lifespan, read-only credentials, rate limits, `/health`, structured logs, metrics per tool, schema snapshot tests in CI, versioned tool names for breaking changes.

---

## 💰 Cost Impact
Server code costs no tokens; its **design** does. Each tool's name, description and schema ride along on every model turn; structured output adds an outputSchema. Return only needed fields to reduce tool-result tokens. Tips: few well-named tools, short precise descriptions, paginated outputs, deterministic code for anything not needing the LLM.

---

## 🔷 When to Use
✅ Use when:
- You own the domain logic and want a stable, safe contract for many agents

❌ Avoid when:
- One agent, one in-process function (plain `@tool`/`@function_tool` is simpler)
- A well-maintained vendor server already fits and is allowed by policy

---

## 📊 Visual Diagram
```
 Dev:   Agent --stdio--> python tariff_custom_server.py
 Prod:  Agent --POST /tariff/mcp--> [FastAPI app]
                                      |-- /health
                                      '-- mounted FastMCP (stateless, JSON)
                                             quote() -> Duty{hs_code, rate_percent, duty_usd}
                                             resource tariff://rate/{hs}   prompt classify
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FastMCP | High-level Python server API | high-level Python server API |
| lifespan | Startup/shutdown shared resources | startup/shutdown के साझा resources |
| structuredContent | Typed JSON tool result | typed JSON tool result |
| Context | Per-request helper (log, progress) | प्रति-request helper |
| Stateless HTTP | No server-side session | बिना server-side session के HTTP |

---

## ⚡ 3-Line Summary
English: Decorate typed Python functions to make tools; return pydantic models for structured output. Use lifespan for shared resources and stateless HTTP for scaling. Keep tools narrow, validated and well described.
Hindi: Typed Python functions पर decorator लगाकर tools बनाएँ; structured output के लिए pydantic models लौटाएँ। साझा resources के लिए lifespan और scaling के लिए stateless HTTP लें। Tools संकीर्ण, validated और अच्छी तरह वर्णित रखें।

---

## ➡️ Next Topic
**026. MCP Registry** - how servers are published, found and trusted.

---
