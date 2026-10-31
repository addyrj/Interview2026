---

# Q072. Merge Two Objects
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deepMerge(a, b)` that merges two objects recursively. Values in `b` win; nested plain objects are merged, not replaced. Do not mutate inputs.

```javascript
deepMerge({ a: 1, n: { x: 1 } }, { b: 2, n: { y: 2 } }); // { a: 1, n: { x: 1, y: 2 }, b: 2 }
```

---

## 💡 Quick Concept (2 lines only)
Shallow merge uses spread; deep merge recurses when both sides hold plain objects.
हिंदी: shallow merge में spread चलता है, deep merge में दोनों तरफ object हो तो recursion लगाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: helper to detect plain objects
// Step 2: start from a copy of a
// Step 3: for each key in b, merge recursively if both are plain objects, else overwrite

const isPlain = (v) => v !== null && typeof v === 'object' && !Array.isArray(v); // plain object check

function deepMerge(a, b) {
  const result = { ...a };                              // copy so a is not mutated
  for (const key of Object.keys(b)) {                   // each key from b
    if (isPlain(a[key]) && isPlain(b[key])) {           // both nested objects?
      result[key] = deepMerge(a[key], b[key]);          // merge them deeply
    } else {
      result[key] = b[key];                             // b wins
    }
  }
  return result;                                        // merged object
}

// ============================================
// TEST CASES
// ============================================

console.log(deepMerge({ a: 1, n: { x: 1 } }, { b: 2, n: { y: 2 } })); // Expected: { a: 1, n: { x: 1, y: 2 }, b: 2 }
console.log(deepMerge({ a: 1 }, { a: 2 }));                           // Expected: { a: 2 }
console.log(deepMerge({ list: [1] }, { list: [2] }));                 // Expected: { list: [ 2 ] }
const base = { n: { x: 1 } };
deepMerge(base, { n: { x: 9 } });
console.log(base.n.x);                                                // Expected: 1 (unchanged)
```

---

## 🔍 Why This Works (3 lines max)
Only when both values are plain objects do we recurse; otherwise the later value overwrites. Starting from `{ ...a }` keeps the input safe.
हिंदी: दोनों तरफ object हों तभी recursion होता है, वरना b की value जीतती है।

---

## ⚡ Alternative Solution
```javascript
// Shallow merge (nested objects get REPLACED)
console.log({ ...{ n: { x: 1 } }, ...{ n: { y: 2 } } }); // Expected: { n: { y: 2 } }
console.log(Object.assign({}, { a: 1 }, { b: 2 }));      // Expected: { a: 1, b: 2 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Object.assign(a, b) mutates a
const a = { x: 1 };
Object.assign(a, { y: 2 });
console.log(a); // { x: 1, y: 2 } (a changed)
// ✅ Correct: first argument is an empty object
console.log(Object.assign({}, { x: 1 }, { y: 2 })); // { x: 1, y: 2 }
```

---

## 🎯 Interview Tip (1 line)
Differentiate shallow vs deep merge, say who wins on conflict, and mention arrays need a policy (replace vs concat).

---

## 🔗 Related Questions
→ Q071 (deep clone) | Q075 (omit keys) | Q076 (pick keys)
