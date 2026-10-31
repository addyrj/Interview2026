---

# 105. Euclidean Distance — Complete Guide
# हिंदी में: Euclidean Distance — पूरी Guide

---

## 🔵 Simple Definition (English)
Euclidean distance (also called L2 distance) is the straight-line distance between two points (vectors) in space. Smaller distance means more similar. Unlike cosine, it is affected by vector length as well as direction.

## 🔵 सरल परिभाषा (Hindi)
Euclidean distance (L2 distance) space में दो points (vectors) के बीच की सीधी दूरी है। Distance जितनी कम, उतनी ज़्यादा similarity। Cosine के उलट, यह direction के साथ vector की length से भी प्रभावित होती है।

---

## 🔴 Problem it Solves
Sometimes magnitude matters: two product-feature vectors may point the same way but one is "much stronger". Cosine would call them identical; Euclidean notices the gap. It is also the natural metric for clustering (k-means) and for many ANN indexes (FAISS `IndexFlatL2`).

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी magnitude मायने रखती है: दो vectors same direction में हों पर एक "बहुत ज़्यादा strong" हो। Cosine उन्हें identical कहेगी, Euclidean फर्क पकड़ेगी। Clustering (k-means) और FAISS `IndexFlatL2` में यही metric natural है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take vectors a and b of the same dimension d
Step 2 → Subtract element-wise: diff_i = a_i - b_i
Step 3 → Square each difference: diff_i^2
Step 4 → Sum them: S = sum(diff_i^2)  (this is squared L2, cheaper)
Step 5 → Take square root: dist = sqrt(S)
Step 6 → Smaller dist = more similar; rank ascending
Step 7 → For unit vectors: dist^2 = 2 - 2*cosine, so ranking matches cosine
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Same dimension d के vectors a और b लो
Step 2 → Element-wise अंतर: a_i - b_i
Step 3 → हर अंतर का square
Step 4 → सबका sum S (squared L2, सस्ता)
Step 5 → Square root लो: dist = sqrt(S)
Step 6 → कम dist = ज़्यादा similar; ascending rank करो
Step 7 → Unit vectors के लिए dist^2 = 2 - 2*cosine, यानी ranking cosine जैसी ही
```

---

## 🟡 Real World Example
**Tariff Classification System**: Cluster 100,000 past customs declarations with k-means (uses Euclidean) to discover groups such as "consumer electronics", "textiles", "machinery parts". Each cluster gets a reviewer queue. New declarations are assigned to the nearest cluster centre.

**Amazon-style**: Product vectors that include price and rating features; Euclidean distance finds products that are close in all features at once.

## 🟡 Real Example Hindi mein
**Tariff System**: 1,00,000 पुरानी declarations को k-means (Euclidean) से cluster करो: "electronics", "textiles", "machinery parts"। हर cluster की अलग reviewer queue। नई declaration nearest cluster centre में जाती है।

**Amazon-style**: Product vectors में price और rating features हों तो Euclidean distance उन products को ढूँढती है जो सभी features में close हैं।

---

## 💻 Code Example — Basic
```python
# Pure Python Euclidean distance (runs offline)
import math                                    # for sqrt
from typing import Sequence                    # type hint


