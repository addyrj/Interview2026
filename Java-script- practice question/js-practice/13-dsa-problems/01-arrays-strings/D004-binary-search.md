---

# D004. Binary Search (+ Variations)
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #704 | Asked: Every company — must know cold

---

## ❓ Problem
Given a sorted array `nums` and a target, return the index of target. Return -1 if not found. Must be O(log n).

```javascript
binarySearch([-1,0,3,5,9,12], 9);   // 4
binarySearch([-1,0,3,5,9,12], 2);   // -1
binarySearch([5], 5);                // 0
```

---

## 💡 Quick Concept (2 lines only)
Split the search space in half each time. Compare middle element — go left if target < mid, go right if target > mid. O(log n) because we halve the problem every step.
हिंदी: हर step में search space को आधा करो — mid compare करके left या right जाओ। O(log n) time।

---

## ✅ Solution

```javascript
// ============================================
// CLASSIC BINARY SEARCH — O(log n) ✅
// ============================================

function binarySearch(nums, target) {
  let left = 0, right = nums.length - 1;
  
  while (left <= right) {                    // <= because single element is valid
    const mid = left + Math.floor((right - left) / 2);  // avoid overflow
    
    if (nums[mid] === target) return mid;    // found!
    else if (nums[mid] < target) left = mid + 1;   // target is in right half
    else right = mid - 1;                    // target is in left half
  }
  
  return -1;
}

// ============================================
// TEST CASES
// ============================================

console.log(binarySearch([-1,0,3,5,9,12], 9));   // 4
console.log(binarySearch([-1,0,3,5,9,12], 2));   // -1
console.log(binarySearch([5], 5));               // 0
console.log(binarySearch([1,2,3,4,5], 1));       // 0 (first element)
console.log(binarySearch([1,2,3,4,5], 5));       // 4 (last element)

// ============================================
// CRITICAL VARIATIONS — All asked in interviews
// ============================================

// VARIANT 1: First occurrence of target (find LEFTMOST)
function firstOccurrence(nums, target) {
  let left = 0, right = nums.length - 1, result = -1;
  
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);
    if (nums[mid] === target) {
      result = mid;          // found, but keep searching LEFT for earlier occurrence
      right = mid - 1;       // ← key: move right left (not left right)
    } else if (nums[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return result;
}

// VARIANT 2: Last occurrence of target (find RIGHTMOST)
function lastOccurrence(nums, target) {
  let left = 0, right = nums.length - 1, result = -1;
  
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);
    if (nums[mid] === target) {
      result = mid;          // found, but keep searching RIGHT
      left = mid + 1;        // ← key: move left right
    } else if (nums[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return result;
}

// Count occurrences of target:
function countOccurrences(nums, target) {
  const first = firstOccurrence(nums, target);
  if (first === -1) return 0;
  const last = lastOccurrence(nums, target);
  return last - first + 1;
}
console.log(countOccurrences([1,1,2,2,2,3,4], 2));  // 3

// VARIANT 3: Search in Rotated Sorted Array (LeetCode #33)
function searchRotated(nums, target) {
  let left = 0, right = nums.length - 1;
  
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);
    if (nums[mid] === target) return mid;
    
    // Check which half is sorted:
    if (nums[left] <= nums[mid]) {            // left half is sorted
      if (target >= nums[left] && target < nums[mid]) right = mid - 1;
      else left = mid + 1;
    } else {                                  // right half is sorted
      if (target > nums[mid] && target <= nums[right]) left = mid + 1;
      else right = mid - 1;
    }
  }
  return -1;
}
console.log(searchRotated([4,5,6,7,0,1,2], 0));  // 4
console.log(searchRotated([4,5,6,7,0,1,2], 3));  // -1

// VARIANT 4: Find minimum in rotated array (LeetCode #153)
function findMin(nums) {
  let left = 0, right = nums.length - 1;
  while (left < right) {
    const mid = left + Math.floor((right - left) / 2);
    if (nums[mid] > nums[right]) left = mid + 1;  // min is in right half
    else right = mid;                              // min is in left half (or mid)
  }
  return nums[left];
}
console.log(findMin([3,4,5,1,2]));  // 1

// VARIANT 5: Find peak element (LeetCode #162)
function findPeakElement(nums) {
  let left = 0, right = nums.length - 1;
  while (left < right) {
    const mid = left + Math.floor((right - left) / 2);
    if (nums[mid] > nums[mid + 1]) right = mid;  // peak is on left side
    else left = mid + 1;                          // peak is on right side
  }
  return left;
}
```

---

## 🔍 Template to Memorize
```javascript
// Universal Binary Search Template:
function binarySearchTemplate(nums, target) {
  let left = 0, right = nums.length - 1;
  
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);  // safe mid (no overflow)
    
    if (condition(mid)) {
      // Found answer or narrow to left
    } else {
      // Narrow to right
    }
  }
}

// Key decisions:
// 1. left <= right vs left < right (usually <=)
// 2. mid = (l+r)/2  vs  l + (r-l)/2 (use second — no integer overflow)
// 3. left = mid+1 and right = mid-1 (avoid infinite loop with mid)
```
हिंदी: Template याद रखो — left<=right, mid = l+(r-l)/2, condition पर left/right adjust करो।

---

## 📊 Complexity
```
Time:  O(log n) — search space halved each iteration
Space: O(1) iterative | O(log n) recursive (call stack)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mid = (left + right) / 2  — integer overflow for large arrays
const mid = Math.floor((left + right) / 2);  // left + right could overflow 32-bit int
// ✅ Safe: const mid = left + Math.floor((right - left) / 2);

// ❌ Wrong: left = mid (not mid + 1) — infinite loop!
// If left = mid when left === right, loop never exits
// ✅ Always move left = mid + 1, right = mid - 1

// ❌ Wrong: left < right instead of left <= right
// Misses single-element case where left === right === target
```

---

## 🎯 Interview Tip
Say: "Binary search works on any monotonic condition — not just sorted arrays. Template: while(left<=right), safe mid = left+(right-left)/2, move pointers by mid±1 to avoid infinite loops. Rotated sorted array: check which half is sorted, then determine which half target falls in."

---

## 🔗 Related Problems
→ D005 (Search 2D Matrix) | D006 (Koko Eating Bananas) | D007 (Three Sum) | D015 (Sliding Window)
