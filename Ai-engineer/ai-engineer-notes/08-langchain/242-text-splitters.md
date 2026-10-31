---

# 242. Text Splitters
# हिंदी में: Text Splitters

---

## 🔵 Simple Definition (English)
A text splitter cuts long documents into smaller chunks (with optional overlap) that fit embedding and context limits. The recommended default is `RecursiveCharacterTextSplitter`, which tries paragraph, line, sentence, then word boundaries.

## 🔵 सरल परिभाषा (Hindi)
Text splitter लंबे documents को छोटे chunks (overlap के साथ) में काटता है ताकि embedding और context limits में fit हों। Default `RecursiveCharacterTextSplitter` है, जो पहले paragraph, फिर line, sentence, और word की सीमाओं पर काटता है।

---

## 🔴 Problem it Solves
A 300-page tariff PDF cannot go into one prompt or one embedding. Chunks too big = vague embeddings and wasted tokens; too small = lost context; cutting mid-sentence = broken meaning. Good splitting is the biggest lever on retrieval quality.

## 🔴 यह क्यों बना? (Hindi)
300 पन्ने का tariff PDF एक prompt या एक embedding में नहीं जा सकता। Chunk बहुत बड़ा = धुंधला embedding और बेकार tokens; बहुत छोटा = context खो जाता है; sentence के बीच कटा = मतलब टूटता है। अच्छा splitting retrieval quality का सबसे बड़ा lever है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick splitter + chunk_size + chunk_overlap (e.g., 800 / 100)
Step 2 → Recursive: try separators in order ["\n\n", "\n", " ", ""]
Step 3 → Split on the first separator; merge pieces up to chunk_size
Step 4 → Any piece still too big -> recurse with the next separator
Step 5 → Overlap: repeat the last N characters in the next chunk
Step 6 → split_documents(docs) keeps metadata on each chunk
Step 7 → Add start_index metadata if needed (add_start_index=True)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Splitter + chunk_size + chunk_overlap चुनो (जैसे 800 / 100)
Step 2 → Recursive: separators क्रम से आज़माओ ["\n\n", "\n", " ", ""]
Step 3 → पहले separator पर बाँटो; टुकड़े chunk_size तक जोड़ो
Step 4 → अभी भी बड़ा टुकड़ा हो तो अगले separator से दोबारा
Step 5 → Overlap: अगले chunk में पिछले N characters दोहराओ
Step 6 → split_documents(docs) हर chunk पर metadata रखता है
Step 7 → ज़रूरत हो तो add_start_index=True
```

---

## 🟡 Real World Example
**Tariff Classification System**: tariff text is hierarchical (Section > Chapter > Heading). Use `MarkdownHeaderTextSplitter` or a custom regex split on "Heading 85.18" so each chunk is one heading with its notes; then size-limit with RecursiveCharacter (chunk_size ~1000, overlap 100). **Zomato**: menu items split per dish, not mid-description.

## 🟡 Real Example Hindi mein
**Tariff System**: tariff text hierarchical है (Section > Chapter > Heading)। `MarkdownHeaderTextSplitter` या "Heading 85.18" पर custom regex split करो ताकि हर chunk एक heading + उसके notes हो; फिर RecursiveCharacter से size limit (chunk_size ~1000, overlap 100)। **Zomato**: menu को dish के हिसाब से split, description के बीच नहीं।

---

## 💻 Code Example — Basic
```python
# Runs with: pip install langchain-text-splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

text = (
    "Chapter 85. Electrical machinery and equipment.\n\n"
    "85.17 Telephone sets, including smartphones. Parts thereof.\n\n"
    "85.18 Microphones, headphones, earphones. Whether or not combined with a microphone. "
    "Includes wireless Bluetooth earbuds with charging cases.\n\n"
    "Chapter 64. Footwear, gaiters and the like."
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,  # max characters per chunk (use small for demo)
    chunk_overlap=20,  # characters repeated between chunks
    add_start_index=True,  # store position in metadata
)

chunks = splitter.split_text(text)  # list[str]
for i, c in enumerate(chunks):
    print(i, len(c), repr(c[:60]))  # see sizes and starts

docs = splitter.split_documents([Document(page_content=text, metadata={"source": "tariff.pdf"})])
print(docs[0].metadata)  # {'source': 'tariff.pdf', 'start_index': 0}
```

## 💻 Code Example — Advanced
```python
# Token-aware, structure-aware splitting with validation and async wrapper
import asyncio
import re
import tiktoken
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

enc = tiktoken.get_encoding("cl100k_base")  # tokenizer for length function

def tok_len(s: str) -> int:
    return len(enc.encode(s))  # length measured in tokens, not characters

HEADING = re.compile(r"(?m)^(?=\d{2}\.\d{2}\s)")  # lines like "85.18 ..."

def split_tariff(doc: Document, max_tokens: int = 300, overlap: int = 30) -> list[Document]:
    """1) split on tariff headings, 2) sub-split large headings by tokens."""
    parts = [p for p in HEADING.split(doc.page_content) if p.strip()]  # heading-level pieces
    sub = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens, chunk_overlap=overlap, length_function=tok_len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    out: list[Document] = []
    for part in parts:
        m = re.match(r"(\d{2}\.\d{2})", part)  # heading code if present
        for piece in sub.split_text(part):
            out.append(Document(
                page_content=piece,
                metadata={**doc.metadata, "heading": m.group(1) if m else None},
            ))
    if any(tok_len(d.page_content) > max_tokens * 1.2 for d in out):  # sanity check
        raise ValueError("chunk exceeds token budget")
    return out

