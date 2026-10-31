---

# 209. ColBERT Reranking
# हिंदी में: ColBERT Reranking (Late Interaction)

---

## 🔵 Simple Definition (English)
ColBERT keeps one small vector per token (not one vector per chunk). A query token is matched to its most similar document token ("MaxSim"), and the matches are summed. This is "late interaction": more detail than a bi-encoder, much cheaper than a cross-encoder.

## 🔵 सरल परिभाषा (Hindi)
ColBERT हर token के लिए एक छोटा vector रखता है (पूरे chunk के लिए एक नहीं)। Query का हर token document के सबसे similar token से match होता है ("MaxSim") और matches जोड़े जाते हैं। यह "late interaction" है: bi-encoder से ज़्यादा detail, cross-encoder से बहुत सस्ता।

---

## 🔴 Problem it Solves
A single vector per chunk loses detail (bi-encoder). A cross-encoder keeps detail but cannot precompute anything. ColBERT precomputes token vectors for all documents offline, and at query time only does cheap vector math. It also gives token-level explainability: you can see which words matched.

## 🔴 यह क्यों बना? (Hindi)
हर chunk के लिए एक vector detail खो देता है (bi-encoder)। Cross-encoder detail रखता है पर कुछ precompute नहीं हो सकता। ColBERT सारे documents के token vectors offline बना लेता है और query पर सिर्फ़ सस्ता vector math करता है। साथ में explainability भी मिलती है: कौन से words match हुए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Offline: encode each document into a matrix  D  (num_tokens x 128 dims)
Step 2 → Store D matrices (or compressed residuals) in an index
Step 3 → Query time: encode the query into matrix  Q  (num_query_tokens x 128)
Step 4 → For each query token, compute similarity with all doc tokens
Step 5 → Take MAX similarity per query token  (MaxSim)
Step 6 → Score(doc) = SUM of those max similarities
Step 7 → Rank docs by score (as retriever, or as a reranker on top-N)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Offline: हर document को matrix D (tokens x 128 dims) में encode करो
Step 2 → D matrices को index में store करो
Step 3 → Query time: query को matrix Q में encode करो
Step 4 → हर query token की सारे doc tokens से similarity निकालो
Step 5 → हर query token के लिए MAX similarity लो (MaxSim)
Step 6 → Score(doc) = इन max similarities का SUM
Step 7 → Score से rank करो (retriever या top-N पर reranker की तरह)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "stainless steel kitchen sink". A bi-encoder may match any "steel" chapter. ColBERT matches "stainless" to "stainless", "kitchen" to "kitchen/household", "sink" to "sinks, wash basins" at token level, so Chapter 7324 (sanitary ware of steel) scores higher than generic steel bars. **Zomato**: dish search where each word (paneer, tikka, spicy) must match. **Amazon**: product title token matching.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "stainless steel kitchen sink"। Bi-encoder किसी भी "steel" chapter से match कर सकता है। ColBERT token स्तर पर "stainless" को "stainless" से, "kitchen" को "household" से, "sink" को "sinks, wash basins" से match करता है, इसलिए Chapter 7324 generic steel bars से ऊपर आता है। **Zomato**: dish search जहाँ हर word (paneer, tikka, spicy) match होना चाहिए। **Amazon**: product title के token matching।

---

