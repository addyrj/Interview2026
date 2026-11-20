---

# 62. Lifecycle Hooks
# हिंदी में: Lifecycle Hooks (RunHooks और AgentHooks)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts shown come from the fake model (10 in / 5 out per call), not from a real LLM.

---

## 🔵 Simple Definition (2-3 lines)
Lifecycle hooks are callbacks the SDK calls at fixed moments of a run: agent start/end, LLM start/end, tool start/end, handoff. `RunHooks` watch the whole run (every agent); `AgentHooks` are attached to one agent.

## 🔵 सरल परिभाषा (Hindi)
Lifecycle hooks वे callbacks हैं जिन्हें SDK run के तय क्षणों पर बुलाता है: agent start/end, LLM start/end, tool start/end, handoff। `RunHooks` पूरे run (हर agent) को देखते हैं; `AgentHooks` किसी एक agent से जुड़े होते हैं।

---

## 🔴 Problem it Solves
Without hooks, metrics, logging, audit and budget checks get copy-pasted into every tool and endpoint, or you parse trace output after the fact. You also cannot react while the run is in progress (count LLM calls, stop on budget).

## 🔴 यह क्यों बना? (Hindi)
Hooks के बिना metrics, logging, audit और budget checks हर tool और endpoint में copy-paste होते हैं, या आप बाद में trace output parse करते हैं। Run चलते समय प्रतिक्रिया भी नहीं दे सकते (LLM calls गिनना, budget पर रोकना)।

---

## 🟢 How it Works

```
Runner.run(agent, input, hooks=MyRunHooks())    # whole run
Agent(..., hooks=MyAgentHooks())                 # one agent

Order we observed (b62), agent with one tool:
  run  agent_start   (RunHooks.on_agent_start)
  own  start         (AgentHooks.on_start)
  run  llm_start / llm_end
  run  tool_start  get_tariff_rate
  run  tool_end    get_tariff_rate -> 20%
  run  llm_start / llm_end   (model answers)
  run  agent_end   Tariff -> 20%
  own  end

Data available: context (RunContextWrapper -> .context, .usage),
                agent, tool, result/output
```

## 🟢 कैसे काम करता है? (Hindi)

```
Runner.run(agent, input, hooks=MyRunHooks())    # पूरा run
Agent(..., hooks=MyAgentHooks())                 # एक agent

हमने जो क्रम देखा (b62), एक tool वाला agent:
  run  agent_start   (RunHooks.on_agent_start)
  own  start         (AgentHooks.on_start)
  run  llm_start / llm_end
  run  tool_start  get_tariff_rate
  run  tool_end    get_tariff_rate -> 20%
  run  llm_start / llm_end   (model जवाब देता है)
  run  agent_end   Tariff -> 20%
  own  end

उपलब्ध data: context (RunContextWrapper -> .context, .usage),
              agent, tool, result/output
```

**Verified method names (0.24.0):** `RunHooks`: `on_agent_start`, `on_agent_end`, `on_llm_start(context, agent, system_prompt, input_items)`, `on_llm_end(context, agent, response)`, `on_tool_start(context, agent, tool)`, `on_tool_end(context, agent, tool, result)`, `on_handoff(context, from_agent, to_agent)`. `AgentHooks`: `on_start`, `on_end(context, agent, output)` and the matching llm/tool/handoff methods. All are `async def`, and all can be left unimplemented (defaults do nothing).

**Where is usage?** `context.usage` (the `RunContextWrapper`) has running `input_tokens` / `output_tokens` - the advanced sample logs it in `on_agent_end`.

**Hindi नोट:** Hooks vs Tracing: tracing बाहरी dashboard के लिए (बाद में देखना), hooks आपके अपने code में (उसी समय कुछ करना: गिनना, रोकना, log करना)। Hook के अंदर exception raise करने से run रुक जाता है, इसलिए hook में भारी काम या network call न करें; उसे queue में डालें।

---

## 🟡 Real World Example
**Tariff Agent.** A `MetricsHooks` increments `llm_calls` in the request context on every `on_llm_start` and logs `agent=Tariff in=20 out=10 llm_calls=2` in `on_agent_end`. The platform team alerts when `llm_calls` per request exceeds 6.

