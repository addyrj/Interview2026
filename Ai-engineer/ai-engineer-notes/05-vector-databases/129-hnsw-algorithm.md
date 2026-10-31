---

# 129. HNSW Algorithm
# हिंदी में: HNSW Algorithm (Hierarchical Navigable Small World)

---

## 🔵 Simple Definition (English)
HNSW is a graph-based ANN index. Every vector is a node connected to nearby nodes. The graph has several layers: the top layer is sparse (long jumps), the bottom layer is dense (fine detail). Search starts at the top, greedily walks toward the query, drops a layer, repeats, and finishes at the bottom. It is fast and has very high recall.

## 🔵 सरल परिभाषा (Hindi)
HNSW graph-based ANN index है। हर vector एक node है जो पास के nodes से जुड़ा है। Graph में कई layers होती हैं: ऊपर की layer sparse (लंबी छलाँगें), नीचे की layer dense (बारीक detail)। Search ऊपर से शुरू होकर query की तरफ़ चलता है, एक layer नीचे आता है और आख़िर में सबसे नीचे पहुँचता है। यह तेज़ है और recall बहुत high देता है।

---

## 🔴 Problem it Solves
Brute force is too slow, and tree/hash methods lose accuracy in high dimensions. A plain "small world" graph can get stuck far from the target or need many hops. HNSW adds a hierarchy (like a skip list or a road map: highway first, then streets) so the walk reaches the right neighbourhood in O(log N) hops.

## 🔴 यह क्यों बना? (Hindi)
Brute force धीमा है, और trees/hashing high dimensions में accuracy खो देते हैं। साधारण small-world graph में walk target से दूर अटक सकती है या बहुत hops लगते हैं। HNSW hierarchy जोड़ता है (skip list या road map की तरह: पहले highway, फिर गलियाँ), जिससे O(log N) hops में सही neighbourhood मिल जाती है।

---

## 🟢 How it Works — Step by Step

```
Insert:
Step 1 → Pick a random max layer L for the new vector (exponentially decaying: most get 0)
Step 2 → From the entry point at the top layer, greedy-walk down to layer L+1
Step 3 → On each layer <= L, search with ef_construction candidates
Step 4 → Connect the new node to its best M neighbours (bidirectional links, pruned)

Query:
Step 5 → Start at the entry point on the top layer
Step 6 → Greedy move to the neighbour closest to the query until no improvement
Step 7 → Go down one layer, continue from that node
Step 8 → On layer 0, keep a candidate list of size ef_search, expand best-first
Step 9 → Return the k best of that list
```

## 🟢 कैसे काम करता है? (Hindi)

