---

# 305. OpenAI Functions Agent
# हिंदी में: OpenAI Functions Agent

---

## 🔵 Simple Definition (English)
The OpenAI Functions Agent is a LangChain agent built on OpenAI's original `functions` / `function_call` API. The model returns a structured function call instead of free-text "Action:" lines, so there is no fragile text parsing. In LangChain it is `create_openai_functions_agent` with `AgentExecutor`. OpenAI has since replaced `functions` with `tools`, so new code should prefer `create_tool_calling_agent` or `create_openai_tools_agent`.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Functions Agent LangChain का agent है जो OpenAI की मूल `functions` / `function_call` API पर बना है। Model free-text "Action:" lines की जगह structured function call देता है, इसलिए fragile text parsing नहीं करनी पड़ती। LangChain में यह `create_openai_functions_agent` + `AgentExecutor` है। OpenAI ने `functions` की जगह अब `tools` दिया है, इसलिए नए code में `create_tool_calling_agent` या `create_openai_tools_agent` बेहतर हैं।

---

## 🔴 Problem it Solves
Classic ReAct agents ask the model to write "Thought / Action / Action Input" text and then parse it with regex. Models break the format, causing parsing errors and retries. Function calling makes the model emit JSON arguments that match a schema, which is far more reliable.

## 🔴 यह क्यों बना? (Hindi)
Classic ReAct agents में model से "Thought / Action / Action Input" text लिखवाकर regex से parse करना पड़ता था। Model format तोड़ देता था, जिससे parsing errors और retries होते थे। Function calling में model schema से मेल खाते JSON arguments देता है, जो कहीं ज़्यादा भरोसेमंद है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools; convert to function schemas (convert_to_openai_function)
Step 2 → Prompt with system + {input} + agent_scratchpad (messages)
Step 3 → Model returns AIMessage with function_call {name, arguments}
Step 4 → Output parser turns it into AgentActionMessageLog (tool, tool_input)
Step 5 → AgentExecutor runs the tool; result becomes a FunctionMessage
Step 6 → Scratchpad (function call + result messages) is sent back
Step 7 → Model replies with plain text -> AgentFinish (final answer)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tools define करो; function schemas में बदलो (convert_to_openai_function)
Step 2 → Prompt: system + {input} + agent_scratchpad (messages)
Step 3 → Model AIMessage में function_call {name, arguments} देता है
Step 4 → Output parser इसे AgentActionMessageLog (tool, tool_input) बनाता है
Step 5 → AgentExecutor tool चलाता है; result FunctionMessage बनता है
Step 6 → Scratchpad (function call + result) वापस model को जाता है
Step 7 → Model plain text देता है -> AgentFinish (final जवाब)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tools: `search_hs_codes`, `get_duty_rate`. For "duty on a Bluetooth speaker", the Functions agent emits `function_call: search_hs_codes {"query": "bluetooth speaker"}`, then `get_duty_rate {"hs_code": "851822"}`, then answers. A legacy system built in 2023 on this API can be migrated by changing only the constructor to `create_tool_calling_agent`.

**Zomato AI**: `find_restaurants(cuisine, city)` and `place_order(item_ids)`.

## 🟡 Real Example Hindi mein
**Tariff System**: Tools: `search_hs_codes`, `get_duty_rate`। "Bluetooth speaker पर duty" के लिए agent पहले `function_call: search_hs_codes {"query": "bluetooth speaker"}`, फिर `get_duty_rate {"hs_code": "851822"}` और फिर जवाब देता है। 2023 में इस API पर बना पुराना system सिर्फ़ constructor बदलकर `create_tool_calling_agent` पर migrate हो सकता है।

**Zomato AI**: `find_restaurants(cuisine, city)` और `place_order(item_ids)`।

---

