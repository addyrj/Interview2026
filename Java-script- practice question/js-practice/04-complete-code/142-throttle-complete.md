---

# Q142. Complete Throttle Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so `fn` runs at most once per `limit` ms.

```javascript
function throttle(fn, limit) {
  let last = 0;
  return function (...args) {
    const now = ____.now();               // current time
    if (now - last ____ limit) {          // enough time passed?
      last = ____;                        // remember this run
      return fn.apply(____, args);        // run original
    }
  };
}
```

---

## 💡 Quick Concept (2 lines only)
Throttle allows a call only if enough time has passed since the last executed one; extra calls are ignored.
हिंदी: Throttle एक निश्चित समय में सिर्फ एक बार function चलने देता है, बाकी calls ignore होती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function throttle(fn, limit) {
  let last = 0;                           // Step 1: time of last execution
  return function (...args) {
    const now = Date.now();               // blank 1: current time
    if (now - last >= limit) {            // blank 2: window elapsed
      last = now;                         // blank 3: record run time
      return fn.apply(this, args);        // blank 4: run with this
    }
  };
}

// ============================================
// TEST CASES
// ============================================

const t = throttle((x) => console.log('run', x), 100); // throttled logger
t(1);                                     // runs immediately
t(2);                                     // ignored (within 100ms)
setTimeout(() => t(3), 150);              // runs after window
// Expected: run 1
// Expected: run 3
```

---

## 🔍 Why This Works (3 lines max)
`last` remembers the previous run in the closure. Calls inside the window fail the time check and do nothing.
हिंदी: `last` closure में पिछला run time रखता है, और window के अंदर की calls skip हो जाती हैं।

---

## ⚡ Alternative Solution
```javascript
// Flag + timer version
const throttle2 = (fn, ms) => {
  let wait = false;
  return (...a) => { if (wait) return; fn(...a); wait = true; setTimeout(() => (wait = false), ms); };
};
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using > 0 or forgetting to update last (runs every time)
// if (now - last >= limit) { fn(); }   // last never updated
// ✅ Correct: last = now before calling fn
```

---

## 🎯 Interview Tip (1 line)
Say: "Throttle for scroll/resize/mousemove; debounce for search input — and mention leading vs trailing."

---

## 🔗 Related Questions
→ Q082 (implement throttle) | Q141 (complete debounce) | Q309 (throttle use case)
