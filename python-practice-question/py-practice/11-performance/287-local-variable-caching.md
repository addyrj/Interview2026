---

# Q287. Local Variable Caching
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Inside a hot loop you call `math.sqrt` and `out.append`. How can binding them to local names help, and how big is the gain on Python 3.13?

---

## 💡 Quick Concept (2 lines only)
Local names are array slots (fast); globals and attributes need dict lookups every time. Caching a lookup in a local avoids repeating it per iteration.
हिंदी: Local variable का lookup तेज़ होता है — loop के बाहर एक बार bind करो, अंदर बार-बार lookup नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import math  # module with sqrt
import timeit  # for timing


def slow(n: int) -> list[float]:
    out: list[float] = []  # result list
    for i in range(n):  # hot loop
        out.append(math.sqrt(i))  # global + 2 attribute lookups every iteration
    return out  # return results


def fast(n: int) -> list[float]:
    out: list[float] = []  # result list
    append = out.append  # Step 1: cache bound method in a local
    sqrt = math.sqrt  # Step 2: cache function in a local
    for i in range(n):  # hot loop
        append(sqrt(i))  # only local lookups
    return out  # return results


# ============================================
# TEST CASES
# ============================================
print(slow(5) == fast(5))  # Expected: True (same result)
t_slow = timeit.timeit(lambda: slow(100_000), number=20)  # time slow version
t_fast = timeit.timeit(lambda: fast(100_000), number=20)  # time fast version
print(t_fast < t_slow)  # Expected: True on a typical run (gain ~10-30%; timings vary)
```

---

## 🔍 Why This Works (3 lines max)
`math.sqrt` does a global lookup plus an attribute lookup each iteration; a local is a direct slot read. Python 3.11+ specializes these lookups, so gains shrank - measure before applying; it only matters in very hot loops.
हिंदी: Python 3.11+ में gain कम हो गया है, इसलिए पहले measure करो, फिर optimize।

---

## ⚡ Alternative Solution
```python
import math  # module


def with_default_arg(n: int, sqrt=math.sqrt) -> list[float]:  # default arg binds once at def time
    return [sqrt(i) for i in range(n)]  # comprehension uses the local 'sqrt'


from math import sqrt as s  # import the name directly (module-level global, still one lookup less)

print(with_default_arg(4))  # Expected: [0.0, 1.0, 1.4142135623730951, 1.7320508075688772]
print(s(9))  # Expected: 3.0
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: micro-optimizing everything / caching outside the hot path with no measurement
#    (makes code ugly, gain may be within noise on 3.13)

# ✅ Correct: profile first (cProfile/timeit), then cache only inside the proven hot loop
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd profile first; local caching is a micro-optimization that helps in tight loops, but algorithmic fixes matter far more."

---

## 🔗 Related Questions
→ Q276 (timeit) | Q277 (cProfile) | Q290 (slow patterns) | Q041 (LEGB scope)
