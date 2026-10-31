---

# Q215. Memoize an Async Function
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `memoizeAsync(fn)` that caches results by arguments. Concurrent calls with the same arguments must share ONE in-flight request, and failed calls must NOT be cached.

```javascript
const getUser = memoizeAsync(fetchUser);
await Promise.all([getUser(1), getUser(1)]); // fetchUser called once
```

---

## 💡 Quick Concept (2 lines only)
Cache the PROMISE (not the value) so parallel callers share it. Delete the cache entry if the promise rejects.
हिंदी: Value की जगह promise को cache करो ताकि एक साथ आए calls एक ही request share करें; error पर cache हटा दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: build a cache key from the arguments
// Step 2: if key exists return the cached promise
// Step 3: otherwise call fn, store promise, remove it on failure

function memoizeAsync(fn) {
  const cache = new Map();                            // key -> promise

  return function (...args) {
    const key = JSON.stringify(args);                 // simple key from arguments
    if (cache.has(key)) return cache.get(key);        // reuse (in-flight OR settled) promise

    const promise = fn.apply(this, args)              // start the real call
      .catch(err => {
        cache.delete(key);                            // do NOT cache failures
        throw err;                                    // keep rejection for callers
      });

    cache.set(key, promise);                          // store immediately (before it resolves)
    return promise;
  };
}

// ============================================
// TEST CASES
// ============================================

let calls = 0;                                        // real call counter
const fetchUser = async id => {
  calls++;                                            // count real executions
  await new Promise(r => setTimeout(r, 30));          // fake latency
  if (id === 99) throw new Error('not found');        // simulate failure
  return { id };
};

(async () => {
  const getUser = memoizeAsync(fetchUser);

  const [a, b] = await Promise.all([getUser(1), getUser(1)]); // concurrent, same args
  console.log(a === b, calls);                        // Expected: true 1

  await getUser(1);                                   // later call, from cache
  console.log(calls);                                 // Expected: 1

  await getUser(2);                                   // different args -> new call
  console.log(calls);                                 // Expected: 2

  await getUser(99).catch(e => console.log(e.message)); // Expected: not found
  await getUser(99).catch(e => console.log(e.message)); // Expected: not found
  console.log(calls);                                 // Expected: 4 (failure retried, not cached)
})();
```

---

## 🔍 Why This Works (3 lines max)
Storing the promise synchronously means a second call made while the first is pending finds it in the cache. The `catch` removes failed entries so the next call can retry.
हिंदी: Promise तुरंत store होता है इसलिए दूसरा call वही promise पाता है; fail होने पर entry हट जाती है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Add TTL so stale data expires
function memoizeAsyncTTL(fn, ttl) {
  const cache = new Map();
  return async (...args) => {
    const key = JSON.stringify(args);
    const hit = cache.get(key);
    if (hit && Date.now() - hit.time < ttl) return hit.promise; // still fresh
    const promise = fn(...args);
    cache.set(key, { promise, time: Date.now() });    // store with timestamp
    promise.catch(() => cache.delete(key));           // drop on failure
    return promise;
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: caching the value only after await -> parallel calls all hit the API
if (!cache[key]) cache[key] = await fn(...args);

// ✅ Correct: cache the promise immediately, before awaiting
cache.set(key, fn(...args));
```

---

## 🎯 Interview Tip (1 line)
Say: "Cache the promise to dedupe in-flight requests, evict rejections, and consider TTL + max size."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q218 (cache API responses) | Q185 (cache with TTL) | Q214 (debounce async)
