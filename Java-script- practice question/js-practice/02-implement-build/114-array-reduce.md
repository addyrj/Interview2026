---

# Q114. Implement Array.reduce
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `Array.prototype.myReduce(callback, initialValue)` that folds an array into a single value. Callback gets `(acc, item, index, array)`.

```javascript
[1, 2, 3].myReduce((a, b) => a + b, 0); // 6
```

---

## 💡 Quick Concept (2 lines only)
Keep an accumulator; for each item, replace it with `callback(acc, item)`. Without an initial value, the first item becomes the accumulator.
हिंदी: एक accumulator रखो और हर item के साथ उसे update करते जाओ, अंत में एक ही value मिलती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate callback
// Step 2: decide start index and initial accumulator
// Step 3: loop and update accumulator, then return it

Array.prototype.myReduce = function (callback, initialValue) {
  if (typeof callback !== 'function') {
    throw new TypeError(`${callback} is not a function`); // same as native
  }
  let acc;                                      // accumulator
  let start;                                    // first index to process
  if (arguments.length >= 2) {                  // initial value was provided (even undefined)
    acc = initialValue;
    start = 0;
  } else {
    if (this.length === 0) {
      throw new TypeError('Reduce of empty array with no initial value'); // native error
    }
    acc = this[0];                              // first item is the start value
    start = 1;                                  // skip it in loop
  }
  for (let i = start; i < this.length; i++) {   // walk remaining items
    if (i in this) acc = callback(acc, this[i], i, this); // update accumulator
  }
  return acc;                                   // final single value
};

// ============================================
// TEST CASES
// ============================================

console.log([1, 2, 3].myReduce((a, b) => a + b, 0));        // Expected: 6
console.log([1, 2, 3].myReduce((a, b) => a * b));           // Expected: 6
console.log([[1], [2, 3]].myReduce((a, b) => a.concat(b), [])); // Expected: [ 1, 2, 3 ]
console.log(['a', 'b', 'a'].myReduce((m, x) => ({ ...m, [x]: (m[x] || 0) + 1 }), {})); // Expected: { a: 2, b: 1 }

try { [].myReduce((a, b) => a + b); }                       // empty + no initial
catch (e) { console.log(e.message); }                       // Expected: Reduce of empty array with no initial value
```

---

## 🔍 Why This Works (3 lines max)
`arguments.length` tells us whether an initial value was truly passed, even if it was `undefined`. Starting at index 1 avoids using the first item twice.
हिंदी: `arguments.length` से पता चलता है कि initial value दी गई या नहीं, और बिना दिए पहला item ही शुरुआत बनता है।

---

## ⚡ Alternative Solution
```javascript
// Recursive version
function reduceRec(arr, cb, acc, i = 0) {
  if (i >= arr.length) return acc;                   // done
  return reduceRec(arr, cb, cb(acc, arr[i], i, arr), i + 1); // update + recurse
}
console.log(reduceRec([1, 2, 3], (a, b) => a + b, 0)); // Expected: 6
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `initialValue ? ...` treats 0 / '' / false as "not provided"
let acc = initialValue ? initialValue : this[0];

// ✅ Correct: check how many arguments were passed
if (arguments.length >= 2) acc = initialValue;
```

---

## 🎯 Interview Tip (1 line)
Mention the empty-array TypeError and that reduce can implement map, filter and more.

---

## 🔗 Related Questions
→ Q112 (map) | Q113 (filter) | Q085 (compose) | Q066 (count occurrences)
