---

# Q104. Implement Bubble Sort
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `bubbleSort(arr)` that sorts numbers in ascending order by repeatedly swapping adjacent elements that are out of order. Do not mutate the input.

```javascript
bubbleSort([5, 2, 9, 1]); // [1, 2, 5, 9]
```

---

## 💡 Quick Concept (2 lines only)
Compare neighbours and swap if the left is bigger; after each pass the largest value "bubbles" to the end. Time O(n²), simple but slow.
हिंदी: पास-पास के elements compare करके swap करते हैं, हर round में सबसे बड़ा अंत में पहुँच जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: copy the array so the original stays safe
// Step 2: outer loop = passes, inner loop = compare neighbours
// Step 3: stop early if a pass made no swap

function bubbleSort(arr) {
  const a = [...arr];                         // copy, avoid mutating input

  for (let i = 0; i < a.length - 1; i++) {    // each pass
    let swapped = false;                      // track swaps in this pass

    for (let j = 0; j < a.length - 1 - i; j++) { // last i items already sorted
      if (a[j] > a[j + 1]) {                  // out of order?
        [a[j], a[j + 1]] = [a[j + 1], a[j]];  // swap neighbours
        swapped = true;                       // remember we swapped
      }
    }

    if (!swapped) break;                      // already sorted -> stop early
  }

  return a;                                   // sorted copy
}

// ============================================
// TEST CASES
// ============================================

console.log(bubbleSort([5, 2, 9, 1]));     // Expected: [ 1, 2, 5, 9 ]
console.log(bubbleSort([3, 3, 1]));        // Expected: [ 1, 3, 3 ]
console.log(bubbleSort([1, 2, 3]));        // Expected: [ 1, 2, 3 ]
console.log(bubbleSort([]));               // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Each pass pushes the biggest unsorted element to its final spot. The `swapped` flag gives O(n) on already sorted input.
हिंदी: हर pass में सबसे बड़ा element अपनी सही जगह पहुँच जाता है, swap न हो तो रुक जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// While-loop version with do/while
function bubbleSort2(arr) {
  const a = [...arr];                         // copy
  let swapped;                                // flag
  do {
    swapped = false;                          // reset each round
    for (let i = 0; i < a.length - 1; i++) {
      if (a[i] > a[i + 1]) {                  // compare neighbours
        [a[i], a[i + 1]] = [a[i + 1], a[i]];  // swap
        swapped = true;
      }
    }
  } while (swapped);                          // repeat until no swaps
  return a;
}
console.log(bubbleSort2([4, 1, 3])); // Expected: [ 1, 3, 4 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: default .sort() compares as strings
[10, 9, 1].sort();            // [1, 10, 9]

// ✅ Correct: pass a numeric comparator
[10, 9, 1].sort((a, b) => a - b); // [1, 9, 10]
```

---

## 🎯 Interview Tip (1 line)
Say: "Bubble sort is O(n²), stable, in-place; I'd use merge/quick sort for real data."

---

## 🔗 Related Questions
→ Q105 (quick sort) | Q106 (merge sort) | Q065 (sort array of objects)
