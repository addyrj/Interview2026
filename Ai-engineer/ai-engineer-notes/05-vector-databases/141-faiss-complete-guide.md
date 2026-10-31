---

# 141. FAISS — Complete Guide
# हिंदी में: FAISS — पूरी Guide

---

## 🔵 Simple Definition (English)
FAISS (Facebook AI Similarity Search) is Meta's open-source C++ library (with Python bindings) for fast similarity search and clustering of dense vectors. It is a **library, not a database**: you hold the index in memory, add float32 vectors, and search. It offers exact (Flat) and approximate indexes (IVF, HNSW, PQ) and can run on CPU or GPU.

## 🔵 सरल परिभाषा (Hindi)
FAISS (Facebook AI Similarity Search) Meta की open-source C++ library (Python bindings के साथ) है जो dense vectors की तेज़ similarity search और clustering के लिए है। यह **library है, database नहीं**: index memory में रहता है, आप float32 vectors add करते हैं और search करते हैं। इसमें exact (Flat) और approximate indexes (IVF, HNSW, PQ) हैं और यह CPU या GPU पर चल सकती है।

---

## 🔴 Problem it Solves
Pure Python/NumPy brute force becomes slow beyond ~100k vectors, and you do not want to run a database for an offline job or a small service. FAISS provides highly optimised SIMD/BLAS/GPU search and many index types, with memory-saving compression, in a single `pip install faiss-cpu`.

## 🔴 यह क्यों बना? (Hindi)
Pure Python/NumPy brute force ~1 लाख vectors के बाद धीमा हो जाता है, और offline job या छोटी service के लिए database नहीं चलाना चाहते। FAISS highly optimised SIMD/BLAS/GPU search और कई index types, memory बचाने वाली compression के साथ, बस एक `pip install faiss-cpu` में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install faiss-cpu numpy        (faiss-gpu for CUDA builds)
Step 2 → Make a float32 matrix xb of shape (N, d); normalise rows if you want cosine
Step 3 → Create an index:  faiss.IndexFlatIP(d)  (exact inner product)   or IndexFlatL2(d)
Step 4 → (IVF/PQ only) index.train(xb)  — learns centroids / codebooks
Step 5 → index.add(xb)  — vectors get ids 0..N-1 in insertion order
Step 6 → D, I = index.search(xq, k)  — D: scores/distances (nq, k), I: row numbers (nq, k); -1 = no result
Step 7 → Map row numbers back to your own ids/text with a Python list or dict (FAISS stores NO metadata)
Step 8 → faiss.write_index(index, "file.index") / faiss.read_index("file.index")
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install faiss-cpu numpy        (CUDA के लिए faiss-gpu)
Step 2 → (N, d) shape का float32 matrix xb बनाओ; cosine चाहिए तो rows normalise करो
Step 3 → Index बनाओ: faiss.IndexFlatIP(d) (exact inner product) या IndexFlatL2(d)
Step 4 → (सिर्फ़ IVF/PQ) index.train(xb) — centroids / codebooks सीखता है
Step 5 → index.add(xb) — vectors को insertion order में ids 0..N-1 मिलते हैं
Step 6 → D, I = index.search(xq, k) — D: scores/distances, I: row numbers; -1 = result नहीं
Step 7 → Row numbers को अपने ids/text से map करो (FAISS metadata store नहीं करता)
Step 8 → faiss.write_index(index, "file.index") / faiss.read_index("file.index")
```

---

## 🟡 Real World Example
**Tariff Classification System**: an offline job embeds 2M historical declarations to find near-duplicates and cluster them before manual review. A `faiss.IndexFlatIP` on normalised vectors gives exact results in seconds with batch queries, with no server needed. The service later keeps a smaller FAISS index (200k headings) in RAM inside the API pod, rebuilt nightly and loaded from a file.

**Amazon-style**: "visually similar products" computed in a batch pipeline with a GPU FAISS index, with results written to a database.

## 🟡 Real Example Hindi mein
**Tariff System**: Offline job 20 लाख पुराने declarations embed करके near-duplicates ढूँढता है और manual review से पहले cluster करता है। Normalised vectors पर `faiss.IndexFlatIP` बिना server के seconds में exact results देता है। Service में API pod की RAM में छोटा FAISS index (2 लाख headings) रहता है, रात को rebuild और file से load। **Amazon-style**: "visually similar products" GPU FAISS index से batch pipeline में निकलते हैं और database में लिखे जाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: exact cosine search with FAISS (pip install faiss-cpu numpy)
import faiss                                                  # the library
import numpy as np                                            # arrays (FAISS needs float32 numpy)

d = 4                                                         # vector dimension
texts = ["Headphones and earphones", "Men's shirts", "Smartphones", "Cotton fabric"]   # our documents
xb = np.array([                                               # database vectors (toy embeddings)
    [0.9, 0.1, 0.0, 0.1],
    [0.0, 0.1, 0.9, 0.2],
    [0.8, 0.3, 0.1, 0.1],
    [0.1, 0.0, 0.8, 0.3],
], dtype="float32")                                           # float32 is REQUIRED

faiss.normalize_L2(xb)                                        # unit length -> inner product == cosine
index = faiss.IndexFlatIP(d)                                  # exact inner-product index
index.add(xb)                                                 # add all vectors (ids 0..3)
print("stored:", index.ntotal)                                # number of vectors

xq = np.array([[1.0, 0.0, 0.1, 0.0]], dtype="float32")        # one query (shape (1, d))
faiss.normalize_L2(xq)                                        # same normalisation as the data
scores, ids = index.search(xq, 2)                             # top 2 -> arrays of shape (1, 2)
for s, i in zip(scores[0], ids[0]):                           # first (only) query
    print(round(float(s), 3), texts[i])                       # map row number back to text
```

