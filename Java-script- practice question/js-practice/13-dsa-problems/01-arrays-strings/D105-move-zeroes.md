---

# D105. Move Zeroes
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #283 | Asked: Facebook, Amazon, Apple, Zomato

---

## ❓ Problem
Move all 0s to the end of `nums` while keeping the relative order of non-zero elements. Do it in place.

```
Input:  [0, 1, 0, 3, 12]
Output: [1, 3, 12, 0, 0]
```

---

## 💡 Quick Concept (2 lines only)
Keep a write pointer for the next non-zero slot. Scan; whenever you see a non-zero, swap it into the write position and advance.
हिंदी: Non-zero को आगे लाते जाओ, zeros अपने आप पीछे चले जाते हैं।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Extra array — O(n) time, O(n) space
// ============================================

function moveZeroesExtra(nums) {
  const nonZero = nums.filter((x) => x !== 0);       // keep non-zeros in order
  const zeros = new Array(nums.length - nonZero.length).fill(0); // zeros to append
  const result = [...nonZero, ...zeros];             // non-zeros then zeros
  for (let i = 0; i < nums.length; i++) nums[i] = result[i]; // copy back in place
  return nums;
}

// ============================================
// APPROACH 2: Two pointers with swap — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function moveZeroes(nums) {
  let write = 0;                                     // next slot for a non-zero
  for (let read = 0; read < nums.length; read++) {   // scan every element
    if (nums[read] !== 0) {                          // found a non-zero
      [nums[write], nums[read]] = [nums[read], nums[write]]; // swap into place
      write++;                                       // advance write slot
    }
  }
  return nums;                                       // modified in place
}

// ============================================
// TEST CASES
// ============================================

console.log(moveZeroes([0, 1, 0, 3, 12]));           // [ 1, 3, 12, 0, 0 ]
console.log(moveZeroes([0]));                        // [ 0 ]
console.log(moveZeroes([1, 2, 3]));                  // [ 1, 2, 3 ]
console.log(moveZeroes([0, 0, 1]));                  // [ 1, 0, 0 ]
console.log(moveZeroes([]));                         // []
console.log(moveZeroesExtra([4, 0, 5, 0]));          // [ 4, 5, 0, 0 ]
```

---

## 🔍 Why It Works
```
[0,1,0,3,12]  write=0
read=0 (0) skip
read=1 (1) swap(0,1) → [1,0,0,3,12] write=1
read=2 (0) skip
read=3 (3) swap(1,3) → [1,3,0,0,12] write=2
read=4 (12) swap(2,4)→ [1,3,12,0,0] write=3
```
Everything before `write` is non-zero and in original order.
हिंदी: `write` के पहले का हिस्सा हमेशा non-zero और सही order में रहता है।

---

## 📊 Complexity
```
Extra array: Time O(n) | Space O(n)
Two pointer: Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Remove Element (LeetCode #27) — remove all of value val, return new length
function removeElement(nums, val) {
  let write = 0;                                     // next keep position
  for (const x of nums) {                            // scan
    if (x !== val) nums[write++] = x;                // keep only non-val
  }
  return write;                                      // new length
}
console.log(removeElement([3, 2, 2, 3], 3));         // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: splice inside a loop while indexing forward — skips elements and is O(n²)
// ❌ Wrong: returning a new array (problem asks in-place)
// ✅ Correct: single pass with a write pointer
```

---

## 🎯 Interview Tip
Say: "Two pointers, one pass, minimal writes. A swap-free version writes non-zeros forward then fills zeros — both are O(n)." Order of non-zeros must stay stable.

---

## 🔗 Related Problems
→ D104 (Rotate Array) | D108 (Valid Palindrome) | D004 (Binary Search)
