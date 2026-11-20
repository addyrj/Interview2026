---

# 60. Cloning Agents
# हिंदी में: Agents की Cloning (clone())
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts shown come from the fake model (10 in / 5 out per call), not from a real LLM.

---

## 🔵 Simple Definition (2-3 lines)
`agent.clone(**overrides)` makes a new Agent that copies every field of an existing agent and replaces only the fields you pass (name, instructions, model, tools...). It is the SDK's way to build variants (per country, per tenant, per environment) from one template.

## 🔵 सरल परिभाषा (Hindi)
`agent.clone(**overrides)` मौजूदा agent के सारे fields की copy वाला नया Agent बनाता है और सिर्फ़ वही fields बदलता है जो आप देते हैं (name, instructions, model, tools...)। एक template से variants (देश, tenant, environment के हिसाब से) बनाने का यह SDK का तरीका है।

---

## 🔴 Problem it Solves
Teams copy-paste an Agent definition for India, US and EU and the copies drift: a fix to one prompt never reaches the others. Building agents with giant factory functions with 15 parameters is also hard to read and test.

## 🔴 यह क्यों बना? (Hindi)
Teams India, US और EU के लिए Agent definition copy-paste करती हैं और copies अलग-अलग हो जाती हैं: एक prompt की fix बाकियों तक नहीं पहुँचती। 15 parameters वाले बड़े factory functions भी पढ़ने और test करने में कठिन हैं।

---

## 🟢 How it Works

```
Step 1 -> base = Agent(name="TariffAgent", instructions=..., tools=[...],
                       model_settings=ModelSettings(temperature=0.0))
Step 2 -> india = base.clone(name="TariffAgent-IN",
                            instructions="... for India.")
Step 3 -> clone copies all other fields (tools, settings, hooks...)
Step 4 -> CAUTION: copy is SHALLOW
          india.tools is base.tools  -> True (same list object!)
Step 5 -> need own list?  clone(tools=[*base.tools])
Step 6 -> cache clones (lru_cache) - build once per country
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> base = Agent(name="TariffAgent", instructions=..., tools=[...],
                       model_settings=ModelSettings(temperature=0.0))
Step 2 -> india = base.clone(name="TariffAgent-IN",
                            instructions="... India के लिए")
Step 3 -> clone बाकी सब fields (tools, settings, hooks...) copy करता है
Step 4 -> सावधानी: copy SHALLOW है
          india.tools is base.tools  -> True (वही list object!)
Step 5 -> अपनी list चाहिए?  clone(tools=[*base.tools])
Step 6 -> clones को cache करो (lru_cache) - देश के हिसाब से एक बार बनाओ
```

**Verified output (b60):** `india.name` is `TariffAgent-IN` while `base.name` stays `TariffAgent`; `model_settings.temperature` is `0.0` on the clone (copied); `india.tools is base.tools` printed `True` - so appending to one list changes both unless you pass a fresh list; after `base.clone(tools=[*base.tools])` the lengths were `1` and `2` after appending to the clone only.

**Hindi नोट:** `clone` dataclass की `replace` जैसा है: जो पास करो वही बदलता है। Shallow copy का मतलब: list/dict fields दोनों agents में साझा रहते हैं। इसलिए mutate करना हो (tools जोड़ना) तो पहले नई list दो। Interview में यह "gotcha" अक्सर पूछा जाता है।

---

## 🟡 Real World Example
**Tariff Agent.** One `TEMPLATE` agent (tools, temperature 0, 300 max tokens) is cloned into `Tariff-IN` and `Tariff-US`. Each clone's instructions say 'only answer for <country>'. The FastAPI route `/{country}/ask` picks the clone, caches it, and returns 404 for an unknown country.

**Customer Support Agent:** `base_support` cloned per brand with a different tone and model.

## 🟡 Real Example Hindi mein
**Tariff Agent.** एक `TEMPLATE` agent (tools, temperature 0, 300 max tokens) से `Tariff-IN` और `Tariff-US` clones बनते हैं। हर clone की instructions कहती हैं 'सिर्फ़ <देश> के लिए जवाब दो'। FastAPI route `/{country}/ask` सही clone चुनता है, उसे cache करता है और अज्ञात देश पर 404 देता है।

