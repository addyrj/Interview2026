# 287. Build Multi-tenant API
# हिंदी में: Multi-tenant API बनाना

---

## 🔵 Simple Definition (English)
A **multi-tenant API** serves multiple independent customers ("tenants" — e.g. separate companies using the same SaaS product) from one shared application, while strictly isolating each tenant's data from the others. The core engineering challenge is guaranteeing that Tenant A can NEVER see or modify Tenant B's data, even under bugs or malicious attempts.

## 🔵 सरल परिभाषा (Hindi)
**Multi-tenant API** एक shared application से multiple independent customers ("tenants" — जैसे एक SaaS product use करने वाली अलग-अलग companies) को serve करता है, हर tenant का data दूसरों से strictly isolated रखते हुए। Core challenge ये guarantee करना है कि Tenant A कभी Tenant B का data न देख सके न बदल सके, bugs या malicious attempts के बावजूद।

---

## 🔴 Problem it Solves
Running a SEPARATE application instance/database per customer (single-tenant architecture) is operationally expensive at scale — hundreds of customers mean hundreds of deployments to patch, monitor, and scale individually. Multi-tenancy shares infrastructure and application code across customers, dramatically reducing operational overhead and cost-per-customer, while the architecture must still provide the SAME data isolation guarantees a dedicated-instance-per-customer setup would give.

## 🔴 यह क्यों बना? (Hindi)
हर customer के लिए अलग application instance/database (single-tenant architecture) चलाना scale पर operationally expensive है — सैकड़ों customers मतलब सैकड़ों deployments individually patch/monitor/scale करने पड़ें। Multi-tenancy infrastructure और code customers के बीच share करती है, operational overhead/cost-per-customer कम करती है, जबकि वही data isolation guarantees देती है जो dedicated instance देता।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose an isolation model:
  - **Shared database, shared schema** (most common): one DB, one set of tables, every row has a `tenant_id` column; every query MUST filter by `tenant_id`. Cheapest to operate, highest risk of a missed filter leaking data.
  - **Shared database, separate schema per tenant**: one DB instance, but each tenant gets its own schema/namespace — stronger isolation, more operational overhead (migrations must run per-schema).
  - **Separate database per tenant**: strongest isolation, highest operational cost — typically reserved for enterprise customers with strict compliance requirements.
