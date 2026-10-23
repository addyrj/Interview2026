---

# Q082. Implement Throttle
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `throttle(fn, limit)` function.
Throttle should ensure `fn` is called at most once per `limit` milliseconds, no matter how often it's invoked. First call executes immediately; subsequent calls during the limit window are ignored.

```javascript
const throttledScroll = throttle(handleScroll, 200);
window.addEventListener('scroll', throttledScroll);
// handleScroll runs at most once every 200ms
```

---

## 💡 Quick Concept (2 lines only)
Throttle limits execution frequency — "fire at most once per N ms." Used for scroll/resize handlers — "keep firing but at a controlled rate."
हिंदी: Throttle execution rate limit करता है — N ms में एक बार ही function run होगा, चाहे कितनी बार call हो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function throttle(fn, limit) {
  let lastRun = 0;  // Step 1: track when function last ran
  
  return function(...args) {
    const now = Date.now();                  // Step 2: get current time
    
    if (now - lastRun >= limit) {            // Step 3: enough time has passed?
      lastRun = now;                         // Step 4: update last run time
      return fn.apply(this, args);           // Step 5: run the function
    }
    // else: ignore this call — too soon
  };
}

// ============================================
// TEST CASES
// ============================================

const log = throttle((msg) => console.log(msg + ' at ' + Date.now()), 300);

log('A');  // Runs immediately (first call)
log('B');  // Ignored — 0ms since last run (< 300ms)
log('C');  // Ignored — still < 300ms

setTimeout(() => log('D'), 400);   // Runs — 400ms > 300ms limit
setTimeout(() => log('E'), 500);   // Ignored — 100ms since D (< 300ms)
setTimeout(() => log('F'), 900);   // Runs — 500ms since D (> 300ms)

// Expected output:
// A   (immediate)
// D   (400ms later)
// F   (900ms later)
```

---

## 🔍 Why This Works (3 lines max)
Track the last execution time. On each call, check if `now - lastRun >= limit`. If yes, run and update `lastRun`. If no, skip. Unlike debounce (waits for pause), throttle runs periodically regardless.
हिंदी: Last run time track करो — अगर N ms गुज़र गए तो run करो, नहीं तो skip।

---

## ⚡ Alternative Solution
```javascript
// Timer-based throttle (trailing edge — runs after delay):
function throttleTimer(fn, limit) {
  let inThrottle = false;
  
  return function(...args) {
    if (!inThrottle) {
      fn.apply(this, args);   // run immediately (leading edge)
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;   // allow next call after limit ms
      }, limit);
    }
  };
}

// Complete throttle with trailing call:
function throttleFull(fn, limit) {
  let lastRun = 0;
  let timerId;
  
  return function(...args) {
    const now = Date.now();
    const remaining = limit - (now - lastRun);
    
    if (remaining <= 0) {
      if (timerId) { clearTimeout(timerId); timerId = null; }
      lastRun = now;
      fn.apply(this, args);
    } else {
      clearTimeout(timerId);
      timerId = setTimeout(() => {   // trailing call
        lastRun = Date.now();
        timerId = null;
        fn.apply(this, args);
      }, remaining);
    }
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: confusing debounce with throttle
// Debounce: waits for activity to STOP, then fires ONCE
// Throttle: fires PERIODICALLY while activity continues

// ❌ Wrong: forgetting to pass 'this' context
return function(...args) {
  fn(...args);  // lost 'this'
};

// ✅ Correct:
return function(...args) {
  fn.apply(this, args);  // preserves 'this'
};
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce = wait for silence, fire once; Throttle = fire periodically — scroll/resize use throttle, search input uses debounce."

---

## 🔗 Related Questions
→ Q081 (debounce) | Q083 (memoize) | Q309 (throttle real use case)
