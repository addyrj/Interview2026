---

# 74. Agent role + goal + backstory
# हिंदी में: Agent के role, goal और backstory
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`role` is the job title, `goal` is what the agent must achieve, `backstory` is context and behavioural rules. CrewAI combines them into the agent's system prompt. All three accept `{placeholders}` filled at `kickoff(inputs=...)`.

## 🔵 सरल परिभाषा (Hindi)
`role` job title है, `goal` वह लक्ष्य है जो agent को पाना है, `backstory` संदर्भ और व्यवहार के नियम हैं। CrewAI इन्हें मिलाकर agent का system prompt बनाता है। तीनों में `{placeholders}` हो सकते हैं जो `kickoff(inputs=...)` पर भरते हैं।

---

## 🔴 Problem it Solves
Without a persona the LLM answers in a generic, inconsistent style and may guess. These fields pin down expertise, tone and boundaries (for example 'say unknown if data is missing') at a small token cost.

## 🔴 यह क्यों बना? (Hindi)
Persona के बिना LLM सामान्य, असंगत शैली में जवाब देता है और अंदाज़ा लगा सकता है। ये fields थोड़े tokens में expertise, tone और सीमाएँ (जैसे 'data न हो तो unknown कहो') तय कर देते हैं।

---

## 🟢 How it Works

```
Step 1 -> You write role, goal, backstory (with {placeholders})
Step 2 -> kickoff(inputs) interpolates the placeholders
Step 3 -> CrewAI renders them into the system prompt template
Step 4 -> Every LLM iteration of this agent re-sends that prompt
Step 5 -> Behaviour follows persona + task description
Step 6 -> Change persona = change prompt = re-test
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> आप role, goal, backstory लिखते हैं ({placeholders} सहित)
Step 2 -> kickoff(inputs) placeholders भरता है
Step 3 -> CrewAI इन्हें system prompt template में रखता है
Step 4 -> इस agent की हर LLM iteration यही prompt दोबारा भेजती है
Step 5 -> व्यवहार persona + task description से तय होता है
Step 6 -> Persona बदला = prompt बदला = दोबारा test
```

---

## 🟡 Real World Example
**Tariff Agent**: role `{country} Customs Tariff Analyst`, goal 'exact duty, never guess', backstory 'say unknown when data is missing'. One agent definition serves India, USA and EU by changing `inputs`.

## 🟡 Real Example Hindi mein
**Tariff Agent**: role `{country} Customs Tariff Analyst`, goal 'सटीक duty, कभी अंदाज़ा नहीं', backstory 'data न हो तो unknown कहो'। `inputs` बदलकर एक ही agent India, USA और EU के लिए चलता है।

---

## 💻 Code Example — Basic
```python
# persona_basic.py - role/goal/backstory with {placeholders} filled from kickoff inputs
from crewai import Agent, Task, Crew, LLM            # core

llm = LLM(model="gpt-4o-mini")                       # real run needs a key
agent = Agent(
    role="{country} Customs Tariff Analyst",         # placeholder interpolated at kickoff
    goal="Give the exact duty for {country} imports, never guess",   # concrete + constrained
    backstory="You classify goods under the {country} tariff schedule. "
              "You say 'unknown' when the data is missing.",         # behaviour rules live here
    llm=llm,
)
task = Task(description="Duty for HS {hs} into {country}?", expected_output="One line.", agent=agent)
crew = Crew(agents=[agent], tasks=[task])            # one agent crew
print(crew.kickoff(inputs={"country": "India", "hs": "8517"}).raw)   # same agent code, many countries
```
Verified: ran offline with a scripted fake LLM; with a similar test we confirmed the role text appears in the prompt sent to the model. Real model behaviour: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# persona_api.py - safe persona templating from API input
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel, Field                # validation

app = FastAPI()                                      # app
ALLOWED = {"India", "USA", "EU"}                     # allow-list: never put raw user text in a role

class Req(BaseModel):                                # body
    country: str                                     # target market
    hs: str = Field(pattern=r"^\d{4,10}$")           # digits only, blocks prompt injection via this field

@app.post("/persona")                                # endpoint
async def persona(req: Req) -> dict[str, str]:       # typed
    if req.country not in ALLOWED:                   # validate before building the prompt
        raise HTTPException(422, "unsupported country")
    agent = Agent(role="{country} Tariff Analyst", goal="Exact duty only",
                  backstory="Says 'unknown' if unsure.", llm=LLM(model="gpt-4o-mini"))
    task = Task(description="Duty for HS {hs} into {country}?", expected_output="One line.", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs=req.model_dump())
    except Exception as exc:                         # LLM failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}                       # response
