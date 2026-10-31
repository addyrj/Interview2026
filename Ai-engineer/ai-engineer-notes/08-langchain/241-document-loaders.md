---

# 241. Document Loaders
# हिंदी में: Document Loaders

---

## 🔵 Simple Definition (English)
A Document Loader reads data from a source (PDF, CSV, web page, database, S3) and returns a list of LangChain `Document` objects, each with `page_content` (text) and `metadata` (source, page, etc.).

## 🔵 सरल परिभाषा (Hindi)
Document Loader किसी source (PDF, CSV, web page, database, S3) से data पढ़कर LangChain `Document` objects की list देता है, जिनमें `page_content` (text) और `metadata` (source, page आदि) होते हैं।

---

## 🔴 Problem it Solves
Data lives in dozens of formats; every RAG project would need custom parsing code. Loaders give one output shape (`Document`) so splitters, embeddings and vector stores work with any source. Metadata kept at load time powers citations and filtering later.

## 🔴 यह क्यों बना? (Hindi)
Data दर्जनों formats में है; हर RAG project को अपना parsing code चाहिए होता। Loaders एक ही output shape (`Document`) देते हैं, इसलिए splitters, embeddings और vector stores किसी भी source के साथ चलते हैं। Load के समय का metadata बाद में citations और filtering को ताकत देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose loader: PyPDFLoader, CSVLoader, WebBaseLoader, TextLoader, DirectoryLoader
Step 2 → loader = PyPDFLoader("file.pdf")
Step 3 → docs = loader.load()           (list[Document], eager)
          or loader.lazy_load()          (generator, memory-friendly)
          or await loader.aload()        (async)
Step 4 → Each Document: page_content + metadata {"source", "page", ...}
Step 5 → Clean/enrich metadata (doc type, date, country)
Step 6 → Pass docs to a text splitter
Step 7 → Embed and index
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Loader चुनो: PyPDFLoader, CSVLoader, WebBaseLoader, TextLoader, DirectoryLoader
Step 2 → loader = PyPDFLoader("file.pdf")
Step 3 → docs = loader.load() (list, eager) या lazy_load() (generator) या await loader.aload()
Step 4 → हर Document: page_content + metadata {"source", "page", ...}
Step 5 → Metadata साफ/समृद्ध करो (doc type, date, country)
Step 6 → Docs को text splitter में दो
Step 7 → Embed करके index करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: load `Customs_Tariff_2026.pdf` with PyPDFLoader (one Document per page with `page` metadata), `HS_codes.csv` with CSVLoader (one Document per row), and the CBIC notifications web page with WebBaseLoader. Add `metadata["doc_type"]` so retrieval can filter. **Amazon**: seller policy pages loaded from the web nightly.

## 🟡 Real Example Hindi mein
**Tariff System**: `Customs_Tariff_2026.pdf` को PyPDFLoader से (हर page एक Document, `page` metadata), `HS_codes.csv` को CSVLoader से (हर row एक Document), और CBIC notifications web page को WebBaseLoader से load करो। `metadata["doc_type"]` जोड़ो ताकि retrieval में filter हो सके।

---

## 💻 Code Example — Basic
```python
# Runs offline (langchain-core): create Documents the way loaders do, and write a tiny custom loader
from pathlib import Path
from typing import Iterator
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader

class TextFolderLoader(BaseLoader):
    """Loads every .txt file in a folder as one Document each."""
    def __init__(self, folder: str) -> None:
        self.folder = Path(folder)  # folder path

    def lazy_load(self) -> Iterator[Document]:
        for p in sorted(self.folder.glob("*.txt")):  # deterministic order
            text = p.read_text(encoding="utf-8")  # read file
            yield Document(page_content=text, metadata={"source": str(p), "doc_type": "note"})

# demo with a temp folder
import tempfile
with tempfile.TemporaryDirectory() as d:
    Path(d, "a.txt").write_text("HS 8518 headphones")
    Path(d, "b.txt").write_text("HS 6403 footwear")
    docs = TextFolderLoader(d).load()  # load() calls lazy_load() and lists it
    for doc in docs:
        print(doc.metadata["source"].split("/")[-1], "->", doc.page_content)
```

