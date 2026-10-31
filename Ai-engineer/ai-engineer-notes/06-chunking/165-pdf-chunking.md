---

# 165. PDF Chunking
# हिंदी में: PDF Chunking (PDF को chunks में बाँटना)

---

## 🔵 Simple Definition (English)
PDF chunking is extracting text from a PDF and cutting it into chunks while keeping page numbers, headings and tables. A PDF is a "printed page" format, not a "text" format, so extraction is the hard part. Good PDF chunking keeps the page number so answers can cite "page 42".

## 🔵 सरल परिभाषा (Hindi)
PDF chunking में PDF से text निकालकर उसे chunks में बाँटा जाता है, और page number, headings, tables सुरक्षित रखे जाते हैं। PDF "printed page" format है, "text" format नहीं, इसलिए extraction ही सबसे मुश्किल हिस्सा है। अच्छी chunking में page number रहता है ताकि जवाब में "page 42" cite हो सके।

---

## 🔴 Problem it Solves
- PDFs have no tags: no `<h2>`, only text at x/y positions.
- Two-column layouts get read in the wrong order (left line, right line, left line).
- Headers, footers and page numbers repeat on every page and pollute chunks.
- Scanned PDFs have no text at all - only images (need OCR).
- A sentence often runs across a page break.

## 🔴 यह क्यों बना? (Hindi)
- PDF में tags नहीं होते, सिर्फ x/y positions पर text होता है।
- Two-column layout में पढ़ने का order गलत हो जाता है।
- Header, footer, page number हर page पर दोहराते हैं और chunks गंदे करते हैं।
- Scanned PDF में text नहीं, सिर्फ image होती है (OCR चाहिए)।
- एक वाक्य अक्सर page break के पार चला जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect type: text PDF or scanned PDF (extracted text almost empty = scanned)
Step 2 → Extract text per page (pypdf / pdfplumber / PyMuPDF); OCR if scanned
Step 3 → Clean: remove repeating headers/footers, page numbers, hyphenation
Step 4 → Join pages into one stream but remember page boundaries (offset -> page)
Step 5 → Split by headings / paragraphs first, then by size (recursive)
Step 6 → Tag each chunk with page_start, page_end, source, section
Step 7 → Extract tables separately (pdfplumber) and keep each as one chunk
Step 8 → Embed + store; at answer time show "Source: file, page N"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Type पहचानो: text PDF या scanned PDF
Step 2 → हर page का text निकालो; scanned हो तो OCR
Step 3 → Clean करो: header/footer, page number हटाओ
Step 4 → Pages जोड़ो पर page boundary याद रखो
Step 5 → पहले heading/paragraph से, फिर size से split
Step 6 → हर chunk पर page_start, page_end, source लगाओ
Step 7 → Tables अलग निकालो, हर table एक chunk
Step 8 → Embed + store; जवाब में "page N" दिखाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 300-page customs tariff PDF. Every page has the footer "Customs Tariff 2025 - Page 87". If not removed, 300 chunks contain this footer and match every query about "tariff". After cleaning and chunking with page metadata, the answer says "HS 8517.13 - 10% duty (page 87)", and an officer can verify the page.

**Amazon style**: Seller policy PDFs. A support bot answers "return window for electronics?" and cites "Policy PDF, page 12".

## 🟡 Real Example Hindi mein
**Tariff System**: 300 page का customs tariff PDF। हर page पर footer "Customs Tariff 2025 - Page 87" है। हटाया नहीं तो 300 chunks में यह footer होगा। Clean करने के बाद जवाब में "page 87" cite होता है और officer verify कर सकता है।

**Amazon**: Seller policy PDF। Bot जवाब देता है और "Policy PDF, page 12" cite करता है।

---