async def split_many(docs: list[Document]) -> list[Document]:
    parts = await asyncio.gather(*(asyncio.to_thread(split_tariff, d) for d in docs))  # CPU off the loop
    return [c for p in parts for c in p]
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class SplitReq(BaseModel):
    text: str
    chunk_size: int = Field(800, ge=100, le=4000)
    overlap: int = Field(100, ge=0, le=500)

@app.post("/split-preview")
async def split_preview(req: SplitReq) -> dict:
    s = RecursiveCharacterTextSplitter(chunk_size=req.chunk_size, chunk_overlap=req.overlap)
    chunks = s.split_text(req.text)  # fast, CPU light for modest input
    return {"count": len(chunks), "sizes": [len(c) for c in chunks]}
```

---

## 🔗 LangChain / LangGraph Connection
Splitters live in the `langchain-text-splitters` package: RecursiveCharacter, Character, Token (`TokenTextSplitter`), Markdown/HTML header splitters, Language-aware code splitters (`RecursiveCharacterTextSplitter.from_language`), and semantic splitters (`langchain_experimental` SemanticChunker). In LangGraph ingestion graphs, "split" is a node between "load" and "index". `ParentDocumentRetriever` uses two splitters (small child chunks for search, large parents for context).

```python
# splitter = RecursiveCharacterTextSplitter.from_language(Language.PYTHON, chunk_size=500, chunk_overlap=50)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using chunk_size in characters while thinking in tokens
```python
# Wrong: chunk_size=8000 (characters) for an embedding model with 512-token limit -> truncation
# Right: length_function=token_len, or chunk_size ~ 4 chars per token
```

❌ Mistake 2: Zero overlap and mid-sentence cuts
```python
# Wrong: CharacterTextSplitter(separator="", chunk_size=500, chunk_overlap=0)
# Right: RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
```

---

## 🧠 Tricky Interview Question
**Q**: "Reducing chunk size from 1000 to 300 tokens lowered answer quality. Why?"

**Answer**: Smaller chunks lose surrounding context (a duty rate separated from its heading and exclusions), so retrieval returns fragments that look relevant but cannot answer. Also top-k now covers less text. Fixes: parent-document retrieval, keep headings in chunk text/metadata, bigger overlap, or increase k and rerank.

---

## ⚫ Interview Questions + Answers

Q1: What does chunk_overlap do? (Easy)
A1: Repeats text at chunk edges so ideas cut at a boundary appear whole in at least one chunk.

Q2: Why RecursiveCharacterTextSplitter by default? (Easy)
A2: It respects natural boundaries (paragraphs, sentences) before falling back to characters.

Q3: How to choose chunk size? (Medium)
A3: Match the embedding model's limit, the nature of questions (fact lookup = smaller, reasoning = larger), then evaluate recall@k on a labelled set for sizes 300/600/1000.

Q4: What is semantic chunking? (Medium)
A4: Splits where embedding similarity between adjacent sentences drops. Better coherence, costs embedding calls and is slower.

Q5: Explain parent-document retrieval. (Hard)
A5: Index small child chunks for precise matching, but return their larger parent chunk to the LLM for context. LangChain's `ParentDocumentRetriever` stores parents in a docstore and children in the vector store.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any document longer than your embedding/context budget

❌ Avoid when:
- Records are already atomic (FAQ entries, CSV rows): don't split further

---

## 📊 Visual Diagram
```
 Long text ─► split on "\n\n" ─► too big? ─► split on "\n" ─► too big? ─► split on " "
                    │
                    ▼
   chunk1 [.......xxx]
   chunk2        [xxx.......yyy]      xxx = overlap
   chunk3                  [yyy.......]
```

---

## 💰 Cost Impact
Chunking sets embedding cost (total tokens x embedding price; overlap adds ~10-15 percent) and per-query LLM cost (k x chunk_size tokens). Example: k=5 with 1,000-token chunks = 5,000 context tokens per query; cutting to 500-token chunks halves that. Optimise: right-size chunks, small overlap, dedupe repeated boilerplate, rerank then send fewer chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Piece of text | Text का टुकड़ा |
| Overlap | Shared edge text | साझा किनारे का text |
| Separator | Boundary marker | सीमा चिह्न |
| Semantic chunking | Split by meaning | अर्थ के आधार पर |
| Parent document | Larger context chunk | बड़ा context chunk |

---

## ⚡ 3-Line Summary
English: Splitters cut documents into overlapping chunks that fit limits. Use RecursiveCharacterTextSplitter, measure size in tokens, and respect document structure. Chunking strongly affects retrieval quality and cost.
Hindi: Splitters documents को overlap वाले chunks में काटते हैं। RecursiveCharacterTextSplitter लो, size tokens में नापो और document structure का सम्मान करो। Chunking retrieval quality और cost दोनों को प्रभावित करती है।

---

## ➡️ Next Topic
**243. Embeddings in LangChain** — turning chunks into vectors with the `Embeddings` interface.
