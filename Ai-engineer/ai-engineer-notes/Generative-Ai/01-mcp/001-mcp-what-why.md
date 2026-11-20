---

# 1. MCP — What + Why
# हिंदी में: MCP — क्या है और क्यों
# Framework: MCP (all 4 frameworks can consume it)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python, `FastMCP`), `mcp` 2.3.0 (renamed `MCPServer`), `@modelcontextprotocol/sdk` 1.32.2. Offline stdio + in-memory runs done. Real LLM calls: not run - needs an API key.

---

## 🔵 Simple Definition (2-3 lines)
MCP (Model Context Protocol) is an open, JSON-RPC based standard that lets any AI application (host) talk to any tool/data provider (server) in one common way. Think "USB-C for AI tools": write a tool once as an MCP server and Claude Desktop, your LangGraph agent, CrewAI, OpenAI Agents SDK or AutoGen can all use it.

## 🔵 सरल परिभाषा (Hindi)
MCP (Model Context Protocol) एक open, JSON-RPC आधारित standard है, जिससे कोई भी AI application (host) किसी भी tool/data provider (server) से एक ही तरीके से बात कर सकता है। इसे "AI tools का USB-C" समझिए: tool एक बार MCP server के रूप में लिखिए और Claude Desktop, LangGraph, CrewAI, OpenAI Agents SDK, AutoGen सब उसे इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves
Without MCP, every (app x tool) pair needs custom glue: N apps times M tools = N x M integrations. Each framework has its own tool schema, auth, and error format. A Tariff DB tool written for LangChain must be rewritten for CrewAI. MCP turns N x M into N + M: each app implements the MCP client once, each tool implements the MCP server once.

## 🔴 यह क्यों बना? (Hindi)
MCP के बिना हर (app x tool) जोड़ी के लिए अलग glue code चाहिए: N apps x M tools = N x M integrations। हर framework का अपना tool schema, auth और error format होता है। LangChain के लिए लिखा Tariff DB tool CrewAI के लिए दोबारा लिखना पड़ता है। MCP से N x M घटकर N + M हो जाता है: हर app एक बार MCP client बनाता है, हर tool एक बार MCP server।

---

## 🟢 How it Works

```
Step 1 → Host app (agent) starts an MCP client for each server it trusts
Step 2 → Client sends  initialize  (protocol version + capabilities)
Step 3 → Server answers with its capabilities (tools / resources / prompts)
Step 4 → Client sends  tools/list  -> agent gets names + JSON schemas
Step 5 → LLM picks a tool -> client sends  tools/call  {name, arguments}
Step 6 → Server runs the code, returns content (+ isError flag)
Step 7 → Result goes back to the LLM as an observation; loop continues
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Host app (agent) हर भरोसेमंद server के लिए एक MCP client बनाता है
Step 2 → Client  initialize  भेजता है (protocol version + capabilities)
Step 3 → Server अपनी capabilities बताता है (tools / resources / prompts)
Step 4 → Client  tools/list  भेजता है -> agent को नाम + JSON schema मिलते हैं
Step 5 → LLM tool चुनता है -> client  tools/call  {name, arguments} भेजता है
Step 6 → Server code चलाकर content (+ isError flag) लौटाता है
Step 7 → नतीजा LLM को observation बनकर जाता है; loop चलता रहता है
```

---

## 🟡 Real World Example
**Tariff Agent**: the customs team has a Postgres DB of HS codes and duty rates. One engineer writes `tariff-server` (MCP). Now the in-house LangGraph agent, the analyst's Claude Desktop, and a CrewAI research crew all call `get_duty_rate` with zero extra glue. When the rate table changes, one server is updated for everyone.

**Other**: GitHub MCP server (issues/PRs), Slack, Postgres, filesystem, Playwright browser.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs टीम के पास HS codes और duty rates का Postgres DB है। एक engineer `tariff-server` (MCP) लिखता है। अब company का LangGraph agent, analyst का Claude Desktop और CrewAI research crew सब बिना extra glue के `get_duty_rate` call करते हैं। Rate table बदले तो सिर्फ़ एक server update होता है।

**और उदाहरण**: GitHub MCP server (issues/PRs), Slack, Postgres, filesystem, Playwright browser।

---

