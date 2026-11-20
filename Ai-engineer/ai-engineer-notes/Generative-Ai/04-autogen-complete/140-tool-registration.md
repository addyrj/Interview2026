---

# 140. Tool Registration
# हिंदी में: Tool Registration — tools को agent से जोड़ना
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
Registering a tool means making it available to an agent. v0.2 used decorators (`register_for_llm` on the caller and `register_for_execution` on the executor). In v0.4 there are three ways: pass `tools=[...]` to `AssistantAgent`, pass a `workbench=` (a container of tools, e.g. `StaticWorkbench`, or `McpWorkbench` for MCP servers), or, at the Core level, use `ToolAgent`.

## 🔵 सरल परिभाषा (Hindi)
Tool register करने का मतलब उसे agent के लिए उपलब्ध कराना। v0.2 में decorators थे (call करने वाले पर `register_for_llm` और execute करने वाले पर `register_for_execution`)। v0.4 में तीन तरीके हैं: `AssistantAgent` को `tools=[...]` देना, `workbench=` देना (tools का container, जैसे `StaticWorkbench`, या MCP servers के लिए `McpWorkbench`), या Core level पर `ToolAgent` इस्तेमाल करना।

---

## 🔴 Problem it Solves
Two-agent registration in v0.2 confused people (which agent proposes, which executes?). Static tool lists also cannot change per tenant or per request, and cannot discover tools from external servers. You need registration that is simple for the common case and dynamic for the advanced case (permissions, MCP).

## 🔴 यह क्यों बना? (Hindi)
v0.2 में दो-agent registration लोगों को उलझाता था (कौन प्रस्ताव देता है, कौन चलाता है?)। Static tool lists tenant या request के हिसाब से बदल भी नहीं सकतीं और बाहरी servers से tools खोज भी नहीं सकतीं। ऐसा registration चाहिए जो सामान्य मामले में सरल और advanced मामले में (permissions, MCP) dynamic हो।

---

## 🟢 How it Works

```
Step 1 -> Simple: AssistantAgent(name, client, tools=[fn, FunctionTool(...)])
Step 2 -> Same agent sees schemas, requests calls, and executes them (no second agent)
Step 3 -> Dynamic: wb = StaticWorkbench([FunctionTool(...)]) built per request/role
Step 4 -> AssistantAgent(name, client, workbench=wb)
Step 5 -> MCP: McpWorkbench(StdioServerParams(...)) discovers tools from an MCP server at runtime
Step 6 -> Do NOT pass the same tools via both tools= and workbench= for the same names
Step 7 -> Core level: ToolAgent(description, tools=[...]) answers FunctionCall messages; tool_agent_caller_loop drives the loop
Step 8 -> Verify what the model sees: list_tools() / tool names
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> सरल: AssistantAgent(name, client, tools=[fn, FunctionTool(...)])
Step 2 -> वही agent schemas देखता है, calls माँगता है और उन्हें चलाता है (दूसरा agent नहीं)
Step 3 -> dynamic: wb = StaticWorkbench([FunctionTool(...)]) हर request/role के लिए बनाओ
Step 4 -> AssistantAgent(name, client, workbench=wb)
Step 5 -> MCP: McpWorkbench(StdioServerParams(...)) runtime पर MCP server से tools खोजता है
Step 6 -> एक ही नाम के tools tools= और workbench= दोनों से मत दो
Step 7 -> Core level: ToolAgent(description, tools=[...]) FunctionCall messages का जवाब देता है; tool_agent_caller_loop loop चलाता है
Step 8 -> जाँचो कि model क्या देखता है: list_tools() / tool names
```

---

## 🟡 Real World Example
**Role-based tariff tools.** A `viewer` role may only call `get_rate`; an `admin` role also gets `update_rate`. The service builds a `StaticWorkbench` per request from the caller's role, so the model never even sees tools it may not use. The verified offline call for role `viewer` returned tools `['get_rate']`.

## 🟡 Real Example Hindi mein
**Role-based tariff tools।** `viewer` role सिर्फ़ `get_rate` call कर सकता है; `admin` को `update_rate` भी मिलता है। Service हर request में caller के role से `StaticWorkbench` बनाती है, इसलिए model वे tools देखता ही नहीं जिनका उसे उपयोग नहीं करना। Role `viewer` के लिए verified offline call ने tools `['get_rate']` लौटाए।

---

## 💻 Code Example — Basic
Basic: the v0.2 decorator style as comments (not run) and the v0.4 `tools=[...]` style, mixing a plain function and a `FunctionTool`.

