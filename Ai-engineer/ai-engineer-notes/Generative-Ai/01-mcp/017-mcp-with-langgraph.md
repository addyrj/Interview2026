---

# 17. MCP with LangGraph
# हिंदी में: LangGraph के साथ MCP
# Framework: LangGraph
# Already Known: No

> Verified against: `langgraph` 1.2.22, `langchain-mcp-adapters` 0.3.2, `langchain-core` 1.8.0, `mcp` 1.30.0. The StateGraph with `ToolNode` over a persistent MCP stdio session was run with a **fake chat model**; the FastAPI lifespan pattern was run with `TestClient` (MCP part). Real LLM + checkpointer backends (Postgres/Redis): not run - need keys/services.

---

## 🔵 Simple Definition (2-3 lines)
In LangGraph you build the agent loop yourself as a graph: an `agent` node calls the model, a `ToolNode` runs tools, and `tools_condition` decides whether to loop. MCP tools plug in as ordinary tools via `load_mcp_tools(session)`, so you control state, retries, approvals and persistence.

## 🔵 सरल परिभाषा (Hindi)
LangGraph में agent loop आप खुद graph की तरह बनाते हैं: `agent` node model बुलाता है, `ToolNode` tools चलाता है, और `tools_condition` तय करता है कि loop चलेगा या नहीं। MCP tools `load_mcp_tools(session)` से सामान्य tools की तरह जुड़ते हैं, इसलिए state, retries, approvals और persistence आपके control में रहते हैं।

---

## 🔴 Problem it Solves
Prebuilt ReAct agents hide the loop. Real tariff workflows need more: validate HS code first, ask a human before a high-value filing, resume after a crash. A graph makes each step explicit, while MCP keeps the tools reusable and outside the graph code.

## 🔴 यह क्यों बना? (Hindi)
Prebuilt ReAct agents loop को छिपा देते हैं। असली tariff workflow में और चाहिए: पहले HS code validate करना, बड़ी value की filing से पहले human से पूछना, crash के बाद resume करना। Graph हर step को साफ़ दिखाता है, और MCP tools को graph code से बाहर reusable रखता है।

---

## 🟢 How it Works

```
Step 1 -> Open MCP session (stdio_client + ClientSession), initialize()
Step 2 -> tools = await load_mcp_tools(session)
Step 3 -> model = llm.bind_tools(tools)
Step 4 -> START -> agent node: model.ainvoke(messages)
Step 5 -> tools_condition: AIMessage has tool_calls? -> "tools" else END
Step 6 -> ToolNode runs MCP tools, appends ToolMessage -> back to agent
Step 7 -> loop until no tool_calls -> final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> MCP session खोलें (stdio_client + ClientSession), initialize()
Step 2 -> tools = await load_mcp_tools(session)
Step 3 -> model = llm.bind_tools(tools)
Step 4 -> START -> agent node: model.ainvoke(messages)
Step 5 -> tools_condition: AIMessage में tool_calls हैं? -> "tools" वरना END
Step 6 -> ToolNode MCP tools चलाकर ToolMessage जोड़ता है -> वापस agent
Step 7 -> जब तक tool_calls हैं loop; फिर final answer
```

---

## 🟡 Real World Example
**Tariff Agent**: nodes `classify` -> `agent` <-> `tools` -> `review`. The `tools` node calls the shared tariff MCP server; `review` pauses for human approval when duty > 10,000 USD (via `interrupt`, not run here). State is checkpointed so a crashed worker resumes.

## 🟡 Real Example Hindi mein
**Tariff Agent**: nodes `classify` -> `agent` <-> `tools` -> `review`। `tools` node साझा tariff MCP server बुलाता है; duty 10,000 USD से ज़्यादा हो तो `review` human approval के लिए रुकता है (`interrupt` से, यहाँ run नहीं किया)। State checkpoint होती है, इसलिए crash के बाद worker resume कर सकता है।

---