## 💻 Code Example — Basic
```python
# basic_server.py - smallest useful MCP server (verified: mcp 1.30.0)
from mcp.server.fastmcp import FastMCP          # high-level server helper

mcp = FastMCP("tariff-server")                   # name shown to clients

RATES: dict[str, float] = {"8517": 0.0, "6403": 10.0}   # HS code -> duty percent

@mcp.tool()                                      # expose this function as an MCP tool
def get_duty_rate(hs_code: str) -> float:        # type hints become the JSON schema
    """Return duty percent for an HS code."""    # docstring becomes the tool description
    if hs_code not in RATES:                     # validate input
        raise ValueError(f"unknown HS code {hs_code}")  # becomes isError=True result
    return RATES[hs_code]                        # return value is sent to the client

if __name__ == "__main__":                       # run as a script
    mcp.run()                                    # default transport = stdio
```

```python
# basic_client.py - talk to the server above (ran offline, output below)
import asyncio, sys                              # asyncio for the async client
from mcp import ClientSession, StdioServerParameters   # client session + launch params
from mcp.client.stdio import stdio_client        # spawns server as a subprocess

async def main() -> None:                        # async entry point
    params = StdioServerParameters(command=sys.executable, args=["basic_server.py"])  # how to start server
    async with stdio_client(params) as (read, write):          # open stdio pipes
        async with ClientSession(read, write) as session:      # protocol session
            init = await session.initialize()                  # handshake
            print(init.protocolVersion, init.serverInfo.name)  # -> 2025-11-25 tariff-server
            tools = await session.list_tools()                 # discover tools
            print([t.name for t in tools.tools])               # -> ['get_duty_rate']
            ok = await session.call_tool("get_duty_rate", {"hs_code": "8517"})  # call it
            print(ok.structuredContent)                        # -> {'result': 0.0}
            bad = await session.call_tool("get_duty_rate", {"hs_code": "1"})    # error path
            print(bad.isError, bad.content[0].text)           # -> True Error executing tool ...

asyncio.run(main())                              # run the client
```

## 💻 Code Example — Advanced
```python
# api.py - MCP server mounted inside a FastAPI app (ran with uvicorn + real HTTP client)
import contextlib                                # for the lifespan helper
from fastapi import FastAPI                      # your normal web app
from mcp.server.fastmcp import FastMCP           # MCP server helper

mcp = FastMCP("tariff-http", stateless_http=True, json_response=True)  # stateless = easy to scale

@mcp.tool()                                      # tool for agents
async def add_duty(base: float, rate: float) -> float:   # async tool, typed
    """Duty amount = base value x rate percent."""
    if rate < 0:                                 # input guard
        raise ValueError("rate must be >= 0")    # surfaces as tool error, not a crash
    return round(base * rate / 100, 2)           # compute duty

@contextlib.asynccontextmanager                  # FastAPI lifespan wrapper
async def lifespan(app: FastAPI):                # MCP session manager must be running
    async with mcp.session_manager.run():        # starts MCP task group
        yield                                    # app serves requests here

app = FastAPI(lifespan=lifespan)                 # main web app
app.mount("/tools", mcp.streamable_http_app())   # MCP endpoint -> POST /tools/mcp

@app.get("/health")                              # normal REST route still works
def health() -> dict[str, str]:                  # typed response
    return {"ok": "yes"}                         # liveness probe
```
Run: `uvicorn api:app --port 8000`, then client URL = `http://127.0.0.1:8000/tools/mcp` (a verified add-tool variant returned `{'result': 5}` via `streamablehttp_client`).

Async: both client and server above are async. Error handling: raise in the tool -> client sees `isError=True`. Token usage: tool schemas are sent to the LLM on every call, so 10 tools x ~150 tokens = ~1.5k tokens of overhead per request (estimate).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Consume MCP servers | Via `langchain-mcp-adapters` (convert to LangChain tools) | Via MCP tools integration (check current docs) | Built-in MCP server classes in Agents SDK | MCP workbench/tools extension (`autogen-ext`) |
| Native tool format | LangChain `@tool` | `@tool` / BaseTool | `@function_tool` | Python functions / `FunctionTool` |
| Without MCP | Rewrite per app | Rewrite per app | Rewrite per app | Rewrite per app |
| Best for | Stateful graphs | Role-based crews | Simple handoff agents | Multi-agent chats |
Exact adapter APIs change fast: not run here - verify in each framework's docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Calling MCP "just another function-calling API".
✅ Correct: Function calling is the LLM feature; MCP is the wire protocol between app and tool provider. They work together.

