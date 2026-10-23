---

# D031. Coin Change
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #322 | Asked: Google, Flipkart, Amazon, Paytm

---

## ❓ Problem
Given an array of coin denominations `coins` and an integer `amount`, return the minimum number of coins needed to make up that amount. Return `-1` if it's not possible.

```javascript
coinChange([1, 5, 6, 9], 11);   // 2  (5+6)
coinChange([1, 2, 5], 11);      // 3  (5+5+1)
coinChange([2], 3);              // -1 (impossible)
coinChange([1], 0);              // 0
```

---

## 💡 Quick Concept (2 lines only)
Bottom-up DP: `dp[i]` = minimum coins to make amount `i`. For each coin, `dp[i] = min(dp[i], dp[i - coin] + 1)`. Fill from 0 to amount.
हिंदी: `dp[i]` = i amount बनाने के minimum coins; हर coin के लिए: `dp[i] = min(dp[i], dp[i-coin]+1)`।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Greedy — WRONG! (always take biggest coin)
// ============================================

// [1,5,6,9], amount=11: greedy takes 9 → 2 (9+1+1) — but optimal is 5+6=2 ✅
// [1,3,4], amount=6: greedy takes 4 → 3 (4+1+1) — but optimal is 3+3=2 ❌
// Greedy fails — use DP

// ============================================
// APPROACH 2: DP (Bottom-Up) — O(amount × coins) ✅
// ============================================

function coinChange(coins, amount) {
  // dp[i] = minimum coins to make amount i
  const dp = new Array(amount + 1).fill(Infinity);
  dp[0] = 0;  // base case: 0 coins to make amount 0
  
  for (let i = 1; i <= amount; i++) {
    for (const coin of coins) {
      if (coin <= i) {
        // Use this coin: 1 coin + whatever it takes to make (i - coin)
        dp[i] = Math.min(dp[i], dp[i - coin] + 1);
      }
    }
  }
  
  return dp[amount] === Infinity ? -1 : dp[amount];
}

// ============================================
// TEST CASES
// ============================================

console.log(coinChange([1, 5, 6, 9], 11));  // 2  (5+6)
console.log(coinChange([1, 2, 5], 11));     // 3  (5+5+1)
console.log(coinChange([2], 3));             // -1
console.log(coinChange([1], 0));             // 0
console.log(coinChange([186, 419, 83, 408], 6249));  // 20

// WALKTHROUGH for [1,2,5], amount=5:
// dp = [0, ∞, ∞, ∞, ∞, ∞]
// i=1: coin=1: dp[1]=min(∞,dp[0]+1)=1; coin=2: 2>1 skip; coin=5: 5>1 skip
//      dp[1]=1
// i=2: coin=1: dp[2]=min(∞,dp[1]+1)=2; coin=2: dp[2]=min(2,dp[0]+1)=1
//      dp[2]=1
// i=3: coin=1: dp[3]=2; coin=2: dp[3]=min(2,dp[1]+1)=2
//      dp[3]=2
// i=4: coin=1: dp[4]=3; coin=2: dp[4]=min(3,dp[2]+1)=2
//      dp[4]=2
// i=5: coin=1: dp[5]=3; coin=2: dp[5]=min(3,dp[3]+1)=3; coin=5: dp[5]=min(3,dp[0]+1)=1
//      dp[5]=1 ✅
```

---

## 🔍 DP Pattern
```
State:      dp[i] = min coins to make amount i
Recurrence: dp[i] = min(dp[i - coin] + 1) for all coins where coin ≤ i
Base:       dp[0] = 0
Init:       dp[i] = Infinity (impossible until proven otherwise)
Return:     dp[amount] if finite, else -1
```
हिंदी: State = amount i के लिए minimum coins; हर coin try करो और best pick करो।

---

## 📊 Complexity
```
Time:  O(amount × len(coins))
Space: O(amount) — dp array
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Number of ways to make amount (LeetCode #518)
function change(amount, coins) {
  const dp = new Array(amount + 1).fill(0);
  dp[0] = 1;  // one way to make 0: use no coins
  
  for (const coin of coins) {         // outer loop: coins (not amounts!)
    for (let i = coin; i <= amount; i++) {
      dp[i] += dp[i - coin];          // each coin can be used unlimited times
    }
  }
  
  return dp[amount];
}
console.log(change(5, [1, 2, 5]));   // 4 ways: [1,1,1,1,1],[1,1,1,2],[1,2,2],[5]

// VARIANT 2: 0/1 Knapsack — each coin used at most once
function coinChangeOnce(coins, amount) {
  const dp = new Array(amount + 1).fill(Infinity);
  dp[0] = 0;
  
  for (const coin of coins) {
    // Go backwards to prevent reusing same coin!
    for (let i = amount; i >= coin; i--) {
      dp[i] = Math.min(dp[i], dp[i - coin] + 1);
    }
  }
  
  return dp[amount] === Infinity ? -1 : dp[amount];
}

// VARIANT 3: Minimum coin change with coin tracking
function coinChangeWithCoins(coins, amount) {
  const dp = new Array(amount + 1).fill(Infinity);
  const used = new Array(amount + 1).fill(-1);
  dp[0] = 0;
  
  for (let i = 1; i <= amount; i++) {
    for (const coin of coins) {
      if (coin <= i && dp[i - coin] + 1 < dp[i]) {
        dp[i] = dp[i - coin] + 1;
        used[i] = coin;  // track which coin was used
      }
    }
  }
  
  if (dp[amount] === Infinity) return { count: -1, coins: [] };
  
  // Reconstruct coins used:
  const result = [];
  let rem = amount;
  while (rem > 0) {
    result.push(used[rem]);
    rem -= used[rem];
  }
  return { count: dp[amount], coins: result };
}
console.log(coinChangeWithCoins([1, 5, 6, 9], 11));  // { count: 2, coins: [6, 5] }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: initializing dp with 0 (instead of Infinity)
const dp = new Array(amount + 1).fill(0);
// dp[i]=0 means "we assume 0 coins are needed" — incorrect!
// ✅ Fill with Infinity, only dp[0]=0

// ❌ Wrong: greedy approach
// Always taking largest coin first fails for [1,3,4], amount=6
// Greedy: 4,1,1 = 3 coins. DP: 3,3 = 2 coins

// ❌ Wrong: not checking dp[amount] === Infinity before returning
return dp[amount];  // returns Infinity if impossible!
// ✅ return dp[amount] === Infinity ? -1 : dp[amount]

// ❌ Wrong: outer loop coins, inner loop amounts gives different results
// For "min coins" — loop order doesn't matter (both give correct answer)
// For "number of ways" — outer:coins inner:amounts = combinations, vice versa = permutations
```

---

## 🎯 Interview Tip
Say: "Greedy fails — prove it with [1,3,4],6. DP: dp[i] = min coins for amount i; try every coin, take the min; initialize dp to Infinity (impossible) except dp[0]=0."

---

## 🔗 Related Problems
→ D030 (Climbing Stairs) | D032 (Target Sum) | D033 (LCS) | D034 (0/1 Knapsack)
