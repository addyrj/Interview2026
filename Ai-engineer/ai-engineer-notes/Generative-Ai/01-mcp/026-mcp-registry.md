---

# 26. MCP Registry
# हिंदी में: MCP Registry (servers की सूची और खोज)
# Framework: MCP
# Already Known: No

> Verified against: `fastapi` 0.163.0, `pydantic` 2.14.3, `mcp` 1.30.0. Ran locally: an **internal** registry service (publish, immutable versions, search, resolve latest approved version, hash verification) and a client that resolved an entry, checked the file hash, launched the server over stdio and compared its tool list with the registry contract. **NOT run / NOT verified: the public official MCP Registry** (my background knowledge: a community-driven registry service run under the MCP project, launched in preview in 2025, using a `server.json` metadata format, namespaced names, and a `mcp-publisher` CLI; the exact URL, schema fields, API paths and CLI flags must be checked on modelcontextprotocol.io before use - I did not call it, and the schema below is my own, not the official one). Also not run: real LLM use.

---

## 🔵 Simple Definition (2-3 lines)
An MCP registry is a catalogue of MCP servers: name, version, how to run or reach it (package or URL), owner and metadata. Clients and platform teams use it to **discover** servers and **resolve** them to a launch config, instead of copy-pasting commands from blog posts. A public registry covers the ecosystem; companies run a private one for approved servers.

## 🔵 सरल परिभाषा (Hindi)
MCP registry MCP servers की सूची (catalogue) है: नाम, version, कैसे चलाएँ या कहाँ पहुँचें (package या URL), मालिक और metadata। Clients और platform teams इससे servers **खोजते** हैं और उन्हें launch config में **resolve** करते हैं, blog posts से commands कॉपी करने की जगह। Public registry पूरे ecosystem को कवर करती है; कंपनियाँ approved servers के लिए private registry चलाती हैं।

---

## 🔴 Problem it Solves
Without a registry, teams find servers by Google, run `npx -y random-package`, and nobody knows which servers touch production data or who owns them. A registry gives one place for discovery, versions, ownership, approval status (approved/deprecated/blocked) and integrity checks.

## 🔴 यह क्यों बना? (Hindi)
Registry के बिना teams Google से servers ढूँढती हैं, `npx -y random-package` चलाती हैं, और किसी को पता नहीं होता कि कौन-से servers production data छूते हैं या उनका मालिक कौन है। Registry discovery, versions, ownership, approval status (approved/deprecated/blocked) और integrity checks के लिए एक जगह देती है।

---

## 🟢 How it Works

```
Publisher side
Step 1 -> Author writes metadata (name, version, transport, package/url, owner, tools)
Step 2 -> Publishes to registry (auth required); versions are immutable (ran: 2nd publish -> 409)
Step 3 -> Security review sets status=approved (or deprecated/blocked)

Consumer side
Step 4 -> Search: GET /servers?q=tariff (only approved by default)
Step 5 -> Resolve: GET /servers/acme/tariff/latest -> newest approved semver (ran: 1.10.0 > 1.2.0)
Step 6 -> Verify: sha256 of the launched file == registry hash (ran: mismatch refuses)
Step 7 -> Launch/connect, list_tools, compare with registered tool contract (ran: contract ok)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Publisher की तरफ
Step 1 -> Author metadata लिखता है (name, version, transport, package/url, owner, tools)
Step 2 -> Registry में publish (auth ज़रूरी); versions अपरिवर्तनीय (run: दूसरा publish -> 409)
Step 3 -> Security review status=approved (या deprecated/blocked) करती है

Consumer की तरफ
Step 4 -> Search: GET /servers?q=tariff (default में सिर्फ़ approved)
Step 5 -> Resolve: GET /servers/acme/tariff/latest -> सबसे नया approved semver (run: 1.10.0 > 1.2.0)
Step 6 -> Verify: launch होने वाली file का sha256 == registry का hash (run: mismatch पर मना)
Step 7 -> Launch/connect, list_tools, registered tool contract से मिलान (run: contract ok)
```

---

## 🟡 Real World Example
**Tariff Agent platform**: 15 teams publish MCP servers to the company registry. The Tariff agent config says only `acme/tariff@^1`; the platform resolves the newest approved 1.x, verifies the hash, and refuses to start if the server's tools differ from the registered contract. When a vulnerability is found, the platform marks the version `blocked` and every agent stops using it on next resolve.

