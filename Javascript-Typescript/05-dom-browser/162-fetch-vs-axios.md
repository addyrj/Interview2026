# 162. Fetch vs Axios
# हिंदी में: Fetch बनाम Axios

---

## 🔵 Simple Definition (English)
`fetch` is a built-in API in browsers and in Node.js (global since Node 18). It sends an HTTP request and returns a Promise that resolves to a `Response`. `axios` is a popular third-party library that wraps HTTP requests and adds automatic JSON handling, errors for non-2xx responses, interceptors, and timeouts.

## 🔵 सरल परिभाषा (Hindi)
`fetch` browser और Node.js (Node 18 से global) में पहले से मौजूद API है। यह HTTP request भेजता है और एक Promise देता है, जो `Response` पर resolve होता है। `axios` एक लोकप्रिय third-party library है, जो JSON अपने-आप बदलती है, 2xx के बाहर के status पर error फेंकती है, और interceptors व timeout जैसी सुविधाएँ देती है।

---

## 🔴 Problem it Solves
Before `fetch`, browsers used `XMLHttpRequest`, which was callback-based and verbose. Developers added jQuery `$.ajax` just for network calls, which made the page heavier. `axios` filled the gap with a Promise API, but it is still an extra dependency. `fetch` is the standard, so it needs no install, but it is low-level. It does not throw on HTTP errors, does not parse JSON for you, and has no timeout option. Choosing between the two means choosing between "no dependency" and "more features out of the box".

## 🔴 यह क्यों बना? (Hindi)
`fetch` से पहले browsers में `XMLHttpRequest` चलता था, जो callbacks पर आधारित और लंबा लिखना पड़ता था। Network calls के लिए लोग सिर्फ़ jQuery `$.ajax` जोड़ लेते थे, जिससे page भारी हो जाता था। `axios` ने Promise वाला API दिया, लेकिन वह भी एक extra dependency है। `fetch` standard है, इसलिए install नहीं करना पड़ता, पर वह low-level है। वह HTTP error पर throw नहीं करता, JSON अपने-आप नहीं बदलता, और उसमें timeout का सीधा option नहीं है। चुनाव असल में "कोई dependency नहीं" और "ज़्यादा features पहले से" के बीच का है।

---

## 🟢 How it Works — Step by Step

Step 1 → You call `fetch(url, options)`. It returns a Promise right away.
Step 2 → The request goes over the network. The Promise resolves as soon as the response headers arrive, even for a 404 or 500.
Step 3 → You read the body with `res.json()`, `res.text()`, or `res.blob()`. A body can be read only once.
Step 4 → Only network failures, DNS errors, CORS blocks (browser), or aborted signals reject the Promise.
Step A (axios) → `axios.get(url)` passes the request through request interceptors, then sends it.
Step B (axios) → The response body is parsed to JavaScript automatically when it is JSON.
Step C (axios) → Any status outside 2xx rejects the Promise. The error has `err.response.status` and `err.response.data`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `fetch(url, options)` call करें। वह तुरंत एक Promise देता है।
Step 2 → Request network पर जाती है। Response headers आते ही Promise resolve हो जाता है, भले ही status 404 या 500 हो।
Step 3 → Body को `res.json()`, `res.text()` या `res.blob()` से पढ़ें। Body सिर्फ़ एक बार पढ़ी जा सकती है।
Step 4 → सिर्फ़ network failure, DNS error, CORS block (browser) या abort signal से Promise reject होता है।
Step A (axios) → `axios.get(url)` request को पहले request interceptors से गुज़ारता है, फिर भेजता है।
Step B (axios) → अगर body JSON है, तो response अपने-आप JavaScript object में बदल जाता है।
Step C (axios) → 2xx के बाहर का कोई भी status Promise को reject करता है। Error में `err.response.status` और `err.response.data` होते हैं।

---

## 🟡 Real World Example
A food delivery web app like Zomato or Swiggy usually fetches the restaurant list with plain `fetch`, because the call is simple and the bundle stays small. The same team may use `axios` in the admin panel, where one request interceptor adds the auth token to every call and refreshes it when the server returns 401. Payment status checks in a checkout flow, like Razorpay or Paytm, need a hard timeout, so the code either sets `AbortSignal.timeout()` with `fetch` or `timeout` with `axios`.

