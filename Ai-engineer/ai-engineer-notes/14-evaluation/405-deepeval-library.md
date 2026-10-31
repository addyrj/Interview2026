---

# 405. DeepEval Library
# हिंदी में: DeepEval Library

---

## 🔵 Simple Definition (English)
DeepEval is an open-source Python framework that makes LLM testing feel like unit testing. You create `LLMTestCase` objects, pick metrics (faithfulness, answer relevancy, G-Eval, hallucination, etc.), and run them with `deepeval test run` inside pytest or CI, with pass/fail thresholds.

## 🔵 सरल परिभाषा (Hindi)
DeepEval एक open-source Python framework है जो LLM testing को unit testing जैसा बना देता है। आप `LLMTestCase` बनाते हैं, metrics चुनते हैं (faithfulness, answer relevancy, G-Eval, hallucination आदि) और pytest/CI में `deepeval test run` से threshold के साथ pass/fail पाते हैं।

---

## 🔴 Problem it Solves
Ad-hoc eval scripts have no standard structure, no thresholds and no CI integration. Developers already know pytest; DeepEval lets them add LLM quality tests that fail the build when quality drops, with reasons for every score.

## 🔴 यह क्यों बना? (Hindi)
Ad-hoc eval scripts में standard structure, thresholds और CI integration नहीं होता। Developers pytest जानते हैं; DeepEval से LLM quality tests जुड़ते हैं जो quality गिरने पर build fail करते हैं और हर score का कारण बताते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install deepeval; set judge key (OPENAI_API_KEY by default)
Step 2 → Build LLMTestCase(input, actual_output, expected_output, retrieval_context)
Step 3 → Choose metrics with thresholds (0..1)
Step 4 → metric.measure(test_case) -> metric.score, metric.reason, metric.is_successful()
Step 5 → Or assert_test(test_case, [metrics]) inside a pytest function
Step 6 → Run: deepeval test run test_rag.py
Step 7 → CI fails if any metric is below threshold
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install deepeval; judge key सेट करो (default OPENAI_API_KEY)
Step 2 → LLMTestCase(input, actual_output, expected_output, retrieval_context) बनाओ
Step 3 → Thresholds (0..1) के साथ metrics चुनो
Step 4 → metric.measure(test_case) -> metric.score, metric.reason, metric.is_successful()
Step 5 → या pytest function में assert_test(test_case, [metrics])
Step 6 → चलाओ: deepeval test run test_rag.py
Step 7 → कोई metric threshold से नीचे हो तो CI fail
```

---

## 🟡 Real World Example
**Tariff Classification System**: A `test_tariff.py` with 30 test cases. Metrics: `FaithfulnessMetric(threshold=0.8)` (answer supported by retrieved tariff text), `AnswerRelevancyMetric(0.7)`, and a `GEval` "HS code format" metric. GitHub Actions runs `deepeval test run` on each PR; a failing case prints the judge's reason ("Claim 'duty is 5%' not found in context").

**Zomato-style**: Tests that the bot never recommends a closed restaurant, using GEval with a strict criterion.

## 🟡 Real Example Hindi mein
**Tariff System**: `test_tariff.py` में 30 test cases। Metrics: `FaithfulnessMetric(threshold=0.8)` (answer retrieved tariff text से supported), `AnswerRelevancyMetric(0.7)`, और "HS code format" का `GEval`। GitHub Actions हर PR पर `deepeval test run` चलाता है; fail होने पर judge का reason दिखता है ("'duty 5% है' claim context में नहीं मिला")।

**Zomato-style**: Tests कि bot कभी बंद restaurant recommend न करे, कड़े GEval criterion से।

---

## 💻 Code Example — Basic
```python
# Basic: DeepEval-style test structure in pure Python (offline stand-in, same shape)
from dataclasses import dataclass, field  # light data containers


@dataclass
class TestCase:  # mirrors LLMTestCase fields
    input: str  # question
    actual_output: str  # answer from our system
    retrieval_context: list[str] = field(default_factory=list)  # retrieved chunks


