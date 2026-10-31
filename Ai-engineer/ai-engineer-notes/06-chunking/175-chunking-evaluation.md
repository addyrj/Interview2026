---

# 175. Chunking Evaluation
# हिंदी में: Chunking Evaluation (chunking की quality नापना)

---

## 🔵 Simple Definition (English)
Chunking evaluation means measuring with numbers whether a chunking strategy helps your RAG system. You build a small set of real questions with known correct answers (or source passages), run retrieval with each strategy, and compare metrics such as recall@k, MRR, precision, answer correctness and token cost. Without this, chunk settings are guesses.

## 🔵 सरल परिभाषा (Hindi)
Chunking evaluation का मतलब है numbers से नापना कि कोई chunking strategy आपके RAG system को सच में बेहतर बना रही है या नहीं। असली questions का छोटा set बनाओ (सही जवाब या source passage के साथ), हर strategy से retrieval चलाओ और recall@k, MRR, precision, answer correctness और token cost compare करो। इसके बिना chunk settings अंदाज़ा हैं।

---

## 🔴 Problem it Solves
- Teams pick chunk_size=1000 "because a tutorial said so" and never learn that 300 would be 15% better.
- Changes (new splitter, new embedding model) silently break retrieval.
- "Looks good" demos hide failures on rare question types (exact HS codes, tables).
- Evaluation turns chunking into an engineering decision with evidence and regression tests.

## 🔴 यह क्यों बना? (Hindi)
- Teams "tutorial में लिखा था" कहकर chunk_size=1000 चुन लेती हैं और कभी नहीं जानतीं कि 300 से 15% बेहतर नतीजा मिलता।
- बदलाव (नया splitter, नया embedding model) चुपचाप retrieval बिगाड़ देते हैं।
- "ठीक दिख रहा है" वाले demos दुर्लभ question types (exact HS codes, tables) की failures छुपाते हैं।
- Evaluation chunking को सबूत-आधारित engineering decision बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect 50-200 real questions (query logs, officers, support tickets)
Step 2 → For each question mark the gold source: document id + the passage/span with the answer
Step 3 → Chunk the corpus with strategy A, B, C (same embedding model, same top_k)
Step 4 → A chunk is a "hit" if it contains (or overlaps) the gold passage
Step 5 → Retrieval metrics: recall@k, MRR, precision@k, hit rate by question type
Step 6 → End-to-end metrics: answer correctness / faithfulness (LLM judge or human spot check)
Step 7 → Cost metrics: average chunk tokens, tokens per query, index size, latency
Step 8 → Pick the best trade-off; keep the eval set in CI to catch regressions
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 50-200 असली questions इकट्ठा करो (query logs, officers, tickets)
Step 2 → हर question का gold source चिह्नित करो: document id + जवाब वाला passage
Step 3 → Strategy A, B, C से corpus chunk करो (वही embedding model, वही top_k)
Step 4 → Chunk "hit" है अगर उसमें gold passage है
Step 5 → Metrics: recall@k, MRR, precision@k, question-type के हिसाब से hit rate
Step 6 → End-to-end: answer correctness / faithfulness
Step 7 → Cost: औसत chunk tokens, tokens प्रति query, index size, latency
Step 8 → सबसे अच्छा trade-off चुनो; eval set को CI में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Golden set = 150 past customs rulings: (product description -> correct HS code + the tariff line text). Compare: (A) 1000-char fixed chunks, (B) one tariff line with breadcrumb, (C) B + chapter notes. Results (illustrative): A recall@5 = 0.62, B = 0.84, C = 0.88; B also uses 40% fewer prompt tokens. The team ships C.

**Amazon style**: Questions from real customer searches; gold = the product page section containing the answer.

## 🟡 Real Example Hindi mein
**Tariff System**: Golden set = 150 पुराने customs rulings: (product description -> सही HS code + tariff line text)। तुलना: (A) 1000-char fixed chunks, (B) breadcrumb सहित एक tariff line, (C) B + chapter notes। नतीजे (उदाहरण): A recall@5 = 0.62, B = 0.84, C = 0.88; B में 40% कम prompt tokens भी लगते हैं। Team C ship करती है।

**Amazon**: असली customer searches से questions; gold = वह product page section जिसमें जवाब है।

