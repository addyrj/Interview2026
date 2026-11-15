---

# 120. zip() + enumerate()
# हिंदी में: zip() और enumerate() (दो iterables जोड़ना और index के साथ loop)

---

## 🔵 Simple Definition (English)
`zip()` walks over several iterables together and gives you tuples of matching items. `enumerate()` walks over one iterable and gives you `(index, item)` pairs. Both are lazy: they produce values one at a time.

## 🔵 सरल परिभाषा (Hindi)
`zip()` कई iterables पर एक साथ चलता है और हर position के items का tuple देता है। `enumerate()` एक iterable पर चलता है और `(index, item)` जोड़े देता है। दोनों lazy हैं: values एक-एक करके बनती हैं।

---

## 🔴 Problem it Solves
In C-style code you write `for i in range(len(a)): a[i], b[i]`. It is noisy and easy to get wrong (off-by-one, index errors). `zip` and `enumerate` remove manual index handling, work on any iterable (lists, files, generators) and make the code read like the intent: "pair these two", "number these items".

## 🔴 यह क्यों बना? (Hindi)
C-style code में `for i in range(len(a)): a[i], b[i]` लिखना पड़ता है। यह गंदा है और गलती (off-by-one, IndexError) आसानी से होती है। `zip` और `enumerate` manual index हटा देते हैं, किसी भी iterable (list, file, generator) पर चलते हैं और code वही पढ़ता है जो इरादा है: "इन दोनों को जोड़ो", "इन items को number दो"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → zip(a, b) calls iter() on each argument
Step 2 → Each next() call pulls ONE item from each iterator -> tuple (x, y)
Step 3 → It stops as soon as the SHORTEST iterator ends (default)
Step 4 → strict=True (3.10+) raises ValueError if lengths differ
Step 5 → enumerate(it, start=0) keeps a counter, yields (counter, item)
Step 6 → Both return iterators: use list()/dict() to materialize, they can be used only once

zip([1,2,3], "ab")  ->  (1,'a'), (2,'b')      # 3 is dropped silently
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → zip(a, b) हर argument पर iter() बुलाता है
Step 2 → हर next() पर हर iterator से एक item लेकर tuple (x, y) बनता है
Step 3 → सबसे छोटा iterator खत्म होते ही रुक जाता है (default)
Step 4 → strict=True (3.10+) में लंबाई अलग हो तो ValueError आता है
Step 5 → enumerate(it, start=0) एक counter रखता है, (counter, item) देता है
Step 6 → दोनों iterator लौटाते हैं: list()/dict() से materialize करो, इन्हें सिर्फ एक बार use कर सकते हैं
```

---

## 🟡 Real World Example
A Zomato-like backend has `names = [...]` and `prices = [...]` coming from two DB columns: `zip` builds the menu dict. A Razorpay settlement report numbers each row with `enumerate(rows, start=1)`. A CSV importer reports "row 17 is invalid" using `enumerate` so users can fix their file.

## 🟡 Real Example Hindi mein
Zomato जैसे backend में `names` और `prices` दो DB columns से आते हैं: `zip` से menu dict बनता है। Razorpay का settlement report हर row को `enumerate(rows, start=1)` से number देता है। CSV importer "row 17 गलत है" बताने के लिए `enumerate` use करता है ताकि user अपनी file ठीक कर सके।

---

## 💻 Code Example — Basic
```python
# Basic zip and enumerate
from itertools import zip_longest                  # pads shorter iterables

names: list[str] = ["Asha", "Ravi", "Meena"]       # customer names
prices: list[int] = [250, 180, 320]                # matching order totals

for n, p in zip(names, prices):                    # pair the two lists
    print(n, p)                                    # one pair per line

print(list(zip([1, 2, 3], "ab")))                  # shortest wins: 3 is dropped
for i, n in enumerate(names, start=1):             # numbering from 1, not 0
    print(i, n)                                    # index and name
print(dict(zip(names, prices)))                    # build a dict from two lists

pairs: list[tuple[int, str]] = [(1, "a"), (2, "b")]   # list of pairs
nums, letters = zip(*pairs)                        # zip(*x) "unzips" (transpose)
print(nums, letters)                               # two tuples

try:                                               # strict mode catches bad data
    list(zip([1, 2], [1], strict=True))            # lengths differ -> error (3.10+)
except ValueError as e:                            # catch it
    print("Error:", e)                             # explain the mismatch

print(list(zip_longest([1, 2, 3], "a", fillvalue="-")))   # pad instead of dropping

# Output:
# Asha 250
# Ravi 180
# Meena 320
# [(1, 'a'), (2, 'b')]
# 1 Asha
# 2 Ravi
# 3 Meena
# {'Asha': 250, 'Ravi': 180, 'Meena': 320}
# (1, 2) ('a', 'b')
# Error: zip() argument 2 is shorter than argument 1
# [(1, 'a'), (2, '-'), (3, '-')]
```

## 💻 Code Example — Advanced
```python
# Production style: validate CSV-like rows, build records, sliding pairs
from dataclasses import dataclass                  # simple record type
from itertools import islice                       # take a slice of an iterator


