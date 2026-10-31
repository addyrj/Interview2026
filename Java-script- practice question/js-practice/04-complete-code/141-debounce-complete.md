---

# Q141. Complete Debounce Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so the function runs only after the caller stops calling for `delay` ms.

```javascript
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    ____(timer);                          // cancel previous timer
    timer = ____(() => {                  // schedule new call
      fn.____(this, args);                // call with correct this + args
    }, ____);
  };
}
```

---

## 💡 Quick Concept (2 lines only)
Debounce resets a timer on every call, so only the last call in a burst executes.
हिंदी: Debounce हर call पर timer reset करता है, इसलिए burst की आखिरी call ही चलती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function debounce(fn, delay) {
  let timer;                              // Step 1: holds the pending timer id
  return function (...args) {             // Step 2: wrapper keeps this + args
    clearTimeout(timer);                  // blank 1: cancel previous timer
    timer = setTimeout(() => {            // blank 2: schedule new call
      fn.apply(this, args);               // blank 3: call with this + args
    }, delay);                            // blank 4: wait delay ms
  };
}

// ============================================
// TEST CASES
// ============================================

const log = debounce((x) => console.log('called with', x), 50); // debounced logger
log(1); log(2); log(3);                   // rapid calls, only last should run
// Expected (after 50ms): called with 3
```

---

## 🔍 Why This Works (3 lines max)
Each call clears the old timer and starts a fresh one; only when calls stop does the timer finish. The closure keeps `timer` between calls.
हिंदी: closure में `timer` बचा रहता है, और नई call पुराने timer को रद्द कर देती है।

---

## ⚡ Alternative Solution
```javascript
// Leading-edge debounce: run first call immediately
const debounceLead = (fn, d) => {
  let t;
  return (...a) => { if (!t) fn(...a); clearTimeout(t); t = setTimeout(() => (t = null), d); };
};
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: timer declared inside the returned function (reset every call, nothing cancelled)
// return function () { let timer; timer = setTimeout(...); }
// ✅ Correct: timer lives in the outer closure
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce = wait for silence (search box); throttle = limit rate (scroll) — and preserve this/args."

---

## 🔗 Related Questions
→ Q081 (implement debounce) | Q142 (complete throttle) | Q181 (search debounce) | Q308 (debounce use case)
