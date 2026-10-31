---

# Q159. Complete Retry Logic
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to retry an async task up to `retries` times with a delay.

```javascript
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function retry(fn, retries, delay) {
  for (let attempt = 0; attempt <= ____; attempt++) {
    try {
      return ____ fn();                         // success -> return
    } catch (err) {
      if (attempt === retries) ____ err;        // out of attempts
      await ____(delay);                        // wait then retry
    }
  }
}
```

---

## 💡 Quick Concept (2 lines only)
Wrap the call in try/catch inside a loop; on failure wait and try again, and rethrow after the last attempt.
हिंदी: loop में try/catch लगाओ, fail होने पर रुककर दोबारा कोशिश करो और आखिर में error फेंक दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const sleep = (ms) => new Promise(r => setTimeout(r, ms)); // Step 1: delay helper

async function retry(fn, retries, delay) {
  for (let attempt = 0; attempt <= retries; attempt++) {   // blank 1: 1 try + N retries
    try {
      return await fn();                                   // blank 2: await so errors are caught
    } catch (err) {
      if (attempt === retries) throw err;                  // blank 3: final failure
      await sleep(delay);                                  // blank 4: wait before next try
    }
  }
}

// ============================================
// TEST CASES
// ============================================

let n = 0;                                                 // counts attempts
const flaky = async () => { n++; if (n < 3) throw new Error('fail'); return 'ok'; }; // fails twice

retry(flaky, 3, 10).then(r => console.log(r, 'after', n, 'attempts')); // Expected: ok after 3 attempts

retry(async () => { throw new Error('always'); }, 1, 5)
  .catch(e => console.log('gave up:', e.message));         // Expected: gave up: always
```

---

## 🔍 Why This Works (3 lines max)
`await fn()` inside try turns rejections into catchable errors. The loop repeats until success or the last attempt rethrows the error.
हिंदी: `await` से rejection catch में आता है और आखिरी attempt पर error दोबारा throw होता है।

---

## ⚡ Alternative Solution
```javascript
// Exponential backoff: delay doubles each time
// await sleep(delay * 2 ** attempt);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `return fn()` without await inside try -> catch never sees rejections
// ✅ Correct: return await fn()
```

---

## 🎯 Interview Tip (1 line)
Say: "Add exponential backoff with jitter and only retry transient errors (5xx/network), never 4xx."

---

## 🔗 Related Questions
→ Q089 (implement retry) | Q090 (sleep) | Q183 (retry API call) | Q204 (retry failed promise)
