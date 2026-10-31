---

# Q059. Deep Flatten Array
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deepFlatten(arr)` that flattens an array of ANY nesting depth into a single-level array, without using `flat(Infinity)`.

```javascript
deepFlatten([1, [2, [3, [4]]]]); // [1, 2, 3, 4]
```

---

## 💡 Quick Concept (2 lines only)
Use recursion: if an item is an array, flatten it too; otherwise push the value.
हिंदी: अगर item खुद array है तो उसे फिर से flatten करो (recursion), वरना सीधे जोड़ दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: loop through each item
// Step 2: if item is array -> recurse and spread result
// Step 3: else push item into result

function deepFlatten(arr) {
  const result = [];                          // output array
  for (const item of arr) {                   // visit each element
    if (Array.isArray(item)) {                // nested array?
      result.push(...deepFlatten(item));      // flatten it recursively
    } else {
      result.push(item);                      // plain value
    }
  }
  return result;                              // flat array
}

// ============================================
// TEST CASES
// ============================================

console.log(deepFlatten([1, [2, [3, [4]]]]));   // Expected: [ 1, 2, 3, 4 ]
console.log(deepFlatten([[], [1, [], [2]]]));   // Expected: [ 1, 2 ]
console.log(deepFlatten([1, 2, 3]));            // Expected: [ 1, 2, 3 ]
console.log(deepFlatten([]));                   // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Each nested array is solved by the same function, so depth does not matter. The base case is a non-array value, which is pushed directly.
हिंदी: recursion हर गहराई के array को खुद संभाल लेता है, इसलिए depth की चिंता नहीं।

---

## ⚡ Alternative Solution
```javascript
// Built-in
console.log([1, [2, [3, [4]]]].flat(Infinity)); // Expected: [ 1, 2, 3, 4 ]
// Iterative with a stack (no recursion limit)
function flatIter(arr) {
  const stack = [...arr];                 // copy input onto stack
  const out = [];                         // result
  while (stack.length) {                  // until stack empty
    const x = stack.pop();                // take last item
    if (Array.isArray(x)) stack.push(...x); // expand nested array
    else out.push(x);                     // collect value
  }
  return out.reverse();                   // restore original order
}
console.log(flatIter([1, [2, [3, [4]]]])); // Expected: [ 1, 2, 3, 4 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: concat flattens only ONE level
console.log([].concat(...[1, [2, [3]]])); // [ 1, 2, [ 3 ] ]
// ✅ Correct: recurse for deeper levels
console.log([1, [2, [3]]].flat(Infinity)); // [ 1, 2, 3 ]
```

---

## 🎯 Interview Tip (1 line)
Show recursion first, then mention the iterative stack version and `flat(Infinity)`.

---

## 🔗 Related Questions
→ Q058 (flatten array) | Q073 (flatten object) | Q117 (implement Array.flat)
