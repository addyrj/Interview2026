---

# 080. Choosing Right Data Structure
# हिंदी में: सही Data Structure कैसे चुनें

---

## 🔵 Simple Definition (English)
Choosing the right data structure means picking the container (list, tuple, set, dict, deque, heap, array...) whose operations are fast for what your program does most. The same task can take 1 millisecond or 10 minutes depending on this one choice.

## 🔵 सरल परिभाषा (Hindi)
सही data structure चुनने का मतलब है ऐसा container (list, tuple, set, dict, deque, heap, array...) चुनना जिसके operations आपके program के सबसे ज्यादा होने वाले काम के लिए तेज हों। यही एक choice तय करती है कि काम 1 millisecond में होगा या 10 minute में।

---

## 🔴 Problem it Solves
Beginners use `list` for everything. A list is great for ordered data, but checking `x in my_list` scans every item (O(n)), removing from the front shifts everything (O(n)), and finding the smallest repeatedly is O(n) each time. With 1 million users, these costs explode. Interviewers test exactly this: "what is the complexity, and is there a better structure?"

## 🔴 यह क्यों बना? (Hindi)
Beginners हर चीज़ के लिए `list` लेते हैं। List ordered data के लिए अच्छी है, लेकिन `x in my_list` हर item देखता है (O(n)), आगे से remove करने पर सब खिसकता है (O(n)), और बार-बार सबसे छोटा ढूँढना हर बार O(n) है। 10 लाख users पर यह costs बहुत बढ़ जाती हैं। Interviewer यही पूछते हैं: "complexity क्या है, और क्या इससे बेहतर structure है?"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: what operation will I do MOST? (lookup, add, remove, order, min)
Step 2 → Ask: do I need order? duplicates? changes (mutable)?
Step 3 → Ask: lookup by key or by position?
Step 4 → Pick the structure that makes that operation O(1) or O(log n)
Step 5 → Check memory: millions of numbers? maybe array / NumPy
Step 6 → Measure with timeit if unsure, then decide

Need                            -> Use
ordered, changeable, any type   -> list
fixed record, hashable key      -> tuple
unique items, fast "in"         -> set
key -> value lookup             -> dict
queue (add/remove both ends)    -> collections.deque
smallest / priority first       -> heapq
sorted + binary search          -> list + bisect
compact numbers                 -> array / NumPy
count things                    -> collections.Counter
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछो: मैं सबसे ज्यादा कौन सा operation करूँगा? (lookup, add, remove, order, min)
Step 2 → पूछो: order चाहिए? duplicates? बदलाव (mutable)?
Step 3 → Lookup key से होगा या position से?
Step 4 → वो structure चुनो जिसमें वो operation O(1) या O(log n) हो
Step 5 → Memory देखो: लाखों numbers हैं? तो array / NumPy
Step 6 → शक हो तो timeit से नापो, फिर तय करो
```

---

## 🟡 Real World Example
Zomato-style restaurant search: user IDs already seen today -> `set` (is this a duplicate click?). Restaurant by ID -> `dict`. Orders waiting for a delivery partner -> `deque` (first in, first out). Show the 10 closest restaurants -> `heapq.nsmallest`. A fixed (lat, lng) location -> `tuple`. Rating slabs -> `bisect`. Word frequency in reviews -> `Counter`.

## 🟡 Real Example Hindi mein
Zomato जैसा restaurant search: आज देखे हुए user IDs -> `set` (क्या यह duplicate click है?)। ID से restaurant -> `dict`। Delivery partner का इंतज़ार करते orders -> `deque` (पहले आया, पहले गया)। सबसे नजदीकी 10 restaurants -> `heapq.nsmallest`। Fixed (lat, lng) location -> `tuple`। Rating slabs -> `bisect`। Reviews में words की गिनती -> `Counter`।

---

## 💻 Code Example — Basic
```python
# Basic: see why the choice matters
from collections import deque                      # double-ended queue
import timeit                                      # simple timing tool

