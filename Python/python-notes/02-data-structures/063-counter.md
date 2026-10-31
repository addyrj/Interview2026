---

# 063. Counter
# हिंदी में: Counter (गिनती करने वाला Dict)

---

## 🔵 Simple Definition (English)
`Counter` is a dict subclass from `collections` made for counting hashable items. Give it any iterable and it returns `{item: count}`. It adds helpers like `most_common(n)`, `elements()`, `update()`, `subtract()` and supports `+`, `-`, `&`, `|` between counters.

## 🔵 सरल परिभाषा (Hindi)
`Counter` `collections` का dict subclass है जो hashable items गिनने के लिए बना है। कोई भी iterable दो तो `{item: count}` मिलता है। इसमें `most_common(n)`, `elements()`, `update()`, `subtract()` जैसे helpers हैं और counters के बीच `+`, `-`, `&`, `|` चलते हैं।

---

## 🔴 Problem it Solves
Counting with a normal dict needs `if key in d: d[key] += 1 else: d[key] = 1`. Finding the top 10 needs sorting by hand. Comparing two word-frequency tables needs loops. Counter does counting, top-N and comparisons in one line, with clean and fast C-optimized counting.

## 🔴 यह क्यों बना? (Hindi)
Normal dict से गिनती में `if key in d` वाला code लगता है। Top 10 निकालने के लिए हाथ से sort करना पड़ता है। दो frequency tables compare करने के लिए loops। Counter गिनती, top-N और comparison एक line में करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Counter("banana")            → loops over items, adds 1 to each item's count
Step 2 → c["a"]                       → returns 3; for a missing key returns 0 (no KeyError)
Step 3 → c.most_common(2)             → list of the 2 highest (item, count) pairs
Step 4 → c.update("aab")              → ADDS to existing counts (dict.update would replace)
Step 5 → c1 + c2 / c1 - c2            → add / subtract counts; result keeps only positive counts
Step 6 → c1 & c2 / c1 | c2            → min of counts / max of counts
```

## 🟢 कैसे काम करता है? (Hindi)
```
Counter("banana") → हर item के लिए count +1
c["x"] (नहीं है) → 0 लौटाता है, KeyError नहीं
most_common(n) → सबसे ज़्यादा वाले n pairs
update() → counts जोड़ता है (replace नहीं)
c1 + c2 → counts जोड़ना; c1 - c2 → घटाना (सिर्फ positive रखता है)
```

---

## 🟡 Real World Example
Swiggy: find the top 5 most ordered dishes from millions of order lines: `Counter(dish for order in orders for dish in order.items).most_common(5)`. In an AI app: count word frequencies for a simple keyword search or token statistics for prompts. In FastAPI: count HTTP status codes from access logs for a metrics endpoint.

## 🟡 Real Example Hindi mein
Swiggy में लाखों order lines से top 5 dishes: `Counter(dish for order in orders for dish in order.items).most_common(5)`। AI app में keyword search के लिए word frequency। FastAPI में access logs से HTTP status codes गिनकर metrics endpoint।

---

## 💻 Code Example — Basic
```python
# Basic: counting with Counter
from collections import Counter              # import Counter

word: str = "banana"                         # sample string
c: Counter[str] = Counter(word)              # count each character
print(c)                                     # Output: Counter({'a': 3, 'n': 2, 'b': 1})
print(c["a"])                                # Output: 3
print(c["z"])                                # Output: 0  (missing key -> 0, no error)

print(c.most_common(2))                      # Output: [('a', 3), ('n', 2)]
print(list(c.elements()))                    # Output: ['b', 'a', 'a', 'a', 'n', 'n']

words: list[str] = "the cat and the dog and the bird".split()   # sample words
wc: Counter[str] = Counter(words)            # word frequency
print(wc.most_common(1))                     # Output: [('the', 3)]

wc.update(["cat", "cat"])                    # ADD more counts
print(wc["cat"])                             # Output: 3
wc.subtract(["the"])                         # reduce a count
print(wc["the"])                             # Output: 2

