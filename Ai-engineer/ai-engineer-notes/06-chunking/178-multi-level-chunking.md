---

# 178. Multi-level Chunking
# हिंदी में: Multi-level Chunking (एक ही text को कई sizes में index करना)

---

## 🔵 Simple Definition (English)
Multi-level chunking indexes the same document at several chunk sizes at the same time, for example small (about 128 tokens), medium (about 512) and large (about 2000). At query time you search one or all levels and merge the results. Small chunks answer pinpoint questions, large chunks answer broad questions. It is a parallel-index idea, unlike a tree (hierarchical) where levels are linked.

## 🔵 सरल परिभाषा (Hindi)
Multi-level chunking में एक ही document को एक साथ कई chunk sizes पर index किया जाता है, जैसे छोटा (~128 tokens), मध्यम (~512) और बड़ा (~2000)। Query पर एक या सभी levels में खोजकर नतीजे merge करते हैं। छोटे chunks सटीक सवालों के लिए, बड़े chunks व्यापक सवालों के लिए। यह parallel-index का idea है, tree (hierarchical) की तरह levels आपस में linked नहीं होते।

---

## 🔴 Problem it Solves
- One chunk size cannot fit every question: "duty for 8517.13.00?" wants a tiny chunk; "explain the rules for telephones" wants a whole section.
- Users ask both kinds of questions in the same app.
- Tuning one size is always a compromise; multiple sizes avoid choosing.

## 🔴 यह क्यों बना? (Hindi)
- एक chunk size हर सवाल के लिए ठीक नहीं: "8517.13.00 की duty?" को छोटा chunk चाहिए; "telephones के rules समझाओ" को पूरा section।
- एक ही app में दोनों तरह के सवाल आते हैं।
- एक size tune करना हमेशा समझौता है; कई sizes से चुनने की ज़रूरत नहीं पड़ती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose 2-3 levels, e.g. S=128, M=512, L=2000 tokens (ratio about 4x)
Step 2 → Chunk the same document once per level (each with its own overlap)
Step 3 → Tag each chunk: level, doc_id, span (start, end) for later merging
Step 4 → Embed and store them (one collection with a "level" field, or one per level)
Step 5 → Query: embed once, search each level (top-k per level)
Step 6 → Optionally route: exact/narrow question -> S; "explain/summarise" -> L
Step 7 → Merge with Reciprocal Rank Fusion (RRF); drop results whose span is inside a better result
Step 8 → Send the best few chunks (mix of levels) to the LLM within the token budget
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 2-3 levels चुनो, जैसे S=128, M=512, L=2000 tokens
Step 2 → उसी document को हर level पर chunk करो
Step 3 → हर chunk पर tag: level, doc_id, span (start, end)
Step 4 → Embed करके store करो (एक collection में "level" field)
Step 5 → Query: एक बार embed, हर level में top-k खोजो
Step 6 → चाहो तो routing: narrow सवाल -> S; "explain/summarise" -> L
Step 7 → RRF से merge; जिसका span बेहतर result के अंदर है उसे हटाओ
Step 8 → Token budget में कुछ best chunks (मिश्रित levels) LLM को भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Levels: S = one tariff line (about 60 tokens), M = heading with all its lines (about 500), L = chapter notes plus heading (about 1500-2000). Question "duty on 8517.13.00" -> S hit. Question "what does Chapter 85 exclude?" -> L hit. Question "classify a foldable smartphone" -> S + M hits (line and heading context), with the chapter note from L added if the budget allows.

**Zomato style**: Dish line (S), menu category (M), whole restaurant page (L). "Is paneer tikka spicy?" -> S. "Describe this restaurant" -> L.

## 🟡 Real Example Hindi mein
**Tariff System**: Levels: S = एक tariff line (~60 tokens), M = पूरा heading अपनी lines सहित (~500), L = chapter notes + heading (~1500-2000)। "8517.13.00 की duty" -> S। "Chapter 85 क्या exclude करता है?" -> L। "Foldable smartphone classify करो" -> S + M, और budget हो तो L से chapter note।

