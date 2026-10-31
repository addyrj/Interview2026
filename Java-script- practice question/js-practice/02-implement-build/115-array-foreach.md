---

# Q115. Implement Array.forEach
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `Array.prototype.myForEach(callback, thisArg)` that calls `callback(item, index, array)` for every element and returns `undefined`.

```javascript
[1, 2].myForEach(x => console.log(x)); // 1, 2
```

---

## 💡 Quick Concept (2 lines only)
Loop and call the callback for side effects only. It returns nothing and cannot be stopped with `break`.
हिंदी: हर element पर callback चलता है, कुछ return नहीं होता और बीच में रोक नहीं सकते।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate callback
// Step 2: loop over present items
// Step 3: call callback with thisArg, return nothing

Array.prototype.myForEach = function (callback, thisArg) {
  if (typeof callback !== 'function') {
    throw new TypeError(`${callback} is not a function`); // same as native
  }
  const len = this.length;                       // length is fixed at start (like native)
  for (let i = 0; i < len; i++) {                // visit every index
    if (i in this) {                             // skip holes in sparse arrays
      callback.call(thisArg, this[i], i, this);  // item, index, array
    }
  }
  // no return -> undefined
};

// ============================================
// TEST CASES
// ============================================

[10, 20].myForEach((x, i) => console.log(i, x));   // Expected: 0 10  then  1 20

const sum = { total: 0 };                          // object to collect into
[1, 2, 3].myForEach(function (x) { this.total += x; }, sum); // thisArg = sum
console.log(sum.total);                            // Expected: 6

console.log([1, 2].myForEach(x => x));             // Expected: undefined

const sparse = [1, , 3];                           // has an empty slot
const seen = [];
sparse.myForEach(x => seen.push(x));
console.log(seen);                                 // Expected: [ 1, 3 ]
```

---

## 🔍 Why This Works (3 lines max)
`forEach` only runs side effects, so it returns nothing. Reading `length` once and checking `i in this` copies the native behaviour for sparse arrays.
हिंदी: forEach सिर्फ काम करवाता है, कुछ लौटाता नहीं, और खाली slots को छोड़ देता है।

---

## ⚡ Alternative Solution
```javascript
// Using for...of with entries() (does NOT skip holes, so slightly different)
Array.prototype.myForEach2 = function (cb, thisArg) {
  for (const [i, item] of this.entries()) {   // index + item pairs
    cb.call(thisArg, item, i, this);
  }
};
[7].myForEach2(x => console.log(x));          // Expected: 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting break/return to stop forEach
[1, 2, 3].forEach(x => { if (x === 2) return; console.log(x); }); // return only skips, prints 1 and 3

// ✅ Correct: use a for...of loop (or some/every) when you need to stop early
for (const x of [1, 2, 3]) { if (x === 2) break; console.log(x); } // prints 1
```

---

## 🎯 Interview Tip (1 line)
Say: "forEach returns undefined, can't be broken, and doesn't wait for async callbacks."

---

## 🔗 Related Questions
→ Q112 (map) | Q113 (filter) | Q299 (map vs forEach vs filter vs reduce)
