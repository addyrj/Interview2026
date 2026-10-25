# 87. Request + Response Objects
# हिंदी में: Request और Response Objects

---

## 🔵 Simple Definition (English)
In every Express route handler `(req, res) => {}`, **`req`** (request) carries data about the incoming HTTP request — URL, headers, body, params, query. **`res`** (response) is used to send data back to the client — JSON, status codes, headers, redirects. Both are enhanced versions of Node's core `http.IncomingMessage` and `http.ServerResponse`.

## 🔵 सरल परिभाषा (Hindi)
हर Express route handler `(req, res) => {}` में, **`req`** (request) incoming HTTP request की data रखता है — URL, headers, body, params, query। **`res`** (response) client को data वापस भेजने के लिए use होता है — JSON, status codes, headers, redirects। दोनों Node के core `http.IncomingMessage` और `http.ServerResponse` के enhanced versions हैं।

---

## 🔴 Problem it Solves
```
WITH RAW http MODULE:
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const query = url.searchParams;        // manual query parsing
    let body = '';
    req.on('data', chunk => body += chunk); // manual body buffering
    req.on('end', () => {
      const data = JSON.parse(body);        // manual JSON parsing
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true })); // manual response formatting
    });
  });

WITH EXPRESS req/res:
  app.post('/data', (req, res) => {
    console.log(req.query, req.params, req.body);  // already parsed!
    res.status(200).json({ ok: true });              // one-liner response
  });
```

## 🔴 यह क्यों बना? (Hindi)
Raw Node `http` module में request data (query, body) manually parse करना पड़ता था और response manually format करना पड़ता था — बहुत boilerplate। Express ने `req` और `res` को extend करके ready-made properties (`req.query`, `req.params`, `req.body`) और helper methods (`res.json`, `res.status`, `res.redirect`) दे दिए, जिससे handler code छोटा और readable हो गया।

---

## 🟢 How it Works — Step by Step

Step 1 → Node creates raw `http.IncomingMessage` (req) and `http.ServerResponse` (res) objects for each request
Step 2 → Express wraps/extends these with its own prototype methods (`req.params`, `res.json`, etc.) via `Object.setPrototypeOf` internally
Step 3 → Middleware (e.g., `express.json()`) populate `req.body` by parsing the raw request stream
Step 4 → Route matching populates `req.params` (from URL segments) and `req.query` (from `?key=value`)
Step 5 → Handler reads from `req`, writes to `res` — calling a terminal method like `res.send()`/`res.json()`/`res.end()` completes the cycle

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node हर request के लिए raw `http.IncomingMessage` (req) और `http.ServerResponse` (res) बनाता है
Step 2 → Express इनको अपने prototype methods से extend करता है (`req.params`, `res.json`, आदि)
Step 3 → Middleware (जैसे `express.json()`) raw stream parse करके `req.body` भरते हैं
Step 4 → Route matching से `req.params` (URL segments से) और `req.query` (`?key=value` से) भरते हैं
Step 5 → Handler `req` से पढ़ता है, `res` में लिखता है — `res.send()`/`res.json()`/`res.end()` call होने पर cycle पूरा होता है

---

## 🟡 Real World Example
**Paytm wallet API:** `GET /api/wallet/:userId/transactions?limit=20&page=2` — Express parses `req.params.userId` from the URL path, `req.query.limit` and `req.query.page` from the query string. The handler fetches transactions and responds with `res.status(200).json({ transactions, page, totalPages })`. If the user isn't found, `res.status(404).json({ error: 'User not found' })` — all without manual URL parsing.

## 🟡 Real Example Hindi mein
**Paytm wallet API:** `GET /api/wallet/:userId/transactions?limit=20&page=2` — Express `req.params.userId` को URL path से और `req.query.limit`, `req.query.page` को query string से parse करता है। Handler transactions fetch करता है और `res.status(200).json({ transactions, page, totalPages })` से respond करता है। User नहीं मिला तो `res.status(404).json({ error: 'User not found' })` — बिना manual URL parsing के।

---

## 💻 Code Example — Basic

