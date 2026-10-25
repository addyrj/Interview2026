# 75. Microtask Queue vs Macrotask Queue
# हिंदी में: Microtask Queue बनाम Macrotask Queue — कौन पहले चलेगा और क्यों

---

## 🔵 Simple Definition (English)
**Microtasks** are small follow-up jobs (Promise `then/catch/finally`, `queueMicrotask`, `process.nextTick`) that run right after the current code finishes. **Macrotasks** are bigger jobs (timers, I/O, `setImmediate`) that run one at a time in later event loop phases. All pending microtasks are drained before the next macrotask starts.

## 🔵 सरल परिभाषा (Hindi)
**Microtasks** छोटे follow-up काम हैं (Promise के `then/catch/finally`, `queueMicrotask`, `process.nextTick`), जो मौजूदा code खत्म होते ही तुरंत चलते हैं। **Macrotasks** बड़े काम हैं (timers, I/O, `setImmediate`), जो बाद के event loop phases में एक-एक करके चलते हैं। अगला macrotask शुरू होने से पहले सारे pending microtasks खाली किए जाते हैं।

---

## 🔴 Problem it Solves
Promise का result आने पर उसका follow-up code तुरंत चलना चाहिए, वरना data और UI या response के बीच बेमेल हो सकता है। अगर promise callbacks को भी timer queue में डाला जाता, तो हर `await` के बाद कई timer ticks की देर लगती। दो queues अलग रखने से promises predictable और तेज़ रहते हैं।

## 🔴 यह क्यों बना? (Hindi)
Paytm wallet में balance check करने के बाद "payment successful" दिखाना है। यह promise chain का अगला step है। अगर यह step timer queue में जाए, तो बीच में दूसरे timers और I/O आ सकते हैं, और wallet state पुराना दिखेगा। इसलिए promise follow-ups को microtask queue में रखा गया, ताकि वे एक ही चक्र में निपट जाएँ।

---

## 🟢 How it Works — Step by Step

Step 1 → एक macrotask (जैसे timer callback) चलता है
Step 2 → उस दौरान बने सारे microtasks queue में जुड़ते हैं
Step 3 → Macrotask खत्म होते ही engine सारे microtasks एक-एक करके चलाता है, नए बने microtasks भी उसी drain में चलते हैं
Step 4 → Microtask queue पूरी खाली होने पर ही अगला macrotask उठता है
Step 5 → Node में `process.nextTick` queue, promise queue से पहले drain होती है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक macrotask (जैसे timer callback) चलता है
Step 2 → उसके दौरान बने सारे microtasks queue में जुड़ते हैं
Step 3 → Macrotask खत्म होने पर सारे microtasks एक-एक करके चलते हैं, नए बने microtasks भी इसी drain में चलते हैं
Step 4 → Microtask queue खाली होने पर ही अगला macrotask आता है
Step 5 → Node में `process.nextTick` queue, promise queue से पहले खाली होती है

---

## 🟡 Real World Example
Flipkart पर "Place order" click करने के बाद API call (macrotask/I/O) पूरी होती है। उसका `then` callback (microtask) तुरंत order ID दिखाता है और cart clear करता है। अगर इस बीच कोई timer फायर हो, तो वह उस microtask drain के बाद ही चलेगा, इसलिए UI का अगला state पहले से तय रहता है।

## 🟡 Real Example Hindi mein
Flipkart पर "Place order" click के बाद API call पूरी होती है। उसका `then` callback (microtask) तुरंत order ID दिखाता है और cart खाली करता है। इस बीच आया कोई timer उस microtask drain के बाद ही चलेगा, इसलिए अगला state पहले से तय रहता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: microtasks run before macrotasks, even when the timer was scheduled first
// Run with: node 75-microtask-queue-vs-macrotask-queue.js

setTimeout(() => console.log("macrotask: timer"), 0);      // macrotask, queued first

Promise.resolve().then(() => console.log("microtask: promise then"));  // microtask

queueMicrotask(() => console.log("microtask: queueMicrotask")); // microtask, queued last

console.log("sync: main code");                             // runs before any queue

// Output order: sync, then both microtasks (in insertion order), then the timer.
// Even though setTimeout was written first, its callback waits for the macrotask turn.
```

## 💻 Code Example — Advanced
```javascript
// Goal: process a large list without starving the event loop.
// Strategy: do a chunk of work in one macrotask, then yield with setImmediate.

// Simulated job list (imagine 100k order records to recompute)
const orders = Array.from({ length: 100_000 }, (_, i) => ({ id: i, amount: i % 500 }));

