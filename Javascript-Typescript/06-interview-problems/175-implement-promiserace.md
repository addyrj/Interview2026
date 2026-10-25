# 175. Implement Promise.race
# हिंदी में: Promise.race लागू करना — जो सबसे पहले settle हो, उसी का नतीजा लेना

---

## 🔵 Simple Definition (English)
`Promise.race` takes a list of promises and settles as soon as the first one settles, either by resolving or by rejecting. The result is that first outcome, and the others are ignored. It is the usual tool for timeouts.

## 🔵 सरल परिभाषा (Hindi)
`Promise.race` promises की list लेता है और जैसे ही पहला promise settle हो (resolve या reject), वही नतीजा लौटा देता है। बाकी results अनदेखे रहते हैं। Timeout बनाने के लिए यही सबसे आम तरीका है।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `promiseRace(iterable)` that returns a promise. It settles with the same outcome as the first input promise to settle, whether it fulfils or rejects. Plain values count as already-resolved promises. An empty input never settles, the same as the built-in.

A payment gateway can hang for 30 seconds. If the checkout waits forever, the user sees a spinner and leaves. A race between the real call and a timer lets the app stop waiting after, say, 3 seconds and show a clear message.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `promiseRace(iterable)` लिखो जो एक promise लौटाए। वह उसी नतीजे पर settle हो जिस पर पहला input promise settle हुआ हो, चाहे वह resolve हो या reject। सामान्य values को resolved promise माना जाए। खाली input कभी settle नहीं होता, built-in की तरह।

Payment gateway 30 सेकंड तक अटक सकता है। अगर checkout हमेशा इंतज़ार करे, तो user spinner देखकर चला जाता है। Real call और timer की race से app 3 सेकंड बाद रुककर साफ़ message दिखा सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Convert the input into an array.
Step 2 → Wrap each item with `Promise.resolve`, so plain values also count.
Step 3 → Attach `resolve` and `reject` of the outer promise to each item.
Step 4 → The first item to fulfil or reject calls its handler first, and the outer promise settles.
Step 5 → Later settlements call `resolve` or `reject` again, but a settled promise ignores them.
Step 6 → For a timeout, race the real work against a timer that rejects; clear the timer when the work finishes.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Input को array में बदलो।
Step 2 → हर item को `Promise.resolve` से लपेटो, ताकि सामान्य values भी गिनी जाएँ।
Step 3 → हर item के साथ बाहर वाले promise के `resolve` और `reject` जोड़ो।
Step 4 → जो item सबसे पहले fulfil या reject हो, उसका handler पहले चलता है, और बाहर वाला promise settle हो जाता है।
Step 5 → बाद के settlements `resolve` या `reject` को फिर से बुलाते हैं, पर settled promise उन्हें अनदेखा करता है।
Step 6 → Timeout के लिए असली काम को एक ऐसे timer के साथ race कराओ जो reject करता है; काम पूरा होने पर timer साफ़ करो।

---

## 🟡 Real World Example
Razorpay's checkout waits for the bank's response, but gives up after a fixed time and asks the user to retry. Swiggy's live tracking races the GPS update with a 5-second fallback, so the screen never shows a blank map. Amazon's search shows cached results when the live search is slower than a set time.

Scenario: A payment call takes 4 seconds. The timeout is 3 seconds. The race rejects with "timed out", and the app shows "Payment is taking longer, please check your bank app".

## 🟡 Real Example Hindi mein
Razorpay का checkout bank के response का इंतज़ार करता है, पर तय समय के बाद रुककर user से retry करने को कहता है। Swiggy की live tracking GPS update को 5 सेकंड के fallback के साथ race कराती है, ताकि screen पर खाली map न दिखे। Amazon की search, live search धीमी हो तो cached results दिखाती है।

उदाहरण: Payment call 4 सेकंड लेती है, और timeout 3 सेकंड है। Race "timed out" के साथ reject होती है, और app दिखाता है "Payment में ज़्यादा समय लग रहा है, कृपया bank app देखें"।

---

## 💻 Code Example — Basic
```javascript
// Basic: the first promise to settle decides the outcome
function promiseRaceBasic(items) {
  return new Promise((resolve, reject) => {   // the outer promise we return
    items.forEach((item) => {                 // attach handlers to every item
      Promise.resolve(item).then(resolve, reject); // the first settlement wins; later ones are ignored
    });
  });
}

// Sample: two servers answer, the faster one wins
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
promiseRaceBasic([delay(30, "slow server"), delay(10, "fast server")])
  .then((winner) => console.log(winner));    // Expected output: fast server

// Edge case: a rejection can also be the first to settle
promiseRaceBasic([delay(20, "ok"), Promise.reject(new Error("down"))])
  .catch((err) => console.log("first was:", err.message)); // Expected output: first was: down

// Edge case: a plain value is already resolved, so it wins immediately
promiseRaceBasic([42, delay(5, "later")]).then((v) => console.log(v)); // Expected output: 42
```

