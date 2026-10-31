---

# 114. Embedding Cost Optimization — Complete Guide
# हिंदी में: Embedding Cost Optimization — पूरी Guide

---

## 🔵 Simple Definition (English)
Embedding cost optimization means getting the same retrieval quality while paying less: fewer tokens embedded, no repeated work, cheaper models, smaller vectors, and cheaper batch pricing. Embedding APIs bill only for input tokens, so every token you avoid sending is money saved.

## 🔵 सरल परिभाषा (Hindi)
Embedding cost optimization का मतलब है retrieval quality वही रखते हुए कम खर्च करना: कम tokens embed करना, दोहराया हुआ काम नहीं, सस्ते models, छोटे vectors, और सस्ती batch pricing। Embedding APIs सिर्फ input tokens का bill बनाती हैं, इसलिए जो token आप नहीं भेजते वो पैसा बचता है।

---

## 🔴 Problem it Solves
Embedding looks cheap per call ($0.02 per 1M tokens) but costs grow with: re-embedding unchanged documents on each sync, embedding boilerplate (headers, footers, legal text), embedding every user query repeatedly, and model migrations that re-embed everything. Plus hidden costs: vector DB RAM and search compute scale with dimension and count.

## 🔴 यह क्यों बना? (Hindi)
Embedding प्रति call सस्ता दिखता है ($0.02 प्रति 1M tokens) पर cost बढ़ती है: हर sync में unchanged documents दोबारा embed करना, boilerplate (header, footer, legal text) embed करना, हर user query बार-बार embed करना, और model migration में सब कुछ फिर embed करना। साथ ही छिपी cost: vector DB की RAM और search compute।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: log tokens per job, per day, per source
Step 2 → Deduplicate: hash(text) -> skip texts already embedded
Step 3 → Clean: strip boilerplate, HTML, repeated headers before embedding
Step 4 → Chunk smartly: right-size chunks (no giant overlaps)
Step 5 → Incremental updates: embed only new/changed documents
Step 6 → Choose the cheapest model that passes your recall target
Step 7 → Reduce vector size (dimensions=512, int8) to cut DB cost
Step 8 → Use batch pricing (OpenAI Batch API, 50% off) for non-urgent jobs
Step 9 → Cache query embeddings (see topic 115)
Step 10 → Re-measure and set budget alerts
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले नापो: job, दिन, source के हिसाब से tokens log करो
Step 2 → Dedupe: hash(text) से पहले embed हुए texts skip करो
Step 3 → Clean: embed से पहले boilerplate, HTML, repeated headers हटाओ
Step 4 → Chunk सही size का रखो (बहुत ज़्यादा overlap नहीं)
Step 5 → Incremental update: सिर्फ new/changed documents embed करो
Step 6 → सबसे सस्ता model चुनो जो recall target पूरा करे
Step 7 → Vector size घटाओ (dimensions=512, int8)
Step 8 → Non-urgent jobs के लिए Batch API (50% सस्ता)
Step 9 → Query embeddings cache करो (topic 115)
Step 10 → फिर नापो और budget alerts लगाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The nightly sync used to re-embed all 400,000 tariff notes (about 120M tokens, $2.40 with small, plus hours of time). After adding content hashing, only the 2,000 changed notes are embedded. Stripping repeated "Chapter header" boilerplate removed 18% of tokens. Moving to `dimensions=512` cut the vector DB size by two thirds.

**Amazon-style**: Product descriptions with 40% identical manufacturer text; dedupe at paragraph level.

## 🟡 Real Example Hindi mein
**Tariff System**: Nightly sync पहले सभी 4,00,000 tariff notes (लगभग 12 करोड़ tokens) दोबारा embed करता था। Content hashing के बाद सिर्फ बदले हुए 2,000 notes embed होते हैं। बार-बार आने वाले "Chapter header" हटाने से 18% tokens कम हुए। `dimensions=512` से vector DB का size दो-तिहाई घटा।

**Amazon-style**: Product descriptions में 40% manufacturer text एक जैसा होता है; paragraph level पर dedupe करो।

---

