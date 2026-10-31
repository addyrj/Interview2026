---

# 112. Sentence Transformers (local embeddings) — Complete Guide
# हिंदी में: Sentence Transformers (local embeddings) — पूरी Guide

---

## 🔵 Simple Definition (English)
`sentence-transformers` is an open-source Python library that runs embedding models **on your own machine** (CPU or GPU). You load a model such as `all-MiniLM-L6-v2` and call `model.encode(texts)` to get vectors. No API key, no per-token cost, and data never leaves your server.

## 🔵 सरल परिभाषा (Hindi)
`sentence-transformers` एक open-source Python library है जो embedding models को **आपकी अपनी machine** (CPU या GPU) पर चलाती है। `all-MiniLM-L6-v2` जैसा model load करो और `model.encode(texts)` से vectors पाओ। API key नहीं, per-token cost नहीं, और data server से बाहर नहीं जाता।

---

## 🔴 Problem it Solves
APIs add cost, latency, rate limits and privacy risk. Customs or legal data may not be allowed to leave the company. At very high volume, paying per token costs more than owning a GPU. Local models solve these, at the price of managing hardware, model versions and scaling.

## 🔴 यह क्यों बना? (Hindi)
APIs से cost, latency, rate limits और privacy risk आते हैं। Customs या legal data company से बाहर भेजना मना हो सकता है। बहुत high volume पर per-token pay करना GPU खरीदने से महँगा पड़ता है। Local models ये हल करते हैं, बदले में hardware, model versions और scaling खुद संभालनी पड़ती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install sentence-transformers  (installs torch; heavy)
Step 2 → model = SentenceTransformer("all-MiniLM-L6-v2")  (downloads once, cached)
Step 3 → Text is tokenised, passed through a transformer
Step 4 → Token vectors are pooled (mean pooling) into one sentence vector
Step 5 → model.encode(list, batch_size=32, normalize_embeddings=True)
Step 6 → Returns numpy array (n, d); MiniLM d = 384
Step 7 → Compare with cosine (util.cos_sim) or dot (normalised)
Step 8 → Max input length ~256 word pieces for MiniLM (longer text is truncated)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install sentence-transformers  (torch भी आता है; भारी)
Step 2 → model = SentenceTransformer("all-MiniLM-L6-v2")  (एक बार download, cache)
Step 3 → Text tokenise होकर transformer से गुज़रता है
Step 4 → Token vectors को pool (mean) करके एक sentence vector बनता है
Step 5 → model.encode(list, batch_size=32, normalize_embeddings=True)
Step 6 → numpy array (n, d) मिलता है; MiniLM में d = 384
Step 7 → cosine (util.cos_sim) या dot (normalised) से compare करो
Step 8 → MiniLM की max length ~256 word pieces; उससे लंबा text कटता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A government client forbids sending shipment descriptions to external APIs. The team deploys `paraphrase-multilingual-MiniLM-L12-v2` (supports Hindi) on an internal GPU server, behind a FastAPI `/embed` route. Costs are fixed, latency is 10 to 20 ms per batch.

**Zomato-style**: Embedding millions of reviews nightly on one GPU is cheaper than API calls.

## 🟡 Real Example Hindi mein
**Tariff System**: Government client shipment descriptions को external API पर भेजने की अनुमति नहीं देता। Team `paraphrase-multilingual-MiniLM-L12-v2` (Hindi support) को internal GPU server पर FastAPI `/embed` route के पीछे चलाती है। Cost fixed, latency प्रति batch 10-20 ms।

**Zomato-style**: करोड़ों reviews को रात में एक GPU पर embed करना API calls से सस्ता है।

---

## 💻 Code Example — Basic
```python
# Local embeddings with sentence-transformers (falls back to a fake model if not installed)
from typing import Any

try:
    from sentence_transformers import SentenceTransformer, util   # pip install sentence-transformers
    HAVE_ST = True
except ImportError:
    HAVE_ST = False                              # offline demo path


def load_model(name: str = "all-MiniLM-L6-v2") -> Any:
    """Load the model (first run downloads weights)."""
    if not HAVE_ST:
        return None
    return SentenceTransformer(name)             # runs on CPU or GPU automatically


model = load_model()
texts: list[str] = ["Wireless earbuds", "Bluetooth headphones", "Fresh coffee beans"]

if model is not None:
    vecs = model.encode(texts, normalize_embeddings=True)   # numpy array (3, 384)
    print("shape:", vecs.shape)
    print("earbuds vs headphones:", float(util.cos_sim(vecs[0], vecs[1])))   # high
    print("earbuds vs coffee    :", float(util.cos_sim(vecs[0], vecs[2])))   # low
else:
    print("sentence-transformers not installed; pip install sentence-transformers")
```

