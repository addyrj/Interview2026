---

# Q011. MERGE Statement (and Its Gotchas)
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MERGE is ANSI-ish; MySQL: INSERT ... ON DUPLICATE KEY UPDATE, PostgreSQL: ON CONFLICT, MERGE only from v15)

---

## ❓ Question
Apply an `Incoming` stock feed to `ProductStock`: add quantity when the product exists, insert when it is new, and report what happened. Why do many senior engineers avoid MERGE for plain upserts?

---

## 💡 Quick Concept (2 lines only)
`MERGE target USING source ON condition` runs WHEN MATCHED / NOT MATCHED BY TARGET / NOT MATCHED BY SOURCE branches in one statement and must end with a semicolon. It has known concurrency pitfalls, so wrap it in a transaction with `HOLDLOCK` or use UPDATE-then-INSERT.
हिंदी: MERGE = upsert एक statement में, पर race conditions के लिए HOLDLOCK/transaction चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.ProductStock (
  ProductId INT NOT NULL PRIMARY KEY,
  Qty       INT NOT NULL
);

CREATE TABLE dbo.Incoming (
  ProductId INT NOT NULL,
  Qty       INT NOT NULL
);

INSERT INTO dbo.ProductStock (ProductId, Qty) VALUES (1, 10), (2, 5), (3, 0);
INSERT INTO dbo.Incoming     (ProductId, Qty) VALUES (2, 20), (3, 0), (4, 7);

-- ============================================
-- SOLUTION: MERGE with OUTPUT $action
-- ============================================

BEGIN TRANSACTION;

MERGE dbo.ProductStock WITH (HOLDLOCK) AS t
USING dbo.Incoming AS s
   ON t.ProductId = s.ProductId
WHEN MATCHED THEN
  UPDATE SET t.Qty = t.Qty + s.Qty
WHEN NOT MATCHED BY TARGET THEN
  INSERT (ProductId, Qty) VALUES (s.ProductId, s.Qty)
OUTPUT $action AS Action, inserted.ProductId, inserted.Qty;   -- the statement ends with ;

COMMIT TRANSACTION;

-- Action | ProductId | Qty
-- UPDATE | 2         | 25
-- UPDATE | 3         | 0
-- INSERT | 4         | 7
-- (row order of OUTPUT is not guaranteed)

-- Final table:
-- ProductId | Qty
-- 1         | 10     (not in feed, untouched)
-- 2         | 25
-- 3         | 0
-- 4         | 7

-- Note: final table and per-row quantities derived from an equivalent
-- INSERT ... ON CONFLICT DO UPDATE ... RETURNING on SQLite; the MERGE statement, HOLDLOCK
-- and $action are not executable there. Not executed on SQL Server; behaviour per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
The source is joined to the target on the key; matched rows follow the UPDATE branch, unmatched source rows follow the INSERT branch, and OUTPUT `$action` reports which branch fired. HOLDLOCK (serializable range lock) stops two sessions from both deciding "not matched" and inserting the same key.
हिंदी: HOLDLOCK नहीं लगाया तो दो sessions एक साथ same key insert करने की कोशिश करके duplicate key error दे सकते हैं।

---

## ⚡ Alternative Solution

```sql
-- Explicit UPDATE-then-INSERT upsert (simple, easy to reason about, widely preferred)
BEGIN TRANSACTION;

UPDATE t
SET t.Qty = t.Qty + s.Qty
FROM dbo.ProductStock AS t WITH (UPDLOCK, SERIALIZABLE)
JOIN dbo.Incoming AS s ON s.ProductId = t.ProductId;

INSERT INTO dbo.ProductStock (ProductId, Qty)
SELECT s.ProductId, s.Qty
FROM dbo.Incoming AS s
WHERE NOT EXISTS (SELECT 1 FROM dbo.ProductStock AS t WHERE t.ProductId = s.ProductId);

COMMIT TRANSACTION;
-- (Assumes one row per ProductId in Incoming; aggregate it first if the feed can repeat a key.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no semicolon after MERGE -> error ("MERGE statement must be terminated by a semicolon")

-- ❌ Wrong: duplicate keys in the source -> the same target row matched twice:
--    error "The MERGE statement attempted to UPDATE or DELETE the same row more than once".
-- ✅ De-duplicate the source first (ROW_NUMBER() or GROUP BY).

-- ❌ Wrong: no HOLDLOCK / transaction under concurrency -> intermittent PK violations.

-- ❌ Wrong: WHEN NOT MATCHED BY SOURCE THEN DELETE with a filter-less source
--    (an empty or partial feed wipes the target table).

-- ❌ Wrong: ignoring triggers: a MERGE fires insert, update and delete triggers in one statement;
--    triggers must handle multi-row inserted/deleted sets.
-- Microsoft docs and community lists note several historical MERGE bugs (check current
-- patch level) - a reason many teams standardise on UPDATE+INSERT.
```

---

## 🎯 Interview Tip (1 line)
Say: "MERGE is fine for ETL-style syncs with a deduplicated source, always with a semicolon, HOLDLOCK and a transaction. For OLTP upserts from an API I use UPDATE-then-INSERT with UPDLOCK, SERIALIZABLE or a unique index plus catching the duplicate-key error, since it's simpler and avoids MERGE's edge cases."

---

## 🔗 Related Questions
→ Q084 (Upsert procedure - MERGE vs UPDATE/INSERT) | Q010 (OUTPUT clause) | Q125 (Lock hints) | Q096 (inserted and deleted tables) | Q086 (Bulk insert and batching procedure)
