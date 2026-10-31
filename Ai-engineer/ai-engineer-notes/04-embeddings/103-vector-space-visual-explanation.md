---

# 103. Vector Space — Visual Explanation
# हिंदी में: Vector Space — Visual Explanation

---

## 🔵 Simple Definition (English)
A vector space is a space where every text is a point (an arrow from the origin) with many coordinates, for example 1536 numbers. Similar meanings are nearby points; different meanings are far apart. We cannot draw 1536 dimensions, but the idea is the same as points on a 2D map: distance and direction carry meaning.

## 🔵 सरल परिभाषा (Hindi)
Vector space ऐसी space है जहाँ हर text एक point (origin से तीर) है जिसके कई coordinates हैं, जैसे 1536 numbers। समान मतलब वाले points पास-पास होते हैं; अलग मतलब वाले दूर। हम 1536 dimensions नहीं बना सकते, पर idea वही है जो 2D नक्शे के points का है: दूरी और दिशा में मतलब होता है।

---

## 🔴 Problem it Solves
"Meaning" is abstract. To search, cluster or compare, we need something we can calculate. A vector space turns "how similar are these two texts?" into a simple measurement (distance or angle). It also lets us visualise our data (e.g. a 2D map of all tariff codes) to debug retrieval.

## 🔴 यह क्यों बना? (Hindi)
"मतलब" अमूर्त है। Search, cluster या compare करने के लिए हमें calculate करने लायक कुछ चाहिए। Vector space "ये दो texts कितने समान हैं?" को सरल माप (distance या angle) में बदल देती है। इससे हम अपने data को visualise भी कर सकते हैं (जैसे सारे tariff codes का 2D नक्शा) ताकि retrieval debug हो सके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Embedding model maps each text to a vector v = [x1, x2, ..., xN]
Step 2 → Each vector is a point in N-dimensional space
Step 3 → Distance measures: Euclidean (straight line), cosine (angle), dot product
Step 4 → Normalised vectors (length 1): cosine = dot product, so search is fast
Step 5 → Nearby points form clusters (electronics, food, footwear ...)
Step 6 → Directions can carry meaning: king - man + woman ≈ queen (in word vectors)
Step 7 → To SEE it: reduce N dims to 2 with PCA / t-SNE / UMAP and plot
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Embedding model हर text को vector v = [x1, x2, ..., xN] में बदलता है
Step 2 → हर vector N-dimensional space में एक point है
Step 3 → दूरी के माप: Euclidean (सीधी रेखा), cosine (angle), dot product
Step 4 → Normalised vectors (लंबाई 1): cosine = dot product, इसलिए search तेज़
Step 5 → पास-पास के points clusters बनाते हैं (electronics, food, footwear ...)
Step 6 → दिशाएँ भी मतलब रखती हैं: king - man + woman ≈ queen (word vectors में)
Step 7 → इसे देखने के लिए: PCA / t-SNE / UMAP से N dims को 2 में घटाओ और plot करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Plot 5,000 tariff descriptions in 2D. You see islands: chapter 85 (electrical) forms one island, chapter 64 (footwear) another. A query "wireless earbuds" lands inside the electrical island next to codes 8518.xx. When a query lands between islands (e.g. "smart shoes with sensors"), that signals ambiguity, so route to review.

**Zomato-style**: Dish embeddings cluster by cuisine; "paneer butter masala" sits near "palak paneer", far from "sushi".

## 🟡 Real Example Hindi mein
**Tariff System**: 5,000 tariff descriptions को 2D में plot करो। आपको द्वीप (islands) दिखते हैं: chapter 85 (electrical) एक द्वीप, chapter 64 (footwear) दूसरा। Query "wireless earbuds" electrical द्वीप में 8518.xx codes के पास गिरती है। जब query दो द्वीपों के बीच गिरे (जैसे "smart shoes with sensors"), तो यह अस्पष्टता का संकेत है, इसलिए review में भेजो।

**Zomato-style**: Dish embeddings cuisine के हिसाब से cluster बनाते हैं; "paneer butter masala" "palak paneer" के पास, "sushi" से दूर।

---

