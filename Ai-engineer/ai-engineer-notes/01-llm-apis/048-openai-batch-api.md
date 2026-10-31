---

# 048. OpenAI Batch API
# हिंदी में: OpenAI Batch API

---

## 🔵 Simple Definition (English)
The Batch API lets you upload a file of many requests (JSONL), and OpenAI processes them asynchronously within a completion window (currently 24 hours) at a discount (about 50% cheaper than normal calls). You come back later and download the results file.

## 🔵 सरल परिभाषा (Hindi)
Batch API में आप कई requests की file (JSONL) upload करते हैं और OpenAI उन्हें एक completion window (अभी 24 घंटे) में asynchronously process करता है, normal calls से लगभग 50% सस्ता। बाद में आप results file download करते हैं।

---

## 🔴 Problem it Solves
- Bulk jobs (classify 2 million products) hit rate limits when sent as normal live calls.
- Live calls cost full price even when nobody is waiting.
- Writing your own queue, retry and rate-limit handling is a lot of work.

## 🔴 यह क्यों बना? (Hindi)
- Bulk jobs (20 लाख products classify करना) live calls से भेजने पर rate limits में फँसते हैं।
- कोई इंतज़ार न कर रहा हो तब भी live calls full price लेते हैं।
- अपनी queue, retry और rate-limit handling लिखना बहुत काम है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a .jsonl file: each line = {custom_id, method, url, body}
Step 2 → Upload the file with purpose="batch"
Step 3 → Create the batch: input_file_id, endpoint="/v1/chat/completions", completion_window="24h"
Step 4 → OpenAI processes requests in the background (separate rate-limit pool)
Step 5 → Poll batch status: validating -> in_progress -> finalizing -> completed (or failed/expired)
Step 6 → Download output_file_id (and error_file_id for failed lines)
Step 7 → Match each result line to your data by custom_id (order is NOT guaranteed)
Step 8 → Retry failed lines in a new batch
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → .jsonl file बनाओ: हर line = {custom_id, method, url, body}
Step 2 → File को purpose="batch" के साथ upload करो
Step 3 → Batch बनाओ: input_file_id, endpoint="/v1/chat/completions", completion_window="24h"
Step 4 → OpenAI background में process करता है (अलग rate-limit pool)
Step 5 → Status poll करो: validating -> in_progress -> finalizing -> completed (या failed/expired)
Step 6 → output_file_id download करो (failed lines के लिए error_file_id)
Step 7 → custom_id से result को अपने data से match करो (order की guarantee नहीं)
Step 8 → Failed lines को नए batch में दोबारा भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker uploads 300,000 historical invoice lines to be classified overnight. We write them to a JSONL file with `custom_id="inv-000123"`, submit a batch, and next morning download results and load them into the database. Cost is about half of live calls, and no live traffic is affected.

**Amazon-style**: Generating product descriptions or tags for the full catalogue each weekend; nobody needs the answers instantly.

## 🟡 Real Example Hindi mein
**Tariff System**: एक customs broker 300,000 पुरानी invoice lines रात भर classify करने के लिए upload करता है। हम उन्हें `custom_id="inv-000123"` के साथ JSONL में लिखते हैं, batch submit करते हैं, और अगली सुबह results download करके database में डालते हैं। Cost live calls की लगभग आधी, और live traffic पर कोई असर नहीं।

**Amazon-style**: हर weekend पूरे catalogue के product descriptions या tags बनाना; जवाब तुरंत नहीं चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic: build a batch input file and parse a fake output file (offline, pure Python)
import json  # JSON lines
from pathlib import Path  # file paths

products = ["wireless earbuds", "cotton t-shirt", "basmati rice"]  # data to classify

def build_line(i: int, text: str) -> dict:
    return {
        "custom_id": f"item-{i}",  # your key to match results later
        "method": "POST",  # HTTP method
        "url": "/v1/chat/completions",  # endpoint
        "body": {  # normal request body
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"HS chapter for: {text}"}],
            "max_tokens": 20,
        },
    }

path = Path("batch_input.jsonl")  # file name
with path.open("w", encoding="utf-8") as f:  # write the file
    for i, p in enumerate(products):  # one line per request
        f.write(json.dumps(build_line(i, p)) + "\n")  # JSONL: one JSON per line
