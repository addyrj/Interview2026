---

# 123. Embedding Drift — Complete Guide
# हिंदी में: Embedding Drift — पूरी Guide

---

## 🔵 Simple Definition (English)
Embedding drift is when retrieval quality quietly gets worse over time because something changed: the data (new products, new vocabulary), the user queries (new topics), or the embedding model itself (a provider updates or deprecates it, or you switch versions). Vectors from old and new states no longer line up.

## 🔵 सरल परिभाषा (Hindi)
Embedding drift तब होती है जब कुछ बदलने की वजह से retrieval quality चुपचाप गिरती है: data बदला (नए products, नई शब्दावली), user queries बदलीं (नए topics), या embedding model खुद बदला (provider update/deprecate करे, या आप version बदलें)। पुराने और नए vectors आपस में match नहीं रहते।

---

## 🔴 Problem it Solves
Search systems rarely crash; they decay. New terms ("USB-C PD 140W charger") are missing from the old distribution, the index mixes vectors from two model versions after a partial re-embed, and users stop trusting results. Monitoring drift detects this early and triggers re-indexing or fine-tuning before users complain.

## 🔴 यह क्यों बना? (Hindi)
Search systems शायद ही crash होते हैं; वे धीरे-धीरे बिगड़ते हैं। नए terms ("USB-C PD 140W charger") पुराने distribution में नहीं थे, partial re-embed के बाद index में दो model versions के vectors मिल जाते हैं, और users का भरोसा घटता है। Drift monitoring यह जल्दी पकड़ती है और users के शिकायत करने से पहले re-indexing या fine-tuning शुरू करवाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Types of drift:
          (a) Data drift: new documents differ from old ones
          (b) Query drift: users ask new kinds of questions
          (c) Model drift: model version changed / API model updated / mixed versions
Step 2 → Store model name, version, dimensions and embedded_at with every vector
Step 3 → Keep a frozen golden set; re-run recall@k on schedule (weekly / every deploy)
Step 4 → Compare distributions: mean cosine of recent queries to the nearest centroid,
          average top-1 score, empty-result rate, distance between old/new centroids
Step 5 → Online signals: click-through, "no result" rate, thumbs down
Step 6 → Alert when metrics cross thresholds
Step 7 → Fix: re-embed changed data, rebuild with a new model in a parallel index,
          switch via blue/green, or fine-tune
Step 8 → Pin model versions; never mix versions in one index
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Drift के types:
          (a) Data drift: नए documents पुराने जैसे नहीं
          (b) Query drift: users नए तरह के सवाल पूछते हैं
          (c) Model drift: model version बदला / API model update / mixed versions
Step 2 → हर vector के साथ model name, version, dimensions, embedded_at store करो
Step 3 → Frozen golden set रखो; schedule पर (हर हफ्ते / हर deploy) recall@k दोबारा चलाओ
Step 4 → Distributions compare करो: नई queries का nearest centroid से औसत cosine,
          औसत top-1 score, empty-result rate, पुराने/नए centroids की दूरी
Step 5 → Online signals: click-through, "no result" rate, thumbs down
Step 6 → Thresholds पार होने पर alert
Step 7 → Fix: बदले data को re-embed, नए model से parallel index बनाओ, blue/green switch, या fine-tune
Step 8 → Model versions pin करो; एक index में versions कभी मत मिलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: In January the customs authority updates the HS nomenclature (new codes for e-bikes and EV chargers). Importers start using new terms. The weekly check shows average top-1 cosine for the last 7 days fell from 0.71 to 0.58 and the "no good match" rate doubled. The team ingests the new nomenclature, re-embeds the changed codes, and adds the new query phrases to the golden set.

**Zomato-style**: New food trends ("birria tacos") are not in older embeddings; search quality drops until terms are indexed or the model is updated.

## 🟡 Real Example Hindi mein
**Tariff System**: जनवरी में customs authority HS nomenclature update करती है (e-bikes और EV chargers के नए codes)। Importers नए terms इस्तेमाल करने लगते हैं। Weekly check दिखाता है कि पिछले 7 दिनों का औसत top-1 cosine 0.71 से 0.58 हो गया और "no good match" rate दोगुना। Team नई nomenclature ingest करती है, बदले codes re-embed करती है और नए query phrases golden set में जोड़ती है।

**Zomato-style**: नए food trends ("birria tacos") पुराने embeddings में नहीं होते; terms index होने या model update होने तक search quality गिरती है।

---

