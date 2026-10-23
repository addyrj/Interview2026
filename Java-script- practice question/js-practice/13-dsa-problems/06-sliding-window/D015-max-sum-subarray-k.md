---

# D015. Maximum Sum Subarray of Size K
# Category: DSA — Sliding Window
# Difficulty: ⭐ Easy | Asked: Amazon, Razorpay, Paytm, Goldman Sachs

---

## ❓ Problem
Given an array `nums` and integer `k`, find the maximum sum of any contiguous subarray of size `k`.

```javascript
maxSumSubarray([2, 1, 5, 1, 3, 2], 3);   // 9  ([5,1,3])
maxSumSubarray([2, 3, 4, 1, 5], 2);       // 7  ([3,4])
maxSumSubarray([-1, -2, -3, -4], 2);      // -3 ([-1,-2])
```

---

## 💡 Quick Concept (2 lines only)
Sliding Window: compute first window sum, then slide by adding next element and removing first element of window. O(n) instead of O(n×k).
हिंदी: पहले window की sum calculate करो, फिर slide करो — next add करो, first remove करो। O(n) solution।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n×k)
// ============================================

function maxSumBrute(nums, k) {
  let max = -Infinity;
  for (let i = 0; i <= nums.length - k; i++) {
    let sum = 0;
    for (let j = i; j < i + k; j++) sum += nums[j];
    max = Math.max(max, sum);
  }
  return max;
}

// ============================================
// APPROACH 2: Sliding Window — O(n) time, O(1) space ✅
// ============================================

function maxSumSubarray(nums, k) {
  if (nums.length < k) return null;
  
  // Step 1: compute sum of first window
  let windowSum = 0;
  for (let i = 0; i < k; i++) windowSum += nums[i];
  
  let maxSum = windowSum;
  
  // Step 2: slide window from index k to end
  for (let i = k; i < nums.length; i++) {
    windowSum += nums[i];         // add new element (entering window)
    windowSum -= nums[i - k];     // remove old element (leaving window)
    maxSum = Math.max(maxSum, windowSum);
  }
  
  return maxSum;
}

// ============================================
// TEST CASES
// ============================================

console.log(maxSumSubarray([2, 1, 5, 1, 3, 2], 3));  // 9
console.log(maxSumSubarray([2, 3, 4, 1, 5], 2));      // 7
console.log(maxSumSubarray([-1, -2, -3, -4], 2));     // -3
console.log(maxSumSubarray([1, 2, 3, 4, 5], 5));      // 15 (entire array)

// WALKTHROUGH for [2,1,5,1,3,2], k=3:
// First window: 2+1+5 = 8, max=8
// i=3: +1 -2 = 7,  max=8
// i=4: +3 -1 = 9,  max=9
// i=5: +2 -5 = 6,  max=9
// Answer: 9 ✅
```

---

## 🔍 Why Sliding Window Works
Instead of recomputing sum for each window (O(k) per window), we maintain a running sum. Each slide: add one new element, remove one old element. Total: O(n).
हिंदी: Sliding window में हर step पर सिर्फ एक add और एक remove — O(n) में सब windows check होती हैं।

---

## 📊 Complexity
```
Brute Force:    Time O(n×k) | Space O(1)
Sliding Window: Time O(n)   | Space O(1) ← optimal
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Smallest subarray with sum >= target (variable window)
function minSubarrayLen(target, nums) {
  let left = 0, sum = 0, minLen = Infinity;
  
  for (let right = 0; right < nums.length; right++) {
    sum += nums[right];
    
    while (sum >= target) {            // shrink window from left
      minLen = Math.min(minLen, right - left + 1);
      sum -= nums[left++];
    }
  }
  
  return minLen === Infinity ? 0 : minLen;
}
console.log(minSubarrayLen(7, [2,3,1,2,4,3]));  // 2 ([4,3])

// VARIANT 2: Longest substring without repeating characters (LeetCode #3)
function lengthOfLongestSubstring(s) {
  const seen = new Map();  // char → index
  let left = 0, maxLen = 0;
  
  for (let right = 0; right < s.length; right++) {
    if (seen.has(s[right]) && seen.get(s[right]) >= left) {
      left = seen.get(s[right]) + 1;  // move left past duplicate
    }
    seen.set(s[right], right);
    maxLen = Math.max(maxLen, right - left + 1);
  }
  
  return maxLen;
}
console.log(lengthOfLongestSubstring('abcabcbb'));  // 3 ('abc')
console.log(lengthOfLongestSubstring('pwwkew'));    // 3 ('wke')

// VARIANT 3: Fruits into Baskets (at most 2 distinct types) (LeetCode #904)
function totalFruit(fruits) {
  const basket = new Map();
  let left = 0, maxLen = 0;
  
  for (let right = 0; right < fruits.length; right++) {
    basket.set(fruits[right], (basket.get(fruits[right]) || 0) + 1);
    
    while (basket.size > 2) {
      const leftFruit = fruits[left++];
      basket.set(leftFruit, basket.get(leftFruit) - 1);
      if (basket.get(leftFruit) === 0) basket.delete(leftFruit);
    }
    
    maxLen = Math.max(maxLen, right - left + 1);
  }
  
  return maxLen;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting the initial window computation
function maxSum(nums, k) {
  let windowSum = 0, max = 0;
  
  for (let i = k; i < nums.length; i++) {  // starts from k, misses first window!
    windowSum += nums[i] - nums[i - k];
    max = Math.max(max, windowSum);
  }
  return max;  // windowSum never initialized with first k elements!
}

// ✅ Correct: always initialize first window separately, then slide

// ❌ Wrong: using max = 0 (fails for all-negative arrays)
// ✅ Initialize max to first window sum
```

---

## 🎯 Interview Tip
Say: "Sliding window avoids recomputing overlapping parts — fixed window: add right, remove left; variable window: expand right until invalid, shrink from left. Recognizing 'contiguous subarray/substring' → think sliding window."

---

## 🔗 Related Problems
→ D016 (Longest Substring No Repeat) | D017 (Subarray Sum = K) | D002 (Max Subarray — Kadane's)
