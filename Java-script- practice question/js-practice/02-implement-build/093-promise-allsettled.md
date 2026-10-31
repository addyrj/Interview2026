---

# Q093. Implement Promise.allSettled
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `myAllSettled(promises)` that waits for ALL promises to finish and never rejects. Each result is `{status:'fulfilled', value}` or `{status:'rejected', reason}`, in input order.

```javascript
myAllSettled([Promise.resolve(1), Promise.reject('x')]);
```

---

## 💡 Quick Concept (2 lines only)
Convert every promise into a "never failing" result object, then wait for all of them. Order is preserved by index.
हिंदी: allSettled सब promises का इंतज़ार करता है और हर एक का success/fail status देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle empty input
// Step 2: wrap each promise to record its outcome by index
// Step 3: when counter reaches total, resolve with results

function myAllSettled(promises) {
  return new Promise((resolve) => {                       // never rejects
    const results = [];                                   // outcomes by index
    let done = 0;                                         // finished count
    if (promises.length === 0) return resolve(results);   // empty => immediately []

    promises.forEach((p, i) => {                          // loop with index
      Promise.resolve(p).then(
        (value) => { results[i] = { status: 'fulfilled', value }; },   // success record
        (reason) => { results[i] = { status: 'rejected', reason }; }   // failure record
      ).finally(() => {
        done++;                                           // one more finished
        if (done === promises.length) resolve(results);   // all done => resolve
      });
    });
  });
}

// ============================================
// TEST CASES
// ============================================

const wait = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));

myAllSettled([wait(30, 'a'), Promise.reject('err'), 42]).then(r => console.log(JSON.stringify(r)));
// Expected: [{"status":"fulfilled","value":"a"},{"status":"rejected","reason":"err"},{"status":"fulfilled","value":42}]

myAllSettled([]).then(r => console.log(r));  // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Both success and failure handlers store a result, so nothing ever rejects. Writing to `results[i]` keeps the original order.
हिंदी: Success और fail दोनों को record किया जाता है, इसलिए यह कभी reject नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Using map + Promise.all with catch converted to a value
const myAllSettled2 = (promises) =>
  Promise.all(promises.map(p =>
    Promise.resolve(p).then(
      value => ({ status: 'fulfilled', value }),   // map success
      reason => ({ status: 'rejected', reason })   // map failure
    )
  ));

myAllSettled2([1, Promise.reject('no')]).then(r => console.log(r.length)); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: results.push() — order depends on finish time
// ❌ Wrong: using Promise.all directly — one rejection fails everything

// ✅ Correct: results[i] = ... and convert rejections into values
```

---

## 🎯 Interview Tip (1 line)
Say: "all rejects fast, allSettled always waits; use it when partial success is acceptable, like batch API calls."

---

## 🔗 Related Questions
→ Q091 (Promise.all) | Q094 (Promise.any) | Q208 (handle multiple async errors)
