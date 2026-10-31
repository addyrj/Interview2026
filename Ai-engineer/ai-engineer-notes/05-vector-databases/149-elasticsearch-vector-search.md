---

# 149. Elasticsearch Vector Search
# हिंदी में: Elasticsearch Vector Search

---

## 🔵 Simple Definition (English)
Elasticsearch (and OpenSearch) can store embeddings in a `dense_vector` field and search them with kNN, while keeping its classic BM25 keyword search, filters and aggregations. It is a search engine first and a vector store second.

## 🔵 सरल परिभाषा (Hindi)
Elasticsearch (और OpenSearch) `dense_vector` field में embeddings रखकर kNN search कर सकता है, साथ में BM25 keyword search, filters और aggregations भी मिलते हैं। यह पहले search engine है, फिर vector store।

---

## 🔴 Problem it Solves
Many companies already have Elasticsearch for logs or product search. Their users still need exact keyword matches (HS code "8518.30", brand names) and semantic matches. Running both keyword and vector search in one engine gives good hybrid results without new infrastructure.

## 🔴 यह क्यों बना? (Hindi)
कई कंपनियों के पास logs या product search के लिए Elasticsearch पहले से है। Users को exact keyword (HS code "8518.30", brand names) और semantic matches दोनों चाहिए। एक ही engine में दोनों चलाने से नई infrastructure नहीं लगती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create an index with mapping: dense_vector (dims, index:true, similarity:cosine)
Step 2 → Index documents with text fields + the embedding array
Step 3 → ES builds an HNSW graph per segment for the vector field
Step 4 → Search with the "knn" option: field, query_vector, k, num_candidates, filter
Step 5 → Optionally add a "query" (BM25 match) in the same request -> scores combined
Step 6 → Read hits[]._score and _source; send top hits to the LLM
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → dense_vector (dims, index:true, similarity:cosine) mapping वाला index बनाओ
Step 2 → Text fields + embedding array के साथ documents index करो
Step 3 → ES हर segment में vector field के लिए HNSW graph बनाता है
Step 4 → "knn" option से search: field, query_vector, k, num_candidates, filter
Step 5 → चाहें तो उसी request में "query" (BM25 match) जोड़ो -> scores मिल जाते हैं
Step 6 → hits[]._score और _source पढ़ो; top hits LLM को भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a customs officer searches "8518.30" (exact code) one time and "noise cancelling earbuds" another time. BM25 handles the code, kNN handles the descriptive phrase, and one hybrid request serves both. Filters restrict `country: IN` and `effective_year >= 2024`.

**Amazon-style product search**: text match for brand ("Sony"), vector match for intent ("good for running"), plus facets (price ranges) from Elasticsearch aggregations.

## 🟡 Real Example Hindi mein
**Tariff System**: officer कभी "8518.30" (exact code) खोजता है, कभी "noise cancelling earbuds"। Code के लिए BM25 और phrase के लिए kNN काम करता है, एक hybrid request दोनों संभालती है। Filters `country: IN` और `effective_year >= 2024` लगाते हैं।

**Amazon-style product search**: brand ("Sony") के लिए text match, intent ("running के लिए अच्छा") के लिए vector match, और price ranges जैसे facets Elasticsearch aggregations से।

---

## 💻 Code Example — Basic
```python
# pip install elasticsearch   (v8 client)  | server: elasticsearch 8.x
from elasticsearch import Elasticsearch  # official client

es = Elasticsearch("http://localhost:9200")  # connect (add api_key=... for cloud)

es.options(ignore_status=400).indices.create(  # create index; ignore "already exists" (400)
    index="tariff",
    mappings={"properties": {
        "hs_code": {"type": "keyword"},  # exact match
        "description": {"type": "text"},  # BM25 text
        "country": {"type": "keyword"},  # filter field
        "embedding": {"type": "dense_vector", "dims": 3, "index": True, "similarity": "cosine"},
    }},
)

es.index(index="tariff", id="8518.30", document={  # add one document
    "hs_code": "8518.30", "description": "Headphones and earphones",
    "country": "IN", "embedding": [0.9, 0.1, 0.0],
}, refresh=True)  # refresh so it is searchable immediately (demo only)

res = es.search(  # kNN search
    index="tariff",
    knn={"field": "embedding", "query_vector": [0.8, 0.2, 0.0],
         "k": 3, "num_candidates": 50, "filter": {"term": {"country": "IN"}}},
    source=["hs_code", "description"],  # return only these fields
)
for h in res["hits"]["hits"]:  # iterate hits
    print(h["_id"], h["_score"], h["_source"])
```

