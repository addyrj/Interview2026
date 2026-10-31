---

# 121. Semantic Search — Complete Guide
# हिंदी में: Semantic Search — पूरी Guide

---

## 🔵 Simple Definition (English)
Semantic search finds results by **meaning**, not by exact words. Text is converted to embeddings, and the documents whose vectors are closest to the query vector are returned. "cheap laptop for students" can match "budget notebook for college" even though they share no words.

## 🔵 सरल परिभाषा (Hindi)
Semantic search results **meaning** के आधार पर ढूँढता है, exact शब्दों से नहीं। Text को embeddings में बदला जाता है और query vector के सबसे पास वाले documents लौटाए जाते हैं। "cheap laptop for students" का "budget notebook for college" से match हो जाता है, भले कोई शब्द साझा न हो।

---

## 🔴 Problem it Solves
Keyword search fails on synonyms ("earbuds" vs "earphones"), paraphrases, typos, and different languages. Users do not know the exact terms in the documents (an importer does not know the official HS wording). Semantic search bridges the vocabulary gap.

## 🔴 यह क्यों बना? (Hindi)
Keyword search synonyms ("earbuds" बनाम "earphones"), paraphrases, typos और अलग भाषाओं में fail होता है। Users को documents के exact terms नहीं पता होते (importer को official HS wording नहीं पता)। Semantic search vocabulary का यह gap भर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prepare documents: clean, chunk (200-500 tokens), add metadata
Step 2 → Embed every chunk (document side, same model)
Step 3 → Store vectors + text + metadata in a vector index (FAISS/Chroma/pgvector/Qdrant)
Step 4 → At query time embed the user query with the SAME model
Step 5 → Nearest-neighbour search (cosine / dot) with optional metadata filter
Step 6 → Take top-k (e.g. 20), optionally rerank with a cross-encoder
Step 7 → Apply a minimum-score or "no good match" rule
Step 8 → Return results (or send them to an LLM for RAG)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Documents तैयार करो: clean, chunk (200-500 tokens), metadata जोड़ो
Step 2 → हर chunk embed करो (same model)
Step 3 → Vectors + text + metadata को vector index में store करो
Step 4 → Query के समय user query को SAME model से embed करो
Step 5 → Nearest-neighbour search (cosine / dot), चाहें तो metadata filter
Step 6 → Top-k (जैसे 20) लो, चाहें तो cross-encoder से rerank
Step 7 → न्यूनतम score या "कोई अच्छा match नहीं" का नियम लगाओ
Step 8 → Results लौटाओ (या RAG के लिए LLM को दो)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The importer types "bluetooth speaker with FM radio". Semantic search over 8,000 HS descriptions returns "8518.22 Multiple loudspeakers mounted in the same enclosure" and "8527.99 Reception apparatus for radio-broadcasting" even though neither contains the word "bluetooth". The LLM then picks the best code.

**Zomato-style**: "something warm for a rainy evening" returns soups, chai and pakoras.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer लिखता है "bluetooth speaker with FM radio"। 8,000 HS descriptions पर semantic search "8518.22 Multiple loudspeakers mounted in the same enclosure" और "8527.99 Reception apparatus for radio-broadcasting" लौटाता है, भले किसी में "bluetooth" शब्द नहीं है। फिर LLM सबसे अच्छा code चुनता है।

**Zomato-style**: "something warm for a rainy evening" पर soups, chai और pakoras मिलते हैं।

---

