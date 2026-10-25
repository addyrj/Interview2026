# 82. Promise Methods (all, allSettled, race, any)
# हिंदी में: Promise Methods — Many Promises को एक साथ संभालना (all, allSettled, race, any)

---

## 🔵 Simple Definition (English)
`Promise.all`, `Promise.allSettled`, `Promise.race`, and `Promise.any` take an array (iterable) of promises and combine them into one promise. Each one differs in when it settles and whether a single failure makes the whole result fail.

## 🔵 सरल परिभाषा (Hindi)
`Promise.all`, `Promise.allSettled`, `Promise.race`, और `Promise.any` promises के array को लेते हैं और उन्हें एक promise में जोड़ देते हैं। हर एक का फर्क इस बात में है कि वह कब settle होता है और क्या एक भी failure पूरे result को fail कर देता है।

---

## 🔴 Problem it Solves
Often you need several async calls at once: restaurant details, menu, and offers for one screen. Awaiting them one by one wastes time, because each waits for the previous. But starting them all at once raises new questions: What if one fails? Do you want the first answer or all answers? Do you want a result even when some calls fail? The four combinators give a clear answer to each question.

## 🔴 यह क्यों बना? (Hindi)
अक्सर एक screen के लिए कई async calls एक साथ चाहिए होती हैं, जैसे restaurant details, menu और offers। एक-एक करके await करने से समय बर्बाद होता है, क्योंकि हर call पिछले का इंतज़ार करती है। लेकिन सब एक साथ शुरू करने पर नए सवाल आते हैं: अगर एक fail हो जाए तो? सिर्फ पहला जवाब चाहिए या सारे? कुछ fail होने पर भी result चाहिए? चारों combinators इन सवालों के अलग-अलग जवाब देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → All the promises start running at the same time (they are created in parallel)
Step 2 → `Promise.all` waits for ALL to fulfill; resolves with an array in INPUT order; rejects on the FIRST rejection
Step 3 → `Promise.allSettled` waits for ALL to settle (fulfill or reject); never rejects; gives `{status, value}` or `{status, reason}`
Step 4 → `Promise.race` settles with the FIRST promise to settle (fulfill OR reject)
Step 5 → `Promise.any` resolves with the FIRST promise to FULFILL; rejects with `AggregateError` only if ALL reject
Step 6 → An empty array: `all` and `allSettled` resolve with `[]`, `any` rejects, and `race` stays pending forever

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → सारे promises एक साथ शुरू हो जाते हैं
Step 2 → `Promise.all` सबके fulfill होने का इंतज़ार करता है; INPUT के क्रम में array देता है; पहली rejection पर reject हो जाता है
Step 3 → `Promise.allSettled` सबके settle होने (fulfill या reject) का इंतज़ार करता है; कभी reject नहीं होता; `{status, value}` या `{status, reason}` देता है
Step 4 → `Promise.race` सबसे पहले settle होने वाले promise के नतीजे पर settle होता है (fulfill हो या reject)
Step 5 → `Promise.any` सबसे पहले FULFILL होने वाले promise की value देता है; सब reject हों तो `AggregateError` के साथ reject होता है
Step 6 → खाली array: `all` और `allSettled` `[]` के साथ resolve होते हैं, `any` reject होता है, और `race` हमेशा pending रहता है

---

## 🟡 Real World Example
A Swiggy restaurant page needs three things: restaurant info, menu, and offers. The menu is the most important part, and offers are nice-to-have. So you want:
- `Promise.all` for restaurant + menu (if either fails, the page cannot show anything useful)
- `Promise.allSettled` for restaurant + menu + offers (show the page even if offers API is down)
- `Promise.race` for a timeout-like fast answer from one of two CDN mirrors
- `Promise.any` for the same data from several mirrors, using the first one that works

## 🟡 Real Example Hindi mein
मान लो Swiggy पर restaurant का page खुलता है। उसे तीन चीज़ें चाहिए: restaurant info, menu और offers। Menu ज़रूरी है, offers अच्छा-होने-वाला डेटा है। तो restaurant + menu के लिए `Promise.all` चाहिए (कोई एक fail हो तो page का कोई फायदा नहीं)। Offers API बंद हो तब भी page दिखाने के लिए `Promise.allSettled`। दो CDN mirrors में से सबसे तेज़ जवाब के लिए `Promise.race`। और किसी भी एक working mirror से data के लिए `Promise.any`।

---

