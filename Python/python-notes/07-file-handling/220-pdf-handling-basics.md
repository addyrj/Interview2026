---

# 220. PDF Handling Basics
# हिंदी में: PDF Handling Basics (PDF पढ़ना, merge और split करना)

---

## 🔵 Simple Definition (English)
Python has no built-in PDF support, but the pure-Python `pypdf` package (`pip install pypdf`) can read text and metadata, merge, split, rotate and encrypt PDFs. To create PDFs from scratch use `reportlab` or `fpdf2`; for scanned images you need OCR (`pytesseract`).

## 🔵 सरल परिभाषा (Hindi)
Python में PDF का built-in support नहीं है, पर pure-Python `pypdf` package (`pip install pypdf`) text और metadata पढ़ सकता है, PDFs को merge, split, rotate और encrypt कर सकता है। नई PDF बनाने के लिए `reportlab` या `fpdf2` इस्तेमाल करें; scanned images के लिए OCR (`pytesseract`) चाहिए।

---

## 🔴 Problem it Solves
PDF is a print format, not a data format: text is stored as positioned glyphs, not paragraphs, and many PDFs are just photos of paper. Businesses still receive invoices, resumes and bank statements as PDF, so code must pull out the text, join or split documents and handle broken or locked files.

## 🔴 यह क्यों बना? (Hindi)
PDF print का format है, data का नहीं: text positioned glyphs के रूप में होता है, paragraphs के रूप में नहीं, और कई PDFs काग़ज़ की photo भर होती हैं। फिर भी businesses को invoices, resumes और bank statements PDF में ही मिलते हैं, इसलिए code को text निकालना, documents जोड़ना/बाँटना और टूटी या locked files संभालना आना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → PdfReader(path or BytesIO) parses the file structure (xref table)
Step 2 → reader.pages is a list-like of Page objects (0-based)
Step 3 → page.extract_text() rebuilds text from drawing commands (may be '' for scans)
Step 4 → PdfWriter() collects pages: add_page(), append(file), add_metadata()
Step 5 → writer.write(file_or_BytesIO) saves a new PDF; encrypt('pw') locks it
Step 6 → Handle PdfReadError, encrypted files, and size/page limits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → PdfReader(path या BytesIO) file की structure (xref table) parse करता है
Step 2 → reader.pages Page objects की list जैसी चीज़ है (0 से शुरू)
Step 3 → page.extract_text() drawing commands से text बनाता है (scan हो तो '' मिल सकता है)
Step 4 → PdfWriter() pages इकट्ठा करता है: add_page(), append(file), add_metadata()
Step 5 → writer.write(file_or_BytesIO) नई PDF save करता है; encrypt('pw') उसे lock करता है
Step 6 → PdfReadError, encrypted files और size/page limits संभालो
```

---

## 🟡 Real World Example
A loan app extracts the invoice number and amount from uploaded PDFs with a regex on `extract_text()`. An HR tool merges 'offer letter + policy + NDA' into one PDF. A document-AI (RAG) pipeline reads PDF pages, splits text into chunks and embeds them. A compliance job password-protects exported statements.

## 🟡 Real Example Hindi mein
Loan app upload हुई PDFs से `extract_text()` पर regex लगाकर invoice number और amount निकालता है। HR tool 'offer letter + policy + NDA' को एक PDF में merge करता है। Document-AI (RAG) pipeline PDF pages पढ़कर text को chunks में बाँटता और embed करता है। Compliance job exported statements पर password लगाती है।

---

## 💻 Code Example — Basic
```python
# helper: build a tiny valid 2-page PDF by hand (no reportlab needed)
def make_pdf(pages: list[str]) -> bytes:
    objs: list[bytes] = []
    n = len(pages)
    kids = " ".join(f"{3+2*i} 0 R" for i in range(n))
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, t in enumerate(pages):
        content = f"BT /F1 18 Tf 72 720 Td ({t}) Tj ET".encode()
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4+2*i} 0 R /Resources << /Font << /F1 {3+2*n} 0 R >> >> >>".encode())
        objs.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n"); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for o in offs: out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    return bytes(out)


import io
from pypdf import PdfReader, PdfWriter  # pip install pypdf

