---

# Q211. Waterfall Async Execution
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `waterfall(tasks, initial)`: run async functions in order, passing each function's result as the input to the next. Return the final value. If any task throws, stop immediately.

```javascript
await waterfall([double, addTen, toString], 5); // "20"
```

---

## 💡 Quick Concept (2 lines only)
Waterfall = pipe for async functions: output of step N is input of step N+1. Like `pipe`, but each step may return a promise.
हिंदी: Waterfall में हर function का output अगले function का input बनता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: start with the initial value
// Step 2: await each task with the previous result
// Step 3: return the last result (a throw stops the loop)

async function waterfall(tasks, initial) {
  let value = initial;                                // value flowing through the chain
  for (const task of tasks) {                         // strict order
    value = await task(value);                        // feed previous output as input
  }
  return value;                                       // final output
}

// ============================================
// TEST CASES
// ============================================

const sleep = ms => new Promise(r => setTimeout(r, ms)); // fake latency

const double = async n => { await sleep(10); return n * 2; };        // 5 -> 10
const addTen = async n => { await sleep(10); return n + 10; };       // 10 -> 20
const toStr = async n => `${n}`;                                      // 20 -> "20"

(async () => {
  console.log(await waterfall([double, addTen, toStr], 5));   // Expected: 20
  console.log(typeof await waterfall([double, addTen, toStr], 5)); // Expected: string

  console.log(await waterfall([], 'untouched'));              // Expected: untouched

  const log = [];                                             // track which steps ran
  try {
    await waterfall([
      async x => { log.push('s1'); return x; },               // runs
      async () => { throw new Error('step 2 failed'); },      // throws
      async x => { log.push('s3'); return x; }                // never runs
    ], 1);
  } catch (e) {
    console.log(e.message, log);                              // Expected: step 2 failed [ 's1' ]
  }
})();
```

---

## 🔍 Why This Works (3 lines max)
Each `await` resolves before the next call, so inputs are always concrete values. A thrown error exits the async function, so later steps never run.
हिंदी: Error आते ही function बाहर निकल जाता है, इसलिए आगे के steps नहीं चलते।

---

## ⚡ Alternative Solution (if exists)
```javascript
// One-liner with reduce
const waterfallReduce = (tasks, initial) =>
  tasks.reduce((p, task) => p.then(task), Promise.resolve(initial)); // chain .then(task)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not awaiting — the next task receives a Promise, not the value
let v = initial;
for (const t of tasks) v = t(v);

// ✅ Correct
for (const t of tasks) v = await t(v);
```

---

## 🎯 Interview Tip (1 line)
Relate it to `async.waterfall` in the async library, Express middleware, and Redux thunk-like pipelines.

---

## 🔗 Related Questions
→ Q086 (pipe) | Q207 (chain async) | Q209 (async reduce) | Q201 (sequential)
