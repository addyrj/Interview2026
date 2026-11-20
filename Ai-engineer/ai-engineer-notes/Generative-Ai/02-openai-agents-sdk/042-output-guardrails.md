---

# 42. Output Guardrails
# हिंदी में: Output Guardrails (आउटपुट जाँच)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). `output_guardrail` signature read with `inspect.signature`. All code ran offline with `agents.testing.ScriptedModel`, so the "leaking" answers are scripted. How often a real model leaks is not measured here, and a real model call needs `OPENAI_API_KEY` (not run).

---

## 🔵 Simple Definition (2-3 lines)
An output guardrail is a function attached to an `Agent` that inspects the agent's final output after it is produced and returns `GuardrailFunctionOutput(tripwire_triggered=True/False)`. If the tripwire fires, the run raises `OutputGuardrailTripwireTriggered` and your code decides what the user sees instead. Output guardrails run only on the last agent's final output.

## 🔵 सरल परिभाषा (Hindi)
Output guardrail एक function है जो `Agent` से जुड़ता है और agent का final output बनने के बाद उसे जाँचकर `GuardrailFunctionOutput(tripwire_triggered=True/False)` लौटाता है। Tripwire चालू हुआ तो run `OutputGuardrailTripwireTriggered` उठाता है और user को क्या दिखे यह आपका code तय करता है। Output guardrails सिर्फ आखिरी agent के final output पर चलते हैं।

---

## 🔴 Problem it Solves
Even a well-prompted model can leak internal notes, secrets, PII, or produce unsafe or off-format text. Prompts are requests, not guarantees. Checking the final answer before it reaches the user gives a last line of defence and a clean place to log and measure such failures.

## 🔴 यह क्यों बना? (Hindi)
अच्छे prompt वाला model भी internal notes, secrets, PII leak कर सकता है या असुरक्षित/गलत format का text दे सकता है। Prompt अनुरोध है, गारंटी नहीं। User तक पहुँचने से पहले final answer जाँचना आखिरी सुरक्षा परत देता है और ऐसी गलतियों को log और measure करने की साफ जगह भी।

---

## 🟢 How it Works

```
@output_guardrail(name=None)                          (signature from 0.24.0)
async def g(ctx, agent, output) -> GuardrailFunctionOutput(output_info=..., tripwire_triggered=bool)

Step 1 -> Agent(output_guardrails=[g])
Step 2 -> Runner.run ... the agent loop finishes with a final output (str or output_type object)
Step 3 -> SDK calls g(ctx, agent, final_output) for each output guardrail of the LAST agent
Step 4 -> tripwire_triggered=True -> raises OutputGuardrailTripwireTriggered(exc.guardrail_result)
Step 5 -> your except block: log, retry once, or return a canned fallback (the leaked text is never returned)
Step 6 -> otherwise result.output_guardrail_results lists each guardrail and its output
```

## 🟢 कैसे काम करता है? (Hindi)

```
@output_guardrail(name=None)                          (signature 0.24.0 से)
async def g(ctx, agent, output) -> GuardrailFunctionOutput(output_info=..., tripwire_triggered=bool)

Step 1 -> Agent(output_guardrails=[g])
Step 2 -> Runner.run ... agent loop final output (str या output_type object) के साथ खत्म होता है
Step 3 -> SDK आखिरी agent के हर output guardrail पर g(ctx, agent, final_output) चलाता है
Step 4 -> tripwire_triggered=True -> OutputGuardrailTripwireTriggered उठता है (exc.guardrail_result)
Step 5 -> आपका except block: log करें, एक बार retry करें, या canned fallback लौटाएँ (leak हुआ text कभी नहीं जाता)
Step 6 -> वरना result.output_guardrail_results में हर guardrail और उसका नतीजा
```

