---

# 299. ReAct in LangChain
# हिंदी में: LangChain में ReAct

---

## 🔵 Simple Definition (English)
LangChain provides `create_react_agent(llm, tools, prompt)` which builds a text-based ReAct agent (a runnable that outputs `AgentAction` or `AgentFinish`), and `AgentExecutor` which runs the loop. The prompt must contain `{tools}`, `{tool_names}`, `{input}` and `{agent_scratchpad}`.

## 🔵 सरल परिभाषा (Hindi)
LangChain `create_react_agent(llm, tools, prompt)` देता है जो text-based ReAct agent बनाता है (एक runnable जो `AgentAction` या `AgentFinish` लौटाता है), और `AgentExecutor` loop चलाता है। Prompt में `{tools}`, `{tool_names}`, `{input}` और `{agent_scratchpad}` ज़रूर होने चाहिए।

---

## 🔴 Problem it Solves
Writing the parser, prompt, tool registry, error handling and loop yourself (note 298) is repetitive. LangChain standardises these pieces: tools are `@tool` functions, the prompt is shared via the hub, parsing is done by `ReActSingleInputOutputParser`, and tracing works out of the box with LangSmith.

## 🔴 यह क्यों बना? (Hindi)
Parser, prompt, tool registry, error handling और loop खुद लिखना (note 298) बार-बार का काम है। LangChain इन्हें standard बनाता है: tools `@tool` functions हैं, prompt hub से मिलता है, parsing `ReActSingleInputOutputParser` करता है, और LangSmith tracing अपने आप चलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools with @tool (docstring = description)
Step 2 → Get the ReAct prompt: hub.pull("hwchase17/react") or your own PromptTemplate
Step 3 → agent = create_react_agent(llm, tools, prompt)   (llm | prompt | parser pipeline)
Step 4 → executor = AgentExecutor(agent=agent, tools=tools, max_iterations=..., handle_parsing_errors=True)
Step 5 → executor.invoke({"input": question})
Step 6 → Each loop: agent outputs AgentAction -> executor runs tool -> Observation -> scratchpad grows
Step 7 → AgentFinish -> executor returns {"input":..., "output":...}
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → @tool से tools बनाओ (docstring = description)
Step 2 → ReAct prompt लो: hub.pull("hwchase17/react") या अपना PromptTemplate
Step 3 → agent = create_react_agent(llm, tools, prompt)   (llm | prompt | parser pipeline)
Step 4 → executor = AgentExecutor(agent=agent, tools=tools, max_iterations=..., handle_parsing_errors=True)
Step 5 → executor.invoke({"input": question})
Step 6 → हर loop: agent AgentAction देता है -> executor tool चलाता है -> Observation -> scratchpad बढ़ता है
Step 7 → AgentFinish -> executor {"input":..., "output":...} लौटाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: an `AgentExecutor` with `search_hs_codes`, `get_tariff_rate` and `calculator`. A broker asks "Duty on 200 steel bolts valued at 1,000 USD?"; the agent finds HS 7318.15, the 10% rate, and computes the duty. `verbose=True` prints the full Thought/Action/Observation trail for training new staff.

**Amazon AI**: a seller-support ReAct agent with `get_order`, `get_policy`, `create_ticket`.

## 🟡 Real Example Hindi mein
**Tariff System**: `search_hs_codes`, `get_tariff_rate`, `calculator` वाला `AgentExecutor`। Broker पूछता है "1,000 USD के 200 steel bolts की duty?"; agent HS 7318.15 खोजता है, 10% rate लेता है और duty निकालता है। `verbose=True` से पूरा Thought/Action/Observation trail दिखता है, नए staff की training के लिए उपयोगी।

**Amazon AI**: seller-support ReAct agent: `get_order`, `get_policy`, `create_ticket`।

---