## 💻 Code Example — Basic
```python
# Basic: the legacy OpenAI "functions" message format, simulated offline
import json                                              # parse arguments string
from typing import Any, Callable                         # typing

# 1) Function schema in the legacy format (what you pass as functions=[...])
FUNCTIONS: list[dict[str, Any]] = [{
    "name": "get_duty_rate",
    "description": "Get customs duty percent for an HS code",
    "parameters": {"type": "object",
                   "properties": {"hs_code": {"type": "string"}},
                   "required": ["hs_code"]},
}]

def get_duty_rate(hs_code: str) -> str:
    """Real function."""
    return {"851822": "20%"}.get(hs_code, "unknown")

REGISTRY: dict[str, Callable[..., str]] = {"get_duty_rate": get_duty_rate}

# 2) What the legacy model returns: arguments is a JSON STRING, not a dict
fake_ai_message: dict[str, Any] = {
    "role": "assistant", "content": None,
    "function_call": {"name": "get_duty_rate", "arguments": '{"hs_code": "851822"}'},
}

# 3) Parse + execute
call = fake_ai_message["function_call"]
try:
    args = json.loads(call["arguments"])                 # may fail if model emits bad JSON
    result = REGISTRY[call["name"]](**args)              # run the function
except (json.JSONDecodeError, KeyError, TypeError) as exc:
    result = f"error: {exc}"

# 4) Result goes back as a role="function" message (legacy) - modern API uses role="tool"
follow_up = {"role": "function", "name": call["name"], "content": result}
print(follow_up)                                         # {'role': 'function', 'name': 'get_duty_rate', 'content': '20%'}
```

## 💻 Code Example — Advanced
```python
# Production: create_openai_functions_agent + AgentExecutor, with the modern replacement alongside
import asyncio                                           # async runtime
import logging                                           # logs
from typing import Any                                   # typing
from langchain.agents import (AgentExecutor, create_openai_functions_agent,
                              create_tool_calling_agent)  # pip install langchain langchain-openai
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

logger = logging.getLogger("functions_agent")

@tool
def search_hs_codes(query: str) -> str:
    """Search HS codes by product description."""
    return "851822 Loudspeakers, mounted in enclosures"

@tool
def get_duty_rate(hs_code: str) -> str:
    """Get basic customs duty percent for an HS code."""
    return "20%"

TOOLS = [search_hs_codes, get_duty_rate]
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant. Always use tools for facts."),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),             # required slot
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Legacy style (functions API under the hood; deprecated path):
legacy_agent = create_openai_functions_agent(llm, TOOLS, prompt)
# Recommended style (tools API; supports parallel tool calls):
modern_agent = create_tool_calling_agent(llm, TOOLS, prompt)

executor = AgentExecutor(
    agent=modern_agent, tools=TOOLS,
    max_iterations=6, max_execution_time=30,
    handle_parsing_errors=True, return_intermediate_steps=True,
)

async def ask(question: str) -> dict[str, Any]:
    try:
        out = await executor.ainvoke({"input": question})
    except Exception as exc:
        logger.exception("agent failed")
        return {"answer": "Sorry, something went wrong.", "error": type(exc).__name__}
    steps = [(a.tool, a.tool_input) for a, _ in out["intermediate_steps"]]
    return {"answer": out["output"], "tool_calls": steps}

if __name__ == "__main__":
    print(asyncio.run(ask("Duty on a Bluetooth speaker?")))     # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException               # framework
from pydantic import BaseModel, Field

app = FastAPI()

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/tariff/agent")
async def tariff_agent(body: Ask) -> dict[str, Any]:
    result = await ask(body.question)                    # uses the executor built once at startup
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result
```

---

## 🔗 LangChain / LangGraph Connection
`create_openai_functions_agent` and `AgentExecutor` are the older LangChain path. Today LangChain recommends LangGraph's `create_react_agent`, which uses the model's native tool calling and gives you persistence, streaming and human-in-the-loop.

```python
from langgraph.prebuilt import create_react_agent
graph_agent = create_react_agent(llm, TOOLS)
res = graph_agent.invoke({"messages": [("user", "Duty on a Bluetooth speaker?")]})
print(res["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Starting a new project on the deprecated `functions` agent
✅ Correct: Use `create_tool_calling_agent` or LangGraph `create_react_agent`.

```python
# Wrong (legacy)
agent = create_openai_functions_agent(llm, tools, prompt)
# Right
agent = create_tool_calling_agent(llm, tools, prompt)
```

❌ Mistake 2: Trusting `arguments` as a dict (in the raw API it is a JSON string that may be invalid)
✅ Correct: Parse with try/except and validate with Pydantic.

```python
# Wrong
args = call["arguments"]["hs_code"]
# Right
try:
    args = json.loads(call["arguments"])
