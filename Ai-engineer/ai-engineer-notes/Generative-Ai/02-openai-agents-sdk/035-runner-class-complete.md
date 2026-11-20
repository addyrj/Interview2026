---

# 35. Runner Class — Complete
# हिंदी में: Runner Class पूरी जानकारी
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0). Signatures read with `inspect.signature`; examples run offline with `agents.testing.ScriptedModel`. Token counts are 0 because the scripted model reports no usage. Real-model runs are not run, they need `OPENAI_API_KEY`.

---

## 🔵 Simple Definition (2-3 lines)
`Runner` is the engine that runs an `Agent`: it calls the model, executes tools, follows handoffs, runs guardrails and loops until there is a final answer or `max_turns` is hit. It returns a `RunResult` with the final output, new items, usage and the last agent.

## 🔵 सरल परिभाषा (Hindi)
`Runner` वह engine है जो `Agent` को चलाता है: model बुलाता है, tools चलाता है, handoffs फॉलो करता है, guardrails चलाता है और final answer मिलने या `max_turns` तक loop करता है। यह `RunResult` लौटाता है जिसमें final output, new items, usage और last agent होते हैं।

---

## 🔴 Problem it Solves
The agent loop (call model, parse tool calls, run tools, append results, retry, stop) is easy to get wrong: infinite loops, lost tool errors, no tracing, history not carried across requests. `Runner` implements it once, with limits, tracing and session support built in.

## 🔴 यह क्यों बना? (Hindi)
Agent loop (model बुलाओ, tool calls parse करो, tools चलाओ, results जोड़ो, रुको) गलत लिखना आसान है: infinite loop, खोए tool errors, tracing नहीं, requests के बीच history नहीं। `Runner` इसे limits, tracing और session support के साथ एक बार सही लिख देता है।

---

## 🟢 How it Works

```
Runner.run(starting_agent, input, *, context, max_turns=10, hooks, run_config,
           error_handlers, previous_response_id, auto_previous_response_id,
           conversation_id, session)                       (signature read from 0.24.0)

Step 1 -> Load history: session items (if session) + new input
Step 2 -> Run input guardrails (first agent only)
Step 3 -> Call model with instructions + items + tool schemas + handoff tools
Step 4 -> Model returns: final output | tool calls | handoff
Step 5 -> tools run (in parallel when several), outputs appended as items
Step 6 -> handoff -> current agent switches, go to Step 3
Step 7 -> final output -> run output guardrails (last agent) -> save to session
Step 8 -> turn counter > max_turns -> MaxTurnsExceeded
Step 9 -> RunResult(final_output, new_items, raw_responses, last_agent, context_wrapper.usage, ...)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> History load: session के items (अगर session है) + नया input
Step 2 -> Input guardrails चलते हैं (सिर्फ पहले agent पर)
Step 3 -> Model को instructions + items + tool schemas + handoff tools भेजे जाते हैं
Step 4 -> Model लौटाता है: final output | tool calls | handoff
Step 5 -> Tools चलते हैं (कई हों तो parallel), outputs items में जुड़ते हैं
Step 6 -> handoff -> current agent बदलता है, Step 3
Step 7 -> final output -> output guardrails (आखिरी agent पर) -> session में save
Step 8 -> turns > max_turns -> MaxTurnsExceeded
Step 9 -> RunResult(final_output, new_items, raw_responses, last_agent, usage, ...)
```

**Verified details:**
- `Runner.run`, `run_sync` and `run_streamed` take `max_turns: int | None = 10`.
- `RunConfig` fields include `model`, `model_provider`, `model_settings`, `handoff_input_filter`, `nest_handoff_history`, `input_guardrails`, `output_guardrails`, `tracing_disabled`, `workflow_name`, `trace_id`, `group_id`, `trace_metadata`, `session_input_callback`, `call_model_input_filter`.
- `RunResult` fields include `input`, `new_items`, `raw_responses`, `final_output`, `input_guardrail_results`, `output_guardrail_results`, `context_wrapper`; plus `last_agent`, `to_input_list()`, `final_output_as(...)`.
- With a `SQLiteSession`, the second run sent 5 items to the model (earlier call, tool output, answer, and the new question), proving history was carried automatically.
- Runs from `Runner` are not memoised: each call is a fresh loop. Memory comes only from `session`, `previous_response_id`/`conversation_id`, or you passing `to_input_list()` back.

