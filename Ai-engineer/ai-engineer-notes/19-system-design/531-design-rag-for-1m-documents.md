
---

# 531. Design: RAG for 1M Documents
# हिंदी में: Design: 10 लाख Documents के लिए RAG

---

## 🔵 Simple Definition (English)
This is a system design exercise: build a Retrieval-Augmented Generation (RAG) system that can answer questions over one million documents. At this size you need batch ingestion, a scalable vector database with metadata filters, hybrid search plus reranking, caching, and monitoring. A naive "load everything into one list" design will not work.

## 🔵 सरल परिभाषा (Hindi)
यह एक system design exercise है: ऐसा Retrieval-Augmented Generation (RAG) system बनाना जो 10 लाख documents पर सवालों के जवाब दे सके। इस size पर batch ingestion, metadata filters वाला scalable vector database, hybrid search और reranking, caching और monitoring चाहिए। "सब कुछ एक list में load करो" वाला naive design नहीं चलेगा।

---

## 🔴 Problem it Solves
- 1M documents (for example 10 chunks each = 10M chunks) cannot fit in an LLM context window.
- Brute-force similarity over 10M vectors per query is too slow and expensive.
- Embedding everything is a big one-time cost, and documents change daily.
- Quality drops as the corpus grows: more near-duplicates and more distractors.

## 🔴 यह क्यों बना? (Hindi)
- 10 लाख documents (जैसे हर एक के 10 chunks = 1 करोड़ chunks) LLM के context window में नहीं आते।
- हर query पर 1 करोड़ vectors का brute-force similarity बहुत slow और महँगा है।
- सब कुछ embed करना बड़ा one-time cost है, और documents रोज़ बदलते हैं।
- Corpus बढ़ने पर quality गिरती है: ज़्यादा near-duplicates और distractors।

---

## 🟢 How it Works — Step by Step

```
Step 0 → Clarify: users, QPS, latency target, doc types, freshness, languages, access control
Step 1 → Estimate scale: 1M docs x ~10 chunks = ~10M chunks; 1024-dim float32 = ~4 KB/vector
         = ~40 GB raw vectors (plus index overhead; quantisation can cut this by 4x or more)
Step 2 → Ingestion pipeline (async, queued): parse -> clean -> dedupe -> chunk -> embed (batched) -> upsert
Step 3 → Store: vector DB (HNSW index) with metadata (tenant, doc id, date, type) + keyword index (BM25)
Step 4 → Query path: guard -> rewrite -> hybrid search (vector + BM25, with filters) top 50
Step 5 → Rerank top 50 -> top 5 with a cross-encoder
Step 6 → Build prompt with citations -> LLM -> output guard
Step 7 → Cache (exact + semantic), rate limit, stream the answer
Step 8 → Update path: incremental re-index by document hash; delete = remove vectors by doc id
Step 9 → Evaluate (recall@k, groundedness) and monitor (latency, cost, empty-retrieval rate)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 0 → Clarify करो: users, QPS, latency target, doc types, freshness, languages, access control
Step 1 → Scale estimate: 10 लाख docs x ~10 chunks = ~1 करोड़ chunks; 1024-dim float32 = ~4 KB/vector
         = ~40 GB raw vectors (index overhead अलग; quantisation से 4x या ज़्यादा घट सकता है)
Step 2 → Ingestion pipeline (async, queue): parse -> clean -> dedupe -> chunk -> embed (batch) -> upsert
Step 3 → Store: vector DB (HNSW index) + metadata (tenant, doc id, date, type) + keyword index (BM25)
Step 4 → Query path: guard -> rewrite -> hybrid search (vector + BM25, filters के साथ) top 50
Step 5 → Top 50 को cross-encoder से rerank करके top 5
Step 6 → Citations के साथ prompt -> LLM -> output guard
Step 7 → Cache (exact + semantic), rate limit, answer stream करो
Step 8 → Update path: document hash से incremental re-index; delete = doc id से vectors हटाओ
Step 9 → Evaluate (recall@k, groundedness) और monitor (latency, cost, empty-retrieval rate)
```

---

## 🟡 Real World Example
**Tariff Classification System** at national scale: 1M documents = tariff schedules, customs rulings, past classification decisions, and notices from many countries and years. Queries such as "HS code for lithium battery packs, 2024 ruling" need:
- metadata filters (country, year, document type) to cut the search space before similarity search;
- hybrid search because HS codes and legal terms ("8507.60") need exact keyword match, which pure embeddings miss;
- reranking to put the most relevant ruling on top;
- citations so the officer can open the source ruling.

