---

# 161. Paragraph Splitting
# हिंदी में: Paragraph Splitting (अनुच्छेद के आधार पर)

---

## 🔵 Simple Definition (English)
Paragraph splitting uses the blank lines that authors already put between paragraphs as chunk boundaries. Each paragraph is usually one idea, so chunks are natural. Tiny paragraphs get merged and huge ones get split further.

## 🔵 सरल परिभाषा (Hindi)
Paragraph splitting उन खाली lines को chunk की सीमा बनाती है जो लेखक ने paragraphs के बीच पहले से रखी हैं। हर paragraph आमतौर पर एक idea होता है, इसलिए chunks स्वाभाविक बनते हैं। बहुत छोटे paragraphs मिला दिए जाते हैं और बहुत बड़े आगे तोड़े जाते हैं।

---

## 🔴 Problem it Solves
Authors structure meaning with paragraphs; ignoring that and cutting every 500 characters wastes free structure. But raw paragraphs vary wildly (1 line to 3 pages), so a good splitter also normalises size.

## 🔴 यह क्यों बना? (Hindi)
लेखक अर्थ को paragraphs से संरचित करते हैं; इसे अनदेखा करके हर 500 characters पर काटना मुफ़्त structure बेकार करना है। पर कच्चे paragraphs का size बहुत अलग-अलग होता है (1 line से 3 pages), इसलिए अच्छा splitter size को सामान्य भी करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise line endings (\r\n -> \n)
Step 2 → Split on blank lines: regex \n\s*\n
Step 3 → Drop empty paragraphs; strip whitespace
Step 4 → Merge consecutive short paragraphs until min_chars is reached (stay under max_chars)
Step 5 → Split an oversized paragraph by sentences, then by words as a last resort
Step 6 → Attach paragraph index/section metadata and embed
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Line endings normalise करो (\r\n -> \n)
Step 2 → खाली lines पर बाँटो: regex \n\s*\n
Step 3 → खाली paragraphs हटाओ; whitespace strip करो
Step 4 → लगातार छोटे paragraphs को min_chars तक merge करो (max_chars से नीचे रहकर)
Step 5 → बहुत बड़े paragraph को sentences से, आख़िर में words से बाँटो
Step 6 → Paragraph index/section metadata जोड़ो और embed करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: customs rulings and legal commentary are written in focused paragraphs: one for the facts, one for the legal reasoning, one for the conclusion. Paragraph chunks let retrieval return "the reasoning paragraph" directly, and a reviewer can cite "paragraph 7 of ruling 2025/114".

**Amazon-style**: product Q&A answers and long reviews are paragraph-structured; each paragraph covers one aspect (battery, fit, delivery).

## 🟡 Real Example Hindi mein
**Tariff System**: customs rulings और legal commentary केंद्रित paragraphs में लिखे होते हैं: एक तथ्यों के लिए, एक कानूनी तर्क के लिए, एक निष्कर्ष के लिए। Paragraph chunks से retrieval सीधे "तर्क वाला paragraph" लौटा सकता है, और reviewer "ruling 2025/114 का paragraph 7" cite कर सकता है।

**Amazon-style**: product Q&A जवाब और लंबे reviews paragraph-आधारित होते हैं; हर paragraph एक पहलू (battery, fit, delivery) बताता है।

---