## 💻 Code Example — Basic
```python
# basic_graph.py - StateGraph + ToolNode over MCP tools (ran; server = tariff_server.py from note 015)
import asyncio, sys                                         # stdlib
from typing import Annotated, Any, TypedDict                # type hints
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel   # offline model
from langchain_core.messages import AIMessage, AnyMessage   # message types
from langchain_mcp_adapters.tools import load_mcp_tools     # MCP session -> LangChain tools
from langgraph.graph import END, START, StateGraph         # graph builder
from langgraph.graph.message import add_messages            # reducer that appends messages
from langgraph.prebuilt import ToolNode, tools_condition    # tool runner + router
from mcp import ClientSession, StdioServerParameters        # MCP client
from mcp.client.stdio import stdio_client                   # stdio transport

class State(TypedDict):                                     # graph state
    messages: Annotated[list[AnyMessage], add_messages]     # append-only message list

class FakeLLM(GenericFakeChatModel):                        # scripted model for offline test
    def bind_tools(self, tools: Any, **kw: Any) -> "FakeLLM":
        return self                                         # real code: ChatAnthropic(...).bind_tools(tools)

async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
    async with stdio_client(params) as (read, write):       # start MCP server
        async with ClientSession(read, write) as session:   # persistent session
            await session.initialize()                      # handshake
            tools = await load_mcp_tools(session)           # tools/list -> LangChain tools
            llm = FakeLLM(messages=iter([                   # reply 1: call tool; reply 2: final text
                AIMessage(content="", tool_calls=[{"name": "calc_duty",
                    "args": {"value_usd": 1000, "rate_percent": 10}, "id": "c1"}]),
                AIMessage(content="100 USD duty")]))
            model = llm.bind_tools(tools)                   # tell model about the tools

            async def agent(state: State) -> dict[str, list[Any]]:   # node 1: call the model
                return {"messages": [await model.ainvoke(state["messages"])]}

            g = StateGraph(State)                           # build graph
            g.add_node("agent", agent)                      # model node
            g.add_node("tools", ToolNode(tools))            # tool execution node
            g.add_edge(START, "agent")                      # entry
            g.add_conditional_edges("agent", tools_condition)   # tool_calls? -> "tools" else END
            g.add_edge("tools", "agent")                    # loop back with tool result
            app = g.compile()                               # runnable graph
            out = await app.ainvoke({"messages": [("user", "duty?")]})   # run
            for m in out["messages"]:                       # human, ai(tool call), tool, ai(final)
                print(type(m).__name__, m.content)

asyncio.run(main())                                         # observed last line: AIMessage 100 USD duty
```

## 💻 Code Example — Advanced
```python
# graph_api.py - FastAPI service: MCP session owned by lifespan, graph compiled once (MCP + route ran)
import sys                                                  # interpreter path
from contextlib import AsyncExitStack, asynccontextmanager  # keep session open for app lifetime
from typing import Annotated, Any, AsyncIterator, TypedDict # hints
from fastapi import FastAPI, HTTPException                  # web layer
from langchain_core.messages import AnyMessage              # message type
from langchain_mcp_adapters.tools import load_mcp_tools     # MCP -> tools
from langgraph.graph import END, START, StateGraph         # graph
from langgraph.graph.message import add_messages            # reducer
from langgraph.prebuilt import ToolNode, tools_condition    # tool node + router
from mcp import ClientSession, StdioServerParameters        # MCP client
from mcp.client.stdio import stdio_client                   # stdio
from pydantic import BaseModel                              # body model

class State(TypedDict):                                     # state with a step counter
    messages: Annotated[list[AnyMessage], add_messages]

class Ask(BaseModel):
    question: str

def build_graph(model: Any, tools: list[Any]) -> Any:       # pure function -> compiled graph
    bound = model.bind_tools(tools)                         # attach tools to model
    async def agent(state: State) -> dict[str, list[Any]]:
        return {"messages": [await bound.ainvoke(state["messages"])]}
    g = StateGraph(State)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(tools, handle_tool_errors=True))   # tool errors become ToolMessages
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile()                                      # add checkpointer=... for persistence

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncExitStack() as stack:                   # closes MCP on shutdown
        params = StdioServerParameters(command=sys.executable, args=["tariff_server.py"])
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        tools = await load_mcp_tools(session)               # discover once
        app.state.graph = build_graph(app.state.model, tools)   # model injected (ChatAnthropic in prod)
        yield

app = FastAPI(lifespan=lifespan)

@app.post("/ask")
async def ask(body: Ask) -> dict[str, Any]:
    try:
        out = await app.state.graph.ainvoke(                # recursion_limit stops infinite loops
            {"messages": [("user", body.question)]}, config={"recursion_limit": 8})
    except Exception as exc:                                # GraphRecursionError, model errors...
        raise HTTPException(502, f"{type(exc).__name__}") from exc
    last = out["messages"][-1]
    return {"answer": str(last.content), "usage": str(getattr(last, "usage_metadata", None))}
```
Token usage: read `usage_metadata` from each AI message (real models only; the fake model has none). Error handling: `recursion_limit` plus `handle_tool_errors`. Async: `ainvoke`. The route ran with a scripted fake model in the same way as note 016 (answer "Duty is 20%").

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Loop control | Explicit graph (verified) | Crew/Task process | `Runner` loop (hidden) | Team/agent loop |
| State + resume | Checkpointers | limited (verify) | sessions | state save (verify) |
| Human-in-loop | `interrupt` | human_input flag (verify) | `require_approval` for MCP | UserProxy |
| MCP | via adapters (verified) | verify | native classes | workbench (verify) |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Opening the MCP session inside a node.
✅ Correct: Open once outside, pass tools into the graph builder.

