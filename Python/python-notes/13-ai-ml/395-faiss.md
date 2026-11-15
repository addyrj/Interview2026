---

# 395. FAISS
# हिंदी में: FAISS (Vector Similarity Search Library)

---

## 🔵 Simple Definition (English)
FAISS (Facebook AI Similarity Search) is a library that finds the nearest vectors to a query vector very fast. You give it a NumPy array of embeddings, it builds an index, and `index.search()` returns the ids of the closest vectors. It runs inside your own Python process, no server needed.

## 🔵 सरल परिभाषा (Hindi)
FAISS (Facebook AI Similarity Search) एक library है जो query vector के सबसे पास के vectors बहुत तेजी से ढूंढती है। आप embeddings का NumPy array देते हैं, यह index बनाती है, और `index.search()` सबसे पास के vectors के ids लौटाता है। यह आपके अपने Python process के अंदर चलती है, server की जरूरत नहीं।

---

## 🔴 Problem it Solves
Finding similar items by comparing the query with every vector (brute force) is fine for 10,000 vectors but slow for 100 million. Plain NumPy loops also waste CPU. FAISS gives optimized C++ code (SIMD, optional GPU) and smart indexes (IVF clusters, HNSW, product quantization) that trade a tiny bit of accuracy for huge speed and memory savings.

## 🔴 यह क्यों बना? (Hindi)
Query को हर vector से compare करना (brute force) 10,000 vectors के लिए ठीक है लेकिन 10 करोड़ के लिए धीमा है। सादे NumPy loops CPU भी बर्बाद करते हैं। FAISS optimized C++ code (SIMD, optional GPU) और smart indexes (IVF clusters, HNSW, product quantization) देता है जो थोड़ी सी accuracy के बदले बहुत ज्यादा speed और memory बचत देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Make embeddings as a float32 NumPy array of shape (n, dim)
Step 2 → Create an index: IndexFlatL2(dim) (exact) or IndexIVFFlat / IndexHNSWFlat (approximate)
Step 3 → If the index type needs it (IVF, PQ), call index.train(data) first
Step 4 → index.add(data) stores vectors; their ids are 0, 1, 2 ... in insertion order
Step 5 → index.search(query, k) returns (distances, ids), both shape (n_queries, k)
Step 6 → Map the ids back to your own documents yourself (FAISS stores only vectors)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Embeddings को float32 NumPy array (shape (n, dim)) में बनाओ
Step 2 → Index बनाओ: IndexFlatL2(dim) (exact) या IndexIVFFlat / IndexHNSWFlat (approximate)
Step 3 → अगर index type को जरूरत हो (IVF, PQ) तो पहले index.train(data) करो
Step 4 → index.add(data) vectors store करता है; ids insertion order में 0, 1, 2 ... होते हैं
Step 5 → index.search(query, k) (distances, ids) लौटाता है, दोनों की shape (n_queries, k)
Step 6 → ids को अपने documents से खुद map करो (FAISS सिर्फ vectors रखता है)
```

---

## 🟡 Real World Example
A company stores 2 million support-ticket embeddings. On ticket creation, the backend searches the 5 most similar past tickets using an `IndexIVFFlat` loaded from disk at startup. A Zomato-style "similar restaurants" feature and image search ("find similar product photos") work the same way. In RAG demos and local development, FAISS is the free alternative to a cloud vector database.

## 🟡 Real Example Hindi mein
एक company के पास 20 लाख support-ticket embeddings हैं। नया ticket बनते ही backend startup पर disk से load किए `IndexIVFFlat` से 5 सबसे मिलते-जुलते पुराने tickets ढूंढता है। Zomato जैसा "similar restaurants" feature और image search ("मिलते-जुलते product photos") भी ऐसे ही काम करते हैं। RAG demos और local development में FAISS cloud vector database का मुफ्त विकल्प है।

---

## 💻 Code Example — Basic
```python
# Basic FAISS examples   (pip install faiss-cpu numpy; tested with faiss-cpu 1.16.0)
import numpy as np                                 # FAISS needs float32 numpy arrays
import faiss                                       # the vector search library

dim: int = 4                                       # each vector has 4 numbers
vectors: np.ndarray = np.array([                   # our tiny "database" of 5 vectors
    [1.0, 0.0, 0.0, 0.0],                          # id 0
    [0.9, 0.1, 0.0, 0.0],                          # id 1 (close to id 0)
    [0.0, 1.0, 0.0, 0.0],                          # id 2
    [0.0, 0.0, 1.0, 0.0],                          # id 3
    [0.0, 0.0, 0.0, 1.0],                          # id 4
], dtype="float32")                                # float32 is the dtype FAISS works with

