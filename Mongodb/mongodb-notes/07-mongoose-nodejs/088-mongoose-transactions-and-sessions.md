# 88. Mongoose Transactions and Sessions
# हिंदी में: Mongoose Transactions और Sessions

---

## 🔵 Simple Definition (English)
A **transaction** groups several read/write operations (possibly across collections) into one all-or-nothing unit: either every change is committed or all are rolled back. In Mongoose you open a **session** (`mongoose.startSession()`), run the work inside `session.withTransaction(async () => { ... })`, and **pass `{ session }` to every operation**. Transactions require a **replica set or sharded cluster** (MongoDB 4.0+ for replica sets); they do not work on a standalone `mongod`.

## 🔵 सरल परिभाषा (Hindi)
**Transaction** कई read/write operations को (कई collections में भी) एक all-or-nothing इकाई में बाँधता है: या तो हर बदलाव commit होता है या सब rollback। Mongoose में आप **session** खोलते हैं (`mongoose.startSession()`), काम `session.withTransaction(async () => { ... })` के अंदर चलाते हैं, और **हर operation को `{ session }` पास करते हैं**। Transactions के लिए **replica set या sharded cluster** चाहिए (replica sets के लिए MongoDB 4.0+); standalone `mongod` पर ये नहीं चलते।

---

## 🔴 Problem it Solves
A single-document update in MongoDB is already atomic. But a money transfer touches two accounts and writes a ledger entry: three documents. If the app crashes after debiting account A but before crediting B, money vanishes. Transactions guarantee ACID across those documents: other clients never see the half-done state, and a failure rolls everything back.

