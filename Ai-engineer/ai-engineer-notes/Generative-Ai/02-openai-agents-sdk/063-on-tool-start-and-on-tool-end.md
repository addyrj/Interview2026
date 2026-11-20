---

# 63. on_tool_start + on_tool_end
# हिंदी में: on_tool_start और on_tool_end (tool call के आगे-पीछे के hooks)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Outputs shown are from the fake model and fake tools.

---

## 🔵 Simple Definition (2-3 lines)
`on_tool_start(context, agent, tool)` is called just before the SDK executes a tool; `on_tool_end(context, agent, tool, result)` is called right after, with the tool's result as a string. They are the best place for timing, audit logging and redaction around every tool call.

## 🔵 सरल परिभाषा (Hindi)
`on_tool_start(context, agent, tool)` तब बुलाया जाता है जब SDK tool चलाने वाला होता है; `on_tool_end(context, agent, tool, result)` tool खत्म होते ही बुलाया जाता है, जिसमें tool का result string के रूप में मिलता है। Timing, audit logging और redaction के लिए यह सबसे अच्छी जगह है।

---

## 🔴 Problem it Solves
Tools are where side effects happen (DB reads, customs API calls, payments). Without a central hook you add timing and logging inside every tool, forget some, and log sensitive values (PAN, card numbers) by accident. You also cannot see which agent called which tool.

## 🔴 यह क्यों बना? (Hindi)
Tools में ही side effects होते हैं (DB read, customs API call, payment)। Central hook के बिना आप हर tool में timing और logging डालते हैं, कुछ भूल जाते हैं, और संवेदनशील values (PAN, card number) गलती से log हो जाती हैं। साथ ही यह भी नहीं दिखता कि किस agent ने कौन सा tool बुलाया।

---

## 🟢 How it Works

```
LLM returns tool_call(get_tariff_rate, {"hs_code": "6109.10"})
Step 1 -> SDK finds the tool by name in agent.tools
Step 2 -> RunHooks.on_tool_start(context, agent, tool)     (+ AgentHooks.on_tool_start)
Step 3 -> tool body runs (your Python function)
Step 4 -> RunHooks.on_tool_end(context, agent, tool, result)  (result is str)
Step 5 -> result is sent back to the LLM as a tool output item

What you get:  context (state + usage), agent (who called), tool (.name)
What you do NOT get in on_tool_start: the parsed arguments
                                      (basic sample b63 prints only agent + tool name)
```

## 🟢 कैसे काम करता है? (Hindi)

```
LLM tool_call(get_tariff_rate, {"hs_code": "6109.10"}) लौटाता है
Step 1 -> SDK agent.tools में नाम से tool ढूँढता है
Step 2 -> RunHooks.on_tool_start(context, agent, tool)     (+ AgentHooks.on_tool_start)
Step 3 -> tool body चलता है (आपका Python function)
Step 4 -> RunHooks.on_tool_end(context, agent, tool, result)  (result str है)
Step 5 -> result LLM को tool output item बनकर वापस जाता है

मिलता है:  context (state + usage), agent (किसने बुलाया), tool (.name)
on_tool_start में नहीं मिलता: parsed arguments
```

**Verified signatures (0.24.0):** `on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool)` and `on_tool_end(self, context, agent, tool, result: str)`. Both are `async def`. `result` is a `str` even if your tool returned a number or object (the SDK stringifies it).

**Hindi नोट:** अगर arguments चाहिए तो tool function के अंदर ही log करें, या tool को एक thin wrapper में लपेटें। Hook में सिर्फ़ tool का नाम और result मिलता है। ध्यान रखें: `on_tool_end` का result वही है जो model को जाएगा; hook उसे बदल नहीं सकता, सिर्फ़ देख सकता है (redaction तभी करें जब आप log कर रहे हों; model को जाने वाला मान बदलने के लिए tool के अंदर या guardrail में काम करें)।

---

## 🟡 Real World Example
**Tariff Agent.** One request calls `get_tariff_rate` (public data) and `get_importer_pan` (sensitive). `AuditHooks` records `{tool, ms, result}` for each call into the request context; the PAN result is replaced with `***` and long results are truncated to 80 chars. The API returns the audit list to the compliance dashboard.

**Customer Support Agent:** on_tool_start for `issue_refund` increments a per-ticket counter; more than 2 refunds in a run triggers an alert.

## 🟡 Real Example Hindi mein
**Tariff Agent.** एक request में `get_tariff_rate` (public data) और `get_importer_pan` (संवेदनशील) दोनों बुलाए जाते हैं। `AuditHooks` हर call के लिए `{tool, ms, result}` request context में रखता है; PAN का result `***` से बदल दिया जाता है और लंबे results 80 अक्षरों पर काट दिए जाते हैं। API यह audit list compliance dashboard को लौटाती है।

