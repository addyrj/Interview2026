---

# 14. MCP with Claude Desktop
# हिंदी में: Claude Desktop के साथ MCP
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0, `fastapi` 0.163.0, Python 3.13. NOT run: Claude Desktop itself (it is a GUI app, not available here). The config file shape, file locations and log paths below come from Anthropic's published guidance as recalled at the time of writing, so **verify them in the current Claude Desktop docs** before relying on them. What WAS run: a script that reads a `claude_desktop_config.json`-style file and launches each server the same way a stdio host does, which reproduces the most common failures.

---

## 🔵 Simple Definition (2-3 lines)
Claude Desktop is an MCP **host**. You register local servers in a JSON config file under the key `mcpServers`, each with a `command`, `args` and optional `env`. On start, Desktop spawns each command as a stdio server, lists its tools and lets Claude call them, asking you for approval. Remote HTTP servers are generally added through Desktop's connector/settings UI rather than this file (verify for your version).

## 🔵 सरल परिभाषा (Hindi)
Claude Desktop एक MCP **host** है। आप local servers को JSON config file में `mcpServers` key के नीचे register करते हैं, हर एक के लिए `command`, `args` और optional `env`। Start होने पर Desktop हर command को stdio server की तरह चलाता है, उसके tools list करता है और Claude को call करने देता है, हर बार आपसे approval माँगकर। Remote HTTP servers आम तौर पर config file की जगह Desktop के connector/settings UI से जुड़ते हैं (अपने version में जाँचें)।

---

## 🔴 Problem it Solves
Without a host like Desktop you must build your own chat UI, tool loop and approval flow just to try your server. Desktop gives analysts a ready UI: add one config entry and the tariff tools appear in the chat, with per-call permission prompts. It is also the fastest way to demo a server in an interview and to dogfood it with non-developers.

## 🔴 यह क्यों बना? (Hindi)
Desktop जैसे host के बिना अपना server आज़माने के लिए खुद chat UI, tool loop और approval flow बनाना पड़ता है। Desktop analysts को तैयार UI देता है: config में एक entry जोड़ें और tariff tools chat में आ जाते हैं, हर call पर permission prompt के साथ। Interview में server demo करने और non-developers के साथ आज़माने का यह सबसे तेज़ तरीका है।

---

## 🟢 How it Works

```
Step 1 -> open the config (Desktop: Settings -> Developer -> Edit Config; verify menu names)
          macOS : ~/Library/Application Support/Claude/claude_desktop_config.json
          Windows: %APPDATA%\Claude\claude_desktop_config.json     (verify for your version)
Step 2 -> add under "mcpServers": { "tariff": { "command": "<ABS python>", "args": ["<ABS script>"], "env": {...} } }
Step 3 -> fully QUIT and restart Claude Desktop (config is read at start)
Step 4 -> Desktop spawns the command (stdio), runs initialize + tools/list
Step 5 -> tools appear in the chat UI; Claude asks to call them; you click Allow
Step 6 -> result returns to Claude's context; answer is produced
Step 7 -> problems? read the MCP log files (macOS: ~/Library/Logs/Claude/mcp*.log; verify) and run the SAME command by hand
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> config खोलें (Desktop: Settings -> Developer -> Edit Config; menu नाम जाँचें)
          macOS : ~/Library/Application Support/Claude/claude_desktop_config.json
          Windows: %APPDATA%\Claude\claude_desktop_config.json     (अपने version में जाँचें)
Step 2 -> "mcpServers" में जोड़ें: { "tariff": { "command": "<ABS python>", "args": ["<ABS script>"], "env": {...} } }
Step 3 -> Claude Desktop को पूरी तरह QUIT करके दोबारा खोलें (config start पर पढ़ी जाती है)
Step 4 -> Desktop command spawn करता है (stdio), initialize + tools/list चलाता है
Step 5 -> tools chat UI में दिखते हैं; Claude call माँगता है; आप Allow दबाते हैं
Step 6 -> result Claude के context में जाता है; जवाब बनता है
Step 7 -> दिक्कत? MCP log files (macOS: ~/Library/Logs/Claude/mcp*.log; जाँचें) पढ़ें और वही command हाथ से चलाएँ
```

---

## 🟡 Real World Example
**Tariff Agent**: a customs analyst adds the `tariff` entry (absolute path to the Python in the project venv and to `tariff_server.py`) and restarts Desktop. Asking "What is the duty and landed cost for a 100 USD shipment of 6109 garments?" makes Claude call `get_duty_rate` and `landed_cost`; each call shows an approval prompt. When it fails with "server disconnected", the analyst runs the exact config command in a terminal and sees the traceback.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs analyst `tariff` entry जोड़ता है (project venv के Python और `tariff_server.py` के absolute paths) और Desktop restart करता है। "100 USD की 6109 garments shipment पर duty और landed cost क्या है?" पूछने पर Claude `get_duty_rate` और `landed_cost` call करता है; हर call पर approval prompt आता है। "server disconnected" आए तो analyst config का वही command terminal में चलाकर traceback देखता है।

