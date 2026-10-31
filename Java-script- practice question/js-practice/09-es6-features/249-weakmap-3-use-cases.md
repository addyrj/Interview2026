---

# Q249. WeakMap — 3 Use Cases
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show 3 use cases of `WeakMap`: private data, object-keyed cache, and attaching metadata without memory leaks.

---

## 💡 Quick Concept (2 lines only)
WeakMap holds keys (objects only) weakly, so when the key object has no other references it can be garbage collected.
हिंदी: WeakMap की key object को GC रोकता नहीं, इसलिए memory leak नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Private data per instance
// Step 2: Cache keyed by object
// Step 3: Metadata for objects you don't own

// Use case 1: Private instance data
const priv = new WeakMap();                      // instance -> private data
class Account {
  constructor(balance) { priv.set(this, { balance }); } // store hidden
  get balance() { return priv.get(this).balance; }      // read hidden
}
const acc = new Account(500);                    // create instance
console.log(acc.balance, acc.hasOwnProperty('balance')); // Expected: 500 false

// Use case 2: Cache computed result per object
const cache = new WeakMap();                     // obj -> result
function heavy(obj) {
  if (cache.has(obj)) return 'cached:' + cache.get(obj); // hit
  const r = Object.keys(obj).length;             // pretend expensive work
  cache.set(obj, r);                             // store
  return 'computed:' + r;                        // miss
}
const data = { a: 1, b: 2 };                     // key object
console.log(heavy(data));                        // Expected: computed:2
console.log(heavy(data));                        // Expected: cached:2

// Use case 3: Metadata on foreign objects (e.g. DOM nodes), no leak
const clicks = new WeakMap();                    // node -> click count
const node = {};                                 // stand-in for a DOM node
clicks.set(node, (clicks.get(node) || 0) + 1);   // track
console.log(clicks.get(node));                   // Expected: 1

// ============================================
// TEST CASES
// ============================================

try { new WeakMap().set('str', 1); } catch (e) { console.log(e.constructor.name); } // Expected: TypeError
console.log(typeof new WeakMap().size);          // Expected: undefined
console.log(new WeakMap().has({}));              // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
Entries disappear automatically when the key object is unreachable, so the cache never grows forever. Because of that, WeakMap has no `size`, no iteration and no `clear`.
हिंदी: GC कभी भी key हटा सकता है, इसीलिए WeakMap को iterate या size नहीं कर सकते।

---

## ⚡ Alternative Solution
```javascript
// Modern private fields (#) for real privacy
class Acc2 {
  #balance;                                      // private field
  constructor(b) { this.#balance = b; }          // assign
  get balance() { return this.#balance; }        // expose read-only
}
console.log(new Acc2(7).balance);                // Expected: 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Map as object cache -> keeps objects alive forever (leak)
const leaky = new Map();                         // strong references
leaky.set({ big: 1 }, 'x');                      // never collected until deleted

// ✅ Correct: WeakMap lets GC clean up
const safe = new WeakMap();                      // weak references
safe.set({ big: 1 }, 'x');                       // collectable once key is unreferenced
console.log(leaky.size);                         // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "WeakMap = non-enumerable, object-only keys, GC-friendly — ideal for private data and caches tied to object lifetime."

---

## 🔗 Related Questions
→ Q048 (WeakMap output) | Q170 (WeakMap use case) | Q250 (WeakRef) | Q283 (WeakMap for cache)
