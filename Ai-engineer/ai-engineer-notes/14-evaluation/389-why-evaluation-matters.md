---

# 389. Why Evaluation Matters
# हिंदी में: Evaluation क्यों ज़रूरी है

---

## 🔵 Simple Definition (English)
Evaluation means measuring how good your AI system is using a fixed test set and clear scores. Instead of saying "it looks fine", you say "correct on 87 of 100 test questions". Without evaluation you cannot know if a prompt, model or retriever change made things better or worse.

## 🔵 सरल परिभाषा (Hindi)
Evaluation का मतलब है एक fixed test set और साफ scores से अपने AI system की quality नापना। "ठीक लग रहा है" कहने की जगह आप कहते हैं "100 में से 87 सवाल सही"। Evaluation के बिना पता नहीं चलता कि prompt, model या retriever बदलने से चीज़ें बेहतर हुईं या खराब।

---

## 🔴 Problem it Solves
LLM outputs are non-deterministic free text, so normal unit tests ("assert result == 5") do not work. Teams demo with 3 happy-path examples, ship, and then find hallucinated HS codes in production. Every change (new model version, chunk size, prompt tweak) can silently break something. Evaluation gives a repeatable score so you can compare versions, catch regressions and justify cost.

## 🔴 यह क्यों बना? (Hindi)
LLM के outputs non-deterministic free text होते हैं, इसलिए सामान्य unit tests ("assert result == 5") काम नहीं करते। Teams 3 आसान examples से demo करती हैं, ship कर देती हैं, और production में hallucinated HS codes मिलते हैं। हर बदलाव (नया model version, chunk size, prompt tweak) चुपचाप कुछ तोड़ सकता है। Evaluation एक repeatable score देता है ताकि versions compare हों, regressions पकड़े जाएँ और cost justify हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a golden dataset: questions + expected answers (+ source docs)
Step 2 → Run the system on every question and record outputs (answer, retrieved chunks)
Step 3 → Score each output with metrics (exact match, retrieval hit-rate, LLM judge...)
Step 4 → Aggregate: average score, per-category scores, failures list
Step 5 → Change something (prompt / model / chunking) and re-run the SAME dataset
Step 6 → Compare scores; ship only if quality is up or equal and cost/latency acceptable
Step 7 → Run in CI before deploy + sample real traffic in production (online eval)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Golden dataset बनाओ: सवाल + expected answer (+ source docs)
Step 2 → हर सवाल पर system चलाओ और outputs record करो (answer, retrieved chunks)
Step 3 → Metrics से score दो (exact match, retrieval hit-rate, LLM judge...)
Step 4 → Aggregate करो: average score, category-wise score, failures की list
Step 5 → कुछ बदलो (prompt / model / chunking) और वही dataset दोबारा चलाओ
Step 6 → Scores compare करो; quality बढ़ी/बराबर और cost/latency ठीक हो तभी ship करो
Step 7 → Deploy से पहले CI में चलाओ + production traffic के sample पर online eval करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 100 golden questions with correct HS codes. Version A (gpt-4o-mini, chunk 1000) scores 78% correct. Version B (chunk 500 + reranker) scores 88% but costs 20% more latency. Without the dataset the team would argue by opinion; with it they decide using data. A wrong HS code can mean a customs fine, so a regression gate in CI is essential.

**Amazon AI**: A product Q&A bot is tested on thousands of past customer questions each release; the release is blocked if the "grounded answer" rate drops by more than 2 points.

## 🟡 Real Example Hindi mein
**Tariff System**: 100 golden सवाल, सही HS codes के साथ। Version A (gpt-4o-mini, chunk 1000) 78% सही। Version B (chunk 500 + reranker) 88% सही, पर latency 20% ज़्यादा। Dataset न हो तो team राय पर बहस करती; dataset हो तो data से फैसला होता है। गलत HS code का मतलब customs fine हो सकता है, इसलिए CI में regression gate ज़रूरी है।

**Amazon AI**: Product Q&A bot को हर release पर हज़ारों पुराने customer सवालों पर test किया जाता है; "grounded answer" rate 2 points से ज़्यादा गिरे तो release रुक जाती है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny golden-set evaluation loop (offline, no API key needed)
from typing import Callable                       # type for the system under test

# Golden dataset: question -> expected HS code prefix
GOLDEN: list[dict[str, str]] = [
    {"q": "HS code for lithium-ion batteries", "expected": "8507"},
    {"q": "HS code for cotton t-shirts", "expected": "6109"},
    {"q": "HS code for smartphones", "expected": "8517"},
]


def system_v1(question: str) -> str:
    """Pretend AI system, version 1 (very naive keyword rules)."""
    q = question.lower()                          # normalise
    if "battery" in q or "batteries" in q:
        return "8507"
    if "cotton" in q:
        return "6109"
    return "0000"                                 # unknown -> wrong


