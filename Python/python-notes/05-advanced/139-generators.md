---

# 139. Generators — Complete Guide
# हिंदी में: Generators — पूरी Guide

---

## 🔵 Simple Definition (English)
A generator is a special function that uses `yield` instead of `return`. It produces values one at a time — pausing execution after each `yield` and resuming from the same point when the next value is requested. Generators are lazy: they compute values on-demand without storing all values in memory.

## 🔵 सरल परिभाषा (Hindi)
Generator एक special function है जो `return` की जगह `yield` use करता है। एक बार में एक value produce करता है — हर `yield` के बाद pause करता है और अगली बार वहीं से resume करता है। Generators lazy हैं: सभी values memory में store नहीं होतीं, on-demand calculate होती हैं।

---

## 🔴 Problem it Solves
Reading a 10 GB CSV file into a list: crashes your server (10 GB in RAM). Processing one million DB rows: `fetchall()` loads all into memory. Generating an infinite sequence: impossible with a list. Generators solve all three — process one item at a time, memory stays O(1).

## 🔴 यह क्यों बना? (Hindi)
10 GB CSV file list में load करो: server crash। 1 million DB rows `fetchall()`: सब RAM में। Infinite sequence list से impossible। Generator = एक time में एक item, memory O(1) रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call generator function → returns a generator OBJECT (doesn't run code!)
Step 2 → Call next() on generator object → code runs until it hits yield
Step 3 → yield sends the value out + SUSPENDS execution (saves entire stack frame)
Step 4 → Call next() again → resumes from exactly after the last yield
Step 5 → When function ends or hits return → raises StopIteration automatically
Step 6 → for loop catches StopIteration → stops cleanly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Generator function call करो → generator object मिलता है (code नहीं चलता!)
Step 2 → next() call करो → code yield तक चलता है
Step 3 → yield: value बाहर भेजता है + execution suspend (stack frame save हो जाता है)
Step 4 → next() फिर call करो → last yield के बाद से resume
Step 5 → Function खत्म → automatically StopIteration raise
Step 6 → for loop StopIteration पकड़ता है → cleanly stop
```

---

## 🟡 Real World Example
Razorpay processes millions of transactions daily. To generate a monthly report: `Transaction.objects.all()` would load millions of rows. Using a generator, you process and write one transaction at a time to CSV — memory stays at ~1KB regardless of whether there are 1K or 100M transactions.

## 🟡 Real Example Hindi mein
Razorpay daily millions of transactions। Monthly report: `Transaction.objects.all()` = सब RAM में। Generator से: एक-एक transaction CSV में write करो — memory 1KB रहती है चाहे 1K transactions हों या 100M।

---

## 💻 Code Example — Basic
```python
# Basic generator — counts up to n
from typing import Generator

def count_up(n: int) -> Generator[int, None, None]:  # yields int, no send, no return
    """Generates numbers from 0 to n-1."""
    print("Generator started!")          # runs only when first next() is called
    for i in range(n):
        print(f"  About to yield {i}")
        yield i                          # pause here, send i to caller
        print(f"  Resumed after yield {i}")  # runs after caller requests next
    print("Generator done!")             # runs after last yield

# Creating generator object (NO code runs yet!)
gen = count_up(3)
print(type(gen))    # <class 'generator'>

# Manual next() calls:
print(next(gen))    # "Generator started!" + "About to yield 0" → 0
print(next(gen))    # "Resumed after yield 0" + "About to yield 1" → 1
print(next(gen))    # "Resumed after yield 1" + "About to yield 2" → 2
# next(gen) → "Generator done!" then raises StopIteration

# Using in for loop (cleanest way):
for value in count_up(5):
    print(value)    # 0, 1, 2, 3, 4 — for loop handles StopIteration internally
```

## 💻 Code Example — Advanced
```python
# Production patterns: file processing + generator pipeline
import csv
from pathlib import Path
from typing import Generator, Iterator
from dataclasses import dataclass

@dataclass
class Transaction:
    id: str
    amount: float
    user_id: str
    status: str

def read_transactions_csv(path: Path) -> Generator[dict, None, None]:
    """Read CSV lazily — one row at a time. Memory: O(1) regardless of file size."""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row               # pause and yield each row — file stays open during iteration

def parse_transaction(row: dict) -> Transaction:
    """Convert raw dict to typed Transaction."""
    return Transaction(
        id=row['id'],
        amount=float(row['amount']),
        user_id=row['user_id'],
        status=row['status']
    )

def filter_completed(transactions: Iterator[Transaction]) -> Generator[Transaction, None, None]:
    """Generator that filters — passes only completed transactions."""
    for txn in transactions:
        if txn.status == 'completed':
            yield txn               # only yield completed ones

def compute_totals(transactions: Iterator[Transaction]) -> Generator[tuple, None, None]:
    """Generator that computes running total per user."""
    totals: dict[str, float] = {}
    for txn in transactions:
        totals[txn.user_id] = totals.get(txn.user_id, 0) + txn.amount
        yield (txn.user_id, totals[txn.user_id])  # yield after each update

# GENERATOR PIPELINE — each step is lazy:
# read_transactions_csv → parse → filter → compute
# Data flows through one item at a time!

def process_report(csv_path: Path) -> dict[str, float]:
    """Process a 10GB CSV file using generator pipeline — ~constant memory."""
    raw_rows = read_transactions_csv(csv_path)              # lazy
    transactions = (parse_transaction(row) for row in raw_rows)  # generator expression!
    completed = filter_completed(transactions)              # lazy filter
    
    # Only here do we actually pull all data through:
    user_totals: dict[str, float] = {}
    for user_id, running_total in compute_totals(completed):
        user_totals[user_id] = running_total    # just track last value per user
    
    return user_totals

# yield from — delegate to sub-generator:
def chain_generators(*iterables) -> Generator:
    """Combine multiple generators into one."""
    for iterable in iterables:
        yield from iterable     # yield from = yield each item from sub-generator

result = list(chain_generators([1, 2], [3, 4], [5]))
print(result)    # [1, 2, 3, 4, 5]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python generator:
def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:                 # infinite generator!
        yield a
        a, b = b, a + b

gen = fibonacci()
print([next(gen) for _ in range(8)])  # [0, 1, 1, 2, 3, 5, 8, 13]

# Generator expression (like list comprehension but lazy):
squares = (x**2 for x in range(1_000_000))  # NO memory used yet
first_10 = [next(squares) for _ in range(10)]  # only computes 10 values
```

```javascript
// JavaScript generator (very similar syntax!):
function* fibonacci() {
    let [a, b] = [0, 1];
    while (true) {
        yield a;
        [a, b] = [b, a + b];
    }
}

const gen = fibonacci();
const first8 = Array.from({length: 8}, () => gen.next().value);
console.log(first8); // [0, 1, 1, 2, 3, 5, 8, 13]

// Python 'generator expression' → JS has no direct equivalent
// Python: (x**2 for x in range(10)) — lazy
// JS: you'd need a generator function or Array.from with lazy logic
```

---

## 🟠 FastAPI Connection

```python
# FastAPI: streaming large responses with generators
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import csv
import io
from typing import AsyncGenerator

app = FastAPI()

async def generate_csv_rows() -> AsyncGenerator[str, None]:
    """Async generator — yields CSV rows one at a time.
    Client gets data as it streams — no waiting for full file."""
    yield "id,name,amount\n"                    # header row first
    
    # Simulate DB query (replace with actual async DB query)
    for i in range(1, 100_001):                  # 100K rows
        yield f"{i},User{i},{i * 9.99:.2f}\n"  # yield one row at a time
        
        # In production with asyncpg:
        # async for row in conn.cursor("SELECT id,name,amount FROM transactions"):
        #     yield f"{row['id']},{row['name']},{row['amount']}\n"

@app.get("/export/transactions")
async def export_transactions():
    """Stream 100K rows to client — server memory stays minimal."""
    return StreamingResponse(
        generate_csv_rows(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )
# Client receives data chunk by chunk — no timeout, no memory explosion
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to use a generator twice
```python
# Wrong — generator is exhausted after one iteration!
gen = (x**2 for x in range(5))
print(list(gen))    # [0, 1, 4, 9, 16] ✅
print(list(gen))    # [] ← EMPTY! Generator is exhausted

# Correct — recreate if you need it again:
def squares(n: int):
    return (x**2 for x in range(n))   # function creates fresh generator each call
print(list(squares(5)))   # [0, 1, 4, 9, 16]
print(list(squares(5)))   # [0, 1, 4, 9, 16] ✅ fresh generator
```

❌ Mistake 2: Confusing generator function with generator object
```python
# Wrong understanding:
def my_gen():
    yield 1
    yield 2

my_gen()           # This creates a generator object but THROWS IT AWAY!
# Nothing printed — the function body hasn't run at all!

# Correct:
gen = my_gen()     # assign the generator object
print(next(gen))   # 1
print(next(gen))   # 2
```

❌ Mistake 3: Using list() when you should stay lazy
```python
# Wrong — defeats the purpose:
big_data = list(read_huge_csv("10gb.csv"))   # loads 10GB into RAM!
process(big_data)

# Correct — stay lazy through the pipeline:
for row in read_huge_csv("10gb.csv"):
    process(row)                              # process one row at a time
```

---

## 🧠 Tricky Interview Question

```python
# What will this print?
def gen():
    print("start")
    x = yield 1          # yield AND receive a sent value!
    print(f"got: {x}")
    yield 2

g = gen()
print(next(g))           # A
print(g.send("hello"))   # B
```
Answer:
- `next(g)` → runs until `yield 1` → prints "start", returns `1` → **A prints: start, then 1**
- `g.send("hello")` → resumes, assigns `"hello"` to `x` → runs until `yield 2` → prints "got: hello", returns `2` → **B prints: got: hello, then 2**

`send()` is a two-way channel: you can both receive from and send values into a generator. This is how coroutines worked before `async/await`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a generator and a list?
A1: A list stores all values in memory at once (eager). A generator produces values one at a time on demand (lazy). List: O(n) memory, O(1) random access. Generator: O(1) memory, forward-only (no random access, can't rewind). Use generators for large/infinite data; lists when you need random access or reuse values.

Q2: What is `yield from`?
A2: `yield from iterable` is equivalent to `for item in iterable: yield item` but more efficient (C-level loop, no Python overhead). It also properly forwards `.send()`, `.throw()`, and `.close()` to the sub-generator — critical for coroutine delegation. Used to compose generators and build generator pipelines.

Q3: What is a generator expression vs list comprehension?
A3: `[x**2 for x in range(n)]` — list comprehension → creates a list immediately, O(n) memory. `(x**2 for x in range(n))` — generator expression → creates a generator object, O(1) memory, lazy. Use `()` instead of `[]`. Pass generator expressions directly to functions: `sum(x**2 for x in range(n))` — no need for `[]`.

Q4: How does `send()` work with generators?
A4: `send(value)` resumes the generator AND passes `value` as the result of the `yield` expression inside the generator. First call must be `next()` or `send(None)` — you can't send a value to a generator that hasn't started yet. This bidirectional communication was the basis for Python's coroutines before `async/await`.

Q5: How are generators related to `async/await` in Python?
A5: Python's `async/await` is built on generators. An `async def` function is a coroutine — which is a generator-based state machine under the hood. `await expr` is equivalent to `yield from expr` in a coroutine context. The event loop calls `send()` on coroutines to resume them after I/O completes. `asyncio` is the framework that manages the event loop.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Processing large files (logs, CSVs, database exports) without loading into memory
- Infinite sequences (Fibonacci, streaming data, event streams)
- Building lazy data pipelines (read → filter → transform → aggregate)
- Streaming HTTP responses (FastAPI StreamingResponse)
- When you need to generate many items but the caller might stop early (saves computation)

❌ Avoid when:
- You need random access by index (use a list)
- You need to iterate the data multiple times (generators are single-pass)
- Data is small enough to fit in memory AND you need to reuse it
- You need `len()` — generators have no length

---

## 📊 Visual Diagram
```
List:                           Generator:
┌───────────────────────┐      
│ [0,1,4,9,16,25,...] ← │      gen = (x**2 for x...)
│  All in memory NOW!    │      
│  O(n) memory          │       next() → computes 0,  yields 0
└───────────────────────┘       next() → computes 1,  yields 1
                                next() → computes 4,  yields 4
                                ... only when asked
                                O(1) memory

Generator Pipeline:
read_csv() → filter() → transform() → aggregate()
    ↓             ↓           ↓             ↓
  lazy          lazy         lazy       pulls data
One row flows through all stages before the next row starts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| yield | Pause and send value to caller | रुको और caller को value दो |
| Generator object | Object returned by generator function | Generator function का return |
| lazy evaluation | Compute only when needed | जब जरूरत हो तब compute करो |
| StopIteration | Exception when generator is exhausted | Generator खत्म होने पर exception |
| yield from | Delegate to sub-generator | Sub-generator को delegate करो |
| send() | Resume + pass value into generator | Resume करो + value अंदर भेजो |
| Generator expression | `(expr for x in iterable)` — lazy | `()` वाला list comprehension |

---

## ⚡ 3-Line Summary
English: A generator uses `yield` to produce values one at a time — code pauses at each yield and resumes on the next `next()` call. This gives O(1) memory for arbitrarily large data streams. Generator expressions `(expr for x in ...)` are lazy alternatives to list comprehensions.
Hindi: Generator `yield` से एक-एक value produce करता है — हर yield पर pause, next() पर resume। Memory O(1) रहती है। Generator expression `()` list comprehension का lazy alternative है।

---

## ➡️ Next Topic
**140. yield Statement — Deep Dive** — `yield` vs `return`, `send()` protocol, bidirectional generators, coroutine foundations. Then **141. yield from** for generator delegation.
