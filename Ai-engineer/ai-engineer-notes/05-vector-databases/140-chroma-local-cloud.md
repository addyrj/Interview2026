---

# 140. Chroma — Local + Cloud
# हिंदी में: Chroma — Local + Cloud (चलाने के अलग-अलग modes)

---

## 🔵 Simple Definition (English)
Chroma can run in four ways: **in-memory** (`EphemeralClient`/`Client`, lost on exit), **local persistent** (`PersistentClient(path)`, saved to disk, one process), **client-server** (run `chroma run --path ./db` and connect with `HttpClient`, many apps share it), and **Chroma Cloud** (managed service via `CloudClient`). Your collection code stays the same; only the client changes.

## 🔵 सरल परिभाषा (Hindi)
Chroma चार तरीकों से चल सकता है: **in-memory** (`EphemeralClient`/`Client`, exit पर data खत्म), **local persistent** (`PersistentClient(path)`, disk पर save, एक process), **client-server** (`chroma run --path ./db` चलाओ और `HttpClient` से connect करो, कई apps share करते हैं) और **Chroma Cloud** (`CloudClient` से managed service)। Collection वाला code वही रहता है; सिर्फ़ client बदलता है।

---

## 🔴 Problem it Solves
A prototype on a laptop (embedded mode) breaks when you deploy it: multiple API workers cannot safely share a `PersistentClient` folder, containers lose in-memory data, and there is no backup or scaling. Understanding the modes lets you move from notebook to server to cloud without rewriting the application.

## 🔴 यह क्यों बना? (Hindi)
Laptop पर चलने वाला prototype (embedded mode) deploy करते ही टूटता है: कई API workers एक `PersistentClient` folder सुरक्षित रूप से share नहीं कर सकते, containers में in-memory data खो जाता है, और backup या scaling नहीं होती। Modes समझने से notebook से server और cloud तक application दोबारा लिखे बिना जा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Mode 1 (memory)    : client = chromadb.EphemeralClient()                    -> tests, notebooks
Mode 2 (local disk): client = chromadb.PersistentClient(path="./chroma")    -> single-process apps
Mode 3 (server)    : shell: chroma run --path ./chroma_data --port 8000
                     client = chromadb.HttpClient(host="localhost", port=8000)  -> multi-worker apps
Mode 4 (cloud)     : client = chromadb.CloudClient(tenant=..., database=..., api_key=...)  -> managed
Step 5 → Pick the mode from configuration (env var), not hard-coded
Step 6 → Collections, add, query, where filters are IDENTICAL in all modes
Step 7 → Migrate data between modes: read from old (col.get(include=[...])) -> upsert into new in batches
Step 8 → Back up: copy the persist folder (stop writes first) or snapshot the server volume
```

## 🟢 कैसे काम करता है? (Hindi)

```
Mode 1 (memory)    : client = chromadb.EphemeralClient()                    -> tests, notebooks
Mode 2 (local disk): client = chromadb.PersistentClient(path="./chroma")    -> single-process apps
Mode 3 (server)    : shell: chroma run --path ./chroma_data --port 8000
                     client = chromadb.HttpClient(host="localhost", port=8000)  -> multi-worker apps
Mode 4 (cloud)     : client = chromadb.CloudClient(tenant=..., database=..., api_key=...)  -> managed
Step 5 → Mode को configuration (env var) से चुनो, hard-code मत करो
Step 6 → Collections, add, query, where filters सभी modes में एक जैसे हैं
Step 7 → Modes के बीच data migrate: पुराने से col.get(include=[...]) पढ़ो -> नए में batches में upsert
Step 8 → Backup: persist folder copy करो (पहले writes रोको) या server volume का snapshot लो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dev laptops use `EphemeralClient` in pytest (fast, isolated). The staging environment uses a Docker Compose service running `chroma run` with a mounted volume, and 4 Uvicorn workers connect with `HttpClient`. Production, after the team grows, moves to Chroma Cloud (or Qdrant/Pinecone) with the same repository class because mode selection comes from `CHROMA_MODE`.

