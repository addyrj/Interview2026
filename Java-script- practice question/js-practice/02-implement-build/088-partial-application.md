---

# Q088. Implement Partial Application
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `partial(fn, ...presetArgs)` that returns a new function with some arguments pre-filled. The remaining arguments are supplied later.

```javascript
const greet = (greeting, name) => `${greeting}, ${name}`;
const hello = partial(greet, 'Hello');
hello('Adi'); // "Hello, Adi"
```

---

## 💡 Quick Concept (2 lines only)
Partial application fixes a few arguments now and takes the rest later. Different from curry: partial can fix any number at once.
हिंदी: Partial कुछ arguments पहले fix कर देता है, बाकी बाद में देते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: capture fn and the preset args
// Step 2: return a new function taking the later args
// Step 3: call fn with preset + later args combined

function partial(fn, ...presetArgs) {
  return function (...laterArgs) {                    // args supplied at call time
    return fn.apply(this, [...presetArgs, ...laterArgs]); // merge both lists and call
  };
}

// ============================================
// TEST CASES
// ============================================

const greet = (greeting, name, punct) => `${greeting}, ${name}${punct}`; // 3-arg fn

const hello = partial(greet, 'Hello');          // fixes first arg
console.log(hello('Adi', '!'));                 // Expected: Hello, Adi!

const helloAdi = partial(greet, 'Hi', 'Adi');   // fixes two args
console.log(helloAdi('?'));                     // Expected: Hi, Adi?

const add = (a, b, c) => a + b + c;
console.log(partial(add, 1, 2)(3));             // Expected: 6
```

---

## 🔍 Why This Works (3 lines max)
The closure remembers `presetArgs`. When the new function is called, both argument lists are joined in order.
हिंदी: Closure पहले वाले arguments याद रखता है और बाद वालों के साथ जोड़कर call करता है।

---

## ⚡ Alternative Solution
```javascript
// Using built-in bind (this = null)
const hello2 = greet.bind(null, 'Hello');
console.log(hello2('Adi', '.')); // Expected: Hello, Adi.

// Placeholder support: use `_` to skip positions
const _ = Symbol('placeholder');                       // unique marker
function partialP(fn, ...preset) {
  return (...later) => {
    const args = preset.map(a => (a === _ ? later.shift() : a)); // fill holes
    return fn(...args, ...later);                      // remaining go at the end
  };
}
console.log(partialP(greet, _, 'Adi', _)('Yo', '!')); // Expected: Yo, Adi!
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: confusing partial with curry — curry returns one-arg functions step by step
// curry(add)(1)(2)(3)  vs  partial(add, 1)(2, 3)

// ❌ Wrong: forgetting to spread — passes arrays as single args
const bad = (fn, ...p) => (...l) => fn([...p, ...l]); // fn receives ONE array

// ✅ Correct: fn(...p, ...l)
```

---

## 🎯 Interview Tip (1 line)
Clarify "partial fixes some args in one go; curry transforms into unary chain" and mention `Function.prototype.bind` does partial.

---

## 🔗 Related Questions
→ Q084 (curry) | Q109 (implement bind) | Q085 (compose)