**Amazon-style AI**: product-help assistant over 1M product manuals, filtering by product id before search.

## 🟡 Real Example Hindi mein
**Tariff Classification System** राष्ट्रीय scale पर: 10 लाख documents = tariff schedules, customs rulings, पुराने classification decisions और कई देशों व सालों के notices। "lithium battery packs का HS code, 2024 ruling" जैसे सवालों के लिए चाहिए:
- Similarity search से पहले search space घटाने के लिए metadata filters (देश, साल, document type);
- Hybrid search, क्योंकि HS codes और legal terms ("8507.60") को exact keyword match चाहिए जो सिर्फ embeddings चूक जाते हैं;
- Reranking, ताकि सबसे relevant ruling ऊपर आए;
- Citations, ताकि officer source ruling खोल सके।

**Amazon-style AI**: 10 लाख product manuals पर help assistant, search से पहले product id से filter।

---

## 💻 Code Example — Basic
```python
# Basic: back-of-envelope capacity calculator (pure Python)
def capacity(docs: int, chunks_per_doc: int, dim: int, bytes_per_float: int = 4) -> dict[str, float]:
    """Estimate vector count and raw storage."""
    chunks = docs * chunks_per_doc                     # total chunks
    raw_gb = chunks * dim * bytes_per_float / 1e9      # raw vector size in GB
    return {"chunks": float(chunks), "raw_gb": raw_gb, "int8_gb": raw_gb / 4}  # 8-bit quantised

def embed_cost(chunks: int, tokens_per_chunk: int, price_per_m: float) -> float:
    """One-time embedding cost in USD for a given price per 1M tokens."""
    return chunks * tokens_per_chunk * price_per_m / 1_000_000

if __name__ == "__main__":
    c = capacity(1_000_000, 10, 1024)                  # 1M docs, 10 chunks, 1024-dim
    print(c)                                           # chunks 1e7, raw ~41 GB, int8 ~10 GB
    # Price is a placeholder: use your embedding provider's real price.
    print(f"one-time embed cost: ${embed_cost(10_000_000, 400, 0.02):,.0f}")  # 4B tokens -> $80
```

## 💻 Code Example — Advanced
```python
# Advanced: batched async ingestion + hybrid fusion (mock embedder, runs offline)
import asyncio                                         # concurrency
import hashlib                                         # content hash for dedupe/incremental
from typing import Iterable

BATCH = 64                                             # embed 64 chunks per call
SEM = asyncio.Semaphore(4)                             # max 4 concurrent embed calls

def chunk(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    """Split by characters with overlap (illustrative; use token-aware splitters in prod)."""
    if size <= overlap:
        raise ValueError("size must be larger than overlap")
    step = size - overlap                              # window step
    return [text[i:i + size] for i in range(0, max(len(text), 1), step)]

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()   # stable id for dedupe

async def embed_batch(batch: list[str]) -> list[list[float]]:
    """Mock embedder. Replace with a real embedding API call + retry."""
    async with SEM:                                    # limit concurrency (rate limits)
        await asyncio.sleep(0.01)                      # pretend network
        return [[float(len(t) % 7)] for t in batch]    # fake 1-dim vectors

def batches(items: list[str], n: int) -> Iterable[list[str]]:
    for i in range(0, len(items), n):                  # slice into batches
        yield items[i:i + n]

async def ingest(docs: dict[str, str], seen: set[str]) -> int:
    """Chunk, dedupe, embed in batches, 'upsert'. Returns chunks written."""
    all_chunks: list[str] = []
    for text in docs.values():
        for c in chunk(text):
            h = content_hash(c)
            if h in seen:                              # skip unchanged/duplicate chunk
                continue
            seen.add(h)
            all_chunks.append(c)
    written = 0
    for b in batches(all_chunks, BATCH):
        try:
            vectors = await embed_batch(b)             # in prod: retry with backoff
        except Exception as exc:                       # do not lose the whole job
            print("batch failed, will retry later:", exc)
            continue
        written += len(vectors)                        # upsert(vectors, metadata) here
    return written

def rrf(rank_lists: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal Rank Fusion: merge vector and BM25 results."""
    score: dict[str, float] = {}
    for ranks in rank_lists:
        for pos, doc_id in enumerate(ranks, start=1):
            score[doc_id] = score.get(doc_id, 0.0) + 1.0 / (k + pos)
    return sorted(score, key=score.get, reverse=True)

if __name__ == "__main__":
    seen: set[str] = set()
    docs = {"d1": "battery " * 200, "d2": "steel " * 200}
    print("chunks written:", asyncio.run(ingest(docs, seen)))
    print(rrf([["a", "b", "c"], ["c", "a", "d"]]))     # a and c rise to the top
```

