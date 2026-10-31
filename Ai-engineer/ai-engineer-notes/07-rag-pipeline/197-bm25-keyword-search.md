---

# 197. BM25 — Keyword Search
# हिंदी में: BM25 — Keyword Search

---

## 🔵 Simple Definition (English)
BM25 (Best Matching 25) is a ranking function for keyword search. It scores a document higher when it contains the query words often (term frequency), when those words are rare across the corpus (inverse document frequency), and it avoids favouring very long documents (length normalisation).

## 🔵 सरल परिभाषा (Hindi)
BM25 (Best Matching 25) keyword search के लिए ranking function है। Document का score तब ज़्यादा होता है जब उसमें query के शब्द बार-बार आते हैं (term frequency), वे शब्द पूरे corpus में दुर्लभ हैं (inverse document frequency), और बहुत लंबे documents को अनुचित फ़ायदा नहीं मिलता (length normalisation)।

---

## 🔴 Problem it Solves
Dense embeddings are fuzzy: "8518.30" and "8518.39" look almost identical to an embedding model, and rare names or part numbers may not be represented well. Plain word-count matching over-rewards long documents and common words like "the". BM25 gives exact-term matching with good statistical weighting, at tiny cost and with no model.

## 🔴 यह क्यों बना? (Hindi)
Dense embeddings fuzzy होते हैं: embedding model को "8518.30" और "8518.39" लगभग एक जैसे दिखते हैं, और दुर्लभ नाम या part numbers ठीक से represent नहीं होते। सादा word-count matching लंबे documents और "the" जैसे आम शब्दों को ज़्यादा इनाम देता है। BM25 exact-term matching अच्छी statistical weighting के साथ देता है, बहुत कम cost में और बिना किसी model के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Tokenize every document and the query (lowercase, split)
Step 2 → Build an inverted index: term -> {doc_id: term_frequency}
Step 3 → For each query term compute IDF = ln(1 + (N - n + 0.5) / (n + 0.5))
Step 4 → Per document and term: tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_len))
Step 5 → Score(doc) = sum over query terms of IDF * that value
Step 6 → Sort by score; return top-k
Defaults: k1 = 1.5 (term saturation), b = 0.75 (length normalisation)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर document और query को tokenize करो (lowercase, split)
Step 2 → Inverted index बनाओ: term -> {doc_id: term_frequency}
Step 3 → हर query term का IDF = ln(1 + (N - n + 0.5) / (n + 0.5))
Step 4 → हर document और term के लिए: tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_len))
Step 5 → Score(doc) = query terms पर IDF * ऊपर वाली value का जोड़
Step 6 → Score से sort करके top-k लौटाओ
Defaults: k1 = 1.5 (term saturation), b = 0.75 (length normalisation)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer searches "8518.30" or "Section XVI note 3". Dense search returns nearby codes; BM25 returns the exact chunk containing that token. BM25 also handles legal phrases and abbreviations ("CIF", "MFN") that embeddings blur.
**Amazon AI**: Searching by model number "WH-1000XM5" works best with keyword matching.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer "8518.30" या "Section XVI note 3" search करता है। Dense search आस-पास के codes देता है; BM25 उसी token वाला exact chunk देता है। BM25 कानूनी phrases और abbreviations ("CIF", "MFN") भी संभालता है जिन्हें embeddings धुंधला कर देते हैं।
**Amazon AI**: Model number "WH-1000XM5" से search keyword matching में सबसे अच्छा चलता है।

---

## 💻 Code Example — Basic
```python
# BM25 from scratch (standard library only): see exactly how the score works
import math
import re
from collections import Counter
from typing import Dict, List, Tuple

def tokenize(text: str) -> List[str]:
    """Lowercase; keep dots inside numbers so '8518.30' stays one token."""
    return re.findall(r"\d+\.\d+|\w+", text.lower())

class BM25:
    def __init__(self, docs: List[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b  # tuning parameters
        self.tokens = [tokenize(d) for d in docs]  # tokenised corpus
        self.tf = [Counter(t) for t in self.tokens]  # term frequency per doc
        self.n = len(docs)  # number of documents
        self.avg_len = sum(len(t) for t in self.tokens) / self.n  # average doc length
        self.df: Counter = Counter(term for t in self.tokens for term in set(t))  # doc frequency

    def idf(self, term: str) -> float:
        n_t = self.df.get(term, 0)  # docs containing term
        return math.log(1 + (self.n - n_t + 0.5) / (n_t + 0.5))  # always >= 0

    def score(self, query: List[str], i: int) -> float:
        dl = len(self.tokens[i])  # length of doc i
        s = 0.0  # running score
        for term in query:
            f = self.tf[i].get(term, 0)  # tf of term in doc
            if f == 0:
                continue  # term absent
            denom = f + self.k1 * (1 - self.b + self.b * dl / self.avg_len)  # length-normalised denominator
            s += self.idf(term) * f * (self.k1 + 1) / denom  # BM25 term score
        return s

    def search(self, query: str, k: int = 3) -> List[Tuple[int, float]]:
        q = tokenize(query)  # tokenise query
        scored = [(i, self.score(q, i)) for i in range(self.n)]  # score all docs
        return sorted([x for x in scored if x[1] > 0], key=lambda x: -x[1])[:k]  # best first

if __name__ == "__main__":
    corpus = ["HS 8518.30 earphones and headphones duty 0",
              "HS 8518.40 audio amplifiers duty 0",
              "HS 6403.99 leather footwear duty 20 percent"]
    bm = BM25(corpus)  # build index
    for i, s in bm.search("8518.30 earphones"):
        print(round(s, 3), corpus[i])  # doc 0 ranks first
```

