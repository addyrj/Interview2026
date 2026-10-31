---

# Q094. Implement Promise.any
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `myAny(promises)` that resolves with the FIRST fulfilled promise. If ALL reject (or input is empty), reject with an `AggregateError` containing all reasons.

```javascript
myAny([Promise.reject(1), Promise.resolve(2)]); // resolves 2
```

---

## 💡 Quick Concept (2 lines only)
Opposite of `all`: ignore rejections until every promise has failed. The first success wins immediately.
हिंदी: any पहला सफल promise लौटाता है, सब fail हों तभी error देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep array of errors and a failure counter
// Step 2: first fulfilled => resolve outer promise
// Step 3: when all failed => reject with AggregateError

function myAny(promises) {
  return new Promise((resolve, reject) => {                 // outer promise
    const errors = [];                                      // collect reasons by index
    let failed = 0;                                         // rejected count
    if (promises.length === 0) {                            // empty input
      return reject(new AggregateError([], 'All promises were rejected'));
    }
    promises.forEach((p, i) => {                            // loop with index
      Promise.resolve(p).then(
        resolve,                                            // first success wins
        (err) => {
          errors[i] = err;                                  // store failure reason
          failed++;                                         // count failure
          if (failed === promises.length) {                 // everyone failed
            reject(new AggregateError(errors, 'All promises were rejected'));
          }
        }
      );
    });
  });
}

// ============================================
// TEST CASES
// ============================================

const wait = (ms, v, fail) => new Promise((res, rej) =>
  setTimeout(() => (fail ? rej(v) : res(v)), ms));          // timer helper

(async () => {
  console.log(await myAny([wait(10, 'e1', true), wait(40, 'ok')])); // Expected: ok

  try {
    await myAny([wait(10, 'e1', true), wait(20, 'e2', true)]);
  } catch (e) {
    console.log(e.constructor.name, e.errors);   // Expected: AggregateError [ 'e1', 'e2' ]
  }

  console.log(await myAny([5, Promise.reject('x')])); // Expected: 5
})();
```

---

## 🔍 Why This Works (3 lines max)
Rejections are only counted, never forwarded, until the count equals the total. Any fulfillment resolves immediately.
हिंदी: Rejections सिर्फ गिने जाते हैं, पहला success मिलते ही promise resolve हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Trick: invert promises and reuse Promise.all
const myAny2 = (promises) =>
  Promise.all(promises.map(p =>
    Promise.resolve(p).then(
      v => Promise.reject(v),     // success becomes rejection (stops Promise.all)
      e => e                      // failure becomes value
    )
  )).then(
    errs => { throw new AggregateError(errs, 'All promises were rejected'); }, // all failed
    first => first                // first "rejection" is actual success
  );

myAny2([Promise.reject('a'), Promise.resolve('b')]).then(console.log); // Expected: b
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rejecting on the first error — that is Promise.all/race behavior
// ❌ Wrong: rejecting with a plain Error and losing all reasons

// ✅ Correct: collect errors by index and throw AggregateError at the end
```

---

## 🎯 Interview Tip (1 line)
Compare all four: all (all succeed), allSettled (wait all), race (first settle), any (first success) — with AggregateError.

---

## 🔗 Related Questions
→ Q091 (all) | Q092 (race) | Q093 (allSettled) | Q212 (race with fallback)
