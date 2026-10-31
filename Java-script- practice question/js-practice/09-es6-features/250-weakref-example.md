---

# Q250. WeakRef Example
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Use `WeakRef` to build a cache that does not keep objects alive, and use `FinalizationRegistry` to be notified on cleanup.

---

## 💡 Quick Concept (2 lines only)
`WeakRef` holds an object without preventing garbage collection; `deref()` returns the object or `undefined` if collected.
हिंदी: WeakRef object को पकड़ता है पर GC को रोकता नहीं; `deref()` object या undefined देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Wrap an object in a WeakRef
// Step 2: Build a cache storing WeakRefs
// Step 3: Register a cleanup callback

// Step 1: create a weak reference
let big = { name: 'huge-data' };                 // strongly held object
const ref = new WeakRef(big);                    // weak pointer to it
console.log(ref.deref().name);                   // Expected: huge-data

// Step 2: cache that doesn't prevent GC
class WeakCache {
  #map = new Map();                              // key -> WeakRef
  set(key, obj) { this.#map.set(key, new WeakRef(obj)); } // store weakly
  get(key) {
    const obj = this.#map.get(key)?.deref();     // may be undefined if collected
    if (!obj) this.#map.delete(key);             // clean dead entry
    return obj;                                  // object or undefined
  }
}
const wc = new WeakCache();                      // create cache
wc.set('a', big);                                // cache big
console.log(wc.get('a') === big);                // Expected: true

// Step 3: get notified after GC (timing NOT guaranteed)
const registry = new FinalizationRegistry(label => {
  console.log('cleaned', label);                 // may run later, or never
});
registry.register(big, 'big-object');            // watch the object

// ============================================
// TEST CASES
// ============================================

console.log(ref instanceof WeakRef);             // Expected: true
console.log(typeof ref.deref);                   // Expected: function
console.log(wc.get('missing'));                  // Expected: undefined
try { new WeakRef(1); } catch (e) { console.log(e.constructor.name); } // Expected: TypeError
```

---

## 🔍 Why This Works (3 lines max)
While `big` is still referenced, `deref()` returns it. Once all strong references vanish, the engine may free it and `deref()` returns `undefined`. GC timing is unpredictable, so never rely on it.
हिंदी: GC कब चलेगा यह तय नहीं, इसलिए हमेशा `deref()` का result check करो।

---

## ⚡ Alternative Solution
```javascript
// Simpler: WeakMap when keys are objects and you don't need deref
const wm = new WeakMap();                        // auto-cleaned map
const k = {};                                    // key
wm.set(k, 'v');                                  // store
console.log(wm.get(k));                          // Expected: v
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using deref() result without checking
// const name = ref.deref().name;   // TypeError if object was collected

// ✅ Correct: optional chaining
console.log(ref.deref()?.name);                  // Expected: huge-data
```

---

## 🎯 Interview Tip (1 line)
Say: "WeakRef is for rare cache-like cases; prefer WeakMap, and never depend on GC timing or finalizer callbacks."

---

## 🔗 Related Questions
→ Q249 (WeakMap) | Q282 (avoid memory leaks) | Q283 (WeakMap for cache) | Q125 (fix memory leak)
