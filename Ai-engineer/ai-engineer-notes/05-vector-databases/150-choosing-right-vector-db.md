---

# 150. Choosing Right Vector DB
# हिंदी में: सही Vector Database चुनना

---

## 🔵 Simple Definition (English)
Choosing a vector database means matching your needs (data size, query speed, filters, team skills, budget, compliance) to the option that meets them with the least complexity. There is no best database, only the best fit.

## 🔵 सरल परिभाषा (Hindi)
Vector database चुनने का मतलब है अपनी ज़रूरतों (data size, query speed, filters, team skills, budget, compliance) को उस option से match करना जो सबसे कम complexity में पूरी करे। कोई "सबसे अच्छा" database नहीं होता, सिर्फ़ "सबसे सही fit" होता है।

---

## 🔴 Problem it Solves
Teams pick tools by hype: they deploy a heavy distributed vector DB for 50K vectors, or push 500M vectors through a single Postgres. A structured decision saves months of migration and money.

## 🔴 यह क्यों बना? (Hindi)
Teams hype देखकर tool चुनती हैं: 50K vectors के लिए भारी distributed DB, या 50 करोड़ vectors एक Postgres में। Structured decision से महीनों का migration और पैसा बचता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: number of vectors (now / 12 months), dimension, writes per day
Step 2 → Requirements: p95 latency, QPS, recall target, filters, multi-tenancy
Step 3 → Constraints: existing stack (Postgres? Mongo? ES? Redis?), cloud, data residency
Step 4 → Shortlist 2 options: start with what you already run
Step 5 → Benchmark on YOUR data (100K sample): recall@10, p95, cost per month
Step 6 → Wrap behind an interface; document the exit plan
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → नापो: vectors की संख्या (अभी / 12 महीने बाद), dimension, रोज़ की writes
Step 2 → Requirements: p95 latency, QPS, recall target, filters, multi-tenancy
Step 3 → Constraints: मौजूदा stack (Postgres? Mongo? ES? Redis?), cloud, data residency
Step 4 → 2 options shortlist करो: जो पहले से चलता है उससे शुरू करो
Step 5 → अपने data (100K sample) पर benchmark: recall@10, p95, मासिक cost
Step 6 → Interface के पीछे रखो; exit plan लिखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 2M vectors, 50 QPS, heavy relational filters, audit tables in Postgres, team of three. Decision: pgvector with HNSW. If it grows past 50M vectors or 1,000 QPS, revisit with Qdrant/Pinecone/Milvus.

**Zomato AI**: millions of dishes, low-latency "near me" plus vector similarity, spiky lunch-hour traffic: a managed or horizontally scalable engine with geo filters (Elasticsearch/OpenSearch or Qdrant) fits.

## 🟡 Real Example Hindi mein
**Tariff System**: 2M vectors, 50 QPS, भारी relational filters, audit tables Postgres में, तीन लोगों की team। फैसला: HNSW के साथ pgvector। 5 करोड़ vectors या 1,000 QPS के बाद Qdrant/Pinecone/Milvus पर दोबारा सोचेंगे।

**Zomato AI**: लाखों dishes, "आस-पास" + vector similarity की low latency, lunch-hour में spike: geo filters वाला scalable engine (Elasticsearch/OpenSearch या Qdrant) सही रहेगा।

---

## 💻 Code Example — Basic
```python
# Runs offline: a simple rule-based recommender (no libraries needed)
from dataclasses import dataclass  # lightweight data holder


@dataclass
class Needs:
    vectors: int  # total vectors expected
    qps: int  # peak queries per second
    uses_postgres: bool  # already running Postgres?
    needs_hybrid: bool  # keyword + vector search required?
    ops_team: bool  # do you have people to run infra?


def recommend(n: Needs) -> str:
    """Return a short recommendation string."""
    if n.vectors < 1_000_000 and n.qps < 200 and n.uses_postgres:  # small + Postgres in place
        return "pgvector"
    if n.needs_hybrid and not n.uses_postgres:  # hybrid is the main need
        return "Elasticsearch/OpenSearch"
    if n.vectors > 50_000_000 and not n.ops_team:  # huge and nobody to operate it
        return "Managed (Pinecone / Zilliz / Qdrant Cloud)"
    if n.vectors > 50_000_000:  # huge but ops exist
        return "Milvus / Qdrant / sharded cluster"
    return "pgvector or Qdrant (benchmark both)"  # default: compare


print(recommend(Needs(2_000_000, 50, True, False, True)))  # pgvector or Qdrant (benchmark both)
print(recommend(Needs(500_000, 20, True, False, True)))  # pgvector
print(recommend(Needs(200_000_000, 800, False, False, False)))  # Managed (...)
```

