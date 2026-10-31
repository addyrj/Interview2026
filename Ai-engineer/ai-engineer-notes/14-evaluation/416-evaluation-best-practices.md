---

# 416. Evaluation Best Practices
# हिंदी में: Evaluation की Best Practices

---

## 🔵 Simple Definition (English)
Evaluation best practices are the habits that make your AI scores trustworthy: a good golden dataset, many small focused metrics, human-checked LLM judges, versioning, and tracking results over time. A bad eval gives false confidence, which is worse than no eval.

## 🔵 सरल परिभाषा (Hindi)
Evaluation best practices वे आदतें हैं जिनसे आपके AI scores भरोसेमंद बनते हैं: अच्छा golden dataset, कई छोटे focused metrics, human से जाँचे हुए LLM judges, versioning, और समय के साथ results की tracking। खराब eval झूठा भरोसा देता है, जो eval न होने से भी बुरा है।

---

## 🔴 Problem it Solves
- Teams build evals on 10 hand-picked easy examples, see 95%, ship, and users find failures instantly.
- LLM judges are biased (prefer long answers, prefer their own style) and nobody checks them.
- Prompts get tuned until they overfit the eval set, so the score rises but real quality does not.
- Results are in notebooks, not versioned, so nobody knows if v12 is better than v11.

## 🔴 यह क्यों बना? (Hindi)
- Teams 10 आसान examples पर eval बनाती हैं, 95% देखती हैं, ship करती हैं, और users को तुरंत failures मिल जाते हैं।
- LLM judges biased होते हैं (लंबे answers पसंद करते हैं) और कोई उन्हें जाँचता नहीं।
- Prompt को eval set पर इतना tune करते हैं कि score बढ़ता है पर असली quality नहीं।
- Results notebooks में रहते हैं, version नहीं होते, इसलिए पता नहीं v12, v11 से बेहतर है या नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define success per use-case (what is a "correct" answer?)
Step 2 → Build dataset from REAL traffic; cover easy, hard, edge, adversarial
Step 3 → Split: dev set (tune on it) and held-out test set (never tune on it)
Step 4 → Use several simple metrics, not one vague "quality" score
Step 5 → Prefer deterministic checks; use LLM-judge only where needed
Step 6 → Calibrate the judge against human labels (agreement score)
Step 7 → Version dataset + prompt + model + results; track trend
Step 8 → Feed production failures back into the dataset (flywheel)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर use-case के लिए success define करो ("सही answer" क्या है?)
Step 2 → असली traffic से dataset बनाओ; आसान, कठिन, edge, adversarial सब
Step 3 → Split: dev set (इस पर tune करो) और held-out test set (इस पर कभी tune नहीं)
Step 4 → एक धुंधले "quality" score की जगह कई सरल metrics
Step 5 → Deterministic checks को प्राथमिकता, LLM-judge सिर्फ़ ज़रूरत पर
Step 6 → Judge को human labels से calibrate करो (agreement score)
Step 7 → Dataset + prompt + model + results version करो; trend देखो
Step 8 → Production failures वापस dataset में डालो (flywheel)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team had 30 examples, all electronics. Accuracy 96%. In production, textile and chemical products failed. Best-practice fix: stratified dataset of 300 products across all 21 HS sections, a held-out set of 100, separate metrics (6-digit match, 8-digit match, valid-code rate, explanation faithfulness), and a judge for explanations calibrated against 60 customs-officer labels (agreement 88%). Every wrong production answer reported by a user is added with its correct HS code.

**Zomato AI**: Metrics split into "dietary constraint respected" (rule check), "price within budget" (rule check) and "recommendation feels relevant" (judge).

## 🟡 Real Example Hindi mein
**Tariff System**: Team के पास 30 examples थे, सब electronics। Accuracy 96%। Production में textile और chemical products fail हुए। Best-practice fix: HS के सभी 21 sections में 300 products का stratified dataset, 100 का held-out set, अलग metrics (6-digit match, 8-digit match, valid-code rate, explanation faithfulness), और explanations के लिए judge जो 60 customs-officer labels से calibrate हुआ (agreement 88%)। User की बताई हर गलती सही HS code के साथ dataset में जुड़ती है।

**Zomato AI**: Metrics अलग-अलग: "dietary constraint माना गया" (rule), "price budget में" (rule), "recommendation relevant लगा" (judge)।

---

