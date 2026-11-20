---

# 4. MCP Transport Types (stdio, SSE, HTTP)
# हिंदी में: MCP Transport के प्रकार (stdio, SSE, HTTP)
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0. stdio, legacy SSE and Streamable HTTP servers + clients were all started locally and called successfully. Protocol version negotiated: 2025-11-25. Remote/cloud deployment and auth: not run.

---

## 🔵 Simple Definition (2-3 lines)
A transport is the pipe that carries MCP's JSON-RPC messages. **stdio**: the host launches the server as a child process and talks over stdin/stdout (local). **Streamable HTTP**: one HTTP endpoint (e.g. `/mcp`) that supports POST and optional streaming (remote, current standard). **SSE** (HTTP+SSE): the older remote transport, now deprecated in favour of Streamable HTTP.

## 🔵 सरल परिभाषा (Hindi)
Transport वह pipe है जिसमें MCP के JSON-RPC messages चलते हैं। **stdio**: host server को child process की तरह चलाता है और stdin/stdout पर बात करता है (local)। **Streamable HTTP**: एक HTTP endpoint (जैसे `/mcp`) जो POST और वैकल्पिक streaming देता है (remote, मौजूदा standard)। **SSE** (HTTP+SSE): पुराना remote transport, जो अब Streamable HTTP के पक्ष में deprecated है।

---

## 🔴 Problem it Solves
One transport cannot fit all deployments. A desktop app wants zero-network, zero-auth local servers. A company wants a shared tariff server on Kubernetes serving 500 agents with OAuth and load balancing. Separate transports let the same server code run in both worlds.

## 🔴 यह क्यों बना? (Hindi)
एक transport हर deployment में फ़िट नहीं होता। Desktop app को बिना network और auth के local server चाहिए। कंपनी को Kubernetes पर साझा tariff server चाहिए जो OAuth और load balancing के साथ 500 agents को सेवा दे। अलग transports से वही server code दोनों जगह चलता है।

---

## 🟢 How it Works

```
stdio            Step 1 -> host spawns "python server.py"
                 Step 2 -> JSON-RPC lines over stdin/stdout (stderr = logs)
                 Step 3 -> host kills process when done

Streamable HTTP  Step 1 -> client POST /mcp  {initialize}
                 Step 2 -> server replies JSON or an SSE stream; may issue Mcp-Session-Id
                 Step 3 -> next requests POST with that session id
                 Step 4 -> stateless mode: no session id, any replica can answer

Legacy SSE       Step 1 -> client GET /sse (long-lived event stream)
                 Step 2 -> server sends "endpoint" event with POST url
                 Step 3 -> client POSTs requests to /messages/, replies come via the stream
```

## 🟢 कैसे काम करता है? (Hindi)

```
stdio            Step 1 -> host "python server.py" spawn करता है
                 Step 2 -> stdin/stdout पर JSON-RPC lines (stderr = logs)
                 Step 3 -> काम ख़त्म होने पर host process kill करता है

Streamable HTTP  Step 1 -> client POST /mcp {initialize}
                 Step 2 -> server JSON या SSE stream लौटाता है; Mcp-Session-Id दे सकता है
                 Step 3 -> आगे के requests उसी session id के साथ POST होते हैं
                 Step 4 -> stateless mode: कोई session id नहीं, कोई भी replica जवाब दे सकता है

Legacy SSE       Step 1 -> client GET /sse (लंबी चलने वाली event stream)
                 Step 2 -> server "endpoint" event में POST url भेजता है
                 Step 3 -> client /messages/ पर POST करता है, जवाब stream से आते हैं
```

---

## 🟡 Real World Example
**Tariff Agent**: on an analyst's laptop, Claude Desktop launches `tariff-server` via stdio (no ports, no auth). In production, the same code runs as Streamable HTTP in `stateless_http=True` mode behind an NGINX/Kubernetes service so any of 10 replicas can serve any request.

## 🟡 Real Example Hindi mein
**Tariff Agent**: analyst के laptop पर Claude Desktop `tariff-server` को stdio से चलाता है (न port, न auth)। Production में वही code `stateless_http=True` mode में Streamable HTTP पर NGINX/Kubernetes service के पीछे चलता है, ताकि 10 में से कोई भी replica कोई भी request संभाल ले।

---

