---

# 23. MCP Versioning
# हिंदी में: MCP Versioning (संस्करण प्रबंधन)
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0 (supports protocol versions 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25; latest 2025-11-25). Ran locally: raw `initialize` requests asking for old and invalid protocol versions against a Streamable HTTP server, a client reading `serverInfo`, and feature detection between a v1 and v2 tool. Spec details beyond what the SDK reports (e.g. exact negotiation wording, header requirements) were not read from the spec text here - verify on modelcontextprotocol.io. Real LLM runs: not run.

---

## 🔵 Simple Definition (2-3 lines)
MCP has **three kinds of version**: (1) the **protocol version**, a date string like `2025-11-25`, negotiated in `initialize`; (2) the **server/app version** in `serverInfo.version`; (3) your **tool contract version** (names and JSON schemas), which you manage yourself. Compatibility problems usually come from (3).

## 🔵 सरल परिभाषा (Hindi)
MCP में **तीन तरह के version** हैं: (1) **protocol version**, तारीख वाला string जैसे `2025-11-25`, जो `initialize` में तय होता है; (2) **server/app version**, `serverInfo.version` में; (3) आपका **tool contract version** (नाम और JSON schemas), जिसे आप खुद संभालते हैं। अनुकूलता की समस्याएँ ज़्यादातर (3) से आती हैं।

---

## 🔴 Problem it Solves
The tariff team renames `hs_code` to `hs_code_10` and 40 agents start failing with validation errors. Or a new client speaks a protocol the old server does not know. Versioning rules let both sides agree on what they speak and let you evolve tools without breaking callers.

## 🔴 यह क्यों बना? (Hindi)
Tariff team `hs_code` का नाम `hs_code_10` कर देती है और 40 agents validation errors से fail होने लगते हैं। या नया client ऐसा protocol बोलता है जो पुराना server नहीं जानता। Versioning के नियम दोनों पक्षों को तय करने देते हैं कि वे क्या बोलेंगे और tools को callers तोड़े बिना बदलने देते हैं।

---

## 🟢 How it Works

```
Observed negotiation (server supports 4 versions, latest 2025-11-25):
client asks 2024-11-05 -> server answers protocolVersion 2024-11-05
client asks 2025-03-26 -> server answers protocolVersion 2025-03-26
client asks 1999-01-01 -> server answers its latest, 2025-11-25 (client must then decide: continue or disconnect)

Step 1 -> client sends initialize{protocolVersion: its preferred (usually latest)}
Step 2 -> server replies with a version it supports (same if possible, else its latest)
Step 3 -> client checks the reply; if unsupported -> disconnect
Step 4 -> client reads serverInfo {name, version} and capabilities
Step 5 -> client feature-detects tools (list_tools) instead of assuming
Step 6 -> breaking tool change? ship a NEW tool name (get_tariff_rate_v2), deprecate the old one
```

## 🟢 कैसे काम करता है? (Hindi)

```
देखी गई negotiation (server 4 versions जानता है, latest 2025-11-25):
client 2024-11-05 माँगे -> server protocolVersion 2024-11-05 लौटाता है
client 2025-03-26 माँगे -> server protocolVersion 2025-03-26 लौटाता है
client 1999-01-01 माँगे -> server अपना latest 2025-11-25 लौटाता है (client तय करे: जारी रखे या disconnect)

Step 1 -> client initialize{protocolVersion: पसंदीदा (आमतौर पर latest)} भेजता है
Step 2 -> server ऐसा version लौटाता है जो वह जानता है (हो सके तो वही, वरना अपना latest)
Step 3 -> client जवाब जाँचता है; unsupported हो तो disconnect
Step 4 -> client serverInfo {name, version} और capabilities पढ़ता है
Step 5 -> client मानकर नहीं चलता, list_tools से feature-detect करता है
Step 6 -> breaking tool change? नया tool नाम (get_tariff_rate_v2) जारी करें, पुराने को deprecate करें
```

---

## 🟡 Real World Example
**Tariff Agent**: `get_tariff_rate(hs_code)` stays for old agents while `get_tariff_rate_v2(hs_code, country)` returns a structured result. New agents feature-detect v2; old ones keep working until the team removes v1 after all clients migrate (tracked by per-tool call metrics).

## 🟡 Real Example Hindi mein
**Tariff Agent**: `get_tariff_rate(hs_code)` पुराने agents के लिए बना रहता है जबकि `get_tariff_rate_v2(hs_code, country)` structured result देता है। नए agents v2 को feature-detect करते हैं; पुराने तब तक चलते रहते हैं जब तक सब clients migrate न हो जाएँ और team v1 हटा दे (प्रति-tool call metrics से ट्रैक)।

