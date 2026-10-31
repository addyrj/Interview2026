---

# 117. Embedding for Different Data Types — Complete Guide
# हिंदी में: अलग-अलग Data Types के लिए Embedding — पूरी Guide

---

## 🔵 Simple Definition (English)
Embedding models read text, so every other data type (tables, JSON, code, logs, PDFs, emails, product records, numbers) must first be turned into meaningful text, or embedded with a specialised model. How you convert the data decides the retrieval quality.

## 🔵 सरल परिभाषा (Hindi)
Embedding models text पढ़ते हैं, इसलिए बाकी हर data type (tables, JSON, code, logs, PDFs, emails, product records, numbers) को पहले अर्थपूर्ण text में बदलना पड़ता है, या specialised model से embed करना पड़ता है। Conversion कैसे करते हैं, यही retrieval quality तय करता है।

---

## 🔴 Problem it Solves
Naively embedding `{"hs":"8518","d":"hp","u":3}` or a raw CSV row gives poor vectors: keys, brackets and numbers dominate. Tables lose structure when flattened; code needs code-aware models; long PDFs exceed token limits; numbers like "5 kg" vs "5000 kg" are poorly captured. Good preprocessing is the fix.

## 🔴 यह क्यों बना? (Hindi)
`{"hs":"8518","d":"hp","u":3}` या raw CSV row को सीधे embed करने से खराब vectors बनते हैं: keys, brackets और numbers हावी हो जाते हैं। Tables flatten होने पर structure खो देती हैं; code को code-aware model चाहिए; लंबे PDFs token limit पार कर देते हैं; "5 kg" और "5000 kg" जैसे numbers ठीक से capture नहीं होते। अच्छी preprocessing इसका हल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the type: prose, table, JSON, code, log, PDF, chat, numeric
Step 2 → Convert to natural-language text that keeps the meaning
          table row  -> "Product: wireless earbuds. Category: audio. Duty: 10%."
          JSON       -> pick meaningful fields, drop ids/noise, render as sentences
          code       -> split by function/class; add file path + docstring
          PDF        -> extract text (OCR if scanned), keep headings, chunk by section
          logs       -> template-normalise (replace ids/timestamps), group
Step 3 → Chunk to the model limit with overlap; attach metadata (source, page)
Step 4 → Choose the model: general text, code (voyage-code-3), multilingual, multimodal
Step 5 → Embed; store vector + original structured record + metadata
Step 6 → Keep numbers and exact IDs in metadata filters (not in vectors)
Step 7 → Evaluate per data type separately
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Type पहचानो: prose, table, JSON, code, log, PDF, chat, numeric
Step 2 → Meaning बचाते हुए natural-language text में बदलो
          table row  -> "Product: wireless earbuds. Category: audio. Duty: 10%."
          JSON       -> ज़रूरी fields चुनो, ids/noise हटाओ, sentences बनाओ
          code       -> function/class से split; file path + docstring जोड़ो
          PDF        -> text extract (scan हो तो OCR), headings रखो, section से chunk
          logs       -> ids/timestamps बदलकर template बनाओ, group करो
Step 3 → Model limit तक chunk करो (overlap सहित); metadata जोड़ो
Step 4 → Model चुनो: general, code, multilingual, multimodal
Step 5 → Embed करो; vector + original record + metadata store करो
Step 6 → Numbers और exact IDs को metadata filters में रखो
Step 7 → हर data type का अलग evaluation
```

---

## 🟡 Real World Example
**Tariff Classification System**: Data comes as (a) PDF legal notes, (b) a CSV of HS codes with duty rates, (c) JSON customs declarations, (d) Excel product catalogues. The pipeline renders every CSV row as "HS 8518.30: Headphones and earphones. Chapter: Electrical machinery. General duty: 10%" and stores `duty_rate` and `hs_code` as metadata for filtering. Declarations JSON keeps only `description`, `material`, `origin_country` rendered as a sentence.

**Amazon-style**: Product record (title, bullets, brand, price). Embed title + bullets; filter on price and brand through metadata.

## 🟡 Real Example Hindi mein
**Tariff System**: Data चार रूपों में आता है: (a) PDF legal notes, (b) duty rates वाली HS codes की CSV, (c) JSON customs declarations, (d) Excel product catalogues। Pipeline हर CSV row को "HS 8518.30: Headphones and earphones. Chapter: Electrical machinery. General duty: 10%" बनाकर embed करती है और `duty_rate`, `hs_code` को filtering के लिए metadata में रखती है। Declarations JSON से सिर्फ `description`, `material`, `origin_country` लेकर एक sentence बनाया जाता है।

**Amazon-style**: Product record (title, bullets, brand, price)। Title + bullets embed करो; price और brand पर metadata से filter।

---

## 💻 Code Example — Basic
```python
# Convert different data types into embedding-friendly text (pure Python, runs offline)
import json
from typing import Any


