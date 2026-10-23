# 135. Pinecone + pgvector
# हिंदी में: Pinecone और pgvector — दो सबसे लोकप्रिय vector store: Pinecone (पूरी तरह managed, serverless vector database) और pgvector (Postgres का extension) — दोनों को सेट करना, डेटा डालना, filters, namespaces/tenants, tuning और कब कौन चुनें

---

## 🔵 Simple Definition (English)
- **pgvector** is an open-source **Postgres extension** that adds a `vector` column type, distance operators (`<=>` cosine, `<->` L2, `<#>` negative inner product) and ANN indexes (**HNSW**, **IVFFlat**), plus `halfvec`/`sparsevec` types. Your embeddings live **next to your relational data**, with SQL joins, transactions, row-level security, backups and your existing Postgres tooling (RDS/Aurora, Cloud SQL, Supabase, Neon).
- **Pinecone** is a **fully managed vector database** (serverless or pod-based) where you create an **index** (dimension + metric), **upsert** vectors with metadata, organize them in **namespaces** (great for multi-tenancy), and **query** top-k with metadata filters. It offers sparse-dense (hybrid) search, integrated inference (embedding and reranking hosted by Pinecone) and scales without you managing servers.
Both are common backbones for RAG and semantic search. The choice depends on **scale, ops capacity, data residency, cost and how tightly the vectors relate to your transactional data**.

## 🔵 सरल परिभाषा (Hindi)
pgvector = Postgres का open-source extension — `vector` column, दूरी के operators (`<=>` cosine), HNSW/IVFFlat index; embeddings आपके बाक़ी डेटा के बगल में — SQL joins, transactions, row-level security, backups सब वैसे ही (RDS, Supabase…)।
Pinecone = पूरी तरह managed vector database — index बनाओ (dimension + metric), metadata के साथ upsert, namespaces (हर tenant अलग), filters के साथ top-k query; hybrid search, hosted embedding/reranking, बिना servers संभाले scale। चुनाव पैमाना, ops क्षमता, डेटा कहाँ रहे (residency), ख़र्च और transactional डेटा से कितना जुड़ा है — इस पर।

---

## 🔴 Problem it Solves
Teams building RAG must decide **where vectors live** and implement it correctly:
- **Speed to production**: pgvector reuses your Postgres (no new system), while Pinecone gives a managed endpoint in minutes.
- **Consistency**: when a help article or product is updated in Postgres, its vectors must update too. That's trivial in the same transaction with pgvector and needs a sync pipeline with Pinecone.
- **Isolation and security**: multi-tenant SaaS needs strict per-tenant retrieval (RLS in Postgres, namespaces in Pinecone).
- **Scale and ops**: hundreds of millions of vectors with high QPS strain a single Postgres box, where managed vector DBs shine.
- **Compliance**: Indian BFSI and health data often must stay in India. Postgres in Mumbai (ap-south-1) is straightforward, and a managed vendor's region availability must be checked.

## 🔴 यह क्यों बना? (Hindi)
RAG बनाने वाली टीमों को तय करना है कि vectors कहाँ रहें और सही तरीके से लागू करना है: जल्दी production — pgvector मौजूदा Postgres में (नया system नहीं), Pinecone मिनटों में managed endpoint; एकरूपता — Postgres में लेख बदला तो vectors भी बदलें (pgvector में एक ही transaction, Pinecone में sync pipeline); हर tenant का अलग डेटा (Postgres RLS, Pinecone namespaces); करोड़ों vectors और भारी QPS पर एक Postgres दबता है — managed DB बेहतर; और भारत के BFSI/health डेटा को भारत में रखना — Mumbai region का Postgres आसान, vendor का region जाँचो।

---

## 🟢 How it Works — Step by Step

### pgvector essentials

