---

# 403. LLM as Judge Pattern
# हिंदी में: LLM as Judge Pattern

---

## 🔵 Simple Definition (English)
LLM-as-judge means using one LLM to grade the output of another LLM (or your system) against a rubric, returning a score and a reason. It scales evaluation of open-ended text where exact-match metrics fail.

## 🔵 सरल परिभाषा (Hindi)
LLM-as-judge में एक LLM दूसरे LLM (या आपके system) के output को rubric के आधार पर grade करता है और score व reason देता है। जहाँ exact-match metrics fail होते हैं, वहाँ open-ended text की evaluation scale करने का यही तरीका है।

---

## 🔴 Problem it Solves
Humans are the best graders but slow and expensive. BLEU/ROUGE only check word overlap and miss meaning. For free-text answers ("explain this tariff ruling") we need meaning-aware, cheap, repeatable grading. A judge LLM gives that, at some cost in bias and noise.

## 🔴 यह क्यों बना? (Hindi)
Humans सबसे अच्छे grader हैं पर धीमे और महँगे। BLEU/ROUGE सिर्फ शब्द overlap देखते हैं, अर्थ नहीं। Free-text answers के लिए meaning समझने वाली, सस्ती और repeatable grading चाहिए। Judge LLM यह देता है, बस bias और noise का trade-off है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a rubric (criteria, scale, examples)
Step 2 → Build judge prompt: rubric + question + (context) + answer(s)
Step 3 → Force structured output (JSON: score, reason)
Step 4 → Call judge with temperature 0
Step 5 → Validate/parse output; retry on bad JSON
Step 6 → Aggregate scores; calibrate against human labels
Step 7 → Monitor bias: position, verbosity, self-preference
```

Three common modes: **single-answer scoring**, **pairwise comparison (A vs B)**, **reference-based grading**.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Rubric तय करो (criteria, scale, examples)
Step 2 → Judge prompt बनाओ: rubric + question + (context) + answer(s)
Step 3 → Structured output (JSON: score, reason) force करो
Step 4 → Temperature 0 पर judge call करो
Step 5 → Output parse/validate करो; खराब JSON पर retry
Step 6 → Scores aggregate करो; human labels से calibrate करो
Step 7 → Bias monitor करो: position, verbosity, self-preference
```

---

## 🟡 Real World Example
**Tariff Classification System**: The system writes a justification: "Classified under 8517.13 because it is a smartphone...". A judge LLM checks the rubric: (1) correct chapter reasoning, (2) cites the tariff note, (3) no invented rules. Score 1-5 with reason. Low scores are routed to a customs officer.

**Zomato-style**: Pairwise judge picks the better of two restaurant-recommendation responses (A/B test), with order randomised.

## 🟡 Real Example Hindi mein
**Tariff System**: System justification लिखता है: "8517.13 में classify किया क्योंकि यह smartphone है...". Judge LLM rubric जाँचता है: (1) chapter reasoning सही, (2) tariff note का हवाला, (3) बनाए हुए नियम नहीं। 1-5 score और reason। कम score वाले customs officer को जाते हैं।

**Zomato-style**: Pairwise judge दो restaurant-recommendation responses में बेहतर चुनता है, order random रखकर।

---

