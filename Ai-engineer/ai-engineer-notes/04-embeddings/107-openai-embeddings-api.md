---

# 107. OpenAI Embeddings API — Complete Guide
# हिंदी में: OpenAI Embeddings API — पूरी Guide

---

## 🔵 Simple Definition (English)
The OpenAI Embeddings API turns text into a list of numbers (a vector) that captures meaning. You send strings to `client.embeddings.create(...)` and get back one vector per string. Similar meanings give vectors that are close together.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Embeddings API text को numbers की list (vector) में बदलती है जो meaning पकड़ती है। आप `client.embeddings.create(...)` को strings भेजते हैं और हर string के लिए एक vector मिलता है। मिलते-जुलते meaning के vectors पास-पास होते हैं।

---

## 🔴 Problem it Solves
Training your own embedding model needs data, GPUs and expertise. The API gives you a strong, general model with one HTTP call, priced per token. It removes the need to host anything for semantic search, clustering, classification, and RAG.

## 🔴 यह क्यों बना? (Hindi)
अपना embedding model train करने के लिए data, GPUs और expertise चाहिए। API एक HTTP call में strong general model देती है, token के हिसाब से price। Semantic search, clustering, classification और RAG के लिए कुछ host नहीं करना पड़ता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install openai (>=1.0); set OPENAI_API_KEY
Step 2 → client = OpenAI()
Step 3 → client.embeddings.create(model="text-embedding-3-small", input=[...])
Step 4 → Limits: up to 2048 inputs per request, each <= 8191 tokens
Step 5 → Response: resp.data[i].embedding (list[float]), resp.data[i].index
Step 6 → resp.usage.prompt_tokens / total_tokens = what you are billed for
Step 7 → Optional: dimensions=N to shorten the vector; encoding_format="float"|"base64"
Step 8 → Store vectors in a vector DB; embed queries with the SAME model
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install openai (>=1.0); OPENAI_API_KEY set करो
Step 2 → client = OpenAI()
Step 3 → client.embeddings.create(model=..., input=[...])
Step 4 → Limits: एक request में 2048 inputs तक, हर input <= 8191 tokens
Step 5 → Response: resp.data[i].embedding
Step 6 → resp.usage.total_tokens = billing के tokens
Step 7 → Optional: dimensions=N से vector छोटा करो
Step 8 → Vector DB में store करो; query को SAME model से embed करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: At ingestion, every HS code description (about 8,000 rows) is embedded in batches of 500 with `text-embedding-3-small`. At query time the product description from the importer is embedded and the nearest HS codes are fetched.

**Zomato-style**: Embed every dish name + description once; embed the user's craving "something light and spicy" at search time.

## 🟡 Real Example Hindi mein
**Tariff System**: Ingestion में हर HS code description (लगभग 8,000 rows) 500 के batches में `text-embedding-3-small` से embed होती है। Query के समय importer का product description embed होता है और nearest HS codes निकलते हैं।

**Zomato-style**: हर dish का नाम + description एक बार embed करो; user की craving "something light and spicy" search के समय embed करो।

---

## 💻 Code Example — Basic
```python
# Basic OpenAI embedding call (needs OPENAI_API_KEY; falls back to a fake offline vector)
import os                                      # to read env var
from typing import Optional                    # type hints

try:
    from openai import OpenAI                  # openai>=1.0
except ImportError:                            # package missing
    OpenAI = None                              # type: ignore[assignment]


def embed_one(text: str) -> list[float]:
    """Return one embedding vector for the text."""
    if OpenAI is None or not os.getenv("OPENAI_API_KEY"):   # offline demo mode
        return [float(ord(c) % 7) / 7 for c in text[:8].ljust(8)]   # fake 8-d vector
    client = OpenAI()                          # reads key from env
    resp = client.embeddings.create(           # call the API
        model="text-embedding-3-small",        # cheap, 1536 dimensions
        input=text,                            # single string
    )
    print("tokens billed:", resp.usage.total_tokens)   # usage for cost tracking
    return resp.data[0].embedding              # list[float] of length 1536


vec: list[float] = embed_one("Wireless earbuds with charging case")
print("dimension:", len(vec))                  # 1536 (or 8 in demo mode)
print("first values:", [round(x, 3) for x in vec[:4]])
```

