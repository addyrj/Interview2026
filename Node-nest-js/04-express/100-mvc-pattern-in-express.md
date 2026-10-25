# 100. MVC Pattern in Express
# हिंदी में: Express में MVC Pattern

---

## 🔵 Simple Definition (English)
**MVC (Model-View-Controller)** separates an application into three layers: **Model** (data/business logic, e.g., database schemas), **View** (presentation, e.g., HTML templates/JSON response shape), and **Controller** (handles requests, coordinates Model and View). In Express APIs (no server-rendered views), it's often adapted to Model-Controller-Route, with "View" being the JSON response.

## 🔵 सरल परिभाषा (Hindi)
**MVC (Model-View-Controller)** application को तीन layers में बांटता है: **Model** (data/business logic, जैसे database schemas), **View** (presentation, जैसे HTML templates/JSON response shape), और **Controller** (requests handle करता है, Model और View को coordinate करता है)। Express APIs में (जहाँ server-rendered views नहीं होते), यह अक्सर Model-Controller-Route में adapt होता है, "View" JSON response होता है।

---

## 🔴 Problem it Solves
```
WITHOUT MVC — everything mixed in route handlers:
  app.post('/users', async (req, res) => {
    // Validation logic mixed here
    if (!req.body.email) return res.status(400).json({ error: 'Email required' });
    // Database logic mixed here
    const existing = await db.collection('users').findOne({ email: req.body.email });
    if (existing) return res.status(409).json({ error: 'Email taken' });
    const user = await db.collection('users').insertOne(req.body);
    // Response formatting mixed here
    res.status(201).json({ id: user.insertedId, email: req.body.email });
  });
  → 200+ lines per route file, impossible to test business logic separately

WITH MVC:
  routes/users.js    → router.post('/', userController.createUser)
  controllers/userController.js → calls userService, formats response
  models/User.js      → defines schema, DB queries
  → Each layer testable independently, clear responsibilities
```

## 🔴 यह क्यों बना? (Hindi)
बिना MVC के, route handlers में validation, DB logic, और response formatting सब mix हो जाता था — testing और maintenance मुश्किल हो जाती थी। MVC ने हर concern को अलग layer में separate किया: Model data संभालता है, Controller request flow coordinate करता है, और (API context में) response shape "View" का काम करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Route** receives the HTTP request and maps it to a specific controller function
Step 2 → **Controller** extracts/validates input from `req`, calls the appropriate Model/Service method
Step 3 → **Model** interacts with the database (queries, schema validation) and returns data
Step 4 → **Controller** receives the data back, decides the response shape and status code
Step 5 → Response ("View" in API context — a JSON structure) is sent back via `res.json()`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Route** HTTP request लेता है और specific controller function से map करता है
Step 2 → **Controller** `req` से input extract/validate करता है, appropriate Model/Service method call करता है
Step 3 → **Model** database से interact करता है (queries, schema validation) और data return करता है
Step 4 → **Controller** data वापस लेकर response shape और status code decide करता है
Step 5 → Response ("View" API context में — JSON structure) `res.json()` से भेजा जाता है

---

## 🟡 Real World Example
**Zomato restaurant management backend:** `models/Restaurant.js` defines the Mongoose schema and static query methods (`Restaurant.findNearby(coords)`). `controllers/restaurantController.js` has `getNearbyRestaurants(req, res)` which validates `req.query.lat/lng`, calls `Restaurant.findNearby()`, and formats the JSON response. `routes/restaurants.js` wires `router.get('/nearby', restaurantController.getNearbyRestaurants)`. Each file has ONE clear job — a new engineer can find any logic quickly.

## 🟡 Real Example Hindi mein
**Zomato restaurant management backend:** `models/Restaurant.js` Mongoose schema और query methods define करता है। `controllers/restaurantController.js` में `getNearbyRestaurants` function `req.query` validate करके model को call करता है और response format करता है। `routes/restaurants.js` route को controller से जोड़ता है। हर file का एक clear job है — नया engineer जल्दी logic ढूंढ सकता है।

---

## 💻 Code Example — Basic

```javascript
// models/userModel.js — "Model" layer: data access
let users = [{ id: 1, name: 'Rahul', email: 'rahul@example.com' }];  // mock in-memory DB

const UserModel = {
  findAll: () => users,
  findById: (id) => users.find(u => u.id === Number(id)),
  create: (data) => {
    const newUser = { id: users.length + 1, ...data };
    users.push(newUser);
    return newUser;
  },
};
module.exports = UserModel;
```

