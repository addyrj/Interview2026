---

# 181. RAG — What + Why — Complete Guide
# हिंदी में: RAG — क्या है + क्यों — पूरी Guide

---

## 🔵 Simple Definition (English)
RAG (Retrieval Augmented Generation) = search your documents first, then generate an answer using retrieved content. Without RAG: LLM answers from training data (may be outdated/wrong). With RAG: LLM answers grounded in YOUR documents — accurate, up-to-date, cited. RAG is the #1 pattern for building AI apps on private data.

## 🔵 सरल परिभाषा (Hindi)
RAG (Retrieval Augmented Generation) = पहले documents search करो, फिर retrieved content से answer generate करो। RAG के बिना: LLM training data से answer देता है (outdated/wrong हो सकता है)। RAG के साथ: LLM YOUR documents पर grounded answer देता है — accurate, up-to-date। Private data पर AI apps बनाने का #1 pattern।

---

## 🔴 Problem it Solves
Problem 1 — Knowledge cutoff: GPT-4o training data has a cutoff. New tariff regulations from 2025 are unknown to the model. RAG solves this by injecting current documents at query time.
Problem 2 — Private data: LLMs don't know your company's internal tariff rules. RAG lets you add private knowledge without retraining.
Problem 3 — Hallucination: LLM invents HS codes when uncertain. RAG grounds answers in retrieved documents, enabling citations and verification.

## 🔴 यह क्यों बना? (Hindi)
Problem 1 — Cutoff: LLM को 2025 के नए tariff rules नहीं पता। RAG: documents inject करो।
Problem 2 — Private data: Company के internal rules LLM नहीं जानता। RAG: private knowledge add करो।
Problem 3 — Hallucination: LLM uncertain होने पर HS codes invent करता है। RAG: documents से grounded answer।

---

## 🟢 How it Works — Step by Step

```
INDEXING PHASE (one-time, offline):
Step 1 → Load documents (PDFs, CSVs, web pages)
Step 2 → Split into chunks (e.g. 500 tokens each, 50 overlap)
Step 3 → Embed each chunk → vector [1536 floats]
Step 4 → Store (chunk_text, vector, metadata) in vector DB

RETRIEVAL PHASE (at query time):
Step 5 → User sends query: "What HS code for iPhone?"
Step 6 → Embed query → query vector
Step 7 → Vector DB: cosine similarity → top-k most relevant chunks
Step 8 → Optional: rerank retrieved chunks for better precision

GENERATION PHASE:
Step 9 → Build prompt: system + retrieved_context + user_query
Step 10 → Send to LLM → answer grounded in context
Step 11 → Return answer + source citations
```

---

## 🟡 Real World Example
**Tariff Classification System**: 
- Indexing: 5,000 pages of HS code regulations → chunked → embedded → stored in pgvector
- Query: "What is the import duty for lithium batteries?"
- Retrieve: top-5 chunks from Chapter 85 tariff docs
- Generate: LLM reads retrieved chunks → answers with exact duty % + cites "Chapter 85.06"
- Without RAG: LLM might give 2020 duty rates (wrong) or hallucinate a rate entirely

## 🟡 Real Example Hindi mein
**Tariff System**: 5,000 pages HS code regulations → chunk → embed → pgvector में store। Query: "lithium batteries import duty?" → Chapter 85 से top-5 chunks retrieve → LLM exact duty% + source cite करता है। RAG के बिना: 2020 की rates (wrong) या hallucinated rate।

---

