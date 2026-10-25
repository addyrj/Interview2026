# 150. Sequelize Hooks
# हिंदी में: Sequelize Hooks — Model Lifecycle Events

---

## 🔵 Simple Definition (English)
**Sequelize Hooks** (also called lifecycle callbacks) are functions that run automatically before or after certain model operations — like `beforeCreate`, `afterUpdate`, `beforeDestroy`. They let you run side-effect code (hashing passwords, validation, logging, sending emails) without manually calling it every time you create/update/delete a record.

## 🔵 सरल परिभाषा (Hindi)
**Sequelize Hooks** (lifecycle callbacks) वो functions हैं जो model operations से पहले या बाद automatically चलते हैं — जैसे `beforeCreate`, `afterUpdate`, `beforeDestroy`। इनसे side-effect code (password hash करना, validation, logging, email भेजना) हर बार manually call किए बिना automatically चलता है।

---

## 🔴 Problem it Solves
Without hooks, every piece of code that creates a User would need to remember to hash the password manually:
```javascript
const bcrypt = require('bcrypt');
const hashed = await bcrypt.hash(password, 10);
await User.create({ email, password: hashed }); // must remember EVERY time
```
If a developer forgets this in even one place (a script, a seed file, an admin panel), plaintext passwords get saved — a serious security bug. Hooks centralize this logic in the model itself so it ALWAYS runs, regardless of where `.create()` is called from.

## 🔴 यह क्यों बना? (Hindi)
Hooks के बिना, जहाँ भी User create होता, वहाँ manually password hash करना याद रखना पड़ता। अगर developer कहीं भूल गया (script, seed file, admin panel), plaintext password save हो जाता — security bug। Hooks इस logic को model में centralize करते हैं ताकि हमेशा चले, चाहे `.create()` कहीं से भी call हो।

---

## 🟢 How it Works — Step by Step

Step 1 → Define hooks either in model options (`hooks: { beforeCreate() {} }`) or via `Model.beforeCreate(fn)`.
Step 2 → Sequelize runs hooks automatically around CRUD operations: create, update, destroy, bulkCreate, validate.
Step 3 → "before" hooks run BEFORE the SQL query executes — can modify data or throw to cancel the operation.
Step 4 → "after" hooks run AFTER the SQL query succeeds — good for side effects like logging or notifications.
Step 5 → Hooks can be async (return a Promise) — Sequelize awaits them before continuing.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Hooks model options में (`hooks: { beforeCreate() {} }`) या `Model.beforeCreate(fn)` से define करो।
Step 2 → Sequelize CRUD operations के आस-पास automatically hooks चलाता है।
Step 3 → "before" hooks SQL query से पहले चलते हैं — data modify कर सकते या operation cancel कर सकते (throw करके)।
Step 4 → "after" hooks SQL query सफल होने के बाद चलते हैं — logging, notification के लिए अच्छे।
Step 5 → Hooks async हो सकते हैं (Promise return करें) — Sequelize await करता है।

---

## 🟡 Real World Example
**Paytm's wallet transaction system:** Every `Transaction.create()` triggers a `beforeCreate` hook that validates the sender has sufficient balance, and an `afterCreate` hook that updates the wallet balance and sends a push notification. Also a `beforeSave` hook hashes any password field if a `User` model is updated. This guarantees business rules are enforced at the DATA layer, not scattered across every controller that might create a transaction.

## 🟡 Real Example Hindi mein
**Paytm का wallet transaction system:** हर `Transaction.create()` पर `beforeCreate` hook sender का balance check करता है, और `afterCreate` hook wallet balance update करके push notification भेजता है। यह business rules को DATA layer पर enforce करता है, हर controller में बार-बार नहीं लिखना पड़ता।

---

## 💻 Code Example — Basic