```javascript
// controllers/userController.js — "Controller" layer: request/response logic
const UserModel = require('../models/userModel');

const UserController = {
  getAllUsers: (req, res) => {
    const users = UserModel.findAll();
    res.status(200).json(users);          // "View" = JSON shape
  },
  getUserById: (req, res) => {
    const user = UserModel.findById(req.params.id);
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.status(200).json(user);
  },
  createUser: (req, res) => {
    if (!req.body.email) return res.status(400).json({ error: 'Email required' });
    const user = UserModel.create(req.body);
    res.status(201).json(user);
  },
};
module.exports = UserController;
```

```javascript
// routes/userRoutes.js — "Route" layer: wiring
const express = require('express');
const router = express.Router();
const UserController = require('../controllers/userController');

router.get('/', UserController.getAllUsers);
router.get('/:id', UserController.getUserById);
router.post('/', UserController.createUser);

module.exports = router;
```

```javascript
// app.js
const express = require('express');
const app = express();
app.use(express.json());
app.use('/api/users', require('./routes/userRoutes'));
app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// models/orderModel.js — Model with validation logic encapsulated
class OrderModel {
  constructor() {
    this.orders = [];
    this.nextId = 1;
  }

  validate(data) {
    const errors = [];
    if (!data.items || data.items.length === 0) errors.push('items required');
    if (!data.userId) errors.push('userId required');
    return errors;
  }

  create(data) {
    const errors = this.validate(data);
    if (errors.length) {
      const err = new Error('Validation failed');
      err.statusCode = 400;
      err.details = errors;
      throw err;
    }
    const order = { id: this.nextId++, status: 'pending', ...data };
    this.orders.push(order);
    return order;
  }

  findById(id) {
    return this.orders.find(o => o.id === Number(id));
  }
}
module.exports = new OrderModel();   // singleton instance
```

```javascript
// controllers/orderController.js — Controller delegates to Model, handles HTTP concerns only
const OrderModel = require('../models/orderModel');

exports.createOrder = (req, res, next) => {
  try {
    const order = OrderModel.create(req.body);     // Model throws on invalid data
    res.status(201).json(order);
  } catch (err) {
    next(err);    // delegate error formatting to centralized error middleware
  }
};

exports.getOrder = (req, res) => {
  const order = OrderModel.findById(req.params.id);
  if (!order) return res.status(404).json({ error: 'Order not found' });
  res.status(200).json(order);
};
```

```javascript
// routes/orderRoutes.js
const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');

router.post('/', orderController.createOrder);
router.get('/:id', orderController.getOrder);

module.exports = router;
```

---

## 🟠 Express.js Integration

```javascript
// Full MVC wiring in app.js for a Paytm-style wallet service
const express = require('express');
const app = express();
app.use(express.json());

app.use('/api/users', require('./routes/userRoutes'));
app.use('/api/orders', require('./routes/orderRoutes'));
app.use('/api/wallet', require('./routes/walletRoutes'));

app.use((err, req, res, next) => {
  res.status(err.statusCode || 500).json({ error: err.message, details: err.details });
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting database queries directly inside controllers
```javascript
// WRONG: controller directly touches the DB — hard to test, hard to reuse
exports.getUser = async (req, res) => {
  const user = await db.collection('users').findOne({ _id: req.params.id });  // ❌ DB logic in controller
  res.json(user);
};

// CORRECT: controller delegates to the Model
exports.getUser = async (req, res) => {
  const user = await UserModel.findById(req.params.id);
  res.json(user);
};
```

❌ **Mistake 2:** Controllers sending responses directly from Model methods (tight coupling)
```javascript
// WRONG: Model knows about HTTP (res) — breaks separation of concerns
class UserModel {
  findById(id, res) {   // ❌ Model should NEVER receive res
    res.json({ id });
  }
}

// CORRECT: Model only returns/throws data; Controller decides HTTP response
class UserModel {
  findById(id) { return { id }; }   // pure data logic, no HTTP awareness
}
```

---

## 🧠 Tricky Interview Question

```javascript
// controllers/userController.js
exports.createUser = async (req, res) => {
  const user = await UserModel.create(req.body);
  res.status(201).json(user);
};

// models/userModel.js
exports.create = async (data) => {
  if (!data.email) throw new Error('Email required');   // sync throw inside async function
  return db.insert(data);
};

