# 74. Event Loop — Complete Guide
# हिंदी में: Event Loop — पूरा चक्र जो async code को चलाता है

---

## 🔵 Simple Definition (English)
The **event loop** is a repeating cycle that checks whether the call stack is empty and, if so, moves the next ready callback onto it. Node.js runs it in ordered phases (timers, pending callbacks, poll, check, close), and microtasks run between them.

## 🔵 सरल परिभाषा (Hindi)
**Event loop** एक लगातार चलने वाला चक्र है, जो देखता है कि call stack खाली है या नहीं, और खाली होने पर अगला तैयार callback उसपर डालता है। Node.js इसे क्रमबद्ध phases में चलाता है (timers, pending callbacks, poll, check, close), और microtasks इन phases के बीच में चलते हैं।

---

## 🔴 Problem it Solves
JavaScript एक thread पर चलती है, फिर भी server हज़ारों connections संभालता है। Event loop वह mechanism है जो एक thread को बार-बार अलग-अलग तैयार कामों पर लगाता है, बिना किसी काम को अटकाए। इसके बिना हर connection के लिए अलग thread चाहिए होता, जो memory और CPU दोनों महँगा पड़ता।

## 🔴 यह क्यों बना? (Hindi)
Zomato के backend पर एक ही समय पर हज़ारों requests आती हैं। हर request के लिए thread बनाना बहुत महँगा है। Event loop एक thread पर सारी तैयार requests के callbacks को क्रम से चलाता है। जो काम I/O में इंतज़ार कर रहा है, वह बीच में ही दूसरे काम के लिए रास्ता दे देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Timers phase: जिन timers की समय-सीमा पूरी हो गई, उनके callbacks चलते हैं
Step 2 → Pending callbacks phase: पिछले चक्र से बचे कुछ system callbacks चलते हैं
Step 3 → Poll phase: नए I/O events लिए जाते हैं और उनके callbacks चलते हैं (यहीं सबसे ज़्यादा इंतज़ार होता है)
Step 4 → Check phase: `setImmediate` के callbacks चलते हैं
Step 5 → Close phase: `socket.on("close")` जैसे cleanup callbacks चलते हैं, फिर चक्र दोबारा शुरू होता है
Note → हर phase के बीच और हर callback के बाद microtasks (`process.nextTick`, Promise) खाली किए जाते हैं

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Timers phase: समय पूरा हुए timers के callbacks चलते हैं
Step 2 → Pending callbacks phase: पिछले चक्र के कुछ system callbacks चलते हैं
Step 3 → Poll phase: नए I/O events लिए जाते हैं और उनके callbacks चलते हैं
Step 4 → Check phase: `setImmediate` के callbacks चलते हैं
Step 5 → Close phase: cleanup callbacks चलते हैं, फिर चक्र दोबारा शुरू होता है
नोट → हर phase के बीच microtasks (`process.nextTick`, Promise) पूरे खाली किए जाते हैं

---

## 🟡 Real World Example
Razorpay का webhook server हर सेकंड हज़ारों payment confirmations receive करता है। Poll phase में नए requests के callbacks आते हैं, timers phase में retry timers चलते हैं, और check phase में `setImmediate` से logs लिखे जाते हैं। एक ही thread पर यह सब क्रम से होता है, इसलिए server कम resources में चलता है।

## 🟡 Real Example Hindi mein
Razorpay का webhook server हर सेकंड हज़ारों payment confirmations लेता है। Poll phase में नए requests के callbacks आते हैं, timers phase में retry timers चलते हैं, और check phase में `setImmediate` से logs लिखे जाते हैं। यह सब एक thread पर क्रम से होता है, इसलिए server कम resources में चलता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: the order of sync code, nextTick, promises, and timers
// Run with: node 74-event-loop-complete-guide.js

console.log("1. sync start");                   // runs first, on the call stack

setTimeout(() => {
  console.log("5. timer (timers phase)");        // runs in the timers phase of a later cycle
}, 0);

Promise.resolve().then(() => {
  console.log("3. promise (microtask)");         // microtask: runs after sync code, before timers
});

process.nextTick(() => {
  console.log("2. nextTick (microtask, runs first)"); // nextTick queue is drained before promises
});

console.log("1b. sync end");                     // still synchronous, runs before any callback

// Output order: 1, 1b, 2, 3, 5
// Sync code finishes first, then the nextTick queue, then the promise queue,
// and only then does the event loop reach the timers phase.
```

## 💻 Code Example — Advanced
```javascript
// Goal: measure event loop lag, so you can detect when something blocks the loop

const { performance } = require("perf_hooks"); // high-resolution clock