---

## 💻 Code Example — Basic
```python
# basic_version.py - read the negotiated protocol version and serverInfo (ran against tariff_server.py)
import asyncio, sys                                         # stdlib
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # transport
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS  # versions this SDK build can speak
import mcp.types as types                                   # types.LATEST_PROTOCOL_VERSION

async def main() -> None:
    print(SUPPORTED_PROTOCOL_VERSIONS, types.LATEST_PROTOCOL_VERSION)   # 4 versions, latest 2025-11-25
    params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()                     # negotiation happens here
            print(init.protocolVersion, init.serverInfo)    # 2025-11-25 name='tariff' version='1.30.0' ...
asyncio.run(main())
```
Note: `serverInfo.version` printed `1.30.0` - that is the **SDK package version**, not your app version, because FastMCP did not set one. To report your own app version, use the low-level `Server(name, version="2.3.0")` (the `version` parameter exists in its signature) or expose a `get_server_info` tool.

## 💻 Code Example — Advanced
```python
# version_check.py - negotiation probes + compatibility gate + feature detection (ran)
import asyncio, httpx, uvicorn                              # runner + raw HTTP client
from mcp import ClientSession                               # client
from mcp.client.streamable_http import streamablehttp_client   # HTTP transport
from mcp.server.fastmcp import FastMCP                      # server
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS  # versions this SDK build speaks
import mcp.types as types                                   # LATEST_PROTOCOL_VERSION

mcp = FastMCP("tariff", port=8781)                          # demo server
@mcp.tool()
def get_tariff_rate(hs_code: str) -> str:                   # v1 tool (keep working)
    """Return duty percent for an HS code (v1)."""
    return "20%"
@mcp.tool()
def get_tariff_rate_v2(hs_code: str, country: str = "US") -> dict:   # additive change -> new name
    """Return {rate, country} (v2)."""
    return {"rate": 20.0, "country": country}

MIN_SERVER = (1, 0)                                         # our client needs server >= 1.0

async def main() -> None:
    print("sdk supports:", SUPPORTED_PROTOCOL_VERSIONS, "latest:", types.LATEST_PROTOCOL_VERSION)
    srv = uvicorn.Server(uvicorn.Config(mcp.streamable_http_app(), port=8781, log_level="error"))
    t = asyncio.create_task(srv.serve())                    # start the server in-process
    while not srv.started:
        await asyncio.sleep(0.05)
    hdr = {"Accept": "application/json, text/event-stream"} # required by Streamable HTTP
    async with httpx.AsyncClient() as h:
        for ver in ["2024-11-05", "2025-03-26", "1999-01-01"]:        # probe negotiation
            body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": ver, "capabilities": {}, "clientInfo": {"name": "c", "version": "1"}}}
            r = await h.post("http://localhost:8781/mcp", json=body, headers=hdr)
            data = r.text.split("data: ")[-1] if "data: " in r.text else r.text
            print("asked", ver, "->", r.status_code, data[:120].replace("\n", " "))
    async with streamablehttp_client("http://localhost:8781/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            print("negotiated:", init.protocolVersion, "server:", init.serverInfo.name, init.serverInfo.version)
            if init.protocolVersion not in SUPPORTED_PROTOCOL_VERSIONS:   # gate: refuse unknown protocol
                raise RuntimeError("unsupported protocol version")
            major_minor = tuple(int(x) for x in init.serverInfo.version.split(".")[:2])
            print("server version OK:", major_minor >= MIN_SERVER)
            names = {x.name for x in (await s.list_tools()).tools}
            use = "get_tariff_rate_v2" if "get_tariff_rate_v2" in names else "get_tariff_rate"   # feature detect
            print("using", use, (await s.call_tool(use, {"hs_code": "6109.10"})).content[0].text)
    srv.should_exit = True
    await t

asyncio.run(main())
```
Observed output: asking `2024-11-05` and `2025-03-26` returned the same versions; asking `1999-01-01` returned `2025-11-25`; negotiated `2025-11-25`, `server version OK: True`, using `get_tariff_rate_v2` with `{"rate": 20.0, "country": "US"}`. Token usage: versioning has no direct token effect; adding `_v2` while keeping v1 exposes **both** tools to the model (more tokens) - hide the deprecated one from new agents with a tool filter. Error handling: raise on unsupported protocol; fall back to v1 when v2 is missing. Async: all awaited.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Protocol negotiation | done by `mcp` SDK underneath (verified: adapter uses `ClientSession`) | verify docs | done by `mcp` SDK underneath (verified: uses `ClientSession`) | verify |
| Pin tool versions | filter / name prefix by version | verify | `tool_filter` allow-list by exact name (verified) | verify |
| Detect server version | via `session` access (`load_mcp_tools(session)`) | verify | not directly exposed in the high-level API (check docs) | verify |
| Schema drift handling | re-load tools | verify | `invalidate_tools_cache()` (verified name) | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Renaming or removing an argument in place.
✅ Correct: Additive changes only (optional args with defaults); breaking change -> new tool name.