## 💻 Code Example — Basic
```javascript
// Helper: resolves with `value` after `ms`. If `fail` is true, rejects instead.
const delay = (ms, value, fail = false) =>
  new Promise((resolve, reject) =>
    setTimeout(() => (fail ? reject(new Error(`${value} failed`)) : resolve(value)), ms)
  );

// Fake API calls for a restaurant page
const getRestaurant = () => delay(100, "Biryani House");       // succeeds after 100ms
const getMenu = () => delay(50, ["Chicken Biryani", "Raita"]); // succeeds after 50ms
const getOffers = () => delay(150, "20% off", true);           // fails after 150ms

// Wrap everything in an async function so we can run the examples in order
(async () => {
  // 1. Promise.all: all succeed, we get an array in INPUT order
  const [restaurant, menu] = await Promise.all([getRestaurant(), getMenu()]);
  console.log("1. all ok:", restaurant, menu);       // both values

  // 2. Promise.all: one fails, the whole thing rejects
  try {
    await Promise.all([getRestaurant(), getOffers()]); // offers fails at 150ms
  } catch (err) {
    console.log("2. all failed:", err.message);       // "20% off failed"
  }

  // 3. Promise.allSettled: never rejects, reports every outcome
  const results = await Promise.allSettled([getRestaurant(), getOffers()]);
  results.forEach((r) => {                             // check each outcome
    console.log("3.", r.status, r.value ?? r.reason.message); // value if fulfilled, else error text
  });

  // 4. Promise.race: first to SETTLE wins (here the faster one)
  const winner = await Promise.race([delay(200, "slow CDN"), delay(80, "fast CDN")]);
  console.log("4. race winner:", winner);            // "fast CDN"

  // 5. Promise.any: first to FULFILL wins, rejections are ignored
  const mirror = await Promise.any([delay(60, "mirror A", true), delay(120, "mirror B")]);
  console.log("5. any winner:", mirror);             // "mirror B" (A failed)
})();
```

**Expected output (basic):**
```
1. all ok: Biryani House [ 'Chicken Biryani', 'Raita' ]
2. all failed: 20% off failed
3. fulfilled Biryani House
3. rejected 20% off failed
4. race winner: fast CDN
5. any winner: mirror B
```

## 💻 Code Example — Advanced
```javascript
// Advanced: timeout wrapper, a settled-results summary, and a concurrency limiter.

// Helper: resolves with value after ms; rejects if fail is true
const delay = (ms, value, fail = false) =>
  new Promise((resolve, reject) =>
    setTimeout(() => (fail ? reject(new Error(`${value} failed`)) : resolve(value)), ms)
  );

// 1. Timeout wrapper: reject if the promise takes longer than `ms`
function withTimeout(promise, ms, label) {
  let timer;                                        // holds the timer id so we can clear it
  const timeout = new Promise((_, reject) => {      // this promise only rejects, after ms
    timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms}ms`)), ms);
  });
  // whichever settles first wins; always clear the timer to avoid leaks
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

// 2. Summarize many tasks: never throws, returns which labels succeeded and which failed
async function summarize(tasks) {                   // tasks: [ [label, promise], ... ]
  const labels = tasks.map(([label]) => label);     // keep labels in input order
  const settled = await Promise.allSettled(tasks.map(([, p]) => p)); // wait for all
  const ok = [];                                    // successful labels
  const failed = [];                                // "label: reason" strings
  settled.forEach((r, i) => {                       // go through each outcome
    if (r.status === "fulfilled") ok.push(labels[i]);                    // success
    else failed.push(`${labels[i]}: ${r.reason.message}`);              // failure
  });
  return { ok, failed };                            // plain object summary
}

// 3. Concurrency limiter: run fn over items, at most `limit` at a time (worker pool)
async function mapWithLimit(items, limit, fn) {
  const results = new Array(items.length);          // results keep the original order
  let next = 0;                                     // index of the next item to start
  async function worker() {                         // each worker pulls items until none remain
    while (next < items.length) {                   // more work left?
      const i = next++;                             // claim an index (safe: JS is single-threaded)
      results[i] = await fn(items[i]);              // do the work and store its result
    }
  }
  const workers = Array.from({ length: limit }, () => worker()); // start `limit` workers
  await Promise.all(workers);                       // wait until every worker is done
  return results;                                   // results in original order
}

