# 288. Build Audit Log System
# हिंदी में: Audit Log System बनाना

---

## 🔵 Simple Definition (English)
An **audit log system** records WHO did WHAT, WHEN, and (often) WHY/HOW for every sensitive action in an application (data changes, logins, permission changes) — creating an immutable, queryable trail used for compliance, security investigations, and debugging "who changed this and when?" questions.

## 🔵 सरल परिभाषा (Hindi)
**Audit log system** record करता है कि किसने क्या किया, कब, और कैसे — किसी भी sensitive action के लिए (data changes, logins, permission changes) — एक immutable, queryable trail बनाता है जो compliance, security investigations, और "किसने कब ये बदला?" जैसे debugging questions के लिए use होता है।

---

## 🔴 Problem it Solves
Without an audit trail, when something goes wrong (a customer's order total was mysteriously changed, a user's account was deleted, sensitive data was accessed inappropriately), there's no way to answer "who did this and when?" — critical for security incident investigation, regulatory compliance (many industries legally REQUIRE audit trails for sensitive data access), and customer support ("why does my order show a different price than what I paid?"). Regular application logs are often too verbose/unstructured and get rotated/deleted quickly; audit logs are a deliberately separate, durable, structured record of specifically the actions that matter for accountability.

## 🔴 यह क्यों बना? (Hindi)
Audit trail के बिना, कुछ गलत होने पर (order total मिस्टीरियसली बदल गया, account delete हो गया) ये पता नहीं चलता कि किसने और कब किया — security investigation, regulatory compliance, customer support के लिए critical। Regular application logs अक्सर बहुत verbose/unstructured होते हैं और जल्दी rotate/delete हो जाते हैं; audit logs specifically accountability वाले actions का deliberately separate, durable, structured record हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Define what counts as an **auditable action** — typically: create/update/delete of sensitive records, authentication events (login, failed login, password change), permission/role changes, data exports, admin actions.
Step 2 → Design the audit log schema: `actorId` (who), `action` (what, e.g. `order.status_changed`), `resourceType`/`resourceId` (which record), `timestamp`, `changes` (before/after values for updates), `metadata` (IP address, user agent, request ID for correlation).
Step 3 → Capture audit entries at the point of the actual mutation — ideally via a centralized mechanism (middleware, ORM hooks, database triggers) rather than scattered manual logging calls that are easy to forget in some code paths.
Step 4 → Write audit logs to APPEND-ONLY storage, separate from the primary application database if possible — audit logs should be resistant to tampering/deletion, including by administrators of the main application (a compromised admin account shouldn't be able to cover its tracks by editing audit history).
Step 5 → Never allow UPDATE or DELETE on audit log entries through normal application code paths — only INSERT. Some systems additionally use write-once storage (S3 with object lock, or a dedicated audit-log service) for regulatory-grade immutability guarantees.
Step 6 → Build query/search capabilities for investigators: "show all actions by user X," "show all changes to order #42," "show all failed login attempts in the last 24 hours."
Step 7 → Set a retention policy appropriate to compliance requirements (some regulations require 7+ years of audit history) and archive older entries to cheaper storage rather than deleting them.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Auditable action** define करो — sensitive record changes, auth events, permission changes, admin actions।
Step 2 → Audit log schema design करो: actorId, action, resourceType/Id, timestamp, changes, metadata।
Step 3 → Actual mutation के point पर audit entry capture करो — centralized mechanism से।
Step 4 → Audit logs को APPEND-ONLY storage में लिखो, primary DB से अलग अगर possible हो।
Step 5 → Audit log entries पर UPDATE/DELETE कभी allow न करो — सिर्फ INSERT।
Step 6 → Investigators के लिए query/search capabilities बनाओ।
Step 7 → Compliance के हिसाब से retention policy set करो, पुराने entries archive करो delete नहीं।

---

## 🟡 Real World Example
**Paytm's** wallet and banking services maintain audit logs for every balance-affecting action — compliance regulations (RBI guidelines for payment companies in India) legally require this. Every transaction, refund, and admin adjustment is logged with the actor's ID, exact before/after balance, IP address, and a correlation ID linking it to the originating API request. These logs are written to an append-only store SEPARATE from the main transactional database, and even senior engineers with full production database access cannot modify or delete audit entries — only a formal, logged process (itself audited) can archive old entries after the mandated retention period.

## 🟡 Real Example Hindi mein
**Paytm** के wallet/banking services हर balance-affecting action के लिए audit logs maintain करते हैं — compliance regulations (RBI guidelines) legally ये require करती हैं। हर transaction actor ID, exact before/after balance, IP address के साथ logged होता है। ये logs append-only store में लिखे जाते हैं main transactional DB से अलग, और senior engineers भी audit entries modify/delete नहीं कर सकते।

---

## 💻 Code Example — Basic

```javascript
// basic-audit-log.js — minimal audit logging function
// npm install pg
// Run after creating an audit_logs table:
//   CREATE TABLE audit_logs (
//     id SERIAL PRIMARY KEY, actor_id TEXT, action TEXT,
//     resource_type TEXT, resource_id TEXT, changes JSONB,
//     created_at TIMESTAMPTZ DEFAULT now()
//   );

const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function logAuditEvent({ actorId, action, resourceType, resourceId, changes }) {
  await pool.query(
    `INSERT INTO audit_logs (actor_id, action, resource_type, resource_id, changes)
     VALUES ($1, $2, $3, $4, $5)`,
    [actorId, action, resourceType, resourceId, JSON.stringify(changes)]
  );
}

// Example usage: logging an order status change
async function updateOrderStatus(orderId, newStatus, actorId) {
  const oldOrder = { status: 'pending' }; // normally fetched from DB

  // ... perform the actual update ...
  console.log(`Order ${orderId} status updated to ${newStatus}`);

  // Log the change AFTER it succeeds
  await logAuditEvent({
    actorId,
    action: 'order.status_changed',
    resourceType: 'order',
    resourceId: String(orderId),
    changes: { before: { status: oldOrder.status }, after: { status: newStatus } },
  });
}

updateOrderStatus(42, 'shipped', 'user-101');
```

## 💻 Code Example — Advanced

```javascript
// advanced-audit-log.js — centralized interceptor pattern + query helpers
// npm install pg

const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

class AuditLogger {
  constructor(pool) {
    this.pool = pool;
  }

  async log({ actorId, action, resourceType, resourceId, before, after, metadata }) {
    // Compute only the FIELDS THAT ACTUALLY CHANGED — avoids noisy logs of unchanged data
    const changedFields = {};
    if (before && after) {
      for (const key of new Set([...Object.keys(before), ...Object.keys(after)])) {
        if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) {
          changedFields[key] = { before: before[key], after: after[key] };
        }
      }
    }

    await this.pool.query(
      `INSERT INTO audit_logs (actor_id, action, resource_type, resource_id, changes, metadata, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, now())`,
      [actorId, action, resourceType, resourceId, JSON.stringify(changedFields), JSON.stringify(metadata || {})]
    );
  }

  // ─── Query helpers for investigators ────────────────────────────────────
  async getActionsByActor(actorId, { limit = 50 } = {}) {
    const result = await this.pool.query(
      `SELECT * FROM audit_logs WHERE actor_id = $1 ORDER BY created_at DESC LIMIT $2`,
      [actorId, limit]
    );
    return result.rows;
  }

  async getHistoryForResource(resourceType, resourceId) {
    const result = await this.pool.query(
      `SELECT * FROM audit_logs WHERE resource_type = $1 AND resource_id = $2 ORDER BY created_at ASC`,
      [resourceType, resourceId]
    );
    return result.rows; // full chronological change history for one specific record
  }

  async getFailedLoginAttempts(sinceHours = 24) {
    const result = await this.pool.query(
      `SELECT * FROM audit_logs
       WHERE action = 'auth.login_failed' AND created_at > now() - interval '${sinceHours} hours'
       ORDER BY created_at DESC`
    );
    return result.rows;
  }
}

// ─── Generic wrapper enforcing "always audit, never forget" for mutations ─
function withAudit(auditLogger, { action, resourceType }) {
  return function (mutationFn) {
    return async function (req, resourceId, ...args) {
      const before = await mutationFn.getCurrentState?.(resourceId);
      const result = await mutationFn(resourceId, ...args);
      const after = result;

      await auditLogger.log({
        actorId: req.userId,
        action,
        resourceType,
        resourceId: String(resourceId),
        before,
        after,
        metadata: { ip: req.ip, userAgent: req.headers['user-agent'], requestId: req.id },
      });

      return result;
    };
  };
}

module.exports = { AuditLogger, withAudit };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { AuditLogger } = require('./advanced-audit-log');

const app = express();
app.use(express.json());

const pool = require('./db-pool'); // shared pg Pool instance
const auditLogger = new AuditLogger(pool);

// Middleware: attach a correlation request ID for cross-referencing logs
app.use((req, res, next) => {
  req.id = require('crypto').randomUUID();
  next();
});

app.patch('/api/orders/:id/status', async (req, res) => {
  const before = await getOrder(req.params.id); // fetch current state
  const updated = await updateOrderStatus(req.params.id, req.body.status);

  // Explicit audit call at the mutation point — always paired with the actual change
  await auditLogger.log({
    actorId: req.user.id,
    action: 'order.status_changed',
    resourceType: 'order',
    resourceId: req.params.id,
    before: { status: before.status },
    after: { status: updated.status },
    metadata: { ip: req.ip, userAgent: req.headers['user-agent'], requestId: req.id },
  });

  res.json({ data: updated });
});

// Investigator-facing endpoint — should itself be restricted to admin/compliance roles
app.get('/api/admin/audit-logs/resource/:type/:id', requireAdminRole, async (req, res) => {
  const history = await auditLogger.getHistoryForResource(req.params.type, req.params.id);
  res.json({ data: history });
});

function requireAdminRole(req, res, next) {
  if (req.user?.role !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  next();
}

async function getOrder(id) { return { id, status: 'pending' }; } // mock
async function updateOrderStatus(id, status) { return { id, status }; } // mock

app.listen(3000, () => console.log('Audit-logged API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Scattering manual `logAuditEvent()` calls across the codebase, easy to forget in some code paths
✅ Correct: Centralize audit logging as close to the data-mutation layer as possible (ORM hooks, database triggers, a wrapper service) so NEW code paths don't need developers to remember to add logging manually.

```javascript
// Wrong: relies on every developer remembering to call this in every update path
async function updateOrder(id, data) {
  await db.query('UPDATE orders SET ... WHERE id = $1', [id]);
  await logAuditEvent({ action: 'order.updated', ... }); // easy to forget, especially in a new endpoint
}

// Right: ORM-level hook fires automatically for ANY update to this model, no matter which code path
OrderModel.addHook('afterUpdate', async (instance, options) => {
  await auditLogger.log({ action: 'order.updated', resourceId: instance.id, ... });
});
```

❌ Mistake 2: Allowing audit log entries to be updated or deleted through normal application code
✅ Correct: Audit logs must be append-only — if they can be edited/deleted by the same privileges that can edit regular data, they're useless for investigating a compromised account or insider threat (the attacker could just erase their own trail).

```javascript
// Wrong: a generic "admin can edit any table" tool includes audit_logs
app.delete('/api/admin/records/:table/:id', requireAdminRole, async (req, res) => {
  await pool.query(`DELETE FROM ${req.params.table} WHERE id = $1`, [req.params.id]);
  // if table === 'audit_logs', an admin (or compromised admin account) can erase evidence!
});

// Right: explicitly exclude audit_logs from any generic delete/update tooling,
// and enforce it at the DB level too:
// REVOKE UPDATE, DELETE ON audit_logs FROM application_role;
```

---

## 🧠 Tricky Interview Question

```javascript
// This audit log entry looks correct. What's missing that would matter for a real investigation?
await auditLogger.log({
  actorId: req.user.id,
  action: 'user.role_changed',
  resourceId: targetUserId,
  before: { role: 'member' },
  after: { role: 'admin' },
});
// A week later, security needs to investigate: was this role change legitimate?
```
Answer: The entry captures WHO (actorId), WHAT (role changed member→admin), and WHICH record — but is missing crucial CONTEXT for a real investigation: the actor's IP address and user agent (was this done from a known office IP or a suspicious location?), a request correlation ID (to cross-reference with other logs/traces from the same request), and WHY (was there an approval ticket/reason field associated with this privilege escalation? Many compliance-grade systems require a `reason` or `ticketId` field for sensitive actions like granting admin access). Without IP/metadata, investigators can't distinguish "the legitimate admin did this from the office" from "someone's compromised session did this from an unusual location" — the `metadata` field (as included in the advanced example) exists specifically to capture this investigative context that the core who/what/when alone doesn't provide.

---

## ⚫ Interview Questions + Answers

Q1: Why should audit logs be stored separately from the main application database?
A1: Separation provides defense-in-depth: if the main application database is compromised (SQL injection, stolen credentials, insider threat with full DB access), a SEPARATE audit store (different credentials, different infrastructure, possibly write-once storage like S3 with object lock) means the attacker can't simply delete the evidence of their own actions along with everything else. It also prevents audit-log write volume/growth from impacting the performance of the primary transactional database, and allows different retention/backup policies suited to compliance needs (years of audit history vs. typical application data retention).

Q2: What's the difference between application logs (Winston/Pino output) and audit logs, and why not just use one for both?
A2: Application logs are typically high-volume, unstructured/semi-structured, developer-facing, and rotated/discarded quickly (days to weeks) — meant for debugging and operational monitoring. Audit logs are a deliberately curated SUBSET of events (specifically ones with accountability/compliance significance), structured consistently (same schema for every entry), retained for much longer (often years, per regulation), and must support reliable investigator queries ("all actions by user X"). Mixing them means either audit-relevant events get lost in rotation, or you're retaining ALL verbose debug logs for years unnecessarily (expensive, and makes genuine investigation harder due to noise).

Q3: How would you ensure audit log integrity — proving logs haven't been tampered with after the fact?
A3: Options with increasing strength: (1) Database-level permission restrictions (`REVOKE UPDATE, DELETE`) preventing modification through normal access. (2) Write-once storage (S3 Object Lock in compliance mode, or append-only log files with restricted filesystem permissions). (3) Cryptographic hash-chaining — each log entry includes a hash of the PREVIOUS entry (similar to a blockchain's structure), so altering any historical entry breaks the hash chain for everything after it, making tampering detectable even if direct deletion/editing were somehow possible. Most systems use layer (1) and (2); hash-chaining (3) is reserved for the highest-compliance-bar systems (e.g. certain financial/legal audit requirements).

Q4: How do you balance audit log verbosity with storage cost and query performance at scale?
A4: Only log genuinely AUDITABLE actions (not every single read/GET request — focus on mutations and sensitive access), store only the FIELDS THAT CHANGED rather than entire before/after record snapshots (as the advanced example's `changedFields` diffing does), index on commonly-queried fields (`actor_id`, `resource_type + resource_id`, `created_at`) for fast investigator queries, and implement a tiered retention strategy — recent logs (e.g. last 90 days) in fast, queryable storage, older logs archived to cheaper cold storage (S3 Glacier) that's still retrievable for compliance but not optimized for frequent querying.

Q5: Should audit logging happen synchronously (blocking the main request) or asynchronously?
A5: For most use cases, audit logging should NOT block the primary operation's response — log asynchronously (fire-and-forget, or via a background queue) so a slow/failing audit-log write doesn't degrade the user-facing API's latency or availability. However, for the HIGHEST-compliance-bar actions (e.g. an irreversible financial transaction), some systems intentionally make the audit write part of the SAME database transaction as the business mutation (ensuring the audit record and the actual change either both succeed or both roll back together) — trading a small latency cost for the guarantee that no mutation can ever happen without a corresponding audit entry, even under partial failures.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Regulated industries (fintech, healthcare, government) with legal audit-trail requirements
- Any system handling sensitive data, permissions, or financial transactions where accountability matters
- Debugging/support scenarios where "who changed this and when" is a recurring need

❌ Avoid when:
- Logging every trivial, non-sensitive read-only action — this bloats storage and query complexity without investigative value; reserve audit logging for genuinely accountability-relevant events
- A simple internal tool with a single trusted operator and no compliance requirement — standard application logs likely suffice

---

## 📊 Visual Diagram
```
MUTATION REQUEST                    AUDIT LOGGING                    STORAGE
──────────────────                  ───────────────                  ─────────────────────
PATCH /orders/42/status
        │
        ▼
  Fetch current state (before)
        │
        ▼
  Perform the actual update ────────────────────────────────────►  orders table (mutable)
        │
        ▼
  Compute changed fields (before vs after)
        │
        ▼
  auditLogger.log({                 ──────────────────────────►   audit_logs table
    actorId, action,                                              (APPEND-ONLY,
    resourceType, resourceId,                                      no UPDATE/DELETE
    changes, metadata                                              permission granted)
  })
        │
        ▼
  Response to client

INVESTIGATOR QUERY (weeks later):
  GET /admin/audit-logs/resource/order/42
        │
        ▼
  SELECT * FROM audit_logs
  WHERE resource_type='order' AND resource_id='42'
  ORDER BY created_at ASC
        │
        ▼
  Full chronological change history returned
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Audit Trail | Chronological record of who did what, when | किसने क्या किया, कब, इसका chronological record |
| Append-Only | Storage allowing only new writes, no edits/deletes | सिर्फ नए writes allow, edit/delete नहीं |
| Actor | The user/system that performed the action | Action करने वाला user/system |
| Resource | The record/entity the action was performed on | वो record/entity जिस पर action हुआ |
| Correlation ID | Identifier linking related log entries across a request | Request के related log entries को जोड़ने वाला identifier |
| Retention Policy | Rules for how long data/logs must be kept | Data/logs कितनी देर रखने के rules |

---

## ⚡ 3-Line Summary
English: 1. Audit logs record who-did-what-when for sensitive/compliance-relevant actions, as a deliberately separate, structured, long-retained trail distinct from regular application logs. 2. Centralize audit capture (ORM hooks, wrapper services) so new code paths can't accidentally skip logging, and store only diffed/changed fields rather than full snapshots. 3. Audit storage must be genuinely append-only — no update/delete permission through normal application access — so even a compromised privileged account can't erase its own trail.
Hindi: 1. Audit logs sensitive/compliance-relevant actions के लिए who-did-what-when record करते हैं, regular application logs से अलग एक deliberately separate, structured, long-retained trail। 2. Audit capture centralize करो ताकि नए code paths logging skip न कर सकें, और सिर्फ changed fields store करो, पूरे snapshots नहीं। 3. Audit storage genuinely append-only होना चाहिए — compromised privileged account भी अपना trail न मिटा सके।

---

## ➡️ Next Topic
**289. Build Notification System (Push/In-App)** — multi-channel notification system बनाना preferences और delivery tracking के साथ।
