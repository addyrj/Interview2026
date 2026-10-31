---

# 125. Embedding Best Practices
# हिंदी में: Embedding Best Practices (embeddings का सही तरीका)

---

## 🔵 Simple Definition (English)
Embedding best practices are the proven rules for producing good vectors: pick the right model, clean and chunk text well, normalise vectors, batch and cache calls, version the model, and measure retrieval quality. Following them prevents the most common silent RAG failures.

## 🔵 सरल परिभाषा (Hindi)
Embedding best practices वो सिद्ध नियम हैं जिनसे अच्छे vectors बनते हैं: सही model चुनो, text को साफ़ करके सही chunk करो, vectors normalise करो, calls को batch और cache करो, model version रखो और retrieval quality measure करो। इनसे RAG की चुपचाप होने वाली गलतियाँ रुकती हैं।

---

## 🔴 Problem it Solves
Most RAG bugs are not LLM bugs, they are embedding bugs: chunks too big (topic diluted), mixed models in one index, un-normalised vectors with dot-product metric, re-embedding unchanged documents (wasted money), no evaluation (nobody knows quality). A checklist makes the retriever reliable and cheap.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर RAG bugs LLM के नहीं, embedding के होते हैं: बहुत बड़े chunks, एक index में अलग-अलग models, बिना normalise किए vectors, unchanged documents को बार-बार embed करना (पैसा बर्बाद), और evaluation न होना। Checklist से retriever भरोसेमंद और सस्ता बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose model by language, domain, dimension, cost (test 2-3 on YOUR data)
Step 2 → Clean text (strip HTML/boilerplate, keep headings as context)
Step 3 → Chunk: ~200-500 tokens, 10-15% overlap, split on structure (sections/paragraphs)
Step 4 → Embed in batches (e.g. 100-500 texts per call) with retry + backoff
Step 5 → Cache by content hash so unchanged text is never re-embedded
Step 6 → Normalise to unit length; use cosine (or dot product on normalised vectors)
Step 7 → Store model name + version + chunk metadata with every vector
Step 8 → Evaluate Recall@k / MRR on a golden set; re-run on every change
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → भाषा, domain, dimension, cost देखकर model चुनो (अपने data पर 2-3 test करो)
Step 2 → Text साफ़ करो (HTML/boilerplate हटाओ, headings रखो)
Step 3 → Chunk: ~200-500 tokens, 10-15% overlap, sections/paragraphs पर split
Step 4 → Batches में embed करो, retry + backoff के साथ
Step 5 → Content hash से cache करो ताकि unchanged text दोबारा embed न हो
Step 6 → Unit length पर normalise करो, cosine use करो
Step 7 → हर vector के साथ model name + version + metadata रखो
Step 8 → Golden set पर Recall@k / MRR measure करो, हर बदलाव पर दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 40,000 tariff lines are re-ingested every week, but only ~3% change. A content-hash cache means we embed 1,200 lines instead of 40,000, saving 97% of the embedding bill. Each vector stores `{"model": "text-embedding-3-small", "chapter": 85, "hs": "8517.13"}` so we can filter by chapter and safely migrate models later.

**Amazon-style product search**: embed `title + brand + category` as one string (not title alone), and keep price/stock out of the embedded text (they change often and belong in metadata filters).

## 🟡 Real Example Hindi mein
**Tariff System**: 40,000 tariff lines हर हफ्ते आते हैं पर सिर्फ ~3% बदलती हैं। Content-hash cache से हम 40,000 की जगह 1,200 lines embed करते हैं, यानी 97% बचत। हर vector में model, chapter, HS code metadata है। **Amazon-style search**: `title + brand + category` साथ embed करो, price/stock को metadata में रखो।

---

## 💻 Code Example — Basic
```python
# Basic: chunking + normalising + hash cache, pure Python, runs offline
import hashlib                                   # for content hashing
import math                                      # for vector length
from typing import Dict, List                    # type hints

def chunk_words(text: str, size: int = 50, overlap: int = 8) -> List[str]:
    """Split text into word chunks with overlap."""
    words = text.split()                         # split on whitespace
    if size <= overlap:                          # invalid config guard
        raise ValueError("size must be larger than overlap")
    step = size - overlap                        # how far the window moves
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words), 1), step)]  # windows

def normalize(vec: List[float]) -> List[float]:
    """Scale a vector to length 1 so dot product == cosine."""
    length = math.sqrt(sum(x * x for x in vec))  # L2 norm
    return vec if length == 0 else [x / length for x in vec]  # avoid divide-by-zero

cache: Dict[str, List[float]] = {}               # content-hash -> vector
calls = 0                                        # counts "paid" embedding calls

def fake_embed(text: str) -> List[float]:
    """Stand-in for a real embedding API (deterministic, offline)."""
    global calls                                 # we modify the module counter
    calls += 1                                   # one paid call
    return [len(text) % 7 + 1.0, text.count("a") + 1.0, text.count("e") + 1.0]  # toy 3-D vector

def embed_cached(text: str) -> List[float]:
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()  # stable key from content
    if key not in cache:                         # only embed unseen text
        cache[key] = normalize(fake_embed(text)) # embed + normalise + store
    return cache[key]                            # cached vector

chunks = chunk_words("static converters other than ... " * 20, size=10, overlap=2)  # make chunks
for c in chunks + chunks:                        # run twice: second pass is all cache hits
    embed_cached(c)                              # embed (or hit cache)
print("chunks:", len(chunks), "paid calls:", calls)   # calls == unique chunks only
```

