# 88. Routes — Complete Guide
# हिंदी में: Routes — पूरी जानकारी

---

## 🔵 Simple Definition (English)
A **route** in Express defines how the application responds to a client request for a specific URL path and HTTP method. `app.METHOD(PATH, HANDLER)` is the basic form, e.g., `app.get('/users', handler)`. Express supports exact paths, path parameters (`:id`), wildcards, regex patterns, and chained route definitions via `app.route()`.

## 🔵 सरल परिभाषा (Hindi)
**Route** Express में define करता है कि application किसी specific URL path और HTTP method के request पर कैसे respond करे। `app.METHOD(PATH, HANDLER)` basic form है, जैसे `app.get('/users', handler)`। Express exact paths, path parameters (`:id`), wildcards, regex patterns, और `app.route()` से chained routes support करता है।

---

## 🔴 Problem it Solves
```
WITHOUT STRUCTURED ROUTING:
  http.createServer((req, res) => {
    if (req.url === '/users' && req.method === 'GET') { ... }
    else if (req.url === '/users' && req.method === 'POST') { ... }
    else if (req.url.startsWith('/users/') && req.method === 'GET') {
      const id = req.url.split('/')[2];   // manual parsing, error-prone
      ...
    }
    // This if/else chain grows unmanageable past ~10 routes
  });

WITH EXPRESS ROUTES:
  app.get('/users', listUsers);
  app.post('/users', createUser);
  app.get('/users/:id', getUserById);     // :id auto-extracted to req.params.id
  app.put('/users/:id', updateUser);
  app.delete('/users/:id', deleteUser);
  → Declarative, self-documenting, no manual URL splitting
```

## 🔴 यह क्यों बना? (Hindi)
Raw routing में URL और method manually check करना पड़ता था, path parameters manually extract करने पड़ते थे — यह error-prone और unreadable था बड़े applications में। Express routes ने declarative syntax दिया जहाँ path pattern और handler साफ़ दिखते हैं, params auto-extract होते हैं, और routes को order में match किया जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Register routes using `app.get()`, `app.post()`, `app.put()`, `app.patch()`, `app.delete()`, or `app.all()` (matches any method)
Step 2 → Express compiles each path pattern into a regex internally using the `path-to-regexp` library
Step 3 → On each incoming request, Express walks its route stack TOP TO BOTTOM, checking method + path match
Step 4 → First matching route's handler(s) run; if the handler calls `next()`, Express continues to the next matching route
Step 5 → If no route matches, Express falls through to the default 404 handler (unless you define your own)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `app.get()`, `app.post()`, `app.put()`, `app.patch()`, `app.delete()`, या `app.all()` (हर method match करता है) से routes register करो
Step 2 → Express हर path pattern को `path-to-regexp` library से regex में compile करता है
Step 3 → हर incoming request पर Express अपना route stack TOP TO BOTTOM check करता है, method + path match देखता है
Step 4 → पहला matching route का handler चलता है; अगर handler `next()` call करे तो Express आगे के matching routes देखता है
Step 5 → कोई route match नहीं हुआ तो default 404 handler चलता है (जब तक अपना custom न बनाया हो)

---

## 🟡 Real World Example
**Amazon product catalog API:** Routes like `GET /products` (list), `GET /products/:id` (detail), `POST /products` (admin create), `PUT /products/:id` (update), `DELETE /products/:id` (remove) are all registered with distinct HTTP methods on the SAME path `/products` or `/products/:id`. Express distinguishes them purely by HTTP method — a RESTful convention that keeps the API predictable for frontend/mobile teams.

## 🟡 Real Example Hindi mein
**Amazon product catalog API:** Routes जैसे `GET /products` (list), `GET /products/:id` (detail), `POST /products` (admin create), `PUT /products/:id` (update), `DELETE /products/:id` (remove) सब same path `/products` या `/products/:id` पर अलग HTTP methods के साथ register होते हैं। Express इन्हें सिर्फ HTTP method से अलग करता है — यह RESTful convention frontend/mobile teams के लिए API predictable रखता है।

---

## 💻 Code Example — Basic

