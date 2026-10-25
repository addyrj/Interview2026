# 73. Callback Queue (Task Queue)
# हिंदी में: Callback Queue (Task Queue) — पूरे हुए callbacks की लाइन

---

## 🔵 Simple Definition (English)
The **callback queue** (also called the task or macrotask queue) is a FIFO line where finished async callbacks wait until the call stack is empty. The **event loop** takes the first callback from the queue and pushes it onto the call stack.

## 🔵 सरल परिभाषा (Hindi)
**Callback queue** (जिसे task queue भी कहते हैं) एक FIFO लाइन है, जहाँ पूरे हो चुके async callbacks तब तक इंतज़ार करते हैं जब तक call stack खाली न हो। **Event loop** लाइन से पहला callback उठाकर call stack पर डालता है।

---

## 🔴 Problem it Solves
Async काम (timer, I/O) कभी भी पूरा हो सकता है, जबकि main thread अभी दूसरा काम कर रहा हो। अगर callback उसी समय बीच में घुस जाए, तो दो कामों का state आपस में टकरा सकता है। Queue यह तय करती है कि callbacks एक-एक करके, सही क्रम में चलें।

## 🔴 यह क्यों बना? (Hindi)
मान लो Swiggy के backend पर एक ही समय पर तीन orders के callbacks तैयार हो गए। अगर वे सब एक साथ stack पर घुस जाएँ, तो shared variables बिगड़ सकते हैं। Queue उन्हें एक के बाद एक लगाती है, जैसे counter पर लाइन में लोग खड़े होते हैं। इससे हर callback को पूरा चलने का मौका मिलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Timer या I/O पूरा होता है, उसका callback queue के पीछे (end) में जुड़ता है
Step 2 → Call stack अभी भरा है, तो callback इंतज़ार करता है
Step 3 → Stack खाली होने पर event loop queue के सबसे आगे वाला callback उठाता है
Step 4 → वह callback stack पर push होता है और पूरा चलता है
Step 5 → Stack फिर खाली होने पर अगला callback उठता है (FIFO)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Timer या I/O पूरा होने पर callback queue के पीछे जुड़ता है
Step 2 → Call stack भरा हो तो callback इंतज़ार करता है
Step 3 → Stack खाली होने पर event loop सबसे आगे वाला callback उठाता है
Step 4 → वह callback stack पर चलता है
Step 5 → फिर अगला callback, इसी तरह FIFO में

---

## 🟡 Real World Example
Amazon पर "Add to cart" click करने के बाद analytics log, cart count update, और recommendation fetch जैसे callbacks queue में आते हैं। ये एक-एक करके चलते हैं, इसलिए cart count का update और analytics का log आपस में नहीं टकराते। अगर इनमें से कोई callback बहुत लंबा हो, तो पीछे वाले सब callbacks देर से चलते हैं।

## 🟡 Real Example Hindi mein
Amazon पर "Add to cart" क्लिक करने पर analytics log, cart count update और recommendations fetch के callbacks queue में आते हैं। ये एक-एक करके चलते हैं, इसलिए cart count और analytics एक-दूसरे से नहीं टकराते। अगर एक callback बहुत लंबा हो, तो उसके पीछे वाले सब देर से चलेंगे।

---

## 💻 Code Example — Basic
```javascript
// Demo: callbacks wait in a FIFO queue and run in the order they became ready
// Run with: node 73-callback-queue-task-queue.js

console.log("A: sync start");                  // runs immediately (call stack)

setTimeout(() => console.log("B: first timer"), 0);   // queued first
setTimeout(() => console.log("C: second timer"), 0);  // queued second
setTimeout(() => console.log("D: third timer"), 0);   // queued third

console.log("E: sync end");                    // runs before any queued callback

// Output order: A, E, then B, C, D (FIFO, same delay means insertion order)

// Timers with different delays go into the queue when they become ready,
// so the 0 ms ones above run before any longer delay below.
setTimeout(() => console.log("F: 50 ms timer"), 50); // becomes ready last
```

