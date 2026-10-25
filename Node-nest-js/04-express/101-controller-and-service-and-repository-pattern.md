# 101. Controller + Service + Repository Pattern
# हिंदी में: Controller + Service + Repository Pattern

---

## 🔵 Simple Definition (English)
This is a more granular layered architecture than basic MVC: **Controller** handles HTTP I/O, **Service** holds business logic (rules, orchestration, calling multiple repositories), and **Repository** is the ONLY layer that talks to the database (abstracting away the specific DB/ORM). This gives clean separation: HTTP ↔ Business Logic ↔ Data Access.

## 🔵 सरल परिभाषा (Hindi)
यह basic MVC से ज्यादा granular layered architecture है: **Controller** HTTP I/O handle करता है, **Service** business logic रखता है (rules, orchestration, कई repositories को call करना), और **Repository** सिर्फ वही layer है जो database से बात करती है (specific DB/ORM को abstract करके)। यह clean separation देता है: HTTP ↔ Business Logic ↔ Data Access।

---

## 🔴 Problem it Solves
```
WITH BASIC MVC (Model does both business logic AND DB access):
  class UserModel {
    async createUser(data) {
      // business logic mixed with DB calls
      const existing = await db.collection('users').findOne({ email: data.email });
      if (existing) throw new Error('Email taken');
      await sendWelcomeEmail(data.email);     // side effect mixed in too
      return db.collection('users').insertOne(data);
    }
  }
  → Hard to test business rules without a real DB
  → Hard to swap MongoDB for PostgreSQL later — DB-specific code is everywhere

WITH CONTROLLER + SERVICE + REPOSITORY:
  Repository: ONLY knows how to query/insert — swappable DB implementation
  Service:    business rules (email uniqueness, side effects) — testable with a MOCK repository
  Controller: HTTP concerns only
```

## 🔴 यह क्यों बना? (Hindi)
Basic MVC में Model अक्सर business logic AND database access दोनों करता था — testing के लिए हमेशा real DB चाहिए होता, DB बदलना (MongoDB से PostgreSQL) मुश्किल होता क्योंकि DB-specific code हर जगह फैला होता। Controller-Service-Repository pattern ने data access को अलग Repository layer में isolate किया, जिससे Service layer को mock करके बिना DB के test किया जा सके, और DB implementation बदलना आसान हो।

---

## 🟢 How it Works — Step by Step

Step 1 → **Controller** receives the request, extracts/validates basic input shape, calls a Service method
Step 2 → **Service** applies BUSINESS RULES (e.g., "email must be unique", "can't cancel a shipped order"), orchestrates calls to one or more Repositories, and may trigger side effects (emails, events)
Step 3 → **Repository** executes the actual database query/mutation (via ORM/driver) and returns plain data — it has NO business logic, just CRUD-style data access
Step 4 → Data flows back UP: Repository → Service → Controller → HTTP response
Step 5 → For testing, you can inject a FAKE/MOCK Repository into the Service to test business logic without touching a real database

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Controller** request लेता है, basic input validate करता है, Service method call करता है
Step 2 → **Service** BUSINESS RULES apply करता है, एक या कई Repositories को call करता है, side effects trigger करता है
Step 3 → **Repository** actual DB query/mutation execute करता है (ORM/driver से), plain data return करता है — कोई business logic नहीं
Step 4 → Data ऊपर जाता है: Repository → Service → Controller → HTTP response
Step 5 → Testing के लिए, Service में FAKE/MOCK Repository inject करके बिना real DB के business logic test कर सकते हैं

---

## 🟡 Real World Example
**Razorpay refund processing:** `RefundRepository` has `findById()`, `create()`, `updateStatus()` — pure DB operations, no logic. `RefundService.processRefund(paymentId, amount)` checks business rules: "refund amount can't exceed payment amount", "payment must be captured first", calls `PaymentRepository.findById()` AND `RefundRepository.create()`, then triggers a notification event. `RefundController.createRefund(req, res)` just validates the request shape and calls `RefundService.processRefund()`. Unit tests mock BOTH repositories to test the service's business rules in isolation — no real database needed.

## 🟡 Real Example Hindi mein
**Razorpay refund processing:** `RefundRepository` सिर्फ DB operations करता है, कोई logic नहीं। `RefundService.processRefund()` business rules check करता है, कई repositories call करता है, notification event trigger करता है। `RefundController` सिर्फ request validate करके service call करता है। Unit tests दोनों repositories को mock करके service के business rules test करते हैं — real database की जरूरत नहीं।

---

## 💻 Code Example — Basic

```javascript
// repositories/userRepository.js — ONLY data access, no business logic
let users = [];   // mock "DB" for demo
let nextId = 1;

const UserRepository = {
  findByEmail: (email) => users.find(u => u.email === email),
  findById: (id) => users.find(u => u.id === id),
  insert: (data) => {
    const user = { id: nextId++, ...data };
    users.push(user);
    return user;
  },
};
module.exports = UserRepository;
```

