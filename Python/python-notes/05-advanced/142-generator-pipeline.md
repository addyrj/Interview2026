---

# 142. Generator Pipeline
# हिंदी में: Generator Pipeline (generators की chain जिसमें data एक-एक करके बहता है)

---

## 🔵 Simple Definition (English)
A generator pipeline connects several generators in a row: the output of one is the input of the next (`read → clean → filter → transform → write`). Data flows through the stages one item at a time, so memory stays tiny and work starts immediately. Nothing runs until the last stage asks for a value.

## 🔵 सरल परिभाषा (Hindi)
Generator pipeline में कई generators एक कतार में जुड़े होते हैं: एक का output अगले का input बनता है (`read → clean → filter → transform → write`)। Data हर stage से एक-एक item करके गुज़रता है, इसलिए memory बहुत कम लगती है और काम तुरंत शुरू हो जाता है। जब तक आखिरी stage value न माँगे, कुछ नहीं चलता।

---

## 🔴 Problem it Solves
A normal script builds a full list at every stage: read all lines, then a cleaned list, then a filtered list, then a transformed list. For a 20 GB file this means several copies in RAM. A generator pipeline needs only one item in memory at any moment and each stage stays a small, testable function.

## 🔴 यह क्यों बना? (Hindi)
सामान्य script हर stage पर पूरी list बनाती है: सारी lines पढ़ो, फिर cleaned list, फिर filtered list, फिर transformed list। 20 GB की file में यह RAM में कई copies बना देता है। Generator pipeline में किसी भी समय सिर्फ एक item memory में होता है और हर stage छोटा, test करने लायक function रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write each stage as a generator that takes an iterable and yields items
Step 2 → Connect them: stage3(stage2(stage1(source)))
Step 3 → Nothing runs yet; you only built the chain
Step 4 → A consumer (for loop / sum / list) pulls ONE item from the last stage
Step 5 → The pull travels backwards through every stage to the source
Step 6 → The item then flows forward through all stages; repeat for the next item
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर stage को ऐसा generator लिखो जो iterable ले और items yield करे
Step 2 → उन्हें जोड़ो: stage3(stage2(stage1(source)))
Step 3 → अभी कुछ नहीं चला, सिर्फ chain बनी है
Step 4 → Consumer (for loop / sum / list) आखिरी stage से एक item माँगता है
Step 5 → यह माँग पीछे की ओर हर stage से होती हुई source तक जाती है
Step 6 → फिर item सभी stages से आगे बढ़ता है; अगले item के लिए यही दोहराओ
```

---

## 🟡 Real World Example
A Razorpay nightly job processes a 15 GB payments log: `read_lines → parse_json → keep_failed → add_fee_info → write_to_db`. Each stage is a generator, so the job runs in 50 MB of RAM. An AI ingestion pipeline does `load_pdfs → split_chunks → embed_batches → upsert` in the same way, and can stop as soon as enough chunks are processed.

## 🟡 Real Example Hindi mein
Razorpay का nightly job 15 GB की payments log को `read_lines → parse_json → keep_failed → add_fee_info → write_to_db` से process करता है। हर stage generator है, इसलिए job सिर्फ 50 MB RAM में चलता है। AI ingestion pipeline में `load_pdfs → split_chunks → embed_batches → upsert` इसी तरह चलता है और ज़रूरत भर chunks बनते ही रुक भी सकता है।

---

## 💻 Code Example — Basic
```python
# Basic generator pipeline - every line commented
from collections.abc import Iterable, Iterator  # type hints


def numbers(limit: int) -> Iterator[int]:  # stage 1: source
    for n in range(1, limit + 1):  # produce 1..limit
        print(f"  produce {n}")  # trace when each item is made
        yield n  # give it to the next stage


def only_even(items: Iterable[int]) -> Iterator[int]:  # stage 2: filter
    for n in items:  # pull from previous stage
        if n % 2 == 0:  # keep even numbers only
            yield n  # pass it on


def squared(items: Iterable[int]) -> Iterator[int]:  # stage 3: transform
    for n in items:  # pull from previous stage
        yield n * n  # pass the square on


pipeline = squared(only_even(numbers(4)))  # build the chain, nothing runs yet
print("pipeline built")  # proves laziness
# Output: pipeline built

for value in pipeline:  # consumer pulls one item at a time
    print("got", value)  # use the final value
# Output:
#   produce 1
#   produce 2
# got 4
#   produce 3
#   produce 4
# got 16

# Same pipeline with generator expressions
src = (n for n in range(1, 7))  # source
evens = (n for n in src if n % 2 == 0)  # filter
squares = (n * n for n in evens)  # transform
print(sum(squares))  # consumer drives everything: 4 + 16 + 36
# Output: 56

# Stop early: only 2 items are ever produced
first_two = []  # collect results
for v in squared(only_even(numbers(1000))):  # huge source
    first_two.append(v)  # store
    if len(first_two) == 2:  # enough
        break  # stop - rest is never computed
