---

# Q291. var vs let vs const
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain the differences between `var`, `let`, and `const`. Show code examples demonstrating: hoisting, scope, re-declaration, re-assignment, and temporal dead zone.

---

## 💡 Quick Concept (2 lines only)
`var` = function-scoped, hoisted+initialized, re-declarable. `let` = block-scoped, TDZ, no re-declaration. `const` = block-scoped, TDZ, must initialize, no re-assignment.
हिंदी: `var` function scope + hoisted; `let`/`const` block scope + TDZ; `const` re-assign नहीं हो सकती।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — Full comparison
// ============================================

// 1. SCOPE
function scopeDemo() {
  if (true) {
    var x = 'var';    // function-scoped → visible outside the if block
    let y = 'let';    // block-scoped → only inside this if block
    const z = 'const'; // block-scoped → only inside this if block
  }
  console.log(x);  // 'var'          ← accessible outside block
  // console.log(y);  // ReferenceError ← block-scoped
  // console.log(z);  // ReferenceError ← block-scoped
}

// 2. HOISTING
console.log(a);  // undefined    ← var: hoisted + initialized as undefined
var a = 1;

// console.log(b);  // ReferenceError ← let: hoisted but TDZ
let b = 2;

// console.log(c);  // ReferenceError ← const: hoisted but TDZ
const c = 3;

// 3. RE-DECLARATION
var v = 1;
var v = 2;  // ✅ OK — var allows re-declaration

let l = 1;
// let l = 2;  // ❌ SyntaxError: Identifier 'l' already declared

const cn = 1;
// const cn = 2;  // ❌ SyntaxError

// 4. RE-ASSIGNMENT
var v2 = 1;
v2 = 2;  // ✅ OK

let l2 = 1;
l2 = 2;  // ✅ OK — let allows re-assignment

const cn2 = 1;
// cn2 = 2;  // ❌ TypeError: Assignment to constant variable

// 5. CONST DOESN'T MEAN IMMUTABLE (for objects/arrays)
const obj = { name: 'Arjun' };
obj.name = 'Priya';   // ✅ OK — modifying property (not re-assigning binding)
// obj = {};           // ❌ TypeError — re-assigning the binding

const arr = [1, 2, 3];
arr.push(4);           // ✅ OK — modifying array
// arr = [1, 2, 3, 4]; // ❌ TypeError

// ============================================
// COMPARISON TABLE (as code comments)
// ============================================

/*
Feature           var         let         const
─────────────────────────────────────────────────
Scope             function    block       block
Hoisted           yes (undef) yes (TDZ)  yes (TDZ)
Re-declare        yes         no          no
Re-assign         yes         yes         no
Initialize        optional    optional    required
Global property   yes         no          no
(in global scope)
*/
```

---

## 🔍 Why This Works (3 lines max)
`var` was original JS — function-scoped with hoisting quirks. `let`/`const` added in ES6 to fix var's confusing behavior. `const` binding is constant — the object/array it points to can still be mutated.
हिंदी: `var` ES6 से पहले था — confusing behavior था; `let`/`const` ES6 में आए block scope के साथ।

---

## ⚡ Alternative Solution
```javascript
// When to use which:

// const by DEFAULT — most variables don't change
const API_URL = 'https://api.example.com';
const user = { name: 'Arjun' };  // object is const, properties can change

// let when value changes (counters, accumulators, loop vars)
let count = 0;
for (let i = 0; i < 5; i++) { count += i; }

// var — almost never in modern JS
// Exception: extremely rare global variable needed for legacy code

// React example:
const [count, setCount] = useState(0);  // const — useState array is const
let isLoading = false;                  // let — might change
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;  // const — never changes
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking const makes objects immutable
const config = { debug: true };
config.debug = false;  // This WORKS — const only prevents re-binding
// config = { debug: false };  // This FAILS — re-binding fails

// ❌ Wrong: using var in loops with closures
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);  // 3, 3, 3 — not 0, 1, 2
}

// ✅ Correct: use let in loops
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);  // 0, 1, 2
}
```

---

## 🎯 Interview Tip (1 line)
Say: "Use const by default, let when reassignment needed, avoid var — const prevents rebinding but NOT object mutation."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q002 (let TDZ) | Q003 (const hoisting) | Q006 (closure loop var)
