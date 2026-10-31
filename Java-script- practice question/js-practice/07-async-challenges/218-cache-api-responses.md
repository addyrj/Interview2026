---

# Q218. Cache API Responses
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `createCachedFetcher(fetchFn, ttl)`. Repeated requests for the same URL within `ttl` ms return the cached response without hitting the network. After expiry, fetch again. Expose a `clear()` method.

```javascript
const get = createCachedFetcher(api, 100);
await get('/users'); await get('/users'); // 1 network call
```

---

## 💡 Quick Concept (2 lines only)
Store `{ promise, expiresAt }` per URL in a Map. A hit is valid only while `Date.now() < expiresAt`.
हिंदी: हर URL के लिए response और expiry time रखो; समय बीतने पर cache अमान्य मान लो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Map url -> { promise, expiresAt }
// Step 2: valid hit -> return cached promise
// Step 3: miss/expired -> fetch, store; on error remove entry

function createCachedFetcher(fetchFn, ttl) {
  const cache = new Map();                            // url -> entry

  async function get(url) {
    const entry = cache.get(url);                     // look up
    if (entry && Date.now() < entry.expiresAt) {      // fresh?
      return entry.promise;                           // serve from cache
    }
    const promise = fetchFn(url);                     // start network call
    cache.set(url, { promise, expiresAt: Date.now() + ttl }); // store immediately
    try {
      return await promise;                           // wait for result
    } catch (err) {
      cache.delete(url);                              // never cache errors
      throw err;
    }
  }

  get.clear = () => cache.clear();                    // manual invalidation
  return get;
}

// ============================================
// TEST CASES
// ============================================

let network = 0;                                      // real network hits
const api = async url => {
  network++;                                          // count hit
  await new Promise(r => setTimeout(r, 10));          // fake latency
  if (url === '/bad') throw new Error('500');         // simulate server error
  return { url, hit: network };                       // response includes hit number
};

const sleep = ms => new Promise(r => setTimeout(r, ms)); // wait helper

(async () => {
  const get = createCachedFetcher(api, 100);          // 100ms TTL

  console.log(await get('/users'));                   // Expected: { url: '/users', hit: 1 }
  console.log(await get('/users'));                   // Expected: { url: '/users', hit: 1 } (cached)
  console.log('network:', network);                   // Expected: network: 1

  await sleep(150);                                   // let TTL expire
  console.log(await get('/users'));                   // Expected: { url: '/users', hit: 2 }

  get.clear();                                        // manual invalidate
  console.log(await get('/users'));                   // Expected: { url: '/users', hit: 3 }

  await get('/bad').catch(e => console.log(e.message)); // Expected: 500
  await get('/bad').catch(e => console.log(e.message)); // Expected: 500 (errors not cached)
  console.log('network:', network);                   // Expected: network: 5
})();
```

---

## 🔍 Why This Works (3 lines max)
Caching the promise dedupes concurrent requests and TTL bounds staleness. Deleting entries on error prevents a temporary failure from being served repeatedly.
हिंदी: TTL से पुराना data नहीं मिलता, और error cache में नहीं रखा जाता।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Stale-while-revalidate: return stale data instantly, refresh in background
function swr(fetchFn, ttl) {
  const cache = new Map();                            // url -> { value, time }
  return async url => {
    const hit = cache.get(url);
    const refresh = () => fetchFn(url).then(v => cache.set(url, { value: v, time: Date.now() }));
    if (!hit) { await refresh(); return cache.get(url).value; } // first load waits
    if (Date.now() - hit.time > ttl) refresh().catch(() => {}); // stale: refresh silently
    return hit.value;                                 // serve instantly
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: cache never expires -> user sees stale data forever; memory also grows
cache[url] = data;

// ✅ Correct: TTL (+ max size / LRU eviction) and manual invalidation after mutations
```

---

## 🎯 Interview Tip (1 line)
Name real tools (React Query/SWR, HTTP Cache-Control/ETag) and talk about cache invalidation after POST/PUT.

---

## 🔗 Related Questions
→ Q185 (cache with TTL) | Q215 (memoize async) | Q099 (LRU cache) | Q283 (WeakMap for cache)