## 💻 Code Example — Basic
```python
# LangChain text-based ReAct agent. Needs: pip install langchain langchain-openai langchain-core
# Requires OPENAI_API_KEY to actually run; syntax shown is current for langchain 0.2/0.3.
from langchain.agents import AgentExecutor, create_react_agent    # agent + loop runner
from langchain_core.prompts import PromptTemplate                  # prompt object
from langchain_core.tools import tool                              # tool decorator
from langchain_openai import ChatOpenAI                            # chat model wrapper

@tool
def search_hs_codes(query: str) -> str:
    """Find an HS code from a product description."""              # docstring becomes tool description
    return "6109.10 - T-shirts, cotton" if "shirt" in query.lower() else "no match"

@tool
def get_tariff_rate(hs_code: str) -> str:
    """Get the duty percent for a known HS code like 6109.10."""
    return {"6109.10": "20%"}.get(hs_code.strip(), "unknown")

tools = [search_hs_codes, get_tariff_rate]                         # list of tools

# Same structure as hwchase17/react on LangChain Hub (written inline so no network is needed):
prompt = PromptTemplate.from_template("""Answer the following question as best you can. You have access to these tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)               # deterministic
agent = create_react_agent(llm, tools, prompt)                     # Runnable that returns AgentAction/AgentFinish
executor = AgentExecutor(agent=agent, tools=tools, verbose=True,   # verbose prints the trail
                         max_iterations=6, handle_parsing_errors=True)

if __name__ == "__main__":
    print(executor.invoke({"input": "What is the duty on a cotton t-shirt?"})["output"])
```

## 💻 Code Example — Advanced
```python
# Production: async execution, token accounting, intermediate steps, error handling
import asyncio
from typing import Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.callbacks import get_openai_callback      # token + cost tracking
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
async def get_exchange_rate(pair: str) -> str:
    """Exchange rate for a pair like 'USD INR'."""
    await asyncio.sleep(0)                                         # pretend async I/O
    return "83.2" if pair.upper().replace("/", " ").strip() == "USD INR" else "unknown pair"

def build_executor(prompt: Any) -> AgentExecutor:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=2)   # client-level retries
    tools = [get_exchange_rate]
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, tools=tools,
        max_iterations=6,                                          # step cap
        max_execution_time=40,                                     # seconds cap
        early_stopping_method="force",                             # return a canned message at the limit
        handle_parsing_errors="Invalid format. Use Thought/Action/Action Input or Final Answer.",
        return_intermediate_steps=True,                            # expose (action, observation) pairs
    )

async def ask(executor: AgentExecutor, question: str) -> dict[str, Any]:
    try:
        with get_openai_callback() as cb:                          # counts tokens for this run only
            result = await executor.ainvoke({"input": question})
    except Exception as exc:                                       # network, auth, etc.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    steps = [{"tool": a.tool, "input": a.tool_input, "obs": str(o)[:100]}
             for a, o in result["intermediate_steps"]]
    return {"ok": True, "answer": result["output"], "steps": steps,
            "tokens": cb.total_tokens, "cost_usd": round(cb.total_cost, 6)}
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

state: dict[str, AgentExecutor] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    state["executor"] = build_executor(prompt)         # build once at startup (prompt from the basic example)
    yield

app = FastAPI(lifespan=lifespan)

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/react")
async def react(body: Ask) -> dict:
    result = await ask(state["executor"], body.question)
    if not result["ok"]:
        raise HTTPException(status_code=502, detail=result["error"])
    return result
```
`AgentExecutor` is stateless between calls (state lives in `input` and `agent_scratchpad`), so a single instance is safe to share across requests. Use `astream_events` for token streaming.

---

## 🔗 LangChain / LangGraph Connection
LangChain's `AgentExecutor` is considered the legacy path. The recommended modern route is LangGraph:

```python
from langgraph.prebuilt import create_react_agent as create_graph_agent
graph_agent = create_graph_agent(ChatOpenAI(model="gpt-4o-mini"), [get_exchange_rate])
# result = await graph_agent.ainvoke({"messages": [("user", "USD to INR?")]}, {"recursion_limit": 10})
```
Differences: LangChain's `create_react_agent` uses the text Thought/Action format and works with any LLM; LangGraph's version uses native tool calling (needs a model supporting `bind_tools`), supports memory via checkpointers, human approval, and streaming of state.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Prompt missing required variables
✅ Correct: Include `{tools}`, `{tool_names}`, `{agent_scratchpad}` and `{input}`.

```python
# Wrong — raises "Prompt missing required variables":
PromptTemplate.from_template("Answer: {input}")
# Right: use the full ReAct template (see basic example)
```

❌ Mistake 2: Using `create_react_agent` with models that ignore the format, no parsing error handling
✅ Correct: `handle_parsing_errors=True` plus low temperature.

