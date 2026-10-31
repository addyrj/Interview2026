---

# 191. Document Loaders (PDF, CSV, Web, DB)
# हिंदी में: Document Loaders (PDF, CSV, Web, DB)

---

## 🔵 Simple Definition (English)
A document loader reads data from a source (PDF, CSV, web page, database) and converts it into a uniform object: text plus metadata (source, page, row). Every later RAG step works on that uniform object, so loader quality sets the quality of the whole system.

## 🔵 सरल परिभाषा (Hindi)
Document loader किसी source (PDF, CSV, web page, database) से data पढ़कर उसे uniform object में बदलता है: text + metadata (source, page, row)। RAG के आगे के सारे steps इसी object पर चलते हैं, इसलिए loader की quality पूरे system की quality तय करती है।

---

## 🔴 Problem it Solves
Real data is messy: PDFs have columns, headers and scanned images; CSV rows lose meaning without column names; web pages have menus and ads; databases have normalised tables. Feeding raw bytes or badly extracted text gives garbage chunks, and "garbage in, garbage out" ruins retrieval.

## 🔴 यह क्यों बना? (Hindi)
असली data गंदा होता है: PDFs में columns, headers और scanned images; CSV rows बिना column names के अर्थहीन; web pages में menu और ads; databases में normalised tables। Raw bytes या खराब extracted text से garbage chunks बनते हैं और "garbage in, garbage out" retrieval बिगाड़ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the loader for the source type (PDF/CSV/HTML/SQL)
Step 2 → Read raw content (file, URL, query result)
Step 3 → Extract text: PDF per page (OCR if scanned), HTML main content only, CSV row -> "col: value" lines
Step 4 → Clean: strip boilerplate, fix encoding, normalise whitespace
Step 5 → Attach metadata: source, page/row, loaded_at, content type
Step 6 → Emit a list of Document(page_content, metadata)
Step 7 → Handle errors per item (bad page, 404, bad row) without stopping the batch
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Source type के हिसाब से loader चुनो (PDF/CSV/HTML/SQL)
Step 2 → Raw content पढ़ो (file, URL, query result)
Step 3 → Text निकालो: PDF page-wise (scanned हो तो OCR), HTML सिर्फ main content, CSV row -> "col: value"
Step 4 → Clean: boilerplate हटाओ, encoding ठीक करो, whitespace normalise करो
Step 5 → Metadata जोड़ो: source, page/row, loaded_at, content type
Step 6 → Document(page_content, metadata) की list लौटाओ
Step 7 → हर item की error अलग संभालो (bad page, 404, bad row), पूरा batch न रुके
```

---

## 🟡 Real World Example
**Tariff Classification System**: Sources are (1) the official tariff PDF (per-page text, page number in metadata), (2) a CSV of duty rates (each row becomes "hs_code: 8518.30; description: ...; duty: 0"), (3) the customs website for circulars (main article only), (4) a Postgres table of past classification decisions (one row = one Document).
**Zomato AI**: Menus come from a database, reviews from a CSV, and blog posts from the web.

## 🟡 Real Example Hindi mein
**Tariff System**: Sources: (1) official tariff PDF (page-wise text, metadata में page number), (2) duty rates की CSV (हर row "hs_code: 8518.30; description: ...; duty: 0"), (3) circulars के लिए customs website (सिर्फ main article), (4) पुराने classification decisions की Postgres table (एक row = एक Document)।
**Zomato AI**: Menus database से, reviews CSV से, blog posts web से।

---

## 💻 Code Example — Basic
```python
# Standard-library loaders: CSV, HTML text, SQLite (PDF shown with pypdf in Advanced)
import csv
import io
import sqlite3
from html.parser import HTMLParser
from typing import Dict, List

Doc = Dict[str, object]  # {"page_content": str, "metadata": dict}

def load_csv(text: str, source: str) -> List[Doc]:
    """Each CSV row becomes 'col: value' lines so the meaning survives chunking."""
    docs: List[Doc] = []  # output
    for i, row in enumerate(csv.DictReader(io.StringIO(text))):  # header-aware reader
        content = "; ".join(f"{k}: {v}" for k, v in row.items())  # keep column names
        docs.append({"page_content": content, "metadata": {"source": source, "row": i}})
    return docs

class _TextExtractor(HTMLParser):
    """Collect visible text, skipping script/style/nav."""
    def __init__(self) -> None:
        super().__init__(); self.parts: List[str] = []; self.skip = 0  # state
    def handle_starttag(self, tag, attrs): self.skip += tag in ("script", "style", "nav")  # enter skip zone
    def handle_endtag(self, tag): self.skip -= tag in ("script", "style", "nav")  # leave skip zone
    def handle_data(self, data): 
        if not self.skip and data.strip(): self.parts.append(data.strip())  # keep visible text

