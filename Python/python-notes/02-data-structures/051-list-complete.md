---

# 051. List — Complete Guide
# हिंदी में: List — पूरी Guide

---

## 🔵 Simple Definition (English)
A Python list is an ordered, mutable, heterogeneous collection. Ordered: elements maintain insertion order, accessible by index. Mutable: elements can be added, removed, or changed after creation. Heterogeneous: can mix types (`[1, "hello", True, None]`). Lists are the most-used data structure in Python — equivalent to JavaScript arrays.

## 🔵 सरल परिभाषा (Hindi)
Python list ordered, mutable, heterogeneous collection है। Ordered: index से access। Mutable: add/remove/change। Heterogeneous: types mix हो सकते हैं। JavaScript array का equivalent।

---

## 💻 Code Example — Basic
```python
# ─── Creating lists ──────────────────────────────────────────────
empty    = []
numbers  = [1, 2, 3, 4, 5]
mixed    = [1, "hello", True, None, 3.14]
nested   = [[1, 2], [3, 4], [5, 6]]
from_range = list(range(1, 6))       # [1, 2, 3, 4, 5]
from_str   = list("Python")          # ['P','y','t','h','o','n']

# ─── Indexing and slicing ─────────────────────────────────────────
nums = [10, 20, 30, 40, 50]
print(nums[0])     # 10  (first)
print(nums[-1])    # 50  (last)
print(nums[-2])    # 40  (second from last)

# Slicing: list[start:stop:step]
print(nums[1:4])   # [20, 30, 40]  (index 1,2,3 — stop is exclusive)
print(nums[:3])    # [10, 20, 30]  (from start to index 3)
print(nums[2:])    # [30, 40, 50]  (from index 2 to end)
print(nums[::-1])  # [50, 40, 30, 20, 10]  (reversed!)
print(nums[::2])   # [10, 30, 50]  (every 2nd element)
copy = nums[:]     # [10, 20, 30, 40, 50]  (shallow copy)

# ─── Core methods ────────────────────────────────────────────────
fruits = ["apple", "mango"]

# Add:
fruits.append("banana")          # add to end → ["apple","mango","banana"]
fruits.insert(1, "grape")        # insert at index → ["apple","grape","mango","banana"]
fruits.extend(["kiwi", "berry"]) # add multiple → appends all items

# Remove:
fruits.remove("grape")           # removes first occurrence of value
popped = fruits.pop()            # removes and returns last item
popped_i = fruits.pop(0)         # removes and returns item at index 0
del fruits[0]                    # delete by index (no return)
fruits.clear()                   # removes all items

# Search:
nums = [10, 20, 30, 20, 40]
print(nums.index(20))    # 1 (first occurrence)
print(nums.count(20))    # 2
print(20 in nums)        # True

# Sort + reverse:
nums = [3, 1, 4, 1, 5, 9, 2, 6]
nums.sort()                   # in-place sort: [1,1,2,3,4,5,6,9]
nums.sort(reverse=True)       # in-place descending
nums.reverse()                # in-place reverse

sorted_copy = sorted(nums)    # returns NEW sorted list (original unchanged)
reversed_copy = list(reversed(nums))  # returns NEW reversed list

# Users sorted by age:
users = [{"name": "Raj", "age": 25}, {"name": "Priya", "age": 22}]
users.sort(key=lambda u: u["age"])        # sort in-place
sorted_u = sorted(users, key=lambda u: u["age"])  # new sorted list

# Info:
print(len(nums))    # length
print(min(nums))    # minimum
print(max(nums))    # maximum
print(sum(nums))    # sum (works on numeric lists)
```

## 💻 Code Example — Advanced
```python
# ─── List comprehension ───────────────────────────────────────────
# [expression for item in iterable if condition]

squares   = [x**2 for x in range(1, 11)]          # [1,4,9,...,100]
evens     = [x for x in range(20) if x % 2 == 0]  # [0,2,4,...,18]
uppercased = [s.upper() for s in ["a","b","c"]]    # ['A','B','C']

# Nested comprehension:
matrix = [[i*j for j in range(1,4)] for i in range(1,4)]
# [[1,2,3],[2,4,6],[3,6,9]]

# Flat list from nested:
nested = [[1,2],[3,4],[5,6]]
flat = [n for row in nested for n in row]   # [1,2,3,4,5,6]

# ─── Copying lists — shallow vs deep ─────────────────────────────
original = [[1, 2], [3, 4]]

# Shallow copy — nested objects still shared:
shallow = original.copy()          # or original[:]  or list(original)
shallow[0].append(99)
print(original)   # [[1,2,99],[3,4]] ← inner list was mutated!

# Deep copy — completely independent:
import copy
deep = copy.deepcopy(original)
deep[0].append(88)
print(original)   # [[1,2,99],[3,4]] ← unchanged!

# ─── Memory-efficient iteration — don't build big lists ──────────
# Wrong — builds 1M item list in memory:
big = [x**2 for x in range(1_000_000)]
# process each one...

# Correct — generator expression (O(1) memory):
big_gen = (x**2 for x in range(1_000_000))   # () not []
for val in big_gen:
    pass   # computed one at a time

# ─── Common patterns ─────────────────────────────────────────────
# Remove duplicates (preserving order — Python 3.7+ dict is ordered):
def deduplicate(lst: list) -> list:
    return list(dict.fromkeys(lst))

print(deduplicate([1, 2, 2, 3, 1, 4]))   # [1, 2, 3, 4]

# Chunk list into batches:
def chunk(lst: list, size: int) -> list[list]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]

print(chunk([1,2,3,4,5,6,7], 3))   # [[1,2,3],[4,5,6],[7]]

# Flatten one level:
from itertools import chain
flat = list(chain.from_iterable([[1,2],[3,4],[5,6]]))  # [1,2,3,4,5,6]

# Zip two lists into dict:
keys   = ["name", "age", "city"]
values = ["Priya", 25, "Mumbai"]
result = dict(zip(keys, values))   # {'name':'Priya','age':25,'city':'Mumbai'}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python list operations:
lst = [1, 2, 3]

lst.append(4)         # → [1,2,3,4]
lst.extend([5,6])     # → [1,2,3,4,5,6]
lst.pop()             # returns 6, list → [1,2,3,4,5]
lst.insert(0, 0)      # → [0,1,2,3,4,5]

# Slice (creates a copy):
sub = lst[1:4]        # [1,2,3]

# Sorted (new list):
nums = [3,1,2]
sorted_nums = sorted(nums)    # [1,2,3], nums unchanged
```

