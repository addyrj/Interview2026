---

# 099. Common Structured Output Patterns
# हिंदी में: Structured Output के आम Patterns

---

## 🔵 Simple Definition (English)
Patterns are reusable recipes for structured output. The five most common are: **Extraction** (pull fields from text), **Classification** (pick a label), **Routing** (choose the next step), **Scoring/Grading** (give a rating with reasons) and **Decision with evidence** (answer plus a quote that proves it). Learn these and most LLM features are variations.

## 🔵 सरल परिभाषा (Hindi)
Patterns structured output के दोबारा काम आने वाले recipes हैं। पाँच सबसे आम: **Extraction** (text से fields निकालना), **Classification** (label चुनना), **Routing** (अगला step चुनना), **Scoring/Grading** (कारणों के साथ rating) और **Decision with evidence** (answer के साथ सबूत वाला quote)। ये सीख लो तो ज़्यादातर LLM features इन्हीं के रूप हैं।

---

## 🔴 Problem it Solves
Teams reinvent schemas for each feature and repeat the same mistakes. A pattern library gives tested shapes (with null handling, enums, evidence, confidence) that you copy and adapt, saving design time and improving quality.

## 🔴 यह क्यों बना? (Hindi)
Teams हर feature के लिए schema फिर से बनाती हैं और वही गलतियाँ दोहराती हैं। Pattern library tested shapes (null handling, enums, evidence, confidence के साथ) देती है जिन्हें copy और adapt करो, इससे design time बचता है और quality बढ़ती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the task type: extract / classify / route / score / decide
Step 2 → Pick the matching pattern (schema skeleton)
Step 3 → Replace field names and enums with your domain's
Step 4 → Add the safety fields: confidence, evidence, needs_review
Step 5 → Write a short system prompt for the pattern (role + rules + null policy)
Step 6 → Test on labelled examples
Step 7 → Wrap in a generic helper so every feature reuses the same call/validate/retry code
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task type पहचानो: extract / classify / route / score / decide
Step 2 → मेल खाने वाला pattern (schema skeleton) चुनो
Step 3 → Field names और enums को अपने domain के बनाओ
Step 4 → Safety fields जोड़ो: confidence, evidence, needs_review
Step 5 → Pattern के लिए छोटा system prompt लिखो (role + rules + null policy)
Step 6 → Labelled examples पर test करो
Step 7 → एक generic helper में wrap करो ताकि हर feature वही call/validate/retry code use करे
```

---

## 🟡 Real World Example
**Tariff Classification System** uses all five:
- Extraction: pull product name, material, origin from an invoice line.
- Classification: choose the HS chapter.
- Routing: `auto_approve | ask_user | human_review`.
- Scoring: rate "description quality" 1-5 to decide if more detail is needed.
- Decision with evidence: final HS code plus the words from the product text that justify it.

**Zomato-style**: Routing support chats to refund/delivery/payment teams.

## 🟡 Real Example Hindi mein
**Tariff System** पाँचों use करता है:
- Extraction: invoice line से product name, material, origin निकालना।
- Classification: HS chapter चुनना।
- Routing: `auto_approve | ask_user | human_review`।
- Scoring: "description quality" को 1-5 rate करना कि और detail चाहिए या नहीं।
- Decision with evidence: अंतिम HS code और product text के वे शब्द जो उसे justify करते हैं।

**Zomato-style**: Support chats को refund/delivery/payment teams में route करना।

---

## 💻 Code Example — Basic
```python
# Basic: the five pattern skeletons as Pydantic models + a generic validator.
# Needs: pip install pydantic. Runs offline with canned replies.
from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError

class Extraction(BaseModel):                            # pattern 1: pull fields (null if absent)
    product_name: str
    material: Optional[str]
    origin_country: Optional[str]

class Classification(BaseModel):                        # pattern 2: choose a label + confidence
    chapter: Literal["85", "64", "61", "other"]
    confidence: float = Field(ge=0, le=1)

