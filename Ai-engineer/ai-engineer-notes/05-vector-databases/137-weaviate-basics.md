---

# 137. Weaviate Basics
# हिंदी में: Weaviate Basics (open-source vector database)

---

## 🔵 Simple Definition (English)
Weaviate is an open-source vector database (self-host with Docker/Kubernetes or use Weaviate Cloud). You define a **collection** (like a table) with typed **properties**, then store **objects** (properties + vector). It supports HNSW vector search, keyword (BM25) search, **hybrid search**, metadata filters, multi-tenancy, and optional built-in "vectorizer" modules that embed text for you.

## 🔵 सरल परिभाषा (Hindi)
Weaviate एक open-source vector database है (Docker/Kubernetes पर खुद host करो या Weaviate Cloud use करो)। आप typed **properties** वाली **collection** (table जैसी) बनाते हैं और **objects** (properties + vector) store करते हैं। यह HNSW vector search, keyword (BM25) search, **hybrid search**, metadata filters, multi-tenancy और optional built-in "vectorizer" modules (जो text खुद embed करते हैं) देता है।

---

## 🔴 Problem it Solves
Teams often need vector search AND keyword search AND structured filters in one engine, with control over hosting (data residency, on-prem). Pure vector libraries (FAISS) lack storage and filtering; managed-only services lack self-hosting. Weaviate gives an open-source, schema-based database with hybrid search and a rich filter language.

## 🔴 यह क्यों बना? (Hindi)
Teams को अक्सर एक ही engine में vector search, keyword search और structured filters चाहिए, साथ में hosting पर control (data residency, on-prem)। FAISS जैसी libraries में storage और filtering नहीं; सिर्फ़ managed services में self-hosting नहीं। Weaviate open-source, schema-based database है जिसमें hybrid search और अच्छा filter language है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run Weaviate: docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:<version>
Step 2 → client = weaviate.connect_to_local()   (or connect_to_weaviate_cloud(...))
Step 3 → client.collections.create("TariffHeading", properties=[...], vectorizer_config=Configure.Vectorizer.none())
Step 4 → col = client.collections.get("TariffHeading")
Step 5 → col.data.insert(properties={...}, vector=[...])  or  insert_many([...])
Step 6 → Query: col.query.near_vector(...) | col.query.bm25(...) | col.query.hybrid(...)
Step 7 → Add filters: Filter.by_property("country").equal("IN")
Step 8 → client.close()  (always close; use try/finally or `with`)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Weaviate चलाओ: docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:<version>
Step 2 → client = weaviate.connect_to_local()   (या connect_to_weaviate_cloud(...))
Step 3 → client.collections.create("TariffHeading", properties=[...], vectorizer_config=Configure.Vectorizer.none())
Step 4 → col = client.collections.get("TariffHeading")
Step 5 → col.data.insert(properties={...}, vector=[...])  या  insert_many([...])
Step 6 → Query: col.query.near_vector(...) | col.query.bm25(...) | col.query.hybrid(...)
Step 7 → Filters लगाओ: Filter.by_property("country").equal("IN")
Step 8 → client.close()  (हमेशा close करो; try/finally या `with`)
```

---

## 🟡 Real World Example
**Tariff Classification System**: collection `TariffHeading` with properties `hs_code`, `text`, `country`, `chapter`. Users often type exact codes ("8517.13") or product words ("smartphone"). `hybrid` search with `alpha=0.5` blends BM25 (catches the exact code) and vector similarity (catches meaning), which beats either alone. The team self-hosts on Kubernetes because customs data must stay in India.

**Amazon-style**: product search combining semantic similarity with keyword matches on brand names and filters on price.

## 🟡 Real Example Hindi mein
**Tariff System**: Collection `TariffHeading`, properties `hs_code`, `text`, `country`, `chapter`। Users कभी exact code ("8517.13") लिखते हैं और कभी product words ("smartphone")। `alpha=0.5` वाला `hybrid` search BM25 (exact code पकड़ता है) और vector similarity (meaning पकड़ती है) मिलाता है, इसलिए अकेले किसी एक से बेहतर है। Team Kubernetes पर self-host करती है क्योंकि customs data भारत में रहना चाहिए। **Amazon-style**: semantic similarity + brand keyword match + price filter।

---

## 💻 Code Example — Basic
```python
# Basic: Weaviate v4 Python client (pip install weaviate-client). Needs a running Weaviate at localhost:8080.
# Collection created with `vectorizer_config=Configure.Vectorizer.none()` = we supply our own vectors.
# (Newer client versions also offer vector_config=...; check your installed version's docs.)
import weaviate                                              # client library
from weaviate.classes.config import Configure, DataType, Property   # schema helpers
from weaviate.classes.query import Filter, MetadataQuery     # query helpers