def evaluate(system: Callable[[str], str]) -> float:
    """Return accuracy (0..1) of the system on the golden set."""
    correct = 0                                   # counter of right answers
    for row in GOLDEN:                            # loop every test case
        got = system(row["q"])                    # run the system
        ok = got.startswith(row["expected"])      # simple scoring rule
        print(f"{'PASS' if ok else 'FAIL'} | {row['q']} -> {got}")
        correct += int(ok)                        # True counts as 1
    return correct / len(GOLDEN)                  # accuracy


print("accuracy v1:", round(evaluate(system_v1), 2))   # 2 of 3 pass -> 0.67
```

## 💻 Code Example — Advanced
```python
# Advanced: async evaluation harness with concurrency, error capture and regression gate
import asyncio                                    # async runtime
import statistics                                 # mean / median
import time                                       # latency timing
from dataclasses import dataclass                 # result container
from typing import Awaitable, Callable

AsyncSystem = Callable[[str], Awaitable[str]]     # async system under test


@dataclass
class CaseResult:
    question: str                                 # test input
    expected: str                                 # gold label
    got: str                                      # system output
    passed: bool                                  # score
    latency_s: float                              # time taken
    error: str | None = None                      # exception text if crashed


async def run_case(system: AsyncSystem, row: dict[str, str], sem: asyncio.Semaphore) -> CaseResult:
    """Run one test case; never let one failure kill the whole run."""
    async with sem:                               # limit parallel calls (rate limits)
        start = time.perf_counter()               # start timer
        try:
            got = await asyncio.wait_for(system(row["q"]), timeout=10)   # protect from hangs
            return CaseResult(row["q"], row["expected"], got,
                              got.startswith(row["expected"]), time.perf_counter() - start)
        except Exception as exc:                  # timeout, API error, bug
            return CaseResult(row["q"], row["expected"], "", False,
                              time.perf_counter() - start, error=repr(exc))


async def evaluate_async(system: AsyncSystem, dataset: list[dict[str, str]],
                         concurrency: int = 5) -> dict[str, float]:
    sem = asyncio.Semaphore(concurrency)          # concurrency cap
    results = await asyncio.gather(*(run_case(system, r, sem) for r in dataset))
    return {
        "accuracy": sum(r.passed for r in results) / len(results),
        "errors": float(sum(r.error is not None for r in results)),
        "p50_latency_s": statistics.median(r.latency_s for r in results),
    }


async def system_v2(question: str) -> str:
    """Improved fake system (async like a real LLM call)."""
    await asyncio.sleep(0.01)                     # simulate network latency
    q = question.lower()
    table = {"batter": "8507", "cotton": "6109", "smartphone": "8517"}
    for key, code in table.items():
        if key in q:
            return code
    return "0000"


def regression_gate(old: float, new: float, tolerance: float = 0.0) -> bool:
    """CI rule: new version must not be worse than old (minus tolerance)."""
    return new >= old - tolerance


async def main() -> None:
    report = await evaluate_async(system_v2, GOLDEN)   # GOLDEN from basic example
    print(report)
    print("ship?", regression_gate(old=0.67, new=report["accuracy"]))


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Expose evaluation as an internal endpoint (or a CI script) and log online feedback from real users.

```python
# FastAPI: /eval/run for offline regression + /feedback for online signals
from fastapi import BackgroundTasks, FastAPI      # framework
from pydantic import BaseModel                     # validation

app = FastAPI()
last_report: dict[str, float] = {}                 # latest eval result (store in DB in prod)
feedback_log: list[dict] = []                      # thumbs up/down from users


class Feedback(BaseModel):
    question: str
    answer: str
    thumbs_up: bool                                # real user verdict


async def _run_eval() -> None:
    global last_report
    last_report = await evaluate_async(system_v2, GOLDEN)   # reuse harness


@app.post("/eval/run")
async def trigger(bg: BackgroundTasks) -> dict:
    bg.add_task(_run_eval)                         # do not block the request
    return {"status": "started"}


@app.get("/eval/report")
async def report() -> dict:
    return last_report or {"status": "no run yet"}


@app.post("/feedback")
async def feedback(item: Feedback) -> dict:
    feedback_log.append(item.model_dump())         # later turn bad answers into new test cases
    return {"ok": True}
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith (LangChain's platform) stores datasets and runs evaluators on them; Ragas and DeepEval plug in the same way. A basic custom evaluator with LangChain Runnables:

```python
# LangChain core: evaluate any Runnable over a dataset with a plain function scorer
from langchain_core.runnables import RunnableLambda   # wrap python function as Runnable

chain = RunnableLambda(lambda q: system_v1(q))        # pretend this is prompt | llm | parser

# .batch runs all questions (in parallel threads) and returns a list of outputs
outputs = chain.batch([row["q"] for row in GOLDEN])
scores = [o.startswith(r["expected"]) for o, r in zip(outputs, GOLDEN)]
print(sum(scores) / len(scores))
# With LangGraph: evaluate the final state of the graph, and also intermediate nodes
# (e.g. did the retriever node fetch the right chunk?) to locate WHERE failures come from.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Judging by a few hand-picked examples
✅ Correct: A dataset of at least 50-100 diverse cases, including hard and edge cases.

