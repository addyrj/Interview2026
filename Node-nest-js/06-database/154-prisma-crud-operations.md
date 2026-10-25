# 154. Prisma CRUD Operations
# हिंदी में: Prisma CRUD Operations — Create, Read, Update, Delete

---

## 🔵 Simple Definition (English)
Prisma Client exposes typed CRUD methods on every model: `create`, `findMany`/`findUnique`/`findFirst`, `update`/`updateMany`, `delete`/`deleteMany`, plus `upsert` (update-or-create) and `createMany`. Every method takes a structured options object (`where`, `data`, `select`, `include`, `orderBy`, `take`, `skip`) instead of raw SQL, and returns fully typed results.

## 🔵 सरल परिभाषा (Hindi)
Prisma Client हर model पर typed CRUD methods देता है: `create`, `findMany`/`findUnique`/`findFirst`, `update`/`updateMany`, `delete`/`deleteMany`, और `upsert` (update-or-create), `createMany`। हर method structured options object (`where`, `data`, `select`, `include`, `orderBy`, `take`, `skip`) लेता है raw SQL की जगह, और fully typed results return करता है।

---

## 🔴 Problem it Solves
Writing raw SQL for every CRUD operation means hand-building query strings, manually escaping values (SQL injection risk), and manually parsing results into JS objects. Even query builders like Knex require learning a chainable API that doesn't give compile-time type checking. Prisma's CRUD methods are declarative, safe-by-default (parameterized under the hood, no injection risk), and fully typed — the returned object's shape matches your schema exactly, with autocomplete.

## 🔴 यह क्यों बना? (Hindi)
हर CRUD operation के लिए raw SQL लिखने में query strings hand-build करनी पड़तीं, values manually escape करनी पड़तीं (SQL injection risk), results manually parse करने पड़ते। Prisma के CRUD methods declarative हैं, safe-by-default (parameterized, injection risk नहीं), और fully typed — returned object schema से exactly match करता है, autocomplete के साथ।

---

## 🟢 How it Works — Step by Step

Step 1 → **Create**: `prisma.model.create({ data: {...} })` — inserts one row, returns it.
Step 2 → **Read**: `findUnique` (by unique field, returns one or null), `findFirst` (first match of any filter), `findMany` (array, supports pagination/filtering/sorting).
Step 3 → **Update**: `update({ where, data })` updates ONE record matched by a unique field; `updateMany({ where, data })` updates ALL matches.
Step 4 → **Delete**: `delete({ where })` removes one record; `deleteMany({ where })` removes all matches.
Step 5 → **Upsert**: `upsert({ where, update, create })` — updates if a match exists, otherwise creates a new record; atomic at the DB level.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Create**: `prisma.model.create({ data: {...} })` — एक row insert करता है, वही return करता है।
Step 2 → **Read**: `findUnique` (unique field से, एक या null), `findFirst` (पहला match), `findMany` (array, pagination/filtering/sorting के साथ)।
Step 3 → **Update**: `update({ where, data })` एक record update करता है; `updateMany` सभी matches update करता है।
Step 4 → **Delete**: `delete({ where })` एक record हटाता है; `deleteMany({ where })` सभी matches हटाता है।
Step 5 → **Upsert**: `upsert({ where, update, create })` — match मिला तो update, नहीं तो create; DB level पर atomic।

---

## 🟡 Real World Example
**Zomato's restaurant-onboarding service** uses `upsert` heavily when syncing restaurant data from an external partner feed: `prisma.restaurant.upsert({ where: { externalId }, update: { name, address, isOpen }, create: { externalId, name, address, isOpen } })`. This single atomic call handles both "new restaurant joining the platform" and "existing restaurant details changed" without needing a separate `findFirst` + conditional `create`/`update` (which would have a race condition under concurrent syncs).

## 🟡 Real Example Hindi mein
**Zomato की restaurant-onboarding service** external partner feed से restaurant data sync करते समय `upsert` बहुत use करती है। एक atomic call से दोनों case handle होते हैं — "नया restaurant" या "existing details बदले" — बिना separate `findFirst` + conditional `create`/`update` के (जिसमें concurrent syncs में race condition हो सकती)।

---

## 💻 Code Example — Basic

