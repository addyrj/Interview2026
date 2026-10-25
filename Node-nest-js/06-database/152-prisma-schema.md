# 152. Prisma Schema
# हिंदी में: Prisma Schema — Models को Define करना

---

## 🔵 Simple Definition (English)
The **Prisma Schema** (`schema.prisma`) is a single declarative file that defines three things: the **datasource** (which DB and connection URL), the **generator** (what client to generate, e.g., `prisma-client-js`), and your **models** (tables, fields, types, relations, attributes). Everything Prisma does — migrations, the generated client, autocomplete — comes from this one file.

## 🔵 सरल परिभाषा (Hindi)
**Prisma Schema** (`schema.prisma`) एक declarative file है जो तीन चीज़ें define करती है: **datasource** (कौनसा DB और connection URL), **generator** (कौनसा client generate करना है), और **models** (tables, fields, types, relations, attributes)। Prisma जो भी करता है — migrations, generated client, autocomplete — सब इस एक file से आता है।

---

## 🔴 Problem it Solves
Before schema-first ORMs, a developer had to maintain the DB schema in SQL migration files AND separately maintain matching model classes/types in application code — two sources of truth that could drift apart. With Prisma's schema file, there's exactly ONE place to define a model, its field types, defaults, and relations. Both the migration SQL and the typed client are generated from this single file, eliminating drift.

## 🔴 यह क्यों बना? (Hindi)
Schema-first ORMs से पहले, developer को DB schema SQL migration files में और application code में model classes/types अलग-अलग maintain करने पड़ते — दो sources of truth जो अलग हो सकती थीं। Prisma schema file से सिर्फ एक जगह model define होता है — migration SQL और typed client दोनों इस एक file से generate होते हैं, drift खत्म।

---

## 🟢 How it Works — Step by Step

Step 1 → `datasource db { provider = "postgresql"; url = env("DATABASE_URL") }` — declares DB type + connection.
Step 2 → `generator client { provider = "prisma-client-js" }` — declares the client generator to run.
Step 3 → `model User { id Int @id @default(autoincrement()) email String @unique ... }` — declares a model with typed fields and attributes (`@id`, `@unique`, `@default`).
Step 4 → Relations are declared with `@relation` and foreign-key-like fields, e.g. `posts Post[]` on User, `author User @relation(fields: [authorId], references: [id])` on Post.
Step 5 → Run `npx prisma format` to auto-format, `npx prisma validate` to check syntax, and `npx prisma migrate dev` to apply changes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `datasource db` block — DB type + connection URL declare करता है।
Step 2 → `generator client` block — कौनसा client generate करना है declare करता है।
Step 3 → `model User {...}` — typed fields + attributes (`@id`, `@unique`, `@default`) के साथ model।
Step 4 → Relations `@relation` से declare होते हैं — जैसे `posts Post[]` और `author User @relation(...)`।
Step 5 → `prisma format` (auto-format), `prisma validate` (syntax check), `prisma migrate dev` (apply changes)।

---

## 🟡 Real World Example
**Flipkart's seller-dashboard microservice** keeps its entire DB structure — Sellers, Products, Inventory, Orders — in one `schema.prisma` file checked into git. A PR that changes a field type (e.g., `price Int` → `price Decimal`) shows up as a tiny, readable diff in code review, and the generated migration file documents exactly what SQL will run. New engineers onboard faster because the whole data model is readable in one file instead of scattered across dozens of model class files.

## 🟡 Real Example Hindi mein
**Flipkart की seller-dashboard microservice** अपना पूरा DB structure — Sellers, Products, Inventory, Orders — एक `schema.prisma` file में रखती है जो git में committed है। Field type बदलने वाला PR (जैसे `price Int` → `price Decimal`) एक छोटा, readable diff दिखाता है। नए engineers तेज़ी से समझ जाते हैं क्योंकि पूरा data model एक file में readable है।

---

## 💻 Code Example — Basic

