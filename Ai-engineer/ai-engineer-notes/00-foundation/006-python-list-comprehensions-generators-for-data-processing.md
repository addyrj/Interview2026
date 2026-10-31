---

# 006. Python List Comprehensions + Generators for Data Processing
# हिंदी में: Data Processing के लिए List Comprehensions + Generators

---

## 🔵 Simple Definition (English)
A list comprehension builds a list in one line: `[f(x) for x in data if cond]`. A generator produces items one at a time and remembers its place (`yield`), so it uses almost no memory. In AI work, generators stream huge files, create chunk batches and stream LLM tokens.

## 🔵 सरल परिभाषा (Hindi)
List comprehension एक line में list बनाती है: `[f(x) for x in data if cond]`। Generator items एक-एक करके देता है और अपनी जगह याद रखता है (`yield`), इसलिए memory लगभग नहीं लगती। AI में generators बड़ी files stream करने, chunk batches बनाने और LLM tokens stream करने में काम आते हैं।

---

## 🔴 Problem it Solves
Loading a 5 GB tariff CSV or 1 million chunks into a list crashes memory. Writing long `for` loops with `append` is noisy. Comprehensions make transforms short and fast; generators process data lazily (one piece at a time), which is exactly what embedding pipelines and streaming APIs need.

## 🔴 यह क्यों बना? (Hindi)
5 GB की tariff CSV या 10 लाख chunks को list में लोड करने से memory crash होती है। `append` वाले लंबे `for` loops शोर जैसे लगते हैं। Comprehension transforms को छोटा और तेज़ बनाती है; generators data को lazily (एक-एक टुकड़ा) process करते हैं, जो embedding pipelines और streaming APIs की ज़रूरत है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List comprehension: [expr for item in iterable if condition] builds the full list NOW
Step 2 → Generator expression: (expr for item in iterable) builds NOTHING yet, only a recipe
Step 3 → Generator function: a def with `yield`; calling it returns a generator object
Step 4 → Each next() runs the function until the next `yield`, hands the value, pauses
Step 5 → State (local variables) is preserved between yields
Step 6 → When the function ends, StopIteration is raised; a for-loop handles it silently
Step 7 → Chain generators into a pipeline: read -> clean -> chunk -> batch -> embed (constant memory)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → List comprehension: [expr for item in iterable if condition] पूरी list अभी बना देती है
Step 2 → Generator expression: (expr for item in iterable) अभी कुछ नहीं बनाती, सिर्फ़ recipe है
Step 3 → Generator function: `yield` वाला def; call करने पर generator object मिलता है
Step 4 → हर next() अगले `yield` तक चलता है, value देता है, रुक जाता है
Step 5 → yields के बीच local variables की state बची रहती है
Step 6 → Function खत्म होने पर StopIteration; for-loop इसे चुपचाप संभालता है
Step 7 → Generators को जोड़कर pipeline: read -> clean -> chunk -> batch -> embed (constant memory)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The government tariff schedule has 500K rows. A generator reads one row at a time, a comprehension-style filter keeps only chapter 85 rows, another generator groups rows into batches of 100, and each batch is sent to the embedding API. Memory stays flat at a few MB.

**Amazon AI**: Millions of product reviews are streamed from S3, cleaned, de-duplicated, and sent for summarisation in batches without ever holding all reviews in memory.

## 🟡 Real Example Hindi mein
**Tariff System**: Tariff schedule में 5 लाख rows हैं। Generator एक-एक row पढ़ता है, filter सिर्फ़ chapter 85 की rows रखता है, दूसरा generator 100-100 के batches बनाता है और हर batch embedding API को जाता है। Memory कुछ MB पर स्थिर रहती है।

**Amazon AI**: करोड़ों product reviews S3 से stream होकर clean, de-duplicate और batches में summarise होते हैं, सब reviews memory में कभी एक साथ नहीं आते।

---

## 💻 Code Example — Basic
```python
# Basic comprehensions and generators - pure Python, runs directly
import sys  # to compare memory sizes

codes = ["8517", "8471", "6403", "8528", "0901"]  # sample HS codes

chapter_85 = [c for c in codes if c.startswith("85")]  # list comprehension with filter
print(chapter_85)  # ['8517', '8528']

labels = {c: f"HS-{c}" for c in codes}  # dict comprehension
print(labels["8517"])  # HS-8517

unique_chapters = {c[:2] for c in codes}  # set comprehension (first 2 digits)
print(sorted(unique_chapters))  # ['06', '09', '84', '85']

big_list = [i for i in range(1_000_000)]  # builds 1M ints in memory
big_gen = (i for i in range(1_000_000))  # generator expression: lazy, tiny
print(sys.getsizeof(big_list) > sys.getsizeof(big_gen))  # True

def batches(items: list[str], size: int):  # generator function
    for start in range(0, len(items), size):  # step through the list
        yield items[start:start + size]  # hand out one batch, then pause

for batch in batches(codes, 2):  # pulls batches lazily
    print(batch)  # ['8517','8471'], ['6403','8528'], ['0901']

print(sum(x * x for x in range(5)))  # 30, generator inside sum() needs no extra list
```