## 💻 Code Example — Basic (RAG from scratch)
```python
# Minimal RAG implementation — no frameworks
from openai import AsyncOpenAI
import numpy as np
from typing import Any

client = AsyncOpenAI()

# ─── Step 1: Index documents ───────────────────────────────────────
async def build_index(documents: list[str]) -> tuple[list[list[float]], list[str]]:
    """Embed all documents. Returns (vectors, texts)."""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=documents,
    )
    vectors = [item.embedding for item in response.data]
    return vectors, documents

# ─── Step 2: Retrieve ──────────────────────────────────────────────
def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_np, b_np = np.array(a), np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

async def retrieve(
    query: str,
    doc_vectors: list[list[float]],
    doc_texts: list[str],
    top_k: int = 3,
) -> list[str]:
    """Find top-k most relevant documents for a query."""
    # Embed the query:
    q_response = await client.embeddings.create(
        model="text-embedding-3-small", input=[query]
    )
    query_vector = q_response.data[0].embedding

    # Score all documents:
    scores = [(cosine_similarity(query_vector, dv), dt)
              for dv, dt in zip(doc_vectors, doc_texts)]
    scores.sort(key=lambda x: x[0], reverse=True)    # sort by score

    return [text for _, text in scores[:top_k]]        # return top-k texts

# ─── Step 3: Generate ──────────────────────────────────────────────
async def rag_query(
    query: str,
    doc_vectors: list[list[float]],
    doc_texts: list[str],
) -> str:
    """Full RAG pipeline: retrieve → generate."""
    # Retrieve relevant chunks:
    relevant = await retrieve(query, doc_vectors, doc_texts)
    context = "\n\n".join(f"[Source {i+1}]: {text}" for i, text in enumerate(relevant))

    # Generate answer grounded in context:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a tariff classification expert. "
                    "Answer ONLY based on the provided context. "
                    "If not in context, say 'Not found in documents.' "
                    "Always cite the source number."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        temperature=0.0,    # deterministic for factual answers
        max_tokens=500,
    )
    return response.choices[0].message.content

# Demo:
import asyncio

async def main():
    # Small tariff knowledge base:
    docs = [
        "HS Code 8517: Telephone sets including smartphones and mobile phones. Import duty 20%.",
        "HS Code 8471: Automatic data processing machines (computers). Import duty 0%.",
        "HS Code 6101: Men's overcoats and jackets of textile. Import duty 12.5%.",
        "Chapter 85 covers electrical machinery including phones, batteries, and electronics.",
    ]

    print("Building index...")
    vectors, texts = await build_index(docs)

    answer = await rag_query("What is the import duty for iPhone 15?", vectors, texts)
    print(f"Answer:\n{answer}")

asyncio.run(main())
```

## 💻 Code Example — Advanced (Production RAG with LangChain + pgvector)
```python
# Production RAG: LangChain + pgvector + FastAPI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import AsyncGenerator

# ─── Setup ─────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# pgvector connection (PostgreSQL with pgvector extension):
CONNECTION_STRING = "postgresql+psycopg://user:password@localhost:5432/tariff_db"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="tariff_chunks",
    connection=CONNECTION_STRING,
)

# ─── Indexing ──────────────────────────────────────────────────────
async def index_pdf(pdf_path: str) -> int:
    """Load PDF, chunk it, embed, store in pgvector."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()                         # list of Document objects

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # tokens approx
        chunk_overlap=50,     # overlap prevents cutting context mid-sentence
        separators=["\n\n", "\n", ".", " "],  # try larger separators first
    )
    chunks = splitter.split_documents(documents)      # split into smaller pieces

    # Add metadata to each chunk:
    for chunk in chunks:
        chunk.metadata["source"] = pdf_path
        chunk.metadata["indexed_at"] = "2025-01-01"

    # Batch embed + store:
    await vector_store.aadd_documents(chunks)
    return len(chunks)

# ─── RAG Chain (LCEL) ──────────────────────────────────────────────
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},      # retrieve top 5 chunks
)

TARIFF_PROMPT = ChatPromptTemplate.from_template("""
You are a tariff classification expert. Answer ONLY based on the context below.
If the answer is not in the context, say "Not found in tariff documents."
Always cite which part of the document supports your answer.

Context:
{context}

Question: {question}

Answer:""")

def format_docs(docs) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n".join(
        f"[Source {i+1} — {doc.metadata.get('source', 'unknown')}]:\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

# LCEL chain: question → retrieve → prompt → llm → parse
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | TARIFF_PROMPT
    | llm
    | StrOutputParser()
)

# ─── FastAPI endpoints ─────────────────────────────────────────────
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import tempfile, os

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/index-document")
async def index_document(file: UploadFile = File(...)):
    """Upload and index a PDF document."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        chunk_count = await index_pdf(tmp_path)
        return {"message": f"Indexed {chunk_count} chunks", "filename": file.filename}
    finally:
        os.unlink(tmp_path)

@app.post("/query")
async def query_tariff(request: QueryRequest):
    """RAG query: retrieve relevant tariff info and generate answer."""
    answer = await rag_chain.ainvoke(request.question)
    return {"question": request.question, "answer": answer}

@app.post("/query/stream")
async def query_tariff_stream(request: QueryRequest):
    """Streaming RAG query — returns answer as it's generated."""
    from fastapi.responses import StreamingResponse

    async def stream():
        async for chunk in rag_chain.astream(request.question):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")
```

