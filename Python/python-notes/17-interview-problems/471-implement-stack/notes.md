---

# 471. Implement Stack
# हिंदी में: Stack बनाना (LIFO)

Full runnable solution (list stack, linked stack, MinStack, tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
A stack is a collection where the last item added is the first one removed (LIFO: Last In, First Out). The three core operations are `push` (add on top), `pop` (remove from top) and `peek` (look at top). In Python a list already works as a stack.

## 🔵 सरल परिभाषा (Hindi)
Stack ऐसा collection है जिसमें आख़िरी जोड़ा गया item सबसे पहले निकलता है (LIFO: Last In, First Out)। मुख्य operations: `push` (ऊपर जोड़ना), `pop` (ऊपर से निकालना) और `peek` (ऊपर वाला देखना)। Python में list खुद stack का काम कर देती है।

---

## 🔴 Problem it Solves
Many problems need "undo the most recent thing first": the browser back button, editor undo, function calls, bracket matching and depth-first search. A stack models this exactly, with O(1) push and pop.

## 🔴 यह क्यों बना? (Hindi)
कई problems में "सबसे हाल की चीज़ पहले undo करो" चाहिए: browser का back button, editor का undo, function calls, bracket matching और depth-first search। Stack यही दिखाता है, push और pop दोनों O(1) में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a list; the END of the list is the top
Step 2 → push(x): list.append(x)
Step 3 → pop(): if empty raise an error, else list.pop()
Step 4 → peek(): return list[-1] without removing
Step 5 → is_empty(): not list
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक list रखो; list का आख़िरी हिस्सा ही top है
Step 2 → push(x): list.append(x)
Step 3 → pop(): खाली हो तो error, नहीं तो list.pop()
Step 4 → peek(): बिना निकाले list[-1] लौटाओ
Step 5 → is_empty(): not list
```

---

## 🟡 Real World Example
An editor like VS Code keeps an undo stack: every edit is pushed, Ctrl+Z pops the last one. A Swiggy app navigation stack: each screen is pushed, the back button pops. Python's own call stack works the same way, which is why deep recursion raises `RecursionError`.

## 🟡 Real Example Hindi mein
VS Code जैसे editor में undo stack होता है: हर edit push होता है, Ctrl+Z आख़िरी को pop करता है। Swiggy app के navigation stack में हर screen push होती है और back button pop करता है। Python का call stack भी ऐसे ही चलता है, इसीलिए बहुत गहरी recursion पर `RecursionError` आता है।

---

## 💻 Code Example — Basic
```python
# Basic stack class backed by a list
class Stack:  # simple LIFO container
    def __init__(self) -> None:  # constructor
        self._items: list[int] = []  # end of list is the top

    def push(self, item: int) -> None:  # add on top
        self._items.append(item)  # O(1) amortized

    def pop(self) -> int:  # remove and return the top
        if not self._items:  # empty stack
            raise IndexError("pop from empty stack")  # clear error
        return self._items.pop()  # O(1)

    def peek(self) -> int:  # look at the top
        if not self._items:  # empty stack
            raise IndexError("peek from empty stack")  # clear error
        return self._items[-1]  # last item

    def is_empty(self) -> bool:  # check emptiness
        return not self._items  # empty list is falsy


s = Stack()  # create
s.push(1)  # stack: 1
s.push(2)  # stack: 1 2
s.push(3)  # stack: 1 2 3
print(s.peek())  # top without removing
# Output: 3
print(s.pop(), s.pop(), s.pop())  # reverse order of pushing
# Output: 3 2 1
print(s.is_empty())  # nothing left
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: generic, linked version, MinStack (min in O(1))
from __future__ import annotations  # forward references
from typing import Generic, List, Optional, TypeVar  # type hints

T = TypeVar("T")  # element type


class Node(Generic[T]):  # linked-list node
    def __init__(self, value: T, below: Optional[Node[T]]) -> None:
        self.value: T = value  # stored value
        self.below: Optional[Node[T]] = below  # node under this one


class LinkedStack(Generic[T]):
    """Every operation is true O(1), no list resizing."""

    def __init__(self) -> None:
        self._top: Optional[Node[T]] = None  # head is the top
        self._size: int = 0  # number of items

    def push(self, item: T) -> None:
        self._top = Node(item, self._top)  # new node points to old top
        self._size += 1  # count

    def pop(self) -> T:
        if self._top is None:  # empty
            raise IndexError("pop from empty stack")  # error
        node = self._top  # current top
        self._top = node.below  # move head down
        self._size -= 1  # count
        return node.value  # value

    def __len__(self) -> int:
        return self._size  # item count


class MinStack:
    """push, pop, top and get_min are all O(1)."""

    def __init__(self) -> None:
        self._data: List[int] = []  # values
        self._mins: List[int] = []  # minimum at each depth

    def push(self, x: int) -> None:
        self._data.append(x)  # store value
        self._mins.append(x if not self._mins else min(x, self._mins[-1]))  # running minimum

    def pop(self) -> int:
        self._mins.pop()  # drop the min snapshot
        return self._data.pop()  # drop the value

    def get_min(self) -> int:
        return self._mins[-1]  # current minimum


ls: LinkedStack[str] = LinkedStack()  # create
ls.push("a")  # push a
ls.push("b")  # push b
print(ls.pop(), len(ls))  # LIFO: b first
# Output: b 1

ms = MinStack()  # create
for v in (5, 3, 7, 3, 1):  # push values
    ms.push(v)  # push
print(ms.get_min())  # smallest so far
# Output: 1
ms.pop()  # remove 1
print(ms.get_min())  # minimum goes back to 3
# Output: 3

from collections import deque  # alternative for queues AND stacks
d: deque[int] = deque([1, 2])  # create
d.append(3)  # push
print(d.pop())  # pop from the same end
# Output: 3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
stack: list[int] = []
stack.append(1)     # push
top = stack[-1]     # peek
stack.pop()         # pop, IndexError if empty
```

```javascript
// JavaScript
const stack = [];
stack.push(1);                    // push
const top = stack[stack.length - 1];   // peek
stack.pop();                      // pop, returns undefined if empty
```

Key difference: Python `pop()` on an empty list raises `IndexError`, while JS returns `undefined` silently. Python also gives `stack[-1]` for peek.

---

## 🟠 FastAPI Connection
FastAPI endpoints do not usually keep a stack in memory (many workers do not share it). A typical use is an undo history stored in Redis or a DB. For a single process demo, protect shared state with a lock.

```python
# FastAPI: undo stack demo (single worker only) (pip install fastapi)
from fastapi import FastAPI, HTTPException  # app and errors

app: FastAPI = FastAPI()  # create app
history: list[str] = []  # in-memory stack (lost on restart, not shared between workers)


@app.post("/edit")  # POST /edit?text=hello
def edit(text: str) -> dict[str, int]:
    history.append(text)  # push
    return {"size": len(history)}  # current depth


@app.post("/undo")  # POST /undo
def undo() -> dict[str, str]:
    if not history:  # empty stack
        raise HTTPException(status_code=409, detail="nothing to undo")  # error
    return {"undone": history.pop()}  # pop
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `pop(0)` as the stack top
```python
# Wrong - O(n) because every item shifts:
# stack.pop(0)

# Correct - push and pop at the END: append() / pop()
```

❌ Mistake 2: Popping without checking
```python
# Wrong:
# [].pop()   # IndexError: pop from empty list

# Correct:
# if stack: stack.pop()
```

❌ Mistake 3: Using `queue.LifoQueue` when threads are not involved
```python
# Wrong - LifoQueue adds locking overhead that a single thread does not need

# Correct - plain list or deque for single-thread; LifoQueue only for thread-safe sharing
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
stack = [1, 2, 3]
print(stack.pop(), stack)
print(stack[-1], stack.pop(0), stack)
try:
    [].pop()
except IndexError as e:
    print(e)
print(bool([]), bool([0]))
```

**Answer**:
```
3 [1, 2]
2 1 [2]
pop from empty list
False True
```
`pop()` removes from the end. In the second line the arguments are evaluated left to right: `stack[-1]` is `2`, then `pop(0)` removes `1`, then `stack` prints `[2]`. An empty list is falsy, but `[0]` is truthy because it has an item.

---

## ⚫ Interview Questions + Answers

Q1: What are the time complexities?
A1: `push`, `pop`, `peek`, `is_empty` are all O(1) (amortized for `list.append`).

Q2: Why is `list.append` "amortized" O(1)?
A2: The list sometimes resizes, which costs O(n), but spread over many appends the average is O(1).

Q3: List vs deque vs linked list for a stack?
A3: List is simplest and fastest in practice. `deque` has true O(1) at both ends. A linked list has no resize but uses more memory per item.

Q4: How do you get the minimum in O(1)?
A4: Keep a second stack of running minimums (`MinStack`).

Q5: Name classic stack problems.
A5: Valid parentheses, evaluating postfix expressions, next greater element, DFS, undo/redo, browser history.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need LIFO order (undo, DFS, parsing)
- You process the most recent item first

❌ Avoid when:
- You need FIFO order (use `collections.deque` as a queue)
- You need random access by index or search (use a list or dict)
- Threads share it (use `queue.LifoQueue`)

---

## 📊 Visual Diagram

```
push 1, push 2, push 3        pop -> 3

   |   |     |   |     |   3 |        |   |
   |   |     | 2 |     | 2   |        | 2 |
   | 1 |     | 1 |     | 1   |        | 1 |
   +---+     +---+     +-----+        +---+
   top=1     top=2     top=3          top=2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LIFO | Last In, First Out | आख़िरी आया, पहले गया |
| push | Add on top | ऊपर जोड़ना |
| pop | Remove from top | ऊपर से निकालना |
| peek | Read top without removing | बिना निकाले ऊपर देखना |
| Amortized | Average cost over many operations | कई operations का औसत खर्च |

---

## ⚡ 3-Line Summary
English: A stack is LIFO with O(1) push, pop and peek. In Python use a list (`append`/`pop` at the end) or `deque`. Raise `IndexError` on empty pop and use a second stack for O(1) minimum.
Hindi: Stack LIFO है, push, pop और peek O(1) में। Python में list (`append`/`pop` अंत में) या `deque` इस्तेमाल करो। खाली stack पर `IndexError` दो और O(1) minimum के लिए दूसरा stack रखो।

---

## ➡️ Next Topic
**472. Implement Queue** — the FIFO partner of a stack, using `collections.deque`.