```python
# Tool registration in v0.4: pass tools=[...] when constructing the agent (no register_for_llm / register_for_execution)
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_core.tools import FunctionTool                       # tool wrapper
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

# --- v0.2 style (OLD; not run, needs pyautogen) ---
# @user_proxy.register_for_execution()
# @assistant.register_for_llm(description="duty rate")
# def get_rate(hs: str) -> str: ...

def get_rate(hs_code: str) -> str:                                # tool 1
    """Duty rate for an HS code."""
    return "20%"

def get_hs_code(product: str) -> str:                             # tool 2
    """HS code for a product."""
    return "6109.10"

async def main() -> None:
    info = {"function_calling": True, "vision": False, "json_output": False, "family": "unknown", "structured_output": False}
    agent = AssistantAgent(
        "tariff", ReplayChatCompletionClient(["ok"], model_info=info),
        tools=[get_rate, FunctionTool(get_hs_code, description="HS code for a product")],  # mix plain functions and FunctionTool
    )
    print([t.name for t in (FunctionTool(get_rate, description="x"), FunctionTool(get_hs_code, description="y"))])  # names the LLM sees
    res = await agent.run(task="hello")
    print(res.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: a per-request `StaticWorkbench` for role-based tool exposure. The `McpWorkbench` snippet is a comment: NOT run. Importing it failed here because the installed `mcp` package (2.3.0) was incompatible with `autogen-ext` 0.7.5 (`RequestContext` import error), so MCP integration is unverified; pin an `mcp` version matching the `autogen-ext[mcp]` extra.

```python
# Registration via Workbench (a tool CONTAINER) shared by several agents; MCP workbench shown but NOT run.
import asyncio                                                    # async
from fastapi import FastAPI                                       # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_core import FunctionCall                             # scripted call
from autogen_core.models import CreateResult, RequestUsage        # scripted result
from autogen_core.tools import FunctionTool, StaticWorkbench      # static container of tools
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

INFO = {"function_calling": True, "vision": False, "json_output": False, "family": "unknown", "structured_output": False}

def get_rate(hs_code: str) -> str:
    """Duty rate for an HS code."""
    return "20%"

def only_if_allowed(role: str):                                   # tiny RBAC: choose tools per caller role
    tools = [FunctionTool(get_rate, description="Duty rate lookup")]
    # admin-only tools would be appended here, e.g. if role == "admin": tools.append(...)
    return StaticWorkbench(tools)                                 # one workbench per request/role

# MCP alternative (needs the `mcp` extra + a running MCP server) -- NOT run here:
#   from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
#   async with McpWorkbench(StdioServerParams(command="python", args=["tariff_mcp_server.py"])) as wb:
#       agent = AssistantAgent("a", client, workbench=wb)          # tools discovered at runtime from the server

app = FastAPI()

@app.get("/rate/{role}")
async def rate(role: str) -> dict:
    call = CreateResult(finish_reason="function_calls",
                        content=[FunctionCall(id="1", name="get_rate", arguments='{"hs_code": "6109.10"}')],
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)
    client = ReplayChatCompletionClient([call, "Duty is 20%."], model_info=INFO)
    wb = only_if_allowed(role)                                    # tools chosen at request time
    agent = AssistantAgent("tariff", client, workbench=wb, reflect_on_tool_use=True)  # workbench= instead of tools=
    res = await agent.run(task="duty?")
    names = [t["name"] for t in await wb.list_tools()]            # what the model was allowed to see
    return {"tools": names, "answer": str(res.messages[-1].content)}