---

## 💻 Code Example — Basic
```python
# Basic: compare two chunking strategies with recall@k and MRR (pure Python, keyword retrieval)
import re  # tokenizer

corpus = (  # tiny corpus
    "Smartphones are classified under heading 8517 and attract ten percent duty. "
    "Microphones are classified under heading 8518 and attract seven percent duty. "
    "Batteries are classified under heading 8507 and attract twenty percent duty. "
    "Televisions are classified under heading 8528 and attract fifteen percent duty."
)  # four facts

evalset = [  # (question, gold substring that must appear in a retrieved chunk)
    ("which heading for smartphones", "8517"),
    ("duty on batteries", "twenty percent"),
    ("heading for televisions", "8528"),
]

def by_size(text: str, n: int) -> list[str]:  # fixed-size word chunks
    w = text.split()  # words
    return [" ".join(w[i:i + n]) for i in range(0, len(w), n)]  # slices

def by_sentence(text: str) -> list[str]:  # sentence chunks
    return [s.strip() + "." for s in text.split(".") if s.strip()]  # one per sentence

def retrieve(q: str, chunks: list[str], k: int) -> list[str]:  # keyword-overlap ranking
    qw = set(re.findall(r"[a-z]+", q.lower()))  # query words
    return sorted(chunks, key=lambda c: -len(qw & set(re.findall(r"[a-z]+", c.lower()))))[:k]  # top-k

def evaluate(chunks: list[str], k: int = 1) -> tuple[float, float]:  # returns (recall@k, MRR)
    hits, rr = 0, 0.0  # counters
    for q, gold in evalset:  # each question
        ranked = retrieve(q, chunks, len(chunks))  # full ranking
        pos = next((i for i, c in enumerate(ranked, 1) if gold in c), None)  # first hit position
        hits += 1 if pos is not None and pos <= k else 0  # recall@k
        rr += 1 / pos if pos else 0.0  # reciprocal rank
    return hits / len(evalset), rr / len(evalset)  # averages

for name, chunks in [("size=30 words", by_size(corpus, 30)), ("size=12 words", by_size(corpus, 12)),
                     ("sentence", by_sentence(corpus))]:  # strategies
    r, m = evaluate(chunks, k=1)  # evaluate
    print(f"{name:14} chunks={len(chunks):2} recall@1={r:.2f} MRR={m:.2f}")  # report
```

## 💻 Code Example — Advanced
```python
# Production evaluator: injected async retriever, metrics suite, per-category breakdown, cost proxy.
from __future__ import annotations  # modern hints

import asyncio  # async
import statistics  # mean
from collections import defaultdict  # grouping
from dataclasses import dataclass  # containers
from typing import Awaitable, Callable  # types

Retriever = Callable[[str, int], Awaitable[list[str]]]  # (query, k) -> chunk texts (ranked)


@dataclass
class EvalCase:  # one labelled question
    question: str  # user question
    gold: str  # text that must appear in a relevant chunk
    category: str = "general"  # e.g. "exact_code", "semantic", "table"


@dataclass
class EvalReport:  # aggregated result
    recall_at_k: float  # share of questions with a hit in top-k
    mrr: float  # mean reciprocal rank
    precision_at_k: float  # share of retrieved chunks that are relevant
    avg_chunk_chars: float  # cost proxy
    by_category: dict[str, float]  # recall per category


async def evaluate(cases: list[EvalCase], retrieve: Retriever, k: int = 5) -> EvalReport:
    if not cases:  # validate
        raise ValueError("eval set is empty")  # error
    results = await asyncio.gather(*(retrieve(c.question, k) for c in cases), return_exceptions=True)  # parallel
    hits, rrs, precs, sizes = [], [], [], []  # metric lists
    cat: dict[str, list[int]] = defaultdict(list)  # category -> hit flags
    for case, res in zip(cases, results):  # each case
        if isinstance(res, Exception):  # retrieval failed
            hits.append(0); rrs.append(0.0); precs.append(0.0); cat[case.category].append(0)  # count as a miss
            continue  # next case
        rel = [case.gold.lower() in chunk.lower() for chunk in res]  # relevance flags
        first = rel.index(True) + 1 if any(rel) else None  # first relevant rank
        hits.append(1 if first else 0)  # recall@k
        rrs.append(1 / first if first else 0.0)  # reciprocal rank
        precs.append(sum(rel) / max(1, len(res)))  # precision@k
        sizes += [len(c) for c in res]  # chunk sizes
        cat[case.category].append(1 if first else 0)  # per category
    return EvalReport(statistics.mean(hits), statistics.mean(rrs), statistics.mean(precs),
                      statistics.mean(sizes) if sizes else 0.0,
                      {c: statistics.mean(v) for c, v in cat.items()})  # report


def make_retriever(chunks: list[str]) -> Retriever:  # keyword retriever factory for the demo
    async def retrieve(q: str, k: int) -> list[str]:  # async retriever
        await asyncio.sleep(0)  # pretend I/O
        qw = set(q.lower().split())  # query words
        return sorted(chunks, key=lambda c: -len(qw & set(c.lower().split())))[:k]  # top-k
    return retrieve  # closure


if __name__ == "__main__":  # demo
    text = ["smartphones heading 8517 duty ten percent", "batteries heading 8507 duty twenty percent",
            "televisions heading 8528 duty fifteen percent"]  # chunks
    cases = [EvalCase("heading smartphones", "8517", "exact_code"),
             EvalCase("duty batteries", "twenty percent", "semantic")]  # eval set
    print(asyncio.run(evaluate(cases, make_retriever(text), k=1)))  # report
```