```
Types: vector(n) (float32), halfvec(n) (float16 → half memory), sparsevec, bit (binary)
Operators: <=> cosine distance | <-> L2 distance | <#> negative inner product | <+> L1
Indexes:
  HNSW:    CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)
           query knob: SET hnsw.ef_search = 40..200
  IVFFlat: CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000)
           build AFTER loading data; query knob: SET ivfflat.probes = 10..
Filtered queries: B-tree indexes on filter columns + hnsw.iterative_scan (0.8+) to avoid empty results;
           or partition by tenant (declarative partitioning) with per-partition HNSW indexes
Memory: HNSW index should fit in RAM for best latency → use halfvec / fewer dims / bigger instance
Security: Row-Level Security policies by tenant; regular Postgres backups/PITR, replicas for read scaling
```

### Pinecone essentials

```
Index: name, dimension (e.g., 1024), metric (cosine | dotproduct | euclidean), spec (serverless: cloud+region)
Records: {id, values: [...], sparse_values?: {...}, metadata: {tenant, lang, doc_id, url, ...}}
Namespaces: logical partitions inside an index → one per tenant/customer → isolation, fast deletes
Operations: upsert (batches ~100–1000), query (vector/top_k/filter/include_metadata), fetch, delete
            (by id / by metadata filter / delete namespace), list ids by prefix ("doc123#")
Filters: MongoDB-like syntax {"lang": {"$in": ["hi","en"]}, "doc_type": {"$eq": "policy"}}
Hybrid: sparse-dense vectors (BM25/SPLADE sparse + dense) in one query (Topic 138)
Integrated inference: Pinecone-hosted embedding & rerank models (optional)
Consistency: eventually consistent — fresh upserts become queryable after a short delay
```

### Sync pattern when the source of truth is elsewhere (Pinecone)

```
Postgres (articles/products) ──CDC (Debezium) / outbox events──► Kafka/SQS ──► embedding worker
   → chunk → embed → upsert to Pinecone (ids "doc_id#n", namespace=tenant) → delete stale chunk ids
Idempotent, retryable; periodic reconciliation (compare doc versions) to fix drift
pgvector: same flow but can be a single DB transaction (update article + chunks)
```

### Decision guide

```
Choose pgvector if:                              Choose Pinecone if:
✓ already on Postgres; vectors tied to rows      ✓ want zero-ops managed, serverless scaling
✓ ≤ ~10–50M vectors, moderate QPS                ✓ 100M+ vectors / spiky high QPS
✓ need transactions, joins, RLS                  ✓ many tenants → namespaces
✓ data must stay in-region (e.g., Mumbai)        ✓ want hybrid & hosted inference out of the box
✓ cost-sensitive (no extra vendor)               ✓ team lacks DB tuning capacity
Hybrid strategy: start with pgvector, move hot/large workloads to a dedicated store when metrics demand
```

## 🟢 कैसे काम करता है? (Hindi)
1. pgvector: `vector(n)` (या आधी memory वाला `halfvec`), `<=>` cosine दूरी; HNSW index (`m`, `ef_construction`, query पर `hnsw.ef_search`) या IVFFlat (डेटा डालने के बाद बनाओ, `ivfflat.probes`); filters के लिए B-tree indexes + iterative scan या tenant के partitions; HNSW RAM में आए तो सबसे तेज़; RLS से tenant सुरक्षा।
2. Pinecone: index (dimension, metric, serverless region) → records (id, values, metadata) → namespaces हर tenant के लिए → upsert batches, filters वाली query, id/filter/namespace से delete; sparse-dense hybrid; upsert के थोड़ी देर बाद query में दिखता है (eventual)।
3. Sync: source of truth Postgres में हो और vectors Pinecone में, तो CDC/outbox → queue → worker (chunk, embed, upsert, पुराने chunks हटाओ) — idempotent और बीच-बीच में reconciliation; pgvector में यह एक ही transaction।
4. pgvector चुनो: पहले से Postgres, vectors rows से जुड़े, करोड़ों तक, transactions/joins/RLS, Mumbai में डेटा, कम ख़र्च।
5. Pinecone चुनो: बिना ops, serverless, 10 करोड़+ vectors या भारी QPS, बहुत सारे tenants (namespaces), hybrid और hosted inference; अक्सर pgvector से शुरू करके ज़रूरत पड़ने पर बड़ा हिस्सा dedicated store में।