@dataclass(frozen=True)                            # immutable record
class Order:
    order_id: int                                  # unique id
    user: str                                      # who ordered
    amount: float                                  # rupees


def parse_orders(ids: list[int], users: list[str], amounts: list[float]) -> list[Order]:
    """Build Orders from three parallel columns; reject uneven columns."""
    try:                                           # strict zip detects bad input
        rows = list(zip(ids, users, amounts, strict=True))   # 3-way zip
    except ValueError as e:                        # columns have different lengths
        raise ValueError(f"column length mismatch: {e}") from e   # clearer error
    return [Order(i, u, a) for i, u, a in rows]    # tuple unpacking in comprehension


def find_bad_rows(rows: list[dict[str, str]]) -> list[int]:
    """Return 1-based row numbers whose amount is not a number."""
    bad: list[int] = []                            # collect problem rows
    for line_no, row in enumerate(rows, start=1):  # human-friendly numbering
        try:                                       # try converting
            float(row["amount"])                   # may raise ValueError
        except ValueError:                         # not a number
            bad.append(line_no)                    # remember the row number
    return bad                                     # all bad row numbers


def deltas(values: list[int]) -> list[int]:
    """Difference between consecutive values using zip(a, a[1:])."""
    return [b - a for a, b in zip(values, values[1:])]   # sliding window of 2


orders = parse_orders([1, 2], ["asha", "ravi"], [99.5, 10.0])   # works
print(orders[0])                                   # frozen dataclass repr
try:                                               # now an uneven column
    parse_orders([1, 2, 3], ["asha"], [1.0])       # users column too short
except ValueError as e:                            # caught
    print("Error:", e)                             # mismatch message
print(find_bad_rows([{"amount": "10"}, {"amount": "abc"}, {"amount": "7.5"}]))
print(deltas([10, 12, 15, 15, 20]))                # day-over-day change
lazy = zip(range(10**9), "abc")                    # lazy: no billion-item list built
print(list(islice(lazy, 2)))                       # take only 2 pairs
it = zip([1, 2], [3, 4])                           # a one-shot iterator
print(list(it), list(it))                          # second use is empty!

# Output:
# Order(order_id=1, user='asha', amount=99.5)
# Error: column length mismatch: zip() argument 2 is shorter than argument 1
# [2]
# [2, 3, 0, 5]
# [(0, 'a'), (1, 'b')]
# [(1, 3), (2, 4)] []
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Index + item | `enumerate(arr)` | `arr.entries()` / `arr.forEach((x, i) => ...)` |
| Pair two lists | `zip(a, b)` | none built in: `a.map((x, i) => [x, b[i]])` |
| Unequal lengths | stops at shortest (or `strict=True`) | `undefined` for missing items |
| Result type | lazy iterator | array (eager) |
| Start index | `enumerate(x, start=1)` | manual `i + 1` |

```python
# Python way
names = ["a", "b"]                                 # list one
ages = [20, 30]                                    # list two
print(list(zip(names, ages)))                      # [('a', 20), ('b', 30)]
for i, n in enumerate(names, start=1):             # index from 1
    print(i, n)                                    # 1 a / 2 b
```
```javascript
// JavaScript way
const names = ["a", "b"], ages = [20, 30];         // two arrays
const zipped = names.map((n, i) => [n, ages[i]]);  // manual zip (breaks if lengths differ)
names.forEach((n, i) => console.log(i + 1, n));    // manual +1
```

Key difference: JavaScript has no `zip`; you index the second array by hand and a longer first array gives `undefined`. Python's `zip` is lazy and safe, and `strict=True` turns silent length bugs into errors.

---

## 🟠 FastAPI Connection
FastAPI handlers often receive parallel lists (for example `ids` and `quantities` as repeated query params). `zip(..., strict=True)` validates them cleanly, and a 422/400 response tells the client the lists must match. `enumerate` is handy for reporting which item of a bulk request failed.

