---

# 148. MongoDB Atlas Vector Search
# हिंदी में: MongoDB Atlas Vector Search

---

## 🔵 Simple Definition (English)
Atlas Vector Search lets you store embeddings as arrays inside MongoDB documents and query them with the `$vectorSearch` aggregation stage. The vector sits next to the rest of the JSON document, so you keep one flexible data model.

## 🔵 सरल परिभाषा (Hindi)
Atlas Vector Search में embeddings MongoDB documents के अंदर arrays की तरह रहते हैं और `$vectorSearch` aggregation stage से query होते हैं। Vector बाकी JSON document के साथ रहता है, इसलिए एक ही flexible data model मिलता है।

---

## 🔴 Problem it Solves
Product catalogs and tariff records are often nested, changing JSON. Forcing them into fixed columns and a second vector store is painful. With Atlas the document, its metadata and its vector are one record.

## 🔴 यह क्यों बना? (Hindi)
Product catalogs और tariff records अक्सर nested, बदलते JSON होते हैं। इन्हें fixed columns और अलग vector store में डालना कठिन है। Atlas में document, metadata और vector एक ही record हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use an Atlas cluster (M10+ or free tier supports vector search)
Step 2 → Store documents with an "embedding": [floats] array field
Step 3 → Create an Atlas Vector Search index (type "vectorSearch") with numDimensions,
         similarity (cosine / euclidean / dotProduct), and filter fields
Step 4 → Query with aggregate([{ "$vectorSearch": {index, path, queryVector, numCandidates, limit, filter}}])
Step 5 → Project the fields you need plus {"$meta": "vectorSearchScore"}
Step 6 → Post-process results (rerank, send to LLM)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Atlas cluster use करो (M10+ या free tier में vector search है)
Step 2 → Documents में "embedding": [floats] array field रखो
Step 3 → numDimensions, similarity (cosine / euclidean / dotProduct) और filter fields के साथ
         Atlas Vector Search index (type "vectorSearch") बनाओ
Step 4 → aggregate([{ "$vectorSearch": {index, path, queryVector, numCandidates, limit, filter}}]) चलाओ
Step 5 → ज़रूरी fields और {"$meta": "vectorSearchScore"} project करो
Step 6 → Results post-process करो (rerank, LLM को भेजो)
```

---

## 🟡 Real World Example
**Tariff Classification System**: each document is `{hs_code, description, notes: [...], country, rulings: [{year, text}], embedding}`. Nested rulings stay inside the document. A query filters `country: "IN"` and returns the top 5 with their rulings in a single call.

**Amazon AI**: product documents have variable attributes per category (shoes have sizes, laptops have RAM). A flexible schema avoids hundreds of sparse columns.

## 🟡 Real Example Hindi mein
**Tariff System**: हर document `{hs_code, description, notes, country, rulings, embedding}` है। Nested rulings document के अंदर रहती हैं। Query `country: "IN"` filter करके top 5 और उनकी rulings एक ही call में लौटाती है।

**Amazon AI**: हर category के product में अलग attributes होते हैं (shoes में size, laptops में RAM)। Flexible schema से सैकड़ों sparse columns नहीं बनानी पड़तीं।

---

## 💻 Code Example — Basic
```python
# pip install pymongo
from pymongo import MongoClient  # sync driver
from pymongo.operations import SearchIndexModel  # for creating the vector index

client = MongoClient("mongodb+srv://USER:PASS@cluster0.example.mongodb.net")  # your Atlas URI
col = client["tariff_db"]["codes"]  # database.collection

col.insert_one({  # one document with its embedding (3 dims for demo)
    "hs_code": "8518.30",
    "description": "Headphones and earphones",
    "country": "IN",
    "embedding": [0.9, 0.1, 0.0],
})

index = SearchIndexModel(  # define the vector index
    name="tariff_vec",
    type="vectorSearch",
    definition={
        "fields": [
            {"type": "vector", "path": "embedding", "numDimensions": 3, "similarity": "cosine"},
            {"type": "filter", "path": "country"},  # fields usable in $vectorSearch filter
        ]
    },
)
col.create_search_index(model=index)  # index builds asynchronously; wait until READY

pipeline = [
    {"$vectorSearch": {
        "index": "tariff_vec",  # index name
        "path": "embedding",  # field with vectors
        "queryVector": [0.8, 0.2, 0.0],  # embedded query
        "numCandidates": 100,  # ANN candidates (10-20x limit is typical)
        "limit": 3,  # results to return
        "filter": {"country": "IN"},  # pre-filter
    }},
    {"$project": {"_id": 0, "hs_code": 1, "description": 1,
                  "score": {"$meta": "vectorSearchScore"}}},  # similarity score
]
for doc in col.aggregate(pipeline):  # run it
    print(doc)
```

## 💻 Code Example — Advanced
```python
# Production: async Motor/PyMongo-async, typed results, error handling
import logging
from typing import Any, TypedDict

from motor.motor_asyncio import AsyncIOMotorClient  # pip install motor
from pymongo.errors import OperationFailure, PyMongoError

log = logging.getLogger("atlas_vs")


class Hit(TypedDict):
    hs_code: str
    description: str
    score: float


