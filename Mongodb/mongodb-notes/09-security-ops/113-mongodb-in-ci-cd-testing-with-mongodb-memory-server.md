# 113. MongoDB in CI/CD (testing with mongodb-memory-server)
# हिंदी में: CI/CD में MongoDB (mongodb-memory-server से testing)

---

## 🔵 Simple Definition (English)
Testing code that talks to MongoDB needs a real MongoDB. In **CI/CD** (GitHub Actions, GitLab CI, Jenkins) you have three practical options: **`mongodb-memory-server`** (an npm package that downloads and starts a throw-away real `mongod` from your tests, storing data in memory/temp folder), a **service container** (a MongoDB Docker container started next to your job), or **Testcontainers**. All three give you a real database, unlike mocks, so index rules, duplicate-key errors and aggregation behave exactly like production.

## 🔵 सरल परिभाषा (Hindi)
MongoDB से बात करने वाले code को test करने के लिए असली MongoDB चाहिए। **CI/CD** (GitHub Actions, GitLab CI, Jenkins) में तीन practical तरीके हैं: **`mongodb-memory-server`** (npm package जो आपके tests से एक अस्थायी असली `mongod` download और start करता है, data memory/temp folder में रहता है), **service container** (job के साथ चलने वाला MongoDB Docker container), या **Testcontainers**। तीनों असली database देते हैं, mocks की तरह नहीं, इसलिए index rules, duplicate-key errors और aggregation बिल्कुल production जैसे चलते हैं।

---

## 🔴 Problem it Solves
Mocking the driver (`jest.fn()` returning fake documents) proves nothing: it will not catch a missing unique index, a wrong `$group`, or an `E11000` error. Pointing tests at a shared dev database makes tests slow, flaky and destructive (one developer's test deletes another's data, parallel CI runs collide). You need an isolated, disposable, fast, real MongoDB for every test run, with zero manual setup on every developer laptop and CI machine.

## 🔴 यह क्यों बना? (Hindi)
Driver को mock करना (`jest.fn()` जो नकली documents दे) कुछ साबित नहीं करता: यह missing unique index, गलत `$group` या `E11000` error नहीं पकड़ेगा। Tests को shared dev database पर चलाने से वे धीमे, flaky और खतरनाक हो जाते हैं (एक developer का test दूसरे का data मिटा दे, parallel CI runs टकराएँ)। हर test run के लिए अलग, disposable, तेज़ और असली MongoDB चाहिए, बिना हर laptop और CI machine पर manual setup के।

---

## 🟢 How it Works — Step by Step

Step 1 -> `npm i -D mongodb-memory-server` (we tested v11.3 with MongoDB 8.0.4).
Step 2 -> In `beforeAll`, call `MongoMemoryServer.create()`. It finds or downloads a `mongod` binary (cached under `node_modules/.cache`), starts it on a **random free port** with a temp data directory.
Step 3 -> `mongod.getUri()` gives a connection string like `mongodb://127.0.0.1:PORT/`; connect Mongoose or the driver to it.
Step 4 -> Run tests; clean collections in `afterEach` (`deleteMany({})`) so tests stay independent.
Step 5 -> In `afterAll`, disconnect and call `mongod.stop()` (kills the process and deletes the temp folder).
Step 6 -> In CI, cache the binary (`~/.cache/mongodb-binaries` or `node_modules/.cache`) so you do not re-download ~100+ MB each run, and pin the version (`MONGOMS_VERSION`) to match production. For transactions or change streams use `MongoMemoryReplSet`.
Step 7 -> If your CI cannot download binaries (air-gapped), set `MONGOMS_SYSTEM_BINARY=/usr/bin/mongod` to use an installed one, or use a service container instead.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> `npm i -D mongodb-memory-server` (हमने v11.3 को MongoDB 8.0.4 के साथ test किया)।
Step 2 -> `beforeAll` में `MongoMemoryServer.create()` call करो। यह `mongod` binary ढूँढता या download करता है (`node_modules/.cache` में cache), और उसे **random free port** पर temp data directory के साथ चलाता है।
Step 3 -> `mongod.getUri()` से `mongodb://127.0.0.1:PORT/` जैसी connection string मिलती है; Mongoose या driver को उससे जोड़ो।
Step 4 -> Tests चलाओ; `afterEach` में collections साफ करो (`deleteMany({})`) ताकि tests independent रहें।
Step 5 -> `afterAll` में disconnect करके `mongod.stop()` call करो (process बंद और temp folder delete)।
Step 6 -> CI में binary cache करो (`~/.cache/mongodb-binaries` या `node_modules/.cache`) ताकि हर run में ~100+ MB दोबारा download न हो, और version pin करो (`MONGOMS_VERSION`) ताकि production से मेल खाए। Transactions या change streams के लिए `MongoMemoryReplSet` इस्तेमाल करो।
Step 7 -> अगर CI binaries download नहीं कर सकता (air-gapped), तो `MONGOMS_SYSTEM_BINARY=/usr/bin/mongod` से installed binary इस्तेमाल करो, या service container लो।

