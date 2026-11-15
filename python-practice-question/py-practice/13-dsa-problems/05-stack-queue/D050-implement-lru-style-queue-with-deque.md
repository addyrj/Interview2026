---

# D050. Implement LRU-style Queue with deque
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium

---

## ❓ Problem
Build a fixed-capacity "recently used" queue. `access(x)` marks `x` as most recently used (adding it if new). When capacity is exceeded, the least recently used item is evicted and returned. Implement it with `collections.deque`, then improve it to O(1).

```
cap = 3
access(1), access(2), access(3)   -> order [1, 2, 3]
access(1)                          -> order [2, 3, 1]
access(4)                          -> evicts 2, order [3, 1, 4]
```

---

## 💡 Quick Concept (2 lines only)
A deque keeps order (left = least recent, right = most recent). Re-accessing means remove from the middle and append at the right; overflow means `popleft()`. `deque.remove` is O(n), `OrderedDict` makes it O(1).
हिंदी: Deque में बाईं तरफ सबसे पुराना और दाईं तरफ सबसे नया; दोबारा access पर बीच से हटाकर दाईं तरफ जोड़ो, भर जाए तो बाईं तरफ से निकालो।

---

## ✅ Solution

```python
from collections import deque, OrderedDict      # deque for brute, OrderedDict for O(1)
from typing import Optional                     # evicted item may be None


# ============================================
# APPROACH 1: deque + remove — O(n) access, simple
# ============================================
class LRUQueue:
    def __init__(self, capacity: int) -> None:
        self.cap = capacity                     # max items kept
        self.q: deque[int] = deque()            # left = LRU, right = MRU

    def access(self, x: int) -> Optional[int]:
        if x in self.q:                         # O(n) membership test
            self.q.remove(x)                    # O(n) remove from the middle
        self.q.append(x)                        # x becomes most recent
        if len(self.q) > self.cap:              # over capacity
            return self.q.popleft()             # evict least recent, O(1)
        return None                             # nothing evicted

    def order(self) -> list[int]:
        return list(self.q)                     # LRU -> MRU snapshot


# ============================================
# APPROACH 2: OrderedDict — O(1) access ✅ PREFERRED
# ============================================
class LRUQueueFast:
    def __init__(self, capacity: int) -> None:
        self.cap = capacity                     # max items kept
        self.d: OrderedDict[int, None] = OrderedDict()  # keys keep order, values unused

    def access(self, x: int) -> Optional[int]:
        if x in self.d:                         # O(1) membership
            self.d.move_to_end(x)               # O(1) mark most recent
        else:
            self.d[x] = None                    # insert new at the end
        if len(self.d) > self.cap:              # over capacity
            old, _ = self.d.popitem(last=False)  # O(1) pop least recent
            return old                          # report the evicted item
        return None                             # nothing evicted

    def order(self) -> list[int]:
        return list(self.d)                     # LRU -> MRU snapshot


# ============================================
# TEST CASES
# ============================================
for cls in (LRUQueue, LRUQueueFast):            # same test for both
    q = cls(3)                                  # capacity 3
    for x in (1, 2, 3):                         # fill up
        q.access(x)                             # no evictions
    print(q.order())                            # [1, 2, 3]
    q.access(1)                                 # refresh 1
    print(q.order())                            # [2, 3, 1]
    print(q.access(4), q.order())               # 2 [3, 1, 4]
    print(q.access(3), q.order())               # None [1, 4, 3]
```

---

## 🔍 Why It Works
```
cap=3   [1,2,3]  --access 1--> remove 1, append 1 -> [2,3,1]
        --access 4--> append -> [2,3,1,4] len 4 > 3 -> popleft -> evict 2 -> [3,1,4]
```
हिंदी: दाईं तरफ हमेशा सबसे हाल में इस्तेमाल हुआ item रहता है, इसलिए बाईं तरफ का item ही evict होता है।

---

## 📊 Complexity
```
deque + remove: access O(n), evict O(1) | Space O(capacity)
OrderedDict:    access O(1), evict O(1) | Space O(capacity) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Full LRU Cache with get/put values (Q099 / LeetCode #146) — OrderedDict with values
# VARIANT 2: functools.lru_cache(maxsize=3) decorator for memoised functions
# VARIANT 3: Sliding window of last N events — deque(maxlen=N) evicts automatically
from collections import deque
w = deque(maxlen=3)                             # auto-evicting window
for i in range(5):                              # push 0..4
    w.append(i)                                 # oldest drops when full
print(list(w))                                  # [2, 3, 4]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: not removing the old occurrence before appending -> duplicates in the queue
#    q.append(x)  # x now appears twice, capacity is wasted
# ❌ Wrong: using list.pop(0) to evict — O(n); deque.popleft() is O(1)
# ✅ Correct: remove (or move_to_end) first, then append; evict with popleft()
```

---

## 🎯 Interview Tip
Say: "deque gives O(1) at both ends but O(n) removal from the middle. For true O(1) recency updates I use OrderedDict.move_to_end, or a hash map plus doubly linked list." Name `deque(maxlen=)` for simple sliding windows.

---

## 🔗 Related Problems
→ Q099 (Implement LRU cache) | D044 (Implement Queue using Stacks) | D051 (Design Circular Queue)
