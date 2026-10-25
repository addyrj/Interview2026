# 86. Creating Express Server
# हिंदी में: Express Server बनाना

---

## 🔵 Simple Definition (English)
**Express** is a minimal, unopinionated web framework for Node.js built on top of the core `http` module. `express()` returns an `app` object that you use to define routes, middleware, and start a server with `app.listen(port)`. It removes the boilerplate of raw `http.createServer()` — routing, body parsing, and response helpers come built-in or via middleware.

## 🔵 सरल परिभाषा (Hindi)
**Express** Node.js के लिए एक minimal web framework है जो core `http` module के ऊपर बना है। `express()` एक `app` object return करता है जिससे routes, middleware define करते हैं और `app.listen(port)` से server start करते हैं। यह raw `http.createServer()` की boilerplate code हटा देता है — routing, body parsing, response helpers built-in या middleware से मिलते हैं।

---

## 🔴 Problem it Solves
```
WITH RAW http MODULE:
  const http = require('http');
  const server = http.createServer((req, res) => {
    if (req.url === '/users' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ users: [] }));
    } else if (req.url === '/orders' && req.method === 'POST') {
      // manually parse body chunks, buffer them, JSON.parse...
      // manually handle routing with if/else chains
      // manually set headers, status codes every time
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  });
  → Grows into an unmaintainable if/else routing mess for 100+ endpoints

WITH EXPRESS:
  const express = require('express');
  const app = express();
  app.get('/users', (req, res) => res.json({ users: [] }));
  app.post('/orders', (req, res) => res.json({ created: true }));
  app.listen(3000);
  → Clean, declarative routing. Middleware handles parsing, auth, logging.
```

## 🔴 यह क्यों बना? (Hindi)
Raw `http` module के साथ routing, body parsing, headers सब manually करना पड़ता था — 100+ endpoints के लिए if/else chain unmaintainable हो जाती थी। Express ने declarative routing (`app.get`, `app.post`), middleware system, और built-in helpers (`res.json`, `res.send`) देकर यह सब simplify कर दिया। Express 2010 में TJ Holowaychuk ने बनाया था, Sinatra (Ruby) से inspired होकर।

---

## 🟢 How it Works — Step by Step

Step 1 → Install express: `npm install express`
Step 2 → Import and call `express()` to create an `app` instance — this wraps `http.createServer()` internally
Step 3 → Register middleware and routes on `app` (`app.use()`, `app.get()`, `app.post()`, etc.)
Step 4 → Call `app.listen(port, callback)` — under the hood this calls `http.createServer(app).listen(port)`
Step 5 → When a request comes in, Express matches it against registered routes/middleware in order and invokes the first matching handler

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install express` से install करो
Step 2 → `express()` call करके `app` instance बनाओ — ये internally `http.createServer()` को wrap करता है
Step 3 → `app` पर middleware और routes register करो (`app.use()`, `app.get()`, आदि)
Step 4 → `app.listen(port, callback)` call करो — ये internally `http.createServer(app).listen(port)` करता है
Step 5 → Request आने पर Express registered routes/middleware को order में match करता है और पहला matching handler चलाता है

---

## 🟡 Real World Example
**Swiggy backend:** Swiggy's order service starts with `const app = express()`. Then it registers middleware (JSON parsing, auth, logging) and routes (`/api/orders`, `/api/restaurants`, `/api/menu`). A single `app.listen(4000)` starts the HTTP server that handles thousands of concurrent requests from the mobile app — all routed by Express's internal routing engine instead of hand-written `if (req.url === ...)` checks.

## 🟡 Real Example Hindi mein
**Swiggy backend:** Swiggy का order service `const app = express()` से शुरू होता है। फिर middleware (JSON parsing, auth, logging) और routes (`/api/orders`, `/api/restaurants`, `/api/menu`) register होते हैं। एक `app.listen(4000)` से HTTP server start होता है जो mobile app से हजारों concurrent requests handle करता है — सब Express के internal routing engine से, hand-written `if (req.url === ...)` checks से नहीं।

---

## 💻 Code Example — Basic

```javascript
// basic-server.js
// Run: node basic-server.js  then open http://localhost:3000

