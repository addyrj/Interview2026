---

# 132. Pinecone Index Setup
# हिंदी में: Pinecone Index Setup (index सही तरीके से बनाना)

---

## 🔵 Simple Definition (English)
Setting up a Pinecone index means choosing its name, `dimension` (must equal your embedding size), `metric` (cosine, dotproduct or euclidean) and `spec` (serverless cloud/region, or pod type). These choices are fixed at creation: dimension and metric cannot be changed later, so you must get them right the first time.

## 🔵 सरल परिभाषा (Hindi)
Pinecone index setup का मतलब है name, `dimension` (embedding size के बराबर), `metric` (cosine, dotproduct या euclidean) और `spec` (serverless cloud/region या pod type) चुनना। ये choices बनाते समय fix हो जाती हैं: dimension और metric बाद में नहीं बदल सकते, इसलिए पहली बार में सही चुनो।

---

## 🔴 Problem it Solves
Wrong setup is the most common Pinecone failure: dimension mismatch errors, poor ranking from the wrong metric, an index created in a far-away region (high latency), or duplicate index creation crashing deployment scripts. A repeatable, validated, idempotent setup avoids all of this.

## 🔴 यह क्यों बना? (Hindi)
गलत setup Pinecone की सबसे common समस्या है: dimension mismatch error, गलत metric से खराब ranking, दूर के region में index (ज़्यादा latency) और duplicate creation से deployment script crash। Validated और idempotent setup इन सब से बचाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the embedding model -> note its dimension (text-embedding-3-small = 1536)
Step 2 → Pick the metric the model expects (cosine for most text models)
Step 3 → Pick spec: ServerlessSpec(cloud="aws", region="us-east-1") close to your app servers
Step 4 → Check the index does not already exist (list_indexes().names())
Step 5 → create_index(name, dimension, metric, spec, deletion_protection="enabled" optional)
Step 6 → Wait until describe_index(name).status["ready"] is True
Step 7 → Get host/handle: pc.Index(name); verify with describe_index_stats()
Step 8 → Tag with model name/version (in the index name or metadata) for future migrations
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Embedding model तय करो -> उसका dimension देखो (text-embedding-3-small = 1536)
Step 2 → Model जो metric माँगता है वो चुनो (ज़्यादातर text models के लिए cosine)
Step 3 → Spec: app servers के पास का ServerlessSpec(cloud="aws", region="us-east-1")
Step 4 → देखो index पहले से मौजूद तो नहीं (list_indexes().names())
Step 5 → create_index(name, dimension, metric, spec, deletion_protection optional)
Step 6 → describe_index(name).status["ready"] True होने तक रुको
Step 7 → pc.Index(name) लो और describe_index_stats() से verify करो
Step 8 → Migration के लिए index name/metadata में model name/version रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: index name `tariff-hs-te3s-v1` encodes the model (`te3s` = text-embedding-3-small). Dimension 1536, metric cosine, serverless AWS `ap-south-1`-nearest supported region. When the team moves to `text-embedding-3-large` (3072 dims) they create `tariff-hs-te3l-v1`, re-embed, test on the golden set, switch the env var, then delete the old index. No downtime.

**Zomato AI**: separate indexes per use case (`dishes`, `restaurants`) because they use different embedding models and dimensions.

## 🟡 Real Example Hindi mein
**Tariff System**: Index name `tariff-hs-te3s-v1` में model (`te3s` = text-embedding-3-small) encode है। Dimension 1536, metric cosine, serverless AWS, सबसे पास का supported region। जब team `text-embedding-3-large` (3072 dims) पर जाती है तो नया `tariff-hs-te3l-v1` बनता है, re-embed, golden set पर test, env var बदलना, फिर पुराना delete। Downtime नहीं। **Zomato**: use case के हिसाब से अलग indexes (`dishes`, `restaurants`)।

---

