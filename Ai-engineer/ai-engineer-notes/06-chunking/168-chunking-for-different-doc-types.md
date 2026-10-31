---

# 168. Chunking for Different Doc Types
# हिंदी में: अलग-अलग Document Types के लिए Chunking

---

## 🔵 Simple Definition (English)
Different documents have different natural units: code has functions, Markdown has headings, tables have rows, chat logs have turns, FAQs have question-answer pairs. Chunking for doc types means choosing the splitting rule that matches the document's own structure, instead of using one fixed size for everything.

## 🔵 सरल परिभाषा (Hindi)
हर document की अपनी natural unit होती है: code में functions, Markdown में headings, tables में rows, chat में turns, FAQ में question-answer pair। Doc type के हिसाब से chunking का मतलब है कि document की अपनी structure के अनुसार splitting rule चुनना, हर चीज़ के लिए एक fixed size नहीं।

---

## 🔴 Problem it Solves
- One-size-fits-all (for example 500 characters) cuts a Python function in half, breaks a table row, or splits a question from its answer.
- Each doc type loses meaning in a different way: code loses scope, tables lose headers, chat loses who said what.
- A single strategy forces a bad compromise on every type.

## 🔴 यह क्यों बना? (Hindi)
- हर चीज़ पर एक ही size (जैसे 500 characters) function को आधा काट देता है, table row तोड़ देता है, सवाल को जवाब से अलग कर देता है।
- हर doc type अलग तरह से meaning खोता है: code scope खोता है, table header खोती है, chat में "किसने कहा" खो जाता है।
- एक strategy हर type पर खराब समझौता थोपती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect doc type (file extension, MIME type, or a quick classifier)
Step 2 → Look up the strategy for that type (a registry / dispatch table)
Step 3 → Code      → split on function/class boundaries (AST or language-aware splitter)
Step 4 → Markdown  → split on headings, keep heading path
Step 5 → Table/CSV → one row (or group of rows) per chunk, header repeated
Step 6 → Chat/log  → group N turns or one time window; keep speaker + timestamp
Step 7 → FAQ/JSON  → one record = one chunk, zero overlap
Step 8 → Unknown   → fall back to recursive character splitting
Step 9 → Always attach doc_type + source in metadata, then embed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Doc type पहचानो (extension, MIME, classifier)
Step 2 → उस type की strategy lookup करो (dispatch table)
Step 3 → Code → function/class boundary पर split
Step 4 → Markdown → headings पर split, heading path रखो
Step 5 → Table/CSV → एक row (या कुछ rows) प्रति chunk, header दोहराओ
Step 6 → Chat/log → N turns या time window; speaker + timestamp रखो
Step 7 → FAQ/JSON → एक record = एक chunk, overlap 0
Step 8 → Unknown → recursive character splitter
Step 9 → metadata में doc_type + source जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The knowledge base mixes (1) tariff schedule tables (CSV), (2) legal notes (prose PDF), (3) customs rulings (Q&A style), (4) an internal Python rules library, and (5) officer chat logs. Each needs a different splitter: CSV by row with header, legal notes by heading with overlap, rulings one-per-chunk, code by function, chat by conversation window.

**Zomato style**: Menu CSV (row = dish), reviews JSON (item = review), help-centre Markdown (heading = topic), and support chats (turn windows).

## 🟡 Real Example Hindi mein
**Tariff System**: Knowledge base में (1) tariff tables (CSV), (2) legal notes (prose PDF), (3) customs rulings (Q&A), (4) internal Python rules, (5) officer chat logs। CSV row के हिसाब से, legal notes heading + overlap से, rulings एक-एक chunk, code function से, chat conversation window से।

**Zomato**: Menu CSV (row = dish), reviews JSON (item = review), help Markdown (heading = topic), support chat (turn windows)।

---