---

## 🟠 FastAPI Integration
Expose evaluation as an internal endpoint (or a CI job) that runs the eval set against a named chunking configuration and returns the report. This makes "which chunking is better?" a button, not a meeting.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app
CONFIGS: dict[str, list[str]] = {  # name -> chunk list (build these from your splitters)
    "sentence": ["smartphones heading 8517 duty ten percent", "batteries heading 8507 duty twenty percent"],
}
EVALSET = [EvalCase("heading smartphones", "8517"), EvalCase("duty batteries", "twenty percent")]  # golden set


class EvalIn(BaseModel):  # request
    config: str  # which chunking configuration
    k: int = Field(default=5, ge=1, le=20)  # top-k


@app.post("/eval/chunking")  # route
async def run_eval(req: EvalIn) -> dict:  # handler
    if req.config not in CONFIGS:  # validate
        raise HTTPException(404, f"unknown config {req.config}")  # not found
    rep = await evaluate(EVALSET, make_retriever(CONFIGS[req.config]), req.k)  # run
    return {"config": req.config, "recall_at_k": rep.recall_at_k, "mrr": rep.mrr,
            "precision_at_k": rep.precision_at_k, "avg_chunk_chars": rep.avg_chunk_chars,
            "by_category": rep.by_category}  # JSON report
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets and evaluators, and libraries such as RAGAS (`context_recall`, `context_precision`, `faithfulness`), can compute these metrics for LangChain retrievers. In LangGraph, add an `evaluate` node after `retrieve` and `generate` for offline runs.

```python
# Retrieval-only evaluation with any LangChain retriever (sync example):
def langchain_recall(retriever, cases: list[tuple[str, str]], k: int = 5) -> float:  # cases: (question, gold)
    hits = 0  # counter
    for q, gold in cases:  # each case
        docs = retriever.invoke(q)[:k]  # LCEL-style retriever call returns list[Document]
        hits += any(gold.lower() in d.page_content.lower() for d in docs)  # hit if gold text is present
    return hits / len(cases)  # recall@k

# RAGAS (sketch): from ragas import evaluate; from ragas.metrics import context_precision, context_recall, faithfulness
# result = evaluate(dataset, metrics=[context_precision, context_recall, faithfulness])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating on questions written by the person who built the chunker
✅ Correct: Use real user questions (logs) and include hard categories (exact codes, tables, multi-hop).

```python
# Wrong - eval questions copied from chunk text (always passes)
cases = [EvalCase(chunk[:40], chunk[:20]) for chunk in chunks]  # leakage