**Zomato**: Dish line (S), menu category (M), पूरा restaurant page (L)। "पनीर टिक्का तीखा है?" -> S। "यह restaurant बताओ" -> L।

---

## 💻 Code Example — Basic
```python
# Basic multi-level chunking in pure Python: three sizes, simple routing by question type.
import re  # tokenizer

text = ("Smartphones heading 8517 attract ten percent duty. Cordless phones heading 8517 attract twelve percent duty. "
        "Exclusion for heading 8517: parts of phones are classified elsewhere. "
        "Batteries heading 8507 attract twenty percent duty. Lead acid batteries attract fifteen percent duty. "
        "Exclusion for heading 8507: spent batteries are waste.")  # sample document

def make_levels(t: str) -> dict[str, list[str]]:  # S = sentences, M = 3 sentences, L = whole text
    sents = [s.strip() + "." for s in t.split(".") if s.strip()]  # sentence list
    return {"S": sents,  # small: one sentence
            "M": [" ".join(sents[i:i + 3]) for i in range(0, len(sents), 3)],  # medium: 3 sentences
            "L": [t]}  # large: everything

LEVELS = make_levels(text)  # index all levels

def route(question: str) -> str:  # decide which level to search
    broad = any(w in question.lower() for w in ("explain", "summarise", "summarize", "all", "exclude"))  # broad cues
    return "L" if broad else "S"  # broad -> large, otherwise small

def search(question: str) -> tuple[str, str]:  # return (level, best chunk)
    level = route(question)  # pick level
    qw = set(re.findall(r"[a-z0-9]+", question.lower()))  # query words
    best = max(LEVELS[level], key=lambda c: len(qw & set(re.findall(r"[a-z0-9]+", c.lower()))))  # best chunk
    return level, best  # result

print(search("duty on lithium batteries"))  # S level
print(search("explain what heading 8507 excludes"))  # L level (whole text)
```