// Demo: run all three helpers in order
(async () => {
  // Timeout: slow call takes 500ms but we only wait 100ms
  try {
    await withTimeout(delay(500, "slow menu"), 100, "menu API");
  } catch (err) {
    console.log("1.", err.message);                  // "menu API timed out after 100ms"
  }

  // Summary: two succeed, one fails
  const summary = await summarize([
    ["restaurant", delay(50, "ok")],                // succeeds
    ["offers", delay(30, "x", true)],               // fails
    ["menu", delay(10, "ok")],                      // succeeds
  ]);
  console.log("2.", JSON.stringify(summary));       // {"ok":["restaurant","menu"],"failed":["offers: x failed"]}

  // Limiter: squares of 3, 1, 2 with at most 2 running at once; each task waits x*10 ms
  const squares = await mapWithLimit([3, 1, 2], 2, async (x) => {
    await delay(x * 10, null);                      // simulate work of x*10 ms
    return x * x;                                   // the result for this item
  });
  console.log("3.", squares);                        // [ 9, 1, 4 ] (original order kept)
})();
```

**Expected output (advanced):**
```
1. menu API timed out after 100ms
2. {"ok":["restaurant","menu"],"failed":["offers: x failed"]}
3. [ 9, 1, 4 ]
```

---

## 🟠 Express.js Integration
A product or restaurant detail endpoint often calls several services. `Promise.all` is right when every piece is required. `Promise.allSettled` is right when the response can be partial. Below, the menu is required but offers are optional.

```javascript
// Express.js example: parallel calls with partial failure allowed
const express = require("express");                 // import Express
const app = express();                              // create the app

// Fake services (in a real app: DB or HTTP calls)
const getRestaurant = (id) => Promise.resolve({ id, name: "Biryani House" });
const getMenu = (id) => Promise.resolve(["Chicken Biryani", "Raita"]);
const getOffers = (id) => Promise.reject(new Error("offers service down"));