```
Insert:
Step 1 → नए vector की random max layer L चुनो (ज़्यादातर की 0 होती है)
Step 2 → Top layer के entry point से greedy चलकर layer L+1 तक आओ
Step 3 → Layer <= L पर ef_construction candidates से search करो
Step 4 → सबसे अच्छे M neighbours से दोनों तरफ़ links बनाओ

Query:
Step 5 → Top layer के entry point से शुरू करो
Step 6 → Query के सबसे पास वाले neighbour की तरफ़ चलो जब तक सुधार हो
Step 7 → एक layer नीचे जाओ और उसी node से आगे बढ़ो
Step 8 → Layer 0 पर ef_search size की candidate list best-first expand करो
Step 9 → उस list से सबसे अच्छे k लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 3M declaration embeddings in Qdrant using HNSW (`m=16`, `ef_construct=200`). With `hnsw_ef=64` at query time, p95 latency is ~8 ms at ~97% recall. Raising `hnsw_ef` to 256 for hard "ambiguous product" queries pushes recall to ~99.5% at ~25 ms.

**Amazon-style**: "similar products" for 100M items; HNSW shards live in RAM so recommendation calls finish in a few ms.

## 🟡 Real Example Hindi mein
**Tariff System**: 30 लाख declaration embeddings Qdrant में HNSW (`m=16`, `ef_construct=200`) से। Query पर `hnsw_ef=64` से p95 ~8 ms और ~97% recall। मुश्किल "ambiguous product" queries के लिए `hnsw_ef=256` करने पर recall ~99.5% और latency ~25 ms। **Amazon-style**: 10 करोड़ items के "similar products" के लिए HNSW shards RAM में रहते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: single-layer "navigable small world" greedy search (the core idea of HNSW).
# Pure Python, offline. (Real HNSW adds layers; this shows the graph walk.)
import heapq                                          # priority queue for best-first search
import math                                           # sqrt for distance
import random                                         # random data
from typing import Dict, List, Set                    # type hints

random.seed(1)                                        # reproducible
Point = List[float]                                   # vector type

def dist(a: Point, b: Point) -> float:
    return math.dist(a, b)                            # Euclidean distance (py3.8+)

N, M = 500, 8                                         # points, max links per node
pts: List[Point] = [[random.random(), random.random()] for _ in range(N)]  # 2-D data
graph: Dict[int, Set[int]] = {i: set() for i in range(N)}   # adjacency lists

def search(q: Point, entry: int, ef: int) -> List[int]:
    visited = {entry}                                 # nodes already seen
    cand = [(dist(q, pts[entry]), entry)]             # min-heap of candidates to expand
    best = [(-dist(q, pts[entry]), entry)]            # max-heap (negated) of best ef results
    while cand:                                       # best-first expansion
        d, u = heapq.heappop(cand)                    # closest unexpanded candidate
        if len(best) >= ef and d > -best[0][0]:       # worse than our worst kept result
            break                                     # no way to improve: stop
        for v in graph[u]:                            # look at neighbours of u
            if v in visited:                          # skip repeats
                continue
            visited.add(v)                            # mark seen
            dv = dist(q, pts[v])                      # distance to query
            if len(best) < ef or dv < -best[0][0]:    # promising neighbour
                heapq.heappush(cand, (dv, v))         # expand it later
                heapq.heappush(best, (-dv, v))        # remember as a result
                if len(best) > ef:                    # keep only ef best
                    heapq.heappop(best)               # drop the worst
    return [i for _, i in sorted((-d, i) for d, i in best)]   # nearest first

for i in range(1, N):                                 # insert points one by one
    near = search(pts[i], 0, ef=20)[:M]               # find M nearest among inserted points
    for j in near:                                    # link both directions
        graph[i].add(j); graph[j].add(i)              # undirected edge

q: Point = [0.5, 0.5]                                 # a query point
approx = search(q, 0, ef=30)[:5]                      # graph search
exact = sorted(range(N), key=lambda i: dist(q, pts[i]))[:5]  # brute force truth
print("approx:", approx, "exact:", exact, "overlap:", len(set(approx) & set(exact)), "/5")
```