## 💻 Code Example — Advanced
```javascript
// Advanced: accepts any iterable, mirrors the built-in, and includes a timeout helper
function promiseRace(iterable) {
  const items = Array.from(iterable);        // turn the input into an array
  return new Promise((resolve, reject) => {  // one outer promise for the whole race
    // An empty input never settles, which is what the built-in does too
    for (const item of items) {              // subscribe to every item
      Promise.resolve(item).then(resolve, reject); // whichever settles first decides the result
    }
  });
}

// Timeout helper: race the real work against a timer that rejects
function withTimeout(promise, ms) {
  // Guard: the timeout must be a positive number
  if (typeof ms !== "number" || ms <= 0) throw new RangeError("ms must be a positive number");
  let timer;                                 // holds the timer id so we can clear it later
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`timed out after ${ms} ms`)), ms); // reject when time is up
  });
  // finally runs whether the race resolved or rejected, so the timer never keeps the process alive
  return promiseRace([promise, timeout]).finally(() => clearTimeout(timer));
}

// Test helpers
const sleep = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

(async () => {
  // Test 1: the faster promise wins
  console.log(await promiseRace([sleep(30, "slow"), sleep(10, "fast")])); // Expected output: fast

  // Test 2: the real work is slower than the timeout, so the timeout rejects
  try {
    await withTimeout(sleep(100, "late"), 20);
  } catch (err) {
    console.log(err.message);                // Expected output: timed out after 20 ms
  }

  // Test 3: the real work finishes in time, and the timer is cleared
  console.log(await withTimeout(sleep(5, "in time"), 50)); // Expected output: in time
})();

// Time:  O(n) to subscribe to n items
// Space: O(n) for the subscriptions and the one timer
```

### Edge Cases
- An empty input never settles; the promise stays pending forever, the same as the built-in.
- A rejection that comes first makes the race reject, even if a later item would have resolved.
- After the race has settled, later results are ignored, because a promise settles only once.
- In `withTimeout`, the timer is cleared with `finally`, so a finished request does not leave a timer running.
- The timed-out work is not cancelled by `withTimeout`; it keeps running in the background. Real systems use `AbortController` to stop the request.

---

## 🟠 Express.js Integration
An Express route calls an upstream payment API. If the upstream does not answer in 3 seconds, the route stops waiting and returns HTTP 504 (gateway timeout), so client connections are not held open.

```javascript
// Express.js: stop waiting for a slow upstream payment API after 3 seconds
const express = require("express");          // web framework
const app = express();                       // create the app

// Pretend upstream call (in real life this is an HTTP request to the payment provider)
const callPaymentGateway = (orderId) =>
  new Promise((resolve) => setTimeout(() => resolve({ orderId, status: "CAPTURED" }), 4000)); // slow on purpose

// Same timeout pattern as the advanced block: race the call against a timer
function withTimeout(promise, ms) {
  let timer;                                 // timer id, so it can be cleared
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(Object.assign(new Error("gateway timeout"), { code: "TIMEOUT" })), ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer)); // clean up in every case
}

// POST /api/payments/:orderId/capture
app.post("/api/payments/:orderId/capture", async (req, res) => {
  try {
    const result = await withTimeout(callPaymentGateway(req.params.orderId), 3000); // wait at most 3 s
    res.json(result);                        // 200 OK with the gateway answer
  } catch (err) {
    if (err.code === "TIMEOUT") {            // our own deadline passed
      return res.status(504).json({ error: "payment is taking longer, please check status later" }); // 504
    }
    res.status(502).json({ error: "payment provider failed" }); // 502 Bad Gateway for other failures
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Payment API running");        // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `Promise.race` to pick the one that resolved "successfully"
✅ Correct: it picks the first settlement, and a rejection counts as well.

```javascript
// Wrong: the author expects "ok" because it resolves, but the rejection came first
const delayReject = (ms) => new Promise((_, reject) => setTimeout(() => reject(new Error("fail")), ms));
const delayOk = (ms) => new Promise((resolve) => setTimeout(() => resolve("ok"), ms));
Promise.race([delayReject(5), delayOk(20)])
  .then((v) => console.log("result:", v))
  .catch((e) => console.log("result error:", e.message)); // Expected output: result error: fail

