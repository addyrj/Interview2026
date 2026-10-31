---

# 106. Dot Product Similarity — Complete Guide
# हिंदी में: Dot Product Similarity — पूरी Guide

---

## 🔵 Simple Definition (English)
The dot product multiplies two vectors element by element and adds the results. A bigger number means more similar. It looks at both direction and length. For unit-length vectors it equals cosine similarity, and it is the fastest metric to compute.

## 🔵 सरल परिभाषा (Hindi)
Dot product दो vectors के elements को आपस में multiply करके जोड़ देता है। बड़ा number = ज़्यादा similar। यह direction और length दोनों देखता है। Unit-length vectors के लिए यह cosine similarity के बराबर है, और सबसे तेज़ metric है।

---

## 🔴 Problem it Solves
Cosine needs two extra norm computations per comparison. When you search millions of vectors, that overhead adds up. If vectors are normalised once at indexing time, a plain dot product (a single matrix multiplication, perfect for GPUs/SIMD) gives the same ranking. Also, some models (recommendation, retrieval models like DPR, some Cohere/E5 setups) are trained for dot product, where magnitude encodes importance.

## 🔴 यह क्यों बना? (Hindi)
Cosine में हर comparison पर दो norms अलग से निकालनी पड़ती हैं। Millions vectors में यह बोझ बढ़ता है। Vectors को indexing के समय एक बार normalise कर दो, तो dot product (एक matrix multiplication, GPU के लिए बढ़िया) वही ranking देता है। कुछ models dot product के लिए train होते हैं, जहाँ magnitude का मतलब importance होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Two vectors a, b with the same dimension
Step 2 → Multiply pairwise: a_i * b_i
Step 3 → Add them: score = sum(a_i * b_i)
Step 4 → Higher score = more similar (opposite of distance metrics)
Step 5 → Whole corpus at once: scores = Matrix(n,d) @ query(d)
Step 6 → Pick the top-k scores
Step 7 → If |a| = |b| = 1, score == cosine similarity
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Same dimension के दो vectors a, b
Step 2 → Pairwise multiply: a_i * b_i
Step 3 → सबका sum: score
Step 4 → ज़्यादा score = ज़्यादा similar (distance के उलट)
Step 5 → पूरा corpus एक साथ: Matrix(n,d) @ query(d)
Step 6 → Top-k scores चुनो
Step 7 → |a| = |b| = 1 हो तो score = cosine
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200,000 HS code descriptions and rulings are embedded once, normalised, and stored. Each user query becomes one matrix-vector product, returning scores in milliseconds, with no norm maths at query time.

**Amazon-style recommendation**: User and item vectors are trained so that dot(user, item) predicts a click. A popular item may have a larger magnitude, so it scores higher. Here cosine would remove useful popularity information.

## 🟡 Real Example Hindi mein
**Tariff System**: 2,00,000 HS code descriptions एक बार embed और normalise होकर store होती हैं। हर query एक matrix-vector product बनती है, और milliseconds में scores मिल जाते हैं, norm की गणना की ज़रूरत नहीं।

**Amazon-style recommendation**: User और item vectors ऐसे train होते हैं कि dot(user, item) click predict करे। Popular item की magnitude बड़ी हो सकती है, इसलिए score ज़्यादा। यहाँ cosine popularity की useful information हटा देती।

---

## 💻 Code Example — Basic
```python
# Dot product similarity in pure Python (offline)
import math                                    # sqrt for normalisation demo
from typing import Sequence                    # type hints


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Return the dot product of two equal-length vectors."""
    if len(a) != len(b):                       # shape check
        raise ValueError("length mismatch")
    return sum(x * y for x, y in zip(a, b))    # multiply pairs and add


def normalise(v: Sequence[float]) -> list[float]:
    """Scale a vector to length 1."""
    n = math.sqrt(sum(x * x for x in v))       # vector length
    if n == 0:                                 # avoid division by zero
        raise ValueError("zero vector")
    return [x / n for x in v]                  # divide each element


a = [3.0, 4.0]                                 # length 5
b = [6.0, 8.0]                                 # same direction, length 10
print("raw dot:", dot(a, b))                   # 50.0 (grows with length)
print("unit dot:", round(dot(normalise(a), normalise(b)), 3))  # 1.0 == cosine
c = [4.0, -3.0]                                # perpendicular to a
print("perpendicular:", dot(a, c))             # 0.0 (unrelated)
```

