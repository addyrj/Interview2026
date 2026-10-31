---

# Q183. Build Retry API Call
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `fetchWithRetry(fn, { retries, delay })` that retries a failing API call with exponential backoff, but only for retryable errors (network / 5xx), not for 4xx.

```javascript
const data = await fetchWithRetry(() => getUser(1), { retries: 3, delay: 100 });
```

---

## 💡 Quick Concept (2 lines only)
Loop up to N attempts; on failure wait `delay * 2^attempt` then retry; rethrow the last error.
हिंदी: Fail होने पर बढ़ते delay (backoff) के साथ दोबारा try करो — 4xx errors पर retry मत करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms)); // Step 1: wait helper

const isRetryable = (err) => !err.status || err.status >= 500; // Step 2: network or 5xx only

async function fetchWithRetry(fn, { retries = 3, delay = 100 } = {}) {
  let lastError;                                 // remember last failure
  for (let attempt = 0; attempt <= retries; attempt++) { // Step 3: 1 try + N retries
    try {
      return await fn(attempt);                  // success -> return result
    } catch (err) {
      lastError = err;                           // save error
      if (!isRetryable(err) || attempt === retries) break; // Step 4: stop if not retryable / last
      await sleep(delay * 2 ** attempt);         // Step 5: exponential backoff
    }
  }
  throw lastError;                               // give up with last error
}

// ============================================
// TEST CASES
// ============================================

let calls = 0;                                   // count attempts
const flaky = async () => {
  calls++;                                       // track call
  if (calls < 3) throw Object.assign(new Error('Server down'), { status: 503 }); // fail twice
  return 'ok';                                   // third time works
};

const notFound = async () => { throw Object.assign(new Error('Not found'), { status: 404 }); };

(async () => {
  console.log(await fetchWithRetry(flaky, { retries: 3, delay: 10 })); // Expected: ok
  console.log('attempts:', calls);               // Expected: attempts: 3
  try { await fetchWithRetry(notFound, { retries: 3, delay: 10 }); }
  catch (e) { console.log(e.message); }          // Expected: Not found (no retries)
})();
```

---

## 🔍 Why This Works (3 lines max)
Each failure waits longer (10, 20, 40ms...) so a struggling server gets breathing room. Non-retryable errors break out immediately, saving time.
हिंदी: हर बार delay दोगुना होता है, और 404 जैसे errors पर तुरंत रुक जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// Recursive version
function retry(fn, n, delay) {
  return fn().catch((err) =>
    n <= 0 ? Promise.reject(err)                 // out of retries -> fail
           : sleep(delay).then(() => retry(fn, n - 1, delay * 2)) // wait then retry
  );
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: fixed instant retry hammers the server (and retries 4xx forever)
while (true) { try { return await fn(); } catch (e) {} }

// ✅ Correct: limited attempts + backoff (+ jitter in production) + retryable check
```

---

## 🎯 Interview Tip (1 line)
Say "exponential backoff with jitter, retry only idempotent/retryable errors, and cap attempts."

---

## 🔗 Related Questions
→ Q089 (retry function) | Q159 (retry logic) | Q204 (retry failed promise) | Q205 (timeout a promise)
