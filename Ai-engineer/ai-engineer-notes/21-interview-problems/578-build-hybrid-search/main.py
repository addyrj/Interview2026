"""Hybrid search = BM25 (keyword) + vector (semantic) fused with Reciprocal Rank Fusion.

Runs offline: the "embedding" is a hashed bag-of-words stand-in (illustrative only).
In production replace `embed` with a real embedding model call.
"""
from __future__ import annotations

import asyncio
import math
import re
from collections import Counter

DOCS: dict[str, str] = {
    "d1": "HS code 8517.13 smartphones and mobile phones import duty 20 percent",
    "d2": "HS code 8471.30 laptop portable computer import duty 0 percent",
    "d3": "HS code 6109.10 cotton t-shirts knitted apparel duty 12 percent",
    "d4": "HS code 8528.72 television color display duty 10 percent",
    "d5": "Rules of origin and certificate requirements for preferential duty",
}


def tokenize(text: str) -> list[str]:
    """Lowercase and split into alphanumeric tokens (keeps 8517.13 style codes)."""
    return re.findall(r"[a-z0-9][a-z0-9.\-]*", text.lower())


class BM25:
    """Minimal BM25 implementation (k1=1.5, b=0.75)."""

    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tokens = {i: tokenize(t) for i, t in docs.items()}  # tokenised docs
        self.avgdl = sum(len(t) for t in self.tokens.values()) / len(self.tokens)
        self.df: Counter[str] = Counter()  # document frequency per term
        for toks in self.tokens.values():
            self.df.update(set(toks))
        self.n = len(self.tokens)

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        """Return top-k (doc_id, score) pairs by BM25."""
        scores: dict[str, float] = {}
        for doc_id, toks in self.tokens.items():
            tf = Counter(toks)
            score = 0.0
            for term in tokenize(query):
                if term not in tf:
                    continue
                idf = math.log(1 + (self.n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                denom = tf[term] + self.k1 * (1 - self.b + self.b * len(toks) / self.avgdl)
                score += idf * tf[term] * (self.k1 + 1) / denom
            if score > 0:
                scores[doc_id] = score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]


SYNONYMS = {"mobile": "smartphones", "phone": "smartphones", "tv": "television", "tee": "t-shirts"}


def embed(text: str, dim: int = 64) -> list[float]:
    """Fake embedding: hashed bag-of-words with a tiny synonym map (illustrative)."""
    vec = [0.0] * dim
    for tok in tokenize(text):
        tok = SYNONYMS.get(tok, tok)
        vec[hash(tok) % dim] += 1.0  # hash() differs per process but is stable inside one run
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def vector_search(docs: dict[str, str], query: str, k: int = 5) -> list[tuple[str, float]]:
    """Cosine similarity search over fake embeddings."""
    q = embed(query)
    scored = [(i, sum(a * b for a, b in zip(q, embed(t)))) for i, t in docs.items()]
    return sorted([s for s in scored if s[1] > 0], key=lambda x: x[1], reverse=True)[:k]


def rrf(rankings: list[list[tuple[str, float]]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion: score = sum 1/(k + rank). Needs ranks only, not raw scores."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(fused.items(), key=lambda x: x[1], reverse=True)


def hybrid_search(query: str, k: int = 3) -> list[tuple[str, float]]:
    """Run both retrievers and fuse. Raises ValueError on an empty query."""
    if not query.strip():
        raise ValueError("query must not be empty")
    bm25 = BM25(DOCS)
    return rrf([bm25.search(query, 10), vector_search(DOCS, query, 10)])[:k]


async def ahybrid_search(query: str, k: int = 3) -> list[tuple[str, float]]:
    """Async wrapper: CPU work runs in a thread so the event loop stays free."""
    return await asyncio.to_thread(hybrid_search, query, k)


if __name__ == "__main__":
    for q in ["HS 8517.13", "mobile phone duty", "certificate of origin"]:
        res = asyncio.run(ahybrid_search(q))
        print(q, "->", [(d, round(s, 4)) for d, s in res])
    try:
        hybrid_search("   ")
    except ValueError as exc:
        print("error handled:", exc)