client = weaviate.connect_to_local()                         # connects to localhost:8080 / gRPC 50051
try:                                                         # always close the client
    NAME = "TariffHeading"                                   # collection name (capitalised by convention)
    if client.collections.exists(NAME):                      # keep the script re-runnable
        client.collections.delete(NAME)                      # start clean for the demo
    col = client.collections.create(                         # create the collection
        NAME,
        vectorizer_config=Configure.Vectorizer.none(),       # bring-your-own vectors
        properties=[                                         # typed schema
            Property(name="hs_code", data_type=DataType.TEXT),
            Property(name="text", data_type=DataType.TEXT),
            Property(name="country", data_type=DataType.TEXT),
        ],
    )
    col.data.insert(                                         # insert one object
        properties={"hs_code": "8518.30", "text": "Headphones and earphones", "country": "IN"},
        vector=[0.9, 0.1, 0.0, 0.1],                         # toy 4-D vector
    )
    col.data.insert(
        properties={"hs_code": "6205", "text": "Men's shirts", "country": "IN"},
        vector=[0.0, 0.1, 0.9, 0.2],
    )
    res = col.query.near_vector(                             # vector similarity search
        near_vector=[1.0, 0.0, 0.1, 0.0],                    # query vector
        limit=1,                                             # top 1
        filters=Filter.by_property("country").equal("IN"),   # metadata filter
        return_metadata=MetadataQuery(distance=True),        # ask for the distance
    )
    for obj in res.objects:                                  # iterate results
        print(obj.properties["hs_code"], obj.metadata.distance)   # smaller distance = closer (cosine default)
finally:
    client.close()                                           # releases connections
```

## 💻 Code Example — Advanced
```python
# Advanced: typed repository with batch import (error reporting), hybrid search, and an async wrapper.
import asyncio                                               # async runtime
import logging                                               # logs
from contextlib import contextmanager                        # safe client lifecycle
from typing import Any, Dict, Iterator, List, Optional       # type hints

import weaviate                                              # client
from weaviate.classes.query import Filter, MetadataQuery     # query helpers

log = logging.getLogger("weaviate-repo")                     # logger

@contextmanager
def connect() -> Iterator[weaviate.WeaviateClient]:
    client = weaviate.connect_to_local()                     # or connect_to_weaviate_cloud(url, auth_credentials=...)
    try:
        yield client                                         # use the client
    finally:
        client.close()                                       # ALWAYS close

