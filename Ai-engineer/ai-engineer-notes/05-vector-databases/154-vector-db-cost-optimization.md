---

# 154. Vector DB Cost Optimization
# हिंदी में: Vector DB Cost Optimization

---

## 🔵 Simple Definition (English)
Vector DB cost comes from storage and RAM (vectors x dimension x bytes plus index), compute for queries, embedding API tokens and the LLM tokens that retrieved chunks create. Optimisation reduces each: smaller vectors, quantization, fewer and better chunks, caching and tiering.

## 🔵 सरल परिभाषा (Hindi)
Vector DB की cost storage और RAM (vectors x dimension x bytes + index), queries के compute, embedding API tokens, और retrieved chunks से बनने वाले LLM tokens से आती है। Optimisation हर एक को घटाता है: छोटे vectors, quantization, कम और बेहतर chunks, caching और tiering।

---

## 🔴 Problem it Solves
A prototype costs nothing; at 50M vectors of 3072 dims the RAM alone is about 600 GB. Bills grow silently: duplicate chunks, stale data, oversized dimensions and re-embedding the same text again and again.

## 🔴 यह क्यों बना? (Hindi)
Prototype की cost लगभग शून्य होती है; 5 करोड़ vectors x 3072 dims पर सिर्फ़ RAM लगभग 600 GB होती है। Bill चुपचाप बढ़ता है: duplicate chunks, पुराना data, ज़रूरत से बड़े dimensions और एक ही text को बार-बार embed करना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: GB per million vectors, monthly infra, embedding tokens, LLM tokens per query
Step 2 → Remove waste: dedupe chunks (hash), delete stale versions, TTL old data
Step 3 → Shrink vectors: lower dimensions (text-embedding-3 "dimensions"), float16/int8/binary quantization
Step 4 → Avoid re-embedding: store content_hash; embed only changed chunks; cache query embeddings
Step 5 → Tier data: hot (RAM/HNSW) vs cold (disk or object storage, exact scan on demand)
Step 6 → Cut LLM tokens: smaller k, score threshold, rerank then trim, cache answers
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → नापो: प्रति मिलियन vectors GB, मासिक infra, embedding tokens, प्रति query LLM tokens
Step 2 → बर्बादी हटाओ: chunks dedupe (hash), पुराने versions delete, पुराने data पर TTL
Step 3 → Vectors छोटे करो: कम dimensions (text-embedding-3 "dimensions"), float16/int8/binary quantization
Step 4 → दोबारा embed मत करो: content_hash रखो; सिर्फ़ बदले chunks embed करो; query embeddings cache करो
Step 5 → Data tier करो: hot (RAM/HNSW) बनाम cold (disk या object storage)
Step 6 → LLM tokens घटाओ: छोटा k, score threshold, rerank फिर trim, answers cache करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: the first design embedded every PDF page at 3072 dims. Changes: 1024 dims (via `dimensions`), content-hash dedupe (the same legal note repeats in many documents; 30 percent removed), and re-embedding only changed pages on each yearly tariff update. Storage dropped by roughly 70 percent and ingestion cost by a similar amount.

**Amazon-style**: product images and titles embedded at 768 dims with int8 quantization; only the top 100 candidates are rescored using full-precision vectors.

## 🟡 Real Example Hindi mein
**Tariff System**: पहले design में हर PDF page 3072 dims पर embed होता था। बदलाव: 1024 dims (`dimensions` से), content-hash से dedupe (एक ही legal note कई documents में दोहराता है; 30% हटे), और हर साल tariff update में सिर्फ़ बदले pages दोबारा embed। Storage लगभग 70% और ingestion cost भी इसी के आसपास घटी।

**Amazon-style**: product images और titles 768 dims पर int8 quantization के साथ; सिर्फ़ top 100 candidates को full-precision vectors से दोबारा score करते हैं।

---

