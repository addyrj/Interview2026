# 79. Promises — Complete Guide
# हिंदी में: Promises — भविष्य में मिलने वाले result का पूरा गाइड

---

## 🔵 Simple Definition (English)
A **Promise** is an object that represents the eventual result of an async operation. It is either pending, fulfilled with a value, or rejected with a reason. You attach work with `.then`, `.catch`, and `.finally`, and combine many with `Promise.all`, `allSettled`, `race`, and `any`.

## 🔵 सरल परिभाषा (Hindi)
**Promise** एक object है जो async काम के भविष्य के result को दर्शाता है। वह या तो pending होता है, या value के साथ fulfilled, या reason के साथ rejected। काम जोड़ने के लिए `.then`, `.catch`, `.finally` लगते हैं, और कई promises को `Promise.all`, `allSettled`, `race`, `any` से combine किया जाता है।

---

## 🔴 Problem it Solves
Callbacks में result और error दोनों एक callback के argument में आते हैं, nesting बढ़ती है, और return value नहीं मिलता। Promise एक ऐसी वस्तु देता है जिसे कहीं भी pass किया जा सके, chain किया जा सके, और एक जगह error पकड़ा जा सके। यह callback hell का सीधा जवाब है।

## 🔴 यह क्यों बना? (Hindi)
Swiggy पर order placed → payment confirmed → restaurant accepted → rider assigned, यह चार dependent steps हैं। Promise से यह chain में लिखा जाता है, और कोई भी step fail हो तो एक `catch` उसे पकड़ता है। Callbacks में यही काम कई if-else और nesting से होता।

---

## 🟢 How it Works — Step by Step

Step 1 → `new Promise((resolve, reject) => ...)` बनता है, state `pending` से शुरू होती है
Step 2 → अंदर का async काम पूरा होने पर `resolve(value)` या `reject(err)` बुलाया जाता है
Step 3 → State बदलती है, और पहले से जुड़े `then` या `catch` handlers microtask queue में जाते हैं
Step 4 → `.then(fn)` का return एक नया Promise है, इसलिए chain बनती है
Step 5 → `.finally` हर हाल में चलता है, और error अगले `.catch` तक bubble करता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `new Promise((resolve, reject) => ...)` बनता है, state `pending` से शुरू होती है
Step 2 → Async काम पूरा होने पर `resolve(value)` या `reject(err)` बुलाया जाता है
Step 3 → State बदलती है, और जुड़े `then`/`catch` handlers microtask queue में जाते हैं
Step 4 → `.then(fn)` एक नया Promise लौटाता है, इसलिए chain बनती है
Step 5 → `.finally` हर हाल में चलता है, और error अगले `.catch` तक bubble होता है

---

## 🟡 Real World Example
Razorpay की refund flow: refund request बनाना → bank API को भेजना → status update करना → user को email भेजना। हर step promise return करता है। अगर bank API fail हो, तो `catch` में refund status "failed" लिखा जाता है और `finally` में connection बंद होता है। यह पूरा flow एक chain में साफ़ पढ़ा जाता है।

## 🟡 Real Example Hindi mein
Razorpay की refund flow: refund request बनाना → bank API को भेजना → status update → user को email। हर step एक promise लौटाता है। Bank fail हो तो `catch` में status "failed" लिखा जाता है, और `finally` में connection बंद होता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: create a promise, chain then/catch/finally, and combine with Promise.all
// Run with: node 79-promises-complete-guide.js

// A promise that resolves with a value after 20 ms (simulated network call)
function fetchOrder(id) {
  return new Promise((resolve) => {          // executor runs immediately
    setTimeout(() => resolve({ id, total: 499 }), 20); // resolve when "data" arrives
  });
}

// A promise that rejects after 10 ms (simulated payment failure)
function chargeCard(amount) {
  return new Promise((resolve, reject) => {
    setTimeout(() => reject(new Error(`card declined for ${amount}`)), 10);
  });
}

fetchOrder(7)
  .then((order) => {                         // runs when fetchOrder resolves
    console.log("order:", order);            // { id: 7, total: 499 }
    return chargeCard(order.total);          // returning a promise: chain waits for it
  })
  .then(() => console.log("paid"))           // skipped because chargeCard rejected
  .catch((err) => console.log("error:", err.message)) // catches the rejection above
  .finally(() => console.log("cleanup done")); // runs no matter what happened

// Promise.all: waits for all promises; rejects as soon as one rejects
Promise.all([fetchOrder(1), fetchOrder(2)])
  .then((orders) => console.log("both orders:", orders.map((o) => o.id))); // [ 1, 2 ]
```

## 💻 Code Example — Advanced
```javascript
// Goal: production helpers: timeout, retry with backoff, and parallel with partial failures