## 💻 Code Example — Basic
```python
# Pure Python MaxSim with tiny hand-made token vectors (no numpy, runs offline).
from math import sqrt  # for vector length
from typing import Dict, List  # type hints

Vec = List[float]  # a token vector

# Toy 3-d "embeddings" for tokens (real ColBERT uses 128-d learned vectors).
EMB: Dict[str, Vec] = {
    "stainless": [1.0, 0.0, 0.0],
    "steel": [0.9, 0.1, 0.0],
    "sink": [0.0, 1.0, 0.0],
    "basin": [0.0, 0.9, 0.1],
    "kitchen": [0.0, 0.2, 1.0],
    "bar": [0.5, 0.0, 0.0],
}


def cos(a: Vec, b: Vec) -> float:
    """Cosine similarity of two vectors."""
    dot = sum(x * y for x, y in zip(a, b))  # dot product
    na, nb = sqrt(sum(x * x for x in a)), sqrt(sum(y * y for y in b))  # norms
    return dot / (na * nb) if na and nb else 0.0  # avoid divide by zero


def encode(text: str) -> List[Vec]:
    """Text -> list of token vectors (unknown tokens skipped)."""
    return [EMB[t] for t in text.lower().split() if t in EMB]  # one vector per token


def maxsim(query: str, doc: str) -> float:
    """Sum over query tokens of the best matching doc token."""
    q_vecs, d_vecs = encode(query), encode(doc)  # token matrices
    if not q_vecs or not d_vecs:  # empty guard
        return 0.0  # no score
    return sum(max(cos(q, d) for d in d_vecs) for q in q_vecs)  # MaxSim


if __name__ == "__main__":
    query = "stainless steel sink"  # query
    docs = ["steel bar", "stainless basin kitchen"]  # candidates
    for d in docs:  # score each
        print(f"{maxsim(query, d):.2f}  {d}")  # print score
```

## 💻 Code Example — Advanced
```python
# Production: RAGatouille (ColBERTv2 wrapper) as a reranker, async-safe with fallback.
import asyncio  # to_thread
import logging  # logs
from typing import Optional  # typing

logger = logging.getLogger("colbert")  # logger


class ColbertReranker:
    """Wraps ragatouille's RAGPretrainedModel. pip install ragatouille (heavy, needs torch)."""

    def __init__(self, model_name: str = "colbert-ir/colbertv2.0") -> None:
        self.model_name = model_name  # HF checkpoint
        self._model: Optional[object] = None  # lazy loaded

    def _get(self):
        if self._model is None:  # first use
            from ragatouille import RAGPretrainedModel  # delayed heavy import
            self._model = RAGPretrainedModel.from_pretrained(self.model_name)  # load weights
        return self._model  # cached

    def _rerank_sync(self, query: str, docs: list[str], k: int) -> list[dict]:
        model = self._get()  # model
        return model.rerank(query=query, documents=docs, k=k)  # list of dicts with content/score/rank

    async def rerank(self, query: str, docs: list[str], k: int = 5) -> list[dict]:
        if not docs:  # nothing to do
            return []  # empty
        try:  # safe call
            return await asyncio.to_thread(self._rerank_sync, query, docs, min(k, len(docs)))  # off event loop
        except Exception as exc:  # missing lib, OOM...
            logger.warning("ColBERT rerank failed: %s", exc)  # log
            return [{"content": d, "score": 0.0, "rank": i + 1} for i, d in enumerate(docs[:k])]  # fallback order
```

---

## 🟠 FastAPI Integration
Load ColBERT lazily and share it. It is heavier than MiniLM, so prefer a GPU worker or a separate microservice.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
colbert = ColbertReranker()  # shared instance


class Req(BaseModel):
    query: str  # query
    documents: list[str]  # candidates
    k: int = 5  # keep


@app.post("/colbert-rerank")  # POST route
async def colbert_route(req: Req) -> list[dict]:
    return await colbert.rerank(req.query, req.documents, req.k)  # returns content, score, rank
```

---

## 🔗 LangChain / LangGraph Connection
RAGatouille can expose a LangChain retriever (`as_langchain_retriever`) when you index documents with ColBERT; as a reranker you can also wrap it in a custom `BaseDocumentCompressor`.

```python
from langchain_core.documents import Document  # doc type

# RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
# RAG.index(collection=texts, index_name="tariff")  # build ColBERT index
# retriever = RAG.as_langchain_retriever(k=5)  # LangChain retriever
# docs = retriever.invoke("stainless steel sink duty")  # returns Documents
# In LangGraph: use `retriever` inside the retrieve node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Averaging token vectors back into one vector
✅ Correct: Keep per-token vectors and use MaxSim; averaging destroys the benefit.

