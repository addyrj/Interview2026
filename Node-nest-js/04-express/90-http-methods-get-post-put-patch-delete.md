# 90. HTTP Methods (GET, POST, PUT, PATCH, DELETE)
# हिंदी में: HTTP Methods (GET, POST, PUT, PATCH, DELETE)

---

## 🔵 Simple Definition (English)
HTTP methods (verbs) tell the server WHAT KIND of action to perform on a resource. **GET** reads data, **POST** creates data, **PUT** fully replaces data, **PATCH** partially updates data, **DELETE** removes data. Express maps each to `app.get()`, `app.post()`, `app.put()`, `app.patch()`, `app.delete()` — using the correct verb is central to building RESTful APIs.

## 🔵 सरल परिभाषा (Hindi)
HTTP methods (verbs) server को बताते हैं कि resource पर कौन सा action करना है। **GET** data पढ़ता है, **POST** data बनाता है, **PUT** data पूरी तरह replace करता है, **PATCH** data को partially update करता है, **DELETE** data हटाता है। Express इन्हें `app.get()`, `app.post()`, `app.put()`, `app.patch()`, `app.delete()` से map करता है — RESTful APIs बनाने के लिए सही verb use करना जरूरी है।

---

## 🔴 Problem it Solves
```
WITHOUT STANDARD METHODS (everything as GET or POST):
  GET /getUser?id=5
  GET /deleteUser?id=5        ← dangerous! GET requests get cached/prefetched
                                  by browsers/crawlers, could delete data accidentally
  POST /updateUserPartial
  POST /updateUserFull
  → No semantic meaning, no caching rules, no idempotency guarantees

WITH PROPER HTTP METHODS:
  GET    /users/5     → read (safe, cacheable, idempotent)
  DELETE /users/5      → delete (idempotent — calling twice = same result)
  PUT    /users/5      → full replace (idempotent)
  PATCH  /users/5      → partial update (not necessarily idempotent)
  POST   /users        → create (NOT idempotent — calling twice creates 2 users)
  → Clear semantics, proper caching, browsers/proxies behave correctly
```

## 🔴 यह क्यों बना? (Hindi)
बिना standard methods के, सब कुछ GET/POST से होता था — न semantic meaning, न caching rules, न idempotency guarantee। खतरा यह था कि GET requests browsers/crawlers द्वारा prefetch/cache हो जाती हैं, तो अगर delete action GET से हो तो accidental data loss हो सकता है। HTTP methods standard (RFC 7231) ने हर verb का clear meaning और behavior (safe, idempotent, cacheable) define किया।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends a request with a specific HTTP method in the request line (e.g., `GET /users/5 HTTP/1.1`)
Step 2 → Express's router checks the method against each registered route (`app.get`, `app.post`, etc.)
Step 3 → GET/DELETE typically have no request body (though DELETE CAN technically have one); POST/PUT/PATCH typically carry a body
Step 4 → Server performs the appropriate action based on verb semantics (read/create/replace/update/delete)
Step 5 → Server returns an appropriate status code (200 GET, 201 POST, 200/204 PUT/PATCH, 204 DELETE) confirming the semantic outcome

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client request line में specific HTTP method भेजता है (जैसे `GET /users/5 HTTP/1.1`)
Step 2 → Express का router method को registered routes के against check करता है
Step 3 → GET/DELETE में usually body नहीं होता; POST/PUT/PATCH में body होता है
Step 4 → Server verb के semantics के हिसाब से action करता है (read/create/replace/update/delete)
Step 5 → Server appropriate status code return करता है (200 GET, 201 POST, 200/204 PUT/PATCH, 204 DELETE)

---

