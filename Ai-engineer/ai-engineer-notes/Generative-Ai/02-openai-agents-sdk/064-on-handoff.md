---

# 64. on_handoff
# हिंदी में: on_handoff (agent बदलने पर callback)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. The "model decides to hand off" step is scripted, not a real LLM decision.

---

## 🔵 Simple Definition (2-3 lines)
A handoff transfers the conversation from one agent to another. There are two ways to observe it: the `on_handoff` callback passed to `handoff(...)` (fires for that one handoff, can receive typed input from the model) and the `RunHooks.on_handoff(context, from_agent, to_agent)` hook (fires for every handoff in the run).

## 🔵 सरल परिभाषा (Hindi)
Handoff बातचीत को एक agent से दूसरे agent को सौंप देता है। इसे देखने के दो तरीके हैं: `handoff(...)` में दिया गया `on_handoff` callback (सिर्फ़ उस handoff पर चलता है, और model से typed input पा सकता है) और `RunHooks.on_handoff(context, from_agent, to_agent)` hook (run के हर handoff पर चलता है)।

---

## 🔴 Problem it Solves
A handoff is a silent control transfer. Without a hook you cannot prefetch data for the next agent, record why the escalation happened, alert a human on high severity, or count how often triage routes to Legal. Also the next agent sees the whole earlier history including noisy tool calls unless you filter it.

## 🔴 यह क्यों बना? (Hindi)
Handoff चुपचाप control बदल देता है। Hook के बिना आप अगले agent के लिए data prefetch नहीं कर सकते, escalation का कारण record नहीं कर सकते, high severity पर इंसान को alert नहीं कर सकते, या यह नहीं गिन सकते कि triage कितनी बार Legal को भेजता है। साथ ही filter न लगाएँ तो अगला agent पिछला पूरा history (शोर वाली tool calls समेत) देखता है।

---

## 🟢 How it Works

```
Triage agent has handoffs=[handoff(legal, on_handoff=cb, input_type=EscalationData,
                                   input_filter=remove_all_tools)]
Step 1 -> SDK exposes a tool named transfer_to_<agent name snake_case> (e.g. transfer_to_legal)
Step 2 -> LLM calls it, optionally with JSON matching input_type
Step 3 -> SDK validates the JSON -> EscalationData
Step 4 -> your on_handoff callback runs (ctx, data)         <- per-handoff
Step 5 -> RunHooks.on_handoff(context, from_agent, to_agent) <- per-run hook
Step 6 -> input_filter edits the history the next agent will see
Step 7 -> Legal agent becomes the current agent; run continues
```

## 🟢 कैसे काम करता है? (Hindi)

```
Triage agent: handoffs=[handoff(legal, on_handoff=cb, input_type=EscalationData,
                                input_filter=remove_all_tools)]
Step 1 -> SDK transfer_to_<agent name snake_case> नाम का tool दिखाता है (जैसे transfer_to_legal)
Step 2 -> LLM उसे बुलाता है, चाहें तो input_type वाला JSON देकर
Step 3 -> SDK JSON validate करके EscalationData बनाता है
Step 4 -> आपका on_handoff callback चलता है (ctx, data)      <- per-handoff
Step 5 -> RunHooks.on_handoff(context, from_agent, to_agent)  <- per-run hook
Step 6 -> input_filter अगले agent को दिखने वाला history बदलता है
Step 7 -> Legal अब current agent है; run आगे चलता है
```

**Verified details (0.24.0):**
- Basic sample (b64) output: `callback: handoff to Legal fired`, `hook: Triage -> Legal`, then `Section 12 applies. | last agent: Legal`. So the per-handoff callback fired first, then the run hook.
- With `input_type`, the callback must accept `(ctx, data)`; without it, `(ctx)` only. `handoff_filters.remove_all_tools` comes from `agents.extensions.handoff_filters`.
- `result.last_agent` tells you who produced the final answer - use it in the API response.

**Hindi नोट:** `input_type` का मतलब है कि model को handoff करते समय structured जानकारी (कारण, severity) भरनी पड़ती है; यह "फिर से पूछना" बचाता है। Callback में भारी काम न करें; जहाँ ज़रूरत हो वहाँ background task में डालें।

---

## 🟡 Real World Example
**Tariff Agent.** `Triage` sees "Can I import from a sanctioned entity?" and hands off to `Legal` with `{"reason": "possible sanctions hit", "severity": 4}`. The callback stores that in the request context for audit and could page compliance when severity >= 4. The filter removes earlier tool calls so Legal starts with a clean conversation.