```javascript
// req-res-basics.js
const express = require('express');
const app = express();

app.use(express.json());   // needed to populate req.body

// Demonstrates key req properties
app.get('/api/items/:id', (req, res) => {
  console.log(req.params);   // { id: '42' }  — route params
  console.log(req.query);    // { sort: 'price' } for ?sort=price
  console.log(req.headers);  // all request headers object
  console.log(req.method);   // 'GET'
  console.log(req.path);     // '/api/items/42'
  console.log(req.ip);       // client IP address

  res.status(200).json({    // res.status() sets HTTP status code
    id: req.params.id,
    sort: req.query.sort || 'default',
  });
});

// Demonstrates key res methods
app.post('/api/items', (req, res) => {
  console.log(req.body);     // parsed JSON body, e.g. { name: 'Pizza' }

  res.set('X-Custom-Header', 'value');  // set a response header
  res.status(201).json({ created: true, data: req.body });  // chainable
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// req-res-advanced.js — common production patterns

const express = require('express');
const app = express();
app.use(express.json());

// Custom request-scoped data (common pattern: attach things to req)
app.use((req, res, next) => {
  req.startTime = Date.now();              // custom property for timing
  req.requestId = Math.random().toString(36).slice(2);  // trace ID
  next();
});

app.get('/api/orders/:orderId', async (req, res, next) => {
  try {
    const { orderId } = req.params;

    // req.query with defaults and type coercion (query values are always strings!)
    const includeItems = req.query.includeItems === 'true';
    const page = parseInt(req.query.page, 10) || 1;

    // Simulate DB fetch
    const order = await findOrder(orderId);
    if (!order) {
      // Early return with 404 — terminal response, nothing after runs
      return res.status(404).json({
        error: 'Order not found',
        requestId: req.requestId,
      });
    }

    const duration = Date.now() - req.startTime;
    res.set('X-Response-Time', `${duration}ms`);  // custom header

    res.status(200).json({
      order,
      items: includeItems ? order.items : undefined,
      page,
      requestId: req.requestId,
    });
  } catch (err) {
    next(err);  // pass to error-handling middleware
  }
});

async function findOrder(id) {
  // mock async DB call
  return id === '404' ? null : { id, total: 599, items: ['Pizza', 'Coke'] };
}

// res methods comparison: send vs json vs end
app.get('/compare', (req, res) => {
  // res.json(obj)   → JSON.stringify + sets Content-Type: application/json
  // res.send(str)   → sends string/buffer, auto-detects Content-Type
  // res.end()       → raw, no body processing, lowest-level
  res.json({ note: 'res.json is most common for APIs' });
});

app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, requestId: req.requestId });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Common req/res patterns inside a real Express app

app.get('/api/products', (req, res) => {
  // Destructure query params with defaults
  const { category = 'all', minPrice, maxPrice, sort = 'name' } = req.query;

  // req.get(headerName) — shortcut to read a specific header
  const acceptLanguage = req.get('Accept-Language');

  // res.location() + res.redirect() for redirects
  if (category === 'legacy') {
    return res.redirect(301, '/api/v2/products');  // permanent redirect
  }

  // res.vary() tells caches that response varies by this header
  res.vary('Accept-Language');

  res.status(200).json({ category, minPrice, maxPrice, sort, acceptLanguage });
});

// req.is() — check content-type of incoming request
app.post('/api/upload', (req, res) => {
  if (!req.is('multipart/form-data')) {
    return res.status(415).json({ error: 'Unsupported Media Type' });
  }
  res.sendStatus(200);  // sends status code with its standard text body
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming `req.query` values are numbers/booleans
```javascript
// WRONG
app.get('/search', (req, res) => {
  if (req.query.page > 1) { }  // "2" > 1 works due to coercion, but risky
});

// CORRECT: explicitly parse
app.get('/search', (req, res) => {
  const page = parseInt(req.query.page, 10) || 1;  // always a string, convert explicitly
});
```

❌ **Mistake 2:** Sending multiple responses for one request
```javascript
// WRONG
app.get('/data', (req, res) => {
  res.json({ a: 1 });
  res.json({ b: 2 });  // ❌ Error: Cannot set headers after they are sent
});

