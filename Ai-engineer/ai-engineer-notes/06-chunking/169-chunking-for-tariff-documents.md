---

# 169. Chunking for Tariff Documents
# हिंदी में: Tariff Documents के लिए Chunking

---

## 🔵 Simple Definition (English)
Tariff documents are organised as a hierarchy: Section > Chapter > Heading (4 digits) > Subheading (6 digits) > Tariff line (8 digits), plus legal Notes that modify the rules. Chunking them well means one chunk per tariff line that carries its full path ("breadcrumb") and its governing notes. This is the main project in this guide.

## 🔵 सरल परिभाषा (Hindi)
Tariff documents एक hierarchy में होते हैं: Section > Chapter > Heading (4 digit) > Subheading (6 digit) > Tariff line (8 digit), और साथ में legal Notes जो rules बदलते हैं। अच्छी chunking = हर tariff line का एक chunk, जिसमें उसका पूरा path (breadcrumb) और संबंधित notes हों। यही इस guide का main project है।

---

## 🔴 Problem it Solves
- Tariff lines say things like "- Other" or "-- Parts". Alone, "Other: 10%" is meaningless; the parent heading gives the meaning ("Telephone sets > Other").
- Chapter Notes and General Interpretive Rules decide classification but live far from the lines they affect.
- Fixed-size chunks mix several HS codes together, so the LLM may return the wrong code.
- Exact codes ("8517.13.00") must be matched exactly, which pure semantic search handles badly.

## 🔴 यह क्यों बना? (Hindi)
- Tariff line में अक्सर "- Other" लिखा होता है। अकेले "Other: 10%" बेमतलब है; parent heading ("Telephone sets > Other") से मतलब बनता है।
- Chapter Notes और Interpretive Rules classification तय करते हैं पर lines से दूर लिखे होते हैं।
- Fixed-size chunks कई HS codes मिला देते हैं, LLM गलत code दे सकता है।
- Exact code ("8517.13.00") को exact match चाहिए, सिर्फ semantic search कमज़ोर है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parse the schedule into rows: code, indent level, description, duty
Step 2 → Rebuild the hierarchy with a stack: a row at indent N inherits parents < N
Step 3 → Build breadcrumb: "Ch 85 > 8517 Telephone sets > 8517.13 Smartphones > Other"
Step 4 → One chunk per tariff line = breadcrumb + description + duty + unit
Step 5 → Chunk Chapter Notes separately by note number; link via chapter metadata
Step 6 → Metadata: hs_code, hs4, chapter, level, duty_rate, effective_date, doc_type
Step 7 → Store the exact hs_code as a keyword field too (hybrid search)
Step 8 → At query time: retrieve line chunks + the chapter's notes for the top hits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Schedule को rows में parse करो: code, indent, description, duty
Step 2 → Stack से hierarchy बनाओ: indent N वाली row अपने parents से inherit करती है
Step 3 → Breadcrumb बनाओ: "Ch 85 > 8517 > 8517.13 > Other"
Step 4 → हर tariff line = एक chunk (breadcrumb + description + duty)
Step 5 → Chapter Notes अलग chunks, chapter metadata से जुड़े
Step 6 → Metadata: hs_code, hs4, chapter, duty_rate, effective_date
Step 7 → Exact hs_code keyword field में भी रखो (hybrid search)
Step 8 → Query पर: top line chunks + उस chapter की notes लाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "Import duty for a 5G smartphone?" Retrieval returns the chunk:

`Chapter 85 > 8517 Telephone sets > 8517.13 Smartphones > 8517.13.00 Smartphones | duty 10% | unit: u`

plus Chapter 85 Note 4 ("Smartphones include..."). The LLM answers with code 8517.13.00, 10%, and cites the note. Without the breadcrumb, the chunk would only say "Smartphones 10%" and the HS prefix would be lost.

**Amazon style**: Amazon's product categories are also a tree (Electronics > Phones > Smartphones). Same pattern: chunk with category breadcrumb.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "5G smartphone पर import duty?" Retrieval यह chunk देता है:

`Chapter 85 > 8517 Telephone sets > 8517.13 Smartphones > 8517.13.00 | duty 10%`