## 💻 Code Example — Basic
```python
# Basic: judge prompt + strict JSON parsing with a fake judge (runs offline)
import json  # to parse judge output
from dataclasses import dataclass  # simple result container


@dataclass
class Verdict:  # parsed judge result
    score: int  # 1..5
    reason: str  # short explanation


RUBRIC = "Score 1-5: 5 = correct HS code and cites tariff note; 1 = wrong or invented."  # criteria


def build_prompt(question: str, answer: str) -> str:  # create judge prompt
    return (f"{RUBRIC}\nQuestion: {question}\nAnswer: {answer}\n"
            'Reply ONLY with JSON: {"score": <1-5>, "reason": "<short>"}')  # force format


def fake_judge(prompt: str) -> str:  # stand-in for a real LLM call
    return '{"score": 4, "reason": "Correct code, note not cited."}'  # canned reply


def parse(raw: str) -> Verdict:  # validate judge output
    try:
        data = json.loads(raw)  # parse JSON
        score = int(data["score"])  # must be int
        if not 1 <= score <= 5:  # range check
            raise ValueError("score out of range")  # invalid
        return Verdict(score, str(data["reason"]))  # build result
    except (json.JSONDecodeError, KeyError, ValueError) as exc:  # any bad format
        raise ValueError(f"bad judge output: {exc}") from exc  # raise clear error


v = parse(fake_judge(build_prompt("HS code for iPhone?", "8517.13")))  # run
print(v)  # Verdict(score=4, reason='Correct code, note not cited.')
```

## 💻 Code Example — Advanced
```python
# Advanced: async OpenAI judge with pydantic validation, retries, and position-swap for pairwise
# pip install openai pydantic
import asyncio  # concurrency
import json  # parse
import logging  # logs
from typing import Literal  # type for winner

from openai import AsyncOpenAI, APIError, RateLimitError  # client + errors
from pydantic import BaseModel, Field, ValidationError  # validation

log = logging.getLogger("judge")  # logger
client = AsyncOpenAI()  # reads OPENAI_API_KEY


class Score(BaseModel):  # single-answer verdict
    score: int = Field(ge=1, le=5)  # 1..5
    reason: str  # explanation


class Pair(BaseModel):  # pairwise verdict
    winner: Literal["A", "B", "tie"]  # which is better
    reason: str  # explanation


async def call_judge(system: str, user: str, retries: int = 3) -> dict:
    for attempt in range(retries):  # retry loop
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0,  # deterministic judge
                response_format={"type": "json_object"},  # force JSON
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}])
            return json.loads(r.choices[0].message.content)  # parsed dict
        except RateLimitError:  # 429
            await asyncio.sleep(2 ** attempt)  # exponential backoff
        except (APIError, json.JSONDecodeError) as exc:  # other failures
            log.warning("judge attempt %d failed: %s", attempt, exc)  # log
    raise RuntimeError("judge failed after retries")  # give up


async def grade(question: str, answer: str) -> Score:
    data = await call_judge(
        'You are a strict grader. Return JSON {"score":1-5,"reason":"..."}.',
        f"Question: {question}\nAnswer: {answer}")  # prompt
    try:
        return Score(**data)  # validate fields
    except ValidationError as exc:  # schema mismatch
        raise RuntimeError(f"invalid verdict: {exc}") from exc


async def compare(q: str, a: str, b: str) -> str:
    """Run twice with swapped order to cancel position bias."""
    async def once(x: str, y: str) -> str:  # one judging call
        d = await call_judge('Return JSON {"winner":"A|B|tie","reason":"..."}.',
                             f"Question: {q}\nA: {x}\nB: {y}")  # pairwise prompt
        return Pair(**d).winner  # validated winner
    w1, w2 = await asyncio.gather(once(a, b), once(b, a))  # both orders
    flip = {"A": "B", "B": "A", "tie": "tie"}  # map swapped result back
    return w1 if w1 == flip[w2] else "tie"  # disagree -> tie
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # request models

app = FastAPI()  # app


class GradeReq(BaseModel):  # request
    question: str  # user question
    answer: str  # answer to grade


@app.post("/judge/grade", response_model=Score)  # endpoint returns validated Score
async def judge_endpoint(req: GradeReq) -> Score:
    try:
        return await grade(req.question, req.answer)  # call judge
    except RuntimeError as exc:  # judge failure
        raise HTTPException(502, str(exc))  # upstream error
```

---

## 🔗 LangChain / LangGraph Connection
LangChain can enforce the judge schema with `with_structured_output`. In LangGraph, add a "grader" node after generation; if score < 3, loop back to regenerate (self-correcting RAG).

