---

# Q043. Default Parameter Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
function f(a, b = a * 2, c = []) {
  c.push(a);
  return [a, b, c];
}
console.log(f(1));
console.log(f(1, null));
console.log(f(1, undefined, [0]));
console.log(f(2));
```

---

## 💡 Quick Concept (2 lines only)
Defaults apply only for `undefined`, are evaluated at call time (left to right), and can use earlier parameters. Each call gets a fresh default.
हिंदी: Default सिर्फ undefined पर लगता है, हर call पर नया बनता है और पिछले parameters इस्तेमाल कर सकता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: f(1) -> b = 1*2 = 2, c = new [] -> [1]
// Step 2: f(1, null) -> null is NOT undefined, b stays null
// Step 3: f(1, undefined, [0]) -> b default 2, c is the passed array
// Step 4: f(2) -> c is a fresh [] again (not shared)

function f(a, b = a * 2, c = []) { // defaults evaluated per call
  c.push(a);                       // mutate c
  return [a, b, c];                // return all
}
console.log(f(1));                 // [ 1, 2, [ 1 ] ]
console.log(f(1, null));           // [ 1, null, [ 1 ] ]
console.log(f(1, undefined, [0])); // [ 1, 2, [ 0, 1 ] ]
console.log(f(2));                 // [ 2, 4, [ 2 ] ]

// ============================================
// TEST CASES
// ============================================

console.log(f.length);             // Expected: 1 (counts params before first default)
try {
  (function (x = y, y = 1) {})();  // y used before init
} catch (e) {
  console.log(e.name);             // Expected: ReferenceError
}
console.log((function (x = 5) { return x; })(undefined)); // Expected: 5

// ============================================
// OUTPUT:
// ============================================
// [ 1, 2, [ 1 ] ]
// [ 1, null, [ 1 ] ]
// [ 1, 2, [ 0, 1 ] ]
// [ 2, 4, [ 2 ] ]
// 1
// ReferenceError
// 5
```

---

## 🔍 Why This Works (3 lines max)
Default expressions run at call time, not definition time, so `[]` is new each call (unlike Python). They sit in a TDZ-like scope, so a default cannot use a later parameter.
हिंदी: Default call के समय evaluate होता है, इसलिए हर बार नया [] मिलता है और बाद वाला parameter पहले use नहीं हो सकता।

---

## ⚡ Alternative Solution
```javascript
// Pre-ES6 manual default
function g(a, b) {
  b = b === undefined ? a * 2 : b; // emulate default only for undefined
  return [a, b];
}
console.log(g(3)); // [ 3, 6 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting null to trigger the default
function greet(name = 'Guest') { return name; }
console.log(greet(null));      // null

// ✅ Correct: handle null with ??
const greet2 = (name) => name ?? 'Guest';
console.log(greet2(null));     // Guest
```

---

## 🎯 Interview Tip (1 line)
Say: "Defaults trigger only on undefined, run per call, and can reference earlier parameters."

---

## 🔗 Related Questions
→ Q042 (destructuring) | Q038 (nullish coalescing) | Q002 (TDZ)
