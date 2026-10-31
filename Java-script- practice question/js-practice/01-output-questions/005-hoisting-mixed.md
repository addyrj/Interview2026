---

# Q005. Hoisting Mixed Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log(a);
console.log(typeof foo);
console.log(typeof bar);
var a = 1;
function foo() {}
var foo = 5;
var bar = function () {};
console.log(foo);
try { console.log(c); } catch (e) { console.log(e.name); }
let c = 3;
```

---

## 💡 Quick Concept (2 lines only)
Function declarations hoist first, then `var` names (undefined, no override of existing function), and let/const sit in TDZ.
हिंदी: पहले function hoist होते हैं, फिर var (undefined), और let/const TDZ में रहते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: foo (function) hoisted with body; var foo does not reset it
// Step 2: a and bar are hoisted as undefined
// Step 3: foo = 5 runs later and overwrites the function

console.log(a);               // var hoisted -> undefined
console.log(typeof foo);      // function wins at hoisting time
console.log(typeof bar);      // var + expression -> undefined
var a = 1;                    // assigned now
function foo() {}             // hoisted declaration
var foo = 5;                  // runtime assignment overwrites foo
var bar = function () {};     // assigned now
console.log(foo);             // foo is now 5
try {
  console.log(c);             // let in TDZ
} catch (e) {
  console.log(e.name);        // error type
}
let c = 3;                    // initialized here

// ============================================
// TEST CASES
// ============================================

console.log(a);               // Expected: 1
console.log(typeof bar);      // Expected: function

// Overall output:
// undefined
// function
// undefined
// 5
// ReferenceError
// 1
// function
```

---

## 🔍 Why This Works (3 lines max)
Hoisting happens in the creation phase: functions first, then var as undefined. Assignments only take effect when execution reaches their line.
हिंदी: Hoisting creation phase में होती है, assignment तभी होता है जब execution उस line पर पहुँचे।

---

## ⚡ Alternative Solution
```javascript
// Same-name function declarations: the last one wins
console.log(dup());           // Expected: second
function dup() { return 'first'; }
function dup() { return 'second'; }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Assuming "var foo = 5" doesn't affect function foo
// ✅ The var line reassigns foo at runtime, replacing the function
var f = 1;
function f() {}
console.log(typeof f);        // Expected: number
```

---

## 🎯 Interview Tip (1 line)
Walk through two phases out loud: "creation phase (hoist) then execution phase (assign)."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q004 (function hoisting) | Q132 (hoisting bug) | Q303 (hoisting 5 scenarios)
