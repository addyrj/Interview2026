---

# 142. FAISS — Local Vector Search
# हिंदी में: FAISS — Local Vector Search (अपने ही machine पर semantic search)

---

## 🔵 Simple Definition (English)
Local vector search with FAISS means building a complete search feature on one machine: embed documents, build a FAISS index, save the index + a side file with texts/metadata, load it at startup, and answer queries in milliseconds with no database server. This note focuses on the end-to-end workflow: index types for different sizes, id mapping, metadata filtering patterns and persistence.

## 🔵 सरल परिभाषा (Hindi)
FAISS से local vector search का मतलब है एक ही machine पर पूरा search feature बनाना: documents embed करो, FAISS index बनाओ, index के साथ texts/metadata की side file save करो, startup पर load करो, और बिना database server के milliseconds में queries का जवाब दो। यह note end-to-end workflow पर है: अलग sizes के लिए index types, id mapping, metadata filtering patterns और persistence।

---

## 🔴 Problem it Solves
After learning FAISS basics, people get stuck on the practical gaps: "which index do I pick for 50k vs 5M vectors?", "how do I keep my text and metadata?", "how do I filter by country?", "how do I save and reload?", and "how do I rebuild safely?". A repeatable local workflow answers all of these for small and medium apps and batch jobs.

## 🔴 यह क्यों बना? (Hindi)
FAISS की basics सीखने के बाद लोग practical gaps में अटकते हैं: "50k बनाम 50 लाख vectors के लिए कौन सा index?", "text और metadata कैसे रखें?", "country से filter कैसे करें?", "save और reload कैसे?", और "rebuild सुरक्षित कैसे?" एक repeatable local workflow छोटे और मध्यम apps तथा batch jobs के लिए इन सबका जवाब देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load documents -> list of {id, text, metadata}
Step 2 → Embed all texts in batches -> float32 matrix (N, d); normalise rows (cosine)
Step 3 → Pick the index by size:
           N < ~100k   : IndexFlatIP          (exact, simplest)
           100k - 5M   : IndexHNSWFlat(d, 32) (fast, high recall, more RAM)
           5M +        : IndexIVFPQ / OPQ      (compressed; needs training)
Step 4 → Wrap with IndexIDMap2 if you want your own int ids and deletions (not for HNSW: no removal)
Step 5 → Save: faiss.write_index(index, "tariff.faiss") + docs.json (id -> text/metadata)
Step 6 → Startup: read_index + load docs.json into a dict
Step 7 → Query: embed, normalise, search k*3 candidates, post-filter by metadata, keep top k
Step 8 → Rebuild nightly from source of truth; write to a temp file, then atomically rename to swap
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Documents load करो -> {id, text, metadata} की list
Step 2 → सारे texts batches में embed करो -> float32 matrix (N, d); rows normalise (cosine)
Step 3 → Size के हिसाब से index:
           N < ~1 लाख   : IndexFlatIP          (exact, सबसे सरल)
           1 लाख - 50 लाख: IndexHNSWFlat(d, 32) (तेज़, high recall, ज़्यादा RAM)
           50 लाख+      : IndexIVFPQ / OPQ      (compressed; training ज़रूरी)
Step 4 → अपने int ids और deletions चाहिए तो IndexIDMap2 (HNSW में removal नहीं)
Step 5 → Save: faiss.write_index(index, "tariff.faiss") + docs.json (id -> text/metadata)
Step 6 → Startup: read_index + docs.json को dict में load
Step 7 → Query: embed, normalise, k*3 candidates search, metadata से post-filter, top k रखो
Step 8 → रात में source of truth से rebuild; temp file में लिखकर atomic rename से swap
```

---

## 🟡 Real World Example
**Tariff Classification System**: a CLI tool for customs officers on an air-gapped office PC (no internet, no database). A nightly build job exports `tariff.faiss` and `docs.json` (200k headings). The tool loads both in 2 seconds and answers "wireless earbuds" in 3 ms. Country filtering uses over-fetch + post-filter.

**Zomato AI**: an offline analyst notebook finds near-duplicate dish descriptions among 1M items using batch `index.search(all_vectors, 5)`.

## 🟡 Real Example Hindi mein
**Tariff System**: Air-gapped office PC पर customs officers के लिए CLI tool (internet या database नहीं)। Nightly build job `tariff.faiss` और `docs.json` (2 लाख headings) बनाता है। Tool दोनों 2 seconds में load करता है और "wireless earbuds" का जवाब 3 ms में देता है। Country filtering over-fetch + post-filter से। **Zomato**: Analyst notebook 10 लाख dish descriptions में near-duplicates `index.search(all_vectors, 5)` batch query से ढूँढता है।

---

## 💻 Code Example — Basic
```python
# Basic: a complete local semantic search that runs fully offline.
# We use a deterministic "hashing" embedding (bag of words) instead of a real model so no API key is needed.
# pip install faiss-cpu numpy
import hashlib                                                # stable hashing of words
import faiss                                                  # FAISS
import numpy as np                                            # arrays