## 🟡 Real Example Hindi mein
Zomato या Swiggy जैसे food delivery web app में restaurant list आम तौर पर सीधे `fetch` से लाई जाती है, क्योंकि call सरल है और bundle छोटा रहता है। उसी टीम का admin panel `axios` इस्तेमाल कर सकता है, जहाँ एक request interceptor हर call में auth token जोड़ता है और server 401 दे तो token refresh करता है। Razorpay या Paytm जैसे checkout flow में payment status check के लिए सख़्त timeout चाहिए, इसलिए code `fetch` के साथ `AbortSignal.timeout()` या `axios` के साथ `timeout` लगाता है।

---

## 💻 Code Example — Basic
Runs with plain Node.js (18 or newer). No install needed. Run: `node fetch-basic.js`

```javascript
// fetch-basic.js — run with: node fetch-basic.js
const http = require("http");                             // built-in module to create a tiny local server

const server = http.createServer((req, res) => {          // handle every incoming request
  res.setHeader("Content-Type", "application/json");      // tell the client the body is JSON

  if (req.method === "POST" && req.url === "/orders") {   // route: POST /orders
    let body = "";                                        // will collect the request body text
    req.on("data", (chunk) => (body += chunk));           // append each piece of the body
    req.on("end", () => {                                 // runs when the whole body has arrived
      const data = JSON.parse(body);                      // turn the JSON text into an object
      res.statusCode = 201;                               // 201 Created
      res.end(JSON.stringify({ id: 101, item: data.item }));// send the new order back as JSON
    });
    return;                                               // stop here for this route
  }

  if (req.url === "/restaurants") {                       // route: GET /restaurants
    res.end(JSON.stringify([{ id: 1, name: "Biryani House" }])); // send a JSON array
    return;                                               // stop here for this route
  }

  res.statusCode = 500;                                   // any other route: send 500 for the demo
  res.end(JSON.stringify({ error: "boom" }));             // error body
});

server.listen(0, async () => {                            // port 0 means "any free port"
  const base = `http://localhost:${server.address().port}`; // build the base URL with the chosen port
  try {                                                   // network errors land in catch
    const list = await fetch(`${base}/restaurants`);      // GET is the default method
    const restaurants = await list.json();                // parse the JSON body
    console.log("GET:", restaurants);                      // print the array

    const res = await fetch(`${base}/orders`, {           // POST request with an options object
      method: "POST",                                     // HTTP method
      headers: { "Content-Type": "application/json" },    // tell the server the body is JSON
      body: JSON.stringify({ item: "Paneer Tikka" }),     // body must be a string, so stringify it
    });
    console.log("POST status:", res.status);               // prints 201
    console.log("POST body:", await res.json());            // prints { id: 101, item: 'Paneer Tikka' }
  } catch (err) {                                         // runs on network failure
    console.error("Failed:", err.message);                // show what went wrong
  } finally {                                             // always runs
    server.close();                                       // stop the server so node can exit
  }
});
```

## 💻 Code Example — Advanced
Runs with plain Node.js (18.2+ for `closeAllConnections`, 20.3+ for `AbortSignal.any`). Run: `node fetch-advanced.js`

```javascript
// fetch-advanced.js — run with: node fetch-advanced.js
const http = require("http");                             // built-in module for the demo server

class HttpError extends Error {                           // custom error that carries the HTTP status
  constructor(status, body) {                             // receives the status and the parsed body
    super(`HTTP ${status}`);                              // message for logs
    this.name = "HttpError";                              // name we check in the retry logic
    this.status = status;                                 // keep the status code
    this.body = body;                                     // keep the response body
  }
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)); // small helper to wait

