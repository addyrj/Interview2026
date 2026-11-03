---

# 534. Design: Document QA System
# हिंदी में: Document QA System का Design

---

## 🔵 Simple Definition (English)
A Document QA system lets users upload files (PDF, DOCX) and ask questions answered only from those files, with citations. It has two paths: an ingestion path (parse, chunk, embed, store) and a query path (retrieve, rerank, generate, cite). This is RAG as a full product.

## 🔵 सरल परिभाषा (Hindi)
Document QA system में user files (PDF, DOCX) upload करता है और उन्हीं files से citations के साथ सवालों के जवाब पाता है। इसके दो रास्ते हैं: ingestion (parse, chunk, embed, store) और query (retrieve, rerank, generate, cite)। यह RAG का पूरा product रूप है।

---

## 🔴 Problem it Solves
LLMs do not know private documents, and pasting a 300-page PDF into the prompt is too large, slow and expensive. Without grounding, the model also invents answers. We need to find the few relevant passages and force the model to answer from them.

## 🔴 यह क्यों बना? (Hindi)
LLM private documents नहीं जानता, और 300 पेज का PDF prompt में डालना बहुत बड़ा, धीमा और महँगा है। Grounding के बिना model जवाब गढ़ भी देता है। हमें कुछ relevant हिस्से ढूँढकर model को उन्हीं से जवाब देने के लिए मजबूर करना है।

---

## 🟢 How it Works — Step by Step

```
INGESTION (async, background worker)
Step 1 → Upload to object storage (S3), create a doc record: status=processing
Step 2 → Parse text (PDF parser, OCR for scans), keep page numbers
Step 3 → Chunk (e.g. 500 tokens, 50 overlap) with metadata (doc_id, page, tenant)
Step 4 → Embed chunks in batches, store in vector DB
Step 5 → Mark status=ready

QUERY (sync, low latency)
Step 6 → Embed the question, search top-k with metadata filter (tenant, doc_id)
Step 7 → Optional rerank to best 4-5 chunks
Step 8 → Prompt: "Answer only from context. Cite [doc,page]. Say 'not found' otherwise"
Step 9 → Return answer + sources
```

## 🟢 कैसे काम करता है? (Hindi)

```
INGESTION (background में)
Step 1 → File को storage में upload, doc record बनाओ: status=processing
Step 2 → Text parse करो (scan हो तो OCR), page numbers रखो
Step 3 → Chunks बनाओ (500 tokens, 50 overlap) + metadata
Step 4 → Chunks को embed करके vector DB में रखो
Step 5 → status=ready

QUERY (तेज़)
Step 6 → सवाल embed करो, tenant/doc filter के साथ top-k खोजो
Step 7 → Rerank करके सबसे अच्छे 4-5 chunks लो
Step 8 → Prompt: "सिर्फ context से जवाब दो, citation दो, न मिले तो 'not found' कहो"
Step 9 → Answer + sources लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Officers upload the HS tariff schedule, customs notices and past rulings. A question like "Is a Bluetooth speaker under 8518 or 8517?" retrieves the chapter notes and prior rulings, and the answer cites "Chapter 85, Note 3, page 412". Tenant filters keep one importer's rulings away from another.
**Amazon-style**: Seller support asks questions over the policy PDFs and gets answers with the policy page.

## 🟡 Real Example Hindi mein
**Tariff System**: Officers HS tariff schedule, customs notices और पुराने rulings upload करते हैं। "Bluetooth speaker 8518 में आएगा या 8517 में?" पूछने पर chapter notes और पुराने rulings मिलते हैं, और जवाब में "Chapter 85, Note 3, page 412" का citation आता है। Tenant filter एक importer का data दूसरे से अलग रखता है।
**Amazon-style**: Seller support policy PDFs पर सवाल पूछता है और page के साथ जवाब पाता है।

---

## 💻 Code Example — Basic
```python
# Basic: tiny in-memory RAG using keyword overlap (pure Python, runs offline)
import re                                              # regex for tokenizing words
from typing import NamedTuple                          # structured chunk type


class Chunk(NamedTuple):
    doc: str                                           # document name
    page: int                                          # page number
    text: str                                          # chunk text


def chunk_text(doc: str, page: int, text: str, size: int = 12) -> list[Chunk]:
    """Split text into word chunks of `size` words."""
    words = text.split()                               # split into words
    return [Chunk(doc, page, " ".join(words[i:i + size]))   # join each slice
            for i in range(0, len(words), size)]       # step by size


