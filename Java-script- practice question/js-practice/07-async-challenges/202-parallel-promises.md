---

# Q202. Run Promises in Parallel
# Category: Async Challenges
# Difficulty: ⭐ Easy

---

## ❓ Question
Given an array of async tasks (functions that return Promises), start ALL of them at the same time and collect the results in the ORIGINAL order (not completion order).

```javascript
runInParallel([() => taskA(), () => taskB(), () => taskC()])
  .then(results => console.log(results));
// [A, B, C] — same order as input, total time = slowest task
```

---

## 💡 Quick Concept (2 lines only)
Parallel = call every task first (so all timers start), then wait for all with `Promise.all`. Results keep input order even if tasks finish in a different order.
हिंदी: Parallel में सारे tasks एक साथ शुरू होते हैं, और `Promise.all` result को input के order में देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: call every task immediately via map (all timers start now)
// Step 2: Promise.all waits until every promise is fulfilled
// Step 3: results array keeps the input order

function runInParallel(tasks) {                       // takes an array of functions
  return Promise.all(tasks.map(task => task()));      // start all, wait for all
}

// ============================================
// TEST CASES
// ============================================

// Fake async task: finishes after `delay` ms
const createTask = (id, delay) => () => new Promise(resolve => { // returns a task fn
  setTimeout(() => {                                  // simulate async work
    console.log(`Task ${id} done`);                   // log completion order
    resolve(`result_${id}`);                          // resolve with a value
  }, delay);                                          // wait `delay` ms
});

const tasks = [createTask(1, 300), createTask(2, 100), createTask(3, 200)]; // 3 tasks

const start = Date.now();                             // remember start time
runInParallel(tasks).then(results => {                // run all together
  const took = Math.round((Date.now() - start) / 100) * 100; // round to nearest 100ms
  console.log(results);                               // Expected: [ 'result_1', 'result_2', 'result_3' ]
  console.log(`~${took}ms`);                          // Expected: ~300ms (not 600ms)
});
// Console order:
// Task 2 done
// Task 3 done
// Task 1 done
// [ 'result_1', 'result_2', 'result_3' ]
// ~300ms
```

---

## 🔍 Why This Works (3 lines max)
`tasks.map(task => task())` invokes every function right away, so all timers run together. `Promise.all` resolves when the slowest finishes and returns values by index, not by finish time.
हिंदी: सारे tasks साथ चलते हैं, इसलिए कुल समय सबसे धीमे task के बराबर होता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Parallel with async/await (same behaviour):
async function runInParallelAwait(tasks) {
  const promises = tasks.map(t => t());   // start everything first
  return await Promise.all(promises);     // then await once
}

// Parallel but never fail-fast (collect failures too):
const runSettled = tasks => Promise.allSettled(tasks.map(t => t()));
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: await inside a loop makes it sequential
const results = [];
for (const t of tasks) results.push(await t()); // 600ms, not 300ms

// ✅ Correct: start all first, await together
const fast = await Promise.all(tasks.map(t => t()));
```

---

## 🎯 Interview Tip (1 line)
Say: "Promise.all is fail-fast — one rejection rejects everything; use allSettled if I need every outcome."

---

## 🔗 Related Questions
→ Q201 (sequential) | Q203 (limit concurrent) | Q208 (multiple errors) | Q091 (implement Promise.all)
