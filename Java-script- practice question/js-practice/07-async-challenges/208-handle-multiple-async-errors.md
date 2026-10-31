---

# Q208. Handle Multiple Async Errors
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Run several async tasks in parallel where some may fail. Return `{ results, errors }` so successful values are kept and every error is reported — without one failure aborting the rest.

```javascript
collect([ok1, fail1, ok2, fail2]).then(console.log);
// { results: [...], errors: [...] }
```

---

## 💡 Quick Concept (2 lines only)
`Promise.all` stops at the first rejection. `Promise.allSettled` waits for everything and reports each status, so you can split successes and failures.
हिंदी: `Promise.all` पहली error पर रुक जाता है, `allSettled` सबका status देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: start all tasks with allSettled (never rejects)
// Step 2: split outcomes into results and errors
// Step 3: keep the original index so you know WHICH task failed

async function collect(tasks) {
  const settled = await Promise.allSettled(tasks.map(t => t())); // wait for every task
  const results = [];                                 // successful values
  const errors = [];                                  // failures with index
  settled.forEach((s, index) => {                     // inspect each outcome
    if (s.status === 'fulfilled') results.push(s.value);            // success
    else errors.push({ index, message: s.reason.message });         // failure
  });
  return { results, errors };                         // both reported together
}

// ============================================
// TEST CASES
// ============================================

const ok = (v, ms) => () => new Promise(r => setTimeout(() => r(v), ms));          // succeeds
const fail = (msg, ms) => () => new Promise((_, rej) => setTimeout(() => rej(new Error(msg)), ms)); // fails

(async () => {
  const out = await collect([ok('A', 30), fail('E1', 10), ok('B', 20), fail('E2', 40)]);
  console.log(out);
  // Expected: {
  //   results: [ 'A', 'B' ],
  //   errors: [ { index: 1, message: 'E1' }, { index: 3, message: 'E2' } ]
  // }

  // Promise.all contrast: only the FIRST error is seen
  try {
    await Promise.all([ok('A', 30)(), fail('E1', 10)(), fail('E2', 40)()]);
  } catch (e) {
    console.log('all():', e.message);                 // Expected: all(): E1
  }

  // Promise.any: all failed -> AggregateError holds every reason
  try {
    await Promise.any([fail('X', 10)(), fail('Y', 20)()]);
  } catch (e) {
    console.log(e.constructor.name, e.errors.map(x => x.message)); // Expected: AggregateError [ 'X', 'Y' ]
  }
})();
```

---

## 🔍 Why This Works (3 lines max)
`allSettled` always fulfils with `{status, value|reason}` objects, so nothing is lost. We then partition them, keeping the index to map errors back to tasks.
हिंदी: `allSettled` कभी reject नहीं होता, इसलिए सारे success और error एक साथ मिल जाते हैं।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Catch inside each task so Promise.all never rejects
const safe = task => task().then(value => ({ ok: true, value }), error => ({ ok: false, error }));
const all = await Promise.all(tasks.map(safe)); // every entry says ok:true/false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: one try/catch around Promise.all hides the other errors
try { await Promise.all(tasks.map(t => t())); } catch (e) { /* only first error */ }

// ✅ Correct: allSettled and inspect every status
const settled = await Promise.allSettled(tasks.map(t => t()));
```

---

## 🎯 Interview Tip (1 line)
Know all four: all (fail-fast), allSettled (never rejects), race (first settle), any (first success, AggregateError).

---

## 🔗 Related Questions
→ Q202 (parallel) | Q093 (implement allSettled) | Q094 (implement any) | Q122 (fix async error handling)
