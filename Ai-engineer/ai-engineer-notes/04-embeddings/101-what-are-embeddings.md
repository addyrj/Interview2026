---

# 101. What are Embeddings
# हिंदी में: Embeddings क्या हैं

---

## 🔵 Simple Definition (English)
An embedding is a dense vector of floating-point numbers that represents the **meaning** of text in high-dimensional space. Similar meanings → vectors that are close together. "iPhone" and "smartphone" have similar embeddings. "iPhone" and "potato" have very different embeddings. This "meaning as a number" representation is what powers semantic search, RAG, and recommendation systems.

## 🔵 सरल परिभाषा (Hindi)
Embedding floating-point numbers का dense vector है जो text की **meaning** को high-dimensional space में represent करता है। Similar meanings → close vectors। "iPhone" और "smartphone" close embeddings। "iPhone" और "potato" बहुत different। "Meaning as numbers" = semantic search, RAG, recommendations।

---

## 🔴 Problem it Solves
Traditional search: keyword matching — "HS code for mobile phone" won't find documents that say "smartphone tariff" (different words, same meaning). Embeddings capture semantic similarity — "mobile phone" and "smartphone" are near each other in vector space, so semantic search finds both. This is the foundation of RAG systems.

## 🔴 यह क्यों बना? (Hindi)
Traditional keyword search: "mobile phone HS code" search करो → "smartphone tariff" वाला document नहीं मिलेगा (same meaning, different words)। Embeddings semantic similarity capture करते हैं — "mobile phone" और "smartphone" vector space में close हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Text → Embedding model (trained neural network)
Step 2 → Model runs the text through multiple transformer layers
Step 3 → Final layer output = dense vector [0.231, -0.872, 0.154, ...]
Step 4 → Vector has fixed dimensions (1536 for text-embedding-3-small)
Step 5 → Store vector in vector database (Pinecone, pgvector, etc.)
Step 6 → At query time: embed the query → compare to stored vectors
Step 7 → Similarity metric (cosine similarity) → top-k most similar vectors
Step 8 → Return original text chunks corresponding to similar vectors
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Text → Embedding model (trained neural network)
Step 2 → Multiple transformer layers से pass
Step 3 → Final output = dense vector [0.231, -0.872, ...]
Step 4 → Fixed dimensions (1536 for text-embedding-3-small)
Step 5 → Vector database में store (Pinecone, pgvector)
Step 6 → Query time: query embed करो → stored vectors से compare
Step 7 → Cosine similarity → top-k most similar
Step 8 → Similar vectors के original text chunks return करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tariff PDFs contain "Chapter 85: Electrical machinery and equipment." User asks "HS code for smartphone." The word "smartphone" never appears in Chapter 85 — but the embedding of "smartphone" is close to "mobile telephone" (which does appear). Semantic search finds the right chapter. Keyword search would miss it.

## 🟡 Real Example Hindi mein
**Tariff System**: PDF में "Chapter 85: Electrical machinery" है। User "smartphone" पूछता है — PDF में "smartphone" नहीं है, "mobile telephone" है। Embedding से "smartphone" और "mobile telephone" close निकलते हैं → सही chapter मिलता है। Keyword search miss कर देती।

---

## 💻 Code Example — Basic
```python
# Getting embeddings from OpenAI
from openai import AsyncOpenAI
import numpy as np

client = AsyncOpenAI()

async def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Get embedding vector for a single text."""
    # Always normalize text: strip whitespace, newlines
    text = text.replace("\n", " ").strip()

    response = await client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding   # list of 1536 floats for text-embedding-3-small

# Compute cosine similarity:
def cosine_similarity(a: list[float], b: list[float]) -> float:
    """1.0 = identical meaning, 0.0 = unrelated, -1.0 = opposite."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

import asyncio

async def demo():
    # Embed three texts:
    e1 = await get_embedding("smartphone")
    e2 = await get_embedding("mobile phone")
    e3 = await get_embedding("potato")

    print(f"smartphone vs mobile phone: {cosine_similarity(e1, e2):.4f}")  # ~0.92 high!
    print(f"smartphone vs potato:        {cosine_similarity(e1, e3):.4f}")  # ~0.15 low
    print(f"Vector dimensions: {len(e1)}")   # 1536

asyncio.run(demo())
```

