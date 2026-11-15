---

# 479. Implement Generator
# हिंदी में: Generator बनाना (yield)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A generator is a function that uses `yield` to hand back values one at a time and pause. When asked again it resumes exactly where it stopped, keeping its local variables. It is the easiest way to write an iterator.

## 🔵 सरल परिभाषा (Hindi)
Generator ऐसा function है जो `yield` से एक-एक value देकर रुक जाता है। दोबारा माँगने पर वह ठीक वहीं से चलता है जहाँ रुका था, local variables के साथ। Iterator लिखने का यह सबसे आसान तरीका है।

---

## 🔴 Problem it Solves
Building a full list for large or endless data wastes memory and delays the first result. Writing an iterator class needs boilerplate (`__iter__`, `__next__`, state fields). A generator gives lazy evaluation and automatic state-saving in a few lines, and lets you chain steps into pipelines.

## 🔴 यह क्यों बना? (Hindi)
बड़े या अनंत data की पूरी list बनाना memory बर्बाद करता है और पहला नतीजा देर से मिलता है। Iterator class लिखने में boilerplate (`__iter__`, `__next__`, state fields) लगता है। Generator कुछ ही लाइनों में lazy evaluation और अपने-आप state सहेजना देता है, और steps को pipeline में जोड़ने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Calling a generator function does NOT run the body; it returns a generator object
Step 2 → next(gen) runs the body until the first `yield value`
Step 3 → The value is returned; the function is frozen with all locals intact
Step 4 → The next next(gen) resumes right after the yield
Step 5 → When the body ends (or `return`), StopIteration is raised automatically
Step 6 → gen.send(x) resumes and makes the `yield` expression evaluate to x
Step 7 → `yield from sub` delegates to another iterable; gen.close() runs finally blocks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Generator function बुलाने पर body नहीं चलती; generator object मिलता है
Step 2 → next(gen) पहले `yield value` तक body चलाता है
Step 3 → Value लौटती है; function सारे locals के साथ रुक (freeze) जाता है
Step 4 → अगला next(gen) yield के ठीक बाद से चलता है
Step 5 → Body खत्म होने (या `return`) पर StopIteration अपने-आप raise होता है
Step 6 → gen.send(x) चलाकर `yield` expression की value x बना देता है
Step 7 → `yield from sub` दूसरे iterable को सौंप देता है; gen.close() finally blocks चलाता है
```

---

## 🟡 Real World Example
Reading a 10 GB server log and counting `ERROR` lines without loading the file. A pipeline `read_lines -> clean -> filter_errors -> parse` where each stage is a generator. Streaming a CSV export from a Swiggy orders table. Generating unique IDs. Chunking a million records into batches of 500 for bulk inserts.

## 🟡 Real Example Hindi mein
10 GB server log पढ़कर `ERROR` lines गिनना, बिना file memory में लोड किए। `read_lines -> clean -> filter_errors -> parse` जैसी pipeline जहाँ हर stage एक generator है। Swiggy orders table से CSV export stream करना। Unique IDs बनाना। दस लाख records को 500-500 के batches में बाँटकर bulk insert करना।

---

## 💻 Code Example — Basic
```python
# Basic generators
from typing import Iterator                    # return type

def countdown(n: int) -> Iterator[int]:
    while n > 0:                               # loop while numbers remain
        yield n                                # pause here and hand out n
        n -= 1                                 # resume here on the next request

gen = countdown(3)                             # nothing runs yet
print(next(gen))                               # runs to the first yield
print(next(gen))                               # resumes, runs to the next yield
print(list(gen))                               # consume the rest

squares = (x * x for x in range(4))            # generator expression
print(sum(squares))                            # 0+1+4+9, computed lazily
print(sum(squares))                            # already exhausted -> 0

# Output:
# 3
# 2
# [1]
# 14
# 0
```

## 💻 Code Example — Advanced
```python
# Production style: pipeline, send(), yield from, chunking, cleanup (tests in main.py)
from itertools import islice
from typing import Generator, Iterable, Iterator


def read_lines(lines: Iterable[str]) -> Iterator[str]:
    for ln in lines:                           # stage 1: clean each line
        yield ln.strip()

def only_errors(lines: Iterable[str]) -> Iterator[str]:
    return (ln for ln in lines if "ERROR" in ln)   # stage 2: filter lazily

def chunked(it: Iterable[int], size: int) -> Iterator[list[int]]:
    iterator = iter(it)                        # one shared iterator
    while chunk := list(islice(iterator, size)):   # take `size` items; stop when empty
        yield chunk

def running_average() -> Generator[float, float, None]:
    total, count, avg = 0.0, 0, 0.0            # state lives inside the generator
    while True:
        x = yield avg                          # give avg, receive next number
        total += x                             # update total
        count += 1                             # update count
        avg = total / count                    # new average

def flatten(nested: Iterable) -> Iterator:     # type: ignore[type-arg]
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)           # delegate to the sub-generator
        else:
            yield item

logs = ["ok\n", "ERROR disk\n", "ok\n", "ERROR net\n"]
print(list(only_errors(read_lines(logs))))     # pipeline: nothing is stored in between
print(list(chunked(range(5), 2)))              # batches
avg = running_average(); next(avg)             # prime: run to the first yield
print(avg.send(10), avg.send(20))              # two-way communication
print(list(flatten([1, [2, [3, 4]], 5])))      # recursive flatten

