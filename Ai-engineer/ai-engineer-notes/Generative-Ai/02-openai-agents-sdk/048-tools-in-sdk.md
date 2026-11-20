---

# 48. Tools in SDK
# हिंदी में: SDK में Tools (सभी प्रकार)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline. Function tools, `as_tool` and `tool_use_behavior` were really executed with a scripted model; hosted tools (`FileSearchTool`, `WebSearchTool`) were only attached and listed, not executed (they run on OpenAI's side and need an API key). MCP tools are covered in the MCP notes.

---

## 🔵 Simple Definition (2-3 lines)
A tool is a capability the agent can call. The SDK has four families: (1) function tools (your Python functions via `@function_tool`), (2) hosted tools run by OpenAI (`WebSearchTool`, `FileSearchTool`, `ComputerTool`, and others), (3) agents as tools (`agent.as_tool(...)`), and (4) tools exposed by MCP servers.

## 🔵 सरल परिभाषा (Hindi)
Tool वह क्षमता है जिसे agent call कर सकता है। SDK में चार परिवार हैं: (1) function tools (`@function_tool` से आपके Python functions), (2) OpenAI द्वारा चलने वाले hosted tools (`WebSearchTool`, `FileSearchTool`, `ComputerTool` आदि), (3) agents as tools (`agent.as_tool(...)`), और (4) MCP servers के tools।

---

## 🔴 Problem it Solves
An LLM alone only produces text; it cannot look up a duty rate, read your files or click a button. Tools let it act. The SDK turns Python functions into JSON-schema tool definitions, runs the call loop (model asks, SDK executes, result goes back) and handles errors, so you write business logic, not plumbing.

## 🔴 यह क्यों बना? (Hindi)
अकेला LLM सिर्फ़ text बनाता है; वह duty rate नहीं देख सकता, आपकी files नहीं पढ़ सकता, button नहीं दबा सकता। Tools उसे कार्रवाई करने देते हैं। SDK Python functions को JSON-schema tool definitions में बदलता है, call loop चलाता है (model माँगता है, SDK चलाता है, result वापस जाता है) और errors संभालता है, ताकि आप business logic लिखें, plumbing नहीं।

---

## 🟢 How it Works

```
Step 1 -> Define tools: @function_tool / FileSearchTool() /
          WebSearchTool() / other_agent.as_tool() / MCP server
Step 2 -> Agent(tools=[...]) -> SDK sends all tool schemas to model
Step 3 -> Model returns a tool call (name + JSON args)
Step 4 -> Function tool: SDK validates args, runs YOUR code
          Hosted tool: OpenAI runs it, result arrives in the response
Step 5 -> Output goes back to the model as a tool result item
Step 6 -> Loop until final answer (or tool_use_behavior stops it)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Tools बनाओ: @function_tool / FileSearchTool() /
          WebSearchTool() / other_agent.as_tool() / MCP server
Step 2 -> Agent(tools=[...]) -> SDK सारे tool schemas model को भेजता है
Step 3 -> Model tool call लौटाता है (name + JSON args)
Step 4 -> Function tool: SDK args validate करके आपका code चलाता है
          Hosted tool: OpenAI चलाता है, result response में आता है
Step 5 -> Output tool result item बनकर model को वापस जाता है
Step 6 -> Final answer तक loop (या tool_use_behavior रोक दे)
```

**Verified in 0.24.0:** `function_tool(...)` accepts `name_override`, `description_override`, `failure_error_function`, `strict_mode`, `is_enabled`, `needs_approval`, `timeout`, `timeout_behavior`; `Agent(..., tools=[...], tool_use_behavior=...)`. In our run the model was shown exactly: `FunctionTool:hs_duty`, `FunctionTool:ask_duty_helper`, `FileSearchTool:file_search`, `WebSearchTool:web_search`.

**Default error behaviour (observed):** when a function tool raises (we raised `ValueError('code not found')`), the model received a generic string, `An error occurred while running the tool. Please try again.`, and the run continued. The exception text is NOT leaked to the model by default. Pass `failure_error_function` to customise.

