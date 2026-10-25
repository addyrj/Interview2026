# 72. Phase 5 — Check (setImmediate)
# हिंदी में: Phase 5 — Check Phase (setImmediate)

---

## 🔵 Simple Definition (English)
The **Check** phase runs immediately after the Poll phase, and it's where `setImmediate()` callbacks execute. Despite the name "immediate," it does NOT run instantly when called — it runs after the current Poll phase completes, making it useful for "run this right after I/O, but before the next full loop iteration" scenarios.

## 🔵 सरल परिभाषा (Hindi)
**Check** phase Poll phase के बिल्कुल बाद चलता है, और यहीं `setImmediate()` के callbacks execute होते हैं। "immediate" नाम के बावजूद ये call होते ही तुरंत नहीं चलता — current Poll phase खत्म होने के बाद चलता है, इसलिए "I/O के ठीक बाद, पर अगले पूरे loop iteration से पहले" वाले cases में useful है।

---

## 🔴 Problem it Solves
```
NEED: Sometimes you want a callback to run AFTER the current I/O
      processing completes, but you don't want to wait a full timer cycle.

WITHOUT setImmediate (only setTimeout available):
  setTimeout(fn, 0) — order relative to I/O callbacks is INCONSISTENT
  (depends on how much time has already elapsed in the current tick)

WITH setImmediate:
  Inside an I/O callback, setImmediate(fn) ALWAYS runs right after
  the current Poll phase finishes — deterministic, no guessing.
  Common use: breaking up CPU-heavy loops into chunks so I/O isn't starved.
```

## 🔴 यह क्यों बना? (Hindi)
```
कभी-कभी current I/O processing के ठीक बाद callback चलाना होता है
setTimeout(fn, 0) का order I/O callbacks के relative inconsistent होता है
setImmediate() से I/O callback के अंदर guaranteed order मिलता है
CPU-heavy loops को chunks में तोड़ने के लिए भी useful है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → setImmediate(callback) registers the callback in the "check queue"
Step 2 → Event loop finishes current Poll phase (processes all ready I/O)
Step 3 → Event loop immediately moves to CHECK phase (Phase 5)
Step 4 → All queued setImmediate callbacks run, in registration order
Step 5 → Microtasks (nextTick/Promise) drain between Poll and Check too
Step 6 → Event loop moves to Phase 6: Close Callbacks
Step 7 → setImmediate scheduled INSIDE a Check-phase callback runs on the
          NEXT loop iteration's Check phase, not immediately again
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. setImmediate(callback) "check queue" में register होता है
2. Poll phase खत्म होने पर event loop तुरंत Check phase में आता है
3. सभी queued setImmediate callbacks registration order में run होते हैं
4. Poll और Check के बीच भी microtasks drain होते हैं
5. फिर Close Callbacks phase चलता है
```

---

## 🟡 Real World Example
**Swiggy order-batch processing:** When processing a large batch of 10,000 orders for end-of-day reconciliation, instead of running all 10,000 in one tight synchronous loop (which would block the event loop and stall live order requests), engineers process orders in chunks of 100, then call `setImmediate(processNextChunk)` — this yields control back to the event loop after each chunk, letting pending HTTP requests (new live orders) get handled in between chunks, before resuming the batch job. This keeps the API responsive even during heavy background processing.

## 🟡 Real Example Hindi mein
**Swiggy:** 10,000 orders का end-of-day batch process करते वक्त, सबको एक साथ tight loop में process करने से event loop block हो जाएगा। इसलिए 100-100 के chunks में process करके हर chunk के बाद `setImmediate(processNextChunk)` call करते हैं — इससे live order requests बीच में handle हो जाती हैं, API responsive रहता है।

---

## 💻 Code Example — Basic

```javascript
// check-phase-basic.js
// Run: node check-phase-basic.js

console.log('1: sync start');

setImmediate(() => {
  console.log('3: setImmediate (Check phase)');
});

setTimeout(() => {
  console.log('4: setTimeout (Timers phase, next iteration)');
}, 0);

console.log('2: sync end');

// OUTPUT (in the main script, order of 3 vs 4 can vary slightly,
// but INSIDE an I/O callback it is always deterministic — see next example):
// 1: sync start
// 2: sync end
// 3: setImmediate (Check phase)   <- often but not always first
// 4: setTimeout (Timers phase)
```