def keyword_faithfulness(tc: TestCase) -> float:
    """Toy metric: fraction of answer words found in context (NOT a real judge)."""
    words = [w.strip(".,").lower() for w in tc.actual_output.split()]  # answer words
    ctx = " ".join(tc.retrieval_context).lower()  # context text
    if not words:  # empty answer guard
        return 0.0  # nothing supported
    return sum(w in ctx for w in words) / len(words)  # supported ratio


def assert_metric(tc: TestCase, threshold: float = 0.6) -> None:  # like assert_test
    score = keyword_faithfulness(tc)  # compute score
    assert score >= threshold, f"score {score:.2f} < {threshold}"  # fail test if low


tc = TestCase("HS code?", "Code is 8507.60", ["8507.60 covers lithium-ion accumulators"])  # sample
assert_metric(tc)  # passes silently when OK
print("passed")  # confirm
```

## 💻 Code Example — Advanced
```python
# Advanced: real DeepEval tests (pytest) + async measurement + custom G-Eval
# pip install deepeval pytest   |   run: deepeval test run test_tariff.py
import asyncio  # async measure
import pytest  # test framework

from deepeval import assert_test  # pytest-style assertion
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval  # metrics
from deepeval.test_case import LLMTestCase, LLMTestCaseParams  # test objects

JUDGE = "gpt-4o-mini"  # cheap judge model name

CASES: list[dict] = [  # dataset of cases (normally loaded from JSONL)
    {"q": "HS code for lithium-ion batteries?",
     "a": "8507.60 - lithium-ion accumulators.",
     "ctx": ["Heading 8507.60 covers lithium-ion accumulators."],
     "exp": "8507.60"},
]


def make_case(c: dict) -> LLMTestCase:  # convert dict -> LLMTestCase
    return LLMTestCase(input=c["q"], actual_output=c["a"],
                       expected_output=c["exp"], retrieval_context=c["ctx"])  # all fields


def metrics() -> list:  # build fresh metric objects
    return [
        FaithfulnessMetric(threshold=0.8, model=JUDGE, include_reason=True),  # grounded?
        AnswerRelevancyMetric(threshold=0.7, model=JUDGE),  # on-topic?
        GEval(name="HS format", criteria="Answer must contain an HS code like 1234.56.",
              evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT], threshold=0.7, model=JUDGE),
    ]


@pytest.mark.parametrize("case", CASES)  # one test per case
def test_tariff(case: dict) -> None:
    assert_test(make_case(case), metrics())  # raises AssertionError with reasons


async def measure_all(cases: list[dict]) -> list[dict]:
    """Programmatic async run for dashboards (not via pytest)."""
    results: list[dict] = []  # collected output
    sem = asyncio.Semaphore(5)  # limit concurrency

    async def one(c: dict) -> None:  # measure one case
        async with sem:  # respect limit
            tc = make_case(c)  # build test case
            for m in metrics():  # each metric
                try:
                    await m.a_measure(tc)  # async judge call
                    results.append({"q": c["q"], "metric": m.__class__.__name__,
                                    "score": m.score, "ok": m.is_successful(),
                                    "reason": getattr(m, "reason", None)})  # record
                except Exception as exc:  # judge/API failure
                    results.append({"q": c["q"], "metric": m.__class__.__name__,
                                    "error": str(exc)})  # keep going
    await asyncio.gather(*(one(c) for c in cases))  # run all
    return results  # list of dicts
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class CaseIn(BaseModel):  # request item
    q: str  # question
    a: str  # answer
    ctx: list[str]  # retrieved contexts
    exp: str = ""  # expected output


@app.post("/eval/deepeval")  # endpoint
async def run_deepeval(cases: list[CaseIn]) -> dict:
    if not cases or len(cases) > 50:  # input guard
        raise HTTPException(400, "send 1-50 cases")  # bad request
    out = await measure_all([c.model_dump() for c in cases])  # reuse async runner
    failed = [r for r in out if r.get("ok") is False or "error" in r]  # failures
    return {"total": len(out), "failed": len(failed), "results": out}  # summary + detail