```javascript
// prisma-crud-basic.js
// Assumes schema.prisma has: model User { id Int @id @default(autoincrement()) email String @unique name String? }
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  // CREATE — insert one row
  const created = await prisma.user.create({
    data: { email: 'priya@example.com', name: 'Priya' },
  });
  console.log('Created:', created);

  // READ ONE (by unique field)
  const byEmail = await prisma.user.findUnique({ where: { email: 'priya@example.com' } });
  console.log('Found by email:', byEmail);

  // READ MANY (with filter, sort, limit)
  const recentUsers = await prisma.user.findMany({
    where: { name: { contains: 'P' } },   // SQL LIKE '%P%'
    orderBy: { id: 'desc' },
    take: 5,
  });
  console.log('Recent users matching "P":', recentUsers);

  // UPDATE — change one field on a specific record
  const updated = await prisma.user.update({
    where: { id: created.id },
    data: { name: 'Priya Sharma' },
  });
  console.log('Updated:', updated);

  // DELETE — remove the record
  const deleted = await prisma.user.delete({ where: { id: created.id } });
  console.log('Deleted:', deleted);

  await prisma.$disconnect();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// prisma-crud-advanced.js — Production patterns: pagination, upsert, batch ops, select
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// ─── 1. CURSOR-BASED PAGINATION (efficient for large tables) ─────────────────
async function getUsersPage(cursorId, pageSize = 20) {
  return prisma.user.findMany({
    take: pageSize,
    skip: cursorId ? 1 : 0,          // skip the cursor row itself
    cursor: cursorId ? { id: cursorId } : undefined,
    orderBy: { id: 'asc' },
    select: { id: true, email: true, name: true }, // only fetch needed columns
  });
}

// ─── 2. UPSERT (atomic update-or-create) ─────────────────────────────────────
async function syncRestaurantFromFeed(externalId, data) {
  return prisma.restaurant.upsert({
    where: { externalId },
    update: { name: data.name, isOpen: data.isOpen },
    create: { externalId, name: data.name, isOpen: data.isOpen },
  });
}

// ─── 3. BATCH OPERATIONS ─────────────────────────────────────────────────────
async function bulkDeactivateStaleProducts(productIds) {
  // updateMany returns { count: number }, not the updated rows
  const result = await prisma.product.updateMany({
    where: { id: { in: productIds } },
    data: { isActive: false },
  });
  console.log(`Deactivated ${result.count} products`);
  return result;
}

async function createManyOrders(orders) {
  // createMany is faster than looping create() — single INSERT with multiple VALUES
  return prisma.order.createMany({
    data: orders,
    skipDuplicates: true, // ignore rows that would violate a unique constraint
  });
}

// ─── 4. SELECT vs INCLUDE ────────────────────────────────────────────────────
async function getOrderSummary(orderId) {
  return prisma.order.findUnique({
    where: { id: orderId },
    select: {
      id: true,
      amount: true,
      user: { select: { name: true, email: true } }, // nested select
      items: { select: { productId: true, quantity: true } },
    },
  });
}

// ─── 5. CONDITIONAL FILTERS WITH AND/OR/NOT ──────────────────────────────────
async function searchOrders(filters) {
  return prisma.order.findMany({
    where: {
      AND: [
        { amount: { gte: filters.minAmount ?? 0 } },
        { status: { not: 'cancelled' } },
      ],
      OR: [
        { userId: filters.userId },
        { guestEmail: filters.guestEmail },
      ],
    },
  });
}

async function run() {
  try {
    await syncRestaurantFromFeed('ext-123', { name: 'Spice Garden', isOpen: true });
    await bulkDeactivateStaleProducts([1, 2, 3]);
    const page = await getUsersPage(null, 10);
    console.log('First page of users:', page);
  } catch (err) {
    console.error('CRUD operation failed:', err.message);
  } finally {
    await prisma.$disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express REST API using Prisma CRUD methods
const express = require('express');
const { PrismaClient } = require('@prisma/client');
const app = express();
app.use(express.json());
const prisma = new PrismaClient();

app.get('/api/orders', async (req, res) => {
  const page = Number(req.query.page) || 1;
  const pageSize = 20;
  const orders = await prisma.order.findMany({
    skip: (page - 1) * pageSize,
    take: pageSize,
    orderBy: { createdAt: 'desc' },
    include: { user: { select: { name: true } } },
  });
  res.json(orders);
});

app.patch('/api/orders/:id/cancel', async (req, res) => {
  try {
    const order = await prisma.order.update({
      where: { id: Number(req.params.id) },
      data: { status: 'cancelled' },
    });
    res.json(order);
  } catch (err) {
    if (err.code === 'P2025') { // "record not found" error
      return res.status(404).json({ error: 'Order not found' });
    }
    res.status(500).json({ error: 'Failed to cancel order' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `update()` with a non-unique `where` filter
```javascript
// Wrong — update() REQUIRES a unique field in `where`, not an arbitrary filter
await prisma.user.update({ where: { name: 'Priya' }, data: {...} });
// Throws: "Argument where of type UserWhereUniqueInput needs exactly one argument"

// Right — use updateMany for non-unique filters, or findFirst + update by id
await prisma.user.updateMany({ where: { name: 'Priya' }, data: {...} });
```

❌ Mistake 2: Looping `create()` calls instead of using `createMany()`
✅ Correct: `createMany` sends ONE SQL statement with multiple VALUES, far faster than N separate round trips.
```javascript
// Wrong — N round trips to the DB
for (const order of orders) { await prisma.order.create({ data: order }); }

