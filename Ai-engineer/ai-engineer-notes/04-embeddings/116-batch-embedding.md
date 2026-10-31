---

# 116. Batch Embedding — Complete Guide
# हिंदी में: Batch Embedding — पूरी Guide

---

## 🔵 Simple Definition (English)
Batch embedding means embedding many texts together instead of one by one. You send a list of texts in a single request (up to 2048 for OpenAI) or process them with a local model in mini-batches. It is faster, cheaper in overhead, and avoids rate limits. For large offline jobs, OpenAI's Batch API gives a 50% discount.

## 🔵 सरल परिभाषा (Hindi)
Batch embedding का मतलब है कई texts को एक साथ embed करना, एक-एक करके नहीं। एक request में texts की list भेजते हैं (OpenAI में 2048 तक) या local model में mini-batches चलाते हैं। यह तेज़ है, overhead कम होता है, rate limits से बचाता है। बड़े offline jobs के लिए OpenAI Batch API 50% discount देती है।

---

## 🔴 Problem it Solves
Embedding 1 million rows with one request per row means 1 million HTTP round trips (about 100 ms each = 28 hours serially) and instant rate-limit errors. Batching cuts requests 100 to 1000 times. On GPUs, batching also fills the hardware, giving 10 to 50x throughput versus single-item encoding.

## 🔴 यह क्यों बना? (Hindi)
10 लाख rows को एक-एक request से embed करने पर 10 लाख HTTP round trips (प्रत्येक लगभग 100 ms = serial में 28 घंटे) और तुरंत rate-limit errors। Batching से requests 100-1000 गुना घटती हैं। GPU पर batching hardware को भरती है और single-item से 10-50x throughput देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clean + dedupe texts; keep (id, text) pairs
Step 2 → Sort by length (optional) so batches have similar sizes
Step 3 → Split into batches: <= 2048 inputs and a safe token total per request
Step 4 → Send batches concurrently with a semaphore (e.g. 4 to 8 at once)
Step 5 → On 429/5xx retry with exponential backoff + jitter
Step 6 → Map results back by index (response order = input order; verify)
Step 7 → Write to the vector DB in bulk; checkpoint progress (resume on crash)
Step 8 → Offline/non-urgent: OpenAI Batch API (JSONL file, 24h, 50% cheaper)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Texts clean + dedupe करो; (id, text) pairs रखो
Step 2 → लंबाई से sort करो (optional) ताकि batches का size एक जैसा रहे
Step 3 → Batches में बाँटो: <= 2048 inputs और सुरक्षित token total
Step 4 → Semaphore के साथ concurrent भेजो (जैसे 4-8 एक साथ)
Step 5 → 429/5xx पर exponential backoff + jitter से retry
Step 6 → Index से results वापस map करो
Step 7 → Vector DB में bulk write करो; progress checkpoint करो (crash पर resume)
Step 8 → Non-urgent: OpenAI Batch API (JSONL file, 24h, 50% सस्ता)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The initial load has 2 million historical declarations (about 400M tokens). The team writes a JSONL file with one `/v1/embeddings` request per 1,000 rows and submits it through the Batch API: cost $4 instead of $8 (small model), finished overnight. Daily deltas (5,000 rows) go through the normal real-time batched endpoint.

**Amazon-style**: Catalogue refresh of 50M products each week via the Batch API.

## 🟡 Real Example Hindi mein
**Tariff System**: Initial load में 20 लाख historical declarations (लगभग 40 करोड़ tokens) हैं। Team JSONL file बनाती है जिसमें हर 1,000 rows की एक `/v1/embeddings` request है, और Batch API से भेजती है: cost $8 की जगह $4, रात भर में पूरा। रोज़ के delta (5,000 rows) normal real-time batched endpoint से जाते हैं।

**Amazon-style**: हर हफ्ते 5 करोड़ products का catalogue refresh Batch API से।

---