## 💻 Code Example — Advanced
```python
# Production-style multi-level index: parallel levels, one embedder call, RRF merge, span de-nesting.
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # cosine
from dataclasses import dataclass  # container
from typing import Awaitable, Callable  # types

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]  # async embedder


@dataclass
class LChunk:  # chunk with level and span
    level: str  # "S" / "M" / "L"
    doc_id: str  # document id
    start: int  # start word index
    end: int  # end word index (exclusive)
    text: str  # chunk text
    vec: list[float]  # embedding


def windows(words: list[str], size: int, overlap: int) -> list[tuple[int, int]]:  # word spans
    if not 0 <= overlap < size:  # validate
        raise ValueError("need 0 <= overlap < size")  # error
    return [(i, min(i + size, len(words))) for i in range(0, len(words), size - overlap)]  # spans


class MultiLevelIndex:  # the index
    def __init__(self, embed: Embedder, levels: dict[str, tuple[int, int]]) -> None:
        self.embed, self.levels = embed, levels  # embedder and {name: (size, overlap)}
        self.chunks: list[LChunk] = []  # all chunks, all levels

    async def add(self, doc_id: str, text: str) -> int:  # index a document at every level
        words = text.split()  # tokens ~ words
        meta = [(lvl, s, e) for lvl, (size, ov) in self.levels.items() for s, e in windows(words, size, ov)]  # spans
        texts = [" ".join(words[s:e]) for _, s, e in meta]  # chunk texts
        try:  # embedding call can fail
            vecs = await self.embed(texts)  # ONE batched call for all levels
        except Exception as exc:  # wrap
            raise RuntimeError("embedding failed") from exc  # message
        self.chunks += [LChunk(l, doc_id, s, e, t, v) for (l, s, e), t, v in zip(meta, texts, vecs)]  # store
        return len(meta)  # number of chunks

    @staticmethod
    def _cos(a: list[float], b: list[float]) -> float:  # cosine
        d = sum(x * y for x, y in zip(a, b))  # dot
        n = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0  # norms
        return d / n  # similarity

    async def search(self, q: str, k_per_level: int = 3, final_k: int = 3) -> list[LChunk]:
        qv = (await self.embed([q]))[0]  # embed query once
        rrf: dict[int, float] = {}  # chunk index -> fused score
        for lvl in self.levels:  # search each level separately
            idx = [i for i, c in enumerate(self.chunks) if c.level == lvl]  # chunks in this level
            top = sorted(idx, key=lambda i: -self._cos(qv, self.chunks[i].vec))[:k_per_level]  # level top-k
            for rank, i in enumerate(top, start=1):  # RRF: 1 / (60 + rank)
                rrf[i] = rrf.get(i, 0.0) + 1.0 / (60 + rank)  # accumulate
        ordered = sorted(rrf, key=lambda i: -rrf[i])  # fused ranking
        picked: list[LChunk] = []  # final list
        for i in ordered:  # drop chunks nested inside an already picked chunk
            c = self.chunks[i]  # candidate
            if any(p.doc_id == c.doc_id and p.start <= c.start and c.end <= p.end for p in picked):  # contained?
                continue  # skip redundant
            picked.append(c)  # keep
            if len(picked) == final_k:  # enough
                break  # stop
        return picked  # result


async def toy_embed(texts: list[str]) -> list[list[float]]:  # demo embedder
    await asyncio.sleep(0)  # async placeholder
    return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # letter counts


if __name__ == "__main__":  # demo
    async def main() -> None:  # async main
        idx = MultiLevelIndex(toy_embed, {"S": (6, 0), "M": (18, 3), "L": (60, 6)})  # three levels
        n = await idx.add("d1", "smartphones heading 8517 duty ten percent cordless phones heading 8517 duty twelve percent "
                                "exclusion parts of phones elsewhere batteries heading 8507 duty twenty percent")  # doc
        print("chunks:", n)  # total
        for c in await idx.search("duty batteries"):  # search
            print(c.level, c.start, c.end, c.text[:50])  # show
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
One endpoint accepts a `mode` (`auto`, `precise`, `broad`). `auto` searches all levels and fuses results; `precise`/`broad` restrict to small or large levels. The response reports which levels contributed so you can monitor usage.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app
index = MultiLevelIndex(toy_embed, {"S": (60, 0), "M": (250, 25), "L": (1000, 100)})  # levels in words


class Query(BaseModel):  # request
    question: str = Field(min_length=2)  # user question
    final_k: int = Field(default=3, ge=1, le=8)  # chunks to return


@app.post("/search")  # route
async def search(q: Query) -> dict:  # handler
    if not index.chunks:  # empty index
        raise HTTPException(503, "index is empty")  # not ready
    hits = await index.search(q.question, final_k=q.final_k)  # fused search
    return {"levels_used": sorted({h.level for h in hits}),  # monitoring
            "hits": [{"level": h.level, "doc": h.doc_id, "text": h.text[:200]} for h in hits]}  # payload
```

---

## 🔗 LangChain / LangGraph Connection
Implement each level as its own splitter and vector store collection (or one with `metadata["level"]`), then combine retrievers with `EnsembleRetriever` (which uses weighted reciprocal rank fusion). In LangGraph, add a `route` node that picks levels by question type.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitters

levels = {"S": (150, 0), "M": (600, 60), "L": (2000, 200)}  # token sizes and overlaps
splitters = {n: RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=s, chunk_overlap=o)
             for n, (s, o) in levels.items()}  # one splitter per level
# for n, sp in splitters.items():  # index each level with metadata
#     docs = sp.create_documents([text], metadatas=[{"level": n, "doc_id": "d1"}])
#     stores[n].add_documents(docs)
# from langchain.retrievers import EnsembleRetriever
# retriever = EnsembleRetriever(retrievers=[stores["S"].as_retriever(), stores["M"].as_retriever(),
#                                           stores["L"].as_retriever()], weights=[0.5, 0.3, 0.2])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending results from all levels to the LLM without removing overlaps
✅ Correct: Drop chunks whose span is already inside a selected chunk.

```python
# Wrong - the same sentence appears in S, M and L results
context = "\n".join(c.text for c in hits)  # triple repetition

# Right - span de-nesting + token budget
picked = [c for c in hits if not any(p.start <= c.start and c.end <= p.end for p in picked_so_far)]  # skip nested
```