## 💻 Code Example — Basic
```python
# Runs offline: storage calculator + savings from dimension/quantization choices
def storage_gb(vectors: int, dims: int, bytes_per_value: float, index_overhead: float = 0.2) -> float:
    """Approximate RAM/disk for vectors plus ANN index overhead (graph links)."""
    raw = vectors * dims * bytes_per_value  # raw vector bytes
    return raw * (1 + index_overhead) / 1024 ** 3  # add overhead, convert to GB


N = 10_000_000  # ten million chunks
options = {
    "3072d float32": (3072, 4),
    "1536d float32": (1536, 4),
    "1024d float32": (1024, 4),
    "1024d int8   ": (1024, 1),
    "1024d binary ": (1024, 1 / 8),
}
base = storage_gb(N, 3072, 4)  # baseline for comparison
for name, (d, b) in options.items():
    gb = storage_gb(N, d, b)
    print(f"{name}: {gb:8.1f} GB  ({gb / base * 100:5.1f}% of baseline)")
# Always re-check recall: quantization usually needs rescoring with full vectors.
```

## 💻 Code Example — Advanced
```python
# Production: skip re-embedding unchanged chunks (content hash) + embedding cache, async
import hashlib
import logging
from typing import Awaitable, Callable

log = logging.getLogger("cost")


def content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()  # stable identity of the text


class IncrementalEmbedder:
    """Embeds only chunks whose text is new or changed."""

    def __init__(self, embed_batch: Callable[[list[str]], Awaitable[list[list[float]]]],
                 known_hashes: dict[str, str], batch_size: int = 100) -> None:
        self.embed_batch = embed_batch  # async function: texts -> vectors
        self.known = known_hashes  # chunk_id -> hash already stored in the DB
        self.batch_size = batch_size

    async def run(self, chunks: dict[str, str]) -> dict[str, list[float]]:
        """chunks: chunk_id -> text. Returns vectors only for items that changed."""
        todo = [(cid, t) for cid, t in chunks.items() if self.known.get(cid) != content_hash(t)]
        skipped = len(chunks) - len(todo)
        log.info("embedding %d chunks, skipped %d unchanged", len(todo), skipped)
        out: dict[str, list[float]] = {}
        for i in range(0, len(todo), self.batch_size):  # batches reduce overhead
            part = todo[i:i + self.batch_size]
            try:
                vecs = await self.embed_batch([t for _, t in part])
            except Exception:
                log.exception("batch %d failed", i // self.batch_size)  # keep going, retry later
                continue
            for (cid, t), v in zip(part, vecs):
                out[cid] = v
                self.known[cid] = content_hash(t)  # remember to skip next time
        return out


# Usage sketch:
# async def embed_batch(texts): r = await client.embeddings.create(model="text-embedding-3-small",
#                                      input=texts, dimensions=1024); return [d.embedding for d in r.data]
```

---

## 🟠 FastAPI Integration
```python
from functools import lru_cache
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
_embed_cache: dict[str, list[float]] = {}  # simple in-process cache (use Redis for multi-worker)


async def cached_embedding(text: str) -> list[float]:
    key = text.strip().lower()  # normalise so near-identical queries share an entry
    if key not in _embed_cache:
        # _embed_cache[key] = (await oa.embeddings.create(...)).data[0].embedding
        _embed_cache[key] = [0.0]  # placeholder so the sketch runs
    return _embed_cache[key]


class Q(BaseModel):
    text: str


@app.post("/tariff/search")
async def search(q: Q) -> dict:
    vec = await cached_embedding(q.text)  # repeated questions cost zero embedding tokens
    return {"dims": len(vec), "cache_size": len(_embed_cache)}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Cache embeddings on disk so unchanged chunks are never paid for twice
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings

base = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1024)  # smaller vectors
store = LocalFileStore("./emb_cache")  # persistent key-value store
cached = CacheBackedEmbeddings.from_bytes_store(base, store, namespace=base.model)  # namespace avoids model mix-ups
# Use `cached` in any vector store; re-running ingestion hits the cache instead of the API.
# LangChain's RecordManager (indexing API) also skips unchanged documents and deletes stale ones.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-embedding the whole corpus on every deploy
```python
# Wrong
for doc in all_docs:
    embed(doc)          # pays full cost every run
# Right
if known_hash.get(doc.id) != content_hash(doc.text):
    embed(doc)          # only changed text
