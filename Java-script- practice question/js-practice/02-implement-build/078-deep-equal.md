---

# Q078. Deep Equal Comparison
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `deepEqual(a, b)` that returns `true` if two values are structurally equal, including nested objects and arrays.

```javascript
deepEqual({ a: [1, 2] }, { a: [1, 2] }); // true
deepEqual({ a: 1 }, { a: 2 });           // false
```

---

## 💡 Quick Concept (2 lines only)
Primitives are compared with `===`; objects are compared key by key, recursively. Check types, key counts, then each value.
हिंदी: Deep equal में हर nested key और value को recursively compare किया जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: same reference or same primitive => equal
// Step 2: if either is not an object (or null) => not equal
// Step 3: array vs object mismatch => not equal
// Step 4: compare key counts
// Step 5: recursively compare each key

function deepEqual(a, b) {
  if (a === b) return true;                                  // same value or same reference
  if (Number.isNaN(a) && Number.isNaN(b)) return true;       // NaN should equal NaN
  if (typeof a !== 'object' || typeof b !== 'object' ||
      a === null || b === null) return false;                // primitives that differ
  if (Array.isArray(a) !== Array.isArray(b)) return false;   // array vs object mismatch

  const keysA = Object.keys(a);                              // keys of first
  const keysB = Object.keys(b);                              // keys of second
  if (keysA.length !== keysB.length) return false;           // different size => not equal

  for (const key of keysA) {                                 // check every key of a
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false; // key missing in b
    if (!deepEqual(a[key], b[key])) return false;            // recursive value compare
  }
  return true;                                               // everything matched
}

// ============================================
// TEST CASES
// ============================================

console.log(deepEqual({ a: [1, 2], b: { c: 3 } }, { a: [1, 2], b: { c: 3 } })); // Expected: true
console.log(deepEqual({ a: 1 }, { a: 2 }));      // Expected: false
console.log(deepEqual([1, 2, 3], [1, 2, 3]));    // Expected: true
console.log(deepEqual([1, 2], { 0: 1, 1: 2 })); // Expected: false
console.log(deepEqual(NaN, NaN));                // Expected: true
console.log(deepEqual(null, {}));                // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
Recursion walks both structures together; any mismatch returns false immediately. Key-length check catches extra keys.
हिंदी: Recursion दोनों structures को साथ-साथ चलाता है, कहीं भी फर्क मिला तो false।

---

## ⚡ Alternative Solution
```javascript
// Quick but lossy: JSON.stringify (order-sensitive, drops undefined/functions)
const quickEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

console.log(quickEqual({ a: 1, b: 2 }, { a: 1, b: 2 })); // Expected: true
console.log(quickEqual({ a: 1, b: 2 }, { b: 2, a: 1 })); // Expected: false (order matters!)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting null check — typeof null === 'object'
function bad(a, b) {
  if (typeof a === 'object') return Object.keys(a).length === Object.keys(b).length; // crashes on null
}

// ✅ Correct: guard null and compare recursively (see solution above)
```

---

## 🎯 Interview Tip (1 line)
Mention edge cases: NaN, null, arrays vs objects, Date/Map/Set, and circular references (use a WeakMap to track visited pairs).

---

## 🔗 Related Questions
→ Q071 (deep clone) | Q077 (empty object) | Q199 (deep diff utility)
