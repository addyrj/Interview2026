---

# 052. List Methods (append, extend, insert, remove, pop, sort, reverse)
# हिंदी में: List के Methods

---

## 🔵 Simple Definition (English)
List methods are built-in functions attached to every list that add, remove, find, order or copy items. Most of them change the list IN PLACE and return `None`, which is the single biggest source of beginner bugs. The key ones are `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `reverse`, `index`, `count`, `copy`, `clear`.

## 🔵 सरल परिभाषा (Hindi)
List methods हर list के साथ आने वाले built-in functions हैं जो items जोड़ते, हटाते, खोजते, sort करते या copy करते हैं। ज़्यादातर methods list को वहीं बदल देते हैं (in place) और `None` return करते हैं। यही सबसे आम गलती का कारण है। मुख्य methods: `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `reverse`, `index`, `count`, `copy`, `clear`।

---

## 🔴 Problem it Solves
Without methods you would have to write loops and index arithmetic for every common task (add to the end, delete a value, sort). Methods give a tested, fast (implemented in C) vocabulary so the code says what it means: `cart.append(item)` instead of manual resizing.

## 🔴 यह क्यों बना? (Hindi)
Methods के बिना हर काम (अंत में जोड़ना, value हटाना, sort करना) के लिए loop और index का हिसाब खुद लिखना पड़ता। Methods C में लिखे tested और तेज़ हैं, इसलिए code वही कहता है जो वह करता है: `cart.append(item)`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A list is a dynamic array of references: [ref0, ref1, ref2, ...]
Step 2 → append(x)       adds x at the END           O(1) amortized
Step 3 → extend(iter)    adds EACH item of iter      O(k)
Step 4 → insert(i, x)    shifts items right, adds x  O(n)
Step 5 → remove(x)       deletes FIRST match by value (ValueError if missing)  O(n)
Step 6 → pop(i=-1)       deletes by index AND returns it; pop() end O(1), pop(0) O(n)
Step 7 → sort()/reverse() reorder IN PLACE and return None
Step 8 → sorted(lst)/reversed(lst) return NEW objects, original untouched
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → list references की dynamic array है
Step 2 → append(x): अंत में एक item जोड़ता है, O(1)
Step 3 → extend(iter): iterable के हर item को जोड़ता है
Step 4 → insert(i, x): बीच में जोड़ता है, items खिसकते हैं, O(n)
Step 5 → remove(x): value से पहला match हटाता है (नहीं मिला तो ValueError)
Step 6 → pop(i): index से हटाकर वही item return करता है
Step 7 → sort()/reverse(): list को वहीं बदलते हैं, None return करते हैं
Step 8 → sorted()/reversed(): नई चीज़ देते हैं, original वैसी ही रहती है
```

---

## 🟡 Real World Example
Swiggy cart: `cart.append(item)` when user adds a dish, `cart.remove(item)` when they remove it, `cart.extend(combo_items)` for a combo offer, `cart.sort(key=lambda i: i["price"])` to sort by price. A task queue uses `queue.pop(0)` (better: `collections.deque.popleft()`) to take the oldest job.

## 🟡 Real Example Hindi mein
Swiggy cart: dish जोड़ने पर `cart.append(item)`, हटाने पर `cart.remove(item)`, combo offer में `cart.extend(combo_items)`, price से sort करने के लिए `cart.sort(key=...)`। Task queue में सबसे पुराना job `pop(0)` से लिया जाता है (बेहतर: `deque.popleft()`)।

---

## 💻 Code Example — Basic
```python
# Basic list methods, one by one
fruits: list[str] = ["apple", "banana"]  # start with two items

fruits.append("cherry")          # add ONE item at the end
print(fruits)                    # Output: ['apple', 'banana', 'cherry']

fruits.extend(["date", "fig"])   # add EACH item of another iterable
print(fruits)                    # Output: ['apple', 'banana', 'cherry', 'date', 'fig']

fruits.insert(1, "blueberry")    # insert at index 1, others shift right
print(fruits)                    # Output: ['apple', 'blueberry', 'banana', 'cherry', 'date', 'fig']

fruits.remove("banana")          # remove first item equal to "banana"
print(fruits)                    # Output: ['apple', 'blueberry', 'cherry', 'date', 'fig']

last: str = fruits.pop()         # remove and return the LAST item
print(last, fruits)              # Output: fig ['apple', 'blueberry', 'cherry', 'date']

first: str = fruits.pop(0)       # remove and return item at index 0
print(first, fruits)             # Output: apple ['blueberry', 'cherry', 'date']

nums: list[int] = [3, 1, 2]      # numbers to order
nums.sort()                      # sort in place (ascending)
print(nums)                      # Output: [1, 2, 3]
nums.reverse()                   # reverse in place
print(nums)                      # Output: [3, 2, 1]