```
Verified with `TestClient`. Never interpolate free-form user text into role/goal/backstory: that is prompt injection into the system prompt. The route validates `country` against an allow-list and `hs` with a digits-only regex.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Persona fields | System prompt you write | `role`, `goal`, `backstory` | `instructions` | `system_message` |
| Templating | f-strings / prompt templates | `{placeholder}` + `kickoff(inputs)` | Dynamic instructions (callable) | Python string formatting |
| Structure enforced | None | Three named fields | One string | One string |
| Reuse across tasks | Reuse node | Same agent object in many tasks | Same agent object | Same agent object |
| Prompt visibility | You own it fully | Template customisable (`system_template`) | You own it fully | You own it fully |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Role as a long paragraph.
✅ Correct: Role = short title; put rules in backstory.

❌ Mistake 2: Contradictory goal and backstory ('be brief' vs 'explain in detail').
✅ Correct: Keep one consistent instruction set; test with 5 sample inputs.

❌ Mistake 3: Putting user input straight into backstory.
✅ Correct: Validate/allow-list inputs; pass user text only via task description, treated as data.

---

## 🧠 Tricky Interview Question
Does a better backstory always improve accuracy?

Answer: No. Persona text nudges style and boundaries but cannot add knowledge the model lacks, and it is resent on every iteration, so long backstories cost tokens and can dilute instructions. For factual accuracy use tools or retrieval; use the backstory for rules ('answer unknown if tool returns unknown'), then verify with a small eval set rather than intuition.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What do role, goal, backstory mean?
A1: Job title, objective, and background/behaviour rules that together form the agent's system prompt.

Q2: [Medium] How do placeholders work?
A2: Write `{country}` in the fields; `crew.kickoff(inputs={'country': 'India'})` replaces them before execution.

Q3: [Hard] Why is persona text a security concern?
A3: It sits in the system prompt; interpolating untrusted input there enables prompt injection with high privilege. Allow-list and validate inputs.

Q4: [Hard] How do you test persona changes?
A4: Fix a dataset of tasks, run before/after with the same model and temperature, compare accuracy, refusal behaviour and token use.

Q5: [System Design] One agent definition for 20 country teams?
A5: Template role/goal/backstory with `{country}`, load per-country rules from config, validate the country against a registry, build the agent per request, and version the template.

---

## 💰 Cost Impact
Formula: persona tokens x iterations = recurring input cost per run. Example estimate: 200 persona tokens x 8 iterations = 1,600 input tokens (approximate). Tips: keep backstory under a short paragraph, move rarely-needed rules into tools, rely on prompt caching if your provider supports it (verify).
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- You need consistent tone and boundaries
- One agent serving many contexts via templating

❌ Avoid when:
- Using persona as a substitute for retrieval or tools
- Interpolating unvalidated user text

---

## 📊 Visual Diagram
```
  inputs={'country':'India'}
          |
          v
  role     : "{country} Tariff Analyst"  --+
  goal     : "Exact duty only"            +--> SYSTEM PROMPT --> LLM (each iteration)
  backstory: "Say unknown if unsure"    --+
          |
  task.description  --------------------------> USER PROMPT
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Role | Job title of the agent | भूमिका |
| Goal | Objective the agent pursues | लक्ष्य |
| Backstory | Context and behaviour rules | पृष्ठभूमि |
| Placeholder | `{name}` slot filled at kickoff | स्थान-धारक |
| Prompt injection | Malicious text altering instructions | प्रॉम्प्ट इंजेक्शन |
| System prompt | Top-level instructions to the LLM | सिस्टम प्रॉम्प्ट |

---

## ⚡ 3-Line Summary
English: Role = title, goal = objective, backstory = rules. They are templated with {placeholders} and resent every iteration, so keep them short and never interpolate untrusted text.
Hindi: Role = title, goal = लक्ष्य, backstory = नियम। ये {placeholders} से template होते हैं और हर iteration में दोबारा जाते हैं, इसलिए छोटे रखें और untrusted text कभी न डालें।

---

## ➡️ Next Topic
**075. Agent tools** - giving the persona real capabilities.

---
