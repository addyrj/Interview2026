---

# D044. Implement Queue using Stacks
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #232 | Asked: Amazon, Microsoft, Bloomberg, Adobe

---

## ❓ Problem
Implement a FIFO queue (`push`, `pop`, `peek`, `empty`) using only stack operations (append / pop from the end of a list).

```
push(1), push(2)
peek()  -> 1
pop()   -> 1
empty() -> False
```

---

## 💡 Quick Concept (2 lines only)
Use two stacks: `inbox` receives pushes; `outbox` serves pops. Only when `outbox` is empty, pour all of `inbox` into it — this reverses the order to FIFO.
हिंदी: दो stacks रखो — push inbox में, pop outbox से; outbox खाली हो तभी inbox को उसमें उलट दो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — move everything on every push
# push O(n), pop/peek O(1)
# ============================================
class QueueBrute:
    def __init__(self) -> None:
        self.s: list[int] = []                  # main stack, front of queue on top

    def push(self, x: int) -> None:
        tmp: list[int] = []                     # helper stack
        while self.s:                           # unload everything
            tmp.append(self.s.pop())            # reverse into helper
        self.s.append(x)                        # new item goes to bottom
        while tmp:                              # reload everything
            self.s.append(tmp.pop())            # restore order, x is now at the back

    def pop(self) -> int:
        return self.s.pop()                     # front of queue is the top

    def peek(self) -> int:
        return self.s[-1]                       # front of queue

    def empty(self) -> bool:
        return not self.s                       # no items


# ============================================
# APPROACH 2: Two stacks, lazy transfer — amortized O(1) ✅ PREFERRED
# ============================================
class MyQueue:
    def __init__(self) -> None:
        self.inbox: list[int] = []              # new items arrive here
        self.outbox: list[int] = []             # items ready to leave, front on top

    def push(self, x: int) -> None:
        self.inbox.append(x)                    # O(1)

    def _shift(self) -> None:
        if not self.outbox:                     # only refill when empty
            while self.inbox:                   # pour all of inbox
                self.outbox.append(self.inbox.pop())  # reverses order -> FIFO

    def pop(self) -> int:
        self._shift()                           # make sure outbox has the front
        return self.outbox.pop()                # remove front

    def peek(self) -> int:
        self._shift()                           # make sure outbox has the front
        return self.outbox[-1]                  # look at front

    def empty(self) -> bool:
        return not self.inbox and not self.outbox  # both stacks empty


# ============================================
# TEST CASES
# ============================================
for cls in (QueueBrute, MyQueue):               # same test for both
    q = cls()                                   # fresh queue
    q.push(1); q.push(2); q.push(3)             # enqueue 1,2,3
    print(q.peek())                             # 1
    print(q.pop())                              # 1
    q.push(4)                                   # enqueue while outbox non-empty
    print(q.pop(), q.pop(), q.pop())            # 2 3 4
    print(q.empty())                            # True
```

---

## 🔍 Why It Works
```
push 1,2,3  inbox=[1,2,3]  outbox=[]
pop -> outbox empty -> pour: outbox=[3,2,1], inbox=[]  -> pop gives 1
push 4      inbox=[4]      outbox=[3,2]
pop -> 2, pop -> 3, pop -> outbox empty -> pour -> 4
Each element moves between stacks at most once => amortized O(1).
```
हिंदी: हर element ज़्यादा से ज़्यादा एक बार inbox से outbox जाता है, इसलिए औसतन हर operation O(1) है।

---

## 📊 Complexity
```
Brute force: push O(n), pop/peek O(1) | Space O(n)
Two stacks:  push O(1), pop/peek amortized O(1), worst single pop O(n) | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Implement a Stack using two queues (LeetCode #225) — rotate after each push
# VARIANT 2: Queue with a single stack using recursion (call stack as the 2nd stack)
# VARIANT 3: In real Python code just use collections.deque
from collections import deque
d: deque[int] = deque([1, 2, 3])                # O(1) popleft
print(d.popleft())                              # 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: pouring inbox into outbox on EVERY pop — breaks order when outbox still has items
#    outbox=[3,2] + pour inbox=[4] -> [3,2,4] -> pop gives 4 before 2 (wrong!)
# ✅ Correct: pour ONLY when outbox is empty
```

---

## 🎯 Interview Tip
Say: "Two stacks reverse twice to get FIFO. Pouring only when outbox is empty keeps order and gives amortized O(1)." Be ready to explain amortized vs worst-case.

---

## 🔗 Related Problems
→ D043 (Min Stack) | D051 (Design Circular Queue) | D050 (Implement LRU-style Queue with deque)
