---

# 159. Semantic Chunking
# हिंदी में: Semantic Chunking (अर्थ के आधार पर टुकड़े)

---

## 🔵 Simple Definition (English)
Semantic chunking splits a document where the topic changes. It embeds sentences, compares neighbouring sentences, and starts a new chunk when similarity drops sharply. Chunks end up as coherent topics instead of arbitrary sizes.

## 🔵 सरल परिभाषा (Hindi)
Semantic chunking document को वहाँ बाँटती है जहाँ topic बदलता है। यह sentences को embed करती है, पास के sentences की similarity तुलना करती है, और similarity अचानक गिरने पर नया chunk शुरू करती है। Chunks मनमाने size की जगह एक topic वाले बनते हैं।

---

## 🔴 Problem it Solves
Size-based splitters can glue two unrelated topics into one chunk (blurry vector) or cut one topic into pieces. Semantic chunking aims for one idea per chunk, improving retrieval precision on long, varied documents.

## 🔴 यह क्यों बना? (Hindi)
Size-based splitters दो असंबंधित topics को एक chunk में जोड़ सकते हैं (धुँधला vector) या एक topic के टुकड़े कर सकते हैं। Semantic chunking हर chunk में एक idea रखने का लक्ष्य रखती है, जिससे लंबे और विविध documents में retrieval precision बढ़ती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split text into sentences
Step 2 → Embed each sentence (often with a small window of neighbours for context)
Step 3 → Compute distance between consecutive sentence embeddings (1 - cosine similarity)
Step 4 → Choose a breakpoint threshold (for example 95th percentile of distances)
Step 5 → Every distance above the threshold = a topic boundary
Step 6 → Group sentences between boundaries into chunks; enforce min/max size limits
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Text को sentences में बाँटो
Step 2 → हर sentence embed करो (अक्सर पड़ोसी sentences की छोटी window के साथ)
Step 3 → लगातार sentence embeddings की दूरी निकालो (1 - cosine similarity)
Step 4 → Breakpoint threshold चुनो (जैसे distances का 95वाँ percentile)
Step 5 → जो distance threshold से ऊपर हो = topic की सीमा
Step 6 → सीमाओं के बीच के sentences को chunks में समूहित करो; min/max size लागू करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a long "General Notes" section jumps from the definition of electronics, to rules for textiles, to origin rules. Semantic chunking breaks at those topic switches so each chunk is purely about one subject. A query on textile origin rules retrieves clean chunks instead of a blend.

**Zomato AI**: a long restaurant blog post covers history, menu and delivery policy; semantic chunks separate them so "what is the refund policy?" pulls only the policy part.

## 🟡 Real Example Hindi mein
**Tariff System**: लंबा "General Notes" section electronics की परिभाषा से textiles के नियमों और फिर origin rules पर जाता है। Semantic chunking इन topic बदलावों पर तोड़ती है ताकि हर chunk एक ही विषय का हो। Textile origin rules के सवाल पर मिला-जुला नहीं, साफ़ chunks मिलते हैं।

**Zomato AI**: restaurant का लंबा blog इतिहास, menu और delivery policy कवर करता है; semantic chunks उन्हें अलग करते हैं ताकि "refund policy क्या है?" पर सिर्फ़ policy वाला हिस्सा आए।

---

