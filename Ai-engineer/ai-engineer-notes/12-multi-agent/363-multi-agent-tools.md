---

# 363. Multi-Agent Tools
# हिंदी में: Multi-Agent Tools

---

## 🔵 Simple Definition (English)
In a multi-agent system, **tools** are functions (search, database, calculator, APIs) that agents can call. The key design question is **which agent gets which tools**: give each agent a small, role-specific toolset with clear descriptions, permission checks and timeouts, instead of giving every agent every tool.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent system में **tools** वे functions हैं (search, database, calculator, APIs) जिन्हें agents बुला सकते हैं। मुख्य design सवाल है कि **किस agent को कौन से tools मिलें**: हर agent को उसकी role के हिसाब से छोटा toolset दो, साफ़ descriptions, permission checks और timeouts के साथ, हर agent को हर tool नहीं।

---

## 🔴 Problem it Solves
If every agent has 30 tools, the model gets confused about which to use, tool descriptions eat thousands of tokens, risky tools (delete, payment) become reachable by the wrong agent, and failures are hard to trace. A tool design with scoping, validation and a registry makes agents reliable and safe.

## 🔴 यह क्यों बना? (Hindi)
हर agent के पास 30 tools हों तो model उलझ जाता है कि कौन सा चुने, tool descriptions हज़ारों tokens खा जाते हैं, जोखिम वाले tools (delete, payment) गलत agent की पहुँच में आ जाते हैं और गड़बड़ी का पता लगाना कठिन होता है। Scoping, validation और registry वाला tool design agents को भरोसेमंद और सुरक्षित बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write tools as typed functions with clear docstrings
Step 2 → Register all tools in one registry with metadata (risk, owner)
Step 3 → Define a permission map: agent -> allowed tool names
Step 4 → At agent creation, bind only its allowed tools
Step 5 → LLM emits a tool call (name + JSON arguments)
Step 6 → Runtime validates args (pydantic), checks permission, applies timeout
Step 7 → Tool result (short, structured) returns to the agent
Step 8 → Log every call: agent, tool, args, latency, cost; retry only if idempotent
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tools को typed functions के रूप में साफ़ docstrings के साथ लिखो
Step 2 → सभी tools को metadata (risk, owner) के साथ एक registry में रखो
Step 3 → Permission map बनाओ: agent -> अनुमत tool नाम
Step 4 → Agent बनाते समय सिर्फ उसके अनुमत tools जोड़ो
Step 5 → LLM tool call देता है (नाम + JSON arguments)
Step 6 → Runtime args validate करता है (pydantic), permission जाँचता है, timeout लगाता है
Step 7 → Tool का छोटा, structured result agent को लौटता है
Step 8 → हर call log करो: agent, tool, args, latency, cost; retry सिर्फ idempotent पर
```

---

## 🟡 Real World Example
**Tariff Classification System**: `Classifier` gets `search_tariff` and `get_chapter_notes`. `DutyAgent` gets `get_duty_rate` and `calculator`. `Filing` agent gets `submit_declaration`, a high-risk write tool that also requires human approval. If the Classifier tried `submit_declaration`, the registry would deny it.

**Zomato-style**: `Menu` agent can read menus; only `Payment` agent can call `charge_card`.

## 🟡 Real Example Hindi mein
**Tariff System**: `Classifier` को `search_tariff` और `get_chapter_notes` मिलते हैं। `DutyAgent` को `get_duty_rate` और `calculator`। `Filing` agent को `submit_declaration` मिलता है, जो जोखिम वाला write tool है और human approval भी माँगता है। Classifier `submit_declaration` बुलाने की कोशिश करे तो registry मना कर देती है।

**Zomato-style**: `Menu` agent सिर्फ menus पढ़ सकता है; सिर्फ `Payment` agent `charge_card` बुला सकता है।

---

## 💻 Code Example — Basic
```python
# Tool registry with per-agent permissions and validation (runs offline)
from typing import Any, Callable  # type hints

TOOLS: dict[str, Callable[..., Any]] = {}  # name -> function
RISK: dict[str, str] = {}                  # name -> "read" | "write"

def register(name: str, risk: str = "read") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        TOOLS[name] = fn   # add to registry
        RISK[name] = risk  # remember risk level
        return fn
    return deco

@register("get_duty_rate")
def get_duty_rate(hs_code: str) -> float:
    return {"8518.30": 0.20}.get(hs_code, 0.10)  # fake lookup

