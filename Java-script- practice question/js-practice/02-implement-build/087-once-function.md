---

# Q087. Implement Once Function
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `once(fn)` that returns a function which runs `fn` only the FIRST time. Later calls return the first result without calling `fn` again.

```javascript
const init = once(() => 'connected');
init(); // runs
init(); // returns cached result, doesn't run again
```

---

## 💡 Quick Concept (2 lines only)
Use a closure with a `called` flag and a stored `result`. Useful for initialization, DB connections, singletons.
हिंदी: Once function सिर्फ पहली बार चलता है, बाद में पुराना result ही लौटाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: closure variables to remember state
// Step 2: on first call run fn and store result
// Step 3: on later calls return stored result

function once(fn) {
  let called = false;                       // has fn already run?
  let result;                               // cached return value

  return function (...args) {               // wrapper
    if (!called) {                          // first time only
      called = true;                        // mark as done
      result = fn.apply(this, args);        // run original with this + args
    }
    return result;                          // always return first result
  };
}

// ============================================
// TEST CASES
// ============================================

let count = 0;                                      // counts real executions
const init = once((name) => { count++; return 'hello ' + name; });

console.log(init('A'));   // Expected: hello A
console.log(init('B'));   // Expected: hello A   (arg ignored, cached result)
console.log(count);       // Expected: 1
console.log(init());      // Expected: hello A
```

---

## 🔍 Why This Works (3 lines max)
The closure keeps `called` and `result` alive between calls. After the first run the flag blocks any further execution.
हिंदी: Closure में flag और result सुरक्षित रहते हैं, इसलिए function दोबारा नहीं चलता।

---

## ⚡ Alternative Solution
```javascript
// Replace fn with a no-op after first call (no flag needed)
function once2(fn) {
  let result;                                // cache
  return function (...args) {
    if (fn) {                                // fn still exists => first call
      result = fn.apply(this, args);         // execute
      fn = null;                             // drop reference (also frees memory)
    }
    return result;                           // return cached
  };
}

const f = once2(() => Math.random());
console.log(f() === f()); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returns undefined on later calls (result not cached)
function bad(fn) {
  let called = false;
  return (...args) => { if (!called) { called = true; return fn(...args); } };
}
console.log(bad(() => 5)()); // 5
// second call => undefined

// ✅ Correct: store result and return it every time (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Closure holds the state; real use cases are one-time init, payment button double-click guard, and singleton setup."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q081 (debounce) | Q261 (singleton pattern)