// Process in chunks and return a promise with the final total
function sumOrderAmounts(items, chunkSize = 10_000) {
  return new Promise((resolve, reject) => {       // promise wraps the whole job
    let index = 0;                                // where we are in the list
    let total = 0;                                // running sum
    let yieldCount = 0;                           // how many times we yielded to the loop

    function runChunk() {
      try {                                       // protect the chunk from unexpected errors
        const end = Math.min(index + chunkSize, items.length); // chunk boundary
        for (; index < end; index++) {
          total += items[index].amount;           // do one unit of work
        }
        if (index < items.length) {
          yieldCount++;                           // count the yield for logging
          setImmediate(runChunk);                 // macrotask: give timers and I/O a turn
        } else {
          resolve({ total, yieldCount });         // all chunks done
        }
      } catch (err) {
        reject(err);                              // surface any error to the caller
      }
    }

    runChunk();                                   // start the first chunk right away
  });
}

// Microtask-based follow-up: runs as soon as the promise resolves
async function main() {
  const { total, yieldCount } = await sumOrderAmounts(orders); // wait for the chunked job
  console.log("total:", total);                   // total of all amounts
  console.log("yields:", yieldCount);             // 9 yields for 10 chunks
}

// A timer scheduled during the job proves the loop was not starved
let ticked = false;
setTimeout(() => { ticked = true; }, 0);          // should fire between chunks

main().then(() => console.log("timer ran during job:", ticked)).catch((e) => console.error(e));
```

---

## 🟠 Express.js Integration
Express middleware और route handlers अक्सर promises return करते हैं। Promise का `.then`/`await` के बाद का code microtask है, और response भेजने का काम उसी drain में होता है। नीचे का route एक DB-like async call (microtask के बाद) से data लेकर JSON भेजता है। Express 5 में rejected promise अपने-आप `next(err)` को जाता है। Express 4 में `try/catch` लगाना पड़ता है, जो यहाँ किया गया है।

```javascript
const express = require("express");          // web framework
const app = express();

// Fake async data source (returns a promise; resolution is a microtask follow-up)
async function findOrder(id) {
  return { id, status: "PREPARING" };        // pretend this came from a database
}

