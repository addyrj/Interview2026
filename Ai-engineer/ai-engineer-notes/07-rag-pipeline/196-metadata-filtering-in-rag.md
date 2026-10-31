---

# 196. Metadata Filtering in RAG
# हिंदी में: RAG में Metadata Filtering

---

## 🔵 Simple Definition (English)
Metadata filtering restricts vector search to chunks whose metadata matches conditions (country = IN, year >= 2024, tenant = acme). The filter narrows the candidate set so similarity search only ranks allowed chunks. It improves precision, speed and security.

## 🔵 सरल परिभाषा (Hindi)
Metadata filtering vector search को सिर्फ उन chunks तक सीमित करता है जिनका metadata शर्तों से मेल खाता है (country = IN, year >= 2024, tenant = acme)। Filter candidate set छोटा करता है ताकि similarity search सिर्फ allowed chunks को rank करे। इससे precision, speed और security बढ़ती है।

---

## 🔴 Problem it Solves
Semantic similarity ignores hard constraints: "duty for earphones in India 2025" may retrieve the US 2019 rule because it is textually similar. In multi-tenant apps, one customer's query must never see another's data, and similarity alone cannot guarantee that.

## 🔴 यह क्यों बना? (Hindi)
Semantic similarity कठोर शर्तें नहीं मानती: "India 2025 earphones duty" का जवाब US 2019 वाला rule भी हो सकता है क्योंकि text मिलता-जुलता है। Multi-tenant apps में एक customer को दूसरे का data कभी नहीं दिखना चाहिए, और सिर्फ similarity यह गारंटी नहीं दे सकती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At indexing: store metadata fields next to each vector (indexed fields for speed)
Step 2 → At query time: build a filter from (a) the user request, (b) auth context, (c) LLM self-query
Step 3 → Pre-filter: apply the filter INSIDE the vector search (DB supports it)
Step 4 → Rank only matching chunks by similarity (or hybrid score)
Step 5 → If results are too few, relax soft filters step by step (year -> any year)
Step 6 → Return results with the metadata used for citation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Indexing पर हर vector के साथ metadata fields रखो (speed के लिए indexed fields)
Step 2 → Query पर filter बनाओ: (a) user request, (b) auth context, (c) LLM self-query से
Step 3 → Pre-filter: filter को vector search के अंदर लगाओ (DB support करे)
Step 4 → सिर्फ matching chunks को similarity (या hybrid score) से rank करो
Step 5 → Results कम हों तो soft filters धीरे-धीरे ढीले करो (year -> any year)
Step 6 → Citation के लिए metadata के साथ results लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The user asks "earphones duty India 2025". Hard filters: `country=IN` (from the request) and `tenant_id` (from JWT, never from the client). Soft filter: `effective_year=2025`. If no result matches the year, relax to `effective_year<=2025` and sort by newest.
**Zomato AI**: "veg biryani under 300 in Indiranagar" becomes filters `veg=true`, `price<300`, `area="Indiranagar"` plus semantic query "biryani".

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "India 2025 earphones duty"। Hard filters: `country=IN` (request से) और `tenant_id` (JWT से, client से कभी नहीं)। Soft filter: `effective_year=2025`। साल से कोई result न मिले तो `effective_year<=2025` करके सबसे नया दिखाओ।
**Zomato AI**: "Indiranagar में 300 से कम veg biryani" -> filters `veg=true`, `price<300`, `area="Indiranagar"` + semantic query "biryani"।

---

## 💻 Code Example — Basic
```python
# Metadata filter with operators, applied BEFORE ranking (pure Python)
from typing import Any, Dict, List

Chunk = Dict[str, Any]
CHUNKS: List[Chunk] = [
    {"id": 1, "text": "earphones duty 0", "country": "IN", "year": 2025},
    {"id": 2, "text": "earphones duty 5", "country": "US", "year": 2019},
    {"id": 3, "text": "earphones duty 2", "country": "IN", "year": 2022},
]

OPS = {  # mongo-style operators
    "$eq": lambda a, b: a == b,
    "$gte": lambda a, b: a is not None and a >= b,
    "$lte": lambda a, b: a is not None and a <= b,
    "$in": lambda a, b: a in b,
}

def match(meta: Chunk, flt: Dict[str, Any]) -> bool:
    """All conditions must hold. Value can be a plain value or {operator: value}."""
    for key, cond in flt.items():
        value = meta.get(key)  # metadata value (None if missing)
        if isinstance(cond, dict):  # operator form
            if not all(OPS[op](value, arg) for op, arg in cond.items()):
                return False
        elif value != cond:  # equality shorthand
            return False
    return True

def search(query: str, flt: Dict[str, Any], k: int = 2) -> List[Chunk]:
    pool = [c for c in CHUNKS if match(c, flt)]  # PRE-filter
    q = set(query.lower().split())  # toy similarity: shared words
    pool.sort(key=lambda c: len(q & set(c["text"].split())), reverse=True)  # rank filtered pool
    return pool[:k]

if __name__ == "__main__":
    print(search("earphones duty", {"country": "IN", "year": {"$gte": 2024}}))  # only id 1
    print(search("earphones duty", {"country": {"$in": ["IN", "US"]}}))  # ids from both countries
```