```

---

## 🔗 LangChain / LangGraph Connection
DeepEval has integrations (callback handlers) for LangChain and LangGraph so traces can be scored, and you can also just call your chain inside a test and wrap the result in `LLMTestCase`.

```python
def build_case(chain, retriever, question: str, expected: str) -> LLMTestCase:
    docs = retriever.invoke(question)  # LCEL retriever call
    answer = chain.invoke({"question": question, "context": docs})  # LCEL chain call
    return LLMTestCase(input=question, actual_output=answer, expected_output=expected,
                       retrieval_context=[d.page_content for d in docs])  # ready for assert_test
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `retrieval_context` for RAG metrics
✅ Correct: Faithfulness needs it

```python
# Wrong - Faithfulness cannot run
LLMTestCase(input=q, actual_output=a)
# Right
LLMTestCase(input=q, actual_output=a, retrieval_context=ctx)
```

❌ Mistake 2: Using `retrieval_context` where `context` is meant (ground-truth docs vs what the retriever returned)
✅ Correct: `retrieval_context` = retrieved at runtime; `context` = ideal context.

❌ Mistake 3: Thresholds so low that nothing ever fails.
✅ Correct: tune thresholds from a baseline run, then tighten.

---

## 🧠 Tricky Interview Question
**Q**: "Your DeepEval suite passes locally but is flaky in CI (random failures). Why and what to do?"

**Answer**: LLM-judged metrics are non-deterministic and rate limits cause timeouts. Pin judge model, use low concurrency, add retries, set thresholds with margin below baseline, and rerun failing cases once before failing the build. Separate fast deterministic tests from judge-based tests so the cheap suite always blocks merges and the expensive suite runs nightly.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is an `LLMTestCase`?
A1: A container for input, actual output, optional expected output and retrieval context that metrics evaluate.

Q2: [Easy] How do you run DeepEval tests?
A2: Write pytest-style tests with `assert_test` and run `deepeval test run file.py`.

Q3: [Medium] Name some built-in metrics.
A3: Faithfulness, AnswerRelevancy, ContextualPrecision/Recall/Relevancy, Hallucination, Bias, Toxicity, GEval.

Q4: [Medium] How can you use a non-OpenAI judge?
A4: Subclass `DeepEvalBaseLLM` (implement `generate`, `a_generate`, `get_model_name`) and pass it as `model`.

Q5: [Hard] How do you control cost in a 1,000-case suite?
A5: Tiered suites (smoke 30 cases on PRs, full nightly), cheap judge, caching results by case hash, async with concurrency limits, and skipping unchanged cases.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want LLM evals in CI like unit tests
- You need many ready-made metrics with reasons

❌ Avoid when:
- You only need a one-off notebook check
- You cannot send data to the judge provider and have no local judge

---

## 📊 Visual Diagram
```
 test_tariff.py
   │  LLMTestCase(input, output, context)
   ▼
 assert_test(case, [Faithfulness, Relevancy, GEval])
   │        judge LLM (reason + score each)
   ▼
 score ≥ threshold ? ── yes ─► PASS
                      └─ no ─► FAIL (reason printed) ─► CI red
```

---

## 💰 Cost Impact
Each metric makes about 2-4 judge calls per test case (claim extraction + verdicts), ~1-3K tokens each. 30 cases x 3 metrics on gpt-4o-mini ≈ 300-500K tokens ≈ $0.05-$0.08 per run; a gpt-4o judge is ~15x more.
Optimise: smoke subset on PRs, full run nightly, cache, `include_reason=False` where reasons are not needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LLMTestCase | One test example | एक test उदाहरण |
| Metric | Scorer with threshold | Threshold वाला scorer |
| assert_test | pytest-style check | pytest जैसी जाँच |
| retrieval_context | Chunks actually retrieved | असल में retrieve हुए chunks |
| Threshold | Pass cutoff | Pass की सीमा |

---

## ⚡ 3-Line Summary
English: DeepEval brings pytest-style testing to LLM apps with ready metrics and thresholds. Build LLMTestCases, run `deepeval test run`, and gate CI. Control flakiness and cost with pinned judge and tiered suites.
Hindi: DeepEval LLM apps में pytest-style testing लाता है, ready metrics और thresholds के साथ। LLMTestCases बनाओ, `deepeval test run` चलाओ और CI gate लगाओ। Pinned judge और tiered suites से flakiness और cost संभालो।

---

## ➡️ Next Topic
**406. TruLens Library** - another evaluation library, built around the "RAG triad" and tracing.
