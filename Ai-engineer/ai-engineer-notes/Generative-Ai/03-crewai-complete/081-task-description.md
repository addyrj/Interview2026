---

# 81. Task description
# हिंदी में: Task का description
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`description` is the instruction text the agent receives for a task. It can contain `{placeholders}` filled by `kickoff(inputs=...)`. Good descriptions state the input, constraints, edge cases and scope.

## 🔵 सरल परिभाषा (Hindi)
`description` वह instruction text है जो agent को task के लिए मिलता है। इसमें `{placeholders}` हो सकते हैं जो `kickoff(inputs=...)` से भरते हैं। अच्छे description में input, constraints, edge cases और scope साफ़ लिखे होते हैं।

---

## 🔴 Problem it Solves
Vague descriptions produce vague, inconsistent output and extra iterations. The description is the main lever you have over behaviour per task.

## 🔴 यह क्यों बना? (Hindi)
अस्पष्ट description से अस्पष्ट, असंगत output और ज़्यादा iterations मिलते हैं। हर task पर behaviour पर आपका मुख्य नियंत्रण description ही है।

---

## 🟢 How it Works

```
Step 1 -> Write: goal + input slots + rules + edge cases
Step 2 -> kickoff(inputs) replaces {placeholders}
Step 3 -> Description is placed in the user part of the prompt with expected_output
Step 4 -> Agent follows it each iteration
Step 5 -> Test on 5-10 inputs
Step 6 -> Version the text like code
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> लिखें: लक्ष्य + input slots + नियम + edge cases
Step 2 -> kickoff(inputs) {placeholders} बदलता है
Step 3 -> Description expected_output के साथ prompt के user हिस्से में जाता है
Step 4 -> Agent हर iteration में इसे follow करता है
Step 5 -> 5-10 inputs पर test करें
Step 6 -> इसे code की तरह version करें
```

---

## 🟡 Real World Example
**Tariff Agent**: 'Find the import duty for HS code {hs} into {country}. Use only the get_duty_rate tool; if unknown say unknown; do not mention other codes.' In an offline test we confirmed the interpolated text (`DESCX 8517`) appears in the prompt sent to the model.

## 🟡 Real Example Hindi mein
**Tariff Agent**: 'HS code {hs} की {country} में import duty निकालो। सिर्फ़ get_duty_rate tool इस्तेमाल करो; पता न हो तो unknown कहो; दूसरे codes का ज़िक्र मत करो।' Offline test में पुष्टि हुई कि भरा हुआ text (`DESCX 8517`) model को भेजे prompt में होता है।

---

## 💻 Code Example — Basic
```python
# description_basic.py - good vs vague task description, with {placeholders}
from crewai import Agent, Task, Crew, LLM            # core

agent = Agent(role="Tariff Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))

vague = Task(description="Look at the tariff.", expected_output="Info.", agent=agent)   # BAD: no input, no steps

good = Task(                                         # GOOD
    description=(
        "Find the import duty for HS code {hs} into {country}.\n"   # input + target
        "Rules:\n"
        "1. Use only the get_duty_rate tool; do not guess.\n"       # constraint
        "2. If the tool returns 'unknown', answer 'unknown'.\n"     # edge case
        "3. Do not mention other codes.\n"                          # scope limit
    ),
    expected_output="One sentence: '<hs> into <country>: <rate>%'.",   # format example
    agent=agent,
)
print(len(good.description) > len(vague.description))   # longer is fine if every line has a job
```
Verified: ran offline (printed True comparing description lengths). Real answers: not run - needs an API key. Length is not quality: every line should change behaviour.

