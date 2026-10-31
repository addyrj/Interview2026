---

# 192. LangChain Document Loaders
# हिंदी में: LangChain Document Loaders

---

## 🔵 Simple Definition (English)
LangChain document loaders are ready-made classes (`PyPDFLoader`, `CSVLoader`, `WebBaseLoader`, `DirectoryLoader`, ...) that read a source and return `langchain_core.documents.Document` objects. They all share the interface `.load()`, `.lazy_load()` and async `.aload()` / `.alazy_load()`.

## 🔵 सरल परिभाषा (Hindi)
LangChain document loaders तैयार classes हैं (`PyPDFLoader`, `CSVLoader`, `WebBaseLoader`, `DirectoryLoader`, ...) जो source पढ़कर `langchain_core.documents.Document` objects लौटाती हैं। सबका interface एक जैसा है: `.load()`, `.lazy_load()` और async `.aload()` / `.alazy_load()`।

---

## 🔴 Problem it Solves
Writing and maintaining parsers for 100+ formats (PDF, Word, Notion, S3, Slack, SQL) is slow and repetitive. Each library returns a different shape. LangChain gives one `Document` format so loaders, splitters, embedders and vector stores plug together.

## 🔴 यह क्यों बना? (Hindi)
100+ formats (PDF, Word, Notion, S3, Slack, SQL) के parsers लिखना और maintain करना धीमा और दोहराव वाला काम है। हर library अलग shape लौटाती है। LangChain एक `Document` format देता है ताकि loaders, splitters, embedders और vector stores आपस में जुड़ सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install the package (langchain-community, plus parser deps like pypdf)
Step 2 → Instantiate a loader with the source path/URL and options
Step 3 → Call .load() (all at once) or .lazy_load() (stream)
Step 4 → Get list[Document]; each has page_content and metadata
Step 5 → (Optional) subclass BaseLoader to support a custom source
Step 6 → Pipe Documents into a text splitter -> embeddings -> vector store
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package install करो (langchain-community, और pypdf जैसी deps)
Step 2 → Source path/URL और options के साथ loader बनाओ
Step 3 → .load() (एक साथ) या .lazy_load() (stream) call करो
Step 4 → list[Document] मिलती है; हर एक में page_content और metadata
Step 5 → (Optional) custom source के लिए BaseLoader subclass करो
Step 6 → Documents को splitter -> embeddings -> vector store में भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: `DirectoryLoader` + `PyPDFLoader` loads 400 tariff PDFs (metadata `source`, `page`); `CSVLoader(source_column="hs_code")` loads rate tables (each row a Document with `source`=HS code); a custom `TariffApiLoader(BaseLoader)` pulls daily amendments from a government JSON API.
**Amazon AI**: `S3FileLoader` for product manuals, `WebBaseLoader` for help pages.

## 🟡 Real Example Hindi mein
**Tariff System**: `DirectoryLoader` + `PyPDFLoader` से 400 tariff PDFs load (metadata `source`, `page`); `CSVLoader(source_column="hs_code")` से rate tables (हर row एक Document); custom `TariffApiLoader(BaseLoader)` सरकारी JSON API से रोज़ के amendments लाता है।
**Amazon AI**: Product manuals के लिए `S3FileLoader`, help pages के लिए `WebBaseLoader`।

---

## 💻 Code Example — Basic
```python
# Runs offline: build a custom BaseLoader and use CSVLoader on a temp file
# pip install langchain-core langchain-community
import csv
import tempfile
from typing import Iterator

from langchain_community.document_loaders import CSVLoader  # ready-made loader
from langchain_core.document_loaders import BaseLoader  # base class for custom loaders
from langchain_core.documents import Document  # the shared data type

class TariffListLoader(BaseLoader):
    """Custom loader: turns an in-memory list of tariff dicts into Documents."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows  # source data

    def lazy_load(self) -> Iterator[Document]:  # the only method you must implement
        for i, row in enumerate(self.rows):  # one Document per row
            text = f"HS {row['hs']}: {row['name']}, duty {row['duty']} percent"  # readable sentence
            yield Document(page_content=text, metadata={"source": "inline", "row": i})

if __name__ == "__main__":
    docs = TariffListLoader([{"hs": "8518.30", "name": "earphones", "duty": "0"}]).load()  # load() uses lazy_load()
    print(docs[0].page_content, docs[0].metadata)  # check result

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:  # temp CSV
        w = csv.writer(f); w.writerow(["hs_code", "duty"]); w.writerow(["8518.30", "0"])
        path = f.name
    csv_docs = CSVLoader(file_path=path, source_column="hs_code").load()  # one Document per row
    print(csv_docs[0].page_content)  # "hs_code: 8518.30\nduty: 0"
    print(csv_docs[0].metadata)  # {'source': '8518.30', 'row': 0}
```

