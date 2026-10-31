---

# 198. Dense Retrieval
# हिंदी में: Dense Retrieval (सघन रिट्रीवल)

---

## 🔵 Simple Definition (English)
Dense retrieval converts the query and every chunk into dense vectors (embeddings) and returns the chunks whose vectors are closest to the query vector (cosine similarity or dot product). It matches by meaning, so "mobile phone" can find "smartphone" even with no shared words.

## 🔵 सरल परिभाषा (Hindi)
Dense retrieval query और हर chunk को dense vectors (embeddings) में बदलता है और उन chunks को लौटाता है जिनके vectors query vector के सबसे पास हैं (cosine similarity या dot product)। यह अर्थ से match करता है, इसलिए "mobile phone" बिना साझा शब्दों के भी "smartphone" ढूँढ लेता है।

---

## 🔴 Problem it Solves
Keyword search fails on paraphrases, synonyms, typos and multilingual queries (vocabulary mismatch). Users do not know the document's exact words. Dense retrieval captures semantics, so natural-language questions retrieve relevant passages.

## 🔴 यह क्यों बना? (Hindi)
Keyword search paraphrase, synonyms, typos और multilingual queries पर fail होता है (vocabulary mismatch)। Users को document के exact शब्द नहीं पता होते। Dense retrieval semantics पकड़ता है, इसलिए natural-language सवाल relevant passages ढूँढ लेते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose an embedding model (e.g., text-embedding-3-small, 1536 dims)
Step 2 → Offline: embed every chunk -> store vectors in a vector index (HNSW / IVF)
Step 3 → Online: embed the query with the SAME model
Step 4 → ANN search: find the k nearest vectors (cosine / dot product)
Step 5 → Return chunk text + metadata + similarity score
Step 6 → (Optional) rerank with a cross-encoder for precision
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Embedding model चुनो (जैसे text-embedding-3-small, 1536 dims)
Step 2 → Offline: हर chunk embed करके vector index (HNSW / IVF) में रखो
Step 3 → Online: query को उसी model से embed करो
Step 4 → ANN search: k सबसे नज़दीकी vectors ढूँढो (cosine / dot product)
Step 5 → Chunk text + metadata + similarity score लौटाओ
Step 6 → (Optional) precision के लिए cross-encoder से rerank
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user types "noise cancelling things you put in ears from Shenzhen". No document says that, but the embedding of the query is near "wireless earphones / headsets, HS 8518.30". Dense retrieval finds it; BM25 would not. Weak spot: it may confuse "8518.30" with "8518.40".
**Zomato AI**: "something light and healthy for dinner" retrieves "grilled chicken salad" with no shared keywords.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "कान में लगाने वाली noise cancelling चीज़ें Shenzhen से"। किसी document में ऐसा नहीं लिखा, पर query का embedding "wireless earphones / headsets, HS 8518.30" के पास है। Dense retrieval उसे ढूँढ लेता है; BM25 नहीं ढूँढता। कमज़ोरी: यह "8518.30" और "8518.40" को confuse कर सकता है।
**Zomato AI**: "रात के खाने के लिए कुछ हल्का और healthy" बिना साझा शब्दों के "grilled chicken salad" ढूँढता है।

---

## 💻 Code Example — Basic
```python
# Dense retrieval mechanics in pure Python.
# A real system calls an embedding API; here a tiny hand-made "meaning space" shows the idea.
import math
from typing import Dict, List, Tuple

# Pretend embedding model: 3 meaning axes = [audio, phone, footwear]
FAKE_EMBED: Dict[str, List[float]] = {
    "earphones": [0.95, 0.05, 0.0],
    "headset": [0.90, 0.10, 0.0],
    "smartphone": [0.05, 0.95, 0.0],
    "leather shoes": [0.0, 0.0, 1.0],
}

def embed(text: str) -> List[float]:
    """Average the vectors of known words (toy model)."""
    vecs = [v for w, v in FAKE_EMBED.items() if w in text.lower()]  # known phrases found
    if not vecs:
        return [0.0, 0.0, 0.0]  # unknown text -> zero vector
    return [sum(col) / len(vecs) for col in zip(*vecs)]  # mean per axis

def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))  # dot product
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))  # norms
    return dot / (na * nb) if na and nb else 0.0  # safe divide

def dense_search(query: str, docs: List[str], k: int = 2) -> List[Tuple[float, str]]:
    q = embed(query)  # embed query
    scored = [(cosine(q, embed(d)), d) for d in docs]  # similarity to each doc
    return sorted(scored, reverse=True)[:k]  # top-k

if __name__ == "__main__":
    docs = ["HS 8518.30 earphones", "HS 8517.13 smartphone", "HS 6403.99 leather shoes"]
    print(dense_search("headset for music", docs))  # earphones doc first: shares MEANING, not words
```

