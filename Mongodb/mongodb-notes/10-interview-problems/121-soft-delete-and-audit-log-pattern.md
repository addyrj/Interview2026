# 121. Soft Delete + Audit Log Pattern
# हिंदी में: Soft Delete + Audit Log Pattern

---

## 🔵 Simple Definition (English)
**Soft delete** means you do not physically remove a document; you mark it as deleted (for example `deletedAt: <Date>`) and every normal query ignores marked documents. An **audit log** is an append-only collection that records *who* changed *what* and *when*. Together they give you "undo", compliance history and safe debugging.

## 🔵 सरल परिभाषा (Hindi)
**Soft delete** का मतलब है document को असल में हटाना नहीं, बल्कि उस पर निशान लगाना (जैसे `deletedAt: <Date>`) और हर normal query उस निशान वाले documents को ignore करे। **Audit log** एक append-only collection है जो रिकॉर्ड करती है *किसने*, *क्या* और *कब* बदला। दोनों मिलकर "undo", compliance history और आसान debugging देते हैं।

---

## 🔴 Problem it Solves
A hard `deleteOne` is permanent. Support staff accidentally delete a user, finance asks "who removed this invoice last March?", or a legal hold forbids erasing records. Without soft delete + audit you cannot restore data and you cannot prove what happened. The catch: soft delete creates new problems (unique indexes, forgotten filters, growing data) that this pattern must solve.

## 🔴 यह क्यों बना? (Hindi)
Hard `deleteOne` हमेशा के लिए होता है। Support staff गलती से user delete कर दे, finance पूछे "पिछले March में यह invoice किसने हटाया?", या legal hold कहे कि records मिटाना मना है। Soft delete + audit के बिना न data restore हो सकता है न यह साबित हो सकता है कि क्या हुआ। दिक्कत यह है कि soft delete नई समस्याएँ लाता है (unique indexes, भूले हुए filters, बढ़ता data) जिन्हें यह pattern हल करता है।

---

## 🟢 How it Works — Step by Step

Step 1 -> Add `deletedAt: null` (and optionally `deletedBy`) to every document at creation. Using `null` instead of a missing field lets you use a **partial index** on `deletedAt: null`.
Step 2 -> "Delete" = `updateOne({_id, deletedAt: null}, {$set: {deletedAt: now, deletedBy}})`. The `deletedAt: null` in the filter makes it idempotent.
Step 3 -> Every read adds `deletedAt: null`. Enforce this centrally (Mongoose query middleware, repository layer) so no developer forgets it.
Step 4 -> Make **unique indexes partial** (`partialFilterExpression: {deletedAt: null}`) so a deleted user's email can be reused.
Step 5 -> Write one audit entry per change into an `audit` collection (`coll, docId, action, by, at, before/after or diff`). Never update or delete audit rows.
Step 6 -> Restore = set `deletedAt` back to `null` (check the unique constraint can still hold). Purge old soft-deleted rows and old audit rows with a TTL index or a scheduled job.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> हर document में creation पर `deletedAt: null` (और चाहें तो `deletedBy`) रखो। Missing field की जगह `null` रखने से `deletedAt: null` पर **partial index** बन पाता है।
Step 2 -> "Delete" = `updateOne({_id, deletedAt: null}, {$set: {deletedAt: now, deletedBy}})`। Filter में `deletedAt: null` इसे idempotent बनाता है।
Step 3 -> हर read में `deletedAt: null` जोड़ो। इसे central जगह (Mongoose query middleware, repository layer) में enforce करो ताकि कोई developer भूले नहीं।
Step 4 -> Unique indexes को **partial** बनाओ (`partialFilterExpression: {deletedAt: null}`) ताकि delete हुए user का email दोबारा इस्तेमाल हो सके।
Step 5 -> हर बदलाव पर `audit` collection में एक entry लिखो (`coll, docId, action, by, at, before/after या diff`)। Audit rows को कभी update/delete मत करो।
Step 6 -> Restore = `deletedAt` वापस `null` (देखो unique constraint अब भी टिकता है या नहीं)। पुराने soft-deleted rows और audit rows को TTL index या scheduled job से purge करो।

---

## 🟡 Real World Example
**Razorpay-style merchant dashboard:** a merchant "deletes" a payment link. The record must disappear from the UI instantly, but finance and RBI audits require it to remain for years. The `payment_links` document gets `deletedAt` and `deletedBy: "merchant_88"`, and the `audit` collection gets `{action: "SOFT_DELETE", docId, by, at}`. When the merchant creates a new link with the same `slug`, the partial unique index allows it because the old one is soft-deleted. Six months later a support agent restores the old link in one update.

