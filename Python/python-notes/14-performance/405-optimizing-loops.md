---

# 405. Optimizing Loops
# हिंदी में: Loops को तेज़ बनाना

---

## 🔵 Simple Definition (English)
Optimizing loops means making repeated work cheaper: use built-ins (`sum`, `any`, `map`) that run in C, use comprehensions, move repeated calculations out of the loop, use sets/dicts for lookups, and stop early. Always measure before and after.

## 🔵 सरल परिभाषा (Hindi)
Loops optimize करने का मतलब बार-बार होने वाले काम को सस्ता बनाना है: C में चलने वाले built-ins (`sum`, `any`, `map`) लें, comprehension लिखें, दोहराई गणना loop के बाहर निकालें, lookup के लिए set/dict लें और जल्दी रुक जाएँ। हमेशा पहले और बाद में measure करें।

---

## 🔴 Problem it Solves
Python runs each bytecode step in an interpreter, so a plain `for` loop over millions of items is slow (roughly 30-100x slower than C). In an API a slow loop blocks the worker and raises latency. Cheap fixes often give 2-10x, and fixing a wrong algorithm (list lookup inside a loop) gives 100x or more.

## 🔴 यह क्यों बना? (Hindi)
Python हर bytecode step interpreter में चलाता है, इसलिए लाखों items पर साधारण `for` loop धीमा है (C से लगभग 30-100 गुना)। API में धीमा loop worker को रोक देता है और latency बढ़ाता है। सस्ते बदलाव अक्सर 2-10 गुना देते हैं और गलत algorithm ठीक करने (loop में list lookup) से 100 गुना या ज़्यादा मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Profile first (cProfile / line_profiler) to find the REAL hot loop
Step 2 → Fix the algorithm: list "in" -> set "in", nested loops -> dict lookup
Step 3 → Replace the loop with a builtin (sum, min, max, any, all, sorted)
Step 4 → Use a comprehension / generator instead of append in a loop
Step 5 → Hoist invariants: compute constants, attribute lookups ONCE outside
Step 6 → Exit early (break, any/all, next) ; for huge numeric data use NumPy
Step 7 → Re-measure with timeit; keep the change only if it is really faster
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले profile करें (cProfile / line_profiler) ताकि असली hot loop मिले
Step 2 → Algorithm सुधारें: list "in" -> set "in", nested loops -> dict lookup
Step 3 → Loop की जगह builtin लें (sum, min, max, any, all, sorted)
Step 4 → Loop में append की जगह comprehension / generator लिखें
Step 5 → Invariants बाहर निकालें: constants और attribute lookups एक बार निकालें
Step 6 → जल्दी निकलें (break, any/all, next); बहुत बड़े numeric data के लिए NumPy
Step 7 → timeit से दोबारा measure करें; सच में तेज़ हो तभी बदलाव रखें
```

---

## 🟡 Real World Example
Razorpay checks 200k incoming payment ids against a list of 5000 already-processed ids with `if pid in processed_list`. Each check scans the list: O(n). Changing `processed` to a `set` makes each check O(1). On our benchmark below the set version was ~600x faster. In another place, a Swiggy report summed order totals with a manual loop; replacing it with `sum()` made that step about 5x faster.

## 🟡 Real Example Hindi mein
Razorpay 2 लाख आने वाले payment ids को 5000 processed ids की list से `if pid in processed_list` से जाँचता है। हर check पूरी list scan करता है: O(n)। `processed` को `set` बनाने से हर check O(1) हो जाता है। नीचे के benchmark में set वाला लगभग 600 गुना तेज़ निकला। एक और जगह Swiggy की report में order totals manual loop से जुड़ते थे; `sum()` लगाने से वह step करीब 5 गुना तेज़ हुआ।

---

## 💻 Code Example — Basic
```python
# Basic loop optimizations - every line commented
import timeit  # simple timer
from typing import List  # type hints

nums: List[int] = list(range(200_000))  # test data


def loop_sum(data: List[int]) -> int:  # manual loop
    t: int = 0  # accumulator
    for x in data:  # visit each item
        t += x  # add it
    return t  # result


def builtin_sum(data: List[int]) -> int:  # builtin version
    return sum(data)  # loop runs in C


