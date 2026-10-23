---

# Q002. let Hoisting + TDZ Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print? (No try/catch — predict the behavior)

```javascript
console.log(a);
let a = 5;
console.log(a);
```

---

## 💡 Quick Concept (2 lines only)
`let` is hoisted but NOT initialized — it lives in the "Temporal Dead Zone" (TDZ) from the start of the block until the declaration line. Accessing it in TDZ throws `ReferenceError`.
हिंदी: `let` hoist होती है पर TDZ में रहती है — declaration से पहले access करने पर `ReferenceError` आता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// What actually happens:
// Step 1: 'a' is hoisted into TDZ (exists but NOT accessible)
// Step 2: console.log(a) — tries to access 'a' which is in TDZ
// Step 3: ❌ ReferenceError: Cannot access 'a' before initialization
// Step 4: Code stops — line 3 never runs

console.log(a);  // ❌ ReferenceError: Cannot access 'a' before initialization
let a = 5;
console.log(a);  // Never reached

// ============================================
// TEST CASES — Correct way to use let
// ============================================

let b = 10;
console.log(b);  // Expected: 10 ✅

// TDZ exists even in same block:
{
  // console.log(c);  // ❌ TDZ — ReferenceError
  let c = 20;
  console.log(c);    // Expected: 20 ✅
}
```

---

## 🔍 Why This Works (3 lines max)
`let` and `const` are hoisted to the top of their BLOCK scope (not function/global). Unlike `var`, they are NOT initialized — they're in TDZ. Any access before the declaration line = ReferenceError.
हिंदी: `let` block scope में hoist होती है पर initialized नहीं — TDZ में access = ReferenceError।

---

## ⚡ Alternative Solution
```javascript
// TDZ in a function:
function test() {
  console.log(x);  // ❌ ReferenceError — TDZ even inside function
  let x = 5;
}

// TDZ with typeof:
console.log(typeof x);  // ✅ "undefined" — typeof does NOT throw for TDZ!
let x = 5;
// EXCEPTION: typeof is the only operator that doesn't throw in TDZ
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: "let is same as var, just block-scoped, so it prints undefined"
console.log(a);  // NOT undefined — throws ReferenceError!
let a = 5;

// ✅ Correct: let is hoisted but in TDZ until declaration
// var → hoisted + initialized to undefined → no error
// let/const → hoisted + NOT initialized → TDZ → ReferenceError
```

---

## 🎯 Interview Tip (1 line)
Say: "let is hoisted but stays in TDZ — accessing it before initialization throws ReferenceError, NOT undefined like var."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q003 (const hoisting) | Q164 (hoisting explained)
