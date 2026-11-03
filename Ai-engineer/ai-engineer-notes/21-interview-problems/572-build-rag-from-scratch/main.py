"""572. RAG from scratch: chunk -> embed -> retrieve -> prompt -> answer.

Run offline demo:  python main.py
Uses a hashing "embedding" and a mock LLM so it needs no API key or packages.
Swap `embed` and `generate` for real models (OpenAI/Qdrant) in production.
"""
from __future__ import annotations

import asyncio  # async API
import hashlib  # stable hashing for toy embeddings
import math  # cosine math
import re  # tokenizing
from dataclasses import dataclass  # chunk record

DIM = 256  # size of the toy embedding vector

DOCS: dict[str, str] = {
    "hs-8517": "HS 8517: telephone sets including smartphones. Duty rate 20 percent. Applies to mobile phones and routers.",
    "hs-6109": "HS 6109: T-shirts, singlets and vests, knitted or crocheted. Duty rate 12 percent for cotton garments.",
    "hs-8471": "HS 8471: automatic data processing machines such as laptops and desktops. Duty rate 0 to 5 percent.",
}


@dataclass(frozen=True)
class Chunk:
    doc_id: str  # source document id
    text: str  # chunk text


def chunk_text(doc_id: str, text: str, size: int = 12, overlap: int = 3) -> list[Chunk]:
    """Split by words with overlap so facts at boundaries survive."""
    if size <= overlap:
        raise ValueError("size must be larger than overlap")  # avoid infinite loop
    words = text.split()  # simple word split
    step = size - overlap  # window stride
    out: list[Chunk] = []  # result list
    for start in range(0, max(len(words), 1), step):  # slide the window
        piece = " ".join(words[start:start + size])  # take a window
        if piece:
            out.append(Chunk(doc_id, piece))  # store chunk
        if start + size >= len(words):
            break  # reached the end
    return out


def embed(text: str) -> list[float]:
    """Toy bag-of-words hashing embedding (replace with a real model)."""
    vec = [0.0] * DIM  # empty vector
    for tok in re.findall(r"[a-z0-9]+", text.lower()):  # tokens
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM  # bucket
        vec[h] += 1.0  # count
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0  # avoid divide by zero
    return [v / norm for v in vec]  # unit vector


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # vectors are normalised -> dot = cosine


class VectorIndex:
    """In-memory vector store (Qdrant/FAISS in production)."""

    def __init__(self) -> None:
        self.items: list[tuple[Chunk, list[float]]] = []  # (chunk, vector)

    def add(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self.items.append((c, embed(c.text)))  # embed at index time

    def search(self, query: str, k: int = 2, min_score: float = 0.1) -> list[tuple[Chunk, float]]:
        q = embed(query)  # embed query
        scored = [(c, cosine(q, v)) for c, v in self.items]  # score all
        scored.sort(key=lambda p: p[1], reverse=True)  # best first
        return [(c, s) for c, s in scored[:k] if s >= min_score]  # drop weak hits


def build_prompt(question: str, hits: list[tuple[Chunk, float]]) -> str:
    context = "\n".join(f"[{c.doc_id}] {c.text}" for c, _ in hits)  # numbered sources
    return (
        "Answer ONLY from the context. If missing, say 'I don't know'.\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer (cite [doc id]):"
    )


async def generate(prompt: str) -> str:
    """Mock LLM: returns the first context line so the demo is deterministic."""
    await asyncio.sleep(0)  # pretend network
    lines = [ln for ln in prompt.splitlines() if ln.startswith("[")]  # context lines
    return f"{lines[0]}" if lines else "I don't know"  # grounded or refuse


class RAG:
    def __init__(self) -> None:
        self.index = VectorIndex()  # store

    def ingest(self, docs: dict[str, str]) -> int:
        n = 0  # count chunks
        for doc_id, text in docs.items():
            chunks = chunk_text(doc_id, text)  # split
            self.index.add(chunks)  # embed + store
            n += len(chunks)
        return n

    async def ask(self, question: str) -> dict[str, object]:
        hits = self.index.search(question)  # retrieve
        if not hits:
            return {"answer": "I don't know", "sources": []}  # refuse w/o context
        answer = await generate(build_prompt(question, hits))  # generate
        return {"answer": answer, "sources": [c.doc_id for c, _ in hits]}


def create_app() -> object:
    from fastapi import FastAPI  # lazy import
    from pydantic import BaseModel

    class Q(BaseModel):
        question: str  # user question

    rag = RAG()  # service
    rag.ingest(DOCS)  # load sample data
    app = FastAPI(title="RAG from scratch")

    @app.post("/ask")
    async def ask(q: Q) -> dict[str, object]:
        return await rag.ask(q.question)  # route

    return app


try:
    app = create_app()  # for uvicorn
except ImportError:
    app = None


if __name__ == "__main__":
    rag = RAG()  # build
    print("chunks indexed:", rag.ingest(DOCS))  # ingest
    for q in ["duty on smartphones", "tax on rocket fuel zzz"]:
        print(q, "->", asyncio.run(rag.ask(q)))  # run questions
