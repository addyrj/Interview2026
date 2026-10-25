# 86. XMLHttpRequest (legacy)
# हिंदी में: XMLHttpRequest (Legacy) — पुराना Browser HTTP API और उसकी जगह

---

## 🔵 Simple Definition (English)
`XMLHttpRequest` (XHR) is the older browser API for making HTTP requests from JavaScript without reloading the page. You create an object, call `open()` and `send()`, and listen for events such as `onload` and `onerror`. It is callback-based and is mostly replaced by `fetch`, but it is still found in old codebases and interview questions.

## 🔵 सरल परिभाषा (Hindi)
`XMLHttpRequest` (XHR) browser का पुराना API है, जिससे JavaScript बिना page reload किए HTTP requests भेजता है। आप object बनाते हो, `open()` और `send()` call करते हो, और `onload` व `onerror` जैसे events सुनते हो। यह callback-based है, और अब ज़्यादातर `fetch` ने इसकी जगह ले ली है, पर पुराने codebases और interviews में यह आज भी मिलता है।

---

## 🔴 Problem it Solves
Before XHR (around 1999–2004), any change on a web page needed a full reload: click, wait for the server, see a new page. XHR (introduced by Microsoft in IE5, standard by 2006) let scripts exchange data with the server in the background. This was the foundation of "AJAX" (topic 87) and of Gmail- and Facebook-style apps.

## 🔴 यह क्यों बना? (Hindi)
XHR से पहले web page पर हर बदलाव के लिए पूरा reload चाहिए था: click करो, server का इंतज़ार करो, नया page देखो। XHR (Microsoft ने IE5 में शुरू किया, 2006 तक standard बना) ने scripts को background में server से data बदलने दिया। यही "AJAX" (topic 87) और Gmail या Facebook जैसी apps की नींव बना।

---

## 🟢 How it Works — Step by Step

Step 1 → `new XMLHttpRequest()` creates the request object (`readyState` is 0, UNSENT)
Step 2 → `xhr.open(method, url)` sets the method and URL (`readyState` becomes 1, OPENED)
Step 3 → Optionally set headers, `timeout`, and `responseType`
Step 4 → `xhr.send(body)` starts the request asynchronously
Step 5 → The state moves through 2 (HEADERS_RECEIVED), 3 (LOADING), and 4 (DONE), firing `onreadystatechange`
Step 6 → At DONE, read `xhr.status` and `xhr.responseText`; `onload` runs for any HTTP status, `onerror` for network errors, and `ontimeout` on timeout

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `new XMLHttpRequest()` request object बनाता है (`readyState` 0, UNSENT)
Step 2 → `xhr.open(method, url)` method और URL सेट करता है (`readyState` 1, OPENED हो जाता है)
Step 3 → ज़रूरत हो तो headers, `timeout` और `responseType` सेट करो
Step 4 → `xhr.send(body)` request async में भेजता है
Step 5 → State 2 (HEADERS_RECEIVED), 3 (LOADING) और 4 (DONE) से होकर जाती है, और `onreadystatechange` चलता है
Step 6 → DONE पर `xhr.status` और `xhr.responseText` पढ़ो; `onload` किसी भी HTTP status पर चलता है, `onerror` network error पर, और `ontimeout` timeout पर

---

## 🟡 Real World Example
An older IRCTC-style ticket search page, or an internal admin panel written around 2010, uses XHR to load seat availability when a user picks a train. The page stays on screen, the request runs in the background, and the code updates a dropdown when `onload` fires. Many enterprise apps still have this code, so you must be able to read it.

## 🟡 Real Example Hindi mein
कोई पुरानी ticket booking वेबसाइट (जैसे IRCTC जैसी), या 2010 के आसपास बना internal admin panel, user के train चुनने पर seat availability लाने के लिए XHR इस्तेमाल करता है। Page वहीं रहता है, request background में चलती है, और `onload` चलने पर code dropdown अपडेट करता है। बहुत सारे enterprise apps में यह code आज भी है, इसलिए इसे पढ़ना आना चाहिए।

---

