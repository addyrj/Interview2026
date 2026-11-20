---

# 18. MCP with OpenAI
# हिंदी में: OpenAI के साथ MCP
# Framework: OpenAI SDK
# Already Known: No

> Verified against: `openai-agents` 0.24.0, `openai` 3.51.0, `mcp` 1.30.0. Ran locally: `MCPServerStdio` with `cache_tools_list` and a static tool filter; a full `Runner.run` loop using a **scripted offline `Model`** (so no API key) and the FastAPI route via `TestClient`; the Responses API `mcp` tool payload was captured through a mock HTTP transport. Not run: real OpenAI model calls, `MCPServerStreamableHttp` against a live remote server (needs a server), `HostedMCPTool` against OpenAI (needs key + public server). Token numbers shown are from the scripted test model, not real usage.

---

## 🔵 Simple Definition (2-3 lines)
OpenAI offers two MCP paths. In the **Agents SDK** you pass MCP server objects (`MCPServerStdio`, `MCPServerStreamableHttp`, `MCPServerSse`) to `Agent(mcp_servers=[...])` and your process talks to the server. With the **Responses API** you can instead send a `{"type": "mcp", "server_url": ...}` tool and OpenAI's side connects to a public server (hosted MCP).

## 🔵 सरल परिभाषा (Hindi)
OpenAI में MCP के दो रास्ते हैं। **Agents SDK** में आप MCP server objects (`MCPServerStdio`, `MCPServerStreamableHttp`, `MCPServerSse`) को `Agent(mcp_servers=[...])` में देते हैं और आपका process server से बात करता है। **Responses API** में आप `{"type": "mcp", "server_url": ...}` tool भेजते हैं और OpenAI की तरफ से public server से connection होता है (hosted MCP)।

---

## 🔴 Problem it Solves
Function calling needs you to define each function schema in your code. With MCP, the SDK lists the server's tools at run time, converts them to function tools and routes calls back - so one shared tariff server serves all OpenAI-based agents without copy-pasted schemas.

## 🔴 यह क्यों बना? (Hindi)
Function calling में हर function का schema आपको अपने code में देना पड़ता है। MCP में SDK run time पर server के tools list करता है, उन्हें function tools में बदलता है और calls वापस route करता है - इसलिए एक साझा tariff server सभी OpenAI agents को बिना schema copy-paste के सेवा देता है।

---

## 🟢 How it Works

```
Agents SDK (local connection)
Step 1 -> async with MCPServerStdio(params=...) as srv   # connect + initialize
Step 2 -> Agent(model=..., mcp_servers=[srv])
Step 3 -> Runner.run(agent, text): SDK calls srv.list_tools() each run (cached if cache_tools_list=True)
Step 4 -> tools offered to the model like normal function tools
Step 5 -> model returns a function call -> SDK calls srv.call_tool(name, args)
Step 6 -> result goes back to the model; loop until final output or max_turns

Hosted MCP (Responses API)
Step 1 -> tools=[{"type":"mcp","server_label","server_url","require_approval","allowed_tools"}]
Step 2 -> OpenAI connects to server_url and runs the tool calls
```

## 🟢 कैसे काम करता है? (Hindi)

```
Agents SDK (local connection)
Step 1 -> async with MCPServerStdio(params=...) as srv   # connect + initialize
Step 2 -> Agent(model=..., mcp_servers=[srv])
Step 3 -> Runner.run(agent, text): SDK हर run में srv.list_tools() बुलाता है (cache_tools_list=True हो तो cache)
Step 4 -> tools model को सामान्य function tools की तरह दिखते हैं
Step 5 -> model function call देता है -> SDK srv.call_tool(name, args) चलाता है
Step 6 -> result model को वापस; final output या max_turns तक loop

Hosted MCP (Responses API)
Step 1 -> tools=[{"type":"mcp","server_label","server_url","require_approval","allowed_tools"}]
Step 2 -> OpenAI खुद server_url से जुड़कर tool calls चलाता है
```

---

