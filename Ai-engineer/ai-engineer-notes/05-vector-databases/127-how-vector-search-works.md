---

# 127. How Vector Search Works
# हिंदी में: Vector Search कैसे काम करता है

---

## 🔵 Simple Definition (English)
Vector search turns the query into a vector, measures its distance to stored vectors (cosine, dot product or L2) and returns the k closest. Closer in space means closer in meaning. It can scan everything (exact/brute force) or use an index to scan only a small part (approximate).

## 🔵 सरल परिभाषा (Hindi)
Vector search query को vector में बदलता है, stored vectors से उसकी दूरी (cosine, dot product या L2) नापता है और सबसे पास वाले k लौटाता है। Space में पास होना = meaning में पास होना। यह सब कुछ scan कर सकता है (exact/brute force) या index से सिर्फ़ थोड़ा हिस्सा scan करता है (approximate)।

---

## 🔴 Problem it Solves
Keyword search fails on "cheap phone" vs "affordable smartphone" because no words match. Vector search compares meaning, so synonyms, paraphrases and even other languages match. Understanding the mechanics (metrics, normalisation, filters, top-k) is required to debug "why did it return this?".

## 🔴 यह क्यों बना? (Hindi)
Keyword search "cheap phone" और "affordable smartphone" को match नहीं करता क्योंकि words अलग हैं। Vector search meaning compare करता है, इसलिए synonyms, paraphrases और दूसरी भाषाएँ भी match होती हैं। "यह result क्यों आया?" debug करने के लिए metrics, normalisation, filters और top-k समझना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Query text -> embedding model -> query vector q (same model as documents!)
Step 2 → Choose metric: cosine = dot(a,b)/(|a||b|), dot = a.b, L2 = sqrt(sum((a-b)^2))
Step 3 → (Optional) apply metadata filter: pre-filter, post-filter or filtered ANN
Step 4 → Compare q with candidate vectors (all of them, or those the index selects)
Step 5 → Keep the k best in a min-heap (priority queue)
Step 6 → Return ids, scores, metadata sorted best-first
Step 7 → (Optional) rerank the top 20-50 with a cross-encoder for better precision
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Query -> embedding model -> query vector q (documents वाला ही model!)
Step 2 → Metric चुनो: cosine, dot product या L2
Step 3 → (Optional) metadata filter: pre-filter, post-filter या filtered ANN
Step 4 → q को candidates से compare करो (सभी से, या index द्वारा चुने गए)
Step 5 → Min-heap में सबसे अच्छे k रखो
Step 6 → ids, scores, metadata best-first लौटाओ
Step 7 → (Optional) top 20-50 को cross-encoder से rerank करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "wireless earbuds". Cosine scores against headings: 8518.30 (headphones) 0.83, 8517.62 (communication apparatus) 0.78, 6307 (textile articles) 0.12. Filter `chapter in [85]` removes noise. A reranker then reads the top 20 and promotes 8518.30 to rank 1.

**Amazon-style**: a "red running shoes under 3000" query uses vector similarity for "running shoes" and a metadata filter `price < 3000, color = red`.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "wireless earbuds"। Cosine scores: 8518.30 (headphones) 0.83, 8517.62 0.78, 6307 (textile) 0.12। `chapter in [85]` filter noise हटाता है। Reranker top 20 पढ़कर 8518.30 को rank 1 देता है। **Amazon-style**: "red running shoes under 3000" में "running shoes" vector similarity से और `price < 3000, color = red` metadata filter से।

---

## 💻 Code Example — Basic
```python
# Basic: the three metrics and a top-k search, pure Python, runs offline
import heapq                                     # efficient top-k selection
import math                                      # sqrt
from typing import List, Tuple                   # type hints

Vec = List[float]                                # alias for readability

def dot(a: Vec, b: Vec) -> float:
    return sum(x * y for x, y in zip(a, b))      # multiply pairs and add

def l2(a: Vec, b: Vec) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))  # straight-line distance

def cosine(a: Vec, b: Vec) -> float:
    na, nb = math.sqrt(dot(a, a)), math.sqrt(dot(b, b))  # vector lengths
    return dot(a, b) / (na * nb) if na and nb else 0.0   # angle-based similarity

docs = {                                         # id -> toy 2-D embedding
    "earbuds": [0.9, 0.1],
    "headphones": [0.8, 0.3],
    "t-shirt": [0.1, 0.9],
}
q: Vec = [1.0, 0.0]                              # query "wireless earbuds"

def top_k(query: Vec, k: int, metric) -> List[Tuple[float, str]]:
    scored = ((metric(query, v), i) for i, v in docs.items())  # lazy scores
    return heapq.nlargest(k, scored)             # k highest similarities

print("cosine:", top_k(q, 2, cosine))            # earbuds first
print("dot   :", top_k(q, 2, dot))               # same order here
print("L2 (smaller is better):", sorted((l2(q, v), i) for i, v in docs.items())[:2])
```

