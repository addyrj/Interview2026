---

# Q240. Web Worker Basics
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Run a heavy computation (sum of primes up to N) in a Web Worker so the UI doesn't freeze. Send N to the worker and receive the result with `postMessage`.

---

## 💡 Quick Concept (2 lines only)
A Web Worker runs JS on a separate thread with no DOM access; main thread and worker talk using `postMessage` and `onmessage`.
हिंदी: Web Worker अलग thread पर चलता है, DOM नहीं छू सकता, और `postMessage` से बात करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — file 1: worker.js
// ============================================

// Step 1: Listen for messages from main thread
// Step 2: Do heavy work
// Step 3: Post result back

self.onmessage = (e) => {                                // message from main thread
  const n = e.data;                                      // the number sent
  let sum = 0;                                           // running total
  for (let i = 2; i <= n; i++) {                         // check each number
    let isPrime = true;                                  // assume prime
    for (let j = 2; j * j <= i; j++) {                   // trial division
      if (i % j === 0) { isPrime = false; break; }       // found divisor
    }
    if (isPrime) sum += i;                               // add prime
  }
  self.postMessage(sum);                                 // send result back
};

// ============================================
// SOLUTION — file 2: main.js
// ============================================

const worker = new Worker('worker.js');                  // start worker thread

worker.onmessage = (e) => {                              // result received
  console.log('Sum of primes:', e.data);                 // show result
};
worker.onerror = (err) => {                              // worker crashed
  console.error('Worker error:', err.message);           // show error
};

console.log('Sending job...');                           // main thread stays free
worker.postMessage(100000);                              // send N to worker
console.log('UI still responsive');                      // prints immediately

// worker.terminate();                                   // call when no longer needed

// ============================================
// TEST CASES
// ============================================

// Test 1: console order -> Expected: "Sending job..." , "UI still responsive", then "Sum of primes: 454396537"
// Test 2: worker.postMessage(10)  -> Expected: "Sum of primes: 17" (2+3+5+7)
// Test 3: while worker runs, click buttons / type in input -> Expected: page stays responsive
// Test 4: inside worker.js try document.title -> Expected: ReferenceError (no DOM in workers)
```

---

## 🔍 Why This Works (3 lines max)
The loop runs on a different thread, so the main thread keeps rendering and handling events. Messages are copied with structured clone, so no shared state or race conditions. `terminate()` frees the thread.
हिंदी: भारी loop दूसरे thread पर चलता है, इसलिए main thread/UI अटकता नहीं।

---

## ⚡ Alternative Solution
```javascript
// Inline worker using Blob (no separate file needed)
const code = `onmessage = (e) => postMessage(e.data * 2);`; // worker source text
const blob = new Blob([code], { type: 'text/javascript' });   // wrap in Blob
const w = new Worker(URL.createObjectURL(blob));              // create worker from blob URL
w.onmessage = (e) => console.log(e.data);                     // Expected: 42
w.postMessage(21);                                            // send 21
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: running heavy loop on main thread -> UI freezes
for (let i = 0; i < 1e9; i++) {}

// ❌ Wrong: touching DOM/window inside a worker -> ReferenceError
// ✅ Correct: compute in worker, send data back, update DOM in main thread
```

---

## 🎯 Interview Tip (1 line)
Say: "Workers offload CPU-heavy tasks; communication is by message passing (structured clone, Transferable for big buffers), and there's no DOM access."

---

## 🔗 Related Questions
→ Q239 (service worker) | Q285 (web workers for CPU tasks) | Q163 (event loop)