## 💻 Code Example — Basic
```python
# Batching helper + resumable processing (pure Python with a fake embedder; runs offline)
from typing import Iterator, TypeVar

T = TypeVar("T")


def batched(items: list[T], size: int) -> Iterator[list[T]]:
    """Yield consecutive slices of `size` items."""
    if size <= 0:
        raise ValueError("size must be positive")
    for i in range(0, len(items), size):
        yield items[i:i + size]


def fake_embed(batch: list[str]) -> list[list[float]]:
    return [[float(len(t))] for t in batch]       # stand-in for a real API call


texts = [f"tariff note {i}" for i in range(10)]
done: dict[int, list[float]] = {}                 # checkpoint: index -> vector
for start, batch in enumerate(batched(texts, 4)):
    offset = start * 4
    if offset in done:                            # already processed -> skip (resume)
        continue
    for j, vec in enumerate(fake_embed(batch)):
        done[offset + j] = vec                    # save result with its global index
print(len(done), "vectors; batches:", len(list(batched(texts, 4))))   # 10, 3
```

## 💻 Code Example — Advanced
```python
# Async batch embedder with bounded concurrency, retries, and order preservation
import asyncio
import random
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIStatusError

client = AsyncOpenAI(max_retries=0)
MODEL = "text-embedding-3-small"


async def embed_batch(texts: list[str], attempts: int = 5) -> list[list[float]]:
    """One request with exponential backoff and jitter."""
    for i in range(attempts):
        try:
            r = await client.embeddings.create(model=MODEL, input=texts)
            return [d.embedding for d in sorted(r.data, key=lambda d: d.index)]
        except (RateLimitError, APIConnectionError):
            await asyncio.sleep(min(60, 2 ** i) + random.random())
        except APIStatusError as exc:
            if exc.status_code < 500:
                raise                              # client error: do not retry
            await asyncio.sleep(2 ** i)
    raise RuntimeError(f"batch failed after {attempts} attempts")


async def embed_many(texts: list[str], batch_size: int = 500, concurrency: int = 4
                     ) -> list[list[float] | None]:
    """Embed all texts; failed batches leave None so the job can resume."""
    sem = asyncio.Semaphore(concurrency)
    results: list[list[float] | None] = [None] * len(texts)

    async def worker(start: int) -> None:
        chunk = texts[start:start + batch_size]
        async with sem:
            try:
                vecs = await embed_batch(chunk)
            except Exception as exc:               # log and continue with other batches
                print(f"batch at {start} failed: {exc}")
                return
        results[start:start + len(vecs)] = vecs    # place by position

    await asyncio.gather(*(worker(s) for s in range(0, len(texts), batch_size)))
    return results


if __name__ == "__main__":
    out = asyncio.run(embed_many([f"note {i}" for i in range(1200)]))
    print(sum(v is not None for v in out), "of", len(out), "embedded")
```