**Zomato AI**: data scientists explore in notebooks with `PersistentClient`; the same collection is later exported to the shared server.

## 🟡 Real Example Hindi mein
**Tariff System**: Dev laptops पर pytest में `EphemeralClient` (तेज़, isolated)। Staging में Docker Compose service `chroma run` चलाती है, volume mounted है, और 4 Uvicorn workers `HttpClient` से connect होते हैं। Team बढ़ने पर production Chroma Cloud (या Qdrant/Pinecone) पर जाता है, वही repository class चलती है क्योंकि mode `CHROMA_MODE` से चुना जाता है। **Zomato**: Data scientists notebooks में `PersistentClient` से explore करते हैं; वही collection बाद में shared server में export होती है।

---

## 💻 Code Example — Basic
```python
# Basic: choose the Chroma mode from an environment variable. The selection logic is pure Python
# so it runs offline; chromadb is only imported when a client is actually built.
import os                                                    # read env vars
from typing import Any, Dict                                 # type hints

def describe_mode(env: Dict[str, str]) -> str:
    """Pure function: decide which mode the config asks for (easy to unit test)."""
    mode = env.get("CHROMA_MODE", "memory").lower()          # default: in-memory
    if mode not in {"memory", "persistent", "server", "cloud"}:
        raise ValueError(f"unknown CHROMA_MODE: {mode}")     # fail early with a clear message
    if mode == "cloud" and not env.get("CHROMA_API_KEY"):    # cloud needs credentials
        raise ValueError("cloud mode requires CHROMA_API_KEY")
    return mode

def make_client(env: Dict[str, str]) -> Any:
    import chromadb                                          # lazy import (heavy package)
    mode = describe_mode(env)                                # validate first
    if mode == "memory":
        return chromadb.EphemeralClient()                    # in-memory
    if mode == "persistent":
        return chromadb.PersistentClient(path=env.get("CHROMA_PATH", "./chroma"))
    if mode == "server":
        return chromadb.HttpClient(host=env.get("CHROMA_HOST", "localhost"), port=int(env.get("CHROMA_PORT", "8000")))
    return chromadb.CloudClient(                             # managed Chroma Cloud (check your chromadb version)
        tenant=env["CHROMA_TENANT"], database=env["CHROMA_DATABASE"], api_key=env["CHROMA_API_KEY"])

for cfg in ({}, {"CHROMA_MODE": "server"}, {"CHROMA_MODE": "persistent"}):   # demo configs
    print(cfg, "->", describe_mode(cfg))                     # shows the decision
try:
    describe_mode({"CHROMA_MODE": "cloud"})                  # missing key
except ValueError as exc:
    print("error:", exc)                                     # clear config error
# With chromadb installed: client = make_client(dict(os.environ)); col = client.get_or_create_collection("tariff")
```

## 💻 Code Example — Advanced
```python
# Advanced: migrate a collection between Chroma modes in batches, with verification and async support.
import asyncio                                               # async runtime
import logging                                               # logs
from typing import Any, Dict, Iterator, List                 # type hints

log = logging.getLogger("chroma-migrate")                    # logger

def read_batches(src: Any, batch: int = 500) -> Iterator[Dict[str, List[Any]]]:
    """Yield pages of items from a source collection using limit/offset."""
    total = src.count()                                      # number of items
    for offset in range(0, total, batch):
        yield src.get(limit=batch, offset=offset, include=["documents", "metadatas", "embeddings"])

def migrate(src_col: Any, dst_col: Any, batch: int = 500) -> int:
    """Copy src -> dst idempotently (upsert), then verify the counts."""
    copied = 0
    for page in read_batches(src_col, batch):
        if not page["ids"]:                                  # empty page: nothing to do
            continue
        try:
            dst_col.upsert(ids=page["ids"], documents=page["documents"],
                           metadatas=page["metadatas"], embeddings=page["embeddings"])   # keep the SAME vectors
        except Exception as exc:                             # surface which batch failed
            log.error("batch failed at id %s: %s", page["ids"][0], exc)
            raise
        copied += len(page["ids"])
    if dst_col.count() < src_col.count():                    # verify (destination may hold more if reused)
        raise RuntimeError(f"verification failed: dst={dst_col.count()} src={src_col.count()}")
    return copied

async def migrate_async(src_col: Any, dst_col: Any) -> int:
    return await asyncio.to_thread(migrate, src_col, dst_col)    # off the event loop

def spot_check(src_col: Any, dst_col: Any, probe_vec: List[float], k: int = 3) -> bool:
    """Same query should return the same ids in both collections (identical vectors and metric)."""
    a = src_col.query(query_embeddings=[probe_vec], n_results=k)["ids"][0]
    b = dst_col.query(query_embeddings=[probe_vec], n_results=k)["ids"][0]
    return a == b                                            # ANN may differ slightly; compare overlap in practice

# Token usage: migration re-uses stored embeddings, so it costs 0 embedding tokens. Re-embedding would.
```

