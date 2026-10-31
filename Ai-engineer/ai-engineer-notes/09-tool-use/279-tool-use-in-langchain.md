---

# 279. Tool Use in LangChain
# हिंदी में: LangChain में Tool Use

---

## 🔵 Simple Definition (English)
In LangChain a tool is a Python function wrapped with a name, description and input schema. You attach tools to a chat model with `bind_tools`, the model returns `tool_calls`, and you run them and send back `ToolMessage` results. The same code works for OpenAI, Claude, Gemini and others.

## 🔵 सरल परिभाषा (Hindi)
LangChain में tool एक Python function है जिसके साथ नाम, description और input schema जुड़ा होता है। `bind_tools` से tools model से जोड़ते हैं, model `tool_calls` लौटाता है, आप उन्हें चलाकर `ToolMessage` में result भेजते हैं। यही code OpenAI, Claude, Gemini सब पर चलता है।

---

## 🔴 Problem it Solves
Each provider has a different tool format (OpenAI `tools`, Anthropic `input_schema`, Gemini `FunctionDeclaration`). Rewriting tool schemas for every vendor is slow and error-prone. LangChain gives one standard interface so you can switch models without touching tool code.

## 🔴 यह क्यों बना? (Hindi)
हर provider का tool format अलग है (OpenAI `tools`, Anthropic `input_schema`, Gemini `FunctionDeclaration`)। हर vendor के लिए schema दोबारा लिखना धीमा और error-prone है। LangChain एक standard interface देता है, ताकि model बदलने पर tool code न बदलना पड़े।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools with @tool (name, docstring, type hints -> JSON schema)
Step 2 → llm_with_tools = llm.bind_tools([tool1, tool2])
Step 3 → Invoke with messages -> AIMessage with .tool_calls (name, args, id)
Step 4 → For each call, run tool.invoke(args) (or tool.invoke(tool_call) -> ToolMessage)
Step 5 → Append AIMessage + ToolMessage(s) to the message list
Step 6 → Invoke the model again -> final AIMessage text
Step 7 → (Agents/LangGraph automate steps 3-6 as a loop)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → @tool से tools define करो (नाम, docstring, type hints -> JSON schema)
Step 2 → llm_with_tools = llm.bind_tools([tool1, tool2])
Step 3 → Messages भेजो -> AIMessage में .tool_calls (name, args, id)
Step 4 → हर call के लिए tool.invoke(args) चलाओ
Step 5 → AIMessage + ToolMessage को messages में जोड़ो
Step 6 → Model को फिर चलाओ -> final text
Step 7 → (Agents/LangGraph steps 3-6 को loop में automate करते हैं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tools `search_hs_codes(query)` and `get_duty_rate(hs_code)`. User: "Duty on Bluetooth earbuds?" The model first calls `search_hs_codes("bluetooth earbuds")`, gets 8518.30, then calls `get_duty_rate("851830")`. It combines both into one answer. Swap `ChatOpenAI` for `ChatAnthropic` and nothing else changes.

**Amazon-style assistant**: tools `track_package`, `start_return`.

## 🟡 Real Example Hindi mein
**Tariff System**: Tools `search_hs_codes(query)` और `get_duty_rate(hs_code)`। User: "Bluetooth earbuds पर duty?" Model पहले `search_hs_codes` से 8518.30 पाता है, फिर `get_duty_rate("851830")` चलाता है और दोनों को जोड़कर जवाब देता है। `ChatOpenAI` की जगह `ChatAnthropic` लगाओ, बाकी code वही रहता है।

**Amazon-style assistant**: tools `track_package`, `start_return`।

---

## 💻 Code Example — Basic
```python
# Basic: LangChain tools without any LLM (runs offline)
# pip install langchain-core
from langchain_core.tools import tool          # decorator that builds a tool

@tool                                          # turns the function into a LangChain tool
def get_duty_rate(hs_code: str) -> float:
    """Return basic customs duty percent for an HS code."""   # becomes the description
    rates: dict[str, float] = {"8517": 20.0, "8518": 15.0}    # fake tariff table
    return rates.get(hs_code, -1.0)            # -1.0 means "not found"

print(get_duty_rate.name)                      # get_duty_rate
print(get_duty_rate.description)               # the docstring
print(get_duty_rate.args)                      # {'hs_code': {'title': 'Hs Code', 'type': 'string'}}
print(get_duty_rate.invoke({"hs_code": "8517"}))   # 20.0

# What the model returns after bind_tools (we fake it here):
fake_tool_call: dict = {"name": "get_duty_rate", "args": {"hs_code": "8518"}, "id": "call_1", "type": "tool_call"}
tool_map = {t.name: t for t in [get_duty_rate]}        # name -> tool lookup
msg = tool_map[fake_tool_call["name"]].invoke(fake_tool_call)  # passing a tool_call returns a ToolMessage
print(type(msg).__name__, msg.content)         # ToolMessage 15.0
```

## 💻 Code Example — Advanced
```python
# Production: manual tool loop, async, parallel tool execution, error handling
import asyncio                                           # async runtime
from typing import Any                                   # type hints
from langchain_core.tools import tool                    # tool decorator
from langchain_core.messages import (                    # message types
    BaseMessage, HumanMessage, SystemMessage, ToolMessage)
from langchain_openai import ChatOpenAI                  # any chat model works here

@tool
async def get_duty_rate(hs_code: str) -> dict[str, Any]:
    """Return basic customs duty percent for an HS code."""
    await asyncio.sleep(0)                               # pretend async DB call
    return {"hs_code": hs_code, "rate_percent": 20.0}

@tool
async def search_hs_codes(query: str) -> list[str]:
    """Search HS codes by product description."""
    await asyncio.sleep(0)
    return ["851830 - Headphones and earphones"]

TOOLS = [get_duty_rate, search_hs_codes]                 # tool list
TOOL_MAP = {t.name: t for t in TOOLS}                    # allow-list by name
MAX_STEPS = 6                                            # loop guard

async def run_agent(question: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(TOOLS)  # model + tools
    messages: list[BaseMessage] = [
        SystemMessage(content="You are a tariff assistant. Use tools for facts."),
        HumanMessage(content=question),
    ]
    for _ in range(MAX_STEPS):                           # bounded loop
        ai = await llm.ainvoke(messages)                 # async model call
        messages.append(ai)                              # keep the AIMessage
        if not ai.tool_calls:                            # no tools requested -> done
            return str(ai.content)

        async def run_one(call: dict[str, Any]) -> ToolMessage:
            tool_obj = TOOL_MAP.get(call["name"])        # allow-list check
            if tool_obj is None:
                return ToolMessage(content="unknown tool", tool_call_id=call["id"], status="error")
            try:
                out = await asyncio.wait_for(tool_obj.ainvoke(call["args"]), timeout=10)  # timeout
                return ToolMessage(content=str(out), tool_call_id=call["id"])
            except Exception as exc:                     # return error so model can recover
                return ToolMessage(content=f"error: {exc}", tool_call_id=call["id"], status="error")

        results = await asyncio.gather(*(run_one(c) for c in ai.tool_calls))  # parallel calls
        messages.extend(results)                         # feed results back
    return "Stopped: step limit reached"

if __name__ == "__main__":
    print(asyncio.run(run_agent("Duty on bluetooth earbuds?")))   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
# FastAPI endpoint using the LangChain tool loop
from fastapi import FastAPI, HTTPException          # framework
from pydantic import BaseModel                      # validation

app = FastAPI()

class Query(BaseModel):
    question: str                                   # user question

@app.post("/tariff/ask")
async def ask(q: Query) -> dict[str, str]:
    try:
        answer = await run_agent(q.question)        # from the Advanced example
    except Exception as exc:                        # model / network failure
        raise HTTPException(status_code=502, detail=str(exc))
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
`bind_tools` is the core primitive. Higher levels build on it: `create_react_agent` from `langgraph.prebuilt` runs the exact loop above as a graph, and `ToolNode` executes `tool_calls` in a graph node.

```python
# LangGraph prebuilt agent (same tools)
from langgraph.prebuilt import create_react_agent     # pip install langgraph
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), TOOLS)
result = agent.invoke({"messages": [("user", "Duty on bluetooth earbuds?")]})
print(result["messages"][-1].content)                 # final answer
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to send ToolMessage back with the right `tool_call_id`
✅ Correct: Every tool call id needs a matching ToolMessage.

