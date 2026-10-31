---

# Q090. Implement Sleep Function
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `sleep(ms)` that returns a Promise resolving after `ms` milliseconds, so you can `await sleep(1000)` inside async functions.

```javascript
await sleep(1000); // pauses this async function for 1 second
```

---

## 💡 Quick Concept (2 lines only)
Wrap `setTimeout` in a Promise and resolve in its callback. It pauses only the async function, not the whole thread.
हिंदी: sleep, setTimeout को Promise में लपेटता है ताकि await से रुक सकें।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: return a new Promise
// Step 2: inside, call setTimeout with resolve
// Step 3: caller uses await to pause

function sleep(ms) {
  return new Promise((resolve) => {        // create promise
    setTimeout(resolve, ms);               // resolve after ms milliseconds
  });
}

// ============================================
// TEST CASES
// ============================================

(async () => {
  const start = Date.now();                // note start time
  console.log('start');                    // Expected: start
  await sleep(200);                        // pause ~200ms
  const elapsed = Date.now() - start;      // measure time passed
  console.log(elapsed >= 190);             // Expected: true
  console.log('end');                      // Expected: end

  const value = await sleep(50).then(() => 'done'); // chain with then
  console.log(value);                      // Expected: done
})();
```

---

## 🔍 Why This Works (3 lines max)
`setTimeout` schedules `resolve`; the Promise stays pending until then. `await` suspends only this async function while the event loop keeps running.
हिंदी: Promise तब तक pending रहता है जब तक timer पूरा नहीं होता, बाकी program चलता रहता है।

---

## ⚡ Alternative Solution
```javascript
// Node 16+: built-in promise timers
const { setTimeout: nodeSleep } = require('node:timers/promises');

(async () => {
  await nodeSleep(50);                     // built-in sleep
  console.log('built-in sleep done');      // Expected: built-in sleep done
})();

// Sleep that resolves with a value
const sleepWith = (ms, val) => new Promise(r => setTimeout(() => r(val), ms));
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: busy-wait blocks the entire thread (UI/server freezes)
function badSleep(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}              // CPU burning loop
}

// ✅ Correct: non-blocking Promise + setTimeout
const goodSleep = (ms) => new Promise(r => setTimeout(r, ms));
```

---

## 🎯 Interview Tip (1 line)
Stress "non-blocking": sleep must not freeze the event loop — contrast with a busy-wait loop.

---

## 🔗 Related Questions
→ Q089 (retry) | Q081 (debounce) | Q213 (polling with async/await)