## 💻 Code Example — Advanced
```python
# Production pipeline: streaming file -> clean -> chunk -> batch -> async embed (mock)
import asyncio  # async runtime
import csv  # read CSV rows lazily
import io  # in-memory file for the demo
from typing import AsyncIterator, Iterable, Iterator  # generator types

SAMPLE = "code,description\n8517,Smartphone\n8517,  smartphone  \n6403,Leather shoes\n8528,Television\n"  # demo data


def read_rows(f: io.TextIOBase) -> Iterator[dict[str, str]]:  # lazy row reader
    for row in csv.DictReader(f):  # DictReader itself is lazy
        yield row  # one row at a time


def clean(rows: Iterable[dict[str, str]]) -> Iterator[dict[str, str]]:  # normalise + dedupe
    seen: set[tuple[str, str]] = set()  # remember what we saw
    for row in rows:  # pull lazily from previous stage
        desc = " ".join(row["description"].split()).lower()  # collapse spaces, lowercase
        key = (row["code"], desc)  # dedupe key
        if key in seen:  # duplicate
            continue  # skip it (saves embedding tokens)
        seen.add(key)  # remember
        yield {"code": row["code"], "description": desc}  # cleaned row


def batched(items: Iterable[dict[str, str]], size: int) -> Iterator[list[dict[str, str]]]:  # group rows
    batch: list[dict[str, str]] = []  # current batch
    for item in items:  # pull lazily
        batch.append(item)  # add to batch
        if len(batch) == size:  # batch full
            yield batch  # emit
            batch = []  # start a new one
    if batch:  # leftover rows
        yield batch  # emit the last partial batch


async def embed_batch(texts: list[str]) -> list[list[float]]:  # mock embedding API
    await asyncio.sleep(0.01)  # pretend network time
    return [[float(len(t))] for t in texts]  # fake 1-d vectors


async def embed_stream(batches: Iterable[list[dict[str, str]]]) -> AsyncIterator[tuple[str, list[float]]]:  # async generator
    for batch in batches:  # sync iteration over lazy batches
        try:  # protect each API call
            vectors = await embed_batch([r["description"] for r in batch])  # one call per batch
        except Exception as exc:  # do not kill the whole pipeline
            print("batch failed:", exc)  # log and continue
            continue  # skip failed batch
        for row, vec in zip(batch, vectors):  # pair rows with vectors
            yield row["code"], vec  # stream results out


async def main() -> None:  # demo
    rows = clean(read_rows(io.StringIO(SAMPLE)))  # build the lazy pipeline (nothing runs yet)
    async for code, vec in embed_stream(batched(rows, size=2)):  # pull results
        print(code, vec)  # 8517, 6403, 8528 (duplicate removed)


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Generators power `StreamingResponse`: FastAPI iterates your generator and sends each yielded piece immediately, so large exports and token streams start fast and use little memory.

```python
# FastAPI + generator: stream a big export as NDJSON lines
import json  # encode lines
from collections.abc import Iterator  # type
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming response

app = FastAPI()  # app


def rows() -> Iterator[dict]:  # pretend this reads from DB lazily
    for i in range(5):  # 5 demo rows
        yield {"id": i, "hs_code": f"85{i:02d}"}  # one row


def to_ndjson() -> Iterator[str]:  # transform each row into a text line
    for row in rows():  # lazily iterate
        yield json.dumps(row) + "\n"  # newline-delimited JSON


@app.get("/export")  # route
def export() -> StreamingResponse:  # sync generator is run in a threadpool by Starlette
    return StreamingResponse(to_ndjson(), media_type="application/x-ndjson")  # starts sending immediately
```

---

## 🔗 LangChain / LangGraph Connection
`chain.stream()` / `chain.astream()` return generators of chunks; `llm.batch()` takes lists. Document loaders offer `lazy_load()` (a generator) so big corpora are not loaded at once. LangGraph `graph.stream()` yields state updates step by step.

```python
# LangChain lazy loading + streaming (needs langchain-community and an API key for the LLM part)
from langchain_core.documents import Document  # doc type


def lazy_docs(texts: list[str]):  # generator of Documents, same idea as loader.lazy_load()
    for i, t in enumerate(texts):  # iterate
        yield Document(page_content=t, metadata={"row": i})  # one doc at a time


for doc in lazy_docs(["Smartphone", "Shoes"]):  # consume lazily
    print(doc.metadata["row"], doc.page_content)  # 0 Smartphone / 1 Shoes

# for chunk in chain.stream({"item": "phone"}):  # token streaming is a generator too
#     print(chunk.content, end="")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a list comprehension for huge data
✅ Correct: use a generator expression.

```python
# Wrong: builds 10M items in memory first
total = sum([len(line) for line in open("tariff.csv")])
# Right: lazy, constant memory
total = sum(len(line) for line in open("tariff.csv"))
```