@register("submit_declaration", risk="write")
def submit_declaration(hs_code: str) -> str:
    return f"submitted {hs_code}"  # pretend side effect

PERMISSIONS: dict[str, set[str]] = {
    "duty_agent": {"get_duty_rate"},
    "filing_agent": {"get_duty_rate", "submit_declaration"},
}

def call_tool(agent: str, name: str, **kwargs: Any) -> Any:
    if name not in TOOLS:
        raise KeyError(f"unknown tool {name}")                 # tool must exist
    if name not in PERMISSIONS.get(agent, set()):
        raise PermissionError(f"{agent} may not call {name}")  # least privilege
    return TOOLS[name](**kwargs)                                # run

if __name__ == "__main__":
    print(call_tool("duty_agent", "get_duty_rate", hs_code="8518.30"))  # 0.2
    try:
        call_tool("duty_agent", "submit_declaration", hs_code="8518.30")
    except PermissionError as exc:
        print("blocked:", exc)  # expected
```

## 💻 Code Example — Advanced
```python
# Async tool runner: pydantic validation, timeout, retry for read tools, logging
import asyncio  # async runtime
import time  # latency
from typing import Any, Awaitable, Callable  # types
from pydantic import BaseModel, ValidationError  # pydantic v2

class DutyArgs(BaseModel):
    hs_code: str  # must be a string

async def duty_tool(args: DutyArgs) -> dict[str, Any]:
    await asyncio.sleep(0)  # fake I/O
    return {"hs_code": args.hs_code, "rate": 0.20}

SPEC: dict[str, tuple[type[BaseModel], Callable[[Any], Awaitable[dict[str, Any]]], bool]] = {
    "get_duty_rate": (DutyArgs, duty_tool, True),  # (schema, function, idempotent)
}
LOG: list[dict[str, Any]] = []  # audit log

async def run_tool(agent: str, name: str, raw_args: dict[str, Any], timeout: float = 5.0) -> dict[str, Any]:
    schema, fn, idempotent = SPEC[name]
    try:
        args = schema(**raw_args)  # validate model-produced JSON
    except ValidationError as exc:
        return {"error": "invalid_args", "detail": exc.errors()[0]["msg"]}  # let the agent fix it
    attempts = 3 if idempotent else 1  # never auto-retry writes
    start = time.perf_counter()
    for i in range(attempts):
        try:
            res = await asyncio.wait_for(fn(args), timeout)  # timeout guard
            LOG.append({"agent": agent, "tool": name, "ms": (time.perf_counter() - start) * 1000, "ok": True})
            return res
        except asyncio.TimeoutError:
            await asyncio.sleep(0.05 * 2 ** i)  # backoff
        except Exception as exc:
            LOG.append({"agent": agent, "tool": name, "ok": False, "err": str(exc)})
            return {"error": "tool_failed", "detail": str(exc)}
    return {"error": "timeout"}

if __name__ == "__main__":
    print(asyncio.run(run_tool("duty_agent", "get_duty_rate", {"hs_code": "8518.30"})))
    print(asyncio.run(run_tool("duty_agent", "get_duty_rate", {"wrong": 1})))  # invalid args
