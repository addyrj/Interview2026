---

# 272. Function Calling in OpenAI
# हिंदी में: Function Calling — OpenAI में

---

## 🔵 Simple Definition (English)
Function calling lets LLMs trigger your code. You describe your functions as JSON schemas — the LLM decides when to call them and with what arguments. The LLM doesn't execute code itself — it returns a JSON object saying "call `get_hs_code` with `{product: 'iPhone'}`" — your code executes it and sends the result back. This is how agents get superpowers.

## 🔵 सरल परिभाषा (Hindi)
Function calling LLMs को आपका code trigger करने देता है। आप functions को JSON schemas के रूप में describe करते हो — LLM decide करता है कब call करना है और किन arguments से। LLM खुद execute नहीं करता — JSON object return करता है: "call `get_hs_code` with `{product: 'iPhone'}`" — आपका code execute करता है।

---

## 🔴 Problem it Solves
Without function calling: LLM can only generate text. It can't look up live data, run calculations, query databases, or take actions. With function calling: LLM becomes an orchestrator — it generates text AND triggers real-world actions. This is the bridge between LLMs (reasoning) and your code (execution).

## 🔴 यह क्यों बना? (Hindi)
Function calling के बिना: LLM सिर्फ text generate करता है। Live data lookup, calculations, DB queries — नहीं हो सकता। Function calling से: LLM orchestrator बन जाता है — text AND real-world actions trigger करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You define tools: name, description, parameters (JSON schema)
Step 2 → User sends message + tools list to LLM
Step 3 → LLM decides: "I need to call get_hs_code to answer this"
Step 4 → LLM returns: tool_calls = [{function: "get_hs_code", arguments: {...}}]
Step 5 → finish_reason = "tool_calls" (not "stop")
Step 6 → Your code executes the function with given arguments
Step 7 → Append tool result to messages as role="tool"
Step 8 → Send messages back to LLM
Step 9 → LLM reads the result, generates final text answer
Step 10 → finish_reason = "stop" → return to user
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "What is the import duty for 10 iPhones from USA?"
1. LLM calls `get_hs_code(product="iPhone")` → returns `{"hs_code": "8517.12.00"}`
2. LLM calls `get_duty_rate(hs_code="8517.12.00", origin="USA")` → returns `{"duty_rate": 20, "gst": 18}`
3. LLM calls `calculate_duty(quantity=10, unit_price=80000, duty_rate=20, gst=18)` → returns `{"total_duty": 144000}`
4. LLM generates: "The import duty for 10 iPhones (HS 8517.12.00) from USA is ₹1,44,000 (20% duty + 18% GST)."

## 🟡 Real Example Hindi mein
User: "10 iPhones की import duty क्या है?" → LLM: `get_hs_code` call → `get_duty_rate` call → `calculate_duty` call → Final answer with all calculations।

---

## 💻 Code Example — Basic
```python
# Single tool call — complete working example
import json
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

# ─── Tool definitions (JSON schema) ───────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_hs_code",
            "description": "Get the HS (Harmonized System) tariff code for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "The product name, e.g. 'iPhone 15', 'lithium battery'",
                    }
                },
                "required": ["product"],    # product is required
            },
        },
    }
]

# ─── Actual function implementation ───────────────────────────────
def get_hs_code(product: str) -> dict:
    """Your actual implementation — DB lookup, API call, etc."""
    hs_database = {
        "iphone": "8517.12.00",
        "smartphone": "8517.12.00",
        "laptop": "8471.30.00",
        "rice": "1006.30.00",
    }
    key = product.lower().replace(" ", "")
    code = hs_database.get(key, "unknown")
    return {"product": product, "hs_code": code, "chapter": code[:2] if code != "unknown" else None}

# ─── Dispatcher: maps function names to actual functions ──────────
FUNCTION_MAP = {
    "get_hs_code": get_hs_code,
}

def execute_tool_call(tool_call) -> str:
    """Execute the function the LLM requested."""
    func_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)   # parse JSON string → dict

    func = FUNCTION_MAP.get(func_name)
    if not func:
        return json.dumps({"error": f"Unknown function: {func_name}"})

    result = func(**arguments)
    return json.dumps(result)   # must return as JSON string

# ─── Main: LLM + tool call loop ───────────────────────────────────
async def main():
    messages = [
        {"role": "user", "content": "What is the HS code for iPhone 15?"}
    ]

    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",     # LLM decides whether to call a tool
        )

        message = response.choices[0].message
        messages.append(message)    # add assistant response to history

        if response.choices[0].finish_reason == "stop":
            # LLM has final answer (no more tool calls needed)
            print(f"Answer: {message.content}")
            break

        # LLM wants to call tools:
        for tool_call in message.tool_calls:
            print(f"LLM calling: {tool_call.function.name}({tool_call.function.arguments})")

            result = execute_tool_call(tool_call)
            print(f"Result: {result}")

            # Add tool result to messages:
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id,   # must match the tool_call id!
            })
        # Loop back: send updated messages (with tool results) to LLM

asyncio.run(main())
```

