# 72. Web APIs
# हिंदी में: Web APIs — Timers, Network और I/O call stack से बाहर कैसे चलते हैं

---

## 🔵 Simple Definition (English)
**Web APIs** are capabilities provided by the runtime outside the JavaScript engine, such as timers, network requests, and DOM events in the browser. In Node.js the same idea exists as libuv-backed APIs (timers, fs, net) and the global `fetch`. They do the waiting work so the call stack does not have to.

## 🔵 सरल परिभाषा (Hindi)
**Web APIs** वे सुविधाएँ हैं जो JavaScript engine के बाहर, runtime देता है, जैसे browser में timers, network requests और DOM events। Node.js में वही idea libuv पर बने APIs (timers, fs, net) और global `fetch` के रूप में है। असली इंतज़ार का काम ये संभालते हैं, ताकि call stack न रुके।

---

## 🔴 Problem it Solves
JavaScript engine (V8) खुद timer गिनना या network packet का इंतज़ार करना नहीं जानता। अगर engine यह काम अपने main thread पर करे, तो पूरी app जमी रहेगी। इसलिए runtime के पास ये capabilities अलग से हैं। Engine सिर्फ "यह काम शुरू करो और जब हो जाए तो मुझे callback दो" कहता है।

## 🔴 यह क्यों बना? (Hindi)
Engine में timer या network नहीं होता। अगर Zomato पर restaurant location लेने के लिए geolocation का इंतज़ार main thread पर हो, तो UI रुक जाएगा। Runtime के Web APIs यह इंतज़ार बाहर संभालते हैं और काम पूरा होने पर callback वापस भेजते हैं। इससे engine हमेशा दूसरे काम के लिए खाली रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Code `setTimeout(cb, 500)` या `fetch(url)` call करता है
Step 2 → Engine इस call को runtime के Web API को सौंप देता है और call stack से तुरंत हट जाता है
Step 3 → Runtime timer या network operation को अपने तरीके से चलाता है (browser threads या libuv)
Step 4 → काम पूरा होने पर runtime callback को callback queue में डालता है
Step 5 → Event loop, call stack खाली होने पर वह callback stack पर लाता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कोड `setTimeout(cb, 500)` या `fetch(url)` call करता है
Step 2 → Engine यह काम runtime के Web API को सौंप देता है और call stack खाली कर देता है
Step 3 → Runtime timer या network काम को अपने तरीके से चलाता है
Step 4 → काम पूरा होने पर callback को queue में डाला जाता है
Step 5 → Event loop call stack खाली होते ही वह callback stack पर लाता है

---

## 🟡 Real World Example
Razorpay checkout में payment status poll करने के लिए `fetch` और timer दोनों चाहिए। `fetch` network से जवाब माँगता है, और `setTimeout` अगले poll से पहले रुकता है। ये दोनों runtime के Web APIs हैं। अगर ये engine के अंदर blocking तरीके से चलते, तो checkout page हर poll पर freeze हो जाता।

## 🟡 Real Example Hindi mein
Razorpay checkout में payment status बार-बार check करने के लिए `fetch` और timer दोनों चाहिए। `fetch` network से जवाब माँगता है और `setTimeout` अगले poll से पहले इंतज़ार करता है। ये दोनों runtime के Web APIs हैं। अगर ये blocking चलते, तो हर poll पर page जम जाता।

---

## 💻 Code Example — Basic
```javascript
// Demo: timers and file I/O are handled by the runtime, not by the call stack
// Run with: node 72-web-apis.js
const fs = require("fs");                       // Node's built-in file system module

console.log("1. Start");                        // sync: runs first

// setTimeout is a runtime timer: the engine hands off the waiting
setTimeout(() => {
  console.log("3. Timer fired after 100 ms");   // runs from the callback queue later
}, 100);

// fs.readFile is an I/O task: libuv does the disk read in the background
fs.readFile(__filename, "utf8", (err, data) => { // __filename = this file's path
  if (err) {
    console.log("File error:", err.message);    // handle errors first (error-first callback)
    return;
  }
  console.log("4. File read done, bytes:", data.length); // data.length > 0
});

console.log("2. Still running sync code");       // sync: runs before any callback

// Expected order: 1, 2, then the callbacks in whichever order they finish.
// The file read finishes quickly, so "4" usually comes before "3" here,
// but the order of "3" vs "4" is not guaranteed; the sync lines 1 and 2 are.
```