class HeadingRepo:
    def __init__(self, name: str = "TariffHeading") -> None:
        self.name = name                                     # collection name

    def import_batch(self, rows: List[Dict[str, Any]]) -> int:
        """rows: [{'props': {...}, 'vector': [...]}]. Returns number of FAILED objects."""
        with connect() as client:
            col = client.collections.get(self.name)          # existing collection
            with col.batch.dynamic() as batch:               # auto-sized batches
                for r in rows:
                    batch.add_object(properties=r["props"], vector=r["vector"])   # queued
            failed = col.batch.failed_objects                # batch never raises per object: CHECK this
            if failed:
                log.error("%d objects failed, first error: %s", len(failed), failed[0].message)
            return len(failed)

    def hybrid(self, text: str, vec: List[float], country: Optional[str] = None,
               alpha: float = 0.5, k: int = 5) -> List[Dict[str, Any]]:
        """alpha=0 pure keyword (BM25), alpha=1 pure vector."""
        if not 0.0 <= alpha <= 1.0:                          # validate
            raise ValueError("alpha must be between 0 and 1")
        flt = Filter.by_property("country").equal(country) if country else None   # optional filter
        with connect() as client:
            col = client.collections.get(self.name)
            res = col.query.hybrid(query=text, vector=vec, alpha=alpha, limit=k,
                                   filters=flt, return_metadata=MetadataQuery(score=True))
            return [{**o.properties, "score": o.metadata.score} for o in res.objects]

    async def hybrid_async(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.hybrid, *args, **kwargs)   # keeps FastAPI responsive
# (Weaviate client also offers a native async client: weaviate.use_async_with_local(); check your version.)
# Token usage: Weaviate itself uses 0 LLM tokens unless you enable a vectorizer module, which calls an
# embedding provider (billed per token by that provider).
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException                  # FastAPI
from openai import AsyncOpenAI                               # embeddings

app = FastAPI()                                              # app
oai = AsyncOpenAI()                                          # client
repo = HeadingRepo()                                         # repository

@app.get("/headings/search")                                 # hybrid search route
async def search(q: str, country: str | None = None, alpha: float = 0.5) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)   # query vector
    try:
        hits = await repo.hybrid_async(q, emb.data[0].embedding, country, alpha)
    except ValueError as exc:                                # bad alpha
        raise HTTPException(422, str(exc))
    except Exception as exc:                                 # connection problems
        raise HTTPException(503, f"weaviate unavailable: {exc}")
    return {"hits": hits}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-weaviate weaviate-client
import weaviate                                              # client
from langchain_openai import OpenAIEmbeddings                # embeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore   # integration