## 💻 Code Example — Advanced
```python
# Advanced: FAISS store with stable external ids, deletion, persistence, thread-safety and async.
import asyncio                                                # async runtime
import logging                                                # logs
import threading                                              # lock for writes
from pathlib import Path                                      # file handling
from typing import Dict, List, Tuple

import faiss                                                  # library
import numpy as np                                            # arrays

log = logging.getLogger("faiss-store")                        # logger

class FaissStore:
    """Exact cosine search with external int64 ids and a side dictionary for text/metadata."""

    def __init__(self, dim: int) -> None:
        self.dim = dim                                        # vector size
        self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))   # IDMap2 = our own ids + removal support
        self.meta: Dict[int, Dict[str, str]] = {}             # id -> metadata (FAISS stores none)
        self.lock = threading.Lock()                          # FAISS add/remove are not thread-safe with search

    def _prep(self, x: np.ndarray) -> np.ndarray:
        x = np.ascontiguousarray(x, dtype="float32")          # FAISS needs contiguous float32
        if x.ndim != 2 or x.shape[1] != self.dim:             # validate shape
            raise ValueError(f"expected (n, {self.dim}), got {x.shape}")
        faiss.normalize_L2(x)                                 # cosine via inner product
        return x

    def upsert(self, ids: List[int], vecs: np.ndarray, metas: List[Dict[str, str]]) -> None:
        x = self._prep(vecs.copy())                           # copy so the caller's array is not modified
        with self.lock:
            self.index.remove_ids(np.array(ids, dtype="int64"))   # remove old versions (no error if missing)
            self.index.add_with_ids(x, np.array(ids, dtype="int64"))
            for i, m in zip(ids, metas):
                self.meta[i] = m

    def delete(self, ids: List[int]) -> int:
        with self.lock:
            removed = int(self.index.remove_ids(np.array(ids, dtype="int64")))   # returns number removed
            for i in ids:
                self.meta.pop(i, None)
        return removed

    def search(self, q: np.ndarray, k: int = 5, min_score: float = 0.0) -> List[Tuple[int, float, Dict[str, str]]]:
        x = self._prep(q.copy())
        with self.lock:
            scores, ids = self.index.search(x, min(k, max(self.index.ntotal, 1)))
        return [(int(i), float(s), self.meta.get(int(i), {}))
                for s, i in zip(scores[0], ids[0]) if i != -1 and s >= min_score]   # -1 = padding

    def save(self, path: str) -> None:
        faiss.write_index(self.index, path)                   # index only; persist `meta` separately (JSON/DB)

    @classmethod
    def load(cls, path: str, dim: int) -> "FaissStore":
        if not Path(path).exists():
            raise FileNotFoundError(path)
        store = cls(dim)
        store.index = faiss.read_index(path)                  # restores IDMap2 with ids
        return store

    async def search_async(self, q: np.ndarray, k: int = 5, min_score: float = 0.0):
        return await asyncio.to_thread(self.search, q, k, min_score)   # keep the event loop free

# Token usage: FAISS uses 0 tokens. Memory: N x d x 4 bytes (1M x 768 = ~3 GB) for Flat indexes.
```

