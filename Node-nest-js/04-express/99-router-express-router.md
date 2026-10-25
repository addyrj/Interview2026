# 99. Router — Express Router
# हिंदी में: Express Router

---

## 🔵 Simple Definition (English)
`express.Router()` creates a mini, self-contained instance of an Express app — a "mini-app" that can have its own routes and middleware, and gets "mounted" onto a path in the main app via `app.use(path, router)`. It's the standard way to organize routes into modular, feature-based files.

## 🔵 सरल परिभाषा (Hindi)
`express.Router()` एक mini, self-contained Express app का instance बनाता है — एक "mini-app" जिसके अपने routes और middleware हो सकते हैं, और जो main app में किसी path पर `app.use(path, router)` से "mount" हो जाता है। यह routes को modular, feature-based files में organize करने का standard तरीका है।

---

## 🔴 Problem it Solves
```
WITHOUT ROUTER — all routes crammed into one file:
  // app.js — 2000 lines!
  app.get('/users', ...);
  app.post('/users', ...);
  app.get('/orders', ...);
  app.post('/orders', ...);
  app.get('/products', ...);
  // ... hundreds more routes, impossible to navigate or maintain

WITH ROUTER — split by feature into separate files:
  // routes/users.js
  const router = express.Router();
  router.get('/', listUsers);
  router.post('/', createUser);
  module.exports = router;

  // app.js
  app.use('/api/users', require('./routes/users'));
  app.use('/api/orders', require('./routes/orders'));
  app.use('/api/products', require('./routes/products'));
  → Each feature is self-contained, testable, and maintainable independently
```

## 🔴 यह क्यों बना? (Hindi)
बिना Router के, सभी routes एक ही file में define करने पड़ते — बड़े apps में यह file हजारों lines की हो जाती, maintain करना मुश्किल। Express ने `Router` दिया जो हर feature के routes को अलग file में encapsulate करने देता है, और उन्हें main app में एक path prefix के साथ mount किया जा सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `const router = express.Router()` creates a new router instance (it behaves like a mini `app`)
Step 2 → Define routes/middleware on it exactly like on `app`: `router.get()`, `router.post()`, `router.use()`
Step 3 → Export the router from its file: `module.exports = router`
Step 4 → In the main app, mount it at a path prefix: `app.use('/api/users', router)`
Step 5 → When a request comes to `/api/users/5`, Express strips the `/api/users` prefix and passes `/5` to the router, which then matches it against its OWN internal routes (e.g., `router.get('/:id', ...)`)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const router = express.Router()` एक नया router instance बनाता है (mini `app` जैसा behave करता है)
Step 2 → उस पर `app` जैसे ही routes/middleware define करो: `router.get()`, `router.post()`, `router.use()`
Step 3 → File से router export करो: `module.exports = router`
Step 4 → Main app में path prefix के साथ mount करो: `app.use('/api/users', router)`
Step 5 → Request `/api/users/5` आने पर Express `/api/users` prefix हटाकर `/5` router को देता है, जो अपने internal routes से match करता है

---

## 🟡 Real World Example
**Amazon seller dashboard backend:** Separate router files for each domain — `routes/products.js`, `routes/orders.js`, `routes/inventory.js`, `routes/payouts.js`. Each router has its own middleware (e.g., `routes/payouts.js` requires `requireFinanceRole` middleware applied via `router.use()`). The main `app.js` simply mounts: `app.use('/api/products', productsRouter)`, `app.use('/api/payouts', payoutsRouter)` — keeping each team's code isolated and independently testable.

## 🟡 Real Example Hindi mein
**Amazon seller dashboard backend:** हर domain के लिए अलग router files — `routes/products.js`, `routes/orders.js`, `routes/inventory.js`, `routes/payouts.js`। हर router का अपना middleware होता है (जैसे `payouts.js` में `requireFinanceRole` जो `router.use()` से apply होता है)। Main `app.js` सिर्फ mount करता है — हर team का code isolated और independently testable रहता है।

---

## 💻 Code Example — Basic

```javascript
// routes/users.js
const express = require('express');
const router = express.Router();     // create a router instance

router.get('/', (req, res) => {
  res.json({ users: ['Rahul', 'Priya'] });
});

router.get('/:id', (req, res) => {
  res.json({ id: req.params.id, name: 'Rahul' });
});

