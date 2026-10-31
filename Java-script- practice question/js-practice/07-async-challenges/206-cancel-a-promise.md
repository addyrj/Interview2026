---

# Q206. Cancel a Promise
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Native promises cannot be cancelled. Build `makeCancellable(promise)` that returns `{ promise, cancel }`. After `cancel()`, the wrapped promise must reject with a `Cancelled` error and ignore the original result.

```javascript
const { promise, cancel } = makeCancellable(slowTask());
cancel(); // promise now rejects with Cancelled
```

---

## 💡 Quick Concept (2 lines only)
Wrap the promise and keep a `cancelled` flag; when the original settles, honour the flag instead of the value. For real work-stopping, pass an `AbortSignal`.
हिंदी: Promise को सच में रोका नहीं जा सकता, बस wrapper में flag लगाकर उसका result ignore करते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: wrap original in a new promise
// Step 2: keep a `cancelled` flag + the wrapper's reject function
// Step 3: cancel() flips flag and rejects immediately

function makeCancellable(promise) {
  let cancelled = false;                              // has cancel() been called?
  let rejectWrapper;                                  // reject fn of the wrapper

  const wrapped = new Promise((resolve, reject) => {
    rejectWrapper = reject;                           // expose reject for cancel()
    promise.then(
      value => { if (!cancelled) resolve(value); },   // ignore value if cancelled
      error => { if (!cancelled) reject(error); }     // ignore error if cancelled
    );
  });

  return {
    promise: wrapped,                                 // use this instead of original
    cancel() {
      cancelled = true;                               // mark as cancelled
      rejectWrapper(new Error('Cancelled'));          // settle wrapper right away
    }
  };
}

// ============================================
// TEST CASES
// ============================================

const sleep = (ms, v) => new Promise(r => setTimeout(() => r(v), ms)); // fake task

(async () => {
  const a = makeCancellable(sleep(100, 'done'));      // will not be cancelled
  console.log(await a.promise);                       // Expected: done

  const b = makeCancellable(sleep(100, 'never seen')); // will be cancelled
  setTimeout(() => b.cancel(), 20);                   // cancel after 20ms
  try {
    await b.promise;
  } catch (e) {
    console.log(e.message);                           // Expected: Cancelled
  }

  // AbortSignal-aware sleep: really stops the timer
  const abortableSleep = (ms, signal) => new Promise((resolve, reject) => {
    const id = setTimeout(resolve, ms, 'ok');         // normal completion
    signal.addEventListener('abort', () => {          // on abort:
      clearTimeout(id);                               // stop the work itself
      reject(new Error('Aborted'));                   // reject caller
    }, { once: true });
  });
  const ctrl = new AbortController();                 // controller to cancel
  setTimeout(() => ctrl.abort(), 20);                 // abort after 20ms
  await abortableSleep(1000, ctrl.signal).catch(e => console.log(e.message)); // Expected: Aborted
})();
// Console order:
// done
// Cancelled
// Aborted
```

---

## 🔍 Why This Works (3 lines max)
A promise settles only once, so the first `reject` from `cancel()` wins and later resolves are ignored. The flag stops late values from leaking into your code, but the original work still runs.
हिंदी: Promise एक ही बार settle होता है, इसलिए cancel का reject पहले आकर बाकी result दबा देता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Cancel via a token object passed into the async function
async function task(token) {
  for (let i = 0; i < 5; i++) {
    if (token.cancelled) throw new Error('Cancelled'); // check between steps
    await new Promise(r => setTimeout(r, 10));         // do a chunk of work
  }
  return 'finished';
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: believing promise.cancel() exists, or that the work stops
promise.cancel(); // TypeError — no such method

// ✅ Correct: wrap it, or use AbortController so the work itself stops
```

---

## 🎯 Interview Tip (1 line)
Say: "Promises are not cancellable by design; the standard answer is AbortController/AbortSignal."

---

## 🔗 Related Questions
→ Q205 (timeout) | Q219 (abort fetch) | Q213 (polling) | Q214 (debounce async)
