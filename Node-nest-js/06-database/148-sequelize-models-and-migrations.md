# 148. Sequelize Models + Migrations
# हिंदी में: Sequelize Models + Migrations

---

## 🔵 Simple Definition (English)
**Models** in Sequelize define the SHAPE of your data (fields, types, validations, associations) as JavaScript. **Migrations** are versioned, ordered scripts that apply INCREMENTAL changes to the actual database schema (create table, add column, add index) — tracked so every environment's schema can be brought to the same, known state reliably.

## 🔵 सरल परिभाषा (Hindi)
**Models** Sequelize में आपके data की SHAPE define करते हैं (fields, types, validations, associations) JavaScript में। **Migrations** versioned, ordered scripts हैं जो actual database schema में incremental changes apply करते हैं (table create, column add, index add) — tracked होते हैं ताकि हर environment का schema reliably same known state में आए।

---

## 🔴 Problem it Solves
Models alone describe what the app EXPECTS the schema to look like, but don't track HOW the schema got there or handle changing it safely over time on a database that already has production data. Without migrations, schema changes become manual, undocumented, error-prone (`ALTER TABLE` run by hand on production, forgotten on staging, different order across environments) — leading to "works on my machine" schema drift. Migrations solve this by making every schema change an explicit, reviewable, version-controlled, and REVERSIBLE script, applied in a defined order and tracked in a `SequelizeMeta` table so the tool always knows exactly which migrations have run where.

## 🔴 यह क्यों बना? (Hindi)
Models सिर्फ यह describe करते हैं कि app schema को कैसा expect करती है, पर यह track नहीं करते कि schema वहाँ कैसे पहुंचा या existing production data वाले database पर उसे safely कैसे बदलें। Migrations के बिना schema changes manual, undocumented, error-prone हो जाते हैं। Migrations हर schema change को explicit, reviewable, version-controlled, और REVERSIBLE script बना देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install Sequelize CLI: `npm install --save-dev sequelize-cli`, initialize project structure: `npx sequelize-cli init` (creates `models/`, `migrations/`, `config/`, `seeders/` folders)
Step 2 → Generate a model + its matching migration together: `npx sequelize-cli model:generate --name Product --attributes name:string,price:decimal,stock:integer`
Step 3 → This creates `models/product.js` (the model definition) AND `migrations/XXXXXX-create-product.js` (the migration with `up`/`down` functions)
Step 4 → Review/edit the migration file — `up()` describes what to DO (create table), `down()` describes how to UNDO it (drop table) — critical for rollback safety
Step 5 → Apply migrations: `npx sequelize-cli db:migrate` — runs all PENDING migrations in order, recording each as applied in the `SequelizeMeta` table
Step 6 → Need to roll back? `npx sequelize-cli db:migrate:undo` reverts the LAST applied migration using its `down()` function
Step 7 → For LATER schema changes (not initial table creation), generate a new migration: `npx sequelize-cli migration:generate --name add-category-to-product` and manually write `addColumn`/`removeColumn` logic — never edit an already-applied migration file retroactively, always add a NEW one

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Sequelize CLI install करो, project structure initialize करो
Step 2 → Model + migration साथ generate करो
Step 3 → Model file और migration file बनती है
Step 4 → Migration file review करो — `up()` और `down()` दोनों
Step 5 → `db:migrate` से pending migrations apply करो
Step 6 → `db:migrate:undo` से rollback करो
Step 7 → Schema changes के लिए नई migration generate करो, पुरानी को edit मत करो

---

## 🟡 Real World Example
**Zomato's engineering team schema evolution:** When adding a `loyalty_points` column to the `customers` table, a developer creates a migration `20240315-add-loyalty-points-to-customers.js` with `up()` adding the column (default 0, nullable false after backfill) and `down()` removing it. This migration file is committed to git, reviewed in a PR like any code change, and applied identically across dev → staging → production via CI/CD running `npx sequelize-cli db:migrate` as a deployment step — ensuring every environment's schema evolves in lockstep, with a full audit trail in git history of every schema change ever made.

## 🟡 Real Example Hindi mein
**Zomato की engineering team schema evolution:** `customers` table में `loyalty_points` column add करते समय developer एक migration बनाता है `up()`/`down()` के साथ। यह migration git में commit होती है, PR में review होती है, CI/CD के through dev → staging → production में identically apply होती है।

