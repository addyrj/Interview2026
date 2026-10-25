# 85. Fetch API
# हिंदी में: Fetch API — Browser और Node.js में HTTP Requests करना

---

## 🔵 Simple Definition (English)
`fetch(url, options)` is the built-in, promise-based way to make HTTP requests in browsers and in Node.js 18+. It returns a Promise that resolves with a `Response` object. Important: it rejects only on network failure, not on HTTP errors like 404 or 500, so you must check `response.ok` yourself.

## 🔵 सरल परिभाषा (Hindi)
`fetch(url, options)` browser और Node.js 18+ में HTTP requests करने का built-in, promise-based तरीका है। यह एक Promise लौटाता है जो `Response` object के साथ resolve होता है। ध्यान रखें: यह सिर्फ network failure पर reject होता है, 404 या 500 जैसे HTTP errors पर नहीं, इसलिए `response.ok` खुद चेक करना होता है।

---

## 🔴 Problem it Solves
Before `fetch`, browsers used `XMLHttpRequest` (topic 86), which was callback-based and verbose. Developers wrote wrapper libraries (jQuery `$.ajax`) to get promises. `fetch` standardized the promise-based API, works with streams, and is available in the same form on the server (Node.js), so one HTTP API works on both sides.

## 🔴 यह क्यों बना? (Hindi)
`fetch` से पहले browsers में `XMLHttpRequest` (topic 86) था, जो callback-based और लंबा था। Developers को promise पाने के लिए jQuery `$.ajax` जैसी libraries लेनी पड़ती थीं। `fetch` ने promise-based API को standard बनाया, streams के साथ काम करता है, और server (Node.js) पर भी वही API है, इसलिए एक ही HTTP API दोनों तरफ चलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `fetch(url, options)` starts the HTTP request and returns a Promise
Step 2 → The promise resolves with a `Response` as soon as HTTP headers arrive (body may still be streaming)
Step 3 → The promise REJECTS only for network problems (DNS failure, offline, CORS block, abort)
Step 4 → HTTP 404 or 500 still RESOLVES; check `response.ok` (true for status 200–299) or `response.status`
Step 5 → Read the body with `response.json()`, `response.text()`, or `response.blob()`; each can be called only once
Step 6 → Options: `method`, `headers`, `body` (must be a string for JSON), `signal` (for cancel, topic 88)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `fetch(url, options)` HTTP request शुरू करता है और Promise लौटाता है
Step 2 → HTTP headers आते ही Promise `Response` के साथ resolve हो जाता है (body अभी stream हो रही हो सकती है)
Step 3 → Promise सिर्फ network problems पर REJECT होता है (DNS fail, offline, CORS block, abort)
Step 4 → HTTP 404 या 500 पर भी RESOLVE होता है; `response.ok` (200–299 के लिए true) या `response.status` खुद चेक करो
Step 5 → Body `response.json()`, `response.text()`, या `response.blob()` से पढ़ो; हर एक सिर्फ एक बार call हो सकता है
Step 6 → Options: `method`, `headers`, `body` (JSON के लिए string), `signal` (cancel के लिए, topic 88)

---

## 🟡 Real World Example
On Swiggy's restaurant search, the browser calls `fetch("/api/restaurants?city=Mumbai&q=biryani")`. If the user's network drops, `fetch` rejects and the app shows "No internet". If the server returns 404 because the restaurant was removed, `fetch` resolves, so the code must check `response.ok` and show "Restaurant not found" instead.

## 🟡 Real Example Hindi mein
Swiggy पर restaurant search में browser `fetch("/api/restaurants?city=Mumbai&q=biryani")` call करता है। अगर user का net चला जाए, तो `fetch` reject होता है और app "No internet" दिखाता है। अगर restaurant हट गया हो और server 404 दे, तो `fetch` resolve होता है, इसलिए code को `response.ok` चेक करके "Restaurant नहीं मिला" दिखाना होगा।

---