print(first_two)  # result
# Output:
#   produce 1
#   produce 2
#   produce 3
#   produce 4
# [4, 16]
# (only 4 of 1000 items were produced - the rest never ran)
```

## 💻 Code Example — Advanced
```python
# Production style: log processing pipeline with typed stages and error handling
import io  # in-memory file for the demo
import json  # parse JSON lines
from collections import Counter  # count results
from collections.abc import Iterable, Iterator  # type hints
from itertools import islice  # take first N
from typing import Any  # dict typing

Event = dict[str, Any]  # type alias for one log event


def read_lines(f: Iterable[str]) -> Iterator[str]:  # stage 1: raw lines
    for line in f:  # file is already lazy
        line = line.strip()  # remove spaces/newline
        if line:  # skip blank lines
            yield line  # pass it on


def parse_json(lines: Iterable[str], stats: Counter[str]) -> Iterator[Event]:  # stage 2
    for line in lines:  # each raw line
        try:  # JSON may be invalid
            yield json.loads(line)  # good line -> dict
        except json.JSONDecodeError:  # bad line
            stats["bad_json"] += 1  # count it, do not crash


def only_status(events: Iterable[Event], status: str) -> Iterator[Event]:  # stage 3
    for e in events:  # each event
        if e.get("status") == status:  # match status
            yield e  # keep it


def add_fee(events: Iterable[Event], rate: float) -> Iterator[Event]:  # stage 4
    for e in events:  # each event
        yield {**e, "fee": round(e["amount"] * rate, 2)}  # new dict, no mutation


def batched(items: Iterable[Event], size: int) -> Iterator[list[Event]]:  # stage 5
    it = iter(items)  # make an iterator
    while chunk := list(islice(it, size)):  # take `size` items; stop on empty
        yield chunk  # one batch for a DB insert


raw = io.StringIO(  # fake log file
    '{"id": 1, "status": "failed", "amount": 500}\n'
    "not json\n"
    "\n"
    '{"id": 2, "status": "success", "amount": 900}\n'
    '{"id": 3, "status": "failed", "amount": 1200}\n'
    '{"id": 4, "status": "failed", "amount": 100}\n'
)
stats: Counter[str] = Counter()  # shared counters
pipeline: Iterator[list[Event]] = batched(  # outermost stage
    add_fee(only_status(parse_json(read_lines(raw), stats), "failed"), 0.02), 2
)
for batch in pipeline:  # drive the whole chain
    print([(e["id"], e["fee"]) for e in batch])  # pretend DB insert
# Output:
# [(1, 10.0), (3, 24.0)]
# [(4, 2.0)]
print(dict(stats))  # side statistics gathered along the way
# Output: {'bad_json': 1}


# Reusable composition helper
from functools import reduce  # fold stages together
from collections.abc import Callable  # type hint

Stage = Callable[[Iterable[int]], Iterator[int]]  # a stage maps iterable -> iterator


def compose(*stages: Stage) -> Stage:  # build a pipeline from stage functions
    def run(source: Iterable[int]) -> Iterator[int]:  # combined function
        return reduce(lambda acc, st: st(acc), stages, iter(source))  # feed output forward
    return run  # return it


def plus_one(xs: Iterable[int]) -> Iterator[int]:  # stage
    return (x + 1 for x in xs)  # add one


def times_ten(xs: Iterable[int]) -> Iterator[int]:  # stage
    return (x * 10 for x in xs)  # multiply


pipe = compose(plus_one, times_ten)  # stages run left to right
print(list(pipe([1, 2, 3])))  # (x+1)*10
# Output: [20, 30, 40]
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript arrays chain `map().filter().map()` but each step builds a **full new array**. Python generator pipelines are lazy, like Node streams or the newer JS iterator helpers (`Iterator.prototype.map`, available in recent runtimes).

```python
# Python way (lazy)
nums = range(1, 1_000_000_000)
result = (n * n for n in (n for n in nums if n % 2 == 0))
print(next(result))                 # 4  (instant, nothing else computed)
```
```javascript
// JavaScript way (array chain = eager)
const out = [1, 2, 3, 4].filter(n => n % 2 === 0).map(n => n * n);
console.log(out);                   // [4, 16]  (two intermediate arrays)
// Lazy JS needs generators or iterator helpers:
function* evens(xs) { for (const n of xs) if (n % 2 === 0) yield n; }
```

Key differences: JS array methods are eager and allocate arrays; Python generators stay lazy by default. In JS you reach for generators or streams to get the same behaviour.

---

## 🟠 FastAPI Connection
Pipelines power streaming exports in FastAPI: read database rows lazily, convert to CSV lines, send with `StreamingResponse`. The client starts receiving data before the last row is read, and memory stays small.

