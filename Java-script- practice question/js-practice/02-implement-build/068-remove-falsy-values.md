---

# Q068. Remove Falsy Values
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `compact(arr)` that removes all falsy values (`false`, `0`, `''`, `null`, `undefined`, `NaN`) from an array.

```javascript
compact([0, 1, false, 2, '', 3, null]); // [1, 2, 3]
```

---

## 💡 Quick Concept (2 lines only)
`filter(Boolean)` keeps only truthy values because `Boolean(x)` is false for falsy ones.
हिंदी: filter(Boolean) सिर्फ truthy values रखता है, falsy सब हट जाती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: call filter on the array
// Step 2: use Boolean as the predicate
// Step 3: truthy items stay, falsy items drop

function compact(arr) {
  return arr.filter(Boolean); // Boolean(item) === true keeps the item
}

// ============================================
// TEST CASES
// ============================================

console.log(compact([0, 1, false, 2, '', 3, null]));        // Expected: [ 1, 2, 3 ]
console.log(compact([NaN, undefined, 'a', [], {}]));        // Expected: [ 'a', [], {} ]
console.log(compact([0, '', null]));                        // Expected: []
console.log(compact([]));                                   // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
`filter` passes each item to `Boolean`, which converts it to true/false using JS truthiness rules. Empty arrays and objects are truthy, so they stay.
हिंदी: Boolean हर value को true/false में बदलता है और filter false वाली हटा देता है।

---

## ⚡ Alternative Solution
```javascript
// Explicit loop
function compact2(arr) {
  const out = [];                     // result
  for (const x of arr) {              // each element
    if (x) out.push(x);               // truthy -> keep
  }
  return out;                         // cleaned array
}
console.log(compact2([0, 'hi', null, 5])); // Expected: [ 'hi', 5 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: removing 0 when it is valid data
console.log([0, 1, 2].filter(Boolean)); // [ 1, 2 ]  (0 lost!)
// ✅ Correct: remove only null/undefined when 0 is valid
console.log([0, 1, null, undefined].filter((x) => x != null)); // [ 0, 1 ]
```

---

## 🎯 Interview Tip (1 line)
List the 6 falsy values and warn that `0` and `''` may be legitimate data, so filter only null/undefined when needed.

---

## 🔗 Related Questions
→ Q036 (truthy/falsy) | Q069 (unique values) | Q055 (remove duplicates)
