---

# 19. MCP Tool Discovery
# हिंदी में: MCP Tool Discovery (tools की खोज)
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0 (protocol 2025-11-25). A stdio server that adds a tool at run time and sends `notifications/tools/list_changed`, a client `message_handler` that receives it, cursor pagination loop, and a FastAPI registry with TTL + invalidation were all run locally. Observed oddity: FastMCP 1.30.0 reports `capabilities.tools.listChanged=False` yet the notification still arrived - do not rely on the capability flag alone. Real LLM use: not run.

---

## 🔵 Simple Definition (2-3 lines)
Discovery is how a client learns what a server offers. The client sends `tools/list` after `initialize` and gets each tool's `name`, `description` and `inputSchema` (JSON Schema). Results can be paginated with `nextCursor`, and servers may send `notifications/tools/list_changed` when the list changes.

## 🔵 सरल परिभाषा (Hindi)
Discovery वह तरीका है जिससे client जानता है कि server क्या देता है। `initialize` के बाद client `tools/list` भेजता है और हर tool का `name`, `description` और `inputSchema` (JSON Schema) पाता है। Results `nextCursor` से पन्नों में आ सकते हैं, और list बदलने पर server `notifications/tools/list_changed` भेज सकता है।

---

## 🔴 Problem it Solves
Hard-coded tool lists go stale: the tariff team ships `bulk_rates` and agents never see it, or an agent calls a removed tool. Discovery makes the server the source of truth. But naive discovery (list on every request, expose all tools) wastes latency and tokens, so caching and filtering matter.

## 🔴 यह क्यों बना? (Hindi)
Hard-coded tool list पुरानी पड़ जाती है: tariff team `bulk_rates` जारी करती है और agents उसे कभी नहीं देखते, या agent हटाए गए tool को बुलाता है। Discovery server को सच्चाई का स्रोत बनाती है। पर हर request पर list करना और सारे tools दिखाना latency और tokens बर्बाद करता है, इसलिए caching और filtering ज़रूरी है।

---

## 🟢 How it Works

```
Step 1 -> client: initialize -> server returns capabilities (tools: {...})
Step 2 -> client: tools/list (cursor=None)
Step 3 -> server: {tools:[{name, description, inputSchema, annotations?}], nextCursor?}
Step 4 -> if nextCursor: call tools/list(cursor=nextCursor) until it is null
Step 5 -> client caches the list; filters it; gives it to the model
Step 6 -> server changes tools -> notifications/tools/list_changed
Step 7 -> client marks cache dirty and re-lists (not on every call)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> client: initialize -> server capabilities लौटाता है (tools: {...})
Step 2 -> client: tools/list (cursor=None)
Step 3 -> server: {tools:[{name, description, inputSchema, annotations?}], nextCursor?}
Step 4 -> nextCursor हो तो tools/list(cursor=nextCursor) तब तक जब तक वह null न हो
Step 5 -> client list cache करता है; filter करता है; model को देता है
Step 6 -> server के tools बदलें -> notifications/tools/list_changed
Step 7 -> client cache को dirty करके दोबारा list करता है (हर call पर नहीं)
```

---

## 🟡 Real World Example
**Tariff Agent**: the customs MCP server has 4 tools in the morning. After a deploy it registers `bulk_rates` and sends `list_changed`. The agent platform's registry marks its cache dirty and exposes the new tool to the next conversation, without redeploying the agents.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs MCP server में सुबह 4 tools हैं। Deploy के बाद वह `bulk_rates` register करके `list_changed` भेजता है। Agent platform की registry cache को dirty कर देती है और अगली बातचीत में नया tool दिखा देती है, agents को दोबारा deploy किए बिना।

---

## 💻 Code Example — Basic
```python
# dyn_server.py - server that registers a tool at runtime and notifies clients (ran)
from mcp.server.fastmcp import Context, FastMCP            # server helper + request context

mcp = FastMCP("dyn")                                        # server name

@mcp.tool()                                                 # tool available from the start
def get_tariff_rate(hs_code: str) -> str:                   # typed arg
    """Return duty percent for an HS code."""               # description clients see
    return "20%"                                            # demo value

@mcp.tool()                                                 # tool that changes the tool list
async def enable_bulk(ctx: Context) -> str:                 # ctx gives access to the session
    """Register a new tool at runtime and tell clients."""
    @mcp.tool()                                             # registered while server is running
    def bulk_rates(codes: list[str]) -> list[str]:          # new tool
        """Rates for many codes."""
        return ["20%" for _ in codes]                       # demo values
    await ctx.session.send_tool_list_changed()              # notifications/tools/list_changed
    return "bulk enabled"

if __name__ == "__main__":                                  # entry
    mcp.run()                                               # stdio
```

