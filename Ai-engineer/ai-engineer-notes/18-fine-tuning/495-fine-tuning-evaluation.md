---

# 495. Fine Tuning Evaluation
# हिंदी में: Fine Tuning का Evaluation

---

## 🔵 Simple Definition (English)
Fine tuning evaluation checks whether the tuned model is truly better than the baseline on data it never saw. You compare metrics (accuracy, F1, format-valid rate, judged quality, cost, latency) on a held-out test set.

## 🔵 सरल परिभाषा (Hindi)
Fine tuning evaluation यह जाँचता है कि tuned model उस data पर baseline से सच में बेहतर है जो उसने कभी नहीं देखा। आप held-out test set पर metrics (accuracy, F1, format-valid rate, judged quality, cost, latency) की तुलना करते हैं।

---

## 🔴 Problem it Solves
Training loss going down does not mean the model is useful. Without evaluation you may ship a model that is overfit, forgot general skills, or is no better than a good prompt.

## 🔴 यह क्यों बना? (Hindi)
Training loss घटने का मतलब यह नहीं कि model उपयोगी है। Evaluation के बिना आप ऐसा model ship कर सकते हैं जो overfit है, general skills भूल गया है या अच्छे prompt से बेहतर नहीं है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Hold out a test set before training (never train on it)
Step 2 → Run baseline (base model + best prompt) on the test set
Step 3 → Run the tuned model on the same test set
Step 4 → Compute metrics: accuracy / F1 per class, valid-JSON rate
Step 5 → For open-ended output use LLM-as-judge or human review
Step 6 → Check regressions on general tasks (forgetting) and safety
Step 7 → Compare cost and latency; decide ship / iterate / stop
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Training से पहले test set अलग रखो (उस पर कभी train नहीं)
Step 2 → Test set पर baseline (base model + सबसे अच्छा prompt) चलाओ
Step 3 → उसी test set पर tuned model चलाओ
Step 4 → Metrics निकालो: accuracy / class-wise F1, valid-JSON rate
Step 5 → Open-ended output के लिए LLM-as-judge या human review
Step 6 → General tasks पर regression (forgetting) और safety जाँचो
Step 7 → Cost और latency compare करो; ship / iterate / stop तय करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Test set: 1,000 products never used in training. Baseline (prompted large model): 82 percent chapter accuracy, 94 percent valid JSON. Tuned small model: 91 percent accuracy, 99.8 percent valid JSON, 5x cheaper. Per-class report shows chapter 85 lags; we add examples there. A regression set of 50 general questions confirms no big drop in general ability.

**Zomato-style**: Review tags: report precision and recall per tag, because "price" complaints are rare but important.

## 🟡 Real Example Hindi mein
**Tariff System**: Test set: 1,000 products जो training में कभी नहीं थे। Baseline (prompted बड़ा model): 82 percent chapter accuracy, 94 percent valid JSON। Tuned छोटा model: 91 percent accuracy, 99.8 percent valid JSON, 5 गुना सस्ता। Per-class report में chapter 85 पीछे है; वहाँ examples जोड़ते हैं। 50 general सवालों का regression set पुष्टि करता है कि general ability में बड़ी गिरावट नहीं है।

**Zomato-style**: Review tags में हर tag का precision और recall देखो, क्योंकि "price" शिकायतें कम पर ज़रूरी हैं।

---

## 💻 Code Example — Basic
```python
# Basic: accuracy, valid-JSON rate and per-class recall (pure Python, offline)
import json  # check valid JSON
from collections import Counter  # count per class
from typing import List, Tuple  # type hints

# (model output, true label)
results: List[Tuple[str, str]] = [
    ('{"hs": "8518"}', "8518"), ('{"hs": "6109"}', "6109"),
    ('{"hs": "8471"}', "8518"), ("not json", "6109"),
]


def parse(out: str) -> str:
    """Return predicted label or empty string if output is invalid."""
    try:
        return str(json.loads(out)["hs"])  # read the hs field
    except (json.JSONDecodeError, KeyError, TypeError):  # bad format
        return ""


preds = [parse(o) for o, _ in results]  # predictions
truth = [t for _, t in results]  # labels
valid = sum(1 for p in preds if p) / len(results)  # valid output rate
acc = sum(p == t for p, t in zip(preds, truth)) / len(results)  # accuracy
hits, total = Counter(), Counter()  # per class counters
for p, t in zip(preds, truth):
    total[t] += 1  # support
    hits[t] += int(p == t)  # correct count
print(f"valid={valid:.0%} accuracy={acc:.0%}")  # overall
print({k: f"{hits[k]}/{total[k]}" for k in total})  # per class recall
```

## 💻 Code Example — Advanced
```python
# Production style: async A/B evaluation of baseline vs tuned model with bootstrap confidence
import asyncio  # async
import random  # bootstrap sampling
from typing import Awaitable, Callable, List, Tuple  # types

Model = Callable[[str], Awaitable[str]]  # async model: input -> output
Case = Tuple[str, str]  # (input, expected label)


async def accuracy(model: Model, cases: List[Case], concurrency: int = 8) -> List[int]:
    """Return a list of 1/0 correctness flags, running calls with bounded concurrency."""
    sem = asyncio.Semaphore(concurrency)  # respect rate limits

    async def one(x: str, y: str) -> int:
        async with sem:
            try:
                out = await model(x)  # call model
            except Exception:  # count failures as wrong
                return 0
            return int(y in out)  # simple containment check

    return await asyncio.gather(*(one(x, y) for x, y in cases))


def bootstrap_ci(flags: List[int], n: int = 1000, seed: int = 0) -> Tuple[float, float]:
    """95 percent bootstrap confidence interval for mean accuracy."""
    rng = random.Random(seed)  # reproducible
    means = sorted(sum(rng.choices(flags, k=len(flags))) / len(flags) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


async def base(x: str) -> str:
    return "8518" if "head" in x else "0000"  # stub baseline


async def tuned(x: str) -> str:
    return "8518" if "head" in x or "ear" in x else "6109"  # stub tuned


async def main() -> None:
    cases = [("headphones", "8518"), ("earphones", "8518"), ("shirt", "6109")] * 20
    for name, m in (("baseline", base), ("tuned", tuned)):
        flags = await accuracy(m, cases)  # run
        lo, hi = bootstrap_ci(flags)  # uncertainty
        print(name, round(sum(flags) / len(flags), 3), (round(lo, 3), round(hi, 3)))


if __name__ == "__main__":
    asyncio.run(main())  # demo with stubs
```