## 💻 Code Example — Advanced
```python
# Fast corpus search with dot product, async embedding, error handling
import asyncio                                 # async runner
import numpy as np                             # matrix maths
from numpy.typing import NDArray
from openai import AsyncOpenAI

client = AsyncOpenAI()


class DotIndex:
    """Tiny in-memory index: stores unit vectors, searches by dot product."""

    def __init__(self) -> None:
        self.texts: list[str] = []             # original texts
        self.matrix: NDArray[np.float32] | None = None   # (n, d) vectors

    def add(self, texts: list[str], vecs: NDArray[np.float32]) -> None:
        """Normalise once at write time (cheap), so search is a pure dot."""
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)       # row norms
        vecs = vecs / np.maximum(norms, 1e-12)                    # avoid /0
        self.texts += texts                                       # keep texts
        self.matrix = vecs if self.matrix is None else np.vstack([self.matrix, vecs])

    def search(self, q: NDArray[np.float32], k: int = 3) -> list[tuple[str, float]]:
        """Return top-k texts by dot product."""
        if self.matrix is None:                # empty index guard
            return []
        q = q / max(float(np.linalg.norm(q)), 1e-12)              # unit query
        scores = self.matrix @ q                                  # one matmul
        top = np.argsort(-scores)[: min(k, len(scores))]          # best first
        return [(self.texts[i], float(scores[i])) for i in top]


async def embed(texts: list[str]) -> NDArray[np.float32]:
    try:
        r = await client.embeddings.create(model="text-embedding-3-small", input=texts)
    except Exception as exc:
        raise RuntimeError(f"embedding failed: {exc}") from exc
    return np.asarray([d.embedding for d in r.data], dtype=np.float32)


async def main() -> None:
    idx = DotIndex()
    docs = ["Smartphones", "Laptop computers", "Wheat flour"]
    idx.add(docs, await embed(docs))           # index once
    q = (await embed(["mobile handset"]))[0]
    print(idx.search(q, k=2))                  # best two


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
import numpy as np

app = FastAPI()
# In a real app, load the normalised matrix once at startup:
MATRIX = np.random.default_rng(0).normal(size=(1000, 64)).astype(np.float32)
MATRIX /= np.linalg.norm(MATRIX, axis=1, keepdims=True)   # unit rows
TEXTS = [f"doc-{i}" for i in range(1000)]


class SearchRequest(BaseModel):
    vector: list[float] = Field(min_length=64, max_length=64)   # query vector
    k: int = Field(default=5, ge=1, le=50)                      # result count


@app.post("/search/dot")
async def search(req: SearchRequest) -> list[dict[str, float | str]]:
    q = np.asarray(req.vector, dtype=np.float32)
    q /= max(float(np.linalg.norm(q)), 1e-12)                   # normalise query
    scores = MATRIX @ q                                         # dot product search
    top = np.argsort(-scores)[: req.k]
    return [{"text": TEXTS[i], "score": float(scores[i])} for i in top]
```

---

## 🔗 LangChain / LangGraph Connection
FAISS `IndexFlatIP` (inner product) is the standard way to get cosine search: normalise vectors, then use inner product. LangChain exposes this as `DistanceStrategy.MAX_INNER_PRODUCT`, and `normalize_L2=True` makes it behave as cosine.

