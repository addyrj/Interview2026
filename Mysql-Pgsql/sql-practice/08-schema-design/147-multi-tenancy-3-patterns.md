---

# Q147. Multi-Tenancy — 3 Patterns (Separate DB / Schema / Shared Table)
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Explain the three multi-tenancy patterns. Show schema and code for the shared-table approach with tenant isolation. How do you use PostgreSQL Row-Level Security for automatic enforcement?

---

## 💡 Quick Concept (2 lines only)
Three patterns: (1) Separate databases — max isolation, high overhead. (2) Separate schemas (PgSQL) — good isolation, moderate overhead. (3) Shared tables with tenant_id — cheapest, needs careful query enforcement. PgSQL RLS can enforce tenant isolation at the DB level.
हिंदी: 3 patterns: separate DB (max isolation), separate schema (medium), shared table+tenant_id (cheapest)। PgSQL RLS = automatic enforcement।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- PATTERN 1: SEPARATE DATABASE PER TENANT
-- ============================================

-- Each tenant gets their own MySQL/PgSQL database:
-- tenant_acme_db  → all Acme's tables
-- tenant_beta_db  → all Beta's tables
-- tenant_gamma_db → all Gamma's tables

-- Pros:
--   ✅ Maximum isolation (data breach can't leak cross-tenant)
--   ✅ Easy per-tenant backup and restore
--   ✅ Per-tenant customization (different schemas per customer)
--   ✅ Compliance-friendly (GDPR: "delete all user data" = drop database)
--   ✅ Performance isolation (one busy tenant doesn't affect others)

-- Cons:
--   ❌ 1000 tenants = 1000 databases (connection overhead, management nightmare)
--   ❌ Migrations must run on every database
--   ❌ Expensive (database per tenant has baseline resource cost)
--   ❌ Analytics across all tenants is hard (need federated queries)

-- Use when: enterprise SaaS with few (< 50) large tenants needing strong isolation

-- ============================================
-- PATTERN 2: SEPARATE SCHEMA PER TENANT (PostgreSQL)
-- ============================================

-- One database, one schema per tenant:
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_beta;
CREATE SCHEMA tenant_gamma;

-- Each schema has same tables:
CREATE TABLE tenant_acme.orders (id SERIAL PRIMARY KEY, user_id INT, amount DECIMAL);
CREATE TABLE tenant_beta.orders (id SERIAL PRIMARY KEY, user_id INT, amount DECIMAL);

-- Route queries via search_path:
SET search_path TO tenant_acme;     -- ← all queries now hit tenant_acme schema
SELECT * FROM orders;               -- → queries tenant_acme.orders!

-- Node.js: Set search_path per connection:
-- await client.query(`SET search_path TO ${tenantSchema}`);
-- await client.query('SELECT * FROM orders');  -- hits correct schema

-- Pros:
--   ✅ Good isolation (queries can't accidentally cross schemas)
--   ✅ Easier to manage than separate databases (1 DB, N schemas)
--   ✅ Shared connection pool (PgBouncer works well here)
--   ✅ PostgreSQL-native, good tooling support

-- Cons:
--   ❌ 10,000 tenants = 10,000 schemas (schema metadata can bloat)
--   ❌ Migrations still run per-schema (use migration tools that support this)
--   ❌ MySQL doesn't have separate schema isolation (schema ≈ database in MySQL)

-- Use when: mid-range (50-10,000 tenants), PgSQL, need schema isolation

-- ============================================
-- PATTERN 3: SHARED TABLES WITH TENANT_ID (Most Common)
-- ============================================

-- All tenants share the same tables, tenant_id column separates them:

CREATE TABLE tenants (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  name       VARCHAR(200) NOT NULL,
  subdomain  VARCHAR(100) UNIQUE NOT NULL,
  plan       VARCHAR(20) DEFAULT 'starter',
  created_at DATETIME DEFAULT NOW()
);

CREATE TABLE users (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  tenant_id  INT NOT NULL,         -- ← every table has tenant_id!
  email      VARCHAR(255) NOT NULL,
  name       VARCHAR(200),
  role       VARCHAR(50) DEFAULT 'member',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  UNIQUE (tenant_id, email)        -- email unique per tenant (not globally)
);

CREATE TABLE orders (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  tenant_id  INT NOT NULL,         -- ← every table has tenant_id!
  user_id    INT NOT NULL,
  amount     DECIMAL(10,2),
  status     VARCHAR(20),
  created_at DATETIME DEFAULT NOW(),
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- CRITICAL: Every index must include tenant_id as LEFTMOST column!
CREATE INDEX idx_users_tenant ON users(tenant_id, email);
CREATE INDEX idx_orders_tenant_user ON orders(tenant_id, user_id);
CREATE INDEX idx_orders_tenant_status ON orders(tenant_id, status, created_at DESC);

-- ← tenant_id first = queries always filter to one tenant's data first!
-- Without: index scan across ALL tenants → data leakage risk + slow

-- ============================================
-- APPLICATION-LAYER ENFORCEMENT (Node.js)
-- ============================================

/*
// Middleware: attach tenant to every request
app.use(async (req, res, next) => {
  const subdomain = req.hostname.split('.')[0];  // e.g., 'acme' from acme.app.com
  const tenant = await Tenant.findOne({ where: { subdomain } });
  if (!tenant) return res.status(404).json({ error: 'Tenant not found' });
  req.tenantId = tenant.id;
  next();
});

// Repository layer: ALWAYS filter by tenantId
class OrderRepository {
  constructor(tenantId) {
    this.tenantId = tenantId;
  }

  async findAll(filters = {}) {
    return db.query(
      'SELECT * FROM orders WHERE tenant_id = ? AND status = ?',
      [this.tenantId, filters.status]  // tenant_id always first!
    );
  }

  async findById(orderId) {
    const [rows] = await db.query(
      'SELECT * FROM orders WHERE tenant_id = ? AND id = ?',
      [this.tenantId, orderId]          // ← both tenant_id AND id!
    );
    // Without tenant_id check: tenant B could access tenant A's orders by guessing IDs!
    return rows[0] || null;
  }
}

// Usage:
const repo = new OrderRepository(req.tenantId);
const orders = await repo.findAll({ status: 'pending' });
*/

-- ============================================
-- POSTGRESQL ROW-LEVEL SECURITY (AUTOMATIC ENFORCEMENT)
-- ============================================

-- Enable RLS on the table:
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy: users can only see rows where tenant_id matches their session variable
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::int);
-- ← Every SELECT/UPDATE/DELETE on orders automatically has this WHERE condition appended!

CREATE POLICY tenant_isolation ON users
  USING (tenant_id = current_setting('app.current_tenant_id')::int);

-- Set the tenant context before queries:
-- In Node.js, at request start:
-- await client.query("SET app.current_tenant_id = $1", [tenantId]);
-- Now ALL queries on orders/users are automatically scoped!

-- Even if developer forgets tenant_id in query:
SELECT * FROM orders WHERE status = 'pending';
-- PgSQL automatically rewrites to:
-- SELECT * FROM orders WHERE status = 'pending' AND tenant_id = 42
-- (where 42 = app.current_tenant_id session variable)

-- ← RLS = defense in depth: even buggy code can't accidentally leak cross-tenant data!

-- Force RLS even for table owner (important!):
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
-- Without FORCE: table owner bypasses RLS (dangerous!)

-- Separate read and write policies:
CREATE POLICY tenant_read ON orders FOR SELECT
  USING (tenant_id = current_setting('app.current_tenant_id')::int);

CREATE POLICY tenant_write ON orders FOR INSERT
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::int);
-- ← Prevents INSERT with wrong tenant_id too!

-- ============================================
-- MYSQL EQUIVALENT (No RLS — must use views)
-- ============================================

-- MySQL has no RLS — use views as a workaround:
CREATE VIEW v_orders AS
  SELECT * FROM orders WHERE tenant_id = @current_tenant_id;
-- SET @current_tenant_id = 42; SELECT * FROM v_orders;
-- Weak: variable must be set manually, can be bypassed by querying the base table

-- Better MySQL approach: enforce at application layer (repository pattern above)
-- and use a static analysis tool to check all queries have tenant_id filter

-- ============================================
-- COMPARISON TABLE
-- ============================================

/*
Pattern           | Isolation | Cost    | Tenants | Best For
──────────────────┼───────────┼─────────┼─────────┼──────────────────────────
Separate DB       | ⭐⭐⭐⭐⭐ | $$$     | < 50    | Enterprise, compliance
Separate Schema   | ⭐⭐⭐⭐   | $$      | 50-10K  | Mid-range PgSQL SaaS
Shared Table+RLS  | ⭐⭐⭐     | $       | 10K+    | High-scale B2B/B2C SaaS
Shared Table only | ⭐⭐       | $       | 10K+    | Small apps (careful!)
*/
```

---

## 🔍 Why This Works (3 lines max)
Shared-table multi-tenancy is cheapest but puts all trust in application code to filter by tenant_id — one missing WHERE clause leaks another tenant's data. PgSQL RLS turns this into a database-enforced constraint: the session variable approach sets context once per request, and RLS appends the tenant filter to every query automatically. Putting tenant_id as the leftmost column in every index ensures queries don't scan across all tenants' data.
हिंदी: Shared table = cheapest लेकिन tenant_id filter हर query में जरूरी। PgSQL RLS = database level enforcement, code bug से data leak नहीं। tenant_id leftmost index = one tenant का data scan।

---

## ⚡ Alternative Solution

```sql
-- PgSQL: Set tenant via role instead of session variable:
CREATE ROLE acme_role;
CREATE POLICY tenant_by_role ON orders
  USING (tenant_id = (
    SELECT id FROM tenants WHERE name = current_user  -- current DB role
  ));
-- Connect as 'acme_role' → only sees acme's data
-- Useful when each tenant gets their own DB user (less common but strong isolation)

-- Hybrid approach: tenant_id in JWT claim → app sets session variable:
-- Middleware: verify JWT → extract tenantId from claims → SET app.current_tenant_id
-- No DB lookup needed per request (tenant from token)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Missing tenant_id from unique constraint
CREATE TABLE users (
  id INT PRIMARY KEY,
  tenant_id INT,
  email VARCHAR(255),
  UNIQUE(email)           -- ← global uniqueness! user@acme.com can't exist twice
);
-- Two tenants can't have same email!
-- ✅ Fix:
UNIQUE(tenant_id, email)  -- email unique WITHIN a tenant, not globally

-- ❌ Wrong: Querying by ID without tenant_id
SELECT * FROM orders WHERE id = 1234;
-- Tenant A's admin could access tenant B's order #1234 by guessing IDs!
-- ✅ Always:
SELECT * FROM orders WHERE tenant_id = $1 AND id = $2;

-- ❌ Wrong: Skipping FORCE ROW LEVEL SECURITY in PgSQL
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
-- Without FORCE: table owner role bypasses RLS completely!
-- ✅ Fix:
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- ❌ Wrong: Shared table without tenant_id in indexes
CREATE INDEX idx_status ON orders(status);
-- Querying all pending orders scans ALL tenants → slow + potential data leak
-- ✅ Fix: tenant_id always leftmost:
CREATE INDEX idx_tenant_status ON orders(tenant_id, status);
```

---

## 🎯 Interview Tip (1 line)
Say: "For most SaaS products I use shared tables with tenant_id, since it's cost-efficient at scale. The critical practices are: tenant_id in every table, tenant_id as the leftmost column in every index, and repository-layer enforcement in app code. In PostgreSQL I add RLS as defense-in-depth — even if app code has a bug, the DB enforces tenant isolation automatically via the session variable pattern."

---

## 🔗 Related Questions
→ Q181 (JSONB) | Q185 (LISTEN/NOTIFY) | Q196 (row-level security) | Q220 (zero-downtime migration)