**Customer Support Agent:** `issue_refund` के on_tool_start पर per-ticket counter बढ़ता है; एक run में 2 से ज़्यादा refunds पर alert जाता है।

---

## 💻 Code Example — Basic
Runs offline. Output: `START Tariff -> get_tariff_rate` then `END   get_tariff_rate -> '20%'`.

```python
# Basic: on_tool_start / on_tool_end - log which tool ran, with what result (offline).
# verified against openai-agents 0.24.0
import asyncio
from typing import Any
from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return "20%"

class ToolLogger(RunHooks[Any]):
    async def on_tool_start(self, context: RunContextWrapper[Any], agent: Agent[Any], tool: Tool) -> None:
        print(f"START {agent.name} -> {tool.name}")               # no arguments here: only agent + tool object
    async def on_tool_end(self, context: RunContextWrapper[Any], agent: Agent[Any], tool: Tool, result: str) -> None:
        print(f"END   {tool.name} -> {result!r}")                 # result is what goes back to the model

m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("20%")]])
asyncio.run(Runner.run(Agent(name="Tariff", instructions="x", tools=[get_tariff_rate], model=m), "rate?", hooks=ToolLogger()))
```

## 💻 Code Example — Advanced
FastAPI: per-tool latency, an audit list in the request context, PII redaction and truncation. Two tools are called in parallel in one model turn. Output: `done [('get_importer_pan', '***'), ('get_tariff_rate', '20%')]` (latency in ms varies per run, so it is not printed).

```python
# Advanced: per-tool latency, audit log and result redaction using on_tool_start/on_tool_end + FastAPI.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import asyncio, time
from dataclasses import dataclass, field
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@dataclass
class Audit:
    events: list[dict[str, Any]] = field(default_factory=list)    # returned to the caller for compliance
    _starts: dict[str, float] = field(default_factory=dict)

class AuditHooks(RunHooks[Audit]):
    async def on_tool_start(self, context: RunContextWrapper[Audit], agent: Agent[Audit], tool: Tool) -> None:
        context.context._starts[tool.name] = time.perf_counter()  # key by tool name (parallel calls of SAME tool would collide)
    async def on_tool_end(self, context: RunContextWrapper[Audit], agent: Agent[Audit], tool: Tool, result: str) -> None:
        ms = (time.perf_counter() - context.context._starts.pop(tool.name, time.perf_counter())) * 1000
        safe = "***" if tool.name == "get_importer_pan" else str(result)[:80]   # never log PII; truncate big outputs
        context.context.events.append({"tool": tool.name, "ms": round(ms), "result": safe})

@function_tool
async def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    await asyncio.sleep(0.05)
    return "20%"

@function_tool
async def get_importer_pan(importer_id: str) -> str:
    """Tax id of an importer (sensitive)."""
    return "ABCDE1234F"

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, Any]:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"1"}'), tool_call("get_importer_pan", '{"importer_id":"7"}')], [text("done")]])
    ctx = Audit()
    agent = Agent[Audit](name="Tariff", instructions="x", tools=[get_tariff_rate, get_importer_pan], model=m)
    res = await Runner.run(agent, q.question, context=ctx, hooks=AuditHooks(), max_turns=4)
    return {"answer": res.final_output, "audit": ctx.events}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    r = TestClient(app).post("/ask", json={"question": "x"}).json()
    print(r["answer"], [(e["tool"], e["result"]) for e in r["audit"]])   # ms varies per run, so it is not printed
```

Note the event order: the PAN tool finished first (no sleep), so it appears first - events are appended in completion order, not call order.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Tool start/end callback | `on_tool_start` / `on_tool_end` in callback handlers | Tool-usage events / step callback | `RunHooks.on_tool_start/end`, `AgentHooks` | Tool call/result events in the message stream |
| Sees tool arguments | Yes (input in callback) | Via event payload | Not in the hook; log inside the tool | In the call event |
| Sees result | Yes | Yes | Yes (`result: str`) | Yes |
| Can modify result | No (observe) | No | No (observe) | Via custom tool wrapper |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Keying timing state by tool name when the model can call the same tool twice in parallel.
✅ Correct: Parallel calls of the same tool overwrite each other's start time. Wrap the tool body with its own timer, or key by a unique id you generate inside the tool.

❌ Mistake 2: Logging `result` raw.
✅ Correct: Redact by tool name or by pattern and truncate; `result` may contain PII or megabytes of text.

