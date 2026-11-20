---

# 6. MCP Tools — Deep Dive
# हिंदी में: MCP Tools — गहराई से
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python), `@modelcontextprotocol/sdk` 1.32.2 (Node), `fastapi` 0.163.0, `pydantic` (installed with mcp). Server and client ran offline over an in-memory connection and over stdio. No real LLM was called (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
An MCP tool is a named function with a JSON-Schema input (and optionally output) that a server lists via `tools/list` and runs via `tools/call`. The result is a list of content blocks, optionally plus `structuredContent`, and an `isError` flag. The model decides when to call it, so descriptions, schemas and annotations matter a lot.

## 🔵 सरल परिभाषा (Hindi)
MCP tool एक नाम वाला function है जिसका input (और optionally output) JSON Schema में होता है। Server उसे `tools/list` से दिखाता है और `tools/call` से चलाता है। Result content blocks की list होती है, साथ में optional `structuredContent` और `isError` flag। Tool कब चलाना है यह model तय करता है, इसलिए description, schema और annotations बहुत मायने रखते हैं।

---

## 🔴 Problem it Solves
Hand-written function-calling glue gives the LLM a vague schema, free-form text results and no standard way to say "this failed". MCP tools standardise: discoverable schema, typed output, an error channel the model can read and recover from, hints about danger (`readOnlyHint`, `destructiveHint`), and progress/log notifications for slow work.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखा function-calling glue LLM को धुंधला schema, free-form text result और "fail हुआ" बताने का कोई standard तरीका नहीं देता। MCP tools standard देते हैं: खोजा जा सकने वाला schema, typed output, ऐसा error channel जिसे model पढ़कर सुधार सके, ख़तरे के hints (`readOnlyHint`, `destructiveHint`), और धीमे काम के लिए progress/log notifications।

---

## 🟢 How it Works

```
Step 1 -> client sends tools/list -> server returns name, description, inputSchema,
          (outputSchema, annotations, title)
Step 2 -> host gives these to the LLM as its tool list
Step 3 -> LLM emits a tool call {name, arguments}
Step 4 -> host (after policy / human approval) sends tools/call
Step 5 -> server validates arguments against inputSchema, runs the function
Step 6 -> result = content[] (+ structuredContent), isError true/false
Step 7 -> host appends the result to the conversation; LLM reads it, may retry
```

Two kinds of errors (important):
```
Protocol error  -> bad request / unknown tool (JSON-RPC error)       -> client exception
Tool error      -> the tool ran/validated and failed: isError = true -> LLM can read the text and fix its call
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> client tools/list भेजता है -> server name, description, inputSchema,
          (outputSchema, annotations, title) लौटाता है
Step 2 -> host इन्हें LLM की tool list बनाकर देता है
Step 3 -> LLM tool call बनाता है {name, arguments}
Step 4 -> host (policy / human approval के बाद) tools/call भेजता है
Step 5 -> server arguments को inputSchema से validate करके function चलाता है
Step 6 -> result = content[] (+ structuredContent), isError true/false
Step 7 -> host result को बातचीत में जोड़ता है; LLM पढ़ता है, ज़रूरत हो तो दोबारा कोशिश करता है
```

दो तरह की errors: **Protocol error** (गलत request / unknown tool) client में exception बनती है; **Tool error** (`isError=true`) में text LLM को वापस जाता है ताकि वह अपनी call सुधार सके।

---

## 🟡 Real World Example
**Tariff Agent**: tool `duty(hs_code)` is read-only and idempotent, so annotated `readOnlyHint=True` and the host can auto-approve it. A tool `file_declaration(...)` would be `destructiveHint=True` and always needs a human click. If the LLM sends an invalid HS code, the tool returns `isError=true` with "unknown HS code", and the model retries with a corrected code instead of the whole run crashing.

## 🟡 Real Example Hindi mein
**Tariff Agent**: tool `duty(hs_code)` read-only और idempotent है, इसलिए `readOnlyHint=True`, और host उसे अपने-आप approve कर सकता है। `file_declaration(...)` जैसा tool `destructiveHint=True` होगा और हमेशा human click माँगेगा। LLM गलत HS code भेजे तो tool `isError=true` के साथ "unknown HS code" लौटाता है और model सही code से दोबारा कोशिश करता है, पूरा run crash नहीं होता।

---

## 💻 Code Example — Basic
```python
# tools_basic.py - minimal typed tool + error handling (ran: unknown code -> isError True)
from mcp.server.fastmcp import FastMCP                      # high-level server

mcp = FastMCP("tariff-tools")                               # server name
RATES: dict[str, float] = {"8517": 0.0, "6403": 10.0}       # demo data

@mcp.tool()                                                 # register as a tool
def get_duty_rate(hs_code: str) -> float:                   # type hints -> inputSchema + outputSchema
    """Return duty percent for an HS code (4 digits)."""    # shown to the LLM: make it precise
    if hs_code not in RATES:                                # validate business rule
        raise ValueError(f"unknown HS code {hs_code}")      # SDK -> CallToolResult(isError=True, text=...)
    return RATES[hs_code]                                   # returned as structuredContent {"result": 10.0}

if __name__ == "__main__":                                  # entry
    mcp.run()                                               # stdio
```
Client side (verified): `res = await session.call_tool("get_duty_rate", {"hs_code": "8517"})` gave `res.structuredContent == {'result': 0.0}`; with code `"1"` we got `res.isError == True` and text `Error executing tool get_duty_rate: unknown HS code 1`.

## 💻 Code Example — Advanced
```python
# tools_adv.py - Pydantic output model, annotations, progress + logging, async, and a client test
import asyncio                                              # run the demo
from pydantic import BaseModel, Field                       # typed output with validation
from mcp.server.fastmcp import FastMCP, Context             # server + request context
from mcp.types import ToolAnnotations                       # safety hints for the host
from mcp.shared.memory import create_connected_server_and_client_session as connect   # in-memory client

mcp = FastMCP("tariff-rich")                                # server

class Duty(BaseModel):                                      # structured result -> outputSchema
    hs_code: str                                            # echo of the input
    rate_pct: float = Field(ge=0, le=100)                   # constraint is part of the schema
    note: str = ""                                          # optional free text

@mcp.tool(                                                  # register with metadata
    title="Duty lookup",                                    # human-friendly name for UIs
    annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))   # hints (untrusted by spec - not security!)
async def duty(hs_code: str, ctx: Context) -> Duty:         # ctx injected by the SDK
    """Look up the duty for an HS code."""
    await ctx.report_progress(1, 2, "looking up")           # progress notification (needs client progress token)
    await ctx.info("lookup start")                          # log notification to the client
    return Duty(hs_code=hs_code, rate_pct=10.0)             # replace with an async DB call

async def log_cb(p) -> None:                                # client-side log handler
    print("LOG", p.data)                                    # prints "lookup start"

async def prog(done: float, total: float | None, msg: str | None) -> None:   # client-side progress handler
    print("PROG", done, total, msg)                         # prints 1.0 2.0 looking up

async def main() -> None:                                   # demo driver
    async with connect(mcp._mcp_server, logging_callback=log_cb) as c:   # client wired to server
        tool = (await c.list_tools()).tools[0]              # discover
        print(tool.name, tool.title, tool.annotations.readOnlyHint, list(tool.outputSchema["properties"]))   # metadata
        ok = await c.call_tool("duty", {"hs_code": "85"}, progress_callback=prog)   # success path
        print(ok.structuredContent)                         # {'hs_code': '85', 'rate_pct': 10.0, 'note': ''}
        bad = await c.call_tool("duty", {})                 # missing argument
        print(bad.isError, bad.content[0].text[:60])        # True, validation error text (LLM can read it)

asyncio.run(main())                                         # run
```
Ran output (abridged): `duty Duty lookup True ['hs_code', 'rate_pct', 'note']`, `PROG 1.0 2.0 looking up`, `LOG lookup start`, `{'hs_code': '85', 'rate_pct': 10.0, 'note': ''}`, `True Error executing tool duty: 1 validation error for dutyArguments`.

FastAPI integration (pattern verified in topic 012): `app.mount("/tariff", mcp.streamable_http_app())` with `stateless_http=True` on the `FastMCP(...)` and `async with mcp.session_manager.run()` inside FastAPI's lifespan. Token usage: the `inputSchema`, `description` and `title` of every tool are sent to the LLM on every request, so keep them tight. Node SDK equivalent (ran): `server.registerTool("get_duty_rate", {title, description, inputSchema: {hs_code: z.string().regex(/^\d{4}$/)}, outputSchema, annotations}, handler)`; invalid input there returned `isError: true` with `MCP error -32602: Input validation error`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Use MCP tools | Via MCP adapter -> LangChain tools (not verified here) | MCP tool integration (verify docs) | `MCPServerStdio` / `MCPServerStreamableHttp` (verified import earlier) | MCP workbench (verify docs) |
| Uses `outputSchema` | Usually only text content (verify) | Usually text (verify) | Verify | Verify |
| Honors `readOnlyHint` for approval | You build it in a node/interrupt | You build it | Approval options exist on tools (verify) | You build it |
| Error feedback to LLM | Tool message with error text | Verify | Verify | Verify |

Treat framework cells marked "verify" as unconfirmed; check each framework's current docs before an interview demo.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Raising exceptions for expected bad input and expecting a 500-style failure.
✅ Correct: In FastMCP a raised exception becomes `isError=true` text. That is good: the LLM sees it and retries. Write error messages that say how to fix the call.

❌ Mistake 2: Trusting annotations for security.
✅ Correct: Annotations are hints from a possibly untrusted server. Enforce approval and permissions in the host.

❌ Mistake 3: Vague descriptions ("does stuff") and untyped `dict` arguments.
✅ Correct: Typed parameters, enums, regex/range constraints, one precise sentence of when to use it.

❌ Mistake 4: Blocking calls (`requests.get`, heavy CPU) inside `async def` tools.
✅ Correct: Use async clients or `asyncio.to_thread`, otherwise one slow tool blocks the server's event loop.

❌ Mistake 5: Returning huge payloads.
✅ Correct: Paginate or return IDs plus a resource link; big results are re-billed as input tokens on every turn.

---

## 🧠 Tricky Interview Question
"The model keeps calling `get_duty_rate` with `'8517.12'` and your server says unknown code. Do you fix the prompt or the tool?"

Answer: Fix the tool first. Put the format in the schema (`pattern`, description with an example) so invalid input is rejected with a clear message, and normalise safe variants server-side (strip dots). Return an `isError` message such as "hs_code must be 4 digits, e.g. 8517; got 8517.12" so the model can self-correct in one retry. Prompt changes are a last step because the schema travels with every tool list and is the most reliable contract.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does a tool result contain?
A1: `content` (text/image/resource blocks), optional `structuredContent` matching `outputSchema`, and `isError`.

Q2: [Medium] Protocol error vs tool error?
A2: Protocol errors (unknown tool, malformed request) are JSON-RPC errors. Tool errors are normal results with `isError=true` so the LLM can read and recover. Note: in the Node SDK, input validation failures also came back as `isError=true` text in our run.

Q3: [Hard] How do you handle a 2-minute tool?
A3: Make it async, send progress notifications, set client-side timeouts, make it cancellable/idempotent, or return a job ID and expose a status tool/resource instead of blocking.

Q4: [Hard] Why can tool annotations not be trusted?
A4: A malicious server can claim `readOnlyHint=True` on a destructive tool. Only use hints for UX; enforce policy by server allow-list and per-tool approval in the host.

Q5: [System Design] How would you expose 200 internal APIs as tools?
A5: Do not list 200 tools to the LLM (token cost, worse selection). Group by domain into several servers, add a search/"describe tool" layer or have the host filter tools per task, namespace names, and measure tool-selection accuracy.

---

## 💰 Cost Impact
Every listed tool adds its name + description + schema to the input of every LLM call. As a rough rule (approximate, measure with your tokenizer) a small tool costs on the order of 100-300 input tokens, so 50 tools can add several thousand tokens per turn. Tips: expose only needed tools per task, short descriptions, return compact structured results, enable prompt caching for the stable tool list where your provider supports it (verify provider docs).

---

## 🔷 When to Use
✅ Use when:
- The model must take an action or fetch data on demand
- You need a validated, typed contract and readable errors

❌ Avoid when:
- The data is static reference material (use a resource)
- The tool does irreversible work with no approval step
- You would expose hundreds of tools at once

---

## 📊 Visual Diagram
```
 LLM --"call duty(hs_code='85')"--> HOST --tools/call--> SERVER
                                                 |
                       validate vs inputSchema --+--> fail -> isError=true (text) --+
                                                 |                                  |
                       run function (async) -----+--> progress/log notifications -->|
                                                 |                                  v
                                                 +--> content[] + structuredContent -> HOST -> LLM
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inputSchema | JSON Schema of arguments | arguments का schema |
| outputSchema | JSON Schema of structured result | structured result का schema |
| structuredContent | Typed JSON result | typed JSON नतीजा |
| isError | Flag: tool failed, text explains | tool fail हुआ का flag |
| Annotations | Hints (readOnly, destructive...) | सुरक्षा संकेत (hints) |
| Progress notification | Updates during long calls | लंबे काम के दौरान प्रगति सूचना |

---

## ⚡ 3-Line Summary
English: A tool is a typed, discoverable function with a readable error channel. Good schemas and descriptions decide how well the model uses it. Annotations are hints, never security.
Hindi: Tool एक typed, खोजा जा सकने वाला function है जिसका error channel पढ़ा जा सकता है। अच्छे schema और description से model उसे बेहतर इस्तेमाल करता है। Annotations सिर्फ़ संकेत हैं, security नहीं।

---

## ➡️ Next Topic
**007. MCP Resources - Deep Dive** - how to expose documents and data (static and templated) so the app, not the model, decides what to load.

---
