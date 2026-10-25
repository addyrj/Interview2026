# 193. Event Loop Output Questions
# हिंदी में: Event Loop Output Questions — कोड का output पहले से predict करना

---

## 🔵 Simple Definition (English)
Event loop output questions ask you to predict the exact order in which `console.log` lines print when code mixes synchronous code, `process.nextTick`, Promises (microtasks), `setTimeout` (timers) and `setImmediate`. The answer depends only on the queue rules, not on how long the code takes.

## 🔵 सरल परिभाषा (Hindi)
Event loop output questions में आपको यह predict करना होता है कि जब synchronous code, `process.nextTick`, Promises (microtasks), `setTimeout` (timers) और `setImmediate` एक साथ हों, तो `console.log` किस exact क्रम में print होंगे। जवाब queue के नियमों पर निर्भर करता है, code कितनी देर चलता है उस पर नहीं।

---

## 🔴 Problem it Solves

**Problem statement:** Predict the output of the following code without running it, then explain each step.

```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
process.nextTick(() => console.log("D"));
(async () => { console.log("E"); await null; console.log("F"); })();
console.log("G");
```

Interviewers ask this because most candidates think `setTimeout(fn, 0)` runs "immediately". It does not. Async code that depends on order (logging, caching, retries, analytics) needs a correct mental model of the event loop. Without it, bugs look random.

## 🔴 यह क्यों बना? (Hindi)
JavaScript single-threaded है, इसलिए async काम को queues में लगाना पड़ता है। लोग अक्सर मान लेते हैं कि `setTimeout(fn, 0)` तुरंत चलेगा, जबकि वह current stack और microtasks खत्म होने के बाद चलता है। Logging, caching, retries और analytics जैसे कामों में गलत order से bugs आते हैं, जो random लगते हैं। इसलिए event loop का सही mental model ज़रूरी है।

---

## 🟢 How it Works — Step by Step

Step 1 → Main script runs fully on the call stack: `A`, then the synchronous part of the async function `E`, then `G`.
Step 2 → When the main script ends, Node drains the `process.nextTick` queue: `D`.
Step 3 → Then Node drains the microtask queue (Promise jobs) in queue order: `C`, then `F` (the `await` continuation).
Step 4 → When microtasks are empty, the event loop enters the timers phase: `B`.
Step 5 → `setImmediate` callbacks run in the check phase, after the poll phase (I/O). Both are macrotasks.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Main script call stack पर पूरा चलती है: `A`, फिर async function का synchronous हिस्सा `E`, फिर `G`।
Step 2 → Main script खत्म होने पर Node `process.nextTick` queue खाली करता है: `D`।
Step 3 → फिर Node microtask queue (Promise jobs) queue के क्रम में खाली करता है: `C`, फिर `F` (यानी `await` के बाद का हिस्सा)।
Step 4 → Microtasks खत्म होने पर event loop timers phase में जाता है: `B`।
Step 5 → `setImmediate` callbacks check phase में चलते हैं, poll phase (I/O) के बाद। ये दोनों macrotasks हैं।

---

## 🟡 Real World Example
Swiggy के order-tracking service में एक function पहले log लिखता है, फिर Razorpay webhook की पुष्टि के लिए Promise चलाता है, और फिर 0ms का retry timer लगाता है। Developer सोचता है कि retry timer पुष्टि से पहले चलेगा, पर असल में पुष्टि (microtask) पहले पूरी होती है। अगर वह गलत order समझे तो UI पहले "retry" दिखाएगा और बाद में "paid", जिससे flicker होता है।

Zomato के delivery-partner app में location update को `setTimeout(0)` से schedule किया गया, जबकि UI render को `process.nextTick` के तुरंत बाद होना था। Output questions इसी तरह की गलती पकड़ने के लिए होते हैं।

## 🟡 Real Example Hindi mein
Swiggy के order-tracking service में एक function पहले log लिखता है, फिर Razorpay webhook की पुष्टि के लिए Promise चलाता है, और फिर 0ms का retry timer लगाता है। Developer सोचता है कि retry timer पुष्टि से पहले चलेगा, पर असल में पुष्टि (microtask) पहले पूरी होती है। अगर वह गलत order समझे तो UI पहले "retry" दिखाएगा और बाद में "paid", जिससे flicker होता है।