index: faiss.IndexFlatL2 = faiss.IndexFlatL2(dim)  # exact search, L2 (euclidean) distance
print(index.is_trained, index.ntotal)              # flat index needs no training; 0 vectors so far
index.add(vectors)                                 # add all vectors (ids become 0..4)
print(index.ntotal)                                # how many vectors are stored

query: np.ndarray = np.array([[1.0, 0.05, 0.0, 0.0]], dtype="float32")   # shape (1, dim): one query
distances, ids = index.search(query, 3)            # find the 3 nearest neighbours
print(ids)                                         # row of ids, nearest first
print(np.round(distances, 4))                      # SQUARED L2 distances

_, ids_all = index.search(query, 7)                # ask for more than we have
print(ids_all)                                     # missing results are padded with -1

# Output (really executed):
# True 0
# 5
# [[0 1 2]]
# [[0.0025 0.0125 1.9025]]
# [[ 0  1  2  3  4 -1 -1]]
```

## 💻 Code Example — Advanced
```python
# Production style: cosine search with real ids, delete, save/load, and an IVF index
import os                                          # file handling
import tempfile                                    # safe temp folder
import numpy as np                                 # arrays
import faiss                                       # vector search


class VectorStore:
    """Cosine-similarity store that maps FAISS int ids to our own doc ids."""

    def __init__(self, dim: int) -> None:
        self.dim: int = dim                                        # vector size
        self.index: faiss.IndexIDMap2 = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))   # inner product + custom ids
        self.docs: dict[int, str] = {}                             # id -> text

    @staticmethod
    def _prep(x: np.ndarray) -> np.ndarray:
        x = np.ascontiguousarray(x, dtype="float32")               # FAISS wants C-contiguous float32
        faiss.normalize_L2(x)                                      # in place: unit length, so inner product = cosine
        return x

    def add(self, ids: list[int], texts: list[str], vecs: np.ndarray) -> None:
        if vecs.shape != (len(ids), self.dim):                     # validate shape early
            raise ValueError(f"expected {(len(ids), self.dim)}, got {vecs.shape}")
        self.index.add_with_ids(self._prep(vecs), np.array(ids, dtype="int64"))   # store with our ids
        self.docs.update(dict(zip(ids, texts)))                    # remember the text

    def search(self, vec: np.ndarray, k: int = 3) -> list[tuple[str, float]]:
        scores, ids = self.index.search(self._prep(vec.reshape(1, -1)), k)   # one query row
        return [(self.docs[int(i)], round(float(s), 3))            # skip -1 padding
                for s, i in zip(scores[0], ids[0]) if i != -1]

    def remove(self, ids: list[int]) -> int:
        removed: int = self.index.remove_ids(np.array(ids, dtype="int64"))   # IDMap supports delete
        for i in ids:
            self.docs.pop(i, None)                                 # drop text too
        return int(removed)


store = VectorStore(3)                                             # 3-d toy embeddings
store.add([101, 102, 103], ["refund policy", "delivery time", "pizza menu"],
          np.array([[1, 0, 0], [0.9, 0.4, 0], [0, 0, 1]]))
print(store.search(np.array([2.0, 0.0, 0.0]), 2))                  # length of query does not matter
print(store.remove([101]), store.index.ntotal)                     # delete one id
try:
    store.add([1], ["bad"], np.zeros((1, 5)))                      # wrong dimension
except ValueError as e:
    print("Error:", e)

with tempfile.TemporaryDirectory() as tmp:                         # persist index to disk
    path: str = os.path.join(tmp, "docs.faiss")
    faiss.write_index(store.index, path)                           # save
    loaded = faiss.read_index(path)                                # load
    print(loaded.ntotal, os.path.getsize(path) > 0)

rng = np.random.default_rng(0)                                     # reproducible random data
data = rng.random((2000, 16), dtype="float32")                     # 2000 vectors, 16-d
quantizer = faiss.IndexFlatL2(16)                                  # used to assign clusters
ivf = faiss.IndexIVFFlat(quantizer, 16, 20)                        # 20 clusters (nlist)
ivf.train(data)                                                    # IVF must be trained first
ivf.add(data)                                                      # then add
ivf.nprobe = 5                                                     # search 5 of 20 clusters (speed vs recall)
exact = faiss.IndexFlatL2(16); exact.add(data)                     # ground truth
q = data[:100]                                                     # use 100 stored vectors as queries
_, ie = exact.search(q, 1)
_, ia = ivf.search(q, 1)
print("recall@1:", float((ie == ia).mean()))                       # 1.0 here since each query is in the data
print(ivf.is_trained, ivf.ntotal, ivf.nlist)

