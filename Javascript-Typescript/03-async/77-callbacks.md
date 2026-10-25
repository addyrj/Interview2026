# 77. Callbacks
# हिंदी में: Callbacks — वह function जो काम पूरा होने पर बुलाया जाता है

---

## 🔵 Simple Definition (English)
A **callback** is a function passed as an argument to another function, to be called later when some work finishes. Node.js uses the **error-first** convention: the first argument is `err` (null when OK), and the result follows.

## 🔵 सरल परिभाषा (Hindi)
**Callback** वह function है जिसे किसी दूसरे function को argument के रूप में दिया जाता है, ताकि काम पूरा होने पर उसे बाद में बुलाया जा सके। Node.js में **error-first** convention है: पहला argument `err` होता है (ठीक होने पर `null`), और उसके बाद result।

---

## 🔴 Problem it Solves
Async काम (file read, DB query, HTTP call) का result तुरंत नहीं मिलता। बिना callback के कोई function यह नहीं बता सकता कि result कब आया। Callback वह "वापसी का रास्ता" है, जिससे result और error दोनों सही समय पर caller तक पहुँचते हैं।

## 🔴 यह क्यों बना? (Hindi)
Node.js के शुरुआती दिनों में I/O non-blocking था, पर उसे promise नहीं था। हर async API को कोई न कोई callback चाहिए था। Paytm जैसे services में "DB से user लाओ, फिर wallet लाओ, फिर log लिखो" जैसे steps callback से ही लिखे जाते थे। इसी से callback की पहली पीढ़ी बनी।

---

## 🟢 How it Works — Step by Step

Step 1 → Caller एक function और एक callback देता है (जैसे `readFile(path, cb)`)
Step 2 → Async API काम runtime को सौंपता है और तुरंत लौट आता है
Step 3 → काम पूरा होने पर runtime callback को queue में डालता है
Step 4 → Callback को `(err, data)` के साथ चलाया जाता है
Step 5 → Caller पहले `err` जाँचता है, फिर `data` इस्तेमाल करता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Caller एक function और callback देता है, जैसे `readFile(path, cb)`
Step 2 → Async API काम runtime को सौंपता है और तुरंत लौट आता है
Step 3 → काम पूरा होने पर callback queue में जाता है
Step 4 → Callback को `(err, data)` के साथ चलाया जाता है
Step 5 → Caller पहले `err` जाँचता है, फिर `data` इस्तेमाल करता है

---

## 🟡 Real World Example
Zomato के backend में restaurant menu की JSON फाइल से menu पढ़ना हो, तो `fs.readFile(path, cb)` लिखा जाता है। `cb` में पहले error check होता है (फाइल न मिले तो fallback), फिर menu parse होकर response जाता है। यह सीधे callback pattern का उदाहरण है।

## 🟡 Real Example Hindi mein
Zomato के backend में menu की JSON फाइल पढ़ने के लिए `fs.readFile(path, cb)` लिखा जाता है। `cb` में पहले error जाँचा जाता है (फाइल न मिले तो fallback), फिर menu parse होकर response जाता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: callbacks, the error-first pattern, and why order differs from code order
// Run with: node 77-callbacks.js
const fs = require("fs");                      // built-in file system module

// 1. A simple callback passed to a sync array method (runs immediately)
[1, 2, 3].forEach((n) => console.log("forEach callback:", n)); // called right away

// 2. An async callback: fs.readFile calls our function later
fs.readFile(__filename, "utf8", (err, data) => { // error-first: err, then data
  if (err) {                                   // err is null on success
    console.log("Could not read file:", err.message); // handle the error first
    return;                                    // stop here, do not touch data
  }
  console.log("File read, first 20 chars:", data.slice(0, 20)); // use data safely
});

console.log("readFile started (this prints first)"); // sync: runs before the callback

// Output order: forEach lines, then "readFile started", then the file result
```

## 💻 Code Example — Advanced
```javascript
// Goal: write an error-first async function, guard against double callbacks,
// and convert it into a promise-based wrapper.
const fs = require("fs");