**Customer Support Agent:** an AgentHooks on the refund agent writes an audit row when it starts.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `MetricsHooks` हर `on_llm_start` पर request context में `llm_calls` बढ़ाता है और `on_agent_end` में `agent=Tariff in=20 out=10 llm_calls=2` log करता है। Platform team तब alert पाती है जब एक request में `llm_calls` 6 से ऊपर जाए।

**Customer Support Agent:** refund agent पर लगा AgentHooks उसके शुरू होने पर audit row लिखता है।

---

## 💻 Code Example — Basic
Runs offline. Prints the event order for RunHooks (run-wide) and AgentHooks (one agent).

```python
# Basic: RunHooks (whole run) vs AgentHooks (one agent) - print the event order.
# verified against openai-agents 0.24.0 (offline)
import asyncio
from typing import Any
from agents import Agent, AgentHooks, RunContextWrapper, RunHooks, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return "20%"

class RunLog(RunHooks[Any]):                                      # sees EVERY agent/tool/handoff/LLM call in the run
    async def on_agent_start(self, context, agent) -> None:        print("run  agent_start", agent.name)
    async def on_llm_start(self, context, agent, system_prompt, input_items) -> None:   print("run  llm_start  ", agent.name)
    async def on_llm_end(self, context, agent, response) -> None:   print("run  llm_end    ", agent.name)
    async def on_tool_start(self, context, agent, tool) -> None:    print("run  tool_start ", tool.name)
    async def on_tool_end(self, context, agent, tool, result) -> None:   print("run  tool_end   ", tool.name, "->", result)
    async def on_agent_end(self, context, agent, output) -> None:   print("run  agent_end  ", agent.name, "->", output)

class OwnLog(AgentHooks[Any]):                                    # attached to ONE agent only
    async def on_start(self, context, agent) -> None:               print("own  start")
    async def on_end(self, context, agent, output) -> None:         print("own  end")

m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"1"}')], [text("20%")]])
agent = Agent(name="Tariff", instructions="x", tools=[get_tariff_rate], model=m, hooks=OwnLog())
asyncio.run(Runner.run(agent, "rate?", hooks=RunLog()))
```

Output matches the 'Order we observed' block above.

## 💻 Code Example — Advanced
FastAPI: request-scoped `Metrics` dataclass in the context, `MetricsHooks` counting LLM calls and logging token usage. Output: `{'answer': '20%', 'llm_calls': 2, 'total_tokens': 30}` plus the log line `agent=Tariff in=20 out=10 llm_calls=2`.