def load_html(html: str, source: str) -> List[Doc]:
    """Strip tags and boilerplate."""
    p = _TextExtractor(); p.feed(html)  # parse
    return [{"page_content": " ".join(p.parts), "metadata": {"source": source}}]

def load_sql(conn: sqlite3.Connection) -> List[Doc]:
    """One DB row = one document."""
    cur = conn.execute("SELECT id, product, hs_code FROM decisions")  # query
    return [{"page_content": f"product: {p}; hs_code: {h}", "metadata": {"source": "db", "id": i}}
            for i, p, h in cur.fetchall()]

if __name__ == "__main__":
    print(load_csv("hs_code,duty\n8518.30,0\n6403.99,20", "rates.csv"))  # CSV
    print(load_html("<nav>menu</nav><p>Circular 12: duty cut</p>", "web"))  # HTML
    db = sqlite3.connect(":memory:")  # temp DB
    db.execute("CREATE TABLE decisions(id INTEGER, product TEXT, hs_code TEXT)")
    db.execute("INSERT INTO decisions VALUES (1, 'earbuds', '8518.30')")
    print(load_sql(db))  # SQL
```

## 💻 Code Example — Advanced
```python
# Async multi-source loader: per-item error isolation, retries for web, PDF via pypdf (pip install pypdf httpx)
import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("loaders")  # logger

@dataclass
class Document:
    page_content: str  # extracted text
    metadata: dict[str, Any] = field(default_factory=dict)  # provenance

def load_pdf(path: str) -> list[Document]:
    """Per-page extraction; a bad page is logged and skipped."""
    from pypdf import PdfReader  # imported lazily so other loaders work without it
    docs: list[Document] = []  # output
    reader = PdfReader(path)  # open file
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()  # may be empty for scanned pages
        except Exception:
            logger.exception("page %d failed in %s", i, path); continue
        if not text:  # likely scanned -> needs OCR
            logger.warning("page %d has no text layer (scan?)", i); continue
        docs.append(Document(text, {"source": Path(path).name, "page": i}))
    return docs

async def load_web(url: str, retries: int = 3) -> list[Document]:
    """Fetch a URL with retry/backoff and return its text (use trafilatura/bs4 for cleaner extraction)."""
    import httpx  # async HTTP client
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for attempt in range(retries):
            try:
                r = await client.get(url)  # request
                r.raise_for_status()  # 4xx/5xx -> exception
                return [Document(r.text, {"source": url, "status": r.status_code})]
            except httpx.HTTPError as exc:
                logger.warning("%s attempt %d: %r", url, attempt + 1, exc)
                await asyncio.sleep(2 ** attempt)  # backoff
    return []  # give up quietly; caller records failure

async def load_all(pdfs: list[str], urls: list[str]) -> list[Document]:
    loop = asyncio.get_running_loop()  # to run blocking PDF code in threads
    pdf_jobs = [loop.run_in_executor(None, load_pdf, p) for p in pdfs]  # CPU/IO blocking -> thread pool
    web_jobs = [load_web(u) for u in urls]  # native async
    results = await asyncio.gather(*pdf_jobs, *web_jobs, return_exceptions=True)  # never fail all
    docs: list[Document] = []
    for r in results:
        if isinstance(r, Exception):
            logger.error("loader error: %r", r)  # record and continue
        else:
            docs.extend(r)
    return docs
```

---

## 🟠 FastAPI Integration
Accept uploads with `UploadFile`, validate type and size, save to a temp path, run the loader in a thread (blocking PDF parsing must not block the event loop) and return a summary.

```python
# FastAPI upload endpoint that loads a PDF
import tempfile
from fastapi import FastAPI, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

app = FastAPI()  # app
MAX_BYTES = 20 * 1024 * 1024  # 20 MB limit