## 💻 Code Example — Basic
```python
# Minimal semantic search (bag-of-words hashing 'embedder' so it runs offline; swap in a real model)
import hashlib
import math

DIM = 64                                              # toy embedding size

SYNONYMS = {"earbuds": "earphones", "notebook": "laptop", "cheap": "budget"}   # toy 'meaning'


def embed(text: str) -> list[float]:
    """Toy embedder: hash words (after synonym mapping) into a fixed vector."""
    vec = [0.0] * DIM
    for w in text.lower().split():
        w = SYNONYMS.get(w, w)                       # map synonyms to the same token
        idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % DIM
        vec[idx] += 1.0
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]                      # unit length


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))          # unit vectors: dot == cosine


docs = ["wireless earphones", "arabica coffee beans", "budget laptop for college"]
index = [(d, embed(d)) for d in docs]                # build the index

def search(query: str, k: int = 2) -> list[tuple[str, float]]:
    q = embed(query)
    scored = [(d, cosine(q, v)) for d, v in index]   # score every doc
    return sorted(scored, key=lambda x: -x[1])[:k]   # best first

print(search("earbuds"))                             # finds 'wireless earphones' via the synonym map
print(search("cheap notebook"))                      # finds 'budget laptop for college'
```

## 💻 Code Example — Advanced
```python
# Production-style semantic search: OpenAI embeddings + numpy index + metadata filter + score threshold (async)
import asyncio
from dataclasses import dataclass, field
from typing import Any
import numpy as np
from openai import AsyncOpenAI

client = AsyncOpenAI()
MODEL = "text-embedding-3-small"


@dataclass
class Hit:
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticIndex:
    def __init__(self) -> None:
        self.texts: list[str] = []
        self.meta: list[dict[str, Any]] = []
        self.vecs: np.ndarray = np.zeros((0, 0), dtype=np.float32)

    async def _embed(self, texts: list[str]) -> np.ndarray:
        try:
            r = await client.embeddings.create(model=MODEL, input=texts)
        except Exception as exc:
            raise RuntimeError(f"embedding failed: {exc}") from exc
        v = np.asarray([d.embedding for d in sorted(r.data, key=lambda d: d.index)], dtype=np.float32)
        return v / np.linalg.norm(v, axis=1, keepdims=True)

    async def add(self, texts: list[str], meta: list[dict[str, Any]] | None = None) -> None:
        new = await self._embed(texts)
        self.texts += texts
        self.meta += meta or [{} for _ in texts]
        self.vecs = new if self.vecs.size == 0 else np.vstack([self.vecs, new])

    async def search(self, query: str, k: int = 5, min_score: float = 0.25,
                     where: dict[str, Any] | None = None) -> list[Hit]:
        if not self.texts:
            return []
        q = (await self._embed([query]))[0]
        scores = self.vecs @ q
        order = np.argsort(-scores)
        hits: list[Hit] = []
        for i in order:
            if where and any(self.meta[i].get(key) != val for key, val in where.items()):
                continue                              # metadata filter
            if scores[i] < min_score:
                break                                 # rest are even lower
            hits.append(Hit(self.texts[i], float(scores[i]), self.meta[i]))
            if len(hits) == k:
                break
        return hits


async def main() -> None:
    idx = SemanticIndex()
    await idx.add(["Headphones and earphones", "Coffee, not roasted", "Loudspeakers"],
                  [{"chapter": 85}, {"chapter": 9}, {"chapter": 85}])
    for h in await idx.search("bluetooth speaker", k=2, where={"chapter": 85}):
        print(round(h.score, 3), h.text)


if __name__ == "__main__":
    asyncio.run(main())                               # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()


class Result(BaseModel):
    text: str
    score: float


async def semantic_search(q: str, k: int) -> list[Result]:
    # Replace with SemanticIndex.search(...) from the advanced example
    return [Result(text=f"match for {q}", score=0.9)][:k]


@app.get("/search", response_model=list[Result])
async def search(q: str = Query(min_length=2, max_length=300), k: int = Query(5, ge=1, le=50)) -> list[Result]:
    try:
        results = await semantic_search(q, k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))   # embedding backend down
    return results
```
Add caching for repeated queries and rate limiting per user.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_chroma import Chroma                    # pip install langchain-chroma
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma.from_texts(
    ["Headphones and earphones", "Coffee, not roasted", "Loudspeakers"],
    embedding=emb,
    metadatas=[{"chapter": 85}, {"chapter": 9}, {"chapter": 85}],
)
results = store.similarity_search_with_relevance_scores("bluetooth speaker", k=2, filter={"chapter": 85})
retriever = store.as_retriever(search_kwargs={"k": 4})   # plug into LCEL / LangGraph nodes
```
In LangGraph, `retrieve` is a node that calls the retriever and writes `documents` into the state; a conditional edge goes to "ask clarification" when no result passes the score threshold.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning top-k blindly
✅ Correct: Apply a score threshold; otherwise unrelated results appear when nothing matches.

```python
# Wrong
return top_k
# Right
return [h for h in top_k if h.score >= MIN_SCORE] or "no good match"
```

❌ Mistake 2: Chunks too big or too small
✅ Correct: 200 to 500 tokens with small overlap; evaluate sizes on your queries.

❌ Mistake 3: Using semantic search for exact identifiers
✅ Correct: Use keyword/metadata lookup for IDs (see topic 122 hybrid search).

---

## 🧠 Tricky Interview Question

**Q**: "A user searches 'HS code 8518.30' and semantic search returns unrelated codes. Why?"

**Answer**: Embeddings encode meaning and treat numbers/codes as weak tokens; exact string matching is not their strength. Fix: detect identifier patterns (regex) and route to keyword or SQL lookup, or use hybrid search (BM25 + vectors with rank fusion) so that exact matches score high.

---

## ⚫ Interview Questions + Answers

Q1: What does semantic search compare?
A1: The query embedding and document embeddings, usually with cosine similarity.

Q2: Why must query and documents use the same model?
A2: Different models create incompatible vector spaces.

Q3: What is top-k and why a threshold?
A3: Top-k returns the k nearest; a threshold stops weak matches from being returned when nothing relevant exists.

Q4: How does a reranker improve results?
A4: A cross-encoder reads query + document together and scores relevance more precisely than vector distance; apply it to the top 20 to 50.

Q5: How would you scale semantic search to 50M documents with 100 queries per second?
A5: Use an ANN index (HNSW/IVF-PQ) in a vector DB like Qdrant/pgvector/Pinecone, shard and replicate, reduce dimensions or quantise, cache hot queries, pre-filter with metadata, rerank only a small top-k, monitor recall vs latency, and batch embed ingestion offline.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users describe needs in their own words
- Synonyms, paraphrases, multilingual queries
- RAG retrieval

❌ Avoid when:
- Exact IDs, codes, names, or boolean logic
- Tiny corpus where keyword search is enough

---

## 📊 Visual Diagram
```
 docs ─► chunk ─► embed ─► [vector index]
                               ▲
 query ─► embed ───────────────┘ nearest neighbours
                               │
                               ▼ top-k ─► (rerank) ─► results / LLM
