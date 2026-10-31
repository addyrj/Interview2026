---

# 128. ANN — Approximate Nearest Neighbor
# हिंदी में: ANN — लगभग सबसे पास वाला पड़ोसी

---

## 🔵 Simple Definition (English)
Approximate Nearest Neighbor (ANN) search finds vectors that are very likely among the closest to the query, without checking every vector. It trades a tiny loss of accuracy (recall, e.g. 97%) for a huge gain in speed (10x to 1000x faster). Almost every vector database uses ANN.

## 🔵 सरल परिभाषा (Hindi)
ANN search ऐसे vectors ढूँढता है जो बहुत संभावना से सबसे पास वालों में होते हैं, बिना हर vector check किए। थोड़ी accuracy (recall, जैसे 97%) के बदले बहुत ज़्यादा speed (10x से 1000x) मिलती है। लगभग हर vector database ANN use करता है।

---

## 🔴 Problem it Solves
Exact k-NN must compare the query with all N vectors. For N = 100M and d = 768 that is 76 billion operations per query; latency would be seconds and CPU cost huge. The "curse of dimensionality" also makes classic tree indexes (KD-tree) useless above ~20 dimensions. ANN gives sub-10 ms queries by looking only at promising regions.

## 🔴 यह क्यों बना? (Hindi)
Exact k-NN को सभी N vectors से compare करना पड़ता है। N = 10 करोड़, d = 768 पर हर query में 76 अरब operations, यानी seconds की latency। "Curse of dimensionality" के कारण KD-tree जैसे indexes ~20 dimensions के बाद बेकार हो जाते हैं। ANN सिर्फ़ promising regions देखकर 10 ms से कम में जवाब देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build time: organise vectors into a structure (graph, clusters, hash buckets, trees)
Step 2 → Query time: jump quickly to the region of space near the query
Step 3 → Collect a small candidate set (hundreds, not millions)
Step 4 → Compute exact distances only for the candidates
Step 5 → Return the best k among candidates (may miss a few true neighbours)
Step 6 → Measure recall@k = (true neighbours found) / k against brute force
Step 7 → Tune knobs (ef_search, nprobe, number of trees) to balance recall vs latency vs memory
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Build time: vectors को structure में रखो (graph, clusters, hash buckets, trees)
Step 2 → Query time: query के पास वाले region पर जल्दी पहुँचो
Step 3 → छोटा candidate set (सैकड़ों, लाखों नहीं) इकट्ठा करो
Step 4 → सिर्फ़ candidates की exact distance निकालो
Step 5 → Candidates में से best k लौटाओ (कुछ true neighbours छूट सकते हैं)
Step 6 → Brute force से तुलना करके recall@k नापो
Step 7 → Knobs (ef_search, nprobe, trees) tune करके recall, latency, memory balance करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 5M historical customs declarations are indexed. Brute force takes 800 ms on one machine. With an HNSW index, the same query takes 6 ms at 98% recall. Missing 2% of true neighbours is fine because the LLM only needs a few good examples, not the mathematically exact top 5.

**Zomato AI**: dish search over 50M dish/restaurant vectors must respond within 50 ms at lunch peak, so ANN is mandatory.

## 🟡 Real Example Hindi mein
**Tariff System**: 50 लाख पुराने declarations index हैं। Brute force में 800 ms लगते हैं। HNSW index से वही query 98% recall पर 6 ms में होती है। 2% true neighbours छूटना ठीक है क्योंकि LLM को कुछ अच्छे examples चाहिए, गणितीय रूप से exact top 5 नहीं। **Zomato**: 5 करोड़ dish vectors पर lunch peak में 50 ms के अंदर जवाब चाहिए, इसलिए ANN ज़रूरी है।

---

## 💻 Code Example — Basic
```python
# Basic: a toy ANN using random-hyperplane LSH, compared with exact search.
# Pure Python, runs offline. Shows speed idea + recall measurement.
import random                                        # random hyperplanes and data
from collections import defaultdict                  # bucket table
from typing import Dict, List, Tuple                 # type hints

random.seed(7)                                       # reproducible demo
DIM, N, PLANES = 16, 2000, 3                         # dims, vectors, hash bits (fewer bits = bigger buckets = higher recall)

def rand_vec() -> List[float]:
    return [random.gauss(0, 1) for _ in range(DIM)]  # random Gaussian vector

def dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))          # dot product

data: List[List[float]] = [rand_vec() for _ in range(N)]     # the "database"
planes: List[List[float]] = [rand_vec() for _ in range(PLANES)]  # random hyperplanes

def signature(v: List[float]) -> Tuple[int, ...]:
    return tuple(1 if dot(v, p) > 0 else 0 for p in planes)  # which side of each plane

buckets: Dict[Tuple[int, ...], List[int]] = defaultdict(list)  # signature -> vector ids
for i, v in enumerate(data):                         # build the index
    buckets[signature(v)].append(i)                  # place vector in its bucket

def exact(q: List[float], k: int) -> List[int]:
    return sorted(range(N), key=lambda i: -dot(q, data[i]))[:k]  # scan all N

def approx(q: List[float], k: int) -> List[int]:
    cand = buckets.get(signature(q), [])             # only the query's bucket
    return sorted(cand, key=lambda i: -dot(q, data[i]))[:k]  # exact rank inside bucket

hits = total = scanned = 0                           # counters for recall + work
for _ in range(50):                                  # 50 random queries
    q = rand_vec()                                   # new query
    truth, found = set(exact(q, 5)), set(approx(q, 5))  # compare result sets
    hits += len(truth & found); total += 5           # recall bookkeeping
    scanned += len(buckets.get(signature(q), []))    # candidates we really scored
print(f"recall@5 = {hits/total:.2f}, avg scanned = {scanned/50:.0f} of {N}")  # observed ~0.38 recall scanning ~14% of data; real LSH uses many tables
```

