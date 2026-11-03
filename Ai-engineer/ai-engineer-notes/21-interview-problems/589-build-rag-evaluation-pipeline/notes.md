---

# 589. Build RAG Evaluation Pipeline
# हिंदी में: RAG Evaluation Pipeline बनाना

---

## 🔵 Simple Definition (English)
A RAG evaluation pipeline runs a labelled "golden set" of questions through the system and scores retrieval (hit@k, recall@k, MRR) and generation (faithfulness, answer match). A threshold turns the scores into a pass/fail CI gate.

## 🔵 सरल परिभाषा (Hindi)
RAG evaluation pipeline एक labelled "golden set" के सवालों को system से चलाकर retrieval (hit@k, recall@k, MRR) और generation (faithfulness, answer match) की scoring करता है। Threshold इन scores को CI का pass/fail gate बना देता है।

---

## 🔴 Problem it Solves
Teams change chunk size, embeddings or prompts and judge the result by "it feels better". Quality silently regresses. Without separate retrieval and generation metrics you cannot tell whether the retriever or the LLM is at fault.

## 🔴 यह क्यों बना? (Hindi)
Teams chunk size, embeddings या prompt बदलती हैं और "बेहतर लग रहा है" से फैसला करती हैं। Quality चुपचाप गिरती है। Retrieval और generation के अलग metrics के बिना पता नहीं चलता कि गलती retriever की है या LLM की।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build golden set: Case(question, relevant doc ids, gold answer,
         retrieved ids, context, answer)
Step 2 → Retrieval: hit@k, recall@k, MRR from retrieved vs relevant
Step 3 → Generation: faithfulness (answer words supported by context),
         answer_match (gold answer words inside the answer)
Step 4 → evaluate() averages each metric; empty golden set -> ValueError
Step 5 → CI gate: any metric below 0.6 -> FAIL list, else PASS
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Golden set बनाओ: Case(question, relevant doc ids, gold answer,
         retrieved ids, context, answer)
Step 2 → Retrieval: relevant बनाम retrieved से hit@k, recall@k, MRR
Step 3 → Generation: faithfulness (answer के कितने words context में हैं),
         answer_match (gold answer के words answer में हैं या नहीं)
Step 4 → evaluate() हर metric का औसत; खाली golden set पर ValueError
Step 5 → CI gate: 0.6 से कम कोई metric -> FAIL list, वरना PASS
```

---

## 🟡 Real World Example
**Tariff Classification System**: 3 golden questions. For "origin rules" the retriever returned d3, d4 instead of d5, and the LLM answered "You need a visa", unsupported by the context. The report shows faithfulness 0.56 and MRR 0.50, so the CI gate fails and the change is not merged.

**Other**: Amazon product-QA bot regression tests before each release.

## 🟡 Real Example Hindi mein
**Tariff System**: 3 golden सवाल। "origin rules" पर retriever ने d5 की जगह d3, d4 दिए और LLM ने "You need a visa" कहा, जो context में नहीं है। Report में faithfulness 0.56 और MRR 0.50 आता है, CI gate fail होता है और change merge नहीं होता।

**Other**: Amazon product-QA bot का हर release से पहले regression test।

---

## 💻 Code Example — Basic
```python
retrieved = ["d4", "d2", "d9"]        # ranked results from the retriever
relevant = {"d2"}                      # gold document ids

hit = float(bool(set(retrieved[:2]) & relevant))          # was a relevant doc in the top 2?
rank = next((i for i, d in enumerate(retrieved, 1) if d in relevant), None)
mrr = 1 / rank if rank else 0.0                           # reciprocal rank of first relevant
print(hit, mrr)                                           # 1.0 0.5
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
hit@2          0.67
recall@2       0.67
mrr            0.50
faithfulness   0.56
answer_match   0.67
CI gate: FAIL ['mrr', 'faithfulness']
```
Excerpt from `main.py` (metrics and aggregation; `Case` as in the file):
```python
import asyncio
import re
from dataclasses import dataclass


@dataclass
class Case:
    question: str
    relevant: set[str]
    gold_answer: str
    retrieved: list[str]
    context: str
    answer: str


def toks(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))


def mrr(c: Case) -> float:
    for rank, d in enumerate(c.retrieved, 1):
        if d in c.relevant:
            return 1 / rank
    return 0.0


def faithfulness(c: Case) -> float:
    """Share of answer words supported by the context (mock for an LLM judge)."""
    a = toks(c.answer) - {"the", "is", "you", "a"}
    return len(a & toks(c.context)) / max(1, len(a))


async def evaluate(cases: list[Case], k: int = 2) -> dict[str, float]:
    if not cases:
        raise ValueError("golden set is empty")           # CI must never silently pass
    n = len(cases)
    return {"mrr": sum(mrr(c) for c in cases) / n,
            "faithfulness": sum(faithfulness(c) for c in cases) / n}