## 💻 Code Example — Advanced (Parallel tool calls + production)
```python
# Production: multiple tools, parallel calls, type safety
import json
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Any

client = AsyncOpenAI()

# ─── Tool definitions ──────────────────────────────────────────────
TARIFF_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_hs_code",
            "description": "Look up HS tariff code for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product name"},
                },
                "required": ["product"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_duty_rate",
            "description": "Get import duty rate for an HS code from a specific country",
            "parameters": {
                "type": "object",
                "properties": {
                    "hs_code":   {"type": "string"},
                    "origin":    {"type": "string", "description": "Country of origin, e.g. 'USA', 'China'"},
                    "quantity":  {"type": "number", "description": "Quantity of units"},
                    "unit_price": {"type": "number", "description": "Price per unit in INR"},
                },
                "required": ["hs_code", "origin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_trade_agreement",
            "description": "Check if a trade agreement applies between India and origin country",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "hs_code": {"type": "string"},
                },
                "required": ["origin", "hs_code"],
            },
        },
    },
]

# ─── Function implementations ──────────────────────────────────────
def get_hs_code(product: str) -> dict:
    return {"hs_code": "8517.12.00", "description": "Telephone sets including smartphones"}

def get_duty_rate(hs_code: str, origin: str, quantity: float = 1, unit_price: float = 0) -> dict:
    base_rates = {"8517.12.00": 20.0, "8471.30.00": 0.0}
    rate = base_rates.get(hs_code, 10.0)
    total_value = quantity * unit_price
    return {"hs_code": hs_code, "duty_rate_pct": rate, "total_duty_inr": total_value * rate / 100}

def check_trade_agreement(origin: str, hs_code: str) -> dict:
    agreements = {"UAE": True, "ASEAN": True, "USA": False}
    has_agreement = agreements.get(origin, False)
    return {"origin": origin, "has_agreement": has_agreement, "reduced_rate": 5.0 if has_agreement else None}

FUNCTION_MAP = {
    "get_hs_code": get_hs_code,
    "get_duty_rate": get_duty_rate,
    "check_trade_agreement": check_trade_agreement,
}

async def run_tariff_agent(user_query: str) -> str:
    """Run multi-tool agent. Handles parallel tool calls (LLM may request multiple at once)."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a tariff classification agent. "
                "Use the available tools to find HS codes, duty rates, and trade agreements. "
                "Always calculate the final duty amount if quantity and price are given."
            )
        },
        {"role": "user", "content": user_query},
    ]

    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TARIFF_TOOLS,
            tool_choice="auto",
            parallel_tool_calls=True,    # allow multiple tools in one response!
        )

        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "stop":
            return message.content

        # Handle PARALLEL tool calls (LLM may call multiple tools simultaneously):
        tool_results = []
        for tool_call in message.tool_calls:
            func = FUNCTION_MAP.get(tool_call.function.name)
            if func:
                args = json.loads(tool_call.function.arguments)
                result = func(**args)
            else:
                result = {"error": f"Unknown tool: {tool_call.function.name}"}

            tool_results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
            })

        messages.extend(tool_results)   # add all tool results before next LLM call

import asyncio
async def test():
    answer = await run_tariff_agent(
        "What is the total import duty for 50 iPhones from USA at ₹80,000 each?"
    )
    print(answer)

asyncio.run(test())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI
import json

app = FastAPI()
client = AsyncOpenAI()

class AgentRequest(BaseModel):
    query: str
    max_iterations: int = 10   # prevent infinite loops

class AgentResponse(BaseModel):
    answer: str
    tools_called: list[str]
    total_iterations: int

@app.post("/tariff-agent", response_model=AgentResponse)
async def tariff_agent(request: AgentRequest):
    """Agent that uses tools to answer tariff questions."""
    messages = [
        {"role": "system", "content": "Use tools to answer tariff questions."},
        {"role": "user",   "content": request.query},
    ]
    tools_called = []
    iterations = 0

    while iterations < request.max_iterations:
        iterations += 1
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TARIFF_TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "stop":
            return AgentResponse(
                answer=message.content,
                tools_called=tools_called,
                total_iterations=iterations,
            )

        for tc in message.tool_calls:
            tools_called.append(tc.function.name)
            func = FUNCTION_MAP.get(tc.function.name)
            result = func(**json.loads(tc.function.arguments)) if func else {}
            messages.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tc.id})

    return AgentResponse(answer="Max iterations reached", tools_called=tools_called, total_iterations=iterations)
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain: @tool decorator wraps Python functions as LLM-callable tools
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

@tool
def get_hs_code(product: str) -> str:
    """Look up HS tariff code for a product. Input: product name."""
    return f"HS code for {product}: 8517.12.00"

@tool
def get_duty_rate(hs_code: str, origin_country: str) -> str:
    """Get import duty rate for HS code from country. Returns duty percentage."""
    return f"Duty rate for {hs_code} from {origin_country}: 20%"

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([get_hs_code, get_duty_rate])

# LangGraph: tools are nodes in the agent graph
# Standard pattern: LLM node → ToolNode (executes tools) → back to LLM
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools=[get_hs_code, get_duty_rate])
# This creates the full ReAct loop automatically
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not handling the tool call loop — calling LLM once and stopping
```python
# Wrong — misses the response after tool execution:
response = await client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
if response.choices[0].finish_reason == "tool_calls":
    execute_tool(response.choices[0].message.tool_calls[0])
    # WRONG — never calls LLM again with the tool result!