```javascript
// schema.prisma (not JS — Prisma's own DSL — shown with full annotations)
/*
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"           // or "postgresql", "mysql"
  url      = "file:./dev.db"    // or env("DATABASE_URL") for real DBs
}

model User {
  id        Int      @id @default(autoincrement())  // primary key, auto-increments
  email     String   @unique                          // unique constraint
  name      String?                                   // "?" means optional (nullable)
  role      Role     @default(CUSTOMER)                // enum field with default
  posts     Post[]                                      // 1-to-many relation (no FK here)
  createdAt DateTime @default(now())                   // auto-set on create
  updatedAt DateTime @updatedAt                          // auto-updated on every save
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  content  String?
  authorId Int                                          // foreign key column
  author   User   @relation(fields: [authorId], references: [id])  // belongsTo
}

enum Role {
  CUSTOMER
  ADMIN
  SELLER
}
*/

// basic-schema-usage.js — using the generated client that matches the schema above
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  // Create a User — "role" defaults to CUSTOMER if omitted, matching @default
  const user = await prisma.user.create({
    data: { email: 'vikram@example.com', name: 'Vikram' },
  });
  console.log('New user (role defaulted):', user.role); // "CUSTOMER"

  // createdAt/updatedAt are set automatically by Prisma — no manual timestamps needed
  console.log('Timestamps:', user.createdAt, user.updatedAt);

  await prisma.$disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// advanced-schema-usage.js — composite keys, indexes, and cascading deletes
// schema.prisma excerpt (for context):
/*
model Product {
  id         Int      @id @default(autoincrement())
  sku        String
  warehouseId Int
  quantity   Int      @default(0)

  @@unique([sku, warehouseId])     // composite unique constraint (same SKU per warehouse only once)
  @@index([warehouseId])           // explicit index for faster lookups by warehouse
}

model Order {
  id        Int         @id @default(autoincrement())
  items     OrderItem[]
}

model OrderItem {
  id        Int     @id @default(autoincrement())
  orderId   Int
  order     Order   @relation(fields: [orderId], references: [id], onDelete: Cascade) // cascading delete
  productId Int
  quantity  Int
}
*/

const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient({ log: ['warn', 'error'] });

async function run() {
  try {
    // Upsert uses the composite @@unique([sku, warehouseId]) as the lookup key
    const product = await prisma.product.upsert({
      where: { sku_warehouseId: { sku: 'SHOE-42', warehouseId: 1 } }, // Prisma auto-names composite key
      update: { quantity: { increment: 10 } },
      create: { sku: 'SHOE-42', warehouseId: 1, quantity: 10 },
    });
    console.log('Upserted product:', product);

    // Create order with nested items in one call (nested writes)
    const order = await prisma.order.create({
      data: {
        items: {
          create: [
            { productId: product.id, quantity: 2 },
            { productId: product.id, quantity: 1 },
          ],
        },
      },
      include: { items: true }, // return with items eagerly loaded
    });
    console.log('Order with items:', order);

    // Deleting the order cascades to delete its OrderItems (onDelete: Cascade in schema)
    await prisma.order.delete({ where: { id: order.id } });
    const remainingItems = await prisma.orderItem.count({ where: { orderId: order.id } });
    console.log('Remaining order items after cascade delete:', remainingItems); // 0
  } catch (err) {
    console.error('Schema-driven operation failed:', err.message);
  } finally {
    await prisma.$disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express route demonstrating schema-driven validation (enum + required fields)
const express = require('express');
const { PrismaClient, Prisma } = require('@prisma/client');
const app = express();
app.use(express.json());
const prisma = new PrismaClient();

app.post('/api/users', async (req, res) => {
  try {
    // Passing an invalid enum value (e.g., role: "HACKER") throws a Prisma validation error
    const user = await prisma.user.create({ data: req.body });
    res.status(201).json(user);
  } catch (err) {
    if (err instanceof Prisma.PrismaClientValidationError) {
      // schema-defined type/enum mismatch caught before hitting the DB
      return res.status(400).json({ error: 'Invalid field value — check role/type' });
    }
    res.status(500).json({ error: 'Internal error' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Manually editing the DB schema without updating `schema.prisma`
✅ Correct: ALWAYS change `schema.prisma` first, then run `prisma migrate dev` to apply the change to the DB — editing the DB directly causes schema drift that Prisma will complain about (and may require `prisma db pull` to reconcile).

❌ Mistake 2: Forgetting `?` for optional fields, causing unwanted `NOT NULL` constraints
```javascript
// Wrong — "bio" becomes required (NOT NULL), breaks existing create calls without it
model User {
  bio String
}

