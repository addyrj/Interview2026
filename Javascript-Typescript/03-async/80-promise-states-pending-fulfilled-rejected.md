# 80. Promise States (pending, fulfilled, rejected)
# हिंदी में: Promise States — pending, fulfilled और rejected का पूरा नियम

---

## 🔵 Simple Definition (English)
Every Promise is in exactly one of three states: **pending** (result not ready), **fulfilled** (succeeded with a value), or **rejected** (failed with a reason). Once a promise leaves `pending`, it is **settled** and can never change state again.

## 🔵 सरल परिभाषा (Hindi)
हर Promise तीन में से एक state में होता है: **pending** (result अभी नहीं आया), **fulfilled** (value के साथ सफल), या **rejected** (reason के साथ असफल)। एक बार `pending` से निकल गया, तो वह **settled** हो जाता है और फिर कभी state नहीं बदलता।

---

## 🔴 Problem it Solves
अगर किसी async काम की state साफ़ न हो, तो code यह तय नहीं कर सकता कि result पढ़ा जा सकता है या अभी इंतज़ार करना है। एक ही result दो बार बदल जाए, तो caching और retry logic गलत चलेंगे। Promise state के सख्त नियम इन समस्याओं को रोकते हैं।

## 🔴 यह क्यों बना? (Hindi)
Razorpay के payment status को सोचो: एक बार "success" हो गया, तो वह "failed" नहीं हो सकता। अगर promise state बदल सकती, तो एक ही payment दो बार capture या दो बार refund हो सकता। State का "एक बार settle, हमेशा settle" नियम इसी को रोकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Promise बनते ही state `pending` होती है
Step 2 → Executor में `resolve(value)` बुलाने पर state `fulfilled` होती है
Step 3 → Executor में `reject(reason)` बुलाने पर state `rejected` होती है
Step 4 → एक बार settle होने के बाद बाद की resolve या reject calls ignore होती हैं
Step 5 → `then` और `catch` handlers settle होने के बाद microtask queue में चलते हैं

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Promise बनते ही state `pending` होती है
Step 2 → `resolve(value)` बुलाने पर state `fulfilled` होती है
Step 3 → `reject(reason)` बुलाने पर state `rejected` होती है
Step 4 → एक बार settle होने के बाद बाद की resolve/reject calls ignore होती हैं
Step 5 → `then`/`catch` handlers settle होने के बाद microtask queue में चलते हैं

---

## 🟡 Real World Example
Paytm wallet top-up: request भेजी गई (pending)। Bank ने पैसे जोड़ दिए (fulfilled), या bank ने मना कर दिया (rejected)। एक बार "fulfilled" हो गया, तो बाद में आया duplicate webhook उसे बदल नहीं सकता। इससे wallet balance दो बार नहीं बढ़ता, यह Promise के "settle once" नियम का असर है।

## 🟡 Real Example Hindi mein
Paytm wallet top-up: request गई (pending)। Bank ने पैसे जोड़े (fulfilled) या मना किया (rejected)। एक बार fulfilled हुआ तो बाद का duplicate webhook उसे बदल नहीं सकता, इसलिए balance दो बार नहीं बढ़ता।

---

## 💻 Code Example — Basic
```javascript
// Demo: watch a promise move from pending to fulfilled or rejected
// Run with: node 80-promise-states-pending-fulfilled-rejected.js

// track(p): attaches handlers and records the state in a plain object
function track(p) {
  const info = { state: "pending", value: undefined }; // starts pending
  p.then(
    (v) => { info.state = "fulfilled"; info.value = v; },   // success handler sets state
    (e) => { info.state = "rejected"; info.value = e; }     // failure handler sets state
  );
  return info;                                 // caller reads info.state later
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms)); // helper: sleep for ms

async function main() {
  const never = new Promise(() => {});        // never resolves, so stays pending forever
  const paid = new Promise((r) => setTimeout(() => r("paid"), 10));          // fulfills at 10 ms
  const declined = new Promise((_, j) => setTimeout(() => j(new Error("declined")), 20)); // rejects at 20 ms

  const a = track(never);
  const b = track(paid);
  const c = track(declined);

  console.log(a.state, b.state, c.state);      // pending pending pending

  await wait(15);                              // let 15 ms pass
  console.log(a.state, b.state, c.state);      // pending fulfilled pending

  await wait(15);                              // let 30 ms pass in total
  console.log(a.state, b.state, c.state);      // pending fulfilled rejected
  console.log("value of paid:", b.value);      // value of paid: paid
}

main();
```