// Error-first function: calls cb(err, value) exactly once
function readJsonFile(path, cb) {
  let called = false;                          // guard flag for "call only once"
  const done = (err, value) => {               // single exit point
    if (called) return;                        // ignore any second call
    called = true;                             // mark as finished
    cb(err, value);                            // deliver the result to the caller
  };

  fs.readFile(path, "utf8", (err, raw) => {    // async runtime read
    if (err) return done(err);                 // pass the error through
    try {
      done(null, JSON.parse(raw));             // success: parsed JSON as the value
    } catch (parseErr) {
      done(parseErr);                          // invalid JSON: report through callback
    }
  });
}

// Wrapper that turns the callback function into a promise
function readJsonAsync(path) {
  return new Promise((resolve, reject) => {    // promise wraps the callback world
    readJsonFile(path, (err, value) => {       // use the callback version inside
      if (err) reject(err);                    // error path
      else resolve(value);                     // success path
    });
  });
}

// Demo with a file that does not exist, to show error-first handling
readJsonFile("./no-such-file.json", (err, value) => {
  if (err) {                                   // err is set, value is undefined
    console.log("callback error code:", err.code); // ENOENT
    return;
  }
  console.log("value:", value);                // not reached in this demo
});

// Demo promise wrapper with the same missing file, caught with try/catch
(async () => {
  try {
    await readJsonAsync("./no-such-file.json"); // will reject
  } catch (err) {
    console.log("promise error code:", err.code); // ENOENT
  }
})();
```

---

## 🟠 Express.js Integration
Express का हर middleware और route handler एक callback है। `(req, res, next)` वही callback signature है, जिसमें `next(err)` error-first जैसा काम करता है। नीचे का example दिखाता है कि callback-style middleware कैसे error को `next(err)` से आगे भेजता है, जो Express का सबसे सीधा callback इस्तेमाल है।

```javascript
const express = require("express");          // web framework
const fs = require("fs");                    // callback-style file API
const app = express();

// Middleware is a callback: (req, res, next). Calling next(err) is error-first in spirit.
app.get("/menu", (req, res, next) => {
  fs.readFile("./menu.json", "utf8", (err, raw) => { // callback-style async read
    if (err) return next(err);               // error-first: hand the error to Express
    try {
      res.json(JSON.parse(raw));             // success: send the parsed menu
    } catch (parseErr) {
      next(parseErr);                        // invalid JSON: also go to error middleware
    }
  });
});

