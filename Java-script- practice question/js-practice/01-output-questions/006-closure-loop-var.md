---

# Q006. Closure in Loop (var) Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(function() {
    console.log(i);
  }, 1000);
}
```

---

## 💡 Quick Concept (2 lines only)
`var` has function scope — all 3 callbacks share the SAME `i`. By the time setTimeout fires (1000ms later), the loop is done and `i` is 3.
हिंदी: `var` function-scoped होती है — सब timeouts एक ही `i` share करते हैं जो loop बाद 3 हो जाती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

for (var i = 0; i < 3; i++) {
  setTimeout(function() {
    console.log(i);  // All three see i = 3 (loop finished before callbacks run)
  }, 1000);
}

// ============================================
// OUTPUT (after 1 second):
// ============================================

// Expected: 3
//           3
//           3
// NOT: 0, 1, 2

// WHY: var is function-scoped, so there's ONE i shared across all callbacks
// Loop runs: i=0,1,2,3 (exits at 3)
// All 3 timeouts fire after 1 sec → i is now 3 → all print 3
```

---

## 🔍 Why This Works (3 lines max)
`var` creates ONE `i` in the outer function scope — not one per iteration. The closures all close over the same `i` reference. The loop finishes before any setTimeout fires, so `i` is already 3.
हिंदी: `var` से एक ही `i` बनती है — loop finish होने पर 3 हो जाती है, सब setTimeout 3 print करते हैं।

---

## ⚡ Alternative Solution
```javascript
// FIX 1: Use let (block-scoped — new i per iteration)
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 1000);
}
// Output: 0, 1, 2 ✅ (each iteration has its own i)

// FIX 2: IIFE (create new scope per iteration)
for (var i = 0; i < 3; i++) {
  (function(j) {
    setTimeout(() => console.log(j), 1000);
  })(i);
}
// Output: 0, 1, 2 ✅ (IIFE captures current value of i as j)

// FIX 3: bind to capture current value
for (var i = 0; i < 3; i++) {
  setTimeout(console.log.bind(null, i), 1000);
}
// Output: 0, 1, 2 ✅
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking it prints 0, 1, 2
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 1000);
}
// Actual: 3, 3, 3

// ✅ Fix: use let instead of var
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 1000);
}
// Output: 0, 1, 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Classic closure trap — var shares one reference; fix with let (new binding per iteration), IIFE, or bind."

---

## 🔗 Related Questions
→ Q007 (closure in loop with let) | Q008 (setTimeout + closure) | Q161 (closure explained)
