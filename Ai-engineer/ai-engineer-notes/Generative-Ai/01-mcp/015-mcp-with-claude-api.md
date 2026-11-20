---

# 15. MCP with Claude API
# हिंदी में: Claude API के साथ MCP
# Framework: MCP
# Already Known: No

> Verified against: `anthropic` 2.8.0, `mcp` 1.30.0 (Python 3.13). The stdio MCP server, the MCP client session, `async_mcp_tool`, `tool_runner` and the FastAPI route were run locally against a **mock HTTP transport** that plays Claude's replies. Real Claude calls and the hosted MCP connector against a real remote server: **not run - needs ANTHROPIC_API_KEY and a public MCP server**. The connector request body was only captured, not sent to Anthropic. Note: `anthropic` 2.x uses `httpx2` (not `httpx`) for custom HTTP clients.

---

## 🔵 Simple Definition (2-3 lines)
There are two ways to give Claude MCP tools. (1) **Client-side**: your Python code is the MCP client, lists the server's tools, converts them with `async_mcp_tool`, and the SDK's `tool_runner` runs the agent loop. (2) **MCP connector**: you pass a remote server URL in `mcp_servers` and Anthropic's API itself connects to that server (beta).

## 🔵 सरल परिभाषा (Hindi)
Claude को MCP tools देने के दो तरीके हैं। (1) **Client-side**: आपका Python code खुद MCP client है, server के tools list करता है, `async_mcp_tool` से convert करता है और SDK का `tool_runner` agent loop चलाता है। (2) **MCP connector**: आप `mcp_servers` में remote server का URL देते हैं और Anthropic का API खुद उस server से जुड़ता है (beta)।

---

## 🔴 Problem it Solves
Without MCP you hand-write a JSON tool schema and a dispatch `if/elif` for every tool, per app. When the Tariff team adds a tool, every agent must be redeployed. With MCP the tool list comes from the server at runtime and the same server works with Claude, OpenAI or LangGraph agents.

## 🔴 यह क्यों बना? (Hindi)
MCP के बिना हर app में हर tool के लिए हाथ से JSON schema और `if/elif` dispatch लिखना पड़ता है। Tariff team नया tool जोड़े तो हर agent दोबारा deploy करना पड़ता है। MCP में tool list runtime पर server से आती है और वही server Claude, OpenAI या LangGraph agents के साथ चलता है।

---

## 🟢 How it Works

```
Client-side (tool_runner)
Step 1 -> stdio_client spawns the MCP server, ClientSession.initialize()
Step 2 -> session.list_tools() -> [Tool(name, description, inputSchema)]
Step 3 -> async_mcp_tool(tool, session) -> Claude tool (input_schema)
Step 4 -> client.beta.messages.tool_runner(tools=[...]) sends request
Step 5 -> Claude returns stop_reason=tool_use
Step 6 -> runner calls session.call_tool(...) and sends tool_result back
Step 7 -> Claude returns end_turn with the final text

MCP connector (server-side)
Step 1 -> request has mcp_servers=[{type:url,url,name,authorization_token}]
Step 2 -> request has tools=[{type:mcp_toolset, mcp_server_name:...}]
Step 3 -> Anthropic connects to the URL and runs the tool calls for you
```

## 🟢 कैसे काम करता है? (Hindi)

```
Client-side (tool_runner)
Step 1 -> stdio_client MCP server spawn करता है, ClientSession.initialize()
Step 2 -> session.list_tools() -> [Tool(name, description, inputSchema)]
Step 3 -> async_mcp_tool(tool, session) -> Claude tool (input_schema)
Step 4 -> client.beta.messages.tool_runner(tools=[...]) request भेजता है
Step 5 -> Claude stop_reason=tool_use लौटाता है
Step 6 -> runner session.call_tool(...) चलाकर tool_result वापस भेजता है
Step 7 -> Claude end_turn के साथ final text देता है

MCP connector (server-side)
Step 1 -> request में mcp_servers=[{type:url,url,name,authorization_token}]
Step 2 -> request में tools=[{type:mcp_toolset, mcp_server_name:...}]
Step 3 -> Anthropic खुद URL से जुड़कर tool calls चलाता है
```

---

