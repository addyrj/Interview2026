# 174. Implement Promise.all
# हिंदी में: Promise.all लागू करना — कई async tasks को एक साथ चलाकर सबके नतीजे इकट्ठे करना

---

## 🔵 Simple Definition (English)
`Promise.all` takes a list of promises (or plain values), waits until all of them succeed, and resolves with an array of results in the same order as the input. If any one of them fails, the whole result rejects with that error.

## 🔵 सरल परिभाषा (Hindi)
`Promise.all` promises (या सामान्य values) की एक list लेता है, सबके सफल होने तक इंतज़ार करता है, और नतीजों की एक array लौटाता है जो input के उसी क्रम में हो। अगर उनमें से कोई एक भी fail हो, तो पूरा result उसी error के साथ reject हो जाता है।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `promiseAll(iterable)` that returns a promise. It resolves with an array of all values, in input order, once every item has resolved. It rejects with the first rejection reason. Plain values are treated as already-resolved promises. An empty input resolves with `[]`.

Often one screen needs data from several services. An order page needs the order, the payment status and the delivery ETA. If you await them one by one, the total time is the sum of all three. Running them together with `Promise.all` costs only as long as the slowest one.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `promiseAll(iterable)` लिखो जो एक promise लौटाए। हर item resolve होने पर यह input के क्रम में सभी values की array के साथ resolve हो। पहली rejection का error लेकर reject हो। सामान्य values को पहले से resolved promise माना जाए। खाली input पर `[]` के साथ resolve हो।

एक screen अक्सर कई services से data माँगती है। Order page को order, payment status और delivery ETA चाहिए। इन्हें एक-एक करके await करो तो कुल समय तीनों का जोड़ होगा। `Promise.all` से ये एक साथ चलते हैं, और समय सबसे धीमे call जितना लगता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Convert the input into an array, so every item can be indexed.
Step 2 → Create a result array with one slot per input item, and a counter of pending items.
Step 3 → Wrap each item with `Promise.resolve`, so plain values also work.
Step 4 → When an item resolves, store its value in the slot for its index (not in arrival order).
Step 5 → When the counter reaches zero, resolve the outer promise with the results.
Step 6 → If any item rejects, reject the outer promise. Later results are ignored because a promise settles only once.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Input को array में बदलो, ताकि हर item का index मिल सके।
Step 2 → Result array में input जितने slots बनाओ, और pending items का counter रखो।
Step 3 → हर item को `Promise.resolve` से लपेटो, ताकि सामान्य values भी काम करें।
Step 4 → जब item resolve हो, तो उसकी value उसके index वाले slot में रखो (आने के क्रम में नहीं)।
Step 5 → Counter शून्य पर पहुँचे तो बाहर वाला promise results के साथ resolve करो।
Step 6 → कोई item reject हो तो बाहर वाला promise reject करो। बाद के results अनदेखे रहते हैं, क्योंकि promise एक ही बार settle होता है।

---

## 🟡 Real World Example
Amazon's order detail page calls the product service, the pricing service, and the inventory service at the same time, then combines the results. Flipkart's home page loads banners, deals and recommendations together. Razorpay's dashboard loads settlements and refunds in parallel, then renders one summary. If the inventory call fails, the page shows an error for the whole section, because the data is incomplete.

Scenario: An order page needs `getOrder` (120 ms), `getPayment` (80 ms), and `getEta` (100 ms). Sequentially it takes about 300 ms. With `Promise.all` it takes about 120 ms.

## 🟡 Real Example Hindi mein
Amazon का order detail page product service, pricing service और inventory service को एक साथ बुलाता है, फिर नतीजे जोड़ता है। Flipkart का home page banners, deals और recommendations एक साथ लोड करता है। Razorpay का dashboard settlements और refunds को parallel लोड करके एक summary दिखाता है। अगर inventory call fail हो, तो पूरे section पर error दिखता है, क्योंकि data अधूरा है।

उदाहरण: Order page को `getOrder` (120 ms), `getPayment` (80 ms) और `getEta` (100 ms) चाहिए। एक-एक करके यह लगभग 300 ms लेता है। `Promise.all` से लगभग 120 ms।

---

## 💻 Code Example — Basic
```javascript
// Basic: Promise.all with a counter and a result array in input order
function promiseAllBasic(items) {
  return new Promise((resolve, reject) => {  // the outer promise we return
    if (items.length === 0) return resolve([]); // nothing to wait for: resolve with an empty array
    const results = new Array(items.length); // one slot per input item, kept in input order
    let done = 0;                            // how many items have resolved so far
    items.forEach((item, index) => {         // handle each item with its index
      Promise.resolve(item).then((value) => { // plain values and promises both work here
        results[index] = value;              // put the value in its own slot, not in arrival order
        done++;                              // one more item is finished
        if (done === items.length) resolve(results); // all finished: resolve with the results
      }, reject);                            // the first rejection rejects the whole batch
    });
  });
}

// Sample: three "services" that answer after different delays
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
promiseAllBasic([delay(30, "A"), 2, delay(10, "C")])
  .then((r) => console.log(JSON.stringify(r)));  // Expected output: ["A",2,"C"]  (input order, not finish order)

// Edge case: empty input resolves at once, so this line prints before the sample above
promiseAllBasic([]).then((r) => console.log(r.length)); // Expected output (first): 0
```

