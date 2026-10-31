---

# Q007. Closure in Loop (let) Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const fns = [];
for (let i = 0; i < 3; i++) {
  fns.push(() => i);
}
console.log(fns.map(f => f()));
```

---

## 💡 Quick Concept (2 lines only)
`let` creates a fresh binding of `i` for every loop iteration, so each closure captures its own value.
हिंदी: let हर iteration के लिए नया i बनाता है, इसलिए हर closure की अपनी अलग value होती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: each iteration gets its own block-scoped i
// Step 2: each arrow function closes over that iteration's i
// Step 3: calling them later returns 0, 1, 2

const fns = [];                    // holds the closures
for (let i = 0; i < 3; i++) {      // let -> new i per iteration
  fns.push(() => i);               // captures this iteration's i
}
console.log(fns.map(f => f()));    // call each closure

// ============================================
// TEST CASES
// ============================================

console.log(fns[0]());             // Expected: 0
console.log(fns[1]());             // Expected: 1
console.log(fns[2]());             // Expected: 2

// Overall output:
// [ 0, 1, 2 ]
// 0
// 1
// 2
```

---

## 🔍 Why This Works (3 lines max)
For `let` in a for loop, the engine copies the binding into a new scope on each iteration. Closures therefore keep different variables, not one shared one.
हिंदी: let loop में हर बार नया scope बनता है, इसलिए closure अलग-अलग i याद रखता है।

---

## ⚡ Alternative Solution
```javascript
// Same result with var + IIFE
const fns2 = [];                   // closures list
for (var j = 0; j < 3; j++) {      // shared var
  fns2.push(((k) => () => k)(j));  // IIFE copies j into k
}
console.log(fns2.map(f => f()));   // Expected: [ 0, 1, 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Using var: all closures share one i
const bad = [];
for (var i = 0; i < 3; i++) bad.push(() => i);
console.log(bad.map(f => f()));    // [ 3, 3, 3 ]
// ✅ Use let (or an IIFE) to get [ 0, 1, 2 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "let is block-scoped and per-iteration in for loops, so closures capture separate bindings."

---

## 🔗 Related Questions
→ Q006 (closure with var) | Q009 (setTimeout + var) | Q010 (setTimeout + let) | Q121 (fix closure bug)