## 💻 Code Example — Basic
```javascript
// Stub fetch so this runs offline (no real network). Real fetch has the same return shape.
globalThis.fetch = async (url, options = {}) => {
  await new Promise((r) => setTimeout(r, 10));                  // fake latency
  if (url.includes("/offline")) throw new TypeError("Failed to fetch"); // network failure: REJECTS
  if (url.endsWith("/users/404")) {                              // HTTP error: RESOLVES with ok=false
    return { ok: false, status: 404, json: async () => ({ error: "no user" }) };
  }
  return {                                                       // success response
    ok: true,
    status: 200,
    json: async () => ({ url, method: options.method ?? "GET", body: options.body ? JSON.parse(options.body) : null }),
  };
};

// Helper: GET a user and convert HTTP errors into thrown errors
async function getUser(id) {
  const res = await fetch(`https://api.example.com/users/${id}`); // no real request; stub answers
  if (!res.ok) throw new Error(`HTTP ${res.status}`);           // fetch does NOT throw on 404
  return res.json();                                             // parse JSON body (returns a promise)
}

(async () => {
  // 1. Successful GET
  console.log("1.", await getUser(1));                           // { url: ..., method: 'GET', body: null }

  // 2. HTTP 404: fetch resolved, so our own check throws
  try {
    await getUser("404");                                        // URL ends with /users/404
  } catch (err) {
    console.log("2.", err.message);                              // "HTTP 404"
  }

  // 3. Query string built safely with URLSearchParams
  const params = new URLSearchParams({ city: "Mumbai", page: 2 }); // city=Mumbai&page=2
  const res = await fetch(`https://api.example.com/restaurants?${params}`);
  console.log("3.", (await res.json()).url);                    // ends with ?city=Mumbai&page=2

  // 4. POST with a JSON body (headers + JSON.stringify are required)
  const created = await fetch("https://api.example.com/orders", {
    method: "POST",                                              // HTTP method
    headers: { "Content-Type": "application/json" },             // tell the server it is JSON
    body: JSON.stringify({ item: "Biryani", qty: 2 }),           // body must be a string
  });
  console.log("4.", (await created.json()).body);                // { item: 'Biryani', qty: 2 }

  // 5. Network failure: fetch itself rejects
  try {
    await fetch("https://api.example.com/offline");              // stub throws TypeError
  } catch (err) {
    console.log("5.", err.name, err.message);                    // TypeError Failed to fetch
  }
})();
```

**Expected output (basic):**
```
1. { url: 'https://api.example.com/users/1', method: 'GET', body: null }
2. HTTP 404
3. https://api.example.com/restaurants?city=Mumbai&page=2
4. { item: 'Biryani', qty: 2 }
5. TypeError Failed to fetch
```

## 💻 Code Example — Advanced
```javascript
// Advanced: retry on 5xx and network errors, per-attempt timeout, no retry on 4xx.
// The stub below honors AbortSignal, like real fetch does.

let serverCalls = 0;                                             // counts calls to /server-error
globalThis.fetch = async (url, options = {}) => {                // stub fetch (offline demo)
  if (url.includes("/offline")) throw new TypeError("Failed to fetch");   // network error
  if (url.includes("/slow")) {                                   // slow route: wait unless aborted
    await new Promise((resolve, reject) => {
      const t = setTimeout(resolve, 500);                        // would take 500ms
      options.signal?.addEventListener("abort", () => {          // if the signal aborts first
        clearTimeout(t);                                         // stop the wait
        reject(options.signal.reason);                           // reject like real fetch
      });
    });
  }
  if (url.includes("/server-error") && ++serverCalls < 3) {      // first two calls fail
    return { ok: false, status: 503, json: async () => ({}) };
  }
  if (url.endsWith("/users/404")) return { ok: false, status: 404, json: async () => ({}) };
  await new Promise((r) => setTimeout(r, 10));                   // normal latency
  return { ok: true, status: 200, json: async () => ({ url, method: options.method ?? "GET", body: null }) };
};

