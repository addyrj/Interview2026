---

# 474. Implement LRU Cache
# हिंदी में: LRU Cache बनाना (Least Recently Used)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
An LRU cache stores a limited number of items. When it is full and a new item arrives, it throws away the item that was used the longest time ago. `get` and `put` must both be O(1).

## 🔵 सरल परिभाषा (Hindi)
LRU cache सीमित संख्या में items रखता है। भर जाने पर जब नया item आता है, तो वह उस item को हटाता है जिसे सबसे लंबे समय से इस्तेमाल नहीं किया गया। `get` और `put` दोनों O(1) होने चाहिए।

---

## 🔴 Problem it Solves
Reading from a database or calling an external API is slow. Caching helps, but memory is limited, so you must decide what to evict. LRU assumes "recently used will be used again" (temporal locality). The interview challenge: a dict gives O(1) lookup but no order; a list gives order but O(n) moves. You need both together.

## 🔴 यह क्यों बना? (Hindi)
Database पढ़ना या external API बुलाना धीमा है। Cache मदद करता है, पर memory सीमित है, इसलिए तय करना पड़ता है कि क्या हटाएँ। LRU मानता है कि "हाल में इस्तेमाल हुआ item फिर से इस्तेमाल होगा"। Interview की चुनौती: dict O(1) lookup देता है पर order नहीं; list order देती है पर move O(n) है। दोनों साथ चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a dict: key -> node (O(1) lookup)
Step 2 → Keep a doubly linked list ordered by recency (front = most recent)
Step 3 → get(k): if missing return -1; else move the node to the front
Step 4 → put(k, v): if exists, update and move to front; else insert at front
Step 5 → If size > capacity: remove the node at the back (least recent)
         and delete its key from the dict
Step 6 → Shortcut in Python: OrderedDict.move_to_end + popitem(last=False)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक dict रखो: key -> node (O(1) lookup)
Step 2 → Recency के क्रम में doubly linked list रखो (आगे = सबसे हाल का)
Step 3 → get(k): न मिले तो -1; मिले तो node को आगे ले आओ
Step 4 → put(k, v): मौजूद हो तो update करके आगे लाओ; वरना आगे insert करो
Step 5 → अगर size > capacity: पीछे वाला node हटाओ और dict से उसकी key भी हटाओ
Step 6 → Python shortcut: OrderedDict.move_to_end + popitem(last=False)
```

---

## 🟡 Real World Example
A product-detail API for Flipkart caches the 1000 most recently viewed products in memory so repeated views skip the database. An LLM app caches embeddings of recent prompts. Redis itself offers `maxmemory-policy allkeys-lru`. Python's `functools.lru_cache` is the same idea for function results.

## 🟡 Real Example Hindi mein
Flipkart का product-detail API सबसे हाल में देखे गए 1000 products को memory में cache करता है ताकि बार-बार देखने पर database न जाना पड़े। LLM app हाल के prompts के embeddings cache करता है। Redis में `maxmemory-policy allkeys-lru` मिलता है। Python का `functools.lru_cache` function results के लिए यही विचार है।

---

## 💻 Code Example — Basic
```python
# Basic LRU with OrderedDict
from collections import OrderedDict           # dict that remembers order

cache: OrderedDict[str, int] = OrderedDict()  # most recent at the end
CAP: int = 2                                   # capacity

def put(key: str, value: int) -> None:
    if key in cache:                           # existing key?
        cache.move_to_end(key)                 # mark as most recent
    cache[key] = value                         # insert or update
    if len(cache) > CAP:                       # over capacity?
        cache.popitem(last=False)              # drop the oldest (front)

put("a", 1)                                    # cache: a
put("b", 2)                                    # cache: a, b
cache.move_to_end("a")                         # we "read" a -> now b is the oldest
put("c", 3)                                    # evicts b
print(list(cache))                             # remaining keys

