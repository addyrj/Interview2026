---

# Q106. Implement Merge Sort
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `mergeSort(arr)` that sorts numbers ascending by splitting the array in halves, sorting each, and merging them.

```javascript
mergeSort([38, 27, 43, 3]); // [3, 27, 38, 43]
```

---

## 💡 Quick Concept (2 lines only)
Split until each piece has one item, then merge two sorted pieces into one sorted piece. Always O(n log n) and stable.
हिंदी: Array को आधा-आधा बाँटो, फिर दो sorted हिस्सों को जोड़कर एक sorted बनाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: base case — length <= 1 is already sorted
// Step 2: split in two halves and sort each recursively
// Step 3: merge the two sorted halves

function merge(left, right) {
  const result = [];                          // merged output
  let i = 0, j = 0;                           // pointers for left and right

  while (i < left.length && j < right.length) { // both have items
    if (left[i] <= right[j]) result.push(left[i++]); // smaller from left (<= keeps stable)
    else result.push(right[j++]);             // smaller from right
  }

  return [...result, ...left.slice(i), ...right.slice(j)]; // add leftovers
}

function mergeSort(arr) {
  if (arr.length <= 1) return arr;            // base case

  const mid = Math.floor(arr.length / 2);     // middle index
  const left = mergeSort(arr.slice(0, mid));  // sort left half
  const right = mergeSort(arr.slice(mid));    // sort right half

  return merge(left, right);                  // merge sorted halves
}

// ============================================
// TEST CASES
// ============================================

console.log(mergeSort([38, 27, 43, 3]));   // Expected: [ 3, 27, 38, 43 ]
console.log(mergeSort([5, 1, 5, 2]));      // Expected: [ 1, 2, 5, 5 ]
console.log(mergeSort([1]));               // Expected: [ 1 ]
console.log(mergeSort([]));                // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Merging two already sorted lists needs only one pass comparing the fronts. There are log n levels of splitting, each costing O(n).
हिंदी: दो sorted lists के सामने वाले elements compare करके एक ही pass में merge हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Shorter merge using shift (simple but O(n) per shift)
function mergeSort2(arr) {
  if (arr.length < 2) return arr;                // base case
  const mid = arr.length >> 1;                   // bit shift = floor(len / 2)
  const l = mergeSort2(arr.slice(0, mid));       // left sorted
  const r = mergeSort2(arr.slice(mid));          // right sorted
  const out = [];
  while (l.length && r.length) out.push(l[0] <= r[0] ? l.shift() : r.shift()); // take smaller
  return [...out, ...l, ...r];                   // leftovers
}
console.log(mergeSort2([9, 4, 7])); // Expected: [ 4, 7, 9 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting leftovers after the while loop loses items
return result;

// ✅ Correct: append what remains in either half
return [...result, ...left.slice(i), ...right.slice(j)];
```

---

## 🎯 Interview Tip (1 line)
Say: "Merge sort is guaranteed O(n log n) and stable, but needs O(n) extra space."

---

## 🔗 Related Questions
→ Q105 (quick sort) | Q104 (bubble sort) | Q154 (complete merge sort)