## 💻 Code Example — Advanced
```javascript
// Goal: a Deferred object that enforces "settle once" and exposes its state safely.

class Deferred {
  #state = "pending";                          // private: current state
  #resolveFn;                                  // private: the real resolve function
  #rejectFn;                                   // private: the real reject function
  #promise;                                    // private: the wrapped promise

  constructor() {
    this.#promise = new Promise((resolve, reject) => {
      this.#resolveFn = resolve;               // capture resolve so we can call it later
      this.#rejectFn = reject;                 // capture reject so we can call it later
    });
  }

  get state() {
    return this.#state;                        // read-only view of the state
  }

  get promise() {
    return this.#promise;                      // the promise callers can await
  }

  resolve(value) {
    if (this.#state !== "pending") return false; // already settled: ignore the call
    this.#state = "fulfilled";                 // move to fulfilled
    this.#resolveFn(value);                    // settle the real promise
    return true;                               // tell the caller it took effect
  }

  reject(reason) {
    if (this.#state !== "pending") return false; // already settled: ignore the call
    this.#state = "rejected";                  // move to rejected
    this.#rejectFn(reason);                    // settle the real promise
    return true;                               // tell the caller it took effect
  }
}

async function main() {
  const d = new Deferred();                    // starts pending

  console.log("initial:", d.state);            // pending
  console.log("first resolve applied:", d.resolve("first")); // true
  console.log("second resolve applied:", d.resolve("second")); // false, already settled
  console.log("reject after resolve applied:", d.reject(new Error("late"))); // false

  console.log("final state:", d.state);        // fulfilled
  console.log("awaited value:", await d.promise); // first (the first settle wins)

  // Use case: a payment confirmation that only the first webhook can settle
  const confirm = new Deferred();
  setTimeout(() => confirm.resolve({ txn: "T1", status: "captured" }), 10); // first webhook
  setTimeout(() => confirm.resolve({ txn: "T1", status: "duplicate" }), 20); // duplicate ignored
  const result = await confirm.promise;
  console.log("confirmed:", result.status);    // captured
}

main().catch((err) => console.error("fatal:", err));
```

---

## 🟠 Express.js Integration
Express route में promise state का सबसे सीधा असर `res.json` और `next(err)` के चुनाव पर होता है। Promise `fulfilled` हो तो response जाता है, और `rejected` हो तो error middleware में। नीचे का route एक async lookup लेता है, और state के हिसाब से सही response भेजता है। Express का अपना कोई state-tracking feature नहीं है, यह normal promise handling है।

```javascript
const express = require("express");          // web framework
const app = express();

// Async lookup: returns a promise that will fulfill with a record or reject with an error
function findPayment(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id === "bad") return reject(new Error("payment not found")); // rejected state
      resolve({ id, status: "captured" });   // fulfilled state
    }, 10);
  });
}

app.get("/payments/:id", async (req, res, next) => {
  try {
    const payment = await findPayment(req.params.id); // promise must settle before continuing
    res.json(payment);                        // fulfilled: send the value
  } catch (err) {
    res.status(err.message.includes("not found") ? 404 : 500) // rejected: map to an HTTP code
      .json({ error: err.message });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** सोचना कि promise के दो बार resolve होने पर दूसरा value लागू होगा
✅ **Correct:** पहला settle जीतता है। बाद की resolve/reject calls ignore होती हैं।

```javascript
// Wrong: expecting the value to change to "second"
const p = new Promise((resolve) => {
  resolve("first");
  resolve("second");                         // ignored
});
p.then((v) => console.log(v));               // first

// Right: design code so only one settle path exists, or use a Deferred
```

❌ **Mistake 2:** `console.log(promise)` से value पाने की उम्मीद करना
✅ **Correct:** Promise object का state `console.log` में `Promise { <pending> }` या `Promise { value }` दिखता है, पर value पाने के लिए `await` या `.then` चाहिए।

```javascript
// Wrong: treating the promise as its value
const p2 = Promise.resolve(42);
console.log(p2 + 1); // "[object Promise]1" — not 43

// Right: await the promise to get the value
(async () => {
  const v = await p2;
  console.log(v + 1); // 43
})();
```

❌ **Mistake 3:** `pending` promise को state check करके "अभी नहीं आया" समझकर उसे अनदेखा करना
✅ **Correct:** Pending promise कभी न settle हो सकता है। इसलिए timeout लगाओ (`Promise.race`) या cancellation रखो।

```javascript
// Wrong: waiting forever if the promise never settles
const forever = new Promise(() => {});
await forever;                               // hangs