## 💻 Code Example — Advanced
```python
# Production: batch embedding with caching and retry
from openai import AsyncOpenAI
from pydantic import BaseModel
import asyncio
import hashlib
import json
import redis.asyncio as aioredis
from typing import Optional

client = AsyncOpenAI()

class EmbeddingService:
    """Production embedding service with Redis caching and batch processing."""

    def __init__(self, redis_url: str = "redis://localhost", model: str = "text-embedding-3-small"):
        self.model = model
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.dimensions = 1536   # text-embedding-3-small dimensions

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)

    def _cache_key(self, text: str) -> str:
        """Deterministic cache key from text content."""
        return f"emb:{self.model}:{hashlib.sha256(text.encode()).hexdigest()}"

    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding with Redis caching."""
        text = text.replace("\n", " ").strip()
        cache_key = self._cache_key(text)

        # Try cache first:
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)   # cache hit — no API cost!

        # Cache miss → call API:
        response = await client.embeddings.create(model=self.model, input=text)
        embedding = response.data[0].embedding

        # Store in cache (TTL: 30 days — embeddings don't change):
        if self.redis:
            await self.redis.setex(cache_key, 30 * 86400, json.dumps(embedding))

        return embedding

    async def batch_embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Embed many texts efficiently — OpenAI supports up to 2048 inputs per call."""
        all_embeddings: list[list[float]] = []

        # Check cache for all texts first:
        uncached: list[tuple[int, str]] = []
        results: dict[int, list[float]] = {}

        for i, text in enumerate(texts):
            text = text.replace("\n", " ").strip()
            cache_key = self._cache_key(text)
            if self.redis:
                cached = await self.redis.get(cache_key)
                if cached:
                    results[i] = json.loads(cached)
                    continue
            uncached.append((i, text))

        # Batch API calls for uncached texts:
        for batch_start in range(0, len(uncached), batch_size):
            batch = uncached[batch_start:batch_start + batch_size]
            indices = [item[0] for item in batch]
            texts_batch = [item[1] for item in batch]

            response = await client.embeddings.create(model=self.model, input=texts_batch)

            for j, emb_data in enumerate(response.data):
                idx = indices[j]
                embedding = emb_data.embedding
                results[idx] = embedding

                # Cache the result:
                if self.redis:
                    cache_key = self._cache_key(texts_batch[j])
                    await self.redis.setex(cache_key, 30 * 86400, json.dumps(embedding))

        return [results[i] for i in range(len(texts))]

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        import numpy as np
        a_np, b_np = np.array(a), np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

# Cost: text-embedding-3-small = $0.02 / 1M tokens
# Tariff doc (10K chunks × 200 tokens avg = 2M tokens) → $0.04 one-time cost to index!
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import numpy as np

app = FastAPI()
client = AsyncOpenAI()

class EmbedRequest(BaseModel):
    texts: list[str]               # batch embedding
    model: str = "text-embedding-3-small"

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

@app.post("/embed")
async def embed_texts(request: EmbedRequest):
    """Batch embed texts and return vectors."""
    if len(request.texts) > 100:
        raise HTTPException(status_code=400, detail="Max 100 texts per batch")

    response = await client.embeddings.create(
        model=request.model,
        input=[t.replace("\n", " ").strip() for t in request.texts],
    )
    return {
        "embeddings": [item.embedding for item in response.data],
        "dimensions": len(response.data[0].embedding),
        "tokens_used": response.usage.total_tokens,
        "cost_usd": round(response.usage.total_tokens * 0.02 / 1_000_000, 8),
    }

@app.post("/similarity")
async def compute_similarity(request: SimilarityRequest):
    """Compute semantic similarity between two texts."""
    embeddings = await client.embeddings.create(
        model="text-embedding-3-small",
        input=[request.text1, request.text2],
    )
    e1, e2 = [item.embedding for item in embeddings.data]
    a, b = np.array(e1), np.array(e2)
    sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return {
        "similarity": round(sim, 4),
        "interpretation": "very similar" if sim > 0.9 else "related" if sim > 0.7 else "unrelated",
    }
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain wraps embedding models:
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Single text:
vector = await embeddings.aembed_query("smartphone HS code")

# Batch (for indexing documents):
vectors = await embeddings.aembed_documents([
    "Chapter 85: Electrical machinery",
    "HS code 8517: Telephone sets including smartphones",
    "Chapter 61: Clothing and accessories",
])

# LangGraph: embeddings are used in the RAG retrieval node
# State["query"] → embed → vector search → State["context"]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling API for each document individually (expensive + slow)
```python
# Wrong — 1000 documents = 1000 API calls:
for doc in documents:
    embedding = await get_embedding(doc)   # 1000 separate calls!

