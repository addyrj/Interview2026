---

# 155. Vector DB Best Practices
# हिंदी में: Vector DB Best Practices

---

## 🔵 Simple Definition (English)
Vector DB best practices are the habits that keep a vector search system correct, fast, secure and maintainable: consistent embeddings, good ids and metadata, versioning, evaluation, access control, backups and monitoring.

## 🔵 सरल परिभाषा (Hindi)
Vector DB best practices वे आदतें हैं जो vector search system को सही, तेज़, सुरक्षित और maintainable रखती हैं: consistent embeddings, अच्छे ids और metadata, versioning, evaluation, access control, backups और monitoring।

---

## 🔴 Problem it Solves
Common production failures: mixed embedding models, no way to delete a customer's data, stale chunks answering with last year's tariff rates, one tenant seeing another's documents, and quality regressions nobody notices. Practices prevent these.

## 🔴 यह क्यों बना? (Hindi)
Production में आम failures: embedding models का मिश्रण, किसी customer का data delete करने का तरीका नहीं, पुराने chunks से पिछले साल के tariff rates के जवाब, एक tenant को दूसरे के documents दिखना, और quality गिरना जिसका किसी को पता नहीं चलता। Best practices इन्हें रोकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Schema: id, text, embedding, model_name, model_version, source, version, tenant_id, created_at
Step 2 → Deterministic ids (hash of source + chunk index) so re-ingestion is an upsert, not a duplicate
Step 3 → Same embedding model for documents and queries; never mix; migrate to a new index
Step 4 → Metadata for filtering (country, year, doc_type) and for citations (page, url)
Step 5 → Security: tenant filter enforced server-side, least-privilege DB role, encryption, no secrets in logs
Step 6 → Operate: backups, evaluation set in CI, monitoring (recall, p95, error rate, index freshness)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Schema: id, text, embedding, model_name, model_version, source, version, tenant_id, created_at
Step 2 → Deterministic ids (source + chunk index का hash) ताकि दोबारा ingest upsert बने, duplicate नहीं
Step 3 → Documents और queries के लिए एक ही embedding model; मिलाओ मत; नए index पर migrate करो
Step 4 → Filtering (country, year, doc_type) और citations (page, url) के लिए metadata
Step 5 → Security: tenant filter server-side लागू, least-privilege DB role, encryption, logs में secrets नहीं
Step 6 → Operate: backups, CI में evaluation set, monitoring (recall, p95, error rate, index freshness)
```

---

## 🟡 Real World Example
**Tariff Classification System**: tariff schedules change each year. Each chunk stores `schedule_year` and `status`. Ingesting the 2026 schedule marks 2025 chunks `status='superseded'`; queries filter `status='active'`. A regression suite of 150 labelled product descriptions runs in CI before any embedding model, chunking or index change reaches production.

**Zomato AI**: each restaurant's private notes carry `tenant_id`; the API adds the filter from the authenticated user, never from the request body.

## 🟡 Real Example Hindi mein
**Tariff System**: tariff schedules हर साल बदलते हैं। हर chunk में `schedule_year` और `status` रहता है। 2026 schedule ingest होने पर 2025 chunks `status='superseded'` हो जाते हैं; queries `status='active'` filter करती हैं। 150 labelled product descriptions की regression suite किसी भी embedding model, chunking या index बदलाव से पहले CI में चलती है।

**Zomato AI**: हर restaurant के private notes में `tenant_id` है; API filter authenticated user से लगाता है, request body से कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Runs offline: deterministic ids + metadata validation with pydantic-free dataclasses
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


def chunk_id(source: str, index: int, text: str) -> str:
    """Deterministic id: same source+position+text always gives the same id (idempotent upserts)."""
    raw = f"{source}|{index}|{text}".encode("utf-8")  # combine identity parts
    return hashlib.sha256(raw).hexdigest()[:32]  # short but collision-safe enough


@dataclass
class ChunkRecord:
    source: str
    index: int
    text: str
    tenant_id: str
    model_name: str = "text-embedding-3-small"  # which model produced the vector
    schedule_year: int = 2026
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("empty text")  # never embed empty chunks
        if self.status not in {"active", "superseded"}:
            raise ValueError(f"bad status {self.status!r}")

    @property
    def id(self) -> str:
        return chunk_id(self.source, self.index, self.text)


rec = ChunkRecord("tariff_2026.pdf", 12, "Headphones fall under 8518.30", tenant_id="acme")
print(rec.id, rec.status, rec.schedule_year)  # same input -> same id every run
```