## 🟡 Real World Example
**Tariff Agent** for a customs broker: the agent uses `MCPServerStreamableHttp` to reach the company's tariff server with a bearer token, allow-lists two tools, and caps the loop at 6 turns. For a public docs server, the team uses hosted MCP with `require_approval` for anything that writes.

## 🟡 Real Example Hindi mein
**Tariff Agent** customs broker के लिए: agent `MCPServerStreamableHttp` से कंपनी के tariff server तक bearer token के साथ पहुँचता है, दो tools allow-list करता है और loop को 6 turns पर रोकता है। Public docs server के लिए hosted MCP लेते हैं और कुछ भी लिखने वाले tools पर `require_approval` रखते हैं।

---

## 💻 Code Example — Basic
```python
# tariff_server.py: same FastMCP server as note 015 (get_tariff_rate, calc_duty) - omitted for brevity
```

```python
# basic_openai_mcp.py - Agents SDK + MCPServerStdio + tool filter + offline scripted model (ran)
import asyncio, json, sys                                   # stdlib
from agents import Agent, ModelResponse, Runner, Usage, set_tracing_disabled   # SDK core
from agents.mcp import MCPServerStdio, create_static_tool_filter               # MCP server + filter
from agents.models.interface import Model                   # base class to script replies
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

set_tracing_disabled(True)                                  # no tracing upload in an offline test

class Scripted(Model):                                      # fake model: call a tool, then answer
    def __init__(self) -> None:
        self.n = 0                                          # call counter
    async def get_response(self, system_instructions, input, model_settings, tools,
                           output_schema, handoffs, tracing, **kw) -> ModelResponse:
        self.n += 1                                         # first call -> tool call
        print("tools offered:", [t.name for t in tools])    # shows MCP tools reached the model
        if self.n == 1:
            out = [ResponseFunctionToolCall(type="function_call", call_id="c1",
                   name="get_tariff_rate", arguments=json.dumps({"hs_code": "6109.10"}))]
        else:                                               # second call -> final text
            out = [ResponseOutputMessage(id="m1", type="message", role="assistant", status="completed",
                   content=[ResponseOutputText(type="output_text", text="Duty is 20%", annotations=[])])]
        return ModelResponse(output=out, response_id=None,  # usage below is fake test data
                             usage=Usage(requests=1, input_tokens=7, output_tokens=3, total_tokens=10))
    def stream_response(self, *a, **k):                     # not needed for this test
        raise NotImplementedError

async def main() -> None:
    allow = create_static_tool_filter(allowed_tool_names=["get_tariff_rate"])   # expose only one tool
    async with MCPServerStdio(                              # connects on enter, closes on exit
            params={"command": sys.executable, "args": ["tariff_server.py"]},
            cache_tools_list=True, tool_filter=allow) as srv:
        print([t.name for t in await srv.list_tools()])     # ['get_tariff_rate'] (filter works)
        agent = Agent(name="tariff", instructions="Use tools.",
                      model=Scripted(), mcp_servers=[srv])  # real: model="gpt-4.1" (needs OPENAI_API_KEY)
        r = await Runner.run(agent, "duty for 6109.10?", max_turns=5)   # agent loop
        print(r.final_output, r.context_wrapper.usage.total_tokens)     # -> Duty is 20% 20 (2 fake calls)

asyncio.run(main())                                         # run
```

