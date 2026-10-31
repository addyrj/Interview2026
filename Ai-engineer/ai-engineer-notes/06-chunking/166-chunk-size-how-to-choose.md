---

# 166. chunk_size — How to Choose
# हिंदी में: chunk_size — कैसे चुनें

---

## 🔵 Simple Definition (English)
`chunk_size` is the maximum length of one chunk, in characters or (better) tokens. Small chunks are precise but lose context. Big chunks keep context but are noisy and expensive. There is no universal best value - you pick a starting point (for example 300-500 tokens) and then measure.

## 🔵 सरल परिभाषा (Hindi)
`chunk_size` एक chunk की अधिकतम लंबाई है (characters या बेहतर: tokens में)। छोटे chunks precise होते हैं पर context खो देते हैं। बड़े chunks में context रहता है पर noise और cost बढ़ती है। कोई universal best value नहीं है - starting point (जैसे 300-500 tokens) चुनो और फिर measure करो।

---

## 🔴 Problem it Solves
- Too small (for example 100 tokens): the answer is split across chunks, and the retrieved chunk says "the rate is 10%" without saying for which product.
- Too big (for example 3000 tokens): the embedding becomes a blurry average of many topics, so search is less accurate. You also pay for irrelevant text in every prompt.
- Embedding models and LLMs have limits (an embedding model might accept only 512 or 8192 tokens), so chunks must also fit those.

## 🔴 यह क्यों बना? (Hindi)
- बहुत छोटा: जवाब कई chunks में बँट जाता है; chunk कहता है "rate 10% है" पर किस product का, पता नहीं।
- बहुत बड़ा: embedding कई topics का धुंधला average बन जाता है; prompt में बेकार text का भी पैसा लगता है।
- Embedding model की input limit होती है, chunk उसमें fit होना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Know the limits: embedding model max tokens, LLM context, top_k you will send
Step 2 → Look at your documents: how long is one "idea" (a paragraph? a tariff entry?)
Step 3 → Pick a starting size: about 1-3 paragraphs (300-500 tokens is a common start)
Step 4 → Build a small eval set: 30-100 real questions with the right source chunk known
Step 5 → Test several sizes (128, 256, 512, 1024) with the same overlap ratio (10-15%)
Step 6 → Measure recall@k, answer correctness, latency, tokens per query
Step 7 → Choose the knee of the curve (best quality before cost climbs)
Step 8 → Re-test whenever documents or the embedding model change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Limits जानो: embedding max tokens, LLM context, top_k
Step 2 → Documents देखो: एक "idea" कितना बड़ा है?
Step 3 → Starting size चुनो: 1-3 paragraphs (300-500 tokens)
Step 4 → छोटा eval set बनाओ: 30-100 असली questions
Step 5 → अलग sizes test करो (128, 256, 512, 1024), overlap 10-15%
Step 6 → recall@k, correctness, latency, tokens मापो
Step 7 → Curve का knee चुनो
Step 8 → Docs या model बदले तो दोबारा test करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A tariff entry is short: "8517.13 - Smartphones - 10%". Chunk size 1000 tokens packs 20 unrelated entries into one chunk, so a query about smartphones retrieves a chunk mostly about other items. Chunk size 150-250 tokens (one entry plus its heading path) retrieves exactly the right entry. But legal notes for a chapter are long and need 600-800 tokens to stay meaningful. So the size depends on the document type.

**Zomato style**: Restaurant reviews are 50-100 tokens each - use one review per chunk. Menu descriptions - one dish per chunk.

## 🟡 Real Example Hindi mein
**Tariff System**: Tariff entry छोटी होती है: "8517.13 - Smartphones - 10%"। 1000 tokens का chunk 20 अलग entries मिला देता है और search खराब होता है। 150-250 tokens (एक entry + heading path) सही रहता है। पर chapter की legal notes लंबी होती हैं, उन्हें 600-800 tokens चाहिए।

**Zomato**: Review छोटा होता है - एक review = एक chunk। Menu - एक dish = एक chunk।

---

## 💻 Code Example — Basic
```python
# Basic experiment: how chunk size changes retrieval on a tiny corpus (pure Python, no API)
import re  # tokenizer helper

corpus = (  # a small "tariff" document
    "Smartphones are classified under heading 8517 and attract ten percent duty. "
    "Microphones are classified under heading 8518 and attract seven percent duty. "
    "Batteries are classified under heading 8507 and attract twenty percent duty. "
    "Televisions are classified under heading 8528 and attract fifteen percent duty. "
)  # four facts

def words(text: str) -> list[str]:  # simple word tokenizer
    return re.findall(r"[a-z0-9]+", text.lower())  # lowercase words

def chunk_by_words(text: str, size: int) -> list[str]:  # fixed-size chunker
    w = text.split()  # split on whitespace
    return [" ".join(w[i:i + size]) for i in range(0, len(w), size)]  # slices

def score(query: str, chunk: str) -> float:  # overlap score
    q, c = set(words(query)), set(words(chunk))  # unique words
    return len(q & c) / (len(c) ** 0.5 or 1)  # overlap, penalise long chunks

def best_chunk(query: str, chunks: list[str]) -> str:  # retrieve top-1
    return max(chunks, key=lambda ch: score(query, ch))  # highest score

query = "duty on smartphones heading"  # user question
for size in (6, 12, 40):  # tiny, medium, huge
    chunks = chunk_by_words(corpus, size)  # build chunks
    top = best_chunk(query, chunks)  # retrieve
    print(f"size={size:>3} chunks={len(chunks):>2} top_len={len(top.split()):>2} -> {top[:70]}")
# Small chunk may miss 'duty'; huge chunk returns everything (noise); middle is the sweet spot.
```

