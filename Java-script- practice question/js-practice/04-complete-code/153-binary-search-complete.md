---

# Q153. Complete Binary Search
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to return the index of `target` in a sorted array, or -1.

```javascript
function binarySearch(arr, target) {
  let lo = 0, hi = arr.length ____ 1;          // last index
  while (lo ____ hi) {                         // search window valid
    const mid = Math.____((lo + hi) / 2);      // middle index
    if (arr[mid] === target) return ____;      // found
    if (arr[mid] < target) lo = mid ____ 1;    // go right
    else hi = mid ____ 1;                      // go left
  }
  return -1;
}
```

---

## 💡 Quick Concept (2 lines only)
Binary search halves the search range each step on a SORTED array, giving O(log n).
हिंदी: Binary search sorted array में हर बार आधा हिस्सा हटाकर O(log n) में खोजता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function binarySearch(arr, target) {
  let lo = 0, hi = arr.length - 1;             // blank 1: inclusive bounds
  while (lo <= hi) {                           // blank 2: window not empty
    const mid = Math.floor((lo + hi) / 2);     // blank 3: middle index
    if (arr[mid] === target) return mid;       // blank 4: found
    if (arr[mid] < target) lo = mid + 1;       // blank 5: discard left half
    else hi = mid - 1;                         // blank 6: discard right half
  }
  return -1;                                   // not found
}

// ============================================
// TEST CASES
// ============================================

console.log(binarySearch([1, 3, 5, 7, 9], 7));  // Expected: 3
console.log(binarySearch([1, 3, 5, 7, 9], 4));  // Expected: -1
console.log(binarySearch([], 1));               // Expected: -1
```

---

## 🔍 Why This Works (3 lines max)
Comparing with the middle tells which half can contain the target, so the other half is skipped. The window shrinks until found or empty.
हिंदी: middle से compare करके एक आधा हिस्सा छोड़ दिया जाता है, window खाली होने पर -1।

---

## ⚡ Alternative Solution
```javascript
// Recursive
const bs = (a, t, lo = 0, hi = a.length - 1) => {
  if (lo > hi) return -1;
  const m = (lo + hi) >> 1;
  return a[m] === t ? m : a[m] < t ? bs(a, t, m + 1, hi) : bs(a, t, lo, m - 1);
};
console.log(bs([1, 2, 3], 3)); // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: while (lo < hi) skips the single-element case; lo = mid causes infinite loop
// ✅ Correct: lo <= hi with mid + 1 / mid - 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Array must be sorted; O(log n) time, O(1) space — watch off-by-one on bounds."

---

## 🔗 Related Questions
→ Q103 (binary search) | Q126 (infinite loop) | Q154 (complete merge sort)
