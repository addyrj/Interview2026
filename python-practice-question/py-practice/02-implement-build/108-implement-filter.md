---

# Q108. Implement filter()
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `my_filter(fn, iterable)` like the built-in `filter`: lazy, keeps items for which `fn(item)` is truthy, and when `fn` is `None` it keeps truthy items.

```python
list(my_filter(lambda x: x % 2 == 0, range(10)))   # [0, 2, 4, 6, 8]
```

---

## 💡 Quick Concept (2 lines only)
`filter` yields only the items where the predicate is truthy. Note: it uses truthiness, not `is True`, and `None` as predicate means "drop falsy values".
हिंदी: filter सिर्फ वही items देता है जिनके लिए predicate truthy हो; fn=None हो तो falsy items हट जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable, Iterable, Iterator, TypeVar  # type hints

T = TypeVar("T")  # item type

def my_filter(fn: Callable[[T], object] | None, iterable: Iterable[T]) -> Iterator[T]:  # lazy filter
    for item in iterable:  # Step 1: walk the input
        if (item if fn is None else fn(item)):  # Step 2: truthiness of item or fn(item)
            yield item  # Step 3: yield the ORIGINAL item (not fn's result)

# ============================================
# TEST CASES
# ============================================
print(list(my_filter(lambda x: x % 2 == 0, range(10))))  # Expected: [0, 2, 4, 6, 8]
print(list(my_filter(None, [0, 1, "", "a", None, [], [0]])))  # Expected: [1, 'a', [0]]
print(list(my_filter(str.isalpha, "a1b2")))  # Expected: ['a', 'b']
print(list(my_filter(lambda x: True, [])))  # Expected: []
print(list(filter(None, [0, 1, "", "a"])))  # Expected: [1, 'a']  (built-in, same)
print([x for x in range(10) if x % 2 == 0])  # Expected: [0, 2, 4, 6, 8]  (comprehension equivalent)
print(list(my_filter(lambda x: x > 0, (n for n in [-1, 2, -3, 4]))))  # Expected: [2, 4]  (works on generators)
```

---

## 🔍 Why This Works (3 lines max)
`if` tests truthiness, exactly like the built-in. We yield the original item, so the predicate's return value is only used to decide, never to transform.
हिंदी: `if` truthiness देखता है, और हम predicate का result नहीं बल्कि original item yield करते हैं।

---

## ⚡ Alternative Solution
```python
# Opposite helper from the stdlib
import itertools  # filterfalse keeps items where predicate is FALSY
print(list(itertools.filterfalse(lambda x: x % 2, range(6))))  # Expected: [0, 2, 4]

# One-liner generator expression (when fn is not None)
def alt(fn, it):
    return (x for x in it if fn(x))  # lazy and readable
print(list(alt(lambda x: x > 1, [1, 2, 3])))  # Expected: [2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `is True` only accepts the literal True, so truthy values like 1 are rejected
def bad(fn, it):
    return [x for x in it if fn(x) is True]
print(bad(lambda x: x % 2, [1, 2, 3]))  # Output: []  (x % 2 returns 1, not True)

# ✅ Correct: rely on truthiness
print(list(my_filter(lambda x: x % 2, [1, 2, 3])))  # Output: [1, 3]
```

---

## 🎯 Interview Tip (1 line)
Say: "filter is lazy and uses truthiness; filter(None, xs) drops falsy values — and I would usually write a comprehension instead."

---

## 🔗 Related Questions
→ Q107 (map) | Q109 (reduce) | Q068 (remove falsy values) | Q303 (comprehension vs map/filter)
