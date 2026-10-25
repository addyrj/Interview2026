# 70. Synchronous vs Asynchronous
# हिंदी में: Synchronous बनाम Asynchronous — कोड कब रुकता है और कब नहीं

---

## 🔵 Simple Definition (English)
**Synchronous** code runs line by line, and each line waits for the previous one to finish. **Asynchronous** code starts a task now, lets it run in the background, and continues with the next line without waiting.

## 🔵 सरल परिभाषा (Hindi)
**Synchronous** कोड एक-एक line करके चलता है, और हर line अपनी पिछली line खत्म होने का इंतज़ार करती है। **Asynchronous** कोड अभी एक task शुरू करता है, उसे background में चलने देता है, और बिना रुके अगली line पर चला जाता है।

---

## 🔴 Problem it Solves
JavaScript के पास एक ही main thread है। अगर हर काम synchronous हो, तो database से data आने तक पूरा server या browser freeze हो जाएगा। Zomato पर सोचो: अगर एक user का restaurant list load होते समय बाकी सारे users की requests रुक जाएँ, तो app unusable हो जाएगा। Asynchronous model से main thread free रहता है और waiting का काम runtime संभाल लेता है।

## 🔴 यह क्यों बना? (Hindi)
JavaScript में सिर्फ एक main thread होता है। अगर database, network या file जैसे धीमे कामों को synchronous रखा जाए, तो जब तक जवाब नहीं आता, पूरा program अटका रहेगा। जैसे Swiggy पर हज़ारों orders एक साथ आते हैं, वैसे ही server को एक request के इंतज़ार में बाकी requests नहीं रोकनी चाहिए। इसलिए async model बना, ताकि waiting के दौरान भी काम चलता रहे।

---

## 🟢 How it Works — Step by Step

Step 1 → Code ऊपर से नीचे चलता है और हर line call stack पर जाकर तुरंत खत्म होती है (synchronous)
Step 2 → कोई async काम (जैसे `setTimeout`, file read, HTTP call) आता है, तो उसे runtime को सौंप दिया जाता है
Step 3 → Main thread बाकी synchronous lines चलाता रहता है, बिना उस काम का इंतज़ार किए
Step 4 → जब async काम पूरा होता है, उसका callback या `then` queue में जाता है
Step 5 → Call stack खाली होने पर event loop वह callback उठाकर चलाता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कोड ऊपर से नीचे चलता है, हर line तुरंत पूरी होती है (synchronous)
Step 2 → कोई async काम (जैसे `setTimeout`, file read, HTTP call) आए, तो उसे runtime को दे दिया जाता है
Step 3 → Main thread बिना रुके बाकी synchronous lines चलाता है
Step 4 → काम पूरा होने पर उसका callback या `then` queue में चला जाता है
Step 5 → Call stack खाली होने पर event loop वह callback उठाकर चलाता है

---

## 🟡 Real World Example
Razorpay पर payment करते समय: (1) card details validate करना synchronous हो सकता है, लेकिन (2) bank को API call करके payment confirm करना asynchronous है। अगर यह call synchronous होती, तो उसी server पर दूसरे merchants की payments तब तक रुकी रहतीं जब तक bank जवाब नहीं देता। Async होने से server इस दौरान दूसरी requests संभालता है।

## 🟡 Real Example Hindi mein
Razorpay पर payment करते समय: card details की validation तुरंत हो सकती है (sync), लेकिन bank से payment confirm करने की API call async होती है। अगर यह call sync होती, तो server उस एक bank response तक दूसरे merchants की सभी payments रोक देता। Async होने से server उसी समय बाकी requests संभालता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: synchronous vs asynchronous execution order
// Run with: node 70-synchronous-vs-asynchronous.js

console.log("Step 1: Order placed");        // sync — runs immediately, first

// setTimeout schedules a callback to run LATER, after the delay
setTimeout(() => {
  console.log("Step 3: Restaurant accepted order"); // async — runs after all sync code
}, 1000);                                   // delay of 1000 ms (1 second)

console.log("Step 2: Customer keeps browsing"); // sync — runs BEFORE the timer fires

// A blocking (synchronous) helper that freezes the thread for `ms` milliseconds
function blockFor(ms) {
  const end = Date.now() + ms;              // compute the time when we should stop
  while (Date.now() < end) {}               // busy-wait: nothing else can run meanwhile
}

// Uncomment the line below to see the freeze effect on other work:
// blockFor(3000); // would delay the timer callback by about 3 seconds extra
```

## 💻 Code Example — Advanced
```javascript
// Simulate an I/O call (database, HTTP, file) that takes `ms` milliseconds
function fakeIO(name, ms, shouldFail = false) {
  return new Promise((resolve, reject) => {  // promise settles later, not now
    setTimeout(() => {                       // Node timer does the waiting, not our code
      if (shouldFail) {
        reject(new Error(`${name} failed`)); // reject = async error path
      } else {
        resolve(`${name} done`);             // resolve = async success path
      }
    }, ms);
  });
}

