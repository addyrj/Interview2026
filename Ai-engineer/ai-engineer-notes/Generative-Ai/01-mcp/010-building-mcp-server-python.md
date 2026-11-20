---

# 10. Building MCP Server (Python)
# हिंदी में: Python में MCP Server बनाना
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python, `mcp.server.fastmcp.FastMCP`), `fastapi` 0.163.0. The full server below was launched as a real stdio subprocess by a Python client and every tool/error path ran. Not run: the `mcp dev` / `mcp install` CLI helpers (they need the optional `mcp[cli]` extra which was not installed) and any real LLM host (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
Building an MCP server in Python means creating a `FastMCP` object, decorating typed functions with `@mcp.tool()`, `@mcp.resource()` and `@mcp.prompt()`, and calling `mcp.run()`. The SDK generates JSON schemas from your type hints, handles the JSON-RPC protocol, and talks stdio (or HTTP). A good server adds validation, logging to stderr, shared state via a lifespan, and tests.

## 🔵 सरल परिभाषा (Hindi)
Python में MCP server बनाने का मतलब है `FastMCP` object बनाना, typed functions पर `@mcp.tool()`, `@mcp.resource()` और `@mcp.prompt()` लगाना, और `mcp.run()` चलाना। SDK आपके type hints से JSON schema बनाता है, JSON-RPC protocol संभालता है और stdio (या HTTP) पर बात करता है। अच्छे server में validation, stderr पर logging, lifespan से साझा state और tests होते हैं।

---

## 🔴 Problem it Solves
Without a proper server structure, each team writes ad-hoc scripts: schemas drift from code, `print()` debugging corrupts the protocol, DB connections are opened per call, and errors crash the process instead of reaching the LLM. A standard layout (typed tools, lifespan resources, structured logging, error handling) makes the server safe to run under any MCP host.

## 🔴 यह क्यों बना? (Hindi)
सही structure के बिना हर team ad-hoc scripts लिखती है: schema code से अलग हो जाता है, `print()` debugging protocol बिगाड़ देती है, हर call पर DB connection खुलता है, और errors process crash कर देती हैं, LLM तक नहीं पहुँचतीं। Standard layout (typed tools, lifespan resources, structured logging, error handling) server को किसी भी MCP host के नीचे सुरक्षित चलाने लायक बनाता है।

---

## 🟢 How it Works

```
Step 1 -> pip install "mcp"           (verified with mcp 1.30.0 on Python 3.13; check the package's requires-python)
Step 2 -> mcp = FastMCP("name", instructions=..., lifespan=...)
Step 3 -> @mcp.tool() on typed functions   -> inputSchema from type hints, docstring = description
Step 4 -> @mcp.resource("uri/{param}") / @mcp.prompt() for context and templates
Step 5 -> logging -> STDERR only (stdout belongs to the protocol on stdio)
Step 6 -> mcp.run()  -> stdio by default; host spawns it and talks JSON-RPC
Step 7 -> test with an MCP client (stdio or in-memory) BEFORE connecting a real host
Step 8 -> package it: entry point / uv or pip, pinned deps, README with the host config
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> pip install "mcp"           (mcp 1.30.0, Python 3.13 पर verified; requires-python देख लें)
Step 2 -> mcp = FastMCP("name", instructions=..., lifespan=...)
Step 3 -> typed functions पर @mcp.tool() -> type hints से inputSchema, docstring = description
Step 4 -> context और templates के लिए @mcp.resource("uri/{param}") / @mcp.prompt()
Step 5 -> logging -> सिर्फ़ STDERR (stdio में stdout protocol का है)
Step 6 -> mcp.run()  -> default stdio; host इसे spawn करके JSON-RPC से बात करता है
Step 7 -> असली host जोड़ने से पहले MCP client (stdio या in-memory) से test करें
Step 8 -> package करें: entry point / uv या pip, pinned deps, host config वाला README
```

---

## 🟡 Real World Example
**Tariff Agent**: `tariff_server.py` loads the HS-code rate table once at startup (lifespan), exposes `get_duty_rate` (read-only, validated) and `landed_cost`, a resource and a review prompt. The same file is launched by Claude Desktop (stdio), by the LangGraph/FastAPI agent (stdio client) and by tests. A bad code like `9999` returns a readable error listing known codes, so the agent can retry.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `tariff_server.py` startup (lifespan) पर HS-code rate table एक बार लोड करता है, और `get_duty_rate` (read-only, validated), `landed_cost`, एक resource और review prompt देता है। यही file Claude Desktop (stdio), LangGraph/FastAPI agent (stdio client) और tests तीनों चलाते हैं। `9999` जैसा गलत code पढ़ने लायक error देता है जिसमें ज्ञात codes होते हैं, ताकि agent दोबारा कोशिश कर सके।

---

## 💻 Code Example — Basic
```python
# server.py - smallest useful MCP server (ran over stdio)
from mcp.server.fastmcp import FastMCP                      # high-level API

mcp = FastMCP("tariff-server")                              # name the host will display
RATES: dict[str, float] = {"8517": 0.0, "6403": 10.0}       # demo data

@mcp.tool()                                                 # expose as a tool
def get_duty_rate(hs_code: str) -> float:                   # type hints -> JSON schema
    """Return duty percent for an HS code."""               # LLM-visible description
    if hs_code not in RATES:                                # unknown input
        raise ValueError(f"unknown HS code {hs_code}")      # -> isError result the LLM can read
    return RATES[hs_code]                                   # structuredContent {"result": 10.0}

if __name__ == "__main__":                                  # script entry
    mcp.run()                                               # stdio transport
```
Verified with a stdio client: `{'result': 0.0}` for 8517 and `isError True` with `unknown HS code ...` for a bad code.

## 💻 Code Example — Advanced
```python
# tariff_server.py - production-style: lifespan state, validation, stderr logging, typed output (all paths ran)
import logging                                              # structured logs
import sys                                                  # to point logs at stderr
from collections.abc import AsyncIterator                   # lifespan return type
from contextlib import asynccontextmanager                  # build the lifespan
from dataclasses import dataclass                           # typed app state
from pydantic import BaseModel, Field                       # typed + validated output
from mcp.server.fastmcp import Context, FastMCP             # server + context
from mcp.server.session import ServerSession                # typed session
from mcp.types import ToolAnnotations                       # safety hints

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(name)s %(message)s")   # NEVER stdout on stdio
log = logging.getLogger("tariff")                           # module logger

@dataclass
class AppState:                                             # shared objects (DB pool, caches ...)
    rates: dict[str, float]                                 # demo: in-memory table

@asynccontextmanager                                        # runs once per server process
async def lifespan(server: FastMCP) -> AsyncIterator[AppState]:   # yields state to every request
    log.info("startup: loading rates")                      # visible on stderr
    state = AppState(rates={"8517": 0.0, "6403": 10.0, "6109": 12.0})   # real code: await db.connect()
    try:                                                    # guarantee cleanup
        yield state                                         # server runs while we are suspended here
    finally:                                                # always executed
        log.info("shutdown")                                # real code: await db.close()

mcp = FastMCP("tariff-server", instructions="Look up customs duty rates by 4-digit HS code.", lifespan=lifespan)   # server-level hint for LLMs

class Duty(BaseModel):                                      # output contract -> outputSchema
    hs_code: str = Field(pattern=r"^\d{4}$")                # 4 digits
    rate_pct: float = Field(ge=0, le=100)                   # sane range

AppCtx = Context[ServerSession, AppState]                   # alias: ctx.request_context.lifespan_context is AppState

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))   # hints for the host UI
async def get_duty_rate(hs_code: str, ctx: AppCtx) -> Duty:   # async + typed
    """Return the duty percent for a 4-digit HS code, e.g. 6403."""
    if not (len(hs_code) == 4 and hs_code.isdigit()):       # validate untrusted LLM input
        raise ValueError(f"hs_code must be 4 digits, got {hs_code!r}")   # tells the LLM how to fix it
    rates = ctx.request_context.lifespan_context.rates      # shared state from lifespan
    if hs_code not in rates:                                # business error
        raise ValueError(f"unknown HS code {hs_code}; known: {sorted(rates)}")   # helpful message
    log.info("lookup %s", hs_code)                          # audit trail (stderr)
    return Duty(hs_code=hs_code, rate_pct=rates[hs_code])   # validated model

@mcp.tool()                                                 # second tool
async def landed_cost(price: float, hs_code: str, ctx: AppCtx) -> float:   # numbers are typed
    """Price plus duty for a 4-digit HS code."""
    rates = ctx.request_context.lifespan_context.rates      # shared state
    if hs_code not in rates:                                # same validation idea
        raise ValueError(f"unknown HS code {hs_code}")      # -> isError
    return round(price * (1 + rates[hs_code] / 100), 2)     # 100 * 1.12 -> 112.0

@mcp.resource("tariff://rates/{hs_code}", mime_type="text/plain")   # resource template
def rate_text(hs_code: str) -> str:                         # URI parameter
    return f"{hs_code}: see get_duty_rate"                  # demo body

@mcp.prompt()                                               # user-controlled template
def review(hs_code: str) -> str:                            # argument
    return f"Review the classification {hs_code} and list risks."   # one user message

def main() -> None:                                         # console-script friendly entry
    mcp.run()                                               # stdio; use mcp.run(transport="streamable-http") for HTTP

if __name__ == "__main__":                                  # script entry
    main()                                                  # run
```
Test client (ran against the file above as a stdio subprocess):
```python
# tariff_test.py - spawn the server exactly like a host would and exercise it
import asyncio                                              # runtime
import sys                                                  # current python path
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # stdio transport

async def main() -> None:                                   # driver
    p = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])   # spawn command
    async with stdio_client(p) as (r, w):                   # starts the process
        async with ClientSession(r, w) as s:                # protocol session
            init = await s.initialize()                     # handshake
            print(init.serverInfo.name, "|", init.instructions)   # tariff-server | Look up ...
            print((await s.call_tool("get_duty_rate", {"hs_code": "6403"})).structuredContent)   # {'hs_code': '6403', 'rate_pct': 10.0}
            print((await s.call_tool("landed_cost", {"price": 100, "hs_code": "6109"})).structuredContent)   # {'result': 112.0}
            bad = await s.call_tool("get_duty_rate", {"hs_code": "64"})   # invalid input
            print(bad.isError, bad.content[0].text)         # True, "hs_code must be 4 digits, got '64'"

asyncio.run(main())                                         # run
```
FastAPI integration: expose the same `mcp` over HTTP with `app.mount("/tariff", mcp.streamable_http_app())` (topic 012). Token usage: the tool descriptions and schemas above cost input tokens on every LLM call; keep docstrings to one precise sentence. Logs showed `INFO tariff startup`, `lookup 6403` and `shutdown` on stderr only.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Consumes this server | MCP adapter loads its tools into a graph (verify package/version) | MCP tools integration (verify) | `MCPServerStdio(params={"command": ..., "args": [...]})` (class import verified earlier) | MCP workbench/tool adapter (verify) |
| Who writes the server | Same `FastMCP` file works for all | Same | Same | Same |
| Server-side framework dependency | None | None | None | None |

The point: **the server is framework-agnostic**; write it once, consume it from any of the four.

---

## ⚠️ Common Mistakes
❌ Mistake 1: `print()` for debugging in a stdio server.
✅ Correct: `logging` to stderr. stdout is the protocol channel and extra text breaks it.

❌ Mistake 2: Opening a DB connection inside each tool call.
✅ Correct: Create pools in `lifespan`, read them from `ctx.request_context.lifespan_context`.

❌ Mistake 3: Returning dicts with no schema / swallowing errors.
✅ Correct: Typed or Pydantic return values; raise `ValueError` with a fix-it message (becomes `isError`).

❌ Mistake 4: Blocking I/O in `async def` tools.
✅ Correct: Use async drivers or `asyncio.to_thread`.

❌ Mistake 5: Never testing outside a host.
✅ Correct: A small stdio/in-memory client test as above, run in CI.

---

## 🧠 Tricky Interview Question
"Your server works in your test client but Claude Desktop shows 'server disconnected' right after start. What do you check?"

Answer: First stdout pollution: any `print`, library banner or warning written to stdout breaks JSON-RPC framing; send logs to stderr and read the host's MCP log file. Second, the command: the host starts a process without your shell environment, so use absolute paths to the interpreter/script (or `uv --directory`), and put required env vars in the config's `env`. Third, import errors or missing dependencies in that interpreter (the host may use a different Python than your venv). Run the exact config command by hand to reproduce.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `FastMCP` do for you?
A1: Builds JSON schemas from type hints, registers tools/resources/prompts via decorators, handles the protocol and transport.

Q2: [Medium] How do you share a DB pool across tool calls?
A2: Use the `lifespan` async context manager; whatever it yields is available as `ctx.request_context.lifespan_context`.

Q3: [Hard] How are exceptions in a tool reported?
A3: FastMCP catches them and returns a result with `isError=true` and the message text (we saw `Error executing tool get_duty_rate: ...`), so the LLM can self-correct.

Q4: [Hard] How do you test a server without an LLM?
A4: Use an MCP client: stdio subprocess (real launch path) or in-memory `create_connected_server_and_client_session`. Assert on `structuredContent`, `isError` and listings.

Q5: [System Design] Ship the same server to desktop users and a cloud agent.
A5: One codebase, two entry points: stdio for desktop (`mcp.run()`), Streamable HTTP with stateless mode mounted in FastAPI for cloud, auth in front, shared logic in plain modules, same test suite for both.

---

## 💰 Cost Impact
The server itself makes no LLM calls (unless you use sampling), so its cost is compute only. What you control is **LLM input tokens**: number of tools, description length and result size. A concise `get_duty_rate` description plus schema is on the order of 100 tokens (approximate; count with your tokenizer). Return compact structured data instead of long prose, and cache static lookups in lifespan state.

---

## 🔷 When to Use
✅ Use when:
- You want tools/data reusable by many hosts and frameworks
- You need a clean boundary and tests between the agent and your systems

❌ Avoid when:
- A single script-local function is enough (a plain framework tool is simpler)
- You cannot secure the data the server exposes

---

## 📊 Visual Diagram
```
 tariff_server.py
 +-------------------------------------------------+
 | FastMCP("tariff-server", lifespan=...)          |
 |   lifespan: load rates / open DB   --> AppState |
 |   @tool get_duty_rate  (validate, typed)        |
 |   @tool landed_cost                             |
 |   @resource tariff://rates/{hs_code}            |
 |   @prompt review                                |
 |   logging -> stderr                             |
 +--------------------^----------------------------+
                      | stdio / streamable-http
   Claude Desktop | FastAPI agent | pytest client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FastMCP | High-level Python server API | Python का high-level server API |
| lifespan | Startup/shutdown context for shared state | startup/shutdown पर साझा state |
| stderr logging | Logs not touching protocol stdout | protocol से अलग logs |
| structuredContent | Typed tool result | typed नतीजा |
| Entry point | `mcp.run()` start | server शुरू करने की जगह |

---

## ⚡ 3-Line Summary
English: `FastMCP` plus typed decorated functions gives you a working server fast. Add lifespan state, validation, stderr logging and a client-based test. The same file serves every host and framework.
Hindi: `FastMCP` और typed decorated functions से server जल्दी बनता है। Lifespan state, validation, stderr logging और client-based test जोड़ें। वही file हर host और framework के लिए चलती है।

---

## ➡️ Next Topic
**011. Building MCP Server (Node.js)** - the same tariff server in TypeScript/JavaScript, to see how the SDKs differ.

---
