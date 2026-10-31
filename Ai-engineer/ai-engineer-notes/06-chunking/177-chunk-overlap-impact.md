---

# 177. Chunk Overlap Impact
# हिंदी में: Chunk Overlap का असर

---

## 🔵 Simple Definition (English)
Topic 167 explained how to choose overlap. This topic measures what overlap does to a running RAG system: it raises recall for facts near chunk borders, but also adds storage, embedding tokens, near-duplicate results in top-k and wasted prompt tokens. The impact is positive at small values (10-15%) and turns negative at large values.

## 🔵 सरल परिभाषा (Hindi)
Topic 167 में बताया गया कि overlap कैसे चुनें। यह topic नापता है कि चलते हुए RAG system पर overlap का क्या असर होता है: border के पास वाले facts की recall बढ़ती है, पर storage, embedding tokens, top-k में लगभग-duplicate नतीजे और बेकार prompt tokens भी बढ़ते हैं। छोटे मान (10-15%) पर असर सकारात्मक, बड़े मान पर नकारात्मक।

---

## 🔴 Problem it Solves
- You need to know whether the overlap you set is paying for itself.
- Symptoms: top-5 contains almost the same text three times; index is 40% larger than expected; recall plateaued but cost kept rising.
- Understanding the impact tells you when to raise, lower or replace overlap with other techniques (parent-child, window retrieval, contextual headers).

## 🔴 यह क्यों बना? (Hindi)
- आपको जानना है कि लगाया गया overlap अपना पैसा वसूल कर रहा है या नहीं।
- लक्षण: top-5 में लगभग एक ही text तीन बार; index अपेक्षा से 40% बड़ा; recall रुक गई पर cost बढ़ती रही।
- असर समझने से पता चलता है कि overlap कब बढ़ाना, घटाना या parent-child, window retrieval, contextual headers से बदलना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Overlap makes the last O tokens of chunk n also the first O tokens of chunk n+1
Step 2 → A fact at the border now sits fully inside at least one chunk -> recall up
Step 3 → Total stored tokens = text x size / (size - overlap)  -> storage and embedding cost up
Step 4 → Neighbour chunks share text -> their vectors are similar -> they rank together
Step 5 → Top-k gets near-duplicates -> less diversity, wasted prompt tokens
Step 6 → Gain flattens: after about 10-20% overlap extra overlap adds little recall
Step 7 → Measure: border-question recall, duplicate rate in top-k, index growth, tokens/query
Step 8 → Fix side-effects: dedupe/MMR at query time, or lower overlap and use window retrieval
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Overlap में chunk n के अंतिम O tokens chunk n+1 के पहले O tokens भी बनते हैं
Step 2 → Border का fact कम से कम एक chunk में पूरा आ जाता है -> recall बढ़ती है
Step 3 → कुल stored tokens = text x size / (size - overlap) -> storage और embedding cost बढ़ती है
Step 4 → पड़ोसी chunks का text साझा है -> vectors मिलते-जुलते -> साथ rank होते हैं
Step 5 → Top-k में लगभग-duplicates -> diversity कम, prompt tokens बर्बाद
Step 6 → 10-20% के बाद extra overlap से recall लगभग नहीं बढ़ती
Step 7 → नापो: border-question recall, top-k में duplicate rate, index growth, tokens/query
Step 8 → Side-effects ठीक करो: query पर dedupe/MMR, या overlap घटाकर window retrieval
```

---

## 🟡 Real World Example
**Tariff Classification System**: Evaluate overlap on 120 questions whose answers lie on chunk borders (rule sentence at the end of one chunk, exception at the start of the next). Illustrative result:

| overlap | border recall@5 | index size | duplicates in top-5 |
|---------|-----------------|------------|---------------------|
| 0% | 0.58 | 1.00x | 0.0 |
| 10% | 0.81 | 1.11x | 0.4 |
| 20% | 0.84 | 1.25x | 0.9 |
| 40% | 0.85 | 1.67x | 2.1 |

The gain from 10% to 40% is 4 points but costs 50% more storage and two duplicates in every top-5. The team picks 10-15%.

**Amazon style**: Product Q&A texts with long specs: 10% overlap is enough; with 40% overlap the same spec paragraph is returned 3 times.

## 🟡 Real Example Hindi mein
**Tariff System**: 120 questions पर overlap जाँचा जिनके जवाब chunk border पर हैं (नियम वाला वाक्य एक chunk के अंत में, exception अगले chunk की शुरुआत में)। उदाहरण नतीजा ऊपर की table में है। 10% से 40% तक सिर्फ 4 points का फायदा है पर 50% ज़्यादा storage और हर top-5 में दो duplicates। Team 10-15% चुनती है।

**Amazon**: लंबे specs वाले Product Q&A में 10% overlap काफी है; 40% पर वही spec paragraph 3 बार लौटता है।

---

## 💻 Code Example — Basic
```python
# Basic: measure border recall, storage growth and duplication for different overlap values.
words = ("smartphones attract ten percent duty . this rate does not apply to refurbished units . "
         "batteries attract twenty percent duty . this rate does not apply to damaged cells .").split()  # corpus