// Right: use Promise.allSettled when every outcome matters, and race only when the first one decides
Promise.allSettled([delayReject(5), delayOk(20)])
  .then((r) => console.log(r.map((x) => x.status).join(","))); // Expected output: rejected,fulfilled
```

❌ **Mistake 2:** Forgetting to clear the timeout timer after the work finishes
✅ Correct: clear the timer in `finally`, so the process can exit and no late rejection is created.

```javascript
// Wrong: the timer keeps running after the work is done, and it keeps Node alive
function badTimeout(promise, ms) {
  return Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(new Error("t/o")), ms))]);
}
badTimeout(Promise.resolve("done"), 5000).then((v) => console.log(v)); // Expected output: done (the 5 s timer is still pending)

// Right: clear the timer as soon as the race settles
function goodTimeout(promise, ms) {
  let timer;                                 // to clear later
  const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error("t/o")), ms); });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer)); // no timer left behind
}
goodTimeout(Promise.resolve("done"), 5000).then((v) => console.log(v)); // Expected output: done (process exits at once)
```

---

## 🧠 Tricky Interview Question
```javascript
const a = new Promise((resolve) => setTimeout(() => resolve("A"), 20));
const b = new Promise((resolve) => setTimeout(() => resolve("B"), 10));
const c = Promise.resolve("C");

Promise.race([a, b, c]).then((v) => console.log("winner:", v));
Promise.race([]).then((v) => console.log("empty:", v));
console.log("sync end");
```
Answer:
```
sync end        ← the synchronous line runs first; all promise callbacks are asynchronous
winner: C       ← c is already resolved, so its handler runs first in the microtask queue
```
The empty race never settles, so `empty:` is never printed. Explain that `Promise.race([a, b, c])` settles with the first handler that runs, which is `c`, because already-resolved promises run before timers. `b` and `a` are ignored.

---

## ⚫ Interview Questions + Answers

**Q1: What does `Promise.race` return for an empty array?**
A1: A promise that never settles. It stays pending forever, as the built-in does.

**Q2: Does a rejected promise win a race?**
A2: Yes. The race settles with whichever promise settles first, whether it resolves or rejects.

**Q3: How do you build a timeout with `Promise.race`?**
A3: Race the real promise with a timer promise that rejects after `ms`. Clear the timer in `finally` so it does not keep running.

**Q4: Does a timeout cancel the underlying work?**
A4: No. The race stops waiting, but the request keeps running. Use `AbortController` with `fetch` to really cancel it.

**Q5: What is the time complexity?**
A5: O(n) to subscribe to n promises. The race settles at the time of the first settlement, not after all of them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a timeout around a slow call
- The first available answer is enough, such as a cache versus a live source
- You are checking several mirrors or regions and want the fastest one

❌ Avoid when:
- You need every result; use `Promise.all` or `Promise.allSettled`
- The first result might be a failure you want to ignore; race rejects on the first failure
- You expect the timed-out work to stop; race does not cancel it

---

## 📊 Visual Diagram
```
Promise.race([ paymentCall (4 s), timer (3 s) ])

time:    0 s ............ 3 s ............ 4 s
paymentCall:  pending ......................  resolves (ignored, too late)
timer:        pending ........ rejects      <- first to settle
result:                       reject("timed out")  -> 504 to the client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Race | Several async tasks, the first to settle wins | कई async tasks में जो पहले settle हो वही जीते |
| Settle | Resolve or reject, the final state | Resolve या reject, अंतिम अवस्था |
| Timeout | A limit on how long we wait | इंतज़ार की अधिकतम सीमा |
| finally | Runs after the promise settles, in any case | Settle होने के बाद हर हाल में चलता है |
| AbortController | Lets you cancel a fetch request | Fetch request को रद्द करने का साधन |
| 504 | HTTP code for "gateway timeout" | "Gateway timeout" का HTTP code |

---

## ⚡ 3-Line Summary
English:
1. `Promise.race` settles with the first promise that settles, whether it resolves or rejects.
2. Use it for timeouts: race the real call against a timer, and clear the timer when done.
3. A race does not cancel the work, so use `AbortController` when you need to stop a request.

Hindi:
1. `Promise.race` उसी promise के नतीजे पर settle होता है जो सबसे पहले settle हो, चाहे resolve हो या reject।
2. Timeout के लिए इसका इस्तेमाल करो: असली call को timer के साथ race कराओ, और काम पूरा होने पर timer साफ़ करो।
3. Race काम को रद्द नहीं करती, इसलिए request रोकनी हो तो `AbortController` इस्तेमाल करो।

---

## ➡️ Next Topic
**176. Curry a Function** — the race and the batch helpers take arguments as a list; the next problem turns one function with many arguments into a chain of single-argument calls.
