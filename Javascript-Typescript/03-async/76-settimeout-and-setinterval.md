# 76. setTimeout + setInterval
# हिंदी में: setTimeout और setInterval — समय के बाद या बार-बार code चलाना

---

## 🔵 Simple Definition (English)
`setTimeout(fn, ms)` runs `fn` once after at least `ms` milliseconds. `setInterval(fn, ms)` runs `fn` repeatedly every `ms` milliseconds until it is cleared with `clearInterval`. Both return a handle that you use to cancel them.

## 🔵 सरल परिभाषा (Hindi)
`setTimeout(fn, ms)` `fn` को `ms` milliseconds के बाद एक बार चलाता है। `setInterval(fn, ms)` उसे हर `ms` पर बार-बार चलाता है, जब तक `clearInterval` से बंद न किया जाए। दोनों एक handle लौटाते हैं, जिससे उन्हें cancel किया जा सकता है।

---

## 🔴 Problem it Solves
Apps को समय-आधारित काम चाहिए: OTP का timeout, retry का अंतराल, cache की expiry, health check। इन्हें हाथ से "रुको और फिर करो" लिखना संभव नहीं। Timers यह काम runtime को सौंपते हैं, और callback तय समय के बाद queue में आता है।

## 🔴 यह क्यों बना? (Hindi)
Razorpay पर OTP 60 सेकंड में expire होना चाहिए। अगर server हर 5 सेकंड में अपनी status-check repeat न करे, तो stale data रह सकता है। `setTimeout` एक बार का cutoff देता है, और `setInterval` बार-बार की जाँच। दोनों एक ही timer system से चलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `setTimeout(fn, 500)` call होने पर runtime 500 ms का timer शुरू करता है और handle लौटाता है
Step 2 → Call stack खाली करके code आगे बढ़ता है
Step 3 → 500 ms पूरे होने पर `fn` callback queue में जाता है
Step 4 → Event loop timers phase में `fn` चलाता है
Step 5 → `setInterval` में यही चक्र हर बार दोहराया जाता है, जब तक `clearInterval(handle)` न हो

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `setTimeout(fn, 500)` पर runtime 500 ms का timer शुरू करता है और handle लौटाता है
Step 2 → Call stack खाली करके code आगे बढ़ता है
Step 3 → 500 ms पूरे होने पर `fn` queue में जाता है
Step 4 → Event loop timers phase में `fn` चलाता है
Step 5 → `setInterval` में यही चक्र बार-बार होता है, जब तक `clearInterval(handle)` न हो

---

## 🟡 Real World Example
Swiggy delivery tracking screen हर 10 सेकंड में rider की location मांगती है, जो `setInterval` का काम है। Order delivered होते ही उसे `clearInterval` से बंद किया जाता है। OTP screen पर 60 सेकंड का countdown `setTimeout` से होता है, और expire होने पर "Resend OTP" का button दिखता है।

## 🟡 Real Example Hindi mein
Swiggy की tracking screen हर 10 सेकंड में rider की location माँगती है, यह `setInterval` है। Order deliver होते ही `clearInterval` से बंद होता है। OTP screen का 60 सेकंड का countdown `setTimeout` से होता है, और expire होने पर "Resend OTP" दिखता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: setTimeout runs once; setInterval repeats until cleared
// Run with: node 76-settimeout-and-setinterval.js

// setTimeout: one-time callback after 100 ms
setTimeout(() => {
  console.log("OTP expired after 100 ms");     // runs once
}, 100);

// setInterval: repeats every 30 ms, counts ticks, stops after 3
let ticks = 0;                                 // counter for how many times it ran
const handle = setInterval(() => {
  ticks++;                                     // count this tick
  console.log(`Rider location update #${ticks}`); // one update per tick
  if (ticks === 3) {                           // after the third update...
    clearInterval(handle);                     // ...stop the repeating timer
    console.log("Tracking stopped");           // final message
  }
}, 30);

// Expected order: updates #1, #2, #3, "Tracking stopped", then the OTP message
// (the OTP message fires at 100 ms; the three ticks finish around 90 ms)
```

## 💻 Code Example — Advanced
```javascript
// Goal: retry with exponential backoff using setTimeout (safer than setInterval for retries)
// and a cancellable delay that cleans up its timer.

// Cancellable sleep: returns a promise and a cancel() function
function sleep(ms) {
  let timer;                                   // handle kept so we can cancel
  const promise = new Promise((resolve) => {
    timer = setTimeout(resolve, ms);           // resolve the promise after ms
  });
  const cancel = () => clearTimeout(timer);    // stop the timer if caller no longer needs it
  return { promise, cancel };                  // give both back to the caller
}

