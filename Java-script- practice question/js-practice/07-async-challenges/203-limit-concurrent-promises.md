---

# Q203. Limit Concurrent Promises
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Run an array of async tasks but never have more than `limit` running at the same time. As soon as one finishes, start the next. Return results in input order.

```javascript
runWithLimit(tasks, 2).then(console.log);
// at most 2 tasks active at any moment
```

---

## 💡 Quick Concept (2 lines only)
Create `limit` "workers"; each worker loops, grabbing the next unstarted task index until none remain. Shared index = natural queue.
हिंदी: `limit` जितने workers बनाओ, हर worker खत्म होते ही अगला task उठा लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep a shared `next` index and a results array
// Step 2: each worker repeatedly takes the next task and awaits it
// Step 3: start `limit` workers and wait for all of them

async function runWithLimit(tasks, limit) {
  const results = new Array(tasks.length);            // pre-sized, keeps input order
  let next = 0;                                       // index of the next task to start

  async function worker() {                           // one worker = one "slot"
    while (next < tasks.length) {                     // until tasks are exhausted
      const index = next++;                           // claim an index (sync, so no race)
      results[index] = await tasks[index]();          // run it and store by index
    }
  }

  const workers = Array.from(                         // build `limit` workers
    { length: Math.min(limit, tasks.length) },        // never more than tasks
    worker                                            // each starts immediately
  );
  await Promise.all(workers);                         // wait for every worker to drain
  return results;                                     // ordered results
}

// ============================================
// TEST CASES
// ============================================

let running = 0;                                      // currently active tasks
let maxRunning = 0;                                   // peak concurrency seen

const createTask = (id, delay) => async () => {       // fake task
  running++;                                          // one more active
  maxRunning = Math.max(maxRunning, running);         // track the peak
  await new Promise(r => setTimeout(r, delay));       // simulate work
  running--;                                          // finished
  return `r${id}`;                                    // return value
};

const tasks = [300, 100, 250, 100, 100].map((d, i) => createTask(i + 1, d)); // 5 tasks

runWithLimit(tasks, 2).then(results => {
  console.log(results);                               // Expected: [ 'r1', 'r2', 'r3', 'r4', 'r5' ]
  console.log('max concurrent:', maxRunning);         // Expected: max concurrent: 2
});
```

---

## 🔍 Why This Works (3 lines max)
`next++` runs synchronously so two workers can never claim the same task. A finished worker immediately loops and pulls the next one, so exactly `limit` slots stay busy.
हिंदी: `next++` synchronous है इसलिए दो workers एक ही task नहीं उठाते; slot खाली होते ही नया task चलता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Promise.race pool (classic): keep a Set of in-flight promises
async function runWithLimitRace(tasks, limit) {
  const results = [];
  const executing = new Set();                        // in-flight promises
  for (const [i, task] of tasks.entries()) {
    const p = task().then(v => { results[i] = v; });  // store at index
    executing.add(p);
    p.finally(() => executing.delete(p));             // remove when settled
    if (executing.size >= limit) await Promise.race(executing); // wait for a free slot
  }
  await Promise.all(executing);                       // drain the rest
  return results;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: batching in chunks — a slow task blocks the whole batch
for (let i = 0; i < tasks.length; i += 2) {
  await Promise.all(tasks.slice(i, i + 2).map(t => t())); // idle slots wait for slowest
}

// ✅ Correct: worker pool — free slot is refilled immediately
await runWithLimit(tasks, 2);
```

---

## 🎯 Interview Tip (1 line)
Say: "Worker pool keeps all slots busy; chunking wastes time waiting on the slowest task per batch."

---

## 🔗 Related Questions
→ Q202 (parallel) | Q210 (async map with limit) | Q216 (queue async tasks) | Q184 (request queue)