```

---

## 💰 Cost Impact
Indexing cost is a one-time embedding fee (about $0.02 per 1M tokens with small); each query costs one tiny embedding (about 20 tokens = $0.0000004) plus vector DB compute. The bigger cost is infrastructure for ANN indexes. If results feed an LLM, tokens for the retrieved chunks matter: 5 chunks x 300 tokens = 1,500 input tokens per query. Optimise with query caching, smaller chunks plus reranking (send 3 instead of 8), and dimension reduction.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic search | Search by meaning | Meaning से search |
| Vector index | Structure for fast nearest search | Fast nearest search की structure |
| Top-k | k best results | सबसे अच्छे k results |
| Threshold | Minimum acceptable score | न्यूनतम score |
| Reranker | Precise second-stage ranker | दूसरे चरण का precise ranker |
| ANN | Approximate nearest neighbour | अनुमानित nearest neighbour |

---

## ⚡ 3-Line Summary
English: Semantic search embeds the query and finds the nearest document vectors, matching meaning rather than words. Use the same model both sides, add a score threshold, and rerank for precision. Combine with keyword search for exact identifiers.
Hindi: Semantic search query को embed करके सबसे पास के document vectors ढूँढता है; शब्द नहीं, meaning match होता है। दोनों तरफ same model, score threshold और precision के लिए rerank। Exact identifiers के लिए keyword search के साथ मिलाओ।

---

## ➡️ Next Topic
**122. Semantic vs Keyword Search** - when each wins and how hybrid search combines them.
