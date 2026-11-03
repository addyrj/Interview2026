# 93. ACID in MongoDB + Multi-Document Transactions
# हिंदी में: MongoDB में ACID + Multi-Document Transactions

---

## 🔵 Simple Definition (English)
**ACID** = Atomicity (all or nothing), Consistency (rules always hold), Isolation (concurrent work does not interfere), Durability (committed data survives crashes). MongoDB has always been ACID for a **single document** (even with nested arrays). Since **4.0 (replica sets)** and **4.2 (sharded clusters)** it also supports **multi-document transactions** — several operations across documents/collections that commit or roll back together.

## 🔵 सरल परिभाषा (Hindi)
**ACID** = Atomicity (या सब या कुछ नहीं), Consistency (नियम हमेशा बने रहें), Isolation (concurrent काम एक-दूसरे में दखल न दें), Durability (commit हुआ data crash के बाद भी बचे)। MongoDB **एक document** के लिए (nested arrays समेत) हमेशा से ACID है। **4.0 (replica sets)** और **4.2 (sharded clusters)** से यह **multi-document transactions** भी देता है — कई documents/collections पर operations जो साथ commit या साथ rollback होते हैं।

---

## 🔴 Problem it Solves
Moving ₹300 from Asha's wallet to Ravi's is two updates. If the server crashes after debiting Asha but before crediting Ravi, money vanishes. Single-document atomicity cannot help because the two balances live in different documents. Without transactions, developers build fragile "saga" and compensation code. Transactions give an all-or-nothing guarantee, and snapshot isolation hides half-finished work from other readers.

## 🔴 यह क्यों बना? (Hindi)
Asha के wallet से Ravi के wallet में ₹300 भेजना दो updates हैं। Asha का debit होने के बाद पर Ravi का credit होने से पहले server crash हो जाए तो पैसे गायब हो जाते हैं। Single-document atomicity यहाँ मदद नहीं करती क्योंकि दोनों balances अलग documents में हैं। Transactions के बिना developers नाज़ुक "saga" और compensation code लिखते। Transactions all-or-nothing guarantee और snapshot isolation देते हैं जो अधूरा काम दूसरे readers से छुपाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Requires a **replica set** (or sharded cluster). A standalone `mongod` cannot run transactions (error: "Transaction numbers are only allowed on a replica set member or mongos").
Step 2 → Start a **session**: `client.startSession()`.
Step 3 → Run `session.withTransaction(async () => { ... })` — the callback executes operations that all receive `{ session }`.
Step 4 → Writes inside the transaction are held privately; other clients see the old data (**snapshot isolation**).
Step 5 → On success, `commit` makes all writes visible atomically (oplog entry written as one unit). On exception, `abort` discards everything.
Step 6 → `withTransaction` automatically **retries** on `TransientTransactionError` and on unknown commit results.
Step 7 → Limits: default `transactionLifetimeLimitSeconds` = 60; keep transactions short; oplog entry size ≤ 16 MB per transaction (4.2+ can span multiple oplog entries).

**Design first:** model data so most business operations touch ONE document (embed). Use transactions only for the rest.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Replica set** (या sharded cluster) ज़रूरी है। Standalone `mongod` पर transaction नहीं चलती (error: "Transaction numbers are only allowed on a replica set member or mongos")।
Step 2 → **Session** शुरू करो: `client.startSession()`।
Step 3 → `session.withTransaction(async () => { ... })` चलाओ — callback के सारे operations को `{ session }` देना होता है।
Step 4 → Transaction के अंदर की writes private रहती हैं; बाकी clients पुराना data देखते हैं (**snapshot isolation**)।
Step 5 → Success पर `commit` सारी writes atomically visible करता है। Exception पर `abort` सब फेंक देता है।
Step 6 → `withTransaction` `TransientTransactionError` पर automatically **retry** करता है।
Step 7 → Limits: default `transactionLifetimeLimitSeconds` = 60; transactions छोटी रखो।

**पहले design:** data ऐसे model करो कि ज़्यादातर business operations **एक document** पर हों (embed)। Transactions सिर्फ बाकी के लिए।

---

## 🟡 Real World Example
**PhonePe-style wallet transfer**: debit sender, credit receiver and write a ledger entry must be atomic. If the sender's balance is insufficient, the whole transaction aborts and no ledger entry exists. Meanwhile, **Zomato's order document** (items, address, status history embedded) is updated with a single `updateOne` — no transaction needed because one document is already atomic.

## 🟡 Real Example Hindi mein
**PhonePe-जैसा wallet transfer**: sender का debit, receiver का credit और ledger entry — तीनों atomic होने चाहिए। Sender का balance कम हो तो पूरी transaction abort होती है और ledger में कुछ नहीं बनता। वहीं **Zomato का order document** (items, address, status history embedded) एक `updateOne` से update होता है — transaction नहीं चाहिए क्योंकि एक document पहले से atomic है।

