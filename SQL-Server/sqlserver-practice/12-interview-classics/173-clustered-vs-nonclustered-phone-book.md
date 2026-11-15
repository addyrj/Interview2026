---

# Q173. Clustered vs Non-Clustered Index — Explain with a Phone Book
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL InnoDB: PK is always the clustered index; PostgreSQL has no clustered index, heap + separate indexes)

---

## ❓ Question
Explain clustered vs non-clustered indexes to a non-technical person using a phone book, then show the T-SQL: create a table, a clustered and a non-clustered index, and a query that needs a key lookup.

---

## 💡 Quick Concept (2 lines only)
A clustered index IS the table, with data rows stored in key order at the leaf level (one per table). A non-clustered index is a separate sorted structure whose leaves hold the key plus a pointer (the clustering key) back to the row.
हिंदी: Clustered = table खुद key order में sorted (एक ही)। Non-clustered = अलग sorted list जो असली row की तरफ point करती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- PHONE BOOK ANALOGY
-- ============================================
-- Clustered index   = the printed phone book itself, sorted by LAST NAME.
--                     The entries (rows) ARE the pages. You can only sort the book one way.
-- Non-clustered idx = the index at the back "by phone number -> page number".
--                     Sorted differently, holds only the number + where to find the entry.
--                     Find by number: look up index, then flip to the page (= key lookup).
-- Covering index    = the back index also lists the name, so you never flip to the page.

-- ============================================
-- SETUP  (verified by sqlglot tsql parse; not executed on SQL Server)
-- ============================================

CREATE TABLE dbo.Customers (
    CustomerId INT           NOT NULL,
    LastName   NVARCHAR(50)  NOT NULL,
    FirstName  NVARCHAR(50)  NOT NULL,
    Phone      VARCHAR(20)   NOT NULL,
    City       NVARCHAR(50)  NULL,
    CONSTRAINT PK_Customers PRIMARY KEY CLUSTERED (CustomerId)   -- clustered = the data
);

INSERT INTO dbo.Customers (CustomerId, LastName, FirstName, Phone, City) VALUES
  (1, N'Sharma', N'Asha',  '9810000001', N'Delhi'),
  (2, N'Iyer',   N'Ravi',  '9810000002', N'Chennai'),
  (3, N'Khan',   N'Meera', '9810000003', N'Pune');

-- Non-clustered index on Phone: leaf = (Phone, CustomerId)
CREATE NONCLUSTERED INDEX IX_Customers_Phone ON dbo.Customers (Phone);

-- ============================================
-- QUERIES
-- ============================================

-- 1) Seek on non-clustered, then KEY LOOKUP into clustered for LastName, City
SELECT LastName, City FROM dbo.Customers WHERE Phone = '9810000002';

-- 2) Covering index removes the lookup
CREATE NONCLUSTERED INDEX IX_Customers_Phone_Cover
    ON dbo.Customers (Phone) INCLUDE (LastName, City);
SELECT LastName, City FROM dbo.Customers WHERE Phone = '9810000002';

-- EXPECTED OUTPUT (hand-checked on 3 rows; not executed on SQL Server):
-- LastName | City
-- Iyer     | Chennai
-- Plan shape (per Microsoft docs, not captured here): query 1 = Index Seek + Key Lookup;
-- query 2 = Index Seek only.
```

```text
Facts to state in the interview
- Only ONE clustered index per table (rows can be stored in one order); many non-clustered (limit 999 on modern versions).
- A table without a clustered index is a heap.
- PRIMARY KEY creates a CLUSTERED index by default, but you can choose NONCLUSTERED PK.
- Every non-clustered index carries the clustering key, so a WIDE clustering key bloats all indexes.
- Ideal clustering key: narrow, unique, static, ever-increasing (INT IDENTITY). Random GUIDs cause page splits.
```

---

## 🔍 Why This Works (3 lines max)
The clustered index defines physical (logical-ordered) storage so range scans on its key are cheap. Non-clustered indexes trade extra storage and write cost for fast alternate lookups, and each non-covered hit costs a key lookup per row. INCLUDE columns make the index covering without widening the key.
हिंदी: Clustered = data की storage order। Non-clustered = alternate रास्ता + lookup cost। INCLUDE से lookup खत्म।

---

## ⚡ Alternative Solution

```sql
-- Clustering on something other than the PK (e.g. time-series, range queries by date)
CREATE TABLE dbo.Events (
    EventId   BIGINT IDENTITY(1,1) NOT NULL,
    CreatedAt DATETIME2(0) NOT NULL,
    Payload   NVARCHAR(400) NULL,
    CONSTRAINT PK_Events PRIMARY KEY NONCLUSTERED (EventId)
);
CREATE CLUSTERED INDEX CX_Events_CreatedAt ON dbo.Events (CreatedAt, EventId);
-- Date-range scans read contiguous pages; PK lookups use the nonclustered PK.
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: "I will create a clustered index on each column I filter by" -> only one allowed.
-- Wrong: clustering on a wide or random key
--   CONSTRAINT PK PRIMARY KEY CLUSTERED (Email)            -- wide, every NC index copies it
--   CustomerId UNIQUEIDENTIFIER DEFAULT NEWID()            -- random inserts, page splits
--   Better: NEWSEQUENTIALID() or INT/BIGINT IDENTITY (Q024).
-- Wrong: "primary key = clustered index" as a law. It is only the default.
-- Wrong: indexing every column; each index costs on INSERT/UPDATE/DELETE and storage.
```

---

## 🎯 Interview Tip (1 line)
Say: "The clustered index is the table, one per table, so I pick a narrow, unique, static, increasing key because every non-clustered index carries it. Non-clustered indexes are separate B-trees pointing to the clustering key, and I use INCLUDE columns to cover hot queries and avoid key lookups, while watching write overhead. I confirm lookups in the actual execution plan."

---

## 🔗 Related Questions
→ Q102 (clustered vs non-clustered) | Q103 (covering index and INCLUDE) | Q104 (composite index order) | Q107 (reading execution plans) | Q024 (GUID vs INT keys) | Q176 (PK vs unique vs FK)