def chunks(size: int, overlap: int) -> list[tuple[int, int]]:  # word-index spans
    step = size - overlap  # window step
    return [(i, min(i + size, len(words))) for i in range(0, len(words), step)]  # spans

def border_recall(size: int, overlap: int, fact: tuple[int, int]) -> int:  # is the fact fully inside one chunk?
    return int(any(s <= fact[0] and fact[1] <= e for s, e in chunks(size, overlap)))  # 1 if yes

FACT = (6, 13)  # the exception "this rate does not apply to refurbished" (7 words, crosses a border)
for ov in (0, 2, 4, 6):  # overlaps in words
    cs = chunks(10, ov)  # size 10 words
    stored = sum(e - s for s, e in cs)  # total stored words
    print(f"overlap={ov} chunks={len(cs)} fact_inside_one_chunk={border_recall(10, ov, FACT)} "
          f"storage={stored / len(words):.2f}x")  # report
```

## 💻 Code Example — Advanced
```python
# Production: remove near-duplicate results caused by overlap with MMR-style diversification,
# and report the duplication rate. Pure Python; embedder injected (async).
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # cosine
from typing import Awaitable, Callable  # types

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]  # async embedder


def cosine(a: list[float], b: list[float]) -> float:  # cosine similarity
    d = sum(x * y for x, y in zip(a, b))  # dot
    n = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0  # norms
    return d / n  # similarity


def duplicate_rate(vectors: list[list[float]], threshold: float = 0.9) -> float:  # share of near-duplicate pairs
    pairs = [(i, j) for i in range(len(vectors)) for j in range(i + 1, len(vectors))]  # all pairs
    if not pairs:  # fewer than 2 vectors
        return 0.0  # no duplicates
    dup = sum(1 for i, j in pairs if cosine(vectors[i], vectors[j]) >= threshold)  # count near duplicates
    return dup / len(pairs)  # fraction


def mmr(query_vec: list[float], vecs: list[list[float]], k: int, lam: float = 0.7) -> list[int]:
    """Maximal Marginal Relevance: balance relevance (lam) against redundancy (1 - lam)."""
    if not 0 <= lam <= 1:  # validate
        raise ValueError("lam must be in [0, 1]")  # error
    chosen: list[int] = []  # selected indexes
    candidates = list(range(len(vecs)))  # remaining indexes
    while candidates and len(chosen) < k:  # pick k items
        def score(i: int) -> float:  # MMR score
            rel = cosine(query_vec, vecs[i])  # relevance to query
            red = max((cosine(vecs[i], vecs[j]) for j in chosen), default=0.0)  # redundancy
            return lam * rel - (1 - lam) * red  # trade-off
        best = max(candidates, key=score)  # best candidate
        chosen.append(best)  # select it
        candidates.remove(best)  # remove from pool
    return chosen  # selected order


async def diversified_top_k(query: str, chunks: list[str], embed: Embedder, k: int = 3) -> list[str]:
    try:  # embedding can fail
        qv, *cv = await embed([query, *chunks])  # embed query and chunks together
    except Exception as exc:  # wrap error
        raise RuntimeError("embedding failed") from exc  # message
    first = sorted(range(len(chunks)), key=lambda i: -cosine(qv, cv[i]))[:k * 3]  # shortlist
    picked = mmr(qv, [cv[i] for i in first], k)  # diversify the shortlist
    return [chunks[first[p]] for p in picked]  # final chunks


async def toy_embed(texts: list[str]) -> list[list[float]]:  # demo embedder (letter counts)
    await asyncio.sleep(0)  # async placeholder
    return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # vectors


if __name__ == "__main__":  # demo
    cs = ["smartphones attract ten percent duty this rate does not apply",
          "ten percent duty this rate does not apply to refurbished units",  # heavy overlap with the first
          "batteries attract twenty percent duty"]  # a different topic
    print(asyncio.run(diversified_top_k("smartphone duty rate", cs, toy_embed, k=2)))  # diversified
```

---

## 🟠 FastAPI Integration
Return overlap-impact metrics from a diagnostics endpoint, and apply MMR in the query path so overlap never floods the prompt with duplicates.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app
CHUNKS = ["smartphones attract ten percent duty this rate does not apply",
          "ten percent duty this rate does not apply to refurbished units",
          "batteries attract twenty percent duty"]  # replace with your vector store


class Q(BaseModel):  # request
    question: str  # user question


@app.post("/ask")  # route
async def ask(q: Q) -> dict:  # handler
    try:  # guard embedding failures
        ctx = await diversified_top_k(q.question, CHUNKS, toy_embed, k=2)  # MMR-diversified
    except RuntimeError as exc:  # upstream failure
        raise HTTPException(502, str(exc))  # bad gateway
    vecs = await toy_embed(CHUNKS)  # (cache in production)
    return {"context": ctx, "diagnostics": {"duplicate_rate": round(duplicate_rate(vecs), 3)}}  # metric
```

---

