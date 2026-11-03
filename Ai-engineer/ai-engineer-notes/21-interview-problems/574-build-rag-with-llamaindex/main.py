"""574. RAG with LlamaIndex.

Install:  pip install llama-index-core     (fastapi optional)
Run:      python main.py
Offline: uses MockEmbedding + MockLLM from llama_index.core (wiring demo; the mock LLM
returns placeholder text, and mock embeddings carry no meaning).
With OPENAI_API_KEY set and `pip install llama-index-llms-openai llama-index-embeddings-openai`,
real models are used.
"""
from __future__ import annotations

import asyncio  # async query
import os  # env check

try:
    from llama_index.core import Document, Settings, VectorStoreIndex  # core objects
    from llama_index.core.embeddings import MockEmbedding  # offline embeddings
    from llama_index.core.llms import MockLLM  # offline LLM
    from llama_index.core.node_parser import SentenceSplitter  # chunker
except ImportError as exc:
    raise SystemExit(f"Missing dependency: {exc}. Run: pip install llama-index-core")

RAW_DOCS: list[tuple[str, str]] = [
    ("hs-8517", "HS 8517 covers telephone sets including smartphones. Duty rate is 20 percent."),
    ("hs-6109", "HS 6109 covers knitted T-shirts. Duty rate is 12 percent for cotton."),
    ("hs-8471", "HS 8471 covers laptops and computers. Duty rate is 0 to 5 percent."),
]


def configure_models() -> None:
    """Set global models (LlamaIndex uses the global Settings object)."""
    if os.getenv("OPENAI_API_KEY"):
        from llama_index.embeddings.openai import OpenAIEmbedding  # lazy import
        from llama_index.llms.openai import OpenAI

        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)  # real LLM
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")  # real embeddings
    else:
        Settings.llm = MockLLM()  # offline LLM
        Settings.embed_model = MockEmbedding(embed_dim=64)  # offline embeddings
    Settings.node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=20)  # chunking


def build_query_engine():  # type: ignore[no-untyped-def]
    configure_models()  # models first
    docs = [Document(text=t, metadata={"id": i}) for i, t in RAW_DOCS]  # documents
    index = VectorStoreIndex.from_documents(docs)  # chunk + embed + index
    return index.as_query_engine(similarity_top_k=2)  # retriever + synthesizer


def create_app():  # type: ignore[no-untyped-def]
    from fastapi import FastAPI, HTTPException  # lazy import
    from pydantic import BaseModel

    class Q(BaseModel):
        question: str  # user question

    engine = build_query_engine()  # build once
    app = FastAPI(title="RAG LlamaIndex")

    @app.post("/ask")
    async def ask(q: Q) -> dict[str, object]:
        try:
            resp = await engine.aquery(q.question)  # async query
        except Exception as exc:
            raise HTTPException(status_code=502, detail=type(exc).__name__) from exc
        sources = [n.node.metadata.get("id") for n in resp.source_nodes]  # cited chunks
        return {"answer": str(resp), "sources": sources}

    return app


async def demo() -> None:
    engine = build_query_engine()  # build
    resp = await engine.aquery("What is the duty on smartphones?")  # ask
    print("answer:", str(resp)[:120])  # mock answer is placeholder text
    print("sources:", [n.node.metadata.get("id") for n in resp.source_nodes])  # retrieved ids


if __name__ == "__main__":
    asyncio.run(demo())
