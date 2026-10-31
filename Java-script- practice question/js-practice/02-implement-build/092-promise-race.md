---

# Q092. Implement Promise.race
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `myRace(promises)` that returns a Promise settling as soon as the FIRST input promise settles (resolve or reject), with that value or reason.

```javascript
myRace([slow, fast]).then(console.log); // result of whichever finishes first
```

---

## 💡 Quick Concept (2 lines only)
Attach `resolve` and `reject` of one outer promise to every input. First to settle wins; later calls are ignored automatically.
हिंदी: race में जो promise सबसे पहले पूरा या fail हो, वही result बन जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: return a new Promise
// Step 2: loop over inputs, wrap each with Promise.resolve
// Step 3: forward first settle to outer resolve/reject

function myRace(promises) {
  return new Promise((resolve, reject) => {       // outer promise
    for (const p of promises) {                   // iterate all inputs
      Promise.resolve(p).then(resolve, reject);   // first to settle wins
    }
  });
}

// ============================================
// TEST CASES
// ============================================

const delay = (ms, val, fail) => new Promise((res, rej) =>
  setTimeout(() => (fail ? rej(val) : res(val)), ms));   // helper timer promise

(async () => {
  console.log(await myRace([delay(100, 'slow'), delay(20, 'fast')])); // Expected: fast

  try {
    await myRace([delay(100, 'ok'), delay(10, 'err', true)]);
  } catch (e) {
    console.log(e);                                // Expected: err
  }

  console.log(await myRace([1, delay(10, 'x')]));  // Expected: 1  (plain value wins)

  myRace([]).then(() => console.log('never'));     // empty array => stays pending forever
})();
```

---

## 🔍 Why This Works (3 lines max)
A promise can settle only once, so after the first `resolve`/`reject`, the rest are no-ops. `Promise.resolve` lets plain values work too.
हिंदी: Promise सिर्फ एक बार settle होता है, इसलिए पहला ही जीतता है।

---

## ⚡ Alternative Solution
```javascript
// Practical use: timeout wrapper built with race
const withTimeout = (promise, ms) =>
  myRace([promise, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms))]);

withTimeout(delay(200, 'late'), 50).catch(e => console.log(e.message)); // Expected: timeout
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: awaiting in a loop makes it sequential, not a race
async function bad(promises) {
  for (const p of promises) return await p;   // just returns the first input
}

// ✅ Correct: attach handlers to ALL promises at once (see solution)
```

---

## 🎯 Interview Tip (1 line)
Mention that an empty array never settles, and show the timeout pattern as the real use case.

---

## 🔗 Related Questions
→ Q091 (Promise.all) | Q093 (allSettled) | Q094 (any) | Q205 (timeout a promise)
