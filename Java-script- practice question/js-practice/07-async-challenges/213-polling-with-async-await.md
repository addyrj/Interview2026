---

# Q213. Polling with Async/Await
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `poll(fn, { interval, maxAttempts, until })` that calls an async function repeatedly (waiting `interval` ms between calls) until `until(result)` is true. Reject if `maxAttempts` is exceeded.

```javascript
await poll(checkJobStatus, { interval: 100, maxAttempts: 5, until: r => r.status === 'done' });
```

---

## 💡 Quick Concept (2 lines only)
Loop: call, check condition, sleep, repeat. Wait for the previous call to finish before sleeping, so requests never overlap (unlike `setInterval`).
हिंदी: पहले call पूरा होने का इंतज़ार करो, फिर sleep, फिर दोबारा — `setInterval` की तरह overlap नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: loop up to maxAttempts
// Step 2: call fn and test the stop condition
// Step 3: sleep between attempts, throw when attempts run out

const sleep = ms => new Promise(r => setTimeout(r, ms)); // delay helper

async function poll(fn, { interval = 100, maxAttempts = 5, until = Boolean } = {}) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) { // bounded loop
    const result = await fn(attempt);                 // wait for this call to finish
    if (until(result)) return result;                 // condition met -> done
    if (attempt < maxAttempts) await sleep(interval); // pause before next poll
  }
  throw new Error(`Polling gave up after ${maxAttempts} attempts`); // never satisfied
}

// ============================================
// TEST CASES
// ============================================

// Fake job: becomes "done" on the 3rd check
const jobStatus = async n => {
  console.log(`check #${n}`);                         // visible poll count
  return { status: n >= 3 ? 'done' : 'pending' };     // pending, pending, done
};

(async () => {
  const r = await poll(jobStatus, { interval: 20, maxAttempts: 5, until: x => x.status === 'done' });
  console.log(r);                                     // Expected: check #1, check #2, check #3, then { status: 'done' }

  try {
    await poll(async () => ({ status: 'pending' }), {
      interval: 10, maxAttempts: 2, until: x => x.status === 'done'
    });
  } catch (e) {
    console.log(e.message);                           // Expected: Polling gave up after 2 attempts
  }
})();
// Console order:
// check #1
// check #2
// check #3
// { status: 'done' }
// Polling gave up after 2 attempts
```

---

## 🔍 Why This Works (3 lines max)
Awaiting `fn` before sleeping means polls never pile up if the server is slow. `maxAttempts` guarantees termination, and the `until` callback keeps the helper reusable.
हिंदी: `await` की वजह से requests overlap नहीं होते, और `maxAttempts` loop को खत्म होने की गारंटी देता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Recursive setTimeout version (never use setInterval for async work)
function pollRecursive(fn, until, interval) {
  return new Promise((resolve, reject) => {
    (async function tick() {
      try {
        const r = await fn();                         // call
        if (until(r)) return resolve(r);              // done
        setTimeout(tick, interval);                   // schedule next AFTER this finishes
      } catch (e) { reject(e); }                      // stop on error
    })();
  });
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: setInterval fires even if the previous request is still pending
setInterval(() => fetchStatus(), 1000);

// ✅ Correct: await the call, then sleep (or recursive setTimeout), with a max attempt/timeout
```

---

## 🎯 Interview Tip (1 line)
Mention backoff, an overall timeout, AbortSignal to stop polling, and WebSockets/SSE as alternatives.

---

## 🔗 Related Questions
→ Q090 (sleep) | Q204 (retry) | Q206 (cancel) | Q194 (data fetcher hook)
