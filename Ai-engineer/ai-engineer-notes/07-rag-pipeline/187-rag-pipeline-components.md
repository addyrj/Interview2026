---

# 187. RAG Pipeline Components
# हिंदी में: RAG Pipeline के Components

---

## 🔵 Simple Definition (English)
A RAG pipeline has two halves. **Offline (indexing):** loader, cleaner, splitter, embedder, vector store. **Online (query):** query processor, retriever, reranker, prompt builder, LLM, output parser. Knowing each part and its knobs lets you debug which part is failing.

## 🔵 सरल परिभाषा (Hindi)
RAG pipeline के दो हिस्से होते हैं। **Offline (indexing):** loader, cleaner, splitter, embedder, vector store। **Online (query):** query processor, retriever, reranker, prompt builder, LLM, output parser। हर हिस्सा और उसके knobs जानने से पता चलता है कि कौन सा हिस्सा fail हो रहा है।

---

## 🔴 Problem it Solves
Teams say "RAG is bad" without knowing where. Is the PDF parsed badly? Chunks too big? Embedding model weak? Retriever misses? Prompt ignores context? A clear component map turns one vague problem into five testable ones.

## 🔴 यह क्यों बना? (Hindi)
Teams कहती हैं "RAG खराब है" पर पता नहीं कहाँ। PDF गलत parse हुआ? Chunks बड़े हैं? Embedding कमज़ोर है? Retriever miss कर रहा है? Prompt context ignore करता है? Component map एक vague problem को पाँच testable problems में बदल देता है।

---

## 🟢 How it Works — Step by Step

```
OFFLINE
Step 1 → Loader      : read PDF/CSV/web/DB into Document(text, metadata)
Step 2 → Cleaner     : remove headers, footers, noise
Step 3 → Splitter    : cut into chunks (e.g., 500 tokens, 50 overlap)
Step 4 → Embedder    : chunk -> vector (e.g., 1536 numbers)
Step 5 → Vector store: save vector + text + metadata (+ BM25 index)
ONLINE
Step 6 → Query processor : clean/rewrite query, extract filters
Step 7 → Retriever       : embed query, search top-k
Step 8 → Reranker        : reorder by true relevance
Step 9 → Prompt builder  : system rules + context + question
Step 10 → LLM + parser   : generate, parse, cite sources
```

## 🟢 कैसे काम करता है? (Hindi)
```
OFFLINE
Step 1 → Loader   : PDF/CSV/web/DB को Document(text, metadata) में पढ़ो
Step 2 → Cleaner  : header, footer, noise हटाओ
Step 3 → Splitter : chunks में काटो (जैसे 500 tokens, 50 overlap)
Step 4 → Embedder : chunk -> vector
Step 5 → Vector store: vector + text + metadata save करो
ONLINE
Step 6 → Query processor : query साफ़/rewrite, filters निकालो
Step 7 → Retriever       : query embed करके top-k search
Step 8 → Reranker        : असली relevance से दोबारा क्रम
Step 9 → Prompt builder  : rules + context + question
Step 10 → LLM + parser   : जवाब बनाओ, parse करो, sources दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Loader reads the WCO PDF; cleaner removes page numbers; splitter cuts per heading (chapter, heading, subheading) so one HS code is never split; embedder is `text-embedding-3-small`; store is pgvector with metadata `{chapter, hs_code, year}`; retriever uses hybrid search; prompt says "answer only from context, cite HS code".
**Zomato AI**: Menu items are chunks; metadata has `restaurant_id`, `veg`, `price`; the retriever filters on those before similarity.

## 🟡 Real Example Hindi mein
**Tariff System**: Loader WCO PDF पढ़ता है; cleaner page numbers हटाता है; splitter heading के हिसाब से काटता है ताकि एक HS code टूटे नहीं; embedder `text-embedding-3-small`; store pgvector जिसमें metadata `{chapter, hs_code, year}`; retriever hybrid; prompt: "सिर्फ context से जवाब दो, HS code cite करो"।
**Zomato AI**: Menu items chunks हैं; metadata में `restaurant_id`, `veg`, `price`; similarity से पहले filter।

---

## 💻 Code Example — Basic
```python
# Every RAG component as a tiny pure-Python function (no external packages)
import math
from collections import Counter
from typing import Dict, List, Tuple

def load() -> List[Dict[str, str]]:
    """Loader: return raw documents with metadata."""
    return [{"text": "HS 8517.13 smartphones. Duty 0 percent. Chapter 85.", "chapter": "85"},
            {"text": "HS 0902.30 black tea in packs. Duty 10 percent. Chapter 09.", "chapter": "09"}]

def split(doc: Dict[str, str], size: int = 6) -> List[Dict[str, str]]:
    """Splitter: cut by words, keep metadata on each chunk."""
    words = doc["text"].split()  # word list
    return [{"text": " ".join(words[i:i + size]), "chapter": doc["chapter"]}
            for i in range(0, len(words), size)]  # fixed-size windows

