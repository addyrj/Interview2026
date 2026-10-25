# 151. Prisma ORM — Complete Guide
# हिंदी में: Prisma ORM — पूरी गाइड

---

## 🔵 Simple Definition (English)
**Prisma** is a modern, type-safe ORM (Object-Relational Mapper) for Node.js and TypeScript. It has three main parts: the **Prisma Schema** (defines your DB models in one file), **Prisma Migrate** (generates and runs SQL migrations from schema changes), and **Prisma Client** (an auto-generated, fully typed query builder for your models). Unlike Sequelize's class-based models, Prisma generates code FROM your schema file.

## 🔵 सरल परिभाषा (Hindi)
**Prisma** Node.js और TypeScript के लिए एक modern, type-safe ORM है। तीन main parts: **Prisma Schema** (एक file में सारे DB models define), **Prisma Migrate** (schema changes से SQL migrations generate+run करना), और **Prisma Client** (auto-generated, fully typed query builder)। Sequelize के class-based models के उलट, Prisma schema file से code generate करता है।

---

## 🔴 Problem it Solves
Traditional ORMs like Sequelize use JavaScript classes to define models, which means no compile-time type safety by default (in plain JS) and manual effort to keep TypeScript types in sync with the DB schema. Writing raw SQL gives full control but no autocomplete, no type checking on query results, and you must manually write migrations. Prisma solves this by generating a fully-typed client directly from a single schema file — autocomplete for every field, compile-time errors if you typo a column name, and migrations generated automatically from schema diffs.

## 🔴 यह क्यों बना? (Hindi)
Traditional ORMs (जैसे Sequelize) JavaScript classes से models define करते हैं — plain JS में compile-time type safety नहीं होती, TypeScript types manually sync रखनी पड़तीं। Raw SQL में full control है पर कोई autocomplete नहीं, query results पर type checking नहीं, migrations manually लिखनी पड़ती। Prisma एक schema file से पूरी तरह typed client generate करता है — हर field का autocomplete, column name typo पर compile-time error, और schema diffs से automatic migrations।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install prisma --save-dev` and `npm install @prisma/client`, then `npx prisma init`.
Step 2 → Define your DB connection and models in `prisma/schema.prisma` (the single source of truth).
Step 3 → Run `npx prisma migrate dev --name init` — Prisma generates SQL migration files AND applies them to the DB.
Step 4 → Run `npx prisma generate` — Prisma reads the schema and generates a fully typed `PrismaClient` in `node_modules/@prisma/client`.
Step 5 → Import `PrismaClient` in your app and call type-safe methods: `prisma.user.findMany()`, `prisma.user.create({ data: {...} })`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `prisma` (dev) + `@prisma/client`, फिर `npx prisma init`।
Step 2 → `prisma/schema.prisma` में DB connection + models define करो।
Step 3 → `npx prisma migrate dev --name init` — Prisma SQL migration files generate करता है AND DB पर apply करता है।
Step 4 → `npx prisma generate` — schema से fully typed `PrismaClient` generate होता है।
Step 5 → App में `PrismaClient` import करके type-safe methods call करो: `prisma.user.findMany()` etc.

---

## 🟡 Real World Example
**Razorpay's internal dashboard team** migrated from raw `pg` queries to Prisma for their merchant-settlements service. Before: every query was a hand-written SQL string with no compile-time check — a renamed column broke production silently. After Prisma: `schema.prisma` is the single source of truth; running `prisma generate` after any schema change immediately shows TypeScript errors in every file using the old field name, catching bugs before deploy. `prisma migrate dev` also keeps a versioned migration history, making rollbacks and team collaboration on schema changes much safer.

## 🟡 Real Example Hindi mein
**Razorpay की internal dashboard team** ने raw `pg` queries से Prisma में migrate किया merchant-settlements service के लिए। पहले: हर query hand-written SQL string थी, compile-time check नहीं था। Prisma के बाद: `schema.prisma` single source of truth है; schema change के बाद `prisma generate` चलाने पर पुराने field name इस्तेमाल करने वाली हर जगह TypeScript error दिखता है — deploy से पहले bug पकड़ में आ जाता है।

---

## 💻 Code Example — Basic

```javascript
// Step 1: prisma/schema.prisma (not JS, but shown for context)
/*
generator client {
  provider = "prisma-client-js"
}
datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
}
*/

// basic-prisma.js — after running `npx prisma migrate dev` and `npx prisma generate`
// npm install prisma @prisma/client
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient(); // single client instance, reused across the app