router.post('/', (req, res) => {
  res.status(201).json({ created: true, data: req.body });
});

module.exports = router;   // export so app.js can mount it
```

```javascript
// app.js
const express = require('express');
const app = express();
app.use(express.json());

const usersRouter = require('./routes/users');
app.use('/api/users', usersRouter);   // mount at /api/users prefix

// GET  /api/users      → router's '/' handler
// GET  /api/users/5    → router's '/:id' handler (req.params.id = '5')
// POST /api/users      → router's '/' POST handler

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// routes/orders.js — router-level middleware, nested routers, route chaining

const express = require('express');
const router = express.Router();

// Router-level middleware — runs for EVERY route in THIS router only
router.use((req, res, next) => {
  console.log(`Orders router: ${req.method} ${req.path}`);
  next();
});

// Middleware specific to one router, e.g., require auth for all order routes
const requireAuth = (req, res, next) => {
  if (!req.headers.authorization) return res.status(401).json({ error: 'Unauthorized' });
  next();
};
router.use(requireAuth);

// Chained route methods for the same path
router.route('/:id')
  .get((req, res) => res.json({ id: req.params.id, action: 'get' }))
  .patch((req, res) => res.json({ id: req.params.id, action: 'update', data: req.body }))
  .delete((req, res) => res.status(204).send());

router.get('/', (req, res) => res.json({ orders: [] }));
router.post('/', (req, res) => res.status(201).json({ created: true }));

module.exports = router;
```

```javascript
// app.js — mounting with { mergeParams: true } for nested routers

const express = require('express');
const app = express();
app.use(express.json());

// Nested router example: /api/users/:userId/orders/*
const userOrdersRouter = express.Router({ mergeParams: true });
// mergeParams:true lets this nested router access :userId from the PARENT router's path

userOrdersRouter.get('/', (req, res) => {
  res.json({ userId: req.params.userId, orders: [] });   // userId available thanks to mergeParams
});

const usersRouter = express.Router();
usersRouter.use('/:userId/orders', userOrdersRouter);   // nest it inside the users router

app.use('/api/users', usersRouter);
app.use('/api/orders', require('./routes/orders'));

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world modular app structure (Razorpay-style payment service)
// Directory structure:
//   app.js
//   routes/
//     payments.js
//     refunds.js
//     webhooks.js

const express = require('express');
const app = express();
app.use(express.json());

app.use('/api/payments', require('./routes/payments'));
app.use('/api/refunds', require('./routes/refunds'));
app.use('/api/webhooks', require('./routes/webhooks'));

app.use((req, res) => res.status(404).json({ error: 'Route not found' }));

