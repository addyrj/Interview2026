---

# 280. @tool Decorator
# हिंदी में: @tool Decorator

---

## 🔵 Simple Definition (English)
`@tool` from `langchain_core.tools` turns a normal Python function into a LangChain tool. It uses the function name as the tool name, the docstring as the description, and the type hints as the input schema. Options like `parse_docstring`, `args_schema` and `return_direct` give more control.

## 🔵 सरल परिभाषा (Hindi)
`langchain_core.tools` का `@tool` एक सामान्य Python function को LangChain tool बना देता है। Function का नाम = tool का नाम, docstring = description, type hints = input schema। `parse_docstring`, `args_schema`, `return_direct` जैसे options से और control मिलता है।

---

## 🔴 Problem it Solves
Writing a JSON schema by hand for each function is boring and gets out of sync with the code. With `@tool`, the function itself is the single source of truth: change a type hint and the schema updates.

## 🔴 यह क्यों बना? (Hindi)
हर function का JSON schema हाथ से लिखना उबाऊ है और code से अलग हो जाता है। `@tool` में function ही single source of truth है: type hint बदलो, schema अपने-आप बदल जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python reads the decorated function (name, signature, docstring)
Step 2 → Pydantic builds an args schema from type hints
Step 3 → A StructuredTool object is created (name, description, args_schema, func)
Step 4 → tool.invoke({"arg": value}) validates input against schema
Step 5 → Your function runs; return value becomes tool output
Step 6 → With bind_tools the schema is sent to the LLM as JSON
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Python decorated function पढ़ता है (नाम, signature, docstring)
Step 2 → Pydantic type hints से args schema बनाता है
Step 3 → Tool object बनता है (name, description, args_schema, func)
Step 4 → tool.invoke({"arg": value}) input को schema से validate करता है
Step 5 → आपका function चलता है; return value tool का output बनती है
Step 6 → bind_tools से schema JSON बनकर LLM को जाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `@tool def get_duty_rate(hs_code: str, country: str = "IN") -> float`. The docstring says "Use after you know the HS code." The LLM reads this and calls the tool in the right order. If the docstring is poor ("gets rate"), the model picks wrong tools.

**Zomato AI**: `@tool def restaurant_search(city: str, cuisine: str, max_price: int)`.

## 🟡 Real Example Hindi mein
**Tariff System**: `@tool def get_duty_rate(hs_code: str, country: str = "IN") -> float`। Docstring में लिखा है "HS code पता होने के बाद इस्तेमाल करो।" LLM यह पढ़कर सही क्रम में tool चलाता है। Docstring कमज़ोर हो ("gets rate") तो model गलत tool चुनता है।

**Zomato AI**: `@tool def restaurant_search(city: str, cuisine: str, max_price: int)`।

---

## 💻 Code Example — Basic
```python
# Basic: inspect what @tool builds (runs offline, pip install langchain-core)
from langchain_core.tools import tool           # the decorator

@tool                                           # plain usage: name/description come from function
def get_duty_rate(hs_code: str, country: str = "IN") -> float:
    """Return the basic customs duty percent for an HS code in a country."""
    table: dict[str, float] = {"8517": 20.0}    # fake data
    return table.get(hs_code, -1.0)             # -1.0 = not found

@tool("duty_lookup", return_direct=False)       # custom tool name via first argument
def other(hs_code: str) -> str:
    """Look up duty text for an HS code."""
    return f"duty for {hs_code}"                # simple return

print(get_duty_rate.name)                       # get_duty_rate
print(get_duty_rate.description)                # docstring (includes signature in some versions)
print(get_duty_rate.args)                       # JSON-schema-like dict of args
print(other.name)                               # duty_lookup
print(get_duty_rate.invoke({"hs_code": "8517"}))   # 20.0 (country uses default)

# Validation: wrong type is rejected by the schema
try:
    get_duty_rate.invoke({"hs_code": ["not", "a", "string"]})   # list instead of str
except Exception as exc:                        # pydantic ValidationError
    print("validation failed:", type(exc).__name__)
```

## 💻 Code Example — Advanced
```python
# Production: @tool with Pydantic args_schema, async body, error handling, injected config
import asyncio                                           # async runtime
import logging                                           # logs
from typing import Annotated, Any, Optional              # typing helpers
from pydantic import BaseModel, Field, field_validator   # pydantic v2
from langchain_core.tools import tool, ToolException     # decorator + tool error type

logger = logging.getLogger("tools")                      # logger

class DutyInput(BaseModel):
    """Validated input for the duty tool."""
    hs_code: str = Field(description="HS code, 4 to 10 digits, e.g. 851830")   # shown to the LLM
    country: str = Field(default="IN", description="ISO-2 country code")

    @field_validator("hs_code")                          # reject bad codes BEFORE running tool
    @classmethod
    def digits_only(cls, v: str) -> str:
        v = v.replace(".", "").strip()                   # allow 8518.30 style
        if not v.isdigit() or not 4 <= len(v) <= 10:
            raise ValueError("hs_code must be 4-10 digits")
        return v

@tool(args_schema=DutyInput, handle_tool_error=True)     # ToolException becomes text for the LLM
async def get_duty_rate(hs_code: str, country: str = "IN") -> dict[str, Any]:
    """Get basic customs duty percent. Call AFTER you know the HS code."""
    try:
        await asyncio.sleep(0)                           # pretend DB / HTTP call
        if hs_code.startswith("9"):                      # demo failure branch
            raise ToolException(f"No rate published for {hs_code}")
        return {"hs_code": hs_code, "country": country, "rate_percent": 20.0}
    except ToolException:
        raise                                            # let LangChain format it for the model
    except Exception as exc:                             # unexpected failure -> safe message
        logger.exception("duty lookup failed")
        raise ToolException("internal lookup error") from exc

async def main() -> None:
    print(await get_duty_rate.ainvoke({"hs_code": "8518.30"}))   # normal result
    print(await get_duty_rate.ainvoke({"hs_code": "9999"}))      # error text instead of crash

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Tools are plain callables, so you can expose them directly for testing and reuse the same Pydantic model as the API schema.

```python
from fastapi import FastAPI, HTTPException         # framework

