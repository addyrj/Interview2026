---

# 41. Input Guardrails
# हिंदी में: Input Guardrails (इनपुट जाँच)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). `input_guardrail` signature read with `inspect.signature`. All code ran offline with `agents.testing.ScriptedModel`; the "checker agent" in the basic example is a scripted model, so its judgement quality is not tested. A real classifier model needs `OPENAI_API_KEY` (not run).

---

## 🔵 Simple Definition (2-3 lines)
An input guardrail is a function attached to an `Agent` that inspects the user's input before (or alongside) the agent's work and returns a `GuardrailFunctionOutput(tripwire_triggered=True/False)`. If the tripwire is triggered, the run stops with `InputGuardrailTripwireTriggered`. Input guardrails run only on the first agent of a run.

## 🔵 सरल परिभाषा (Hindi)
Input guardrail एक function है जो `Agent` से जुड़ता है और agent के काम से पहले (या साथ-साथ) user के input को जाँचकर `GuardrailFunctionOutput(tripwire_triggered=True/False)` लौटाता है। Tripwire चालू हुआ तो run `InputGuardrailTripwireTriggered` के साथ रुक जाता है। Input guardrails सिर्फ run के पहले agent पर चलते हैं।

---

## 🔴 Problem it Solves
Without checks, an expensive agent happily processes off-topic requests ("write me a poem"), prompt-injection attempts, or messages containing card numbers, wasting tokens and creating risk. Checking input first, ideally with a cheap rule or a small model, protects cost and safety.

## 🔴 यह क्यों बना? (Hindi)
जाँच न हो तो महँगा agent off-topic अनुरोध ("मुझे कविता लिखो"), prompt-injection की कोशिशें, या card numbers वाले संदेश भी खुशी से process करता है, जिससे tokens बर्बाद होते हैं और जोखिम बढ़ता है। पहले input जाँचना, अच्छा हो तो सस्ते rule या छोटे model से, cost और safety दोनों बचाता है।

---

## 🟢 How it Works

```
@input_guardrail(name=None, run_in_parallel=True)      (signature from 0.24.0)
async def g(ctx, agent, user_input) -> GuardrailFunctionOutput(output_info=..., tripwire_triggered=bool)

Step 1 -> Agent(input_guardrails=[g])
Step 2 -> Runner.run(agent, input) starts
Step 3a -> run_in_parallel=True  (default): guardrail runs CONCURRENTLY with the first model call
Step 3b -> run_in_parallel=False: guardrail finishes FIRST; the model is not called if it trips
Step 4 -> tripwire_triggered=True -> raises InputGuardrailTripwireTriggered (exc.guardrail_result)
Step 5 -> otherwise the run continues; results in result.input_guardrail_results
Note   -> only the FIRST agent's input guardrails run; after a handoff they do not run again
```

## 🟢 कैसे काम करता है? (Hindi)

```
@input_guardrail(name=None, run_in_parallel=True)      (signature 0.24.0 से)
async def g(ctx, agent, user_input) -> GuardrailFunctionOutput(output_info=..., tripwire_triggered=bool)

Step 1 -> Agent(input_guardrails=[g])
Step 2 -> Runner.run(agent, input) शुरू
Step 3a -> run_in_parallel=True (default): guardrail पहली model call के साथ-साथ चलता है
Step 3b -> run_in_parallel=False: guardrail पहले खत्म होता है; trip हुआ तो model call नहीं होती
Step 4 -> tripwire_triggered=True -> InputGuardrailTripwireTriggered उठता है (exc.guardrail_result)
Step 5 -> वरना run आगे बढ़ता है; नतीजे result.input_guardrail_results में
Note   -> सिर्फ पहले agent के input guardrails चलते हैं; handoff के बाद दोबारा नहीं
```

**Verified facts (0.24.0):**
- Guardrail function signature: `(ctx: RunContextWrapper, agent: Agent, user_input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput`; sync or async both accepted by the decorator type hints.
- `GuardrailFunctionOutput` has exactly two fields: `output_info` (any object, kept for logging) and `tripwire_triggered` (bool).
- When blocked, the run raises `InputGuardrailTripwireTriggered`; `exc.guardrail_result.guardrail.get_name()` gives the rule name and `exc.guardrail_result.output.output_info` the details (ran both).
- On success, `result.input_guardrail_results` lists each guardrail with its output.
- Measured with a scripted main model and a guardrail that always trips after a 50 ms delay: `run_in_parallel=False` gave 0 main-model calls; `run_in_parallel=True` gave 1 main-model call (already started, so its tokens are spent). This is the key cost trade-off.
- A guardrail can itself call `Runner.run` on a small checker agent with `output_type`; that is the pattern in the basic example.
- Rule-based guardrails (regex, length) cost no tokens and no extra latency.