// What happens if 'Email required' is thrown, given the controller has NO try/catch?
```
Answer: The request HANGS (or crashes the process on unhandled rejection, depending on Node version/config) — because `createUser` is an `async` function and the error is thrown inside `UserModel.create` (also async), it becomes a REJECTED PROMISE. Since the controller's `await UserModel.create(...)` is not wrapped in try/catch, and Express doesn't automatically catch rejected promises from route handlers, the error is never passed to `next(err)` and the centralized error middleware never fires. The fix: wrap the controller logic in try/catch and call `next(err)`, or use an `asyncHandler` wrapper utility.

---

## ⚫ Interview Questions + Answers

Q1: In the context of a JSON REST API (not server-rendered HTML), what does "View" mean in MVC?
A1: Since there's no HTML template rendering, "View" is reinterpreted as the SHAPE/STRUCTURE of the JSON response — i.e., how data is formatted before being sent via `res.json()`. Some architectures introduce a dedicated "serializer" or "presenter" layer for this (e.g., converting a DB document into a public-facing DTO, excluding sensitive fields like password hashes).

Q2: What's the key responsibility boundary between Controller and Model?
A2: The Controller handles HTTP-specific concerns: reading `req`, validating/extracting input, choosing status codes, formatting the response. The Model handles DATA concerns: database queries, business rule validation, data transformation — it should have NO knowledge of `req`/`res` objects. This separation lets you test Model logic without spinning up an HTTP server, and swap out the HTTP layer (e.g., for a CLI tool) without touching Model code.

Q3: Why is it considered bad practice for a Model method to accept and use the `res` object directly?
A3: It tightly couples data logic to the HTTP layer, destroying the Model's reusability and testability — you couldn't call that Model method from a background job, a CLI script, or a GraphQL resolver without dragging along an Express `res` object. Models should return data or throw errors; the Controller decides HOW to communicate the result over HTTP.

Q4: How does MVC in Express differ from MVC in a framework like Ruby on Rails or Django?
A4: Rails/Django have MVC baked into the framework with strict conventions (auto-routing by naming convention, built-in ORM as the Model layer, template engines as View). Express is UNOPINIONATED — MVC is a PATTERN you impose yourself through folder structure (`routes/`, `controllers/`, `models/`) and discipline; Express doesn't enforce or auto-wire anything. This gives flexibility but requires more manual setup and team convention agreement.

Q5: Where should request validation logic live in an MVC-structured Express app?
A5: Commonly, BASIC format/presence validation (is email present, is age a number) lives in a dedicated VALIDATION MIDDLEWARE layer (using `express-validator`/Joi/Zod) that runs BEFORE the controller — keeping the controller clean. BUSINESS RULE validation (is this email already taken, is this operation allowed given current state) often lives in the Model/Service layer, since it requires data access. The controller itself should ideally contain minimal logic — just orchestration.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building medium-to-large APIs where separating concerns improves maintainability and testability
- Multiple developers/teams work on different features and need clear boundaries

❌ Avoid when:
- A tiny prototype/script-level app where the overhead of multiple files/layers isn't justified
- When it devolves into "MVC in name only" — controllers that still do everything, defeating the purpose (watch for this anti-pattern)

---

## 📊 Visual Diagram
```
  MVC FLOW IN EXPRESS (API context)
  ─────────────────────────────────────────────
  HTTP Request
       │
       ▼
  ┌─────────────┐
  │   ROUTE       │  maps URL+method → controller function
  └──────┬────────┘
         ▼
  ┌─────────────┐
  │  CONTROLLER   │  validates input, calls Model, picks status code
  └──────┬────────┘
         ▼
  ┌─────────────┐
  │    MODEL      │  DB queries, business rules, returns/throws data
  └──────┬────────┘
         ▼
  (back to Controller)
         │
         ▼
  ┌─────────────┐
  │ "VIEW" (JSON) │  res.json({...}) — shaped response
  └─────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model | Data & business logic layer | Data और business logic layer |
| View | Response presentation (JSON shape) | Response presentation (JSON shape) |
| Controller | Request orchestration layer | Request orchestration layer |
| Separation of concerns | Each layer has one job | हर layer का एक ही काम |
| Route | URL-to-controller mapping | URL-to-controller mapping |

---

## ⚡ 3-Line Summary
English: 1. MVC separates Routes (URL mapping), Controllers (request orchestration), and Models (data/business logic) for maintainability. 2. In JSON APIs, "View" becomes the shape of the JSON response rather than an HTML template. 3. Models should never touch `req`/`res` directly — keep HTTP concerns strictly in Controllers.
Hindi: 1. MVC Routes, Controllers, और Models को अलग करता है maintainability के लिए। 2. JSON APIs में "View" JSON response की shape बन जाता है। 3. Models को कभी `req`/`res` directly touch नहीं करना चाहिए — HTTP concerns Controllers में रखो।

---

## ➡️ Next Topic
**101. Controller + Service + Repository Pattern** — A more granular layered architecture splitting business logic from data access.
