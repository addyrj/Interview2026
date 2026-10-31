---

# Q212. Race with Fallback
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Call a primary source. If it fails OR takes longer than `ms`, use a fallback source instead. Return whichever valid data arrives (primary preferred).

```javascript
await fetchWithFallback(primaryApi, backupApi, 200);
```

---

## 💡 Quick Concept (2 lines only)
Race the primary against a timer; if the timer wins or primary rejects, call the fallback. Plain `Promise.race` is not enough because a fast rejection would also "win".
हिंदी: Primary धीमा या fail हो तो fallback चलाओ; `race` अकेला काफी नहीं क्योंकि fast error भी जीत जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: wrap primary in a timeout that rejects after `ms`
// Step 2: on any failure (error or timeout) call fallback
// Step 3: clear the timer once primary settles

async function fetchWithFallback(primary, fallback, ms) {
  let timerId;                                        // so we can clear it
  const timeout = new Promise((_, reject) => {
    timerId = setTimeout(() => reject(new Error('timeout')), ms); // slow primary -> reject
  });
  try {
    return await Promise.race([primary(), timeout]);  // primary wins if fast and OK
  } catch (err) {
    console.log(`primary failed (${err.message}), using fallback`); // log why
    return fallback();                                // use backup source
  } finally {
    clearTimeout(timerId);                            // always cleanup
  }
}

// ============================================
// TEST CASES
// ============================================

const source = (value, ms, shouldFail = false) => () => new Promise((resolve, reject) =>
  setTimeout(() => shouldFail ? reject(new Error('api error')) : resolve(value), ms)
);

(async () => {
  console.log(await fetchWithFallback(source('primary', 50), source('backup', 10), 200));
  // Expected: primary

  console.log(await fetchWithFallback(source('primary', 500), source('backup', 10), 100));
  // Expected: primary failed (timeout), using fallback
  //           backup

  console.log(await fetchWithFallback(source('primary', 20, true), source('backup', 10), 100));
  // Expected: primary failed (api error), using fallback
  //           backup
})();
```

---

## 🔍 Why This Works (3 lines max)
`Promise.race` rejects on a slow primary (timer) or on a primary error, and both land in `catch`, where the fallback runs. `finally` clears the timer so nothing leaks.
हिंदी: Timeout या error दोनों `catch` में जाते हैं, वहीं fallback call होता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// "Hedged request": fire fallback after a delay, take the FIRST SUCCESS
const hedged = (primary, fallback, ms) =>
  Promise.any([
    primary(),                                        // start primary now
    new Promise(r => setTimeout(r, ms)).then(fallback) // start fallback after ms
  ]);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no catch -> primary error never triggers the fallback
const data = await Promise.race([primary(), timeout]);

// ✅ Correct: try/catch (or .catch(fallback)) around the race
```

---

## 🎯 Interview Tip (1 line)
Mention hedged requests (Promise.any) as the latency-optimised variant used by large systems.

---

## 🔗 Related Questions
→ Q205 (timeout) | Q092 (implement race) | Q094 (implement any) | Q204 (retry)
