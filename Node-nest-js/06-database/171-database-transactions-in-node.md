# 171. Database Transactions in Node
# हिंदी में: Database Transactions — Multiple Operations को Atomic बनाना

---

## 🔵 Simple Definition (English)
A **database transaction** groups multiple read/write operations into one all-or-nothing unit. Either ALL operations succeed and get **committed**, or if any one fails, ALL changes are **rolled back** — the database returns to its state before the transaction started. Transactions guarantee **ACID** properties (Atomicity, Consistency, Isolation, Durability).

## 🔵 सरल परिभाषा (Hindi)
**Database transaction** multiple read/write operations को एक all-or-nothing unit में group करता है। या तो सारे operations succeed होकर **commit** होते हैं, या अगर कोई एक भी fail हो तो सारे changes **rollback** हो जाते हैं — database transaction शुरू होने से पहले वाली state में वापस आ जाता है। Transactions **ACID** properties guarantee करते हैं (Atomicity, Consistency, Isolation, Durability)।

---

## 🔴 Problem it Solves
Imagine Paytm's wallet transfer: deduct ₹500 from User A, add ₹500 to User B. These are TWO separate database writes. Without a transaction:
```
Step 1: Deduct ₹500 from A → SUCCESS
Step 2: Add ₹500 to B → Server crashes / DB error!
Result: A lost ₹500, B never got it. Money disappeared!
```
With a transaction, if step 2 fails, step 1 is automatically undone — A keeps their ₹500. This "all or nothing" guarantee is critical anywhere money, inventory, or any multi-step state change is involved.

## 🔴 यह क्यों बना? (Hindi)
Paytm wallet transfer का उदाहरण लो: User A से ₹500 deduct करना, User B को ₹500 add करना। ये TWO अलग database writes हैं। Transaction के बिना:
```
Step 1: A से ₹500 deduct → SUCCESS
Step 2: B को ₹500 add → Server crash / DB error!
Result: A का ₹500 गया, B को मिला ही नहीं। पैसा गायब!
```
Transaction के साथ, अगर step 2 fail हो, step 1 automatically undo हो जाता है — A के पास अभी भी ₹500 रहते हैं। यह "all or nothing" guarantee पैसे, inventory, या किसी भी multi-step state change में critical है।

---

## 🟢 How it Works — Step by Step

Step 1 → Start a transaction / session (`BEGIN` in SQL, `session.startTransaction()` in Mongoose).
Step 2 → Perform multiple operations using the SAME session/connection — none are permanently visible to other queries yet.
Step 3 → If all operations succeed → **COMMIT** — changes become permanent and visible to everyone.
Step 4 → If ANY operation throws an error → **ROLLBACK** — undo everything done since `BEGIN`.
Step 5 → Always release/end the session in a `finally` block to free resources.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Transaction/session शुरू करो (SQL में `BEGIN`, Mongoose में `session.startTransaction()`)।
Step 2 → SAME session/connection से multiple operations perform करो — अभी तक किसी और query को permanently visible नहीं।
Step 3 → अगर सारे operations succeed → **COMMIT** — changes permanent और सबको visible हो जाते हैं।
Step 4 → अगर कोई operation error throw करे → **ROLLBACK** — `BEGIN` से अब तक के सारे changes undo।
Step 5 → `finally` block में session को हमेशा release/end करो।

---

## 🟡 Real World Example
**Flipkart order placement:** Placing an order requires: (1) deduct stock from `inventory`, (2) create a row in `orders`, (3) deduct balance from `wallet` if paying via wallet, (4) create a `payment` record. If stock deduction succeeds but payment fails (e.g., insufficient wallet balance detected mid-flow), without a transaction the inventory would be wrongly reduced with no order ever completing — causing phantom stock shortages. With a transaction wrapping all 4 steps, any failure rolls everything back, keeping inventory and order data consistent.

## 🟡 Real Example Hindi mein
**Flipkart order placement:** Order place करने के लिए चाहिए: (1) `inventory` से stock deduct, (2) `orders` में row create, (3) wallet से payment हो तो balance deduct, (4) `payment` record create। अगर stock deduction succeed हो पर payment fail हो जाये (जैसे बीच में insufficient wallet balance पता चले), transaction के बिना inventory गलत तरीके से कम हो जायेगी बिना कोई order complete हुए — phantom stock shortage बनेगी। Transaction के साथ, 4 steps में से कोई fail हो तो सब rollback, inventory और order data consistent रहता है।

---

## 💻 Code Example — Basic