```python
# Wrong
print(system("HS code for phones"))   # "looks good!" ship it
# Right
print(evaluate(system))               # accuracy over the whole golden set
```

❌ Mistake 2: Testing on the same examples used to tune the prompt
✅ Correct: Keep a held-out test set that you never tune on (otherwise you overfit).

```python
# Wrong - tune and test on the same data
tune_prompt(GOLDEN); evaluate(system, GOLDEN)
# Right
dev, test = GOLDEN[:2], GOLDEN[2:]
tune_prompt(dev); evaluate_on(test)
```

❌ Mistake 3: Only looking at the average
✅ Correct: Break down by category (country, product type) - a 90% average can hide a 40% category.

---

## 🧠 Tricky Interview Question

**Q**: "Your RAG bot scores 92% on your eval set but users complain about wrong answers. How is that possible?"

**Answer**: The eval set does not represent real traffic (selection bias, too easy, too clean), or it leaked into prompt tuning (overfitting), or the metric is weak (e.g. LLM judge that likes fluent text). Also production has drifting documents and new question types. Fix: sample real queries into the dataset regularly, add failure cases from user feedback, use held-out data, combine offline eval with online monitoring, and audit the judge against human labels.

---

## ⚫ Interview Questions + Answers

Q1: What is a golden dataset?
A1: A curated set of inputs with trusted expected outputs (and sometimes source documents), used as the fixed yardstick to compare system versions.

Q2: Why can't we use normal unit tests for LLM apps?
A2: Outputs vary in wording, so exact equality fails. We still use unit tests for deterministic parts (parsers, routers), but need metrics and judges for free-text quality.

Q3: What is the difference between offline and online evaluation?
A3: Offline: run on a fixed dataset before release (repeatable, safe). Online: measure on live traffic (thumbs, escalation rate, sampled LLM-judge scores). You need both: offline for gating, online for reality.

Q4: What is a regression and how do you catch it?
A4: A regression is when a change makes previously good behaviour worse. Catch it by re-running the same dataset in CI and failing the build when scores drop beyond a tolerance.

Q5 (Hard): How do you evaluate a RAG system end to end and still know which component is at fault?
A5: Evaluate retrieval and generation separately. Retrieval: context precision/recall, hit-rate on gold chunks. Generation: faithfulness (grounded in context?) and answer relevancy/correctness. Then read the pattern: low recall means fix chunking/embeddings; low faithfulness with good context means fix prompt or model; low relevancy means the answer drifts from the question. This component-level view tells you where to spend effort.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything goes to production, or a wrong answer has real cost (customs, finance, health)
- You compare prompts, models, chunk sizes, retrievers
- Several people change the system over time

❌ Avoid (heavy setup) when:
- A throwaway prototype for a single demo
- Even then, keep at least 10 test questions

---

## 📊 Visual Diagram
```
   Golden Dataset (Q, expected, contexts)
              │
              ▼
   ┌──────────────────────┐      change prompt / model / chunking
   │  AI System (RAG)     │◄───────────────────────────────┐
   └──────────┬───────────┘                                │
              ▼                                            │
   outputs + retrieved chunks                              │
              ▼                                            │
   Metrics: faithfulness | relevancy | precision | recall  │
              ▼                                            │
   Score report ──► better? ── yes ──► deploy              │
                         └──── no ───────────────────────►─┘
```

---

## 💰 Cost Impact
- Evaluation itself costs tokens: LLM-judge metrics call a model per metric per sample. 100 questions x 4 metrics x ~1500 tokens = 600K tokens, about $0.09 on gpt-4o-mini input pricing ($0.15 per 1M) plus output tokens. Cheap compared with one production incident.
- Optimise: run cheap checks (exact match, regex, retrieval hit-rate) on everything, and LLM-judge only on a sample or on cheap-model; cache judge results by (input, output) hash; evaluate on every PR with a small set and run the full set nightly.
- Evaluation often reveals savings: you may prove a cheaper model scores the same.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden dataset | Trusted Q/A test set | भरोसेमंद test सवाल-जवाब |
| Regression | New change breaks old behaviour | नए बदलाव से पुराना काम बिगड़ना |
| Offline eval | Test before release on fixed data | Release से पहले fixed data पर test |
| Online eval | Measure on live traffic | Live traffic पर नापना |
| Overfitting | Tuned to test set, fails on real data | Test set पर tune, असली data पर फेल |
| Metric | Number describing quality | Quality बताने वाला number |

---

## ⚡ 3-Line Summary
English: Evaluation turns "looks fine" into measurable scores on a golden dataset. It catches regressions and shows which component (retriever or generator) is failing. Combine offline gates in CI with online monitoring.
Hindi: Evaluation "ठीक लग रहा है" को golden dataset पर measurable scores में बदलता है। ये regressions पकड़ता है और बताता है कि retriever या generator में से कौन फेल है। CI में offline gate और production में online monitoring दोनों रखो।

---

## ➡️ Next Topic
**390. RAG Evaluation Metrics** — the actual metrics (faithfulness, relevancy, precision, recall) that measure a RAG pipeline.