async function main() {
  // CREATE — fully typed, autocomplete works for every field
  const user = await prisma.user.create({
    data: { email: 'anita@example.com', name: 'Anita' },
  });
  console.log('Created:', user);

  // READ — findMany returns typed array of User objects
  const allUsers = await prisma.user.findMany();
  console.log('All users:', allUsers);

  // READ ONE — findUnique uses the @unique field
  const found = await prisma.user.findUnique({ where: { email: 'anita@example.com' } });
  console.log('Found by email:', found);

  // Always disconnect to close the DB connection pool cleanly
  await prisma.$disconnect();
}

main().catch(async (e) => {
  console.error(e);
  await prisma.$disconnect();
  process.exit(1);
});
```

## 💻 Code Example — Advanced

```javascript
// advanced-prisma.js — Production patterns: transactions, error handling, singleton client
const { PrismaClient, Prisma } = require('@prisma/client');

// Singleton pattern: prevents exhausting DB connections in dev (hot reload) / serverless
let prisma;
if (!global.__prisma) {
  global.__prisma = new PrismaClient({
    log: ['query', 'error', 'warn'], // log all queries — useful for debugging slow queries
  });
}
prisma = global.__prisma;

async function transferFunds(fromUserId, toUserId, amount) {
  try {
    // $transaction ensures ALL queries succeed together, or ALL roll back
    const result = await prisma.$transaction(async (tx) => {
      const sender = await tx.wallet.findUnique({ where: { userId: fromUserId } });
      if (!sender || sender.balance < amount) {
        throw new Error('Insufficient balance'); // throwing inside rolls back the transaction
      }

      const updatedSender = await tx.wallet.update({
        where: { userId: fromUserId },
        data: { balance: { decrement: amount } }, // atomic decrement at DB level
      });

      const updatedReceiver = await tx.wallet.update({
        where: { userId: toUserId },
        data: { balance: { increment: amount } }, // atomic increment at DB level
      });

      await tx.transaction.create({
        data: { fromUserId, toUserId, amount, status: 'completed' },
      });

      return { updatedSender, updatedReceiver };
    });

    return result;
  } catch (err) {
    // Prisma throws typed errors — check known error codes
    if (err instanceof Prisma.PrismaClientKnownRequestError) {
      // e.g., P2002 = unique constraint violation, P2025 = record not found
      console.error('Known Prisma error code:', err.code);
    }
    throw err;
  }
}

