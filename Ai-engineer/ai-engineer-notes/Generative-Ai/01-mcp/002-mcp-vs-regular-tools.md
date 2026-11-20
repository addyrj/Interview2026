---

# 2. MCP vs Regular Tools
# हिंदी में: MCP बनाम सामान्य Tools
# Framework: All (MCP + LangGraph + OpenAI SDK)
# Already Known: No

> Verified against: `mcp` 1.30.0, `langchain-core` 1.8.0, `langchain-mcp-adapters` 0.3.2, `openai-agents` 0.24.0. Tool listing/calls over stdio ran offline. Real LLM tool-selection: not run - needs an API key.

---

## 🔵 Simple Definition (2-3 lines)
A "regular tool" is a function you register inside one app (LangChain `@tool`, OpenAI `@function_tool`). It runs in the same process and only that app can use it. An MCP tool is the same idea but lives in a separate server speaking a standard protocol, so any MCP-aware app can discover and call it.

## 🔵 सरल परिभाषा (Hindi)
"Regular tool" वह function है जिसे आप एक ही app के अंदर register करते हैं (LangChain `@tool`, OpenAI `@function_tool`)। वह उसी process में चलता है और सिर्फ़ वही app उसे इस्तेमाल कर सकता है। MCP tool वही विचार है, पर वह अलग server में रहता है और standard protocol बोलता है, इसलिए कोई भी MCP-aware app उसे खोजकर call कर सकता है।

---

## 🔴 Problem it Solves
Regular tools are fast and simple, but they are locked to one codebase, one language and one framework, and they share the agent's permissions. Teams duplicate the same Tariff lookup in five agents; a bug fix must be copied five times; a tool with DB credentials runs next to untrusted LLM output. MCP separates tool ownership and trust from the agent.

## 🔴 यह क्यों बना? (Hindi)
Regular tools तेज़ और सरल हैं, लेकिन एक codebase, एक भाषा और एक framework में बंद रहते हैं और agent की ही permissions साझा करते हैं। टीमें वही Tariff lookup पाँच agents में दोहराती हैं; bug fix पाँच जगह करना पड़ता है; DB credentials वाला tool उसी जगह चलता है जहाँ untrusted LLM output है। MCP tool की ownership और trust को agent से अलग करता है।

---

## 🟢 How it Works

```
REGULAR TOOL                          MCP TOOL
Step 1 -> @tool def f()  (same repo)  Step 1 -> server exposes f over stdio/HTTP
Step 2 -> pass [f] to agent           Step 2 -> client.list_tools() discovers f
Step 3 -> LLM emits tool call         Step 3 -> LLM emits tool call
Step 4 -> framework calls f()         Step 4 -> client sends tools/call to server
Step 5 -> result string               Step 5 -> server runs f(), returns content
```

## 🟢 कैसे काम करता है? (Hindi)

```
REGULAR TOOL                          MCP TOOL
Step 1 -> @tool def f() (वही repo)    Step 1 -> server f को stdio/HTTP पर expose करता है
Step 2 -> [f] agent को दो             Step 2 -> client.list_tools() से f मिलता है
Step 3 -> LLM tool call बनाता है      Step 3 -> LLM tool call बनाता है
Step 4 -> framework f() चलाता है      Step 4 -> client server को tools/call भेजता है
Step 5 -> result string               Step 5 -> server f() चलाकर content लौटाता है
```

---

## 🟡 Real World Example
**Tariff Agent**: a prototype has `lookup_rate()` as a LangChain `@tool` inside the agent - fine for a weekend demo. Later the Research Agent (CrewAI) and the analyst's Claude Desktop also need it, and security wants the DB password out of the agent container. Move `lookup_rate` into an MCP server: three consumers, one codebase, credentials only on the server.

## 🟡 Real Example Hindi mein
**Tariff Agent**: prototype में `lookup_rate()` agent के अंदर LangChain `@tool` है - weekend demo के लिए ठीक। बाद में Research Agent (CrewAI) और analyst का Claude Desktop भी इसे चाहते हैं, और security चाहती है कि DB password agent container से बाहर रहे। `lookup_rate` को MCP server में डालिए: तीन consumers, एक codebase, credentials सिर्फ़ server पर।