```python
# Wrong:
AgentExecutor(agent=agent, tools=tools)               # OutputParserException on a bad format
# Right:
AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, max_iterations=6)
```

❌ Mistake 3: Vague tool docstrings, so the agent picks wrong tools. Docstrings are the tool descriptions.

---

## 🧠 Tricky Interview Question

**Q**: "Your LangChain ReAct agent works with gpt-4o-mini but a smaller open-source model keeps raising `OutputParserException: Could not parse LLM output`. Why, and what are your options?"

**Answer**: Text ReAct relies on the model following the exact `Action:` / `Action Input:` format, and weaker models add extra prose, quote inputs wrongly or output both an Action and a Final Answer. Options: set `handle_parsing_errors` so the error goes back as an Observation, add few-shot examples, lower temperature, stop at `\nObservation:` (`llm.bind(stop=["\nObservation"])` is applied by `create_react_agent` by default), or switch to native tool calling (`create_tool_calling_agent` or LangGraph) with a model that supports function calling.

---

## ⚫ Interview Questions + Answers

Q1: Which variables must a ReAct prompt have in LangChain? (Easy)
A1: `tools`, `tool_names`, `input`, `agent_scratchpad`.

Q2: What does `AgentExecutor` do? (Easy)
A2: It runs the agent loop: call the agent, run chosen tools, append observations to the scratchpad, repeat until `AgentFinish` or limits.

Q3: What is `handle_parsing_errors`? (Medium)
A3: When the LLM output does not match the ReAct format, instead of raising it returns the error message (or a custom string) as an observation so the model can retry.

Q4: How do you see the agent's steps? (Medium)
A4: `verbose=True` for console logs, `return_intermediate_steps=True` for structured data, and LangSmith tracing for full production traces.

Q5: LangChain ReAct agent vs LangGraph prebuilt agent? (Hard)
A5: Both implement the pattern. LangChain's is a text-parsing loop in `AgentExecutor` (legacy, simple, model-agnostic). LangGraph's builds a state graph with native tool calling, supports persistence/checkpointing, human-in-the-loop, streaming, subgraphs and multi-agent setups. LangChain recommends LangGraph for new projects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick prototypes and learning
- Model lacks tool calling
- You like the standard ReAct trace

❌ Avoid when:
- You need persistence, approvals or complex flows (use LangGraph)
- Reliability matters most (use native tool calling)

---

## 📊 Visual Diagram
```
 input ─► AgentExecutor
            │   ┌─────────────────────────────────────────┐
            │   │ agent = prompt | llm.bind(stop) | parser │
            │   └──────────────┬──────────────────────────┘
            │                  │ AgentAction(tool, input)  /  AgentFinish
            ▼                  ▼
        loop ◄── run tool ── Observation ─► agent_scratchpad (grows)
            │
            └─ AgentFinish ─► {"output": "..."}
```

---

## 💰 Cost Impact
`{tools}` descriptions and the format instructions are re-sent every iteration (about 250-400 tokens before your question). The scratchpad grows each loop. Text ReAct usually needs more tokens than native tool calling because of the verbose format and Thought text.

Optimize: short tool docstrings, `max_iterations`, `get_openai_callback` to measure, cheaper model, trimming observations inside tools, and prompt caching for the fixed prefix where supported.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create_react_agent | Builds text ReAct agent | ReAct agent बनाने का function |
| AgentExecutor | Runs the agent loop | Agent loop चलाने वाला |
| AgentAction | Decision to call a tool | Tool चलाने का निर्णय |
| AgentFinish | Final result | अंतिम नतीजा |
| agent_scratchpad | Steps so far | अब तक के steps |
| LangSmith | Tracing/observability platform | Tracing platform |

---

## ⚡ 3-Line Summary
English: `create_react_agent` builds a text ReAct agent from an LLM, tools and a prompt with `{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`; `AgentExecutor` runs it. Add `handle_parsing_errors`, `max_iterations` and token tracking. For new projects prefer LangGraph's agent.
Hindi: `create_react_agent` LLM, tools और prompt (`{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`) से text ReAct agent बनाता है; `AgentExecutor` उसे चलाता है। `handle_parsing_errors`, `max_iterations` और token tracking जोड़ो। नए projects में LangGraph का agent चुनो।

---

## ➡️ Next Topic
**300. ReAct Agent** — the agent concept as a whole: components, memory, and when an agent is the right tool.
