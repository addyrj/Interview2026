---

# 188. Indexing Pipeline
# हिंदी में: Indexing Pipeline (इंडेक्सिंग पाइपलाइन)

---

## 🔵 Simple Definition (English)
The indexing pipeline is the offline job that turns raw documents into a searchable index: load, clean, chunk, enrich with metadata, embed, and upsert into the vector store. It must be repeatable, incremental and idempotent so re-running it never creates duplicates.

## 🔵 सरल परिभाषा (Hindi)
Indexing pipeline वह offline job है जो raw documents को searchable index में बदलती है: load, clean, chunk, metadata जोड़ना, embed, और vector store में upsert। यह repeatable, incremental और idempotent होनी चाहिए ताकि दोबारा चलाने पर duplicates न बनें।

---

## 🔴 Problem it Solves
Quick scripts index everything once. Then documents change, new files arrive, the job crashes halfway, and the index fills with duplicates and stale chunks. Re-embedding the entire corpus on each change wastes money and time. A proper indexing pipeline handles change detection, retries and cleanup.

## 🔴 यह क्यों बना? (Hindi)
Quick scripts सब कुछ एक बार index करती हैं। फिर documents बदलते हैं, नई files आती हैं, job बीच में crash होती है, और index में duplicates व stale chunks भर जाते हैं। हर बदलाव पर पूरा corpus re-embed करना पैसे और समय की बर्बादी है। Proper pipeline change detection, retries और cleanup संभालती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Discover sources (folder, S3, DB table, URL list)
Step 2 → Compute content hash per document; skip unchanged ones
Step 3 → Load + clean the changed documents
Step 4 → Chunk with stable chunk ids: f"{doc_id}:{chunk_no}:{hash}"
Step 5 → Attach metadata (source, page, chapter, version, indexed_at)
Step 6 → Embed in batches (e.g., 64 chunks) with retry + backoff
Step 7 → Delete old chunks of the changed doc, upsert the new ones
Step 8 → Record a manifest (doc_id -> hash) and log counts / tokens / failures
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Sources खोजो (folder, S3, DB table, URL list)
Step 2 → हर document का content hash निकालो; unchanged skip करो
Step 3 → बदले हुए documents load + clean करो
Step 4 → Stable chunk ids के साथ chunk करो
Step 5 → Metadata जोड़ो (source, page, chapter, version, indexed_at)
Step 6 → Batches में embed करो, retry + backoff के साथ
Step 7 → बदले doc के पुराने chunks delete करो, नए upsert करो
Step 8 → Manifest (doc_id -> hash) सेव करो; counts / tokens / failures log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs publishes a new tariff schedule every January and amendments monthly. The indexer hashes each file, finds only 3 of 400 PDFs changed, deletes their old chunks (`doc_id` filter), re-embeds ~600 chunks (not 120,000) and updates the manifest. Cost: cents, not dollars.
**Amazon AI**: Product descriptions change hourly; a nightly incremental indexer re-embeds only changed products.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs हर January नया tariff schedule और हर महीने amendments निकालता है। Indexer हर file का hash देखता है, 400 में से सिर्फ 3 PDFs बदली मिलती हैं, उनके पुराने chunks delete होते हैं, ~600 chunks (120,000 नहीं) re-embed होते हैं। Cost: dollars नहीं, cents।
**Amazon AI**: Product descriptions हर घंटे बदलती हैं; nightly incremental indexer सिर्फ बदले products re-embed करता है।

---

## 💻 Code Example — Basic
```python
# Incremental indexing with a hash manifest (pure Python, runs directly)
import hashlib
from typing import Dict, List

MANIFEST: Dict[str, str] = {}  # doc_id -> last indexed content hash
INDEX: Dict[str, str] = {}  # chunk_id -> chunk text (our fake vector store)

def content_hash(text: str) -> str:
    """Stable fingerprint of the document content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]  # short hash is enough here

def chunk(text: str, size: int = 5) -> List[str]:
    """Split into word windows."""
    words = text.split()  # words
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]

def index_document(doc_id: str, text: str) -> str:
    """Index one doc; return 'skipped', 'added' or 'updated'."""
    h = content_hash(text)  # fingerprint
    if MANIFEST.get(doc_id) == h:  # unchanged
        return "skipped"
    status = "updated" if doc_id in MANIFEST else "added"  # new or changed
    for cid in [c for c in INDEX if c.startswith(f"{doc_id}:")]:  # remove stale chunks
        del INDEX[cid]
    for n, piece in enumerate(chunk(text)):  # write fresh chunks
        INDEX[f"{doc_id}:{n}"] = piece
    MANIFEST[doc_id] = h  # remember the hash
    return status

if __name__ == "__main__":
    print(index_document("ch85", "HS 8517.13 smartphones duty 0 percent in 2025"))  # added
    print(index_document("ch85", "HS 8517.13 smartphones duty 0 percent in 2025"))  # skipped
    print(index_document("ch85", "HS 8517.13 smartphones duty 5 percent in 2026"))  # updated
    print(len(INDEX), "chunks in index")  # no duplicates
```

