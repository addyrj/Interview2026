---

# Q219. Abort a Fetch Request
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use `AbortController` to cancel an in-flight `fetch`. Show (1) manual abort, (2) automatic abort after a timeout, and (3) how to tell an abort apart from a real network error.

```javascript
const controller = new AbortController();
fetch(url, { signal: controller.signal });
controller.abort(); // rejects with AbortError
```

---

## 💡 Quick Concept (2 lines only)
Pass `controller.signal` to `fetch`; calling `controller.abort()` rejects the promise with an `AbortError` and stops the request.
हिंदी: `AbortController` का signal fetch को दो और `abort()` बुलाओ तो request रुक जाती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: start a local server that responds slowly (so abort is testable)
// Step 2: fetch with a signal; abort manually / via timeout
// Step 3: check err.name === 'AbortError'

const http = require('http');                         // Node core module

async function fetchJson(url, { signal } = {}) {
  try {
    const res = await fetch(url, { signal });         // signal links fetch to controller
    return await res.json();                          // parse body
  } catch (err) {
    if (err.name === 'AbortError') return 'aborted';  // manual abort
    if (err.name === 'TimeoutError') return 'timed out'; // AbortSignal.timeout
    throw err;                                        // real network errors bubble up
  }
}

// ============================================
// TEST CASES
// ============================================

const server = http.createServer((req, res) => {     // slow server: replies after 300ms
  setTimeout(() => {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ ok: true }));            // tiny JSON body
  }, 300);
});

server.listen(0, async () => {                        // port 0 = any free port
  const url = `http://127.0.0.1:${server.address().port}/`; // build URL

  // Test 1: no abort -> normal result
  console.log(await fetchJson(url));                  // Expected: { ok: true }

  // Test 2: manual abort after 50ms
  const controller = new AbortController();           // create controller
  setTimeout(() => controller.abort(), 50);           // cancel quickly
  console.log(await fetchJson(url, { signal: controller.signal })); // Expected: aborted

  // Test 3: built-in timeout signal (Node 18+)
  console.log(await fetchJson(url, { signal: AbortSignal.timeout(50) })); // Expected: timed out

  // Test 4: abort before sending
  const early = new AbortController();
  early.abort();                                      // already aborted
  console.log(await fetchJson(url, { signal: early.signal })); // Expected: aborted

  server.closeAllConnections?.();                     // drop leftover sockets
  server.close();                                     // let Node exit
});
```

---

## 🔍 Why This Works (3 lines max)
The signal is a one-way channel: `abort()` fires an event that fetch listens to, rejecting its promise and closing the connection. `AbortSignal.timeout(ms)` is a signal that aborts itself with `TimeoutError`.
हिंदी: `abort()` signal पर event भेजता है, जिससे fetch reject होकर connection बंद कर देता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// React pattern: abort the previous request when a new one starts / on unmount
let current;                                          // controller of latest request
async function search(q) {
  current?.abort();                                   // cancel the older request
  current = new AbortController();                    // fresh controller
  const res = await fetch(`/api?q=${q}`, { signal: current.signal });
  return res.json();
}
// useEffect(() => { const c = new AbortController(); fetch(u, {signal:c.signal}); return () => c.abort(); }, [u]);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: treating AbortError as a failure and showing an error toast
catch (err) { showError(err.message); }

// ✅ Correct: ignore intentional aborts
catch (err) { if (err.name !== 'AbortError') showError(err.message); }
```

---

## 🎯 Interview Tip (1 line)
Say: "A controller is single-use; create a new one per request, and abort in useEffect cleanup to avoid race conditions."

---

## 🔗 Related Questions
→ Q206 (cancel a promise) | Q205 (timeout) | Q181 (search with debounce) | Q127 (fix async state update bug)
