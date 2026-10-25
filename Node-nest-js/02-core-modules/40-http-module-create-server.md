# 40. http Module — Create Server
# हिंदी में: http Module — Server बनाना

---

## 🔵 Simple Definition (English)
The **`http`** module is Node's built-in API for creating HTTP servers and clients WITHOUT any external framework. `http.createServer()` builds a raw server that listens for requests and sends responses — it's the low-level foundation that Express and every other Node web framework are built on top of.

## 🔵 सरल परिभाषा (Hindi)
**`http`** module Node का built-in API है HTTP servers और clients बनाने के लिए बिना किसी external framework के। `http.createServer()` एक raw server बनाता है जो requests सुनता है और responses भेजता है — यह वो low-level foundation है जिस पर Express और हर दूसरा Node web framework बना है।

---

## 🔴 Problem it Solves
Before Node, handling raw TCP/HTTP traffic for a web server typically meant working with lower-level languages (C, or server software like Apache/Nginx with CGI scripts) — JavaScript had no native way to listen for network requests at all. Node's `http` module gave JavaScript the ability to directly accept HTTP connections, parse requests, and send responses, making it possible to write an entire web server in JS with just a few lines, no external process needed. Understanding `http` directly matters because it reveals EXACTLY what Express does under the hood — every `req`/`res` object, every middleware call, ultimately interacts with this module's primitives.

## 🔴 यह क्यों बना? (Hindi)
Node से पहले, raw TCP/HTTP traffic handle करने के लिए web server के लिए typically lower-level languages चाहिए होती थीं (C, या Apache/Nginx जैसा server software CGI scripts के साथ) — JavaScript के पास network requests सुनने का कोई native तरीका नहीं था। Node के `http` module ने JavaScript को directly HTTP connections accept करने, requests parse करने, और responses भेजने की ability दी, पूरा web server JS में सिर्फ कुछ lines में बिना किसी external process के लिखना possible बनाया। `http` को directly समझना matter करता है क्योंकि यह EXACTLY दिखाता है कि Express नीचे क्या करता है — हर `req`/`res` object, हर middleware call, आखिर में इस module के primitives से interact करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `const http = require('http')` or `require('node:http')`.
Step 2 → `http.createServer((req, res) => { ... })` creates a server instance — the callback runs ONCE PER INCOMING REQUEST, receiving `req` (IncomingMessage — a Readable stream with request data) and `res` (ServerResponse — a Writable stream used to send the response).
Step 3 → `req.method`, `req.url`, `req.headers` give basic request info. For POST/PUT bodies, you must manually collect data chunks (`req.on('data', chunk => ...)`) since `req` itself is a STREAM, not a pre-parsed object — THIS is exactly what body-parsing middleware (`express.json()`) automates for you.
Step 4 → `res.writeHead(statusCode, headers)` sets the status and headers; `res.write(chunk)` sends body data (can be called multiple times for streaming); `res.end([data])` finalizes and sends the response, optionally with final data.
Step 5 → `server.listen(port, callback)` starts the server listening for incoming connections on the specified port.
Step 6 → Routing, JSON body parsing, static file serving, and middleware chains are ALL things `http` does NOT provide natively — frameworks like Express exist specifically to add these conveniences on top of the raw `http` module.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const http = require('http')` या `require('node:http')`।
Step 2 → `http.createServer((req, res) => { ... })` एक server instance बनाता है — callback हर INCOMING REQUEST के लिए एक बार चलता है, `req` (IncomingMessage — request data वाला एक Readable stream) और `res` (ServerResponse — response भेजने के लिए एक Writable stream) receive करता है।
Step 3 → `req.method`, `req.url`, `req.headers` basic request info देते हैं। POST/PUT bodies के लिए, data chunks manually collect करने होते हैं (`req.on('data', chunk => ...)`) क्योंकि `req` खुद एक STREAM है, pre-parsed object नहीं — यही exactly body-parsing middleware (`express.json()`) आपके लिए automate करता है।
Step 4 → `res.writeHead(statusCode, headers)` status और headers set करता है; `res.write(chunk)` body data भेजता है (streaming के लिए कई बार call हो सकता है); `res.end([data])` response finalize और भेजता है, optionally final data के साथ।
Step 5 → `server.listen(port, callback)` specified port पर incoming connections सुनना शुरू करता है।
Step 6 → Routing, JSON body parsing, static file serving, और middleware chains ये सब `http` natively नहीं देता — Express जैसे frameworks exactly इन्हीं conveniences को raw `http` module के ऊपर add करने के लिए exist करते हैं।

---

## 🟡 Real World Example
**Razorpay's internal webhook-receiving microservice:** For maximum performance on a hot path receiving thousands of payment webhook callbacks per second, the team built a minimal raw `http` server instead of using Express — bypassing the overhead of a full routing/middleware framework for this single-purpose endpoint. It manually parses the single expected route, validates the signature header, reads the raw body stream, and responds with a 200 — shaving off microseconds per request that matter at extreme scale, while most of their other, more complex services still use Express for its productivity benefits.

## 🟡 Real Example Hindi mein
**Razorpay का internal webhook-receiving microservice:** Hot path पर maximum performance के लिए जो हर second हज़ारों payment webhook callbacks receive करता है, team ने Express use करने की जगह एक minimal raw `http` server बनाया — इस single-purpose endpoint के लिए पूरे routing/middleware framework के overhead को bypass करते हुए। यह manually single expected route parse करता है, signature header validate करता है, raw body stream पढ़ता है, और 200 के साथ respond करता है — हर request पर microseconds बचाता है जो extreme scale पर matter करते हैं, जबकि उनकी बाकी ज्यादा complex services अभी भी Express use करती हैं अपने productivity benefits के लिए।

---

## 💻 Code Example — Basic

```javascript
// httpBasics.js — a raw Node.js HTTP server, no framework
const http = require('http');

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`); // log every incoming request

  // Basic manual routing (Express automates this with app.get/app.post etc.)
  if (req.url === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Welcome to the homepage!');
  } else if (req.url === '/about' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('About this server.');
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000');
});

// Try: curl http://localhost:3000/
// Try: curl http://localhost:3000/about
// Try: curl http://localhost:3000/missing  → 404 Not Found
```