def loop_double(data: List[int]) -> List[int]:  # append loop
    out: List[int] = []  # result list
    for x in data:  # each item
        out.append(x * 2)  # method lookup + call every time
    return out  # result


def comp_double(data: List[int]) -> List[int]:  # comprehension
    return [x * 2 for x in data]  # faster: LIST_APPEND opcode


assert loop_sum(nums) == builtin_sum(nums)  # same answer
assert loop_double(nums) == comp_double(nums)  # same answer

t1: float = min(timeit.repeat(lambda: loop_sum(nums), number=20, repeat=3)) / 20 * 1000  # ms
t2: float = min(timeit.repeat(lambda: builtin_sum(nums), number=20, repeat=3)) / 20 * 1000  # ms
print(f"loop sum {t1:.2f} ms, builtin sum {t2:.2f} ms")  # compare
# Output (machine dependent, Python 3.13, Apple silicon): loop sum 3.97 ms, builtin sum 0.78 ms
# so sum() was about 5x faster in this run.

# Early exit: stop at the first match instead of scanning everything
print(any(x > 10 for x in nums))  # stops after finding 11
# Output: True
print(next((x for x in nums if x % 7 == 0 and x > 100), None))  # first match or None
# Output: 105
```

## 💻 Code Example — Advanced
```python
# Production style: benchmark several strategies and verify they give identical results
import math  # sqrt, pi
import timeit  # timing
from typing import Callable, List, Set  # type hints

N: int = 200_000  # size of data
data: List[int] = list(range(N))  # input data


def loop_append() -> List[int]:  # baseline
    out: List[int] = []  # result
    for x in data:  # loop
        out.append(x * 2)  # append each
    return out  # result


def loop_bound() -> List[int]:  # cache the bound method
    out: List[int] = []  # result
    add = out.append  # lookup once
    for x in data:  # loop
        add(x * 2)  # call the cached method
    return out  # result


def comp() -> List[int]:  # comprehension
    return [x * 2 for x in data]  # fastest pure-Python list build


def with_map() -> List[int]:  # map with a C-level callable
    return list(map((2).__mul__, data))  # no Python function call per item


def ranged_index() -> int:  # un-Pythonic index loop
    t: int = 0  # total
    for i in range(len(data)):  # index loop
        t += data[i]  # extra index operation
    return t  # result


def sum_loop() -> int:  # plain loop sum
    t: int = 0  # total
    for x in data:  # iterate items directly
        t += x  # add
    return t  # result


def sum_builtin() -> int:  # builtin sum
    return sum(data)  # C loop


def invariant_inside() -> List[float]:  # repeated global + attribute lookups
    return [math.sqrt(x) * math.pi for x in data]  # looks up math.sqrt each time


def invariant_hoisted() -> List[float]:  # hoist lookups out of the loop
    sqrt = math.sqrt  # local variable is fastest to read
    k: float = math.pi  # constant once
    return [sqrt(x) * k for x in data]  # cheaper per item


def bench(fn: Callable[[], object], n: int = 20) -> float:  # time in ms per call
    return min(timeit.repeat(fn, number=n, repeat=3)) / n * 1000  # best of 3


assert loop_append() == loop_bound() == comp() == with_map()  # same results
assert sum_loop() == sum_builtin() == ranged_index()  # same results
for f in (loop_append, loop_bound, comp, with_map, sum_loop, sum_builtin,
          ranged_index, invariant_inside, invariant_hoisted):  # all candidates
    print(f"{f.__name__:18s}{bench(f):7.2f} ms")  # print timing
# Output (Python 3.13.3, Apple silicon; your numbers will differ, ratios are what matter):
# loop_append          5.81 ms
# loop_bound           6.31 ms
# comp                 4.47 ms
# with_map             6.18 ms
# sum_loop             3.97 ms
# sum_builtin          0.78 ms
# ranged_index         7.00 ms
# invariant_inside    10.11 ms
# invariant_hoisted    7.85 ms

