---

# Q160. Complete Pipe Function
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks so `pipe(f, g, h)(x)` equals `h(g(f(x)))`.

```javascript
const pipe = (...fns) => (input) =>
  fns.____((acc, fn) => ____(acc), ____);   // run left to right
```

---

## 💡 Quick Concept (2 lines only)
`pipe` passes a value through functions from left to right; `reduce` carries the result along.
हिंदी: `pipe` value को functions से बाएँ से दाएँ गुज़ारता है और `reduce` result आगे ले जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const pipe = (...fns) => (input) =>              // Step 1: collect functions, take input later
  fns.reduce((acc, fn) => fn(acc), input);       // blanks: reduce, fn(acc), initial = input

const compose = (...fns) => (input) =>           // Step 2: compose is the right-to-left twin
  fns.reduceRight((acc, fn) => fn(acc), input);  // reduceRight reverses order

// ============================================
// TEST CASES
// ============================================

const add1 = (x) => x + 1;                       // helper
const double = (x) => x * 2;                     // helper
console.log(pipe(add1, double)(3));              // Expected: 8   ((3+1)*2)
console.log(compose(add1, double)(3));           // Expected: 7   ((3*2)+1)
console.log(pipe()(5));                          // Expected: 5   (no functions)
```

---

## 🔍 Why This Works (3 lines max)
Each reduce step feeds the previous output to the next function. With no functions, the initial input is returned unchanged.
हिंदी: हर step पिछला output अगले function को देता है, और functions न हों तो input वैसा ही लौटता है।

---

## ⚡ Alternative Solution
```javascript
// Async pipe: await each step
const pipeAsync = (...fns) => (x) => fns.reduce((p, f) => p.then(f), Promise.resolve(x));
pipeAsync(add1, double)(3).then(console.log); // 8
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: omitting the initial value -> first function receives (fn, fn) wrongly
// ✅ Correct: pass input as reduce's initial value
```

---

## 🎯 Interview Tip (1 line)
Say: "pipe is left-to-right, compose is right-to-left — both are reduce over functions."

---

## 🔗 Related Questions
→ Q085 (compose) | Q086 (pipe) | Q143 (complete curry) | Q306 (currying use case)