# Output (really executed):
# [('refund policy', 1.0), ('delivery time', 0.914)]
# 1 2
# Error: expected (1, 3), got (1, 5)
# 2 True
# recall@1: 1.0
# True 2000 20
```
Note: `recall@1 = 1.0` is optimistic because the queries are copies of stored vectors. With fresh queries and a small `nprobe`, recall is below 1.0; raise `nprobe` to improve it.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Library | `faiss-cpu` (official) | no official build; use `faiss-node` (community) or a server |
| Data type | NumPy `float32` array | `Float32Array` |
| Exact search | `IndexFlatL2` | write a loop or use a vector DB |
| Save/load | `faiss.write_index / read_index` | n/a in most cases |
| Ecosystem | LangChain, LlamaIndex support it | LangChain.js has a FAISS wrapper (uses faiss-node) |

```python
# Python way — vectorised, 4 lines
import numpy as np, faiss
idx = faiss.IndexFlatL2(2); idx.add(np.array([[0, 0], [1, 1]], dtype="float32"))
d, i = idx.search(np.array([[0.9, 0.9]], dtype="float32"), 1)
print(i[0][0])                                    # 1
```
```javascript
// JavaScript way — plain brute force (no built-in vector index)
const db = [[0, 0], [1, 1]];
const q = [0.9, 0.9];
const dist = (a, b) => a.reduce((s, x, k) => s + (x - b[k]) ** 2, 0);
const best = db.map((v, i) => [dist(v, q), i]).sort((a, b) => a[0] - b[0])[0][1];
console.log(best);                                // 1
```

Key difference: Python has first-class FAISS and NumPy. In JS you usually call a Python service or a vector DB instead.

---

## 🟠 FastAPI Connection
Load the FAISS index once at startup (a global or `lifespan`) and share it across requests. A search is CPU-bound and fast, so a plain `def` endpoint (threadpool) is fine. FAISS searches are thread-safe for read-only use; do not call `add()` while other threads search without a lock.

```python
# FastAPI example — similar-document endpoint (tested with TestClient)
import numpy as np
import faiss
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()
DOCS: list[str] = ["refund policy", "delivery time", "pizza menu"]
index = faiss.IndexFlatL2(2)                       # in real code: faiss.read_index("docs.faiss") at startup
index.add(np.array([[1, 0], [0, 1], [-1, 0]], dtype="float32"))


@app.get("/similar")
def similar(x: float, y: float, k: int = 1) -> list[str]:
    q = np.array([[x, y]], dtype="float32")        # build the query row
    _, ids = index.search(q, k)                    # nearest ids
    return [DOCS[i] for i in ids[0] if i != -1]    # map ids back to documents, skip padding


print(TestClient(app).get("/similar", params={"x": 0.9, "y": 0.1}).json())   # ['refund policy']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to normalise vectors when you want cosine similarity
✅ Correct: `faiss.normalize_L2(x)` before `add` and before `search`, then use `IndexFlatIP`

```python
# Wrong: inner product on raw vectors favours long vectors, it is NOT cosine
idx = faiss.IndexFlatIP(3); idx.add(raw_vectors)
# Right
faiss.normalize_L2(raw_vectors); idx.add(raw_vectors)   # and normalise the query too
```

❌ Mistake 2: Treating `-1` ids as real results and treating L2 distance as normal distance
✅ Correct: filter `-1`; remember `IndexFlatL2` returns SQUARED distance (a point 5 units away shows `25.0`)

```python
d, i = idx.search(q, 10)
# Wrong: DOCS[-1] silently returns the LAST document when fewer than 10 vectors exist
docs = [DOCS[j] for j in i[0]]
# Right
docs = [DOCS[j] for j in i[0] if j != -1]
```

❌ Mistake 3: Searching an IVF index that was never trained, or importing FAISS and PyTorch in one process on macOS
✅ Correct: call `train()` first; if you need both libraries on macOS, put them in different processes (or, as a last resort, set `KMP_DUPLICATE_LIB_OK=TRUE`, which is unsafe)

