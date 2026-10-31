---

# 167. chunk_overlap — How to Choose
# हिंदी में: chunk_overlap — कैसे चुनें

---

## 🔵 Simple Definition (English)
`chunk_overlap` is how much text two neighbouring chunks share. If chunk 1 ends with "...duty is 10%" and chunk 2 starts with the same sentence, an answer at the border is not lost. A common choice is 10-20% of `chunk_size`. Overlap is cheap insurance, not a free lunch.

## 🔵 सरल परिभाषा (Hindi)
`chunk_overlap` बताता है कि दो पास-पास वाले chunks कितना text साझा करते हैं। Chunk 1 "...duty 10%" पर खत्म हो और chunk 2 उसी वाक्य से शुरू हो, तो border पर जवाब नहीं कटता। आम तौर पर `chunk_size` का 10-20%। Overlap सस्ता बीमा है, मुफ़्त नहीं।

---

## 🔴 Problem it Solves
- A hard cut can separate a question from its answer, a condition from its rule, or a pronoun from its noun ("It attracts 10%" - what is "It"?).
- Facts that sit on the border belong to neither chunk fully, so neither is retrieved well.
- Overlap repeats the border text in both chunks so at least one chunk has the whole idea.

## 🔴 यह क्यों बना? (Hindi)
- Hard cut सवाल को जवाब से, शर्त को नियम से, या pronoun को noun से अलग कर देता है ("It attracts 10%" - "It" कौन?)।
- Border पर बैठा fact किसी chunk में पूरा नहीं होता।
- Overlap border text दोनों chunks में दोहराता है, ताकि कम से कम एक chunk में पूरा idea रहे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Splitter fills chunk 1 up to chunk_size
Step 2 → It steps BACK by chunk_overlap units
Step 3 → Chunk 2 starts at that point, so the last part of chunk 1 repeats at the start of chunk 2
Step 4 → Repeat to the end of the document
Step 5 → Start with overlap = 10-15% of chunk_size
Step 6 → Check duplicates: more overlap = more chunks = more storage + embedding tokens
Step 7 → Evaluate: does recall improve at border questions? If not, reduce overlap
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Splitter chunk 1 को chunk_size तक भरता है
Step 2 → फिर chunk_overlap जितना पीछे लौटता है
Step 3 → Chunk 2 वहाँ से शुरू होता है, इसलिए chunk 1 का अंतिम हिस्सा chunk 2 की शुरुआत में दोहराता है
Step 4 → Document के अंत तक दोहराओ
Step 5 → 10-15% overlap से शुरू करो
Step 6 → ज़्यादा overlap = ज़्यादा chunks = ज़्यादा cost
Step 7 → Border questions पर recall सुधरा या नहीं, जाँचो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A passage reads "Smartphones are dutiable at 10%. This rate does not apply to refurbished units." With a hard cut between the sentences, the second chunk says "This rate does not apply to refurbished units" - which rate? One sentence of overlap fixes it, and the classifier correctly applies the exception.

**Amazon style**: A return policy says "Returns accepted within 30 days." (end of chunk 1) and "except for opened software." (start of chunk 2). Overlap keeps the exception attached.

## 🟡 Real Example Hindi mein
**Tariff System**: "Smartphones पर 10% duty है। यह rate refurbished units पर लागू नहीं होता।" दोनों वाक्यों के बीच cut हो तो दूसरे chunk में "यह rate" किसका? एक वाक्य का overlap इसे ठीक करता है और exception सही लागू होता है।

**Amazon**: "30 दिन में return" chunk 1 के अंत में और "खुले software को छोड़कर" chunk 2 में। Overlap exception को जोड़े रखता है।

---

## 💻 Code Example — Basic
```python
# Basic: see overlap in action with a sentence-based chunker (pure Python)
text = (  # sample policy text
    "Smartphones are dutiable at ten percent. "
    "This rate does not apply to refurbished units. "
    "Batteries are dutiable at twenty percent. "
    "Chargers are dutiable at five percent."
)  # four sentences

def sentences(t: str) -> list[str]:  # naive sentence splitter
    return [s.strip() + "." for s in t.split(".") if s.strip()]  # keep the full stop

def chunk(sents: list[str], per_chunk: int, overlap: int) -> list[list[str]]:  # sentence windows
    if overlap >= per_chunk:  # would loop forever
        raise ValueError("overlap must be < per_chunk")  # guard
    step = per_chunk - overlap  # how far we move each time
    return [sents[i:i + per_chunk] for i in range(0, len(sents), step)  # windows
            if sents[i:i + per_chunk]]  # skip empty window

sents = sentences(text)  # list of sentences
print("NO overlap:")  # header
for c in chunk(sents, 2, 0):  # overlap = 0
    print("  ", " ".join(c))  # exception sentence is separated from its rule
print("WITH overlap=1:")  # header
for c in chunk(sents, 2, 1):  # overlap = 1 sentence
    print("  ", " ".join(c))  # rule + exception stay together in some chunk
```

