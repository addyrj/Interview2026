---

# 133. Pinecone Upsert + Query
# हिंदी में: Pinecone Upsert + Query (data डालना और खोजना)

---

## 🔵 Simple Definition (English)
`upsert` writes vectors into an index (insert new, overwrite existing by id). `query` takes a query vector and returns the `top_k` most similar vectors with scores and (optionally) metadata. Together they are the read/write core of any Pinecone app.

## 🔵 सरल परिभाषा (Hindi)
`upsert` index में vectors लिखता है (नया हो तो insert, id पहले से हो तो overwrite)। `query` एक query vector लेकर `top_k` सबसे similar vectors scores और (optional) metadata के साथ लौटाता है। ये दोनों मिलकर हर Pinecone app का read/write core हैं।

---

## 🔴 Problem it Solves
Naive ingestion (one vector per request) is slow and hits rate limits; oversize requests fail (request size limit around 2 MB, and batches of 100-200 vectors are recommended). Naive querying forgets `include_metadata`, returns scores nobody interprets, or sends huge `top_k`. Correct batching, ids and query options make ingestion fast and idempotent, and retrieval useful.

## 🔴 यह क्यों बना? (Hindi)
Naive ingestion (हर request में एक vector) धीमा है और rate limit मारता है; बहुत बड़ी requests fail होती हैं (request size limit ~2 MB, 100-200 vectors का batch recommended)। Naive query में `include_metadata` भूल जाते हैं या बहुत बड़ा `top_k` भेजते हैं। सही batching, ids और query options से ingestion तेज़ और idempotent बनता है।

---

## 🟢 How it Works — Step by Step

```
Upsert:
Step 1 → Chunk documents -> embed in batches -> list of (id, values, metadata)
Step 2 → Use STABLE ids (e.g. f"{doc_id}#{chunk_no}") so re-runs overwrite, not duplicate
Step 3 → Split into batches of ~100 vectors
Step 4 → index.upsert(vectors=batch, namespace=ns); retry on 429/5xx with backoff
Query:
Step 5 → Embed the question with the SAME model
Step 6 → index.query(vector=q, top_k=5, include_metadata=True, namespace=ns, filter=...)
Step 7 → matches = [{id, score, metadata}], sorted best first
Step 8 → Drop matches below a score threshold, build the LLM context from metadata["text"]
```

## 🟢 कैसे काम करता है? (Hindi)

```
Upsert:
Step 1 → Documents chunk करो -> batches में embed करो -> (id, values, metadata) की list
Step 2 → STABLE ids रखो (जैसे f"{doc_id}#{chunk_no}") ताकि दोबारा चलाने पर overwrite हो, duplicate नहीं
Step 3 → ~100 vectors के batches में बाँटो
Step 4 → index.upsert(vectors=batch, namespace=ns); 429/5xx पर backoff के साथ retry
Query:
Step 5 → Question को उसी model से embed करो
Step 6 → index.query(vector=q, top_k=5, include_metadata=True, namespace=ns, filter=...)
Step 7 → matches = [{id, score, metadata}], best पहले
Step 8 → Score threshold से कम वाले हटाओ, metadata["text"] से LLM context बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: each HS heading is split into chunks with ids like `8518.30#0`. Nightly sync re-embeds only changed headings and upserts them; the same ids overwrite old versions, so there are no duplicates. A query "wireless earbuds with case" returns `8518.30#0` (score 0.84), `8517.62#1` (0.77), and we drop anything under 0.5.

**Amazon-style**: product id = vector id. Price changes only update metadata via `index.update(id=..., set_metadata={"price": 1999})`, avoiding a re-embed.

