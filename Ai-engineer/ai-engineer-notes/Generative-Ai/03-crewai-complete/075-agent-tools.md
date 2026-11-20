---

# 75. Agent tools
# हिंदी में: Agent के tools
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
Tools are functions an agent may call to get facts or take actions. In CrewAI you create them with the `@tool` decorator (fast) or by subclassing `BaseTool` with an `args_schema` (typed, validated). The docstring/description is what the LLM reads to decide when to call.

## 🔵 सरल परिभाषा (Hindi)
Tools वे functions हैं जिन्हें agent facts पाने या actions लेने के लिए call कर सकता है। CrewAI में आप `@tool` decorator (तेज़) या `args_schema` वाले `BaseTool` subclass (typed, validated) से tool बनाते हैं। LLM docstring/description पढ़कर तय करता है कि कब call करना है।

---

## 🔴 Problem it Solves
LLMs cannot look up live data or change systems. They also hallucinate numbers. Tools give grounded answers (a real duty rate) and safe, auditable side effects.

## 🔴 यह क्यों बना? (Hindi)
LLM live data नहीं देख सकते और सिस्टम नहीं बदल सकते। वे numbers भी गढ़ देते हैं। Tools असली जवाब (असली duty rate) और सुरक्षित, audit हो सकने वाले side effects देते हैं।

---

## 🟢 How it Works

```
Step 1 -> Tool name + description + arg schema are added to the agent prompt
Step 2 -> LLM emits Action: tool_name and Action Input: {json}
Step 3 -> CrewAI validates args against the schema and runs the tool
Step 4 -> Return value (string) becomes the Observation
Step 5 -> Identical calls may be served from the agent cache (cache=True default)
Step 6 -> Loop continues until Final Answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Tool का नाम + description + arg schema agent prompt में जुड़ते हैं
Step 2 -> LLM Action: tool_name और Action Input: {json} देता है
Step 3 -> CrewAI args को schema से validate करके tool चलाता है
Step 4 -> Return value (string) Observation बनती है
Step 5 -> एक जैसी calls agent cache से आ सकती हैं (cache=True default)
Step 6 -> Final Answer तक loop चलता है
```

---

## 🟡 Real World Example
**Tariff Agent**: `get_duty_rate(hs_code)` reads the tariff DB; `LandedCostTool(value, rate)` computes value x (1 + rate/100). Offline we confirmed `LandedCostTool().run(value=1000, rate=10)` returns 1100.0 and the schema marks both args required.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `get_duty_rate(hs_code)` tariff DB पढ़ता है; `LandedCostTool(value, rate)` value x (1 + rate/100) निकालता है। Offline हमने पुष्टि की कि `LandedCostTool().run(value=1000, rate=10)` 1100.0 देता है और schema में दोनों args required हैं।

---

## 💻 Code Example — Basic
```python
# tools_basic.py - three ways to give an agent a tool: @tool, BaseTool subclass, tool on Task
from pydantic import BaseModel, Field                # schema for BaseTool arguments
from crewai import Agent, Task, Crew, LLM            # core
from crewai.tools import tool, BaseTool              # both tool styles

@tool("get_duty_rate")                               # style 1: decorator, fastest
def get_duty_rate(hs_code: str) -> str:              # type hints become the args schema
    """Return duty percent for an HS code, or 'unknown'."""   # description the LLM reads
    return {"8517": "0.0", "6403": "10.0"}.get(hs_code, "unknown")

class LandedCostInput(BaseModel):                    # style 2: explicit schema
    value: float = Field(description="Goods value in USD")    # described fields help the LLM
    rate: float = Field(description="Duty percent")

class LandedCostTool(BaseTool):                      # class-based tool
    name: str = "landed_cost"                        # tool name
    description: str = "Goods value plus duty amount."   # when to use it
    args_schema: type[BaseModel] = LandedCostInput   # validated before _run
    def _run(self, value: float, rate: float) -> str:    # sync body
        return str(round(value * (1 + rate / 100), 2))   # compute

llm = LLM(model="gpt-4o-mini")                       # real run needs a key
agent = Agent(role="Analyst", goal="Compute landed cost", backstory="Precise.", llm=llm,
              tools=[get_duty_rate, LandedCostTool()])    # agent-level tools: available on all its tasks
task = Task(description="Landed cost of 1000 USD of HS {hs}.", expected_output="A number.", agent=agent)
print(Crew(agents=[agent], tasks=[task]).kickoff(inputs={"hs": "6403"}).raw)
```
Verified: tools execute directly (`get_duty_rate.run(hs_code='6403')` returned 10.0) and the crew ran offline with a fake LLM. A real model deciding to call these tools: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# tools_api.py - production tool: timeout, error string back to the LLM, FastAPI wrapper
import httpx                                         # HTTP client for a real tariff service
from crewai import Agent, Task, Crew, LLM            # core
from crewai.tools import tool                        # decorator
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app

@tool("tariff_lookup")                               # tool name
def tariff_lookup(hs_code: str) -> str:              # typed
    """Look up the duty percent for an HS code from the tariff service."""
    if not hs_code.isdigit():                        # validate LLM-produced input
        return "ERROR: hs_code must be digits only"  # return text, do not raise: LLM can self-correct
    try:
        r = httpx.get(f"https://tariff.internal.example/rate/{hs_code}", timeout=5.0)  # hard timeout
        r.raise_for_status()                         # 4xx/5xx -> exception
        return r.text                                # plain text back to the agent
    except httpx.HTTPError as exc:                   # network/HTTP problems
        return f"ERROR: tariff service unavailable ({type(exc).__name__})"   # observation, not crash

