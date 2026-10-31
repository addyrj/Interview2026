---

# Q295. synchronous vs asynchronous
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain synchronous vs asynchronous JavaScript. Write code that mixes sync code, a `setTimeout`, a Promise and `async/await`, and predict the exact print order.

---

## 💡 Quick Concept (2 lines only)
Sync code runs line by line and blocks; async work (timers, network) is handed off and its callback runs later, after the sync code finishes.
हिंदी: Sync code एक के बाद एक चलता है और रुकावट बनता है; async काम बाद में callback से वापस आता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: all sync code runs first on the call stack
// Step 2: then microtasks (Promise .then, await continuation)
// Step 3: then macrotasks (setTimeout, setInterval)

// A helper that resolves after ms milliseconds (fake network call)
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms)); // wraps timer in a Promise

// An async function: runs sync until the first await
async function fetchUser() {
  console.log('3: inside fetchUser (still sync)'); // runs immediately when called
  await delay(10);                                  // pauses here, gives control back
  console.log('7: fetchUser resumed after await');  // runs after 10ms
}

// ============================================
// TEST CASES
// ============================================

console.log('1: start');                                   // sync
setTimeout(() => console.log('6: setTimeout 0'), 0);       // macrotask, runs later
Promise.resolve().then(() => console.log('5: promise'));   // microtask, runs before timers
fetchUser();                                                // logs "3" synchronously
console.log('4: end');                                      // sync, last sync line

// Expected output (in order):
// 1: start
// 3: inside fetchUser (still sync)
// 4: end
// 5: promise
// 6: setTimeout 0
// 7: fetchUser resumed after await
```

---

## 🔍 Why This Works (3 lines max)
The call stack must be empty before any queued callback runs. Microtasks (promises) are drained before the next macrotask (timers). `await` splits a function: code before it is sync, code after it is a microtask.
हिंदी: पहले पूरा sync code, फिर promises (microtask), फिर timers (macrotask) चलते हैं।

---

## ⚡ Alternative Solution
```javascript
// Callback style (old) vs async/await (modern) for the same async job
function loadCb(cb) { setTimeout(() => cb(null, 'data'), 5); } // callback version
loadCb((err, data) => console.log('callback:', data));          // callback: data

const loadP = () => new Promise((r) => setTimeout(() => r('data'), 5)); // promise version
(async () => {
  const data = await loadP();          // wait without blocking the thread
  console.log('async/await:', data);   // async/await: data
})();
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting the value right after an async call
let result;
setTimeout(() => { result = 42; }, 0);
console.log(result); // undefined — callback has not run yet

// ✅ Correct: use the value inside the callback / after await
(async () => {
  const value = await new Promise((r) => setTimeout(() => r(42), 0)); // wait for it
  console.log(value); // 42
})();
```

---

## 🎯 Interview Tip (1 line)
Say: "JS is single-threaded; async doesn't mean parallel — the event loop runs callbacks after the stack is empty, microtasks first."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q012 (async/await order) | Q016 (microtask vs macrotask) | Q296 (call stack vs event loop)