## 💻 Code Example — Advanced
```python
# Advanced: benchmark harness to pick ANN parameters by measuring recall vs latency.
# Works with ANY index object that has .search(query, k) -> list of ids.
import asyncio                                         # async wrapper
import logging                                         # logging
import statistics                                      # p50/p95
import time                                            # timing
from typing import Callable, List, Protocol, Sequence  # type hints

log = logging.getLogger("ann-bench")                   # logger

class Index(Protocol):
    def search(self, q: Sequence[float], k: int) -> List[int]: ...   # minimal interface

def recall_at_k(truth: List[List[int]], found: List[List[int]], k: int) -> float:
    if not truth or len(truth) != len(found):          # validate shapes
        raise ValueError("truth and found must be non-empty and equal length")
    ok = sum(len(set(t[:k]) & set(f[:k])) for t, f in zip(truth, found))  # overlap per query
    return ok / (k * len(truth))                       # fraction of true neighbours found

def benchmark(index: Index, queries: List[Sequence[float]], truth: List[List[int]], k: int = 10) -> dict:
    lat: List[float] = []                              # latencies in ms
    found: List[List[int]] = []                        # results per query
    for q in queries:                                  # run all queries
        t0 = time.perf_counter()                       # start timer
        try:
            found.append(index.search(q, k))           # ANN search
        except Exception as exc:                       # one failure should not kill the benchmark
            log.error("query failed: %s", exc)         # log it
            found.append([])                           # count as zero recall
        lat.append((time.perf_counter() - t0) * 1000)  # ms
    lat.sort()                                         # for percentiles
    return {
        "recall": round(recall_at_k(truth, found, k), 3),          # quality
        "p50_ms": round(statistics.median(lat), 2),                # typical latency
        "p95_ms": round(lat[int(0.95 * (len(lat) - 1))], 2),       # tail latency
    }

async def sweep(make_index: Callable[[int], Index], knob_values: List[int], queries, truth) -> List[dict]:
    """Try several knob values (e.g. ef_search) and return the recall/latency table."""
    rows = []
    for v in knob_values:                              # each setting
        idx = make_index(v)                            # build / configure index
        res = await asyncio.to_thread(benchmark, idx, queries, truth)  # off the event loop
        rows.append({"knob": v, **res})                # collect row
    return rows
# Rule: pick the cheapest knob value that meets your recall target (e.g. >= 0.95) at p95 < SLA.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query                    # FastAPI

app = FastAPI()                                        # app

@app.get("/search")                                    # ANN search route with a recall/speed knob
async def search(q: str, k: int = Query(5, ge=1, le=50), accurate: bool = False) -> dict:
    # `accurate=True` raises the search effort (e.g. ef_search=200); default is the fast setting (ef=40).
    effort = 200 if accurate else 40                   # the ANN knob exposed to callers
    # vec = await embed(q); hits = index.search(vec, k, ef=effort)   <- plug your DB client here
    return {"query": q, "k": k, "effort": effort}      # return config so it is observable
```

---

## 🔗 LangChain / LangGraph Connection
Retrievers in LangChain pass ANN parameters through `search_kwargs`. In LangGraph you can add a conditional edge: if the first fast search returns low scores, re-run with a higher-effort setting.