---

## 🟡 Real World Example
**Swiggy-style order service:** the team's pull-request pipeline must prove that "an order with a duplicate `idempotencyKey` returns 409" and "the daily-revenue aggregation returns the right totals". Developers run `npm test` locally in 2 seconds (an in-memory `mongod` starts, 2 tests run, it shuts down). On every PR, GitHub Actions runs the same tests against MongoDB 8.0 pinned to match production, plus a nightly job that runs integration tests against a service container with the production indexes script. Nobody shares a database, and a broken index definition fails the PR instead of the production deploy.

## 🟡 Real Example Hindi mein
**Swiggy जैसी order service:** टीम की pull-request pipeline को साबित करना है कि "duplicate `idempotencyKey` वाला order 409 लौटाता है" और "daily-revenue aggregation सही totals देता है"। Developers locally `npm test` 2 second में चलाते हैं (in-memory `mongod` start, 2 tests चलते, वह बंद)। हर PR पर GitHub Actions वही tests production से मेल खाते pinned MongoDB 8.0 पर चलाता है, और nightly job production indexes script के साथ service container पर integration tests चलाती है। कोई database share नहीं करता, और गलत index definition production deploy की जगह PR में ही fail हो जाती है।

---

## 💻 Code Example — Basic

Verified on Node 24, mongodb-memory-server 11.3, Mongoose 9, MongoDB 8.0.4 (the first run on a machine without the binary also downloads it; we used `MONGOMS_SYSTEM_BINARY` to reuse the installed one).

```javascript
// src/user.js — Mongoose model with a unique index
const mongoose = require('mongoose');                  // ODM
const schema = new mongoose.Schema({
  email: { type: String, required: true, unique: true }, // unique index -> E11000 on duplicates
  name: String,
});
module.exports = mongoose.models.User || mongoose.model('User', schema); // avoid OverwriteModelError
```

```javascript
// src/app.js — tiny Express API under test
const express = require('express');
const User = require('./user');
const app = express();
app.use(express.json());                               // parse JSON bodies

app.post('/users', async (req, res) => {
  try {
    res.status(201).json(await User.create(req.body)); // insert
  } catch (e) {
    // 11000 = duplicate key; anything else is a validation error here
    res.status(e.code === 11000 ? 409 : 400).json({ error: e.message });
  }
});
app.get('/users', async (req, res) => res.json(await User.find().lean()));
module.exports = app;                                  // export app, do NOT call listen() (supertest handles it)
```

```javascript
// test/users.node.test.js — runs with: node --test
const { test, before, after, afterEach } = require('node:test'); // built-in runner (Node 18+)
const assert = require('node:assert');
const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');
const request = require('supertest');                  // HTTP assertions without opening a real port
const app = require('../src/app');
const User = require('../src/user');

let mongod;                                            // handle to the temporary mongod

before(async () => {
  mongod = await MongoMemoryServer.create();           // start a real mongod on a random port
  await mongoose.connect(mongod.getUri());             // e.g. mongodb://127.0.0.1:52345/
  await User.init();                                   // WAIT for the unique index to be built before testing it
});

afterEach(async () => {
  await User.deleteMany({});                           // isolate tests: every test starts with an empty collection
});

after(async () => {
  await mongoose.disconnect();                         // close pool first
  await mongod.stop();                                 // kill mongod and remove its temp data dir
});

test('creates a user', async () => {
  const res = await request(app).post('/users').send({ email: 'a@x.com', name: 'Asha' });
  assert.strictEqual(res.status, 201);                 // created
  assert.strictEqual(await User.countDocuments(), 1);  // really stored in MongoDB
});

test('duplicate email gives 409', async () => {
  await User.create({ email: 'a@x.com' });             // first insert
  const res = await request(app).post('/users').send({ email: 'a@x.com' }); // second insert, same email
  assert.strictEqual(res.status, 409);                 // real E11000 from the real unique index
});
```

```
$ node --test test/users.node.test.js
✔ creates a user (1230ms)                              # timing varies
✔ duplicate email gives 409 (6ms)
ℹ tests 2   ℹ pass 2   ℹ fail 0
```

## 💻 Code Example — Advanced

```javascript
// test/setup-replset.js — replica set in memory: needed for transactions & change streams
const { MongoMemoryReplSet } = require('mongodb-memory-server');
const mongoose = require('mongoose');

let replSet;
exports.start = async () => {
  replSet = await MongoMemoryReplSet.create({
    replSet: { count: 1, storageEngine: 'wiredTiger' }, // one-node replica set is enough for transactions
    binary: { version: '8.0.4' },                       // pin to production's version
  });
  await mongoose.connect(replSet.getUri());             // URI already contains ?replicaSet=testset
};
exports.stop = async () => { await mongoose.disconnect(); await replSet.stop(); };
```

