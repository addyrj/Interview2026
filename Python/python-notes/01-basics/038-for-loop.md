---

# 038. for Loop
# हिंदी में: for Loop (बार-बार दोहराना)

---

## 🔵 Simple Definition (English)
A `for` loop in Python walks over every item of an iterable (list, string, dict, file, generator...) one by one. You do not manage an index counter yourself. Python asks the iterable for the next item until it says "no more".

## 🔵 सरल परिभाषा (Hindi)
Python का `for` loop किसी iterable (list, string, dict, file, generator) के हर item पर एक-एक करके चलता है। Index counter आपको खुद संभालना नहीं पड़ता। Python iterable से अगला item माँगता रहता है, जब तक items खत्म न हों।

---

## 🔴 Problem it Solves
In C and old JavaScript you wrote `for (i = 0; i < n; i++)` and then `arr[i]`. This causes off-by-one bugs, wrong bounds, and noisy code. Python's `for` removes the counter: you say "for each item in this collection" and the language handles iteration, even for things that have no length (streams, generators, DB cursors).

## 🔴 यह क्यों बना? (Hindi)
C और पुराने JavaScript में `for (i = 0; i < n; i++)` लिखना पड़ता था, जिससे off-by-one bugs होते थे। Python का `for` counter हटा देता है: "इस collection के हर item के लिए" बोलो, बाकी Python संभालता है। Generators, DB cursors, files जैसी चीज़ों पर भी यही चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python calls iter(obj)       → gets an iterator object
Step 2 → Python calls next(iterator)  → gets first item
Step 3 → Item is bound to loop variable (for item in ...)
Step 4 → Loop body runs
Step 5 → Go to Step 2; when StopIteration is raised → loop ends
Step 6 → Optional else block runs ONLY if loop was not broken by break
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → iter(obj) से iterator बनता है
Step 2 → next(iterator) से अगला item आता है
Step 3 → Item loop variable में जाता है, body चलती है
Step 4 → StopIteration आते ही loop खत्म
Step 5 → else block सिर्फ तब चलता है जब break नहीं हुआ
```

---

## 🟡 Real World Example
Swiggy order service: a cart has many items. A `for` loop walks every cart item, adds `price * qty`, and builds the bill. Razorpay settlement jobs loop over thousands of transactions. An AI app loops over document chunks to embed each one before storing them in a vector DB.

## 🟡 Real Example Hindi mein
Swiggy में cart के हर item पर `for` loop चलता है, `price * qty` जोड़कर bill बनता है। Razorpay settlement job हज़ारों transactions पर loop करती है। AI app में document के हर chunk को embed करने के लिए loop चलता है।

---

## 💻 Code Example — Basic
```python
# Basic for loop examples - every line commented
from typing import Dict, List  # import type helpers for hints

fruits: List[str] = ["apple", "mango", "banana"]  # a list of strings

for fruit in fruits:  # loop variable 'fruit' takes each item in turn
    print(fruit.upper())  # print the item in upper case
# Output:
# APPLE
# MANGO
# BANANA

for ch in "Hey":  # strings are iterable, one character at a time
    print(ch)  # print each character
# Output:
# H
# e
# y

prices: Dict[str, int] = {"tea": 10, "coffee": 30}  # dict name -> price

for name, price in prices.items():  # items() gives (key, value) pairs, unpacked
    print(f"{name} costs {price}")  # f-string formatting
# Output:
# tea costs 10
# coffee costs 30

total: int = 0  # accumulator for the sum
for price in prices.values():  # values() iterates only the values
    total += price  # add each price to total
print(total)  # Output: 40

for n in [1, 3, 5, 6, 7]:  # numbers, one of them is even
    if n % 2 == 0:  # check for an even number
        print("found even", n)  # report it
        break  # stop the loop early
else:  # runs only when the loop finished WITHOUT break
    print("no even number")  # not printed here, because we broke out
# Output:
# found even 6
```

## 💻 Code Example — Advanced
```python
# Production style: for loop with generators, unpacking, nested loops, else
from dataclasses import dataclass  # lightweight data class
from typing import Iterator, List, Optional  # type hints


