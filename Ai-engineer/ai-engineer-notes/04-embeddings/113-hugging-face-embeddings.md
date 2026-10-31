---

# 113. Hugging Face Embeddings — Complete Guide
# हिंदी में: Hugging Face Embeddings — पूरी Guide

---

## 🔵 Simple Definition (English)
Hugging Face is the main hub for open embedding models (BGE, E5, GTE, MiniLM, nomic and more). You can use them three ways: (1) directly with `transformers` (tokenizer + model + pooling), (2) through `sentence-transformers`, or (3) as a hosted service (Inference API / Inference Endpoints / Text Embeddings Inference server).

## 🔵 सरल परिभाषा (Hindi)
Hugging Face open embedding models (BGE, E5, GTE, MiniLM, nomic आदि) का main hub है। इन्हें तीन तरह से use करते हैं: (1) `transformers` से सीधे (tokenizer + model + pooling), (2) `sentence-transformers` से, (3) hosted service से (Inference API / Endpoints / Text Embeddings Inference server)।

---

## 🔴 Problem it Solves
Closed APIs lock you in on price, privacy and model choice. The Hub offers hundreds of models ranked on the MTEB leaderboard, in many languages and sizes, with open licences. You can pick the best model for your language and domain, fine-tune it, and host it anywhere.

## 🔴 यह क्यों बना? (Hindi)
Closed APIs में price, privacy और model choice पर lock-in रहता है। Hub में सैकड़ों models हैं (MTEB leaderboard पर ranked), कई भाषाओं और sizes में, open licences के साथ। आप अपनी भाषा और domain का best model चुन सकते हैं, fine-tune कर सकते हैं और कहीं भी host कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a model on the Hub (check MTEB score, language, licence, size)
Step 2 → Read the model card: pooling type (mean/CLS), normalisation, prefixes
          e.g. E5 needs "query: " / "passage: " prefixes; BGE uses a query instruction
Step 3 → Load tokenizer + AutoModel (or SentenceTransformer)
Step 4 → Tokenise (padding, truncation, return_tensors="pt")
Step 5 → Forward pass -> last_hidden_state (batch, tokens, hidden)
Step 6 → Pool: mean over tokens using the attention mask (or take CLS)
Step 7 → L2 normalise -> final vectors
Step 8 → Host yourself or use TEI / Inference Endpoints for production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Hub पर model चुनो (MTEB score, भाषा, licence, size देखो)
Step 2 → Model card पढ़ो: pooling (mean/CLS), normalisation, prefixes
          जैसे E5 को "query: " / "passage: " prefix चाहिए
Step 3 → Tokenizer + AutoModel (या SentenceTransformer) load करो
Step 4 → Tokenise (padding, truncation, return_tensors="pt")
Step 5 → Forward pass -> last_hidden_state
Step 6 → Pool: attention mask के साथ tokens पर mean (या CLS)
Step 7 → L2 normalise -> final vectors
Step 8 → Production के लिए खुद host करो या TEI / Inference Endpoints use करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team compares `BAAI/bge-m3` (multilingual), `intfloat/multilingual-e5-base`, and OpenAI small on 300 labelled customs queries. `bge-m3` matches OpenAI recall on Hindi queries, is free to run locally, and is deployed on one GPU with TEI.

**Amazon-style**: Fine-tune a small BGE model on click logs (query to product pairs) to improve product search.

## 🟡 Real Example Hindi mein
**Tariff System**: Team 300 labelled customs queries पर `BAAI/bge-m3` (multilingual), `intfloat/multilingual-e5-base` और OpenAI small compare करती है। Hindi queries पर `bge-m3` OpenAI के बराबर recall देता है, locally free चलता है, और एक GPU पर TEI से deploy होता है।

**Amazon-style**: Click logs (query से product pairs) पर छोटे BGE model को fine-tune करके product search बेहतर करो।

---

