---

# 406. List Comprehension Performance
# हिंदी में: List Comprehension की Performance (तेज़ list बनाना)

---

## 🔵 Simple Definition (English)
A list comprehension (`[f(x) for x in data if cond]`) builds a list in one expression. In CPython it is usually 20-40% faster than the same loop with `.append()`, because the loop runs inside optimized bytecode and avoids the repeated `list.append` attribute lookup and call.

## 🔵 सरल परिभाषा (Hindi)
List comprehension (`[f(x) for x in data if cond]`) एक ही expression में list बना देती है। CPython में यह उसी काम के `.append()` वाले loop से आमतौर पर 20-40% तेज़ होती है, क्योंकि हर बार `list.append` को ढूँढने और call करने का खर्च बचता है।

---

## 🔴 Problem it Solves
A normal `for` loop with `result.append(...)` does a method lookup and a function call on every iteration. For millions of items this overhead adds up. Comprehensions use a dedicated `LIST_APPEND` bytecode, so the same result is produced with less work. They also make the intent ("build a list from this") obvious.

## 🔴 यह क्यों बना? (Hindi)
सामान्य `for` loop में `result.append(...)` हर iteration पर method lookup और function call करता है। लाखों items पर यह खर्च बढ़ जाता है। Comprehension में `LIST_APPEND` नाम का खास bytecode चलता है, इसलिए वही नतीजा कम काम में मिलता है। साथ ही code पढ़ने में साफ़ होता है कि "इससे list बन रही है"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python compiles the comprehension into its own small code object
Step 2 → It creates an empty list and starts the iteration (GET_ITER / FOR_ITER)
Step 3 → For each item it evaluates the condition and the expression
Step 4 → LIST_APPEND adds the value directly (no method lookup, no call)
Step 5 → The finished list is returned
Note   → Python 3.12+ (PEP 709) inlines comprehensions into the parent function,
         removing the extra function-call cost of creating the comprehension
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python comprehension को एक छोटे code object में compile करता है
Step 2 → खाली list बनती है और iteration शुरू होता है
Step 3 → हर item पर condition और expression evaluate होते हैं
Step 4 → LIST_APPEND सीधे value जोड़ देता है (method lookup या call नहीं)
Step 5 → पूरी list return होती है
नोट   → Python 3.12+ (PEP 709) में comprehension parent function में inline हो जाती है
```

---

## 🟡 Real World Example
Zomato backend: from 100,000 menu rows, keep only available dishes and convert price to rupees: `[d.price / 100 for d in dishes if d.available]`. A FastAPI response builder turns DB rows into dicts with one comprehension. An AI app normalizes a million text chunks (`[c.strip().lower() for c in chunks]`) before embedding.

## 🟡 Real Example Hindi mein
Zomato backend में 1 लाख menu rows में से सिर्फ available dishes लेकर price रुपये में बदलना: `[d.price / 100 for d in dishes if d.available]`। FastAPI response builder DB rows को एक comprehension से dicts में बदलता है। AI app embedding से पहले दस लाख text chunks को `[c.strip().lower() for c in chunks]` से साफ़ करता है।

---

## 💻 Code Example — Basic
```python
# Basic: loop vs comprehension vs map - same result, different speed
import timeit  # standard library timer
from typing import List  # type hints

N: int = 200_000  # size of the data


def with_loop() -> List[int]:
    result: List[int] = []  # empty list to fill
    for x in range(N):  # visit every number
        if x % 2 == 0:  # keep only even numbers
            result.append(x * 2)  # method lookup + call every time
    return result  # finished list


def with_comprehension() -> List[int]:
    return [x * 2 for x in range(N) if x % 2 == 0]  # one expression, LIST_APPEND


def with_filter_map() -> List[int]:
    return list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, range(N))))  # 2 lambda calls per item


# Results must be identical
print(with_loop() == with_comprehension() == with_filter_map())  # compare all three
# Output: True

t_loop: float = min(timeit.repeat(with_loop, number=5, repeat=3))  # best of 3 runs
t_comp: float = min(timeit.repeat(with_comprehension, number=5, repeat=3))  # best of 3 runs
t_map: float = min(timeit.repeat(with_filter_map, number=5, repeat=3))  # best of 3 runs

print("comprehension faster than loop:", t_comp < t_loop)  # usually True
# Output: comprehension faster than loop: True
print("comprehension faster than map+lambda:", t_comp < t_map)  # lambdas are slow
# Output: comprehension faster than map+lambda: True
# (exact seconds differ on every machine - compare, do not hard-code them)

