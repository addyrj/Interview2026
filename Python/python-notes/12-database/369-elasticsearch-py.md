---

# 369. Elasticsearch-py
# हिंदी में: Elasticsearch-py (Python से Elasticsearch Search Engine)

---

## 🔵 Simple Definition (English)
`elasticsearch-py` is the official Python client for Elasticsearch, a search engine built on Lucene. You store JSON documents in an index and search them with a JSON query language (Query DSL). It gives fast full-text search, filters and aggregations on millions of documents.

## 🔵 सरल परिभाषा (Hindi)
`elasticsearch-py` Elasticsearch का official Python client है। Elasticsearch Lucene पर बना search engine है। आप JSON documents को index में रखते हैं और JSON query language (Query DSL) से search करते हैं। लाखों documents पर तेज full-text search, filters और aggregations मिलते हैं।

---

## 🔴 Problem it Solves
A normal database query like `WHERE name LIKE '%paneer%'` cannot use an index, so it scans every row and gives no relevance ranking. It also cannot handle typos ("panner"), synonyms, or "best match first". Elasticsearch builds an inverted index (word -> list of documents), so it finds matches in milliseconds, ranks them by relevance (BM25), and supports fuzzy search, autocomplete and analytics.

## 🔴 यह क्यों बना? (Hindi)
सामान्य database query `WHERE name LIKE '%paneer%'` index इस्तेमाल नहीं कर पाती, इसलिए हर row scan करती है और relevance ranking भी नहीं देती। यह typo ("panner"), synonyms, या "सबसे अच्छा match पहले" भी नहीं संभाल सकती। Elasticsearch inverted index (शब्द -> documents की list) बनाता है, इसलिए milliseconds में match ढूंढता है, BM25 से relevance के अनुसार rank करता है, और fuzzy search, autocomplete और analytics सपोर्ट करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a client: Elasticsearch("http://host:9200") (lazy, no network yet)
Step 2 → Create an index (like a table) with a mapping (field types)
Step 3 → Index documents: es.index(index=..., id=..., document={...})
Step 4 → Elasticsearch analyzes text: lowercase, split into tokens, store inverted index
Step 5 → Data becomes searchable after a "refresh" (default about 1 second)
Step 6 → Search with Query DSL: es.search(index=..., query={...})
Step 7 → Response: hits.hits[] with _id, _score, _source
Step 8 → For big loads use helpers.bulk(); for big reads use helpers.scan()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client बनाओ: Elasticsearch("http://host:9200") (lazy है, अभी network call नहीं)
Step 2 → Index बनाओ (table जैसा) mapping के साथ (field types)
Step 3 → Documents index करो: es.index(index=..., id=..., document={...})
Step 4 → Elasticsearch text analyze करता है: lowercase, tokens में तोड़ना, inverted index बनाना
Step 5 → Data "refresh" के बाद searchable होता है (default लगभग 1 सेकंड)
Step 6 → Query DSL से search करो: es.search(index=..., query={...})
Step 7 → Response: hits.hits[] जिसमें _id, _score, _source होते हैं
Step 8 → बड़े load के लिए helpers.bulk(); बड़े read के लिए helpers.scan()
```

---

## 🟡 Real World Example
Zomato/Swiggy restaurant and dish search: the user types "panner tika" and still sees "Paneer Tikka" first, filtered by city and price. Flipkart product search, log search in an ELK stack (Elasticsearch + Logstash + Kibana), and a RAG app that stores text chunks with vectors for semantic search all use Elasticsearch.

## 🟡 Real Example Hindi mein
Zomato/Swiggy में restaurant और dish search: user "panner tika" लिखता है और फिर भी "Paneer Tikka" सबसे ऊपर दिखता है, city और price से filter होकर। Flipkart product search, ELK stack (Elasticsearch + Logstash + Kibana) में log search, और RAG app जो text chunks को vectors के साथ semantic search के लिए रखता है, सब Elasticsearch इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Elasticsearch-py: build a client and a search body (needs a server to actually send)
from elasticsearch import Elasticsearch                      # official client (pip install elasticsearch)
from typing import Any                                       # type hint helper

es: Elasticsearch = Elasticsearch("http://localhost:9200")   # lazy: no network call yet
print(type(es).__name__)                                     # client class name

doc: dict[str, Any] = {"name": "Paneer Tikka", "city": "Pune", "price": 249}   # one document
query: dict[str, Any] = {                                    # Query DSL is plain dict/JSON
    "bool": {                                                # combine conditions
        "must": [{"match": {"name": "paneer"}}],             # full-text, scored
        "filter": [{"range": {"price": {"lte": 300}}}],      # exact filter, cached, no score
    }
}
print(list(query["bool"].keys()))                            # shape of the query

# With a live server you would run:
# es.indices.create(index="dishes")                          # create index
# es.index(index="dishes", id="1", document=doc)             # store the document
# es.indices.refresh(index="dishes")                         # make it searchable now
# resp = es.search(index="dishes", query=query, size=5)      # search
# for hit in resp["hits"]["hits"]: print(hit["_id"], hit["_score"], hit["_source"])

# Output:
# Elasticsearch
# ['must', 'filter']
```
Verified: the lines above were run with elasticsearch 9.5.1 (client creation and query building). The commented server calls were NOT run: no Elasticsearch server is available here.

