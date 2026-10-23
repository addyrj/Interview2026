# 134. Vector Databases
# हिंदी में: Vector Databases — करोड़ों embeddings (vectors) को metadata के साथ रखना और किसी सवाल के सबसे पास वाले vectors मिलीसेकंड में ढूँढना (approximate nearest neighbour search) — HNSW, IVF, filtering, multi-tenancy और scaling

---

## 🔵 Simple Definition (English)
A **vector database** (or vector index) stores **embeddings plus metadata** and answers **nearest-neighbour queries**: "give me the top-k vectors most similar to this query vector", optionally **filtered** by metadata (tenant, language, date, category).
Exact search compares the query with every vector (O(N)), which is too slow for millions of vectors. Vector databases use **Approximate Nearest Neighbour (ANN)** indexes that trade a tiny bit of accuracy (**recall**) for huge speed-ups:
- **HNSW** (Hierarchical Navigable Small World graphs): very fast with high recall, but memory-hungry. The most popular.
- **IVF** (inverted file / clustering): searches only the nearest clusters (`nprobe`).
- **PQ / quantization** (product quantization, scalar/binary quantization): compresses vectors to save memory.
- **DiskANN**: SSD-based indexes for billion-scale.
Options:
- **dedicated**: Pinecone, Weaviate, Qdrant, Milvus/Zilliz, Chroma
- **extensions of existing databases**: **pgvector** (Postgres), OpenSearch/Elasticsearch k-NN, MongoDB Atlas Vector Search, Redis
- **libraries**: FAISS, ScaNN, hnswlib

## 🔵 सरल परिभाषा (Hindi)
Vector database embeddings को metadata के साथ रखता है और पूछता है "इस सवाल वाले vector के सबसे पास वाले top-k कौन?" — साथ में filters (tenant, भाषा, तारीख़)। हर vector से तुलना (exact) करोड़ों पर बहुत धीमी, इसलिए ANN indexes: HNSW (graph, तेज़ और सटीक, पर memory ज़्यादा — सबसे लोकप्रिय), IVF (सिर्फ़ पास के clusters देखो), PQ/quantization (vectors को compress), DiskANN (SSD पर अरबों)।
विकल्प: अलग DB (Pinecone, Weaviate, Qdrant, Milvus), मौजूदा DB के extensions (pgvector, OpenSearch, MongoDB Atlas, Redis), libraries (FAISS)।

---

## 🔴 Problem it Solves
RAG and semantic search need to find the most relevant chunks among **millions to billions** of vectors in **milliseconds**, for every query:
- Brute-force cosine similarity over 10M vectors of 1024 dims is ~10 billion multiply-adds per query, far too slow at hundreds of QPS.
- Results must respect **filters and permissions**: a user should only retrieve their company's documents (multi-tenancy), in their language, from current policy versions.
- Data changes continuously (new help articles, products, tickets), so the index must support **upserts and deletes** without full rebuilds.
- At scale you need **replication, sharding, backups and monitoring**, like any database.
Vector databases provide fast ANN search with filtering, CRUD, scaling and operational features, often combined with keyword search (hybrid).

## 🔴 यह क्यों बना? (Hindi)
RAG और semantic search को हर सवाल पर करोड़ों-अरबों vectors में से सबसे सही chunks मिलीसेकंड में चाहिए: 1 करोड़ vectors × 1024 dims पर brute force = एक सवाल पर ~10 अरब गुणा-जोड़ — सैकड़ों QPS पर असंभव; नतीजे filters और permissions मानें (एक कंपनी के यूज़र को सिर्फ़ अपनी कंपनी के documents — multi-tenancy, भाषा, नई नीति); डेटा लगातार बदलता है — बिना पूरा rebuild किए upsert/delete; बड़े पैमाने पर replication, sharding, backup — किसी भी DB की तरह।
Vector DB तेज़ ANN search + filtering + CRUD + scaling देते हैं, अक्सर keyword search के साथ (hybrid)।

