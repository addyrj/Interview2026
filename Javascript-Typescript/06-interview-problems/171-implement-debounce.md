# 171. Implement debounce
# हिंदी में: Debounce लागू करना — Typing के बाद एक ही बार function चलाना

---

## 🔵 Simple Definition (English)
Debounce delays a function until the calls stop coming for a set time. Each new call resets the timer, so the function runs only once, after the quiet period. It is used for search-as-you-type, autosave, and window resize.

## 🔵 सरल परिभाषा (Hindi)
Debounce किसी function को तब तक रोकता है जब तक calls आना एक तय समय के लिए बंद न हो जाएँ। हर नई call timer को फिर से शुरू करती है, इसलिए function सिर्फ़ एक बार, शांति के बाद चलता है। इसका इस्तेमाल search-as-you-type, autosave और window resize में होता है।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `debounce(fn, wait)` that returns a new function. When the returned function is called many times in quick succession, `fn` runs only once, `wait` milliseconds after the last call. Its arguments come from that last call.

Without debounce, a search box that calls the API on every key press sends 6 requests for the word "pizza". Each request costs money and load, and the results come back out of order. A payment page that saves on every keystroke floods the server.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `debounce(fn, wait)` लिखो जो एक नया function लौटाए। जब यह function तेज़ी से कई बार बुलाया जाए, तो `fn` सिर्फ़ एक बार चले, आख़िरी call के `wait` ms बाद। Arguments आख़िरी call वाले हों।

Debounce के बिना, search box हर key press पर API बुलाता है, तो "pizza" लिखने में 6 requests जाती हैं। हर request का खर्च और load होता है, और results गलत क्रम में वापस आ सकते हैं। Save on every keystroke वाला page server को भर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The returned wrapper receives arguments from each call.
Step 2 → Cancel the timer that was set by the previous call (if any).
Step 3 → Start a new timer for `wait` milliseconds, with the latest arguments.
Step 4 → If no new call comes before the timer ends, `fn` runs.
Step 5 → If another call comes first, go back to step 2. The timer restarts.
Step 6 → Keep `this` so methods still work when called on an object.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Wrapper को हर call के arguments मिलते हैं।
Step 2 → पिछली call का timer (अगर है) रद्द करो।
Step 3 → नया timer `wait` ms का शुरू करो, आख़िरी arguments के साथ।
Step 4 → अगर timer खत्म होने से पहले कोई नई call नहीं आती, तो `fn` चलता है।
Step 5 → अगर उससे पहले नई call आ जाए, तो step 2 पर लौटो। Timer फिर से शुरू होता है।
Step 6 → `this` को सहेजो, ताकि object के method भी सही चलें।

---

## 🟡 Real World Example
Flipkart's search bar waits about 300 ms after the user stops typing before it calls the suggestions API. Swiggy's address form autosaves the draft only after the user pauses. Google Docs saves your edits after you stop typing for a short time, instead of after every letter.

Scenario: A user types "pizza" in 600 ms. Keystrokes come at p, pi, piz, pizz, pizza. With a 300 ms debounce, only one API call for "pizza" is sent.

## 🟡 Real Example Hindi mein
Flipkart का search bar user के type करना बंद करने के लगभग 300 ms बाद suggestions API बुलाता है। Swiggy का address form user के रुकने पर ही draft autosave करता है। Google Docs हर अक्षर पर save नहीं करता, बल्कि थोड़ी देर type बंद होने पर save करता है।

उदाहरण: User 600 ms में "pizza" लिखता है। Keystrokes p, pi, piz, pizz, pizza आते हैं। 300 ms debounce के साथ सिर्फ़ "pizza" के लिए एक API call जाती है।

---

## 💻 Code Example — Basic
```javascript
// Basic: debounce with setTimeout and clearTimeout
function debounce(fn, wait) {
  let timer = null;                          // id of the pending timeout (null when nothing is pending)
  return function (...args) {                // the wrapper that callers use
    clearTimeout(timer);                     // cancel the previous pending call, if any
    timer = setTimeout(() => fn.apply(this, args), wait); // schedule a new call with the latest args
  };
}

// Sample: a search box that logs the query
const search = debounce((text) => console.log("search:", text), 100); // wait 100 ms of quiet
search("p");                                 // replaced by the next call
search("pi");                                // replaced by the next call
search("pizza");                             // the last call: this one runs
// Expected output (after 100 ms): search: pizza

// Edge case: a single call still runs once, after the wait (the basic version has no cancel)
const once = debounce((v) => console.log("once:", v), 10); // a debounced function
once("only call");                           // one call, no others come, so it runs after 10 ms
// Expected output (after 10 ms): once: only call
```

