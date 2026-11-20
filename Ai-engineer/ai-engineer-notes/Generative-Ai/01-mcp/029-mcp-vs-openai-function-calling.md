---

# 29. MCP vs OpenAI Function Calling
# हिंदी में: MCP बनाम OpenAI Function Calling
# Framework: MCP (compared with OpenAI SDK / All)
# Already Known: No

> Verified offline against `mcp 2.3.0` (note: in mcp 2.x the class is `MCPServer`, not `FastMCP`), `openai-agents 0.24.0`, `fastapi 0.163.0`, `pydantic 2.14.3`. Real LLM calls were NOT run (no API key); only the tool/protocol layer was executed.

---

## 🔵 Simple Definition (2-3 lines)
**Function calling** is a feature of an LLM API: you send a JSON schema of your functions inside one request, and the model replies with "call this function with these arguments". **MCP (Model Context Protocol)** is an open protocol between a *client* (your agent) and a *server* (a process that owns tools, resources and prompts). They are not rivals: MCP decides *where tools live and how they are discovered*; function calling decides *how the model asks to use one*.

## 🔵 सरल परिभाषा (Hindi)
**Function calling** LLM API का एक feature है: आप एक request में अपने functions का JSON schema भेजते हैं और model जवाब देता है "यह function इन arguments के साथ चलाओ"। **MCP (Model Context Protocol)** एक open protocol है जो *client* (आपका agent) और *server* (वह process जिसके पास tools, resources और prompts हैं) के बीच चलता है। ये प्रतिद्वंद्वी नहीं हैं: MCP तय करता है *tools कहाँ रहते हैं और कैसे खोजे जाते हैं*; function calling तय करता है *model उन्हें कैसे माँगता है*।

---

## 🔴 Problem it Solves
With plain function calling every app re-implements the same tools: a Tariff Agent, a Slack bot and an IDE assistant each carry their own copy of `get_tariff_rate()`. Schemas are pasted by hand, tools are hard-coded into one codebase, and a tool written for OpenAI must be re-wrapped for Anthropic or Gemini. MCP solves the **N x M integration problem**: write the tool once as an MCP server and any MCP-capable client can discover and call it.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ function calling के साथ हर app वही tools दोबारा लिखता है: Tariff Agent, Slack bot और IDE assistant, तीनों में `get_tariff_rate()` की अपनी-अपनी copy होती है। Schema हाथ से paste होते हैं, tools एक ही codebase में hard-code रहते हैं, और OpenAI के लिए लिखा tool Anthropic या Gemini के लिए दोबारा wrap करना पड़ता है। MCP **N x M integration problem** हल करता है: tool एक बार MCP server के रूप में लिखो और कोई भी MCP client उसे खोजकर चला सकता है।

---

## 🟢 How it Works

```
FUNCTION CALLING (inside one app)
Step 1 → App hard-codes tools=[{name, description, parameters}] in the request
Step 2 → LLM returns tool_call(name, arguments-json)
Step 3 → App's own code runs the function, sends the result back
Step 4 → LLM writes the final answer

MCP (tools live in a separate server)
Step 1 → Client connects to server (stdio / streamable-http), handshake
Step 2 → Client calls tools/list  -> gets names + JSON schemas at runtime
Step 3 → Client converts those schemas into the LLM's function-calling format
Step 4 → LLM returns tool_call(...)  (still function calling!)
Step 5 → Client sends tools/call to the MCP server, gets the result
Step 6 → Result goes back to the LLM -> final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
FUNCTION CALLING (एक ही app के अंदर)
Step 1 → App request में tools=[{name, description, parameters}] hard-code करता है
Step 2 → LLM tool_call(name, arguments-json) लौटाता है
Step 3 → App का अपना code function चलाता है, result वापस भेजता है
Step 4 → LLM अंतिम जवाब लिखता है

MCP (tools अलग server में रहते हैं)
Step 1 → Client server से जुड़ता है (stdio / streamable-http), handshake
Step 2 → Client tools/list बुलाता है -> runtime पर names + JSON schemas मिलते हैं
Step 3 → Client उन schemas को LLM के function-calling format में बदलता है
Step 4 → LLM tool_call(...) लौटाता है (यह अब भी function calling है!)
Step 5 → Client MCP server को tools/call भेजता है, result पाता है
Step 6 → Result LLM को वापस जाता है -> अंतिम जवाब
```

