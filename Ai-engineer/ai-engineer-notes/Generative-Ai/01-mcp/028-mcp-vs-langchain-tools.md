---

# 28. MCP vs LangChain Tools
# हिंदी में: MCP बनाम LangChain Tools
# Framework: All
# Already Known: No

> Verified against: `langchain-core` 1.8.0, `langchain-mcp-adapters` 0.3.2, `langgraph` 1.2.22, `mcp` 1.30.0. Ran locally: the same Tariff function as a LangChain `@tool` and as an MCP tool (compared schemas, calls and error behaviour), and a FastAPI agent that mixes both kinds of tools, driven by a **fake chat model** (no API key). Not run: real LLM tool-selection quality, latency/throughput benchmarks (I did not measure any - statements about overhead are qualitative), other frameworks' tool decorators beyond what is cited as "verify".

---

## 🔵 Simple Definition (2-3 lines)
A **LangChain tool** is a Python callable (usually `@tool`) that runs **inside your agent process**. An **MCP tool** is a function exposed by a separate **server speaking a standard protocol**, which any MCP-capable agent can discover and call. MCP is not a replacement for LangChain tools: via `langchain-mcp-adapters` an MCP tool *becomes* a LangChain tool (we saw both as `StructuredTool`).

## 🔵 सरल परिभाषा (Hindi)
**LangChain tool** एक Python callable (आमतौर पर `@tool`) है जो **आपके agent process के अंदर** चलता है। **MCP tool** अलग **server** द्वारा दिया गया function है जो **मानक protocol** बोलता है, और कोई भी MCP-सक्षम agent उसे खोजकर call कर सकता है। MCP, LangChain tools का विकल्प नहीं है: `langchain-mcp-adapters` से MCP tool खुद LangChain tool बन जाता है (दोनों `StructuredTool` दिखे)।

---

## 🔴 Problem it Solves
Choosing wrongly costs you. Putting every tool behind MCP adds processes, auth and deployment work for functions only one agent uses. Keeping every tool in-process means five teams copy the same tariff tool into five agents in three frameworks, and each copy drifts. The comparison tells you where each belongs.

## 🔴 यह क्यों बना? (Hindi)
गलत चुनाव महँगा पड़ता है। हर tool MCP के पीछे रखने से ऐसे functions के लिए भी processes, auth और deployment का काम बढ़ता है जिन्हें सिर्फ़ एक agent इस्तेमाल करता है। हर tool in-process रखने से पाँच teams वही tariff tool तीन frameworks के पाँच agents में कॉपी करती हैं, और हर copy अलग हो जाती है। यह तुलना बताती है कि कौन-सा कहाँ फिट बैठता है।

---

## 🟢 How it Works

```
Observed on the same function (get_tariff_rate):
schema (local @tool)  : {'hs_code': {'title': 'Hs Code', 'type': 'string'}}
schema (MCP, adapted) : {'hs_code': {'title': 'Hs Code', 'type': 'string'}}   <- identical
call result (local)   : '20.0%'                                              (plain str)
call result (MCP)     : [{'type': 'text', 'text': '20.0%', 'id': ...}]       (content blocks)
bad input (local)     : raises ValueError('unknown HS code zz')              (exception in YOUR code)
bad input (MCP)       : returns text 'Error executing tool get_tariff_rate: unknown HS code zz'
type                  : both StructuredTool

Execution paths:
LangChain @tool : model -> tool_call -> your Python function (same process)
MCP tool        : model -> tool_call -> adapter -> MCP client -> (stdio/HTTP) -> server process -> function
```

## 🟢 कैसे काम करता है? (Hindi)

```
एक ही function (get_tariff_rate) पर देखा गया:
schema (local @tool)  : {'hs_code': {'title': 'Hs Code', 'type': 'string'}}
schema (MCP, adapted) : {'hs_code': {'title': 'Hs Code', 'type': 'string'}}   <- एक जैसा
call result (local)   : '20.0%'                                              (साधारण str)
call result (MCP)     : [{'type': 'text', 'text': '20.0%', 'id': ...}]       (content blocks)
गलत input (local)     : ValueError('unknown HS code zz') उठता है              (आपके code में exception)
गलत input (MCP)       : text लौटता है 'Error executing tool get_tariff_rate: unknown HS code zz'
type                  : दोनों StructuredTool

Execution paths:
LangChain @tool : model -> tool_call -> आपका Python function (वही process)
MCP tool        : model -> tool_call -> adapter -> MCP client -> (stdio/HTTP) -> server process -> function
```

---

