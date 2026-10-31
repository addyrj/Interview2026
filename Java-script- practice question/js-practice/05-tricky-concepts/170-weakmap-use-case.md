---

# Q170. Explain WeakMap Use Case
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a WeakMap and when should you use it? Show private data storage and metadata caching without causing memory leaks.

---

## 💡 Quick Concept (2 lines only)
WeakMap holds keys weakly: keys must be objects, and when the key object has no other references it is garbage collected along with its value. It is not iterable and has no `size`.
हिंदी: WeakMap के keys object होते हैं और key हटते ही entry अपने आप memory से साफ हो जाती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Use object as key, store hidden data as value
// Step 2: Only code that holds the WeakMap can read the data (privacy)
// Step 3: When object is dropped, entry disappears (no leak)

const privateData = new WeakMap();          // module-private storage

class User {
  constructor(name, password) {
    this.name = name;                       // public field
    privateData.set(this, { password });    // hidden field keyed by instance
  }
  check(pw) {
    return privateData.get(this).password === pw; // read hidden data
  }
}

const u = new User('Aditya', 'secret');     // create user
console.log(u.check('secret'));             // true
console.log(u.check('wrong'));              // false
console.log(Object.keys(u));                // [ 'name' ] -> password not exposed

// Use case 2: cache computed results per object
const cache = new WeakMap();                // object -> result
function heavy(obj) {
  if (cache.has(obj)) return cache.get(obj) + ' (cached)'; // reuse
  const result = `size:${Object.keys(obj).length}`;        // pretend heavy work
  cache.set(obj, result);                   // store for next time
  return result;                            // first-time result
}
const data = { a: 1, b: 2 };                // key object
console.log(heavy(data));                   // size:2
console.log(heavy(data));                   // size:2 (cached)

// Restrictions
try { new WeakMap().set('str', 1); }        // primitives not allowed
catch (e) { console.log(e.name); }          // TypeError
console.log(typeof cache.size);             // undefined (no size)

// ============================================
// TEST CASES
// ============================================
// Expected output:
// true
// false
// [ 'name' ]
// size:2
// size:2 (cached)
// TypeError
// undefined
```

---

## 🔍 Why This Works (3 lines max)
A normal Map keeps strong references, so keys never get collected. WeakMap does not count as a reference, letting the GC free the key and its associated value automatically.
हिंदी: Map key को पकड़े रखता है, WeakMap नहीं पकड़ता — इसलिए GC उसे हटा सकता है।

---

## ⚡ Alternative Solution
```javascript
// Track DOM nodes without leaking (browser idea)
const clicks = new WeakMap();               // element -> count
function track(el) {
  clicks.set(el, (clicks.get(el) || 0) + 1); // increment per element
}
// When el is removed from the DOM and unreferenced, the count is freed too
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Map as cache -> objects never garbage collected (leak)
const leaky = new Map();
// leaky.set(bigObject, result);

// ✅ WeakMap lets bigObject be collected when no longer used
const safe = new WeakMap();
```

---

## 🎯 Interview Tip (1 line)
Say: "WeakMap = object-keyed, non-enumerable, GC-friendly — ideal for private data and per-object caches."

---

## 🔗 Related Questions
→ Q048 (WeakMap output) | Q249 (WeakMap 3 use cases) | Q250 (WeakRef) | Q283 (WeakMap for cache)