```javascript
// sequelize-hooks-basic.js
// npm install sequelize sqlite3 bcrypt
const { Sequelize, DataTypes } = require('sequelize');
const bcrypt = require('bcrypt');

const sequelize = new Sequelize('sqlite::memory:', { logging: false });

const User = sequelize.define('User', {
  email: { type: DataTypes.STRING, unique: true, allowNull: false },
  password: { type: DataTypes.STRING, allowNull: false },
}, {
  hooks: {
    // beforeCreate runs right before INSERT query
    async beforeCreate(user) {
      // hash the plaintext password automatically
      user.password = await bcrypt.hash(user.password, 10);
    },
    // beforeUpdate runs right before UPDATE query
    async beforeUpdate(user) {
      // only rehash if password field actually changed
      if (user.changed('password')) {
        user.password = await bcrypt.hash(user.password, 10);
      }
    },
  },
});

async function main() {
  await sequelize.sync({ force: true });

  // password gets hashed automatically via beforeCreate hook
  const user = await User.create({ email: 'rahul@example.com', password: 'mySecret123' });
  console.log('Stored hash:', user.password); // bcrypt hash, not plaintext

  // Verify login works with original password against the hash
  const isValid = await bcrypt.compare('mySecret123', user.password);
  console.log('Password matches:', isValid); // true

  await sequelize.close();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// sequelize-hooks-advanced.js — Production pattern: audit log + validation + rollback
const { Sequelize, DataTypes, Model } = require('sequelize');
const sequelize = new Sequelize('sqlite::memory:', { logging: false });

class Wallet extends Model {}
Wallet.init({
  userId: DataTypes.INTEGER,
  balance: { type: DataTypes.FLOAT, defaultValue: 0 },
}, { sequelize, modelName: 'wallet' });

class Transaction extends Model {}
Transaction.init({
  walletId: DataTypes.INTEGER,
  amount: DataTypes.FLOAT,
  type: DataTypes.STRING, // 'debit' | 'credit'
}, { sequelize, modelName: 'transaction' });

class AuditLog extends Model {}
AuditLog.init({ action: DataTypes.STRING, meta: DataTypes.TEXT }, { sequelize, modelName: 'auditLog' });

// beforeCreate: VALIDATE sufficient balance for debit, else cancel operation by throwing
Transaction.beforeCreate(async (txn, options) => {
  if (txn.type === 'debit') {
    const wallet = await Wallet.findByPk(txn.walletId, { transaction: options.transaction });
    if (!wallet || wallet.balance < txn.amount) {
      // throwing inside a hook CANCELS the create — no row inserted
      throw new Error('Insufficient balance for debit transaction');
    }
  }
});

// afterCreate: update wallet balance + write audit log (side effects after success)
Transaction.afterCreate(async (txn, options) => {
  const wallet = await Wallet.findByPk(txn.walletId, { transaction: options.transaction });
  const delta = txn.type === 'credit' ? txn.amount : -txn.amount;
  await wallet.increment('balance', { by: delta, transaction: options.transaction });

  await AuditLog.create({
    action: `transaction:${txn.type}`,
    meta: JSON.stringify({ walletId: txn.walletId, amount: txn.amount }),
  }, { transaction: options.transaction });
});

async function run() {
  await sequelize.sync({ force: true });
  const wallet = await Wallet.create({ userId: 1, balance: 1000 });

  try {
    // Wrap in a DB transaction so hook side effects are atomic with the main insert
    await sequelize.transaction(async (t) => {
      await Transaction.create(
        { walletId: wallet.id, amount: 200, type: 'debit' },
        { transaction: t }
      );
    });

    const updated = await Wallet.findByPk(wallet.id);
    console.log('Balance after debit:', updated.balance); // 800

    // This one will fail — insufficient balance — and the hook throws, rolling back
    await sequelize.transaction(async (t) => {
      await Transaction.create(
        { walletId: wallet.id, amount: 5000, type: 'debit' },
        { transaction: t }
      );
    });
  } catch (err) {
    console.error('Transaction blocked by hook:', err.message);
  }

  const auditCount = await AuditLog.count();
  console.log('Audit log entries (only successful txns):', auditCount); // 1

  await sequelize.close();
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express route — hooks run transparently, controller stays clean
const express = require('express');
const app = express();
app.use(express.json());

app.post('/api/register', async (req, res) => {
  try {
    // beforeCreate hook hashes password automatically — controller never touches bcrypt
    const user = await User.create({
      email: req.body.email,
      password: req.body.password,
    });
    res.status(201).json({ id: user.id, email: user.email }); // password never returned
  } catch (err) {
    if (err.name === 'SequelizeUniqueConstraintError') {
      return res.status(409).json({ error: 'Email already registered' });
    }
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rehashing an already-hashed password on every update
```javascript
// Wrong — hashes password on EVERY update, even if unrelated field changed
beforeUpdate(user) {
  user.password = bcrypt.hashSync(user.password, 10); // double-hashes!
}

// Right — only rehash when password field actually changed
beforeUpdate(user) {
  if (user.changed('password')) {
    user.password = bcrypt.hashSync(user.password, 10);
  }
}
```

❌ Mistake 2: Doing side effects in hooks without passing the transaction down
✅ Correct: Always forward `options.transaction` to any query inside a hook, otherwise hook queries run OUTSIDE the parent transaction and won't roll back together on failure.
```javascript
// Wrong — ignores options.transaction, breaks atomicity
afterCreate(async (txn) => { await Wallet.update(..., {}); });
// Right
afterCreate(async (txn, options) => {
  await Wallet.update(..., { transaction: options.transaction });
});
```

---

## 🧠 Tricky Interview Question

```javascript
User.beforeCreate(() => { throw new Error('Blocked!'); });
User.afterCreate(() => { console.log('After ran'); });