```javascript
// basic-transaction-mongoose.js
// Install: npm install mongoose (requires MongoDB replica set for transactions)

const mongoose = require('mongoose');

const Wallet = mongoose.model('Wallet', new mongoose.Schema({
  userId: String, balance: Number,
}));

async function transferMoney(fromUserId, toUserId, amount) {
  const session = await mongoose.startSession(); // start a session
  try {
    session.startTransaction(); // begin transaction on this session

    // Deduct from sender — pass { session } so this write is part of the transaction
    const sender = await Wallet.findOne({ userId: fromUserId }).session(session);
    if (sender.balance < amount) {
      throw new Error('Insufficient balance'); // triggers rollback below
    }
    sender.balance -= amount;
    await sender.save({ session });

    // Add to receiver — also part of the SAME transaction
    const receiver = await Wallet.findOne({ userId: toUserId }).session(session);
    receiver.balance += amount;
    await receiver.save({ session });

    await session.commitTransaction(); // all good -> make changes permanent
    console.log('Transfer successful');
  } catch (err) {
    await session.abortTransaction(); // something failed -> undo everything
    console.error('Transfer failed, rolled back:', err.message);
    throw err;
  } finally {
    session.endSession(); // always release the session
  }
}

module.exports = { transferMoney };
```

## 💻 Code Example — Advanced

```javascript
// advanced-transaction-sql.js — PostgreSQL with 'pg' pool, production patterns

const { Pool } = require('pg'); // npm install pg
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function placeOrder({ userId, items, paymentMethod }) {
  const client = await pool.connect(); // get a dedicated connection from the pool
  try {
    await client.query('BEGIN'); // start transaction

    let totalAmount = 0;
    for (const item of items) {
      // Lock the row with FOR UPDATE to prevent concurrent overselling
      const { rows } = await client.query(
        'SELECT stock, price FROM products WHERE id = $1 FOR UPDATE',
        [item.productId]
      );
      if (!rows.length || rows[0].stock < item.qty) {
        throw new Error(`Insufficient stock for product ${item.productId}`);
      }
      totalAmount += rows[0].price * item.qty;

      // Deduct stock
      await client.query(
        'UPDATE products SET stock = stock - $1 WHERE id = $2',
        [item.qty, item.productId]
      );
    }

    // Create order row
    const orderResult = await client.query(
      'INSERT INTO orders (user_id, total, status) VALUES ($1, $2, $3) RETURNING id',
      [userId, totalAmount, 'PLACED']
    );
    const orderId = orderResult.rows[0].id;

    // Deduct wallet balance if paying by wallet
    if (paymentMethod === 'WALLET') {
      const walletResult = await client.query(
        'UPDATE wallets SET balance = balance - $1 WHERE user_id = $2 AND balance >= $1 RETURNING balance',
        [totalAmount, userId]
      );
      if (walletResult.rowCount === 0) {
        throw new Error('Insufficient wallet balance'); // rolls back stock deduction too
      }
    }

    await client.query('COMMIT'); // all steps succeeded -> persist everything
    return { orderId, totalAmount };
  } catch (err) {
    await client.query('ROLLBACK'); // any failure -> undo stock + order + wallet changes
    console.error('Order placement failed:', err.message);
    throw err;
  } finally {
    client.release(); // return connection to the pool (critical! prevents pool exhaustion)
  }
}

module.exports = { placeOrder };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();
app.use(express.json());

app.post('/orders', async (req, res) => {
  try {
    const result = await placeOrder({
      userId: req.body.userId,
      items: req.body.items,
      paymentMethod: req.body.paymentMethod,
    });
    res.status(201).json({ success: true, order: result });
  } catch (err) {
    // Transaction already rolled back inside placeOrder; just respond with an error
    res.status(400).json({ success: false, error: err.message });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to pass `{ session }` / using the shared connection consistently
✅ Correct: Every query inside the transaction MUST use the same session/client, otherwise it runs outside the transaction and won't roll back.

```javascript
// Wrong — uses default connection, not the transaction's session
await Wallet.findOne({ userId }).save();

// Right
await Wallet.findOne({ userId }).session(session).save({ session });
```

❌ Mistake 2: Not releasing the connection/session in `finally`
✅ Correct: Always call `client.release()` / `session.endSession()` in `finally`, even on error — otherwise connections leak and the pool exhausts under load.

```javascript
// Wrong
const client = await pool.connect();
await client.query('BEGIN');
// ...no release on error path -> connection leak