def row_to_text(row: dict[str, Any], fields: list[str]) -> str:
    """Render a table row as 'Field: value.' sentences, skipping empty values."""
    parts = [f"{f.replace('_', ' ').title()}: {row[f]}." for f in fields if row.get(f) not in (None, "")]
    return " ".join(parts)


def json_to_text(raw: str, keep: list[str]) -> str:
    """Pick useful keys from a JSON string; ignore ids and noise."""
    try:
        data = json.loads(raw)                    # parse safely
    except json.JSONDecodeError as exc:
        raise ValueError(f"bad JSON: {exc}") from exc
    return row_to_text(data, keep)


def code_to_chunks(source: str, path: str) -> list[str]:
    """Very simple code splitter: one chunk per top-level def/class, with path header."""
    chunks: list[str] = []
    current: list[str] = []
    for line in source.splitlines():
        if line.startswith(("def ", "class ")) and current:
            chunks.append(f"# file: {path}\n" + "\n".join(current))
            current = []
        current.append(line)
    if current:
        chunks.append(f"# file: {path}\n" + "\n".join(current))
    return chunks


row = {"hs_code": "8518.30", "description": "Headphones and earphones", "duty_rate": "10%", "note": ""}
print(row_to_text(row, ["hs_code", "description", "duty_rate", "note"]))
print(json_to_text('{"id": 991, "description": "wireless earbuds", "origin_country": "CN"}',
                   ["description", "origin_country"]))
print(len(code_to_chunks("def a():\n    pass\n\ndef b():\n    pass\n", "utils.py")), "code chunks")
```

## 💻 Code Example — Advanced
```python
# Multi-type ingestion pipeline: render -> chunk -> embed -> store with metadata (async)
import asyncio
from dataclasses import dataclass, field
from typing import Any
from openai import AsyncOpenAI

client = AsyncOpenAI()
MODEL = "text-embedding-3-small"


@dataclass
class Record:
    text: str                                    # what gets embedded
    metadata: dict[str, Any] = field(default_factory=dict)   # filters, not embedded


def from_csv_row(row: dict[str, str]) -> Record:
    text = (f"HS {row['hs_code']}: {row['description']}. "
            f"Chapter: {row.get('chapter', 'n/a')}.")
    return Record(text, {"hs_code": row["hs_code"], "duty": float(row.get("duty", 0) or 0), "type": "csv"})


def from_declaration(d: dict[str, Any]) -> Record:
    text = f"{d['description']}. Material: {d.get('material', 'unknown')}. Origin: {d.get('origin', 'unknown')}."
    return Record(text, {"declaration_id": d["id"], "type": "declaration"})


def from_pdf_text(page_text: str, page: int, size: int = 1200, overlap: int = 150) -> list[Record]:
    out: list[Record] = []
    step = size - overlap
    for i in range(0, max(len(page_text), 1), step):          # character chunks (simple)
        piece = page_text[i:i + size].strip()
        if piece:
            out.append(Record(piece, {"page": page, "type": "pdf"}))
    return out


async def embed_records(records: list[Record]) -> list[tuple[Record, list[float]]]:
    if not records:
        return []
    try:
        r = await client.embeddings.create(model=MODEL, input=[x.text for x in records])
    except Exception as exc:
        raise RuntimeError(f"embedding failed: {exc}") from exc
    return [(rec, d.embedding) for rec, d in zip(records, sorted(r.data, key=lambda d: d.index))]


async def main() -> None:
    recs = [
        from_csv_row({"hs_code": "8518.30", "description": "Headphones", "duty": "10"}),
        from_declaration({"id": 7, "description": "wireless earbuds", "origin": "CN"}),
        *from_pdf_text("Chapter 85 notes ... " * 100, page=12),
    ]
    pairs = await embed_records(recs)
    print(len(pairs), "records embedded; first meta:", pairs[0][0].metadata)


if __name__ == "__main__":
    asyncio.run(main())                           # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Literal

app = FastAPI()


class IngestReq(BaseModel):
    kind: Literal["csv_row", "declaration", "text"]
    payload: dict[str, Any]


def render(kind: str, payload: dict[str, Any]) -> str:
    if kind == "csv_row":
        return f"HS {payload['hs_code']}: {payload['description']}"
    if kind == "declaration":
        return f"{payload['description']}. Origin: {payload.get('origin', 'unknown')}"
    return str(payload["text"])


@app.post("/ingest/preview")
async def preview(req: IngestReq) -> dict[str, str]:
    try:
        return {"text_to_embed": render(req.kind, req.payload)}
    except KeyError as exc:
        raise HTTPException(422, f"missing field {exc}")      # tell client what is missing
