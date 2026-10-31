---

# 134. Pinecone Metadata Filtering
# हिंदी में: Pinecone Metadata Filtering (fields से search सीमित करना)

---

## 🔵 Simple Definition (English)
Metadata filtering lets you attach key-value data to each vector (country, chapter, date, tenant) and restrict a query to vectors whose metadata matches a condition. Pinecone applies the filter during the search, so you still get `top_k` results that satisfy the filter. Operators: `$eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $exists`, combined with `$and` / `$or`.

## 🔵 सरल परिभाषा (Hindi)
Metadata filtering में हर vector के साथ key-value data (country, chapter, date, tenant) जुड़ा होता है और query को उन्हीं vectors तक सीमित किया जा सकता है जिनका metadata शर्त से match करे। Pinecone filter को search के दौरान लगाता है, इसलिए आपको filter पर खरे उतरने वाले `top_k` results ही मिलते हैं। Operators: `$eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $exists`, और `$and` / `$or`।

---

## 🔴 Problem it Solves
Pure similarity ignores business rules. "Headphones" in the US tariff schedule is the wrong answer for an Indian importer. Fetching top 50 and filtering in Python is wasteful and can return zero results. Filtering inside the vector search gives correct, fast and secure (tenant-scoped) results.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ similarity business rules नहीं जानती। US tariff schedule का "Headphones" भारतीय importer के लिए गलत जवाब है। Top 50 लाकर Python में filter करना महँगा है और zero results भी दे सकता है। Vector search के अंदर filtering सही, तेज़ और सुरक्षित (tenant-scoped) results देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At upsert, attach flat metadata: {"country": "IN", "chapter": 85, "year": 2024, "tags": ["audio"]}
Step 2 → Build a filter dict: {"country": {"$eq": "IN"}, "chapter": {"$in": [84, 85]}}
Step 3 → Pass it to index.query(vector=q, top_k=5, filter=flt, include_metadata=True)
Step 4 → Pinecone restricts candidates to matching vectors, then ranks by similarity
Step 5 → You receive up to top_k matches ALL satisfying the filter
Step 6 → Combine rules with $and / $or for complex conditions
Step 7 → Index only the fields you filter on (serverless indexes all metadata by default; pod indexes can limit with metadata_config)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Upsert के समय flat metadata जोड़ो: {"country": "IN", "chapter": 85, "year": 2024}
Step 2 → Filter dict बनाओ: {"country": {"$eq": "IN"}, "chapter": {"$in": [84, 85]}}
Step 3 → index.query(vector=q, top_k=5, filter=flt, include_metadata=True) में दो
Step 4 → Pinecone candidates को matching vectors तक सीमित करके similarity से rank करता है
Step 5 → आपको top_k तक matches मिलते हैं, सभी filter को satisfy करते हुए
Step 6 → जटिल शर्तों के लिए $and / $or मिलाओ
Step 7 → सिर्फ़ उन्हीं fields को index करो जिन पर filter लगाते हो
```

---

## 🟡 Real World Example
**Tariff Classification System**: each heading carries `{country, chapter, effective_year, active}`. For an Indian importer classifying electronics in 2024, the filter is `{"$and": [{"country": {"$eq": "IN"}}, {"chapter": {"$in": [84, 85]}}, {"effective_year": {"$lte": 2024}}, {"active": {"$eq": True}}]}`. Expired codes and other countries never reach the LLM.

**Zomato AI**: `{"city": "Bengaluru", "veg": True, "price": {"$lt": 300}}` combined with "spicy paneer" similarity.

## 🟡 Real Example Hindi mein
**Tariff System**: हर heading के साथ `{country, chapter, effective_year, active}`। 2024 में electronics classify करने वाले भारतीय importer के लिए filter: `country == IN`, `chapter in [84, 85]`, `effective_year <= 2024`, `active == True`। Expired codes और दूसरे देशों के codes LLM तक पहुँचते ही नहीं। **Zomato**: `{"city": "Bengaluru", "veg": True, "price": {"$lt": 300}}` + "spicy paneer" similarity।

---

## 💻 Code Example — Basic
```python
# Basic: a pure-Python evaluator that mimics Pinecone filter semantics, so you can unit-test
# filters offline before sending them to Pinecone.
from typing import Any, Dict                              # type hints

def matches(meta: Dict[str, Any], flt: Dict[str, Any]) -> bool:
    """Return True if `meta` satisfies the Pinecone-style filter `flt`."""
    for key, cond in flt.items():                         # every top-level key must hold (implicit AND)
        if key == "$and":                                 # explicit AND of sub-filters
            if not all(matches(meta, sub) for sub in cond):
                return False
        elif key == "$or":                                # OR of sub-filters
            if not any(matches(meta, sub) for sub in cond):
                return False
        else:                                             # field condition
            if not isinstance(cond, dict):                # shorthand {"country": "IN"} means $eq
                cond = {"$eq": cond}
            val = meta.get(key)                           # missing field -> None
            for op, target in cond.items():               # evaluate each operator
                ok = {
                    "$eq": lambda: val == target,         # equal
                    "$ne": lambda: val != target,         # not equal
                    "$gt": lambda: val is not None and val > target,
                    "$gte": lambda: val is not None and val >= target,
                    "$lt": lambda: val is not None and val < target,
                    "$lte": lambda: val is not None and val <= target,
                    "$in": lambda: val in target,         # value in list
                    "$nin": lambda: val not in target,    # value not in list
                    "$exists": lambda: (key in meta) == bool(target),   # field present?
                }[op]()                                   # KeyError for unsupported operator
                if not ok:
                    return False
    return True                                           # all conditions passed

