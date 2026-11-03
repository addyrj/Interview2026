---

# 585. Build PDF Chat App
# हिंदी में: PDF Chat App बनाना

---

## 🔵 Simple Definition (English)
A PDF chat app extracts text from each page of a PDF, splits it into chunks that remember their page number, finds the chunk that best matches the question, and answers with a page citation like "(page 2)".

## 🔵 सरल परिभाषा (Hindi)
PDF chat app PDF के हर page से text निकालता है, उसे ऐसे chunks में बाँटता है जो अपना page number याद रखते हैं, सवाल से सबसे मिलता chunk ढूँढता है, और "(page 2)" जैसे citation के साथ जवाब देता है।

---

## 🔴 Problem it Solves
Long PDFs (tariff schedules, contracts) cannot be read by hand and often do not fit in one prompt. A plain "chat with PDF" that gives answers without page numbers cannot be verified. Scanned PDFs silently return empty text and the bot then hallucinates.

## 🔴 यह क्यों बना? (Hindi)
लंबे PDFs (tariff schedule, contract) हाथ से पढ़ना मुश्किल है और एक prompt में fit भी नहीं होते। Page number के बिना जवाब verify नहीं हो सकता। Scanned PDF से text खाली आता है और bot hallucinate करने लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → extract_pages(path): read text per page (pypdf), or fall back to FAKE_PAGES offline
Step 2 → If every page is empty -> raise ValueError (scanned PDF, run OCR first)
Step 3 → to_chunks(): split each page separately into 200-char PageChunk(page, text)
Step 4 → ask(): score chunks by word overlap with the question (stand-in for embeddings)
Step 5 → No overlap at all -> "Not found in the PDF."
Step 6 → Else return best chunk text + "(page N)"
Step 7 → achat(): run blocking extraction in asyncio.to_thread
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → extract_pages(): हर page का text पढ़ो (pypdf), offline हो तो FAKE_PAGES
Step 2 → सारे pages खाली हों तो ValueError (scanned PDF, पहले OCR करो)
Step 3 → to_chunks(): हर page को अलग से 200-char PageChunk(page, text) में बाँटो
Step 4 → ask(): सवाल के साथ word overlap से chunks score करो (embeddings का stand-in)
Step 5 → बिल्कुल overlap नहीं -> "Not found in the PDF."
Step 6 → वरना best chunk + "(page N)" लौटाओ
Step 7 → achat(): blocking extraction को asyncio.to_thread में चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: a broker uploads the 400-page customs tariff PDF and asks "What is the duty on laptops?". The app answers "Laptops 0 percent under agreement (page 2)" so the officer can open page 2 and confirm before filing a declaration.

**Other**: Amazon seller-policy PDF bot, Zomato restaurant-contract assistant that always cites the clause page.

## 🟡 Real Example Hindi mein
**Tariff System**: broker 400 page का customs tariff PDF upload करता है और पूछता है "Laptops पर duty क्या है?"। App जवाब देता है "Laptops 0 percent (page 2)", ताकि officer page 2 खोलकर पक्का कर सके।

**Other**: Amazon seller-policy PDF bot, Zomato contract assistant जो हमेशा clause का page बताता है।

---

## 💻 Code Example — Basic
Full solution: `main.py` (offline, uses a built-in fake 3-page PDF).

```python
import re
from dataclasses import dataclass

PAGES = ["Smartphones fall under 8517.13.", "Laptops 0 percent under agreement."]  # fake pages


@dataclass(frozen=True)
class PageChunk:
    page: int      # 1-based page number kept with the text
    text: str


def words(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))          # lowercase word set


chunks = [PageChunk(n, t) for n, t in enumerate(PAGES, start=1)]
q = words("duty on laptops")                            # question words
best = max(chunks, key=lambda c: len(q & words(c.text)))  # most shared words wins
print(best.text, f"(page {best.page})")                 # Laptops 0 percent under agreement. (page 2)
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
Duty rates: smartphones 20 percent. Laptops 0 percent under agreement. (page 2)
Appeals must be filed within 60 days of the assessment notice. (page 3)
```
Excerpt from `main.py` (chunking per page, citation, async wrapper):
```python
import asyncio
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PageChunk:
    page: int
    text: str


def to_chunks(pages: list[str], size: int = 200) -> list[PageChunk]:
    """Chunk each page separately so every chunk keeps its page number."""
    out: list[PageChunk] = []
    for n, text in enumerate(pages, start=1):
        for i in range(0, len(text), size):
            piece = text[i:i + size].strip()
            if piece:                                   # skip blank pieces
                out.append(PageChunk(n, piece))
    return out


def ask(chunks: list[PageChunk], question: str) -> str:
    """Pick best chunk by word overlap; cite the page."""
    q = set(re.findall(r"\w+", question.lower()))
    best = max(chunks, key=lambda c: len(q & set(re.findall(r"\w+", c.text.lower()))))
    if not q & set(re.findall(r"\w+", best.text.lower())):
        return "Not found in the PDF."                  # refuse instead of guessing
    return f"{best.text} (page {best.page})"


async def achat(pages: list[str], question: str) -> str:
    # In main.py extraction itself runs via asyncio.to_thread(extract_pages, path)
    return ask(to_chunks(pages), question)
```