# Output:
# ['a', 'c']
```

## 💻 Code Example — Advanced
```python
# Production style: dict + doubly linked list with sentinels (tests in main.py)
from typing import Optional


class _Node:
    __slots__ = ("key", "val", "prev", "next")   # smaller memory per node

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key, self.val = key, val            # payload
        self.prev: Optional[_Node] = None        # towards most recent
        self.next: Optional[_Node] = None        # towards least recent


class LRU:
    def __init__(self, capacity: int) -> None:
        self._cap = capacity                     # max items
        self._map: dict[int, _Node] = {}         # key -> node
        self._head, self._tail = _Node(), _Node()   # sentinels: no None checks needed
        self._head.next, self._tail.prev = self._tail, self._head   # empty list

    def _remove(self, n: _Node) -> None:
        n.prev.next, n.next.prev = n.next, n.prev   # type: ignore[union-attr]  # unlink

    def _add_front(self, n: _Node) -> None:
        n.next, n.prev = self._head.next, self._head   # place after head
        self._head.next.prev = n                 # type: ignore[union-attr]
        self._head.next = n                      # now most recent

    def get(self, key: int) -> int:
        n = self._map.get(key)                   # O(1) lookup
        if n is None:
            return -1                            # miss
        self._remove(n); self._add_front(n)      # refresh recency
        return n.val

    def put(self, key: int, val: int) -> None:
        if key in self._map:
            self._remove(self._map[key])         # drop old position
        n = self._map[key] = _Node(key, val)     # new/updated node
        self._add_front(n)                       # most recent
        if len(self._map) > self._cap:           # evict?
            lru = self._tail.prev                # least recent node
            self._remove(lru)                    # type: ignore[arg-type]
            del self._map[lru.key]               # type: ignore[union-attr]


c = LRU(2)
c.put(1, 1); c.put(2, 2)                         # cache: 2, 1
print(c.get(1))                                  # hit, 1 is now most recent
c.put(3, 3)                                      # evicts key 2
print(c.get(2), c.get(3))                        # miss, hit
c.put(4, 4)                                      # evicts key 1
print(c.get(1), c.get(3), c.get(4))              # miss, hit, hit

# Output:
# 1
# -1 3
# -1 3 4
```

---

## 🟠 JavaScript vs Python Comparison
JS `Map` keeps insertion order too, so the same trick works: delete and re-set the key to move it to the end; the first key is the oldest.

```python
# Python way
from collections import OrderedDict
d: OrderedDict[str, int] = OrderedDict()
d["a"] = 1
d.move_to_end("a")            # mark recent
d.popitem(last=False)         # evict oldest
```
```javascript
// JavaScript way
const m = new Map();
m.set("a", 1);
const v = m.get("a"); m.delete("a"); m.set("a", v);   // move to end
const oldest = m.keys().next().value;                 // first key = oldest
m.delete(oldest);                                     // evict
```

---

## 🟠 FastAPI Connection
Use `functools.lru_cache` for pure functions (settings, compiled regex) and a TTL cache or Redis for request data. Do not use `lru_cache` directly on `async def`: it would cache the coroutine object, not the result.

```python
from functools import lru_cache
from fastapi import FastAPI

app = FastAPI()

@lru_cache(maxsize=256)                          # sync pure function: safe to cache
def shipping_fee(pincode: str) -> int:
    return 40 if pincode.startswith("11") else 70   # imagine a slow lookup

@app.get("/fee/{pincode}")
def fee(pincode: str) -> dict[str, int]:
    return {"fee": shipping_fee(pincode)}        # repeated pincodes hit the cache
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: a plain dict with `min()` over timestamps to find the oldest (O(n) per eviction).
✅ Correct: OrderedDict or dict + doubly linked list.

❌ Mistake 2: not refreshing recency on `get` (then it is FIFO, not LRU).
✅ Correct: every hit moves the entry to the most-recent end.