## 🟡 Real Example Hindi mein
**Tariff Agent platform**: 15 teams company registry में MCP servers publish करती हैं। Tariff agent की config कहती है सिर्फ़ `acme/tariff@^1`; platform सबसे नया approved 1.x resolve करता है, hash verify करता है, और server के tools registered contract से अलग हों तो start करने से मना करता है। Vulnerability मिलने पर platform version को `blocked` कर देता है और हर agent अगले resolve पर उसे छोड़ देता है।

---

## 💻 Code Example — Basic
```python
# basic_registry_entry.py - the metadata a registry entry needs (our own illustrative shape; ran)
from pydantic import BaseModel                              # validation

class Entry(BaseModel):                                     # NOT the official server.json schema
    name: str                                               # unique namespaced name, e.g. "acme/tariff"
    version: str                                            # immutable once published
    transport: str                                          # "stdio" or "streamable_http"
    command: str | None = None                              # how to launch (stdio)
    url: str | None = None                                  # where to connect (HTTP)
    owner: str                                              # accountable team
    tools: list[str]                                        # expected tool names

e = Entry(name="acme/tariff", version="1.2.0", transport="stdio",
          command="python", owner="customs-team", tools=["get_tariff_rate", "calc_duty"])
print(e.model_dump_json())                                  # what you would POST to the registry
```

## 💻 Code Example — Advanced
```python
# internal_registry.py - tiny internal registry with FastAPI (ran with TestClient)
import hashlib                                              # hashing for supply-chain pinning
from typing import Literal                                  # restricted values
from fastapi import FastAPI, HTTPException, Query           # web layer
from pydantic import BaseModel, Field                       # models

class ServerEntry(BaseModel):                               # one registry record (our own shape)
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9\-/.]*$")   # e.g. "acme/tariff"
    version: str                                            # semver of the server
    description: str
    transport: Literal["stdio", "streamable_http"]
    command: str | None = None                              # for stdio
    args: list[str] = []
    url: str | None = None                                  # for streamable_http
    owner: str                                              # accountable team
    tools: list[str]                                        # expected tool names (contract)
    sha256: str | None = None                               # hash of the launched script for pinning
    status: Literal["approved", "deprecated", "blocked"] = "approved"

DB: dict[str, ServerEntry] = {}                             # real: Postgres
app = FastAPI(title="Internal MCP Registry")

@app.post("/servers", status_code=201)                      # publish (protect with auth in real life)
async def publish(entry: ServerEntry) -> dict[str, str]:
    key = f"{entry.name}@{entry.version}"
    if key in DB:                                           # versions are immutable
        raise HTTPException(409, f"{key} already exists")
    DB[key] = entry
    return {"id": key}

@app.get("/servers")                                        # search/discover
async def search(q: str = "", status: str = "approved", limit: int = Query(20, le=100)) -> list[ServerEntry]:
    hits = [e for e in DB.values() if e.status == status and (q in e.name or q in e.description)]
    return hits[:limit]

@app.get("/servers/{name:path}/latest")                     # resolve newest approved version
async def latest(name: str) -> ServerEntry:
    cands = [e for e in DB.values() if e.name == name and e.status == "approved"]
    if not cands:
        raise HTTPException(404, "no approved version")
    return max(cands, key=lambda e: tuple(int(x) for x in e.version.split(".")))   # numeric semver compare

def verify_hash(path: str, expected: str | None) -> None:   # supply-chain check before launching
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if expected and digest != expected:
        raise RuntimeError("server file hash mismatch - refusing to launch")
```

```python
# resolve_and_connect.py - consumer: resolve -> verify -> launch -> contract check (ran)
import asyncio, sys                                         # stdlib
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # stdio transport
import internal_registry as m                               # the registry module above
from fastapi.testclient import TestClient                   # call the registry in-process

c = TestClient(m.app)                                       # in production: httpx.AsyncClient to the registry URL

async def go() -> None:
    ent = m.ServerEntry(**c.get("/servers/acme/tariff/latest").json())   # resolve newest approved
    m.verify_hash(ent.args[0], ent.sha256)                  # refuse tampered files
    params = StdioServerParameters(command=ent.command or sys.executable, args=ent.args)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            got = {t.name for t in (await s.list_tools()).tools}
            print("contract ok:", got == set(ent.tools))    # tool list must match the registered contract
asyncio.run(go())
```
Observed (after publishing 1.2.0 and 1.10.0): first publish `201`, duplicate `409`; search returned versions `['1.2.0', '1.10.0']`; latest resolved `1.10.0` (a naive string compare would wrongly pick 1.2.0 - that is why we compare numeric tuples); an unknown name returned `404`; `contract ok: True`; a wrong hash raised "server file hash mismatch - refusing to launch". Token usage: none; the registry is control-plane. Error handling: 404/409 plus hash and contract checks. Async: FastAPI handlers and MCP client are async.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Built-in registry support | none known; build connection dict from your registry | verify docs | none known; build `MCPServer*` from your registry | verify |
| Consume resolved entry | `MultiServerMCPClient(conns)` (verified) | verify | `MCPServerStdio/StreamableHttp(params=...)` (verified) | verify |
| Allow-list by registry status | your code | verify | your code + `tool_filter` | verify |
| Contract check | compare `get_tools()` names | verify | compare `list_tools()` names | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Comparing versions as strings (`"1.2.0" > "1.10.0"`).
✅ Correct: Parse semver numerically (shown above).