## 💻 Code Example — Basic
```python
# Basic PDF-style chunking in pure Python: pages are a list of strings.
# (In real life the list comes from pypdf; here we simulate it so it runs anywhere.)
import re  # regex for cleaning

pages = [  # fake extracted pages
    "Customs Tariff 2025\nChapter 85 Electrical machinery.\nSmartphones: 10 percent duty.\nPage 1",
    "Customs Tariff 2025\nMicrophones: 7.5 percent duty.\nBatteries: 20 percent duty.\nPage 2",
]  # same footer/header on every page

def clean(page: str) -> str:  # remove header and page-number lines
    lines = page.splitlines()  # split into lines
    keep = [ln for ln in lines  # filter lines
            if not ln.startswith("Customs Tariff")  # drop repeating header
            and not re.fullmatch(r"Page \d+", ln.strip())]  # drop page number
    return "\n".join(keep)  # join back

def chunk_pages(pages: list[str], max_chars: int = 80) -> list[dict]:  # page-aware chunker
    chunks: list[dict] = []  # output
    for page_no, raw in enumerate(pages, start=1):  # 1-based page numbers
        text = clean(raw)  # clean the page
        buf = ""  # current chunk text
        for line in text.splitlines():  # go line by line
            if len(buf) + len(line) > max_chars and buf:  # chunk is full
                chunks.append({"text": buf.strip(), "page": page_no})  # save it
                buf = ""  # start a new one
            buf += line + "\n"  # add the line
        if buf.strip():  # leftover text
            chunks.append({"text": buf.strip(), "page": page_no})  # save it
    return chunks  # all chunks

for c in chunk_pages(pages):  # print result
    print(c)  # each chunk has its page number
```

## 💻 Code Example — Advanced
```python
# Production PDF chunker: pypdf extraction, scanned-PDF detection, repeated-line removal,
# page metadata, async wrapper. pip install pypdf  (imported lazily so syntax check is cheap)
from __future__ import annotations  # modern annotations

import asyncio  # async version
import logging  # logging
from collections import Counter  # count repeated lines
from dataclasses import dataclass  # data container
from pathlib import Path  # file paths

logger = logging.getLogger(__name__)  # logger


@dataclass
class PdfChunk:  # one chunk
    text: str  # content
    page_start: int  # first page it touches
    page_end: int  # last page it touches
    source: str  # file name


class ScannedPdfError(RuntimeError):  # raised when OCR is needed
    pass


def extract_pages(path: Path) -> list[str]:  # read text page by page
    try:  # import may fail if pypdf is missing
        from pypdf import PdfReader  # real library
    except ImportError as exc:  # missing dependency
        raise RuntimeError("pip install pypdf") from exc  # clear message
    if not path.exists():  # validate input
        raise FileNotFoundError(path)  # nicer error
    reader = PdfReader(str(path))  # open the PDF
    pages = [(p.extract_text() or "") for p in reader.pages]  # text per page
    if sum(len(p) for p in pages) < 50 * max(1, len(pages)):  # almost no text
        raise ScannedPdfError(f"{path.name} looks scanned - run OCR first")  # need OCR
    return pages  # extracted pages


def strip_repeats(pages: list[str], min_share: float = 0.6) -> list[str]:  # remove header/footer
    counts: Counter[str] = Counter()  # line -> pages containing it
    for p in pages:  # each page
        counts.update({ln.strip() for ln in p.splitlines() if ln.strip()})  # unique lines
    limit = max(2, int(len(pages) * min_share))  # appears on most pages
    repeated = {ln for ln, n in counts.items() if n >= limit}  # header/footer lines
    return ["\n".join(ln for ln in p.splitlines() if ln.strip() not in repeated)
            for p in pages]  # pages without repeats


def chunk_pdf(path: Path, size: int = 1000, overlap: int = 100) -> list[PdfChunk]:  # main API
    if overlap >= size:  # sanity check
        raise ValueError("overlap must be smaller than size")  # fail fast
    pages = strip_repeats(extract_pages(path))  # extract + clean
    text, owner = "", []  # joined text and char->page map
    for no, page in enumerate(pages, start=1):  # each page
        text += page + "\n"  # append text
        owner += [no] * (len(page) + 1)  # page number per char
    out: list[PdfChunk] = []  # result list
    start = 0  # window start
    while start < len(text):  # slide window
        end = min(start + size, len(text))  # window end
        body = text[start:end].strip()  # chunk text
        if body:  # skip empty
            out.append(PdfChunk(body, owner[start], owner[end - 1], path.name))  # save
        if end == len(text):  # reached the end
            break  # stop
        start = end - overlap  # step forward with overlap
    return out  # chunks


async def chunk_pdf_async(path: Path) -> list[PdfChunk]:  # async wrapper
    return await asyncio.to_thread(chunk_pdf, path)  # CPU/IO off the event loop


if __name__ == "__main__":  # quick offline demo of the pure-Python helpers
    demo = ["Header\nA one\nPage", "Header\nB two\nPage", "Header\nC three\nPage"]  # fake pages
    print(strip_repeats(demo))  # header and 'Page' lines are removed
```