## 🟡 Real World Example
**Tariff Agent**: customs analyst asks "What is the duty on 6109.10 goods worth 1000 USD?". Claude calls `get_tariff_rate("6109.10")` (20%) then `calc_duty`. The tariff team owns the MCP server; the agent code never changes when tools are added.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs analyst पूछता है "6109.10 माल की कीमत 1000 USD हो तो duty कितनी?"। Claude `get_tariff_rate("6109.10")` (20%) और फिर `calc_duty` बुलाता है। MCP server tariff team का है; tool जोड़ने पर agent code नहीं बदलता।

---

## 💻 Code Example — Basic
```python
# tariff_server.py - the MCP server (ran over stdio)
from mcp.server.fastmcp import FastMCP                      # high-level server helper

mcp = FastMCP("tariff")                                     # server name shown to clients
RATES: dict[str, float] = {"6109.10": 20.0, "7318.15": 10.0}  # demo rate table

@mcp.tool()                                                 # expose as an MCP tool
def get_tariff_rate(hs_code: str) -> str:                   # typed arg -> JSON schema
    """Return duty percent for an HS code."""               # docstring = tool description
    if hs_code not in RATES:                                # validate untrusted input
        raise ValueError(f"unknown HS code {hs_code}")      # becomes isError=True result
    return f"{RATES[hs_code]}%"                             # plain text result

@mcp.tool()                                                 # second tool
def calc_duty(value_usd: float, rate_percent: float) -> float:  # typed args
    """Duty = value * rate / 100."""                        # description
    return value_usd * rate_percent / 100                   # pure arithmetic

if __name__ == "__main__":                                  # script entry
    mcp.run()                                               # default transport = stdio
```

```python
# basic_claude_mcp.py - MCP tools -> Claude tool_runner (ran with a mock transport)
import asyncio, sys, json                                   # stdlib
import httpx2, anthropic                                    # anthropic 2.x needs httpx2 clients
from mcp import ClientSession, StdioServerParameters        # MCP client pieces
from mcp.client.stdio import stdio_client                   # spawn server over stdio
from anthropic.lib.tools.mcp import async_mcp_tool          # MCP tool -> Claude tool helper

def msg(content: list[dict], stop: str) -> dict:            # build a fake Messages API reply
    return {"id": "msg_1", "type": "message", "role": "assistant", "model": "claude-sonnet-4-5",
            "content": content, "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 5}}   # usage numbers are fake test data

def handler(req: httpx2.Request) -> httpx2.Response:        # plays "Claude" in the test
    body = json.loads(req.content)                          # request Claude would receive
    done = any(m["role"] == "user" and isinstance(m["content"], list)
               and m["content"][0].get("type") == "tool_result" for m in body["messages"])
    if done:                                                # tool result present -> final answer
        return httpx2.Response(200, json=msg([{"type": "text", "text": "Duty is 20%"}], "end_turn"))
    return httpx2.Response(200, json=msg([{"type": "tool_use", "id": "tu_1",
        "name": "get_tariff_rate", "input": {"hs_code": "6109.10"}}], "tool_use"))

async def main() -> None:                                   # async entry point
    # for a real run: anthropic.AsyncAnthropic() reads ANTHROPIC_API_KEY (not run here)
    claude = anthropic.AsyncAnthropic(api_key="x",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)))
    params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
    async with stdio_client(params) as (read, write):       # start the MCP server
        async with ClientSession(read, write) as session:   # protocol session
            await session.initialize()                      # handshake
            listed = await session.list_tools()             # discover tools
            tools = [async_mcp_tool(t, session) for t in listed.tools]   # convert for Claude
            runner = claude.beta.messages.tool_runner(      # SDK runs the tool loop
                model="claude-sonnet-4-5", max_tokens=256, tools=tools,
                messages=[{"role": "user", "content": "duty for 6109.10?"}])
            async for m in runner:                          # one iteration per Claude reply
                print(m.stop_reason, [b.type for b in m.content])   # tool_use then end_turn

asyncio.run(main())                                         # output seen: tool_use ['tool_use'] / end_turn ['text']
```