**`tool_use_behavior`:** `"run_llm_again"` (default), `"stop_on_first_tool"` (we saw the tool output become `final_output` with only 1 LLM call), `StopAtTools(stop_at_tool_names=[...])`, or a custom function.

**Hindi नोट:** Tool चुनने का नियम: अपना logic हो तो function tool; OpenAI के managed search/files हों तो hosted tool; किसी specialist agent को delegate करना हो तो `as_tool`; बाहरी standard server हो तो MCP।

---

## 🟡 Real World Example
**Tariff Agent.** `hs_duty` is a function tool hitting your tariff DB; `FileSearchTool` searches uploaded customs circulars; `WebSearchTool` checks recent notifications; a `Duty Helper` sub-agent exposed with `as_tool` summarises long legal text. One agent, four tool families, one loop.

**Code Agent:** function tools for `read_file`, `run_tests`, and an MCP server for the issue tracker.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `hs_duty` आपकी tariff DB पर चलने वाला function tool है; `FileSearchTool` अपलोड की गई customs circulars खोजता है; `WebSearchTool` हाल की notifications देखता है; `as_tool` से लगाया `Duty Helper` sub-agent लंबे कानूनी text का सार बनाता है। एक agent, चार tool families, एक loop।

**Code Agent:** `read_file`, `run_tests` function tools, और issue tracker के लिए MCP server।

---

## 💻 Code Example — Basic
Runs offline. One function tool executes for real; an agent-as-tool and two hosted tools are attached and listed (hosted tools were not executed).

```python
# Basic: the tool families in the SDK, with a function tool actually executed (offline)
import asyncio                                           # async runner
from agents import (Agent, Runner, function_tool, FileSearchTool, WebSearchTool)  # SDK tool types
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool                                           # family 1: function tool (your Python code)
def hs_duty(code: str) -> str:                           # type hints -> JSON schema
    """Return the duty percent for an HS code."""       # docstring -> description for the LLM
    return {"6109.10": "20%", "6203.42": "12%"}.get(code, "unknown")  # tiny local lookup table

async def main() -> None:
    sub = Agent(name="Duty Helper", instructions="Answer duty questions.",
                model=ScriptedModel([[assistant_message("Helper says 20%")]]))  # family 3 target
    helper_tool = sub.as_tool(tool_name="ask_duty_helper",
                              tool_description="Delegate duty questions")       # family 3: agent AS a tool
    model = ScriptedModel([[function_call("hs_duty", {"code": "6109.10"}, call_id="c1")],
                           [assistant_message("Duty on 6109.10 is 20%.")]])
    agent = Agent(name="Tariff Agent", instructions="Use tools.", model=model,
                  tools=[hs_duty, helper_tool,
                         FileSearchTool(vector_store_ids=["vs_demo"]),  # family 2: hosted tool (runs on OpenAI side; not executed here)
                         WebSearchTool()])               # family 2: hosted tool
    res = await Runner.run(agent, "Duty on 6109.10?")    # run: only hs_duty is actually invoked
    print("final:", res.final_output)
    print("tools shown to model:", [type(t).__name__ + ":" + getattr(t, "name", "") for t in model.calls[0].tools])
    # a 4th family, MCP servers (Agent(mcp_servers=[...])), is covered in the MCP notes

asyncio.run(main())
```

## 💻 Code Example — Advanced
Pydantic-typed async tool with a timeout, a tool error the model sees safely, agent-as-tool, and `tool_use_behavior='stop_on_first_tool'`, behind FastAPI. Offline.