lst: List[int] = list(range(5000))  # list of ids
st: Set[int] = set(lst)  # same ids in a set
q: List[int] = list(range(4000, 6000))  # ids to check
t_list: float = timeit.timeit(lambda: [x for x in q if x in lst], number=3)  # O(n) per check
t_set: float = timeit.timeit(lambda: [x for x in q if x in st], number=3)  # O(1) per check
print(f"list/set membership ratio ~{t_list / t_set:.0f}x")  # how much slower the list is
# Output: list/set membership ratio ~636x   (a second run gave ~657x)
```
Verified on Python 3.13.3: results matched by the asserts, and the timings above are real runs. Honest finding: caching the bound method (`loop_bound`) was NOT faster on 3.13 (it was slightly slower), because the interpreter now specializes `list.append` calls. Old advice ("always cache `append`") is outdated on recent versions. The big wins were `sum()` (about 5x), the set lookup (hundreds of times) and the comprehension (about 25% over append).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: use builtins and comprehensions
total = sum(x * x for x in nums if x % 2 == 0)
found = any(x > 100 for x in nums)
unique_ids = set(ids)            # O(1) membership
```

```javascript
// JavaScript: use array methods and Set (V8 JIT makes plain loops fast too)
const total = nums.filter(x => x % 2 === 0).reduce((a, x) => a + x * x, 0);
const found = nums.some(x => x > 100);
const uniqueIds = new Set(ids);  // O(1) has()
```

Key differences: in JavaScript the V8 JIT compiles hot loops, so a simple `for` loop is already fast. In CPython (3.13 has only an experimental JIT, off by default) a plain loop stays slow, so moving work into builtins, comprehensions and NumPy matters a lot. The data structure advice (Set vs Array/list lookup) applies to both.

---

## 🟠 FastAPI Connection
Heavy loops inside a normal `def`/`async def` endpoint block a worker. Fix the algorithm first (set/dict lookups), then push CPU-heavy loops to NumPy, a process pool or a background job.

```python
# FastAPI: de-duplicate with a set instead of list lookups (needs: pip install fastapi httpx)
from typing import Dict, List, Set  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client
from pydantic import BaseModel  # request body model

app: FastAPI = FastAPI()  # create app
PROCESSED: Set[int] = {1, 2, 3}  # already handled payment ids (set = O(1) lookup)


class Batch(BaseModel):  # request body
    ids: List[int]  # incoming payment ids


@app.post("/payments/new")  # returns only unseen ids
def new_payments(batch: Batch) -> Dict[str, List[int]]:
    fresh: List[int] = [i for i in batch.ids if i not in PROCESSED]  # comprehension + set lookup
    PROCESSED.update(fresh)  # remember them (bulk update, no loop)
    return {"new": fresh}  # JSON response


client = TestClient(app)  # test client
print(client.post("/payments/new", json={"ids": [2, 3, 4, 5]}).json())  # Output: {'new': [4, 5]}
print(client.post("/payments/new", json={"ids": [4, 6]}).json())  # Output: {'new': [6]}
```
Verified by running the logic with the TestClient.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `in` on a list inside a loop
```python
# Wrong - O(n * m): 2000 checks over a 5000-item list was ~600x slower than a set
result = [x for x in queries if x in big_list]

# Right - build a set once
big_set = set(big_list)
result = [x for x in queries if x in big_set]
```

❌ Mistake 2: `range(len(x))` when you only read items
```python
# Wrong - extra indexing (7.00 ms vs 3.97 ms in our test)
for i in range(len(data)):
    t += data[i]

# Right - iterate directly (use enumerate if you need the index)
for x in data:
    t += x
```

❌ Mistake 3: Repeating invariant work inside the loop
```python
# Wrong - recomputes len(), re.compile(), config lookups every iteration
for row in rows:
    if re.compile(r"\d+").match(row): ...

# Right - compute once outside
pattern = re.compile(r"\d+")
for row in rows:
    if pattern.match(row): ...
```

❌ Mistake 4: Modifying a list while looping over it
```python
# Wrong - items get skipped while the list shifts (verified)
nums = [1, 2, 3, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)          # [1, 3, 5]  (3 and 5 were skipped; harmless here by luck)

# Right - build a new list
nums = [n for n in nums if n % 2 != 0]
```
(The result looks correct by luck. With `[2, 4, 6]` the output is `[4]`, which is wrong (verified). Never mutate what you iterate.)

