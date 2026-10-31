---

# 172. Late Chunking
# हिंदी में: Late Chunking (पहले embed, बाद में chunk)

---

## 🔵 Simple Definition (English)
Normal chunking splits the text first and embeds each chunk alone ("early chunking"). Late chunking flips the order: pass the whole document through a long-context embedding model to get one vector per token, then cut the token vectors into chunks and average (mean-pool) each piece. Every chunk vector is computed with the whole document in view, so "It" or "the rate" keeps its meaning.

## 🔵 सरल परिभाषा (Hindi)
Normal chunking में पहले text काटते हैं, फिर हर chunk को अलग से embed करते हैं ("early chunking")। Late chunking में order उल्टा है: पूरा document long-context embedding model से गुज़ारो, हर token का vector लो, फिर token vectors को chunks में काटकर average (mean-pool) करो। हर chunk का vector पूरे document को देखकर बनता है, इसलिए "It" या "the rate" का मतलब बना रहता है।

---

## 🔴 Problem it Solves
- Early chunking: a chunk like "It attracts 10% duty." is embedded alone. The model does not know what "It" means, so the vector is weak and search misses it.
- Chunks lose document-level context: the title, the product name, the date.
- Fixes like overlap or LLM-written context work, but overlap is limited and LLM context (topic 173) costs money for every chunk.
- Late chunking gives context "for free" at embedding time, using the model's attention over the whole text.

