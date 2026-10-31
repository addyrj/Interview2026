---

# 138. Qdrant Basics
# हिंदी में: Qdrant Basics (Rust में बना open-source vector database)

---

## 🔵 Simple Definition (English)
Qdrant (say "quadrant") is an open-source vector database written in Rust. You create a **collection** with a vector size and distance, then store **points** (id + vector + **payload**, which is JSON metadata). Search uses HNSW with powerful payload filtering. You can run it in memory for tests, in Docker, self-hosted in a cluster, or on Qdrant Cloud.

## 🔵 सरल परिभाषा (Hindi)
Qdrant (उच्चारण "क्वाड्रेंट") Rust में लिखा open-source vector database है। आप vector size और distance के साथ **collection** बनाते हैं और **points** (id + vector + **payload**, यानी JSON metadata) store करते हैं। Search HNSW और शक्तिशाली payload filtering के साथ होता है। इसे tests के लिए memory में, Docker में, cluster में self-host या Qdrant Cloud पर चला सकते हैं।

---

## 🔴 Problem it Solves
Developers need a fast, filter-friendly vector database that is easy to start (one `docker run` or even `:memory:`) yet scales to billions of points with quantisation and sharding. Many engines slow down badly with selective filters; Qdrant integrates filtering into the HNSW search so filtered queries stay fast and accurate.