```python
# discover.py - list, paginate, and react to list_changed (ran)
import asyncio, sys                                         # stdlib
from typing import Any                                      # hints
import mcp.types as types                                   # protocol types
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # stdio transport

async def main() -> None:
    changed = asyncio.Event()                               # set when server says list changed
    async def on_message(msg: Any) -> None:                 # receives notifications from server
        if isinstance(msg, types.ServerNotification) and isinstance(msg.root, types.ToolListChangedNotification):
            changed.set()                                   # mark that we must re-list
    params = StdioServerParameters(command=sys.executable, args=["dyn_server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w, message_handler=on_message) as s:   # handler passed here
            init = await s.initialize()                     # handshake
            print("caps.tools:", init.capabilities.tools)    # observed: listChanged=False (still notified)
            page = await s.list_tools()                     # first page
            print([t.name for t in page.tools], "next:", page.nextCursor)   # next: None (one page)
            await s.call_tool("enable_bulk", {})            # server adds a tool
            await asyncio.wait_for(changed.wait(), 5)       # wait for the notification (timeout = safety)
            print("relist:", [t.name for t in (await s.list_tools()).tools])   # now includes bulk_rates

asyncio.run(main())                                         # run
```

## 💻 Code Example — Advanced
```python
# tool_registry_api.py - cached discovery with list_changed invalidation, served by FastAPI (ran via TestClient)
import asyncio, sys, time                                   # stdlib
from contextlib import AsyncExitStack, asynccontextmanager  # lifespan helper
from typing import Any, AsyncIterator                       # hints
import mcp.types as types                                   # protocol types
from fastapi import FastAPI, HTTPException                  # web layer
from mcp import ClientSession, StdioServerParameters        # client
from mcp.client.stdio import stdio_client                   # transport
from pydantic import BaseModel                              # response model

class ToolInfo(BaseModel):                                  # what we expose to callers
    name: str
    description: str
    required_args: list[str]

class Registry:                                             # discovery cache for one MCP session
    def __init__(self, session: ClientSession, ttl: float = 300.0) -> None:
        self.session, self.ttl = session, ttl               # session + max cache age (seconds)
        self.tools: list[types.Tool] = []                   # cached tool list
        self.fetched_at: float = 0.0                        # when we last fetched
        self.dirty = True                                   # set by list_changed notification
        self.lock = asyncio.Lock()                          # avoid thundering-herd refetch

    async def get(self) -> list[types.Tool]:                # cached read
        async with self.lock:
            if self.dirty or time.monotonic() - self.fetched_at > self.ttl:
                tools: list[types.Tool] = []
                cursor: str | None = None
                while True:                                 # follow pagination cursors
                    page = await self.session.list_tools(cursor=cursor)
                    tools.extend(page.tools)
                    cursor = page.nextCursor
                    if not cursor:
                        break
                self.tools, self.fetched_at, self.dirty = tools, time.monotonic(), False
            return self.tools

registry: Registry | None = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global registry
    async def on_message(msg: Any) -> None:                 # handles server notifications
        if isinstance(msg, types.ServerNotification) and isinstance(msg.root, types.ToolListChangedNotification):
            if registry:
                registry.dirty = True                       # next get() refetches
    async with AsyncExitStack() as stack:
        params = StdioServerParameters(command=sys.executable, args=["dyn_server.py"])
        r, w = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(r, w, message_handler=on_message))
        await session.initialize()
        registry = Registry(session)
        app.state.session = session
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/tools", response_model=list[ToolInfo])
async def tools(prefix: str = "") -> list[ToolInfo]:        # optional name filter
    if registry is None:
        raise HTTPException(503, "registry not ready")
    try:
        found = await registry.get()
    except Exception as exc:                                # server crashed / timeout
        raise HTTPException(502, f"discovery failed: {type(exc).__name__}") from exc
    return [ToolInfo(name=t.name, description=t.description or "",
                     required_args=list(t.inputSchema.get("required", [])))
            for t in found if t.name.startswith(prefix)]

@app.post("/call/{name}")
async def call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    res = await app.state.session.call_tool(name, args)
    return {"is_error": res.isError, "text": res.content[0].text if res.content else ""}
```
Test run output: first `/tools` -> `['get_tariff_rate', 'enable_bulk']`; after calling `enable_bulk` -> `['get_tariff_rate', 'enable_bulk', 'bulk_rates']`; `/tools?prefix=bulk` returned only `bulk_rates` with `required_args ['codes']`. Token usage: discovery itself costs no LLM tokens; the tools you pass to the model do (name + description + schema, every turn). Async: all calls awaited. Other SDKs: OpenAI Agents SDK has `cache_tools_list` and `invalidate_tools_cache()` (names verified); see note 018.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Discovery call | `get_tools()` / `load_mcp_tools` | verify docs | `list_tools()` per run | workbench lists tools (verify) |
| Cache | your code | verify | `cache_tools_list` flag | verify |
| list_changed | handle via `ClientSession` handler (not automatic) | verify | `invalidate_tools_cache()` manual; `message_handler` param exists | verify |
| Filtering | filter list before `bind_tools` | verify | `tool_filter` (static or callable) | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Calling `tools/list` on every user message.
✅ Correct: Cache with TTL and invalidate on `list_changed`.