# Correct — batch them (up to 2048 per call):
response = await client.embeddings.create(
    model="text-embedding-3-small",
    input=documents[:100],    # 100 docs per batch (safe limit)
)
embeddings = [item.embedding for item in response.data]
```

❌ Mistake 2: Not normalizing text before embedding
```python
# Wrong — whitespace, newlines, case affect embeddings slightly:
embedding = await get_embedding(text)   # text may have "\n\n\n" from PDF

# Correct — normalize first:
text = " ".join(text.split())   # collapse whitespace
text = text[:8191]              # stay within token limit
embedding = await get_embedding(text)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your tariff search works great for English queries, but Hindi queries return wrong results even though the documents are also in Hindi. What's wrong?"

**Answer**: The embedding model choice. `text-embedding-3-small` is primarily trained on English — it creates much weaker semantic representations for Hindi. The vectors for Hindi words don't cluster meaningfully. Solutions: (1) Use `multilingual-e5-large` (Hugging Face) — specifically trained on 100+ languages for cross-lingual similarity. (2) Use `text-embedding-3-large` which has better multilingual coverage. (3) Translate Hindi queries to English before embedding (extra latency). (4) For production multilingual apps, benchmark embedding models with your actual data before choosing.

---

## ⚫ Interview Questions + Answers

Q1: What dimensions are used for OpenAI embeddings and can you change them?
A1: `text-embedding-3-small`: 1536 dimensions (default) or smaller via `dimensions` parameter (min 256). `text-embedding-3-large`: 3072 dimensions. Smaller dimensions = faster search, less storage, slightly lower quality. The `dimensions` parameter truncates the vector using Matryoshka Representation Learning — a special training technique where shorter prefixes of the full vector remain semantically meaningful.

Q2: What is cosine similarity and why is it preferred over Euclidean distance for embeddings?
A2: Cosine similarity measures the angle between two vectors — range [-1, 1]. It's length-invariant — a short document and a long document with the same meaning have similar cosine similarity. Euclidean distance is magnitude-sensitive — longer documents generate larger vectors, so distance is biased. For embeddings that may come from documents of varying lengths, cosine similarity is more reliable.

Q3: What is the difference between `embed_query` and `embed_documents` in LangChain?
A3: For some embedding models (like E5, BGE), the document and query are prefixed differently — "passage: " for documents, "query: " for queries — to optimize retrieval. LangChain's `embed_query` and `embed_documents` handle this automatically. For OpenAI, the same prefix is used for both, so the methods behave identically. Always use the right method to ensure optimal retrieval performance with asymmetric models.

Q4: What is embedding drift and why does it matter in production?
A4: Embedding drift occurs when OpenAI (or another provider) updates their embedding model — the new model produces different vectors for the same text. If you update your embedding model without re-indexing all your documents, your queries (embedded with the new model) won't match your indexed documents (embedded with the old model) — search quality degrades silently. Solution: version your embeddings, test new models before switching, re-index all documents when changing models.