```python
from langchain_community.vectorstores import FAISS         # FAISS-backed store (pip install faiss-cpu)
from langchain_openai import OpenAIEmbeddings               # embeddings

vs = FAISS.from_texts(["Headphones 8518.30", "Shirts 6205"], OpenAIEmbeddings())  # build index
retriever = vs.as_retriever(search_kwargs={"k": 3, "fetch_k": 20})   # fetch_k = candidate pool size
docs = retriever.invoke("wireless earbuds")                          # ANN/flat search + top-k
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using ANN defaults without measuring recall
✅ Correct: build a ground truth with brute force on a sample and measure.

```python
# Wrong: "it's fast, ship it"
# Right: compare against exact search on 1,000 sample queries
print("recall@10:", recall_at_k(truth_ids, ann_ids, 10))   # must meet your target
```

❌ Mistake 2: Using ANN for tiny datasets
✅ Correct: under ~10k-50k vectors, exact search is fast and has 100% recall.

```python
# Wrong: building HNSW for 3,000 vectors
# Right: numpy / flat index
scores = matrix @ query            # exact, simple, perfect recall
```

---

## 🧠 Tricky Interview Question

**Q**: "Your ANN index has 99% recall in benchmarks, but users complain a specific document is never found. How is that possible?"

**Answer**: Recall is an average. A specific vector can be consistently unreachable (e.g. an isolated node in an HNSW graph, or sitting in a poorly-assigned IVF cluster that is never probed). It can also be excluded by filtering: with post-filtering or restrictive filters, the candidate pool can run out. Check by querying with that document's own vector (should return itself), raise ef_search/nprobe, inspect the filter strategy, and rebuild the index if many deletes degraded the graph.

---

## ⚫ Interview Questions + Answers

Q1: What does "approximate" mean in ANN?
A1: The returned neighbours are usually, but not always, the true closest ones. We accept a small recall loss for big speed gains.

Q2: What is recall@k?
A2: The fraction of the true top-k neighbours (from exact search) that the ANN search returned. 0.95 means 95% overlap.

Q3: Name the main ANN families.
A3: Graph-based (HNSW), cluster-based (IVF), hashing (LSH), tree-based (Annoy), and compression-based (Product Quantisation, often combined with IVF as IVF-PQ or with graphs as DiskANN).

Q4: Why do KD-trees fail for embeddings?
A4: In high dimensions almost all points are about equally distant (curse of dimensionality), so tree pruning stops working and the search degenerates into scanning everything.

Q5: How do you choose an ANN algorithm and parameters for 50M vectors with a 20 ms budget?
A5: Estimate memory first: 50M x 768 x 4 bytes = 150 GB raw, too large for one RAM node, so use quantisation (PQ/SQ cut 4-32x) or disk-based DiskANN, or shard. Candidates: IVF-PQ (small, moderate recall) or sharded HNSW (high recall, bigger memory). Benchmark recall vs p95 latency on real queries with the real filters, choose the cheapest configuration that hits recall >= 0.95 and p95 < 20 ms, and monitor recall periodically as data changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than ~100k vectors or strict latency SLAs
- Interactive search/RAG at scale

❌ Avoid when:
- Small datasets (use exact search)
- Legal/compliance cases that need guaranteed exact results

---

## 📊 Visual Diagram
```
 EXACT (brute force)                 ANN (index)
 ┌───────────────────────┐          ┌───────────────────────┐
 │ q vs v1, v2, ... vN   │          │ q -> jump to region   │
 │ N comparisons         │          │ ~200 comparisons      │
 │ recall 100%, 800 ms   │          │ recall ~97%, 6 ms     │
 └───────────────────────┘          └───────────────────────┘

 Recall ▲                       knob: ef_search / nprobe ↑
   1.0 ─┤            ●────●            recall ↑  latency ↑  memory same
  0.95 ─┤        ●                      pick the knee of the curve
   0.80 ─┤  ●
        └─────────────────► latency
```

---

## 💰 Cost Impact
- Compute: ANN cuts per-query CPU by 10-1000x, so a service that needed 20 machines can run on 1-2.
- Memory: HNSW stores raw vectors plus graph links (~+30%); 10M x 1536 floats = ~61 GB + graph. Quantisation (int8, PQ) shrinks this 4-32x with a small recall loss.
- LLM tokens: no direct token cost. Indirect: higher recall means fewer retrieval misses, so fewer retries and fewer long prompts. A 3-point recall gain can save more in LLM retries than the extra memory costs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ANN | Approximate nearest neighbour | लगभग निकटतम पड़ोसी |
| Exact k-NN | Compare against all vectors | सभी से तुलना |
| Recall@k | Share of true neighbours found | सही पड़ोसियों में से मिले हुए का अनुपात |
| Curse of dimensionality | Distances lose meaning in high dims | ज़्यादा dimensions में दूरी का अर्थ घटना |
| LSH | Locality-sensitive hashing | पास की चीज़ों को एक bucket में डालना |
| Quantisation | Compress vectors | Vectors को compress करना |
| Latency p95 | 95% of queries finish faster than this | 95% queries इससे तेज़ |

---

## ⚡ 3-Line Summary
English: ANN finds almost-the-closest vectors by checking only a small candidate set. You trade a little recall for massive speed and cost savings. Always measure recall against brute force and tune the knobs.
Hindi: ANN सिर्फ़ छोटे candidate set को check करके लगभग सबसे पास वाले vectors ढूँढता है। थोड़ा recall देकर बहुत speed और cost बचत मिलती है। हमेशा brute force से recall नापो और knobs tune करो।

---

## ➡️ Next Topic
**129. HNSW Algorithm** — the most popular graph-based ANN index: layers, M, efConstruction and ef_search.