## 💻 Code Example — Advanced
```javascript
// Goal: a cancellable timer and a safe file read, both using runtime APIs
const { setTimeout: sleep } = require("timers/promises"); // promise-based timer
const fs = require("fs/promises");                        // promise-based file API

// Helper: run any promise with an AbortController so it can be cancelled
async function withCancel() {
  const controller = new AbortController();              // controller owns the cancel signal
  const timer = sleep(5000, "finished", { signal: controller.signal }); // long timer

  setTimeout(() => controller.abort(), 50);              // cancel after 50 ms

  try {
    const value = await timer;                           // wait for the timer
    console.log("Timer value:", value);                  // not printed when cancelled
  } catch (err) {
    // AbortError is thrown when the signal fires before the timer completes
    console.log("Cancelled:", err.name === "AbortError"); // Cancelled: true
  }
}

// Helper: read a file safely, returning a fallback instead of crashing
async function readConfig(path) {
  try {
    const raw = await fs.readFile(path, "utf8");        // non-blocking runtime I/O
    return JSON.parse(raw);                             // parse the JSON text
  } catch (err) {
    if (err.code === "ENOENT") {                        // ENOENT = file does not exist
      return { theme: "light" };                        // safe default config
    }
    throw err;                                          // any other error goes up
  }
}

async function main() {
  await withCancel();                                   // demo the cancellable timer
  const cfg = await readConfig("./definitely-missing.json"); // file does not exist
  console.log("Config:", cfg);                          // { theme: 'light' }
}

main().catch((err) => console.error("Fatal:", err));    // catch anything unexpected
```

---

## 🟠 Express.js Integration
Express route में `fetch` (Node 18+ का global Web API) लगभग हर बार external service को call करता है, जैसे payment gateway या weather API। `fetch` खुद background में network चलाता है, और `await` के बाद handler आगे बढ़ता है। नीचे का route एक external API को call करता है और timeout के लिए `AbortSignal.timeout` का इस्तेमाल करता है। यह भी Web API है, जो runtime देता है।

