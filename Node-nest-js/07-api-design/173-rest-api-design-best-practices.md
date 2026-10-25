# 173. REST API Design — Best Practices
# हिंदी में: REST API Design — Best Practices

---

## 🔵 Simple Definition (English)
**REST (Representational State Transfer)** is an architectural style for designing APIs around **resources** (nouns like `users`, `orders`) manipulated via standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). Best practices are a set of conventions — consistent naming, correct status codes, statelessness — that make an API predictable, easy to consume, and maintainable.

## 🔵 सरल परिभाषा (Hindi)
**REST** एक architectural style है APIs design करने का, जो **resources** (nouns जैसे `users`, `orders`) के around बना होता है और standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) से manipulate होता है। Best practices एक set of conventions हैं — consistent naming, सही status codes, statelessness — जो API को predictable, use करने में आसान, और maintainable बनाते हैं।

---

## 🔴 Problem it Solves
Before REST conventions became standard, APIs were inconsistent and hard to predict:
```
BAD (RPC-style, inconsistent):
  POST /getUser?id=5
  POST /createNewUser
  GET  /user_delete/5
  POST /updateUserInfo

Problems: every endpoint invents its own verb and convention.
No client can "guess" the next endpoint. Hard to cache, hard to document,
inconsistent error formats, no clear resource hierarchy.
```
REST fixes this by standardizing: resources are nouns (`/users/5`), actions are HTTP verbs (`DELETE /users/5`), and the same pattern repeats for every resource — making APIs self-consistent and far easier to learn, cache, and build tooling around (e.g., auto-generated docs, consistent client SDKs).

## 🔴 यह क्यों बना? (Hindi)
REST conventions standard बनने से पहले APIs inconsistent और predict करना मुश्किल होता था:
```
BAD (RPC-style, inconsistent):
  POST /getUser?id=5
  POST /createNewUser
  GET  /user_delete/5
  POST /updateUserInfo

Problem: हर endpoint अपना verb और convention बनाता है।
कोई client next endpoint "guess" नहीं कर सकता। Cache करना मुश्किल,
document करना मुश्किल, inconsistent error formats, कोई clear resource hierarchy नहीं।
```
REST इसे standardize करके fix करता है: resources nouns हैं (`/users/5`), actions HTTP verbs हैं (`DELETE /users/5`), और यही pattern हर resource के लिए repeat होता है — जिससे APIs self-consistent बनते हैं और सीखना, cache करना, tooling बनाना बहुत आसान हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify your **resources** (nouns): `users`, `orders`, `products` — never verbs in the URL.
Step 2 → Use HTTP methods to express the action: `GET` (read), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).
Step 3 → Use plural resource names and nest sub-resources logically: `/users/5/orders` (orders belonging to user 5).
Step 4 → Return proper HTTP status codes: `200` OK, `201` Created, `204` No Content, `400` Bad Request, `404` Not Found, `409` Conflict.
Step 5 → Keep the API **stateless** — each request carries all info needed (auth token, params); the server stores no client session context between requests (session data, if any, lives in DB/Redis, not in server process memory tied to a connection).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → अपने **resources** (nouns) identify करो: `users`, `orders`, `products` — URL में कभी verbs नहीं।
Step 2 → Action express करने के लिए HTTP methods use करो: `GET` (read), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove)।
Step 3 → Plural resource names use करो और sub-resources को logically nest करो: `/users/5/orders` (user 5 के orders)।
Step 4 → सही HTTP status codes return करो: `200` OK, `201` Created, `204` No Content, `400` Bad Request, `404` Not Found, `409` Conflict।
Step 5 → API को **stateless** रखो — हर request में जरूरी सारी info हो (auth token, params); server client के बीच कोई session context memory में नहीं रखता।

---

## 🟡 Real World Example
**Amazon's product catalog API:** `GET /products` lists products, `GET /products/{id}` fetches one, `POST /products` creates (seller dashboard), `PATCH /products/{id}` updates stock/price, `DELETE /products/{id}` removes a listing. Every one of Amazon's hundreds of internal/external APIs follows this SAME pattern, so a new engineer or partner integrating with the Seller API doesn't need special documentation for every resource — they already know the pattern from `/orders`, `/products`, `/reviews`, etc.