## 💻 Code Example — Advanced
```javascript
// Advanced: accepts any iterable, validates input, and matches the built-in Promise.all behavior
function promiseAll(iterable) {
  // Convert any iterable (array, Set, generator) into an array so we can index it
  const items = Array.from(iterable);        // a plain array of the inputs
  return new Promise((resolve, reject) => {  // one outer promise for the whole batch
    const results = new Array(items.length); // result slots in input order
    let remaining = items.length;            // how many items are still pending
    if (remaining === 0) return resolve(results); // empty input resolves with []

    items.forEach((item, i) => {             // subscribe to every item
      Promise.resolve(item)                  // non-promise values become resolved promises
        .then((value) => {                   // this item succeeded
          results[i] = value;                // keep its value at its index
          remaining -= 1;                    // one less pending item
          if (remaining === 0) resolve(results); // the last one resolves the batch
        })
        .catch(reject);                      // the first failure rejects the batch; later ones are ignored
    });
  });
}

// Test helpers
const slow = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
const failing = (ms, message) => new Promise((_, reject) => setTimeout(() => reject(new Error(message)), ms));

(async () => {
  // Test 1: a Set is an iterable, and the order follows the Set's insertion order
  console.log(JSON.stringify(await promiseAll(new Set([slow(15, "x"), "y"])))); // Expected output: ["x","y"]

  // Test 2: empty input
  console.log((await promiseAll([])).length);                                  // Expected output: 0

  // Test 3: one failure rejects the whole batch with that error
  try {
    await promiseAll([slow(50, "ok"), failing(20, "payment down")]);
  } catch (err) {
    console.log("caught:", err.message);                                       // Expected output: caught: payment down
  }

  // Test 4: same result as the built-in Promise.all
  const mine = await promiseAll([1, slow(5, 2)]);
  const builtIn = await Promise.all([1, slow(5, 2)]);
  console.log(JSON.stringify(mine) === JSON.stringify(builtIn));                // Expected output: true
})();

// Time:  O(n) to subscribe to n items; the total wait is the slowest item (not the sum)
// Space: O(n) for the result array and the pending-count state
```

### Edge Cases
- An empty array or empty Set resolves at once with `[]`.
- Plain values (numbers, strings, `null`) are allowed and resolve immediately.
- If two items reject, only the first rejection is used, because the outer promise settles once.
- Results keep input order even when the slowest item was first in the list.
- A rejected item that is not subscribed to would be an unhandled rejection, which is why every item gets a `.catch` path.

---

## 🟠 Express.js Integration
An order summary endpoint loads three services at the same time. If one service fails, the route returns a clear error with HTTP 502, which means that an upstream service is bad.

```javascript
// Express.js: aggregate three services in parallel for one summary endpoint
const express = require("express");          // web framework
const app = express();                       // create the app

// Pretend service calls (in real life these are HTTP or database calls)
const getOrder = (id) => new Promise((r) => setTimeout(() => r({ id, total: 540 }), 120));
const getPayment = (id) => new Promise((r) => setTimeout(() => r({ id, status: "PAID" }), 80));
const getEta = (id) => new Promise((r) => setTimeout(() => r({ id, minutes: 35 }), 100));

// GET /api/orders/:id/summary
app.get("/api/orders/:id/summary", async (req, res) => {
  const { id } = req.params;                 // the order id from the URL
  try {
    // Start all three calls together; the total time is the slowest one (about 120 ms)
    const [order, payment, eta] = await Promise.all([getOrder(id), getPayment(id), getEta(id)]);
    res.json({ order, payment, eta });       // 200 OK with the combined summary
  } catch (err) {
    // One upstream service failed: report it as a bad gateway (502), not as our own bug
    res.status(502).json({ error: "upstream service failed", detail: err.message });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Order summary API running"); // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `await` inside a loop when the calls are independent
✅ Correct: start all the promises first, then wait for them together. A sequential loop waits for each call before starting the next.

```javascript
// Wrong: each call waits for the previous one, so the total time is the sum
const slowFetch = (v) => new Promise((r) => setTimeout(() => r(v), 50));
(async () => {
  const start = Date.now();
  const out = [];
  for (const v of [1, 2, 3]) out.push(await slowFetch(v)); // about 150 ms in total
  console.log(out.join(","), Date.now() - start >= 140);      // Expected output: 1,2,3 true
})();