```javascript
// Jest style (same shape; common in teams). Note the 60s hook timeout:
// the first start can download the binary and Jest's default hook timeout is only 5 s.
beforeAll(async () => {
  mongod = await MongoMemoryServer.create();
  await mongoose.connect(mongod.getUri());
  await User.init();
}, 60000);
```
Note: in our test machine Jest 30 + Mongoose 9 + driver 7 failed at `mongoose.connect` with `Missing required sub-document 'driver' in the client metadata document`, an environment/version mismatch inside Jest's sandbox, while the identical test passed with `node --test`. We did not get Jest green, so treat the Jest snippet as unverified and pin compatible versions (or use the built-in runner / Vitest).

```yaml
# .github/workflows/test.yml — syntax-checked only (not run here)
name: test
on: [push, pull_request]
jobs:
  unit:                                                  # option A: mongodb-memory-server (no service needed)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - uses: actions/cache@v4                           # cache the downloaded mongod binary
        with:
          path: ~/.cache/mongodb-binaries
          key: mongodb-binaries-8.0.4
      - run: npm ci
      - run: npm test
        env:
          MONGOMS_VERSION: 8.0.4                         # pin the version
  integration:                                           # option B: real MongoDB service container
    runs-on: ubuntu-latest
    services:
      mongo:
        image: mongo:8.0
        ports: ['27017:27017']
        options: >-
          --health-cmd "mongosh --quiet --eval 'db.runCommand({ping:1})'"
          --health-interval 5s --health-timeout 5s --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run test:integration
        env:
          MONGO_URI: mongodb://localhost:27017/ci_test   # tests use a throw-away database name
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Pattern: build the app in a factory so the test injects the in-memory URI.
// server.js (production)  ->  connect(process.env.MONGO_URI) then app.listen()
// tests                   ->  connect(mongod.getUri()) and use supertest, no listen()
const mongoose = require('mongoose');
const buildApp = require('./src/app');                  // returns an express app, no side effects

async function startServer() {
  await mongoose.connect(process.env.MONGO_URI);        // real URI in production, memory-server URI in tests
  buildApp().listen(3000);
}
if (require.main === module) startServer();             // only auto-start when run directly (node server.js)
module.exports = { buildApp };                          // tests import buildApp()
```

Key rule: never hard-code the connection string inside the model or route files; read it in one place so tests can swap it.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not waiting for index creation
```javascript
// Wrong — the unique index may not exist yet, the duplicate test passes/fails randomly
await mongoose.connect(uri);
// ... test inserts duplicate email immediately

// Right — wait for autoIndex to finish
await mongoose.connect(uri);
await User.init();           // resolves when the model's indexes are built (or syncIndexes())
```

❌ Mistake 2: Sharing data between tests
```javascript
// Wrong — test 2 depends on documents created by test 1 (breaks when run alone or in parallel)
// Right — clean in afterEach, or give each test file its own MongoMemoryServer
afterEach(async () => { await User.deleteMany({}); });
```

❌ Mistake 3: Starting a new server per test (slow) or never stopping it (leaked processes, CI hangs)
✅ Correct: one server per test file (`beforeAll`/`before`), clean collections per test, always `stop()` in `afterAll`. Run Jest with `--detectOpenHandles` if the process will not exit.

❌ Mistake 4: Testing transactions on a standalone memory server
✅ Correct: transactions and change streams need a replica set; use `MongoMemoryReplSet`, otherwise you get "Transaction numbers are only allowed on a replica set member or mongos".

❌ Mistake 5: Different version in tests than in production
✅ Correct: pin `MONGOMS_VERSION` (or the Docker tag) to production's major version; otherwise features like `$setWindowFields` or new operators pass or fail differently.

---

## 🧠 Tricky Interview Question

"Your tests pass locally with `mongodb-memory-server`, but in CI the test job fails with a timeout in `beforeAll`. Production is MongoDB Atlas 7. What are the likely causes?"

Answer: (1) The first run downloads the `mongod` binary (100+ MB) inside the hook, exceeding the test framework's default timeout (Jest: 5 s); fix by caching the binary, pre-downloading in a `postinstall` step, and raising the hook timeout. (2) The CI image lacks libraries the downloaded binary needs (e.g. `libcurl`/OpenSSL on minimal Alpine/Debian images) or has no outbound internet; fix by using a supported base image, `MONGOMS_SYSTEM_BINARY`, or a service container. (3) Version drift: default `mongodb-memory-server` version may differ from Atlas 7, so pin `MONGOMS_VERSION=7.0.x`. We reproduced cause (1) on our machine: the hook exceeded 5 s until a 60 s timeout was set. An in-memory `mongod` is real MongoDB, not Atlas, so Atlas-only features (Atlas Search, Vector Search) cannot be tested this way.