## 🟡 Real Example Hindi mein
**Razorpay जैसा merchant dashboard:** merchant एक payment link "delete" करता है। UI से तुरंत गायब होना चाहिए, लेकिन finance और RBI audits के लिए record सालों रहना चाहिए। `payment_links` document में `deletedAt` और `deletedBy: "merchant_88"` लगता है, और `audit` collection में `{action: "SOFT_DELETE", docId, by, at}` जाता है। जब merchant उसी `slug` का नया link बनाता है तो partial unique index इसकी अनुमति देता है क्योंकि पुराना soft-deleted है। छह महीने बाद support agent एक update से पुराना link restore कर सकता है।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4 with mongosh (dates and ObjectIds vary; here `_id` is a number).

```javascript
// mongosh --port 27017
const d = db.getSiblingDB("sd");                      // pick a demo database
d.dropDatabase();                                      // start clean

// Partial unique index: email must be unique ONLY among non-deleted users
d.users.createIndex(
  { email: 1 },                                        // field to keep unique
  { unique: true, partialFilterExpression: { deletedAt: null } } // applies only when deletedAt is null
);

d.users.insertMany([                                   // two active users
  { _id: 1, email: "a@x.com", name: "Asha", deletedAt: null },
  { _id: 2, email: "b@x.com", name: "Bob",  deletedAt: null },
]);

// SOFT DELETE: filter has deletedAt:null so double-delete is a no-op
const r = d.users.updateOne(
  { _id: 1, deletedAt: null },                         // only if currently active
  { $set: { deletedAt: new Date("2026-01-01"), deletedBy: "admin7" } } // mark deleted
);
print("modified", r.modifiedCount);                    // Output: modified 1

// AUDIT entry (append-only)
d.audit.insertOne({ coll: "users", docId: 1, action: "SOFT_DELETE", by: "admin7", at: new Date("2026-01-01") });

// Re-use the same email: allowed, because the old row is soft-deleted
d.users.insertOne({ _id: 3, email: "a@x.com", name: "Asha2", deletedAt: null }); // Output: acknowledged, no error

// Duplicate among ACTIVE users is still blocked
try { d.users.insertOne({ _id: 4, email: "a@x.com", name: "dup", deletedAt: null }); }
catch (e) { print("dup:", e.code); }                   // Output: dup: 11000

// Normal read: always filter deletedAt:null
d.users.find({ deletedAt: null }, { name: 1 });
// Output: [ { _id: 2, name: 'Bob' }, { _id: 3, name: 'Asha2' } ]

// RESTORE of _id 1 now FAILS, because "a@x.com" is active on _id 3
try { d.users.updateOne({ _id: 1 }, { $set: { deletedAt: null } }); }
catch (e) { print("restore conflict", e.code); }       // Output: restore conflict 11000
```

## 💻 Code Example — Advanced

```javascript
// soft-delete-mongoose.js — Mongoose plugin: auto-filter, soft delete, restore, audit
const mongoose = require('mongoose');                  // ODM

// Audit model: append-only, TTL of 7 years for compliance
const auditSchema = new mongoose.Schema({
  coll: String,                                        // which collection changed
  docId: mongoose.Schema.Types.Mixed,                  // which document
  action: String,                                      // CREATE | UPDATE | SOFT_DELETE | RESTORE
  by: String,                                          // actor (user id from the request)
  at: { type: Date, default: Date.now },               // when
  diff: mongoose.Schema.Types.Mixed,                   // optional changed fields
}, { versionKey: false });
auditSchema.index({ at: 1 }, { expireAfterSeconds: 60 * 60 * 24 * 365 * 7 }); // TTL purge after 7y
auditSchema.index({ coll: 1, docId: 1, at: -1 });      // "history of this document" query
const Audit = mongoose.model('Audit', auditSchema);

function softDelete(schema, { collName }) {
  schema.add({ deletedAt: { type: Date, default: null }, deletedBy: { type: String, default: null } });

  // Auto-add deletedAt:null to every find* / count unless caller opts out with .setOptions({withDeleted:true})
  ['find', 'findOne', 'countDocuments', 'findOneAndUpdate', 'updateOne', 'updateMany'].forEach((op) => {
    schema.pre(op, function () {
      if (!this.getOptions().withDeleted) this.where({ deletedAt: null });
    });
  });

  // Instance helpers
  schema.methods.softDelete = async function (actor) {
    const res = await this.constructor.updateOne(      // goes through the pre-hook, so double-delete is a no-op
      { _id: this._id },
      { $set: { deletedAt: new Date(), deletedBy: actor } }
    );
    if (res.modifiedCount) {                           // only audit when something really changed
      await Audit.create({ coll: collName, docId: this._id, action: 'SOFT_DELETE', by: actor });
    }
    return res.modifiedCount === 1;
  };

  schema.statics.restore = async function (id, actor) {
    const res = await this.updateOne(
      { _id: id },
      { $set: { deletedAt: null, deletedBy: null } },
      { withDeleted: true }                            // we must be allowed to see deleted rows to restore them
    );
    if (res.modifiedCount) await Audit.create({ coll: collName, docId: id, action: 'RESTORE', by: actor });
    return res.modifiedCount === 1;
  };
}

module.exports = { softDelete, Audit };
```

