---

# 510. Embedding Model Selection
# हिंदी में: Embedding Model का चुनाव

---

## 🔵 Simple Definition (English)
Embedding model selection is choosing the model that turns text into vectors for search. Key factors: retrieval quality on your data, language support, vector dimension, max input length, cost, speed and whether it is hosted or self-hosted.

## 🔵 सरल परिभाषा (Hindi)
Embedding model selection का मतलब है वो model चुनना जो text को search के लिए vectors में बदले। मुख्य factors: आपके data पर retrieval quality, भाषा support, vector dimension, max input length, cost, speed, और hosted या self-hosted।

---

## 🔴 Problem it Solves
A weak or mismatched embedding model gives bad retrieval, and no LLM can fix missing context. Also, changing the embedding model later forces re-embedding every document, so the choice is costly to reverse.

## 🔴 यह क्यों बना? (Hindi)
कमज़ोर या mismatch embedding model से retrieval खराब होता है और कोई LLM missing context ठीक नहीं कर सकता। Model बाद में बदलने पर सारे documents दोबारा embed करने पड़ते हैं, इसलिए चुनाव पलटना महँगा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List needs: languages (English + Hindi?), domain (legal/tariff), doc length, scale
Step 2 → Shortlist models (hosted API and open-source, e.g. sentence-transformers family)
Step 3 → Build a retrieval eval: 100-300 real queries with known relevant chunks
Step 4 → Embed the corpus with each model; compute recall@k and MRR
Step 5 → Compare dimension (storage), latency, price per 1M tokens
Step 6 → Pick best quality per cost; version the model name in index metadata
Step 7 → Plan migration: build a new index in parallel, switch, then delete old
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ज़रूरतें लिखो: भाषाएँ, domain, doc length, scale
Step 2 → Models shortlist करो (hosted और open-source)
Step 3 → 100-300 real queries और सही chunks का eval बनाओ
Step 4 → हर model से corpus embed करो; recall@k और MRR निकालो
Step 5 → Dimension (storage), latency, price compare करो
Step 6 → प्रति cost सबसे अच्छा model चुनो; model name index metadata में रखो
Step 7 → Migration: नया index parallel बनाओ, switch करो, पुराना हटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Queries mix English product names and Hindi/regional trade terms, and the corpus has legal notes. A general English-only model misses Hindi terms; a multilingual model improves recall@5 on the eval from, say, 0.71 to 0.86 (illustrative). Storage: 1,024-dim vs 384-dim vectors for 5M chunks is about 2.7x more memory, so test whether the bigger one is worth it.
**Amazon-style example**: Product search with many languages and short queries needs a multilingual model.

## 🟡 Real Example Hindi mein
**Tariff System**: Queries में English product names और Hindi/regional trade terms मिले होते हैं, corpus में legal notes हैं। सिर्फ English वाला model Hindi terms miss करता है; multilingual model से eval पर recall@5 0.71 से 0.86 (illustrative) हो सकता है। 5M chunks के लिए 1,024-dim vs 384-dim vectors में लगभग 2.7x memory का फर्क है, इसलिए test करो कि बड़ा model सही में worth है।

---

## 💻 Code Example — Basic
```python
# Basic: compute recall@k for two toy "embedding models" (pure Python, offline)
import math  # for cosine similarity


def cos(a: list[float], b: list[float]) -> float:  # cosine similarity
    dot = sum(x * y for x, y in zip(a, b))  # dot product
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))  # norms
    return dot / (na * nb) if na and nb else 0.0  # guard zero vectors


def recall_at_k(query_vec: list[float], docs: dict[str, list[float]], relevant: str, k: int = 1) -> int:
    ranked = sorted(docs, key=lambda d: cos(query_vec, docs[d]), reverse=True)[:k]  # top-k ids
    return int(relevant in ranked)  # 1 if relevant doc is in top-k


# Fake vectors from two imaginary models:
model_a = {"q": [1, 0, 0], "docs": {"phone": [0.9, 0.1, 0], "shirt": [0, 1, 0]}}  # good
model_b = {"q": [1, 0, 0], "docs": {"phone": [0.2, 0.9, 0], "shirt": [0.8, 0.2, 0]}}  # bad
print("A:", recall_at_k(model_a["q"], model_a["docs"], "phone"))  # 1
print("B:", recall_at_k(model_b["q"], model_b["docs"], "phone"))  # 0
```

## 💻 Code Example — Advanced
```python
# Advanced: async benchmark harness for embedding providers with batching + error handling
import asyncio  # async runtime
from typing import Protocol  # interface typing


class Embedder(Protocol):  # any embedder must implement this
    name: str  # model name
    async def embed(self, texts: list[str]) -> list[list[float]]: ...  # batch embed


class FakeEmbedder:  # offline stand-in; replace with a real client
    def __init__(self, name: str, dim: int) -> None:  # set name and dimension
        self.name, self.dim = name, dim  # store

    async def embed(self, texts: list[str]) -> list[list[float]]:  # produce deterministic vectors
        await asyncio.sleep(0.005)  # simulate network
        return [[(hash((t, i)) % 100) / 100 for i in range(self.dim)] for t in texts]  # fake


async def embed_all(e: Embedder, texts: list[str], batch: int = 64) -> list[list[float]]:  # batching
    out: list[list[float]] = []  # collected vectors
    for i in range(0, len(texts), batch):  # slice batches
        for attempt in range(3):  # retry loop
            try:
                out += await e.embed(texts[i:i + batch])  # embed one batch
                break  # success
            except Exception:  # transient failure
                await asyncio.sleep(0.1 * 2 ** attempt)  # exponential backoff
        else:  # all retries failed
            raise RuntimeError(f"{e.name}: batch {i} failed")  # surface error
    return out  # all vectors


async def main() -> None:  # compare models
    texts = [f"tariff note {i}" for i in range(130)]  # sample corpus
    for e in (FakeEmbedder("small-384", 384), FakeEmbedder("large-1024", 1024)):  # candidates
        v = await embed_all(e, texts)  # embed
        mb = len(v) * len(v[0]) * 4 / 1e6  # float32 memory estimate in MB
        print(e.name, "vectors:", len(v), "dim:", len(v[0]), f"~{mb:.1f}MB")  # report


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Wrap embeddings in one service function so model name and version are config. Store the model name next to each vector so you never mix spaces.

```python
from fastapi import FastAPI  # app
from pydantic import BaseModel  # schema