## 💻 Code Example — Advanced
```javascript
// Goal: build a tiny FIFO task queue that runs jobs one at a time,
// yields between jobs, and keeps going even if one job throws.

class TaskQueue {
  constructor() {
    this.queue = [];                        // FIFO list of pending jobs
    this.running = false;                   // true while the worker loop is active
  }

  // Add a job to the back of the queue; returns a promise for its result
  push(name, job) {
    return new Promise((resolve, reject) => {  // promise settles when the job finishes
      this.queue.push({ name, job, resolve, reject }); // store job plus its callbacks
      this.#drain();                        // start the worker if it is idle
    });
  }

  // Private method: process jobs one by one until the queue is empty
  #drain() {
    if (this.running) return;               // already working, new job waits in queue
    this.running = true;                    // mark worker as busy
    setImmediate(async () => {              // yield to the event loop before starting
      while (this.queue.length > 0) {       // keep going while jobs remain
        const { name, job, resolve, reject } = this.queue.shift(); // take the first job
        try {
          const result = await job();       // run the job, wait if it is async
          console.log(`done: ${name}`);     // log success
          resolve(result);                  // resolve the caller's promise
        } catch (err) {
          console.log(`failed: ${name} (${err.message})`); // log the failure
          reject(err);                      // reject only this caller's promise
        }
        await new Promise((r) => setImmediate(r)); // yield between jobs so others can run
      }
      this.running = false;                 // queue empty, worker goes idle
    });
  }
}

const q = new TaskQueue();                  // one queue shared by the app

async function main() {
  // Three jobs; the second one fails but the queue keeps running
  const jobs = [
    q.push("send-email", async () => "sent"),
    q.push("charge-card", async () => { throw new Error("card declined"); }),
    q.push("update-stock", async () => "updated"),
  ];

  // allSettled waits for every job, even the ones that reject
  const results = await Promise.allSettled(jobs);
  console.log(results.map((r) => r.status)); // [ 'fulfilled', 'rejected', 'fulfilled' ]
}

main();
```

---

## 🟠 Express.js Integration
Express में callback queue का सीधा इस्तेमाल कम होता है, पर `res.on("finish")` जैसे event callbacks इसी queue से चलते हैं। Response पूरा भेजे जाने के बाद callback तभी चलता है जब stack खाली हो। नीचे का route response भेजकर analytics को बाद में log करता है। यह direct task queue नहीं है, पर उसी FIFO model का इस्तेमाल है।

```javascript
const express = require("express");          // web framework
const app = express();

// Route sends the response first, then logs analytics after the response finishes
app.post("/cart/add", (req, res) => {
  const { productId } = req.body;            // product id from JSON body (needs express.json())
  res.status(201).json({ added: productId }); // send response to the client now

  // 'finish' fires after the response is written; its callback waits in the queue
  res.on("finish", () => {
    console.log("analytics: add-to-cart", productId); // runs later, does not delay the reply
  });
});

app.use(express.json());                     // parse JSON bodies (must be before routes that need it)
app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** सोचना कि `setTimeout(fn, 0)` callback को queue से "आगे" कर देगा
✅ **Correct:** Queue FIFO है। पहले से लाइन में लगे callbacks पहले चलते हैं, और `0` ms का मतलब सिर्फ "जल्द से जल्द लाइन में"।

```javascript
// Wrong: expecting "urgent" to jump the line
setTimeout(() => console.log("normal"), 0);
setTimeout(() => console.log("urgent"), 0);  // still runs AFTER "normal"

// Right: use microtasks (Promise.then / queueMicrotask) when you need to run
// before the macrotask queue continues (covered in topic 75)
```

❌ **Mistake 2:** Queue में लंबा synchronous callback डालना
✅ **Correct:** एक callback जितनी देर चलता है, पीछे वाले सब उतनी देर रुकते हैं। बड़े काम को छोटे hunks में बाँटो।

```javascript
// Wrong: one callback blocks everyone behind it
setTimeout(() => {
  for (let i = 0; i < 1e9; i++) {}   // blocks the queue for seconds
}, 0);
setTimeout(() => console.log("waited ages"), 0);

// Right: process in chunks and yield with setImmediate
function processChunk(i) {
  const end = Math.min(i + 1e6, 1e9);
  for (let j = i; j < end; j++) {}
  if (end < 1e9) setImmediate(() => processChunk(end)); // yield, let others run
}
processChunk(0);
```

❌ **Mistake 3:** Callback के अंदर error throw करके उम्मीद करना कि caller उसे पकड़ेगा
✅ **Correct:** Queue से चला callback अपने caller के stack में नहीं होता। Error को `try/catch` में पकड़ो, या promise को reject करो।

```javascript
// Wrong: throw inside a queued callback has no try/catch above it
setTimeout(() => { throw new Error("boom"); }, 0); // crashes the process

// Right: catch inside the callback, or use a promise and handle its rejection
setTimeout(() => {
  try {
    throw new Error("boom");
  } catch (err) {
    console.log("handled:", err.message);
  }
}, 0);
```

---

## 🧠 Tricky Interview Question
```javascript
const fs = require("fs");

