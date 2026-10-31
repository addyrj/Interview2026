---

# 108. text-embedding-3-small vs large — Complete Guide
# हिंदी में: text-embedding-3-small vs large — पूरी Guide

---

## 🔵 Simple Definition (English)
OpenAI offers two third-generation embedding models. `text-embedding-3-small` is cheap and fast (1536 dimensions by default). `text-embedding-3-large` is more accurate but costs more and gives bigger vectors (3072 dimensions by default). Both support shortening via the `dimensions` parameter.

## 🔵 सरल परिभाषा (Hindi)
OpenAI के दो third-generation embedding models हैं। `text-embedding-3-small` सस्ता और तेज़ है (default 1536 dimensions)। `text-embedding-3-large` ज़्यादा accurate पर महँगा है और बड़े vectors देता है (default 3072)। दोनों में `dimensions` parameter से vector छोटा किया जा सकता है।

---

## 🔴 Problem it Solves
Older `ada-002` was one size for everyone: 1536 dims, $0.10 per 1M tokens. Teams needed a cheaper option for bulk data and a stronger one for hard retrieval tasks. The v3 pair lets you pick the point on the quality/cost curve and tune the vector size.

## 🔴 यह क्यों बना? (Hindi)
पुराना `ada-002` सबके लिए एक ही size था: 1536 dims, $0.10 प्रति 1M tokens। Teams को bulk data के लिए सस्ता और कठिन retrieval के लिए strong option चाहिए था। v3 जोड़ी से आप quality और cost का balance चुन सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a small labelled eval set (queries + correct documents)
Step 2 → Embed corpus with small AND large (optionally with dimensions=512/1024)
Step 3 → Measure recall@k / MRR for each configuration
Step 4 → Compute cost: tokens x price, plus storage: n x dims x 4 bytes
Step 5 → Compare quality gain vs cost increase (large is ~6.5x price)
Step 6 → Choose the cheapest config meeting your quality target
Step 7 → Re-evaluate when data or languages change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → छोटा labelled eval set बनाओ (queries + सही documents)
Step 2 → Corpus को small और large दोनों से embed करो (चाहें तो dimensions=512/1024)
Step 3 → हर config का recall@k / MRR नापो
Step 4 → Cost निकालो: tokens x price, और storage: n x dims x 4 bytes
Step 5 → Quality gain बनाम cost increase compare करो (large लगभग 6.5x महँगा)
Step 6 → सबसे सस्ता config चुनो जो target पूरा करे
Step 7 → Data या language बदले तो फिर evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: HS code descriptions are short, formal English. `small` at 1536 dims already hits recall@5 of 0.93 in our test. For multilingual importer descriptions (Hindi, Arabic, Chinese) `large` lifts recall@5 to 0.97. Decision: use `large` at `dimensions=1024` for multilingual queries; keep `small` for the English-only internal search.

(These numbers are illustrative; measure on your own data.)

**Amazon-style**: Product titles are short; small is enough. Legal contracts search might justify large.

## 🟡 Real Example Hindi mein
**Tariff System**: HS code descriptions छोटी, formal English में होती हैं। `small` (1536 dims) पहले ही अच्छा recall देता है। Multilingual importer descriptions (Hindi, Arabic, Chinese) में `large` बेहतर रहता है। Decision: multilingual queries के लिए `large` (`dimensions=1024`), English-only internal search के लिए `small`।

(ये numbers उदाहरण हैं; अपने data पर नापो।)

---

