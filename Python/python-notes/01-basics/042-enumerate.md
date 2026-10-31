---

# 042. enumerate()
# हिंदी में: enumerate() (index के साथ item)

---

## 🔵 Simple Definition (English)
`enumerate(iterable, start=0)` wraps any iterable and yields pairs `(index, item)`. It gives you a counter and the value in one loop, so you never write `range(len(x))` or keep a manual `i += 1`.

## 🔵 सरल परिभाषा (Hindi)
`enumerate(iterable, start=0)` किसी भी iterable को लपेटकर `(index, item)` के pairs देता है। एक ही loop में counter और value दोनों मिलते हैं, इसलिए `range(len(x))` या manual `i += 1` की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Often you need the position and the value: show "1. Task", report which CSV row failed, or find where an item sits. People wrote `for i in range(len(items)): items[i]` (ugly, slow) or kept a separate counter variable (easy to forget to update). `enumerate` is the clean, standard answer.

## 🔴 यह क्यों बना? (Hindi)
अक्सर position और value दोनों चाहिए: "1. Task" दिखाना, CSV की किस row में error आया, या item कहाँ है। लोग `range(len(items))` या अलग counter लिखते थे (भद्दा और भूलने लायक)। `enumerate` इसका साफ़ standard हल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → enumerate(items, start=1) creates a lazy enumerate object
Step 2 → Each next() pulls one item from the underlying iterator
Step 3 → It pairs the item with a counter: (counter, item)
Step 4 → Counter goes up by 1 each time, beginning at start
Step 5 → Tuple unpacking in the for: for i, item in ...
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → enumerate एक lazy object बनाता है
Step 2 → हर next() पर underlying iterator से एक item आता है
Step 3 → उसे counter के साथ जोड़कर (counter, item) tuple बनता है
Step 4 → counter start से शुरू होकर हर बार 1 बढ़ता है
Step 5 → for i, item में tuple अपने आप unpack होता है
```

---

## 🟡 Real World Example
Zomato admin imports a restaurant CSV: when row 37 has a bad price, the error message says "row 37" thanks to `enumerate(rows, start=2)` (row 1 is the header). A to-do app prints a numbered list. An AI app tags each document chunk with `chunk_id` while embedding.

## 🟡 Real Example Hindi mein
Zomato admin जब restaurant CSV import करता है और row 37 में price गलत हो, तो error में "row 37" `enumerate(rows, start=2)` की वजह से आता है (row 1 header है)। To-do app numbered list दिखाता है। AI app embedding करते समय हर chunk को `chunk_id` देता है।

---

## 💻 Code Example — Basic
```python
# Basic enumerate examples - every line commented
from typing import List  # type hint helper

colors: List[str] = ["red", "green", "blue"]  # sample list

for index, color in enumerate(colors):  # unpack (index, item) pairs
    print(index, color)  # index starts at 0
# Output:
# 0 red
# 1 green
# 2 blue

for number, color in enumerate(colors, start=1):  # start counting from 1
    print(f"{number}. {color}")  # human friendly numbering
# Output:
# 1. red
# 2. green
# 3. blue

pairs = list(enumerate("abc"))  # works on strings too; list() to see it
print(pairs)  # Output: [(0, 'a'), (1, 'b'), (2, 'c')]

lookup = dict(enumerate(colors))  # build an index -> item dict
print(lookup)  # Output: {0: 'red', 1: 'green', 2: 'blue'}

e = enumerate(colors)  # an enumerate object (lazy)
print(next(e))  # first pair: Output: (0, 'red')
print(next(e))  # second pair: Output: (1, 'green')

# Find all positions of a value
nums: List[int] = [5, 1, 5, 2, 5]  # repeated values
positions: List[int] = [i for i, n in enumerate(nums) if n == 5]  # collect indexes
print(positions)  # Output: [0, 2, 4]
```

## 💻 Code Example — Advanced
```python
# Production style: row numbers in errors, first/last handling, lazy sources
import io  # in-memory file for the demo
from typing import Iterable, Iterator, List, Tuple  # type hints


