# 273. Build REST API from Scratch
# हिंदी में: शुरू से REST API बनाना

---

## 🔵 Simple Definition (English)
Building a REST API from scratch means designing resource-based endpoints (`/products`, `/orders`) that follow REST conventions (proper HTTP verbs, status codes, JSON bodies), with clean separation of routes, controllers, and data access — the exact kind of task asked in live-coding interview rounds.

## 🔵 सरल परिभाषा (Hindi)
Scratch से REST API बनाने का मतलब है resource-based endpoints (`/products`, `/orders`) design करना जो REST conventions follow करें (सही HTTP verbs, status codes, JSON bodies), routes/controllers/data access का clean separation — यही live-coding interview rounds में पूछा जाता है।

---

## 🔴 Problem it Solves
Without REST conventions, every API ends up inconsistent — some endpoints use GET for mutations, some return 200 for errors, some nest verbs in URLs (`/getProduct`, `/createOrder`). This makes APIs hard to predict, document, and consume. REST standardizes: nouns in URLs, HTTP verbs express actions, status codes communicate outcome — any client (mobile app, frontend, another service) can predict behavior without reading custom docs for every single endpoint.

## 🔴 यह क्यों बना? (Hindi)
REST conventions के बिना, हर API inconsistent हो जाती है — कुछ endpoints mutations के लिए GET use करते हैं, कुछ errors के लिए भी 200 return करते हैं, कुछ URLs में verbs डाल देते हैं (`/getProduct`)। REST standardize करता है: URLs में nouns, actions के लिए HTTP verbs, outcome बताने के लिए status codes — कोई भी client बिना हर endpoint के लिए अलग docs पढ़े behavior predict कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify **resources** (nouns): `/products`, `/orders`, `/users` — never verbs in URLs.
Step 2 → Map CRUD to HTTP verbs: `GET /products` (list), `GET /products/:id` (read one), `POST /products` (create), `PUT/PATCH /products/:id` (update), `DELETE /products/:id` (delete).
Step 3 → Use correct status codes: `200` OK, `201` Created, `204` No Content, `400` Bad Request, `404` Not Found, `409` Conflict, `500` Server Error.
Step 4 → Structure the project: `routes/` (URL → handler mapping), `controllers/` (business logic), `models/` (data layer) — separation of concerns.
Step 5 → Add validation middleware (reject malformed input before it reaches business logic).
Step 6 → Add centralized error handling so every endpoint returns a consistent error JSON shape.
Step 7 → Version the API (`/api/v1/products`) so breaking changes don't affect existing clients.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Resources** (nouns) identify करो: `/products`, `/orders` — URLs में verbs कभी नहीं।
Step 2 → CRUD को HTTP verbs पर map करो: GET (list/read), POST (create), PUT/PATCH (update), DELETE।
Step 3 → सही status codes use करो: 200, 201, 204, 400, 404, 409, 500।
Step 4 → Project structure करो: `routes/`, `controllers/`, `models/` — concerns अलग रखो।
Step 5 → Validation middleware add करो।
Step 6 → Centralized error handling — हर endpoint की error shape consistent हो।
Step 7 → API version करो (`/api/v1/`) ताकि breaking changes existing clients को तोड़ें नहीं।

---

## 🟡 Real World Example
**Swiggy's** restaurant menu service exposes `GET /api/v1/restaurants/:id/menu`, `POST /api/v1/restaurants/:id/menu-items`, `PATCH /api/v1/menu-items/:id` (partial update, e.g. only price), `DELETE /api/v1/menu-items/:id`. Every error response has the SAME shape: `{ error: { code, message } }`, so the mobile app's error-handling code is written once and works for every endpoint. This consistency is exactly what interviewers check for in a "build an API" round — not just working code, but predictable conventions.

