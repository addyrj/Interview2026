"""PDF chat: extract text per page, chunk with page metadata, answer with page citations.

Uses `pypdf` if installed and a path is given; otherwise a built-in fake 3-page PDF so the
script runs offline. Retrieval/answering are keyword-based stand-ins for embeddings + LLM.
"""
from __future__ import annotations

import asyncio
import re
import sys
from dataclasses import dataclass

FAKE_PAGES = [
    "Chapter 85 covers electrical machinery. Smartphones fall under 8517.13.",
    "Duty rates: smartphones 20 percent. Laptops 0 percent under agreement.",
    "Appeals must be filed within 60 days of the assessment notice.",
]


def extract_pages(path: str | None) -> list[str]:
    """Return a list of page texts. Falls back to FAKE_PAGES when no usable PDF."""
    if not path:
        return FAKE_PAGES
    try:
        from pypdf import PdfReader  # optional dependency
    except ImportError:
        print("pypdf missing, using fake pages")
        return FAKE_PAGES
    reader = PdfReader(path)  # raises FileNotFoundError/PdfReadError for bad files
    pages = [(p.extract_text() or "") for p in reader.pages]
    if not any(t.strip() for t in pages):  # scanned PDF -> needs OCR
        raise ValueError("no extractable text: scanned PDF? run OCR first")
    return pages


@dataclass(frozen=True)
class PageChunk:
    page: int
    text: str


def to_chunks(pages: list[str], size: int = 200) -> list[PageChunk]:
    """Chunk each page separately so every chunk keeps its page number."""
    out: list[PageChunk] = []
    for n, text in enumerate(pages, start=1):
        for i in range(0, len(text), size):
            piece = text[i:i + size].strip()
            if piece:
                out.append(PageChunk(n, piece))
    return out


def ask(chunks: list[PageChunk], question: str) -> str:
    """Pick best chunk by word overlap; cite the page."""
    q = set(re.findall(r"\w+", question.lower()))
    best = max(chunks, key=lambda c: len(q & set(re.findall(r"\w+", c.text.lower()))))
    if not q & set(re.findall(r"\w+", best.text.lower())):
        return "Not found in the PDF."
    return f"{best.text} (page {best.page})"


async def achat(path: str | None, question: str) -> str:
    """Async: extraction is blocking IO, so run it in a thread."""
    pages = await asyncio.to_thread(extract_pages, path)
    return ask(to_chunks(pages), question)


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else None
    print(asyncio.run(achat(pdf, "What is the duty on laptops?")))
    print(asyncio.run(achat(pdf, "How many days to file an appeal?")))