## 💻 Code Example — Advanced
```python
# Async dense retriever: batching, caching, retries, similarity threshold, in-memory vector index
import asyncio
import hashlib
import logging
import math
import random
from typing import Awaitable, Callable, Sequence

logger = logging.getLogger("dense")  # logger
EmbedBatch = Callable[[Sequence[str]], Awaitable[list[list[float]]]]  # provider call: texts -> vectors

def normalise(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0  # avoid zero division
    return [x / n for x in v]  # unit vector -> dot product == cosine

class DenseRetriever:
    def __init__(self, embed_batch: EmbedBatch, batch_size: int = 64, min_score: float = 0.25) -> None:
        self.embed_batch, self.batch_size, self.min_score = embed_batch, batch_size, min_score  # config
        self.cache: dict[str, list[float]] = {}  # text hash -> vector
        self.ids: list[str] = []; self.texts: list[str] = []; self.vecs: list[list[float]] = []  # index

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        keys = [hashlib.sha1(t.encode()).hexdigest() for t in texts]  # cache keys
        missing = [(k, t) for k, t in zip(keys, texts) if k not in self.cache]  # not cached yet
        for i in range(0, len(missing), self.batch_size):  # batch provider calls
            part = missing[i:i + self.batch_size]
            for attempt in range(3):  # retry with backoff
                try:
                    vecs = await self.embed_batch([t for _, t in part])
                    for (k, _), v in zip(part, vecs):
                        self.cache[k] = normalise(v)  # store normalised
                    break
                except Exception as exc:
                    logger.warning("embed retry %d: %r", attempt + 1, exc)
                    if attempt == 2:
                        raise  # give up
                    await asyncio.sleep(2 ** attempt + random.random())
        return [self.cache[k] for k in keys]

    async def add(self, items: dict[str, str]) -> None:
        vecs = await self._embed(list(items.values()))  # embed all texts
        for (cid, text), v in zip(items.items(), vecs):
            self.ids.append(cid); self.texts.append(text); self.vecs.append(v)

    async def search(self, query: str, k: int = 5) -> list[tuple[str, float, str]]:
        (q,) = await self._embed([query])  # embed query (cached if repeated)
        scored = [(sum(a * b for a, b in zip(q, v)), i) for i, v in enumerate(self.vecs)]  # dot = cosine
        scored.sort(reverse=True)  # best first
        return [(self.ids[i], s, self.texts[i]) for s, i in scored[:k] if s >= self.min_score]  # thresholded

async def fake_embed(texts: Sequence[str]) -> list[list[float]]:
    return [[1.0 if "earphone" in t.lower() else 0.0, 1.0 if "phone" in t.lower() else 0.0, 0.1] for t in texts]  # offline stub

if __name__ == "__main__":
    async def main() -> None:
        r = DenseRetriever(fake_embed)
        await r.add({"a": "HS 8518.30 earphones", "b": "HS 6403.99 shoes"})
        print(await r.search("earphones duty", k=2))
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Create the retriever and the real embedding client (`AsyncOpenAI`) once at startup; embed the query per request; use `async` end to end. Return scores so clients can threshold.

```python
# FastAPI dense search with the OpenAI embeddings API (openai>=1)
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

client = AsyncOpenAI()  # reads OPENAI_API_KEY from env

async def openai_embed(texts):
    resp = await client.embeddings.create(model="text-embedding-3-small", input=list(texts))  # batch call
    return [d.embedding for d in resp.data]  # list of vectors

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retriever = DenseRetriever(openai_embed)  # DenseRetriever from the Advanced example
    yield  # app runs here

app = FastAPI(lifespan=lifespan)  # app with startup logic

class Q(BaseModel):
    query: str
    k: int = 5

@app.post("/dense-search")
async def dense_search_route(q: Q) -> list[dict]:
    try:
        hits = await app.state.retriever.search(q.query, q.k)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="embedding provider error") from exc
    return [{"id": i, "score": round(s, 4), "text": t} for i, s, t in hits]
```

---

## 🔗 LangChain / LangGraph Connection
`OpenAIEmbeddings` + a vector store (`Chroma`, `FAISS`, `PGVector`, `Qdrant`...) -> `.as_retriever()`. Search types: `similarity`, `similarity_score_threshold`, `mmr`. In LangGraph the retriever is a node writing `documents` to state.

```python
# FAISS needs `pip install faiss-cpu langchain-community`; Chroma shown here (langchain-chroma)
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

