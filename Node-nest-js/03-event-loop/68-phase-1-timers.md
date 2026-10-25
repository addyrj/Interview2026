# 68. Phase 1 — Timers
# हिंदी में: Phase 1 — Timers Phase

---

## 🔵 Simple Definition (English)
The **Timers phase** is the FIRST phase of the Event Loop. It executes callbacks scheduled by `setTimeout()` and `setInterval()` whose timer threshold has expired. Important: the delay you pass (e.g. `100`ms) is a **minimum** wait time, not a guarantee — the callback runs only when the event loop reaches this phase AND the time has elapsed.

## 🔵 सरल परिभाषा (Hindi)
**Timers phase** Event Loop का पहला phase है। इसमें `setTimeout()` और `setInterval()` के वो callbacks run होते हैं जिनका time threshold खत्म हो गया है। ध्यान रहे: दिया गया delay (जैसे `100`ms) एक **minimum** wait time है, guarantee नहीं — callback तभी run होगा जब event loop इस phase पर पहुंचे AND time निकल गया हो।

---

## 🔴 Problem it Solves
```
NEED: Schedule code to run AFTER some delay, without blocking execution

WITHOUT TIMERS PHASE (if Node ran timers synchronously):
  setTimeout(fn, 1000) → would BLOCK the whole process for 1 second!
  No other code could run meanwhile.

WITH TIMERS PHASE:
  setTimeout(fn, 1000) → registers fn in a timer list, returns IMMEDIATELY
  Event loop keeps running other code, I/O, etc.
  Once 1000ms elapses AND event loop reaches Timers phase → fn executes
  → Non-blocking delayed execution
```

## 🔴 यह क्यों बना? (Hindi)
```
Delay के बाद code run करना चाहिए था, बिना block किए
setTimeout synchronous होता तो पूरा process रुक जाता
Timers phase से delay register होता है, event loop आगे चलता रहता है
Time पूरा होने पर + event loop इस phase पर आने पर callback चलता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → setTimeout(callback, delay) registers callback + expiry time (now + delay)
Step 2 → Node stores it in an internal timers data structure (min-heap style, sorted by expiry)
Step 3 → Event loop enters TIMERS phase on each iteration
Step 4 → Checks: is there a timer whose expiry time has passed?
Step 5 → If yes → runs that callback (and any others that have also expired)
Step 6 → If a timer hasn't expired yet → event loop moves to NEXT phase (Pending Callbacks)
Step 7 → Timer gets checked again on the NEXT event loop iteration
Step 8 → setInterval() re-registers itself after each run (repeats this cycle)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. setTimeout(callback, delay) → callback + expiry time register होता है
2. Node internal timer list में expiry time के हिसाब से sort करके रखता है
3. हर loop iteration में TIMERS phase check करता है
4. Expired timer मिले → callback run, नहीं तो आगे बढ़ो
5. setInterval() हर बार फिर से register होता है (repeat)
```

---