class AtlasTariffStore:
    def __init__(self, uri: str) -> None:
        self.col = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)["tariff_db"]["codes"]  # fail fast

    async def search(self, vec: list[float], country: str = "IN", k: int = 5) -> list[Hit]:
        pipeline: list[dict[str, Any]] = [
            {"$vectorSearch": {
                "index": "tariff_vec", "path": "embedding", "queryVector": vec,
                "numCandidates": max(50, k * 20), "limit": k, "filter": {"country": country},
            }},
            {"$project": {"_id": 0, "hs_code": 1, "description": 1,
                          "score": {"$meta": "vectorSearchScore"}}},
        ]
        try:
            return await self.col.aggregate(pipeline).to_list(length=k)  # async cursor -> list
        except OperationFailure:
            log.exception("index missing or filter field not indexed")  # common config errors
            raise
        except PyMongoError:
            log.exception("mongo error")
            raise

    async def upsert(self, hs_code: str, description: str, vec: list[float], country: str = "IN") -> None:
        await self.col.update_one(  # idempotent write
            {"hs_code": hs_code, "country": country},
            {"$set": {"description": description, "embedding": vec}},
            upsert=True,
        )
```

---

## 🟠 FastAPI Integration
```python
import os
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pymongo.errors import PyMongoError

app = FastAPI()
store = AtlasTariffStore(os.environ["MONGODB_URI"])  # from Advanced example
client = AsyncOpenAI()


class Q(BaseModel):
    text: str
    country: str = "IN"


@app.post("/tariff/search")
async def search(q: Q) -> dict:
    emb = (await client.embeddings.create(model="text-embedding-3-small", input=q.text)).data[0].embedding
    try:
        hits = await store.search(emb, q.country)
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="vector store unavailable") from exc
    return {"results": hits}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-mongodb
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

vs = MongoDBAtlasVectorSearch.from_connection_string(
    "mongodb+srv://USER:PASS@cluster0.example.mongodb.net",
    namespace="tariff_db.codes",  # db.collection
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name="tariff_vec",
)
retriever = vs.as_retriever(search_kwargs={"k": 5, "pre_filter": {"country": {"$eq": "IN"}}})
# use `retriever` as a node in LCEL chains or a LangGraph retrieve step
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filtering on a field that is not declared as a `filter` in the index
```python
# Wrong: index only has the vector field -> "Path 'country' needs to be indexed as token" error
# Right: add {"type": "filter", "path": "country"} to the index definition, then rebuild
```

❌ Mistake 2: `numCandidates` equal to `limit`
```python
# Wrong: poor recall
{"$vectorSearch": {"numCandidates": 5, "limit": 5}}
# Right: numCandidates about 10-20x limit
{"$vectorSearch": {"numCandidates": 100, "limit": 5}}
```

---

## 🧠 Tricky Interview Question

**Q**: "You inserted documents but `$vectorSearch` returns nothing, with no error. Why?"

**Answer**: Atlas Search indexes are built asynchronously, so a new index (or freshly added documents) may not be searchable yet, and status must be `READY`. Other causes: wrong index name or `path`, a vector length that differs from `numDimensions` (such documents are skipped), or a filter that matches nothing. Check `list_search_indexes()`, document vector lengths, and try without a filter.

---

## ⚫ Interview Questions + Answers

Q1: Which stage performs vector search?
A1: `$vectorSearch` in an aggregation pipeline (it must be the first stage).

Q2: Which similarity functions exist?
A2: `cosine`, `euclidean` and `dotProduct`.

Q3: What is `numCandidates`?
A3: How many approximate neighbours the engine examines before returning `limit` results. Higher means better recall and more latency.

Q4: How is it different from pgvector?
A4: Documents are flexible JSON, vector indexing runs in the separate Atlas Search process (`mongot`) with eventual consistency, and scaling uses dedicated search nodes. pgvector offers SQL joins and transactional consistency.

Q5: How do you keep embeddings in sync when text changes?
A5: Use a change stream or an ingestion service: on update, re-embed only if the text hash changed, then `$set` the new vector. Atlas also offers automated embedding for some tiers, but explicit control with a content hash is portable and cheap.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your system of record is already MongoDB with nested, evolving documents
- You want managed ops and combined text plus vector search

❌ Avoid when:
- You need strong relational joins and transactions across tables
- You run self-hosted community MongoDB without Atlas Search

---

## 📊 Visual Diagram
```
 {                                  aggregate([
  hs_code: "8518.30",                 { $vectorSearch: {
  country: "IN",       ──index──►       index, path:"embedding",
  rulings: [ {...} ],  (mongot)         queryVector, numCandidates,
  embedding: [0.9,...]                  limit, filter } },
 }                                    { $project: {score: vectorSearchScore} }
                                    ])  ──► top-k documents with nested data
```

---

## 💰 Cost Impact
- Embedding tokens are the same as elsewhere (one-time per document plus a few tokens per query).
- Atlas bills by cluster tier and search nodes; vector indexes use RAM, so large dimensions cost more. Use `dimensions=512/768` or quantization options where available.
- Keep documents slim: do not store huge text blobs next to vectors if you only need the snippet; return only projected fields to cut LLM prompt tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $vectorSearch | Aggregation stage for ANN search | ANN search stage |
| numCandidates | ANN candidates examined | जाँचे गए candidates |
| Filter field | Field allowed in pre-filter | Pre-filter वाला field |
| mongot | Atlas Search engine process | Atlas Search engine |
| Document model | Flexible JSON records | लचीला JSON record |

---

## ⚡ 3-Line Summary
English: Atlas stores vectors inside documents and searches them with `$vectorSearch`. Declare filter fields in the index and set `numCandidates` well above `limit`. Indexing is asynchronous, so check index status.
Hindi: Atlas documents के अंदर vectors रखता है और `$vectorSearch` से search करता है। Index में filter fields declare करो और `numCandidates` को `limit` से काफी बड़ा रखो। Indexing asynchronous है, इसलिए status देखो।

---

## ➡️ Next Topic
**149. Elasticsearch Vector Search** — dense_vector, kNN search and combining it with BM25.