```

---

## 🟠 FastAPI Integration
Expose evaluation as an internal endpoint (or a CI script) so every deploy can be gated.

```python
from fastapi import FastAPI, HTTPException

from main import GOLDEN, evaluate                         # our module

app = FastAPI()


@app.post("/eval")
async def run_eval(threshold: float = 0.6) -> dict:
    try:
        report = await evaluate(GOLDEN)
    except ValueError as e:                               # empty golden set
        raise HTTPException(status_code=500, detail=str(e))
    failed = [m for m, v in report.items() if v < threshold]
    return {"report": report, "passed": not failed, "failed": failed}
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets and evaluators, or Ragas, provide the same metrics with an LLM judge instead of word overlap.

```python
# from langsmith import Client
# from langsmith.evaluation import evaluate
#
# def faithfulness_judge(run, example) -> dict:
#     ...  # LLM-as-judge: is every claim in run.outputs supported by the context?
#     return {"key": "faithfulness", "score": 0.9}
#
# evaluate(my_rag_chain, data="tariff-golden-set", evaluators=[faithfulness_judge])
score_example = {"key": "faithfulness", "score": 0.9}    # shape of an evaluator result
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Only checking the final answer. A right answer from the model's memory hides a broken retriever.
✅ Correct: score retrieval and generation separately.

```python
# Wrong: score = answer_match only
# Right: report hit@k, recall@k, MRR, faithfulness, answer_match together
```

❌ Mistake 2: Tiny or unlabelled golden set (3 cases is a demo, not a benchmark).
✅ Correct: grow to 50-200 real questions, reviewed by experts.

❌ Mistake 3: Letting an empty dataset pass. `evaluate` raises so CI fails loudly.

---

## 🧠 Tricky Interview Question
**Q**: "hit@2 is 0.67 but MRR is only 0.50. What does it tell you?"

**Answer**: The relevant document is usually in the top 2 but often at rank 2 (case 2: d2 at rank 2 gives 0.5; case 3 misses entirely). So the retriever finds the right docs but ranks them low. Fix with a reranker or better embeddings, since the LLM may pay more attention to top chunks.

---

## ⚫ Interview Questions + Answers

Q1: Difference between hit@k and recall@k?
A1: hit@k is 1 if any relevant doc is in the top k; recall@k is the fraction of all relevant docs found in the top k. They coincide when each question has one relevant doc.

Q2: What is MRR?
A2: Mean Reciprocal Rank: the average of 1/rank of the first relevant result.

Q3: What does faithfulness measure?
A3: Whether the answer is supported by the retrieved context (hallucination check). Here approximated by word overlap; in production an LLM judge.

Q4: Why a CI gate with a threshold?
A4: To block regressions automatically; tune thresholds per metric from a baseline.

Q5 (Hard): LLM-as-judge is noisy and biased. How do you trust it?
A5: Calibrate against human labels on a sample, use a fixed rubric and temperature 0, use a different model family than the one being judged, run pairwise comparisons, and track agreement rate and judge cost over time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Changing chunking, embeddings, rerankers or prompts
- Before every production release

❌ Avoid when:
- No labelled data yet (first build a small golden set by hand)

---

## 📊 Visual Diagram
```
 Golden set ─► RAG system ─► retrieved ids + answer
                                  │
        ┌─────────────────────────┴────────────────────┐
        ▼ retrieval                                    ▼ generation
  hit@k  recall@k  MRR                       faithfulness  answer_match
        └─────────────────────────┬────────────────────┘
                                  ▼
                       average, compare to 0.6
                          PASS ◄──┴──► FAIL [metrics]
```

---

## 💰 Cost Impact
Retrieval metrics are free. LLM-as-judge metrics cost tokens per case, so run the full judge nightly and a small smoke set per PR. Cache judge results for unchanged cases and use a cheaper judge model where rubric agreement is high.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Labelled test questions | सही उत्तरों वाला test set |
| hit@k | Relevant doc in top k? | Top k में सही doc है? |
| MRR | Average 1/rank of first hit | पहले सही result की rank का औसत |
| Faithfulness | Answer supported by context | जवाब context पर आधारित |
| CI gate | Automatic pass/fail check | Automatic pass/fail जाँच |

---

## ⚡ 3-Line Summary
English: Score retrieval and generation separately on a labelled golden set. Aggregate and compare with thresholds to gate CI. Fail loudly on empty data.
Hindi: Labelled golden set पर retrieval और generation की अलग scoring करो। Aggregate करके threshold से CI gate बनाओ। खाली data पर साफ fail करो।

---

## ➡️ Next Topic
**590. Build LangSmith Tracing** — metrics tell you that quality dropped; traces show where in the pipeline it happened.