@dataclass  # auto-generates __init__ and __repr__
class CartItem:
    name: str  # product name
    price: float  # unit price
    qty: int  # quantity


def read_cart() -> Iterator[CartItem]:  # generator: yields items lazily
    yield CartItem("pizza", 250.0, 2)  # first item
    yield CartItem("coke", 40.0, 3)  # second item
    yield CartItem("garlic bread", 90.0, 1)  # third item


def bill_total(items: Iterator[CartItem]) -> float:  # compute total
    total: float = 0.0  # running total
    for item in items:  # works on generators too, no len() needed
        total += item.price * item.qty  # add line total
    return total  # final amount


print(bill_total(read_cart()))  # Output: 710.0


def find_user(users: List[str], target: str) -> Optional[int]:  # search helper
    for idx, user in enumerate(users):  # idx + value together
        if user == target:  # match found
            return idx  # return immediately
    return None  # loop ended with no match


print(find_user(["a", "b", "c"], "c"))  # Output: 2
print(find_user(["a", "b", "c"], "z"))  # Output: None

# Nested loops: build a multiplication grid
for i in range(1, 3):  # outer loop: 1, 2
    row: List[int] = []  # collects one row
    for j in range(1, 4):  # inner loop: 1, 2, 3
        row.append(i * j)  # store product
    print(row)  # print the row
# Output:
# [1, 2, 3]
# [2, 4, 6]

# Loop variable leaks after the loop (unlike let in JS)
for k in range(3):  # k goes 0, 1, 2
    pass  # do nothing
print(k)  # Output: 2  (k still exists after the loop)

# Never modify a list while iterating; iterate over a copy
nums: List[int] = [1, 2, 3, 4]  # original list
for n in nums[:]:  # [:] makes a shallow copy to iterate
    if n % 2 == 0:  # even numbers
        nums.remove(n)  # safe, because we iterate the copy
print(nums)  # Output: [1, 3]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
items = ["a", "b", "c"]
for item in items:                 # value directly
    print(item)
for i, item in enumerate(items):   # index + value
    print(i, item)
d = {"x": 1, "y": 2}
for key, value in d.items():       # dict iteration
    print(key, value)
```

```javascript
// JavaScript
const items = ["a", "b", "c"];
for (const item of items) {        // value (for...of)
  console.log(item);
}
items.forEach((item, i) => console.log(i, item));  // index + value
for (const i in items) {}          // for...in gives KEYS/indexes (strings!)
const d = { x: 1, y: 2 };
for (const [key, value] of Object.entries(d)) {    // dict-like iteration
  console.log(key, value);
}
```

Key differences: Python `for x in` = JS `for...of`. Python has no C-style `for(;;)`. Python `for` has an `else` clause; JS does not. Python loop variable stays alive after the loop; JS `let/const` is block-scoped.

---

## 🟠 FastAPI Connection
FastAPI endpoints constantly loop: over DB rows to build response models, over uploaded files, and over chunks in `StreamingResponse`. A generator inside `for` keeps memory low for large exports.

```python
# FastAPI: loop over items and stream a CSV (needs: pip install fastapi)
from typing import Iterator, List  # type hints
from fastapi import FastAPI  # the app class
from fastapi.responses import StreamingResponse  # streaming response

app: FastAPI = FastAPI()  # create the app
ORDERS: List[dict] = [{"id": i, "amount": i * 100} for i in range(1, 4)]  # fake data


def csv_rows() -> Iterator[str]:  # generator of CSV lines
    yield "id,amount\n"  # header row
    for order in ORDERS:  # for loop over each order
        yield f"{order['id']},{order['amount']}\n"  # one CSV line at a time


@app.get("/export")  # GET /export
def export() -> StreamingResponse:  # returns streamed content
    return StreamingResponse(csv_rows(), media_type="text/csv")  # stream it
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `range(len(x))` when you only need the items
```python
items = ["a", "b", "c"]

# Wrong (C-style, noisy):
for i in range(len(items)):
    print(items[i])

# Correct (Pythonic):
for item in items:
    print(item)
# Need index too? Use: for i, item in enumerate(items):
```

