---

# Q179. Explain Spread vs Rest
# Category: Tricky Concepts
# Difficulty: ⭐ Easy

---

## ❓ Question
Both use `...`. Explain the difference between spread and rest, with examples of each, and the shallow-copy gotcha.

---

## 💡 Quick Concept (2 lines only)
Rest COLLECTS many items into one array/object (function params, destructuring). Spread EXPANDS an iterable/object into individual items (calls, array/object literals).
हिंदी: Rest बिखरी values को इकट्ठा करता है, Spread इकट्ठी values को फैला देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Rest -> appears in parameters / destructuring (left side)
// Step 2: Spread -> appears in calls / literals (right side)
// Step 3: Both are shallow

// REST in function parameters
function sum(...nums) {                        // collects all args into array
  return nums.reduce((a, b) => a + b, 0);      // add them
}
console.log(sum(1, 2, 3, 4));                  // 10

// REST in destructuring (must be last)
const [head, ...tail] = [1, 2, 3];             // tail collects remaining
console.log(head, tail);                       // 1 [ 2, 3 ]
const { a, ...others } = { a: 1, b: 2, c: 3 }; // others collects remaining keys
console.log(others);                           // { b: 2, c: 3 }

// SPREAD in function call
const nums = [5, 1, 9];                        // array
console.log(Math.max(...nums));                // 9

// SPREAD in array literals
const merged = [...[1, 2], ...[3, 4], 5];      // combine arrays
console.log(merged);                           // [ 1, 2, 3, 4, 5 ]
console.log([...'abc']);                       // [ 'a', 'b', 'c' ]

// SPREAD in object literals (later keys override)
const base = { x: 1, y: 2 };                   // base object
console.log({ ...base, y: 99, z: 3 });         // { x: 1, y: 99, z: 3 }

// Shallow copy gotcha
const original = { inner: { v: 1 } };          // nested object
const copy = { ...original };                  // shallow copy
copy.inner.v = 100;                            // mutates shared nested object
console.log(original.inner.v);                 // 100

// Spread skips non-iterables in arrays
try { [...123]; } catch (e) { console.log(e.name); } // TypeError

// ============================================
// TEST CASES
// ============================================
// Expected output:
// 10
// 1 [ 2, 3 ]
// { b: 2, c: 3 }
// 9
// [ 1, 2, 3, 4, 5 ]
// [ 'a', 'b', 'c' ]
// { x: 1, y: 99, z: 3 }
// 100
// TypeError
```

---

## 🔍 Why This Works (3 lines max)
Same `...` token, opposite direction: in a binding position it gathers, in an expression position it expands. Copies are shallow, so nested references are shared.
हिंदी: एक ही `...` है — बाईं तरफ इकट्ठा करता है, दाईं तरफ फैलाता है; copy सिर्फ ऊपरी स्तर की होती है।

---

## ⚡ Alternative Solution
```javascript
// Deep copy when nested data matters
const deep = structuredClone({ inner: { v: 1 } }); // true deep copy
deep.inner.v = 5;                              // does not affect source
console.log(deep.inner.v);                     // Expected: 5
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Rest parameter not last
// function f(...a, b) {}   // SyntaxError

// ✅ Rest must be the final parameter
function f(b, ...a) { return [b, a]; }
console.log(f(1, 2, 3)); // [ 1, [ 2, 3 ] ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Rest gathers, spread expands; both are shallow — use structuredClone for deep copies."

---

## 🔗 Related Questions
→ Q040 (spread output) | Q041 (rest output) | Q242 (spread 10 examples) | Q294 (shallow vs deep copy)
