---

# 393. chromadb
# हिंदी में: chromadb (open-source vector database)

---

## 🔵 Simple Definition (English)
ChromaDB is an open-source vector database. You store text with its embedding vector and metadata, then search by meaning: give a query and it returns the nearest documents. It runs in memory, on disk, or as a server.

## 🔵 सरल परिभाषा (Hindi)
ChromaDB एक open-source vector database है। आप text को उसके embedding vector और metadata के साथ रखते हैं, फिर अर्थ (meaning) से search करते हैं: query दीजिए और यह सबसे नज़दीकी documents लौटाता है। यह memory में, disk पर या server की तरह चल सकता है।

---

## 🔴 Problem it Solves
Normal databases match exact words (`LIKE '%refund%'`). A user who types "get my money back" will not find a document titled "Refund policy". Embeddings put similar meanings close together in vector space, and a vector database finds the nearest vectors quickly. Chroma gives this with a tiny API and no server setup, so it is the usual first choice for RAG prototypes.

## 🔴 यह क्यों बना? (Hindi)
साधारण database सिर्फ exact शब्द मिलाता है (`LIKE '%refund%'`)। जो user "get my money back" लिखता है उसे "Refund policy" वाला document नहीं मिलेगा। Embeddings मिलते-जुलते अर्थ को vector space में पास रखते हैं और vector database सबसे नज़दीकी vectors जल्दी ढूँढता है। Chroma यह बिना server setup के छोटे से API में देता है, इसलिए RAG prototype के लिए पहली पसंद है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a client (EphemeralClient / PersistentClient / HttpClient)
Step 2 → Create a collection and attach an embedding function and distance space
Step 3 → add(ids, documents, metadatas): Chroma embeds each document and stores it
Step 4 → query(query_texts, n_results, where): embed the query, find nearest vectors
Step 5 → Results return ids, documents, metadatas and distances (smaller = closer)
Step 6 → upsert / update / delete keep the collection in sync with your source data
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client बनाएँ (EphemeralClient / PersistentClient / HttpClient)
Step 2 → Collection बनाएँ और embedding function व distance space जोड़ें
Step 3 → add(ids, documents, metadatas): Chroma हर document को embed करके रखता है
Step 4 → query(query_texts, n_results, where): query को embed करके नज़दीकी vectors ढूँढता है
Step 5 → Result में ids, documents, metadatas और distances आते हैं (कम = ज़्यादा पास)
Step 6 → upsert / update / delete से collection को source data के साथ sync रखें
```

---

## 🟡 Real World Example
A company builds an internal HR bot. Policy PDFs are split into chunks, embedded and stored in Chroma with metadata like `{"dept": "hr", "year": 2026}`. When an employee asks "how many casual leaves do I get", the app queries Chroma with `where={"dept": "hr"}`, takes the top 3 chunks and sends them to the LLM as context. This is RAG (Retrieval-Augmented Generation).

## 🟡 Real Example Hindi mein
एक company internal HR bot बनाती है। Policy PDFs को chunks में बाँटकर embed करके Chroma में `{"dept": "hr", "year": 2026}` जैसे metadata के साथ रखा जाता है। कर्मचारी पूछता है "मुझे कितनी casual leaves मिलती हैं", तो app `where={"dept": "hr"}` के साथ Chroma से query करती है, top 3 chunks लेती है और उन्हें context बनाकर LLM को भेजती है। यही RAG है।

---

## 💻 Code Example — Basic
```python
# Basic Chroma usage (pip install chromadb). Uses a tiny local embedding so no model download is needed.
import hashlib  # to turn words into stable numbers
from typing import List  # type hints
import chromadb  # the vector database
from chromadb import Documents, EmbeddingFunction, Embeddings  # types for a custom embedder

DIM: int = 4096  # vector size of our toy embedder


