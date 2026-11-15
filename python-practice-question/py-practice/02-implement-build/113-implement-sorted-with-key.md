---

# Q113. Implement sorted() with key
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `my_sorted(iterable, key=None, reverse=False)` that behaves like built-in `sorted()`: returns a NEW list, calls `key` once per element, and is **stable** (equal keys keep original order). Do not use `sorted()` / `list.sort()`.

```python
my_sorted(["banana", "kiwi", "apple", "fig", "cherry"], key=len)
# ['fig', 'kiwi', 'apple', 'banana', 'cherry']
```

---

## 💡 Quick Concept (2 lines only)
Decorate each item with its key, merge-sort on the key only (stable), then strip the keys off (decorate-sort-undecorate).
हिंदी: पहले हर item के साथ key जोड़ो, key पर stable sort करो, फिर key हटा दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any, Callable, Iterable            # type hints

def my_sorted(iterable: Iterable, key: Callable[[Any], Any] | None = None, reverse: bool = False) -> list:
    items = list(iterable)                        # Step 1: copy input, never mutate original
    keys = [key(x) if key else x for x in items]  # Step 2: call key() exactly once per element
    pairs = list(zip(keys, items))                # Step 3: decorate -> (key, value)

    def before(a: Any, b: Any) -> bool:           # should b jump ahead of a?
        return b > a if reverse else b < a        # strict comparison keeps sort stable

    def merge_sort(arr: list) -> list:            # Step 4: stable merge sort on pairs
        if len(arr) <= 1:                         # base case
            return arr                            # already sorted
        mid = len(arr) // 2                       # split point
        left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])  # sort halves
        out, i, j = [], 0, 0                      # merge state
        while i < len(left) and j < len(right):   # both halves have items
            if before(left[i][0], right[j][0]):   # right strictly earlier?
                out.append(right[j]); j += 1      # take right
            else:
                out.append(left[i]); i += 1       # ties go left -> stable
        return out + left[i:] + right[j:]         # append leftovers

    return [v for _, v in merge_sort(pairs)]      # Step 5: undecorate

# ============================================
# TEST CASES
# ============================================
words = ["banana", "kiwi", "apple", "fig", "cherry"]
people = [("Ann", 30), ("Bob", 25), ("Cy", 30)]
print(my_sorted([3, 1, 2]))                                      # Expected: [1, 2, 3]
print(my_sorted(words, key=len))                                 # Expected: ['fig', 'kiwi', 'apple', 'banana', 'cherry']
print(my_sorted(words, key=len, reverse=True))                   # Expected: ['banana', 'cherry', 'apple', 'kiwi', 'fig']
print(my_sorted("hello"))                                        # Expected: ['e', 'h', 'l', 'l', 'o']
print(my_sorted(people, key=lambda p: p[1]))                     # Expected: [('Bob', 25), ('Ann', 30), ('Cy', 30)]
print(my_sorted(people, key=lambda p: p[1], reverse=True))       # Expected: [('Ann', 30), ('Cy', 30), ('Bob', 25)]  (Ann before Cy: stable, same as sorted())
print(my_sorted([]))                                             # Expected: []
assert my_sorted(words, key=len) == sorted(words, key=len)       # matches built-in
```

---

## 🔍 Why This Works (3 lines max)
Computing keys once (like CPython) avoids repeated key() calls, and merging with a strict `<` takes from the left on ties, so equal keys keep their input order. Sorting only the key means values never need to be comparable.
हिंदी: key सिर्फ एक बार निकलती है और tie पर left वाला पहले आता है, इसलिए sort stable रहता है।

---

## ⚡ Alternative Solution
```python
# Different approach: heap with an index tiebreaker (also stable, O(n log n))
import heapq                                                  # heap module

def sorted_heap(iterable, key=None):
    items = list(iterable)                                    # copy input
    decorated = [((key(x) if key else x), i, x) for i, x in enumerate(items)]  # index i breaks ties
    heapq.heapify(decorated)                                  # O(n) heap build
    return [heapq.heappop(decorated)[2] for _ in range(len(decorated))]  # pop smallest first

print(sorted_heap(["banana", "kiwi", "apple", "fig", "cherry"], key=len))
# Output: ['fig', 'kiwi', 'apple', 'banana', 'cherry']
print(sorted_heap([("Ann", 30), ("Bob", 25), ("Cy", 30)], key=lambda p: p[1]))
# Output: [('Bob', 25), ('Ann', 30), ('Cy', 30)]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: decorating without a tiebreaker -> Python compares the VALUES when keys tie
# sorted([(1, {"a": 1}), (1, {"a": 2})])
# TypeError: '<' not supported between instances of 'dict' and 'dict'   (verified)

# ✅ Correct: sort on the key only (or add an index tiebreaker like in the heap version)
# Also remember: key() is called once per item, in input order:
calls = []                                    # record key calls
def k(x):
    calls.append(x); return x                 # log and return
sorted([3, 1, 2], key=k)                      # built-in behaviour
print(calls)                                  # Output: [3, 1, 2]  (one call per element)
```

---

## 🎯 Interview Tip (1 line)
Say: "Decorate-sort-undecorate, key computed once per element, merge sort for stability (Timsort in CPython), O(n log n) time and O(n) space."

---

## 🔗 Related Questions
→ Q106 (merge sort) | Q105 (quick sort) | Q065 (sort list of dicts) | Q258 (sorted() key tricks)