**Customer Support Agent:** Billing hands off to Human-Escalation with `{"ticket_id", "sentiment"}`; the callback creates the CRM ticket before the human agent even speaks.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `Triage` को "क्या मैं sanctioned entity से import कर सकता हूँ?" दिखता है और वह `Legal` को handoff करता है `{"reason": "possible sanctions hit", "severity": 4}` के साथ। Callback इसे audit के लिए request context में रखता है और severity >= 4 पर compliance को page कर सकता है। Filter पुरानी tool calls हटा देता है ताकि Legal साफ़ बातचीत से शुरू करे।

**Customer Support Agent:** Billing, Human-Escalation को `{"ticket_id", "sentiment"}` के साथ handoff करता है; callback इंसान के बोलने से पहले ही CRM ticket बना देता है।

---

## 💻 Code Example — Basic
Runs offline. Shows both observation points.

```python
# Basic: on_handoff - two ways to observe a handoff (offline).
# verified against openai-agents 0.24.0
import asyncio
from typing import Any
from agents import Agent, RunContextWrapper, RunHooks, Runner, handoff, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

specialist = Agent(name="Legal", instructions="Answer legal questions.", model=ScriptedModel([[text("Section 12 applies.")]]))

def announce(ctx: RunContextWrapper[Any]) -> None:                # way 1: callback attached to ONE handoff (runs when it fires)
    print("callback: handoff to Legal fired")

class Hooks(RunHooks[Any]):                                       # way 2: hook for EVERY handoff in the run
    async def on_handoff(self, context: RunContextWrapper[Any], from_agent: Agent[Any], to_agent: Agent[Any]) -> None:
        print(f"hook: {from_agent.name} -> {to_agent.name}")

triage_model = ScriptedModel([[tool_call("transfer_to_legal", "{}")]])   # tool name = transfer_to_<agent name, snake_case>
triage = Agent(name="Triage", instructions="Route.", model=triage_model,
               handoffs=[handoff(specialist, on_handoff=announce)])
result = asyncio.run(Runner.run(triage, "Is this import banned?", hooks=Hooks()))
print(result.final_output, "| last agent:", result.last_agent.name)
```

## 💻 Code Example — Advanced
FastAPI with typed handoff input, an audit callback and an input filter. Output: `{'answer': 'Escalated to compliance.', 'last_agent': 'Legal', 'handoffs': [{'to': 'Legal', 'reason': 'possible sanctions hit', 'severity': 4}]}`.