## 💻 Code Example — Basic
```javascript
// Node.js has NO XMLHttpRequest (it is a browser API). This small stub copies its shape
// (simplified: real XHR also fires states 2 and 3) so the same browser-style code runs with node.
class FakeXHR {
  static UNSENT = 0;                       // constant states, same names as the real API
  static OPENED = 1;
  static HEADERS_RECEIVED = 2;
  static LOADING = 3;
  static DONE = 4;

  constructor() {
    this.readyState = 0;                   // starts as UNSENT
    this.status = 0;                       // HTTP status (0 until a response arrives)
    this.responseText = "";                // response body as text
    this.onreadystatechange = null;        // callback slots, assigned by user code
    this.onload = null;
    this._url = "";                        // internal: remembered URL
  }

  open(method, url) {
    this._url = url;                       // remember the URL
    this.readyState = 1;                   // OPENED
    this.onreadystatechange?.();           // real XHR fires this synchronously inside open()
  }

  send() {
    setTimeout(() => {                     // simulate the network: response arrives later
      this.readyState = 4;                 // DONE
      this.status = 200;                   // pretend success
      this.responseText = JSON.stringify({ url: this._url, ok: true }); // body as text
      this.onreadystatechange?.();         // state changed to DONE
      this.onload?.();                     // request finished successfully
    }, 20);
  }
}

globalThis.XMLHttpRequest = FakeXHR;     // give the stub the browser's global name for this demo

// ---- Browser-style code starts here ----
const xhr = new XMLHttpRequest();        // create the request object
console.log("state after new:", xhr.readyState);   // 0 (UNSENT)

xhr.onreadystatechange = () => {         // called for every state change
  if (xhr.readyState === 4) {            // only act when the request is DONE
    console.log("state 4, status:", xhr.status);   // 200
  }
};

xhr.onload = () => {                     // called when DONE with any HTTP status
  console.log("onload data:", JSON.parse(xhr.responseText)); // parse the text as JSON
};

xhr.open("GET", "https://api.example.com/menu"); // set method and URL
console.log("state after open:", xhr.readyState);  // 1 (OPENED)
xhr.send();                              // start the request (returns immediately)
console.log("send returned, waiting...");          // prints before the response
```

**Expected output (basic):**
```
state after new: 0
state after open: 1
send returned, waiting...
state 4, status: 200
onload data: { url: 'https://api.example.com/menu', ok: true }
```

## 💻 Code Example — Advanced
```javascript
// Advanced: wrap XHR in a Promise, check status yourself, handle timeout and network errors.

// Stub XHR (Node has no XHR). It supports timeout, onerror, and ontimeout.
class FakeXHR {
  constructor() {
    this.readyState = 0;                   // current state
    this.status = 0;                       // HTTP status code
    this.responseText = "";                // body text
    this.timeout = 0;                      // ms before timeout (0 = no timeout)
    this.onload = null;                    // callbacks
    this.onerror = null;
    this.ontimeout = null;
    this._url = "";
  }
  open(method, url) {
    this._url = url;                       // remember the URL
    this.readyState = 1;                   // OPENED
  }
  send() {
    if (this._url.includes("/slow")) {     // slow route: fire timeout after this.timeout ms
      setTimeout(() => this.ontimeout?.(), this.timeout);
      return;                              // no load event on timeout
    }
    setTimeout(() => {                     // normal route: respond after 20ms
      this.readyState = 4;                 // DONE
      // 404 still fires onload in real XHR: the request completed, the status says it failed
      this.status = this._url.includes("/missing") ? 404 : 200;
      this.responseText = JSON.stringify({ url: this._url });
      this.onload?.();                     // any HTTP status fires onload
    }, 20);
  }
}
globalThis.XMLHttpRequest = FakeXHR;     // install the stub as the browser global

// Promise wrapper around XHR: resolves with parsed JSON, rejects on errors
function getJson(url, { timeoutMs = 1000 } = {}) {
  return new Promise((resolve, reject) => {          // convert callbacks into a promise
    const xhr = new XMLHttpRequest();                // new request object
    xhr.open("GET", url);                            // configure
    xhr.timeout = timeoutMs;                         // real XHR property: ms until timeout
    xhr.onload = () => {                             // HTTP response arrived (any status)
      if (xhr.status >= 200 && xhr.status < 300) {   // XHR does NOT reject on 4xx: check it
        try {
          resolve(JSON.parse(xhr.responseText));    // parse the body and resolve
        } catch (err) {
          reject(err);                               // body was not valid JSON
        }
      } else {
        reject(new Error(`HTTP ${xhr.status}`));     // turn HTTP errors into rejections
      }
    };
    xhr.onerror = () => reject(new Error("network error"));  // DNS, offline, CORS
    xhr.ontimeout = () => reject(new Error("timeout"));     // took longer than timeoutMs
    xhr.send();                                      // start the request
  });
}

(async () => {
  console.log(await getJson("https://api.example.com/menu"));   // { url: ... }
  try {
    await getJson("https://api.example.com/missing");           // 404 -> onload -> we reject
  } catch (err) {
    console.log(err.message);                                    // HTTP 404
  }
  try {
    await getJson("https://api.example.com/slow", { timeoutMs: 50 }); // times out at 50ms
  } catch (err) {
    console.log(err.message);                                    // timeout
  }
})();
```

