---

# 071. Prompt Testing Strategy
# हिंदी में: Prompt Testing Strategy — Prompts को कैसे परखें

---

## 🔵 Simple Definition (English)
Prompt testing is running a prompt on a fixed set of example inputs with known expected results, then scoring the outputs. It tells you whether a change made things better or worse. Because LLMs are non-deterministic, tests use metrics and thresholds rather than exact "pass or fail" on one run.

## 🔵 सरल परिभाषा (Hindi)
Prompt testing में prompt को ऐसे example inputs पर चलाते हैं जिनके expected results पहले से पता हों, फिर outputs को score करते हैं। इससे पता चलता है कि बदलाव से हालत सुधरी या बिगड़ी। LLM non-deterministic है, इसलिए tests एक run के exact pass/fail की जगह metrics और thresholds इस्तेमाल करते हैं।

---

## 🔴 Problem it Solves
"It worked on my 3 examples" is not testing. A prompt tweak that fixes one case often breaks five others (regression). Without tests, teams ship on gut feeling, discover failures from users, and cannot compare models or prompt versions fairly.

## 🔴 यह क्यों बना? (Hindi)
"मेरे 3 examples पर चल गया" testing नहीं है। एक case ठीक करने वाला prompt tweak अक्सर पाँच और तोड़ देता है (regression)। Tests के बिना team अंदाज़े पर ship करती है, failures users से पता चलते हैं, और models या prompt versions की निष्पक्ष तुलना नहीं हो पाती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a golden dataset: real inputs + expected outputs (start with 50-200)
Step 2 → Include slices: easy, hard, edge cases, adversarial, other languages
Step 3 → Choose metrics: exact match, schema validity, field accuracy, LLM-as-judge
Step 4 → Run the prompt on every case (temperature 0, same model, concurrent)
Step 5 → Compute overall score and per-slice scores
Step 6 → Compare with the baseline version; fail CI if below threshold
Step 7 → Add every production failure to the dataset (the flywheel)
Step 8 → Re-run on every prompt, model or retrieval change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Golden dataset बनाओ: असली inputs + expected outputs (50-200 से शुरू)
Step 2 → Slices रखो: easy, hard, edge cases, adversarial, दूसरी भाषाएँ
Step 3 → Metrics चुनो: exact match, schema validity, field accuracy, LLM-as-judge
Step 4 → हर case पर prompt चलाओ (temperature 0, वही model, concurrent)
Step 5 → Overall और per-slice score निकालो
Step 6 → Baseline से तुलना; threshold से नीचे हो तो CI fail
Step 7 → हर production failure dataset में जोड़ो (flywheel)
Step 8 → हर prompt, model या retrieval बदलाव पर दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The golden set has 200 products with correct HS codes, tagged by slice: `electronics`, `accessories`, `ambiguous`, `hindi-names`. A pull request changes the prompt. CI runs all 200 cases and reports: overall 89% (baseline 86%), accessories 85% (baseline 70%), hindi-names 78% (baseline 80%). The slice report shows a small regression that the overall score would hide.

**Zomato-style**: Intent classification tests with misspelt and Hinglish messages.

## 🟡 Real Example Hindi mein
**Tariff System**: Golden set में 200 products और सही HS codes हैं, slice tags के साथ: `electronics`, `accessories`, `ambiguous`, `hindi-names`। Pull request prompt बदलता है। CI सभी 200 cases चलाता है: overall 89% (baseline 86%), accessories 85% (baseline 70%), hindi-names 78% (baseline 80%)। Slice report छोटी regression दिखाता है जो overall score छुपा देता।

**Zomato-style**: गलत spelling और Hinglish messages के साथ intent classification tests।

---

## 💻 Code Example — Basic
```python
# Basic: tiny eval harness with a fake LLM (offline)
from dataclasses import dataclass  # test case container

@dataclass(frozen=True)
class Case:
    product: str     # input
    expected: str    # correct HS code
    slice: str       # group name for per-slice scores

CASES = [
    Case("wireless earbuds", "8518.30", "electronics"),
    Case("phone case", "3926.90", "accessories"),
    Case("usb charger", "8504.40", "accessories"),
]

def fake_llm(product: str) -> str:
    # Pretend model that is wrong on chargers
    table = {"wireless earbuds": "8518.30", "phone case": "3926.90", "usb charger": "8517.13"}
    return table[product]

def evaluate(cases: list[Case]) -> dict[str, float]:
    totals: dict[str, list[int]] = {}                      # slice -> list of 1/0 results
    for c in cases:
        ok = int(fake_llm(c.product) == c.expected)        # 1 if correct
        totals.setdefault(c.slice, []).append(ok)          # group by slice
        totals.setdefault("overall", []).append(ok)        # also overall
    return {k: sum(v) / len(v) for k, v in totals.items()} # accuracy per group

report = evaluate(CASES)
print(report)                                              # overall 0.67, accessories 0.5, ...
assert report["overall"] >= 0.6, "quality gate failed"     # simple gate
```

