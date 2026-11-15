---

# Q303. Comprehension vs map/filter
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
Square the even numbers of a list using (a) a list comprehension and (b) `map`/`filter`. Which is preferred and why?

---

## 💡 Quick Concept (2 lines only)
Both transform/filter iterables. Comprehensions are more readable and return a list; `map`/`filter` return lazy iterators and shine with existing named functions.
हिंदी: Comprehension ज़्यादा readable है; map/filter lazy iterator देते हैं (list नहीं)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
nums = [1, 2, 3, 4, 5, 6]  # input data

comp = [n * n for n in nums if n % 2 == 0]  # Step 1: comprehension -> list
mf = map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))  # Step 2: lazy map/filter chain

# ============================================
# TEST CASES
# ============================================
print(comp)  # Expected: [4, 16, 36]
print(type(mf).__name__)  # Expected: map  (lazy, nothing computed yet)
print(list(mf))  # Expected: [4, 16, 36]
print(list(mf))  # Expected: []  (iterator is exhausted)

print(list(map(str, nums)))  # Expected: ['1', '2', '3', '4', '5', '6'] (map shines with a built-in)
print(list(map(lambda a, b: a + b, [1, 2], [10, 20])))  # Expected: [11, 22] (map over 2 iterables)
print(list(filter(None, [0, 1, "", "a", None])))  # Expected: [1, 'a'] (filter(None) drops falsy)
```

---

## 🔍 Why This Works (3 lines max)
A comprehension is one readable expression and builds a list immediately. `map`/`filter` return one-shot iterators, so you must wrap them in `list()` and can't reuse them. Python style (PEP 8 culture) prefers comprehensions over `lambda` chains.
हिंदी: Lambda chain से comprehension साफ़ पढ़ी जाती है — इसलिए वही preferred है।

---

## ⚡ Alternative Solution
```python
import timeit  # speed comparison

nums = list(range(1000))  # data
t_comp = timeit.timeit(lambda: [n * 2 for n in nums], number=2000)  # comprehension
t_map_lambda = timeit.timeit(lambda: list(map(lambda n: n * 2, nums)), number=2000)  # map + lambda
print(t_comp < t_map_lambda)  # Expected: True (lambda call overhead; timings vary)

gen = (n * 2 for n in nums)  # generator expression = lazy comprehension
print(next(gen), next(gen))  # Expected: 0 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting map() to be a list
result = map(str, [1, 2, 3])  # iterator
print(len(list(result)), list(result))  # 3 [] -> second use is empty

# ✅ Correct: materialize once, or use a comprehension
result = [str(n) for n in [1, 2, 3]]  # list, reusable
print(result, result)  # Expected: ['1', '2', '3'] ['1', '2', '3']
```

---

## 🎯 Interview Tip (1 line)
Say: "Comprehension for readability; map(builtin, data) is fine and lazy; both beat manual append loops."

---

## 🔗 Related Questions
→ Q107 (implement map) | Q108 (implement filter) | Q241 (comprehensions) | Q279 (generators vs lists)