## 💻 Code Example — Basic
```python
# Runs offline: paragraph splitter with merge of tiny paragraphs and split of huge ones
import re


def paragraph_chunks(text: str, min_chars: int = 150, max_chars: int = 600) -> list[str]:
    if min_chars > max_chars:
        raise ValueError("min_chars must not exceed max_chars")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]  # real paragraphs
    chunks: list[str] = []
    buf = ""  # buffer used to merge short paragraphs
    for p in paras:
        if len(p) > max_chars:  # oversized paragraph
            if buf:
                chunks.append(buf)  # flush buffer first
                buf = ""
            sents = re.split(r"(?<=[.!?।])\s+", p)  # fall back to sentences
            cur = ""
            for s in sents:
                if cur and len(cur) + len(s) + 1 > max_chars:
                    chunks.append(cur)  # current piece is full
                    cur = s
                else:
                    cur = f"{cur} {s}".strip()
            if cur:
                chunks.append(cur)
            continue
        if buf and len(buf) + len(p) + 2 > max_chars:
            chunks.append(buf)  # adding p would exceed max: flush
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p  # merge short neighbours
        if len(buf) >= min_chars:  # big enough: emit
            chunks.append(buf)
            buf = ""
    if buf:
        chunks.append(buf)  # leftover
    return chunks


doc = "Facts: item is a wireless headset.\n\nReasoning: it transmits sound, so 8518.30 applies.\n\n" + "Long annex. " * 80 + "\n\nConclusion: code 8518.30."
for i, c in enumerate(paragraph_chunks(doc, 60, 300)):
    print(i, len(c), repr(c[:45]))
```

## 💻 Code Example — Advanced
```python
# Production: paragraph chunker with metadata, async file loading, and robust error handling
import asyncio
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("paragraph_chunker")


@dataclass
class ParaChunk:
    text: str
    paragraph_ids: list[int]  # which source paragraphs are inside (for citations)
    meta: dict[str, str] = field(default_factory=dict)


def chunk_paragraphs(text: str, source: str, target_chars: int = 500, max_chars: int = 900) -> list[ParaChunk]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]
    out: list[ParaChunk] = []
    cur: list[tuple[int, str]] = []  # (paragraph id, text)
    size = 0

    def flush() -> None:
        nonlocal cur, size
        if cur:
            out.append(ParaChunk("\n\n".join(t for _, t in cur), [i for i, _ in cur], {"source": source}))
        cur, size = [], 0

    for i, p in enumerate(paras):
        if len(p) > max_chars:  # hard-split oversize paragraph by chars at word boundaries
            flush()
            words, piece = p.split(" "), ""
            for w in words:
                if len(piece) + len(w) + 1 > max_chars:
                    out.append(ParaChunk(piece, [i], {"source": source, "split": "oversize"}))
                    piece = w
                else:
                    piece = f"{piece} {w}".strip()
            if piece:
                out.append(ParaChunk(piece, [i], {"source": source, "split": "oversize"}))
            continue
        if size + len(p) > max_chars:
            flush()
        cur.append((i, p))
        size += len(p)
        if size >= target_chars:
            flush()
    flush()
    return out


async def load_and_chunk(path: str) -> list[ParaChunk]:
    try:
        text = await asyncio.to_thread(Path(path).read_text, encoding="utf-8")  # file IO off the event loop
    except (FileNotFoundError, UnicodeDecodeError):
        log.exception("cannot read %s", path)
        raise
    return await asyncio.to_thread(chunk_paragraphs, text, Path(path).name)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()


@app.post("/chunk/paragraphs")
async def chunk_upload(file: UploadFile) -> dict:
    data = await file.read()
    try:
        text = data.decode("utf-8")  # reject non-UTF-8 input clearly
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="file must be UTF-8 text")
    chunks = chunk_paragraphs(text, file.filename or "upload")  # from Advanced example
    return {"chunks": len(chunks), "first": chunks[0].text[:100] if chunks else ""}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# Pure paragraph splitting (merges paragraphs up to chunk_size):
para_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=800, chunk_overlap=0, is_separator_regex=False)
docs = para_splitter.create_documents(["Facts...\n\nReasoning...\n\nConclusion..."])

# Safer default: paragraph first, then smaller separators only when needed
safe = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", ". ", " "], chunk_size=800, chunk_overlap=0)
# Note: CharacterTextSplitter never splits inside an over-long paragraph; chunks may exceed chunk_size.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming extracted PDF text has real paragraph breaks
```python
# Wrong: PDF extraction often puts "\n" at every visual line, and no "\n\n" at all -> one giant chunk
# Right: inspect extraction output; rebuild paragraphs (join lines, split where line is short or indent starts),
#        or fall back to recursive splitting
text = re.sub(r"(?<!\n)\n(?!\n)", " ", raw)   # join single line-wraps, keep blank-line paragraphs
```

❌ Mistake 2: Leaving tiny paragraphs as separate chunks
```python
# Wrong: headings or one-word lines such as "Notes" become their own vectors (noise)
# Right: merge with the following paragraph, or attach as a heading/prefix
```

---

## 🧠 Tricky Interview Question

**Q**: "Your paragraph splitter produced one chunk of 40,000 characters for a scanned legal PDF. What happened and what do you do?"

**Answer**: OCR/PDF extraction typically yields single newlines inside text and no blank lines, so the "\n\n" separator never occurs and the entire page becomes one paragraph. Always enforce `max_chars` with a fallback (sentence split, then word split). Also fix the source: clean the extraction (join wrapped lines, detect headings by font size or layout), or use a layout-aware parser. Add a monitoring check that alerts when any chunk is larger than max_chars.

---

## ⚫ Interview Questions + Answers

Q1: Why use paragraphs as chunk boundaries?
A1: Authors place paragraph breaks where ideas change, so chunks are naturally coherent.

Q2: Biggest risk?
A2: Uneven sizes, from one-liners to enormous blocks, and missing breaks in extracted text.

Q3: How do you handle tiny paragraphs?
A3: Merge them with neighbours until a minimum size is reached.

Q4: How do you handle huge paragraphs?
A4: Split by sentences, then words, to respect the max size.

Q5: How would you combine paragraph splitting with context preservation?
A5: Prepend the section heading to each chunk, store paragraph ids and the parent section id, retrieve the matched paragraph but expand to neighbours (previous/next) or the parent section when passing to the LLM, and add 1-sentence overlap if answers span paragraph borders.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Articles, legal commentary, reports, documentation with real paragraph structure

❌ Avoid when:
- Poorly extracted text with no blank lines
- Chat logs, tables, code

---

## 📊 Visual Diagram
```
 doc:  [P1 short]\n\n[P2 short]\n\n[P3 LONG LONG LONG ...]\n\n[P4]
          └── merge ──┘                │ split by sentences
 chunks: [P1+P2]   [P3a]  [P3b]   [P4]
         each within min..max size, keeps paragraph ids