## 💻 Code Example — Advanced
```python
# Production: sweep chunk sizes against an eval set, async, with errors handled.
# Embedding is injected as a function so you can plug OpenAI / local models; a fake one is used here.
from __future__ import annotations  # modern hints

import asyncio  # async runner
import math  # for cosine
from dataclasses import dataclass  # result record
from typing import Awaitable, Callable  # type aliases

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]  # async embed function type


@dataclass
class SweepResult:  # one row of the report
    size: int  # chunk size in words
    n_chunks: int  # how many chunks
    recall_at_k: float  # fraction of questions answered
    avg_words: float  # average chunk length (cost proxy)


def split(text: str, size: int, overlap_ratio: float = 0.1) -> list[str]:  # sliding chunker
    if size <= 0 or not 0 <= overlap_ratio < 1:  # validate
        raise ValueError("bad size/overlap")  # fail fast
    words = text.split()  # tokens ~ words here
    step = max(1, int(size * (1 - overlap_ratio)))  # window step
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]  # chunks


def cosine(a: list[float], b: list[float]) -> float:  # cosine similarity
    dot = sum(x * y for x, y in zip(a, b))  # dot product
    na = math.sqrt(sum(x * x for x in a)) or 1.0  # norm a
    nb = math.sqrt(sum(y * y for y in b)) or 1.0  # norm b
    return dot / (na * nb)  # similarity


async def sweep(text: str, evalset: list[tuple[str, str]], embed: Embedder,
                sizes: list[int], k: int = 2) -> list[SweepResult]:  # run the experiment
    results: list[SweepResult] = []  # report rows
    for size in sizes:  # each candidate size
        chunks = split(text, size)  # chunk the corpus
        try:  # embeddings can fail (network, quota)
            chunk_vecs = await embed(chunks)  # embed all chunks
            q_vecs = await embed([q for q, _ in evalset])  # embed questions
        except Exception as exc:  # surface which size failed
            raise RuntimeError(f"embedding failed for size={size}") from exc  # wrap
        hits = 0  # correct retrievals
        for (q, gold), qv in zip(evalset, q_vecs):  # each question
            ranked = sorted(range(len(chunks)), key=lambda i: -cosine(qv, chunk_vecs[i]))  # rank
            if any(gold.lower() in chunks[i].lower() for i in ranked[:k]):  # gold fact in top-k?
                hits += 1  # count hit
        results.append(SweepResult(size, len(chunks), hits / len(evalset),
                                   sum(len(c.split()) for c in chunks) / len(chunks)))  # row
    return results  # full report


async def fake_embed(texts: list[str]) -> list[list[float]]:  # bag-of-letters embedder for the demo
    await asyncio.sleep(0)  # pretend to be async I/O
    return [[t.lower().count(ch) for ch in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # vectors


if __name__ == "__main__":  # demo run
    doc = ("Smartphones heading 8517 duty ten percent. Microphones heading 8518 duty seven percent. "
           "Batteries heading 8507 duty twenty percent. Televisions heading 8528 duty fifteen percent.")  # text
    evals = [("duty for batteries", "8507"), ("heading of televisions", "8528")]  # (question, gold)
    for row in asyncio.run(sweep(doc, evals, fake_embed, [4, 8, 16])):  # run sweep
        print(row)  # print report row
```

---

## 🟠 FastAPI Integration
Make `chunk_size` a validated request parameter for an ingestion endpoint, with safe bounds and a default read from settings. This lets you A/B test sizes per collection without redeploying.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # validation (pydantic v2)

app = FastAPI()  # app


class ChunkRequest(BaseModel):  # request body
    text: str = Field(min_length=1)  # document text
    chunk_size: int = Field(default=400, ge=50, le=2000)  # bounded size
    overlap_ratio: float = Field(default=0.1, ge=0.0, lt=0.5)  # bounded overlap


@app.post("/chunk")  # route
async def chunk(req: ChunkRequest) -> dict:  # handler
    try:  # splitter raises ValueError on bad config
        chunks = split(req.text, req.chunk_size, req.overlap_ratio)  # reuse split()
    except ValueError as exc:  # invalid combination
        raise HTTPException(422, str(exc))  # report to client
    return {"n_chunks": len(chunks), "chunk_size": req.chunk_size, "preview": chunks[:2]}  # answer
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain, `chunk_size` is the first argument of every text splitter. Use `from_tiktoken_encoder` so the size counts tokens, not characters.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(  # measure in tokens
    encoding_name="cl100k_base",  # tokenizer (needs tiktoken)
    chunk_size=400,  # max tokens per chunk
    chunk_overlap=40,  # 10% overlap
)
chunks = splitter.split_text("long tariff text ...")  # list[str]
# LangGraph: put chunk_size in graph state/config so an eval node can sweep it automatically.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Measuring chunk_size in characters but thinking in tokens
✅ Correct: Count tokens (tiktoken) or convert: about 4 characters per token in English, fewer for Hindi.