❌ Mistake 2: No `recursion_limit`.
✅ Correct: Set a limit (we used 8); it raises an error instead of looping.

❌ Mistake 3: Using `create_react_agent` in new code.
✅ Correct: It prints a deprecation warning in LangGraph 1.x (moved to `langchain.agents.create_agent`); a hand-built graph is stable.

❌ Mistake 4: Forgetting `bind_tools` on the model.
✅ Correct: The model cannot emit tool calls unless tools are bound.

---

## 🧠 Tricky Interview Question
"Your graph is compiled at startup with MCP tools. The tariff team deploys a new tool. How does the agent see it?"

Answer: It does not - tools were captured at compile time. Options: restart/rolling deploy, rebuild the graph when a `tools/list_changed` notification arrives, or build the graph per request from a cached tool list refreshed on a TTL. Mention the trade-off: rebuilding changes behaviour mid-conversation, so pin the tool list per thread.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What routes between agent and tools?
A1: `tools_condition` - goes to `"tools"` if the last AI message has `tool_calls`, else to END.

Q2: [Medium] `load_mcp_tools(session)` vs `MultiServerMCPClient`?
A2: `load_mcp_tools` uses a session you own (stateful, persistent); the client manages connections for you and supports many servers.

Q3: [Hard] How add human approval before `calc_duty` on big values?
A3: Add a node before `tools` that calls `interrupt(...)` when the pending tool args exceed a threshold; resume with a checkpointer and `Command(resume=...)`. (Concept; not run here.)

Q4: [Hard] Concurrency with one shared stdio session?
A4: MCP multiplexes requests by id so concurrent calls work, but one slow tool still shares one process. For heavy load use HTTP servers with replicas.

Q5: [System Design] Durable tariff workflows.
A5: Graph + Postgres checkpointer, thread_id per case, MCP over HTTP with auth, idempotent tools, tracing, and recursion/time limits.

---

## 💰 Cost Impact
Cost = turns x (messages + tool schemas) input tokens + outputs. The graph makes turn count visible and boundable (`recursion_limit`). Tips: trim message history in the agent node, summarise old tool outputs, pass only needed tools per graph, use cheaper models for routing nodes. Numbers vary by provider (approximate - verify on pricing pages).

---

## 🔷 When to Use
✅ Use when:
- You need custom routing, approvals, persistence
- Many steps beyond simple tool calling

❌ Avoid when:
- A single tool call answers the question

---

## 📊 Visual Diagram
```
 START -> [agent] --tool_calls?--yes--> [tools: ToolNode] --+
              ^                                            |
              +--------------------------------------------+
              |no
              v
             END           [tools] -> MCP ClientSession -> tariff_server.py
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StateGraph | Graph with shared typed state | साझा state वाला graph |
| ToolNode | Node that executes tool calls | tool calls चलाने वाला node |
| tools_condition | Router on tool_calls | tool_calls पर routing |
| recursion_limit | Max graph steps | अधिकतम steps |
| checkpointer | Saves state for resume | state सहेजकर resume |

---

## ⚡ 3-Line Summary
English: Build the loop as a graph and feed it MCP tools via `load_mcp_tools`. Own the session in lifespan, cap steps with `recursion_limit`. Add checkpointers and interrupts for production flows.
Hindi: Loop को graph बनाएं और `load_mcp_tools` से MCP tools दें। Session lifespan में रखें, `recursion_limit` से steps सीमित करें। Production के लिए checkpointer और interrupt जोड़ें।

---

## ➡️ Next Topic
**018. MCP with OpenAI** - the Agents SDK's native MCP classes and the Responses API hosted MCP tool.

---
