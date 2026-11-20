---

# 78. Agent max_iter
# हिंदी में: Agent का max_iter
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`max_iter` is the maximum number of reasoning iterations (LLM calls in the ReAct loop) an agent may use on a task. The default is 25. When the limit is reached CrewAI forces the agent to produce its best final answer.

## 🔵 सरल परिभाषा (Hindi)
`max_iter` वह अधिकतम reasoning iterations (ReAct loop में LLM calls) है जो agent एक task पर इस्तेमाल कर सकता है। Default 25 है। Limit पूरी होने पर CrewAI agent से उसका best final answer निकलवाता है।

---

## 🔴 Problem it Solves
A confused agent can loop: call a tool, get 'unknown', try again. Each loop is a paid LLM call with a growing prompt. Without a cap one bad request can cost 25 calls and many seconds.

## 🔴 यह क्यों बना? (Hindi)
उलझा हुआ agent loop में फँस सकता है: tool call, 'unknown' मिला, फिर कोशिश। हर loop एक paid LLM call है और prompt बढ़ता जाता है। Cap के बिना एक बुरी request 25 calls और कई सेकंड खा सकती है।

---

## 🟢 How it Works

```
Step 1 -> iteration counter starts at 0
Step 2 -> LLM call -> Thought/Action or Final Answer
Step 3 -> Tool runs -> Observation appended -> counter +1
Step 4 -> If counter reaches max_iter, CrewAI asks for a final answer
Step 5 -> Agent returns best-effort answer (may be imperfect)
Step 6 -> Your guardrail/monitoring checks quality
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Iteration counter 0 से शुरू
Step 2 -> LLM call -> Thought/Action या Final Answer
Step 3 -> Tool चलता है -> Observation जुड़ता है -> counter +1
Step 4 -> counter max_iter तक पहुँचे तो CrewAI final answer माँगता है
Step 5 -> Agent best-effort जवाब देता है (अधूरा हो सकता है)
Step 6 -> आपका guardrail/monitoring quality जाँचता है
```

---

## 🟡 Real World Example
**Tariff Agent**: lookup needs 1 tool call + 1 answer, so `max_iter=3` is plenty. In our offline run with `max_iter=1` and a scripted tool call, the agent made exactly 2 LLM calls (the tool step, then the forced final answer) and returned a result instead of crashing.

## 🟡 Real Example Hindi mein
**Tariff Agent**: lookup में 1 tool call + 1 answer चाहिए, इसलिए `max_iter=3` काफ़ी है। हमारे offline run में `max_iter=1` और scripted tool call पर agent ने ठीक 2 LLM calls कीं (tool step, फिर forced final answer) और crash की जगह result दिया।

---

## 💻 Code Example — Basic
```python
# max_iter_basic.py - cap the reasoning loop so a confused agent cannot burn tokens forever
from crewai import Agent, Task, Crew, LLM            # core
from crewai.tools import tool                        # tool decorator

@tool("get_duty_rate")                               # tool
def get_duty_rate(hs_code: str) -> str:              # typed
    """Return duty percent for an HS code."""
    return {"8517": "0.0"}.get(hs_code, "unknown")

agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.",
              llm=LLM(model="gpt-4o-mini"), tools=[get_duty_rate],
              max_iter=3)                            # default is 25; each iteration = 1 LLM call
task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent)
print(Crew(agents=[agent], tasks=[task]).kickoff(inputs={"hs": "8517"}).raw)
```
Verified offline: default `max_iter` is 25 (read from the `Agent` model fields). The 2-calls-at-`max_iter=1` observation came from a scripted fake LLM; real models may behave differently.

