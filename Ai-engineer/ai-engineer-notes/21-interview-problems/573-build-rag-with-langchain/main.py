"""573. RAG with LangChain (LCEL).

Install:  pip install langchain-core langchain-text-splitters   (fastapi optional)
Run:      python main.py
Offline: uses langchain_core fake embeddings + fake chat model, no API key.
With OPENAI_API_KEY set (and `pip install langchain-openai`) it uses real models.
Fake embeddings are random-but-deterministic, so retrieval ORDER here is NOT meaningful;
the demo shows wiring only. Use real embeddings for real relevance.
"""
from __future__ import annotations

import asyncio  # async invoke
import os  # env check

try:
    from langchain_core.documents import Document  # document type
    from langchain_core.embeddings import DeterministicFakeEmbedding  # offline embeddings
    from langchain_core.language_models.fake_chat_models import FakeListChatModel  # offline LLM
    from langchain_core.output_parsers import StrOutputParser  # to plain string
    from langchain_core.prompts import ChatPromptTemplate  # prompt template
    from langchain_core.runnables import RunnablePassthrough  # pass question through
    from langchain_core.vectorstores import InMemoryVectorStore  # vector store
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # chunker
except ImportError as exc:  # clear message instead of a stack trace
    raise SystemExit(f"Missing dependency: {exc}. Run: pip install langchain-core langchain-text-splitters")

RAW_DOCS: list[tuple[str, str]] = [
    ("hs-8517", "HS 8517 covers telephone sets including smartphones. Duty rate is 20 percent."),
    ("hs-6109", "HS 6109 covers knitted T-shirts. Duty rate is 12 percent for cotton."),
    ("hs-8471", "HS 8471 covers laptops and computers. Duty rate is 0 to 5 percent."),
]


def build_models() -> tuple[object, object]:
    """Return (embeddings, chat_model): real if a key exists, else fakes."""
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # lazy import

        return OpenAIEmbeddings(model="text-embedding-3-small"), ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return DeterministicFakeEmbedding(size=64), FakeListChatModel(responses=["Smartphones fall under HS 8517 (duty 20 percent) [hs-8517]."])


def build_chain():  # type: ignore[no-untyped-def]
    emb, llm = build_models()  # models
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)  # chunking
    docs = [Document(page_content=t, metadata={"id": i}) for i, t in RAW_DOCS]  # raw docs
    chunks = splitter.split_documents(docs)  # split
    store = InMemoryVectorStore(emb)  # vector store
    store.add_documents(chunks)  # embed + index
    retriever = store.as_retriever(search_kwargs={"k": 2})  # top-2 retrieval

    def fmt(ds: list[Document]) -> str:
        return "\n".join(f"[{d.metadata['id']}] {d.page_content}" for d in ds)  # context string

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer only from the context. Cite [id]. If unsure say 'I don't know'.\n\nContext:\n{context}"),
        ("human", "{question}"),
    ])  # grounded prompt
    chain = (
        {"context": retriever | fmt, "question": RunnablePassthrough()}  # parallel: retrieve + pass
        | prompt
        | llm
        | StrOutputParser()
    )  # LCEL pipeline
    return chain


def create_app():  # type: ignore[no-untyped-def]
    from fastapi import FastAPI, HTTPException  # lazy import
    from pydantic import BaseModel

    class Q(BaseModel):
        question: str  # user question

    chain = build_chain()  # build once at import
    app = FastAPI(title="RAG LangChain")

    @app.post("/ask")
    async def ask(q: Q) -> dict[str, str]:
        try:
            return {"answer": await chain.ainvoke(q.question)}  # async LCEL call
        except Exception as exc:  # provider or retrieval failure
            raise HTTPException(status_code=502, detail=type(exc).__name__) from exc

    return app


async def demo() -> None:
    chain = build_chain()  # build
    print(await chain.ainvoke("What is the duty on smartphones?"))  # async call


if __name__ == "__main__":
    asyncio.run(demo())