## 💻 Code Example — Advanced
```python
# Production: directory of PDFs, lazy streaming, async, per-file error isolation, batching into a splitter
import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, Iterator

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger("lc_loaders")  # logger

def iter_pdf_docs(folder: str) -> Iterator[Document]:
    """Stream pages of all PDFs; one broken file does not stop the rest."""
    for path in sorted(Path(folder).glob("**/*.pdf")):  # find PDFs recursively
        try:
            for doc in PyPDFLoader(str(path)).lazy_load():  # lazy: one page at a time
                doc.metadata["file_name"] = path.name  # enrich metadata
                yield doc
        except Exception:  # corrupted/encrypted PDF
            logger.exception("failed to load %s", path)

async def aiter_pdf_docs(folder: str) -> AsyncIterator[Document]:
    """Async variant: runs blocking parsing in worker threads so the event loop stays free."""
    for path in sorted(Path(folder).glob("**/*.pdf")):
        try:
            docs = await asyncio.to_thread(PyPDFLoader(str(path)).load)  # offload blocking IO/CPU
        except Exception:
            logger.exception("failed to load %s", path); continue
        for d in docs:
            yield d

def to_chunks(docs: Iterator[Document], batch_pages: int = 50) -> Iterator[list[Document]]:
    """Split in batches so memory stays flat for huge folders."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)  # splitter config
    batch: list[Document] = []  # pending pages
    for d in docs:
        batch.append(d)
        if len(batch) >= batch_pages:  # flush batch
            yield splitter.split_documents(batch); batch = []
    if batch:
        yield splitter.split_documents(batch)  # last partial batch

# Usage:
# for chunk_batch in to_chunks(iter_pdf_docs("./tariffs")):
#     vectorstore.add_documents(chunk_batch)     # index batch by batch
```

---

## 🟠 FastAPI Integration
Load the uploaded file in a worker thread (`asyncio.to_thread`) because most LangChain loaders are synchronous, then return page count. Keep a whitelist of loader classes by extension.

```python
# FastAPI: extension -> loader registry, async upload
import asyncio, tempfile, os
from fastapi import FastAPI, File, HTTPException, UploadFile
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader

app = FastAPI()  # app
LOADERS = {".pdf": PyPDFLoader, ".csv": CSVLoader, ".txt": TextLoader}  # safe whitelist

@app.post("/load")
async def load(file: UploadFile = File(...)) -> dict:
    ext = os.path.splitext(file.filename or "")[1].lower()  # file extension
    loader_cls = LOADERS.get(ext)  # pick loader
    if loader_cls is None:
        raise HTTPException(status_code=415, detail=f"unsupported type {ext}")
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:  # persist for loader
        tmp.write(await file.read()); path = tmp.name
    try:
        docs = await asyncio.to_thread(loader_cls(path).load)  # blocking -> thread
    finally:
        os.remove(path)  # always clean up temp file
    return {"documents": len(docs), "first_metadata": docs[0].metadata if docs else None}
```

---

## 🔗 LangChain / LangGraph Connection
Loaders are step 1 of the classic chain: `Loader -> TextSplitter -> Embeddings -> VectorStore -> Retriever`. In LangGraph, ingestion is usually a separate script; the graph only queries the store. `Document.metadata` flows through to retrieved results, so citations (`source`, `page`) come for free.