## 💻 Code Example — Advanced
```javascript
// Advanced: debounce with a leading option, cancel(), and argument validation
function debounce(fn, wait, { leading = false } = {}) {
  // Guard: fn must be a function
  if (typeof fn !== "function") throw new TypeError("fn must be a function");

  let timer = null;                          // pending timeout id, null when no burst is active
  let count = 0;                             // how many calls happened in the current burst
  let lastArgs;                              // arguments of the latest call
  let lastThis;                              // this of the latest call

  function debounced(...args) {              // the wrapper
    lastArgs = args;                         // remember the latest arguments
    lastThis = this;                         // remember the latest this
    count++;                                 // one more call in this burst
    if (leading && count === 1) {            // leading edge: run immediately on the first call
      fn.apply(lastThis, lastArgs);
    }
    clearTimeout(timer);                     // restart the quiet period
    timer = setTimeout(() => {               // runs only after `wait` ms without a new call
      // Trailing edge: run if we are not leading-only, or if more calls came after the first one
      if (!leading || count > 1) fn.apply(lastThis, lastArgs);
      timer = null;                          // the burst is over
      count = 0;                             // reset for the next burst
    }, wait);
  }

  debounced.cancel = () => {                 // stop a pending trailing call
    clearTimeout(timer);                     // clear the timer
    timer = null;                            // no burst is active
    count = 0;                               // forget the burst
  };
  return debounced;                          // the wrapper with its cancel method
}

// Test 1: trailing only. Three calls, one run with the last value.
const save = debounce((v) => console.log("saved", v), 50);
save(1); save(2); save(3);                   // prints "saved 3" after 50 ms

// Test 2: leading and trailing. First call runs now, last call runs after the quiet period.
const instant = debounce((v) => console.log("instant", v), 50, { leading: true });
instant("a"); instant("b");                  // "instant a" now, "instant b" after 50 ms

// Test 3: cancel stops the pending call, so nothing is printed
const never = debounce(() => console.log("never"), 10);
never(); never.cancel();                     // cancelled before it runs

// Expected output, in order:
// instant a
// saved 3
// instant b

// Time:  O(1) per call (one clearTimeout and one setTimeout)
// Space: O(1), only the timer id and the latest arguments are stored
```

### Edge Cases
- Calls spaced further apart than `wait` each run on their own, because the timer finishes between them.
- Only the last arguments are used in trailing mode, so earlier values are dropped on purpose.
- `cancel()` clears a pending call. It is important on component unmount in React, so the function does not run after the screen closes.
- `wait = 0` still defers to the next macrotask, which is not the same as calling immediately.
- Using an arrow function for the wrapper would lose the caller's `this`; that is why the wrapper is a normal function.

---

## 🟠 Express.js Integration
Debounce usually runs in the browser, because it limits calls from the UI. The Express route below receives the debounced autosave, so the server does not get a request for every keystroke.

```javascript
// Express.js: the server receives one autosave request per pause, not one per keystroke
const express = require("express");           // web framework
const app = express();                        // create the app
app.use(express.json());                      // parse JSON bodies

const drafts = new Map();                     // in-memory store for demo (use a database in production)

// PUT /api/drafts/:id  body: { "text": "..." }  called by the client through a debounced function
app.put("/api/drafts/:id", (req, res) => {
  const { id } = req.params;                  // the draft id from the URL
  const text = req.body.text;                 // the latest text sent by the client
  if (typeof text !== "string") {             // validate the input type
    return res.status(400).json({ error: "text must be a string" }); // 400 Bad Request
  }
  drafts.set(id, { text, savedAt: Date.now() }); // store the latest version only
  res.json({ ok: true, savedAt: drafts.get(id).savedAt }); // 200 OK
});

// Browser side (for reference, not run by Node):
// const saveDraft = debounce((id, text) => fetch(`/api/drafts/${id}`, { method: "PUT", ... }), 500);
// textarea.addEventListener("input", (e) => saveDraft(id, e.target.value));

app.listen(process.env.PORT || 3000, () => {
  console.log("Draft API running");         // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the debounced function inside the event handler
✅ Correct: each event creates a new timer, so nothing is ever debounced. Create it once, outside the handler.

```javascript
function debounce(fn, wait) {                // basic debounce, repeated so this block runs alone
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}
const events = ["p", "pi", "pizza"];         // three keystrokes, typed one after another

// Wrong: a new debounced function for each keystroke, so each one has its own timer
for (const text of events) {
  const run = debounce((t) => console.log("run", t), 20); // new timer every time
  run(text);                                 // all three fire, so nothing was debounced
}
// Expected output (after 20 ms): run p, run pi, run pizza

