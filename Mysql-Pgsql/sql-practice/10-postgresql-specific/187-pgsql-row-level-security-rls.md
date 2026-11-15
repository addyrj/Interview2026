---

# Q187. PgSQL Row-Level Security (RLS)
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only (MySQL has no RLS — use views / app-layer filters)

---

## ❓ Question
Your SaaS app stores all tenants' invoices in one table. How do you make sure a connection acting for tenant 1 can never read, update, or insert tenant 2's rows — even if a developer forgets the `WHERE tenant_id = ...`? Show how RLS policies enforce this in the database.

---

## 💡 Quick Concept (2 lines only)
RLS attaches a policy predicate to a table: `USING` filters which rows are visible/updatable, `WITH CHECK` validates new/changed rows. The database appends the predicate to every query automatically.
हिंदी: RLS में policy हर query पर अपने-आप लगती है — दूसरे tenant की rows दिखती ही नहीं, चाहे WHERE भूल जाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- verified on PostgreSQL 18 (PGlite)
-- ============================================

CREATE TABLE invoices (
  id         INT PRIMARY KEY,
  tenant_id  INT NOT NULL,
  amount     NUMERIC,
  note       TEXT
);

INSERT INTO invoices VALUES
  (1, 1, 100, 'a'), (2, 1, 250, 'b'),
  (3, 2, 999, 'c'), (4, 2,  50, 'd');

-- Application role (NOT superuser, NOT table owner -> RLS applies to it)
CREATE ROLE app_user NOLOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON invoices TO app_user;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: turn RLS on (default-deny for non-owners once enabled)
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
-- Step 2: make even the table owner obey policies (superusers/BYPASSRLS still bypass)
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;

-- Step 3: one policy for all commands, tenant id comes from a session setting
CREATE POLICY tenant_isolation ON invoices
  FOR ALL TO app_user
  USING      (tenant_id = current_setting('app.tenant_id')::int)  -- which rows are visible
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::int); -- which rows may be written

-- Step 4: act as tenant 1 (in a real app: SET LOCAL at start of each transaction)
SET ROLE app_user;
SET app.tenant_id = '1';

SELECT * FROM invoices ORDER BY id;           -- no WHERE needed!
INSERT INTO invoices VALUES (5, 2, 1, 'evil');-- tries to write into tenant 2
UPDATE invoices SET amount = 0 WHERE id = 3;  -- tenant 2's row: silently 0 rows updated
DELETE FROM invoices WHERE id = 3;            -- silently 0 rows deleted

SET app.tenant_id = '2';
SELECT * FROM invoices ORDER BY id;

RESET ROLE;
SELECT count(*) FROM invoices;                -- superuser bypasses RLS

-- ============================================
-- EXPECTED OUTPUT (real output seen)
-- ============================================

-- As tenant 1:
-- id | tenant_id | amount | note
-- ---+-----------+--------+------
-- 1  | 1         | 100    | a
-- 2  | 1         | 250    | b
--
-- INSERT (5,2,...) -> ERROR: new row violates row-level security policy for table "invoices"
-- UPDATE id=3      -> UPDATE 0   (row is invisible, not an error)
-- DELETE id=3      -> DELETE 0
--
-- As tenant 2:
-- 3 | 2 | 999 | c
-- 4 | 2 |  50 | d
--
-- After RESET ROLE (superuser): count = 4   (bypasses RLS)
-- pg_policies: tenant_isolation | cmd = ALL
```

---

## 🔍 Why This Works (3 lines max)
Once RLS is enabled the planner adds the policy's `USING` expression to every scan, so invisible rows can't leak via SELECT/UPDATE/DELETE; `WITH CHECK` rejects writes that would land outside the tenant. Tenant identity is passed through a custom GUC (`app.tenant_id`), so one policy serves all tenants.
हिंदी: USING = कौन सी rows दिखें, WITH CHECK = कौन सी rows लिखी जा सकें; tenant id session setting से आती है।

---

## ⚡ Alternative Solution

```sql
-- Per-command policies (read all of own tenant, but only admins can delete):
CREATE POLICY inv_select ON invoices FOR SELECT TO app_user
  USING (tenant_id = current_setting('app.tenant_id')::int);
CREATE POLICY inv_delete ON invoices FOR DELETE TO app_user
  USING (tenant_id = current_setting('app.tenant_id')::int
         AND current_setting('app.role', true) = 'admin');   -- 'true' = no error if unset

-- Safer in pooled connections: SET LOCAL inside a transaction (resets at COMMIT)
BEGIN;
SET LOCAL app.tenant_id = '1';
SELECT * FROM invoices;
COMMIT;

-- MySQL (no RLS): closest tool is a view + SQL SECURITY, or app-level filters
-- CREATE VIEW my_invoices AS SELECT * FROM invoices WHERE tenant_id = @tenant_id;
-- (session variable in a view is NOT allowed -> use a stored procedure or per-tenant views)
-- Not run here (MySQL side not tested for this question).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: testing as the table owner / superuser and thinking RLS is "broken"
--    Owners and superusers bypass RLS unless FORCE ROW LEVEL SECURITY (and superusers always do).
-- ✅ Test with a normal role: SET ROLE app_user;

-- ❌ Wrong: enabling RLS but creating no policy
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
--    -> non-owner roles see ZERO rows (default deny). Not a bug, add a policy.

-- ❌ Wrong: SET app.tenant_id on a pooled connection (PgBouncer) and never resetting it
--    -> next client inherits the previous tenant. ✅ Use SET LOCAL inside a transaction.

-- ❌ Wrong: current_setting('app.tenant_id') when unset -> ERROR for every query
-- ✅ current_setting('app.tenant_id', true) returns NULL (=> no rows match, fail closed)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use RLS as defence in depth for multi-tenancy — policy keyed on a session GUC set with SET LOCAL per transaction, app role is non-owner and non-BYPASSRLS, and I index tenant_id because the policy predicate runs on every query."

---

## 🔗 Related Questions
→ Q240 (Multi-tenant design) | Q243 (Views) | Q181 (JSONB operators) | Q188 (Inheritance)