## 💻 Code Example — Basic
```python
# Compare the two models' cost and storage (pure Python, runs offline)
from dataclasses import dataclass              # simple record


@dataclass(frozen=True)
class EmbModel:
    name: str                                  # API model name
    dims: int                                  # default dimension
    price_per_m: float                         # USD per 1M input tokens


SMALL = EmbModel("text-embedding-3-small", 1536, 0.02)
LARGE = EmbModel("text-embedding-3-large", 3072, 0.13)


def estimate(model: EmbModel, docs: int, tokens_per_doc: int, dims: int | None = None) -> dict[str, float]:
    """Return embedding cost (USD) and vector storage (MB) for a corpus."""
    d = dims or model.dims                     # use shortened dims if given
    cost = docs * tokens_per_doc * model.price_per_m / 1_000_000   # token price
    storage_mb = docs * d * 4 / 1_048_576      # float32 = 4 bytes each
    return {"cost_usd": round(cost, 2), "storage_mb": round(storage_mb, 1)}


for m, d in [(SMALL, None), (LARGE, None), (LARGE, 1024)]:
    print(m.name, d or m.dims, estimate(m, docs=1_000_000, tokens_per_doc=300, dims=d))
# small: ~$6.00, ~5859 MB; large full: ~$39.00, ~11719 MB; large@1024: ~$39.00, ~3906 MB
```

## 💻 Code Example — Advanced
```python
# Evaluate both models on a labelled set (recall@k), async, with error handling
import asyncio
import numpy as np
from numpy.typing import NDArray
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def embed(model: str, texts: list[str], dims: int | None = None) -> NDArray[np.float32]:
    """Embed texts; pass dimensions only when supplied."""
    kwargs: dict = {"model": model, "input": texts}
    if dims is not None:
        kwargs["dimensions"] = dims            # v3 models only
    try:
        r = await client.embeddings.create(**kwargs)
    except Exception as exc:
        raise RuntimeError(f"{model} failed: {exc}") from exc
    v = np.asarray([d.embedding for d in r.data], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)    # re-normalise (needed after truncation)


async def recall_at_k(model: str, docs: list[str], queries: list[str],
                      truth: list[int], k: int = 3, dims: int | None = None) -> float:
    """Fraction of queries whose correct doc index is in top-k."""
    d_vec, q_vec = await asyncio.gather(embed(model, docs, dims), embed(model, queries, dims))
    scores = q_vec @ d_vec.T                   # (queries, docs) cosine
    top = np.argsort(-scores, axis=1)[:, :k]   # indexes of best docs
    hits = sum(t in row for t, row in zip(truth, top))
    return hits / len(queries)


async def main() -> None:
    docs = ["Headphones and earphones", "Coffee, not roasted", "Mobile phones", "Wheat flour"]
    queries = ["wireless earbuds", "arabica beans", "smartphone"]
    truth = [0, 1, 2]
    for model, dims in [("text-embedding-3-small", None), ("text-embedding-3-large", 1024)]:
        r = await recall_at_k(model, docs, queries, truth, k=1, dims=dims)
        print(model, dims, "recall@1 =", r)


if __name__ == "__main__":
    asyncio.run(main())                        # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, OpenAIError
from typing import Literal

app = FastAPI()
client = AsyncOpenAI()
MODELS = {"fast": ("text-embedding-3-small", None), "accurate": ("text-embedding-3-large", 1024)}


class Req(BaseModel):
    text: str = Field(min_length=1)
    tier: Literal["fast", "accurate"] = "fast"   # caller picks quality tier


@app.post("/embed")
async def embed(req: Req) -> dict[str, int | str]:
    model, dims = MODELS[req.tier]
    kwargs = {"model": model, "input": req.text}
    if dims:
        kwargs["dimensions"] = dims
    try:
        r = await client.embeddings.create(**kwargs)
    except OpenAIError as exc:
        raise HTTPException(502, str(exc))
    return {"model": model, "dims": len(r.data[0].embedding), "tokens": r.usage.total_tokens}
```
Important: documents embedded with one tier must be queried with the same tier.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings

small = OpenAIEmbeddings(model="text-embedding-3-small")
large = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)  # shortened