// Monitor: schedules a timer every `interval` ms and measures how late it runs
function startLagMonitor(intervalMs, onLag) {
  let expected = performance.now() + intervalMs; // when the next tick should fire

  const timer = setInterval(() => {              // repeating timer in the timers phase
    const now = performance.now();               // actual time now
    const lag = now - expected;                  // how late we are (0 means on time)
    if (lag > 0) onLag(lag);                     // report any delay above zero
    expected = now + intervalMs;                 // schedule the next expected time
  }, intervalMs);

  timer.unref();                                  // do not keep the process alive just for this
  return () => clearInterval(timer);              // return a stop function
}

// Simulate a blocking task that freezes the loop for about 200 ms
function blockFor(ms) {
  const end = performance.now() + ms;            // end time for busy-wait
  while (performance.now() < end) {}             // synchronous: the loop cannot run anything else
}

let worstLag = 0;                                // track the biggest delay seen
const stop = startLagMonitor(10, (lag) => {      // check every 10 ms
  if (lag > worstLag) worstLag = lag;            // remember the worst lag
});

// After 50 ms, block the loop, then check the worst lag after recovering
setTimeout(() => {
  blockFor(200);                                 // freeze the loop for ~200 ms
  setTimeout(() => {
    stop();                                      // stop the monitor
    console.log("Lag detected (>= 150 ms):", worstLag >= 150); // true
  }, 50);
}, 50);
```

---

## 🟠 Express.js Integration
Express server पूरी तरह event loop पर चलता है। Route handler में CPU-heavy काम सीधे करोगे तो loop रुकेगा, और बाकी सारी requests अटकेंगी। नीचे का route लंबे काम को `setImmediate` से छोटे hunks में बाँटता है, ताकि हर chunk के बाद poll और check phases को मौका मिले। यह event loop को समझकर लिखा गया सही तरीका है।

```javascript
const express = require("express");          // web framework
const app = express();