```python
# Wrong: collapse to one vector, becomes a normal bi-encoder
doc_vec = [sum(col) / len(d_vecs) for col in zip(*d_vecs)]

# Right: keep matrix, use MaxSim
score = sum(max(cos(q, d) for d in d_vecs) for q in q_vecs)
```

❌ Mistake 2: Ignoring storage size
✅ Correct: Token vectors are big (about 100x a single vector); use compression/PLAID or rerank only top-N.

```python
# Wrong: store raw float32 token vectors for 10M chunks
# Right: use ColBERTv2 residual compression, or use ColBERT only as a reranker on N=50
```

---

## 🧠 Tricky Interview Question
**Q**: "Why is ColBERT cheaper than a cross-encoder yet nearly as accurate?"

**Answer**: In a cross-encoder, query and document tokens attend to each other inside the transformer, so every pair needs a full forward pass. In ColBERT, the query and document are encoded separately (so document matrices are precomputed offline), and interaction happens only at the end via a light MaxSim on vectors. You lose some cross-attention power, but keep fine-grained token matching, and query-time cost becomes simple matrix multiplication.

---

## ⚫ Interview Questions + Answers

Q1: What does ColBERT stand for?
A1: Contextualized Late Interaction over BERT.

Q2: What is MaxSim?
A2: For each query token, take the highest similarity to any document token, then sum over query tokens.

Q3: How does ColBERT differ from a bi-encoder?
A3: Bi-encoder stores one vector per chunk; ColBERT stores one vector per token and compares at token level.

Q4: What is the main drawback?
A4: Index size and memory: many vectors per document. ColBERTv2 and PLAID reduce this using residual compression and centroid-based pruning.

Q5: When would you pick ColBERT over cross-encoder or Cohere?
A5: When you need token-level precision with an index you control, fast query time on large candidate sets, domain-specific vocabulary (part numbers, codes), or explainability of matches. If you only need top-30 reranking and have GPU, a cross-encoder is simpler; if you want zero ops, use Cohere.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fine-grained matching of terms, codes, names
- Large candidate sets where a cross-encoder is too slow
- You want explainable token matches

❌ Avoid when:
- Memory/storage is tight
- Small corpus where a cross-encoder is fine
- Team cannot maintain extra infra (torch, index)

---

## 📊 Visual Diagram
```
 Query tokens:     [stainless] [steel] [sink]
                        │         │       │
 Doc tokens:   [stainless][basin][kitchen][steel]
                        │         │       │
 MaxSim each:         1.00      0.99    0.90   (best doc token per query token)
                        └─────────┴───────┘
                         SUM = 2.89  → doc score
```

---

## 💰 Cost Impact
- No per-call API fee if self-hosted, but needs GPU/CPU RAM for token matrices.
- Index size: roughly (avg tokens per chunk x 128 dims) per chunk, compressed by ColBERTv2.
- LLM savings: same as any reranker (fewer, better chunks, about 40-60 percent fewer prompt tokens).
- Optimise: use ColBERT only on top-50 candidates, use compressed indexes, quantise.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Late interaction | Compare after separate encoding | अलग encode करके बाद में तुलना |
| MaxSim | Best token match per query token | हर query token का सबसे अच्छा match |
| Token vector | One embedding per token | हर token का embedding |
| PLAID | ColBERT's fast, compressed engine | ColBERT का तेज़ engine |
| Residual compression | Store small differences from centroids | Centroids से अंतर store करना |

---

## ⚡ 3-Line Summary
English: ColBERT stores a vector per token and scores with MaxSim late interaction. It is more precise than a bi-encoder and cheaper than a cross-encoder. The cost is a larger index.
Hindi: ColBERT हर token का vector रखता है और MaxSim late interaction से score करता है। यह bi-encoder से ज़्यादा precise और cross-encoder से सस्ता है। कीमत यह है कि index बड़ा होता है।

---

## ➡️ Next Topic
**210. LLM Reranking** — using a general LLM itself as the reranker, when quality matters more than cost.