## 💻 Code Example — Advanced
```python
# Production-style BM25 service: inverted index, incremental add/remove, async search, thread-safe, field boosts
import asyncio
import logging
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

logger = logging.getLogger("bm25")  # logger
TOKEN_RE = re.compile(r"\d+\.\d+|\w+")  # keeps HS codes whole

def tok(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

@dataclass
class Posting:
    doc_id: str  # id
    tf: int  # frequency

class BM25Index:
    """Inverted-index BM25 that supports add/delete without a full rebuild."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b  # params
        self.postings: dict[str, dict[str, int]] = defaultdict(dict)  # term -> {doc_id: tf}
        self.doc_len: dict[str, int] = {}  # doc_id -> length
        self.total_len = 0  # sum of lengths
        self._lock = asyncio.Lock()  # serialise writers

    async def add(self, doc_id: str, text: str) -> None:
        async with self._lock:
            if doc_id in self.doc_len:  # update = delete + add
                self._remove_unlocked(doc_id)
            terms = tok(text)
            for term, tf in Counter(terms).items():
                self.postings[term][doc_id] = tf  # add postings
            self.doc_len[doc_id] = len(terms); self.total_len += len(terms)

    def _remove_unlocked(self, doc_id: str) -> None:
        for term in list(self.postings):
            self.postings[term].pop(doc_id, None)  # remove postings
            if not self.postings[term]:
                del self.postings[term]
        self.total_len -= self.doc_len.pop(doc_id, 0)

    async def remove(self, doc_id: str) -> None:
        async with self._lock:
            self._remove_unlocked(doc_id)

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        n = len(self.doc_len)
        if n == 0:
            return []  # empty index
        avg = self.total_len / n  # average length
        scores: dict[str, float] = defaultdict(float)  # doc -> score
        for term in set(tok(query)):
            plist = self.postings.get(term)
            if not plist:
                continue  # unknown term
            idf = math.log(1 + (n - len(plist) + 0.5) / (len(plist) + 0.5))
            for doc_id, tf in plist.items():  # only docs containing the term
                denom = tf + self.k1 * (1 - self.b + self.b * self.doc_len[doc_id] / avg)
                scores[doc_id] += idf * tf * (self.k1 + 1) / denom
        return sorted(scores.items(), key=lambda x: -x[1])[:k]

    async def asearch(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        return await asyncio.to_thread(self.search, query, k)  # keep the event loop free

if __name__ == "__main__":
    async def main() -> None:
        idx = BM25Index()
        await idx.add("d1", "HS 8518.30 earphones duty 0")
        await idx.add("d2", "HS 6403.99 footwear duty 20")
        print(await idx.asearch("8518.30"))   # d1 only
        await idx.add("d1", "HS 8518.30 earphones duty 5 updated")  # update
        await idx.remove("d2")  # delete
        print(await idx.asearch("footwear"))  # []
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Keep the BM25 index in memory at startup (or use Elasticsearch/OpenSearch/Postgres full-text for big corpora). Expose `/keyword-search`. `asearch` runs in a thread so slow queries do not block other requests.

```python
# FastAPI keyword search endpoint
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()  # app
index = BM25Index()  # from the Advanced example (load documents at startup)

class Hit(BaseModel):
    doc_id: str
    score: float

@app.get("/keyword-search", response_model=list[Hit])
async def keyword_search(q: str = Query(min_length=1, max_length=200), k: int = Query(5, ge=1, le=50)) -> list[Hit]:
    results = await index.asearch(q, k)  # threaded search
    return [Hit(doc_id=d, score=round(s, 4)) for d, s in results]
```

---

## 🔗 LangChain / LangGraph Connection
`BM25Retriever` in `langchain_community.retrievers` (uses the `rank_bm25` package). It returns `Document`s and plugs into `EnsembleRetriever` for hybrid search. In LangGraph, make it a retrieval node next to a dense node.

```python
# LangChain BM25Retriever (pip install langchain-community rank_bm25)
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

docs = [Document(page_content="HS 8518.30 earphones duty 0"),
        Document(page_content="HS 6403.99 leather footwear duty 20")]
