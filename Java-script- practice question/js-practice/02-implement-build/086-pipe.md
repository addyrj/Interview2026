---

# Q086. Implement Pipe
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `pipe(...fns)` that combines functions LEFT to RIGHT.
`pipe(f, g, h)(x)` equals `h(g(f(x)))`.

```javascript
pipe(double, add1)(5); // add1(double(5)) = 11
```

---

## 💡 Quick Concept (2 lines only)
Pipe passes the value through functions in the order they are written, like a pipeline. Implemented with `reduce`.
हिंदी: Pipe functions को बाएं से दाएं चलाता है — जैसे pipeline में data बहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: collect functions
// Step 2: return function accepting the initial value
// Step 3: reduce left to right, feeding each result forward
// Step 4: return final value

function pipe(...fns) {
  return function (initial) {                    // starting value
    return fns.reduce(                           // left to right
      (acc, fn) => fn(acc),                      // apply fn on accumulated value
      initial                                    // initial accumulator
    );
  };
}

// ============================================
// TEST CASES
// ============================================

const add1 = x => x + 1;       // +1
const double = x => x * 2;     // *2
const square = x => x * x;     // squared

console.log(pipe(double, add1)(5));          // Expected: 11  (10 then 11)
console.log(pipe(add1, double, square)(2));  // Expected: 36  (3 -> 6 -> 36)
console.log(pipe()(9));                      // Expected: 9
console.log(pipe(s => s.trim(), s => s.toUpperCase())('  hello ')); // Expected: HELLO
```

---

## 🔍 Why This Works (3 lines max)
`reduce` walks the functions in order, and the accumulator carries the latest result. Empty pipe just returns the input.
हिंदी: reduce functions को क्रम से चलाता है और accumulator में पिछला result रखता है।

---

## ⚡ Alternative Solution
```javascript
// Async-aware pipe: supports functions returning promises
const pipeAsync = (...fns) => (x) =>
  fns.reduce((p, fn) => p.then(fn), Promise.resolve(x)); // chain promises

pipeAsync(async x => x + 1, x => x * 3)(2).then(console.log); // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no initial value on reduce => first fn gets called with function args wrongly
const bad = (...fns) => x => fns.reduce((acc, fn) => fn(acc)); // acc starts as fns[0] itself!

// ✅ Correct: pass `x` as the initial accumulator
const good = (...fns) => x => fns.reduce((acc, fn) => fn(acc), x);
console.log(good(double, add1)(5)); // 11
```

---

## 🎯 Interview Tip (1 line)
Explain that pipe reads naturally top-to-bottom and is the left-to-right twin of compose; mention async pipe as a bonus.

---

## 🔗 Related Questions
→ Q085 (compose) | Q084 (curry) | Q160 (complete pipe function)