## 💻 Code Example — Advanced
```python
# description_api.py - build description from validated inputs, never from raw user text
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel, Field                # validation

app = FastAPI()                                      # app
TEMPLATE = ("Find the import duty for HS code {hs} into {country}. "
            "Use only verified data; answer 'unknown' if unsure.")   # fixed template, variable slots only

class Req(BaseModel):                                # body
    hs: str = Field(pattern=r"^\d{4,10}$")           # digits only
    country: str = Field(pattern=r"^[A-Za-z ]{2,30}$")   # letters only

@app.post("/duty")                                   # endpoint
async def duty(req: Req) -> dict[str, str]:          # typed
    agent = Agent(role="Tariff Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))
    task = Task(description=TEMPLATE, expected_output="One sentence.", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs=req.model_dump())
    except Exception as exc:                         # failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}
```
Verified with `TestClient`. The template is fixed server-side and only validated slots (digits-only HS, letters-only country) are filled, so user text cannot rewrite the instructions.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Instruction text | Node prompt you write | Task `description` with `{vars}` | Agent `instructions` + user input | Task message to agent |
| Templating | Prompt templates | Built-in `{placeholder}` interpolation | Dynamic instructions / f-strings | Python formatting |
| Per-step instructions | Per node | Per task | Per agent/run | Per message |
| Reuse | Shared prompt modules | Same Task object, new inputs | Same agent, new input | Same agent |
| Injection risk | Prompt/state mixing | Placeholder values go into prompt | User input in prompt | User input in prompt |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Description: 'Look at the tariff.'
✅ Correct: State the input, the tool to use, the rules and the edge cases.

❌ Mistake 2: Putting output format only in `description`.
✅ Correct: Put format in `expected_output`; keep description about what to do.

❌ Mistake 3: Embedding raw user text with braces.
✅ Correct: Validate inputs; unmatched `{}` in text can confuse templating - pass user text as an input value.

---

## 🧠 Tricky Interview Question
Two tasks have almost the same description but behave differently. Why?

Answer: Differences usually come from agent persona, tools, `context` and `expected_output` rather than description alone. The prompt is persona + description + expected_output + context + tool schemas. Compare the full prompts the model received (use a fake LLM that records `messages`, or tracing) and diff them; also check temperature and model. Then move shared rules into a single constant to avoid drift.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is `description`?
A1: The task's instruction text, supporting `{placeholders}` from kickoff inputs.

Q2: [Medium] What belongs in a good description?
A2: Goal, input values, allowed tools, constraints, edge-case handling and scope limits.

Q3: [Hard] How do you stop prompt injection via descriptions?
A3: Fixed templates, validated inputs, allow-lists, treat user text as data, and keep tools authorised server-side.

Q4: [Hard] How to test a description change?
A4: Run a fixed eval set with the same model and temperature before/after; compare accuracy, tokens and iterations.

Q5: [System Design] Manage 100 task templates across teams?
A5: Store in versioned config/repo, schema for placeholders, CI eval per change, ownership, and a registry with deprecation.

---

## 💰 Cost Impact
Formula: description tokens are resent on every iteration: description tokens x iterations. A precise description often lowers cost overall by cutting wasted iterations and retries, even if it is longer (approximate; measure on your eval set). Tips: remove filler, move static knowledge to tools.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Every task
- When behaviour must be consistent across inputs

❌ Avoid when:
- Copy-pasting giant policy documents (use retrieval/tools)
- Free-text user input in the template

---

## 📊 Visual Diagram
```
  TEMPLATE: "Duty for HS {hs} into {country}. Rules: ..."
        |   + inputs {"hs":"8517","country":"India"}  (validated)
        v
  "Duty for HS 8517 into India. Rules: ..."
        |
        v   (+ expected_output + context)
     Agent prompt  -->  LLM
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| description | Task instruction text | विवरण / निर्देश |
| Placeholder | Slot filled at kickoff | स्थान-धारक |
| Edge case | Unusual input to handle | किनारे का मामला |
| Template | Fixed text with slots | साँचा |
| Eval set | Fixed test inputs | मूल्यांकन सेट |
| Injection | Malicious instructions in input | इंजेक्शन |

---

## ⚡ 3-Line Summary
English: The description is your main per-task lever: state input, rules and edge cases, fill slots from validated inputs only, and test changes on a fixed eval set.
Hindi: Description हर task पर आपका मुख्य साधन है: input, नियम और edge cases लिखें, slots सिर्फ़ validated inputs से भरें, और बदलाव fixed eval set पर test करें।

---

## ➡️ Next Topic
**082. Task expected_output** - defining what a good answer looks like.

---