retriever = BM25Retriever.from_documents(docs, k=1)  # builds BM25 index over page_content
print(retriever.invoke("earphones")[0].page_content)  # HS 8518.30 earphones duty 0
```
Note: default tokenisation is whitespace split and lowercase-agnostic; pass `preprocess_func` for custom tokenisation (e.g., keep dots in codes, stemming).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Tokenizing with a regex that splits "8518.30" into "8518" and "30".
✅ Correct: Use a tokenizer that preserves codes, or index the code as an exact-match field too.

```python
# Wrong
re.findall(r"\w+", "HS 8518.30")       # ['hs', '8518', '30'] -> '30' matches thousands of docs
# Right
re.findall(r"\d+\.\d+|\w+", "HS 8518.30")   # ['hs', '8518.30']
```

❌ Mistake 2: Rebuilding the whole BM25 index on each document update.
✅ Correct: Use an engine with incremental updates (Elasticsearch/OpenSearch/Tantivy/Postgres FTS) or an inverted index with add/remove.

```python
# Wrong
retriever = BM25Retriever.from_documents(all_docs)   # on every change
# Right
await index.add(doc_id, new_text)
```

---

## 🧠 Tricky Interview Question
**Q**: "The user searches 'import duty on mobile phones' but the tariff text only says 'smartphones' and 'cellular telephones'. BM25 returns nothing useful. Why, and how do you fix it?"

**Answer**: BM25 matches only exact tokens: this is the **vocabulary mismatch** problem. No shared words (except maybe "duty"), so scores are low. Fixes: combine with dense retrieval (hybrid), expand the query with synonyms or LLM-generated terms (query expansion), apply stemming/lemmatisation, or index synonyms. Hybrid search with RRF is the standard answer.

---

## ⚫ Interview Questions + Answers

Q1: What do TF and IDF mean in BM25?
A1: TF is how often a term appears in a document; IDF measures how rare the term is across the corpus (rare terms matter more).

Q2: What do k1 and b control?
A2: k1 controls how quickly repeated terms saturate (higher = more weight to repeats). b controls length normalisation (0 = none, 1 = full).

Q3: Why is BM25 better than raw TF-IDF?
A3: It saturates term frequency (the tenth occurrence adds little) and normalises by document length, giving more robust rankings.

Q4: When does BM25 beat dense retrieval?
A4: For exact identifiers, rare names, codes, legal citations, and when you have no embedding model or labeled data.

Q5: How do you scale BM25 to 100M documents?
A5: Use a search engine (Elasticsearch/OpenSearch/Vespa/Tantivy) with sharding and inverted indexes on disk; use block-max WAND for faster top-k; keep stemming/analyzers consistent between index and query; tune k1/b on a labeled set; combine with dense retrieval through RRF. In-memory Python BM25 is fine up to roughly a few hundred thousand chunks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Queries include codes, names, IDs, exact phrases
- You need a fast, cheap baseline or hybrid component
- Explainable ranking matters

❌ Avoid alone when:
- Queries are paraphrased or multilingual (vocabulary mismatch)
- Users ask conceptual questions without the document's words

---

## 📊 Visual Diagram
```
 Query: "8518.30 earphones"
        │ tokenize
        ▼
 Inverted index
   8518.30   → {d1: 1}
   earphones → {d1: 1, d7: 2}
        │ for each doc: IDF × tf-saturation × length-norm
        ▼
 scores: d1 = 7.9, d7 = 3.1
        ▼
 ranked list [d1, d7]
```

---

## 💰 Cost Impact
BM25 uses no LLM or embedding tokens: cost is CPU and RAM only (roughly a few hundred bytes per chunk for postings). It is often the cheapest way to boost recall: adding BM25 to dense retrieval costs near 0 USD per query but can improve recall by 5-15 percent on code-heavy queries, letting you send fewer chunks to the LLM.
Optimize: precompute the index offline, keep it in memory or on a search engine, cache frequent queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BM25 | Keyword ranking function | Keyword ranking function |
| TF | Term frequency | शब्द की बारंबारता |
| IDF | Inverse document frequency (rarity) | शब्द की दुर्लभता |
| Inverted index | term -> documents map | शब्द से documents का map |
| k1 / b | Saturation / length parameters | Saturation / length parameters |
| Vocabulary mismatch | Query and doc use different words | Query और doc के शब्द अलग |

---

## ⚡ 3-Line Summary
English: BM25 ranks documents by rare matching query terms with saturation and length normalisation.
It is cheap, exact and great for codes, but blind to synonyms.
Combine it with dense retrieval for the best recall.
Hindi: BM25 documents को query के दुर्लभ matching शब्दों, saturation और length normalisation से rank करता है।
यह सस्ता, exact और codes के लिए बढ़िया है, पर synonyms नहीं समझता।
सबसे अच्छे recall के लिए इसे dense retrieval के साथ मिलाओ।

---

## ➡️ Next Topic
**198. Dense Retrieval**: embedding-based semantic search that understands meaning, the complement of BM25.
