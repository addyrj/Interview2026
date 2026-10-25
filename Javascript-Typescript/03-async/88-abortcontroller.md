# 88. AbortController
# हिंदी में: AbortController — Async Work (fetch, Timers) को Cancel करना

---

## 🔵 Simple Definition (English)
`AbortController` is a built-in object that lets you cancel one or more async operations. It has a `signal` (an `AbortSignal`) that you pass to `fetch` or your own code. Calling `controller.abort()` sets `signal.aborted` to `true` and fires an `abort` event, so the work can stop.

## 🔵 सरल परिभाषा (Hindi)
`AbortController` एक built-in object है जिससे आप एक या ज़्यादा async कामों को cancel कर सकते हो। इसके पास एक `signal` (`AbortSignal`) होता है, जिसे `fetch` या अपने code को देते हो। `controller.abort()` call करने पर `signal.aborted` `true` हो जाता है और `abort` event चलता है, जिससे काम रुक सकता है।

---

## 🔴 Problem it Solves
Promises cannot be cancelled. Once `fetch` starts, there is no `promise.cancel()`. Without cancellation, a user who leaves a search page still has requests running, a slow API keeps the server busy, and old responses can update the screen (the race from topic 87). `AbortController` gives a standard way to say "stop, I no longer need this".

## 🔴 यह क्यों बना? (Hindi)
Promise को cancel नहीं किया जा सकता। एक बार `fetch` शुरू हो गया, तो `promise.cancel()` जैसा कुछ नहीं है। Cancel न हो तो user search page छोड़ने के बाद भी requests चलती रहती हैं, धीमी API server को व्यस्त रखती है, और पुराने responses screen को बदल देते हैं (topic 87 वाली race)। `AbortController` एक standard तरीका देता है यह कहने का: "रुको, अब इसकी ज़रूरत नहीं है।"

---

## 🟢 How it Works — Step by Step

Step 1 → `const controller = new AbortController()` creates the controller
Step 2 → `controller.signal` is the signal you pass to `fetch(url, { signal })` or listen to yourself
Step 3 → When work is still pending, `controller.abort(reason)` sets `signal.aborted = true` and dispatches an `abort` event
Step 4 → `fetch` rejects with the signal's `reason` (name `AbortError` by default)
Step 5 → Your own code listens with `signal.addEventListener("abort", ...)` and cleans up timers or connections
Step 6 → Calling `abort()` again does nothing; a signal that is already aborted never fires `abort` again

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const controller = new AbortController()` controller बनाता है
Step 2 → `controller.signal` वह signal है जिसे `fetch(url, { signal })` को देते हो, या खुद सुनते हो
Step 3 → जब काम अभी pending हो, तब `controller.abort(reason)` `signal.aborted` को `true` करता है और `abort` event भेजता है
Step 4 → `fetch` signal के `reason` के साथ reject होता है (डिफ़ॉल्ट name `AbortError`)
Step 5 → अपना code `signal.addEventListener("abort", ...)` से सुनता है और timers या connections साफ़ करता है
Step 6 → `abort()` दोबारा call करने का कोई असर नहीं होता; पहले से aborted signal पर `abort` event दोबारा नहीं चलता

---

## 🟡 Real World Example
On Zomato's restaurant search, the user types "biryani", then changes to "pizza" before the first search returns. The app should cancel the "biryani" request, so its slow response cannot replace the "pizza" results. Another case: a checkout page times out payment status after 10 seconds, and the user can also press "Cancel". Both must stop the same request, which is what `AbortSignal.any` makes easy.

## 🟡 Real Example Hindi mein
Zomato के restaurant search में user "biryani" लिखता है, फिर पहला search आने से पहले "pizza" लिख देता है। App को "biryani" वाली request cancel करनी चाहिए, ताकि उसका धीमा जवाब "pizza" के results को न बदले। दूसरा case: checkout page 10 सेकंड बाद payment status का timeout करता है, और user "Cancel" भी दबा सकता है। दोनों एक ही request को रोकें, यही `AbortSignal.any` आसान बनाता है।

---

## 💻 Code Example — Basic
```javascript
// Fake fetch that respects AbortSignal (real fetch behaves the same way). No real network.
function fakeFetch(url, { signal } = {}) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason);     // already cancelled: reject at once
    const timer = setTimeout(() => {                       // pretend the server takes 300ms
      resolve({ url, status: 200 });                       // success if not cancelled
    }, 300);
    signal?.addEventListener(                              // listen for cancellation
      "abort",
      () => {
        clearTimeout(timer);                               // stop the pending work
        reject(signal.reason);                             // reject with the abort reason
      },
      { once: true }                                       // remove the listener after one call
    );
  });
}

const controller = new AbortController();                  // 1. create the controller
const { signal } = controller;                             // 2. take its signal

console.log("aborted before?", signal.aborted);            // false

fakeFetch("https://api.example.com/menu", { signal })      // 3. start work with the signal
  .then((res) => console.log("got:", res.status))          // not printed: cancelled first
  .catch((err) => console.log("error:", err.name, err.message)); // prints the cancel