---

## 💻 Code Example — Basic

```javascript
// models/product.js — a Sequelize model definition (typically generated + edited)

const { Model, DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  class Product extends Model {}

  Product.init(
    {
      name: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: { notEmpty: true },
      },
      price: {
        type: DataTypes.DECIMAL(10, 2),
        allowNull: false,
        validate: { min: 0 },
      },
      stock: {
        type: DataTypes.INTEGER,
        defaultValue: 0,
      },
    },
    {
      sequelize,       // the Sequelize connection instance (passed in from models/index.js)
      modelName: 'Product',
      tableName: 'products',   // explicit table name (otherwise Sequelize pluralizes modelName)
      timestamps: true,         // adds createdAt/updatedAt columns automatically
    }
  );

  return Product;
};

// migrations/20240101000000-create-product.js — the matching migration
'use strict';
module.exports = {
  // up() runs when applying this migration — creates the table
  async up(queryInterface, Sequelize) {
    await queryInterface.createTable('products', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER,
      },
      name: { type: Sequelize.STRING, allowNull: false },
      price: { type: Sequelize.DECIMAL(10, 2), allowNull: false },
      stock: { type: Sequelize.INTEGER, defaultValue: 0 },
      createdAt: { allowNull: false, type: Sequelize.DATE },
      updatedAt: { allowNull: false, type: Sequelize.DATE },
    });
  },

  // down() runs when rolling back — must UNDO exactly what up() did
  async down(queryInterface, Sequelize) {
    await queryInterface.dropTable('products');
  },
};
```

## 💻 Code Example — Advanced

```javascript
// migrations/20240315000000-add-category-and-index-to-products.js
// A later, incremental schema change — adding a column + index to an EXISTING table

'use strict';
module.exports = {
  async up(queryInterface, Sequelize) {
    // Use a TRANSACTION so multiple related schema changes are atomic
    await queryInterface.sequelize.transaction(async (t) => {
      // 1. Add the new column (nullable initially, to avoid failing on existing rows)
      await queryInterface.addColumn(
        'products',
        'category',
        { type: Sequelize.STRING, allowNull: true },
        { transaction: t }
      );

      // 2. Backfill existing rows with a default value before enforcing NOT NULL
      await queryInterface.sequelize.query(
        `UPDATE products SET category = 'uncategorized' WHERE category IS NULL`,
        { transaction: t }
      );

      // 3. NOW enforce NOT NULL, since all rows have a value
      await queryInterface.changeColumn(
        'products',
        'category',
        { type: Sequelize.STRING, allowNull: false, defaultValue: 'uncategorized' },
        { transaction: t }
      );

      // 4. Add an index for query performance (category is frequently filtered on)
      await queryInterface.addIndex('products', ['category'], { transaction: t });
    });
  },

  async down(queryInterface, Sequelize) {
    // Reverse EVERYTHING done in up(), in REVERSE order
    await queryInterface.sequelize.transaction(async (t) => {
      await queryInterface.removeIndex('products', ['category'], { transaction: t });
      await queryInterface.removeColumn('products', 'category', { transaction: t });
    });
  },
};

// seeders/20240101000001-demo-products.js — seed data (separate from migrations)
'use strict';
module.exports = {
  async up(queryInterface) {
    await queryInterface.bulkInsert('products', [
      { name: 'Wireless Mouse', price: 799, stock: 50, category: 'electronics', createdAt: new Date(), updatedAt: new Date() },
      { name: 'Keyboard', price: 1299, stock: 30, category: 'electronics', createdAt: new Date(), updatedAt: new Date() },
    ]);
  },
  async down(queryInterface) {
    await queryInterface.bulkDelete('products', null, {});
  },
};
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app using generated models, with migration-managed schema
const express = require('express');
const { Sequelize } = require('sequelize');

const app = express();
app.use(express.json());

// models/index.js pattern (simplified here): load config, init Sequelize, load all models
const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASSWORD, {
  host: process.env.DB_HOST,
  dialect: 'mysql',
  logging: false,
});

const Product = require('./models/product')(sequelize);  // model file exports a function(sequelize)

app.get('/products', async (req, res) => {
  try {
    const { category } = req.query;
    const products = await Product.findAll({
      where: category ? { category } : undefined,
      order: [['createdAt', 'DESC']],
    });
    res.json(products);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

app.post('/products', async (req, res) => {
  try {
    const product = await Product.create(req.body);
    res.status(201).json(product);
  } catch (err) {
    if (err.name === 'SequelizeValidationError') {
      return res.status(400).json({ errors: err.errors.map((e) => e.message) });
    }
    res.status(500).json({ error: 'Failed to create product' });
  }
});

async function start() {
  await sequelize.authenticate();  // confirm connection works
  // NOTE: schema itself is managed by migrations (run separately via CI/CD:
  //   npx sequelize-cli db:migrate
  // NOT by calling sequelize.sync() here — migrations are the source of truth)
  console.log('Connected to DB. Schema managed via migrations.');
  app.listen(3000, () => console.log('Server running on port 3000'));
}

start().catch((err) => { console.error(err); process.exit(1); });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing an already-applied migration file instead of creating a new one
```javascript
// WRONG: directly modifying migrations/20240101-create-product.js after it's already
// been run in production — the SequelizeMeta table thinks it's already applied,
// so the EDITED version never actually runs there; environments silently diverge!