## 🟡 Real Example Hindi mein
**Tariff System**: हर HS heading chunks में बँटती है, ids जैसे `8518.30#0`। Nightly sync सिर्फ़ बदली headings को re-embed करके upsert करता है; वही ids पुराने version को overwrite करते हैं, duplicates नहीं बनते। Query "wireless earbuds with case" से `8518.30#0` (0.84), `8517.62#1` (0.77) मिलते हैं, 0.5 से कम वाले हटा देते हैं। **Amazon-style**: product id ही vector id है; price बदलने पर `index.update(id=..., set_metadata=...)` से सिर्फ़ metadata बदलता है, re-embed नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: build upsert records + batch them + query-result post-processing. Offline-safe.
from typing import Any, Dict, Iterator, List               # type hints

def make_records(doc_id: str, chunks: List[str], vecs: List[List[float]], country: str) -> List[Dict[str, Any]]:
    """Create Pinecone-shaped records with stable ids."""
    if len(chunks) != len(vecs):                           # sanity check
        raise ValueError("chunks and vectors length mismatch")
    return [
        {"id": f"{doc_id}#{i}",                            # stable id -> idempotent upsert
         "values": v,                                      # the embedding
         "metadata": {"text": c[:500], "country": country, "doc_id": doc_id}}   # small payload only
        for i, (c, v) in enumerate(zip(chunks, vecs))
    ]

def batched(items: List[Any], size: int = 100) -> Iterator[List[Any]]:
    for i in range(0, len(items), size):                   # step through the list
        yield items[i:i + size]                            # one batch at a time

def keep_relevant(matches: List[Dict[str, Any]], min_score: float = 0.5) -> List[Dict[str, Any]]:
    return [m for m in matches if m["score"] >= min_score] # drop weak matches

recs = make_records("8518.30", ["Headphones, earphones", "Microphones"], [[0.1] * 4, [0.2] * 4], "IN")
print([b[0]["id"] for b in batched(recs, 1)])              # ['8518.30#0', '8518.30#1']
print(keep_relevant([{"id": "a", "score": 0.84}, {"id": "b", "score": 0.3}]))   # keeps only "a"

# Real calls (need PINECONE_API_KEY + an index handle called `index`):
#   for b in batched(recs): index.upsert(vectors=b, namespace="headings")
#   res = index.query(vector=q, top_k=5, include_metadata=True, namespace="headings")
#   matches = [{"id": m.id, "score": m.score, **m.metadata} for m in res.matches]
```

## 💻 Code Example — Advanced
```python
# Advanced: concurrent batched upsert with retry + rate-limit semaphore, query with filter,
# update/delete helpers, async throughout. Pinecone SDK calls are blocking, so use to_thread.
import asyncio                                             # async runtime
import logging                                             # logs
import random                                              # jitter
from typing import Any, Dict, List, Optional               # type hints

log = logging.getLogger("pc-io")                           # logger

class PineconeIO:
    def __init__(self, index: Any, namespace: str, concurrency: int = 4) -> None:
        self.index = index                                 # pinecone Index handle
        self.ns = namespace                                # namespace to read/write
        self.sem = asyncio.Semaphore(concurrency)          # cap parallel requests (avoid 429)

    async def _upsert_batch(self, batch: List[Dict[str, Any]], retries: int = 4) -> int:
        async with self.sem:                               # respect concurrency limit
            for attempt in range(retries):                 # retry loop
                try:
                    await asyncio.to_thread(self.index.upsert, vectors=batch, namespace=self.ns)
                    return len(batch)                      # success
                except Exception as exc:                   # network, 429, 5xx
                    wait = 2 ** attempt + random.random()  # exponential backoff + jitter
                    log.warning("upsert attempt %d failed: %s (sleep %.1fs)", attempt + 1, exc, wait)
                    await asyncio.sleep(wait)              # wait before retry
            raise RuntimeError(f"batch starting {batch[0]['id']} failed permanently")

    async def upsert_all(self, records: List[Dict[str, Any]], batch_size: int = 100) -> int:
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]   # split
        counts = await asyncio.gather(*(self._upsert_batch(b) for b in batches))            # parallel
        return sum(counts)                                 # total written

    async def query(self, vec: List[float], k: int = 5, flt: Optional[Dict[str, Any]] = None,
                    min_score: float = 0.0) -> List[Dict[str, Any]]:
        res = await asyncio.to_thread(                     # blocking SDK call off the loop
            self.index.query, vector=vec, top_k=k, filter=flt,
            include_metadata=True, namespace=self.ns)
        return [{"id": m.id, "score": m.score, **(m.metadata or {})}
                for m in res.matches if m.score >= min_score]

    async def update_metadata(self, vec_id: str, **fields: Any) -> None:
        await asyncio.to_thread(self.index.update, id=vec_id, set_metadata=fields, namespace=self.ns)

    async def delete(self, ids: List[str]) -> None:
        await asyncio.to_thread(self.index.delete, ids=ids, namespace=self.ns)   # remove stale vectors

