---

# 053. List Comprehension
# हिंदी में: List Comprehension (एक line में list बनाना)

---

## 🔵 Simple Definition (English)
A list comprehension is a compact way to build a new list from any iterable: `[expression for item in iterable if condition]`. It replaces the "create empty list, loop, append" pattern with a single readable line. It is usually faster than the equivalent loop with `append`.

## 🔵 सरल परिभाषा (Hindi)
List comprehension किसी भी iterable से नई list बनाने का छोटा तरीका है: `[expression for item in iterable if condition]`। यह "खाली list बनाओ, loop चलाओ, append करो" वाले pattern को एक पढ़ने लायक line में बदल देता है। आम तौर पर यह `append` वाले loop से तेज़ भी होता है।

---

## 🔴 Problem it Solves
Transforming and filtering data is the most common job in programs. The loop version takes 4 lines and a temporary variable, and the real intent (`squares of even numbers`) is hidden in mechanics. Comprehensions state the intent directly and are executed with optimized bytecode.

## 🔴 यह क्यों बना? (Hindi)
Data को बदलना और filter करना सबसे आम काम है। Loop वाले तरीके में 4 lines और एक temporary variable लगते हैं और असली मकसद (even numbers के squares) छुप जाता है। Comprehension मकसद सीधे बताता है और optimized bytecode से चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → [ x*x  for x in nums  if x % 2 == 0 ]
Step 2 → Python creates a NEW hidden function scope (x does not leak out in Python 3)
Step 3 → Loop: takes each x from nums
Step 4 → if-clause: keep x only when condition is True (filter)
Step 5 → expression x*x is evaluated for kept items (transform)
Step 6 → Results are collected into a brand new list
Step 7 → Nested: [a for row in matrix for a in row] — loops read LEFT to RIGHT, like nested for loops
Step 8 → Ternary goes BEFORE the for:  [x if x > 0 else 0 for x in nums]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → [ x*x  for x in nums  if x % 2 == 0 ]
Step 2 → Python अलग hidden scope बनाता है (x बाहर leak नहीं होता)
Step 3 → nums से एक-एक x लिया जाता है
Step 4 → if शर्त True हो तभी x रखा जाता है (filter)
Step 5 → रखे गए items पर expression x*x चलता है (transform)
Step 6 → नतीजे एक नई list में जमा होते हैं
Step 7 → Nested: loops बाएँ से दाएँ पढ़ें, nested for loops की तरह
Step 8 → ternary (if-else) for से पहले लिखते हैं
```

---

## 🟡 Real World Example
Razorpay settlement report: from a list of transactions, take only successful ones and extract amounts: `[t["amount"] for t in txns if t["status"] == "success"]`. An AI app cleans user messages: `[m.strip().lower() for m in messages if m.strip()]` before sending them to an embedding model.

## 🟡 Real Example Hindi mein
Razorpay settlement report: transactions में से सिर्फ successful चुनकर amounts निकालना: `[t["amount"] for t in txns if t["status"] == "success"]`। AI app में embedding से पहले messages साफ़ करना: `[m.strip().lower() for m in messages if m.strip()]`।

---

## 💻 Code Example — Basic
```python
# Basic list comprehensions

nums: list[int] = [1, 2, 3, 4, 5, 6]  # sample numbers

# Loop version (for comparison)
squares_loop: list[int] = []  # start empty
for n in nums:  # visit each number
    squares_loop.append(n * n)  # add its square
print(squares_loop)  # Output: [1, 4, 9, 16, 25, 36]

# Comprehension version: same result, one line
squares: list[int] = [n * n for n in nums]  # expression for item in iterable
print(squares)  # Output: [1, 4, 9, 16, 25, 36]

# With a filter (if at the end)
even_squares: list[int] = [n * n for n in nums if n % 2 == 0]  # keep only even n
print(even_squares)  # Output: [4, 16, 36]

# Transform strings
names: list[str] = ["  priya ", "RAHUL", " amit"]  # messy names
clean: list[str] = [s.strip().title() for s in names]  # strip spaces, Title Case
print(clean)  # Output: ['Priya', 'Rahul', 'Amit']

# Ternary (if-else) goes BEFORE the for
labels: list[str] = ["even" if n % 2 == 0 else "odd" for n in nums]  # label each number
print(labels)  # Output: ['odd', 'even', 'odd', 'even', 'odd', 'even']

