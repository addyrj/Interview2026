---

# 399. Ragas Dataset Creation
# हिंदी में: Ragas Dataset बनाना

---

## 🔵 Simple Definition (English)
Ragas is a library that scores RAG systems. Before it can score anything, it needs a **dataset**: for each test question, the user question, the retrieved contexts, the generated answer, and (for some metrics) a ground-truth reference answer. Creating this dataset correctly is step zero of every Ragas evaluation.

## 🔵 सरल परिभाषा (Hindi)
Ragas एक library है जो RAG system को score करती है। Score करने से पहले उसे एक **dataset** चाहिए: हर test question के लिए user question, retrieved contexts, generated answer, और (कुछ metrics के लिए) ground-truth reference answer। यह dataset सही बनाना हर Ragas evaluation का पहला कदम है।

---

## 🔴 Problem it Solves
Teams "eyeball" RAG answers and say "looks fine". There is no repeatable number. Ragas needs structured rows so every metric (faithfulness, context precision, etc.) can run on the same data. Wrong column names or missing fields make metrics crash or silently return NaN.

## 🔴 यह क्यों बना? (Hindi)
Teams RAG answers को आँख से देखकर बोलती हैं "ठीक लग रहा है"। कोई repeatable number नहीं होता। Ragas को structured rows चाहिए ताकि हर metric एक ही data पर चल सके। गलत column names या missing fields से metrics crash होते हैं या चुपचाप NaN देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect test questions (user_input) from real logs or synthetic generation
Step 2 → Run your RAG pipeline on each question
Step 3 → Capture retrieved_contexts (list of strings) and response (answer string)
Step 4 → Add reference (ground-truth answer) where you have one
Step 5 → Wrap rows in SingleTurnSample objects
Step 6 → Combine into EvaluationDataset
Step 7 → Pass dataset to ragas.evaluate() with chosen metrics
```

Note: in Ragas v0.2+ the column names are `user_input`, `retrieved_contexts`, `response`, `reference`. Older v0.1 used `question`, `contexts`, `answer`, `ground_truth`. Check your installed version.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Test questions (user_input) real logs या synthetic generation से लो
Step 2 → हर question पर अपनी RAG pipeline चलाओ
Step 3 → retrieved_contexts (strings की list) और response (answer) save करो
Step 4 → जहाँ ground truth हो वहाँ reference जोड़ो
Step 5 → Rows को SingleTurnSample में डालो
Step 6 → EvaluationDataset बनाओ
Step 7 → ragas.evaluate() को metrics के साथ दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: We have 100 questions like "What is the HS code for lithium-ion batteries?". For each, the RAG retrieves 3 tariff-schedule chunks and the LLM answers. The customs expert provides the correct HS code and explanation as `reference`. We store all 100 rows as an EvaluationDataset, so every new prompt or chunking change is scored on the same rows.

**Zomato-style**: "Is there a veg-only restaurant near me open after 11 PM?" - contexts are restaurant records, the response is the bot answer, the reference is a human-verified answer.

## 🟡 Real Example Hindi mein
**Tariff System**: हमारे पास 100 questions हैं जैसे "Lithium-ion batteries का HS code क्या है?"। हर question के लिए RAG 3 tariff chunks लाता है और LLM जवाब देता है। Customs expert सही HS code `reference` में देता है। इन 100 rows का EvaluationDataset बनता है, ताकि हर नए prompt या chunking बदलाव को उसी data पर score किया जा सके।

**Zomato-style**: "रात 11 बजे के बाद खुला veg-only restaurant पास में है?" - contexts restaurant records हैं, response bot का जवाब, reference human-verified जवाब।

---

## 💻 Code Example — Basic
```python
# Basic: build a Ragas-shaped dataset as plain dicts (pure Python, runs offline)
from typing import TypedDict  # TypedDict gives our row a fixed shape


class Row(TypedDict):  # one evaluation row
    user_input: str  # the question asked
    retrieved_contexts: list[str]  # chunks the retriever returned
    response: str  # answer the LLM generated
    reference: str  # ground-truth answer written by an expert


def validate_row(row: Row) -> list[str]:  # returns a list of problems found
    problems: list[str] = []  # start with no problems
    if not row["user_input"].strip():  # question must not be blank
        problems.append("empty user_input")  # record the problem
    if not row["retrieved_contexts"]:  # we need at least one context
        problems.append("no retrieved_contexts")  # record the problem
    if not all(isinstance(c, str) for c in row["retrieved_contexts"]):  # contexts must be strings
        problems.append("contexts must be list[str]")  # record the problem
    if not row["response"].strip():  # answer must not be blank
        problems.append("empty response")  # record the problem
    return problems  # empty list means the row is valid