---

## 💻 Code Example — Basic
```python
# compare_tools.py - same tool as regular LangChain tool, OpenAI tool, and via MCP (all ran offline)
import asyncio, sys                                    # async + current python path
from langchain_core.tools import tool                  # regular LangChain tool decorator
from agents import function_tool                       # regular OpenAI Agents SDK tool
from langchain_mcp_adapters.client import MultiServerMCPClient   # MCP -> LangChain tools

@tool                                                  # REGULAR tool #1 (LangChain)
def get_duty_rate(hs_code: str) -> float:              # typed input
    """Return duty percent."""                         # description for the LLM
    return {"8517": 0.0}.get(hs_code, 5.0)             # in-process lookup

@function_tool                                         # REGULAR tool #2 (OpenAI SDK) - duplicate code!
def get_duty_rate_oai(hs_code: str) -> float:          # same logic copy-pasted
    """Return duty percent."""                         # description again
    return {"8517": 0.0}.get(hs_code, 5.0)             # duplicated lookup

print(get_duty_rate.invoke({"hs_code": "8517"}))       # -> 0.0 (runs in-process)
print(get_duty_rate_oai.name)                          # -> get_duty_rate_oai

async def main() -> None:                              # MCP version: one server, many clients
    client = MultiServerMCPClient({                    # config of MCP servers
        "tariff": {"command": sys.executable,          # start server.py (from note 001/010)
                   "args": ["server.py"], "transport": "stdio"}})
    tools = await client.get_tools()                   # discover tools via tools/list
    print([t.name for t in tools])                     # -> ['get_duty_rate', 'classify']
    out = await tools[0].ainvoke({"hs_code": "6403"})  # call over MCP
    print(out)                                         # -> [{'type': 'text', 'text': '10.0', ...}]

asyncio.run(main())                                    # run the MCP demo
```

## 💻 Code Example — Advanced
```python
# agent_with_mcp.py - OpenAI Agents SDK consuming an MCP server (imports + construction ran; no model call)
import asyncio, sys                                    # standard libs
from agents import Agent                               # agent definition
from agents.mcp import MCPServerStdio                  # MCP server wrapper for the SDK

async def build_agent() -> None:                       # async because server start is async
    async with MCPServerStdio(                         # starts + stops server subprocess safely
        params={"command": sys.executable, "args": ["server.py"]},   # launch command
        cache_tools_list=True,                         # avoid re-listing tools every run (saves latency)
    ) as server:                                       # server is connected here
        tools = await server.list_tools()              # verified: returns the server's tools
        print([t.name for t in tools])                 # -> ['get_duty_rate', 'classify']
        agent = Agent(                                 # build the agent
            name="Tariff Agent",                       # display name
            instructions="Use tools to find duty rates.",   # system prompt
            mcp_servers=[server],                      # MCP tools auto-added to the agent
        )
        # Runner.run(agent, "Duty for 6403?") would call the LLM -> not run, needs OPENAI_API_KEY
        print(agent.name, len(agent.mcp_servers))      # -> Tariff Agent 1

asyncio.run(build_agent())                             # run it
```
Error handling: if the MCP server crashes, the client raises on the next call; wrap `Runner.run` in try/except and restart the server. Token usage: both styles send tool JSON schemas to the LLM, so token cost is the same; MCP adds only a small latency per call (process/network hop).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Regular tool | LangChain `@tool` | `@tool` decorator | `@function_tool` | Function / `FunctionTool` |
| MCP tool | `langchain-mcp-adapters` (verified) | MCP integration (verify docs) | `agents.mcp.MCPServerStdio` etc. (verified) | `autogen-ext` MCP workbench (verify docs) |
| Reuse across frameworks | No (regular) / Yes (MCP) | Same | Same | Same |
| Isolation | Same process | Same process | Same process | Same process |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Making every helper an MCP server.
✅ Correct: Keep pure, app-private functions as regular tools; use MCP only for shared or privileged capabilities.