## 💻 Code Example — Advanced
```python
# Advanced: HNSW with the hnswlib library (pip install hnswlib numpy)
# Shows M, ef_construction, ef (query), persistence, batch add, error handling, async wrapper.
import asyncio                                         # async runtime
import logging                                         # logs
from pathlib import Path                               # file paths
from typing import List, Tuple                         # type hints

import hnswlib                                         # fast C++ HNSW
import numpy as np                                     # arrays

log = logging.getLogger("hnsw")                        # logger

class HNSWIndex:
    def __init__(self, dim: int, max_elements: int = 100_000, m: int = 16, ef_construction: int = 200) -> None:
        self.dim = dim                                 # vector dimension
        self.index = hnswlib.Index(space="cosine", dim=dim)   # cosine distance space
        self.index.init_index(max_elements=max_elements, M=m, ef_construction=ef_construction)  # build params
        self.index.set_ef(64)                          # default query-time effort

    def add(self, vectors: np.ndarray, ids: List[int]) -> None:
        if vectors.shape[1] != self.dim:               # dimension check
            raise ValueError(f"expected dim {self.dim}, got {vectors.shape[1]}")
        self.index.add_items(vectors.astype("float32"), np.array(ids))   # batch insert

    def search(self, query: np.ndarray, k: int = 5, ef: int | None = None) -> List[Tuple[int, float]]:
        if ef:                                         # per-call recall/speed override
            self.index.set_ef(max(ef, k))              # ef must be >= k
        try:
            labels, dists = self.index.knn_query(query.astype("float32"), k=k)   # ANN search
        except RuntimeError as exc:                    # raised when k > number of elements
            log.error("hnsw query failed: %s", exc)    # log it
            return []                                  # safe fallback
        return [(int(l), float(1 - d)) for l, d in zip(labels[0], dists[0])]    # cosine sim = 1 - dist

    def save(self, path: str) -> None:
        self.index.save_index(path)                    # write index to disk

    def load(self, path: str, max_elements: int = 100_000) -> None:
        if not Path(path).exists():                    # fail clearly if file missing
            raise FileNotFoundError(path)
        self.index.load_index(path, max_elements=max_elements)   # read index back

    async def search_async(self, query: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        return await asyncio.to_thread(self.search, query, k)    # keep event loop responsive

# Memory estimate: ~ N * (dim*4 + M*2*4) bytes. 1M x 768 dims, M=16 -> ~3.2 GB.
# Token usage: 0 LLM tokens; only the query embedding is paid for.
```

---

## 🟠 FastAPI Integration
```python
import numpy as np                                    # arrays
from fastapi import FastAPI                            # FastAPI
from pydantic import BaseModel, Field                  # pydantic v2

app = FastAPI()                                        # app
idx = HNSWIndex(dim=384)                               # load once at startup (shared)

class Query(BaseModel):
    vector: list[float] = Field(min_length=384, max_length=384)   # exact dim
    k: int = Field(5, ge=1, le=100)                    # bounded k
    ef: int = Field(64, ge=10, le=512)                 # recall/speed knob

@app.post("/hnsw/search")                              # route
async def hnsw_search(body: Query) -> dict:
    q = np.array([body.vector])                        # shape (1, dim)
    hits = await idx.search_async(q, body.k)           # non-blocking search
    return {"hits": [{"id": i, "score": s} for i, s in hits], "ef": body.ef}
```

---

## 🔗 LangChain / LangGraph Connection
Most LangChain vector stores use HNSW under the hood (Chroma, Qdrant, Weaviate, pgvector HNSW, FAISS `IndexHNSWFlat`). You can configure it per store.

