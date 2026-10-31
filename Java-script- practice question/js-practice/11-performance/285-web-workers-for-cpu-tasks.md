---

# Q285. Web Workers for CPU Tasks
# Category: Performance
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Offload a CPU-heavy task (count primes up to 200,000) to a worker so the main thread stays responsive. Use Node's `worker_threads` (same idea as browser Web Workers).

---

## 💡 Quick Concept (2 lines only)
Workers run JS on a separate thread and communicate through messages, so heavy loops don't freeze the main thread/UI.
हिंदी: Worker अलग thread पर भारी काम करता है और message से result भेजता है, UI अटकता नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Worker code computes and posts the result
// Step 2: Main thread wraps worker in a Promise
// Step 3: Main thread keeps running while waiting

const { Worker } = require('worker_threads');     // Node's worker API

const workerCode = `
  const { parentPort, workerData } = require('worker_threads'); // worker side
  let count = 0;                                   // prime counter
  for (let n = 2; n <= workerData; n++) {          // heavy loop
    let isPrime = true;                            // assume prime
    for (let d = 2; d * d <= n; d++) {             // trial division
      if (n % d === 0) { isPrime = false; break; } // composite
    }
    if (isPrime) count++;                          // tally prime
  }
  parentPort.postMessage(count);                   // send result to main
`;

function countPrimes(limit) {
  return new Promise((resolve, reject) => {
    const w = new Worker(workerCode, { eval: true, workerData: limit }); // spawn thread
    w.on('message', resolve);                      // result arrives
    w.on('error', reject);                         // worker crashed
  });
}

// ============================================
// TEST CASES
// ============================================

countPrimes(200000).then((n) => console.log('primes:', n)); // Expected (later): primes: 17984
console.log('main thread free');                    // Expected (first): main thread free
setTimeout(() => console.log('timer ran'), 0);     // Expected: timer ran (before primes, not blocked)
```

---

## 🔍 Why This Works (3 lines max)
The loop runs in a separate thread with its own event loop, so the main thread's call stack stays free. Data is copied via `postMessage` (structured clone).
हिंदी: भारी loop दूसरे thread में चलता है, main thread अपना काम करता रहता है।

---

## ⚡ Alternative Solution
```javascript
// Browser version (two files):
// main.js:   const w = new Worker('worker.js');
//            w.postMessage(200000);
//            w.onmessage = (e) => console.log(e.data);
// worker.js: onmessage = (e) => { /* heavy loop */ postMessage(result); };
// Tip: transfer big buffers with postMessage(buf, [buf]) to avoid copying.
console.log('see browser comments'); // Expected: see browser comments
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: heavy loop on main thread → UI freezes, timers/clicks delayed
// for (let i = 0; i < 1e10; i++) {}

// ✅ Correct: move to a Worker (workers can't touch the DOM — send data back)
```

---

## 🎯 Interview Tip (1 line)
Say workers suit CPU-bound work, not I/O (async already handles I/O), and message passing copies data.

---

## 🔗 Related Questions
→ Q240 (Web worker basics) | Q163 (Event loop) | Q220 (Stream large data)
