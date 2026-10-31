---

# Q184. Build Request Queue
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a `RequestQueue(concurrency)` that accepts async tasks, runs at most `concurrency` at once, and returns a promise for each task's result (FIFO order).

```javascript
const q = new RequestQueue(2);
q.add(() => fetch('/a')); q.add(() => fetch('/b')); q.add(() => fetch('/c')); // c waits
```

---

## 💡 Quick Concept (2 lines only)
Keep a waiting list and a running counter; when a task finishes, start the next waiting one.
हिंदी: एक समय में सिर्फ N requests चलती हैं, बाकी queue में इंतज़ार करती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class RequestQueue {
  constructor(concurrency = 2) {
    this.concurrency = concurrency;              // Step 1: max parallel tasks
    this.running = 0;                            // currently running count
    this.waiting = [];                           // FIFO list of pending jobs
  }

  add(task) {
    return new Promise((resolve, reject) => {    // Step 2: caller gets a promise
      this.waiting.push({ task, resolve, reject }); // store job
      this._next();                              // try to start
    });
  }

  _next() {
    while (this.running < this.concurrency && this.waiting.length) { // Step 3: free slot?
      const { task, resolve, reject } = this.waiting.shift(); // take oldest job
      this.running++;                            // occupy slot
      task()
        .then(resolve, reject)                   // pass result / error to caller
        .finally(() => { this.running--; this._next(); }); // Step 4: free slot, start next
    }
  }
}

// ============================================
// TEST CASES
// ============================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const job = (name, ms) => async () => {
  console.log('start', name);                    // log start
  await sleep(ms);                               // simulate request
  console.log('end', name);                      // log end
  return name.toUpperCase();                     // result
};

const q = new RequestQueue(2);
Promise.all([q.add(job('a', 30)), q.add(job('b', 10)), q.add(job('c', 10))])
  .then((r) => console.log(r));
// Expected:
// start a
// start b
// end b
// start c
// end c
// end a
// [ 'A', 'B', 'C' ]
```

---

## 🔍 Why This Works (3 lines max)
`running` never exceeds `concurrency` because `_next` only starts jobs while a slot is free. Finishing a job frees a slot and pulls the next one automatically.
हिंदी: Task खत्म होते ही slot खाली होता है और अगला waiting task अपने आप शुरू हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Sequential queue (concurrency = 1) using a promise chain
let chain = Promise.resolve();                   // tail of the queue
const addSeq = (task) => (chain = chain.then(task, task)); // run after previous, even if it failed
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to decrement `running` on failure -> queue gets stuck
task().then((r) => { this.running--; resolve(r); });

// ✅ Correct: use finally so success AND failure free the slot
task().then(resolve, reject).finally(() => { this.running--; this._next(); });
```

---

## 🎯 Interview Tip (1 line)
Explain the invariant "running <= concurrency" and that errors must also release the slot.

---

## 🔗 Related Questions
→ Q095 (async queue) | Q203 (limit concurrent promises) | Q216 (queue async tasks) | Q217 (batch API calls)