## 🔴 यह क्यों बना? (Hindi)
MongoDB में single-document update पहले से atomic है। पर पैसे का transfer दो accounts छूता है और एक ledger entry लिखता है: तीन documents। App A से debit करने के बाद B में credit से पहले crash हो जाए तो पैसा गायब हो जाता है। Transactions इन documents पर ACID की गारंटी देते हैं: दूसरे clients को अधूरी state कभी नहीं दिखती, और failure पर सब rollback हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Run MongoDB as a replica set (even a single-node `--replSet rs0` + `rs.initiate()` for dev). This lab ran exactly that.
Step 2 → `const session = await mongoose.startSession()`.
Step 3 → `await session.withTransaction(async () => { ... })`. It starts a transaction, runs your callback, **commits**, and automatically **retries** the callback on transient errors (`TransientTransactionError`) and the commit on `UnknownTransactionCommitResult`.
Step 4 → Inside, **every** operation must receive the session: `Model.updateOne(filter, update, { session })`, `Model.create([doc], { session })` (note the **array** form for `create` with options), `query.session(session)`, `doc.save({ session })`.
Step 5 → To abort and roll back, **throw** inside the callback. `withTransaction` aborts, and rethrows your error.
Step 6 → Always `await session.endSession()` in a `finally`.
Step 7 → Shortcut: `mongoose.connection.transaction(async (session) => { ... })` does start/commit/abort/endSession for you (Mongoose also resets documents' state if the transaction aborts).
Step 8 → Collections must **exist before** the transaction in older servers (create them first with `Model.createCollection()`); since 4.4 implicit creation inside a transaction is allowed, but pre-creating is a safe habit.
Step 9 → Keep transactions **short** (default `transactionLifetimeLimitSeconds` is 60) and avoid long network calls inside.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → MongoDB को replica set की तरह चलाओ (dev में single-node `--replSet rs0` + `rs.initiate()` भी चलता है)। यह lab बिल्कुल ऐसे ही चला।
Step 2 → `const session = await mongoose.startSession()`।
Step 3 → `await session.withTransaction(async () => { ... })`। यह transaction शुरू करता है, आपका callback चलाता है, **commit** करता है, और transient errors (`TransientTransactionError`) पर callback तथा `UnknownTransactionCommitResult` पर commit को अपने आप **retry** करता है।
Step 4 → अंदर **हर** operation को session मिलना चाहिए: `Model.updateOne(filter, update, { session })`, `Model.create([doc], { session })` (options के साथ `create` का **array** रूप), `query.session(session)`, `doc.save({ session })`।
Step 5 → रोकने और rollback के लिए callback के अंदर **throw** करो। `withTransaction` abort करता है और आपकी error दोबारा throw करता है।
Step 6 → `finally` में हमेशा `await session.endSession()`।
Step 7 → Shortcut: `mongoose.connection.transaction(async (session) => { ... })` start/commit/abort/endSession खुद कर देता है (transaction abort होने पर Mongoose documents की state भी reset करता है)।
Step 8 → पुराने servers में transaction से **पहले** collections मौजूद होनी चाहिए (`Model.createCollection()` से बनाओ); 4.4 से transaction के अंदर implicit creation allowed है, फिर भी पहले बनाना सुरक्षित आदत है।
Step 9 → Transactions **छोटे** रखो (default `transactionLifetimeLimitSeconds` 60 है) और अंदर लंबे network calls मत करो।

---

## 🟡 Real World Example
**Razorpay / PhonePe style wallet transfer**: debit Aman's wallet by Rs 300, credit Priya's wallet by Rs 300, insert a `Txn` ledger row. If the debit fails because Aman has only Rs 100, the conditional update (`balance: { $gte: 300 }`) matches nothing, the callback throws "Insufficient funds", and the transaction aborts: no credit, no ledger entry. During peak load, MongoDB may abort a transaction due to a write conflict; `withTransaction` simply re-runs the callback, so your code must be **idempotent inside the callback**.

## 🟡 Real Example Hindi mein
**Razorpay / PhonePe जैसा wallet transfer**: Aman के wallet से Rs 300 debit, Priya के wallet में Rs 300 credit, और `Txn` ledger row insert। Aman के पास सिर्फ Rs 100 हों तो conditional update (`balance: { $gte: 300 }`) कुछ match नहीं करता, callback "Insufficient funds" throw करता है और transaction abort हो जाता है: न credit, न ledger entry। Peak load में write conflict की वजह से MongoDB transaction abort कर सकता है; `withTransaction` callback को दोबारा चला देता है, इसलिए आपका callback के अंदर का code **idempotent** होना चाहिए।

---

## 💻 Code Example — Basic

```javascript
// txn-basic.js — real output. Requires a replica set (this lab: single-node rs0 on MongoDB 8.0.4)
const mongoose = require('mongoose'); const { Schema } = mongoose;

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  await mongoose.connection.dropDatabase();

  const Acc = mongoose.model('Account', new Schema({ name: String, balance: Number }));
  const Txn = mongoose.model('Txn', new Schema({ from: String, to: String, amt: Number }));
  await Acc.createCollection(); await Txn.createCollection();       // pre-create collections (safe habit)
  await Acc.create([{ name: 'A', balance: 1000 }, { name: 'B', balance: 0 }]);

  async function transfer(from, to, amt) {
    const session = await mongoose.startSession();                  // 1) open a session
    try {
      await session.withTransaction(async () => {                   // 2) start txn, auto-commit, auto-retry
        // conditional debit: matches only if enough balance, otherwise returns null
        const f = await Acc.findOneAndUpdate(
          { name: from, balance: { $gte: amt } },
          { $inc: { balance: -amt } },
          { session, returnDocument: 'after' });                    // 3) PASS THE SESSION
        if (!f) throw new Error('Insufficient funds');              // 4) throw => abort + rollback
        await Acc.updateOne({ name: to }, { $inc: { balance: amt } }, { session });
        await Txn.create([{ from, to, amt }], { session });         // array form when passing options
      });
      return 'ok';
    } finally {
      await session.endSession();                                   // 5) always release the session
    }
  }

  console.log(await transfer('A', 'B', 300));
  // Output: ok

  try { await transfer('A', 'B', 5000); } catch (e) { console.log('rolled back:', e.message); }
  // Output: rolled back: Insufficient funds

  console.log((await Acc.find().sort('name').lean()).map(a => a.name + '=' + a.balance).join(' '),
              '| txns:', await Txn.countDocuments());
  // Output: A=700 B=300 | txns: 1        (the failed transfer left nothing behind)
  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// txn-advanced.js — the forgotten-session bug, document saves, and the connection.transaction() helper
const mongoose = require('mongoose');
(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const Acc = mongoose.model('Account');               // from the Basic example (A=700, B=300)
  const show = async () => (await Acc.find().sort('name').lean()).map(a => a.name + '=' + a.balance).join(' ');

  // 1) THE CLASSIC BUG: one operation forgets { session } => it runs OUTSIDE the transaction
  const s = await mongoose.startSession(); s.startTransaction();
  await Acc.updateOne({ name: 'A' }, { $inc: { balance: -100 } }, { session: s }); // inside txn
  await Acc.updateOne({ name: 'B' }, { $inc: { balance: 100 } });                  // forgot session!
  await s.abortTransaction(); await s.endSession();                                // rolls back only A
  console.log(await show());
  // Output: A=700 B=400      <- B kept the +100 although the transaction aborted: money was created!

  // 2) Documents loaded in a session remember it: doc.save() uses the session automatically
  const s2 = await mongoose.startSession();
  await s2.withTransaction(async () => {
    const a = await Acc.findOne({ name: 'A' }).session(s2);   // .session() on the query
    a.balance += 1;
    await a.save();                                            // saved inside the same transaction
  });
  await s2.endSession();

  // 3) Helper: connection.transaction() = start + commit/abort + endSession in one call
  await mongoose.connection.transaction(async (session) => {
    await Acc.updateOne({ name: 'A' }, { $inc: { balance: 1 } }, { session });
  });
  console.log((await Acc.findOne({ name: 'A' })).balance);
  // Output: 702      (700 + 1 from save() + 1 from the helper)

  // 4) Transaction options: stronger guarantees (use when needed; costs latency)
  // await session.withTransaction(fn, { readConcern: { level: 'snapshot' }, writeConcern: { w: 'majority' } });
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Product, Order } = require('./models');

const app = express();
app.use(express.json());

// Place an order: reserve stock for every item AND create the order atomically
app.post('/api/orders', async (req, res) => {
  const { userId, items } = req.body;                       // [{ productId, qty }]
  let created;
  try {
    // connection.transaction handles session lifecycle; it retries on transient errors
    await mongoose.connection.transaction(async (session) => {
      const lines = [];                                      // reset on every retry attempt!
      for (const it of items) {
        const p = await Product.findOneAndUpdate(
          { _id: it.productId, stock: { $gte: it.qty } },
          { $inc: { stock: -it.qty } },
          { session, returnDocument: 'after' });
        if (!p) throw Object.assign(new Error(`Out of stock: ${it.productId}`), { status: 409 });
        lines.push({ productId: p._id, name: p.name, priceAtPurchase: p.price, qty: it.qty });
      }
      const total = lines.reduce((s, l) => s + l.priceAtPurchase * l.qty, 0);
      [created] = await Order.create([{ userId, items: lines, total }], { session });
    });
    res.status(201).json(created);                           // respond only AFTER commit
  } catch (err) {
    res.status(err.status || 500).json({ error: err.message });  // stock decrements were rolled back
  }
});
// In production keep the callback free of side effects (emails, HTTP calls) — it can run more than once.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to pass the session to one operation
```javascript
// Wrong — runs outside the transaction and is NOT rolled back (verified: B kept +100)
await Acc.updateOne({ name: 'B' }, { $inc: { balance: 100 } });

// Right
await Acc.updateOne({ name: 'B' }, { $inc: { balance: 100 } }, { session });
```

❌ Mistake 2: Using transactions on a standalone mongod
```javascript
// Wrong — error: "Transaction numbers are only allowed on a replica set member or mongos"
// Right — run mongod with --replSet and rs.initiate(); Atlas clusters are replica sets already
```

❌ Mistake 3: Side effects or non-idempotent code in the callback
✅ Correct: `withTransaction` may run the callback multiple times. Do not send emails, charge cards, or push to outer arrays without resetting them. Do side effects after the commit.

---

## 🧠 Tricky Interview Question

**Q:** Do you need a transaction for "decrement stock and create order" if both are in the same document?

**Answer:** No. Operations on a **single document** are atomic in MongoDB, even if they modify many fields and nested arrays. That is why good schema design (embedding things that change together) often removes the need for transactions. Transactions are for changes that must be atomic across **multiple documents or collections**, such as moving money between two accounts. They cost more (locks, snapshots, retry logic, a 60-second default lifetime), so use them where embedding or conditional atomic updates cannot give the guarantee.

---

## ⚫ Interview Questions + Answers

Q1: What do I need to run transactions locally?
A1: A replica set. For dev: `mongod --replSet rs0` then `rs.initiate()` (a one-node replica set is fine), and connect with `?replicaSet=rs0`. Standalone servers reject transactions.

Q2: Difference between `session.withTransaction()` and manual `startTransaction/commitTransaction`?
A2: `withTransaction` wraps the callback and handles retry of transient errors and unknown commit results automatically. Manual control needs you to implement those retries and call `commitTransaction`/`abortTransaction` yourself.

Q3: How do you roll back?
A3: Throw inside the `withTransaction` callback (or call `abortTransaction()` in manual mode). All changes made with that session are discarded; changes made without it are not.

Q4: What are write conflicts?
A4: Two concurrent transactions modify the same document; the second gets a `WriteConflict` (a TransientTransactionError) and is retried by `withTransaction`. Keep transactions short and touch few documents to reduce conflicts.

Q5: Are there alternatives to transactions?
A5: Yes: embed related data in one document, use conditional atomic updates (`{ stock: { $gte: n } }` with `$inc`), the saga/outbox pattern with idempotent steps, or two-phase-commit-like status fields. These scale better in distributed systems.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A business operation must change several documents/collections atomically (transfers, order + stock + ledger)
- You need a consistent snapshot read across collections

❌ Avoid when:
- Single-document changes (already atomic)
- High-throughput hot-path writes that could be redesigned with embedding or atomic operators
- Long-running work, external calls or user interaction inside the transaction

---

## 📊 Visual Diagram
```
TRANSFER Rs 300  A → B
──────────────────────────────────────────────────────
 session.withTransaction(async () => {
    ┌─ findOneAndUpdate A {balance>=300} -300  {session}
    │   └─ null? → throw "Insufficient funds" ──► ABORT (nothing visible)
    ├─ updateOne B +300                        {session}
    └─ Txn.create([...])                       {session}
 })                                   │
                    all OK ───────────┴──► COMMIT (all 3 changes become visible together)

 transient error / write conflict ──► callback re-run automatically (be idempotent!)
 missing {session} on any call ──► that call is OUTSIDE the transaction (not rolled back)
 requires: replica set / sharded cluster
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transaction | All-or-nothing group of operations | All-or-nothing operations का समूह |
| Session | Context that carries a transaction | Transaction ले जाने वाला context |
| `withTransaction` | Helper with auto-retry and commit | Auto-retry और commit वाला helper |
| Rollback / abort | Discard all changes | सारे बदलाव रद्द करना |
| Write conflict | Two txns touch one document | दो transactions एक document छूते हैं |
| Replica set | Group of mongod nodes | mongod nodes का समूह |
| Idempotent | Safe to repeat | दोहराने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
English:
1. Transactions need a replica set; open a session and use `withTransaction` (or `connection.transaction`) so commit and retries are handled.
2. Pass `{ session }` to every operation, because one forgotten call runs outside the transaction and is never rolled back.
3. Keep them short and idempotent, and prefer embedding or atomic updates when a single document is enough.

Hindi:
1. Transactions के लिए replica set चाहिए; session खोलो और `withTransaction` (या `connection.transaction`) इस्तेमाल करो ताकि commit और retries सँभल जाएँ।
2. हर operation को `{ session }` दो, क्योंकि एक भी भूली call transaction के बाहर चलती है और कभी rollback नहीं होती।
3. उन्हें छोटा और idempotent रखो, और एक document काफी हो तो embedding या atomic updates को प्राथमिकता दो।

---

## ➡️ Next Topic
**89. Mongoose Indexes and Performance** — defining indexes in schemas, reading `explain()` and avoiding common slow-query traps.
