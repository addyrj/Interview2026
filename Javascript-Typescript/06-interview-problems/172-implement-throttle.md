# 172. Implement throttle
# हिंदी में: Throttle लागू करना — एक तय अंतराल में function को सीमित बार चलाना

---

## 🔵 Simple Definition (English)
Throttle limits a function so that it runs at most once per time interval, no matter how many times it is called. The first call runs right away, and the extra calls are skipped or saved for one run at the end of the window.

## 🔵 सरल परिभाषा (Hindi)
Throttle किसी function को इस तरह सीमित करता है कि वह एक तय समय-अंतराल में ज़्यादा से ज़्यादा एक बार चले, चाहे उसे कितनी भी बार call किया जाए। पहली call तुरंत चलती है, और बाकी calls छोड़ दी जाती हैं या window के अंत में एक बार चलने के लिए रखी जाती हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `throttle(fn, wait)` that returns a wrapper. The wrapper calls `fn` at most once every `wait` milliseconds. Calls that arrive inside the window are not lost: the latest one runs at the end of the window (trailing call).

Scroll and mouse-move events can fire 60 or more times per second. A handler that recalculates layout or sends analytics on each event slows the page and floods the server. Debounce would wait for the scrolling to stop, which is too late for a "load more" trigger. Throttle runs the work regularly while the user keeps scrolling.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `throttle(fn, wait)` लिखो जो एक wrapper लौटाए। यह wrapper `fn` को हर `wait` ms में ज़्यादा से ज़्यादा एक बार चलाए। Window के अंदर आई calls खोनी नहीं चाहिए: आख़िरी call window के अंत में एक बार चले (trailing call)।

Scroll और mouse-move events एक सेकंड में 60 से ज़्यादा बार आ सकते हैं। हर event पर layout दोबारा गिनना या analytics भेजना page को धीमा करता है और server को भर देता है। Debounce scroll रुकने का इंतज़ार करता है, जो "load more" trigger के लिए बहुत देर है। Throttle scroll चलते रहने के दौरान भी नियमित रूप से काम करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Store the time of the last real run (start at 0, meaning never).
Step 2 → On each call, compute how many milliseconds are left before the next run is allowed.
Step 3 → If the time is up, run `fn` now and store the new time.
Step 4 → If not, keep the latest arguments and schedule one trailing run for the remaining time.
Step 5 → Later calls in the same window replace the saved arguments; they do not add more timers.
Step 6 → When the trailing run happens, it uses the latest arguments and sets the new time.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → आख़िरी असली run का समय सहेजो (शुरू में 0, यानी कभी नहीं चला)।
Step 2 → हर call पर देखो कि अगले run से पहले कितने ms बाकी हैं।
Step 3 → अगर समय पूरा हो गया, तो `fn` अभी चलाओ और नया समय सहेजो।
Step 4 → अगर नहीं, तो आख़िरी arguments रखो और बाकी समय के बाद एक trailing run तय करो।
Step 5 → उसी window की बाद की calls saved arguments को बदल देती हैं; वे और timers नहीं बनातीं।
Step 6 → Trailing run आख़िरी arguments के साथ चलता है और नया समय सहेजता है।

---

## 🟡 Real World Example
Google Maps updates the map position while you drag, but only a few times per second. Instagram's infinite feed checks "am I near the bottom?" on scroll, throttled to avoid many checks per second. Razorpay's live dashboard refreshes the transaction count at most once every 5 seconds, even when hundreds of payments arrive.

Scenario: A user drags a slider and 300 events arrive in one second. With `wait = 100`, the app updates the price about 10 times, and the last value is always applied at the end.

## 🟡 Real Example Hindi mein
Google Maps में map drag करते समय position हर सेकंड कुछ बार ही update होती है। Instagram का infinite feed scroll पर check करता है कि user नीचे के पास है या नहीं, पर throttle के साथ, ताकि हर सेकंड सैकड़ों checks न हों। Razorpay का live dashboard transaction count हर 5 सेकंड में ज़्यादा से ज़्यादा एक बार refresh होता है, भले ही सैकड़ों payments आ रहे हों।