```

❌ Mistake 2: Mixing embedding models or dimensions in one index
```python
# Wrong: half the rows from text-embedding-3-small, half from a new model (different space)
# Right: store model name + version with each vector; migrate to a NEW index and switch over
```

---

## 🧠 Tricky Interview Question

**Q**: "You cut vector storage 8x with binary quantization and search got much faster, yet answer quality dropped. How do you keep the savings?"

**Answer**: Binary or int8 codes lose precision, so ranking is noisier. Use two-stage retrieval: search the compact index for a wide candidate set (for example top 100 with `oversampling`), then rescore those candidates with the original full-precision vectors (kept on cheap disk) and return the top k. This usually recovers most recall while memory stays small. Also validate on labelled queries, and consider a modest reduction (int8, or fewer dimensions) rather than binary if the data is subtle.

---

## ⚫ Interview Questions + Answers

Q1: What drives vector storage size?
A1: Number of vectors x dimensions x bytes per value, plus index overhead.

Q2: How can you reduce dimensions?
A2: `text-embedding-3-*` models accept a `dimensions` parameter that returns a shortened embedding with modest quality loss. Other options are PCA or Matryoshka-trained models.

Q3: Why store a content hash?
A3: To detect unchanged chunks and skip embedding them again, saving API cost.

Q4: What is quantization?
A4: Storing numbers with fewer bits (float16, int8, binary) to reduce memory and speed up distance computation, usually with some recall loss.

Q5: Give a full cost-reduction plan for a RAG system.
A5: Dedupe and clean content; chunk sensibly; reduce dimensions or quantize with rescoring; incremental embedding by hash; cache query embeddings and final answers; set k and score threshold to limit LLM tokens; route simple queries to a cheaper LLM; tier cold data; monitor cost per query and recall together so savings never silently hurt quality.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bills grow with data, or storage is the largest line item
- You re-ingest frequently

❌ Avoid when:
- Dataset is small (under 100K vectors) where engineering time costs more than the savings
- Accuracy is regulated and you cannot afford any recall loss (validate first)

---

## 📊 Visual Diagram
```
 10M vectors, RAM (approx, with 20% index overhead)

 3072d float32 ████████████████████████████████ 137 GB
 1536d float32 ████████████████                  69 GB
 1024d float32 ███████████                       46 GB
 1024d int8    ███                               11 GB
 1024d binary  █                                  1.4 GB

 Query path: compact index (top 100) ──► rescore with full vectors ──► top 5 ──► LLM
```

---

## 💰 Cost Impact
- Embedding tokens: one-time per chunk plus tiny per query. Hash-based incremental ingestion avoids paying again for unchanged text. Check current embedding prices; they are low per 1M tokens but add up for large corpora.
- LLM tokens usually dominate: 5 chunks x 300 tokens = 1,500 input tokens per question. Dropping to 3 well-ranked chunks saves about 600 tokens per request, which at 100K requests per day is 60M tokens per day.
- Infra: RAM is the main driver, so quantization and lower dimensions give the biggest savings; caching reduces compute.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Quantization | Fewer bits per value | कम bits में संख्याएँ |
| Rescoring | Re-rank candidates with full vectors | Full vectors से दोबारा score |
| Content hash | Fingerprint of text | Text की पहचान |
| Tiering | Hot vs cold storage | Hot/cold storage |
| Dimension | Length of a vector | Vector की लंबाई |
| TTL | Auto-expiry time | अपने आप हटने का समय |

---

## ⚡ 3-Line Summary
English: Vector cost = storage/RAM + compute + embedding tokens + LLM tokens. Reduce dimensions, quantize with rescoring, dedupe, embed incrementally and cache. Always monitor recall and cost together.
Hindi: Vector cost = storage/RAM + compute + embedding tokens + LLM tokens। Dimensions घटाओ, rescoring के साथ quantize करो, dedupe करो, incremental embed करो और cache करो। Recall और cost दोनों साथ मॉनिटर करो।

---

## ➡️ Next Topic
**155. Vector DB Best Practices** — a production checklist: schema, ids, metadata, versioning, security, backups.