# Token usage: only embedding calls cost tokens (~300 tokens per chunk). Upsert/query cost
# write/read units, not tokens.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks   # FastAPI
from openai import AsyncOpenAI                                # embeddings
from pydantic import BaseModel, Field                         # pydantic v2

app = FastAPI()                                               # app
oai = AsyncOpenAI()                                           # client
# io = PineconeIO(index, "headings")                          # created at startup (see 132)

class Doc(BaseModel):
    doc_id: str                                               # stable document id
    chunks: list[str] = Field(min_length=1, max_length=500)   # text chunks
    country: str = "IN"                                       # metadata

@app.post("/ingest", status_code=202)                         # accept and process in background
async def ingest(doc: Doc, bg: BackgroundTasks) -> dict:
    async def job() -> None:
        resp = await oai.embeddings.create(model="text-embedding-3-small", input=doc.chunks)
        recs = make_records(doc.doc_id, doc.chunks, [d.embedding for d in resp.data], doc.country)
        await io.upsert_all(recs)                             # batched concurrent upsert
    bg.add_task(job)                                          # do not block the request
    return {"status": "queued", "chunks": len(doc.chunks)}

@app.get("/query")                                            # query route
async def query(q: str, country: str | None = None) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    flt = {"country": {"$eq": country}} if country else None
    try:
        return {"matches": await io.query(emb.data[0].embedding, 5, flt, min_score=0.5)}
    except Exception as exc:
        raise HTTPException(502, f"vector store error: {exc}")
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.documents import Document              # LangChain document type
from langchain_openai import OpenAIEmbeddings                # embeddings
from langchain_pinecone import PineconeVectorStore            # integration

vs = PineconeVectorStore(index_name="tariff-hs-te3s-v1", embedding=OpenAIEmbeddings(model="text-embedding-3-small"), namespace="headings")
vs.add_documents(                                             # embed + upsert in one call
    [Document(page_content="Headphones, earphones", metadata={"country": "IN"})],
    ids=["8518.30#0"],                                        # stable ids keep it idempotent
)
hits = vs.similarity_search_with_score("wireless earbuds", k=5, filter={"country": "IN"})   # query
# LangGraph: `retrieve` node = the line above; store hits in state["docs"].
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Random UUID ids on every ingestion run
✅ Correct: deterministic ids so re-runs overwrite.

```python
# Wrong: duplicates grow every night
{"id": str(uuid.uuid4()), "values": v}
# Right
{"id": f"{doc_id}#{chunk_no}", "values": v}
```

❌ Mistake 2: Forgetting `include_metadata=True` and then having no text to show the LLM
✅ Correct: request metadata (and keep a short text snippet or id to look up).

```python
# Wrong: matches have id + score only
index.query(vector=q, top_k=5)
# Right
index.query(vector=q, top_k=5, include_metadata=True)
```

---

## 🧠 Tricky Interview Question

**Q**: "You upsert the same document twice with the new text but identical ids, yet some old chunks still appear in results. Why?"