print(sum(wc.values()))                      # Output: 9 (total items counted)
print(wc.total())                            # Output: 9 (same, Python 3.10+)

c1 = Counter(a=3, b=1)                       # first counter
c2 = Counter(a=1, b=2)                       # second counter
print(c1 + c2)                               # Output: Counter({'a': 4, 'b': 3})
print(c1 - c2)                               # Output: Counter({'a': 2})  (negatives dropped)
print(c1 & c2)                               # Output: Counter({'a': 1, 'b': 1})  (min)
print(c1 | c2)                               # Output: Counter({'a': 3, 'b': 2})  (max)
```

## 💻 Code Example — Advanced
```python
# Advanced: log analysis, anagram check and top-N with ties
from __future__ import annotations           # modern hints
from collections import Counter              # counting tool
import re                                    # regex for tokenizing


def top_words(text: str, n: int = 3, stop: frozenset[str] = frozenset({"the", "a", "is"})) -> list[tuple[str, int]]:
    """Return the n most common words, ignoring stop words."""
    words: list[str] = re.findall(r"[a-z']+", text.lower())   # lowercase tokens
    counts: Counter[str] = Counter(w for w in words if w not in stop)   # skip stop words
    return counts.most_common(n)             # top n pairs


def is_anagram(a: str, b: str) -> bool:
    """True if both strings use the same letters (ignoring case/spaces)."""
    clean = lambda s: Counter(s.replace(" ", "").lower())   # letter counts
    return clean(a) == clean(b)              # Counters compare by content


def status_report(lines: list[str]) -> dict[str, int]:
    """Count HTTP status codes in 'METHOD PATH STATUS' log lines."""
    counter: Counter[str] = Counter()        # empty counter
    for line in lines:                       # walk log lines
        parts: list[str] = line.split()      # split by whitespace
        if len(parts) != 3:                  # skip malformed lines
            continue                         # ignore bad line
        counter[parts[2]] += 1               # count status code
    return dict(counter)                     # plain dict for JSON


text = "The cat is on the mat. The cat is happy, the mat is soft."
print(top_words(text))                       # Output: [('cat', 2), ('mat', 2), ('on', 1)]
print(is_anagram("Listen", "Silent"))        # Output: True
print(is_anagram("abc", "abd"))              # Output: False

logs: list[str] = ["GET /a 200", "GET /b 404", "POST /a 200", "bad line"]
print(status_report(logs))                   # Output: {'200': 2, '404': 1}

# Counter arithmetic for inventory: stock - sold
stock = Counter({"pen": 10, "book": 3})      # stock counts
sold = Counter({"pen": 4, "book": 5})        # sold counts
print(stock - sold)                          # Output: Counter({'pen': 6})  (book would be negative, dropped)
stock.subtract(sold)                         # subtract() KEEPS negatives
print(dict(stock))                           # Output: {'pen': 6, 'book': -2}
print(+stock)                                # Output: Counter({'pen': 6})  (unary + removes <= 0)

