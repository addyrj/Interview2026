---

# 156. Why Chunking Matters
# हिंदी में: Chunking क्यों ज़रूरी है

---

## 🔵 Simple Definition (English)
Chunking means splitting long documents into smaller pieces (chunks) before embedding and storing them. Retrieval then returns only the few chunks relevant to a question. Chunk quality decides RAG quality: bad chunks mean bad answers, even with the best model.

## 🔵 सरल परिभाषा (Hindi)
Chunking का मतलब है लंबे documents को embedding और storage से पहले छोटे टुकड़ों (chunks) में बाँटना। Retrieval सिर्फ़ सवाल से जुड़े कुछ chunks लौटाता है। Chunk की quality RAG की quality तय करती है: खराब chunks का मतलब खराब answers, चाहे model कितना भी अच्छा हो।

---

## 🔴 Problem it Solves
1. Embedding models have input limits (for example 8,191 tokens for OpenAI embeddings), and long text gives a blurry single vector.
2. LLM context is limited and costly: sending a 200-page PDF per question is slow and expensive, and models lose details in the middle ("lost in the middle").
3. Search needs precision: a vector for the whole document cannot point at the one paragraph with the answer.

## 🔴 यह क्यों बना? (Hindi)
1. Embedding models की input limit होती है (जैसे OpenAI embeddings में 8,191 tokens), और लंबे text का एक vector धुँधला होता है।
2. LLM context सीमित और महँगा है: हर सवाल पर 200-page PDF भेजना धीमा और महँगा है, और models बीच की details भूल जाते हैं।
3. Search को precision चाहिए: पूरे document का vector उस एक paragraph को नहीं पकड़ सकता जिसमें जवाब है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load document (PDF, HTML, Markdown) and extract clean text
Step 2 → Split into chunks (size + overlap + boundaries chosen by strategy)
Step 3 → Attach metadata (source, page, section, year) to each chunk
Step 4 → Embed each chunk -> vector, store in the vector DB
Step 5 → Query: embed question -> retrieve top-k chunks
Step 6 → Put only those chunks in the LLM prompt -> grounded answer with citations
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Document (PDF, HTML, Markdown) load करो और साफ text निकालो
Step 2 → Chunks में बाँटो (strategy से size + overlap + boundaries तय)
Step 3 → हर chunk में metadata जोड़ो (source, page, section, year)
Step 4 → हर chunk को embed करो -> vector, vector DB में रखो
Step 5 → Query: सवाल embed करो -> top-k chunks निकालो
Step 6 → सिर्फ़ वही chunks LLM prompt में डालो -> citations के साथ grounded answer
```

---

## 🟡 Real World Example
**Tariff Classification System**: a 300-page tariff document has a rule: "Headphones 8518.30 except those with microphones classified under 8518.40." If chunking cuts the sentence in half, one chunk says "Headphones 8518.30" and the exception sits in another, so the retriever may return only the first half and the LLM confidently picks the wrong code. Good chunking keeps each rule with its exception.

**Zomato AI**: a restaurant's menu chunked per dish (name, price, allergens together) answers "is the paneer tikka nut-free?" correctly; chunked by fixed 500 characters it could split allergens from the dish name.

## 🟡 Real Example Hindi mein
**Tariff System**: 300-page tariff document में नियम है: "Headphones 8518.30, सिवाय microphone वालों के जो 8518.40 में आते हैं।" अगर chunking वाक्य को बीच से काट दे तो एक chunk में सिर्फ़ "Headphones 8518.30" होगा और अपवाद दूसरे chunk में, retriever आधा हिस्सा लाएगा और LLM आत्मविश्वास से गलत code चुनेगा। अच्छी chunking हर नियम को उसके अपवाद के साथ रखती है।

**Zomato AI**: menu को हर dish (नाम, कीमत, allergens साथ) के हिसाब से chunk करने पर "क्या paneer tikka में nuts नहीं हैं?" का सही जवाब मिलता है; 500 characters पर fixed काटने से allergens dish के नाम से अलग हो सकते हैं।

---

## 💻 Code Example — Basic
```python
# Runs offline: compare "whole document" vs "chunks" for retrieval precision and prompt size
import re