उदाहरण: User एक slider खींचता है और एक सेकंड में 300 events आते हैं। `wait = 100` के साथ app price लगभग 10 बार update करता है, और आख़िरी value हमेशा अंत में लागू होती है।

---

## 💻 Code Example — Basic
```javascript
// Basic: throttle with a timestamp (leading call only, calls inside the window are dropped)
function throttle(fn, wait) {
  let last = 0;                              // time of the last real run (0 means it never ran)
  return function (...args) {                // the wrapper that callers use
    const now = Date.now();                  // current time in milliseconds
    if (now - last >= wait) {                // enough time has passed since the last run?
      last = now;                            // remember this run
      fn.apply(this, args);                  // run the original function
    }                                        // otherwise the call is simply dropped
  };
}

// Sample: a scroll handler that logs the position
const onScroll = throttle((y) => console.log("scroll at", y), 1000); // at most once per second
onScroll(10);                                // runs now
onScroll(20);                                // dropped: less than 1000 ms since the last run
onScroll(30);                                // dropped as well
// Expected output: scroll at 10

// Edge case: a function with no arguments still runs once per window
const ping = throttle(() => console.log("ping"), 1000); // no arguments needed
ping(); ping();                              // second call is dropped
// Expected output: ping
```
Expected output of the full block: `scroll at 10` then `ping`.

## 💻 Code Example — Advanced
```javascript
// Advanced: throttle with a trailing call, cancel(), and argument validation
function throttle(fn, wait) {
  // Guard: fn must be a function
  if (typeof fn !== "function") throw new TypeError("fn must be a function");

  let last = 0;                              // time of the last real run (0 = never)
  let timer = null;                          // pending trailing timeout, or null
  let lastArgs;                              // arguments of the most recent call
  let lastThis;                              // this of the most recent call

  function throttled(...args) {              // the wrapper
    lastArgs = args;                         // always keep the newest arguments
    lastThis = this;                         // and the newest this
    const now = Date.now();                  // current time
    const remaining = wait - (now - last);   // ms left before the next run is allowed

    if (remaining <= 0) {                    // the window is over: run now
      if (timer) {                           // a trailing run was scheduled earlier...
        clearTimeout(timer);                 // ...but this run replaces it
        timer = null;
      }
      last = now;                            // start a new window
      fn.apply(lastThis, lastArgs);          // run with the newest arguments
    } else if (!timer) {                     // inside the window and no trailing run yet
      timer = setTimeout(() => {             // schedule exactly one trailing run
        last = Date.now();                   // the trailing run starts a new window
        timer = null;                        // nothing is pending any more
        fn.apply(lastThis, lastArgs);        // run with the latest arguments
      }, remaining);
    }
  }

  throttled.cancel = () => {                 // drop a pending trailing run
    clearTimeout(timer);                     // stop the timer
    timer = null;                            // nothing pending
    last = 0;                                // the next call may run immediately
  };
  return throttled;                          // the wrapper with cancel
}

// Test 1: calls 2 and 3 are inside the window; only 3 (the latest) runs at the end
const track = throttle((n) => console.log("track", n), 100);
track(1);                                    // runs now
track(2);                                    // scheduled as a trailing run, replaced by the next call
track(3);                                    // the trailing run will use this value
// Expected output: track 1 (now), then track 3 (about 100 ms later)

// Test 2: a call after the window runs immediately
setTimeout(() => track(4), 250);             // well after the window ended
// Expected output: track 4 (about 250 ms)

// Time:  O(1) per call
// Space: O(1), only the last arguments, last run time and one timer id are stored
```

### Edge Cases
- Calls that arrive exactly at the end of the window run right away, because `remaining <= 0`.
- The trailing run never adds a second timer; it only replaces the saved arguments.
- With `wait = 0`, every call runs, so throttle has no effect.
- `cancel()` clears the trailing run, which matters on component unmount.
- Long pauses do not cause a burst later: the next call after a pause runs immediately, and only one trailing run follows.

---

## 🟠 Express.js Integration
On the server, the same idea is used as rate limiting: one request per interval from the same client. The middleware below throttles an OTP resend endpoint, so one phone number cannot receive SMS every second.