OpenAI Batch API outline (file based):
```python
import json
from openai import OpenAI

client = OpenAI()
with open("batch_input.jsonl", "w") as f:
    for i, chunk in enumerate([["a", "b"], ["c", "d"]]):          # your chunks
        f.write(json.dumps({"custom_id": f"req-{i}", "method": "POST",
                            "url": "/v1/embeddings",
                            "body": {"model": "text-embedding-3-small", "input": chunk}}) + "\n")
file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch = client.batches.create(input_file_id=file.id, endpoint="/v1/embeddings",
                              completion_window="24h")
print(batch.id, batch.status)       # poll client.batches.retrieve(batch.id) later
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
import asyncio
import uuid

app = FastAPI()
jobs: dict[str, dict[str, object]] = {}               # use Redis/DB in production


class BatchReq(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100_000)


async def run_job(job_id: str, texts: list[str]) -> None:
    jobs[job_id]["status"] = "running"
    for i in range(0, len(texts), 500):                # simulate batched embedding
        await asyncio.sleep(0)                         # real code: await embed_batch(...)
        jobs[job_id]["done"] = min(len(texts), i + 500)
    jobs[job_id]["status"] = "finished"


@app.post("/embed/jobs")
async def create_job(req: BatchReq, bg: BackgroundTasks) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "done": 0, "total": len(req.texts)}
    bg.add_task(run_job, job_id, req.texts)            # return immediately
    return {"job_id": job_id}


@app.get("/embed/jobs/{job_id}")
async def job_status(job_id: str) -> dict[str, object]:
    return jobs.get(job_id, {"status": "not_found"})
```
For huge jobs use a real queue (Celery, RQ, Arq) instead of `BackgroundTasks`.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=500)  # texts per request
vectors = emb.embed_documents(["note 1", "note 2"])                      # auto-batches
# async: vectors = await emb.aembed_documents(texts)
```
In LangGraph ingestion pipelines, use a "chunk list" state key and one `embed` node that processes a batch per super-step; use `Send` for parallel fan-out over batches.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loop of single calls
✅ Correct: Send lists.

```python
# Wrong
for t in texts: client.embeddings.create(model=M, input=t)
# Right
for b in batched(texts, 500): client.embeddings.create(model=M, input=b)
```

❌ Mistake 2: Unlimited `asyncio.gather` over thousands of requests
✅ Correct: Use a semaphore to cap concurrency.

❌ Mistake 3: No checkpointing
✅ Correct: Store progress so a crash at 90% does not restart from zero.

---

## 🧠 Tricky Interview Question

**Q**: "Your batch job embedded 1M rows, but 3,000 vectors are attached to the wrong documents. What went wrong?"

**Answer**: Results were matched by arrival order instead of by `index`/ID. With concurrency, batches finish out of order; also within a response you should sort by `data[i].index`. Another cause: dropping empty or failed texts shifts the list. Fix: carry stable IDs with every text, write results by ID, validate counts (`len(vectors) == len(texts)`), and run a spot check by re-embedding samples.

---

## ⚫ Interview Questions + Answers

Q1: Max inputs per OpenAI embeddings request?
A1: 2048 inputs, each up to 8191 tokens (and a total token limit per request).

Q2: Why is batching faster?
A2: Fewer network round trips and better hardware utilisation.

Q3: What is the Batch API trade-off?
A3: 50% cheaper, higher rate limits, but results within up to 24 hours; not for real-time.

Q4: How do you avoid rate-limit failures?
A4: Bounded concurrency, backoff with jitter, respect `Retry-After`, and spread load.

Q5: Design a resumable pipeline for 100M documents.
A5: Shard data by ID range; a queue of shard tasks; workers embed batches and bulk-upsert (id, vector, model, content_hash) into the vector DB; a progress table marks shards done; idempotent upserts allow retries; dead-letter queue for poison documents; metrics on tokens, errors, and throughput; use Batch API where latency is not needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Ingesting more than a few dozen texts
- Backfills and migrations
- Local GPU encoding

❌ Avoid when:
- A single interactive query (just one call)
- Batches so large that one bad item fails the whole request (keep moderate)

---

## 📊 Visual Diagram
```
 1,000,000 texts
      │ split
      ▼
 [b1][b2][b3]...[b2000]   (500 each)
      │ semaphore: 4 in flight
      ▼
  embedding API ──retry/backoff──► vectors by index
      │
      ▼
  bulk upsert to vector DB + checkpoint
```

---

## 💰 Cost Impact
Batching itself does not change per-token price, but the Batch API gives 50% off: for 400M tokens with small, $8 becomes $4 (large: $52 becomes $26). Savings also come from fewer failed/retried calls. Estimate tokens first with tiktoken, dedupe before sending, and keep per-request token totals under limits.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Batch | Group of inputs in one call | एक call में inputs का समूह |
| Batch API | 24h async job, 50% cheaper | सस्ता async job |
| Semaphore | Concurrency limiter | Concurrency सीमित करने वाला |
| Backoff | Wait longer after each failure | हर failure पर ज़्यादा इंतज़ार |
| Checkpoint | Saved progress | Saved progress |
| Idempotent upsert | Safe to repeat write | दोहराने पर भी सुरक्षित write |

---

## ⚡ 3-Line Summary
English: Send many texts per request, cap concurrency, retry with backoff, and map results by index. Use the Batch API for 50% savings on offline loads. Checkpoint progress so jobs can resume.
Hindi: एक request में कई texts भेजो, concurrency सीमित करो, backoff के साथ retry करो और index से results map करो। Offline loads पर Batch API से 50% बचत। Progress checkpoint करो ताकि job resume हो सके।

---

## ➡️ Next Topic
**117. Embedding for Different Data Types** - text is not the only input: tables, code, JSON, logs and PDFs need different handling.