और Chapter 85 की Note 4। LLM code 8517.13.00, 10% और note cite करके जवाब देता है। Breadcrumb के बिना chunk सिर्फ "Smartphones 10%" होता और HS prefix खो जाता।

**Amazon**: Product categories भी tree हैं (Electronics > Phones > Smartphones)। वही pattern: breadcrumb वाला chunk।

---

## 💻 Code Example — Basic
```python
# Basic: turn an indented tariff list into breadcrumb chunks (pure Python, runs offline)
SCHEDULE = """\
85 | Electrical machinery
8517 | Telephone sets
- 8517.13 | Smartphones
-- 8517.13.00 | Smartphones | 10%
- 8517.18 | Other telephone sets
-- 8517.18.00 | Other | 12%
"""  # code | description | optional duty; leading dashes are only decoration

def build_chunks(raw: str) -> list[dict]:  # create breadcrumb chunks
    stack: list[str] = []  # path of parent descriptions
    chunks: list[dict] = []  # output
    for line in raw.strip().splitlines():  # each row
        parts = [p.strip() for p in line.lstrip("- ").split("|")]  # code, desc, duty
        code, desc = parts[0], parts[1]  # first two fields
        duty = parts[2] if len(parts) > 2 else None  # optional duty
        depth = {2: 0, 4: 1, 7: 2, 10: 3}.get(len(code), 3)  # depth from code length (85, 8517, 8517.13, 8517.13.00)
        stack = stack[:depth] + [f"{code} {desc}"]  # keep parents, add self
        if duty:  # only tariff lines have a duty
            chunks.append({"text": " > ".join(stack) + f" | duty {duty}",  # breadcrumb text
                           "hs_code": code, "chapter": stack[0].split()[0]})  # metadata
    return chunks  # all line chunks

for c in build_chunks(SCHEDULE):  # print them
    print(c)  # each chunk knows its parents
```

## 💻 Code Example — Advanced
```python
# Production: tariff-aware chunker with hierarchy stack, notes chunks, validation, async batch.
from __future__ import annotations  # modern hints

import asyncio  # async version
import re  # code validation
from dataclasses import dataclass, field  # containers

HS_RE = re.compile(r"^\d{2}(\d{2}(\.\d{2}(\.\d{2})?)?)?$")  # 85, 8517, 8517.13, 8517.13.00


@dataclass
class TariffRow:  # one parsed row of the schedule
    code: str  # HS code at any level
    description: str  # official description
    duty: str | None = None  # duty rate if it is a tariff line
    depth: int = 0  # indent level (0=chapter ... 3=tariff line)


@dataclass
class TariffChunk:  # output chunk
    text: str  # text to embed
    metadata: dict = field(default_factory=dict)  # filters + citation info


def level_for(code: str) -> int:  # derive depth from the code length itself
    return {2: 0, 4: 1, 7: 2, 10: 3}.get(len(code), 3)  # 85 / 8517 / 8517.13 / 8517.13.00


def parse_row(line: str) -> TariffRow:  # parse "code | description | duty"
    parts = [p.strip() for p in line.split("|")]  # split fields
    if len(parts) < 2 or not HS_RE.match(parts[0]):  # validate code format
        raise ValueError(f"bad tariff row: {line!r}")  # report bad input
    return TariffRow(parts[0], parts[1], parts[2] if len(parts) > 2 else None, level_for(parts[0]))


def chunk_schedule(raw: str, effective: str) -> list[TariffChunk]:  # schedule -> chunks
    stack: list[TariffRow] = []  # parent rows
    out: list[TariffChunk] = []  # chunks
    for n, line in enumerate(filter(str.strip, raw.splitlines()), start=1):  # each non-empty line
        try:  # tolerate a few bad rows but log them
            row = parse_row(line)  # parse
        except ValueError:  # bad row
            continue  # skip (in production: log + count)
        stack = stack[:row.depth] + [row]  # keep parents, add self
        if row.duty is None:  # headings are context only
            continue  # not a tariff line
        crumb = " > ".join(f"{r.code} {r.description}" for r in stack)  # breadcrumb
        out.append(TariffChunk(  # create chunk
            text=f"{crumb} | duty {row.duty}",  # embed text includes full path
            metadata={"hs_code": row.code, "hs4": row.code[:4], "chapter": row.code[:2],
                      "duty": row.duty, "effective": effective, "doc_type": "tariff_line", "row": n}))
    return out  # line chunks


def chunk_notes(chapter: str, notes_text: str) -> list[TariffChunk]:  # one chunk per numbered note
    parts = re.split(r"(?m)^(?=\d+\.\s)", notes_text.strip())  # split at "1. ", "2. " ...
    return [TariffChunk(f"Chapter {chapter} Note {p.split('.')[0]}: {p.strip()}",
                        {"chapter": chapter, "doc_type": "chapter_note"}) for p in parts if p.strip()]  # notes


async def chunk_all(schedule: str, notes: dict[str, str], effective: str) -> list[TariffChunk]:  # async
    lines, *note_lists = await asyncio.gather(  # run parts concurrently
        asyncio.to_thread(chunk_schedule, schedule, effective),  # lines
        *(asyncio.to_thread(chunk_notes, ch, txt) for ch, txt in notes.items()))  # notes
    return lines + [c for sub in note_lists for c in sub]  # flatten


if __name__ == "__main__":  # demo
    sched = "85 | Electrical machinery\n8517 | Telephone sets\n8517.13 | Smartphones\n8517.13.00 | Smartphones | 10%\n"  # data
    notes = {"85": "1. This chapter does not cover toys.\n2. Smartphones include 5G devices."}  # notes
    for ch in asyncio.run(chunk_all(sched, notes, "2025-04-01")):  # run
        print(ch.metadata["doc_type"], "|", ch.text)  # show
```