// Route handler: await resumes in a microtask, then the response is sent
app.get("/orders/:id", async (req, res, next) => {
  try {
    const order = await findOrder(req.params.id); // resumes in the microtask queue
    res.json(order);                          // send the JSON response
  } catch (err) {
    next(err);                                // hand errors to Express error middleware
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** सोचना कि `setTimeout(fn, 0)` promise `then` से पहले चलेगा
✅ **Correct:** Promise `then` microtask है और हमेशा timer (macrotask) से पहले चलता है।

```javascript
// Wrong: expecting the timer to win
setTimeout(() => console.log("timer"), 0);
Promise.resolve().then(() => console.log("promise")); // prints promise first

// Right: remember that microtasks always drain before the next macrotask
```

❌ **Mistake 2:** Microtask के अंदर recursion करके loop को रोक देना
✅ **Correct:** Promise chain या `queueMicrotask` को खुद को अनंत बार schedule न करने दो। Long work को macrotask (`setImmediate`) में डालो।

```javascript
// Wrong: this microtask chain never ends, so no timer or I/O ever runs
function forever() {
  queueMicrotask(forever);
}
// forever();  // uncommenting this freezes the event loop

// Right: schedule the next step as a macrotask so others get a turn
function everyStep(n) {
  if (n === 0) return;
  setImmediate(() => everyStep(n - 1));
}
everyStep(3);
```

❌ **Mistake 3:** `await` के बाद की values को पुराना मान लेना
✅ **Correct:** `await` के बाद का code microtask में चलता है। उसके पहले लिखा गया code पहले ही चल चुका होता है, इसलिए shared state पर ध्यान दो।

```javascript
// Wrong: assuming value is set synchronously after the call
let status = "pending";
(async () => { status = "done"; })();
console.log(status); // "pending" — the async body has not finished yet

// Right: await the result before reading it
(async () => {
  await Promise.resolve();
  console.log("after await:", status); // "pending" was read earlier; now updated below
  status = "done";
})();
```

---

## 🧠 Tricky Interview Question
```javascript
setTimeout(() => console.log("T1"), 0);

Promise.resolve().then(() => {
  console.log("P1");
  setTimeout(() => console.log("T2"), 0);
  return Promise.resolve().then(() => console.log("P2"));
}).then(() => console.log("P3"));

queueMicrotask(() => console.log("Q1"));

console.log("sync");
// What is the exact order of the output?
```
**Answer:** `sync`, `P1`, `Q1`, `P2`, `P3`, `T1`, `T2`।

- Sync code: `sync` print होता है, और T1 timer व दो microtasks queue में जाते हैं (P1 का callback, फिर Q1)।
- Microtask drain: `P1` print होता है, `T2` timer जुड़ता है, और inner `P2` callback microtask queue में जाता है। P1 का return value एक promise है, इसलिए resolution में दो extra microtask ticks लगते हैं।
- Queue में अब `Q1`, `P2`, और promise resolution का job है। `Q1` चलता है, फिर `P2`।
- Resolution पूरा होने पर `P3` चलता है, यह सब अभी उसी microtask drain में है।
- Drain खत्म होने पर timers: `T1` पहले (पहले queue हुआ), फिर `T2`।

---

## ⚫ Interview Questions + Answers

Q1: Microtask और macrotask में मुख्य फर्क क्या है?
A1: Microtasks (promise callbacks, queueMicrotask, nextTick) हर macrotask के बाद तुरंत और पूरे drain होते हैं। Macrotasks (timers, I/O, setImmediate) event loop के phases में एक-एक करके चलते हैं।

Q2: `process.nextTick` और Promise में कौन पहले चलता है?
A2: nextTick queue, promise queue से पहले drain होती है। दोनों microtasks हैं, पर Node में nextTick का अपना higher-priority queue है।

Q3: क्या microtask queue में नए microtasks जुड़ सकते हैं और कब चलते हैं?
A3: हाँ। Drain के दौरान जुड़े नए microtasks भी उसी drain में चलते हैं, जब तक queue खाली न हो। इसीलिए बहुत लंबी microtask chain timers और I/O को रोक सकती है।

Q4: Long-running काम को microtask में क्यों नहीं डालना चाहिए?
A4: Microtasks macrotask की तरह बीच में नहीं रुकते। एक लंबा काम पूरी event loop को तब तक रोक देगा जब तक वह खत्म न हो। Chunks में बाँटकर `setImmediate` से yield करो।

Q5: `queueMicrotask` का use कब करें?
A5: जब किसी callback को बस इतनी जल्दी चलाना हो कि वह मौजूदा sync code के बाद, पर अगले macrotask से पहले चले। Promise के बिना सीधा microtask schedule करने के लिए यह standard API है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Promise के follow-up code को तुरंत (same tick) चलाना हो
- Macrotask के बीच में छोटा cleanup या state update करना हो
- Chunked processing में yield का समय तय करना हो

❌ Avoid when:
- Recursive microtask chains बनाने हों
- लंबा CPU काम microtask में डालना हो
- Timer और promise के क्रम पर ऐसा code लिखना हो जो अपने आप पर निर्भर न हो

---

## 📊 Visual Diagram
```
   ┌────────────────────────────────────────────────────────┐
   │ macrotask: timer callback / I/O callback / setImmediate │
   └───────────────────────────┬────────────────────────────┘
                               │ finishes
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ MICROTASKS (drained fully, new ones join the same run) │
   │  1. process.nextTick queue                             │
   │  2. Promise then/catch/finally, queueMicrotask         │
   └───────────────────────────┬────────────────────────────┘
                               │ queue empty
                               ▼
                  next macrotask in the event loop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Microtask | Small follow-up job run right after current work | तुरंत बाद चलने वाला छोटा काम |
| Macrotask | Larger job run in a later event loop phase | बाद के phase में चलने वाला बड़ा काम |
| Microtask queue | Holds promise and queueMicrotask callbacks | Promise callbacks की queue |
| nextTick queue | Highest-priority microtask queue in Node | Node की सबसे पहले चलने वाली queue |
| queueMicrotask | Schedules a microtask directly | सीधा microtask schedule करना |
| Drain | Run all queued items until empty | Queue पूरी तरह खाली करना |
| Starvation | A queue never lets others run | दूसरे कामों को मौका न मिलना |

---

## ⚡ 3-Line Summary
**English:**
1. Microtasks (promise then, queueMicrotask, nextTick) हर macrotask के बाद पूरे drain होते हैं।
2. Macrotasks (timers, I/O, setImmediate) एक-एक करके बाद के phases में चलते हैं।
3. Microtask चेन को अनंत मत बनाओ, और लंबे काम को `setImmediate` से chunks में बाँटो।

**Hindi:**
1. Microtasks (promise then, queueMicrotask, nextTick) हर macrotask के बाद पूरे drain होते हैं।
2. Macrotasks (timers, I/O, setImmediate) एक-एक करके बाद के phases में चलते हैं।
3. Microtask चेन को अनंत मत बनाओ, और लंबे काम को `setImmediate` से chunks में बाँटो।

---

## ➡️ Next Topic
**76. setTimeout + setInterval** — timers के असली व्यवहार, delay की सीमाएँ, और repeating jobs को सही तरीके से cancel करना।
