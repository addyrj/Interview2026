---

# 397. Ragas — Complete Guide
# हिंदी में: Ragas — पूरी Guide

---

## 🔵 Simple Definition (English)
Ragas is an open-source Python library to evaluate RAG and LLM apps. You give it a dataset (question, retrieved contexts, response, reference) and a list of metrics (faithfulness, context recall, answer relevancy, factual correctness...). It uses an LLM judge and returns scores.

## 🔵 सरल परिभाषा (Hindi)
Ragas RAG और LLM apps को evaluate करने की open-source Python library है। इसे dataset (question, retrieved contexts, response, reference) और metrics की list (faithfulness, context recall, answer relevancy, factual correctness...) दो। ये LLM judge से scores लौटाती है।

---

## 🔴 Problem it Solves
"Looks good to me" testing does not scale and hides regressions. Writing your own judge prompts for every metric is slow and inconsistent. Ragas gives standard, reusable metrics so you can compare changes with numbers.

## 🔴 यह क्यों बना? (Hindi)
"मुझे ठीक लग रहा है" वाली testing scale नहीं होती और regressions छुपाती है। हर metric के लिए अपने judge prompts लिखना धीमा और inconsistent है। Ragas standard, reusable metrics देता है ताकि बदलावों की तुलना numbers से हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect samples: user_input, retrieved_contexts, response, reference
Step 2 → Wrap them in an EvaluationDataset
Step 3 → Choose metrics (retrieval, generation, end-to-end)
Step 4 → Configure judge LLM (and embeddings where needed)
Step 5 → evaluate(dataset, metrics) -> each metric prompts the judge
Step 6 → Get per-row scores + averages (result.to_pandas())
Step 7 → Compare runs, find weak slices, fix retriever/prompt, re-run
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Samples इकट्ठा करो: user_input, retrieved_contexts, response, reference
Step 2 → उन्हें EvaluationDataset में रखो
Step 3 → Metrics चुनो (retrieval, generation, end-to-end)
Step 4 → Judge LLM (और ज़रूरत हो तो embeddings) configure करो
Step 5 → evaluate(dataset, metrics) -> हर metric judge को prompt करता है
Step 6 → Per-row scores + averages मिलते हैं (result.to_pandas())
Step 7 → Runs compare करो, कमज़ोर slices ढूँढो, retriever/prompt सुधारो, दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200 golden questions with expert references. After switching chunk size from 800 to 400 tokens, Ragas shows context recall 0.71 -> 0.82 but faithfulness 0.93 -> 0.90. The team keeps 400 and tweaks the prompt. **Amazon-style**: compare two product-QA prompts by answer relevancy before an A/B test.

## 🟡 Real Example Hindi mein
**Tariff System**: 200 golden सवाल expert references के साथ। Chunk size 800 से 400 tokens करने पर Ragas दिखाता है context recall 0.71 -> 0.82 पर faithfulness 0.93 -> 0.90। Team 400 रखती है और prompt tweak करती है। **Amazon-style**: A/B test से पहले दो product-QA prompts को answer relevancy से compare करो।

---

## 💻 Code Example — Basic
```python
# Basic Ragas run. pip install ragas langchain-openai   (needs OPENAI_API_KEY)
from ragas import evaluate, EvaluationDataset                 # core API
from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness   # metrics
from ragas.llms import LangchainLLMWrapper                    # judge wrapper
from langchain_openai import ChatOpenAI                       # judge model

samples = [{                                                  # one test row
    "user_input": "What is the duty on lithium-ion batteries?",              # question
    "retrieved_contexts": ["Lithium-ion packs fall under HS 8507.60; basic duty 20 percent."],
    "response": "HS 8507.60 with 20 percent basic duty.",     # system answer
    "reference": "HS 8507.60, basic duty 20 percent.",        # ground truth
}]
dataset = EvaluationDataset.from_list(samples)                # build dataset
judge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))   # judge LLM
result = evaluate(dataset=dataset,                            # run evaluation
                  metrics=[Faithfulness(), LLMContextRecall(), FactualCorrectness()],
                  llm=judge)
print(result)                                                 # averages per metric
print(result.to_pandas())                                     # per-row details
```
Not run here (needs API key and the ragas package); API names follow Ragas 0.2+.

## 💻 Code Example — Advanced
```python
# Production: async evaluation wrapper, threshold gate for CI, error handling, typed output.
import asyncio                                                # async
import logging                                                # logs
from dataclasses import dataclass                             # result type
from ragas import evaluate, EvaluationDataset                 # core
from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness, ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

log = logging.getLogger("ragas_eval")                         # logger

@dataclass
class EvalReport:
    scores: dict[str, float]                                  # metric -> mean
    passed: bool                                              # threshold gate

THRESHOLDS = {"faithfulness": 0.85, "context_recall": 0.75}   # CI gates

def _run(rows: list[dict]) -> EvalReport:
    ds = EvaluationDataset.from_list(rows)
    llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
    emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))
    res = evaluate(ds, metrics=[Faithfulness(), LLMContextRecall(), FactualCorrectness(), ResponseRelevancy()],
                   llm=llm, embeddings=emb)
    df = res.to_pandas()                                      # per-row dataframe
    numeric = df.select_dtypes("number").mean().to_dict()     # mean per metric column
    ok = all(numeric.get(k, 0.0) >= v for k, v in THRESHOLDS.items())
    return EvalReport(scores={k: float(v) for k, v in numeric.items()}, passed=ok)

async def run_eval(rows: list[dict]) -> EvalReport:
    try:
        return await asyncio.to_thread(_run, rows)            # evaluate() is sync/blocking
    except Exception as exc:                                  # judge/network errors
        log.error("ragas failed: %s", exc)
        raise
```
Column names in the dataframe depend on the Ragas version; print `df.columns` once and adjust THRESHOLDS keys.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException                    # app + errors
from pydantic import BaseModel                                # models