```python
# Advanced: tool errors, tool_use_behavior, agent-as-tool, FastAPI (offline)
import asyncio                                           # sleeps
from fastapi import FastAPI, HTTPException               # web
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel, Field                    # schemas
from agents import Agent, Runner, function_tool, ModelBehaviorError  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

class DutyQuery(BaseModel):                              # pydantic model as a tool argument (rich schema)
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code like 6109.10")
    country: str = Field(default="IN", description="2-letter import country")

@function_tool(timeout=2.0)                              # per-tool timeout (seconds); verified param in 0.24.0
async def duty(q: DutyQuery) -> str:                     # async tools are first-class
    """Look up import duty for an HS code and country."""
    await asyncio.sleep(0)                               # pretend I/O
    if q.hs_code == "0000.00":
        raise ValueError("code not found")               # becomes an error STRING for the model by default
    return f"{q.country}:{q.hs_code}=20%"

def build(model, behavior="run_llm_again") -> Agent:     # tool_use_behavior controls what happens after tools run
    helper = Agent(name="Summariser", instructions="Summarise.", model=ScriptedModel([[assistant_message("short summary")]]))
    return Agent(name="Tariff Agent", instructions="Use tools.", model=model,
                 tools=[duty, helper.as_tool(tool_name="summarise", tool_description="Summarise text")],
                 tool_use_behavior=behavior)             # "run_llm_again" (default) | "stop_on_first_tool" | StopAtTools | callable

app = FastAPI()

class Ask(BaseModel):
    question: str
    code: str = "6109.10"

@app.post("/ask")
async def ask(b: Ask) -> dict:
    model = ScriptedModel([[function_call("duty", {"q": {"hs_code": b.code}}, call_id="c1")],
                           [assistant_message("Done.")]])
    try:
        res = await Runner.run(build(model), b.question, max_turns=5)
    except ModelBehaviorError as exc:                    # model sent invalid args / unknown tool
        raise HTTPException(status_code=502, detail=str(exc)[:120]) from exc
    tool_outputs = [i.output for i in res.new_items if i.type == "tool_call_output_item"]  # what the model saw
    return {"answer": res.final_output, "tool_outputs": tool_outputs}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/ask", json={"question": "q"}).json())                    # happy path
    print(c.post("/ask", json={"question": "q", "code": "0000.00"}).json())  # tool raised: model sees an error string, run continues
    m = ScriptedModel([[function_call("duty", {"q": {"hs_code": "6109.10"}}, call_id="c")]])
    r = asyncio.run(Runner.run(build(m, "stop_on_first_tool"), "q"))        # no second LLM call
    print("stop_on_first_tool ->", r.final_output, "| llm calls:", len(m.calls))
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Define a custom tool | Plain function + `ToolNode` / `@tool` | `@tool` / BaseTool subclass | `@function_tool` / `FunctionTool` | Function wrapped in `FunctionTool` |
| Hosted/provider tools | Via model bindings (e.g. provider search) | Via tool packages (crewai-tools) | `WebSearchTool`, `FileSearchTool`, `ComputerTool`... | Via model client built-ins |
| Agent as a tool | Subgraph/node | Delegation between agents | `agent.as_tool(...)` | `AgentTool` |
| MCP support | `langchain-mcp-adapters` | MCP adapter | Built-in MCP server classes | `McpWorkbench` |
| Stop after tool | Conditional edges | Task/agent config | `tool_use_behavior` | Reflect on tool use / termination conditions |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Writing vague tool docstrings like 'does stuff'.
✅ Correct: The docstring is the description the LLM reads. Say what it does, inputs and when to use it.

❌ Mistake 2: Returning huge raw JSON from a tool.
✅ Correct: Return only the fields the model needs; big outputs cost tokens every later turn.

❌ Mistake 3: Letting tools raise and assuming the model sees the message.
✅ Correct: By default it sees a generic error; use `failure_error_function` to give safe, actionable text.

❌ Mistake 4: Giving the agent 30 overlapping tools.
✅ Correct: Fewer, clearer tools (or route with handoffs); tool-choice accuracy drops as the list grows.

❌ Mistake 5: Expecting a hosted tool to run locally.
✅ Correct: Hosted tools execute on OpenAI's servers and need a Responses-API OpenAI model.

---

## 🧠 Tricky Interview Question
Your agent has `hs_duty` and `web_search`. For one query it calls web search for a stable duty rate that is in your DB, increasing cost and latency. How do you make it prefer the DB?

**Answer:** Fix it at several layers rather than hoping. (1) Improve tool descriptions: say `hs_duty` is the authoritative source for current duty rates and `web_search` is only for recent notifications. (2) Put the routing rule in the instructions. (3) Order and prune: remove web search from agents that do not need it, or split into a lookup agent and a research agent with a handoff. (4) Use `ModelSettings(tool_choice='hs_duty')` for the first turn when the query type is known, or classify first and call different agents. (5) Add a guardrail or `is_enabled` callable that hides web search unless the DB returned 'unknown'. (6) Measure with traces: count web_search calls per run and alert on drift.

---

## ⚫ Interview Questions + Answers

**Q1:** Name the tool families in the Agents SDK.

**A1:** Function tools, hosted tools (web search, file search, computer, etc.), agents as tools, and MCP server tools.

**Q2:** How does `@function_tool` build the schema?

**A2:** From type hints and the docstring (descriptions per argument); pydantic models give richer schemas. The first `RunContextWrapper` parameter is excluded.

**Q3:** What happens when a function tool raises?

**A3:** By default the model gets a generic error string and the run continues; customise with `failure_error_function`. We observed the generic text.

**Q4:** Agent-as-tool vs handoff?

**A4:** As-tool: the manager keeps control, calls the sub-agent like a function and gets output back. Handoff: control transfers to another agent which continues the conversation.

**Q5:** Design the tool layer for a production Tariff Agent.

**A5:** Few clearly named tools with typed pydantic args; timeouts and retries inside tools; idempotent reads; authorization from the context not the LLM; truncate outputs; `needs_approval` for risky writes; per-tool metrics via hooks and traces; separate agents per domain exposed with `as_tool`; eval the tool-choice accuracy before shipping.

---

## 💰 Cost Impact
Each tool adds its schema to every request: roughly 50-300 input tokens per tool depending on description length (estimate; measure with your provider's token counter). Tool outputs are re-sent on later turns, so long outputs multiply cost. Hosted tools have their own per-call fees from OpenAI (see their pricing page; verify before budgeting). Tips: prune tools per agent, shorten outputs, use `stop_on_first_tool` when the tool output is the answer (saves one LLM call), and cache deterministic lookups.

---

## 🔷 When to Use
✅ Use when:
- The model must act on systems or data it cannot know
- You want typed, validated arguments
- You need provider-managed search or file retrieval
- Splitting a big job into specialist agents

❌ Avoid when:
- A single deterministic step you can code directly (no LLM needed)
- Dozens of overlapping tools in one agent
- Tools whose side effects are irreversible without approval

---

## 📊 Visual Diagram
```
             +-----------------------------+
 user -----> |           Agent             |
             |  instructions + tools=[..]  |
             +--------------+--------------+
                            | tool schemas
                            v
                       +---------+     tool call(name,args)
                       |  LLM    |----------------------+
                       +---------+                      |
                            ^                           v
                  tool result|        +------------------+------------------+
                            |        | function tool -> YOUR python code    |
                            |        | hosted tool   -> OpenAI executes     |
                            +--------| agent.as_tool -> sub-agent run       |
                                     | MCP tool      -> MCP server          |
                                     +--------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function tool | Your Python function exposed to the LLM | LLM को दिया गया आपका Python function |
| Hosted tool | Tool executed by OpenAI's servers | OpenAI के servers पर चलने वाला tool |
| Agent as tool | Sub-agent called like a function | function की तरह call होने वाला sub-agent |
| tool_use_behavior | Rule for what happens after tools run | tools के बाद क्या हो, इसका नियम |
| failure_error_function | Builds the error text the model sees | model को दिखने वाला error text बनाता है |

---

## ⚡ 3-Line Summary
English: Tools come in four families: function tools, hosted tools, agents as tools and MCP tools.
The SDK builds the schema, validates arguments, runs the loop and hides raw exceptions by default.
Keep tools few, well described and typed, and choose `tool_use_behavior` deliberately.

Hindi: Tools चार परिवारों में आते हैं: function tools, hosted tools, agents as tools और MCP tools।
SDK schema बनाता है, arguments validate करता है, loop चलाता है और default रूप से raw exceptions छिपाता है।
Tools कम, अच्छी तरह वर्णित और typed रखें, और `tool_use_behavior` सोच-समझकर चुनें।

---

## ➡️ Next Topic
**#49 FunctionTool** - the decorator is sugar; next we open the `FunctionTool` class itself: schema, strict mode, invocation contract, timeouts and dynamic enabling.

---
