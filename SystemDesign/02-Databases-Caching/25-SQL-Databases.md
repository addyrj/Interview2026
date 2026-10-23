# 25. SQL Databases (MySQL / PostgreSQL)
# हिंदी में: SQL Database — डेटा को टेबल (rows और columns) में रखने वाला, रिश्तों (relations) और नियमों के साथ भरोसेमंद डेटाबेस

---

## 🔵 Simple Definition (English)
A **SQL (relational) database** stores data in **tables** of rows and columns with a fixed **schema**. Tables are linked with **keys** (primary key, foreign key), and you query them using **SQL** (Structured Query Language). They guarantee **ACID transactions**: correct, consistent data even with many users at once.
Popular ones: **PostgreSQL, MySQL**, SQL Server, Oracle, SQLite.

## 🔵 सरल परिभाषा (Hindi)
SQL Database डेटा को टेबल में रखता है (जैसे Excel शीट — rows और columns), हर टेबल का तय ढाँचा (schema) होता है।
टेबल आपस में keys से जुड़ी होती हैं, और SQL भाषा से डेटा पढ़ा/लिखा जाता है। ACID की वजह से डेटा हमेशा सही रहता है।

---

## 🔴 Problem it Solves
Before relational DBs (1970s), data lived in files or hierarchical/network databases:
- Each app had its own file format; **duplicated data** got out of sync (customer address in 5 files).
- To answer a new question ("orders by city last month"), you had to **write a new program**.
- Concurrent updates **corrupted** data; crashes left half-written records.