def score(query: str, chunk: Chunk) -> int:
    """Count shared words (a stand-in for vector similarity)."""
    q = set(re.findall(r"\w+", query.lower()))         # query word set
    c = set(re.findall(r"\w+", chunk.text.lower()))    # chunk word set
    return len(q & c)                                  # overlap size


def retrieve(query: str, chunks: list[Chunk], k: int = 2) -> list[Chunk]:
    """Return top-k chunks by score."""
    return sorted(chunks, key=lambda c: score(query, c), reverse=True)[:k]   # best first


corpus = chunk_text("tariff.pdf", 12, "Chapter 85 covers electrical machinery. Lithium batteries are classified under heading 8507. Speakers fall under 8518.")
for c in retrieve("which heading for lithium batteries", corpus):   # run a query
    print(f"[{c.doc} p.{c.page}] {c.text}")                         # print with citation
```

## 💻 Code Example — Advanced
```python
# Production style: async query pipeline with tenant filter, grounding prompt, timeout, errors
import asyncio                                         # timeouts and async
from dataclasses import dataclass                      # lightweight result type
from typing import Protocol                            # interface for pluggable parts


@dataclass
class Passage:
    doc_id: str                                        # source document id
    page: int                                          # page number
    text: str                                          # passage text
    score: float                                       # similarity score


class Retriever(Protocol):
    async def search(self, query: str, tenant: str, k: int) -> list[Passage]: ...   # vector search


class LLM(Protocol):
    async def complete(self, prompt: str) -> str: ...  # text generation