**Answer**: If the new version has fewer chunks than the old one (say 8 instead of 10), ids `#8` and `#9` still exist: upsert only overwrites ids you send. Fix: delete by the document's old ids (or delete by metadata filter `doc_id` on pod indexes; on serverless list ids by prefix and delete them) before or after upserting, or version the ids (`doc#v2#0`) and delete the old version when done. Keep a manifest of ids per document in your own database.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between insert and upsert?
A1: Pinecone has no separate insert: upsert inserts when the id is new and overwrites (values and metadata) when it exists.

Q2: What does `top_k` mean?
A2: The number of nearest results to return. Typical RAG values: 3-10.

Q3: What do scores mean with cosine?
A3: Higher is more similar (about 0 to 1 for typical text embeddings). Use a threshold calibrated on your data rather than a fixed universal number.

Q4: How do you update only metadata?
A4: `index.update(id=..., set_metadata={...}, namespace=...)`. It avoids re-embedding.

Q5: How would you ingest 10 million chunks efficiently and safely?
A5: Stream chunks, embed in batches (OpenAI accepts up to 2048 inputs per request but keep it ~100-500), upsert batches of ~100 with bounded concurrency, exponential backoff with jitter on 429/5xx, stable ids for idempotency, and checkpoints (last successful batch) so a crash resumes instead of restarting. Alternatively use Pinecone's bulk import from object storage for very large loads. Validate with `describe_index_stats()` counts and spot-check queries afterwards.

---

## 🔷 When to Use + When Not to Use
✅ Use upsert/query when:
- Building RAG, semantic search, recommendations
- Keeping the index in sync with changing documents

❌ Avoid when:
- You need transactional multi-row consistency (use Postgres)
- Exact-match lookups by key (use a key-value store)

---

## 📊 Visual Diagram
```
 chunks ─embed─► [ {id, values, metadata}, ... ]
                    │ batches of 100 (concurrency 4, retry/backoff)
                    ▼
              index.upsert(namespace="headings")
                    ...
 question ─embed─► q ─► index.query(top_k=5, filter, include_metadata)
                                │
                                ▼
         matches: [ (8518.30#0, 0.84), (8517.62#1, 0.77), ... ]
                                │ score >= 0.5
                                ▼
                        context text ─► LLM
```

---

## 💰 Cost Impact
- Embedding: 1M chunks x 300 tokens = 300M tokens = $6 with text-embedding-3-small ($0.02 / 1M). Re-embedding only changed docs (stable ids + content hash) can cut this 90%+.
- Pinecone serverless bills write units for upserts (by data size) and read units for queries (scales with namespace size and top_k), so smaller namespaces and lean metadata reduce cost.
- Query token cost: each query embeds ~20 tokens (negligible). The LLM bill depends on how many chunks you pass: top_k=5 x 300 tokens = 1,500 tokens (about $0.000225 on gpt-4o-mini input) versus top_k=20 = 6,000 tokens.
- Optimise: score threshold, `top_k` small, cache frequent queries, batch upserts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Upsert | Insert or overwrite by id | id से डालो या overwrite करो |
| top_k | Number of results returned | लौटाए जाने वाले results की संख्या |
| Score | Similarity value | Similarity का मान |
| Stable id | Deterministic vector id | Deterministic id |
| Batch | Group of vectors per request | एक request में vectors का group |
| Backoff | Increasing wait between retries | Retry के बीच बढ़ता इंतज़ार |
| Idempotent | Same result if repeated | दोहराने पर वही नतीजा |

---

## ⚡ 3-Line Summary
English: Upsert vectors in batches of about 100 with stable ids; query with top_k, filters and include_metadata. Handle retries and stale chunks (delete old ids). Apply a score threshold before sending context to the LLM.
Hindi: Vectors को ~100 के batches में stable ids के साथ upsert करो; top_k, filters और include_metadata के साथ query करो। Retries और पुराने chunks (old ids delete) संभालो। LLM को context भेजने से पहले score threshold लगाओ।

---

## ➡️ Next Topic
**134. Pinecone Metadata Filtering** — restricting search by country, chapter, date and other fields.