```python
# Advanced: metrics hooks with a typed request context, FastAPI.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import logging, time
from dataclasses import dataclass, field
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, RunHooks, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)
log = logging.getLogger("agent.metrics")

@dataclass
class Metrics:                                                    # request-scoped, lives in context
    llm_calls: int = 0
    tool_ms: dict[str, float] = field(default_factory=dict)
    t0: float = field(default_factory=time.perf_counter)

class MetricsHooks(RunHooks[Metrics]):
    async def on_llm_start(self, context: RunContextWrapper[Metrics], agent: Agent[Metrics], system_prompt, input_items) -> None:
        context.context.llm_calls += 1                            # count model round-trips
    async def on_agent_end(self, context: RunContextWrapper[Metrics], agent: Agent[Metrics], output: Any) -> None:
        u = context.usage                                         # token usage is on the context wrapper
        log.info("agent=%s in=%s out=%s llm_calls=%s", agent.name, u.input_tokens, u.output_tokens, context.context.llm_calls)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return "20%"

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, Any]:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"1"}')], [text("20%")]])
    agent = Agent[Metrics](name="Tariff", instructions="x", tools=[get_tariff_rate], model=m)
    ctx = Metrics()
    res = await Runner.run(agent, q.question, context=ctx, hooks=MetricsHooks(), max_turns=5)
    return {"answer": res.final_output, "llm_calls": ctx.llm_calls, "total_tokens": res.context_wrapper.usage.total_tokens}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    logging.basicConfig(level=logging.INFO)
    print(TestClient(app).post("/ask", json={"question": "rate?"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Lifecycle callbacks | Callback handlers (`BaseCallbackHandler`) | Step / task callbacks, event listeners | `RunHooks` / `AgentHooks` | Message/event logging, `on_messages` stream |
| Scope | Per invoke via config callbacks | Per crew/agent | Per run or per agent | Per team/agent |
| Can stop the run | Raise in callback | Raise in callback | Raise in hook | Termination conditions |
| Token usage | In callback outputs / LangSmith | `crew.usage_metrics` | `context.usage` | Model client usage |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: Doing network I/O inside hooks.
✅ Correct: Hooks sit on the hot path; push events to a queue or use a batching tracing processor.

❌ Mistake: Storing request state in a global dict inside the hook class.
✅ Correct: Put it in the run `context`; hooks objects may be shared across requests.

❌ Mistake: Using AgentHooks and expecting to see other agents.
✅ Correct: Use RunHooks for the whole run; AgentHooks only fire for their agent.

❌ Mistake: Forgetting hooks are `async def`.
✅ Correct: Define methods with `async def`.

---

## 🧠 Tricky Interview Question
Your hook counts `llm_calls` correctly in tests but the number is wrong under load. Why?

**Answer:** The classic cause is shared mutable state: a single hooks instance stored on the module or app and writing to `self.count`, while many requests run concurrently. Keep counters in the per-request `context` object (as `Metrics` does) and create hooks per request or make them stateless. Second cause: nested agent runs (agent-as-tool) call their own hooks only if you pass hooks to `as_tool(hooks=...)`; otherwise inner calls are not counted. Third: parallel tool calls with the same name share a key in dictionaries (see #63).

---

## ⚫ Interview Questions + Answers

**Q1:** RunHooks vs AgentHooks?

**A1:** RunHooks observe the whole run across agents; AgentHooks belong to one agent.

**Q2:** Where do I read token usage in a hook?

**A2:** `context.usage` on the RunContextWrapper.

**Q3:** Hooks vs tracing?

**A3:** Hooks run your code inline during the run; tracing records spans for external viewing.

**Q4:** Can a hook stop a run?

**A4:** Yes, by raising an exception (the budget guard in #69 does this).

**Q5:** Design: per-tenant rate and budget enforcement.

**A5:** Tenant id in context; RunHooks checks a Redis counter in `on_llm_start`/`on_llm_end` (async, with timeout), raises a typed error mapped to HTTP 429/402, and emits usage events to a queue for billing.

---

## 💰 Cost Impact
Hooks add no tokens, only CPU/latency of your callback. Use them to measure tokens (`context.usage`) and enforce budgets, which is where real savings come from. Keep callbacks O(1). Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Metrics, logging, audit trails
- Budget and rate enforcement mid-run
- Reacting to handoffs and tool calls in your own code

❌ Avoid when:
- Heavy synchronous work inside callbacks
- Replacing a proper tracing backend
- Storing per-request state on shared hook objects

---

## 📊 Visual Diagram
```
  Runner.run(..., hooks=RunHooks)
     |
     v  on_agent_start ---------> AgentHooks.on_start
  +--> on_llm_start
  |      LLM call
  |    on_llm_end
  |      tool call?  -> on_tool_start -> tool -> on_tool_end
  |      handoff?    -> on_handoff
  +--- loop until final output
     v  on_agent_end  ---------> AgentHooks.on_end
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RunHooks | Callbacks for the whole run | पूरे run के callbacks |
| AgentHooks | Callbacks for one agent | एक agent के callbacks |
| on_llm_start | Before each model call | हर model call से पहले |
| on_tool_end | After a tool returns | tool लौटने के बाद |
| RunContextWrapper | Holds context + usage | context + usage रखता है |
| Audit trail | Record of actions | क्रियाओं का रिकॉर्ड |

---

## ⚡ 3-Line Summary
English: Hooks are async callbacks at agent, LLM, tool and handoff moments.
RunHooks see everything; AgentHooks see one agent.
Keep state in the run context and keep callbacks fast.

Hindi: Hooks agent, LLM, tool और handoff के क्षणों पर चलने वाले async callbacks हैं।
RunHooks सब देखते हैं; AgentHooks सिर्फ़ एक agent।
State को run context में रखें और callbacks तेज़ रखें।

---

## ➡️ Next Topic
**#63 on_tool_start + on_tool_end** - the most useful pair of hooks: timing, redaction and audit around every tool call.

---