// 1. Reject a promise if it takes longer than `ms` (clear the timer when it settles)
function withTimeout(promise, ms, label = "operation") {
  let timer;                                   // handle so we can clear it later
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms} ms`)), ms);
  });
  return Promise.race([promise, timeout])      // whichever settles first wins
    .finally(() => clearTimeout(timer));       // always clear the timer (no leaks)
}

// 2. Retry a promise-returning function with exponential backoff
async function retry(fn, { attempts = 3, baseMs = 10 } = {}) {
  let lastErr;                                 // remember the last failure
  for (let i = 1; i <= attempts; i++) {        // try up to `attempts` times
    try {
      return await fn(i);                      // success: return the value immediately
    } catch (err) {
      lastErr = err;                           // keep the error for the final throw
      if (i < attempts) {
        await new Promise((r) => setTimeout(r, baseMs * 2 ** (i - 1))); // wait before retry
      }
    }
  }
  throw new Error(`all ${attempts} attempts failed: ${lastErr.message}`); // give up
}

// 3. Fake services for the demo
const slowService = () => new Promise((r) => setTimeout(() => r("slow ok"), 200));
const flakyService = (attempt) =>
  attempt < 2 ? Promise.reject(new Error("503")) : Promise.resolve("flaky ok");

async function main() {
  // Timeout: slow service is cut off after 50 ms
  try {
    await withTimeout(slowService(), 50, "slowService");
  } catch (err) {
    console.log("timeout case:", err.message); // slowService timed out after 50 ms
  }

  // Retry: first attempt fails, second succeeds
  const value = await retry(flakyService, { attempts: 3, baseMs: 5 });
  console.log("retry case:", value);          // flaky ok

  // allSettled: every promise finishes, we see each outcome
  const outcomes = await Promise.allSettled([
    Promise.resolve("inventory ok"),
    Promise.reject(new Error("coupon api down")),
  ]);
  console.log(outcomes.map((o) => o.status));  // [ 'fulfilled', 'rejected' ]
}

main().catch((err) => console.error("fatal:", err));
```

---

## 🟠 Express.js Integration
Express route handlers में promises सबसे ज़्यादा इस्तेमाल होते हैं, क्योंकि DB, HTTP और file calls सब promises लौटाते हैं। नीचे का route `Promise.all` से दो independent data sources को parallel में लाता है। Express 5 में async handler का rejected promise अपने-आप `next(err)` को जाता है, और Express 4 में `try/catch` जैसा यह example लिखा गया है।

```javascript
const express = require("express");          // web framework
const app = express();

// Two independent data sources, each returning a promise
const getProfile = (id) => Promise.resolve({ id, name: "Aditya" });
const getRecentOrders = (id) => Promise.resolve([{ id: 101, total: 499 }]);

app.get("/dashboard/:id", async (req, res, next) => {
  try {
    const userId = req.params.id;             // id from the URL
    // Both calls start immediately and run in parallel; we wait for both together
    const [profile, orders] = await Promise.all([
      getProfile(userId),                     // promise 1
      getRecentOrders(userId),                // promise 2
    ]);
    res.json({ profile, orders });            // combined response
  } catch (err) {
    next(err);                                // if either promise rejects, the error goes here
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `.then` के अंदर से value return करना भूल जाना
✅ **Correct:** `.then` का return value अगली chain में जाता है। Return न करने पर अगला step `undefined` पाता है।

```javascript
// Wrong: the second then receives undefined
Promise.resolve(5)
  .then((n) => { n * 2; })                    // no return
  .then((v) => console.log(v));               // undefined

// Right: return the value
Promise.resolve(5)
  .then((n) => n * 2)
  .then((v) => console.log(v));               // 10
```

❌ **Mistake 2:** Promise को `await` या `.then` किए बिना छोड़ देना, जिससे error unhandled रह जाए
✅ **Correct:** हर promise को await करो, return करो, या उसके साथ catch जोड़ो।

```javascript
// Wrong: rejection is never handled; Node may crash with unhandledRejection
function save() {
  Promise.reject(new Error("db down")); // nobody awaits or catches it
}
save();

// Right: await it, or attach a catch
async function saveRight() {
  await Promise.reject(new Error("db down")).catch((e) => console.log("handled:", e.message));
}
saveRight();
```

❌ **Mistake 3:** `Promise.all` को सभी results का इंतज़ार मानना, जबकि एक reject होते ही वह reject हो जाता है
✅ **Correct:** सभी outcomes चाहिए तो `Promise.allSettled` इस्तेमाल करो।

```javascript
// Wrong: one failure hides the successful results
// const [a, b] = await Promise.all([okPromise, failPromise]); // throws, a and b lost

// Right: get every outcome, then decide
const results = await Promise.allSettled([okPromise, failPromise]);
// results[0].value and results[1].reason are both available
```

---

## 🧠 Tricky Interview Question
```javascript
Promise.resolve(1)
  .then((x) => x + 1)                         // 1 + 1 = 2
  .then((x) => {
    throw new Error("boom " + x);             // throws with message "boom 2"
  })
  .catch((e) => {
    console.log(e.message);                   // handles the error
    return 10;                                // returning a value recovers the chain
  })
  .then((x) => console.log("value", x));      // what is printed here?
