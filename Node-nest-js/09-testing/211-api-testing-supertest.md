# 211. API Testing (Supertest)
# हिंदी में: API Testing — Supertest से Real HTTP Requests Test करना

---

## 🔵 Simple Definition (English)
**Supertest** is a library that lets you send real HTTP requests (GET, POST, PUT, DELETE) directly to your Express app in tests — without actually starting a server on a port. It wraps your app, sends a request through the full middleware/route stack, and lets you assert on status codes, headers, and response bodies with a chainable API.

## 🔵 सरल परिभाषा (Hindi)
**Supertest** एक library है जो तुम्हें test में Express app पर real HTTP requests (GET, POST, PUT, DELETE) भेजने देती है — बिना किसी port पर server चलाए। ये तुम्हारे app को wrap करती है, full middleware/route stack से request भेजती है, और status codes, headers, response bodies को chainable API से assert करने देती है।

---

## 🔴 Problem it Solves
Without Supertest, testing an API route means either: (1) manually starting the server and using `curl`/Postman (slow, manual, not automatable in CI), or (2) unit-testing the handler function with fake `req`/`res` objects (misses real Express behavior like middleware order, body parsing, routing params, error-handling middleware). Supertest solves both — it runs the actual Express app's request pipeline in-process, fast, and fully automatable in CI, catching real HTTP-level bugs (wrong status code, missing header, malformed JSON).

## 🔴 यह क्यों बना? (Hindi)
Supertest के बिना, API route test करने के दो तरीके थे: (1) server manually start करके `curl`/Postman use करना (slow, manual, CI में automate नहीं हो सकता), या (2) handler function को fake `req`/`res` objects से unit-test करना (real Express behavior जैसे middleware order, body parsing, route params, error middleware miss हो जाता है)। Supertest दोनों problem solve करता है — ये actual Express app की request pipeline को in-process चलाता है, fast है, और CI में पूरी तरह automatable है।

---

## 🟢 How it Works — Step by Step

Step 1 → Export your Express `app` object WITHOUT calling `app.listen()` in the test environment
Step 2 → Install: `npm install --save-dev supertest`
Step 3 → `const request = require('supertest')` then `request(app).get('/route')`
Step 4 → Supertest internally starts an ephemeral server on a random port, sends the request, then tears it down
Step 5 → Chain `.send()` for body, `.set()` for headers, `.expect()` for assertions, or use the returned response with Jest's `expect()`
Step 6 → Await the request (it returns a Promise) and assert on `res.status`, `res.body`, `res.headers`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Test environment में `app.listen()` call किए बिना अपना Express `app` object export करो
Step 2 → Install करो: `npm install --save-dev supertest`
Step 3 → `const request = require('supertest')` फिर `request(app).get('/route')`
Step 4 → Supertest internally random port पर एक ephemeral server start करता है, request भेजता है, फिर उसे बंद कर देता है
Step 5 → Body के लिए `.send()`, headers के लिए `.set()`, assertion के लिए `.expect()` chain करो, या return हुए response पर Jest का `expect()` use करो
Step 6 → Request को await करो (Promise return करता है) और `res.status`, `res.body`, `res.headers` पर assert करो

---

## 🟡 Real World Example
**Flipkart's cart API** (`POST /cart/items`, `GET /cart`, `DELETE /cart/items/:id`) is tested with Supertest before every deploy. Tests cover: adding an item returns 201 with the item in the response, adding an out-of-stock item returns 400 with a clear error message, missing auth token returns 401, and a full flow test — add item → get cart → verify item present → delete item → get cart → verify empty. These run in CI on every PR in under 5 seconds total, catching regressions from route/middleware changes before they ever hit staging.