## 💻 Code Example — Advanced

```javascript
// httpAdvanced.js — manually handling JSON body parsing (what Express automates)
const http = require('http');
const { URL } = require('url');

function parseJSONBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';

    // req is a READABLE STREAM — body data arrives in chunks over time
    req.on('data', (chunk) => {
      body += chunk.toString(); // accumulate chunks into a full string
    });

    req.on('end', () => {
      // 'end' fires once ALL chunks have arrived
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(new Error('Invalid JSON body'));
      }
    });

    req.on('error', reject); // handle stream errors (e.g., connection dropped mid-upload)
  });
}

function sendJSON(res, statusCode, data) {
  const json = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(json), // important for HTTP/1.1 keep-alive correctness
  });
  res.end(json);
}

const users = [{ id: 1, name: 'Aditya' }]; // in-memory "database" for this example

const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);

  try {
    if (parsedUrl.pathname === '/users' && req.method === 'GET') {
      return sendJSON(res, 200, users);
    }

    if (parsedUrl.pathname === '/users' && req.method === 'POST') {
      const body = await parseJSONBody(req); // manually parse the request body
      const newUser = { id: users.length + 1, name: body.name };
      users.push(newUser);
      return sendJSON(res, 201, newUser);
    }

    sendJSON(res, 404, { error: 'Not Found' });
  } catch (err) {
    sendJSON(res, 400, { error: err.message }); // e.g., malformed JSON body
  }
});

server.listen(3000, () => console.log('Advanced raw HTTP server running on port 3000'));

// Try: curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"name":"Riya"}'
```

---

## 🟠 Express.js Integration