---

## 💻 Code Example — Basic
```json
{
  "mcpServers": {
    "tariff": {
      "command": "/ABSOLUTE/PATH/TO/venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/tariff_server.py"],
      "env": { "TARIFF_ENV": "dev" }
    }
  }
}
```
Shape: server name -> `command`, `args`, `env`. Use **absolute** paths: a desktop app does not load your shell profile or start in your project directory. (Not run in Claude Desktop. The same command/args/env triple was run by a Python stdio client in the next example and listed `['get_duty_rate', 'landed_cost']`.) The server file is the one from topic 010; no `print()` to stdout.

## 💻 Code Example — Advanced
```python
# check_config.py - dry-run a claude_desktop_config.json: static checks + real stdio launch (ran)
import asyncio                                              # runtime + timeout
import json                                                 # parse the config
import shutil                                               # find commands on PATH
import sys                                                  # CLI args
from pathlib import Path                                    # file checks
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # stdio transport

async def check(name: str, spec: dict) -> str:             # validate ONE server entry
    command: str = spec.get("command", "")                  # executable
    problems: list[str] = []                                # collected static problems
    if not (Path(command).is_file() or shutil.which(command)):   # must exist as a file or on PATH
        problems.append(f"command not found: {command}")    # typical: bare "python" not on Desktop's PATH
    for arg in spec.get("args", []):                        # inspect arguments
        if arg.endswith(".py") and not Path(arg).is_absolute():   # relative script path
            problems.append(f"relative script path (hosts start in an unknown cwd): {arg}")   # classic bug
    if problems:                                            # fail fast, no launch
        return f"{name}: FAIL static check -> " + "; ".join(problems)
    params = StdioServerParameters(command=command, args=spec.get("args", []), env=spec.get("env"))   # same triple Desktop uses
    try:                                                    # real launch like a host
        async with asyncio.timeout(15):                     # a hung server must not hang the checker
            async with stdio_client(params) as (read, write):   # spawn
                async with ClientSession(read, write) as session:   # protocol
                    await session.initialize()              # handshake (fails if stdout is polluted)
                    tools = [t.name for t in (await session.list_tools()).tools]   # discovery
    except Exception as exc:                                # import error, crash, timeout, bad JSON-RPC
        return f"{name}: FAIL launch -> {type(exc).__name__}: {exc}"   # message to fix
    return f"{name}: OK tools={tools}"                      # healthy

async def main(path: str) -> None:                          # check every entry
    cfg = json.loads(Path(path).read_text())                # raises on invalid JSON (also a classic failure)
    servers: dict[str, dict] = cfg["mcpServers"]            # same key Desktop reads
    for name, spec in servers.items():                      # sequential for readable output
        print(await check(name, spec))                      # report

if __name__ == "__main__":                                  # CLI entry
    asyncio.run(main(sys.argv[1]))                          # python check_config.py claude_desktop_config.json
```
Ran against a config with three entries. Output: `tariff: OK tools=['get_duty_rate', 'landed_cost']`; `broken-relative: FAIL static check -> command not found: python; relative script path ...` (bare `python` was not on PATH in this environment, a real example of the problem); `missing-binary: FAIL static check -> command not found: /no/such/python; ...`.

FastAPI wrapper (ran with `TestClient`) so a team portal can validate entries before analysts paste them:
```python
# validate_api.py - POST a server spec, get a verdict
from fastapi import FastAPI                                 # web layer
from pydantic import BaseModel                              # typed body
from check_config import check                              # reuse the checker

app = FastAPI()                                             # app

class ServerSpec(BaseModel):                                # same keys as the config entry
    command: str                                            # executable
    args: list[str] = []                                    # arguments
    env: dict[str, str] | None = None                       # optional env

@app.post("/validate/{name}")                               # one endpoint
async def validate(name: str, spec: ServerSpec) -> dict[str, str]:   # async + typed
    return {"result": await check(name, spec.model_dump())} # reuse the same logic
```
Ran: a valid spec returned `OK tools=[...]`; a spec with `python`/`x.py` returned the static-check failure. Token usage: every tool Desktop exposes is part of Claude's context each turn, so connect only the servers you need (many servers means many tools means higher cost and worse tool choice). Not run: the real Desktop UI, approvals, and Desktop's own log files.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Claude Desktop is a host | Not related: Desktop is a separate host app | Not related | Not related | Not related |
| Same server usable in both Desktop and the framework | Yes, via MCP adapter (verify) | Yes (verify) | Yes, `MCPServerStdio` (import verified earlier) | Yes (verify) |
| Config style | Python code | Python/YAML | Python code | Python code |
| Approval UX | You build it (`interrupt`) | You build it | Approval options (verify) | You build it |