## 💻 Code Example — Basic
```python
# Simple drift monitor: compare recent top-1 scores against a baseline (pure Python, runs offline)
from statistics import mean, pstdev


def drift_report(baseline: list[float], recent: list[float], z_threshold: float = 2.0) -> dict[str, float | bool]:
    """Flag drift if the recent mean falls well below the baseline mean."""
    if len(baseline) < 2 or not recent:
        raise ValueError("need at least 2 baseline scores and 1 recent score")
    b_mean, b_std = mean(baseline), pstdev(baseline) or 1e-9      # avoid division by zero
    r_mean = mean(recent)
    z = (b_mean - r_mean) / (b_std / (len(recent) ** 0.5))        # how many std errors below baseline
    return {"baseline_mean": round(b_mean, 3), "recent_mean": round(r_mean, 3),
            "z": round(z, 2), "drift": z > z_threshold}


baseline_scores = [0.72, 0.70, 0.74, 0.69, 0.71, 0.73, 0.70]      # top-1 cosine last quarter
this_week = [0.60, 0.58, 0.61, 0.57, 0.62]                        # after nomenclature update
print(drift_report(baseline_scores, this_week))                   # drift True
print(drift_report(baseline_scores, [0.71, 0.72, 0.70]))          # drift False
```

## 💻 Code Example — Advanced
```python
# Drift checks on real embeddings: golden-set recall + centroid shift between old and new data (async)
import asyncio
import numpy as np
from openai import AsyncOpenAI

client = AsyncOpenAI()
MODEL = "text-embedding-3-small"


async def embed(texts: list[str]) -> np.ndarray:
    try:
        r = await client.embeddings.create(model=MODEL, input=texts)
    except Exception as exc:
        raise RuntimeError(f"embed failed: {exc}") from exc
    v = np.asarray([d.embedding for d in sorted(r.data, key=lambda d: d.index)], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def centroid_shift(old: np.ndarray, new: np.ndarray) -> float:
    """1 - cosine between mean vectors: 0 = same topic mix, larger = more shift."""
    a, b = old.mean(0), new.mean(0)
    return float(1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def novelty(queries: np.ndarray, docs: np.ndarray, threshold: float = 0.35) -> float:
    """Share of queries whose best document match is weak -> content gap or query drift."""
    best = (queries @ docs.T).max(axis=1)
    return float((best < threshold).mean())


async def golden_recall(docs: list[str], golden: list[tuple[str, int]], k: int = 3) -> float:
    d = await embed(docs)
    q = await embed([g[0] for g in golden])
    top = np.argsort(-(q @ d.T), axis=1)[:, :k]
    return float(np.mean([g[1] in row for g, row in zip(golden, top)]))


async def main() -> None:
    docs = ["Headphones and earphones", "Coffee, not roasted", "Smartphones", "Electric bicycles"]
    old_q = await embed(["earbuds", "coffee beans", "mobile phone"])
    new_q = await embed(["e-bike motor kit", "EV charger 22kW", "lithium battery pack"])
    d = await embed(docs)
    print("centroid shift:", round(centroid_shift(old_q, new_q), 3))
    print("novelty (old):", novelty(old_q, d), "novelty (new):", novelty(new_q, d))
    print("golden recall:", await golden_recall(docs, [("earbuds", 0), ("e-bike", 3)], k=1))


if __name__ == "__main__":
    asyncio.run(main())                                           # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from collections import deque
from statistics import mean

app = FastAPI()
BASELINE = 0.70                                      # measured top-1 score on the golden set
window: deque[float] = deque(maxlen=500)             # rolling live top-1 scores


class Observation(BaseModel):
    top1_score: float = Field(ge=-1, le=1)           # logged at every search


@app.post("/metrics/search")
async def record(obs: Observation) -> dict[str, str]:
    window.append(obs.top1_score)
    return {"status": "ok"}


@app.get("/metrics/drift")
async def drift() -> dict[str, float | bool | int]:
    if len(window) < 50:
        return {"samples": len(window), "drift": False}
    m = mean(window)
    return {"samples": len(window), "rolling_mean": round(m, 3), "drift": m < BASELINE - 0.08}
```
In production send these metrics to Prometheus/Grafana or Datadog and alert from there.

---

## 🔗 LangChain / LangGraph Connection
LangChain's indexing API (`RecordManager` + `index()`) tracks content hashes so changed documents are re-embedded and deleted ones cleaned up, which handles data drift. Put the embedding model name in the vector store collection name or metadata.

