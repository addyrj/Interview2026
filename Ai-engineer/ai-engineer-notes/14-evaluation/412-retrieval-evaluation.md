---

# 412. Retrieval Evaluation
# हिंदी में: Retrieval Evaluation

---

## 🔵 Simple Definition (English)
Retrieval evaluation measures how well the retriever alone finds the right chunks for a question, before the LLM writes anything. You label which chunks are relevant for each query, then compute ranking metrics such as Recall@k, Precision@k, MRR and nDCG.

## 🔵 सरल परिभाषा (Hindi)
Retrieval evaluation सिर्फ retriever को नापता है कि वह सवाल के लिए सही chunks कितनी अच्छी तरह ढूँढता है, LLM के कुछ लिखने से पहले। हर query के लिए relevant chunks label करते हैं, फिर Recall@k, Precision@k, MRR और nDCG जैसे ranking metrics निकालते हैं।

---

## 🔴 Problem it Solves
When a RAG answer is wrong, is it retrieval or generation? If the right chunk was never retrieved, no prompt can fix it. Measuring retrieval separately (cheap, no LLM judge needed) tells you where to invest: chunking, embeddings, hybrid search, reranking.

## 🔴 यह क्यों बना? (Hindi)
RAG का जवाब गलत हो तो समस्या retrieval की है या generation की? सही chunk मिला ही नहीं तो कोई prompt ठीक नहीं कर सकता। Retrieval को अलग नापना (सस्ता, LLM judge नहीं चाहिए) बताता है कि कहाँ मेहनत करनी है: chunking, embeddings, hybrid search या reranking।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build labelled set: query -> set of relevant chunk ids
Step 2 → Run retriever for each query, get ranked top-k ids
Step 3 → Hit@k / Recall@k: fraction of relevant chunks found in top-k
Step 4 → Precision@k: fraction of top-k that are relevant
Step 5 → MRR: 1 / rank of first relevant result, averaged
Step 6 → nDCG@k: gain discounted by position, normalised by ideal order
Step 7 → Slice by query type; compare retrievers (BM25 vs vector vs hybrid vs +rerank)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Labelled set बनाओ: query -> relevant chunk ids का set
Step 2 → हर query पर retriever चलाओ, ranked top-k ids लो
Step 3 → Hit@k / Recall@k: top-k में मिले relevant chunks का अनुपात
Step 4 → Precision@k: top-k में relevant chunks का अनुपात
Step 5 → MRR: पहले relevant result की rank का 1/rank, औसत
Step 6 → nDCG@k: position के हिसाब से discounted gain, ideal order से normalise
Step 7 → Query type से slice करो; retrievers की तुलना (BM25, vector, hybrid, +rerank)
```

---

## 🟡 Real World Example
**Tariff Classification System**: For the query "lithium battery for laptop", chunk `8507.60` is the only relevant one. BM25 puts it at rank 4, vectors at rank 1, hybrid at rank 1. Over 200 labelled queries: BM25 Recall@5 = 0.71, vector 0.83, hybrid 0.89, hybrid + reranker 0.93. The team picks hybrid + reranker because Recall@5 directly bounds answer quality.

**Zomato-style**: For "cheap veg biryani near me open now", metrics are computed per filter type (price, cuisine, open-now) to see which filter the retriever ignores.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "laptop के लिए lithium battery" में सिर्फ chunk `8507.60` relevant है। BM25 उसे rank 4 पर रखता है, vectors rank 1 पर, hybrid rank 1 पर। 200 labelled queries पर: BM25 Recall@5 = 0.71, vector 0.83, hybrid 0.89, hybrid + reranker 0.93। Team hybrid + reranker चुनती है क्योंकि Recall@5 सीधे answer quality की सीमा तय करता है।

**Zomato-style**: "सस्ता veg biryani पास में अभी खुला" के लिए metrics filter type (price, cuisine, open-now) के हिसाब से निकलते हैं ताकि पता चले कौन सा filter retriever अनदेखा करता है।

---

## 💻 Code Example — Basic
```python
# Basic: retrieval metrics from scratch (pure Python, offline)
import math  # log2 for nDCG


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:  # nothing to find
        return 0.0
    return len(set(ranked[:k]) & relevant) / len(relevant)  # found / total relevant