---

## 🟢 How it Works — Step by Step

### HNSW intuition

```
Multi-layer graph: top layers sparse (long jumps), bottom layer dense (all points, short links)
Search: start at entry point in top layer → greedily move to neighbours closer to query → drop a layer
        → repeat → at bottom layer explore a candidate list of size ef_search → return top-k
Parameters:
  M               = links per node (higher → better recall, more memory)
  ef_construction = candidate list size while building (higher → better graph, slower build)
  ef_search       = candidate list size at query (higher → better recall, higher latency)  ← tune per QPS/recall
Pros: excellent recall/latency; incremental inserts. Cons: RAM heavy (vectors + graph), deletes are tricky
```

### IVF & quantization intuition

```
IVF: k-means cluster vectors into nlist cells; at query probe nprobe nearest cells only
     → faster, needs training on sample data; recall depends on nprobe
PQ: split vector into sub-vectors, encode each with a small codebook (e.g., 1024 floats → 64 bytes)
     → 10–50× memory reduction, some recall loss → often re-rank top candidates with full vectors
Scalar/binary quantization: float32 → int8 / 1-bit per dim → big memory savings, fast scans
```

### Recall vs latency vs cost

```
Recall@10 = fraction of true top-10 neighbours returned by ANN (measure vs brute force on a sample)
Typical target: recall ≥ 0.95 at p95 latency < 50 ms
Knobs: ef_search / nprobe ↑ → recall ↑, latency ↑ ; quantization → memory ↓, recall ↓ (rerank to recover)
```

### Filtering (the tricky part)

```
Query: top-5 similar chunks WHERE tenant_id = 42 AND lang IN ('hi','en') AND doc_type = 'policy'
Post-filtering: ANN top-100 → apply filter → may leave too few results (if tenant is small)
Pre-filtering: restrict candidate set first → exact search on subset, or filter-aware ANN traversal
Solutions: filter-aware indexes (most vector DBs), partitions/namespaces per tenant, iterative scans
(pgvector 0.8+), separate indexes for large tenants; keep filter columns indexed
```

### Multi-tenancy patterns

```
1) Shared index + tenant_id metadata filter (simple; needs good filtered search; risk if filter forgotten)
2) Namespace/partition per tenant (Pinecone namespaces, Postgres partitions) → isolation, easy deletes
3) Separate index/collection per large tenant (enterprise isolation, noisy-neighbour control)
Always enforce tenant filter server-side (never trust client-supplied tenant) — data leakage risk
```

### Data lifecycle

```
Upsert by stable chunk id (doc_id#chunk_n); delete all chunks of a doc on update/removal
Store metadata needed for filtering & citations (title, url, section, updated_at, acl, lang, model_version)
Re-index on embedding model change (new index, backfill, switch) (Topic 133)
Backups/snapshots; monitor index size, memory, latency, recall drift
```

### Choosing a vector store

```
┌────────────────────────┬────────────────────────────────────────────┬──────────────────────────────┐
│ Option                 │ Best when                                  │ Watch out                    │
├────────────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
│ pgvector (Postgres)    │ Already on Postgres, ≤ tens of millions of │ RAM for HNSW; tuning; big-   │
│                        │ vectors, need joins/transactions/RLS, data │ scale sharding is DIY        │
│                        │ residency (RDS Mumbai), low cost           │                              │
│ Pinecone (managed)     │ Serverless scale, minimal ops, namespaces, │ Vendor lock-in, region/data  │
│                        │ hybrid sparse-dense                        │ residency, cost at scale     │
│ Qdrant / Weaviate /    │ Open-source, rich filtering, self-host or  │ Ops if self-hosted           │
│ Milvus                 │ managed cloud, large scale                 │                              │
│ OpenSearch/Elastic kNN │ Need strong keyword + vector hybrid in one │ Tuning complexity, cost      │
│ FAISS (library)        │ Offline/batch, in-process, research        │ No DB features (CRUD, HA)    │
└────────────────────────┴────────────────────────────────────────────┴──────────────────────────────┘
```