## 💻 Code Example — Basic
```python
# Basic doc-type dispatcher in pure Python
import re  # regex for markdown and code boundaries

def split_markdown(text: str) -> list[str]:  # split on markdown headings
    parts = re.split(r"(?m)^(?=#{1,3} )", text)  # lookahead keeps the heading
    return [p.strip() for p in parts if p.strip()]  # drop empties

def split_code(text: str) -> list[str]:  # split python on def/class
    parts = re.split(r"(?m)^(?=def |class )", text)  # new chunk at each def/class
    return [p.strip() for p in parts if p.strip()]  # drop empties

def split_csv(text: str) -> list[str]:  # one row per chunk with header
    header, *rows = text.strip().splitlines()  # first line is the header
    return [f"{header}\n{r}" for r in rows]  # repeat header in each chunk

def split_chat(text: str, turns: int = 2) -> list[str]:  # group chat lines
    lines = [ln for ln in text.splitlines() if ln.strip()]  # non-empty lines
    return ["\n".join(lines[i:i + turns]) for i in range(0, len(lines), turns)]  # windows

def split_default(text: str, size: int = 60) -> list[str]:  # fallback fixed size
    return [text[i:i + size] for i in range(0, len(text), size)]  # slices

STRATEGIES = {"md": split_markdown, "py": split_code, "csv": split_csv, "chat": split_chat}  # registry

def chunk(doc_type: str, text: str) -> list[str]:  # dispatcher
    return STRATEGIES.get(doc_type, split_default)(text)  # pick strategy or fallback

print(chunk("csv", "code,duty\n8517,10%\n8518,7%"))  # header repeated on every row
print(chunk("py", "def a():\n    return 1\ndef b():\n    return 2"))  # one function each
print(chunk("md", "# Rules\ntext\n## Exempt\nmore"))  # one section each
print(chunk("chat", "A: hi\nB: hello\nA: hs code?\nB: 8517"))  # two turns each
```

## 💻 Code Example — Advanced
```python
# Production: registry-based chunker with metadata, python AST splitting, validation, async batch
from __future__ import annotations  # modern hints

import ast  # real Python parsing for code
import asyncio  # async batch
import csv  # robust CSV parsing
import io  # in-memory text stream
import json  # for JSON/FAQ records
from dataclasses import dataclass, field  # containers
from typing import Callable  # type alias


@dataclass
class Chunk:  # output record
    text: str  # chunk text
    metadata: dict = field(default_factory=dict)  # doc_type, source, extra


def chunk_python(src: str) -> list[str]:  # AST based: one chunk per top-level def/class
    tree = ast.parse(src)  # raises SyntaxError on bad code
    lines = src.splitlines()  # source lines
    out = []  # chunks
    for node in tree.body:  # top-level nodes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):  # callable units
            out.append("\n".join(lines[node.lineno - 1: node.end_lineno]))  # exact source slice
    return out or [src]  # fall back to the whole file


def chunk_csv(src: str, rows_per_chunk: int = 5) -> list[str]:  # group rows, repeat header
    reader = csv.reader(io.StringIO(src))  # handles quotes/commas correctly
    rows = list(reader)  # all rows
    if len(rows) < 2:  # header only
        return []  # nothing to index
    header, body = rows[0], rows[1:]  # split header and body
    out = []  # chunks
    for i in range(0, len(body), rows_per_chunk):  # group rows
        group = body[i:i + rows_per_chunk]  # rows for this chunk
        out.append("\n".join(", ".join(f"{h}: {v}" for h, v in zip(header, r)) for r in group))  # key: value
    return out  # chunks


def chunk_faq(src: str) -> list[str]:  # JSON list of {q, a}
    data = json.loads(src)  # raises JSONDecodeError on bad input
    return [f"Q: {d['q']}\nA: {d['a']}" for d in data]  # one record = one chunk


def chunk_text(src: str, size: int = 500, overlap: int = 50) -> list[str]:  # fallback
    step = max(1, size - overlap)  # window step
    return [src[i:i + size] for i in range(0, len(src), step)]  # fixed windows


REGISTRY: dict[str, Callable[[str], list[str]]] = {  # doc_type -> strategy
    "py": chunk_python, "csv": chunk_csv, "faq": chunk_faq,
}


def build_chunks(doc_type: str, source: str, text: str) -> list[Chunk]:  # public API
    if not text.strip():  # validate
        raise ValueError(f"{source} is empty")  # error
    strategy = REGISTRY.get(doc_type, chunk_text)  # choose strategy
    try:  # parsers can fail on malformed input
        pieces = strategy(text)  # run it
    except (SyntaxError, json.JSONDecodeError, csv.Error) as exc:  # known failures
        pieces = chunk_text(text)  # degrade gracefully to generic splitting
        doc_type = f"{doc_type}-fallback"  # mark it so we can monitor
    return [Chunk(p, {"doc_type": doc_type, "source": source, "i": i})
            for i, p in enumerate(pieces)]  # attach metadata


async def build_many(items: list[tuple[str, str, str]]) -> list[list[Chunk]]:  # async batch
    tasks = [asyncio.to_thread(build_chunks, t, s, x) for t, s, x in items]  # one task each
    return await asyncio.gather(*tasks)  # run concurrently


if __name__ == "__main__":  # demo
    items = [("py", "rules.py", "def a():\n    return 1\n\ndef b():\n    return 2\n"),
             ("csv", "tariff.csv", "code,duty\n8517,10%\n8518,7%\n"),
             ("faq", "faq.json", '[{"q": "HS code of phone?", "a": "8517"}]')]  # sample docs
    for res in asyncio.run(build_many(items)):  # run batch
        for c in res:  # print each chunk
            print(c.metadata["doc_type"], repr(c.text))  # show result
```

