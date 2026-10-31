---

# 414. End-to-End Evaluation
# हिंदी में: End-to-End Evaluation (पूरे pipeline का मूल्यांकन)

---

## 🔵 Simple Definition (English)
End-to-end (E2E) evaluation tests the whole AI system as a user sees it: question goes in, final answer comes out. You do not score retriever, prompt or LLM separately — you score the final result against a golden answer. It tells you "does the product work?", not "which part is broken?".

## 🔵 सरल परिभाषा (Hindi)
End-to-end (E2E) evaluation पूरे AI system को वैसे test करता है जैसे user देखता है: सवाल अंदर, final जवाब बाहर। Retriever, prompt या LLM को अलग-अलग score नहीं करते — सिर्फ़ final result को golden answer से compare करते हैं। यह बताता है "product काम कर रहा है या नहीं", यह नहीं कि "कौन सा हिस्सा टूटा है"।

---

## 🔴 Problem it Solves
- Component metrics (retrieval recall, faithfulness) can all be green while the final answer is still wrong, because errors compound across steps (retriever -> reranker -> LLM -> parser).
- Unit-testing each part misses integration bugs: wrong JSON schema between steps, truncated context, bad prompt template variables.
- Business owners care about one number: "how many answers are correct for real users?"

## 🔴 यह क्यों बना? (Hindi)
- Component metrics सब green हो सकते हैं फिर भी final answer गलत हो सकता है, क्योंकि errors हर step में जुड़ती जाती हैं।
- हर हिस्से का अलग test integration bugs miss कर देता है: steps के बीच गलत JSON, context truncate होना, prompt template की गलती।
- Business को एक ही number चाहिए: "real users के लिए कितने answers सही हैं?"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a golden dataset: (input, expected_output) pairs from real traffic
Step 2 → Run the FULL pipeline (same code as production) on every input
Step 3 → Capture final output + latency + token usage per case
Step 4 → Score each output: exact match / rule check / LLM-as-judge
Step 5 → Aggregate: accuracy, p95 latency, avg cost per query
Step 6 → Compare with last release (regression check) and a pass threshold
Step 7 → If a case fails, drill down with component evals + traces
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Golden dataset बनाओ: real traffic से (input, expected_output) जोड़े
Step 2 → हर input पर पूरा pipeline चलाओ (production वाला same code)
Step 3 → हर case का final output + latency + token usage save करो
Step 4 → हर output को score करो: exact match / rule check / LLM-as-judge
Step 5 → Aggregate करो: accuracy, p95 latency, औसत cost
Step 6 → पिछले release से compare करो और pass threshold देखो
Step 7 → Case fail हो तो component eval और trace से कारण खोजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "HS code for a lithium-ion power bank?". Pipeline = query rewrite -> retrieve tariff notes -> LLM classify -> validate 8-digit code format. The E2E golden set has 200 products with the customs-approved HS code. Score = exact match on the 6-digit heading plus a check that the code exists in the tariff table. Result: "84% correct, p95 3.1s, $0.004/query". Even if retrieval recall was 95%, E2E showed 84% because the parser sometimes dropped leading zeros.

**Zomato AI**: "Suggest a veg dinner under 300 rupees" is judged end to end: are the returned dishes veg, under 300, and open now?

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "Power bank का HS code?"। Pipeline = query rewrite -> tariff notes retrieve -> LLM classify -> 8-digit code format validate। Golden set में 200 products हैं जिनका customs-approved HS code पता है। Score = 6-digit heading का exact match + code tariff table में मौजूद है या नहीं। Retrieval recall 95% था, लेकिन E2E में 84% आया क्योंकि parser कभी-कभी leading zero हटा देता था।

**Zomato AI**: "300 रुपये में veg dinner" को end to end जाँचते हैं: dishes veg हैं, 300 से कम हैं, और अभी खुले हैं?

---