## 🟡 Real World Example
**Zomato order flow:** `POST /api/orders` creates a new order (not idempotent — retry creates a duplicate order, so clients use idempotency keys). `GET /api/orders/123` fetches order details (safe, cacheable). `PATCH /api/orders/123` updates ONLY the status field (`{ status: 'cancelled' }`) without touching other fields. `PUT /api/orders/123` would replace the ENTIRE order object. `DELETE /api/orders/123` cancels/removes the order — calling it twice has the same end state (idempotent).

## 🟡 Real Example Hindi mein
**Zomato order flow:** `POST /api/orders` नया order बनाता है (not idempotent — retry से duplicate order बन सकता है, इसलिए clients idempotency keys use करते हैं)। `GET /api/orders/123` order details fetch करता है (safe, cacheable)। `PATCH /api/orders/123` सिर्फ status field update करता है। `PUT /api/orders/123` पूरे order object को replace करेगा। `DELETE /api/orders/123` order cancel/remove करता है — दो बार call करने पर भी same end state (idempotent)।

---

## 💻 Code Example — Basic

```javascript
// http-methods-basic.js
const express = require('express');
const app = express();
app.use(express.json());

// In-memory "DB" for demo
let users = [{ id: 1, name: 'Rahul', email: 'rahul@example.com', age: 25 }];

// GET — read data (safe: never modifies server state)
app.get('/users', (req, res) => {
  res.status(200).json(users);
});

// POST — create a new resource (not idempotent: each call adds a new user)
app.post('/users', (req, res) => {
  const newUser = { id: users.length + 1, ...req.body };
  users.push(newUser);
  res.status(201).json(newUser);   // 201 Created
});

// PUT — full replace of a resource (idempotent: same input = same result every time)
app.put('/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === Number(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'User not found' });
  users[index] = { id: Number(req.params.id), ...req.body };  // ENTIRE object replaced
  res.status(200).json(users[index]);
});

// PATCH — partial update (only given fields change)
app.patch('/users/:id', (req, res) => {
  const user = users.find(u => u.id === Number(req.params.id));
  if (!user) return res.status(404).json({ error: 'User not found' });
  Object.assign(user, req.body);   // merge only provided fields
  res.status(200).json(user);
});

// DELETE — remove a resource (idempotent: deleting twice = still gone)
app.delete('/users/:id', (req, res) => {
  users = users.filter(u => u.id !== Number(req.params.id));
  res.status(204).send();   // 204 No Content — success, nothing to return
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// http-methods-advanced.js — idempotency keys, method-based validation

const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const idempotencyStore = new Map();  // simple in-memory store (use Redis in production)

// POST with idempotency key support — safe retries for payment-like operations
app.post('/api/payments', (req, res) => {
  const idempotencyKey = req.headers['idempotency-key'];

  if (!idempotencyKey) {
    return res.status(400).json({ error: 'Idempotency-Key header required' });
  }

  // If we've already processed this exact request, return the cached result
  if (idempotencyStore.has(idempotencyKey)) {
    return res.status(200).json(idempotencyStore.get(idempotencyKey));
  }

  const payment = {
    id: crypto.randomUUID(),
    amount: req.body.amount,
    status: 'success',
  };

  idempotencyStore.set(idempotencyKey, payment);
  res.status(201).json(payment);
});

// PUT requires the FULL resource — validate all required fields present
app.put('/api/profile/:id', (req, res) => {
  const { name, email, age } = req.body;
  if (!name || !email || age === undefined) {
    // PUT semantics require complete replacement — missing fields is a client error
    return res.status(400).json({ error: 'PUT requires full resource: name, email, age' });
  }
  res.status(200).json({ id: req.params.id, name, email, age });
});

// PATCH accepts partial fields — no "required all fields" validation
app.patch('/api/profile/:id', (req, res) => {
  const allowedFields = ['name', 'email', 'age'];
  const updates = Object.keys(req.body).filter(k => allowedFields.includes(k));

  if (updates.length === 0) {
    return res.status(400).json({ error: 'No valid fields to update' });
  }

  const patch = {};
  updates.forEach(key => { patch[key] = req.body[key]; });
  res.status(200).json({ id: req.params.id, updated: patch });
});

// DELETE that's idempotent even for already-deleted resources (returns 204 either way)
const deletedIds = new Set();
app.delete('/api/orders/:id', (req, res) => {
  deletedIds.add(req.params.id);  // adding to a Set twice has no extra effect — idempotent
  res.status(204).send();  // same response whether it existed or was already deleted
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Real-world RESTful resource using all 5 methods consistently
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => res.json({ action: 'list all restaurants' }));
router.get('/:id', (req, res) => res.json({ action: 'get one', id: req.params.id }));
router.post('/', (req, res) => res.status(201).json({ action: 'create', data: req.body }));
router.put('/:id', (req, res) => res.json({ action: 'full update', id: req.params.id }));
router.patch('/:id', (req, res) => res.json({ action: 'partial update', id: req.params.id }));
router.delete('/:id', (req, res) => res.status(204).send());

module.exports = router;
// mounted in app.js as: app.use('/api/restaurants', router);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using GET for actions that modify data
```javascript
// WRONG: GET should NEVER change server state — browsers/crawlers can trigger it accidentally
app.get('/users/:id/delete', (req, res) => {
  deleteUser(req.params.id);  // ❌ a web crawler following this link deletes data!
  res.send('Deleted');
});