**Connect to what you know:** `Runner.run` ~ `graph.ainvoke` / `AgentExecutor.ainvoke`; `session` ~ a LangGraph checkpointer keyed by `thread_id`; `RunConfig.group_id` ~ LangSmith session/thread metadata.

---

## 🟡 Real World Example
**Tariff Agent chat.** `/chat` takes `{conversation_id, message}`. The server reuses one session per conversation so "same for kids sizes?" works, caps concurrent runs, applies a 30 s timeout, sets `max_turns=6`, labels traces with `workflow_name` and `group_id`, and logs `usage.total_tokens` per run.

**Research Agent:** same, but with a longer timeout and streaming.

## 🟡 Real Example Hindi mein
**Tariff Agent chat.** `/chat` में `{conversation_id, message}` आता है। Server हर conversation के लिए एक session दोबारा इस्तेमाल करता है ताकि "same for kids sizes?" काम करे, concurrent runs सीमित करता है, 30 s timeout लगाता है, `max_turns=6` रखता है, traces पर `workflow_name` और `group_id` लगाता है, और हर run का `usage.total_tokens` log करता है।

**Research Agent:** यही, पर लंबा timeout और streaming के साथ।

---

## 💻 Code Example — Basic
Main parameters and the result object, with a `SQLiteSession` carrying history. Runs offline.

```python
# Basic: Runner parameters and the RunResult object on the Tariff Agent (runs offline)
from agents import (Agent, Runner, RunConfig, ModelSettings, SQLiteSession,
                    function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

model = ScriptedModel([
    [function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],  # turn 1: tool call
    [assistant_message("HS 6109 duty is 12%.")],         # turn 2: answer
    [assistant_message("Yes, same rate for kids sizes.")],  # a second run, later
])
agent = Agent(name="Tariff Agent", instructions="Be brief.", tools=[get_tariff_rate], model=model)

session = SQLiteSession("user-42")                       # in-memory sqlite by default: remembers history per id
result = Runner.run_sync(                                # Runner is a class with static-style entry points
    agent,                                               # starting agent
    "Duty for HS 6109?",                                 # input: str or list of input items
    context={"user": "u42"},                             # local context for tools/hooks (not sent to model)
    max_turns=5,                                         # loop cap (default is 10)
    run_config=RunConfig(                                # settings for the WHOLE run
        workflow_name="tariff-lookup",                   # trace name
        model_settings=ModelSettings(temperature=0),     # override agent settings run-wide
    ),
    session=session,                                     # persists items between runs
)

print("final_output :", result.final_output)             # HS 6109 duty is 12%.
print("last_agent   :", result.last_agent.name)          # agent that produced the final answer
print("model calls  :", len(result.raw_responses))       # 2
print("new_items    :", [type(i).__name__ for i in result.new_items])  # call, output, message
print("usage tokens :", result.context_wrapper.usage.total_tokens)  # 0 offline; real number with real model
print("input list   :", len(result.to_input_list()), "items")  # history you could feed back in manually

second = Runner.run_sync(agent, "Same for kids sizes?", session=session)  # session adds earlier turns automatically
print("second answer:", second.final_output)             # Yes, same rate for kids sizes.
print("sent to model:", len(model.last_call.input), "items (history + new question)")  # shows memory worked
```

## 💻 Code Example — Advanced
FastAPI chat endpoint: session per conversation, semaphore, timeout, `RunConfig` trace labels, error mapping, token usage. Runs offline via `TestClient`. The in-memory dict of sessions is for the demo; production should use a shared store (Redis/SQLAlchemy sessions) because several workers do not share process memory.

