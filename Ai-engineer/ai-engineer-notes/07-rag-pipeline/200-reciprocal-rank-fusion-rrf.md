---

# 200. Reciprocal Rank Fusion (RRF)
# हिंदी में: Reciprocal Rank Fusion (RRF)

---

## 🔵 Simple Definition (English)
Reciprocal Rank Fusion merges several ranked lists into one. Each item gets `sum over lists of 1 / (k + rank)`, where `rank` starts at 1 and `k` is a constant (usually 60). Items that appear high in many lists win. It uses only ranks, so it needs no score normalisation.

## 🔵 सरल परिभाषा (Hindi)
Reciprocal Rank Fusion कई ranked lists को एक में मिलाता है। हर item का score = `सभी lists में 1 / (k + rank) का जोड़`, जहाँ `rank` 1 से शुरू होता है और `k` एक constant (आमतौर पर 60) है। जो items कई lists में ऊपर हैं वे जीतते हैं। यह सिर्फ ranks इस्तेमाल करता है, इसलिए score normalisation नहीं चाहिए।

---

## 🔴 Problem it Solves
BM25 scores (0-30) and cosine similarities (0-1) are not comparable. Weighted-sum fusion needs normalisation that is fragile (outliers, different distributions). RRF ignores raw scores and uses only ordering, which is simple, robust and needs no tuning to work well.

## 🔴 यह क्यों बना? (Hindi)
BM25 scores (0-30) और cosine similarities (0-1) comparable नहीं हैं। Weighted-sum fusion को normalisation चाहिए जो नाज़ुक है (outliers, अलग distributions)। RRF raw scores ignore करके सिर्फ क्रम इस्तेमाल करता है, जो सरल, robust है और बिना tuning के भी अच्छा चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run each retriever; keep only ranked ids (rank 1 = best)
Step 2 → For every id and every list it appears in: add 1 / (k + rank)
Step 3 → Missing from a list = contributes 0 from that list
Step 4 → Sort ids by total score, highest first
Step 5 → Return top-K

Worked example (k = 60):
  BM25 list : [A, B, C]      Dense list: [C, A, D]
  A = 1/61 + 1/62 = 0.01639 + 0.01613 = 0.03252
  C = 1/63 + 1/61 = 0.01587 + 0.01639 = 0.03226
  B = 1/62        = 0.01613
  D = 1/63        = 0.01587
  Final: A, C, B, D
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर retriever चलाओ; सिर्फ ranked ids रखो (rank 1 = सबसे अच्छा)
Step 2 → हर id के लिए, जितनी lists में वह है, उनमें 1 / (k + rank) जोड़ो
Step 3 → किसी list में न हो तो उस list से 0 योगदान
Step 4 → कुल score से sort करो, सबसे ज़्यादा पहले
Step 5 → Top-K लौटाओ

उदाहरण (k = 60): ऊपर के worked example में A पहले, फिर C, B, D।
```

---

## 🟡 Real World Example
**Tariff Classification System**: BM25 ranks the chunk for "8518.30" first; dense ranks the "Bluetooth headsets" explanatory note first and the code chunk third. With k = 60, the code chunk scores `1/61 + 1/63 = 0.0323` (rank 1 in BM25, rank 3 in dense) and the note scores `1/62 + 1/61 = 0.0325` (rank 2 in BM25, rank 1 in dense). Both rise above chunks that only one retriever liked, which is what we want before reranking.
**Zomato AI**: Combine "text relevance", "distance" and "popularity" rankings into one restaurant list using RRF.

## 🟡 Real Example Hindi mein
**Tariff System**: BM25 "8518.30" वाले chunk को पहले रखता है; dense "Bluetooth headsets" वाले explanatory note को पहले और code chunk को तीसरे। RRF दोनों को ऊँचा कर देता है, उन chunks से ऊपर जिन्हें सिर्फ एक retriever ने पसंद किया, और reranking से पहले हमें यही चाहिए।
**Zomato AI**: "text relevance", "distance" और "popularity" rankings को RRF से एक restaurant list में मिलाओ।

---

## 💻 Code Example — Basic
```python
# RRF in a few lines (pure Python), with the worked example from above
from collections import defaultdict
from typing import Dict, Hashable, List, Sequence

def rrf(rank_lists: Sequence[Sequence[Hashable]], k: int = 60) -> List[Hashable]:
    """Fuse ranked lists. rank starts at 1. Returns ids sorted by fused score."""
    scores: Dict[Hashable, float] = defaultdict(float)  # id -> total score
    for ranking in rank_lists:  # each retriever's list
        for rank, item in enumerate(ranking, start=1):  # rank 1 = best
            scores[item] += 1.0 / (k + rank)  # reciprocal rank contribution
    return sorted(scores, key=scores.get, reverse=True)  # high score first

def rrf_with_scores(rank_lists: Sequence[Sequence[Hashable]], k: int = 60) -> Dict[Hashable, float]:
    scores: Dict[Hashable, float] = defaultdict(float)
    for ranking in rank_lists:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
    return dict(sorted(scores.items(), key=lambda kv: -kv[1]))  # ordered dict with scores