## 💻 Code Example — Basic
```python
# Basic: a 2D vector space by hand; distances, cosine and nearest neighbour + ASCII scatter plot.
# Pure Python, no libraries.
import math

# Hand-made 2D "embeddings": x = electronic-ness, y = food-ness (real models have ~1536 learned dims)
points: dict[str, tuple[float, float]] = {
    "earbuds":    (0.95, 0.05),
    "headphones": (0.90, 0.10),
    "smartphone": (0.85, 0.05),
    "banana":     (0.05, 0.95),
    "mango":      (0.10, 0.90),
    "biryani":    (0.15, 0.85),
}

def euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.dist(a, b)                              # straight-line distance

def cosine(a: tuple[float, float], b: tuple[float, float]) -> float:
    dot = a[0] * b[0] + a[1] * b[1]
    return dot / (math.hypot(*a) * math.hypot(*b))      # angle-based similarity

def nearest(query: tuple[float, float], k: int = 2) -> list[tuple[str, float]]:
    """k nearest neighbours by cosine similarity."""
    ranked = sorted(((n, cosine(query, p)) for n, p in points.items()), key=lambda t: t[1], reverse=True)
    return ranked[:k]

query = (0.92, 0.08)                                    # pretend: embedding of "bluetooth earphones"
print("nearest:", [(n, round(s, 3)) for n, s in nearest(query)])
print("dist earbuds-headphones:", round(euclidean(points["earbuds"], points["headphones"]), 3))
print("dist earbuds-banana    :", round(euclidean(points["earbuds"], points["banana"]), 3))

# ASCII scatter plot: 20 columns x 10 rows
W, H = 20, 10
grid = [["." for _ in range(W)] for _ in range(H)]
for name, (x, y) in points.items():
    col, row = min(W - 1, int(x * W)), min(H - 1, int((1 - y) * H))     # y flipped for screen
    grid[row][col] = name[0].upper()                    # first letter marks the point
qx, qy = query
grid[min(H - 1, int((1 - qy) * H))][min(W - 1, int(qx * W))] = "*"   # query star
print("\n".join("".join(r) for r in grid))
```

## 💻 Code Example — Advanced
```python
# Production-style: normalise vectors, brute-force top-K with numpy-free code, PCA-to-2D via power iteration.
# Pure Python so it runs anywhere; in production use numpy / a vector DB (FAISS, pgvector).
import asyncio
import math
import random
from typing import Sequence

Vector = list[float]

def normalize(v: Sequence[float]) -> Vector:
    """Scale to length 1 so dot product == cosine similarity."""
    n = math.sqrt(sum(x * x for x in v))
    if n == 0:
        raise ValueError("zero vector cannot be normalised")
    return [x / n for x in v]

def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

class VectorIndex:
    """Tiny in-memory index with cosine top-K search."""
    def __init__(self) -> None:
        self.keys: list[str] = []
        self.vecs: list[Vector] = []

    def add(self, key: str, vec: Sequence[float]) -> None:
        self.keys.append(key)
        self.vecs.append(normalize(vec))                # store normalised

    async def search(self, query: Sequence[float], k: int = 3) -> list[tuple[str, float]]:
        await asyncio.sleep(0)                          # keep the API async like a real DB client
        q = normalize(query)
        scores = [(key, dot(q, v)) for key, v in zip(self.keys, self.vecs)]
        return sorted(scores, key=lambda t: t[1], reverse=True)[:k]

def pca_2d(vectors: list[Vector], iters: int = 50) -> list[tuple[float, float]]:
    """Project vectors to 2D with the top-2 principal components (power iteration)."""
    n, d = len(vectors), len(vectors[0])
    mean = [sum(v[i] for v in vectors) / n for i in range(d)]
    X = [[v[i] - mean[i] for i in range(d)] for v in vectors]          # centre the data
    comps: list[Vector] = []
    for _ in range(2):
        w = normalize([random.random() + 0.1 for _ in range(d)])       # random start
        for _ in range(iters):
            xw = [dot(row, w) for row in X]                            # X w
            w_new = [sum(xw[r] * X[r][j] for r in range(n)) for j in range(d)]   # X^T (X w)
            for c in comps:                                            # remove earlier component
                proj = dot(w_new, c)
                w_new = [a - proj * b for a, b in zip(w_new, c)]
            w = normalize(w_new)
        comps.append(w)
    return [(dot(row, comps[0]), dot(row, comps[1])) for row in X]

async def main() -> None:
    random.seed(0)
    index = VectorIndex()
    data = {"earbuds": [0.9, 0.1, 0.0, 0.1], "headphones": [0.8, 0.2, 0.1, 0.0],
            "banana": [0.0, 0.1, 0.9, 0.2], "mango": [0.1, 0.0, 0.8, 0.3]}
    for k, v in data.items():
        index.add(k, v)
    print(await index.search([0.85, 0.15, 0.05, 0.05], k=2))           # electronics first
    print(pca_2d(list(data.values())))                                  # 2D coordinates to plot

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
index = VectorIndex()                                    # from the advanced example (use a vector DB in prod)

class SearchIn(BaseModel):
    vector: list[float]
    k: int = 3

@app.post("/vectors/search")
async def vectors_search(body: SearchIn) -> dict:
    if not index.keys:
        raise HTTPException(status_code=409, detail="index is empty")
    try:
        hits = await index.search(body.vector, body.k)
    except ValueError as exc:                            # zero vector
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"hits": [{"key": k, "score": round(s, 4)} for k, s in hits]}
# Real endpoint: embed the query text with the SAME model used for documents, then search.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS       # pip install faiss-cpu langchain-community

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = FAISS.from_texts(["Headphones and earphones", "Bananas, fresh or dried"], emb)
for doc, score in store.similarity_search_with_score("wireless earbuds", k=2):
    print(doc.page_content, score)                       # FAISS returns a DISTANCE: smaller is closer
# LangGraph retrieve node: store.as_retriever(search_kwargs={"k": 5}).ainvoke(query)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting 2D plots as exact truth
✅ Correct: PCA/t-SNE/UMAP distort distances; use plots for intuition, rely on real-dimension metrics for decisions.

```python
# Wrong: "points look far in the t-SNE plot so similarity is low"
# Right: compute cosine in the original vector space
```

❌ Mistake 2: Mixing up distance and similarity
✅ Correct: Higher cosine similarity is better; smaller distance is better.

```python
# Wrong: sorted(scores, reverse=False) on cosine similarity  # worst first
# Right: cosine -> reverse=True ; euclidean distance -> reverse=False
```

---

## 🧠 Tricky Interview Question

**Q**: "In a 1536-dimensional space, why do all points seem about equally far from each other, and does that break similarity search?"

**Answer**: This is the "curse of dimensionality": in very high dimensions, distances concentrate, so the gap between the nearest and farthest neighbour shrinks for random data. Embeddings from trained models are not random: they lie on a much lower-dimensional manifold, so meaningful differences still exist and cosine search works well. But it explains why normalisation, good models, approximate nearest-neighbour indexes (HNSW) and reranking are used, and why raw Euclidean distance on unnormalised vectors can mislead.

---

## ⚫ Interview Questions + Answers

Q1: What is a vector?
A1: An ordered list of numbers; here, the coordinates of a text in embedding space.

Q2: Cosine similarity vs Euclidean distance?
A2: Cosine measures the angle (direction), ignoring length; Euclidean measures straight-line distance. For normalised vectors they give the same ranking.

Q3: Why normalise embeddings?
A3: Makes dot product equal cosine similarity, which is faster to compute and makes scores comparable.

Q4: How can you visualise embeddings?
A4: Reduce dimensions with PCA, t-SNE or UMAP and scatter-plot; colour by label to see clusters.

Q5: What is approximate nearest neighbour (ANN) search and why is it needed?
A5: Exact search compares the query to every vector (O(N)). ANN indexes like HNSW or IVF trade a little recall for big speed gains, enabling millisecond search over millions of vectors; tune recall vs latency, and measure recall against brute force on a sample.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging retrieval by looking at clusters
- Explaining embeddings to stakeholders
- Anomaly/duplicate detection

❌ Avoid when:
- Making decisions from 2D plots alone
- Exact lookups (use a normal index)

---

## 📊 Visual Diagram
```
 electronic-ness ▲
        1.0 ┤  ● earbuds  ● headphones
            │     ● smartphone         ★ query "bluetooth earphones"
            │
        0.5 ┤
            │                      ■ biryani
            │           ■ mango
        0.0 ┼──────■ banana─────────────────► food-ness
            0                              1.0

 Distance: ★ to ● small  →  similar meaning
           ★ to ■ large  →  different meaning
 Angle (cosine) compares direction from the origin: same direction = similar.