## 💻 Code Example — Advanced
```python
# Production: async, batching, retries with backoff, order-safe, usage tracking
import asyncio                                 # async runner
import random                                  # jitter for backoff
from dataclasses import dataclass              # simple result object
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIStatusError

client = AsyncOpenAI(max_retries=0)            # we control retries ourselves
MODEL = "text-embedding-3-small"
BATCH = 256                                    # inputs per request (max 2048)


@dataclass
class EmbedResult:
    vectors: list[list[float]]                 # same order as input texts
    tokens: int                                # total tokens billed


async def _embed_batch(texts: list[str], attempts: int = 5) -> tuple[list[list[float]], int]:
    """One API call with exponential backoff for transient errors."""
    for attempt in range(attempts):
        try:
            resp = await client.embeddings.create(model=MODEL, input=texts)
            ordered = sorted(resp.data, key=lambda d: d.index)   # keep input order
            return [d.embedding for d in ordered], resp.usage.total_tokens
        except (RateLimitError, APIConnectionError):             # retryable
            await asyncio.sleep(2 ** attempt + random.random())  # backoff + jitter
        except APIStatusError as exc:                            # 4xx/5xx
            if exc.status_code >= 500:                           # server error: retry
                await asyncio.sleep(2 ** attempt)
            else:
                raise                                            # 400/401: do not retry
    raise RuntimeError("embedding failed after retries")


async def embed_texts(texts: list[str]) -> EmbedResult:
    """Embed any number of texts in batches, concurrently but bounded."""
    clean = [t.replace("\n", " ").strip() or " " for t in texts]  # empty string is invalid
    sem = asyncio.Semaphore(4)                 # at most 4 concurrent requests

    async def run(chunk: list[str]) -> tuple[list[list[float]], int]:
        async with sem:                        # limit concurrency
            return await _embed_batch(chunk)

    chunks = [clean[i:i + BATCH] for i in range(0, len(clean), BATCH)]
    parts = await asyncio.gather(*(run(c) for c in chunks))
    vectors = [v for part in parts for v in part[0]]             # flatten in order
    return EmbedResult(vectors, sum(p[1] for p in parts))


if __name__ == "__main__":
    res = asyncio.run(embed_texts(["HS 8518 earphones", "HS 0901 coffee"]))
    print(len(res.vectors), res.tokens)        # 2 vectors, small token count
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, OpenAIError

app = FastAPI()
client = AsyncOpenAI()                         # one shared client (connection pool)


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100)


class EmbedResponse(BaseModel):
    vectors: list[list[float]]
    tokens: int


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest) -> EmbedResponse:
    try:
        r = await client.embeddings.create(
            model="text-embedding-3-small", input=req.texts
        )
    except OpenAIError as exc:                 # covers auth, rate limit, network
        raise HTTPException(status_code=502, detail=f"upstream: {exc}")
    return EmbedResponse(vectors=[d.embedding for d in r.data], tokens=r.usage.total_tokens)
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")   # LangChain wrapper
v = emb.embed_query("wireless earbuds")                  # one vector
vs = emb.embed_documents(["Headphones", "Coffee"])       # batch of vectors
# async: await emb.aembed_query(...), await emb.aembed_documents([...])
```
`OpenAIEmbeddings` is what vector stores such as Chroma, FAISS, and PGVector call. In a LangGraph RAG graph the "retrieve" node calls it implicitly through `vectorstore.as_retriever()`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One API call per text in a loop
✅ Correct: Send a list; the API accepts up to 2048 inputs per request.

