---

# 281. StructuredTool
# हिंदी में: StructuredTool

---

## 🔵 Simple Definition (English)
`StructuredTool` is LangChain's tool class for functions with multiple typed inputs. You build it with `StructuredTool.from_function(func=..., coroutine=..., name=..., description=..., args_schema=...)`. It is what `@tool` creates under the hood, but the explicit form lets you attach both a sync and an async function and set everything by hand.

## 🔵 सरल परिभाषा (Hindi)
`StructuredTool` LangChain की वह class है जो कई typed inputs वाले functions के लिए बनी है। `StructuredTool.from_function(...)` से बनाते हैं। `@tool` अंदर यही बनाता है, पर explicit रूप में आप sync और async दोनों functions जोड़ सकते हैं और सब कुछ खुद set कर सकते हैं।

---

## 🔴 Problem it Solves
Old-style tools accepted only one string input, so multi-argument tools needed ugly parsing ("8517,IN"). StructuredTool accepts a validated dict of arguments. It also solves "I have an existing function from another library and cannot decorate it".

## 🔴 यह क्यों बना? (Hindi)
पुराने tools सिर्फ़ एक string input लेते थे, इसलिए multi-argument के लिए "8517,IN" जैसी parsing करनी पड़ती थी। StructuredTool validated dict लेता है। साथ ही, जिस function को decorate नहीं कर सकते (दूसरी library का), उसे भी tool बना सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write (or import) a function: def calc(hs_code, value, country)
Step 2 → Define args_schema (Pydantic BaseModel) with Field descriptions
Step 3 → StructuredTool.from_function(func, coroutine, name, description, args_schema)
Step 4 → LLM sees name + description + JSON schema from args_schema
Step 5 → LLM emits tool_call args dict -> validated by Pydantic
Step 6 → .invoke() runs func; .ainvoke() runs coroutine (or func in a thread)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Function लिखो (या import करो): def calc(hs_code, value, country)
Step 2 → Pydantic BaseModel से args_schema बनाओ, Field descriptions के साथ
Step 3 → StructuredTool.from_function(func, coroutine, name, description, args_schema)
Step 4 → LLM को name + description + JSON schema दिखता है
Step 5 → LLM tool_call args देता है -> Pydantic validate करता है
Step 6 → .invoke() func चलाता है; .ainvoke() coroutine चलाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `calculate_landed_cost(hs_code, cif_value, country, currency)` needs four inputs. As a StructuredTool, the LLM fills all four fields; Pydantic ensures `cif_value > 0`. Your finance team's existing `calculate_landed_cost` function from an internal library is wrapped without editing it.

**Amazon AI**: `create_return(order_id, item_id, reason)`.

## 🟡 Real Example Hindi mein
**Tariff System**: `calculate_landed_cost(hs_code, cif_value, country, currency)` में चार inputs हैं। StructuredTool में LLM चारों fields भरता है; Pydantic पक्का करता है कि `cif_value > 0`। Finance team का पहले से बना function बिना बदले wrap हो जाता है।

**Amazon AI**: `create_return(order_id, item_id, reason)`।

---

## 💻 Code Example — Basic
```python
# Basic: build a StructuredTool by hand (offline, pip install langchain-core pydantic)
from pydantic import BaseModel, Field                 # schema definition
from langchain_core.tools import StructuredTool       # the class

class LandedCostInput(BaseModel):
    hs_code: str = Field(description="HS code such as 8517")       # field 1
    cif_value: float = Field(gt=0, description="CIF value in USD") # must be positive
    duty_percent: float = Field(ge=0, le=100, description="Duty percent")

def landed_cost(hs_code: str, cif_value: float, duty_percent: float) -> float:
    """Compute cost after duty."""
    return round(cif_value * (1 + duty_percent / 100), 2)   # simple formula

tool = StructuredTool.from_function(                  # explicit construction
    func=landed_cost,                                  # the callable
    name="landed_cost",                                # name shown to LLM
    description="Compute landed cost = CIF + duty. Use after finding duty percent.",
    args_schema=LandedCostInput,                       # validation + schema
)

print(tool.args)                                       # schema of arguments
print(tool.invoke({"hs_code": "8517", "cif_value": 100, "duty_percent": 20}))   # 120.0
try:
    tool.invoke({"hs_code": "8517", "cif_value": -5, "duty_percent": 20})       # invalid
except Exception as exc:                               # Pydantic ValidationError
    print("rejected:", type(exc).__name__)
```

## 💻 Code Example — Advanced
```python
# Production: sync + async functions, error handling, structured output, timeouts
import asyncio                                          # async runtime
import logging                                          # logs
from typing import Any                                  # typing
from pydantic import BaseModel, Field                   # pydantic v2
from langchain_core.tools import StructuredTool, ToolException

logger = logging.getLogger("structured_tool")           # logger

class CostInput(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4,10}$", description="4-10 digit HS code")  # regex check
    cif_value: float = Field(gt=0, description="CIF value in USD")
    country: str = Field(default="IN", min_length=2, max_length=2)

def _rate_for(hs_code: str) -> float:
    """Pretend DB read (sync, blocking)."""
    if hs_code.startswith("0"):
        raise LookupError("rate not found")
    return 20.0

def cost_sync(hs_code: str, cif_value: float, country: str = "IN") -> dict[str, Any]:
    """Sync implementation."""
    try:
        rate = _rate_for(hs_code)                       # may raise LookupError
    except LookupError as exc:
        raise ToolException(str(exc)) from exc          # expected failure
    return {"country": country, "rate": rate, "total": round(cif_value * (1 + rate / 100), 2)}

async def cost_async(hs_code: str, cif_value: float, country: str = "IN") -> dict[str, Any]:
    """Async implementation: run blocking code in a thread, with timeout."""
    try:
        return await asyncio.wait_for(                  # guard slow dependencies
            asyncio.to_thread(cost_sync, hs_code, cif_value, country), timeout=5)
    except asyncio.TimeoutError as exc:
        raise ToolException("lookup timed out") from exc

cost_tool = StructuredTool.from_function(
    func=cost_sync,                                     # used by .invoke
    coroutine=cost_async,                               # used by .ainvoke
    name="landed_cost",
    description="Landed cost for an HS code and CIF value.",
    args_schema=CostInput,
    handle_tool_error=True,                             # ToolException -> text for LLM
)

async def main() -> None:
    print(await cost_tool.ainvoke({"hs_code": "8517", "cif_value": 100}))   # works
    print(await cost_tool.ainvoke({"hs_code": "0101", "cif_value": 100}))   # error text

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# Serve the same tool object over HTTP (handy for testing and non-LLM clients)
from fastapi import FastAPI                             # framework

app = FastAPI()

@app.post("/tools/landed-cost")
async def landed(body: CostInput) -> dict:              # FastAPI validates with same schema
    result = await cost_tool.ainvoke(body.model_dump()) # reuse tool logic
    return {"result": result}
```

