---

# Q283. WeakMap for Cache
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Cache an expensive per-object computation so the cache entry disappears automatically when the object is garbage collected.

---

## 💡 Quick Concept (2 lines only)
WeakMap holds object keys weakly, so entries vanish when the key has no other references. Perfect for caches tied to object lifetime.
हिंदी: WeakMap key को कमजोर पकड़ता है, इसलिए object हटते ही cache entry अपने आप हट जाती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Create a WeakMap keyed by the object
// Step 2: Return cached result if present
// Step 3: Otherwise compute, store and return

const cache = new WeakMap();                    // object -> result (weak keys)
let computeCount = 0;                           // how many real computations ran

function expensive(obj) {
  if (cache.has(obj)) return cache.get(obj);    // cache hit
  computeCount++;                               // cache miss → real work
  const result = Object.keys(obj).length * 100; // pretend expensive computation
  cache.set(obj, result);                       // store by object identity
  return result;
}

// ============================================
// TEST CASES
// ============================================

const user = { a: 1, b: 2 };                    // key object
console.log(expensive(user));                   // Expected: 200
console.log(expensive(user));                   // Expected: 200 (cached)
console.log(computeCount);                      // Expected: 1
console.log(expensive({ a: 1, b: 2 }));         // Expected: 200 (different object → recompute)
console.log(computeCount);                      // Expected: 2
try { cache.set('str', 1); } catch (e) { console.log(e.constructor.name); } // Expected: TypeError (keys must be objects)
console.log(typeof cache.size);                 // Expected: undefined (not enumerable/sized)
```

---

## 🔍 Why This Works (3 lines max)
Keys are compared by identity and referenced weakly, so once `user` is unreachable the engine can drop both key and cached value. A normal Map would keep it alive forever.
हिंदी: Normal Map object को पकड़े रखता है, WeakMap नहीं, इसलिए memory leak नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Private data per instance with WeakMap
const priv = new WeakMap();                      // instance -> private state
class Acct {
  constructor(b) { priv.set(this, { balance: b }); } // hide state
  get balance() { return priv.get(this).balance; }   // controlled access
}
console.log(new Acct(50).balance);               // Expected: 50
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Map cache keyed by objects → entries never freed (leak)
// const cache = new Map(); cache.set(domNode, data);

// ✅ Correct: WeakMap for object-keyed caches; Map only for primitive keys
```

---

## 🎯 Interview Tip (1 line)
Say WeakMap isn't iterable and has no size precisely because GC timing is non-deterministic.

---

## 🔗 Related Questions
→ Q048 (WeakMap output) | Q170 (WeakMap use case) | Q249 (WeakMap uses)