❌ Mistake 2: Comparing raw similarity scores across levels (large chunks score differently).
✅ Correct: Fuse by rank (RRF) or normalise scores per level.

❌ Mistake 3: Indexing five levels "to be safe" - storage and cost explode.
✅ Correct: Use 2-3 levels with a 4x ratio, and prove each level helps on the eval set.

---

## 🧠 Tricky Interview Question
**Q**: "You added a large-chunk level and the answers for precise code questions got worse. Why?"

**Answer**: Large-chunk similarity scores are generally lower for narrow queries but the chunks cover many topics, and in a score-based merge they may crowd out small chunks, or RRF gives them equal weight to small chunks. The prompt fills with broad text, burying the precise line. Fix: route precise queries to the small level (or use weights), cap how many large chunks can enter the prompt, apply span de-nesting, and keep per-category metrics so you see the regression on "exact code" questions before shipping.

---

## ⚫ Interview Questions + Answers

Q1: What is multi-level chunking?
A1: Indexing the same text at multiple chunk sizes in parallel and merging results at query time.

Q2: How is it different from hierarchical chunking?
A2: Hierarchical builds a linked tree with parent/child relations and summaries and searches top-down. Multi-level keeps independent indexes per size and fuses results.

Q3: How do you merge results from several levels?
A3: Reciprocal Rank Fusion or weighted ensemble, then remove results nested inside better ones.

Q4: What is the storage cost?
A4: About one extra copy of the text per level (plus overlap). Three levels = about 3x vectors' text volume.

Q5: (Hard) How do you decide which level to search per query?
A5: Rule-based cues (exact codes, "explain"), a small classifier or LLM router, or search all levels and let fusion and reranking decide. Validate the router on an eval set with per-category metrics.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same corpus serves both pinpoint and broad questions
- You have budget for 2-3x index size
- You can measure per-category quality

❌ Avoid when:
- One size already meets quality goals
- Storage or embedding budget is tight
- You prefer a linked structure (use hierarchical or parent-child)

---

## 📊 Visual Diagram
```
 document ──┬─► chunk S (128 tok) ─► index S ─┐
            ├─► chunk M (512 tok) ─► index M ─┼─► per-level top-k ─► RRF merge ─► remove nested spans
            └─► chunk L (2000 tok)─► index L ─┘                                      │
                                                                                      ▼
 query ─► embed once ──────────────────────────────────────────────────►  best 2-4 chunks ─► LLM
 router: "duty on 8517.13.00" → S      "explain chapter 85 rules" → L
```

---

## 💰 Cost Impact
- Index: each level re-embeds the whole text. 3 levels = about 3x embedding tokens (plus overlap). For 50M tokens at $0.02 per 1M: about $3 total - small, but storage and vectors triple.
- Query: embedding the query once is cheap; the LLM prompt size is controlled by your final_k and token budget, not by the number of levels.
- Optimise: 2 levels first; share embeddings between levels when chunks coincide; route to a single level when confident; apply span de-nesting before building the prompt; use scalar/binary quantisation in the vector DB for the large level.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Level | One chunk-size layer | एक chunk-size परत |
| RRF | Reciprocal Rank Fusion | Rank आधारित merge |
| Span | Start-end position of chunk | Chunk की शुरुआत-अंत स्थिति |
| De-nesting | Remove chunks inside others | दूसरे के अंदर वाले chunks हटाना |
| Router | Chooses level per query | Query के लिए level चुनने वाला |
| Parallel index | Separate index per size | हर size का अलग index |

---

## ⚡ 3-Line Summary
English: Multi-level chunking indexes the same text at several sizes and fuses the results. Small levels answer precise questions; large levels answer broad ones. Remove nested duplicates and keep the number of levels small.
Hindi: Multi-level chunking एक ही text को कई sizes पर index करके नतीजे fuse करती है। छोटे levels सटीक सवालों के लिए, बड़े levels व्यापक सवालों के लिए। Nested duplicates हटाओ और levels कम रखो।

---

## ➡️ Next Topic
**179. Chunking + Metadata** - the filters and citations that make chunks searchable beyond similarity.
