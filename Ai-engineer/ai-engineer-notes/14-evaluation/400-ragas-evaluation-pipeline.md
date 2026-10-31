---

# 400. Ragas Evaluation Pipeline
# हिंदी में: Ragas Evaluation Pipeline

---

## 🔵 Simple Definition (English)
A Ragas evaluation pipeline is the full loop: load dataset, choose metrics, give Ragas a judge LLM, run `evaluate()`, read the score table, and decide pass or fail. It turns "is my RAG good?" into numbers you can track in CI.

## 🔵 सरल परिभाषा (Hindi)
Ragas evaluation pipeline पूरा loop है: dataset load करो, metrics चुनो, Ragas को judge LLM दो, `evaluate()` चलाओ, score table पढ़ो और pass/fail तय करो। इससे "मेरा RAG अच्छा है?" एक number बन जाता है जिसे CI में track कर सकते हैं।

---

## 🔴 Problem it Solves
Running metrics one by one in notebooks is slow, inconsistent and not repeatable. Different people use different judge models and thresholds. A pipeline fixes the judge, metrics, thresholds and output format so results are comparable run after run.

## 🔴 यह क्यों बना? (Hindi)
Notebook में metrics एक-एक करके चलाना धीमा और inconsistent है। अलग लोग अलग judge और thresholds लेते हैं। Pipeline judge, metrics, thresholds और output format तय कर देती है, ताकि हर run के results comparable रहें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load EvaluationDataset (question, contexts, response, reference)
Step 2 → Pick metrics: Faithfulness, ResponseRelevancy, context precision/recall
Step 3 → Wrap a judge LLM (and embeddings for relevancy) for Ragas
Step 4 → evaluate(dataset, metrics, llm, embeddings) - Ragas calls judge per row/metric
Step 5 → Get result object -> to_pandas() for per-row scores
Step 6 → Aggregate: mean per metric
Step 7 → Compare to thresholds -> fail the CI job if below
Step 8 → Save report for trend tracking
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → EvaluationDataset load करो
Step 2 → Metrics चुनो: Faithfulness, ResponseRelevancy, context precision/recall
Step 3 → Judge LLM (और relevancy के लिए embeddings) Ragas के लिए wrap करो
Step 4 → evaluate() चलाओ - Ragas हर row/metric पर judge को call करता है
Step 5 → result.to_pandas() से per-row scores लो
Step 6 → हर metric का mean निकालो
Step 7 → Thresholds से compare करो, कम हो तो CI fail करो
Step 8 → Trend के लिए report save करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Every pull request that touches the prompt or chunker triggers the pipeline on the 100-row tariff dataset. Gate: faithfulness >= 0.85 and context recall >= 0.80. A PR that changes chunk size from 500 to 200 tokens drops context recall to 0.71, so CI fails and the engineer sees the exact rows that regressed.

**Amazon-style**: Product-QA bot is evaluated nightly; a dashboard shows faithfulness trend per product category.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt या chunker बदलने वाला हर pull request 100-row tariff dataset पर pipeline चलाता है। Gate: faithfulness >= 0.85 और context recall >= 0.80। Chunk size 500 से 200 tokens करने पर context recall 0.71 हो गया, CI fail हुआ और engineer को वही rows दिखीं जो खराब हुईं।

**Amazon-style**: Product-QA bot हर रात evaluate होता है; dashboard में category-wise faithfulness trend दिखता है।

---

## 💻 Code Example — Basic
```python
# Basic: the pipeline's decision logic, pure Python (no API key needed)
from statistics import mean  # to average scores


scores_per_row: list[dict[str, float]] = [  # pretend Ragas output rows
    {"faithfulness": 0.9, "context_recall": 0.8},  # row 1
    {"faithfulness": 0.7, "context_recall": 0.9},  # row 2
    {"faithfulness": 0.95, "context_recall": 0.7},  # row 3
]

THRESHOLDS: dict[str, float] = {"faithfulness": 0.85, "context_recall": 0.80}  # pass levels


def aggregate(rows: list[dict[str, float]]) -> dict[str, float]:  # mean per metric
    keys = rows[0].keys()  # metric names
    return {k: round(mean(r[k] for r in rows), 3) for k in keys}  # average each


def gate(agg: dict[str, float]) -> list[str]:  # returns failing metrics
    return [k for k, t in THRESHOLDS.items() if agg.get(k, 0.0) < t]  # below threshold


agg = aggregate(scores_per_row)  # compute means
print(agg)  # {'faithfulness': 0.85, 'context_recall': 0.8}
failed = gate(agg)  # find failures
print("FAIL" if failed else "PASS", failed)  # PASS [] for this data (0.85 >= 0.85, 0.8 >= 0.8)
```