## 🟡 Real Example Hindi mein
**Flipkart का cart API** (`POST /cart/items`, `GET /cart`, `DELETE /cart/items/:id`) हर deploy से पहले Supertest से test होता है। Tests cover करते हैं: item add करने पर 201 और response में item मिलना चाहिए, out-of-stock item add करने पर 400 और clear error message, missing auth token पर 401, और एक full flow test — item add करो → cart get करो → item present check करो → item delete करो → cart get करो → empty check करो। ये सब CI में हर PR पर 5 seconds से कम में चलते हैं।

---

## 💻 Code Example — Basic

```javascript
// app.js — simple Express app (exported, not listening)
const express = require('express');
const app = express();
app.use(express.json());

// In-memory "todos" for demo purposes
let todos = [];
let nextId = 1;

app.get('/todos', (req, res) => {
  res.status(200).json(todos);
});

app.post('/todos', (req, res) => {
  const { title } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }
  const todo = { id: nextId++, title, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

app.delete('/todos/:id', (req, res) => {
  const id = Number(req.params.id);
  const index = todos.findIndex(t => t.id === id);
  if (index === -1) {
    return res.status(404).json({ error: 'todo not found' });
  }
  todos.splice(index, 1);
  res.status(204).send();
});

module.exports = { app, resetTodos: () => { todos = []; nextId = 1; } };
```

```javascript
// app.test.js — basic Supertest API tests
const request = require('supertest');
const { app, resetTodos } = require('./app');

describe('Todos API', () => {
  // Reset in-memory data before every test for isolation
  beforeEach(() => resetTodos());

  test('GET /todos returns empty array initially', async () => {
    const res = await request(app).get('/todos');

    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });

  test('POST /todos creates a new todo', async () => {
    const res = await request(app)
      .post('/todos')
      .send({ title: 'Buy groceries' }) // request body
      .set('Content-Type', 'application/json'); // explicit header

    expect(res.status).toBe(201);
    expect(res.body.title).toBe('Buy groceries');
    expect(res.body.done).toBe(false);
  });

  test('POST /todos without title returns 400', async () => {
    const res = await request(app).post('/todos').send({});

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('title is required');
  });

  test('DELETE /todos/:id removes the todo', async () => {
    const createRes = await request(app).post('/todos').send({ title: 'Test' });
    const id = createRes.body.id;

    const deleteRes = await request(app).delete(`/todos/${id}`);
    expect(deleteRes.status).toBe(204);

    const getRes = await request(app).get('/todos');
    expect(getRes.body).toEqual([]); // confirms it's actually gone
  });
});
```

## 💻 Code Example — Advanced