## 💻 Code Example — Basic
```python
# Raw transformers: tokenizer + model + mean pooling (shows what encode() does inside)
from typing import Any

try:
    import torch                                 # pip install torch transformers
    from transformers import AutoTokenizer, AutoModel
    HAVE = True
except ImportError:
    HAVE = False                                 # offline demo path


def mean_pool(last_hidden: Any, mask: Any) -> Any:
    """Average token vectors, ignoring padding."""
    m = mask.unsqueeze(-1).float()               # (batch, tokens, 1)
    return (last_hidden * m).sum(1) / m.sum(1).clamp(min=1e-9)


def embed(texts: list[str], name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Any:
    tok = AutoTokenizer.from_pretrained(name)    # download tokenizer
    model = AutoModel.from_pretrained(name).eval()   # download weights, eval mode
    batch = tok(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():                        # no gradients needed
        out = model(**batch)                     # forward pass
    pooled = mean_pool(out.last_hidden_state, batch["attention_mask"])
    return torch.nn.functional.normalize(pooled, p=2, dim=1)   # unit length


if HAVE:
    v = embed(["Wireless earbuds", "Bluetooth headphones"])
    print(v.shape, float(v[0] @ v[1]))           # (2, 384) and a high score
else:
    print("install torch and transformers to run this example")
```

## 💻 Code Example — Advanced
```python
# Hosted embeddings via huggingface_hub InferenceClient + E5 prefixes, async, retries
import asyncio
import os
import numpy as np
from huggingface_hub import AsyncInferenceClient      # pip install huggingface_hub

MODEL = "intfloat/multilingual-e5-large"
client = AsyncInferenceClient(model=MODEL, token=os.getenv("HF_TOKEN"))


def with_prefix(texts: list[str], kind: str) -> list[str]:
    """E5 models need 'query: ' or 'passage: ' in front of the text."""
    prefix = "query: " if kind == "query" else "passage: "
    return [prefix + t for t in texts]


async def embed(texts: list[str], kind: str = "passage", attempts: int = 4) -> np.ndarray:
    """Call the feature-extraction endpoint with backoff."""
    for i in range(attempts):
        try:
            out = await client.feature_extraction(with_prefix(texts, kind))
            arr = np.asarray(out, dtype=np.float32)
            arr = arr.reshape(len(texts), -1)           # (n, d) for pooled output
            return arr / np.linalg.norm(arr, axis=1, keepdims=True)
        except Exception as exc:
            if i == attempts - 1:
                raise RuntimeError(f"HF embedding failed: {exc}") from exc
            await asyncio.sleep(2 ** i)                  # model loading / rate limit
    raise RuntimeError("unreachable")


async def main() -> None:
    docs = await embed(["Static converters (chargers)", "Coffee, not roasted"], "passage")
    q = (await embed(["मोबाइल चार्जर"], "query"))[0]
    print(np.argsort(-(docs @ q)))                       # best doc index first


if __name__ == "__main__":
    asyncio.run(main())                                  # needs HF_TOKEN
```
(`feature_extraction` output shape depends on the model/endpoint; if you get token-level output, mean-pool it. Check the model card.)

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
import os

app = FastAPI()
TEI_URL = os.getenv("TEI_URL", "http://localhost:8080")   # Text Embeddings Inference server


class Req(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=128)


@app.post("/embed")
async def embed(req: Req) -> dict[str, list[list[float]]]:
    try:
        async with httpx.AsyncClient(timeout=30) as http:
            r = await http.post(f"{TEI_URL}/embed", json={"inputs": req.texts})
            r.raise_for_status()                       # 4xx / 5xx -> exception
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"TEI error: {exc}")
    return {"vectors": r.json()}                       # TEI returns list of vectors
```
TEI is Hugging Face's high-throughput embedding server (Docker image) with dynamic batching.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings

# Local model
local = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5",
                              encode_kwargs={"normalize_embeddings": True})

# Hosted endpoint (HF token needed)
remote = HuggingFaceEndpointEmbeddings(model="BAAI/bge-small-en-v1.5")
```
Both implement the LangChain `Embeddings` interface, so Chroma, FAISS and retrievers work unchanged; LangGraph nodes just call the retriever.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ignoring required prefixes (E5, BGE queries)
✅ Correct: Follow the model card.