**Connect to what you know:** like a FastAPI dependency or middleware that validates the request before the handler, except it can use an LLM. In LangGraph you would add a first "guard" node with a conditional edge to END.

---

## 🟡 Real World Example
**Tariff Agent.** The portal accepts only customs questions. A small checker agent flags "off-topic" messages (poems, homework). A regex guardrail blocks messages containing card numbers before any model sees them (blocking mode), and a length guardrail blocks pasted novels (parallel mode). The API returns HTTP 400 with the rule name.

**Customer Support:** block abuse and prompt-injection phrases; **Research Agent:** block disallowed domains.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Portal सिर्फ customs सवाल लेता है। एक छोटा checker agent off-topic संदेश (कविता, homework) पकड़ता है। एक regex guardrail card numbers वाले संदेशों को किसी model के देखने से पहले रोक देता है (blocking mode), और length guardrail लंबे संदेश रोकता है (parallel mode)। API rule के नाम के साथ HTTP 400 लौटाता है।

**Customer Support:** गाली-गलौज और prompt-injection वाक्यांश रोकें; **Research Agent:** मना किए गए domains रोकें।

---

## 💻 Code Example — Basic
A checker agent as guardrail: allowed request passes, off-topic request raises. Runs offline (checker verdict scripted).

```python
# Basic: an input guardrail (cheap checker agent) in front of the Tariff Agent (runs offline)
from pydantic import BaseModel                           # structured verdict from the checker agent
from agents import (Agent, Runner, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem,
                    InputGuardrailTripwireTriggered, input_guardrail,
                    set_tracing_disabled)                # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

class OffTopic(BaseModel):                               # what the checker agent must return
    is_off_topic: bool
    reason: str

def make_checker(verdict_json: str) -> Agent:            # small, cheap agent whose only job is classifying
    return Agent(name="Topic Checker", instructions="Is the message about customs duty/tariffs? JSON only.",
                 output_type=OffTopic, model=ScriptedModel([[assistant_message(verdict_json)]]))

@input_guardrail                                         # registers this function as an input guardrail
async def topic_guardrail(ctx: RunContextWrapper[None], agent: Agent,
                          user_input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    checker = make_checker(CHECKER_VERDICT["json"])      # production: a small real model, not a script
    result = await Runner.run(checker, user_input, context=ctx.context)  # run the checker like any agent
    verdict: OffTopic = result.final_output              # typed verdict
    return GuardrailFunctionOutput(output_info=verdict,  # kept on the result for logging
                                   tripwire_triggered=verdict.is_off_topic)  # True -> stop the run

CHECKER_VERDICT = {"json": ""}                           # demo switch for the scripted checker

tariff = Agent(name="Tariff Agent", instructions="Answer customs duty questions.",
               input_guardrails=[topic_guardrail],       # runs on the FIRST agent of a run
               model=ScriptedModel([[assistant_message("HS 6109 duty is 12%.")]] * 2))

CHECKER_VERDICT["json"] = '{"is_off_topic": false, "reason": "customs question"}'
ok = Runner.run_sync(tariff, "Duty on HS 6109?")         # guardrail passes, agent answers
print("allowed :", ok.final_output)
print("guardrail results:", [(r.guardrail.get_name(), r.output.tripwire_triggered) for r in ok.input_guardrail_results])

CHECKER_VERDICT["json"] = '{"is_off_topic": true, "reason": "asks for a poem"}'
try:
    Runner.run_sync(tariff, "Write me a poem about the moon")  # guardrail trips
except InputGuardrailTripwireTriggered as exc:           # raised instead of returning a result
    info: OffTopic = exc.guardrail_result.output.output_info  # see why it tripped
    print("blocked :", info.reason)                      # asks for a poem
```

## 💻 Code Example — Advanced
Rule-based guardrails (regex, length), blocking vs parallel mode, FastAPI returning 400, error handling, model call counting. Runs offline via `TestClient`.