def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    top = ranked[:k]  # top-k results
    return sum(r in relevant for r in top) / k if k else 0.0  # relevant share


def mrr(ranked: list[str], relevant: set[str]) -> float:
    for i, r in enumerate(ranked, start=1):  # rank starts at 1
        if r in relevant:  # first relevant hit
            return 1 / i  # reciprocal rank
    return 0.0  # never found


def ndcg_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    dcg = sum(1 / math.log2(i + 1) for i, r in enumerate(ranked[:k], start=1) if r in relevant)  # actual
    ideal = sum(1 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))  # best order
    return dcg / ideal if ideal else 0.0  # normalised


ranked = ["8501", "8507.60", "8517", "8471"]  # retriever output
rel = {"8507.60"}  # ground truth
print(recall_at_k(ranked, rel, 3), precision_at_k(ranked, rel, 3), mrr(ranked, rel), round(ndcg_at_k(ranked, rel, 3), 3))
# 1.0, 0.333..., 0.5, 0.631
```

## 💻 Code Example — Advanced
```python
# Advanced: evaluate several retrievers concurrently over a labelled set, with slices and error handling
import asyncio  # async
import logging  # logs
from collections import defaultdict  # grouping
from statistics import mean  # averages
from typing import Awaitable, Callable  # types

from pydantic import BaseModel  # schema

log = logging.getLogger("retr_eval")  # logger
Retriever = Callable[[str, int], Awaitable[list[str]]]  # (query, k) -> ranked ids


class LabelledQuery(BaseModel):  # one labelled query
    query: str
    relevant: set[str]
    slice: str = "all"  # e.g. 'typo', 'hinglish', 'multi-hop'


async def eval_retriever(name: str, fn: Retriever, data: list[LabelledQuery], k: int = 5) -> dict:
    sem = asyncio.Semaphore(10)  # limit concurrency
    per_slice: dict[str, list[tuple[float, float]]] = defaultdict(list)  # slice -> [(recall, mrr)]
    failures = 0  # count errors

    async def one(q: LabelledQuery) -> None:
        nonlocal failures
        async with sem:
            try:
                ranked = await asyncio.wait_for(fn(q.query, k), timeout=10)  # retrieve
            except Exception as exc:  # retriever failure counts as zero
                log.error("%s failed on %r: %s", name, q.query, exc)
                failures += 1
                ranked = []
            per_slice[q.slice].append((recall_at_k(ranked, q.relevant, k), mrr(ranked, q.relevant)))
            per_slice["ALL"].append(per_slice[q.slice][-1])  # also overall

    await asyncio.gather(*(one(q) for q in data))  # run all queries
    return {"retriever": name, "failures": failures,
            "slices": {s: {"recall@k": round(mean(r for r, _ in v), 3),
                           "mrr": round(mean(m for _, m in v), 3), "n": len(v)}
                       for s, v in per_slice.items()}}  # report


async def compare(retrievers: dict[str, Retriever], data: list[LabelledQuery]) -> list[dict]:
    return await asyncio.gather(*(eval_retriever(n, f, data) for n, f in retrievers.items()))  # all retrievers
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web

app = FastAPI()  # app


async def demo_retriever(q: str, k: int) -> list[str]:  # stub retriever
    return ["8507.60", "8501", "8517"][:k]


@app.post("/eval/retrieval")  # run retrieval evaluation
async def eval_retrieval(data: list[LabelledQuery]) -> list[dict]:
    if not data:  # validate
        raise HTTPException(400, "empty dataset")
    return await compare({"demo": demo_retriever}, data)  # report per retriever
```

---

## 🔗 LangChain / LangGraph Connection
Any LangChain retriever (`retriever.invoke(query)`) can be wrapped into the same function by returning document ids from `metadata`. Ragas context precision/recall add LLM-judged versions when you have no chunk-level labels.

```python
def lc_retriever(retriever):  # adapt a LangChain retriever to our interface
    async def fn(q: str, k: int) -> list[str]:
        docs = await retriever.ainvoke(q)  # async retrieval
        return [d.metadata["chunk_id"] for d in docs][:k]  # ids in ranked order
    return fn
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Judging retrieval only through final answers
✅ Correct: measure retrieval separately