## 🟢 कैसे काम करता है? (Hindi)
1. HNSW: कई परतों वाला graph — ऊपर कम nodes (लंबी छलाँग), नीचे सब nodes; ऊपर से शुरू कर पास वाले पड़ोसी की ओर बढ़ते जाओ, नीचे उतरते जाओ; `M`, `ef_construction`, `ef_search` बढ़ाओ तो recall बढ़ता पर memory/देर भी।
2. IVF vectors को clusters में बाँटता है और सिर्फ़ पास के `nprobe` clusters देखता है; PQ/quantization vectors को 10–50 गुना छोटा करता है (थोड़ा recall घटता — ऊपर के उम्मीदवारों को पूरे vectors से दोबारा rank करो)।
3. लक्ष्य जैसे recall@10 ≥ 0.95 और p95 < 50 ms — brute force से तुलना करके नापो।
4. Filtering कठिन: पहले ANN फिर filter (छोटे tenant पर कम नतीजे) बनाम पहले filter; filter-aware indexes, tenant के partitions/namespaces, pgvector 0.8+ के iterative scans; tenant filter हमेशा सर्वर पर लागू करो।
5. Lifecycle: stable chunk id से upsert, document बदले तो उसके सारे chunks हटाओ, citations/filters के लिए metadata, model बदलने पर नया index; चुनाव — पहले से Postgres और करोड़ों तक vectors → pgvector, बिना ops के बड़ा पैमाना → Pinecone, open-source → Qdrant/Weaviate/Milvus, keyword + vector साथ → OpenSearch।

---

## 🟡 Real World Example

**FAISS (Meta, 2017), ScaNN (Google), Annoy (Spotify)** — open-source ANN libraries from companies that needed similarity search at massive scale (image/video dedupe, recommendations, music similarity). Their algorithms (IVF, PQ, HNSW variants) underpin many vector databases.

**HNSW (2016 paper)** — Malkov and Yashunin's HNSW became the default ANN index in pgvector, Qdrant, Weaviate, OpenSearch and others, thanks to its strong recall and latency trade-off.

**pgvector adoption** — Postgres with pgvector is offered on AWS RDS/Aurora, Google Cloud SQL, Azure and Supabase. Many startups (including Indian SaaS companies) start RAG with pgvector because they already run Postgres and need data in-region (e.g., ap-south-1 Mumbai) for compliance.

**Managed vector DBs at scale** — Pinecone, Zilliz (Milvus) and Weaviate Cloud serve production RAG and recommendation workloads with billions of vectors, offering serverless pricing and namespaces for multi-tenant SaaS.

## 🟡 Real Example Hindi में
Meta का FAISS (2017), Google का ScaNN, Spotify का Annoy — बड़े पैमाने पर similarity search (image/video duplicate, recommendations, गानों की समानता) के लिए बने open-source libraries; 2016 का HNSW paper आज pgvector, Qdrant, Weaviate, OpenSearch का default index है।
pgvector AWS RDS/Aurora, Cloud SQL, Supabase पर मिलता है — कई भारतीय SaaS startups RAG pgvector से शुरू करते हैं क्योंकि Postgres पहले से है और डेटा Mumbai region में रखना ज़रूरी; Pinecone, Zilliz, Weaviate Cloud अरबों vectors वाले काम serverless/namespaces के साथ चलाते हैं।

---

## 🟠 My Stack Example

### pgvector: schema, HNSW index, filtered query (Postgres)
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE kb_chunks (
  id TEXT PRIMARY KEY,                       -- doc_id#chunk_n (stable for upserts)
  tenant_id BIGINT NOT NULL, doc_id TEXT NOT NULL, lang TEXT, doc_type TEXT,
  title TEXT, url TEXT, content TEXT NOT NULL, updated_at TIMESTAMPTZ DEFAULT now(),
  embedding_model TEXT NOT NULL, embedding vector(1024) NOT NULL);