---

## 🟠 FastAPI Integration
Split into two services: an **ingestion worker** (queue consumer, heavy, async) and a **query API** (low latency). Never ingest inside the request path.

```python
# FastAPI query API: filters, hybrid search, rerank, citations (retrieval mocked)
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    country: str | None = None                         # optional metadata filter
    year: int | None = None

async def tenant(x_tenant: str = Header(default="")) -> str:
    if not x_tenant:
        raise HTTPException(401, "missing tenant")     # real apps: verify JWT
    return x_tenant

async def hybrid_search(q: str, filters: dict[str, object], k: int) -> list[dict[str, str]]:
    return [{"id": "ruling-77", "text": "Lithium battery packs: 8507.60"}][:k]  # mock

@app.post("/ask")
async def ask(body: Ask, t: str = Depends(tenant)) -> dict[str, object]:
    filters: dict[str, object] = {"tenant": t}         # tenant filter always present
    if body.country:
        filters["country"] = body.country
    if body.year:
        filters["year"] = body.year
    hits = await hybrid_search(body.question, filters, k=50)   # recall stage
    top = hits[:5]                                     # rerank stage would reorder these
    if not top:
        return {"answer": "No source found.", "citations": []}  # do not guess
    return {"answer": "See cited ruling.", "citations": [h["id"] for h in top]}
```
For queue-based ingestion, an upload endpoint stores the file, pushes a job (Celery, SQS, Redis, Kafka), and returns 202 with a job id.

---

## 🔗 LangChain / LangGraph Connection
- **LangChain**: `RecursiveCharacterTextSplitter`, embeddings classes, vector store integrations (Qdrant, pgvector, Pinecone, etc.), `EnsembleRetriever` (BM25 + vector), and contextual compression or reranker wrappers.
- **LangGraph**: model the query path as a graph: `guard -> rewrite -> retrieve -> rerank -> grade -> generate`, with a conditional edge that retries with a rewritten query when retrieval is weak.

```python
# LangChain hybrid retriever (illustrative; needs installed integrations)
# from langchain.retrievers import EnsembleRetriever
# hybrid = EnsembleRetriever(retrievers=[bm25_retriever, vector_retriever], weights=[0.4, 0.6])
# docs = await hybrid.ainvoke("battery pack HS code 2024")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding and upserting one chunk at a time
✅ Correct: Batch (for example 64-256 chunks per call) with bounded concurrency and retries.

```python
# Wrong: 10M network calls
for c in chunks:
    vec = await embed([c])
# Right: batches
for b in batches(chunks, 64):
    vecs = await embed_batch(b)
