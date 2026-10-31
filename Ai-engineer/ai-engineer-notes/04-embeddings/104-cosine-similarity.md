---

# 104. Cosine Similarity — Complete Guide
# हिंदी में: Cosine Similarity — पूरी Guide

---

## 🔵 Simple Definition (English)
Cosine similarity measures the **angle** between two vectors, not their length. The result is between -1 and 1: 1 means "pointing the same way" (very similar meaning), 0 means unrelated, -1 means opposite. It is the most common way to compare text embeddings.

## 🔵 सरल परिभाषा (Hindi)
Cosine similarity दो vectors के बीच का **angle** नापती है, उनकी length नहीं। Result -1 से 1 के बीच होता है: 1 = same direction (meaning बहुत similar), 0 = unrelated, -1 = opposite। Text embeddings compare करने का यह सबसे common तरीका है।

---

## 🔴 Problem it Solves
Two embeddings are just lists of numbers. We need a single score that says "how close in meaning are these two texts?". A raw distance is affected by vector length (a long document may have a bigger vector than a short one even if the topic is the same). Cosine ignores length and looks only at direction, so a short query and a long document on the same topic still score high.

## 🔴 यह क्यों बना? (Hindi)
Embeddings सिर्फ numbers की list हैं। हमें एक score चाहिए जो बताए कि दो texts का meaning कितना close है। Raw distance vector की length से प्रभावित होती है। Cosine सिर्फ direction देखती है, इसलिए छोटी query और लंबा document, same topic पर, फिर भी high score पाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Embed text A and text B into vectors a and b (same dimension)
Step 2 → Compute dot product: a·b = sum(a_i * b_i)
Step 3 → Compute lengths (norms): |a| = sqrt(sum(a_i^2)), |b| similarly
Step 4 → cosine = (a·b) / (|a| * |b|)
Step 5 → Score near 1 = similar, near 0 = unrelated, negative = opposite
Step 6 → Rank candidates by score, take top-k
Step 7 → Shortcut: if vectors are already unit length, cosine == dot product
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Text A और B को vectors a, b में embed करो (same dimension)
Step 2 → Dot product निकालो: sum(a_i * b_i)
Step 3 → दोनों की norm (length) निकालो
Step 4 → cosine = dot product / (|a| * |b|)
Step 5 → 1 के पास = similar, 0 = unrelated, negative = opposite
Step 6 → Score से rank करो, top-k लो
Step 7 → Shortcut: vectors पहले से unit length हों तो cosine = dot product
```

---

## 🟡 Real World Example
**Tariff Classification System**: User types "wireless earbuds with charging case". The system embeds the query and compares it with embeddings of 5,000 HS code descriptions using cosine similarity. "8518.30 Headphones and earphones" scores 0.82, "0901.11 Coffee, not roasted" scores 0.05. Top results go to the LLM for final classification.

**Zomato-style**: "spicy paneer dish" matches "Paneer Tikka Masala" by cosine even though the words differ.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "wireless earbuds with charging case"। System query को embed करके 5,000 HS code descriptions से cosine similarity से compare करता है। "8518.30 Headphones and earphones" को 0.82 मिलता है, "Coffee" को 0.05। Top results LLM को जाते हैं।

**Zomato-style**: "spicy paneer dish" का "Paneer Tikka Masala" से match होता है, भले words अलग हों।

---

## 💻 Code Example — Basic
```python
# Pure Python cosine similarity (no libraries needed, runs offline)
import math                                   # math.sqrt for the vector length
from typing import Sequence                   # type hint for list-like inputs


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Return cosine similarity between two equal-length vectors."""
    if len(a) != len(b):                      # vectors must have same dimension
        raise ValueError("Vectors must have the same length")
    dot: float = sum(x * y for x, y in zip(a, b))        # a . b
    norm_a: float = math.sqrt(sum(x * x for x in a))     # |a|
    norm_b: float = math.sqrt(sum(y * y for y in b))     # |b|
    if norm_a == 0.0 or norm_b == 0.0:        # zero vector has no direction
        return 0.0                            # define similarity as 0 in that case
    return dot / (norm_a * norm_b)            # final formula


# Tiny hand-made 3-d "embeddings" to see the behaviour
earbuds = [0.9, 0.1, 0.0]                     # pretend vector for "earbuds"
headphones = [0.8, 0.2, 0.1]                  # similar direction
coffee = [0.0, 0.1, 0.9]                      # very different direction

print(round(cosine_similarity(earbuds, headphones), 3))   # high, close to 1
print(round(cosine_similarity(earbuds, coffee), 3))       # low, close to 0
# Length does not matter: same direction, 10x longer vector
print(round(cosine_similarity(earbuds, [9.0, 1.0, 0.0]), 3))  # exactly 1.0
```

## 💻 Code Example — Advanced
```python
# Production style: numpy, batch scoring, top-k, async embedding
import asyncio                                # for the async version
import numpy as np                            # fast vector maths
from numpy.typing import NDArray              # type hint for arrays
from openai import AsyncOpenAI                # openai>=1.0 async client

client = AsyncOpenAI()                        # reads OPENAI_API_KEY from env


def top_k_cosine(
    query: NDArray[np.float32],               # shape (d,)
    matrix: NDArray[np.float32],              # shape (n, d)
    k: int = 5,                               # how many results to return
) -> list[tuple[int, float]]:
    """Return indices and scores of the k most similar rows."""
    if matrix.ndim != 2 or query.ndim != 1:   # validate shapes
        raise ValueError("query must be 1-D and matrix 2-D")
    q = query / (np.linalg.norm(query) + 1e-12)                       # unit query
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)  # unit rows
    scores = m @ q                            # dot of unit vectors == cosine
    k = min(k, len(scores))                   # do not ask for more than we have
    idx = np.argpartition(-scores, k - 1)[:k]  # fast partial sort
    idx = idx[np.argsort(-scores[idx])]       # sort the k winners
    return [(int(i), float(scores[i])) for i in idx]


async def embed(texts: list[str]) -> NDArray[np.float32]:
    """Embed texts with OpenAI; raises on API failure after logging."""
    try:
        resp = await client.embeddings.create(         # one batched API call
            model="text-embedding-3-small", input=texts
        )
    except Exception as exc:                  # network, auth, rate limit
        raise RuntimeError(f"Embedding failed: {exc}") from exc
    return np.array([d.embedding for d in resp.data], dtype=np.float32)


async def main() -> None:
    docs = ["Headphones and earphones", "Coffee, not roasted", "Mobile phones"]
    doc_vecs = await embed(docs)              # (3, 1536)
    q_vec = (await embed(["wireless earbuds"]))[0]   # (1536,)
    for i, s in top_k_cosine(q_vec, doc_vecs, k=2):
        print(f"{docs[i]!r}: {s:.3f}")        # best matches first


if __name__ == "__main__":
    asyncio.run(main())                       # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Expose a `/similarity` endpoint so other services (or a UI) can compare two texts. The embedding call is async so the event loop is not blocked.

```python
from fastapi import FastAPI, HTTPException    # web framework
from pydantic import BaseModel, Field         # request validation (pydantic v2)
import numpy as np
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()


class SimilarityRequest(BaseModel):
    text_a: str = Field(min_length=1, max_length=8000)   # guard against huge input
    text_b: str = Field(min_length=1, max_length=8000)


@app.post("/similarity")
async def similarity(req: SimilarityRequest) -> dict[str, float | int]:
    try:
        resp = await client.embeddings.create(
            model="text-embedding-3-small", input=[req.text_a, req.text_b]
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))   # upstream error
    a, b = (np.array(d.embedding) for d in resp.data)
    score = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    return {"cosine": round(score, 4), "tokens": resp.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
Vector stores in LangChain (Chroma, FAISS, pgvector) use cosine or inner product under the hood. You can also compute it yourself on `Embeddings` objects.

```python
from langchain_openai import OpenAIEmbeddings
import numpy as np

emb = OpenAIEmbeddings(model="text-embedding-3-small")   # LangChain wrapper
q = np.array(emb.embed_query("wireless earbuds"))        # single query vector
docs = np.array(emb.embed_documents(["Headphones", "Coffee beans"]))  # batch
scores = docs @ q / (np.linalg.norm(docs, axis=1) * np.linalg.norm(q))
print(scores)                                            # cosine per document

# Chroma: choose cosine explicitly
# Chroma.from_texts(texts, emb, collection_metadata={"hnsw:space": "cosine"})
```
In LangGraph, a "retrieve" node typically calls `vectorstore.similarity_search_with_score` and passes the top chunks to the next node.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing vectors from different models
✅ Correct: Always use the same model (and dimension) for query and documents.

```python
# Wrong: 1536-d doc vectors vs 3072-d query vector -> error or meaningless score
# Right: same model name everywhere
MODEL = "text-embedding-3-small"
```

❌ Mistake 2: Confusing cosine similarity with cosine distance
✅ Correct: Chroma/FAISS often return **distance** = 1 - similarity (lower is better).

```python
# Wrong: sorting distance descending (picks the WORST match)
results.sort(key=lambda r: r.score, reverse=True)
# Right: convert first
similarity = 1.0 - distance
```

❌ Mistake 3: Dividing by zero for empty text vectors
✅ Correct: add a small epsilon or return 0.0 when the norm is 0.

---

## 🧠 Tricky Interview Question

**Q**: "Your tariff search returns cosine score 0.78 for a correct HS code and 0.76 for a wrong one. Is a threshold of 0.75 safe?"

**Answer**: No. Cosine scores are not calibrated probabilities. The absolute range depends on the model (OpenAI v3 models rarely give scores above 0.9 even for near duplicates, other models differ). Close scores mean the embedding cannot separate the two codes. Use a re-ranker (cross-encoder) or LLM for the final decision, and set thresholds by evaluating on labelled queries, not by guessing.

---

## ⚫ Interview Questions + Answers

Q1: What range does cosine similarity have?
A1: -1 to 1. For most text embedding models real scores fall between about 0 and 1.

Q2: Why is cosine preferred over Euclidean for text?
A2: It ignores vector length, which is often noise (text length, frequency). Direction carries the meaning.

Q3: If vectors are normalised, what is the relation between cosine and dot product?
A3: They are identical. OpenAI embeddings are normalised to length 1, so a dot product (faster) gives the same ranking as cosine.

Q4: How do cosine similarity and cosine distance relate, and how do vector DBs expose them?
A4: distance = 1 - similarity. Many DBs (Chroma, pgvector `<=>`) return distance where lower is better. Always check docs before sorting or thresholding.

Q5: Cosine search over 50 million vectors is slow. What do you do?
A5: Use approximate nearest neighbour indexes (HNSW, IVF) instead of brute force; normalise vectors so inner product can be used; reduce dimensions (e.g. `dimensions=512` for OpenAI v3) and optionally quantise. Accept small recall loss and measure it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Comparing text embeddings for semantic search or RAG
- Vector lengths are not meaningful
- You need a bounded, easy to read score

❌ Avoid when:
- Magnitude carries information (e.g. recommendation strength) - consider dot product
- Vectors are all-zero or sparse counts where other metrics fit better
- You need calibrated probabilities (cosine is not one)

---

## 📊 Visual Diagram
```
        ^ y
        |      b
        |     /
        |    /  angle θ
        |   /
        |  /__________ a
        +-----------------> x

cosine = cos(θ) = (a . b) / (|a| |b|)

θ = 0°   -> cos = 1   (same meaning)
θ = 90°  -> cos = 0   (unrelated)
θ = 180° -> cos = -1  (opposite)
```

---

## 💰 Cost Impact
Cosine itself is nearly free (CPU maths). Cost comes from creating embeddings: `text-embedding-3-small` is about $0.02 per 1M tokens. A 20-token query costs about $0.0000004. Real cost is in compute at scale: brute force over millions of vectors needs ANN indexes. Optimise by normalising once at write time (so search uses a fast dot product), caching query embeddings, and using smaller dimensions to cut memory.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cosine similarity | Angle based similarity, -1 to 1 | Angle पर आधारित similarity |
| Cosine distance | 1 - cosine similarity | 1 - cosine similarity |
| Norm | Length of a vector | Vector की length |
| Unit vector | Vector with length 1 | Length 1 वाला vector |
| Dot product | Sum of element-wise products | Elements के products का sum |
| ANN | Approximate nearest neighbour search | लगभग सही nearest search |

---

## ⚡ 3-Line Summary
English: Cosine similarity compares the direction of two embedding vectors and ignores their length. Scores are relative, not probabilities, so tune thresholds with real data. With normalised vectors it equals a dot product, which is faster.
Hindi: Cosine similarity दो embedding vectors की direction compare करती है, length नहीं। Scores probabilities नहीं हैं, इसलिए threshold real data से तय करो। Normalised vectors में यह dot product के बराबर है, जो तेज़ है।

---

## ➡️ Next Topic
**105. Euclidean Distance** - the straight-line distance metric; when it differs from cosine and when it is the right choice.