@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if file.content_type != "application/pdf":  # type check
        raise HTTPException(status_code=415, detail="PDF only")
    data = await file.read()  # read bytes
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file too large")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:  # temp file
        tmp.write(data); tmp.flush()
        docs = await run_in_threadpool(load_pdf, tmp.name)  # load_pdf from Advanced example
    return {"pages_loaded": len(docs), "chars": sum(len(d.page_content) for d in docs)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has loaders with the same `Document` shape: `PyPDFLoader`, `CSVLoader`, `WebBaseLoader`, `SQLDatabaseLoader` (community). All expose `.load()` and `.lazy_load()` (memory-friendly iterator). Details in the next topic (192).

```python
# LangChain loaders (needs langchain-community, pypdf, beautifulsoup4)
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, WebBaseLoader

# pdf_docs = PyPDFLoader("tariff.pdf").load()  # one Document per page, metadata has page
# csv_docs = CSVLoader("rates.csv").load()  # one Document per row
# web_docs = WebBaseLoader("https://example.com/circular").load()  # page text
# for d in PyPDFLoader("big.pdf").lazy_load(): ...  # stream, low memory
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loading CSV rows as bare values, so the column meaning is lost.
✅ Correct: Include column names in the text.

```python
# Wrong
content = ",".join(row.values())      # "8518.30,0" -> what is 0?
# Right
content = "; ".join(f"{k}: {v}" for k, v in row.items())   # "hs_code: 8518.30; duty: 0"
```

❌ Mistake 2: Assuming every PDF has a text layer.
✅ Correct: Detect empty pages and route them to OCR (e.g., Tesseract, AWS Textract, Azure Document Intelligence).

```python
# Wrong
text = page.extract_text()      # "" for scanned page -> silently empty index
# Right
text = page.extract_text() or ocr(page_image)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your tariff PDF has a table of HS codes and rates. After loading and chunking, the bot mixes up rates between rows. Why, and how to fix it?"

**Answer**: Plain text extraction flattens tables and loses row/column alignment, and fixed-size chunking can split a row or separate headers from values. Fixes: use a table-aware parser (pdfplumber, Camelot, Unstructured, Azure Document Intelligence), convert each table row to a self-describing sentence ("HS 8518.30 earphones: duty 0 percent"), keep the header context in each chunk, and chunk by row. Verify by inspecting loaded text, not by assuming.

---

## ⚫ Interview Questions + Answers

Q1: What is a Document in RAG frameworks?
A1: An object with `page_content` (text) and `metadata` (dictionary: source, page, etc.).

Q2: Why keep metadata at load time?
A2: For citations, filters, access control and later updates/deletes; it is cheapest to attach where the context is known.

Q3: How do you handle scanned PDFs?
A3: Detect pages with no text and run OCR, or use a layout-aware cloud service; check OCR confidence and store it in metadata.

Q4: How do you load a huge CSV without running out of memory?
A4: Stream with `lazy_load()` or pandas `chunksize`, and index in batches.

Q5: How do you load a website safely and politely?
A5: Respect `robots.txt` and terms, rate-limit, set a user agent, extract main content only (trafilatura/readability), dedupe by URL hash, handle redirects and timeouts, and re-crawl on a schedule using ETag/Last-Modified.

---

## 🔷 When to Use + When Not to Use
✅ Use custom/robust loaders when:
- Sources are messy (tables, scans, dynamic pages)
- You need provenance for citations and compliance

❌ Avoid building your own when:
- A maintained loader covers the format (use LangChain/LlamaIndex/Unstructured)
- Data is already clean text in a database

---

## 📊 Visual Diagram
```
 PDF ───► page text (+OCR) ─┐
 CSV ───► "col: value" rows ─┤
 Web ───► main content only ─┼──► Document(page_content, metadata) ──► Cleaner ──► Splitter
 DB  ───► row -> sentence ───┘                                         (errors logged, batch continues)
```

---

## 💰 Cost Impact
Loading itself costs no tokens, but its quality drives later costs. Boilerplate (menus, headers, repeated disclaimers) becomes chunks you pay to embed and later pay to send to the LLM. OCR/cloud parsers charge per page (roughly 1-15 USD per 1000 pages).
Optimize: strip boilerplate before chunking, dedupe repeated text, OCR only pages with no text layer, cache parsed output by file hash.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Loader | Reads a source into Documents | Source से Documents बनाने वाला |
| Document | Text plus metadata object | Text + metadata object |
| OCR | Image to text | Image से text निकालना |
| lazy_load | Stream documents one by one | एक-एक करके load करना |
| Boilerplate | Repeated non-content text | बार-बार आने वाला बेकार text |
| Provenance | Where data came from | Data कहाँ से आया |

---

## ⚡ 3-Line Summary
English: Loaders turn PDF, CSV, web and DB data into uniform Documents with metadata.
Handle tables, scans and boilerplate carefully because bad loading ruins retrieval.
Isolate errors per item and stream large sources.
Hindi: Loaders PDF, CSV, web और DB data को metadata वाले uniform Documents में बदलते हैं।
Tables, scans और boilerplate ध्यान से संभालो क्योंकि खराब loading retrieval बिगाड़ देती है।
हर item की error अलग रखो और बड़े sources stream करो।

---

## ➡️ Next Topic
**192. LangChain Document Loaders**: the ready-made loader classes and how to customise them.