DOC = (
    "Chapter 85 covers electrical machinery. "
    "Headphones and earphones are classified under 8518.30, except those with microphones, "
    "which are classified under 8518.40. "
    "Chapter 61 covers knitted apparel. Cotton T-shirts are classified under 6109.10. "
    "Chapter 94 covers furniture. Wooden chairs are classified under 9401.61."
)


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9.]+", text.lower()))  # crude word set (stand-in for embeddings)


def overlap(query: str, text: str) -> int:
    return len(tokens(query) & tokens(text))  # shared words = toy relevance score


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=\.)\s+(?=[A-Z])", text) if s.strip()]  # naive splitter


query = "code for headphones with microphones"
chunks = split_sentences(DOC)  # chunk = one sentence in this toy
best = max(chunks, key=lambda c: overlap(query, c))  # pick the most relevant chunk
print("Whole doc words :", len(DOC.split()))  # what you would send without chunking
print("Best chunk words:", len(best.split()))  # what you send with chunking
print("Best chunk      :", best)
```

## 💻 Code Example — Advanced
```python
# Production: ingestion pipeline with chunk metadata, validation, async embedding, error handling
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable

log = logging.getLogger("chunking")


@dataclass
class Chunk:
    text: str
    source: str
    page: int
    index: int
    metadata: dict[str, str] = field(default_factory=dict)


def chunk_page(text: str, source: str, page: int, size: int = 800, overlap: int = 100) -> list[Chunk]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")  # otherwise the loop never advances
    out: list[Chunk] = []
    start, idx = 0, 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:  # skip empty pieces
            out.append(Chunk(piece, source, page, idx, {"year": "2026"}))
            idx += 1
        start += size - overlap  # slide forward with overlap
    return out


async def ingest(pages: dict[int, str], source: str,
                 embed_batch: Callable[[list[str]], Awaitable[list[list[float]]]]) -> int:
    chunks = [c for p, t in pages.items() for c in chunk_page(t, source, p)]
    stored = 0
    for i in range(0, len(chunks), 64):  # embed in batches of 64
        batch = chunks[i:i + 64]
        try:
            vecs = await embed_batch([c.text for c in batch])
        except Exception:
            log.exception("embedding batch failed at %d", i)
            continue  # keep ingesting the rest
        # await store.upsert(batch, vecs)   # write to your vector DB here
        stored += len(vecs)
    return stored


async def _fake_embed(texts: list[str]) -> list[list[float]]:
    return [[float(len(t))] for t in texts]  # stand-in for an embeddings API call


if __name__ == "__main__":
    print(asyncio.run(ingest({1: "Headphones are 8518.30. " * 200}, "tariff.pdf", _fake_embed)))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()


