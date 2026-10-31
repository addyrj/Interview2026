---

# 282. Custom Tools
# हिंदी में: Custom Tools

---

## 🔵 Simple Definition (English)
A custom tool is a tool you design for your own business logic, usually by subclassing `BaseTool`. It holds its own state (DB connection, API client, user context), has a clear name, description and `args_schema`, and implements `_run` (sync) and `_arun` (async). Use it when `@tool` is too small for the job.

## 🔵 सरल परिभाषा (Hindi)
Custom tool वह tool है जो आप अपनी business logic के लिए खुद डिज़ाइन करते हैं, आमतौर पर `BaseTool` को subclass करके। इसमें अपनी state (DB connection, API client, user context) रहती है, साफ़ name, description और `args_schema` होता है, और `_run` (sync) व `_arun` (async) लिखे जाते हैं। जब `@tool` छोटा पड़े तब इस्तेमाल करें।

---

## 🔴 Problem it Solves
Real tools need more than a function: shared DB pool, auth, caching, retries, metrics, per-tenant config. Putting these in globals gets messy and untestable. A class gives dependency injection and a single place for cross-cutting concerns.

## 🔴 यह क्यों बना? (Hindi)
असली tools को function से ज़्यादा चाहिए: shared DB pool, auth, caching, retries, metrics, per-tenant config। इन्हें globals में रखना messy और untestable है। Class से dependency injection मिलता है और cross-cutting काम एक जगह रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define args_schema (Pydantic) for inputs
Step 2 → Subclass BaseTool; set name, description, args_schema
Step 3 → Add fields for dependencies (repo, client) as Pydantic fields
Step 4 → Implement _run (sync) and _arun (async) with error handling
Step 5 → Instantiate with real dependencies (or fakes for tests)
Step 6 → Give to agent/bind_tools; the LLM sees name + description + schema
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Inputs के लिए args_schema (Pydantic) बनाओ
Step 2 → BaseTool subclass करो; name, description, args_schema set करो
Step 3 → Dependencies (repo, client) को fields की तरह जोड़ो
Step 4 → error handling के साथ _run और _arun लिखो
Step 5 → असली dependencies (या tests के लिए fakes) से instance बनाओ
Step 6 → agent/bind_tools को दो; LLM को name + description + schema दिखता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `HSCodeSearchTool` holds a vector-store retriever and a Redis cache. `_arun` checks cache, then searches embeddings, returns the top 3 codes with confidence. In tests, you inject a fake retriever. The same class is used by the agent and the batch classification job.

**Zomato AI**: `OrderStatusTool` holds the order-service client and the current user's id.

## 🟡 Real Example Hindi mein
**Tariff System**: `HSCodeSearchTool` में vector-store retriever और Redis cache रहता है। `_arun` पहले cache देखता है, फिर embeddings में search करके top 3 codes confidence के साथ लौटाता है। Tests में fake retriever inject होता है। वही class agent और batch job दोनों में चलती है।

**Zomato AI**: `OrderStatusTool` में order-service client और current user की id रहती है।

---

## 💻 Code Example — Basic
```python
# Basic: custom BaseTool with injected dependency (offline)
from typing import Type                                 # for class attribute typing
from pydantic import BaseModel, Field                   # schema
from langchain_core.tools import BaseTool               # base class

class SearchInput(BaseModel):
    query: str = Field(description="Product description, e.g. 'wireless earbuds'")

class HSSearchTool(BaseTool):
    name: str = "hs_search"                              # tool name for LLM
    description: str = "Search HS codes by product description."   # when to use
    args_schema: Type[BaseModel] = SearchInput           # input schema
    catalog: dict[str, str] = {}                         # injected dependency (pydantic field)

    def _run(self, query: str) -> str:
        """Sync implementation."""
        hits = [f"{code}: {desc}" for code, desc in self.catalog.items()
                if query.lower() in desc.lower()]        # naive substring search
        return "\n".join(hits) if hits else "no match"   # always return a string

tool = HSSearchTool(catalog={"851830": "Headphones and earphones", "640399": "Footwear, leather"})
print(tool.invoke({"query": "earphones"}))               # 851830: Headphones and earphones
print(tool.invoke({"query": "spaceship"}))               # no match
print(tool.name, "|", tool.args)                         # metadata the LLM sees
```