Zomato के delivery-partner app में location update को `setTimeout(0)` से schedule किया गया, जबकि UI render को `process.nextTick` के तुरंत बाद होना था। Output questions इसी तरह की गलती पकड़ने के लिए होते हैं।

---

## 💻 Code Example — Basic
```javascript
// ── Event loop order: sync, nextTick, microtask, timer ──

console.log("1. sync start");              // runs immediately on the call stack

setTimeout(() => {                         // timers phase (macrotask), 0ms means "as soon as possible"
  console.log("5. setTimeout 0");          // runs last, after microtasks are empty
}, 0);

Promise.resolve().then(() => {             // microtask queue (Promise job)
  console.log("3. promise then");          // runs after nextTick queue is empty
});

process.nextTick(() => {                   // nextTick queue, drained before promise jobs in Node
  console.log("2. process.nextTick");      // runs right after main script finishes
});

queueMicrotask(() => {                     // microtask queue, same lane as Promise.then
  console.log("4. queueMicrotask");        // queued after the promise callback, so runs after it
});

console.log("1b. sync end");               // still synchronous, prints before any queue runs
```

**Expected output (verified with `node`):**
```
1. sync start
1b. sync end
2. process.nextTick
3. promise then
4. queueMicrotask
5. setTimeout 0
```

## 💻 Code Example — Advanced
```javascript
// Simplified model of the event loop for code scheduled from the MAIN script.
// Lanes are drained in a fixed order: tick -> micro -> timer -> immediate.

const LANES = ["tick", "micro", "timer", "immediate"]; // drain priority (highest first)

// tasks: array of { name, lane } where lane is "sync" or one of LANES.
// Returns the predicted console output order as an array of names.
function predictOrder(tasks) {
  if (!Array.isArray(tasks)) throw new TypeError("tasks must be an array"); // validate input
  const order = [];                                   // result list
  const queues = { tick: [], micro: [], timer: [], immediate: [] }; // one FIFO per lane
  for (const task of tasks) {                         // single pass: O(n)
    if (!task || typeof task.name !== "string") {     // guard against bad items
      throw new TypeError("each task needs a string name"); // fail loudly
    }
    if (task.lane === "sync") order.push(task.name);  // sync code prints first, in source order
    else if (queues[task.lane]) queues[task.lane].push(task.name); // FIFO keeps source order
    else throw new RangeError(`unknown lane: ${task.lane}`); // unknown lane is a bug
  }
  for (const lane of LANES) {                         // drain lanes in priority order
    order.push(...queues[lane]);                      // append all tasks of this lane
  }
  return order;                                       // predicted output order
}

// Test the model against the basic example's scheduling.
const predicted = predictOrder([
  { name: "1. sync start", lane: "sync" },            // sync
  { name: "5. setTimeout 0", lane: "timer" },         // timer
  { name: "3. promise then", lane: "micro" },         // microtask
  { name: "2. process.nextTick", lane: "tick" },      // nextTick
  { name: "4. queueMicrotask", lane: "micro" },       // microtask (after promise)
  { name: "1b. sync end", lane: "sync" },             // sync
]);
console.log(predicted.join("\n"));                    // print predicted order

// Complexity: time O(n) (one pass to bucket, one pass to drain), space O(n) for queues and output.
// Limitation: this models only tasks queued by the main script, not nested scheduling.
```

**Expected output:**
```
1. sync start
1b. sync end
2. process.nextTick
3. promise then
4. queueMicrotask
5. setTimeout 0
```

## 🟣 Express.js Integration
In Express, a request handler is itself a callback run by the event loop. A CPU-heavy loop inside a route blocks every other request. The fix is to split the work and yield with `setImmediate`, so `/health` and other routes keep responding between chunks.

