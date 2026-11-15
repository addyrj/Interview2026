---

# Q288. Efficient Dict/Set Operations
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Count word frequencies and test membership efficiently. Compare manual dict counting, `defaultdict`, `Counter`, and `in list` vs `in set`.

---

## 💡 Quick Concept (2 lines only)
Dict/set lookups are O(1) average (hashing); list lookups are O(n). Built-in tools like `Counter` run the loop in C.
हिंदी: Dict/set में lookup O(1) है, list में O(n) — और Counter जैसे built-ins C में चलते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit  # timing
from collections import Counter, defaultdict  # efficient counters

words = ["a", "b", "a", "c"] * 50_000  # 200k words


def manual() -> dict[str, int]:
    d: dict[str, int] = {}  # plain dict
    for w in words:  # loop in Python
        if w in d:  # check key
            d[w] += 1  # increment
        else:
            d[w] = 1  # first time
    return d  # result


def with_defaultdict() -> dict[str, int]:
    d: defaultdict[str, int] = defaultdict(int)  # missing key -> 0
    for w in words:  # still a Python loop
        d[w] += 1  # no key check needed
    return d  # result


def with_counter() -> Counter[str]:
    return Counter(words)  # counting loop runs in C


# ============================================
# TEST CASES
# ============================================
print(dict(with_counter()))  # Expected: {'a': 100000, 'b': 50000, 'c': 50000}
print(manual() == dict(with_defaultdict()) == dict(with_counter()))  # Expected: True
for f in (manual, with_defaultdict, with_counter):  # time each
    print(f.__name__, round(timeit.timeit(f, number=10), 3))  # Expected order: manual > defaultdict > Counter (times vary)

lst = list(range(10_000))  # list data
st = set(lst)  # set data
print(timeit.timeit(lambda: 9999 in lst, number=1000) > timeit.timeit(lambda: 9999 in st, number=1000))  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
`manual` hashes each key twice (check and write); `defaultdict` once; `Counter` uses a C helper. A set hashes the item and jumps to its bucket, while a list scans up to n items.
हिंदी: Hash से सीधे bucket पर पहुँचते हैं, list में एक-एक करके ढूँढना पड़ता है।

---

## ⚡ Alternative Solution
```python
a = {1, 2, 3, 4}  # set a
b = {3, 4, 5}  # set b
print(a & b, a | b, a - b)  # Expected: {3, 4} {1, 2, 3, 4, 5} {1, 2}  (set ops run in C)

d: dict[str, int] = {}  # plain dict
d.setdefault("x", 0)  # insert only if missing
d["x"] += 1  # then update
print(d.get("missing", -1), d)  # Expected: -1 {'x': 1}

print(list(dict.fromkeys([3, 1, 3, 2, 1])))  # Expected: [3, 1, 2] (order-preserving dedupe)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: membership test on a list inside a loop -> O(n*m)
# for x in big_a:
#     if x in big_list_b: ...

# ✅ Correct: convert once to a set -> O(n + m)
big_b = set(range(1000))  # build set once
print(sum(1 for x in range(2000) if x in big_b))  # Expected: 1000
```

---

## 🎯 Interview Tip (1 line)
Say: "Dict/set give O(1) average lookups; I convert to a set before repeated membership checks and use Counter/defaultdict for counting."

---

## 🔗 Related Questions
→ Q281 (list vs deque vs set) | Q066 (count occurrences) | Q055 (dedupe keep order) | Q013 (set operations)