// Retry wrapper around fetch that returns parsed JSON
async function fetchJson(url, { retries = 2, timeoutMs = 1000, ...init } = {}) {
  let lastError;                                                 // remember the last failure
  for (let attempt = 0; attempt <= retries; attempt++) {         // attempt 0 is the first try
    try {
      const res = await fetch(url, {
        ...init,                                                 // pass method, headers, body
        signal: AbortSignal.timeout(timeoutMs),                  // this attempt aborts after timeoutMs
      });
      if (res.status >= 500) throw new Error(`server error ${res.status}`); // 5xx: retry
      if (!res.ok) {                                             // 4xx: client mistake, do not retry
        const err = new Error(`HTTP ${res.status}`);
        err.retryable = false;                                   // mark as not retryable
        throw err;
      }
      return await res.json();                                   // success: return parsed body
    } catch (err) {
      lastError = err;                                           // save this failure
      if (err.retryable === false) break;                        // 4xx: stop immediately
      console.log(`attempt ${attempt + 1} failed: ${err.message}`); // log retryable failure
      await new Promise((r) => setTimeout(r, 20 * (attempt + 1))); // small growing wait
    }
  }
  throw lastError;                                               // all attempts failed
}

(async () => {
  // 1. Two 503s, then success on the third attempt
  console.log(await fetchJson("https://api.example.com/server-error"));

  // 2. 404 is not retried
  try {
    await fetchJson("https://api.example.com/users/404");
  } catch (err) {
    console.log("no retry:", err.message, err.retryable);     // no retry: HTTP 404 false
  }

  // 3. Timeout: the slow route takes 500ms, our limit is 100ms, no retries
  try {
    await fetchJson("https://api.example.com/slow", { retries: 0, timeoutMs: 100 });
  } catch (err) {
    console.log("timeout:", err.name);                            // timeout: TimeoutError
  }
})();
```

**Expected output (advanced):**
```
attempt 1 failed: server error 503
attempt 2 failed: server error 503
{
  url: 'https://api.example.com/server-error',
  method: 'GET',
  body: null
}
no retry: HTTP 404 false
attempt 1 failed: The operation was aborted due to timeout
timeout: TimeoutError
```

---

## 🟠 Express.js Integration
Node.js 18+ has `fetch` built in, so an Express route can call another HTTP service without any package. A common use is a backend-for-frontend route that calls a payment or shipping API, adds a timeout, and maps upstream errors to clean responses.

```javascript
// Express.js example: calling an upstream API with fetch (Node 18+)
const express = require("express");                 // import Express
const app = express();                              // create the app

