# 185. Next.js + Prisma + PostgreSQL
# हिंदी में: Next.js + Prisma + PostgreSQL — Database के साथ Full-stack app

---

## 🔵 Simple Definition (English)
**Prisma** is an ORM that lets you define your database tables in a schema file and query them with type-safe JavaScript instead of raw SQL. With **PostgreSQL** as the database, you can read and write data directly in Next.js Server Components, Server Actions and Route Handlers.

## 🔵 सरल परिभाषा (Hindi)
**Prisma** एक ORM है जिसमें आप database की tables schema file में लिखते हैं और raw SQL की जगह type-safe JavaScript से query करते हैं। **PostgreSQL** database के साथ आप Next.js के Server Components, Server Actions और Route Handlers में सीधे data पढ़ और लिख सकते हैं।

---

## 🔴 Problem it Solves

Writing raw SQL strings in JavaScript is error-prone: typos are found at runtime, results have no types, schema changes break code silently, and SQL injection is a risk when strings are concatenated. Keeping the database schema and the code in sync by hand is painful. Prisma gives one source of truth (`schema.prisma`), generated types, safe parameterized queries and migrations.

```jsx
// PROBLEM: string SQL, no types, injection risk
const rows = await pool.query("SELECT * FROM orders WHERE user_id = '" + userId + "'");

// SOLUTION: typed, parameterized query
const orders = await prisma.order.findMany({ where: { userId } });
```