---

## 🟠 FastAPI Integration
```python
import os                                                    # env
from contextlib import asynccontextmanager                   # lifespan
from fastapi import FastAPI, HTTPException                    # FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = make_client(dict(os.environ))                    # mode chosen by CHROMA_MODE
    app.state.col = client.get_or_create_collection("tariff", metadata={"hnsw:space": "cosine"})
    yield                                                      # serve requests

app = FastAPI(lifespan=lifespan)                               # app

@app.get("/health/chroma")                                     # health check
async def health() -> dict:
    try:
        return {"mode": os.getenv("CHROMA_MODE", "memory"), "items": app.state.col.count()}
    except Exception as exc:                                   # server down etc.
        raise HTTPException(503, f"chroma unreachable: {exc}")
# Rule: with several uvicorn workers, do NOT use PersistentClient (each process opens the same files).
# Use server mode: `uvicorn app:app --workers 4` + HttpClient to one Chroma server.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_chroma import Chroma                          # integration
from langchain_openai import OpenAIEmbeddings                 # embeddings
import chromadb                                               # client types

emb = OpenAIEmbeddings(model="text-embedding-3-small")
# LangChain accepts either a path (persistent) or a ready-made client (server / cloud):
local = Chroma(collection_name="tariff", embedding_function=emb, persist_directory="./chroma")
remote = Chroma(collection_name="tariff", embedding_function=emb,
                client=chromadb.HttpClient(host="localhost", port=8000))     # shared server
retriever = remote.as_retriever(search_kwargs={"k": 4})       # the retriever API is identical
# LangGraph: choose local/remote in the graph's config so the same graph runs in tests and production.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sharing one `PersistentClient` folder across multiple workers/containers
✅ Correct: run a Chroma server and use `HttpClient`.

```python
# Wrong: 4 uvicorn workers each open ./chroma -> locking/corruption risk
client = chromadb.PersistentClient(path="./chroma")
# Right
client = chromadb.HttpClient(host="chroma", port=8000)
```

❌ Mistake 2: Running the Chroma server container without a volume
✅ Correct: mount a persistent volume.

```python
# Wrong (docker): docker run -p 8000:8000 chromadb/chroma         -> data gone on restart
# Right (docker): docker run -p 8000:8000 -v chroma_data:/data chromadb/chroma   # check image docs for the data path
```

❌ Mistake 3: Hard-coding mode and secrets in code
✅ Correct: environment variables / secret manager.

---

## 🧠 Tricky Interview Question

**Q**: "Your RAG API works with one Uvicorn worker but returns stale or missing data with four workers when using `PersistentClient`. Why?"

**Answer**: Each worker is a separate process with its own in-process Chroma instance (its own HNSW index in memory) pointing at the same files. Writes made by one process are not visible to the others' in-memory indexes, and concurrent access to the same SQLite/index files is unsafe. Solution: run Chroma as a server (one writer process) and connect all workers via `HttpClient`, or switch to a database built for multi-writer access (Qdrant, pgvector, Pinecone). Also keep ingestion as a separate job rather than inside web workers.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `Client()` and `PersistentClient()`?
A1: `Client()` (ephemeral) keeps everything in memory and loses it on exit; `PersistentClient(path)` saves to disk and reloads on restart.

Q2: How do you run Chroma as a server?
A2: `chroma run --path ./chroma_data --port 8000` (or the Docker image), then `chromadb.HttpClient(host=..., port=...)`.

Q3: Does the collection API change between modes?
A3: No. `get_or_create_collection`, `add`, `upsert`, `query`, `get`, `delete` are the same; only client creation differs.

Q4: How do you secure a Chroma server?
A4: Keep it on a private network behind a reverse proxy with TLS and authentication, restrict ports, never expose it to the public internet unauthenticated, and use token auth/headers supported by your version, or use Chroma Cloud's API keys.

Q5: Plan a path from prototype to production on Chroma.
A5: Start with `PersistentClient` behind a repository interface. Add a golden-set evaluation. Before multiple workers, switch to server mode with a mounted volume and backups (volume snapshots), and move ingestion to a background job. Monitor latency and memory; if you need replication, SLAs or scale beyond one machine, choose Chroma Cloud or migrate to another database by copying ids, documents, metadata and embeddings in batches (no re-embedding) and validating with the golden set and spot-check queries before cutover.

---

## 🔷 When to Use + When Not to Use
✅ Use by mode:
- Ephemeral: tests, notebooks
- Persistent: single-process tools, desktop apps, small internal apps
- Server: small multi-worker deployments
- Cloud: managed convenience for teams

❌ Avoid when:
- You need high availability across regions or very large scale self-managed (consider other databases)

---

## 📊 Visual Diagram
```
 Mode 1  EphemeralClient ──► RAM (lost on exit)
 Mode 2  PersistentClient ─► ./chroma  (one process only)
 Mode 3  uvicorn worker 1 ─┐
         uvicorn worker 2 ─┼─ HttpClient ─► Chroma server ─► volume /data
         uvicorn worker 3 ─┘
 Mode 4  your app ─ CloudClient(api_key) ─► Chroma Cloud (managed)

 Same collection API everywhere:  col.add(...)  col.query(...)  col.get(...)