setTimeout(() => controller.abort(), 100);                 // 4. user cancels after 100ms
setTimeout(() => console.log("aborted after?", signal.aborted), 150); // true
```

**Expected output (basic):**
```
aborted before? false
error: AbortError This operation was aborted
aborted after? true
```

## 💻 Code Example — Advanced
```javascript
// Advanced: combine a timeout with a user cancel using AbortSignal.any, and clean up properly.

// Fake fetch that respects AbortSignal (same as the basic example)
function fakeFetch(url, { signal } = {}) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason);     // already aborted
    const timer = setTimeout(() => resolve({ url, status: 200 }), 300); // 300ms "server"
    signal?.addEventListener("abort", () => {              // cancel path
      clearTimeout(timer);                                  // no leaked timer
      reject(signal.reason);                                // reject with the reason
    }, { once: true });
  });
}

// Combine: the request stops when the timeout OR the user's signal fires, whichever comes first
async function fetchWithTimeout(url, { timeoutMs, userSignal } = {}) {
  const signals = [AbortSignal.timeout(timeoutMs)];         // built-in: aborts after timeoutMs
  if (userSignal) signals.push(userSignal);                 // user cancel is optional
  const signal = AbortSignal.any(signals);                  // aborts when ANY input aborts
  try {
    const res = await fakeFetch(url, { signal });           // pass the combined signal
    return res;                                             // success path
  } catch (err) {
    console.log("request stopped:", err.name);               // log which kind of stop it was
    throw err;                                              // let the caller decide what to do
  }
}

(async () => {
  // 1. Timeout wins: the server needs 300ms, we allow 100ms
  try {
    await fetchWithTimeout("https://api.example.com/slow-menu", { timeoutMs: 100 });
  } catch (err) {
    console.log("1. timeout case:", err.name);               // TimeoutError
  }

  // 2. User cancel wins: user cancels after 50ms, timeout is 1000ms
  const userController = new AbortController();              // the user's "Cancel" button
  setTimeout(() => userController.abort(), 50);              // user presses cancel at 50ms
  try {
    await fetchWithTimeout("https://api.example.com/menu", {
      timeoutMs: 1000,
      userSignal: userController.signal,
    });
  } catch (err) {
    console.log("2. user cancel case:", err.name);           // AbortError
  }

  // 3. Success: nothing cancels, the response arrives in 300ms
  const ok = await fetchWithTimeout("https://api.example.com/menu", { timeoutMs: 1000 });
  console.log("3. success:", ok.status);                    // 200
})();
```

**Expected output (advanced):**
```
request stopped: TimeoutError
1. timeout case: TimeoutError
request stopped: AbortError
2. user cancel case: AbortError
3. success: 200
```

---

## 🟠 Express.js Integration
In Express, the most useful pattern is to cancel server-side work when the client disconnects, for example a slow report or a call to another service. Create a controller per request, abort it when the response closes early, and pass its signal to `fetch`. The `AbortError` is then ignored, because the client is gone and there is nothing to send.

```javascript
// Express.js example: cancel upstream work when the client disconnects
const express = require("express");                 // import Express
const app = express();                              // create the app

// Fake upstream call that honors a signal (real code: fetch(url, { signal }))
function buildReport(signal) {
  return new Promise((resolve, reject) => {         // returns a promise
    const timer = setTimeout(() => resolve({ rows: 10000 }), 5000); // 5 seconds of work
    signal.addEventListener("abort", () => {        // if the client leaves early
      clearTimeout(timer);                          // stop the work
      reject(signal.reason);                        // reject with the reason
    }, { once: true });
  });
}

