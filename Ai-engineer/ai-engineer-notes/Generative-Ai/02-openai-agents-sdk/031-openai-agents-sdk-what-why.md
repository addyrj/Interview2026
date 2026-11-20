---

# 31. OpenAI Agents SDK — What + Why
# हिंदी में: OpenAI Agents SDK — क्या है और क्यों
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Code was run offline with `agents.testing.ScriptedModel` (a scripted fake model, no API key). Token counts show 0 because the scripted model reports no usage; a real model reports real counts. Real-model calls are not run here, they need `OPENAI_API_KEY`.

---

## 🔵 Simple Definition (2-3 lines)
The OpenAI Agents SDK (`pip install openai-agents`, `import agents`) is a small Python library with a few primitives: `Agent` (model + instructions + tools), `Runner` (the loop), handoffs (agent-to-agent delegation), guardrails (checks) and tracing (built-in spans). You write normal Python; the SDK runs the tool-calling loop for you.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Agents SDK (`pip install openai-agents`, `import agents`) एक छोटी Python library है जिसमें कुछ ही primitives हैं: `Agent` (model + instructions + tools), `Runner` (loop चलाने वाला), handoffs (एक agent से दूसरे को काम सौंपना), guardrails (जाँच) और tracing (built-in spans)। आप सामान्य Python लिखते हैं; tool-calling loop SDK चलाता है।

---

## 🔴 Problem it Solves
Hand-rolling an agent means writing the same loop every time: call the LLM, parse tool calls, run tools, append results, call again, stop on a final answer, enforce a turn limit, record traces. Each team writes it slightly differently and slightly wrong (infinite loops, lost tool errors, no tracing). Heavy graph frameworks fix that but add a lot of concepts to learn.

## 🔴 यह क्यों बना? (Hindi)
Agent खुद बनाने का मतलब हर बार वही loop लिखना: LLM बुलाओ, tool calls parse करो, tools चलाओ, results जोड़ो, फिर बुलाओ, final answer पर रुको, turn limit लगाओ, traces रखो। हर team इसे थोड़ा अलग और थोड़ा गलत लिखती है (infinite loop, खोए हुए tool errors, tracing नहीं)। भारी graph frameworks यह हल करते हैं पर सीखने के लिए बहुत सारे concepts जोड़ देते हैं।

---

## 🟢 How it Works

```
Step 1 -> You build Agent(name, instructions, tools, handoffs, guardrails, model)
Step 2 -> Runner.run(agent, input) starts the agent loop
Step 3 -> Loop turn: send instructions + history + tool schemas to the model
Step 4 -> Model returns one of:
            a) final text / structured output  -> loop ENDS, result returned
            b) tool call(s)                    -> SDK runs them, appends results, goes to Step 3
            c) handoff call (transfer_to_X)    -> current agent switches to X, goes to Step 3
Step 5 -> If turns > max_turns (default 10) -> MaxTurnsExceeded
Step 6 -> RunResult: final_output, new_items, last_agent, usage, raw_responses
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Agent(name, instructions, tools, handoffs, guardrails, model) बनाएँ
Step 2 -> Runner.run(agent, input) agent loop शुरू करता है
Step 3 -> हर turn: instructions + history + tool schemas model को भेजे जाते हैं
Step 4 -> Model तीन में से एक लौटाता है:
            a) final text / structured output -> loop खत्म, result वापस
            b) tool call(s) -> SDK चलाता है, results जोड़ता है, Step 3 पर वापस
            c) handoff call (transfer_to_X)   -> current agent X बन जाता है, Step 3
Step 5 -> turns > max_turns (default 10) -> MaxTurnsExceeded
Step 6 -> RunResult: final_output, new_items, last_agent, usage, raw_responses
```

**Verified facts (0.24.0):** `Runner.run`, `Runner.run_sync` and `Runner.run_streamed` all default to `max_turns=10`. The loop is Python code you can read in `agents.run`. The SDK ships `OpenAIResponsesModel` (default) and `OpenAIChatCompletionsModel`; the model can also be any object that subclasses `agents.Model`, which is exactly how the offline `ScriptedModel` works.