```python
# Wrong - 1000 characters is only ~250 tokens; Hindi 1000 chars may be 600+ tokens
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)  # characters by default

# Right - explicit token budget
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=250)  # tokens
```

❌ Mistake 2: Copying "chunk_size=1000" from a blog without testing
✅ Correct: Build a small eval set and compare 3-4 sizes.

❌ Mistake 3: Exceeding the embedding model's input limit (silent truncation).
✅ Correct: Keep chunk_size comfortably below the model's max input tokens.

---

## 🧠 Tricky Interview Question
**Q**: "You doubled chunk_size from 256 to 512 tokens. Recall@5 went up, but answer quality went down and cost rose. How is that possible?"

**Answer**: Recall@5 measures whether the gold passage is somewhere in the top 5, and bigger chunks contain more text, so they "contain" the answer more often. But each chunk is now diluted: the LLM receives 5 x 512 tokens, with more irrelevant text, hitting "lost in the middle" and raising input tokens about 2x. Also embeddings of bigger chunks are less specific, so ranking gets worse. Evaluate end-to-end answer correctness and precision, not only recall; consider smaller chunks with parent expansion (small-to-big).

---

## ⚫ Interview Questions + Answers

Q1: What does chunk_size control?
A1: The maximum size of each chunk (characters or tokens). It balances retrieval precision against context completeness.

Q2: What is a sensible default?
A2: Around 300-500 tokens with 10-15% overlap for prose. It is only a starting point.

Q3: Why prefer token-based sizes?
A3: Models limit and bill by tokens, and tokens per character differ by language. Token-based sizes stay predictable.

Q4: How do you pick chunk_size for mixed documents?
A4: Do not use one size. Choose per document type (FAQ small, legal notes large) or use hierarchical/parent-child chunking.

Q5: (Hard) How would you pick chunk_size scientifically?
A5: Create a labelled eval set (question to gold chunk), sweep sizes with fixed overlap ratio and fixed top_k, measure recall@k, MRR, answer faithfulness, tokens per query and latency, and plot quality vs cost. Choose the knee; repeat when the embedding model or corpus changes; guard with a regression test in CI.

---

## 🔷 When to Use + When Not to Use
✅ Tune chunk_size carefully when:
- Retrieval quality is a product requirement (legal, tariff, medical)
- Corpus is large and token cost matters

❌ Do not over-tune when:
- Documents are already atomic (one FAQ per record)
- You are still prototyping - start with 400 tokens and move on

---

## 📊 Visual Diagram
```
 chunk size:   small ◄────────────────────────────► large
 precision:    HIGH                                  LOW (blurry embedding)
 context:      LOW  (answer split)                   HIGH
 cost/query:   LOW                                   HIGH (more input tokens)
 recall@k:     risky                                 inflated

 quality
   ▲        ____
   │      /      \___        <- sweet spot (the "knee")
   │    /            \___
   │  /                  \___
   └──┴────┴────┴────┴────┴──► chunk_size (128 256 512 1024 2048)
```

---

## 💰 Cost Impact
- Input tokens per query = top_k x chunk_size + prompt. Example: top_k=5 x 512 = 2560 tokens vs 5 x 256 = 1280 tokens. At $0.15 per 1M input tokens: 100K queries x 2560 = $38.40 vs $19.20.
- Embedding cost is roughly the same (same total text), but overlap adds 10-20% extra tokens.
- Optimise: smaller chunks plus parent expansion only for the top 1-2 hits; cache frequent queries; use rerankers to cut top_k.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| chunk_size | Max size of a chunk | Chunk की अधिकतम लंबाई |
| recall@k | Gold chunk found in top k | सही chunk top k में मिला |
| Precision | Share of relevant text retrieved | कितना retrieved text काम का |
| Eval set | Labelled questions | जाँच के लिए प्रश्न-उत्तर सेट |
| Knee | Best trade-off point | सबसे अच्छा संतुलन बिंदु |
| Token budget | Max tokens allowed | Tokens की सीमा |

---

## ⚡ 3-Line Summary
English: chunk_size trades precision (small) against context (large); start near 300-500 tokens. Measure in tokens and tune with an eval set, not with blog advice. Different document types need different sizes.
Hindi: chunk_size में precision (छोटा) और context (बड़ा) का trade-off है; 300-500 tokens से शुरू करो। Tokens में नापो और eval set से tune करो। अलग document types को अलग sizes चाहिए।

---

## ➡️ Next Topic
**167. chunk_overlap - How to Choose** - the second knob that stops answers from being cut at chunk borders.