## 🟡 Real Example Hindi mein
**Amazon का product catalog API:** `GET /products` products list करता है, `GET /products/{id}` एक fetch करता है, `POST /products` create करता है (seller dashboard), `PATCH /products/{id}` stock/price update करता है, `DELETE /products/{id}` listing remove करता है। Amazon के सैकड़ों internal/external APIs यही SAME pattern follow करते हैं, तो नया engineer या partner Seller API integrate करते वक़्त हर resource के लिए special documentation नहीं चाहिए — pattern `/orders`, `/products`, `/reviews` से already पता है।

---

## 💻 Code Example — Basic

```javascript
// basic-rest-api.js
// Install: npm install express

const express = require('express');
const app = express();
app.use(express.json());

let products = [{ id: 1, name: 'Phone', price: 20000, stock: 10 }]; // in-memory store for demo

// GET /products -> list all (READ, collection)
app.get('/products', (req, res) => {
  res.status(200).json({ data: products }); // 200 OK for successful reads
});

// GET /products/:id -> get one (READ, single resource)
app.get('/products/:id', (req, res) => {
  const product = products.find(p => p.id === Number(req.params.id));
  if (!product) return res.status(404).json({ error: 'Product not found' }); // 404 if missing
  res.status(200).json({ data: product });
});

// POST /products -> create (CREATE)
app.post('/products', (req, res) => {
  const newProduct = { id: products.length + 1, ...req.body };
  products.push(newProduct);
  res.status(201).json({ data: newProduct }); // 201 Created, return the created resource
});

// PATCH /products/:id -> partial update (UPDATE)
app.patch('/products/:id', (req, res) => {
  const product = products.find(p => p.id === Number(req.params.id));
  if (!product) return res.status(404).json({ error: 'Product not found' });
  Object.assign(product, req.body); // merge only provided fields
  res.status(200).json({ data: product });
});

// DELETE /products/:id -> remove (DELETE)
app.delete('/products/:id', (req, res) => {
  const index = products.findIndex(p => p.id === Number(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Product not found' });
  products.splice(index, 1);
  res.status(204).send(); // 204 No Content -- successful delete, nothing to return
});

app.listen(3000, () => console.log('REST API on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-rest-api.js — production patterns: nested resources, validation, consistent envelope

const express = require('express');
const router = express.Router();

// Nested resource: orders belonging to a specific user
// GET /users/:userId/orders
router.get('/users/:userId/orders', async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { page = 1, limit = 20 } = req.query; // pagination via query params, not URL path

    const orders = await Order.find({ userId })
      .skip((page - 1) * limit)
      .limit(Number(limit));

    const total = await Order.countDocuments({ userId });

    // Consistent response envelope used across the entire API
    res.status(200).json({
      success: true,
      data: orders,
      meta: { page: Number(page), limit: Number(limit), total },
    });
  } catch (err) {
    next(err); // delegate to centralized error middleware
  }
});

// Creating a sub-resource: POST /users/:userId/orders
router.post('/users/:userId/orders', async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { items } = req.body;

    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ success: false, error: 'items array is required' });
    }

    const order = await Order.create({ userId, items, status: 'PLACED' });

    // Return Location header pointing to the new resource (REST convention)
    res.status(201)
      .location(`/orders/${order.id}`)
      .json({ success: true, data: order });
  } catch (err) {
    next(err);
  }
});

// Idempotent full update: PUT replaces the ENTIRE resource
router.put('/orders/:id', async (req, res, next) => {
  try {
    const order = await Order.findByIdAndUpdate(req.params.id, req.body, {
      new: true,         // return updated document
      overwrite: true,   // PUT = full replace, not partial merge
      runValidators: true,
    });
    if (!order) return res.status(404).json({ success: false, error: 'Order not found' });
    res.status(200).json({ success: true, data: order });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();
app.use(express.json());
app.use('/api/v1', require('./advanced-rest-api')); // mount under versioned prefix

// Centralized 404 handler for unmatched routes
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Route not found' });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using verbs in URLs
✅ Correct: Use nouns for resources, let the HTTP method express the verb.

```javascript
// Wrong
app.post('/createUser', ...);
app.post('/deleteUser/:id', ...);

// Right
app.post('/users', ...);
app.delete('/users/:id', ...);
```

❌ Mistake 2: Returning 200 OK for everything, including errors
✅ Correct: Use the HTTP status code that actually matches the outcome.

```javascript
// Wrong
res.status(200).json({ error: 'User not found' }); // misleading -- client thinks it succeeded