GROUND_PROMPT = (
    "Answer ONLY using the context. Cite sources as [doc_id p.page]. "
    "If the answer is not in the context, reply exactly: NOT_FOUND.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)                                                      # grounding template


async def answer(q: str, tenant: str, retriever: Retriever, llm: LLM) -> dict:
    """Retrieve, ground, generate, return answer with sources."""
    try:
        passages = await asyncio.wait_for(retriever.search(q, tenant, k=6), timeout=3)   # bounded search
    except asyncio.TimeoutError:                       # slow vector DB
        return {"answer": None, "error": "retrieval_timeout"}
    passages = [p for p in passages if p.score >= 0.3]  # drop weak matches
    if not passages:                                   # nothing relevant
        return {"answer": "NOT_FOUND", "sources": []}  # refuse instead of guessing
    context = "\n".join(f"[{p.doc_id} p.{p.page}] {p.text}" for p in passages[:5])   # build context
    try:
        text = await asyncio.wait_for(llm.complete(GROUND_PROMPT.format(context=context, question=q)), timeout=30)
    except Exception as exc:                           # model error
        return {"answer": None, "error": f"llm_failed: {exc}"}
    return {"answer": text, "sources": [(p.doc_id, p.page) for p in passages[:5]]}   # final payload
```

---

## 🟠 FastAPI Integration
Upload returns immediately with a `doc_id`; heavy parsing and embedding run in a background task or queue worker (Celery, SQS). Queries are normal async endpoints.

```python
from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException   # FastAPI pieces
import uuid                                            # make ids

app = FastAPI()                                        # app
STATUS: dict[str, str] = {}                            # doc status (DB in prod)


def ingest(doc_id: str, data: bytes) -> None:
    """Parse, chunk, embed, store (placeholder)."""
    STATUS[doc_id] = "ready"                           # mark done


@app.post("/documents")
async def upload(file: UploadFile, bg: BackgroundTasks) -> dict:
    if file.content_type not in ("application/pdf", "text/plain"):   # validate type
        raise HTTPException(415, "unsupported type")   # reject
    doc_id = uuid.uuid4().hex                          # new id
    STATUS[doc_id] = "processing"                      # initial status
    bg.add_task(ingest, doc_id, await file.read())     # run after response
    return {"doc_id": doc_id, "status": "processing"}  # return fast


@app.get("/documents/{doc_id}")
async def status(doc_id: str) -> dict:
    return {"doc_id": doc_id, "status": STATUS.get(doc_id, "unknown")}   # poll status
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides loaders (`PyPDFLoader`), splitters (`RecursiveCharacterTextSplitter`), vector stores and retrievers. LangGraph can model the query path as nodes: retrieve, grade relevance, generate, and a retry/rewrite loop.

```python
# LangChain ingestion + retriever (needs API key and `pip install langchain-community pypdf faiss-cpu`)
from langchain_community.document_loaders import PyPDFLoader          # PDF loader
from langchain_text_splitters import RecursiveCharacterTextSplitter    # splitter
from langchain_community.vectorstores import FAISS                     # local vector store
from langchain_openai import OpenAIEmbeddings                          # embeddings


def build_index(path: str) -> FAISS:
    docs = PyPDFLoader(path).load()                                    # one Document per page
    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
    return FAISS.from_documents(chunks, OpenAIEmbeddings())            # embed and index
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Parsing and embedding inside the upload request
✅ Correct: return a `doc_id` and process in the background.

```python
# Wrong: user waits minutes, request times out
# embed_all(await file.read()); return {"ok": True}
# Right: bg.add_task(ingest, doc_id, data); return {"status": "processing"}
```

❌ Mistake 2: No "not found" path, so the model hallucinates
✅ Correct: score threshold plus a prompt that allows NOT_FOUND.

❌ Mistake 3: No tenant filter on retrieval
✅ Correct: always filter by tenant in the vector query, never after generation. Data leak otherwise.

---

## 🧠 Tricky Interview Question
**Q**: "Users say answers are wrong for questions about tables in PDFs, though retrieval returns the right page. Why?"

**Answer**: Plain text extraction flattens tables, so rows and columns lose their relation and the chunk is meaningless. Use a layout-aware parser, convert tables to markdown/CSV chunks, keep table headers with each chunk, or use a vision-capable model on the page image. Also evaluate retrieval and generation separately to find which one fails.

---

## ⚫ Interview Questions + Answers

Q1: Why chunk documents?
A1: Embeddings work best on focused passages, and prompts have limited size. Small chunks give precise retrieval, overlap prevents cutting a fact in half.

Q2: What is a citation and why add it?
A2: A pointer (doc, page) to the supporting passage. It builds trust, lets users verify, and helps debug hallucinations.

Q3: How do you choose chunk size?
A3: Start around 300-800 tokens with 10-15% overlap, then test with a labelled question set measuring hit rate. Structured docs may split by headings instead.

Q4: What is hybrid search and why use it?
A4: Combine keyword (BM25) and vector search. Keywords catch exact codes like "8507.60", vectors catch meaning. Merge with reciprocal rank fusion.

Q5: (Hard) How do you update documents without re-indexing everything?
A5: Store content hash per document and chunk id. On change, delete that doc's chunks by metadata filter and re-ingest only it. Version documents, keep embedding model version in metadata, and re-embed fully only when the embedding model changes (vectors from different models are not comparable).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Knowledge is private, large or changes often
- You need citations and auditability

❌ Avoid when:
- The document is small enough to fit in the prompt (just send it)
- Questions need whole-document reasoning, such as summarizing everything (use map-reduce or long context)

---

## 📊 Visual Diagram
```
 Upload ─▶ S3 ─▶ Queue ─▶ Worker: parse ▶ chunk ▶ embed ─▶ Vector DB
                                                              ▲
 Question ─▶ API ─▶ embed ─▶ search(filter tenant) ───────────┘
                         │
                    top-k ▶ rerank ▶ prompt ▶ LLM ▶ answer + citations
```

---

## 💰 Cost Impact
Ingestion cost = total document tokens x embedding price, paid once. Query cost = question embedding (tiny) + prompt (system + k chunks + question) + answer. With 5 chunks of 500 tokens, the prompt is about 2,700 tokens per query (illustrative).
Optimize: fewer, better chunks via reranking; cache answers for repeated questions; small model for generation; skip re-embedding unchanged docs by hash; batch embedding calls.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ingestion | Loading and indexing documents | Documents को index करना |
| Chunk | Small piece of a document | Document का छोटा हिस्सा |
| Embedding | Vector of meaning | Meaning का vector |
| Reranker | Re-orders results by relevance | Results को दोबारा क्रम देना |
| Grounding | Answer based on provided context | दिए गए context पर आधारित जवाब |
| Citation | Source reference | स्रोत का हवाला |

---

## ⚡ 3-Line Summary
English: Document QA has an async ingestion path and a fast query path. Retrieve with tenant filters, ground the prompt, and cite sources. Allow "not found" to prevent hallucination.
Hindi: Document QA में async ingestion और तेज़ query path होते हैं। Tenant filter से retrieve करो, prompt को ground करो और sources cite करो। Hallucination रोकने के लिए "not found" का विकल्प रखो।

---

## ➡️ Next Topic
**535. Design: AI Code Review System**: apply the same retrieval and LLM ideas to code diffs, with webhooks and structured comments.