---

## 🟠 FastAPI Integration
```python
import numpy as np                                           # arrays
from fastapi import FastAPI, HTTPException, Query             # FastAPI
from openai import AsyncOpenAI                                # embeddings
from pydantic import BaseModel                                # pydantic v2

app = FastAPI()                                               # app
oai = AsyncOpenAI()                                           # client
store = FaissStore(dim=1536)                                  # index lives in process memory

class Item(BaseModel):
    id: int                                                   # external id
    text: str                                                 # text to index
    country: str = "IN"                                       # metadata

@app.post("/index")                                           # add/replace an item
async def add_item(item: Item) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=item.text)
    store.upsert([item.id], np.array([emb.data[0].embedding]), [{"text": item.text, "country": item.country}])
    return {"indexed": item.id, "total": store.index.ntotal}

@app.get("/search")                                           # query route
async def search(q: str, k: int = Query(5, ge=1, le=50)) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    try:
        hits = await store.search_async(np.array([emb.data[0].embedding]), k, min_score=0.3)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"hits": [{"id": i, "score": s, **m} for i, s, m in hits]}
# Note: each worker process holds its own index copy. For multi-worker setups, load a shared read-only file at startup.
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-community faiss-cpu
from langchain_community.vectorstores import FAISS             # LangChain wrapper
from langchain_openai import OpenAIEmbeddings                   # embeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.from_texts(["Headphones and earphones", "Men's shirts"], emb,
                      metadatas=[{"country": "IN"}, {"country": "IN"}])   # builds a FAISS index + docstore
vs.save_local("faiss_tariff")                                   # writes index.faiss + index.pkl
# SECURITY: loading uses pickle. Only load files you created yourself.
vs2 = FAISS.load_local("faiss_tariff", emb, allow_dangerous_deserialization=True)
docs = vs2.similarity_search("wireless earbuds", k=2, filter={"country": "IN"})   # metadata filter (post-filter)
retriever = vs2.as_retriever(search_kwargs={"k": 3})            # use in LCEL or a LangGraph node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing float64 (the NumPy default) or non-contiguous arrays
✅ Correct: `np.asarray(x, dtype="float32")` and `np.ascontiguousarray`.

```python
# Wrong: crashes or gives garbage
index.add(np.random.rand(10, 4))             # float64
# Right
index.add(np.random.rand(10, 4).astype("float32"))
```

❌ Mistake 2: Expecting FAISS to store text/metadata or to survive restart automatically
✅ Correct: keep a side store (dict/DB) keyed by id, and save the index with `write_index`.

```python
# Wrong: "where is my document text?" -> only row numbers come back
D, I = index.search(xq, 3)
# Right
texts_by_id = {0: "Headphones", 1: "Shirts"}
print([texts_by_id[i] for i in I[0] if i != -1])
```

❌ Mistake 3: Using `IndexFlatL2` with unnormalised vectors and expecting cosine ranking
✅ Correct: normalise and use `IndexFlatIP`.

---

## 🧠 Tricky Interview Question

**Q**: "You delete 30% of documents from a FAISS IVF index with `remove_ids`, but search memory and latency barely change. Why?"

**Answer**: Not every FAISS index supports efficient removal. IVF indexes can remove ids from inverted lists, but HNSW indexes do not support removal at all, and Flat indexes shift data around (removal is O(N)). Memory may not shrink immediately and list fragmentation remains. The common production pattern is: keep deletes in a tombstone set and filter results (over-fetching `k`), then rebuild the index periodically from the source of truth, and swap it atomically. This is also why a real database may be a better fit when updates and deletes are frequent.

---

## ⚫ Interview Questions + Answers

Q1: Is FAISS a vector database?
A1: No. It is a similarity-search library: no metadata, no server, no built-in persistence beyond saving the index file, no multi-user access. Databases like Chroma or Qdrant wrap similar algorithms with storage and APIs.

Q2: What is the difference between `IndexFlatL2` and `IndexFlatIP`?
A2: Flat means exact (brute force). L2 ranks by Euclidean distance (smaller is better); IP ranks by inner product (larger is better), which equals cosine when vectors are normalised.

Q3: Why does `search` sometimes return `-1` ids?
A3: When fewer than `k` vectors are found (empty index, IVF probing empty lists, filtered results), the remaining slots are filled with -1 and a large/zero distance. Always filter `i != -1`.

Q4: How do you persist and reload an index?
A4: `faiss.write_index(index, path)` and `faiss.read_index(path)`. Persist metadata separately.

Q5: How would you scale FAISS to 500M vectors?
A5: Use compressed indexes (IVF-PQ, OPQ+IVF-PQ) to fit in RAM, or on-disk/GPU indexes; shard the data over machines and merge top-k from each shard; train on a sample; tune `nprobe` for recall vs latency with a held-out ground truth; rerank the top few hundred with exact vectors; and plan rebuilds because updates are limited. If you also need metadata filtering, replication and updates, move to a vector database that uses FAISS-like algorithms internally.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Offline/batch similarity (dedup, clustering, evaluation)
- Embedded search in a service with mostly read-only data
- You need GPU speed or aggressive compression

❌ Avoid when:
- You need metadata filtering, frequent updates/deletes, multi-writer access or persistence guarantees
- You want a managed service (use Pinecone, Qdrant Cloud, etc.)

---

## 📊 Visual Diagram
```
 embeddings (N x d, float32)
        │ normalize_L2 (for cosine)
        ▼
 ┌──────────────────────────┐   train()   (IVF/PQ only)
 │ FAISS Index              │◄────────────
 │  Flat | IVF | HNSW | PQ  │
 └───────────┬──────────────┘
   add(xb)   │   search(xq, k)
             ▼
   D (scores), I (row numbers)  ──► your dict {row: text, metadata} ──► LLM
   write_index / read_index  ──►  file on disk
