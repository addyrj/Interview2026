# 210. Integration Testing
# हिंदी में: Integration Testing — कई Modules को साथ में Test करना

---

## 🔵 Simple Definition (English)
**Integration testing** verifies that multiple pieces of your system work correctly together — e.g. an Express route + a service + a real (test) database. Unlike unit tests, dependencies are NOT mocked (or only partially mocked); the goal is to catch bugs that happen at the "seams" between modules, which unit tests miss.

## 🔵 सरल परिभाषा (Hindi)
**Integration testing** यह check करता है कि system के कई हिस्से — जैसे Express route + service + real (test) database — साथ में सही काम करते हैं या नहीं। Unit tests में dependencies mock होती हैं, पर integration tests में नहीं (या कम mock होती हैं) — ताकि modules के बीच के "seam" bugs पकड़ में आएं जो unit tests miss कर देते हैं।

---

## 🔴 Problem it Solves
A unit test proves `calculateDiscount()` works in isolation, and another proves the DB layer's `saveOrder()` works. But what if the route handler passes the wrong field name between them? Both unit tests pass, yet the real app breaks in production. Integration tests catch exactly this class of bug — wrong SQL query, wrong HTTP status mapping, wrong middleware order — by exercising the real wiring between components, typically against a real (but disposable/test) database.

## 🔴 यह क्यों बना? (Hindi)
एक unit test prove करता है कि `calculateDiscount()` अलग से सही काम करता है, और दूसरा prove करता है कि DB layer का `saveOrder()` सही काम करता है। पर अगर route handler बीच में गलत field नाम पास कर दे? दोनों unit tests pass होंगे, फिर भी production में app टूट जाएगा। Integration tests यही class की bugs पकड़ते हैं — गलत SQL query, गलत HTTP status mapping, गलत middleware order — modules के बीच की real wiring को एक real (पर disposable) test database के साथ चला कर।

---

## 🟢 How it Works — Step by Step

Step 1 → Spin up a test database (in-memory SQLite, a Docker Postgres container, or `mongodb-memory-server`) — separate from production data
Step 2 → `beforeAll`/`beforeEach` seed known test data; `afterEach`/`afterAll` clean up so tests don't leak state into each other
Step 3 → Call the real route handler / service chain — only mock truly external systems (3rd-party payment APIs, SMS gateways)
Step 4 → Assert on real side effects: was a row actually inserted? Does a second query reflect the change?
Step 5 → Tear down: close DB connections, drop test data, so CI runs stay clean and repeatable

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक test database चालू करो (in-memory SQLite, Docker Postgres container, या `mongodb-memory-server`) — production data से अलग
Step 2 → `beforeAll`/`beforeEach` में known test data seed करो; `afterEach`/`afterAll` में cleanup करो ताकि tests एक-दूसरे में state leak न करें
Step 3 → Real route handler / service chain call करो — केवल truly external systems (3rd-party payment API, SMS gateway) को mock करो
Step 4 → Real side effects पर assert करो: क्या row actually insert हुई? क्या दूसरी query change reflect करती है?
Step 5 → Teardown: DB connections close करो, test data drop करो, ताकि CI runs clean और repeatable रहें

---

## 🟡 Real World Example
**Paytm's wallet-topup service** has a route (`POST /wallet/topup`) → a service layer (validates amount, calls bank API) → a DB write (updates wallet balance) → an event emit (sends notification). A unit test can mock the bank API and DB separately, but an integration test spins up a test Postgres DB, calls the real route with a test HTTP client, and verifies: the wallet row balance actually increased by the right amount, a transaction log row was created, and the response JSON has the right shape — catching bugs in how these pieces are wired together that unit tests alone would miss.