def embed(text: str) -> Counter:
    """Embedder: bag-of-words vector (stand-in for a real model)."""
    return Counter(text.lower().replace(".", "").split())

def cosine(a: Counter, b: Counter) -> float:
    """Similarity between two sparse vectors."""
    dot = sum(a[w] * b[w] for w in a)  # dot product over shared words
    na = math.sqrt(sum(v * v for v in a.values()))  # norm a
    nb = math.sqrt(sum(v * v for v in b.values()))  # norm b
    return dot / (na * nb) if na and nb else 0.0  # avoid divide by zero

def build_store() -> List[Tuple[Counter, Dict[str, str]]]:
    """Vector store: list of (vector, chunk)."""
    return [(embed(c["text"]), c) for d in load() for c in split(d)]

def retrieve(store, query: str, k: int = 2) -> List[Dict[str, str]]:
    """Retriever: top-k chunks by cosine similarity."""
    qv = embed(query)  # embed the query
    ranked = sorted(store, key=lambda item: cosine(qv, item[0]), reverse=True)  # best first
    return [chunk for _, chunk in ranked[:k]]

def build_prompt(query: str, chunks: List[Dict[str, str]]) -> str:
    """Prompt builder: instructions + context + question."""
    ctx = "\n".join(f"- {c['text']}" for c in chunks)  # bullet context
    return f"Answer only from context.\nContext:\n{ctx}\nQuestion: {query}"

if __name__ == "__main__":
    store = build_store()  # offline half
    print(build_prompt("duty on tea", retrieve(store, "duty on tea")))  # online half
```

## 💻 Code Example — Advanced
```python
# Production-style component interfaces (Protocols) so each part is swappable and testable
import asyncio
import logging
from dataclasses import dataclass
from typing import Protocol, Sequence

logger = logging.getLogger("rag_components")  # logger

@dataclass(frozen=True)
class Chunk:
    id: str  # stable id (for dedupe and updates)
    text: str  # chunk text
    metadata: dict  # filters and citation info

class Embedder(Protocol):
    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...  # batch embed

class VectorStore(Protocol):
    async def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None: ...
    async def search(self, vector: list[float], k: int, flt: dict | None) -> list[Chunk]: ...

class LLM(Protocol):
    async def complete(self, prompt: str) -> str: ...  # one-shot completion

class RagApp:
    """Composes components; depends only on interfaces."""

    def __init__(self, embedder: Embedder, store: VectorStore, llm: LLM) -> None:
        self.embedder, self.store, self.llm = embedder, store, llm  # dependency injection

    async def index(self, chunks: Sequence[Chunk], batch: int = 64) -> int:
        done = 0  # count of indexed chunks
        for i in range(0, len(chunks), batch):  # batch to respect API limits
            part = chunks[i:i + batch]
            try:
                vecs = await self.embedder.embed([c.text for c in part])  # embed batch
                await self.store.upsert(part, vecs)  # idempotent write
                done += len(part)
            except Exception:
                logger.exception("batch %d failed", i)  # keep going, report later
        return done

    async def ask(self, query: str, k: int = 4, flt: dict | None = None) -> str:
        (qv,) = await self.embedder.embed([query])  # embed query
        hits = await self.store.search(qv, k, flt)  # retrieval
        if not hits:  # no evidence
            return "Not found in documents."
        ctx = "\n".join(f"[{h.id}] {h.text}" for h in hits)  # cite-able context
        return await self.llm.complete(f"Use only this context:\n{ctx}\n\nQ: {query}")  # generation
```

---

## 🟠 FastAPI Integration
Two separate entry points: an **ingestion** endpoint (or background worker) and a **query** endpoint. Never re-index inside the query path. Use `BackgroundTasks` or a queue for indexing large files.

```python
# FastAPI: /ingest (offline half) and /ask (online half)
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()  # app

class IngestReq(BaseModel):
    doc_id: str  # document identifier
    text: str  # raw text

class AskReq(BaseModel):
    query: str  # question
    chapter: str | None = None  # optional metadata filter

@app.post("/ingest", status_code=202)
async def ingest(req: IngestReq, bg: BackgroundTasks) -> dict:
    bg.add_task(index_document, req.doc_id, req.text)  # run indexing after responding
    return {"status": "queued", "doc_id": req.doc_id}

@app.post("/ask")
async def ask(req: AskReq) -> dict:
    flt = {"chapter": req.chapter} if req.chapter else None  # build filter
    return {"answer": await rag_app.ask(req.query, flt=flt)}  # RagApp from Advanced example
```

---

## 🔗 LangChain / LangGraph Connection
Each component has a LangChain class: `PyPDFLoader` (loader), `RecursiveCharacterTextSplitter` (splitter), `OpenAIEmbeddings` (embedder), `Chroma`/`PGVector` (store), `.as_retriever()` (retriever), `ChatPromptTemplate` (prompt), `ChatOpenAI` (LLM), `StrOutputParser` (parser).

```python
# LangChain mapping of the 10 steps (needs langchain-core, langchain-openai, langchain-chroma, langchain-text-splitters)
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = [Document(page_content="HS 0902.30 black tea duty 10 percent", metadata={"chapter": "09"})]  # loader output
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)  # splitter
store = Chroma.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))  # embed + store
retriever = store.as_retriever(search_kwargs={"k": 4})  # retriever
prompt = ChatPromptTemplate.from_template("Context:\n{context}\n\nQuestion: {question}")  # prompt
fmt = lambda ds: "\n".join(d.page_content for d in ds)  # join docs
chain = ({"context": retriever | fmt, "question": RunnablePassthrough()}
         | prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser())  # LLM + parser