if __name__ == "__main__":
    bm25 = ["A", "B", "C"]  # keyword ranking
    dense = ["C", "A", "D"]  # semantic ranking
    print(rrf([bm25, dense]))  # ['A', 'C', 'B', 'D']
    print({i: round(s, 5) for i, s in rrf_with_scores([bm25, dense]).items()})  # A 0.03252, C 0.03226 ...
    print(rrf([bm25, dense], k=1))  # small k: top ranks matter much more
```

## 💻 Code Example — Advanced
```python
# Weighted RRF with ties handling, input validation, dedupe, async fan-out and explainability
import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Hashable, Sequence

logger = logging.getLogger("rrf")  # logger

@dataclass
class Fused:
    id: Hashable  # item id
    score: float  # fused score
    detail: dict[str, int] = field(default_factory=dict)  # retriever name -> rank (explainability)

def weighted_rrf(lists: dict[str, Sequence[Hashable]], weights: dict[str, float] | None = None,
                 k: int = 60, top: int | None = None) -> list[Fused]:
    """lists: retriever name -> ranked ids. Duplicates inside one list count only at their best rank."""
    if k <= 0:
        raise ValueError("k must be positive")  # guard bad config
    weights = weights or {}  # default weight 1.0
    acc: dict[Hashable, Fused] = defaultdict(lambda: Fused(None, 0.0))  # accumulator
    for name, ranking in lists.items():
        seen: set[Hashable] = set()  # per-list dedupe
        w = weights.get(name, 1.0)  # retriever weight
        for rank, item in enumerate(ranking, start=1):
            if item in seen:
                continue  # keep best (first) occurrence only
            seen.add(item)
            f = acc[item]; f.id = item
            f.score += w / (k + rank)  # weighted contribution
            f.detail[name] = rank
    out = sorted(acc.values(), key=lambda f: (-f.score, str(f.id)))  # ties broken deterministically
    return out[:top] if top else out

async def fan_out(retrievers: dict[str, Callable[[str], Awaitable[list[Hashable]]]], query: str,
                  timeout_s: float = 2.0) -> dict[str, list[Hashable]]:
    """Run all retrievers in parallel; failures yield empty lists, not errors."""
    async def one(name: str, fn: Callable[[str], Awaitable[list[Hashable]]]) -> tuple[str, list[Hashable]]:
        try:
            return name, await asyncio.wait_for(fn(query), timeout_s)  # bounded
        except Exception as exc:
            logger.warning("%s failed: %r", name, exc); return name, []
    return dict(await asyncio.gather(*(one(n, f) for n, f in retrievers.items())))

async def _bm25(q: str) -> list[str]: return ["A", "B", "C"]
async def _dense(q: str) -> list[str]: return ["C", "A", "D"]

if __name__ == "__main__":
    lists = asyncio.run(fan_out({"bm25": _bm25, "dense": _dense}, "8518.30"))
    for f in weighted_rrf(lists, weights={"bm25": 1.0, "dense": 1.5}, top=3):
        print(f)  # dense weighted higher -> C may overtake A
```

---

## 🟠 FastAPI Integration
RRF is just a pure function, so a "fusion" step lives inside your search route. Return `detail` (the rank per retriever) when `debug=true` so you can understand ranking problems.

```python
# FastAPI: fuse three rankings (bm25, dense, recency) with RRF
from fastapi import FastAPI, Query

app = FastAPI()  # app

@app.get("/search")
async def search(q: str = Query(min_length=2), k: int = 5, debug: bool = False) -> list[dict]:
    lists = await fan_out({"bm25": bm25_search, "dense": dense_search, "recent": recent_search}, q)  # your async searchers
    fused = weighted_rrf(lists, weights={"bm25": 1.0, "dense": 1.0, "recent": 0.3}, top=k)  # recency weighted low
    return [{"id": f.id, "score": round(f.score, 5), **({"ranks": f.detail} if debug else {})} for f in fused]
```

---

## 🔗 LangChain / LangGraph Connection
`EnsembleRetriever` implements **weighted RRF** internally (it takes `weights` and the constant `c`, default 60). You can also write your own `RunnableLambda` fusion step in LCEL, which is how multi-query retrieval merges its per-query results.

```python
# Custom RRF as an LCEL step, then used after parallel retrievers
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda, RunnableParallel

def fuse(results: dict[str, list[Document]], k: int = 60) -> list[Document]:
    scores: dict[str, float] = {}; docs: dict[str, Document] = {}  # score + doc store
    for lst in results.values():
        for rank, d in enumerate(lst, start=1):
            key = d.page_content  # use a stable id in production (metadata id)
            scores[key] = scores.get(key, 0.0) + 1 / (k + rank); docs[key] = d
    return [docs[x] for x in sorted(scores, key=scores.get, reverse=True)]