## 💻 Code Example — Basic
```python
# Cost estimator + hash-based dedupe (pure Python, runs offline)
import hashlib
from dataclasses import dataclass

PRICE_PER_M = {"small": 0.02, "large": 0.13, "ada": 0.10}   # USD per 1M tokens


def rough_tokens(text: str) -> int:
    """Approximate token count (about 4 characters per token for English)."""
    return max(1, len(text) // 4)


def sha(text: str) -> str:
    """Stable fingerprint of a text."""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


@dataclass
class Plan:
    unique: int
    skipped: int
    tokens: int
    cost: float


def plan(texts: list[str], already: set[str], model: str = "small", batch_discount: float = 1.0) -> Plan:
    """Count only texts that are new; apply optional batch discount (0.5)."""
    seen = set(already)
    new: list[str] = []
    for t in texts:
        h = sha(t)
        if h in seen:                            # duplicate or already stored
            continue
        seen.add(h)
        new.append(t)
    tokens = sum(rough_tokens(t) for t in new)
    cost = tokens * PRICE_PER_M[model] / 1_000_000 * batch_discount
    return Plan(len(new), len(texts) - len(new), tokens, round(cost, 6))


texts = ["Headphones", "Headphones", "headphones ", "Coffee beans"] * 1000
print("naive tokens:", sum(rough_tokens(t) for t in texts))   # pays for every duplicate
print("dedupe:", plan(texts, set()))
print("batch :", plan(texts, set(), batch_discount=0.5))
```

## 💻 Code Example — Advanced
```python
# Incremental embedding pipeline: hash store + dedupe + batching + cost report
import asyncio
import hashlib
import sqlite3
from openai import AsyncOpenAI

client = AsyncOpenAI()
MODEL, PRICE = "text-embedding-3-small", 0.02 / 1_000_000


class Store:
    """SQLite table of hash -> vector (as JSON text) so we never pay twice."""

    def __init__(self, path: str = "emb_cache.db") -> None:
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS emb(h TEXT PRIMARY KEY, model TEXT, v TEXT)")

    def get_many(self, hashes: list[str]) -> dict[str, str]:
        q = ",".join("?" * len(hashes))
        rows = self.db.execute(f"SELECT h, v FROM emb WHERE model=? AND h IN ({q})", [MODEL, *hashes])
        return dict(rows.fetchall())

    def put_many(self, items: dict[str, str]) -> None:
        self.db.executemany("INSERT OR REPLACE INTO emb VALUES(?,?,?)",
                            [(h, MODEL, v) for h, v in items.items()])
        self.db.commit()


async def embed_incremental(texts: list[str], store: Store) -> tuple[dict[str, str], float]:
    """Embed only unseen texts; return hash->vector map and USD spent."""
    import json
    by_hash = {hashlib.sha256(t.encode()).hexdigest(): t for t in texts}   # dedupe
    cached = store.get_many(list(by_hash)) if by_hash else {}
    todo = [h for h in by_hash if h not in cached]
    spent = 0.0
    for i in range(0, len(todo), 500):           # batches of 500
        part = todo[i:i + 500]
        try:
            r = await client.embeddings.create(model=MODEL, input=[by_hash[h] for h in part])
        except Exception as exc:
            raise RuntimeError(f"embedding failed: {exc}") from exc
        spent += r.usage.total_tokens * PRICE
        store.put_many({h: json.dumps(d.embedding) for h, d in zip(part, r.data)})
    return {**cached, **store.get_many(todo)}, spent


if __name__ == "__main__":
    out, usd = asyncio.run(embed_incremental(["Headphones", "Headphones", "Coffee"], Store()))
    print(len(out), "unique vectors, spent $", round(usd, 8))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
PRICE = {"text-embedding-3-small": 0.02, "text-embedding-3-large": 0.13}


class EstimateReq(BaseModel):
    documents: int = Field(gt=0)
    avg_tokens: int = Field(gt=0)
    model: str = "text-embedding-3-small"
    duplicate_rate: float = Field(default=0.0, ge=0, le=0.99)
    use_batch_api: bool = False


@app.post("/embedding/estimate")
async def estimate(r: EstimateReq) -> dict[str, float]:
    tokens = r.documents * (1 - r.duplicate_rate) * r.avg_tokens   # after dedupe
    usd = tokens * PRICE.get(r.model, 0.02) / 1_000_000
    if r.use_batch_api:
        usd *= 0.5                                                  # batch discount
    return {"tokens": tokens, "usd": round(usd, 4)}
```
Expose this to product managers and add it to CI as a budget gate.

---