## 🟡 Real World Example
**Zomato order timeout:** When a customer places an order, Zomato starts a `setTimeout(() => cancelOrderIfUnconfirmed(orderId), 5 * 60 * 1000)` — if the restaurant doesn't confirm within 5 minutes, auto-cancel. This doesn't block anything — thousands of such timers can be "ticking" simultaneously while the event loop handles other requests. Each one fires in the Timers phase once its 5-minute threshold is reached AND the event loop gets there (if the loop is busy with other work, the callback might fire a few ms late — that's expected and fine for this use case).

## 🟡 Real Example Hindi mein
**Zomato order timeout:** Order place होने पर `setTimeout(() => cancelOrderIfUnconfirmed(orderId), 5*60*1000)` set होता है — 5 मिनट में restaurant confirm नहीं करता तो auto-cancel। ये block नहीं करता — हजारों ऐसे timers parallel में चल सकते हैं, event loop बाकी requests handle करता रहता है। हर timer अपने threshold पूरा होने पर Timers phase में fire होता है।

---

## 💻 Code Example — Basic

```javascript
// timers-basic.js
// Run: node timers-basic.js

console.log('1: sync start');

// Register two timers with different delays
setTimeout(() => {
  console.log('3: timer A (100ms)');
}, 100);

setTimeout(() => {
  console.log('4: timer B (200ms)');
}, 200);

console.log('2: sync end');

// OUTPUT:
// 1: sync start
// 2: sync end
// 3: timer A (100ms)
// 4: timer B (200ms)
// Explanation: sync code ALWAYS runs first (call stack empties).
// Then event loop enters Timers phase repeatedly, checking elapsed time.
// Timer A expires first (100ms < 200ms) so it runs before Timer B.
```

## 💻 Code Example — Advanced

```javascript
// timers-advanced.js — demonstrating minimum delay guarantee, not exact delay

console.log('START:', Date.now());

setTimeout(() => {
  console.log('Timer fired at:', Date.now(), '(expected ~100ms later)');
}, 100);

// Simulate blocking the event loop with heavy synchronous work
// This DELAYS the timer beyond its scheduled 100ms!
const blockUntil = Date.now() + 300;
while (Date.now() < blockUntil) {
  // busy loop — blocks the event loop for 300ms
}

console.log('Blocking work done at:', Date.now());

// OUTPUT (approx):
// START: 1700000000000
// Blocking work done at: 1700000000300   <- 300ms later (sync block)
// Timer fired at: 1700000000301          <- fires IMMEDIATELY after block ends
//                                            NOT at the 100ms mark!
// LESSON: setTimeout(fn, 100) guarantees "at least 100ms", never "exactly 100ms".
// If the event loop is blocked, timers queue up and fire late, as soon as
// the loop becomes free and reaches the Timers phase.

// Realistic use: order expiry timers with graceful handling of lateness
function scheduleOrderExpiry(orderId, delayMs) {
  const scheduledAt = Date.now();
  return setTimeout(() => {
    const actualDelay = Date.now() - scheduledAt;
    console.log(`Order ${orderId} expiry fired after ${actualDelay}ms (requested ${delayMs}ms)`);
    // Production tip: if actualDelay >> delayMs, log it — could indicate event loop lag
  }, delayMs);
}
scheduleOrderExpiry('ORD123', 50);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Common pattern: request timeout using setTimeout in the Timers phase
app.get('/slow-upstream', (req, res) => {
  let responded = false;

  // Timeout guard: if upstream call takes too long, respond with 504
  const timeoutId = setTimeout(() => {
    if (!responded) {
      responded = true;
      res.status(504).json({ error: 'Upstream timeout' });
    }
  }, 5000);  // 5 second timeout

  callSlowUpstreamService()
    .then((data) => {
      if (!responded) {
        responded = true;
        clearTimeout(timeoutId);  // cancel the timer, it's no longer needed
        res.json(data);
      }
    })
    .catch((err) => {
      if (!responded) {
        responded = true;
        clearTimeout(timeoutId);
        res.status(500).json({ error: err.message });
      }
    });
});

function callSlowUpstreamService() {
  return new Promise((resolve) => setTimeout(() => resolve({ ok: true }), 2000));
}

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `setTimeout(fn, 0)` to run before synchronous code
```javascript
// WRONG assumption
setTimeout(() => console.log('timer'), 0);
console.log('sync');
// Output: 'sync' THEN 'timer' — sync code always runs first, call stack must empty

// CORRECT understanding: 0ms is just the MINIMUM delay; the Timers
// phase only runs after current sync code finishes and microtasks drain
```

❌ **Mistake 2:** Not clearing timers, causing memory leaks or unwanted firings
```javascript
// WRONG: timer keeps a reference alive even if the operation it was guarding completed
function fetchWithTimeout() {
  setTimeout(() => console.log('timeout fired!'), 5000);
  return fetch('/api/data');  // if this resolves fast, timer still fires later — wasted work
}

// CORRECT: always save and clear the timer reference
function fetchWithTimeout() {
  const timer = setTimeout(() => console.log('timeout fired!'), 5000);
  return fetch('/api/data').finally(() => clearTimeout(timer));
}
```

---

## 🧠 Tricky Interview Question

```javascript
setTimeout(() => console.log('A'), 100);
setTimeout(() => console.log('B'), 100);
setTimeout(() => console.log('C'), 50);
console.log('D');
```

**Answer:** Output: `D`, `C`, `A`, `B`. Explanation: `D` runs first (sync code). Then the Timers phase checks the timer list sorted by expiry — `C` (50ms) expires first, so it runs. `A` and `B` both have 100ms delay and were registered in that order — when both expire, Node runs them in **registration order** (FIFO for timers with equal expiry), so `A` before `B`.

---

## ⚫ Interview Questions + Answers

**Q1: Is `setTimeout(fn, 1000)` guaranteed to run exactly after 1000ms?**
A1: No. It's a **minimum** delay. The actual firing time depends on: (1) whether the event loop is busy with synchronous code or blocked operations when the timer expires, (2) how many other timers/microtasks need to run first, (3) OS-level timer resolution (not perfectly precise). The callback runs "no earlier than" the specified delay, possibly later.

**Q2: What determines the order multiple `setTimeout` calls run in?**
A2: Primarily by expiry time (shorter delay runs first). If two timers have the SAME delay and were registered in the same tick, they run in the order they were registered (FIFO) — Node maintains them in a sorted internal list.

**Q3: What's the difference between `setTimeout` and `setInterval`?**
A3: `setTimeout(fn, delay)` runs `fn` ONCE after the delay. `setInterval(fn, delay)` runs `fn` REPEATEDLY every `delay` ms until `clearInterval()` is called. Internally, `setInterval` re-schedules itself in the Timers phase after each execution — if the previous execution takes longer than the interval, the next one is delayed (no overlapping runs by default).

**Q4: Why might a `setTimeout(fn, 0)` sometimes take longer than 1ms to actually fire?**
A4: Because even with `0` or very small delays, the callback can only run in the Timers phase, which only happens after: (a) current synchronous code finishes, (b) all pending microtasks (nextTick, Promises) drain, (c) the event loop actually cycles back to the Timers phase. If there's other work queued (I/O callbacks, other timers), the 0ms timer waits its turn.

**Q5: How do you cancel a scheduled timer, and why is it important to do so?**
A5: Use `clearTimeout(timerId)` or `clearInterval(timerId)`, where `timerId` is the value returned by `setTimeout`/`setInterval`. It's important because: (1) prevents unnecessary callback execution after the operation it was guarding is already done, (2) prevents memory leaks from closures held by the timer, (3) with `setInterval`, forgetting to clear it keeps the process alive forever (Node won't exit) unless you call `.unref()` on it.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Scheduling delayed/repeated tasks (order expiry, polling, retries with backoff)
- Implementing timeouts for async operations

❌ **Avoid when:**
- You need millisecond-precision timing (use a dedicated scheduler or external cron for that)
- Using it for CPU-bound busy-waiting (defeats the purpose of non-blocking I/O)

---

## 📊 Visual Diagram

```
TIMERS PHASE (Phase 1 of Event Loop):
──────────────────────────────────────────────────────

  Event Loop Iteration N:
  ┌─────────────────────────────────────────┐
  │  TIMERS PHASE                            │
  │  Check internal timer list (sorted)      │
  │                                           │
  │  Timer list:                             │
  │   [C: expires@50ms] [A: expires@100ms]   │
  │   [B: expires@100ms]                     │
  │                                           │
  │  If current time >= expiry → run it      │
  │  Run ALL expired timers before moving on │
  └──────────────────┬────────────────────────┘
                     │ not expired yet?
                     ▼
            Move to Phase 2: Pending Callbacks
                     │
                     ▼ (next loop iteration)
            Re-check Timers phase again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Timers Phase | Phase 1, runs expired setTimeout/setInterval | Expired timers run करने वाला phase |
| Minimum Delay | Delay is "at least", not "exactly" | कम से कम delay, exact नहीं |
| `clearTimeout()` | Cancels a scheduled timer | Scheduled timer cancel करता है |
| FIFO | First registered, first run (equal delay) | पहले register, पहले run |
| Timer List | Internal sorted structure of pending timers | Pending timers की internal list |

---

## ⚡ 3-Line Summary
English:
1. Timers phase is the first Event Loop phase — it runs `setTimeout`/`setInterval` callbacks whose delay has expired.
2. The delay is a MINIMUM wait, never a guarantee — a busy event loop delays timer firing.
3. Timers with equal expiry run in registration order (FIFO); always `clearTimeout`/`clearInterval` when no longer needed.

Hindi:
1. Timers phase Event Loop का पहला phase है — expired `setTimeout`/`setInterval` callbacks यहीं run होते हैं।
2. Delay minimum guarantee है, exact नहीं — busy event loop timer को late कर देता है।
3. बराबर expiry वाले timers FIFO order में run होते हैं; जरूरत ना हो तो `clearTimeout`/`clearInterval` जरूर करो।

---

## ➡️ Next Topic
**69. Phase 2 — Pending Callbacks** — How deferred I/O callbacks (like certain TCP errors) run in the next phase।
