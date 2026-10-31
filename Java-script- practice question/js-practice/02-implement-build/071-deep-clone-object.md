---

# Q071. Deep Clone Object
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deepClone(value)` that creates a fully independent copy of nested objects/arrays (also Date and circular references).

```javascript
const copy = deepClone(original);
copy.a.b = 99; // original.a.b stays unchanged
```

---

## 💡 Quick Concept (2 lines only)
Recursively copy every nested object/array; keep a WeakMap of visited objects to survive circular references.
हिंदी: हर nested object को recursion से नया बनाओ, और circular reference के लिए WeakMap में याद रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: primitives are returned as-is
// Step 2: handle Date and already-visited objects
// Step 3: create empty array/object and copy keys recursively

function deepClone(value, seen = new WeakMap()) {
  if (value === null || typeof value !== 'object') return value; // primitive or function
  if (value instanceof Date) return new Date(value);             // copy Date
  if (seen.has(value)) return seen.get(value);                   // circular ref -> reuse clone
  const copy = Array.isArray(value) ? [] : {};                   // empty container
  seen.set(value, copy);                                         // register before recursing
  for (const key of Object.keys(value)) {                        // own enumerable keys
    copy[key] = deepClone(value[key], seen);                     // clone each child
  }
  return copy;                                                   // finished clone
}

// ============================================
// TEST CASES
// ============================================

const original = { a: { b: 1 }, list: [1, { c: 2 }], d: new Date(0) };
const copy = deepClone(original);
copy.a.b = 99;                                // change clone only
copy.list[1].c = 77;                          // change nested array item
console.log(original.a.b, original.list[1].c); // Expected: 1 2
console.log(copy.a.b, copy.list[1].c);         // Expected: 99 77
console.log(copy.d instanceof Date);           // Expected: true

const circ = { name: 'x' };
circ.self = circ;                              // circular reference
const circCopy = deepClone(circ);
console.log(circCopy.self === circCopy);       // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Every object level gets a brand-new container so no references are shared. The WeakMap maps original to clone, stopping infinite recursion on cycles.
हिंदी: हर level पर नया container बनता है, इसलिए कोई reference साझा नहीं रहता।

---

## ⚡ Alternative Solution
```javascript
// Built-in (Node 17+, modern browsers): handles Date, Map, Set, cycles
const c1 = structuredClone({ a: { b: 1 }, d: new Date(0) });
console.log(c1.a.b); // Expected: 1
// JSON trick: loses Date (-> string), undefined, functions, fails on cycles
console.log(JSON.parse(JSON.stringify({ d: new Date(0), f() {} }))); // Expected: { d: '1970-01-01T00:00:00.000Z' }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: spread / Object.assign is only a SHALLOW copy
const o = { a: { b: 1 } };
const shallow = { ...o };
shallow.a.b = 2;
console.log(o.a.b); // 2 (original changed!)
// ✅ Correct: deepClone / structuredClone
const deep = deepClone(o);
deep.a.b = 3;
console.log(o.a.b); // 2 (unchanged)
```

---

## 🎯 Interview Tip (1 line)
Mention circular references, Date/Map/Set handling, and that `structuredClone` is the modern built-in.

---

## 🔗 Related Questions
→ Q072 (merge objects) | Q078 (deep equal) | Q260 (structuredClone)