// Route: sum a large range without freezing the event loop for every other request
app.get("/report/sum", (req, res) => {
  const limit = 5_000_000;                   // size of the CPU-heavy work
  let total = 0;                             // accumulator
  let i = 0;                                 // current position in the range

  function chunk() {
    const end = Math.min(i + 500_000, limit); // process up to 500k items per chunk
    for (; i < end; i++) total += i;         // small piece of CPU work
    if (i < limit) {
      setImmediate(chunk);                   // yield: let other requests run, then continue
    } else {
      res.json({ total });                   // finished: send the answer
    }
  }
  chunk();                                   // start the first chunk right away
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `process.nextTick` को हमेशा `setTimeout` से पहले पर सोचना, और यह भूल जाना कि nextTick और promise का अपना क्रम है
✅ **Correct:** Node में nextTick queue, promise microtasks से पहले खाली होता है। दोनों microtasks हैं, पर उनके queues अलग हैं।

```javascript
// Wrong: assuming promise always beats nextTick
Promise.resolve().then(() => console.log("promise"));
process.nextTick(() => console.log("nextTick"));
// Prints: nextTick, then promise (not promise first)

// Right: know the order and never depend on fragile ordering across modules
```

❌ **Mistake 2:** Recursive `process.nextTick` या promise चेन से I/O को भूखा रखना
✅ **Correct:** Microtasks तब तक चलते रहते हैं जब तक खाली न हों, इसलिए timers और I/O बीच में नहीं आते। Recursion को `setImmediate` से तोड़ो।

```javascript
// Wrong: this starves the event loop, the timer never gets its turn in time
function spin() {
  process.nextTick(spin);       // schedules itself forever
}
spin();

// Right: yield to the event loop with setImmediate
function spinSafe(n) {
  if (n === 0) return;
  setImmediate(() => spinSafe(n - 1)); // each step gives timers and I/O a chance
}
spinSafe(3);
```

❌ **Mistake 3:** Sync CPU work को Express handler में डालकर उम्मीद करना कि server responsive रहेगा
✅ **Correct:** Heavy CPU काम को chunks में बाँटो, या `worker_threads` में चलाओ।

```javascript
// Wrong: 3 seconds of computation freezes every other request
app.get("/slow", (req, res) => {
  let x = 0;
  for (let i = 0; i < 3e9; i++) x += i;
  res.send(String(x));
});

// Right: move heavy work to a worker thread, keep the loop free
// (see the chunked Express example above for a simpler approach)
```

---

## 🧠 Tricky Interview Question
```javascript
console.log("start");

setTimeout(() => {
  console.log("timeout 1");
  Promise.resolve().then(() => console.log("promise inside timeout 1"));
  process.nextTick(() => console.log("nextTick inside timeout 1"));
}, 0);

setTimeout(() => console.log("timeout 2"), 0);

Promise.resolve().then(() => console.log("promise"));
console.log("end");
```
**Answer:** `start`, `end`, `promise`, `timeout 1`, `nextTick inside timeout 1`, `promise inside timeout 1`, `timeout 2`।

- पहले सारा sync code: `start`, `end`।
- फिर microtasks: `promise` (main module के microtasks)।
- Timers phase में पहला callback `timeout 1` चलता है।
- Node 11+ में हर timer callback के बाद microtasks पूरे खाली होते हैं। इनमें पहले `nextTick` queue, फिर promise queue आती है, इसलिए `nextTick inside timeout 1` पहले और `promise inside timeout 1` बाद में।
- आख़िर में `timeout 2`, जो उसी timers phase में अगला callback है।

---

## ⚫ Interview Questions + Answers

Q1: Event loop क्या है?
A1: Event loop वह चक्र है जो देखता है कि call stack खाली है या नहीं, और खाली होने पर queues से अगला callback उठाकर चलाता है। इसी से single-threaded JavaScript एक साथ कई async कामों को संभालती है।

Q2: Node.js के event loop के phases कौन-से हैं?
A2: Timers, pending callbacks, poll, check (setImmediate), और close callbacks। हर phase का अपना callback queue होता है, और चक्र इसी क्रम में दोहराया जाता है।

Q3: `process.nextTick` और Promise microtask में क्या फर्क है?
A3: दोनों microtask हैं, पर nextTick queue, promise queue से पहले खाली होती है। इसलिए जब दोनों एक साथ queue हों, nextTick पहले चलता है।

Q4: Event loop कब block होता है?
A4: जब कोई synchronous काम (लंबा loop, `readFileSync`, heavy JSON parse) call stack को लंबे समय तक रोक दे। तब timers और I/O callbacks देर से चलते हैं।

Q5: `setImmediate` और `setTimeout(0)` का अंतर event loop के संदर्भ में क्या है?
A5: `setTimeout(0)` timers phase में चलता है, और `setImmediate` check phase में। Main module में उनका क्रम अनिश्चित है, पर I/O callback के अंदर `setImmediate` हमेशा पहले चलता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High concurrency वाले I/O servers बनाने हों
- Short, non-blocking callbacks और promises से काम करना हो
- Lag monitoring या performance debugging करनी हो

❌ Avoid when:
- Heavy CPU computation को सीधे main thread पर चलाना हो
- Recursive microtasks या nextTick chains बनानी हों
- Event loop की ordering पर ऐसे code के भरोसे रहना हो जो फ़्रेज़ाइल हो

---

## 📊 Visual Diagram
```
   ┌───────────────────────────┐
┌─▶│ timers (setTimeout/Interval)│
│  └──────────────┬────────────┘
│  ┌──────────────▼────────────┐
│  │ pending callbacks (system) │
│  └──────────────┬────────────┘
│  ┌──────────────▼────────────┐
│  │ poll (new I/O, waits here) │
│  └──────────────┬────────────┘
│  ┌──────────────▼────────────┐
│  │ check (setImmediate)       │
│  └──────────────┬────────────┘
│  ┌──────────────▼────────────┐
└──┤ close (socket.on('close')) │
   └───────────────────────────┘

 Between every phase and every callback:
   drain process.nextTick queue  →  drain Promise microtask queue
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Repeating cycle that runs callbacks | Callbacks चलाने वाला चक्र |
| Phase | One stage of the loop | Loop का एक चरण |
| Poll phase | Waits for and handles new I/O | नए I/O का इंतज़ार और संभालना |
| Check phase | Runs setImmediate callbacks | setImmediate चलाने का चरण |
| nextTick queue | Microtask queue with highest priority | सबसे पहले चलने वाली microtask queue |
| Microtask | Promise and nextTick callback | Promise और nextTick का callback |
| Lag | Delay between expected and actual run time | तय समय और असली समय का फर्क |

---

## ⚡ 3-Line Summary
**English:**
1. Event loop phases में चलता है: timers, pending, poll, check, close, और हर step के बीच microtasks खाली होते हैं।
2. Microtasks (nextTick, then Promise) callbacks से पहले चलते हैं, और nextTick का queue पहले खाली होता है।
3. लंबा sync काम loop को रोकता है, इसलिए chunking या worker threads से loop को free रखो।

**Hindi:**
1. Event loop phases में चलता है: timers, pending, poll, check, close, और हर step के बीच microtasks खाली होते हैं।
2. Microtasks (nextTick, then Promise) callbacks से पहले चलते हैं, और nextTick का queue पहले खाली होता है।
3. लंबा sync काम loop को रोकता है, इसलिए chunking या worker threads से loop को free रखो।

---

## ➡️ Next Topic
**75. Microtask Queue vs Macrotask Queue** — यह देखेंगे कि promise callbacks और timer callbacks एक-दूसरे से कब आगे-पीछे होते हैं।
