---

# 158. Recursive Character Splitting
# हिंदी में: Recursive Character Splitting

---

## 🔵 Simple Definition (English)
Recursive character splitting tries a list of separators from biggest to smallest (paragraph break, line break, space, character). It splits on the biggest one first, and only goes deeper for pieces that are still too large. Chunks stay close to natural boundaries and under a size limit.

## 🔵 सरल परिभाषा (Hindi)
Recursive character splitting separators की list को बड़े से छोटे क्रम में आज़माती है (paragraph break, line break, space, character)। पहले सबसे बड़े separator पर बाँटती है, और सिर्फ़ उन टुकड़ों को और गहराई से तोड़ती है जो अभी भी बड़े हैं। Chunks प्राकृतिक सीमाओं के पास और size limit के अंदर रहते हैं।

---

## 🔴 Problem it Solves
Fixed windows cut mid-sentence; pure paragraph splitting can create huge chunks. Recursive splitting gives both: respect structure when possible, enforce a hard size cap always. It is the default recommendation for general text.

## 🔴 यह क्यों बना? (Hindi)
Fixed windows वाक्य के बीच में कटती हैं; सिर्फ़ paragraph splitting बहुत बड़े chunks बना सकती है। Recursive splitting दोनों देती है: जब संभव हो structure का सम्मान, और हमेशा size की सख़्त सीमा। सामान्य text के लिए यही default सुझाव है।

---

## 🟢 How it Works — Step by Step

```
separators = ["\n\n", "\n", " ", ""]

Step 1 → Split text by the first separator ("\n\n") into pieces
Step 2 → Pieces that fit chunk_size are kept; small neighbours are MERGED up to chunk_size
Step 3 → A piece larger than chunk_size is split recursively with the NEXT separator ("\n", then " ")
Step 4 → Last resort separator "" cuts by characters
Step 5 → Add overlap by repeating the tail of the previous chunk
Step 6 → Result: chunks <= chunk_size that mostly end at paragraph/sentence/word boundaries
```

## 🟢 कैसे काम करता है? (Hindi)

```
separators = ["\n\n", "\n", " ", ""]

Step 1 → पहले separator ("\n\n") से text को टुकड़ों में बाँटो
Step 2 → chunk_size में फिट टुकड़े रखो; छोटे पड़ोसियों को chunk_size तक MERGE करो
Step 3 → chunk_size से बड़े टुकड़े को अगले separator ("\n", फिर " ") से recursively बाँटो
Step 4 → आख़िरी separator "" characters से काटता है
Step 5 → पिछले chunk की पूँछ दोहराकर overlap जोड़ो
Step 6 → नतीजा: chunks <= chunk_size जो ज़्यादातर paragraph/sentence/word सीमा पर ख़त्म होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: tariff notes mix short bullet lines, long legal paragraphs and tables converted to text. A recursive splitter (800 chars, 100 overlap) keeps most legal paragraphs intact, splits very long ones at sentence or word boundaries, and merges tiny bullets. This is the default ingestion splitter for the system.

**Amazon-style**: product descriptions with bullet points and paragraphs chunk neatly with the same configuration.

## 🟡 Real Example Hindi mein
**Tariff System**: tariff notes में छोटी bullet lines, लंबे legal paragraphs और text में बदली tables मिली होती हैं। Recursive splitter (800 chars, 100 overlap) ज़्यादातर legal paragraphs को पूरा रखता है, बहुत लंबे paragraphs को sentence या word सीमा पर तोड़ता है और छोटे bullets को जोड़ देता है। यही system का default ingestion splitter है।

**Amazon-style**: bullet points और paragraphs वाले product descriptions इसी configuration से साफ़ chunk होते हैं।

---

## 💻 Code Example — Basic
```python
# Runs offline: a compact recursive splitter (no libraries) to show the algorithm
def recursive_split(text: str, size: int = 200, seps: tuple[str, ...] = ("\n\n", "\n", ". ", " ")) -> list[str]:
    """Split text into pieces <= size, preferring the earliest separator in `seps`."""
    if len(text) <= size:  # already small enough
        return [text]
    if not seps:  # no separators left: hard cut by characters
        return [text[i:i + size] for i in range(0, len(text), size)]
    sep, rest = seps[0], seps[1:]  # current separator and deeper ones
    parts = text.split(sep)  # split on the biggest separator
    chunks: list[str] = []  # output
    buf = ""  # accumulator for merging small parts
    for part in parts:
        candidate = f"{buf}{sep}{part}" if buf else part  # try to append to the buffer
        if len(candidate) <= size:
            buf = candidate  # still fits: keep merging
            continue
        if buf:
            chunks.append(buf)  # flush what we have
            buf = ""
        if len(part) <= size:
            buf = part  # start a new buffer with this part
        else:
            chunks.extend(recursive_split(part, size, rest))  # too big: go deeper
    if buf:
        chunks.append(buf)  # flush the remainder
    return chunks