❌ Mistake 2: Treating a public registry entry as vetted.
✅ Correct: A listing is discoverability, not a security audit; review before approving internally.

❌ Mistake 3: Mutable versions.
✅ Correct: Immutable versions, new publish for every change, hashes recorded.

❌ Mistake 4: No `blocked` state.
✅ Correct: Plan for revocation; resolvers must honour status on every start.

---

## 🧠 Tricky Interview Question
"Your agents resolve `latest` from the registry on every start. A publisher pushes a malicious 1.11.0. What happened and how do you design against it?"

Answer: "Latest" auto-upgrades turned a registry compromise into instant production compromise. Design: require human/security approval before status becomes `approved` (resolve only approved), pin ranges (`^1.2`) or exact versions plus hashes in agent config, run new versions in canary, compare tool schemas with the previous version and alert on description changes (tool poisoning), sandbox servers, and keep a revoke path (`blocked`) that resolvers honour.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is an MCP registry for?
A1: Discovering and resolving MCP servers with metadata (name, version, how to run, owner).

Q2: [Medium] Public vs private registry?
A2: Public: ecosystem-wide discovery, unvetted. Private: approved servers, ownership, policy, integrity checks.

Q3: [Hard] Why store the expected tool list in the registry?
A3: It is the server's contract; clients detect drift (added/removed/renamed tools or changed descriptions) before giving tools to a model.

Q4: [Hard] How do you handle a vulnerable server version?
A4: Mark `blocked`, resolvers refuse it, alerts on agents still pinned to it, and publish a fixed version.

Q5: [System Design] Registry for 200 servers and 50 teams.
A5: Postgres-backed API, SSO + role-based publishing, review workflow, immutable versions with hashes, status lifecycle, search index, audit log, webhook to the gateway for revocation, usage metrics per server/tool.

---

## 💰 Cost Impact
The registry itself is cheap (a small service + database; no LLM tokens). It saves money indirectly: a catalogue with a vetted, minimal tool set per use case avoids loading huge tool lists into every prompt, and revocation limits the cost of misbehaving servers. No numbers claimed.

---

## 🔷 When to Use
✅ Use when:
- Many teams/servers, compliance needs, or agents resolving servers dynamically

❌ Avoid when:
- One team, two servers, config in git is enough

---

## 📊 Visual Diagram
```
 Publisher --POST /servers--> [Registry: immutable versions, status, sha256, tools]
 Platform  --review--> status = approved | deprecated | blocked
 Agent     --GET /servers/acme/tariff/latest--> entry
     |-- verify sha256 --> launch/connect --> list_tools == entry.tools ? run : refuse
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Catalogue of MCP servers | MCP servers की सूची |
| Resolve | Turn a name into a launch config | नाम को launch config में बदलना |
| Immutable version | Cannot be edited after publish | publish के बाद बदला नहीं जा सकता |
| Contract | Expected tools/schemas | अपेक्षित tools/schemas |
| Revocation | Blocking a bad version | खराब version को रोकना |

---

## ⚡ 3-Line Summary
English: A registry lets you discover and resolve MCP servers with owners, versions and status. Use immutable versions, hashes and contract checks. A listing is not a security review.
Hindi: Registry से आप owners, versions और status के साथ MCP servers खोज और resolve करते हैं। Immutable versions, hashes और contract checks इस्तेमाल करें। सूची में होना security review नहीं है।

---

## ➡️ Next Topic
**027. MCP in Production** - scaling, observability, deployment and operating servers for real traffic.

---
