---

# D051. Design Circular Queue
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #622 | Asked: Amazon, Microsoft, Google

---

## ❓ Problem
Design a fixed-size circular queue (ring buffer) with `en_queue`, `de_queue`, `front`, `rear`, `is_empty`, `is_full`. Reuse freed slots — no shifting elements.

```
q = CircularQueue(3)
en_queue(1), en_queue(2), en_queue(3) -> True True True
en_queue(4) -> False (full)
de_queue()  -> True
en_queue(4) -> True   (reuses freed slot)
rear()      -> 4
```

---

## 💡 Quick Concept (2 lines only)
Keep a fixed array, a `head` index and a `size` counter. The tail slot is `(head + size) % capacity`; indices wrap around with the modulo operator.
हिंदी: Fixed array, `head` और `size` रखो; नई जगह `(head + size) % capacity` होती है, modulo से index घूमकर शुरू पर आ जाता है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — list with pop(0) / append
# en_queue O(1), de_queue O(n) because pop(0) shifts everything
# ============================================
class CircularQueueBrute:
    def __init__(self, k: int) -> None:
        self.k = k                              # capacity
        self.items: list[int] = []              # plain list as queue

    def en_queue(self, v: int) -> bool:
        if len(self.items) == self.k:           # full
            return False                        # reject
        self.items.append(v)                    # add at back
        return True                             # success

    def de_queue(self) -> bool:
        if not self.items:                      # empty
            return False                        # nothing to remove
        self.items.pop(0)                       # O(n) shift
        return True                             # success

    def front(self) -> int:
        return self.items[0] if self.items else -1  # -1 when empty

    def rear(self) -> int:
        return self.items[-1] if self.items else -1  # -1 when empty

    def is_empty(self) -> bool:
        return not self.items                   # no items

    def is_full(self) -> bool:
        return len(self.items) == self.k        # at capacity


# ============================================
# APPROACH 2: Fixed array + head + size — all O(1) ✅ PREFERRED
# ============================================
class CircularQueue:
    def __init__(self, k: int) -> None:
        self.k = k                              # capacity
        self.buf: list[int] = [0] * k           # preallocated ring buffer
        self.head = 0                           # index of the front element
        self.size = 0                           # current number of items

    def en_queue(self, v: int) -> bool:
        if self.is_full():                      # no space
            return False                        # reject
        self.buf[(self.head + self.size) % self.k] = v  # write at wrapped tail slot
        self.size += 1                          # one more item
        return True                             # success

    def de_queue(self) -> bool:
        if self.is_empty():                     # nothing to remove
            return False                        # reject
        self.head = (self.head + 1) % self.k    # move head forward, wrapping
        self.size -= 1                          # one less item
        return True                             # success

    def front(self) -> int:
        return -1 if self.is_empty() else self.buf[self.head]  # front item

    def rear(self) -> int:
        return -1 if self.is_empty() else self.buf[(self.head + self.size - 1) % self.k]  # last item

    def is_empty(self) -> bool:
        return self.size == 0                   # no items

    def is_full(self) -> bool:
        return self.size == self.k              # at capacity


# ============================================
# TEST CASES
# ============================================
for cls in (CircularQueueBrute, CircularQueue): # same test for both
    q = cls(3)                                  # capacity 3
    print(q.en_queue(1), q.en_queue(2), q.en_queue(3))  # True True True
    print(q.en_queue(4))                        # False
    print(q.rear(), q.is_full())                # 3 True
    print(q.de_queue())                         # True
    print(q.en_queue(4))                        # True
    print(q.front(), q.rear())                  # 2 4
    print(q.de_queue(), q.de_queue(), q.de_queue(), q.de_queue())  # True True True False
    print(q.front(), q.rear(), q.is_empty())    # -1 -1 True
```

---

## 🔍 Why It Works
```
cap=3, buf=[_,_,_]  head=0 size=0
en 1,2,3 -> buf=[1,2,3] size=3 (full)
de       -> head=1 size=2
en 4     -> slot (1+2)%3 = 0 -> buf=[4,2,3] size=3   (wrapped!)
front=buf[1]=2   rear=buf[(1+3-1)%3]=buf[0]=4
```
हिंदी: head और size से ही खाली/भरा पता चल जाता है, और modulo की वजह से कोई element खिसकाना नहीं पड़ता।

---

## 📊 Complexity
```
Brute force (list.pop(0)): en_queue O(1), de_queue O(n) | Space O(k)
Ring buffer:               all operations O(1)          | Space O(k) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Circular Deque (LeetCode #641) — also move head backwards: (head - 1) % k
# VARIANT 2: Use head + tail pointers with one wasted slot (size k+1) to tell full vs empty
# VARIANT 3: Python shortcut: collections.deque(maxlen=k) — but it overwrites instead of rejecting
from collections import deque
d: deque[int] = deque(maxlen=3)                 # bounded deque
for i in range(5):                              # push 0..4
    d.append(i)                                 # oldest silently dropped
print(list(d))                                  # [2, 3, 4]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: tracking only head and tail — head == tail is ambiguous (empty OR full)
# ❌ Wrong: forgetting % k -> IndexError when the tail passes the end of the array
# ✅ Correct: keep a size counter (or a spare slot) and wrap every index with % k
```

---

## 🎯 Interview Tip
Say: "A size counter removes the full-vs-empty ambiguity, and modulo arithmetic makes every operation O(1) with no shifting." Mention that ring buffers are used for streaming and network buffers.

---

## 🔗 Related Problems
→ D044 (Implement Queue using Stacks) | D050 (Implement LRU-style Queue with deque) | Q101 (Implement queue)