## 💻 Code Example — Basic
```python
# Basic E2E evaluation with a fake pipeline (pure Python, runs offline)
from typing import Callable                                   # type for the pipeline function

def fake_pipeline(question: str) -> str:                      # stands in for the real RAG pipeline
    table = {"power bank": "8507.60", "laptop": "8471.30"}    # tiny knowledge base
    for key, code in table.items():                           # look for a known product
        if key in question.lower():                           # simple keyword match
            return code                                       # return the HS code
    return "UNKNOWN"                                          # fallback answer

GOLDEN: list[dict[str, str]] = [                              # golden dataset: input + expected
    {"q": "HS code for a power bank?", "expected": "8507.60"},
    {"q": "HS code for a laptop?", "expected": "8471.30"},
    {"q": "HS code for a banana?", "expected": "0803.90"},    # pipeline will fail this one
]

def run_e2e(pipeline: Callable[[str], str], golden: list[dict[str, str]]) -> dict[str, float]:
    passed = 0                                                # count of correct answers
    for case in golden:                                       # loop over all cases
        got = pipeline(case["q"])                             # run FULL pipeline
        ok = got == case["expected"]                          # exact-match score
        passed += int(ok)                                     # add 1 if correct
        print(f"{'PASS' if ok else 'FAIL'} | {case['q']} -> {got}")  # show result
    return {"accuracy": passed / len(golden)}                 # final metric

print(run_e2e(fake_pipeline, GOLDEN))                         # {'accuracy': 0.666...}
```

## 💻 Code Example — Advanced
```python
# Production-style E2E evaluator: async, concurrency limit, error handling, cost + latency
import asyncio                                                # async runtime
import time                                                   # latency measurement
import statistics                                             # p95 calculation helper
from dataclasses import dataclass, field                      # light result container
from typing import Awaitable, Callable                        # types for pipeline

@dataclass
class CaseResult:                                             # result of one test case
    question: str                                             # input
    expected: str                                             # golden answer
    actual: str = ""                                          # pipeline output
    passed: bool = False                                      # score
    latency_s: float = 0.0                                    # seconds taken
    tokens: int = 0                                           # total tokens used
    error: str | None = None                                  # error text if pipeline crashed

@dataclass
class Report:                                                 # aggregated report
    results: list[CaseResult] = field(default_factory=list)   # all case results

    @property
    def accuracy(self) -> float:                              # fraction correct
        return sum(r.passed for r in self.results) / max(len(self.results), 1)

    @property
    def p95_latency(self) -> float:                           # 95th percentile latency
        lat = sorted(r.latency_s for r in self.results)       # sort latencies
        return lat[int(0.95 * (len(lat) - 1))] if lat else 0.0

    @property
    def total_tokens(self) -> int:                            # token usage for cost estimate
        return sum(r.tokens for r in self.results)

Pipeline = Callable[[str], Awaitable[tuple[str, int]]]        # returns (answer, tokens_used)

async def eval_case(pipe: Pipeline, q: str, exp: str, sem: asyncio.Semaphore) -> CaseResult:
    res = CaseResult(question=q, expected=exp)                # start a result object
    async with sem:                                           # limit concurrent calls (rate limits)
        start = time.perf_counter()                           # start timer
        try:
            ans, tok = await asyncio.wait_for(pipe(q), timeout=30)  # run with a timeout
            res.actual, res.tokens = ans, tok                 # store output and tokens
            res.passed = ans.strip() == exp.strip()           # exact match scoring
        except Exception as exc:                              # a crash is a FAILED case, not a stop
            res.error = f"{type(exc).__name__}: {exc}"        # keep error for debugging
        res.latency_s = time.perf_counter() - start           # stop timer
    return res                                                # return the result

async def run_suite(pipe: Pipeline, golden: list[dict[str, str]], concurrency: int = 5) -> Report:
    sem = asyncio.Semaphore(concurrency)                      # shared limiter
    tasks = [eval_case(pipe, g["q"], g["expected"], sem) for g in golden]  # one task per case
    return Report(results=await asyncio.gather(*tasks))       # run all and build report

async def demo_pipeline(q: str) -> tuple[str, int]:           # mock pipeline, no API key needed
    await asyncio.sleep(0.01)                                 # fake network delay
    if "banana" in q:                                         # simulate a crash
        raise ValueError("no tariff note found")
    return ("8507.60" if "power bank" in q else "8471.30"), 420  # fake answer and tokens

if __name__ == "__main__":
    golden = [{"q": "power bank hs?", "expected": "8507.60"},
              {"q": "laptop hs?", "expected": "8471.30"},
              {"q": "banana hs?", "expected": "0803.90"}]
    rep = asyncio.run(run_suite(demo_pipeline, golden))       # run the async suite
    print(f"accuracy={rep.accuracy:.2f} p95={rep.p95_latency:.3f}s tokens={rep.total_tokens}")
    assert rep.accuracy >= 0.5, "E2E quality gate failed"     # gate used later in CI
```