```javascript
// npm install express
const express = require("express");                     // import Express
const app = express();                                  // create the app

// Sum 0..n in chunks, yielding to the event loop between chunks
function chunkedSum(n, chunkSize = 1e6) {               // returns a Promise
  return new Promise(resolve => {                       // wrap the callback style in a Promise
    let i = 0;                                          // next number to add
    let total = 0;                                      // running total
    function step() {                                   // do one chunk of work
      const end = Math.min(i + chunkSize, n + 1);       // upper bound of this chunk
      for (; i < end; i++) total += i;                  // CPU work for this chunk only
      if (i <= n) setImmediate(step);                   // yield: other requests can run now
      else resolve(total);                              // finished, resolve the Promise
    }
    step();                                             // start the first chunk
  });
}

app.get("/health", (req, res) => res.json({ ok: true })); // stays fast while sums run

app.get("/sum/:n", async (req, res) => {                // route with a path parameter
  const n = Number(req.params.n);                       // params are strings, convert to number
  if (!Number.isInteger(n) || n < 0 || n > 1e9) {       // validate input before doing work
    return res.status(400).json({ error: "n must be an integer 0..1e9" }); // reject bad input
  }
  const total = await chunkedSum(n);                    // non-blocking loop
  res.json({ n, total });                               // send the result
});

app.listen(3000, () => console.log("listening on 3000")); // start the server
```

**Verified:** `GET /sum/10` returns `{"n":10,"total":55}` and `/health` answers while `/sum/1000000000` is running.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `setTimeout(fn, 0)` runs immediately.
✅ Correct: It runs after the current stack, all nextTicks, and all microtasks are finished.

```javascript
// Wrong: expects the timer to have run already
let flag = false;                                       // shared state
setTimeout(() => { flag = true; }, 0);                  // schedule the change
console.log("flag:", flag);                             // prints false, not true

// Right: read the value inside the callback, after the timer ran
let flag2 = false;                                      // shared state
setTimeout(() => { flag2 = true; console.log("flag:", flag2); }, 0); // prints true here
```

❌ Mistake 2: `await` lets timers and I/O run.
✅ Correct: `await` only yields to the microtask queue. A long chain of `await null` runs before any timer. To really yield to the timers phase, await a timer.

```javascript
// Wrong assumption: "the timer fires between the awaits, so done is still false"
// Real output: "timer, done = true", because all microtasks finish before any timer
let done = false;                                       // flag set by async work
setTimeout(() => console.log("timer, done =", done), 0); // scheduled first
(async () => { for (let i = 0; i < 3; i++) await null; done = true; })(); // only microtasks

// Right: await a real timer, so the timers phase gets a turn
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); // helper
(async () => {                                          // async IIFE
  await sleep(0);                                       // yields to the timers phase
  console.log("after a real macrotask yield");          // runs in a later turn
})();
```

