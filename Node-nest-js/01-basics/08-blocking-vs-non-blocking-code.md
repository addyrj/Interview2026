# 08. Blocking vs Non-Blocking Code
# हिंदी में: Blocking vs Non-Blocking Code

---

## 🔵 Simple Definition (English)
**Blocking code** occupies the single JS thread until it finishes, preventing anything else from running. **Non-blocking code** starts an operation, immediately returns control to the Event Loop, and finishes later via a callback/promise — letting other code run in the meantime.

## 🔵 सरल परिभाषा (Hindi)
**Blocking code** single JS thread को तब तक occupy रखता है जब तक वह पूरा न हो जाए, तब तक कुछ और नहीं चल सकता। **Non-blocking code** operation शुरू करके तुरंत control Event Loop को वापस दे देता है, और बाद में callback/promise से पूरा होता है — बीच में बाकी code चल सकता है।

---

## 🔴 Problem it Solves
In a single-threaded runtime, if every operation were blocking (like traditional synchronous file/network calls), Node.js could only ever do ONE thing at a time, server-wide — completely defeating the purpose of using Node for concurrent servers. Non-blocking APIs let one thread juggle thousands of in-flight operations by never waiting idle on any single one.

## 🔴 यह क्यों बना? (Hindi)
Single-threaded runtime में अगर हर operation blocking होता (traditional sync file/network calls जैसे), तो Node.js पूरे server में एक समय पर सिर्फ एक काम कर पाता — concurrent servers के लिए Node use करने का मतलब ही खत्म हो जाता। Non-blocking APIs एक thread को हज़ारों in-flight operations juggle करने देते हैं, किसी एक पर idle wait किए बिना।

---

## 🟢 How it Works — Step by Step

Step 1 → A **blocking** call (e.g., `fs.readFileSync`) invokes the OS, and the JS thread literally pauses/waits until the OS returns data — no other JS can run during this time.
Step 2 → A **non-blocking** call (e.g., `fs.readFile`) invokes the OS/libuv, registers a callback, and returns IMMEDIATELY — the JS thread moves to the next line of code right away.
Step 3 → The actual I/O work (disk read, network wait) happens in the background (thread pool or OS async mechanism) while your JS thread continues running other code.
Step 4 → When the I/O finishes, the result is placed in the Event Loop's queue as a task/microtask.
Step 5 → The Event Loop picks up that task when it's JS's turn again (after the current synchronous code block finishes), and runs your callback with the result.
Step 6 → `async/await` is syntactic sugar over this same non-blocking mechanism — `await` doesn't block the thread, it just pauses that specific async function until its Promise resolves, while OTHER code can run.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Blocking** call (जैसे `fs.readFileSync`) OS को call करता है, और JS thread literally रुक जाता है जब तक OS data वापस न दे — इस दौरान कोई और JS नहीं चल सकता।
Step 2 → **Non-blocking** call (जैसे `fs.readFile`) OS/libuv को call करता है, callback register करता है, और तुरंत return हो जाता है — JS thread अगली line पर चला जाता है।
Step 3 → असली I/O काम (disk read, network wait) background में होता है (thread pool या OS mechanism) जबकि JS thread बाकी code चलाता रहता है।
Step 4 → I/O पूरा होने पर उसका result Event Loop की queue में task/microtask के रूप में रखा जाता है।
Step 5 → Event Loop जब JS की बारी आती है (current sync code खत्म होने के बाद) उस task को उठाता है और callback को result के साथ run करता है।
Step 6 → `async/await` इसी non-blocking mechanism के ऊपर syntactic sugar है — `await` thread को block नहीं करता, सिर्फ उस async function को रोकता है जब तक Promise resolve न हो, बाकी code चल सकता है।

---

## 🟡 Real World Example
**Flipkart checkout page:** When you click "Place Order," the backend needs to: verify inventory (DB call), charge payment (external API call), and send a confirmation email (another API call). If written with blocking calls, each step would freeze the server for ALL other shoppers for the full duration of that network round-trip. Written non-blocking (async/await with proper I/O APIs), the single Node.js thread keeps serving other shoppers' requests while each of your checkout's steps waits in the background.

## 🟡 Real Example Hindi mein
**Flipkart checkout page:** "Place Order" click करने पर backend को: inventory verify करना है (DB call), payment charge करना है (external API), और confirmation email भेजना है (एक और API)। Blocking calls से लिखा गया हो तो हर step पूरे server को बाकी सभी shoppers के लिए उस network round-trip जितनी देर freeze कर देगा। Non-blocking (async/await सही I/O APIs के साथ) लिखा हो तो single Node.js thread बाकी shoppers के requests serve करता रहता है जबकि आपका checkout background में wait करता है।