```python
# Wrong: 1000 requests, slow, hits rate limits
vecs = [client.embeddings.create(model=M, input=t).data[0].embedding for t in texts]
# Right: a few batched requests
resp = client.embeddings.create(model=M, input=texts[:500])
```

❌ Mistake 2: Sending an empty string or text over 8191 tokens
✅ Correct: Replace empties with a space, chunk long text first (see tiktoken).

❌ Mistake 3: Embedding queries with a different model than documents
✅ Correct: Keep one `EMBED_MODEL` constant in config.

---

## 🧠 Tricky Interview Question

**Q**: "You embedded 1M documents with `text-embedding-ada-002` last year. Now you want `text-embedding-3-small` for queries only, to save money. Will it work?"

**Answer**: No. Each model has its own vector space; vectors from different models cannot be compared even if dimensions match (or are shortened to match). You must re-embed the whole corpus with the new model (about 1M x avg tokens x $0.02/1M), or keep the old model for queries. Plan model versioning and store the model name in metadata.

---

## ⚫ Interview Questions + Answers

Q1: What does the Embeddings API return?
A1: A list `data` where each item has `embedding` (floats), `index`, plus `usage` token counts.

Q2: How many inputs and tokens can one request take?
A2: Up to 2048 input strings, each up to 8191 tokens (and a total token cap per request, so batch moderately).

Q3: How do you handle rate limits?
A3: Batch inputs, limit concurrency with a semaphore, retry with exponential backoff and jitter on `RateLimitError`, and use the Batch API for offline bulk jobs.

Q4: What is the `dimensions` parameter?
A4: Only for v3 models. It returns a shortened vector (e.g. 256 or 512) with small quality loss, saving storage and search time.

Q5: Design embedding ingestion for 10M documents.
A5: Chunk with tiktoken, dedupe by content hash, check cache, batch 500-1000 per request, run N workers with backoff, write vectors + model name + hash to the vector DB in bulk, make the job idempotent and resumable (store progress), and use the Batch API (50% cheaper, 24h) for non-urgent loads.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want strong quality with zero infrastructure
- Corpus and query volume are moderate
- Multi-language support is needed

❌ Avoid when:
- Data cannot leave your network (use local models)
- Extremely high volume makes self-hosting cheaper
- You need offline operation

---

## 📊 Visual Diagram
```
 texts ["a","b","c"]
      │  client.embeddings.create(model, input)
      ▼
 ┌──────────────┐
 │ OpenAI model │  -> 3 x 1536 floats
 └──────────────┘
      │
      ▼
 vector DB (store)   query text -> same model -> nearest vectors
```

---

## 💰 Cost Impact
Embeddings are billed only for **input tokens** (no output tokens). Prices per 1M tokens: `text-embedding-3-small` $0.02, `text-embedding-3-large` $0.13, `ada-002` $0.10 (check the pricing page, prices change). Example: 100,000 tariff chunks x 300 tokens = 30M tokens = $0.60 with small. Optimise: dedupe, cache by hash, strip boilerplate, use Batch API (50% off), and shorter `dimensions` to cut storage.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector representing meaning | Meaning का vector |
| `input` | String or list of strings | Embed होने वाला text |
| `dimensions` | Shorten vector (v3 only) | Vector छोटा करना |
| `usage.total_tokens` | Billed tokens | Billing के tokens |
| Batch API | Async 50% cheaper processing | सस्ता async processing |
| Rate limit | Max requests/tokens per minute | प्रति मिनट सीमा |

---

## ⚡ 3-Line Summary
English: `client.embeddings.create` converts strings to vectors; batch many inputs per call. You pay per input token only, and queries must use the same model as documents. Add retries, caching, and store the model name.
Hindi: `client.embeddings.create` strings को vectors में बदलता है; एक call में कई inputs भेजो। सिर्फ input tokens का पैसा लगता है, और query व documents में same model चाहिए। Retries, caching और model name store करो।

---

## ➡️ Next Topic
**108. text-embedding-3-small vs large** - which model to pick, quality vs cost trade-offs.