---

## 🟠 FastAPI Integration
Upload endpoint: save the PDF to a temp file, chunk it in a thread, return chunk count and a preview. Reject scanned PDFs with a clear 422 so the client can route them to OCR.

```python
import tempfile  # temp files
from pathlib import Path  # paths
from fastapi import FastAPI, File, HTTPException, UploadFile  # FastAPI parts

app = FastAPI()  # app


@app.post("/ingest/pdf")  # route
async def ingest_pdf(file: UploadFile = File(...)) -> dict:  # upload handler
    if not (file.filename or "").lower().endswith(".pdf"):  # check extension
        raise HTTPException(400, "only .pdf allowed")  # bad file type
    data = await file.read()  # read bytes
    if len(data) > 25_000_000:  # 25 MB cap
        raise HTTPException(413, "file too large")  # too big
    with tempfile.TemporaryDirectory() as tmp:  # auto-cleanup folder
        path = Path(tmp) / file.filename  # target path
        path.write_bytes(data)  # save upload
        try:  # chunk it
            chunks = await chunk_pdf_async(path)  # async chunking
        except ScannedPdfError as exc:  # needs OCR
            raise HTTPException(422, str(exc))  # tell the client
    return {"chunks": len(chunks), "first": chunks[0].text[:200] if chunks else ""}  # summary
```

---

## 🔗 LangChain / LangGraph Connection
`PyPDFLoader` returns one `Document` per page with `metadata["page"]`. Pass them to a splitter with `split_documents` - the page metadata is copied to every chunk automatically.

```python
from langchain_community.document_loaders import PyPDFLoader  # loader (needs pypdf)
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

pages = PyPDFLoader("tariff_2025.pdf").load()  # list[Document], metadata has page
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)  # size rules
chunks = splitter.split_documents(pages)  # keeps metadata["page"]
print(chunks[0].metadata)  # {'source': 'tariff_2025.pdf', 'page': 0}  (0-based!)
# LangGraph: nodes -> load_pdf -> clean -> chunk -> embed, with a conditional edge to an OCR node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not removing headers and footers
✅ Correct: Detect lines that repeat on most pages and drop them.

```python
# Wrong - footer stays in every chunk
chunks = chunk_pages(["Footer\ntext A", "Footer\ntext B"])  # footer pollutes retrieval