---

## 🟠 FastAPI Integration
Expose the evaluator as an internal admin route so a dashboard or a CI job can trigger an E2E run and read the report. The production route and the eval use the same pipeline function, so there is no drift.

```python
from fastapi import FastAPI, HTTPException                    # web framework
from pydantic import BaseModel                                # request/response validation

app = FastAPI()                                               # app instance

class EvalRequest(BaseModel):                                 # request body
    min_accuracy: float = 0.8                                 # quality gate

@app.post("/internal/eval/e2e")                               # admin-only route
async def run_e2e_eval(req: EvalRequest) -> dict[str, float | bool]:
    golden = [{"q": "power bank hs?", "expected": "8507.60"}] # load from DB/file in real life
    try:
        report = await run_suite(demo_pipeline, golden)       # reuse the runner above
    except Exception as exc:                                  # never leak stack traces
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"accuracy": report.accuracy,                      # return metrics
            "p95_latency_s": report.p95_latency,
            "passed_gate": report.accuracy >= req.min_accuracy}
```

---

## 🔗 LangChain / LangGraph Connection
A LangChain LCEL chain or compiled LangGraph app is just a callable, so E2E eval = `chain.ainvoke` over the dataset. `chain.abatch(inputs, config={"max_concurrency": 5})` gives you the concurrency control for free. In LangSmith, `evaluate(target_fn, data=dataset, evaluators=[...])` does the same with tracing.