try {
  await User.create({ email: 'a@a.com', password: 'x' });
} catch (e) {
  console.log('Caught:', e.message);
}
```
Answer: Output is only `"Caught: Blocked!"` — `"After ran"` never prints. When a `beforeCreate` hook throws, Sequelize immediately cancels the entire operation: no INSERT query runs, and no subsequent hooks (including `afterCreate`) execute. The error propagates up to the caller's `try/catch`. This is why `beforeCreate`/`beforeUpdate` hooks are the right place for validation that should block the operation.

---

## ⚫ Interview Questions + Answers

Q1: What are the main hook types available in Sequelize?
A1: Grouped by operation: Create (`beforeCreate`, `afterCreate`), Update (`beforeUpdate`, `afterUpdate`), Destroy (`beforeDestroy`, `afterDestroy`), Save (`beforeSave`/`afterSave` — fires for both create AND update), Validate (`beforeValidate`, `afterValidate`), Bulk operations (`beforeBulkCreate`, `beforeBulkUpdate`, `beforeBulkDestroy`), and transaction-level (`beforeTransaction`, `afterCommit`).

Q2: How do you cancel an operation from inside a hook?
A2: Throw an error (or return a rejected Promise) inside a "before" hook. Sequelize catches it, stops the operation (no SQL query is sent), and propagates the error to the caller. This is commonly used for custom validation that's too complex for built-in `validate` rules — e.g., checking account balance before a debit.

Q3: What is the difference between `beforeSave` and `beforeCreate`/`beforeUpdate`?
A3: `beforeSave` fires on BOTH create and update operations (it's a combined hook), while `beforeCreate` only fires on create and `beforeUpdate` only fires on update. Use `beforeSave` for logic that should apply regardless of whether it's a new or existing record (e.g., always normalize an email to lowercase); use the specific ones when behavior differs (e.g., only rehash password if changed, on update).

Q4: Do hooks fire for bulk operations like `bulkCreate` or `Model.update()`?
A4: By default, individual instance hooks (`beforeCreate`) do NOT fire for `bulkCreate()` or `Model.update()` (these skip per-instance hooks for performance). You must pass `{ individualHooks: true }` to force per-row hooks to run, or use the dedicated bulk hooks (`beforeBulkCreate`, `beforeBulkUpdate`) which receive the whole array/options instead of a single instance.

Q5: Can hooks be async, and how does Sequelize handle that?
A5: Yes — hooks can be `async` functions or return a Promise. Sequelize awaits the hook's Promise before proceeding to the next step (or the SQL query). This lets you do things like calling an external API, hashing passwords with async bcrypt, or running nested DB queries inside a hook, all while keeping the operation properly sequenced.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Enforcing data integrity rules that MUST always apply (password hashing, slug generation, balance checks)
- Centralizing audit logging / notification side effects tied to model changes
- Normalizing data (lowercase emails, trimming strings) before save

❌ Avoid when:
- The logic is business-specific to ONE particular API endpoint, not a model-wide rule (put it in the controller/service instead)
- Hooks would create hidden, hard-to-trace side effects for simple CRUD apps — too much "magic" can make debugging harder

---

## 📊 Visual Diagram
```
SEQUELIZE HOOK LIFECYCLE (for .create())
──────────────────────────────────────────────
  User.create({...})
        │
        ▼
  beforeValidate  ──▶ afterValidate
        │
        ▼
  beforeCreate  (can throw → cancels operation)
        │
        ▼
     INSERT INTO users ... (actual SQL)
        │
        ▼
  afterCreate   (side effects: logging, notifications)
        │
        ▼
  beforeSave / afterSave  (fires for create AND update)
        │
        ▼
     returns created instance
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hook | Lifecycle callback function | Lifecycle callback function |
| beforeCreate | Runs before INSERT | INSERT से पहले चलता है |
| afterCreate | Runs after successful INSERT | INSERT सफल होने के बाद |
| beforeSave | Fires on both create+update | Create और update दोनों पर |
| individualHooks | Force hooks on bulk ops | Bulk operations पर hooks force करना |
| transaction | Atomic group of queries | Queries का atomic group |
| changed() | Checks if a field was modified | Field modify हुआ या नहीं check करना |

---

## ⚡ 3-Line Summary
English:
1. Sequelize hooks run code automatically before/after model operations (create, update, destroy) without needing to call it manually everywhere.
2. Throwing inside a "before" hook cancels the operation entirely — useful for validation and business rule enforcement.
3. Always forward `options.transaction` inside hooks that run queries, or the hook's side effects won't roll back with the main operation.

Hindi:
1. Sequelize hooks model operations (create, update, destroy) से पहले/बाद automatically code चलाते हैं।
2. "before" hook में throw करने से operation cancel हो जाता है — validation के लिए useful।
3. Hooks के अंदर queries में हमेशा `options.transaction` pass करो, नहीं तो rollback साथ नहीं होगा।

---

## ➡️ Next Topic
**151. Prisma ORM — Complete Guide** — A modern, type-safe alternative to Sequelize with auto-generated client and schema-first design.
