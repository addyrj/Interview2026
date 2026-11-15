---

# Q290. Avoiding Common Slow Patterns
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Name and fix common slow Python patterns: `list.insert(0, x)` in a loop, `in list` checks, `+=` string building, and manual loops where a built-in exists.

---

## 💡 Quick Concept (2 lines only)
Most slowness is an O(n) operation hidden inside a loop (O(n^2) total). Pick the right data structure or use C-implemented built-ins.
हिंदी: Loop के अंदर छुपा O(n) काम पूरा program O(n²) बना देता है — सही data structure चुनो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit  # timing
from collections import deque  # O(1) at both ends


def insert_front_list() -> list[int]:
    x: list[int] = []  # plain list
    for i in range(20_000):  # loop
        x.insert(0, i)  # O(n) each: shifts every element
    return x  # result


def insert_front_deque() -> list[int]:
    x: deque[int] = deque()  # deque
    for i in range(20_000):  # loop
        x.appendleft(i)  # O(1) each
    return list(x)  # same result as a list


def fast_sum_squares(n: int) -> int:
    return sum(i * i for i in range(n))  # built-in sum, no manual accumulator


# ============================================
# TEST CASES
# ============================================
print(insert_front_list() == insert_front_deque())  # Expected: True
t_list = timeit.timeit(insert_front_list, number=3)  # time list version
t_deque = timeit.timeit(insert_front_deque, number=3)  # time deque version
print(t_deque < t_list)  # Expected: True (list insert(0) is much slower; timings vary)
print(fast_sum_squares(4))  # Expected: 14

data = list(range(5000))  # list of 5000
lookups = list(range(4000, 6000))  # items to check
as_set = set(data)  # set for O(1) lookups
slow = timeit.timeit(lambda: [x in data for x in lookups], number=3)  # O(n) each
fast = timeit.timeit(lambda: [x in as_set for x in lookups], number=3)  # O(1) each
print(fast < slow)  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
`list.insert(0, x)` moves all existing items, so n inserts cost O(n²); a deque links blocks and appends left in O(1). `in list` is a linear scan, `in set` is a hash lookup.
हिंदी: सही structure चुनने से O(n²) सीधे O(n) हो जाता है।

---

## ⚡ Alternative Solution
```python
nums = [1, 2, 3]  # data
print(sum(nums), max(nums), any(n > 2 for n in nums))  # Expected: 6 3 True (C-level built-ins)

parts = ["a", "b", "c"]  # pieces
print("".join(parts))  # Expected: abc (instead of s += p in a loop)

sq = [n * n for n in range(5)]  # comprehension beats append loop
print(sq)  # Expected: [0, 1, 4, 9, 16]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: len() recomputed or list rebuilt inside the loop, repeated 'in list'
# for x in items:
#     if x in seen_list: ...   # O(n) each

# ✅ Correct: use a set for 'seen'
seen: set[int] = set()  # O(1) membership
dupes = [x for x in [1, 2, 1, 3, 2] if x in seen or seen.add(x)]  # add returns None (falsy)
print(dupes)  # Expected: [1, 2]
```

---

## 🎯 Interview Tip (1 line)
Say: "I look for hidden O(n) calls inside loops - insert(0), `in list`, string +=, repeated sorting - and swap in the right structure."

---

## 🔗 Related Questions
→ Q281 (list vs deque vs set) | Q282 (concat vs join) | Q288 (dict/set ops) | Q276 (timeit)
