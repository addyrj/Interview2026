---

# Q204. Retry a Failed Promise
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `retry(fn, retries, delay)` that calls an async function. If it rejects, wait `delay` ms and try again, up to `retries` extra times. If all attempts fail, reject with the last error.

```javascript
retry(() => fetchData(), 3, 100).then(console.log).catch(console.error);
```

---

## 💡 Quick Concept (2 lines only)
Loop attempts with `try/catch`; on failure sleep then retry; after the last attempt rethrow the error.
हिंदी: Fail होने पर थोड़ा रुककर दोबारा try करो, और आखिरी बार भी fail हो तो error फेंक दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: loop from attempt 0 up to `retries` (total = retries + 1 calls)
// Step 2: try fn(); return on success
// Step 3: on failure, rethrow if last attempt, else sleep and loop

const sleep = ms => new Promise(r => setTimeout(r, ms)); // tiny delay helper

async function retry(fn, retries = 3, delay = 100) {
  let lastError;                                      // remember the latest failure
  for (let attempt = 0; attempt <= retries; attempt++) { // 1 try + `retries` retries
    try {
      return await fn(attempt);                       // success -> return immediately
    } catch (err) {
      lastError = err;                                // store error
      if (attempt < retries) await sleep(delay);      // wait before next attempt
    }
  }
  throw lastError;                                    // all attempts failed
}

// ============================================
// TEST CASES
// ============================================

// Flaky function: fails twice, succeeds on the 3rd call
let calls = 0;                                        // counts invocations
const flaky = async () => {
  calls++;                                            // count this call
  console.log(`call ${calls}`);                       // show each attempt
  if (calls < 3) throw new Error('boom');             // fail first two times
  return 'success';                                   // then succeed
};

(async () => {
  console.log(await retry(flaky, 3, 50));             // Expected: call 1, call 2, call 3, success

  try {
    await retry(async () => { throw new Error('always fails'); }, 2, 10); // never succeeds
  } catch (e) {
    console.log('gave up:', e.message);               // Expected: gave up: always fails
  }
})();
// Console order:
// call 1
// call 2
// call 3
// success
// gave up: always fails
```

---

## 🔍 Why This Works (3 lines max)
`return await` inside `try` makes rejections land in `catch`. We only sleep between attempts, never after the last one, and rethrow the final error so callers can handle it.
हिंदी: `try/catch` हर failure पकड़ता है; आखिरी attempt के बाद error बाहर फेंक दिया जाता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Exponential backoff: 100ms, 200ms, 400ms ...
async function retryBackoff(fn, retries = 3, base = 100) {
  try {
    return await fn();                                // try once
  } catch (err) {
    if (retries === 0) throw err;                     // out of retries
    await new Promise(r => setTimeout(r, base));      // wait current delay
    return retryBackoff(fn, retries - 1, base * 2);   // recurse with doubled delay
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `return fn()` without await — rejection skips catch, no retry happens
try { return fn(); } catch (e) { /* never runs for async errors */ }

// ✅ Correct: await inside try so the rejection is caught
try { return await fn(); } catch (e) { /* retry here */ }
```

---

## 🎯 Interview Tip (1 line)
Mention exponential backoff + jitter, and only retry transient errors (network/5xx), never 4xx.

---

## 🔗 Related Questions
→ Q089 (implement retry) | Q183 (retry API call) | Q205 (timeout a promise) | Q159 (retry logic)
