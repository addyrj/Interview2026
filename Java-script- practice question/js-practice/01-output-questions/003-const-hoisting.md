---

# Q003. const Hoisting Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
try {
  console.log(PI);
} catch (e) {
  console.log(e.name);
}
const PI = 3.14;
console.log(PI);
```

---

## 💡 Quick Concept (2 lines only)
`const` is hoisted but stays in the Temporal Dead Zone until its declaration line runs, so early access throws ReferenceError.
हिंदी: const hoist होता है पर declaration से पहले TDZ में रहता है, इसलिए पहले access करने पर ReferenceError आता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: PI is hoisted but uninitialized (TDZ)
// Step 2: Accessing PI before declaration throws ReferenceError
// Step 3: After the declaration line, PI is usable

try {
  console.log(PI);          // TDZ access -> throws
} catch (e) {
  console.log(e.name);      // prints the error type
}
const PI = 3.14;            // initialization happens here
console.log(PI);            // now accessible

// ============================================
// TEST CASES
// ============================================

const obj = { a: 1 };       // const object
obj.a = 2;                  // mutation is allowed
console.log(obj.a);         // Expected: 2

try {
  PI = 3.15;                // reassigning const
} catch (e) {
  console.log(e.name);      // Expected: TypeError
}

// Overall output:
// ReferenceError
// 3.14
// 2
// TypeError
```

---

## 🔍 Why This Works (3 lines max)
const is hoisted to the top of its block but not initialized, so the TDZ applies. Once initialized it cannot be reassigned, though object contents can change.
हिंदी: const को दोबारा assign नहीं कर सकते (TypeError), पर object के अंदर की value बदल सकते हैं।

---

## ⚡ Alternative Solution
```javascript
// Freeze the object to make it truly immutable
const cfg = Object.freeze({ a: 1 }); // freeze shallowly
cfg.a = 99;                          // silently ignored (non-strict)
console.log(cfg.a);                  // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking const makes objects immutable
const user = { name: 'A' };
user.name = 'B';                     // allowed!
// ✅ const protects the binding, not the value. Use Object.freeze for immutability.
```

---

## 🎯 Interview Tip (1 line)
Say: "const is hoisted into the TDZ; it prevents reassignment, not mutation."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q002 (let + TDZ) | Q004 (function hoisting) | Q136 (object mutation bug)