# Right - strip repeated lines first
cleaned = strip_repeats(["Footer\ntext A", "Footer\ntext B", "Footer\ntext C"])  # footer gone
```

❌ Mistake 2: Treating a scanned PDF as text and silently indexing empty strings
✅ Correct: Check extracted text length and send scans to OCR (Tesseract, a vision LLM).

❌ Mistake 3: Losing page numbers, then being unable to cite sources.
✅ Correct: Store `page_start` / `page_end` in metadata (remember pypdf pages are 0-based; users expect 1-based).

---

## 🧠 Tricky Interview Question
**Q**: "A two-column tariff PDF is indexed. Answers mix sentences from the left and right columns. Embedding model and chunk size are fine. What is wrong?"

**Answer**: The extractor reads lines across the full page width, interleaving columns, so chunks contain scrambled text. Fix at extraction, not at chunking: use a layout-aware tool (PyMuPDF blocks, pdfplumber with column crop, Unstructured, or a vision-LLM/document-AI parser) so reading order is correct. Then re-index. Tuning chunk size cannot repair garbled input - "garbage in, garbage out".

---

## ⚫ Interview Questions + Answers

Q1: Why is PDF harder than HTML or Markdown?
A1: PDF stores glyphs at positions, not structure. No headings, paragraphs or reading order are stored, so they must be inferred.

Q2: How do you know a PDF is scanned?
A2: Extracted text is empty or tiny compared to the page count. Then use OCR (Tesseract, cloud OCR or a vision model).

Q3: How do you keep page numbers on chunks?
A3: Keep page-level documents, split each with `split_documents` (metadata copied), or build a char-to-page map when joining pages, like in the advanced example.

Q4: How should tables in PDFs be handled?
A4: Extract with pdfplumber/Camelot/a layout model, keep each table as one chunk, include the caption and header row, optionally convert to markdown or row sentences.

Q5: (Hard) A sentence spans two pages and the answer is cut. How do you fix it?
A5: Join pages into one text stream before splitting (with a page map), use overlap, and fix hyphenation ("classi-\nfication"). Alternatively retrieve neighbour chunks (window retrieval) at query time.

---

## 🔷 When to Use + When Not to Use
✅ Use page-aware PDF chunking when:
- Source documents are PDFs (laws, tariffs, contracts, manuals)
- Users need citations with page numbers
- Tables and headings matter

❌ Avoid when:
- A cleaner source exists (HTML/XML/DOCX of the same document) - use that instead
- The PDF is a scan with poor quality and no OCR budget

---

## 📊 Visual Diagram
```
 PDF file
   │
   ├─ text PDF ──► extract per page ─┐
   │                                  ├─► remove header/footer ─► join + page map
   └─ scanned ───► OCR ──────────────┘                              │
                                                                     ▼
                                      split (heading → paragraph → size + overlap)
                                                                     │
                                  chunk {text, page_start, page_end, source}
                                                                     │
                                                              embed → vector DB
```

---

## 💰 Cost Impact
- Cleaning headers/footers and page numbers removes 2-5% of tokens and, more importantly, removes false matches.
- OCR is the expensive step: cloud OCR is typically billed per page; a vision LLM costs tokens per page image (roughly 1-2K input tokens per page). Run OCR only for scanned PDFs, once, and cache the text.
- Token estimate: a 300-page text PDF is about 150-200K tokens to embed. With a small embedding model this is cents, but sending whole PDFs to a chat model each query would be dollars - so chunk and retrieve.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text extraction | Getting text from PDF | PDF से text निकालना |
| OCR | Image to text | Image से text पढ़ना |
| Layout analysis | Detect columns, tables | Layout समझना |
| Header/footer | Repeating page lines | हर page की repeating lines |
| Page map | Char offset to page number | Offset से page number |
| Hyphenation | Word split across lines | Line के अंत में टूटा शब्द |

---

## ⚡ 3-Line Summary
English: PDF chunking = extract, clean, split, and tag with page numbers. Extraction quality (reading order, OCR, tables) matters more than chunk size. Always strip repeated headers and cite pages.
Hindi: PDF chunking = extract, clean, split और page number लगाना। Extraction की quality (reading order, OCR, tables) chunk size से ज़्यादा ज़रूरी है। Header/footer हटाओ और pages cite करो।

---

## ➡️ Next Topic
**166. chunk_size - How to Choose** - the number every splitter asks for and how to pick it with data.