```python
# Advanced: rule-based input guardrails, parallel vs blocking mode, FastAPI 400 mapping (runs offline)
import re                                                # cheap rule-based check
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Runner, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem,
                    InputGuardrailTripwireTriggered, AgentsException, input_guardrail,
                    set_tracing_disabled)                # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")             # naive card-number pattern (demo, not production PII detection)

def as_text(user_input: str | list[TResponseInputItem]) -> str:  # input can be a string or a list of items
    if isinstance(user_input, str):
        return user_input
    return " ".join(str(item.get("content", "")) for item in user_input if isinstance(item, dict))

@input_guardrail(name="no_card_numbers", run_in_parallel=False)  # blocking: agent never starts if it trips
async def no_card_numbers(ctx: RunContextWrapper[None], agent: Agent,
                          user_input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    hit = bool(CARD.search(as_text(user_input)))         # no LLM call = no token cost, no latency
    return GuardrailFunctionOutput(output_info={"pattern": "card_number"}, tripwire_triggered=hit)

@input_guardrail(name="max_length", run_in_parallel=True)  # parallel: runs alongside the first model call
async def max_length(ctx: RunContextWrapper[None], agent: Agent,
                     user_input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    too_long = len(as_text(user_input)) > 2000
    return GuardrailFunctionOutput(output_info={"chars": len(as_text(user_input))}, tripwire_triggered=too_long)

def make_agent(model: ScriptedModel) -> Agent:           # fresh agent per request in this demo
    return Agent(name="Tariff Agent", instructions="Answer customs duty questions.",
                 input_guardrails=[no_card_numbers, max_length], model=model)

class In(BaseModel):
    message: str

class Out(BaseModel):
    answer: str
    model_calls: int                                     # how many times the main model was invoked

app = FastAPI()

@app.post("/ask", response_model=Out)
async def ask(body: In) -> Out:
    model = ScriptedModel([[assistant_message("HS 6109 duty is 12%.")]] * 2)
    try:
        result = await Runner.run(make_agent(model), body.message, max_turns=3)
    except InputGuardrailTripwireTriggered as exc:       # client error, not a server error
        name = exc.guardrail_result.guardrail.get_name()  # which rule fired
        raise HTTPException(400, f"request blocked by guardrail: {name}")
    except AgentsException as exc:
        raise HTTPException(502, type(exc).__name__)
    return Out(answer=str(result.final_output), model_calls=len(model.calls))

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.post("/ask", json={"message": "Duty on HS 6109?"}).json())  # passes, 1 model call
    r = c.post("/ask", json={"message": "My card 4111 1111 1111 1111, duty on 6109?"})
    print(r.status_code, r.json())                       # 400 blocked by no_card_numbers
    r = c.post("/ask", json={"message": "x" * 3000})
    print(r.status_code, r.json())                       # 400 blocked by max_length
```

Third snippet: blocking vs parallel, measured.

```python
# Blocking vs parallel input guardrails: does the main model get called when the guardrail trips? (runs offline)
import asyncio                                           # run the async demo
from agents import (Agent, Runner, GuardrailFunctionOutput, InputGuardrailTripwireTriggered,
                    input_guardrail, set_tracing_disabled)  # SDK pieces
from agents.testing import ScriptedModel, assistant_message  # offline model

set_tracing_disabled(True)                               # no key in this demo

def make_guardrail(parallel: bool):                      # same rule, two modes
    @input_guardrail(run_in_parallel=parallel)           # the only difference between the two runs
    async def always_trip(ctx, agent, user_input) -> GuardrailFunctionOutput:
        await asyncio.sleep(0.05)                        # a slow check (like a real LLM classifier)
        return GuardrailFunctionOutput(output_info="blocked", tripwire_triggered=True)
    return always_trip

async def main() -> None:
    for parallel in (False, True):
        model = ScriptedModel([[assistant_message("answer")]] * 2)  # records how often it is called
        agent = Agent(name="A", model=model, input_guardrails=[make_guardrail(parallel)])
        try:
            await Runner.run(agent, "hello")
        except InputGuardrailTripwireTriggered:
            pass                                         # expected: the guardrail trips
        print(f"run_in_parallel={parallel}: main model calls = {len(model.calls)}")

asyncio.run(main())
```

Observed: `run_in_parallel=False: main model calls = 0` and `run_in_parallel=True: main model calls = 1`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Input checks | Guard node + conditional edge | Task guardrails (validate task output) | `input_guardrails` on first agent | Custom agent / termination logic |
| Built-in tripwire exception | No (you route to END) | No | `InputGuardrailTripwireTriggered` | No |
| Runs in parallel with the model | You build it | No | Yes, `run_in_parallel=True` (default) | You build it |
| Blocking mode | Edge before agent node | n/a | `run_in_parallel=False` | You build it |
| Result inspection | State | Task output | `result.input_guardrail_results` | Messages |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Expecting input guardrails to run on every agent in a handoff chain.
✅ Correct: They run only for the first agent; put checks there (triage) or on tools/outputs for later agents.

❌ Mistake 2: Using parallel mode and assuming "blocked" means "no tokens spent".
✅ Correct: Parallel mode starts the model call at the same time (verified 1 call). Use `run_in_parallel=False` for expensive or sensitive agents.

❌ Mistake 3: Catching generic `Exception` and returning 500 for a tripwire.
✅ Correct: Catch `InputGuardrailTripwireTriggered` and return a clear 4xx (we used 400).

❌ Mistake 4: Using a big model as the checker.
✅ Correct: Rules first, then a small cheap model; reserve big models for the main agent.