```javascript
// services/userService.js — BUSINESS LOGIC, calls repository
const UserRepository = require('../repositories/userRepository');

const UserService = {
  registerUser: (data) => {
    // Business rule: email must be unique
    const existing = UserRepository.findByEmail(data.email);
    if (existing) {
      const err = new Error('Email already registered');
      err.statusCode = 409;
      throw err;
    }
    // Business rule: default role assignment
    const user = UserRepository.insert({ ...data, role: data.role || 'customer' });
    return user;
  },
};
module.exports = UserService;
```

```javascript
// controllers/userController.js — HTTP concerns only
const UserService = require('../services/userService');

exports.register = (req, res, next) => {
  try {
    const user = UserService.registerUser(req.body);
    res.status(201).json(user);
  } catch (err) {
    next(err);
  }
};
```

```javascript
// routes/userRoutes.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
router.post('/register', userController.register);
module.exports = router;
```

## 💻 Code Example — Advanced

```javascript
// repositories/orderRepository.js — abstracts the DB (easy to swap MongoDB <-> Postgres)
class OrderRepository {
  constructor(dbClient) {
    this.db = dbClient;   // dependency injection — any DB client with this interface works
  }
  async findById(id) { return this.db.orders.find(o => o.id === id); }
  async updateStatus(id, status) {
    const order = await this.findById(id);
    if (order) order.status = status;
    return order;
  }
  async create(data) {
    const order = { id: this.db.orders.length + 1, status: 'pending', ...data };
    this.db.orders.push(order);
    return order;
  }
}
module.exports = OrderRepository;
```

```javascript
// services/orderService.js — orchestrates multiple repositories + business rules
class OrderService {
  constructor(orderRepository, inventoryRepository, notificationService) {
    this.orderRepository = orderRepository;
    this.inventoryRepository = inventoryRepository;
    this.notificationService = notificationService;
  }

  async placeOrder(data) {
    // Business rule: check stock BEFORE creating order
    const inStock = await this.inventoryRepository.checkStock(data.productId, data.qty);
    if (!inStock) {
      const err = new Error('Insufficient stock');
      err.statusCode = 400;
      throw err;
    }

    const order = await this.orderRepository.create(data);
    await this.inventoryRepository.decrementStock(data.productId, data.qty);
    await this.notificationService.sendOrderConfirmation(order);  // side effect

    return order;
  }

  async cancelOrder(orderId) {
    const order = await this.orderRepository.findById(orderId);
    if (!order) {
      const err = new Error('Order not found');
      err.statusCode = 404;
      throw err;
    }
    // Business rule: can't cancel shipped orders
    if (order.status === 'shipped') {
      const err = new Error('Cannot cancel a shipped order');
      err.statusCode = 400;
      throw err;
    }
    return this.orderRepository.updateStatus(orderId, 'cancelled');
  }
}
module.exports = OrderService;
```

```javascript
// controllers/orderController.js — wires everything via DI
const OrderService = require('../services/orderService');
const OrderRepository = require('../repositories/orderRepository');
// ... assume inventoryRepository, notificationService are set up similarly
const orderService = new OrderService(orderRepository, inventoryRepository, notificationService);

exports.placeOrder = async (req, res, next) => {
  try {
    const order = await orderService.placeOrder(req.body);
    res.status(201).json(order);
  } catch (err) {
    next(err);
  }
};

exports.cancelOrder = async (req, res, next) => {
  try {
    const order = await orderService.cancelOrder(req.params.id);
    res.status(200).json(order);
  } catch (err) {
    next(err);
  }
};
```

---

## 🟠 Express.js Integration

```javascript
// app.js — full layered wiring for a Flipkart-style order service
const express = require('express');
const app = express();
app.use(express.json());

app.use('/api/orders', require('./routes/orderRoutes'));
app.use('/api/users', require('./routes/userRoutes'));

app.use((err, req, res, next) => {
  res.status(err.statusCode || 500).json({ error: err.message });
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting business logic (rules) inside the Repository
```javascript
// WRONG: Repository checking business rules — violates its single responsibility
class UserRepository {
  async insert(data) {
    const existing = await this.db.users.findOne({ email: data.email });  // ❌ business rule here
    if (existing) throw new Error('Email taken');
    return this.db.users.insertOne(data);
  }
}

// CORRECT: Repository only does raw data operations; Service enforces the rule
class UserRepository {
  async insert(data) { return this.db.users.insertOne(data); }
  async findByEmail(email) { return this.db.users.findOne({ email }); }
}
// UserService checks uniqueness BEFORE calling repository.insert()
```

❌ **Mistake 2:** Controller calling the Repository directly, skipping the Service layer
```javascript
// WRONG: bypasses business rules entirely
exports.createOrder = async (req, res) => {
  const order = await OrderRepository.create(req.body);   // ❌ no stock check, no validation
  res.json(order);
};

// CORRECT: always go through the Service for business logic
exports.createOrder = async (req, res, next) => {
  try {
    const order = await orderService.placeOrder(req.body);   // enforces rules
    res.json(order);
  } catch (err) { next(err); }
};
```

---

## 🧠 Tricky Interview Question

```javascript
// Service test using a MOCK repository (no real DB)
const mockRepo = {
  findByEmail: () => ({ id: 1, email: 'taken@example.com' }),  // simulate existing user
  insert: () => { throw new Error('Should never be called!'); },
};
const UserService = require('../services/userService');  // (imagine it's injectable)