**Why "small on purpose":** the SDK has about five concepts to learn (Agent, Runner, handoff, guardrail, tracing) and no graph or state-machine language. Control flow is plain Python (`if`, `for`, `asyncio.gather`). This is the main trade-off against LangGraph: less ceremony, but also no built-in checkpointing/time-travel graph state.

**Connect to what you know (LangChain/LangGraph):** an `Agent` is like a `create_react_agent` node; handoffs are like a router edge to another agent; `Runner` is like `graph.invoke`. There is no separate state schema, the conversation items are the state.

---

## 🟡 Real World Example
**Tariff Agent.** A customs portal needs an assistant that looks up the duty rate for an HS code, explains it, and hands billing questions to a Billing Agent. With the SDK this is two `Agent` objects, one `@function_tool` and a `Runner.run` call inside a FastAPI endpoint, with tracing on by default.

**Research Agent / Customer Support:** the same shape: a triage agent with specialist agents attached as handoffs.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Customs portal को ऐसा assistant चाहिए जो HS code का duty rate खोजे, समझाए, और billing के सवाल Billing Agent को सौंप दे। SDK में यह दो `Agent` objects, एक `@function_tool` और FastAPI endpoint में `Runner.run` call है; tracing default रूप से चालू रहती है।

**Research Agent / Customer Support:** यही ढाँचा: एक triage agent, और specialist agents handoffs के रूप में जुड़े।

---

## 💻 Code Example — Basic
Runs offline (scripted model: first turn calls the tool, second turn answers).

```python
# Basic: smallest useful Tariff Agent with the OpenAI Agents SDK (runs offline)
from agents import Agent, Runner, function_tool, set_tracing_disabled   # core SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline fake model

set_tracing_disabled(True)                               # no OPENAI_API_KEY here, so skip trace export

@function_tool                                           # turns a typed function into an LLM tool
def get_tariff_rate(hs_code: str) -> str:                # type hints become the JSON schema
    """Return the duty rate for an HS code."""           # docstring becomes the tool description
    rates: dict[str, str] = {"6109": "12%"}              # tiny in-memory tariff table
    return rates.get(hs_code, "unknown")                 # return a string the model can read

model = ScriptedModel([                                  # scripted turns replace a real LLM
    [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],  # turn 1: model asks for the tool
    [assistant_message("The duty on HS 6109 is 12%.")],  # turn 2: model writes the final answer
])

agent = Agent(                                           # the agent = model + instructions + tools
    name="Tariff Agent",                                 # shown in traces
    instructions="Answer customs duty questions briefly.",  # system prompt
    tools=[get_tariff_rate],                             # tools the model may call
    model=model,                                         # production: model="<your model name>"
)

result = Runner.run_sync(agent, "Duty on cotton t-shirts, HS 6109?")  # blocking helper for scripts
print(result.final_output)                               # The duty on HS 6109 is 12%.
print("turns:", len(result.raw_responses))               # 2 model calls (tool turn + answer turn)
print("tokens:", result.context_wrapper.usage.total_tokens)  # 0 offline; real number with a real model
print("items:", [type(i).__name__ for i in result.new_items])  # tool call, tool output, message
```

## 💻 Code Example — Advanced
FastAPI, async, typed request/response, error handling, `max_turns` cost cap. Runs offline through `TestClient`. For production replace the scripted model with `model="<your model name>"` (not run here, needs a key).

