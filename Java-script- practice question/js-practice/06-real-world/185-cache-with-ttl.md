---

# Q185. Build Cache with TTL
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `TTLCache` where each entry expires after `ttl` milliseconds. Support `set`, `get`, `has`, `delete`, `size`. Expired entries must behave as missing.

```javascript
const cache = new TTLCache(1000);
cache.set('user', { id: 1 });   // valid for 1 second
```

---

## 💡 Quick Concept (2 lines only)
Store `{ value, expiresAt }` in a Map; on read, compare `now()` with `expiresAt` and lazily delete if expired.
हिंदी: हर value के साथ expiry time रखो; पढ़ते समय expire हो चुकी हो तो हटा दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class TTLCache {
  constructor(defaultTtl, now = () => Date.now()) {
    this.defaultTtl = defaultTtl;                // Step 1: default lifetime in ms
    this.now = now;                              // injectable clock (easy to test)
    this.store = new Map();                      // key -> { value, expiresAt }
  }

  set(key, value, ttl = this.defaultTtl) {
    this.store.set(key, { value, expiresAt: this.now() + ttl }); // Step 2: save with expiry
    return this;                                 // allow chaining
  }

  get(key) {
    const entry = this.store.get(key);           // Step 3: look up
    if (!entry) return undefined;                // missing
    if (this.now() >= entry.expiresAt) {         // Step 4: expired?
      this.store.delete(key);                    // lazy cleanup
      return undefined;                          // behave as missing
    }
    return entry.value;                          // still fresh
  }

  has(key) { return this.get(key) !== undefined; } // reuse get logic
  delete(key) { return this.store.delete(key); }   // manual removal

  get size() {
    for (const key of [...this.store.keys()]) this.get(key); // purge expired first
    return this.store.size;                      // live entries only
  }
}

// ============================================
// TEST CASES
// ============================================

let time = 0;                                    // fake clock
const cache = new TTLCache(1000, () => time);    // 1s default TTL
cache.set('a', 1).set('b', 2, 500);              // b lives only 500ms

console.log(cache.get('a'));                     // Expected: 1
time = 600;                                      // advance 600ms
console.log(cache.get('b'));                     // Expected: undefined (expired)
console.log(cache.get('a'));                     // Expected: 1
time = 1000;                                     // advance to 1000ms
console.log(cache.has('a'), cache.size);         // Expected: false 0
```

---

## 🔍 Why This Works (3 lines max)
Expiry is just a timestamp compare, so no timers are needed. Lazy deletion on access keeps it simple; the injected clock makes tests deterministic.
हिंदी: Timer की ज़रूरत नहीं — access पर timestamp compare करके expired entry हटा देते हैं।

---

## ⚡ Alternative Solution
```javascript
// Eager cleanup with setTimeout per key (frees memory even if never read)
function setWithTimer(map, key, value, ttl) {
  clearTimeout(map.get(key)?.timer);             // clear old timer
  const timer = setTimeout(() => map.delete(key), ttl); // auto delete
  map.set(key, { value, timer });
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only checking existence -> stale data returned forever
get(key) { return this.store.get(key)?.value; }

// ✅ Correct: always compare expiresAt before returning
get(key) { const e = this.store.get(key); return e && this.now() < e.expiresAt ? e.value : undefined; }
```

---

## 🎯 Interview Tip (1 line)
Mention lazy vs eager expiry, memory growth, and combining TTL with LRU eviction.

---

## 🔗 Related Questions
→ Q083 (memoize) | Q099 (LRU cache) | Q218 (cache API responses) | Q283 (WeakMap for cache)