Step 2 → Identify the tenant for each incoming request: via subdomain (`acme.yourapp.com`), a header (`X-Tenant-ID`), a JWT claim (`tenantId` embedded in the user's token at login), or the authenticated user's associated tenant record.
Step 3 → Enforce tenant scoping at the LOWEST possible layer — ideally the database query layer itself (e.g. a middleware/ORM hook that automatically injects `WHERE tenant_id = ?` into EVERY query) rather than relying on each individual route handler to remember to filter correctly.
Step 4 → Validate that any resource ID in a request (e.g. `/orders/42`) actually belongs to the authenticated tenant BEFORE returning/modifying it — never trust that a resource ID alone implies authorization.
Step 5 → For shared-schema designs, add a database-level safety net: Postgres **Row-Level Security (RLS)** policies that enforce tenant isolation even if application code has a bug, as defense-in-depth beyond app-layer filtering.
Step 6 → Design tenant-aware caching keys (`cache:tenant123:product:42`, never just `cache:product:42`) to avoid cache collisions leaking data across tenants.
Step 7 → Rate-limit and monitor per-tenant to prevent one noisy tenant from degrading service for others ("noisy neighbor" problem).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Isolation model चुनो: shared schema (cheapest, risk ज़्यादा), separate schema per tenant, या separate DB per tenant (strongest, expensive)।
Step 2 → हर request के लिए tenant identify करो: subdomain, header, JWT claim, या user record से।
Step 3 → Tenant scoping को सबसे नीचे layer पर enforce करो — ideally DB query layer में automatically।
Step 4 → Resource ID हमेशा verify करो कि authenticated tenant का ही है।
Step 5 → Shared-schema के लिए DB-level safety net: Postgres **Row-Level Security**।
Step 6 → Cache keys tenant-aware बनाओ।
Step 7 → Per-tenant rate-limit/monitor करो "noisy neighbor" से बचने के लिए।

---

## 🟡 Real World Example
**Razorpay's** merchant dashboard is multi-tenant: every merchant (tenant) sees only their own transactions, settlements, and API keys, all stored in shared tables with a `merchant_id` column. Every database query in their codebase goes through a query-builder wrapper that AUTOMATICALLY injects `WHERE merchant_id = ?` based on the authenticated session — making it structurally difficult for a developer to accidentally write an unscoped query. As an additional safety net, their Postgres tables use Row-Level Security policies, so even a raw SQL query run by an engineer debugging in production can't accidentally return cross-merchant data.

## 🟡 Real Example Hindi mein
**Razorpay** का merchant dashboard multi-tenant है: हर merchant (tenant) सिर्फ अपने transactions, settlements, API keys देखता है, shared tables में `merchant_id` column के साथ। हर DB query एक query-builder wrapper से जाती है जो automatically `WHERE merchant_id = ?` inject करती है। Additional safety net के रूप में, Postgres tables Row-Level Security policies use करती हैं।

---

## 💻 Code Example — Basic

```javascript
// basic-multi-tenant.js — tenant identification + manual scoping
// npm install express
// Run: node basic-multi-tenant.js

const express = require('express');
const app = express();
app.use(express.json());

// Mock data — note every record has a tenantId
const orders = [
  { id: 1, tenantId: 'acme-corp', amount: 500 },
  { id: 2, tenantId: 'globex-inc', amount: 1200 },
  { id: 3, tenantId: 'acme-corp', amount: 750 },
];

// Middleware: extract tenant from a header (in real apps, derive this from an
// authenticated JWT claim, NOT a client-supplied header which could be spoofed)
function identifyTenant(req, res, next) {
  const tenantId = req.headers['x-tenant-id'];
  if (!tenantId) {
    return res.status(400).json({ error: 'X-Tenant-ID header required' });
  }
  req.tenantId = tenantId;
  next();
}

app.use(identifyTenant);

// EVERY query must filter by req.tenantId — this is the critical discipline
app.get('/api/orders', (req, res) => {
  const tenantOrders = orders.filter((o) => o.tenantId === req.tenantId);
  res.json({ data: tenantOrders });
});

app.listen(3000, () => console.log('Multi-tenant API on port 3000'));

// Test: curl -H "X-Tenant-ID: acme-corp" http://localhost:3000/api/orders
// Returns ONLY acme-corp's orders, never globex-inc's
```

## 💻 Code Example — Advanced

```javascript
// advanced-multi-tenant.js — JWT-derived tenant, query-layer auto-scoping, resource ownership check
// npm install express jsonwebtoken pg

const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const JWT_SECRET = process.env.JWT_SECRET;

// ─── Middleware: derive tenantId from the VERIFIED JWT, never from client input directly ─
function requireTenant(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Missing token' });

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.tenantId = decoded.tenantId; // tenantId was embedded in the token at login, server-controlled
    req.userId = decoded.userId;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

// ─── Scoped query helper — a single place where tenant filtering is enforced ─
class TenantScopedDb {
  constructor(pool, tenantId) {
    this.pool = pool;
    this.tenantId = tenantId;
  }

  // Every query automatically appends the tenant filter — individual callers
  // can't forget to scope, since it's baked into this wrapper
  async find(table, whereClause = '', params = []) {
    const query = `SELECT * FROM ${table} WHERE tenant_id = $1 ${whereClause ? `AND ${whereClause}` : ''}`;
    const result = await this.pool.query(query, [this.tenantId, ...params]);
    return result.rows;
  }

  async findOne(table, id) {
    const result = await this.pool.query(
      `SELECT * FROM ${table} WHERE tenant_id = $1 AND id = $2`,
      [this.tenantId, id]
    );
    return result.rows[0] || null; // null if not found OR belongs to a different tenant
  }

  async insert(table, data) {
    const columns = Object.keys(data);
    const values = Object.values(data);
    const placeholders = values.map((_, i) => `$${i + 2}`).join(', ');
    const result = await this.pool.query(
      `INSERT INTO ${table} (tenant_id, ${columns.join(', ')}) VALUES ($1, ${placeholders}) RETURNING *`,
      [this.tenantId, ...values]
    );
    return result.rows[0];
  }
}

function tenantDb(req, res, next) {
  req.db = new TenantScopedDb(pool, req.tenantId);
  next();
}

module.exports = { requireTenant, tenantDb, TenantScopedDb };

// ─── Usage in routes ────────────────────────────────────────────────────────
// app.get('/api/orders/:id', requireTenant, tenantDb, async (req, res) => {
//   const order = await req.db.findOne('orders', req.params.id);
//   // findOne already scopes by tenant_id — a request for another tenant's order ID
//   // simply returns null (looks identical to "not found"), never leaks existence
//   if (!order) return res.status(404).json({ error: 'Order not found' });
//   res.json({ data: order });
// });
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { requireTenant, tenantDb } = require('./advanced-multi-tenant');

const app = express();
app.use(express.json());

app.get('/api/orders', requireTenant, tenantDb, async (req, res) => {
  const orders = await req.db.find('orders');
  res.json({ data: orders });
});

app.get('/api/orders/:id', requireTenant, tenantDb, async (req, res) => {
  const order = await req.db.findOne('orders', req.params.id);
  if (!order) return res.status(404).json({ error: 'Order not found' }); // never "403 forbidden" — don't leak existence
  res.json({ data: order });
});

app.post('/api/orders', requireTenant, tenantDb, async (req, res) => {
  const order = await req.db.insert('orders', { amount: req.body.amount, status: 'pending' });
  res.status(201).json({ data: order });
});

app.listen(3000, () => console.log('Multi-tenant orders API on port 3000'));

/* Postgres Row-Level Security as defense-in-depth (run once as DB setup):
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant')::text);
-- App sets `SET app.current_tenant = '<tenantId>'` per connection/transaction,
-- and Postgres itself then refuses to return rows from other tenants,
-- even if application code forgets a WHERE clause.
*/
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Trusting a client-supplied tenant ID (e.g. a header or query param) without verifying it against the authenticated user's actual tenant
✅ Correct: Derive the tenant ID from the server-verified JWT/session, never from client-controlled input — otherwise any authenticated user could simply change a header to access another tenant's data.

```javascript
// Wrong: any logged-in user can just change this header to view ANY tenant's data
app.get('/api/orders', (req, res) => {
  const tenantId = req.headers['x-tenant-id']; // fully client-controlled!
  const orders = db.find('orders', { tenantId });
  res.json(orders);
});

// Right: tenantId comes from the verified token, impossible for the client to forge
app.get('/api/orders', requireTenant, (req, res) => {
  const orders = db.find('orders', { tenantId: req.tenantId }); // from jwt.verify(), trusted
  res.json(orders);
});
```

❌ Mistake 2: Checking tenant ownership AFTER fetching the resource by ID, in a way that leaks existence via different error codes
✅ Correct: Return the SAME `404 Not Found` whether a resource doesn't exist OR belongs to a different tenant — distinguishing them (e.g. `403 Forbidden` for "exists but not yours") leaks information about other tenants' data existing.

```javascript
// Wrong: leaks that order #42 EXISTS (just not yours) — an information disclosure
const order = await db.findOne('orders', { id: req.params.id }); // no tenant filter here!
if (order.tenantId !== req.tenantId) return res.status(403).json({ error: 'Not your order' });

// Right: the query itself is tenant-scoped, so a cross-tenant ID simply returns "not found"
const order = await db.findOne('orders', { id: req.params.id, tenantId: req.tenantId });
if (!order) return res.status(404).json({ error: 'Order not found' }); // identical for both cases
```

---

## 🧠 Tricky Interview Question

```javascript
// This endpoint has been in production for months with no reported issues.
// What's the subtle multi-tenant bug, and why did it go unnoticed?
app.get('/api/orders/:id/invoice', requireTenant, tenantDb, async (req, res) => {
  const order = await req.db.findOne('orders', req.params.id); // correctly tenant-scoped
  if (!order) return res.status(404).json({ error: 'Not found' });

  // Fetch the customer info for the invoice — DIFFERENT table, DIFFERENT query
  const customerResult = await pool.query('SELECT * FROM customers WHERE id = $1', [order.customerId]);
  res.json({ order, customer: customerResult.rows[0] });
});
```
Answer: The `order` lookup is correctly tenant-scoped via `req.db.findOne`, but the SECOND query (fetching `customers`) uses the raw `pool.query` directly, bypassing the `TenantScopedDb` wrapper entirely — it has NO `tenant_id` filter at all. If `order.customerId` were ever manipulable or if there's any data-integrity issue where a `customerId` could point to a record belonging to a DIFFERENT tenant (e.g. due to a prior bug, a migration error, or an admin tool bug that created cross-tenant references), this query would happily return that other tenant's customer data with no isolation check. This went unnoticed because in NORMAL operation, `order.customerId` always correctly points to a same-tenant customer — the bug only manifests under edge cases (data corruption, a separate bug elsewhere) that monitoring hadn't yet surfaced. The broader interview lesson: EVERY database query touching tenant-scoped tables must go through the scoped-query layer, with NO exceptions for "just this one related lookup" — consistency of the discipline matters more than any single query being individually correct.

---

## ⚫ Interview Questions + Answers

Q1: What's the main tradeoff between shared-schema and separate-database-per-tenant multi-tenancy?
A1: Shared-schema (one DB, `tenant_id` column everywhere) is operationally cheap — one set of migrations, one connection pool, trivial to add new tenants (just a new row/ID) — but the isolation is purely application-enforced, meaning a single missed `WHERE tenant_id` filter is a serious data leak. Separate-database-per-tenant provides the strongest isolation (a bug in one tenant's queries literally cannot touch another tenant's database) and simplifies compliance requirements (some enterprise contracts REQUIRE physical data separation), but massively increases operational complexity — migrations, backups, and monitoring must all be done per-tenant-database, which doesn't scale well past a few hundred tenants without heavy automation.

Q2: How does Postgres Row-Level Security (RLS) provide defense-in-depth for multi-tenant isolation?
A2: RLS policies are enforced by the DATABASE itself, independent of application code correctness — once enabled with a policy like `USING (tenant_id = current_setting('app.current_tenant'))`, even a raw, unscoped `SELECT * FROM orders` run by ANY database connection (including a developer debugging directly, or a bug in application code that forgot to filter) will only return rows matching the currently-set tenant context. It's a safety net that catches application-layer mistakes that would otherwise silently leak data, at the cost of needing to correctly set the session-level tenant context on every connection/transaction.

Q3: How would you design per-tenant rate limiting to prevent a "noisy neighbor" problem?
A3: Use the tenant ID (not just IP or user ID) as the rate-limiting key, so each tenant gets an independent quota regardless of how many individual users they have. Size limits based on the tenant's subscription tier (free tier: 100 req/min; enterprise: 10,000 req/min). For truly strong isolation against resource exhaustion (not just request COUNT but actual compute/DB load), some systems go further with per-tenant connection pool limits or dedicated worker queues for heavy operations, so one tenant running an expensive report generation can't starve other tenants' simple read requests.

Q4: Why is deriving the tenant ID from a subdomain (`acme.yourapp.com`) sometimes preferred over a header or JWT claim?
A4: Subdomain-based tenant identification is visible and verifiable at the DNS/routing layer BEFORE the request even reaches application code — it can be used for infra-level isolation (different subdomains routed to different infrastructure/regions for enterprise tenants with data-residency requirements) and gives users a clear, bookmarkable, branded URL per tenant. The downside: it requires wildcard DNS/SSL setup and more complex routing logic. JWT-claim-based identification is simpler to implement and works fine for API-only products without a tenant-specific UI domain requirement.

Q5: How do you handle a user who legitimately belongs to MULTIPLE tenants (e.g. a consultant working with several client organizations)?
A5: The JWT/session shouldn't hardcode a single tenant at login if a user can belong to multiple — instead, store the user's list of accessible tenant IDs, and require the client to specify WHICH tenant context they're currently operating in for each request (e.g. via an explicit "switch organization" action that issues a new scoped token, or a tenant-selection header validated against the user's allowed-tenants list server-side). Critically, the server must verify the requested tenant is actually one the authenticated user is a MEMBER of — never trust a client-supplied tenant ID as automatically authorized just because the user is logged in to SOME tenant.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a SaaS product serving multiple independent customer organizations from shared infrastructure
- Cost efficiency and operational simplicity matter more than absolute physical data separation

❌ Avoid when:
- Regulatory/compliance requirements mandate physically separate infrastructure per customer (some healthcare/financial/government contracts require this) — use separate-database or separate-deployment architecture instead
- You're building a single-customer internal tool with no need for tenant isolation at all — adding multi-tenancy machinery is unnecessary complexity

---

## 📊 Visual Diagram
```
SHARED-SCHEMA MULTI-TENANCY
──────────────────────────────
                    ┌─────────────────────────────┐
  Tenant A request  │                               │
  (JWT: tenantId=A) │   orders table                │
       │            │   ┌────┬───────────┬────────┐│
       ▼            │   │ id │ tenant_id │ amount ││
  requireTenant() ──►│   ├────┼───────────┼────────┤│
       │            │   │ 1  │     A      │  500   ││ ◄── Tenant A sees only this
       ▼            │   │ 2  │     B      │  1200  ││
  WHERE tenant_id=A │   │ 3  │     A      │  750   ││ ◄── and this
       │            │   └────┴───────────┴────────┘│
       ▼            │                               │
  [rows 1, 3 only]  └─────────────────────────────┘
                              ▲
                     Tenant B request (tenantId=B)
                     WHERE tenant_id=B → [row 2 only]

DEFENSE IN DEPTH:
  App-layer filter (WHERE tenant_id = ?)
            +
  DB-layer Row-Level Security policy (enforced even if app forgets)
            =
  Isolation holds even under application bugs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tenant | An independent customer/organization sharing the platform | Platform share करने वाला independent customer/organization |
| Shared Schema | One database/tables, isolated by tenant_id column | एक database, tenant_id column से isolated |
| Row-Level Security | DB-enforced per-row access policy | DB-enforced per-row access policy |
| Noisy Neighbor | One tenant's load degrading others' performance | एक tenant का load दूसरों को प्रभावित करना |
| Tenant Scoping | Filtering every query/operation by tenant identity | हर query को tenant identity से filter करना |
| Defense in Depth | Multiple independent layers of protection | Protection की कई independent layers |

---

## ⚡ 3-Line Summary
English: 1. Multi-tenant APIs serve multiple customers from shared infrastructure while strictly isolating each tenant's data, typically via a `tenant_id` column filtered on every query. 2. Derive the tenant ID from a server-verified source (JWT claim), never client-supplied input, and scope EVERY query — including "unrelated" secondary lookups — through a consistent tenant-aware layer. 3. Use database-level Row-Level Security as defense-in-depth against application bugs that might otherwise leak cross-tenant data.
Hindi: 1. Multi-tenant APIs shared infrastructure से कई customers serve करती हैं, हर tenant का data `tenant_id` column से strictly isolated रखते हुए। 2. Tenant ID server-verified source (JWT) से लो, client input से नहीं, और हर query को consistent tenant-aware layer से scope करो। 3. Database-level Row-Level Security को defense-in-depth के रूप में use करो।

---

## ➡️ Next Topic
**288. Build Audit Log System** — compliance और debugging के लिए audit trail system बनाना।