❌ Mistake 3: Expecting `on_tool_end` to fire when the tool is skipped or the run is cancelled.
✅ Correct: Treat the hooks as best-effort observers; use `try/finally` in the tool for guaranteed cleanup.

❌ Mistake 4: Doing a blocking network call (log shipping) inside the hook.
✅ Correct: Append to an in-memory queue and ship in a background task.

---

## 🧠 Tricky Interview Question
Your audit log shows `get_tariff_rate` took 0 ms in production although the customs API is slow. Why?

**Answer:** Most likely the timer was started and stopped for different calls: with parallel tool calls of the same tool, a dict keyed by `tool.name` is overwritten or popped early (the `pop(..., default)` in our sample would hide it by returning "now"). Second possibility: the tool itself returned a pending task or cached value, so the hook measured only the cheap wrapper. Fix: measure inside the tool (`time.perf_counter()` around the I/O) or use a per-call id; confirm with a test that fires two calls of the same tool in one turn.

---

## ⚫ Interview Questions + Answers

**Q1:** What arguments does `on_tool_end` receive?

**A1:** `context` (RunContextWrapper), `agent`, `tool`, and `result` as a string.

**Q2:** Can you read the tool's input arguments in `on_tool_start`?

**A2:** Not in 0.24.0 - the hook gets the `tool` object, not the parsed call arguments. Log them inside the tool or in a wrapper.

**Q3:** How do you avoid logging PII from tool results?

**A3:** Redact in `on_tool_end` by tool name or regex before writing to logs, and truncate; never log raw `result` for sensitive tools.

**Q4:** How would you enforce "max 3 refund calls per run" with hooks?

**A4:** Keep a counter in the request context; increment in `on_tool_start` for `issue_refund`; raise a typed exception above 3, which aborts the run and is mapped to an HTTP error. A tool-level guard is stronger because it also covers non-hook paths.

**Q5:** System design: tool-level observability for 50 tools and 10k requests/min.

**A5:** RunHooks emits `{request_id, agent, tool, ms, ok, bytes}` to an async queue (no network in the hook). A consumer batches into a metrics store (histograms per tool, error rate), and a separate redacted audit stream goes to compliance storage. Alerts on p95 latency and error rate per tool.

---

## 💰 Cost Impact
The hooks add no model tokens. Value comes from what they reveal: tools whose big results get fed back to the model (every extra token is paid again on the next turn). Log `len(result)` and truncate or summarise large outputs inside the tool. Formula: extra cost per run is roughly `result_tokens x remaining_turns x input_price`. Prices approximate, from public pricing at time of writing - verify.

---

## 🔷 When to Use
✅ Use when:
- Per-tool latency and error metrics
- Audit trail with redaction
- Counting/limiting risky tool calls

❌ Avoid when:
- You need the arguments (log inside the tool instead)
- You want to change the tool result (do it in the tool)
- Heavy synchronous work would block the event loop

---

## 📊 Visual Diagram
```
  LLM: tool_call(get_tariff_rate, args)
          |
          v
   +----------------+   on_tool_start(ctx, agent, tool)
   |  RunHooks      |-----------------------------+
   +----------------+                             |
          |                                       v
          v                               start timer / audit
   +----------------+
   |  tool body     |  (your function, can be slow)
   +----------------+
          |
          v
   on_tool_end(ctx, agent, tool, result:str) --> stop timer, redact, append
          |
          v
   result -> back to LLM as tool output
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| on_tool_start | Hook before a tool runs | tool चलने से पहले का hook |
| on_tool_end | Hook after a tool returns | tool लौटने के बाद का hook |
| Redaction | Hiding sensitive values | संवेदनशील मान छिपाना |
| Audit trail | Record of tool actions | tool क्रियाओं का रिकॉर्ड |
| Parallel tool calls | Several tools in one turn | एक turn में कई tools |
| Request context | Per-request state object | per-request state object |

---

## ⚡ 3-Line Summary
English: on_tool_start and on_tool_end wrap every tool execution with agent, tool and result.
Use them for timing, audit and redaction; they cannot see arguments or change results.
Key timers by a unique id, not the tool name, if parallel calls are possible.

Hindi: on_tool_start और on_tool_end हर tool execution को agent, tool और result के साथ घेरते हैं।
Timing, audit और redaction के लिए इनका उपयोग करें; ये arguments नहीं देखते और result नहीं बदलते।
अगर parallel calls संभव हैं तो timers को tool name नहीं, unique id से key करें।

---

## ➡️ Next Topic
**#64 on_handoff** - the hook and callback fired when one agent transfers control to another, including typed handoff input.

---
