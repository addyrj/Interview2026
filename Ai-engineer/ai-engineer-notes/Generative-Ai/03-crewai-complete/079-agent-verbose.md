---

# 79. Agent verbose
# हिंदी में: Agent का verbose
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`verbose=True` prints the agent's thoughts, tool calls and results to the terminal. It exists on `Agent` and `Crew`, defaults to False, and is for debugging. In servers use `step_callback`, task callbacks and logging instead.

## 🔵 सरल परिभाषा (Hindi)
`verbose=True` agent के thoughts, tool calls और results terminal पर छापता है। यह `Agent` और `Crew` दोनों पर है, default False है और debugging के लिए है। Servers में `step_callback`, task callbacks और logging इस्तेमाल करें।

---

## 🔴 Problem it Solves
Agents are black boxes: when an answer is wrong you cannot tell if the prompt, tool or loop failed. Verbose output shows the reasoning trail so you can fix the right layer.

## 🔴 यह क्यों बना? (Hindi)
Agents black box जैसे हैं: जवाब ग़लत हो तो पता नहीं चलता कि prompt, tool या loop में दिक़्क़त है। Verbose output reasoning का रास्ता दिखाता है ताकि सही layer ठीक की जा सके।

---

## 🟢 How it Works

```
Step 1 -> verbose=True on Agent and/or Crew
Step 2 -> Event listeners render panels to stdout (task start, agent thought, tool use, final answer)
Step 3 -> You read the trail while running locally
Step 4 -> Fix prompt / tool / limit
Step 5 -> Turn verbose off in production
Step 6 -> Use callbacks + structured logs/tracing instead
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Agent और/या Crew पर verbose=True
Step 2 -> Event listeners stdout पर panels दिखाते हैं (task शुरू, agent का thought, tool use, final answer)
Step 3 -> Local run में आप trail पढ़ते हैं
Step 4 -> prompt / tool / limit ठीक करें
Step 5 -> Production में verbose बंद करें
Step 6 -> इसके बजाय callbacks + structured logs/tracing इस्तेमाल करें
```

---

## 🟡 Real World Example
**Tariff Agent**: the agent returns 'unknown' for HS 8517. With verbose you see it passed '8517 ' with a trailing space to the tool - a tool-input bug, not an LLM bug. In an offline run with `verbose=True`, output was printed and `step_callback` received `AgentAction` and `ToolResult` events.

## 🟡 Real Example Hindi mein
**Tariff Agent**: HS 8517 के लिए agent 'unknown' लौटाता है। Verbose में दिखता है कि tool को '8517 ' (पीछे space) गया - यह tool-input bug है, LLM bug नहीं। Offline run में `verbose=True` पर output छपा और `step_callback` को `AgentAction` व `ToolResult` events मिले।

---

## 💻 Code Example — Basic
```python
# verbose_basic.py - verbose on the agent vs on the crew
from crewai import Agent, Task, Crew, LLM            # core

agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.",
              llm=LLM(model="gpt-4o-mini"),
              verbose=True)                          # prints this agent's thoughts/tool calls
task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent)
crew = Crew(agents=[agent], tasks=[task],
            verbose=True)                            # prints crew/task start-finish panels
crew.kickoff(inputs={"hs": "8517"})                  # watch the terminal
```
Verified offline: `verbose=True` produced terminal output (captured and checked non-empty) with a scripted fake LLM. The exact panel layout may change between versions.