# Min-heap style: least common
print(Counter("aabbbc").most_common()[:-3:-1])   # Output: [('c', 1), ('a', 2)]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import Counter
c = Counter(["a", "b", "a"])
print(c.most_common(1))              # [('a', 2)]
```

```javascript
// JavaScript
const arr = ["a", "b", "a"];
const c = arr.reduce((acc, x) => {   // manual counting with reduce
  acc[x] = (acc[x] || 0) + 1;
  return acc;
}, {});
const top = Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 1); // manual top-N
// [["a", 2]]
```

Key difference: JS has no Counter; you write `reduce` + sort by hand. FastAPI link: Counter is handy in metrics or analytics endpoints (status code counts, top search terms) and returns a dict subclass that serializes to JSON directly.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `update()` to replace counts
```python
c = Counter(a=1)
c.update(a=5)         # c["a"] is now 6 (added), NOT 5
# Replace with: c["a"] = 5
```

❌ Mistake 2: Using `-` and expecting negatives
```python
# Counter(a=1) - Counter(a=3)  -> Counter()   (negatives dropped)
# Use .subtract() if you need negative counts
```

❌ Mistake 3: Counting unhashable items
```python
# Counter([[1], [1]])   # TypeError: unhashable type: 'list'
# Correct: Counter(tuple(x) for x in [[1], [1]])
```

---

## 🧠 Tricky Interview Question

**Q**: "`Counter('aabb').most_common()` returns `[('a', 2), ('b', 2)]`. How are ties ordered, and what is the time complexity of `most_common(k)`?"

**Answer**: For equal counts, items keep the order in which they were first inserted (Python 3.7+), because `most_common` uses a stable sort / `heapq.nlargest`. Complexity: `most_common()` with no argument sorts all `n` unique items: O(n log n). `most_common(k)` uses `heapq.nlargest`, which is about O(n log k), so asking for a small top-k is cheaper. Counting itself is O(N) for N items.

---

## ⚫ Interview Questions + Answers

Q1: What is Counter and what does it return for a missing key?
A1: Counter is a dict subclass for counting hashable objects. For a missing key, it returns `0` instead of raising `KeyError` (but it does not insert the key). It can be created from an iterable, a mapping or keyword arguments.

Q2: How do you find the k most frequent elements?
A2: `Counter(nums).most_common(k)` gives `(item, count)` pairs. For just the items: `[x for x, _ in Counter(nums).most_common(k)]`. This is a classic interview problem ("Top K Frequent Elements") solved in 2 lines in Python.

Q3: What is the difference between `update` in Counter and in dict?
A3: `dict.update` replaces values for existing keys. `Counter.update` ADDS the counts. `Counter.subtract` reduces counts and allows zero and negative results. Use `c[key] = n` to set an exact value.

Q4: What do `+`, `-`, `&`, `|` do on Counters?
A4: `+` adds counts; `-` subtracts and keeps only positive results; `&` keeps the minimum count of each item (intersection); `|` keeps the maximum (union). These operations drop zero and negative counts from the result.

Q5: Counter vs defaultdict(int)?
A5: Both count. Counter accepts an iterable in its constructor, has `most_common`, `elements`, `total` and arithmetic, and returns 0 for missing keys without inserting them. `defaultdict(int)` inserts the key on read and has no helpers, but is more general for custom aggregation. For pure counting use Counter.

---

## 🔷 When to Use Counter

✅ Use when:
- Counting items, words, characters or status codes
- Getting top-N frequent items
- Comparing multisets (anagrams, inventory)

❌ Avoid when:
- Items are unhashable (convert to tuples first)
- You need sums or averages instead of counts (use defaultdict)
- The data is huge and does not fit in memory (use a database or streaming sketch)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multiset | Collection that allows repeats with counts | Repeat के साथ counts वाला collection |
| `most_common` | Top items by count | सबसे ज़्यादा count वाले items |
| `elements()` | Expand counts back to items | Counts को वापस items में फैलाना |
| `subtract` | Reduce counts, keeps negatives | Counts घटाना, negative भी रहते हैं |
| Frequency | How many times something appears | कितनी बार आया |
| Hashable | Can be used as a key | Key बन सकने वाला |

---

## ⚡ 3-Line Summary
English: Counter counts hashable items and returns 0 for missing keys. Use `most_common(k)` for top-k, `update` to add counts, and `+ - & |` to combine counters. Operators drop non-positive counts; `subtract` keeps them.
Hindi: Counter hashable items गिनता है और missing key पर 0 देता है। Top-k के लिए `most_common(k)`, counts जोड़ने के लिए `update`, और counters मिलाने के लिए `+ - & |`। Operators non-positive counts हटाते हैं; `subtract` रखता है।

---

## ➡️ Next Topic
**064. ChainMap** — combine several dicts into one layered view without copying, config and scope lookups.
