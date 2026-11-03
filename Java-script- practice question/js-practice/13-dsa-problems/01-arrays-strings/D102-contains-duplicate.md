---

# D102. Contains Duplicate
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #217 | Asked: Amazon, Apple, Adobe, Paytm

---

## ❓ Problem
Given an integer array `nums`, return `true` if any value appears at least twice, else `false`.

```
Input:  [1, 2, 3, 1]
Output: true

Input:  [1, 2, 3, 4]
Output: false
```

---

## 💡 Quick Concept (2 lines only)
Put numbers in a Set as you go; if the number is already in the Set, a duplicate exists. Sorting is an O(1)-extra-space alternative.
हिंदी: Set में डालते जाओ — अगर number पहले से मौजूद है तो duplicate मिल गया।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) space
// ============================================

function containsDuplicateBrute(nums) {
  for (let i = 0; i < nums.length; i++) {         // pick each element
    for (let j = i + 1; j < nums.length; j++) {   // compare with every later one
      if (nums[i] === nums[j]) return true;       // equal → duplicate
    }
  }
  return false;                                   // no pair matched
}

// ============================================
// APPROACH 2: Sorting — O(n log n) time, O(1) extra space
// ============================================

function containsDuplicateSort(nums) {
  const sorted = [...nums].sort((a, b) => a - b); // copy then sort numerically
  for (let i = 1; i < sorted.length; i++) {       // duplicates become neighbours
    if (sorted[i] === sorted[i - 1]) return true; // neighbour equal → duplicate
  }
  return false;                                   // all distinct
}

// ============================================
// APPROACH 3: Hash Set — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function containsDuplicate(nums) {
  const seen = new Set();                 // numbers visited so far
  for (const n of nums) {                 // go through each number
    if (seen.has(n)) return true;         // already seen → duplicate
    seen.add(n);                          // remember this number
  }
  return false;                           // never repeated
}

// One-liner: Set drops duplicates, so a smaller size means a repeat existed
const oneLiner = (nums) => new Set(nums).size !== nums.length; // compare sizes

// ============================================
// TEST CASES
// ============================================

console.log(containsDuplicate([1, 2, 3, 1]));        // true
console.log(containsDuplicate([1, 2, 3, 4]));        // false
console.log(containsDuplicate([]));                  // false
console.log(containsDuplicate([5]));                 // false
console.log(containsDuplicateSort([1, 1, 1, 3]));    // true
console.log(containsDuplicateBrute([9, 8, 7]));      // false
console.log(oneLiner([4, 4]));                       // true
```

---

## 🔍 Why Set Works
```
nums = [1, 2, 3, 1]
1 → not in set → add   {1}
2 → not in set → add   {1,2}
3 → not in set → add   {1,2,3}
1 → in set!   → return true
```
Set lookup is O(1) average, so one pass finishes in O(n).
हिंदी: Set में check करना O(1) है, इसलिए एक ही pass काफी है।

---

## 📊 Complexity
```
Brute Force: Time O(n²)     | Space O(1)
Sorting:     Time O(n log n)| Space O(1) extra
Hash Set:    Time O(n)      | Space O(n) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Duplicate within k indices (LeetCode #219)
function nearbyDuplicate(nums, k) {
  const last = new Map();                       // value → last index seen
  for (let i = 0; i < nums.length; i++) {       // scan array
    if (last.has(nums[i]) && i - last.get(nums[i]) <= k) return true; // close enough
    last.set(nums[i], i);                       // update last index
  }
  return false;                                 // none within distance k
}
console.log(nearbyDuplicate([1, 2, 3, 1], 3));  // true
console.log(nearbyDuplicate([1, 2, 3, 1], 2));  // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: default sort() compares as strings
[10, 9, 1].sort();            // [1, 10, 9] — wrong numeric order

// ✅ Correct: pass a comparator
[10, 9, 1].sort((a, b) => a - b);  // [1, 9, 10]
```

---

## 🎯 Interview Tip
Say: "Hash set gives O(n) time with O(n) space. If memory matters, sort first for O(n log n) time and O(1) extra space." Interviewers like hearing the trade-off.

---

## 🔗 Related Problems
→ D001 (Two Sum) | D101 (Best Time to Buy and Sell Stock) | D116 (Longest Consecutive Sequence)