# Condition position: filter uses "if" at the end, ternary goes in the front
print([x if x % 2 == 0 else -x for x in range(5)])  # ternary: changes the value
# Output: [0, -1, 2, -3, 4]
print([x for x in range(5) if x % 2 == 0])  # filter: drops items
# Output: [0, 2, 4]
```

## 💻 Code Example — Advanced
```python
# Production style: bytecode, memory, hoisting, generator vs list
import dis  # disassembler to see bytecode
import sys  # memory size
import timeit  # benchmark
from typing import Dict, Iterable, List, Set


def build_loop(data: List[int]) -> List[int]:
    out: List[int] = []  # empty list
    for x in data:  # iterate
        out.append(x + 1)  # explicit append call
    return out  # return list


def build_comp(data: List[int]) -> List[int]:
    return [x + 1 for x in data]  # comprehension


# 1) Bytecode proof: the loop calls append, the comprehension uses LIST_APPEND
loop_ops: Set[str] = {i.opname for i in dis.get_instructions(build_loop)}  # opcode names
comp_ops: Set[str] = {i.opname for i in dis.get_instructions(build_comp)}  # opcode names
print("loop has CALL:", "CALL" in loop_ops)  # method call every iteration
# Output: loop has CALL: True
print("comp has LIST_APPEND:", "LIST_APPEND" in comp_ops)  # direct append opcode
# Output: comp has LIST_APPEND: True

# 2) Memory: a list stores everything, a generator stores almost nothing
as_list: List[int] = [x for x in range(100_000)]  # all values in memory
as_gen: Iterable[int] = (x for x in range(100_000))  # lazy, computed on demand
print(sys.getsizeof(as_list) > 100 * sys.getsizeof(as_gen))  # list is far bigger
# Output: True

# 3) Membership in a list is O(n); build a set (comprehension) for O(1) lookups
ids: List[int] = list(range(20_000))  # pretend user ids
id_set: Set[int] = {i for i in ids}  # set comprehension
t_list: float = timeit.timeit(lambda: 19_999 in ids, number=2000)  # scans the list
t_set: float = timeit.timeit(lambda: 19_999 in id_set, number=2000)  # hash lookup
print("set lookup faster:", t_set < t_list)  # hashing wins
# Output: set lookup faster: True

# 4) Hoist repeated work out of the comprehension
words: List[str] = ["Apple", "BANANA", "Cherry"] * 3  # sample data
upper_limit: int = 5  # computed once, outside
short: List[str] = [w.lower() for w in words if len(w) <= upper_limit]  # cheap body
print(short)  # only "Apple" has <= 5 letters (3 copies)
# Output: ['apple', 'apple', 'apple']

# 5) Dict comprehension for fast lookups (id -> row)
rows: List[Dict[str, int]] = [{"id": i, "qty": i * 2} for i in range(3)]  # fake rows
by_id: Dict[int, Dict[str, int]] = {r["id"]: r for r in rows}  # index by id
print(by_id[2]["qty"])  # direct lookup
# Output: 4
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: comprehension = map + filter in one expression
prices = [100, 250, 40, 900]
discounted = [p * 0.9 for p in prices if p > 50]   # [90.0, 225.0, 810.0]
lookup = {p: p * 0.9 for p in prices}              # dict comprehension
unique = {p % 3 for p in prices}                   # set comprehension
```
```javascript
// JavaScript: chain of array methods
const prices = [100, 250, 40, 900];
const discounted = prices.filter(p => p > 50).map(p => p * 0.9);   // two passes
const lookup = Object.fromEntries(prices.map(p => [p, p * 0.9]));
const unique = new Set(prices.map(p => p % 3));
```

Key differences: JS chains `filter().map()` (two passes, each creating an array). A Python comprehension does filter and transform in a single pass. Python has dedicated syntax for list, dict and set; JS needs `Object.fromEntries` and `new Set`.

---

## 🟠 FastAPI Connection
In FastAPI you turn DB objects into response dictionaries or schemas for hundreds of rows per request. A single comprehension is the idiomatic, fastest pure-Python way. For very large responses prefer pagination instead of building a giant list.

```python
# FastAPI: build the response with a comprehension (pip install fastapi httpx)
from typing import Dict, List  # type hints
from fastapi import FastAPI, Query  # app and query validation
from fastapi.testclient import TestClient  # in-process testing

app: FastAPI = FastAPI()  # create the app
DISHES: List[Dict[str, object]] = [  # pretend DB table
    {"name": f"dish{i}", "price": i * 10, "available": i % 2 == 0} for i in range(10)
]


@app.get("/dishes")  # GET /dishes?max_price=50
def dishes(max_price: int = Query(100, ge=0)) -> List[Dict[str, object]]:
    return [  # one pass: filter + shape the output
        {"name": d["name"], "price": d["price"]}
        for d in DISHES
        if d["available"] and d["price"] <= max_price  # type: ignore[operator]
    ]


