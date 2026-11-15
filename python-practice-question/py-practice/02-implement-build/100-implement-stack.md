---

# Q100. Implement Stack
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Stack` class (LIFO) with `push`, `pop`, `peek`, `is_empty` and `len()`.
`pop`/`peek` on an empty stack should raise `IndexError` with a clear message.

```python
s = Stack()
s.push(1); s.push(2)
s.pop()   # 2  (last in, first out)
```

---

## 💡 Quick Concept (2 lines only)
A stack is Last-In-First-Out: add and remove only at the top. A Python `list` gives O(1) amortized `append`/`pop` at the end.
हिंदी: Stack में जो सबसे आखिर में आया वही सबसे पहले निकलता है — list का end ही top है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Generic, TypeVar  # for a typed generic container

T = TypeVar("T")  # element type

class Stack(Generic[T]):  # LIFO stack
    def __init__(self) -> None:  # constructor
        self._items: list[T] = []  # Step 1: list end = top of stack

    def push(self, item: T) -> None:  # add to the top
        self._items.append(item)  # Step 2: O(1) amortized

    def pop(self) -> T:  # remove + return the top
        if not self._items:  # Step 3: empty check
            raise IndexError("pop from empty stack")  # clear error message
        return self._items.pop()  # O(1)

    def peek(self) -> T:  # look at top without removing
        if not self._items:  # empty check
            raise IndexError("peek from empty stack")  # clear error
        return self._items[-1]  # last element is the top

    def is_empty(self) -> bool:  # emptiness test
        return not self._items  # True when no items

    def __len__(self) -> int:  # makes len(stack) work
        return len(self._items)  # size of the list

    def __repr__(self) -> str:  # debug-friendly output
        return f"Stack({self._items})"  # show contents bottom -> top

# ============================================
# TEST CASES
# ============================================
s: Stack[int] = Stack()  # new empty stack
s.push(1); s.push(2); s.push(3)  # push three values
print(s)  # Expected: Stack([1, 2, 3])
print(s.pop())  # Expected: 3
print(s.peek())  # Expected: 2
print(len(s))  # Expected: 2
print(s.is_empty())  # Expected: False
s.pop(); s.pop()  # empty it
print(s.is_empty())  # Expected: True
try:  # popping an empty stack
    s.pop()  # should raise
except IndexError as e:  # catch it
    print(e)  # Expected: pop from empty stack
```

---

## 🔍 Why This Works (3 lines max)
`list.append` and `list.pop()` both work on the end, so push and pop are O(1) amortized. Guarding with an explicit check gives a friendlier error than the raw list message.
हिंदी: list का end पर append/pop तेज़ है, इसलिए list ही stack के लिए सही है।

---

## ⚡ Alternative Solution
```python
# In real code a plain list IS the stack (no class needed)
st: list[int] = []  # empty stack
st.append(1); st.append(2)  # push 1 then 2
print(st.pop(), st[-1])  # Expected: 2 1  (pop returns 2, peek shows 1)
# collections.deque also works: append()/pop() are O(1) and thread-safe for single ops
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: pop(0) removes from the FRONT -> that is a queue (FIFO), and O(n)
st2 = [1, 2, 3]
print(st2.pop(0))  # prints 1 (not LIFO!)

# ✅ Correct: pop() with no argument removes the last element
st2 = [1, 2, 3]
print(st2.pop())  # prints 3
```

---

## 🎯 Interview Tip (1 line)
Say: "Stack = LIFO; list append/pop at the end are O(1); I'd use a stack for brackets matching, undo, and DFS."

---

## 🔗 Related Questions
→ Q101 (queue) | Q102 (linked list) | Q154 (complete stack class) | Q200 (undo/redo)
