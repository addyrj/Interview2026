---

# Q282. Avoid Memory Leaks
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show three common leak sources (forgotten listeners, timers, growing caches) and how to clean each one.

---

## 💡 Quick Concept (2 lines only)
A leak happens when something is still referenced (listener, timer, cache, closure) after you no longer need it, so GC can't free it.
हिंदी: जब बेकार चीज़ पर कोई reference बचा रहता है तो garbage collector उसे हटा नहीं पाता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Listener leak → remove or use AbortController
// Step 2: Timer leak → clearInterval
// Step 3: Cache leak → bound the size

const { EventEmitter } = require('events');        // Node emitter as our "DOM target"
const bus = new EventEmitter();                     // long-lived object

function mountLeaky() {
  bus.on('data', () => {});                         // never removed → leaks each mount
}

function mountClean() {
  const handler = () => {};                         // named reference
  bus.on('data', handler);                          // subscribe
  return () => bus.off('data', handler);            // cleanup function
}

// Bounded cache: evict oldest when over limit
function boundedSet(map, key, val, max = 3) {
  map.set(key, val);                                // insert
  if (map.size > max) map.delete(map.keys().next().value); // delete oldest key
}

// ============================================
// TEST CASES
// ============================================

for (let i = 0; i < 3; i++) mountLeaky();           // 3 leaked listeners
console.log(bus.listenerCount('data'));             // Expected: 3
const unmount = mountClean();                       // add one
console.log(bus.listenerCount('data'));             // Expected: 4
unmount();                                          // cleanup
console.log(bus.listenerCount('data'));             // Expected: 3 (clean one removed)

const timer = setInterval(() => {}, 1000);          // repeating timer
clearInterval(timer);                               // ✅ stop it so process can exit
const cache = new Map();                            // cache
for (let i = 1; i <= 5; i++) boundedSet(cache, i, i); // insert 5, max 3
console.log([...cache.keys()]);                     // Expected: [ 3, 4, 5 ]
```

---

## 🔍 Why This Works (3 lines max)
Removing the listener/timer drops the last reference so the callback and its closure become collectable. Bounding the cache stops unbounded growth.
हिंदी: Reference हटते ही callback और उसका closure GC से साफ हो जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// AbortController: remove many listeners with one call (Node 15+ & browsers)
const t = new EventTarget();                          // target
const ac = new AbortController();                     // controller
t.addEventListener('x', () => {}, { signal: ac.signal }); // tied to signal
t.addEventListener('y', () => {}, { signal: ac.signal }); // tied to signal
ac.abort();                                           // removes both at once
t.dispatchEvent(new Event('x'));                      // nothing runs
console.log('cleaned');                               // Expected: cleaned
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: useEffect(() => { window.addEventListener('resize', fn); }, []);
// ✅ Correct: return () => window.removeEventListener('resize', fn);
// Also avoid: accidental globals, detached DOM refs, unbounded arrays/Maps
```

---

## 🎯 Interview Tip (1 line)
Mention DevTools heap snapshots / "detached DOM nodes" for finding leaks, and WeakMap/WeakRef for caches.

---

## 🔗 Related Questions
→ Q125 (Fix memory leak) | Q130 (Event listener leak) | Q283 (WeakMap cache)
