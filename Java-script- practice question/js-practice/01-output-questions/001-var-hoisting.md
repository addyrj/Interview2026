---

# Q001. var Hoisting Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
console.log(a);
var a = 5;
console.log(a);
```

---

## 💡 Quick Concept (2 lines only)
`var` declarations are hoisted to the top of their scope — but only the declaration, NOT the assignment. Initialized to `undefined` until the assignment line runs.
हिंदी: `var` declaration ऊपर जाती है लेकिन value नहीं — इसलिए पहले `undefined` मिलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// What JavaScript actually sees (after hoisting):
var a;           // Step 1: declaration hoisted to top, value = undefined
console.log(a);  // Step 2: prints undefined (declaration exists, no value yet)
a = 5;           // Step 3: assignment stays in original position
console.log(a);  // Step 4: prints 5

// ============================================
// TEST CASES
// ============================================

console.log(a);  // Expected: undefined
var a = 5;
console.log(a);  // Expected: 5
```

---

## 🔍 Why This Works (3 lines max)
JavaScript's compiler scans code before running it. It hoists `var` declarations (not values) to the top of their function/global scope. So `a` exists but is `undefined` before the assignment.
हिंदी: Compiler पहले सब `var` declarations ऊपर ले जाता है — value `undefined` रहती है assignment तक।

---

## ⚡ Alternative Solution
```javascript
// Compare: var vs let hoisting behavior
console.log(x);  // undefined  ← var: hoisted, undefined
var x = 10;

// console.log(y);  // ReferenceError ← let: hoisted but TDZ (not accessible)
let y = 10;
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong assumption: "It will throw ReferenceError"
console.log(a);  // NOT an error — prints undefined
var a = 5;

// ✅ Correct: var never throws ReferenceError for undeclared-before-use
// (let and const DO throw — that's the TDZ)
```

---

## 🎯 Interview Tip (1 line)
Say: "var is hoisted and initialized to `undefined`; let/const are hoisted but in TDZ — accessing them throws ReferenceError."

---

## 🔗 Related Questions
→ Q002 (let hoisting + TDZ) | Q003 (const hoisting) | Q004 (function hoisting)