## 🟡 Real Example Hindi mein
**Swiggy** का restaurant menu service `GET /api/v1/restaurants/:id/menu`, `POST .../menu-items`, `PATCH /menu-items/:id` (partial update), `DELETE /menu-items/:id` expose करता है। हर error response की shape SAME होती है: `{ error: { code, message } }`, जिससे mobile app का error-handling code एक बार लिखा जाता है और हर endpoint के लिए काम करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-rest-api.js — minimal in-memory REST API, no dependencies except express
// Run: npm install express && node basic-rest-api.js

const express = require('express');
const app = express();
app.use(express.json()); // parse JSON request bodies

// In-memory "database" — just an array for demo purposes
let products = [
  { id: 1, name: 'Laptop', price: 50000 },
  { id: 2, name: 'Mouse', price: 500 },
];
let nextId = 3;

// GET /products — list all
app.get('/products', (req, res) => {
  res.status(200).json(products);
});

// GET /products/:id — get one
app.get('/products/:id', (req, res) => {
  const product = products.find((p) => p.id === Number(req.params.id));
  if (!product) return res.status(404).json({ error: 'Product not found' });
  res.status(200).json(product);
});

// POST /products — create
app.post('/products', (req, res) => {
  const { name, price } = req.body;
  if (!name || typeof price !== 'number') {
    return res.status(400).json({ error: 'name (string) and price (number) are required' });
  }
  const newProduct = { id: nextId++, name, price };
  products.push(newProduct);
  res.status(201).json(newProduct); // 201 Created, return the created resource
});