data: bytes = make_pdf(["Invoice 101", "Total 500"])
reader = PdfReader(io.BytesIO(data))  # accepts path, file or BytesIO
print(len(reader.pages))
print(reader.pages[0].extract_text())
print([p.extract_text() for p in reader.pages])
print(reader.pages[0].mediabox.width, reader.pages[0].mediabox.height)
w = PdfWriter()  # new PDF
w.add_page(reader.pages[1])  # copy page 2 only
w.add_metadata({"/Title": "Only totals"})
buf = io.BytesIO(); w.write(buf)
r2 = PdfReader(io.BytesIO(buf.getvalue()))
print(len(r2.pages), r2.metadata.title)
print(reader.is_encrypted)
```

**Real output** (Python 3.13.3):
```
2
Invoice 101
['Invoice 101', 'Total 500']
612 792
1 Only totals
False
```

Note: this note builds a tiny valid PDF with the helper `make_pdf` (about 20 lines) so every example is self-contained. With real files just write `PdfReader('your.pdf')`. Stderr warnings from pypdf about broken input (like the `EOF marker not found` lines) are logging output and are not shown in the stdout block above.

## 💻 Code Example — Advanced
```python
# helper: build a tiny valid 2-page PDF by hand (no reportlab needed)
def make_pdf(pages: list[str]) -> bytes:
    objs: list[bytes] = []
    n = len(pages)
    kids = " ".join(f"{3+2*i} 0 R" for i in range(n))
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, t in enumerate(pages):
        content = f"BT /F1 18 Tf 72 720 Td ({t}) Tj ET".encode()
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4+2*i} 0 R /Resources << /Font << /F1 {3+2*n} 0 R >> >> >>".encode())
        objs.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n"); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for o in offs: out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    return bytes(out)


from __future__ import annotations
import io, re, tempfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


def extract_text(path: Path, max_pages: int = 50) -> str:
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:  # password-protected
            raise PermissionError("PDF is encrypted")
        if len(reader.pages) > max_pages:  # guard resources
            raise ValueError("too many pages")
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except PdfReadError as exc:
        raise ValueError(f"not a valid PDF: {exc}") from exc


def merge(paths: list[Path], out: Path) -> int:
    w = PdfWriter()
    for p in paths:
        w.append(str(p))  # append whole file
    with out.open("wb") as fh:
        w.write(fh)
    return len(w.pages)


def split_pages(path: Path, outdir: Path) -> list[Path]:
    reader = PdfReader(path); res = []
    for i, page in enumerate(reader.pages, 1):
        w = PdfWriter(); w.add_page(page)
        o = outdir / f"{path.stem}_p{i}.pdf"
        with o.open("wb") as fh:
            w.write(fh)
        res.append(o)
    return res


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "a.pdf").write_bytes(make_pdf(["Invoice INV-2024-0042", "Amount Rs 1500"]))
    (d / "b.pdf").write_bytes(make_pdf(["Appendix"]))
    text = extract_text(d / "a.pdf")
    print(re.search(r"INV-\d{4}-\d{4}", text).group())
    print(merge([d / "a.pdf", d / "b.pdf"], d / "m.pdf"))
    print([p.name for p in split_pages(d / "m.pdf", d)])
    enc = PdfWriter(); enc.append(str(d / "b.pdf")); enc.encrypt("secret")
    with (d / "e.pdf").open("wb") as fh: enc.write(fh)
    try: extract_text(d / "e.pdf")
    except PermissionError as e: print(e)
    (d / "bad.pdf").write_text("hello")
    try: extract_text(d / "bad.pdf")
    except ValueError as e: print("ValueError", str(e)[:30])
```

**Real output** (Python 3.13.3):
```

```

Warnings such as `invalid pdf header` / `EOF marker not found` are printed by pypdf to the log (stderr) for the corrupt test file. A wrapped `ValueError` is better than leaking library errors to callers. `extract_text()` returns an empty string for scanned pages, which is the hint to use OCR.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (pip install pypdf)
from pypdf import PdfReader
reader = PdfReader("invoice.pdf")
print(len(reader.pages))
text = reader.pages[0].extract_text()
```

```javascript
// JavaScript (npm i pdf-parse   |  pdfjs-dist  |  pdf-lib)
const pdf = require("pdf-parse");
const data = await pdf(require("fs").readFileSync("invoice.pdf"));
console.log(data.numpages);
console.log(data.text);      // all pages as one string
```

Both ecosystems use third-party libraries. Node: `pdf-parse`/`pdfjs-dist` for reading, `pdf-lib` for editing/merging. Python: `pypdf` for read/edit, `pdfplumber` for tables, `reportlab`/`fpdf2` to create, `PyMuPDF (fitz)` for speed. In both, extracted text order can be messy.

---

## 🟠 FastAPI Connection
For a PDF upload endpoint, read the `UploadFile` bytes into `BytesIO`, parse with `PdfReader`, and convert `PdfReadError` into HTTP 422. PDF parsing is CPU bound, so declare the endpoint with plain `def` (threadpool) or use `run_in_threadpool`, and cap upload size and page count. To return a generated PDF use `Response(content=bytes, media_type='application/pdf')`.

```python
# helper: build a tiny valid 2-page PDF by hand (no reportlab needed)
def make_pdf(pages: list[str]) -> bytes:
    objs: list[bytes] = []
    n = len(pages)
    kids = " ".join(f"{3+2*i} 0 R" for i in range(n))
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, t in enumerate(pages):
        content = f"BT /F1 18 Tf 72 720 Td ({t}) Tj ET".encode()
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4+2*i} 0 R /Resources << /Font << /F1 {3+2*n} 0 R >> >> >>".encode())
        objs.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n"); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for o in offs: out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    return bytes(out)


import io
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.testclient import TestClient
from pypdf import PdfReader
from pypdf.errors import PdfReadError
app = FastAPI()
@app.post("/pdf/text")
async def pdf_text(file: UploadFile) -> dict[str, object]:
    raw = await file.read()
    try:
        r = PdfReader(io.BytesIO(raw))
        return {"pages": len(r.pages), "text": r.pages[0].extract_text()}
    except PdfReadError:
        raise HTTPException(422, "invalid pdf")
c = TestClient(app)
print(c.post("/pdf/text", files={"file": ("a.pdf", make_pdf(["Hi PDF"]), "application/pdf")}).json())
print(c.post("/pdf/text", files={"file": ("a.pdf", b"junk")}).status_code)
```

