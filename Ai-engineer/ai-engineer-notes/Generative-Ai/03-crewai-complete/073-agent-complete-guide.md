---

# 73. Agent — Complete Guide
# हिंदी में: Agent — पूरी गाइड
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
A CrewAI `Agent` is an LLM with a persona (role, goal, backstory), optional tools and limits. It runs a think -> act -> observe loop until it produces a final answer. You can use it inside a Crew or alone with `agent.kickoff(...)`.

## 🔵 सरल परिभाषा (Hindi)
CrewAI का `Agent` एक LLM है जिसके पास persona (role, goal, backstory), optional tools और limits होती हैं। यह सोचो -> करो -> देखो loop चलाकर final answer देता है। इसे Crew में या अकेले `agent.kickoff(...)` से चला सकते हैं।

---

## 🔴 Problem it Solves
A raw LLM call has no identity, no tools and no loop guard. Agents give a repeatable bundle of persona + capability + limits so that behaviour is consistent and bounded.

## 🔴 यह क्यों बना? (Hindi)
Raw LLM call में पहचान, tools और loop की सीमा नहीं होती। Agent persona + क्षमता + limits का दोहराया जा सकने वाला bundle देता है ताकि behaviour स्थिर और सीमित रहे।

---

## 🟢 How it Works

```
Step 1 -> Build system prompt from role + goal + backstory
Step 2 -> Add tool names and schemas to the prompt
Step 3 -> LLM produces Thought + Action (tool) or Final Answer
Step 4 -> Tool runs; Observation is appended to the scratchpad
Step 5 -> Repeat until Final Answer or max_iter reached
Step 6 -> On limit, agent is forced to give its best final answer
Step 7 -> Output returned (TaskOutput inside a crew, LiteAgentOutput standalone)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> role + goal + backstory से system prompt बनता है
Step 2 -> Tool के नाम और schemas prompt में जुड़ते हैं
Step 3 -> LLM Thought + Action (tool) या Final Answer देता है
Step 4 -> Tool चलता है; Observation scratchpad में जुड़ता है
Step 5 -> Final Answer या max_iter तक दोहराएँ
Step 6 -> Limit पर agent को best final answer देना पड़ता है
Step 7 -> Output लौटता है (crew में TaskOutput, अकेले में LiteAgentOutput)
```

---

## 🟡 Real World Example
**Tariff Agent**: `Tariff Analyst` with a `get_duty_rate` tool, `max_iter=5`, temperature 0. Asked 'duty for 8517?' it calls the tool once and answers. Without the tool it would guess.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `Tariff Analyst` जिसके पास `get_duty_rate` tool है, `max_iter=5`, temperature 0। 'HS 8517 की duty?' पूछने पर यह tool एक बार call करके जवाब देता है। Tool न हो तो अंदाज़ा लगाएगा।

---

## 💻 Code Example — Basic
```python
# agent_basic.py - an Agent with the most-used parameters, plus standalone agent.kickoff()
from crewai import Agent, LLM                        # no Task/Crew needed for a one-off call
from crewai.tools import tool                        # decorator that turns a function into a tool

@tool("get_duty_rate")                               # name the LLM sees
def get_duty_rate(hs_code: str) -> str:              # type hints -> args schema
    """Return duty percent for an HS code."""        # docstring = tool description (required)
    return {"8517": "0.0", "6403": "10.0"}.get(hs_code, "unknown")  # fake DB

agent = Agent(
    role="Tariff Analyst",                           # identity
    goal="Answer duty questions accurately",         # objective
    backstory="Customs classification specialist.",  # persona
    llm=LLM(model="gpt-4o-mini", temperature=0.0),   # deterministic-ish for lookups
    tools=[get_duty_rate],                           # capabilities
    max_iter=5,                                      # loop cap (default 25)
    verbose=False,                                   # set True to debug
    allow_delegation=False,                          # default False: no asking other agents
)
out = agent.kickoff("What is the duty for HS 8517?")     # returns LiteAgentOutput
print(out.raw)                                       # final text
```
Verified: `Agent.kickoff('...')` standalone returns a `LiteAgentOutput` (ran offline with a scripted fake LLM); the system prompt contained the role text. Real answers: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# agent_api.py - agent factory + FastAPI + guarded execution
from crewai import Agent, LLM                        # agent + model
from crewai.tools import tool                        # tool decorator
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app

@tool("get_duty_rate")                               # tool name
def get_duty_rate(hs_code: str) -> str:              # typed arg
    """Return duty percent for an HS code, or 'unknown'."""
    return {"8517": "0.0"}.get(hs_code, "unknown")   # deterministic lookup

def make_agent() -> Agent:                           # new agent per request (agents carry run state)
    return Agent(role="Tariff Analyst", goal="Answer duty questions",
                 backstory="Customs expert.", llm=LLM(model="gpt-4o-mini", temperature=0.0),
                 tools=[get_duty_rate], max_iter=4, max_execution_time=60,   # seconds, hard stop
                 max_retry_limit=1)                  # retries on error (default 2)