❌ Mistake 2: Modifying a list while looping over it
```python
nums = [1, 2, 3, 4]

# Wrong - skips items because the list shrinks during iteration:
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)   # [1, 3]  works here by luck; try [2, 4, 6] -> [4]

# Correct - build a new list:
nums = [n for n in [1, 2, 3, 4] if n % 2 != 0]   # [1, 3]
```

❌ Mistake 3: Looping over a dict and expecting values
```python
d = {"a": 1, "b": 2}
for x in d:          # x is the KEY, not the value
    print(x)         # a, b
for v in d.values(): # correct way to get values
    print(v)         # 1, 2
```

---

## 🧠 Tricky Interview Question

**Q**: What will this print?

```python
for i in range(3):
    pass
else:
    print("done", i)

for j in range(3):
    if j == 1:
        break
else:
    print("never printed")
print(j)
```

**Answer**: It prints `done 2`, then `1`. The first loop never breaks, so its `else` runs and `i` is still 2. The second loop breaks at `j == 1`, so its `else` is skipped, and `j` stays 1. The `else` of a loop means "no break happened", not "otherwise".

---

## ⚫ Interview Questions + Answers

Q1: What does `for x in obj` do internally?
A1: It calls `iter(obj)` to get an iterator, then repeatedly calls `next()` on it. When `StopIteration` is raised, the loop ends silently. Any object with `__iter__` (or `__getitem__` with integer indexes) can be looped over.

Q2: What is the `for...else` clause?
A2: The `else` block runs when the loop finishes normally, meaning no `break` happened. It is useful for search loops: "if I did not find it, do X". If the iterable is empty, `else` still runs.

Q3: Difference between iterable and iterator?
A3: An iterable can produce an iterator (has `__iter__`), e.g. list, str, dict. An iterator has `__next__` and remembers its position, and is used up once consumed. A list can be looped many times; a generator only once.

Q4: How do you loop over a dict safely while changing it?
A4: Changing dict size during iteration raises `RuntimeError`. Loop over `list(d.items())` (a copy) or build a new dict with a comprehension.

Q5: When should you prefer a comprehension to a for loop?
A5: When you build a new list/dict/set from a simple transform or filter. Use a normal `for` when the body has side effects, multiple statements, or needs `break`/`continue`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You know the collection to walk over (list, dict, file, generator)
- You need side effects per item (save to DB, call an API)
- You need `break`, `continue` or early `return`

❌ Avoid when:
- A comprehension, `sum()`, `any()`, `all()` or `map()` says it more clearly
- Heavy numeric work on big arrays (use NumPy vectorization, it is far faster)
- The number of iterations depends on a changing condition (use `while`)

---

## 📊 Visual Diagram

```
 iterable ──iter()──► iterator ──next()──► item ──► loop body
                          ▲                             │
                          └─────────────────────────────┘
                 StopIteration ──► exit loop ──► else (if no break)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iterable | Object you can loop over | जिस पर loop चल सके |
| Iterator | Object that gives next item | अगला item देने वाला object |
| StopIteration | Signal that items are finished | items खत्म होने का signal |
| Loop variable | Name bound to current item | मौजूदा item का नाम |
| for...else | else runs if no break | break न हो तो else चलता है |
| Generator | Lazy iterator made with yield | yield वाला lazy iterator |

---

## ⚡ 3-Line Summary
English: A Python `for` loop iterates over any iterable using `iter()` and `next()`, with no manual counter. Use `enumerate` for indexes and `.items()` for dict pairs. The `else` clause runs only if the loop was not stopped by `break`.
Hindi: Python का `for` किसी भी iterable पर `iter()` और `next()` से चलता है, counter की ज़रूरत नहीं। Index के लिए `enumerate`, dict के लिए `.items()`। `else` तभी चलता है जब `break` न हुआ हो।

---

## ➡️ Next Topic
**039. while Loop** — loops that run on a condition instead of a collection, infinite loops, and retry patterns.