## 💻 Code Example — Advanced
```python
# Async search with security filter + soft-filter relaxation + audit trail
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

logger = logging.getLogger("filtering")  # logger
Filter = dict[str, Any]
SearchFn = Callable[[str, Filter, int], Awaitable[list[dict]]]  # (query, filter, k) -> hits

@dataclass
class FilteredResult:
    hits: list[dict]  # results
    applied_filter: Filter  # final filter used
    relaxed: list[str] = field(default_factory=list)  # soft filters that were dropped

class FilteredSearcher:
    def __init__(self, search_fn: SearchFn, min_hits: int = 3) -> None:
        self.search_fn, self.min_hits = search_fn, min_hits  # deps

    async def search(self, query: str, tenant_id: str, hard: Filter, soft: list[tuple[str, Any]], k: int = 5) -> FilteredResult:
        security: Filter = {"tenant_id": tenant_id}  # ALWAYS from auth, never user input
        flt: Filter = {**hard, **security, **dict(soft)}  # combine all filters
        relaxed: list[str] = []  # audit
        remaining = list(soft)  # soft filters not yet dropped
        while True:
            try:
                hits = await self.search_fn(query, flt, k)  # pre-filtered search
            except Exception:
                logger.exception("filtered search failed"); return FilteredResult([], flt, relaxed)
            if len(hits) >= self.min_hits or not remaining:  # enough, or nothing left to relax
                return FilteredResult(hits, flt, relaxed)
            key, _ = remaining.pop()  # drop least important soft filter (last)
            flt.pop(key, None); relaxed.append(key)
            logger.info("relaxed filter %s", key)

async def demo_search(q: str, flt: Filter, k: int) -> list[dict]:
    data = [{"id": 1, "country": "IN", "year": 2022, "tenant_id": "t1"}, {"id": 2, "country": "IN", "year": 2025, "tenant_id": "t2"}]
    return [d for d in data if all(d.get(a) == b for a, b in flt.items())][:k]  # equality filter

if __name__ == "__main__":
    fs = FilteredSearcher(demo_search, min_hits=1)
    r = asyncio.run(fs.search("earphones", "t1", {"country": "IN"}, [("year", 2025)]))
    print(r)  # year relaxed; tenant t2 data never returned
```

---

## 🟠 FastAPI Integration
Derive security filters from the authenticated user (dependency), not from request JSON. Accept only whitelisted user filters.

```python
# FastAPI: tenant from auth dependency, user filters validated
from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()  # app

class UserFilters(BaseModel):
    country: Optional[str] = None  # allowed filter
    year: Optional[int] = None  # allowed filter

class Req(BaseModel):
    query: str
    filters: UserFilters = UserFilters()

def tenant(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    return "t1"  # decode JWT here and return the tenant claim

@app.post("/search")
async def search(req: Req, tenant_id: str = Depends(tenant)) -> dict:
    hard = {k: v for k, v in req.filters.model_dump().items() if v is not None}  # drop None
    res = await searcher.search(req.query, tenant_id, hard, soft=[])  # FilteredSearcher from Advanced example
    return {"applied_filter": res.applied_filter, "hits": res.hits}
```

---

## 🔗 LangChain / LangGraph Connection
`vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {...}})` (Chroma accepts Mongo-style `{"country": "IN", "year": {"$gte": 2024}}`; Pinecone/Qdrant/PGVector have their own syntax). `SelfQueryRetriever` builds the filter from natural language. In LangGraph, add a node that extracts filters from the question into state before the retrieve node.

