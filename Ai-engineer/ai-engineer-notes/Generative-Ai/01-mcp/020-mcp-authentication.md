---

# 20. MCP Authentication
# हिंदी में: MCP Authentication (पहचान और अनुमति)
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0, `uvicorn` 0.54.0, `httpx` 0.28.1, `langchain-mcp-adapters` 0.3.2, `openai-agents` 0.24.0. A Streamable HTTP server with `TokenVerifier` + `AuthSettings` was run on localhost; observed: 401 + `WWW-Authenticate` without a token, `/.well-known/oauth-protected-resource` metadata, valid-token tool calls, and per-tool scope checks. NOT run: a real OAuth authorization server (login, PKCE, token exchange, refresh) - needs an identity provider such as Entra/Auth0/Keycloak. stdio servers have no HTTP auth (they inherit the host's trust).

---

## 🔵 Simple Definition (2-3 lines)
For remote (HTTP) MCP servers the standard approach is OAuth 2.x: the MCP server is a **resource server** that only accepts `Authorization: Bearer <token>`; a separate **authorization server** issues the tokens. The server verifies each token (`TokenVerifier`), checks scopes, and advertises where to get tokens via protected-resource metadata.

## 🔵 सरल परिभाषा (Hindi)
Remote (HTTP) MCP servers के लिए मानक तरीका OAuth 2.x है: MCP server एक **resource server** है जो सिर्फ़ `Authorization: Bearer <token>` स्वीकार करता है; tokens एक अलग **authorization server** जारी करता है। Server हर token verify करता है (`TokenVerifier`), scopes जाँचता है, और protected-resource metadata से बताता है कि token कहाँ से मिलेगा।

---

## 🔴 Problem it Solves
An open HTTP MCP endpoint lets anyone list and call your tools - including `update_rate`. Without per-user identity you also cannot audit who changed what or rate-limit one noisy agent.

## 🔴 यह क्यों बना? (Hindi)
खुला HTTP MCP endpoint किसी को भी आपके tools list और call करने देता है - `update_rate` समेत। हर user की पहचान के बिना आप audit नहीं कर सकते कि किसने क्या बदला, और न ही एक शोर मचाने वाले agent को rate-limit कर सकते हैं।

---

## 🟢 How it Works

```
Step 1 -> Client POST /mcp without token
Step 2 -> Server: 401 + WWW-Authenticate: Bearer ... resource_metadata=".../.well-known/oauth-protected-resource"
Step 3 -> Client reads metadata -> finds the authorization server (issuer)
Step 4 -> Client runs OAuth (authorization code + PKCE) -> gets access token (not run here)
Step 5 -> Client sends Authorization: Bearer <token> on every request
Step 6 -> Server TokenVerifier.verify_token(token) -> AccessToken(client_id, scopes) or None (401)
Step 7 -> Tool code checks scopes (get_access_token()) for sensitive tools
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Client बिना token के POST /mcp भेजता है
Step 2 -> Server: 401 + WWW-Authenticate: Bearer ... resource_metadata=".../.well-known/oauth-protected-resource"
Step 3 -> Client metadata पढ़कर authorization server (issuer) ढूँढता है
Step 4 -> Client OAuth (authorization code + PKCE) चलाकर access token लेता है (यहाँ run नहीं किया)
Step 5 -> हर request पर Authorization: Bearer <token>
Step 6 -> Server TokenVerifier.verify_token(token) -> AccessToken(client_id, scopes) या None (401)
Step 7 -> संवेदनशील tools में code scopes जाँचता है (get_access_token())
```

---

## 🟡 Real World Example
**Tariff Agent**: analysts get tokens with `tariff:read`; only the pricing admin's token has `tariff:write`. When an analyst's agent tries `update_rate`, the tool refuses; the audit log shows `client_id=analyst`.

## 🟡 Real Example Hindi mein
**Tariff Agent**: analysts को `tariff:read` वाले tokens मिलते हैं; सिर्फ़ pricing admin के token में `tariff:write` है। Analyst का agent `update_rate` आज़माए तो tool मना कर देता है; audit log में `client_id=analyst` दिखता है।

---

## 💻 Code Example — Basic
```python
# basic_auth_server.py - minimal bearer-protected MCP server (ran: no token 401, bad token 401, good token -> pong)
import asyncio, httpx, uvicorn                              # runner + HTTP client for the demo
from mcp import ClientSession                               # MCP client session
from mcp.client.streamable_http import streamablehttp_client   # HTTP transport (accepts headers=)
from mcp.server.auth.provider import AccessToken, TokenVerifier   # verifier interface
from mcp.server.auth.settings import AuthSettings           # resource-server settings
from mcp.server.fastmcp import FastMCP                      # server helper

class StaticVerifier(TokenVerifier):                        # replace with JWT / introspection in production
    async def verify_token(self, token: str) -> AccessToken | None:
        if token == "secret-123":                           # demo secret
            return AccessToken(token=token, client_id="tariff-client", scopes=["tariff:read"], expires_at=None)
        return None                                         # anything else -> 401

mcp = FastMCP("tariff-auth", token_verifier=StaticVerifier(), port=8765,
    auth=AuthSettings(issuer_url="https://auth.example.com",         # your authorization server URL
                      resource_server_url="http://localhost:8765",   # canonical URL of this server
                      required_scopes=["tariff:read"]))              # every request needs this scope

@mcp.tool()                                                 # a tool behind auth
def ping() -> str:
    """ping"""
    return "pong"

async def main() -> None:
    srv = uvicorn.Server(uvicorn.Config(mcp.streamable_http_app(), port=8765, log_level="error"))
    task = asyncio.create_task(srv.serve())                 # run the server in the background
    while not srv.started:                                  # wait until it listens
        await asyncio.sleep(0.05)
    async with httpx.AsyncClient() as h:
        r = await h.post("http://localhost:8765/mcp", json={})          # no token
        print("no token", r.status_code, r.headers.get("www-authenticate"))
        r = await h.post("http://localhost:8765/mcp", json={}, headers={"Authorization": "Bearer bad"})
        print("bad", r.status_code)                         # 401
    async with streamablehttp_client("http://localhost:8765/mcp",
                                     headers={"Authorization": "Bearer secret-123"}) as (r, w, _):
        async with ClientSession(r, w) as s:                # authenticated session
            await s.initialize()
            print((await s.call_tool("ping", {})).content[0].text)      # pong
    srv.should_exit = True                                  # stop the server
    await task

asyncio.run(main())
```
Observed output: `no token 401 Bearer error="invalid_token", error_description="Authentication required", resource_metadata="http://localhost:8765/.well-known/oauth-protected-resource"`, `bad 401`, `pong`. (The SDK also logs a harmless `ClosedResourceError` from the standalone SSE writer at shutdown.)

## 💻 Code Example — Advanced
```python
# scoped_server.py - per-tool authorisation with get_access_token() (ran; same demo harness as above)
from mcp.server.auth.middleware.auth_context import get_access_token   # token of the current request
from mcp.server.auth.provider import AccessToken, TokenVerifier        # verifier interface
from mcp.server.auth.settings import AuthSettings                      # settings
from mcp.server.fastmcp import FastMCP                                 # server

TOKENS: dict[str, AccessToken] = {                          # demo token store; real: validate JWT signature, exp, aud
    "reader-123": AccessToken(token="reader-123", client_id="analyst", scopes=["tariff:read"], expires_at=None),
    "writer-456": AccessToken(token="writer-456", client_id="admin", scopes=["tariff:read", "tariff:write"], expires_at=None),
}

class StaticVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        return TOKENS.get(token)                            # None -> HTTP 401 before any tool runs

mcp = FastMCP("tariff-auth", token_verifier=StaticVerifier(), port=8765,
    auth=AuthSettings(issuer_url="https://auth.example.com",
                      resource_server_url="http://localhost:8765",
                      required_scopes=["tariff:read"]))

@mcp.tool()
def get_tariff_rate(hs_code: str) -> str:                   # read tool
    """Return duty percent for an HS code."""
    return "20%"

@mcp.tool()
def update_rate(hs_code: str, rate: float) -> str:          # write tool
    """Update a duty rate (admin only)."""
    tok = get_access_token()                                # AccessToken for THIS request (or None)
    if tok is None or "tariff:write" not in tok.scopes:     # authorise at tool level
        raise PermissionError("tariff:write scope required")   # -> isError result for the client
    return f"{hs_code} -> {rate}% by {tok.client_id}"       # include identity for audit
```
Observed results: reader calling `update_rate` -> `isError=True ... tariff:write scope required`; writer -> `6109.10 -> 5.0% by admin`. The protected-resource metadata endpoint returned `{'resource': 'http://localhost:8765/', 'authorization_servers': ['https://auth.example.com/'], 'scopes_supported': ['tariff:read'], 'bearer_methods_supported': ['header']}`. The SDK printed a DeprecationWarning that `AuthSettings.validate_token_resource` is unset - set it deliberately (True to reject tokens meant for another resource, or False if your verifier checks audience).

```python
# client_headers.py - how agent frameworks send the token (fields verified from the installed types; not run against a live server)
from agents.mcp import MCPServerStreamableHttp              # OpenAI Agents SDK
openai_srv = MCPServerStreamableHttp(params={               # params keys: url, headers, timeout, auth, ...
    "url": "https://tariff.internal/mcp", "headers": {"Authorization": "Bearer TOKEN"}})
lc_conn = {"tariff": {"transport": "streamable_http",       # langchain-mcp-adapters connection dict
                      "url": "https://tariff.internal/mcp", "headers": {"Authorization": "Bearer TOKEN"}}}
```
Token usage: auth adds zero LLM tokens - never put tokens in prompts. Error handling: 401 -> refresh token and retry once; 403/insufficient scope -> surface to the user. Async: verifier is `async`, so it can call an introspection endpoint (cache results!).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Send bearer header | `headers` in connection dict (verified key) | verify docs | `params["headers"]` (verified key) | verify |
| Custom `httpx` auth | `auth` / `httpx_client_factory` keys (verified) | verify | `auth`, `httpx_client_factory` keys (verified) | verify |
| OAuth flow helper | use `mcp` client auth provider | verify | use `mcp` client auth provider | verify |
| Per-user tokens | build connection per request | verify | build server per request | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Binding an open HTTP MCP server to `0.0.0.0` "for now".
✅ Correct: Auth from day one, even a static verifier.

❌ Mistake 2: One shared admin token for every agent.
✅ Correct: Per-agent/user tokens with minimal scopes.

❌ Mistake 3: Passing the user's token through to a downstream API (token passthrough).
✅ Correct: Server validates tokens meant for itself (audience) and uses its own credentials downstream.

❌ Mistake 4: Putting secrets in tool arguments or prompts.
✅ Correct: Secrets in headers/env only; the model never sees them.

---

## 🧠 Tricky Interview Question
"Your MCP server validates tokens, yet an intern's agent deleted production rates. How?"

Answer: Authentication only proved who the caller was; there was no authorisation per tool. Coarse scopes (`tariff:read` implied write) or a shared token let any holder call destructive tools. Fix: scope-per-capability (`tariff:write`), check it inside the tool (as above), separate read-only and write servers, require human approval for writes, mark tools with annotations (`destructiveHint`), and log `client_id` for every call.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Does stdio MCP use OAuth?
A1: No. A stdio server runs as the user's child process and inherits trust and environment; credentials usually come from env vars.

Q2: [Medium] What does the 401 response tell the client?
A2: `WWW-Authenticate` with `resource_metadata` pointing to the protected-resource document, which names the authorization server(s) and scopes.

Q3: [Hard] Why is token passthrough dangerous?
A3: Confused-deputy risk: the server would accept tokens issued for other services and forward them downstream, bypassing audience checks and audit.

Q4: [Hard] Where do you check scopes - gateway or tool?
A4: Both: gateway for coarse access, tool for fine-grained decisions (user, resource, value limits).

Q5: [System Design] 200 agents, 12 MCP servers, enterprise SSO.
A5: IdP issues short-lived tokens with audience per server; gateway validates and rate-limits; scopes per tool group; token cache for introspection; audit log with client_id and tool name; rotation and revocation process.

---

## 💰 Cost Impact
No token cost from auth itself. Infra/latency: verifying a JWT locally is microseconds-to-milliseconds; remote introspection adds a network call per request unless cached (estimate - measure). Failed auth retries waste time, not tokens. Misconfigured auth can cause expensive runaway usage by unauthorised callers, which is a real cost risk.

---

## 🔷 When to Use
✅ Use when:
- Any HTTP-exposed MCP server, multi-user or multi-agent

❌ Avoid (extra complexity) when:
- A single-user stdio server on your laptop

---

## 📊 Visual Diagram
```
 Agent --POST /mcp (no token)--> MCP server --401 + metadata--> Agent
 Agent --OAuth (PKCE)--> Authorization Server --access token--> Agent
 Agent --Bearer token--> MCP server --verify_token()--> AccessToken(scopes)
                                         |-- get_tariff_rate  (tariff:read)
                                         '-- update_rate      (tariff:write)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Resource server | Server that protects resources | संसाधन की रक्षा करने वाला server |
| Authorization server | Issues tokens | token जारी करने वाला server |
| Bearer token | Token sent in Authorization header | Authorization header में token |
| Scope | Permission label | अनुमति का लेबल |
| PKCE | Safe code-exchange extension | सुरक्षित code विनिमय |

---

## ⚡ 3-Line Summary
English: Remote MCP servers act as OAuth resource servers: verify the bearer token, then check scopes per tool. stdio servers rely on process trust. Never pass tokens through or put them in prompts.
Hindi: Remote MCP servers OAuth resource server की तरह काम करते हैं: bearer token verify करें, फिर हर tool पर scopes जाँचें। stdio servers process के भरोसे पर चलते हैं। Token कभी passthrough न करें और prompts में न डालें।

---

## ➡️ Next Topic
**021. MCP Security** - beyond auth: prompt injection, tool poisoning, DNS rebinding and least privilege.

---