## 💻 Code Example — Basic
```python
# Basic: validate an index config BEFORE calling Pinecone (pure Python, runs offline),
# then show the real create call (needs PINECONE_API_KEY, so it is guarded).
import os                                            # env access
from dataclasses import dataclass                    # config container
from typing import Dict                              # type hints

KNOWN_DIMS: Dict[str, int] = {                       # embedding model -> dimension
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}
METRICS = {"cosine", "dotproduct", "euclidean"}      # metrics Pinecone supports

@dataclass(frozen=True)
class IndexConfig:
    name: str                                        # lowercase letters, digits, hyphens
    model: str                                       # embedding model used
    metric: str = "cosine"                           # similarity metric
    cloud: str = "aws"                               # cloud provider
    region: str = "us-east-1"                        # serverless region

    def dimension(self) -> int:
        if self.model not in KNOWN_DIMS:             # unknown model -> fail early
            raise ValueError(f"unknown model {self.model}")
        return KNOWN_DIMS[self.model]                # exact size

    def validate(self) -> None:
        if self.metric not in METRICS:               # reject bad metric
            raise ValueError(f"metric must be one of {METRICS}")
        if not self.name.replace("-", "").isalnum() or self.name != self.name.lower():
            raise ValueError("index name: lowercase letters, digits and hyphens only")
        if len(self.name) > 45:                      # Pinecone limits name length
            raise ValueError("index name too long (max 45)")

cfg = IndexConfig(name="tariff-hs-te3s-v1", model="text-embedding-3-small")   # our setup
cfg.validate()                                       # raises on a bad config
print("OK:", cfg.name, "dim =", cfg.dimension(), "metric =", cfg.metric)

if os.getenv("PINECONE_API_KEY"):                    # only call the cloud when configured
    from pinecone import Pinecone, ServerlessSpec    # SDK
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])   # client
    if cfg.name not in pc.list_indexes().names():    # idempotent
        pc.create_index(name=cfg.name, dimension=cfg.dimension(), metric=cfg.metric,
                        spec=ServerlessSpec(cloud=cfg.cloud, region=cfg.region))
```

## 💻 Code Example — Advanced
```python
# Advanced: idempotent, verified index provisioning with readiness wait, dimension check,
# deletion protection, and an async variant. Safe to run on every deploy.
import asyncio                                           # async runtime
import logging                                           # logs
import time                                              # polling sleep
from typing import Any                                   # type hints

from pinecone import Pinecone, ServerlessSpec            # Pinecone SDK

log = logging.getLogger("provision")                     # logger

def ensure_index(pc: Pinecone, cfg: "IndexConfig", timeout_s: int = 120) -> Any:
    """Create the index if missing, verify settings if present, wait until ready, return handle."""
    cfg.validate()                                       # reuse validation from the basic example
    names = pc.list_indexes().names()                    # existing index names
    if cfg.name not in names:                            # create path
        log.info("creating index %s", cfg.name)
        try:
            pc.create_index(
                name=cfg.name, dimension=cfg.dimension(), metric=cfg.metric,
                spec=ServerlessSpec(cloud=cfg.cloud, region=cfg.region),
                deletion_protection="enabled",           # prevents accidental deletes in prod
            )
        except Exception as exc:                         # e.g. quota exceeded, race with another deploy
            if "already exists" not in str(exc).lower(): # a race is fine, anything else is not
                raise
    else:                                                # verify path: never trust an existing index blindly
        desc = pc.describe_index(cfg.name)               # read its configuration
        if desc.dimension != cfg.dimension() or desc.metric != cfg.metric:
            raise RuntimeError(f"index {cfg.name} exists with different dimension/metric")
    deadline = time.time() + timeout_s                   # readiness deadline
    while not pc.describe_index(cfg.name).status["ready"]:   # poll
        if time.time() > deadline:                       # do not hang forever
            raise TimeoutError(f"index {cfg.name} not ready after {timeout_s}s")
        time.sleep(2)                                    # polite polling
    return pc.Index(cfg.name)                            # data-plane handle

async def ensure_index_async(pc: Pinecone, cfg: "IndexConfig") -> Any:
    return await asyncio.to_thread(ensure_index, pc, cfg)   # run blocking SDK calls off the event loop

# Token usage: provisioning uses no LLM tokens and no read/write units.
```

---

## 🟠 FastAPI Integration
```python
import os                                              # env
from contextlib import asynccontextmanager             # lifespan handler
from fastapi import FastAPI                             # FastAPI
from pinecone import Pinecone                           # client

@asynccontextmanager
async def lifespan(app: FastAPI):                       # runs once at startup/shutdown
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])   # fail fast if the key is missing
    app.state.index = await ensure_index_async(pc, cfg)     # provision + keep handle
    yield                                               # app serves requests here

app = FastAPI(lifespan=lifespan)                        # attach lifespan

@app.get("/health/index")                               # health check route
async def index_health() -> dict:
    stats = app.state.index.describe_index_stats()      # vector counts per namespace
    return {"dimension": stats.dimension, "total": stats.total_vector_count}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings            # embeddings
from langchain_pinecone import PineconeVectorStore        # integration

emb = OpenAIEmbeddings(model=cfg.model)                   # SAME model as the index config
vs = PineconeVectorStore(index_name=cfg.name, embedding=emb)   # attaches to the existing index
# `PineconeVectorStore.from_documents(docs, emb, index_name=cfg.name)` also works to ingest.
# LangGraph: read cfg.name from graph config so each environment (dev/prod) uses its own index.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dimension does not match the model
✅ Correct: derive the dimension from the model, never type it by hand.

```python
# Wrong
pc.create_index(name="tariff", dimension=1024, metric="cosine", spec=spec)   # model gives 1536
# Right
pc.create_index(name="tariff", dimension=KNOWN_DIMS["text-embedding-3-small"], metric="cosine", spec=spec)
```

❌ Mistake 2: Creating the index on every app start without a check
✅ Correct: check existence first (or catch "already exists").

```python
# Wrong: crashes on the second deploy
pc.create_index(name=cfg.name, dimension=1536, metric="cosine", spec=spec)
# Right
if cfg.name not in pc.list_indexes().names():
    pc.create_index(name=cfg.name, dimension=1536, metric="cosine", spec=spec)