// Right
try { /* ... */ } finally { client.release(); }
```

---

## 🧠 Tricky Interview Question

```javascript
// Inside a transaction, you SELECT a row, then UPDATE it based on the value read.
// Another request runs the SAME operation concurrently, on the same row.
// Without any locking, what can go wrong?
```
Answer: This is a **race condition** known as "lost update." Both transactions read the SAME initial value (e.g., stock = 5), both compute a deduction (e.g., -1), and both write back stock = 4 — even though 2 units should have been deducted, leaving stock = 3. The fix: use row-level locking (`SELECT ... FOR UPDATE` in SQL) so the second transaction BLOCKS until the first commits, or use atomic conditional updates (`UPDATE products SET stock = stock - 1 WHERE stock >= 1`) that let the database do the read-check-write atomically.

---

## ⚫ Interview Questions + Answers

Q1: What does ACID stand for?
A1: **Atomicity** — all operations succeed or none do. **Consistency** — the database moves from one valid state to another, respecting constraints. **Isolation** — concurrent transactions don't interfere with each other's intermediate states. **Durability** — once committed, changes survive crashes/restarts (written to disk/WAL).

Q2: Does MongoDB support transactions, and what's required?
A2: Yes, since MongoDB 4.0 for replica sets (and 4.2 for sharded clusters). A standalone MongoDB instance does NOT support multi-document transactions — it requires a replica set (even a single-node one for dev) because transactions rely on the oplog for rollback capability.

Q3: What is an isolation level, and what's the default in PostgreSQL?
A3: Isolation level controls how much one transaction can "see" of another transaction's uncommitted or concurrent changes. Levels (from least to most strict): Read Uncommitted, Read Committed, Repeatable Read, Serializable. PostgreSQL's default is **Read Committed** — each query within a transaction sees only data committed before that query started, preventing dirty reads but allowing some anomalies like non-repeatable reads.

Q4: How do nested transactions / savepoints work?
A4: Most databases don't have true nested transactions, but support **savepoints** — a named point within a transaction you can roll back to without aborting the whole transaction. E.g., `SAVEPOINT sp1; ... ROLLBACK TO sp1;` lets you undo part of a transaction while keeping earlier work intact, useful for complex multi-step flows with partial recovery.

Q5: Why should transactions be kept short?
A5: A long-running transaction holds locks on rows/tables for its entire duration, blocking other transactions from reading/writing those rows (depending on isolation level), which hurts concurrency and throughput. Long transactions also increase the chance of deadlocks and make rollback more expensive. Best practice: fetch data outside the transaction where possible, keep the actual transactional critical section minimal (just the writes that must be atomic).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple writes must succeed/fail together (payments, order placement, inventory updates, wallet transfers).
- Data integrity across related tables/collections is critical.

❌ Avoid when:
- A single simple write/read with no related state changes — unnecessary overhead.
- High-throughput operations where eventual consistency is acceptable (e.g., view counters, analytics logging) — transactions add latency and lock contention.

---

## 📊 Visual Diagram
```
TRANSACTION FLOW:
──────────────────────────────────────────────
BEGIN
  │
  ├─ Deduct ₹500 from Wallet A   ──┐
  │                                 │  all operations use
  ├─ Add ₹500 to Wallet B        ──┤  the SAME session/
  │                                 │  connection
  └─ Create transaction log row  ──┘
  │
  ▼
 All succeeded?
  ├── YES → COMMIT  → changes permanent, visible to everyone
  └── NO  → ROLLBACK → DB reverts to state before BEGIN
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transaction | Group of atomic operations | Atomic operations का group |
| COMMIT | Make changes permanent | Changes permanent करना |
| ROLLBACK | Undo all changes in transaction | सारे changes undo करना |
| ACID | Atomicity, Consistency, Isolation, Durability | चार guarantees |
| Isolation level | How much concurrent txns see each other | Concurrency visibility rule |
| Savepoint | Partial rollback point inside a transaction | Transaction के अंदर rollback point |
| Deadlock | Two txns waiting on each other forever | दो transactions एक-दूसरे का wait |

---

## ⚡ 3-Line Summary
English:
1. Transactions bundle multiple DB operations into an all-or-nothing unit — critical for money, inventory, and multi-step state changes.
2. Always use the same session/connection for every operation in the transaction, and commit or rollback explicitly with proper error handling.
3. Keep transactions short, release connections in `finally`, and use row locking (`FOR UPDATE`) to avoid race conditions like lost updates.

Hindi:
1. Transactions multiple DB operations को all-or-nothing unit में bundle करते हैं — पैसे, inventory, multi-step changes के लिए critical।
2. Transaction के हर operation के लिए same session/connection use करो, और proper error handling से commit या rollback करो।
3. Transactions छोटे रखो, `finally` में connections release करो, और race conditions से बचने के लिए row locking (`FOR UPDATE`) use करो।

---

## ➡️ Next Topic
**172. Database Error Handling** — DB errors को gracefully catch, classify, और handle करना।