## 💻 Code Example — Advanced
```python
# Async batch indexer with retry/backoff, bounded concurrency and a report
import asyncio
import hashlib
import logging
import random
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence

logger = logging.getLogger("indexer")  # logger

EmbedFn = Callable[[Sequence[str]], Awaitable[list[list[float]]]]  # embedding backend
UpsertFn = Callable[[list[str], list[list[float]], list[dict]], Awaitable[None]]  # store backend

@dataclass
class IndexReport:
    indexed: int = 0  # chunks written
    skipped_docs: int = 0  # unchanged docs
    failed_batches: int = 0  # batches that exhausted retries
    approx_tokens: int = 0  # rough embedding tokens
    errors: list[str] = field(default_factory=list)  # messages

async def with_retry(fn: Callable[[], Awaitable], tries: int = 4) -> object:
    """Exponential backoff with jitter for rate limits/timeouts."""
    for attempt in range(tries):
        try:
            return await fn()  # success path
        except Exception as exc:
            if attempt == tries - 1:  # out of retries
                raise
            delay = (2 ** attempt) + random.random()  # 1s, 2s, 4s (+jitter)
            logger.warning("retry in %.1fs: %s", delay, exc)
            await asyncio.sleep(delay)

class Indexer:
    def __init__(self, embed: EmbedFn, upsert: UpsertFn, manifest: dict[str, str],
                 batch: int = 64, concurrency: int = 4) -> None:
        self.embed, self.upsert, self.manifest = embed, upsert, manifest  # deps
        self.batch, self.sem = batch, asyncio.Semaphore(concurrency)  # limit parallel API calls

    async def _do_batch(self, ids: list[str], texts: list[str], metas: list[dict], rep: IndexReport) -> None:
        async with self.sem:  # bounded concurrency
            try:
                vecs = await with_retry(lambda: self.embed(texts))  # embed with retry
                await with_retry(lambda: self.upsert(ids, vecs, metas))  # idempotent upsert
                rep.indexed += len(ids)  # count success
                rep.approx_tokens += int(sum(len(t.split()) for t in texts) * 1.3)
            except Exception as exc:  # isolate failures per batch
                rep.failed_batches += 1
                rep.errors.append(repr(exc))

    async def run(self, docs: dict[str, str], chunker: Callable[[str], list[str]]) -> IndexReport:
        rep = IndexReport()  # fresh report
        ids: list[str] = []; texts: list[str] = []; metas: list[dict] = []  # pending chunks
        for doc_id, text in docs.items():
            h = hashlib.sha256(text.encode()).hexdigest()  # doc hash
            if self.manifest.get(doc_id) == h:  # unchanged
                rep.skipped_docs += 1
                continue
            for n, piece in enumerate(chunker(text)):  # build chunks
                ids.append(f"{doc_id}:{n}"); texts.append(piece); metas.append({"doc_id": doc_id})
            self.manifest[doc_id] = h  # (commit only after success in real code)
        tasks = [self._do_batch(ids[i:i + self.batch], texts[i:i + self.batch], metas[i:i + self.batch], rep)
                 for i in range(0, len(ids), self.batch)]  # one task per batch
        await asyncio.gather(*tasks)  # run concurrently
        return rep
```

---

## 🟠 FastAPI Integration
Expose indexing as an admin-only endpoint that returns a job id immediately (HTTP 202) and runs the indexer in the background. A second endpoint reports status. For heavy workloads use Celery/RQ/Arq instead of in-process tasks.

```python
# FastAPI admin endpoints for indexing jobs
import uuid
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()  # app
JOBS: dict[str, dict] = {}  # job_id -> status (use Redis/DB in production)

class IndexRequest(BaseModel):
    docs: dict[str, str]  # doc_id -> text

def require_admin(x_api_key: str = Header(...)) -> None:
    if x_api_key != "change-me":  # replace with real secret check
        raise HTTPException(status_code=403, detail="forbidden")

async def job(job_id: str, docs: dict[str, str]) -> None:
    JOBS[job_id] = {"status": "running"}  # mark running
    rep = await indexer.run(docs, chunker=lambda t: t.split(". "))  # indexer from Advanced example
    JOBS[job_id] = {"status": "done", "indexed": rep.indexed, "failed": rep.failed_batches}

@app.post("/admin/index", status_code=202, dependencies=[Depends(require_admin)])
async def start(req: IndexRequest, bg: BackgroundTasks) -> dict:
    job_id = str(uuid.uuid4())  # new job id
    bg.add_task(job, job_id, req.docs)  # run after response
    return {"job_id": job_id}

@app.get("/admin/index/{job_id}")
async def status(job_id: str) -> dict:
    return JOBS.get(job_id, {"status": "unknown"})
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships an **Indexing API** (`langchain.indexes.index` with `SQLRecordManager`) that tracks hashes and deletes stale documents for you (cleanup modes: `None`, `incremental`, `full`).

```python
# LangChain indexing API with a record manager (needs langchain, langchain-chroma, langchain-openai)
from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