**Customer Support Agent:** `base_support` को हर brand के लिए अलग tone और model के साथ clone करो।

---

## 💻 Code Example — Basic
Runs offline. Shows what is copied, what is overridden, and the shallow-copy gotcha.

```python
# Basic: Agent.clone() - copy an agent and override a few fields (offline).
# verified against openai-agents 0.24.0
import asyncio
from agents import Agent, Runner, ModelSettings, function_tool, set_tracing_disabled
from fake import ScriptedModel, text

set_tracing_disabled(True)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

base = Agent(name="TariffAgent", instructions="Answer tariff questions.",
             tools=[get_tariff_rate], model_settings=ModelSettings(temperature=0.0),
             model=ScriptedModel([[text("base answer")]]))

india = base.clone(name="TariffAgent-IN", instructions="Answer tariff questions for India.",
                   model=ScriptedModel([[text("India answer")]]))   # override name, instructions, model only
print(india.name, "|", base.name)                                 # TariffAgent-IN | TariffAgent
print(india.model_settings.temperature)                           # 0.0 (copied from base)
print(india.tools is base.tools)                                  # True -> clone is SHALLOW: same list object!

safe = base.clone(tools=[*base.tools])                            # give the clone its own list when you plan to mutate
safe.tools.append(get_tariff_rate)                                # does not touch base.tools
print(len(base.tools), len(safe.tools))                           # 1 2

print(asyncio.run(Runner.run(india, "rate?")).final_output)       # India answer
```

Expected output: `TariffAgent-IN | TariffAgent`, `0.0`, `True`, `1 2`, `India answer`.

## 💻 Code Example — Advanced
FastAPI service creating one clone per country from a template, cached with `lru_cache`, with an unknown-country 404. Output: `{'agent': 'Tariff-IN', 'answer': 'IN agent reply'}`, `404`, and `True Tariff-IN Tariff-template`.

