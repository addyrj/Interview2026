---

# D002. Best Time to Buy and Sell Stock
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #121

---

## ❓ Problem
`prices[i]` is the stock price on day `i`. Choose one day to buy and a LATER day to sell to maximise profit. Return the max profit, or 0 if no profit is possible.

```
Input:  prices = [7, 1, 5, 3, 6, 4]
Output: 5   (buy at 1, sell at 6)
```

---

## 💡 Quick Concept (2 lines only)
Walk once, tracking the lowest price so far. At each day the best profit if you sell today is `price - min_so_far`; keep the maximum of those.
हिंदी: अब तक की सबसे कम price याद रखो, हर दिन `price - min_price` देखो और सबसे बड़ा profit रखो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — try every buy/sell pair
# O(n^2) time, O(1) space
# ============================================
def max_profit_brute(prices: list[int]) -> int:
    best = 0                                       # profit never below 0
    for i in range(len(prices)):                   # buy day
        for j in range(i + 1, len(prices)):        # sell day after buy
            best = max(best, prices[j] - prices[i])  # keep the larger profit
    return best                                    # final answer

# ============================================
# APPROACH 2: One pass, track min price ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def max_profit(prices: list[int]) -> int:
    min_price = float("inf")                       # cheapest price seen so far
    best = 0                                       # best profit so far
    for p in prices:                               # each day
        min_price = min(min_price, p)              # update cheapest buy day
        best = max(best, p - min_price)            # profit if sold today
    return best                                    # 0 if prices only fall

# ============================================
# TEST CASES
# ============================================
print(max_profit_brute([7, 1, 5, 3, 6, 4]))   # 5
print(max_profit([7, 1, 5, 3, 6, 4]))         # 5
print(max_profit([7, 6, 4, 3, 1]))            # 0  (falling prices)
print(max_profit([2]))                        # 0  (single day)
print(max_profit([]))                         # 0  (empty)
print(max_profit([1, 2, 3, 4, 5]))            # 4
```

---

## 🔍 Why It Works
```
prices: 7  1  5  3  6  4
min:    7  1  1  1  1  1
profit: 0  0  4  2  5  3   -> max = 5
```
हिंदी: बेचने वाले दिन के लिए सबसे अच्छा खरीद दिन वही है जहाँ अब तक की सबसे कम price थी।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
One pass:    Time O(n)   | Space O(1)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Unlimited transactions (LeetCode #122) — sum every positive rise
def max_profit_many(prices: list[int]) -> int:
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))  # add all up-moves

print(max_profit_many([7, 1, 5, 3, 6, 4]))         # 7  (4 + 3)

# VARIANT 2: Return the buy/sell days too
def max_profit_days(prices: list[int]) -> tuple[int, int, int]:
    best, buy_i, lo = 0, 0, 0                      # best profit, best buy, current low idx
    sell_i = 0                                     # best sell day
    for i, p in enumerate(prices):                 # each day
        if p < prices[lo]:                         # new low
            lo = i                                 # remember it
        if p - prices[lo] > best:                  # better profit
            best, buy_i, sell_i = p - prices[lo], lo, i  # record
    return best, buy_i, sell_i                     # profit and days

print(max_profit_days([7, 1, 5, 3, 6, 4]))         # (5, 1, 4)

# VARIANT 3: At most 2 transactions (LeetCode #123) — DP with 4 states
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: max price - min price ignores that you must buy BEFORE selling
prices = [7, 1, 5, 3, 6, 4]                        # sample
print(max(prices) - min(prices))                   # 6  <- wrong (expected 5)
prices2 = [3, 2, 6, 1]                             # 6 comes before the min (1), so no valid trade uses both
print(max(prices2) - min(prices2))                 # 5  <- wrong, true answer is 4

# ✅ Correct: track min so far and compute profit at each later day (see max_profit)
```

---

## 🎯 Interview Tip
Say: "Selling today, the best buy is the minimum before today, so one pass with a running minimum gives O(n) time, O(1) space." Mention returning 0 when prices only fall.

---

## 🔗 Related Problems
→ D005 (Maximum Subarray) | D001 (Two Sum) | D014 (Trapping Rain Water)