big_list: list[int] = list(range(100000))          # 100k numbers in a list
big_set: set[int] = set(big_list)                  # same numbers in a set
print(99999 in big_list, 99999 in big_set)         # both True, very different speed
t_list: float = timeit.timeit(lambda: 99999 in big_list, number=200)   # scans the list
t_set: float = timeit.timeit(lambda: 99999 in big_set, number=200)     # hash lookup
print(t_list > t_set)                              # set is much faster -> True

q: deque[int] = deque([1, 2, 3])                   # queue
q.appendleft(0)                                    # O(1) add at the front
first: int = q.popleft()                           # O(1) remove from the front
print(first, q)                                    # 0 deque([1, 2, 3])

point: tuple[int, int] = (3, 4)                    # tuple is hashable
d: dict[tuple[int, int], str] = {point: "A"}       # tuple can be a dict key
print(d[(3, 4)])                                   # A  (a list could not be a key)
print(list(dict.fromkeys([3, 1, 3, 2, 1])))        # unique + keeps order -> [3, 1, 2]

# Output:
# True True
# True
# 0 deque([1, 2, 3])
# A
# [3, 1, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: the right structure for each job
from collections import Counter, defaultdict, deque   # specialised containers
from typing import Hashable                            # type for dict/set keys
import heapq                                           # heap functions


def dedupe_keep_order(items: list[Hashable]) -> list[Hashable]:
    """Remove duplicates but keep first-seen order (dict keeps order)."""
    return list(dict.fromkeys(items))                  # O(n), set() would lose order


def group_by_city(users: list[dict[str, str]]) -> dict[str, list[str]]:
    """Group user names by city."""
    groups: defaultdict[str, list[str]] = defaultdict(list)   # missing key -> []
    for u in users:                                    # one pass
        groups[u["city"]].append(u["name"])            # no "if key in" check needed
    return dict(groups)                                # plain dict for output


def recent_n(events: list[str], n: int) -> list[str]:
    """Keep only the last n events (sliding window)."""
    window: deque[str] = deque(maxlen=n)               # old items drop automatically
    for e in events:                                   # stream of events
        window.append(e)                               # O(1)
    return list(window)                                # newest n items


def top_words(text: str, k: int) -> list[tuple[str, int]]:
    """Most common k words."""
    return Counter(text.split()).most_common(k)        # counting is built in


def smallest_k(nums: list[int], k: int) -> list[int]:
    """k smallest numbers without sorting everything."""
    return heapq.nsmallest(k, nums)                    # O(n log k)


print(dedupe_keep_order([3, 1, 3, 2, 1]))              # [3, 1, 2]
print(group_by_city([{"name": "A", "city": "Pune"},
                     {"name": "B", "city": "Delhi"},
                     {"name": "C", "city": "Pune"}]))  # grouped by city
print(recent_n(["e1", "e2", "e3", "e4"], 2))           # ['e3', 'e4']
print(top_words("a b a c b a", 2))                     # [('a', 3), ('b', 2)]
print(smallest_k([9, 2, 7, 1], 2))                     # [1, 2]