```javascript
// comparison.js — same logic, raw http vs Express, side by side

// ─── RAW http (what you'd have to write manually) ───────────────────────────
const http = require('http');
http.createServer((req, res) => {
  if (req.url === '/ping' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'pong' }));
  } else {
    res.writeHead(404);
    res.end();
  }
}).listen(3001);

// ─── Express (same behavior, far less boilerplate) ──────────────────────────
const express = require('express');
const app = express();

app.get('/ping', (req, res) => {
  res.json({ message: 'pong' }); // Express handles Content-Type, serialization, status automatically
});

app.listen(3002, () => console.log('Express server on 3002'));

// IMPORTANT: Express's app itself is built by calling http.createServer(app)
// internally — app.listen(port) is really just a wrapper around:
//   http.createServer(app).listen(port)
// Every Express app IS a raw http server underneath, with Express providing
// routing, middleware, and convenience methods (res.json, res.send, etc.) on top.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that `req` is a stream and trying to read the body synchronously
```javascript
// Wrong — req.body doesn't exist on the raw http module; data arrives asynchronously
http.createServer((req, res) => {
  console.log(req.body); // undefined — raw http has NO built-in body parsing
}).listen(3000);

// Right — manually collect data events, or use Express's express.json() middleware
http.createServer((req, res) => {
  let body = '';
  req.on('data', (chunk) => { body += chunk; });
  req.on('end', () => {
    console.log(JSON.parse(body || '{}'));
    res.end('OK');
  });
}).listen(3000);
```

❌ Mistake 2: Forgetting `res.end()`, leaving requests hanging forever
```javascript
// Wrong — res.write() alone never finalizes the response; the client hangs waiting
http.createServer((req, res) => {
  res.writeHead(200);
  res.write('Hello'); // sent, but connection never closes!
}).listen(3000);

// Right — always call res.end() to signal the response is complete
http.createServer((req, res) => {
  res.writeHead(200);
  res.write('Hello');
  res.end(); // finalizes the response, client receives it and the connection can close/reuse
}).listen(3000);
```

---

## 🧠 Tricky Interview Question

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.end('Hello');
  res.end('World'); // called a second time
});

server.listen(3000);
// What happens when you request this?
```
Answer: The client receives **only `"Hello"`** — and the SECOND `res.end('World')` call throws an error: **`Error: write after end`**. Once `res.end()` is called, the HTTP response is considered COMPLETE and the underlying stream is closed for writing — any further attempt to write or end again is invalid and Node throws (which, if unhandled, could crash the process via an unhandled error event on the response stream). This demonstrates that `res` behaves like a Writable stream with a definite lifecycle: write any number of times, but `end()` exactly once, as the final action.

---

## ⚫ Interview Questions + Answers

Q1: What are `req` and `res` in a raw Node.js `http.createServer()` callback?
A1: `req` is an instance of `http.IncomingMessage` — it's a READABLE STREAM representing the incoming request, exposing properties like `method`, `url`, `headers`, and emitting `'data'`/`'end'` events as the body streams in. `res` is an instance of `http.ServerResponse` — a WRITABLE STREAM used to construct and send the response, via `writeHead()`, `write()`, and `end()`. Both are built on Node's Streams API, which is why body parsing requires manually handling stream events in raw `http`.

Q2: Why doesn't raw `http.createServer()` provide `req.body` or routing like Express does?
A2: The core `http` module is intentionally LOW-LEVEL — it only handles the raw protocol mechanics (parsing headers, exposing the body as a stream, sending responses). Parsing specific body formats (JSON, form data, multipart uploads) and providing declarative routing (`app.get()`, `app.post()`) are APPLICATION-LEVEL conveniences that vary by use case, which is exactly the gap frameworks like Express fill — they're built ON TOP of `http`, adding middleware chains, routers, and convenience methods (`res.json()`, `res.send()`) while `http.createServer(app)` still does the actual low-level listening underneath.

Q3: Is Express's `app.listen()` different from `http.createServer().listen()`?
A3: Not fundamentally — `app.listen(port)` is essentially a convenience wrapper that internally does `http.createServer(app).listen(port)`. The Express `app` itself is a request-handler FUNCTION compatible with `http.createServer()`'s expected callback signature `(req, res) => {...}` — Express just adds a lot of logic (routing, middleware) inside that function before eventually calling the equivalent of `res.end()`.