## 💻 Code Example — Basic
```python
# tsrv.py - ONE server file, transport chosen at launch (all three ran locally)
import sys                                                  # read CLI args
from mcp.server.fastmcp import FastMCP                      # server helper

mcp = FastMCP("tariff-net", host="127.0.0.1", port=int(sys.argv[2]))   # host/port used by HTTP transports only

@mcp.tool()                                                 # one demo tool
def get_duty_rate(hs_code: str) -> float:                   # typed argument
    """Duty percent for an HS code."""                      # description
    return 10.0                                             # fixed value for the demo

if __name__ == "__main__":                                  # script entry
    mcp.run(transport=sys.argv[1])                          # 'stdio' | 'sse' | 'streamable-http'
```
Run: `python tsrv.py sse 8801` and `python tsrv.py streamable-http 8802` (for stdio any port number works, it is ignored).

```python
# tcli.py - client side for both HTTP transports (ran: printed 10.0 twice)
import asyncio                                              # async runtime
from mcp import ClientSession                               # session
from mcp.client.sse import sse_client                       # legacy SSE client
from mcp.client.streamable_http import streamablehttp_client   # Streamable HTTP client

async def go(cm) -> None:                                   # cm = a transport context manager
    async with cm as streams:                               # streamable client yields 3 items, sse yields 2
        r, w = streams[0], streams[1]                       # read/write streams are the first two
        async with ClientSession(r, w) as s:                # protocol session over any transport
            await s.initialize()                            # handshake
            res = await s.call_tool("get_duty_rate", {"hs_code": "1"})   # call tool
            print(res.content[0].text)                      # -> 10.0

async def main() -> None:                                   # try both transports
    await go(sse_client("http://127.0.0.1:8801/sse"))       # legacy: GET /sse
    await go(streamablehttp_client("http://127.0.0.1:8802/mcp"))   # modern: POST /mcp

asyncio.run(main())                                         # run
```

## 💻 Code Example — Advanced
```python
# gateway.py - production-style: stateless Streamable HTTP inside FastAPI, with typed error handling
import contextlib                                           # lifespan helper
import logging                                              # server logs (never print to stdout on stdio!)
from fastapi import FastAPI                                 # web app
from mcp.server.fastmcp import FastMCP                      # MCP server

log = logging.getLogger("tariff")                           # module logger

mcp = FastMCP(                                              # configure for horizontal scaling
    "tariff-prod",
    stateless_http=True,                                    # no per-session memory -> any replica works
    json_response=True,                                     # plain JSON replies (simpler proxies/caching)
)

@mcp.tool()                                                 # async tool
async def get_duty_rate(hs_code: str) -> float:             # typed
    """Duty percent for an HS code."""
    if not hs_code.isdigit():                               # validate untrusted LLM input
        raise ValueError("hs_code must be digits")          # becomes isError result (no 500)
    log.info("lookup %s", hs_code)                          # log to stderr/handlers
    return 10.0                                             # replace with async DB call

@contextlib.asynccontextmanager                             # MCP needs its session manager running
async def lifespan(app: FastAPI):                           # FastAPI lifespan
    async with mcp.session_manager.run():                   # start/stop MCP task group
        yield                                               # serve

app = FastAPI(lifespan=lifespan)                            # main app (add auth middleware here)
app.mount("/tariff", mcp.streamable_http_app())            # endpoint = POST /tariff/mcp (verified for /mcp-app/mcp)
```
Token usage: transport does not change LLM tokens; `json_response=True` vs SSE streaming only changes how bytes travel. Error handling: connection errors surface as exceptions in the client; wrap with retry + timeout. Async: all HTTP transports are async.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| stdio | `transport: "stdio"` (verified) | supported (verify docs) | `MCPServerStdio` (verified import) | stdio params (verify) |
| Streamable HTTP | `transport: "streamable_http"` (check adapter docs) | supported (verify) | `MCPServerStreamableHttp` (verified signature) | HTTP params (verify) |
| Legacy SSE | adapter option | verify | `MCPServerSse` | verify |
| Notes | Uses `mcp` client under the hood | - | Has retry/backoff params on HTTP class | - |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `print("debug")` in a stdio server.
✅ Correct: stdout is protocol-only. Use `logging` (stderr).

