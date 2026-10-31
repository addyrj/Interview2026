---

# 139. Chroma DB — Complete Guide
# हिंदी में: Chroma DB — पूरी Guide

---

## 🔵 Simple Definition (English)
Chroma is an open-source, developer-friendly vector database that runs inside your Python process (or as a server). You create a **collection**, `add` documents with ids and metadata, and `query` by text or vector. It can embed text for you with a default embedding function, or you can pass your own embeddings. It is the fastest way to build a RAG prototype.

## 🔵 सरल परिभाषा (Hindi)
Chroma एक open-source, developer-friendly vector database है जो आपके Python process के अंदर (या server के रूप में) चलता है। आप **collection** बनाते हैं, ids और metadata के साथ documents `add` करते हैं और text या vector से `query` करते हैं। यह default embedding function से text खुद embed कर सकता है, या आप अपने embeddings दे सकते हैं। RAG prototype बनाने का सबसे तेज़ तरीका।

---

## 🔴 Problem it Solves
Setting up Pinecone/Weaviate/Qdrant just to try an idea means accounts, Docker and config. FAISS has no metadata or persistence. Chroma needs `pip install chromadb` and three lines of code, stores documents + metadata + vectors together, persists to disk, and uses HNSW under the hood.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ idea try करने के लिए Pinecone/Weaviate/Qdrant का setup मतलब accounts, Docker और config। FAISS में metadata या persistence नहीं। Chroma के लिए बस `pip install chromadb` और तीन lines; यह documents + metadata + vectors साथ रखता है, disk पर persist करता है और अंदर HNSW use करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install chromadb
Step 2 → client = chromadb.Client()                      (in-memory)  or  PersistentClient(path="./chroma")
Step 3 → col = client.get_or_create_collection("tariff", metadata={"hnsw:space": "cosine"})
Step 4 → col.add(ids=[...], documents=[...], metadatas=[...], embeddings=[...] optional)
Step 5 → If embeddings are omitted, Chroma's embedding function creates them (default: a small local ONNX model)
Step 6 → col.query(query_texts=[...] or query_embeddings=[...], n_results=5, where={...})
Step 7 → Result is a dict of lists-of-lists: ids, documents, metadatas, distances (one inner list per query)
Step 8 → col.update / col.upsert / col.delete(ids=...) / col.count()
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install chromadb
Step 2 → client = chromadb.Client()  (in-memory)  या  PersistentClient(path="./chroma")
Step 3 → col = client.get_or_create_collection("tariff", metadata={"hnsw:space": "cosine"})
Step 4 → col.add(ids=[...], documents=[...], metadatas=[...], embeddings=[...] optional)
Step 5 → Embeddings न दो तो Chroma का embedding function बनाता है (default: छोटा local ONNX model)
Step 6 → col.query(query_texts=[...] या query_embeddings=[...], n_results=5, where={...})
Step 7 → Result lists-of-lists का dict: ids, documents, metadatas, distances (हर query के लिए एक inner list)
Step 8 → col.update / col.upsert / col.delete(ids=...) / col.count()
```

---

## 🟡 Real World Example
**Tariff Classification System**: during the prototype phase, the team loads 5,000 HS heading descriptions into a local `PersistentClient("./chroma_tariff")`. In two days they have a working RAG demo for the customs team, with metadata filters on `country` and `chapter`. Later, when traffic grows, they migrate to Qdrant/Pinecone behind the same repository interface.

**Zomato AI**: an intern builds a "dish recommender" demo with Chroma on a laptop to show the idea before engineering invests in infrastructure.

## 🟡 Real Example Hindi mein
**Tariff System**: Prototype phase में team 5,000 HS heading descriptions को local `PersistentClient("./chroma_tariff")` में load करती है। दो दिन में customs team के लिए RAG demo तैयार, `country` और `chapter` filters के साथ। Traffic बढ़ने पर वही repository interface रखकर Qdrant/Pinecone पर migrate। **Zomato**: Intern laptop पर Chroma से "dish recommender" demo बनाता है ताकि engineering infrastructure में पैसा लगाने से पहले idea दिखाया जा सके।

---

## 💻 Code Example — Basic
```python
# Basic: Chroma in-memory collection with our own embeddings (pip install chromadb).
# We pass embeddings ourselves so nothing is downloaded and no API key is needed.
import chromadb                                              # the library

client = chromadb.Client()                                   # in-memory client (data lost when process ends)
col = client.get_or_create_collection(                       # create or reuse the collection
    name="tariff_demo",
    metadata={"hnsw:space": "cosine"},                       # use cosine distance (default is l2)
)

col.add(                                                     # insert documents
    ids=["8518.30", "6205", "8517.13"],                      # unique string ids
    documents=["Headphones and earphones", "Men's shirts", "Smartphones"],   # the raw text
    metadatas=[{"country": "IN", "chapter": 85}, {"country": "IN", "chapter": 62}, {"country": "IN", "chapter": 85}],
    embeddings=[[0.9, 0.1, 0.0], [0.0, 0.1, 0.9], [0.8, 0.3, 0.1]],   # toy 3-D vectors
)

