---

# Q015. setImmediate Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
In Node.js, what is the order of `setTimeout(0)` and `setImmediate` when both are scheduled inside an I/O callback?

```javascript
const fs = require('fs');
fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
});
```

---

## 💡 Quick Concept (2 lines only)
`setImmediate` runs in the check phase right after the poll (I/O) phase, so inside an I/O callback it always beats `setTimeout(0)`.
हिंदी: I/O callback के अंदर setImmediate हमेशा setTimeout(0) से पहले चलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: readFile callback runs in the poll phase
// Step 2: next phase is "check" -> setImmediate callbacks run
// Step 3: loop wraps around to "timers" -> timeout runs

const fs = require('fs');                          // file system module
fs.readFile(__filename, () => {                    // I/O callback (poll phase)
  setTimeout(() => console.log('timeout'), 0);     // timers phase (next loop)
  setImmediate(() => console.log('immediate'));    // check phase (right after poll)
});

// ============================================
// TEST CASES
// ============================================

console.log('sync');                               // sync always first

// Output order:
// sync
// immediate
// timeout
```

---

## 🔍 Why This Works (3 lines max)
Event loop phases: timers -> poll -> check -> timers. From inside poll, check comes before the next timers phase. From the main module the order is non-deterministic.
हिंदी: Phases का order timers, poll, check है, इसलिए poll के बाद immediate पहले आता है।

---

## ⚡ Alternative Solution
```javascript
// Deterministic ordering with nextTick vs setImmediate
setImmediate(() => console.log('immediate'));      // check phase
process.nextTick(() => console.log('tick'));       // before any phase
// Expected: tick, immediate
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Assuming setTimeout(0) vs setImmediate order is fixed in the main module
// ✅ In main module it depends on process speed; only inside I/O callbacks it is guaranteed
```

---

## 🎯 Interview Tip (1 line)
Say: "setImmediate runs in the check phase; inside I/O it always precedes timers, in main it's non-deterministic."

---

## 🔗 Related Questions
→ Q013 (Promise + setTimeout) | Q014 (nextTick) | Q016 (microtask vs macrotask) | Q163 (explain event loop)