---

## 🟠 FastAPI Integration
Expose an evaluation endpoint, or run evaluation in CI and block deployment when metrics regress.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema
from typing import List  # types

app = FastAPI()  # app


class EvalInput(BaseModel):
    predictions: List[str]  # model predictions
    labels: List[str]  # ground truth


@app.post("/eval/accuracy")
async def eval_accuracy(body: EvalInput) -> dict:
    """Compute accuracy and gate deployment on a threshold."""
    n = len(body.labels)  # sample count
    if n == 0 or n != len(body.predictions):  # validate
        return {"error": "predictions and labels must be equal non-empty lists"}
    acc = sum(p == t for p, t in zip(body.predictions, body.labels)) / n  # accuracy
    return {"accuracy": acc, "n": n, "deploy_ok": acc >= 0.90}  # threshold gate
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith runs evaluators over datasets and compares experiments side by side. OpenAI Evals and similar tools provide graders too. In LangGraph you can add an evaluation node that blocks a release branch.

```python
# Illustrative LangSmith evaluator (needs LANGSMITH_API_KEY and a dataset)
# def exact_match(run, example) -> dict:
#     return {"key": "exact", "score": run.outputs["hs"] == example.outputs["hs"]}
# client.evaluate(tuned_chain.invoke, data="tariff-test", evaluators=[exact_match])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating on training data
✅ Correct: Use a held-out test set.

```python
# Wrong: score = evaluate(model, train_rows)   # inflated
# Right: score = evaluate(model, test_rows)    # unseen data
```

❌ Mistake 2: Reporting only overall accuracy
✅ Correct: Report per-class metrics and confidence intervals.

```python
# Wrong: "91% accuracy!" (but rare class is at 30%)
# Right: per-class recall table + bootstrap CI + valid-output rate
```

---

## 🧠 Tricky Interview Question
**Q**: "Tuned model beats baseline by 2 points on 100 test examples. Do you ship?"

**Answer**: Not yet. With 100 examples, a 2 point difference is within noise (confidence interval is several points wide). Enlarge the test set, run a bootstrap or paired significance test, check per-class and failure types, and consider cost and latency. Ship only when improvement is statistically and practically meaningful.

---

## ⚫ Interview Questions + Answers

Q1: Why a separate test set? (Easy)
A1: To measure performance on unseen data; train data scores are inflated.

Q2: What baseline should you compare against? (Easy)
A2: The base model with the best prompt (and RAG if used), not a lazy prompt.

Q3: How do you evaluate free-text outputs? (Medium)
A3: Human review, rubric-based LLM-as-judge (validated against human labels), and task-specific checks like schema validity or key-fact presence.

Q4: What is a regression set? (Medium)
A4: A small set of general tasks and safety prompts to confirm tuning did not hurt unrelated abilities.

Q5: How to evaluate continuously in production? (Hard)
A5: Sample live traffic, log inputs/outputs, run automated checks and judges, collect user feedback, monitor drift in input distribution, and re-run the offline eval for each candidate model before rollout (canary and rollback).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before and after every tuning run
- Before changing base model versions

❌ Avoid when:
- Never skip; avoid relying on a single metric or a tiny test set

---

## 📊 Visual Diagram
```
            Same held-out test set
        ┌────────────┴────────────┐
        ▼                         ▼
  Baseline (prompt)         Tuned model
        │                         │
        └──► metrics ◄────────────┘
   accuracy | F1 | valid-JSON | cost | latency
                    │
                    ▼
        ship / iterate / stop
```

---

## 💰 Cost Impact
- Evaluation calls cost tokens: 1,000 cases x 2 models x ~200 tokens each is about 400K tokens (cheap compared with training).
- LLM-as-judge adds a third call per case; use a cheaper judge and sample.
- Optimise: cache baseline results, run evals in batch mode where offered, evaluate on a stratified sample first.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Held-out set | Data not used in training | Training में न इस्तेमाल हुआ data |
| Baseline | Reference to beat | तुलना का संदर्भ |
| F1 | Balance of precision and recall | Precision और recall का संतुलन |
| LLM-as-judge | LLM scores outputs | LLM से outputs की scoring |
| Regression set | Checks for lost abilities | खोई क्षमताओं की जाँच |
| Confidence interval | Range of likely true value | सही मान की संभावित range |

---

## ⚡ 3-Line Summary
English: Evaluate tuned models on a held-out test set against the best baseline.
Report per-class metrics, valid-output rate, cost and latency with uncertainty.
Add regression checks and keep evaluating in production.
Hindi: Tuned model को held-out test set पर सबसे अच्छे baseline से compare करो।
Per-class metrics, valid-output rate, cost और latency uncertainty के साथ बताओ।
Regression checks जोड़ो और production में भी evaluate करते रहो।

---

## ➡️ Next Topic
**496. LoRA — What + Why** — efficient fine tuning that trains small adapters instead of all weights.
