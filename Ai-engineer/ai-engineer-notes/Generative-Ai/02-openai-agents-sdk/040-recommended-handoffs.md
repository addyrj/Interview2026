---

# 40. Recommended Handoffs
# हिंदी में: सुझाए गए Handoff तरीके
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0). The prefix text and helper were read from the installed `agents/extensions/handoff_prompt.py`. Code ran offline with `agents.testing.ScriptedModel`. Whether a real model routes better with the prefix is not measured here (needs `OPENAI_API_KEY` and an eval set); treat the advice below as engineering practice, not benchmark results.

---

## 🔵 Simple Definition (2-3 lines)
"Recommended handoffs" means the practices the SDK itself suggests for reliable multi-agent routing: add the recommended prompt prefix (`RECOMMENDED_PROMPT_PREFIX` / `prompt_with_handoff_instructions`) to every agent that uses handoffs, give each target a clear `handoff_description`, and keep the topology simple (one triage hub, few specialists).

## 🔵 सरल परिभाषा (Hindi)
"Recommended handoffs" का मतलब वे तरीके हैं जो SDK खुद भरोसेमंद multi-agent routing के लिए सुझाता है: handoffs इस्तेमाल करने वाले हर agent में recommended prompt prefix (`RECOMMENDED_PROMPT_PREFIX` / `prompt_with_handoff_instructions`) जोड़ें, हर target को साफ `handoff_description` दें, और topology सरल रखें (एक triage hub, कम specialists)।

---

## 🔴 Problem it Solves
Models do not know what a "handoff" is unless told. Without guidance they announce "I am transferring you to billing" (breaking the user experience), call the wrong transfer tool, or try to answer everything themselves. Loose naming and mesh topologies make routing flaky and hard to debug.

## 🔴 यह क्यों बना? (Hindi)
Model को बताए बिना पता नहीं होता कि "handoff" क्या है। मार्गदर्शन न हो तो वह "मैं आपको billing में transfer कर रहा हूँ" जैसा बोल देता है (user experience बिगड़ता है), गलत transfer tool चुनता है, या सब कुछ खुद जवाब देने की कोशिश करता है। ढीले नाम और mesh topology routing को अस्थिर और debug करने में कठिन बना देते हैं।

---

## 🟢 How it Works

```
Recommended practice (what the SDK ships + common engineering guidance):

1. Prefix       -> instructions = prompt_with_handoff_instructions("your routing rules")
                   (adds the "# System context" block that explains Agents, Handoffs and
                    transfer_to_<agent_name>, and tells the model not to mention transfers)
2. Descriptions -> handoff_description on every target: one line, "Use for X, not for Y"
3. Names        -> short, distinct agent names (they become transfer_to_<name>)
4. Topology     -> hub-and-spoke: triage -> specialists; specialists may hand back to triage
5. Guards       -> max_turns, input guardrail on triage, output guardrail on specialists
6. Tests        -> scripted model asserts which handoff tools were offered + evals for routing accuracy
```

## 🟢 कैसे काम करता है? (Hindi)

```
सुझाए गए तरीके (SDK जो देता है + आम engineering सलाह):

1. Prefix       -> instructions = prompt_with_handoff_instructions("आपके routing नियम")
                   ("# System context" block जोड़ता है जो Agents, Handoffs और
                    transfer_to_<agent_name> समझाता है और transfers का ज़िक्र न करने को कहता है)
2. Descriptions -> हर target पर handoff_description: एक पंक्ति, "X के लिए, Y के लिए नहीं"
3. Names        -> छोटे, अलग नाम (ये transfer_to_<name> बनते हैं)
4. Topology     -> hub-and-spoke: triage -> specialists; specialists triage को वापस सौंप सकते हैं
5. Guards       -> max_turns, triage पर input guardrail, specialists पर output guardrail
6. Tests        -> scripted model से जाँचें कौन-से handoff tools दिखे + routing accuracy की evals
```