```

---

## 🟠 FastAPI Integration
Expose a tool-gateway endpoint so every tool call from any agent passes through one place for auth, rate limits and audit.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()

class ToolCall(BaseModel):
    agent: str             # calling agent
    tool: str              # tool name
    args: dict             # tool arguments

@app.post("/tools/call")
async def tool_gateway(call: ToolCall) -> dict:
    if call.tool not in SPEC:
        raise HTTPException(404, "unknown tool")
    allowed = {"duty_agent": {"get_duty_rate"}}.get(call.agent, set())  # permission map
    if call.tool not in allowed:
        raise HTTPException(403, "not permitted")  # least privilege
    return await run_tool(call.agent, call.tool, call.args)
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool  # decorator that creates a tool with a schema from type hints
from langchain_openai import ChatOpenAI  # llm
from langgraph.prebuilt import create_react_agent  # prebuilt tool-calling agent

@tool
def get_duty_rate(hs_code: str) -> float:
    """Return the basic customs duty rate for an HS code."""  # docstring is the tool description
    return {"8518.30": 0.20}.get(hs_code, 0.10)

@tool
def search_tariff(query: str) -> str:
    """Search tariff headings by product text."""
    return "8518.30 headphones"

llm = ChatOpenAI(model="gpt-4o-mini")

# Each agent gets only its own tools (least privilege):
classifier = create_react_agent(llm, tools=[search_tariff], prompt="You classify products.")
duty_agent = create_react_agent(llm, tools=[get_duty_rate], prompt="You compute duty.")
# A supervisor graph then routes between classifier and duty_agent.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Giving all tools to all agents
✅ Correct: minimal toolset per role.

```python
# Wrong
agent = create_react_agent(llm, tools=ALL_TOOLS)
# Right
agent = create_react_agent(llm, tools=[search_tariff])
```

❌ Mistake 2: Returning huge raw outputs and trusting arguments blindly
✅ Correct: validate inputs, return compact results.

```python
# Wrong
def search(q): return db.query(q)   # 5 MB of JSON back into the prompt
# Right
def search(q: str) -> list[dict]: return db.query(q)[:5]   # top 5, only needed fields
```

---

## 🧠 Tricky Interview Question
**Q**: "The model calls `submit_declaration` twice because of a retry, and a duplicate filing is created. How do you prevent this?"

**Answer**: Write tools must be idempotent. Require an `idempotency_key` (for example hash of shipment id and version) that the backend de-duplicates, avoid automatic retries on writes, require human approval for high-risk tools, and record every attempt in an audit log. Retrying reads is fine; retrying writes without an idempotency key is a bug.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a tool in an agent system?
A1: A function with a name, description and argument schema that the LLM can ask the runtime to run.

Q2: [Easy] Why should tool descriptions be clear?
A2: The model chooses tools by reading the descriptions and schemas. Vague text causes wrong or missed calls.

Q3: [Medium] What is least privilege for tools?
A3: Each agent gets only the tools its role needs, and risky tools need extra checks like approval.

Q4: [Medium] How do you handle tool errors?
A4: Return structured error messages to the agent so it can retry or adapt, set timeouts, retry only idempotent reads, and cap total tool calls.

Q5: [Hard] How do you scale to 100 tools?
A5: Group tools by domain, route to specialist agents, use retrieval over tool descriptions to select a few tools per request, keep schemas compact, and measure tool-selection accuracy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Agents need fresh data or actions beyond the model's knowledge
- Deterministic computation (math, lookups) is required

❌ Avoid when:
- A prompt alone answers the question
- A tool would expose risky actions without controls

---

## 📊 Visual Diagram
```
 Agent ---(tool call: name + JSON)---> [Tool Gateway]
                                          | 1. schema validate
                                          | 2. permission check
                                          | 3. timeout / retry (reads)
                                          | 4. audit log
                                          v
                        +---------+----------+-----------------+
                        |search   |get_duty  | submit (write,  |
                        |_tariff  |_rate     | needs approval) |
                        +---------+----------+-----------------+
 Result (short JSON) ---------------------------------> back to Agent
```

---

## 💰 Cost Impact
- Tool schemas are sent on every call: 10 tools can add 1,000-2,000 input tokens each call.
- Each tool round trip is another LLM call carrying the result.
- Optimise: fewer tools per agent, short descriptions, compact outputs (top-k, selected fields), deterministic tools instead of LLM reasoning, cache read results, limit max tool calls per run.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool | Function an agent can call | Agent द्वारा बुलाया जाने वाला function |
| Tool registry | Central list of tools | Tools की केंद्रीय सूची |
| Least privilege | Minimum needed access | न्यूनतम ज़रूरी पहुँच |
| Idempotent | Repeat gives same effect | दोहराने पर वही असर |
| Idempotency key | Id to de-duplicate writes | Writes दोहराव रोकने की पहचान |
| Tool gateway | Single controlled entry for calls | Tool calls का एकल नियंत्रित द्वार |

---

## ⚡ 3-Line Summary
English: Give each agent a small, role-specific toolset through a registry with permissions. Validate arguments, add timeouts, and make writes idempotent with approval. Keep tool outputs small to save tokens.
Hindi: Registry और permissions के ज़रिए हर agent को छोटा, role-आधारित toolset दो। Arguments validate करो, timeouts लगाओ और writes को idempotent व approval के साथ रखो। Tokens बचाने के लिए tool outputs छोटे रखो।

---

## ➡️ Next Topic
**364. Multi-Agent Evaluation** — measuring whether a team of agents actually works.
