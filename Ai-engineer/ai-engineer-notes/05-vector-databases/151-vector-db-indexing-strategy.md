---

# 151. Vector DB Indexing Strategy
# हिंदी में: Vector DB Indexing Strategy

---

## 🔵 Simple Definition (English)
An index is a data structure that finds near vectors without comparing against every vector. Main types: FLAT (exact, compare all), IVF (cluster, search a few clusters) and HNSW (layered graph walk). Each trades recall, speed, memory and build time.

## 🔵 सरल परिभाषा (Hindi)
Index एक data structure है जो हर vector से compare किए बिना नज़दीकी vectors ढूँढता है। मुख्य प्रकार: FLAT (exact, सब compare), IVF (clusters, कुछ clusters में search) और HNSW (layered graph walk)। हर एक recall, speed, memory और build time में trade-off करता है।

---

## 🔴 Problem it Solves
Exact search costs O(N x d). With 10M vectors x 1536 dims, a single query is about 15 billion multiplications: too slow for real time. Approximate nearest neighbour (ANN) indexes cut this to a few thousand distance computations with a small recall loss.

## 🔴 यह क्यों बना? (Hindi)
Exact search की cost O(N x d) है। 1 करोड़ vectors x 1536 dims पर एक query में लगभग 15 अरब multiplications लगते हैं: real time के लिए बहुत धीमा। ANN indexes इसे कुछ हज़ार distance computations तक घटाते हैं, थोड़े recall नुकसान के साथ।

---

## 🟢 How it Works — Step by Step

```
FLAT : store raw vectors -> query compares ALL -> exact, slow at scale
IVF  : Step 1 k-means into nlist clusters  Step 2 assign each vector to its centroid
       Step 3 query finds nprobe nearest centroids  Step 4 scans only those lists
HNSW : Step 1 build multi-layer graph (m links per node)
       Step 2 query enters at top layer, greedily walks closer
       Step 3 at layer 0 explores ef_search candidates, returns top-k
Tuning: raise nprobe / ef_search for recall, lower for speed
```

## 🟢 कैसे काम करता है? (Hindi)

```
FLAT : raw vectors रखो -> query सबसे compare करती है -> exact, बड़े scale पर धीमा
IVF  : Step 1 k-means से nlist clusters  Step 2 हर vector को centroid में डालो
       Step 3 query nprobe सबसे नज़दीकी centroids ढूँढती है  Step 4 सिर्फ़ उन्हीं lists को scan
HNSW : Step 1 multi-layer graph बनाओ (हर node के m links)
       Step 2 query ऊपरी layer से greedy चलकर नज़दीक पहुँचती है
       Step 3 layer 0 पर ef_search candidates देखकर top-k लौटाती है
Tuning: recall के लिए nprobe / ef_search बढ़ाओ, speed के लिए घटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 20K HS descriptions need no ANN at all: FLAT gives exact results in under 5 ms. After ingesting 2M historical declarations, switch the declarations table to HNSW (m=16, ef_construction=64, ef_search=80) and keep the code table FLAT.

**Amazon-style catalog**: 300M products use IVF with product quantization (IVF-PQ) because HNSW would not fit in RAM.

## 🟡 Real Example Hindi mein
**Tariff System**: 20K HS descriptions को ANN की ज़रूरत ही नहीं: FLAT से 5 ms से कम में exact results। 20 लाख पुराने declarations आने के बाद उस table में HNSW (m=16, ef_construction=64, ef_search=80) लगाओ और code table को FLAT रखो।

**Amazon-style catalog**: 30 करोड़ products में IVF + product quantization (IVF-PQ) क्योंकि HNSW RAM में fit नहीं होगा।

---

## 💻 Code Example — Basic
```python
# Pure-Python demo (no libraries): FLAT exact search vs a toy IVF to show the recall/speed idea
import math
import random
import time

random.seed(7)  # reproducible
DIM, N = 16, 5000  # small so it runs in a second
data = [[random.gauss(0, 1) for _ in range(DIM)] for _ in range(N)]  # random vectors


def dist(a: list[float], b: list[float]) -> float:
    return math.dist(a, b)  # Euclidean distance