## 💻 Code Example — Advanced
```python
# Advanced: real Ragas v0.2+ pipeline with OpenAI judge, async, error handling
# pip install ragas langchain-openai pandas
import asyncio  # run blocking evaluate in a thread
import logging  # logging for failures
import sys  # exit codes for CI

from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # judge + embeddings
from ragas import EvaluationDataset, evaluate  # core API
from ragas.embeddings import LangchainEmbeddingsWrapper  # wrap embeddings
from ragas.llms import LangchainLLMWrapper  # wrap judge LLM
from ragas.metrics import (  # metric classes (v0.2 names)
    Faithfulness,
    LLMContextRecall,
    ResponseRelevancy,
)

log = logging.getLogger("ragas_pipeline")  # logger
THRESHOLDS: dict[str, float] = {"faithfulness": 0.85, "context_recall": 0.80}  # CI gate


def run_eval(rows: list[dict]) -> dict[str, float]:  # synchronous core
    ds = EvaluationDataset.from_list(rows)  # build dataset from dicts
    judge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))  # cheap judge
    emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))  # embeddings
    result = evaluate(  # run all metrics
        dataset=ds,
        metrics=[Faithfulness(), LLMContextRecall(), ResponseRelevancy()],
        llm=judge,
        embeddings=emb,
        raise_exceptions=False,  # a failing row becomes NaN instead of crashing
    )
    df = result.to_pandas()  # per-row table
    numeric = df.select_dtypes("number")  # keep only score columns
    return numeric.mean(skipna=True).round(3).to_dict()  # mean per metric


async def run_eval_async(rows: list[dict]) -> dict[str, float]:  # async wrapper
    return await asyncio.to_thread(run_eval, rows)  # do not block the event loop


def check(agg: dict[str, float]) -> int:  # returns process exit code
    bad = {k: v for k, v in agg.items() if k in THRESHOLDS and v < THRESHOLDS[k]}  # failures
    if bad:  # any failure
        log.error("quality gate failed: %s", bad)  # explain
        return 1  # non-zero fails CI
    return 0  # success


if __name__ == "__main__":
    rows = [{"user_input": "HS code for lithium-ion batteries?",
             "retrieved_contexts": ["8507.60 covers lithium-ion accumulators."],
             "response": "8507.60", "reference": "8507.60"}]  # tiny demo row
    try:
        agg = asyncio.run(run_eval_async(rows))  # run pipeline
    except Exception as exc:  # network/auth errors
        log.exception("evaluation crashed: %s", exc)  # log traceback
        sys.exit(2)  # distinct code for infra errors
    print(agg)  # show means
    sys.exit(check(agg))  # pass/fail
```

---

## 🟠 FastAPI Integration
Expose evaluation as a background job so a dashboard can trigger it without blocking.

```python
import uuid  # job ids
from fastapi import BackgroundTasks, FastAPI, HTTPException  # FastAPI tools

app = FastAPI()  # app
JOBS: dict[str, dict] = {}  # job store (use Redis/DB in production)


async def _job(job_id: str, rows: list[dict]) -> None:  # background worker
    try:
        JOBS[job_id] = {"status": "running"}  # mark running
        agg = await run_eval_async(rows)  # reuse pipeline from above
        JOBS[job_id] = {"status": "done", "scores": agg, "exit": check(agg)}  # save result
    except Exception as exc:  # any failure
        JOBS[job_id] = {"status": "error", "detail": str(exc)}  # save error


@app.post("/eval/run")  # start a run
async def start(rows: list[dict], bg: BackgroundTasks) -> dict:
    if not rows:  # validate input
        raise HTTPException(400, "rows required")  # bad request
    job_id = uuid.uuid4().hex  # unique id
    bg.add_task(_job, job_id, rows)  # schedule work
    return {"job_id": job_id}  # client polls this id


@app.get("/eval/{job_id}")  # poll status
async def status(job_id: str) -> dict:
    return JOBS.get(job_id, {"status": "unknown"})  # return job info
```

---