## 💻 Code Example — Advanced
```python
# max_iter_api.py - iteration budget + wall-clock budget + counting LLM calls with step_callback
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app

class Q(BaseModel):                                  # body
    question: str                                    # input

@app.post("/bounded")                                # endpoint
async def bounded(q: Q) -> dict[str, object]:        # typed
    steps: list[str] = []                            # collects step types for observability
    agent = Agent(role="Analyst", goal="Answer", backstory="Brief.", llm=LLM(model="gpt-4o-mini"),
                  max_iter=4,                        # iteration cap
                  max_execution_time=45,             # seconds cap (separate from max_iter)
                  step_callback=lambda s: steps.append(type(s).__name__))   # called every step
    task = Task(description="{q}", expected_output="Short answer.", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs={"q": q.question})
    except Exception as exc:                         # includes timeouts
        raise HTTPException(504, f"{type(exc).__name__}") from exc
    return {"answer": out.raw, "steps": steps}       # show how many steps were used
```
Verified with `TestClient`. `max_execution_time` is a separate wall-clock cap; `step_callback` is invoked on each step (in an offline run with a tool it received `AgentAction` and `ToolResult` events), so you can count steps. In the TestClient run the fake never used tools so `steps` was an empty list.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Loop cap | `recursion_limit` on graph run | `max_iter` (default 25) | `max_turns` on Runner | Termination conditions / max turns |
| On limit | Raises recursion error | Forces best final answer | Raises MaxTurnsExceeded (check docs) | Stops with termination reason |
| Time cap | Your own timeout | `max_execution_time` | Your own timeout | Timeouts via cancellation tokens |
| Granularity | Whole graph | Per agent | Per run | Per team |
| Observability | Stream events | `step_callback` | Tracing | Message stream |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Leaving 25 for a one-lookup task.
✅ Correct: Set the smallest value that works (3-6) after testing.

❌ Mistake 2: Setting `max_iter=1` for tool agents.
✅ Correct: A tool agent needs at least a tool step and a final answer; use 3+.

❌ Mistake 3: Treating the forced answer as correct.
✅ Correct: Add guardrails/validation; a forced answer may be a guess.

---

## 🧠 Tricky Interview Question
You lowered `max_iter` to 3 and accuracy dropped. Is the cap wrong?

Answer: Not necessarily. First read the traces: if the agent legitimately needs 5 tool calls, 3 is too low and you either raise it or redesign (one tool that does the whole lookup, better descriptions, fewer retries). If it wastes iterations on tool errors, fix the tool messages instead. The cap is a safety net, not a tuning knob for quality; measure the distribution of steps used (via `step_callback`) and set the cap near the 95th percentile with a guardrail on top.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Default `max_iter`?
A1: 25.

Q2: [Medium] What happens when the limit is hit?
A2: CrewAI prompts the agent to give its best final answer so the run completes instead of failing (we saw 2 LLM calls with `max_iter=1`).

Q3: [Hard] `max_iter` vs `max_execution_time`?
A3: `max_iter` bounds the number of loop iterations; `max_execution_time` bounds seconds. Use both: slow tools can hurt even with few iterations.

Q4: [Hard] How to choose a value?
A4: Log steps per task in staging, choose near the 95th percentile plus buffer, and alert when runs hit the cap.

Q5: [System Design] Prevent runaway cost across a fleet?
A5: Per-agent caps, `max_rpm`, per-request token budgets, circuit breaker on repeated cap hits, queue with timeouts, and dashboards on steps/tokens per task.

---

## 💰 Cost Impact
Formula: worst-case calls = max_iter per agent per task. Because the scratchpad grows each iteration, worst-case tokens grow roughly quadratically with iterations. Example (approximate): 25 iterations of a 2,000-token prompt that grows by 300 each time is far more than 3 iterations. Always cap.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Every production agent
- Tool-using agents that may loop

❌ Avoid when:
- Setting it so low the agent cannot finish its tool step
- Using it instead of fixing bad tool errors

---

## 📊 Visual Diagram
```
  iter 1: LLM -> tool -> obs
  iter 2: LLM -> tool -> obs
  iter 3: LLM -> ...          counter == max_iter ?
                                   |no            |yes
                                   v              v
                             continue loop   force FINAL ANSWER
                                                  |
                                                  v
                                       guardrail / monitoring
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iteration | One LLM step in the loop | दोहराव |
| max_iter | Iteration cap | अधिकतम दोहराव |
| Runaway loop | Agent repeating without progress | बेकाबू लूप |
| Guardrail | Validation of outputs | गार्डरेल |
| step_callback | Hook called per step | स्टेप कॉलबैक |
| Percentile | Statistic for choosing caps | प्रतिशतक |

---

## ⚡ 3-Line Summary
English: max_iter caps the ReAct loop (default 25) and forces a final answer at the limit. Set it low, pair with max_execution_time, and watch how often runs hit it.
Hindi: max_iter ReAct loop को सीमित करता है (default 25) और limit पर final answer निकलवाता है। इसे कम रखें, max_execution_time के साथ जोड़ें, और देखें कि कितनी बार runs limit छूते हैं।

---

## ➡️ Next Topic
**079. Agent verbose** - seeing what the agent is thinking while you debug.

---