## 💻 Code Example — Advanced
```python
# Production style: repository with injected client, error handling, bulk helper; tested with a fake client
from __future__ import annotations                           # forward references in hints
from dataclasses import dataclass                            # simple result object
from typing import Any, Iterable, Protocol                   # typing tools
from elasticsearch import Elasticsearch, NotFoundError, ApiError   # real exception classes
from elasticsearch.helpers import bulk                       # fast bulk indexing helper


class SearchClient(Protocol):                                # what our repo needs from a client
    def search(self, **kwargs: Any) -> dict[str, Any]: ...   # only the search method


@dataclass
class DishHit:                                               # clean result for the API layer
    id: str                                                  # document id
    score: float                                             # relevance score
    name: str                                                # dish name


class DishSearch:
    def __init__(self, client: SearchClient, index: str = "dishes") -> None:
        self.client = client                                 # dependency injection
        self.index = index                                   # index name

    def find(self, text: str, max_price: int, size: int = 10) -> list[DishHit]:
        body: dict[str, Any] = {                             # build the Query DSL
            "bool": {
                "must": [{"match": {"name": text}}],         # scored text match
                "filter": [{"range": {"price": {"lte": max_price}}}],   # cheap filter
            }
        }
        try:
            resp = self.client.search(index=self.index, query=body, size=size)   # call ES
        except NotFoundError:                                # index missing -> empty result
            return []
        except ApiError as exc:                              # other HTTP errors from ES
            raise RuntimeError(f"search failed: {exc.status_code}") from exc
        return [DishHit(h["_id"], h["_score"], h["_source"]["name"])   # map hits to objects
                for h in resp["hits"]["hits"]]


def bulk_actions(index: str, rows: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for i, row in enumerate(rows):                           # one action per row
        yield {"_index": index, "_id": str(i), "_source": row}   # format bulk() expects
# bulk(es, bulk_actions("dishes", rows))                     # real call: returns (ok_count, errors)


class FakeClient:                                            # test double, no server needed
    def search(self, **kwargs: Any) -> dict[str, Any]:
        assert kwargs["index"] == "dishes"                   # check what repo sent
        assert kwargs["query"]["bool"]["filter"][0]["range"]["price"]["lte"] == 300
        return {"hits": {"hits": [{"_id": "1", "_score": 1.5, "_source": {"name": "Paneer Tikka"}}]}}


repo = DishSearch(FakeClient())                              # inject fake
print(repo.find("paneer", 300))                              # run through the same code path
print(list(bulk_actions("dishes", [{"name": "Dosa"}])))      # preview bulk actions
print(callable(bulk))                                        # helper imported fine

# Output:
# [DishHit(id='1', score=1.5, name='Paneer Tikka')]
# [{'_index': 'dishes', '_id': '0', '_source': {'name': 'Dosa'}}]
# True
```
Verified: run with a fake client (real imports from elasticsearch 9.5.1). Real server calls (`bulk`, real `search`) were NOT run.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Package | `pip install elasticsearch` | `npm i @elastic/elasticsearch` |
| Client | `Elasticsearch("http://...")` | `new Client({ node: "http://..." })` |
| Index a doc | `es.index(index=, document=)` | `await client.index({ index, document })` |
| Search | `es.search(index=, query=)` | `await client.search({ index, query })` |
| Async version | `AsyncElasticsearch` | all calls are already async |
| Bulk | `helpers.bulk()` | `client.helpers.bulk()` |