rows = [
    {"id": "8518.30", "country": "IN", "chapter": 85, "year": 2023},
    {"id": "8518.30-US", "country": "US", "chapter": 85, "year": 2024},
    {"id": "6205", "country": "IN", "chapter": 62, "year": 2024},
]
flt = {"$and": [{"country": {"$eq": "IN"}}, {"chapter": {"$in": [84, 85]}}, {"year": {"$lte": 2024}}]}
print([r["id"] for r in rows if matches(r, flt)])         # only "8518.30"
```

## 💻 Code Example — Advanced
```python
# Advanced: type-safe filter builder + tenant-scoped query + fallback when the filter is too strict.
import asyncio                                            # async runtime
import logging                                            # logs
from typing import Any, Dict, List, Optional              # type hints

from pydantic import BaseModel, Field                     # pydantic v2

log = logging.getLogger("pc-filter")                      # logger

class TariffFilter(BaseModel):
    country: str                                          # required: always scope by country
    chapters: Optional[List[int]] = None                  # optional chapter whitelist
    max_year: Optional[int] = Field(default=None, ge=1990, le=2100)   # effective year upper bound
    only_active: bool = True                              # skip expired codes

    def to_pinecone(self) -> Dict[str, Any]:
        clauses: List[Dict[str, Any]] = [{"country": {"$eq": self.country}}]   # base clause
        if self.chapters:
            clauses.append({"chapter": {"$in": self.chapters}})                # chapter list
        if self.max_year is not None:
            clauses.append({"effective_year": {"$lte": self.max_year}})        # date limit
        if self.only_active:
            clauses.append({"active": {"$eq": True}})                          # active only
        return {"$and": clauses} if len(clauses) > 1 else clauses[0]           # single clause needs no $and

async def filtered_query(io: Any, vec: List[float], f: TariffFilter, k: int = 5) -> List[Dict[str, Any]]:
    """Query with filter; if too few hits, relax the chapter filter and flag it."""
    hits = await io.query(vec, k=k, flt=f.to_pinecone(), min_score=0.4)        # io from note 133
    if len(hits) >= 2 or not f.chapters:                  # enough results, or nothing left to relax
        return hits
    log.info("filter too strict, relaxing chapters")      # observable fallback
    relaxed = f.model_copy(update={"chapters": None})     # drop the chapter whitelist
    hits = await io.query(vec, k=k, flt=relaxed.to_pinecone(), min_score=0.4)
    for h in hits:
        h["relaxed"] = True                               # tell downstream code (and the LLM) it is a weaker match
    return hits

# Token usage: filters add 0 tokens. Smaller candidate sets mean fewer irrelevant chunks in the prompt.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Header, HTTPException   # FastAPI
from openai import AsyncOpenAI                                # embeddings

app = FastAPI()                                               # app
oai = AsyncOpenAI()                                           # client

def tenant_country(x_country: str = Header(...)) -> str:      # derive scope from the authenticated context
    if x_country not in {"IN", "US", "EU"}:                   # whitelist, never trust raw input blindly
        raise HTTPException(400, "unsupported country")
    return x_country

@app.get("/classify/search")                                  # filtered search route
async def search(q: str, chapters: str | None = None, country: str = Depends(tenant_country)) -> dict:
    f = TariffFilter(country=country, chapters=[int(c) for c in chapters.split(",")] if chapters else None)
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    hits = await filtered_query(io, emb.data[0].embedding, f)  # `io` from the ingestion note
    return {"filter": f.to_pinecone(), "hits": hits}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings               # embeddings
from langchain_pinecone import PineconeVectorStore           # integration