app = FastAPI()

@app.post("/tools/duty")
async def duty(payload: DutyInput) -> dict:        # same schema validates API and LLM input
    try:
        return await get_duty_rate.ainvoke(payload.model_dump())   # call the tool
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

---

## 🔗 LangChain / LangGraph Connection
`@tool` objects plug into `bind_tools`, `create_react_agent` and `ToolNode`. Agents read `name`, `description`, `args_schema`.

```python
from langgraph.prebuilt import create_react_agent, ToolNode   # prebuilt pieces
from langchain_openai import ChatOpenAI

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [get_duty_rate])  # tool in agent
node = ToolNode([get_duty_rate])                                # tool executor node for custom graphs
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No docstring (the decorator raises an error or the model has no guidance)
✅ Correct: Always write a clear docstring saying what, when and inputs.

```python
# Wrong
@tool
def f(x: str) -> str:
    return x
# Right
@tool
def get_rate(hs_code: str) -> str:
    """Return duty percent for an HS code. Use after classification."""
    return "20"
```

❌ Mistake 2: Missing type hints, so the schema becomes loose
✅ Correct: Type every parameter; use `Literal` / Pydantic for constraints.

```python
# Wrong
@tool
def pick(mode): ...
# Right
from typing import Literal
@tool
def pick(mode: Literal["import", "export"]) -> str:
    """Choose trade mode."""
    return mode
```

---

## 🧠 Tricky Interview Question
**Q**: "Your tool raises an exception and the whole agent run crashes. How should the decorator be configured?"

**Answer**: Use `handle_tool_error=True` (or a function/string) and raise `ToolException` for expected failures. LangChain then returns the error text as the tool output, the model sees it, and can retry with different arguments or explain the failure. Unexpected exceptions should be caught and converted to a safe message so internal details do not leak. Without this, an uncaught exception ends the loop.

---

## ⚫ Interview Questions + Answers

Q1: Where does `@tool` get the tool's description?
A1: From the docstring. If you pass `description=` to the decorator, that wins. The model uses it to decide when to call the tool.

Q2: How do you rename a tool?
A2: `@tool("new_name")` or `@tool(name_or_callable)` style first argument. Names should be snake_case and unique.

Q3: What is `args_schema` for?
A3: A Pydantic model giving explicit field descriptions, defaults and validators. Better than inferring from hints for complex inputs.

Q4: What does `return_direct=True` do?
A4: In legacy agents the tool output is returned to the user immediately without another LLM call. It saves one call (tokens/latency) but you lose model polishing.

Q5: (Hard) How do you give a tool access to per-request data (user id) without the LLM seeing or setting it?
A5: Use `InjectedToolArg` / `RunnableConfig` injection (pass `config: RunnableConfig` and read `config["configurable"]["user_id"]`). The parameter is hidden from the schema, so the model cannot fake it; your server sets it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Function is simple and fully described by hints + docstring
- You want fast prototyping

❌ Avoid when:
- You need complex shared state or class-based tools (use `StructuredTool` / `BaseTool`)
- Input rules are heavy (add `args_schema` then)

---

## 📊 Visual Diagram
```
 def get_duty_rate(hs_code: str, country: str = "IN") -> float:
     """Return duty percent..."""
            |
          @tool
            |
  +-------------------------------+
  | name:        get_duty_rate    |
  | description: Return duty ...  |
  | args_schema: {hs_code: str*,  |
  |               country: str}   |
  +-------------------------------+
            |
   JSON schema --> LLM (bind_tools)
```

---

## 💰 Cost Impact
- The name + description + schema is sent as input tokens every call (~60-150 tokens per tool).
- Long docstrings (examples, policies) multiply across steps.
- Optimise: one clear sentence + "when to use", short field descriptions, remove unused tools, and use `return_direct` or direct API responses for simple lookups to skip an LLM call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @tool | Decorator creating a tool | Function को tool बनाने वाला decorator |
| docstring | Function description text | Function का विवरण |
| args_schema | Pydantic input model | Input का Pydantic model |
| ToolException | Expected tool failure | Tool की अपेक्षित विफलता |
| handle_tool_error | Return error text, don't crash | Error को text बनाकर लौटाना |
| return_direct | Skip LLM after tool | Tool के बाद LLM छोड़ो |

---

## ⚡ 3-Line Summary
English: `@tool` converts a typed, documented function into a tool with a schema the LLM can read. Use `args_schema` for validation and `ToolException` with `handle_tool_error` for safe failures. The description and schema are billed as input tokens on every call.
Hindi: `@tool` typed और documented function को ऐसे tool में बदलता है जिसका schema LLM पढ़ सके। Validation के लिए `args_schema` और सुरक्षित failure के लिए `ToolException` + `handle_tool_error` इस्तेमाल करें। Description और schema हर call में input tokens की तरह गिने जाते हैं।

---

## ➡️ Next Topic
**281. StructuredTool** — building tools explicitly, with sync and async functions together.