class Routing(BaseModel):                               # pattern 3: choose the next step
    next_step: Literal["auto_approve", "ask_user", "human_review"]
    reason: str

class Scoring(BaseModel):                               # pattern 4: rating with reasons first
    reasons: list[str]
    quality_score: int = Field(ge=1, le=5)

class Decision(BaseModel):                              # pattern 5: answer + evidence
    evidence_quote: str = Field(description="Exact words from the input supporting the answer")
    hs_code: str

def validate(model: type[BaseModel], raw: str) -> Optional[BaseModel]:
    """Generic: parse raw JSON into the pattern model or return None."""
    try:
        return model.model_validate_json(raw)
    except ValidationError as exc:
        print(model.__name__, "invalid:", exc.errors()[0]["msg"])
        return None

samples = [
    (Extraction, '{"product_name": "T-shirt", "material": "cotton", "origin_country": null}'),
    (Classification, '{"chapter": "85", "confidence": 0.93}'),
    (Routing, '{"next_step": "ask_user", "reason": "origin missing"}'),
    (Scoring, '{"reasons": ["no material"], "quality_score": 2}'),
    (Decision, '{"evidence_quote": "wireless earbuds", "hs_code": "8518.30"}'),
    (Routing, '{"next_step": "delete_everything", "reason": "x"}'),     # invalid label
]
for model, raw in samples:
    print(model.__name__, "->", validate(model, raw) is not None)
```

## 💻 Code Example — Advanced
```python
# Production: ONE generic async helper for all patterns, with retry and usage tracking.
import asyncio
from typing import Optional, TypeVar
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

client = AsyncOpenAI()
T = TypeVar("T", bound=BaseModel)