```python
# Advanced: handoff with typed input (input_type), audit callback, input filter, FastAPI.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
from dataclasses import dataclass, field
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, Runner, handoff, set_tracing_disabled
from agents.extensions import handoff_filters                     # ready-made input filters
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

class EscalationData(BaseModel):                                  # the LLM must fill this when it hands off
    reason: str
    severity: int

@dataclass
class Ctx:
    handoffs: list[dict[str, Any]] = field(default_factory=list)

async def on_escalate(ctx: RunContextWrapper[Ctx], data: EscalationData) -> None:   # called with parsed model arguments
    ctx.context.handoffs.append({"to": "Legal", "reason": data.reason, "severity": data.severity})   # persist for audit/alerts

def build(triage_model: Any, legal_model: Any) -> Agent[Ctx]:
    legal = Agent[Ctx](name="Legal", instructions="Legal review.", model=legal_model)
    return Agent[Ctx](
        name="Triage", instructions="Hand off sanctions questions.", model=triage_model,
        handoffs=[handoff(legal, on_handoff=on_escalate, input_type=EscalationData,
                          input_filter=handoff_filters.remove_all_tools)],   # hide earlier tool noise from the next agent
    )

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, Any]:
    t = ScriptedModel([[tool_call("transfer_to_legal", '{"reason":"possible sanctions hit","severity":4}')]])
    l = ScriptedModel([[text("Escalated to compliance.")]])
    ctx = Ctx()
    res = await Runner.run(build(t, l), q.question, context=ctx, max_turns=5)
    return {"answer": res.final_output, "last_agent": res.last_agent.name, "handoffs": ctx.handoffs}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/ask", json={"question": "Import from sanctioned entity?"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Agent-to-agent transfer | `Command(goto=...)` / conditional edges | Delegation to another agent / hierarchical process | `handoff()` as a tool call | `Swarm` handoff messages / `HandoffMessage` |
| Observe the transfer | Node transition in stream/callbacks | Task/agent callbacks | `on_handoff` callback + `RunHooks.on_handoff` | Handoff message in the stream |
| Typed payload | State schema | Task context | `input_type` (Pydantic) | Message content |
| Who decides | Code (edges) or LLM | Manager LLM / process | The LLM (tool call) | The LLM (handoff tool) |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Giving an `input_type` but writing the callback as `def cb(ctx)`.
✅ Correct: With `input_type`, the callback takes `(ctx, data)`; without it, only `(ctx)`.

❌ Mistake 2: Assuming the handoff tool is named after the Python variable.
✅ Correct: It is `transfer_to_` + the agent `name` in snake_case (`Legal` becomes `transfer_to_legal`). Scripted tests and prompts must use that name.

❌ Mistake 3: Returning `result.final_output` without saying who wrote it.
✅ Correct: Also return `result.last_agent.name` so the client and logs know which specialist answered.

❌ Mistake 4: Letting the next agent inherit all noisy tool history.
✅ Correct: Use `input_filter` (for example `handoff_filters.remove_all_tools`) to cut tokens and confusion.

---

## 🧠 Tricky Interview Question
Triage hands off to Legal, Legal hands back to Triage, and the run keeps ping-ponging until `MaxTurnsExceeded`. How do you prevent this?

**Answer:** Ping-pong happens when both agents list each other in `handoffs` and neither instruction says when to stop. Fixes: (1) make routing one-directional unless a real loop is intended, (2) give each specialist explicit "answer, do not transfer back" instructions, (3) set a low `max_turns` and handle `MaxTurnsExceeded` (see #66), (4) count handoffs in `RunHooks.on_handoff` and raise after N, (5) use `is_enabled` or a per-handoff condition to remove the handoff after it has been used once. Detect it in tests with a scripted model that loops.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the tool name for handing off to an agent called "Legal"?

**A1:** `transfer_to_legal` (prefix plus snake-cased agent name).

**Q2:** Callback vs `RunHooks.on_handoff`?

**A2:** The callback is attached to one `handoff(...)` and can receive typed model input; the hook sees every handoff in the run but only gets `from_agent` and `to_agent`.

**Q3:** What does `input_filter` do?

**A3:** It rewrites the conversation history the next agent receives (for example removing tool calls) to save tokens and avoid confusion.

**Q4:** How do you make the model supply a reason when it hands off?

**A4:** Pass `input_type=` a Pydantic model; the SDK adds it to the handoff tool schema and passes the validated object to your callback.

**Q5:** System design: escalation to humans with audit.

**A5:** Triage hands off to an Escalation agent with typed `{reason, severity, ticket_id}`. The callback writes to a DB/queue and returns quickly; a worker pages on-call for severity >= 4. API returns `last_agent` and ticket id. Add a handoff counter to prevent loops, and an input filter so the human summary has no raw tool dumps.

---

## 💰 Cost Impact
Each handoff costs one extra LLM turn (the triage model call that emits the handoff) plus the next agent's own calls; the next agent re-reads the history as input tokens. An `input_filter` that drops tool noise cuts those input tokens. Rough formula: `extra = history_tokens x input_price + triage_turn_cost`. Route with a cheap small model for triage, stronger model for the specialist. Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Specialist agents own different domains
- You need an audit of why an escalation happened
- Next agent needs a clean, filtered history

❌ Avoid when:
- A simple tool call would do (no need for a new persona)
- Routing is deterministic (use code routing; see #68)
- Agents can hand back and forth without a guard

---

## 📊 Visual Diagram
```
   user -> [Triage]
              | LLM calls transfer_to_legal({"reason","severity"})
              v
        validate input_type  -> EscalationData
              |
              +--> handoff(on_handoff=cb)  ........ per-handoff callback
              +--> RunHooks.on_handoff(from, to) .. per-run hook
              +--> input_filter(history)  ......... trim what Legal sees
              v
           [Legal]  -> final answer  (result.last_agent = Legal)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Handoff | Transfer control to another agent | दूसरे agent को control सौंपना |
| on_handoff | Callback when a handoff fires | handoff पर callback |
| input_type | Typed data the LLM supplies | LLM द्वारा दिया typed data |
| input_filter | Edits history for next agent | अगले agent का history बदलता है |
| last_agent | Agent that produced the answer | जिसने जवाब दिया वह agent |
| Escalation | Move to a higher authority | उच्च स्तर पर भेजना |

---

## ⚡ 3-Line Summary
English: A handoff is a tool call that switches the active agent; observe it with a per-handoff callback or RunHooks.on_handoff.
Typed input_type forces the model to explain the transfer, and input_filter trims history.
Guard against ping-pong with one-way routing, counters and max_turns.

Hindi: Handoff एक tool call है जो active agent बदलता है; इसे per-handoff callback या RunHooks.on_handoff से देखें।
Typed input_type model से transfer का कारण भरवाता है, और input_filter history छोटा करता है।
Ping-pong से बचने के लिए एकतरफ़ा routing, counters और max_turns रखें।

---

## ➡️ Next Topic
**#65 SDK + FastAPI Integration** - lifespan, dependency injection, sessions and streaming so all these agents become a real HTTP service.

---