❌ Mistake 2: Consuming a generator twice
✅ Correct: generators are single-use; recreate or convert to a list once.

```python
# Wrong: the second loop prints nothing
gen = (c for c in ["8517", "6403"])
print(list(gen))   # ['8517', '6403']
print(list(gen))   # [] - exhausted!
# Right: build a new generator, or keep a list if you need reuse
```

❌ Mistake 3: Over-nested comprehensions that nobody can read. If it has more than two `for`/`if` parts, use a normal loop or a helper function.

---

## 🧠 Tricky Interview Question

**Q**: "`results = (call_llm(x) for x in items)` and you expected 1000 LLM calls to be fired, but nothing happened and no tokens were billed. Why? And how would you then run them concurrently?"

**Answer**: A generator expression is lazy; nothing executes until something iterates it. Also, if `call_llm` is `async`, the generator only creates coroutine objects that still need `await`. To run them: `await asyncio.gather(*(call_llm(x) for x in items))` (with a semaphore to limit concurrency). Note that `gather(*gen)` creates all 1000 coroutines immediately, so for very large inputs process in batches to keep memory and rate limits under control.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `[x for x in a]` and `(x for x in a)`? (Easy)
A1: The first builds a full list in memory immediately; the second is a lazy generator that produces one item per request and uses constant memory.

Q2: What does `yield` do? (Easy)
A2: It returns a value to the caller and pauses the function, keeping its local state. The next `next()` call resumes right after the `yield`.

Q3: When is a list comprehension better than a generator? (Medium)
A3: When you need the result more than once, need `len()`, indexing, or sorting, or the data is small. Lists are also slightly faster for small data because of lower overhead.

Q4: How do you batch a large iterable for embedding calls? (Medium)
A4: Write a `batched` generator (or `itertools.batched` in Python 3.12+) that collects `size` items and yields lists. Pick batch size based on API limits (e.g. up to 2048 inputs per OpenAI embeddings request, and a total token cap per request). Process batches with bounded concurrency.

Q5: How would you stream LLM tokens through FastAPI and what pitfall exists? (Hard)
A5: Use an async generator that does `async for chunk in client.chat.completions.create(..., stream=True)` and yields `data: ...\n\n` lines in a `StreamingResponse` (media type `text/event-stream`). Pitfalls: errors after the first byte cannot change the 200 status, so send an error event; reverse proxies (nginx) may buffer unless you disable buffering; and on client disconnect you must stop the upstream stream to avoid paying for unread tokens. Usage stats are only included at the end when you request `stream_options={"include_usage": True}`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Transforming or filtering small to medium lists (comprehension)
- Processing files/rows/chunks too big for memory (generator)
- Building ETL pipelines for embeddings and streaming responses

❌ Avoid when:
- You need random access, `len()`, or multiple passes (use a list)
- The comprehension is so complex it hurts readability
- Debugging: lazy pipelines can make stack traces harder to follow

---

## 📊 Visual Diagram
```
 LIST (eager)                      GENERATOR (lazy pipeline)
 [ r1 r2 r3 ... r1M ]              read_rows -> clean -> batched -> embed
   all in memory                      │          │         │         │
   memory = O(N)                      r1 ───────>r1' ────> [r1'..r100] ──> API
                                      (one item flows at a time)
                                      memory = O(batch size)
```

---

## 💰 Cost Impact
Generators do not change token pricing, but pipelines built with them let you cut tokens before calling the API: dedupe, filter irrelevant rows and trim whitespace lazily before embedding. Example: 500K rows at 40 tokens each = 20M tokens; at $0.02 per 1M tokens (text-embedding-3-small) that is about $0.40. Removing 30 percent duplicates saves about $0.12 per run, and with larger models the saving grows. Batching reduces request count and latency, not tokens, but stays within rate limits. Memory savings also reduce server size and cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| List comprehension | One-line list builder | एक line में list बनाना |
| Generator | Lazy producer of values | lazily values देने वाला |
| yield | Return value and pause | value देकर रुकना |
| Lazy evaluation | Compute only when needed | ज़रूरत पर ही गणना |
| Exhausted | Generator has no more items | generator खत्म |
| Batch | Group of items processed together | items का समूह |
| Pipeline | Chain of processing stages | processing stages की श्रृंखला |
| Streaming | Send data piece by piece | टुकड़ों में भेजना |

---

## ⚡ 3-Line Summary
English: Comprehensions build lists concisely; generators produce items lazily with constant memory. Chain generators to stream, clean, dedupe and batch large datasets before calling LLM or embedding APIs. Remember generators are single-use.
Hindi: Comprehensions छोटे code में list बनाती हैं; generators constant memory में items lazily देते हैं। बड़े datasets को LLM या embedding APIs से पहले generators से stream, clean, dedupe और batch करो। Generators सिर्फ़ एक बार use होते हैं।

---

## ➡️ Next Topic
**007. FastAPI Route Creation** — now that Python basics are ready, we build the first API endpoints for the tariff system.