```

❌ Mistake 2: Pure vector search for codes, names and IDs
✅ Correct: Hybrid search (BM25 + vectors) and metadata filters.

❌ Mistake 3: Re-embedding the whole corpus on every change
✅ Correct: Hash content; re-embed only changed chunks; delete by doc id.

---

## 🧠 Tricky Interview Question

**Q**: "Recall was great at 10K documents. At 1M, answers get worse even though the vector DB returns results quickly. Why, and what do you change?"

**Answer**: More documents means more near-duplicates and similar-but-wrong chunks, so the true answer is not always in the top-k and the top-k holds distractors. The ANN index also trades some recall for speed. Fixes: (1) metadata filters (country, year, type) to shrink the candidate set; (2) hybrid search for exact terms; (3) retrieve wide (top 50-100) then rerank with a cross-encoder to top 5; (4) dedupe near-identical chunks at ingestion; (5) tune HNSW parameters (`ef_search`) and measure recall against a brute-force baseline on a sample; (6) better chunking with titles or context added to each chunk; (7) evaluate with a labelled set at each scale step.

---

## ⚫ Interview Questions + Answers

Q1: Why chunk documents?
A1: Embeddings and LLM context work best on focused pieces. Smaller chunks improve retrieval precision; chunks that are too small lose context. Typical sizes are a few hundred tokens with a bit of overlap.

Q2: What is hybrid search?
A2: Combining keyword search (BM25) and vector search, then fusing the rankings (for example with Reciprocal Rank Fusion). It handles both exact terms (codes) and meaning.

Q3: What does a reranker do?
A3: A cross-encoder reads the query and each candidate together and scores relevance more accurately than the bi-encoder used for first-stage retrieval. It is slower, so use it only on the top 50-100.

Q4: How do you handle document updates and deletions?
A4: Keep a document id and content hash in metadata. On change, delete that doc's vectors and upsert new chunks. For access changes or legal deletions, remove by doc id and verify; use soft-delete flags only if filtered at query time.

Q5 (Hard): Estimate and design for 200 QPS peak with a 3-second p95 end-to-end.
A5: Budget the latency: guard 20 ms, embed query 50 ms, hybrid search 100 ms, rerank 150 ms, LLM time to first token about 600 ms, then stream. Scale the stateless query API horizontally behind a load balancer; shard or replicate the vector DB by tenant or hash, with read replicas for QPS. Cache exact and semantic queries (popular questions may hit 20-40%). Put rate limits and per-tenant quotas in front, use a connection pool to the LLM provider with provider-side rate limit awareness, and a fallback model. Load test and watch p95 per stage.

---

## 🔷 When to Use + When Not to Use
✅ Use this architecture when:
- Corpus is large (hundreds of thousands to millions of docs) and changes over time
- You need citations and access control

❌ Avoid when:
- Corpus fits in a long context window and rarely changes (just send it, perhaps with prompt caching)
- Questions need aggregation across all documents ("count all rulings"): use SQL or structured extraction instead

---

## 📊 Visual Diagram
```
INGEST (async)                         QUERY (low latency)
 Files -> Queue -> Workers              User -> API -> Guard -> Rewrite
          parse/clean/dedupe                       |
          chunk (+ metadata)                       v
          embed (batched)               +-----------------------+
                |                       | Hybrid search + filters|
                v                       |  vector DB  |  BM25    |
        +---------------+  upsert       +-----------+-----------+
        | Vector DB     |<--------------------------+ top 50
        | HNSW + meta   |                           v
        +---------------+                    Reranker -> top 5
        | Keyword index |                           v
        +---------------+                  LLM (+citations) -> Output guard
                                                    v
        Cache (exact+semantic) <-------------  Answer (stream)
        Monitoring: recall, latency, cost, empty-retrieval
```

---

## 💰 Cost Impact
- **One-time embedding**: 10M chunks x 400 tokens = 4B tokens. At an illustrative $0.02 per 1M tokens that is about $80; real prices vary by model. Re-embedding only changed chunks keeps monthly cost small.
- **Storage**: ~40 GB raw vectors; quantisation (int8 or binary) can cut memory 4x or more, which often dominates infra cost (RAM for HNSW).
- **Per query**: the LLM dominates. Sending top 5 chunks of 400 tokens plus a prompt is about 2,500 input tokens. Retrieve wide, rerank, and send few chunks.
- **Savings**: semantic and exact caching, a smaller model for easy queries, prompt caching for the fixed system prompt, and a reranker instead of sending 20 chunks to the LLM.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ANN / HNSW | Fast approximate nearest-neighbour index | तेज़ approximate पास-खोज index |
| Hybrid search | Keyword plus vector search | Keyword और vector search का मेल |
| Reranker | Re-scores top candidates precisely | Top candidates की सटीक दोबारा scoring |
| RRF | Rank fusion method | Rankings मिलाने की विधि |
| Quantisation | Smaller vectors, less memory | छोटे vectors, कम memory |
| Metadata filter | Narrow search by fields | Fields से search सीमित करना |
| Incremental indexing | Re-embed only changed data | सिर्फ बदला हुआ data दोबारा embed |

---

## ⚡ 3-Line Summary
English: At 1M documents use async batched ingestion, a vector DB with metadata filters, hybrid search, and a reranker. Dedupe and index incrementally, cache aggressively, and measure recall as the corpus grows. Design the latency and cost budget per stage.
Hindi: 10 लाख documents पर async batched ingestion, metadata filters वाला vector DB, hybrid search और reranker use करो। Dedupe और incremental indexing करो, खूब caching करो और corpus बढ़ने पर recall नापो। हर stage का latency और cost budget तय करो।

---

## ➡️ Next Topic
**532. Design: Multi-tenant AI API** — serving many customers safely from one platform: isolation, quotas, billing and noisy neighbours.