async function main() {
  // ── 1. SEQUENTIAL: each await waits for the previous one ──
  const seqStart = Date.now();               // record start time in ms
  const menu = await fakeIO("menu", 300);    // pause here until menu is ready (~300ms)
  const rating = await fakeIO("rating", 300); // then wait another ~300ms
  const seqTime = Date.now() - seqStart;     // total time, roughly 600ms
  console.log(menu, "|", rating);

  // ── 2. CONCURRENT: start both first, then wait for both together ──
  const concStart = Date.now();
  const [m2, r2] = await Promise.all([       // both timers run at the same time
    fakeIO("menu", 300),
    fakeIO("rating", 300),
  ]);
  const concTime = Date.now() - concStart;   // roughly 300ms
  console.log(m2, "|", r2);
  console.log("concurrent is faster:", concTime < seqTime); // true

  // ── 3. ERROR HANDLING: async errors must be caught with try/catch + await ──
  try {
    await fakeIO("payment", 100, true);     // this will reject
  } catch (err) {                            // the rejection lands here
    console.log("Caught:", err.message);     // Caught: payment failed
  }
}

// Top-level call: main() returns a promise, so attach .catch for safety
main().catch((err) => console.error("Unexpected:", err));
```

---

## 🟠 Express.js Integration
Express route handlers ज़्यादातर I/O (database, file, external API) छूते हैं, इसलिए उन्हें async होना ही चाहिए। नीचे का route `fs/promises` से file पढ़ता है। `readFile` के दौरान server दूसरी requests संभालता रहता है। Express 5 में `async` handler से throw हुआ error अपने-आप `next(err)` में चला जाता है। Express 4 में `try/catch` और `next(err)` लिखना ज़रूरी है, जो मैंने यहाँ किया है।

```javascript
const express = require("express");          // web framework
const fs = require("fs/promises");           // promise-based file API (non-blocking)

const app = express();

// Route handler is async: it awaits file I/O without blocking other requests
app.get("/menu", async (req, res, next) => {
  try {
    const raw = await fs.readFile("./menu.json", "utf8"); // async read, server stays free
    res.json(JSON.parse(raw));              // send parsed menu as JSON response
  } catch (err) {
    next(err);                              // hand any error to Express error middleware
  }
});

app.listen(3000, () => console.log("Menu API on port 3000"));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** सोचना कि `setTimeout(fn, 0)` तुरंत चल जाएगा
✅ **Correct:** `0` का मतलब है "call stack खाली होने के बाद जल्द से जल्द", तुरंत नहीं। Sync code पहले पूरा होता है।

```javascript
// Wrong: expecting "B" before "C"
setTimeout(() => console.log("B"), 0);
console.log("C");   // prints first, B comes later

// Right: understand that timers always wait for sync code to finish
console.log("C");
setTimeout(() => console.log("B"), 0); // B comes after C
```

❌ **Mistake 2:** Synchronous file API को server में इस्तेमाल करना
✅ **Correct:** Request handler में `readFileSync` की जगह `fs.promises.readFile` या callback वाला `readFile` इस्तेमाल करो।

```javascript
// Wrong: blocks the whole Node process for every request
app.get("/menu", (req, res) => {
  const raw = fs.readFileSync("./menu.json", "utf8"); // freezes event loop
  res.json(JSON.parse(raw));
});

// Right: non-blocking, other requests keep flowing
app.get("/menu", async (req, res, next) => {
  try {
    const raw = await fs.promises.readFile("./menu.json", "utf8");
    res.json(JSON.parse(raw));
  } catch (err) {
    next(err);
  }
});
```

❌ **Mistake 3:** `async` function को बिना `await` के call करना और उसका result सीधे इस्तेमाल करना
✅ **Correct:** `async` function हमेशा Promise लौटाता है। Value पाने के लिए `await` या `.then` ज़रूरी है।

```javascript
async function getPrice() { return 249; }

// Wrong: price is a Promise object, not the number
const price = getPrice();
console.log(price * 2); // NaN

// Right: await the promise to get the value
async function run() {
  const price2 = await getPrice();  // 249
  console.log(price2 * 2);          // 498
}
run();
```

---

## 🧠 Tricky Interview Question
```javascript
function getData() {
  let result;                                  // local variable, starts as undefined
  setTimeout(() => {                           // callback runs LATER (async)
    result = "data from server";               // assigned only after the timer fires
  }, 0);
  return result;                               // returned BEFORE the timer callback runs
}

console.log(getData());                        // what will this print?
```
**Answer:** `undefined`. `getData` को `return` करते समय `result` अभी भी `undefined` है, क्योंकि `setTimeout` का callback तब तक नहीं चलता जब तक call stack खाली न हो। `return` पहले होता है, timer बाद में। इसीलिए async काम का result सीधे return करना काम नहीं करता। Fix: Promise लौटाओ या callback में result भेजो।