client = weaviate.connect_to_local()                         # v4 client (LangChain integration requires v4)
try:
    vs = WeaviateVectorStore(client=client, index_name="TariffHeadingLC", text_key="text",
                             embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
    vs.add_texts(["Headphones and earphones"], metadatas=[{"country": "IN"}])   # embed + store
    docs = vs.similarity_search("wireless earbuds", k=3)     # vector search
    retriever = vs.as_retriever(search_kwargs={"k": 3})      # use in LCEL / LangGraph nodes
finally:
    client.close()                                           # close when the app shuts down
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to close the client (leaks connections, scripts hang)
✅ Correct: `try/finally` or a context manager.

```python
# Wrong
client = weaviate.connect_to_local(); do_work(client)
# Right
with weaviate.connect_to_local() as client:
    do_work(client)
```

❌ Mistake 2: Assuming batch inserts raise on bad objects
✅ Correct: inspect `failed_objects` after the batch.

```python
# Wrong: silently loses rows
with col.batch.dynamic() as b:
    for r in rows: b.add_object(properties=r)
# Right
if col.batch.failed_objects: handle(col.batch.failed_objects)
```

❌ Mistake 3: Mixing old v3 syntax (`client.query.get(...)`) with the v4 client
✅ Correct: use `client.collections.get(...).query...`; v3 code does not work on the v4 client.

---

## 🧠 Tricky Interview Question

**Q**: "Hybrid search returns a keyword-only match at rank 1 although the vector similarity is poor. Is that a bug?"

**Answer**: No. Hybrid search fuses two ranked lists (BM25 and vector) using a fusion method (relative score or ranked fusion) weighted by `alpha`. An exact keyword hit (like an HS code string) can legitimately rank highly even when its embedding is distant, which is exactly why hybrid is used for identifiers. If it hurts, raise `alpha` toward vector, apply filters, or use a reranker. Tune `alpha` on a golden set with both code-like and natural-language queries.

---

## ⚫ Interview Questions + Answers

Q1: What is a Weaviate collection?
A1: The equivalent of a table/class: a named set of objects that share a schema (properties) and vector index configuration.

Q2: What vector index does Weaviate use?
A2: HNSW by default (also flat and dynamic indexes, and compression like PQ/BQ/SQ to reduce memory).

Q3: What is hybrid search?
A3: A query that combines BM25 keyword scoring with vector similarity and fuses the results, controlled by `alpha` (0 = keyword only, 1 = vector only).

Q4: Bring-your-own vectors vs vectorizer modules?
A4: With `Vectorizer.none()` you embed yourself and pass `vector=`. With a module (e.g. text2vec-openai) Weaviate calls the provider on insert and query, which is convenient but ties you to that provider and bills tokens there.

Q5: How would you operate Weaviate in production for 50M objects?
A5: Run a multi-node cluster on Kubernetes with sharding and replication, enable vector compression (PQ or BQ) to reduce RAM, use multi-tenancy for tenant isolation, set resource limits and persistent volumes, back up regularly, and monitor memory, query latency and indexing queue. Benchmark recall after compression, batch-import with failure handling, and plan re-embedding (new collection, alias swap) for model changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want open-source with self-hosting and hybrid search
- You need multi-tenancy, filters and a schema
- You want optional built-in embedding modules

❌ Avoid when:
- A tiny prototype (Chroma is lighter)
- You have no capacity to operate a database (consider a managed option)

---

## 📊 Visual Diagram
```
 Docker / K8s / Weaviate Cloud
 ┌──────────────────────────────────────────────┐
 │ Collection "TariffHeading"                   │
 │  properties: hs_code, text, country          │
 │  ├─ object {props + vector}                  │
 │  ├─ HNSW vector index                        │
 │  ├─ inverted (BM25) index                    │
 │  └─ filters on properties                    │
 └──────────────────────────────────────────────┘
   near_vector ─┐
   bm25 ────────┼─► hybrid (alpha) ─► ranked objects ─► LLM
   filters ─────┘
```

---

## 💰 Cost Impact
- Self-hosting: you pay for machines (RAM-heavy for HNSW). Enable compression (PQ/BQ) to reduce memory 4-32x with a small recall loss.
- Weaviate Cloud bills by cluster size/usage, so check current plans.
- Vectorizer modules add embedding cost (e.g. text-embedding-3-small at $0.02 per 1M tokens): 1M chunks x 300 tokens = 300M tokens = $6, the same as embedding yourself.
- Hybrid search often improves precision so you can send fewer chunks to the LLM (for example 3 chunks = ~900 tokens instead of 8 = ~2,400 tokens).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | Named group of objects with a schema | Schema वाले objects का group |
| Property | Typed field of an object | Object का typed field |
| Vectorizer | Module that creates embeddings | Embeddings बनाने वाला module |
| Hybrid search | BM25 + vector fusion | Keyword + vector का मिश्रण |
| alpha | Hybrid weight (0 keyword, 1 vector) | Hybrid का weight |
| BM25 | Keyword ranking function | Keyword ranking function |
| Multi-tenancy | Isolated data per tenant | हर tenant का अलग data |

---

## ⚡ 3-Line Summary
English: Weaviate is an open-source, schema-based vector database with HNSW, BM25 and hybrid search plus filters. Create a collection, insert objects with vectors, query with near_vector, bm25 or hybrid, and always close the client. Use compression to control RAM.
Hindi: Weaviate open-source, schema-based vector database है जिसमें HNSW, BM25, hybrid search और filters हैं। Collection बनाओ, vectors के साथ objects insert करो, near_vector, bm25 या hybrid से query करो और client हमेशा close करो। RAM के लिए compression use करो।

---

## ➡️ Next Topic
**138. Qdrant Basics** — another open-source vector database (Rust) with powerful payload filtering.