bm = RunnableLambda(lambda q: [Document(page_content="A"), Document(page_content="B")])  # stand-in retriever
dn = RunnableLambda(lambda q: [Document(page_content="B"), Document(page_content="C")])  # stand-in retriever
chain = RunnableParallel(bm25=bm, dense=dn) | RunnableLambda(fuse)  # parallel then fuse
print([d.page_content for d in chain.invoke("q")])  # ['B', 'A', 'C']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Starting ranks at 0.
✅ Correct: Rank 1 is the best; using 0 changes the formula (and with k=0 divides by zero).

```python
# Wrong
for rank, item in enumerate(lst): s += 1 / (k + rank)
# Right
for rank, item in enumerate(lst, start=1): s += 1 / (k + rank)
```

❌ Mistake 2: Using different id formats in different lists, so the same chunk is counted as two items.
✅ Correct: Use one stable `chunk_id` across retrievers.

```python
# Wrong
bm25_ids = ["doc12_chunk3"]; dense_ids = ["12-3"]   # same chunk, two spellings
# Right
bm25_ids = ["doc12:3"]; dense_ids = ["doc12:3"]     # one stable id format
```

---

## 🧠 Tricky Interview Question
**Q**: "Why is k = 60 used in RRF, and what happens if you use k = 1 or k = 1000?"

**Answer**: k controls how much top ranks dominate. The contribution at rank 1 vs 2 is 1/(k+1) vs 1/(k+2). With k = 1 that is 0.5 vs 0.33 (a huge gap, top positions dominate and a single list's rank 1 can overrule agreement across lists). With k = 1000 the contributions are almost equal (0.000999 vs 0.000998) so position barely matters and only the count of lists an item appears in counts. k = 60 comes from the original paper (Cormack et al., 2009), found to work robustly across datasets; it is a sensible default and rarely needs tuning.

---

## ⚫ Interview Questions + Answers

Q1: What does RRF stand for and what is the formula?
A1: Reciprocal Rank Fusion; score(d) = sum over rankers of 1 / (k + rank_r(d)), commonly k = 60.

Q2: Why does RRF not need score normalisation?
A2: It only uses ranks, not raw scores, so scales and distributions of different retrievers do not matter.

Q3: What if a document appears in only one list?
A3: It receives a contribution only from that list; it can still rank high if its rank there is 1-3, but docs found by several rankers usually outrank it.

Q4: What are RRF's weaknesses?
A4: It ignores score magnitude (a very confident match and a weak one with the same rank count equally), and cannot express "retriever X is much better" without weights.

Q5: When would you prefer weighted score fusion over RRF?
A5: When scores are calibrated and informative (e.g., same family of models, or you have labeled data to learn weights), you may do better with normalised score fusion or a learned reranker/learning-to-rank. In practice start with RRF, then try a cross-encoder reranker on top; only add score fusion if evals show a gain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Combining BM25 + dense, multi-query results, or multiple indexes
- You want a robust fusion with no training data

❌ Avoid when:
- You have strong calibrated scores and labels (learn the weights)
- Only one retriever (nothing to fuse)

---

## 📊 Visual Diagram
```
 BM25:   1:A  2:B  3:C
 Dense:  1:C  2:A  3:D

 score(A) = 1/(60+1) + 1/(60+2) = 0.03252
 score(C) = 1/(60+3) + 1/(60+1) = 0.03226
 score(B) = 1/(60+2)            = 0.01613
 score(D) = 1/(60+3)            = 0.01587

 Fused ranking:  A > C > B > D
```

---

## 💰 Cost Impact
RRF itself costs no tokens and microseconds of CPU. The cost effect is indirect: it enables cheap multi-retriever and multi-query setups whose combined recall lets you send fewer chunks to the LLM. Multi-query fusion adds one small LLM call (about 150 tokens, 0.00005 USD) but can replace sending 8 chunks "just in case".
Optimize: retrieve N=30 per list, fuse, then rerank only the top 20-30.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rank | Position in a list (1 = best) | List में स्थान |
| k (constant) | Smoothing term in RRF (60) | RRF का smoothing constant |
| Fusion | Merging ranked lists | Lists को मिलाना |
| Weighted RRF | RRF with per-retriever weights | हर retriever के वज़न वाला RRF |
| Score normalisation | Rescaling to compare scores | Scores को तुलनीय बनाना |
| Ensemble | Using several retrievers | कई retrievers का इस्तेमाल |

---

## ⚡ 3-Line Summary
English: RRF scores each item as the sum of 1/(k+rank) across ranked lists, with k = 60.
It is rank-based, so no normalisation is needed, and it is a strong default for hybrid and multi-query search.
Use stable ids and ranks starting at 1.
Hindi: RRF हर item का score ranked lists में 1/(k+rank) का जोड़ लेता है, k = 60।
यह rank आधारित है, इसलिए normalisation नहीं चाहिए, और hybrid व multi-query search के लिए मज़बूत default है।
Stable ids इस्तेमाल करो और ranks 1 से शुरू करो।

---

## ➡️ Next Topic
**201. Multi-Query Retrieval**: generate several rewrites of the question, retrieve for each, and fuse with RRF.