Key insight: **MCP sits underneath function calling, not instead of it.** The model never speaks MCP; your client translates between the two. / मुख्य बात: **MCP, function calling के नीचे बैठता है, उसकी जगह नहीं लेता।** Model कभी MCP नहीं बोलता; आपका client दोनों के बीच अनुवाद करता है।

---

## 🟡 Real World Example
**Tariff Agent**: the customs team owns a `get_tariff_rate(hs_code, country)` tool that reads the government schedule. With function calling the Tariff Agent, the Finance Copilot and the Slack bot each paste a copy. With MCP the customs team ships one `tariff-mcp` server; all three clients connect and always see the latest schema. **Research Agent**: a GitHub MCP server gives every agent repo search without anyone writing GitHub wrappers.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs team के पास `get_tariff_rate(hs_code, country)` tool है जो सरकारी schedule पढ़ता है। Function calling में Tariff Agent, Finance Copilot और Slack bot हर एक अपनी copy paste करते हैं। MCP में customs team एक `tariff-mcp` server देती है; तीनों clients जुड़ते हैं और हमेशा ताज़ा schema देखते हैं। **Research Agent**: GitHub MCP server हर agent को repo search देता है, किसी को GitHub wrapper नहीं लिखना पड़ता।

---

## 💻 Code Example — Basic
```python
# Same tool, two ways. Runs offline (no API key): only the tool layer is exercised.
import asyncio                                         # run the async MCP client
from mcp.server.mcpserver import MCPServer             # mcp 2.x server class (was FastMCP in 1.x)
from mcp.client import Client                          # mcp 2.x client with in-memory transport

HS_RATES: dict[str, float] = {"6109": 12.0, "8517": 0.0}  # tiny fake duty table (percent)

def get_tariff_rate(hs_code: str) -> float:            # the ONE real implementation
    """Return import duty percent for an HS code."""   # docstring becomes the tool description
    if hs_code not in HS_RATES:                        # unknown code -> clear error
        raise ValueError(f"unknown HS code {hs_code}") # surfaces as is_error=True in MCP
    return HS_RATES[hs_code]                           # happy path

# ---- WAY 1: plain function calling: you hand-write the JSON schema -----------
FC_TOOL: dict = {                                      # OpenAI chat-completions style tool
    "type": "function",                                # tool kind
    "function": {                                      # function block
        "name": "get_tariff_rate",                     # name the model will emit
        "description": "Return import duty percent for an HS code.",  # hand-copied text
        "parameters": {                                # hand-written JSON schema
            "type": "object",                          # object of args
            "properties": {"hs_code": {"type": "string"}},  # one string arg
            "required": ["hs_code"],                   # mandatory
        },
    },
}

# ---- WAY 2: MCP: schema is generated from the type hints ----------------------
server = MCPServer("tariff")                           # name shown in handshake
server.tool()(get_tariff_rate)                         # register same function as an MCP tool

async def main() -> None:                              # demo driver
    async with Client(server) as client:               # in-memory client<->server session
        tools = (await client.list_tools()).tools      # tools/list, discovered at runtime
        print([t.name for t in tools])                 # ['get_tariff_rate']
        print(tools[0].input_schema["properties"])     # schema generated, not hand-written
        ok = await client.call_tool("get_tariff_rate", {"hs_code": "6109"})  # tools/call
        print(ok.is_error, ok.content[0].text)         # False, "12.0"
        bad = await client.call_tool("get_tariff_rate", {"hs_code": "0000"}) # raises inside tool
        print(bad.is_error, bad.content[0].text)       # True, "Error executing tool ..."

if __name__ == "__main__":                             # script entry
    asyncio.run(main())                                # start event loop
```
Run result (offline, mcp 2.3.0): names `['get_tariff_rate']`, schema keys `['hs_code']`, success `is_error=False`, bad code `is_error=True` — the exception did **not** crash the client; it came back as data the LLM can read. / नतीजा: exception client को crash नहीं करता, डेटा बनकर वापस आता है जिसे LLM पढ़ सकता है।