---

## 🟡 Real World Example

**Supabase & AWS RDS with pgvector** — Supabase popularized pgvector for app developers ("vector search in your existing Postgres"), and AWS added pgvector to RDS and Aurora PostgreSQL. Many startups build RAG features on it without adding a new database.

**Pinecone serverless (2024)** — Pinecone launched a serverless architecture separating storage and compute, aimed at lower costs for large indexes and spiky workloads. It's commonly used by SaaS products offering "chat with your docs" to many customers via namespaces.

**Indian BFSI and health compliance** — teams handling regulated data typically keep embeddings in-region (Postgres + pgvector on RDS ap-south-1, or self-hosted Qdrant/Milvus) because embeddings derived from sensitive text are themselves sensitive.

**Migration stories** — teams frequently start with pgvector for simplicity and move to a dedicated vector DB once vector counts or QPS outgrow a single Postgres cluster. Others go the opposite way, consolidating into Postgres to reduce the operational surface. Both are valid, metric-driven decisions.

## 🟡 Real Example Hindi में
Supabase ने pgvector को app developers में लोकप्रिय किया ("मौजूदा Postgres में vector search"), AWS ने RDS/Aurora में जोड़ा — कई startups बिना नया DB जोड़े RAG बनाते हैं; Pinecone ने 2024 में serverless (storage-compute अलग) लाया — कई ग्राहकों वाले "chat with your docs" SaaS namespaces से।
भारत के BFSI/health में embeddings भी संवेदनशील माने जाते हैं, इसलिए Mumbai region में pgvector या self-hosted Qdrant/Milvus; टीमें अक्सर pgvector से शुरू करती हैं और बढ़ने पर dedicated DB पर जाती हैं — या उल्टा, ops घटाने के लिए Postgres में समेटती हैं।

---

## 🟠 My Stack Example