## 🟡 Real Example Hindi mein
**Paytm की wallet-topup service** में एक route (`POST /wallet/topup`) → service layer (amount validate करता है, bank API call करता है) → DB write (wallet balance update करता है) → event emit (notification भेजता है) होता है। Unit test अलग से bank API और DB mock कर सकता है, पर integration test एक test Postgres DB चला कर, real HTTP client से real route call करके verify करता है: wallet row का balance सही amount से बढ़ा, transaction log row बनी, और response JSON का shape सही है — ये bugs पकड़ता है जो सिर्फ unit tests miss कर देते।

---

## 💻 Code Example — Basic

```javascript
// db.js — simple in-memory "database" using an array (simulating a real DB layer)
let users = [];
let nextId = 1;

async function createUser(name, email) {
  // Simulate async DB call
  const user = { id: nextId++, name, email };
  users.push(user);
  return user;
}

async function findUserByEmail(email) {
  return users.find(u => u.email === email) || null;
}

function resetDb() {
  users = [];
  nextId = 1;
}

module.exports = { createUser, findUserByEmail, resetDb };
```

```javascript
// userService.js — logic that uses the DB layer (what we integration test)
const { createUser, findUserByEmail } = require('./db');

async function registerUser(name, email) {
  // Check for duplicate email — real integration behavior, not mocked
  const existing = await findUserByEmail(email);
  if (existing) {
    throw new Error('Email already registered');
  }
  return createUser(name, email);
}

module.exports = { registerUser };
```

```javascript
// userService.integration.test.js — tests DB + service layer TOGETHER (no mocks)
const { registerUser } = require('./userService');
const { resetDb, findUserByEmail } = require('./db');

describe('registerUser (integration)', () => {
  // Reset the "database" before every test so tests don't affect each other
  beforeEach(() => {
    resetDb();
  });

  test('creates a new user and persists it to DB', async () => {
    const user = await registerUser('Amit', 'amit@example.com');

    expect(user.id).toBeDefined();
    // Verify by querying the DB again — proves the write ACTUALLY happened
    const found = await findUserByEmail('amit@example.com');
    expect(found.name).toBe('Amit');
  });

  test('rejects duplicate email across the full flow', async () => {
    await registerUser('Amit', 'amit@example.com');
    // Second registration with same email should fail
    await expect(registerUser('Amit2', 'amit@example.com'))
      .rejects.toThrow('Email already registered');
  });
});
```

## 💻 Code Example — Advanced

```javascript
// integration-with-real-db.test.js — using a real SQLite file DB for integration tests
// npm install better-sqlite3
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const TEST_DB_PATH = path.join(__dirname, 'test.db');

describe('Orders integration (real SQLite)', () => {
  let db;

  // Runs ONCE before all tests in this file
  beforeAll(() => {
    // Delete any leftover test DB file from a previous failed run
    if (fs.existsSync(TEST_DB_PATH)) fs.unlinkSync(TEST_DB_PATH);

    db = new Database(TEST_DB_PATH);
    db.exec(`
      CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending'
      )
    `);
  });

  // Runs after EVERY test — keeps tests independent
  afterEach(() => {
    db.exec('DELETE FROM orders');
  });

  // Runs once after all tests — cleanup the DB file
  afterAll(() => {
    db.close();
    fs.unlinkSync(TEST_DB_PATH);
  });

  function createOrder(userId, amount) {
    const stmt = db.prepare('INSERT INTO orders (user_id, amount) VALUES (?, ?)');
    const result = stmt.run(userId, amount);
    return result.lastInsertRowid;
  }

  function markOrderPaid(orderId) {
    db.prepare("UPDATE orders SET status = 'paid' WHERE id = ?").run(orderId);
  }

  test('creates order then marks it paid — full flow', () => {
    const orderId = createOrder('user123', 999.99);

    // Verify the order was actually inserted with correct initial status
    let order = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    expect(order.status).toBe('pending');
    expect(order.amount).toBe(999.99);

    // Now run the second operation and verify real DB state changed
    markOrderPaid(orderId);
    order = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    expect(order.status).toBe('paid');
  });

  test('multiple orders for same user are independent', () => {
    const id1 = createOrder('user123', 100);
    const id2 = createOrder('user123', 200);

    markOrderPaid(id1);

    const order1 = db.prepare('SELECT * FROM orders WHERE id = ?').get(id1);
    const order2 = db.prepare('SELECT * FROM orders WHERE id = ?').get(id2);

    expect(order1.status).toBe('paid');
    expect(order2.status).toBe('pending'); // unaffected — proves isolation within flow
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// app.js — exported Express app (NOT listening) so tests can import it directly
const express = require('express');
const app = express();
app.use(express.json());

app.post('/users', async (req, res) => {
  try {
    const { registerUser } = require('./userService');
    const user = await registerUser(req.body.name, req.body.email);
    res.status(201).json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

module.exports = app; // exported, not app.listen() — lets tests control the server

// app.integration.test.js — full HTTP-level integration test using supertest
const request = require('supertest');
const app = require('./app');
const { resetDb } = require('./db');

describe('POST /users (integration)', () => {
  beforeEach(() => resetDb());

  test('creates user via real HTTP request through full middleware stack', async () => {
    const res = await request(app)
      .post('/users')
      .send({ name: 'Priya', email: 'priya@example.com' });

    expect(res.status).toBe(201);
    expect(res.body.name).toBe('Priya');
  });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reusing the production database for tests
```javascript
// WRONG: tests run against the real production DB connection string
const db = require('../config/db'); // points to prod!
// Tests create/delete REAL customer data — disaster.