```python
# End-to-end: loader -> splitter -> store (needs langchain-chroma, langchain-openai, OPENAI_API_KEY)
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# pages = PyPDFLoader("tariff.pdf").load()
# chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(pages)
# store = Chroma.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))
# hits = store.similarity_search("duty on earphones", k=3)
# print(hits[0].metadata)   # {'source': 'tariff.pdf', 'page': 12}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the old import path `langchain.document_loaders`.
✅ Correct: Loaders live in `langchain_community.document_loaders`; core types in `langchain_core`.

```python
# Wrong (deprecated)
from langchain.document_loaders import PyPDFLoader
# Right
from langchain_community.document_loaders import PyPDFLoader
```

❌ Mistake 2: Calling `.load()` on a giant directory (everything in RAM).
✅ Correct: Use `.lazy_load()` and index in batches.

```python
# Wrong
docs = DirectoryLoader("./big", glob="**/*.pdf").load()
# Right
for doc in DirectoryLoader("./big", glob="**/*.pdf").lazy_load():
    process(doc)
```

---

## 🧠 Tricky Interview Question
**Q**: "You use `WebBaseLoader` on a JavaScript-heavy tariff portal and get an almost empty document. Why?"

**Answer**: `WebBaseLoader` fetches static HTML with requests and parses it with BeautifulSoup; it does not run JavaScript, so content rendered client-side is missing. Use a browser-based loader (`PlaywrightURLLoader`, `SeleniumURLLoader`, or `AsyncChromiumLoader`), or call the site's underlying JSON API directly (preferred: faster and more stable). Also check robots/terms and add rate limiting.

---

## ⚫ Interview Questions + Answers

Q1: What does `.load()` return?
A1: A `list[Document]`, each having `page_content` and `metadata`.

Q2: Difference between `.load()` and `.lazy_load()`?
A2: `.load()` returns everything in memory; `.lazy_load()` returns an iterator that yields documents one at a time.

Q3: What metadata does `PyPDFLoader` add?
A3: `source` (file path) and `page` (zero-based page number).

Q4: How do you write a custom loader?
A4: Subclass `BaseLoader` and implement `lazy_load()` yielding `Document`s; `load()` and async versions come for free.

Q5: How would you build a loader for a paginated API with auth, rate limits and incremental sync?
A5: Subclass `BaseLoader`; implement `lazy_load` that walks pages with a cursor, sends the token from env/secret manager, respects `Retry-After`, stores `updated_at` in metadata, accepts a `since` parameter so scheduled runs fetch only changes, and implement `alazy_load` with `httpx.AsyncClient` for concurrency.

---

## 🔷 When to Use + When Not to Use
✅ Use LangChain loaders when:
- A loader exists for your format
- You want a consistent `Document` shape across sources
- Prototyping quickly

❌ Avoid when:
- You need advanced layout/table extraction (use Unstructured, Docling, cloud parsers, then wrap output in Documents)
- You want to avoid framework dependencies (then write 20 lines yourself)

---

## 📊 Visual Diagram
```
 PyPDFLoader ─┐
 CSVLoader ───┤
 WebBaseLoader┼─► list[Document] ─► TextSplitter ─► Embeddings ─► VectorStore
 DirectoryLoader                     (metadata travels along: source, page)
 Custom BaseLoader ┘
```

---

## 💰 Cost Impact
Loaders are free (CPU only) but decide token spend: unfiltered web pages and repeated PDF headers inflate chunks. A tariff folder of 120,000 chunks with 15 percent boilerplate wastes about 7M embedding tokens (0.14 USD) once, and ~15 percent more prompt tokens on every query forever.
Optimize: clean in the loader or a post-load step, dedupe, lazy_load and batch, cache by file hash, choose `PyPDFLoader` (cheap) before paid OCR services.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseLoader | Parent class for loaders | Loaders की base class |
| Document | LangChain data type | LangChain का data type |
| lazy_load | Streaming iterator | Stream करने वाला iterator |
| DirectoryLoader | Loads many files from a folder | Folder की सारी files load करे |
| source_column | CSV column used as source | CSV का source column |
| aload | Async load | Async load |

---

## ⚡ 3-Line Summary
English: LangChain loaders convert many source types into one `Document` type with metadata.
Use `lazy_load()` for big data and subclass `BaseLoader` for custom sources.
Import from `langchain_community.document_loaders`.
Hindi: LangChain loaders कई source types को metadata वाले एक `Document` type में बदलते हैं।
बड़े data के लिए `lazy_load()` और custom sources के लिए `BaseLoader` subclass करो।
Import `langchain_community.document_loaders` से करो।

---

## ➡️ Next Topic
**193. LlamaIndex Loaders**: the same idea in LlamaIndex (`SimpleDirectoryReader`, LlamaHub readers).
