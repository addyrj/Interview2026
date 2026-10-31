---

# Q105. Implement Quick Sort
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `quickSort(arr)` that sorts numbers ascending using the divide-and-conquer quick sort algorithm.

```javascript
quickSort([5, 2, 9, 1, 5]); // [1, 2, 5, 5, 9]
```

---

## 💡 Quick Concept (2 lines only)
Pick a pivot, put smaller items on its left and bigger on its right, then sort both sides recursively. Average O(n log n), worst O(n²).
हिंदी: एक pivot चुनो, छोटे बाएँ और बड़े दाएँ रखो, फिर दोनों तरफ यही दोहराओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: base case — 0 or 1 items are already sorted
// Step 2: choose pivot and partition into left / equal / right
// Step 3: recursively sort left and right, then join

function quickSort(arr) {
  if (arr.length <= 1) return arr;               // base case

  const pivot = arr[Math.floor(arr.length / 2)]; // pick middle as pivot
  const left = arr.filter(x => x < pivot);       // smaller than pivot
  const equal = arr.filter(x => x === pivot);    // same as pivot (handles duplicates)
  const right = arr.filter(x => x > pivot);      // greater than pivot

  return [...quickSort(left), ...equal, ...quickSort(right)]; // sort sides + join
}

// ============================================
// TEST CASES
// ============================================

console.log(quickSort([5, 2, 9, 1, 5]));   // Expected: [ 1, 2, 5, 5, 9 ]
console.log(quickSort([3, 2, 1]));         // Expected: [ 1, 2, 3 ]
console.log(quickSort([7]));               // Expected: [ 7 ]
console.log(quickSort([]));                // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
After partitioning, the pivot group is already in its final place, so only the two sides need sorting. Splitting evenly gives about log n levels.
हिंदी: Partition के बाद pivot अपनी सही जगह पर होता है, बस दोनों तरफ sort करना बचता है।

---

## ⚡ Alternative Solution
```javascript
// In-place version (Lomuto partition) — O(1) extra space
function quickSortInPlace(a, lo = 0, hi = a.length - 1) {
  if (lo >= hi) return a;                        // base case
  const pivot = a[hi];                           // last element as pivot
  let i = lo;                                    // boundary of smaller items
  for (let j = lo; j < hi; j++) {
    if (a[j] < pivot) {                          // smaller than pivot
      [a[i], a[j]] = [a[j], a[i]];               // move to the left zone
      i++;
    }
  }
  [a[i], a[hi]] = [a[hi], a[i]];                 // put pivot in final place
  quickSortInPlace(a, lo, i - 1);                // sort left part
  quickSortInPlace(a, i + 1, hi);                // sort right part
  return a;
}
console.log(quickSortInPlace([4, 1, 3, 2])); // Expected: [ 1, 2, 3, 4 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only < and >= partition with the pivot included -> infinite recursion on duplicates
const right = arr.filter(x => x >= pivot);   // pivot goes right every time, never shrinks

// ✅ Correct: keep equal items in a separate bucket
const equal = arr.filter(x => x === pivot);
```

---

## 🎯 Interview Tip (1 line)
Mention average O(n log n), worst O(n²) with bad pivots, and that a random/median pivot avoids it.

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q106 (merge sort) | Q103 (binary search)