```

---

## 💰 Cost Impact
Vector size drives storage and speed: 1536 floats x 4 bytes = ~6 KB per vector; 1M vectors = ~6 GB raw. Search cost grows with dimensions and number of vectors; the embedding API call itself is cheap per token.
Optimise: shorter vectors (`dimensions=512/256` on text-embedding-3), quantisation (int8/binary), ANN indexes (HNSW), normalise and use dot product, store vectors in a managed vector DB or pgvector, and embed each document only once.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vector | List of numbers | Numbers की list |
| Dimension | Number of coordinates | Coordinates की संख्या |
| Cosine similarity | Angle-based similarity | Angle वाली समानता |
| Euclidean distance | Straight-line distance | सीधी रेखा की दूरी |
| Normalisation | Scale to length 1 | लंबाई 1 करना |
| Cluster | Group of nearby points | पास-पास के points का समूह |
| ANN / HNSW | Fast approximate search | तेज़ अनुमानित search |
| PCA / t-SNE | Reduce to 2D for plotting | Plot के लिए 2D में घटाना |

---

## ⚡ 3-Line Summary
English: Every text becomes a point in high-dimensional space where distance and angle mean similarity. Normalise vectors, use cosine/dot product and ANN indexes for speed. 2D plots help intuition but do not replace real metrics.
Hindi: हर text high-dimensional space का एक point बनता है जहाँ दूरी और angle का मतलब समानता है। Vectors normalise करो, तेज़ी के लिए cosine/dot product और ANN indexes use करो। 2D plots समझ देते हैं पर असली metrics की जगह नहीं लेते।

---

## ➡️ Next Topic
**104. Embedding Models Comparison** — choosing between OpenAI, Cohere, open-source models by quality, dimension and price.