# chain.invoke("duty on tea")  # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding documents with one model and queries with another.
✅ Correct: Use the same embedding model (and version) for both; re-index if you change it.

```python
# Wrong
index_vecs = embed_small(docs); query_vec = embed_large(q)  # different spaces, garbage scores
# Right
index_vecs = embed_small(docs); query_vec = embed_small(q)
```

❌ Mistake 2: Storing only text, with no metadata.
✅ Correct: Store source, page, chapter, date. You need them for filters, citations and deletes.

```python
# Wrong
store.add_texts(["HS 0902.30 black tea ..."])
# Right
store.add_texts(["HS 0902.30 black tea ..."], metadatas=[{"source": "wco.pdf", "page": 12, "chapter": "09"}])
```

---

## 🧠 Tricky Interview Question
**Q**: "Answers are wrong. How do you find which RAG component is at fault?"

**Answer**: Test bottom-up using a labeled set. (1) Parsing: eyeball chunks, is the answer text intact? (2) Retrieval: is the gold chunk in top-k (recall@k)? If not, tune chunking, embedding, hybrid. (3) If retrieved but the answer is wrong, check ordering/rerank and prompt. (4) If context is right and the answer is still wrong, it is a generation problem (model, temperature, instructions). Never tune the LLM before confirming the context contains the answer.

---

## ⚫ Interview Questions + Answers

Q1: Name the offline and online parts of RAG.
A1: Offline: load, clean, split, embed, store. Online: process query, retrieve, rerank, build prompt, generate.

Q2: Why do chunks need overlap?
A2: Overlap keeps sentences that sit on a boundary visible in both chunks, so facts are not cut in half.

Q3: What metadata would you store for tariff chunks?
A3: source file, page, chapter, HS code, country, effective year; used for filtering, citation and invalidating old versions.

Q4: How do you update a changed document?
A4: Use stable chunk ids or a doc hash; delete old chunks by `doc_id`, re-embed only changed chunks, upsert.

Q5: How do you size chunks and k?
A5: Start 300-500 tokens, 10-15 percent overlap, k=4-5 after rerank. Evaluate recall@k and answer faithfulness on a gold set; structured docs should be split on headings, not fixed length.

---

## 🔷 When to Use + When Not to Use
✅ Use this component view when:
- Debugging quality problems
- Designing a new RAG system
- Choosing vendors per layer

❌ Avoid over-engineering when:
- The corpus fits in one prompt (long-context model may do)
- Data changes every second (use live API/SQL tools instead)

---

## 📊 Visual Diagram
```
OFFLINE:  Loader → Cleaner → Splitter → Embedder → Vector Store
                                                     ▲
ONLINE:   Query → Processor → Retriever ─────────────┘
                                 │ top-20
                              Reranker → top-4
                                 │
                       Prompt Builder → LLM → Parser → Answer
```

---

## 💰 Cost Impact
Offline cost: embeddings, e.g. 1M tokens x 0.02 USD/1M (text-embedding-3-small) = 0.02 USD one time. Online cost per query: embed query (~20 tokens, negligible) + prompt (4 chunks x 400 = 1600 tokens + 200 system) + answer (~200 tokens). With gpt-4o-mini, about 0.0004 USD per query.
Optimize: smaller chunks and rerank to send fewer tokens, cache embeddings by hash, batch embed calls, cap `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Loader | Reads raw files into Documents | Files पढ़ने वाला |
| Splitter | Cuts text into chunks | Text को टुकड़ों में काटना |
| Embedder | Turns text into vectors | Text -> vector |
| Vector store | DB for vectors + metadata | Vectors का database |
| Retriever | Finds relevant chunks | सही chunks ढूँढने वाला |
| Reranker | Reorders candidates | Candidates का दोबारा क्रम |
| Chunk overlap | Shared text between neighbours | पास के chunks का साझा text |

---

## ⚡ 3-Line Summary
English: RAG = offline indexing (load, clean, split, embed, store) + online querying (retrieve, rerank, prompt, generate).
Each component has its own knobs and failure modes.
Debug bottom-up: parsing, retrieval, ranking, then generation.
Hindi: RAG = offline indexing (load, clean, split, embed, store) + online querying (retrieve, rerank, prompt, generate)।
हर component के अपने knobs और failure modes होते हैं।
Debug नीचे से ऊपर करो: parsing, retrieval, ranking, फिर generation।

---

## ➡️ Next Topic
**188. Indexing Pipeline**: the offline half in detail: incremental updates, dedupe, batching and idempotent writes.