## 💻 Code Example — Advanced
```python
# Production: BaseTool with cache, timeout, async, error handling, metrics
import asyncio                                           # async runtime
import logging                                           # logs
import time                                              # timing
from typing import Any, Optional, Type                   # typing
from pydantic import BaseModel, Field                    # pydantic v2
from langchain_core.tools import BaseTool, ToolException # base + error

logger = logging.getLogger("hs_tool")                    # logger

class SearchInput(BaseModel):
    query: str = Field(min_length=3, max_length=200, description="Product description")
    top_k: int = Field(default=3, ge=1, le=10, description="How many results")

class HSSearchTool(BaseTool):
    name: str = "hs_search"
    description: str = ("Search HS codes by product description. "
                        "Returns code, description and score. Use BEFORE duty lookup.")
    args_schema: Type[BaseModel] = SearchInput
    handle_tool_error: bool = True                       # ToolException -> text for model
    retriever: Any = None                                # async callable (query, k) -> list[dict]
    cache: dict[str, list[dict]] = Field(default_factory=dict)   # simple in-memory cache
    timeout_s: float = 8.0                               # per-call timeout

    def _run(self, query: str, top_k: int = 3) -> str:
        """Sync path: run the async path in a fresh loop (fine for scripts/tests)."""
        return asyncio.run(self._arun(query=query, top_k=top_k))

    async def _arun(self, query: str, top_k: int = 3) -> str:
        key = f"{query.lower()}|{top_k}"                 # cache key
        if key in self.cache:                            # cache hit saves latency
            return self._fmt(self.cache[key])
        start = time.perf_counter()
        try:
            results = await asyncio.wait_for(self.retriever(query, top_k), self.timeout_s)
        except asyncio.TimeoutError as exc:
            raise ToolException("search timed out, try a shorter query") from exc
        except Exception as exc:                         # do not leak internals to the model
            logger.exception("retriever failed")
            raise ToolException("search backend error") from exc
        finally:
            logger.info("hs_search took %.1f ms", (time.perf_counter() - start) * 1000)
        self.cache[key] = results                        # store for next time
        return self._fmt(results)

    @staticmethod
    def _fmt(rows: list[dict]) -> str:
        if not rows:
            return "no match"
        return "\n".join(f"{r['code']} | {r['desc']} | {r['score']:.2f}" for r in rows)

async def fake_retriever(query: str, k: int) -> list[dict]:
    await asyncio.sleep(0)                               # pretend vector search
    return [{"code": "851830", "desc": "Headphones", "score": 0.91}][:k]

async def main() -> None:
    tool = HSSearchTool(retriever=fake_retriever)
    print(await tool.ainvoke({"query": "bluetooth earbuds"}))   # computed
    print(await tool.ainvoke({"query": "bluetooth earbuds"}))   # cached

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Create the tool once at startup (lifespan) and reuse it, so cache and connection pools are shared.

```python
from contextlib import asynccontextmanager              # lifespan helper
from fastapi import FastAPI, Request                    # framework

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hs_tool = HSSearchTool(retriever=fake_retriever)   # build once
    yield                                                        # app runs
    # close clients here if the tool owns any

app = FastAPI(lifespan=lifespan)

@app.get("/hs/search")
async def search(q: str, request: Request) -> dict:
    out = await request.app.state.hs_tool.ainvoke({"query": q})  # reuse tool
    return {"result": out}