```python
# Python way
from elasticsearch import Elasticsearch                  # import client
es = Elasticsearch("http://localhost:9200")              # create client
r = es.search(index="dishes", query={"match": {"name": "dosa"}})   # keyword arguments
print(r["hits"]["total"]["value"])                       # response behaves like a dict
```
```javascript
// JavaScript way
const { Client } = require("@elastic/elasticsearch");   // import client
const client = new Client({ node: "http://localhost:9200" });   // create client
const r = await client.search({ index: "dishes", query: { match: { name: "dosa" } } });   // one object
console.log(r.hits.total.value);                         // response is an object (8.x+ returns body directly)
```

Key difference: the Python client takes keyword arguments (`index=`, `query=`), while JS takes one options object. Since the 8.x clients, the old `body=` argument is deprecated in Python; pass `query=`, `size=`, `sort=` directly.

---

## 🟠 FastAPI Connection
Create ONE client when the app starts (or one module-level object), expose it through `Depends`, and use `AsyncElasticsearch` in `async def` endpoints so search does not block the event loop. In tests, override the dependency with a fake.

```python
# FastAPI example — search endpoint with an injectable client (fake used so it runs without a server)
from typing import Any                                        # typing
from fastapi import Depends, FastAPI                          # FastAPI + DI
from fastapi.testclient import TestClient                     # in-process test client

app: FastAPI = FastAPI()                                      # app


class FakeES:                                                 # stands in for Elasticsearch
    def search(self, **kw: Any) -> dict[str, Any]:
        return {"hits": {"hits": [{"_id": "1", "_source": {"name": "Dosa"}}]}}


def get_es() -> FakeES:                                       # in prod: return the shared Elasticsearch()
    return FakeES()


@app.get("/search")                                           # GET /search?q=dosa
def search(q: str, es: FakeES = Depends(get_es)) -> list[dict[str, str]]:
    resp = es.search(index="dishes", query={"match": {"name": q}})   # same call as real client
    return [{"id": h["_id"], **h["_source"]} for h in resp["hits"]["hits"]]


print(TestClient(app).get("/search", params={"q": "dosa"}).json())
# Output:
# [{'id': '1', 'name': 'Dosa'}]
```
Verified: run with TestClient and the fake. In production swap `FakeES` for `AsyncElasticsearch` and use `await es.search(...)` (not run here).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using Elasticsearch as the primary database
✅ Correct: keep the source of truth in PostgreSQL/MongoDB and sync a copy into Elasticsearch for search

```python
# Wrong — only copy of the order lives in ES (no real transactions, can lose data on bad config)
# es.index(index="orders", document=order)
# Right — save to the DB first, then index a searchable copy (or sync via queue / CDC)
# db.add(order); db.commit(); es.index(index="orders", id=str(order.id), document=order.search_view())
```

❌ Mistake 2: Searching right after indexing and finding nothing
✅ Correct: documents become visible only after a refresh (about 1 second). In tests use `refresh=True` or `es.indices.refresh()`

```python
# Wrong
# es.index(index="dishes", id="1", document=doc)
# es.search(index="dishes", query={"match_all": {}})   # may return 0 hits!
# Right
# es.index(index="dishes", id="1", document=doc, refresh="wait_for")   # waits until searchable
```

❌ Mistake 3: Indexing documents one by one in a loop
✅ Correct: use `helpers.bulk` (thousands of docs per request)

```python
# Wrong — 100000 HTTP calls
# for row in rows: es.index(index="dishes", document=row)
# Right — a few HTTP calls
# from elasticsearch.helpers import bulk
# bulk(es, ({"_index": "dishes", "_source": r} for r in rows))
```

❌ Mistake 4: Using `match` on exact fields (ids, emails, status)
✅ Correct: use `term` on a `keyword` field, and put it in `filter` so it is cached and unscored

```python
# Wrong: analyzed text query on an exact value
wrong: dict = {"match": {"status": "In Progress"}}          # splits into tokens "in" and "progress"
# Right: exact match on keyword field
right: dict = {"term": {"status.keyword": "In Progress"}}   # whole value must match
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (no Elasticsearch server is running on port 9)
from elasticsearch import Elasticsearch
es = Elasticsearch("http://localhost:9")
print(es.ping())
print(es.options(request_timeout=5) is es)
print(type(es.options(request_timeout=5)).__name__)
```
Answer: `False`, `False`, `Elasticsearch`. `ping()` does not raise when the server is unreachable; it returns `False` (it is a health check). `options()` does not change the client in place: it returns a NEW client object that shares the same connection pool but has different per-request settings (timeout, headers, retries), so `is es` is `False`. This is a change from the old 7.x style where such settings were passed on each call. (Output verified with elasticsearch 9.5.1.)