```python
from langchain_core.runnables import RunnableLambda           # wrap any function as a Runnable

chain = RunnableLambda(lambda q: "8507.60" if "power" in q else "UNKNOWN")  # stand-in chain
questions = ["power bank?", "banana?"]                        # eval inputs
answers = chain.batch(questions, config={"max_concurrency": 2})  # run the whole chain on all
print(answers)                                                # ['8507.60', 'UNKNOWN']
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Evaluating a different pipeline than production (mock retriever, different prompt).
✅ Correct: import the exact production function.

```python
# Wrong: test-only copy of the pipeline drifts away from production
def test_pipeline(q): return old_prompt_chain(q)
# Right: same entrypoint as the API route
async def test_pipeline(q): return await production_pipeline(q)
```

❌ Mistake 2: Letting one crash stop the whole eval, or counting a crash as "skipped".
✅ Correct: catch the exception, mark the case failed, keep the error text.

```python
# Wrong
results = [await pipe(q) for q in questions]                  # first exception kills everything
# Right
results = await asyncio.gather(*(safe_eval(q) for q in questions))  # safe_eval catches errors
```

---

## 🧠 Tricky Interview Question
**Q**: "Your RAG metrics (context precision 0.92, faithfulness 0.95) are excellent, but users say answers are wrong. What do you do?"

**Answer**: Component metrics can hide failures between components and measure the wrong thing (faithful to the wrong document is still wrong). Run E2E eval against a golden set built from real user questions with human-verified answers. Then compare E2E failures with component scores to find the gap: often it is query rewriting, outdated documents, parser bugs or a golden set that does not match real traffic. Fix, then keep both layers: component evals to diagnose, E2E eval as the release gate.

---

## ⚫ Interview Questions + Answers

Q1: What is end-to-end evaluation? (Easy)
A1: Scoring the full system output for a real input against an expected answer, treating the pipeline as a black box.

Q2: Name one advantage and one disadvantage of E2E eval. (Easy)
A2: Advantage: matches user experience, catches integration bugs. Disadvantage: does not tell which component failed, and it is slower and costlier because every case calls the LLM.

Q3: How do you build a good golden dataset? (Medium)
A3: Sample real production queries, cover each intent and edge case (typos, Hindi/English mixing, ambiguous items), get domain experts to label the answers, version the dataset, and keep a held-out part to avoid overfitting prompts to it.

Q4: How do you score free-text answers where exact match fails? (Medium)
A4: Use layered scoring: rules first (format, required fields), then embedding similarity, then LLM-as-judge with a rubric and a fixed judge model at temperature 0. Calibrate the judge against 50-100 human labels.

Q5: Your E2E eval takes 40 minutes and costs a lot. How do you make it CI-friendly? (Hard)
A5: Split into tiers: a 30-case smoke set on every PR (under 3 minutes, small model), the full set nightly or before release. Run cases concurrently with a semaphore, cache LLM outputs for unchanged inputs, use `temperature=0`, and track statistical noise (run flaky cases 3 times, use majority). Gate on a threshold plus "no regression versus main by more than 2 points".

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every release or prompt/model change
- Comparing two full architectures (RAG v1 vs v2)
- Measuring real business accuracy and latency

❌ Avoid when:
- You need to know exactly which component broke (use component evals)
- Very early prototyping with no golden data yet (use manual spot checks first)

---

## 📊 Visual Diagram
```
 Golden set ──► [ Query rewrite ─► Retriever ─► LLM ─► Parser ] ──► Final answer
 (input,exp)         \________ treated as ONE black box ________/          │
                                                                           ▼
                                                              Scorer (exact / rule / judge)
                                                                           │
                                                      accuracy, p95 latency, cost/query
                                                                           │
                                                          ≥ threshold ? ── ship : block
```

---

## 💰 Cost Impact
- Cost per run = cases x tokens per case x price. 200 cases x 2,500 tokens = 500K tokens; on gpt-4o-mini (about $0.15 input / $0.60 output per 1M) that is roughly $0.10-$0.20. An LLM judge adds about the same again.
- Optimise: small smoke set per PR, full set nightly; cache outputs; use a cheap judge model with a short rubric; cap `max_tokens`; stratified sampling instead of running everything every time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| End-to-end eval | Score final output of whole system | पूरे system के final output की जाँच |
| Golden dataset | Verified input/expected pairs | सही जवाबों वाला reference dataset |
| Regression | New release is worse than old | नए version में quality गिरना |
| Quality gate | Threshold to allow release | Release की न्यूनतम शर्त |
| LLM-as-judge | LLM scores another LLM's answer | LLM से answer की जाँच |
| p95 latency | 95% requests are faster than this | 95% requests इससे तेज़ |

---

## ⚡ 3-Line Summary
English: E2E evaluation runs the full production pipeline on a golden dataset and scores the final answers. It catches integration bugs that component metrics miss, but needs component evals and traces to find the root cause. Use tiers (smoke per PR, full nightly) to control cost and time.
Hindi: E2E evaluation golden dataset पर पूरा production pipeline चलाकर final answers को score करता है। यह वे integration bugs पकड़ता है जो component metrics miss करते हैं, पर कारण खोजने के लिए component evals और traces चाहिए। Cost और समय कम रखने के लिए smoke (हर PR) और full (रात में) tiers बनाओ।

---

## ➡️ Next Topic
**415. Evaluation in CI/CD Pipeline** — turn this E2E suite into an automatic quality gate on every pull request.
