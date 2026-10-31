---

# Q120. Implement deepFreeze
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `deepFreeze(obj)` that makes an object and ALL nested objects/arrays immutable. `Object.freeze` alone only freezes the first level.

```javascript
const o = deepFreeze({ a: { b: 1 } });
o.a.b = 2; // ignored (or TypeError in strict mode)
```

---

## 💡 Quick Concept (2 lines only)
Freeze the object, then recursively freeze every property value that is an object or function.
हिंदी: पहले object को freeze करो, फिर उसके अंदर के हर object को भी recursively freeze करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: freeze the current object
// Step 2: loop over all own keys (including symbols)
// Step 3: recursively freeze object/function values (skip already frozen)

function deepFreeze(obj) {
  if (obj === null || (typeof obj !== 'object' && typeof obj !== 'function')) {
    return obj;                                   // primitives are already immutable
  }
  if (Object.isFrozen(obj)) return obj;           // already frozen -> stops cycles too
  Object.freeze(obj);                             // freeze current level FIRST
  for (const key of Reflect.ownKeys(obj)) {       // string + symbol keys, even non-enumerable
    deepFreeze(obj[key]);                         // freeze nested value
  }
  return obj;                                     // return same object
}

// ============================================
// TEST CASES
// ============================================

const config = deepFreeze({ api: { url: 'x', tags: ['a', 'b'] }, port: 80 });

config.port = 99;                                 // silently ignored (sloppy mode)
config.api.url = 'y';                             // nested also ignored
try { config.api.tags.push('c'); } catch (e) { console.log(e.constructor.name); } // Expected: TypeError
console.log(config.port, config.api.url);         // Expected: 80 x
console.log(Object.isFrozen(config.api.tags));    // Expected: true

const shallow = Object.freeze({ inner: { n: 1 } });  // only top level frozen
shallow.inner.n = 2;                              // this works!
console.log(shallow.inner.n);                     // Expected: 2

const cyc = { name: 'c' }; cyc.self = cyc;        // circular reference
console.log(Object.isFrozen(deepFreeze(cyc)));    // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Freezing before recursing plus the `isFrozen` check prevents infinite loops on circular references. `Reflect.ownKeys` also covers symbol and non-enumerable keys.
हिंदी: पहले freeze करने और isFrozen जाँचने से circular reference में भी infinite loop नहीं बनता।

---

## ⚡ Alternative Solution
```javascript
// Compact version using Object.values (enumerable string keys only)
const deepFreeze2 = (o) => {
  Object.values(o).forEach(v => typeof v === 'object' && v !== null && deepFreeze2(v)); // freeze children
  return Object.freeze(o);                         // then freeze self
};
console.log(Object.isFrozen(deepFreeze2({ a: { b: 1 } }).a)); // Expected: true
// Weakness: loops forever on circular objects
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking Object.freeze is deep
const o = Object.freeze({ a: { b: 1 } });
o.a.b = 5;            // works! nested object not frozen

// ✅ Correct: freeze recursively
const o2 = deepFreeze({ a: { b: 1 } });
```

---

## 🎯 Interview Tip (1 line)
Say: "freeze is shallow and in sloppy mode fails silently; use strict mode to see TypeErrors."

---

## 🔗 Related Questions
→ Q071 (deep clone) | Q136 (fix object mutation bug) | Q260 (structuredClone) | Q294 (shallow vs deep copy)
