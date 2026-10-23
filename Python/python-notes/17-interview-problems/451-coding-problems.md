---

# 451. Python Coding Problems — Complete Interview Guide
# हिंदी में: Python Coding Problems — Interview Guide

---

## 🔵 Overview
Top Python coding problems asked in interviews. These test: string manipulation, data structures, algorithms, and Pythonic solutions. Always think about: time complexity, space complexity, edge cases, and Pythonic alternatives to brute force.

---

## 📚 Problem 1: Reverse a String
```python
# Multiple approaches:
s = "Hello, World!"

# 1. Slice (most Pythonic):
reversed_s = s[::-1]   # "!dlroW ,olleH"

# 2. reversed() + join:
reversed_s = "".join(reversed(s))

# 3. Manual loop (for learning):
def reverse_string(s: str) -> str:
    result = []
    for i in range(len(s) - 1, -1, -1):
        result.append(s[i])
    return "".join(result)

# Time: O(n), Space: O(n)
```

---

## 📚 Problem 2: Check Palindrome
```python
def is_palindrome(s: str) -> bool:
    """Check if string is a palindrome (ignoring case and non-alphanumeric)."""
    # Clean string: lowercase, alphanumeric only
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

# Test:
print(is_palindrome("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("race a car"))                        # False

# Two-pointer approach (O(1) space):
def is_palindrome_two_pointer(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]
    left, right = 0, len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True
# Time: O(n), Space: O(n) for cleaned
```

---

## 📚 Problem 3: FizzBuzz
```python
# Classic with Pythonic twist:
def fizzbuzz(n: int) -> list[str]:
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:       # check 15 first!
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

# One-liner (Pythonic but less readable):
print([
    "FizzBuzz" if i % 15 == 0 else
    "Fizz" if i % 3 == 0 else
    "Buzz" if i % 5 == 0 else
    str(i)
    for i in range(1, 101)
])
```

---

## 📚 Problem 4: Two Sum
```python
from typing import Optional

def two_sum(nums: list[int], target: int) -> Optional[tuple[int, int]]:
    """Return indices of two numbers that add up to target."""
    seen = {}   # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return None

# Test:
print(two_sum([2, 7, 11, 15], 9))   # (0, 1) — 2+7=9

# Time: O(n), Space: O(n)
# Brute force: O(n²) — two nested loops, never use this
```

---

## 📚 Problem 5: Fibonacci (multiple ways)
```python
# 1. Recursive (elegant but O(2^n) — terrible):
def fib_recursive(n: int) -> int:
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

# 2. With memoization (O(n) time, O(n) space):
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n-1) + fib_memo(n-2)

# 3. Bottom-up DP (O(n) time, O(1) space — best):
def fib_dp(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# 4. Generator (lazy, infinite):
def fibonacci_gen():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Get first 10:
fib = fibonacci_gen()
first_10 = [next(fib) for _ in range(10)]
print(first_10)   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 📚 Problem 6: Find Duplicates
```python
from collections import Counter

def find_duplicates(lst: list) -> list:
    """Return elements that appear more than once."""
    count = Counter(lst)
    return [item for item, cnt in count.items() if cnt > 1]

# Alternative — O(n) with set:
def find_duplicates_set(lst: list) -> list:
    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

print(find_duplicates([1, 2, 3, 2, 4, 3, 5]))   # [2, 3]
```

---

## 📚 Problem 7: Anagram Check
```python
from collections import Counter

def are_anagrams(s1: str, s2: str) -> bool:
    """Check if two strings are anagrams."""
    return Counter(s1.lower()) == Counter(s2.lower())

# Alternative — sorted:
def are_anagrams_sorted(s1: str, s2: str) -> bool:
    return sorted(s1.lower()) == sorted(s2.lower())   # O(n log n)

print(are_anagrams("listen", "silent"))   # True
print(are_anagrams("hello", "world"))     # False
```

---

## 📚 Problem 8: LRU Cache
```python
from collections import OrderedDict
from typing import Optional