```python
from langchain_chroma import Chroma                    # pip install langchain-chroma
from langchain_openai import OpenAIEmbeddings          # embeddings

vs = Chroma(                                           # Chroma uses HNSW internally
    collection_name="tariff",                          # collection name
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 200},  # HNSW params
)
# LangGraph tip: expose `ef`/`k` in graph state so a "retry with higher recall" edge can raise them.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `ef_search` smaller than `k`
✅ Correct: always set `ef >= k` (usually 2-10 times k).

```python
# Wrong: ef=5 but k=10 -> cannot even return 10 results reliably
index.set_ef(5); index.knn_query(q, k=10)
# Right
index.set_ef(64); index.knn_query(q, k=10)
```

❌ Mistake 2: Ignoring memory (HNSW lives in RAM) and heavy deletes
✅ Correct: budget RAM, use quantisation if needed, rebuild periodically after many deletes.

```python
# Wrong: 100M x 1536 vectors in one HNSW node (~600 GB RAM)
# Right: shard, or use scalar/product quantisation, or an on-disk index
```

---

## 🧠 Tricky Interview Question

**Q**: "You double `M` from 16 to 32. What changes, and is it always better?"

**Answer**: Each node keeps more links, so recall rises (more routes through the graph) especially for high-dimensional or clustered data. But memory grows (more links per node), build time increases, and each hop evaluates more neighbours so queries can get slower for the same `ef`. It is not always better: after a point recall saturates. Tune `M` (12-48), `ef_construction` (100-400) and `ef_search` together using recall-vs-latency curves on real data.

---

## ⚫ Interview Questions + Answers

Q1: What does HNSW stand for?
A1: Hierarchical Navigable Small World, a multi-layer proximity graph for approximate nearest neighbour search.

Q2: What are the three key parameters?
A2: `M` (links per node), `ef_construction` (candidate list size while building) and `ef_search` (candidate list size while querying). Higher means better recall but more time or memory.

Q3: Why is the layered structure useful?
A3: Upper layers have few nodes and long edges so the search crosses the space in a few hops; lower layers refine locally. It gives roughly logarithmic search time like a skip list.

Q4: What are HNSW's weaknesses?
A4: High RAM usage, slow index build, awkward deletes (nodes are marked or the graph degrades), and filtered search can lose recall when filters are very selective.

Q5: Compare HNSW and IVF for a 100M-vector workload.
A5: HNSW gives the best recall/latency but needs the full graph plus vectors in RAM (huge at 100M). IVF clusters the data and probes `nprobe` clusters, so it builds fast and uses less memory, especially with PQ, but has lower recall at the same latency and needs training. At 100M, teams commonly pick IVF-PQ or DiskANN, or shard HNSW across machines when recall matters most.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need top recall at low latency, data fits in RAM
- Data is updated incrementally (inserts are easy)

❌ Avoid when:
- Memory is tight or data is billions of vectors (consider IVF-PQ/DiskANN)
- Frequent bulk deletes or very selective filters without filtered-HNSW support

---

## 📊 Visual Diagram
```
 Layer 2 (sparse):   A ─────────────────────► E
                     │                         │
 Layer 1:            A ───► C ─────► E ──► G   │
                     │      │        │     │   │
 Layer 0 (all nodes):A─B─C─D─E─F─G─H─I─J─K─L ...

 Query q near "I":  start A(L2) ─► E(L2) ─drop─► E(L1) ─► G(L1) ─drop─► G(L0) ─► H ─► I ✓
 Few hops on top, fine search at the bottom.
```

---

## 💰 Cost Impact
- RAM dominates cost. Rough size = N x (4 x dim + ~8 x M) bytes. 10M x 1536 dims, M=16 = ~62 GB. On a cloud RAM-optimised machine that can be hundreds of dollars per month.
- Reduce with lower dimensions (OpenAI `dimensions=512` cuts 3x), int8 quantisation (4x), or smaller `M`.
- Query-time `ef` is a free knob: a lower `ef` saves CPU; raise it only for hard queries.
- No LLM token cost in the index itself. Better recall means fewer irrelevant chunks, which reduces prompt tokens (e.g. 5 good chunks = ~1,500 tokens instead of 10 mixed chunks = ~3,000).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Node | One vector in the graph | Graph में एक vector |
| M | Max neighbours per node | हर node के अधिकतम neighbours |
| efConstruction | Candidate list size on build | Build के समय candidate list का आकार |
| ef_search | Candidate list size on query | Query के समय candidate list का आकार |
| Layer | Level of the hierarchy | Hierarchy का स्तर |
| Entry point | Top-layer start node | शुरुआती node |
| Greedy search | Always move to the closest neighbour | हमेशा सबसे पास वाले की तरफ़ चलना |

---

## ⚡ 3-Line Summary
English: HNSW is a layered proximity graph: coarse jumps at the top, fine search at the bottom. Tune M, efConstruction and ef_search for the recall/latency/memory balance. It is the default, high-recall ANN index but costs RAM.
Hindi: HNSW layers वाला proximity graph है: ऊपर बड़ी छलाँगें, नीचे बारीक search। Recall, latency और memory के balance के लिए M, efConstruction, ef_search tune करो। यह default high-recall ANN index है पर RAM ज़्यादा लेता है।

---

## ➡️ Next Topic
**130. IVF Algorithm** — the cluster-based alternative that trades some recall for lower memory and faster builds.