```javascript
const express = require("express");          // web framework
const app = express();

// Route calls an external Web API (global fetch) and waits without blocking the server
app.get("/weather/:city", async (req, res, next) => {
  try {
    const url = `https://api.example.com/weather?city=${encodeURIComponent(req.params.city)}`;
    const upstream = await fetch(url, {
      signal: AbortSignal.timeout(3000),    // abort the network call after 3 seconds
    });
    if (!upstream.ok) {                     // check HTTP status (fetch does not throw on 404/500)
      return res.status(502).json({ error: "Upstream failed" }); // bad gateway
    }
    const data = await upstream.json();     // parse the JSON body
    res.json(data);                         // forward result to our client
  } catch (err) {
    next(err);                              // timeouts and network errors go to error middleware
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Browser के `setTimeout` की तरह Node के timer को भी number समझना
✅ **Correct:** Node में `setTimeout` एक `Timeout` object लौटाता है (browser में number)। Cancel के लिए उसी object को `clearTimeout` को दो।

```javascript
// Wrong: expecting a number and comparing it
const id = setTimeout(() => {}, 100);
console.log(typeof id);     // "object" in Node, not "number"

// Right: keep the returned handle and cancel with it
const handle = setTimeout(() => console.log("never"), 100);
clearTimeout(handle);       // cancels the pending timer
```

❌ **Mistake 2:** `fetch` को error मानना जब HTTP status 404 या 500 हो
✅ **Correct:** `fetch` केवल network failure पर reject होता है। HTTP status को `response.ok` से खुद जाँचो।

```javascript
// Wrong: assumes a 500 response throws
try {
  const r = await fetch("https://api.example.com/order/1");
  const order = await r.json();  // runs even when r.status is 500
} catch (err) {
  console.log("never happens for HTTP 500");
}

// Right: check r.ok explicitly
const r = await fetch("https://api.example.com/order/1");
if (!r.ok) throw new Error(`HTTP ${r.status}`); // turn bad status into an error
const order = await r.json();
```

❌ **Mistake 3:** Timer पर blocking loop चलाकर उम्मीद करना कि timer ठीक समय पर चलेगा
✅ **Correct:** Timer का callback तभी चलता है जब main thread खाली हो। लंबा sync loop उसे देर से चलाएगा।

```javascript
// Wrong: the 100 ms timer is delayed by the busy loop below
setTimeout(() => console.log("should be 100 ms"), 100);
const end = Date.now() + 500;
while (Date.now() < end) {}     // blocks for 500 ms; timer runs after this

// Right: break big work into chunks, or move it to a worker thread
```

---

## 🧠 Tricky Interview Question
```javascript
const start = Date.now();                              // remember when we started

setTimeout(() => {
  // Timer asked for 100 ms, but it can only run after the main thread is free
  console.log("sync finished:", Date.now() - start >= 300);
  console.log("timer ran:", true);
}, 100);

// Block the main thread for about 300 ms with synchronous work
while (Date.now() - start < 300) {}

console.log("sync done");                              // what gets printed, and in which order?
```
**Answer:** पहले `sync done` आता है, फिर `sync finished: true`, और फिर `timer ran: true`। Web API ने 100 ms का timer तो शुरू किया, पर callback तभी चल सकता है जब call stack खाली हो। Loop 300 ms तक main thread रोकता है, इसलिए timer की "100 ms" वाली मंशा पूरी नहीं होती और callback 300 ms के बाद ही चलता है। Timer delay की guarantee देता है कि "कम से कम इतनी देर बाद", ठीक समय की नहीं।

---

## ⚫ Interview Questions + Answers

Q1: Web APIs क्या हैं और JavaScript engine इन्हें क्यों इस्तेमाल करता है?
A1: Web APIs runtime (browser या Node.js) द्वारा दी गई सुविधाएँ हैं, जैसे timers, network और file I/O। Engine में ये नहीं होते, इसलिए engine इन्हें runtime को सौंपता है ताकि main thread busy न हो।

Q2: `setTimeout` के callback को तुरंत क्यों नहीं चलाया जाता?
A2: Timer शुरू होने के बाद callback को callback queue में रखा जाता है। वह तभी चलता है जब call stack खाली हो और event loop उसे उठाए। इसलिए delay कम से कम उतना होता है, ठीक उतना नहीं।

Q3: Node.js में browser के Web APIs का equivalent क्या है?
A3: Timers और I/O के लिए libuv और उसके ऊपर Node के APIs (`timers`, `fs`, `net`) हैं। Global `fetch` भी उपलब्ध है, जो Web Fetch standard के अनुसार है। Concept एक जैसा है, implementation अलग है।

Q4: `AbortController` का use क्या है?
A4: `AbortController` किसी async काम को बाहर से cancel करने देता है। `signal` को `fetch` या `timers/promises` में pass करके `abort()` करने पर वह काम `AbortError` के साथ reject हो जाता है।

Q5: `fetch` कब reject होता है?
A5: केवल network failure, DNS error, या abort होने पर। HTTP 404 या 500 पर `fetch` resolve होता है, इसलिए `response.ok` खुद चेक करना होता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Timers, network calls या file I/O जैसे waiting वाले काम हों
- Long-running काम को cancel या timeout करना हो (AbortController के साथ)
- Browser और Node दोनों में एक जैसा code चाहिए (fetch, timers)

❌ Avoid when:
- Pure computation हो, जिसे Web API की ज़रूरत ही नहीं
- Timer की exact accuracy पर भरोसा करना हो
- Blocking Node API (जैसे `readFileSync`) server request handler के अंदर इस्तेमाल करना हो

---

## 📊 Visual Diagram
```
  YOUR CODE (call stack)            RUNTIME (Web APIs / libuv)          QUEUE
  ─────────────────────            ──────────────────────────          ─────
  setTimeout(cb, 100)  ──────────▶  timer starts (100 ms)
  fs.readFile(p, cb)   ──────────▶  disk read in background
  console.log("sync") ✔ runs now
  stack empty
                                    timer done  ──────────────────▶  [cb timer]
                                    read done   ──────────────────▶  [cb timer, cb read]
  event loop: stack empty? ──────────────────────────────────────────▶ take cb, push on stack
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Web API | Runtime-provided capability outside the engine | Runtime द्वारा दी गई सुविधा |
| libuv | C library behind Node's async I/O and timers | Node का async I/O engine |
| Callback queue | Holds finished callbacks waiting for the stack | पूरे हुए callbacks की लाइन |
| fetch | Global API for HTTP requests | HTTP request करने का global API |
| AbortController | Object to cancel async operations | Async काम को रोकने का साधन |
| AbortSignal.timeout | Signal that aborts after given ms | तय समय बाद अपने-आप cancel होने वाला signal |
| Timeout handle | Object returned by setTimeout in Node | Node में timer की पहचान |

---

## ⚡ 3-Line Summary
**English:**
1. Web APIs runtime की capabilities हैं, जैसे timers, network और file I/O, जो engine के बाहर चलती हैं।
2. Engine इन्हें शुरू करके call stack खाली कर देता है, और पूरे हुए callbacks queue से वापस आते हैं।
3. Timer की delay "कम से कम" होती है, और external calls के लिए `response.ok` व `AbortSignal.timeout` ज़रूरी हैं।

**Hindi:**
1. Web APIs runtime की सुविधाएँ हैं, जैसे timers, network और file I/O, जो engine के बाहर चलती हैं।
2. Engine इन्हें शुरू करके call stack खाली कर देता है, और पूरे हुए callbacks queue से वापस आते हैं।
3. Timer की delay "कम से कम" होती है, और external calls के लिए `response.ok` व `AbortSignal.timeout` ज़रूरी हैं।

---

## ➡️ Next Topic
**73. Callback Queue (Task Queue)** — जानेंगे कि पूरे हुए callbacks किस क्रम में लाइन में लगते हैं और event loop उन्हें कैसे चुनता है।