```python
ivf = faiss.IndexIVFFlat(faiss.IndexFlatL2(16), 16, 20)
# Wrong: ivf.add(data)  -> RuntimeError, index is not trained
# Right
ivf.train(data); ivf.add(data)
# In our test on macOS, `import faiss, torch` in the same script aborted with:
# OMP: Error #15: Initializing libomp.dylib, but found libomp.dylib already initialized.
```

---

## 🧠 Tricky Interview Question

```python
import numpy as np, faiss
ix = faiss.IndexFlatL2(2)
ix.add(np.array([[0, 0]], dtype="float32"))
d, i = ix.search(np.array([[3, 4]], dtype="float32"), 1)
print(d, i)
print(ix.search(np.array([[3, 4]], dtype="float32"), 3))
```
Answer (really executed):
```
[[25.]] [[0]]
(array([[2.5000000e+01, 3.4028235e+38, 3.4028235e+38]], dtype=float32), array([[ 0, -1, -1]]))
```
The point (3, 4) is 5 units from the origin, but FAISS returns `25.0` because `IndexFlatL2` gives the squared distance (no square root, which is faster and keeps the same ranking). When you ask for more neighbours than exist, the extra ids are `-1` and their distances are the float32 maximum (about 3.4e38). Take `np.sqrt` yourself if you need real distance.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Flat index and IVF?
A1: Flat compares the query with every vector: exact, O(n). IVF clusters the data (`nlist` cells) and searches only the `nprobe` nearest cells: approximate but much faster. IVF needs `train()`.

Q2: How do you do cosine similarity in FAISS?
A2: Normalise vectors to length 1 with `faiss.normalize_L2` and use `IndexFlatIP`. Inner product of unit vectors equals cosine similarity.

Q3: Does FAISS store my text or metadata?
A3: No. It stores only vectors. You keep a separate mapping (dict, SQL table) from FAISS ids to documents. `IndexIDMap` lets you use your own int64 ids.

Q4: FAISS vs Pinecone?
A4: FAISS is a library inside your process: free, fast, you handle persistence, scaling and filters. Pinecone is a managed service with metadata filtering, namespaces and auto-scaling but costs money and adds network latency.

Q5: How do you trade speed vs accuracy?
A5: Choose an approximate index (IVF, HNSW, PQ) and tune parameters: `nprobe` for IVF, `efSearch` for HNSW. Measure recall against a Flat index on a sample of queries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want fast nearest-neighbour search inside your own service
- Dataset fits on one machine (up to hundreds of millions of vectors with compression)
- Prototypes, offline batch jobs, RAG for small and medium corpora

❌ Avoid when:
- You need rich metadata filtering, frequent updates or deletes at scale (use a vector DB)
- Several servers must share one live index (FAISS is a local library)
- You have only a few hundred vectors: plain NumPy dot product is enough

---

## 📊 Visual Diagram
```
 Flat (exact)                         IVF (approximate)
 query ─► compare with ALL n          vectors grouped into nlist clusters
          vectors                                  ● ● ●   ● ●   ●
          slow for big n               query ─► find nearest clusters (nprobe=2)
                                                 └─► compare only inside those
 search() returns:
   distances [[0.0025, 0.0125, 1.9025]]   (squared L2)
   ids       [[0,      1,      2     ]]   (-1 = no result)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Data structure that makes search fast | Search तेज करने वाली data structure |
| Flat | Exact brute-force index | सटीक brute-force index |
| IVF / nlist | Clustered index / number of clusters | Cluster वाला index / clusters की संख्या |
| nprobe | Clusters searched per query | हर query में खोजे गए clusters |
| Recall | Share of true neighbours found | असली पड़ोसियों में से कितने मिले |
| float32 | Required number type | जरूरी number type |

---

## ⚡ 3-Line Summary
English: FAISS is an in-process library for fast nearest-neighbour search on float32 NumPy arrays. Use Flat for exact results, IVF or HNSW for speed, normalise vectors for cosine, and keep your own id-to-document mapping. L2 distances are squared and missing results come back as `-1`.
Hindi: FAISS float32 NumPy arrays पर तेज nearest-neighbour search के लिए in-process library है। सटीक नतीजों के लिए Flat, speed के लिए IVF या HNSW लें, cosine के लिए vectors normalise करें, और id से document का mapping खुद रखें। L2 distances squared होते हैं और missing results `-1` आते हैं।

---

## ➡️ Next Topic
**396. tiktoken** — count and split text into tokens the way OpenAI models do, so you can control cost and context-window limits.