app.get("/reports/sales", async (req, res, next) => {
  const controller = new AbortController();         // one controller per request
  res.on("close", () => {                           // fires when the response ends or the client leaves
    if (!res.writableEnded) controller.abort();     // only abort if we did not finish sending
  });
  try {
    const report = await buildReport(controller.signal); // pass the signal down
    res.json(report);                               // normal response
  } catch (err) {
    if (err.name === "AbortError") return;          // client is gone: nothing to send
    next(err);                                      // real error: error middleware
  }
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the controller once and reusing it after it has been aborted
✅ **Correct:** An aborted controller stays aborted. Create a new `AbortController` for each new request.

```javascript
// Wrong: the second request is already aborted, so it fails immediately
const c = new AbortController();
fetch("/api/a", { signal: c.signal });
c.abort();
fetch("/api/b", { signal: c.signal });     // rejects at once: signal is aborted

// Right: one controller per request
const c1 = new AbortController();
fetch("/api/a", { signal: c1.signal });
const c2 = new AbortController();
fetch("/api/b", { signal: c2.signal });
```

❌ **Mistake 2:** Treating `AbortError` as a real failure and showing an error to the user
✅ **Correct:** An abort is usually intentional (the user moved on). Ignore it or handle it quietly.

```javascript
// Wrong: the user sees "Something went wrong" every time they type quickly
try {
  await search(q, { signal });
} catch (err) {
  showError("Something went wrong");
}

// Right: ignore intentional aborts
try {
  await search(q, { signal });
} catch (err) {
  if (err.name !== "AbortError") showError("Something went wrong");
}
```

❌ **Mistake 3:** Forgetting to remove timers or listeners when the work finishes
✅ **Correct:** Clear timers in the abort handler, and use `{ once: true }` for listeners.

```javascript
// Wrong: the timer keeps running after the user has already cancelled
signal.addEventListener("abort", () => console.log("cancelled"));
setTimeout(doWork, 5000);                  // runs even though the request was cancelled

// Right: keep the timer id and clear it on abort
const t = setTimeout(doWork, 5000);
signal.addEventListener("abort", () => clearTimeout(t), { once: true });
```

---

## 🧠 Tricky Interview Output Question
```javascript
const c = new AbortController();                             // a fresh controller

c.signal.addEventListener("abort", () => console.log("listener 1")); // listener before abort
c.abort("network lost");                                     // abort with a custom reason

console.log("aborted:", c.signal.aborted, "reason:", c.signal.reason); // what is printed?

c.abort("second call");                                      // second abort: any effect?
c.signal.addEventListener("abort", () => console.log("listener 2")); // added after abort

console.log("done");
```
**Answer:**
```
listener 1
aborted: true reason: network lost
done
```
**Why:** `c.abort("network lost")` runs synchronously and fires the `abort` event right away, so `listener 1` prints before the next line. The reason is stored on the signal, so the log shows `reason: network lost`. The second `abort("second call")` does nothing, because a signal can be aborted only once, and the reason stays `"network lost"`. `listener 2` is added after the abort event has already been dispatched, so it never runs.

---

## ⚫ Interview Questions + Answers

Q1: What is an `AbortController` and what does it contain?
A1: An object with one property, `signal` (an `AbortSignal`), and one method, `abort(reason)`. Calling `abort` marks the signal as aborted and dispatches an `abort` event.

Q2: How do you cancel a `fetch`?
A2: Pass `signal: controller.signal` in the options. Calling `controller.abort()` makes `fetch` reject with an `AbortError`.

Q3: Can an aborted signal be reset?
A3: No. Create a new controller for each new operation.

Q4: What does `AbortSignal.timeout(ms)` do?
A4: It returns a signal that aborts automatically after `ms` milliseconds, with a `TimeoutError` as its reason. You do not need to create a controller or timer yourself.

Q5: What does `AbortSignal.any([...])` do?
A5: It returns one signal that aborts when any of the input signals aborts, and it uses that input's reason. This is how you combine a timeout with a user cancel.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The user can leave or change a search while a request is running
- You need timeouts for network calls
- A server-side task should stop when the client disconnects
- You want to cancel timers and listeners together with a request

❌ Avoid when:
- The work is short and can't cause stale UI updates (cancelling adds noise)
- You expect cancellation to undo work that has already happened on the server (it only stops waiting; a POST may still be processed)
- You reuse one controller across unrelated requests

---

## 📊 Visual Diagram
```
new AbortController()
   │
   ├── controller.signal ──► fetch(url, { signal })     ── pending ──┐
   │                      └► signal.addEventListener("abort", ...)   │
   │                                                                 │
   └── controller.abort(reason) ──► signal.aborted = true  ◄─────────┘
                                 ├─► "abort" event fires  → clean up timers
                                 └─► fetch rejects with reason (AbortError)

AbortSignal.timeout(ms) ──┐
                          ├──► AbortSignal.any([...]) ──► one signal for fetch
user controller.signal  ──┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `AbortController` | Object that creates and triggers a cancel signal | Cancel signal बनाने और चलाने वाला object |
| `AbortSignal` | The read-only signal passed to work | वह signal जो काम को दिया जाता है |
| `abort(reason)` | Cancels the operation and stores the reason | काम cancel करना और कारण रखना |
| `signal.aborted` | True after abort | Abort होने के बाद true |
| `AbortError` | Default error name for user abort | User abort का डिफ़ॉल्ट error name |
| `AbortSignal.timeout` | Signal that aborts after given ms | दिए गए ms बाद abort होने वाला signal |
| `AbortSignal.any` | One signal that aborts when any input aborts | कोई भी input abort हो तो abort होने वाला signal |

---

## ⚡ 3-Line Summary
**English:**
1. `AbortController.abort()` cancels any work that accepts a `signal`, and `fetch` rejects with an `AbortError`.
2. Use one controller per request, and clean up timers and listeners in the abort handler.
3. Combine timeouts and user cancels with `AbortSignal.timeout` and `AbortSignal.any`, and ignore intentional aborts in the UI.

**Hindi:**
1. `AbortController.abort()` signal लेने वाले किसी भी काम को cancel करता है, और `fetch` `AbortError` के साथ reject होता है।
2. हर request के लिए एक controller रखो, और abort handler में timers और listeners साफ़ करो।
3. Timeout और user cancel को `AbortSignal.timeout` और `AbortSignal.any` से जोड़ो, और UI में जानबूझकर किए गए abort को error मत दिखाओ।

---

## ➡️ Next Topic
**89. Async Generators** — Now you can cancel async work. Next, learn async generators (`async function*` with `for await...of`), which produce a stream of values over time, such as paginated API results.
