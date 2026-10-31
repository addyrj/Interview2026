---

# 243. Embeddings in LangChain
# हिंदी में: LangChain में Embeddings

---

## 🔵 Simple Definition (English)
LangChain's `Embeddings` interface turns text into vectors with two methods: `embed_documents(list[str])` for many texts and `embed_query(str)` for one query (plus async `aembed_*`). Implementations include `OpenAIEmbeddings`, `HuggingFaceEmbeddings`, `CohereEmbeddings` and more.

## 🔵 सरल परिभाषा (Hindi)
LangChain का `Embeddings` interface text को vectors में बदलता है, दो methods से: कई texts के लिए `embed_documents(list[str])` और एक query के लिए `embed_query(str)` (साथ में async `aembed_*`)। Implementations: `OpenAIEmbeddings`, `HuggingFaceEmbeddings`, `CohereEmbeddings` आदि।

---

## 🔴 Problem it Solves
Semantic search needs vectors, and every provider has a different SDK, batch limit and output size. One interface lets vector stores and retrievers work with any embedding model, and lets you switch models (or run local ones) with one line. It also adds batching and caching helpers.

## 🔴 यह क्यों बना? (Hindi)
Semantic search को vectors चाहिए, और हर provider का SDK, batch limit और vector size अलग है। एक interface से vector stores और retrievers किसी भी embedding model के साथ चलते हैं, और model बदलना (या local चलाना) एक line का काम है। Batching और caching helpers भी मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a model: OpenAIEmbeddings(model="text-embedding-3-small")
Step 2 → Indexing: embed_documents([chunk texts]) -> list[list[float]]
Step 3 → Querying: embed_query("earbuds HS code") -> list[float]
Step 4 → Vector store saves doc vectors; searches with query vector (cosine / dot)
Step 5 → Same model MUST be used for docs and queries
Step 6 → Wrap with CacheBackedEmbeddings to avoid paying twice
Step 7 → Dimensions: text-embedding-3-small=1536 (can shorten with dimensions=)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model चुनो: OpenAIEmbeddings(model="text-embedding-3-small")
Step 2 → Indexing: embed_documents([chunk texts]) -> list[list[float]]
Step 3 → Query: embed_query("earbuds HS code") -> list[float]
Step 4 → Vector store doc vectors रखता है; query vector से search (cosine / dot)
Step 5 → Docs और queries के लिए वही model ज़रूरी
Step 6 → CacheBackedEmbeddings से दोबारा पैसे नहीं लगते
Step 7 → Dimensions: text-embedding-3-small=1536 (dimensions= से घटा सकते हैं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200,000 tariff chunks are embedded once with `text-embedding-3-small` (cost a few dollars). User queries like "Bluetooth earphones" are embedded at request time and matched against chunk vectors. Hindi product names ("ईयरबड्स") work because the model is multilingual. **Zomato**: dish descriptions embedded for "something spicy and light" searches.

## 🟡 Real Example Hindi mein
**Tariff System**: 2,00,000 tariff chunks `text-embedding-3-small` से एक बार embed होते हैं (कुछ dollars)। "Bluetooth earphones" जैसी user query request के समय embed होकर chunk vectors से match होती है। Hindi नाम ("ईयरबड्स") भी चलते हैं क्योंकि model multilingual है।

---

## 💻 Code Example — Basic
```python
# Runs offline: implement the Embeddings interface with a toy hashing embedder, then do similarity search
import math
from langchain_core.embeddings import Embeddings

class ToyEmbeddings(Embeddings):
    """Bag-of-words hashing into 32 dims. Not smart, but shows the interface."""
    def __init__(self, dims: int = 32) -> None:
        self.dims = dims

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.dims  # empty vector
        for w in text.lower().split():
            v[hash(w) % self.dims] += 1.0  # count words into buckets
        n = math.sqrt(sum(x * x for x in v)) or 1.0  # L2 norm
        return [x / n for x in v]  # normalise

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]  # many

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)  # one

emb = ToyEmbeddings()
docs = ["wireless headphones earphones", "leather shoes footwear", "smartphone telephone"]
dv = emb.embed_documents(docs)
qv = emb.embed_query("earphones headphones")
sims = [sum(a * b for a, b in zip(qv, d)) for d in dv]  # cosine (vectors are normalised)
best = max(range(len(docs)), key=sims.__getitem__)
print("best match:", docs[best], round(sims[best], 3))
```

## 💻 Code Example — Advanced
```python
# Production: OpenAI embeddings + disk cache + batching + async + error handling
import asyncio
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore

base = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=768,  # shorter vectors: cheaper storage, small quality drop
    chunk_size=500,  # texts per API request
    max_retries=3,  # built-in retry on transient errors
)
store = LocalFileStore("./emb_cache")  # use Redis/S3 store in prod
cached = CacheBackedEmbeddings.from_bytes_store(
    base, store, namespace=base.model  # namespace prevents mixing models
)

async def embed_all(texts: list[str], batch: int = 256) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        try:
            out.extend(await cached.aembed_documents(part))  # async + cached
        except Exception as exc:  # RateLimitError, network...
            print(f"batch {i} failed: {exc}; retrying slowly")
            await asyncio.sleep(2)
            out.extend(await cached.aembed_documents(part))  # one more try, then raise
    return out

async def embed_query(q: str) -> list[float]:
    return await cached.aembed_query(q.strip())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextsIn(BaseModel):
    texts: list[str]

@app.post("/embed")
async def embed(body: TextsIn) -> dict:
    if len(body.texts) > 100:
        return {"error": "max 100 texts per call"}  # protect cost
    vecs = await embed_all(body.texts)
    return {"count": len(vecs), "dims": len(vecs[0]) if vecs else 0}
```

---

## 🔗 LangChain / LangGraph Connection
Vector stores accept an `Embeddings` object (`Chroma(embedding_function=emb)`, `FAISS.from_documents(docs, emb)`) and call `embed_documents` on add and `embed_query` on search. Semantic splitters, `EmbeddingsFilter` in compression retrievers, and semantic caches also use it. In LangGraph, LangGraph's own `Store` can index with embeddings for long-term memory search.

```python
# vs = FAISS.from_documents(chunks, cached); retriever = vs.as_retriever(search_kwargs={"k": 5})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Different models for indexing and querying
```python
# Wrong: index with text-embedding-3-small, query with text-embedding-ada-002 -> garbage similarity
# Right: one model for both; store model name in index metadata; re-embed everything when changing
```

❌ Mistake 2: Re-embedding unchanged text every run
```python
# Wrong: FAISS.from_documents(all_chunks, emb)   # pays again each deployment
# Right: CacheBackedEmbeddings or RecordManager indexing to embed only new/changed chunks
```

---

## 🧠 Tricky Interview Question
**Q**: "You switch from text-embedding-3-small to a better model and retrieval gets worse. Why?"

**Answer**: Old vectors in the index belong to a different vector space; mixing is meaningless. After switching you must re-embed the entire corpus (or build a new index). Also check dimension mismatch, normalisation, and whether the new model needs query/passage prefixes (e.g., E5/BGE instructions). Evaluate with a golden set before and after.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `embed_documents` and `embed_query`? (Easy)
A1: documents: batch of corpus texts; query: one search text. Some models (E5, BGE) add different prefixes for each.

Q2: What does cosine similarity measure? (Easy)
A2: The angle between vectors; closeness in meaning independent of length.

Q3: How to cut embedding cost? (Medium)
A3: Cache, dedupe, chunk wisely, use small model, shorten dimensions, batch API for bulk (50 percent off), skip unchanged docs.

Q4: Open-source vs API embeddings? (Medium)
A4: API: easy, high quality, per-token cost, data leaves your system. Open-source (BGE, E5 via `HuggingFaceEmbeddings`): no per-token fee, private, needs GPU/CPU ops and tuning.

Q5: How to handle multilingual tariff queries (Hindi/English)? (Hard)
A5: Use multilingual embeddings (text-embedding-3, multilingual-e5, BGE-M3), test cross-lingual recall on labelled pairs, optionally translate queries to English, store language metadata, and evaluate separately per language since token counts and recall differ.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Semantic search, RAG, dedupe, clustering, classification by similarity

❌ Avoid when:
- Exact lookups (IDs, HS code strings): use keyword/BM25 or SQL

---

## 📊 Visual Diagram
```
 "Bluetooth earbuds" ─► embed_query ─► [0.12, -0.5, ... 1536 dims]
                                              │ cosine similarity
 chunk texts ─► embed_documents ─► vectors ─► Vector store ─► top-k chunks
 (same model for both!)
```

---

## 💰 Cost Impact
Embeddings are billed on input tokens only. text-embedding-3-small costs about $0.02 per 1M tokens: embedding 100M tokens of tariff text is about $2, one-time. text-embedding-3-large is roughly 6.5x more. Query embeddings are tiny per request but add up at scale. Optimise: caching, dedupe, small model, `dimensions=` for storage, batch API for bulk jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector of meaning | अर्थ का vector |
| embed_query | Embed one query | एक query का vector |
| Cosine similarity | Angle-based closeness | कोण से समानता |
| Dimensions | Vector length | Vector की लंबाई |
| CacheBackedEmbeddings | Cache wrapper | Cache वाला wrapper |

---

## ⚡ 3-Line Summary
English: The Embeddings interface (`embed_documents`, `embed_query`) lets any model plug into LangChain vector stores. Use the same model for indexing and querying, and cache to save cost. Switching models means re-embedding everything.
Hindi: Embeddings interface (`embed_documents`, `embed_query`) से कोई भी model LangChain vector stores में लगता है। Indexing और query में वही model लो और cache से cost बचाओ। Model बदलने पर सब दोबारा embed करना पड़ता है।

---

## ➡️ Next Topic
**244. Vector Stores in LangChain** — storing and searching these vectors.