CREATE INDEX kb_hnsw ON kb_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX kb_tenant ON kb_chunks (tenant_id, doc_type);

-- Query-time recall knob + iterative scan for filtered searches (pgvector ≥ 0.8)
SET hnsw.ef_search = 80;
SET hnsw.iterative_scan = relaxed_order;
SELECT id, title, url, content, 1 - (embedding <=> $1) AS score
FROM kb_chunks
WHERE tenant_id = $2 AND doc_type = 'policy' AND lang = ANY($3)
ORDER BY embedding <=> $1
LIMIT 5;
```

### Measure recall of the ANN index vs exact search (Python)
```python
def recall_at_k(sample_queries, k=10):
    total = 0
    for q in sample_queries:
        with db.transaction():
            db.execute("SET LOCAL enable_indexscan = off")          # force exact (brute-force) scan = ground truth
            exact = set(r["id"] for r in db.fetch("SELECT id FROM kb_chunks ORDER BY embedding <=> $1 LIMIT $2", q, k))
        approx = set(r["id"] for r in db.fetch("SELECT id FROM kb_chunks ORDER BY embedding <=> $1 LIMIT $2", q, k))
        total += len(exact & approx) / k
    return total / len(sample_queries)      # tune ef_search until ≥ 0.95 within latency budget
```

### Qdrant (open-source) quick example with payload filter (Python)
```python
from qdrant_client import QdrantClient, models
qc = QdrantClient(url="http://qdrant:6333")
qc.create_collection("kb", vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE))
qc.upsert("kb", points=[models.PointStruct(id=1, vector=vec, payload={"tenant_id": 42, "lang": "hi", "doc_id": "refund-policy"})])
hits = qc.query_points("kb", query=q_vec, limit=5,
        query_filter=models.Filter(must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=42))])).points