def euclidean(a: Sequence[float], b: Sequence[float]) -> float:
    """Return L2 distance between two equal-length vectors."""
    if len(a) != len(b):                       # dimensions must match
        raise ValueError("Vectors must have the same length")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))   # sqrt of squared diffs


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity, to compare behaviour."""
    dot = sum(x * y for x, y in zip(a, b))     # dot product
    na = math.sqrt(sum(x * x for x in a))      # norm a
    nb = math.sqrt(sum(y * y for y in b))      # norm b
    return dot / (na * nb)                     # formula


short = [1.0, 1.0]                             # small vector
long_ = [10.0, 10.0]                           # same direction, 10x longer
print("euclidean:", round(euclidean(short, long_), 3))   # large (12.728)
print("cosine   :", round(cosine(short, long_), 3))      # 1.0 (identical direction)

# Unit vectors: dist^2 == 2 - 2*cos
u = [1.0, 0.0]
v = [math.sqrt(0.5), math.sqrt(0.5)]
print(round(euclidean(u, v) ** 2, 4), round(2 - 2 * cosine(u, v), 4))  # equal
```

## 💻 Code Example — Advanced
```python
# numpy batch L2 search + async embedding + error handling
import asyncio                                 # async runner
import numpy as np                             # vector maths
from numpy.typing import NDArray               # array type hints
from openai import AsyncOpenAI                 # openai>=1 client

client = AsyncOpenAI()                         # key from OPENAI_API_KEY


def nearest_l2(
    query: NDArray[np.float32],                # (d,)
    matrix: NDArray[np.float32],               # (n, d)
    k: int = 3,
) -> list[tuple[int, float]]:
    """k nearest rows by Euclidean distance (smaller is better)."""
    if query.shape[0] != matrix.shape[1]:      # dimension check
        raise ValueError("Dimension mismatch")
    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b  (avoids a big (n,d) temp array)
    d2 = (matrix ** 2).sum(1) + (query ** 2).sum() - 2.0 * matrix @ query
    d2 = np.maximum(d2, 0.0)                   # clamp tiny negatives from rounding
    k = min(k, len(d2))                        # safe k
    idx = np.argsort(d2)[:k]                   # ascending distance
    return [(int(i), float(np.sqrt(d2[i]))) for i in idx]


async def embed(texts: list[str]) -> NDArray[np.float32]:
    """Embed a list of texts; wrap errors in a clear message."""
    try:
        r = await client.embeddings.create(model="text-embedding-3-small", input=texts)
    except Exception as exc:                   # auth / network / rate limit
        raise RuntimeError(f"embedding failed: {exc}") from exc
    return np.asarray([d.embedding for d in r.data], dtype=np.float32)


async def main() -> None:
    docs = ["Smartphones", "Laptops", "Wheat flour"]
    mat = await embed(docs)                    # (3, 1536)
    q = (await embed(["mobile phone"]))[0]     # (1536,)
    for i, dist in nearest_l2(q, mat, k=2):
        print(docs[i], round(dist, 3))         # smaller = closer


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np

app = FastAPI()


class DistanceRequest(BaseModel):
    a: list[float] = Field(min_length=1)       # first vector
    b: list[float] = Field(min_length=1)       # second vector


@app.post("/distance/l2")
async def l2(req: DistanceRequest) -> dict[str, float]:
    if len(req.a) != len(req.b):               # validate dimensions
        raise HTTPException(status_code=422, detail="Dimension mismatch")
    a, b = np.asarray(req.a), np.asarray(req.b)
    return {"l2": float(np.linalg.norm(a - b))}   # straight-line distance
```
Typical use: an internal "clustering" service that compares a new declaration vector with cluster centroids.

---

## 🔗 LangChain / LangGraph Connection
LangChain's FAISS wrapper defaults to **L2** (`DistanceStrategy.EUCLIDEAN_DISTANCE`), and `similarity_search_with_score` returns the distance, where lower is better.

```python
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = FAISS.from_texts(
    ["Smartphones", "Laptops", "Wheat flour"],
    emb,
    distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,   # L2 (default)
)
for doc, dist in store.similarity_search_with_score("mobile phone", k=2):
    print(doc.page_content, dist)               # lower dist = better
```
In LangGraph, a clustering/triage node can use this to route items to different branches.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating a larger score as better
✅ Correct: For L2, **smaller** is better.

```python
# Wrong
best = max(results, key=lambda r: r.distance)
# Right
best = min(results, key=lambda r: r.distance)
```

❌ Mistake 2: Mixing up squared and non-squared L2 in thresholds
✅ Correct: FAISS returns squared L2. Take `sqrt` before comparing with a plain distance threshold.

❌ Mistake 3: Using Euclidean on un-normalised vectors when you only care about meaning
✅ Correct: Normalise vectors first, or use cosine.

---

## 🧠 Tricky Interview Question

**Q**: "Same OpenAI embeddings, but FAISS L2 and cosine give the same top-5 order. Why?"

**Answer**: OpenAI embeddings have length 1. For unit vectors, ||a-b||^2 = 2 - 2cos(a,b), a monotonic decreasing function of cosine, so the ranking is identical. They differ only if vectors are not normalised (e.g. some sentence-transformer models or after averaging vectors).

---

## ⚫ Interview Questions + Answers

Q1: What is Euclidean distance?
A1: The straight-line (L2) distance: sqrt of the sum of squared differences.

Q2: Does smaller or larger mean more similar?
A2: Smaller. 0 means identical vectors.

Q3: When would you pick Euclidean over cosine?
A3: When magnitude is meaningful, for clustering with k-means, or when the index/library is built for L2 (FAISS flat L2).

Q4: Why do ANN libraries use squared L2?
A4: It avoids the sqrt, which is costly and does not change the ranking.

Q5: Why can Euclidean distance degrade in very high dimensions?
A5: "Curse of dimensionality": distances concentrate, so nearest and farthest points look almost equally far. Mitigate with normalisation, dimensionality reduction, and good embedding models, then verify with recall tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Clustering (k-means) embeddings or features
- Magnitude carries meaning
- The vector DB index is L2 by default

❌ Avoid when:
- Vectors are un-normalised text embeddings of different lengths (prefer cosine)
- You need a bounded, interpretable score

---

## 📊 Visual Diagram
```
   y
   |        b (4,5)
   |       /|
   |      / |  dy = 3
   |     /  |
   |    a---+
   |  (1,2)  dx = 3
   +------------------> x

dist = sqrt(dx^2 + dy^2) = sqrt(9+9) = 4.24
```

---

## 💰 Cost Impact
Distance maths is cheap; embedding calls are the paid part (about $0.02 per 1M tokens for `text-embedding-3-small`). Brute-force L2 over n vectors of dimension d costs O(n*d) per query. Optimise using ANN indexes (HNSW, IVF), lower dimensions (`dimensions=512`), float16 or int8 quantisation, and cached query embeddings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Euclidean / L2 distance | Straight-line distance | सीधी रेखा की दूरी |
| Squared L2 | Distance without sqrt | बिना sqrt की distance |
| k-means | Clustering using L2 | L2 आधारित clustering |
| Centroid | Cluster centre vector | Cluster का केंद्र |
| Curse of dimensionality | Distances lose contrast in high d | High dimension में distance का फर्क खो जाना |

---

## ⚡ 3-Line Summary
English: Euclidean distance is the straight-line distance between vectors; smaller means closer. It reacts to length, so for unit vectors it ranks the same as cosine. Use it for clustering and L2-based indexes.
Hindi: Euclidean distance vectors के बीच की सीधी दूरी है; कम = ज़्यादा close। यह length से प्रभावित होती है, unit vectors पर cosine जैसी ranking देती है। Clustering और L2 indexes में use करो।

---

## ➡️ Next Topic
**106. Dot Product Similarity** - the fastest metric, and why it equals cosine for normalised vectors.