## 💻 Code Example — Advanced
```python
# Production wrapper: lazy load, batching, thread offload so async servers stay responsive
import asyncio
from functools import lru_cache
import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)                            # load the model only once per process
def get_model(name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> SentenceTransformer:
    return SentenceTransformer(name)


def encode_sync(texts: list[str], batch_size: int = 64) -> NDArray[np.float32]:
    """Blocking encode; call from a thread in async code."""
    if not texts:
        return np.empty((0, 0), dtype=np.float32)    # nothing to do
    try:
        arr = get_model().encode(
            texts,
            batch_size=batch_size,               # larger batch = faster on GPU
            normalize_embeddings=True,           # unit vectors -> dot == cosine
            show_progress_bar=False,
            convert_to_numpy=True,
        )
    except Exception as exc:                     # OOM, bad input, etc.
        raise RuntimeError(f"local embedding failed: {exc}") from exc
    return arr.astype(np.float32)


async def encode(texts: list[str]) -> NDArray[np.float32]:
    """Async wrapper: CPU/GPU-bound work runs in a worker thread."""
    return await asyncio.to_thread(encode_sync, texts)


if __name__ == "__main__":
    v = asyncio.run(encode(["मोबाइल चार्जर", "phone charger"]))
    print(v.shape, float(v[0] @ v[1]))           # multilingual model -> high similarity
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel, Field
import asyncio
from sentence_transformers import SentenceTransformer

state: dict[str, SentenceTransformer] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = SentenceTransformer("all-MiniLM-L6-v2")   # load once at startup
    yield
    state.clear()


app = FastAPI(lifespan=lifespan)


class Req(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=256)


@app.post("/embed")
async def embed(req: Req) -> dict[str, list[list[float]]]:
    arr = await asyncio.to_thread(                # do not block the event loop
        state["model"].encode, req.texts, normalize_embeddings=True
    )
    return {"vectors": arr.tolist()}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_huggingface import HuggingFaceEmbeddings     # pip install langchain-huggingface

emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True},           # unit vectors
)
print(len(emb.embed_query("wireless earbuds")))             # 384
```
Use it as the `embedding` for Chroma/FAISS. In LangGraph, a local-embedding retriever node needs no API key, so the whole graph can run in an air-gapped environment (with a local LLM).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loading the model inside every request
✅ Correct: Load once at startup.

```python
# Wrong: 2-5 seconds per request
@app.post("/e")
def e(t: str): return SentenceTransformer("all-MiniLM-L6-v2").encode(t)
# Right: global/lifespan model
```

❌ Mistake 2: Calling blocking `encode` directly in `async def`
✅ Correct: `await asyncio.to_thread(model.encode, ...)`.

❌ Mistake 3: Ignoring max sequence length
✅ Correct: Chunk to the model's limit (`model.max_seq_length`), otherwise the tail is silently cut.

---

## 🧠 Tricky Interview Question

**Q**: "Your local model gives great results in a notebook but your FastAPI service is slow under load. Why and how to fix?"

**Answer**: Likely causes: model loaded per request; blocking `encode` stalls the event loop; batch size of 1 wastes the GPU; multiple workers each load a copy and exhaust memory. Fixes: load once in lifespan, run encode in a thread or a dedicated worker, use dynamic micro-batching (collect requests for ~10 ms and encode together), limit workers per GPU, and consider ONNX/quantised models or a dedicated server such as Text Embeddings Inference.

---

## ⚫ Interview Questions + Answers

Q1: What does `model.encode` return?
A1: A numpy array of shape (n_texts, dimension), or a tensor if requested.

Q2: Name a small, fast local model and its dimension.
A2: `all-MiniLM-L6-v2`, 384 dimensions.

Q3: Why pass `normalize_embeddings=True`?
A3: Makes vectors unit length so a dot product equals cosine similarity.

Q4: Cloud API or local model: how to choose?
A4: Local if privacy, steady high volume, or offline needs; API if you want top quality quickly, low ops, and bursty volume. Compare on your eval data.

Q5: How would you serve local embeddings for 500 requests/second?
A5: GPU instances with a dedicated embedding server (e.g. Hugging Face TEI or Triton), dynamic batching, FP16/ONNX, autoscaling on queue length, warm model loading, and a cache for repeated queries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data privacy / air-gapped deployments
- High steady volume, fixed hardware budget
- Fine-tuning your own embedding model

❌ Avoid when:
- You have no GPU/ops capacity and low volume
- You need the very best quality and the API model wins your eval

---

## 📊 Visual Diagram
```
 texts ─► tokenizer ─► transformer (local CPU/GPU) ─► mean pooling ─► vector (384)
                         ▲
              weights cached in ~/.cache/huggingface
 No network call at inference time.
```

---

## 💰 Cost Impact
Zero per-token cost, but you pay for hardware: e.g. one small GPU instance for a month can cost a few hundred dollars (prices vary), while MiniLM on CPU may embed hundreds of short texts per second. Break-even versus `text-embedding-3-small` ($0.02 per 1M tokens) is at very high volume (billions of tokens). Optimise: batch, FP16, smaller model, cache, and avoid re-embedding unchanged text.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SentenceTransformer | Library class to load models | Models load करने वाली class |
| `encode` | Text to vectors | Text से vectors |
| Mean pooling | Average token vectors | Token vectors का average |
| `max_seq_length` | Max tokens per text | Per text अधिकतम tokens |
| MiniLM | Small fast model | छोटा तेज़ model |
| Air-gapped | No internet | बिना internet का environment |

---

## ⚡ 3-Line Summary
English: sentence-transformers runs embedding models locally; no API cost and full privacy. Load the model once, normalise vectors, and keep blocking encode off the async event loop. Watch the max sequence length.
Hindi: sentence-transformers embedding models को locally चलाता है; API cost नहीं, पूरी privacy। Model एक बार load करो, vectors normalise करो, और blocking encode को async event loop से बाहर रखो। Max sequence length का ध्यान रखो।

---

## ➡️ Next Topic
**113. Hugging Face Embeddings** - the wider Hugging Face ecosystem: Hub models, `transformers`, TEI server and the Inference API.