## 💻 Code Example — Advanced
```python
# Production shape: MCP tools are discovered at runtime and ADAPTED to function calling.
# Plus a FastAPI endpoint, async, type hints, error handling and a token-usage guard.
from __future__ import annotations                     # allow forward type hints
import json                                            # serialise tool results
from typing import Any                                 # generic JSON type
from fastapi import FastAPI, HTTPException             # web layer
from pydantic import BaseModel, Field                  # request validation
from mcp.server.mcpserver import MCPServer             # tool server
from mcp.client import Client                          # tool client

server = MCPServer("tariff")                           # the "customs team" server

@server.tool()                                         # schema auto-built from hints
def get_tariff_rate(hs_code: str, country: str = "IN") -> dict[str, Any]:
    """Return import duty percent for an HS code and destination country."""
    if not hs_code.isdigit():                          # validate input early
        raise ValueError("hs_code must be digits only")
    return {"hs_code": hs_code, "country": country, "rate_pct": 12.0}  # fake data

def to_openai_tools(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    """Convert MCP tool descriptors into OpenAI function-calling tool dicts."""
    return [                                           # one dict per MCP tool
        {
            "type": "function",                        # function-calling envelope
            "function": {
                "name": t.name,                        # name from the server
                "description": t.description or "",    # description from the server
                "parameters": t.input_schema,          # JSON schema from the server
            },
        }
        for t in mcp_tools                             # every discovered tool
    ]

async def dispatch(client: Client, name: str, args: dict[str, Any]) -> str:
    """Execute one model-requested tool call through MCP."""
    result = await client.call_tool(name, args)        # tools/call over the protocol
    text = result.content[0].text if result.content else ""  # first text block
    if result.is_error:                                # tool failed -> tell the model, do not crash
        return json.dumps({"error": text[:300]})       # truncate error to save tokens
    return text                                        # success payload

class Ask(BaseModel):                                  # request body
    hs_code: str = Field(min_length=4, max_length=10)  # basic HS length guard

app = FastAPI(title="Tariff gateway")                  # FastAPI app

@app.post("/tools/preview")                            # shows what the LLM would receive
async def preview(body: Ask) -> dict[str, Any]:
    try:
        async with Client(server) as client:           # connect (in-memory here; stdio/http in prod)
            tools = (await client.list_tools()).tools  # discovery
            fc_tools = to_openai_tools(tools)          # adapt for the LLM request
            # Pretend the LLM answered with this tool_call (a real run would call the LLM here)
            out = await dispatch(client, "get_tariff_rate", {"hs_code": body.hs_code})
        approx_tokens = len(json.dumps(fc_tools)) // 4 # rough chars/4 estimate, NOT a real count
        return {"tools_sent_to_llm": fc_tools, "tool_result": out, "approx_schema_tokens": approx_tokens}
    except Exception as exc:                           # any transport/protocol failure
        raise HTTPException(status_code=502, detail=f"tool server error: {exc}") from exc
```
Verified with `fastapi.testclient.TestClient`: POST `{"hs_code":"6109"}` returned the converted tool list and a JSON result with `rate_pct: 12.0`; `"abcd"` returned an `{"error": ...}` string (not a 500). The LLM step itself was **not run — needs an OpenAI/Anthropic key**. / LLM वाला step **चलाया नहीं गया — API key चाहिए**।

