---

# Q154. Complete Stack Class
# Category: Complete The Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Complete a generic `Stack` (LIFO) with `push`, `pop`, `peek`, `is_empty`, `len()` and a friendly error on empty pop.

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.____(item)                     # BLANK 1: add to the top

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.____()                  # BLANK 2: remove from the top

    def peek(self) -> T:
        return self._items[____]                   # BLANK 3: look at the top without removing

    def is_empty(self) -> bool:
        return not self._items

    def ____(self) -> int:                         # BLANK 4: makes len(stack) work
        return len(self._items)
```

---

## 💡 Quick Concept (2 lines only)
A stack is Last-In-First-Out; a Python list is a perfect backing store because `append` and `pop()` at the end are O(1).
हिंदी: Stack में आख़िर में डाला गया सबसे पहले निकलता है; list का `append`/`pop()` O(1) है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Generic, TypeVar                # generic container typing

T = TypeVar("T")                                   # element type


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []                  # Step 1: end of the list = top of the stack

    def push(self, item: T) -> None:               # O(1)
        self._items.append(item)                   # BLANK 1: add on top

    def pop(self) -> T:                            # O(1)
        if self.is_empty():                        # guard: nothing to remove
            raise IndexError("pop from empty stack")  # clear message
        return self._items.pop()                   # BLANK 2: remove and return the top

    def peek(self) -> T:                           # O(1)
        if self.is_empty():                        # guard
            raise IndexError("peek from empty stack")
        return self._items[-1]                     # BLANK 3: last element = top

    def is_empty(self) -> bool:
        return not self._items                     # empty list is falsy

    def __len__(self) -> int:                      # BLANK 4: enables len(s) and truthiness
        return len(self._items)


# ============================================
# TEST CASES
# ============================================
s: Stack[int] = Stack()
s.push(1); s.push(2); s.push(3)                    # stack: 1 2 3 (top = 3)
print(s.peek())                                    # Expected: 3
print(s.pop(), s.pop())                            # Expected: 3 2
print(len(s), s.is_empty())                        # Expected: 1 False
s.pop()                                            # now empty
print(s.is_empty())                                # Expected: True
try:
    s.pop()                                        # pop on empty
except IndexError as e:
    print(e)                                       # Expected: pop from empty stack
```

---

## 🔍 Why This Works (3 lines max)
The list's right end is the top, so push/pop are amortised O(1). Guarding against empty gives a clear `IndexError`, and `__len__` lets `len(s)` and `if s:` work naturally.
हिंदी: List का आख़िरी सिरा ही top है, इसलिए push/pop तेज़ हैं; `__len__` से `len(s)` काम करता है।

---

## ⚡ Alternative Solution
```python
# Simplest: use a list directly, or collections.deque (also O(1) at both ends)
from collections import deque

stack: list[int] = []                              # plain list as stack
stack.append(1); stack.append(2)                   # push
print(stack.pop())                                 # Expected: 2

d: deque[int] = deque()                            # deque is the thread-friendly option
d.append(1); d.append(2)
print(d.pop(), d[-1])                              # Expected: 2 1

def balanced(s: str) -> bool:                      # classic stack use: bracket matching
    pairs, st = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{": st.append(ch)              # open -> push
        elif ch in pairs:
            if not st or st.pop() != pairs[ch]: return False  # mismatch
    return not st                                  # nothing left open

print(balanced("([]{})"), balanced("(]"))          # Expected: True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: list.pop(0) / insert(0, x) as "push/pop" -> O(n) each time (that is a slow queue-like use)
# ❌ Wrong: no empty check -> raw "IndexError: pop from empty list" leaks implementation detail
# ❌ Wrong: peek() returning self._items.pop() -> peek must not remove
# ✅ Correct: append/pop at the END, guard empty, peek via [-1]
```

---

## 🎯 Interview Tip (1 line)
Say: "Stack = LIFO with O(1) push/pop; list is enough, deque for thread-safety and queues; classic uses are bracket matching, undo and DFS."

---

## 🔗 Related Questions
→ Q100 (implement stack) | Q101 (implement queue) | Q153 (linked list) | D042 (valid parentheses) | D043 (min stack)