---

## 🟠 FastAPI Integration
(See Advanced code example above — complete FastAPI integration with index + query + stream endpoints.)

Key patterns:
- `POST /index-document` — upload PDF, chunk, embed, store
- `POST /query` — RAG query with source citations
- `POST /query/stream` — streaming response (better UX for long answers)

---

## 🔗 LangChain / LangGraph Connection
```python
# LangGraph RAG: query → conditional routing → retrieve → generate → check → respond

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class RAGState(TypedDict):
    question: str
    context: list[str]
    answer: str
    needs_clarification: bool

def retrieve_node(state: RAGState) -> RAGState:
    docs = retriever.invoke(state["question"])
    return {"context": [doc.page_content for doc in docs]}

def generate_node(state: RAGState) -> RAGState:
    context = "\n".join(state["context"])
    answer = rag_chain.invoke(state["question"])
    return {"answer": answer}

def check_answer_node(state: RAGState) -> RAGState:
    # LLM-as-judge: is the answer grounded in context?
    if "Not found" in state["answer"]:
        return {"needs_clarification": True}
    return {"needs_clarification": False}

def route_after_check(state: RAGState) -> str:
    return "clarify" if state["needs_clarification"] else END

graph = StateGraph(RAGState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_node("check", check_answer_node)
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "check")
graph.add_conditional_edges("check", route_after_check)
graph.set_entry_point("retrieve")
rag_graph = graph.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Chunk size too large (loses precision) or too small (loses context)
```python
# Wrong — 5000 token chunks: retrieved chunk contains too much unrelated content
splitter = RecursiveCharacterTextSplitter(chunk_size=5000)

# Wrong — 50 token chunks: sentences cut in half, no coherent context
splitter = RecursiveCharacterTextSplitter(chunk_size=50)

# Correct — 300-500 tokens with 50-100 overlap:
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,      # enough context, not too much noise
    chunk_overlap=50,    # prevents cutting important sentences at boundaries
)
```

❌ Mistake 2: Not including source metadata in the prompt
```python
# Wrong — LLM can't cite sources (user can't verify):
context = "\n".join(doc.page_content for doc in docs)

# Correct — include source info:
context = "\n\n".join(
    f"[Source: {doc.metadata['source']}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
    for doc in docs
)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your RAG system retrieves 5 chunks correctly but the LLM still gives wrong answers. The chunks are relevant — they contain the right information. What could be wrong?"

**Answer**: "Lost in the middle" problem — LLMs perform significantly worse on information in the middle of a long context. If chunk 3 of 5 contains the answer, the model may miss it. Solutions: (1) Put most relevant chunk first or last (not middle). (2) Reduce k from 5 to 3 (less context = less confusion). (3) Use reranking before passing to LLM — reranker picks the single best chunk, eliminating noise. (4) Use `MMR` (Maximum Marginal Relevance) retrieval — avoids returning 5 nearly identical chunks. (5) Compress retrieved chunks to only the relevant sentence using a compression retriever.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Naive RAG, Advanced RAG, and Modular RAG?
A1: Naive RAG: simple chunk → embed → retrieve → generate. Works but limited — fixed chunk size, no query optimization, single retrieval step. Advanced RAG: adds query transformation (HyDE, multi-query), reranking, hybrid search (BM25 + dense), better chunking strategies. Modular RAG: highly customizable pipeline — mix and match components, add memory, feedback loops, self-evaluation. Production systems usually use Advanced RAG patterns.

Q2: What is the difference between semantic search and hybrid search in RAG?
A2: Semantic search: only vector similarity — good at understanding meaning, bad at exact keyword matches (product codes, legal terms, HS codes). BM25/keyword search: only term matching — good at exact matches, bad at synonyms. Hybrid search: combine both scores (RRF — Reciprocal Rank Fusion). For Tariff Classification, hybrid is critical — "8517.12.00" must exact-match, but "smartphones" should also match "mobile telephones."