async def run_pattern(
    schema: type[T],                                   # which pattern/model
    system: str,                                       # pattern-specific instructions
    user: str,                                         # the input text
    *, model: str = "gpt-4o-mini",
    max_tokens: int = 300,
    retries: int = 1,
) -> Optional[T]:
    """Call -> validate -> retry with feedback. Returns None when it cannot comply."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    for attempt in range(retries + 1):
        try:
            completion = await client.beta.chat.completions.parse(
                model=model, messages=messages, response_format=schema,
                temperature=0, max_tokens=max_tokens)
        except ValidationError as exc:                 # semantic failure -> feedback loop
            messages.append({"role": "user", "content": f"Invalid: {exc.errors()[0]['msg']}. Fix it."})
            continue
        except OpenAIError as exc:                     # infrastructure failure
            print("API error:", exc)
            return None
        msg = completion.choices[0].message
        if msg.refusal:
            return None
        return msg.parsed
    return None

# Pattern instances (system prompts) -- reuse the same helper everywhere:
EXTRACT_SYS = "Extract fields from the text. Use null if a value is not stated. Never guess."
ROUTE_SYS = "Choose the next step. ask_user if key facts are missing; human_review if confidence < 0.7."

async def main() -> None:
    from_extraction = await run_pattern(Extraction, EXTRACT_SYS, "Cotton T-shirt, 20 pcs")  # needs API key
    print(from_extraction)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

PATTERNS: dict[str, tuple[type[BaseModel], str]] = {   # name -> (schema, system prompt)
    "extract": (Extraction, EXTRACT_SYS),
    "route": (Routing, ROUTE_SYS),
}

@app.post("/pattern/{name}")
async def pattern_endpoint(name: str, text: str) -> dict:
    """One generic endpoint serving several patterns (internal tools / prototyping)."""
    if name not in PATTERNS:
        raise HTTPException(status_code=404, detail="unknown pattern")
    schema, system = PATTERNS[name]
    result = await run_pattern(schema, system, text)
    if result is None:
        raise HTTPException(status_code=502, detail="LLM failed")
    return result.model_dump()
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extract = llm.with_structured_output(Extraction)
route = llm.with_structured_output(Routing)
# LangGraph: nodes = patterns. extract_node -> classify_node -> route_node,
# then add_conditional_edges("route_node", lambda s: s["route"].next_step,
#   {"auto_approve": "save", "ask_user": "ask", "human_review": "queue"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Classification without an "other/unsure" label and no confidence
✅ Correct: Include an escape label and a confidence or `needs_review` field.

```python
# Wrong: chapter: Literal["85","64"]   # forced guess
# Right: chapter: Literal["85","64","other"]; confidence: float
```

❌ Mistake 2: Scoring without reasons
✅ Correct: Reasons first, then the number, so scores are consistent and auditable.

```python
# Wrong: class S(BaseModel): quality_score: int
# Right: class S(BaseModel): reasons: list[str]; quality_score: int
```

---

## 🧠 Tricky Interview Question

**Q**: "LLM scores (1-10) for the same text vary between runs even at temperature 0 and between prompt versions. How do you make scoring reliable?"

**Answer**: Numeric scales are poorly calibrated. Use a small rubric with defined levels (anchors) in the prompt, fewer levels (1-5 or categorical: poor/ok/good), reasons before the score, few-shot examples per level, and calibrate against human labels. Average across multiple samples or use pairwise comparisons if consistency is critical, and track agreement with humans over time.

---

## ⚫ Interview Questions + Answers

Q1: Name common structured output patterns.
A1: Extraction, classification, routing, scoring, decision-with-evidence.

Q2: Why include an evidence quote?
A2: It reduces hallucination and makes answers verifiable: you can check that the quote exists in the source text.

Q3: How is routing different from classification?
A3: Classification labels data; routing chooses an action/next node. Routing outputs drive control flow.

Q4: Why a confidence field? Is it reliable?
A4: It enables thresholds and review queues. LLM self-reported confidence is poorly calibrated, so calibrate it against labelled data or use logprobs/agreement across samples.

Q5: How do you build a reusable library of patterns?
A5: A generic `run_pattern(schema, system, input)` helper plus a registry of schemas and prompts, shared validation/retry/usage logging, a labelled eval set per pattern, and CI that re-runs evals when prompts or schemas change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting a new feature: pick the closest pattern
- Standardising across a team

❌ Avoid when:
- Task is novel and does not fit (design a custom schema, but borrow safety fields)

---

## 📊 Visual Diagram
```
 EXTRACT   text ─► {fields | null}
 CLASSIFY  text ─► {label ∈ enum, confidence}
 ROUTE     state ─► {next_step ∈ enum, reason}
 SCORE     text ─► {reasons[], score 1-5}
 DECIDE    text ─► {evidence_quote, answer}

 Typical Tariff flow:
 EXTRACT ─► CLASSIFY ─► DECIDE ─► ROUTE ─► save | ask user | human review
```

---

## 💰 Cost Impact
Each pattern call costs input (schema + prompt + text) plus a small output (20-100 tokens). Chaining five patterns is five calls: use small models for easy patterns (route, classify) and a stronger model only for the hard one (decide).
Optimise: merge extract+classify into one call when accuracy allows, cache by normalised input, prompt caching for system prompts, cap `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Extraction | Pull fields from text | Text से fields निकालना |
| Classification | Choose a label | Label चुनना |
| Routing | Choose next step | अगला step चुनना |
| Scoring | Rate with reasons | Reasons के साथ rating |
| Evidence | Proof quote from source | Source से सबूत |
| Rubric | Defined scoring levels | Scoring के तय स्तर |

---

## ⚡ 3-Line Summary
English: Most structured-output features are five patterns: extract, classify, route, score and decide with evidence. Add confidence, evidence and null/other options. Build one generic helper to reuse everywhere.
Hindi: ज़्यादातर structured-output features पाँच patterns हैं: extract, classify, route, score और evidence के साथ decide। Confidence, evidence और null/other options जोड़ो। हर जगह reuse के लिए एक generic helper बनाओ।

---

## ➡️ Next Topic
**100. Structured Output for Tariff System** — the capstone: a full, production-style tariff pipeline using everything in this section.
