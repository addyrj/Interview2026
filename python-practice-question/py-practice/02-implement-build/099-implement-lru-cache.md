---

# Q099. Implement LRU Cache
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `LRUCache(capacity)` with `get(key)` and `put(key, value)`, both in O(1).
When the cache is full, `put` must evict the **least recently used** key. `get` on a missing key returns `-1`.

```python
cache = LRUCache(2)
cache.put(1, 1); cache.put(2, 2)
cache.get(1)      # 1
cache.put(3, 3)   # evicts key 2
cache.get(2)      # -1
```

---

## 💡 Quick Concept (2 lines only)
Keep keys ordered by recency: every `get`/`put` moves the key to the "newest" end, eviction pops the "oldest" end. `OrderedDict` gives O(1) `move_to_end` and `popitem`.
हिंदी: हर access पर key को सबसे नया बनाओ, और जगह भरने पर सबसे पुराना key हटा दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import OrderedDict  # dict that remembers order + has move_to_end

class LRUCache:  # LRU cache with fixed capacity
    def __init__(self, capacity: int) -> None:  # constructor
        self.capacity = capacity  # Step 1: max number of items allowed
        self.data: OrderedDict[int, int] = OrderedDict()  # order = oldest -> newest

    def get(self, key: int) -> int:  # read a value
        if key not in self.data:  # Step 2: missing key
            return -1  # sentinel for a cache miss
        self.data.move_to_end(key)  # mark as most recently used
        return self.data[key]  # return the stored value

    def put(self, key: int, value: int) -> None:  # write a value
        if key in self.data:  # Step 3: key already exists
            self.data.move_to_end(key)  # refresh its recency
        self.data[key] = value  # insert or update the value
        if len(self.data) > self.capacity:  # Step 4: over capacity?
            self.data.popitem(last=False)  # evict the least recently used (front)

# ============================================
# TEST CASES
# ============================================
cache = LRUCache(2)  # capacity 2
cache.put(1, 1)  # cache: {1}
cache.put(2, 2)  # cache: {1, 2}
print(cache.get(1))  # Expected: 1
cache.put(3, 3)  # evicts key 2 (1 was just used)
print(cache.get(2))  # Expected: -1
cache.put(4, 4)  # evicts key 1
print(cache.get(1))  # Expected: -1
print(cache.get(3))  # Expected: 3
print(cache.get(4))  # Expected: 4
print(list(cache.data))  # Expected: [3, 4]  (oldest -> newest)
```

---

## 🔍 Why This Works (3 lines max)
`OrderedDict` is a hash map plus a doubly linked list internally, so lookup, `move_to_end` and `popitem(last=False)` are all O(1). The front of the order is always the LRU key.
हिंदी: OrderedDict में hash map और linked list दोनों हैं, इसलिए सब कुछ O(1) में होता है।

---

## ⚡ Alternative Solution
```python
# Manual hash map + doubly linked list (what interviewers often ask you to build)
class Node:  # list node
    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key, self.val = key, val  # payload
        self.prev: "Node | None" = None  # left link
        self.next: "Node | None" = None  # right link

class LRUManual:
    def __init__(self, capacity: int) -> None:
        self.cap = capacity  # capacity
        self.map: dict[int, Node] = {}  # key -> node
        self.head, self.tail = Node(), Node()  # dummy sentinels (no edge cases)
        self.head.next, self.tail.prev = self.tail, self.head  # link them

    def _remove(self, n: Node) -> None:  # unlink a node
        n.prev.next, n.next.prev = n.next, n.prev  # bypass n

    def _add_front(self, n: Node) -> None:  # insert right after head (MRU)
        n.next, n.prev = self.head.next, self.head  # set n's links
        self.head.next.prev = n  # old first node points back to n
        self.head.next = n  # head points to n

    def get(self, key: int) -> int:
        if key not in self.map:  # miss
            return -1
        n = self.map[key]  # find node
        self._remove(n); self._add_front(n)  # move to front
        return n.val  # value

    def put(self, key: int, value: int) -> None:
        if key in self.map:  # update existing
            self._remove(self.map[key])  # unlink old node
        n = self.map[key] = Node(key, value)  # create + register
        self._add_front(n)  # becomes MRU
        if len(self.map) > self.cap:  # too many?
            lru = self.tail.prev  # least recent node
            self._remove(lru)  # unlink it
            del self.map[lru.key]  # forget it

m = LRUManual(2)  # capacity 2
m.put(1, 1); m.put(2, 2)  # fill
print(m.get(1))  # Expected: 1
m.put(3, 3)  # evicts 2
print(m.get(2))  # Expected: -1
print(m.get(3))  # Expected: 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: dict + list for order -> list.remove() is O(n), so get() is NOT O(1)
class SlowLRU:
    def __init__(self, c): self.c, self.d, self.order = c, {}, []
    def get(self, k):
        if k not in self.d: return -1
        self.order.remove(k)  # ❌ O(n) scan
        self.order.append(k)
        return self.d[k]

# ✅ Correct: OrderedDict.move_to_end (O(1)) or a hash map + doubly linked list
# Also (Python): functools.lru_cache is for FUNCTION results, not a get/put cache.
```

---

## 🎯 Interview Tip (1 line)
Say: "Hash map for O(1) lookup + doubly linked list for O(1) reorder/evict; in Python OrderedDict does both" — then offer to code the manual version.

---

## 🔗 Related Questions
→ Q083 (memoize) | Q100 (stack) | Q102 (linked list) | Q150 (complete LRU cache) | Q185 (cache with TTL)
