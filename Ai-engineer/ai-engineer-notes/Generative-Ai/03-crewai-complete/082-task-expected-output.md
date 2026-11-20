---

# 82. Task expected_output
# हिंदी में: Task का expected_output
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`expected_output` describes what the finished task should look like (format, length, fields). It is required, goes into the prompt, and works with `output_pydantic`/`output_json` and guardrails to turn that description into an enforced contract.

## 🔵 सरल परिभाषा (Hindi)
`expected_output` बताता है कि पूरा हुआ task कैसा दिखे (format, length, fields)। यह ज़रूरी है, prompt में जाता है और `output_pydantic`/`output_json` व guardrails के साथ इस description को लागू होने वाले contract में बदलता है।

---

## 🔴 Problem it Solves
Without a clear target the agent decides the format: sometimes prose, sometimes bullets, sometimes JSON. Downstream code and later tasks then break.

## 🔴 यह क्यों बना? (Hindi)
साफ़ target के बिना format agent तय करता है: कभी prose, कभी bullets, कभी JSON। फिर आगे का code और अगले tasks टूट जाते हैं।

---

## 🟢 How it Works

```
Step 1 -> Write expected_output in words (format + fields + limits)
Step 2 -> Optionally add output_pydantic / output_json for parsing
Step 3 -> CrewAI includes the description in the agent prompt
Step 4 -> Agent aims at it; output is parsed into the model
Step 5 -> Guardrail verifies business rules (range, completeness)
Step 6 -> Next task / API consumes typed result
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> expected_output शब्दों में लिखें (format + fields + limits)
Step 2 -> चाहें तो output_pydantic / output_json जोड़ें
Step 3 -> CrewAI यह description agent prompt में डालता है
Step 4 -> Agent इसे target बनाता है; output model में parse होता है
Step 5 -> Guardrail business rules जाँचता है (range, completeness)
Step 6 -> अगला task / API typed result इस्तेमाल करता है
```

---

## 🟡 Real World Example
**Tariff Agent**: `expected_output='JSON: hs_code, percent'` plus `output_pydantic=Duty` plus a guardrail for 0-100. We confirmed offline that `expected_output` text appears in the prompt (`EXPECTY`), and that the typed output returned as `hs_code='8517' percent=0.0` through FastAPI.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `expected_output='JSON: hs_code, percent'` के साथ `output_pydantic=Duty` और 0-100 वाला guardrail। Offline पुष्टि हुई कि `expected_output` text prompt में जाता है (`EXPECTY`) और typed output FastAPI से `hs_code='8517' percent=0.0` लौटा।

---

## 💻 Code Example — Basic
```python
# expected_output_basic.py - expected_output as a contract: text, JSON, Pydantic
from pydantic import BaseModel                       # schema
from crewai import Agent, Task, LLM                  # core

agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))

text_task = Task(description="Duty for HS {hs}?",
                 expected_output="One sentence ending with the percent sign.", agent=agent)   # prompt-only contract

class Duty(BaseModel):                               # enforced contract
    hs_code: str                                     # code
    percent: float                                   # rate

json_task = Task(description="Duty for HS {hs}?",
                 expected_output="hs_code and percent",   # still describe it in words
                 agent=agent, output_pydantic=Duty)  # + parsed into a model
print(json_task.output_pydantic.__name__)            # Duty
```
Verified: ran offline (printed `Duty`, the Pydantic class name). Real model compliance with JSON formats: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# expected_output_api.py - contract validated twice: Pydantic parse + guardrail
from typing import Any                               # typing
from pydantic import BaseModel                       # schema
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web

app = FastAPI()                                      # app

class Duty(BaseModel):                               # contract
    hs_code: str                                     # code
    percent: float                                   # rate

def check(out: Any) -> tuple[bool, Any]:             # guardrail
    ok = out.pydantic is not None and 0 <= out.pydantic.percent <= 100   # parsed AND sane
    return (True, out) if ok else (False, "Return JSON {hs_code, percent} with percent 0-100")

class Q(BaseModel):                                  # body
    hs: str                                          # input

