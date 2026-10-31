---

# Q070. Array Rotation
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `rotate(arr, k)` that rotates an array to the RIGHT by `k` steps and returns a new array. `k` can be larger than the length or negative (left rotation).

```javascript
rotate([1, 2, 3, 4, 5], 2); // [4, 5, 1, 2, 3]
```

---

## 💡 Quick Concept (2 lines only)
Normalize `k` with modulo, then move the last `k` items to the front using slice.
हिंदी: k को length से mod करो, फिर आखिरी k elements को आगे लगा दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle empty array
// Step 2: normalize k (works for k > length and negatives)
// Step 3: last k items + the rest

function rotate(arr, k) {
  const n = arr.length;                     // array length
  if (n === 0) return [];                   // nothing to rotate
  const steps = ((k % n) + n) % n;          // normalize to 0..n-1
  if (steps === 0) return [...arr];         // no change needed
  return [...arr.slice(-steps), ...arr.slice(0, n - steps)]; // tail first, then head
}

// ============================================
// TEST CASES
// ============================================

console.log(rotate([1, 2, 3, 4, 5], 2));    // Expected: [ 4, 5, 1, 2, 3 ]
console.log(rotate([1, 2, 3, 4, 5], 7));    // Expected: [ 4, 5, 1, 2, 3 ]
console.log(rotate([1, 2, 3, 4, 5], -1));   // Expected: [ 2, 3, 4, 5, 1 ]
console.log(rotate([], 3));                 // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Rotating by n returns the same array, so `k % n` removes useless full turns; the double-modulo fixes negative k. Slices then rebuild the array in the new order.
हिंदी: पूरा चक्कर बेकार होता है, इसलिए k % n लेते हैं और slice से नया क्रम बनाते हैं।

---

## ⚡ Alternative Solution
```javascript
// In-place with the reverse trick (O(1) extra space)
function rotateInPlace(arr, k) {
  const n = arr.length;                         // length
  k = ((k % n) + n) % n;                        // normalize
  const rev = (l, r) => {                       // reverse arr[l..r]
    while (l < r) { [arr[l], arr[r]] = [arr[r], arr[l]]; l++; r--; }
  };
  rev(0, n - 1);                                // reverse all
  rev(0, k - 1);                                // reverse first k
  rev(k, n - 1);                                // reverse the rest
  return arr;                                   // rotated array
}
console.log(rotateInPlace([1, 2, 3, 4, 5], 2)); // Expected: [ 4, 5, 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: slice(-0) returns the whole array
console.log([1, 2, 3].slice(-0)); // [ 1, 2, 3 ]  (breaks when k % n === 0)
// ✅ Correct: return early when steps === 0 (as in solution)
console.log(rotate([1, 2, 3], 3)); // [ 1, 2, 3 ]
```

---

## 🎯 Interview Tip (1 line)
Show the slice version first, then the 3-reverse in-place trick for O(1) space.

---

## 🔗 Related Questions
→ Q060 (chunk) | Q051 (reverse string) | Q106 (merge sort)