**Verified facts (0.24.0):**
- `agents.extensions.handoff_prompt` exports `RECOMMENDED_PROMPT_PREFIX` and `prompt_with_handoff_instructions(prompt: str) -> str`.
- The helper returns exactly `RECOMMENDED_PROMPT_PREFIX + "\n\n" + prompt` (we compared the helper with a manual f-string: equal).
- The prefix starts with `# System context`, mentions `transfer_to_<agent_name>`, and instructs the model not to mention or draw attention to transfers.
- The model's system prompt (recorded by `ScriptedModel.first_call.system_instructions`) started with the prefix and ended with our routing text.
- The hub-and-spoke factory (`build_team`) with specialists as data rows worked: both routes ran and `team.instructions` started with the prefix, which a unit test can assert without any LLM.

**Connect to what you know:** it is like a LangGraph supervisor prompt that lists the available workers and the rule "reply with the worker name only", except here the SDK writes the tool plumbing and you only supply the preface and descriptions.

---

## 🟡 Real World Example
**Tariff Agent platform.** A `Specialist` table lists Tariff Agent, Billing Agent, Tech Agent with one-line descriptions. A factory builds the team, applies the prefix to all prompts, and exposes `/chat`. CI asserts that every agent's instructions start with the prefix and that the triage agent offers exactly the expected transfer tools. A weekly eval of 200 labelled questions measures routing accuracy.

## 🟡 Real Example Hindi mein
**Tariff Agent platform.** `Specialist` table में Tariff Agent, Billing Agent, Tech Agent की एक-एक पंक्ति के description होते हैं। एक factory team बनाती है, सब prompts पर prefix लगाती है और `/chat` देती है। CI जाँचता है कि हर agent के instructions prefix से शुरू होते हैं और triage ठीक वही transfer tools देता है जो अपेक्षित हैं। हर हफ्ते 200 labelled सवालों की eval से routing accuracy नापी जाती है।

---

## 💻 Code Example — Basic
The helper, what it produces, and proof that the model receives the prefix. Runs offline.

```python
# Basic: the recommended handoff prompt prefix and how it reaches the model (runs offline)
from agents import Agent, Runner, set_tracing_disabled  # SDK pieces
from agents.extensions.handoff_prompt import (RECOMMENDED_PROMPT_PREFIX,
                                              prompt_with_handoff_instructions)  # official helpers
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

print(RECOMMENDED_PROMPT_PREFIX.splitlines()[0])         # "# System context"
print("mentions transfer_to_<agent_name>:", "transfer_to_<agent_name>" in RECOMMENDED_PROMPT_PREFIX)  # True

body = "Route the user to the right specialist."          # your own routing instructions
via_helper = prompt_with_handoff_instructions(body)      # helper = prefix + your text
via_manual = f"{RECOMMENDED_PROMPT_PREFIX}\n\n{body}"    # same thing written by hand
print("helper equals manual:", via_helper == via_manual)  # shows what the helper does

tariff = Agent(name="Tariff Agent", handoff_description="Customs duty and HS code questions",
               instructions="Answer duty questions.",
               model=ScriptedModel([[assistant_message("HS 6109 duty is 12%.")]]))

triage_model = ScriptedModel([[function_call("transfer_to_tariff_agent", {}, call_id="h1")]])
triage = Agent(name="Triage Agent",
               instructions=prompt_with_handoff_instructions(body),  # prefix teaches the model what handoffs are
               handoffs=[tariff], model=triage_model)

result = Runner.run_sync(triage, "Duty on HS 6109?")     # run the routing
sent = triage_model.first_call.system_instructions       # exactly what the model received as system prompt
print("system prompt starts with prefix:", sent.startswith(RECOMMENDED_PROMPT_PREFIX))  # True
print("system prompt ends with your text:", sent.endswith(body))  # True
print("answer:", result.final_output, "| handled by:", result.last_agent.name)
```

## 💻 Code Example — Advanced
A reusable hub-and-spoke factory: specialists are data rows, every prompt gets the prefix, specialists can hand back with a clear description, FastAPI endpoint with error mapping. Runs offline via `TestClient`; `pick` only scripts the fake router.