Q5: How would you embed 10 million tariff document chunks efficiently and cost-effectively?
A5: (1) Use OpenAI Batch API — 50% cheaper than real-time API, rate limit much higher. (2) Process in parallel — `asyncio.gather` with multiple batch requests. (3) Use `text-embedding-3-small` not `large` — 5x cheaper, nearly same quality for retrieval. (4) Deduplicate before embedding — many tariff docs repeat the same regulations. (5) Cache embeddings in Redis — identical text chunks won't need re-embedding. Estimate: 10M chunks × 200 tokens = 2B tokens × $0.02/1M = **$40 total** for small model.

---

## 🔷 When to Use + When Not to Use

✅ Use embeddings when:
- Semantic search (find similar meaning, not just keywords)
- RAG pipeline (embed documents + queries)
- Clustering similar content
- Recommendation systems ("find similar products")
- Duplicate detection (near-duplicate documents)

❌ Don't use embeddings for:
- Exact keyword search — use BM25/Elasticsearch
- Lookup by ID — use a regular database
- Structured queries (`price > 100`) — use SQL
- Real-time search with very low latency (< 10ms) — embedding lookup adds overhead

---

## 📊 Visual Diagram
```
Vector Space (simplified to 2D):

           "mobile phone" ×
           "smartphone"   ×     ← close together
           "iPhone"       ×

                              "automobile" ×

"potato"  ×        "vegetable" ×

───────────────────────────────────────────
Query: "cell phone HS code"
    │
    ▼
Embed: [0.23, -0.87, 0.14, ...]  (1536 dims)
    │
    ▼
Cosine similarity vs all stored vectors
    │
    ▼
Top matches:
  0.94 → "smartphone tariff Chapter 85"
  0.91 → "mobile telephone HS 8517"
  0.88 → "wireless communication devices"
```

---

## 💰 Cost Impact
| Model | Dimensions | Price/1M tokens | 10M chunks × 200 tokens |
|-------|------------|-----------------|------------------------|
| text-embedding-3-small | 1536 | $0.020 | $40 |
| text-embedding-3-large | 3072 | $0.130 | $260 |
| ada-002 (old) | 1536 | $0.100 | $200 |

**Recommendation**: `text-embedding-3-small` — 6.5x cheaper than `large`, competitive quality for most retrieval tasks. Use `large` only if benchmarks show significant quality improvement for your specific use case.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Dense vector representing text meaning | Text की meaning को vector में बदलना |
| Vector space | Multi-dimensional space where vectors live | High-dimensional mathematical space |
| Cosine similarity | Angle-based similarity measure | Angle-based similarity (0-1) |
| Dimensions | Size of the embedding vector | Vector कितना बड़ा है |
| Semantic search | Meaning-based (not keyword) search | Meaning से search |
| Vector database | DB storing and searching vectors | Vectors store + search करने वाला DB |
| Batch embedding | Embed multiple texts in one API call | एक call में multiple texts embed करो |

---

## ⚡ 3-Line Summary
English: Embeddings convert text meaning into dense vectors — similar meanings are close in vector space, enabling semantic search that finds "smartphone" when you have "mobile telephone" in your documents. Use `text-embedding-3-small` (cheapest, good quality) and always batch your API calls. For RAG: embed all document chunks at indexing time, embed queries at search time, retrieve top-k by cosine similarity.
Hindi: Embeddings text की meaning को vectors में convert करते हैं — similar meanings close होते हैं। Semantic search "smartphone" query से "mobile telephone" document ढूंढ सकती है। `text-embedding-3-small` use करो (सस्ता), batch calls करो, RAG में documents index time पर और queries search time पर embed करो।

---

## ➡️ Next Topic
**102. Why Embeddings Work** — mathematical intuition, why neural networks produce meaningful geometry, what dimensions capture.
