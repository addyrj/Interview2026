---

# D030. Climbing Stairs
# Category: DSA — Dynamic Programming
# Difficulty: ⭐ Easy | LeetCode #70 | Asked: Almost every company as intro to DP

---

## ❓ Problem
You are climbing a staircase with `n` steps. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?

```javascript
climbStairs(1);  // 1  (only: [1])
climbStairs(2);  // 2  ([1,1] or [2])
climbStairs(3);  // 3  ([1,1,1], [1,2], [2,1])
climbStairs(4);  // 5  ([1,1,1,1],[1,1,2],[1,2,1],[2,1,1],[2,2])
climbStairs(5);  // 8
```

---

## 💡 Quick Concept (2 lines only)
This is Fibonacci! To reach step n, you came from step n-1 (took 1 step) or step n-2 (took 2 steps). So `ways(n) = ways(n-1) + ways(n-2)`.
हिंदी: Step n तक पहुंचने के ways = (n-1 से आओ) + (n-2 से आओ) — यही Fibonacci है।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Recursion — O(2^n) — TOO SLOW
// ============================================

function climbStairsRecursive(n) {
  if (n <= 2) return n;
  return climbStairsRecursive(n - 1) + climbStairsRecursive(n - 2);
}
// Recomputes same subproblems millions of times — never use in interview!

// ============================================
// APPROACH 2: Memoization (Top-Down DP) — O(n) time, O(n) space
// ============================================

function climbStairsMemo(n, memo = {}) {
  if (n <= 2) return n;
  if (memo[n]) return memo[n];
  memo[n] = climbStairsMemo(n - 1, memo) + climbStairsMemo(n - 2, memo);
  return memo[n];
}

// ============================================
// APPROACH 3: Tabulation (Bottom-Up DP) — O(n) time, O(n) space ✅
// ============================================

function climbStairsDP(n) {
  if (n <= 2) return n;
  
  const dp = new Array(n + 1);
  dp[1] = 1;  // 1 way to climb 1 step
  dp[2] = 2;  // 2 ways to climb 2 steps
  
  for (let i = 3; i <= n; i++) {
    dp[i] = dp[i - 1] + dp[i - 2];  // Fibonacci recurrence
  }
  
  return dp[n];
}

// ============================================
// APPROACH 4: Space-Optimized — O(n) time, O(1) space ✅ BEST
// ============================================

function climbStairs(n) {
  if (n <= 2) return n;
  
  let prev2 = 1;  // ways(1)
  let prev1 = 2;  // ways(2)
  
  for (let i = 3; i <= n; i++) {
    const curr = prev1 + prev2;  // ways(i) = ways(i-1) + ways(i-2)
    prev2 = prev1;
    prev1 = curr;
  }
  
  return prev1;
}

// ============================================
// TEST CASES
// ============================================

console.log(climbStairs(1));   // 1
console.log(climbStairs(2));   // 2
console.log(climbStairs(3));   // 3
console.log(climbStairs(4));   // 5
console.log(climbStairs(5));   // 8
console.log(climbStairs(10));  // 89
console.log(climbStairs(45));  // 1836311903
```

---

## 🔍 DP Pattern — Recognize It!
```
State:      dp[i] = number of ways to reach step i
Recurrence: dp[i] = dp[i-1] + dp[i-2]
Base cases: dp[1] = 1, dp[2] = 2
Direction:  Bottom-up (i = 3 to n)

This is Fibonacci: 1, 2, 3, 5, 8, 13, 21...
```
हिंदी: DP का pattern: state define करो → recurrence relation लिखो → base cases → bottom-up fill करो।

---

## 📊 Complexity
```
Recursion:   Time O(2^n) | Space O(n)  ← too slow
Memo:        Time O(n)   | Space O(n)
Tabulation:  Time O(n)   | Space O(n)
Optimized:   Time O(n)   | Space O(1) ← use this
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Jump can be 1, 2 or 3 steps
function climbStairs3(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  if (n === 2) return 2;
  if (n === 3) return 4;  // [1,1,1],[1,2],[2,1],[3]
  
  let a = 1, b = 2, c = 4;
  for (let i = 4; i <= n; i++) {
    const d = a + b + c;
    a = b; b = c; c = d;
  }
  return c;
}

// VARIANT 2: Minimum cost to reach top (LeetCode #746)
function minCostClimbingStairs(cost) {
  const n = cost.length;
  let prev2 = cost[0], prev1 = cost[1];
  
  for (let i = 2; i <= n; i++) {
    const curr = Math.min(prev1, prev2) + (cost[i] || 0); // cost[n]=0 (top)
    prev2 = prev1;
    prev1 = curr;
  }
  
  return Math.min(prev1, prev2);
}
console.log(minCostClimbingStairs([10, 15, 20]));    // 15
console.log(minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])); // 6

// VARIANT 3: House Robber (same DP pattern! LeetCode #198)
function rob(nums) {
  if (nums.length === 0) return 0;
  if (nums.length === 1) return nums[0];
  
  let prev2 = nums[0];
  let prev1 = Math.max(nums[0], nums[1]);
  
  for (let i = 2; i < nums.length; i++) {
    const curr = Math.max(prev1, prev2 + nums[i]);
    prev2 = prev1;
    prev1 = curr;
  }
  
  return prev1;
}
console.log(rob([1,2,3,1]));  // 4 (rob house 1 and 3)
console.log(rob([2,7,9,3,1])); // 12 (rob house 1,3,5)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not handling edge cases
function climbStairs(n) {
  const dp = [0, 1, 2];  // dp[0]=0, dp[1]=1, dp[2]=2
  for (let i = 3; i <= n; i++) dp[i] = dp[i-1] + dp[i-2];
  return dp[n];
}
climbStairs(0);  // 0 — what should this be? (1 way: do nothing)
// Check problem constraints: usually n >= 1

// ❌ Wrong: not recognizing THIS IS FIBONACCI (wastes time re-deriving)
// ✅ Recognize the pattern: "reach here from prev state" → DP → often Fibonacci-like

// ❌ Wrong: starting bottom-up from i=2 with dp[0] and dp[1]
// Make sure your indexing is consistent (1-indexed vs 0-indexed)
```

---

## 🎯 Interview Tip
Say: "This is Fibonacci — recognize the recurrence: ways(n) = ways(n-1) + ways(n-2). Mention all 4 approaches (naive recursion → memo → tabulation → space-optimized). Always optimize to O(1) space for linear DP."

---

## 🔗 Related Problems
→ D031 (House Robber) | D032 (Coin Change) | D033 (Longest Common Subsequence)