---

## 🟠 FastAPI Integration
One ingestion endpoint accepts a file and a `doc_type` (or infers it from the extension) and routes it to the right strategy. Unknown types fall back safely, malformed files return 422.

```python
from fastapi import FastAPI, HTTPException, UploadFile, File  # framework

app = FastAPI()  # app
EXT_TO_TYPE = {".py": "py", ".csv": "csv", ".json": "faq"}  # extension map


@app.post("/ingest")  # route
async def ingest(file: UploadFile = File(...)) -> dict:  # upload handler
    name = file.filename or "unknown"  # file name
    ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""  # extension
    raw = await file.read()  # bytes
    try:  # decode safely
        text = raw.decode("utf-8")  # text
    except UnicodeDecodeError:  # not text
        raise HTTPException(415, "binary files are not supported here")  # unsupported
    try:  # chunk
        chunks = await asyncio.to_thread(build_chunks, EXT_TO_TYPE.get(ext, "text"), name, text)  # off-loop
    except ValueError as exc:  # empty file
        raise HTTPException(422, str(exc))  # report
    return {"source": name, "chunks": len(chunks), "type": chunks[0].metadata["doc_type"]}  # summary
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships language-aware splitters: `RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)` and `MarkdownHeaderTextSplitter`. In LangGraph, model the dispatcher as a router node with conditional edges, one node per doc type.

```python
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter  # splitters

code_splitter = RecursiveCharacterTextSplitter.from_language(  # code-aware
    language=Language.PYTHON, chunk_size=600, chunk_overlap=0)  # splits on def/class first
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2")])  # heading-aware
py_chunks = code_splitter.create_documents(["def a():\n    return 1\n\ndef b():\n    return 2\n"])  # Documents
md_chunks = md_splitter.split_text("# Rules\ntext\n## Exempt\nmore")  # Documents with header metadata
# LangGraph: add_conditional_edges("detect_type", route_fn, {"py": "code_node", "md": "md_node", ...})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Splitting code with a plain character splitter
✅ Correct: Split on function/class boundaries so a chunk is a complete unit.

```python
# Wrong - may cut a function in half
bad = [src[i:i + 200] for i in range(0, len(src), 200)]  # arbitrary cuts

# Right - AST based
good = chunk_python(src)  # complete functions
```

❌ Mistake 2: Chunking CSV rows without the header
✅ Correct: Repeat the header or convert to "column: value" text, otherwise "10%" has no meaning.