// Right — "?" makes it optional/nullable
model User {
  bio String?
}
```

---

## 🧠 Tricky Interview Question

```prisma
model Post {
  id       Int  @id @default(autoincrement())
  authorId Int
  author   User @relation(fields: [authorId], references: [id])
}
```
What happens if you try `prisma.post.create({ data: { authorId: 999 } })` when no User with id 999 exists?

Answer: It throws a `PrismaClientKnownRequestError` with code `P2003` — "Foreign key constraint failed on the field: `authorId`". Prisma enforces referential integrity at the database level via the foreign key Prisma generates from the `@relation` declaration. The insert never happens; you must catch `P2003` and return a meaningful error (e.g., 400 "Invalid author ID") rather than letting it crash the request.

---

## ⚫ Interview Questions + Answers

Q1: What are the three blocks every `schema.prisma` file typically has?
A1: (1) `generator client` — specifies which client to generate (usually `prisma-client-js`). (2) `datasource db` — specifies the DB provider (`postgresql`, `mysql`, `sqlite`, `sqlserver`, `mongodb`) and connection `url` (usually from an env variable). (3) One or more `model` blocks — each defines a table's fields, types, and relations.

Q2: What do `@id`, `@unique`, `@default`, and `@updatedAt` do?
A2: `@id` marks the field as the primary key. `@unique` adds a unique constraint. `@default(value)` sets a default value when none is provided (e.g., `@default(now())`, `@default(autoincrement())`, `@default(uuid())`). `@updatedAt` automatically sets the field to the current timestamp every time the record is updated — no manual code needed.

Q3: What's the difference between `@unique` and `@@unique`?
A3: `@unique` (single `@`) is a FIELD attribute — applies a unique constraint to ONE field. `@@unique([field1, field2])` (double `@@`) is a BLOCK attribute — applies a COMPOSITE unique constraint across MULTIPLE fields together (e.g., `sku` can repeat across different warehouses, but not within the SAME `warehouseId`).

Q4: How are relations represented in the Prisma schema, and is a foreign key column always explicit?
A4: Relations use `@relation(fields: [...], references: [...])` on the "many" or "belongs-to" side, which explicitly declares the foreign key column (e.g., `authorId Int`). The "one" or "has-many" side (e.g., `posts Post[]` on `User`) is just a VIRTUAL field — Prisma doesn't create a column for it; it's purely for the client to know how to query/include related records.

Q5: What is `prisma format` and `prisma validate` used for?
A5: `prisma format` auto-formats the `schema.prisma` file (consistent indentation/alignment) and can auto-complete missing relation back-references. `prisma validate` checks the schema for syntax errors and semantic issues (e.g., missing `@relation` references) WITHOUT touching the database — useful in CI pipelines to catch schema mistakes before attempting a migration.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want ONE readable file documenting your entire data model, reviewable in PRs
- You need auto-generated, type-safe relation handling (`include`/`select`)
- You're starting fresh or willing to adopt Prisma's migration workflow

❌ Avoid when:
- Your DB schema is managed by another tool/team and Prisma would just be a secondary consumer (use introspection/`db pull` read-only instead, and avoid running migrations from Prisma)
- You need provider-specific DB features Prisma's DSL doesn't support yet (check `$queryRaw` escape hatch first)

---

## 📊 Visual Diagram
```
schema.prisma STRUCTURE
──────────────────────────────────────────────
generator client { provider = "prisma-client-js" }
        │
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }
        │
model User {
  id    Int    @id @default(autoincrement())
  email String @unique
  posts Post[]              ◄── virtual relation field (no column)
}
        │
model Post {
  id       Int  @id @default(autoincrement())
  authorId Int                              ◄── real FK column
  author   User @relation(fields: [authorId], references: [id])
}
        │
        ▼
   npx prisma generate ──▶ typed PrismaClient
   npx prisma migrate dev ──▶ SQL migration + DB update
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| datasource | DB connection config | DB connection config |
| generator | What client to generate | कौनसा client generate करना है |
| model | Table definition | Table की definition |
| @id | Primary key attribute | Primary key attribute |
| @relation | Declares a relation/FK | Relation/FK declare करना |
| @@unique | Composite unique constraint | Composite unique constraint |
| enum | Fixed set of allowed values | Fixed values का set |
| P2003 | Foreign key constraint error | Foreign key constraint error |

---

## ⚡ 3-Line Summary
English:
1. `schema.prisma` is the single source of truth defining datasource, generator, and all models with their fields and relations.
2. Field attributes (`@id`, `@unique`, `@default`) and block attributes (`@@unique`, `@@index`) control constraints at both column and table level.
3. Always edit `schema.prisma` first and run `prisma migrate dev` — never change the DB schema directly outside Prisma.

Hindi:
1. `schema.prisma` datasource, generator, और सारे models + relations की single source of truth है।
2. Field attributes (`@id`, `@unique`, `@default`) और block attributes (`@@unique`, `@@index`) constraints control करते हैं।
3. हमेशा `schema.prisma` पहले edit करो फिर `prisma migrate dev` चलाओ — DB को directly बाहर से मत बदलो।

---

## ➡️ Next Topic
**153. Prisma Migrations** — How `prisma migrate dev`/`deploy` generate and apply versioned SQL migrations from schema changes.
