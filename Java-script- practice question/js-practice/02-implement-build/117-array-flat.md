---

# Q117. Implement Array.flat
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `Array.prototype.myFlat(depth = 1)` that flattens nested arrays up to the given depth. `Infinity` flattens everything.

```javascript
[1, [2, [3]]].myFlat();         // [1, 2, [3]]
[1, [2, [3]]].myFlat(Infinity); // [1, 2, 3]
```

---

## 💡 Quick Concept (2 lines only)
For every item: if it is an array and depth is left, flatten it with `depth - 1`; otherwise push as is.
हिंदी: Array मिले और depth बाकी हो तो उसे खोलो, वरना item जैसा है वैसा रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: default depth is 1
// Step 2: loop items; recurse into arrays while depth > 0
// Step 3: collect everything into one result array

Array.prototype.myFlat = function (depth = 1) {
  const result = [];                             // flattened output
  for (let i = 0; i < this.length; i++) {        // walk the array
    if (!(i in this)) continue;                  // flat() removes holes
    const item = this[i];                        // current item
    if (Array.isArray(item) && depth > 0) {      // nested and allowed to go deeper
      result.push(...item.myFlat(depth - 1));    // flatten one level less
    } else {
      result.push(item);                         // keep as is
    }
  }
  return result;                                 // new array
};

// ============================================
// TEST CASES
// ============================================

console.log([1, [2, [3, [4]]]].myFlat());            // Expected: [ 1, 2, [ 3, [ 4 ] ] ]
console.log([1, [2, [3, [4]]]].myFlat(2));           // Expected: [ 1, 2, 3, [ 4 ] ]
console.log([1, [2, [3, [4]]]].myFlat(Infinity));    // Expected: [ 1, 2, 3, 4 ]
console.log([1, 2, 3].myFlat());                     // Expected: [ 1, 2, 3 ]
console.log([1, , 3].myFlat());                      // Expected: [ 1, 3 ]
console.log([[1], [2]].myFlat(0));                   // Expected: [ [ 1 ], [ 2 ] ]
```

---

## 🔍 Why This Works (3 lines max)
Each recursive call handles one level and reduces `depth`. When depth hits 0, nested arrays are kept untouched. `Infinity - 1` is still `Infinity`, so it goes all the way.
हिंदी: हर recursion में depth घटती है, 0 होने पर nested arrays वैसे ही रहते हैं।

---

## ⚡ Alternative Solution
```javascript
// Using reduce + concat
Array.prototype.myFlat2 = function (depth = 1) {
  return this.reduce(
    (acc, item) => acc.concat(Array.isArray(item) && depth > 0 ? item.myFlat2(depth - 1) : item),
    []                                             // start with empty array
  );
};
console.log([1, [2, [3]]].myFlat2(Infinity));     // Expected: [ 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: ignoring depth (always flattens fully)
item.myFlat();                  // default depth = 1 each time, not what user asked

// ✅ Correct: pass depth - 1 down
item.myFlat(depth - 1);
```

---

## 🎯 Interview Tip (1 line)
Mention an iterative stack-based version for very deep arrays to avoid stack overflow.

---

## 🔗 Related Questions
→ Q058 (flatten nested array) | Q059 (deep flatten) | Q073 (flatten nested object) | Q114 (reduce)