## 💻 Code Example — Advanced
```python
# Weighted scoring matrix + typed result + validation (pure Python, async-friendly wrapper)
import asyncio
from dataclasses import dataclass, field

CRITERIA = ("scale", "latency", "filters", "hybrid", "ops_simplicity", "cost")  # what we score


@dataclass
class Option:
    name: str
    scores: dict[str, int]  # 1 (poor) .. 5 (great) per criterion

    def __post_init__(self) -> None:
        missing = set(CRITERIA) - set(self.scores)  # validate completeness
        if missing:
            raise ValueError(f"{self.name}: missing scores {sorted(missing)}")
        if any(not 1 <= v <= 5 for v in self.scores.values()):  # validate range
            raise ValueError(f"{self.name}: scores must be 1..5")


@dataclass
class Decision:
    ranking: list[tuple[str, float]] = field(default_factory=list)


def rank(options: list[Option], weights: dict[str, float]) -> Decision:
    total = sum(weights.values())  # normalise weights
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    result = [(o.name, sum(o.scores[c] * weights.get(c, 0) for c in CRITERIA) / total) for o in options]
    return Decision(sorted(result, key=lambda t: t[1], reverse=True))  # best first


async def arank(options: list[Option], weights: dict[str, float]) -> Decision:
    return await asyncio.to_thread(rank, options, weights)  # keep API handlers non-blocking


# Illustrative scores, YOU must replace them with benchmark results
OPTIONS = [
    Option("pgvector", dict(scale=3, latency=3, filters=5, hybrid=3, ops_simplicity=5, cost=5)),
    Option("pinecone", dict(scale=5, latency=4, filters=4, hybrid=3, ops_simplicity=5, cost=2)),
    Option("elasticsearch", dict(scale=4, latency=3, filters=5, hybrid=5, ops_simplicity=2, cost=3)),
    Option("redis", dict(scale=2, latency=5, filters=3, hybrid=3, ops_simplicity=4, cost=2)),
]
W = dict(scale=1, latency=2, filters=3, hybrid=1, ops_simplicity=3, cost=2)  # tariff team's priorities
print(asyncio.run(arank(OPTIONS, W)).ranking)
```

---

## 🟠 FastAPI Integration
Expose the store behind a config switch and a health endpoint so you can swap and observe.

```python
import os
import time
from fastapi import FastAPI

app = FastAPI()
BACKEND = os.getenv("VECTOR_BACKEND", "pgvector")


@app.get("/health/vector")
async def vector_health() -> dict:
    start = time.perf_counter()  # measure a trivial query
    # await store.query(probe_vector, 1)   # a real probe query against your adapter
    latency_ms = (time.perf_counter() - start) * 1000
    return {"backend": BACKEND, "probe_ms": round(latency_ms, 2)}  # feed to monitoring/alerts
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `VectorStore` interface is the portability layer: `add_documents`, `similarity_search`, `as_retriever` are the same for pgvector, Pinecone, Redis, Mongo, Elasticsearch and others.

```python
from langchain_core.vectorstores import VectorStore


def build_retriever(vs: VectorStore, k: int = 5):
    """Any backend works: the rest of the LCEL chain or LangGraph graph never changes."""
    return vs.as_retriever(search_kwargs={"k": k})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing from vendor benchmarks
```python
# Wrong: "Vendor X is 10x faster in their blog" -> pick X
# Right: run recall@10 and p95 on your own 100K vectors, your filters, your hardware
```