docs = [Document(page_content="HS 8518.30 earphones duty 0"), Document(page_content="HS 6403.99 leather shoes duty 20")]
# store = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))   # needs OPENAI_API_KEY
# retriever = store.as_retriever(search_type="similarity_score_threshold",
#                                search_kwargs={"k": 3, "score_threshold": 0.3})
# print(retriever.invoke("things you wear in your ears"))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using different embedding models (or versions) for documents and queries.
✅ Correct: Same model for both; re-embed everything when you switch.

```python
# Wrong
doc_vecs = embed("text-embedding-3-small", docs); q = embed("text-embedding-3-large", query)
# Right
doc_vecs = embed(MODEL, docs); q = embed(MODEL, query)
```

❌ Mistake 2: No similarity threshold, so irrelevant chunks always fill top-k.
✅ Correct: Drop results below a tuned threshold; abstain when none remain.

```python
# Wrong
return top_k
# Right
return [h for h in top_k if h.score >= 0.3]
```

---

## 🧠 Tricky Interview Question
**Q**: "Your dense retriever ranks 'HS 8518.40 amplifiers' above 'HS 8518.30 earphones' for the query '8518.30'. Why?"

**Answer**: Embeddings encode overall semantics, not exact character sequences. Numbers and codes that differ by one digit are nearly identical in vector space, and the amplifier chunk may be longer or more generic. Dense models are weak at exact identifiers. Add BM25 (hybrid), extract HS codes into metadata and filter/boost on exact match, or route code-like queries to keyword search.

---

## ⚫ Interview Questions + Answers

Q1: What is an embedding?
A1: A fixed-length vector of numbers representing the meaning of text; similar meanings are close together.

Q2: Cosine similarity vs dot product?
A2: Cosine ignores vector length and measures angle; dot product also uses length. With normalised vectors they are equal, so most systems normalise and use dot product for speed.

Q3: What is ANN and why is it used?
A3: Approximate nearest neighbour search (HNSW, IVF) trades a tiny amount of accuracy for large speed-ups over scanning every vector.

Q4: What are the weaknesses of dense retrieval?
A4: Exact IDs/codes, rare terms, negation, numbers, domain shift without fine-tuning, and it needs an embedding model plus storage.

Q5: How do you choose an embedding model?
A5: Evaluate on your own labeled queries (recall@k, nDCG): compare candidates (OpenAI text-embedding-3, Cohere, BGE, E5) for quality, dimension (storage/latency), max input tokens, language support (Hindi!), cost and licensing; consider fine-tuning or Matryoshka dimension truncation for cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Natural-language questions and paraphrases
- Multilingual or conceptual search
- You lack the exact terms users will type

❌ Avoid alone when:
- Exact codes, names, part numbers matter (add BM25)
- You cannot afford embedding storage/latency (small corpora may use keyword search)

---

## 📊 Visual Diagram
```
 OFFLINE:  chunk ─► embedding model ─► [0.12, -0.7, ... 1536 dims] ─► vector index (HNSW)

 ONLINE:   query ─► same model ─► q-vector
                                      │ nearest neighbours (cosine)
                                      ▼
                         top-k chunks (+ scores)

 meaning space:   "earphones" • • "headset"        • "smartphone"
                       (close)                          (far)
```

---

## 💰 Cost Impact
Embedding cost with text-embedding-3-small is 0.02 USD per 1M tokens: indexing 100M tokens costs 2 USD once. Each query embedding (~20 tokens) is negligible (0.0000004 USD). Storage: 1536 floats x 4 bytes = 6 KB per chunk; 1M chunks = about 6 GB (use float16, quantisation or smaller dims to cut it).
Optimize: cache query embeddings, batch indexing, use dimension truncation (e.g., 512) where recall is fine, store vectors in a quantised index.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector of text meaning | Text के अर्थ का vector |
| Cosine similarity | Angle-based closeness | कोण पर आधारित समानता |
| ANN | Fast approximate nearest neighbour | तेज़ अनुमानित nearest neighbour |
| HNSW | Graph-based ANN index | Graph आधारित ANN index |
| Dimension | Vector length | Vector की लंबाई |
| Semantic search | Search by meaning | अर्थ से search |

---

## ⚡ 3-Line Summary
English: Dense retrieval embeds queries and chunks and finds nearest vectors, matching by meaning.
It handles paraphrases and languages well but is weak on exact codes.
Use the same model for both sides, set thresholds, and pair it with BM25.
Hindi: Dense retrieval queries और chunks को embed करके nearest vectors ढूँढता है, यानी अर्थ से match।
यह paraphrase और भाषाओं में अच्छा है पर exact codes में कमज़ोर।
दोनों तरफ़ एक ही model, thresholds, और BM25 के साथ जोड़ी बनाओ।

---

## ➡️ Next Topic
**199. Hybrid Search (BM25 + Dense)**: combine both retrievers to get exact-match precision and semantic recall.
