---

# Q085. Implement Compose
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `compose(...fns)` that combines functions RIGHT to LEFT.
`compose(f, g, h)(x)` equals `f(g(h(x)))`.

```javascript
const add1 = x => x + 1;
const double = x => x * 2;
compose(add1, double)(5); // add1(double(5)) = 11
```

---

## 💡 Quick Concept (2 lines only)
Compose chains functions so the output of one becomes input of the previous. Execution goes right to left, done with `reduceRight`.
हिंदी: Compose functions को दाएं से बाएं जोड़ता है — एक का output अगले का input बनता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: collect functions with rest params
// Step 2: return a function taking the initial value
// Step 3: reduceRight applies functions from last to first
// Step 4: return final result

function compose(...fns) {
  return function (initial) {                              // takes the starting value
    return fns.reduceRight(                                // go from right to left
      (acc, fn) => fn(acc),                                // feed previous result into fn
      initial                                              // starting accumulator
    );
  };
}

// ============================================
// TEST CASES
// ============================================

const add1 = x => x + 1;          // adds one
const double = x => x * 2;        // doubles
const square = x => x * x;        // squares

console.log(compose(add1, double)(5));          // Expected: 11  (double 5 = 10, add1 = 11)
console.log(compose(square, add1, double)(2));  // Expected: 25  (4 -> 5 -> 25)
console.log(compose()(7));                      // Expected: 7   (no fns => identity)
console.log(compose(s => s + '!', s => s.trim())('  hi ')); // Expected: hi!
```

---

## 🔍 Why This Works (3 lines max)
`reduceRight` starts from the last function and threads the value through each one. With no functions, the initial value is returned untouched.
हिंदी: reduceRight आखिरी function से शुरू करके value को आगे पास करता जाता है।

---

## ⚡ Alternative Solution
```javascript
// Compose as a one-liner with reduce
const compose2 = (...fns) => fns.reduce((f, g) => (...args) => f(g(...args)));

console.log(compose2(add1, double)(5)); // Expected: 11
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using reduce (left to right) — that is pipe, not compose
const wrong = (...fns) => x => fns.reduce((acc, fn) => fn(acc), x);
console.log(wrong(add1, double)(5)); // 12 (add1 first) — wrong order!

// ✅ Correct: reduceRight for compose
console.log(compose(add1, double)(5)); // 11
```

---

## 🎯 Interview Tip (1 line)
Clearly state "compose = right-to-left, pipe = left-to-right" and relate it to Redux middleware / functional programming.

---

## 🔗 Related Questions
→ Q086 (pipe) | Q084 (curry) | Q160 (complete pipe)
