---

# Q209. Async Reduce
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `asyncReduce(array, asyncFn, initial)` — like `Array.reduce`, but the reducer is async. Each step must wait for the previous accumulator.

```javascript
await asyncReduce([1, 2, 3], async (acc, n) => acc + n, 0); // 6
```

---

## 💡 Quick Concept (2 lines only)
`reduce` with an async callback gives promises as accumulator, so you must `await` the accumulator each step. A `for...of` loop is the cleanest way.
हिंदी: Async reduce में हर step पिछले accumulator का इंतज़ार करता है, इसलिए `for...of` + `await` सबसे आसान है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: start with the initial accumulator
// Step 2: for each item, await the async reducer
// Step 3: return the final accumulator

async function asyncReduce(array, fn, initial) {
  let acc = initial;                                  // running accumulator
  for (let i = 0; i < array.length; i++) {            // go in order
    acc = await fn(acc, array[i], i, array);          // wait before moving on
  }
  return acc;                                         // final value
}

// ============================================
// TEST CASES
// ============================================

const sleep = ms => new Promise(r => setTimeout(r, ms)); // fake latency

(async () => {
  // Test 1: simple sum with async work
  const sum = await asyncReduce([1, 2, 3, 4], async (acc, n) => {
    await sleep(10);                                  // pretend to call an API
    return acc + n;                                   // new accumulator
  }, 0);
  console.log(sum);                                   // Expected: 10

  // Test 2: build object, order matters
  const order = [];                                   // track call order
  const obj = await asyncReduce(['a', 'b', 'c'], async (acc, key, i) => {
    await sleep(30 - i * 10);                       // later items are FASTER
    order.push(key);                                  // still processed in order
    return { ...acc, [key]: i };
  }, {});
  console.log(obj, order);                            // Expected: { a: 0, b: 1, c: 2 } [ 'a', 'b', 'c' ]

  // Test 3: empty array returns initial
  console.log(await asyncReduce([], async (a, x) => a + x, 'init')); // Expected: init
})();
```

---

## 🔍 Why This Works (3 lines max)
Each loop iteration awaits the reducer before touching the next element, so the accumulator is always a real value, never a promise. Order is guaranteed even when later items are faster.
हिंदी: हर iteration पर `await` होने से accumulator हमेशा असली value रहता है और क्रम बना रहता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Using native reduce: accumulator is a promise chain
const asyncReduceNative = (arr, fn, initial) =>
  arr.reduce(
    (accPromise, item, i) => accPromise.then(acc => fn(acc, item, i)), // chain each step
    Promise.resolve(initial)                          // start with resolved initial
  );
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: acc is a Promise in the 2nd iteration -> "[object Promise]1"
arr.reduce(async (acc, n) => acc + n, 0);

// ✅ Correct: await the accumulator, or use the loop version
arr.reduce(async (accP, n) => (await accP) + n, Promise.resolve(0));
```

---

## 🎯 Interview Tip (1 line)
Point out that async reduce is inherently sequential — if steps are independent, use Promise.all then a normal reduce.

---

## 🔗 Related Questions
→ Q201 (sequential) | Q211 (waterfall) | Q114 (implement reduce) | Q210 (async map with limit)