```python
# Advanced: per-tenant agents from one template via clone(), cached, behind FastAPI.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
from functools import lru_cache                                   # cache one agent per country
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, ModelSettings, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, text

set_tracing_disabled(True)

RATES: dict[str, dict[str, str]] = {"IN": {"6109.10": "10%"}, "US": {"6109.10": "16.5%"}}   # demo data, not real law

@function_tool
def tariff_table_lookup(country: str, hs_code: str) -> str:
    """Return the demo duty for (country, HS code)."""
    return RATES.get(country, {}).get(hs_code, "unknown")

TEMPLATE = Agent(                                                 # one template, no model call at import time
    name="Tariff-template", instructions="You are a customs assistant.",
    tools=[tariff_table_lookup], model_settings=ModelSettings(temperature=0.0, max_tokens=300),
)

@lru_cache(maxsize=64)                                            # clone once per country, reuse afterwards
def agent_for(country: str) -> Agent:
    if country not in RATES:
        raise KeyError(country)
    return TEMPLATE.clone(                                        # fresh Agent object, shared tool objects
        name=f"Tariff-{country}",
        instructions=f"{TEMPLATE.instructions} Only answer for {country}. Use tariff_table_lookup.",
        tools=[*TEMPLATE.tools],                                  # own list: later edits stay local
        model=ScriptedModel([[text(f"{country} agent reply")]]),  # offline; production: model="<model name>"
    )

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/{country}/ask")
async def ask(country: str, q: Q) -> dict[str, str]:
    try:
        agent = agent_for(country.upper())
    except KeyError:
        raise HTTPException(404, f"no tariff data for {country}")
    res = await Runner.run(agent, q.question, max_turns=5)
    return {"agent": agent.name, "answer": str(res.final_output)}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    c = TestClient(app)
    print(c.post("/in/ask", json={"question": "rate?"}).json())
    print(c.post("/xx/ask", json={"question": "rate?"}).status_code)
    print(agent_for("IN") is agent_for("IN"), agent_for("IN").name, TEMPLATE.name)
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Create variant of an agent | Compile another graph with different config | Create another `Agent` object (no clone helper) | `agent.clone(**overrides)` | Construct a new agent / `component_config` dump + load |
| Share base prompt | Python constants / config | YAML (`agents.yaml`) templates | `instructions` string or dynamic function | Config object |
| Mutation safety | State is immutable-ish per run | Objects are mutable | Shallow copy - own your lists | Config round-trip copies data |
| Per-tenant overrides | `config['configurable']` | Pass variables to tasks | clone + dynamic instructions with context | Per-team factory |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: Appending to `clone.tools` and being surprised that the base agent changed.
✅ Correct: `clone(tools=[*base.tools])` first, then append.

❌ Mistake: Cloning on every request in a hot path with no cache.
✅ Correct: Cheap, but build once per variant (lru_cache) and reuse.

❌ Mistake: Cloning when only the user's data changes.
✅ Correct: Use the run `context` or dynamic instructions; clone is for static variants.

❌ Mistake: Expecting `clone` to deep-copy a model client.
✅ Correct: The model/client object is shared; give each clone its own model only if you need isolation.

---

## 🧠 Tricky Interview Question
You clone an agent per tenant (500 tenants) and memory grows. What are the options?

**Answer:** 500 Agent objects are small; the real cost is whatever they hold (tool objects, model clients, big prompts). Because clone is shallow they share tool objects, which is good. Do not cache unbounded keys: use `lru_cache(maxsize=...)` or build lazily. If tenants differ only by a few strings, keep ONE agent and use dynamic `instructions` as a function of the run context (tenant name, rules), which avoids N objects altogether. Use clones when the variant needs different tools or models.

---

## ⚫ Interview Questions + Answers

**Q1:** What does `Agent.clone()` do?

**A1:** Returns a new Agent with the same fields except those you override.

**Q2:** Is clone deep or shallow?

**A2:** Shallow: `india.tools is base.tools` was True in our run.

**Q3:** Clone vs dynamic instructions?

**A3:** Clone makes static variants; dynamic instructions read the run context and vary per request without new objects.

**Q4:** How do you give a variant a different model?

**A4:** `base.clone(model="<model name>")` (we passed a scripted model offline).

**Q5:** Design: white-label support bot for 50 brands.

**A5:** One base agent, clone per brand for tone/tools/model, LRU cache, brand config in DB, per-brand guardrails and tracing metadata, and tests that every clone keeps the base safety instructions.

---

## 💰 Cost Impact
Cloning itself costs no tokens (no model call). Token cost comes from each variant's prompt: long per-variant instructions are re-sent on every turn, so keep the shared part short. A cheaper `model=` on low-risk variants is the main saving. Approximate pricing - verify.

---

## 🔷 When to Use
✅ Use when:
- Same behaviour with small static differences (country, brand, model)
- You want one place to fix the shared prompt/tools
- A/B test two prompts

❌ Avoid when:
- Only user data differs (use context)
- The variants have almost nothing in common
- You plan to mutate shared lists without copying them

---

## 📊 Visual Diagram
```
            TEMPLATE Agent
   (tools, ModelSettings, base instructions)
        |                         |
   clone(name, instructions)   clone(name, instructions)
        v                         v
   Tariff-IN                  Tariff-US
        \                       /
         lru_cache (per country)
                |
     /{country}/ask -> Runner.run(clone)
   shared by reference: tools list unless you pass tools=[*...]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| clone | Copy an agent with overrides | overrides के साथ agent की copy |
| Template agent | Base agent for variants | variants का base agent |
| Shallow copy | Nested objects are shared | अंदर की objects साझा रहती हैं |
| lru_cache | Keep recent results | हाल के results याद रखना |
| Variant | Specialised copy | विशेष copy |
| Dynamic instructions | Prompt built from context | context से बना prompt |

---

## ⚡ 3-Line Summary
English: `clone()` copies an agent and overrides only the fields you pass.
The copy is shallow, so give the clone its own tools list before mutating it.
Cache clones per variant, or use dynamic instructions when only data changes.

Hindi: `clone()` agent की copy बनाता है और सिर्फ़ दिए गए fields बदलता है।
Copy shallow है, इसलिए mutate करने से पहले clone को अपनी tools list दें।
Variants को cache करें, या सिर्फ़ data बदलता हो तो dynamic instructions लें।

---

## ➡️ Next Topic
**#61 Forcing Tool Use** - clones may still skip tools; next we learn how to make the model (or the SDK) always call a tool.

---