# Output:
# [3, 1, 2]
# {'Pune': ['A', 'C'], 'Delhi': ['B']}
# ['e3', 'e4']
# [('a', 3), ('b', 2)]
# [1, 2]
```

---

## 🟠 JavaScript vs Python Comparison

| Need | Python | JavaScript |
|------|--------|-----------|
| Ordered list | `list` | `Array` |
| Unique values | `set` | `Set` |
| Key -> value | `dict` | `Map` / plain object |
| Immutable record | `tuple` | `Object.freeze([...])` |
| Fast queue | `deque` | `Array.shift()` is O(n) |
| Priority queue | `heapq` | none built in |
| Counter | `Counter` | manual object |
| Typed numbers | `array` | `Int32Array` |

```python
# Python way — dict with tuple key, set for unique
seen: set[str] = set()                         # unique ids
grid: dict[tuple[int, int], str] = {(0, 0): "start"}   # tuple keys work
seen.add("u1")                                 # add id
print("u1" in seen, grid[(0, 0)])              # True start
```
```javascript
// JavaScript way — object keys become strings, Map needs same reference
const seen = new Set();                        // unique ids
const grid = new Map([["0,0", "start"]]);      // must build a string key like "0,0"
seen.add("u1");                                // add id
console.log(seen.has("u1"), grid.get("0,0"));  // true start
```

Key difference: Python dict and set accept any hashable value, including tuples, as keys. JS `Map` compares object keys by reference, so `[0,0]` is not found with a new `[0,0]`; developers turn keys into strings.

---

## 🟠 FastAPI Connection
In a real FastAPI service this choice shows up everywhere: a `dict` as an in-memory cache keyed by id, a `set` of revoked JWT tokens (O(1) check on every request), a `deque(maxlen=100)` for recent logs, a `Counter` for request counts per route. A `list` check like `if token in revoked_list` on each request is a hidden slowdown.

```python
# FastAPI example — right structure for each job
from collections import Counter, deque            # counter and bounded queue
from fastapi import FastAPI, HTTPException        # app + error

app: FastAPI = FastAPI()                          # create app
REVOKED: set[str] = {"tok_bad1", "tok_bad2"}      # set: O(1) membership check
USERS: dict[int, str] = {1: "Priya", 2: "Ravi"}   # dict: O(1) lookup by id
RECENT: deque[str] = deque(maxlen=3)              # keeps only last 3 paths
HITS: Counter[str] = Counter()                    # counts hits per path


@app.get("/users/{user_id}")                      # GET /users/1?token=abc
def get_user(user_id: int, token: str = "") -> dict[str, str]:
    if token in REVOKED:                          # fast set lookup
        raise HTTPException(status_code=401, detail="Token revoked")   # block
    if user_id not in USERS:                      # fast dict lookup
        raise HTTPException(status_code=404, detail="User not found")  # not found
    RECENT.append(f"/users/{user_id}")            # bounded history
    HITS["/users"] += 1                           # count the request
    return {"name": USERS[user_id]}               # response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a list for membership checks in a loop
✅ Correct: convert to a set once

```python
allowed = ["a", "b", "c"]
# Wrong — each "in" scans the list: O(n * m)
hits = [x for x in ["a", "z"] if x in allowed]
# Right — set lookup is O(1)
allowed_set = set(allowed)
hits = [x for x in ["a", "z"] if x in allowed_set]
```

❌ Mistake 2: Using `list.pop(0)` as a queue
✅ Correct: use `deque.popleft()`

```python
from collections import deque
# Wrong — pop(0) shifts every remaining item: O(n)
q_list = [1, 2, 3]
q_list.pop(0)
# Right — O(1)
q = deque([1, 2, 3])
q.popleft()
```

❌ Mistake 3: Using a set and expecting order or duplicates
✅ Correct: use `list` for order/duplicates, or `dict.fromkeys` for ordered unique

```python
# Wrong assumption: a set keeps order and counts
s = {3, 1, 3, 2}
print(s)                       # {1, 2, 3} — duplicates gone, order not promised
# Right — ordered unique
print(list(dict.fromkeys([3, 1, 3, 2])))   # [3, 1, 2]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
d = {}
d[1] = "int"
d[1.0] = "float"
d[True] = "bool"
print(d, len(d))
s = {[1, 2]}
```
Answer: `{1: 'bool'} 1` — `1`, `1.0` and `True` are equal and have the same hash, so they are the SAME key; the key stays `1` (first inserted) while the value is overwritten by the last assignment. The last line raises `TypeError: unhashable type: 'list'` because lists are mutable and cannot be set members or dict keys; use a tuple `(1, 2)` instead.

---

## ⚫ Interview Questions + Answers