// CORRECT: always create a NEW migration for any further schema change
// npx sequelize-cli migration:generate --name add-description-to-product
// Then write addColumn logic in the new file, leave the old one untouched
```

❌ Mistake 2: Adding a NOT NULL column directly without a default or backfill, on a table with existing rows
```javascript
// WRONG: fails immediately if the table already has rows (existing rows have no value for this column)
await queryInterface.addColumn('products', 'category', {
  type: Sequelize.STRING,
  allowNull: false,   // existing rows violate this constraint instantly!
});

// CORRECT: add nullable first, backfill data, THEN enforce NOT NULL (as shown in advanced example)
await queryInterface.addColumn('products', 'category', { type: Sequelize.STRING, allowNull: true });
// ... backfill ...
await queryInterface.changeColumn('products', 'category', { type: Sequelize.STRING, allowNull: false });
```

---

## 🧠 Tricky Interview Question

```javascript
// Migration A: creates table "orders"
// Migration B: adds column "status" to "orders"
// Developer runs: npx sequelize-cli db:migrate:undo:all
// Then runs: npx sequelize-cli db:migrate
// What's the final state of the "orders" table, and in what ORDER did operations run?
```
Answer: `db:migrate:undo:all` reverts ALL applied migrations in **REVERSE** order (most recent first) — so Migration B's `down()` (removing the `status` column) runs FIRST, then Migration A's `down()` (dropping the `orders` table entirely) runs SECOND, leaving NO `orders` table at all. Then `db:migrate` re-applies ALL pending migrations in their ORIGINAL defined order — Migration A's `up()` (create table) runs first, THEN Migration B's `up()` (add status column) runs second. Final state: the `orders` table exists again WITH the `status` column, functionally identical to before — but the key interview insight is understanding that `down()` ALWAYS runs in reverse chronological order relative to how `up()` was applied, since later migrations may depend on earlier ones existing.

---

## ⚫ Interview Questions + Answers

Q1: Why should migrations never be edited after they've been applied to any shared environment (staging/production)?
A1: Sequelize tracks which migrations have run via the `SequelizeMeta` table, keyed by migration FILENAME/timestamp — once recorded as "applied," running `db:migrate` again SKIPS that file entirely, regardless of its current content. If you edit an already-applied migration's code, environments where it was already run will NEVER see the edit (they already have the OLD version's effects), while a FRESH environment running migrations from scratch would apply the NEW edited version — causing silent schema drift between environments that's extremely hard to debug. Always create a new migration for further changes instead.

Q2: What's the difference between a migration and a seeder in Sequelize?
A2: A MIGRATION changes the SCHEMA (structure) of the database — creating/altering/dropping tables, columns, indexes. A SEEDER inserts/removes actual DATA (often sample/test data, or essential reference data like a list of valid categories) — it doesn't change structure, just populates rows. Both use similar `up`/`down` file conventions and CLI commands (`db:seed`, `db:seed:undo`), but conceptually they solve different problems: "what does the table look like" vs. "what data is in it."

Q3: Why is it important for a migration's `down()` function to correctly reverse its `up()` function?
A3: `down()` enables safe ROLLBACK if a migration causes problems in production (a bad deploy, unexpected data issue) — without a correct `down()`, you can't cleanly revert to the previous schema state, potentially leaving the database in a broken or inconsistent state during an incident. It also supports local development workflows (undoing/redoing migrations while iterating on schema design) and testing (spinning up a clean DB, migrating up, running tests, migrating back down).

Q4: How do you handle a migration that needs to run DATA transformation logic, not just schema changes (e.g., splitting a `fullName` column into `firstName`/`lastName`)?
A4: Write the migration's `up()` to: (1) add the new columns (`firstName`, `lastName`) as nullable, (2) run a data-transformation query/loop (`UPDATE` statements, or fetching rows in batches and processing in JS if logic is too complex for pure SQL) to populate them FROM the existing `fullName` data, (3) optionally make them NOT NULL after backfill, (4) optionally drop the old `fullName` column in the SAME or a LATER migration (often safer to drop in a separate, later migration after confirming the new columns work correctly in production). `down()` would need to reverse this — recombining `firstName`/`lastName` back into `fullName` if truly needed for rollback.

Q5: In a CI/CD pipeline, at what point should `db:migrate` run relative to deploying new application code?
A5: Generally, migrations should run BEFORE the new application code version starts receiving traffic — but with care for BACKWARD COMPATIBILITY during the transition: if old and new app code versions might run SIMULTANEOUSLY during a rolling deployment, the migration shouldn't break the OLD code (e.g., don't drop a column the old code still reads from). A common safe pattern: split breaking changes into multiple deploy cycles — first deploy adds new columns/tables (old code ignores them, new code can start using them), later deploy (after old code is fully retired) removes the old now-unused columns.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Sequelize-based project beyond a quick throwaway prototype — migrations are the standard, safe way to manage schema evolution across environments.

❌ Avoid when:
- Rapid local prototyping where you're still figuring out the model shape and don't yet have any real data to protect — `sequelize.sync()` is fine temporarily, switching to migrations once the schema stabilizes and real data exists.

---

## 📊 Visual Diagram

```
MIGRATION LIFECYCLE:
──────────────────────────────────────────────────────────

  Developer writes migration file (up/down functions)
       │
       ▼
  Commits to git, reviewed in PR
       │
       ▼
  CI/CD pipeline runs: npx sequelize-cli db:migrate
       │
       ▼
  Sequelize checks SequelizeMeta table:
    "which migrations have already run here?"
       │
       ▼
  Runs only PENDING migrations, in filename/timestamp order
       │
       ▼
  Records each as applied in SequelizeMeta
       │
       ▼
  Schema now matches the latest migration state
  (same process repeats identically across dev/staging/prod)

  ROLLBACK:  db:migrate:undo  →  runs LAST applied migration's down()
             db:migrate:undo:all → runs ALL applied migrations' down(), reverse order
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | Versioned script applying incremental schema change | Incremental schema change apply करने वाला versioned script |
| up() / down() | Apply change / reverse (rollback) that change | Change apply करना / उसे reverse करना |
| SequelizeMeta | Table tracking which migrations have run | कौन सी migrations चली हैं, track करने वाली table |
| Seeder | Script inserting/removing sample or reference data | Sample/reference data insert/remove करने वाला script |
| Backfill | Populating existing rows with a new column's value | Existing rows में नए column की value डालना |
| Schema drift | Environments having inconsistent database structures | Environments में inconsistent database structures |

---

## ⚡ 3-Line Summary
English:
1. Models define data shape in JS; migrations are versioned, trackable scripts that apply that shape to the actual database incrementally and safely.
2. Always create a NEW migration for further schema changes — never edit an already-applied one — and ensure `down()` correctly reverses `up()`.
3. For NOT NULL additions on existing tables, add nullable first, backfill data, then enforce the constraint in a later step.

Hindi:
1. Models JS में data shape define करते हैं; migrations versioned, trackable scripts हैं जो actual database में वह shape incrementally apply करते हैं।
2. आगे के schema changes के लिए हमेशा नई migration बनाओ — पुरानी को edit मत करो — और `down()` सही से `up()` reverse करे।
3. Existing tables पर NOT NULL column add करने के लिए पहले nullable add करो, backfill करो, फिर constraint enforce करो।

---

## ➡️ Next Topic
**149. MongoDB with Node.js — mongoose Basics** — NoSQL database integration और schema-less modeling की शुरुआत।
