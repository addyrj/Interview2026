---

# 109. Embedding Dimensions — Complete Guide
# हिंदी में: Embedding Dimensions — पूरी Guide

---

## 🔵 Simple Definition (English)
The dimension of an embedding is how many numbers are in the vector (for example 384, 768, 1536, 3072). More dimensions can store more detail about meaning but cost more memory, storage, and search time. Every vector in one index must have the same dimension.

## 🔵 सरल परिभाषा (Hindi)
Embedding की dimension मतलब vector में कितने numbers हैं (जैसे 384, 768, 1536, 3072)। ज़्यादा dimensions में meaning की ज़्यादा detail आ सकती है, पर memory, storage और search time भी बढ़ता है। एक index के सारे vectors की dimension same होनी चाहिए।

---

## 🔴 Problem it Solves
Storing 100M vectors of 3072 floats takes about 1.1 TB of RAM-equivalent data. Teams needed a way to trade a small amount of accuracy for large savings. Understanding dimensions lets you size infrastructure, pick models, and shorten vectors (Matryoshka representation learning in OpenAI v3, Cohere v4, etc.) without retraining.

## 🔴 यह क्यों बना? (Hindi)
3072 floats वाले 10 करोड़ vectors लगभग 1.1 TB data होते हैं। Teams को थोड़ी accuracy देकर बहुत बचत करनी थी। Dimensions समझने से आप infrastructure size कर सकते हैं, model चुन सकते हैं, और बिना retrain किए vectors छोटे कर सकते हैं (Matryoshka)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Model outputs a fixed-length vector (d numbers)
Step 2 → Each dimension is a learned feature (not human readable)
Step 3 → Memory per vector = d x bytes per number (float32 = 4, float16 = 2, int8 = 1)
Step 4 → Search cost grows roughly linearly with d
Step 5 → Matryoshka models pack the most important info first
Step 6 → Truncate to first N dims, then RE-NORMALISE to unit length
Step 7 → Or use API param: dimensions=N (OpenAI v3)
Step 8 → Evaluate recall at each N and choose the knee of the curve
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model fixed-length vector (d numbers) देता है
Step 2 → हर dimension एक learned feature है (इंसान को समझ नहीं आता)
Step 3 → Memory प्रति vector = d x bytes (float32 = 4, float16 = 2, int8 = 1)
Step 4 → Search cost लगभग d के साथ linear बढ़ती है
Step 5 → Matryoshka models ज़रूरी जानकारी पहले dims में रखते हैं
Step 6 → पहले N dims लो, फिर unit length में RE-NORMALISE करो
Step 7 → या API param: dimensions=N (OpenAI v3)
Step 8 → हर N पर recall नापो और सबसे अच्छा point चुनो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 5M tariff rulings and past declarations. At 3072 d float32 that is 61 GB; at 1024 d it is 20 GB; at 512 d int8 it is 2.5 GB, which fits on a small vector DB instance. Evaluation shows recall@10 drops only 1.5% going from 3072 to 1024, so 1024 is chosen.

**Zomato-style**: 384-d MiniLM vectors for 10M dishes run on a cheap server with sub-10ms search.

## 🟡 Real Example Hindi mein
**Tariff System**: 50 लाख tariff rulings और पुरानी declarations। 3072 d float32 में 61 GB; 1024 d में 20 GB; 512 d int8 में 2.5 GB, जो छोटे vector DB instance में आ जाता है। Evaluation में 3072 से 1024 पर recall@10 सिर्फ 1.5% गिरा, इसलिए 1024 चुना।

**Zomato-style**: 10M dishes के लिए 384-d MiniLM vectors सस्ते server पर 10ms से कम में search।

---