## 💻 Code Example — Advanced
```python
# Advanced: search with pre-filtering, score threshold, batching and async wrapper
import asyncio                                          # async runtime
import heapq                                            # top-k heap
import logging                                          # logs
from dataclasses import dataclass                       # light record type
from typing import Any, Callable, Dict, List, Optional  # type hints

log = logging.getLogger("search")                       # logger

@dataclass(frozen=True)
class Item:
    id: str                                             # identifier
    vec: tuple                                          # unit-length vector (tuple = hashable)
    meta: Dict[str, Any]                                # metadata for filters

def dot(a: tuple, b: tuple) -> float:
    return sum(x * y for x, y in zip(a, b))             # cosine when vectors are unit length

class Searcher:
    def __init__(self, items: List[Item]) -> None:
        self.items = items                              # corpus (fits in RAM here)

    def search(
        self,
        q: tuple,                                       # query vector (unit length)
        k: int = 5,                                     # how many results
        pred: Optional[Callable[[Dict[str, Any]], bool]] = None,  # metadata predicate
        min_score: float = 0.0,                         # drop weak matches
    ) -> List[Dict[str, Any]]:
        if k <= 0:                                      # input validation
            raise ValueError("k must be positive")
        pool = (it for it in self.items if pred is None or pred(it.meta))  # PRE-filter
        scored = ((dot(q, it.vec), it) for it in pool)  # lazy scoring
        best = heapq.nlargest(k, scored, key=lambda t: t[0])  # O(N log k)
        out = [{"id": it.id, "score": round(s, 4), **it.meta} for s, it in best if s >= min_score]
        if not out:                                     # nothing relevant: say so, do not guess
            log.info("no results above threshold %.2f", min_score)
        return out

    async def search_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.search, *args, **kwargs)  # CPU work off the loop

# usage
corpus = [Item("8518.30", (0.97, 0.24), {"chapter": 85}), Item("6307", (0.1, 0.99), {"chapter": 63})]
s = Searcher(corpus)
print(s.search((1.0, 0.0), k=2, pred=lambda m: m["chapter"] == 85, min_score=0.5))
# Token usage: the vector search itself uses 0 LLM tokens; only the query embedding costs ~20 tokens.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException            # FastAPI
from pydantic import BaseModel, Field                  # pydantic v2

app = FastAPI()                                        # app
searcher = Searcher(corpus)                            # from the advanced example

class SearchIn(BaseModel):
    vector: list[float]                                # precomputed query vector
    k: int = Field(default=5, ge=1, le=50)             # bound k to protect the server
    chapter: int | None = None                         # optional metadata filter

@app.post("/vector-search")                            # route
async def vector_search(body: SearchIn) -> dict:
    pred = (lambda m: m["chapter"] == body.chapter) if body.chapter else None  # build filter
    try:
        hits = await searcher.search_async(tuple(body.vector), body.k, pred, 0.3)  # run search
    except ValueError as exc:                          # bad input
        raise HTTPException(422, str(exc))             # validation error
    return {"count": len(hits), "hits": hits}          # JSON response
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain exposes the same mechanics through similarity_search_with_score
from langchain_core.vectorstores import InMemoryVectorStore   # no server required
from langchain_openai import OpenAIEmbeddings                  # embeddings

vs = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))  # store
vs.add_texts(["Headphones 8518.30", "Cotton shirts 6205"])                  # index texts
pairs = vs.similarity_search_with_score("wireless earbuds", k=2)             # (Document, score)
for doc, score in pairs:                                                     # inspect scores
    print(round(score, 3), doc.page_content)                                 # higher = closer (cosine)
# MMR retrieval for diverse results: vs.as_retriever(search_type="mmr", search_kwargs={"k": 4})
# LangGraph: put this in a node and branch to "ask clarification" when top score < threshold.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating all metrics' scores the same (L2: smaller is better, cosine: larger is better)
✅ Correct: know your metric's direction.

```python
# Wrong: sort L2 distances descending -> returns the FARTHEST items
sorted(distances, reverse=True)[:5]
# Right: L2 ascending, cosine/dot descending
sorted(distances)[:5]
```

❌ Mistake 2: Post-filtering after top-k (can return zero results)
✅ Correct: filter inside the search (pre-filter) or over-fetch.

```python
# Wrong: take top 5, THEN filter country == "IN" -> maybe 0 left
hits = [h for h in index.search(q, 5) if h.meta["country"] == "IN"]
# Right: pass the filter to the DB so top-k is computed within the filtered set
hits = index.search(q, 5, where={"country": "IN"})
```

---

## 🧠 Tricky Interview Question

**Q**: "Cosine similarity and dot product give different rankings on your data. Why, and which should you use?"

**Answer**: Cosine ignores vector length; dot product includes it. If vectors are normalised to length 1 they are identical. If not, longer vectors win under dot product. Use the metric the embedding model was trained with (OpenAI embeddings are unit length so cosine = dot). Dot product is slightly faster, and some recommenders use magnitude on purpose (popularity). Mixing a cosine-trained model with an L2 index without normalising gives subtly wrong ranks.

---

## ⚫ Interview Questions + Answers

Q1: What is cosine similarity?
A1: The cosine of the angle between two vectors: dot(a,b)/(|a||b|). Range -1 to 1; closer to 1 means more similar direction/meaning.

Q2: What is top-k?
A2: The number of nearest results returned. Typical RAG uses k = 3 to 10; too small misses the answer, too large wastes tokens and distracts the LLM.

Q3: What is the difference between pre-filtering and post-filtering?
A3: Pre-filtering restricts candidates before ranking so you always get k valid results. Post-filtering ranks first and removes later, which can leave fewer than k or none. Modern DBs implement filtered ANN to keep both speed and correctness.

Q4: Why use a reranker after vector search?
A4: Bi-encoder vectors compress text independently, which is fast but approximate. A cross-encoder reads (query, passage) together and is more accurate but slow, so run it only on the top 20-50 candidates.

Q5: Search quality suddenly dropped after a model update. How do you debug?
A5: Check that query and document vectors come from the same model/version and dimension, that normalisation is the same, then compare Recall@k on a golden set between old and new. Inspect score distributions (a shift suggests mixed spaces), check the index metric config, and verify the filter logic. Roll back if documents were only partly re-embedded.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users phrase things differently from your documents
- Multilingual or fuzzy matching is needed
- You need "similar items" features

❌ Avoid (or combine with keyword/BM25) when:
- Exact identifiers, codes, names matter (HS code "8517.13")
- Explainability is required (scores are hard to justify)

---

## 📊 Visual Diagram
```
  query "wireless earbuds"
        │ embed
        ▼
   q = [0.12, -0.4, ...]
        │
        ├── filter chapter=85 ──► candidates
        │
        ▼
   score(q, v) for each candidate
     8518.30  cos=0.83  ◄── best
     8517.62  cos=0.78
     8504.40  cos=0.41
        │ top-k heap (k=2)
        ▼
   [8518.30, 8517.62] ──(optional)──► cross-encoder rerank ──► LLM