```python
from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(collection_name="tariff_te3small_v1", embedding_function=emb)   # model in the name
rm = SQLRecordManager("chroma/tariff_te3small_v1", db_url="sqlite:///records.db")
rm.create_schema()
docs = [Document(page_content="Electric bicycles", metadata={"source": "hs-2025"})]
print(index(docs, rm, store, cleanup="incremental", source_id_key="source"))
```
In LangGraph, add an "evaluate retrieval" node that logs top scores and triggers a re-index sub-graph when thresholds are crossed.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-embedding only part of the corpus with a new model
✅ Correct: One index = one model version. Build a new index and switch.

```python
# Wrong: index.upsert(new_model_vectors)   # mixed spaces
# Right: build "tariff_v2" fully, test, then point the alias to it
```

❌ Mistake 2: No metadata about the model
✅ Correct: Store `model`, `dimensions`, `embedded_at` on every vector.

❌ Mistake 3: Monitoring only latency and errors
✅ Correct: Also monitor retrieval quality (golden-set recall, top score trend).

---

## 🧠 Tricky Interview Question

**Q**: "Nothing in your code changed, yet retrieval quality dropped last month. The provider says the model name is unchanged. What can you check?"

**Answer**: (1) Data drift: new documents or vocabulary; compare distributions and novelty. (2) Query drift: users ask different things; look at the no-match rate and new query clusters. (3) Provider-side changes: some "latest" aliases move; check the exact model version and re-run the golden set against a stored sample of old vectors (re-embed 100 old texts and compare with stored vectors; cosine near 1.0 means same model). (4) Pipeline issues: chunking or cleaning changes, a corrupted ingestion, or mixed dimensions. Fix according to the root cause and pin versions.

---

## ⚫ Interview Questions + Answers

Q1: What is embedding drift?
A1: Degradation of retrieval quality over time caused by changes in data, queries, or the embedding model.

Q2: How do you detect it?
A2: Golden-set recall, tracking average top-k similarity, no-result rate, query/document distribution shift, and user feedback.

Q3: Why should you never mix model versions in one index?
A3: Different models have different vector spaces, so similarity scores between them are meaningless.

Q4: How do you migrate to a new embedding model safely?
A4: Build a parallel index, run the eval set on both, shadow-test live traffic, switch with an alias (blue/green), keep rollback, and then delete the old index.

Q5: Design a drift monitoring system.
A5: Log query text hash, top-k scores and chosen result; nightly job embeds a sample, compares to baseline (centroid shift, novelty rate, KS test on scores); weekly golden-set recall; dashboards and alerts; a canary test that re-embeds fixed sample texts and compares to stored vectors to detect silent model changes; runbook for re-index; track costs of re-embedding.

---

## 🔷 When to Use + When Not to Use
✅ Monitor drift when:
- Content changes often (catalogues, regulations, news)
- Models can change (hosted APIs)
- Quality matters for compliance or revenue

❌ Heavy monitoring is overkill when:
- A static corpus and pinned local model, small internal tool

---

## 📊 Visual Diagram
```
 time ───────────────────────────────────────────────►
 data/queries change ─┐
 model version change ─┼─► vectors out of sync ─► top-1 score ↓, no-result ↑
 partial re-embed ─────┘
          │ detect: golden set, score trend, centroid shift, canary
          ▼ fix: re-embed changed docs / new index + switch / fine-tune
```

---

## 💰 Cost Impact
Monitoring is cheap (a golden set of 500 queries costs cents). Remediation is the cost: a full re-embed of 120M tokens costs about $2.40 with small ($15.60 with large; half with the Batch API) plus vector DB dual-running during migration (double storage temporarily). Incremental re-embedding of only changed documents is far cheaper, so keep content hashes. Drift left unchecked costs more indirectly: poor retrieval makes LLMs hallucinate or users retry, which wastes LLM tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding drift | Quality decay over time | समय के साथ quality गिरना |
| Data drift | Documents change | Documents का बदलना |
| Query drift | User questions change | Users के सवाल बदलना |
| Golden set | Frozen labelled test | Frozen labelled test |
| Blue/green | Switch between two indexes | दो indexes के बीच switch |
| Canary | Small check to detect changes | बदलाव पकड़ने वाली छोटी जाँच |

---

## ⚡ 3-Line Summary
English: Drift is silent decay of retrieval quality from changing data, queries, or models. Store model metadata, monitor a golden set and score trends, and never mix versions in an index. Fix with incremental re-embedding or a blue/green migration.
Hindi: Drift बदलते data, queries या models से retrieval quality का चुपचाप गिरना है। Model metadata store करो, golden set और score trends monitor करो, और index में versions कभी मत मिलाओ। Incremental re-embedding या blue/green migration से सुधारो।

---

## ➡️ Next Topic
**124. Vector Databases Introduction** - where embeddings are stored and searched at scale (next folder section).