app = FastAPI()  # app
EMBED_MODEL = "embed-model-v1"  # placeholder config value


class Docs(BaseModel):  # request
    texts: list[str]  # texts to embed


@app.post("/embed")  # route
async def embed(d: Docs) -> dict[str, object]:
    vectors = [[0.0] * 8 for _ in d.texts]  # replace with a real embedding call
    return {"model": EMBED_MODEL, "dim": 8, "count": len(vectors)}  # include model for traceability
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `Embeddings` interface (`embed_documents`, `embed_query`) lets you swap providers. Vector stores take an embeddings object, so benchmarking is easy.

```python
from langchain_core.embeddings import Embeddings  # real base class


class ToyEmbeddings(Embeddings):  # custom implementation
    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # required method
        return [[float(len(t)), 1.0] for t in texts]  # toy vectors

    def embed_query(self, text: str) -> list[float]:  # required method
        return [float(len(text)), 1.0]  # toy vector


print(ToyEmbeddings().embed_query("hs code"))  # works offline
# vectorstore = SomeVectorStore.from_texts(texts, embedding=ToyEmbeddings())  # swap models here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Different models for indexing and querying
✅ Correct: always the same model and version.
```python
# Wrong
index = embed_v1(docs); hits = search(embed_v2(query))  # incompatible vector spaces
# Right
index = embed(docs, MODEL); hits = search(embed(query, MODEL))  # same model
```

❌ Mistake 2: Picking by MTEB average alone
✅ Correct: test on your queries and your language mix.

---

## 🧠 Tricky Interview Question
**Q**: "You must switch embedding models on a live 50M-chunk index with zero downtime. How?"

**Answer**: Blue/green indexing. Build a new index with the new model in the background (batch workers, rate limited), dual-write new documents to both, run shadow queries comparing recall, then switch reads with a flag and keep the old index for rollback. Store model name in metadata. Estimate embedding cost first: 50M chunks x 300 tokens = 15B tokens.

---

## ⚫ Interview Questions + Answers

Q1: What is an embedding? (Easy)
A1: A vector of numbers representing the meaning of text, so similar meanings are close in space.

Q2: What is cosine similarity? (Easy)
A2: The cosine of the angle between two vectors; closer to 1 means more similar direction.

Q3: Trade-off of higher dimension? (Medium)
A3: Often slightly better quality but more memory, slower search and higher cost. Some models support truncating dimensions (Matryoshka-style) to trade quality for size.

Q4: Why does max input length matter? (Medium)
A4: Text beyond the limit gets truncated, so chunks must fit or information is lost silently.

Q5: How would you handle domain-specific vocabulary? (Hard)
A5: Compare on domain eval, try hybrid search (BM25 handles exact codes), fine-tune embeddings on query-document pairs, or add domain glossaries and query expansion.

---

## 🔷 When to Use + When Not to Use
✅ Use a bigger/multilingual model when:
- Multi-language corpus or hard domain vocabulary

❌ Avoid when:
- Small English corpus where a small fast model hits the quality bar

---

## 📊 Visual Diagram
```
 Eval queries ─┐
               ├─▶ Model A ─▶ recall@5, latency, $ ┐
 Corpus ───────┤                                   ├─▶ pick best per cost
               └─▶ Model B ─▶ recall@5, latency, $ ┘
 Store: vector + model_name + version
```

---

## 💰 Cost Impact
Embedding cost = corpus tokens x price (one time) + query tokens (ongoing). Example (illustrative): 5M chunks x 300 tokens = 1.5B tokens. Memory: vectors x dimension x 4 bytes (float32).
Optimise: smaller dimension or quantisation, batch embeddings, hash chunks to skip unchanged ones, cache query embeddings for repeated queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Text as a vector | text का vector रूप |
| Dimension | Vector length | vector की लंबाई |
| Recall@k | Relevant in top k | top k में सही |
| MRR | Rank quality metric | rank की गुणवत्ता |
| Re-embedding | Recompute all vectors | सब दोबारा embed करना |
| Quantisation | Compress vectors | vectors छोटा करना |

---

## ⚡ 3-Line Summary
English: Choose embeddings with a retrieval eval on your own queries, languages and domain.
Balance quality against dimension, speed and price.
Never mix models in one index; plan blue/green migration.
Hindi: अपने queries, भाषाओं और domain पर retrieval eval से embeddings चुनो।
Quality को dimension, speed और price से balance करो।
एक index में models मत मिलाओ; blue/green migration plan रखो।

---

## ➡️ Next Topic
**511. Vector DB Selection** — where to store and search those vectors.
