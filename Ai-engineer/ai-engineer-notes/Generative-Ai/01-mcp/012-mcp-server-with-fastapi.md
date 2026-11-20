---

# 12. MCP Server with FastAPI
# हिंदी में: FastAPI के साथ MCP Server
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0, `fastapi` 0.163.0, `uvicorn` 0.54.0, `starlette` 1.10.0, `httpx` 0.28.1. Both examples below ran under a real `uvicorn` process on localhost and were called by an MCP Streamable HTTP client. Not run: multi-replica deployment, TLS, OAuth, and any real LLM host (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
`FastMCP` can produce an ASGI app (`mcp.streamable_http_app()`). You mount that app inside a normal FastAPI application, so one process serves your REST endpoints, health checks, auth middleware **and** an MCP endpoint over Streamable HTTP. The one catch: the MCP session manager must be started in FastAPI's `lifespan`.

## 🔵 सरल परिभाषा (Hindi)
`FastMCP` एक ASGI app (`mcp.streamable_http_app()`) बना सकता है। उसे आप सामान्य FastAPI application में mount करते हैं, ताकि एक process आपके REST endpoints, health checks, auth middleware **और** Streamable HTTP पर MCP endpoint, सब serve करे। एक शर्त: MCP session manager को FastAPI के `lifespan` में शुरू करना ज़रूरी है।

---

## 🔴 Problem it Solves
stdio servers only work on the same machine and for one user. A team needs a **shared remote** MCP server with authentication, health probes, metrics and the same deployment pipeline as their other FastAPI services. Running a separate bare MCP process means duplicating auth, logging and ops. Mounting into FastAPI reuses all of it.

## 🔴 यह क्यों बना? (Hindi)
stdio servers सिर्फ़ उसी machine पर और एक user के लिए चलते हैं। Team को **साझा remote** MCP server चाहिए जिसमें authentication, health probes, metrics और बाकी FastAPI services जैसी deployment pipeline हो। अलग bare MCP process चलाने से auth, logging और ops दोहराने पड़ते हैं। FastAPI में mount करने से ये सब दोबारा इस्तेमाल हो जाता है।

---

## 🟢 How it Works

```
Step 1 -> mcp = FastMCP("name", stateless_http=True, json_response=True)
Step 2 -> register tools/resources/prompts on mcp
Step 3 -> lifespan: async with mcp.session_manager.run(): yield     (REQUIRED - starts MCP's task group)
Step 4 -> app = FastAPI(lifespan=lifespan)
Step 5 -> app.mount("/tariff", mcp.streamable_http_app())            -> endpoint = POST /tariff/mcp
Step 6 -> add auth middleware on the /tariff prefix, plus /health for the load balancer
Step 7 -> run: uvicorn module:app ; clients connect with streamablehttp_client(url, headers=...)
```

Mount path rule (verified): mounting at `/tariff` gives the MCP URL `/tariff/mcp` because the inner app serves `/mcp`.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> mcp = FastMCP("name", stateless_http=True, json_response=True)
Step 2 -> mcp पर tools/resources/prompts register करें
Step 3 -> lifespan: async with mcp.session_manager.run(): yield     (ज़रूरी - MCP का task group शुरू करता है)
Step 4 -> app = FastAPI(lifespan=lifespan)
Step 5 -> app.mount("/tariff", mcp.streamable_http_app())            -> endpoint = POST /tariff/mcp
Step 6 -> /tariff prefix पर auth middleware, और load balancer के लिए /health जोड़ें
Step 7 -> चलाएँ: uvicorn module:app ; clients streamablehttp_client(url, headers=...) से जुड़ते हैं
```

Mount path नियम (verified): `/tariff` पर mount करने से MCP URL `/tariff/mcp` बनता है क्योंकि अंदर का app `/mcp` serve करता है।

---

## 🟡 Real World Example
**Tariff Agent**: the platform team deploys `gateway:app` (FastAPI) on Kubernetes. `/health` serves the readiness probe, `/tariff/mcp` is the MCP endpoint protected by an `x-api-key` header (swap for OAuth in production), and `/docs` stays available for ordinary REST routes. Agents from LangGraph, CrewAI, the OpenAI Agents SDK or AutoGen connect to the same URL.

## 🟡 Real Example Hindi mein
**Tariff Agent**: platform team `gateway:app` (FastAPI) को Kubernetes पर deploy करती है। `/health` readiness probe देता है, `/tariff/mcp` MCP endpoint है जो `x-api-key` header से सुरक्षित है (production में OAuth लगाएँ), और `/docs` सामान्य REST routes के लिए बना रहता है। LangGraph, CrewAI, OpenAI Agents SDK या AutoGen के agents उसी URL से जुड़ते हैं।

---

## 💻 Code Example — Basic
```python
# fa.py - minimal mount (ran under uvicorn; client printed {'result': 5})
import contextlib                                           # for the lifespan helper
from fastapi import FastAPI                                 # web framework
from mcp.server.fastmcp import FastMCP                      # MCP server

mcp = FastMCP("tariff-http", stateless_http=True, json_response=True)   # stateless: any replica can answer; JSON replies

@mcp.tool()                                                 # one demo tool
def add(a: int, b: int) -> int:                             # typed arguments
    """Add two numbers."""                                  # description for the LLM
    return a + b                                            # result

@contextlib.asynccontextmanager                             # MCP's session manager must run during the app's life
async def lifespan(app: FastAPI):                           # FastAPI lifespan hook
    async with mcp.session_manager.run():                   # start MCP internals (without this, requests fail)
        yield                                               # app serves while we wait here

app = FastAPI(lifespan=lifespan)                            # FastAPI app

@app.get("/health")                                         # plain REST route next to MCP
def health() -> dict[str, str]:                             # typed
    return {"ok": "yes"}                                    # readiness response

app.mount("/mcp-app", mcp.streamable_http_app())            # MCP endpoint = /mcp-app/mcp
```
Run: `uvicorn fa:app --port 8821`. Client (ran): `streamablehttp_client("http://127.0.0.1:8821/mcp-app/mcp")` then `call_tool("add", {"a": 2, "b": 3})` -> `{'result': 5}`; `GET /health` -> `{"ok":"yes"}`.

## 💻 Code Example — Advanced
```python
# gateway.py - API-key protected, typed, logged MCP endpoint inside FastAPI (ran under uvicorn)
import contextlib                                           # lifespan helper
import hmac                                                 # constant-time key comparison
import logging                                              # audit logs
import os                                                   # read the secret from the environment
from collections.abc import AsyncIterator                   # lifespan type
from fastapi import FastAPI                                 # web framework
from mcp.server.fastmcp import FastMCP                      # MCP server
from starlette.responses import JSONResponse                # 401 body
from starlette.types import ASGIApp, Receive, Scope, Send   # ASGI types

log = logging.getLogger("tariff.gateway")                   # logger
API_KEY: str = os.environ.get("TARIFF_API_KEY", "dev-key")  # NEVER hard-code a real key; env/secret manager in production
RATES: dict[str, float] = {"8517": 0.0, "6403": 10.0}       # demo data

mcp = FastMCP("tariff-http", stateless_http=True, json_response=True)   # horizontally scalable settings

@mcp.tool()                                                 # async tool
async def get_duty_rate(hs_code: str) -> float:             # typed
    """Return the duty percent for a 4-digit HS code."""
    if hs_code not in RATES:                                # validate input
        raise ValueError(f"unknown HS code {hs_code}")      # -> isError result (LLM can retry)
    return RATES[hs_code]                                   # structured float

class ApiKeyMiddleware:                                     # pure ASGI middleware (safe for streaming responses)
    def __init__(self, app: ASGIApp, protected_prefix: str) -> None:   # config
        self.app = app                                      # next app
        self.prefix = protected_prefix                      # path prefix to guard

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:   # ASGI entry
        if scope["type"] == "http" and scope["path"].startswith(self.prefix):   # only guard MCP routes
            headers = dict(scope["headers"])                # raw header pairs (bytes)
            supplied = headers.get(b"x-api-key", b"").decode()   # client's key or ""
            if not hmac.compare_digest(supplied, API_KEY):  # constant-time compare
                log.warning("rejected request to %s", scope["path"])   # audit
                await JSONResponse({"error": "invalid api key"}, status_code=401)(scope, receive, send)   # reject early
                return                                      # do not reach MCP
        await self.app(scope, receive, send)                # allowed (or non-guarded) -> continue

@contextlib.asynccontextmanager                             # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:    # typed
    async with mcp.session_manager.run():                   # start/stop MCP
        yield                                               # serve

app = FastAPI(lifespan=lifespan)                            # app
app.add_middleware(ApiKeyMiddleware, protected_prefix="/tariff")   # guard /tariff/*

@app.get("/health")                                         # unauthenticated probe
async def health() -> dict[str, str]:                       # async + typed
    return {"status": "ok"}                                 # for k8s readiness

app.mount("/tariff", mcp.streamable_http_app())             # MCP URL = /tariff/mcp
```
Client (ran against `uvicorn gateway:app --port 8822`):
```python
# gwclient.py - authenticated Streamable HTTP client with error handling
import asyncio                                              # runtime
import httpx                                                # health check
from mcp import ClientSession                               # session
from mcp.client.streamable_http import streamablehttp_client   # HTTP transport

URL = "http://127.0.0.1:8822/tariff/mcp"                    # mounted path + /mcp

async def call(key: str | None) -> None:                    # try one call with a key
    headers = {"x-api-key": key} if key else {}             # auth header
    try:                                                    # connection/auth errors surface as exceptions
        async with streamablehttp_client(URL, headers=headers) as (r, w, _):   # third item is the session-id getter
            async with ClientSession(r, w) as s:            # protocol session
                await s.initialize()                        # handshake
                res = await s.call_tool("get_duty_rate", {"hs_code": "6403"})   # call
                print("OK", res.structuredContent)          # {'result': 10.0}
    except Exception as exc:                                # wrong key -> ExceptionGroup in this SDK version
        print("FAILED", type(exc).__name__)                 # log and retry/alert in production

async def main() -> None:                                   # driver
    print(httpx.get("http://127.0.0.1:8822/health").json()) # {'status': 'ok'}
    await call("dev-key")                                   # OK {'result': 10.0}
    await call("wrong")                                     # FAILED ExceptionGroup (server logged a 401)

asyncio.run(main())                                         # run
```
Ran output: `{'status': 'ok'}`, `OK {'result': 10.0}`, `FAILED ExceptionGroup`; a raw `curl -X POST /tariff/mcp` without a key returned HTTP `401`. Token usage: the HTTP layer adds no LLM tokens; the same tool schema cost applies as for stdio. Not run: TLS, OAuth, rate limiting, and multiple replicas.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Connect to this HTTP MCP URL | Adapter with `transport: "streamable_http"` and `headers` (verify adapter docs) | MCP integration with a URL (verify) | `MCPServerStreamableHttp(params={"url": ..., "headers": {...}})` (class existed in an earlier check; confirm params) | HTTP MCP params (verify) |
| Auth headers | Pass in connection config | Same | Same | Same |
| Run the server itself | Independent of agent framework | Same | Same | Same |

The server is the same regardless; what differs is how each framework passes the URL and headers.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Forgetting `mcp.session_manager.run()` in the lifespan.
✅ Correct: Always start it; mounted sub-apps do not run their own lifespan.

❌ Mistake 2: Wrong URL (`/tariff` instead of `/tariff/mcp`).
✅ Correct: Mount path + the inner `/mcp`.

❌ Mistake 3: `BaseHTTPMiddleware` for auth on a streaming MCP endpoint.
✅ Correct: Use a pure ASGI middleware like above (BaseHTTPMiddleware can interfere with streaming responses).

❌ Mistake 4: Stateful sessions behind a round-robin load balancer.
✅ Correct: `stateless_http=True` or sticky routing on `Mcp-Session-Id`.

❌ Mistake 5: Hard-coded or shared API keys, plain HTTP on the internet.
✅ Correct: Secrets from env/secret manager, TLS at the ingress, OAuth/JWT with per-user scopes, validate `Origin`/`Host` for local servers.

---

## 🧠 Tricky Interview Question
"You mounted the MCP app in FastAPI and every request returns an error like 'Task group is not initialized'. Locally, `mcp.run()` worked. What is wrong?"

Answer: When you mount `streamable_http_app()` inside another ASGI app, the sub-app's own lifespan does not run, so the MCP session manager never starts. Fix: start it in the parent's lifespan with `async with mcp.session_manager.run(): yield`. Also confirm the URL includes the mount prefix plus `/mcp`. (We saw the working configuration; the exact error text can vary by SDK version.)

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you serve MCP over HTTP from Python?
A1: `mcp.run(transport="streamable-http")` for a standalone server, or mount `mcp.streamable_http_app()` into FastAPI/Starlette.

Q2: [Medium] Why `stateless_http=True`?
A2: No per-session server memory, so any replica can serve any request; required for simple horizontal scaling. Trade-off: server-initiated features (sampling, long-lived notifications) are limited.

Q3: [Hard] Why pure ASGI middleware?
A3: It does not buffer or wrap the response body, so streamed MCP responses are not disturbed; `BaseHTTPMiddleware` wraps responses and can cause issues with streaming.

Q4: [Hard] How do you do per-user authorization on tools?
A4: Authenticate in middleware, store the user in a request-scoped context (contextvar), and check permissions inside each tool; never trust identities supplied as tool arguments by the LLM.

Q5: [System Design] 500 concurrent agents, 20 tools, SLA 99.9%.
A5: Stateless replicas behind an L7 balancer with autoscaling, connection pooling to backends, request timeouts and circuit breakers, API gateway for OAuth and rate limits, metrics per tool, structured audit logs, canary deploys, contract tests.

---

## 💰 Cost Impact
LLM tokens are unaffected by HTTP vs stdio. Infrastructure: one small FastAPI container can host both REST and MCP; stateless mode lets you autoscale and scale to a minimum. Rough sizing must be measured under your load (no numbers claimed here). Tips: cache hot lookups, keep tool responses small (they re-enter the LLM context), and use one gateway for many MCP servers instead of many idle pods.

---

## 🔷 When to Use
✅ Use when:
- A shared, remote, authenticated MCP server is needed
- You already operate FastAPI (auth, logging, probes)

❌ Avoid when:
- Only a local desktop user needs it (stdio is simpler and safer)
- You cannot provide auth and TLS

---

## 📊 Visual Diagram
```
 Agents (LangGraph / CrewAI / OpenAI SDK / AutoGen)
        | POST /tariff/mcp   (x-api-key)
        v
 +-------------------- FastAPI app --------------------+
 | ApiKeyMiddleware(/tariff)  -- 401 if key invalid    |
 |    +--> mounted MCP app (stateless, JSON)           |
 |            tools: get_duty_rate                     |
 | GET /health  (no auth)                              |
 | lifespan: mcp.session_manager.run()                 |
 +------------------------------------------------------+
        replicas x N behind a load balancer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| streamable_http_app | ASGI app serving MCP over HTTP | HTTP पर MCP देने वाला ASGI app |
| session_manager | MCP's HTTP session engine | MCP का HTTP session engine |
| lifespan | App startup/shutdown hook | app startup/shutdown hook |
| stateless_http | No server-side session memory | server में session याद नहीं |
| ASGI middleware | Request filter around an app | request छानने वाली परत |

---

## ⚡ 3-Line Summary
English: Mount `mcp.streamable_http_app()` inside FastAPI and start `session_manager.run()` in the lifespan. Add pure-ASGI auth, a health route and stateless mode. The MCP URL is mount path plus `/mcp`.
Hindi: `mcp.streamable_http_app()` को FastAPI में mount करें और lifespan में `session_manager.run()` चलाएँ। Pure-ASGI auth, health route और stateless mode जोड़ें। MCP URL = mount path + `/mcp`।

---

## ➡️ Next Topic
**013. MCP Client Integration** - how your agent (the host) connects to many servers, merges their tools and routes calls.

---