## 💻 Code Example — Advanced

```javascript
// check-phase-advanced.js — chunked processing with setImmediate (yielding control)

function processBigArray(items, chunkSize, onDone) {
  let index = 0;

  function processChunk() {
    const end = Math.min(index + chunkSize, items.length);

    // Process a small chunk synchronously (fast, doesn't block long)
    for (; index < end; index++) {
      items[index] = items[index] * 2;  // example transform
    }

    if (index < items.length) {
      // CRITICAL: yield control back to event loop before next chunk
      // This lets any pending I/O (incoming HTTP requests) get processed
      // in between chunks, instead of blocking until the WHOLE array is done
      setImmediate(processChunk);
    } else {
      onDone(items);
    }
  }

  processChunk();
}

// Simulate 1 million items — would block if done in one sync loop
const bigArray = Array.from({ length: 1_000_000 }, (_, i) => i);

console.log('Starting chunked processing...');
const start = Date.now();

processBigArray(bigArray, 50_000, (result) => {
  console.log(`Done in ${Date.now() - start}ms, first item: ${result[0]}, last: ${result[result.length - 1]}`);
});

// While this runs, the event loop is still free to process OTHER
// I/O (like incoming HTTP requests) in between each setImmediate chunk —
// unlike a single synchronous for-loop which would block everything.
console.log('This logs immediately — main script continues');
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Real use case: batch processing endpoint that doesn't block other requests
app.post('/admin/reprocess-orders', (req, res) => {
  const orderIds = req.body.orderIds;  // could be thousands of IDs
  res.json({ status: 'started', count: orderIds.length });  // respond immediately

  let i = 0;
  function processNext() {
    if (i >= orderIds.length) {
      console.log('Batch reprocessing complete');
      return;
    }
    // Process one order's worth of work synchronously (kept small)
    reprocessOrder(orderIds[i]);
    i++;

    // Yield back to event loop after EACH order, so other requests
    // (live customer traffic) get a chance to be handled in between
    setImmediate(processNext);
  }
  processNext();
});

function reprocessOrder(id) {
  // lightweight sync work simulating reconciliation logic
}

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Confusing `setImmediate` with "runs instantly"
```javascript
// WRONG assumption: setImmediate means "right now, synchronously"
setImmediate(() => console.log('immediate'));
console.log('sync');
// Output: 'sync' FIRST, then 'immediate' — sync code always wins
// setImmediate just means "Check phase, soon" — not instant/synchronous
```

❌ **Mistake 2:** Relying on setImmediate vs setTimeout(0) order in the MAIN script
```javascript
// WRONG: assuming this order is always guaranteed outside an I/O callback
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));
// Order here is NOT deterministic — depends on how long it took Node
// to even start executing the script (process startup overhead can vary)