fs.readFile(__filename, () => {              // this callback runs in the I/O phase
  setTimeout(() => console.log("timeout"), 0);  // queue a timer
  setImmediate(() => console.log("immediate")); // queue an immediate
});
// What is printed, and in what order?
```
**Answer:** पहले `immediate`, फिर `timeout`। I/O callback के अंदर event loop poll phase में है, और `setImmediate` का callback check phase में उसी loop चक्र में चलता है। `setTimeout(0)` का callback अगले timers phase में चलता है, जो अगले चक्र में आता है। इसलिए I/O callback के अंदर `setImmediate` हमेशा `setTimeout(0)` से पहले चलता है। यह गारंटी केवल I/O callback के अंदर है। Main module में दोनों का क्रम बदल सकता है।

---

## ⚫ Interview Questions + Answers

Q1: Callback queue और call stack में क्या फर्क है?
A1: Call stack वह जगह है जहाँ code अभी चल रहा है। Callback queue वह लाइन है जहाँ पूरे हो चुके async callbacks चलने का इंतज़ार करते हैं। Event loop तभी queue से callback उठाता है जब stack खाली हो।

Q2: Callback queue FIFO क्यों है?
A2: FIFO (First In, First Out) से callbacks उसी क्रम में चलते हैं जिस क्रम में वे ready हुए। यह predictability देता है, और एक ही delay वाले timers का क्रम स्थिर रहता है।

Q3: Event loop callback कब उठाता है?
A3: जब call stack पूरी तरह खाली हो। Microtasks (promises, queueMicrotask) का queue इससे पहले पूरी तरह खाली किया जाता है, जो topic 75 में विस्तार से है।

Q4: Queue में एक लंबा callback बाकी कामों पर क्या असर डालता है?
A4: वह callback पूरा होने तक stack पर रहता है, इसलिए पीछे के सभी callbacks और UI updates रुक जाते हैं। इसे blocking कहते हैं, और इससे बचने के लिए काम को छोटे हिस्सों में बाँटते हैं।

Q5: `setImmediate` और `setTimeout(0)` में फर्क कब मायने रखता है?
A5: Main module में उनका क्रम अनिश्चित हो सकता है। I/O callback के अंदर `setImmediate` हमेशा पहले चलता है, क्योंकि check phase, timers phase से पहले आता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Background में चलने वाले कई छोटे jobs को एक-एक करके चलाना हो
- Shared state वाले callbacks को क्रम से चलाना हो
- Response भेजने के बाद कोई छोटा काम (logging, analytics) करना हो

❌ Avoid when:
- Queue में एक ही बहुत भारी job डालना हो (पूरा app रुक जाएगा)
- Urgent काम को "आगे" भेजने की उम्मीद हो (queue में यह नहीं होता)
- Microtask वाला काम macrotask queue में डालना हो, जिससे देरी बढ़े

---

## 📊 Visual Diagram
```
  CALLBACK QUEUE (FIFO)                  CALL STACK
  ┌──────────────────────────┐           ┌───────────┐
  │ front → [B] [C] [D] ← back│  ─────▶  │  (empty)  │  ← event loop pushes
  └──────────────────────────┘           └───────────┘     front callback here
          ▲
          │ new callbacks join at the back when work finishes
       timer/I-O done

  Order of execution:  B  →  C  →  D      (first in, first out)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback queue | Line of ready callbacks | तैयार callbacks की लाइन |
| Task queue | Another name for the callback queue | Callback queue का दूसरा नाम |
| FIFO | First in, first out | पहले आया, पहले गया |
| Event loop | Moves callbacks from queue to stack | Callbacks को queue से stack पर लाने वाला |
| Macrotask | Task from timers, I/O, setImmediate | Timers और I/O का task |
| Yield | Let other work run before continuing | दूसरे कामों को मौका देना |
| Phase | Stage in one event loop cycle | Event loop चक्र का चरण |

---

## ⚡ 3-Line Summary
**English:**
1. Callback queue (task queue) पूरे हो चुके async callbacks को FIFO क्रम में रखती है।
2. Event loop तभी एक callback उठाता है जब call stack खाली हो, इसलिए lines में वे एक-एक करके चलते हैं।
3. लंबा callback पूरी queue रोकता है, इसलिए काम छोटा रखो और ज़रूरत पड़ने पर `setImmediate` से yield करो।

**Hindi:**
1. Callback queue (task queue) पूरे हो चुके async callbacks को FIFO क्रम में रखती है।
2. Event loop तभी एक callback उठाता है जब call stack खाली हो, इसलिए वे एक-एक करके चलते हैं।
3. लंबा callback पूरी queue रोकता है, इसलिए काम छोटा रखो और ज़रूरत पड़ने पर `setImmediate` से yield करो।

---

## ➡️ Next Topic
**74. Event Loop — Complete Guide** — यह पूरा चक्र समझेंगे: timers, pending I/O, poll, check और close phases, और microtasks कहाँ फिट होते हैं।
