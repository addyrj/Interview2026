---

# Q132. Fix Hoisting Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`total` should be 30 but the code throws `TypeError: add is not a function`. Fix it.

```javascript
// BUGGY CODE:
const total = add(10, 20);   // called before definition

var add = function (a, b) {
  return a + b;
};
console.log(total);
```

---

## 💡 Quick Concept (2 lines only)
Function declarations are fully hoisted; `var` function expressions hoist only the name as `undefined`. Define before use, or use a declaration.
हिंदी: function declaration पूरा hoist होता है, पर `var` expression सिर्फ `undefined` के रूप में।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function add(a, b) {            // Step 1 (FIX): declaration is hoisted with its body
  return a + b;                 // Step 2: return sum
}

const total = add(10, 20);      // Step 3: safe to call even above the definition

// ============================================
// TEST CASES
// ============================================

console.log(total);             // Expected: 30
console.log(add(1, 2));         // Expected: 3
console.log(typeof add);        // Expected: function
```

---

## 🔍 Why This Works (3 lines max)
Declarations are moved to the top with their body during compilation, so calling early works. Expressions assigned to `var` are `undefined` until the assignment line runs.
हिंदी: declaration का पूरा body ऊपर चला जाता है, इसलिए पहले call करना भी चलता है।

---

## ⚡ Alternative Solution
```javascript
// Keep the expression, but define it BEFORE using it
const add2 = (a, b) => a + b;     // defined first
console.log(add2(10, 20));        // 30
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: const/let are hoisted but in the TDZ
try { console.log(x); } catch (e) { console.log(e.name); } // ReferenceError
let x = 5;
// ✅ Correct: declare first, use after
```

---

## 🎯 Interview Tip (1 line)
Say: "Declarations hoist with body, var hoists as undefined, let/const hoist into the temporal dead zone."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q002 (TDZ) | Q004 (function hoisting) | Q164 (hoisting explained)