---

## 💻 Code Example — Basic

Single-document atomicity (works on any server, no transaction):

```javascript
// mongosh — $inc and array push on ONE document are atomic together
db.orders.updateOne(
  { _id: 1001 },
  { $set: { status: 'PREPARING' },                      // both changes happen
    $push: { history: { s: 'PREPARING', at: new Date() } } } // or neither
);
```

Multi-document transaction (Node driver, tested on a single-node replica set `rs0`, MongoDB 8.0.4):

```javascript
const { MongoClient } = require('mongodb');
const client = new MongoClient('mongodb://127.0.0.1:27017/?replicaSet=rs0');

async function transfer(from, to, amt) {
  const session = client.startSession();                // sessions carry transaction state
  try {
    await session.withTransaction(async () => {         // auto-retries transient errors
      const w = client.db('bank').collection('wallets');
      // Debit only if balance is enough — filter + $inc is atomic per document
      const r = await w.updateOne({ _id: from, bal: { $gte: amt } }, { $inc: { bal: -amt } }, { session });
      if (r.modifiedCount === 0) throw new Error('Insufficient balance'); // throw => ABORT
      await w.updateOne({ _id: to }, { $inc: { bal: amt } }, { session });  // credit
      await client.db('bank').collection('ledger')
        .insertOne({ from, to, amt, at: new Date() }, { session });          // audit row
    }, { readConcern: { level: 'snapshot' }, writeConcern: { w: 'majority' } });
    console.log('committed');
  } catch (e) { console.log('aborted:', e.message); }
  finally { await session.endSession(); }               // always release the session
}
```

Real run (wallets: asha 1000, ravi 100):
```text
await transfer('asha','ravi',300)   -> committed
await transfer('ravi','asha',5000)  -> aborted: Insufficient balance
wallets: [ { _id: 'asha', bal: 700 }, { _id: 'ravi', bal: 400 } ]   ledger count: 1
```
The second transfer left no trace: balances unchanged and no ledger row.

## 💻 Code Example — Advanced

Isolation demo: an open transaction's writes are invisible outside it.

```javascript
const s = client.startSession();
s.startTransaction();                                   // manual control (no auto-retry)
await w.updateOne({ _id: 'asha' }, { $set: { bal: 0 } }, { session: s });
console.log('inside tx:', (await w.findOne({ _id: 'asha' }, { session: s })).bal);  // 0
console.log('outside  :', (await w.findOne({ _id: 'asha' })).bal);                  // 700
await s.abortTransaction();                             // rollback
await s.endSession();
console.log('after abort:', (await w.findOne({ _id: 'asha' })).bal);                // 700
```
Verified output: `inside tx: 0  outside: 700` then `after abort: 700`.