```python
# Wrong
embed(["mobile charger"])                       # E5 without prefix: lower quality
# Right
embed(["query: mobile charger"])
```

❌ Mistake 2: Taking the first token or all tokens instead of correct pooling
✅ Correct: Use the pooling in the model card (mean or CLS), with the attention mask.

❌ Mistake 3: Choosing by leaderboard rank alone
✅ Correct: MTEB averages many tasks; test on your own domain and language.

---

## 🧠 Tricky Interview Question

**Q**: "Model A scores higher than model B on MTEB, but B performs better on your tariff data. Is the benchmark wrong?"

**Answer**: No. MTEB is an average over many tasks and mostly general English text; your task is domain-specific (HS codes, legal wording, multilingual short queries). Also the model might be trained on the benchmark data (leakage). Always build a domain eval set and choose by recall@k, latency, size and licence.

---

## ⚫ Interview Questions + Answers

Q1: What is MTEB?
A1: Massive Text Embedding Benchmark, a leaderboard comparing embedding models on retrieval, clustering, classification, and more.

Q2: What is mean pooling?
A2: Averaging the token vectors (excluding padding) to get one sentence vector.

Q3: What is Text Embeddings Inference (TEI)?
A3: A fast Rust-based server from Hugging Face that serves embedding models with dynamic batching.

Q4: Why do some models need prefixes?
A4: They were trained with task prefixes (e.g. "query:" / "passage:"), so omitting them moves the input off-distribution.

Q5: How would you fine-tune an embedding model for tariff search?
A5: Build (query, positive HS description, hard negative) triples from past classifications, fine-tune with contrastive loss (MultipleNegativesRankingLoss in sentence-transformers), evaluate recall@k against the base model on a held-out set, and version the model; then re-embed the whole corpus.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need open licences, choice of language models, or fine-tuning
- You want to self-host for privacy or cost

❌ Avoid when:
- You cannot manage GPU infra and volume is low
- Model licence prohibits your commercial use (check!)

---

## 📊 Visual Diagram
```
 text ─► tokenizer ─► token ids ─► transformer ─► token vectors
                                                      │ pooling (mean/CLS)
                                                      ▼
                                          sentence vector ─► normalise
 Serving options:  local code | sentence-transformers | TEI server | HF Endpoints
```

---

## 💰 Cost Impact
Open models are free to download; cost is compute. Hosted HF Inference Endpoints bill per hour of the instance (GPU instances can cost from around a dollar per hour upward, check current pricing); the serverless Inference API has free/limited tiers. Throughput with TEI on one GPU can reach thousands of short texts per second, so unit cost drops at scale. Optimise with small models (bge-small), batching, quantisation, and caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hub | Hugging Face model repository | Models का repository |
| MTEB | Embedding benchmark | Embedding benchmark |
| Pooling | Combine token vectors | Token vectors जोड़ना |
| TEI | Text Embeddings Inference server | Embedding serving server |
| Prefix | Task marker text | Task बताने वाला text |
| Fine-tuning | Adapt model to your data | अपने data पर model सुधारना |

---

## ⚡ 3-Line Summary
English: Hugging Face gives access to many open embedding models usable via transformers, sentence-transformers, or TEI. Follow the model card for pooling and prefixes, and pick by your own eval. Self-hosting trades API fees for infra work.
Hindi: Hugging Face कई open embedding models देता है जिन्हें transformers, sentence-transformers या TEI से use कर सकते हैं। Pooling और prefixes के लिए model card follow करो और अपने eval से चुनो। Self-hosting में API fees की जगह infra का काम आता है।

---

## ➡️ Next Topic
**114. Embedding Cost Optimization** - ways to cut embedding spend across all providers.
