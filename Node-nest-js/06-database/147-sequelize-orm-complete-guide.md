# 147. Sequelize ORM — Complete Guide
# हिंदी में: Sequelize ORM — पूरी गाइड

---

## 🔵 Simple Definition (English)
**Sequelize** is a promise-based Node.js ORM supporting MySQL, PostgreSQL, SQLite, and MSSQL. It lets you define JavaScript "models" that map to database tables, providing methods for CRUD operations, associations (relationships), transactions, migrations, and validations — all without writing raw SQL for common operations.

## 🔵 सरल परिभाषा (Hindi)
**Sequelize** एक promise-based Node.js ORM है जो MySQL, PostgreSQL, SQLite, MSSQL support करता है। यह JavaScript "models" define करने देता है जो database tables से map होते हैं, CRUD operations, associations (relationships), transactions, migrations, validations के लिए methods देता है — common operations के लिए raw SQL लिखे बिना।

---

## 🔴 Problem it Solves
Without an ORM, every table needs hand-written INSERT/SELECT/UPDATE/DELETE SQL, manual result-row-to-object mapping, manual relationship joining logic, and ad-hoc schema change tracking (who ran which ALTER TABLE, in what order, across which environments). Sequelize provides a declarative model layer: define the shape once, get safe CRUD methods, relationship-aware queries, and a structured migration system for free — making the codebase more maintainable and less error-prone for typical application data access patterns.

## 🔴 यह क्यों बना? (Hindi)
ORM के बिना हर table के लिए hand-written SQL, manual result mapping, manual relationship joining logic, और ad-hoc schema change tracking चाहिए पड़ता। Sequelize एक declarative model layer देता है — shape एक बार define करो, safe CRUD methods, relationship-aware queries, structured migration system मिलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install sequelize mysql2` (Sequelize is DB-agnostic, needs the specific driver too)
Step 2 → Initialize a `Sequelize` instance with connection config (internally manages a connection pool)
Step 3 → Define models using `sequelize.define('ModelName', { fields })` or class-based `extends Model` syntax, specifying column types/constraints
Step 4 → Define associations: `belongsTo`, `hasMany`, `hasOne`, `belongsToMany` — describing how models relate (foreign keys, junction tables)
Step 5 → Use `sequelize.sync()` for quick dev prototyping (auto-creates tables from models) — but use MIGRATIONS for any real/production schema management (topic 148)
Step 6 → Query via model methods: `findAll`, `findOne`, `findByPk`, `create`, `update`, `destroy` — with `where`, `include` (for joins), `order`, `limit` options
Step 7 → Use `sequelize.transaction()` for atomic multi-step operations, and model-level `validate` hooks for data integrity before writes

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install sequelize mysql2` install करो
Step 2 → `Sequelize` instance initialize करो connection config के साथ
Step 3 → Models define करो fields/types के साथ
Step 4 → Associations define करो (belongsTo, hasMany, etc.)
Step 5 → Dev में `sync()`, production में migrations use करो
Step 6 → Model methods से query करो
Step 7 → Transactions और validation hooks use करो

---

## 🟡 Real World Example
**Swiggy's restaurant management backend:** Models `Restaurant`, `MenuItem`, `Owner`, `Order` are defined with Sequelize, with associations: `Restaurant.hasMany(MenuItem)`, `Restaurant.belongsTo(Owner)`, `Order.belongsToMany(MenuItem, { through: OrderItem })`. Fetching a restaurant with its full menu and owner info becomes one readable call: `Restaurant.findByPk(id, { include: [MenuItem, Owner] })` — Sequelize generates the appropriate JOIN SQL automatically, instead of the team hand-writing and maintaining that JOIN logic across dozens of similar endpoints.

## 🟡 Real Example Hindi mein
**Swiggy का restaurant management backend:** Models `Restaurant`, `MenuItem`, `Owner`, `Order` Sequelize से define होते हैं associations के साथ। Restaurant को उसके menu और owner के साथ fetch करना एक readable call बन जाता है — Sequelize automatically JOIN SQL generate करता है।

---

## 💻 Code Example — Basic