```javascript
// routes-basic.js
const express = require('express');
const app = express();
app.use(express.json());

// Exact path route
app.get('/about', (req, res) => res.send('About page'));

// Route with a path parameter (:id)
app.get('/users/:id', (req, res) => {
  res.json({ userId: req.params.id });  // e.g., /users/42 → { userId: '42' }
});

// Multiple path parameters
app.get('/users/:userId/orders/:orderId', (req, res) => {
  res.json(req.params);  // { userId: '5', orderId: '101' }
});

// app.all() — matches ANY HTTP method for a path (useful for logging/auth gates)
app.all('/admin/*', (req, res, next) => {
  console.log(`Admin area accessed via ${req.method}`);
  next();
});

// Optional parameter using '?'
app.get('/products/:category?', (req, res) => {
  // category is optional: /products OR /products/electronics both match
  res.json({ category: req.params.category || 'all' });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// routes-advanced.js — chained routes, regex, wildcard, and route arrays

const express = require('express');
const app = express();
app.use(express.json());

// app.route() — chain multiple methods for the SAME path (avoids repeating path)
app.route('/products/:id')
  .get((req, res) => {
    res.json({ id: req.params.id, action: 'get' });
  })
  .put((req, res) => {
    res.json({ id: req.params.id, action: 'update', data: req.body });
  })
  .delete((req, res) => {
    res.status(204).send();  // 204 No Content — successful delete, no body
  });

// Regex-based route — match paths ending in specific pattern
app.get(/.*fly$/, (req, res) => {
  // Matches /butterfly, /dragonfly, etc.
  res.send(`Matched regex route: ${req.path}`);
});

// Wildcard segment (modern Express 5 syntax uses named wildcards)
app.get('/files/*splat', (req, res) => {
  // req.params.splat captures everything after /files/
  res.json({ requestedFile: req.params.splat });
});

// Array of middleware for one route — runs in order
const checkAuth = (req, res, next) => {
  if (!req.headers.authorization) return res.status(401).json({ error: 'No auth' });
  next();
};
const checkAdmin = (req, res, next) => {
  if (req.headers['x-role'] !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  next();
};

app.delete('/admin/products/:id', [checkAuth, checkAdmin], (req, res) => {
  res.json({ deleted: req.params.id });
});

// Multiple paths registered to the same handler
app.get(['/health', '/healthz', '/ping'], (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Real-world route organization for a Flipkart-style order service

const express = require('express');
const app = express();
app.use(express.json());

// RESTful resource routes
app.get('/api/orders', listOrders);            // GET all (with pagination)
app.get('/api/orders/:id', getOrderById);       // GET one
app.post('/api/orders', createOrder);           // CREATE
app.put('/api/orders/:id', replaceOrder);       // FULL update
app.patch('/api/orders/:id', updateOrderStatus);// PARTIAL update
app.delete('/api/orders/:id', cancelOrder);     // DELETE (soft-delete usually)

function listOrders(req, res) { res.json({ orders: [] }); }
function getOrderById(req, res) { res.json({ id: req.params.id }); }
function createOrder(req, res) { res.status(201).json({ created: true, data: req.body }); }
function replaceOrder(req, res) { res.json({ id: req.params.id, replaced: req.body }); }
function updateOrderStatus(req, res) { res.json({ id: req.params.id, status: req.body.status }); }
function cancelOrder(req, res) { res.status(204).send(); }

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Registering a generic route before a specific one
```javascript
// WRONG: /users/:id matches BEFORE /users/me, so 'me' is treated as an :id
app.get('/users/:id', (req, res) => res.json({ id: req.params.id }));
app.get('/users/me', (req, res) => res.json({ me: true }));  // never reached!

// CORRECT: specific routes FIRST, dynamic routes AFTER
app.get('/users/me', (req, res) => res.json({ me: true }));
app.get('/users/:id', (req, res) => res.json({ id: req.params.id }));
```

❌ **Mistake 2:** Forgetting that route matching is case-sensitive/slash-sensitive by default behavior nuances
```javascript
// WRONG: assuming /Users and /users are the same
app.get('/users', handler);
// GET /Users → 404 by default (Express path matching is case-insensitive for the
// PATH by default actually, but confusion is common with trailing slashes)

// CORRECT: be aware strict routing & case sensitivity are configurable
app.set('case sensitive routing', true);  // now /Users !== /users
app.set('strict routing', true);          // now /users !== /users/
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();

app.get('/users/:id', (req, res) => res.send(`ID route: ${req.params.id}`));
app.get('/users/new', (req, res) => res.send('New user form'));