// DELETE /products/:id — delete
app.delete('/products/:id', (req, res) => {
  const index = products.findIndex((p) => p.id === Number(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Product not found' });
  products.splice(index, 1);
  res.status(204).send(); // 204 No Content — successful delete, nothing to return
});

app.listen(3000, () => console.log('REST API on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-rest-api/
//   ├── server.js
//   ├── routes/products.js
//   ├── controllers/productController.js
//   └── middleware/validate.js

// ─── middleware/validate.js ───────────────────────────────────────────────
function validateProduct(req, res, next) {
  const { name, price } = req.body;
  const errors = [];
  if (!name || typeof name !== 'string' || name.trim().length === 0) {
    errors.push('name must be a non-empty string');
  }
  if (price === undefined || typeof price !== 'number' || price < 0) {
    errors.push('price must be a non-negative number');
  }
  if (errors.length) {
    return res.status(400).json({ error: { code: 'VALIDATION_ERROR', details: errors } });
  }
  next();
}
module.exports = { validateProduct };

// ─── controllers/productController.js ────────────────────────────────────
let products = new Map([
  [1, { id: 1, name: 'Laptop', price: 50000 }],
]);
let nextId = 2;

const productController = {
  list(req, res) {
    // Pagination support — standard REST practice for list endpoints
    const page = Number(req.query.page) || 1;
    const limit = Number(req.query.limit) || 10;
    const all = Array.from(products.values());
    const start = (page - 1) * limit;
    res.json({
      data: all.slice(start, start + limit),
      meta: { page, limit, total: all.length },
    });
  },

  getOne(req, res, next) {
    const product = products.get(Number(req.params.id));
    if (!product) {
      return next({ status: 404, message: 'Product not found' }); // pass to error handler
    }
    res.json({ data: product });
  },

  create(req, res) {
    const product = { id: nextId++, name: req.body.name, price: req.body.price };
    products.set(product.id, product);
    res.status(201).location(`/products/${product.id}`).json({ data: product });
  },

  update(req, res, next) {
    const id = Number(req.params.id);
    if (!products.has(id)) return next({ status: 404, message: 'Product not found' });
    const existing = products.get(id);
    const updated = { ...existing, ...req.body, id }; // PATCH-style partial update
    products.set(id, updated);
    res.json({ data: updated });
  },

  remove(req, res, next) {
    const id = Number(req.params.id);
    if (!products.has(id)) return next({ status: 404, message: 'Product not found' });
    products.delete(id);
    res.status(204).send();
  },
};
module.exports = productController;

// ─── routes/products.js ────────────────────────────────────────────────────
const express = require('express');
const router = express.Router();
const controller = require('../controllers/productController');
const { validateProduct } = require('../middleware/validate');

router.get('/', controller.list);
router.get('/:id', controller.getOne);
router.post('/', validateProduct, controller.create);
router.patch('/:id', controller.update);
router.delete('/:id', controller.remove);

module.exports = router;

// ─── server.js ──────────────────────────────────────────────────────────────
const express = require('express');
const app = express();
app.use(express.json());
app.use('/api/v1/products', require('./routes/products'));

// Centralized error handler — consistent error shape for EVERY route
app.use((err, req, res, next) => {
  const status = err.status || 500;
  res.status(status).json({ error: { code: err.code || 'INTERNAL_ERROR', message: err.message } });
});

app.listen(3000, () => console.log('Advanced REST API on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Full working mini-project tying it all together with proper HTTP semantics
const express = require('express');
const app = express();
app.use(express.json());

const orders = new Map();
let orderId = 1;

// Idempotent PUT: full replace. Non-idempotent POST: create.
app.post('/api/v1/orders', (req, res) => {
  const { items, customerId } = req.body;
  if (!Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ error: { message: 'items array required' } });
  }
  const order = { id: orderId++, customerId, items, status: 'pending', createdAt: new Date() };
  orders.set(order.id, order);
  res.status(201).json({ data: order });
});

app.get('/api/v1/orders/:id', (req, res) => {
  const order = orders.get(Number(req.params.id));
  if (!order) return res.status(404).json({ error: { message: 'Order not found' } });
  res.json({ data: order });
});

// PATCH for partial state transition (e.g. only status changes)
app.patch('/api/v1/orders/:id/status', (req, res) => {
  const order = orders.get(Number(req.params.id));
  if (!order) return res.status(404).json({ error: { message: 'Order not found' } });
  const validStatuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'];
  if (!validStatuses.includes(req.body.status)) {
    return res.status(400).json({ error: { message: 'Invalid status' } });
  }
  order.status = req.body.status;
  res.json({ data: order });
});

app.listen(3000, () => console.log('Orders API running'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using verbs in URLs (`/getProducts`, `/createOrder`)
✅ Correct: URLs are nouns (resources); the HTTP verb expresses the action.

```javascript
// Wrong
app.get('/getAllProducts', ...);
app.post('/createNewProduct', ...);

// Right — verb is already in the HTTP method
app.get('/products', ...);
app.post('/products', ...);
```

❌ Mistake 2: Returning 200 for everything, including errors
✅ Correct: Use the status code that matches the actual outcome — clients rely on it to branch logic (retry vs show error vs redirect to login).

```javascript
// Wrong: always 200, error info buried in body
res.status(200).json({ success: false, error: 'Not found' });

// Right: status code itself communicates the outcome
res.status(404).json({ error: { message: 'Not found' } });
```

---

## 🧠 Tricky Interview Question

```javascript
// Interviewer: "Should DELETE return 200 or 204? And does it matter?"
app.delete('/products/:id', (req, res) => {
  // ... delete logic ...
  res.status(200).json({ message: 'deleted' }); // vs res.status(204).send();
});
```
Answer: Both are technically valid, but they mean different things. **204 No Content** is the more RESTfully "correct" choice when there's truly nothing meaningful to return — it tells the client "success, don't expect a body." **200 OK** with a body is acceptable when you want to return extra info (e.g. the deleted record for undo functionality, or a confirmation message). The key interview insight: whichever you choose, be CONSISTENT across your API, and never send a 204 with a response body (HTTP spec violation — some clients/proxies will error on this) or a 200 with an empty body (ambiguous — did it work or not?).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between PUT and PATCH?
A1: PUT replaces the ENTIRE resource — any field not included in the request body is expected to be removed/reset. It's idempotent (calling it N times produces the same result as once). PATCH applies a PARTIAL update — only the fields included change, others remain untouched. In practice, many APIs use PATCH loosely for partial updates even where PUT would be "more correct," but interviewers expect you to know the semantic difference.

Q2: What does "idempotent" mean and which HTTP methods are idempotent?
A2: An idempotent operation produces the same result no matter how many times it's repeated. GET, PUT, DELETE, and HEAD are idempotent (deleting an already-deleted resource still results in "resource doesn't exist" — same end state). POST is NOT idempotent (calling it twice creates two resources). This matters for retry logic: clients can safely retry idempotent requests on network failure without side effects, but retrying a POST could cause duplicate orders/payments.

Q3: How would you design pagination for a `GET /products` endpoint?
A3: Common approaches: (1) Offset-based: `?page=2&limit=20` — simple but has consistency issues if items are added/removed between page requests. (2) Cursor-based: `?cursor=eyJpZCI6MjB9&limit=20` — more stable under concurrent writes, commonly used by Twitter/Stripe APIs. Always return metadata: `{ data: [...], meta: { total, page, hasMore } }` so clients know whether more pages exist without guessing.

Q4: How do you handle API versioning, and why does it matter?
A4: Common strategies: URL versioning (`/api/v1/products` — most common, easy to understand), header versioning (`Accept: application/vnd.myapp.v2+json`), or query param (`?version=2`). It matters because once mobile apps or third parties integrate with your API, you can't change response shapes without breaking them — versioning lets you introduce v2 while v1 keeps working for clients that haven't migrated yet.

Q5: What status code should you return for validation errors, and how should the error body be structured?
A5: `400 Bad Request` for malformed/invalid client input (missing required fields, wrong types), `422 Unprocessable Entity` for syntactically valid but semantically invalid input (some APIs distinguish this, many just use 400 for both). Error body should be a consistent, machine-parseable shape: `{ error: { code: 'VALIDATION_ERROR', message: '...', details: [...] } }` so frontend code can branch on `error.code` rather than parsing message strings.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a public or internal API that multiple clients (web, mobile, other services) will consume
- You need predictable, cacheable, well-documented endpoints
- Interview live-coding rounds asking you to "design and build an API"

❌ Avoid when:
- Extremely complex queries with many optional filters/relations — GraphQL may fit better (single flexible endpoint vs many REST endpoints)
- Real-time bidirectional communication needs (use WebSockets/Socket.io instead of polling REST endpoints)

---

## 📊 Visual Diagram
```
CLIENT                          REST API LAYERS
──────                          ─────────────────────────────
POST /api/v1/products           ┌─────────────┐
  { name, price }       ──────► │ Route        │  app.post('/products', ...)
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ Middleware   │  validateProduct()
                                 │ (validation) │  → 400 if invalid
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ Controller   │  business logic
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ Model/DB     │  persist data
                                 └──────┬──────┘
                                        ▼
                                 201 Created
                                 { data: { id, name, price } }  ◄── back to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Resource | A noun representing data (products, orders) | Data को represent करने वाला noun |
| Idempotent | Same result no matter how many times repeated | कितनी भी बार करने पर same result |
| Status Code | Number communicating request outcome | Request outcome बताने वाला number |
| Versioning | Allowing API changes without breaking old clients | पुराने clients तोड़े बिना API बदलना |
| Pagination | Splitting large lists into pages | बड़ी lists को pages में बाँटना |

---

## ⚡ 3-Line Summary
English: 1. REST APIs use nouns for URLs and HTTP verbs for actions, with status codes communicating outcomes consistently. 2. Separate routes, controllers, and models; add validation middleware and a centralized error handler. 3. Version your API from day one (`/api/v1/`) so future breaking changes don't break existing clients.
Hindi: 1. REST APIs URLs में nouns और actions के लिए HTTP verbs use करती हैं, status codes outcome consistently बताते हैं। 2. Routes, controllers, models अलग रखो; validation middleware और centralized error handler add करो। 3. Day one से API version करो (`/api/v1/`) ताकि future breaking changes पुराने clients न तोड़ें।

---

## ➡️ Next Topic
**274. Build Auth System (JWT)** — signup/login/protected routes के साथ JWT-based authentication बनाना।
