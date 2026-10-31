---

# 130. IVF Algorithm
# हिंदी में: IVF Algorithm (Inverted File Index)

---

## 🔵 Simple Definition (English)
IVF (Inverted File) splits all vectors into clusters using k-means. Each cluster has a centroid (its centre). At query time we find the few centroids closest to the query (`nprobe` of them) and search only inside those clusters. It is like going to the right shelves of a library instead of reading every book.

## 🔵 सरल परिभाषा (Hindi)
IVF (Inverted File) सभी vectors को k-means से clusters में बाँटता है। हर cluster का एक centroid (centre) होता है। Query के समय query के सबसे पास वाले कुछ centroids (`nprobe`) चुनकर सिर्फ़ उन्हीं clusters में search करते हैं। जैसे library में हर किताब पढ़ने के बजाय सही shelves पर जाना।

---

## 🔴 Problem it Solves
Brute force scans all N vectors. HNSW is fast but needs a lot of RAM and is slow to build. IVF narrows the search to roughly `nprobe / nlist` of the data, builds quickly, and combines with compression (PQ) to fit hundreds of millions of vectors in modest memory.

## 🔴 यह क्यों बना? (Hindi)
Brute force सभी N vectors scan करता है। HNSW तेज़ है पर RAM बहुत लेता है और build धीमा है। IVF search को data के लगभग `nprobe / nlist` हिस्से तक सीमित करता है, जल्दी build होता है और compression (PQ) के साथ करोड़ों vectors को कम memory में रख सकता है।

---

## 🟢 How it Works — Step by Step

```
Train:
Step 1 → Run k-means on a sample of vectors to get nlist centroids
Add:
Step 2 → For each vector, find its nearest centroid -> append to that cluster's list
Query:
Step 3 → Compare the query with all nlist centroids (cheap: nlist is small, e.g. 1024)
Step 4 → Pick the nprobe closest clusters
Step 5 → Scan every vector inside those clusters (exact distance, or PQ-approximated)
Step 6 → Merge the results, return the top-k
Tune:
Step 7 → Higher nprobe = more recall, more latency. nlist ~ sqrt(N) is a common start.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Train:
Step 1 → Vectors के sample पर k-means चलाकर nlist centroids निकालो
Add:
Step 2 → हर vector को उसके सबसे पास के centroid वाले cluster में डालो
Query:
Step 3 → Query को सभी nlist centroids से compare करो (सस्ता, nlist छोटा है)
Step 4 → सबसे पास के nprobe clusters चुनो
Step 5 → उन clusters के सभी vectors scan करो
Step 6 → Results merge करके top-k लौटाओ
Tune:
Step 7 → nprobe बढ़ाओ = recall और latency दोनों बढ़ते हैं। nlist ~ sqrt(N) से शुरू करो।
```

---

## 🟡 Real World Example
**Tariff Classification System**: 20M customs records, 768-dim. HNSW would need ~70 GB RAM. We use `IVF4096,PQ64` in FAISS: each vector compresses to 64 bytes, so the index is ~1.5 GB. With `nprobe=16` it reaches ~92% recall at ~5 ms, then the top 200 are reranked with exact vectors to get ~98%.

**Amazon-style**: product-image similarity on 300M images stored on disk with IVF-PQ because RAM cost is the constraint.

## 🟡 Real Example Hindi mein
**Tariff System**: 2 करोड़ customs records, 768-dim। HNSW को ~70 GB RAM चाहिए। हम FAISS में `IVF4096,PQ64` use करते हैं: हर vector 64 bytes का, index ~1.5 GB। `nprobe=16` पर ~92% recall और ~5 ms; फिर top 200 को exact vectors से rerank करके ~98%। **Amazon-style**: 30 करोड़ images पर RAM cost बड़ी समस्या है, इसलिए IVF-PQ।

---

