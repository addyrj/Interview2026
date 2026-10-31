---

# Q009. setTimeout + var Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), i * 10);
}
```

---

## 💡 Quick Concept (2 lines only)
`var` is function-scoped, so all callbacks share one `i`, which is already 3 when the timers fire.
हिंदी: var function-scoped है, सारे callbacks एक ही i share करते हैं जो timers चलने तक 3 हो चुका होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: loop finishes synchronously, i becomes 3
// Step 2: three timers (0ms, 10ms, 20ms) were scheduled
// Step 3: each reads the shared i -> 3

for (var i = 0; i < 3; i++) {                 // single shared i
  setTimeout(() => console.log(i), i * 10);   // delay uses i at schedule time
}

// ============================================
// TEST CASES
// ============================================

console.log(i);                               // Expected: 3 (var leaks out of loop)

// Overall output:
// 3
// 3
// 3
// 3
```
(The first 3 comes from the test line, since it is synchronous; the last three come from the timers.)

---

## 🔍 Why This Works (3 lines max)
The loop ends before any timer fires, leaving the shared `i` at 3. All closures read that same variable.
हिंदी: Loop पहले खत्म हो जाता है, फिर timers चलते हैं और सब उसी एक i (=3) को पढ़ते हैं।

---

## ⚡ Alternative Solution
```javascript
// Fix 1: let
for (let k = 0; k < 3; k++) setTimeout(() => console.log('let', k), 50 + k); // 0 1 2
// Fix 2: pass argument to setTimeout
for (var j = 0; j < 3; j++) setTimeout((x) => console.log('arg', x), 100 + j, j); // 0 1 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Expecting 0 1 2 because delays are i * 10
// ✅ Delay uses i at schedule time, but the callback reads i at run time (3)
```

---

## 🎯 Interview Tip (1 line)
Say: "var shares one binding; fix with let, an IIFE, or setTimeout's extra argument."

---

## 🔗 Related Questions
→ Q006 (closure loop var) | Q007 (closure loop let) | Q010 (setTimeout + let) | Q121 (fix closure bug)