---

## 🔗 LangChain / LangGraph Connection
Any `StructuredTool` can go into `bind_tools`, `create_react_agent` or `ToolNode`. You can also turn a Runnable/chain into a tool with `runnable.as_tool(...)`.

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools([cost_tool])   # tool visible to model
ai = llm.invoke("Landed cost for HS 8517 CIF 100 USD?")
print(ai.tool_calls)                                            # model's request
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Giving only `func` for async servers, so each call blocks the event loop
✅ Correct: Provide `coroutine` (or use `asyncio.to_thread` inside).

```python
# Wrong
StructuredTool.from_function(func=slow_blocking_fn, name="x", description="y")
# Right
StructuredTool.from_function(func=slow_blocking_fn, coroutine=async_version, name="x", description="y")
```

❌ Mistake 2: Description missing, so `from_function` falls back to docstring that may be empty and raises
✅ Correct: Always pass `description=`.

```python
# Wrong
StructuredTool.from_function(func=lambda a: a)   # no description -> ValueError
# Right
StructuredTool.from_function(func=lambda a: a, name="echo", description="Echo a string", args_schema=EchoIn)
```

---

## 🧠 Tricky Interview Question
**Q**: "`@tool` and `StructuredTool.from_function` both exist. Why would a senior engineer pick the second?"

**Answer**: `@tool` is sugar for the common case. `from_function` is needed when (1) you wrap a function you cannot decorate (third-party or shared library), (2) you want to register BOTH a sync `func` and an async `coroutine`, (3) you build tools dynamically at runtime (for example one tool per customer config), and (4) you want explicit control over name, description and schema independent of the function's docstring. Behaviour is the same afterwards because both create StructuredTool objects.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between StructuredTool and the old `Tool` class?
A1: `Tool` takes a single string input; `StructuredTool` takes multiple typed arguments described by a Pydantic schema.

Q2: What does `args_schema` do?
A2: It validates inputs and generates the JSON schema shown to the LLM, including descriptions and constraints.

Q3: What happens when you call `.ainvoke` on a tool defined with only `func`?
A3: LangChain runs the sync function in an executor thread, so it works but uses thread-pool resources. A native `coroutine` is better for I/O.

Q4: How do you handle tool failures without crashing the agent?
A4: Raise `ToolException` and set `handle_tool_error=True` (or provide a handler). The text goes back to the model as the tool message.

Q5: (Hard) How do you create tools dynamically per tenant while keeping unique, safe names?
A5: Use a factory function that builds a closure with the tenant config and calls `StructuredTool.from_function(name=f"search_{tenant_slug}")`. Sanitize names to `[a-zA-Z0-9_-]`, cap tool count, cache built tools, and never let the model pass tenant ids itself.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Wrapping existing functions
- Need sync + async pair
- Generating tools dynamically

❌ Avoid when:
- A simple `@tool` is enough
- You need full lifecycle control (subclass `BaseTool`)

---

## 📊 Visual Diagram
```
 func (sync)      coroutine (async)     args_schema (Pydantic)
     \                 |                    /
      +----- StructuredTool.from_function --+
                       |
        name + description + JSON schema --> LLM
                       |
        tool_call args --> validate --> run --> output
```

---

## 💰 Cost Impact
- Field descriptions in `args_schema` are sent to the model: helpful, but each adds tokens.
- Good validation (regex, ranges) prevents wasted retries (each wrong call costs a full extra LLM turn).
- Optimise: concise field descriptions, strict validation, return compact JSON, and use `ToolException` messages that tell the model exactly how to fix its input in one retry.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StructuredTool | Multi-input tool class | कई inputs वाला tool class |
| from_function | Factory method | Function से tool बनाने की method |
| coroutine | Async function for tool | Async function |
| args_schema | Input schema | Input schema |
| BaseTool | Parent class for custom tools | Custom tools की parent class |
| ToolException | Recoverable error | सुधारने योग्य error |

---

## ⚡ 3-Line Summary
English: StructuredTool wraps any function with validated multi-argument input. Use from_function to add both sync and async versions and explicit schema. Validation and compact schemas reduce wasted retries and tokens.
Hindi: StructuredTool किसी भी function को validated multi-argument input के साथ wrap करता है। from_function से sync + async दोनों और explicit schema जोड़ सकते हैं। Validation और छोटे schemas से बेकार retries और tokens बचते हैं।

---

## ➡️ Next Topic
**282. Custom Tools** — subclassing BaseTool for stateful, production-grade tools.