```javascript
// Express.js: throttle the OTP resend endpoint per client IP
const express = require("express");          // web framework
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies

const WINDOW_MS = 30 * 1000;                 // one OTP resend allowed every 30 seconds
const lastSent = new Map();                  // key -> time of the last allowed request (in memory for demo)

// Middleware: let a request through only if the window has passed
function throttleOtp(req, res, next) {
  const key = req.ip;                        // the client's IP address as the key
  const now = Date.now();                    // current time
  const last = lastSent.get(key) ?? 0;       // last allowed time, 0 if none
  if (now - last < WINDOW_MS) {              // still inside the window: reject
    const retryAfter = Math.ceil((WINDOW_MS - (now - last)) / 1000); // seconds to wait
    res.set("Retry-After", String(retryAfter)); // standard header for a 429 response
    return res.status(429).json({ error: "Too many requests", retryAfter }); // 429 Too Many Requests
  }
  lastSent.set(key, now);                    // record this allowed request
  next();                                    // pass the request on to the route
}

// POST /api/otp/resend  body: { "phone": "+919999999999" }
app.post("/api/otp/resend", throttleOtp, (req, res) => {
  const { phone } = req.body;                // the phone number to send to
  if (typeof phone !== "string") {           // validate the input
    return res.status(400).json({ error: "phone must be a string" }); // 400 Bad Request
  }
  res.json({ ok: true, message: "OTP sent" }); // 200 OK (SMS sending is out of scope here)
});

app.listen(process.env.PORT || 3000, () => {
  console.log("OTP API running");          // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Dropping the last call inside the window
✅ Correct: the last call carries the newest state, so it must run at the end of the window.

```javascript
// Wrong: only the first call in each window runs, so the final slider value is lost
let lastRun = 0;
const badThrottle = (fn, wait) => (v) => {
  if (Date.now() - lastRun >= wait) { lastRun = Date.now(); fn(v); }
};
const show = badThrottle((v) => console.log("price", v), 1000);
show(100); show(250); show(999);            // Expected output: price 100 (the final 999 is never shown)

// Right: a throttle with a trailing call (compact version, same rules as the advanced block above)
function throttle(fn, wait) {
  let last = 0, timer = null, args;          // last run time, pending timer, latest arguments
  return (...a) => {
    args = a;                                // keep the newest arguments
    const remaining = wait - (Date.now() - last); // ms left in the window
    if (remaining <= 0) { last = Date.now(); fn(...args); } // window is over: run now
    else if (!timer) timer = setTimeout(() => { timer = null; last = Date.now(); fn(...args); }, remaining);
  };
}
const showRight = throttle((v) => console.log("price", v), 1000);
showRight(100); showRight(250); showRight(999); // Expected output: price 100, then price 999 after about 1 s
```

❌ **Mistake 2:** Creating a new throttled function on every event
✅ Correct: the timestamp lives inside the closure, so a new wrapper starts with no memory and lets every call through.

```javascript
// Basic leading-only throttle, repeated so this block runs alone
function throttle(fn, wait) {
  let last = 0;
  return function (...args) {
    if (Date.now() - last >= wait) { last = Date.now(); fn.apply(this, args); }
  };
}

// Wrong: a new throttled function is created on each event, so nothing is throttled
let count = 0;
const handler = () => {
  const run = throttle(() => count++, 1000); // new closure, last = 0 each time
  run();                                     // always runs
};
handler(); handler(); handler();
console.log(count);                          // Expected output: 3