Q3: What is reranking and when should you add it?
A3: Reranking uses a cross-encoder model (slower but more accurate than bi-encoder) to re-score retrieved chunks for relevance. Process: (1) retrieve top-20 with fast vector search, (2) reranker scores all 20 against the query, (3) take top-5. Add reranking when vector search top-k has low precision (many irrelevant results). Cohere Rerank API, cross-encoder models (sentence-transformers), or LLM-based reranking. Adds ~100-500ms latency.

Q4: How do you evaluate a RAG system?
A4: Using Ragas framework — four metrics: (1) Faithfulness: is the answer grounded in context? (detects hallucinations). (2) Answer Relevancy: does the answer address the question? (3) Context Precision: are retrieved chunks actually relevant? (4) Context Recall: did we retrieve all relevant info? Run these on a golden dataset (test questions + ideal answers + ideal source documents). Automate in CI/CD.

Q5: How would you design a RAG system for 10 million tariff documents?
A5: (1) Storage: pgvector on PostgreSQL (cost-effective) or Pinecone Serverless. (2) Chunking: 400 tokens, sentence-boundary-aware, metadata: chapter, section, regulation_date. (3) Embedding: text-embedding-3-small, batch API. (4) Retrieval: hybrid (BM25 + dense) with RRF. (5) Reranking: Cohere Rerank for top-20→5. (6) Caching: Redis semantic cache for repeated queries. (7) Filtering: metadata filter by regulation_date, chapter number. (8) Evaluation: Ragas with golden dataset in CI. (9) Monitoring: Langfuse for per-query traces, token usage, latency.

---

## 🔷 When to Use + When Not to Use

✅ Use RAG when:
- Working with private/proprietary documents (company knowledge base)
- Documents change frequently (new tariff regulations)
- Need source citations for trust/compliance
- LLM training data doesn't cover your domain
- Reducing hallucination is critical (medical, legal, financial)

❌ Don't use RAG when:
- LLM training data already covers the domain well
- Documents are < 10 pages (just put them in context directly)
- You need real-time data (use function calling + live API instead)
- Simple fact lookup (use a database query, not RAG)

---

## 📊 Visual Diagram
```
INDEXING (one-time):
PDF/Docs → Chunker → [chunks] → Embedder → [vectors] → Vector DB
                                                         (+ metadata)

QUERY TIME:
User Query
    │
    ▼
Embedder → query_vector
    │
    ▼
Vector DB ──── cosine similarity ────► top-k chunks
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ System Prompt     │
                                    │ + Retrieved Docs  │
                                    │ + User Question   │
                                    └──────────────────┘
                                              │
                                              ▼
                                           LLM
                                              │
                                              ▼
                                    Answer + Citations
```

---

## 💰 Cost Impact
Indexing 10,000 tariff document chunks (avg 400 tokens each):
- Embedding: 10K × 400 tokens = 4M tokens × $0.02/1M = **$0.08 one-time**

Per query (gpt-4o-mini):
- Input: system(100) + context(1500) + question(50) = ~1650 tokens = **$0.000248**
- Output: answer ~300 tokens = **$0.000180**
- Total per query: **~$0.000428** (~$42.80 per 100K queries)

Optimization: Redis semantic cache with 30% hit rate → 30% cost reduction

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieval Augmented Generation | Documents से grounded answer |
| Chunking | Splitting documents into smaller pieces | Documents को छोटे टुकड़ों में बाँटना |
| Vector DB | Database for storing + searching vectors | Vectors store करने वाला DB |
| Retriever | Component that fetches relevant chunks | Relevant chunks लाने वाला |
| Grounded answer | Answer based on retrieved documents | Documents पर based answer |
| Hallucination | Confident but wrong answer | गलत पर confident answer |
| Reranking | Re-scoring retrieved chunks | Retrieved chunks को re-score करना |

---

## ⚡ 3-Line Summary
English: RAG = retrieve relevant document chunks first → inject as context → LLM generates grounded answer. Solves LLM knowledge cutoff, private data access, and hallucination. Production RAG adds hybrid search, reranking, caching, and Ragas evaluation.
Hindi: RAG = पहले relevant chunks retrieve → context में inject → LLM grounded answer। LLM cutoff, private data, hallucination तीनों problems solve। Production में hybrid search + reranking + caching + Ragas evaluation जोड़ो।

---

## ➡️ Next Topic
**182. RAG vs Fine-tuning** — when to use each, cost comparison, hybrid approach, decision framework.