## 💻 Code Example — Advanced
```python
# Advanced: batched, cached, retrying, async embedding service (openai>=1)
import asyncio                                         # async runtime
import hashlib                                         # content hash keys
import logging                                         # logs
import random                                          # jitter for backoff
from typing import Dict, List, Optional                # type hints

from openai import APIError, AsyncOpenAI, RateLimitError  # SDK + error classes

log = logging.getLogger("embedder")                    # logger
MODEL = "text-embedding-3-small"                       # 1536 dims, $0.02 / 1M tokens
BATCH = 100                                            # texts per API call

class Embedder:
    """Batching + caching + retry wrapper around the embeddings API."""

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self.client = client or AsyncOpenAI()          # reads OPENAI_API_KEY from env
        self.cache: Dict[str, List[float]] = {}        # swap for Redis in production

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(f"{MODEL}:{text}".encode()).hexdigest()  # model is part of key

    async def _call(self, batch: List[str], retries: int = 4) -> List[List[float]]:
        for attempt in range(retries):                 # retry loop
            try:
                resp = await self.client.embeddings.create(model=MODEL, input=batch)  # one request
                return [d.embedding for d in resp.data]  # keep input order
            except RateLimitError:                     # 429: back off
                await asyncio.sleep(2 ** attempt + random.random())  # exponential + jitter
            except APIError as exc:                    # other API failure
                log.warning("embed error %s (attempt %d)", exc, attempt)  # log and retry
                await asyncio.sleep(1 + attempt)       # small wait
        raise RuntimeError("embedding failed after retries")  # give up loudly

    async def embed(self, texts: List[str]) -> List[List[float]]:
        clean = [t.replace("\n", " ").strip() for t in texts]  # normalise whitespace
        todo = [t for t in dict.fromkeys(clean) if self._key(t) not in self.cache]  # unseen, unique
        for i in range(0, len(todo), BATCH):           # process in batches
            part = todo[i:i + BATCH]                   # current batch
            vecs = await self._call(part)              # embed batch
            for t, v in zip(part, vecs):               # store results
                self.cache[self._key(t)] = v           # cache by content
        return [self.cache[self._key(t)] for t in clean]  # original order, incl. duplicates

# Token usage: ~1 token per 4 chars. 300-token chunk x 1,000 chunks = 300k tokens = $0.006.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException            # FastAPI
from pydantic import BaseModel, Field                  # pydantic v2

app = FastAPI()                                        # app instance
embedder = Embedder()                                  # from the advanced example

class EmbedIn(BaseModel):                              # request body
    texts: list[str] = Field(min_length=1, max_length=500)  # cap batch size

@app.post("/embed")                                    # route
async def embed(body: EmbedIn) -> dict:
    try:
        vecs = await embedder.embed(body.texts)        # cached + batched
    except RuntimeError as exc:                        # all retries failed
        raise HTTPException(status_code=502, detail=str(exc))  # upstream failure
    return {"model": MODEL, "dims": len(vecs[0]), "vectors": vecs}  # always return the model name
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a built-in cache layer for embeddings, so you do not write hashing code yourself.

```python
from langchain.embeddings import CacheBackedEmbeddings          # wraps any embedder with a cache
from langchain.storage import LocalFileStore                    # simple on-disk key-value store
from langchain_openai import OpenAIEmbeddings                   # base embedder

base = OpenAIEmbeddings(model="text-embedding-3-small")         # real embedder
store = LocalFileStore("./emb_cache")                           # cache folder
cached = CacheBackedEmbeddings.from_bytes_store(                # build cached embedder
    base, store, namespace=base.model                           # namespace avoids cross-model mixups
)
vectors = cached.embed_documents(["Static converters 8504.40"]) # first call pays, repeats are free
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing models in the same index
✅ Correct: one index = one model + dimension; store the model name in metadata.

```python
# Wrong: half the docs embedded with model A (1536-d), new docs with model B (3072-d)
# -> dimension error or meaningless scores
# Right: create index_v2 for model B, re-embed everything, then switch traffic
```