❌ Mistake 2: Starting new servers on SSE for new projects.
✅ Correct: SSE transport is deprecated; use Streamable HTTP (SSE only for legacy clients).

❌ Mistake 3: Stateful HTTP sessions behind a round-robin load balancer.
✅ Correct: Use `stateless_http=True`, or sticky sessions on `Mcp-Session-Id`.

❌ Mistake 4: Binding an unauthenticated HTTP server to 0.0.0.0.
✅ Correct: Bind to localhost, validate Origin/Host headers, add OAuth/API-key auth.

---

## 🧠 Tricky Interview Question
"Your MCP server works in Claude Desktop but fails when deployed to Kubernetes with 3 replicas. Why?"

Answer: Desktop used stdio (one process, one client, in-memory state). On Kubernetes, with Streamable HTTP in stateful mode the `Mcp-Session-Id` created on replica A is unknown to replica B, so follow-up requests fail with session errors. Fix: stateless mode (no server-side session; keep state in Redis/DB), or sticky routing, plus proper `lifespan` startup, health checks, and auth. Features that need server-initiated requests (sampling, elicitation) are harder in stateless mode - design accordingly.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which transport for a local desktop tool?
A1: stdio - simplest, no network, process lifetime tied to the host.

Q2: [Medium] SSE vs Streamable HTTP?
A2: SSE needs two channels (GET stream + POST endpoint) and long-lived connections. Streamable HTTP uses one endpoint, can answer with plain JSON or upgrade to a stream, and supports stateless scaling. SSE is deprecated.

Q3: [Hard] Why can't stdio servers write logs to stdout?
A3: Messages are newline-delimited JSON-RPC on stdout; extra text corrupts framing and the client fails to parse. Logs go to stderr.

Q4: [Hard] What are security concerns for local HTTP servers?
A4: DNS rebinding and browser-based requests to localhost. Validate `Origin`/`Host` (the SDK has transport security settings), bind 127.0.0.1, require auth.

Q5: [System Design] Serve 1k req/s of tariff lookups via MCP.
A5: Stateless Streamable HTTP, JSON responses, N replicas behind an L7 LB with HPA, connection pooling to the DB, cached rate table, per-client rate limiting, OAuth at the gateway, metrics per tool (latency, error rate).

---

## 💰 Cost Impact
Transport has no effect on LLM tokens. Infra cost: stdio = zero extra infra; HTTP = a service to run (small container, e.g. well under one vCPU for light tools - estimate, measure yourself). Stateless HTTP lets you autoscale to zero/low. Tip: avoid one-process-per-user stdio servers at scale; process spawn cost and memory add up.

---

## 🔷 When to Use
✅ Use stdio when: local tools, desktop hosts, quick dev, single user.
✅ Use Streamable HTTP when: shared/remote servers, multi-user, cloud deployment.
✅ Use SSE only when: a legacy client cannot do Streamable HTTP.

❌ Avoid stdio when:
- Many concurrent users need one shared server
- Server must run in a different network/zone

---

## 📊 Visual Diagram
```
 stdio:     [Host]--spawn-->[server.py]      stdin/stdout (same machine)

 HTTP:      [Host]--POST /mcp-->[LB]--+-->[replica 1]
                                      +-->[replica 2]   (stateless)
                                      +-->[replica 3]

 Legacy:    [Host]==GET /sse (stream)==>[server]
            [Host]--POST /messages/-->[server]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stdio | stdin/stdout pipe to child process | मानक input/output |
| Streamable HTTP | Single-endpoint HTTP transport | एक endpoint वाला HTTP |
| SSE | Server-Sent Events stream | server से events की धारा |
| Stateless | No server-side session | बिना session याद रखे |
| Mcp-Session-Id | Header identifying a session | session पहचान header |

---

## ⚡ 3-Line Summary
English: stdio for local, Streamable HTTP for remote, SSE is legacy. Same server code can run on all three. Use stateless HTTP to scale horizontally.
Hindi: Local के लिए stdio, remote के लिए Streamable HTTP, SSE पुराना है। वही server code तीनों पर चल सकता है। Horizontal scaling के लिए stateless HTTP इस्तेमाल करें।

---

## ➡️ Next Topic
**005. MCP Primitives (Tools, Resources, Prompts, Sampling)** - the four things a server and client can actually exchange over these transports.

---