```javascript
// sequelize-basic.js — defining a model and basic CRUD
// Run with: node sequelize-basic.js (requires npm install sequelize mysql2, running MySQL)

const { Sequelize, DataTypes } = require('sequelize');

// ─── 1. INITIALIZE SEQUELIZE (manages its own connection pool internally) ───
const sequelize = new Sequelize('shop', 'root', 'password', {
  host: 'localhost',
  dialect: 'mysql',
  logging: false,   // set to console.log to see generated SQL — useful for learning/debugging
});

// ─── 2. DEFINE A MODEL ─────────────────────────────────────────────────────────
const Product = sequelize.define('Product', {
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    validate: { min: 0 },   // built-in validation — rejects negative prices
  },
  stock: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
});

async function main() {
  // ─── 3. SYNC MODEL TO DB (creates table if not exists — dev only, not production) ─
  await sequelize.sync();

  // ─── 4. CREATE ───────────────────────────────────────────────────────────────
  const product = await Product.create({ name: 'Bluetooth Speaker', price: 1999, stock: 50 });
  console.log('Created:', product.toJSON());

  // ─── 5. READ ───────────────────────────────────────────────────────────────────
  const allProducts = await Product.findAll({ where: { stock: { [Sequelize.Op.gt]: 0 } } });
  console.log('In-stock products:', allProducts.length);

  // ─── 6. UPDATE ─────────────────────────────────────────────────────────────────
  await product.update({ price: 1799 });  // instance method
  // OR: await Product.update({ price: 1799 }, { where: { id: product.id } });

  // ─── 7. DELETE ─────────────────────────────────────────────────────────────────
  await product.destroy();

  await sequelize.close();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// sequelize-advanced.js — associations, eager loading, transactions, hooks

const { Sequelize, DataTypes, Op } = require('sequelize');

const sequelize = new Sequelize('shop', 'root', 'password', { host: 'localhost', dialect: 'mysql', logging: false });

// ─── 1. DEFINE MULTIPLE MODELS ────────────────────────────────────────────────
const Restaurant = sequelize.define('Restaurant', {
  name: DataTypes.STRING,
  city: DataTypes.STRING,
});

const MenuItem = sequelize.define('MenuItem', {
  name: DataTypes.STRING,
  price: DataTypes.DECIMAL(10, 2),
});

const Order = sequelize.define('Order', {
  customerId: DataTypes.INTEGER,
  total: DataTypes.DECIMAL(10, 2),
  status: {
    type: DataTypes.ENUM('pending', 'confirmed', 'delivered', 'cancelled'),
    defaultValue: 'pending',
  },
});

// ─── 2. DEFINE ASSOCIATIONS (describes relationships, generates FK columns) ──
Restaurant.hasMany(MenuItem);          // adds restaurantId FK to MenuItem table
MenuItem.belongsTo(Restaurant);

Restaurant.hasMany(Order);
Order.belongsTo(Restaurant);

// ─── 3. HOOKS — lifecycle callbacks for validation/side effects ─────────────
Order.beforeCreate((order, options) => {
  if (order.total < 0) {
    throw new Error('Order total cannot be negative');
  }
});

Order.afterCreate(async (order, options) => {
  console.log(`Order ${order.id} created — sending confirmation notification...`);
  // In real app: trigger notification service, analytics event, etc.
});

// ─── 4. EAGER LOADING (avoids N+1 query problem) ─────────────────────────────
async function getRestaurantWithMenu(restaurantId) {
  return Restaurant.findByPk(restaurantId, {
    include: [
      { model: MenuItem, limit: 20, order: [['price', 'ASC']] },
      { model: Order, where: { status: 'pending' }, required: false },  // required:false = LEFT JOIN
    ],
  });
}

// ─── 5. TRANSACTIONS WITH SEQUELIZE ───────────────────────────────────────────
async function placeOrderTransactional(restaurantId, customerId, items) {
  return sequelize.transaction(async (t) => {
    // All queries using { transaction: t } participate in the same atomic transaction
    const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const order = await Order.create(
      { restaurantId, customerId, total, status: 'confirmed' },
      { transaction: t }
    );

    // If any step throws, Sequelize automatically ROLLS BACK the entire transaction
    for (const item of items) {
      const menuItem = await MenuItem.findByPk(item.id, { transaction: t });
      if (!menuItem) throw new Error(`Menu item ${item.id} not found`);
    }

    return order;  // if we reach here without throwing, Sequelize auto-COMMITS
  });
}

module.exports = { sequelize, Restaurant, MenuItem, Order, getRestaurantWithMenu, placeOrderTransactional };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const { sequelize, Restaurant, MenuItem, Order, getRestaurantWithMenu, placeOrderTransactional } = require('./sequelize-advanced');

const app = express();
app.use(express.json());

app.get('/restaurants/:id', async (req, res) => {
  try {
    const restaurant = await getRestaurantWithMenu(req.params.id);
    if (!restaurant) return res.status(404).json({ error: 'Restaurant not found' });
    res.json(restaurant);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch restaurant' });
  }
});

app.post('/orders', async (req, res) => {
  try {
    const { restaurantId, customerId, items } = req.body;
    const order = await placeOrderTransactional(restaurantId, customerId, items);
    res.status(201).json(order);
  } catch (err) {
    res.status(400).json({ error: err.message });  // e.g., "negative total" validation error
  }
});

// Model-level validation errors surface as SequelizeValidationError — handle distinctly
app.use((err, req, res, next) => {
  if (err.name === 'SequelizeValidationError') {
    return res.status(400).json({ errors: err.errors.map((e) => e.message) });
  }
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

async function start() {
  await sequelize.authenticate();  // verifies connection works before accepting traffic
  console.log('Database connected via Sequelize');
  app.listen(3000, () => console.log('Server running on port 3000'));
}

start().catch((err) => { console.error('Failed to connect:', err); process.exit(1); });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `sequelize.sync({ force: true })` in production
```javascript
// WRONG: force:true DROPS and recreates ALL tables — catastrophic data loss in production!
await sequelize.sync({ force: true });  // NEVER run this against a production database