Relational DBs (E. F. Codd's model) gave:
1. **One structured source of truth** with relationships instead of duplicates.
2. **Declarative queries:** say *what* you want (SQL), and the DB figures out *how*.
3. **Integrity:** constraints (NOT NULL, UNIQUE, FOREIGN KEY, CHECK).
4. **Transactions:** all-or-nothing updates, safe concurrency, crash recovery.

## 🔴 यह क्यों बना? (Hindi)
पहले डेटा अलग-अलग फ़ाइलों में होता था — एक ही जानकारी कई जगह, जो आपस में मेल नहीं खाती थी, और हर नए सवाल के लिए नया प्रोग्राम लिखना पड़ता था।
Relational DB ने एक जगह, रिश्तों के साथ, नियमों के साथ डेटा दिया; SQL से कोई भी सवाल पूछ सकते हो, और transaction से डेटा कभी आधा-अधूरा नहीं बचता।

---

## 🟢 How it Works — Step by Step

### Tables, keys and relationships

```
users                              orders                                order_items
┌────┬────────┬─────────────┐      ┌─────┬─────────┬────────┬────────┐   ┌────┬──────────┬────────────┬─────┐
│ id │ name   │ email (UQ)  │      │ id  │ user_id │ status │ total  │   │ id │ order_id │ product_id │ qty │
├────┼────────┼─────────────┤      ├─────┼─────────┼────────┼────────┤   ├────┼──────────┼────────────┼─────┤
│ 1  │ Aditya │ a@x.com     │◄──┐  │ 101 │ 1  (FK) │ PAID   │ 450.00 │◄──│ 1  │ 101 (FK) │ 7          │ 2   │
│ 2  │ Riya   │ r@x.com     │   └──│ 102 │ 1       │ PLACED │ 120.00 │   │ 2  │ 101      │ 9          │ 1   │
└────┴────────┴─────────────┘      └─────┴─────────┴────────┴────────┘   └────┴──────────┴────────────┴─────┘
 PK = primary key (unique row id)    FK = foreign key (points to another table's PK)

Relationships:
  1 : 1   user ↔ user_profile
  1 : N   user → orders
  N : M   orders ↔ products (via order_items "join table")
```

### SQL basics (you must write these fluently)

```sql
-- Create with constraints
CREATE TABLE orders (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id),
  status      TEXT   NOT NULL CHECK (status IN ('PLACED','PAID','DELIVERED','CANCELLED')),
  total       NUMERIC(10,2) NOT NULL CHECK (total >= 0),   -- money: NUMERIC, never FLOAT
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- JOIN: orders with user names
SELECT o.id, u.name, o.total
FROM orders o JOIN users u ON u.id = o.user_id
WHERE o.created_at >= now() - interval '7 days';

-- Aggregate: revenue per user
SELECT user_id, COUNT(*) AS orders, SUM(total) AS revenue
FROM orders WHERE status = 'PAID'
GROUP BY user_id HAVING SUM(total) > 1000
ORDER BY revenue DESC LIMIT 10;

-- Transaction: all or nothing
BEGIN;
  UPDATE wallets SET balance = balance - 450 WHERE user_id = 1 AND balance >= 450;
  INSERT INTO orders(user_id, status, total) VALUES (1, 'PAID', 450);
COMMIT;   -- or ROLLBACK on error
```

### JOIN types

```
INNER JOIN  → only matching rows in both
LEFT JOIN   → all from left + matches (NULL if none)   e.g. users with or without orders
RIGHT JOIN  → mirror of left
FULL JOIN   → everything from both
CROSS JOIN  → every combination (rarely wanted)
```

### What happens inside when you run a query

```
SQL text
  │ 1. Parser       → syntax tree
  │ 2. Planner/Optimizer → chooses plan: which index? join order? hash vs nested loop?
  │                         (uses table statistics — keep ANALYZE up to date)
  │ 3. Executor     → reads pages from shared buffers (RAM) or disk
  │ 4. WAL          → for writes: change first written to Write-Ahead Log (durability),
  │                   then data pages updated later (checkpoint)
  ▼
Result rows
```

### Storage basics (Postgres)
```
- Data stored in 8 KB pages; tables = "heap" files
- Indexes (B-tree by default) point to row locations   (Topic 28)
- MVCC: updates create new row versions; VACUUM cleans old ones (Topic 37)
- WAL (write-ahead log): crash recovery + replication source (Topic 40)
```

### PostgreSQL vs MySQL (interview favourite)

```
┌──────────────────────┬────────────────────────────────┬────────────────────────────────┐
│                      │ PostgreSQL                     │ MySQL (InnoDB)                 │
├──────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ Philosophy           │ Feature-rich, standards-strict │ Simple, fast reads, popular    │
│ JSON                 │ JSONB + GIN indexes (excellent)│ JSON type (good, less indexing)│
│ Advanced types       │ arrays, ranges, enums, UUID,   │ fewer                          │
│                      │ PostGIS (geo), pgvector (AI)   │                                │
│ Indexes              │ B-tree, GIN, GiST, BRIN, hash, │ B-tree, full-text, spatial     │
│                      │ partial & expression indexes   │ (functional idx in 8.0)        │
│ Concurrency          │ MVCC (row versions in table)   │ MVCC (undo logs)               │
│ Replication          │ streaming + logical            │ binlog-based, very mature      │
│ Extensions           │ huge ecosystem                 │ limited                        │
│ Used by              │ Instagram, Zerodha, Razorpay,  │ Facebook, Uber (early), Swiggy,│
│                      │ Supabase, most new startups    │ Flipkart, WordPress, Shopify   │
└──────────────────────┴────────────────────────────────┴────────────────────────────────┘
Default choice today for a new product: PostgreSQL.
```

### When SQL is the right choice
```
✅ Structured data with relationships (users, orders, payments, inventory)
✅ Need transactions & strong consistency (money!)
✅ Complex queries, reporting, joins, aggregations
✅ Data integrity rules enforced by the DB
⚠️ Harder: horizontal write scaling (sharding), very flexible/changing schemas,
   massive write-heavy event data → consider NoSQL / specialized stores (Topic 26–27)
```

## 🟢 कैसे काम करता है? (Hindi)
1. डेटा टेबल में रहता है; हर row की पहचान Primary Key से, और दूसरी टेबल से रिश्ता Foreign Key से।
2. SQL में बताते हो "क्या चाहिए" (SELECT … JOIN … WHERE), DB का optimizer तय करता है "कैसे लाना है" (कौन-सा index)।
3. लिखने से पहले बदलाव WAL (log) में जाता है, ताकि crash होने पर भी डेटा न खोए।
4. Transaction (BEGIN … COMMIT) में या तो सारे बदलाव होंगे या एक भी नहीं।
5. नए प्रोजेक्ट के लिए PostgreSQL सबसे अच्छा default है; पैसे और रिश्तों वाले डेटा के लिए SQL ही चुनो।

---

## 🟡 Real World Example

**Instagram** — started on PostgreSQL and scaled it with sharding (thousands of logical shards across Postgres servers) to billions of photos. User, media and relationship data is relational.

**Zerodha** — India's largest stockbroker runs heavily on PostgreSQL, including multi-terabyte databases for trade and reporting data, with a small, expert team.

**Uber's MySQL story** — Uber moved from Postgres to MySQL (2016) for its replication behaviour and its own schemaless layer on top. It's a famous example that both are viable at massive scale, and the choice depends on workload and team.

**Banks and UPI** — core banking ledgers are relational (Oracle/Postgres/DB2) because double-entry accounting needs ACID transactions.

## 🟡 Real Example Hindi में
Instagram ने PostgreSQL से शुरुआत की और sharding से अरबों फ़ोटो तक स्केल किया। Zerodha का ज़्यादातर सिस्टम PostgreSQL पर चलता है।
बैंक और UPI के ledger हमेशा SQL DB में होते हैं, क्योंकि पैसे के लेन-देन में ACID transaction ज़रूरी है।

---

## 🟠 My Stack Example

### Node.js — pg with parameterized queries (prevents SQL injection)
```js
import pg from 'pg';
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 10 });

// ❌ NEVER: `SELECT * FROM users WHERE email = '${email}'`  → SQL injection
// ✅
const { rows } = await pool.query('SELECT id, name FROM users WHERE email = $1', [email]);

// Transaction
const client = await pool.connect();
try {
  await client.query('BEGIN');
  const { rows: [w] } = await client.query(
    'UPDATE wallets SET balance = balance - $1 WHERE user_id = $2 AND balance >= $1 RETURNING balance', [amt, uid]);
  if (!w) throw new Error('INSUFFICIENT_FUNDS');
  await client.query('INSERT INTO orders(user_id, status, total) VALUES ($1, $2, $3)', [uid, 'PAID', amt]);
  await client.query('COMMIT');
} catch (e) { await client.query('ROLLBACK'); throw e; }
finally { client.release(); }
```

### Node.js — Prisma ORM (schema-first, migrations)
```prisma
model User  { id Int @id @default(autoincrement())  email String @unique  orders Order[] }
model Order { id Int @id @default(autoincrement())  userId Int  user User @relation(fields:[userId], references:[id])
              total Decimal @db.Decimal(10,2)  status String  createdAt DateTime @default(now())
              @@index([userId, createdAt]) }
```
```js
await prisma.$transaction(async (tx) => {
  await tx.wallet.update({ where: { userId }, data: { balance: { decrement: amt } } });
  await tx.order.create({ data: { userId, total: amt, status: 'PAID' } });
});
```

### FastAPI — SQLAlchemy 2.0 async
```python
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str]

async with session.begin():                     # transaction
    session.add(Order(user_id=uid, total=amt, status="PAID"))
```

### Migrations — never edit prod schema by hand
```bash
npx prisma migrate dev --name add_orders_index     # Node (or knex / TypeORM / drizzle-kit)
alembic revision --autogenerate -m "add orders"     # Python
alembic upgrade head
```

### Docker
```yaml
services:
  db:
    image: postgres:16
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: secret, POSTGRES_DB: app }
    volumes: [pgdata:/var/lib/postgresql/data]   # persist data!
    ports: ["127.0.0.1:5432:5432"]
volumes: { pgdata: {} }
```

### Production: AWS RDS / Aurora PostgreSQL
Multi-AZ, automated backups + PITR, Performance Insights, parameter groups, read replicas.

---

## ⚫ Interview Questions + Answers

**Q1: What is a relational database and when would you choose one?**
A1: A database that stores data in tables with a fixed schema, related through primary and foreign keys, queried with SQL, and providing ACID transactions and integrity constraints. Choose it for structured, related data needing consistency: users, orders, payments, inventory, bookings. Also when you need complex queries, joins and reporting, or when correctness matters more than extreme write scale.

**Q2: PostgreSQL vs MySQL — which would you pick and why?**
A2: Both are excellent, ACID-compliant and battle-tested at scale. Postgres has richer features: JSONB with GIN indexes, advanced index types (partial, expression, GIN/GiST/BRIN), extensions (PostGIS, pgvector, TimescaleDB), strong standards compliance and logical replication. MySQL is simpler to operate for some teams, with very mature replication tooling and great read performance, and is widely used in legacy stacks. For a new product I'd default to Postgres unless the team or ecosystem strongly favours MySQL.

**Q3: What is SQL injection and how do you prevent it?**
A3: An attack where user input is concatenated into SQL so it changes the query, e.g. `' OR '1'='1`, which can dump or delete data. Prevent it with parameterized queries or prepared statements (`$1` placeholders), ORMs/query builders that parameterize, input validation, and least-privilege DB users (no DROP rights for the app). Never build SQL with string interpolation.

**Q4: What's the difference between a primary key and a foreign key? What about UNIQUE?**
A4: A primary key uniquely identifies each row (NOT NULL + UNIQUE, one per table, usually indexed). A foreign key is a column referencing another table's primary key, enforcing referential integrity: you can't create an order for a non-existent user, and with `ON DELETE` rules you control cascades. UNIQUE constraints enforce uniqueness on other columns (email) and create an index.

**Q5: Why should money be stored as NUMERIC/DECIMAL, not FLOAT?**
A5: Floating-point types are binary approximations, so 0.1 + 0.2 ≠ 0.3, and rounding errors accumulate in sums and balances. Use `NUMERIC(precision, scale)` for exact decimal math, or store integer minor units (paise/cents as BIGINT), which many payment systems do (Stripe and Razorpay amounts are in the smallest unit).

---

## 🔷 Trade-offs
✅ Advantages:
- ACID transactions, strong consistency, data integrity constraints.
- Powerful ad-hoc queries (joins, aggregations), mature tooling, huge talent pool.
- Postgres extensions cover JSON, geo, full-text, vectors — one DB for many needs.

❌ Disadvantages:
- Horizontal write scaling is hard (sharding is manual/complex).
- Schema changes on huge tables need care (migrations, locks).
- Joins across huge datasets can get slow without careful indexing/denormalization.
- Not ideal for very high-volume, simple key-value or time-series writes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Table / Row / Column | Data structure in relational DB | टेबल / पंक्ति / स्तंभ |
| Schema | Fixed structure of tables | टेबल का ढाँचा |
| Primary Key | Unique id of a row | row की अनोखी पहचान |
| Foreign Key | Link to another table's PK | दूसरी टेबल से रिश्ता |
| JOIN | Combine rows from tables | टेबल जोड़ना |
| Transaction | All-or-nothing group of operations | सब या कुछ नहीं |
| WAL | Write-ahead log for durability | पहले log, फिर डेटा |
| Query planner | Chooses how to execute SQL | query चलाने का तरीका चुनने वाला |
| SQL Injection | Attack via unsafe query building | query में घुसपैठ वाला हमला |

---

## ⚡ 3-Line Summary
**English:**
1. SQL DBs store structured data in related tables with constraints, queried via SQL, with ACID transactions.
2. Postgres is the default modern choice (JSONB, extensions); MySQL is also excellent and widely used.
3. Always parameterize queries, use migrations, store money as NUMERIC/integers, and index for your queries.

**Hindi:**
1. SQL DB = रिश्तों वाली टेबल, नियम (constraints), SQL query और ACID transaction।
2. नए प्रोजेक्ट के लिए PostgreSQL सबसे अच्छा default; MySQL भी बढ़िया है।
3. हमेशा parameterized query, migrations, पैसे के लिए NUMERIC, और सही index।

---

## ➡️ Next Topic Suggestion
**26. NoSQL Databases** — SQL is great, but not for everything. Next: the four families of NoSQL (document, key-value, wide-column, graph), how MongoDB, Redis, Cassandra and DynamoDB work, and the problems they solve.