---

## 🟠 FastAPI Integration
An admin endpoint ingests a new tariff schedule version. It returns counts per doc_type so the team can sanity-check (for example "10,200 lines, 96 notes"). Retrieval later filters by `effective` date so old rates never leak into new answers.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app


class TariffIngest(BaseModel):  # request body
    schedule: str  # pipe-separated rows
    notes: dict[str, str] = {}  # chapter -> notes text
    effective: str  # ISO date


@app.post("/admin/tariff/ingest")  # route
async def ingest(req: TariffIngest) -> dict:  # handler
    chunks = await chunk_all(req.schedule, req.notes, req.effective)  # chunk
    if not chunks:  # nothing parsed
        raise HTTPException(422, "no tariff lines found - check the row format")  # clear error
    counts: dict[str, int] = {}  # per type counts
    for c in chunks:  # count
        counts[c.metadata["doc_type"]] = counts.get(c.metadata["doc_type"], 0) + 1  # increment
    return {"total": len(chunks), "by_type": counts}  # summary
```

---

## 🔗 LangChain / LangGraph Connection
Wrap chunks as `Document` objects with metadata so any LangChain vector store can filter on `hs4` or `chapter`. A LangGraph classification flow: `retrieve_lines -> fetch_notes(chapter) -> classify -> verify`.

```python
from langchain_core.documents import Document  # LangChain document type

docs = [Document(page_content=c.text, metadata=c.metadata) for c in chunk_schedule(
    "85 | Electrical machinery\n8517 | Telephone sets\n8517.13 | Smartphones\n8517.13.00 | Smartphones | 10%", "2025-04-01")]  # build docs
# vectorstore.add_documents(docs)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {"chapter": "85"}})  # metadata filter
# LangGraph state: {"query", "lines", "notes", "answer"}; node 'fetch_notes' reads lines[0].metadata["chapter"].
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding the tariff line without its parents
✅ Correct: Prepend the breadcrumb so "Other" keeps its meaning.

```python
# Wrong - ambiguous
text = "Other | duty 12%"  # which "Other"?

# Right
text = "85 Electrical machinery > 8517 Telephone sets > 8517.18 Other telephone sets > 8517.18.00 Other | duty 12%"  # clear
```

❌ Mistake 2: Mixing rates from different years in one index without an `effective` date.
✅ Correct: Store `effective` (and `superseded`) metadata and filter at query time.

❌ Mistake 3: Relying on embeddings alone for exact HS codes.
✅ Correct: Hybrid search - keyword/BM25 on `hs_code` plus vectors on descriptions.

---