❌ Mistake 2: Ignoring `nextCursor`.
✅ Correct: Loop until the cursor is empty; otherwise large servers appear to have fewer tools.

❌ Mistake 3: Giving the model all 80 tools.
✅ Correct: Filter by task/tenant; fewer, well-described tools improve selection and cut tokens.

❌ Mistake 4: Trusting the `listChanged` capability flag only.
✅ Correct: Install a `message_handler` anyway and also keep a TTL.

---

## 🧠 Tricky Interview Question
"A conversation is in progress; the server removes `calc_duty`. The model calls it next turn. What do you do?"

Answer: The call returns an error result (an unknown-tool error: the SDK reported `isError=True` with text "Unknown tool: calc_duty" in our run of a missing tool). Do not crash: feed the error to the model, refresh the tool list, and either re-bind updated tools or fail gracefully. For stability pin a tool-list version per conversation (snapshot) and apply updates only to new conversations.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `tools/list` return?
A1: For each tool: `name`, `description`, `inputSchema` (JSON Schema), optionally `annotations`/`outputSchema`, plus `nextCursor` if more pages exist.

Q2: [Medium] How does a client learn the list changed?
A2: Server sends `notifications/tools/list_changed`; the client handles it in its message handler and re-lists.

Q3: [Hard] Why can discovery hurt agent quality?
A3: Large lists confuse tool selection and consume context. Use filtering, namespacing, concise descriptions, or a retrieval step that selects relevant tools per query.

Q4: [Hard] Stdio client missed the notification. Consequence?
A4: Stale cache -> calls to missing tools or no access to new ones. Mitigate with TTL and refresh-on-error.

Q5: [System Design] Tool catalogue for 100 servers.
A5: A gateway/registry that aggregates and namespaces tools, caches per server with TTL + list_changed, applies per-tenant allow-lists, and exposes a search endpoint so the agent loads only the top-k relevant tools.

---

## 💰 Cost Impact
Discovery is cheap (no LLM). The cost is what you pass on: each tool adds roughly its name, description and schema to every model call (typically tens to a few hundred tokens each - measure with your own tokenizer). 50 tools x 150 tokens x 6 turns = 45k input tokens per conversation (illustrative arithmetic, not a measurement). Filter and cache.

---

## 🔷 When to Use
✅ Use dynamic discovery when:
- Tools change often or differ per tenant

❌ Avoid when:
- A fixed small tool set is better pinned in code for reproducibility

---

## 📊 Visual Diagram
```
 Client                                   Server
   | -- initialize ----------------------> |
   | <- capabilities ---------------------- |
   | -- tools/list (cursor) --------------> |
   | <- tools[], nextCursor --------------- |
   |   ... cache + filter -> model ...      |
   | <- notifications/tools/list_changed -- |
   | -- tools/list ------------------------> |   (refresh)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tools/list | Request to list tools | tools की सूची माँगना |
| nextCursor | Pagination token | अगले पन्ने का token |
| list_changed | Notification that list changed | list बदलने की सूचना |
| inputSchema | JSON Schema of arguments | arguments का schema |
| TTL | Cache time-to-live | cache की उम्र |

---

## ⚡ 3-Line Summary
English: Clients discover tools with `tools/list`, following cursors. Cache the result and refresh on `list_changed` or TTL. Filter before giving tools to the model.
Hindi: Client `tools/list` से tools खोजता है और cursors follow करता है। Result cache करें और `list_changed` या TTL पर refresh करें। Model को देने से पहले filter करें।

---

## ➡️ Next Topic
**020. MCP Authentication** - who is allowed to discover and call these tools (bearer tokens, OAuth resource server).

---