### pgvector with FastAPI + asyncpg (RLS by tenant, halfvec to save memory)
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE help_chunks (
  id TEXT PRIMARY KEY, tenant_id BIGINT NOT NULL, article_id BIGINT NOT NULL REFERENCES help_articles(id) ON DELETE CASCADE,
  chunk_no INT NOT NULL, lang TEXT NOT NULL, content TEXT NOT NULL, embedding halfvec(1024) NOT NULL,
  embedding_model TEXT NOT NULL, updated_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON help_chunks USING hnsw (embedding halfvec_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX ON help_chunks (tenant_id, lang);

ALTER TABLE help_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON help_chunks USING (tenant_id = current_setting('app.tenant_id')::bigint);
```
```python
import asyncpg
from pgvector.asyncpg import register_vector

async def get_conn():
    conn = await pool.acquire(); await register_vector(conn); return conn

async def search_help(tenant_id: int, query: str, langs=("en", "hi"), k=5):
    qvec = embed_query(query)                                        # Topic 133
    conn = await get_conn()
    try:
        async with conn.transaction():
            await conn.execute("SELECT set_config('app.tenant_id', $1, true)", str(tenant_id))   # RLS scope
            await conn.execute("SET LOCAL hnsw.ef_search = 80")
            await conn.execute("SET LOCAL hnsw.iterative_scan = relaxed_order")
            return await conn.fetch("""
                SELECT c.id, a.title, a.url, c.content, 1 - (c.embedding <=> $1::halfvec) AS score
                FROM help_chunks c JOIN help_articles a ON a.id = c.article_id
                WHERE c.lang = ANY($2) AND a.status = 'published'
                ORDER BY c.embedding <=> $1::halfvec LIMIT $3""", qvec, list(langs), k)
    finally:
        await pool.release(conn)

# Update an article and its chunks in ONE transaction (always consistent)
async def upsert_article(tenant_id, article, chunks_with_vecs):
    conn = await get_conn()
    async with conn.transaction():
        await conn.execute("UPDATE help_articles SET body=$2, updated_at=now() WHERE id=$1", article.id, article.body)
        await conn.execute("DELETE FROM help_chunks WHERE article_id=$1", article.id)
        await conn.executemany("INSERT INTO help_chunks (id, tenant_id, article_id, chunk_no, lang, content, embedding, embedding_model) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
            [(f"{article.id}#{i}", tenant_id, article.id, i, article.lang, c, v, "voyage-3.5") for i, (c, v) in enumerate(chunks_with_vecs)])
```

### Pinecone serverless with namespaces per tenant (Python)
```python
from pinecone import Pinecone, ServerlessSpec
pc = Pinecone()                                                      # PINECONE_API_KEY from env
if not pc.has_index("help-center"):
    pc.create_index(name="help-center", dimension=1024, metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"))   # check region options vs residency needs
index = pc.Index("help-center")

def upsert_chunks(tenant: str, article_id: str, chunks: list[str], vecs: list[list[float]], lang: str):
    for old_ids in index.list(prefix=f"{article_id}#", namespace=tenant):    # serverless: list ids by prefix
        index.delete(ids=old_ids, namespace=tenant)                          # remove stale chunks of this article
    index.upsert(namespace=tenant, vectors=[
        {"id": f"{article_id}#{i}", "values": v, "metadata": {"article_id": article_id, "lang": lang, "text": c[:2000]}}
        for i, (c, v) in enumerate(zip(chunks, vecs))])

def search(tenant: str, query: str, k=5):
    res = index.query(namespace=tenant, vector=embed_query(query), top_k=k, include_metadata=True,
                      filter={"lang": {"$in": ["en", "hi"]}})
    return [(m.id, m.score, m.metadata["text"]) for m in res.matches]
# Offboarding a customer: index.delete(delete_all=True, namespace=tenant)
```

### Node: Pinecone TypeScript SDK query
```ts
import { Pinecone } from '@pinecone-database/pinecone';
const pc = new Pinecone();
const idx = pc.index('help-center');
export async function retrieve(tenantId: string, qVec: number[]) {
  const r = await idx.namespace(tenantId).query({ vector: qVec, topK: 5, includeMetadata: true, filter: { lang: { $in: ['en', 'hi'] } } });
  return r.matches?.map((m) => ({ id: m.id, score: m.score, text: m.metadata?.text })) ?? [];
}
```

### Sync worker: Postgres outbox → embed → Pinecone (idempotent)
```python
async def handle_article_changed(evt):                    # from outbox/CDC topic
    art = await db.fetchrow("SELECT id, tenant_id, lang, body, version FROM help_articles WHERE id=$1", evt["id"])
    if not art or art["version"] < evt["version"]: return  # stale event → skip
    chunks = chunk_text(art["body"])                       # Topic 136
    vecs = embed_documents(chunks)
    upsert_chunks(str(art["tenant_id"]), str(art["id"]), chunks, vecs, art["lang"])
    await db.execute("UPDATE help_articles SET indexed_version=$2 WHERE id=$1", art["id"], art["version"])
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you set up vector search in Postgres with pgvector?**
A1: Enable the extension, add a `vector(n)` (or `halfvec(n)`) column with the embedding model's dimensionality, insert embeddings, and create an ANN index (HNSW with the operator class matching your metric, e.g. `vector_cosine_ops`, or IVFFlat after loading data). Query with `ORDER BY embedding <=> $query LIMIT k`, plus WHERE filters backed by B-tree indexes. Tune `hnsw.ef_search` (or `ivfflat.probes`) for the recall/latency trade-off, use iterative scans for selective filters, keep the index in memory, and use RLS or partitions for tenant isolation.

**Q2: How do Pinecone namespaces help multi-tenant RAG?**
A2: A namespace is a partition within an index. Putting each customer's vectors in its own namespace means queries are scoped to that namespace, giving strong isolation, smaller search spaces and simpler operations like deleting all of a customer's data or reindexing one tenant. The server chooses the namespace from the authenticated tenant, never from client input. Metadata filters handle finer-grained constraints (language, document type, ACL groups) within a namespace.

**Q3: How do you keep Pinecone in sync with your primary database?**
A3: Emit change events from the source of truth (transactional outbox or CDC with Debezium) to a queue. Idempotent workers re-chunk and re-embed changed documents, upsert new chunk IDs and delete obsolete ones (stable ID prefixes per document make this easy), and record the indexed version. Handle ordering with version checks, retries with backoff, and periodic reconciliation comparing source versions with indexed versions. With pgvector, the same update can happen in one database transaction.

**Q4: What are pgvector's limitations at scale?**
A4: HNSW indexes are memory-intensive and build slowly on very large tables. A single Postgres primary handles writes and index maintenance, so heavy vector workloads can contend with OLTP traffic. Horizontal sharding is DIY (Citus or application-level). Filtered ANN needs careful tuning (iterative scans, partitions), and very high QPS may require read replicas. Beyond tens of millions of vectors or demanding latency at high QPS, dedicated vector databases often offer better performance per cost and simpler scaling.

**Q5: Which would you choose for a fintech startup in India building a document Q&A for customers?**
A5: Likely pgvector on managed Postgres in the Mumbai region: data residency and regulatory comfort, RLS for per-customer isolation, transactional consistency with document metadata and permissions, lower cost and fewer vendors to assess for security. Start with HNSW on halfvec embeddings and a retrieval eval. Revisit a dedicated vector store if vector counts or QPS outgrow Postgres, choosing one with an Indian region or a self-hosted deployment.

---

## 🔷 Trade-offs
✅ pgvector: one database, transactions, joins, RLS, residency, low cost — ❌ scaling/tuning effort, shares resources with OLTP.
✅ Pinecone: managed, elastic scale, namespaces, hybrid & inference — ❌ separate system to sync, cost, vendor lock-in, region constraints.
✅ halfvec/quantization: memory savings — ❌ small recall impact.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pgvector | Postgres vector extension | Postgres का vector extension |
| halfvec | Half-precision vector type | आधी precision वाला vector |
| `<=>` operator | Cosine distance in pgvector | cosine दूरी |
| ef_search / probes | Recall-latency knobs | सटीकता-गति के knobs |
| Iterative scan | Keeps scanning for filtered results | filter के साथ आगे तक खोज |
| Pinecone index | Managed vector collection | managed vector संग्रह |
| Namespace | Partition inside an index | index के अंदर हिस्सा |
| Metadata filter | Constrain query by attributes | गुणों से सीमित query |
| Serverless | Pay-per-use, auto-scaled | उपयोग के हिसाब से |
| CDC sync | Change data capture pipeline | बदलाव पकड़कर sync |

---

## ⚡ 3-Line Summary
**English:**
1. pgvector: vector/halfvec columns, `<=>` cosine, HNSW/IVFFlat indexes, ef_search tuning, iterative scans, RLS/partitions — vectors live with your relational data.
2. Pinecone: managed serverless index, upsert with metadata, namespaces per tenant, filtered top-k, hybrid & hosted inference — needs a CDC/outbox sync pipeline.
3. Choose by scale, ops capacity, residency, cost and coupling to transactional data; measure recall/latency and revisit as you grow.

**Hindi:**
1. pgvector: vector/halfvec, `<=>`, HNSW, ef_search, RLS — vectors आपके डेटा के साथ।
2. Pinecone: managed serverless, metadata के साथ upsert, tenant के namespaces, filters — CDC/outbox से sync।
3. पैमाना, ops, डेटा कहाँ रहे, ख़र्च और transactional जुड़ाव से चुनो; recall/latency नापते रहो।

---

## ➡️ Next Topic Suggestion
**136. Chunking Strategies** — Before documents are embedded, they must be split into chunks, and how you split them strongly affects retrieval quality. Next: fixed, recursive, semantic and structure-aware chunking, overlap and metadata.