❌ Mistake 3: Using overlap on atomic records (FAQ, review).
✅ Correct: One record = one chunk, overlap 0.

---

## 🧠 Tricky Interview Question
**Q**: "Your support-chat index returns chunks like 'Yes, that works.' with no context. How do you chunk chat logs better?"

**Answer**: Chat turns are tiny and depend on earlier turns. Chunk by conversation window (for example 6-10 turns or a time gap of 10 minutes), keep speaker labels and timestamps, and slide the window by 2-3 turns for overlap. Optionally prepend an LLM-written summary or the ticket subject. Store the conversation id so neighbours can be fetched. Alternatively index per-resolution summaries instead of raw turns.

---

## ⚫ Interview Questions + Answers

Q1: Why not use one chunk size for all documents?
A1: Documents differ in structure and meaning units. Fixed size cuts meaningful units and mixes topics.

Q2: How do you chunk source code?
A2: Split on functions/classes (AST or `Language`-aware splitter), include imports/signature context, little or no overlap.

Q3: How do you chunk a table?
A3: Keep header with rows; chunk by row or small row groups; optionally convert rows into sentences. Never separate header from data.

Q4: How do you pick a strategy automatically?
A4: Use extension/MIME type first; for unknown text use a heuristic (many `#` lines = Markdown, JSON parse success = records) or a small classifier; fall back to recursive splitting.

Q5: (Hard) How do you evaluate that a doc-type-specific strategy is actually better?
A5: Build an eval set per doc type, compare retrieval metrics (recall@k, MRR) and answer correctness between the generic and the specific strategy, and track fallback rate in production. Keep the specific strategy only when the gain justifies the extra code.

---

## 🔷 When to Use + When Not to Use
✅ Use type-specific chunking when:
- Your corpus mixes several formats
- Structure carries meaning (code, tables, FAQ)

❌ Avoid when:
- All documents are similar plain prose (one recursive splitter is enough)
- Early prototype with little data

---

## 📊 Visual Diagram
```
                   ┌──────────────┐
 incoming file ──► │ detect type  │
                   └──────┬───────┘
     ┌────────┬───────────┼────────────┬─────────────┐
     ▼        ▼           ▼            ▼             ▼
   code      md         csv/table     chat/log      faq/json
 by def/   by heading  row + header  turn window   1 record
 class     + path      repeated      + speaker     = 1 chunk
     └────────┴───────────┴────────────┴─────────────┘
                          │
                  chunks + metadata{doc_type, source}
                          │
                       embed → store
```

---

## 💰 Cost Impact
- Right-sized atomic chunks avoid sending 5 x 500 tokens of mixed content; typical saving is 20-40% of prompt tokens versus oversized generic chunks.
- Overlap = 0 for atomic types removes 10-20% duplicate embedding tokens.
- Repeating a CSV header per row adds a few tokens per chunk; group 5-10 rows per chunk to amortise it.
- Optimise: dispatch table keeps the code cheap; cache by content hash; embed only changed chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Doc type | Format/kind of document | Document का प्रकार |
| Dispatcher | Picks strategy by type | Strategy चुनने वाला |
| AST | Parsed code tree | Code का tree |
| Atomic chunk | One self-contained record | अपने-आप में पूरा chunk |
| Fallback | Default when type unknown | Default विकल्प |
| Conversation window | Group of chat turns | Chat turns का समूह |

---

## ⚡ 3-Line Summary
English: Different documents have different natural units, so pick the splitter by doc type. Use code boundaries, headings, rows, turns or records, and fall back to recursive splitting for unknown types. Always store doc_type in metadata.
Hindi: अलग documents की natural units अलग हैं, इसलिए doc type से splitter चुनो। Code boundary, heading, row, turn या record इस्तेमाल करो; unknown type पर recursive splitting। metadata में doc_type ज़रूर रखो।

---

## ➡️ Next Topic
**169. Chunking for Tariff Documents** - applying all of this to our main project: schedules, notes and rulings.