## 🔴 यह क्यों बना? (Hindi)
Developers को ऐसा तेज़, filter-friendly vector database चाहिए जो शुरू करना आसान हो (एक `docker run` या `:memory:`) और quantisation व sharding से अरबों points तक scale हो। कई engines selective filters के साथ बहुत धीमे हो जाते हैं; Qdrant filtering को HNSW search में जोड़ता है, इसलिए filtered queries तेज़ और सटीक रहती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start: docker run -p 6333:6333 qdrant/qdrant   (or QdrantClient(":memory:") for tests)
Step 2 → client = QdrantClient(url="http://localhost:6333")
Step 3 → client.create_collection(name, vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
Step 4 → client.upsert(name, points=[PointStruct(id=1, vector=[...], payload={...})])
Step 5 → (Optional) client.create_payload_index(name, "country", PayloadSchemaType.KEYWORD) for fast filters
Step 6 → client.query_points(name, query=vec, limit=5, query_filter=Filter(...), with_payload=True)
Step 7 → Read .points: each has id, score, payload
Step 8 → Maintain: set_payload, delete, scroll (iterate), count
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → शुरू करो: docker run -p 6333:6333 qdrant/qdrant   (tests के लिए QdrantClient(":memory:"))
Step 2 → client = QdrantClient(url="http://localhost:6333")
Step 3 → client.create_collection(name, vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
Step 4 → client.upsert(name, points=[PointStruct(id=1, vector=[...], payload={...})])
Step 5 → (Optional) तेज़ filters के लिए client.create_payload_index(name, "country", PayloadSchemaType.KEYWORD)
Step 6 → client.query_points(name, query=vec, limit=5, query_filter=Filter(...), with_payload=True)
Step 7 → .points पढ़ो: हर में id, score, payload
Step 8 → Maintenance: set_payload, delete, scroll (iterate), count
```

---

## 🟡 Real World Example
**Tariff Classification System**: collection `tariff` (1536, cosine), payload `{hs_code, country, chapter, text, active}` with payload indexes on `country` and `chapter`. A query "wireless earbuds" for an Indian importer uses `Filter(must=[country == "IN", active == True])`; only valid Indian codes are ranked. Developers run `QdrantClient(":memory:")` in unit tests so CI needs no server.

**Zomato AI**: restaurants collection with geo payloads; filter by location radius plus vector similarity of the cuisine description.

## 🟡 Real Example Hindi mein
**Tariff System**: Collection `tariff` (1536, cosine), payload `{hs_code, country, chapter, text, active}` और `country`, `chapter` पर payload indexes। भारतीय importer की "wireless earbuds" query में `Filter(must=[country == "IN", active == True])` लगता है; सिर्फ़ valid भारतीय codes rank होते हैं। Developers unit tests में `QdrantClient(":memory:")` चलाते हैं, CI को server नहीं चाहिए। **Zomato**: restaurants collection में geo payload; location radius filter + cuisine description की vector similarity।

---

## 💻 Code Example — Basic
```python
# Basic: Qdrant in-memory (pip install qdrant-client). No server needed, great for learning and tests.
from qdrant_client import QdrantClient                      # client
from qdrant_client.models import (                           # data models
    Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams,
)

client = QdrantClient(":memory:")                            # local in-process database
NAME = "tariff"                                              # collection name

if not client.collection_exists(NAME):                       # idempotent creation
    client.create_collection(
        collection_name=NAME,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),   # size must equal embedding size
    )

client.upsert(                                               # insert or overwrite points
    collection_name=NAME,
    points=[
        PointStruct(id=1, vector=[0.9, 0.1, 0.0, 0.1], payload={"hs_code": "8518.30", "country": "IN"}),
        PointStruct(id=2, vector=[0.8, 0.2, 0.1, 0.1], payload={"hs_code": "8518.30-US", "country": "US"}),
        PointStruct(id=3, vector=[0.0, 0.1, 0.9, 0.2], payload={"hs_code": "6205", "country": "IN"}),
    ],
)

res = client.query_points(                                   # similarity search
    collection_name=NAME,
    query=[1.0, 0.0, 0.1, 0.0],                              # query vector
    limit=2,                                                 # top 2
    query_filter=Filter(must=[FieldCondition(key="country", match=MatchValue(value="IN"))]),   # only India
    with_payload=True,                                       # return payload too
)
for p in res.points:                                         # iterate matches
    print(p.id, round(p.score, 3), p.payload["hs_code"])     # id, cosine score, code
```

## 💻 Code Example — Advanced
```python
# Advanced: async repository with payload indexes, batched upsert, filtered search, error handling.
import asyncio                                               # async runtime
import logging                                               # logs
import uuid                                                  # deterministic point ids
from typing import Any, Dict, List, Optional                 # type hints

from qdrant_client import AsyncQdrantClient                  # native async client
from qdrant_client.http.exceptions import UnexpectedResponse # HTTP errors from the server
from qdrant_client.models import (
    Distance, FieldCondition, Filter, MatchAny, MatchValue, PayloadSchemaType,
    PointStruct, Range, VectorParams,
)

log = logging.getLogger("qdrant-repo")                       # logger
NS = uuid.UUID("12345678-1234-5678-1234-567812345678")       # fixed namespace for uuid5

def point_id(key: str) -> str:
    return str(uuid.uuid5(NS, key))                          # same key -> same id (idempotent). Qdrant ids: int or UUID

class TariffRepo:
    def __init__(self, url: str = "http://localhost:6333", name: str = "tariff", dim: int = 1536) -> None:
        self.client = AsyncQdrantClient(url=url)             # async connection
        self.name, self.dim = name, dim                      # collection settings

    async def setup(self) -> None:
        if not await self.client.collection_exists(self.name):
            await self.client.create_collection(
                self.name, vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE))
        for field, schema in (("country", PayloadSchemaType.KEYWORD),
                              ("chapter", PayloadSchemaType.INTEGER)):    # index the fields you filter by
            await self.client.create_payload_index(self.name, field_name=field, field_schema=schema)

    async def upsert(self, rows: List[Dict[str, Any]], batch: int = 128) -> None:
        for i in range(0, len(rows), batch):                 # batch to keep requests small
            chunk = rows[i:i + batch]
            pts = [PointStruct(id=point_id(r["key"]), vector=r["vector"], payload=r["payload"]) for r in chunk]
            try:
                await self.client.upsert(self.name, points=pts, wait=True)   # wait=True: durable before return
            except UnexpectedResponse as exc:                # e.g. wrong vector size -> 400
                log.error("upsert failed: %s", exc)
                raise

    async def search(self, vec: List[float], country: str, chapters: Optional[List[int]] = None,
                     min_score: float = 0.4, k: int = 5) -> List[Dict[str, Any]]:
        must: List[FieldCondition] = [FieldCondition(key="country", match=MatchValue(value=country))]
        if chapters:
            must.append(FieldCondition(key="chapter", match=MatchAny(any=chapters)))   # chapter in [..]
        res = await self.client.query_points(
            self.name, query=vec, limit=k, query_filter=Filter(must=must),
            score_threshold=min_score, with_payload=True)    # server drops weak matches
        return [{"id": p.id, "score": p.score, **(p.payload or {})} for p in res.points]

    async def close(self) -> None:
        await self.client.close()                            # release connections

