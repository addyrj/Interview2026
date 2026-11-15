---

# 123. Generator Expressions
# हिंदी में: Generator Expressions (बिना list बनाए lazy comprehension)

---

## 🔵 Simple Definition (English)
A generator expression `(f(x) for x in data if cond)` looks like a list comprehension but with parentheses. It does not build a list; it produces one value at a time when asked. It uses almost no memory and can be used once.

## 🔵 सरल परिभाषा (Hindi)
Generator expression `(f(x) for x in data if cond)` list comprehension जैसा दिखता है पर parentheses के साथ। यह list नहीं बनाता; माँगने पर एक-एक value देता है। यह बहुत कम memory लेता है और सिर्फ एक बार use होता है।

---

## 🔴 Problem it Solves
`sum([x*x for x in range(10**8)])` first builds a 100-million-item list (gigabytes of RAM), then sums it. A generator expression feeds items straight into `sum` one at a time, so memory stays tiny. It also stops early: `any(...)` can quit on the first match without computing the rest.

## 🔴 यह क्यों बना? (Hindi)
`sum([x*x for x in range(10**8)])` पहले 10 करोड़ items की list बनाता है (GBs RAM), फिर जोड़ता है। Generator expression items सीधे `sum` को एक-एक करके देता है, इसलिए memory बहुत कम रहती है। यह जल्दी रुक भी सकता है: `any(...)` पहला match मिलते ही बाकी compute किए बिना रुक जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → (expr for x in it if cond) creates a generator object instantly
Step 2 → No loop runs yet. Nothing is computed
Step 3 → Each next() resumes the loop, computes ONE value, pauses
Step 4 → When the loop ends, StopIteration is raised (for/sum handle it)
Step 5 → The generator is exhausted: iterating again gives nothing
Step 6 → Only the FIRST iterable is evaluated immediately; the rest are late

g = (x*x for x in range(3));  next(g) -> 0;  next(g) -> 1;  next(g) -> 4
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → (expr for x in it if cond) एक generator object तुरंत बनाता है
Step 2 → अभी कोई loop नहीं चला। कुछ compute नहीं हुआ
Step 3 → हर next() loop को आगे बढ़ाकर एक value बनाता है और रुक जाता है
Step 4 → Loop खत्म होने पर StopIteration आता है (for/sum इसे संभालते हैं)
Step 5 → Generator खत्म: दोबारा iterate करने पर कुछ नहीं मिलता
Step 6 → सिर्फ पहला iterable तुरंत evaluate होता है; बाकी बाद में
```

---

## 🟡 Real World Example
Reading a 5 GB access log to count error lines: `sum(1 for line in f if "ERROR" in line)` never loads the file. A Swiggy order-export job checks `any(o.amount > 50000 for o in orders)` to flag fraud and stops at the first hit. A data pipeline chains generators: read lines, strip, parse JSON, filter, all lazily.

## 🟡 Real Example Hindi mein
5 GB access log में error lines गिनने के लिए `sum(1 for line in f if "ERROR" in line)` file को memory में load नहीं करता। Swiggy का order-export job fraud flag करने के लिए `any(o.amount > 50000 for o in orders)` चलाता है और पहला मिलते ही रुक जाता है। Data pipeline में generators जुड़े होते हैं: lines पढ़ो, strip, JSON parse, filter, सब lazily।

---

## 💻 Code Example — Basic
```python
# Basic generator expressions
import sys                                         # to compare object sizes

lst: list[int] = [x * x for x in range(5)]         # list comprehension: built now
gen = (x * x for x in range(5))                    # generator expression: built later
print(lst)                                         # full list is visible
print(type(gen).__name__)                          # a generator object
print(next(gen), next(gen))                        # pull two values manually
print(list(gen))                                   # the remaining values
print(list(gen))                                   # exhausted -> empty

print(sum(x for x in range(1, 5)))                 # no extra parentheses needed in a call
print(any(x > 3 for x in [1, 2, 5]))               # stops at the first True
print(all(x > 0 for x in [1, 2, -5, 7]))           # stops at the first False
print(max((len(w) for w in ["a", "abc", "ab"]), default=0))   # longest word length
print(",".join(str(n) for n in range(3)))          # build a string without a temp list

big_list = [i for i in range(100_000)]             # 100k items in memory
big_gen = (i for i in range(100_000))              # tiny, fixed size
print(sys.getsizeof(big_list) > sys.getsizeof(big_gen))   # the list is much bigger
print(sys.getsizeof(big_gen) < 300)                # generator object stays small

