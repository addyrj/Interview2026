---

# Q125. Fix Memory Leak Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
This cache stores a big object per key forever, so memory never gets freed even when the key object is gone. Fix it.

```javascript
// BUGGY CODE:
const cache = new Map();

function getData(obj) {
  if (!cache.has(obj)) {
    cache.set(obj, { big: new Array(1000).fill(0) }); // strong reference to obj
  }
  return cache.get(obj);
}
```

---

## 💡 Quick Concept (2 lines only)
A `Map` holds strong references to its keys, so they can never be garbage collected. `WeakMap` holds keys weakly — entries vanish when the key is unreachable.
हिंदी: `Map` keys को पकड़े रखता है; `WeakMap` से key हटते ही memory free हो जाती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: WeakMap instead of Map (keys must be objects)
const cache = new WeakMap();

// Step 2: same logic, but entries die with their key object
function getData(obj) {
  if (!cache.has(obj)) {                                    // not cached yet?
    cache.set(obj, { big: new Array(1000).fill(0) });       // store heavy data
  }
  return cache.get(obj);                                    // return cached value
}

// ============================================
// TEST CASES
// ============================================

let user = { id: 1 };                                       // key object
console.log(getData(user) === getData(user));               // Expected: true (cached)
console.log(cache.has(user));                               // Expected: true
user = null;                                                // key unreachable -> GC may free entry
console.log(typeof cache.get);                              // Expected: function (WeakMap has no size/iteration)
```

---

## 🔍 Why This Works (3 lines max)
WeakMap does not prevent its keys from being garbage collected, so when `user` is no longer referenced the cached data is freed too. The trade-off: you cannot iterate or read `.size`.
हिंदी: WeakMap key को weak पकड़ता है, इसलिए object हटते ही cached data भी साफ हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Manual cleanup with a normal Map
const m = new Map();
m.set('a', 1);
m.delete('a');            // explicitly remove when done
console.log(m.size);      // 0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: WeakMap with primitive key
try { new WeakMap().set('key', 1); } catch (e) { console.log(e.constructor.name); } // TypeError
// ✅ Correct: use an object key
new WeakMap().set({}, 1);
```

---

## 🎯 Interview Tip (1 line)
Say: "Common leaks: unbounded Map caches, forgotten listeners/timers, closures holding big data — WeakMap/cleanup fixes them."

---

## 🔗 Related Questions
→ Q048 (WeakMap output) | Q130 (event listener leak) | Q170 (WeakMap use case) | Q283 (WeakMap for cache)