**Expected output (advanced):**
```
{ url: 'https://api.example.com/menu' }
HTTP 404
timeout
```

---

## 🟠 Express.js Integration
XHR runs in the browser, so the XHR code belongs in front-end files, not in Express. The Express side is simply an endpoint that returns JSON. Express does not care whether the caller uses XHR, `fetch`, or `curl`. The commented code below shows the browser side that calls this route.

```javascript
// Express.js example: the server endpoint that an XHR request calls
const express = require("express");                 // import Express
const app = express();                              // create the app

// Serve the HTML/JS (which contains the XHR code) from the public folder
app.use(express.static("public"));                  // public/index.html can load public/app.js

// The endpoint the XHR call hits
app.get("/api/menu", (req, res) => {                // GET /api/menu
  res.json([{ name: "Chicken Biryani", price: 299 }]); // JSON body; XHR gets it as responseText
});

app.listen(3000);                                   // start the server

// ---- Browser side (public/app.js), NOT Node.js: shown here as comments ----
// const xhr = new XMLHttpRequest();                 // create request
// xhr.open("GET", "/api/menu");                     // same-origin URL
// xhr.onload = () => {                              // runs when response arrives
//   if (xhr.status === 200) renderMenu(JSON.parse(xhr.responseText)); // check status!
// };
// xhr.send();                                       // start it
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Treating every `onload` as success (404 and 500 also fire `onload`)
✅ **Correct:** Check `xhr.status` inside `onload`.

```javascript
// Wrong: a 500 page is parsed as menu data
xhr.onload = () => render(JSON.parse(xhr.responseText));

// Right: only 2xx is success
xhr.onload = () => {
  if (xhr.status >= 200 && xhr.status < 300) render(JSON.parse(xhr.responseText));
  else showError(xhr.status);
};
```

❌ **Mistake 2:** Calling `send()` before `open()`
✅ **Correct:** Always call `open()` first, then set headers, then `send()`.

```javascript
// Wrong: throws InvalidStateError in real browsers
const xhr2 = new XMLHttpRequest();
xhr2.send();
xhr2.open("GET", "/api/menu");

// Right
const xhr3 = new XMLHttpRequest();
xhr3.open("GET", "/api/menu");
xhr3.send();
```

❌ **Mistake 3:** Using synchronous XHR (`open(method, url, false)`) on the main thread
✅ **Correct:** Use async XHR or `fetch`. Synchronous XHR freezes the whole page until the response arrives, and browsers have deprecated it.

```javascript
// Wrong: the page freezes while waiting
xhr.open("GET", "/api/menu", false);   // third argument false = synchronous
xhr.send();

// Right: async (default) with a callback or promise wrapper
xhr.open("GET", "/api/menu");
xhr.send();
```

---

## 🧠 Tricky Interview Output Question
```javascript
// Same FakeXHR as the examples: readyState and events follow the real XHR order.
class MiniXHR {
  constructor() { this.readyState = 0; this.log = []; } // starts UNSENT, no events yet
  open() { this.readyState = 1; this.onreadystatechange?.(); } // fires synchronously
  send() {
    setTimeout(() => {                    // response is always asynchronous
      this.readyState = 4;
      this.onreadystatechange?.();        // DONE event
      this.onload?.();                    // load event after the state change
    }, 0);
  }
}

const x = new MiniXHR();
x.onreadystatechange = () => console.log("rsc:", x.readyState); // state change handler
x.onload = () => console.log("load");     // load handler