app.listen(3000, () => console.log('Payment service running on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting that nested routers don't automatically inherit parent route params
```javascript
// WRONG: nested router can't see :userId from parent without mergeParams
const nested = express.Router();   // missing { mergeParams: true }
nested.get('/', (req, res) => {
  console.log(req.params.userId);  // undefined!
});
usersRouter.use('/:userId/orders', nested);

// CORRECT: enable mergeParams
const nested = express.Router({ mergeParams: true });
nested.get('/', (req, res) => {
  console.log(req.params.userId);  // works correctly
});
```

❌ **Mistake 2:** Mounting a router but forgetting to export it from its module
```javascript
// WRONG: router defined but never exported
const router = express.Router();
router.get('/', handler);
// missing module.exports = router;  → require() in app.js gets {} — app.use() fails silently/errors

// CORRECT
const router = express.Router();
router.get('/', handler);
module.exports = router;
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();

const router = express.Router();
router.get('/profile', (req, res) => res.send('Profile'));

app.use('/api/users', router);
app.use('/api/admin', router);   // SAME router mounted TWICE at different paths!

app.listen(3000);
// What happens on GET /api/users/profile AND GET /api/admin/profile?
```
Answer: Both requests succeed and return `"Profile"`. A single router instance can be mounted at MULTIPLE different paths in the main app — Express doesn't restrict a router to one mount point. Inside the router, `req.path` would show `/profile` either way (relative to its mount point), but the FULL original URL (`req.originalUrl` or `req.baseUrl`) would differ (`/api/users/profile` vs `/api/admin/profile`). This is a lesser-known but valid pattern — e.g., mounting an "admin" router both under `/api/admin` and under a legacy `/internal` path during a migration.

---

## ⚫ Interview Questions + Answers

Q1: What is `express.Router()` and how does it relate to the main `app` object?
A1: `express.Router()` creates an independent, mountable instance that behaves like a mini Express app — it supports `.get()`, `.post()`, `.use()`, and its own middleware stack. It does NOT have `.listen()` since it's not meant to run standalone; it must be "mounted" onto a real app (or another router) via `app.use(path, router)`. This enables modular route organization.

Q2: What is `req.baseUrl` and how does it relate to a mounted router?
A2: `req.baseUrl` is the path prefix at which the current router (or app) was mounted. If you do `app.use('/api/users', router)` and a request comes to `/api/users/5`, then inside the router, `req.baseUrl` is `'/api/users'` and `req.path` is `'/5'` (relative to the mount point), while `req.originalUrl` remains the FULL original path `/api/users/5`.

Q3: What does `{ mergeParams: true }` do when creating a nested router?
A3: By default, a nested/child router does NOT have access to route parameters defined in its PARENT router's mount path. `mergeParams: true` makes the child router inherit `req.params` from the parent, enabling patterns like `/users/:userId/orders` where the orders router needs `:userId` from the users router that mounted it.

Q4: Can you mount the same router instance at multiple paths?
A4: Yes — a router is just an object; you can call `app.use(path1, router)` and `app.use(path2, router)` with the SAME router reference. It will respond identically under both mount points (relative paths inside it stay the same), though `req.baseUrl`/`req.originalUrl` will differ based on which mount point was actually hit.

Q5: How does router-level middleware (`router.use()`) differ in scope from app-level middleware (`app.use()`)?
A5: `router.use()` middleware only runs for requests that are routed to THAT specific router (i.e., ones matching its mount path AND its own internal routes). `app.use()` at the top-level app runs for all requests reaching the main app, regardless of which router eventually handles them (if it's registered before the router mount). This lets you apply middleware (like auth) scoped to only a specific feature's routes without affecting the rest of the app.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Organizing routes by feature/domain into separate files for maintainability (users, orders, products, etc.)
- Applying middleware scoped to only a subset of routes (e.g., auth only for `/api/admin/*`)
- Building nested resource hierarchies (`/users/:userId/orders`)

❌ Avoid when:
- The app is trivially small (a handful of routes) — a single file may be simpler and sufficient
- Over-nesting routers many levels deep can make request flow harder to trace; keep nesting shallow and purposeful

---

## 📊 Visual Diagram
```
  ROUTER MOUNTING
  ───────────────────────────────────────────
  app.js
    │
    ├── app.use('/api/users', usersRouter)
    │         │
    │         ├── usersRouter.get('/')           → matches GET /api/users
    │         ├── usersRouter.get('/:id')         → matches GET /api/users/42
    │         └── usersRouter.use('/:userId/orders', nestedOrdersRouter)
    │                   │
    │                   └── nestedOrdersRouter.get('/')  → GET /api/users/42/orders
    │
    ├── app.use('/api/orders', ordersRouter)
    └── app.use('/api/products', productsRouter)

  Each router = independent, testable module with its own middleware stack
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `express.Router()` | Mini mountable Express app | Mini mountable Express app |
| Mount path | Prefix at which router is attached | Router जिस prefix पर attach है |
| `req.baseUrl` | Mount path for current router | Current router का mount path |
| `mergeParams` | Inherits parent router's params | Parent router के params inherit करता है |
| Modular routing | Splitting routes into feature files | Routes को feature files में split करना |

---

## ⚡ 3-Line Summary
English: 1. `express.Router()` creates a mini, mountable mini-app for organizing routes by feature in separate files. 2. Mount it with `app.use(path, router)` — the path prefix is stripped before matching inside the router. 3. Use `{ mergeParams: true }` on nested routers to access parent route params like `:userId`.
Hindi: 1. `express.Router()` feature-wise routes organize करने के लिए mini mountable app बनाता है। 2. `app.use(path, router)` से mount करो — prefix router के अंदर match करने से पहले हट जाता है। 3. Nested routers में parent के `:userId` access करने के लिए `{ mergeParams: true }` use करो।

---

## ➡️ Next Topic
**100. MVC Pattern in Express** — Organizing code into Models, Views, Controllers for scalable architecture.