---

## 💻 Code Example — Basic
```javascript
// blocking-vs-nonblocking-basic.js
const fs = require('fs');

console.log('=== BLOCKING DEMO ===');
console.log('Before blocking read');
const dataSync = fs.readFileSync(__filename, 'utf8'); // THREAD PAUSES here
console.log('After blocking read (nothing else could run during this)');
console.log('File length:', dataSync.length);

console.log('\n=== NON-BLOCKING DEMO ===');
console.log('Before non-blocking read');
fs.readFile(__filename, 'utf8', (err, data) => {
  // This runs LATER — thread was free to do other things meanwhile
  console.log('Non-blocking read finished, length:', data.length);
});
console.log('After non-blocking read call (this prints BEFORE the callback above!)');
// Proof: this line executes before the readFile callback, because readFile
// didn't make the thread wait.
```

## 💻 Code Example — Advanced
```javascript
// blocking-vs-nonblocking-advanced.js
// Measures REAL impact: blocking delays a concurrent "heartbeat" timer

let tickCount = 0;
const heartbeat = setInterval(() => {
  tickCount++;
  console.log(`Heartbeat tick ${tickCount} at ${Date.now()}`);
}, 100);

// ─── BLOCKING: busy-wait for 1 second ─────────────────────────────────────────
function blockFor(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {} // occupies the thread completely
}

// ─── NON-BLOCKING: wait 1 second without occupying the thread ───────────────
function waitFor(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function demo() {
  console.log('--- Starting BLOCKING 1s wait ---');
  blockFor(1000);
  console.log('--- Blocking wait done (heartbeat ticks were DELAYED/skipped) ---');

  console.log('--- Starting NON-BLOCKING 1s wait ---');
  await waitFor(1000);
  console.log('--- Non-blocking wait done (heartbeat ticks kept firing on time) ---');

  clearInterval(heartbeat);
}

demo();
// Observe: during blockFor(1000), heartbeat ticks are DELAYED because the
// thread is busy. During waitFor(1000) (await on setTimeout), heartbeat
// ticks fire normally because the thread is free to run them.
```

---

## 🟠 Express.js Integration
```javascript
// Express: same endpoint logic, blocking vs non-blocking implementations
const express = require('express');
const fs = require('fs');
const app = express();

// BLOCKING version — freezes server for ALL users during the read
app.get('/report-blocking', (req, res) => {
  const data = fs.readFileSync('./large-file.csv', 'utf8'); // blocks everyone
  res.send(`Report size: ${data.length}`);
});

// NON-BLOCKING version — server stays responsive to other requests
app.get('/report-nonblocking', async (req, res) => {
  const data = await fs.promises.readFile('./large-file.csv', 'utf8');
  res.send(`Report size: ${data.length}`);
});

app.get('/ping', (req, res) => res.send('pong')); // use this to test responsiveness

app.listen(3000, () => {
  console.log('Hit /report-blocking then /ping quickly — /ping will be delayed.');
  console.log('Hit /report-nonblocking then /ping quickly — /ping responds instantly.');
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `*Sync` file/crypto functions in a server's hot request path
```javascript
// Wrong — blocks ALL concurrent requests during the operation
app.post('/upload', (req, res) => {
  fs.writeFileSync('./uploads/file.txt', req.body.content);
  res.send('Saved');
});

// Correct — non-blocking, server stays available for others
app.post('/upload', async (req, res) => {
  await fs.promises.writeFile('./uploads/file.txt', req.body.content);
  res.send('Saved');
});
```

❌ Mistake 2: Running heavy synchronous JSON parsing/stringifying on large payloads in a request handler
```javascript
// Wrong — JSON.parse/stringify on huge data is synchronous CPU work, blocks thread
app.post('/import', (req, res) => {
  const huge = JSON.parse(req.body.hugeJsonString); // could take seconds on big payloads
  res.json({ count: huge.length });
});

// Correct — offload to a worker thread for genuinely large payloads
const { Worker } = require('worker_threads');
app.post('/import', (req, res) => {
  const worker = new Worker('./parse-worker.js', { workerData: req.body.hugeJsonString });
  worker.on('message', (count) => res.json({ count }));
});
```

---

## 🧠 Tricky Interview Question

```javascript
console.log('Start');

setTimeout(() => console.log('Timeout'), 0);