res = col.query(                                             # similarity search
    query_embeddings=[[1.0, 0.0, 0.1]],                      # one query vector (list of queries)
    n_results=2,                                             # top 2
    where={"chapter": 85},                                   # metadata filter
    include=["documents", "metadatas", "distances"],         # what to return
)
for doc, dist in zip(res["documents"][0], res["distances"][0]):   # [0] = results of the first query
    print(round(dist, 3), doc)                               # smaller cosine distance = closer
print("count:", col.count())                                 # number of stored items
```

## 💻 Code Example — Advanced
```python
# Advanced: persistent Chroma repository: idempotent upsert, typed results, filter builder,
# error handling, and async wrapper (Chroma's local client is synchronous).
import asyncio                                               # async runtime
import logging                                               # logs
from typing import Any, Dict, List, Optional                 # type hints

import chromadb                                              # library
from chromadb.api.models.Collection import Collection        # type of a collection

log = logging.getLogger("chroma-repo")                       # logger

class ChromaRepo:
    def __init__(self, path: str = "./chroma_tariff", name: str = "tariff", model_tag: str = "te3s") -> None:
        self.client = chromadb.PersistentClient(path=path)   # data persisted to disk
        self.col: Collection = self.client.get_or_create_collection(
            name=f"{name}_{model_tag}",                      # model tag in the name avoids mixing embeddings
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, ids: List[str], texts: List[str], vectors: List[List[float]], metas: List[Dict[str, Any]]) -> int:
        if not (len(ids) == len(texts) == len(vectors) == len(metas)):   # all lists must align
            raise ValueError("ids, texts, vectors and metas must have equal length")
        try:
            self.col.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metas)   # idempotent write
        except Exception as exc:                             # e.g. dimension mismatch with existing data
            log.error("chroma upsert failed: %s", exc)
            raise
        return len(ids)

    @staticmethod
    def build_where(country: Optional[str], chapters: Optional[List[int]]) -> Optional[Dict[str, Any]]:
        clauses: List[Dict[str, Any]] = []
        if country:
            clauses.append({"country": {"$eq": country}})
        if chapters:
            clauses.append({"chapter": {"$in": chapters}})
        if not clauses:
            return None                                      # Chroma rejects an empty where dict
        return clauses[0] if len(clauses) == 1 else {"$and": clauses}   # $and needs 2+ clauses

    def search(self, vec: List[float], k: int = 5, country: Optional[str] = None,
               chapters: Optional[List[int]] = None, max_distance: float = 0.6) -> List[Dict[str, Any]]:
        res = self.col.query(query_embeddings=[vec], n_results=k, where=self.build_where(country, chapters),
                             include=["documents", "metadatas", "distances"])
        out: List[Dict[str, Any]] = []
        for i, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
            if dist <= max_distance:                         # drop far matches (cosine distance = 1 - similarity)
                out.append({"id": i, "text": doc, "distance": dist, **meta})
        return out

    async def search_async(self, *a: Any, **kw: Any) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.search, *a, **kw)   # do not block the event loop

# Token usage: with your own embeddings, Chroma uses 0 tokens. With an OpenAI embedding function you pay
# ~300 tokens per chunk at embedding time and ~20 tokens per query.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException                  # FastAPI
from openai import AsyncOpenAI                                # embeddings

app = FastAPI()                                               # app
oai = AsyncOpenAI()                                           # client
repo = ChromaRepo()                                           # opened once per process

@app.get("/headings/search")                                  # route
async def search(q: str, country: str | None = None, k: int = 5) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)   # query embedding
    try:
        hits = await repo.search_async(emb.data[0].embedding, k=k, country=country)
    except Exception as exc:                                  # Chroma errors
        raise HTTPException(500, f"chroma error: {exc}")
    return {"hits": hits}
# Note: a PersistentClient is single-process. For several API workers use Chroma server mode (see note 140).
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-chroma
from langchain_chroma import Chroma                          # integration package
from langchain_openai import OpenAIEmbeddings                 # embeddings

vs = Chroma(
    collection_name="tariff_lc",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_lc",                          # saved to disk
    collection_metadata={"hnsw:space": "cosine"},
)
vs.add_texts(["Headphones and earphones"], metadatas=[{"country": "IN"}], ids=["8518.30"])
docs = vs.similarity_search("wireless earbuds", k=3, filter={"country": "IN"})   # Chroma `where` syntax
retriever = vs.as_retriever(search_kwargs={"k": 3})          # plug into LCEL / LangGraph retrieve node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `chromadb.Client()` and expecting data to persist
✅ Correct: use `PersistentClient(path=...)`.