## 💻 Code Example — Basic
```python
# Basic: IVF from scratch in pure Python (k-means + nprobe search). Runs offline.
import math                                         # distance
import random                                       # data + k-means init
from typing import Dict, List                       # type hints

random.seed(3)                                      # reproducible
Vec = List[float]                                   # vector alias
N, DIM, NLIST = 3000, 8, 16                         # data size, dims, clusters

def d2(a: Vec, b: Vec) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))  # squared L2 (no sqrt needed for ranking)

data: List[Vec] = [[random.gauss(0, 1) for _ in range(DIM)] for _ in range(N)]   # the vectors

def kmeans(points: List[Vec], k: int, iters: int = 8) -> List[Vec]:
    cents = random.sample(points, k)                # pick k random starting centroids
    for _ in range(iters):                          # a few Lloyd iterations
        groups: List[List[Vec]] = [[] for _ in range(k)]   # members per centroid
        for p in points:                            # assign each point
            j = min(range(k), key=lambda c: d2(p, cents[c]))   # nearest centroid
            groups[j].append(p)                     # add to that group
        for j, g in enumerate(groups):              # recompute centroids
            if g:                                   # skip empty clusters
                cents[j] = [sum(col) / len(g) for col in zip(*g)]   # mean of members
    return cents

centroids = kmeans(data, NLIST)                     # TRAIN step
lists: Dict[int, List[int]] = {j: [] for j in range(NLIST)}   # inverted lists: cluster -> ids
for i, v in enumerate(data):                        # ADD step
    lists[min(range(NLIST), key=lambda c: d2(v, centroids[c]))].append(i)   # nearest centroid

def search(q: Vec, k: int, nprobe: int) -> List[int]:
    order = sorted(range(NLIST), key=lambda c: d2(q, centroids[c]))[:nprobe]   # closest clusters
    cand = [i for c in order for i in lists[c]]     # all ids in those clusters
    return sorted(cand, key=lambda i: d2(q, data[i]))[:k]   # exact rank of candidates

queries = [[random.gauss(0, 1) for _ in range(DIM)] for _ in range(30)]   # test queries
for nprobe in (1, 4, 16):                           # try different nprobe values
    ok = 0
    for q in queries:
        truth = set(sorted(range(N), key=lambda i: d2(q, data[i]))[:5])    # brute force top 5
        ok += len(truth & set(search(q, 5, nprobe)))                       # overlap
    print(f"nprobe={nprobe:2d} recall@5={ok / (5 * len(queries)):.2f}")    # recall rises with nprobe
```

## 💻 Code Example — Advanced
```python
# Advanced: IVF-Flat and IVF-PQ with FAISS (pip install faiss-cpu numpy)
import asyncio                                          # async wrapper
import logging                                          # logs
from typing import Tuple                                # type hints

import faiss                                            # Facebook AI Similarity Search
import numpy as np                                      # arrays

log = logging.getLogger("ivf")                          # logger

def build_ivf(xb: np.ndarray, nlist: int = 100, pq_m: int | None = None) -> faiss.Index:
    """Train + populate an IVF index. xb must be float32 shape (N, d)."""
    if xb.dtype != np.float32:                          # FAISS needs float32
        xb = xb.astype("float32")                       # convert safely
    n, d = xb.shape                                     # sizes
    if n < nlist * 39:                                  # FAISS warns below ~39 points per centroid
        log.warning("only %d vectors for %d clusters; reduce nlist", n, nlist)
    faiss.normalize_L2(xb)                              # unit vectors -> inner product == cosine
    quantizer = faiss.IndexFlatIP(d)                    # coarse index that holds the centroids
    if pq_m:                                            # compressed variant (d must be divisible by pq_m)
        index = faiss.IndexIVFPQ(quantizer, d, nlist, pq_m, 8, faiss.METRIC_INNER_PRODUCT)   # 8 bits per sub-code
    else:
        index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)          # exact vectors
    index.train(xb)                                     # k-means training (REQUIRED before add)
    index.add(xb)                                       # fill inverted lists
    return index

def ivf_search(index: faiss.IndexIVF, xq: np.ndarray, k: int = 5, nprobe: int = 8) -> Tuple[np.ndarray, np.ndarray]:
    if not index.is_trained:                            # guard against untrained index
        raise RuntimeError("index not trained")
    index.nprobe = nprobe                               # clusters to visit
    xq = xq.astype("float32")                           # dtype
    faiss.normalize_L2(xq)                              # same normalisation as data
    return index.search(xq, k)                          # (scores, ids), -1 id means "not found"

async def ivf_search_async(index: faiss.IndexIVF, xq: np.ndarray, k: int = 5, nprobe: int = 8):
    return await asyncio.to_thread(ivf_search, index, xq, k, nprobe)   # off the event loop

# Memory: IVFFlat ~ N*d*4 bytes. IVFPQ(m=64) ~ N*64 bytes (24x smaller for d=384).
# Token usage: 0 LLM tokens in the index; only the query embedding is paid for.
```