```javascript
// auth.js — middleware that requires a bearer token
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  const token = authHeader.split(' ')[1];
  if (token !== 'valid-test-token') { // in real app: verify JWT
    return res.status(401).json({ error: 'Invalid token' });
  }
  req.user = { id: 'u1', role: 'customer' };
  next();
}

module.exports = { requireAuth };

// cartApp.js — protected routes needing auth
const express = require('express');
const { requireAuth } = require('./auth');
const app = express();
app.use(express.json());

let cart = [];

app.post('/cart/items', requireAuth, (req, res) => {
  const { sku, qty, stock } = req.body;
  if (stock <= 0) {
    return res.status(400).json({ error: 'Item out of stock' });
  }
  const item = { sku, qty, addedBy: req.user.id };
  cart.push(item);
  res.status(201).json(item);
});

app.get('/cart', requireAuth, (req, res) => res.status(200).json(cart));

module.exports = { app, resetCart: () => { cart = []; } };

// cartApp.test.js — full flow + auth + edge cases
const request = require('supertest');
const { app, resetCart } = require('./cartApp');

describe('Cart API (full flow)', () => {
  beforeEach(() => resetCart());

  test('returns 401 without auth header', async () => {
    const res = await request(app).get('/cart');
    expect(res.status).toBe(401);
  });

  test('returns 401 with invalid token', async () => {
    const res = await request(app)
      .get('/cart')
      .set('Authorization', 'Bearer wrong-token');
    expect(res.status).toBe(401);
  });

  test('rejects out-of-stock item with 400', async () => {
    const res = await request(app)
      .post('/cart/items')
      .set('Authorization', 'Bearer valid-test-token')
      .send({ sku: 'SKU1', qty: 1, stock: 0 });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('Item out of stock');
  });

  test('full flow: add item then fetch cart with it present', async () => {
    const addRes = await request(app)
      .post('/cart/items')
      .set('Authorization', 'Bearer valid-test-token')
      .send({ sku: 'SKU2', qty: 2, stock: 10 });

    expect(addRes.status).toBe(201);

    const getRes = await request(app)
      .get('/cart')
      .set('Authorization', 'Bearer valid-test-token');

    expect(getRes.body).toHaveLength(1);
    expect(getRes.body[0].sku).toBe('SKU2');
  });

  test('.expect() chaining style (alternative syntax)', () => {
    // Supertest's .expect() can be chained instead of manual assertions
    return request(app)
      .get('/cart')
      .set('Authorization', 'Bearer valid-test-token')
      .expect(200)                 // asserts status code
      .expect('Content-Type', /json/); // asserts header matches regex
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// server.js — the ONLY file that calls app.listen(), kept separate from app.js
const { app } = require('./app');
const PORT = process.env.PORT || 3000;

// This file is never imported by tests — only app.js (the exported app) is
if (require.main === module) {
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}

// This separation (app.js vs server.js) is THE standard pattern for testability:
// - app.js: defines routes/middleware, exports `app`, NEVER calls listen()
// - server.js: imports app, calls app.listen() — only run in production/dev
// - tests import app.js directly, Supertest handles the ephemeral server
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `app.listen()` inside the file you test, causing port conflicts
```javascript
// WRONG: app.js itself starts listening
const app = express();
// ... routes ...
app.listen(3000); // ← every test file importing this tries to bind port 3000!
module.exports = app;

// CORRECT: split listen() into a separate server.js, export just `app`
const app = express();
// ... routes ...
module.exports = app; // no listen() here — Supertest creates its own ephemeral server
```

❌ Mistake 2: Forgetting to `await` the Supertest request
```javascript
// WRONG: no await — test finishes before the request completes, assertions never run
test('bad test', () => {
  request(app).get('/todos').expect(200); // not awaited or returned!
});