// Right: start all three first, then wait; the total is about 50 ms
(async () => {
  const start = Date.now();
  const out = await Promise.all([1, 2, 3].map(slowFetch));   // all three run at the same time
  console.log(out.join(","), Date.now() - start < 140);      // Expected output: 1,2,3 true
})();
```

❌ **Mistake 2:** Pushing results in arrival order instead of using the index
✅ Correct: the slowest item may finish first. Store each result at its own index so the order matches the input.

```javascript
const slowFetchMs = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms)); // resolves with v after ms

// Wrong: results are pushed as they arrive, so the order depends on timing
const arrived = [];                          // filled in finish order
const tasks = [slowFetchMs(30, "30ms"), slowFetchMs(10, "10ms")]; // first takes 30 ms, second 10 ms
tasks.forEach((p) => p.then((v) => arrived.push(v))); // push when each one finishes
setTimeout(() => console.log("arrival order:", arrived.join(",")), 50); // Expected output (at 50 ms): arrival order: 10ms,30ms

// Right: Promise.all keeps the input order, whatever the finish order was
(async () => {
  const values = await Promise.all(tasks);  // results come back in input order
  console.log("input order:", values.join(",")); // Expected output (at 30 ms): input order: 30ms,10ms
})();
```

---

## 🧠 Tricky Interview Question
```javascript
const p1 = Promise.resolve("first");
const p2 = new Promise((_, reject) => reject(new Error("boom")));
const p3 = new Promise((resolve) => setTimeout(() => resolve("late"), 10));

Promise.all([p1, p2, p3])
  .then((v) => console.log("resolved", v))
  .catch((e) => console.log("rejected", e.message));

Promise.all([p1, p3]).then((v) => console.log("second", v));
```
Answer:
```
rejected boom     ← p2 rejects right away, so the first Promise.all rejects with "boom"
second [ 'first', 'late' ]  ← the second batch has no failing item, so it waits 10 ms and resolves
```
The rejection of `p3` in the first batch never matters, since `p3` resolves. The trap is that a failed item rejects the whole batch right away, even if other items are still pending. Use `Promise.allSettled` when you need every outcome.

---

## ⚫ Interview Questions + Answers

**Q1: What does `Promise.all` return when the input is empty?**
A1: A promise that resolves with an empty array right away.

**Q2: Why must the result be stored by index?**
A2: Promises finish in any order. Storing each result at its input index keeps the output in the same order as the input.

**Q3: How is `Promise.all` different from `Promise.allSettled`?**
A3: `Promise.all` rejects on the first failure. `Promise.allSettled` waits for every item and returns an object for each one with `status` as `fulfilled` or `rejected`.

**Q4: Why wrap items with `Promise.resolve`?**
A4: It turns plain values and thenables into promises, so one code path handles both. Without it, a plain value has no `.then` method.

**Q5: What is the time complexity?**
A5: O(n) to subscribe to n items and collect n results. The total waiting time is the slowest item, not the sum of all items, because they run at the same time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several independent async calls are needed for one response
- All results are required, and one failure makes the whole result useless
- You want the total time to be the slowest call, not the sum

❌ Avoid when:
- Items depend on each other; then they must run in sequence
- You need every outcome even when some fail; use `Promise.allSettled`
- You start thousands of calls at once; limit concurrency to avoid overloading the service

---

## 📊 Visual Diagram
```
Input:   [ getOrder(120ms), getPayment(80ms), getEta(100ms) ]

Time ->  0ms        80ms       100ms      120ms
         |-- start all three at 0 ms ----------|
         getPayment ............ done (slot 1)
         getEta .................... done (slot 2)
         getOrder ............................. done (slot 0)
                                                 |
                                                 v
                              resolve([order, payment, eta])   <- input order
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Promise | An object for a value that arrives later | बाद में आने वाली value का object |
| Fulfilled | The promise succeeded | Promise सफल हुआ |
| Rejected | The promise failed | Promise fail हुआ |
| Iterable | Anything you can loop over, such as an array or Set | Loop किया जा सकने वाला collection |
| Concurrency | Several tasks in progress at the same time | एक साथ कई tasks चलना |
| allSettled | Waits for all, reports each outcome | सबका इंतज़ार, हर नतीजा अलग से |

---

## ⚡ 3-Line Summary
English:
1. `Promise.all` runs independent promises together and resolves with their results in input order.
2. Store each result by its index, and reject the whole batch on the first failure.
3. The total time is the slowest task, so avoid `await` in a loop for independent calls.

Hindi:
1. `Promise.all` स्वतंत्र promises को एक साथ चलाता है और उनके नतीजे input के क्रम में लौटाता है।
2. हर नतीजा उसके index पर रखो, और पहली failure पर पूरे batch को reject करो।
3. कुल समय सबसे धीमे task जितना होता है, इसलिए स्वतंत्र calls के लिए loop में `await` मत लगाओ।

---

## ➡️ Next Topic
**175. Implement Promise.race** — `Promise.all` waits for everyone; the next problem resolves as soon as the first promise settles, which is useful for timeouts.