// Error-handling middleware: 4 arguments tell Express this is for errors
app.use((err, req, res, next) => {
  res.status(500).json({ error: "Server error", detail: err.code || err.message });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Error check किए बिना `data` इस्तेमाल करना
✅ **Correct:** Callback में पहले `err` जाँचो। Error होने पर `data` `undefined` हो सकता है।

```javascript
// Wrong: crashes when the file is missing (data is undefined)
fs.readFile("./menu.json", "utf8", (err, data) => {
  console.log(data.length); // TypeError: Cannot read properties of undefined
});

// Right: check err first
fs.readFile("./menu.json", "utf8", (err, data) => {
  if (err) return console.log("failed:", err.code);
  console.log(data.length);
});
```

❌ **Mistake 2:** Callback को return करने के बाद भी उसे "फिर से" call होने देना
✅ **Correct:** `return` लिखो, या एक guard flag रखो, ताकि callback दो बार न चले।

```javascript
// Wrong: missing return means the success path also runs after the error
function getOrder(id, cb) {
  if (!id) cb(new Error("no id"));           // error called...
  cb(null, { id, total: 100 });              // ...and success is called too
}
getOrder(undefined, (err, order) => console.log(err ? "error" : "ok", order));

// Right: return after the error callback
function getOrderRight(id, cb) {
  if (!id) return cb(new Error("no id"));    // stop after the error
  cb(null, { id, total: 100 });
}
getOrderRight(undefined, (err) => console.log(err ? "error" : "ok"));
```

❌ **Mistake 3:** Callback के अंदर `try/catch` रखकर उसे async error पर भी उम्मीद करना
✅ **Correct:** Callback में आने वाला error `err` argument से आता है। `try` उसे नहीं पकड़ता, जब तक error उसी call stack में throw न हो।

```javascript
// Wrong: the try does not see errors that happen later inside the callback
try {
  fs.readFile("./missing.json", "utf8", (err, data) => {
    if (err) throw err;                      // throw inside a callback is not caught by the outer try
  });
} catch (e) {
  console.log("never runs");
}

// Right: handle err inside the callback
fs.readFile("./missing.json", "utf8", (err) => {
  if (err) console.log("handled:", err.code);
});
```

---

## 🧠 Tricky Interview Question
```javascript
function getOrder(id, cb) {
  if (!id) cb(new Error("missing id"));      // no return here
  cb(null, { id, total: 100 });              // runs even after the error call
}

getOrder(undefined, (err, order) => {
  console.log(err ? "err" : "ok", order);    // what gets printed, and how many times?
});
```
**Answer:** दो lines छपती हैं:
```
err undefined
ok { id: undefined, total: 100 }
```
`cb` को दो बार बुलाया गया। पहली बार `err` set था, इसलिए `err ? "err" : "ok"` `"err"` बना, और `order` `undefined` था। दूसरी बार `err` `null` था, तो `"ok"` छपा। `if` के बाद `return` न होने के कारण callback दो बार चला। Fix: `return cb(...)` लिखो।

---

## ⚫ Interview Questions + Answers

Q1: Callback क्या है?
A1: Callback वह function है जिसे किसी दूसरे function को argument के रूप में दिया जाता है, ताकि async काम पूरा होने पर उसे बुलाया जाए।

Q2: Error-first convention क्या है?
A2: Node.js callbacks का पहला argument error होता है (सफल होने पर `null`), और बाकी arguments result होते हैं। इससे caller हमेशा पहले error जाँच सकता है।

Q3: Callbacks से promises की ओर बदलाव क्यों हुआ?
A3: Callbacks में nested pyramid बनता है, error handling बिखरता है, और return value नहीं मिलता। Promises chain लिखने, एक जगह error पकड़ने, और `await` से sequential code देने में आसान हैं।

Q4: `util.promisify` क्या करता है?
A4: यह error-first callback वाले function को Promise लौटाने वाले function में बदल देता है। Node के built-in APIs में इसका उपयोग आम है, जैसे `util.promisify(fs.readFile)`।

Q5: Callback को दो बार call होने से कैसे रोकें?
A5: `return` लिखो, या एक guard flag (जैसे `called`) रखो। Library APIs में यह ज़रूरी है, क्योंकि दो बार चला callback अक्सर अजीब state बनाता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Node के पुराने APIs (कई built-in `fs`, `crypto`) को इस्तेमाल करना हो
- Event listeners या एक-बार की घटना पर code चलाना हो
- Array methods (`map`, `filter`, `forEach`) में sync callbacks देने हों

❌ Avoid when:
- नया code लिखना हो, जहाँ async/await बेहतर है
- कई async steps को sequence में चलाना हो (nested callbacks से pyramid बनेगा)
- Error handling एक जगह केंद्रित करनी हो

---

## 📊 Visual Diagram
```
  caller:  readFile(path, cb)
              │
              ▼
  runtime:  [ disk read in background ... ]
              │
              ▼  finished
  queue:    cb(err, data)
              │
              ▼
  caller's cb:
     if (err) { handle error; return; }
     use data
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback | Function called later with results | बाद में बुलाया जाने वाला function |
| Error-first | First argument is the error (or null) | पहला argument error होता है |
| Higher-order function | Function that takes or returns functions | Function को argument लेने वाला function |
| Guard flag | Variable that prevents double calls | दो बार call रोकने वाला flag |
| promisify | Convert callback API to promise API | Callback को Promise में बदलना |
| Sync callback | Called immediately during the call | उसी समय चलने वाला callback |
| Async callback | Called later from the queue | बाद में queue से चलने वाला callback |

---

## ⚡ 3-Line Summary
**English:**
1. Callback वह function है जो async काम पूरा होने पर बुलाया जाता है, और Node में error-first pattern है।
2. हमेशा पहले `err` जाँचो, और error के बाद `return` लिखो ताकि callback दो बार न चले।
3. Nested callbacks से pyramid बनता है, इसलिए नया code promises और async/await से लिखो।

**Hindi:**
1. Callback वह function है जो async काम पूरा होने पर बुलाया जाता है, और Node में error-first pattern है।
2. हमेशा पहले `err` जाँचो, और error के बाद `return` लिखो ताकि callback दो बार न चले।
3. Nested callbacks से pyramid बनता है, इसलिए नया code promises और async/await से लिखो।

---

## ➡️ Next Topic
**78. Callback Hell (Pyramid of Doom)** — nested callbacks की समस्या, उसे पहचानना, और उसे सुधारने के तरीके।