app.get("/restaurants/:id", async (req, res, next) => { // async handler
  try {
    const id = req.params.id;                       // read the id from the URL
    // Run all three calls at the same time
    const [restaurant, menu, offers] = await Promise.allSettled([
      getRestaurant(id), getMenu(id), getOffers(id),
    ]);
    if (restaurant.status === "rejected" || menu.status === "rejected") {
      return res.status(502).json({ error: "core data unavailable" }); // required data missing
    }
    res.json({                                      // send the page data
      ...restaurant.value,                          // restaurant info
      menu: menu.value,                             // menu (required)
      offers: offers.status === "fulfilled" ? offers.value : [], // optional, default empty
    });
  } catch (err) {
    next(err);                                      // unexpected error -> error middleware
  }
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `Promise.all` when you actually want all outcomes (one failure throws away the rest)
✅ **Correct:** Use `Promise.allSettled` when partial results are fine.

```javascript
// Wrong: offers failure makes the whole page fail
const [r, m, o] = await Promise.all([getRestaurant(), getMenu(), getOffers()]);

// Right: restaurant and menu still render even if offers fails
const [r2, m2, o2] = await Promise.allSettled([getRestaurant(), getMenu(), getOffers()]);
```

❌ **Mistake 2:** Using `await` inside a loop when the calls are independent (runs one by one)
✅ **Correct:** Create all promises first, then await them together.

```javascript
// Wrong: total time = sum of all calls (slow)
for (const id of ids) {
  results.push(await getRestaurant(id));     // waits for each call before starting the next
}

// Right: total time = slowest call (fast)
const results2 = await Promise.all(ids.map((id) => getRestaurant(id)));
```

❌ **Mistake 3:** Expecting `Promise.race` to return the "successful" result
✅ **Correct:** `race` returns the first to SETTLE, and that can be a rejection. Use `any` if you want the first success.

```javascript
// Wrong: if the fast mirror fails, race rejects even though the slow mirror would work
const data = await Promise.race([mirrorA(), mirrorB()]);

// Right: any waits for the first fulfilled promise
const data2 = await Promise.any([mirrorA(), mirrorB()]);
```

---

## 🧠 Tricky Interview Output Question
```javascript
// Edge cases with empty arrays
const a = Promise.all([]);           // empty input: resolves right away with []
const b = Promise.race([]);          // empty input: NEVER settles (pending forever)
const c = Promise.any([]);           // empty input: rejects with AggregateError (no fulfilled)

a.then((v) => console.log("a:", v));                    // a: []
c.catch((e) => console.log("c:", e.constructor.name, e.errors.length)); // c: AggregateError 0
b.then(() => console.log("b fulfilled"), () => console.log("b rejected")); // never prints

console.log("sync");                                     // runs first, before any callback
```
**Answer:**
```
sync
a: []
c: AggregateError 0
```
**Why:** `console.log("sync")` is synchronous, so it prints first. `Promise.all([])` and `Promise.any([])` settle immediately when they are created (`all` fulfills with `[]`, `any` rejects with an `AggregateError` whose `errors` array is empty). Their `.then` and `.catch` callbacks are queued as microtasks in the order they were attached, so `a:` prints before `c:`. `Promise.race([])` has no promise to settle from, so it stays pending forever and its callbacks never run. Node exits because nothing keeps the event loop alive.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `Promise.all` and `Promise.allSettled`?
A1: `all` fails fast: it rejects on the first rejection and discards other results. `allSettled` waits for every promise and always fulfills with an array of `{status, value}` or `{status, reason}` objects, so you can see every outcome.

Q2: Does `Promise.all` keep the order of results?
A2: Yes. The result array is in the same order as the input array, not the order in which the promises finished. That is why destructuring `const [a, b] = await Promise.all([...])` is safe.

Q3: How is `Promise.race` different from `Promise.any`?
A3: `race` settles with the first promise to settle, whether it fulfills or rejects. `any` ignores rejections and settles with the first promise to fulfill. `any` only rejects if every promise rejects, and then it throws an `AggregateError`.

Q4: When would you use `Promise.race` in real code?
A4: Mainly for timeouts: race the real request against a timer that rejects. The first one to settle wins. This is the standard `withTimeout` pattern.

Q5: What happens to the other promises after `Promise.race` or `Promise.all` has already settled?
A5: They are not cancelled. Each promise keeps running to completion. A rejected one that nobody handles can cause an unhandled rejection, so `allSettled` or a `.catch` on each is safer. To actually cancel network work, use `AbortController` (topic 88).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Calls are independent and can run in parallel (`all`, `allSettled`)
- You want a partial response when one service is down (`allSettled`)
- You need a timeout or the fastest of several sources (`race`)
- You need the first successful mirror or fallback (`any`)

❌ Avoid when:
- Each call needs the result of the previous one (use a chain or sequential `await`)
- You expect hundreds of parallel calls; use a concurrency limiter instead of starting them all
- You use `race` expecting success only; it can return a rejection

---

## 📊 Visual Diagram
```
Inputs:            A(100ms ✓)   B(150ms ✗)   C(50ms ✓)

Promise.all      ──────────────────────────────►  REJECT at 150ms (B's error)
Promise.allSettled ────────────────────────────►  FULFILL at 150ms [✓, ✗, ✓]
Promise.race     ─────►  settle at 50ms with C (first to settle)
Promise.any      ───────────────────►  FULFILL at 100ms with A (first success)

Legend: ✓ = fulfilled   ✗ = rejected
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `Promise.all` | Wait for all to fulfill; reject on first failure | सबके fulfill होने का इंतज़ार; पहली failure पर reject |
| `Promise.allSettled` | Wait for all to settle; never rejects | सबके settle होने का इंतज़ार; कभी reject नहीं |
| `Promise.race` | Settles with the first settled promise | सबसे पहले settle होने वाला नतीजा |
| `Promise.any` | Settles with the first fulfilled promise | सबसे पहले सफल (fulfilled) नतीजा |
| `AggregateError` | Error holding all rejection reasons (`errors`) | सारी errors वाला एक error object |
| Combinator | Function that combines many promises into one | कई promises को एक में जोड़ने वाला function |
| Fail fast | Stop and reject at the first error | पहली error पर तुरंत रुक जाना |

---

## ⚡ 3-Line Summary
**English:**
1. `all` needs everything to succeed; `allSettled` reports everything; `race` takes the first to settle; `any` takes the first success.
2. All four start the promises in parallel, and `all`/`allSettled` keep input order.
3. Use `allSettled` for partial pages, `race` for timeouts, and `any` for fallback mirrors.

**Hindi:**
1. `all` को सबका सफल होना चाहिए; `allSettled` सबकी रिपोर्ट देता है; `race` पहले settle होने वाला लेता है; `any` पहली सफलता लेता है।
2. चारों promises को parallel में शुरू करते हैं, और `all`/`allSettled` input का क्रम रखते हैं।
3. Partial page के लिए `allSettled`, timeout के लिए `race`, और fallback mirrors के लिए `any` इस्तेमाल करो।

---

## ➡️ Next Topic
**83. async/await — Complete Guide** — These combinators run promises together. Next, learn `async`/`await`, the syntax that makes sequential and parallel promise code read like normal synchronous code.