❌ Mistake 5: Treating guardrails as complete security.
✅ Correct: They are a layer. Also validate tool arguments, authorise in code, and sandbox risky tools.

---

## 🧠 Tricky Interview Question
Your guardrail uses an LLM classifier in parallel mode. Latency is great, but a security review says "blocked requests still reach the main model and may call tools". Do they?

**Answer:** Possibly. In parallel mode the first model call starts at the same time as the guardrail (we measured one main-model call even though the guardrail tripped). We did not test whether a tool call in that first response would execute before the tripwire is handled, so do not design around timing luck. For anything with side effects, use `run_in_parallel=False` so nothing starts until the guardrail passes, or keep side-effecting tools behind their own checks (approval, authorisation in code, tool input guardrails). Choose parallel only for read-only agents where cost of a wasted call is acceptable.

---

## ⚫ Interview Questions + Answers

**Q1:** What does an input guardrail return and what happens on a trip?

**A1:** `GuardrailFunctionOutput(output_info, tripwire_triggered)`. If `tripwire_triggered` is True the run raises `InputGuardrailTripwireTriggered`.

**Q2:** Which agents' input guardrails run?

**A2:** Only the first agent in the run. After handoffs the new agent's input guardrails do not run.

**Q3:** Parallel versus blocking?

**A3:** Parallel (default) runs with the first model call for lower latency but may waste that call; blocking waits for the guardrail first and prevents the model call when it trips (we measured 1 versus 0 calls).

**Q4:** How would you implement an LLM-based guardrail?

**A4:** A small checker `Agent` with `output_type` (pydantic verdict) run via `Runner.run` inside the guardrail; map the verdict to `tripwire_triggered`; keep `output_info` for logs.

**Q5:** Design guardrails for a public tariff chatbot.

**A5:** Rule layer (length, PII regex, blocklist) in blocking mode; small-model topic/injection classifier in parallel mode for read-only agents; output guardrail for leaks; HTTP 400 with generic message; log guardrail name and `output_info` (not raw PII); metrics on trip rate by rule; eval set of attacks to catch regressions; rate limits per user.

---

## 💰 Cost Impact
Rule-based guardrails: zero tokens. LLM guardrails: one extra small-model call per request (instructions plus the user input plus a short verdict). In parallel mode a tripped request still pays for the main model's first call; in blocking mode it does not but adds the checker latency before the main call. Approximate, from public pricing at time of writing, verify; measure with `usage` of the checker runs.

**Tips:** rules before LLM, small model for classification, `run_in_parallel=False` for expensive agents, cache repeated verdicts, cap input length first.

---

## 🔷 When to Use
✅ Use when:
- The first agent is expensive or has side-effect tools
- You must block PII, off-topic or abusive input
- You want a typed, loggable reason for rejection

❌ Avoid when:
- You need to check every agent in a handoff chain (use tool guardrails / output guardrails there)
- A simple Pydantic request validation in FastAPI already covers it (do that first)

---

## 📊 Visual Diagram
```
 user input
    |
    +--> input guardrails (first agent only)
    |        rules (regex/length)  : 0 tokens
    |        checker agent (small) : few tokens
    |
    |  run_in_parallel=False:  guardrail ---> pass? ---> model call
    |                                          |no -> InputGuardrailTripwireTriggered (0 model calls)
    |  run_in_parallel=True :  guardrail  ||  model call (already started)
    |                                          |no -> InputGuardrailTripwireTriggered (1 wasted call)
    v
 agent loop continues --> result.input_guardrail_results
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| guardrail | Check that can stop a run | run रोकने वाली जाँच |
| tripwire | Flag that triggers the stop | रोकने वाला संकेत |
| GuardrailFunctionOutput | Result object: output_info + tripwire_triggered | guardrail का नतीजा |
| run_in_parallel | Run guardrail alongside the model call | model call के साथ-साथ चलाना |
| checker agent | Small agent used only to classify | सिर्फ classify करने वाला छोटा agent |
| output_info | Details kept for logging | logging के लिए ब्योरा |

---

## ⚡ 3-Line Summary
English: Input guardrails inspect the first agent's input and can raise a tripwire that stops the run.
Use rules first, a small checker agent second; blocking mode saves the model call, parallel mode saves latency.
Catch `InputGuardrailTripwireTriggered` and return a clean 4xx.

Hindi: Input guardrails पहले agent के input को जाँचते हैं और tripwire उठाकर run रोक सकते हैं।
पहले rules, फिर छोटा checker agent; blocking mode model call बचाता है, parallel mode latency।
`InputGuardrailTripwireTriggered` पकड़कर साफ 4xx लौटाएँ।

---

## ➡️ Next Topic
**#42 Output Guardrails** - the mirror image: checking what the final agent is about to return (leaks, wrong format, unsafe text) before it reaches the user.

---
