---

# 301. AgentExecutor
# हिंदी में: AgentExecutor (LangChain का agent runtime)

---

## 🔵 Simple Definition (English)
`AgentExecutor` is LangChain's runtime that repeatedly calls an agent, runs the tool the agent picks, feeds the result back, and stops on a final answer or a limit. The agent decides; the executor acts, handles errors, enforces `max_iterations` and returns the output.

## 🔵 सरल परिभाषा (Hindi)
`AgentExecutor` LangChain का runtime है जो बार-बार agent को call करता है, agent का चुना tool चलाता है, result वापस देता है, और final answer या limit पर रुकता है। Agent निर्णय लेता है; executor काम करता है, errors संभालता है, `max_iterations` लागू करता है और output लौटाता है।

---

## 🔴 Problem it Solves
An agent object only produces the next decision (`AgentAction` or `AgentFinish`). Someone must run the loop, call tools, catch failures, stop runaway loops and expose intermediate steps. Writing this each time (note 298) is error-prone, so `AgentExecutor` packages it.

## 🔴 यह क्यों बना? (Hindi)
Agent object सिर्फ़ अगला निर्णय (`AgentAction` या `AgentFinish`) देता है। Loop चलाना, tools call करना, failures पकड़ना, बेकाबू loops रोकना और intermediate steps दिखाना किसी और को करना पड़ता है। हर बार यह लिखना गलती-प्रवण है, इसलिए `AgentExecutor` इसे package करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → executor.invoke({"input": q}) starts with intermediate_steps = []
Step 2 → Calls agent.plan(input, intermediate_steps)  (LLM decides)
Step 3 → Result is AgentFinish? -> return output
Step 4 → Result is AgentAction(tool, tool_input)? -> look up tool by name
Step 5 → Run tool (errors handled per handle_tool_error); get observation
Step 6 → intermediate_steps.append((action, observation))
Step 7 → Check iteration/time limits; loop back to step 2
Step 8 → On limit: early_stopping_method "force" (canned message) or "generate" (one last LLM call)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → executor.invoke({"input": q}) intermediate_steps = [] से शुरू
Step 2 → agent.plan(input, intermediate_steps) call (LLM निर्णय लेता है)
Step 3 → नतीजा AgentFinish? -> output लौटाओ
Step 4 → नतीजा AgentAction(tool, tool_input)? -> नाम से tool ढूँढो
Step 5 → Tool चलाओ (errors handle_tool_error के अनुसार); observation लो
Step 6 → intermediate_steps.append((action, observation))
Step 7 → iteration/time limits check; Step 2 पर वापस
Step 8 → Limit पर: early_stopping_method "force" (तैयार संदेश) या "generate" (एक आख़िरी LLM call)
```

---

## 🟡 Real World Example
**Tariff Classification System**: the executor wraps `search_hs_codes`, `get_tariff_rate`, `calculator`. Settings: `max_iterations=6`, `max_execution_time=30`, `handle_parsing_errors=True`, `return_intermediate_steps=True`. The API returns the answer plus the tool trail so compliance officers can audit how a rate was found.

**Zomato AI**: a support executor stops after 4 iterations and hands over to a human agent if no final answer.

## 🟡 Real Example Hindi mein
**Tariff System**: executor `search_hs_codes`, `get_tariff_rate`, `calculator` को wrap करता है। Settings: `max_iterations=6`, `max_execution_time=30`, `handle_parsing_errors=True`, `return_intermediate_steps=True`। API जवाब के साथ tool trail भी लौटाती है ताकि compliance officer audit कर सके कि rate कैसे मिला।

**Zomato AI**: support executor 4 iterations के बाद रुककर बिना जवाब के इंसान को सौंप देता है।

---

## 💻 Code Example — Basic
```python
# AgentExecutor with a tiny deterministic "fake" agent so it runs without an API key.
# Requires: pip install langchain langchain-core
from langchain.agents import AgentExecutor                      # runtime
from langchain_core.agents import AgentAction, AgentFinish      # agent decision types
from langchain_core.runnables import RunnableLambda             # wrap a function as a runnable
from langchain_core.tools import tool                           # tool decorator

@tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for an HS code like 6109.10."""
    return {"6109.10": "20%"}.get(hs_code, "unknown")

def plan(inputs: dict) -> AgentAction | AgentFinish:
    """Fake brain: call the tool once, then finish. inputs has 'input' and 'intermediate_steps'."""
    steps = inputs["intermediate_steps"]                        # list[(AgentAction, observation)]
    if not steps:                                               # nothing done yet -> act
        return AgentAction(tool="get_tariff_rate", tool_input={"hs_code": "6109.10"}, log="calling tool")
    observation = steps[-1][1]                                  # last tool result
    return AgentFinish(return_values={"output": f"Duty is {observation}"}, log="done")

agent = RunnableLambda(plan)                                    # executor accepts any Runnable agent
executor = AgentExecutor(agent=agent, tools=[get_tariff_rate],
                         max_iterations=3, return_intermediate_steps=True, verbose=False)

result = executor.invoke({"input": "Duty on cotton shirts?"})
print(result["output"])                                         # Duty is 20%
print(result["intermediate_steps"][0][0].tool)                  # get_tariff_rate
```

## 💻 Code Example — Advanced
```python
# Production: real LLM agent, limits, callbacks, async, error handling
import asyncio, time
from typing import Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

class StepLogger(BaseCallbackHandler):
    """Collects tool latency; plug in metrics/tracing here."""
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._t0: float = 0.0
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        self._t0 = time.perf_counter()
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        self.events.append({"tool_ms": round((time.perf_counter() - self._t0) * 1000), "obs": str(output)[:60]})
    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self.events.append({"error": type(error).__name__})

@tool(handle_tool_error=True)                                   # ToolException text becomes the observation
async def search_hs_codes(query: str) -> str:
    """Find an HS code from a product description."""
    await asyncio.sleep(0)
    return "6109.10 T-shirts, cotton"

def build(prompt: PromptTemplate) -> AgentExecutor:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=2)
    tools = [search_hs_codes]
    return AgentExecutor(
        agent=create_react_agent(llm, tools, prompt),
        tools=tools,
        max_iterations=6,                                       # loop cap
        max_execution_time=30,                                  # wall-clock cap (seconds)
        early_stopping_method="force",                          # default; "generate" is only for some agent types
        handle_parsing_errors=True,                             # bad format -> observation
        return_intermediate_steps=True,
    )

async def run(executor: AgentExecutor, question: str) -> dict[str, Any]:
    logger = StepLogger()
    try:
        out = await executor.ainvoke({"input": question}, config={"callbacks": [logger]})
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    stopped = out["output"].startswith("Agent stopped due to")  # canned "force" message
    return {"ok": not stopped, "answer": out["output"], "events": logger.events,
            "steps": len(out["intermediate_steps"])}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI()

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/agent")
async def ask(body: Ask, request: Request) -> dict:
    executor: AgentExecutor = request.app.state.executor       # built once in lifespan
    result = await run(executor, body.question)
    if not result["ok"]:
        raise HTTPException(status_code=422 if "stopped" in str(result.get("answer", "")) else 502,
                            detail=result.get("error") or "agent did not finish")
    return result
```
Stream progress with `executor.astream_events(..., version="v2")` and `StreamingResponse` so users see tool names as they run.

---

## 🔗 LangChain / LangGraph Connection
`AgentExecutor` is the classic LangChain runtime (still supported but LangChain now recommends LangGraph for new agents). Mapping to LangGraph:

| AgentExecutor | LangGraph |
|---|---|
| `max_iterations` | `recursion_limit` in config |
| `intermediate_steps` | `messages` state (AIMessage tool_calls + ToolMessage) |
| `handle_parsing_errors` | `ToolNode(handle_tool_errors=True)` |
| `return_intermediate_steps` | stream `updates` / read state |
| memory param | checkpointer + `thread_id` |

```python
# Migration target:
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [search_hs_codes])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ignoring the "stopped" case
✅ Correct: Detect it and handle gracefully.

```python
# Wrong — shows "Agent stopped due to iteration limit or time limit." to users:
return out["output"]
# Right:
if out["output"].startswith("Agent stopped"): return fallback_or_escalate()
```

❌ Mistake 2: Building a new executor for every request
✅ Correct: Create once; it is stateless between invocations.

```python
# Wrong:
@app.post("/a")
async def a(): return await build(prompt).ainvoke(...)
# Right: executor created in lifespan and reused
```

❌ Mistake 3: `verbose=True` in production (prints prompts and user data to logs). Use callbacks/tracing with redaction.

---

## 🧠 Tricky Interview Question

**Q**: "You set `max_iterations=5` but the request took 3 minutes. How?"

**Answer**: `max_iterations` counts loop cycles, not time. One cycle can include slow tool calls, LLM retries (`max_retries` on the model with backoff), or a single tool running a long time. Add `max_execution_time`, per-tool timeouts, LLM `timeout`, and an overall `asyncio.wait_for` at the API layer. Also check for tools that themselves call LLMs or sub-agents with their own loops.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an agent and an `AgentExecutor`? (Easy)
A1: The agent decides the next step. The executor runs the loop: calls the agent, executes tools, handles errors and limits.

Q2: Name three `AgentExecutor` parameters. (Easy)
A2: `max_iterations`, `max_execution_time`, `handle_parsing_errors`, `return_intermediate_steps`, `early_stopping_method`, `verbose`.

Q3: What does `return_intermediate_steps` do? (Medium)
A3: Adds `intermediate_steps` to the result: a list of `(AgentAction, observation)` for debugging, UI trails and audits.

Q4: How do you handle a tool raising an exception? (Medium)
A4: Use `@tool(handle_tool_error=True)` with `ToolException`, or catch inside the tool and return an error string. Otherwise the exception propagates and fails the run.

Q5: Why is LangChain moving users from `AgentExecutor` to LangGraph? (Hard)
A5: AgentExecutor is a fixed loop with limited control. LangGraph models agents as graphs with explicit state, persistence (checkpointers), human-in-the-loop interrupts, streaming, branching and multi-agent composition, which production systems need.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Maintaining existing LangChain agents
- Simple single-agent loops
- Quick prototypes with `verbose=True`

❌ Avoid when:
- You need approvals, persistence, or branching (LangGraph)
- You require full control of the loop

---

## 📊 Visual Diagram
```
 invoke({"input": q})
        │
        ▼
 ┌───────────── AgentExecutor ───────────────┐
 │ intermediate_steps = []                   │
 │ loop:                                     │
 │   decision = agent.plan(q, steps)         │
 │   AgentFinish ─────────────► return       │
 │   AgentAction ─► tool.run ─► observation  │
 │   steps.append((action, observation))     │
 │   limits: iterations / time ──► stop      │
 └───────────────────────────────────────────┘
```

---

## 💰 Cost Impact
Each loop is one LLM call whose prompt includes all `intermediate_steps` rendered into the scratchpad, so tokens grow every iteration. `early_stopping_method="generate"` (where supported) adds one more LLM call at the limit; `"force"` adds none. `max_retries` on the LLM can silently multiply calls on rate-limit errors.

Optimize: tight `max_iterations`, short tool outputs, small model, caching tool results, and callbacks (`get_openai_callback`) to track tokens per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AgentExecutor | Runs the agent loop | Agent loop चलाने वाला |
| max_iterations | Loop cap | Loop की सीमा |
| max_execution_time | Time cap in seconds | समय सीमा |
| intermediate_steps | (action, observation) list | Steps की list |
| early_stopping_method | What to do at the limit | Limit पर क्या करें |
| Callback handler | Hook for events | Events पर चलने वाला hook |

---

## ⚡ 3-Line Summary
English: `AgentExecutor` runs the loop: ask the agent, run the tool, store the observation, repeat until finish or limit. Set `max_iterations`, `max_execution_time`, `handle_parsing_errors` and `return_intermediate_steps`. For new work, LangGraph is the recommended runtime.
Hindi: `AgentExecutor` loop चलाता है: agent से पूछो, tool चलाओ, observation रखो, finish या limit तक दोहराओ। `max_iterations`, `max_execution_time`, `handle_parsing_errors` और `return_intermediate_steps` सेट करो। नए काम के लिए LangGraph recommended है।

---

## ➡️ Next Topic
**302. Agent Scratchpad** — the working memory of an agent loop and how it is rendered into the prompt.