---

## 🟠 FastAPI Integration
Accept an upload, run extraction off the event loop, map scanned-PDF errors to HTTP 422.

```python
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile

from main import achat                                   # our module

app = FastAPI()


@app.post("/pdf/ask")
async def pdf_ask(file: UploadFile, question: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(await file.read())                     # save upload to disk
        tmp.flush()
        try:
            answer = await achat(tmp.name, question)
        except ValueError as e:                          # scanned PDF, no text
            raise HTTPException(status_code=422, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="bad file")
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain gives `PyPDFLoader` (page metadata included), a splitter, a vector store and a retriever. Same idea, real embeddings.

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = PyPDFLoader("tariff.pdf").load()                  # one Document per page, metadata["page"]
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)                  # metadata (page) is preserved
# retriever = vectorstore.as_retriever(); cite chunk.metadata["page"] in the answer
```
In LangGraph: nodes `extract -> retrieve -> answer`, with the page numbers kept in state.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Chunking the whole document text as one string (page numbers are lost).
✅ Correct: chunk page by page, as `to_chunks` does.

```python
# Wrong: "\n".join(pages) then split -> no page info
# Right: PageChunk(page=n, text=piece) for every piece of page n
```

❌ Mistake 2: Ignoring scanned PDFs. `extract_text()` returns empty strings, the bot has no context.
✅ Correct: detect "all pages empty" and raise/route to OCR (as `main.py` does).

❌ Mistake 3: Always answering. Return "Not found in the PDF." when nothing matches.

---

## 🧠 Tricky Interview Question
**Q**: "A fact is split across the end of page 5 and the start of page 6. Your per-page chunks miss it. Fix?"

**Answer**: Per-page chunking trades cross-page context for exact citations. Fix with overlap that crosses the page boundary (append the last N chars of page 5 to page 6's first chunk, citing "pages 5-6"), or retrieve neighbouring chunks (page +/- 1) after the top hit. Do not drop page metadata to solve this.

---

## ⚫ Interview Questions + Answers

Q1: Why keep the page number in each chunk?
A1: So the answer can cite its source and a human can verify it.

Q2: Why `asyncio.to_thread` in `achat`?
A2: PDF parsing is blocking CPU/IO; running it directly would freeze the event loop for other requests.

Q3: How do you detect a scanned PDF?
A3: All extracted page texts are empty/whitespace; `main.py` raises ValueError("no extractable text...") and the caller should run OCR.

Q4: What replaces word-overlap in production?
A4: Embeddings plus a vector store (and often a reranker); the structure (chunks with page metadata, cite page) stays the same.

Q5 (Hard): How do you handle a 2,000 page PDF with many users?
A5: Extract and embed once at upload time (background job), store vectors with page metadata keyed by document id, and at query time only retrieve top-k chunks. Cache by file hash so re-uploads cost nothing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers must be traceable to a page (legal, tariff, compliance)
- Documents are text-based PDFs

❌ Avoid when:
- PDFs are scans without OCR
- Questions need arithmetic over tables (use structured extraction instead)

---

## 📊 Visual Diagram
```
 PDF ─► extract_pages ─► [p1, p2, p3]
                              │  (empty? -> ValueError / OCR)
                              ▼
                 to_chunks: PageChunk(page, text)
                              │
 question ─► ask(): word overlap ─► best chunk
                              │ none -> "Not found in the PDF."
                              ▼
                    "text ... (page N)"
```

---

## 💰 Cost Impact
Extraction and chunking are free (no tokens). Cost comes only from embedding the chunks once and from the final LLM call. Send only top-k chunks (not the whole PDF) to cut input tokens by 10-100x; cache embeddings by file hash.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Small piece of text for retrieval | Text का छोटा टुकड़ा |
| Citation | Source reference like page number | Source का हवाला |
| OCR | Turning scanned images into text | Image से text निकालना |
| Metadata | Extra info stored with a chunk | Chunk के साथ जुड़ी जानकारी |
| to_thread | Run blocking code off the event loop | Blocking code को अलग thread में चलाना |

---

## ⚡ 3-Line Summary
English: Extract per page, chunk per page, and keep page numbers. Answer from the best chunk with a citation, or say not found. Handle scanned PDFs explicitly.
Hindi: हर page से extract और chunk करो और page number साथ रखो। Best chunk से citation के साथ जवाब दो, नहीं मिले तो साफ बोलो। Scanned PDF को अलग से handle करो।

---

## ➡️ Next Topic
**586. Build CSV Chat App** — PDFs are text; CSVs are tables, so next the LLM writes a safe query plan instead of free text.