```python
# Wrong: everything disappears on restart
client = chromadb.Client()
# Right
client = chromadb.PersistentClient(path="./chroma_tariff")
```

❌ Mistake 2: Forgetting the default distance is squared L2, not cosine
✅ Correct: set `metadata={"hnsw:space": "cosine"}` when creating the collection (it cannot be changed later).

```python
# Wrong: distances are L2 and thresholds like 0.3 mean something else
col = client.get_or_create_collection("tariff")
# Right
col = client.get_or_create_collection("tariff", metadata={"hnsw:space": "cosine"})
```

❌ Mistake 3: Switching embedding model on an existing collection (dimension error or garbage results)
✅ Correct: new collection per embedding model.

---

## 🧠 Tricky Interview Question

**Q**: "You ask Chroma for `n_results=5` with a `where` filter and get an error or fewer results. Why?"

**Answer**: Several possibilities: `n_results` larger than the number of matching/stored items (older versions raised a warning or error; new ones return fewer); an empty `where={}` is invalid; combining several conditions requires `$and`/`$or` instead of putting two keys in the same dict; metadata values must be str/int/float/bool (no lists or nested dicts); and stored embeddings with a different dimension than the query fail. Also, results are lists-of-lists: `res["documents"][0]` is the first query's list, a common indexing bug.

---

## ⚫ Interview Questions + Answers

Q1: What is a Chroma collection?
A1: A named group of embeddings, documents and metadata with one embedding function and distance setting, like a table.

Q2: How do you persist Chroma data?
A2: Use `chromadb.PersistentClient(path=...)`, or run Chroma as a server and use `HttpClient`.

Q3: What does Chroma do if you do not pass embeddings?
A3: It calls the collection's embedding function (default: a small local sentence-transformer model via ONNX) to embed `documents` and `query_texts`. You can set OpenAI or other embedding functions.

Q4: How do you filter?
A4: `where={"country": "IN"}` for metadata, `where_document={"$contains": "phone"}` for text content, with `$and`, `$or`, `$in`, `$gt`, etc.

Q5: When should you outgrow Chroma, and how do you prepare?
A5: Outgrow it when you need many API workers writing concurrently, multi-million vectors with high QPS, replication/SLAs, or advanced features such as hybrid search and multi-tenant isolation. Prepare by hiding Chroma behind a repository interface, keeping source documents and ids in your own store, versioning collections by embedding model, and measuring recall on a golden set so you can compare against the next database during migration.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prototypes, notebooks, demos, small apps (up to roughly a few hundred thousand vectors)
- Local development and unit tests

❌ Avoid when:
- Heavy concurrent production traffic with strict SLAs
- You need horizontal scaling, replication, or advanced hybrid search (consider Qdrant, Weaviate, Pinecone, pgvector)

---

## 📊 Visual Diagram
```
 Python process
 ┌──────────────────────────────────────────────┐
 │ chromadb.PersistentClient("./chroma_tariff") │
 │   Collection "tariff_te3s" (cosine)          │
 │    ids | documents | metadatas | embeddings  │
 │    HNSW index  +  SQLite metadata store      │
 └──────────────────────────────────────────────┘
   add/upsert ─►  query(embeddings, where) ─► {ids, documents, metadatas, distances}
```

---

## 💰 Cost Impact
- Chroma itself is free (open-source). Costs are your machine's RAM/disk and, if you use an API embedding function, embedding tokens.
- Default local embedding model = $0 but lower quality than top API models; OpenAI text-embedding-3-small = $0.02 per 1M tokens (1M chunks x 300 tokens = $6 one-off).
- Cheap prototype loop: no server bill. The migration cost later is mostly re-indexing (re-embedding only if you change models).
- LLM savings come from retrieving only ~4 relevant chunks (~1,200 tokens) instead of whole files.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | Group of documents + embeddings | Documents + embeddings का group |
| PersistentClient | Disk-backed local client | Disk पर save करने वाला client |
| HttpClient | Client for Chroma server | Chroma server का client |
| where | Metadata filter | Metadata filter |
| n_results | Number of matches | Matches की संख्या |
| Embedding function | Turns text into vectors | Text को vectors में बदलने वाला function |
| hnsw:space | Distance metric setting | Distance metric setting |

---

## ⚡ 3-Line Summary
English: Chroma is the easiest vector database: create a collection, add documents with metadata, query with filters. Use PersistentClient for disk storage and set cosine distance at creation. Great for prototypes; plan to migrate for heavy production use.
Hindi: Chroma सबसे आसान vector database है: collection बनाओ, metadata के साथ documents add करो, filters के साथ query करो। Disk storage के लिए PersistentClient और बनाते समय cosine distance set करो। Prototypes के लिए बढ़िया; भारी production के लिए migrate की योजना रखो।

---

## ➡️ Next Topic
**140. Chroma — Local + Cloud** — in-memory, persistent, server (HttpClient) and Chroma Cloud modes compared.