client: TestClient = TestClient(app)  # test without running a server
print(client.get("/dishes", params={"max_price": 40}).json())  # call the endpoint
# Output: [{'name': 'dish0', 'price': 0}, {'name': 'dish2', 'price': 20}, {'name': 'dish4', 'price': 40}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a comprehension only for side effects
```python
# Wrong - builds a throwaway list of None values:
[print(x) for x in range(3)]

# Correct - use a plain loop:
for x in range(3):
    print(x)
```

❌ Mistake 2: Building a huge list when you only iterate once
```python
# Wrong - 10 million numbers held in memory:
total = sum([x * x for x in range(10_000_000)])

# Correct - generator expression (round brackets), constant memory:
total = sum(x * x for x in range(10_000_000))
```

❌ Mistake 3: Calling an expensive function repeatedly inside, or nesting too deeply
```python
# Wrong - len(big) is recomputed and the nesting is unreadable:
pairs = [(a, b) for a in range(3) for b in range(3) if a != b and len(str(a)) < 5]

# Correct - hoist constants out, keep to 2 levels, use a loop if it gets complex
limit = 5
pairs = [(a, b) for a in range(3) for b in range(3) if a != b]
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
x = 10
squares = [x * x for x in range(3)]
print(x, squares)

funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])

funcs2 = [lambda i=i: i for i in range(3)]
print([f() for f in funcs2])
```

**Answer**:
```
10 [0, 1, 4]
[2, 2, 2]
[0, 1, 2]
```
The comprehension has its own scope, so the loop variable `x` does not leak and the outer `x` stays 10 (in Python 3). The lambdas in `funcs` all share the same `i` and read it after the loop finished (late binding), so each returns 2. Using a default argument `i=i` captures the current value.

---

## ⚫ Interview Questions + Answers

Q1: Why is a list comprehension faster than a `for` loop with `append`?
A1: It uses the `LIST_APPEND` bytecode and skips the attribute lookup and call of `list.append` on every iteration. The gain is typically 20-40%, not 10x.

Q2: Is `map()` faster than a comprehension?
A2: Only when the function is a built-in or C function (`map(str, data)`). With a `lambda` or Python function, the comprehension is faster because it avoids a Python function call per item.

Q3: When should I use a generator expression instead?
A3: When you iterate once or feed `sum`, `any`, `all`, `max`. It uses constant memory. If you need indexing, `len()`, or to iterate multiple times, build the list.

Q4: Did Python 3.12 change comprehensions?
A4: Yes. PEP 709 inlines list, dict and set comprehensions, so no hidden function object is created per comprehension. It makes them up to about 2x faster for tiny comprehensions. Generator expressions are not inlined.

Q5: Can a comprehension be slower than a loop?
A5: Yes. For huge outputs where memory pressure matters, or with side effects, or when you need an early `break`, a loop or generator is better. A comprehension cannot `break`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You transform and/or filter an iterable into a new list, set or dict
- The logic fits in one readable line or two
- You need the fastest pure-Python way to build a list

❌ Avoid when:
- You need side effects (printing, writing to DB)
- The logic needs `break`, `try/except` or many nested branches
- You only iterate once over a huge input (use a generator expression)
- The numeric data is large: use NumPy instead

---

## 📊 Visual Diagram

```
Loop + append                      Comprehension
-------------                      -------------
for x in data:                     [ f(x) for x in data if cond ]
   look up out.append   <- cost          |
   call append(...)     <- cost          v
   next item                       LIST_APPEND (one fast opcode)

per item:  lookup + call + store   per item:  store only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| List comprehension | One-line way to build a list | एक line में list बनाना |
| LIST_APPEND | Bytecode that appends without a method call | बिना method call के जोड़ने वाला bytecode |
| Generator expression | Lazy version with round brackets | lazy रूप, गोल कोष्ठक में |
| PEP 709 | Inlined comprehensions in 3.12+ | 3.12+ में inline comprehension |
| Late binding | Closure reads variable at call time | call के समय variable पढ़ना |
| Hoisting | Moving repeated work outside the loop | दोहराया काम बाहर निकालना |

---

## ⚡ 3-Line Summary
English: A list comprehension is usually 20-40% faster than a `.append()` loop because it uses the `LIST_APPEND` opcode. Use a generator expression when you only iterate once, and NumPy for big numeric data. Do not use comprehensions for side effects.
Hindi: List comprehension `LIST_APPEND` opcode की वजह से `.append()` loop से आमतौर पर 20-40% तेज़ होती है। एक बार iterate करना हो तो generator expression और बड़े numeric data के लिए NumPy लें। Side effects के लिए comprehension न लिखें।

---

## ➡️ Next Topic
**408. NumPy for Performance** — when pure-Python loops and comprehensions are still too slow, vectorized NumPy runs the loop in C.