def flat_search(q: list[float], k: int) -> list[int]:
    ranked = sorted(range(N), key=lambda i: dist(q, data[i]))  # compare against ALL vectors
    return ranked[:k]


# Toy IVF: choose 50 random centroids, assign every vector to its nearest centroid
NLIST = 50
centroids = random.sample(data, NLIST)  # (real IVF uses k-means)
lists: dict[int, list[int]] = {c: [] for c in range(NLIST)}  # inverted lists
for i, v in enumerate(data):
    c = min(range(NLIST), key=lambda c: dist(v, centroids[c]))  # nearest centroid
    lists[c].append(i)


def ivf_search(q: list[float], k: int, nprobe: int) -> list[int]:
    near = sorted(range(NLIST), key=lambda c: dist(q, centroids[c]))[:nprobe]  # closest clusters
    cand = [i for c in near for i in lists[c]]  # only scan those lists
    return sorted(cand, key=lambda i: dist(q, data[i]))[:k]


queries = [[random.gauss(0, 1) for _ in range(DIM)] for _ in range(20)]
for nprobe in (1, 5, 15):  # more probes -> more recall, more time
    t = time.perf_counter()
    hits = sum(len(set(ivf_search(q, 10, nprobe)) & set(flat_search(q, 10))) for q in queries)
    print(f"nprobe={nprobe:>2} recall@10={hits / (10 * len(queries)):.2f} total_s={time.perf_counter() - t:.2f}")
```

## 💻 Code Example — Advanced
```python
# Production: choose and create the index by data size (pgvector), async, error handling
import logging
from psycopg_pool import AsyncConnectionPool

log = logging.getLogger("indexing")


def plan_index(rows: int) -> str:
    """Pick DDL by table size. Thresholds are starting points; always validate with recall tests."""
    if rows < 50_000:
        return ""  # no index: exact scan is fast and 100% recall
    if rows < 5_000_000:
        # HNSW: best speed/recall, more RAM and slower build
        return ("CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_vec ON declarations "
                "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")
    lists = int(rows ** 0.5)  # rule of thumb for IVFFlat: lists ~ sqrt(rows) (rows/1000 up to 1M)
    return (f"CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_vec ON declarations "
            f"USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists})")


async def ensure_index(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        await conn.set_autocommit(True)  # CREATE INDEX CONCURRENTLY cannot run inside a transaction
        cur = await conn.execute("SELECT count(*) FROM declarations")
        (rows,) = await cur.fetchone()  # row count
        ddl = plan_index(int(rows))
        if not ddl:
            log.info("table small: skipping index")
            return
        try:
            await conn.execute("SET maintenance_work_mem = '1GB'")  # faster graph build
            await conn.execute(ddl)
            log.info("index ready for %s rows", rows)
        except Exception:
            log.exception("index build failed")
            raise
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/admin/reindex")
async def reindex() -> dict[str, str]:
    """Protected admin route: rebuild the index after a bulk load (add auth in real life)."""
    try:
        await ensure_index(app.state.pool)  # from Advanced example
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "index ensured"}


@app.get("/search/tune")
async def tune(ef_search: int = 80) -> dict:
    """Per-request recall/speed knob; clamp it."""
    return {"ef_search": max(10, min(ef_search, 400))}
```

---

## 🔗 LangChain / LangGraph Connection
Most LangChain stores accept index parameters at creation. In `PGVector` you build the index in the database; some stores (FAISS, Chroma) expose HNSW settings through the client.

```python
# FAISS example: IVF index through LangChain's underlying faiss
import faiss
dim = 1536
quantizer = faiss.IndexFlatL2(dim)               # coarse quantizer
index = faiss.IndexIVFFlat(quantizer, dim, 100)  # nlist = 100
# index.train(np_vectors); index.add(np_vectors); index.nprobe = 10
# Pass this index into langchain_community.vectorstores.FAISS(...) or use it behind your own retriever node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building IVFFlat on an empty or tiny table
```python
# Wrong: clusters computed from few rows -> poor centroids, bad recall forever
#   CREATE INDEX ... USING ivfflat ... ;  (then load data)
# Right: load representative data first, then build the IVF index (HNSW does not need training)
```