// CORRECT: use sync() only in local dev/testing without force, and migrations for real schema changes
if (process.env.NODE_ENV === 'development') {
  await sequelize.sync();  // safe-ish for local dev, still not ideal vs migrations
}
// Production: npx sequelize-cli db:migrate  (see topic 148)
```

❌ Mistake 2: Not eager-loading associations, causing N+1 queries
```javascript
// WRONG: fetching restaurants, then looping to fetch each one's menu separately
const restaurants = await Restaurant.findAll();
for (const r of restaurants) {
  r.menuItems = await MenuItem.findAll({ where: { restaurantId: r.id } });  // N additional queries!
}

// CORRECT: eager-load via include — ONE query (or an efficiently batched one) instead of N+1
const restaurants = await Restaurant.findAll({ include: MenuItem });
```

---

## 🧠 Tricky Interview Question

```javascript
const order = await Order.create({ total: -500 });  // beforeCreate hook checks total >= 0
console.log('Reached here?');
```
Answer: **"Reached here?" is NEVER logged**, because the `beforeCreate` hook (defined in the advanced example) explicitly `throw`s an Error when `order.total < 0`. Sequelize hooks that throw PREVENT the operation from completing — `Order.create()` itself REJECTS (throws) rather than returning a created order, propagating the hook's error up to the caller. This is a classic interview trap: hooks aren't just "side-effect callbacks" — a throwing hook can abort the entire operation, acting as a enforcement layer similar to model-level `validate` rules, and the calling code's `await Order.create(...)` line itself throws, meaning any code AFTER it in a non-try-catch context never executes.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `sequelize.sync()` and migrations, and why are migrations preferred for production?
A1: `sync()` inspects your current model definitions and creates/alters tables to MATCH them directly — convenient for rapid prototyping, but destructive and unpredictable for production (it can't safely reconcile complex schema changes like renaming columns, and `force: true` drops tables entirely). Migrations are explicit, ordered, VERSIONED scripts (`up`/`down` functions) that describe INCREMENTAL schema changes, trackable in a `SequelizeMeta` table recording which migrations have run — allowing safe, auditable, repeatable schema evolution across dev/staging/production environments, and the ability to roll back a specific change if needed.

Q2: How do `hasMany`/`belongsTo` associations differ from `belongsToMany`?
A2: `hasMany`/`belongsTo` describe a ONE-TO-MANY relationship (one Restaurant has many MenuItems; each MenuItem belongs to one Restaurant) — implemented via a foreign key column on the "many" side's table. `belongsToMany` describes a MANY-TO-MANY relationship (an Order can have many MenuItems, and a MenuItem can appear in many Orders) — implemented via a JUNCTION/through table (e.g., `OrderItem`) holding foreign keys to both sides, often with extra columns of its own (like `quantity`).

Q3: What happens if you don't wrap related operations in a transaction in Sequelize?
A3: Each individual Sequelize call (`.create()`, `.update()`, etc.) runs as its own independent, auto-committed operation. If you perform multiple related writes WITHOUT a transaction (e.g., deduct stock, THEN create an order) and the second operation fails, the FIRST operation's change has already been permanently committed — leaving your data in an inconsistent state (stock deducted, but no corresponding order exists). Wrapping both in `sequelize.transaction()` ensures they either BOTH succeed (commit) or BOTH fail (rollback), maintaining consistency.

Q4: What's the purpose of `required: false` when using `include` for an association?
A4: By default, Sequelize's `include` generates an INNER JOIN — meaning parent records with NO matching related records are EXCLUDED from results entirely (e.g., a restaurant with zero pending orders wouldn't appear if filtering orders by `status: 'pending'` inside the include). Setting `required: false` changes this to a LEFT JOIN, including the parent record even if the association has no matches (the associated field would just be `null`/empty array) — important when you want "all restaurants, with their pending orders IF any exist" rather than "only restaurants that happen to have pending orders."

Q5: Why might you choose Sequelize over Prisma or TypeORM for a Node.js project?
A5: Sequelize has the LONGEST track record and widest community/plugin ecosystem among Node.js ORMs, broad multi-dialect support (MySQL, Postgres, SQLite, MSSQL, MariaDB) with mature dialect-specific feature support, and a flexible (if sometimes verbose) query API that handles complex associations well. Prisma offers a more modern DX with auto-generated type-safe client code and a declarative schema file (often preferred for TypeScript-first projects), while TypeORM leans more toward a Java/Spring-style decorator-based entity approach. Choice often comes down to team familiarity, TypeScript needs (Prisma's generated types are a strong draw), and existing codebase conventions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Standard relational CRUD-heavy applications where productivity, relationship handling, and migration tooling provide clear value over hand-written SQL.
- Multi-dialect portability matters (same codebase potentially targeting MySQL now, Postgres later).

❌ Avoid when:
- Extremely performance-critical, query-heavy workloads where ORM abstraction overhead is unacceptable — consider raw SQL or a lighter query builder (Knex) instead.
- Very simple projects with minimal DB interaction where the ORM's setup/learning overhead outweighs the benefit.

---

## 📊 Visual Diagram

```
SEQUELIZE ARCHITECTURE:
──────────────────────────────────────────────────────────

  Model Definition (JS)
       │
       ▼
  sequelize.define() / class extends Model
       │
       ├──► CRUD methods: findAll, findOne, create, update, destroy
       ├──► Associations: hasMany, belongsTo, belongsToMany
       ├──► Hooks: beforeCreate, afterCreate, beforeUpdate, ...
       └──► Validations: allowNull, min/max, custom validate fns
       │
       ▼
  Sequelize generates parameterized SQL internally
       │
       ▼
  Underlying driver (mysql2/pg/sqlite3) executes against DB
       │
       ▼
  Results hydrated back into Model instances (with .save(), .toJSON(), etc.)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model | JS representation of a database table | Database table का JS representation |
| Association | Defined relationship between models | Models के बीच defined relationship |
| Eager loading | Fetching related data via include/JOIN | Related data को include/JOIN से fetch करना |
| Hook | Lifecycle callback (before/after create etc.) | Lifecycle callback |
| Migration | Versioned schema change script | Versioned schema change script |
| sync() | Auto-create/alter tables from model definitions | Models से tables auto-create/alter करना |

---

## ⚡ 3-Line Summary
English:
1. Sequelize maps JS models to DB tables, providing CRUD methods, association-aware queries, hooks, and validations across multiple SQL dialects.
2. Use eager loading (`include`) to avoid N+1 queries, and `sequelize.transaction()` for atomic multi-step operations.
3. Never use `sync({ force: true })` in production — use migrations for real, trackable schema evolution.

Hindi:
1. Sequelize JS models को DB tables से map करता है, CRUD methods, association-aware queries, hooks, validations देता है।
2. N+1 queries से बचने के लिए eager loading (`include`) use करो, atomic operations के लिए `transaction()`।
3. Production में `sync({force:true})` कभी नहीं — migrations use करो trackable schema evolution के लिए।

---

## ➡️ Next Topic
**148. Sequelize Models + Migrations** — Model definitions, migration files, और schema versioning की practice।