# Use different vector store collections per model:
# Chroma(collection_name="tariff_small", embedding_function=small)
# Chroma(collection_name="tariff_large_1024", embedding_function=large)
```
In LangGraph, a router node can choose the tier (e.g. multilingual query -> large collection), then the retrieve node queries the matching collection.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming "large" is always worth it
✅ Correct: Measure on your data; often small is within 1-3% recall.

❌ Mistake 2: Truncating vectors manually (`vec[:512]`) without re-normalising
✅ Correct: Use the `dimensions` API parameter, or re-normalise after cutting.

```python
# Wrong: raw slice, vector no longer unit length
v = vec[:512]
# Right
v = np.array(vec[:512]); v = v / np.linalg.norm(v)
```

❌ Mistake 3: Mixing small and large vectors in one index
✅ Correct: One index (collection) per model + dimension.

---

## 🧠 Tricky Interview Question

**Q**: "Large at 256 dimensions beat ada-002 at 1536 on MTEB. Why does that matter for cost?"

**Answer**: Matryoshka-style training puts the most important information in the first dimensions, so you can shorten vectors with little loss. A 256-d large vector is 6x smaller than 1536-d: 6x less memory and faster search, with accuracy still above old models. You pay the same embedding API price (per token, not per dimension), but you save on vector DB RAM and latency.

---

## ⚫ Interview Questions + Answers

Q1: Which is cheaper, small or large?
A1: Small: about $0.02 vs $0.13 per 1M tokens.

Q2: Default dimensions of each?
A2: Small 1536, large 3072.

Q3: How do you reduce vector size?
A3: Pass `dimensions=N` in the API call (e.g. 512, 1024). The vector is shortened and renormalised by the service.

Q4: Can you switch models without re-embedding?
A4: No. Different vector spaces; re-embed the corpus. Do a blue/green migration: build a new index, compare, then switch.

Q5: How do you decide between them for a multilingual tariff corpus?
A5: Build a labelled set in each language, measure recall@k and MRR for small, large, and large with reduced dims. Compute total cost = embedding + storage + search latency. Choose the cheapest configuration meeting target recall, and monitor over time for drift.

---

## 🔷 When to Use + When Not to Use
✅ Use small when:
- English or simple domains, large volume, tight budget

✅ Use large when:
- Multilingual, nuanced or long-tail retrieval where recall gains matter

❌ Avoid large when:
- Quality gain is under your noise level in eval
- Memory budget is tight (unless shortened)

---

## 📊 Visual Diagram
```
                 quality
                    ▲
        large 3072  ●  ($0.13/M)
   large@1024      ●
        small 1536 ●   ($0.02/M)
   small@512      ●
                    └──────────────► cost / storage
```

---

## 💰 Cost Impact
| Model | Price / 1M tokens | Default dims | 1M docs x 300 tokens |
|-------|------------------|--------------|----------------------|
| small | $0.02 | 1536 | $6 |
| large | $0.13 | 3072 | $39 |
| ada-002 | $0.10 | 1536 | $30 |

Storage for 1M vectors in float32: 1536 d = 5.7 GB, 3072 d = 11.4 GB, 1024 d = 3.8 GB. Optimise by picking small by default, shortening dims, caching and deduplicating. (Prices from the OpenAI pricing page at the time of writing; recheck.)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| text-embedding-3-small | Cheap, 1536-d model | सस्ता model |
| text-embedding-3-large | Accurate, 3072-d model | ज़्यादा accurate model |
| `dimensions` | Output vector size | Output vector का size |
| MTEB | Embedding benchmark | Embedding benchmark |
| Recall@k | Correct item in top k | Top k में सही item |
| Matryoshka | Nested dimensions trick | Nested dimension तकनीक |

---

## ⚡ 3-Line Summary
English: Small is cheap and good enough for most tasks; large is stronger but 6.5x costlier. Both can be shortened with `dimensions`. Decide with a measured eval, not by guessing.
Hindi: Small सस्ता है और ज़्यादातर tasks के लिए काफी; large ज़्यादा strong पर 6.5x महँगा। दोनों को `dimensions` से छोटा कर सकते हैं। Decision eval से लो, अंदाज़े से नहीं।

---

## ➡️ Next Topic
**109. Embedding Dimensions** - what dimensions mean, how shortening works, and the memory/accuracy trade-off.