app = FastAPI()                                               # app

class Sample(BaseModel):
    user_input: str                                           # question
    retrieved_contexts: list[str]                             # chunks
    response: str                                             # answer
    reference: str                                            # ground truth

@app.post("/eval/ragas")
async def eval_endpoint(rows: list[Sample]) -> dict:
    if len(rows) > 100:
        raise HTTPException(status_code=413, detail="max 100 rows per call")   # protect cost
    report = await run_eval([r.model_dump() for r in rows])   # pydantic v2 dump
    return {"scores": report.scores, "passed": report.passed}
```
Better in production: queue the job and poll, since evaluation takes minutes.

---

## 🔗 LangChain / LangGraph Connection
```python
# Build the dataset from your own LangChain/LangGraph pipeline:
def build_rows(questions: list[str], references: list[str], rag_chain) -> list[dict]:
    rows = []
    for q, ref in zip(questions, references):
        out = rag_chain.invoke({"question": q})               # your chain returns answer + docs
        rows.append({"user_input": q,
                     "retrieved_contexts": [d.page_content for d in out["docs"]],
                     "response": out["answer"],
                     "reference": ref})
    return rows
# Ragas wraps LangChain models (LangchainLLMWrapper) so the judge can be any LangChain chat model.
# LangSmith / Langfuse can store traces to turn production traffic into eval datasets.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating on 5 examples
✅ Correct: 50-200+ diverse rows; LLM judges are noisy.

```python
# Wrong
samples = 5  # rows
# Right
samples = 100  # or more rows covering easy, hard and edge cases
```

❌ Mistake 2: Judge temperature > 0 and unpinned model
✅ Correct: temperature 0, pin the judge model version, record it with results.

```python
# Wrong
ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
# Right
ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

## 🧠 Tricky Interview Question
**Q**: "Ragas scores improved after a prompt change but users are unhappy. How is that possible?"

**Answer**: Metrics are proxies. The golden set may not match real queries, the judge may favour verbose answers, and metrics may not capture tone, latency or safety. Fix: refresh the dataset from production traces, add human review samples, track user feedback, and include slice metrics (by query type/language).

---

## ⚫ Interview Questions + Answers

Q1: What is Ragas? (Easy)
A1: A library that scores RAG/LLM apps with LLM-judged metrics.

Q2: Name four Ragas metrics. (Easy)
A2: Faithfulness, context recall, context precision, answer/response relevancy (also factual correctness).

Q3: Which metrics need a reference? (Medium)
A3: Context recall, factual/answer correctness, reference-based context precision. Faithfulness and response relevancy do not.

Q4: Why is the judge model important? (Medium)
A4: Scores depend on the judge's reasoning; a weak or changing judge makes results incomparable across runs.

Q5: How to integrate Ragas into a release process? (Hard)
A5: Versioned golden dataset, deterministic judge config, nightly and pre-release runs, thresholds with tolerance, per-slice reports, storage of scores per git commit, and periodic human calibration of the judge.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Comparing retrievers, prompts, models
- Regression testing

❌ Avoid when:
- You only need a quick unit-level check (use asserts)
- You cannot afford judge costs at scale (sample instead)

---

## 📊 Visual Diagram
```
 dataset rows ─► [ metrics ] ─► judge LLM (+embeddings) ─► scores
   question        Faithfulness
   contexts        ContextRecall                           mean per metric
   response        FactualCorrectness                      per-row table
   reference       ResponseRelevancy                       thresholds -> CI pass/fail
```

---

## 💰 Cost Impact
Each metric makes several judge calls per row (roughly 1-4K tokens per row per metric). Four metrics x 200 rows can be 1-3M tokens: about $0.15-0.50 on gpt-4o-mini, many times more on a flagship judge. Optimise: sample rows, only run needed metrics, cache unchanged rows, use cheaper judge for dev and stronger for release.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ragas | RAG evaluation library | RAG evaluation library |
| EvaluationDataset | Rows to score | scoring के rows |
| Metric | A scoring method | scoring का तरीका |
| LLM judge | LLM that grades | grade करने वाला LLM |
| Golden set | Trusted test data | भरोसेमंद test data |

---

## ⚡ 3-Line Summary
English: Ragas scores RAG apps with standard LLM-judged metrics over a dataset. Use a pinned, temperature-0 judge and enough rows. Gate releases on trends, not single numbers.
Hindi: Ragas dataset पर standard LLM-judged metrics से RAG apps को score करता है। Pinned, temperature-0 judge और काफ़ी rows इस्तेमाल करो। Releases को single numbers नहीं, trends पर gate करो।

---

## ➡️ Next Topic
**398. Ragas Setup** - installing, configuring the judge and running your first evaluation.