```

---

## 💰 Cost Impact
- No extra embedding cost beyond the chunk tokens; paragraph chunks usually avoid overlap, so embedding tokens equal the source tokens (about 20 percent cheaper than overlapped fixed windows).
- Coherent paragraphs mean fewer retrieved chunks are needed; at 5 chunks of about 150 tokens the prompt context is about 750 tokens.
- Watch out for oversized chunks: a 40,000-character chunk is about 10,000 tokens and can blow up both embedding limits and prompt cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Paragraph | Block of text separated by blank lines | खाली line से अलग text block |
| Merge | Combine small pieces | छोटे हिस्से जोड़ना |
| min/max chars | Size limits | Size की सीमाएँ |
| Parent section | Larger context for a chunk | Chunk का बड़ा संदर्भ |
| Line wrap | Single newline inside a paragraph | Paragraph के अंदर की नई line |

---

## ⚡ 3-Line Summary
English: Paragraph splitting uses authors' own blank lines as boundaries, giving coherent chunks. Merge tiny paragraphs, split huge ones, and verify the extracted text really has paragraph breaks. Keep paragraph ids for citations.
Hindi: Paragraph splitting लेखक की खाली lines को सीमा बनाकर coherent chunks देती है। छोटे paragraphs मिलाओ, बड़े तोड़ो, और जाँचो कि extracted text में सच में paragraph breaks हैं। Citations के लिए paragraph ids रखो।

---

## ➡️ Next Topic
**162. Markdown Splitting** — split by headings so each chunk knows its section path.