// CORRECT: if you need guaranteed order, use setImmediate inside an
// I/O callback where it's ALWAYS guaranteed to run before setTimeout(0)
```

---

## 🧠 Tricky Interview Question

```javascript
setImmediate(() => {
  console.log('immediate 1');
  setImmediate(() => console.log('immediate 2 (nested)'));
});
setImmediate(() => console.log('immediate 3'));
```

**Answer:** Output: `immediate 1`, `immediate 3`, `immediate 2 (nested)`. Explanation: Both top-level `setImmediate` calls (1 and 3) are queued for the SAME Check phase iteration and run in registration order. But the NESTED `setImmediate` (scheduled from inside "immediate 1"'s callback) gets queued for the NEXT loop iteration's Check phase — it doesn't run in the current batch, because the current Check phase's queue was already captured before "immediate 1" started executing.

---

## ⚫ Interview Questions + Answers

**Q1: What is `setImmediate()` and when does it run?**
A1: `setImmediate()` schedules a callback to run in the **Check phase**, which is the phase immediately after Poll in each event loop iteration. It's designed for "run this after I/O processing in this iteration, but don't wait for a full timer cycle."

**Q2: Why is `setImmediate` preferred over `setTimeout(0)` inside I/O callbacks?**
A2: Inside an I/O (Poll-phase) callback, `setImmediate` is GUARANTEED to run before any `setTimeout(0)`, because Check is the very next phase after Poll, while `setTimeout` requires looping all the way back to Timers (Phase 1) on the next full iteration. This determinism makes `setImmediate` the right tool when you specifically need "run right after this I/O work."

**Q3: How does `setImmediate` help avoid blocking the event loop during heavy synchronous processing?**
A3: By breaking a large task into chunks and calling `setImmediate(processNextChunk)` after each chunk, you yield control back to the event loop between chunks. This lets other pending I/O (incoming requests, timers) get processed, instead of running the entire task in one long synchronous block that would starve everything else.

**Q4: What's the difference between `setImmediate` and `process.nextTick`?**
A4: `process.nextTick` is a MICROTASK — it runs before ANY event loop phase, immediately after the current operation completes (even before Promises). `setImmediate` is a MACROTASK tied to a specific phase (Check) — it runs after the Poll phase completes, as part of the normal phase cycle. nextTick has much higher priority and can starve the event loop if used recursively; setImmediate cannot (it always waits its turn in the Check phase queue).

**Q5: Can you cancel a `setImmediate` callback?**
A5: Yes — `setImmediate()` returns an `Immediate` object; pass it to `clearImmediate(immediateObj)` to cancel it before it runs, similar to `clearTimeout`. This is useful for cleanup if the pending work becomes irrelevant (e.g., the associated request was aborted).

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need deterministic "run right after I/O" ordering inside a callback
- Breaking up CPU-heavy loops into event-loop-friendly chunks
- Avoiding starving I/O while doing batch processing

❌ **Avoid when:**
- You need a true delay — use `setTimeout` instead
- In the main script where exact order vs setTimeout(0) doesn't matter and determinism isn't needed

---

## 📊 Visual Diagram

```
CHECK PHASE (Phase 5):
──────────────────────────────────────────────────────

  POLL phase finishes (all ready I/O callbacks processed)
         │
         ▼
  [microtasks drain: nextTick → Promise]
         │
         ▼
  CHECK PHASE
  ┌─────────────────────────────────────┐
  │  Run all setImmediate() callbacks    │
  │  queued SO FAR, in order             │
  │                                      │
  │  If a callback schedules ANOTHER     │
  │  setImmediate → goes to NEXT         │
  │  iteration's Check phase, not this   │
  │  one                                 │
  └──────────────────┬────────────────────┘
                     ▼
         Phase 6: CLOSE CALLBACKS
                     │
                     ▼
         loop back to Phase 1: TIMERS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Check Phase | Phase running setImmediate callbacks | setImmediate callbacks चलाने वाला phase |
| `setImmediate()` | Schedule callback for Check phase | Check phase के लिए callback schedule करना |
| `clearImmediate()` | Cancel a pending setImmediate | Pending setImmediate cancel करना |
| Chunked Processing | Breaking work to yield control | Work को तोड़कर control yield करना |

---

## ⚡ 3-Line Summary
English:
1. Check is Phase 5, running right after Poll — it's where `setImmediate()` callbacks execute.
2. Inside any I/O callback, `setImmediate` always runs before `setTimeout(0)` — this ordering is guaranteed there, unlike in the main script.
3. Use `setImmediate` to break up CPU-heavy loops into chunks, keeping the event loop responsive to other I/O.

Hindi:
1. Check Phase 5 है, Poll के ठीक बाद चलता है — यहीं `setImmediate()` callbacks execute होते हैं।
2. किसी भी I/O callback के अंदर `setImmediate` हमेशा `setTimeout(0)` से पहले चलता है — ये guarantee वहीं मिलती है, main script में नहीं।
3. CPU-heavy loops को chunks में तोड़ने के लिए `setImmediate` use करो, event loop responsive रहता है।

---

## ➡️ Next Topic
**73. Phase 6 — Close Callbacks** — The final phase, handling socket/handle close events।
