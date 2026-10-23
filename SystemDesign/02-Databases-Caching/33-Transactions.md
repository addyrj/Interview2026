# 33. Transactions
# हिंदी में: Transaction — कई DB operations का एक समूह जो या तो पूरा होगा या बिल्कुल नहीं (सब या कुछ नहीं)

---

## 🔵 Simple Definition (English)
A **transaction** is a group of database operations treated as **one single unit of work**. Either **all** of them succeed (**COMMIT**) or **none** of them take effect (**ROLLBACK**). Transactions also isolate concurrent users from each other's half-finished changes.

## 🔵 सरल परिभाषा (Hindi)
Transaction कई DB कामों को एक इकाई बना देता है — या तो सब पूरे होंगे (COMMIT), या कोई भी नहीं (ROLLBACK)।
जैसे पैसे भेजना: एक खाते से कटना और दूसरे में जुड़ना — दोनों साथ होने चाहिए, आधा नहीं।

---

## 🔴 Problem it Solves
Without transactions:
- **Partial failure:** money is debited from A, then the server crashes before crediting B → money vanishes.
- **Inconsistent reads:** a report reads balances while a transfer is half done → totals don't add up.
- **Race conditions:** two users buy the last item at the same time → both succeed → stock = −1.
- **Error handling hell:** you'd have to manually undo every previous step on failure.

The transaction gives a simple contract: **"treat these steps as one, and protect them from concurrency and crashes."**

## 🔴 यह क्यों बना? (Hindi)
बिना transaction के: A के खाते से पैसे कटे और सर्वर crash — B को पैसे नहीं मिले, पैसे ग़ायब। दो लोग एक साथ आख़िरी सामान ख़रीदें तो stock −1।
Transaction एक सीधा वादा देता है: "ये सारे कदम एक हैं — crash और एक साथ चल रहे यूज़र्स से सुरक्षित।"

---

## 🟢 How it Works — Step by Step

### Basic flow

```
BEGIN;                                              ┌─────────────────────────┐
  UPDATE accounts SET bal = bal - 500 WHERE id = A; │ changes visible only to │
  UPDATE accounts SET bal = bal + 500 WHERE id = B; │ THIS transaction        │
  INSERT INTO transfers(...) VALUES (...);          └─────────────────────────┘
COMMIT;      → all 3 become permanent & visible together
-- or
ROLLBACK;    → as if nothing happened

Crash before COMMIT → on restart, DB discards the incomplete transaction (via WAL)
```

### Inside the DB (simplified)

```
1. BEGIN           → transaction gets an ID / snapshot
2. Each write      → logged to WAL (write-ahead log); new row versions created (MVCC)
                     row locks taken on modified rows
3. COMMIT          → commit record written to WAL and flushed to disk (fsync) → DURABLE
                     locks released; other transactions now see the changes
4. ROLLBACK/crash  → new row versions marked dead; nothing visible
```

### Savepoints (partial rollback)

```sql
BEGIN;
  INSERT INTO orders ... ;
  SAVEPOINT before_coupon;
  UPDATE coupons SET used = used + 1 WHERE code = 'DIWALI' AND used < max_uses;
  -- coupon invalid? undo only that part
  ROLLBACK TO SAVEPOINT before_coupon;
COMMIT;
```

### Concurrency problems transactions prevent (with right isolation — Topic 35)

```
Dirty read          → reading uncommitted data of another transaction
Non-repeatable read → same row read twice gives different values
Phantom read        → same query returns new rows inserted by others
Lost update         → two transactions read-modify-write the same row; one overwrites the other
Write skew          → two transactions each check a condition, then both write (doctor on-call example)
```

### Lost update example & fixes

```
T1: SELECT stock FROM items WHERE id=7;   → 1
T2: SELECT stock FROM items WHERE id=7;   → 1
T1: UPDATE items SET stock = 0 WHERE id=7; COMMIT;    (sold)
T2: UPDATE items SET stock = 0 WHERE id=7; COMMIT;    (sold AGAIN!) ❌

Fix A — atomic conditional update (best, simplest):
  UPDATE items SET stock = stock - 1 WHERE id = 7 AND stock > 0;   -- check affected rows = 1
Fix B — pessimistic lock:
  SELECT stock FROM items WHERE id = 7 FOR UPDATE;   -- T2 waits until T1 commits
Fix C — optimistic lock (version column):
  UPDATE items SET stock = 0, version = version + 1 WHERE id = 7 AND version = 5;  -- 0 rows → retry
Fix D — SERIALIZABLE isolation + retry on serialization failure
```

### Transaction best practices

```
✓ Keep transactions SHORT — no HTTP calls, no user waiting, no file uploads inside
✓ Do slow external calls (payment API, email) OUTSIDE the transaction (use outbox for events)
✓ Always COMMIT or ROLLBACK (use try/finally or framework helpers) — leaked transactions hold locks
✓ Touch rows in a consistent order to avoid deadlocks
✓ Retry on serialization failures / deadlocks (SQLSTATE 40001, 40P01)
✓ Use one connection per transaction (from the pool) — don't mix
✓ Monitor "idle in transaction" sessions
```