// Wrapper around fetch: JSON in and out, timeout, retries on 5xx and network errors
async function fetchJson(url, { method = "GET", body, timeoutMs = 3000, retries = 2, signal } = {}) {
  for (let attempt = 0; attempt <= retries; attempt++) {  // attempt 0 is the first try
    try {                                                 // catch both network and HTTP errors below
      const timeout = AbortSignal.timeout(timeoutMs);     // signal that aborts after timeoutMs
      const combined = signal                             // join the caller's signal with the timeout
        ? AbortSignal.any([signal, timeout])              // whichever fires first aborts the request
        : timeout;                                        // otherwise only the timeout applies

      const res = await fetch(url, {                      // perform the request
        method,                                           // HTTP verb
        headers: body ? { "Content-Type": "application/json" } : {}, // JSON header only when sending a body
        body: body ? JSON.stringify(body) : undefined,    // serialize the body if we have one
        signal: combined,                                 // cancel on timeout or caller abort
      });

      const text = await res.text();                      // read the body once, as text
      const data = text ? JSON.parse(text) : null;        // parse only if there is any text
      if (res.ok) return data;                            // 2xx: success, return the data
      throw new HttpError(res.status, data);              // non-2xx: throw so catch can decide
    } catch (err) {                                       // one place to decide about retries
      const retryable =                                   // which failures are worth another try?
        err.name === "TypeError" ||                       // fetch network failure
        err.name === "TimeoutError" ||                    // our timeout fired
        (err.name === "HttpError" && err.status >= 500);  // server-side error only
      if (!retryable || attempt === retries) throw err;   // give up on 4xx, or when out of retries
      console.log(`  retrying after ${err.name} (attempt ${attempt + 1})`); // log the retry
    }
    await sleep(100 * 2 ** attempt);                      // exponential backoff: 100ms, 200ms, ...
  }
}

let flakyHits = 0;                                        // counts calls to /flaky
const server = http.createServer(async (req, res) => {    // demo server with 4 behaviours
  res.setHeader("Content-Type", "application/json");      // every answer is JSON

  if (req.url === "/flaky") {                             // fails the first time, works after
    flakyHits++;                                          // count this call
    if (flakyHits === 1) {                                // first call only
      res.statusCode = 503;                               // Service Unavailable
      return res.end(JSON.stringify({ error: "busy" }));  // error body
    }
    return res.end(JSON.stringify({ ok: true, hits: flakyHits })); // later calls succeed
  }

  if (req.url === "/slow") {                              // takes longer than our timeout
    await sleep(1000);                                    // wait 1 second
    return res.end(JSON.stringify({ slow: true }));       // late answer, client already gave up
  }

  if (req.url === "/missing") {                           // always 404
    res.statusCode = 404;                                 // Not Found
    return res.end(JSON.stringify({ error: "not found" })); // error body
  }

  res.end("{}");                                          // default: empty object
});

server.listen(0, async () => {                            // choose any free port
  const base = `http://localhost:${server.address().port}`; // base URL for all demo calls
  try {                                                   // make sure the server is always closed
    console.log("1) flaky endpoint (503 first, then 200):"); // step 1 title
    console.log("  result:", await fetchJson(`${base}/flaky`)); // retried once, then succeeds

    console.log("2) 200ms timeout on a 1s endpoint:");     // step 2 title
    try {                                                 // expect a failure here
      await fetchJson(`${base}/slow`, { timeoutMs: 200, retries: 0 }); // no retries for the demo
    } catch (err) {                                       // the timeout error arrives here
      console.log("  error name:", err.name);             // prints TimeoutError
    }

    console.log("3) 404 is not retried:");                 // step 3 title
    try {                                                 // expect a failure here too
      await fetchJson(`${base}/missing`, { retries: 3 }); // 4xx must not be retried
    } catch (err) {                                       // HttpError arrives here
      console.log("  error:", err.name, err.status, err.body); // HttpError 404 { error: 'not found' }
    }
  } finally {                                             // always runs
    server.closeAllConnections();                         // drop open sockets, including the slow one
    server.close();                                       // stop listening so node can exit
  }
});
```

---

## 🟠 Express.js Integration
Express runs on the server, so `fetch` is also used there. A common case is a BFF (backend for frontend) route that calls another internal service, such as a menu service. The route sets a timeout, checks `res.ok`, and turns upstream failures into clean errors for the browser.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                        // web framework
const app = express();                                     // create the app

// Base URL of the upstream menu service (set MENU_API in production)
const MENU_API = process.env.MENU_API || "http://localhost:4000"; // upstream base URL

// Proxy route: GET /api/menu/:restaurantId forwards to the upstream service
app.get("/api/menu/:restaurantId", async (req, res) => {   // route with a URL parameter
  const id = encodeURIComponent(req.params.restaurantId);  // protect the URL from odd characters
  try {                                                    // network errors and timeouts go to catch
    const upstream = await fetch(`${MENU_API}/restaurants/${id}/menu`, { // call the upstream service
      signal: AbortSignal.timeout(2000),                   // give up after 2 seconds
    });
    if (!upstream.ok) {                                    // upstream returned 4xx or 5xx
      return res.status(502).json({ error: "menu service error", upstream: upstream.status }); // bad gateway
    }
    const menu = await upstream.json();                    // parse the upstream JSON body
    res.json(menu);                                        // forward the menu to the browser
  } catch (err) {                                          // timeout or network failure
    const status = err.name === "TimeoutError" ? 504 : 502; // 504 for timeout, 502 for other failures
    res.status(status).json({ error: err.name });          // clean error body for the client
  }
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `fetch` to throw on a 404 or 500
✅ Correct: `fetch` resolves for every HTTP response. Check `res.ok` (or `res.status`) yourself.

```javascript
// Wrong — the 404 is treated as a success
try {
  const res = await fetch(`${base}/missing`);        // resolves even though the status is 404
  const data = await res.json();                     // parses the error body as if it were data
  console.log("Order:", data);                       // wrong path, wrong output
} catch (err) {
  console.log("Error caught");                        // never reached for a 404
}