// CORRECT: send exactly once, use return to stop execution
app.get('/data', (req, res) => {
  if (!someCondition) return res.status(400).json({ error: 'bad' });
  res.json({ a: 1 });
});
```

---

## 🧠 Tricky Interview Question

```javascript
app.get('/test', (req, res) => {
  res.status(404);
  res.json({ error: 'not found' });
  console.log(res.statusCode);  // what prints?
});
```
Answer: It prints `404`. `res.status(404)` sets `res.statusCode` and returns `res` (for chaining), it does NOT send the response immediately. `res.json()` is the terminal call that actually flushes headers and body to the client. Since `res.status()` already set `statusCode` before `res.json()` ran, `res.statusCode` is `404` by the time we log it — the response is sent with 404 once `res.json()` executes.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `req.params`, `req.query`, and `req.body`?
A1: `req.params` holds named URL segments from the route pattern (e.g., `/users/:id` → `req.params.id`). `req.query` holds the parsed query string (`?page=2&sort=asc` → `{ page: '2', sort: 'asc' }`) — all values are strings. `req.body` holds the parsed request body (JSON/form data), populated only if a body-parsing middleware like `express.json()` ran first; otherwise it's `undefined`.

Q2: What's the difference between `res.send()`, `res.json()`, and `res.end()`?
A2: `res.json(obj)` JSON-stringifies the argument and sets `Content-Type: application/json`. `res.send(data)` is more generic — it auto-detects type (string → `text/html`, object → calls `res.json` internally, Buffer → `application/octet-stream`). `res.end([data])` is the lowest-level, from core Node `http` — it just ends the response with optional raw data, no content-type magic, no object serialization.

Q3: How do you read a specific request header, and how do you set a response header?
A3: Read: `req.get('Header-Name')` or `req.headers['header-name']` (headers are lowercased by Node). Set: `res.set('Header-Name', 'value')` or `res.header(...)` (alias). You can also pass headers as an object: `res.set({ 'X-A': '1', 'X-B': '2' })`.

Q4: Why does `req.query.page > 1` sometimes behave unexpectedly?
A4: `req.query` values are always strings (query strings have no type info). JS coerces `"2" > 1` to `true` via numeric coercion, which works for simple comparisons, but breaks down for things like `"10" > "9"` as strings (`false`, since string comparison is lexicographic) — but `"10" > 9` is numeric coercion (`true`). To avoid confusing bugs, always explicitly `parseInt`/`Number()` query values before comparing.

Q5: Can you attach custom properties to `req` in middleware, and is that safe?
A5: Yes — this is a very common Express pattern (e.g., `req.user = decodedToken`, `req.requestId = uuid()`). It's safe because `req` is a fresh object per request (not shared across requests), so there's no risk of leaking data between different users' requests, unlike module-level global variables. Always ensure the middleware that sets it runs before any handler that reads it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every Express route handler — `req`/`res` are the fundamental building blocks, always present
- Reading client input (`req.params`, `req.query`, `req.body`) and sending structured output (`res.json`)

❌ Avoid when:
- Needing raw socket-level control beyond what Express exposes — drop to `req.socket` / Node's `net` module for very low-level needs
- Streaming very large responses where you might prefer working with `res` as a writable stream directly (`res.write()`/`res.pipe()`) rather than buffering a full JSON object

---

## 📊 Visual Diagram
```
  INCOMING HTTP REQUEST
  GET /api/items/42?sort=price
  Headers: { authorization: 'Bearer xyz' }
       │
       ▼
  ┌───────────────────────────────┐
  │           req object           │
  │  req.method = 'GET'            │
  │  req.path   = '/api/items/42'  │
  │  req.params = { id: '42' }     │
  │  req.query  = { sort: 'price' }│
  │  req.headers = {...}           │
  │  req.body   = (set by middleware)│
  └───────────────┬─────────────────┘
                  │  handler reads req
                  ▼
  ┌───────────────────────────────┐
  │           res object           │
  │  res.status(200)               │
  │  res.set('X-Header', 'v')      │
  │  res.json({ ... })  ← terminal │
  └───────────────┬─────────────────┘
                  ▼
        HTTP RESPONSE sent to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `req.params` | Named URL segments | Named URL segments |
| `req.query` | Parsed query string (strings only) | Parsed query string (सब strings) |
| `req.body` | Parsed request body | Parse किया हुआ request body |
| `res.json()` | Send JSON response | JSON response भेजना |
| `res.status()` | Set HTTP status code (chainable) | HTTP status code set करना |
| Terminal method | Method that finalizes/sends response | Response को finalize करने वाला method |

---

## ⚡ 3-Line Summary
English: 1. `req` carries incoming data (`params`, `query`, `body`, `headers`); `res` sends outgoing data (`status`, `json`, `send`). 2. `req.query` and `req.params` values are always strings — parse explicitly for numeric comparisons. 3. Only call one terminal response method (`res.json`/`res.send`/`res.end`) per request — calling more throws "headers already sent."
Hindi: 1. `req` आने वाला data रखता है (`params`, `query`, `body`, `headers`); `res` जाने वाला data भेजता है (`status`, `json`, `send`)। 2. `req.query` और `req.params` के values हमेशा strings होते हैं — numeric comparison से पहले parse करो। 3. एक request के लिए सिर्फ एक terminal method call करो, वरना "headers already sent" error आएगा।

---

## ➡️ Next Topic
**88. Routes — Complete Guide** — Defining routes with all HTTP methods, path patterns, and route matching rules.