// Right: create the throttled function once, outside the handler
let count2 = 0;
const runOnce = throttle(() => count2++, 1000); // created once
const handler2 = () => runOnce();            // all events share one window
handler2(); handler2(); handler2();
console.log(count2);                         // Expected output: 1
```

---

## 🧠 Tricky Interview Question
```javascript
function throttle(fn, wait) {                // compact trailing throttle, so this block runs alone
  let last = 0, timer = null, args;
  return (...a) => {
    args = a;
    const remaining = wait - (Date.now() - last);
    if (remaining <= 0) { last = Date.now(); fn(...args); }
    else if (!timer) timer = setTimeout(() => { timer = null; last = Date.now(); fn(...args); }, remaining);
  };
}
const f = throttle((x) => console.log("f", x), 100);
f("a");                                      // at time 0
f("b");                                      // at time 0 as well
setTimeout(() => f("c"), 150);               // at time 150
setTimeout(() => f("d"), 160);               // at time 160
// What is printed, and when?
```
Answer:
```
f a   ← at 0 ms: the first call runs immediately
f b   ← at about 100 ms: the trailing call runs with the latest saved argument of that window
f d   ← at about 200 ms: the window that started at 100 ms still has 100 ms left when c (150 ms)
        arrives, so c is saved as the trailing argument; d (160 ms) replaces it, so c is never printed
```
The key point is that `c` is dropped, not run. The trailing run at 100 ms starts a new window that lasts until 200 ms, so both `c` and `d` wait for it, and only the latest one (`d`) is printed. Students often forget that a trailing run also starts a new window.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between throttle and debounce?**
A1: Throttle runs regularly, at most once per window, while calls keep coming. Debounce runs once, after calls stop. Use throttle for scroll and drag, and debounce for search and autosave.

**Q2: Why does the advanced version schedule only one trailing timer?**
A2: More than one timer would run the function several times. Keeping one timer and replacing the saved arguments means the final state is applied once.

**Q3: Why is `Date.now()` used instead of a counter?**
A3: The window is defined by time, not by the number of calls. `Date.now()` gives the time in ms, so the window works whatever the call rate is.

**Q4: Where is throttle used on the server?**
A4: As rate limiting. An Express middleware keeps the last allowed time per client and rejects calls inside the window with HTTP 429. Production systems often use a token bucket, but the idea is the same.

**Q5: What is the time complexity?**
A5: O(1) per call. Each call reads the clock, compares numbers, and maybe sets or clears one timer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Scroll, resize or mouse-move handlers do work on every event
- A UI should update regularly during a long gesture, such as a drag
- An API should be called at most once per interval, such as a status poll

❌ Avoid when:
- You want the function to run only after input stops; use debounce
- Every single event must be processed, such as a chat message or payment; throttling drops events
- The timing must be exact; throttle depends on the timer and the clock

---

## 📊 Visual Diagram
```
time ms:  0      100     200     300     400
calls:    a b          c d       e
window:   |----------| |---------|
run:      a          b(trail)  c  ...

- a runs now (window opens)
- b, the latest value in window 1, runs at 100 ms (trailing)
- c arrives after the window ends, so it runs right away
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Throttle | Limit runs to once per interval | एक interval में ज़्यादा से ज़्यादा एक बार चलाना |
| Window | The time span during which runs are limited | वह समय-अवधि जिसमें runs सीमित हैं |
| Trailing run | The run at the end of a window with the latest arguments | Window के अंत में आख़िरी arguments के साथ run |
| Rate limiting | Restricting how often a client can call an API | Client कितनी बार API बुला सके, यह सीमित करना |
| Timestamp | A saved time value used to compare with now | तुलना के लिए सहेजा गया समय |
| 429 status | HTTP code for "too many requests" | "बहुत ज़्यादा requests" का HTTP code |

---

## ⚡ 3-Line Summary
English:
1. Throttle runs a function at most once per window, so high-frequency events do not overload the page or server.
2. Keep the last run time and, when a call is inside the window, save its arguments for one trailing run.
3. Create the throttled function once; a new one on each event has no memory and throttles nothing.

Hindi:
1. Throttle एक window में function को ज़्यादा से ज़्यादा एक बार चलाता है, ताकि बहुत तेज़ events page या server को न भरें।
2. आख़िरी run का समय रखो, और window के अंदर की call के arguments एक trailing run के लिए सहेजो।
3. Throttled function एक बार बनाओ; हर event पर नया बनाने से उसकी याददाश्त नहीं रहती और कुछ throttle नहीं होता।

---

## ➡️ Next Topic
**173. Implement memoization** — throttle limits how often work runs; the next problem avoids repeating the same work by caching results for the same inputs.