vs = PineconeVectorStore(index_name="tariff-hs-te3s-v1", embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
retriever = vs.as_retriever(search_kwargs={                  # the filter passes straight to Pinecone
    "k": 5,
    "filter": {"country": {"$eq": "IN"}, "chapter": {"$in": [84, 85]}},
})
docs = retriever.invoke("wireless earbuds")                  # filtered similarity search
# LangGraph: put `country`/`chapters` in graph state and build the filter inside the retrieve node;
# a conditional edge can retry with a relaxed filter when no docs return.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Post-filtering in Python after top_k
✅ Correct: pass the filter to Pinecone.

```python
# Wrong: may return 0 results after filtering
hits = [m for m in index.query(vector=q, top_k=5).matches if m.metadata["country"] == "IN"]
# Right
hits = index.query(vector=q, top_k=5, filter={"country": {"$eq": "IN"}}, include_metadata=True).matches
```

❌ Mistake 2: Nested objects or unsupported types in metadata
✅ Correct: use flat values: string, number, boolean, or list of strings.

```python
# Wrong: nested dict is rejected
{"meta": {"country": {"code": "IN"}}}
# Right
{"country": "IN", "tags": ["audio", "wireless"]}
```

❌ Mistake 3: Filtering on tenant id taken from the request body
✅ Correct: derive the tenant from the authenticated token (or use namespaces) to prevent data leaks.

---

## 🧠 Tricky Interview Question

**Q**: "Your filtered query returns fewer than `top_k` results even though thousands of vectors match the filter. Why?"

**Answer**: Common causes: (1) a similarity score threshold in your own code drops matches; (2) the filter targets a field stored with a different type (e.g. `chapter` stored as string "85" but filtered as number 85); (3) you queried a different namespace than you wrote to; (4) metadata for some vectors lacks the field (use `$exists`); (5) eventual consistency after a recent upsert. Also, with very selective filters approximate search can return slightly fewer than k. Verify with `describe_index_stats()`, fetch a vector by id to inspect its real metadata, and test the filter on a known id.

---

## ⚫ Interview Questions + Answers

Q1: What types can Pinecone metadata hold?
A1: Strings, numbers, booleans and lists of strings. No nested objects. The metadata size limit is about 40 KB per vector.

Q2: How do you express "country is IN and chapter is 84 or 85"?
A2: `{"country": {"$eq": "IN"}, "chapter": {"$in": [84, 85]}}`; multiple keys at the top level are ANDed.

Q3: Is filtering applied before or after similarity ranking?
A3: Pinecone applies it as part of the search (pre-filtering/filtered ANN), so results satisfy the filter and you still get up to `top_k`.

Q4: Should you filter or use namespaces?
A4: Namespaces for hard isolation (tenant, environment) because queries only scan that namespace; metadata filters for soft attributes (chapter, date, active) within a namespace.

Q5: Design secure multi-tenant filtering and discuss what can go wrong.
A5: Use one namespace per tenant when tenants are many but isolated; the namespace comes from the server-side auth context, never from the client payload. Use metadata filters for attributes inside a tenant. Risks: forgetting the tenant filter in one code path (leak), trusting client-supplied filters (injection of `$or` clauses that bypass scope), schema drift (field types differ), and slow queries from over-selective filters on huge namespaces. Mitigate with a central query function that always injects the tenant scope, a pydantic filter model like `TariffFilter`, tests that assert cross-tenant queries return nothing, and audit logs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Business rules constrain results (country, date, permissions, category)
- Multi-attribute search combining meaning with structured fields

❌ Avoid when:
- A field has unique values per vector and you filter by it only (use `fetch` by id)
- Huge metadata blobs (keep them in a database, store only ids and short fields)

---

## 📊 Visual Diagram
```
 all vectors in namespace
   ┌────────────────────────────────────────────┐
   │ IN/85  IN/62  US/85  IN/85(expired) EU/84  │
   └────────────────────────────────────────────┘
        │ filter: country=IN AND chapter in [84,85] AND active
        ▼
   candidates:  IN/85  (others removed)
        │ rank by cosine to query
        ▼
   top_k matches (all satisfy the filter)  ──► LLM context
```

---

## 💰 Cost Impact
- Filters themselves add no tokens, but they cut irrelevant chunks: instead of sending 10 mixed chunks (3,000 tokens) you send 4 correct ones (1,200 tokens), saving ~60% of prompt tokens per query.
- Read units depend on the amount of data scanned; filtering and namespaces scope scans, which lowers read cost on large indexes.
- Metadata increases storage: keep only fields you filter on or display. A 2 KB metadata blob x 10M vectors = ~20 GB extra.
- Optimise: store ids and short fields; keep full text in a database or object store; pre-compute categorical fields (chapter number) rather than free text.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metadata | Key-value data on a vector | Vector के साथ key-value data |
| Filter | Condition restricting candidates | Candidates सीमित करने की शर्त |
| $eq / $in | Equals / in a list | बराबर / list में |
| $and / $or | Combine conditions | शर्तों को जोड़ना |
| Pre-filtering | Filter before ranking | Ranking से पहले filter |
| Tenant | Customer sharing the system | System share करने वाला customer |
| Selectivity | Fraction of data a filter keeps | Filter कितना data बचाता है |

---

## ⚡ 3-Line Summary
English: Attach flat metadata to vectors and pass a filter (`$eq`, `$in`, `$and`, ...) to the query so results obey business rules. Build filters with a typed model and always inject tenant scope on the server. Never post-filter after top_k.
Hindi: Vectors के साथ flat metadata जोड़ो और query में filter (`$eq`, `$in`, `$and`, ...) दो ताकि results business rules मानें। Filters typed model से बनाओ और tenant scope server पर inject करो। top_k के बाद post-filter कभी मत करो।

---

## ➡️ Next Topic
**135. Pinecone Namespaces** — hard partitions inside an index for tenants and environments.
