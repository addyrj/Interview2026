---

# Q250. itertools — 10 Examples
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 10 `itertools` tools: `count`, `cycle`, `chain`, `islice`, `product`, `permutations`, `combinations`, `groupby`, `accumulate`, `pairwise` (and `batched` in 3.12+).

---

## 💡 Quick Concept (2 lines only)
`itertools` gives memory-efficient, LAZY iterator building blocks. They return iterators, so wrap in `list()` to see values.
हिंदी: itertools = lazy iterator tools — memory कम लगती है, देखने के लिए `list()` में लपेटो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import itertools as it                                # Step 1: import with short alias

print(list(it.islice(it.count(10, 5), 3)))            # 1. count (infinite) + islice -> [10, 15, 20]
print(list(it.islice(it.cycle("AB"), 5)))             # 2. cycle repeats forever     -> ['A', 'B', 'A', 'B', 'A']
print(list(it.chain([1, 2], (3,), "ab")))             # 3. chain joins iterables     -> [1, 2, 3, 'a', 'b']
print(list(it.islice(range(100), 2, 8, 2)))           # 4. slice any iterable        -> [2, 4, 6]
print(list(it.product("AB", [1, 2])))                 # 5. cartesian product         -> [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
print(list(it.permutations([1, 2, 3], 2)))            # 6. ordered pairs             -> [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
print(list(it.combinations([1, 2, 3], 2)))            # 7. unordered pairs           -> [(1, 2), (1, 3), (2, 3)]

data = sorted(["apple", "avocado", "banana", "blueberry", "cherry"])  # groupby needs SORTED input
print({k: list(g) for k, g in it.groupby(data, key=lambda s: s[0])})  # 8. group by first letter
# -> {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}

print(list(it.accumulate([1, 2, 3, 4])))              # 9. running total             -> [1, 3, 6, 10]
print(list(it.pairwise([1, 4, 9, 16])))               # 10. adjacent pairs (3.10+)   -> [(1, 4), (4, 9), (9, 16)]

# ============================================
# TEST CASES
# ============================================
print(list(it.batched(range(7), 3)))                  # Expected: [(0, 1, 2), (3, 4, 5), (6,)] (3.12+)
print(list(it.zip_longest([1, 2, 3], "a", fillvalue="-")))  # Expected: [(1, 'a'), (2, '-'), (3, '-')]
print(list(it.starmap(pow, [(2, 3), (3, 2)])))        # Expected: [8, 9]
print(list(it.takewhile(lambda x: x < 3, [1, 2, 5, 1])))  # Expected: [1, 2] (stops at first failure)
```

---

## 🔍 Why This Works (3 lines max)
Each function returns a lazy iterator, so infinite sources like `count`/`cycle` are safe when paired with `islice`. `groupby` only groups CONSECUTIVE equal keys, which is why the data is sorted first.
हिंदी: सब lazy हैं — `groupby` सिर्फ लगातार वाले keys group करता है, इसलिए पहले sort करो।

---

## ⚡ Alternative Solution
```python
# Pure-Python equivalents show what the tools save you
import itertools                                      # stdlib module
pairs = [(a, b) for a in "AB" for b in (1, 2)]        # nested comprehension = product
print(pairs == list(itertools.product("AB", (1, 2)))) # Expected: True

total = 0                                             # manual running total
running = []                                          # result list
for n in [1, 2, 3, 4]:                                # loop
    total += n                                        # add
    running.append(total)                             # collect
print(running)                                        # Expected: [1, 3, 6, 10] (same as accumulate)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: groupby on UNSORTED data -> duplicate groups
import itertools                                      # import
print([(k, len(list(g))) for k, g in itertools.groupby("aabaa")])  # Expected: [('a', 2), ('b', 1), ('a', 2)]

# ✅ Correct: sort first
print([(k, len(list(g))) for k, g in itertools.groupby(sorted("aabaa"))])  # Expected: [('a', 4), ('b', 1)]
```

---

## 🎯 Interview Tip (1 line)
Say: "itertools is lazy and memory-efficient; remember `groupby` needs sorted input, `islice` tames infinite iterators, and `batched`/`pairwise` are built-in now."

---

## 🔗 Related Questions
→ Q114 (implement itertools.chain) | Q115 (implement itertools.groupby) | Q254 (generator tricks) | Q025 (generator exhaustion)