```python
# Advanced: Runner.run in FastAPI with sessions, timeout, concurrency cap, error mapping (runs offline)
import asyncio                                           # timeout + semaphore
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Runner, RunConfig, SQLiteSession, MaxTurnsExceeded, AgentsException,
                    function_tool, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

class ChatIn(BaseModel):                                 # request body
    conversation_id: str
    message: str

class ChatOut(BaseModel):                                # response body
    answer: str
    agent: str
    model_calls: int
    total_tokens: int

@function_tool
async def get_tariff_rate(hs_code: str) -> str:
    """Return the duty rate for an HS code."""
    return {"6109": "12%"}.get(hs_code, "unknown")

def make_agent() -> Agent:                               # factory; production passes a real model name
    model = ScriptedModel([[function_call("get_tariff_rate", {"hs_code": "6109"}, call_id="c1")],
                           [assistant_message("HS 6109 duty is 12%.")]])
    return Agent(name="Tariff Agent", instructions="Be brief.", tools=[get_tariff_rate], model=model)

app = FastAPI()
LIMIT = asyncio.Semaphore(8)                             # at most 8 concurrent agent runs per process
sessions: dict[str, SQLiteSession] = {}                  # demo store; production: Redis/SQLAlchemy session

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn) -> ChatOut:
    session = sessions.setdefault(body.conversation_id, SQLiteSession(body.conversation_id))  # one per conversation
    async with LIMIT:                                    # back-pressure instead of unbounded parallel LLM calls
        try:
            result = await asyncio.wait_for(             # wall-clock limit around the whole run
                Runner.run(make_agent(), body.message, max_turns=6, session=session,
                           run_config=RunConfig(workflow_name="tariff-chat", group_id=body.conversation_id)),
                timeout=30)                              # seconds; tune to your latency budget
        except asyncio.TimeoutError:                     # too slow
            raise HTTPException(504, "agent timed out")
        except MaxTurnsExceeded:                         # loop guard fired
            raise HTTPException(504, "agent exceeded max turns")
        except AgentsException as exc:                   # any other SDK error (guardrail, model behavior, ...)
            raise HTTPException(502, type(exc).__name__)
    return ChatOut(answer=str(result.final_output), agent=result.last_agent.name,
                   model_calls=len(result.raw_responses),
                   total_tokens=result.context_wrapper.usage.total_tokens)  # log this for cost tracking

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.post("/chat", json={"conversation_id": "c1", "message": "Duty for HS 6109?"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Run entry point | `graph.invoke/ainvoke/astream` | `crew.kickoff()` | `Runner.run / run_sync / run_streamed` | `agent.run()` / `team.run()` |
| Loop limit | `recursion_limit` | `max_iter` per agent | `max_turns` (default 10) | Termination conditions, `max_turns` |
| Conversation memory | Checkpointer + `thread_id` | Memory modules | `session`, `conversation_id`, `to_input_list()` | Team state / model context |
| Run-wide config | `config` dict | Crew settings | `RunConfig` | Team/agent arguments |
| Result object | State dict | `CrewOutput` | `RunResult` | `TaskResult` |
| Tracing labels | LangSmith metadata | Integrations | `workflow_name`, `group_id`, `trace_metadata` | OpenTelemetry |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Expecting memory between two `Runner.run` calls with no session.
✅ Correct: Pass a `session`, or feed `result.to_input_list() + [new message]` back in.

❌ Mistake 2: Using one shared `SQLiteSession` object for all users.
✅ Correct: One session id per conversation (per user thread).

❌ Mistake 3: No timeout around the run.
✅ Correct: `asyncio.wait_for(Runner.run(...), timeout=...)` plus `max_turns`.

❌ Mistake 4: Reading `result.final_output` as a string when `output_type` is set.
✅ Correct: It is the typed object; use `result.final_output_as(MyType)` if you want a checked cast.

❌ Mistake 5: Ignoring `usage`.
✅ Correct: Log `result.context_wrapper.usage` per run, so cost is visible before the bill is.

---

## 🧠 Tricky Interview Question
Your `/chat` endpoint works with one worker, but with 4 uvicorn workers users sometimes "forget" the conversation. Why, and how do you fix it?

**Answer:** The sessions live in a per-process dict (and an in-memory SQLite DB per process), so request 2 can land on a worker that never saw request 1. Fix: store session items in a shared backend (SQLAlchemy/Redis-backed session, or your own `Session` implementation), keyed by conversation id; or pin with sticky routing (weaker). Also remember that the history must fit the context window: trim or summarise old items (`session_input_callback` in `RunConfig` is the hook for shaping session input), otherwise cost per turn grows with the conversation.

---

## ⚫ Interview Questions + Answers

**Q1:** What does `Runner.run` return?

**A1:** A `RunResult`: `final_output`, `new_items`, `raw_responses`, `last_agent`, guardrail results and `context_wrapper.usage`.

**Q2:** What is the default `max_turns`, and what happens when exceeded?

**A2:** 10. `MaxTurnsExceeded` is raised (catch it and return a clear error).

**Q3:** How do you give the agent memory across requests?

**A3:** Use a `session` (for example `SQLiteSession(id)`), or `conversation_id`/`previous_response_id` with the Responses API, or pass `to_input_list()` back manually.

**Q4:** What is `RunConfig` for and how does it differ from `Agent` settings?

**A4:** Run-wide overrides and tracing labels: model/model settings override, guardrails added for the whole run, `workflow_name`, `group_id`, `trace_metadata`, handoff input filter. Agent settings are per agent.

**Q5:** Design a production runner layer for 1000 concurrent users.

**A5:** Async `Runner.run`, semaphore per process, timeout, `max_turns`, shared-store sessions, queue/streaming for long runs, per-tenant rate limits, trace `group_id` per conversation, metrics for latency, turns, tokens, guardrail trips and error classes, and a circuit breaker for provider outages.

---

## 💰 Cost Impact
Cost per run = sum over turns of input tokens (instructions + tool schemas + full history) + output tokens. Sessions make later turns more expensive because history is resent each time. Approximate, from public pricing at time of writing, verify: a one-tool run is 2 model calls; long sessions can multiply input tokens.

**Tips:** set `max_turns`, cap history with `session_input_callback` or summarisation, keep tool outputs compact, use a cheaper model for simple agents, track `usage` per run.

---

## 🔷 When to Use
✅ Use when:
- Any time you execute an SDK agent (it is the only way to run the loop)
- You need session memory, tracing labels or run-wide settings

❌ Avoid when:
- You need durable pause/resume with explicit state (consider LangGraph checkpointers)
- You want to hand-write the loop (you lose tracing, guardrails and handoffs)

---

## 📊 Visual Diagram
```
 HTTP /chat --> semaphore --> wait_for(timeout) --> Runner.run(agent, msg, session, RunConfig)
                                                       |
   session.get_items() --> [history + new msg] --> input guardrails
                                                       |
                       +------------- loop (<= max_turns) -------------+
                       | model call -> tool calls / handoff / final     |
                       +------------------------------------------------+
                                                       |
                         output guardrails --> session.add_items --> RunResult
                                                       |
                         ChatOut(answer, last_agent, model_calls, tokens)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runner | Engine that runs the agent loop | agent loop चलाने वाला engine |
| RunResult | Return object of a run | run का नतीजा object |
| RunConfig | Run-wide settings and trace labels | पूरे run की settings |
| max_turns | Loop iteration cap (default 10) | loop की अधिकतम गिनती |
| Session | Stored conversation history | सहेजा गया conversation history |
| new_items | Items generated during this run | इस run में बने items |
| group_id | Trace label linking runs of one conversation | एक conversation के traces जोड़ने वाला label |

---

## ⚡ 3-Line Summary
English: `Runner` runs the agent loop and returns a `RunResult`.
Control it with `max_turns`, `context`, `RunConfig`, `session` and hooks.
In FastAPI add a timeout, a concurrency cap and shared-store sessions.

Hindi: `Runner` agent loop चलाता है और `RunResult` लौटाता है।
इसे `max_turns`, `context`, `RunConfig`, `session` और hooks से नियंत्रित करें।
FastAPI में timeout, concurrency cap और shared-store sessions लगाएँ।

---

## ➡️ Next Topic
**#36 Runner.run() vs run_sync() vs run_streamed()** - the three entry points differ in blocking, async and streaming behaviour; picking wrongly freezes FastAPI or hides tokens from users.

---