## 🔗 LangChain / LangGraph Connection
Ragas judges are LangChain chat models wrapped by `LangchainLLMWrapper`, so any LangChain model works (OpenAI, Anthropic, Ollama). For LangGraph apps, run the compiled graph per question, collect `documents` and `generation` from final state, then feed Ragas.

```python
# Collect rows from a LangGraph app
async def collect(app_graph, questions: list[str]) -> list[dict]:
    rows = []  # output
    for q in questions:  # each question
        state = await app_graph.ainvoke({"question": q})  # run graph
        rows.append({"user_input": q,
                     "retrieved_contexts": [d.page_content for d in state["documents"]],
                     "response": state["generation"]})  # final answer
    return rows  # pass to run_eval_async
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Judging with a different model every run
✅ Correct: pin judge model and temperature 0

```python
# Wrong
judge = ChatOpenAI(model="gpt-4o-mini")   # default temperature, unpinned
# Right
judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

❌ Mistake 2: Averaging with NaN as zero or crashing on one bad row
✅ Correct: `raise_exceptions=False` and `mean(skipna=True)`, and report how many rows were NaN.

❌ Mistake 3: Only looking at the mean.
✅ Correct: inspect the lowest 10 rows - averages hide failure clusters.

---

## 🧠 Tricky Interview Question
**Q**: "Same code, same dataset, faithfulness changes 0.86 -> 0.82 between runs. Is the system worse?"

**Answer**: Not necessarily. LLM-judge metrics are stochastic and sensitive to the judge model version. Pin temperature 0 and the judge model, run 3 times and compare means with the standard deviation, and use a margin (e.g. fail only when drop > 0.03). Also check how many rows were NaN.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `evaluate()` return?
A1: A result object with aggregate scores; `to_pandas()` gives per-row scores.

Q2: [Easy] Why set `temperature=0` for the judge?
A2: To reduce randomness so score changes reflect system changes, not judge noise.

Q3: [Medium] Why do some metrics need embeddings?
A3: ResponseRelevancy generates questions from the answer and compares them to the original using embedding similarity.

Q4: [Medium] How do you gate CI on Ragas?
A4: Compute mean per metric, compare to thresholds, return non-zero exit code on failure, and upload the per-row table as an artifact.

Q5: [Hard] How do you reduce evaluation cost for 5,000 rows?
A5: Stratified sampling for PRs and full runs nightly, a cheaper judge for development, cached outputs, async concurrency limits (`RunConfig(max_workers=...)`), and skipping unchanged rows by hashing input+config.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need repeatable RAG quality tracking
- You compare retrievers, prompts or models

❌ Avoid when:
- You have no judge budget and need real-time scoring per user request
- You evaluate non-RAG tasks (use G-Eval or custom checks)

---

## 📊 Visual Diagram
```
 Dataset ─► evaluate(metrics, judge LLM, embeddings)
                     │
        ┌────────────┼─────────────┐
   Faithfulness  ContextRecall  ResponseRelevancy
        └────────────┼─────────────┘
                     ▼
              per-row DataFrame ─► mean ─► threshold ─► PASS / FAIL
```

---

## 💰 Cost Impact
Each metric makes roughly 1-4 judge calls per row (~1,000-2,500 tokens each). For 100 rows x 3 metrics on gpt-4o-mini: about 600K tokens, roughly $0.10-$0.25. With gpt-4o it is ~30x more.
Optimise: cheap judge in CI, expensive judge monthly; sample rows; cache; fewer metrics per PR.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| evaluate() | Runs metrics on dataset | Dataset पर metrics चलाना |
| Judge LLM | Model that scores outputs | Score देने वाला LLM |
| Threshold | Minimum acceptable score | न्यूनतम स्वीकार्य score |
| Quality gate | CI check on scores | Score पर CI check |
| NaN row | Row where metric failed | जिस row में metric fail हुआ |

---

## ⚡ 3-Line Summary
English: Pipeline = dataset + metrics + pinned judge + evaluate + thresholds. Use per-row output to debug, not only the mean. Pin the judge, handle NaN, and gate CI.
Hindi: Pipeline = dataset + metrics + pinned judge + evaluate + thresholds। Debug के लिए सिर्फ mean नहीं, per-row output देखो। Judge pin करो, NaN संभालो और CI gate लगाओ।

---

## ➡️ Next Topic
**401. Ragas with OpenAI** - configure OpenAI judge and embeddings properly, model choice and cost.
