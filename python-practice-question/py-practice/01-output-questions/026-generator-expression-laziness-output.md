---

# Q026. Generator expression laziness output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
def noisy(n):
    print("compute", n)           # visible side effect
    return n * n

ge = (noisy(i) for i in range(3))
print("created")                  # (a)
print(next(ge))                   # (b)
print("after first")
print(list(ge))                   # (c)

lc = [noisy(i) for i in range(2)]
print("lc done")                  # (d)

n = 3
ge2 = (i * n for i in range(2))
n = 10
print(list(ge2))                  # (e)
```

---

## 💡 Quick Concept (2 lines only)
A generator expression computes values only when asked (lazy); a list comprehension computes everything immediately. The outermost iterable is evaluated at creation, everything else at consumption time.
हिंदी: Generator expression आलसी है — `next()` माँगने पर ही काम करता है; list comprehension तुरंत सब कर देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def noisy(n: int) -> int:                 # Step 1: function that logs each call
    print("compute", n)                   # Shows WHEN it runs
    return n * n                          # Square

ge = (noisy(i) for i in range(3))         # Step 2: nothing computed yet
print("created")                          # (a) created
print(next(ge))                           # (b) compute 0, then 0
print("after first")                      # after first
print(list(ge))                           # (c) compute 1, compute 2, then [1, 4]

lc = [noisy(i) for i in range(2)]         # Step 3: list comp runs everything NOW
print("lc done")                          # (d) compute 0, compute 1, then lc done

n = 3                                     # Step 4: late evaluation of free variables
ge2 = (i * n for i in range(2))           # `n` is NOT read yet (only range(2) is)
n = 10                                    # Changed before consumption
print(list(ge2))                          # (e) [0, 10]

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# created
# compute 0
# 0
# after first
# compute 1
# compute 2
# [1, 4]
# compute 0
# compute 1
# lc done
# [0, 10]
```

---

## 🔍 Why This Works (3 lines max)
Calling `next()` resumes the generator until the next yield, so work is interleaved with the consumer. Only the first `for` iterable is evaluated eagerly; `n` is looked up on each step, so it sees the latest value (10).
हिंदी: Memory भी बचती है — million items की जगह एक बार में एक ही item बनता है।

---

## ⚡ Alternative Solution
```python
import sys                                           # getsizeof

data = [1, 2, 3]                                     # Source list
ge = (x for x in data)                               # First iterable evaluated NOW
data.append(4)                                       # Same list object mutated
print(list(ge))                                      # [1, 2, 3, 4] (sees the append)

data = [1, 2, 3]                                     # Fresh list
ge = (x for x in data)                               # Bound to this list object
data = [9]                                           # Rebinding name does not affect ge
print(list(ge))                                      # [1, 2, 3]

big_list = [i for i in range(10**6)]                 # Stores a million ints
big_gen = (i for i in range(10**6))                  # Stores only state
print(sys.getsizeof(big_list) > sys.getsizeof(big_gen))   # True (sizes vary by build)
print(sum(i for i in range(10**6)))                  # 499999500000 (constant memory)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting side effects to happen when the generator is created
log = []                                    # Collect calls
ge = (log.append(i) for i in range(3))      # Nothing runs yet
print(log)                                  # []  <- empty!

# ✅ Correct: consume it (or use a plain for loop for side effects)
list(ge)                                    # Forces execution
print(log)                                  # [0, 1, 2]
```

---

## 🎯 Interview Tip (1 line)
Say: "Generator expressions are lazy and memory-O(1); only the outermost iterable is evaluated eagerly, everything else at consumption time."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q024 (comprehension scope) | Q027 (yield and send)