rows: list[Row] = [  # our tiny hand-made dataset
    {
        "user_input": "HS code for lithium-ion batteries?",  # question
        "retrieved_contexts": ["8507.60 covers lithium-ion accumulators."],  # context
        "response": "The HS code is 8507.60.",  # generated answer
        "reference": "8507.60",  # expert answer
    },
    {
        "user_input": "",  # deliberately broken row
        "retrieved_contexts": [],  # also broken
        "response": "",  # also broken
        "reference": "n/a",  # reference present
    },
]

for i, r in enumerate(rows):  # check every row
    print(i, validate_row(r) or "OK")  # prints OK or the list of problems
# Output: 0 OK ; 1 ['empty user_input', 'no retrieved_contexts', 'empty response']
```

## 💻 Code Example — Advanced
```python
# Advanced: run a RAG pipeline (async) and build a real Ragas EvaluationDataset
# pip install ragas   (v0.2+)
import asyncio  # for concurrent pipeline calls
import json  # to save the dataset to disk
import logging  # for error logs
from typing import Any  # type hints

from ragas import EvaluationDataset  # Ragas dataset container
from ragas.dataset_schema import SingleTurnSample  # one-row schema

logger = logging.getLogger("ragas_dataset")  # module logger


async def mock_rag(question: str) -> tuple[list[str], str]:  # replace with your real RAG
    await asyncio.sleep(0.01)  # simulate network latency
    contexts = [f"Tariff chunk relevant to: {question}"]  # fake retrieval
    answer = f"Answer for: {question}"  # fake generation
    return contexts, answer  # contexts + answer


async def build_row(
    sem: asyncio.Semaphore, q: str, ref: str
) -> SingleTurnSample | None:  # returns None when the pipeline fails
    async with sem:  # limit concurrency to protect the API
        try:  # a single failure must not kill the batch
            contexts, answer = await mock_rag(q)  # run pipeline
            return SingleTurnSample(  # build Ragas sample
                user_input=q,  # question
                retrieved_contexts=contexts,  # list[str]
                response=answer,  # generated answer
                reference=ref,  # ground truth
            )
        except Exception as exc:  # catch any pipeline error
            logger.error("row failed for %r: %s", q, exc)  # log and continue
            return None  # skip this row


async def build_dataset(pairs: list[tuple[str, str]]) -> EvaluationDataset:
    sem = asyncio.Semaphore(5)  # max 5 parallel pipeline calls
    results = await asyncio.gather(*(build_row(sem, q, r) for q, r in pairs))  # run all
    samples = [s for s in results if s is not None]  # drop failures
    if not samples:  # nothing usable
        raise ValueError("no valid samples produced")  # fail loudly
    return EvaluationDataset(samples=samples)  # wrap in dataset


def save_jsonl(ds: EvaluationDataset, path: str) -> None:
    rows: list[dict[str, Any]] = ds.to_list()  # list of plain dicts
    with open(path, "w", encoding="utf-8") as f:  # open output file
        for row in rows:  # one JSON object per line
            f.write(json.dumps(row, ensure_ascii=False) + "\n")  # keep Hindi readable


if __name__ == "__main__":
    pairs = [("HS code for lithium-ion batteries?", "8507.60")]  # (question, reference)
    ds = asyncio.run(build_dataset(pairs))  # build dataset
    save_jsonl(ds, "tariff_eval.jsonl")  # persist for reuse
```

---

## 🟠 FastAPI Integration
An endpoint lets QA people upload questions and get back a ready dataset id, so evaluation can be triggered from CI.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # request validation

app = FastAPI()  # app instance
DATASETS: dict[str, list[dict]] = {}  # in-memory store (use a DB in production)


class QA(BaseModel):  # one question + expert answer
    question: str = Field(min_length=3)  # reject tiny questions
    reference: str  # ground truth


class BuildRequest(BaseModel):  # request body
    name: str  # dataset name
    items: list[QA] = Field(min_length=1)  # at least one item


@app.post("/eval/datasets")  # create dataset
async def create_dataset(req: BuildRequest) -> dict:
    rows = []  # collected rows
    for item in req.items:  # run RAG for each
        contexts, answer = await mock_rag(item.question)  # reuse pipeline from above
        rows.append({"user_input": item.question, "retrieved_contexts": contexts,
                     "response": answer, "reference": item.reference})  # one row
    if not rows:  # defensive check
        raise HTTPException(400, "empty dataset")  # bad request
    DATASETS[req.name] = rows  # store it
    return {"name": req.name, "rows": len(rows)}  # confirm
```

---