# Loop variable does not leak in Python 3
_ = [m for m in range(3)]  # comprehension variable m lives in its own scope
print("m" in dir())  # m did not leak out -> Output: False
```

## 💻 Code Example — Advanced
```python
# Production style: nested comprehensions, flattening, dedupe, generator vs list, walrus
import sys  # to compare memory sizes
from typing import Any  # for loosely typed records

# 1. Flatten a matrix (read loops left to right)
matrix: list[list[int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 3x3 grid
flat: list[int] = [v for row in matrix for v in row]  # outer loop first, then inner
print(flat)  # Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 2. Transpose a matrix (nested comprehension builds list of lists)
transposed: list[list[int]] = [[row[i] for row in matrix] for i in range(3)]  # columns become rows
print(transposed)  # Output: [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# 3. Cartesian product with a condition
pairs: list[tuple[int, int]] = [(a, b) for a in range(1, 4) for b in range(1, 4) if a < b]  # unique ordered pairs
print(pairs)  # Output: [(1, 2), (1, 3), (2, 3)]

# 4. Filter records and extract a field
txns: list[dict[str, Any]] = [  # sample transactions
    {"id": 1, "amount": 500, "status": "success"},
    {"id": 2, "amount": 200, "status": "failed"},
    {"id": 3, "amount": 900, "status": "success"},
]
paid: list[int] = [t["amount"] for t in txns if t["status"] == "success"]  # amounts of successful ones
print(paid, sum(paid))  # Output: [500, 900] 1400

# 5. Walrus operator: compute once, use in filter AND output
raw: list[str] = [" a ", "  ", "b", ""]  # raw input with blanks
cleaned: list[str] = [s for item in raw if (s := item.strip())]  # strip once, keep non-empty
print(cleaned)  # Output: ['a', 'b']

# 6. Dedupe while keeping order (using a set as helper)
seen: set[int] = set()  # remember what we have seen
data: list[int] = [3, 1, 3, 2, 1]  # duplicates present
unique: list[int] = [x for x in data if not (x in seen or seen.add(x))]  # seen.add returns None (falsy)
print(unique)  # Output: [3, 1, 2]
# (simpler and clearer: list(dict.fromkeys(data)))
print(list(dict.fromkeys(data)))  # Output: [3, 1, 2]

# 7. List vs generator expression: memory
big_list: list[int] = [i for i in range(100_000)]  # builds everything in memory
big_gen = (i for i in range(100_000))  # lazy, produces one at a time
print(sys.getsizeof(big_list) > sys.getsizeof(big_gen))  # Output: True
print(sum(i for i in range(5)))  # generator inside sum, no [] needed -> Output: 10

# 8. Avoid: do not use comprehension only for side effects
# [print(x) for x in range(3)]   # builds a useless list of None; use a for loop
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: one expression
nums: list[int] = [1, 2, 3, 4, 5, 6]
result: list[int] = [n * n for n in nums if n % 2 == 0]   # filter + map
print(result)                                              # [4, 16, 36]

flat: list[int] = [v for row in [[1, 2], [3, 4]] for v in row]   # flatten
print(flat)                                                # [1, 2, 3, 4]
```
```javascript
// JavaScript: chain filter / map / flat
const nums = [1, 2, 3, 4, 5, 6];
const result = nums.filter(n => n % 2 === 0).map(n => n * n);   // [4, 16, 36]
const flat = [[1, 2], [3, 4]].flat();                           // [1, 2, 3, 4]
// JS creates intermediate arrays at each step; the Python comprehension builds one list.
```

---

## 🟠 FastAPI Connection
Comprehensions are everywhere in FastAPI code: converting ORM rows to response models, building lists of IDs for queries, and shaping data before returning it.

```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # response models

app: FastAPI = FastAPI()  # create app

class UserOut(BaseModel):  # response schema
    id: int  # user id
    name: str  # user name

DB: list[dict[str, object]] = [{"id": 1, "name": "Priya", "active": True}, {"id": 2, "name": "Rahul", "active": False}]  # fake table

@app.get("/users", response_model=list[UserOut])  # GET /users
async def active_users() -> list[UserOut]:
    return [UserOut(id=int(u["id"]), name=str(u["name"])) for u in DB if u["active"]]  # filter + convert in one line
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Making it too complex to read
```python
# Wrong: three nested conditions in one line
result = [f(x, y) for x in xs if x > 0 for y in ys if y != x if g(x, y)]

# Right: break it into a function or a normal loop when it needs more than ~2 clauses
def build() -> list[int]:
    out: list[int] = []
    for x in xs:
        ...
    return out
```

❌ Mistake 2: Using it only for side effects
```python
# Wrong:
[print(x) for x in range(3)]     # creates [None, None, None] and throws it away

# Right:
for x in range(3):
    print(x)
```

❌ Mistake 3: Putting if-else at the END
```python
# Wrong:
# [x for x in nums if x > 0 else 0]     # SyntaxError

# Right: ternary goes in the expression part
[x if x > 0 else 0 for x in nums]
```

---

## 🧠 Tricky Interview Question

```python
rows = [[0] * 3] * 3
rows[0][0] = 1
print(rows)

rows2 = [[0] * 3 for _ in range(3)]
rows2[0][0] = 1
print(rows2)
```
Answer: First prints `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`: `[x] * 3` repeats the SAME inner list object three times, so changing one row changes all. Second prints `[[1, 0, 0], [0, 0, 0], [0, 0, 0]]`: the comprehension runs `[0] * 3` freshly for each row, creating three separate lists. Always build 2D grids with a comprehension.

---

## ⚫ Interview Questions + Answers

Q1: What is the syntax of a list comprehension and what does each part do?
A1: `[expr for item in iterable if cond]`. The `for` iterates, the optional `if` filters items, and `expr` transforms each kept item. A ternary `[a if c else b for ...]` is allowed in the expression part and is different from the filter `if`.

Q2: Are list comprehensions faster than for loops?
A2: Usually yes (roughly 10 to 30 percent), because the append is done by a specialized bytecode instead of a method lookup and call each iteration. They are also more readable when simple. The gain is small, so choose them for clarity first.

Q3: What is the difference between a list comprehension and a generator expression?
A3: `[x*x for x in data]` builds the whole list in memory immediately. `(x*x for x in data)` is lazy, yields one value at a time and uses constant memory, but can be iterated only once. Use generators for big data and when passing to `sum`, `any`, `all`, `max`.

Q4: Does the loop variable leak out of a comprehension?
A4: Not in Python 3. A comprehension has its own scope, so `[x for x in range(3)]` leaves no `x` behind. In Python 2 it leaked. (A `for` loop statement still leaks its variable.)

Q5: How do you flatten a list of lists?
A5: `[v for row in matrix for v in row]` (outer loop first, inner loop second, same as nested for loops). Alternatives: `itertools.chain.from_iterable(matrix)` which is lazy and fast, or `sum(matrix, [])` which is slow (O(n^2)) and not recommended.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple map and/or filter creating a new list
- Flattening or transposing small nested lists
- Building 2D grids safely

❌ Avoid when:
- Logic needs multiple statements or try/except
- More than two loops or conditions make it hard to read
- You only want side effects (use a for loop)
- Data is huge and you only iterate once (use a generator expression)

---

## 📊 Visual Diagram
```
 [ n * n   for n in nums   if n % 2 == 0 ]
   ──┬──   ─────┬──────    ──────┬──────
     │          │                │
  OUTPUT     SOURCE           FILTER
  (transform) (loop)          (keep or drop)

 nums = 1 2 3 4 5 6
        │ │ │ │ │ │      filter evens
        ▼ ▼ ▼ ▼ ▼ ▼
          2   4   6      square
          4  16  36  ->  [4, 16, 36]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comprehension | Compact syntax to build a collection | collection बनाने का छोटा syntax |
| Iterable | Anything you can loop over | जिस पर loop चल सके |
| Filter clause | The trailing `if` condition | अंत वाली `if` शर्त |
| Ternary | `a if c else b` expression | एक-line if-else |
| Generator expression | Lazy version with `()` | `()` वाला lazy version |
| Walrus `:=` | Assign inside an expression | expression के अंदर assignment |

---

## ⚡ 3-Line Summary
English: A list comprehension `[expr for x in it if cond]` builds a new list by transforming and filtering an iterable in one line. Keep it simple and readable; switch to a loop or function when it gets complex. Use a generator expression when you do not need the whole list in memory.
Hindi: List comprehension `[expr for x in it if cond]` एक line में iterable को transform और filter करके नई list बनाता है। इसे सरल रखें; जटिल हो तो loop या function लें। पूरी list memory में नहीं चाहिए तो generator expression लें।

---

## ➡️ Next Topic
**054. List Slicing** — extract, copy, reverse and replace parts of a list with `lst[start:stop:step]`.
