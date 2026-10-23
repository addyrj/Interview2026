---

# Q121. Fix Closure Bug in Loop
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
The following code is supposed to log 0, 1, 2 (one per second). But it logs 3, 3, 3. Find and fix the bug.

```javascript
// BUGGY CODE:
for (var i = 0; i < 3; i++) {
  setTimeout(function() {
    console.log(i);
  }, i * 1000);
}
```

---

## 💡 Quick Concept (2 lines only)
`var` is function-scoped — all iterations share the SAME `i`. By the time callbacks fire, loop is done and `i = 3`. Fix with `let` (block scope) or IIFE (create new scope).
हिंदी: `var` से सब callbacks एक ही `i` share करते हैं — loop खत्म होने पर `i = 3` होती है; `let` से fix करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// BUG IDENTIFIED:
// ============================================

// var i is FUNCTION-SCOPED (or global here)
// All 3 setTimeout callbacks close over the SAME i
// Loop runs: i=0, i=1, i=2, i=3 (exits when i=3)
// By the time timeouts fire, i is already 3

for (var i = 0; i < 3; i++) {
  setTimeout(function() {
    console.log(i);  // all print 3 — same i reference!
  }, i * 1000);
}
// Output: 3, 3, 3

// ============================================
// FIX 1: Use let (simplest — modern JS)
// ============================================

for (let i = 0; i < 3; i++) {  // let is BLOCK-scoped
  setTimeout(function() {
    console.log(i);  // each iteration has its own i
  }, i * 1000);
}
// Output: 0 (at 0ms), 1 (at 1000ms), 2 (at 2000ms) ✅

// ============================================
// FIX 2: IIFE (works in older JS too)
// ============================================

for (var i = 0; i < 3; i++) {
  (function(j) {      // IIFE creates new scope, captures current i as j
    setTimeout(function() {
      console.log(j); // j is independent per iteration
    }, j * 1000);
  })(i);              // immediately invoked with current value of i
}
// Output: 0, 1, 2 ✅

// ============================================
// FIX 3: bind to capture current value
// ============================================

for (var i = 0; i < 3; i++) {
  setTimeout(console.log.bind(null, i), i * 1000);
  // bind creates new function with i baked in
}
// Output: 0, 1, 2 ✅

// ============================================
// TEST CASES
// ============================================

// All three fixes produce:
// Expected after 0ms:    0
// Expected after 1000ms: 1
// Expected after 2000ms: 2
```

---

## 🔍 Why This Works (3 lines max)
`let` creates a new binding for EACH loop iteration — each callback closes over its own `i`. IIFE creates a new function scope per iteration, capturing `i`'s current value as parameter `j`. Both break the shared reference.
हिंदी: `let` हर iteration में नई binding बनाता है; IIFE हर iteration में new scope create करता है।

---

## ⚡ Alternative Solution
```javascript
// Fix 4: Array.from with index
Array.from({ length: 3 }, (_, i) => {
  setTimeout(() => console.log(i), i * 1000);
});

// Fix 5: Store value explicitly before timeout
for (var i = 0; i < 3; i++) {
  const j = i;  // const is block-scoped — captures current i
  setTimeout(() => console.log(j), j * 1000);
}
// Output: 0, 1, 2 ✅
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong fix attempt: putting var inside the loop body
for (var i = 0; i < 3; i++) {
  var j = i;  // var is STILL function-scoped — same problem!
  setTimeout(() => console.log(j), 1000);
}
// Output: 2, 2, 2 — j is still shared (last value assigned was 2)

// ✅ Use const or let inside loop body:
for (var i = 0; i < 3; i++) {
  const j = i;  // const/let is block-scoped — works!
  setTimeout(() => console.log(j), 1000);
}
// Output: 0, 1, 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Root cause: var shares one variable across all closures; fix: let (one var per iteration), IIFE (new scope), or const inside loop body."

---

## 🔗 Related Questions
→ Q006 (closure loop output) | Q007 (closure loop let) | Q161 (closure explained) | Q291 (var vs let vs const)