### Transactions across services?
```
A DB transaction only covers ONE database.
Order DB + Payment service + Inventory service → no single transaction.
→ Saga pattern (Topic 70), outbox pattern, idempotency (Topic 64). Avoid 2PC (Topic 69).
```

## 🟢 कैसे काम करता है? (Hindi)
1. `BEGIN` से शुरुआत; सारे बदलाव पहले सिर्फ़ इसी transaction को दिखते हैं।
2. हर बदलाव WAL (log) में लिखा जाता है; बदली गई rows पर lock लगता है।
3. `COMMIT` पर log disk पर पक्का होता है — अब बदलाव स्थायी और सबको दिखते हैं।
4. Error या crash पर `ROLLBACK` — जैसे कुछ हुआ ही नहीं।
5. Transaction छोटा रखो, उसके अंदर बाहरी API कॉल मत करो, और race condition के लिए `UPDATE … WHERE stock > 0` या `FOR UPDATE` इस्तेमाल करो।

---

## 🟡 Real World Example

**UPI / bank transfer** — debit, credit and ledger entries are written in a single transaction (or, across banks, a saga with reversal on failure). This is why a failed UPI payment says "money will be refunded in X days": a compensating reversal for the cross-bank case.

**BookMyShow seat booking** — selecting seats locks them (a short reservation with expiry). Final booking marks the seats sold and creates the booking in one transaction, so two people never get the same seat.

**Flash sales (Flipkart/Amazon)** — "only 100 phones at ₹1": stock decrement uses an atomic conditional update or a Redis Lua script so it never oversells, even with 100,000 concurrent requests.

## 🟡 Real Example Hindi में
UPI में पैसे कटना, जुड़ना और ledger entry — एक transaction में; दो बैंकों के बीच फ़ेल हुआ तो reversal होता है, इसलिए "पैसे वापस आ जाएँगे" दिखता है।
BookMyShow में सीट बुकिंग transaction से होती है, ताकि दो लोगों को एक ही सीट न मिले। Flash sale में stock `WHERE stock > 0` से घटता है, ताकि oversell न हो।

---

## 🟠 My Stack Example

### Node.js (pg) — transaction helper with retry
```js
export async function withTx(fn, { retries = 3 } = {}) {
  for (let attempt = 1; ; attempt++) {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      const result = await fn(client);
      await client.query('COMMIT');
      return result;
    } catch (e) {
      await client.query('ROLLBACK').catch(() => {});
      const retryable = ['40001', '40P01'].includes(e.code);   // serialization failure, deadlock
      if (!retryable || attempt >= retries) throw e;
    } finally {
      client.release();
    }
  }
}

// Place order: decrement stock safely + create order atomically
await withTx(async (tx) => {
  const { rowCount } = await tx.query(
    'UPDATE menu_items SET stock = stock - $1 WHERE id = $2 AND stock >= $1', [qty, itemId]);
  if (rowCount === 0) throw new AppError(409, 'OUT_OF_STOCK');
  const { rows: [order] } = await tx.query(
    'INSERT INTO orders(user_id, total, status) VALUES ($1,$2,$3) RETURNING id', [uid, total, 'PLACED']);
  await tx.query('INSERT INTO outbox(topic, payload) VALUES ($1,$2)',
                 ['order.placed', { orderId: order.id }]);       // event in SAME transaction
  return order;
});
// payment API call + notifications happen AFTER commit (via outbox worker)
```

### Prisma
```js
await prisma.$transaction(async (tx) => {
  const item = await tx.menuItem.updateMany({ where: { id: itemId, stock: { gte: qty } },
                                              data: { stock: { decrement: qty } } });
  if (item.count === 0) throw new Error('OUT_OF_STOCK');
  return tx.order.create({ data: { userId, total, status: 'PLACED' } });
}, { isolationLevel: 'ReadCommitted', timeout: 5000 });
```

### FastAPI + SQLAlchemy async
```python
async def place_order(session: AsyncSession, uid: int, item_id: int, qty: int):
    async with session.begin():                       # COMMIT on success, ROLLBACK on exception
        res = await session.execute(
            update(MenuItem).where(MenuItem.id == item_id, MenuItem.stock >= qty)
            .values(stock=MenuItem.stock - qty))
        if res.rowcount == 0:
            raise HTTPException(409, "OUT_OF_STOCK")
        order = Order(user_id=uid, status="PLACED")
        session.add(order)
    return order
```

### Pessimistic lock when you must read-then-decide
```sql
BEGIN;
SELECT balance FROM wallets WHERE user_id = $1 FOR UPDATE;   -- lock the row
-- app checks business rules...
UPDATE wallets SET balance = balance - $2 WHERE user_id = $1;
INSERT INTO wallet_ledger(user_id, amount, type) VALUES ($1, -$2, 'DEBIT');
COMMIT;
```