// Right — check the status yourself
const res = await fetch(`${base}/missing`);          // same request
if (!res.ok) throw new Error(`HTTP ${res.status}`);  // turn 4xx and 5xx into an error
const data = await res.json();                       // only parse a successful body
```

❌ **Mistake 2:** Sending a plain object as the body
✅ Correct: `fetch` sends whatever you pass. An object becomes the text `[object Object]`. Stringify it and set the header.

```javascript
// Wrong — the server receives the text "[object Object]"
await fetch(`${base}/orders`, { method: "POST", body: { item: "Paneer" } });

// Right — stringify and tell the server it is JSON
await fetch(`${base}/orders`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },   // tells the server how to read the body
  body: JSON.stringify({ item: "Paneer" }),           // a string, not an object
});
```

❌ **Mistake 3:** Reading the same response body twice
✅ Correct: A response body is a stream. After `res.json()`, a second `res.text()` throws. Read it once and reuse the result.

```javascript
// Wrong — the second read fails
const res = await fetch(`${base}/restaurants`);
const data = await res.json();                       // first read: works
const raw = await res.text();                        // TypeError: Body is unusable

// Right — read once, reuse the text
const res2 = await fetch(`${base}/restaurants`);
const raw2 = await res2.text();                      // read the stream once
const data2 = JSON.parse(raw2);                      // parse the saved text as needed
```

❌ **Mistake 4:** Expecting axios to return a 404 response instead of throwing
✅ Correct: axios rejects for any non-2xx status by default. The status is in `err.response`. This needs `npm install axios`.

```javascript
// Wrong — the 404 check never runs, because axios already threw
const res = await axios.get(`${base}/missing`);
if (res.status === 404) console.log("not found");   // unreachable for a 404

// Right — handle the rejection
try {
  await axios.get(`${base}/missing`);
} catch (err) {
  if (err.response?.status === 404) console.log("not found"); // status is in err.response
}
```

---

## 🧠 Tricky Interview Question
What does this print? Run it with `node tricky-fetch.js`.

```javascript
// tricky-fetch.js — run with: node tricky-fetch.js
const http = require("http");                              // built-in server module
const server = http.createServer((req, res) => {           // tiny server
  res.statusCode = 500;                                    // every answer is a server error
  res.end("boom");                                         // plain text body
});

