---

# D101. Best Time to Buy and Sell Stock
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #121 | Asked: Amazon, Microsoft, Goldman Sachs, Flipkart

---

## ❓ Problem
Given an array `prices` where `prices[i]` is the stock price on day i, return the maximum profit from ONE buy and ONE later sell. If no profit is possible, return 0.

```
Input:  [7, 1, 5, 3, 6, 4]
Output: 5   (buy at 1, sell at 6)

Input:  [7, 6, 4, 3, 1]
Output: 0   (prices only fall)
```

---

## 💡 Quick Concept (2 lines only)
Scan once, track the lowest price so far; at each day, profit = price - minSoFar. Keep the best profit.
हिंदी: अब तक का सबसे सस्ता दाम याद रखो, हर दिन उससे profit निकालो और max रखो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) space
// ============================================

function maxProfitBrute(prices) {
  let best = 0;                                   // best profit so far
  for (let i = 0; i < prices.length; i++) {       // try every buy day
    for (let j = i + 1; j < prices.length; j++) { // try every later sell day
      best = Math.max(best, prices[j] - prices[i]); // update best profit
    }
  }
  return best;                                    // 0 if nothing positive
}

// ============================================
// APPROACH 2: One Pass — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function maxProfit(prices) {
  let minPrice = Infinity;                // lowest price seen so far
  let best = 0;                           // best profit so far
  for (const price of prices) {           // visit each day once
    if (price < minPrice) {               // found a cheaper buy day
      minPrice = price;                   // update the minimum
    } else {
      best = Math.max(best, price - minPrice); // selling today: check profit
    }
  }
  return best;                            // maximum profit
}

// ============================================
// TEST CASES
// ============================================

console.log(maxProfit([7, 1, 5, 3, 6, 4]));       // 5
console.log(maxProfit([7, 6, 4, 3, 1]));          // 0
console.log(maxProfit([1]));                      // 0
console.log(maxProfit([]));                       // 0
console.log(maxProfit([2, 4, 1]));                // 2
console.log(maxProfitBrute([7, 1, 5, 3, 6, 4]));  // 5
```

---

## 🔍 Why One Pass Works
```
prices = [7, 1, 5, 3, 6, 4]
day0: price=7 → min=7, best=0
day1: price=1 → min=1, best=0
day2: price=5 → 5-1=4, best=4
day3: price=3 → 3-1=2, best=4
day4: price=6 → 6-1=5, best=5
day5: price=4 → 4-1=3, best=5
```
The best sell on day j always pairs with the cheapest day before j — so we only need the running minimum.
हिंदी: Sell करने वाले दिन के लिए सबसे अच्छा buy हमेशा उससे पहले का minimum होता है।

---

## 📊 Complexity
```
Brute Force: Time O(n²) | Space O(1)
One Pass:    Time O(n)  | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Unlimited transactions (LeetCode #122) — add every upward move
function maxProfitMany(prices) {
  let profit = 0;                                  // total profit
  for (let i = 1; i < prices.length; i++) {        // compare consecutive days
    if (prices[i] > prices[i - 1]) profit += prices[i] - prices[i - 1]; // take every rise
  }
  return profit;                                   // total
}
console.log(maxProfitMany([7, 1, 5, 3, 6, 4]));    // 7

// VARIANT 2: With transaction fee / cooldown (#714, #309) → needs DP with states hold/sold
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using global min and global max (sell could be BEFORE buy)
Math.max(...prices) - Math.min(...prices);  // fails for [9,1]: gives 8, correct answer is 0

// ✅ Correct: sell day must come after buy day — track running minimum
```

---

## 🎯 Interview Tip
Say: "Brute force is O(n²). I track the minimum price so far and compute profit at each day — O(n) time, O(1) space." Mention that returning 0 handles the no-profit case.

---

## 🔗 Related Problems
→ D002 (Maximum Subarray) | D102 (Contains Duplicate) | D103 (Product of Array Except Self)