❌ Mistake 2: Assuming MCP tools are automatically safe.
✅ Correct: They are remote code with LLM-controlled arguments. Validate args, use least-privilege credentials, require approval for writes.

❌ Mistake 3: Starting a new server subprocess on every request.
✅ Correct: Keep a long-lived session (or HTTP server) and cache the tool list.

---

## 🧠 Tricky Interview Question
"Your agent has 6 tools and one team. A teammate wants to migrate all of them to MCP. Do you agree?"

Answer: Not by default. Migration adds deployment, versioning, auth and a network hop for no reuse benefit. Migrate only tools that are (a) needed by several apps, (b) require secrets/privileges the agent should not hold, (c) owned by a different team, or (d) written in another language. Keep a thin regular-tool wrapper for hot-path, latency-sensitive calls.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Main difference between MCP tool and function tool?
A1: Function tool is registered in-process in one app; MCP tool lives in a separate server using a standard protocol, reusable by any MCP client.

Q2: [Medium] Does MCP change how the LLM chooses tools?
A2: No. The LLM still sees names + JSON schemas. MCP changes discovery, transport and ownership.

Q3: [Hard] What extra failure modes does MCP introduce?
A3: Server crash/timeouts, protocol version mismatch, auth expiry, stale tool lists, network partitions, and tool-description injection from untrusted servers.

Q4: [Hard] How do you keep latency low with MCP?
A4: Persistent sessions, streamable HTTP with stateless mode behind a load balancer, `cache_tools_list`, batching, co-locating server and agent.

Q5: [System Design] Plan migration of 40 in-agent tools to MCP.
A5: Inventory tools; group by domain/owner; wrap each group in a server; keep identical tool names so prompts do not change; shadow-run both versions comparing outputs; roll out per agent with a feature flag; add observability (trace id passed in tool metadata).

---

## 💰 Cost Impact
Token cost is equal for both styles: tool schemas count as input tokens either way (roughly 100-300 tokens/tool, approximate - measure). Real extra cost of MCP is infra (another service) and a few ms to tens of ms per call. Savings come from engineering time: one implementation, not N. Tip: filter tools per agent (`tool_filter` in the OpenAI SDK MCP classes) to cut schema tokens.

---

## 🔷 When to Use
✅ Use MCP when:
- Multiple apps/frameworks share a tool
- Secrets must stay off the agent host
- Tool owned by another team/language

❌ Use regular tools when:
- Single app, tiny helper functions
- Hot-path calls where every ms matters
- Prototype or hackathon

---

## 📊 Visual Diagram
```
 REGULAR                              MCP
 +-----------------+          +-----------+   stdio/HTTP   +-----------+
 | Agent process   |          | Agent A   |--------------->|           |
 |  LLM + tool fn  |          +-----------+                | MCP Server|--> DB
 +-----------------+          +-----------+                | (1 copy)  |
 (copy per app)               | Agent B   |--------------->|           |
                              +-----------+                +-----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function tool | In-process callable for an agent | agent के अंदर का function |
| MCP tool | Tool served by an MCP server | MCP server का tool |
| Adapter | Converts MCP tools to framework tools | अनुवादक layer |
| tool_filter | Limit which tools an agent sees | tools छाँटना |
| Trust boundary | Where privileges change | भरोसे की सीमा |

---

## ⚡ 3-Line Summary
English: Regular tools are in-process and framework-specific; MCP tools are out-of-process and portable. Token cost is the same; trade-off is reuse and isolation vs. extra moving parts. Migrate only shared or privileged tools.
Hindi: Regular tools in-process और framework-specific होते हैं; MCP tools अलग process में और portable। Token cost बराबर है; trade-off है reuse और isolation बनाम extra हिस्से। सिर्फ़ shared या privileged tools migrate करें।

---

## ➡️ Next Topic
**003. MCP Architecture (Host, Client, Server)** - to see exactly who owns the LLM, the connection and the tools.

---