class HashEmbed(EmbeddingFunction[Documents]):  # toy word-hash embedder (use a real model in production)
    def __init__(self) -> None:  # explicit init keeps Chroma happy
        pass  # nothing to configure

    def __call__(self, input: Documents) -> Embeddings:  # Chroma calls this with a list of texts
        out: List[List[float]] = []  # one vector per text
        for text in input:  # each document or query
            v: List[float] = [0.0] * DIM  # empty vector
            for word in text.lower().split():  # each word
                v[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1.0  # count it in a bucket
            out.append(v)  # store vector
        return out  # list of vectors


client = chromadb.EphemeralClient()  # in-memory client, data is lost when the process ends
col = client.get_or_create_collection(  # like a table
    "docs", embedding_function=HashEmbed(), configuration={"hnsw": {"space": "cosine"}}  # cosine distance
)
col.add(  # insert documents
    ids=["a", "b", "c"],  # unique string ids
    documents=["refund policy for razorpay payments", "biryani delivery time swiggy", "how to reset password"],  # texts
    metadatas=[{"src": "faq"}, {"src": "blog"}, {"src": "faq"}],  # filterable extras
)
print(col.count())  # how many items stored
# Output: 3

res = col.query(query_texts=["razorpay refund"], n_results=2, where={"src": "faq"})  # search only FAQ items
print(res["ids"], [round(x, 3) for x in res["distances"][0]])  # ids and distances (0 = identical)
# Output: [['a', 'c']] [0.368, 1.0]

res = col.query(query_texts=["swiggy biryani"], n_results=1)  # no filter
print(res["ids"], res["documents"])  # best match
# Output: [['b']] [['biryani delivery time swiggy']]

col.upsert(ids=["c"], documents=["reset your password via email"], metadatas=[{"src": "faq"}])  # insert or replace by id
print(col.get(ids=["c"])["documents"])  # fetch by id (no similarity)
# Output: ['reset your password via email']
col.delete(ids=["b"])  # remove by id
print(col.count())  # one less
# Output: 2
```

## 💻 Code Example — Advanced
```python
# Production style: persistent store, chunk ingestion, cleanup of stale data, typed search helper
import hashlib  # stable ids
import tempfile  # temp folder for the demo database
from typing import Any, Dict, List, Optional  # type hints
import chromadb  # vector DB
from chromadb import Documents, EmbeddingFunction, Embeddings  # embedder base types

DIM: int = 4096  # toy vector size


class HashEmbed(EmbeddingFunction[Documents]):  # replace with OpenAI / sentence-transformers in production
    def __init__(self) -> None:  # explicit init
        pass  # no state

    def __call__(self, input: Documents) -> Embeddings:  # embed a batch
        out: List[List[float]] = []  # result list
        for text in input:  # per text
            v: List[float] = [0.0] * DIM  # vector
            for w in text.lower().split():  # per word
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % DIM] += 1.0  # bucket count
            out.append(v)  # keep
        return out  # vectors


def chunk(text: str, size: int = 8) -> List[str]:  # split into small word windows
    words: List[str] = text.split()  # words
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]  # fixed-size chunks


class KnowledgeBase:  # small wrapper used by the app
    def __init__(self, path: str) -> None:  # path on disk
        self.client = chromadb.PersistentClient(path=path)  # saves to disk automatically
        self.col = self.client.get_or_create_collection("kb_docs", embedding_function=HashEmbed())  # collection

    def ingest(self, doc_id: str, text: str, meta: Dict[str, Any]) -> int:  # add a whole document
        self.col.delete(where={"doc_id": doc_id})  # remove old chunks of this doc (avoid duplicates)
        parts: List[str] = chunk(text)  # make chunks
        self.col.add(  # store chunks
            ids=[f"{doc_id}:{i}" for i in range(len(parts))],  # unique chunk ids
            documents=parts,  # chunk texts
            metadatas=[{**meta, "doc_id": doc_id, "chunk": i} for i in range(len(parts))],  # metadata per chunk
        )
        return len(parts)  # how many chunks

    def search(self, q: str, k: int = 2, where: Optional[Dict[str, Any]] = None) -> List[str]:  # semantic search
        n: int = max(1, min(k, self.col.count()))  # never ask for more than we have
        res = self.col.query(query_texts=[q], n_results=n, where=where)  # run query
        return res["documents"][0] if res["documents"] else []  # list of texts


path: str = tempfile.mkdtemp()  # demo folder
kb = KnowledgeBase(path)  # create
print(kb.ingest("leave", "casual leave is twelve days per year and sick leave is ten days per year", {"dept": "hr"}))  # 2 chunks
# Output: 2
print(kb.ingest("leave", "casual leave is twelve days per year", {"dept": "hr"}))  # re-ingest replaces old chunks
# Output: 1
kb.ingest("it", "reset your laptop password using self service", {"dept": "it"})  # another doc
print(kb.col.count())  # chunks in total
# Output: 2
print(kb.search("laptop password", k=1, where={"dept": "it"}))  # filtered search
# Output: ['reset your laptop password using self service']