## 💻 Code Example — Advanced
```python
# claude_mcp_api.py - FastAPI + lifespan-owned MCP session + token accounting (route ran via TestClient + mock)
import os, sys                                              # env + interpreter path
from contextlib import AsyncExitStack, asynccontextmanager  # keep stdio session alive for app lifetime
from typing import Any, AsyncIterator                       # type hints
import anthropic                                            # Claude SDK
from anthropic.lib.tools.mcp import async_mcp_tool          # MCP -> Claude tool
from fastapi import FastAPI, HTTPException                  # web layer
from mcp import ClientSession, StdioServerParameters        # MCP client
from mcp.client.stdio import stdio_client                   # stdio transport
from pydantic import BaseModel                              # request/response models

MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5") # configurable; check current model ids

class Ask(BaseModel):                                       # request body
    question: str

class Answer(BaseModel):                                    # response body
    answer: str
    input_tokens: int
    output_tokens: int
    turns: int

@asynccontextmanager                                        # start once, reuse for every request
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncExitStack() as stack:                   # closes server on shutdown
        params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()                          # handshake
        listed = await session.list_tools()                 # discover once at startup
        app.state.tools = [async_mcp_tool(t, session) for t in listed.tools]
        if not hasattr(app.state, "claude"):                # tests inject a mock client first
            app.state.claude = anthropic.AsyncAnthropic(max_retries=2, timeout=30.0)
        yield                                               # app serves requests here

app = FastAPI(lifespan=lifespan)                            # attach lifespan

@app.post("/ask", response_model=Answer)                    # async endpoint
async def ask(body: Ask) -> Answer:
    claude: anthropic.AsyncAnthropic = app.state.claude
    runner = claude.beta.messages.tool_runner(              # agent loop with a hard cap
        model=MODEL, max_tokens=512, max_iterations=6,      # max_iterations stops runaway loops
        system="You are a tariff assistant. Use tools for rates and duty math.",
        tools=app.state.tools, messages=[{"role": "user", "content": body.question}])
    tin = tout = turns = 0                                  # token usage counters
    last: Any = None
    try:
        async for message in runner:                        # each loop = one model call
            turns += 1
            tin += message.usage.input_tokens               # sum input tokens across turns
            tout += message.usage.output_tokens
            last = message
    except anthropic.RateLimitError as exc:                 # 429 from Anthropic
        raise HTTPException(429, "Claude rate limit") from exc
    except anthropic.APIStatusError as exc:                 # other 4xx/5xx
        raise HTTPException(502, f"Claude error {exc.status_code}") from exc
    except anthropic.APIConnectionError as exc:             # network down
        raise HTTPException(503, "Cannot reach Claude") from exc
    if last is None:                                        # defensive
        raise HTTPException(500, "no response")
    text = "".join(b.text for b in last.content if b.type == "text")
    return Answer(answer=text, input_tokens=tin, output_tokens=tout, turns=turns)
```
Test result (mock Claude, so tokens are fake test values): `{'answer': 'Duty is 20%', 'input_tokens': 20, 'output_tokens': 10, 'turns': 2}`.

```python
# connector.py - server-side MCP connector payload (captured via mock, NOT sent to Anthropic)
import anthropic                                            # SDK
claude = anthropic.AsyncAnthropic()                         # needs ANTHROPIC_API_KEY (not run)
# await claude.beta.messages.create(
#     model="claude-sonnet-4-5", max_tokens=512,
#     messages=[{"role": "user", "content": "duty for 6109.10?"}],
#     mcp_servers=[{"type": "url", "url": "https://mcp.example.com/mcp",
#                   "name": "tariff", "authorization_token": "TOKEN"}],   # must be a public HTTPS server
#     tools=[{"type": "mcp_toolset", "mcp_server_name": "tariff",
#             "default_config": {"enabled": False},                       # allow-list pattern
#             "configs": {"get_tariff_rate": {"enabled": True}}}],
#     betas=["mcp-client-2025-11-20"])                                    # beta header seen in docs - verify current value
```
Token usage: every tool schema is sent on every turn, so input tokens grow with tool count. Error handling: tool errors come back as `isError` content that Claude can read and retry; transport errors map to 429/502/503. Async: the whole path is `async`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Claude + MCP | `ChatAnthropic` + `langchain-mcp-adapters` tools | MCP tools via CrewAI MCP support (verify docs) | Agents SDK is model-agnostic; Claude needs a LiteLLM/custom model (verify) | MCP workbench + Anthropic client (verify) |
| Who runs the loop | Your graph (ToolNode) | Crew | `Runner` | Agent runtime |
| Direct Claude SDK | n/a | n/a | n/a | n/a (this note uses the Anthropic SDK itself) |
| Remote server connected by | your process | your process | your process | your process |