// CORRECT: await it (or return the promise chain)
test('good test', async () => {
  const res = await request(app).get('/todos');
  expect(res.status).toBe(200);
});
```

---

## 🧠 Tricky Interview Question

```javascript
test('two requests in one test', async () => {
  const res1 = await request(app).post('/todos').send({ title: 'A' });
  const res2 = await request(app).post('/todos').send({ title: 'B' });

  const getRes = await request(app).get('/todos');
  console.log(getRes.body.length); // ❓ what does this print if run AFTER the earlier test file's tests?
});
```
Answer: It prints **2** within this test (both POSTs ran before GET, in the same in-memory `todos` array) — BUT if `resetTodos()` isn't called in `beforeEach`, the count would accumulate ACROSS tests in the same file too, since Supertest doesn't reset your app's in-memory state — only HTTP transport is ephemeral, the underlying app module (and any in-memory arrays/singletons) persists across requests within the same test file unless you explicitly reset it. This is why `beforeEach(() => resetTodos())` is essential even with Supertest.

---

## ⚫ Interview Questions + Answers

Q1: Does Supertest actually start a real network server?
A1: Yes, internally — it calls `app.listen(0)` (port 0 = random free port) under the hood when you call `request(app)`, sends the real HTTP request over localhost, then closes that ephemeral server. This is why it exercises the FULL middleware/routing stack realistically, unlike calling the handler function directly with fake req/res.

Q2: How do you test file uploads with Supertest?
A2: Use `.attach(fieldName, filePathOrBuffer)`: `request(app).post('/upload').attach('file', './test-fixtures/sample.jpg')`. Combine with `.field()` for additional form fields alongside the file in a multipart request.

Q3: How do you test routes that require authentication in every test without repeating login logic?
A3: Extract a helper: `async function authenticatedRequest(method, path) { const token = await getTestToken(); return request(app)[method](path).set('Authorization', \`Bearer ${token}\`); }`. Or use a `beforeAll` to log in once and reuse the token/cookie across tests in that suite.

Q4: What's the difference between asserting with `.expect()` (Supertest's) vs Jest's `expect()`?
A4: Supertest's `.expect(200)` is chained onto the request and throws if the response doesn't match — useful for quick one-liners, and multiple `.expect()` calls can chain. Jest's `expect(res.status).toBe(200)` is more flexible for complex assertions (custom matchers, `toMatchObject`, deep equality) and better error messages. Many projects mix both — use Supertest's `.expect()` for simple status/header checks and Jest's `expect()` on `res.body` for business logic assertions.

Q5: How should test data/state be isolated between API tests?
A5: Reset in-memory state or truncate test DB tables in `beforeEach`. For a real DB, wrap each test in a transaction that's rolled back afterward (`BEGIN` → test → `ROLLBACK`), which is fast and guarantees true isolation without needing to rebuild schema or re-seed every test.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Testing Express/Fastify/any Node HTTP route's real request/response behavior
- Verifying status codes, headers, auth middleware, error handling end-to-end
- Running automated API regression tests in CI before deploy

❌ Avoid when:
- You only need to test pure business logic with no HTTP concerns (use unit tests — faster)
- Testing truly cross-service behavior requiring real network calls between separate deployed services (use E2E/contract testing instead)

---

## 📊 Visual Diagram
```
SUPERTEST FLOW:
─────────────────────────────────────────────────
  Test file
     │
     │ request(app).post('/cart/items').send({...})
     ▼
  Supertest spins up ephemeral server (random port)
     │
     ▼
  Request flows through REAL Express pipeline:
     middleware → auth → route handler → response
     │
     ▼
  Response captured → ephemeral server closed
     │
     ▼
  res.status / res.body / res.headers available
     │
     ▼
  expect(res.status).toBe(201)  ✅ or ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Supertest | HTTP assertion library for testing Express apps | Express app testing library |
| Ephemeral server | Temporary server on random port, auto-closed | Temporary server, auto-close |
| .send() | Attaches request body | Request body भेजना |
| .set() | Sets a request header | Header set करना |
| .expect() | Chainable assertion on response | Response पर assertion |
| app.js vs server.js | Split pattern for testability | Testability के लिए split pattern |
| res.body | Parsed response JSON body | Parsed response JSON |

---

## ⚡ 3-Line Summary
English:
1. Supertest sends real HTTP requests to your Express app in-process via an ephemeral server, letting tests verify actual routing, middleware, and status code behavior.
2. Split `app.js` (exports app, no `listen()`) from `server.js` (calls `listen()`) — this is the standard pattern that makes Supertest testing possible.
3. Always `await` requests and reset app/DB state in `beforeEach` — Supertest resets the HTTP transport per call, but NOT your application's in-memory or DB state.

Hindi:
1. Supertest real HTTP requests को Express app पर in-process, ephemeral server के through भेजता है — real routing, middleware, status code behavior test होता है।
2. `app.js` (app export करे, `listen()` न करे) को `server.js` (जो `listen()` करे) से अलग करो — यही standard pattern Supertest testing possible बनाता है।
3. हमेशा requests को `await` करो और `beforeEach` में app/DB state reset करो — Supertest हर call पर HTTP transport reset करता है, पर application का in-memory या DB state नहीं।

---

## ➡️ Next Topic
**212. Mocking in Tests** — external dependencies (payment gateway, DB, file system) को fake versions से replace करना ताकि tests fast और reliable रहें।