```
**Answer:** पहले `boom 2` छपता है, फिर `value 10`। `throw` होते ही chain रुक जाती है और अगला `.then` skip होता है। `.catch` error पकड़ता है, उसके अंदर log होता है, और `return 10` से chain को "recover" करता है। इसलिए बाद का `.then` fulfilled value `10` के साथ चलता है। अगर `catch` में `return` न होता, तो `x` `undefined` होता।

---

## ⚫ Interview Questions + Answers

Q1: Promise क्या है?
A1: Async काम के भविष्य के result का object। State `pending` से शुरू होकर `fulfilled` या `rejected` बनती है, और एक बार settle होने पर बदलती नहीं।

Q2: `then`, `catch`, `finally` में क्या फर्क है?
A2: `then` fulfilled value पर चलता है, `catch` rejection पर, और `finally` दोनों हालात में बिना value के। तीनों नया Promise लौटाते हैं, इसलिए chain बनती है।

Q3: `Promise.all`, `allSettled`, `race`, `any` में क्या फर्क है?
A3: `all` सब fulfilled होने पर array देता है, पर एक reject होते ही reject। `allSettled` हर outcome देता है। `race` पहले settle होने वाले को लेता है। `any` पहले fulfilled को लेता है, और सब reject हों तो `AggregateError` देता है।

Q4: Promise constructor के अंदर throw हो तो क्या होता है?
A4: Executor के अंदर sync throw हो तो Promise उसी error से reject हो जाता है। उसे `.catch` या `await` के try/catch से पकड़ा जा सकता है।

Q5: Promise chain में error कहाँ पकड़ा जाता है?
A5: Error अगले उपलब्ध `.catch` तक bubble करता है। जब तक कोई catch न हो, वह unhandled rejection बनता है। इसलिए chain के अंत में एक catch रखना अच्छा अभ्यास है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Async काम को return करके chain या combine करना हो
- Multiple independent async calls को parallel में चलाना हो (`Promise.all`)
- Callback-based API को promise में wrap करना हो

❌ Avoid when:
- एक ही सरल sync काम हो जिसे promise में लपेटना बेवजह हो
- Promise को catch किए बिना छोड़ना हो
- Promise constructor के अंदर async काम को बेवजह nest करना हो (`new Promise(async ...)` anti-pattern है)

---

## 📊 Visual Diagram
```
  new Promise((resolve, reject) => { ... })
             │
             ▼
        ┌─────────┐   resolve(v)    ┌────────────┐  .then(fn)  ┌──────────────┐
        │ pending │ ───────────────▶│ fulfilled  │ ──────────▶ │ next then()  │
        └─────────┘                 └────────────┘             └──────────────┘
             │
             │       reject(e)     ┌────────────┐  .catch(fn) ┌──────────────┐
             └───────────────────▶ │ rejected   │ ──────────▶ │ recovers or  │
                                   └────────────┘             │ passes on    │
                                                              └──────────────┘
  .finally(fn) always runs, then the original outcome passes through.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Promise | Object for a future result | भविष्य के result का object |
| Executor | Function passed to `new Promise` | `new Promise` में दिया गया function |
| then | Handler for fulfilled value | सफल value पर चलने वाला handler |
| catch | Handler for rejection | Error पर चलने वाला handler |
| finally | Runs regardless of outcome | हर हाल में चलने वाला handler |
| Chain | Series of then calls | Then calls की श्रृंखला |
| Promise.all | Waits for all, fails fast | सब का इंतज़ार, एक fail पर fail |
| Unhandled rejection | Rejected promise with no catch | बिना catch वाला rejection |

---

## ⚡ 3-Line Summary
**English:**
1. Promise एक object है जो pending, fulfilled या rejected हो सकता है, और settle होने के बाद नहीं बदलता।
2. `then/catch/finally` chain बनाते हैं, और हर `then` अगला Promise लौटाता है।
3. `Promise.all` parallel के लिए, `allSettled` सब outcomes के लिए, और `race` पहले वाले के लिए इस्तेमाल होता है।

**Hindi:**
1. Promise एक object है जो pending, fulfilled या rejected हो सकता है, और settle होने के बाद नहीं बदलता।
2. `then/catch/finally` chain बनाते हैं, और हर `then` अगला Promise लौटाता है।
3. `Promise.all` parallel के लिए, `allSettled` सब outcomes के लिए, और `race` पहले वाले के लिए इस्तेमाल होता है।

---

## ➡️ Next Topic
**80. Promise States (pending, fulfilled, rejected)** — state transitions की बारीकियाँ, settle होने का नियम, और state कैसे परखें।
