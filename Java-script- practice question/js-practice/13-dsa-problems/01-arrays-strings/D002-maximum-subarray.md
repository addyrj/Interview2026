---

# D002. Maximum Subarray (Kadane's Algorithm)
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #53 | Asked: Amazon, Microsoft, Goldman Sachs

---

## ❓ Problem
Given an integer array `nums`, find the subarray with the largest sum, and return its sum.

```javascript
maxSubarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]);  // 6  ([4,-1,2,1])
maxSubarray([1]);                                  // 1
maxSubarray([5, 4, -1, 7, 8]);                    // 23  (entire array)
maxSubarray([-1]);                                 // -1
```

---

## 💡 Quick Concept (2 lines only)
Kadane's Algorithm: track current subarray sum. If adding next element makes it worse than starting fresh, start a new subarray. Keep track of the max seen.
हिंदी: Kadane's: अगर current sum negative हो जाए तो नया subarray start करो — max को track करते रहो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²)
// ============================================

function maxSubarrayBrute(nums) {
  let max = -Infinity;
  for (let i = 0; i < nums.length; i++) {
    let sum = 0;
    for (let j = i; j < nums.length; j++) {
      sum += nums[j];
      max = Math.max(max, sum);
    }
  }
  return max;
}

// ============================================
// APPROACH 2: Kadane's Algorithm — O(n) time, O(1) space ✅ OPTIMAL
// ============================================

function maxSubarray(nums) {
  let currentSum = nums[0];   // current subarray sum
  let maxSum = nums[0];        // best sum seen so far
  
  for (let i = 1; i < nums.length; i++) {
    // Decision: extend current subarray OR start fresh from nums[i]
    currentSum = Math.max(nums[i], currentSum + nums[i]);
    
    // Update global max
    maxSum = Math.max(maxSum, currentSum);
  }
  
  return maxSum;
}

// ============================================
// TEST CASES
// ============================================

console.log(maxSubarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])); // 6
console.log(maxSubarray([1]));                               // 1
console.log(maxSubarray([5, 4, -1, 7, 8]));                 // 23
console.log(maxSubarray([-1]));                              // -1
console.log(maxSubarray([-2, -3, -1, -5]));                 // -1 (least negative)

// WALKTHROUGH for [-2, 1, -3, 4, -1, 2, 1, -5, 4]:
// i=0: curr=-2, max=-2
// i=1: curr=max(1, -2+1)=max(1,-1)=1,   max=1
// i=2: curr=max(-3,1-3)=max(-3,-2)=-2,  max=1
// i=3: curr=max(4,-2+4)=max(4,2)=4,     max=4
// i=4: curr=max(-1,4-1)=max(-1,3)=3,    max=4
// i=5: curr=max(2,3+2)=max(2,5)=5,      max=5
// i=6: curr=max(1,5+1)=max(1,6)=6,      max=6
// i=7: curr=max(-5,6-5)=max(-5,1)=1,    max=6
// i=8: curr=max(4,1+4)=max(4,5)=5,      max=6
// Answer: 6 ✅
```

---

## 🔍 Why Kadane's Works
The key insight: if `currentSum + nums[i] < nums[i]`, then `currentSum` is negative — it's dragging us down. Better to start fresh from `nums[i]`. Otherwise, extend the current subarray.
हिंदी: अगर current sum negative है तो वो new element को घटाता है — fresh start better; इसीलिए `max(nums[i], curr+nums[i])`।

---

## 📊 Complexity
```
Brute Force:      Time O(n²) | Space O(1)
Kadane's:         Time O(n)  | Space O(1) ← optimal
Divide & Conquer: Time O(n log n) | Space O(log n)
```

---

## ⚡ Variations (common follow-ups)

```javascript
// VARIANT 1: Return the subarray indices (not just sum)
function maxSubarrayWithIndices(nums) {
  let currentSum = nums[0], maxSum = nums[0];
  let start = 0, end = 0, tempStart = 0;
  
  for (let i = 1; i < nums.length; i++) {
    if (nums[i] > currentSum + nums[i]) {
      currentSum = nums[i];
      tempStart = i;  // new subarray starts here
    } else {
      currentSum += nums[i];
    }
    if (currentSum > maxSum) {
      maxSum = currentSum;
      start = tempStart;
      end = i;
    }
  }
  
  return { sum: maxSum, subarray: nums.slice(start, end + 1), start, end };
}

console.log(maxSubarrayWithIndices([-2,1,-3,4,-1,2,1,-5,4]));
// { sum: 6, subarray: [4,-1,2,1], start: 3, end: 6 }

// VARIANT 2: Maximum Product Subarray (LeetCode #152)
function maxProduct(nums) {
  let maxProd = nums[0], minProd = nums[0], result = nums[0];
  
  for (let i = 1; i < nums.length; i++) {
    if (nums[i] < 0) [maxProd, minProd] = [minProd, maxProd]; // swap on negative!
    maxProd = Math.max(nums[i], maxProd * nums[i]);
    minProd = Math.min(nums[i], minProd * nums[i]);
    result = Math.max(result, maxProd);
  }
  
  return result;
}
console.log(maxProduct([2, 3, -2, 4]));  // 6

// VARIANT 3: Circular subarray max sum
function maxSubarrayCircular(nums) {
  const totalSum = nums.reduce((a, b) => a + b, 0);
  const maxNormal = maxSubarray(nums);
  const minSubarray = minSubarraySum(nums);  // negate nums and use kadane's
  
  // Either: max non-wrapping OR total - min_subarray (wrapping case)
  return maxNormal > 0 ? Math.max(maxNormal, totalSum - minSubarray) : maxNormal;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: initializing max/curr to 0 (fails for all-negative arrays)
let maxSum = 0;
let currSum = 0;
// For [-1, -2, -3]: returns 0 — WRONG! answer is -1

// ✅ Correct: initialize to nums[0]
let maxSum = nums[0];
let currSum = nums[0];

// ❌ Wrong: resetting curr to 0 (same issue)
if (currSum < 0) currSum = 0;  // wrong for all-negative
// ✅ Correct: take max(nums[i], curr + nums[i]) — includes starting fresh at nums[i]
```

---

## 🎯 Interview Tip
Say: "Kadane's is O(n) with O(1) space — the key decision is: extend current subarray or start fresh? That's `Math.max(nums[i], currentSum + nums[i])`. Initialize to nums[0] not 0 to handle all-negative."

---

## 🔗 Related Problems
→ D003 (Merge Intervals) | D006 (Max Product Subarray) | D021 (House Robber — DP)