## 💻 Code Example — Advanced
```python
# openai_mcp_api.py - FastAPI + Agents SDK + MCP server owned by lifespan (stdio path + route ran offline)
import os, sys                                              # env + interpreter path
from contextlib import asynccontextmanager                  # lifespan helper
from typing import Any, AsyncIterator                       # type hints
from agents import Agent, MaxTurnsExceeded, Runner          # SDK core
from agents.exceptions import AgentsException               # base class of SDK errors
from agents.mcp import MCPServer, MCPServerStdio, MCPServerStreamableHttp, create_static_tool_filter
from fastapi import FastAPI, HTTPException                  # web layer
from pydantic import BaseModel                              # request/response models

class Ask(BaseModel):                                       # request body
    question: str

class Answer(BaseModel):                                    # response body
    answer: str
    total_tokens: int
    requests: int

def make_server() -> MCPServer:                             # choose transport from env
    url = os.getenv("TARIFF_MCP_URL")                       # e.g. https://tariff.internal/mcp
    allow = create_static_tool_filter(allowed_tool_names=["get_tariff_rate", "calc_duty"])
    if url:                                                 # remote server (not run - needs one)
        return MCPServerStreamableHttp(
            params={"url": url, "headers": {"Authorization": f"Bearer {os.getenv('TARIFF_TOKEN', '')}"}, "timeout": 10},
            cache_tools_list=True, tool_filter=allow,       # cache tools/list, allow-list tools
            max_retry_attempts=3, retry_backoff_seconds_base=1.0)   # retry connection-level failures
    return MCPServerStdio(                                  # local fallback (ran)
        params={"command": sys.executable, "args": ["tariff_server.py"]},
        cache_tools_list=True, tool_filter=allow)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    server = make_server()                                  # build server object
    async with server:                                      # connect; disconnect on shutdown
        model: Any = getattr(app.state, "model", "gpt-4.1") # tests inject a scripted Model
        app.state.agent = Agent(name="tariff", model=model, mcp_servers=[server],
            instructions="You are a tariff assistant. Use tools for rates and duty math.")
        yield

app = FastAPI(lifespan=lifespan)

@app.post("/ask", response_model=Answer)
async def ask(body: Ask) -> Answer:
    try:
        result = await Runner.run(app.state.agent, body.question, max_turns=6)   # loop capped at 6 turns
    except MaxTurnsExceeded as exc:                         # agent kept calling tools
        raise HTTPException(422, "agent exceeded max turns") from exc
    except AgentsException as exc:                          # other SDK errors
        raise HTTPException(502, type(exc).__name__) from exc
    usage = result.context_wrapper.usage                    # aggregated token usage
    return Answer(answer=str(result.final_output), total_tokens=usage.total_tokens, requests=usage.requests)
```
Test result with the scripted model: `{'answer': 'Duty is 20%', 'total_tokens': 20, 'requests': 2}` (fake numbers).

```python
# hosted_mcp.py - two "hosted" styles (payload captured with a mock transport; NOT sent to OpenAI)
from agents import Agent, HostedMCPTool                     # hosted MCP tool wrapper in the Agents SDK

hosted = HostedMCPTool(tool_config={                        # fields come from openai.types.responses.tool_param.Mcp
    "type": "mcp", "server_label": "tariff",                # label shown in logs/approvals
    "server_url": "https://mcp.example.com/mcp",            # must be reachable by OpenAI
    "require_approval": "always",                           # human approval before each call
    "allowed_tools": ["get_tariff_rate"]})                  # allow-list
agent = Agent(name="hosted", model="gpt-4.1", tools=[hosted])   # real run needs OPENAI_API_KEY (not run)

# Raw Responses API call - captured body was exactly this tools entry:
# await openai.AsyncOpenAI().responses.create(model="gpt-4.1", input="hi", tools=[{
#   "type": "mcp", "server_label": "tariff", "server_url": "https://mcp.example.com/mcp",
#   "authorization": "TOKEN", "require_approval": "never", "allowed_tools": ["get_tariff_rate"]}])
```
Token usage: `result.context_wrapper.usage` aggregates input/output tokens over all model calls. Error handling: `MaxTurnsExceeded` and `AgentsException`. Retry params exist on the HTTP class (`max_retry_attempts`, `retry_backoff_seconds_base`).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Local MCP | adapters -> tools | verify docs | `MCPServerStdio/Sse/StreamableHttp` (verified) | MCP workbench (verify) |
| Hosted MCP | n/a (provider-specific) | n/a | `HostedMCPTool` (verified construct) | n/a |
| Tool allow-list | filter list yourself | verify | `create_static_tool_filter` (verified) | verify |
| Tool list cache | your code | verify | `cache_tools_list` + `invalidate_tools_cache()` (verified names) | verify |
| Approval | `interrupt` | verify | `require_approval` | UserProxy |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Not using `async with` on the server object.
✅ Correct: Connect first (`async with srv`) or call `connect()`/`cleanup()` - otherwise `list_tools` fails.

