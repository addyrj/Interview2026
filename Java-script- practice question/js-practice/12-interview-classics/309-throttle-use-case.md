---

# Q309. throttle real use case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is throttling? Implement `throttle(fn, limit)` and show a real use case (scroll / resize / button spam). Explain how it differs from debounce.

---

## 💡 Quick Concept (2 lines only)
Throttle lets a function run at most once per time window, ignoring extra calls in between. Debounce waits for silence; throttle guarantees a steady rate.
हिंदी: Throttle function को एक time window में सिर्फ़ एक बार चलने देता है; बाकी calls ignore हो जाती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: remember the time of the last successful run
// Step 2: on each call, check if enough time has passed
// Step 3: if yes run fn and update the timestamp, otherwise ignore the call

function throttle(fn, limit) {
  let lastRun = 0;                              // timestamp of last execution (0 = never)
  return function (...args) {
    const now = Date.now();                     // current time in ms
    if (now - lastRun >= limit) {               // window has passed?
      lastRun = now;                            // start a new window
      return fn.apply(this, args);              // run the real function
    }
    // else: still inside the window -> ignore this call
  };
}

// Real use case: scroll handler that should run at most every 100ms
const onScroll = throttle((label) => console.log('handled', label), 100); // throttled handler

// ============================================
// TEST CASES
// ============================================

// Simulate rapid events on a timeline (ms): A@0, B@20, C@40, D@150, E@170
setTimeout(() => onScroll('A'), 0);             // runs  (first call)
setTimeout(() => onScroll('B'), 20);            // ignored (20ms < 100ms)
setTimeout(() => onScroll('C'), 40);            // ignored (40ms < 100ms)
setTimeout(() => onScroll('D'), 150);           // runs  (150ms >= 100ms since A)
setTimeout(() => onScroll('E'), 170);           // ignored (20ms since D)

// Expected output:
// handled A
// handled D
```

---

## 🔍 Why This Works (3 lines max)
`lastRun` lives in a closure and acts as a gate. Calls that arrive before `limit` ms have elapsed are dropped, so the handler runs at a controlled rate no matter how fast events fire.
हिंदी: `lastRun` closure में रहता है और gate की तरह काम करता है; जल्दी आने वाली calls drop हो जाती हैं।

---

## ⚡ Alternative Solution
```javascript
// Flag + setTimeout version (no Date.now needed)
function throttle2(fn, limit) {
  let waiting = false;                  // true while inside the cooldown window
  return (...args) => {
    if (waiting) return;                // ignore calls during cooldown
    fn(...args);                        // run immediately (leading edge)
    waiting = true;                     // start cooldown
    setTimeout(() => { waiting = false; }, limit); // end cooldown after limit ms
  };
}
// debounce vs throttle: typing search box -> debounce; scroll/resize/drag -> throttle
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: creating a new throttled function on every render/call
// window.addEventListener('scroll', () => throttle(handler, 100)()); // new closure each time, never throttles

// ✅ Correct: create the throttled function ONCE and reuse it
// const throttled = throttle(handler, 100);
// window.addEventListener('scroll', throttled);
```

---

## 🎯 Interview Tip (1 line)
Say: "Throttle = at most once per interval (scroll, resize, drag); debounce = once after activity stops (search input)."

---

## 🔗 Related Questions
→ Q082 (implement throttle) | Q142 (complete throttle) | Q308 (debounce use case) | Q286 (efficient event listeners)