**Async note**: every MCP client method is `async`; never call them from sync code. The in-memory `Client(server)` is for tests; production uses `Client("python tariff_server.py")`-style stdio or an HTTP URL (check `help(Client)` for your version).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Native function calling | Yes via `bind_tools` on chat models | Yes, tools are `@tool` / `BaseTool` | Yes, `@function_tool` | Yes, `FunctionTool` / plain callables |
| MCP client support | `langchain-mcp-adapters` package (separate) | MCP tool adapters (extra package, verify version) | Built in: `MCPServerStdio`, `MCPServerStreamableHttp`, `HostedMCPTool` | `autogen-ext` MCP workbench (extra package) |
| Tool discovery at runtime | Only through the adapter | Only through the adapter | `Agent(mcp_servers=[...])` lists tools each run | Through the MCP workbench |
| Schema source | Pydantic / type hints | Type hints | Type hints + docstring | Type hints |
| Best for | Stateful graphs | Role-based crews | Light agent loops + handoffs | Multi-agent chat |
Entries for non-verified libraries are from memory of public docs; **not run, verify before relying**. / जो libraries install नहीं हुईं उनकी entries docs की याददाश्त से हैं, भरोसे से पहले जाँचें।

---

## ⚠️ Common Mistakes
❌ Mistake 1: Saying "MCP replaces function calling".
✅ Correct: The LLM still emits a function-call; MCP is the transport that fetches schemas and executes the call on a remote server.

❌ Mistake 2: Putting 40 MCP tools straight into every request.
✅ Correct: Every discovered tool schema is sent as input tokens on every turn. Filter to the few tools the agent needs (allow-list per agent).

❌ Mistake 3: Using MCP for a single private helper in one app.
✅ Correct: A local `@function_tool` is simpler, faster (no process hop) and easier to debug. Use MCP when a tool is shared, owned by another team, or must be language-independent.

❌ Mistake 4 (version trap): Copying `from mcp.server.fastmcp import FastMCP` from old blog posts.
✅ Correct: In `mcp 2.x` this import fails with ModuleNotFoundError; use `from mcp.server.mcpserver import MCPServer` or pin `mcp<2`. Always check the installed version.

---

## 🧠 Tricky Interview Question
"Our team already uses OpenAI function calling in production. A teammate says we must rewrite everything in MCP to be 'future-proof'. Do you agree?"

Answer: No, not a rewrite. Keep the model-facing layer (function calling) unchanged. Extract only the tools that are **shared across apps or owned by other teams** into MCP servers, and add a thin adapter (like `to_openai_tools` above) so those tools appear in the same `tools=[...]` list as local ones. Trade-offs to state: MCP adds a network/process hop (latency, failure modes, auth), a larger attack surface (a remote server can return prompt-injected text), and more tokens if you expose every tool. Gains: one implementation, runtime discovery, independent deploys, and reuse across vendors. Decide per tool, not per codebase. / जवाब: rewrite नहीं; सिर्फ वे tools MCP में डालें जो कई apps में shared हैं, बाकी local रखें।

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What is the difference between function calling and MCP?
A1: Function calling is how a model *requests* a tool within one API call. MCP is a protocol for a client to *discover and execute* tools hosted by a separate server. MCP uses function calling underneath.