❌ Mistake 2: Embedding giant chunks (whole pages)
✅ Correct: 200-500 token chunks with overlap and a heading prefix.

```python
# Wrong: one 4,000-token vector for a whole chapter -> blurry meaning
vec = embed(whole_chapter)
# Right: small focused chunks, each prefixed with its section title
chunks = [f"{title}\n{c}" for c in chunk_words(chapter, size=250, overlap=30)]
```

❌ Mistake 3: Forgetting query/document prefixes for models that need them (e5, bge)
✅ Correct: use `"query: ..."` / `"passage: ..."` (e5) or the recommended query instruction (bge).

---

## 🧠 Tricky Interview Question

**Q**: "Your index returns good results for long queries but poor results for 1-2 word queries like 'chargers'. What do you do?"

**Answer**: Short queries carry little signal and sit far from long document embeddings. Options: query expansion/rewriting with a cheap LLM ("chargers" -> "power adapters, static converters, 8504"), HyDE (embed a generated hypothetical answer), hybrid search with BM25 so keyword match rescues short queries, and embedding documents with a title/keywords prefix. Measure each on a golden set that includes short queries.

---

## ⚫ Interview Questions + Answers

Q1: Why normalise embeddings?
A1: With unit-length vectors, dot product equals cosine similarity, which is faster and makes scores comparable. Many models (and OpenAI embeddings) are already normalised, but check.

Q2: What chunk size should I use?
A2: Start with 200-500 tokens and 10-15% overlap, split on natural boundaries. Tune on your own golden set because the best size depends on how questions are phrased.

Q3: How do you handle model upgrades?
A3: Treat the model as part of the schema. Build a new index with the new model, dual-run both on the golden set, switch traffic when quality is better, then delete the old index. Never mix vectors.

Q4: How do you reduce embedding cost?
A4: Content-hash caching, only re-embed changed docs, batch requests, dedupe identical chunks, choose a cheaper/smaller model, and use shorter dimensions (OpenAI `dimensions` parameter on text-embedding-3).

Q5: How would you evaluate an embedding setup end to end?
A5: Build a golden set of 100-300 real queries with known relevant chunks. Compute Recall@k, MRR and nDCG. Track by query type (short, long, jargon, multilingual). Add it to CI so any change (model, chunking, preprocessing) must not reduce metrics, and monitor live click or thumbs-up rates for drift.

---

## 🔷 When to Use + When Not to Use
✅ Use these practices when:
- Building any RAG, semantic search or recommendation system
- Corpus is large or changes often (cache + incremental updates matter)

❌ Over-engineering when:
- A prototype with under 100 documents (a simple loop is fine)
- Exact-match lookup (use a normal database index instead)

---

## 📊 Visual Diagram
```
 raw docs -> clean -> chunk(200-500 tok) -> hash? --hit--> cached vector
                                              │ miss
                                              ▼
                                  batch(100) -> embed API (retry/backoff)
                                              │
                                              ▼
                                  normalise -> store(vector + model + metadata)
                                              │
                                              ▼
                            golden-set eval (Recall@k, MRR) -> ship / rollback
```

---

## 💰 Cost Impact
- Embedding price (text-embedding-3-small): $0.02 per 1M tokens. 1M chunks x 300 tokens = 300M tokens = $6.
- Weekly re-ingest with a hash cache touching 3% of chunks = $0.18 instead of $6.
- Storage: 1536 floats x 4 bytes = ~6 KB per vector, so 1M vectors is ~6 GB. Using `dimensions=512` cuts that to ~2 GB.
- Query cost: each user query is one small embedding (~20 tokens, about $0.0000004), so negligible. The LLM call dominates.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunking | Splitting docs into pieces | Documents को टुकड़ों में बाँटना |
| Overlap | Shared text between neighbouring chunks | Chunks के बीच साझा text |
| Normalisation | Scale vector to length 1 | Vector की length 1 करना |
| Content hash | Fingerprint of text for caching | Text का fingerprint |
| Golden set | Labelled queries for evaluation | Evaluation के लिए labelled queries |
| MRR | Mean Reciprocal Rank | सही result की औसत rank का inverse |
| Backoff | Waiting longer after each failure | हर failure पर ज़्यादा इंतज़ार |

---

## ⚡ 3-Line Summary
English: Chunk small, normalise, batch, cache by content hash and store the model version with every vector. Never mix models in one index. Measure Recall@k on a golden set before and after every change.
Hindi: छोटे chunks बनाओ, normalise करो, batch और cache करो, और हर vector के साथ model version रखो। एक index में कभी अलग models मत मिलाओ। हर बदलाव से पहले-बाद Golden set पर Recall@k measure करो।

---

## ➡️ Next Topic
**126. Vector Database — What + Why** — now that vectors are good, where do we store and search millions of them quickly?
