---

# Q056. Find Max in Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `findMax(arr)` that returns the largest number in an array without using `Math.max`. Return `undefined` for an empty array.

```javascript
findMax([3, 9, 2, 7]); // 9
```

---

## 💡 Quick Concept (2 lines only)
Keep a running "max so far" and update it whenever you see a bigger value.
हिंदी: एक max variable रखो और हर बड़ी value मिलने पर उसे update करते जाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle empty array
// Step 2: start with the first element as max
// Step 3: scan the rest and update max

function findMax(arr) {
  if (arr.length === 0) return undefined; // nothing to compare
  let max = arr[0];                       // assume first is max
  for (let i = 1; i < arr.length; i++) {  // check remaining items
    if (arr[i] > max) max = arr[i];       // bigger found -> update
  }
  return max;                             // largest value
}

// ============================================
// TEST CASES
// ============================================

console.log(findMax([3, 9, 2, 7]));    // Expected: 9
console.log(findMax([-5, -1, -9]));    // Expected: -1
console.log(findMax([42]));            // Expected: 42
console.log(findMax([]));              // Expected: undefined
```

---

## 🔍 Why This Works (3 lines max)
Every element is compared once against the best seen so far, so the final value is the largest. Starting from `arr[0]` (not 0) keeps negative arrays correct.
हिंदी: हर element को अब तक के सबसे बड़े से compare किया जाता है, इसलिए आखिर में सबसे बड़ा बचता है।

---

## ⚡ Alternative Solution
```javascript
// reduce version
const maxR = (arr) => arr.reduce((m, x) => (x > m ? x : m), -Infinity); // start from -Infinity
console.log(maxR([3, 9, 2, 7])); // Expected: 9
// Math.max with spread (fails on huge arrays)
console.log(Math.max(...[3, 9, 2, 7])); // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: starting max at 0 breaks all-negative arrays
let max = 0;
for (const n of [-5, -1, -9]) if (n > max) max = n;
console.log(max); // 0 (wrong!)
// ✅ Correct: start from first element or -Infinity
console.log([-5, -1, -9].reduce((m, x) => Math.max(m, x), -Infinity)); // -1
```

---

## 🎯 Interview Tip (1 line)
Call out the empty-array and all-negative edge cases, and that `Math.max(...arr)` can overflow the stack for very large arrays.

---

## 🔗 Related Questions
→ Q057 (find min) | Q114 (implement reduce) | Q065 (sort objects)