```python
# Wrong - model sees no result, API may raise an error
messages.append(ai)
# Right
messages.append(ai)
messages.append(ToolMessage(content="20.0", tool_call_id=ai.tool_calls[0]["id"]))
```

❌ Mistake 2: Using `llm.invoke` and expecting the tool to run automatically
✅ Correct: `bind_tools` only lets the model REQUEST a tool. Run it yourself or use an agent.

```python
# Wrong
print(llm_with_tools.invoke("duty for 8517?").content)   # empty string, tool_calls has the request
# Right
msg = llm_with_tools.invoke("duty for 8517?")
print(msg.tool_calls)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your agent works with GPT-4o-mini but after switching to a local model through LangChain, tools are never called. Why?"

**Answer**: `bind_tools` only works if the model supports native tool/function calling. Many local models do not, so LangChain sends the schema but the model just replies with text. Check that the integration implements `bind_tools` for a tool-capable model (for example a tool-trained model in Ollama), or fall back to prompt-based parsing (ReAct) or `with_structured_output`. Also verify tool descriptions, because weaker models need clearer ones.

---

## ⚫ Interview Questions + Answers

Q1: What does `bind_tools` do?
A1: It returns a new runnable that sends tool schemas with every request, so the model can answer with `tool_calls`. It does not execute the tools.

Q2: What is the difference between `AIMessage.tool_calls` and `ToolMessage`?
A2: `tool_calls` is the model's request (name, args, id). `ToolMessage` is your reply with the result, linked by `tool_call_id`.

Q3: How does LangChain produce the JSON schema for a tool?
A3: From the function's type hints and docstring (via Pydantic). `tool.args` shows it. For richer control pass `args_schema` with a Pydantic model.

Q4: How do you run several tool calls from one response efficiently?
A4: They are independent, so use `asyncio.gather` with `tool.ainvoke`, or `tool.batch`. Return one `ToolMessage` per call.

Q5: (Hard) How do you stop an agent from looping forever or calling dangerous tools?
A5: Bounded steps (loop limit or LangGraph `recursion_limit`), allow-list of tools, argument validation with Pydantic, timeouts, read-only tools by default, human approval (interrupt) for writes, and logging each call with token usage.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want provider-independent tool definitions
- You plan to move to agents or LangGraph
- You need tracing in LangSmith

❌ Avoid when:
- A single provider SDK call is enough and you want minimum dependencies
- You need a provider-specific feature LangChain does not expose yet

---

## 📊 Visual Diagram
```
 @tool functions
      |
 llm.bind_tools([...])
      |
 messages --> [ LLM ] --> AIMessage(tool_calls=[{name,args,id}])
                               |
                        run tool(s) (parallel)
                               |
                       ToolMessage(tool_call_id=id)
                               |
 messages + AIMessage + ToolMessage --> [ LLM ] --> final answer