# Output:
# [0, 1, 4, 9, 16]
# generator
# 0 1
# [4, 9, 16]
# []
# 10
# True
# False
# 3
# 0,1,2
# True
# True
```

## 💻 Code Example — Advanced
```python
# Production style: lazy log pipeline with early exit and chained generators
from collections.abc import Iterable, Iterator     # type hints for lazy data
import io                                          # in-memory file for the demo
import json                                        # parse JSON lines


def read_lines(f: Iterable[str]) -> Iterator[str]:
    """Strip each line lazily."""
    return (line.strip() for line in f)            # generator expression


def non_empty(lines: Iterable[str]) -> Iterator[str]:
    """Skip blank lines lazily."""
    return (line for line in lines if line)        # filter step


def parse(lines: Iterable[str]) -> Iterator[dict[str, object]]:
    """Parse JSON lines; bad lines are skipped, not fatal."""
    for line in lines:                             # use a real generator for try/except
        try:                                       # genexp cannot contain try
            yield json.loads(line)                 # produce one parsed record
        except json.JSONDecodeError:               # bad JSON line
            continue                               # ignore and move on


raw = io.StringIO('{"level": "INFO", "ms": 20}\n\nnot json\n{"level": "ERROR", "ms": 900}\n'
                  '{"level": "ERROR", "ms": 50}\n')    # fake log file
records = parse(non_empty(read_lines(raw)))        # nothing has run yet (all lazy)
slow_errors = (r for r in records if r["level"] == "ERROR" and r["ms"] > 100)   # one more stage
print(next(slow_errors, None))                     # first slow error only
print(sum(1 for _ in slow_errors))                 # the rest of the pipeline: 0 more

# Early exit demo: count how many items the generator actually evaluated
calls: list[int] = []                              # record every evaluation


def expensive(x: int) -> int:
    calls.append(x)                                # remember that this ran
    return x * 2                                   # pretend this is slow


found = any(expensive(x) > 5 for x in range(100))  # stops at x = 3 (6 > 5)
print(found, calls)                                # only 4 evaluations, not 100

# Late-evaluation gotcha: later iterables are read when consumed
data = [1, 2, 3]                                   # source list
g = (x for x in data)                              # first iterable is bound NOW
data.append(4)                                     # same list object, mutated
print(list(g))                                     # sees 4 because same list object

# Output:
# {'level': 'ERROR', 'ms': 900}
# 0
# True [0, 1, 2, 3]
# [1, 2, 3, 4]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Lazy sequence syntax | `(x for x in it)` | no expression form; use `function*` generator |
| Early exit | `any(...)`, `next(...)` | `some()` on arrays (array already built) |
| Memory | O(1) | arrays are eager, O(n) |
| Reuse | one pass only | arrays reusable |
| Lazy iterator helpers | `itertools` | Iterator helpers (`.map/.filter` on iterators, ES2025) |

```python
# Python way
print(sum(x * x for x in range(5)))                # 30, no list built
```
```javascript
// JavaScript way
const sq = [0, 1, 2, 3, 4].map(x => x * x);        // builds a full array first
console.log(sq.reduce((a, b) => a + b, 0));        // 30
// lazy version needs a generator function:
function* squares(n) { for (let i = 0; i < n; i++) yield i * i; }
console.log([...squares(5)].reduce((a, b) => a + b, 0));
```

Key difference: Python gives a one-line lazy form; in JS you write a `function*` or accept a full array. Newer JS iterator helpers (ES2025) bring similar laziness to iterators.

---

## 🟠 FastAPI Connection
FastAPI's `StreamingResponse` accepts any iterator. A generator expression (or generator function) lets you export a million rows as CSV without holding them all in memory. Combine it with a DB cursor that yields rows.