## 🔴 यह क्यों बना? (Hindi)
JavaScript में raw SQL strings लिखना गलतियों वाला है: typos runtime पर पता चलते हैं, results के types नहीं होते, schema बदलने पर code चुपचाप टूटता है, और strings जोड़ने पर SQL injection का खतरा रहता है। Database schema और code को हाथ से sync रखना दर्दनाक है। Prisma एक ही source of truth (`schema.prisma`), generated types, सुरक्षित parameterized queries और migrations देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install: npm i prisma -D && npm i @prisma/client, then npx prisma init
Step 2 → Put DATABASE_URL (postgresql://user:pass@host:5432/db) in .env
Step 3 → Define models in prisma/schema.prisma (User, Order, relations)
Step 4 → Run npx prisma migrate dev --name init → creates SQL migration + applies it
Step 5 → prisma generate creates a typed client in node_modules (runs after migrate)
Step 6 → Create ONE PrismaClient instance (singleton) in lib/prisma.js
Step 7 → Use it in Server Components, Server Actions and Route Handlers (server only)
Step 8 → Deploy: run npx prisma migrate deploy in production, not migrate dev

Never import prisma in a 'use client' file; it would leak secrets and fail to bundle
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install: npm i prisma -D && npm i @prisma/client, फिर npx prisma init
Step 2 → .env में DATABASE_URL (postgresql://user:pass@host:5432/db) रखो
Step 3 → prisma/schema.prisma में models लिखो (User, Order, relations)
Step 4 → npx prisma migrate dev --name init चलाओ → SQL migration बनता है और apply होता है
Step 5 → prisma generate node_modules में typed client बनाता है (migrate के बाद अपने आप चलता है)
Step 6 → lib/prisma.js में सिर्फ एक PrismaClient instance (singleton) बनाओ
Step 7 → इसे Server Components, Server Actions और Route Handlers (सिर्फ server) में इस्तेमाल करो
Step 8 → Deploy में production पर npx prisma migrate deploy चलाओ, migrate dev नहीं

'use client' file में prisma कभी import मत करो; secrets leak होंगे और bundle फेल होगा
```

---

## 🟡 Real World Example
**Swiggy-style orders:** A `User` has many `Order`s, and each `Order` has many `OrderItem`s pointing to a `MenuItem`. The "My Orders" page is a Server Component that runs one Prisma query with `include` to load orders and their items, newest first. Placing an order is a Server Action that creates the order and its items inside one `$transaction`, so a payment failure never leaves a half-created order.

## 🟡 Real Example Hindi mein
**Swiggy जैसे orders:** एक `User` के कई `Order` होते हैं, और हर `Order` में कई `OrderItem` होते हैं जो `MenuItem` को point करते हैं। "My Orders" page एक Server Component है जो `include` के साथ एक Prisma query चलाकर orders और उनके items नए से पुराने क्रम में लाता है। Order देना एक Server Action है जो order और items को एक `$transaction` में बनाता है, ताकि payment फेल होने पर आधा बना order न बचे।

---

## 💻 Code Example — Basic

```prisma
// prisma/schema.prisma: describes tables and relations
generator client {
  provider = "prisma-client-js"            // generates the JS client
}

datasource db {
  provider = "postgresql"                  // database type
  url      = env("DATABASE_URL")           // connection string from .env
}

model User {
  id     Int     @id @default(autoincrement()) // primary key
  email  String  @unique                       // no two users with same email
  name   String?                               // optional column
  orders Order[]                               // one user → many orders
}

model Order {
  id        Int      @id @default(autoincrement())
  total     Int                                // amount in rupees
  status    String   @default("PLACED")        // default value
  createdAt DateTime @default(now())           // auto timestamp
  userId    Int
  user      User     @relation(fields: [userId], references: [id]) // foreign key
}
```

```jsx
// lib/prisma.js: singleton so hot reload does not open hundreds of connections
import { PrismaClient } from '@prisma/client';                // generated client

const globalForPrisma = globalThis;                           // survives dev hot reloads

export const prisma =
  globalForPrisma.prisma ?? new PrismaClient();               // reuse if it already exists

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;                            // cache only in development
}
```

## 💻 Code Example — Advanced

```jsx
// app/orders/page.jsx: Server Component reading from the database
import { prisma } from '@/lib/prisma';                        // server-only import

export const dynamic = 'force-dynamic';                       // always fetch fresh data (no static cache)

export default async function OrdersPage() {
  const orders = await prisma.order.findMany({                // SELECT ... FROM "Order"
    where: { status: { not: 'CANCELLED' } },                  // filter
    orderBy: { createdAt: 'desc' },                           // newest first
    take: 20,                                                 // pagination limit
    select: {                                                 // only needed columns (smaller payload)
      id: true, total: true, status: true, createdAt: true,
      user: { select: { name: true } },                       // join the user's name
    },
  });

  return (
    <ul>
      {orders.map(o => (
        <li key={o.id}>
          #{o.id} · {o.user.name ?? 'Guest'} · ₹{o.total} · {o.status}
        </li>
      ))}
    </ul>
  );
}
```

```jsx
// app/orders/actions.js: Server Action writing inside a transaction
'use server';
import { prisma } from '@/lib/prisma';
import { revalidatePath } from 'next/cache';

export async function placeOrder(userId, total) {
  if (!Number.isInteger(total) || total <= 0) {               // validate before touching the DB
    return { ok: false, error: 'Invalid total' };
  }
  try {
    const order = await prisma.$transaction(async (tx) => {   // all-or-nothing
      const created = await tx.order.create({ data: { userId, total } }); // INSERT order
      await tx.user.update({                                  // example second write
        where: { id: userId },
        data: { name: { set: undefined } },                   // placeholder update (no-op)
      });
      return created;
    });
    revalidatePath('/orders');                                // refresh the list page
    return { ok: true, id: order.id };
  } catch (e) {
    console.error(e);                                         // log the real error on the server
    return { ok: false, error: 'Could not place order' };     // generic message to the client
  }
}
```

---

## 🟠 Real App Integration

Add scripts and a seed file so teammates and CI get the same database. In `package.json` add `"postinstall": "prisma generate"` so Vercel builds generate the client. Use a pooled connection string (PgBouncer, Neon, Supabase pooler) on serverless platforms.

```jsx
// prisma/seed.js: run with `npx prisma db seed` (configure "prisma.seed" in package.json)
const { PrismaClient } = require('@prisma/client');          // CommonJS for a plain Node script
const prisma = new PrismaClient();

async function main() {
  await prisma.user.upsert({                                 // create if missing, else update
    where: { email: 'aditya@example.com' },
    update: {},
    create: { email: 'aditya@example.com', name: 'Aditya', orders: { create: [{ total: 499 }] } },
  });
}

main()
  .catch(e => { console.error(e); process.exit(1); })        // fail the script on error
  .finally(() => prisma.$disconnect());                      // always close the connection
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating `new PrismaClient()` in every file or request
✅ **Correct:** Use one shared instance from `lib/prisma.js`

```jsx
// Wrong: each hot reload / request opens new connections → "too many connections"
export async function GET() {
  const prisma = new PrismaClient();                         // ❌
  return Response.json(await prisma.user.findMany());
}

// Right
import { prisma } from '@/lib/prisma';                       // ✅ singleton
export async function GET() { return Response.json(await prisma.user.findMany()); }
```

❌ **Mistake 2:** Sending whole database rows to the client (passwords, internal fields)
✅ **Correct:** Use `select` to return only the fields the UI needs

```jsx
// Wrong: leaks every column, including passwordHash
const user = await prisma.user.findUnique({ where: { id } });          // ❌
return <ClientProfile user={user} />;

// Right
const user = await prisma.user.findUnique({
  where: { id },
  select: { id: true, name: true, email: true },                        // ✅ safe subset
});
```

---

## 🧠 Tricky Interview Question

```jsx
// lib/db.js
import { PrismaClient } from '@prisma/client';
export const prisma = new PrismaClient();
```
In development, after saving files many times, the terminal shows "Too many connections". Why, and what is the fix?

**Answer:** Next.js hot reloading re-evaluates modules on every change, so `new PrismaClient()` runs again each time, and each client opens its own connection pool while old ones are not closed. After many saves the database hits its connection limit. The fix is the singleton pattern: store the client on `globalThis` in development so reloads reuse it (shown in `lib/prisma.js` above). In production, modules load once per instance, but on serverless you may still need a pooled connection URL, because each function instance can open its own connections.

---

## ⚫ Interview Questions + Answers

Q1: What is Prisma and why use it?
A1: A type-safe ORM with a schema file, migrations and a generated client. It reduces SQL mistakes, gives autocomplete and types, and parameterizes queries to prevent SQL injection.

Q2: Where can you call Prisma in Next.js?
A2: In server code only: Server Components, Server Actions, Route Handlers and middleware on Node (not Edge, unless using a driver adapter; version-dependent). Never in Client Components.

Q3: What is the difference between `migrate dev` and `migrate deploy`?
A3: `migrate dev` creates new migrations from schema changes and applies them in development (it may reset data). `migrate deploy` only applies existing migrations in production and never creates or resets.

Q4: How do you avoid N+1 queries?
A4: Use `include` or `select` with relations so Prisma loads related rows together, instead of querying inside a loop.

Q5: How do you do multiple writes atomically?
A5: With `prisma.$transaction([...])` or an interactive `$transaction(async tx => {...})`, so all succeed or all roll back.

---

## 🔷 When to Use + When Not to Use
✅ **Use Prisma + PostgreSQL when:**
- You need relational data (users, orders, items) with constraints
- You want type safety and migrations in a TypeScript or JavaScript team
- You build a full-stack Next.js app with Server Components and Actions

❌ **Avoid / reconsider when:**
- You need extreme raw-SQL performance tuning (use SQL or a query builder like Drizzle or Kysely)
- You run on Edge runtimes without a driver adapter (version-dependent)
- Your data is simple key-value or document data (a different store may fit)

---

## 📊 Visual Diagram

```
  schema.prisma ──migrate dev──► SQL migrations ──► PostgreSQL tables
        │
        └─generate─► @prisma/client (typed)

  Request: GET /orders
        │
        ▼
  Server Component (app/orders/page.jsx)
        │  prisma.order.findMany(...)
        ▼
  lib/prisma.js (singleton, connection pool)
        │  parameterized SQL
        ▼
  PostgreSQL ──rows──► typed JS objects ──► HTML sent to the browser

  Re-render behavior: queries run on the server per request (or once if cached);
  Client Components never touch the DB and only re-render from props/state.
  Performance: use select, indexes (@@index), pagination and a pooled connection.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Maps tables to objects | Tables को objects से जोड़ना |
| schema.prisma | File defining models | Models वाली file |
| Migration | Versioned DB change | Database बदलाव का versioned record |
| PrismaClient | Generated query client | Generated query client |
| Singleton | Only one shared instance | सिर्फ एक shared instance |
| Relation | Link between models | Models के बीच संबंध |
| Transaction | All-or-nothing operations | सब सफल या कुछ नहीं |
| Connection pool | Reused DB connections | दोबारा इस्तेमाल होने वाले connections |

---

## ⚡ 3-Line Summary
**English:**
1. Prisma defines the schema once, generates typed queries and migrations, and works with PostgreSQL.
2. Create a single PrismaClient and use it only in server code (Server Components, Actions, Route Handlers).
3. Use `select`, transactions, pooling and `migrate deploy` for safe, fast production use.

**Hindi:**
1. Prisma schema एक बार लिखवाता है, typed queries और migrations बनाता है, और PostgreSQL के साथ चलता है।
2. सिर्फ एक PrismaClient बनाओ और उसे केवल server code (Server Components, Actions, Route Handlers) में इस्तेमाल करो।
3. सुरक्षित और तेज़ production के लिए `select`, transactions, pooling और `migrate deploy` इस्तेमाल करो।

---

## ➡️ Next Topic
**186. Next.js Authentication (NextAuth)** — Auth.js/NextAuth से login, sessions, OAuth providers (Google) और protected routes बनाना।