## 🔴 यह क्यों बना? (Hindi)
- Early chunking: "It attracts 10% duty." अकेले embed होता है; model को "It" का पता नहीं, vector कमज़ोर, search में miss।
- Chunks document-level context (title, product name, date) खो देते हैं।
- Overlap सीमित है; LLM से context लिखवाना (topic 173) हर chunk पर पैसा लगाता है।
- Late chunking में model की attention पूरे text पर चलती है, context मुफ़्त मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a long-context embedding model (for example 8K tokens) that returns token-level vectors
Step 2 → Tokenise the WHOLE document (must fit the model's max length)
Step 3 → Run the transformer ONCE -> one contextual vector per token (attention saw everything)
Step 4 → Decide chunk boundaries (by sentences/paragraphs) and map them to token spans
Step 5 → For each span, mean-pool the token vectors -> one vector per chunk
Step 6 → (Model-specific) normalise the vectors
Step 7 → Store chunk text + its pooled vector in the vector DB
Step 8 → Query is embedded normally (one short text) and compared with chunk vectors
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Long-context embedding model चुनो (जैसे 8K tokens) जो token-level vectors दे
Step 2 → पूरा document tokenise करो (model की max length में fit होना चाहिए)
Step 3 → Transformer एक बार चलाओ -> हर token का contextual vector
Step 4 → Chunk boundaries तय करो और token spans में map करो
Step 5 → हर span के token vectors का mean-pool -> chunk vector
Step 6 → Vectors normalise करो
Step 7 → Chunk text + vector store करो
Step 8 → Query सामान्य तरह embed होता है और chunk vectors से compare होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs ruling reads: "Smartphones with 5G modem... [paragraph 1]. The goods are classified under 8517.13. They attract 10% duty. [paragraph 2]". Paragraph 2 never mentions "smartphone". With early chunking, a query "duty for 5G smartphone" misses paragraph 2. With late chunking the token vectors of "They" and "10%" were computed while attending to paragraph 1, so paragraph 2's vector still carries "smartphone 5G".

**Amazon style**: A product page whose spec table says "Battery: 5000 mAh" far below the title "Galaxy M34". The spec chunk's vector still knows it belongs to Galaxy M34.

## 🟡 Real Example Hindi mein
**Tariff System**: Ruling में लिखा है: "5G modem वाले smartphones... [para 1]। Goods 8517.13 में classified हैं। They 10% duty आकर्षित करते हैं। [para 2]"। Para 2 में "smartphone" शब्द नहीं है। Early chunking में "5G smartphone की duty" query para 2 को miss कर देती है। Late chunking में "They" और "10%" के vectors para 1 को देखकर बने, इसलिए para 2 के vector में "smartphone 5G" का अर्थ बना रहता है।

**Amazon**: Spec table "Battery: 5000 mAh" title "Galaxy M34" से बहुत नीचे है, फिर भी spec chunk का vector जानता है कि यह Galaxy M34 का है।

---

## 💻 Code Example — Basic
```python
# Basic late-chunking SIMULATION in pure Python (toy model, shows the idea, not a real encoder).
# Toy "contextual" token vector = own one-hot-ish vector + share of the document's vector.
VOCAB = ["smartphone", "5g", "duty", "ten", "it", "they"]  # tiny vocabulary

def one_hot(tok: str) -> list[float]:  # toy token vector
    return [1.0 if tok == v else 0.0 for v in VOCAB]  # 1 at its own position

def contextual_vectors(tokens: list[str], mix: float = 0.5) -> list[list[float]]:  # toy attention
    doc = [sum(col) / len(tokens) for col in zip(*[one_hot(t) for t in tokens])]  # document mean
    return [[(1 - mix) * a + mix * b for a, b in zip(one_hot(t), doc)] for t in tokens]  # mix in context

def mean_pool(vecs: list[list[float]]) -> list[float]:  # average vectors
    return [sum(c) / len(vecs) for c in zip(*vecs)]  # column means

tokens = ["smartphone", "5g", "it", "duty", "ten"]  # document tokens
chunk_a, chunk_b = (0, 2), (2, 5)  # chunk spans (token index ranges)

early = mean_pool([one_hot(t) for t in tokens[chunk_b[0]:chunk_b[1]]])  # embed chunk B alone
ctx = contextual_vectors(tokens)  # tokens embedded with whole doc in view
late = mean_pool(ctx[chunk_b[0]:chunk_b[1]])  # pool chunk B from contextual vectors

idx = VOCAB.index("smartphone")  # position of 'smartphone'
print("early chunk B 'smartphone' weight:", round(early[idx], 3))  # 0.0 - context lost
print("late  chunk B 'smartphone' weight:", round(late[idx], 3))  # > 0 - context kept
```

## 💻 Code Example — Advanced
```python
# Production-style late chunking with an injected token-embedding function.
# In production, token_embed wraps a long-context model (e.g. a Jina embeddings model via
# transformers) and returns (token_vectors, offsets). Here a deterministic stub keeps it runnable.
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # norms
import re  # sentence split
from dataclasses import dataclass  # container
from typing import Awaitable, Callable  # types

TokenEmbed = Callable[[str], Awaitable[tuple[list[list[float]], list[tuple[int, int]]]]]
# returns: (vector per token, (char_start, char_end) per token)


@dataclass
class LateChunk:  # output
    text: str  # chunk text
    vec: list[float]  # pooled contextual vector
    start: int  # char start
    end: int  # char end


def sentence_spans(text: str) -> list[tuple[int, int]]:  # chunk boundaries (char spans)
    spans, pos = [], 0  # results, cursor
    for m in re.finditer(r"[^.!?]+[.!?]?\s*", text):  # sentences
        spans.append((m.start(), m.end()))  # record span
        pos = m.end()  # move cursor
    return spans or [(0, len(text))]  # at least one chunk


def pool(vecs: list[list[float]]) -> list[float]:  # mean pool + L2 normalise
    mean = [sum(c) / len(vecs) for c in zip(*vecs)]  # average
    norm = math.sqrt(sum(x * x for x in mean)) or 1.0  # length
    return [x / norm for x in mean]  # unit vector


async def late_chunk(text: str, token_embed: TokenEmbed, max_tokens: int = 8192) -> list[LateChunk]:
    if not text.strip():  # validate
        raise ValueError("empty document")  # error
    try:  # model call can fail
        vecs, offsets = await token_embed(text)  # ONE pass over the whole document
    except Exception as exc:  # wrap
        raise RuntimeError("token embedding failed") from exc  # message
    if len(vecs) > max_tokens:  # too long for one pass
        raise ValueError("document exceeds model window; split into long windows first")  # caller must window
    chunks: list[LateChunk] = []  # output
    for s, e in sentence_spans(text):  # each chunk span
        idx = [i for i, (a, b) in enumerate(offsets) if a >= s and b <= e]  # tokens inside span
        if not idx:  # no tokens (whitespace only)
            continue  # skip
        chunks.append(LateChunk(text[s:e].strip(), pool([vecs[i] for i in idx]), s, e))  # pooled chunk
    return chunks  # result


async def stub_token_embed(text: str):  # deterministic stand-in for a real model
    await asyncio.sleep(0)  # async placeholder
    toks = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\w+", text)]  # word tokens
    vocab = sorted({t.lower() for t, _, _ in toks})  # vocabulary
    doc = [sum(1 for t, _, _ in toks if t.lower() == v) / len(toks) for v in vocab]  # doc context vector
    vecs = [[(0.5 if t.lower() == v else 0.0) + 0.5 * doc[i] for i, v in enumerate(vocab)]
            for t, _, _ in toks]  # token vec = own + context
    return vecs, [(s, e) for _, s, e in toks]  # vectors + offsets


if __name__ == "__main__":  # demo
    doc = "Smartphones with 5G are covered. They attract ten percent duty."  # text
    for c in asyncio.run(late_chunk(doc, stub_token_embed)):  # run
        print(repr(c.text), len(c.vec))  # chunk and vector length
```

---

## 🟠 FastAPI Integration
The ingestion endpoint accepts a full document, runs late chunking once, and returns chunks with vectors ready for the vector DB. Long documents are rejected with 413 (or windowed by the caller).

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app


class DocIn(BaseModel):  # request
    text: str = Field(min_length=1, max_length=60_000)  # bounded document


@app.post("/ingest/late")  # route
async def ingest_late(doc: DocIn) -> dict:  # handler
    try:  # guard
        chunks = await late_chunk(doc.text, stub_token_embed)  # use the real model in production
    except ValueError as exc:  # too long / empty
        raise HTTPException(413, str(exc))  # payload issue
    except RuntimeError as exc:  # model failure
        raise HTTPException(502, str(exc))  # upstream failure
    return {"chunks": [{"text": c.text, "dim": len(c.vec)} for c in chunks]}  # response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has no built-in "late chunking" splitter. You implement it inside a custom `Embeddings` class (or call a provider that supports it, for example Jina's API with a late-chunking option), then store pooled vectors in any vector store. In LangGraph, make `late_chunk` one node that replaces the `split` and `embed` nodes of a normal pipeline.

```python
from langchain_core.embeddings import Embeddings  # base interface


class LateChunkEmbeddings(Embeddings):  # custom embeddings wrapper
    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # called by vector stores
        raise NotImplementedError("call your late-chunking model/API here; pass whole docs, return per-chunk vectors")

    def embed_query(self, text: str) -> list[float]:  # queries are embedded normally (short text)
        raise NotImplementedError("embed the query with the same model")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying late chunking with a model that has a short window (512 tokens)
✅ Correct: Use a long-context embedding model (several thousand tokens). Otherwise there is little context to share.

```python
# Wrong - the document is truncated at 512 tokens, later chunks get no vectors/context
vecs, _ = await token_embed(very_long_text)  # silently truncated by some models

# Right - check the length, or window the document (e.g. 8K windows with some overlap)
if len(vecs) > max_tokens:  # explicit guard
    raise ValueError("window the document first")  # do not truncate silently
```

❌ Mistake 2: Pooling the [CLS]/pooled output instead of token vectors.
✅ Correct: Take the last hidden state per token and mean-pool the span.

❌ Mistake 3: Assuming it always beats early chunking.
✅ Correct: Evaluate on your data; gains are largest when chunks contain pronouns or references to earlier text.

---

## 🧠 Tricky Interview Question
**Q**: "Your 200-page tariff PDF is much longer than the embedding model's 8K window. A teammate says 'just use late chunking on the whole PDF'. What do you say?"

**Answer**: Late chunking needs the full text inside the model's window in one pass. For 200 pages, split into long windows (for example 6-8K tokens, aligned with sections, with some overlap) and apply late chunking within each window. Chunks still see up to 8K tokens of context but not the whole book. For wider context combine with hierarchical/contextual methods (add title and chapter heading to each window). Also note that attention cost grows with window length, so latency and GPU memory matter.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between early and late chunking?
A1: Early: split text, then embed each chunk independently. Late: embed the whole text to token vectors, then split the token vectors and pool per chunk.

Q2: What does late chunking improve?
A2: Chunks keep document-level context (pronouns, titles, topic), improving retrieval of ambiguous chunks.

Q3: What model requirement does it have?
A3: A long-context model that exposes token-level (last hidden state) embeddings, and a window large enough for the document.

Q4: Compared with contextual chunking (Anthropic), what is different?
A4: Contextual chunking pays for an LLM call per chunk to write a context sentence. Late chunking adds context inside the embedding model at no extra LLM cost, but needs a specific embedding model and works only in vector space (BM25 gets no benefit).

Q5: (Hard) What are the limits?
A5: Window size, more compute per document (long sequences), model dependence, less transparent (context is implicit in vectors, cannot be inspected), nothing for keyword search, and re-embedding needed if any part of the document changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chunks depend on earlier text (pronouns, "the above", tables under a title)
- Documents fit a long-context embedding window
- You want better vectors without extra LLM calls

❌ Avoid when:
- Documents are far longer than the window and cannot be windowed sensibly
- Chunks are already self-contained (FAQ)
- Your embedding provider only returns one vector per text

---

## 📊 Visual Diagram
```
 EARLY chunking                          LATE chunking
 ───────────────                         ─────────────
 doc ─► split ─► [c1] [c2] [c3]          doc ─────────────► transformer (whole doc)
              │    │    │                                          │
              ▼    ▼    ▼                              token vectors t1 t2 t3 ... tn
           embed embed embed                                   │ (context mixed in)
           (alone)(alone)(alone)               cut by spans:  [c1]  [c2]  [c3]
              │    │    │                                  mean-pool each span
              ▼    ▼    ▼                                       ▼     ▼     ▼
             v1   v2   v3                                      v1    v2    v3
 c2 = "It attracts 10%"  -> no idea          c2's vector knows "smartphone" from c1
```

---

## 💰 Cost Impact
- Embedding tokens: the document is embedded once, so total tokens are about the same as early chunking (no overlap needed, so possibly lower). No extra LLM calls.
- Compute: attention over an 8K window costs more than many 300-token passes; hosted embedding APIs bill by tokens, so the bill is similar, but self-hosted GPU time rises.
- Example: 50M tokens at $0.02 per 1M = about $1. Contextual chunking with an LLM would add input tokens for every chunk (document plus chunk), which is far more.
- Optimise: window long documents once, cache vectors by content hash, and re-embed only changed documents.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Late chunking | Embed first, chunk later | पहले embed, बाद में chunk |
| Token embedding | One vector per token | हर token का vector |
| Mean pooling | Average of vectors | Vectors का औसत |
| Contextual vector | Vector aware of surroundings | आसपास को समझने वाला vector |
| Context window | Max tokens per pass | एक बार में max tokens |
| Early chunking | Split then embed | पहले split, फिर embed |

---

## ⚡ 3-Line Summary
English: Late chunking embeds the entire document first and then pools token vectors into chunk vectors. Each chunk vector carries document-wide context at no extra LLM cost. It needs a long-context embedding model and documents that fit the window.
Hindi: Late chunking पहले पूरे document को embed करती है और फिर token vectors को pool करके chunk vectors बनाती है। हर chunk vector में document-wide context आता है, बिना extra LLM cost के। इसके लिए long-context embedding model चाहिए और document window में fit होना चाहिए।

---

## ➡️ Next Topic
**173. Contextual Chunking (Anthropic method)** - an LLM writes a short context sentence for each chunk before embedding.
