---

# 16. MCP with LangChain
# हिंदी में: LangChain के साथ MCP
# Framework: MCP
# Already Known: No

> Verified against: `langchain-mcp-adapters` 0.3.2, `langchain-core` 1.8.0, `langgraph` 1.2.22, `mcp` 1.30.0. Tool loading, tool invocation, interceptors, name prefixes and a LangGraph agent with a **fake chat model** were run locally. Real LLM calls (ChatAnthropic / ChatOpenAI): not run - need API keys.

---

## 🔵 Simple Definition (2-3 lines)
`langchain-mcp-adapters` converts every tool of an MCP server into a normal LangChain `StructuredTool`. `MultiServerMCPClient` connects to one or many servers (stdio, SSE, streamable HTTP, websocket) and `await client.get_tools()` returns the list you can bind to any chat model or agent.

## 🔵 सरल परिभाषा (Hindi)
`langchain-mcp-adapters` MCP server के हर tool को सामान्य LangChain `StructuredTool` में बदल देता है। `MultiServerMCPClient` एक या कई servers (stdio, SSE, streamable HTTP, websocket) से जुड़ता है और `await client.get_tools()` वह list देता है जिसे किसी भी chat model या agent से bind किया जा सकता है।

---

## 🔴 Problem it Solves
Without the adapter you would write one `@tool` wrapper per MCP tool, manually copy schemas and manage sessions. When the server adds a tool you must edit code. The adapter generates the wrappers from `tools/list` and handles the session lifecycle.

## 🔴 यह क्यों बना? (Hindi)
Adapter के बिना हर MCP tool के लिए अलग `@tool` wrapper लिखना, schema कॉपी करना और session संभालना पड़ता। Server में tool जुड़े तो code बदलना पड़ता। Adapter `tools/list` से wrappers खुद बना देता है और session lifecycle संभालता है।

---

## 🟢 How it Works

```
Step 1 -> MultiServerMCPClient({"tariff": {command, args, transport:"stdio"}})
Step 2 -> client.get_tools() opens a session, runs tools/list
Step 3 -> each MCP tool becomes StructuredTool(name, description, args_schema)
Step 4 -> agent/model.bind_tools(tools) -> model emits tool_calls
Step 5 -> tool.ainvoke(args) -> (interceptors) -> MCP tools/call
Step 6 -> result returned as content blocks; errors come back as text (handle_tool_errors=True)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> MultiServerMCPClient({"tariff": {command, args, transport:"stdio"}})
Step 2 -> client.get_tools() session खोलकर tools/list चलाता है
Step 3 -> हर MCP tool StructuredTool(name, description, args_schema) बन जाता है
Step 4 -> agent/model.bind_tools(tools) -> model tool_calls देता है
Step 5 -> tool.ainvoke(args) -> (interceptors) -> MCP tools/call
Step 6 -> result content blocks में आता है; errors text में लौटते हैं (handle_tool_errors=True)
```

---

## 🟡 Real World Example
**Tariff Agent** in an existing LangChain/LangGraph app: the customs MCP server exposes `get_tariff_rate` and `calc_duty`. The team already has a ReAct agent; they just replace their hand-written tool list with `await client.get_tools()`.

## 🟡 Real Example Hindi mein
**Tariff Agent** पहले से बने LangChain/LangGraph app में: customs MCP server `get_tariff_rate` और `calc_duty` देता है। Team के पास ReAct agent पहले से है; वे बस हाथ से लिखी tool list की जगह `await client.get_tools()` लगा देते हैं।

---

## 💻 Code Example — Basic
```python
# tariff_server.py - same MCP server as note 015 (FastMCP, stdio, two tools)
from mcp.server.fastmcp import FastMCP                      # server helper
mcp = FastMCP("tariff")                                     # server name
RATES: dict[str, float] = {"6109.10": 20.0, "7318.15": 10.0}  # demo data

@mcp.tool()                                                 # tool 1
def get_tariff_rate(hs_code: str) -> str:                   # typed arg
    """Return duty percent for an HS code."""               # description
    if hs_code not in RATES:                                # validate
        raise ValueError(f"unknown HS code {hs_code}")      # -> isError result
    return f"{RATES[hs_code]}%"                             # text result

@mcp.tool()                                                 # tool 2
def calc_duty(value_usd: float, rate_percent: float) -> float:
    """Duty = value * rate / 100."""
    return value_usd * rate_percent / 100

if __name__ == "__main__":                                  # entry
    mcp.run()                                               # stdio
```