```python
# FastAPI: DB rows -> filter -> CSV lines -> streamed (pip install fastapi httpx)
from collections.abc import Iterable, Iterator  # type hints
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # test

app: FastAPI = FastAPI()  # app
ROWS: list[dict[str, int | str]] = [  # pretend DB table
    {"id": 1, "city": "Pune", "amount": 100},
    {"id": 2, "city": "Delhi", "amount": 250},
    {"id": 3, "city": "Pune", "amount": 75},
]


def fetch_rows() -> Iterator[dict[str, int | str]]:  # stage 1: DB cursor
    yield from ROWS  # a real app yields from a cursor


def by_city(rows: Iterable[dict[str, int | str]], city: str) -> Iterator[dict[str, int | str]]:
    return (r for r in rows if r["city"] == city)  # stage 2: filter


def to_csv(rows: Iterable[dict[str, int | str]]) -> Iterator[str]:  # stage 3: format
    yield "id,amount\n"  # header
    for r in rows:  # each row
        yield f"{r['id']},{r['amount']}\n"  # one line


@app.get("/export")  # GET /export?city=Pune
def export(city: str) -> StreamingResponse:  # endpoint
    return StreamingResponse(to_csv(by_city(fetch_rows(), city)), media_type="text/csv")


client = TestClient(app)  # client
print(client.get("/export?city=Pune").text)  # streamed body
# Output:
# id,amount
# 1,100
# 3,75
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Turning a stage into a list (breaks laziness)
```python
# Wrong - list() loads everything into memory
# cleaned = list(clean(read_lines(f)))

# Right - keep it a generator
# cleaned = clean(read_lines(f))
```

❌ Mistake 2: Reusing a pipeline after it is consumed
```python
# Wrong - second sum is 0
pipe = (n * 2 for n in range(3))
print(sum(pipe), sum(pipe))      # 6 0

# Right - build the pipeline again, or write a function that returns it
def make(): return (n * 2 for n in range(3))
print(sum(make()), sum(make()))  # 6 6
```

❌ Mistake 3: Swallowing errors silently or closing the file too early
```python
# Wrong - the file is closed before the lazy pipeline runs
# with open("log.txt") as f:
#     pipe = parse(read_lines(f))
# for x in pipe: ...        # ValueError: I/O operation on closed file

# Right - consume the pipeline INSIDE the with block
# with open("log.txt") as f:
#     for x in parse(read_lines(f)): ...
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def a():
    for i in range(3):
        print("a", i)
        yield i

def b(src):
    for x in src:
        print("b", x)
        yield x * 10

p = b(a())
print("start")
print(next(p))
print(next(p))
```

**Answer**:
```
start
a 0
b 0
0
a 1
b 1
10
```
Nothing prints until the first `next(p)`. Each `next` pulls exactly one item through both stages, so the trace lines interleave per item, not stage by stage. The second `next` continues exactly where each generator was paused.

---

## ⚫ Interview Questions + Answers

Q1: Why are generator pipelines memory efficient?
A1: Each stage holds one item at a time. No intermediate list exists, so memory is O(1) per stage instead of O(n).

Q2: When does the work actually happen?
A2: When the final consumer (a `for` loop, `sum`, `list`, `next`) pulls values. Building the chain does no work.

Q3: How can you stop a pipeline early?
A3: `break` from the loop, use `itertools.islice`, or call `.close()`. Upstream stages are then never asked for more.

Q4: How do you debug a pipeline?
A4: Test each stage separately with a small list. Add a pass-through `peek` stage that prints and yields the same item.

Q5: Pipeline of generators or `asyncio` queues?
A5: Generators are single-threaded and synchronous: simple and fast for CPU/file work. For network I/O and concurrency use async generators or queues.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Data is large (files, logs, DB cursors, API pages)
- Processing is a sequence of independent steps
- You may stop early (take first N, first match)

❌ Avoid when:
- You need sorting, grouping or the total count before output (they need all data)
- Stages must run in parallel (use multiprocessing or async)
- Data is tiny and a list comprehension is clearer

---

## 📊 Visual Diagram

```
 source ─► read_lines ─► parse_json ─► only_failed ─► add_fee ─► batched ─► consumer
   ▲          ▲             ▲             ▲            ▲          ▲          │
   └──────────┴─────────────┴─────────────┴────────────┴──────────┴── pull ──┘
        (consumer asks for one item; request travels left,
         the item travels right through every stage)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipeline | Chain of processing stages | processing stages की chain |
| Stage | One generator in the chain | chain का एक generator |
| Pull model | Consumer asks, producers respond | consumer माँगता है, producer देता है |
| Backpressure | Slow consumer naturally slows producers | धीमा consumer producers को भी धीमा करता है |
| Laziness | Work happens only when needed | ज़रूरत पर ही काम |
| Batching | Grouping items for efficiency | items को group करना |

---

## ⚡ 3-Line Summary
English: A generator pipeline chains small generators so each item flows through all stages one at a time. Memory stays small and work starts instantly. The consumer at the end pulls data through the chain.
Hindi: Generator pipeline छोटे generators को जोड़ती है ताकि हर item सभी stages से एक-एक करके गुज़रे। Memory कम लगती है और काम तुरंत शुरू होता है। अंत का consumer data को chain में से खींचता है।

---

## ➡️ Next Topic
**143. Coroutines Basics** — generators that receive data, the step before `async`/`await`.