// Right — one round trip
await prisma.order.createMany({ data: orders });
```

---

## 🧠 Tricky Interview Question

```javascript
const result = await prisma.user.updateMany({
  where: { email: 'nonexistent@example.com' },
  data: { name: 'Nobody' },
});
console.log(result);
```
Answer: Output is `{ count: 0 }` — NOT an error. Unlike `update()` (which throws `P2025` if no record matches a unique `where`), `updateMany()` NEVER throws for zero matches — it simply returns how many rows were affected. This distinction matters: code checking "did this succeed" must check `result.count > 0`, not rely on a try/catch, when using `updateMany`/`deleteMany`.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `findUnique`, `findFirst`, and `findMany`?
A1: `findUnique` requires a field marked `@id` or `@unique` in `where` and returns one record or `null`. `findFirst` accepts ANY filter (not necessarily unique) and returns the first matching record (or `null`) based on `orderBy`. `findMany` returns an ARRAY of all matching records, supporting pagination (`take`/`skip`/`cursor`) and sorting.

Q2: How does `upsert` work and when would you use it over separate create/update logic?
A2: `upsert({ where, update, create })` atomically checks if a record matching `where` exists: if yes, applies `update`; if no, runs `create`. It's a single DB operation, avoiding the race condition of manually doing `findFirst` then conditionally `create`/`update` (where two concurrent requests could both see "not found" and both try to create, causing a unique constraint violation).

Q3: What's the difference between `select` and `include` in a query?
A3: `select` explicitly picks ONLY the listed fields (and can nest to pick specific related fields too) — everything else is excluded from the result. `include` returns ALL scalar fields of the model PLUS the specified relations loaded. You can't mix `select` and `include` at the same level in one query — use nested `select` inside `include` if you need to pick specific related fields while still getting all parent fields.

Q4: Why does `updateMany`/`deleteMany` return `{ count }` instead of the updated/deleted records?
A4: Because these operations can affect MANY rows in one SQL statement (`UPDATE ... WHERE ...` / `DELETE ... WHERE ...`), returning all affected rows would require an extra `RETURNING`-style query that not all DB providers support efficiently. Prisma keeps it simple and fast: you just get the count of affected rows. If you need the actual updated rows, use `findMany` with the same `where` filter BEFORE or AFTER the operation.

Q5: How do you build complex filters using `AND`, `OR`, and `NOT` in Prisma?
A5: Prisma's `where` object supports `AND: [...]`, `OR: [...]`, and `NOT: {...}` as special keys, each taking an array (for AND/OR) or object (for NOT) of more `where` conditions. These can nest arbitrarily to express complex boolean logic, e.g., `where: { OR: [{ status: 'active' }, { AND: [{ status: 'pending' }, { amount: { gt: 1000 } }] }] }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Standard CRUD operations on relational data with typed, readable query syntax
- You want compile-time safety on filters, selects, and returned shapes
- Bulk insert/update scenarios where `createMany`/`updateMany` reduce round trips

❌ Avoid when:
- You need complex analytical queries (window functions, CTEs) — use `$queryRaw` for those
- Extremely performance-critical hot paths where even Prisma's query generation overhead matters (benchmark first before assuming this is a real bottleneck)

---

## 📊 Visual Diagram
```
PRISMA CRUD METHODS
──────────────────────────────────────────────
CREATE:  prisma.model.create({ data })        → 1 row
         prisma.model.createMany({ data: [] }) → N rows, 1 query

READ:    prisma.model.findUnique({ where })   → 1 row or null (unique field only)
         prisma.model.findFirst({ where })    → 1 row or null (any filter)
         prisma.model.findMany({ where })     → array

UPDATE:  prisma.model.update({ where, data })      → 1 row (unique field only)
         prisma.model.updateMany({ where, data })  → { count }

DELETE:  prisma.model.delete({ where })       → 1 row (unique field only)
         prisma.model.deleteMany({ where })   → { count }

UPSERT:  prisma.model.upsert({ where, update, create }) → atomic update-or-create
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create | Insert a new row | नया row insert करना |
| findMany | Fetch array of matching rows | Matching rows का array |
| upsert | Update if exists, else create | Exist करे तो update, नहीं तो create |
| select | Pick specific fields | Specific fields चुनना |
| include | Load related data too | Related data भी load करना |
| cursor pagination | Pagination using a unique pointer | Unique pointer से pagination |
| P2025 | Record not found error | Record not found error |

---

## ⚡ 3-Line Summary
English:
1. Prisma CRUD methods (`create`, `findMany`, `update`, `delete`, `upsert`) give fully typed, declarative data access without raw SQL.
2. `update`/`delete` need a unique `where`; `updateMany`/`deleteMany` work on any filter but return only a `{ count }`, never throwing on zero matches.
3. Use `createMany` for bulk inserts and `upsert` for atomic update-or-create — both avoid race conditions and extra round trips.

Hindi:
1. Prisma CRUD methods (`create`, `findMany`, `update`, `delete`, `upsert`) raw SQL के बिना fully typed data access देते हैं।
2. `update`/`delete` को unique `where` चाहिए; `updateMany`/`deleteMany` किसी भी filter पर काम करते हैं, सिर्फ `{ count }` return करते हैं।
3. Bulk insert के लिए `createMany` और atomic update-or-create के लिए `upsert` इस्तेमाल करो।

---

## ➡️ Next Topic
**155. Prisma Relations** — Modeling and querying 1-to-1, 1-to-many, and many-to-many relationships with `include`/nested writes.
