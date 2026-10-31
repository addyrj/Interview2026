---

# 409. Golden Dataset
# हिंदी में: Golden Dataset

---

## 🔵 Simple Definition (English)
A golden dataset is a small, carefully curated set of test cases whose expected answers were verified by domain experts (often by two annotators plus an adjudicator). It is the trusted "ground truth" used to measure accuracy, calibrate LLM judges, and catch regressions.

## 🔵 सरल परिभाषा (Hindi)
Golden dataset test cases का छोटा, ध्यान से बनाया गया set है जिसके expected answers domain experts ने verify किए हैं (अक्सर दो annotators और एक adjudicator)। यही भरोसेमंद "ground truth" है जिससे accuracy नापी जाती है, LLM judges calibrate होते हैं और regressions पकड़े जाते हैं।

---

## 🔴 Problem it Solves
Bulk or synthetic data may contain wrong labels, and LLM judges can be biased. You need one small set you trust completely to answer: "Is the system actually correct?" and "Is my judge accurate?". Without it, you measure noise with noise.

## 🔴 यह क्यों बना? (Hindi)
Bulk या synthetic data में गलत labels हो सकते हैं और LLM judges biased हो सकते हैं। आपको एक छोटा set चाहिए जिस पर पूरा भरोसा हो ताकि जवाब मिले: "क्या system सच में सही है?" और "क्या मेरा judge सही है?"। इसके बिना आप noise को noise से नाप रहे हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Select representative + high-risk cases (50-200)
Step 2 → Two experts label independently
Step 3 → Measure inter-annotator agreement (Cohen's kappa)
Step 4 → A senior expert resolves disagreements (adjudication) and writes rationale
Step 5 → Lock the set: version, hash, read-only
Step 6 → Use it to (a) score the system, (b) calibrate LLM judges, (c) gate releases
Step 7 → Add new cases only through review; never auto-add
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Representative + high-risk cases चुनो (50-200)
Step 2 → दो experts अलग-अलग label करें
Step 3 → Inter-annotator agreement (Cohen's kappa) नापो
Step 4 → Senior expert असहमति सुलझाए (adjudication) और कारण लिखे
Step 5 → Set lock करो: version, hash, read-only
Step 6 → इस्तेमाल: (a) system score, (b) LLM judges calibrate, (c) release gate
Step 7 → नए cases सिर्फ review से जोड़ो; auto-add कभी नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: 120 golden cases, each with the correct 8-digit HS code, the governing note, and a rationale, labelled by two licensed customs brokers (kappa 0.82) and adjudicated by a senior officer. A release is blocked if exact-match accuracy on the golden set drops by more than 2 points. The golden set also checks the LLM judge: judge verdicts must agree with expert verdicts on >= 90% of cases.

**Amazon-style**: A golden set of 200 policy-sensitive product questions (returns, warranty) verified by the legal team.

## 🟡 Real Example Hindi mein
**Tariff System**: 120 golden cases, हर एक में सही 8-digit HS code, लागू note और rationale; दो licensed customs brokers ने label किया (kappa 0.82) और senior officer ने adjudicate किया। Golden set पर exact-match accuracy 2 points से ज़्यादा गिरे तो release रुकता है। Golden set LLM judge भी जाँचता है: judge का verdict कम से कम 90% cases में experts से मिलना चाहिए।

**Amazon-style**: Policy-sensitive product सवालों (returns, warranty) के 200 golden cases, legal team द्वारा verified।

---

## 💻 Code Example — Basic
```python
# Basic: Cohen's kappa between two annotators (pure Python, runs offline)
from collections import Counter  # count label frequencies


def cohens_kappa(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:  # validate inputs
        raise ValueError("label lists must be same non-zero length")  # clear error
    n = len(a)  # number of items
    observed = sum(x == y for x, y in zip(a, b)) / n  # raw agreement
    ca, cb = Counter(a), Counter(b)  # label counts per annotator
    expected = sum((ca[k] / n) * (cb[k] / n) for k in set(a) | set(b))  # chance agreement
    if expected == 1:  # everyone always says same label
        return 1.0  # perfect by definition
    return (observed - expected) / (1 - expected)  # kappa formula


ann1 = ["8507", "8517", "6109", "8507", "8517", "6109", "8507", "8517"]  # annotator 1
ann2 = ["8507", "8517", "6109", "8507", "6109", "6109", "8507", "8517"]  # annotator 2 (1 disagreement)
print(round(cohens_kappa(ann1, ann2), 3))  # high agreement, around 0.8
# Rule of thumb: >0.8 strong, 0.6-0.8 good, <0.6 rubric/labels need work
```

## 💻 Code Example — Advanced
```python
# Advanced: locked golden set with integrity hash + async regression gate
import asyncio  # concurrency
import hashlib  # integrity
import json  # IO
import logging  # logs
from pathlib import Path  # paths
from typing import Awaitable, Callable  # type hints

from pydantic import BaseModel  # schema

log = logging.getLogger("golden")  # logger


class Golden(BaseModel):  # one golden case
    id: str  # stable id
    question: str  # input
    hs_code: str  # expert-verified answer
    rationale: str  # why (helps debugging and judge calibration)


def load_golden(path: Path, expected_sha: str) -> list[Golden]:
    raw = path.read_bytes()  # read file bytes
    sha = hashlib.sha256(raw).hexdigest()  # compute hash
    if sha != expected_sha:  # detect silent edits
        raise RuntimeError(f"golden set changed! {sha[:10]} != {expected_sha[:10]}")  # block run
    return [Golden(**json.loads(line)) for line in raw.decode().splitlines() if line.strip()]  # parse JSONL


async def run_gate(
    cases: list[Golden],
    system: Callable[[str], Awaitable[str]],  # async function: question -> predicted HS code
    baseline_acc: float,  # accuracy of the current production version
    max_drop: float = 0.02,  # allowed regression
) -> dict:
    sem = asyncio.Semaphore(8)  # limit concurrency

    async def one(c: Golden) -> tuple[str, bool]:  # evaluate one case
        async with sem:  # respect limit
            try:
                pred = (await system(c.question)).strip()  # call system
            except Exception as exc:  # system error counts as wrong
                log.error("system failed on %s: %s", c.id, exc)  # log
                return c.id, False
            return c.id, pred == c.hs_code  # exact match

    results = await asyncio.gather(*(one(c) for c in cases))  # run all cases
    acc = sum(ok for _, ok in results) / len(results)  # accuracy
    failed = [i for i, ok in results if not ok]  # failing ids
    return {"accuracy": round(acc, 3), "baseline": baseline_acc,
            "passed": acc >= baseline_acc - max_drop, "failed_ids": failed}  # gate result
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web

app = FastAPI()  # app


async def candidate_system(q: str) -> str:  # stand-in for the new version
    return "8507.60"  # always same demo answer


@app.post("/release/check")  # called by CI before deployment
async def release_check() -> dict:
    try:
        cases = load_golden(Path("golden.jsonl"), expected_sha=GOLDEN_SHA)  # integrity check
    except (RuntimeError, FileNotFoundError) as exc:  # missing/changed
        raise HTTPException(500, str(exc))  # server-side problem
    result = await run_gate(cases, candidate_system, baseline_acc=0.91)  # evaluate
    if not result["passed"]:  # block release
        raise HTTPException(409, detail=result)  # conflict with details
    return result  # OK
```

---

## 🔗 LangChain / LangGraph Connection
Store the golden set as a LangSmith dataset and run your LangChain/LangGraph app with `evaluate()` using exact-match or custom evaluators; or load it as the `reference` column for Ragas/DeepEval. The golden set is also used to calibrate judge prompts.

```python
# Use golden cases to calibrate an LLM judge: measure judge-vs-expert agreement
def judge_agreement(judge_verdicts: list[bool], expert_verdicts: list[bool]) -> float:
    same = sum(j == e for j, e in zip(judge_verdicts, expert_verdicts))  # matches
    return same / len(expert_verdicts)  # fraction; require >= 0.9 before trusting the judge
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One annotator, no agreement check
✅ Correct: two annotators + kappa + adjudication

```python
# Wrong
label = annotator1_label
# Right
label = adjudicate(annotator1_label, annotator2_label) if kappa_ok else escalate()
```

❌ Mistake 2: Letting the golden set leak into prompts or few-shot examples
✅ Correct: keep it out of any prompt, fine-tuning data or retriever index.

❌ Mistake 3: Growing it automatically from model outputs
✅ Correct: add only expert-reviewed cases.

---

## 🧠 Tricky Interview Question
**Q**: "Two experts disagree on 30% of golden cases. What do you do?"

**Answer**: Do not average or pick randomly. Low agreement means the task or guidelines are ambiguous. Hold a calibration session, write clearer labelling guidelines with examples, add an "ambiguous/multiple valid" label or accept a set of valid answers, re-label, and re-measure kappa. Also report that the system's achievable ceiling is limited by human disagreement.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What makes a dataset "golden"?
A1: Expert-verified labels, high agreement, locked and versioned.

Q2: [Easy] Typical size?
A2: Small: 50-200 high-quality cases.

Q3: [Medium] Why compute Cohen's kappa?
A3: It measures agreement beyond chance, revealing ambiguous guidelines or unreliable labels.

Q4: [Medium] Golden vs synthetic dataset?
A4: Golden is small, expert-verified and trusted; synthetic is large, cheap, and may contain errors. Use golden for decisions and calibration, synthetic for breadth.

Q5: [Hard] How do you keep a golden set useful as the product changes?
A5: Review quarterly, retire obsolete cases (e.g. rule changes) with a changelog, add new expert-reviewed cases from incidents, bump versions, and keep a frozen legacy subset to track long-term trends.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Releasing or comparing versions
- Calibrating LLM judges

❌ Avoid when:
- Using it for day-to-day prompt tuning (it will overfit and leak)

---

## 📊 Visual Diagram
```
 candidates ─► Expert A ─┐
             ─► Expert B ─┼─► kappa check ─► adjudication ─► LOCKED golden v3 (sha256)
                          │                                     │
                          │          ┌──────────────────────────┼───────────────┐
                          │          ▼                          ▼               ▼
                          │   score system             calibrate judge   release gate
```

---

## 💰 Cost Impact
Human labelling dominates (e.g. 120 cases x 10 min x 2 experts = 40 hours). LLM costs are tiny: a full golden run of 120 cases at ~1.5K tokens on gpt-4o-mini costs about $0.03, so you can afford to run it on every PR.
Optimise: use the LLM to pre-fill rationales for experts to edit (saves time), cache runs per system version.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden dataset | Expert-verified test set | Expert द्वारा verified test set |
| Cohen's kappa | Agreement beyond chance | संयोग से अधिक सहमति |
| Adjudication | Resolving disagreement | असहमति सुलझाना |
| Regression gate | Block if score drops | Score गिरने पर रोक |
| Calibration | Aligning judge with experts | Judge को experts से मिलाना |

---

## ⚡ 3-Line Summary
English: A golden dataset is a small expert-verified, locked and versioned test set. Check annotator agreement, adjudicate and keep it out of prompts. Use it for release gates and judge calibration.
Hindi: Golden dataset छोटा expert-verified, locked और versioned test set है। Annotator agreement जाँचो, adjudicate करो और इसे prompts से बाहर रखो। Release gates और judge calibration में इस्तेमाल करो।

---

## ➡️ Next Topic
**410. Human Evaluation** - how humans review outputs, rating scales and annotation workflow.