## 💻 Code Example — Basic
```python
# Basic best practice: stratified split + coverage check (pure Python, offline)
import random                                                 # for reproducible shuffling
from collections import Counter                               # to count categories

random.seed(42)                                               # fixed seed => same split every run

dataset: list[dict[str, str]] = [                             # tiny sample dataset
    {"q": "power bank", "section": "electronics", "exp": "8507"},
    {"q": "laptop", "section": "electronics", "exp": "8471"},
    {"q": "cotton shirt", "section": "textile", "exp": "6105"},
    {"q": "silk saree", "section": "textile", "exp": "5007"},
    {"q": "paint", "section": "chemical", "exp": "3208"},
    {"q": "soap", "section": "chemical", "exp": "3401"},
]

def split(data: list[dict[str, str]], test_ratio: float = 0.33) -> tuple[list, list]:
    by_section: dict[str, list] = {}                          # group rows by category
    for row in data:                                          # loop all rows
        by_section.setdefault(row["section"], []).append(row)  # add to its group
    dev, test = [], []                                        # two outputs
    for rows in by_section.values():                          # each category separately
        random.shuffle(rows)                                  # shuffle inside the group
        k = max(1, int(len(rows) * test_ratio))               # at least 1 test row per group
        test += rows[:k]                                      # first k go to test
        dev += rows[k:]                                       # rest go to dev
    return dev, test                                          # return both sets

dev, test = split(dataset)                                    # do the split
print("dev  :", Counter(r["section"] for r in dev))           # coverage in dev
print("test :", Counter(r["section"] for r in test))         # coverage in test
```

## 💻 Code Example — Advanced
```python
# Production helper: multi-metric scoring + judge calibration + versioned report
import asyncio                                                # concurrency
import hashlib                                                # dataset fingerprint
import json                                                   # report output
from dataclasses import dataclass, asdict                     # structured results
from typing import Awaitable, Callable                        # typing

Metric = Callable[[str, str], float]                          # (actual, expected) -> 0..1

def exact_6(actual: str, expected: str) -> float:             # metric 1: 6-digit heading match
    return float(actual.replace(".", "")[:6] == expected.replace(".", "")[:6])

def valid_format(actual: str, expected: str) -> float:        # metric 2: code looks like an HS code
    digits = actual.replace(".", "")                          # strip dots
    return float(digits.isdigit() and len(digits) in (6, 8, 10))

METRICS: dict[str, Metric] = {"exact_6": exact_6, "valid_format": valid_format}  # many small metrics

def fingerprint(rows: list[dict]) -> str:                     # version id for the dataset
    blob = json.dumps(rows, sort_keys=True).encode()          # stable serialisation
    return hashlib.sha256(blob).hexdigest()[:12]              # short hash

def cohen_kappa(a: list[int], b: list[int]) -> float:         # judge vs human agreement (binary)
    n = len(a)                                                # number of items
    if n == 0 or n != len(b):                                 # validate input
        raise ValueError("label lists must be same non-zero length")
    po = sum(x == y for x, y in zip(a, b)) / n                # observed agreement
    pa1, pb1 = sum(a) / n, sum(b) / n                         # share of 1s
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)                    # chance agreement
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)           # kappa

@dataclass
class EvalReport:                                             # versioned output
    dataset_version: str                                      # which data
    prompt_version: str                                       # which prompt
    model: str                                                # pinned model name
    scores: dict[str, float]                                  # metric -> mean score

async def evaluate(pipe: Callable[[str], Awaitable[str]], rows: list[dict],
                   prompt_version: str, model: str) -> EvalReport:
    outs = await asyncio.gather(*(pipe(r["q"]) for r in rows), return_exceptions=True)  # keep errors
    scores: dict[str, float] = {}                             # results
    for name, fn in METRICS.items():                          # every metric
        vals = [fn(o, r["exp"]) if isinstance(o, str) else 0.0 for o, r in zip(outs, rows)]  # error => 0
        scores[name] = sum(vals) / max(len(vals), 1)          # mean score
    return EvalReport(fingerprint(rows), prompt_version, model, scores)

async def fake_pipe(q: str) -> str:                           # mock pipeline
    return "8507.60" if "power" in q else "8471.30"

if __name__ == "__main__":
    rows = [{"q": "power bank", "exp": "8507.60"}, {"q": "laptop", "exp": "8471.30"}]
    rep = asyncio.run(evaluate(fake_pipe, rows, "prompt-v7", "gpt-4o-mini-2024-07-18"))
    print(json.dumps(asdict(rep), indent=2))                  # store this JSON per run
    print("kappa:", round(cohen_kappa([1, 1, 0, 1, 0], [1, 0, 0, 1, 0]), 2))  # judge calibration
```

---

## 🟠 FastAPI Integration
Collect real user feedback ("wrong HS code") through the API and write it to a review queue. After a human confirms the right answer, it joins the golden dataset. This is the data flywheel.

```python
from fastapi import FastAPI                                   # framework
from pydantic import BaseModel, Field                         # validation

app = FastAPI()                                               # app
REVIEW_QUEUE: list[dict] = []                                 # use a DB in production

class Feedback(BaseModel):                                    # feedback body
    question: str = Field(min_length=3)                       # original question
    model_answer: str                                         # what the system said
    user_says_correct: str | None = None                      # optional right answer

@app.post("/feedback")                                        # collect failures
async def feedback(fb: Feedback) -> dict[str, int]:
    REVIEW_QUEUE.append(fb.model_dump())                      # store for human review
    return {"queued": len(REVIEW_QUEUE)}                      # acknowledge
```

---

## 🔗 LangChain / LangGraph Connection
Keep datasets in LangSmith with named versions, and run `evaluate()` with several small evaluators. Each evaluator is a plain function returning a dict with `key` and `score`, which maps to one focused metric.