```

---

## 💰 Cost Impact
- Brute-force cost per query: N x d multiply-adds. 1M x 1536 = 1.5 billion, tens of ms on a good CPU but not free at scale.
- API token cost per query is only the embedding (about 20 tokens = $0.0000004 with text-embedding-3-small).
- The big cost lever is k: sending 10 chunks x 300 tokens = 3,000 input tokens (gpt-4o-mini: $0.00045) versus 4 chunks = 1,200 tokens ($0.00018). Use a score threshold and a reranker to send fewer, better chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cosine similarity | Angle-based similarity | Angle पर आधारित similarity |
| Dot product | Sum of element products | Elements के products का जोड़ |
| L2 distance | Straight-line distance | सीधी रेखा की दूरी |
| Top-k | k best matches | सबसे अच्छे k results |
| Pre-filter | Filter before ranking | Ranking से पहले filter |
| Reranker | Second-stage precise scorer | दूसरे चरण का सटीक scorer |
| Score threshold | Minimum acceptable similarity | न्यूनतम similarity |

---

## ⚡ 3-Line Summary
English: Vector search embeds the query, scores it against stored vectors with cosine, dot or L2, and returns the top-k. Pre-filter by metadata and rerank for precision. Always use the same model and a consistent metric.
Hindi: Vector search query को embed करके stored vectors से cosine, dot या L2 से score करता है और top-k लौटाता है। Metadata से pre-filter और precision के लिए rerank करो। हमेशा वही model और consistent metric use करो।

---

## ➡️ Next Topic
**128. ANN — Approximate Nearest Neighbor** — how indexes avoid scanning everything, and the recall vs speed trade-off.