console.log("A:", x.readyState);          // what is printed here?
x.open();                                 // open fires readystatechange immediately
console.log("B:", x.readyState);          // and here?
x.send();                                 // response comes later
console.log("C");                         // and this?
```
**Answer:**
```
A: 0
rsc: 1
B: 1
C
rsc: 4
load
```
**Why:** Before `open()`, the state is 0 (UNSENT), so `A: 0` prints. `open()` changes the state to 1 and fires `onreadystatechange` synchronously, so `rsc: 1` prints right inside `open()`, before `B: 1`. `send()` schedules the response with `setTimeout`, so it does not finish immediately. `C` prints next. Later the timer runs, the state becomes 4, `onreadystatechange` prints `rsc: 4`, and then `onload` prints `load`. The key idea is that `open()` is synchronous and the response is always asynchronous.

---

## ⚫ Interview Questions + Answers

Q1: What are the four states of `readyState`?
A1: 0 UNSENT (object created), 1 OPENED (`open()` called), 2 HEADERS_RECEIVED (headers arrived), 3 LOADING (body arriving), and 4 DONE (complete). Some interviews only ask for 0, 1, and 4.

Q2: What is the difference between `onload` and `onerror`?
A2: `onload` fires whenever the response arrives, including 404 and 500. `onerror` fires only for network-level failures (no response at all). So you must check `status` inside `onload`.

Q3: Why is XHR called "legacy"?
A3: It uses callbacks instead of promises, is verbose, and has been replaced by `fetch`, which works with `async`/`await`, streams, and `AbortController`. XHR is still needed for upload progress events, which `fetch` does not expose.

Q4: What is the difference between XHR and `fetch` on HTTP errors?
A4: Both deliver 404 and 500 responses without throwing. In both cases you must check the status yourself. The difference is that `fetch` uses promises, and XHR uses callbacks.

Q5: What is the default for `xhr.timeout`?
A5: 0, which means no timeout. Set it to a number of milliseconds to make the request fail with `ontimeout` after that time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You maintain legacy code that already uses XHR
- You need upload progress (`xhr.upload.onprogress`), which `fetch` does not provide
- You must support very old browsers without polyfills

❌ Avoid when:
- You write new code; use `fetch` with `async`/`await` instead
- You need synchronous behavior; synchronous XHR is deprecated and blocks the page
- You run in Node.js; there is no XHR there, so use `fetch` or `http`

---

## 📊 Visual Diagram
```
new XMLHttpRequest()        readyState 0  (UNSENT)
        │
   open(method, url)        readyState 1  (OPENED)  ── onreadystatechange (sync)
        │
    send()                  (returns at once; network runs in background)
        │
   ┌────┴──────────────────────────────────────────────┐
   │ headers arrive         readyState 2  (HEADERS_RECEIVED)
   │ body arrives           readyState 3  (LOADING)
   │ complete               readyState 4  (DONE) ── onreadystatechange
   └────┬──────────────────────────────────────────────┘
        │
        ├── response (any status) ──► onload       → check xhr.status
        ├── no response           ──► onerror      (network failure)
        └── too slow              ──► ontimeout    (after xhr.timeout ms)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| XHR | Legacy browser API for HTTP requests | Legacy browser HTTP API |
| `readyState` | Current stage of the request (0 to 4) | Request का current stage |
| `open()` | Sets method and URL | Method और URL सेट करना |
| `send()` | Starts the request | Request शुरू करना |
| `onload` | Fires when the response arrives (any status) | Response आने पर चलने वाला callback |
| `onerror` | Fires on network failure | Network failure पर चलने वाला callback |
| `ontimeout` | Fires when `timeout` ms pass | Timeout होने पर चलने वाला callback |
| Synchronous XHR | Blocking request (deprecated) | Blocking request (अब deprecated) |

---

## ⚡ 3-Line Summary
**English:**
1. XHR is the older callback-based browser API: `open`, `send`, then `onload`/`onerror`/`ontimeout`.
2. `onload` fires for every HTTP status, so check `xhr.status` yourself.
3. Use `fetch` for new code, and read XHR when you maintain legacy code or need upload progress.

**Hindi:**
1. XHR पुराना callback-based browser API है: `open`, `send`, फिर `onload`/`onerror`/`ontimeout`।
2. `onload` हर HTTP status पर चलता है, इसलिए `xhr.status` खुद चेक करो।
3. नए code में `fetch` इस्तेमाल करो; XHR पुराने code को पढ़ने और upload progress के लिए ज़रूरी है।

---

## ➡️ Next Topic
**87. AJAX** — XHR was the engine behind AJAX. Next, learn what AJAX means as a technique (not an API), the request/response pattern it uses, and how to avoid the classic race condition in live-updating UIs.
