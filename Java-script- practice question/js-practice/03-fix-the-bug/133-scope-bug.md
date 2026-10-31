---

# Q133. Fix Scope Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`result` is used outside the `if` block, and a missing declaration leaks a global. Find and fix both bugs.

```javascript
// BUGGY CODE:
function compute(flag) {
  if (flag) {
    let result = 10;      // block-scoped
  }
  leaked = 5;             // no declaration -> accidental global
  return result;          // ReferenceError
}
```

---

## 💡 Quick Concept (2 lines only)
`let`/`const` live only inside their `{}` block. Declare variables in the scope where you need them and always use a keyword to avoid globals.
हिंदी: `let/const` अपने block तक सीमित हैं — जहाँ चाहिए वहाँ declare करो और बिना keyword global मत बनाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function compute(flag) {
  'use strict';              // Step 1: strict mode throws on undeclared variables
  let result = 0;            // Step 2 (FIX): declare in outer function scope
  if (flag) {
    result = 10;             // Step 3: assign inside block, no redeclaration
  }
  const extra = 5;           // Step 4 (FIX): declared with const, not global
  return result + extra;     // visible here
}

// ============================================
// TEST CASES
// ============================================

console.log(compute(true));         // Expected: 15
console.log(compute(false));        // Expected: 5
console.log(typeof leaked);         // Expected: undefined (no global leak)
```

---

## 🔍 Why This Works (3 lines max)
The outer `let` is visible to the inner block and to the return statement. Using `const` avoids creating a property on the global object.
हिंदी: बाहर declare किया variable block और return दोनों में दिखता है, और global leak नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Ternary removes the need for an outer variable
const compute2 = (flag) => (flag ? 10 : 0) + 5;
console.log(compute2(true)); // 15
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: relying on var leaking out of blocks
if (true) { var v = 1; }
console.log(v); // 1 (works by accident, hides bugs)
// ✅ Correct: let/const + declare in the right scope
```

---

## 🎯 Interview Tip (1 line)
Say: "I prefer const/let for block scope and 'use strict' or ESLint no-undef to catch accidental globals."

---

## 🔗 Related Questions
→ Q002 (let TDZ) | Q132 (hoisting bug) | Q291 (var vs let vs const) | Q304 (scope chain)
