---

# Q057. Find Min in Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `findMin(arr)` that returns the smallest number in an array without using `Math.min`. Return `undefined` for an empty array.

```javascript
findMin([3, 9, 2, 7]); // 2
```

---

## 💡 Quick Concept (2 lines only)
Keep a running "min so far" and replace it whenever a smaller value appears.
हिंदी: एक min variable रखो और छोटी value मिलते ही उसे बदल दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle empty array
// Step 2: start with first element as min
// Step 3: scan the rest and update min

function findMin(arr) {
  if (arr.length === 0) return undefined; // nothing to compare
  let min = arr[0];                       // assume first is min
  for (let i = 1; i < arr.length; i++) {  // check remaining items
    if (arr[i] < min) min = arr[i];       // smaller found -> update
  }
  return min;                             // smallest value
}

// ============================================
// TEST CASES
// ============================================

console.log(findMin([3, 9, 2, 7]));   // Expected: 2
console.log(findMin([-5, -1, -9]));   // Expected: -9
console.log(findMin([8]));            // Expected: 8
console.log(findMin([]));             // Expected: undefined
```

---

## 🔍 Why This Works (3 lines max)
Each element is compared once with the smallest so far, giving O(n) time and O(1) space. Starting from `arr[0]` avoids wrong results for large positive numbers.
हिंदी: हर element को अब तक के सबसे छोटे से compare करते हैं, आखिर में सबसे छोटा मिलता है।

---

## ⚡ Alternative Solution
```javascript
// reduce version
const minR = (arr) => arr.reduce((m, x) => (x < m ? x : m), Infinity); // start from Infinity
console.log(minR([3, 9, 2, 7])); // Expected: 2
// sort version (O(n log n), mutates -> copy first)
console.log([...[3, 9, 2, 7]].sort((a, b) => a - b)[0]); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: default sort is string based
console.log([10, 9, 1].sort()[0]);           // 1 (works by luck)
console.log([10, 9, 2].sort()[0]);           // 10 (wrong! '10' < '2')
// ✅ Correct: numeric comparator
console.log([10, 9, 2].sort((a, b) => a - b)[0]); // 2
```

---

## 🎯 Interview Tip (1 line)
Prefer the single-pass O(n) loop over sorting, and mention empty array handling.

---

## 🔗 Related Questions
→ Q056 (find max) | Q065 (sort objects) | Q114 (implement reduce)