## 🔗 LangChain / LangGraph Connection
LangChain retrievers support MMR directly: `vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.7})`. This is the standard cure for overlap-induced duplicates. In LangGraph put `chunk_overlap` into the config and log duplicate rates in an `evaluate` node.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)  # 10% overlap
# retriever = vectorstore.as_retriever(  # MMR removes near-duplicates created by overlap
#     search_type="mmr", search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.7})
# docs = retriever.invoke("duty on refurbished smartphones")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raising overlap to fix a bad eval score without measuring duplicates
✅ Correct: Track duplicate rate and tokens/query; fix with MMR or smaller overlap.

```python
# Wrong - 50% overlap "just in case"
RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=200)  # 2x storage, duplicate results

# Right - 10-15% plus MMR at query time
RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)  # balanced
```

❌ Mistake 2: Measuring overlap benefit on random questions (most are not on borders).
✅ Correct: Build a border-question subset to see the real effect.

❌ Mistake 3: Re-indexing everything when only overlap changed, without checking cost.
✅ Correct: Estimate tokens first (text x size / (size - overlap)).

---

## 🧠 Tricky Interview Question
**Q**: "You increased overlap and recall@5 went up, but the LLM's answers got longer and contradictory. Why?"

**Answer**: High overlap produces many near-identical chunks, so the top 5 are mostly the same passage with small shifts. The LLM sees repeated or slightly cut versions of one text and fewer distinct sources, so it over-weights it, repeats itself, and may mix partial sentences from different cuts. Recall@5 rose because the gold text appears in several chunks, which inflates the metric. Fix: deduplicate/MMR, lower overlap, return merged neighbouring chunks instead of overlapping ones, and evaluate with precision and answer quality.

---

## ⚫ Interview Questions + Answers

Q1: What is the benefit of overlap?
A1: Facts at chunk borders are kept whole in at least one chunk, which raises recall.

Q2: What is its main cost?
A2: More stored and embedded tokens (size / (size - overlap)) and duplicate-looking results.

Q3: How do you compute the extra storage for 500/50?
A3: 500 / (500 - 50) = 1.11, so about 11% more chunks and tokens.

Q4: How do you remove duplicates in results?
A4: MMR (maximal marginal relevance), a similarity threshold between results, or merging adjacent chunks by id.

Q5: (Hard) When would you set overlap to zero?
A5: For structure-based or atomic chunks (FAQ, tariff lines, reviews), or when you use parent-child, window retrieval or contextual headers that already restore border context.

---

## 🔷 When to Use + When Not to Use
✅ Use small overlap (10-15%) when:
- Continuous prose with cross-sentence dependencies
- Fixed-size or recursive splitting

❌ Avoid large overlap when:
- Chunks are atomic or structure-based
- Storage and prompt tokens are tight
- Retrieval shows duplicate-heavy top-k

---

## 📊 Visual Diagram
```
 overlap 0%   : [AAAA][BBBB][CCCC]            index 1.00x   duplicates: none
 overlap 25%  : [AAAA]                        index 1.33x
                  [ABBB]                      border fact kept whole ✓
                      [BCCC]
 overlap 50%  : [AAAA]
                  [AABB]                      index 2.00x
                    [BBBB]                    neighbours ≈ identical vectors
                      [BBCC]                  -> top-k full of near-duplicates ✗

 recall ▲        ______ plateau
        │   ___/
        │  /
        └──┴──────┴──────┴──► overlap (0% 10% 20% 40%)
```

---

## 💰 Cost Impact
- Extra embedding/storage tokens = size / (size - overlap) - 1. At 10%: +11%; 20%: +25%; 50%: +100%.
- Example: 100M-token corpus at $0.02 per 1M tokens: 10% overlap adds about $0.22, 50% adds $2.00 - small at ingestion, but index storage and vector count also grow, and re-indexing repeats this cost.
- Query cost: duplicates in top-k waste prompt tokens: two duplicate 400-token chunks per query = 800 tokens x 100K queries/day x $0.15/1M = $12/day wasted.
- Optimise: 10-15% overlap, MMR, merge adjacent chunks, content-hash dedupe at ingestion.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Border question | Answer sits at chunk edge | Chunk के किनारे वाला जवाब |
| Duplicate rate | Share of near-identical results | लगभग समान नतीजों का अनुपात |
| MMR | Relevance vs diversity re-ranking | Relevance और विविधता का संतुलन |
| Storage factor | size / (size - overlap) | Storage बढ़ने का गुणक |
| Plateau | Gains stop growing | फायदा रुक जाना |
| Window retrieval | Fetch neighbour chunks | पड़ोसी chunks लाना |

---

## ⚡ 3-Line Summary
English: Overlap raises border recall but adds storage, embedding cost and near-duplicate results. Gains plateau around 10-20%, so more is rarely better. Use MMR or merge adjacent chunks to remove duplicates.
Hindi: Overlap border recall बढ़ाता है पर storage, embedding cost और लगभग-duplicate नतीजे भी बढ़ाता है। फायदा 10-20% पर रुक जाता है, इसलिए ज़्यादा overlap शायद ही बेहतर है। Duplicates हटाने के लिए MMR या adjacent chunks merge करो।

---

## ➡️ Next Topic
**178. Multi-level Chunking** - indexing the same text at several chunk sizes at once.