## 🟡 Real World Example
**Tariff Agent**: `format_duty_message` is a tiny private helper - a plain `@tool`. `get_tariff_rate` and `calc_duty` belong to the customs team and are used by the support bot, the broker assistant and a CrewAI research crew - so they live in one MCP server. The agent gets both through one tool list.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `format_duty_message` छोटा private helper है - साधारण `@tool`। `get_tariff_rate` और `calc_duty` customs team के हैं और support bot, broker assistant तथा एक CrewAI research crew इस्तेमाल करती हैं - इसलिए वे एक MCP server में रहते हैं। Agent को दोनों एक ही tool list में मिलते हैं।

---

## 💻 Code Example — Basic
```python
# compare_tools.py - same capability as LangChain @tool and as an MCP tool (ran; server = tariff_server.py from note 015)
import asyncio, sys                                         # stdlib
from langchain_core.tools import tool                       # in-process LangChain tool decorator
from langchain_mcp_adapters.client import MultiServerMCPClient   # MCP -> LangChain adapter

RATES: dict[str, float] = {"6109.10": 20.0, "7318.15": 10.0}   # same data as tariff_server.py

@tool                                                       # LangChain tool: lives in THIS process
def get_tariff_rate(hs_code: str) -> str:                   # schema from type hints
    """Return duty percent for an HS code."""               # description from docstring
    if hs_code not in RATES:
        raise ValueError(f"unknown HS code {hs_code}")
    return f"{RATES[hs_code]}%"

async def main() -> None:
    client = MultiServerMCPClient({"tariff": {"command": sys.executable, "args": ["tariff_server.py"], "transport": "stdio"}})
    mcp_tools = await client.get_tools()                    # MCP tools, adapted to LangChain tools
    mcp_rate = next(t for t in mcp_tools if t.name == "get_tariff_rate")

    print("local  schema:", get_tariff_rate.args)           # identical schema to the MCP one
    print("mcp    schema:", mcp_rate.args)
    print("local  call  :", await get_tariff_rate.ainvoke({"hs_code": "6109.10"}))   # 20.0%
    print("mcp    call  :", await mcp_rate.ainvoke({"hs_code": "6109.10"}))           # list of content blocks
    try:                                                    # error behaviour differs
        await get_tariff_rate.ainvoke({"hs_code": "zz"})
    except ValueError as e:
        print("local  error : raised ValueError ->", e)
    print("mcp    error :", await mcp_rate.ainvoke({"hs_code": "zz"}))   # returned as text, not raised
    print("same type    :", type(get_tariff_rate).__name__, type(mcp_rate).__name__)   # StructuredTool x2

asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# hybrid_agent_api.py - one agent, two kinds of tools: in-process @tool + shared MCP tools (ran with TestClient + fake model)
import sys                                                  # interpreter path
from contextlib import asynccontextmanager                  # lifespan helper
from typing import Any, AsyncIterator                       # hints
from fastapi import FastAPI, HTTPException                  # web layer
from langchain_core.tools import BaseTool, tool             # tool base + decorator
from langchain_mcp_adapters.client import MultiServerMCPClient   # MCP adapter
from langgraph.prebuilt import create_react_agent           # ReAct loop (deprecated alias in 1.x, still works)
from pydantic import BaseModel

@tool                                                       # private, in-process: no protocol, no network
def format_duty_message(rate: str, value_usd: float) -> str:
    """Format a human-readable duty message."""
    return f"At {rate}, duty on ${value_usd:,.2f} goods is computed by the tariff service."

class Ask(BaseModel):
    question: str

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = MultiServerMCPClient(                          # shared, team-owned tools via MCP
        {"tariff": {"command": sys.executable, "args": ["tariff_server.py"], "transport": "stdio"}},
        tool_name_prefix=True)                              # avoid clashes with local tool names
    mcp_tools: list[BaseTool] = await client.get_tools()    # discovered at startup
    all_tools: list[BaseTool] = [format_duty_message, *mcp_tools]   # same interface for the agent
    app.state.names = [t.name for t in all_tools]
    app.state.agent = create_react_agent(app.state.model, all_tools)   # model injected (ChatAnthropic/ChatOpenAI in prod)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/ask")
async def ask(body: Ask) -> dict[str, Any]:
    try:
        out = await app.state.agent.ainvoke({"messages": [("user", body.question)]})   # async loop
    except Exception as exc:                                # model/tool/network failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"tools": app.state.names, "answer": str(out["messages"][-1].content)}
```
Observed: the tool list was `['format_duty_message', 'tariff_get_tariff_rate', 'tariff_calc_duty']`; a scripted fake model called one MCP tool and then the local tool, and the route returned `answer 'Done'`. Token usage: the model sees only names, descriptions and schemas - identical for both kinds, so MCP does not change the prompt size; extra tokens come from how many tools you expose. Error handling: local tools raise; MCP tools return text errors by default - normalise this in one place. Async: both are awaited via `ainvoke`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| In-process tool | LangChain `@tool` / `ToolNode` (verified) | `@tool` / BaseTool (verify docs) | `@function_tool` (verify docs) | Python function tools (verify) |
| MCP tool | via adapters -> same `StructuredTool` (verified) | MCP support (verify) | `MCPServerStdio` etc. (verified, note 018) | MCP workbench (verify) |
| Reuse across frameworks | in-process: no; MCP: yes | same | same | same |
| Mixed in one agent | yes (verified above) | verify | yes - `tools=[...]` plus `mcp_servers=[...]` | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Wrapping every 5-line helper in an MCP server.
✅ Correct: Keep private helpers as in-process tools.