**Edge cases (keep in mind):**
- A microtask that schedules another microtask runs before any timer, so an endless `Promise` chain can starve timers and I/O.
- A recursive `process.nextTick` loop starves the Promise queue and the event loop completely.
- `setTimeout(fn, 0)` is at least about 1ms in Node, so never use it for "exact" ordering.
- Between `setTimeout(0)` and `setImmediate` from the main module, the order is not guaranteed. Inside an I/O callback, `setImmediate` always runs first.
- An `async` function runs synchronously until its first `await`.

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: scheduling from INSIDE a timer callback
setTimeout(() => {                                      // outer timer, runs in the timers phase
  console.log("outer timeout");                         // (1)
  setTimeout(() => console.log("inner timeout"), 0);    // (4) next loop's timers phase
  setImmediate(() => console.log("inner immediate"));   // (3) check phase, same loop
  process.nextTick(() => console.log("inner tick"));    // (2) runs right after this callback
}, 0);
```

Answer: `outer timeout`, `inner tick`, `inner immediate`, `inner timeout`.
Why: After the outer timer callback returns, Node drains the nextTick queue first (`inner tick`). The event loop then moves to the poll and check phases in the same iteration, so `setImmediate` runs (`inner immediate`). The inner `setTimeout` must wait for the next loop iteration's timers phase, so it prints last. This order is deterministic when the scheduling happens inside a timer or I/O callback, but not when it happens on the main script.

---

## ⚫ Interview Questions + Answers

Q1: Why does `process.nextTick` run before a resolved Promise callback in Node?
A1: Node keeps its own nextTick queue and drains it completely after the current operation and before the microtask (Promise) queue. Both run before any timer or I/O callback.

Q2: Is `setTimeout(fn, 0)` guaranteed to run in exactly 0ms?
A2: No. Node clamps the delay to at least 1ms and the callback runs only when the timers phase is reached, after the current stack and microtasks are done.

Q3: Does `await` block the thread?
A3: No. `await` suspends only the async function and returns control to the caller. The rest of the event loop keeps running.

Q4: What is the order of `setImmediate` and `setTimeout(0)` when scheduled from an I/O callback?
A4: `setImmediate` always runs first, because the check phase comes right after the poll phase, before the next timers phase.

Q5: Does the browser event loop have `process.nextTick`?
A5: No. Browsers have microtasks (Promises, `queueMicrotask`), macrotasks (timers, events) and rendering steps. `process.nextTick` is Node-specific.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to reason about the order of logs, callbacks or state updates in async code.
- You are writing a library that must run a callback "after the current code but before I/O" (`process.nextTick`).
- You want to split a long CPU loop into chunks so the server keeps responding (`setImmediate`).

❌ Avoid when:
- You rely on exact timing (`setTimeout(fn, 0)` ordering) across different machines or Node versions.
- You use recursive `process.nextTick` for scheduling, because it blocks I/O.
- You need guaranteed ordering between independent async operations. Use explicit `await` or a dependency chain instead.

---

## 📊 Visual Diagram
```
 ┌─────────────────────────────────────────────────────────────┐
 │ Main script (call stack)   prints: A, E, G                   │
 └──────────────┬──────────────────────────────────────────────┘
                ▼
 ┌─────────────────────────────┐
 │ process.nextTick queue      │  → D
 └──────────────┬──────────────┘
                ▼
 ┌─────────────────────────────┐
 │ Microtask queue (Promises)  │  → C, F
 └──────────────┬──────────────┘
                ▼
 ┌─────────────────────────────┐
 │ Timers phase (setTimeout)   │  → B
 ├─────────────────────────────┤
 │ Poll phase (I/O callbacks)  │
 ├─────────────────────────────┤
 │ Check phase (setImmediate)  │
 └─────────────────────────────┘
        ↺ loop repeats
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Call stack | Where synchronous code runs, one frame at a time | कॉल स्टैक |
| Event loop | Loop that moves queued callbacks to the stack when it is empty | इवेंट लूप |
| Microtask | Promise job or `queueMicrotask` callback, runs after the current stack | माइक्रोटास्क |
| Macrotask | Timer, I/O or `setImmediate` callback, runs in its own phase | मैक्रोटास्क |
| nextTick queue | Node-only queue, drained before Promise jobs | nextTick queue |
| Timers phase | Phase that runs due `setTimeout`/`setInterval` callbacks | टाइमर्स फेज़ |
| Check phase | Phase that runs `setImmediate` callbacks | चेक फेज़ |
| Starvation | A queue that never gets a turn because another keeps adding work | स्टार्वेशन |

---

## ⚡ 3-Line Summary
English: Predict order by draining in this sequence: synchronous code, then `process.nextTick`, then microtasks (Promises), then timers and `setImmediate`.
English: `setTimeout(fn, 0)` never runs in the current stack, and `await` yields only to microtasks, not to timers.
English: Use this model for interviews, and avoid relying on exact timer ordering in production code.

Hindi: Order predict करने के लिए इस क्रम में queues खाली करें: synchronous code, फिर `process.nextTick`, फिर microtasks (Promises), फिर timers और `setImmediate`।
Hindi: `setTimeout(fn, 0)` current stack में कभी नहीं चलता, और `await` केवल microtasks को yield करता है, timers को नहीं।
Hindi: Interview में यही model इस्तेमाल करें, और production code में exact timer order पर निर्भर न रहें।

---

## ➡️ Next Topic
194. Hoisting Output Questions — अगला topic यह दिखाता है कि `var`, `let`, `const` और function declarations का memory में पहले से कैसे setup होता है। Event loop के बाद hoisting पढ़ना सही है, क्योंकि दोनों में "code चलने से पहले क्या तय होता है" वाला सवाल आता है।