Q2: (Medium) Who executes the tool in each approach?
A2: Function calling: your own application code runs it after the model returns the call. MCP: your client forwards `tools/call` to the MCP server process, which runs it. (Hosted MCP tools in the OpenAI Responses API are the exception: OpenAI's side calls the remote server.)

Q3: (Hard) What are the security differences?
A3: Function calling keeps tools in your trust boundary. MCP adds a boundary: server auth (OAuth/tokens), tool-description poisoning (a malicious server can write instructions in a description), tool-result prompt injection, and over-broad permissions. Mitigate with allow-lists, read-only hints, human approval for write tools, and pinning server versions.

Q4: (Hard) Why can MCP increase cost?
A4: Discovered schemas are re-sent as input tokens on every model turn, and a verbose description multiplies across turns. 30 tools x ~150 tokens is ~4,500 tokens per turn (illustrative figure). Fix: filter tools per agent, shorten descriptions, use prompt caching for the stable tool prefix.

Q5: (System Design) Design tool access for 5 agents owned by 3 teams.
A5: Each team publishes its tools as an MCP server over streamable HTTP behind an API gateway (auth, rate limits, audit log). A shared client library handles connect/reconnect, tool allow-lists per agent, timeouts and an adapter to function calling. Read-only tools are auto-approved; write tools need approval. Version servers semantically and run contract tests on `tools/list`.

---

## 💰 Cost Impact
- Formula: `tokens_per_turn_overhead = sum(tokens(tool_schema_i))` for every exposed tool, paid on **every** model call in the loop. Total overhead = that x number of turns.
- Rough sizing: a short schema is often 60-200 tokens (approximate; measure with your tokenizer). 10 tools over a 5-turn run is therefore thousands of extra input tokens.
- MCP itself (JSON-RPC to your own server) costs no model tokens; the cost is the schema text and the result text you feed back.
- Tips: allow-list tools per agent, truncate tool results, cache the static tool prefix, prefer a small model for routing turns. Pricing changes often: check the provider's pricing page.

---

## 🔷 When to Use
✅ Use MCP when:
- A tool is shared by several apps or agents
- Another team owns the tool and deploys independently
- You want runtime discovery and vendor-neutral tools

✅ Use plain function calling when:
- The tool is private to one app and tightly coupled to its data
- Latency matters and you want no extra process hop

❌ Avoid MCP when:
- You would run a whole server for one trivial helper
- You cannot secure and monitor the server

---

## 📊 Visual Diagram
```
          FUNCTION CALLING                         MCP
   +------------------+               +------------------+    stdio / HTTP    +--------------+
   |   Your App       |               |   Your App       |<------------------>|  MCP Server  |
   |  tools=[...]     |               |  (MCP client)    |  tools/list        |  tariff      |
   |  runs functions  |               |                  |  tools/call        |  tools +     |
   +--------+---------+               +--------+---------+                    |  resources   |
            |  tool_call JSON                  |  tool_call JSON              +--------------+
            v                                  v
        +-------+                          +-------+
        |  LLM  |                          |  LLM  |   (model still uses function calling)
        +-------+                          +-------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function calling | Model asks to run a described function | model का function चलाने का अनुरोध |
| MCP | Open protocol for tools/resources/prompts | tools/resources के लिए open protocol |
| MCP client / server | Agent side / tool-hosting side | agent वाला पक्ष / tool वाला पक्ष |
| tools/list, tools/call | JSON-RPC methods to discover and run tools | tools खोजने और चलाने के methods |
| Transport | stdio, SSE, streamable HTTP | संचार का तरीका |
| N x M problem | Every app x every tool integrations | हर app x हर tool का जोड़ |

---

## ⚡ 3-Line Summary
English: Function calling is the model asking for a tool; MCP is the protocol that hosts, discovers and runs tools remotely.
English: MCP sits under function calling; the client converts MCP schemas into function-call tools.
English: Use MCP for shared or cross-team tools, plain functions for private ones; watch token and security costs.

Hindi: Function calling model का tool माँगना है; MCP वह protocol है जो tools host, discover और remotely चलाता है।
Hindi: MCP, function calling के नीचे है; client MCP schemas को function-call tools में बदलता है।
Hindi: Shared या cross-team tools के लिए MCP, private के लिए सादे functions; token और security cost देखें।

---

## ➡️ Next Topic
**30. MCP Best Practices**: now that you know why MCP exists, learn how to build servers that are safe, cheap in tokens and reliable in production.

---