Only the Anthropic SDK rows were run; other cells are pointers, not verified claims.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Opening a new stdio server per request.
✅ Correct: Start the session once in `lifespan` and reuse it.

❌ Mistake 2: No `max_iterations` on the runner.
✅ Correct: Cap loops (we used 6) so a confused model cannot loop forever and burn tokens.

❌ Mistake 3: Exposing every server tool to Claude.
✅ Correct: Filter the list (or `default_config.enabled=false` in the connector) - fewer tools = fewer tokens and less risk.

❌ Mistake 4: Passing `httpx.AsyncClient` to anthropic 2.x.
✅ Correct: It raises `TypeError`; use `httpx2`.

---

## 🧠 Tricky Interview Question
"Your agent works with the tool_runner but the connector approach fails against `http://localhost:8000/mcp`. Why?"

Answer: The connector runs on Anthropic's servers, which cannot reach your localhost or a private network. The server must be publicly reachable over HTTPS (and only the tools part of MCP is supported by the connector - verify in current docs). Use client-side MCP for local or private servers, the connector for public, authenticated, remote ones.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How does Claude learn what MCP tools exist?
A1: Your client calls `tools/list`; the tool names, descriptions and JSON schemas are passed to Claude as its `tools`.

Q2: [Medium] `async_mcp_tool` vs the connector?
A2: `async_mcp_tool` keeps the MCP connection in your process (private networks, all transports you support). The connector makes Anthropic connect to a public URL for you (less code, less control).

Q3: [Hard] A tool raises an exception. What does Claude see?
A3: FastMCP turns it into a result with `isError=True` and text like "Error executing tool get_tariff_rate: unknown HS code x" (observed). Claude sees this as a tool result and can correct its input.

Q4: [Hard] How do you cut token cost with 40 tools?
A4: Filter to the needed subset per task, shorten descriptions, cache the stable prefix (tool definitions) with prompt caching, and route simple questions to a smaller model.

Q5: [System Design] Multi-tenant Tariff API on Claude + MCP.
A5: One MCP session pool per worker (HTTP transport for shared servers), per-tenant auth tokens forwarded as headers, `max_iterations` and timeouts, per-tenant token budgets from `usage`, retries only on 429/5xx, tracing per tool call.

---

## 💰 Cost Impact
Tokens per run = (system + all tool schemas + messages) x number of model turns, plus output. A tariff question needs about 2 turns (tool call, final answer). Formula: `cost = turns * input_tokens * price_in + output_tokens * price_out`. Prices change - take them from Anthropic's pricing page (approximate, verify). Tips: fewer tools, prompt caching for the static tools block, `max_tokens` caps, smaller model for classification steps.

---

## 🔷 When to Use
✅ Use client-side MCP when:
- Servers are local or in a private network
- You need to log, filter or approve each tool call

✅ Use the connector when:
- The MCP server is public HTTPS and you want minimal code

❌ Avoid when:
- You have 2-3 simple in-process functions (plain tool definitions are simpler)

---

## 📊 Visual Diagram
```
 User -> FastAPI /ask -> tool_runner --messages+tools--> Claude API
                             ^                               |
                             |  tool_use                     v
                       ClientSession <--- call_tool --- [decision]
                             |
                      stdio  v
                     tariff_server.py (get_tariff_rate, calc_duty)
 Connector variant:  Claude API --(HTTPS)--> remote MCP server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_runner | SDK helper that loops tool calls | tool calls का loop चलाने वाला helper |
| async_mcp_tool | Converts MCP tool to Claude tool | MCP tool को Claude tool बनाना |
| mcp_servers | Connector list of remote servers | remote servers की सूची |
| mcp_toolset | Tools entry enabling a server's tools | server के tools चालू करने की entry |
| isError | Flag marking failed tool result | tool fail होने का flag |

---

## ⚡ 3-Line Summary
English: Use `async_mcp_tool` + `tool_runner` when your code is the MCP client. Use the `mcp_servers` connector for public remote servers. Cap iterations, filter tools, track `usage`.
Hindi: जब आपका code MCP client हो तब `async_mcp_tool` + `tool_runner` इस्तेमाल करें। Public remote servers के लिए `mcp_servers` connector लें। Iterations सीमित रखें, tools filter करें, `usage` ट्रैक करें।

---

## ➡️ Next Topic
**016. MCP with LangChain** - the same tariff server, but consumed as LangChain tools through `langchain-mcp-adapters`.

---
