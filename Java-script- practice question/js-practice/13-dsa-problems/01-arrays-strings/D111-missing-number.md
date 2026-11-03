---

# D111. Missing Number
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #268 | Asked: Amazon, Microsoft, Apple, Capgemini

---

## ❓ Problem
Given an array of n distinct numbers in the range [0, n], return the one number missing from the range.

```
Input:  [3, 0, 1]
Output: 2

Input:  [9,6,4,2,3,5,7,0,1]
Output: 8
```

---

## 💡 Quick Concept (2 lines only)
Expected sum 0..n is n(n+1)/2; subtract the actual sum. Or XOR all indices and values — pairs cancel, leaving the missing one.
हिंदी: 0 से n तक का sum निकालो, array का sum घटाओ — जो बचा वही missing number।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Sort — O(n log n) time
// ============================================

function missingSort(nums) {
  const sorted = [...nums].sort((a, b) => a - b);    // sort numerically
  for (let i = 0; i < sorted.length; i++) {          // value should equal index
    if (sorted[i] !== i) return i;                   // first mismatch = missing
  }
  return sorted.length;                              // missing is n
}

// ============================================
// APPROACH 2: Hash Set — O(n) time, O(n) space
// ============================================

function missingSet(nums) {
  const set = new Set(nums);                         // all present numbers
  for (let i = 0; i <= nums.length; i++) {           // check range 0..n
    if (!set.has(i)) return i;                       // not present → missing
  }
  return -1;                                         // unreachable for valid input
}

// ============================================
// APPROACH 3: Math sum — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function missingNumber(nums) {
  const n = nums.length;                             // range is 0..n
  const expected = (n * (n + 1)) / 2;                // sum of 0..n
  const actual = nums.reduce((a, b) => a + b, 0);    // sum of given numbers
  return expected - actual;                          // difference = missing
}

// ============================================
// APPROACH 4: XOR — O(n) time, O(1) space, no overflow
// ============================================

function missingXor(nums) {
  let x = nums.length;                               // start with n (index range 0..n-1 lacks n)
  for (let i = 0; i < nums.length; i++) {            // XOR every index and value
    x ^= i ^ nums[i];                                // equal pairs cancel to 0
  }
  return x;                                          // only missing number remains
}

// ============================================
// TEST CASES
// ============================================

console.log(missingNumber([3, 0, 1]));               // 2
console.log(missingNumber([0, 1]));                  // 2
console.log(missingNumber([9, 6, 4, 2, 3, 5, 7, 0, 1])); // 8
console.log(missingNumber([0]));                     // 1
console.log(missingXor([3, 0, 1]));                  // 2
console.log(missingSort([1, 2, 3]));                 // 0
console.log(missingSet([0, 2]));                     // 1
```

---

## 🔍 Why It Works
```
[3,0,1], n=3
expected = 3*4/2 = 6
actual   = 3+0+1 = 4
missing  = 6-4  = 2

XOR: 3 ^ (0^3) ^ (1^0) ^ (2^1) = 2
```
हिंदी: XOR में same numbers खत्म हो जाते हैं, बस missing वाला बचता है।

---

## 📊 Complexity
```
Sort: Time O(n log n) | Space O(n)
Set:  Time O(n)       | Space O(n)
Sum:  Time O(n)       | Space O(1) ← preferred
XOR:  Time O(n)       | Space O(1) (overflow-safe in other languages)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Find the duplicate AND missing (LeetCode #645, Set Mismatch)
function findErrorNums(nums) {
  const seen = new Set();                            // numbers seen
  let dup = -1;                                      // repeated number
  for (const x of nums) {                            // scan
    if (seen.has(x)) dup = x;                        // second time → duplicate
    seen.add(x);                                     // record
  }
  let missing = -1;                                  // missing number
  for (let i = 1; i <= nums.length; i++) {           // range 1..n
    if (!seen.has(i)) missing = i;                   // never seen → missing
  }
  return [dup, missing];
}
console.log(findErrorNums([1, 2, 2, 4]));            // [ 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using n = nums.length - 1 → expected sum off by n
// ✅ Correct: array has n numbers from range 0..n, so n = nums.length
```

---

## 🎯 Interview Tip
Say: "Sum formula is O(n)/O(1); XOR avoids overflow in fixed-width languages." Interviewers often ask for both.

---

## 🔗 Related Problems
→ D110 (Majority Element) | D102 (Contains Duplicate) | D116 (Longest Consecutive Sequence)