## 💻 Code Example — Advanced
```python
# Production ingestion: many loaders, error isolation, metadata enrichment, async
# pip install langchain-community pypdf beautifulsoup4
import asyncio
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, WebBaseLoader

def load_one(path: Path) -> list[Document]:
    if path.suffix == ".pdf":
        docs = PyPDFLoader(str(path)).load()  # one Document per page
    elif path.suffix == ".csv":
        docs = CSVLoader(str(path), encoding="utf-8").load()  # one per row
    else:
        raise ValueError(f"unsupported type: {path.suffix}")
    for d in docs:
        d.metadata.update({"doc_type": path.suffix.lstrip("."), "file": path.name})  # enrich
    return docs

async def load_folder(folder: str) -> tuple[list[Document], list[str]]:
    ok: list[Document] = []
    errors: list[str] = []
    async def worker(p: Path) -> None:
        try:
            ok.extend(await asyncio.to_thread(load_one, p))  # blocking parsers off the event loop
        except Exception as exc:  # one bad file must not kill ingestion
            errors.append(f"{p.name}: {exc}")
    await asyncio.gather(*(worker(p) for p in Path(folder).iterdir() if p.is_file()))
    return ok, errors

async def load_web(urls: list[str]) -> list[Document]:
    return await WebBaseLoader(urls).aload()  # async web load
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import tempfile

app = FastAPI()

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith((".pdf", ".csv")):
        raise HTTPException(415, "Only PDF/CSV supported")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / Path(file.filename).name  # strip any path parts (security)
        p.write_bytes(await file.read())
        docs = await asyncio.to_thread(load_one, p)  # parse off the loop
    return {"pages_or_rows": len(docs), "first_meta": docs[0].metadata if docs else None}
```

---

## 🔗 LangChain / LangGraph Connection
Loaders are the first stage of the ingestion pipeline: `loader -> splitter -> embeddings -> vector store`. In LangGraph, an ingestion graph can have nodes `load`, `clean`, `split`, `index` with retries per node. `Document` is the standard exchange type for retrievers too.

```python
# docs = loader.load(); chunks = splitter.split_documents(docs); vs.add_documents(chunks)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loading everything into memory
```python
# Wrong: docs = DirectoryLoader("big/").load()   # 50 GB in RAM
# Right: for d in loader.lazy_load(): process(d)  # stream, index in batches
```

❌ Mistake 2: Dropping metadata
```python
# Wrong: texts = [d.page_content for d in docs]   # source/page lost -> no citations
# Right: keep Documents (split_documents) so metadata flows to the vector store
```

---

## 🧠 Tricky Interview Question
**Q**: "PyPDFLoader returns empty text for some tariff PDFs. What do you do?"

**Answer**: Those PDFs are scanned images (no text layer). Detect empty `page_content`, then run OCR (Tesseract via `UnstructuredPDFLoader(strategy="ocr_only")`, or a vision LLM), or use layout-aware loaders for tables. Log such files, keep page numbers, and add a quality check (min characters per page) in the ingestion pipeline.

---

## ⚫ Interview Questions + Answers

Q1: What is a Document in LangChain? (Easy)
A1: A class with `page_content: str` and `metadata: dict` (optional `id`).

Q2: `load()` vs `lazy_load()`? (Easy)
A2: `load` returns a full list; `lazy_load` yields one by one to save memory.

Q3: Which loader for tables in PDFs? (Medium)
A3: Layout-aware options such as `UnstructuredPDFLoader` / `PyMuPDF4LLM` / `pdfplumber` based parsing, or vision-based extraction; plain PyPDF flattens tables.

Q4: How do you keep ingestion idempotent? (Medium)
A4: Deterministic IDs (hash of file + page), upsert into the vector store, record file hashes to skip unchanged files (LangChain's indexing API `RecordManager` supports this).

Q5: Design ingestion for 1M mixed files. (Hard)
A5: Queue (SQS/Celery) per file, worker pool with `lazy_load`, per-type loaders, error table with retries, metadata normalisation, batch embeddings, upsert with RecordManager, observability (counts, failures, tokens), and backpressure on embedding API.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Standard formats feeding RAG

❌ Avoid when:
- Highly custom/complex layouts where a dedicated parser or vision model yields much better text

---

## 📊 Visual Diagram
```
 PDF ─┐
 CSV ─┼─► Loader.load()/lazy_load() ─► [Document(page_content, metadata)] ─► Splitter ─► Embeddings ─► Vector store
 Web ─┤                                   metadata: source, page, doc_type
 DB  ─┘
```

---

## 💰 Cost Impact
Loading itself is free (CPU/IO), but what you load determines embedding and LLM tokens later. Cost levers: dedupe pages, strip headers/footers/boilerplate, skip unchanged files, filter low-value pages, and avoid vision/OCR LLMs unless needed (they cost tokens per page).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Document | Text + metadata object | Text + metadata object |
| Loader | Reads a source | Source पढ़ने वाला |
| lazy_load | Generator loading | धीरे-धीरे load |
| Metadata | Info about the text | Text के बारे में जानकारी |
| OCR | Image to text | Image से text |

---

## ⚡ 3-Line Summary
English: Loaders turn files, web and DBs into `Document` objects with text and metadata. Use `lazy_load` and async for large data and isolate errors per file. Keep metadata for citations.
Hindi: Loaders files, web और DB को text + metadata वाले `Document` में बदलते हैं। बड़े data के लिए `lazy_load` और async लो और हर file की error अलग रखो। Citations के लिए metadata बचाकर रखो।

---

## ➡️ Next Topic
**242. Text Splitters** — cutting loaded documents into good-sized chunks.