---

## ⚫ Interview Questions + Answers

Q1: What is an inverted index and why is search fast?
A1: An inverted index maps each token to the list of documents containing it (like the index at the end of a book). To find "paneer" Elasticsearch looks up one entry instead of scanning all documents. It also stores term frequency, which is used to compute the BM25 relevance score.

Q2: What is the difference between `match` and `term` queries?
A2: `match` analyzes the input (lowercases, tokenizes) and is used for full-text fields (`text`). `term` does NOT analyze and looks for the exact value, used for `keyword`, numbers, booleans and dates. Using `term` on an analyzed text field is a very common bug because the stored tokens are lowercase.

Q3: What is the difference between `must` and `filter` in a `bool` query?
A3: `must` clauses affect the relevance score. `filter` clauses only include or exclude documents, do not compute a score, and results can be cached by Elasticsearch, so they are faster. Use `filter` for city, price range, status and date; use `must` for the search text.

Q4: Why is Elasticsearch called "near real-time"?
A4: New documents are written to an in-memory buffer and become searchable only after a refresh, which by default happens every second. `GET` by id is real-time, but `search` is near real-time. You can force it with `refresh=True`, but doing that on every write hurts performance.

Q5: How do you read millions of documents with the Python client?
A5: Normal `from`/`size` paging is limited to 10,000 results (`index.max_result_window`). Use `helpers.scan()` (scroll API) for export, or `search_after` with a point-in-time (PIT) for consistent deep paging. `helpers.scan` yields documents lazily so memory stays small.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Full-text search with ranking, typo tolerance, autocomplete
- Log and event search (ELK), analytics with aggregations
- Product/restaurant catalogue search with filters and facets
- Semantic or hybrid search with dense vectors (RAG)

❌ Avoid when:
- You need ACID transactions or the only copy of critical data (use PostgreSQL)
- Data is small and `LIKE` or PostgreSQL full-text search is enough
- You need frequent joins between entities (ES is document-oriented)
- You cannot afford the operational cost of a cluster (consider managed service or pg_trgm)

---

## 📊 Visual Diagram
```
 FastAPI app ──(elasticsearch-py)──► Elasticsearch cluster
                                        │
   index "dishes"                       ▼
   ┌──────────────────────┐    Inverted index
   │ doc1 "Paneer Tikka"  │     paneer → [doc1, doc7]
   │ doc2 "Masala Dosa"   │     tikka  → [doc1]
   │ doc7 "Paneer Wrap"   │     dosa   → [doc2]
   └──────────────────────┘
 search "paneer" → lookup token → docs [1,7] → rank by BM25 → hits
 write path: index → buffer → refresh (~1s) → searchable
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Collection of documents (like a table) | Documents का समूह (table जैसा) |
| Document | One JSON record | एक JSON record |
| Mapping | Field types of an index | Index के fields के types |
| Inverted index | Token -> documents lookup | शब्द -> documents की तालिका |
| Query DSL | JSON language for queries | Queries के लिए JSON भाषा |
| BM25 | Default relevance scoring | Default relevance score formula |
| Refresh | Makes new docs searchable | नए docs को searchable बनाना |
| Bulk | Many operations in one request | एक request में कई operations |

---

## ⚡ 3-Line Summary
English: `elasticsearch-py` is the official client for Elasticsearch, a search engine that keeps an inverted index for fast, ranked full-text search. You index JSON documents and search with the Query DSL, using `must` for scored text and `filter` for exact conditions. Keep your main database separate, load data with `bulk`, and remember search is near real-time.
Hindi: `elasticsearch-py` Elasticsearch का official client है, जो तेज और ranked full-text search के लिए inverted index रखता है। आप JSON documents index करते हैं और Query DSL से search करते हैं: scored text के लिए `must` और exact conditions के लिए `filter`। मुख्य database अलग रखें, data `bulk` से load करें, और याद रखें कि search near real-time होता है।

---

## ➡️ Next Topic
**370. Database Connection Pooling** — now that you can talk to many databases, learn how to reuse connections so each request does not pay the expensive connect cost.