## 💻 Code Example — Advanced
```python
# Production: character-level overlap chunker that snaps to sentence boundaries,
# reports duplication overhead, and has an async batch version.
from __future__ import annotations  # modern hints

import asyncio  # async batching
import re  # sentence boundaries
from dataclasses import dataclass  # result type


@dataclass
class OverlapReport:  # stats about chosen overlap
    n_chunks: int  # chunks produced
    original_chars: int  # chars in the source
    stored_chars: int  # chars across chunks
    overhead_pct: float  # extra storage caused by overlap


def validate(size: int, overlap: int) -> None:  # shared validation
    if size <= 0:  # size must be positive
        raise ValueError("chunk_size must be > 0")  # error
    if not 0 <= overlap < size:  # overlap must be smaller than size
        raise ValueError("0 <= chunk_overlap < chunk_size required")  # error
    if overlap > 0.5 * size:  # suspicious setting
        raise ValueError("overlap above 50% of size wastes tokens")  # guard rail


def split_with_overlap(text: str, size: int = 400, overlap: int = 60) -> list[str]:
    """Slide a window; start each new chunk at a sentence start inside the overlap zone."""
    validate(size, overlap)  # check settings
    chunks: list[str] = []  # output
    start = 0  # window start
    while start < len(text):  # until the end
        end = min(start + size, len(text))  # window end
        window = text[start:end]  # raw window
        if end < len(text):  # not the last window
            cut = max(window.rfind(". "), window.rfind("\n"))  # last sentence break
            if cut > size * 0.5:  # only snap if not too early
                end = start + cut + 1  # end after the full stop
                window = text[start:end]  # shorter window
        chunks.append(window.strip())  # save chunk
        if end >= len(text):  # finished
            break  # stop
        nxt = end - overlap  # naive next start
        m = re.search(r"(?<=[.!?]) ", text[nxt:end])  # first sentence start in overlap zone
        start = nxt + m.end() if m else nxt  # snap to sentence start if found
        if start <= end - size:  # safety: always make progress
            start = end  # avoid an infinite loop
    return chunks  # all chunks


def report(text: str, chunks: list[str]) -> OverlapReport:  # measure overhead
    stored = sum(len(c) for c in chunks)  # total chars stored
    over = (stored - len(text)) / max(1, len(text)) * 100  # percent extra
    return OverlapReport(len(chunks), len(text), stored, round(over, 1))  # report


async def split_many(docs: list[str], size: int, overlap: int) -> list[list[str]]:  # async batch
    async def one(d: str) -> list[str]:  # wrapper for a single doc
        return await asyncio.to_thread(split_with_overlap, d, size, overlap)  # off-loop
    return await asyncio.gather(*(one(d) for d in docs))  # run all concurrently


if __name__ == "__main__":  # demo
    doc = ("Smartphones are dutiable at ten percent. This rate does not apply to refurbished units. " * 6).strip()  # text
    for ov in (0, 30, 60):  # compare overlaps
        cs = split_with_overlap(doc, size=200, overlap=ov)  # chunk
        print(ov, report(doc, cs))  # overhead grows with overlap
```

---

## 🟠 FastAPI Integration
An endpoint that previews the effect of an overlap setting before you re-index a whole collection. It returns chunk count and storage overhead so the team can budget embedding tokens.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app


class PreviewRequest(BaseModel):  # request body
    text: str = Field(min_length=1)  # document
    chunk_size: int = Field(default=400, ge=50, le=4000)  # size
    chunk_overlap: int = Field(default=60, ge=0)  # overlap


@app.post("/chunk/preview")  # route
async def preview(req: PreviewRequest) -> dict:  # handler
    try:  # validation errors become 422
        chunks = split_with_overlap(req.text, req.chunk_size, req.chunk_overlap)  # split
    except ValueError as exc:  # bad settings
        raise HTTPException(422, str(exc))  # tell caller
    rep = report(req.text, chunks)  # overhead stats
    return {"chunks": rep.n_chunks, "overhead_pct": rep.overhead_pct}  # response
```

---

## 🔗 LangChain / LangGraph Connection
Every LangChain splitter takes `chunk_overlap` next to `chunk_size`. It must be smaller than `chunk_size` or LangChain raises a ValueError.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75)  # 15% overlap
docs = splitter.create_documents(["long tariff text ..."])  # Documents with metadata
# MarkdownHeaderTextSplitter and HTMLHeaderTextSplitter have no overlap because
# they split at natural section borders; overlap is added by the second-stage recursive splitter.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Overlap equal to or bigger than chunk_size
✅ Correct: Keep overlap well below size (10-20%).

```python
# Wrong - raises ValueError in LangChain (overlap larger than chunk size)
RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=250)  # invalid