```python
# basic_lc.py - load MCP tools as LangChain tools (ran)
import asyncio, sys                                         # stdlib
from langchain_mcp_adapters.client import MultiServerMCPClient   # multi-server client

async def main() -> None:                                   # async entry
    client = MultiServerMCPClient({                         # name -> connection config
        "tariff": {"command": sys.executable,               # how to start the server
                   "args": ["tariff_server.py"], "transport": "stdio"}})
    tools = await client.get_tools()                        # tools/list -> LangChain tools
    print([(t.name, type(t).__name__) for t in tools])      # StructuredTool x2
    print(await tools[0].ainvoke({"hs_code": "6109.10"}))   # -> [{'type': 'text', 'text': '20.0%', ...}]
    try:
        print(await tools[0].ainvoke({"hs_code": "zz"}))    # bad input
    except Exception as e:                                  # not raised in 0.3.2
        print("ERR", type(e).__name__, e)                   # (not reached)
    # observed: the bad call returned text "Error executing tool get_tariff_rate: unknown HS code zz"
    # because handle_tool_errors=True (default) turns MCP errors into text for the model.

asyncio.run(main())                                         # run
```

## 💻 Code Example — Advanced
```python
# lc_agent_api.py - interceptor (audit), prefixes, FastAPI, fake model for offline test (all ran)
import sys                                                  # interpreter path
from contextlib import asynccontextmanager                  # lifespan helper
from typing import Any, AsyncIterator                       # hints
from fastapi import FastAPI, HTTPException                  # web layer
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage               # fake model replies
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent           # deprecated alias in LangGraph 1.x, still works
from pydantic import BaseModel

class FakeModel(GenericFakeChatModel):                      # test model that accepts bind_tools
    def bind_tools(self, tools: Any, **kw: Any) -> "FakeModel":
        return self                                         # ignore tools; replies are scripted

async def audit(request: Any, handler: Any) -> Any:         # interceptor wraps every tool call
    print("AUDIT", request.name, request.args)              # fields: name,args,server_name,headers,runtime
    return await handler(request)                           # continue the call (could block/modify here)

class Ask(BaseModel):                                       # request body
    question: str

@asynccontextmanager                                        # build agent once
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = MultiServerMCPClient(                          # servers dict
        {"tariff": {"command": sys.executable, "args": ["tariff_server.py"], "transport": "stdio"}},
        tool_interceptors=[audit],                          # audit/auth/retry hooks
        tool_name_prefix=True,                              # tools become tariff_get_tariff_rate (no collisions)
    )
    tools = await client.get_tools()                        # discover
    model = app.state.model                                 # real: ChatAnthropic(...) / ChatOpenAI(...)
    app.state.agent = create_react_agent(model, tools)      # ReAct loop over MCP tools
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/ask")                                           # async endpoint
async def ask(body: Ask) -> dict[str, str]:
    try:
        out = await app.state.agent.ainvoke({"messages": [("user", body.question)]})
    except Exception as exc:                                # model/network failures
        raise HTTPException(502, f"agent failed: {type(exc).__name__}") from exc
    last = out["messages"][-1]                              # final AI message
    usage = getattr(last, "usage_metadata", None)           # real models fill token counts; fake = None
    return {"answer": str(last.content), "usage": str(usage)}
```
Verified pieces: `tool_interceptors=[audit]` printed `AUDIT get_tariff_rate {'hs_code': '6109.10'}`; `tool_name_prefix=True` produced `tariff_get_tariff_rate`; a ReAct agent with a scripted fake model called the MCP tool and answered "Duty is 20%". The tool message content is a list of text blocks, not a bare string. Token usage: read `usage_metadata` on real model replies. Async: all calls are `ainvoke`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| MCP integration | `langchain-mcp-adapters` -> tools (verified) | MCP tools support (verify docs) | `MCPServerStdio/StreamableHttp` (verified) | MCP workbench (verify) |
| Multi-server | `MultiServerMCPClient` (verified) | verify | list of `mcp_servers` | verify |
| Hooks | `tool_interceptors` (verified) | verify | `tool_filter`, `require_approval` | verify |
| Error model | text result by default (verified) | verify | `failure_error_function` param | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using `get_tools()` per request.
✅ Correct: Load once at startup; it spawns/connects to the server.