# Correct — loop until finish_reason == "stop":
while True:
    response = await client.chat.completions.create(...)
    if response.choices[0].finish_reason == "stop":
        break
    # execute tools, append results, loop
```

❌ Mistake 2: Forgetting `tool_call_id` in the tool response
```python
# Wrong — LLM can't match result to which tool call it came from:
messages.append({"role": "tool", "content": result})

# Correct — must include tool_call_id:
messages.append({
    "role": "tool",
    "content": json.dumps(result),
    "tool_call_id": tool_call.id,   # matches the tool_call that triggered this
})
```

---

## 🧠 Tricky Interview Question

**Q**: "Your tariff agent sometimes calls `get_duty_rate` before `get_hs_code` — which fails because it doesn't have the HS code yet. How do you fix this without hardcoding the order?"

**Answer**: Three approaches: (1) **Tool description**: change `get_duty_rate` description to "Get duty rate. Requires hs_code — call get_hs_code first if you don't have it." Clear instructions in tool descriptions steer LLM behavior. (2) **Sequential tool choice**: use `tool_choice={"type": "function", "function": {"name": "get_hs_code"}}` to force the first call. (3) **LangGraph explicit flow**: model the dependency as a graph — `get_hs_code` node → conditional edge → `get_duty_rate` node. Explicit graph structure is more reliable than relying on LLM description-following for complex multi-step workflows.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `tool_choice="auto"`, `"required"`, and a specific tool?
A1: `"auto"` (default): LLM decides whether to call a tool or respond directly. `"required"`: LLM MUST call at least one tool (can't respond with text only). `{"type": "function", "function": {"name": "get_hs_code"}}`: LLM MUST call exactly this function — ignores all others. Use `"required"` when you always need structured data. Use specific tool to force a particular step in a pipeline.

Q2: What are parallel tool calls?
A2: When LLM determines two tools don't depend on each other, it can request both in a single response — `message.tool_calls` has length > 1. You execute both, return both results, then the LLM continues. Example: "Get HS code for iPhone AND check if there's a trade agreement with USA" — these can run in parallel. `parallel_tool_calls=True` in the API call enables this (default True for gpt-4o).

Q3: What is the difference between function calling and RAG for knowledge retrieval?
A3: RAG: pre-indexed documents → vector similarity → inject as context. Best for: large corpus of unstructured documents, semantic search. Function calling: your code executes when called — can query databases, call APIs, compute calculations. Best for: live/structured data (current exchange rates, DB queries), exact lookups. In production tariff systems: use RAG for regulations text + function calling for exact rate lookups from a database.

Q4: How do you prevent function calling from running indefinitely?
A4: `max_iterations` guard in your loop: `if iterations > 10: break`. Catch `StopIteration` or custom exceptions from tools. `max_tokens` limits output length. In LangChain: `AgentExecutor(max_iterations=10, handle_parsing_errors=True)`. In LangGraph: `recursion_limit` on the graph. Always assume LLMs can get stuck in loops when tools return unexpected formats.

Q5: How would you implement a tool that queries your PostgreSQL tariff database?
A5: Define a tool `query_tariff_db(hs_code: str, regulation_type: str)`. Inside: use asyncpg/SQLAlchemy to run a parameterized query — `SELECT duty_rate, description FROM tariff_rates WHERE hs_code = $1`. Return result as dict. Key security consideration: NEVER let the LLM construct raw SQL — only accept structured parameters and build queries yourself. The LLM provides hs_code → your code builds the safe SQL. This prevents SQL injection.

---

## 🔷 When to Use + When Not to Use

✅ Use function calling when:
- LLM needs live/dynamic data (current rates, DB lookup, API call)
- Need to take actions (send email, create order, update record)
- Need structured, typed output (LLM fills a schema)
- Building agents that reason + act

❌ Avoid when:
- Only need text generation — function calling adds latency
- Data is static and fits in context — just include it directly
- Every response needs to call a function — consider structured output instead

---

## 📊 Visual Diagram
```
User: "What is import duty for 10 iPhones?"
         │
         ▼