@app.post("/documents")
async def upload(file: UploadFile) -> dict:
    raw = (await file.read()).decode("utf-8", errors="ignore")  # demo: text files only
    if not raw.strip():
        raise HTTPException(status_code=400, detail="empty document")
    chunks = chunk_page(raw, file.filename or "upload", page=1)  # from Advanced example
    return {"chunks": len(chunks), "avg_chars": sum(len(c.text) for c in chunks) // max(1, len(chunks))}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-text-splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)  # sizes in characters by default
docs = splitter.create_documents([DOC], metadatas=[{"source": "tariff.pdf"}])  # list[Document]
# Documents flow into vector_store.add_documents(docs). In LangGraph, "ingest" is usually a separate
# offline job and "retrieve" is a node that reads from the store.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding whole documents
```python
# Wrong: one vector for 300 pages; also may exceed the embedding model's input limit
vector = embed(entire_pdf_text)
# Right: split first, embed each chunk
vectors = embed_batch([c.text for c in chunks])
```

❌ Mistake 2: Choosing chunk size once and never testing it
```python
# Wrong: copy 1000/200 from a blog and ship
# Right: evaluate recall@k for sizes 300/500/800/1200 on labelled questions, keep the best
for size in (300, 500, 800, 1200):
    print(size, evaluate(size))   # evaluate() = your retrieval benchmark
```

---

## 🧠 Tricky Interview Question

**Q**: "Retrieval returns the right document every time, yet the LLM often answers incorrectly. Is chunking involved?"

**Answer**: Yes, probably. The right document is not the right chunk. If chunks are too big, the answer is diluted among irrelevant text; if too small, the chunk lacks context (pronouns like "it" or "the above" lose meaning, or an exception is cut off). Measure at chunk level, not document level: check whether the retrieved chunks actually contain the answer. Fixes: tune size/overlap, split on structure (headings, paragraphs), prepend section titles to each chunk, retrieve small chunks but pass the parent section to the LLM.

---

## ⚫ Interview Questions + Answers

Q1: What is a chunk?
A1: A small piece of a document, embedded and stored as one retrievable unit.

Q2: Why not embed the whole document?
A2: Input limits, blurry vectors, poor precision, and sending it all to the LLM is slow and costly.

Q3: What is chunk overlap?
A3: Repeated text at the boundary between two chunks, so a sentence cut at the border still appears whole in at least one chunk. Typical overlap is 10-20 percent.

Q4: What happens when chunks are too small or too large?
A4: Too small: missing context and many noisy hits. Too large: diluted embeddings, more irrelevant tokens in the prompt, higher cost.

Q5: How do you pick a chunking strategy for a new corpus?
A5: Inspect the documents (structured Markdown/HTML, legal text, code, chat). Start with structure-aware splitting; fall back to recursive splitting with 500-1000 characters and 10-20 percent overlap. Build 50-200 labelled questions, evaluate recall@k and answer correctness for a few candidates, and also compare cost (tokens per answer). Iterate with the evaluation numbers rather than opinions.

---

## 🔷 When to Use + When Not to Use
✅ Chunk when:
- Documents are longer than a few hundred tokens
- You need citations and precise retrieval

❌ Avoid / minimise when:
- Documents are tiny (FAQ entries of 2-3 lines): each one is already a chunk
- The whole document fits cheaply in context and the question needs global reasoning (summaries)

---

## 📊 Visual Diagram
```
 300-page PDF
      │ split
      ▼
 [chunk1][chunk2][chunk3] ... [chunk900]   + metadata (page, section, year)
      │ embed
      ▼
 vectors in DB
      ▲
 question ─► embed ─► top-4 chunks ─► LLM prompt (≈1,200 tokens instead of 150,000)
```

---

## 💰 Cost Impact
- Sending a whole 300-page document (about 150,000 tokens) per question is slow and expensive and often exceeds context; sending 4 chunks of 300 tokens (about 1,200 tokens plus question and instructions) is roughly 100x fewer input tokens.
- Embedding cost is paid once per chunk; overlap increases it a little (10-20 percent more tokens embedded).
- Optimise: remove boilerplate (headers, footers) before chunking, dedupe repeated chunks, pick the smallest chunk size that keeps recall, and use a score threshold so low-relevance chunks never reach the prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Piece of a document | Document का टुकड़ा |
| Chunk size | Length of each chunk | Chunk की लंबाई |
| Overlap | Shared text between chunks | Chunks के बीच साझा text |
| Metadata | Data about a chunk | Chunk की जानकारी |
| Lost in the middle | LLM misses mid-context facts | बीच की बातें छूट जाना |
| Recall@k | Share of answers found in top k | Top k में जवाब मिलने का अनुपात |

---

## ⚡ 3-Line Summary
English: Chunking splits documents into retrievable pieces so RAG sends only relevant text to the LLM. Chunk size, overlap and boundaries strongly affect accuracy and cost. Test strategies with labelled questions.
Hindi: Chunking documents को retrieve होने लायक टुकड़ों में बाँटती है ताकि RAG LLM को सिर्फ़ relevant text भेजे। Chunk size, overlap और boundaries accuracy और cost को काफ़ी प्रभावित करते हैं। Labelled questions से strategies test करो।

---

## ➡️ Next Topic
**157. Fixed Size Chunking** — the simplest strategy: equal-size windows with overlap, and its limits.