## 💻 Code Example — Basic
```python
# Runs offline: semantic chunking with a toy bag-of-words "embedding" (replace with a real model in production)
import math
import re
from collections import Counter


def embed(sentence: str) -> Counter:
    return Counter(re.findall(r"[a-z]+", sentence.lower()))  # word counts as a sparse vector


def cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[w] * b[w] for w in a)  # dot product over shared words
    na = math.sqrt(sum(v * v for v in a.values()))  # norm a
    nb = math.sqrt(sum(v * v for v in b.values()))  # norm b
    return dot / (na * nb) if na and nb else 0.0  # cosine similarity


def semantic_chunks(sentences: list[str], threshold: float = 0.15) -> list[list[str]]:
    """Start a new chunk when similarity to the previous sentence falls below `threshold`."""
    if not sentences:
        return []
    vecs = [embed(s) for s in sentences]  # one vector per sentence
    chunks = [[sentences[0]]]  # first chunk begins with the first sentence
    for i in range(1, len(sentences)):
        sim = cosine(vecs[i - 1], vecs[i])  # similarity with the previous sentence
        if sim < threshold:
            chunks.append([])  # topic change: open a new chunk
        chunks[-1].append(sentences[i])  # add the sentence to the current chunk
    return chunks


sents = [
    "Headphones and earphones are classified under 8518.30.",
    "Earphones with a microphone are classified under 8518.40.",
    "Cotton T-shirts are classified under 6109.10.",
    "Knitted cotton garments follow chapter 61.",
]
for i, ch in enumerate(semantic_chunks(sents, 0.5)):  # toy word-count vectors need a high threshold; real embeddings use percentiles:
    print(i, ch)
```

## 💻 Code Example — Advanced
```python
# Production: percentile breakpoints with real embeddings, size limits, async, error handling
import asyncio
import logging
import re
from typing import Awaitable, Callable

import numpy as np  # pip install numpy

log = logging.getLogger("semantic_chunker")
EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]  # async: texts -> vectors


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?।])\s+", text) if s.strip()]  # includes the Hindi danda


async def semantic_split(text: str, embed: EmbedFn, percentile: float = 90.0,
                         min_chars: int = 200, max_chars: int = 1500) -> list[str]:
    sents = split_sentences(text)
    if len(sents) < 3:
        return [text.strip()] if text.strip() else []  # too short to analyse
    try:
        vecs = np.array(await embed(sents), dtype=np.float32)  # (n, d) matrix
    except Exception:
        log.exception("embedding failed; falling back to one chunk per ~max_chars")
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9  # normalise rows
    dist = 1.0 - np.sum(vecs[:-1] * vecs[1:], axis=1)  # cosine distance between neighbours
    cut = float(np.percentile(dist, percentile))  # adaptive threshold for THIS document
    chunks: list[str] = []
    cur = sents[0]
    for i, s in enumerate(sents[1:]):
        too_big = len(cur) + len(s) > max_chars  # hard cap
        boundary = dist[i] > cut and len(cur) >= min_chars  # topic change, and chunk not tiny
        if too_big or boundary:
            chunks.append(cur)
            cur = s
        else:
            cur += " " + s
    chunks.append(cur)
    return chunks


async def _toy_embed(texts: list[str]) -> list[list[float]]:
    return [[len(t) % 7, len(t) % 5, 1.0] for t in texts]  # placeholder; use OpenAI embeddings in real code


if __name__ == "__main__":
    demo = "Headphones are 8518.30. Earphones too. " * 6 + "Cotton shirts are 6109.10. Knitwear is chapter 61. " * 6
    print(len(asyncio.run(semantic_split(demo, _toy_embed, 90, 50, 400))))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()
oa = AsyncOpenAI()


async def openai_embed(texts: list[str]) -> list[list[float]]:
    r = await oa.embeddings.create(model="text-embedding-3-small", input=texts)  # one batched call
    return [d.embedding for d in r.data]


class Doc(BaseModel):
    text: str
    percentile: float = 90.0


@app.post("/chunk/semantic")
async def chunk(doc: Doc) -> dict:
    chunks = await semantic_split(doc.text, openai_embed, doc.percentile)  # from Advanced example
    return {"count": len(chunks), "sizes": [len(c) for c in chunks]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-experimental langchain-openai
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

chunker = SemanticChunker(
    OpenAIEmbeddings(model="text-embedding-3-small"),
    breakpoint_threshold_type="percentile",   # or "standard_deviation", "interquartile", "gradient"
    breakpoint_threshold_amount=90,           # tune per corpus
)
docs = chunker.create_documents(["...long tariff notes..."])
# Output is the same Document type as other splitters, so the rest of the pipeline is unchanged.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No min/max limits
```python
# Wrong: threshold alone can create 1-sentence chunks or a 20,000-character chunk
# Right: enforce min_chars (merge tiny) and max_chars (force split)
```

❌ Mistake 2: Assuming it is always better and free
```python
# Wrong: replace recursive splitting everywhere
# Right: A/B test on labelled queries; semantic chunking costs embedding calls for EVERY sentence
```

---

## 🧠 Tricky Interview Question

**Q**: "Your semantic chunker works on English but produces random chunks for Hindi legal text. Why?"

**Answer**: Three likely causes: (1) the sentence splitter does not recognise Hindi punctuation (the danda "।"), so the 'sentences' are giant blocks; (2) the embedding model is weak for Hindi, so similarity does not reflect meaning; (3) legal text repeats boilerplate wording, so neighbouring sentences look similar and the distance curve is flat, making percentile thresholds noisy. Fixes: split on "।", use a multilingual embedding model, combine structure (clause numbers) with semantics, and evaluate on Hindi queries specifically.

---

## ⚫ Interview Questions + Answers

Q1: What is semantic chunking?
A1: Splitting where the meaning shifts, detected via embedding similarity between neighbouring sentences.

Q2: What is a breakpoint threshold?
A2: The distance value above which a boundary is placed, often a percentile such as the 90th-95th of all neighbour distances in the document.

Q3: Main drawback?
A3: Cost and latency: embeddings for every sentence at ingestion time, and variable chunk sizes that need min/max controls.

Q4: Why add min and max sizes?
A4: To avoid tiny fragments and huge chunks, keeping embeddings and prompts well-behaved.

Q5: How do you decide between semantic and recursive chunking?
A5: Build a labelled retrieval set, run both with tuned parameters, compare recall@k, answer accuracy and ingestion cost. Use semantic when documents jump between topics without clear structure; prefer recursive or structure-aware splitting when headings and paragraphs already mark topics, since it is cheaper and often equal.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long unstructured documents with several topics
- Retrieval precision matters more than ingestion cost

❌ Avoid when:
- Structured documents (use heading/paragraph splitting)
- Huge corpora with tight ingestion budgets
- Very short documents

---

## 📊 Visual Diagram
```
 sentences:  s1  s2  s3 | s4  s5 | s6  s7  s8
 distance:     .1  .1  .6  .1  .7  .1  .1
                       ▲       ▲   (above the 90th percentile => boundary)
 chunks:     [s1 s2 s3] [s4 s5] [s6 s7 s8]