❌ Mistake 2: Two servers with the same tool name.
✅ Correct: `tool_name_prefix=True` (or distinct names).

❌ Mistake 3: Expecting a Python exception for bad tool input.
✅ Correct: With `handle_tool_errors=True` the model gets an error text; set it to `False` if your code must catch errors.

❌ Mistake 4: Treating the tool output as a `str`.
✅ Correct: It is a list of content blocks; extract `text`.

---

## 🧠 Tricky Interview Question
"Your LangGraph agent keeps calling `get_tariff_rate` with a bad HS code and never recovers. Why, and what do you change?"

Answer: The error comes back as plain text in a ToolMessage. If the system prompt does not say what to do, the model may repeat the same call. Fixes: return actionable errors from the server ("valid format is NNNN.NN"), add a retry budget or a recursion limit in the graph, validate with a pydantic schema server-side, and add an interceptor that counts identical failing calls.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `get_tools()` return?
A1: A list of LangChain `StructuredTool` objects generated from `tools/list`.

Q2: [Medium] Why use `MultiServerMCPClient`?
A2: One object configures several servers with different transports and merges their tools; prefixes avoid name clashes.

Q3: [Hard] stdio sessions in the client: one per call or persistent?
A3: Tools from `get_tools()` are, per the adapter docs, stateless - a short-lived session per call (verify for your version; the `session(server_name)` method exists in 0.3.2). For stateful servers use `client.session("tariff")` as a context manager and `load_mcp_tools(session)`.

Q4: [Hard] How do you add auth headers per user?
A4: HTTP transports take `headers` in the connection config; interceptors expose `request.headers` for per-call changes (check adapter docs for exact usage).

Q5: [System Design] Agent platform with 20 MCP servers.
A5: Registry-driven config, load tools per tenant/task, prefix names, interceptor for audit and rate limits, circuit breakers on unhealthy servers, cache tool lists, trace each tool call.

---

## 💰 Cost Impact
Every bound tool adds its name, description and schema to each model call. 20 tools can add thousands of input tokens per turn (estimate - measure with your tokenizer). Tips: load only relevant servers per route, shorten descriptions, cache prompts, use a cheap model for tool selection. LangGraph recursion limit caps worst-case turns.

---

## 🔷 When to Use
✅ Use when:
- You already run LangChain/LangGraph
- Tools live in shared MCP servers

❌ Avoid when:
- A single local Python function suffices (`@tool` is simpler)

---

## 📊 Visual Diagram
```
 FastAPI -> create_react_agent(model, tools)
                |            ^
        tool_calls          |  ToolMessage (content blocks)
                v            |
        [interceptor: audit] -> StructuredTool -> MCP session -> tariff_server.py
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MultiServerMCPClient | Client for many MCP servers | कई MCP servers का client |
| StructuredTool | LangChain tool with schema | schema वाला LangChain tool |
| interceptor | Hook around each tool call | हर tool call के आसपास hook |
| tool_name_prefix | Prefix names with server name | नाम में server का prefix |
| handle_tool_errors | Return errors as text | errors को text में लौटाना |

---

## ⚡ 3-Line Summary
English: The adapter turns MCP tools into LangChain tools. Load once, prefix names, use interceptors for audit and auth. Errors return as text by default.
Hindi: Adapter MCP tools को LangChain tools बना देता है। एक बार load करें, नामों में prefix लगाएं, audit और auth के लिए interceptors लें। Errors default में text की तरह लौटते हैं।

---

## ➡️ Next Topic
**017. MCP with LangGraph** - build the graph yourself (StateGraph + ToolNode) with a persistent MCP session.

---