## 💻 Code Example — Advanced
```python
# Production: async eval runner, repeated runs for variance, LLM-as-judge hook, regression gate
from __future__ import annotations

import asyncio                                    # concurrency
import statistics                                 # mean / stdev
from collections import defaultdict               # grouping
from dataclasses import dataclass                 # records
from typing import Awaitable, Callable            # type hints

LLM = Callable[[str], Awaitable[str]]             # prompt -> reply
Judge = Callable[[str, str, str], Awaitable[bool]]   # (input, expected, got) -> pass?

@dataclass(frozen=True)
class Case:
    product: str
    expected: str
    slice: str

async def run_case(llm: LLM, prompt: str, case: Case, judge: Judge | None, sem: asyncio.Semaphore) -> bool:
    async with sem:                                       # limit concurrent API calls
        try:
            got = (await llm(f"{prompt}\nProduct: {case.product}")).strip()   # model output
        except Exception:                                 # a failed call counts as a failed test
            return False
    if got == case.expected:                              # exact match passes
        return True
    return await judge(case.product, case.expected, got) if judge else False   # optional fuzzy judge

async def evaluate(llm: LLM, prompt: str, cases: list[Case], runs: int = 3,
                   judge: Judge | None = None, concurrency: int = 8) -> dict[str, tuple[float, float]]:
    sem = asyncio.Semaphore(concurrency)                  # rate-limit friendly
    per_slice: dict[str, list[float]] = defaultdict(list) # slice -> accuracy per run
    for _ in range(runs):                                 # repeat to measure noise
        results = await asyncio.gather(*(run_case(llm, prompt, c, judge, sem) for c in cases))
        groups: dict[str, list[bool]] = defaultdict(list)
        for c, ok in zip(cases, results):
            groups[c.slice].append(ok)                    # per-slice results
            groups["overall"].append(ok)                  # overall results
        for name, oks in groups.items():
            per_slice[name].append(sum(oks) / len(oks))   # accuracy for this run
    return {k: (statistics.mean(v), statistics.pstdev(v)) for k, v in per_slice.items()}

def gate(new: dict[str, tuple[float, float]], base: dict[str, tuple[float, float]],
         max_drop: float = 0.02) -> list[str]:
    """Return list of regressions larger than max_drop (plus noise)."""
    problems: list[str] = []
    for name, (mean, sd) in new.items():
        base_mean = base.get(name, (0.0, 0.0))[0]         # baseline accuracy
        if mean + sd < base_mean - max_drop:              # drop beyond noise
            problems.append(f"{name}: {mean:.2f} < baseline {base_mean:.2f}")
    return problems

async def _demo() -> None:
    cases = [Case("earbuds", "8518.30", "electronics"), Case("phone case", "3926.90", "accessories")]
    async def good(p: str) -> str:
        return "3926.90" if "case" in p else "8518.30"
    async def bad(p: str) -> str:
        return "8518.30"
    base = await evaluate(good, "v1", cases)
    new = await evaluate(bad, "v2", cases)
    print(gate(new, base))                                # accessories regression is reported

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: an eval costs cases x runs x (prompt + output tokens). 200 cases x 3 runs x 1,000 tokens = 600K tokens per evaluation. Use temperature 0, a cheaper model for dev runs, and cache results for unchanged cases.

---

## 🟠 FastAPI Integration
Test the API contract with `pytest` and FastAPI's `TestClient` (override the LLM dependency with a fake), and add an admin route or CI job that runs the golden set against the real model.

```python
from fastapi import Depends, FastAPI               # framework
from fastapi.testclient import TestClient          # test client (needs httpx)
from pydantic import BaseModel                     # models

app = FastAPI()                                    # app

class Q(BaseModel):
    product: str                                   # input

async def get_llm() -> LLM:                        # dependency that returns the LLM function
    async def real(p: str) -> str:
        raise RuntimeError("real LLM not configured in this example")
    return real

@app.post("/classify")
async def classify(q: Q, llm: LLM = Depends(get_llm)) -> dict[str, str]:
    return {"hs_code": (await llm(f"HS code for {q.product}")).strip()}

def test_classify_contract() -> None:
    async def fake(p: str) -> str:
        return "8518.30"
    app.dependency_overrides[get_llm] = lambda: fake       # inject fake LLM
    res = TestClient(app).post("/classify", json={"product": "earbuds"})
    assert res.status_code == 200 and res.json() == {"hs_code": "8518.30"}
    app.dependency_overrides.clear()                       # clean up
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith provides datasets, `evaluate()` runs and evaluators (including LLM-as-judge), and tracks results per prompt version. For LangGraph, unit-test each node with fake state, then run end-to-end graph tests on the golden set.

