---

# 3. MCP Architecture (Host, Client, Server)
# हिंदी में: MCP Architecture (Host, Client, Server)
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0, `@modelcontextprotocol/sdk` 1.32.2, `fastapi` 0.163.0. A Python host talking to a Python server and a Node server over stdio ran offline; the FastAPI wrapper ran through `TestClient`. No LLM was called (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
MCP has three roles. The **Host** is the AI application the user touches (Claude Desktop, your FastAPI agent). The host creates one **Client** per server; a client holds a 1:1 session with one **Server**. The server exposes tools, resources and prompts. The host owns the LLM and the security decisions.

## 🔵 सरल परिभाषा (Hindi)
MCP में तीन भूमिकाएँ हैं। **Host** वह AI application है जिसे user इस्तेमाल करता है (Claude Desktop, आपका FastAPI agent)। Host हर server के लिए एक **Client** बनाता है; client एक **Server** से 1:1 session रखता है। Server tools, resources और prompts देता है। LLM और security के फ़ैसले host के पास रहते हैं।

---

## 🔴 Problem it Solves
If the app talked to every tool provider directly, it would need provider-specific code, one shared connection state, and no clear place to enforce permissions. Splitting roles gives isolation (one server cannot read another server's data), simple lifecycle (one client = one connection) and a single place (host) for user consent and policy.

## 🔴 यह क्यों बना? (Hindi)
अगर app हर tool provider से सीधे बात करे तो provider-specific code, साझा connection state और permissions लागू करने की कोई एक जगह नहीं रहती। भूमिकाएँ बाँटने से isolation मिलता है (एक server दूसरे server का data नहीं पढ़ सकता), lifecycle आसान होता है (एक client = एक connection) और user consent व policy के लिए एक जगह (host) मिलती है।

---

## 🟢 How it Works

```
Step 1 → Host reads its config (list of servers to use)
Step 2 → Host spawns / connects a Client per server
Step 3 → Client <-> Server handshake: initialize + capabilities
Step 4 → Host merges all discovered tools into ONE list for the LLM
         (prefix names: tariff__get_duty_rate to avoid clashes)
Step 5 → LLM picks a tool -> Host asks user/policy if needed
Step 6 → Host routes the call to the right Client -> Server runs it
Step 7 → Result returns to the Host -> appended to LLM context
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Host अपनी config पढ़ता है (कौन से servers इस्तेमाल करने हैं)
Step 2 → Host हर server के लिए Client बनाता/जोड़ता है
Step 3 → Client <-> Server handshake: initialize + capabilities
Step 4 → Host सारे tools को LLM के लिए एक list में जोड़ता है
         (नाम prefix करें: tariff__get_duty_rate ताकि टकराव न हो)
Step 5 → LLM tool चुनता है -> ज़रूरत हो तो Host user/policy से पूछता है
Step 6 → Host call को सही Client तक भेजता है -> Server चलाता है
Step 7 → नतीजा Host को लौटता है -> LLM context में जुड़ता है
```

---

## 🟡 Real World Example
**Tariff Agent** (host = FastAPI service) connects to three servers: `tariff` (rates DB, Python), `docs` (customs PDFs, Node), `fx` (currency rates). The host prefixes tool names, enforces "read-only unless a human approves", and logs every call. If `fx` is down, the host skips it and the agent still answers duty questions.

## 🟡 Real Example Hindi mein
**Tariff Agent** (host = FastAPI service) तीन servers से जुड़ता है: `tariff` (rates DB, Python), `docs` (customs PDFs, Node), `fx` (currency rates)। Host tool नामों में prefix लगाता है, "human approve किए बिना सिर्फ़ read-only" नियम लागू करता है और हर call log करता है। `fx` बंद हो तो host उसे छोड़ देता है और agent फिर भी duty के सवाल हल करता है।

---

## 💻 Code Example — Basic
```python
# host.py - minimal MCP host: many clients, one routing table (ran: py + node servers)
import asyncio, sys                                          # async runtime + python path
from contextlib import AsyncExitStack                        # closes all sessions together
from dataclasses import dataclass, field                     # tidy data holder
from mcp import ClientSession, StdioServerParameters         # client session + launch params
from mcp.client.stdio import stdio_client                    # stdio transport

@dataclass                                                   # Host = owns clients + routing
class Host:
    servers: dict[str, StdioServerParameters]                # name -> how to launch server
    stack: AsyncExitStack = field(default_factory=AsyncExitStack)       # resource manager
    sessions: dict[str, ClientSession] = field(default_factory=dict)    # one client per server
    routes: dict[str, str] = field(default_factory=dict)     # "server__tool" -> server

    async def start(self) -> None:                           # connect every server
        for name, params in self.servers.items():            # loop over config
            try:                                             # one bad server must not kill host
                r, w = await self.stack.enter_async_context(stdio_client(params))   # spawn process
                s = await self.stack.enter_async_context(ClientSession(r, w))       # protocol client
                await s.initialize()                         # handshake
            except Exception as exc:                         # e.g. command not found
                print(f"skip {name}: {exc!r}")               # degrade gracefully
                continue                                     # go to next server
            self.sessions[name] = s                          # remember the client
            for t in (await s.list_tools()).tools:           # discover tools
                self.routes[f"{name}__{t.name}"] = name      # prefixed name avoids clashes

    async def call(self, qualified: str, args: dict) -> str:  # route one tool call
        server = self.routes[qualified]                      # KeyError = unknown tool
        res = await self.sessions[server].call_tool(qualified.split("__", 1)[1], args)  # real call
        return ("ERROR: " if res.isError else "") + res.content[0].text   # flatten for the LLM

    async def close(self) -> None:                           # shutdown
        await self.stack.aclose()                            # closes sessions + subprocesses

async def main() -> None:                                    # demo
    host = Host({"py": StdioServerParameters(command=sys.executable, args=["server.py"]),
                 "node": StdioServerParameters(command="node", args=["node/server.mjs"]),
                 "broken": StdioServerParameters(command="nonexistent-cmd")})   # simulated failure
    await host.start()                                       # prints: skip broken: FileNotFoundError(...)
    print(sorted(host.routes))                               # ['node__get_duty_rate', 'py__classify', 'py__get_duty_rate']
    print(await host.call("py__get_duty_rate", {"hs_code": "6403"}))    # 10.0
    print(await host.call("node__get_duty_rate", {"hs_code": "6403"}))  # 10
    await host.close()                                       # clean up

if __name__ == "__main__":                                   # script guard (so FastAPI can import Host)
    asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# hostapi.py - the Host as a FastAPI service (ran with TestClient)
import sys                                                   # python path for server launch
from collections.abc import AsyncIterator                    # lifespan type
from contextlib import asynccontextmanager                   # lifespan helper
from fastapi import FastAPI, HTTPException                   # web framework
from pydantic import BaseModel                               # request validation
from mcp import StdioServerParameters                        # launch params
from host import Host                                        # class from the basic example

class CallIn(BaseModel):                                     # request body model
    tool: str                                                # qualified tool name
    args: dict[str, str] = {}                                # tool arguments

@asynccontextmanager                                         # startup/shutdown hook
async def lifespan(app: FastAPI) -> AsyncIterator[None]:     # typed
    app.state.host = Host({"py": StdioServerParameters(command=sys.executable, args=["server.py"])})
    await app.state.host.start()                             # connect once at startup (not per request)
    yield                                                    # serve traffic
    await app.state.host.close()                             # disconnect on shutdown

app = FastAPI(lifespan=lifespan)                             # app with managed MCP sessions

@app.get("/tools")                                           # list merged tools
async def tools() -> list[str]:                              # typed response
    return sorted(app.state.host.routes)                     # ['py__classify', 'py__get_duty_rate']

@app.post("/call")                                           # policy point: validate before calling
async def call(body: CallIn) -> dict[str, str]:              # typed in/out
    if body.tool not in app.state.host.routes:               # allowlist check
        raise HTTPException(404, "unknown tool")             # -> 404 (verified)
    return {"result": await app.state.host.call(body.tool, body.args)}   # {'result': '0.0'} for 8517
```
Async: all sessions are async; one shared host per process. Error handling: bad server skipped at start, unknown tool -> 404, tool error -> `ERROR:` prefix. Token usage: the merged tool list is the biggest fixed cost; filter per request.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Who is the host? | Your graph app | Your crew app | Your Runner app | Your team app |
| Multi-server support | `MultiServerMCPClient` (verified) | Per-tool MCP config (verify) | `mcp_servers=[...]` list | Several workbenches (verify) |
| Name clash handling | Adapter option (check) | Manual | Manual / `tool_filter` | Manual |
| Lifecycle | `async with` / client object | Framework managed | `async with` server | `async with` workbench |

---

## ⚠️ Common Mistakes
❌ Mistake 1: One client shared by several servers.
✅ Correct: Exactly one client session per server (spec design); the host aggregates.

❌ Mistake 2: Letting servers talk to each other or see the whole conversation.
✅ Correct: Servers only see what the host sends; keep that minimal. Isolation is a feature.

❌ Mistake 3: Connecting servers on every HTTP request.
✅ Correct: Connect in FastAPI `lifespan`, reuse sessions.

---

## 🧠 Tricky Interview Question
"Two MCP servers both expose a tool called `search`. What happens and how do you fix it?"

Answer: The LLM sees ambiguous names; a naive dict would overwrite one and route calls to the wrong server (silent bug). The host must namespace (`docs__search`, `web__search`) and keep a route table from qualified name to client. Also re-list tools on `tools/list_changed` notifications, and refuse duplicates in security-sensitive setups because a malicious server could shadow a trusted tool.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Name the three MCP roles.
A1: Host (app with LLM), Client (connector inside host, 1:1 with a server), Server (exposes capabilities).

Q2: [Medium] Is Claude Desktop a host or a client?
A2: A host; it contains one MCP client instance per configured server.

Q3: [Hard] Why 1:1 client-server and not one multiplexed connection?
A3: Isolation and security boundaries, independent capability negotiation, independent failure/lifecycle per server.

Q4: [Hard] Who decides whether a tool call is allowed?
A4: The host. The protocol transports calls; consent, allowlists and human approval are host responsibilities.

Q5: [System Design] Design a host for 200 concurrent users with per-user permissions.
A5: Stateless FastAPI hosts behind a load balancer; per-user OAuth tokens passed to HTTP servers; tool allowlist computed from user role; shared long-lived sessions for read-only servers, per-user sessions for privileged ones; audit log (user, tool, args hash, duration); circuit breaker per server.

---

## 💰 Cost Impact
Merging N servers multiplies the schema tokens sent per LLM call: tokens ~ sum over all exposed tools (about 100-300 each, approximate). 3 servers x 10 tools can reach ~3-9k input tokens per call before any user text.
Tips: per-request tool filtering, route queries to a "tool selector" step first, prompt-cache the static tool prefix, lazy-connect rarely used servers.

---

## 🔷 When to Use
✅ Use when:
- You need clear trust boundaries between tool providers
- Several heterogeneous servers (Python, Node, remote) feed one agent

❌ Avoid when:
- A single in-process tool is enough
- You cannot enforce consent/policy in the host (then do not connect untrusted servers)

---

## 📊 Visual Diagram
```
+----------------------- HOST (FastAPI Tariff Agent) -----------------------+
|   LLM  <->  policy / consent / routing table                              |
|              |              |               |                             |
|        +-----v----+   +-----v----+    +-----v----+                        |
|        | Client A |   | Client B |    | Client C |                        |
+--------+----------+---+----------+----+----------+------------------------+
              | stdio       | stdio          | HTTP
        +-----v----+   +-----v----+    +-----v----+
        | Server A |   | Server B |    | Server C |
        | tariff   |   | docs(node)|   | fx (remote)|
        +----------+   +----------+    +----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host | App owning LLM + clients | मेज़बान application |
| Client | 1:1 connector to a server | server से जुड़ा connector |
| Server | Provider of tools/data | सेवा देने वाला server |
| Routing table | Tool name -> server | tool से server का नक्शा |
| Namespacing | Prefixing names | नाम में prefix |

---

## ⚡ 3-Line Summary
English: Host owns the LLM and policy; each Client talks 1:1 to one Server; Servers expose tools/resources/prompts. The host merges and routes. Isolation and consent live in the host.
Hindi: Host के पास LLM और policy है; हर Client एक Server से 1:1 बात करता है; Server tools/resources/prompts देता है। Host उन्हें जोड़कर route करता है। Isolation और consent host में रहते हैं।

---

## ➡️ Next Topic
**004. MCP Transport Types (stdio, SSE, HTTP)** - the wire between client and server decides how you deploy and scale it.

---