// If UserService.registerUser({ email: 'taken@example.com' }) is called with mockRepo,
// what should happen, and why is this test valuable?
```
Answer: It should throw `'Email already registered'` (the business rule error) and NEVER call `mockRepo.insert()`. This test is valuable precisely BECAUSE it doesn't touch a real database — it verifies the Service's BUSINESS LOGIC (the uniqueness check) in complete isolation, running fast and deterministically. This is the core benefit of the Repository pattern: by depending on an INTERFACE (whatever shape the repository has) rather than a concrete DB client, tests can substitute a fake implementation, making business logic unit-testable without spinning up MongoDB/PostgreSQL.

---

## ⚫ Interview Questions + Answers

Q1: What's the core difference in responsibility between Service and Repository layers?
A1: The Repository is responsible ONLY for data access — CRUD operations against a specific data store, with NO business rules (e.g., `findById`, `insert`, `update`). The Service holds BUSINESS LOGIC — rules, validations that require data context, orchestration across multiple repositories, and side effects (sending emails, publishing events). The Service depends on the Repository (via its interface), never the other way around.

Q2: Why is this pattern considered more testable than putting everything in a Model?
A2: Because the Service depends on the Repository through an abstraction (its public method signatures), tests can inject a FAKE/MOCK repository implementing the same interface but with simple canned responses — no real database connection needed. This makes business-logic tests fast, deterministic, and independent of database state/availability.

Q3: How does this pattern make it easier to switch databases (e.g., MongoDB to PostgreSQL)?
A3: Since ALL database-specific code (query syntax, ORM calls) lives exclusively in the Repository layer, switching databases means rewriting ONLY the Repository implementations — the Service and Controller layers, which only call repository methods like `findById()`/`insert()`, remain completely untouched because they don't know or care which database is behind those calls.

Q4: Where should a business rule like "a refund can't exceed the original payment amount" live?
A4: In the SERVICE layer — this is a business rule that requires combining data (payment amount) with logic (comparison) before deciding whether to proceed. It should NOT be in the Repository (which just executes queries) nor purely in the Controller (which shouldn't contain domain logic, only HTTP orchestration).

Q5: Is this pattern overkill for a small CRUD app? When would you introduce it?
A5: For a very small app with simple CRUD and no real business rules, basic MVC (Controller + Model) is often sufficient — adding Service and Repository layers for trivial pass-through operations adds unnecessary indirection. Introduce this pattern when: (1) business logic grows complex enough to need isolated unit testing, (2) multiple data sources/repositories need to be orchestrated together, or (3) you anticipate needing to swap or mock the data layer (e.g., for testing or multi-database support).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Business logic is complex enough to warrant isolated unit testing without a real database
- You need to orchestrate multiple data sources or side effects (emails, events) as part of one business operation
- You anticipate swapping databases/ORMs or need a clean testing seam

❌ Avoid when:
- The app is simple CRUD with no real business rules — the extra layers add boilerplate without proportional benefit
- Early-stage prototypes where speed of iteration matters more than long-term architecture

---

## 📊 Visual Diagram
```
  LAYERED ARCHITECTURE
  ─────────────────────────────────────────────
  HTTP Request
       │
       ▼
  ┌──────────────┐
  │  CONTROLLER    │  HTTP I/O only: req → service call → res
  └───────┬─────────┘
          ▼
  ┌──────────────┐
  │   SERVICE      │  business rules, orchestration, side effects
  └───────┬─────────┘
          ▼
  ┌──────────────┐
  │  REPOSITORY    │  pure data access (DB/ORM specific)
  └───────┬─────────┘
          ▼
       Database

  Testing: Service ←── Mock Repository (no real DB needed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Repository | Pure data-access layer | सिर्फ data-access layer |
| Service | Business logic & orchestration layer | Business logic और orchestration layer |
| Dependency Injection | Passing dependencies instead of hardcoding | Dependencies hardcode करने के बजाय pass करना |
| Mock | Fake implementation for testing | Testing के लिए fake implementation |
| Separation of concerns | Each layer with one responsibility | हर layer की एक responsibility |

---

## ⚡ 3-Line Summary
English: 1. Controller handles HTTP, Service holds business rules/orchestration, Repository does pure data access — each layer has one job. 2. Services depend on Repository interfaces, enabling mock-based unit testing without a real database. 3. Avoid putting business rules in Repositories or bypassing Services from Controllers.
Hindi: 1. Controller HTTP handle करता है, Service business rules रखता है, Repository सिर्फ data access करता है। 2. Services Repository interfaces पर depend करते हैं, जिससे mock-based testing possible होती है। 3. Business rules Repository में मत रखो, और Controller से Service bypass मत करो।

---

## ➡️ Next Topic
**102. Request Validation (express-validator / Joi / Zod)** — Validating and sanitizing incoming request data before it reaches business logic.