Mongosh equivalent:
```javascript
const session = db.getMongo().startSession();           // session object
const wallets = session.getDatabase('bank').wallets;    // collection bound to the session
session.startTransaction({ readConcern: { level: 'snapshot' }, writeConcern: { w: 'majority' } });
wallets.updateOne({ _id: 'asha' }, { $inc: { bal: -100 } });
wallets.updateOne({ _id: 'ravi' }, { $inc: { bal: 100 } });
session.commitTransaction();                            // or session.abortTransaction()
session.endSession();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: Model.startSession() + connection.transaction() helper
app.post('/transfer', async (req, res) => {
  const { from, to, amount } = req.body;
  const session = await mongoose.startSession();
  try {
    await session.withTransaction(async () => {        // retries transient errors
      const a = await Wallet.findOneAndUpdate(
        { _id: from, bal: { $gte: amount } }, { $inc: { bal: -amount } }, { session });
      if (!a) throw new Error('INSUFFICIENT');          // abort
      await Wallet.updateOne({ _id: to }, { $inc: { bal: amount } }, { session });
      await Ledger.create([{ from, to, amount }], { session }); // create() needs an ARRAY with session
    });
    res.json({ ok: true });
  } catch (e) {
    res.status(e.message === 'INSUFFICIENT' ? 400 : 500).json({ error: e.message });
  } finally { await session.endSession(); }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to pass `{ session }`
```javascript
// Wrong — this write runs OUTSIDE the transaction and will NOT roll back
await w.updateOne({ _id: to }, { $inc: { bal: amt } });
// Right
await w.updateOne({ _id: to }, { $inc: { bal: amt } }, { session });
```

❌ Mistake 2: Using transactions for everything
✅ Correct: They cost locks, memory and latency. Embed related data so the common write is single-document.

❌ Mistake 3: Side effects inside `withTransaction`
✅ Correct: The callback can be re-run on retry. Sending an email or calling a payment gateway inside it can fire twice. Do external effects after commit.

❌ Mistake 4: Long transactions
✅ Correct: Default lifetime is 60 s; long ones increase write conflicts (`WriteConflict`) and cache pressure. Keep them under a second where possible.

❌ Mistake 5: Running on a standalone server
✅ Correct: Use a replica set even in development (`--replSet rs0` + `rs.initiate()`).

---

## 🧠 Tricky Interview Question

Q: Two transactions both read Asha's balance 1000 and both try to debit 700 with `$set: {bal: 300}`. What happens?

Answer: MongoDB uses optimistic concurrency with snapshot isolation. The first to write the document wins; the second gets a `WriteConflict` (a `TransientTransactionError`) and, with `withTransaction`, is automatically retried against fresh data — where the guard `bal: {$gte: 700}` now fails. This is why you write `updateOne({bal:{$gte:amt}}, {$inc:{bal:-amt}})` (check-and-update in one atomic step) instead of read-modify-write in application code. Snapshot isolation does not prevent write skew across different documents, so design invariants carefully.

---

## ⚫ Interview Questions + Answers

Q1: Is MongoDB ACID?
A1: Yes. Single-document operations are always atomic. Since 4.0 (replica sets) and 4.2 (sharded) multi-document transactions are ACID with snapshot isolation. Durability depends on write concern (`w: 'majority'`, `j: true`).

Q2: Why do transactions need a replica set?
A2: They rely on the oplog and logical session/cluster-time machinery to commit atomically and replicate as a unit. A standalone node has neither.

Q3: What is `withTransaction` vs manual `startTransaction`?
A3: `withTransaction` wraps start/commit/abort and retries on `TransientTransactionError` and `UnknownTransactionCommitResult`. Manual mode gives control but you must write retry logic yourself.

Q4: Which read/write concerns should you use?
A4: `readConcern: 'snapshot'` and `writeConcern: { w: 'majority' }` for strongest guarantees; transaction-level concerns override session defaults. Individual operations inside cannot set their own.

Q5: Can you create collections inside a transaction?
A5: From MongoDB 4.4 you can create collections/indexes implicitly inside a transaction (if the collection does not exist and it is the first operation on it); earlier versions required them to exist beforehand. Some commands (e.g. `listCollections` variants, `drop` of in-use collections) have restrictions — check your version's docs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Money/inventory movement across documents (wallet, stock + order)
- Maintaining invariants between a document and its audit/summary document

❌ Avoid when:
- A single embedded document can carry the change
- Very high-throughput hot documents (conflicts) or long-running batch jobs (use idempotent bulk operations instead)

---

## 📊 Visual Diagram
```
  startSession ─► startTransaction (snapshot taken)
        │
        ├─ update wallets (asha -300)   ┐ private writes,
        ├─ update wallets (ravi +300)   ├ invisible to others
        ├─ insert ledger                ┘
        │
   ok? ─┴─► commit ──► all visible atomically (one oplog unit)
   error ───► abort  ──► nothing happened

  Other readers during the tx still see:  asha=1000, ravi=100
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Atomicity | All or nothing | या सब या कुछ नहीं |
| Isolation | Concurrent work doesn't interfere | Concurrent काम में दखल नहीं |
| Durability | Committed data survives crash | Commit data crash में बचा रहता है |
| Session | Context carrying transaction state | Transaction state वाला context |
| Snapshot isolation | Tx reads a consistent point-in-time view | एक ही समय-बिंदु का consistent view |
| WriteConflict | Two txs modified same document | दो transactions ने एक document बदला |
| TransientTransactionError | Safe-to-retry error label | दोबारा try करने लायक error label |
| Saga | Compensating-steps pattern without tx | Transaction के बिना compensation pattern |

---

## ⚡ 3-Line Summary
English:
1. MongoDB is ACID per document always, and across documents via transactions on replica sets (4.0+) and sharded clusters (4.2+).
2. Use `session.withTransaction`, pass `{ session }` to every operation, use snapshot read concern and majority write concern.
3. Prefer embedding for atomic single-document writes; keep transactions short and put side effects after commit.

Hindi:
1. MongoDB हर document पर हमेशा ACID है, और documents के पार transactions से replica sets (4.0+) व sharded clusters (4.2+) पर।
2. `session.withTransaction` इस्तेमाल करो, हर operation को `{ session }` दो, snapshot read concern और majority write concern रखो।
3. Atomic single-document writes के लिए embedding चुनो; transactions छोटी रखो और side effects commit के बाद करो।

---

## ➡️ Next Topic
**94. Replica Sets — How They Work** — The primary/secondary architecture that transactions, durability and failover are built on.