// Right: race with a timeout
const timeout = new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 500));
await Promise.race([forever, timeout]);      // rejects after 500 ms
```

---

## 🧠 Tricky Interview Question
```javascript
const p = new Promise((resolve, reject) => {
  resolve("first");                          // this settles the promise
  reject(new Error("second"));               // ignored: already fulfilled
  resolve("third");                          // ignored too
});

p.then((v) => console.log(v))                // what is printed?
 .catch((e) => console.log("caught", e.message));
```
**Answer:** `first`। Promise पहली `resolve("first")` से fulfilled हो गया। उसके बाद `reject` और दूसरा `resolve` ignore हुए, क्योंकि settle होने के बाद state नहीं बदलती। इसलिए `.catch` कभी नहीं चलता, और `.then` को `"first"` मिलता है। यही "settle once" नियम है।

---

## ⚫ Interview Questions + Answers

Q1: Promise की तीन states कौन-सी हैं?
A1: `pending` (result अभी नहीं आया), `fulfilled` (सफल, एक value के साथ), और `rejected` (असफल, एक reason के साथ)।

Q2: Settled promise का state कब बदल सकता है?
A2: कभी नहीं। एक बार `fulfilled` या `rejected` होने पर वह हमेशा वही रहता है। बाद की resolve/reject calls ignore होती हैं।

Q3: `fulfilled` और `rejected` में अंतर के लिए handlers कौन-से हैं?
A3: `.then(onFulfilled, onRejected)` या `.then(...).catch(...)`। `await` के साथ try/catch भी rejection पकड़ता है।

Q4: Promise state सीधे code से पढ़ी जा सकती है?
A4: JavaScript में standard API नहीं है। `console.log` में दिखता है, पर code से पढ़ने के लिए tracker (जैसे ऊपर का `track`) या custom Deferred बनाना पड़ता है।

Q5: Pending promise से बचने के लिए क्या करें?
A5: Timeout के साथ `Promise.race` लगाएँ, या cancellation signal (AbortController) इस्तेमाल करें। Pending promise अनिश्चित समय तक रह सकता है, इसलिए उसे बिना सीमा के await न करें।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Async काम के state को समझकर logic लिखना हो (जैसे loading, success, error screens)
- Duplicate events से बचना हो, जहाँ पहला settle जीते
- Pending work पर timeout या cancellation लगाना हो

❌ Avoid when:
- Promise को value मानकर उसके साथ सीधे calculation करना हो
- Pending promise को बिना timeout के await करना हो
- Settle होने के बाद state बदलने की उम्मीद करना हो

---

## 📊 Visual Diagram
```
                 resolve(v)
   ┌───────────┐ ───────────▶ ┌────────────┐
   │  PENDING  │              │ FULFILLED  │  value = v   (final)
   └───────────┘ ───────────▶ └────────────┘
        │          reject(e)
        │                    ┌────────────┐
        └──────────────────▶ │ REJECTED   │  reason = e  (final)
                             └────────────┘

   Once FULFILLED or REJECTED, later resolve()/reject() calls are ignored.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pending | Result not ready yet | Result अभी नहीं आया |
| Fulfilled | Succeeded with a value | Value के साथ सफल |
| Rejected | Failed with a reason | Reason के साथ असफल |
| Settled | Fulfilled or rejected (final) | अंतिम रूप से तय हो चुका |
| Executor | Function that controls resolve/reject | Resolve/reject को नियंत्रित करने वाला function |
| Deferred | Object that exposes resolve and reject from outside | बाहर से settle करने वाला object |
| Idempotent settle | Only the first settle has effect | केवल पहला settle असर करता है |

---

## ⚡ 3-Line Summary
**English:**
1. हर Promise pending, fulfilled या rejected होता है, और settle होने के बाद state नहीं बदलती।
2. Executor में पहली `resolve` या `reject` ही जीतती है, बाद की calls ignore होती हैं।
3. Pending promise कभी न settle हो सकता है, इसलिए उस पर timeout या cancellation लगाओ।

**Hindi:**
1. हर Promise pending, fulfilled या rejected होता है, और settle होने के बाद state नहीं बदलती।
2. Executor में पहली `resolve` या `reject` ही जीतती है, बाद की calls ignore होती हैं।
3. Pending promise कभी न settle हो सकता है, इसलिए उस पर timeout या cancellation लगाओ।

---

## ➡️ Next Topic
**81. Promise Chaining and Error Propagation** — chain में value कैसे आगे बढ़ती है, error कैसे bubble होता है, और `then` के अंदर return का असर।