```

---

## 🔗 LangChain / LangGraph Connection
A `BaseTool` is a Runnable, so it works with `bind_tools`, `ToolNode` and agents. In LangGraph you can also read graph state/config inside a tool using `RunnableConfig`.

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [HSSearchTool(retriever=fake_retriever)])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting type annotations on class fields (Pydantic then rejects or ignores them)
✅ Correct: Annotate `name: str`, `description: str`, `args_schema: Type[BaseModel]`.

```python
# Wrong
class T(BaseTool):
    name = "x"            # no annotation -> error in pydantic v2
# Right
class T(BaseTool):
    name: str = "x"
```

❌ Mistake 2: Raising raw exceptions with stack traces/secrets
✅ Correct: Catch, log internally, raise `ToolException` with a safe, helpful message.

```python
# Wrong
raise RuntimeError(f"DB password {pwd} invalid")
# Right
logger.exception("db error")
raise ToolException("database unavailable, try again later")
```

---

## 🧠 Tricky Interview Question
**Q**: "Your custom tool stores `user_id` as a class field. Under load, user A sometimes sees user B's data. Why, and how to fix it?"

**Answer**: One tool instance is shared by all concurrent requests, so mutable per-request fields leak between users (a race condition). Never store request data on the tool. Pass it per call via `RunnableConfig["configurable"]` or an injected argument hidden from the LLM schema, or build a lightweight tool instance per request. Shared, read-only dependencies (pools, clients) are fine on the instance.

---

## ⚫ Interview Questions + Answers

Q1: What two methods must a BaseTool subclass implement?
A1: `_run` (sync) is required; `_arun` (async) is optional but recommended for I/O.

Q2: Why subclass BaseTool instead of using `@tool`?
A2: To hold state and dependencies, share caches/pools, add lifecycle hooks, and unit-test with fakes.

Q3: What should a tool return?
A3: Usually a string or small JSON-serialisable value. Keep it short because it re-enters the prompt.

Q4: How do you test a custom tool?
A4: Inject a fake dependency, call `invoke`/`ainvoke` with sample args, and assert on output, including error cases and timeouts.

Q5: (Hard) How do you secure a tool that can write to a database when an LLM controls its inputs?
A5: Treat model input as untrusted: strict Pydantic validation, parameterised queries, allow-listed operations, least-privilege DB role, rate limits, idempotency keys, audit logs, and human approval (LangGraph interrupt) for destructive actions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tool needs state, caching or injected clients
- Several agents/jobs share one tool
- You need testability

❌ Avoid when:
- A stateless function with two arguments (use `@tool`)

---

## 📊 Visual Diagram
```
 class HSSearchTool(BaseTool)
 +----------------------------------+
 | name, description, args_schema   |
 | retriever (dependency)           |
 | cache, timeout                   |
 | _run()  /  _arun()               |
 +----------------+-----------------+
                  |
   LLM --tool_call--> validate --> cache? --> retriever --> format --> text
```

---

## 💰 Cost Impact
- Caching inside the tool avoids repeated vector/API calls (infra cost) but does not reduce LLM tokens by itself.
- Compact formatted output (3 lines instead of raw JSON of 50 fields) can save hundreds of input tokens per step.
- Clear error messages let the model fix input in one retry, avoiding extra paid turns.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseTool | Base class for tools | Tools की base class |
| _run / _arun | Sync / async body | Sync / async हिस्सा |
| Dependency injection | Pass collaborators in | ज़रूरी objects बाहर से देना |
| Race condition | Shared mutable state bug | साझा state का bug |
| Lifespan | FastAPI startup/shutdown hook | Startup/shutdown hook |
| Idempotency key | Prevents duplicate writes | दोहराव रोकने की key |

---

## ⚡ 3-Line Summary
English: Custom tools subclass BaseTool to carry dependencies, caching and safe error handling. Never keep per-request data on a shared instance. Compact outputs and good errors reduce token cost.
Hindi: Custom tools BaseTool subclass करके dependencies, caching और सुरक्षित error handling रखते हैं। Shared instance पर per-request data कभी न रखें। छोटे outputs और अच्छे errors से token cost घटती है।

---

## ➡️ Next Topic
**283. Built-in Tools** — ready-made tools from LangChain and from LLM providers.
