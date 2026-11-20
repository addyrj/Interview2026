---

# 24. Official MCP Servers (filesystem, github, postgres, slack, google drive etc.)
# हिंदी में: आधिकारिक MCP Servers (filesystem, github, postgres, slack, google drive आदि)
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0, `langchain-mcp-adapters` 0.3.2, `openai-agents` 0.24.0. What ran: the launch-config builder below (constructing `MultiServerMCPClient` and `MCPServerStdio` objects without starting any server). **NOT run - needs `npx`/`uvx` plus network downloads (my attempt to run the filesystem server through `npx` was blocked in this environment): every claim about the official servers' tool names, flags, package names and which servers are maintained/archived comes from my background knowledge and must be verified against the `modelcontextprotocol/servers` README and each server's own docs before use.** The server list changes - several servers I recall (github, postgres, slack, gdrive, sqlite, puppeteer, brave-search) were, as far as I know, moved to an "archived" repo and replaced by vendor-maintained servers (e.g. GitHub's own `github-mcp-server`). Treat names below as "check this".

---

## 🔵 Simple Definition (2-3 lines)
"Official" MCP servers are ready-made servers: the **reference servers** maintained in the `modelcontextprotocol/servers` repo (as I recall: filesystem, git, fetch, memory, time, sequential-thinking, everything - verify), and **vendor servers** published by the product owners (GitHub, Slack, Google, database vendors...). You launch them as a subprocess (stdio) or connect to a hosted URL, and their tools appear to your agent like any other.

## 🔵 सरल परिभाषा (Hindi)
"Official" MCP servers तैयार-बने servers हैं: `modelcontextprotocol/servers` repo में रखे **reference servers** (जहाँ तक मुझे याद है: filesystem, git, fetch, memory, time, sequential-thinking, everything - verify करें), और product के मालिकों के **vendor servers** (GitHub, Slack, Google, database vendors...)। इन्हें subprocess (stdio) की तरह चलाएँ या hosted URL से जुड़ें, और इनके tools आपके agent को सामान्य tools जैसे दिखते हैं।

---

## 🔴 Problem it Solves
Writing your own GitHub, filesystem or database integration for every agent framework is repeated work. Ready-made servers give the common integrations instantly. The risk shifts: they run with your credentials, so you must choose, pin and restrict them.

## 🔴 यह क्यों बना? (Hindi)
हर agent framework के लिए अपना GitHub, filesystem या database integration लिखना बार-बार का काम है। तैयार servers आम integrations तुरंत देते हैं। जोखिम बदल जाता है: वे आपके credentials से चलते हैं, इसलिए आपको उन्हें चुनना, pin करना और सीमित करना होगा।

---

## 🟢 How it Works

```
Step 1 -> Pick a server (reference repo or vendor) and READ its README + tool list
Step 2 -> Pin the version (npx -y pkg@x.y.z / uvx pkg==x.y.z) - do not float on "latest"
Step 3 -> Launch config: {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "<allowed dir>"]}
Step 4 -> Restrict: allowed directories / read-only DB user / minimal token scopes
Step 5 -> Host/agent connects over stdio, calls tools/list, applies tool allow-list
Step 6 -> Use; log calls; review updates before bumping versions
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Server चुनें (reference repo या vendor) और उसका README + tool list पढ़ें
Step 2 -> Version pin करें (npx -y pkg@x.y.z / uvx pkg==x.y.z) - "latest" पर न टिकें
Step 3 -> Launch config: {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "<allowed dir>"]}
Step 4 -> सीमित करें: allowed directories / read-only DB user / न्यूनतम token scopes
Step 5 -> Host/agent stdio से जुड़ता है, tools/list चलाता है, tool allow-list लगाता है
Step 6 -> इस्तेमाल करें; calls log करें; version बढ़ाने से पहले updates review करें
```

---

## 🟡 Real World Example
**Tariff Agent** assistant for the customs team: filesystem server limited to `./tariff_docs` (PDF/CSV rate sheets), fetch server to read public customs notices, and a read-only Postgres server (a vendor/community server or your own) for the rates database. Writes (GitHub issues, Slack posts) stay behind human approval.

## 🟡 Real Example Hindi mein
**Tariff Agent** customs team के assistant के रूप में: filesystem server सिर्फ़ `./tariff_docs` (PDF/CSV rate sheets) तक सीमित, fetch server सार्वजनिक customs notices पढ़ने के लिए, और rates database के लिए read-only Postgres server (vendor/community या आपका अपना)। Writes (GitHub issues, Slack posts) human approval के पीछे रहते हैं।

---

## 💻 Code Example — Basic
```python
# list_official_tools.py - connect to a reference server and list its tools (NOT run - needs npx + network)
import asyncio, os                                          # stdlib
from mcp import ClientSession, StdioServerParameters        # MCP client
from mcp.client.stdio import stdio_client                   # stdio transport

async def main() -> None:
    allowed = os.path.abspath("./tariff_docs")              # folder the server may touch
    os.makedirs(allowed, exist_ok=True)                     # make sure it exists
    params = StdioServerParameters(                         # how to launch the server subprocess
        command="npx",                                      # Node package runner (needs Node installed)
        args=["-y", "@modelcontextprotocol/server-filesystem", allowed])   # package name: verify; pin a version in real use
    async with stdio_client(params) as (read, write):       # spawn + connect
        async with ClientSession(read, write) as session:   # protocol session
            init = await session.initialize()               # handshake
            print(init.serverInfo.name, init.serverInfo.version)
            for tool in (await session.list_tools()).tools: # discover what it offers
                print(tool.name, "-", (tool.description or "")[:60])

asyncio.run(main())                                         # run (needs network the first time)
```
The code is syntax/import-checked only. The SDK parts (`stdio_client`, `ClientSession`, `list_tools`) were verified against our own stdio server in other notes; the package name and its tool names are NOT verified here.

## 💻 Code Example — Advanced
```python
# official_servers.py - one config reused by Claude Desktop-style JSON, LangChain and OpenAI Agents SDK
# (ran: objects were constructed; servers were NOT launched)
import json, os                                             # stdlib
from typing import Any                                      # hints
from agents.mcp import MCPServerStdio, create_static_tool_filter   # OpenAI Agents SDK
from langchain_mcp_adapters.client import MultiServerMCPClient     # LangChain adapter

DOCS_DIR: str = os.path.abspath("./tariff_docs")            # the ONLY folder the filesystem server may touch

SERVERS: dict[str, dict[str, Any]] = {                      # name -> launch config (same shape host config files use)
    "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", DOCS_DIR]},
    "git": {"command": "uvx", "args": ["mcp-server-git", "--repository", os.path.abspath(".")]},
    "fetch": {"command": "uvx", "args": ["mcp-server-fetch"]},
}   # package names/flags above are from memory - verify each against its README before use

def desktop_config() -> str:                                # JSON you would paste into a host config file
    return json.dumps({"mcpServers": SERVERS}, indent=2)

def langchain_client() -> MultiServerMCPClient:             # same servers for LangChain/LangGraph
    conns = {n: {**cfg, "transport": "stdio"} for n, cfg in SERVERS.items()}
    return MultiServerMCPClient(conns, tool_name_prefix=True)   # prefix avoids name clashes (e.g. several "read_file")

def openai_server(name: str, read_only_tools: list[str]) -> MCPServerStdio:   # one server for the Agents SDK
    cfg = SERVERS[name]
    return MCPServerStdio(params={"command": cfg["command"], "args": cfg["args"]},
                          cache_tools_list=True,            # avoid tools/list every run
                          tool_filter=create_static_tool_filter(allowed_tool_names=read_only_tools))   # allow-list

if __name__ == "__main__":
    print(desktop_config()[:80].replace("\n", " "))
    print(type(langchain_client()).__name__, type(openai_server("filesystem", ["read_text_file"])).__name__)
    # observed: MultiServerMCPClient MCPServerStdio   (no processes were started)
```
Production hardening (design advice): pin versions, run in a container with no extra mounts, pass only the env vars the server needs (not your whole environment), prefer read-only credentials, and add the client-side guards from note 021. Token usage: official servers can expose many tools (the filesystem server alone has a dozen or so, I recall) - allow-list to keep schemas small. Error handling: wrap `async with stdio_client(...)` in try/except; a missing `npx` raises a `FileNotFoundError`-style error at spawn. Async: all asyncio.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Launch stdio server from config | `MultiServerMCPClient({... "transport": "stdio"})` (constructed) | verify docs | `MCPServerStdio(params=...)` (constructed) | verify |
| Many servers at once | yes, dict of servers | verify | list in `mcp_servers=[...]` | verify |
| Tool allow-list | filter after `get_tools()` | verify | `create_static_tool_filter` (verified) | verify |
| Hosted/remote official servers | `streamable_http` connection | verify | `MCPServerStreamableHttp` / `HostedMCPTool` | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Pointing the filesystem server at `/` or your home directory.
✅ Correct: Give it one narrow folder.

❌ Mistake 2: `npx -y some-package` without a version.
✅ Correct: Pin a version and review changes before upgrading.

❌ Mistake 3: Using a personal admin token for GitHub/Slack servers.
✅ Correct: Fine-grained, least-scope tokens; separate bot accounts.

❌ Mistake 4: Assuming "official" means "audited for your threat model".
✅ Correct: Read the code/tool list; treat all server output as untrusted.

---

## 🧠 Tricky Interview Question
"Your team's agent used the `postgres` MCP server from a tutorial and it stopped working after an update. What do you do and what is the lesson?"

Answer: Check the server's repo/README: it may have moved, been archived or renamed (I recall several early reference servers were archived - verify). Lesson: the ecosystem moves fast, so pin versions, vendor or fork critical servers, own a thin internal wrapper (your own FastMCP server with just the queries you need and a read-only role), and keep contract tests on the tool schemas. Building a narrow custom server is often safer than a generic "run any SQL" server.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How is an official stdio server started?
A1: The host spawns it as a subprocess from a `command` + `args` config (e.g. `npx` or `uvx`) and talks JSON-RPC over stdin/stdout.

Q2: [Medium] Reference vs vendor servers?
A2: Reference servers are examples/maintained in the MCP org's repo; vendor servers are published and supported by the product owner (usually with remote/OAuth options). Check maintenance status.

Q3: [Hard] How do you limit what the filesystem server can do?
A3: Pass only allowed directories as args, run in a container with only that mount, use a client allow-list for read-only tools, and log all calls.

Q4: [Hard] 10 agents each spawn their own filesystem server. Problem?
A4: Process sprawl and inconsistent config. Run a shared HTTP server or a gateway, or standardise a launcher with pinned versions.

Q5: [System Design] Curated internal catalogue of servers.
A5: Security review, version pinning, mirrored packages, sandboxed runtime, per-team allow-lists, usage metrics, deprecation process - exposed through an internal registry (see note 026).

---

## 💰 Cost Impact
Server processes cost little compute (a Node/Python subprocess, memory depends on server - measure). The model cost comes from tool schemas and returned content: reading whole files or web pages into context can be thousands of tokens per call. Tips: allow-list tools, truncate/summarise outputs, chunk large files, cache fetches.

---

## 🔷 When to Use
✅ Use when:
- Prototyping, common integrations (files, git, web fetch)
- A vendor maintains the server you need

❌ Avoid when:
- You need strict control or a narrow API (write a custom server, note 025)
- The server is unmaintained or unreviewed for sensitive data

---

## 📊 Visual Diagram
```
 Agent/Host --stdio--> npx @modelcontextprotocol/server-filesystem ./tariff_docs
            --stdio--> uvx mcp-server-fetch
            --HTTPS--> vendor remote server (OAuth)
 [client allow-list + approvals] sits between the model and every server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reference server | Example server in the MCP org repo | MCP org के repo का उदाहरण server |
| Vendor server | Server published by the product owner | product मालिक का server |
| npx / uvx | Run Node/Python packages on demand | packages को माँग पर चलाना |
| Version pinning | Fix an exact version | सटीक version तय करना |
| Allow-list | Only listed items permitted | सिर्फ़ सूचीबद्ध की अनुमति |

---

## ⚡ 3-Line Summary
English: Official servers give instant integrations over stdio or HTTP. Verify what is currently maintained, pin versions and restrict scope. Allow-list tools and treat outputs as untrusted.
Hindi: Official servers stdio या HTTP पर तुरंत integrations देते हैं। जाँचें कि अभी क्या maintained है, versions pin करें और scope सीमित रखें। Tools allow-list करें और outputs को untrusted मानें।

---

## ➡️ Next Topic
**025. Building Custom MCP Server** - when the generic ones are not enough: a typed, narrow Tariff server with context, progress and structured output.

---