```python
# Advanced: FastAPI + async Runner.run + error handling (runs offline via TestClient)
from agents import (Agent, Runner, function_tool, set_tracing_disabled,
                    MaxTurnsExceeded, AgentsException)  # SDK + its exceptions
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process HTTP client
from pydantic import BaseModel                           # request/response schemas

set_tracing_disabled(True)                               # no key -> no trace export

class AskIn(BaseModel):                                  # request body
    question: str

class AskOut(BaseModel):                                 # response body
    answer: str
    turns: int                                           # how many model calls were used
    total_tokens: int                                    # usage from the SDK

@function_tool                                           # tool the agent can call
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def make_agent() -> Agent:                               # factory: swap model per environment
    model = ScriptedModel([
        [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
        [assistant_message("HS 6109 duty is 12%.")],
    ])
    return Agent(name="Tariff Agent", instructions="Be brief.",
                 tools=[get_tariff_rate], model=model)

def create_app(agent: Agent) -> FastAPI:                 # app factory keeps the agent injectable
    app = FastAPI()                                      # new app

    @app.post("/ask", response_model=AskOut)             # one run per request
    async def ask(body: AskIn) -> AskOut:                # async endpoint, never block the event loop
        try:
            result = await Runner.run(agent, body.question, max_turns=5)  # max_turns = cost/loop cap
        except MaxTurnsExceeded:                         # agent looped too long
            raise HTTPException(status_code=504, detail="agent exceeded max turns")
        except AgentsException as exc:                   # any other SDK failure
            raise HTTPException(status_code=502, detail=type(exc).__name__)
        return AskOut(answer=str(result.final_output),   # final text
                      turns=len(result.raw_responses),   # model calls made
                      total_tokens=result.context_wrapper.usage.total_tokens)  # token usage

    return app

if __name__ == "__main__":
    client = TestClient(create_app(make_agent()))        # call the endpoint without uvicorn
    resp = client.post("/ask", json={"question": "Duty on HS 6109?"})  # one request
    print(resp.status_code, resp.json())                 # 200 {'answer': ..., 'turns': 2, 'total_tokens': 0}
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Core abstraction | Graph of nodes + state | Crew of role-based agents + tasks | Agent + Runner + handoffs | Agents in teams / group chats |
| Concepts to learn | Many (state, reducers, edges, checkpointers) | Medium (agent, task, crew, flow) | Few (agent, runner, handoff, guardrail, trace) | Medium (agent, team, termination) |
| Control flow | Explicit edges, loops, branches | Process sequential/hierarchical | Plain Python + handoffs | Team type decides next speaker |
| Built-in tracing | Via LangSmith | Via integrations | Yes, default spans | Via OpenTelemetry/logging |
| Persistence/state | Checkpointers, time travel | Memory options | Sessions; no graph state | Save/load team state |
| Best fit | Complex, long-running, auditable flows | Quick role-play pipelines | Small/medium agent apps, fast start | Conversational multi-agent research |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Calling `Runner.run_sync` inside an `async def` FastAPI handler.
✅ Correct: Use `await Runner.run(...)`. We verified `run_sync` raises `RuntimeError: ... cannot be called when an event loop is already running`.

❌ Mistake 2: Assuming the SDK only works with OpenAI models and OpenAI keys for everything.
✅ Correct: The model is pluggable (`Model` interface, `OpenAIChatCompletionsModel`, custom providers). Note tracing export itself uses an OpenAI key unless you disable or replace it (`set_tracing_disabled`, custom processors).

❌ Mistake 3: Letting the loop run with defaults on user-facing endpoints.
✅ Correct: Set `max_turns` explicitly and catch `MaxTurnsExceeded`.

❌ Mistake 4: Hard-coding secrets or model names inside the agent module.
✅ Correct: Read model name from config/env so you can swap models without code changes.

---

## 🧠 Tricky Interview Question
Your team already has a LangGraph app with checkpointing. A manager says "use the OpenAI Agents SDK, it is simpler". What do you answer?

**Answer:** Simpler to start does not mean a drop-in replacement. The SDK has no graph state, no checkpointer time travel and no explicit edge model; its state is the item list plus an optional `Session`. If the app needs pause/resume across days, human-in-the-loop edits to state, or deterministic branching you can unit-test, LangGraph fits better. If the app is a tool-using assistant with a few specialists, the SDK removes a lot of boilerplate. A pragmatic answer: migrate only the parts that are plain tool-agents, keep LangGraph for the orchestration that needs durable state, and compare on a fixed eval set (accuracy, latency, tokens) before deciding.

---

## ⚫ Interview Questions + Answers

**Q1:** What are the core primitives of the OpenAI Agents SDK?

**A1:** Agent, Runner, handoffs, guardrails, plus tracing (and tools, sessions). That small set is its selling point.

**Q2:** What does `Runner.run` do each turn and when does it stop?

**A2:** It sends instructions, history and tool schemas to the model, runs any tool calls, handles handoffs, and loops. It stops on a final output (no tool calls) or raises `MaxTurnsExceeded` after `max_turns` (default 10).

**Q3:** How does the SDK let you test without an API key?

**A3:** Subclass `agents.Model`, or use `agents.testing.ScriptedModel` with `assistant_message(...)` and `function_call(...)` steps. We ran every example here that way.

**Q4:** Is the SDK locked to OpenAI?

**A4:** No for models (pluggable `Model`/provider), but defaults assume OpenAI, and default trace export needs an OpenAI key unless disabled or replaced.

**Q5:** Design a support system with the SDK.

**A5:** Triage agent with `handoffs=[billing, tech, tariff]`, input guardrail on the triage agent, output guardrail on specialists that answer, tools with typed schemas, `Runner.run` inside async FastAPI with `max_turns`, a `Session` per conversation, tracing with a `group_id` per customer thread, metrics on handoff rate and tripwire count.

---

## 💰 Cost Impact
**Formula (approximate):** tokens_per_run ~ sum over turns of (instructions + tool schemas + full history + new output). History grows each turn, so cost grows faster than linearly with turns. Each handoff adds a tool-call and tool-output item to the history.

Typical ranges (approximate, from public pricing at time of writing, verify): a one-tool agent run is usually 2 model calls and a few hundred to a couple of thousand tokens; multi-agent runs with long histories can be several times that. **Tips:** keep instructions short, return compact tool results, cap `max_turns`, use a small model for triage and a larger one only where needed, and read `result.context_wrapper.usage` to measure real cost per run.

---

## 🔷 When to Use
✅ Use when:
- You want a tool-calling agent with handoffs and guardrails quickly
- You value built-in tracing and a small API surface
- Python/FastAPI service where control flow is simple enough to write in Python

❌ Avoid when:
- You need durable graph state, time travel or complex conditional graphs
- You need role-play crews with built-in process types (CrewAI) or group-chat patterns (AutoGen)
- You cannot send traces to a third party and have not configured a replacement

---

## 📊 Visual Diagram
```
 user ---> FastAPI /ask ---> Runner.run(agent, input, max_turns)
                                  |
                       +----------v-----------+
                       |      AGENT LOOP      |
                       |  model call          |
                       |    |-- final? --------+--> RunResult --> JSON
                       |    |-- tool call --> run tool --+
                       |    |-- handoff ----> switch agent|
                       |    +<--------------------------+ |
                       +----------------------+
                         guardrails (in/out)   tracing spans
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | Model + instructions + tools (+ handoffs, guardrails) | model, निर्देश और tools का समूह |
| Runner | Runs the agent loop | agent loop चलाने वाला |
| Handoff | Delegating the conversation to another agent | काम दूसरे agent को सौंपना |
| Guardrail | Input/output validation that can stop a run | जाँच जो run रोक सकती है |
| Tracing | Spans recorded for each model/tool call | हर call का रिकॉर्ड (spans) |
| max_turns | Limit on loop iterations (default 10) | loop की अधिकतम गिनती |

---

## ⚡ 3-Line Summary
English: The OpenAI Agents SDK is a small library: Agent, Runner, handoffs, guardrails, tracing.
It runs the tool-calling loop for you and stops on a final answer or `max_turns`.
Pick it for fast, readable agent apps; pick LangGraph when you need durable graph state.

Hindi: OpenAI Agents SDK एक छोटी library है: Agent, Runner, handoffs, guardrails, tracing।
यह tool-calling loop खुद चलाता है और final answer या `max_turns` पर रुकता है।
तेज़ और पढ़ने में आसान agent apps के लिए इसे चुनें; durable graph state चाहिए तो LangGraph।

---

## ➡️ Next Topic
**#32 SDK vs LangGraph vs CrewAI** - now that you know what the SDK is, we compare it side by side with the other frameworks, so you can justify your choice in an interview.

---