del kb  # drop the first client
kb2 = KnowledgeBase(path)  # reopen the same folder
print(kb2.col.count())  # data survived
# Output: 2
```

---

## 🟠 JavaScript vs Python Comparison
Chroma also has a JavaScript client (`chromadb` on npm), but it talks to a Chroma server. Python can run embedded in the same process, which is why it is popular for quick prototypes.

```python
# Python (embedded, no server)
import chromadb  # import
col = chromadb.EphemeralClient().get_or_create_collection("t")  # local collection
col.add(ids=["1"], documents=["hello"], embeddings=[[0.1, 0.2]])  # add with your own vector
print(col.query(query_embeddings=[[0.1, 0.2]], n_results=1)["ids"])  # [['1']]
```
```javascript
// JavaScript (needs a running Chroma server: chroma run)
import { ChromaClient } from "chromadb";
const client = new ChromaClient({ path: "http://localhost:8000" });
const col = await client.getOrCreateCollection({ name: "t" });
await col.add({ ids: ["1"], documents: ["hello"], embeddings: [[0.1, 0.2]] });
const res = await col.query({ queryEmbeddings: [[0.1, 0.2]], nResults: 1 });
```

Key differences: Python has `EphemeralClient`, `PersistentClient`, `HttpClient`; JS uses the HTTP client only. Method names are snake_case in Python and camelCase in JS.

---

## 🟠 FastAPI Connection
A RAG API creates one Chroma client at startup (lifespan), then exposes `POST /ingest` and `GET /search`. Chroma calls are synchronous, so use plain `def` endpoints (FastAPI runs them in a thread pool) instead of `async def`.

```python
# FastAPI + Chroma search endpoint (pip install fastapi httpx chromadb)
import hashlib  # toy embedder
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator, Dict, List  # type hints
import chromadb  # vector db
from chromadb import Documents, EmbeddingFunction, Embeddings  # embedder types
from fastapi import FastAPI, Query  # app and query validation
from fastapi.testclient import TestClient  # in-process testing


class HashEmbed(EmbeddingFunction[Documents]):  # toy embedder
    def __init__(self) -> None:  # explicit init
        pass  # nothing

    def __call__(self, input: Documents) -> Embeddings:  # batch embed
        out: List[List[float]] = []  # vectors
        for t in input:  # each text
            v: List[float] = [0.0] * 4096  # empty vector
            for w in t.lower().split():  # each word
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 4096] += 1.0  # count
            out.append(v)  # keep
        return out  # done


@asynccontextmanager  # lifespan: create once per process
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.col = chromadb.EphemeralClient().get_or_create_collection("api", embedding_function=HashEmbed())  # collection
    yield  # serve requests


app: FastAPI = FastAPI(lifespan=lifespan)  # attach


@app.post("/ingest")  # plain def -> runs in thread pool
def ingest(doc_id: str, text: str) -> Dict[str, str]:  # simple demo signature
    app.state.col.upsert(ids=[doc_id], documents=[text])  # idempotent write
    return {"status": "ok"}  # response


@app.get("/search")  # search endpoint
def search(q: str = Query(min_length=2), k: int = Query(1, ge=1, le=5)) -> Dict[str, List[str]]:  # validated params
    n: int = min(k, app.state.col.count()) or 1  # safe n_results
    res = app.state.col.query(query_texts=[q], n_results=n)  # query
    return {"results": res["documents"][0]}  # list of texts


with TestClient(app) as c:  # runs lifespan
    c.post("/ingest", params={"doc_id": "1", "text": "refund policy razorpay"})  # add one
    c.post("/ingest", params={"doc_id": "2", "text": "biryani delivery time"})  # add two
    print(c.get("/search", params={"q": "razorpay refund"}).json())  # search
# Output: {'results': ['refund policy razorpay']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `EphemeralClient` and expecting data to persist
✅ Correct: use `PersistentClient(path=...)` (or a server) for real data

```python
# Wrong - data vanishes when the process exits
# client = chromadb.EphemeralClient()
# Right
# client = chromadb.PersistentClient(path="./chroma_data")
```

