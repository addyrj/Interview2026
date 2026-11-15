---

# Q152. N+1 Problem from the Application
# Category: Performance Tuning
# Difficulty: ⭐⭐ Medium
# DB: SQL Server with Node.js `mssql` (same issue in MySQL/PostgreSQL clients). Result rows derived from equivalent query on SQLite; round-trip timing not measured.

---

## ❓ Question
An Express endpoint loads 100 customers, then loops and runs one `SELECT ... WHERE CustomerId = @id` per customer (101 queries). Show the set-based fix: one JOIN, or two queries with `IN`/JSON.

---

## 💡 Quick Concept (2 lines only)
N+1 = one query for the parent list plus one query per parent for children. Each is a network round trip (+ a plan lookup), so latency scales with N. Fetch children set-based in one or two queries and group in memory.
हिंदी: N+1 = 1 query parents की + N queries children की। Round trips बढ़ जाते हैं। JOIN या एक batch query से लाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name NVARCHAR(100) NOT NULL);
CREATE TABLE Orders (
  OrderId INT PRIMARY KEY, CustomerId INT NOT NULL, Amount DECIMAL(10,2) NOT NULL,
  CONSTRAINT FK_Orders_Customers FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId)
);
CREATE INDEX IX_Orders_Customer ON Orders (CustomerId) INCLUDE (Amount);

INSERT INTO Customers VALUES (1,N'Aarav'), (2,N'Diya'), (3,N'Kabir');
INSERT INTO Orders VALUES (1,1,10), (2,1,20), (3,2,30), (4,3,40), (5,1,60);

-- ============================================
-- N+1 (what the loop sends: 1 + 3 queries here)
-- ============================================
SELECT CustomerId, Name FROM Customers;
SELECT OrderId, Amount FROM Orders WHERE CustomerId = 1;
SELECT OrderId, Amount FROM Orders WHERE CustomerId = 2;
SELECT OrderId, Amount FROM Orders WHERE CustomerId = 3;

-- ============================================
-- FIX 1: one JOIN (group rows in JS)
-- ============================================
SELECT c.CustomerId, c.Name, o.OrderId, o.Amount
FROM Customers c
LEFT JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY c.CustomerId, o.OrderId;

-- EXPECTED OUTPUT (SQLite equivalent; not executed on SQL Server):
-- CustomerId | Name  | OrderId | Amount
-- 1          | Aarav | 1       | 10.00
-- 1          | Aarav | 2       | 20.00
-- 1          | Aarav | 5       | 60.00
-- 2          | Diya  | 3       | 30.00
-- 3          | Kabir | 4       | 40.00

-- FIX 2: server-side aggregation, one JSON document per customer (SQL Server 2016+)
SELECT c.CustomerId, c.Name,
       (SELECT o.OrderId, o.Amount FROM Orders o
        WHERE o.CustomerId = c.CustomerId FOR JSON PATH) AS OrdersJson
FROM Customers c;
```

```js
// Node.js mssql: one round trip instead of N+1
const result = await pool.request().query(`
  SELECT c.CustomerId, c.Name, o.OrderId, o.Amount
  FROM dbo.Customers c LEFT JOIN dbo.Orders o ON o.CustomerId = c.CustomerId`);
const byCustomer = new Map();
for (const r of result.recordset) { /* push r into byCustomer.get(r.CustomerId) */ }
```

---

## 🔍 Why This Works (3 lines max)
A single round trip lets the optimizer use one hash/merge join with the FK index instead of N separate seeks plus N network latencies. For 100 customers at 2 ms latency that is ~200 ms of pure waiting removed (illustrative arithmetic, not a benchmark).
हिंदी: एक query = एक round trip। Loop में query = हर बार network latency।

---

## ⚡ Alternative Solution

```sql
-- Two queries with a batch of ids via a table-valued parameter (Q076) or OPENJSON
DECLARE @ids NVARCHAR(MAX) = N'[1,2,3]';
SELECT o.OrderId, o.CustomerId, o.Amount
FROM Orders o
WHERE o.CustomerId IN (SELECT CAST(value AS INT) FROM OPENJSON(@ids));   -- compat level 130+
-- ORMs: Prisma include / TypeORM relations / Sequelize include (eager) instead of lazy loading
```

---

## ⚠️ Common Mistake

```js
// ❌ await inside a for-loop over rows (also serialises everything on the pool)
for (const c of customers) { c.orders = await db.query(/* per-customer SELECT */); }
// ❌ Promise.all over 10,000 ids: exhausts the connection pool (Q153) - still N+1
// ❌ Building IN (...) lists by string concatenation: SQL injection and plan cache bloat
```

---

## 🎯 Interview Tip (1 line)
Say: "I spot N+1 by counting queries per request in logs/Query Store (same statement, huge execution_count). Fix with a join or batched IN/TVP, mind row duplication from joins, and add the FK index. ORMs need explicit eager loading."

---

## 🔗 Related Questions
→ Q036 (INNER vs LEFT vs RIGHT vs FULL JOIN) | Q076 (Table-valued parameters) | Q153 (Connection pooling with Node.js) | Q169 (ORM options)
