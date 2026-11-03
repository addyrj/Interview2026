"""Document Q&A: chunk -> index -> retrieve -> answer with citations -> refuse if not found.

Offline: retrieval is keyword-overlap; the answerer is extractive (stand-in for an LLM).
"""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

DOC = """Section 1. Smartphones are classified under HS 8517.13 and attract 20 percent duty.

Section 2. Laptops are classified under HS 8471.30 and are duty free under the trade agreement.

Section 3. Importers must file a certificate of origin to claim preferential rates."""


@dataclass(frozen=True)
class Chunk:
    cid: int
    text: str


STOP = {"the", "a", "an", "is", "are", "of", "to", "for", "and", "under", "what", "on", "in"}


def words(text: str) -> set[str]:
    """Content words only."""
    return {w for w in re.findall(r"[a-z0-9.]+", text.lower()) if w not in STOP}


def chunk(text: str) -> list[Chunk]:
    """Split on blank lines (paragraph chunking keeps meaning intact)."""
    return [Chunk(i, p.strip()) for i, p in enumerate(text.split("\n\n")) if p.strip()]


def retrieve(chunks: list[Chunk], question: str, k: int = 2) -> list[tuple[Chunk, float]]:
    """Score = overlap / question words; drop zero scores."""
    q = words(question)
    scored = [(c, len(q & words(c.text)) / max(1, len(q))) for c in chunks]
    return sorted([s for s in scored if s[1] > 0], key=lambda x: x[1], reverse=True)[:k]


def answer(chunks: list[Chunk], question: str, min_score: float = 0.2) -> dict[str, object]:
    """Return best chunk as answer with citation; refuse when evidence is weak."""
    hits = retrieve(chunks, question)
    if not hits or hits[0][1] < min_score:
        return {"answer": "I could not find this in the document.", "citations": []}
    best = hits[0][0]
    return {"answer": best.text, "citations": [best.cid]}


async def aanswer(question: str) -> dict[str, object]:
    """Async entrypoint (chunking is cheap; a real system would await the vector DB here)."""
    return await asyncio.to_thread(answer, chunk(DOC), question)


if __name__ == "__main__":
    for q in ["What is the duty on smartphones?", "Who won the cricket world cup?"]:
        print(q, "->", asyncio.run(aanswer(q)))