```

---

## 💰 Cost Impact
- Local/persistent/server: $0 license; pay for the VM (RAM grows with vector count: ~dim x 4 bytes x N plus index overhead, so 1M x 1536 is about 6 GB plus overhead).
- Chroma Cloud: usage-based pricing (check current docs).
- Embedding cost is unchanged by mode (OpenAI text-embedding-3-small $0.02 per 1M tokens). Migrating with stored embeddings costs $0; re-embedding 1M x 300-token chunks costs ~$6.
- Operational cost: backups, monitoring and on-call for self-hosting versus paying the managed fee. Small teams often choose managed sooner than they expect.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EphemeralClient | In-memory client | Memory वाला client |
| PersistentClient | Disk-backed local client | Disk वाला local client |
| HttpClient | Client talking to a Chroma server | Chroma server से बात करने वाला client |
| CloudClient | Client for Chroma Cloud | Chroma Cloud का client |
| Tenant / database | Cloud organisation scopes | Cloud में organisation के scopes |
| Volume | Persistent storage for containers | Containers का स्थायी storage |
| Migration | Moving data between stores | Data को एक store से दूसरे में ले जाना |

---

## ⚡ 3-Line Summary
English: Chroma runs in memory, on local disk, as a server, or in the cloud, with the same collection API. Use server mode (HttpClient) when several workers share data, mount a volume, and choose the mode from configuration. Migrate by copying stored embeddings in batches.
Hindi: Chroma memory, local disk, server या cloud में चलता है, collection API वही रहती है। कई workers के साथ server mode (HttpClient) use करो, volume mount करो और mode configuration से चुनो। Stored embeddings को batches में copy करके migrate करो।

---

## ➡️ Next Topic
**141. FAISS — Complete Guide** — Meta's high-performance similarity search library: flat, IVF, HNSW and PQ indexes.