const express = require('express');   // import express package
const app = express();                 // create express application instance

// Define a GET route for the root path
app.get('/', (req, res) => {
  res.send('Hello from Express!');     // res.send() sends plain text/HTML response
});

// Define a GET route that returns JSON
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: Date.now() });  // res.json() sends JSON + sets Content-Type
});

// Start the server, listening on port 3000
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);  // callback runs once server is ready
});
```

## 💻 Code Example — Advanced

```javascript
// advanced-server.js — production-style server setup with graceful shutdown

const express = require('express');
const http = require('http');

const app = express();

// Basic middleware
app.use(express.json());   // parse JSON bodies

// A sample route
app.get('/api/orders/:id', (req, res) => {
  const { id } = req.params;
  res.json({ orderId: id, status: 'preparing' });
});

// Create an explicit http server from app (useful for websockets, custom timeouts)
const server = http.createServer(app);

// Set server-level timeouts (important for production — avoid hung sockets)
server.keepAliveTimeout = 65000;   // slightly more than typical LB (60s) idle timeout
server.headersTimeout = 66000;     // must be > keepAliveTimeout

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT} (pid: ${process.pid})`);
});

// Graceful shutdown — important in containerized/K8s environments
function gracefulShutdown(signal) {
  console.log(`${signal} received — shutting down gracefully`);
  server.close(() => {
    console.log('HTTP server closed. No new connections accepted.');
    // close DB connections, flush logs, etc. here
    process.exit(0);
  });

  // Force exit if shutdown takes too long (e.g., stuck connections)
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000).unref();
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));  // sent by K8s/Docker
process.on('SIGINT', () => gracefulShutdown('SIGINT'));    // Ctrl+C locally

module.exports = app;  // export for testing with supertest etc.
```

---

## 🟠 Express.js Integration

```javascript
// Typical real-world app structure using express()

const express = require('express');
const app = express();

// Core middleware stack
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Feature routers (modular — see topic 99 Router)
app.use('/api/restaurants', require('./routes/restaurants'));
app.use('/api/orders', require('./routes/orders'));

// Health check for load balancers
app.get('/health', (req, res) => res.sendStatus(200));

// Start
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Zomato API running on ${PORT}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `express()` multiple times thinking you need a new instance per route file
```javascript
// WRONG
// routes/users.js
const express = require('express');
const app = express();   // ❌ creates a SEPARATE app, disconnected from main app

// CORRECT: use express.Router() in sub-files, not express()
const router = express.Router();
module.exports = router;
```

❌ **Mistake 2:** Forgetting to call `app.listen()` — server never starts
```javascript
// WRONG
const app = express();
app.get('/', (req, res) => res.send('hi'));
// nothing happens — no server bound to any port

// CORRECT
app.listen(3000, () => console.log('Server started'));
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => res.send('A'));
app.get('/', (req, res) => res.send('B'));

