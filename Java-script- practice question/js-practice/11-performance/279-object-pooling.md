---

# Q279. Object Pooling
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement an `ObjectPool` that reuses particle objects instead of creating and garbage-collecting thousands of them.

---

## 💡 Quick Concept (2 lines only)
Object pooling pre-creates objects and recycles them, reducing allocation and garbage collection pauses.
हिंदी: Object बार-बार बनाने के बजाय पुराने objects को वापस pool में डालकर दोबारा use करते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Pool holds free objects and a factory
// Step 2: acquire() reuses a free one or creates new
// Step 3: release() resets and returns to pool

class ObjectPool {
  constructor(create, reset, size = 0) {
    this.create = create;                          // how to build one
    this.reset = reset;                            // how to clean one
    this.free = Array.from({ length: size }, create); // pre-allocate
    this.created = size;                           // total ever created
  }
  acquire() {
    if (this.free.length) return this.free.pop();  // reuse existing
    this.created++;                                // pool empty → allocate
    return this.create();                          // new object
  }
  release(obj) {
    this.reset(obj);                               // wipe state
    this.free.push(obj);                           // make available again
  }
}

const pool = new ObjectPool(
  () => ({ x: 0, y: 0, alive: false }),            // factory
  (p) => { p.x = 0; p.y = 0; p.alive = false; },   // reset
  2                                                // pre-create 2
);

// ============================================
// TEST CASES
// ============================================

const p1 = pool.acquire();                         // reused #1
p1.x = 10; p1.alive = true;                        // use it
pool.release(p1);                                  // return it
const p2 = pool.acquire();                         // should be the same object
console.log(p1 === p2);                            // Expected: true
console.log(p2.x, p2.alive);                       // Expected: 0 false
for (let i = 0; i < 5; i++) pool.acquire();        // exhaust pool
console.log(pool.created);                         // Expected: 6 (2 pre-made + 4 new)
```

---

## 🔍 Why This Works (3 lines max)
Allocated objects stay alive and are reset instead of becoming garbage, so the GC has less to collect. Created count only grows when demand exceeds the pool.
हिंदी: Objects कचरा बनने के बजाय reuse होते हैं, इसलिए GC का काम कम हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Minimal pool using a plain array
const free = [];                                     // free list
const get = () => free.pop() ?? { v: 0 };            // reuse or create
const put = (o) => { o.v = 0; free.push(o); };       // reset and store
const o = get(); put(o);                             // cycle one object
console.log(get() === o);                            // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: releasing without reset → stale data leaks into the next user
// ✅ Correct: always reset in release(); never use an object after releasing it
```

---

## 🎯 Interview Tip (1 line)
Use pools only for hot paths (games, animations); say modern GCs make them unnecessary for ordinary code.

---

## 🔗 Related Questions
→ Q282 (Memory leaks) | Q284 (requestAnimationFrame) | Q099 (LRU cache)