## 💻 Code Example — Advanced
```python
# verbose_api.py - do NOT use verbose in servers; use callbacks + logging instead
import logging                                       # standard logging
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

log = logging.getLogger("crew")                      # app logger (ship to your log stack)
app = FastAPI()                                      # app

class Q(BaseModel):                                  # body
    hs: str                                          # HS code

@app.post("/traced")                                 # endpoint
async def traced(q: Q) -> dict[str, str]:            # typed
    agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.",
                  llm=LLM(model="gpt-4o-mini"), verbose=False,   # no terminal noise in prod
                  step_callback=lambda s: log.info("step=%s", type(s).__name__))   # structured signal
    task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent,
                callback=lambda o: log.info("task_done chars=%d", len(o.raw)))     # per-task hook
    try:
        out = await Crew(agents=[agent], tasks=[task], verbose=False).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # failure
        log.exception("crew failed")                 # stack trace to logs only
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}
```
Verified with `TestClient` (HTTP 200). Logs include only step types and sizes, not raw prompts: prompts and tool outputs can contain PII, so log metadata by default and sample full traces with redaction.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Debug output | `stream` events, LangSmith tracing | `verbose=True`, event listeners, tracing | Built-in tracing, hooks | Message stream, logging |
| Per-step hook | Stream node updates | `step_callback`, `task_callback` | Run hooks | Event handlers |
| Production observability | LangSmith / OpenTelemetry | Callbacks + logs, tracing (check docs) | Tracing dashboard / processors | Logging + OpenTelemetry |
| Default noise | Silent | Silent (`verbose=False`) | Silent | Configurable |
| Risk | Leaking state in logs | Prompts to stdout in prod | Traces may hold PII | Logs may hold PII |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Leaving `verbose=True` in production.
✅ Correct: Turn it off; it spams stdout and may leak prompts. Use callbacks + structured logs.

❌ Mistake 2: Setting verbose only on the Crew and expecting full tool details.
✅ Correct: Set it on the agents too when you need per-agent traces.

❌ Mistake 3: Logging full prompts with user data.
✅ Correct: Log ids, step types, token counts; redact or sample content.

---

## 🧠 Tricky Interview Question
In production an answer was wrong and nothing was logged because verbose was off. How do you debug after the fact?

Answer: You need observability designed up front: per-request IDs, `step_callback` and task callbacks writing structured events (step type, tool name, duration, token counts) to your log store, optional full-trace capture behind a sampling flag with redaction, and tracing integrations. Then replay: re-run the same inputs against the offline fake or a recorded response to reproduce. Debugging by flipping verbose on in prod is slow and risky.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `verbose=True` do?
A1: Prints the agent/crew's reasoning, tool calls and results to the terminal.

Q2: [Medium] Agent verbose vs Crew verbose?
A2: Both flags exist; Crew-level shows crew/task progress, agent-level shows each agent's thinking and tool use. Set both when debugging.

Q3: [Hard] What replaces verbose in production?
A3: `step_callback` and task `callback` hooks, standard logging with request IDs, and a tracing backend.

Q4: [Hard] Why not log full prompts?
A4: They may contain PII/secrets and are large; log metadata, sample and redact.

Q5: [System Design] Observability for a crew service?
A5: Per-request trace ID through FastAPI middleware, event hooks per step/task, metrics (steps, tokens, latency, cap hits), error taxonomy, sampled redacted traces, dashboards and alerts.

---

## 💰 Cost Impact
Verbose itself does not call the LLM, so it adds no token cost; it adds I/O and log volume. The real cost lever is what you learn from it: spotting redundant iterations and oversized tool outputs. Log volume can be significant in production (approximate: dozens of lines per run), so keep it off and use sampled structured logs.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Local debugging and demos
- Understanding why a tool is misused

❌ Avoid when:
- Production servers (use callbacks/logging)
- Handling sensitive data in shared logs

---

## 📊 Visual Diagram
```
  Agent loop
     |-- thought ----------\
     |-- tool call --------+--> [ verbose panels -> stdout ]   (debug only)
     |-- observation ------+--> [ step_callback  -> logger  ]  (production)
     '-- final answer -----/--> [ task callback  -> metrics ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| verbose | Flag that prints reasoning trail | विस्तृत आउटपुट |
| Callback | Function called on an event | कॉलबैक |
| Trace | Recorded sequence of steps | ट्रेस |
| Observability | Ability to understand system from outputs | अवलोकनीयता |
| Redaction | Removing sensitive data | संवेदनशील डेटा हटाना |
| Sampling | Logging a fraction of runs | नमूना |

---

## ⚡ 3-Line Summary
English: verbose=True is a debug-time window into agent thoughts and tool calls. It costs no tokens but is not a production logger. Use step_callback, task callbacks and structured, redacted logs in servers.
Hindi: verbose=True debugging के समय agent के thoughts और tool calls की खिड़की है। इसमें tokens नहीं लगते पर यह production logger नहीं है। Servers में step_callback, task callbacks और structured, redacted logs इस्तेमाल करें।

---

## ➡️ Next Topic
**080. Task - Complete Guide** - the unit of work each agent executes.

---