// Right: one debounced function, created once and shared by all keystrokes
const runOnce = debounce((t) => console.log("run", t), 20); // created once
for (const text of events) runOnce(text);    // only the last keystroke survives the wait
// Expected output (after 20 ms): run pizza
```

❌ **Mistake 2:** Losing the arguments, or using the first call's arguments
✅ Correct: store the latest arguments on every call, so the final call is the one that runs.

```javascript
// Wrong: the first arguments are captured once and never updated
function badDebounce(fn, wait) {
  let timer;
  let first;                                       // BUG: set only once
  return (...args) => {
    first = first ?? args;                         // keeps the first call forever
    clearTimeout(timer);
    timer = setTimeout(() => fn(...first), wait);  // runs with the first value
  };
}
const shout = badDebounce((v) => console.log("bad", v), 20);
shout("a"); shout("b");                            // Expected output: bad a

// Right: always keep the latest arguments
function goodDebounce(fn, wait) {
  let timer;
  let latest;                                      // updated on every call
  return (...args) => {
    latest = args;                                 // the newest arguments win
    clearTimeout(timer);
    timer = setTimeout(() => fn(...latest), wait); // runs with the latest value
  };
}
const shout2 = goodDebounce((v) => console.log("good", v), 20);
shout2("a"); shout2("b");                          // Expected output: good b
```

---

## 🧠 Tricky Interview Question
```javascript
function debounce(fn, wait) {                // basic debounce, so this block runs alone
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}
const log = debounce((x) => console.log("run", x), 30);
log(1);
setTimeout(() => log(2), 10);                    // arrives before the first timer ends
setTimeout(() => log(3), 60);                    // arrives after the quiet period
// What is printed, and in what order?
```
Answer:
```
run 2   ← at about 40 ms (30 ms after the call at 10 ms); the call at 0 ms was replaced
run 3   ← at about 90 ms (30 ms after the call at 60 ms), a separate burst
```
Each burst is separate. The call with `1` never runs, because `2` replaced it before its timer ended. The call with `3` starts a new burst, so it runs on its own. Mention that the exact times depend on the timer, but the order and values are fixed.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between debounce and throttle?**
A1: Debounce waits for a pause and runs once at the end. Throttle runs at most once per interval while events keep coming. Use debounce for search and autosave; use throttle for scroll and drag.

**Q2: Why use `clearTimeout` and not a flag?**
A2: `clearTimeout` cancels the timer that is already scheduled, so the old call never runs. A flag would still need a timer to know when to run.

**Q3: Why must the wrapper be a normal function and not an arrow function?**
A3: A normal function receives `this` from how it is called, so `obj.method = debounce(fn)` keeps the right object. An arrow function takes `this` from where it was written.

**Q4: What does the leading option do?**
A4: It runs the function on the first call of a burst, right away. The trailing call still runs at the end if more calls came in. Use it when the first action must feel instant, such as a "save" button.

**Q5: What is the time complexity of debounce?**
A5: O(1) per call. Each call does one `clearTimeout` and one `setTimeout`. The function itself is not run until the timer fires.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The user types into a search box and each keystroke would call an API
- Autosave should happen after a pause, not after every change
- A resize or layout function is expensive and only the final size matters

❌ Avoid when:
- Every event matters, such as keyboard shortcuts or game input; a delay loses events
- You need a rate limit during a long action like scrolling; use throttle
- The function must run exactly once per event for logging or analytics

---

## 📊 Visual Diagram
```
calls:    p     pi    piz   pizz  pizza
          |     |     |     |     |
timer:    [----reset----reset----reset----reset----] 300 ms
                                                    |
                                                    v
                                         fn("pizza") runs once
time ->   0 ms                              ...    600 ms + 300 ms
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Debounce | Run once after calls stop for a set time | Calls रुकने के बाद एक बार चलाना |
| Trailing edge | The run at the end of the quiet period | Quiet period के अंत में चलना |
| Leading edge | The run at the start of a burst | Burst की शुरुआत में चलना |
| clearTimeout | Cancels a scheduled timer | Scheduled timer रद्द करना |
| Closure | A function that remembers variables from its creation | बनने के समय के variables याद रखने वाला function |
| cancel | Stops a pending debounced call | Pending call को रोकना |

---

## ⚡ 3-Line Summary
English:
1. Debounce restarts a timer on every call, so the function runs only after the calls stop.
2. Keep the latest arguments and the `this` value, so the final call uses the right data.
3. Create the debounced function once, and use `cancel()` on unmount to avoid late runs.

Hindi:
1. Debounce हर call पर timer फिर से शुरू करता है, इसलिए function calls रुकने के बाद ही चलता है।
2. आख़िरी arguments और `this` सहेजो, ताकि आख़िरी call सही data इस्तेमाल करे।
3. Debounced function एक बार बनाओ, और unmount पर `cancel()` करो ताकि देर से run न हो।

---

## ➡️ Next Topic
**172. Implement throttle** — debounce waits for a pause; the next problem limits a function to one run per interval, which suits scroll and drag events.
