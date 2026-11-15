---

# Q150. Complete LRU Cache
# Category: Complete The Code
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Complete the LRU (Least Recently Used) cache with O(1) `get` and `put`. When full, evict the least recently used key.

```python
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.data: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.data:
            return -1
        self.data.____(key)                        # BLANK 1: mark as most recently used
        return self.data[key]

    def put(self, key: int, value: int) -> None:
        if key in self.data:
            self.data.move_to_end(key)             # refresh
        self.data[key] = value
        if len(self.data) ____ self.capacity:      # BLANK 2: over capacity?
            self.data.____(last=____)              # BLANK 3, 4: pop the OLDEST item
```

---

## 💡 Quick Concept (2 lines only)
`OrderedDict` remembers insertion order and can move a key to the end in O(1): the end = most recent, the front = next to evict.
हिंदी: `OrderedDict` में end = सबसे हाल का, front = सबसे पुराना; पुराना हटाकर जगह बनाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import OrderedDict                # dict that supports reordering


class LRUCache:
    def __init__(self, capacity: int) -> None:     # Step 1: set the size limit
        self.capacity = capacity                   # max number of entries
        self.data: OrderedDict[int, int] = OrderedDict()  # oldest first, newest last

    def get(self, key: int) -> int:                # Step 2: read
        if key not in self.data:                   # miss
            return -1                              # conventional "not found"
        self.data.move_to_end(key)                 # BLANK 1: now the most recently used
        return self.data[key]                      # return the value

    def put(self, key: int, value: int) -> None:   # Step 3: write
        if key in self.data:                       # existing key
            self.data.move_to_end(key)             # refresh its position
        self.data[key] = value                     # insert or update
        if len(self.data) > self.capacity:         # BLANK 2: too many entries?
            self.data.popitem(last=False)          # BLANK 3/4: evict the oldest (front)


# ============================================
# TEST CASES
# ============================================
c = LRUCache(2)                                    # capacity 2
c.put(1, 1)                                        # {1}
c.put(2, 2)                                        # {1, 2}
print(c.get(1))                                    # Expected: 1   (order now 2, 1)
c.put(3, 3)                                        # evicts key 2
print(c.get(2))                                    # Expected: -1
c.put(4, 4)                                        # evicts key 1
print(c.get(1), c.get(3), c.get(4))                # Expected: -1 3 4
print(list(c.data))                                # Expected: [3, 4]
```

---

## 🔍 Why This Works (3 lines max)
Every access moves the key to the end, so the first key is always the least recently used. `popitem(last=False)` removes it in O(1). All operations are O(1) average.
हिंदी: हर access key को end में ले जाता है, इसलिए front हमेशा सबसे पुराना होता है — `popitem(last=False)` उसे हटाता है।

---

## ⚡ Alternative Solution
```python
# Plain dict (insertion-ordered since 3.7): pop and re-insert to refresh
class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity                   # size limit
        self.data: dict[int, int] = {}             # oldest first

    def get(self, key: int) -> int:
        if key not in self.data:
            return -1
        self.data[key] = self.data.pop(key)        # remove + reinsert = move to end
        return self.data[key]

    def put(self, key: int, value: int) -> None:
        self.data.pop(key, None)                   # drop old position if any
        self.data[key] = value                     # insert at the end
        if len(self.data) > self.capacity:
            del self.data[next(iter(self.data))]   # delete the first (oldest) key

c = LRUCache(2)
c.put(1, 1); c.put(2, 2); c.get(1); c.put(3, 3)
print(list(c.data))                                # Expected: [1, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: popitem() with no argument -> pops the NEWEST item (LIFO), evicting the wrong one
# ❌ Wrong: not refreshing the order in get() -> that is FIFO, not LRU
# ❌ Wrong: using a list for order -> remove()/pop(0) are O(n)
# ✅ Correct: move_to_end on every access, popitem(last=False) for eviction
```

---

## 🎯 Interview Tip (1 line)
Say: "Classic answer is hash map + doubly linked list; in Python `OrderedDict` gives the same O(1) — and `functools.lru_cache` is the production choice."

---

## 🔗 Related Questions
→ Q099 (implement LRU) | Q143 (complete memoize) | Q185 (cache with TTL) | Q278 (lru_cache) | Q252 (collections)