---

## 🟠 FastAPI Integration
```python
import numpy as np                                     # arrays
from fastapi import FastAPI, HTTPException              # FastAPI
from pydantic import BaseModel, Field                   # pydantic v2

app = FastAPI()                                         # app
rng = np.random.default_rng(0)                          # demo data generator
index = build_ivf(rng.normal(size=(5000, 64)).astype("float32"), nlist=50)   # built once at startup

class Q(BaseModel):
    vector: list[float] = Field(min_length=64, max_length=64)   # dimension check
    k: int = Field(5, ge=1, le=100)                     # bounded results
    nprobe: int = Field(8, ge=1, le=50)                 # recall/speed knob

@app.post("/ivf/search")                                # route
async def search(q: Q) -> dict:
    try:
        scores, ids = await ivf_search_async(index, np.array([q.vector]), q.k, q.nprobe)
    except RuntimeError as exc:                         # untrained etc.
        raise HTTPException(500, str(exc))
    return {"ids": [int(i) for i in ids[0] if i >= 0], "scores": scores[0].tolist()}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain's FAISS wrapper accepts a prebuilt index, so you can plug in IVF.
import faiss                                            # FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore   # id -> Document map
from langchain_community.vectorstores import FAISS      # LangChain wrapper
from langchain_openai import OpenAIEmbeddings           # embeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536 dims
d = 1536                                                # dimension
quant = faiss.IndexFlatL2(d)                            # centroid holder
ivf = faiss.IndexIVFFlat(quant, d, 100)                 # nlist=100 (train before adding data!)
# ivf.train(train_matrix)                               # needs >= ~3900 sample vectors
vs = FAISS(embedding_function=emb, index=ivf, docstore=InMemoryDocstore({}), index_to_docstore_id={})
# vs.add_texts([...]) then vs.as_retriever(search_kwargs={"k": 5}) works inside any LCEL/LangGraph node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to train the index before adding vectors
✅ Correct: `index.train(sample)` first.

```python
# Wrong: raises "index not trained" / unusable centroids
index = faiss.IndexIVFFlat(quant, d, 100); index.add(xb)
# Right
index.train(xb); index.add(xb)
```

❌ Mistake 2: Leaving `nprobe=1` (the default) and wondering why recall is low
✅ Correct: raise nprobe (8-64) and measure.

```python
# Wrong: default nprobe=1 -> recall maybe 40%
index.search(xq, 5)
# Right
index.nprobe = 16
index.search(xq, 5)
```

---

## 🧠 Tricky Interview Question

**Q**: "A query lies right on the boundary between two clusters. What happens with nprobe=1, and how do you fix it?"

**Answer**: The true neighbours may be split across both clusters, but nprobe=1 searches only the nearest centroid's cluster, so half the true neighbours are missed (the "boundary problem"). Fix: increase nprobe (search several clusters), use more clusters with higher nprobe, or use a hierarchical coarse quantiser (IVF + HNSW over centroids). Recall depends strongly on data clusteredness: embeddings with a uniform spread need larger nprobe.

---

## ⚫ Interview Questions + Answers

Q1: What does "inverted file" mean here?
A1: Like a search engine's inverted index mapping a word to documents, IVF maps each centroid (cluster id) to the list of vectors in that cluster.

Q2: What are nlist and nprobe?
A2: `nlist` = number of clusters built at training; `nprobe` = number of clusters scanned per query. nprobe controls the recall/speed trade-off.

Q3: How do you choose nlist?
A3: A common rule is about 4 x sqrt(N) to 16 x sqrt(N) for large N. Too few means big clusters (slow scans), too many means poor training and lots of boundary misses.

Q4: What is IVF-PQ?
A4: IVF narrows the search; Product Quantisation compresses each vector into short codes (e.g. 64 bytes). Distances are computed on codes, giving 10-30x memory savings with some precision loss. Often followed by exact reranking.

Q5: When would you pick IVF over HNSW, and what are the operational risks?
A5: Pick IVF when memory or build time dominates (100M+ vectors, disk-backed or compressed), or the data is static. Risks: the clusters are trained on the data distribution, so heavy drift or many new vectors from a different distribution degrades recall until you retrain; training needs representative samples; recall at low latency is generally below HNSW. Monitor recall and schedule retraining.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Very large datasets and limited RAM (with PQ)
- Fast build or batch rebuild is acceptable
- You can tune nprobe against a recall target

❌ Avoid when:
- Data is small (flat search is enough)
- Data changes constantly with distribution shift (needs retraining)
- You need the very best recall at tiny latency with plenty of RAM (HNSW)

---

## 📊 Visual Diagram
```
        k-means clusters (nlist = 4)

   ┌───────────┬───────────┐
   │  C1  ●●●  │  C2  ●●   │      query q
   │    ●  c1  │   c2  ●●  │         ✱
   ├───────────┼───────────┤   nprobe=2 -> scan C2 and C4 only
   │  C3  ●    │  C4  ●●●  │
   │   c3  ●●  │    c4  ●  │
   └───────────┴───────────┘
 Step 1: q vs 4 centroids  ->  nearest = C4, C2
 Step 2: scan only members of C4 and C2  ->  top-k
