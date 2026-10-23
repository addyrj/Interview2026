---

# Q091. Implement Promise.all
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement your own `myPromiseAll(promises)` that works exactly like `Promise.all`:
- Takes an array of promises
- Resolves when ALL promises resolve (preserving order)
- Rejects immediately if ANY promise rejects

```javascript
myPromiseAll([p1, p2, p3]).then(results => console.log(results));
// results = [result1, result2, result3] in order
```

---

## 💡 Quick Concept (2 lines only)
Promise.all runs promises in parallel and collects all results. If any rejects, the whole thing rejects immediately ("fail fast").
हिंदी: सब promises parallel run करता है — सब resolve हों तो सब results मिलते हैं; कोई एक fail → सब fail।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function myPromiseAll(promises) {
  return new Promise((resolve, reject) => {
    // Step 1: handle empty array
    if (promises.length === 0) {
      resolve([]);
      return;
    }
    
    const results = new Array(promises.length);  // Step 2: pre-allocate results array
    let resolvedCount = 0;                        // Step 3: track how many resolved
    
    promises.forEach((promise, index) => {
      // Step 4: wrap non-promises with Promise.resolve (handles plain values too)
      Promise.resolve(promise).then(value => {
        results[index] = value;          // Step 5: store result at correct INDEX
        resolvedCount++;
        
        if (resolvedCount === promises.length) {  // Step 6: all done?
          resolve(results);                        // Step 7: resolve with all results
        }
      }).catch(reject);  // Step 8: any rejection → reject immediately
    });
  });
}

// ============================================
// TEST CASES
// ============================================

const p1 = Promise.resolve(1);
const p2 = new Promise(resolve => setTimeout(() => resolve(2), 100));
const p3 = Promise.resolve(3);

myPromiseAll([p1, p2, p3]).then(results => {
  console.log(results);  // Expected: [1, 2, 3] — in order, even though p2 resolved last
});

// Rejection test:
const p4 = Promise.reject('Error!');
myPromiseAll([p1, p4, p3]).catch(err => {
  console.log(err);  // Expected: 'Error!'
});

// Empty array:
myPromiseAll([]).then(results => {
  console.log(results);  // Expected: []
});

// Non-promise values:
myPromiseAll([1, Promise.resolve(2), 3]).then(results => {
  console.log(results);  // Expected: [1, 2, 3]
});
```

---

## 🔍 Why This Works (3 lines max)
Pre-allocate results array to preserve ORDER — use `results[index]` not `results.push()`. Count resolved promises to know when all are done. Wrap each in `Promise.resolve()` to handle non-promise values.
हिंदी: Index से results store करो (order preserve करने के लिए); count track करो; एक reject → immediately reject।

---

## ⚡ Alternative Solution
```javascript
// Using reduce:
function myPromiseAll(promises) {
  return promises.reduce(
    (acc, promise) =>
      acc.then(results =>
        Promise.resolve(promise).then(result => [...results, result])
      ),
    Promise.resolve([])
  );
  // NOTE: this runs SEQUENTIALLY (not parallel) — interview trap!
}

// Implement Promise.allSettled (doesn't reject on failure):
function myPromiseAllSettled(promises) {
  return myPromiseAll(
    promises.map(p =>
      Promise.resolve(p)
        .then(value => ({ status: 'fulfilled', value }))
        .catch(reason => ({ status: 'rejected', reason }))
    )
  );
}

// Usage:
myPromiseAllSettled([
  Promise.resolve(1),
  Promise.reject('error'),
  Promise.resolve(3)
]).then(results => {
  console.log(results);
  // [
  //   { status: 'fulfilled', value: 1 },
  //   { status: 'rejected', reason: 'error' },
  //   { status: 'fulfilled', value: 3 }
  // ]
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using push() — loses order guarantee
results.push(value);  // order depends on resolution time!

// ✅ Correct: use index
results[index] = value;  // preserves original promise order

// ❌ Wrong: not handling non-promise values
promises.forEach((promise, i) => {
  promise.then(...)  // throws if promise is a plain value (1, 'string', etc.)
});

// ✅ Correct: wrap with Promise.resolve()
Promise.resolve(promise).then(...)  // works for both promises and values

// ❌ Wrong: checking results.length instead of resolvedCount
if (results.length === promises.length) // WRONG — push adds length immediately
// ✅ Use separate counter
```

---

## 🎯 Interview Tip (1 line)
Say: "Key insight — use index (not push) to preserve order; wrap all values with Promise.resolve() for safety; fail-fast on first rejection."

---

## 🔗 Related Questions
→ Q092 (Promise.race) | Q093 (Promise.allSettled) | Q094 (Promise.any) | Q201 (run promises sequentially) | Q202 (run in parallel)
