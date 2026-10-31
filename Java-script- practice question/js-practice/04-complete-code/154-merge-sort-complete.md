---

# Q154. Complete Merge Sort
# Category: Complete the Code
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Fill in the blanks for merge sort.

```javascript
function mergeSort(arr) {
  if (arr.length <= ____) return arr;              // base case
  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.____(0, mid));        // sort left half
  const right = mergeSort(arr.slice(____));        // sort right half
  return merge(left, right);
}
function merge(a, b) {
  const out = []; let i = 0, j = 0;
  while (i < a.length && j < b.length) {
    out.push(a[i] ____ b[j] ? a[i++] : b[j++]);   // take smaller
  }
  return out.concat(a.slice(i), b.____(j));        // leftovers
}
```

---

## 💡 Quick Concept (2 lines only)
Merge sort splits the array in halves, sorts each recursively, then merges two sorted halves. Always O(n log n).
हिंदी: Merge sort array को आधा-आधा बाँटता है, सॉर्ट करता है और फिर दो sorted हिस्सों को जोड़ता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function mergeSort(arr) {
  if (arr.length <= 1) return arr;                 // blank 1: 0/1 items already sorted
  const mid = Math.floor(arr.length / 2);          // Step 1: split point
  const left = mergeSort(arr.slice(0, mid));       // blank 2: sort left half
  const right = mergeSort(arr.slice(mid));         // blank 3: sort right half
  return merge(left, right);                       // Step 2: combine
}

function merge(a, b) {
  const out = [];                                  // result array
  let i = 0, j = 0;                                // pointers for a and b
  while (i < a.length && j < b.length) {
    out.push(a[i] <= b[j] ? a[i++] : b[j++]);      // blank 4: <= keeps sort stable
  }
  return out.concat(a.slice(i), b.slice(j));       // blank 5: append remaining items
}

// ============================================
// TEST CASES
// ============================================

console.log(mergeSort([5, 2, 9, 1, 5, 6]));        // Expected: [ 1, 2, 5, 5, 6, 9 ]
console.log(mergeSort([]));                        // Expected: []
console.log(mergeSort([3]));                       // Expected: [ 3 ]
```

---

## 🔍 Why This Works (3 lines max)
Single elements are sorted by definition. Merging two sorted lists only needs comparing the front of each, giving linear merge and O(n log n) overall.
हिंदी: दो sorted lists को merge करना सिर्फ सामने के elements की तुलना है, इसलिए तेज़ है।

---

## ⚡ Alternative Solution
```javascript
// Built-in sort with comparator
console.log([5, 2, 9, 1].sort((a, b) => a - b)); // [ 1, 2, 5, 9 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: base case missing -> infinite recursion
// ❌ Wrong: forgetting leftovers after the while loop loses elements
// ✅ Correct: concat both remaining slices
```

---

## 🎯 Interview Tip (1 line)
Say: "O(n log n) always, stable, O(n) extra space — good for linked lists and external sorting."

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q105 (quick sort) | Q106 (merge sort) | Q153 (binary search)