❌ Mistake 2: Ignoring migration cost
```python
# Wrong: calls to one SDK in 60 places
# Right: one VectorStore adapter, plus a script that can re-embed and re-load from the source of truth
```

---

## 🧠 Tricky Interview Question

**Q**: "Your CTO says 'use the fastest vector DB'. How do you respond?"

**Answer**: Fastest at what? ANN speed alone rarely dominates end-to-end latency, because the LLM call takes seconds and the vector query takes milliseconds. Choose on total cost, recall under your filters, operational burden, security and team skills. A 5 ms versus 15 ms difference is irrelevant next to a 2-second generation, while an extra service to run is a permanent cost. Benchmark with real data and pick the simplest option that meets the SLA.

---

## ⚫ Interview Questions + Answers

Q1: Name four factors for choosing a vector DB.
A1: Scale (vector count), latency/QPS, filtering and hybrid needs, and operational/cost constraints.

Q2: When is pgvector enough?
A2: Up to roughly tens of millions of vectors, moderate QPS, and when you already run Postgres and need joins and transactions.

Q3: Why test with your own data?
A3: Recall and latency depend on embedding distribution, dimension, filters and hardware. Public benchmarks seldom match your workload.

Q4: What is vendor lock-in here and how do you reduce it?
A4: Proprietary APIs make switching costly. Use an adapter interface or LangChain's VectorStore, keep raw text and metadata in your own database, and store the embedding model name/version so you can re-embed.

Q5: Design the evaluation plan for choosing between pgvector and Qdrant.
A5: Take 100K to 1M real documents and 200 labelled queries. Build the same HNSW parameters. Measure recall@10 against exact search, p50/p95/p99 latency at target QPS, filter-heavy query behaviour, ingestion speed, memory, backup/restore, and monthly cost at 12-month volume. Score with weights agreed by stakeholders, then decide and record the reasoning.

---

## 🔷 When to Use + When Not to Use
✅ Use a decision framework when:
- Starting a new RAG platform or planning scale-up
- Costs or latency are growing unexpectedly

❌ Avoid over-analysis when:
- Prototype with under 100K vectors: use what is easiest (Chroma, pgvector) and move on

---

## 📊 Visual Diagram
```
                 ┌──────────── vectors > 50M? ────────────┐
                 │ yes                                    │ no
        ops team available?                      already on Postgres?
        │ yes          │ no                       │ yes            │ no
    Milvus/Qdrant   Managed cloud               pgvector     hybrid search needed?
    (self-hosted)   (Pinecone/Zilliz)                         │ yes          │ no
                                                        Elasticsearch   Qdrant / Chroma
```

---

## 💰 Cost Impact
- The DB choice mostly changes infra cost, not token cost; but poor recall leads to bigger k and bigger prompts, which raises LLM tokens (for example k=10 instead of k=4 adds about 1,800 tokens per request at 300 tokens per chunk).
- Total cost = embeddings (one time) + storage/RAM + compute for queries + LLM tokens + engineering hours. Reusing existing infrastructure usually wins for small to medium workloads.
- Optimise: lower dimensions, quantization, tiered storage, TTL cleanup.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recall@k | Share of true top-k found | सही top-k मिलने का अनुपात |
| p95 latency | 95% requests faster than this | 95% requests इससे तेज़ |
| QPS | Queries per second | प्रति सेकंड queries |
| Lock-in | Hard to switch vendor | Vendor बदलना मुश्किल |
| Multi-tenancy | Many customers in one system | कई customers एक system में |
| Benchmark | Measured comparison | नापकर तुलना |

---

## ⚡ 3-Line Summary
English: Pick the simplest vector DB that meets scale, latency, filter and budget needs. Start with what you already run and benchmark on your own data. Hide the choice behind an interface.
Hindi: वह सबसे सरल vector DB चुनो जो scale, latency, filter और budget की ज़रूरतें पूरी करे। जो पहले से चल रहा है उससे शुरू करो और अपने data पर benchmark करो। चुनाव को interface के पीछे रखो।

---

## ➡️ Next Topic
**151. Vector DB Indexing Strategy** — FLAT vs IVF vs HNSW and how to tune them.