❌ Mistake 2: Mixing embedding models for the same collection
✅ Correct: one collection = one embedding model for both add and query

```python
# Wrong: add with model A (384 dim), query with model B (1536 dim) -> dimension error or garbage results
# Right: pass the same embedding_function every time you open the collection
```

❌ Mistake 3: `add` with an existing id, or asking `n_results` larger than the collection
✅ Correct: use `upsert` for idempotent writes; clamp `n_results`

```python
# Wrong: col.add(ids=["a"], ...) twice -> duplicate id is ignored/warned, old text stays
# Right: col.upsert(ids=["a"], documents=[new_text])
```

---

## 🧠 Tricky Interview Question

**Q**: Cosine distance in Chroma is `1 - cosine_similarity`. A query vector is `[1, 0]`. Which document is returned first?

```python
# doc1 = [2, 0]     doc2 = [0.9, 0.5]     doc3 = [-1, 0]
# collection space = "cosine", n_results = 1
```

**Answer**: `doc1`. Cosine only measures the angle. `[2, 0]` points the same way as `[1, 0]` so its similarity is 1.0 and its distance is 0.0, even though its length is different. `doc2` has distance about 0.13 and `doc3` has distance 2.0. With `l2` (Euclidean) space the answer would change because length matters there (distance from `[1, 0]` to `[2, 0]` is 1 and to `[0.9, 0.5]` about 0.51, so `doc2` wins).

---

## ⚫ Interview Questions + Answers

Q1: What is the default distance in Chroma?
A1: Squared L2 (`l2`). Set `cosine` or `ip` through the collection configuration for text embeddings that were trained for cosine similarity.

Q2: What does Chroma use for fast search?
A2: An HNSW (Hierarchical Navigable Small World) graph index for approximate nearest neighbours. It trades a small accuracy loss for large speed gains.

Q3: Chroma vs Pinecone vs FAISS?
A3: FAISS is a library (index only, no metadata or persistence layer). Pinecone is a managed cloud service. Chroma is an open-source database with metadata filters and simple persistence, good for prototypes and small to medium data.

Q4: How do you filter results?
A4: `where` filters on metadata (`{"dept": "hr"}`, operators like `$gt`, `$in`), and `where_document` filters on text (`{"$contains": "refund"}`).

Q5: How should I chunk documents?
A5: Split into 200 to 500 token pieces with a small overlap, keep the source id in metadata, and re-ingest by deleting old chunks first.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Building a RAG prototype or a small internal search tool
- You want zero setup (embedded mode) and metadata filters
- Data is up to a few million vectors

❌ Avoid when:
- You need multi-region, high availability and billions of vectors (use a managed or distributed vector DB)
- You only need pure in-memory similarity (FAISS or NumPy is enough)

---

## 📊 Visual Diagram

```
 documents ──► embedding model ──► vectors ──► [ Chroma collection ]
                                                  ids | vectors | docs | metadata
 query text ─► same model ─► query vector ─► HNSW nearest search + where filter
                                                  │
                          top-k docs + distances ◄┘ ──► LLM prompt (RAG)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Numbers that capture meaning | अर्थ को दर्शाने वाले numbers |
| Collection | A group of vectors, like a table | Vectors का समूह (table जैसा) |
| Metadata | Extra fields for filtering | Filter के लिए अतिरिक्त जानकारी |
| HNSW | Graph index for fast approximate search | तेज़ अनुमानित search का index |
| Distance | How far two vectors are | दो vectors के बीच दूरी |
| Upsert | Insert or update by id | id से जोड़ना या बदलना |

---

## ⚡ 3-Line Summary
English: Chroma stores text, embeddings and metadata and finds the nearest items for a query. Use PersistentClient for saved data, the same embedding function everywhere, and upsert for safe writes. It is a great fit for RAG prototypes.
Hindi: Chroma text, embeddings और metadata रखता है और query के सबसे नज़दीकी items ढूँढता है। Data बचाने के लिए PersistentClient, हर जगह वही embedding function और सुरक्षित writes के लिए upsert इस्तेमाल करें। RAG prototypes के लिए बढ़िया है।

---

## ➡️ Next Topic
**394. pinecone-client** — managed cloud vector database for production scale.