# Right
RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)  # 15%
```

❌ Mistake 2: Using 50% overlap "to be safe"
✅ Correct: It doubles storage and embedding cost and creates near-duplicate results that fill your top_k.

❌ Mistake 3: Applying overlap to structure-based chunks (one record per chunk) where it adds only duplicates.
✅ Correct: Use zero overlap for atomic chunks like FAQ entries.

---

## 🧠 Tricky Interview Question
**Q**: "After raising overlap from 50 to 200 tokens, your top-5 results contain 3 almost identical chunks and the LLM answer got worse. Why?"

**Answer**: With large overlap, neighbouring chunks share most of their text, so their embeddings are almost identical and they rank together. The top-k fills with near-duplicates and pushes out diverse, useful chunks. The LLM also pays for repeated text. Fix: reduce overlap to 10-15%, deduplicate at query time (MMR - maximal marginal relevance, or similarity threshold between results), and store chunk ids/neighbour links so you can merge adjacent chunks instead of duplicating.

---

## ⚫ Interview Questions + Answers

Q1: What is chunk_overlap?
A1: The amount of text shared between consecutive chunks, so information at the border is not lost.

Q2: What overlap would you start with?
A2: 10-15% of chunk_size (for example 50-75 tokens for 500). Then evaluate.

Q3: What are the downsides of high overlap?
A3: More chunks, more embedding and storage cost, near-duplicate retrieval results, and wasted prompt tokens.

Q4: When is overlap unnecessary?
A4: When chunks follow natural boundaries (one FAQ, one tariff entry, one review) or when you split by headings.

Q5: (Hard) Alternatives to overlap for keeping context at borders?
A5: Sentence-boundary splitting, parent-child (small-to-big) retrieval, window retrieval (fetch neighbour chunks by id), contextual chunk headers (prepend the heading path or an LLM-written context sentence), and late chunking. These often beat large overlap at lower cost.

---

## 🔷 When to Use + When Not to Use
✅ Use overlap when:
- Text is continuous prose (laws, notes, articles) with long sentences and references
- Fixed-size or recursive splitting can cut mid-idea

❌ Avoid (or use 0) when:
- Chunks are atomic records (FAQ, product, review)
- Splitting by headings/sections already respects meaning
- Storage and embedding budget is very tight

---

## 📊 Visual Diagram
```
 text:   [ A A A A A A A A | B B B B B B B B | C C C C ... ]

 overlap = 0:
   chunk1: [A A A A A A A A]
   chunk2:                 [B B B B B B B B]      <- border fact may be cut

 overlap = 2:
   chunk1: [A A A A A A A A]
   chunk2:               [A A B B B B B B B B]    <- shared "A A" protects the border
   chunk3:                                 [B B C C C C ...]
```

---

## 💰 Cost Impact
- Extra tokens = about overlap / (size - overlap). Size 500, overlap 75 gives about 17.6% more tokens to embed and store. Overlap 250 gives 100% more.
- Example: 50M tokens corpus, small embedding model at $0.02 per 1M tokens: 15% overlap adds 7.5M tokens = $0.15 one-time. Cheap to embed, but near-duplicates also increase prompt tokens at query time if they land in top_k.
- Optimise: 10-15% overlap, MMR/deduplicate before building the prompt, content-hash chunks so re-indexing skips unchanged ones.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| chunk_overlap | Shared text between chunks | Chunks के बीच साझा text |
| Border loss | Info cut at chunk edge | Edge पर जानकारी कटना |
| MMR | Rerank for diversity | विविधता वाला reranking |
| Near-duplicate | Almost same chunk | लगभग एक जैसे chunks |
| Overhead | Extra storage from overlap | Overlap से बढ़ी storage |
| Window retrieval | Fetch neighbouring chunks | पड़ोसी chunks लाना |

---

## ⚡ 3-Line Summary
English: Overlap repeats border text so ideas are not cut between chunks. Use 10-15% of chunk_size and never more than about 20-25%. Too much overlap creates duplicates and extra cost.
Hindi: Overlap border text दोहराता है ताकि idea chunks के बीच न कटे। chunk_size का 10-15% रखो, 20-25% से ज़्यादा नहीं। ज़्यादा overlap duplicates और extra cost बनाता है।

---

## ➡️ Next Topic
**168. Chunking for Different Doc Types** - code, tables, chat logs and legal text each need their own strategy.