class LRUCache:
    """Least Recently Used cache with O(1) get and put."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()  # insertion-ordered dict
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # mark as recently used
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # remove least recently used (first item)

# Test:
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))    # 1
cache.put(3, 3)        # evicts key 2 (least recently used)
print(cache.get(2))    # -1 (evicted)
print(cache.get(3))    # 3

# Python has built-in: @functools.lru_cache(maxsize=128)
```

---

## 📚 Problem 9: Flatten Nested List
```python
from typing import Any

def flatten(lst: list) -> list:
    """Flatten arbitrarily nested list."""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))   # recurse
        else:
            result.append(item)
    return result

print(flatten([1, [2, 3], [4, [5, 6]], 7]))   # [1, 2, 3, 4, 5, 6, 7]

# Generator version (memory efficient):
def flatten_gen(lst: list):
    for item in lst:
        if isinstance(item, list):
            yield from flatten_gen(item)   # delegate to sub-generator
        else:
            yield item

# itertools approach (one level only):
from itertools import chain
one_level = list(chain.from_iterable([[1,2],[3,4],[5,6]]))  # [1,2,3,4,5,6]
```

---

## 📚 Problem 10: Group Anagrams
```python
from collections import defaultdict

def group_anagrams(words: list[str]) -> list[list[str]]:
    """Group words that are anagrams of each other."""
    groups = defaultdict(list)
    for word in words:
        key = tuple(sorted(word))   # canonical form
        groups[key].append(word)
    return list(groups.values())

print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))
# [["eat","tea","ate"],["tan","nat"],["bat"]]
# Time: O(n × k log k) where k = max word length
```

---

## 📚 Problem 11: Valid Parentheses
```python
def is_valid_parens(s: str) -> bool:
    """Check if brackets are balanced."""
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
    
    return len(stack) == 0

print(is_valid_parens("()[]{}"))   # True
print(is_valid_parens("([)]"))     # False
print(is_valid_parens("{[]}"))     # True
```

---

## 📚 Problem 12: Find Most Common Element
```python
from collections import Counter

def most_common(lst: list) -> any:
    """Return the most frequently occurring element."""
    return Counter(lst).most_common(1)[0][0]

print(most_common([1, 2, 3, 2, 4, 2, 5]))   # 2

# Top k most common:
def top_k_common(lst: list, k: int) -> list:
    return [item for item, count in Counter(lst).most_common(k)]

print(top_k_common([1,1,2,2,2,3], 2))   # [2, 1]
```

---

## 📚 Problem 13: Binary Search
```python
def binary_search(arr: list[int], target: int) -> int:
    """Return index of target in sorted array, or -1."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2   # avoid overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

print(binary_search([1, 3, 5, 7, 9, 11], 7))   # 3
print(binary_search([1, 3, 5, 7, 9, 11], 4))   # -1
# Time: O(log n), Space: O(1)

# Python built-in:
import bisect
arr = [1, 3, 5, 7, 9]
idx = bisect.bisect_left(arr, 5)   # returns 2
```

---

## 📚 Problem 14: Build REST API (FastAPI)
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

# In-memory store (replace with DB in production):
items_db: dict[str, dict] = {}

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: str
    name: str
    price: float
    description: Optional[str] = None

@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    item_id = str(uuid.uuid4())
    item_data = {"id": item_id, **item.model_dump()}
    items_db[item_id] = item_data
    return item_data

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item

@app.get("/items", response_model=list[ItemResponse])
async def list_items(skip: int = 0, limit: int = 10) -> list[ItemResponse]:
    items = list(items_db.values())
    return items[skip: skip + limit]

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemCreate) -> ItemResponse:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = {"id": item_id, **item.model_dump()}
    items_db[item_id] = item_data
    return item_data

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
```

---

## ⚡ Problem Quick Reference

| Problem | Key Data Structure | Time | Space |
|---------|-------------------|------|-------|
| Two Sum | Hash map | O(n) | O(n) |
| Palindrome | Two pointers | O(n) | O(1) |
| LRU Cache | OrderedDict | O(1) | O(capacity) |
| Group Anagrams | defaultdict + sorted | O(nk log k) | O(nk) |
| Valid Parens | Stack | O(n) | O(n) |
| Binary Search | - | O(log n) | O(1) |
| Fibonacci | Variables | O(n) | O(1) |

---

## 🧠 Tips for Python Interviews

1. **Always ask**: "Can I use built-ins?" — `Counter`, `defaultdict`, `sorted()`, `zip()`, `enumerate()`
2. **Know these**: `sorted(lst, key=lambda x: x[1])`, `zip(*matrix)` for transpose
3. **Pythonic over verbose**: `[x for x in lst if x > 0]` vs explicit loops
4. **Edge cases**: empty input, single element, all duplicates, negative numbers
5. **State your complexity**: "This is O(n) time and O(n) space"
6. **Type hints**: shows Python expertise — `def func(lst: list[int]) -> int:`

---

## ➡️ Next Topic
**452. System Design — Rate Limiter** — sliding window, token bucket. **453. Build Auth System** — JWT + refresh tokens in FastAPI. **500. Interview Tips** — preparation strategy.
