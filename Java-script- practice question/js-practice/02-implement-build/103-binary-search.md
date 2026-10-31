---

# Q103. Implement Binary Search
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `binarySearch(arr, target)` for a SORTED array. Return the index of `target`, or `-1` if not found.

```javascript
binarySearch([1, 3, 5, 7, 9], 7); // 3
```

---

## 💡 Quick Concept (2 lines only)
Compare target with the middle element and throw away half the array each time. Time is O(log n) but the array must be sorted.
हिंदी: हर बार बीच का element देखकर आधा array छोड़ देते हैं — इसलिए बहुत तेज़ है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep low and high boundaries
// Step 2: check the middle element
// Step 3: move low or high to shrink the range

function binarySearch(arr, target) {
  let low = 0;                              // left boundary
  let high = arr.length - 1;                // right boundary

  while (low <= high) {                     // range still valid
    const mid = Math.floor((low + high) / 2); // middle index
    if (arr[mid] === target) return mid;    // found it
    if (arr[mid] < target) low = mid + 1;   // target is in right half
    else high = mid - 1;                    // target is in left half
  }

  return -1;                                // not found
}

// ============================================
// TEST CASES
// ============================================

console.log(binarySearch([1, 3, 5, 7, 9], 7));   // Expected: 3
console.log(binarySearch([1, 3, 5, 7, 9], 1));   // Expected: 0
console.log(binarySearch([1, 3, 5, 7, 9], 4));   // Expected: -1
console.log(binarySearch([], 5));                // Expected: -1
```

---

## 🔍 Why This Works (3 lines max)
The sorted order lets us decide which half can contain the target, so each step halves the search space: O(log n).
हिंदी: Sorted होने की वजह से पता चल जाता है कि target किस आधे हिस्से में है।

---

## ⚡ Alternative Solution
```javascript
// Recursive version
function binarySearchRec(arr, target, low = 0, high = arr.length - 1) {
  if (low > high) return -1;                         // base case: not found
  const mid = low + Math.floor((high - low) / 2);    // overflow-safe mid
  if (arr[mid] === target) return mid;               // found
  return arr[mid] < target
    ? binarySearchRec(arr, target, mid + 1, high)    // search right
    : binarySearchRec(arr, target, low, mid - 1);    // search left
}
console.log(binarySearchRec([2, 4, 6, 8], 8)); // Expected: 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `low < high` skips the last remaining element, and `high = mid` can loop forever
while (low < high) { /* ... */ }

// ✅ Correct: use `low <= high` with mid + 1 / mid - 1
while (low <= high) { /* ... */ }
```

---

## 🎯 Interview Tip (1 line)
Always say "array must be sorted" first, then state O(log n) time and O(1) space for the iterative version.

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q106 (merge sort) | Q153 (complete binary search)