```python
# Advanced: recommended handoff pattern as a reusable, testable FastAPI factory (runs offline)
from dataclasses import dataclass                        # specialist spec
from fastapi import FastAPI, HTTPException               # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schemas
from agents import (Agent, Model, Runner, handoff, MaxTurnsExceeded, AgentsException,
                    set_tracing_disabled)                # SDK pieces
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions  # official prefix helper
from agents.testing import ScriptedModel, assistant_message, function_call  # offline model

set_tracing_disabled(True)                               # no key in this demo

@dataclass(frozen=True)
class Specialist:                                        # one row per specialist: data, not copy-pasted code
    name: str
    description: str                                     # one line the router reads (what it handles)
    instructions: str
    model: Model                                         # a model name string in production

def build_team(specialists: list[Specialist], router_model: Model) -> Agent:
    """Hub-and-spoke team: triage + specialists, all prompts carry the handoff prefix."""
    agents = [Agent(name=s.name, handoff_description=s.description,
                    instructions=prompt_with_handoff_instructions(s.instructions),  # recommended prefix
                    model=s.model) for s in specialists]
    triage = Agent(name="Triage Agent",
                   instructions=prompt_with_handoff_instructions(
                       "Pick exactly one specialist. If unsure, ask ONE clarifying question instead."),
                   handoffs=[handoff(a) for a in agents],  # one generated transfer tool per specialist
                   model=router_model)
    for a in agents:                                     # let specialists hand back when off-topic
        a.handoffs = [handoff(triage, tool_name_override="back_to_triage",
                              tool_description_override="Use only if the request is outside your domain.")]
    return triage

class In(BaseModel):
    message: str
    pick: str                                            # demo only: scripted router choice

class Out(BaseModel):
    answer: str
    handled_by: str

app = FastAPI()

@app.post("/chat", response_model=Out)
async def chat(body: In) -> Out:
    team = build_team(
        [Specialist("Tariff Agent", "Customs duty and HS codes", "Answer duty questions.",
                    ScriptedModel([[assistant_message("HS 6109 duty is 12%.")]])),
         Specialist("Billing Agent", "Invoices and refunds", "Answer billing questions.",
                    ScriptedModel([[assistant_message("Refund is on its way.")]]))],
        ScriptedModel([[function_call(f"transfer_to_{body.pick}", {}, call_id="h1")]]))
    try:
        result = await Runner.run(team, body.message, max_turns=5)
    except MaxTurnsExceeded:
        raise HTTPException(504, "too many hops")
    except AgentsException as exc:
        raise HTTPException(502, type(exc).__name__)
    return Out(answer=str(result.final_output), handled_by=result.last_agent.name)

if __name__ == "__main__":
    c = TestClient(app)                                  # no uvicorn needed
    print(c.post("/chat", json={"message": "HS 6109?", "pick": "tariff_agent"}).json())
    print(c.post("/chat", json={"message": "refund?", "pick": "billing_agent"}).json())
    # the recommended prefix is on every agent, which a unit test can assert without any LLM
    team = build_team([Specialist("A", "d", "i", ScriptedModel([]))], ScriptedModel([]))
    print("triage has prefix:", team.instructions.startswith("# System context"))  # True
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Routing prompt help | You write the supervisor prompt | Manager prompt built in | `RECOMMENDED_PROMPT_PREFIX` helper | Swarm/selector prompts built in |
| Recommended topology | Supervisor + workers | Hierarchical process | Triage hub + specialists | Selector group chat or Swarm |
| Descriptions for routing | Worker descriptions in your prompt | Agent role/goal | `handoff_description` | Agent `description` |
| Loop guard | `recursion_limit` | `max_iter` | `max_turns` | Termination conditions |
| Routing tests | Unit-test router node | Hard | Scripted model + evals | Replay client + evals |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Forgetting the prefix on specialists that can hand back.
✅ Correct: Apply `prompt_with_handoff_instructions` to every agent that has `handoffs`.

❌ Mistake 2: Prefix on top of your own long routing essay that repeats it.
✅ Correct: Keep your routing text short; the prefix already explains the mechanism.

❌ Mistake 3: Overlapping `handoff_description`s ("answers questions", "helps users").
✅ Correct: Mutually exclusive descriptions with explicit "not for" cases.

❌ Mistake 4: Mesh topology (every agent can hand off to every other).
✅ Correct: Hub-and-spoke; limited hand-back; `max_turns`.

❌ Mistake 5: Believing the prefix guarantees correct routing.
✅ Correct: It helps the model understand the mechanism; accuracy still needs evals and good descriptions.

---

## 🧠 Tricky Interview Question
After adding the recommended prefix, users still sometimes see "I'm transferring you to the billing team" in replies. What do you check?

**Answer:** First confirm the prefix really reaches that agent: inspect the system prompt the model received (in tests via the scripted model, in production via traces); a common bug is building the instructions with the prefix for triage but not for the specialist that gets the conversation after the transfer, or overriding `instructions` later with `clone(instructions=...)`. Then check the model: smaller models follow the "do not mention transfers" line less reliably; add an output guardrail or a regex check for phrases like "transferring", or add your own explicit line. Finally add the case to the eval set so a regression is visible.

---

## ⚫ Interview Questions + Answers

**Q1:** What is `RECOMMENDED_PROMPT_PREFIX`?

**A1:** A prompt block from `agents.extensions.handoff_prompt` that explains Agents, Handoffs and `transfer_to_<agent_name>`, and tells the model not to mention transfers to the user.

**Q2:** How do you apply it?

**A2:** `Agent(instructions=prompt_with_handoff_instructions("your text"), handoffs=[...])`, which returns prefix + blank line + your text.

**Q3:** What makes a good `handoff_description`?

**A3:** One line, specific, non-overlapping with other targets, ideally with a "not for" clause, because the routing model reads it as the tool description.

**Q4:** Why prefer hub-and-spoke?

**A4:** Fewer routing choices per agent, easier tests, easier tracing, and a clear fallback. A mesh multiplies the number of transfer tools and the chance of ping-pong.

**Q5:** How would you measure whether your handoff design is good?

**A5:** A labelled eval set of user messages with the expected specialist; run it with real models; report routing accuracy, wrong-route cost, mean hops and tokens per run; track the same in production through traces (handoff spans) and alert on rising `MaxTurnsExceeded`.

---

## 💰 Cost Impact
The prefix is a fixed block (about a hundred tokens, approximate, count with your tokenizer) added to every model call of every agent that uses it. That is a small per-call cost for more reliable routing, and it is cacheable in providers that support prompt caching because it is a stable prefix. Each additional handoff adds a tool schema. Approximate, from public pricing at time of writing, verify.

**Tips:** put the stable prefix first (good for caching), keep descriptions short, use a cheap model for triage, hide irrelevant handoffs with `is_enabled`.

---

## 🔷 When to Use
✅ Use when:
- Any agent in your app has `handoffs`
- You want consistent behaviour across specialists written by different people
- You want testable routing setup (factory + assertions)

❌ Avoid when:
- You have a single agent with no handoffs (the prefix is wasted tokens)
- You use agent-as-tool only (no transfers happen)

---

## 📊 Visual Diagram
```
 instructions = RECOMMENDED_PROMPT_PREFIX + "\n\n" + your routing rules
        |
 Triage Agent --(tools: transfer_to_tariff_agent, transfer_to_billing_agent; each with handoff_description)
        |
   +----+--------------------+
   v                         v
 Tariff Agent            Billing Agent        (each: prefix + short domain prompt)
   |   back_to_triage if off-topic |
   +--------------+----------------+
                  v
        max_turns + guardrails + evals
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RECOMMENDED_PROMPT_PREFIX | Official prompt block explaining handoffs | handoffs समझाने वाला आधिकारिक prompt |
| prompt_with_handoff_instructions | Helper that prepends the prefix | prefix जोड़ने वाला helper |
| handoff_description | One-line routing hint | routing के लिए एक पंक्ति का संकेत |
| hub-and-spoke | Triage plus specialists topology | triage + specialists ढाँचा |
| routing accuracy | Share of questions sent to the right agent | सही agent तक पहुँचे सवालों का प्रतिशत |
| eval set | Labelled examples used to measure quality | गुणवत्ता नापने वाले labelled उदाहरण |

---

## ⚡ 3-Line Summary
English: Add `prompt_with_handoff_instructions(...)` to every agent that uses handoffs.
Write specific, non-overlapping `handoff_description`s and keep a hub-and-spoke design.
Test the setup with scripted models and measure routing accuracy with evals.

Hindi: handoffs वाले हर agent में `prompt_with_handoff_instructions(...)` जोड़ें।
specific, आपस में न टकराने वाले `handoff_description` लिखें और hub-and-spoke रखें।
Scripted models से setup test करें और evals से routing accuracy नापें।

---

## ➡️ Next Topic
**#41 Input Guardrails** - handoffs route the conversation; guardrails decide whether a request should be processed at all, running before or alongside the first agent.

---
