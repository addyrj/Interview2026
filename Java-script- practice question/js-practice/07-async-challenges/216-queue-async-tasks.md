---

# Q216. Queue Async Tasks
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build an `AsyncQueue` class. `add(task)` returns a promise for that task's result. Tasks run in FIFO order with a configurable `concurrency`. Tasks may be added at any time, even while others run.

```javascript
const q = new AsyncQueue(1);
q.add(() => job('A')).then(console.log);
q.add(() => job('B')).then(console.log);
```

---

## 💡 Quick Concept (2 lines only)
Keep an array queue and a `running` counter. After each task finishes (or on `add`), start the next while `running < concurrency`.
हिंदी: Queue में tasks जमा रखो और `running < concurrency` होने पर अगला task शुरू करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: store tasks with their resolve/reject in a FIFO array
// Step 2: _next() starts tasks while there is free capacity
// Step 3: when a task ends, decrement running and call _next() again

class AsyncQueue {
  constructor(concurrency = 1) {
    this.concurrency = concurrency;                   // max parallel tasks
    this.running = 0;                                 // tasks currently running
    this.queue = [];                                  // waiting tasks (FIFO)
  }

  add(task) {
    return new Promise((resolve, reject) => {         // caller gets a promise
      this.queue.push({ task, resolve, reject });     // enqueue
      this._next();                                   // try to start immediately
    });
  }

  _next() {
    while (this.running < this.concurrency && this.queue.length) { // free slot + work
      const { task, resolve, reject } = this.queue.shift();        // oldest task first
      this.running++;                                 // occupy a slot
      task()
        .then(resolve, reject)                        // pass result/error to caller
        .finally(() => {
          this.running--;                             // free the slot
          this._next();                               // pull next task
        });
    }
  }
}

// ============================================
// TEST CASES
// ============================================

const job = (name, ms) => () => new Promise(resolve => {
  console.log(`start ${name}`);                       // when it begins
  setTimeout(() => { console.log(`end ${name}`); resolve(name); }, ms); // when it ends
});

(async () => {
  const q = new AsyncQueue(1);                        // one at a time
  const results = await Promise.all([
    q.add(job('A', 60)),
    q.add(job('B', 20)),
    q.add(job('C', 10)),
  ]);
  console.log(results);                               // Expected: [ 'A', 'B', 'C' ]
})();
// Console order:
// start A
// end A
// start B
// end B
// start C
// end C
// [ 'A', 'B', 'C' ]
```

---

## 🔍 Why This Works (3 lines max)
`running` caps concurrency and `_next()` is called both on `add` and after every finish, so the queue drains itself. Wrapping each task in a promise lets callers `await` their own result.
हिंदी: हर task खत्म होते ही `_next()` चलता है, इसलिए queue अपने आप खाली होती रहती है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Concurrency 1 only: chain on a single promise tail
class SerialQueue {
  tail = Promise.resolve();                           // end of the chain
  add(task) {
    const run = this.tail.then(task);                 // run after previous finishes
    this.tail = run.catch(() => {});                  // keep chain alive after errors
    return run;                                       // caller sees real result/error
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to call _next() in finally -> queue stalls after first error
task().then(resolve, reject);

// ✅ Correct: always release the slot and continue, success OR failure
task().then(resolve, reject).finally(() => { this.running--; this._next(); });
```

---

## 🎯 Interview Tip (1 line)
Mention priorities, pause/resume, and `drain()` hooks as natural extensions.

---

## 🔗 Related Questions
→ Q095 (async queue) | Q184 (request queue) | Q203 (limit concurrent) | Q217 (batch API calls)