// Retry an async task with exponential backoff: waits 20, 40, 80 ms ...
async function retryWithBackoff(task, { retries = 3, baseMs = 20 } = {}) {
  let attempt = 0;                             // how many attempts we have made
  while (true) {                               // loop until success or out of retries
    try {
      attempt++;                               // count this try
      return await task(attempt);              // success: return the result immediately
    } catch (err) {
      if (attempt > retries) {                 // all retries used up
        throw new Error(`Failed after ${attempt} attempts: ${err.message}`);
      }
      const delay = baseMs * 2 ** (attempt - 1); // 20, 40, 80 ...
      console.log(`attempt ${attempt} failed, retry in ${delay} ms`);
      await sleep(delay).promise;              // wait before the next try (no busy loop)
    }
  }
}

// A fake task that succeeds only on the 3rd try
async function flakyPayment(attempt) {
  if (attempt < 3) throw new Error("gateway timeout"); // first two tries fail
  return "payment captured";                   // third try succeeds
}

async function main() {
  const result = await retryWithBackoff(flakyPayment, { retries: 3, baseMs: 20 });
  console.log("Result:", result);              // Result: payment captured

  // Cancellation demo: stop a long wait early
  const long = sleep(5000);                    // would wait 5 seconds
  setTimeout(() => long.cancel(), 10);         // cancel after 10 ms
  // long.promise never resolves after cancel, so we do not await it here
  console.log("Long wait cancelled before it finished");
}

main().catch((err) => console.error("Fatal:", err.message));
```

---

## 🟠 Express.js Integration
Express server में background job (जैसे cache cleanup या health ping) अक्सर `setInterval` से चलता है। Server बंद होते समय उसे `clearInterval` से बंद करना ज़रूरी है, वरना process बंद नहीं होता। नीचे का example एक cleanup job शुरू करता है, और `server.close` पर उसे रोकता है। यह सीधे Express का feature नहीं, Node के timer की normal usage है।

```javascript
const express = require("express");          // web framework
const app = express();

const sessions = new Map();                  // in-memory session store (id -> expiresAt)

// Background job: every 60 seconds, remove sessions that have expired
const cleanup = setInterval(() => {
  const now = Date.now();                    // current time in ms
  for (const [id, expiresAt] of sessions) {  // walk all sessions
    if (expiresAt < now) sessions.delete(id); // delete expired ones
  }
}, 60_000);

app.get("/login", (req, res) => {
  sessions.set("abc", Date.now() + 15 * 60_000); // session valid for 15 minutes
  res.json({ ok: true });                    // reply to the login request
});