D = 256                                                       # embedding size for the toy embedder

def embed(text: str) -> np.ndarray:
    """Toy embedding: hash each word into one of D buckets (NOT semantic; it only matches shared words)."""
    v = np.zeros(D, dtype="float32")                          # start with zeros
    for w in text.lower().split():                            # each word
        h = int(hashlib.md5(w.encode()).hexdigest(), 16)      # stable hash across runs
        v[h % D] += 1.0                                       # count into a bucket
    return v

docs = [                                                      # tiny corpus
    {"id": 10, "text": "wireless headphones and earphones", "country": "IN"},
    {"id": 11, "text": "cotton shirts for men", "country": "IN"},
    {"id": 12, "text": "smartphones and mobile phones", "country": "IN"},
    {"id": 13, "text": "wireless headphones for export", "country": "US"},
]
xb = np.stack([embed(d["text"]) for d in docs])               # matrix (N, D)
faiss.normalize_L2(xb)                                        # cosine via inner product
index = faiss.IndexIDMap2(faiss.IndexFlatIP(D))               # custom ids
index.add_with_ids(xb, np.array([d["id"] for d in docs], dtype="int64"))   # ids 10..13
by_id = {d["id"]: d for d in docs}                            # side store for text/metadata

def search(query: str, k: int = 2, country: str | None = None):
    q = embed(query).reshape(1, -1)                           # shape (1, D)
    faiss.normalize_L2(q)                                     # normalise the query
    scores, ids = index.search(q, k * 3)                      # over-fetch for post-filtering
    out = []
    for s, i in zip(scores[0], ids[0]):
        if i == -1:                                           # padding
            continue
        doc = by_id[int(i)]
        if country and doc["country"] != country:             # metadata post-filter
            continue
        out.append((round(float(s), 3), doc["id"], doc["text"]))
    return out[:k]                                            # keep top k after filtering

print(search("wireless headphones", k=2, country="IN"))       # id 10 first; US doc filtered out
```

## 💻 Code Example — Advanced
```python
# Advanced: persistent local search service: build, atomic save, load, filter with over-fetch,
# HNSW index for larger data, async API. Uses a real embedder callable you inject.
import asyncio                                                # async runtime
import json                                                   # side store
import logging                                                # logs
import os                                                     # atomic rename
from pathlib import Path                                      # paths
from typing import Any, Callable, Dict, List, Optional

import faiss                                                  # library
import numpy as np                                            # arrays

log = logging.getLogger("faiss-local")                        # logger
Embedder = Callable[[List[str]], np.ndarray]                  # texts -> (n, d) float32