## 💻 Code Example — Basic
```python
# Memory sizing + safe truncation (pure Python, runs offline)
import math                                    # sqrt for norm
from typing import Sequence


def memory_gb(n_vectors: int, dims: int, bytes_per_value: int = 4) -> float:
    """GB needed to store n vectors (no index overhead)."""
    return n_vectors * dims * bytes_per_value / 1024 ** 3


def truncate_and_normalise(vec: Sequence[float], dims: int) -> list[float]:
    """Keep the first `dims` values and rescale to unit length."""
    if dims <= 0 or dims > len(vec):           # validate requested size
        raise ValueError("dims out of range")
    cut = list(vec[:dims])                     # take leading dimensions
    norm = math.sqrt(sum(x * x for x in cut))  # new length
    if norm == 0:
        raise ValueError("zero vector after truncation")
    return [x / norm for x in cut]             # back to unit length


for d in (384, 768, 1024, 1536, 3072):
    print(d, "dims ->", round(memory_gb(1_000_000, d), 2), "GB per 1M vectors (float32)")

demo = [0.5, 0.5, 0.5, 0.5]                    # pretend 4-d embedding
short = truncate_and_normalise(demo, 2)
print(short, "length:", round(math.sqrt(sum(x * x for x in short)), 3))  # 1.0
```

## 💻 Code Example — Advanced
```python
# Find the smallest dimension that keeps recall within 2% of the full vector
import asyncio
import numpy as np
from numpy.typing import NDArray
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def embed(texts: list[str], dims: int | None = None) -> NDArray[np.float32]:
    kwargs: dict = {"model": "text-embedding-3-large", "input": texts}
    if dims:
        kwargs["dimensions"] = dims            # API shortens and renormalises
    try:
        r = await client.embeddings.create(**kwargs)
    except Exception as exc:
        raise RuntimeError(f"embed failed: {exc}") from exc
    return np.asarray([d.embedding for d in r.data], dtype=np.float32)


def recall(d_vec: NDArray[np.float32], q_vec: NDArray[np.float32],
           truth: list[int], k: int = 5) -> float:
    scores = q_vec @ d_vec.T                   # cosine because vectors are unit length
    top = np.argsort(-scores, axis=1)[:, :k]
    return float(np.mean([t in row for t, row in zip(truth, top)]))


async def pick_dimension(docs: list[str], queries: list[str], truth: list[int],
                         candidates: tuple[int, ...] = (256, 512, 1024, 3072),
                         tolerance: float = 0.02) -> int:
    """Return the smallest candidate dim within `tolerance` of the best recall."""
    results: dict[int, float] = {}
    for d in candidates:                       # evaluate each size
        dv, qv = await asyncio.gather(embed(docs, d), embed(queries, d))
        results[d] = recall(dv, qv, truth)
    best = max(results.values())
    for d in sorted(results):                  # smallest first
        if results[d] >= best - tolerance:
            return d
    return max(results)                        # fallback


if __name__ == "__main__":
    docs = ["Earphones", "Coffee beans", "Mobile phone", "Wheat flour"]
    print(asyncio.run(pick_dimension(docs, ["earbuds", "smartphone"], [0, 2])))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class SizingRequest(BaseModel):
    vectors: int = Field(gt=0)                 # how many vectors
    dims: int = Field(gt=0, le=4096)           # dimension
    bytes_per_value: int = Field(default=4, ge=1, le=4)   # 4=float32, 2=fp16, 1=int8


@app.post("/capacity-plan")
async def capacity_plan(req: SizingRequest) -> dict[str, float]:
    gb = req.vectors * req.dims * req.bytes_per_value / 1024 ** 3
    return {"raw_gb": round(gb, 2), "with_hnsw_overhead_gb": round(gb * 1.5, 2)}
```
This helps ops estimate Qdrant/pgvector memory before choosing a model or dimension. (The 1.5x HNSW overhead is a rough rule of thumb; measure your index.)

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)
print(len(emb.embed_query("test")))            # 1024
```
The vector store must be created with the same dimension (e.g. PGVector table `vector(1024)`). If you change dimensions, you must rebuild the collection. In LangGraph, keep the embedding config in one settings object shared by the ingestion and retrieval graphs.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating the DB column with the wrong dimension
✅ Correct: Match model output exactly.

```sql
-- Wrong: embedding vector(1536) but you insert 3072-d vectors -> error
-- Right: vector(3072) or request dimensions=1536
```

❌ Mistake 2: Truncating a non-Matryoshka model (e.g. MiniLM, 384 -> 128)
✅ Correct: Only truncate models trained for it (OpenAI v3, nomic, Cohere v4, some Voyage); otherwise use PCA and evaluate.

❌ Mistake 3: Believing higher dimension is always more accurate
✅ Correct: Beyond a point gains are tiny; evaluate.

---

## 🧠 Tricky Interview Question

**Q**: "You reduced vectors from 3072 to 256 by slicing `vec[:256]` and search got worse than expected. Why?"

**Answer**: The sliced vector is no longer unit length, so cosine/dot comparisons are skewed, and the vector may differ from what the API's `dimensions=256` produces (which renormalises). Re-normalise after slicing. Also verify that the model supports Matryoshka truncation; for ordinary models, cutting dims loses arbitrary information.

---

## ⚫ Interview Questions + Answers

Q1: What does "1536 dimensions" mean?
A1: Each embedding has 1536 floating point numbers.

Q2: Do all vectors in an index need the same dimension?
A2: Yes. Distance metrics require equal lengths and DB columns are fixed.

Q3: How much memory do 1M vectors of 768 d need in float32?
A3: 1M x 768 x 4 bytes = about 2.9 GB, plus index overhead.

Q4: What are ways to reduce memory?
A4: Smaller dims (Matryoshka), lower precision (float16, int8, binary quantisation), and product quantisation in the index.

Q5: How would you choose dimension for 500M vectors with a latency budget of 50 ms?
A5: Do capacity math (500M x d x bytes), eval recall for several d and quantisation levels, use HNSW or IVF-PQ with sharding, retrieve more candidates at low d then rerank with full vectors or a cross-encoder. Pick the cheapest config that meets recall and latency.

---

## 🔷 When to Use + When Not to Use
✅ Use smaller dimensions when:
- Corpus is huge or RAM is tight
- Latency matters
- Recall loss is within tolerance

❌ Avoid shrinking when:
- Domain is subtle (legal/medical) and eval shows a big drop
- Model does not support truncation

---

## 📊 Visual Diagram
```
 dims:      256      512      1024     1536     3072
 bytes/vec: 1 KB     2 KB     4 KB     6 KB     12 KB   (float32)
 1M vecs:   0.95 GB  1.9 GB   3.8 GB   5.7 GB   11.4 GB

 recall:    ▁▃▅▆▇ -> curve flattens: diminishing returns
