---

# Q168. Explain Promise Internals
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Explain how a Promise works internally. Build a minimal Promise (`MyPromise`) with states, `then` chaining and async callbacks.

---

## 💡 Quick Concept (2 lines only)
A Promise is a state machine (pending -> fulfilled | rejected) that stores a value and a list of callbacks. `then` registers callbacks and returns a new Promise; callbacks always run asynchronously.
हिंदी: Promise = state machine (pending से fulfilled/rejected) जो value और callbacks याद रखता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Keep state, value and handlers list
// Step 2: resolve/reject change state once and flush handlers
// Step 3: then returns a new promise, runs handlers in a microtask

class MyPromise {
  constructor(executor) {
    this.state = 'pending';                       // initial state
    this.value = undefined;                       // result or error
    this.handlers = [];                           // queued then-callbacks

    const settle = (state, value) => {            // shared settle logic
      if (this.state !== 'pending') return;       // settle only once
      this.state = state;                         // set final state
      this.value = value;                         // store result
      this.handlers.forEach(h => this._run(h));   // flush waiting handlers
    };
    const resolve = v => {                        // resolve function
      if (v && typeof v.then === 'function') {    // thenable -> follow it
        v.then(resolve, reject);                  // adopt its state
      } else settle('fulfilled', v);              // plain value
    };
    const reject = e => settle('rejected', e);    // reject function

    try { executor(resolve, reject); }            // run user code now
    catch (e) { reject(e); }                      // throw -> reject
  }

  _run(h) {                                       // execute one handler
    queueMicrotask(() => {                        // always async
      const cb = this.state === 'fulfilled' ? h.onOk : h.onErr; // pick callback
      if (!cb) {                                  // no handler -> pass through
        return this.state === 'fulfilled' ? h.resolve(this.value) : h.reject(this.value);
      }
      try { h.resolve(cb(this.value)); }          // result feeds next promise
      catch (e) { h.reject(e); }                  // error rejects next promise
    });
  }

  then(onOk, onErr) {
    return new MyPromise((resolve, reject) => {   // new promise for chaining
      const h = { onOk, onErr, resolve, reject }; // bundle handler
      if (this.state === 'pending') this.handlers.push(h); // wait
      else this._run(h);                          // already settled -> run
    });
  }

  catch(onErr) { return this.then(undefined, onErr); } // sugar for then
}

// ============================================
// TEST CASES
// ============================================

new MyPromise(res => setTimeout(() => res(1), 10))   // async resolve
  .then(v => v + 1)                                  // chain: 2
  .then(v => { console.log('A:', v); throw new Error('x'); }) // Expected: A: 2
  .catch(e => { console.log('B:', e.message); return 'ok'; }) // Expected: B: x
  .then(v => console.log('C:', v));                  // Expected: C: ok

new MyPromise(res => res('sync')).then(v => console.log('D:', v)); // Expected: D: sync
console.log('E: first');                             // Expected: E: first (then is async)
```

---

## 🔍 Why This Works (3 lines max)
State changes once and is immutable. `then` returns a new promise so chains form; handlers run via microtask so they never run synchronously. Returning a thenable makes the chain wait for it.
हिंदी: State एक बार ही बदलती है, then नया promise देता है, और callbacks हमेशा microtask में चलते हैं।

---

## ⚡ Alternative Solution
```javascript
// Promisify a callback API using the real Promise
const wait = ms => new Promise(res => setTimeout(res, ms)); // resolve after ms
wait(5).then(() => console.log('waited'));                  // Expected: waited
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Nesting promises (callback hell again)
// p.then(a => other(a).then(b => third(b)));

// ✅ Return the inner promise to flatten the chain
// p.then(a => other(a)).then(b => third(b));
```

---

## 🎯 Interview Tip (1 line)
Say: "Pending, fulfilled, rejected; settles once; then returns a new promise; handlers run as microtasks."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q091 (Promise.all) | Q123 (Promise chain bug) | Q145 (complete Promise chain)