app.listen(3000);
// What does GET / return?
```
Answer: It returns `'A'`. Express matches routes in the order they are registered and invokes the FIRST matching handler. Since the first handler calls `res.send('A')` and doesn't call `next()`, the request-response cycle ends there — the second `app.get('/')` handler never runs. This is a common source of bugs when routes overlap.

---

## ⚫ Interview Questions + Answers

Q1: What does `express()` actually return, and what does it wrap?
A1: `express()` returns an `app` function/object (technically a function that can be passed to `http.createServer()`). It wraps Node's core `http` module, adding routing (`app.get/post/put/delete`), a middleware pipeline (`app.use`), and response helper methods (`res.json`, `res.send`, `res.status`). `app.listen()` internally calls `http.createServer(app).listen()`.

Q2: How is Express different from the raw `http` module?
A2: Raw `http` requires manual URL/method parsing (`req.url`, `req.method`), manual body buffering/parsing, and manual header/status-code setting for every response. Express provides declarative routing, automatic body-parsing middleware (`express.json()`), chainable response methods, and a composable middleware system — drastically reducing boilerplate.

Q3: What's the difference between `app.listen()` and using `http.createServer(app).listen()`?
A3: They're functionally equivalent — `app.listen()` is a convenience shortcut that internally creates an `http.Server` with `app` as the request handler and calls `.listen()` on it. You'd use the explicit `http.createServer(app)` form when you need the raw server instance before listening — e.g., to attach a WebSocket server (`socket.io`), set custom timeouts, or support HTTPS (`https.createServer`).

Q4: Can multiple `app.listen()` calls run on the same port?
A4: No — only one process can bind to a given port at a time (unless using `SO_REUSEPORT` via cluster module). Calling `listen()` twice on the same port throws `EADDRINUSE`. In production, you typically run multiple Node processes (via `cluster` or PM2) each listening on the same port with `SO_REUSEPORT`, or run them on different ports behind a load balancer.

Q5: Why would you create the server with `http.createServer(app)` explicitly instead of `app.listen()`?
A5: You need the raw `http.Server` object to: attach `socket.io` (`new Server(httpServer)`), configure `keepAliveTimeout`/`headersTimeout` for production tuning, use HTTPS (`https.createServer(options, app)`), or handle the `'upgrade'` event for WebSockets. `app.listen()` hides the server instance, so anything needing direct server-level config needs the explicit form.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building REST APIs or web servers quickly without writing low-level HTTP parsing code
- You want a large ecosystem of middleware (auth, validation, security, logging)
- Rapid prototyping or production APIs where routing clarity matters

❌ Avoid when:
- Building extremely performance-critical microservices where even Express's small overhead matters (consider Fastify)
- You need GraphQL-only servers (Apollo Server can run standalone, though it can also sit on Express)
- Building a framework with strong opinions/structure out of the box (consider NestJS instead)

---

## 📊 Visual Diagram
```
  require('express')
        │
        ▼
  const app = express()      ← app is a request handler function
        │
        ├── app.use(middleware)      (registered on app's internal stack)
        ├── app.get('/path', fn)
        ├── app.post('/path', fn)
        │
        ▼
  app.listen(PORT, cb)
        │
        ▼
  internally: http.createServer(app).listen(PORT, cb)
        │
        ▼
  ┌─────────────────────────────┐
  │   Node HTTP Server socket    │
  │   listening on PORT           │
  └──────────────┬───────────────┘
                 │ incoming request
                 ▼
     app(req, res) is invoked
                 │
                 ▼
     Express matches middleware/routes stack → handler runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `app` | Express application instance | Express application का instance |
| `app.listen()` | Starts HTTP server on a port | Port पर HTTP server start करता है |
| Middleware stack | Ordered list of registered functions | Registered functions की ordered list |
| `http.createServer()` | Core Node API that Express wraps | Core Node API जिसे Express wrap करता है |
| Route handler | Function that handles a specific path+method | Specific path+method handle करने वाला function |
| Graceful shutdown | Closing server cleanly on signals | Signal पर server को cleanly बंद करना |

---

## ⚡ 3-Line Summary
English: 1. `express()` creates an `app` that wraps Node's `http` module with routing, middleware, and response helpers. 2. `app.listen(port)` is shorthand for `http.createServer(app).listen(port)`. 3. Use explicit `http.createServer(app)` when you need the raw server for WebSockets, HTTPS, or timeout tuning.
Hindi: 1. `express()` एक `app` बनाता है जो Node के `http` module को routing, middleware और response helpers के साथ wrap करता है। 2. `app.listen(port)` असल में `http.createServer(app).listen(port)` का shortcut है। 3. WebSockets, HTTPS या timeout tuning के लिए explicit `http.createServer(app)` use करो।

---

## ➡️ Next Topic
**87. Request + Response Objects** — Understanding `req` and `res` in depth, their properties and methods.