## 🔗 LangChain / LangGraph Connection
LangChain provides `CacheBackedEmbeddings` (hash-based caching) and `RecordManager` for incremental indexing, which skip unchanged documents.

```python
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings

base = OpenAIEmbeddings(model="text-embedding-3-small")
store = LocalFileStore("./emb_cache")
cached = CacheBackedEmbeddings.from_bytes_store(base, store, namespace=base.model)  # namespace = model name
vectors = cached.embed_documents(["Headphones", "Headphones"])   # second one is free
```
In LangGraph ingestion graphs, put the "dedupe/hash filter" node before the "embed" node.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Full re-index on every run
✅ Correct: Hash content and embed only changes.

```python
# Wrong
vectors = embed(all_docs)                     # pays every night
# Right
vectors = embed([d for d in all_docs if sha(d) not in known])
```

❌ Mistake 2: Cache key without the model name
✅ Correct: Key = hash + model (+ dimensions). Otherwise stale vectors from an old model leak in.

❌ Mistake 3: Optimising price but never measuring recall
✅ Correct: Every cost cut must be validated on the eval set.

---

## 🧠 Tricky Interview Question

**Q**: "Embedding bill is only $50 a month, yet finance says the retrieval system is expensive. Where is the money?"

**Answer**: Embedding API cost is the small part. Vector DB memory (dimensions x count x replicas), LLM generation tokens for retrieved context, rerankers, and engineering time dominate. Fix by reducing dimensions/quantising, retrieving fewer but better chunks (rerank), caching answers, and using smaller LLMs for simple queries.

---

## ⚫ Interview Questions + Answers

Q1: Are embedding output tokens billed?
A1: No. Only input tokens.

Q2: What is the simplest big saving?
A2: Do not re-embed unchanged text (content hash cache).

Q3: How does the Batch API help?
A3: Asynchronous jobs complete within 24 hours at 50% lower price, ideal for backfills.

Q4: How do dimensions affect cost?
A4: Not the API price, but vector DB storage/RAM and query speed.

Q5: Plan a migration from ada-002 to text-embedding-3-small for 200M tokens.
A5: Cost is 200M x $0.02/1M = $4 (or $2 via Batch). The real work: build a parallel index, run both on an eval set, dual-read during rollout, then switch and delete the old index. Store model names in metadata; keep rollback until metrics are stable.

---

## 🔷 When to Use + When Not to Use
✅ Optimise when:
- Corpus is large or refreshed often
- Query volume is high
- Vector DB bill is significant

❌ Don't over-engineer when:
- Total spend is a few dollars; engineering time costs more
- You are prototyping

---

## 📊 Visual Diagram
```
 raw docs ─► clean ─► dedupe(hash) ─► changed only ─► batch ─► embed API
                         │                                  (50% via Batch API)
                         └─► cache hit -> $0
 vectors ─► dimensions=512 / int8 ─► smaller DB bill
```

---

## 💰 Cost Impact
Example: 400k notes x 300 tokens = 120M tokens. Full nightly re-embed with small: $2.40/night (about $72/month). Incremental (0.5% change): $0.012/night. With large: $15.60 vs $0.08. Batch API halves both. Vector storage: 400k x 1536 x 4 B = 2.3 GB vs 400k x 512 x 4 B = 0.8 GB. Always include the vector DB and LLM costs in the total.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dedupe | Remove duplicates | Duplicates हटाना |
| Content hash | Fingerprint of text | Text का fingerprint |
| Incremental indexing | Embed only changes | सिर्फ बदलाव embed करना |
| Batch API | Cheaper async API | सस्ता async API |
| Quantisation | Lower-precision storage | कम precision storage |
| Budget alert | Spend warning | Spend की चेतावनी |

---

## ⚡ 3-Line Summary
English: Embedding cost falls with dedupe, caching, incremental updates, cheaper models, smaller vectors, and the Batch API. Measure tokens first and validate recall after each cut. The vector DB and LLM often cost more than embedding calls.
Hindi: Dedupe, caching, incremental updates, सस्ते models, छोटे vectors और Batch API से embedding cost घटती है। पहले tokens नापो और हर कटौती के बाद recall जाँचो। Vector DB और LLM की cost अक्सर embedding calls से ज़्यादा होती है।

---

## ➡️ Next Topic
**115. Embedding Caching** - implement the cache layer in detail (memory, Redis, disk) with correct keys and invalidation.