❌ Mistake 2: Copy-pasting a shared business tool into each agent.
✅ Correct: Expose it once through MCP and load it everywhere.

❌ Mistake 3: Assuming MCP tools raise Python exceptions like `@tool`.
✅ Correct: Through the adapter errors return as text by default (observed); set `handle_tool_errors` if you need exceptions.

❌ Mistake 4: Expecting MCP to improve tool selection.
✅ Correct: The model sees the same schema either way; quality depends on names/descriptions.

---

## 🧠 Tricky Interview Question
"Your team insists 'MCP is just LangChain tools with extra steps'. When are they right, and when wrong?"

Answer: Right when one agent in one framework uses the function: MCP adds a process, transport, auth and ops with no benefit - an in-process tool is faster to build and debug (no serialisation across a process boundary). Wrong when the capability is shared across agents, frameworks, languages or teams, needs independent deployment/versioning, sandboxing of credentials (the agent never holds DB credentials; the server does), or must be discoverable by off-the-shelf hosts (Claude Desktop, IDEs). Also: MCP offers more than tools (resources, prompts, sampling). A good answer gives the decision criteria rather than a side.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Can I use an MCP tool in LangChain?
A1: Yes, `langchain-mcp-adapters` converts MCP tools to LangChain `StructuredTool`s.

Q2: [Medium] Biggest architectural difference?
A2: Process boundary and standard protocol: MCP tools run in a separate server and are discoverable at run time; LangChain tools are code in your agent.

Q3: [Hard] Security difference?
A3: MCP can isolate credentials and permissions in the server (agent never sees DB passwords) and be audited centrally; in-process tools share the agent's memory and privileges. But MCP adds network attack surface (auth, Host checks).

Q4: [Hard] Performance difference?
A4: MCP adds inter-process/network hops and serialisation per call (I did not benchmark it here). Usually small next to LLM latency, but matters for chatty tools; cache tool lists and prefer coarse-grained tools.

Q5: [System Design] Decide which of 30 tools go MCP.
A5: Score each by number of consumers, need for independent releases, credential sensitivity, language diversity. Shared/sensitive/multi-consumer -> MCP; private/simple/single-agent -> in-process. Review quarterly as usage changes.

---

## 💰 Cost Impact
LLM tokens: same either way (same schemas). Infra: MCP adds a service to run and monitor; in-process tools add none. People cost: shared MCP servers avoid N duplicated implementations. If tools differ in count, trim the list - 40 tools cost more per turn than 8 regardless of origin (no figures claimed).

---

## 🔷 When to Use
✅ Use MCP when:
- Multiple agents/frameworks/teams share a capability
- You want credential isolation, independent deploys, host compatibility

✅ Use in-process tools when:
- Private, simple, single-agent logic; fastest iteration

❌ Avoid MCP when:
- A function is trivial and used once

---

## 📊 Visual Diagram
```
                 +-- @tool format_duty_message (in-process) ----------------+
 Agent (LLM) ----+                                                          |-> same tool interface
                 +-- adapter -> MCP client --stdio/HTTP--> Tariff MCP server +
                                                   ^                 ^
                              CrewAI crew ---------+   Claude Desktop+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| In-process tool | Function inside the agent app | agent app के अंदर का function |
| MCP tool | Function exposed by an MCP server | MCP server द्वारा दिया function |
| Adapter | Converts MCP tool to framework tool | MCP tool को framework tool में बदलता है |
| Process boundary | Separate running program | अलग चलता program |
| Credential isolation | Secrets stay in the server | secrets server में ही रहते हैं |

---

## ⚡ 3-Line Summary
English: MCP tools and LangChain tools look identical to the model; the difference is where they run and who can reuse them. Use in-process tools for private logic and MCP for shared, sensitive or cross-framework capabilities. Mix both through adapters.
Hindi: Model को MCP tools और LangChain tools एक जैसे दिखते हैं; फ़र्क यह है कि वे कहाँ चलते हैं और कौन उन्हें reuse कर सकता है। निजी logic के लिए in-process tools और साझा, संवेदनशील या cross-framework capabilities के लिए MCP लें। Adapters से दोनों मिलाएँ।

---

## ➡️ Next Topic
**029. MCP vs OpenAI Function Calling** - the same question against OpenAI's native tool-calling mechanism.

---