class LocalSearch:
    def __init__(self, dim: int, embed: Embedder, folder: str = "./faiss_tariff") -> None:
        self.dim, self.embed = dim, embed                     # config
        self.dir = Path(folder)                               # where files live
        self.index: Optional[faiss.Index] = None              # loaded lazily
        self.docs: Dict[int, Dict[str, Any]] = {}             # row number -> document

    def build(self, docs: List[Dict[str, Any]], hnsw: bool = False) -> None:
        """Build from scratch. HNSW does not support deletes: rebuild instead."""
        xb = np.ascontiguousarray(self.embed([d["text"] for d in docs]), dtype="float32")
        if xb.shape[1] != self.dim:
            raise ValueError(f"embedder returned dim {xb.shape[1]}, expected {self.dim}")
        faiss.normalize_L2(xb)
        index: faiss.Index = (faiss.IndexHNSWFlat(self.dim, 32, faiss.METRIC_INNER_PRODUCT) if hnsw
                              else faiss.IndexFlatIP(self.dim))           # HNSW M=32 or exact
        index.add(xb)                                         # rows 0..N-1 follow docs order
        self.index, self.docs = index, {i: d for i, d in enumerate(docs)}

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("nothing to save")
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp_idx, tmp_docs = self.dir / "tmp.faiss", self.dir / "tmp.json"
        faiss.write_index(self.index, str(tmp_idx))           # write to temp files first
        tmp_docs.write_text(json.dumps(self.docs), encoding="utf-8")
        os.replace(tmp_idx, self.dir / "index.faiss")         # atomic swap (no half-written files)
        os.replace(tmp_docs, self.dir / "docs.json")

    def load(self) -> None:
        idx_path, docs_path = self.dir / "index.faiss", self.dir / "docs.json"
        if not (idx_path.exists() and docs_path.exists()):
            raise FileNotFoundError("index files missing: run build() + save() first")
        self.index = faiss.read_index(str(idx_path))
        self.docs = {int(k): v for k, v in json.loads(docs_path.read_text(encoding="utf-8")).items()}

    def search(self, query: str, k: int = 5, where: Optional[Dict[str, Any]] = None,
               min_score: float = 0.3, overfetch: int = 5) -> List[Dict[str, Any]]:
        if self.index is None:
            raise RuntimeError("index not loaded")
        q = np.ascontiguousarray(self.embed([query]), dtype="float32")
        faiss.normalize_L2(q)
        scores, rows = self.index.search(q, min(k * overfetch, self.index.ntotal))   # candidates
        hits: List[Dict[str, Any]] = []
        for s, r in zip(scores[0], rows[0]):
            if r == -1 or s < min_score:                      # padding or weak match
                continue
            d = self.docs[int(r)]
            if where and any(d.get(f) != v for f, v in where.items()):   # post-filter
                continue
            hits.append({"score": float(s), **d})
            if len(hits) == k:                                # enough
                break
        if where and len(hits) < k:                           # filter was too strict for the over-fetch window
            log.info("only %d/%d hits after filtering; raise overfetch or use a DB with filtered ANN", len(hits), k)
        return hits

    async def asearch(self, *a: Any, **kw: Any) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.search, *a, **kw)   # non-blocking for FastAPI

# Token usage: search itself uses 0 tokens; query embedding ~20 tokens if you use an API embedder.
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager                  # lifespan
from fastapi import FastAPI, HTTPException, Query            # FastAPI

search_engine: LocalSearch                                    # configured at startup

@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_engine
    search_engine = LocalSearch(dim=1536, embed=my_openai_embedder)   # your sync embedder callable
    try:
        search_engine.load()                                  # load files built by the nightly job
    except FileNotFoundError as exc:
        raise RuntimeError(f"cannot start: {exc}")            # fail fast with a clear message
    yield

app = FastAPI(lifespan=lifespan)                              # app

@app.get("/search")                                           # route
async def search(q: str, country: str | None = None, k: int = Query(5, ge=1, le=20)) -> dict:
    where = {"country": country} if country else None
    try:
        return {"hits": await search_engine.asearch(q, k=k, where=where)}
    except Exception as exc:
        raise HTTPException(500, f"search failed: {exc}")

@app.post("/admin/reload")                                    # hot-swap after the nightly rebuild
async def reload_index() -> dict:
    await asyncio.to_thread(search_engine.load)               # reads the new files
    return {"vectors": search_engine.index.ntotal}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_community.vectorstores import FAISS             # LangChain wrapper
from langchain_openai import OpenAIEmbeddings                   # embeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.load_local("faiss_tariff_lc", emb, allow_dangerous_deserialization=True)   # only for files you created
# Search with a metadata filter (LangChain post-filters; `fetch_k` controls the candidate pool):
docs = vs.similarity_search("wireless earbuds", k=4, filter={"country": "IN"}, fetch_k=40)
# Merge two stores (e.g. daily delta into the main index):
# vs.merge_from(FAISS.from_texts(new_texts, emb))
# LangGraph: wrap `vs.as_retriever(search_kwargs={"k": 4, "fetch_k": 40})` inside the retrieve node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filtering after `search(k=5)` so filtered results run out
✅ Correct: over-fetch (k x 3-10), then filter.

```python
# Wrong: top 5 are all US docs -> zero results after filtering
scores, ids = index.search(q, 5)
# Right
scores, ids = index.search(q, 50)   # then filter and keep 5
```

❌ Mistake 2: Saving the index but not the id -> text mapping (or the mapping order changes after a rebuild)
✅ Correct: save docs.json together with the index, from the same build, and swap both atomically.

```python
# Wrong: index.faiss from today, docs.json from last week -> wrong texts for hits
# Right: write both to temp files, then os.replace() each (or put both in a versioned folder and flip a pointer)
```

❌ Mistake 3: Embedding queries with a different model than the documents
✅ Correct: one embedder (and version) stored in a manifest file next to the index.

---

## 🧠 Tricky Interview Question