❌ Mistake 2: Assuming `serverInfo.version` is your app version.
✅ Correct: With FastMCP it showed the SDK version; set it explicitly or publish a version tool.

❌ Mistake 3: Hard-coding the protocol version in a custom client.
✅ Correct: Use the SDK's handshake and check the negotiated value.

❌ Mistake 4: Deleting v1 without usage data.
✅ Correct: Track per-tool calls and deprecation-warn in the description first.

---

## 🧠 Tricky Interview Question
"You added a required argument `country` to `get_tariff_rate`. Nothing failed in CI, but agents degraded in production. Why?"

Answer: CI tests the server, not each agent's prompts and cached tool lists. Agents with cached schemas (or fine-tuned/few-shot examples) call without `country`, hitting validation errors that the model may fail to repair, or they guess a wrong value. Making an argument required is a breaking change: add it as optional with a default, or publish `_v2`; send `list_changed`; run contract tests with the previous schema snapshot; roll out with metrics on tool error rate.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What format is the MCP protocol version?
A1: A date string, e.g. `2025-11-25`.

Q2: [Medium] What if client and server share no version?
A2: The server answers with a version it supports (we saw its latest for an invalid request); if the client does not support that reply it should disconnect.

Q3: [Hard] How do you evolve a tool safely?
A3: Additive optional fields; new tool name for breaking changes; keep old one with a deprecation note; snapshot schemas in tests; monitor error rates; remove after usage hits zero.

Q4: [Hard] Why is semantic versioning of the server not enough?
A4: Clients consume tool schemas and descriptions - changing a description can change model behaviour without any API break. Treat descriptions as part of the contract.

Q5: [System Design] 30 teams own MCP servers; agents must not break on deploys.
A5: Registry with schema snapshots, CI contract checks (diff schemas), canary deployments, per-tool usage metrics, deprecation policy with deadlines, and a gateway that can pin an old version of a server per agent.

---

## 💰 Cost Impact
No token cost from the protocol version itself. Cost of getting it wrong: broken agents mean failed runs, retries and extra model turns (each turn re-sends all tool schemas). Keeping both v1 and v2 visible roughly doubles that tool's schema tokens - filter the old one out for new agents. No specific numbers claimed.

---

## 🔷 When to Use
✅ Use explicit versioning when:
- Many agents/teams depend on shared servers
- You change schemas or descriptions often

❌ Skip heavy process when:
- One server, one agent, same repo (just change both together)

---

## 📊 Visual Diagram
```
 Client                                   Server (supports 2024-11-05 ... 2025-11-25)
   | initialize{ver=2025-11-25} ---------> |
   | <------- {ver=2025-11-25, serverInfo} |   same version -> ok
   | initialize{ver=1999-01-01} ---------> |
   | <------- {ver=2025-11-25 (latest)}    |   mismatch -> client decides / disconnects
   | list_tools -> has _v2? -> use v2 else v1   (feature detection)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Protocol version | Date-based wire version | तारीख वाला wire संस्करण |
| serverInfo | Server name and version in handshake | handshake में server का नाम/संस्करण |
| Feature detection | Check what exists before using | इस्तेमाल से पहले जाँचना कि क्या है |
| Breaking change | Change that breaks callers | callers को तोड़ने वाला बदलाव |
| Deprecation | Marking something for removal | हटाने के लिए चिह्नित करना |

---

## ⚡ 3-Line Summary
English: Protocol version is negotiated at `initialize`; server version is separate; tool schemas are your real contract. Evolve additively, use new names for breaking changes, and feature-detect. Treat descriptions as part of the contract.
Hindi: Protocol version `initialize` में तय होता है; server version अलग है; tool schemas असली contract हैं। बदलाव additive रखें, breaking बदलाव पर नया नाम दें, और feature-detect करें। Descriptions को भी contract का हिस्सा मानें।

---

## ➡️ Next Topic
**024. Official MCP Servers (filesystem, github, postgres, slack, google drive etc.)** - the ready-made servers you will actually plug in.

---