print("Wrote", len(products), "requests to", path)  # confirm

# Pretend this came back from OpenAI (order can differ!):
fake_output = [
    {"custom_id": "item-2", "response": {"status_code": 200, "body": {"choices": [{"message": {"content": "10"}}]}}, "error": None},
    {"custom_id": "item-0", "response": {"status_code": 200, "body": {"choices": [{"message": {"content": "85"}}]}}, "error": None},
]
results = {r["custom_id"]: r["response"]["body"]["choices"][0]["message"]["content"] for r in fake_output}
for i, p in enumerate(products):  # match by custom_id, not by order
    print(p, "->", results.get(f"item-{i}", "MISSING"))
path.unlink()  # clean up the demo file
```

## 💻 Code Example — Advanced
```python
# Production-style: submit, wait (async), download, parse, collect errors
import asyncio  # async polling
import io  # in-memory file
import json  # parse lines
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI()  # shared client

async def submit_batch(lines: list[dict]) -> str:
    payload = "\n".join(json.dumps(x) for x in lines).encode("utf-8")  # JSONL bytes
    try:
        f = await client.files.create(  # upload file
            file=("batch.jsonl", io.BytesIO(payload)), purpose="batch")
        batch = await client.batches.create(  # create batch
            input_file_id=f.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"job": "tariff-nightly"},
        )
    except APIError as exc:  # upload/create failed
        raise RuntimeError(f"Could not submit batch: {exc}") from exc
    return batch.id  # store this id in your DB

async def wait_for_batch(batch_id: str, every_s: float = 60.0, max_wait_s: float = 86_400) -> object:
    waited = 0.0  # seconds waited
    while waited <= max_wait_s:
        batch = await client.batches.retrieve(batch_id)  # fresh status
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            return batch  # terminal state
        await asyncio.sleep(every_s)  # wait before next poll
        waited += every_s
    raise TimeoutError("Batch did not finish in time")

async def collect(batch) -> tuple[dict[str, str], dict[str, str]]:
    ok: dict[str, str] = {}  # custom_id -> answer
    bad: dict[str, str] = {}  # custom_id -> error text
    if batch.output_file_id:  # successful lines
        content = await client.files.content(batch.output_file_id)  # download
        for line in content.text.splitlines():  # one JSON per line
            row = json.loads(line)  # parse
            body = row["response"]["body"] if row.get("response") else None
            if body and row["response"]["status_code"] == 200:
                ok[row["custom_id"]] = body["choices"][0]["message"]["content"]
            else:
                bad[row["custom_id"]] = json.dumps(row.get("error") or body)
    if batch.error_file_id:  # failed lines
        content = await client.files.content(batch.error_file_id)
        for line in content.text.splitlines():
            row = json.loads(line)
            bad[row["custom_id"]] = json.dumps(row.get("error") or row.get("response"))
    return ok, bad  # caller retries the 'bad' ids in a new batch
```

---

## 🟠 FastAPI Integration
Make job-style endpoints: submit returns a `batch_id` immediately (HTTP 202); a status endpoint lets the client poll; results are read when done.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app

class Item(BaseModel):
    id: str  # your own id
    text: str  # product text

@app.post("/classify-bulk", status_code=202)
async def classify_bulk(items: list[Item]) -> dict:
    if not items or len(items) > 50_000:  # Batch API limit is 50,000 requests per batch
        raise HTTPException(status_code=422, detail="Send 1..50000 items")
    lines = [{"custom_id": it.id, "method": "POST", "url": "/v1/chat/completions",
              "body": {"model": "gpt-4o-mini", "max_tokens": 20,
                       "messages": [{"role": "user", "content": f"HS chapter for: {it.text}"}]}}
             for it in items]
    return {"batch_id": await submit_batch(lines)}  # client keeps the id

@app.get("/classify-bulk/{batch_id}")
async def status(batch_id: str) -> dict:
    b = await client.batches.retrieve(batch_id)  # check status
    out = {"status": b.status, "counts": b.request_counts.model_dump() if b.request_counts else None}
    if b.status == "completed":  # include results
        ok, bad = await collect(b)
        out.update(results=ok, errors=bad)
    return out
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `abatch()` is a different thing: it runs many calls concurrently as normal live requests (not the discounted Batch API) and is limited by `max_concurrency`. For the real OpenAI Batch API, use the OpenAI SDK directly, then feed results back into a LangChain/LangGraph pipeline as the next step.

```python
from langchain_openai import ChatOpenAI  # model wrapper
from langchain_core.runnables import RunnableConfig  # config type