```javascript
// Fix: return a Promise so the caller can await the value
function getDataFixed() {
  return new Promise((resolve) => {
    setTimeout(() => resolve("data from server"), 0); // resolve when data is ready
  });
}
getDataFixed().then((value) => console.log(value));    // data from server
```

---

## ⚫ Interview Questions + Answers

Q1: Synchronous और asynchronous code में मुख्य फर्क क्या है?
A1: Synchronous code में हर statement अपनी बारी पर पूरा होने तक अगला statement रुकता है। Asynchronous code में long-running काम background में चलता है और main flow आगे बढ़ता है। JavaScript single-threaded है, इसलिए async model से ही I/O के दौरान UI या server responsive रहता है।

Q2: क्या JavaScript single-threaded होते हुए भी async हो सकती है?
A2: हाँ। JavaScript engine (जैसे V8) एक समय में एक ही call stack चलाता है, पर waiting वाला काम (timers, network, file I/O) runtime (browser या Node.js) के दूसरे threads/APIs संभालते हैं। Callback या Promise बाद में वापस आकर main thread पर चलता है।

Q3: `setTimeout(fn, 0)` का मतलब क्या है?
A3: इसका मतलब है "जितनी जल्दी हो सके, लेकिन current sync code खत्म होने के बाद"। यह 0 ms पर तुरंत चलने की guarantee नहीं देता। Node.js में minimum delay लगभग 1 ms होता है।

Q4: `async` function कैसे काम करता है और क्या लौटाता है?
A4: `async` function हमेशा एक Promise लौटाता है। अंदर `await` लिखने पर function उस point पर pause होता है, पर पूरा program नहीं रुकता। Return value Promise को resolve करती है, और throw हुआ error Promise को reject करता है।

Q5: Async code में server का performance कैसे बेहतर होता है?
A5: जब एक request database का इंतज़ार करती है, तब event loop दूसरी requests के handlers चला सकता है। इसलिए कम threads में भी हज़ारों concurrent connections संभाले जा सकते हैं। Blocking code (जैसे `readFileSync` या लंबा loop) यह फायदा खत्म कर देता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Network calls, database queries, file I/O या timers हों
- Server को एक साथ कई requests संभालनी हों
- UI को user input पर responsive रखना हो

❌ Avoid when:
- बहुत छोटा, instant calculation हो (async overhead बेकार होगा)
- CPU-heavy काम हो (async इसे अपने-आप तेज़ नहीं करता, इसके लिए worker threads चाहिए)
- Sequence जानबूझकर ज़रूरी हो और उसे साफ़ `await` के साथ लिखा जा सकता हो, तो अनावश्यक callbacks मत बनाओ

---

## 📊 Visual Diagram
```
SYNCHRONOUS (one after another):
  [task A ████████████]  [task B ██████]  [task C ███]
  total time = A + B + C

ASYNCHRONOUS (waiting overlaps):
  main thread: [start A][start B][start C][ handle results ]
  runtime:          [A waits ~~~~~~~~~~]
                        [B waits ~~~~]
                              [C waits ~]
  total time ≈ max(A, B, C)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Synchronous | Line by line, each waits for previous | एक-एक करके, पिछले का इंतज़ार |
| Asynchronous | Starts now, result comes later | अभी शुरू, नतीजा बाद में |
| Blocking | Thread stays busy and nothing else runs | Thread रुका रहना |
| Non-blocking | Thread free while waiting | इंतज़ार में भी thread खाली |
| Callback | Function called when work finishes | काम पूरा होने पर चलने वाला function |
| Promise | Object representing a future value | भविष्य में मिलने वाली value का object |
| Event loop | Moves finished callbacks to call stack | पूरे हुए callbacks को चलाने वाला चक्र |

---

## ⚡ 3-Line Summary
**English:**
1. Synchronous code एक-एक करके चलता है और waiting के दौरान पूरा thread रोक देता है।
2. Asynchronous code धीमे काम को background में छोड़ता है और बाकी code तुरंत चलता रहता है।
3. JavaScript single-threaded है, इसलिए I/O के लिए async model और `await` ही server और UI को responsive रखते हैं।

**Hindi:**
1. Synchronous code एक-एक करके चलता है और इंतज़ार में पूरा thread रोक देता है।
2. Asynchronous code धीमे काम को background में डालता है और बाकी code तुरंत चलता रहता है।
3. JavaScript single-threaded है, इसलिए I/O के लिए async model और `await` ही server और UI को responsive रखते हैं।

---

## ➡️ Next Topic
**71. Call Stack** — यह समझना ज़रूरी है कि sync code किस क्रम में चलता है, और async callbacks कब उसी stack पर वापस आते हैं।