```python
# FastAPI example — bulk request validation with zip(strict=True)
from fastapi import FastAPI, HTTPException, Query  # app, error class, query helper

app: FastAPI = FastAPI()                           # create app


@app.get("/cart/total")                            # GET /cart/total?prices=10&prices=20&qty=1&qty=2
def cart_total(prices: list[float] = Query(), qty: list[int] = Query()) -> dict[str, float]:
    try:                                           # lengths must match
        pairs = list(zip(prices, qty, strict=True))   # pair price with quantity
    except ValueError:                             # mismatch -> client error
        raise HTTPException(status_code=400, detail="prices and qty must have same length")
    return {"total": sum(p * q for p, q in pairs)} # 10*1 + 20*2 = 50.0
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the zip result twice
✅ Correct: convert to a list if you need it more than once

```python
z = zip([1, 2], [3, 4])
# Wrong
print(list(z), list(z))          # [(1, 3), (2, 4)] []   <- exhausted
# Right
z = list(zip([1, 2], [3, 4]))    # materialize once
print(z, z)                      # [(1, 3), (2, 4)] [(1, 3), (2, 4)]
```

❌ Mistake 2: Silently losing data when lengths differ
✅ Correct: use `strict=True` or `zip_longest`

```python
# Wrong — 3 vanishes without a warning
print(list(zip([1, 2, 3], ["a", "b"])))             # [(1, 'a'), (2, 'b')]
# Right — fails loudly (Python 3.10+)
# list(zip([1, 2, 3], ["a", "b"], strict=True))     # ValueError
```

❌ Mistake 3: `range(len(x))` instead of `enumerate`
✅ Correct: `enumerate`

```python
items = ["x", "y"]
# Wrong
for i in range(len(items)):
    print(i, items[i])
# Right
for i, item in enumerate(items):
    print(i, item)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
a = [1, 2, 3]
z = zip(a, a)
print(list(z))
print(list(z))
for i, x in enumerate("ab", 10):
    print(i, x)
print(dict(zip("aab", [1, 2, 3])))
```
Answer: First `list(z)` gives `[(1, 1), (2, 2), (3, 3)]`, the second gives `[]` because a zip object is a one-shot iterator. The enumerate loop prints `10 a` and `11 b` (the second positional argument is `start`). The dict is `{'a': 2, 'b': 3}`: the key `'a'` appears twice and the later value wins.

---

## ⚫ Interview Questions + Answers

Q1: What does `zip(*matrix)` do?
A1: The `*` unpacks the rows as separate arguments, so `zip` pairs the first items of every row, then the second items, and so on. It transposes the matrix: `list(zip(*[[1, 2], [3, 4]]))` gives `[(1, 3), (2, 4)]`.

Q2: What happens when the iterables have different lengths?
A2: Default `zip` stops at the shortest and drops the rest silently. `zip(..., strict=True)` (Python 3.10+) raises `ValueError`. `itertools.zip_longest` pads with `fillvalue` (default `None`).

Q3: Is `zip` in Python 3 a list?
A3: No. In Python 2 it returned a list; in Python 3 it returns a lazy iterator, so it uses O(1) memory and can be used with infinite iterators, but it can be consumed only once.

Q4: What is the `start` argument of `enumerate` for?
A4: It sets the first counter value (default 0). Use `start=1` for human-facing numbering like line numbers or leaderboard ranks. It does not skip items.

Q5: How do you iterate a dict with an index?
A5: `for i, (k, v) in enumerate(d.items()):`. Note the parentheses around `(k, v)` because `d.items()` yields tuples, and `enumerate` wraps them again.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You loop over two or more parallel lists
- You need a counter or line number while looping
- You build a dict from keys and values lists
- You need consecutive pairs: `zip(a, a[1:])`

❌ Avoid when:
- You need random access by index (use the list directly)
- You must reuse the pairs many times without making a list first
- The lists are huge and you only need one element (just index it)

---

## 📊 Visual Diagram
```
names:   Asha   Ravi   Meena
prices:  250    180    320
           |      |      |
zip ->  (Asha,250) (Ravi,180) (Meena,320)

enumerate(names, start=1):
        (1,Asha) (2,Ravi) (3,Meena)

zip(*[(1,'a'),(2,'b')])  ->  (1,2)   ('a','b')     # unzip
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| zip | Combine iterables position by position | Iterables को position के हिसाब से जोड़ना |
| enumerate | Add a counter to iteration | Iteration में counter जोड़ना |
| Unpacking | Split a tuple into variables | Tuple को variables में बाँटना |
| strict | Error if lengths differ | लंबाई अलग हो तो error |
| zip_longest | Pad to longest | सबसे लंबे तक भरना |
| Iterator | One-shot lazy sequence | एक बार चलने वाला lazy sequence |

---

## ⚡ 3-Line Summary
English: `zip` pairs items from several iterables and stops at the shortest; `enumerate` adds a counter. Both are lazy one-shot iterators. Use `strict=True` to catch uneven lengths and `start=1` for human numbering.
Hindi: `zip` कई iterables के items को जोड़ता है और सबसे छोटे पर रुकता है; `enumerate` counter जोड़ता है। दोनों lazy और एक बार चलने वाले iterators हैं। लंबाई की गलती पकड़ने के लिए `strict=True` और human numbering के लिए `start=1` use करें।

---

## ➡️ Next Topic
**121. sorted() + key parameter** — sort anything by any rule: key functions, `itemgetter`, multi-level sorting and stability.
