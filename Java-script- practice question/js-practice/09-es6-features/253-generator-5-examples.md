---

# Q253. Generator — 5 Examples
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show 5 generator examples: basic yield, infinite ID generator, `take` helper, delegation with `yield*`, and two-way communication via `next(value)`.

---

## 💡 Quick Concept (2 lines only)
A generator (`function*`) pauses at each `yield` and resumes on `next()`, producing values lazily.
हिंदी: Generator `yield` पर रुकता है और `next()` पर आगे चलता है, values एक-एक करके देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Basic yield and next()
// Step 2: Infinite sequence + take helper
// Step 3: yield* delegation and two-way next(value)

// Example 1: basic
function* basic() { yield 1; yield 2; return 3; } // yields then returns
const g = basic();                               // create iterator (nothing runs yet)
console.log(g.next(), g.next(), g.next(), g.next());
// Expected: { value: 1, done: false } { value: 2, done: false } { value: 3, done: true } { value: undefined, done: true }

// Example 2: infinite ID generator (lazy)
function* ids() { let i = 1; while (true) yield i++; } // never ends, but lazy
const gen = ids();                               // iterator
console.log(gen.next().value, gen.next().value); // Expected: 1 2

// Example 3: take(n) helper for infinite generators
function* take(it, n) {
  let c = 0;                                     // counter
  for (const v of it) { if (c++ >= n) return; yield v; } // stop after n
}
console.log([...take(ids(), 3)]);                // Expected: [ 1, 2, 3 ]

// Example 4: yield* delegates to another iterable
function* inner() { yield 'a'; yield 'b'; }      // inner generator
function* outer() { yield 0; yield* inner(); yield 'z'; } // delegate
console.log([...outer()]);                       // Expected: [ 0, 'a', 'b', 'z' ]

// Example 5: two-way communication
function* chat() {
  const name = yield 'Name?';                    // receives value from next(arg)
  const lang = yield `Hi ${name}, language?`;    // receives second value
  return `${name} likes ${lang}`;                // final result
}
const c = chat();                                // iterator
console.log(c.next().value);                     // Expected: Name?
console.log(c.next('Ria').value);                // Expected: Hi Ria, language?
console.log(c.next('JS').value);                 // Expected: Ria likes JS

// ============================================
// TEST CASES
// ============================================

console.log(typeof basic().next);                // Expected: function
console.log([...basic()]);                       // Expected: [ 1, 2 ]  (return value skipped)
const early = basic();                           // new iterator
early.next(); console.log(early.return(9));      // Expected: { value: 9, done: true }
```

---

## 🔍 Why This Works (3 lines max)
Calling a generator returns an iterator without running the body; each `next()` runs until the next `yield`. State (local variables) is kept between pauses.
हिंदी: Generator की state हर pause पर सुरक्षित रहती है, इसलिए infinite sequence भी बन जाती है।

---

## ⚡ Alternative Solution
```javascript
// Same infinite idea using a closure (no generator)
const makeIds = () => { let i = 0; return () => ++i; }; // closure counter
const next = makeIds();                          // factory
console.log(next(), next());                     // Expected: 1 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: spreading an infinite generator -> hangs / out of memory
// const all = [...ids()];

// ✅ Correct: limit it first
console.log([...take(ids(), 2)]);                // Expected: [ 1, 2 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators give lazy evaluation and are the foundation behind async/await and redux-saga."

---

## 🔗 Related Questions
→ Q044 (generator output) | Q149 (complete generator) | Q169 (explain generators) | Q254 (async generator)