```python
# FastAPI example — stream a big export lazily
from fastapi import FastAPI                        # app
from fastapi.responses import StreamingResponse    # streams an iterator

app: FastAPI = FastAPI()                           # create app


@app.get("/export")                                # GET /export
def export_numbers() -> StreamingResponse:
    rows = (f"{i},{i * i}\n" for i in range(1, 6)) # lazy CSV lines (use a DB cursor in real life)
    return StreamingResponse(rows, media_type="text/csv")   # sent chunk by chunk
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Iterating a generator twice
✅ Correct: recreate it or store a list

```python
g = (x for x in range(3))
# Wrong
print(sum(g), sum(g))          # 3 0   <- second pass is empty
# Right
make = lambda: (x for x in range(3))
print(sum(make()), sum(make()))   # 3 3
```

❌ Mistake 2: Using `len()` or indexing on a generator
✅ Correct: convert to a list (if it fits memory) or count while iterating

```python
g = (x for x in range(5))
# Wrong
# len(g)        # TypeError: object of type 'generator' has no len()
# g[0]          # TypeError: 'generator' object is not subscriptable
# Right
print(sum(1 for _ in g))       # 5
```

❌ Mistake 3: Using a generator when you need the list many times
✅ Correct: use a list comprehension (faster for small data)

```python
# Wrong — recomputes or exhausts
g = (x * 2 for x in range(3))
print(max(g), min(g) if False else "empty after max")   # second use is exhausted
# Right
vals = [x * 2 for x in range(3)]
print(max(vals), min(vals))    # 4 0
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
x = 10
g = (x * i for i in range(3))
x = 100
print(list(g))
a = [1, 2, 3]
g2 = (v for v in a)
a = [9, 9]
print(list(g2))
print(sum((i for i in range(3)), 10))
```
Answer: `[0, 100, 200]`. The first iterable (`range(3)`) is evaluated immediately, but the name `x` in the body is looked up when each value is produced, so it sees `100`. For `g2`, the first iterable `a` (the list `[1, 2, 3]`) is bound at creation, so rebinding `a` afterwards doesn't matter: output is `[1, 2, 3]`. The last line is `13`, because `10` is the start value passed to `sum`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between a list comprehension and a generator expression?
A1: `[...]` builds the entire list now (O(n) memory, reusable, supports `len` and indexing). `(...)` builds a lazy one-shot iterator (O(1) memory, no `len`, no indexing). Generators are better for big or streaming data.

Q2: When is a generator expression slower?
A2: For small data, a list comprehension is a bit faster because there is no generator pause/resume overhead. Use generators for memory, early exit and pipelines, not for raw speed on tiny lists.

Q3: Why can we write `sum(x for x in data)` without extra parentheses?
A3: When a generator expression is the only argument of a call, the call's parentheses double as the genexp's. With other arguments you must write `sum((x for x in data), 10)`.

Q4: How do you get a generator expression's values?
A4: Iterate with `for`, call `next()`, or pass it to a consumer like `list`, `sum`, `any`, `"".join`. Use `next(g, default)` to avoid `StopIteration`.

Q5: Can you use `try/except` or multiple statements inside one?
A5: No. A generator expression holds a single expression. For anything more, write a generator function with `yield`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Feeding `sum`, `min`, `max`, `any`, `all`, `join`
- Processing big files or streams
- Early exit matters (`any`, `next`)
- Chaining lazy pipeline stages

❌ Avoid when:
- You need `len()`, indexing, slicing or multiple passes
- The data is tiny and speed matters
- Logic needs error handling (use `def` + `yield`)

---

## 📊 Visual Diagram
```
List comp [x*x for x in range(4)]
   -> compute ALL now -> [0, 1, 4, 9]     memory: 4 items

Gen expr  (x*x for x in range(4))
   -> next() -> 0   (pause)
   -> next() -> 1   (pause)
   -> next() -> 4   (pause)
   -> next() -> 9   (pause)
   -> next() -> StopIteration              memory: 1 item at a time
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generator | Object producing values on demand | माँग पर values देने वाला object |
| Lazy evaluation | Compute only when needed | जरूरत पर ही गणना |
| StopIteration | Signal that values are finished | Values खत्म होने का संकेत |
| Exhausted | Already fully consumed | पूरा use हो चुका |
| Pipeline | Chain of lazy stages | Lazy stages की श्रृंखला |
| Early exit | Stop before finishing | खत्म होने से पहले रुकना |

---

## ⚡ 3-Line Summary
English: A generator expression is a lazy, one-shot comprehension written with parentheses. It saves memory, supports early exit and plugs straight into `sum`, `any`, `join`. You cannot index it, take its length or reuse it.
Hindi: Generator expression parentheses वाला lazy, एक बार चलने वाला comprehension है। यह memory बचाता है, जल्दी रुक सकता है और `sum`, `any`, `join` में सीधे लगता है। इसमें index, length या दोबारा use नहीं हो सकता।

---

## ➡️ Next Topic
**126. Decorator with Arguments** — decorators that take their own settings, like `@retry(times=3)`.