server.listen(0, async () => {                             // any free port
  const url = `http://localhost:${server.address().port}/`; // URL of the server
  try {                                                    // the catch block below is the trap
    const res = await fetch(url);                          // HTTP 500 is still a response
    console.log("resolved", res.status, res.ok);           // resolved 500 false
    const first = await res.text();                        // reads the body once
    console.log("first read:", first);                     // first read: boom
    await res.text();                                      // reads the same body again
    console.log("second read done");                       // never printed
  } catch (err) {                                          // runs for the second read
    console.log("caught:", err.name);                      // caught: TypeError
  } finally {                                              // always runs
    server.close();                                        // close the demo server
  }
});
```

Answer: The output is:
```
resolved 500 false
first read: boom
caught: TypeError
```
Explanation: `fetch` rejects only for network-level failures. An HTTP 500 is a valid response, so the Promise resolves and the `catch` block is not run for the first call. `res.ok` is `false` because the status is outside 200 to 299. The body is a stream that can be consumed only once. The first `res.text()` reads it. The second call throws a `TypeError` ("Body is unusable"), which goes to `catch`. The line `second read done` never runs.

---

## ⚫ Interview Questions + Answers

Q1: Does `fetch` reject when the server returns a 404?
A1: No. `fetch` rejects only for network failures, DNS errors, CORS blocks in browsers, and aborted signals. A 404 or 500 is a valid response, so you must check `res.ok` or `res.status`.

Q2: What does axios do differently by default?
A2: Axios parses JSON bodies automatically, rejects the Promise for non-2xx statuses, and supports interceptors and a `timeout` option. The data is in `response.data`.

Q3: How do you set a timeout with plain `fetch`?
A3: Pass `signal: AbortSignal.timeout(ms)`. When the time passes, the request is aborted and `fetch` rejects with a `TimeoutError`. Before this helper existed, you had to create an `AbortController` and call `setTimeout(() => controller.abort(), ms)` yourself.

Q4: Why can't you read `res.json()` and then `res.text()` on the same response?
A4: The body is a stream. Once it has been read, it is used up. Reading it again throws a `TypeError`. Read it once as text and parse it with `JSON.parse` when you need an object.

Q5: How do you choose between `fetch` and `axios`?
A5: Use `fetch` for small apps or libraries that want zero dependencies. Use `axios` when you need shared interceptors (auth headers, token refresh, logging), uniform error handling, or upload progress in the browser. Both are fine in a team, so choose one and use it everywhere.

---

## 🔷 When to Use + When Not to Use
✅ Use `fetch` when:
- You want no dependency and the code is simple (one or two calls)
- You are writing a library and want a small bundle
- You run on Node 18+ and need HTTP without extra packages

✅ Use `axios` when:
- Many calls need the same headers, auth, or retry logic through interceptors
- You want non-2xx responses to be errors without writing a check each time
- You need upload progress in the browser (axios exposes it, plain `fetch` does not)

❌ Avoid:
- Calling `fetch` in a loop without a timeout or abort signal, because one stuck request can hang the page
- Using axios just to avoid writing `if (!res.ok)`; a small wrapper like `fetchJson` gives the same result
- Mixing both libraries in one codebase, which makes error handling inconsistent

---

## 📊 Visual Diagram
```
                 your code
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
  fetch(url, opts)          axios.get(url, cfg)
        │                         │
        │                  request interceptors
        │                         │
        ▼                         ▼
  ┌───────────── network ─────────────┐
  │   server answers: 200 / 404 / 500 │
  └───────────────────────────────────┘
        │                         │
  Promise resolves          2xx? resolve (data parsed)
  for ANY status            non-2xx? reject (err.response)
  you check res.ok          network error? reject
        │                         │
        ▼                         ▼
  res.json() / res.text()    response.data (already parsed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fetch | Built-in API that returns a Promise of a Response | Built-in API जो Response का Promise देता है |
| Response | Object with status, headers, and a readable body | Status, headers और body वाला object |
| res.ok | True when the status is 200 to 299 | Status 200 से 299 हो तो true |
| axios | Third-party HTTP client with interceptors | Interceptors वाला third-party HTTP client |
| Interceptor | Function that runs before each request or response | हर request या response से पहले चलने वाला function |
| AbortSignal.timeout | Signal that aborts after a set time | तय समय के बाद abort करने वाला signal |
| TimeoutError | Error name when a timeout signal fires | Timeout signal चलने पर error का नाम |
| Body is unusable | Error when a response body is read twice | Body दो बार पढ़ने पर आने वाला error |
| Backoff | Waiting longer before each retry | हर retry से पहले ज़्यादा इंतज़ार |

---

## ⚡ 3-Line Summary
**English:**
1. `fetch` is built in and resolves for every HTTP status, so check `res.ok` yourself.
2. `axios` adds JSON parsing, errors for non-2xx, interceptors, and timeouts, at the cost of a dependency.
3. Pick `fetch` for simple and small code, and `axios` when shared rules like auth and retries matter.

**Hindi:**
1. `fetch` पहले से मौजूद है और हर HTTP status पर resolve होता है, इसलिए `res.ok` खुद जाँचें।
2. `axios` JSON parsing, non-2xx पर error, interceptors और timeout देता है, पर एक dependency के साथ।
3. सरल code के लिए `fetch` चुनें, और auth या retry जैसे साझा नियम हों तो `axios`।

---

## ➡️ Next Topic
**163. WebSockets in JavaScript** — अब सीखेंगे कि server और browser के बीच लगातार खुला connection कैसे रहता है, जिसमें दोनों तरफ़ से कभी भी messages भेजे जा सकते हैं।