```python
def valid_format_evaluator(run, example) -> dict:             # LangSmith evaluator signature
    out = (run.outputs or {}).get("answer", "")               # model output
    digits = out.replace(".", "")                             # normalise
    return {"key": "valid_format", "score": int(digits.isdigit())}  # one focused metric
# langsmith.evaluate(target, data="tariff-golden-v3", evaluators=[valid_format_evaluator])
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Tuning the prompt on the same data you report results on.
✅ Correct: tune on dev, report on the held-out test set.

```python
# Wrong
best = max(prompts, key=lambda p: score(p, all_data))
# Right
best = max(prompts, key=lambda p: score(p, dev_data))
final = score(best, test_data)   # reported number
```

❌ Mistake 2: One LLM-judge "rate quality 1-10" metric with no calibration.
✅ Correct: binary, rubric-based criteria and a measured agreement with humans.

```python
# Wrong
prompt = "Rate this answer from 1 to 10."
# Right
prompt = "Answer PASS only if the HS code is in the retrieved context AND matches the product. Else FAIL."
```

---

## 🧠 Tricky Interview Question
**Q**: "Your judge model gives your new prompt 92% vs 85% for the old one. Do you ship?"

**Answer**: Not yet. Check (1) is the 7-point gap larger than noise (bootstrap confidence interval, repeat runs)? (2) Is the judge biased toward longer answers (compare answer length distributions)? (3) Does the judge agree with humans on a sample (kappa)? (4) Was the new prompt tuned on this same set? (5) Do deterministic metrics (exact HS match) agree? If they all agree and the gain holds on a held-out set, ship with a canary and monitor online.

---

## ⚫ Interview Questions + Answers

Q1: Why use a held-out test set? (Easy)
A1: To measure real generalisation. If you tune on a set, its score becomes optimistic.

Q2: Why prefer deterministic metrics over an LLM judge? (Easy)
A2: They are cheap, fast, repeatable and unbiased. Use a judge only for qualities that rules cannot check, like tone or explanation quality.

Q3: How do you validate an LLM judge? (Medium)
A3: Label 50-100 examples by humans, compare judge vs human with accuracy and Cohen's kappa, inspect disagreements, refine the rubric, and re-check whenever the judge model changes.

Q4: How big should a golden dataset be? (Medium)
A4: Start with 50-100 well-chosen cases, grow to a few hundred. What matters more than size is coverage of intents and failure modes. To detect a 3-point change reliably you need hundreds of cases, so use confidence intervals.

Q5: How do you stop evals from becoming outdated? (Hard)
A5: Run the flywheel: log production traces, sample low-feedback and low-confidence ones, have humans label them, add to the dataset with a version bump. Monitor drift between production query distribution and the dataset (embedding clustering). Pin model versions, review the dataset quarterly, and retire cases that no longer match business rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building any LLM feature that will go to real users
- Comparing prompts, models or retrievers
- Reporting quality to stakeholders

❌ Avoid when:
- Over-engineering a throwaway prototype (a quick manual check is enough)
- Trusting a single aggregate number without looking at failures

---

## 📊 Visual Diagram
```
 Production traces ──► human review ──► Golden dataset (versioned)
        ▲                                   │
        │                        ┌──────────┴──────────┐
        │                        ▼                     ▼
   user feedback             DEV set (tune)      TEST set (report only)
        ▲                        │                     │
        │                  many small metrics    judge calibrated w/ humans
        │                        └──────────┬──────────┘
        └────────── ship / canary ◄─────────┘ trend dashboard
```

---

## 💰 Cost Impact
- Deterministic metrics cost nothing in tokens. An LLM judge on 300 cases with 1,500 tokens each is 450K tokens, about $0.07-$0.30 on a small model per run; on a frontier model it can be 10-30x more.
- Optimise: rules first, judge only on cases that pass the rules; short rubric prompts; binary outputs with `max_tokens=5`; cache judge verdicts by (answer hash, rubric version); sample instead of judging everything nightly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Held-out set | Data never used for tuning | जिस data पर tuning नहीं हुई |
| Stratified sampling | Sample proportionally per group | हर group से अनुपात में sample |
| Cohen's kappa | Agreement adjusted for chance | Chance हटाकर agreement का माप |
| Overfitting to eval | Score up, real quality not | Eval पर score बढ़ा, असली quality नहीं |
| Data flywheel | Production failures feed dataset | Production गलतियाँ dataset में वापस |
| Rubric | Written scoring criteria | Scoring के लिखित नियम |

---

## ⚡ 3-Line Summary
English: Good evals use a representative, versioned golden dataset, a held-out test set, several focused metrics and a judge calibrated against humans. Prefer deterministic checks and watch for overfitting and judge bias. Feed production failures back into the dataset so evals stay current.
Hindi: अच्छे evals में representative और versioned golden dataset, held-out test set, कई focused metrics और human से calibrate किया हुआ judge होता है। Deterministic checks को प्राथमिकता दो और overfitting व judge bias पर नज़र रखो। Production failures को dataset में वापस डालो ताकि evals ताज़ा रहें।

---

## ➡️ Next Topic
**417. LangSmith — What + Why** — the tool that stores traces, datasets and experiments so these practices become easy.