```python
# Chroma retriever with metadata filter (needs langchain-chroma, langchain-openai, OPENAI_API_KEY)
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

docs = [Document(page_content="earphones duty 0", metadata={"country": "IN", "year": 2025}),
        Document(page_content="earphones duty 5", metadata={"country": "US", "year": 2019})]
# store = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))
# retriever = store.as_retriever(search_kwargs={"k": 3, "filter": {"$and": [{"country": "IN"}, {"year": {"$gte": 2024}}]}})
# print(retriever.invoke("earphones duty"))   # only the IN 2025 chunk
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Post-filtering after top-k.
✅ Correct: Pass the filter into the vector query.

```python
# Wrong: top-5 overall, then filter -> often 0 matches
hits = [h for h in store.similarity_search(q, k=5) if h.metadata["country"] == "IN"]
# Right
hits = store.similarity_search(q, k=5, filter={"country": "IN"})
```

❌ Mistake 2: Taking the tenant/user id from the request body.
✅ Correct: Derive it from the verified auth token.

```python
# Wrong
flt = {"tenant_id": request.tenant_id}     # attacker can change it
# Right
flt = {"tenant_id": current_user.tenant_id}   # from JWT
```

---

## 🧠 Tricky Interview Question
**Q**: "With an HNSW index, a very selective filter (matches 0.1 percent of data) returns fewer than k results or is very slow. Why?"

**Answer**: HNSW traverses a graph built over all vectors; with a very selective filter most visited nodes fail the filter, so the search either runs out of candidates (low recall, fewer than k results) or explores a lot (slow). Solutions: use a DB with filter-aware HNSW (Qdrant, Weaviate, pgvector with iterative scan), partition or shard by the filter key (a collection/namespace per tenant), build payload indexes on filtered fields, fall back to brute-force scan when the filtered set is small, or raise `ef_search`/candidate count.

---

## ⚫ Interview Questions + Answers

Q1: What is pre-filtering vs post-filtering?
A1: Pre-filtering applies conditions during search so all k results qualify; post-filtering filters the top-k afterward and may leave too few.

Q2: Name two reasons to use metadata filters.
A2: Precision (right country/year/version) and security (tenant or role isolation).

Q3: What is a soft filter?
A3: A preference that can be relaxed if results are too few (e.g., year), versus a hard filter (tenant) that must never be relaxed.

Q4: How can the filter be generated from a user question?
A4: Self-query: an LLM with the metadata schema converts the question into a structured filter; validate it against a whitelist before use.

Q5: How do you design multi-tenant RAG isolation?
A5: Always add tenant_id from auth to every query; prefer separate namespaces/collections per tenant for strong isolation; index the tenant field; test with cross-tenant leakage probes; never rely on the LLM or prompt for isolation; log filters for audit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data has versions, regions, tenants, categories
- Queries contain explicit constraints
- Security requires isolation

❌ Avoid when:
- Metadata is unreliable (use boosts)
- Corpus is small and uniform (extra complexity)

---

## 📊 Visual Diagram
```
 User question ─► (LLM self-query / rules) ─► user filters ─┐
 JWT token ─────────────────────────────────► tenant filter ─┼─► merged filter
                                                             ▼
        Vector DB:  [ metadata index ] ──► candidate set (matching only)
                                                             ▼
                                         similarity ranking ──► top-k
        too few? ──► relax soft filters (year) ──► retry
```

---

## 💰 Cost Impact
Filtering usually reduces cost: smaller candidate set means faster search and fewer irrelevant chunks sent to the LLM (each avoided 400-token chunk saves ~0.00006 USD on gpt-4o-mini input). A self-query LLM call adds ~300 tokens (about 0.00005 USD) per request. Payload indexes cost memory and write time.
Optimize: use rules for common filters and the LLM only when needed, cache parsed filters for repeated queries, index only fields you filter on.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pre-filter | Filter during search | Search के दौरान filter |
| Post-filter | Filter after search | Search के बाद filter |
| Hard filter | Must always apply | जो हमेशा लगना चाहिए |
| Soft filter | Can be relaxed | जिसे ढीला किया जा सकता है |
| Namespace | Isolated partition in a DB | DB में अलग हिस्सा |
| Self-query | LLM creates the filter | LLM से filter बनवाना |

---

## ⚡ 3-Line Summary
English: Metadata filters limit vector search to allowed chunks for precision and security.
Pre-filter inside the search, derive tenant filters from auth, and relax only soft filters.
Index filtered fields and watch recall under very selective filters.
Hindi: Metadata filters precision और security के लिए vector search को allowed chunks तक सीमित करते हैं।
Search के अंदर pre-filter करो, tenant filter auth से लो, और सिर्फ soft filters ढीले करो।
Filtered fields index करो और बहुत selective filters में recall पर नज़र रखो।

---

## ➡️ Next Topic
**197. BM25 — Keyword Search**: the classic sparse ranking function that finds exact terms like HS codes.