## 🧠 Tricky Interview Question
**Q**: "A user types the HS code '8517.13.00' and the vector search returns 8517.18.00 first. Why, and what do you do?"

**Answer**: Embedding models see numbers as similar token patterns, so neighbouring codes have almost identical vectors; vectors are not good at exact identifiers. Add a keyword/exact-match path: detect code-like patterns with a regex, look up `hs_code` directly in metadata (or BM25), and merge with vector results (hybrid search / reciprocal rank fusion). For non-code queries use vector search. Also normalise code formats ("85171300" vs "8517.13.00") at ingest and query time.

---

## ⚫ Interview Questions + Answers

Q1: Why include the breadcrumb in each tariff chunk?
A1: Lines like "Other" are meaningless alone. The parent path supplies meaning and improves embedding quality and the LLM's reasoning.

Q2: What is the chunk unit for a tariff schedule?
A2: One tariff line (8/10 digit) per chunk with its ancestors' text; headings are context, not separate chunks.

Q3: How do you handle Chapter Notes?
A3: Chunk per numbered note, tag with chapter, and fetch them for the chapter of the top-ranked lines (they override line text during classification).

Q4: How do you handle yearly tariff updates?
A4: Store effective-date metadata, version the index, never delete old versions needed for historical clearance, and filter by the date relevant to the shipment.

Q5: (Hard) How would you evaluate tariff chunking quality?
A5: Build a golden set of (product description, correct HS code) pairs from past rulings. Measure recall@k of the correct line chunk, top-1 accuracy of the final classification, and note-retrieval hit rate. Compare variants (with/without breadcrumb, with/without notes, hybrid vs vector only).

---

## 🔷 When to Use + When Not to Use
✅ Use hierarchical line chunks when:
- Data is a coded tree (HS codes, product categories, ICD medical codes, legal sections)
- Children are ambiguous without parents

❌ Avoid when:
- Documents are free narrative text without a hierarchy
- The code list is tiny and fits in the prompt directly

---

## 📊 Visual Diagram
```
 Section XVI
  └─ 85 Electrical machinery ─────────────► Chapter Notes ► chunks (note 1, 2, 3...)
      └─ 8517 Telephone sets
          └─ 8517.13 Smartphones
              └─ 8517.13.00 | 10%  ──► CHUNK:
                                       "85 Electrical > 8517 Telephone > 8517.13
                                        Smartphones > 8517.13.00 | duty 10%"
                                       meta {hs_code, hs4, chapter, effective}

 query ─► [vector search] + [exact hs_code lookup] ─► merge ─► + chapter notes ─► LLM
```

---

## 💰 Cost Impact
- Breadcrumb adds about 20-40 tokens per chunk. For 10,000 lines: 400K extra tokens, about $0.008 at $0.02 per 1M tokens - negligible.
- Gain: correct top-1 retrieval means fewer retries and a smaller top_k (3 instead of 8), saving about 5 x 80 = 400 prompt tokens per query. At 100K queries/day on a $0.15 per 1M input model that is about $6/day.
- Optimise: only re-embed lines whose text or rate changed in a new schedule version (content hash).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS code | Harmonized System product code | Product का अंतर्राष्ट्रीय code |
| Tariff line | Most specific code with a duty | सबसे specific code (duty सहित) |
| Breadcrumb | Parent path in the chunk | Parent path |
| Chapter Note | Legal rule for a chapter | Chapter का कानूनी नियम |
| Hybrid search | Keyword + vector | Keyword + vector search |
| Effective date | Date a rate starts | दर लागू होने की तारीख |

---

## ⚡ 3-Line Summary
English: Tariff documents are trees, so chunk one tariff line per chunk with its full breadcrumb. Chunk Chapter Notes separately and link them by chapter. Use metadata and hybrid search for exact HS codes and effective dates.
Hindi: Tariff documents tree होते हैं, इसलिए हर tariff line का एक chunk, पूरे breadcrumb के साथ। Chapter Notes अलग chunks, chapter से linked। Exact HS code और effective date के लिए metadata और hybrid search।

---

## ➡️ Next Topic
**170. Parent-Child Chunking** - search on small child chunks but give the LLM the bigger parent for context.