except json.JSONDecodeError:
    args = {}
```

---

## 🧠 Tricky Interview Question
**Q**: "A function-calling agent sometimes calls `get_duty_rate` with an HS code it invented, before searching. How do you stop that?"

**Answer**: Function calling guarantees valid JSON shape, not correct values. The model can hallucinate argument values. Fixes: (1) put dependencies in the descriptions ("only call after search_hs_codes; hs_code must come from its result"), (2) validate in code (`hs_code` must exist in the DB, else return a helpful error), (3) use `tool_choice` to force `search_hs_codes` on the first step, or build a LangGraph with an explicit order, (4) add few-shot examples in the system prompt, (5) log and evaluate invalid-argument rate.

---

## ⚫ Interview Questions + Answers

Q1: How is the Functions agent different from a ReAct text agent?
A1: It uses the model's native structured function calls instead of parsing "Action:" text, so it is more reliable.

Q2: Why is `functions` deprecated in the OpenAI API?
A2: It was replaced by `tools` and `tool_calls`, which support multiple (parallel) calls and more tool types. LangChain's `create_openai_functions_agent` is therefore legacy.

Q3: What does `agent_scratchpad` contain in this agent?
A3: Message pairs: the model's function call and the function result (FunctionMessage or ToolMessage).

Q4: Can it call two tools in one turn?
A4: The old `functions` format returns one call per turn. The newer `tools` format (and `create_tool_calling_agent`) allows parallel calls.

Q5: (Hard) How do you migrate a production Functions agent to LangGraph safely?
A5: Keep tools unchanged; build `create_react_agent` with the same prompt as `prompt`/system message; run both on a golden eval set and shadow traffic; compare accuracy, steps, cost and latency; add a checkpointer and recursion limit; switch traffic gradually with a feature flag and roll back if needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Maintaining an existing legacy system
- Learning how function calling evolved

❌ Avoid when:
- Starting new work (use tool calling / LangGraph)
- Using non-OpenAI models (use the generic tool-calling agent)

---

## 📊 Visual Diagram
```
 user input
    |
 [LLM] -- function_call {name, arguments(JSON)} -->
    ^                                                  |
    |                                           [Output parser]
    |                                                  |
 FunctionMessage(result) <-- run tool <-- AgentAction -+
    |
 [LLM] -- plain text --> AgentFinish --> final answer
```

---

## 💰 Cost Impact
- Function schemas are sent as input tokens every call (about 50-150 tokens per tool).
- Fewer parse failures than text-ReAct, so fewer wasted retries.
- Legacy one-call-per-turn behaviour means more turns than parallel tool calling: each extra turn re-sends the history. Migrating to tool calling often reduces total tokens when tasks need several independent lookups.
- Use gpt-4o-mini for routine tool use and cap iterations.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| function_call | Legacy structured call | पुराना structured call |
| tool_calls | Modern structured calls | नए structured calls |
| AgentAction | Parsed decision to call a tool | Tool चलाने का parsed फ़ैसला |
| AgentFinish | Final answer object | Final जवाब object |
| FunctionMessage | Legacy tool result message | पुराना tool result message |
| Deprecated | Still works but not recommended | चलता है पर सुझाया नहीं जाता |

---

## ⚡ 3-Line Summary
English: The OpenAI Functions Agent uses structured function calls instead of parsing text, which made agents far more reliable. It is now a legacy path; prefer tool-calling agents or LangGraph. Schemas and scratchpad history cost tokens on every turn.
Hindi: OpenAI Functions Agent text parse करने की जगह structured function calls इस्तेमाल करता है, जिससे agents कहीं ज़्यादा भरोसेमंद हुए। अब यह legacy रास्ता है; tool-calling agents या LangGraph चुनें। Schemas और scratchpad history हर turn में tokens खाते हैं।

---

## ➡️ Next Topic
**306. OpenAI Tools Agent** — the modern replacement with parallel tool calls.