print(nums.index(2))             # position of first 2 -> Output: 1
print([1, 2, 2, 3].count(2))     # how many 2s -> Output: 2

result = nums.sort()             # sort returns None!
print(result)                    # Output: None
```

## 💻 Code Example — Advanced
```python
# Production style: safe removal, stable sort with key, copy semantics, queue vs deque
from collections import deque  # efficient double-ended queue
from typing import TypedDict  # typed dictionary for records


class Item(TypedDict):  # one cart item
    name: str  # item name
    price: float  # price in rupees


cart: list[Item] = [  # sample cart
    {"name": "Biryani", "price": 250.0},
    {"name": "Raita", "price": 40.0},
    {"name": "Coke", "price": 40.0},
]

# 1. sort by price then keep original order for ties (sort is STABLE)
cart.sort(key=lambda i: i["price"])  # lambda gives the sort key
print([i["name"] for i in cart])  # Output: ['Raita', 'Coke', 'Biryani']

# 2. sort descending with reverse=True (stable even when reversed)
cart.sort(key=lambda i: i["price"], reverse=True)  # highest price first
print([i["name"] for i in cart])  # Output: ['Biryani', 'Raita', 'Coke']

# 3. Safe remove: remove() raises ValueError when missing
def safe_remove(items: list[str], value: str) -> bool:  # returns whether something was removed
    try:  # attempt removal
        items.remove(value)  # may raise ValueError
        return True  # success
    except ValueError:  # value not in list
        return False  # nothing removed

names: list[str] = ["a", "b", "c"]  # sample names
print(safe_remove(names, "b"), safe_remove(names, "z"), names)  # Output: True False ['a', 'c']

# 4. Remove while iterating: build a new list instead (never mutate during a loop)
nums: list[int] = [1, 2, 3, 4, 5, 6]  # numbers
nums = [n for n in nums if n % 2 != 0]  # keep odds only
print(nums)  # Output: [1, 3, 5]

# 5. append vs extend vs +=
a: list[int] = [1, 2]  # base list
a.append([3, 4])  # appends ONE item that is itself a list
print(a)  # Output: [1, 2, [3, 4]]
b: list[int] = [1, 2]  # base list
b.extend([3, 4])  # appends each element
print(b)  # Output: [1, 2, 3, 4]
b += [5]  # += behaves like extend (in place)
print(b)  # Output: [1, 2, 3, 4, 5]

# 6. copy semantics: copy() is shallow
orig: list[list[int]] = [[1], [2]]  # nested list
shallow: list[list[int]] = orig.copy()  # new outer list, SAME inner lists
shallow[0].append(99)  # mutate an inner list
print(orig)  # Output: [[1, 99], [2]]  (original also changed!)

# 7. pop(0) is O(n); use deque.popleft() for queues
q: deque[str] = deque(["job1", "job2", "job3"])  # queue of jobs
print(q.popleft(), list(q))  # Output: job1 ['job2', 'job3']

# 8. clear and del
data: list[int] = [1, 2, 3, 4]  # numbers
del data[0]  # delete by index (statement, no return)
print(data)  # Output: [2, 3, 4]
data.clear()  # remove everything
print(data)  # Output: []
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
items: list[int] = [1, 2, 3]
items.append(4)            # push
items.pop()                # pop (end)  -> 4
items.pop(0)               # shift      -> 1  (O(n))
items.insert(0, 9)         # unshift
items.extend([7, 8])       # push(...[7, 8])
items.remove(7)            # remove by VALUE (JS has no direct method)
items.sort()               # in place, numbers sorted NUMERICALLY by default
items.reverse()            # in place
print(items)               # [9, 8, 3, 2]
```
```javascript
// JavaScript
const items = [1, 2, 3];
items.push(4);               // append
items.pop();                 // pop end
items.shift();               // pop(0)
items.unshift(9);            // insert(0, 9)
items.push(...[7, 8]);       // extend
items.splice(items.indexOf(7), 1);  // remove by value
items.sort();                // WARNING: sorts as STRINGS by default! [10, 9, 1] -> [1, 10, 9]
items.sort((a, b) => a - b); // numeric sort needs a comparator
items.reverse();             // in place
```

---

## 🟠 FastAPI Connection
In FastAPI, list methods build responses and collect validation errors. Query parameters declared as `list[str]` arrive as real Python lists; you then `sort`, `extend` or filter them. Remember a mutable default list in a function signature is shared between calls, so use `None` or Pydantic's `Field(default_factory=list)`.

```python
from fastapi import FastAPI, Query  # app and query helper
from pydantic import BaseModel, Field  # validation models

app: FastAPI = FastAPI()  # create app

