---

# Q048. enumerate and reversed Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
s = ["a", "b", "c"]

print(list(enumerate(s, start=1)))
print(list(reversed(s)))
print(list(enumerate(reversed(s))))
print(list(reversed(list(enumerate(s)))))

try:
    reversed(enumerate(s))
except TypeError as e:
    print("TypeError:", e)

r = reversed(s)
print(list(r), list(r))
```

---

## 💡 Quick Concept (2 lines only)
`enumerate` yields `(index, item)` pairs lazily; `reversed` needs a sequence (`__reversed__` or `__len__` + `__getitem__`) and returns a one-shot iterator.
हिंदी: `enumerate` और `reversed` दोनों lazy iterators हैं; `reversed` सिर्फ sequence पर चलता है, iterator पर नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
s = ["a", "b", "c"]                           # a plain list (a sequence)

print(list(enumerate(s, start=1)))            # Step 1: indices start at 1

print(list(reversed(s)))                      # Step 2: reverse iterator over the list

print(list(enumerate(reversed(s))))           # Step 3: index counts the NEW order (0 is 'c')

print(list(reversed(list(enumerate(s)))))     # Step 4: keep ORIGINAL indexes, reversed order

try:
    reversed(enumerate(s))                    # Step 5: enumerate object is not a sequence
except TypeError as e:
    print("TypeError:", e)                    # cannot reverse an iterator

r = reversed(s)                               # Step 6: reversed() returns a one-shot iterator
print(list(r), list(r))                       # second list() is empty: already exhausted

n = len(s)                                    # keep original indexes without building a list
print([(n - 1 - i, v) for i, v in enumerate(reversed(s))])  # same as Step 4

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# [(1, 'a'), (2, 'b'), (3, 'c')]
# ['c', 'b', 'a']
# [(0, 'c'), (1, 'b'), (2, 'a')]
# [(2, 'c'), (1, 'b'), (0, 'a')]
# TypeError: 'enumerate' object is not reversible
# ['c', 'b', 'a'] []
# [(2, 'c'), (1, 'b'), (0, 'a')]
```

---

## 🔍 Why This Works (3 lines max)
`enumerate(reversed(s))` numbers items in the new order, while `reversed(list(enumerate(s)))` keeps the original index with each item. `reversed()` raises `TypeError` for sets and iterators, and dicts are reversible only since 3.8 (by key insertion order).
हिंदी: `enumerate(reversed(s))` नए order में गिनता है, `reversed(list(enumerate(s)))` पुराने index रखता है।

---

## ⚡ Alternative Solution
```python
print(list(reversed("abc")), list(reversed(range(3))))  # str/range are sequences
# Output: ['c', 'b', 'a'] [2, 1, 0]

try:
    reversed({1, 2})                          # set has no order/index
except TypeError as e:
    print("TypeError:", e)                    # Output: TypeError: 'set' object is not reversible

print(list(reversed({"a": 1, "b": 2})))       # dict reversible since 3.8 -> Output: ['b', 'a']

e = enumerate("xy")                           # one-shot iterator
print(next(e), next(e))                       # Output: (0, 'x') (1, 'y')
# next(e) now raises StopIteration
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: manual index counter or range(len()) loops
items = ["a", "b", "c"]
i = 0
for x in items:
    print(i, x)
    i += 1                                    # easy to forget/misplace

# ✅ Correct: let enumerate do it (and reversed for backwards)
for i, x in enumerate(items):
    print(i, x)                               # Output: 0 a / 1 b / 2 c
```

---

## 🎯 Interview Tip (1 line)
Say: "Use `enumerate` instead of `range(len(x))`; `reversed()` works on sequences and returns an iterator that can be consumed only once."

---

## 🔗 Related Questions
→ Q047 (zip unequal lengths) | Q111 (implement enumerate) | Q171 (iterators vs iterables) | Q297 (generators vs iterators)