# Output:
# ['ERROR disk', 'ERROR net']
# [[0, 1], [2, 3], [4]]
# 10.0 15.0
# [1, 2, 3, 4, 5]
```

---

## 🟠 JavaScript vs Python Comparison
Almost identical: JS has `function*` and `yield`, `gen.next(value)` for sending. Python returns values or raises `StopIteration`; JS returns `{value, done}`.

```python
# Python way
def count(n):
    for i in range(n):
        yield i
print(list(count(3)))     # [0, 1, 2]
```
```javascript
// JavaScript way
function* count(n) {
  for (let i = 0; i < n; i++) yield i;
}
console.log([...count(3)]);   // [0, 1, 2]
```

---

## 🟠 FastAPI Connection
Dependencies with `yield` (DB sessions) are generators; `StreamingResponse` streams a generator to the client; Server-Sent Events send one yielded chunk at a time. Async generators (`async def` + `yield`) are used for async streaming (LLM token streams).

```python
from typing import AsyncIterator, Iterator
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()

def get_db() -> Iterator[dict]:
    db = {"open": True}                        # open resource per request
    try:
        yield db                               # FastAPI injects this value
    finally:
        db["open"] = False                     # runs after the response

async def tokens() -> AsyncIterator[str]:
    for t in ["Hello", " ", "world"]:
        yield t                                # like LLM tokens arriving one by one

@app.get("/chat")
async def chat() -> StreamingResponse:
    return StreamingResponse(tokens(), media_type="text/plain")

print(TestClient(app).get("/chat").text)       # Hello world
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: consuming a generator twice (second pass is empty).
✅ Correct: call the generator function again, or `list()` it if it is small.

```python
# Wrong
g = (x for x in range(3)); list(g); list(g)    # second is []
# Right
def gen(): return (x for x in range(3))
list(gen()); list(gen())
```

❌ Mistake 2: `return value` thinking it yields (it ends the generator; the value goes into `StopIteration.value`), or `raise StopIteration` inside a generator (RuntimeError since 3.7).
✅ Correct: use `yield` for values and plain `return` to finish.

❌ Mistake 3: forgetting to prime a send()-style generator (`TypeError: can't send non-None value to a just-started generator`).
✅ Correct: call `next(gen)` once first.

---

## 🧠 Tricky Interview Question
```python
def g():
    x = yield 1
    print("got", x)
    y = yield 2
    print("got", y)

it = g()
print(next(it))
print(it.send("A"))
print(next(it, "end"))
```
Answer: `1`, then `got A` and `2`, then `got None` and `end`. `send("A")` makes the first `yield` evaluate to "A". The final `next()` sends `None`, so `y` is `None`; the body then ends and `next(it, "end")` returns the default.

---

## ⚫ Interview Questions + Answers

Q1: Generator vs list comprehension?
A1: List comprehension builds everything now (memory O(n)); a generator expression is lazy (memory O(1)) but single-use and has no `len()` or indexing.

Q2: What does `yield from` do?
A2: Delegates to a sub-iterable, forwarding values (and `send`/`throw`), and returns the sub-generator's `return` value. Cleaner than a manual `for ... yield` loop.

Q3: How is a generator different from a normal function?
A3: A call returns a generator object without running the body; local state is preserved between yields, and execution resumes after the last yield.

Q4: How do you clean up resources in a generator?
A4: Use `try/finally` around the yield. `close()` raises `GeneratorExit` at the paused yield, so `finally` runs. Garbage collection also closes it.

Q5: What are async generators?
A5: `async def` with `yield`; consumed by `async for`. Used for streaming I/O such as LLM tokens or paginated async APIs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large files/streams, endless sequences, paginated APIs
- Pipelines of transformation steps
- You only need the first few results (`islice`, `next`)

❌ Avoid when:
- You need `len()`, indexing, or to iterate many times (use a list)
- The data is tiny (a list is simpler and often faster)
- Debuggability matters more than memory (lazy errors surface late)

---

## 📊 Visual Diagram
```
 gen = countdown(3)                 (body not started)

 next(gen) --> run ... yield 3 --> [paused, n=3]      returns 3
 next(gen) --> resume, n=2, yield 2 [paused, n=2]     returns 2
 next(gen) --> resume, n=1, yield 1 [paused, n=1]     returns 1
 next(gen) --> resume, loop ends    [finished]        raises StopIteration

 Pipeline:  file -> read_lines -> only_errors -> consumer
            (one line flows through all stages at a time)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generator | Function with `yield` | `yield` वाला function |
| yield | Pause and give a value | रुककर value देना |
| Lazy evaluation | Compute only on demand | माँगने पर ही गणना |
| send() | Pass a value into a generator | generator के अंदर value भेजना |
| yield from | Delegate to a sub-iterable | दूसरे iterable को सौंपना |
| Pipeline | Chained generator stages | जुड़े हुए stages की श्रृंखला |

---

## ⚡ 3-Line Summary
English: A generator uses `yield` to produce values lazily and keeps its state between calls.
English: It saves memory, enables pipelines, and is the shortest way to write an iterator.
English: Generators are single-use; use try/finally for cleanup and `yield from` to delegate.

Hindi: Generator `yield` से values lazily बनाता है और calls के बीच state सहेजता है।
Hindi: यह memory बचाता है, pipelines बनाने देता है, और iterator लिखने का सबसे छोटा तरीका है।
Hindi: Generators एक बार के होते हैं; cleanup के लिए try/finally और delegate के लिए `yield from` इस्तेमाल करो।

---

## ➡️ Next Topic
**480. Implement Singleton** — controlling object creation so only one instance exists.

---