Note: in Mongoose, a `pre('updateOne')` hook that adds `where({deletedAt:null})` also applies to the restore call, which is why `withDeleted: true` must be passed (the hook above skips the filter when it is set). Test this once in your own project: hook behaviour for update operations differs slightly between Mongoose versions.

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { softDelete } = require('./soft-delete-mongoose');

const userSchema = new mongoose.Schema({ email: String, name: String });
userSchema.plugin(softDelete, { collName: 'users' });  // enable pattern
// Partial unique index: Mongoose passes partialFilterExpression to MongoDB
userSchema.index({ email: 1 }, { unique: true, partialFilterExpression: { deletedAt: null } });
const User = mongoose.model('User', userSchema);

const app = express();
app.use(express.json());

// actor comes from auth middleware in real life; header used here for demo
const actor = (req) => req.get('x-user-id') || 'anonymous';

app.get('/users', async (req, res) => res.json(await User.find().lean()));  // deleted users hidden automatically

app.delete('/users/:id', async (req, res) => {
  const user = await User.findOne({ _id: req.params.id }); // null if already deleted
  if (!user) return res.status(404).json({ error: 'Not found' });
  await user.softDelete(actor(req));                   // sets deletedAt + writes audit entry
  res.status(204).end();
});

app.post('/users/:id/restore', async (req, res) => {
  try {
    const ok = await User.restore(req.params.id, actor(req));
    res.status(ok ? 200 : 404).json({ restored: ok });
  } catch (e) {
    // 11000: another ACTIVE user already uses this email
    res.status(e.code === 11000 ? 409 : 500).json({ error: e.message });
  }
});