// CORRECT: use a dedicated test DB via environment variable
const dbUrl = process.env.NODE_ENV === 'test'
  ? process.env.TEST_DATABASE_URL
  : process.env.DATABASE_URL;
```

❌ Mistake 2: Not cleaning up state between tests, causing flaky order-dependent tests
```javascript
// WRONG: no cleanup — test 2 fails if test 1 ran first and left data behind
test('finds exactly one user', async () => {
  expect((await getAllUsers()).length).toBe(1); // fails if other tests added users
});

// CORRECT: reset state before each test
beforeEach(async () => { await resetDb(); });
```

---

## 🧠 Tricky Interview Question

```javascript
describe('Suite A', () => {
  test('creates order #1', async () => {
    await createOrder('u1', 100);
    expect((await getOrderCount())).toBe(1);
  });
});
describe('Suite B', () => {
  test('creates order #2', async () => {
    await createOrder('u2', 200);
    expect((await getOrderCount())).toBe(1); // ❓ passes or fails?
  });
});
```
Answer: **It depends on test isolation, and usually this FAILS or is flaky.** If both suites share the same underlying test database without `beforeEach`/`afterEach` cleanup, Suite B's assertion of count `1` actually sees `2` orders (the one from Suite A persisted). Jest runs test files in separate processes by default (so separate in-memory state per FILE), but tests WITHIN the same file/describe share database state unless explicitly reset. This is exactly why integration tests must reset DB state between every test — order of execution should never affect the result.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between unit and integration tests?
A1: Unit tests isolate ONE function/module and mock all dependencies — fast, no real I/O. Integration tests exercise multiple real components together (route → service → real test DB) with minimal mocking — slower, but catch wiring/contract bugs between modules that unit tests can't see.

Q2: Why use a separate test database instead of mocking the DB entirely?
A2: Mocking the DB only tests "did my code call the DB function with X args" — it can't catch real SQL errors, constraint violations, wrong column names, or transaction behavior. A real (disposable) test DB catches actual persistence bugs, at the cost of being slower than pure mocks.

Q3: What's a good strategy for test database setup in CI?
A3: Use `docker-compose` to spin up a real Postgres/MySQL container in the CI pipeline, run migrations against it, then run integration tests. Alternatively use lightweight in-memory options like `mongodb-memory-server` or SQLite file DB for faster, no-Docker-needed tests, when the production DB behavior differences don't matter much.

Q4: How do you prevent integration tests from being slow and flaky?
A4: (1) Use `beforeEach`/`afterEach` to reset state — never depend on test execution order. (2) Use transactions that are rolled back after each test instead of full table truncation, for speed. (3) Mock only truly external/unreliable systems (3rd-party APIs, email/SMS) — never mock your own DB in an integration test. (4) Run integration tests in parallel-safe isolated schemas/DBs when using CI parallelization.

Q5: Should integration tests mock external payment gateways like Razorpay?
A5: Yes — always mock genuinely external 3rd-party services in integration tests (payment gateways, SMS/email providers, other microservices you don't own). You want to test YOUR system's wiring reliably and fast, without network flakiness, real charges, or rate limits. Use the gateway's official test/sandbox mode if available, or mock the HTTP call with recorded responses (e.g., `nock`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Verifying that a route handler, service, and database actually work together correctly
- Testing contract behavior (DB constraints, transaction rollback, status code mapping)
- Before deploying critical paths like payments, orders, auth

❌ Avoid when:
- You just need to test pure business logic (unit test is faster and sufficient)
- The 3rd-party dependency is unreliable/costly to call repeatedly (mock it instead)
- You need instant feedback on every keystroke (integration tests are slower — save for CI/pre-push)

---

## 📊 Visual Diagram
```
UNIT TEST vs INTEGRATION TEST:
───────────────────────────────────────────────
UNIT TEST:
  [ Function ] ← mocked DB, mocked payment, mocked everything
  Fast (ms), isolated, many of them