app.listen(3000);
// GET /users/new → what is sent?
```
Answer: It sends `"ID route: new"`. Even though `/users/new` looks like it should match the more specific second route, Express matches routes in REGISTRATION ORDER, not specificity order. Since `/users/:id` is registered first and `:id` matches any segment (including the literal string "new"), that route wins. The fix is to register `/users/new` BEFORE `/users/:id`.

---

## ⚫ Interview Questions + Answers

Q1: In what order does Express match routes when multiple routes could match a request?
A1: Express checks routes in the exact order they were registered (top to bottom in the code), not by specificity. The first route whose method AND path pattern match the request wins (unless its handler calls `next()` to continue down the stack). This means route ORDER matters — more specific/literal routes should be registered before dynamic ones (`:param` or wildcards).

Q2: What's the difference between `app.get('/users/:id', ...)` and `app.all('/users/:id', ...)`?
A2: `app.get()` only matches HTTP GET requests to that path. `app.all()` matches EVERY HTTP method (GET, POST, PUT, DELETE, etc.) for that path — commonly used for cross-cutting concerns like logging or auth checks that should apply regardless of the verb used.

Q3: How do you define multiple HTTP methods for the same path without repeating the path string?
A3: Use `app.route(path)` which returns a route object you can chain: `app.route('/products/:id').get(fn1).put(fn2).delete(fn3)`. This avoids repeating `/products/:id` for each method and groups related handlers together.

Q4: How do optional route parameters work, and give an example?
A4: Append `?` after the parameter name: `app.get('/products/:category?', handler)`. This makes `:category` optional — both `/products` and `/products/shoes` match this route. Inside the handler, `req.params.category` will be `undefined` if not provided.

Q5: How would you capture an arbitrary-depth path segment, like for a file server route?
A5: Use a named wildcard parameter (Express 5 syntax): `app.get('/files/*splat', handler)` — `req.params.splat` captures everything after `/files/` as an array of segments (or string depending on version). In Express 4, the equivalent was `app.get('/files/*', handler)` with `req.params[0]` holding the captured segment. This is commonly used for static file serving or catch-all proxy routes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building RESTful APIs with clear resource-based URL structure (`/resource/:id`)
- You need path parameters, optional segments, or pattern-based matching
- Grouping related HTTP methods for the same resource via `app.route()`

❌ Avoid when:
- Extremely complex URL matching logic might be clearer as explicit conditional logic in a single catch-all handler (rare, but possible for legacy URL migration logic)
- You need GraphQL-style single-endpoint APIs (routes become less relevant; one `/graphql` POST endpoint handles everything)

---

## 📊 Visual Diagram
```
  Route Stack (registration order matters!)
  ────────────────────────────────────────
  1. app.get('/users/me')        ← checked first
  2. app.get('/users/:id')       ← checked second
  3. app.post('/users')
  4. app.use(errorHandler)       ← last

  Incoming: GET /users/me
       │
       ▼
  ┌─────────────────────┐
  │ Check route 1:        │
  │ path='/users/me'      │  ✅ MATCH (method=GET, path matches exactly)
  │ method=GET             │
  └──────────┬────────────┘
             ▼
     Handler runs → response sent
     (routes 2, 3, 4 never checked)

  Incoming: GET /users/42
       │
       ▼
  Route 1: path mismatch ('/users/me' !== '/users/42') → skip
       │
       ▼
  Route 2: '/users/:id' matches '/users/42' → req.params.id = '42' ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Route | URL path + method → handler mapping | URL path + method → handler mapping |
| `:param` | Named dynamic URL segment | Named dynamic URL segment |
| `app.route()` | Chainable route object for one path | एक path के लिए chainable route object |
| `app.all()` | Matches any HTTP method | किसी भी HTTP method को match करता है |
| Route order | Registration sequence determines match priority | Registration sequence match priority decide करती है |
| Wildcard | Matches arbitrary path segments | Arbitrary path segments match करता है |

---

## ⚡ 3-Line Summary
English: 1. Routes map `METHOD + PATH` to a handler using `app.get/post/put/patch/delete`. 2. Matching is strictly by registration order, not specificity — put literal paths before dynamic `:param` routes. 3. `app.route(path)` lets you chain multiple methods for one path without repeating it.
Hindi: 1. Routes `METHOD + PATH` को handler से map करते हैं। 2. Matching registration order से होता है, specificity से नहीं — literal paths को `:param` routes से पहले रखो। 3. `app.route(path)` से एक path के लिए कई methods chain कर सकते हो।

---

## ➡️ Next Topic
**89. Route Parameters + Query Strings** — Deep dive into `req.params` and `req.query` parsing and validation.