❌ Mistake 2: `cache_tools_list=True` while the server adds tools dynamically.
✅ Correct: Call `srv.invalidate_tools_cache()` on `list_changed` or disable the cache.

❌ Mistake 3: Hosted MCP pointed at localhost.
✅ Correct: OpenAI must reach the URL; use local MCP classes for private servers.

❌ Mistake 4: `require_approval: "never"` on a write tool.
✅ Correct: Approve writes; allow-list tools.

---

## 🧠 Tricky Interview Question
"Latency doubled after you added MCP to an OpenAI agent. Why?"

Answer: Without `cache_tools_list=True` the SDK calls `tools/list` on every run (one extra round trip per run), and remote servers add network time per tool call. Also more tools mean more input tokens per model call, which raises time-to-first-token. Fix: cache the list (with invalidation), allow-list tools, co-locate server and agent, use HTTP keep-alive, and set a sensible `timeout`.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which classes connect an MCP server in the Agents SDK?
A1: `MCPServerStdio`, `MCPServerSse`, `MCPServerStreamableHttp` (plus `HostedMCPTool` for hosted).

Q2: [Medium] Local MCP vs hosted MCP?
A2: Local: your process connects (private networks, full control). Hosted: OpenAI connects to a public URL (less code, less control).

Q3: [Hard] How are MCP tool errors surfaced?
A3: The server returns `isError`; the SDK passes error text back to the model, controlled by the `failure_error_function` param (default behaviour: a string for the model).

Q4: [Hard] How do you stop an MCP tool from running without consent?
A4: `require_approval` on the server object or hosted tool, an allow-list filter, and an approval callback for local servers.

Q5: [System Design] Shared MCP gateway for 30 OpenAI agents.
A5: Streamable HTTP servers behind a gateway with OAuth, per-agent allow-lists, tool-list caching, retries with backoff, metrics per tool, and per-agent token budgets.

---

## 💰 Cost Impact
Each model call includes all tool schemas -> input tokens scale with tool count x turns. `HostedMCPTool` also puts tool definitions in context. Cost = sum over turns of input tokens x input price + output x output price (prices: approximate, check OpenAI pricing). Tips: allow-list tools, cap `max_turns`, cache the tool list (saves latency, not tokens), pick a smaller model for simple lookups.

---

## 🔷 When to Use
✅ Use when:
- You standardise on OpenAI models/Agents SDK and have shared MCP servers

❌ Avoid when:
- You only need one in-process function (use `@function_tool`)

---

## 📊 Visual Diagram
```
 FastAPI /ask -> Runner.run(agent, max_turns=6) -> Model (gpt-*)
                      |   ^  function_call / result
                      v   |
              MCPServerStdio|StreamableHttp --> tariff MCP server
 Hosted: Model/OpenAI --(HTTPS, approval)--> public MCP server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MCPServerStdio | Local stdio MCP connection | local stdio MCP connection |
| MCPServerStreamableHttp | Remote HTTP MCP connection | remote HTTP MCP connection |
| HostedMCPTool | OpenAI-side MCP tool | OpenAI की तरफ का MCP tool |
| tool_filter | Allow/deny tool names | tools को allow/deny करना |
| max_turns | Loop cap | loop की सीमा |

---

## ⚡ 3-Line Summary
English: Pass MCP server objects to `Agent(mcp_servers=...)`. Cache and filter tools, cap turns, and use hosted MCP only for public servers. Track usage from `context_wrapper.usage`.
Hindi: MCP server objects को `Agent(mcp_servers=...)` में दें। Tools cache और filter करें, turns सीमित रखें, hosted MCP सिर्फ़ public servers के लिए लें। Usage `context_wrapper.usage` से देखें।

---

## ➡️ Next Topic
**019. MCP Tool Discovery** - how clients find tools, `tools/list`, pagination and `list_changed`.

---