async function run() {
  try {
    await transferFunds(1, 2, 500);
    console.log('Transfer successful');
  } catch (err) {
    console.error('Transfer failed:', err.message);
  } finally {
    await prisma.$disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app using a single shared PrismaClient instance (recommended pattern)
const express = require('express');
const { PrismaClient } = require('@prisma/client');

const app = express();
app.use(express.json());
const prisma = new PrismaClient(); // created once, reused by every request

app.get('/api/users', async (req, res) => {
  const users = await prisma.user.findMany({
    orderBy: { createdAt: 'desc' },
    take: 20, // pagination limit
  });
  res.json(users);
});

app.post('/api/users', async (req, res) => {
  try {
    const user = await prisma.user.create({ data: req.body });
    res.status(201).json(user);
  } catch (err) {
    if (err.code === 'P2002') { // Prisma unique constraint error code
      return res.status(409).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: 'Failed to create user' });
  }
});

// Graceful shutdown: close Prisma's connection pool when server stops
process.on('SIGINT', async () => {
  await prisma.$disconnect();
  process.exit(0);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a new `PrismaClient` on every request
```javascript
// Wrong — exhausts DB connections, each client opens its own pool
app.get('/users', async (req, res) => {
  const prisma = new PrismaClient(); // new pool every request!
  res.json(await prisma.user.findMany());
});

// Right — create ONE client instance, reuse across all requests
const prisma = new PrismaClient(); // outside route handlers, module-level
app.get('/users', async (req, res) => res.json(await prisma.user.findMany()));
```

❌ Mistake 2: Forgetting to run `prisma generate` after editing `schema.prisma`
✅ Correct: After ANY change to `schema.prisma`, run `npx prisma generate` to regenerate the typed client — otherwise your code still uses the OLD types and new fields won't autocomplete or may error at runtime.

---

## 🧠 Tricky Interview Question

```javascript
// What's wrong with this, assuming `email` is marked @unique in schema.prisma?
const user = await prisma.user.create({ data: { email: 'a@a.com' } });
const user2 = await prisma.user.create({ data: { email: 'a@a.com' } }); // duplicate!
```
Answer: The second `create` call throws a `Prisma.PrismaClientKnownRequestError` with code `P2002` ("Unique constraint failed on the fields: (`email`)"). Prisma enforces the `@unique` constraint at the database level, and the client surfaces it as a typed, catchable error. Production code should wrap such calls in try/catch and check `err.code === 'P2002'` to return a friendly 409 Conflict response instead of crashing.

---

## ⚫ Interview Questions + Answers

Q1: What are the three main components of Prisma?
A1: (1) **Prisma Schema** (`schema.prisma`) — single file defining data source, models, and relations in Prisma's own DSL. (2) **Prisma Migrate** — CLI tool (`prisma migrate dev`/`deploy`) that generates versioned SQL migration files from schema changes and applies them. (3) **Prisma Client** — an auto-generated, fully type-safe query builder/ORM client (`@prisma/client`) created by running `prisma generate`, used in app code to query the DB.

Q2: How does Prisma achieve type safety that Sequelize doesn't have by default?
A2: Prisma generates TypeScript types directly FROM the schema file every time you run `prisma generate`. Every model field, relation, and query result is fully typed — autocomplete works, and typos in field names or wrong data types are caught at COMPILE TIME. Sequelize (in plain JS) has no such static generation step; even with `sequelize-typescript`, types must be manually kept in sync with decorators on classes.

Q3: What is `prisma migrate dev` vs `prisma migrate deploy`?
A3: `migrate dev` is for LOCAL development — it compares the schema to the DB, generates a new migration file, applies it, and regenerates the client; it may also reset the dev DB if migrations are out of sync. `migrate deploy` is for PRODUCTION/CI — it only applies existing, already-committed migration files in order, without generating new ones or prompting interactively. You never run `migrate dev` in production.

Q4: What does `prisma.$transaction()` do, and what are the two forms?
A4: It groups multiple queries so they succeed or fail together (atomicity). Two forms: (1) **Sequential array form**: `prisma.$transaction([query1, query2])` — runs an array of prepared queries in one transaction, simpler but can't contain conditional logic between queries. (2) **Interactive callback form**: `prisma.$transaction(async (tx) => {...})` — gives you a transaction client `tx` to run dependent queries with branching logic inside, rolling back everything if any step throws.

Q5: How does Prisma handle relations differently from Sequelize's `include`?
A5: Prisma uses `include` (load full related objects) or `select` (pick specific fields, including nested ones) directly in the query: `prisma.user.findMany({ include: { orders: true } })`. Unlike Sequelize, there's no need to call `.hasMany()`/`.belongsTo()` association setup separately — relations are declared once in the schema via `@relation` fields, and `include`/`select` work automatically off that schema definition, with fully typed nested results.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Working in TypeScript and want full type safety end-to-end from DB to API
- Starting a new project and want fast iteration with auto-generated migrations
- Team collaboration needs a single readable schema file as source of truth

❌ Avoid when:
- You need very complex, hand-tuned raw SQL queries that don't map well to Prisma's query API (though `$queryRaw` is available as an escape hatch)
- Working with legacy DB schemas that don't fit Prisma's conventions well (introspection helps, but can be messy)

---

## 📊 Visual Diagram
```
PRISMA WORKFLOW
──────────────────────────────────────────────
  schema.prisma (single source of truth)
         │
         ├──▶ npx prisma migrate dev ──▶ SQL migration files + applies to DB
         │
         └──▶ npx prisma generate ──▶ typed PrismaClient (node_modules/@prisma/client)
                     │
                     ▼
              Your app code
         const prisma = new PrismaClient()
         prisma.user.findMany()  ← fully typed, autocomplete
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| schema.prisma | Single schema definition file | एक ही schema definition file |
| PrismaClient | Auto-generated typed query client | Auto-generated typed query client |
| migrate dev | Dev migration command | Development migration command |
| migrate deploy | Prod migration command | Production migration command |
| $transaction | Atomic group of queries | Atomic queries का group |
| P2002 | Unique constraint error code | Unique constraint error code |
| introspection | Generate schema from existing DB | Existing DB से schema बनाना |

---

## ⚡ 3-Line Summary
English:
1. Prisma is a type-safe ORM built around a single `schema.prisma` file that generates both migrations and a fully typed client.
2. Use ONE `PrismaClient` instance per app (singleton) — never create one per request, or you exhaust DB connections.
3. `prisma migrate dev` is for local development; `prisma migrate deploy` is for production — never mix them up.

Hindi:
1. Prisma एक type-safe ORM है जो `schema.prisma` file से migrations और typed client दोनों generate करता है।
2. App में एक ही `PrismaClient` instance इस्तेमाल करो — हर request पर नया मत बनाओ।
3. `prisma migrate dev` local development के लिए, `prisma migrate deploy` production के लिए — mix मत करो।

---

## ➡️ Next Topic
**152. Prisma Schema** — Deep dive into model syntax, field types, attributes, and relations in `schema.prisma`.
