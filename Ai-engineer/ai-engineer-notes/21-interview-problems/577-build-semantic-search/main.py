"""577. Build Semantic Search - Tariff Classification.

Offline: a toy hashing embedder stands in for a real embedding model
(it captures word overlap, NOT true meaning - illustrative only).
Run:  python main.py
"""
from __future__ import annotations

import asyncio  # async API
import hashlib  # stable hashing for the toy embedder
import math  # sqrt for normalisation
import re  # tokenizer
from dataclasses import dataclass  # result type
from typing import Any

DIM = 256  # vector size of the toy embedding


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def embed(text: str) -> list[float]:
    """Toy embedding: hashed bag-of-words, L2-normalised."""
    vec = [0.0] * DIM  # empty vector
    for tok in tokenize(text):  # every word
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)  # stable hash
        vec[h % DIM] += 1.0  # count into a bucket
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0  # avoid divide by zero
    return [v / norm for v in vec]  # unit length


def cosine(a: list[float], b: list[float]) -> float:
    """Vectors are unit length, so cosine = dot product."""
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Hit:
    doc_id: str
    text: str
    score: float


class SemanticIndex:
    """In-memory vector index (use Qdrant/pgvector/FAISS in production)."""

    def __init__(self) -> None:
        self.docs: dict[str, str] = {}  # id -> text
        self.vecs: dict[str, list[float]] = {}  # id -> vector

    def add(self, doc_id: str, text: str) -> None:
        """Index one document."""
        if not text.strip():
            raise ValueError("empty document")
        self.docs[doc_id] = text
        self.vecs[doc_id] = embed(text)

    def search(self, query: str, k: int = 3, min_score: float = 0.0) -> list[Hit]:
        """Return top-k hits above min_score."""
        if k < 1:
            raise ValueError("k must be >= 1")
        q = embed(query)  # embed the query the same way
        hits = [Hit(i, self.docs[i], cosine(q, v)) for i, v in self.vecs.items()]
        hits = [h for h in hits if h.score >= min_score]  # threshold
        return sorted(hits, key=lambda h: h.score, reverse=True)[:k]  # best first

    async def asearch(self, query: str, k: int = 3) -> list[Hit]:
        """Async wrapper: CPU work goes to a thread so the loop stays free."""
        return await asyncio.to_thread(self.search, query, k)


CORPUS = {
    "8517.13": "smartphones mobile phones cellular telephones",
    "8471.30": "portable laptop computers notebook data processing machines",
    "6403.99": "footwear leather shoes sports boots",
    "0901.21": "roasted coffee beans not decaffeinated",
}

try:
    from fastapi import FastAPI

    app = FastAPI(title="Semantic Tariff Search")
    index = SemanticIndex()
    for _id, _txt in CORPUS.items():
        index.add(_id, _txt)

    @app.get("/search")
    async def search_route(q: str, k: int = 3) -> list[dict[str, Any]]:
        """GET /search?q=mobile phone"""
        return [h.__dict__ for h in await index.asearch(q, k)]
except ImportError:
    app = None  # type: ignore[assignment]


if __name__ == "__main__":
    idx = SemanticIndex()
    for did, txt in CORPUS.items():
        idx.add(did, txt)
    for hit in asyncio.run(idx.asearch("cellular mobile phone", k=2)):
        print(f"{hit.doc_id}  {hit.score:.3f}  {hit.text}")