```python
from langsmith import evaluate        # pip install langsmith (needs LANGSMITH_API_KEY)

def exact_match(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["hs_code"] == reference_outputs["hs_code"]   # simple evaluator

# evaluate(target_fn, data="tariff-golden-set", evaluators=[exact_match], experiment_prefix="classify-v7")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Testing on 5 hand-picked examples
✅ Correct: Use a larger, sliced dataset from real traffic.
```python
# Wrong
cases = CASES[:5]

# Right
cases = load_golden("golden.jsonl")     # 100-200+, tagged by slice
```

❌ Mistake 2: Only looking at the overall score
✅ Correct: Report per slice and gate on critical slices.
```python
# Wrong
assert overall >= 0.85

# Right
assert overall >= 0.85 and report["accessories"] >= 0.80
```

❌ Mistake 3: Using the same data to tune and to judge (leakage). Keep a hidden holdout set.

---

## 🧠 Tricky Interview Question
**Q**: "Your eval score went from 88% to 90% after a prompt change. Do you ship?"

**Answer**: Not yet. Check: (1) noise: with 100 cases, a 2-point change is within sampling error; run multiple times and compute confidence intervals; (2) slices: did a critical slice regress; (3) leakage: were the prompt examples taken from the eval set; (4) cost and latency changes; (5) a canary in production. Ship only if the gain is statistically meaningful and no critical slice regresses.

---

## ⚫ Interview Questions + Answers

Q1: What is a golden dataset?
A1: A curated set of inputs with trusted expected outputs, used to measure prompt quality repeatedly.

Q2: Why are LLM tests different from normal unit tests?
A2: Outputs are non-deterministic and often free-form, so we use metrics, thresholds, repeated runs, and sometimes another LLM as a judge.

Q3: What is LLM-as-judge and its risks?
A3: Using an LLM to grade outputs against criteria. Risks: bias toward longer answers, self-preference, inconsistency. Mitigate with clear rubrics, temperature 0, calibration against human labels.

Q4: How do you reduce flakiness?
A4: Temperature 0, fixed model version, structured outputs, repeated runs with averages, and tolerance thresholds.

Q5 (Hard): Build a CI pipeline for prompt changes.
A5: On pull request: lint prompt files, run unit tests with fake LLMs, run the golden set on the real model with concurrency limits, compare per-slice scores with the baseline stored from main, enforce gates (no critical slice drop beyond noise, cost per request within budget, p95 latency), post a report to the PR, and require approval. After merge, canary release with live monitoring and feed failures back into the dataset.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompts or models change over time
- Several people edit prompts
- Errors are costly (compliance, money)

❌ Avoid heavy testing when:
- It is a quick prototype (use a small smoke test)
- No ground truth exists yet (start by labelling 30 examples first)

---

## 📊 Visual Diagram
```
 golden.jsonl (200 cases, tagged by slice)
        |
        v
  +-------------+     +-------------+
  | prompt v7   | --> |  LLM (temp0)| --> outputs
  +-------------+     +-------------+
                                |
                     metrics: exact / schema / judge
                                |
                                v
   overall 89%   electronics 93%   accessories 85%   hindi 78%
                                |
              compare with baseline (v6)
                   |                    |
               pass gate            fail -> block PR
```

---

## 💰 Cost Impact
- Each evaluation = cases x runs x tokens per case. Frequent runs add up.
- LLM-as-judge adds a second call per case.
- Good tests save money by catching expensive regressions (longer outputs, more retries) before release.

Optimisation: a small fast "smoke" set on every commit and the full set nightly or on PRs, a cheaper model for dev experiments, cache results by (prompt hash, case id), and judge only the cases that fail exact match.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden dataset | Trusted test cases | भरोसेमंद test cases |
| Regression | New change breaks old behaviour | नया बदलाव पुराना तोड़े |
| Slice | Subgroup of test cases | Test cases का उप-समूह |
| LLM-as-judge | LLM grades outputs | LLM से outputs की grading |
| Flaky test | Result changes between runs | हर run में अलग नतीजा |
| Holdout | Unseen data for final check | अंतिम जाँच का अनदेखा data |

---

## ⚡ 3-Line Summary
English: Prompt testing runs a prompt on a sliced golden dataset and compares scores with a baseline. Use metrics, repeated runs and gates, not gut feeling. Feed every production failure back into the dataset.
Hindi: Prompt testing sliced golden dataset पर prompt चलाकर scores की baseline से तुलना करती है। अंदाज़े की जगह metrics, repeated runs और gates इस्तेमाल करो। हर production failure को dataset में वापस जोड़ो।

---

## ➡️ Next Topic
**072. Prompt Injection Attack** — how attackers hide instructions in user input or documents to hijack your prompt.