## 🔗 LangChain / LangGraph Connection
Ragas works with LangChain: you wrap your LCEL retriever + chain, call it per question, and pass the outputs into the dataset. In LangGraph, capture `state["documents"]` and `state["generation"]` at the end of the graph run.

```python
# Build rows from a LangChain retriever + chain
def rows_from_chain(questions: list[str], retriever, chain) -> list[dict]:
    out = []  # result rows
    for q in questions:  # each question
        docs = retriever.invoke(q)  # LCEL retriever returns Document list
        answer = chain.invoke({"question": q, "context": docs})  # generate
        out.append({"user_input": q,
                    "retrieved_contexts": [d.page_content for d in docs],  # strings only
                    "response": answer})  # answer text
    return out  # ready for EvaluationDataset.from_list
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting Document objects (not strings) in contexts
✅ Correct: pass `d.page_content`

```python
# Wrong - Ragas expects list[str]
sample = {"retrieved_contexts": docs}
# Right
sample = {"retrieved_contexts": [d.page_content for d in docs]}
```

❌ Mistake 2: Using old column names with a new Ragas version
✅ Correct: use `user_input/response/reference`

```python
# Wrong (v0.1 names on v0.2+)
row = {"question": q, "answer": a, "ground_truth": g}
# Right
row = {"user_input": q, "response": a, "reference": g}
```

❌ Mistake 3: Building the dataset from questions the retriever was tuned on (leakage).
✅ Correct: keep a held-out test split.

---

## 🧠 Tricky Interview Question
**Q**: "Your Ragas faithfulness is 0.95 but users complain about wrong answers. Dataset has 40 rows. What is likely wrong?"

**Answer**: The dataset is probably too small and not representative: it was built from easy, clean questions. Faithfulness only checks that the answer is supported by the retrieved context, not that the context is correct. If retrieval is wrong, faithfulness can still be high. Add real production questions, hard cases, and check context recall/precision with references.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What fields does a Ragas single-turn sample have?
A1: `user_input`, `retrieved_contexts`, `response`, and optionally `reference` (ground truth).

Q2: [Easy] Why do we need a dataset before evaluating?
A2: Metrics are computed per row; a fixed dataset makes scores comparable across prompt/model/chunking changes.

Q3: [Medium] Which metrics need `reference` and which do not?
A3: Faithfulness and answer relevancy need only question, contexts, response. Context recall and (reference-based) context precision need `reference`.

Q4: [Medium] How many rows do you need?
A4: Start with 50-100 diverse rows for development signals; 200-500 for release decisions. Cover easy, hard, ambiguous, and out-of-scope questions.

Q5: [Hard] How do you keep the dataset from going stale?
A5: Version it (git or DVC), refresh monthly with sampled production queries, add every reported bug as a new row, and re-run the baseline whenever the dataset changes so scores stay comparable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You change prompts, chunking, retriever or model and need proof
- You want CI regression checks on RAG quality

❌ Avoid when:
- You have only 3-5 rows (scores are noise)
- The system is not RAG (use task-specific evals)

---

## 📊 Visual Diagram
```
 Questions ──► RAG pipeline ──► contexts + response
     │                                │
     └─ expert reference ─────────────┤
                                      ▼
                         SingleTurnSample (per row)
                                      ▼
                          EvaluationDataset
                                      ▼
                          ragas.evaluate(metrics)
```

---

## 💰 Cost Impact
Building the dataset costs one RAG run per row: ~1,500 input + 300 output tokens each. 100 rows on gpt-4o-mini = ~150K in + 30K out = about $0.04. The real cost comes later: each Ragas metric makes several judge LLM calls per row.
Optimise: cache pipeline outputs on disk, build once and reuse, use a cheap judge model for development, and sample rows for quick checks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EvaluationDataset | Container of samples for Ragas | Evaluation rows का container |
| user_input | The question | User का सवाल |
| retrieved_contexts | Chunks retrieved | Retriever से मिले chunks |
| response | LLM answer | LLM का जवाब |
| reference | Ground-truth answer | सही जवाब (expert का) |
| Leakage | Test data seen during tuning | Test data का पहले से इस्तेमाल |

---

## ⚡ 3-Line Summary
English: A Ragas dataset is rows of question, contexts, response and reference. Build it by running your RAG per question and wrapping outputs in SingleTurnSample. Keep it versioned, diverse and free of leakage.
Hindi: Ragas dataset में question, contexts, response और reference की rows होती हैं। हर question पर RAG चलाकर SingleTurnSample में रखो। Dataset versioned, diverse और leakage-free रखो।

---

## ➡️ Next Topic
**400. Ragas Evaluation Pipeline** - now that the dataset exists, run metrics end to end and read the scores.
