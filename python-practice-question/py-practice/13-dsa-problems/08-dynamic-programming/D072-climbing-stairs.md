---

# D072. Climbing Stairs
# Category: DSA — Dynamic Programming
# Difficulty: ⭐ Easy | LeetCode #70

---

## ❓ Problem
You climb a staircase of `n` steps, taking 1 or 2 steps at a time. In how many distinct ways can you reach the top?

```
Input:  n = 3   Output: 3   (1+1+1, 1+2, 2+1)
Input:  n = 5   Output: 8
```

---

## 💡 Quick Concept (2 lines only)
To land on step `n` you came from `n-1` or `n-2`, so `ways(n) = ways(n-1) + ways(n-2)` — the Fibonacci recurrence. Keep only the last two values.
हिंदी: Step n तक या तो n-1 से आए या n-2 से; इसलिए ways(n) = ways(n-1) + ways(n-2), यानी Fibonacci।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — plain recursion
# O(2^n) time, O(n) stack
# ============================================
def climb_brute(n: int) -> int:
    if n <= 2:                               # base: 1 step -> 1 way, 2 steps -> 2 ways
        return n                             # n itself
    return climb_brute(n - 1) + climb_brute(n - 2)   # last move was 1 step or 2 steps


# ============================================
# APPROACH 2: Bottom-up with two variables ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def climb_stairs(n: int) -> int:
    if n <= 2:                               # tiny cases
        return n                             # 1 -> 1, 2 -> 2
    prev, curr = 1, 2                        # ways(1), ways(2)
    for _ in range(3, n + 1):                # build up to n
        prev, curr = curr, prev + curr       # slide the window
    return curr                              # ways(n)


# ============================================
# TEST CASES
# ============================================
print(climb_brute(5))                        # Expected: 8
print(climb_stairs(1))                       # Expected: 1
print(climb_stairs(2))                       # Expected: 2
print(climb_stairs(3))                       # Expected: 3
print(climb_stairs(5))                       # Expected: 8
print(climb_stairs(45))                      # Expected: 1836311903
print(climb_stairs(100))                     # Expected: 573147844013817084101  (Python ints never overflow)
```

---

## 🔍 Why It Works
```
n:     1  2  3  4  5
ways:  1  2  3  5  8      each = sum of previous two
```
हिंदी: हर step पर सिर्फ पिछले दो मान चाहिए, इसलिए पूरा array नहीं, बस दो variables रखो।

---

## 📊 Complexity
```
Brute force: Time O(2^n) | Space O(n)
Two vars:    Time O(n)   | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: memoised recursion (top-down)
@lru_cache(maxsize=None)                     # cache every n
def climb_memo(n: int) -> int:
    if n <= 2:                               # base cases
        return n                             # 1 or 2
    return climb_memo(n - 1) + climb_memo(n - 2)   # cached sub-results


print(climb_memo(45))                        # Expected: 1836311903


# Alternative: allow any step sizes from a list (generalised)
def climb_steps(n: int, steps: tuple[int, ...] = (1, 2, 3)) -> int:
    dp = [0] * (n + 1)                       # dp[i] = ways to reach i
    dp[0] = 1                                # one way to stand at the start
    for i in range(1, n + 1):                # each stair
        dp[i] = sum(dp[i - s] for s in steps if i - s >= 0)   # sum over allowed last moves
    return dp[n]                             # ways to reach n


print(climb_steps(5))                        # Expected: 13  (with steps 1,2,3)

# VARIANT 1: Min Cost Climbing Stairs -> dp[i] = cost[i] + min(dp[i-1], dp[i-2])
# VARIANT 2: Fibonacci in O(log n) -> matrix exponentiation
# VARIANT 3: Some stairs broken -> set dp[i] = 0 for broken steps
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain recursion for n = 45 -> billions of calls, effectively hangs
# ❌ Wrong: base cases ways(0)=0 -> everything becomes 0

# ✅ Correct: memoise, or iterate with two variables; base ways(1)=1, ways(2)=2
```

---

## 🎯 Interview Tip
Say: "It's Fibonacci: the last move is 1 or 2 steps. Recursion is exponential, memoisation is O(n), and I can cut space to O(1)." Follow-up: allow steps {1,2,3}.

---

## 🔗 Related Problems
→ D073 (House Robber) | D074 (Coin Change) | D079 (Unique Paths)
