---

# Q147. Pagination Performance — OFFSET vs Keyset
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server 2012+ (OFFSET FETCH) (MySQL/PostgreSQL: LIMIT ... OFFSET). Timing claims not measured on SQL Server.

---

## ❓ Question
`/orders?page=50000` takes seconds while page 1 is instant. Explain why, and rewrite using keyset (seek) pagination.

---

## 💡 Quick Concept (2 lines only)
`OFFSET n ROWS` must read and discard n rows, so cost grows with page depth. Keyset pagination remembers the last key and seeks `WHERE OrderId > @LastId`, so each page costs about the same.
हिंदी: OFFSET बड़ा हुआ तो पहले के सारे rows पढ़कर फेंकता है। Keyset में last id से सीधे seek होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATE NOT NULL
);

INSERT INTO Orders VALUES
  (1,1,10,'2024-01-01'), (2,1,20,'2024-01-02'), (3,2,30,'2024-01-03'),
  (4,1,40,'2024-01-04'), (5,3,50,'2024-01-05'), (6,1,60,'2024-01-06'),
  (7,2,70,'2024-01-07'), (8,1,80,'2024-01-08'), (9,4,90,'2024-01-09'),
  (10,1,100,'2024-01-10');

-- ============================================
-- OFFSET / FETCH (page 2, size 3): reads 6 rows, returns 3
-- ============================================
SELECT OrderId, Amount
FROM Orders
ORDER BY OrderId
OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY;

-- EXPECTED OUTPUT (derived from equivalent LIMIT/OFFSET on SQLite; not executed on SQL Server):
-- OrderId | Amount
-- 4       | 40.00
-- 5       | 50.00
-- 6       | 60.00

-- ============================================
-- KEYSET: client sends the last OrderId it saw (6) -> seek, not skip
-- ============================================
DECLARE @LastId INT = 6;

SELECT TOP (3) OrderId, Amount
FROM Orders
WHERE OrderId > @LastId
ORDER BY OrderId;

-- EXPECTED OUTPUT (SQLite equivalent; not executed on SQL Server):
-- OrderId | Amount
-- 7       | 70.00
-- 8       | 80.00
-- 9       | 90.00

-- Sorting by a non-unique column (OrderDate, tie-break by OrderId): row-value compare
-- is not supported in T-SQL, so expand it by hand:
DECLARE @LastDate DATE = '2024-01-06', @LastKey INT = 6;
SELECT TOP (3) OrderId, OrderDate
FROM Orders
WHERE OrderDate > @LastDate
   OR (OrderDate = @LastDate AND OrderId > @LastKey)
ORDER BY OrderDate, OrderId;
-- supporting index: CREATE INDEX IX_Orders_Date_Id ON Orders (OrderDate, OrderId);
```

---

## 🔍 Why This Works (3 lines max)
The seek predicate on the index key jumps directly to the start position and reads only the page, so page 50,000 costs the same as page 1. OFFSET cost is O(offset + page size) on every request.
हिंदी: Keyset = index seek, cost स्थिर। OFFSET = जितना बड़ा offset उतना धीमा।

---

## ⚡ Alternative Solution

```sql
-- Deferred join: page through the narrow index first, then fetch wide rows
SELECT o.*
FROM (SELECT OrderId FROM Orders ORDER BY OrderId OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY) p
JOIN Orders o ON o.OrderId = p.OrderId
ORDER BY o.OrderId;

-- Total count: avoid COUNT(*) on every page; cache it or return "hasNext" (fetch size+1 rows).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ OFFSET without ORDER BY (syntax error in T-SQL; with TOP the order is undefined)
-- ❌ Keyset on a non-unique column without a tie-breaker: rows skipped or repeated
-- ❌ ORDER BY not matching the index: sort of the whole set per request
-- ❌ Keyset cannot jump to "page 37"; use OFFSET only for shallow, random-access paging
-- ❌ Rows inserted during OFFSET paging shift pages (duplicates/missing); keyset is stable
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET FETCH is fine for admin screens with shallow pages; for infinite scroll and APIs I use keyset with a unique, indexed sort key plus tie-breaker and return an opaque cursor token. The trade-off is no random page jumps."

---

## 🔗 Related Questions
→ Q002 (TOP WITH TIES and OFFSET FETCH) | Q083 (Pagination procedure with total count) | Q190 (Pagination in SQL Server) | Q103 (Covering index)