for (let i = 0; i < 3_000_000_000; i++) {} // heavy sync loop

console.log('End');
```
Answer: Output is `Start`, then a LONG pause (during the loop), then `End`, then finally `Timeout`. Even though `setTimeout` was scheduled with `0` delay, it's non-blocking — it just registers a callback. But the heavy `for` loop is blocking synchronous code; it must finish completely before the Event Loop gets a chance to process the timer callback, no matter how small the requested delay was.

---

## ⚫ Interview Questions + Answers

Q1: What makes a function "blocking" in Node.js?
A1: A function is blocking if it performs its work synchronously on the main thread, occupying the single JS thread until the entire operation completes — e.g., `fs.readFileSync`, a CPU-heavy loop, or `JSON.parse` on a massive string.

Q2: Is `await` blocking?
A2: No, not the thread. `await` pauses only the current `async` function until its Promise settles; the Event Loop is free to run other code (other requests, timers, callbacks) during that wait. It "feels" synchronous in your code's structure but is non-blocking at the thread level.

Q3: Name Node.js APIs that come in both blocking and non-blocking variants.
A3: `fs.readFileSync` vs `fs.readFile`/`fs.promises.readFile`, `crypto.pbkdf2Sync` vs `crypto.pbkdf2`, `zlib.gzipSync` vs `zlib.gzip`. The `Sync` suffix is Node's convention for the blocking version.

Q4: Why is `JSON.parse` considered a blocking operation even though it's "just parsing"?
A4: Because it runs entirely synchronously on the main thread — for small payloads this is negligible, but for very large JSON strings (megabytes), parsing can take enough time to noticeably stall the Event Loop for all concurrent requests.

Q5: How do you detect if your Node.js app is blocking the Event Loop in production?
A5: Monitor Event Loop lag/delay with tools like `perf_hooks.monitorEventLoopDelay()`, APM tools (New Relic, Datadog), or the `clinic`/`0x` profilers; a healthy app should show sub-millisecond to low-millisecond Event Loop lag under load.

---

## 🔷 When to Use + When Not to Use
✅ Use non-blocking when:
- Handling any I/O in a server request path (file, DB, network) — always prefer async APIs

❌ Blocking (`*Sync`) is acceptable only when:
- Running one-off scripts/CLI tools at startup (e.g., reading a config file once before the server starts listening) where there are no concurrent requests to protect

---

## 📊 Visual Diagram
```
BLOCKING                           NON-BLOCKING
──────────────                     ──────────────────
Thread: [=====WAIT=====][code]     Thread: [code][code][code]...
         (frozen, nothing          (keeps running other things
          else can run)             while I/O happens elsewhere)
                                           │
                                           ▼
                                   [ libuv / OS doing I/O ]
                                           │
                                           ▼
                                   callback queued → runs
                                   when thread is free
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blocking | Code that halts the thread until done | Thread को तब तक रोकने वाला code |
| Non-blocking | Code that returns immediately, finishes later | तुरंत return होने वाला, बाद में पूरा होने वाला code |
| Sync API | Blocking variant (`*Sync` functions) | Blocking variant वाले functions |
| Async API | Non-blocking variant (callback/Promise based) | Non-blocking variant (callback/Promise आधारित) |
| Event Loop lag | Delay caused by blocked thread | Blocked thread से होने वाली delay |

---

## ⚡ 3-Line Summary
English:
1. Blocking code occupies the single JS thread until finished, freezing everything else; non-blocking code returns immediately and finishes later via callback/Promise.
2. Node's core modules offer both variants (`readFileSync` vs `readFile`) — always prefer the non-blocking one inside servers.
3. `await` is non-blocking at the thread level even though it reads like synchronous code — only genuinely synchronous CPU work blocks the Event Loop.

Hindi:
1. Blocking code single JS thread को पूरा होने तक occupy रखता है, बाकी सब freeze हो जाता है; non-blocking code तुरंत return होकर बाद में callback/Promise से पूरा होता है।
2. Node के core modules दोनों variants देते हैं (`readFileSync` vs `readFile`) — server के अंदर हमेशा non-blocking वाला इस्तेमाल करें।
3. `await` thread-level पर non-blocking है भले ही code sync जैसा दिखे — सिर्फ genuinely synchronous CPU काम Event Loop को block करता है।

---

## ➡️ Next Topic
**09. Synchronous vs Asynchronous in Node** — Deepen the blocking/non-blocking distinction into the broader sync vs async programming model, including callbacks, promises, and async/await.
