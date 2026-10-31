---

# 111. Cohere Embeddings — Complete Guide
# हिंदी में: Cohere Embeddings — पूरी Guide

---

## 🔵 Simple Definition (English)
Cohere provides embedding models through its Embed API. They support many languages, require an `input_type` (such as `search_document` or `search_query`), and can return float, int8, or binary vectors. Current models include `embed-v4.0` and the `embed-multilingual-v3.0` family.

## 🔵 सरल परिभाषा (Hindi)
Cohere अपनी Embed API से embedding models देता है। ये कई भाषाओं को support करते हैं, `input_type` माँगते हैं (जैसे `search_document` या `search_query`), और float, int8 या binary vectors दे सकते हैं। Current models में `embed-v4.0` और `embed-multilingual-v3.0` family शामिल हैं।

---

## 🔴 Problem it Solves
Many models are English-first. Indian trade data mixes English, Hindi, Gujarati, Arabic and Chinese product names. Cohere's multilingual models place equivalent meanings from different languages close together, enabling cross-language search. Compressed embedding types (int8, binary) also cut storage up to 32x.

## 🔴 यह क्यों बना? (Hindi)
कई models English-first हैं। Indian trade data में English, Hindi, Gujarati, Arabic, Chinese के product names मिले होते हैं। Cohere के multilingual models अलग भाषाओं के बराबर meaning को पास रखते हैं, जिससे cross-language search संभव है। Compressed types (int8, binary) storage 32x तक घटाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install cohere; set CO_API_KEY (or pass api_key)
Step 2 → co = cohere.ClientV2(api_key=...)
Step 3 → Documents: co.embed(texts=[...], model="embed-v4.0",
                             input_type="search_document", embedding_types=["float"])
Step 4 → Vectors at response.embeddings.float_  (list of lists)
Step 5 → Queries: same call with input_type="search_query"
Step 6 → Other input types: "classification", "clustering"
Step 7 → Max 96 texts per call; chunk larger lists
Step 8 → Store vectors, search by cosine/dot, optionally rerank with Cohere Rerank
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install cohere; API key set करो
Step 2 → co = cohere.ClientV2(api_key=...)
Step 3 → Documents: co.embed(..., input_type="search_document", embedding_types=["float"])
Step 4 → Vectors response.embeddings.float_ में
Step 5 → Queries: वही call, input_type="search_query"
Step 6 → और types: "classification", "clustering"
Step 7 → एक call में अधिकतम 96 texts; बड़ी list को बाँटो
Step 8 → Vectors store करो, cosine/dot से search, चाहें तो Cohere Rerank
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer writes "मोबाइल फोन चार्जर" (Hindi). Documents are English HS descriptions. A multilingual Cohere model embeds both into the same space, so the query matches "8504.40 Static converters (chargers)" without translation. This saves a translation LLM call per request.

**Zomato-style**: Hinglish queries like "paneer wala starter" match English dish names.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer लिखता है "मोबाइल फोन चार्जर" (Hindi)। Documents English HS descriptions हैं। Multilingual Cohere model दोनों को same space में embed करता है, इसलिए query बिना translation के "8504.40 Static converters (chargers)" से match होती है। हर request पर translation की LLM call बचती है।

**Zomato-style**: "paneer wala starter" जैसी Hinglish queries English dish names से match होती हैं।

---

## 💻 Code Example — Basic
```python
# Cohere embeddings with an offline fallback
import os
from typing import Literal

CohereInput = Literal["search_document", "search_query", "classification", "clustering"]


def embed(texts: list[str], input_type: CohereInput = "search_document") -> list[list[float]]:
    """Return one vector per text. Uses Cohere when CO_API_KEY exists."""
    key = os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY")   # either env name
    if not key:                                  # offline demo
        return [[float(len(t)), float(sum(map(ord, t)) % 13), 1.0] for t in texts]
    import cohere                                # pip install cohere
    co = cohere.ClientV2(api_key=key)            # v2 client
    resp = co.embed(                             # call Embed API
        texts=texts,
        model="embed-v4.0",                      # check docs for current models
        input_type=input_type,
        embedding_types=["float"],               # ask for float vectors
    )
    return resp.embeddings.float_                # list[list[float]]


vecs = embed(["Headphones", "Static converters"], "search_document")
print(len(vecs), "vectors, dim", len(vecs[0]))
```