# Right - questions written independently of the chunks
cases = [EvalCase("duty on foldable smartphone", "8517.13")]  # realistic
```

❌ Mistake 2: Judging only recall@k, ignoring tokens and answer quality.
✅ Correct: Report recall, precision, answer correctness and cost together.

❌ Mistake 3: Changing several things (size, overlap, embedding model) at once.
✅ Correct: Change one variable per experiment, fixed top_k and model.

---

## 🧠 Tricky Interview Question
**Q**: "Strategy B has higher recall@5 than strategy A, but the end-to-end answer accuracy is lower. How?"

**Answer**: Recall only says the gold passage is somewhere in the top 5. B may use larger chunks that contain the gold passage but bury it in noise, making the LLM miss it (lost in the middle) or get distracted, while precision drops. Also the gold matching rule may be too lenient (substring in a huge chunk). Evaluate precision, chunk size, and answer correctness (LLM judge plus human spot checks), look at failed cases by category, and consider a reranker or smaller chunks. End-to-end metrics decide; retrieval metrics diagnose.

---

## ⚫ Interview Questions + Answers

Q1: What is recall@k?
A1: The fraction of questions for which at least one relevant chunk appears in the top k results.

Q2: What is MRR?
A2: Mean Reciprocal Rank: average of 1/rank of the first relevant result. It rewards putting the right chunk near the top.

Q3: How big should an eval set be?
A3: Start with 50-100 real questions covering all categories; grow to a few hundred. Even 50 shows large differences.

Q4: How do you label gold passages cheaply?
A4: Use past support tickets or rulings with known answers; or generate synthetic questions from chunks with an LLM and manually review a sample (watch for leakage).

Q5: (Hard) How do you evaluate chunking inside CI without large costs?
A5: Freeze the eval set, use a fixed embedding model (or cached embeddings), run retrieval-only metrics (cheap) on every PR, run LLM-judged end-to-end metrics nightly on a sample, and fail the build when recall@k drops more than a set threshold (for example 2 points) versus the main branch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing or changing chunk size, overlap, splitter, embedding model
- Before and after every big ingestion change
- Production RAG with user-facing accuracy requirements

❌ Avoid heavy evaluation when:
- Early prototype with a handful of documents
- Corpus is tiny and fits in the prompt

---

## 📊 Visual Diagram
```
 questions + gold ─────────────┐
                               ▼
 corpus ─► chunker A ─► index A ─► retrieve ─► metrics A ┐
        ─► chunker B ─► index B ─► retrieve ─► metrics B ├─► compare table
        ─► chunker C ─► index C ─► retrieve ─► metrics C ┘
                                                          │
 metrics:  recall@k  MRR  precision@k  answer-correct  tokens/query  latency
                                                          ▼
                                            choose winner ─► CI regression gate
```

---

## 💰 Cost Impact
- Retrieval-only evaluation is nearly free: embedding the corpus once per strategy (cents) plus query embeddings.
- LLM-judged answer evaluation costs tokens: 200 questions x (3 chunks x 300 tokens + prompt 300 + answer 150 + judge 500) about 400K tokens per run, about $0.06 with a small model at $0.15 per 1M input (output priced higher). Run nightly, not per commit.
- The payoff: choosing a smaller chunk size or a lower top_k that keeps quality can cut prompt tokens by 30-50% in production.
- Optimise: cache embeddings by content hash, sample questions for LLM judging, reuse index builds between experiments.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Labelled questions + answers | जाँच के लिए सही प्रश्न-उत्तर set |
| recall@k | Gold found in top k | Top k में सही chunk मिला |
| MRR | Mean reciprocal rank | सही जवाब की औसत rank का उलटा |
| Precision@k | Relevant share of top k | Top k में काम के chunks का हिस्सा |
| Faithfulness | Answer supported by context | जवाब context पर आधारित |
| Regression test | Detect quality drops | Quality गिरावट पकड़ना |

---

## ⚡ 3-Line Summary
English: Evaluate chunking with a labelled question set and metrics like recall@k, MRR, precision, answer correctness and token cost. Change one variable at a time and keep the eval in CI. Retrieval metrics diagnose; end-to-end accuracy decides.
Hindi: Labelled question set और recall@k, MRR, precision, answer correctness व token cost जैसे metrics से chunking जाँचो। एक बार में एक ही variable बदलो और eval को CI में रखो। Retrieval metrics बीमारी बताते हैं; end-to-end accuracy फैसला करती है।

---

## ➡️ Next Topic
**176. Chunk Size Impact on RAG** - a closer look at how size changes precision, recall, latency and answer quality.