def validate_rows(lines: Iterable[str]) -> List[str]:
    """Return human readable errors with the real file line number."""
    errors: List[str] = []  # collect all problems
    for line_no, line in enumerate(lines, start=2):  # line 1 is the header
        name, _, price = line.strip().partition(",")  # split "name,price"
        if not price.isdigit():  # price must be digits
            errors.append(f"line {line_no}: bad price {price!r}")  # record error
    return errors  # all errors at once


print(validate_rows(["tea,10", "coffee,abc", "milk,", "juice,50"]))
# Output: ["line 3: bad price 'abc'", "line 4: bad price ''"]

# enumerate works on files and other lazy iterators without loading everything
fake_file = io.StringIO("alpha\nbeta\ngamma\n")  # behaves like an open file
for i, text in enumerate(fake_file):  # reads one line at a time
    print(i, text.rstrip())  # strip trailing newline
# Output:
# 0 alpha
# 1 beta
# 2 gamma


def with_separator(words: List[str]) -> str:
    """Join words, adding a comma before every item except the first."""
    out: str = ""  # result string
    for i, word in enumerate(words):  # index tells us if it is first
        out += word if i == 0 else f", {word}"  # no comma before the first
    return out  # final string


print(with_separator(["a", "b", "c"]))  # Output: a, b, c


def chunk_ids(chunks: List[str]) -> Iterator[Tuple[str, str]]:
    """Tag chunks with stable ids, like in a RAG indexer."""
    for n, chunk in enumerate(chunks, start=1):  # ids begin at 1
        yield f"doc-{n:03d}", chunk  # zero padded id, e.g. doc-001


print(list(chunk_ids(["hello", "world"])))
# Output: [('doc-001', 'hello'), ('doc-002', 'world')]

# enumerate over a zip: nested unpacking needs parentheses
names: List[str] = ["Asha", "Ravi"]  # first sequence
scores: List[int] = [90, 85]  # second sequence
for rank, (who, score) in enumerate(zip(names, scores), start=1):  # (rank, (a, b))
    print(rank, who, score)  # show rank, name and score
# Output:
# 1 Asha 90
# 2 Ravi 85
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
for i, fruit in enumerate(["apple", "mango"], start=1):
    print(i, fruit)            # 1 apple, 2 mango
```

```javascript
// JavaScript
["apple", "mango"].forEach((fruit, i) => {
  console.log(i + 1, fruit);   // manual +1 for start=1
});
for (const [i, fruit] of ["apple", "mango"].entries()) {
  console.log(i, fruit);       // entries() is the closest to enumerate
}
```

Key differences: JS `forEach` and `entries()` give the index but work only on arrays (and iterables for `entries`). Python `enumerate` works on any iterable (files, generators, strings) and has a `start` argument. JS callback params are `(value, index)`; Python gives `(index, value)`, so the order is reversed.

---

## 🟠 FastAPI Connection
FastAPI handlers use `enumerate` to attach positions to results (ranking, batch item ids) and to report which item in a bulk request failed validation.

```python
# FastAPI: report which item in a bulk request is invalid (pip install fastapi)
from typing import Dict, List  # type hints
from fastapi import FastAPI, HTTPException  # app and errors

app: FastAPI = FastAPI()  # create app


@app.post("/prices")  # POST /prices with JSON list of numbers
def check_prices(prices: List[float]) -> Dict[str, int]:
    for position, price in enumerate(prices):  # position in the request body
        if price < 0:  # invalid value
            raise HTTPException(  # 422 style error with the exact location
                status_code=422,
                detail=f"price at index {position} is negative",
            )
    return {"count": len(prices)}  # everything fine
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Swapping the unpack order
```python
# Wrong - item and index are reversed:
for item, i in enumerate(["a", "b"]):
    print(item, i)      # prints 0 a  (item holds the number!)

# Correct - index first:
for i, item in enumerate(["a", "b"]):
    print(i, item)      # 0 a
```

