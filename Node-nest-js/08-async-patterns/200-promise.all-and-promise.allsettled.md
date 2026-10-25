# 200. Promise.all + Promise.allSettled
# हिंदी में: Promise.all + Promise.allSettled

---

## 🔵 Simple Definition (English)
**`Promise.all(promises)`** runs multiple promises in parallel and resolves with an array of ALL their results — but it rejects IMMEDIATELY if even one promise rejects ("fail fast"). **`Promise.allSettled(promises)`** also runs them in parallel, but ALWAYS resolves (never rejects) with an array of `{status, value}` or `{status, reason}` objects describing every promise's outcome, success or failure.

## 🔵 सरल परिभाषा (Hindi)
**`Promise.all(promises)`** कई promises को parallel में चलाता है और सबके results का array resolve करता है — लेकिन एक भी promise reject हो तो तुरंत reject हो जाता है ("fail fast")। **`Promise.allSettled(promises)`** भी parallel चलाता है, लेकिन हमेशा resolve होता है (कभी reject नहीं) — हर promise के outcome (success/failure) का array देता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Need to run multiple independent async operations and wait for all of them
  Doing them one by one with sequential awaits wastes time (serializes
  work that could've happened concurrently)
  Sometimes you need ALL to succeed to proceed (Promise.all)
  Sometimes you need results from EVERY one regardless of individual failures
  (Promise.allSettled) — e.g., sending notifications to 5 services where
  one failing shouldn't stop you from knowing which 4 succeeded
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: कई independent async operations को एक साथ चलाना और wait करना चाहिए
एक-एक करके await करना time waste करता है
कभी सबको succeed होना चाहिए (Promise.all)
कभी हर एक का result चाहिए चाहे कोई fail हो (Promise.allSettled)
```

---

## 🟢 How it Works — Step by Step

Step 1 → `Promise.all([p1, p2, p3])` starts ALL promises immediately (they were likely already started by calling the functions) and waits for all to settle
Step 2 → If ALL resolve, it resolves with an array `[result1, result2, result3]` in the SAME ORDER as the input (not completion order)
Step 3 → If ANY rejects, `Promise.all` immediately rejects with THAT rejection reason — the other promises keep running in the background but their results are discarded by `Promise.all` itself
Step 4 → `Promise.allSettled([p1, p2, p3])` ALSO waits for all to settle, but regardless of outcome, resolves with `[{status:'fulfilled', value}, {status:'rejected', reason}, ...]`
Step 5 → Use `Promise.all` when you need everything to succeed to proceed; use `Promise.allSettled` when partial success is acceptable and you need to know what succeeded/failed individually

## 🟢 कैसे काम करता है? (Hindi)
```
1. Promise.all([p1,p2,p3]) सबको parallel चलाता है
2. सब resolve हों तो results का array मिलता है, input order में
3. कोई एक reject हो तो तुरंत पूरा Promise.all reject हो जाता है
4. Promise.allSettled हमेशा resolve होता है — हर एक का status+value/reason
5. सबको succeed होना चाहिए तो Promise.all, partial चलेगा तो Promise.allSettled
```

---

## 🟡 Real World Example
**Flipkart product page load:** Loading a product page needs data from several independent microservices in parallel: price service, reviews service, inventory service, recommendations service. Flipkart uses `Promise.allSettled` here — if the "recommendations" service is down, the page should STILL render with price/reviews/inventory (critical data), just without recommendations (non-critical). Using `Promise.all` instead would be wrong — one failing non-critical service would block the ENTIRE page from loading, which is a worse user experience than showing a page missing one widget.

## 🟡 Real Example Hindi mein
**Flipkart product page:** Price, reviews, inventory, recommendations — सब independent services से parallel में data चाहिए। `Promise.allSettled` use होता है — recommendations service down हो तो भी page load हो जाए बाकी data के साथ। `Promise.all` गलत होगा यहाँ — एक non-critical service fail होने पर पूरा page block हो जाएगा।

---

## 💻 Code Example — Basic

```javascript
// basic-promise-all.js
// Run: node basic-promise-all.js

function fetchPrice() {
  return new Promise((resolve) => setTimeout(() => resolve(999), 100));
}
function fetchReviews() {
  return new Promise((resolve) => setTimeout(() => resolve(['Great!', 'Good']), 150));
}
function fetchInventory() {
  return new Promise((resolve) => setTimeout(() => resolve({ inStock: true }), 80));
}

async function loadProductPage() {
  console.time('load');
  // All 3 calls start IMMEDIATELY and run concurrently — total time ≈ max(100,150,80) = 150ms,
  // NOT 100+150+80 = 330ms (which sequential awaits would cost)
  const [price, reviews, inventory] = await Promise.all([
    fetchPrice(),
    fetchReviews(),
    fetchInventory(),
  ]);
  console.timeEnd('load');  // ~150ms
  console.log({ price, reviews, inventory });
}

loadProductPage();
```

## 💻 Code Example — Advanced

```javascript
// advanced-allSettled.js
// Production pattern: notify multiple channels, tolerate partial failure, report results

function notifySlack(message) {
  return new Promise((resolve, reject) =>
    setTimeout(() => resolve({ channel: 'slack', message }), 50)
  );
}
function notifyEmail(message) {
  return new Promise((resolve, reject) =>
    setTimeout(() => reject(new Error('SMTP server down')), 50)  // simulate a failure
  );
}
function notifySms(message) {
  return new Promise((resolve, reject) =>
    setTimeout(() => resolve({ channel: 'sms', message }), 50)
  );
}

async function notifyAllChannels(message) {
  // allSettled never rejects — we always get a full report of what happened
  const results = await Promise.allSettled([
    notifySlack(message),
    notifyEmail(message),
    notifySms(message),
  ]);

  const succeeded = [];
  const failed = [];

  results.forEach((result, index) => {
    const channelNames = ['slack', 'email', 'sms'];
    if (result.status === 'fulfilled') {
      succeeded.push(channelNames[index]);
    } else {
      // result.reason holds the rejection error for failed promises
      failed.push({ channel: channelNames[index], error: result.reason.message });
    }
  });

  console.log('Succeeded:', succeeded);  // ['slack', 'sms']
  console.log('Failed:', failed);        // [{ channel: 'email', error: 'SMTP server down' }]
  return { succeeded, failed };
}

notifyAllChannels('Order #123 shipped!');

// Contrast: using Promise.all here would REJECT the entire operation
// just because email failed, even though slack and sms succeeded fine.
async function notifyAllOrNothing(message) {
  try {
    await Promise.all([notifySlack(message), notifyEmail(message), notifySms(message)]);
    console.log('All channels notified');
  } catch (err) {
    // We lose visibility into WHICH ones succeeded — Promise.all discards that info
    console.error('At least one channel failed:', err.message);
  }
}
notifyAllOrNothing('Order #124 shipped!');
```

---

## 🟠 Express.js Integration

```javascript
// Express route aggregating data from multiple "services" (simulated here)
const express = require('express');
const app = express();

function getPricing(id) {
  return new Promise((resolve) => setTimeout(() => resolve({ price: 499 }), 100));
}
function getRecommendations(id) {
  // Simulate an UNRELIABLE non-critical service that sometimes fails
  return new Promise((resolve, reject) => setTimeout(() => reject(new Error('timeout')), 100));
}
function getReviews(id) {
  return new Promise((resolve) => setTimeout(() => resolve({ avgRating: 4.5 }), 100));
}

app.get('/api/products/:id', async (req, res) => {
  const results = await Promise.allSettled([
    getPricing(req.params.id),
    getRecommendations(req.params.id),
    getReviews(req.params.id),
  ]);

  const [pricing, recommendations, reviews] = results.map((r) =>
    r.status === 'fulfilled' ? r.value : null  // gracefully degrade failed sections to null
  );

  // Page still renders with partial data instead of a hard 500 error
  res.json({
    productId: req.params.id,
    pricing,
    recommendations,  // null if that service failed — frontend just hides this widget
    reviews,
  });
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `Promise.all` when partial success should be acceptable (one failing non-critical service shouldn't block the whole response).
✅ Correct: Use `Promise.allSettled` and handle each result's status individually when failures are tolerable.

```javascript
// Wrong — one failed non-critical call kills the entire page load
const [price, recs, reviews] = await Promise.all([getPrice(), getRecs(), getReviews()]);

// Right — degrade gracefully
const results = await Promise.allSettled([getPrice(), getRecs(), getReviews()]);
```

❌ Mistake 2: Creating the promises SEQUENTIALLY before passing to `Promise.all`, accidentally serializing work anyway.
✅ Correct: Call all the async functions in the SAME array expression so they all start immediately, concurrently.

```javascript
// Wrong — fnA() is awaited BEFORE fnB() is even called, serializing them
const a = await fnA();
const b = await fnB();
const results = [a, b];

// Right — both start together
const results = await Promise.all([fnA(), fnB()]);
```

❌ Mistake 3: Forgetting that `Promise.all` discards in-flight results of OTHER promises when one rejects — you lose visibility into which ones actually would have succeeded.
✅ Correct: If you need that visibility even on failure, use `Promise.allSettled` instead and inspect each result.

---

## 🧠 Tricky Interview Question

```javascript
const p1 = new Promise((res) => setTimeout(() => res('A'), 100));
const p2 = new Promise((_, rej) => setTimeout(() => rej('B failed'), 50));
const p3 = new Promise((res) => setTimeout(() => res('C'), 200));

Promise.all([p1, p2, p3])
  .then((results) => console.log('all:', results))
  .catch((err) => console.log('caught:', err));

// Does p3's setTimeout callback still fire even though Promise.all already rejected?
```
Answer: **Yes — `p3`'s `setTimeout` still fires after 200ms and resolves `p3` internally, even though `Promise.all` already rejected at the 50ms mark with `"caught: B failed"`.** `Promise.all` rejecting does NOT cancel or stop the other promises' underlying work — JavaScript has no built-in mechanism to "cancel" a Promise. `p1` and `p3` continue running to completion regardless; `Promise.all` simply ignores their eventual results because it already settled (rejected) at `p2`'s failure point. This is a key gotcha: `Promise.all` failing fast does NOT mean the other operations stop — if they have side effects (like an API call or DB write), those side effects still happen even though you've "moved on" from that `Promise.all` call.

---

## ⚫ Interview Questions + Answers

Q1: What's the key behavioral difference between `Promise.all` and `Promise.allSettled`?
A1: `Promise.all` rejects as soon as ANY input promise rejects, discarding visibility into the others (fail-fast). `Promise.allSettled` ALWAYS resolves once every promise has settled, giving you a full array of per-promise outcomes (`fulfilled` with `value`, or `rejected` with `reason`) — it never itself rejects.

Q2: Does `Promise.all` preserve the order of results?
A2: Yes — the resulting array's order matches the INPUT array's order, not the order in which the promises actually resolved. So `Promise.all([slowOne, fastOne])` gives `[slowOneResult, fastOneResult]` even if `fastOne` finishes first internally.

Q3: If one promise in `Promise.all` rejects, do the others stop running?
A3: No. JavaScript promises cannot be cancelled once started. The other promises continue their underlying async work to completion (and any side effects they cause, like API calls, still happen) — `Promise.all` simply stops waiting for them and settles immediately with the rejection, ignoring their eventual results.

Q4: When would you choose `Promise.race` over `Promise.all`/`allSettled`?
A4: `Promise.race` settles as soon as the FIRST promise settles (whether fulfilled or rejected) — useful for implementing timeouts (`Promise.race([actualOperation(), timeoutPromise(5000)])`) or "fastest wins" scenarios like querying multiple redundant servers and using whichever responds first.

Q5: How do you implement a global timeout for an async operation using these Promise combinators?
A5: Create a promise that rejects after N milliseconds via `setTimeout`, then race it against the real operation: `const result = await Promise.race([realOperation(), new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))])`. If `realOperation` doesn't settle within 5 seconds, the timeout promise wins the race and the overall `await` throws a timeout error.

---

## 🔷 When to Use + When Not to Use
✅ Use `Promise.all` when:
- All operations MUST succeed for the overall result to be meaningful (e.g., all steps of a financial transaction)

✅ Use `Promise.allSettled` when:
- Partial success is acceptable and you need to know exactly what succeeded/failed (e.g., multi-channel notifications, aggregating optional widgets on a page)

❌ Avoid Promise.all when:
- One non-critical failure shouldn't block the whole result — use allSettled instead

❌ Avoid both when:
- Operations are sequential/dependent on each other's results — use plain sequential `await`

---

## 📊 Visual Diagram
```
PROMISE.ALL vs PROMISE.ALLSETTLED
──────────────────────────────────────────
Inputs:  p1 ✅   p2 ❌   p3 ✅

Promise.all([p1,p2,p3])
  → rejects immediately when p2 fails
  → .catch(err) gets p2's rejection reason only
  → p1, p3 results DISCARDED (but their side effects still happened)

Promise.allSettled([p1,p2,p3])
  → always resolves, waits for ALL to settle
  → [
      {status:'fulfilled', value: <p1 result>},
      {status:'rejected',  reason: <p2 error>},
      {status:'fulfilled', value: <p3 result>}
    ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fail-fast | Rejects on first failure | पहली failure पर reject हो जाना |
| Settled | Resolved or rejected (final state) | Resolve या reject हो जाना (final state) |
| Graceful degradation | Partial success still usable | Partial success भी काम आना |
| Promise.race | Settles on first settled promise | पहले settle हुए promise पर settle |
| Timeout pattern | Racing operation vs timer | Operation vs timer की race |

---

## ⚡ 3-Line Summary
English:
1. `Promise.all` runs promises in parallel and rejects fast on any single failure, discarding visibility into others.
2. `Promise.allSettled` always resolves with a full per-promise status report, ideal for tolerable partial failures.
3. Neither combinator can cancel in-flight promises — rejected/discarded promises still run their side effects to completion.

Hindi:
1. `Promise.all` parallel चलाता है, एक fail होने पर तुरंत reject हो जाता है।
2. `Promise.allSettled` हमेशा हर promise का status report देता है, partial failure के लिए अच्छा है।
3. कोई भी promise को cancel नहीं कर सकता — discarded promises भी अपना side effect पूरा करते हैं।

---

## ➡️ Next Topic
**201. Async Iterators in Node** — Iterating over asynchronous data sources (streams, paginated APIs) with `for await...of`.