```

---

## 💰 Cost Impact
- Tool schemas are re-sent on every model call: 5 tools x ~100 tokens = ~500 extra input tokens per step.
- Each step re-sends the whole message history, so cost grows with the number of steps.
- Optimise: bind only the tools a route needs, keep docstrings tight, truncate large tool outputs, use a cheap model (gpt-4o-mini / Haiku / Flash), set max steps, and track usage with `AIMessage.usage_metadata`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bind_tools | Attach tool schemas to a model | Model से tools जोड़ना |
| tool_calls | Model's tool requests | Model की tool माँगें |
| ToolMessage | Tool result message | Tool के result का message |
| tool_call_id | Links result to request | Result को request से जोड़ने वाली id |
| args_schema | Pydantic input schema | Input का Pydantic schema |
| ToolNode | LangGraph node running tools | Tools चलाने वाला node |

---

## ⚡ 3-Line Summary
English: LangChain gives one tool interface across providers: define with @tool, attach with bind_tools, run the tool_calls and return ToolMessages. The model only requests tools; you or an agent execute them. Schemas and history cost tokens every step.
Hindi: LangChain सभी providers के लिए एक tool interface देता है: @tool से define, bind_tools से attach, tool_calls चलाकर ToolMessage लौटाओ। Model सिर्फ़ माँगता है, चलाना आपका काम है। Schemas और history हर step tokens खाते हैं।

---

## ➡️ Next Topic
**280. @tool Decorator** — how the decorator builds names, descriptions and schemas.