```python
from langchain_openai import ChatOpenAI  # model
judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Score)  # schema-enforced
# verdict = judge.invoke("Question: ...\nAnswer: ...")   # returns a Score object
# LangGraph: add_conditional_edges("grade", lambda s: "retry" if s["score"] < 3 else "end")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague rubric ("is this good?")
✅ Correct: specific, anchored scale

```python
# Wrong
prompt = "Rate this answer."
# Right
prompt = "Score 1-5. 5=correct HS code AND cites note. 3=correct code, no note. 1=wrong code."
```

❌ Mistake 2: Pairwise judging in one order only (position bias)
✅ Correct: judge A/B and B/A, accept only consistent wins.

❌ Mistake 3: Trusting the judge without human calibration
✅ Correct: label 50 rows by hand, measure agreement first.

---

## 🧠 Tricky Interview Question
**Q**: "Your judge gives longer answers higher scores, and the model team starts making answers verbose. How do you fix this?"

**Answer**: This is verbosity bias, and optimisation against the judge (Goodhart's law) amplifies it. Fixes: put "do not reward length" and a conciseness criterion in the rubric, add length-controlled comparisons, include short-but-correct examples in the rubric, track answer length alongside the score, and spot-check with humans.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is LLM-as-judge?
A1: Using an LLM to grade other outputs against a rubric.

Q2: [Easy] Why temperature 0?
A2: Reduces randomness so scores are more reproducible.

Q3: [Medium] Name three known judge biases.
A3: Position bias, verbosity bias, self-preference bias.

Q4: [Medium] Pointwise vs pairwise judging?
A4: Pointwise gives an absolute score (easy to aggregate, less discriminative); pairwise picks the better of two (more reliable for ranking, needs order swapping).

Q5: [Hard] How do you prove your judge is reliable?
A5: Build a human-labelled set, compute agreement (Spearman/kappa), check consistency across repeated runs, test bias with perturbations (shuffle order, pad length), and re-validate when the judge model version changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Outputs are open-ended text
- You need many evaluations quickly

❌ Avoid when:
- A deterministic check exists (exact match, unit test, schema validation)
- High-stakes decisions without human review

---

## 📊 Visual Diagram
```
 question + answer ──► [ judge prompt: rubric ] ──► LLM (temp 0)
                                                      │
                                      JSON {score, reason}
                                                      ▼
                              validate ──► aggregate ──► compare to human labels
                              (pairwise: run A/B and B/A, keep consistent wins)
```

---

## 💰 Cost Impact
One judge call ≈ 600-1,500 input tokens + 80 output tokens. 1,000 gradings on gpt-4o-mini ≈ 1.2M in + 80K out ≈ $0.23. Pairwise with swap doubles it.
Optimise: use deterministic checks first, cheap judge model, short rubrics, cache by (rubric, question, answer) hash, grade a sample in production.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rubric | Grading criteria | Grading के मानदंड |
| Pointwise | Score one answer | एक answer को score |
| Pairwise | Choose better of two | दो में बेहतर चुनना |
| Position bias | Prefers first/last | पहले/आखिरी को पसंद करना |
| Verbosity bias | Prefers long answers | लंबे answers को पसंद |
| Goodhart's law | Metric becomes target, loses value | Metric लक्ष्य बने तो बेकार |

---

## ⚡ 3-Line Summary
English: LLM-as-judge grades outputs with a rubric and structured JSON. Control bias with order swapping, clear rubrics and temperature 0. Always calibrate against human labels.
Hindi: LLM-as-judge rubric और structured JSON से outputs grade करता है। Order swap, साफ rubric और temperature 0 से bias कम करो। हमेशा human labels से calibrate करो।

---

## ➡️ Next Topic
**404. G-Eval Framework** - a formal LLM-judge method with generated steps and probability-weighted scores.
