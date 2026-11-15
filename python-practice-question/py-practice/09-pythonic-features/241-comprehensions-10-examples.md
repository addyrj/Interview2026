---

# Q241. Comprehensions — 10 Examples
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐ Easy

---

## ❓ Question
Show 10 useful comprehension patterns: list, filter, if/else, nested, dict, set, generator, flatten, transpose and dict inversion.

---

## 💡 Quick Concept (2 lines only)
A comprehension builds a list/dict/set from an iterable in one expression: `[expr for x in it if cond]`. It is faster and clearer than a loop with `.append()`.
हिंदी: Comprehension = एक line में नई list/dict/set बनाना — loop + append से तेज़ और साफ़।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
nums = [1, 2, 3, 4, 5, 6]                                   # sample data

print([n * n for n in nums])                                # 1. map          -> [1, 4, 9, 16, 25, 36]
print([n for n in nums if n % 2 == 0])                      # 2. filter       -> [2, 4, 6]
print(["even" if n % 2 == 0 else "odd" for n in nums])      # 3. if/else (BEFORE for) -> ['odd', 'even', 'odd', 'even', 'odd', 'even']
print([(x, y) for x in (1, 2) for y in "ab"])               # 4. nested loops -> [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
print({n: n ** 2 for n in nums[:3]})                        # 5. dict comp    -> {1: 1, 2: 4, 3: 9}
print({n % 3 for n in nums})                                # 6. set comp     -> {0, 1, 2}
print(sum(n * n for n in nums))                             # 7. generator expr (no list built) -> 91
matrix = [[1, 2, 3], [4, 5, 6]]                             # sample 2x3 matrix
print([v for row in matrix for v in row])                   # 8. flatten      -> [1, 2, 3, 4, 5, 6]
print([[row[i] for row in matrix] for i in range(3)])       # 9. transpose    -> [[1, 4], [2, 5], [3, 6]]
print({v: k for k, v in {"a": 1, "b": 2}.items()})          # 10. invert dict -> {1: 'a', 2: 'b'}

# ============================================
# TEST CASES
# ============================================
words = ["apple", "Bob", "cat"]                             # sample words
print([w.upper() for w in words if len(w) > 2])             # Expected: ['APPLE', 'BOB', 'CAT']
print([c for c in "hello" if c not in "aeiou"])             # Expected: ['h', 'l', 'l']
print(list(zip(*matrix)))                                   # Expected: [(1, 4), (2, 5), (3, 6)]
```

---

## 🔍 Why This Works (3 lines max)
`if` at the END filters items; `if/else` at the START chooses the value. Loops read left-to-right in the same order as nested `for` statements. Since Python 3, the loop variable does NOT leak out of the comprehension.
हिंदी: सिर्फ `if` आख़िर में (filter), `if/else` शुरू में (value चुनना) — loop variable बाहर leak नहीं होता।

---

## ⚡ Alternative Solution
```python
# Same results with map/filter (less readable) and a generator for big data
nums = [1, 2, 3, 4, 5, 6]                                   # sample data
print(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))  # Expected: [4, 16, 36]
print([n * n for n in nums if n % 2 == 0])                  # Expected: [4, 16, 36] (clearer)

gen = (n * n for n in range(1_000_000))                     # lazy: nothing computed yet
print(next(gen), next(gen))                                 # Expected: 0 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: if/else placed at the end -> SyntaxError
# [n if n > 2 for n in nums else 0]

# ❌ Wrong: comprehension used only for side effects (builds a useless list)
# [print(n) for n in nums]

# ✅ Correct: conditional expression first; plain for-loop for side effects
nums = [1, 2, 3, 4]                                         # sample data
print([n if n > 2 else 0 for n in nums])                    # Expected: [0, 0, 3, 4]
```

---

## 🎯 Interview Tip (1 line)
Say: "I use comprehensions for simple map/filter; once it needs more than two `for`/`if` clauses I switch to a normal loop for readability."

---

## 🔗 Related Questions
→ Q024 (comprehension scope) | Q026 (generator expression laziness) | Q058 (flatten list) | Q254 (generator tricks)