## 💻 Code Example — Advanced
```python
# Async batching (max 96 texts/call) + retries + int8 option
import asyncio
import numpy as np
import cohere

co = cohere.AsyncClientV2()                      # reads CO_API_KEY from env
MAX_BATCH = 96                                   # Cohere limit per request


async def embed_batch(texts: list[str], input_type: str, attempts: int = 4) -> np.ndarray:
    """Embed up to 96 texts with exponential backoff."""
    for i in range(attempts):
        try:
            r = await co.embed(texts=texts, model="embed-v4.0",
                               input_type=input_type, embedding_types=["float"])
            return np.asarray(r.embeddings.float_, dtype=np.float32)
        except cohere.errors.TooManyRequestsError:       # 429: slow down
            await asyncio.sleep(2 ** i)
        except Exception as exc:                          # other errors: stop
            raise RuntimeError(f"cohere embed failed: {exc}") from exc
    raise RuntimeError("rate limited too long")


async def embed_all(texts: list[str], input_type: str = "search_document") -> np.ndarray:
    """Split into batches and run a few at a time."""
    sem = asyncio.Semaphore(3)                   # polite concurrency

    async def one(chunk: list[str]) -> np.ndarray:
        async with sem:
            return await embed_batch(chunk, input_type)

    chunks = [texts[i:i + MAX_BATCH] for i in range(0, len(texts), MAX_BATCH)]
    parts = await asyncio.gather(*(one(c) for c in chunks))
    return np.vstack(parts)


if __name__ == "__main__":
    out = asyncio.run(embed_all(["Headphones", "Coffee", "मोबाइल फोन"]))
    print(out.shape)                             # (3, dim)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import cohere

app = FastAPI()
co = cohere.AsyncClientV2()


class SearchReq(BaseModel):
    query: str = Field(min_length=1)


@app.post("/embed/query")
async def embed_query(req: SearchReq) -> dict[str, int]:
    try:
        r = await co.embed(texts=[req.query], model="embed-v4.0",
                           input_type="search_query", embedding_types=["float"])
    except Exception as exc:
        raise HTTPException(502, f"cohere error: {exc}")
    return {"dims": len(r.embeddings.float_[0])}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_cohere import CohereEmbeddings          # pip install langchain-cohere

emb = CohereEmbeddings(model="embed-multilingual-v3.0")  # needs COHERE_API_KEY
vec = emb.embed_query("मोबाइल फोन चार्जर")
docs = emb.embed_documents(["Static converters", "Coffee"])
```
`CohereEmbeddings` sets the right `input_type` for `embed_query` vs `embed_documents`. In LangGraph, use it in the retrieve node, and add `CohereRerank` as a second step for higher precision.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `input_type`
✅ Correct: Always pass it; the v3+ models require it.

```python
# Wrong
co.embed(texts=texts, model="embed-v4.0")           # missing input_type -> error/poor
# Right
co.embed(texts=texts, model="embed-v4.0", input_type="search_document", embedding_types=["float"])
```

❌ Mistake 2: Sending more than 96 texts per call
✅ Correct: Batch in groups of 96.

❌ Mistake 3: Using `search_document` for the query
✅ Correct: Query side uses `search_query`.

---

## 🧠 Tricky Interview Question

**Q**: "Hindi queries retrieve English documents poorly with your English-only model. What are your options and trade-offs?"

**Answer**: (1) Translate queries to English with a small LLM first: adds latency and cost per request, translation errors. (2) Use a multilingual embedding model (Cohere multilingual, multilingual-e5, OpenAI v3 large) so both languages share a space: no extra call, but test per-language recall. (3) Embed documents in both languages: doubles storage. Evaluate each with a labelled Hindi/English set; usually (2) wins on simplicity.

---

## ⚫ Interview Questions + Answers

Q1: What is `input_type` for?
A1: It tells the model if the text is a document, query, or for classification/clustering, so it encodes appropriately.

Q2: Name Cohere's multilingual embedding model.
A2: `embed-multilingual-v3.0` (and `embed-v4.0`, which is also multilingual).

Q3: What are `embedding_types`?
A3: The numeric format returned: `float`, `int8`, `uint8`, `binary`, `ubinary`. Smaller types save storage.

Q4: Why add a reranker after embeddings?
A4: Embedding search is fast but approximate. A cross-encoder reranker reads query and document together to reorder the top-k, raising precision.

Q5: How would you cut vector storage 8x with minimal loss?
A5: Request `int8` (4x) or `binary` (32x) embeddings; search compressed vectors for candidates and rescore the top few hundred with float vectors. Measure recall@k before and after.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multilingual search (Indian languages, Arabic, Chinese)
- You want compressed embeddings and a bundled reranker

❌ Avoid when:
- Data must stay on-prem without an enterprise deployment
- English-only, price-sensitive, and OpenAI small already fits

---

## 📊 Visual Diagram
```
 "मोबाइल फोन चार्जर" ─┐
 "mobile phone charger" ─┼─► Cohere multilingual model ─► nearby vectors
 "8504.40 chargers"   ─┘
        input_type: search_query | search_document
```

---

## 💰 Cost Impact
Cohere bills per input token (embed models cost cents per 1M tokens; see the Cohere pricing page, prices vary by model and plan). Trial keys are rate limited and not for production. Savings: embed once and cache; use int8/binary types to shrink the vector DB bill; batch 96 per call; avoid translation LLM calls by using multilingual embeddings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `search_document` | Input type for corpus | Corpus के लिए input type |
| `search_query` | Input type for queries | Query के लिए input type |
| Multilingual | Many languages, shared space | कई भाषाएँ, एक space |
| int8 / binary | Compressed vectors | Compressed vectors |
| Rerank | Re-order top results precisely | Top results को दोबारा क्रम देना |

---

## ⚡ 3-Line Summary
English: Cohere Embed handles many languages and needs `input_type`. Batch at most 96 texts and consider int8/binary vectors for storage. Add a reranker for precision.
Hindi: Cohere Embed कई भाषाओं को handle करता है और `input_type` माँगता है। एक call में अधिकतम 96 texts, और storage के लिए int8/binary सोचो। Precision के लिए reranker जोड़ो।

---

## ➡️ Next Topic
**112. Sentence Transformers (local embeddings)** - run embeddings on your own machine for free and for privacy.