app.get("/api/shipping/:pin", async (req, res, next) => {  // route with a PIN code param
  try {
    const upstream = await fetch(                   // call the external shipping API
      `https://shipping.example.com/rates/${req.params.pin}`, // URL built from the param
      { signal: AbortSignal.timeout(2000) }         // give up after 2 seconds
    );
    if (upstream.status === 404) {                  // unknown PIN code
      return res.status(404).json({ error: "PIN not serviceable" });
    }
    if (!upstream.ok) {                             // any other HTTP error from upstream
      return res.status(502).json({ error: "shipping service error" }); // 502 Bad Gateway
    }
    res.json(await upstream.json());                // forward the JSON to our client
  } catch (err) {                                   // network error or timeout lands here
    next(err);                                      // send to Express error middleware
  }
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming `fetch` rejects on 404 or 500
✅ **Correct:** Check `response.ok` (or `status`) yourself.

```javascript
// Wrong: a 500 response is silently treated as data
const res = await fetch("/api/menu");
const menu = await res.json();          // might be an error object, not a menu

// Right: convert HTTP errors into exceptions
const res2 = await fetch("/api/menu");
if (!res2.ok) throw new Error(`HTTP ${res2.status}`);
const menu2 = await res2.json();
```

❌ **Mistake 2:** Reading the body twice
✅ **Correct:** Read the body once and store the result.

```javascript
// Wrong: the second read throws "Body is unusable"
const res = await fetch("/api/user");
const a = await res.json();
const b = await res.json();             // TypeError: body already read

// Right: store the parsed value
const res2 = await fetch("/api/user");
const data = await res2.json();         // read once; reuse `data`
```

❌ **Mistake 3:** Sending a JSON object as `body` without `JSON.stringify` and the header
✅ **Correct:** Stringify the body and set `Content-Type: application/json`.

```javascript
// Wrong: body becomes "[object Object]" and the server cannot parse it
await fetch("/api/orders", { method: "POST", body: { item: "Dosa" } });

// Right
await fetch("/api/orders", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ item: "Dosa" }),
});
```

---

## 🧠 Tricky Interview Output Question
```javascript
// A Response built locally (same class fetch returns) with status 404
const res = new Response(JSON.stringify({ id: 1 }), { status: 404 });

console.log("ok?", res.ok, "status:", res.status);  // what is printed?

(async () => {
  console.log(await res.json());                    // first read: works
  try {
    await res.json();                               // second read: ?
  } catch (err) {
    console.log("error name:", err.name);           // what is the error name?
  }
})();
```
**Answer:**
```
ok? false status: 404
{ id: 1 }
error name: TypeError
```
**Why:** `res.ok` is `false` because the status is 404, which is outside 200–299. That is the same check you must do with real `fetch`, because `fetch` would resolve with this response instead of rejecting. The body is a stream, and it can be consumed only once. The first `res.json()` reads it and returns `{ id: 1 }`. The second call finds the body already used and throws a `TypeError` ("Body is unusable").

---

## ⚫ Interview Questions + Answers

Q1: Does `fetch` reject when the server returns 500?
A1: No. It rejects only for network-level failures (DNS, offline, CORS, abort). HTTP error statuses still resolve, so check `response.ok`.

Q2: What does `response.ok` mean?
A2: It is `true` when the status is in the range 200 to 299, and `false` otherwise.

Q3: How do you send JSON with `fetch`?
A3: Set `method` to `"POST"` (or PUT/PATCH), set the header `Content-Type: application/json`, and pass `body: JSON.stringify(data)`.

Q4: Can you call `response.json()` twice?
A4: No. The body is a stream that can be read once. Store the result in a variable if you need it more than once, or use `response.clone()` before reading.

Q5: How do you add a timeout to `fetch`?
A5: Pass `signal: AbortSignal.timeout(ms)` (Node 17.3+ and modern browsers). The request aborts after `ms` milliseconds. Topic 88 covers `AbortController` in depth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need HTTP calls in browsers or Node.js 18+ without extra packages
- You want promise-based code that works with `async`/`await`
- You need streaming bodies (`response.body` is a ReadableStream)

❌ Avoid when:
- You must support very old browsers (IE11) without a polyfill
- You need upload progress events (`fetch` does not expose them; use XHR or a library)
- You rely on automatic rejection on HTTP errors; write a helper that throws instead

---

## 📊 Visual Diagram
```
fetch(url, options)  ──► Promise<Response>
        │
        ├── network error (offline, DNS, CORS, abort)  ──► REJECT (TypeError / AbortError)
        │
        └── HTTP response arrives (any status)          ──► RESOLVE with Response
                 │
                 ├── response.ok === true   (200–299)  ──► await response.json()  ──► data
                 │
                 └── response.ok === false  (404, 500) ──► YOU throw or handle it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `fetch` | Built-in promise-based HTTP function | Built-in HTTP function |
| `Response` | Object with status, headers and body | Status, headers और body वाला object |
| `response.ok` | True for status 200–299 | 200–299 status के लिए true |
| Network error | Request never got an HTTP response | HTTP response तक पहुँचा ही नहीं |
| `Content-Type` | Header that describes the body format | Body का format बताने वाला header |
| `AbortSignal.timeout` | Signal that aborts after given ms | दिए गए ms बाद abort होने वाला signal |
| Body stream | Response body can be read only once | Body सिर्फ एक बार पढ़ी जा सकती है |

---

## ⚡ 3-Line Summary
**English:**
1. `fetch` returns a promise of a `Response`; it rejects only for network failures.
2. Always check `response.ok` and read the body once with `json()`, `text()`, or `blob()`.
3. Send JSON with `JSON.stringify` and the `Content-Type` header, and add a timeout with `AbortSignal.timeout`.

**Hindi:**
1. `fetch` एक `Response` का promise लौटाता है; यह सिर्फ network failure पर reject होता है।
2. हमेशा `response.ok` चेक करो और body को `json()`, `text()` या `blob()` से एक बार पढ़ो।
3. JSON भेजने के लिए `JSON.stringify` और `Content-Type` header लगाओ, और timeout के लिए `AbortSignal.timeout` इस्तेमाल करो।

---

## ➡️ Next Topic
**86. XMLHttpRequest (legacy)** — `fetch` replaced the older callback-based API. Learn how `XMLHttpRequest` works, why it still matters in legacy code and interviews, and how to wrap it in a promise.