**Q**: "Your FAISS search returns the right documents on your laptop, but in production behind 4 Uvicorn workers memory is 4x and reloads cause brief wrong answers. Explain and fix."

**Answer**: Each worker process loads its own copy of the index (4x memory) and reloads independently, so for a moment workers can run different versions or a half-written file. Fixes: build the index offline and publish it as a versioned, immutable folder (atomic rename or pointer flip); load with memory mapping where supported (`faiss.read_index(path, faiss.IO_FLAG_MMAP)` for compatible index types) so workers share the OS page cache; reduce workers or use one process per pod with more replicas; make reload explicit via an admin endpoint or rolling deploy; and include a version number in responses so inconsistencies are visible.

---

## ⚫ Interview Questions + Answers

Q1: Which FAISS index would you start with for 50,000 documents?
A1: `IndexFlatIP` on normalised vectors: exact, no training, fast enough (milliseconds), simplest to maintain.

Q2: How do you keep text and metadata with FAISS?
A2: In your own structure (dict/JSON/SQLite) keyed by the vector's row number or external id, saved with the index.

Q3: How can you filter by metadata with FAISS?
A3: Post-filter with over-fetch, keep separate indexes per category, or (newer FAISS versions) use ID selectors in search parameters. For heavy filtering a vector database is easier.

Q4: How do you update an index with new documents?
A4: Flat/IVF: `add` the new vectors (IVF may need retraining if distribution shifts). HNSW: add works, remove does not. Common approach: nightly full rebuild plus a small delta index searched in parallel, merging the results.

Q5: Design local semantic search for 5M documents on a single 32 GB machine.
A5: Raw float32 at 768 dims = ~15 GB, so Flat is possible but heavy. Use IVF-PQ (e.g. `IVF4096,PQ64`: ~0.4 GB of codes), train on a 200k sample, store the original vectors on disk for reranking the top 100, tune `nprobe` for recall >= 0.95, mmap the index, keep metadata in SQLite, build offline and swap atomically, and monitor recall with a held-out ground truth computed from exact search on a sample.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single machine, read-heavy, offline or air-gapped, batch analytics
- Data changes rarely (nightly rebuilds)

❌ Avoid when:
- Many concurrent writers, frequent deletes, or strict filtered search at scale
- Multiple servers need one shared live index

---

## 📊 Visual Diagram
```
 BUILD (nightly job)                              SERVE (API / CLI)
 docs ─embed─► xb (N,d) ─normalize─► Index         startup: read_index + docs.json
        │                              │                         │
        │ side store                   ▼                         ▼
        └────────► docs.json     index.faiss          query ─embed─► search(k*5)
                       │               │                           │ post-filter
        atomic rename ─┴───────────────┘                           ▼
        (versioned folder)                                   top k hits ─► LLM
```

---

## 💰 Cost Impact
- No database or per-query fee. Hardware only: RAM = index size (Flat: N x d x 4 bytes; 200k x 1536 = ~1.2 GB).
- One-off embedding cost: 200k headings x 50 tokens = 10M tokens = $0.20 with text-embedding-3-small. Nightly rebuild only re-embeds changed rows if you cache by content hash.
- Query-time token cost is one short embedding (~20 tokens). Over-fetch costs only CPU.
- Savings on the LLM side come from sending only the top 3-4 chunks (~1,000 tokens) and applying `min_score`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Over-fetch | Retrieve extra candidates before filtering | Filter से पहले ज़्यादा candidates लाना |
| Post-filter | Filter after the vector search | Search के बाद filter |
| Side store | Separate storage of text/metadata | Text/metadata का अलग store |
| Atomic swap | Replace files in one step | एक step में files बदलना |
| mmap | Memory-map the file, share across processes | File को memory-map करना |
| Delta index | Small index for recent changes | हाल के बदलावों का छोटा index |
| Manifest | File describing model/version of an index | Index के model/version का record |

---

## ⚡ 3-Line Summary
English: Local FAISS search = embed, build an index suited to your size, save it with a side file of texts and metadata, load at startup. Filter with over-fetch plus post-filtering and swap rebuilt indexes atomically. It is perfect for offline or read-heavy single-machine apps.
Hindi: Local FAISS search = embed करो, size के हिसाब से index बनाओ, texts और metadata की side file के साथ save करो और startup पर load करो। Over-fetch + post-filtering से filter करो और rebuild किए index को atomically swap करो। Offline या read-heavy single-machine apps के लिए बढ़िया।

---

## ➡️ Next Topic
**143. pgvector — PostgreSQL Extension** — vector search inside Postgres, with SQL, transactions and metadata joins.
