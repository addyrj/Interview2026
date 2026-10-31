---

# Q095. Implement Async Queue
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement an `AsyncQueue` class with a concurrency limit. `add(task)` takes an async function and returns a Promise of its result. At most `concurrency` tasks run at the same time; others wait in order.

```javascript
const q = new AsyncQueue(2);
q.add(() => fetchSomething());
```

---

## 💡 Quick Concept (2 lines only)
Keep a waiting list and a running counter. When a task finishes, start the next waiting one.
हिंदी: Queue में tasks लाइन में रहते हैं और limit तक ही एक साथ चलते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: store concurrency, waiting list, running count
// Step 2: add() returns a promise and pushes the task
// Step 3: next() starts tasks while slots are free
// Step 4: when a task ends, decrement and call next() again

class AsyncQueue {
  constructor(concurrency = 1) {
    this.concurrency = concurrency;     // max parallel tasks
    this.running = 0;                   // currently running tasks
    this.waiting = [];                  // pending task list (FIFO)
  }

  add(task) {
    return new Promise((resolve, reject) => {   // caller gets result promise
      this.waiting.push({ task, resolve, reject }); // store task with its callbacks
      this.next();                              // try to start immediately
    });
  }

  next() {
    while (this.running < this.concurrency && this.waiting.length) { // free slots?
      const { task, resolve, reject } = this.waiting.shift(); // take oldest task
      this.running++;                           // occupy a slot
      task()                                    // run the async task
        .then(resolve, reject)                  // pass result/error to caller
        .finally(() => {
          this.running--;                       // free the slot
          this.next();                          // start the next waiting task
        });
    }
  }
}

// ============================================
// TEST CASES
// ============================================

const wait = (ms, v) => new Promise(r => setTimeout(() => r(v), ms)); // timer helper
const q = new AsyncQueue(2);                    // 2 at a time
const t0 = Date.now();                          // start time
const log = (m) => console.log(m, Math.round((Date.now() - t0) / 100) * 100 + 'ms');

Promise.all([
  q.add(() => wait(200, 'A').then(v => { log(v); return v; })), // starts at 0
  q.add(() => wait(200, 'B').then(v => { log(v); return v; })), // starts at 0
  q.add(() => wait(200, 'C').then(v => { log(v); return v; })), // waits until A/B finish
]).then(r => console.log(r));
// Expected: A 200ms
// Expected: B 200ms
// Expected: C 400ms
// Expected: [ 'A', 'B', 'C' ]
```

---

## 🔍 Why This Works (3 lines max)
`running` never exceeds `concurrency` because `next()` checks it before starting. Every finished task calls `next()` so the queue drains.
हिंदी: next() हर बार slot चेक करता है, और task खत्म होते ही अगला task शुरू कर देता है।

---

## ⚡ Alternative Solution
```javascript
// Simple sequential queue by chaining promises (concurrency = 1)
class SerialQueue {
  constructor() { this.tail = Promise.resolve(); }     // end of chain
  add(task) {
    const result = this.tail.then(() => task());       // run after previous
    this.tail = result.catch(() => {});                // keep chain alive on error
    return result;                                     // caller gets result
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to call next() on failure — queue stalls forever
task().then(() => { this.running--; this.next(); }); // error path never frees slot

// ✅ Correct: use .finally() so success and failure both free the slot
```

---

## 🎯 Interview Tip (1 line)
Explain the invariant "running <= concurrency", and that errors must also release a slot.

---

## 🔗 Related Questions
→ Q203 (limit concurrent promises) | Q216 (queue async tasks) | Q184 (request queue)