// CORRECT: use DELETE method for deletion
app.delete('/users/:id', (req, res) => {
  deleteUser(req.params.id);
  res.status(204).send();
});
```

❌ **Mistake 2:** Confusing PUT and PATCH semantics
```javascript
// WRONG: PUT handler that only updates one field (should be PATCH!)
app.put('/users/:id', (req, res) => {
  user.email = req.body.email;  // ❌ PUT implies FULL replace, but only one field updated
  res.json(user);
});

// CORRECT: PUT replaces everything; PATCH updates partially
app.put('/users/:id', (req, res) => {
  user = { id: req.params.id, ...req.body };  // full replace — missing fields become undefined
});
app.patch('/users/:id', (req, res) => {
  Object.assign(user, req.body);  // merge — only provided fields change
});
```

---

## 🧠 Tricky Interview Question

```javascript
// Client makes this request TWICE due to network retry:
// POST /api/orders  Body: { item: 'Pizza', qty: 2 }

// What's different about calling this endpoint twice vs calling
// DELETE /api/orders/5 twice?
```
Answer: `POST` is NOT idempotent — calling it twice (e.g., due to a network timeout causing a client retry) creates TWO separate orders, which is a real bug source in e-commerce (duplicate orders/charges). `DELETE /api/orders/5` IS idempotent — calling it twice results in the same end state (order 5 is gone either way); the second call might return 404 or still 204, but no additional side effect occurs. This is exactly why payment/order creation APIs use **idempotency keys** (a client-generated unique ID sent in a header) — the server checks if it already processed that key and returns the cached result instead of creating a duplicate.

---

## ⚫ Interview Questions + Answers

Q1: What does "idempotent" mean in the context of HTTP methods, and which methods are idempotent?
A1: An idempotent operation produces the SAME result no matter how many times it's repeated with the same input. GET, PUT, DELETE, HEAD, and OPTIONS are idempotent by specification. POST and PATCH are generally NOT idempotent (POST creates a new resource each time; PATCH *can* be idempotent depending on the operation, e.g., "set field to X" is idempotent, but "increment counter by 1" is not).

Q2: What's the difference between PUT and PATCH?
A2: PUT replaces the ENTIRE resource with the data provided — any field not included is typically removed/reset. PATCH applies a PARTIAL update — only the fields included in the request body change; everything else stays as-is. PUT requires clients to send the complete representation; PATCH lets clients send only what changed.

Q3: Why is GET considered "safe," and what does that mean practically?
A3: "Safe" means the method must NOT change server state — it's purely for retrieval. Practically, this means browsers can prefetch GET requests, crawlers can follow GET links freely, proxies/CDNs can cache GET responses, and retrying a failed GET request is always safe. This is why actions like "delete" or "logout" should NEVER be implemented as GET endpoints (clicking a link or crawler prefetch could trigger them).

Q4: What status codes are conventionally returned for each method on success?
A4: GET → 200 OK. POST → 201 Created (with a `Location` header pointing to the new resource, ideally). PUT → 200 OK (if returning updated resource) or 204 No Content. PATCH → 200 OK or 204 No Content. DELETE → 204 No Content (most common, since there's nothing to return) or 200 if returning a confirmation body.

Q5: How do idempotency keys solve the duplicate-POST problem in payment systems?
A5: The client generates a unique key (e.g., UUID) per logical operation and sends it in a header like `Idempotency-Key`. The server stores the key along with the result of the FIRST successful request. If the same key arrives again (due to retry after timeout/network failure), the server returns the CACHED result instead of re-executing the operation — preventing duplicate charges/orders even though the underlying method (POST) is not idempotent by default.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- GET: fetching/listing data with no side effects
- POST: creating new resources, or actions that don't map to CRUD (e.g., `/api/login`)
- PUT: replacing an entire resource with client-provided data
- PATCH: updating specific fields without affecting the rest
- DELETE: removing a resource

❌ Avoid when:
- Using GET for any state-changing operation (security/caching risk)
- Using PUT when you only have partial data (use PATCH instead, or you'll wipe other fields)
- Overloading POST for everything just to "keep it simple" — loses semantic clarity and tooling benefits (caching, idempotency assumptions)

---

## 📊 Visual Diagram
```
  HTTP METHOD SEMANTICS
  ─────────────────────────────────────────────────────
  GET     /users/5        → READ          (safe, idempotent, cacheable)
  POST    /users          → CREATE        (not safe, NOT idempotent)
  PUT     /users/5        → FULL REPLACE  (not safe, idempotent)
  PATCH   /users/5        → PARTIAL UPDATE(not safe, idempotent*)
  DELETE  /users/5        → REMOVE        (not safe, idempotent)

  *PATCH idempotency depends on the specific operation

  Idempotent = same result no matter how many times you repeat it
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ DELETE/5 │ →  │ DELETE/5 │ →  │ DELETE/5 │   same end state every time
  └──────────┘    └──────────┘    └──────────┘

  Not idempotent:
  ┌────────┐    ┌────────┐    ┌────────┐
  │ POST / │ →  │ POST / │ →  │ POST / │   3 SEPARATE resources created!
  └────────┘    └────────┘    └────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Idempotent | Same result on repeated calls | Repeat करने पर same result |
| Safe method | No server-side side effects | Server पर कोई side effect नहीं |
| Idempotency key | Client-generated ID to dedupe retries | Retries को dedupe करने के लिए client का unique ID |
| RESTful | Resource-oriented API design using HTTP verbs | HTTP verbs से resource-oriented API design |
| 201 Created | Status for successful resource creation | Successful creation का status |

---

## ⚡ 3-Line Summary
English: 1. GET reads, POST creates, PUT fully replaces, PATCH partially updates, DELETE removes — each has defined semantics per RFC 7231. 2. GET/PUT/DELETE are idempotent and safe (GET); POST generally is not idempotent. 3. Use idempotency keys for POST-based payment/order creation to safely handle client retries without duplicating effects.
Hindi: 1. GET पढ़ता है, POST बनाता है, PUT पूरी तरह replace करता है, PATCH partially update करता है, DELETE हटाता है। 2. GET/PUT/DELETE idempotent हैं; POST generally नहीं है। 3. POST-based payment/order creation में client retries safely handle करने के लिए idempotency keys use करो।

---

## ➡️ Next Topic
**91. Middleware in Express.js** — Already covered; see `91-middleware.md` for the deep dive on the middleware pipeline.