```

---

## 💰 Cost Impact
The embedding API charges per token, not per dimension, so dimensions change **storage and search cost**, not API price. Example: 50M vectors at 3072 d = 572 GB; at 1024 d = 191 GB; with int8 = 48 GB. That can be the difference between a big cluster and one machine. Optimise with `dimensions`, quantisation, and tiered retrieval (cheap short vectors first, rerank with full ones).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dimension | Length of the vector | Vector की length |
| Matryoshka | Nested useful prefixes | Prefix में जानकारी वाला तरीका |
| Quantisation | Lower precision numbers | कम precision वाले numbers |
| Truncation | Keep only first N dims | पहले N dims रखना |
| PCA | Reduce dims mathematically | Dimensions घटाने का math तरीका |
| Float32 | 4-byte number | 4 byte का number |

---

## ⚡ 3-Line Summary
English: Dimension is the vector length; it sets memory, storage, and search cost, not API price. Shorten only models that support it and re-normalise. Pick the knee of the recall-vs-size curve.
Hindi: Dimension vector की length है; यह memory, storage और search cost तय करती है, API price नहीं। सिर्फ supported models छोटे करो और re-normalise करो। Recall बनाम size curve का सही point चुनो।

---

## ➡️ Next Topic
**110. Anthropic Embeddings** - Anthropic has no own embedding model; learn the recommended route (Voyage AI) and how it fits with Claude.