LLM (with tools) ──────────────────────────────────────────────────
         │
         │ finish_reason = "tool_calls"
         ▼
  tool_calls = [
    {name: "get_hs_code", args: {product: "iPhone"}},
    {name: "check_trade_agreement", args: {origin: "USA"}}  ← parallel!
  ]
         │
         ▼
Your Code executes both ──────────────────────────────────────────
  get_hs_code("iPhone") → {hs_code: "8517.12.00"}
  check_trade_agreement("USA") → {has_agreement: false}
         │
         ▼
Messages updated with tool results
         │
         ▼
LLM (second call) ────────────────────────────────────────────────
         │
         │ finish_reason = "stop"
         ▼
"The import duty for 10 iPhones (HS 8517.12.00) from USA is ₹1,60,000 (20% duty, no FTA discount)."
```

---

## 💰 Cost Impact
Each tool call = extra LLM call + tokens for tool definition in context
- Tool definitions: ~200 tokens overhead in every request with tools
- Each tool call round-trip: ~200 extra tokens
- 3-tool agent = ~4 LLM calls = 4x the tokens vs simple query
- Cost: ~$0.001 per 3-tool agent interaction (gpt-4o-mini) — still very affordable

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function calling | LLM requests code execution | LLM code execute करने का request |
| Tool definition | JSON schema describing a function | Function का JSON description |
| tool_calls | LLM's response requesting functions | LLM की function call request |
| tool_call_id | Unique ID matching call to result | Call और result को match करने वाला ID |
| finish_reason | Why LLM stopped: stop/tool_calls | LLM क्यों रुका |
| Parallel tool calls | Multiple tools called simultaneously | एक साथ multiple tools |
| Dispatcher | Code mapping function names → functions | Function names → implementations |

---

## ⚡ 3-Line Summary
English: Function calling lets LLMs trigger your code — you define tools as JSON schemas, the LLM returns `tool_calls`, you execute them and send results back, the LLM reads results and generates a final answer. Always loop until `finish_reason == "stop"`. Include `tool_call_id` in every tool response or the conversation breaks.
Hindi: Function calling LLMs को आपका code trigger करने देता है। JSON schemas से tools define करो → LLM `tool_calls` return करता है → आप execute करो → result भेजो → LLM final answer देता है। Loop `finish_reason == "stop"` तक चलाओ।

---

## ➡️ Next Topic
**273. Tool Definition Schema** — parameter types, `required` fields, `enum` values, `description` best practices that improve LLM tool selection accuracy.