class Q(BaseModel):                                  # body
    hs: str                                          # HS code

@app.post("/lookup")                                 # endpoint
async def lookup(q: Q) -> dict[str, str]:            # typed
    agent = Agent(role="Analyst", goal="Report duty", backstory="Careful.",
                  llm=LLM(model="gpt-4o-mini"), tools=[tariff_lookup], max_iter=4)
    task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # last-resort handler
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}
```
Verified with `TestClient` and the offline fake (the fake LLM did not call the network tool, so the `httpx` branch and the internal URL `tariff.internal.example` are illustrative: not run). Key design: validate input, set a timeout, and return an `ERROR: ...` string instead of raising so the agent can recover.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Define a tool | `@tool` (LangChain) / any callable in ToolNode | `@tool` or `BaseTool` subclass | `@function_tool` | Python function / `FunctionTool` |
| Arg schema | From type hints / Pydantic | From hints or `args_schema` (Pydantic) | From hints (auto JSON schema) | From hints |
| Tool scope | Per graph/node binding | Per agent or per task | Per agent | Per agent |
| MCP tools | Via adapters | Via MCP integration (check docs) | Built-in MCP classes | Via autogen-ext MCP |
| Result caching | DIY | Built-in agent cache | DIY | DIY |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Tool without a docstring/description.
✅ Correct: Write a clear one-line purpose; the LLM chooses tools from it.

❌ Mistake 2: Raising exceptions for expected failures.
✅ Correct: Return a descriptive error string so the agent can retry or answer unknown.

❌ Mistake 3: Trusting LLM-provided arguments.
✅ Correct: Validate in the tool (`isdigit`, ranges, allow-lists) and authorise inside tool code.

---

## 🧠 Tricky Interview Question
Your tool has side effects (sends an email). The agent calls it twice. Why and how do you prevent duplicates?

Answer: Agents retry on ambiguity, and CrewAI's cache only helps identical read-only calls conceptually; a side-effecting tool must not rely on it. Make the tool idempotent (idempotency key such as hash of recipient+subject), return a clear 'already sent' observation, require confirmation (`human_input`) for destructive actions, and log every call. Also reduce `max_iter` so a confused loop cannot repeat many times.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Two ways to define a CrewAI tool?
A1: `@tool("name")` on a function with type hints and docstring, or subclass `BaseTool` with `name`, `description`, `args_schema` and `_run`.

Q2: [Medium] Why use `args_schema`?
A2: It documents and validates arguments with Pydantic so malformed LLM calls fail early with a clear error.

Q3: [Hard] Agent-level vs task-level tools?
A3: Agent-level tools are available on all its tasks; task-level scopes tools to one task (verify replace-vs-extend in the docs for your version).

Q4: [Hard] How to keep tool output from blowing up context?
A4: Truncate/summarise in the tool, return IDs plus short fields, paginate, and rely on `respect_context_window` as a safety net, not a design.

Q5: [System Design] Expose 30 internal APIs as tools safely?
A5: Group into MCP/tool servers per domain, per-agent allow-lists, auth done server-side with the caller's identity, timeouts and rate limits, audit logs, read vs write separation with human approval for writes.

---

## 💰 Cost Impact
Formula: tool schema tokens are added to every iteration: schema tokens x iterations. Approximate guide: 100-300 tokens per tool (measure with your tokenizer). Tool outputs are appended to the scratchpad and resent every later iteration, so large outputs are the biggest hidden cost. Tips: few tools per agent, short descriptions, small outputs.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Need live or private data
- Need deterministic computation (math, lookups)
- Need controlled side effects

❌ Avoid when:
- The model already knows the answer reliably and stakes are low
- Tool returns huge unfiltered payloads

---

## 📊 Visual Diagram
```
  Agent prompt: [name, description, args schema]
        |
        v
   LLM --Action: get_duty_rate {"hs_code":"6403"}--> CrewAI
        ^                                              |
        |                                     validate args (schema)
   Observation: "10.0"                                 |
        ^                                              v
        +-----------------------------------  Tool code (DB/API)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool | Function the agent can call | टूल |
| args_schema | Pydantic model describing arguments | आर्ग्युमेंट स्कीमा |
| Observation | Tool result fed back to LLM | अवलोकन |
| Idempotent | Safe to repeat with same effect | दोहराने पर सुरक्षित |
| Timeout | Max wait before giving up | समय-सीमा |
| Cache | Reuse results of identical calls | कैश |

---

## ⚡ 3-Line Summary
English: Tools ground agents in real data and actions. Use @tool for speed, BaseTool for typed schemas, and always validate inputs, set timeouts and return error strings. Tool schemas cost tokens every iteration.
Hindi: Tools agents को असली data और actions से जोड़ते हैं। तेज़ी के लिए @tool, typed schema के लिए BaseTool; inputs validate करें, timeouts रखें और error strings लौटाएँ। Tool schemas हर iteration में tokens खर्च करते हैं।

---

## ➡️ Next Topic
**076. Agent llm config** - choosing and tuning the model behind each agent.

---