doc = ("Headphones are under 8518.30. They include earphones.\n\n"
       "Smartphones are under 8517.13. " + "Long clause about accessories. " * 12 + "\n\nShort note.")
for i, c in enumerate(recursive_split(doc, 120)):
    print(i, len(c), repr(c[:50]))
```

## 💻 Code Example — Advanced
```python
# Production: LangChain splitter wrapped with validation, metadata, stats, async, error handling
import asyncio
import logging
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

log = logging.getLogger("recursive_chunker")


def build_splitter(chunk_size: int = 800, chunk_overlap: int = 100, by_tokens: bool = False) -> RecursiveCharacterTextSplitter:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    if by_tokens:  # measure sizes in tokens instead of characters
        return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # add ". " so sentences are preferred over words
        add_start_index=True,  # stores "start_index" in metadata for citations
    )


def split_documents(docs: list[Document], **kw: Any) -> list[Document]:
    splitter = build_splitter(**kw)
    try:
        chunks = splitter.split_documents(docs)  # keeps each document's metadata on its chunks
    except Exception:
        log.exception("splitting failed")
        raise
    sizes = [len(c.page_content) for c in chunks]
    log.info("chunks=%d min=%d max=%d", len(chunks), min(sizes, default=0), max(sizes, default=0))
    return chunks


async def asplit_documents(docs: list[Document], **kw: Any) -> list[Document]:
    return await asyncio.to_thread(split_documents, docs, **kw)  # do not block the event loop


if __name__ == "__main__":
    d = Document(page_content="Headphones are under 8518.30.\n\n" * 100, metadata={"source": "tariff.pdf"})
    out = asyncio.run(asplit_documents([d], chunk_size=400, chunk_overlap=50))
    print(len(out), out[0].metadata)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from langchain_core.documents import Document
from pydantic import BaseModel, Field

app = FastAPI()


class SplitReq(BaseModel):
    text: str = Field(min_length=1)
    source: str = "upload"
    chunk_size: int = Field(800, ge=100, le=4000)
    chunk_overlap: int = Field(100, ge=0, le=1000)


