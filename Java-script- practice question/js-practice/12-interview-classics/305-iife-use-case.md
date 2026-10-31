---

# Q305. IIFE use case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is an IIFE (Immediately Invoked Function Expression) and when is it useful? Show 3 real uses: private state, avoiding global pollution / the old `var` loop fix, and an async IIFE.

---

## 💡 Quick Concept (2 lines only)
An IIFE is a function that is defined and called at once: `(function () { ... })();`. It creates a private scope that runs immediately.
हिंदी: IIFE ऐसा function है जो बनते ही तुरंत चल जाता है और अपनी private scope बनाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: wrap function in parentheses so it is an expression
// Step 2: add () at the end to call it immediately
// Step 3: variables inside stay private; only what you return is exposed

// Use 1: module pattern — private state + public API
const counter = (function () {
  let count = 0;                           // private, cannot be touched from outside
  return {
    inc() { return ++count; },             // public method that updates private state
    get() { return count; },               // public getter
  };
})();                                      // called immediately, result stored in counter

// Use 2: fix the classic var-in-loop problem (pre-ES6 way)
const fns = [];                            // will hold three functions
for (var i = 0; i < 3; i++) {
  (function (j) {                          // IIFE gets its own copy `j` per iteration
    fns.push(() => j);                     // closure captures j (0, 1, 2)
  })(i);                                   // pass current i in
}

// Use 3: async IIFE — use await at top level of a CommonJS script
(async () => {
  const data = await Promise.resolve('loaded'); // await allowed inside async IIFE
  console.log('3:', data);                 // Expected: 3: loaded
})();

// Use 0: no global pollution
(function () {
  var temp = 'secret';                     // stays inside the IIFE
})();

// ============================================
// TEST CASES
// ============================================

console.log(counter.inc());                // Expected: 1
console.log(counter.inc());                // Expected: 2
console.log(counter.get());                // Expected: 2
console.log(counter.count);                // Expected: undefined (private)
console.log(typeof temp);                  // Expected: undefined (no leak)
console.log(fns.map((f) => f()));          // Expected: [ 0, 1, 2 ]
// (async IIFE line "3: loaded" prints last, after all sync logs)
```

---

## 🔍 Why This Works (3 lines max)
Functions create scope, and an IIFE runs right away, so its variables never reach the outer scope. Closures let returned functions keep using those private variables.
हिंदी: Function अपनी scope बनाता है और IIFE तुरंत चलता है, इसलिए अंदर के variables बाहर leak नहीं होते।

---

## ⚡ Alternative Solution
```javascript
// Modern replacements: block scope and ES modules
{
  let temp = 'secret';          // block scope replaces IIFE for hiding variables
}
for (let k = 0; k < 3; k++) {   // let creates a fresh binding per iteration
  setTimeout(() => console.log('let loop', k), 0); // let loop 0, 1, 2
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: missing parentheses -> SyntaxError (function statement needs a name)
// function () { console.log('hi'); }();

// ❌ Wrong: no semicolon before an IIFE on the next line
// const a = 1
// (function () {})()   // parsed as 1(function(){})() -> TypeError

// ✅ Correct
(function () { console.log('hi'); })(); // hi
```

---

## 🎯 Interview Tip (1 line)
Say: "IIFE gives instant private scope — I use it for module-style encapsulation and async setup; with let/const and ES modules it's less needed today."

---

## 🔗 Related Questions
→ Q006 (closure loop var) | Q121 (fix closure loop) | Q269 (module pattern) | Q270 (revealing module)