```

---

## 💰 Cost Impact
- Free and open source; cost = your RAM/CPU/GPU. Flat index memory = N x d x 4 bytes: 1M x 1536 = ~6 GB; 10M = ~61 GB.
- Compression: IVF-PQ with 64 bytes per vector makes 10M vectors ~0.6 GB (plus overhead), a huge saving versus managed storage.
- No per-query fee; latency is predictable. Embedding cost is independent (text-embedding-3-small: $0.02 per 1M tokens).
- LLM tokens: exact search with a score threshold limits context to the best 3-5 chunks (~900-1,500 tokens), keeping gpt-4o-mini calls to a fraction of a cent.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FAISS | Meta's similarity-search library | Meta की similarity-search library |
| IndexFlat | Exact brute-force index | Exact brute-force index |
| IndexIVF | Cluster-based approximate index | Cluster-based approximate index |
| IndexHNSWFlat | Graph-based approximate index | Graph-based approximate index |
| PQ | Product quantisation (compression) | Compression की तकनीक |
| IDMap | Wrapper to use your own int ids | अपने ids use करने का wrapper |
| nprobe | Clusters searched in IVF | IVF में देखे जाने वाले clusters |

---

## ⚡ 3-Line Summary
English: FAISS is a fast library, not a database: you manage vectors, ids and metadata yourself. Use float32, normalise for cosine, choose Flat for exact or IVF/HNSW/PQ for scale, and save indexes with write_index. Great for batch and embedded search; limited for updates.
Hindi: FAISS तेज़ library है, database नहीं: vectors, ids और metadata आप खुद संभालते हैं। float32 use करो, cosine के लिए normalise करो, exact के लिए Flat या scale के लिए IVF/HNSW/PQ चुनो, और write_index से save करो। Batch और embedded search के लिए बढ़िया; updates के लिए सीमित।

---

## ➡️ Next Topic
**142. FAISS — Local Vector Search** — building a complete local semantic search: index files, id mapping and filtering patterns.