@app.post("/contract", response_model=Duty)          # response typed by the same model
async def contract(q: Q) -> Duty:                    # endpoint
    agent = Agent(role="Analyst", goal="Find duty", backstory="Careful.", llm=LLM(model="gpt-4o-mini"))
    task = Task(description="Duty for HS {hs}.", expected_output="JSON: hs_code, percent",
                agent=agent, output_pydantic=Duty, guardrail=check)
    try:
        out = await Crew(agents=[agent], tasks=[task]).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # failure
        raise HTTPException(502, type(exc).__name__) from exc
    if out.pydantic is None:                         # parse failed after retries
        raise HTTPException(502, "invalid model output")
    return out.pydantic                              # validated
```
Verified with `TestClient` (HTTP 200 and the validated JSON). The response model equals the task's output model so FastAPI documents the contract (OpenAPI) automatically. Failure path returns 502 when parsing still yields `None`.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Output contract | State schema / structured output | `expected_output` + `output_pydantic` | `output_type` | Structured output / message schema |
| Enforcement | Schema validation in node | Parse + guardrail retries | Schema + output guardrails | Validation in code |
| Natural language target | Prompt text | `expected_output` string (required) | Instructions | System message |
| API alignment | Pydantic state -> response | Same Pydantic model as response | Same | Same |
| Failure signal | Exception / empty value | `pydantic is None` | Exception | Parse error |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: expected_output='A good answer'.
✅ Correct: Specify format, fields and limits, ideally with an example.

❌ Mistake 2: Only text description but code expects JSON.
✅ Correct: Add `output_pydantic` and handle `None`.

❌ Mistake 3: Contract mismatch between task and API response model.
✅ Correct: Use one Pydantic model for task output and FastAPI `response_model`.

---

## 🧠 Tricky Interview Question
The model returns the right JSON wrapped in markdown fences. What do you do?

Answer: That is a typical parse failure source. Say 'return only raw JSON, no markdown' in `expected_output`, supply a tiny example, use `output_pydantic` (CrewAI tries to convert), add a guardrail that returns `(False, 'Return only raw JSON')` to trigger a corrective retry, and consider the provider's native structured-output mode if available. Keep a counter of parse failures to decide when the prompt needs rework.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Is `expected_output` optional?
A1: No, a Task requires `description` and `expected_output`.

Q2: [Medium] `expected_output` vs `output_pydantic`?
A2: The first is natural-language guidance in the prompt; the second parses and validates the result into a model.

Q3: [Hard] How do you make outputs reliable?
A3: Precise format with example, Pydantic model, guardrail with corrective messages, low temperature, and handling of `None`.

Q4: [Hard] Why align with FastAPI `response_model`?
A4: One schema for generation and API response gives validation, documentation and consistency.

Q5: [System Design] Versioned output schemas for many consumers?
A5: Schema registry, versioned Pydantic models, backward-compatible additions, contract tests, and adapters per consumer.

---

## 💰 Cost Impact
Formula: expected_output tokens x iterations (resent each loop) plus retry cost when parsing fails: (1 + retries) x task cost. A tight contract reduces retries and unnecessary prose (fewer output tokens). Approximate: structured JSON is usually shorter than prose explanations - measure for your case.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Any task consumed by code or another task
- APIs returning typed JSON

❌ Avoid when:
- Over-specifying trivial chat answers
- Contracts the model cannot meet without tools

---

## 📊 Visual Diagram
```
  expected_output (words) ---> prompt ---> LLM ---> raw text
                                              |
                              output_pydantic parse
                                  |ok           |None
                                  v             v
                            guardrail(range)   retry with feedback / 502
                                  |ok
                                  v
                       typed result -> API response_model
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| expected_output | Description of the desired result | अपेक्षित आउटपुट |
| Contract | Agreed output shape | अनुबंध |
| Schema | Structure definition of data | स्कीमा |
| Structured output | Machine-readable output | संरचित आउटपुट |
| Parse failure | Output not matching schema | पार्स विफलता |
| response_model | FastAPI output schema | रिस्पॉन्स मॉडल |

---

## ⚡ 3-Line Summary
English: expected_output is the target; output_pydantic enforces the shape and guardrails enforce business rules. Use one model for both task and API, and plan for None.
Hindi: expected_output लक्ष्य है; output_pydantic shape लागू करता है और guardrails business rules। Task और API दोनों के लिए एक ही model रखें और None के लिए तैयार रहें।

---

## ➡️ Next Topic
**083. Task agent assignment** - deciding which agent owns which task.

---
