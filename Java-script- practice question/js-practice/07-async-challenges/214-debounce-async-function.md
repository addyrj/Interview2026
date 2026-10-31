---

# Q214. Debounce an Async Function
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Create `debounceAsync(fn, wait)`. Rapid calls should run `fn` only once (with the LAST arguments) after `wait` ms of silence. Every caller must get a promise that resolves with that single result.

```javascript
const search = debounceAsync(apiSearch, 100);
search('a'); search('ab'); search('abc'); // apiSearch runs once with 'abc'
```

---

## 💡 Quick Concept (2 lines only)
Normal debounce returns nothing. For async, keep a list of pending `resolve/reject` pairs and settle them all when the delayed call finally runs.
हिंदी: Async debounce में सभी callers के promises जमा रखो और आखिरी call के result से सबको resolve करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: on every call, reset the timer
// Step 2: remember each caller's resolve/reject
// Step 3: when timer fires, run fn once and settle everyone

function debounceAsync(fn, wait) {
  let timerId = null;                                 // active timer
  let pending = [];                                   // waiting callers { resolve, reject }

  return function (...args) {
    return new Promise((resolve, reject) => {
      pending.push({ resolve, reject });              // register this caller
      clearTimeout(timerId);                          // cancel previous timer
      timerId = setTimeout(async () => {              // start a fresh countdown
        const callers = pending;                      // snapshot waiting callers
        pending = [];                                 // reset for next burst
        try {
          const result = await fn.apply(this, args);  // run once with LAST args
          callers.forEach(c => c.resolve(result));    // everyone gets the result
        } catch (err) {
          callers.forEach(c => c.reject(err));        // everyone gets the error
        }
      }, wait);
    });
  };
}

// ============================================
// TEST CASES
// ============================================

let apiCalls = 0;                                     // how many times API really ran
const apiSearch = async q => {
  apiCalls++;                                         // count real calls
  await new Promise(r => setTimeout(r, 10));          // fake latency
  return `result:${q}`;
};

(async () => {
  const search = debounceAsync(apiSearch, 50);        // 50ms debounce

  const results = await Promise.all([search('a'), search('ab'), search('abc')]); // burst
  console.log(results);                               // Expected: [ 'result:abc', 'result:abc', 'result:abc' ]
  console.log('api calls:', apiCalls);                // Expected: api calls: 1

  await new Promise(r => setTimeout(r, 80));          // wait out the debounce window
  console.log(await search('xyz'));                   // Expected: result:xyz
  console.log('api calls:', apiCalls);                // Expected: api calls: 2
})();
```

---

## 🔍 Why This Works (3 lines max)
Each call restarts the timer, so only the final one fires. Saving every `resolve/reject` means earlier callers are not left with a promise that never settles.
हिंदी: हर call timer reset करता है, और सारे pending promises एक ही result से resolve होते हैं।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Superseded callers get a "stale" rejection instead of the shared result
function debounceLatest(fn, wait) {
  let timerId, lastReject;
  return (...args) => new Promise((resolve, reject) => {
    clearTimeout(timerId);                            // cancel earlier timer
    if (lastReject) lastReject(new Error('superseded')); // reject the older caller
    lastReject = reject;                              // remember this caller
    timerId = setTimeout(() => fn(...args).then(resolve, reject), wait);
  });
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: plain debounce — earlier callers' promises hang forever
const debounced = debounce(fn, 100);
await debounced('a'); // may never resolve if a newer call arrives

// ✅ Correct: track pending resolvers (above) or reject stale callers
```

---

## 🎯 Interview Tip (1 line)
Mention race conditions too: ignore out-of-order responses (latest-wins) or abort the previous request.

---

## 🔗 Related Questions
→ Q081 (implement debounce) | Q181 (search with debounce) | Q232 (debounce input) | Q215 (memoize async)
