---

# Q113. Implement Array.filter
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `Array.prototype.myFilter(callback, thisArg)` that returns a NEW array containing only the items for which `callback(item, index, array)` returns a truthy value.

```javascript
[1, 2, 3, 4].myFilter(x => x % 2 === 0); // [2, 4]
```

---

## 💡 Quick Concept (2 lines only)
Loop through the array, keep an item only if the callback says "true". Result can be shorter than the original.
हिंदी: हर item पर callback चलाओ, जो true दे सिर्फ वही नए array में रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate callback
// Step 2: loop and test every present item
// Step 3: push item into result when callback is truthy

Array.prototype.myFilter = function (callback, thisArg) {
  if (typeof callback !== 'function') {
    throw new TypeError(`${callback} is not a function`); // same as native
  }
  const result = [];                           // output array
  for (let i = 0; i < this.length; i++) {      // walk the array
    if (i in this && callback.call(thisArg, this[i], i, this)) { // present + truthy
      result.push(this[i]);                    // keep the ORIGINAL item
    }
  }
  return result;                               // filtered copy
};

// ============================================
// TEST CASES
// ============================================

console.log([1, 2, 3, 4].myFilter(x => x % 2 === 0));          // Expected: [ 2, 4 ]
console.log(['a', '', 'b'].myFilter(Boolean));                 // Expected: [ 'a', 'b' ]
console.log([5, 6, 7].myFilter((x, i) => i > 0));              // Expected: [ 6, 7 ]
console.log([1, 2].myFilter(x => x > 10));                     // Expected: []

const users = [{ n: 'A', age: 20 }, { n: 'B', age: 15 }];
console.log(users.myFilter(u => u.age >= 18));                 // Expected: [ { n: 'A', age: 20 } ]
```

---

## 🔍 Why This Works (3 lines max)
The callback acts as a yes/no test. We push the original item (not the callback result), so the output keeps the original values and references.
हिंदी: Callback सिर्फ हाँ/ना बताता है, और हम original item ही result में डालते हैं।

---

## ⚡ Alternative Solution
```javascript
// Using reduce
Array.prototype.myFilter2 = function (cb, thisArg) {
  return this.reduce((acc, item, i, arr) => {
    if (cb.call(thisArg, item, i, arr)) acc.push(item); // keep when truthy
    return acc;
  }, []);
};
console.log([1, 2, 3].myFilter2(x => x > 1)); // Expected: [ 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: pushing the callback's result instead of the item
result.push(callback(this[i]));   // pushes true/false

// ✅ Correct: push the item itself
if (callback(this[i])) result.push(this[i]);
```

---

## 🎯 Interview Tip (1 line)
Say: "filter returns a new array, never mutates, and uses truthiness of the callback result."

---

## 🔗 Related Questions
→ Q112 (map) | Q114 (reduce) | Q116 (find) | Q068 (remove falsy values)