class Ask(BaseModel):                                # body
    question: str                                    # user question

@app.post("/ask")                                    # endpoint
async def ask(body: Ask) -> dict[str, str]:          # typed
    try:
        out = await make_agent().kickoff_async(body.question)   # async standalone agent run
    except Exception as exc:                         # any failure -> 502
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}                       # answer only
```
Verified with `TestClient` and the offline fake. `max_execution_time` (seconds) and `max_retry_limit` are real `Agent` fields in 1.15.41 (defaults: `max_retry_limit=2`, `max_execution_time=None`, `max_iter=25`).

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Agent concept | Node (function) that may call an LLM | `Agent` with role/goal/backstory | `Agent` with instructions + tools | `AssistantAgent` with system message |
| Persona | Prompt you write | First-class fields | `instructions` string | `system_message` |
| Tools | Bound via tool nodes / ToolNode | `tools=[...]` | `tools=[...]` | `tools=[...]` |
| Loop guard | Recursion limit | `max_iter`, `max_execution_time` | `max_turns` | Termination conditions / max tool iterations (check docs) |
| Standalone run | Invoke a graph | `agent.kickoff()` | `Runner.run` | `agent.run()` |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Leaving `max_iter` at the default 25 for simple tasks.
✅ Correct: Set 3-6; each iteration is one paid LLM call.

❌ Mistake 2: Vague goal like 'help the user'.
✅ Correct: Write a measurable goal: 'return the exact duty percent or unknown'.

❌ Mistake 3: Putting secrets in backstory.
✅ Correct: Backstory goes to the LLM provider; keep secrets in tool code and env vars.

---

## 🧠 Tricky Interview Question
An agent keeps calling the same tool with the same arguments. Why and how do you fix it?

Answer: Usually the tool result is unhelpful (e.g. 'unknown' or an error) and the prompt gives no instruction on what to do next, so the ReAct loop repeats. CrewAI also caches identical tool calls by default (`cache=True`), so the repeated call returns instantly but does not change the situation. Fix: make tool errors descriptive, add backstory rules ('if unknown, stop and say unknown'), lower `max_iter`, and use a task guardrail to reject non-answers.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which three fields define an agent's persona?
A1: `role`, `goal` and `backstory`.

Q2: [Medium] What is the default `max_iter` and what happens at the limit?
A2: 25. At the limit the agent is asked to produce its best final answer; in our offline run with `max_iter=1` the agent made 2 LLM calls (one tool step plus the forced final answer).

Q3: [Hard] `allow_delegation` default and effect?
A3: False. When True the agent gets tools to ask/delegate to other crew agents, which adds LLM calls and unpredictability.

Q4: [Hard] Agent vs Task `tools`?
A4: Agent tools are available on all of that agent's tasks; `Task.tools` scopes tools to one task (check the current docs on whether they replace or add to the agent's tools), so you can limit exposure per task.

Q5: [System Design] Many users, each with different tool permissions. Design?
A5: Build the agent per request from a factory that selects tools by the caller's role, pass user context via inputs, enforce authorisation inside tool code (never trust the LLM), cap iterations and time, and log tool calls for audit.

---

## 💰 Cost Impact
Formula: cost per agent run = iterations x (prompt tokens + completion tokens) priced per model. Tool schemas and backstory are resent every iteration, so a long backstory x 25 iterations is expensive (approximate: even 300 backstory tokens x 10 iterations = 3,000 input tokens). Tips: short backstory, few tools, small `max_iter`, cheaper model.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Any task needing LLM reasoning plus tools
- Reusable personas across tasks

❌ Avoid when:
- Pure deterministic code (just write a function)
- Unbounded open-ended exploration without limits

---

## 📊 Visual Diagram
```
  role+goal+backstory --> [ SYSTEM PROMPT ] <-- tool schemas
                               |
                               v
                     +------------------+
        +----------> |       LLM        |
        |            +--------+---------+
        |   Observation       | Thought/Action | Final Answer
        |                     v                |
        |               +-----------+          v
        +---------------|   TOOL    |      OUTPUT
                        +-----------+
              (loop capped by max_iter / max_execution_time)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM + persona + tools + limits | एजेंट |
| ReAct | Reason, act, observe loop | सोच-कर-देखो चक्र |
| max_iter | Maximum loop iterations | अधिकतम दोहराव |
| Delegation | Asking another agent to do work | काम सौंपना |
| Scratchpad | Growing history of thoughts/observations | स्क्रैचपैड |
| Standalone kickoff | Running an agent without a Crew | अकेले चलाना |

---

## ⚡ 3-Line Summary
English: An Agent is persona + tools + limits around an LLM loop. Set clear goals, small max_iter and few tools. Use agent.kickoff for one-off calls, Crews for pipelines.
Hindi: Agent = LLM loop के चारों ओर persona + tools + limits। साफ़ goal, छोटा max_iter और कम tools रखें। एक-बार के काम के लिए agent.kickoff, pipelines के लिए Crew।

---

## ➡️ Next Topic
**074. Agent role + goal + backstory** - the three persona fields that shape every prompt.

---
