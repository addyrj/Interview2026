---

# Q239. Service Worker Basics
# Category: DOM Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Register a service worker that pre-caches the app shell on install, cleans old caches on activate, and serves cached files first (falling back to network) on fetch.

---

## 💡 Quick Concept (2 lines only)
A service worker is a background script acting as a network proxy; lifecycle is register -> install -> activate -> fetch.
हिंदी: Service worker background में चलने वाला proxy है जो network requests को पकड़कर cache से जवाब दे सकता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — file 1: main.js (runs in the page)
// ============================================

// Step 1: Check support and register on load
if ('serviceWorker' in navigator) {                      // feature detection
  window.addEventListener('load', async () => {          // wait for page load
    try {
      const reg = await navigator.serviceWorker.register('/sw.js'); // register worker
      console.log('SW registered, scope:', reg.scope);   // scope it controls
    } catch (err) {
      console.error('SW failed:', err);                  // needs HTTPS/localhost
    }
  });
}

// ============================================
// SOLUTION — file 2: sw.js (runs in worker, served from site root)
// ============================================

const CACHE = 'app-shell-v1';                            // bump version to update
const ASSETS = ['/', '/index.html', '/styles.css', '/main.js']; // files to pre-cache

// Step 2: install -> cache the app shell
self.addEventListener('install', (event) => {
  event.waitUntil(                                       // keep worker alive until done
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS)) // download + store
  );
  self.skipWaiting();                                    // activate immediately
});

// Step 3: activate -> delete old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>                         // all cache names
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))) // drop old ones
    )
  );
  self.clients.claim();                                  // control open pages now
});

// Step 4: fetch -> cache first, then network
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;            // only cache GET
  event.respondWith(
    caches.match(event.request).then((cached) =>         // look in cache
      cached || fetch(event.request)                     // else go to network
    )
  );
});

// ============================================
// TEST CASES
// ============================================

// Test 1: load page on localhost -> Expected console: SW registered, scope: http://localhost/
// Test 2: DevTools > Application > Service Workers -> Expected: status "activated and running"
// Test 3: DevTools > Network > Offline, reload -> Expected: page still loads from cache
// Test 4: change CACHE to 'app-shell-v2', reload -> Expected: old cache 'app-shell-v1' deleted
// Test 5: Console: caches.keys().then(console.log) -> Expected: [ 'app-shell-v1' ]
```

---

## 🔍 Why This Works (3 lines max)
`install` fills the cache once, `activate` removes stale versions, and `fetch` intercepts every request to serve cache first. `waitUntil` keeps the worker alive until async work finishes. Scope is limited by the script's path, so serve it from root.
हिंदी: install में cache भरते हैं, activate में पुराना हटाते हैं, और fetch में cache से जवाब देते हैं।

---

## ⚡ Alternative Solution
```javascript
// Network-first strategy (fresh data when online, cache when offline)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)                                 // try network
      .then((res) => {
        const copy = res.clone();                        // clone: body can be read once
        caches.open(CACHE).then((c) => c.put(event.request, copy)); // update cache
        return res;                                      // return live response
      })
      .catch(() => caches.match(event.request))          // offline -> cached
  );
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting event.waitUntil -> worker may stop before caching finishes
self.addEventListener('install', () => { caches.open(CACHE).then((c) => c.addAll(ASSETS)); });

// ✅ Correct: wrap the promise in event.waitUntil(...)
```

---

## 🎯 Interview Tip (1 line)
Say: "Service workers need HTTPS, have no DOM access, are event-driven, and I choose a strategy per request: cache-first, network-first, or stale-while-revalidate."

---

## 🔗 Related Questions
→ Q238 (IndexedDB wrapper) | Q240 (web worker basics) | Q218 (cache API responses)
