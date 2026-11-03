---

# D104. Rotate Array
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #189 | Asked: Microsoft, Amazon, Adobe, Infosys

---

## ❓ Problem
Rotate array `nums` to the right by `k` steps, in place.

```
Input:  nums = [1,2,3,4,5,6,7], k = 3
Output: [5,6,7,1,2,3,4]
```

---

## 💡 Quick Concept (2 lines only)
Reverse the whole array, then reverse the first k elements, then reverse the remaining n-k. Always use k % n.
हिंदी: पूरा reverse करो, फिर पहले k और बाकी n-k को अलग-अलग reverse करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n·k) time, O(1) space
// ============================================

function rotateBrute(nums, k) {
  k = k % nums.length;                       // k may exceed length
  for (let step = 0; step < k; step++) {     // rotate by one, k times
    const last = nums.pop();                 // take last element
    nums.unshift(last);                      // put it at the front
  }
  return nums;
}

// ============================================
// APPROACH 2: Extra array — O(n) time, O(n) space
// ============================================

function rotateExtra(nums, k) {
  const n = nums.length;                     // length
  const copy = new Array(n);                 // temporary array
  for (let i = 0; i < n; i++) {              // place each element at its new index
    copy[(i + k) % n] = nums[i];             // shifted index with wraparound
  }
  for (let i = 0; i < n; i++) nums[i] = copy[i]; // copy back in place
  return nums;
}

// ============================================
// APPROACH 3: Three reversals — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function reverse(arr, l, r) {
  while (l < r) {                            // swap until pointers meet
    [arr[l], arr[r]] = [arr[r], arr[l]];     // swap ends
    l++; r--;                                // move inward
  }
}

function rotate(nums, k) {
  const n = nums.length;                     // length
  k = k % n;                                 // normalize k
  reverse(nums, 0, n - 1);                   // [7,6,5,4,3,2,1]
  reverse(nums, 0, k - 1);                   // reverse first k   → [5,6,7,4,3,2,1]
  reverse(nums, k, n - 1);                   // reverse the rest  → [5,6,7,1,2,3,4]
  return nums;
}

// ============================================
// TEST CASES
// ============================================

console.log(rotate([1, 2, 3, 4, 5, 6, 7], 3));   // [ 5, 6, 7, 1, 2, 3, 4 ]
console.log(rotate([-1, -100, 3, 99], 2));       // [ 3, 99, -1, -100 ]
console.log(rotate([1, 2], 5));                  // [ 2, 1 ]
console.log(rotate([1], 3));                     // [ 1 ]
console.log(rotateExtra([1, 2, 3, 4, 5, 6, 7], 3)); // [ 5, 6, 7, 1, 2, 3, 4 ]
console.log(rotateBrute([1, 2, 3], 1));          // [ 3, 1, 2 ]
```

---

## 🔍 Why Reversal Works
```
[1,2,3,4,5,6,7], k=3
reverse all   → [7,6,5,4,3,2,1]
reverse [0..2]→ [5,6,7,4,3,2,1]
reverse [3..6]→ [5,6,7,1,2,3,4]
```
The last k elements must come to the front; reversing all moves them there (backwards), then each block is fixed.
हिंदी: Reverse से last k elements आगे आ जाते हैं, फिर दोनों हिस्सों को सीधा कर दो।

---

## 📊 Complexity
```
Brute Force: Time O(n·k) | Space O(1)
Extra array: Time O(n)   | Space O(n)
Reversal:    Time O(n)   | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Rotate LEFT by k → reverse(0,k-1), reverse(k,n-1), reverse(0,n-1)
function rotateLeft(nums, k) {
  const n = nums.length;                     // length
  k = k % n;                                 // normalize
  reverse(nums, 0, k - 1);                   // reverse first k
  reverse(nums, k, n - 1);                   // reverse the rest
  reverse(nums, 0, n - 1);                   // reverse everything
  return nums;
}
console.log(rotateLeft([1, 2, 3, 4, 5], 2));     // [ 3, 4, 5, 1, 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting k = k % n  (k=10, n=3 → out of range / wrong result)
// ❌ Wrong: returning a new array when problem says "in place"
// ✅ Correct: normalize k and mutate nums directly
```

---

## 🎯 Interview Tip
Say: "Extra array is O(n) space; the three-reversal trick gives O(1) space." Mention k % n and the empty-array edge case (n = 0 would make k % n NaN).

---

## 🔗 Related Problems
→ D105 (Move Zeroes) | D108 (Valid Palindrome) | D113 (Spiral Matrix)