Q4: How would you stream a large response using raw `http` without loading everything into memory first?
A4: Call `res.write(chunk)` multiple times as data becomes available (e.g., piping a file read stream directly: `fs.createReadStream(path).pipe(res)` — since `res` is itself a Writable stream, it's pipe-compatible with any Readable source), then call `res.end()` once all data has been sent. This is identical to how Express/any Node HTTP-based framework streams large responses (e.g., file downloads, video streaming) under the hood.

Q5: What happens if you call `res.writeHead()` after already sending some data with `res.write()`?
A5: It throws an error — **`Error: Can't set headers after they are sent`** (or, more precisely here, after the response has started flushing). Headers must be set BEFORE any body data is written, because HTTP's wire format requires headers to come first in the response. This is a very common real-world bug source — e.g., calling `res.json()` in Express after already sending a partial response elsewhere in error-handling code triggers exactly this error.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Learning/understanding what frameworks like Express actually do underneath.
- Building extremely performance-sensitive, minimal single-purpose endpoints where framework overhead matters (rare, but real at extreme scale).
- Writing simple internal tools/scripts that need a tiny HTTP server without pulling in a framework dependency.

❌ Avoid when:
- Building any application with more than a couple of routes — manual routing/body-parsing quickly becomes unmaintainable; use Express/Fastify/another framework.
- You need middleware, structured error handling, or a routing system — reinventing these on raw `http` wastes time better spent on actual business logic.

---

## 📊 Visual Diagram
```
RAW http SERVER — REQUEST LIFECYCLE:
──────────────────────────────────────────────────────────

  Client sends HTTP request
         │
         ▼
  http.createServer(callback)
         │
         ▼
  callback(req, res) fires
    req  → IncomingMessage (Readable stream: method, url, headers, body chunks)
    res  → ServerResponse  (Writable stream: writeHead(), write(), end())
         │
         ▼
  Manually: check req.method/req.url → collect body via 'data'/'end' events
         │
         ▼
  res.writeHead(status, headers) → res.write(data)* → res.end()
         │
         ▼
  Response sent to client

  EXPRESS RELATIONSHIP:
    express()  →  a request-handler function
    app.listen(port)  ≈  http.createServer(app).listen(port)
    (Express adds routing/middleware INSIDE that function, http does the actual listening)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| http.createServer | Creates a raw HTTP server | Raw HTTP server बनाना |
| IncomingMessage (req) | Readable stream for the request | Request के लिए Readable stream |
| ServerResponse (res) | Writable stream for the response | Response के लिए Writable stream |
| writeHead() | Sets status code + headers | Status code + headers set करना |
| res.end() | Finalizes and sends the response | Response finalize और भेजना |
| Body parsing | Manually reading req stream data | req stream data manually पढ़ना |

---

## ⚡ 3-Line Summary
English: `http.createServer()` is Node's low-level building block for HTTP servers — `req`/`res` are Readable/Writable streams with NO built-in routing or body parsing, which is exactly what frameworks like Express add on top. `res.end()` must be called exactly once to complete a response, and headers must be set via `writeHead()` before any body data is written. Understanding raw `http` demystifies what Express does under the hood, since `app.listen()` is essentially `http.createServer(app).listen()`.
Hindi: `http.createServer()` Node का low-level building block है HTTP servers के लिए — `req`/`res` Readable/Writable streams हैं बिना किसी built-in routing या body parsing के, जो exactly Express जैसे frameworks ऊपर add करते हैं। Response पूरा करने के लिए `res.end()` exactly एक बार call होना चाहिए, और headers को body data लिखने से पहले `writeHead()` से set करना चाहिए। Raw `http` समझना demystify करता है कि Express नीचे क्या करता है, क्योंकि `app.listen()` essentially `http.createServer(app).listen()` ही है।

---

## ➡️ Next Topic
**41. https Module** — creating secure HTTP servers and making HTTPS requests with TLS/SSL.