❌ Mistake 2: Never re-measuring recall after changing data or params
```python
# Wrong: set m=8 to save RAM, assume everything is fine
# Right: keep a labelled query set; after every change compute recall@10 vs exact search
def recall(ann: list[int], exact: list[int]) -> float:
    return len(set(ann) & set(exact)) / len(exact)
```

---

## 🧠 Tricky Interview Question

**Q**: "HNSW gives 99 percent recall in tests, but in production with a strict metadata filter it drops to 60 percent. Why?"

**Answer**: HNSW is built over all vectors without knowing your filter. Filtering after the graph walk discards many candidates, so fewer than k valid results remain, and the filtered subgraph may be poorly connected. Solutions: engines with filter-aware traversal (Qdrant, Weaviate, Elasticsearch filtered kNN), larger `ef_search`, iterative scans (pgvector 0.8), partial indexes or partitions per frequent filter value (tenant, country), or fall back to exact scan when the filter is very selective.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between exact and approximate search?
A1: Exact (FLAT) checks every vector and gives 100 percent recall. Approximate indexes check a subset and give faster answers with a small recall loss.

Q2: What does `nprobe` mean in IVF?
A2: How many clusters are scanned per query. More probes means higher recall and higher latency.

Q3: Name the main HNSW parameters.
A3: `m` (links per node, memory and recall), `ef_construction` (build quality), `ef_search` (query-time candidates).

Q4: HNSW vs IVF trade-off?
A4: HNSW is faster and has better recall at the cost of memory and slower builds; IVF uses less memory, builds quickly and pairs well with quantization, but needs training and tuning `nprobe`.

Q5: How do you index 500M vectors on limited RAM?
A5: Use IVF-PQ or DiskANN-style disk-based indexes, scalar or binary quantization with re-scoring on full vectors, shard across nodes, and keep full-precision vectors on SSD. Validate recall at each step against a held-out exact baseline.

---

## 🔷 When to Use + When Not to Use
✅ Use ANN indexes when:
- More than roughly 50K to 100K vectors and latency matters

❌ Avoid when:
- Small collections: FLAT is simpler, exact and fast
- Data changes massively every hour and the index rebuild cost is high (IVF drifts)

---

## 📊 Visual Diagram
```
 FLAT      q ──► [v1][v2][v3] ... [vN]   compare all     exact, O(N)

 IVF       q ──► nearest centroids ──► c3, c7 ──► scan only lists 3 and 7

 HNSW   layer2:  o─────────────o
        layer1:  o───o───o─────o──o
        layer0:  o-o-o-o-o-o-o-o-o-o-o    q enters top, walks down greedily
```

---

## 💰 Cost Impact
- Index choice changes RAM and CPU bills, not token usage directly. HNSW needs roughly vectors + links in RAM (for example 1M x 1536 float32 is about 6 GB plus around 10-20 percent graph overhead).
- Poor recall forces larger k, so more chunks in the LLM prompt: each extra 300-token chunk costs tokens on every request. Good tuning reduces both.
- Optimise: quantization (int8 or binary) with rescoring, smaller dimensions, drop unused indexes, build indexes once after bulk loading.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ANN | Approximate nearest neighbour | अनुमानित निकटतम पड़ोसी |
| FLAT | Exact brute-force index | Exact brute-force index |
| IVF | Inverted file with clusters | Clusters वाला index |
| HNSW | Hierarchical navigable small world graph | Layered graph index |
| nprobe | Clusters scanned per query | प्रति query scan किए clusters |
| ef_search | HNSW query candidate list size | HNSW query candidates |
| PQ | Product quantization (compression) | Vectors compress करने की तकनीक |

---

## ⚡ 3-Line Summary
English: FLAT is exact, IVF scans selected clusters, HNSW walks a graph; each trades recall, speed and memory. Use FLAT for small data and HNSW for most production search. Always measure recall against exact search.
Hindi: FLAT exact है, IVF चुने हुए clusters scan करता है, HNSW graph पर चलता है; हर एक recall, speed और memory में trade-off करता है। छोटे data के लिए FLAT, ज़्यादातर production के लिए HNSW। Recall हमेशा exact search से नापो।

---

## ➡️ Next Topic
**152. Hybrid Search Setup** — combine keyword (BM25) and vector search with Reciprocal Rank Fusion.