app.get('/admin/users/:id/history', async (req, res) => { // audit trail for support staff
  const { Audit } = require('./soft-delete-mongoose');
  res.json(await Audit.find({ coll: 'users', docId: req.params.id }).sort({ at: -1 }).lean());
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A plain unique index with soft delete
```javascript
// Wrong — deleted user still "owns" the email forever, signup fails with E11000
db.users.createIndex({ email: 1 }, { unique: true });

// Right — uniqueness only among active rows
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { deletedAt: null } });
```

❌ Mistake 2: Forgetting the `deletedAt: null` filter in one query (e.g. an aggregation `$lookup`)
```javascript
// Wrong — deleted orders leak into reports and into joined data
db.orders.aggregate([{ $group: { _id: "$userId", total: { $sum: "$amount" } } }]);

// Right — filter first, and also inside $lookup pipelines
db.orders.aggregate([{ $match: { deletedAt: null } }, { $group: { _id: "$userId", total: { $sum: "$amount" } } }]);
```

❌ Mistake 3: Storing the flag as a missing field and using `{deletedAt: {$exists:false}}`
✅ Correct: store `deletedAt: null` explicitly. Partial indexes cannot use `$exists: false`, and `{deletedAt: null}` matches both "null" and "missing", so reads still work for old documents.

❌ Mistake 4: Allowing audit rows to be edited
✅ Correct: give the app user `insert` only on the audit collection (custom RBAC role), so even a bug cannot rewrite history.

---

## 🧠 Tricky Interview Question

"After soft-deleting user 1 (email `a@x.com`) you created user 3 with the same email. Now support clicks Restore on user 1. What happens, and how do you handle it?"

Answer: The update `deletedAt: null` makes user 1 active again, which would put two active documents with `a@x.com` in the partial index, so MongoDB rejects it with **E11000 duplicate key** (we reproduced `restore conflict 11000`). The restore API must catch 11000 and return a 409 telling support to rename/merge or delete the new account first. Options: restore with a changed email, or soft-delete user 3 first (then restore works: after that both steps succeeded in our test). This is the hidden cost of "reusable unique values"; a plain unique index would avoid the conflict but block the re-signup.

---

## ⚫ Interview Questions + Answers

Q1: Soft delete vs hard delete: when each?
A1: Soft delete when you need restore, history or legal retention (users, orders, invoices). Hard delete for truly disposable data (sessions, caches) and when law demands erasure (GDPR right to erasure needs a real purge or anonymization, not just a flag).

Q2: Why `deletedAt` (a Date) instead of `isDeleted` (a boolean)?
A2: A Date tells you *when* and enables retention jobs ("purge everything deleted over 90 days ago") and TTL indexes. A boolean needs a second field for time. `deletedAt: null` also works neatly with partial indexes.

Q3: Can a TTL index physically purge soft-deleted documents?
A3: Yes. `createIndex({deletedAt: 1}, {expireAfterSeconds: 7776000})` removes documents 90 days after `deletedAt`. Rows with `deletedAt: null` are not Date values, so TTL ignores them. The TTL monitor runs about every 60 seconds, so it is approximate.

Q4: How do you build the audit log reliably?
A4: Write the audit entry in the same multi-document transaction as the change (replica set required), or use **change streams** to copy changes into the audit collection asynchronously (no app code can forget it). Without a transaction, a crash between the two writes leaves a missing entry.

Q5: Does a filter on `deletedAt: null` hurt performance?
A5: It adds a predicate, so include it in compound indexes (`{userId:1, deletedAt:1, createdAt:-1}`) or use a partial index with `partialFilterExpression: {deletedAt: null}` so deleted rows are not even in the index. The query must contain the same `deletedAt: null` condition for the partial index to be chosen.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users must be able to restore or undo (admin tools, trash bin, "archived" items)
- Compliance, finance or disputes need history of who deleted what
- Other collections reference the document by id (orders reference products) and you cannot allow dangling references

❌ Avoid when:
- Data must truly be erased (GDPR/DPDP requests, PII): use real delete or anonymize
- Very high-churn data (sessions, OTPs, logs): the collection would only grow; use TTL hard delete
- The team cannot centrally enforce the filter: leaked deleted data is worse than hard delete

---

## 📊 Visual Diagram
```
SOFT DELETE + AUDIT
─────────────────────────────────────────────────────
 DELETE /users/1
      │
      ▼
 updateOne({_id:1, deletedAt:null},
           {$set:{deletedAt:now, deletedBy}})
      │ modifiedCount == 1 ?
      ├── yes ──► audit.insertOne({action:"SOFT_DELETE",...})
      └── no  ──► 404 (already deleted)

 users collection                    audit collection (append-only)
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │ 1 a@x.com deletedAt=DATE │        │ SOFT_DELETE users/1 admin7│
 │ 2 b@x.com deletedAt=null │        │ RESTORE     users/1 admin2│
 │ 3 a@x.com deletedAt=null │        └──────────────────────────┘
 └──────────────────────────┘
 partial unique index on email  (only rows with deletedAt:null)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Soft delete | Mark instead of remove | हटाने की जगह निशान लगाना |
| Hard delete | Physically remove the document | Document असल में हटाना |
| Audit log | Append-only history of changes | बदलावों का append-only इतिहास |
| Partial index | Index only on documents matching a filter | सिर्फ filter-matching documents पर index |
| Idempotent | Repeating gives the same result | दोहराने पर वही नतीजा |
| Restore | Undo a soft delete | Soft delete को वापस करना |
| Change stream | Real-time feed of DB changes | DB बदलावों की real-time feed |

---

## ⚡ 3-Line Summary
English:
1. Soft delete = set `deletedAt`, filter `deletedAt: null` on every read, and write an append-only audit entry for each change.
2. Use partial unique indexes so deleted values can be reused, and expect E11000 when restoring conflicts.
3. Soft delete is not GDPR erasure; purge with TTL or anonymize when the law requires.

Hindi:
1. Soft delete = `deletedAt` set करो, हर read में `deletedAt: null` filter लगाओ, और हर बदलाव पर append-only audit entry लिखो।
2. Partial unique indexes इस्तेमाल करो ताकि deleted values दोबारा use हों, और restore में conflict पर E11000 की उम्मीद रखो।
3. Soft delete GDPR erasure नहीं है; कानून माँगे तो TTL से purge या anonymize करो।

---

## ➡️ Next Topic
**122. Implement Optimistic Locking with Versioning** — protect concurrent updates with a version field and conditional `updateOne`.