llm = ChatOpenAI(model="gpt-4o-mini")  # normal live model
cfg = RunnableConfig(max_concurrency=5)  # limit parallel live calls
# answers = await llm.abatch(["earbuds HS?", "shirt HS?"], config=cfg)  # live, full price
# For 50% discount: build JSONL + client.batches.create(...) as shown above.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming output lines keep the input order
✅ Correct: Match by `custom_id`.

```python
# Wrong: for p, row in zip(products, rows): ...   # misaligned results
# Right: results = {r["custom_id"]: ... for r in rows}; results[f"item-{i}"]
```

❌ Mistake 2: Using Batch API for user-facing requests
✅ Correct: Use live calls (or streaming) when a human waits.

```python
# Wrong: submit batch from a chat button and wait   # could take hours
# Right: live call for chat, batch for nightly/bulk work
```

---

## 🧠 Tricky Interview Question
**Q**: "Your batch finished with status `completed`, but 4% of items are missing from the output file. Is that a bug?"

**Answer**: No. `completed` means the batch finished processing; individual requests can still fail (invalid body, content issues, per-request errors). Failed lines appear in the `error_file_id` file (and `request_counts.failed` shows the count). Download both files, retry failed `custom_id`s, and make the pipeline idempotent. If the batch hits `expired`, partial results are available for finished requests; resubmit the rest.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the main benefit of the Batch API?
A1: A discount (about 50%) and a separate, higher rate-limit pool, in return for waiting up to 24 hours.

Q2: [Easy] What file format is used?
A2: JSONL: one JSON request object per line, each with a unique `custom_id`.

Q3: [Medium] What must each line contain?
A3: `custom_id`, `method` ("POST"), `url` (such as `/v1/chat/completions`), and `body` (the normal request payload).

Q4: [Medium] How do you know results belong to which input?
A4: By `custom_id`; the output order is not guaranteed.

Q5: [Hard] Design a nightly classification pipeline with the Batch API.
A5: Queue new records in a DB, split into batches under the request/file size limits, write JSONL with stable ids, submit and store batch ids, poll with a scheduler, download output and error files, upsert results idempotently by `custom_id`, retry failures with a new batch up to N times, alert on high failure rates, monitor cost with usage in outputs, and keep a live-call fallback for urgent items.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large offline jobs: classification, evals, tagging, summarising archives
- Results can wait hours
- You want lower cost

❌ Avoid when:
- Interactive features
- You need guaranteed fast completion (window is up to 24h)

---

## 📊 Visual Diagram
```
 your data --> requests.jsonl --> upload file --> create batch
                                                      |
                                       OpenAI processes in background
                                                      |
        poll status: in_progress ... completed        v
                                               output.jsonl + errors.jsonl
                                                      |
                              match by custom_id --> save to DB --> retry failures
```

---

## 💰 Cost Impact
- Token usage is the same as live calls, but the price is about 50% lower for both input and output tokens (check current pricing).
- Example (illustrative): 300,000 requests x 300 tokens in + 20 out on `gpt-4o-mini`: live about $16; batch about $8.
- Optimise further: short prompts, small `max_tokens`, small model, dedupe identical inputs before submitting, retry only failed lines.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Batch | Group of requests run async | Requests का समूह |
| JSONL | One JSON object per line | हर line में एक JSON |
| custom_id | Your unique request key | आपका unique key |
| completion_window | Max time to finish | पूरा होने की समय-सीमा |
| output_file_id | File with results | Results वाली file |
| error_file_id | File with failed requests | Failed requests की file |

---

## ⚡ 3-Line Summary
English: Batch API runs large JSONL jobs asynchronously in up to 24 hours at about half price. Match results using `custom_id` and retry failed lines. Never use it for live user requests.
Hindi: Batch API बड़े JSONL jobs को 24 घंटे तक में लगभग आधी कीमत पर चलाता है। Results `custom_id` से match करो और failed lines retry करो। Live user requests के लिए कभी नहीं।

---

## ➡️ Next Topic
**049. Model Fallback Strategy** — what to do when a model is down, slow or rate-limited.