---

## ⚫ Interview Questions + Answers

Q1: Why not just mock the MongoDB driver in unit tests?
A1: Mocks verify only that your code calls certain methods, not that queries are correct. They cannot catch wrong operators, missing indexes, unique-constraint behaviour or schema validation. Use mocks for pure business logic, and a real (in-memory/containerized) MongoDB for repository and API tests.

Q2: `mongodb-memory-server` vs Docker service container vs Testcontainers?
A2: `mongodb-memory-server` needs only npm, starts in ~1-2 s and gives per-test-file isolation, but downloads a binary and is Node-only. A CI service container is language-agnostic and matches production images exactly, but is one shared instance per job (use separate database names). Testcontainers starts a Docker container per test suite from code (any language), isolated but needs Docker available and is slower to start.

Q3: How do you test transactions or change streams?
A3: Use `MongoMemoryReplSet` (a one-node replica set) or a container started with `--replSet`. A standalone `mongod` rejects transactions and change streams.

Q4: How do you keep tests fast as the suite grows?
A4: One server per test file (or per worker, via a global setup), clear collections instead of dropping the database, avoid recreating indexes (build once in setup), run files in parallel since each has its own port, and keep the binary cached.

Q5: What should CI never do with MongoDB?
A5: Never connect tests to production or a shared staging database, never put real credentials in test configs or logs, and never leave the test database around: use unique throw-away database names and tear them down. For security tests also run with auth enabled to mimic production.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want fast, zero-setup repository/API tests that run identically on laptops and CI
- You need to test unique indexes, aggregations, validation and error codes for real
- Many parallel test files need isolation (each gets a random port)

❌ Avoid when:
- You must test Atlas-only features (Atlas Search, Vector Search), sharded behaviour or real network/auth topology; use an Atlas test cluster or a full container setup
- CI has no internet and no cached binary and you cannot install `mongod` (use a service container)
- The tests are pure logic with no database access (plain unit tests are faster)

---

## 📊 Visual Diagram
```
MONGODB IN CI/CD
──────────────────────────────────────────────────────────
 git push / PR
     │
     ▼
 CI job (GitHub Actions)
     │
     ├── A) npm test ─► MongoMemoryServer.create()
     │                       │  spawns real mongod (random port, temp dir)
     │                       ▼
     │                  tests ◄──► mongodb://127.0.0.1:RANDOM
     │                       │
     │                  stop() -> process killed, temp dir deleted
     │
     ├── B) services: mongo:8.0 (Docker container, health-checked)
     │        tests ◄──► mongodb://localhost:27017/ci_test
     │
     └── C) Testcontainers: code starts/stops a container per suite

 Cache binary: ~/.cache/mongodb-binaries   Pin version: MONGOMS_VERSION
 Transactions? -> MongoMemoryReplSet (one-node replica set)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mongodb-memory-server | npm package that runs a temporary real mongod | अस्थायी असली mongod चलाने वाला npm package |
| MongoMemoryReplSet | In-memory replica set for transactions | Transactions के लिए in-memory replica set |
| Service container | Docker container started beside a CI job | CI job के साथ चलने वाला Docker container |
| Testcontainers | Library starting containers from test code | Test code से containers चलाने वाली library |
| MONGOMS_VERSION | Env var pinning the mongod version | mongod version तय करने वाला env var |
| Test isolation | Each test sees clean, independent data | हर test को साफ, स्वतंत्र data |
| Health check | Probe to wait until DB is ready | DB तैयार होने तक इंतज़ार की जाँच |

---

## ⚡ 3-Line Summary
English:
1. Test against a real, disposable MongoDB (`mongodb-memory-server`, CI service container or Testcontainers), not mocks.
2. Start one server per test file, `await Model.init()` before index tests, clean data in `afterEach`, always `stop()` in `afterAll`.
3. In CI cache the binary, pin the MongoDB version to production, and use a replica-set variant for transactions.

Hindi:
1. Mocks की जगह असली, disposable MongoDB पर test करो (`mongodb-memory-server`, CI service container या Testcontainers)।
2. हर test file के लिए एक server चलाओ, index tests से पहले `await Model.init()`, `afterEach` में data साफ करो, `afterAll` में हमेशा `stop()`।
3. CI में binary cache करो, MongoDB version को production से मिलाकर pin करो, और transactions के लिए replica-set variant इस्तेमाल करो।

---

## ➡️ Next Topic
**114. GDPR, Data Retention and TTL Strategy** — how to keep, expire and erase personal data in MongoDB.
