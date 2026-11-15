---

# D074. Coin Change
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #322

---

## ❓ Problem
Given coin denominations and a target `amount`, return the fewest coins needed to make that amount (unlimited coins of each type), or `-1` if impossible.

```
Input:  coins = [1,2,5], amount = 11   Output: 3   (5+5+1)
Input:  coins = [2],     amount = 3    Output: -1
```

---

## 💡 Quick Concept (2 lines only)
`dp[a]` = fewest coins for amount `a`. For every coin `c`, `dp[a] = min(dp[a], dp[a-c] + 1)`. Greedy (largest coin first) fails for some coin sets.
हिंदी: dp[a] = amount a बनाने के कम से कम सिक्के; हर सिक्के c के लिए dp[a-c]+1 से compare करो।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — recursion trying every coin
# O(S^amount) time (S = number of coins), O(amount) stack
# ============================================
def coin_change_brute(coins: list[int], amount: int) -> int:
    def go(rem: int) -> int:                 # fewest coins for remaining amount, inf if impossible
        if rem == 0:                         # exact match
            return 0                         # no more coins needed
        if rem < 0:                          # overshoot
            return float("inf")              # invalid path
        return 1 + min((go(rem - c) for c in coins), default=float("inf"))   # use one coin, recurse

    res = go(amount)                         # solve
    return -1 if res == float("inf") else res   # translate impossible


# ============================================
# APPROACH 2: Bottom-up DP ✅ PREFERRED
# O(amount * S) time, O(amount) space
# ============================================
def coin_change(coins: list[int], amount: int) -> int:
    INF = amount + 1                         # larger than any real answer
    dp = [0] + [INF] * amount                # dp[0] = 0, others unreachable
    for a in range(1, amount + 1):           # every amount up to target
        for c in coins:                      # every coin
            if c <= a:                       # coin fits
                dp[a] = min(dp[a], dp[a - c] + 1)   # use coin c on top of best for a-c
    return dp[amount] if dp[amount] != INF else -1   # -1 if unreachable


# ============================================
# TEST CASES
# ============================================
print(coin_change_brute([1, 2, 5], 11))      # Expected: 3
print(coin_change([1, 2, 5], 11))            # Expected: 3
print(coin_change([2], 3))                   # Expected: -1
print(coin_change([1], 0))                   # Expected: 0
print(coin_change([186, 419, 83, 408], 6249))   # Expected: 20
print(coin_change([1, 3, 4], 6))             # Expected: 2  (3+3; greedy 4+1+1 = 3 coins)
```

---

## 🔍 Why It Works
```
coins [1,2,5]   dp: a=0..11 -> 0 1 1 2 2 1 2 2 3 3 2 3
dp[11] = min(dp[10]+1, dp[9]+1, dp[6]+1) = min(3,4,3) = 3
```
हिंदी: छोटे amounts का best पहले निकालते हैं, फिर बड़े amount में एक सिक्का जोड़कर वही best इस्तेमाल करते हैं।

---

## 📊 Complexity
```
Brute force: Time O(S^amount) | Space O(amount)
Bottom-up:   Time O(amount*S) | Space O(amount) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: BFS — each level = one more coin; first time we hit 0 is the answer
from collections import deque                # queue for BFS


def coin_change_bfs(coins: list[int], amount: int) -> int:
    if amount == 0:                          # nothing to make
        return 0                             # zero coins
    seen = {0}                               # sums already reached
    q = deque([0])                           # current sums
    steps = 0                                # coins used so far
    while q:                                 # level by level
        steps += 1                           # next level uses one more coin
        for _ in range(len(q)):              # whole level
            cur = q.popleft()                # current sum
            for c in coins:                  # add each coin
                nxt = cur + c                # new sum
                if nxt == amount:            # target reached
                    return steps             # fewest coins
                if nxt < amount and nxt not in seen:   # still useful
                    seen.add(nxt)            # mark
                    q.append(nxt)            # explore next level
    return -1                                # unreachable


print(coin_change_bfs([1, 2, 5], 11))        # Expected: 3
print(coin_change_bfs([2], 3))               # Expected: -1


# VARIANT 1: Coin Change II (count the combinations) -> dp[a] += dp[a-c], coins in the OUTER loop
def change_ways(amount: int, coins: list[int]) -> int:
    dp = [1] + [0] * amount                  # one way to make 0
    for c in coins:                          # coin outer loop => combinations, not permutations
        for a in range(c, amount + 1):       # amounts reachable with this coin
            dp[a] += dp[a - c]               # add ways using coin c
    return dp[amount]                        # total combinations


print(change_ways(5, [1, 2, 5]))             # Expected: 4
# VARIANT 2: Print which coins were used -> store parent coin per amount
# VARIANT 3: Limited coin counts -> bounded knapsack
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: greedy largest-coin-first -> coins [1,3,4], amount 6 gives 4+1+1 (3 coins), best is 3+3 (2)
# ❌ Wrong: initialising dp with 0 -> min() always picks 0, answers are all 0
# ❌ Wrong: using float('inf') + 1 then comparing ints -> fine, but forgetting the -1 conversion

# ✅ Correct: dp[0]=0, others = amount+1 (or inf), take min over coins, return -1 if still unreachable
```

---

## 🎯 Interview Tip
Say: "Greedy fails on [1,3,4], so I use DP: dp[a] = min over coins of dp[a-c] + 1, O(amount * coins)." Mention that BFS also works and that Coin Change II counts combinations.

---

## 🔗 Related Problems
→ D072 (Climbing Stairs) | D078 (0/1 Knapsack) | D075 (Longest Increasing Subsequence)