❌ Mistake 2: `print()` inside a stdio server.
✅ Correct: stdout is the protocol channel; a stray print corrupts JSON-RPC. Log to stderr / `ctx.info`.

❌ Mistake 3: Importing `mcp.server.fastmcp` on `mcp>=2`.
✅ Correct: v2 renamed it to `from mcp.server.mcpserver import MCPServer` (we saw a ModuleNotFoundError telling us so). Pin `mcp<2` or migrate.

---

## 🧠 Tricky Interview Question
"If every framework already supports function calling, why do you need MCP?"

Answer: Function calling only describes how an LLM asks for a call. It says nothing about how tools are discovered, versioned, authenticated, run out-of-process, or shared. MCP standardises discovery (`tools/list`), invocation (`tools/call`), transport (stdio/HTTP), capability negotiation and extra primitives (resources, prompts, sampling). Result: tools become separately deployable, language-independent services, and you avoid N x M glue. The trade-off is an extra process/network hop and a new attack surface (tool poisoning, prompt injection through tool output).

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is MCP?
A1: An open JSON-RPC protocol from Anthropic that standardises how AI apps connect to tools, data and prompts.

Q2: [Medium] What does MCP replace?
A2: Per-framework custom tool wrappers. It reduces N x M integrations to N + M.

Q3: [Hard] Which message starts every MCP session and why?
A3: `initialize`: client and server exchange protocol version and capabilities; features are only used if both sides declared them. We saw `2025-11-25` negotiated with mcp 1.30.0.

Q4: [Hard] What are the security risks of MCP?
A4: Malicious/compromised servers (tool poisoning in descriptions), prompt injection via tool results, over-broad permissions, token passthrough. Mitigate with allowlisted servers, least privilege, human approval for writes, sandboxing, output sanitising.

Q5: [System Design] Design tool access for 5 agent teams using 20 internal APIs.
A5: One MCP server per domain (tariff, customs-docs, billing) behind a gateway with OAuth, streamable HTTP + stateless mode for horizontal scaling, per-team tool allowlists, audit logs, rate limits, versioned tool names. Teams' agents (any framework) connect as clients.

---

## 💰 Cost Impact
Formula: extra input tokens per LLM call = (number of tool schemas) x (avg schema tokens). Roughly 100-300 tokens per tool (approximate, depends on descriptions - measure with your tokenizer). 30 tools can add several thousand tokens to every call.
Tips: expose only needed tools per agent, keep descriptions short, cache the tool list, use prompt caching for the static tool prefix, avoid returning huge payloads from tools.

---

## 🔷 When to Use
✅ Use when:
- Same tool needed by multiple apps/frameworks/teams
- Tools must run in separate process/trust boundary
- You want to use ecosystem servers (GitHub, Postgres)

❌ Avoid when:
- One script, one app, 2 simple tools (a plain function is enough)
- Ultra low latency in-process calls

---

## 📊 Visual Diagram
```
 +------------------+        JSON-RPC        +------------------+
 |  HOST (agent)    |  <------------------>  |   MCP SERVER     |
 | LangGraph/Claude |   stdio or HTTP        | tariff-server    |
 |  +------------+  |                        |  tools/resources |
 |  | MCP client |  |  initialize            |  prompts         |
 |  +------------+  |  tools/list            |        |         |
 +------------------+  tools/call            +--------|---------+
                                                       v
                                                 Tariff DB / API
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MCP | Model Context Protocol | मॉडल संदर्भ प्रोटोकॉल |
| Host | App that runs the LLM + clients | होस्ट ऐप |
| Server | Process exposing tools/data | tools देने वाला server |
| JSON-RPC | Request/response message format | संदेश format |
| Capability | Feature declared during handshake | क्षमता |

---

## ⚡ 3-Line Summary
English: MCP is a standard protocol between AI apps and tool servers. Write a tool once, use it from any framework. It cuts N x M integrations to N + M but adds security duties.
Hindi: MCP AI apps और tool servers के बीच standard protocol है। Tool एक बार लिखो, किसी भी framework में चलाओ। यह N x M integrations को N + M कर देता है, पर security की ज़िम्मेदारी बढ़ती है।

---

## ➡️ Next Topic
**002. MCP vs Regular Tools** - to decide exactly when MCP is worth the extra moving part compared with plain function tools.

---