**Real output** (Python 3.13.3):
```
{'pages': 1, 'text': 'Hi PDF'}
422
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming extract_text works for scanned PDFs
```python
# Wrong - returns '' for image-only pages, silently
text = page.extract_text()
save(text)

# Right - detect and route to OCR
text = page.extract_text() or ""
if not text.strip():
    text = run_ocr(page)       # pytesseract / cloud OCR
```

❌ Mistake 2: Ignoring encrypted or corrupt PDFs
```python
# Wrong - crashes with a library-specific exception
PdfReader(path).pages[0]

# Right
reader = PdfReader(path)
if reader.is_encrypted:
    reader.decrypt(password)      # or reject with a clear error
```

❌ Mistake 3: Using the old PyPDF2 API names
```python
# Wrong - PyPDF2 is deprecated/merged into pypdf; PdfFileReader is removed
from PyPDF2 import PdfFileReader

# Right
from pypdf import PdfReader, PdfWriter
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import io, sys
sys.path.insert(0, ".")
from mkpdf import make_pdf
from pypdf import PdfReader
r = PdfReader(io.BytesIO(make_pdf(["One", "Two"])))
print(len(r.pages), r.pages[-1].extract_text(), len(r.pages[0:5]))
try: r.pages[2]
except IndexError as e: print("IndexError")
```

**Answer** (real run on Python 3.13.3):
```
2 Two 2
IndexError
```
`pages` is zero-based and supports negative indexes and slices (`pages[-1]` is the last page, a slice just returns the available pages). Reading past the end raises `IndexError`. PDF page numbers shown to users start at 1.

---

## ⚫ Interview Questions + Answers

Q1: Why is extracting text from PDFs unreliable?
A1: PDF stores glyph positions, not paragraphs, so reading order, columns, tables and hyphenation can break. Scanned PDFs have no text layer at all. Use `pdfplumber` for tables and OCR for scans.

Q2: pypdf vs PyPDF2 vs pdfplumber vs PyMuPDF?
A2: pypdf is the maintained successor of PyPDF2 (merge/split/read). pdfplumber is built on pdfminer and is best for tables. PyMuPDF is fastest and can render pages to images (AGPL license).

Q3: How do you merge PDFs?
A3: `writer = PdfWriter(); writer.append('a.pdf'); writer.append('b.pdf'); writer.write('out.pdf')`.

Q4: How do you create a PDF?
A4: `reportlab` (canvas/platypus), `fpdf2`, or render HTML with WeasyPrint/Playwright. pypdf only manipulates existing PDFs.

Q5: How do you handle large PDFs in a web service?
A5: Stream the upload to a temp file, limit pages and size, process in a worker/background task, and avoid reading all pages into memory at once.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Extracting text/metadata from digital PDFs (invoices, reports)
- Merging, splitting, rotating or encrypting documents
- Feeding documents into a search or RAG pipeline

❌ Avoid when:
- PDFs are scans (use OCR) or you need exact table structure (use pdfplumber)
- You must generate pretty documents (use reportlab / HTML-to-PDF)
- Files are untrusted and huge without limits

---

## 📊 Visual Diagram

```
PdfReader("a.pdf")                         PdfWriter()
   |                                          ^   |
   +--> pages[0] --extract_text()--> "Invoice..."  |
   +--> pages[1] ----add_page()--------------------+
                                                   v
        merge: writer.append("a.pdf"), writer.append("b.pdf")
        write: writer.write("out.pdf")  (encrypt("pw") optional)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PDF | Print-layout document format | print वाला document format |
| pypdf | Pure-Python PDF library | pure-Python PDF library |
| Page | One PDF page object | PDF का एक page |
| OCR | Reading text from images | image से text पढ़ना |
| Encrypted | Password protected | password से सुरक्षित |
| Metadata | Title, author, dates | title, author, dates |

---

## ⚡ 3-Line Summary
English: Use `pypdf` to read page text, merge, split and encrypt PDFs, wrapping `PdfReadError` and encrypted files in clear errors. Text extraction fails on scans (use OCR) and tables (use pdfplumber).
Hindi: PDF का text पढ़ने, merge, split और encrypt करने के लिए `pypdf` इस्तेमाल करें, और `PdfReadError` व encrypted files को साफ़ errors में बदलें। Scans पर text extraction नहीं चलता (OCR लें) और tables के लिए pdfplumber बेहतर है।

---

## ➡️ Next Topic
**221. Concurrency vs Parallelism** — the first topic of the async and concurrency chapter.