## 💻 Code Example — Advanced
```python
# Production: async client, bulk indexing, hybrid (BM25 + kNN) request, error handling
import logging
from typing import Any, Iterable

from elasticsearch import ApiError, AsyncElasticsearch, ConnectionError as ESConnError
from elasticsearch.helpers import async_bulk

log = logging.getLogger("es_vec")


class TariffES:
    def __init__(self, url: str, api_key: str | None = None) -> None:
        self.es = AsyncElasticsearch(url, api_key=api_key, request_timeout=10, max_retries=2, retry_on_timeout=True)

    async def bulk_index(self, docs: Iterable[dict[str, Any]]) -> int:
        actions = ({"_index": "tariff", "_id": d["hs_code"], "_source": d} for d in docs)  # generator saves memory
        ok, _ = await async_bulk(self.es, actions, chunk_size=500, raise_on_error=False)  # batches of 500
        return ok

    async def hybrid(self, text: str, vec: list[float], country: str = "IN", k: int = 5) -> list[dict[str, Any]]:
        try:
            res = await self.es.search(
                index="tariff",
                query={"bool": {  # BM25 part
                    "must": [{"match": {"description": {"query": text, "boost": 0.3}}}],
                    "filter": [{"term": {"country": country}}],
                }},
                knn={"field": "embedding", "query_vector": vec, "k": k, "num_candidates": k * 20,
                     "filter": [{"term": {"country": country}}], "boost": 0.7},  # vector part
                size=k,
                source=["hs_code", "description"],
            )
        except ESConnError:
            log.exception("cannot reach Elasticsearch")
            raise
        except ApiError:
            log.exception("bad query or mapping")
            raise
        return [{"id": h["_id"], "score": h["_score"], **h["_source"]} for h in res["hits"]["hits"]]

    async def close(self) -> None:
        await self.es.close()  # close HTTP sessions
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

es_store = TariffES("http://localhost:9200")  # from Advanced example
oa = AsyncOpenAI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await es_store.close()  # clean shutdown


app = FastAPI(lifespan=lifespan)


class SearchIn(BaseModel):
    text: str
    country: str = "IN"


@app.post("/tariff/hybrid")
async def hybrid(body: SearchIn) -> dict:
    vec = (await oa.embeddings.create(model="text-embedding-3-small", input=body.text)).data[0].embedding
    return {"results": await es_store.hybrid(body.text, vec, body.country)}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings

vs = ElasticsearchStore(
    es_url="http://localhost:9200",
    index_name="tariff_lc",
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
)
vs.add_texts(["Headphones and earphones", "Smartphones"])
docs = vs.similarity_search("bluetooth earbuds", k=3, filter=[{"term": {"metadata.country.keyword": "IN"}}])
# wrap vs.as_retriever() as a LangGraph retrieve node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong `dims` or forgetting `index: true`
```python
# Wrong: dims=1536 but embeddings have 3072 -> indexing error; index False -> only slow script_score scan
{"embedding": {"type": "dense_vector", "dims": 1536}}
# Right
{"embedding": {"type": "dense_vector", "dims": 1536, "index": True, "similarity": "cosine"}}
```

❌ Mistake 2: Tiny `num_candidates`
```python
# Wrong: k=10, num_candidates=10 -> misses neighbours per shard
knn = {"k": 10, "num_candidates": 10}
# Right: num_candidates at least 10x k (more for many shards)
knn = {"k": 10, "num_candidates": 100}
```

---

## 🧠 Tricky Interview Question

**Q**: "Hybrid results look strange: BM25 scores are around 12 while kNN scores are between 0 and 1, so keyword hits always win. What do you do?"

**Answer**: Scores from different scorers are not on the same scale. Use `boost` to weight them, normalise scores, or better use Reciprocal Rank Fusion (RRF), which merges by rank instead of raw score and is available in Elasticsearch's retriever API. RRF avoids hand-tuned weights and is robust when score distributions differ.

---

## ⚫ Interview Questions + Answers

Q1: Which field type stores embeddings?
A1: `dense_vector`.

Q2: What does `index: true` do for it?
A2: Builds an HNSW structure so `knn` search is approximate and fast; without it you can only brute-force with `script_score`.

Q3: kNN `k` vs `num_candidates`?
A3: `k` is results returned; `num_candidates` is candidates examined per shard. Larger values improve recall at higher cost.

Q4: Why choose Elasticsearch for vectors?
A4: Hybrid keyword plus vector search, rich filters, aggregations, and mature operations when it is already deployed.

Q5: How do you reduce memory for large vector indices?
A5: Use quantized index types (`int8_hnsw`, `int4_hnsw`, or binary quantization in newer versions), lower dimensions, fewer shards or replicas, and keep vectors out of `_source` using `excludes` in mappings.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need hybrid keyword + semantic search and already operate Elasticsearch/OpenSearch
- Faceting and complex filters matter

❌ Avoid when:
- You only need simple vector lookup (lighter stores are cheaper)
- Cluster tuning skills are missing (JVM heap, shards)

---

## 📊 Visual Diagram
```
 user query "8518.30 earbuds"
        │
   ┌────┴─────────────┐
   ▼                  ▼
 BM25 match        kNN (HNSW)
 (keyword)         (embedding)
   │                  │
   └──── combine (boost / RRF) ────┐
                                    ▼
                         ranked hits ──► LLM context
```

---

## 💰 Cost Impact
- Embedding tokens: same as any store. Hybrid search can reach good quality with a smaller k, which lowers LLM prompt tokens (for example top 3 instead of top 8 saves about 1,000 input tokens per request).
- Infra: Elasticsearch is memory-hungry. Quantization can reduce vector RAM several times with small recall loss. Use hot/warm tiers and delete unused indices.
- Cache frequent queries at the API layer.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| dense_vector | Field type for embeddings | Embedding का field type |
| num_candidates | Candidates per shard | प्रति shard candidates |
| BM25 | Keyword ranking function | Keyword ranking |
| RRF | Reciprocal Rank Fusion merge | Rank से मिलाने की विधि |
| Shard | Piece of an index | Index का हिस्सा |
| Quantization | Compress vectors | Vectors को compress करना |

---

## ⚡ 3-Line Summary
English: Elasticsearch stores embeddings in `dense_vector` and runs HNSW kNN beside BM25. It is ideal for hybrid search with filters. Tune `num_candidates`, merge scores with RRF, and consider quantization.
Hindi: Elasticsearch `dense_vector` में embeddings रखकर BM25 के साथ HNSW kNN चलाता है। Filters के साथ hybrid search के लिए बढ़िया है। `num_candidates` tune करो, scores RRF से मिलाओ, और quantization सोचो।

---

## ➡️ Next Topic
**150. Choosing Right Vector DB** — a decision framework across all the options so far.