```python
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = FAISS.from_texts(
    ["Smartphones", "Wheat flour"],
    emb,
    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,   # inner product
    normalize_L2=True,                                      # makes it cosine
)
print(store.similarity_search_with_score("mobile phone", k=1))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using dot product on un-normalised vectors and expecting cosine
✅ Correct: Normalise first, or accept that long vectors win.

```python
# Wrong: raw dot, longer vector always wins
score = a @ b
# Right: normalise both
score = (a / np.linalg.norm(a)) @ (b / np.linalg.norm(b))
```

❌ Mistake 2: Sorting ascending (as with distances)
✅ Correct: For dot product, **higher** is better, sort descending.

❌ Mistake 3: Using a metric different from what the model was trained for
✅ Correct: Read the model card (cosine vs dot) and configure the DB to match.

---

## 🧠 Tricky Interview Question

**Q**: "Why does pgvector have three operators (`<->`, `<#>`, `<=>`) and why does `<#>` return negative numbers?"

**Answer**: `<->` is L2 distance, `<=>` cosine distance, `<#>` the **negative** inner product. Postgres index scans only return results in ascending order, so pgvector negates the inner product so that "smaller is better" like the other operators. Multiply by -1 to get the real dot product.

---

## ⚫ Interview Questions + Answers

Q1: What is the dot product of two vectors?
A1: The sum of the element-wise products. Larger means more aligned and/or longer.

Q2: How does it relate to cosine similarity?
A2: cosine = dot / (|a||b|). For unit vectors both are equal.

Q3: Why do many systems normalise embeddings and use dot product?
A3: Normalising once at write time removes norm computation at query time, and dot product maps to fast BLAS/GPU matrix multiplication.

Q4: When is magnitude information useful?
A4: In recommendation or models trained with inner product, where bigger norm means popularity/confidence. Normalising would throw that away.

Q5: How do you choose a metric when a model card does not say?
A5: Test on a labelled query set: compute recall@k for cosine, dot, and L2. For normalised outputs they agree, so choose dot for speed. For un-normalised outputs, prefer the metric used in the model's training or benchmark.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Vectors are normalised (equals cosine, fastest)
- The model was trained with inner product
- Magnitude should influence ranking

❌ Avoid when:
- Vectors have arbitrary lengths and you only want semantic angle
- Interpreting scores as bounded similarity (-1..1) without normalising

---

## 📊 Visual Diagram
```
a = [a1, a2, a3]
b = [b1, b2, b3]
      x    x    x
    (a1*b1)+(a2*b2)+(a3*b3) = score

Corpus search:
  [ n x d matrix ] @ [ d query ] = [ n scores ] -> top-k
  one matrix multiplication, no sqrt, no division
```

---

## 💰 Cost Impact
No API cost for the metric itself. It lowers compute/latency: a single matmul over 1M x 1536 float32 vectors is roughly 6 GB of memory traffic, so use ANN indexes and smaller dimensions. Quantising to int8 cuts memory 4x. Embedding cost stays about $0.02 per 1M tokens (`text-embedding-3-small`), so cache the query embeddings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dot product | Sum of element products | Elements के products का sum |
| Inner product (IP) | Same as dot product | Dot product का दूसरा नाम |
| Normalisation | Scale vector to length 1 | Vector को length 1 करना |
| MIPS | Maximum inner product search | सबसे बड़ा inner product खोजना |
| BLAS | Fast linear algebra library | तेज़ linear algebra library |

---

## ⚡ 3-Line Summary
English: Dot product multiplies and sums vector elements; bigger means more similar. With normalised vectors it is exactly cosine, but faster. Use it when vectors are normalised or when magnitude matters.
Hindi: Dot product vectors के elements को multiply करके जोड़ता है; बड़ा = ज़्यादा similar। Normalised vectors में यह cosine ही है, पर तेज़। Vectors normalised हों या magnitude मायने रखे तो use करो।

---

## ➡️ Next Topic
**107. OpenAI Embeddings API** - now that we know the metrics, learn how to actually generate vectors.