@app.post("/chunk/recursive")
async def chunk(req: SplitReq) -> dict:
    docs = await asplit_documents([Document(page_content=req.text, metadata={"source": req.source})],
                                  chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
    return {"count": len(docs), "preview": [d.page_content[:80] for d in docs[:5]]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# The standard LangChain RAG ingest path:
from langchain_community.document_loaders import PyPDFLoader   # pip install langchain-community pypdf

docs = PyPDFLoader("tariff_2026.pdf").load()                    # one Document per page
chunks = build_splitter(800, 100).split_documents(docs)         # recursive splitting
# vector_store.add_documents(chunks)
# For other languages: RecursiveCharacterTextSplitter.from_language(Language.MARKDOWN / PYTHON / ...)
# In LangGraph: put this in an offline ingest script; the graph itself only retrieves.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting chunks to be exactly chunk_size
```python
# Wrong: assert all(len(c) == 800 for c in chunks)
# Right: chunk_size is a MAXIMUM; sizes vary because boundaries are respected
assert all(len(c) <= 800 for c in chunks)
```

❌ Mistake 2: Using the default separators on text with a different structure
```python
# Wrong: Hindi text uses "।" as the sentence end; default separators never split there
# Right: add it
RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "। ", ". ", " ", ""])
```

---

## 🧠 Tricky Interview Question

**Q**: "You set chunk_size=1000 and chunk_overlap=200, but one chunk in your index has 1,150 characters. Is that a bug?"

**Answer**: Not necessarily. Possible reasons: (1) `chunk_size` in LangChain is measured by the length function, and a token-based length function means 1,150 characters can be under the token limit; (2) a single unbreakable piece (a long URL or string without separators) can exceed the limit when the last separator `""` was removed from the list; (3) your own post-processing (for example prepending headings) added characters. Check `length_function`, the separators list and any metadata prepending.

---

## ⚫ Interview Questions + Answers

Q1: What is the default separator order?
A1: Paragraph break `"\n\n"`, line break `"\n"`, space `" "`, then empty string (characters).

Q2: Why is it called recursive?
A2: If a piece is still larger than `chunk_size`, it is split again using the next separator, recursively.

Q3: What does `chunk_overlap` do here?
A3: Repeats the tail of one chunk at the start of the next to keep context across boundaries.

Q4: How do you make it token-aware?
A4: Use `RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)` so size and overlap are counted in tokens.

Q5: How would you adapt it for legal documents with numbered clauses?
A5: Add clause patterns as separators (for example `"\n\n"`, `"\nArticle "`, `"\n(a) "`) with `is_separator_regex=True`, keep overlap around 10-15 percent, prepend the clause heading to each chunk, and validate with questions about exceptions and cross-references.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- General prose, mixed documents, you need a robust default

❌ Avoid when:
- Strongly structured data (Markdown headers, code, tables) where dedicated splitters preserve structure better
- You need semantic topic boundaries (see semantic chunking)

---

## 📊 Visual Diagram
```
 text ──split "\n\n"──► [P1 small][P2 small][P3 HUGE][P4 small]
                          └─ merge ─┘          │ too big
                                              split "\n" ──► [L1][L2][L3 big]
                                                                      │ split ". "
                                                                      ▼
                                                                [S1][S2][S3]
 final: [P1+P2][L1+L2][S1][S2+S3][P4]    each <= chunk_size, + overlap
```

---

## 💰 Cost Impact
- Same embedding cost as fixed chunking for the same total text, but better boundaries mean fewer retrieved chunks are needed for a correct answer, so prompts are smaller.
- Example: 100K source tokens, 800-char chunks (about 200 tokens), 100-char overlap gives about 570 chunks and about 114K embedded tokens. k=4 gives about 800 prompt tokens.
- Optimise: strip boilerplate first, use a modest overlap (10-15 percent), choose size by evaluation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Separator | Text pattern used to split | बाँटने का pattern |
| Recursive | Apply the same step to leftovers | बचे हुए पर वही step दोबारा |
| chunk_size | Maximum chunk length | Chunk की अधिकतम लंबाई |
| chunk_overlap | Repeated boundary text | दोहराया गया border text |
| length_function | How size is measured | Size नापने का तरीका |
| add_start_index | Store start offset | Start offset सहेजना |

---

## ⚡ 3-Line Summary
English: Recursive splitting tries paragraph, line, sentence, word, character in order until chunks fit. It is the best general default because it respects structure and enforces a size cap. Tune size and overlap with evaluation.
Hindi: Recursive splitting paragraph, line, sentence, word, character क्रम से आज़माती है जब तक chunks फिट न हों। यह सबसे अच्छा general default है क्योंकि structure का सम्मान करती है और size की सीमा लागू करती है। Size और overlap को evaluation से tune करो।

---

## ➡️ Next Topic
**159. Semantic Chunking** — split where the meaning changes, using embeddings.