class Cart(BaseModel):  # cart model
    items: list[str] = Field(default_factory=list)  # fresh list per cart (NOT items: list = [])

@app.get("/tags")  # GET /tags?tag=b&tag=a
async def tags(tag: list[str] = Query(default=[])) -> dict[str, list[str]]:
    result: list[str] = list(tag)  # copy so we never mutate request data
    result.sort()  # in-place sort of our copy
    return {"sorted": result}  # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the return value of in-place methods
```python
# Wrong:
nums = [3, 1, 2]
nums = nums.sort()          # nums is now None!

# Right:
nums = [3, 1, 2]
nums.sort()                 # in place
sorted_nums = sorted(nums)  # or get a new list
```

❌ Mistake 2: Removing items while looping over the same list
```python
# Wrong:
nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)      # skips elements -> result [1, 2, 3]

# Right:
nums = [n for n in nums if n != 2]   # [1, 3]
```

❌ Mistake 3: append vs extend confusion
```python
# Wrong:
x = [1]
x.append([2, 3])    # [1, [2, 3]]  nested!
# Right:
x = [1]
x.extend([2, 3])    # [1, 2, 3]
```

---

## 🧠 Tricky Interview Question

```python
a = [1, 2, 3]
b = a.append(4)
c = a + [5]
a += [6]
print(a, b, c)
```
Answer: `[1, 2, 3, 4, 6] None [1, 2, 3, 4, 5]`. `append` returns `None` so `b` is `None`. `a + [5]` creates a NEW list `c` (a is unchanged at that point). `a += [6]` mutates `a` in place (like `extend`). Follow-up: with a tuple `t += (1,)` creates a new tuple because tuples are immutable.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `append` and `extend`?
A1: `append(x)` adds `x` as ONE element (even if x is a list). `extend(iterable)` adds each element of the iterable individually. `lst.append([1, 2])` makes a nested list; `lst.extend([1, 2])` adds two items.

Q2: What is the difference between `remove`, `pop` and `del`?
A2: `remove(value)` deletes the first item equal to value (ValueError if absent). `pop(index)` deletes by position AND returns the item (default last). `del lst[i]` deletes by position or slice and returns nothing.

Q3: What is the difference between `sort()` and `sorted()`?
A3: `list.sort()` sorts in place and returns `None`; only works on lists. `sorted(iterable)` returns a new sorted list from any iterable and leaves the original unchanged. Both are stable and use Timsort (O(n log n)) and accept `key=` and `reverse=`.

Q4: What are the time complexities of common list operations?
A4: Index access O(1); `append`/`pop()` O(1) amortized; `insert`, `pop(0)`, `remove`, `in`, `index`, `count` O(n); `sort` O(n log n). For queue behaviour use `collections.deque` where both ends are O(1).

Q5: Is `list.copy()` a deep copy?
A5: No, it is shallow. The outer list is new but inner objects are shared. Use `copy.deepcopy(lst)` for nested structures. `lst[:]` and `list(lst)` are also shallow copies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need an ordered, changeable collection
- Frequent appends at the end and index access
- Small to medium collections you sort or filter

❌ Avoid when:
- You need fast membership checks (`in`): use `set`
- You pop from the front often: use `deque`
- Data should not change: use `tuple`

---

## 📊 Visual Diagram
```
 lst = [10, 20, 30]
        0   1   2

 append(40)     [10, 20, 30, 40]            end, fast
 insert(1, 15)  [10, 15, 20, 30]            shifts right, slow
 pop()          returns 30  -> [10, 20]
 pop(0)         returns 10  -> [20, 30]     shifts left, slow
 remove(20)     [10, 30]                    first match by value
 sort()         ordered in place, returns None
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| In place | Changes the same object | उसी object को बदलना |
| Mutable | Can be changed after creation | बदला जा सकने वाला |
| Stable sort | Equal items keep original order | बराबर items का order नहीं बदलता |
| Shallow copy | Copies outer container only | सिर्फ बाहरी container की copy |
| Amortized O(1) | Fast on average | औसतन तेज़ |
| Timsort | Python's sort algorithm | Python का sort algorithm |

---

## ⚡ 3-Line Summary
English: List methods like append, extend, insert, remove, pop, sort and reverse mutate the list in place and usually return None. Know the cost: end operations are fast, front operations are O(n). Use sorted() for a new list and deque for queues.
Hindi: append, extend, insert, remove, pop, sort, reverse list को वहीं बदलते हैं और आम तौर पर None return करते हैं। अंत वाले operations तेज़ हैं, शुरू वाले O(n)। नई list के लिए sorted() और queue के लिए deque उपयोग करें।

---

## ➡️ Next Topic
**053. List Comprehension** — build and filter lists in one readable line instead of append loops.