```
A preview route lets data teams inspect exactly what will be embedded before paying for it.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# Code-aware splitting:
py_splitter = RecursiveCharacterTextSplitter.from_language(Language.PYTHON, chunk_size=800, chunk_overlap=100)
code_docs = py_splitter.create_documents(["def a():\n    pass\n\ndef b():\n    pass\n"])

# Table rows as Documents with metadata:
doc = Document(page_content="HS 8518.30: Headphones and earphones. Duty 10%",
               metadata={"hs_code": "8518.30", "duty": 10.0})

# Loaders: PyPDFLoader, CSVLoader, JSONLoader, UnstructuredExcelLoader, etc.
```
In a LangGraph ingest graph, route by file type to different loader/splitter nodes, then merge into one embed node.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding raw JSON/CSV
✅ Correct: Render selected fields to natural language.

```python
# Wrong
embed(json.dumps(record))
# Right
embed(f"{record['description']}. Material: {record['material']}.")
```

❌ Mistake 2: Putting exact values (prices, IDs) only in the vector
✅ Correct: Keep them as metadata for exact filtering ("duty < 5", "hs_code = '8518.30'").

❌ Mistake 3: One embedding for a whole long PDF
✅ Correct: Chunk by section; the average blurs topics and truncates at 8191 tokens.

---

## 🧠 Tricky Interview Question

**Q**: "Users search 'duty under 5%' and get items with 15% duty. The embedding model is good. Why?"

**Answer**: Embeddings capture topical similarity, not numeric comparison or logic. "5%" and "15%" look alike to the model. Use structured filtering (metadata `duty < 5`) combined with semantic search: have an LLM parse the query into a semantic part and filters (self-query retriever), apply the filter in the vector DB, then rank the remaining items by similarity.

---

## ⚫ Interview Questions + Answers

Q1: Why not embed raw JSON?
A1: Syntax and keys add noise and waste tokens; render only meaningful fields as text.

Q2: How do you embed a spreadsheet row?
A2: Convert it to a sentence with column names and values; store key values as metadata.

Q3: What changes for code embeddings?
A3: Split by function/class, include file path and docstrings, and prefer a code-trained model (e.g. voyage-code-3, OpenAI text-embedding-3 also works).

Q4: How to handle scanned PDFs?
A4: OCR first (Tesseract, cloud OCR, or a vision model), clean the text, then chunk and embed. Check OCR quality, as errors become embedding errors.

Q5: Design retrieval over mixed data: PDFs, tables, and images of invoices.
A5: Separate pipelines per type with a shared metadata schema; PDFs chunked by section; tables rendered as row sentences plus a table summary; images via OCR or a multimodal embedding; one or multiple indexes; query router (LLM or classifier) decides which index/filters; rerank across results; evaluate each source type and the combined system.

---

## 🔷 When to Use + When Not to Use
✅ Use type-specific preprocessing when:
- Data is structured or semi-structured
- Mixed sources feed one search

❌ Avoid semantic embedding when:
- The query is an exact lookup (ID, SKU, HS code): use keyword/SQL
- Numeric range queries (use filters)

---

## 📊 Visual Diagram
```
 PDF ──► extract+chunk ─┐
 CSV ──► row sentence ──┤
 JSON ─► select fields ─┼─► text + metadata ─► embedding model ─► vector DB
 Code ─► split by def ──┤                                         (vector + metadata)
 Image ► OCR / CLIP ────┘
```

---

## 💰 Cost Impact
Cost scales with tokens of the *rendered* text. Raw JSON can be 2 to 3x larger than a clean sentence (brackets, keys, ids), so cleaning cuts cost and noise. Example: 1M declarations at 250 raw tokens vs 80 clean tokens = 250M vs 80M tokens: $5.00 vs $1.60 with small. OCR/vision steps add their own cost; cache them. Skip embedding fields that are only used for filtering.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Serialisation | Turning data into text | Data को text में बदलना |
| Chunking | Splitting long data | लंबे data को बाँटना |
| Metadata filter | Exact conditions on fields | Fields पर exact शर्तें |
| OCR | Image to text | Image से text |
| Self-query | LLM extracts filters | LLM से filters निकालना |
| Code embedding | Model trained on code | Code पर trained model |

---

## ⚡ 3-Line Summary
English: Turn every data type into clean, meaningful text before embedding, and chunk it. Keep exact values and IDs as metadata filters. Evaluate each data type separately.
Hindi: Embed करने से पहले हर data type को साफ, अर्थपूर्ण text में बदलो और chunk करो। Exact values और IDs को metadata filters में रखो। हर data type को अलग से evaluate करो।

---

## ➡️ Next Topic
**118. Image Embeddings Basics** - how pictures become vectors (CLIP and friends) for image search.