## 💻 Code Example — Advanced
```python
# Production: tenant-safe search wrapper + embedding-model guard + audit log (async)
import logging
from dataclasses import dataclass
from typing import Any, Protocol

log = logging.getLogger("vector_guard")


class Store(Protocol):
    async def query(self, vec: list[float], k: int, flt: dict[str, Any]) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class AuthContext:
    tenant_id: str  # comes from the verified auth token, NOT the request body
    user_id: str


class GuardedSearch:
    EXPECTED_MODEL = "text-embedding-3-small"
    EXPECTED_DIM = 1536

    def __init__(self, store: Store) -> None:
        self.store = store

    async def search(self, auth: AuthContext, vec: list[float], model: str, k: int = 5) -> list[dict[str, Any]]:
        if model != self.EXPECTED_MODEL or len(vec) != self.EXPECTED_DIM:  # block silent model mixing
            raise ValueError("embedding model/dimension mismatch with index")
        if not 1 <= k <= 20:
            raise ValueError("k must be between 1 and 20")  # protect the DB
        flt = {"tenant_id": auth.tenant_id, "status": "active"}  # mandatory server-side filters
        try:
            hits = await self.store.query(vec, k, flt)
        except Exception:
            log.exception("vector query failed tenant=%s", auth.tenant_id)  # no vectors or secrets in logs
            raise
        log.info("search tenant=%s user=%s hits=%d", auth.tenant_id, auth.user_id, len(hits))  # audit trail
        return hits
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


async def get_auth(authorization: str = Header(...)) -> AuthContext:
    # Verify a real JWT here (signature, expiry) and read tenant from its claims.
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    return AuthContext(tenant_id="acme", user_id="u1")  # placeholder for decoded claims


@app.post("/tariff/search")
async def search(body: dict, auth: AuthContext = Depends(get_auth)) -> dict:
    guard: GuardedSearch = app.state.guard  # built at startup around your store
    hits = await guard.search(auth, body["vector"], body["model"], k=5)  # tenant comes from auth only
    return {"results": hits}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain indexing API: sync documents to a vector store without duplicates and delete stale ones
from langchain.indexes import SQLRecordManager, index

record_manager = SQLRecordManager("pgvector/tariff", db_url="sqlite:///record_manager.db")
record_manager.create_schema()  # tracks hashes of what was indexed

# result = index(docs, record_manager, vector_store, cleanup="incremental", source_id_key="source")
# cleanup="incremental" removes old chunks of changed sources: tariff updates stay consistent.
# In LangGraph, pass tenant_id through the graph config and apply it inside the retrieve node's filter.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Taking the tenant filter from client input
```python
# Wrong: attacker sends {"tenant_id": "other_company"}
flt = {"tenant_id": body["tenant_id"]}
# Right: derive from the authenticated identity
flt = {"tenant_id": auth.tenant_id}
```

❌ Mistake 2: Random uuid ids on every ingestion run
```python
# Wrong: duplicates pile up and old versions never get replaced
id = str(uuid.uuid4())
# Right: deterministic id, upsert by id
id = chunk_id(source, index, text)
```

---

## 🧠 Tricky Interview Question

**Q**: "A customer invokes their right to erasure. You delete their rows from Postgres, but they say their data still appears in AI answers. What did you miss?"

**Answer**: Copies live in many places: the vector store (embeddings and the text payload), caches (semantic cache, embedding cache, answer cache), search indexes, backups, logs and traces, and possibly fine-tuning data. Embeddings can leak content, so they count as personal data. A correct design tags every record with `tenant_id`/`subject_id`, deletes by filter in the vector DB, flushes caches by tag, expires logs, and documents backup retention. Test it: after deletion, query for the person's content and confirm that nothing returns.

---

## ⚫ Interview Questions + Answers

Q1: Why store the embedding model name with each vector?
A1: Vectors from different models are not comparable. The name lets you detect mixing and plan migrations.

Q2: Why deterministic ids?
A2: Re-ingestion becomes an idempotent upsert, avoiding duplicates and enabling updates and deletes by id.

Q3: How do you handle document updates?
A3: Compare content hashes, re-embed changed chunks, upsert by id, and delete chunks that no longer exist for that source (or mark them superseded).

Q4: How do you secure a multi-tenant vector DB?
A4: Enforce tenant filters server-side from auth claims, use namespaces or separate collections for strict isolation, least-privilege credentials, encryption in transit and at rest, and audit logs.

Q5: How do you detect quality regression after changes?
A5: Maintain a labelled evaluation set with expected sources, run recall@k and MRR in CI on every change to chunking, model or index, alert on drops, and sample production queries for human review. Keep the old index until the new one passes.

---

## 🔷 When to Use + When Not to Use
✅ Use all of these when:
- Real users, real data, or regulated content

❌ Skip heavy process when:
- Throwaway prototypes; but still keep deterministic ids and the model name, they cost nothing

---

## 📊 Visual Diagram
```
 ingest:  doc ─► chunk ─► hash ─► changed? ─► embed ─► upsert(id, vec, metadata{tenant,year,status,model})
                                   no ─► skip
 query :  auth ─► tenant filter ─► embed(same model) ─► ANN + filters ─► top-k ─► LLM
 ops   :  CI eval set │ backups │ monitoring (recall, p95, errors) │ audit log │ delete-by-filter
```

---

## 💰 Cost Impact
- Hash-based incremental ingestion and caches avoid paying repeatedly for embedding tokens.
- Active/superseded status filters keep stale chunks out of prompts, avoiding wasted LLM tokens and wrong answers.
- Evaluation sets let you shrink k safely (for example from 8 to 4 chunks), saving around 1,200 input tokens per request at 300 tokens per chunk.
- Delete unused collections and old index versions to stop paying for idle RAM.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Idempotent upsert | Repeat write with same result | बार-बार चलाने पर वही नतीजा |
| Tenant isolation | Customers cannot see each other | Customers का data अलग |
| Superseded | Replaced by newer version | नए version से बदला हुआ |
| Evaluation set | Labelled queries for testing | Testing के लिए labelled queries |
| Audit log | Record of who did what | किसने क्या किया का record |
| Right to erasure | Delete a person's data on request | माँगने पर data हटाने का अधिकार |

---

## ⚡ 3-Line Summary
English: Use deterministic ids, store model and version metadata, and never mix embedding models. Enforce tenant filters server-side, handle updates and deletes, and keep an evaluation set in CI. Monitor recall, latency and cost together.
Hindi: Deterministic ids use करो, model और version metadata रखो, और embedding models कभी मत मिलाओ। Tenant filters server-side लागू करो, updates और deletes संभालो, और CI में evaluation set रखो। Recall, latency और cost साथ मॉनिटर करो।

---

## ➡️ Next Topic
**156. Why Chunking Matters** — the next stage of RAG: how splitting documents decides retrieval quality.