```

---

## 💰 Cost Impact
- Memory: IVF-Flat stores full vectors (N x d x 4 bytes). IVF-PQ with m=64 stores ~64 bytes per vector: 100M vectors = ~6.4 GB instead of ~300 GB for 768-dim float32, a huge infrastructure saving.
- CPU: scanning nprobe/nlist of the data. nprobe=16 of nlist=4096 touches ~0.4% of vectors.
- Training: one-off cost, minutes on CPU for millions of vectors; retrain on drift.
- LLM token cost: unchanged by index type, but low recall means missed context and re-asked questions; reranking the top 100 candidates with a cheap cross-encoder keeps prompts at ~1,500 tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Centroid | Centre of a cluster | Cluster का केंद्र |
| nlist | Number of clusters | Clusters की संख्या |
| nprobe | Clusters searched per query | Query पर देखे जाने वाले clusters |
| k-means | Clustering algorithm | Clustering algorithm |
| Inverted list | Vectors belonging to a centroid | Centroid के vectors की list |
| PQ | Product quantisation (compression) | Vectors को compress करने की तकनीक |
| Boundary problem | Neighbours split across clusters | Neighbours का दो clusters में बँट जाना |

---

## ⚡ 3-Line Summary
English: IVF clusters vectors with k-means and searches only the nprobe nearest clusters. It builds fast and, with PQ, uses very little memory. Tune nlist and nprobe, and retrain when data drifts.
Hindi: IVF vectors को k-means से clusters में बाँटता है और सिर्फ़ nprobe सबसे पास वाले clusters में search करता है। यह जल्दी build होता है और PQ के साथ बहुत कम memory लेता है। nlist और nprobe tune करो, और data drift होने पर retrain करो।

---

## ➡️ Next Topic
**131. Pinecone — Complete Guide** — a fully managed vector database, so you get these indexes without running them yourself.