```

---

## 💰 Cost Impact
- Extra embedding tokens at ingestion: every sentence is embedded once for boundary detection (about the same as embedding the whole text once), then chunks are embedded again for storage unless you reuse sentence vectors. Plan for roughly 2x the embedding tokens of a basic splitter. Embeddings are cheap relative to LLM calls, so the main cost is time.
- Better-focused chunks can reduce prompt size at query time (smaller k).
- Optimise: embed sentences in batches, cache by hash, reuse sentence vectors to compute chunk vectors (average), and run it only for documents that need it.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Breakpoint | Place where a chunk ends | Chunk ख़त्म होने की जगह |
| Percentile threshold | Cut value from distance distribution | Distance वितरण से तय सीमा |
| Cosine distance | 1 - cosine similarity | 1 - cosine similarity |
| Coherent chunk | Single-topic chunk | एक topic वाला chunk |
| Sentence window | Neighbouring sentences for context | पड़ोसी sentences की window |

---

## ⚡ 3-Line Summary
English: Semantic chunking embeds sentences and cuts where neighbouring similarity drops. It gives topic-coherent chunks at the price of extra embedding work. Always apply min/max sizes and compare against simpler splitters.
Hindi: Semantic chunking sentences को embed करके वहाँ काटती है जहाँ पड़ोसी similarity गिरती है। यह topic वाले chunks देती है पर embedding का extra काम लगता है। हमेशा min/max size लगाओ और सरल splitters से तुलना करो।

---

## ➡️ Next Topic
**160. Sentence Splitting** — the building block: reliable sentence boundaries, including Hindi.