### MongoDB multi-document transaction
```js
const session = await mongoose.startSession();
await session.withTransaction(async () => {
  await Wallet.updateOne({ userId, balance: { $gte: amt } }, { $inc: { balance: -amt } }, { session });
  await Order.create([{ userId, total: amt }], { session });
});
```

### Anti-pattern
```js
// ❌ external API inside a transaction → locks held for seconds; if API slow, DB pool exhausts
await withTx(async (tx) => {
  await tx.query('UPDATE orders SET status = $1 WHERE id = $2', ['PAYING', id]);
  await razorpay.payments.capture(paymentId, amount);   // 2–5 seconds!
  await tx.query('UPDATE orders SET status = $1 WHERE id = $2', ['PAID', id]);
});
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a database transaction?**
A1: A sequence of operations executed as a single logical unit with ACID guarantees: all succeed and are committed, or all are rolled back. It also isolates concurrent transactions from each other's intermediate state and ensures committed data survives crashes. Typical uses are money transfers, order + stock + payment records, and anything where partial updates would corrupt data.

**Q2: How do you prevent two users from buying the last item at the same time?**
A2: Make the check and the update atomic. Best: `UPDATE items SET stock = stock - 1 WHERE id = ? AND stock > 0` and check that the affected row count is 1. Alternatives: `SELECT ... FOR UPDATE` row locking (pessimistic), optimistic locking with a version column and retry, or SERIALIZABLE isolation with retry. At extreme scale (flash sales), use Redis atomic decrements or Lua scripts plus a queue, and reconcile with the DB.

**Q3: Why shouldn't you call external APIs inside a DB transaction?**
A3: The transaction holds row locks and a DB connection for the entire duration. Slow or hanging external calls block other transactions, exhaust the pool and can cascade into an outage. Also, the external side effect can't be rolled back if the transaction later fails. Commit the local state first (e.g. status=PENDING plus an outbox event), then call the external service, and handle its result in a separate transaction, idempotently.

**Q4: What is a deadlock and how do you handle it?**
A4: Two or more transactions wait for each other's locks in a cycle: T1 locks A then wants B, T2 locks B then wants A. The DB detects it and aborts one, with an error like Postgres 40P01. Prevent it by acquiring locks in a consistent order (sort IDs), keeping transactions short, and indexing foreign keys to reduce lock scope. Handle it by retrying the aborted transaction with backoff.

**Q5: Can you have a transaction across two microservices' databases?**
A5: Not a normal ACID transaction. Two-phase commit exists but is blocking, slow and fragile, and is rarely used in microservices. Use the Saga pattern instead: a sequence of local transactions, each publishing an event, with compensating actions on failure (refund, release stock). Combine it with the transactional outbox and idempotent consumers. Design for eventual consistency between services.

---

## 🔷 Trade-offs
✅ Advantages:
- Correctness under failures and concurrency; simple mental model; easy error handling.

❌ Disadvantages:
- Locks reduce concurrency; long transactions hurt throughput and cause bloat (MVCC).
- Higher isolation levels → more retries/aborts.
- Limited to one database — distributed workflows need sagas.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transaction | All-or-nothing unit of work | सब या कुछ नहीं वाला काम |
| COMMIT | Make changes permanent | बदलाव पक्का करना |
| ROLLBACK | Undo all changes | सारे बदलाव वापस |
| Savepoint | Partial rollback point | बीच का वापसी बिंदु |
| Lost update | One write overwrites another | एक update दूसरे को मिटा दे |
| Pessimistic lock | Lock before change (FOR UPDATE) | पहले ताला, फिर बदलाव |
| Optimistic lock | Check version on update | version जाँचकर बदलाव |
| Deadlock | Transactions waiting on each other | आपस में फँसे transactions |
| Outbox | Store events in same transaction | event को उसी transaction में सेव करना |

---

## ⚡ 3-Line Summary
**English:**
1. A transaction groups operations into one all-or-nothing unit (BEGIN → COMMIT/ROLLBACK).
2. Prevent races with atomic conditional updates, FOR UPDATE, or optimistic versioning; retry deadlocks/serialization errors.
3. Keep transactions short, no external calls inside; across services use sagas + outbox.

**Hindi:**
1. Transaction = कई काम एक इकाई में, सब या कुछ नहीं।
2. Race condition से बचने के लिए `UPDATE … WHERE stock > 0`, FOR UPDATE या version check; deadlock पर retry।
3. Transaction छोटा, अंदर बाहरी API नहीं; services के बीच Saga + Outbox।

---

## ➡️ Next Topic Suggestion
**34. ACID Properties** — Transactions are defined by four guarantees. Next: Atomicity, Consistency, Isolation and Durability in depth, and how a DB actually implements each one (WAL, constraints, MVCC, fsync).
