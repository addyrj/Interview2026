---

# Q145. Complete Promise Chain
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks so the chain doubles a number, adds 1, then logs; and errors are handled.

```javascript
Promise.____(5)                           // start with value 5
  .____(n => n * 2)                       // double it
  .then(n => ____ n + 1)                  // add 1 (pass it on)
  .then(n => console.log(n))              // log result
  .____(err => console.log('error'))      // handle errors
  .____(() => console.log('done'));       // always runs
```

---

## 💡 Quick Concept (2 lines only)
Each `.then` returns a new promise; its return value feeds the next. `catch` handles errors and `finally` always runs.
हिंदी: हर `.then` का return अगले step को जाता है; `catch` error पकड़ता है और `finally` हमेशा चलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

Promise.resolve(5)                        // blank 1: promise already resolved with 5
  .then(n => n * 2)                       // blank 2: 5 -> 10
  .then(n => { return n + 1; })           // blank 3: return passes 11 on
  .then(n => console.log(n))              // log the value
  .catch(err => console.log('error'))     // blank 4: handle any failure above
  .finally(() => console.log('done'));    // blank 5: cleanup

// ============================================
// TEST CASES
// ============================================

Promise.resolve(1)
  .then(() => { throw new Error('boom'); }) // force an error
  .catch(e => console.log(e.message))       // Expected: boom
  .finally(() => console.log('cleanup'));   // Expected: cleanup

// Expected order of output:
// boom
// 11
// cleanup
// done
// (interleaved by microtask timing; each line appears once)
```

---

## 🔍 Why This Works (3 lines max)
Returned values are wrapped in a new resolved promise, forming a chain. A thrown error skips to the nearest `catch`.
हिंदी: return value अगले `.then` को मिलती है और throw होने पर सीधे `catch` चलता है।

---

## ⚡ Alternative Solution
```javascript
// async/await version
(async () => {
  try { console.log((await Promise.resolve(5)) * 2 + 1); } // 11
  catch (e) { console.log('error'); } finally { console.log('done'); }
})();
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgot to return, next then gets undefined
Promise.resolve(1).then(x => { x + 1; }).then(console.log); // undefined
// ✅ Correct: return x + 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Always return inside then, put one catch at the end, and use finally for cleanup."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q123 (Promise chain bug) | Q207 (chain async operations) | Q300 (Promise vs async/await)
