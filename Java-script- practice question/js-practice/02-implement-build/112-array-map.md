---

# Q112. Implement Array.map
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `Array.prototype.myMap(callback, thisArg)` that returns a NEW array with the result of calling `callback(item, index, array)` on every element.

```javascript
[1, 2, 3].myMap(x => x * 2); // [2, 4, 6]
```

---

## 💡 Quick Concept (2 lines only)
Loop over the array, call the callback for each item, push the return value into a new array. Original array is never changed.
हिंदी: हर element पर callback चलाओ और नतीजे नए array में रखो — पुराना array वैसा ही रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate callback
// Step 2: loop and call callback with (item, index, array)
// Step 3: store each result in a new array and return it

Array.prototype.myMap = function (callback, thisArg) {
  if (typeof callback !== 'function') {
    throw new TypeError(`${callback} is not a function`); // same as native
  }
  const result = new Array(this.length);       // keep same length (holes stay holes)
  for (let i = 0; i < this.length; i++) {      // `this` is the array
    if (i in this) {                           // skip empty slots like native map
      result[i] = callback.call(thisArg, this[i], i, this); // item, index, array
    }
  }
  return result;                               // new array
};

// ============================================
// TEST CASES
// ============================================

console.log([1, 2, 3].myMap(x => x * 2));              // Expected: [ 2, 4, 6 ]
console.log(['a', 'b'].myMap((x, i) => x + i));        // Expected: [ 'a0', 'b1' ]
console.log([].myMap(x => x));                         // Expected: []

const arr = [1, 2, 3];
const out = arr.myMap(x => x + 1);
console.log(arr, out);                                 // Expected: [ 1, 2, 3 ] [ 2, 3, 4 ]

console.log([1, 2].myMap(function (x) { return x * this.k; }, { k: 10 })); // Expected: [ 10, 20 ]
```

---

## 🔍 Why This Works (3 lines max)
`this` inside a prototype method is the array itself. `callback.call(thisArg, ...)` supports the optional `this` argument, and `i in this` mimics native handling of sparse arrays.
हिंदी: prototype method में `this` खुद array होता है, इसलिए उस पर loop चला सकते हैं।

---

## ⚡ Alternative Solution
```javascript
// Using reduce
Array.prototype.myMap2 = function (cb, thisArg) {
  return this.reduce((acc, item, i, arr) => {
    acc.push(cb.call(thisArg, item, i, arr));  // push transformed item
    return acc;                                // pass accumulator on
  }, []);
};
console.log([1, 2, 3].myMap2(x => x * x)); // Expected: [ 1, 4, 9 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow function as prototype method -> `this` is not the array
Array.prototype.myMap = (cb) => { /* this.length fails */ };

// ✅ Correct: use a normal function
Array.prototype.myMap = function (cb) { /* this = array */ };
```

---

## 🎯 Interview Tip (1 line)
Pass `(item, index, array)` and support `thisArg` — most candidates forget index and array.

---

## 🔗 Related Questions
→ Q113 (filter) | Q114 (reduce) | Q115 (forEach) | Q299 (map vs forEach vs filter vs reduce)