```

---

## 🧠 Tricky Interview Question

**Q**: "You chose `dotproduct` metric but your vectors are not normalised. Search results favour long, repetitive documents. Why, and what is the fix?"

**Answer**: Dot product multiplies magnitudes, so vectors with larger norms score higher regardless of direction. Fix: normalise vectors to unit length (then dot product equals cosine) or use `cosine`. You cannot change the metric of an existing index, so create a new index with the correct metric, re-upsert and swap. Also note that `dotproduct` is required for Pinecone hybrid (sparse + dense) search, so in that case normalise or weight vectors yourself.

---

## ⚫ Interview Questions + Answers

Q1: What are the required arguments to create a Pinecone index?
A1: `name`, `dimension`, `metric` (defaults to cosine) and `spec` (ServerlessSpec or PodSpec).

Q2: Can you change an index's dimension later?
A2: No. You must create a new index with the new dimension, re-embed and re-upsert your data.

Q3: How do you pick the metric?
A3: Use the one the embedding model was trained for. OpenAI and most sentence-transformers models work well with cosine (equivalently dot product on unit vectors). Euclidean is used for some image/geo embeddings.

Q4: How do you make index creation safe in CI/CD?
A4: Idempotent provisioning: list names, create only if missing, verify dimension/metric if existing, wait for readiness, enable deletion protection in production, and keep names versioned.

Q5: How do you migrate an index to a new embedding model with zero downtime?
A5: Create a new versioned index, backfill by re-embedding all source documents (batch, rate limited), dual-write new documents to both indexes during the migration, evaluate retrieval quality on a golden set against the new index, switch the app's index name via config/feature flag, keep the old index for rollback for a few days, then delete it. Never mix vectors from two models in one index.

---

## 🔷 When to Use + When Not to Use
✅ Use a separate index when:
- Embedding model or dimension differs
- Different environments (dev, staging, prod)
- Different metrics are needed

❌ Do not create many indexes when:
- You only need tenant or data-type separation (use namespaces and metadata instead)

---

## 📊 Visual Diagram
```
 embedding model ──► dimension (1536) ─┐
 model docs      ──► metric (cosine)  ─┼─► create_index(name, dim, metric, spec)
 app region      ──► ServerlessSpec   ─┘            │
                                                     ▼
                                          status.ready? ──no──► wait/poll
                                                     │ yes
                                                     ▼
                                       pc.Index(name) ──► describe_index_stats()
```

---

## 💰 Cost Impact
- Creating an empty serverless index is free; you pay for stored data and read/write units. A pod-based index bills hourly even when idle.
- Wrong setup is expensive: re-embedding 1M chunks x 300 tokens with text-embedding-3-small costs ~$6 plus engineering time, and a mistaken high dimension doubles storage (3072 vs 1536 dims = 2x).
- Optimise: choose the smallest dimension that meets recall (text-embedding-3 supports `dimensions=512/1024`), one index with namespaces instead of many indexes, and delete test indexes.
- No LLM tokens are used by setup itself.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dimension | Length of each vector | Vector की लंबाई |
| Metric | Similarity measure (cosine, dotproduct, euclidean) | Similarity नापने का तरीका |
| ServerlessSpec | Cloud + region config for serverless | Serverless का cloud/region config |
| Idempotent | Safe to run many times | बार-बार चलाना सुरक्षित |
| Deletion protection | Blocks accidental delete | गलती से delete रोकना |
| Readiness | Index finished provisioning | Index तैयार होना |
| Host | Index endpoint URL | Index का endpoint |

---

## ⚡ 3-Line Summary
English: Create indexes with the exact dimension and metric your embedding model needs; they cannot be changed later. Provision idempotently, wait for readiness and version index names. Use namespaces, not extra indexes, for tenants.
Hindi: Index को embedding model के सही dimension और metric के साथ बनाओ; ये बाद में नहीं बदलते। Idempotent provisioning करो, readiness का इंतज़ार करो और index names version करो। Tenants के लिए extra indexes नहीं, namespaces use करो।

---

## ➡️ Next Topic
**133. Pinecone Upsert + Query** — writing vectors in batches and querying them with top-k and scores.
