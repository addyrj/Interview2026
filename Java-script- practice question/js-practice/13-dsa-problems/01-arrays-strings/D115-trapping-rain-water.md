---

# D115. Trapping Rain Water
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐⭐ Hard | LeetCode #42 | Asked: Amazon, Google, Goldman Sachs, Microsoft, Flipkart

---

## ❓ Problem
Given n non-negative integers representing an elevation map (bar width 1), compute how much water it can trap after raining.

```
Input:  [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
```

---

## 💡 Quick Concept (2 lines only)
Water above bar i = min(maxLeft, maxRight) - height[i]. Precompute the max arrays, or use two pointers that always move the smaller side.
हिंदी: हर bar के ऊपर पानी = (left max और right max में छोटा) - bar की height।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) space
// ============================================

function trapBrute(height) {
  let total = 0;                                     // total water
  for (let i = 0; i < height.length; i++) {          // for each bar
    let leftMax = 0, rightMax = 0;                   // tallest on each side
    for (let l = 0; l <= i; l++) leftMax = Math.max(leftMax, height[l]);                  // scan left (incl. i)
    for (let r = i; r < height.length; r++) rightMax = Math.max(rightMax, height[r]);     // scan right (incl. i)
    total += Math.min(leftMax, rightMax) - height[i]; // water above this bar
  }
  return total;
}

// ============================================
// APPROACH 2: Prefix/suffix max arrays — O(n) time, O(n) space
// ============================================

function trapArrays(height) {
  const n = height.length;                           // length
  if (n === 0) return 0;                             // no bars
  const left = new Array(n), right = new Array(n);   // max-so-far arrays
  left[0] = height[0];                               // first bar
  for (let i = 1; i < n; i++) left[i] = Math.max(left[i - 1], height[i]);         // tallest up to i
  right[n - 1] = height[n - 1];                      // last bar
  for (let i = n - 2; i >= 0; i--) right[i] = Math.max(right[i + 1], height[i]);  // tallest from i
  let total = 0;                                     // water
  for (let i = 0; i < n; i++) total += Math.min(left[i], right[i]) - height[i];   // per-bar water
  return total;
}

// ============================================
// APPROACH 3: Two pointers — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function trap(height) {
  let left = 0, right = height.length - 1;           // pointers at both ends
  let leftMax = 0, rightMax = 0;                     // tallest seen from each side
  let total = 0;                                     // trapped water
  while (left < right) {                             // until pointers meet
    if (height[left] < height[right]) {              // left side is the limiting side
      if (height[left] >= leftMax) leftMax = height[left]; // new wall on the left
      else total += leftMax - height[left];          // water trapped at left
      left++;                                        // move inward
    } else {                                         // right side is limiting
      if (height[right] >= rightMax) rightMax = height[right]; // new wall on the right
      else total += rightMax - height[right];        // water trapped at right
      right--;                                       // move inward
    }
  }
  return total;                                      // total water
}

// ============================================
// TEST CASES
// ============================================

console.log(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])); // 6
console.log(trap([4, 2, 0, 3, 2, 5]));               // 9
console.log(trap([1, 2, 3]));                        // 0
console.log(trap([]));                               // 0
console.log(trapArrays([4, 2, 0, 3, 2, 5]));         // 9
console.log(trapBrute([3, 0, 2, 0, 4]));             // 7
```

---

## 🔍 Why Two Pointers Work
```
If height[left] < height[right], the right side has a wall at least as tall as
height[left]. So water at `left` depends only on leftMax — the right side can't be the limit.
Process left, move on. Symmetric for the right side.
```
हिंदी: जो side छोटी है उसका पानी उसी side के max से तय होता है, इसलिए उसे ही आगे बढ़ाओ।

---

## 📊 Complexity
```
Brute Force:  Time O(n²) | Space O(1)
Max arrays:   Time O(n)  | Space O(n)
Two pointers: Time O(n)  | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Container With Most Water (LeetCode #11)
function maxArea(height) {
  let l = 0, r = height.length - 1, best = 0;        // pointers and best area
  while (l < r) {                                    // until they meet
    best = Math.max(best, Math.min(height[l], height[r]) * (r - l)); // area of this pair
    if (height[l] < height[r]) l++; else r--;        // drop the shorter wall
  }
  return best;
}
console.log(maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]));   // 49
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using only the left max (or global max) → ignores the shorter right wall
// ❌ Wrong: water = max - height with negative values (not clamping): leftMax >= height always holds when using prefix max, so don't skip updating the max
// ✅ Correct: water = min(leftMax, rightMax) - height[i]
```

---

## 🎯 Interview Tip
Walk through: brute force O(n²), then precomputed max arrays O(n)/O(n), then two pointers O(n)/O(1). A monotonic stack is another accepted solution.

---

## 🔗 Related Problems
→ D103 (Product of Array Except Self) | D101 (Best Time to Buy and Sell Stock) | D116 (Longest Consecutive Sequence)