**Verified facts (0.24.0):**
- Output guardrail signature: `(ctx: RunContextWrapper, agent: Agent, output) -> GuardrailFunctionOutput`. With `output_type=TariffAnswer` the `output` argument was the typed pydantic object; with no `output_type` it was a plain `str`.
- A tripped guardrail raised `OutputGuardrailTripwireTriggered`; `exc.guardrail_result.output.output_info` and `exc.guardrail_result.agent.name` were readable (ran both).
- `result.output_guardrail_results` lists `(guardrail, output)` for passes.
- After a handoff only the LAST agent's output guardrail ran: triage had `guard_on_triage`, specialist had `guard_on_tariff`; the executed list was `['guard_on_tariff']` (third snippet).
- Unlike input guardrails there is no `run_in_parallel` option on `output_guardrail` (its signature is `func`, `name` only); it necessarily runs after the final output exists, so the model cost is already spent when it trips.
- `RunConfig` also has `output_guardrails` for run-wide guardrails and an `output_guardrail_blocked_message` field (present in 0.24.0's `RunConfig`; we did not test its behaviour, check the source/docs before relying on it).
- Retrying with a fresh `Runner.run` after a trip worked in our demo (second scripted answer was clean). A real retry costs a full new run.

**Connect to what you know:** like a LangGraph final "validator" node with a conditional edge back to the generator or to a fallback node, or a pydantic validator on the response model in FastAPI, but evaluated by the SDK around the agent.

---

## 🟡 Real World Example
**Tariff Agent.** The portal must never show internal pricing notes. An output guardrail scans the final answer for `internal`, `margin` and key-like strings. On a trip the API logs the rule name, retries once with a stricter request, and if it trips again returns "Sorry, I cannot share that. Please contact customs support." The user never sees the leaked text.

**Customer Support:** block competitor mentions or promises of refunds; **Research Agent:** block unsupported claims without citations.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Portal को internal pricing notes कभी नहीं दिखाने चाहिए। Output guardrail final answer में `internal`, `margin` और key जैसे strings ढूँढता है। Trip होने पर API rule का नाम log करती है, ज़्यादा सख्त अनुरोध से एक बार retry करती है, और फिर भी trip हो तो "Sorry, I cannot share that. Please contact customs support." लौटाती है। User को leak हुआ text कभी नहीं दिखता।

**Customer Support:** competitors का ज़िक्र या refund के वादे रोकें; **Research Agent:** बिना citation के दावे रोकें।

---

## 💻 Code Example — Basic
Typed output (`output_type`) checked by an output guardrail; pass and block cases. Runs offline.

```python
# Basic: an output guardrail that blocks internal data leaking from the Tariff Agent (runs offline)
from pydantic import BaseModel                           # typed final output
from agents import (Agent, Runner, GuardrailFunctionOutput, RunContextWrapper,
                    OutputGuardrailTripwireTriggered, output_guardrail,
                    set_tracing_disabled)                # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

class TariffAnswer(BaseModel):                           # the agent's structured final output
    hs_code: str
    duty_percent: float
    note: str

@output_guardrail                                        # runs on the LAST agent's final output
async def no_internal_notes(ctx: RunContextWrapper[None], agent: Agent,
                            output: TariffAnswer) -> GuardrailFunctionOutput:
    leaked = "INTERNAL" in output.note.upper()           # simple rule; production: classifier or regex set
    return GuardrailFunctionOutput(output_info={"leaked": leaked, "hs_code": output.hs_code},  # kept for logs
                                   tripwire_triggered=leaked)  # True -> raise, user never sees the answer

def make_agent(answer_json: str) -> Agent:
    return Agent(name="Tariff Agent", instructions="Answer as JSON.", output_type=TariffAnswer,
                 output_guardrails=[no_internal_notes],  # attach to the agent that produces the final output
                 model=ScriptedModel([[assistant_message(answer_json)]]))

good = Runner.run_sync(make_agent('{"hs_code": "6109", "duty_percent": 12.0, "note": "cotton t-shirts"}'),
                       "Duty on HS 6109?")               # guardrail passes
print("allowed:", good.final_output.duty_percent)        # 12.0
print("results:", [(r.guardrail.get_name(), r.output.tripwire_triggered) for r in good.output_guardrail_results])

try:
    Runner.run_sync(make_agent('{"hs_code": "6109", "duty_percent": 12.0, "note": "INTERNAL: margin 30%"}'),
                    "Duty on HS 6109?")                  # model leaked an internal note
except OutputGuardrailTripwireTriggered as exc:          # raised instead of returning the answer
    info = exc.guardrail_result.output.output_info       # why it tripped
    print("blocked:", info)                              # {'leaked': True, 'hs_code': '6109'}
    print("agent that produced it:", exc.guardrail_result.agent.name)  # Tariff Agent
```

## 💻 Code Example — Advanced
FastAPI with two output guardrails (secret patterns, length), one safe retry, canned fallback, error handling. Runs offline via `TestClient`. The `leak_first` flag only scripts the fake model.

```python
# Advanced: output guardrails in FastAPI with one safe retry and a canned fallback (runs offline)
import re                                                # rule-based leak detection
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Runner, GuardrailFunctionOutput, RunContextWrapper,
                    OutputGuardrailTripwireTriggered, AgentsException, output_guardrail,
                    set_tracing_disabled)                # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

SECRET = re.compile(r"(internal|margin|api[_-]?key|sk-[A-Za-z0-9]{8,})", re.I)  # demo patterns, extend for real use

@output_guardrail(name="no_secrets")
async def no_secrets(ctx: RunContextWrapper[None], agent: Agent, output: str) -> GuardrailFunctionOutput:
    hit = SECRET.search(output)                          # plain string output in this example
    return GuardrailFunctionOutput(output_info={"match": hit.group(0) if hit else None},
                                   tripwire_triggered=hit is not None)

@output_guardrail(name="max_answer_length")
async def max_len(ctx: RunContextWrapper[None], agent: Agent, output: str) -> GuardrailFunctionOutput:
    return GuardrailFunctionOutput(output_info={"chars": len(output)}, tripwire_triggered=len(output) > 1200)

def make_agent(first_answer: str, retry_answer: str) -> Agent:  # scripted: first answer leaks, retry is clean
    return Agent(name="Tariff Agent", instructions="Answer duty questions. Never reveal internal data.",
                 output_guardrails=[no_secrets, max_len],
                 model=ScriptedModel([[assistant_message(first_answer)], [assistant_message(retry_answer)]]))

class In(BaseModel):
    message: str
    leak_first: bool = False                             # demo switch: make the first answer leak

class Out(BaseModel):
    answer: str
    retried: bool

app = FastAPI()
FALLBACK = "Sorry, I cannot share that. Please contact customs support."  # safe canned reply

@app.post("/ask", response_model=Out)
async def ask(body: In) -> Out:
    first = "INTERNAL margin is 30%. Duty is 12%." if body.leak_first else "HS 6109 duty is 12%."
    agent = make_agent(first, "HS 6109 duty is 12%.")
    try:
        r = await Runner.run(agent, body.message, max_turns=3)
        return Out(answer=r.final_output, retried=False)  # first attempt passed
    except OutputGuardrailTripwireTriggered as exc:      # the answer was blocked, the user saw nothing
        reason = exc.guardrail_result.guardrail.get_name()  # for logs and metrics
        print("blocked by", reason)                      # production: structured log, never the raw secret
        try:                                             # one retry with a fresh run (new model call)
            r2 = await Runner.run(agent, body.message + " (do not include internal data)", max_turns=3)
            return Out(answer=r2.final_output, retried=True)
        except OutputGuardrailTripwireTriggered:         # still unsafe -> canned fallback, never the raw text
            return Out(answer=FALLBACK, retried=True)
        except AgentsException as exc2:
            raise HTTPException(502, type(exc2).__name__)
    except AgentsException as exc:
        raise HTTPException(502, type(exc).__name__)

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.post("/ask", json={"message": "HS 6109?"}).json())                    # clean, no retry
    print(c.post("/ask", json={"message": "HS 6109?", "leak_first": True}).json())  # blocked, retry succeeds
```

Third snippet: only the last agent's output guardrails run after a handoff.

```python
# Which agent's output guardrails run after a handoff? (runs offline)
from agents import (Agent, Runner, GuardrailFunctionOutput, output_guardrail,
                    set_tracing_disabled)                # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo
ran: list[str] = []                                      # records which guardrails executed

def make(name: str):                                     # one guardrail per agent, same rule: never trips
    @output_guardrail(name=f"guard_on_{name}")
    async def g(ctx, agent, output) -> GuardrailFunctionOutput:
        ran.append(f"guard_on_{name}")                   # note that this guardrail executed
        return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)
    return g

specialist = Agent(name="Tariff Agent", output_guardrails=[make("tariff")],
                   model=ScriptedModel([[assistant_message("HS 6109 duty is 12%.")]]))
triage = Agent(name="Triage Agent", handoffs=[specialist], output_guardrails=[make("triage")],
               model=ScriptedModel([[function_call("transfer_to_tariff_agent", {}, call_id="h1")]]))

result = Runner.run_sync(triage, "Duty on HS 6109?")     # triage hands off, specialist answers
print("final agent        :", result.last_agent.name)    # Tariff Agent
print("guardrails executed:", ran)                       # only the last agent's guardrail
```

Observed: `guardrails executed: ['guard_on_tariff']`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Output validation | Validator node + conditional edge | Task `guardrail` function / `output_pydantic` | `output_guardrails` on agent | Custom agent or termination hook |
| Tripwire exception | You raise/route yourself | Retries then fails task | `OutputGuardrailTripwireTriggered` | You raise |
| Retry on failure | Loop edge back to generator | Built-in guardrail retries (configurable) | Your `except` block re-runs | Your logic |
| Applies to | Any node you wire | Task output | Last agent's final output | Whatever you code |
| Result inspection | State | Task output | `result.output_guardrail_results` | Messages |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Putting the output guardrail on the triage agent when a specialist produces the answer.
✅ Correct: Attach it to every agent that can be the last one (verified: only the last agent's guardrail runs), or use `RunConfig(output_guardrails=[...])` for run-wide checks.

❌ Mistake 2: Returning the blocked text in the error response or logs.
✅ Correct: Log the guardrail name and `output_info` (match type, counts), never the secret itself.

❌ Mistake 3: Expecting to save tokens.
✅ Correct: The model already produced the answer; the trip only protects the user. Combine with input guardrails and good prompts to reduce trips.

❌ Mistake 4: Unlimited retries after a trip.
✅ Correct: At most one retry, then a fallback message.

❌ Mistake 5: Assuming streaming is covered the same way.
✅ Correct: Tokens streamed to the client before the final output exists have already been shown; for strict safety buffer the stream or do not stream to the end user until the output guardrail passes. (We did not run output guardrails with `run_streamed` here, test your own setup.)

---

## 🧠 Tricky Interview Question
Your output guardrail blocks ~2% of answers. Product says "just retry silently until it passes". What is wrong with that, and what would you do?

**Answer:** Each retry is a full extra run: more latency and tokens, and an attacker who can trigger leaks gets unlimited attempts to find one that slips past a weak rule. Also, repeated retries hide a prompt or retrieval bug that is causing the leaks. Do: one retry at most with a tighter instruction, then a safe fallback; log the rule and the rate per rule; investigate the top causes (for example a tool returning internal fields; filter them at the tool instead of at the output); strengthen detection beyond regex with a small classifier for sensitive categories; and add the failing cases to the eval set so fixes are measurable.

---

## ⚫ Interview Questions + Answers

**Q1:** What does an output guardrail receive?

**A1:** `(ctx, agent, output)` where `output` is the agent's final output: a `str`, or the `output_type` object when set.

**Q2:** Which agent's output guardrails run in a handoff chain?

**A2:** Only the last agent's (verified with triage and specialist guardrails).

**Q3:** What exception is raised and what do you do with it?

**A3:** `OutputGuardrailTripwireTriggered`. Catch it, log `exc.guardrail_result` info (not the raw text), retry at most once or return a canned fallback.

**Q4:** Input versus output guardrail?

**A4:** Input: checks the user's message, first agent only, can run in parallel or blocking, can save model cost. Output: checks the final answer of the last agent, runs after generation, protects the user but does not save generation cost.

**Q5:** Design the safety layer for a public tariff chatbot.

**A5:** Input rules and a small topic/injection classifier; least-privilege tools that never return internal fields; output guardrails (secrets/PII regex plus a small classifier) on every possible final agent; one retry then fallback; HTTP responses without raw blocked text; dashboards of trips per rule; red-team eval set run in CI with scripted and real models.

---

## 💰 Cost Impact
Rule-based output guardrails cost no tokens. LLM-based ones add a checker call whose input is the full answer (cost grows with answer length). A trip means the generation cost was already paid, and a retry doubles it. Approximate, from public pricing at time of writing, verify; track `usage` for main run, checker and retries separately.

**Tips:** rules first, small model for classification, prevent leaks upstream (tool filtering, instructions), cap retries at one, keep answers short with `max_tokens`.

---

## 🔷 When to Use
✅ Use when:
- The answer goes to external users and must not leak data or break policy
- You need a typed, loggable reason when an answer is rejected
- Output format must be enforced beyond what `output_type` guarantees

❌ Avoid when:
- A pydantic `output_type` already enforces everything you need
- You are streaming raw tokens to users and cannot buffer (it cannot protect those tokens)

---

## 📊 Visual Diagram
```
 user -> input guardrails -> agent loop (tools, handoffs)
                                  |
                          final output (str / output_type)
                                  |
                 +--- output guardrails (LAST agent only) ---+
                 | rules (regex, length): 0 tokens          |
                 | checker agent (small): few tokens        |
                 +-------------------+----------------------+
                         pass        |          trip
                          |          v            |
                 return answer   OutputGuardrailTripwireTriggered
                                        |
                          log -> retry once -> canned fallback
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| output guardrail | Check on the final answer | final answer की जाँच |
| tripwire | Flag that raises an exception | exception उठाने वाला संकेत |
| output_info | Details for logging the decision | निर्णय का ब्योरा |
| fallback | Safe canned reply when blocked | रोके जाने पर सुरक्षित तैयार उत्तर |
| leak | Unintended exposure of internal data | internal डेटा का अनचाहा बाहर आना |
| last agent | Agent that produced the final output | final output बनाने वाला agent |

---

## ⚡ 3-Line Summary
English: Output guardrails check the last agent's final answer and raise a tripwire exception when it is unsafe.
Attach them to every agent that can be last; retry at most once, then return a canned fallback.
They protect users but do not save generation tokens, so prevent leaks upstream too.

Hindi: Output guardrails आखिरी agent का final answer जाँचते हैं और असुरक्षित होने पर tripwire exception उठाते हैं।
इन्हें हर उस agent पर लगाएँ जो आखिरी हो सकता है; ज़्यादा से ज़्यादा एक retry, फिर canned fallback।
ये users को बचाते हैं पर generation tokens नहीं बचाते, इसलिए leaks को upstream भी रोकें।

---

## ➡️ Next Topic
**#43 Guardrail Tripwire** - a deeper look at tripwire exceptions, what data they carry, how to log and respond to them, and tool-level guardrails.

---