Q1: Give the time complexity of `in` for list, set, dict, deque.
A1: list O(n), deque O(n), set O(1) average, dict O(1) average (on keys). Hash-based structures need hashable items, and worst case O(n) happens only with many hash collisions.

Q2: When do you use a tuple instead of a list?
A2: When the data is a fixed record that must not change (coordinates, a DB row, function return of several values), or when you need a hashable value (dict key, set member). Tuples are also slightly smaller and faster to create. Lists are for collections that grow and change.

Q3: Which structure for a queue and which for a stack?
A3: Queue (FIFO): `collections.deque` with `append` and `popleft`, both O(1). Stack (LIFO): a plain `list` with `append` and `pop` is fine (O(1) at the end). Never use `list.pop(0)` for queues. For threads use `queue.Queue`.

Q4: How do you get the top 3 highest salaries from 1 million records?
A4: `heapq.nlargest(3, salaries)` — O(n log 3) and tiny memory. Sorting everything is O(n log n) and wastes memory. For the single largest use `max()`.

Q5: A list vs array vs NumPy array for 10 million floats?
A5: A list stores 10 million pointers and float objects (hundreds of MB). `array("d")` stores 80 MB of raw doubles. NumPy also stores 80 MB and adds fast vector math. For analysis or ML use NumPy; for simple compact storage use `array`.

---

## 🔷 When to Use + When Not to Use
✅ Use when (quick table):
- `list` — ordered, changeable, needs indexing or sorting
- `tuple` — fixed record, dict key, returning several values
- `set` — uniqueness, fast membership, set math (union, intersection)
- `dict` — lookup by key, caching, grouping, counting
- `deque` — queues, sliding windows
- `heapq` — priority, top-K, scheduling
- `bisect` — sorted data, slabs, range counts

❌ Avoid when:
- `list` for membership tests on large data -> `set`
- `list.pop(0)` / `insert(0, x)` repeatedly -> `deque`
- `set` when order or duplicates matter -> `list` / `dict.fromkeys`
- Premature tuning on small data — clarity beats speed under ~1000 items

---

## 📊 Visual Diagram
```
                 What do you need?
                        |
     +------------------+----------------------+
     |                  |                      |
 lookup by key     unique / "in"           order matters
     |                  |                      |
   dict                set              +------+-------+
                                        |              |
                                   changes?        fixed?
                                        |              |
                            +-----------+---+        tuple
                         at ends?        anywhere
                            |               |
                          deque           list
 smallest first? -> heapq     sorted + search? -> list + bisect
 millions of numbers? -> array / NumPy      counting? -> Counter
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Time complexity | How cost grows with data size | Data बढ़ने पर समय कैसे बढ़ता है |
| O(1) | Constant time, size does not matter | हमेशा बराबर समय |
| O(n) | Time grows with size | Size के साथ बढ़ने वाला समय |
| Hashable | Has a fixed hash, can be a key | Dict key बन सकने वाला |
| FIFO / LIFO | First-in-first-out / Last-in-first-out | पहले आया पहले गया / आखिरी आया पहले गया |
| Trade-off | Gaining one thing, losing another | एक चीज़ पाना, दूसरी खोना |

---

## ⚡ 3-Line Summary
English: Pick the structure by the operation you do most: `set` and `dict` for fast lookup, `deque` for queues, `heapq` for priority, `tuple` for fixed records, `list` for ordered changeable data. The wrong choice turns O(1) into O(n) and slows big systems. When unsure, measure with `timeit`.
Hindi: सबसे ज्यादा होने वाले operation के हिसाब से structure चुनें: तेज lookup के लिए `set` और `dict`, queue के लिए `deque`, priority के लिए `heapq`, fixed record के लिए `tuple`, ordered बदलने वाले data के लिए `list`। गलत choice O(1) को O(n) बना देती है। शक हो तो `timeit` से नापें।

---

## ➡️ Next Topic
**081. OOP Complete** — now that you know Python's built-in data structures, we move to classes and objects to build your own data types.