INTEGRATION TEST:
  [ HTTP Request ]
        │
        ▼
  [ Express Route ] → [ Service Layer ] → [ Real Test DB ]
        │                                       │
        └────────────── real wiring ────────────┘
  Slower (seconds), catches wiring bugs, fewer of them
  Only mock: 3rd-party payment/SMS/email APIs

Test Pyramid:
        ▲
       /E2E\        (few, slow, full browser/app)
      /-----\
     / Integ \      (some, medium speed)
    /---------\
   /   Unit    \    (many, fast, isolated)
  /_____________\
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Integration test | Tests multiple modules together | कई modules को साथ test करना |
| Test database | Disposable DB used only for tests | केवल tests के लिए DB |
| beforeEach/afterEach | Setup/cleanup hooks per test | हर test से पहले/बाद का setup |
| Seeding | Inserting known test data | Known test data डालना |
| Teardown | Cleaning up after tests | Tests के बाद cleanup |
| Flaky test | Test that passes/fails inconsistently | कभी pass कभी fail होने वाला test |
| Test pyramid | Ratio of unit/integration/e2e tests | Unit/integration/e2e का ratio |
| supertest | Library for HTTP-level route testing | HTTP route testing library |

---

## ⚡ 3-Line Summary
English:
1. Integration tests verify that multiple real components (route + service + DB) work correctly together, catching wiring bugs unit tests miss.
2. Use a dedicated, disposable test database — never the production DB — and reset state between every test with `beforeEach`/`afterEach`.
3. Only mock truly external 3rd-party systems (payment gateways, SMS/email); keep your own DB and service layers real for genuine integration coverage.

Hindi:
1. Integration tests कई real components (route + service + DB) को साथ में test करते हैं — unit tests जो wiring bugs miss करते हैं वो पकड़ते हैं।
2. Hमेशा dedicated, disposable test database use करो — production DB कभी नहीं — और हर test से पहले state reset करो।
3. केवल truly external 3rd-party systems (payment gateway, SMS/email) mock करो; अपना DB और service layer real रखो ताकि genuine integration coverage मिले।

---

## ➡️ Next Topic
**211. API Testing (Supertest)** — Express routes को real HTTP requests भेज कर test करना, status codes और response bodies को assert करना।