```javascript
// JavaScript array:
let arr = [1, 2, 3];

arr.push(4);              // [1,2,3,4]
arr.push(...[5,6]);       // spread to extend
arr.pop();                // returns 6, arr → [1,2,3,4,5]
arr.unshift(0);           // insert at front

// Slice (creates a copy):
let sub = arr.slice(1,4); // [1,2,3]

// Sort (MUTATES original, converts to string by default!):
let nums = [3,1,2];
nums.sort((a,b) => a-b);  // must provide comparator for numbers!
```

Key differences:
- Python `sort()` mutates, `sorted()` returns new. JS `sort()` always mutates.
- JS `sort()` converts to strings by default — `[10,2,1].sort()` → `[1,10,2]`! Python sorts numerically.
- Python `extend` = JS spread `push(...arr)`. Python `append` = JS `push` (single item).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `append` vs `extend` confusion
```python
lst = [1, 2, 3]

lst.append([4, 5])     # → [1, 2, 3, [4, 5]] ← nested list!
lst.extend([4, 5])     # → [1, 2, 3, 4, 5]   ← flat

# To concatenate, also works (creates new list):
result = [1, 2] + [3, 4]   # [1, 2, 3, 4]
```

❌ Mistake 2: Modifying list while iterating
```python
# Wrong:
for item in my_list:
    if condition(item):
        my_list.remove(item)    # skips next element!

# Correct:
my_list = [item for item in my_list if not condition(item)]
```

---

## 🧠 Tricky Interview Question

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```
Answer: `[1, 2, 3, 4]`. `b = a` doesn't copy — both variables point to the same list object. Use `b = a.copy()` or `b = a[:]` for a shallow copy.

---

## ⚫ Interview Questions + Answers

Q1: What is the time complexity of common list operations?
A1: Append: O(1) amortized. Pop from end: O(1). Insert/delete at arbitrary index: O(n) — shifts all elements. Index access: O(1). `in` operator: O(n) — linear scan. Sort: O(n log n) — Timsort. `len()`: O(1) — stored separately.

Q2: What is the difference between `list.sort()` and `sorted()`?
A2: `list.sort()` sorts in-place (modifies the original list), returns `None`. `sorted(iterable)` returns a new sorted list (original unchanged), works on any iterable (tuple, generator, dict keys). Prefer `sorted()` when you need the original preserved. Both accept `key` and `reverse` params. Both use Timsort: O(n log n), stable (equal elements maintain relative order).

Q3: What is a shallow copy vs deep copy for lists?
A3: Shallow copy (`lst.copy()`, `lst[:]`, `list(lst)`): creates a new list object, but nested objects (inner lists, dicts) still reference the same objects. Mutating a nested object affects both copies. Deep copy (`copy.deepcopy(lst)`): recursively copies all nested objects — completely independent. Use deep copy when working with nested structures that you need to modify independently.

Q4: How do you efficiently check if an element exists in a list?
A4: `item in my_list` — O(n) linear scan. For frequent lookups, convert to a set: `item in set(my_list)` — O(1) average. Trade-off: converting costs O(n) time and memory. If you're doing many lookups on the same data, maintaining a set alongside the list is efficient. For sorted lists, use `bisect.bisect_left` for O(log n) binary search.

Q5: What is list unpacking and how do you use `*` in it?
A5: `a, b, c = [1, 2, 3]` unpacks exactly 3 elements. `first, *rest = [1, 2, 3, 4, 5]` — `first=1`, `rest=[2,3,4,5]`. `*start, last = [1,2,3,4,5]` — `start=[1,2,3,4]`, `last=5`. `a, *_, b = [1,2,3,4,5]` — `a=1`, `_=[2,3,4]`, `b=5` (discard middle with `_`). Also used for function calls: `func(*lst)` unpacks list as positional args.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mutable | Can be changed after creation | Create होने के बाद बदल सकते हैं |
| Slice | Subset via start:stop:step | list का हिस्सा लेना |
| Comprehension | One-line loop to build list | One-line loop से list बनाना |
| append | Add one item to end | End में एक item add करो |
| extend | Add multiple items to end | End में multiple items add करो |
| Shallow copy | Copy structure, not nested objects | Structure copy, nested share |
| Deep copy | Fully independent copy | पूरी तरह independent copy |

---

## ⚡ 3-Line Summary
English: Lists are ordered, mutable, 0-indexed sequences. Use `append` for one item, `extend` for multiple, `pop` to remove from end. List comprehensions `[expr for x in iterable if cond]` are preferred over manual loops; use generator expressions `(expr...)` when memory matters.
Hindi: Lists ordered, mutable, 0-indexed sequences हैं। `append` = एक item, `extend` = multiple। Comprehensions preferred over loops; memory के लिए generator expression।

---

## ➡️ Next Topic
**052. List Methods Deep Dive** — all methods with time complexity. **053. List Comprehension** — nested, conditions, walrus operator.
