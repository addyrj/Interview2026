---

# Q004. Function Hoisting Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
console.log(greet());
function greet() { return 'Hello'; }

console.log(typeof expr);
try { expr(); } catch (e) { console.log(e.name); }
var expr = function () {};
```

---

## 💡 Quick Concept (2 lines only)
Function declarations are hoisted with their full body; function expressions assigned to `var` only hoist the variable (as undefined).
हिंदी: Function declaration पूरी body के साथ hoist होता है, पर function expression में सिर्फ var (undefined) hoist होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: greet (declaration) is fully hoisted, callable early
// Step 2: expr (var) is hoisted as undefined
// Step 3: calling undefined as a function -> TypeError

console.log(greet());                // declaration works before its line
function greet() { return 'Hello'; } // fully hoisted function

console.log(typeof expr);            // var hoisted as undefined
try {
  expr();                            // undefined is not a function
} catch (e) {
  console.log(e.name);               // prints the error type
}
var expr = function () {};           // assigned only at this line

// ============================================
// TEST CASES
// ============================================

console.log(typeof greet);           // Expected: function
console.log(typeof expr);            // Expected: function (assigned by now)

// Overall output:
// Hello
// undefined
// TypeError
// function
// function
```

---

## 🔍 Why This Works (3 lines max)
During the creation phase, declarations are stored in memory with their body, while `var` only gets undefined. The expression is assigned later at runtime.
हिंदी: Declaration पहले से memory में पूरा मिलता है, expression run होने पर ही assign होता है।

---

## ⚡ Alternative Solution
```javascript
// let/const function expressions throw ReferenceError (TDZ) instead
try {
  fn();                              // before initialization
} catch (e) {
  console.log(e.name);               // Expected: ReferenceError
}
const fn = () => 'x';                // arrow stored in const
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Calling a function expression before it is defined
// run(); var run = function () {};  // TypeError
// ✅ Define it first, or use a function declaration
function run() { return 1; }         // declaration is safe to call early
console.log(run());                  // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Declarations hoist with their body; expressions hoist only the variable, so behavior depends on var/let/const."

---

## 🔗 Related Questions
→ Q003 (const hoisting) | Q005 (hoisting mixed) | Q132 (hoisting bug) | Q164 (explain hoisting)