```python
# Wrong
def get(k): return data.get(k)
# Right
def get(k):
    if k in data: data.move_to_end(k)
    return data.get(k)
```

❌ Mistake 3: sharing the cache across threads without a lock (races corrupt the order). Also `@lru_cache` on a method keeps `self` alive (memory leak).
✅ Correct: guard with `threading.Lock`, or cache module-level functions.

---

## 🧠 Tricky Interview Question
```python
from functools import lru_cache

@lru_cache(maxsize=2)
def f(x: int) -> int:
    print("compute", x)
    return x * 2

f(1); f(2); f(1); f(3); f(2)
print(f.cache_info().hits, f.cache_info().misses)
```
Answer: Prints `compute 1`, `compute 2`, `compute 3`, `compute 2`, then `1 4`. f(1) miss, f(2) miss, f(1) hit (1 becomes recent), f(3) miss and evicts 2, f(2) miss again. Hits 1, misses 4.

---

## ⚫ Interview Questions + Answers

Q1: Why a doubly (not singly) linked list?
A1: To unlink a node in O(1) you need its `prev`. With a singly list you would have to search for it: O(n).

Q2: Why sentinel head and tail nodes?
A2: They remove special cases for empty list/first/last node, so `_remove` and `_add_front` have no `None` checks.

Q3: What is the time and space complexity?
A3: `get` and `put` are O(1); space is O(capacity).

Q4: LRU vs LFU vs FIFO?
A4: FIFO evicts oldest inserted; LRU evicts least recently used; LFU evicts least frequently used (needs counters, better for stable hot sets, worse at adapting).

Q5: How do you make it thread-safe and add expiry?
A5: Wrap `get/put` in a `threading.Lock` (or use asyncio single-thread). For TTL store an expiry timestamp per key and check it lazily on `get` (see `TTLCache` in main.py), using `time.monotonic()`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reads repeat and recomputing/fetching is expensive
- Memory is bounded and access has temporal locality
- You cache pure function results (`lru_cache`)

❌ Avoid when:
- Data changes often and stale values are dangerous (add TTL/invalidations or skip)
- Access is a one-time scan (it will pollute and evict useful entries)
- Multiple processes need to share it (use Redis)

---

## 📊 Visual Diagram
```
 dict:  1 -> N1, 2 -> N2, 3 -> N3          (O(1) lookup)

 HEAD <-> [3] <-> [1] <-> [2] <-> TAIL
          most                 least
          recent               recent

 get(2):  HEAD <-> [2] <-> [3] <-> [1] <-> TAIL
 put(4):  HEAD <-> [4] <-> [2] <-> [3] <-> TAIL   ([1] evicted, cap = 3)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Fast temporary storage | तेज़ अस्थायी भंडार |
| Eviction | Removing an item to make room | जगह बनाने के लिए हटाना |
| LRU | Evict least recently used | सबसे कम हाल में इस्तेमाल हुआ हटाओ |
| Hit / Miss | Found / not found in cache | मिला / नहीं मिला |
| TTL | Time to live before expiry | समाप्ति का समय |
| Sentinel | Dummy head/tail node | सहायक सिरा-node |

---

## ⚡ 3-Line Summary
English: LRU evicts the entry unused for the longest time when the cache is full.
English: A dict plus a doubly linked list gives O(1) get and put; OrderedDict does it for you.
English: Refresh recency on every hit, add a lock for threads and a TTL for freshness.

Hindi: LRU भरे cache में वह entry हटाता है जो सबसे लंबे समय से इस्तेमाल नहीं हुई।
Hindi: Dict + doubly linked list से get और put O(1) होते हैं; OrderedDict यही कर देता है।
Hindi: हर hit पर recency अपडेट करो, threads के लिए lock और ताज़गी के लिए TTL जोड़ो।

---

## ➡️ Next Topic
**475. Implement Trie** — another structure built from linked nodes, used for autocomplete and prefix search.

---