const server = app.listen(3000);
// On shutdown, stop the background job so the process can exit cleanly
process.on("SIGTERM", () => {
  clearInterval(cleanup);                    // stop the repeating timer
  server.close(() => process.exit(0));       // close the server, then exit
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `setTimeout` को exact time पर चलने वाला मानना
✅ **Correct:** Delay "कम से कम" ms है। Main thread busy हो तो callback देर से चलता है।

```javascript
// Wrong: expecting exactly 100 ms
setTimeout(() => console.log("fired"), 100);

// Right: accept at-least semantics, and never rely on sub-millisecond precision
```

❌ **Mistake 2:** `setInterval` को बिना `clearInterval` के छोड़ देना
✅ **Correct:** Interval एक reference रखता है और process को चलता रखता है। जब काम खत्म हो, उसे बंद करो।

```javascript
// Wrong: this keeps the process alive forever
setInterval(() => console.log("tick"), 1000);

// Right: keep the handle and clear it when done
const h = setInterval(() => console.log("tick"), 1000);
setTimeout(() => clearInterval(h), 3000); // stop after 3 seconds
```

❌ **Mistake 3:** Slow async काम के साथ `setInterval` इस्तेमाल करना, जिससे runs overlap हो जाएँ
✅ **Correct:** `setInterval` नया run तय समय पर शुरू करता है, भले पिछला पूरा न हुआ हो। Async job के लिए recursive `setTimeout` बेहतर है।

```javascript
// Wrong: if fetchData takes longer than 1s, runs will pile up
setInterval(async () => { await fetchData(); }, 1000);

// Right: schedule the next run only after the current one finishes
async function poll() {
  await fetchData();                         // wait for this run to end
  setTimeout(poll, 1000);                    // then schedule the next one
}
poll();
```

---

## 🧠 Tricky Interview Question
```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log("var:", i), 0);   // var is function-scoped (one shared i)
}

for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log("let:", j), 0);   // let makes a new j for each iteration
}
// What is printed?
```
**Answer:** `var: 3`, `var: 3`, `var: 3`, फिर `let: 0`, `let: 1`, `let: 2`।

- `var i` पूरे function में एक ही variable है। Timers बाद में चलते हैं, तब तक loop खत्म होकर `i` 3 हो चुका होता है।
- `let j` हर iteration के लिए नया binding बनाता है। हर callback अपनी iteration का `j` पकड़ता है।
- यह closure और scope का सवाल है, पर timers के async होने से यह दिखता है।

---

## ⚫ Interview Questions + Answers

Q1: `setTimeout` और `setInterval` में क्या फर्क है?
A1: `setTimeout` callback को एक बार, तय समय के बाद चलाता है। `setInterval` उसे हर तय अंतराल पर बार-बार चलाता है, जब तक `clearInterval` न हो।

Q2: `setTimeout` का delay क्या guarantee करता है?
A2: कम से कम उतना delay। Call stack या event loop व्यस्त हो तो callback देर से चलता है। Node में 0 ms को 1 ms माना जाता है।

Q3: Timer को cancel कैसे करें?
A3: `setTimeout` या `setInterval` का लौटाया handle `clearTimeout` या `clearInterval` को देकर। Handle सही जगह रखना ज़रूरी है, वरना timer बंद नहीं होगा।

Q4: `setInterval` के बजाय recursive `setTimeout` कब बेहतर है?
A4: जब callback async हो और उसका समय अनिश्चित हो। Recursive `setTimeout` अगला run तभी schedule करता है जब पिछला पूरा हो, इसलिए overlap नहीं होता।

Q5: Node.js में timer का return value क्या है?
A5: Node में `setTimeout` एक `Timeout` object लौटाता है, जो `clearTimeout` में जाता है। Browser में यह number होता है। Node में `timer.unref()` से timer process को जिंदा नहीं रखता।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- OTP, session, cache expiry जैसे समय-सीमा वाले काम हों
- Polling, health check, या cleanup job बार-बार चलाना हो
- Retry का अंतराल तय करना हो

❌ Avoid when:
- Exact timing (जैसे audio या animation frames) चाहिए (requestAnimationFrame या high-res clock बेहतर)
- Async काम लंबा हो और runs overlap हो सकें (recursive setTimeout इस्तेमाल करो)
- Timer का handle खो जाए और बाद में cancel न हो पाए

---

## 📊 Visual Diagram
```
setInterval(fn, 30)  — repeats until cleared

 t=0ms   ─┐ schedule
 t=30ms  ─┤ fn() #1  ── "Rider location update #1"
 t=60ms  ─┤ fn() #2  ── "Rider location update #2"
 t=90ms  ─┤ fn() #3  ── "Rider location update #3"  → clearInterval(handle)
          └ stopped (no more ticks)

setTimeout(fn, 100)  — once

 t=0ms   ─┐ schedule
 t=100ms ─┘ fn() runs once, then done
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| setTimeout | Run once after delay | Delay के बाद एक बार चलाना |
| setInterval | Run repeatedly at fixed gap | तय अंतराल पर बार-बार चलाना |
| clearTimeout | Cancel a pending timeout | Pending timeout रद्द करना |
| clearInterval | Stop a repeating interval | Repeat होने वाला timer बंद करना |
| Handle | Object returned by the timer | Timer की पहचान |
| Backoff | Growing wait between retries | Retry के बीच बढ़ता अंतराल |
| Overlap | Two runs of the same job at once | एक ही काम के दो run एक साथ |

---

## ⚡ 3-Line Summary
**English:**
1. `setTimeout` एक बार, और `setInterval` बार-बार चलाता है; दोनों का handle होता है।
2. Delay "कम से कम" है, और `clearTimeout` / `clearInterval` से cancel करना ज़रूरी है।
3. Async repeating काम के लिए recursive `setTimeout` इस्तेमाल करो, ताकि runs overlap न हों।

**Hindi:**
1. `setTimeout` एक बार, और `setInterval` बार-बार चलाता है; दोनों का handle होता है।
2. Delay "कम से कम" है, और `clearTimeout` / `clearInterval` से cancel करना ज़रूरी है।
3. Async repeating काम के लिए recursive `setTimeout` इस्तेमाल करो, ताकि runs overlap न हों।

---

## ➡️ Next Topic
**77. Callbacks** — callbacks की basic pattern, error-first convention, और promises से पहले async code कैसे लिखा जाता था।