# Range filter example: FieldCondition(key="year", range=Range(lte=2024))
# Token usage: Qdrant uses 0 LLM tokens; only embeddings cost tokens.
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager                  # lifespan
from fastapi import FastAPI, HTTPException                   # FastAPI
from openai import AsyncOpenAI                                # embeddings

oai = AsyncOpenAI()                                           # client
repo = TariffRepo()                                           # repository

@asynccontextmanager
async def lifespan(app: FastAPI):
    await repo.setup()                                        # create collection + indexes at startup
    yield                                                     # serve
    await repo.close()                                        # clean shutdown

app = FastAPI(lifespan=lifespan)                              # app with lifespan

@app.get("/tariff/search")                                    # search route
async def search(q: str, country: str = "IN") -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    try:
        return {"hits": await repo.search(emb.data[0].embedding, country)}
    except Exception as exc:                                  # connection or server errors
        raise HTTPException(503, f"qdrant error: {exc}")
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-qdrant qdrant-client
from langchain_openai import OpenAIEmbeddings                # embeddings
from langchain_qdrant import QdrantVectorStore                # integration
from qdrant_client import QdrantClient                        # client
from qdrant_client.models import Distance, VectorParams       # collection config

client = QdrantClient(":memory:")                             # use url="http://localhost:6333" in real apps
client.create_collection("lc_tariff", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
vs = QdrantVectorStore(client=client, collection_name="lc_tariff",
                       embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
vs.add_texts(["Headphones and earphones"], metadatas=[{"country": "IN"}])   # embed + upsert
retriever = vs.as_retriever(search_kwargs={"k": 3})           # standard retriever for LCEL/LangGraph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using arbitrary strings as point ids
✅ Correct: ids must be unsigned integers or UUIDs; derive UUIDs from your keys (uuid5).

```python
# Wrong: raises a validation error
PointStruct(id="8518.30#0", vector=v)
# Right
PointStruct(id=str(uuid.uuid5(NS, "8518.30#0")), vector=v, payload={"key": "8518.30#0"})
```

❌ Mistake 2: Filtering on a big collection without payload indexes
✅ Correct: create payload indexes for fields used in filters.

```python
# Wrong: slow filtered queries (full payload scan)
client.query_points(name, query=v, query_filter=flt)
# Right
client.create_payload_index(name, field_name="country", field_schema=PayloadSchemaType.KEYWORD)
```

❌ Mistake 3: Using the deprecated `client.search(...)` in new code
✅ Correct: use `client.query_points(...)`.

---

## 🧠 Tricky Interview Question

**Q**: "Your Qdrant filtered query returns good results in dev (10k points) but is slow and sometimes misses results in prod (50M points) when the filter matches only 0.01% of points. Why and what do you do?"

**Answer**: HNSW is built over all points, so a very selective filter can disconnect the graph for the allowed subset, and the traversal must skip many non-matching nodes. Qdrant mitigates this with filterable HNSW (extra links based on payload indexes) and by switching to a payload-index-based exact scan when the filter cardinality is small. For this to work you must create payload indexes on the filtered fields (ideally before inserting data) and, for tenant-style filters, mark the field as a tenant/partition key or use separate collections/shards. Check query plans through benchmarks, raise `hnsw_ef`, and measure recall against an exact search with `exact=True`.

---

## ⚫ Interview Questions + Answers

Q1: What is a point in Qdrant?
A1: A record made of an id (integer or UUID), one or more vectors and an optional JSON payload.

Q2: How is Qdrant different from FAISS?
A2: FAISS is a library for in-process vector search with no storage, payloads or server. Qdrant is a full database with persistence, payload filtering, replication, an API and clustering.

Q3: What are payload indexes for?
A3: They make filters on payload fields fast and let the engine plan filtered vector search efficiently.

Q4: What is `wait=True` in upsert?
A4: The call returns only after the operation is applied (searchable/durable), avoiding "I wrote it but cannot find it" races in tests.

Q5: How do you reduce Qdrant's memory use for 100M vectors?
A5: Store vectors on disk (`on_disk=True`) with HNSW in RAM, enable quantisation (scalar int8 gives ~4x, binary up to ~32x) and keep original vectors on disk for rescoring, use smaller embedding dimensions, and shard across nodes. Validate recall with and without quantisation using `search_params` (rescore) and exact search on a sample before rollout.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need strong payload filtering with vector search
- Open-source, self-hostable, or a simple managed option
- Easy local testing with `:memory:`

❌ Avoid when:
- You need full SQL/joins/transactions (use Postgres + pgvector)
- A few thousand vectors and you want zero dependencies (a simple in-process library is enough)

---

## 📊 Visual Diagram
```
  Collection "tariff"  (size=1536, cosine)
  ┌───────────────────────────────────────────────────────────┐
  │ Point 1: id, vector[1536], payload {country:IN, ch:85}    │
  │ Point 2: id, vector[1536], payload {country:US, ch:85}    │
  │ ...                                                       │
  │ HNSW graph   +   payload indexes (country, chapter)       │
  └───────────────────────────────────────────────────────────┘
   query_points(vec, filter: country=IN) ─► filtered HNSW ─► [(id, score, payload)] ─► LLM
```

---

## 💰 Cost Impact
- Self-hosted: pay for machine RAM/disk. Rough RAM = vectors x dim x 4 bytes (+ HNSW overhead). 10M x 1536 = ~61 GB; with int8 scalar quantisation ~15 GB in RAM (originals on disk).
- Qdrant Cloud has a free tier and paid clusters; check current pricing.
- Tokens: Qdrant itself uses none. Using `score_threshold` and filters sends fewer, better chunks to the LLM, for example 4 chunks (~1,200 tokens) instead of 10 (~3,000), a 60% prompt saving per query.
- Optimise: quantisation, on-disk vectors, payload indexes only for fields you filter on, smaller dims.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | Set of points with the same vector config | समान vector config वाले points का समूह |
| Point | Id + vector + payload | Id + vector + payload |
| Payload | JSON metadata of a point | Point का JSON metadata |
| Payload index | Index on a payload field | Payload field पर index |
| Quantisation | Compressing vectors | Vectors compress करना |
| score_threshold | Minimum acceptable score | न्यूनतम score |
| Shard | Partition of a collection | Collection का हिस्सा |

---

## ⚡ 3-Line Summary
English: Qdrant stores points (id, vector, payload) in collections and searches with HNSW plus fast payload filters. Use `:memory:` for tests, payload indexes for filtered fields and `query_points` for search. Quantisation and on-disk vectors control memory.
Hindi: Qdrant collections में points (id, vector, payload) रखता है और HNSW व तेज़ payload filters से search करता है। Tests के लिए `:memory:`, filtered fields के लिए payload indexes और search के लिए `query_points` use करो। Memory के लिए quantisation और on-disk vectors।

---

## ➡️ Next Topic
**139. Chroma DB — Complete Guide** — the simplest developer-friendly vector store for prototypes and small apps.
