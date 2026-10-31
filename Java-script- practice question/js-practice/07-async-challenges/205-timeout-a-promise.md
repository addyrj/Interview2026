---

# Q205. Timeout a Promise
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `withTimeout(promise, ms)` that rejects with a `Timeout` error if the promise does not settle within `ms` milliseconds. If it settles in time, return its result.

```javascript
withTimeout(slowApi(), 200).catch(e => console.log(e.message));
```

---

## 💡 Quick Concept (2 lines only)
Race the real promise against a timer promise that rejects. Always clear the timer so Node can exit.
हिंदी: असली promise और timer promise के बीच `Promise.race` लगाओ; जो पहले खत्म हो वही जीतता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: create a timer promise that rejects after `ms`
// Step 2: race it against the real promise
// Step 3: clear the timer in finally to avoid leaks

function withTimeout(promise, ms) {
  let timerId;                                        // hold the timer so we can clear it
  const timeout = new Promise((_, reject) => {        // never resolves, only rejects
    timerId = setTimeout(
      () => reject(new Error(`Timeout after ${ms}ms`)), // reject when time is up
      ms
    );
  });
  return Promise.race([promise, timeout])             // first to settle wins
    .finally(() => clearTimeout(timerId));            // cleanup either way
}

// ============================================
// TEST CASES
// ============================================

const sleep = (ms, value) => new Promise(r => setTimeout(() => r(value), ms)); // fake API

(async () => {
  console.log(await withTimeout(sleep(50, 'fast'), 200)); // Expected: fast

  try {
    await withTimeout(sleep(500, 'slow'), 100);       // too slow
  } catch (e) {
    console.log(e.message);                           // Expected: Timeout after 100ms
  }

  try {
    await withTimeout(Promise.reject(new Error('api down')), 100); // real error passes through
  } catch (e) {
    console.log(e.message);                           // Expected: api down
  }
})();
// Console order:
// fast
// Timeout after 100ms
// api down
```

---

## 🔍 Why This Works (3 lines max)
`Promise.race` settles with whichever promise settles first, success or failure. `finally` clears the timer so a fast result does not leave a pending timeout keeping the process alive.
हिंदी: `race` में जो पहले settle हो वही result है; `finally` में timer साफ करना ज़रूरी है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Modern built-in: AbortSignal.timeout (Node 18+/browsers)
async function withSignalTimeout(taskFn, ms) {
  const signal = AbortSignal.timeout(ms);             // auto-aborts after ms
  return Promise.race([
    taskFn(signal),                                   // task may honour the signal
    new Promise((_, rej) =>
      signal.addEventListener('abort', () => rej(new Error('Timeout')), { once: true })
    )
  ]);
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: timer never cleared; also the original work keeps running
Promise.race([promise, new Promise((_, r) => setTimeout(r, ms))]);

// ✅ Correct: clear the timer; use AbortController to actually stop the work (Q206/Q219)
```

---

## 🎯 Interview Tip (1 line)
Say: "Timeout only stops waiting — it does not cancel the underlying work; pair it with AbortController."

---

## 🔗 Related Questions
→ Q206 (cancel a promise) | Q212 (race with fallback) | Q092 (implement Promise.race) | Q219 (abort fetch)
