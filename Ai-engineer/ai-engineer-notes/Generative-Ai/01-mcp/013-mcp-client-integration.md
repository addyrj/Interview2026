---

# 13. MCP Client Integration
# हिंदी में: MCP Client Integration (Host में servers जोड़ना)
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python client), `@modelcontextprotocol/sdk` 1.32.2 (a Node server used as a target), `fastapi` 0.163.0, Node v24.2.0. A Python host connected to a Python server and a Node server over stdio, skipped a broken server, routed namespaced calls and ran a FastAPI wrapper through `TestClient`. The "LLM" in the agent loop is a deterministic FAKE function; no real model was called (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
MCP client integration is the host-side code that connects to one or many MCP servers, runs the handshake, lists their tools, converts them to the format your LLM expects, routes the LLM's tool calls back to the right server, and cleans up connections. In Python it is `stdio_client` or `streamablehttp_client` plus `ClientSession`.

## 🔵 सरल परिभाषा (Hindi)
MCP client integration host-side code है जो एक या कई MCP servers से जुड़ता है, handshake चलाता है, उनके tools list करता है, उन्हें LLM के format में बदलता है, LLM की tool calls सही server तक भेजता है और connections साफ़ करता है। Python में यह `stdio_client` या `streamablehttp_client` के साथ `ClientSession` है।

---

## 🔴 Problem it Solves
Agents need tools from several places (a Python server, a Node server, a remote HTTP server). Without a host layer you hand-code each connection, tool names collide (`get_duty_rate` in two servers), one dead server kills startup, a hung tool blocks the agent, and connections leak. A small host class fixes discovery, namespacing, routing, timeouts and shutdown in one place.

## 🔴 यह क्यों बना? (Hindi)
Agents को कई जगह से tools चाहिए (Python server, Node server, remote HTTP server)। Host layer के बिना हर connection हाथ से लिखना पड़ता है, tool नाम टकराते हैं (`get_duty_rate` दो servers में), एक मरा server पूरा startup गिरा देता है, अटका tool agent को रोक देता है और connections leak होते हैं। छोटा host class discovery, namespacing, routing, timeouts और shutdown एक जगह संभालता है।

---

## 🟢 How it Works

```
Step 1 -> for each configured server: open a transport (stdio spawn or HTTP URL)
Step 2 -> ClientSession(read, write) ; await session.initialize()      (handshake + capabilities)
Step 3 -> await session.list_tools()   -> qualify names: "<server>__<tool>"
Step 4 -> convert to LLM format (OpenAI "function" dicts / Anthropic "input_schema")
Step 5 -> LLM returns a tool call (name + JSON args) -> look up server in routes
Step 6 -> await session.call_tool(original_name, args)  with a timeout
Step 7 -> result.isError? -> pass the text back to the LLM (it can retry)
Step 8 -> loop until the LLM answers; on shutdown close everything (AsyncExitStack)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> हर configured server के लिए transport खोलें (stdio spawn या HTTP URL)
Step 2 -> ClientSession(read, write) ; await session.initialize()      (handshake + capabilities)
Step 3 -> await session.list_tools()   -> नाम qualify करें: "<server>__<tool>"
Step 4 -> LLM के format में बदलें (OpenAI "function" dicts / Anthropic "input_schema")
Step 5 -> LLM tool call (name + JSON args) देता है -> routes से server खोजें
Step 6 -> timeout के साथ await session.call_tool(original_name, args)
Step 7 -> result.isError? -> text LLM को लौटाएँ (वह दोबारा कोशिश कर सकता है)
Step 8 -> LLM के जवाब देने तक loop; shutdown पर सब बंद करें (AsyncExitStack)
```

---

## 🟡 Real World Example
**Tariff Agent**: the FastAPI service is the host. At startup it connects to `py` (rates DB server), `node` (the legacy duty calculator) and `broken` (a misconfigured server). `broken` is logged and skipped, the other two contribute tools `py__get_duty_rate` and `node__get_duty_rate`, and the agent answers "duty for shoes?" by calling the namespaced tool and reading the result.

## 🟡 Real Example Hindi mein
**Tariff Agent**: FastAPI service host है। Startup पर वह `py` (rates DB server), `node` (पुराना duty calculator) और `broken` (गलत configured server) से जुड़ता है। `broken` को log करके छोड़ दिया जाता है, बाकी दो `py__get_duty_rate` और `node__get_duty_rate` tools देते हैं, और agent "duty for shoes?" का जवाब namespaced tool call करके और नतीजा पढ़कर देता है।

---

## 💻 Code Example — Basic
```python
# client.py - connect to ONE stdio server, list tools, call one (ran)
import asyncio                                              # async runtime
import sys                                                  # current interpreter path
from mcp import ClientSession, StdioServerParameters        # session + launch params
from mcp.client.stdio import stdio_client                   # stdio transport

async def main() -> None:                                   # driver
    params = StdioServerParameters(command=sys.executable, args=["server.py"])   # how to start the server
    async with stdio_client(params) as (read, write):       # spawns the process, yields streams
        async with ClientSession(read, write) as session:   # protocol session
            init = await session.initialize()               # handshake
            print(init.protocolVersion, init.serverInfo.name)   # e.g. 2025-11-25 tariff-server
            tools = await session.list_tools()              # discovery
            print([t.name for t in tools.tools])            # tool names
            res = await session.call_tool("get_duty_rate", {"hs_code": "8517"})   # call
            print(res.structuredContent)                    # {'result': 0.0}
            bad = await session.call_tool("get_duty_rate", {"hs_code": "1"})      # tool-level error
            print(bad.isError, bad.content[0].text)         # True, readable message

asyncio.run(main())                                         # run
```
Ran against a small tariff server: printed the protocol version and `tariff-server`, the tool list, `{'result': 0.0}`, and `True Error executing tool get_duty_rate: unknown HS code 1`. For HTTP servers replace `stdio_client(params)` with `streamablehttp_client(url, headers=...)` (it yields three values; ignore the third).

## 💻 Code Example — Advanced
```python
# host.py - multi-server host: skip broken servers, namespace tools, timeout calls, OpenAI-style tool list, agent loop with a FAKE LLM (ran)
import asyncio                                              # timeouts
import logging                                              # diagnostics
import sys                                                  # interpreter path
from contextlib import AsyncExitStack                       # one place to close everything
from dataclasses import dataclass, field                    # tidy state
from typing import Any                                      # JSON-ish types
from mcp import ClientSession, StdioServerParameters, types # client + types
from mcp.client.stdio import stdio_client                   # transport

log = logging.getLogger("tariff.host")                      # logger

@dataclass
class Host:                                                 # the "host" role from topic 003
    servers: dict[str, StdioServerParameters]               # name -> how to launch
    call_timeout_s: float = 10.0                            # protect the agent from hung tools
    stack: AsyncExitStack = field(default_factory=AsyncExitStack)   # owns every connection
    sessions: dict[str, ClientSession] = field(default_factory=dict)   # name -> live session
    routes: dict[str, tuple[str, str]] = field(default_factory=dict)   # qualified -> (server, tool)
    tools: list[types.Tool] = field(default_factory=list)   # merged tool list

    async def start(self) -> None:                          # connect all servers
        for name, params in self.servers.items():           # one by one (parallelise with gather if needed)
            try:                                            # one bad server must not kill startup
                read, write = await self.stack.enter_async_context(stdio_client(params))   # spawn
                session = await self.stack.enter_async_context(ClientSession(read, write))  # session
                await session.initialize()                  # handshake
                listed = await session.list_tools()         # discover tools
            except Exception as exc:                        # missing binary, crash, bad handshake
                log.warning("skipping server %s: %r", name, exc)   # visible but non-fatal
                continue                                    # next server
            self.sessions[name] = session                   # keep it
            for tool in listed.tools:                       # namespace to avoid collisions
                qualified = f"{name}__{tool.name}"          # py__get_duty_rate
                self.routes[qualified] = (name, tool.name)  # remember original name
                self.tools.append(tool.model_copy(update={"name": qualified}))   # renamed copy for the LLM

    def openai_tools(self) -> list[dict[str, Any]]:         # convert to OpenAI function-calling shape
        return [{"type": "function", "function": {"name": t.name, "description": t.description or "", "parameters": t.inputSchema}} for t in self.tools]   # inputSchema is already JSON Schema

    async def call(self, qualified: str, args: dict[str, Any]) -> str:   # route one call
        if qualified not in self.routes:                    # LLM hallucinated a tool
            return f"ERROR: unknown tool {qualified}"       # let it recover
        server, tool = self.routes[qualified]               # resolve
        try:                                                # timeout guard
            res = await asyncio.wait_for(self.sessions[server].call_tool(tool, args), timeout=self.call_timeout_s)   # remote call
        except asyncio.TimeoutError:                        # tool too slow
            return f"ERROR: {qualified} timed out after {self.call_timeout_s}s"   # report instead of hanging
        text = res.content[0].text if res.content and res.content[0].type == "text" else ""   # first text block
        return ("ERROR: " if res.isError else "") + text    # keep error flag visible to the LLM

    async def close(self) -> None:                          # shutdown
        await self.stack.aclose()                           # closes sessions and kills child processes

async def fake_llm(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:   # STAND-IN for a real model
    last = messages[-1]                                     # latest message
    if last["role"] == "user":                              # first turn: pick a tool
        name = next(t["function"]["name"] for t in tools if t["function"]["name"].endswith("get_duty_rate"))   # deterministic choice
        return {"tool_call": {"name": name, "arguments": {"hs_code": "6403"}}}   # as a real model would
    return {"content": f"Duty is {last['content']}%"}      # second turn: answer from the tool result

async def run_agent(host: Host, question: str) -> str:      # tiny tool loop
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]   # conversation
    for _ in range(5):                                      # hard step limit (avoid infinite loops/cost)
        reply = await fake_llm(messages, host.openai_tools())   # replace with your async LLM client
        if "tool_call" not in reply:                        # final answer
            return reply["content"]                         # done
        call = reply["tool_call"]                           # requested tool
        result = await host.call(call["name"], call["arguments"])   # execute via MCP
        messages.append({"role": "tool", "content": result})   # feed result back
    return "ERROR: too many steps"                          # safety stop

async def main() -> None:                                   # demo
    host = Host({"py": StdioServerParameters(command=sys.executable, args=["server.py"]),
                 "node": StdioServerParameters(command="node", args=["node/server.mjs"]),
                 "broken": StdioServerParameters(command="nonexistent-cmd")})   # intentionally bad
    await host.start()                                      # connect
    print(sorted(host.routes))                              # ['node__get_duty_rate', 'py__classify', 'py__get_duty_rate']
    print(await run_agent(host, "duty for shoes?"))         # Duty is 10.0%
    print(await host.call("py__get_duty_rate", {"hs_code": "1"}))   # ERROR: Error executing tool ...
    print(await host.call("nope__x", {}))                   # ERROR: unknown tool nope__x
    await host.close()                                      # cleanup

if __name__ == "__main__":                                  # entry
    asyncio.run(main())                                     # run
```
Ran output: a warning `skipping server broken: FileNotFoundError(...)`, the three routes above, `Duty is 10.0%`, `ERROR: Error executing tool get_duty_rate: unknown HS code 1`, `ERROR: unknown tool nope__x`. Note: the `py__classify` tool uses sampling and this host passes no `sampling_callback`, so calling it would fail; pass one to `ClientSession(..., sampling_callback=...)` if you want it (topic 009).

FastAPI wrapper (ran with `TestClient`): create the `Host` in `lifespan`, store it on `app.state`, expose `GET /tools`, `POST /call` (404 for unknown tool) and `POST /ask`; always `await host.close()` in `finally`. Result: tools `['py__classify', 'py__get_duty_rate']`, call result `{'result': '0.0'}`, unknown tool `404`, ask `{'answer': 'Duty is 10.0%'}`. Token usage: every tool you forward is in the prompt on every turn, so filter `host.tools` per task. For Anthropic-style APIs use `{"name", "description", "input_schema": t.inputSchema}` instead of the OpenAI wrapper (shape not run here).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Built-in MCP client | Adapter library (`MultiServerMCPClient`-style, verify current docs) | MCP integration (verify) | `MCPServerStdio`, `MCPServerStreamableHttp` classes (imports verified earlier) | MCP workbench (verify) |
| Multi-server + namespacing | Adapter handles it (verify) | Verify | One object per server, you combine | Verify |
| Lifecycle | You manage `async with`/cleanup | Verify | `async with` context managers | Verify |
| Custom host like above | Always possible and sometimes clearer | Possible | Possible | Possible |

Use the framework's adapter when it covers your needs; write your own host (as above) when you need timeouts, filtering, sampling callbacks or custom routing. Cells marked verify were not checked in this run.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Opening a new connection (and spawning a process) for every tool call.
✅ Correct: Connect once at startup (lifespan) and reuse the session.

❌ Mistake 2: Not namespacing tools from different servers.
✅ Correct: Prefix with the server name and map back to the original on call.

❌ Mistake 3: Letting one failing server break startup, or never closing connections.
✅ Correct: try/except per server and `AsyncExitStack` for cleanup.

❌ Mistake 4: No timeouts, no step limits.
✅ Correct: `asyncio.wait_for` around calls and a max-iterations guard in the loop.

❌ Mistake 5: Auto-running every tool the LLM asks for.
✅ Correct: Allow-list servers/tools, require human approval for destructive ones (host's job).

---

## 🧠 Tricky Interview Question
"Your FastAPI host serves 100 concurrent users but all share one stdio MCP session. Users report slow answers and sometimes wrong results. Why, and how do you fix it?"

Answer: A single stdio pipe is a single server process; requests are multiplexed but a slow tool delays others, and any server-side global state (current user, cwd, cached auth) is shared by every user, which is a correctness and security risk. Fixes: make the server stateless and pass the user identity explicitly through your own authenticated channel (never through LLM-chosen args), run a pool of server processes or use HTTP servers with horizontal scaling, add per-call timeouts, and keep per-request state out of the shared session.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the minimum client steps?
A1: Open a transport, create `ClientSession`, `initialize()`, then `list_tools()` and `call_tool()`.

Q2: [Medium] How do you avoid tool name collisions?
A2: Prefix names with the server name (`server__tool`), keep a route table to the original name, and call the right session.

Q3: [Hard] How do you convert MCP tools to OpenAI tool format?
A3: `{"type": "function", "function": {"name", "description", "parameters": tool.inputSchema}}`; `inputSchema` is already JSON Schema.

Q4: [Hard] A server crashes mid-run. What does the host do?
A4: Catch the exception from `call_tool`, return an error string to the LLM or retry once, mark the server unhealthy, optionally reconnect with backoff, and alert. Never let it crash the whole agent.

Q5: [System Design] Design a host for 20 internal MCP servers and 500 users.
A5: Central gateway holding connections to HTTP servers, per-user auth and tool allow-lists, tool filtering by task to control tokens, circuit breakers and timeouts, audit logs of every call, cached tool listings, approval workflow for write tools.

---

## 💰 Cost Impact
Each forwarded tool adds its schema to every request (approximate: roughly 100-300 input tokens per typical tool; measure). The agent loop adds one LLM call per tool step, and history grows with every tool result. Tips: filter tools per task, cap steps, truncate or summarise large tool results, use prompt caching for the stable tool list where supported (verify), and use a cheaper model for routing.

---

## 🔷 When to Use
✅ Use a custom host when:
- You need multi-server routing, timeouts, approvals or sampling callbacks
- Your framework adapter lacks a feature

✅ Use the framework adapter when: a simple "load all tools" is enough.

❌ Avoid when:
- Only one local function is needed (plain framework tool)

---

## 📊 Visual Diagram
```
 FastAPI host (lifespan: connect once)
 +--------------------------------------------------+
 | LLM <-> run_agent loop (max 5 steps)             |
 |          |  tool_call "py__get_duty_rate"        |
 |          v                                       |
 |  routes: py__* -> (py, tool)  node__* -> (node)  |
 +------+-------------------------+-----------------+
        | stdio                   | stdio
        v                         v
   [python server]          [node server]      [broken -> skipped]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host | App that owns the LLM and clients | LLM और clients वाला app |
| ClientSession | One protocol session to one server | एक server से एक session |
| AsyncExitStack | Closes many async resources together | कई async resources साथ बंद करना |
| Namespacing | Prefixing tool names by server | server नाम का prefix |
| Route table | Map from tool name to server | tool से server का map |

---

## ⚡ 3-Line Summary
English: A host connects to each server once, merges and namespaces their tools, and routes calls with timeouts. One bad server must not break the others. Close everything on shutdown.
Hindi: Host हर server से एक बार जुड़ता है, उनके tools merge और namespace करता है और timeouts के साथ calls route करता है। एक खराब server बाकी को न बिगाड़े। Shutdown पर सब बंद करें।

---

## ➡️ Next Topic
**014. MCP with Claude Desktop** - plug your server into a real desktop host with a config file, and debug the common failures.

---
