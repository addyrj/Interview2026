---

# Q201. Run Promises Sequentially
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Given an array of async tasks (functions that return Promises), run them one by one — each starts only after the previous one finishes. Collect all results in order.

```javascript
const tasks = [
  () => fetchUser(1),
  () => fetchUser(2),
  () => fetchUser(3)
];
runSequentially(tasks).then(results => console.log(results));
// [user1, user2, user3] — in order, each waits for previous
```

---

## 💡 Quick Concept (2 lines only)
Sequential = each promise starts after previous resolves. Use `for...of` with `await`, or `reduce` with promise chaining.
हिंदी: Sequential execution = पिछला promise complete होने के बाद ही अगला start होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION 1: for...of with await (clearest)
// ============================================

async function runSequentially(tasks) {
  const results = [];
  
  for (const task of tasks) {          // Step 1: iterate tasks one by one
    const result = await task();       // Step 2: wait for each to complete
    results.push(result);              // Step 3: collect result
  }
  
  return results;                      // Step 4: return all results in order
}

// ============================================
// SOLUTION 2: reduce (functional style)
// ============================================

function runSequentiallyReduce(tasks) {
  return tasks.reduce(
    (chain, task) => chain.then(results =>
      task().then(result => [...results, result])
    ),
    Promise.resolve([])  // start with resolved empty array
  );
}

// ============================================
// TEST CASES
// ============================================

// Mock async task:
const createTask = (id, delay) => () => new Promise(resolve => {
  setTimeout(() => {
    console.log(`Task ${id} done`);
    resolve(`result_${id}`);
  }, delay);
});

const tasks = [
  createTask(1, 300),  // 300ms
  createTask(2, 100),  // 100ms — starts AFTER task 1
  createTask(3, 200),  // 200ms — starts AFTER task 2
];

// Sequential:
console.time('sequential');
runSequentially(tasks).then(results => {
  console.timeEnd('sequential');  // ~600ms total (300+100+200)
  console.log(results);           // ['result_1', 'result_2', 'result_3']
});

// Contrast with parallel:
console.time('parallel');
Promise.all(tasks.map(t => t())).then(results => {
  console.timeEnd('parallel');  // ~300ms total (all run simultaneously)
  console.log(results);         // ['result_1', 'result_2', 'result_3']
});
```

---

## 🔍 Why This Works (3 lines max)
`await` inside `for...of` pauses the loop until each promise resolves. `forEach` does NOT work — it doesn't wait for async callbacks. `reduce` builds a promise chain where each `.then()` triggers the next task.
हिंदी: `for...of` + `await` loop को pause करता है; `forEach` async के साथ काम नहीं करता।

---

## ⚡ Alternative Solution
```javascript
// Sequential with error handling per task:
async function runSequentiallyWithErrors(tasks) {
  const results = [];
  
  for (const [index, task] of tasks.entries()) {
    try {
      const result = await task();
      results.push({ status: 'fulfilled', value: result });
    } catch (error) {
      results.push({ status: 'rejected', reason: error, index });
      // continue to next task instead of stopping
    }
  }
  
  return results;
}

// Using async generator (can yield results one by one):
async function* sequentialGenerator(tasks) {
  for (const task of tasks) {
    yield await task();  // yield each result as it completes
  }
}

// Consuming:
for await (const result of sequentialGenerator(tasks)) {
  console.log(result);  // logs each result as it arrives
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forEach doesn't await
async function wrong(tasks) {
  const results = [];
  tasks.forEach(async task => {
    const result = await task();  // these all fire simultaneously!
    results.push(result);
  });
  return results;  // returns BEFORE any task completes — empty array!
}

// ❌ Wrong: map doesn't make it sequential
const results = await Promise.all(tasks.map(async task => {
  return await task();  // all start at once — this is PARALLEL, not sequential
}));

// ✅ Correct: for...of awaits each
for (const task of tasks) {
  await task();  // each one waits for the previous
}
```

---

## 🎯 Interview Tip (1 line)
Say: "for...of + await = sequential; Promise.all(array.map) = parallel; forEach with async = bug (fire-and-forget, doesn't wait)."

---

## 🔗 Related Questions
→ Q202 (parallel promises) | Q203 (limit concurrent) | Q207 (chain async) | Q300 (Promise vs async/await)
