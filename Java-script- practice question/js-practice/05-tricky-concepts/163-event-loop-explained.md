---

# Q163. Explain Event Loop with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Explain how the JavaScript event loop works. Show the order of sync code, microtasks (Promises), and macrotasks (setTimeout).

---

## 💡 Quick Concept (2 lines only)
JS is single-threaded: the call stack runs sync code first, then ALL microtasks (promises, queueMicrotask), then one macrotask (timers, I/O), and repeats.
हिंदी: Event loop पहले sync code, फिर सारे microtasks, फिर एक macrotask चलाता है — और यही चक्र दोहराता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Sync code runs on the call stack immediately
// Step 2: Promise callbacks go to microtask queue (high priority)
// Step 3: setTimeout callbacks go to macrotask queue (after microtasks)

console.log('1: sync start');                       // sync -> runs first

setTimeout(() => console.log('5: timeout 0'), 0);  // macrotask -> runs later

Promise.resolve()                                  // already resolved promise
  .then(() => {                                    // microtask 1
    console.log('3: promise 1');                   // runs after sync code
    return Promise.resolve();                      // schedule next link
  })
  .then(() => console.log('4: promise 2'));        // microtask chained after 1

queueMicrotask(() => console.log('3.5: microtask')); // another microtask, queued early

console.log('2: sync end');                        // sync -> runs before any async

// ============================================
// TEST CASES
// ============================================

// Run the file with node and observe the order:
// Expected:
// 1: sync start
// 2: sync end
// 3: promise 1
// 3.5: microtask
// 4: promise 2
// 5: timeout 0
```

---

## 🔍 Why This Works (3 lines max)
After each macrotask the engine drains the entire microtask queue before the next macrotask starts. So promises always beat `setTimeout(…, 0)`, even though both are "async".
हिंदी: हर macrotask के बाद पूरी microtask queue खाली होती है, इसलिए promise हमेशा setTimeout से पहले चलता है।

---

## ⚡ Alternative Solution
```javascript
// Starving the loop: a blocking sync loop delays timers
const start = Date.now();                          // record start time
setTimeout(() => {                                 // wants to run after 10ms
  console.log(Date.now() - start >= 100);          // Expected: true (delayed by block)
}, 10);
while (Date.now() - start < 100) {}                // block call stack for 100ms
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking setTimeout(fn, 0) runs immediately
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
console.log('sync');
// Output: sync, promise, timeout

// ✅ Remember order: sync -> microtasks -> macrotasks
```

---

## 🎯 Interview Tip (1 line)
Say: "Call stack, then microtask queue fully drained, then one macrotask, then render — and a long sync task blocks everything."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q016 (microtask vs macrotask) | Q017 (event loop mixed) | Q296 (call stack vs event loop)