❌ Mistake 2: Using `range(len())` or a manual counter
```python
items = ["a", "b"]

# Wrong:
i = 0
for item in items:
    print(i, item)
    i += 1              # easy to forget or misplace

# Correct:
for i, item in enumerate(items):
    print(i, item)
```

❌ Mistake 3: Expecting enumerate to be a list
```python
e = enumerate(["a", "b"])
print(list(e))   # [(0, 'a'), (1, 'b')]
print(list(e))   # []  - it is an iterator, already used up!
# e[0] would raise TypeError: 'enumerate' object is not subscriptable
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
items = ["a", "b", "c"]
for i, x in enumerate(items):
    if x == "a":
        items.append("d")
    if i > 5:
        break
print(items)

print(list(enumerate("ab", start=-1)))
```

**Answer**:
```
['a', 'b', 'c', 'd']
[(-1, 'a'), (0, 'b')]
```
`enumerate` is lazy and reads the live list, so the appended "d" is visited too (but only one "d" is added, since only "a" triggers the append). `start` can be any integer, including negative.

---

## ⚫ Interview Questions + Answers

Q1: What does `enumerate` return?
A1: A lazy `enumerate` iterator yielding `(index, item)` tuples. It does not copy the data. You can wrap it in `list()` or `dict()`, but it can be consumed only once.

Q2: How do you start counting at 1?
A2: `enumerate(items, start=1)`. The `start` only changes the counter, not which items are read, so no items are skipped.

Q3: Why is `enumerate` better than `range(len(x))`?
A3: It is more readable, avoids index mistakes, and works on iterables with no `len()` or indexing (files, generators). `range(len(x))` plus `x[i]` also does an extra lookup each time.

Q4: Can you use `enumerate` with a dict?
A4: Yes: `for i, (k, v) in enumerate(d.items())`. Note the parentheses for nested unpacking. Plain `enumerate(d)` gives `(index, key)`.

Q5: How do you get both index and values from two lists?
A5: `for i, (a, b) in enumerate(zip(list_a, list_b))`. `zip` pairs the values; `enumerate` adds the index.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need position and value together
- Error messages should mention the row or index
- Numbering output (`start=1`)

❌ Avoid when:
- You only need the values (plain `for x in items`)
- You only need the count (use `len()`)
- You need to look at neighbours often (use `zip(items, items[1:])`)

---

## 📊 Visual Diagram

```
 items:         "red"    "green"   "blue"
                  │         │         │
 enumerate(...,1) ▼         ▼         ▼
                (1,"red") (2,"green") (3,"blue")
                  │
        for n, color in ... → n=1, color="red"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| enumerate | Adds a counter to an iterable | iterable में counter जोड़ता है |
| start | First counter value | counter की शुरुआती value |
| Tuple unpacking | `i, x = (0, "a")` | tuple को अलग-अलग names में बाँटना |
| Iterator | Single-use stream of items | एक बार चलने वाली stream |
| Index | Position of an item | item की position |
| Lazy | Produced on demand | माँगने पर बनता है |

---

## ⚡ 3-Line Summary
English: `enumerate(iterable, start=0)` yields `(index, item)` pairs lazily. It replaces `range(len(x))` and manual counters, and works on files and generators too. Remember: index comes first, and the object is single-use.
Hindi: `enumerate(iterable, start=0)` lazily `(index, item)` pairs देता है। यह `range(len(x))` और manual counter की जगह लेता है, files और generators पर भी चलता है। याद रखें: index पहले आता है और object एक बार ही चलता है।

---

## ➡️ Next Topic
**043. zip()** — walk two or more iterables side by side and pair their items.