store = Chroma(collection_name="tariffs", embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))  # target store
rm = SQLRecordManager("chroma/tariffs", db_url="sqlite:///record_manager.sqlite")  # tracks what was indexed
rm.create_schema()  # create tables once
docs = [Document(page_content="HS 0902.30 tea duty 10", metadata={"source": "ch09.pdf"})]  # input docs
# result = index(docs, rm, store, cleanup="incremental", source_id_key="source")  # needs OPENAI_API_KEY
# print(result)  # {'num_added': 1, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 0}
```
In LangGraph, indexing is usually a separate batch job, not part of the query graph.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-indexing everything on every run, with random chunk ids.
✅ Correct: Use content hashes and deterministic ids so upserts replace rather than duplicate.

```python
# Wrong
store.add_texts(chunks)  # new uuid every run -> duplicates
# Right
store.add_texts(chunks, ids=[f"{doc_id}:{i}" for i in range(len(chunks))])
```

❌ Mistake 2: Updating the manifest before the writes succeed.
✅ Correct: Commit the hash only after upsert succeeds, otherwise a crash leaves docs marked "done" but missing.

```python
# Wrong
manifest[doc_id] = h; await upsert(...)   # crash between = lost document
# Right
await upsert(...); manifest[doc_id] = h
```

---

## 🧠 Tricky Interview Question
**Q**: "A tariff PDF was corrected: one paragraph shortened. After re-indexing, users still see old text sometimes. Why?"

**Answer**: Chunk boundaries shifted. If chunk ids are `doc:chunk_no` and the new version has fewer chunks, the trailing old chunks (e.g., `doc:41`) were never overwritten, so stale text remains. Fix: delete all chunks by `doc_id` before upserting (or use the record manager with `cleanup="incremental"`), and store a `version` in metadata. Also check any semantic cache holding old answers.

---

## ⚫ Interview Questions + Answers

Q1: What does idempotent indexing mean?
A1: Running the pipeline twice gives the same index, with no duplicates; achieved with deterministic ids and upserts.

Q2: How do you detect that a document changed?
A2: Compare a content hash (or file modified time/ETag) against the stored manifest.

Q3: Why batch embedding requests?
A3: Fewer HTTP calls, higher throughput, lower rate-limit pressure; embedding APIs accept lists (up to a few thousand inputs/limits per call).

Q4: How do you handle rate limits during large indexing?
A4: Exponential backoff with jitter, a semaphore for concurrency, smaller batches, and a resumable manifest so a failed run continues where it stopped.

Q5: Design indexing for 1M documents that update daily.
A5: Event-driven (S3/DB change events to a queue), workers hash and skip unchanged docs, chunk and embed in batches, upsert with doc-level delete, write manifest after success, dead-letter queue for failures, metrics for lag and token spend, and blue/green collections when the embedding model changes.

---

## 🔷 When to Use + When Not to Use
✅ Use a robust pipeline when:
- Data changes over time
- Corpus is large (re-embedding is costly)
- Multiple teams depend on the index

❌ Avoid heavy machinery when:
- One-time static corpus of a few hundred pages
- Prototype demo (a simple script is fine)

---

## 📊 Visual Diagram
```
 Sources ──► Hash check ──unchanged──► skip
               │ changed
               ▼
        Load → Clean → Chunk (stable ids) → Metadata
               │
               ▼
       Batch embed (retry/backoff)
               │
               ▼
   delete old doc chunks → upsert new → update manifest
               │
               ▼
          Report (indexed / skipped / failed / tokens)
```

---

## 💰 Cost Impact
Embedding cost = tokens x price. Example: 400 PDFs x 300 chunks x 400 tokens = 48M tokens = ~0.96 USD at 0.02 USD/1M. Full re-index monthly is cheap here, but at 10B tokens it is 200 USD each time. Incremental indexing reduces this by 95 percent or more.
Optimize: hash-skip unchanged docs, cache embeddings by chunk hash, use a smaller/dimension-reduced model where recall allows, use the Batch API for non-urgent bulk jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Idempotent | Same result if run repeatedly | बार-बार चलाने पर भी वही नतीजा |
| Manifest | Record of what was indexed | क्या index हुआ उसका record |
| Upsert | Insert or update by id | Id से insert या update |
| Content hash | Fingerprint of content | Content की पहचान |
| Backoff | Waiting longer after each retry | हर retry पर ज़्यादा इंतज़ार |
| Stale chunk | Outdated leftover chunk | पुराना बचा हुआ chunk |

---

## ⚡ 3-Line Summary
English: Indexing turns documents into a searchable store through load, chunk, embed, upsert.
Make it incremental and idempotent with hashes, stable ids and retries.
This keeps the index fresh and cuts embedding cost.
Hindi: Indexing documents को load, chunk, embed, upsert से searchable store में बदलती है।
Hashes, stable ids और retries से इसे incremental और idempotent बनाओ।
इससे index ताज़ा रहता है और embedding cost घटती है।

---

## ➡️ Next Topic
**189. Retrieval Pipeline**: the online half that fetches the best chunks at query time.