❌ Mistake 5: Optimizing without measuring
```python
# Wrong - rewriting code "because it feels slow"
# Right - profile, change one thing, timeit again, keep it only if faster
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print, and why is it a bug?

```python
nums = [1, 2, 3, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
```

**Answer**: It prints `[1, 3, 5]` (verified). It looks right only by luck of the data. The `for` loop uses an internal index. When `2` is removed, the list shifts left, so `3` moves to index 1 and the loop jumps to index 2 (value `4`): `3` was skipped. Skipping happens to be harmless for the odd numbers here, but with `[2, 4, 6]` the output would be `[4]` because `4` gets skipped. The safe pattern is a comprehension: `[n for n in nums if n % 2 != 0]`.

---

## ⚫ Interview Questions + Answers

Q1: Why is a list comprehension faster than a for loop with append?
A1: It uses the `LIST_APPEND` bytecode directly and avoids the attribute lookup and method call on every item. In our test it was about 25% faster (4.47 vs 5.81 ms). On 3.12+ comprehensions are also inlined (PEP 709).

Q2: Why is `x in some_set` faster than `x in some_list`?
A2: A set uses hashing, so the check is O(1) on average; a list compares one by one, O(n). In the benchmark the gap was 600x+.

Q3: When is `map()` better than a comprehension?
A3: When the function is a C-level builtin or a bound method (`map(str, data)`). With a lambda, a comprehension is usually as fast or faster and more readable.

Q4: A generator expression or a list comprehension?
A4: Generator if you iterate once or the data is huge (low memory, supports early exit with `any`/`next`). List if you need indexing, `len`, or several passes.

Q5: When do plain loops stop being enough?
A5: For big numeric arrays use NumPy/pandas (vectorized C loops, often 10-100x faster). For CPU-bound pure Python, use multiprocessing, Numba/Cython, or PyPy.

Q6: What is "hoisting"?
A6: Moving work that does not change between iterations (a regex compile, `len()`, attribute lookups, a constant) out of the loop so it runs once.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Profiling shows a loop is the hot spot
- A list is used for membership tests inside a loop
- You can replace the loop with `sum`, `min`, `max`, `any`, `all`, `sorted`

❌ Avoid when:
- The loop runs only a few times (readability beats speed)
- It is not on the hot path (do not micro-optimize everywhere)
- The trick makes code unreadable for a tiny gain (e.g. caching `append` on 3.13)

---

## 📊 Visual Diagram

```
 Slow                                   Faster
 ----                                   ------
 for i in range(len(a)):                for x in a:
     if a[i] in big_list: ...               if x in big_set: ...
          |                                      |
          v                                      v
   O(n) scan per check                   O(1) hash lookup

 Order of impact:
 1. better algorithm / data structure   (100x+)
 2. builtins, NumPy                     (5-50x)
 3. comprehension, hoisting             (1.2-2x)
 4. micro tricks                        (often 0 on modern Python)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hoisting | Moving repeated work out of the loop | दोहराया काम loop के बाहर निकालना |
| Vectorization | Doing the loop in C over whole arrays | पूरे array पर C में loop चलाना |
| Short-circuit | Stop as soon as the answer is known | जवाब मिलते ही रुक जाना |
| O(1) lookup | Constant time (set/dict) | स्थिर समय में खोज |
| Builtin | Function implemented in C | C में बना function |
| Hot loop | Loop that uses most of the time | जो loop सबसे ज़्यादा समय लेता है |

---

## ⚡ 3-Line Summary
English: First fix the algorithm (set/dict instead of list lookups), then use builtins and comprehensions, hoist repeated work and exit early. Measure with timeit; some old tricks (like caching `append`) no longer help on Python 3.13. Use NumPy for big numeric loops.
Hindi: पहले algorithm सुधारें (list lookup की जगह set/dict), फिर builtins और comprehension लें, दोहराया काम बाहर निकालें और जल्दी रुकें। timeit से measure करें; पुराने tricks (जैसे `append` cache करना) Python 3.13 में काम नहीं करते। बड़े numeric loops के लिए NumPy लें।

---

## ➡️ Next Topic
**406. List Comprehension Performance** — a deeper look at comprehensions vs loops, `map`/`filter` and generator expressions.