```python
# Wrong
score = llm_judge(final_answer)
# Right
r = recall_at_k(retriever_ids, relevant_ids, k=5)   # fast, deterministic
```

❌ Mistake 2: Re-chunking the corpus and reusing old chunk ids as labels
✅ Correct: label at document/section level or re-map labels after chunking changes.

❌ Mistake 3: Only reporting the mean
✅ Correct: report by slice (typos, Hinglish, multi-hop).

---

## 🧠 Tricky Interview Question
**Q**: "Recall@10 is 0.95 but answers are still often wrong. Why?"

**Answer**: The right chunk is somewhere in the top 10 but the LLM sees noise: relevant chunks are buried at ranks 8-10 ('lost in the middle'), or top ranks are filled with near-duplicates. Check Recall@3/MRR/nDCG and context precision, add a reranker, reduce k, dedupe chunks, and order chunks sensibly. Also check whether the labelled chunk really contains the whole answer.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does Recall@k mean?
A1: The fraction of all relevant chunks that appear in the top-k results.

Q2: [Easy] What does MRR measure?
A2: Average of 1/rank of the first relevant result; rewards putting the answer first.

Q3: [Medium] Recall@k vs Precision@k trade-off?
A3: Larger k raises recall but lowers precision and adds noise tokens (cost, distraction).

Q4: [Medium] Why use nDCG?
A4: It handles graded relevance and position: relevant results lower in the list count less.

Q5: [Hard] How do you evaluate retrieval without chunk-level labels?
A5: Use LLM-judged context relevance/recall (Ragas), synthetic queries generated from known chunks (the source chunk is the label), click/edit logs as weak labels, and periodically verify against a small human-labelled set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing embeddings, chunk size, hybrid search or rerankers
- Debugging whether failures come from retrieval

❌ Avoid when:
- You have no way to define relevance (build labels first)
- Evaluating only end-to-end user satisfaction (add this as a complement, not a replacement)

---

## 📊 Visual Diagram
```
 query ─► retriever ─► ranked ids: [8501, 8507.60, 8517, 8471]
                                      relevant = {8507.60}
   Recall@3 = 1/1 = 1.0
   Precision@3 = 1/3 = 0.33
   MRR = 1/2 = 0.5
   nDCG@3 = (1/log2(3)) / 1 = 0.63
```

---

## 💰 Cost Impact
Metric computation is free (pure Python). Costs come from embedding queries (e.g. 500 queries x 20 tokens on text-embedding-3-small ≈ $0.0002) and any reranker or LLM-labelled relevance. Better retrieval also lowers generation cost: higher precision lets you send fewer chunks (k=3 instead of 8 saves ~60% context tokens).
Optimise: cache embeddings, evaluate retrieval nightly (cheap) and end-to-end weekly (expensive).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recall@k | Relevant found in top-k | Top-k में मिले relevant का अनुपात |
| Precision@k | Top-k that are relevant | Top-k में relevant का अनुपात |
| MRR | Mean reciprocal rank | पहले सही result की औसत 1/rank |
| nDCG | Position-aware gain | Position के हिसाब से gain |
| Reranker | Reorders retrieved chunks | Retrieved chunks को दोबारा क्रम देता है |

---

## ⚡ 3-Line Summary
English: Retrieval evaluation tests the retriever alone with labelled relevant chunks and metrics like Recall@k, MRR and nDCG. It shows whether failures come from retrieval or generation. Report by slice and keep labels in sync with chunking.
Hindi: Retrieval evaluation labelled relevant chunks और Recall@k, MRR, nDCG जैसे metrics से सिर्फ retriever को परखता है। इससे पता चलता है कि गलती retrieval की है या generation की। Slice-wise report दो और labels को chunking के साथ sync रखो।

---

## ➡️ Next Topic
**413. Generation Evaluation** - once retrieval is good, measure the quality of the generated answer.