if __name__ == "__main__":
    print(TestClient(app).get("/rate/viewer").json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Registration | bind_tools / ToolNode(tools) | tools=[...] on Agent/Task | tools=[...] on Agent | tools=[...] or workbench=... |
| Dynamic per request | Build graph/tools per call | Build crew per request | Build agent per request | Build StaticWorkbench per request |
| MCP support | langchain-mcp-adapters | MCP tools integration | Native MCP server support | McpWorkbench (autogen-ext[mcp]) |
| Separate caller/executor | No | No | No | No in v0.4 (v0.2 yes) |
| Core-level | ToolNode | - | - | ToolAgent + tool_agent_caller_loop |

---

## ⚠️ Common Mistakes
❌ Mistake: Using `@assistant.register_for_llm` in v0.4.
✅ Correct: Pass the function in `tools=[...]`.

❌ Mistake: Registering admin tools on a shared agent and relying on the prompt to restrict them.
✅ Correct: Enforce permissions in code: build the tool list per role and check identity inside tools.

❌ Mistake: Passing the same tool name in both `tools=` and `workbench=`.
✅ Correct: Pick one source of tools per agent; avoid duplicates.

❌ Mistake: Using `McpWorkbench` without closing it.
✅ Correct: Use `async with McpWorkbench(...) as wb:` so the server process is stopped.

---

## 🧠 Tricky Interview Question
A tenant's tool list changes at runtime (an admin enables a new integration). A long-lived agent doesn't see it. What do you do?

Answer: Agents read their tools at construction, so a static `tools=[...]` list will not change. Options: (1) build agents per request/session from the current tenant configuration (cheap with AgentChat; state in saved context); (2) pass a workbench object whose `list_tools()` reflects current configuration; (3) with MCP, the server's tool list is discovered through the workbench, so refreshing a connection updates it (verify behaviour for your versions). Whatever you choose, enforce authorisation inside tool implementations, not only by hiding schemas, and remember schema changes alter prompt size and cost.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you register a tool in v0.4?
A1: Pass a typed function or `FunctionTool` in `tools=[...]` when creating `AssistantAgent`.

Q2: [Medium] What replaced `register_for_llm` / `register_for_execution`?
A2: A single `tools=` (or `workbench=`) argument: the same agent proposes and executes calls.

Q3: [Hard] What is a Workbench?
A3: A container that provides tool schemas and executes tool calls: `StaticWorkbench` for fixed sets, `McpWorkbench` for MCP servers.

Q4: [Hard] How do you give different users different tools?
A4: Create the agent (or workbench) per request from the user's permissions, and re-check permissions inside the tool.

Q5: [System Design] Design tool registration for a multi-tenant platform with 200 integrations.
A5: Registry keyed by tenant; a resolver builds a `StaticWorkbench` per request with only the enabled integrations (max ~10 per agent to control prompt size); route first with a cheap classifier to choose the relevant subset; MCP for third-party servers behind an allow-list; per-tool authz, timeouts, audit and rate limits; contract tests with replay clients.

---

## 💰 Cost Impact
Registration choices drive prompt size: every registered tool's schema is sent on every model call. 200 integrations registered at once is both too many for reliable tool choice and expensive. Formula: `tool_schema_tokens = sum(len(schema_i))`, paid each call. Strategies: per-request subsets (routing), short descriptions, workbenches per role, MCP servers exposing few focused tools. Measure `prompt_tokens` in `models_usage` before and after trimming the tool list. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Simple agents: `tools=[...]`.
- Role/tenant-specific tools: per-request `StaticWorkbench`.
- External tool servers: `McpWorkbench` (after verifying versions).
- Custom Core systems: `ToolAgent`.

❌ Avoid when:
- Registering every available tool on every agent.
- Relying on prompts for permissions.
- Mixing v0.2 decorators into v0.4 code.

---

## 📊 Visual Diagram
```
 v0.2:  assistant.register_for_llm(fn)  +  user_proxy.register_for_execution(fn)   (two agents)

 v0.4:  AssistantAgent(tools=[fn1, FunctionTool(fn2)])                   (one agent)
        AssistantAgent(workbench=StaticWorkbench([...]))   <-- per request / per role
        AssistantAgent(workbench=McpWorkbench(server))     <-- tools from an MCP server (not run here)
        Core: ToolAgent(tools=[...]) <-- tool_agent_caller_loop(...)

        request(role=viewer) --> [get_rate]           request(role=admin) --> [get_rate, update_rate]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tools= | Constructor argument listing tools | tools की list वाला argument |
| Workbench | Container offering and running tools | tools देने और चलाने वाला container |
| StaticWorkbench | Fixed set of tools | तय tools का set |
| McpWorkbench | Tools discovered from an MCP server | MCP server से खोजे गए tools |
| ToolAgent | Core agent executing tool calls | tool calls चलाने वाला Core agent |
| register_for_llm | v0.2 decorator (not v0.4) | v0.2 decorator (v0.4 में नहीं) |
| RBAC | Role-based access control | भूमिका-आधारित access नियंत्रण |
| allow-list | Explicitly permitted items | स्पष्ट रूप से अनुमत सूची |

---

## ⚡ 3-Line Summary
English: v0.4 registers tools with `tools=[...]` or `workbench=`; no more two-agent decorators.
Build per-request workbenches for roles and tenants, and enforce authorisation inside the tool.
Every registered schema costs prompt tokens on every call, so register only what is needed.
Hindi: v0.4 में tools `tools=[...]` या `workbench=` से register होते हैं; दो-agent decorators ख़त्म।
Roles और tenants के लिए per-request workbench बनाएँ और authorisation tool के अंदर लागू करें।
हर registered schema हर call में prompt tokens खर्च करता है, इसलिए सिर्फ़ ज़रूरी tools register करें।

---

## ➡️ Next Topic
141. Tool Execution -- what happens after registration: how calls are run, parallelised, timed out and retried.

---