// Right
res.status(404).json({ error: 'User not found' });
```

---

## 🧠 Tricky Interview Question

```javascript
// What's the difference between PUT /orders/5 and PATCH /orders/5
// if both are called with body: { status: 'SHIPPED' }?
```
Answer: `PUT` means "replace the entire resource" — semantically, if other fields exist on the order (e.g., `items`, `total`) and they're NOT included in the body, a strict PUT implementation should treat them as removed/reset to default (full replacement). `PATCH` means "partially update" — only the fields provided (`status`) are changed; everything else on the resource stays untouched. In practice, many APIs implement PUT more leniently (merge-like), but the correct semantic distinction is: PUT = idempotent full replace, PATCH = partial modify.

---

## ⚫ Interview Questions + Answers

Q1: What makes an API "RESTful" vs just "using HTTP"?
A1: True REST (per Roy Fielding's definition) requires: resource-based URLs, standard HTTP verbs used correctly, statelessness, cacheability where applicable, a uniform interface, and (strictly) HATEOAS (hypermedia links). Most "RESTful" APIs in practice follow the resource/verb/status-code conventions but skip strict HATEOAS — this is sometimes called "pragmatic REST" rather than pure REST.

Q2: Why should REST APIs be stateless?
A2: Statelessness means the server doesn't store any client context between requests — each request is self-contained (carries auth token, needed params). This allows horizontal scaling (any server instance can handle any request, since no server holds client-specific memory state), simplifies load balancing, and improves reliability (a server restart doesn't lose per-client state).

Q3: What's the difference between 401 and 403 status codes?
A3: **401 Unauthorized** means the request lacks valid authentication (no token, or an expired/invalid token) — "we don't know who you are." **403 Forbidden** means the request IS authenticated, but the authenticated user lacks permission for this specific action — "we know who you are, but you can't do this."

Q4: Should DELETE requests have a body?
A4: Generally no — DELETE should operate purely on the resource identified by the URL (`/orders/5`). While the HTTP spec technically allows a body, many servers/proxies/caches don't support or forward it reliably. If you need extra context for a delete (e.g., a reason), prefer a query param or a dedicated endpoint.

Q5: How do you handle an action that doesn't map cleanly to CRUD, like "approve an order"?
A5: Model it as a state-changing sub-resource or action endpoint: e.g., `POST /orders/5/approve` (treating "approve" as creating an approval record/event) or `PATCH /orders/5` with `{ status: 'APPROVED' }`. The former is more explicit and auditable for complex business actions; the latter is simpler for straightforward status transitions. Avoid custom verbs directly as top-level resources (`POST /approveOrder`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a public or internal HTTP API consumed by multiple clients (web, mobile, partners).
- You want predictable, cacheable, well-documented endpoints.

❌ Avoid when:
- You need highly flexible querying (fetch nested, varying shapes in one request) — consider GraphQL.
- Extremely performance-sensitive internal service-to-service calls — consider gRPC.

---

## 📊 Visual Diagram
```
RESOURCE-BASED URL + HTTP VERB = ACTION
──────────────────────────────────────────────
  GET    /products         → list all products       (200)
  GET    /products/5       → get product 5            (200/404)
  POST   /products         → create a product         (201)
  PUT    /products/5       → replace product 5 fully   (200)
  PATCH  /products/5       → partially update product 5 (200)
  DELETE /products/5       → remove product 5          (204)

  Nested: /users/5/orders  → orders belonging to user 5
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Resource | A noun entity exposed by the API | API का noun entity |
| Statelessness | No server-side client session memory | Server पर client state नहीं |
| Idempotent | Same result if repeated | दोहराने पर same result |
| HATEOAS | Hypermedia links in responses | Response में hypermedia links |
| Status code | Numeric outcome indicator | Outcome बताने वाला number |

---

## ⚡ 3-Line Summary
English:
1. REST models APIs around resources (nouns) and uses HTTP verbs (GET/POST/PUT/PATCH/DELETE) to express actions.
2. Consistent naming, correct status codes, and statelessness make APIs predictable and scalable.
3. PUT is a full idempotent replace, PATCH is a partial update — pick the right one for the semantics you need.

Hindi:
1. REST APIs resources (nouns) के around model करता है और actions के लिए HTTP verbs (GET/POST/PUT/PATCH/DELETE) use करता है।
2. Consistent naming, सही status codes, और statelessness APIs को predictable और scalable बनाते हैं।
3. PUT full idempotent replace है, PATCH partial update है — सही semantics के लिए सही एक चुनो।

---

## ➡️ Next Topic
**174. RESTful Routes Convention** — Standard route naming और structure patterns (index, show, create, update, destroy)।