```

### Tenant-safe retrieval service (Node) — tenant from auth, never from client
```js
app.post('/api/retrieve', auth, async (req, res) => {
  const qVec = await embedQuery(req.body.query);
  const { rows } = await pg.query(
    `SELECT id, title, url, content, 1 - (embedding <=> $1::vector) AS score
     FROM kb_chunks WHERE tenant_id = $2 ORDER BY embedding <=> $1::vector LIMIT 8`,
    [toSql(qVec), req.user.tenantId]);                  // pgvector npm: toSql([...]) → '[...]'
  res.json(rows.filter((r) => r.score > 0.3));          // drop very weak matches
});
```

### Document update: replace all chunks atomically
```sql
BEGIN;
DELETE FROM kb_chunks WHERE tenant_id = $1 AND doc_id = $2;
INSERT INTO kb_chunks (id, tenant_id, doc_id, lang, doc_type, title, url, content, embedding_model, embedding)
SELECT * FROM unnest($3::text[], $4::bigint[], ...);   -- new chunks (or batched inserts)
COMMIT;
```

---

## ⚫ Interview Questions + Answers

**Q1: How does a vector database find nearest neighbours quickly?**
A1: It uses approximate nearest neighbour indexes instead of brute force. HNSW builds a multi-layer proximity graph and greedily navigates from coarse to fine layers toward the query, exploring a bounded candidate list (`ef_search`), which gives high recall with sub-linear latency. IVF clusters vectors and probes only the nearest clusters. Quantization (PQ, scalar, binary) compresses vectors to cut memory and speed up scans, often followed by reranking with full-precision vectors. Parameters trade recall against latency and memory.

**Q2: How do you handle metadata filters and multi-tenancy?**
A2: Store filterable metadata (tenant, language, document type, ACLs, dates) with each vector and use filter-aware search. For multi-tenancy, either share an index with a mandatory server-enforced tenant filter, or partition per tenant (namespaces or table partitions) for isolation and easy deletion, with separate indexes for very large tenants. Watch for post-filtering returning too few results on small tenants: use pre-filtering, iterative scans or per-tenant partitions. Never trust a client-supplied tenant ID.

**Q3: pgvector or a dedicated vector database?**
A3: Choose pgvector when you already run Postgres, have up to tens of millions of vectors, value transactions and joins with relational data, need row-level security and in-region data residency, and want low operational overhead and cost. Choose a dedicated or managed vector database (Pinecone, Qdrant, Weaviate, Milvus) for very large scale (hundreds of millions to billions), high QPS, advanced filtering, hybrid sparse-dense features, serverless scaling, or to keep vector workloads isolated from OLTP. Benchmark both on your data.

**Q4: How do you measure and tune vector search quality?**
A4: Measure ANN recall@k against exact brute-force search on a sample of real queries, and end-to-end retrieval quality (recall@k and MRR of relevant documents) on labelled query-document pairs. Tune index parameters (HNSW M, ef_construction, ef_search, IVF nlist/nprobe, quantization) to reach target recall within latency and memory budgets. Monitor p95 latency, recall drift as data grows, and filter selectivity, and re-evaluate after embedding model changes.

**Q5: How do you keep a vector index in sync with source documents?**
A5: Use stable chunk IDs derived from document ID and chunk position. On document create or update, re-chunk and re-embed, then atomically replace all chunks for that document (delete and insert in one transaction, or versioned upserts). On delete, remove its chunks. Drive this from change events (CDC, CMS webhooks or queue jobs) with idempotent workers, and store `updated_at`, source version and embedding model per chunk for audits and for filtering stale content. Run periodic reconciliation jobs to catch drift.

---

## 🔷 Trade-offs
✅ HNSW: best recall/latency — ❌ memory heavy; slower builds.
✅ Quantization: memory & cost savings — ❌ recall loss (rerank to recover).
✅ pgvector: simplicity, joins, RLS, residency — ❌ scaling & tuning limits vs specialized DBs.
✅ Managed vector DB: scale without ops — ❌ cost, lock-in, data location constraints.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vector database | Stores & searches embeddings | vectors का database |
| ANN | Approximate nearest neighbour | लगभग सबसे पास वाले |
| HNSW | Graph-based ANN index | graph वाला index |
| IVF | Cluster-based ANN index | cluster वाला index |
| PQ / quantization | Vector compression | vector छोटा करना |
| Recall@k | ANN accuracy vs exact | सटीकता का नाप |
| ef_search / nprobe | Query-time accuracy knobs | खोज की गहराई |
| Metadata filter | Restrict by attributes | गुणों से छाँटना |
| Namespace / partition | Tenant isolation unit | tenant का अलग हिस्सा |
| Upsert | Insert or update | डालो या बदलो |

---

## ⚡ 3-Line Summary
**English:**
1. Vector DBs store embeddings + metadata and answer top-k similarity queries using ANN indexes (HNSW, IVF, quantization) that trade small recall loss for big speed-ups.
2. Filtering & multi-tenancy need filter-aware search, partitions/namespaces and server-enforced tenant filters; keep indexes in sync with stable chunk IDs and atomic replaces.
3. Pick pgvector for Postgres-native, moderate scale & residency; dedicated/managed DBs for massive scale; measure recall@k and latency to tune.

**Hindi:**
1. Vector DB embeddings + metadata रखकर ANN (HNSW, IVF, quantization) से top-k जल्दी ढूँढते हैं।
2. Filters और multi-tenancy: filter-aware search, partitions, सर्वर पर tenant filter; stable chunk id से sync।
3. Postgres और मध्यम पैमाना → pgvector; बहुत बड़ा → dedicated/managed; recall@k और latency नापकर tune।

---

## ➡️ Next Topic Suggestion
**135. Pinecone + pgvector** — Hands-on with the two most common choices: setting up pgvector on Postgres and Pinecone serverless, upserting, filtering, namespaces, tuning and when to pick which.