The point: write the server once; Desktop and your agent framework are just two different hosts for it.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Relative paths or bare `python`/`node` in `command`/`args`.
✅ Correct: Absolute paths to the interpreter and script (Desktop does not use your shell PATH or cwd).

❌ Mistake 2: Editing the config but not fully quitting Desktop.
✅ Correct: Quit the app completely and reopen; changes are read at startup.

❌ Mistake 3: `print()` or banners on stdout in the server.
✅ Correct: Log to stderr only; stdout pollution breaks the handshake (looks like "server disconnected").

❌ Mistake 4: Invalid JSON (trailing comma, comments) in the config.
✅ Correct: Validate the JSON (the script above does) before restarting.

❌ Mistake 5: Putting secrets in the config file and sharing it.
✅ Correct: Use env entries from a secret store or OS keychain and keep the file out of git; give servers least-privilege access (file roots, read-only DB users).

---

## 🧠 Tricky Interview Question
"Your server works when you run it in the terminal but Claude Desktop shows it as failed. Walk me through debugging."

Answer: Reproduce the host's launch: run the exact `command` and `args` from the config in a clean shell (`env -i` style) with no cwd assumptions. Check (1) bare command names not on the app's PATH (use absolute paths; our checker flagged `python` as not found), (2) relative script paths, (3) a different interpreter than your venv, so imports fail, (4) stdout noise breaking JSON-RPC, (5) missing env vars (put them in `env`), (6) invalid JSON in the config. Then read the host's MCP log files, and finally test with a standalone client (like `check_config.py`) before blaming Desktop.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Where do you register a server for Claude Desktop?
A1: In the `mcpServers` object of `claude_desktop_config.json` (macOS: under `~/Library/Application Support/Claude/`; verify the current path), with `command`, `args`, `env`.

Q2: [Medium] Why must paths be absolute?
A2: The desktop app starts the process without your shell profile or project cwd, so relative paths and PATH-dependent commands often fail.

Q3: [Hard] Is Desktop the host or the client?
A3: The **host**. It creates one MCP **client** per configured server, owns the LLM, and applies the user approval policy.

Q4: [Hard] What security risks come from adding a community server?
A4: It runs code on your machine with your permissions, may read files/env/network, and its tool descriptions can try to steer the model (tool poisoning). Pin versions, read the source, run with least privilege or in a container, and review each approval prompt.

Q5: [System Design] Roll out MCP tools to 200 analysts using Claude Desktop.
A5: Package the server as a signed installer or a Desktop extension (verify current extension format), distribute config via MDM, prefer remote authenticated servers where possible, central logging, version pinning, an allow-list of servers, and a validator like `check_config.py` in CI.

---

## 💰 Cost Impact
Desktop usage is billed under your Claude plan/API terms (check current pricing; no numbers claimed here). What you control: every connected server's tools are added to Claude's context, so unused servers cost tokens and degrade tool selection. Tips: enable only needed servers per task, keep tool descriptions short, and return compact results.

---

## 🔷 When to Use
✅ Use when:
- Demoing or dogfooding a server quickly
- Non-developers need a chat UI over your tools

❌ Avoid when:
- You need server-side orchestration, multi-user control, or automation (use your own host: topic 013)
- The server needs secrets you cannot protect on user laptops

---

## 📊 Visual Diagram
```
 claude_desktop_config.json
   mcpServers.tariff = {command, args, env}
            |
            v   (read at app start)
 +---------------- Claude Desktop (HOST) ----------------+
 |  spawn command --stdio--> [tariff_server.py]          |
 |  initialize / tools/list  <------------------------   |
 |  Claude asks to call get_duty_rate -> [Allow?] click  |
 |  result -> Claude context -> answer                   |
 +--------------------------------------------------------+
   logs: host MCP log files   |   server logs: stderr
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mcpServers | Config key listing servers | servers की सूची वाली config key |
| command / args / env | How to launch a stdio server | server शुरू करने का तरीका |
| Host | App that runs the LLM and clients | LLM चलाने वाला app |
| Approval prompt | User permission before a tool call | tool call से पहले user की अनुमति |
| Tool poisoning | Malicious tool text steering the model | खराब tool text से model को भटकाना |

---

## ⚡ 3-Line Summary
English: Add a `command`/`args`/`env` entry under `mcpServers`, use absolute paths, and restart Desktop fully. Debug by running the same command by hand and checking stdout cleanliness and logs. Desktop is just one host; the server is portable.
Hindi: `mcpServers` में `command`/`args`/`env` entry जोड़ें, absolute paths इस्तेमाल करें और Desktop को पूरी तरह restart करें। वही command हाथ से चलाकर, stdout की सफ़ाई और logs देखकर debug करें। Desktop सिर्फ़ एक host है; server portable है।

---

## ➡️ Next Topic
**015. MCP with Claude API** - the same servers, but called from your own code through the Claude API instead of a desktop app.

---
