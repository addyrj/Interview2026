---

# Q089. Implement Retry Function
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `retry(fn, retries, delay)` where `fn` returns a Promise. If it rejects, retry up to `retries` times, waiting `delay` ms between tries. If all attempts fail, reject with the last error.

```javascript
retry(fetchData, 3, 500).then(console.log).catch(console.error);
```

---

## 💡 Quick Concept (2 lines only)
Try the call; on failure wait and call again until attempts run out. Use async/await with a loop for clean code.
हिंदी: Fail होने पर थोड़ा रुककर function दोबारा चलाओ, जब तक tries खत्म न हों।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: helper to wait for ms
// Step 2: loop from 0..retries (first try + retries)
// Step 3: return on success
// Step 4: on failure wait, and throw if last attempt

const sleep = (ms) => new Promise((res) => setTimeout(res, ms)); // wait helper

async function retry(fn, retries, delay) {
  let lastError;                                    // remember the latest error
  for (let attempt = 0; attempt <= retries; attempt++) { // 1 try + N retries
    try {
      return await fn(attempt);                     // success => return result
    } catch (err) {
      lastError = err;                              // save error
      if (attempt < retries) await sleep(delay);    // wait before the next attempt
    }
  }
  throw lastError;                                  // all attempts failed
}

// ============================================
// TEST CASES
// ============================================

let calls = 0;                                      // counts attempts
const flaky = async () => {                         // fails twice, then succeeds
  calls++;
  if (calls < 3) throw new Error('fail ' + calls);
  return 'success';
};

const alwaysFail = async () => { throw new Error('boom'); };

(async () => {
  console.log(await retry(flaky, 3, 10));           // Expected: success
  console.log(calls);                               // Expected: 3
  try {
    await retry(alwaysFail, 2, 10);                 // fails 3 times total
  } catch (e) {
    console.log(e.message);                         // Expected: boom
  }
})();
```

---

## 🔍 Why This Works (3 lines max)
Loop gives (1 + retries) attempts. `return await` ensures rejections are caught inside the try block. The last error is rethrown at the end.
हिंदी: Loop से कई attempts मिलते हैं, और आखिरी error अंत में throw होता है।

---

## ⚡ Alternative Solution
```javascript
// Exponential backoff: delay doubles each time (100, 200, 400...)
async function retryBackoff(fn, retries, baseDelay) {
  for (let i = 0; ; i++) {                          // infinite loop with manual exit
    try { return await fn(); }                      // success
    catch (e) {
      if (i >= retries) throw e;                    // out of tries
      await sleep(baseDelay * 2 ** i);              // 1x, 2x, 4x...
    }
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `return fn()` without await — rejection escapes the try/catch
async function bad(fn) {
  try { return fn(); } catch (e) { /* never runs for async errors */ }
}

// ✅ Correct: `return await fn()` so catch handles the rejection
```

---

## 🎯 Interview Tip (1 line)
Mention exponential backoff + jitter, and retrying only on retryable errors (network/5xx, not 4xx).

---

## 🔗 Related Questions
→ Q090 (sleep) | Q183 (retry API call) | Q204 (retry failed promise)
