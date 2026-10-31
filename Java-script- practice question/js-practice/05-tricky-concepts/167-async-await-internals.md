---

# Q167. Explain async/await Internals
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
How does `async/await` work under the hood? Show that an async function always returns a Promise, that `await` pauses only the function (not the thread), and how it maps to generators.

---

## 💡 Quick Concept (2 lines only)
`async` wraps the return value in a Promise; `await x` pauses the function, lets the stack unwind, and resumes in a microtask when `x` settles. It is sugar over Promises + generators.
हिंदी: async function हमेशा Promise देता है; await function को रोकता है, thread को नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: async function always returns a Promise
// Step 2: await pauses ONLY this function; the caller continues
// Step 3: Resume happens as a microtask after the awaited value settles

async function getValue() {                  // async -> returns Promise
  return 42;                                 // same as Promise.resolve(42)
}
console.log(getValue() instanceof Promise);  // Expected: true

async function demo() {
  console.log('A: before await');            // runs synchronously
  await null;                                // pause, yield control to caller
  console.log('C: after await');             // resumes in microtask
}
demo();                                      // start async function
console.log('B: caller continues');          // runs before C

// Manual version: async/await == generator + promise runner
function run(genFn) {                        // tiny co-like runner
  const gen = genFn();                       // create generator object
  return new Promise((resolve, reject) => {  // result promise
    function step(method, arg) {             // advance generator
      let r;                                 // holds iterator result
      try { r = gen[method](arg); }          // next(value) or throw(err)
      catch (e) { return reject(e); }        // generator threw -> reject
      if (r.done) return resolve(r.value);   // finished -> resolve
      Promise.resolve(r.value).then(         // "await" the yielded value
        v => step('next', v),                // resume with value
        e => step('throw', e)                // resume by throwing
      );
    }
    step('next');                            // kick off
  });
}

run(function* () {                           // yield == await
  const x = yield Promise.resolve(10);       // pause until promise resolves
  const y = yield 20;                        // non-promise works too
  return x + y;                              // final value
}).then(v => console.log('D:', v));          // Expected: D: 30

// Error handling: rejected await throws
(async () => {
  try { await Promise.reject(new Error('boom')); } // rejection becomes throw
  catch (e) { console.log('E:', e.message); }      // caught by try/catch
})();

// ============================================
// TEST CASES
// ============================================
// Expected output order:
// true
// A: before await
// B: caller continues
// C: after await
// E: boom
// D: 30
```

---

## 🔍 Why This Works (3 lines max)
Each `await` splits the function into pieces; the continuation is queued as a microtask when the promise settles. A rejected promise resumes the function by throwing, so `try/catch` works.
हिंदी: हर await के बाद का हिस्सा microtask में चलता है, और reject होने पर error throw होता है।

---

## ⚡ Alternative Solution
```javascript
// Same logic with .then chain
function getUser() {
  return Promise.resolve({ id: 1 })          // fake fetch
    .then(u => u.id + 1);                    // equals: const u = await ...; return u.id+1
}
getUser().then(console.log);                 // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Sequential awaits when tasks are independent (slow: ~200ms)
// const a = await wait(100); const b = await wait(100);

// ✅ Start together, await together (~100ms)
// const [a, b] = await Promise.all([wait(100), wait(100)]);
```

---

## 🎯 Interview Tip (1 line)
Say: "await is non-blocking: it suspends the async function and resumes via the microtask queue; it is generators plus promises."

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q122 (async error handling) | Q146 (complete async/await) | Q300 (Promise vs async/await)
