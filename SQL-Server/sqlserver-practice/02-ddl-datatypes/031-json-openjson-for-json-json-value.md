---

# Q031. JSON in SQL Server — OPENJSON, FOR JSON, JSON_VALUE
# Category: DDL + Data Types
# Difficulty: ⭐⭐ Medium
# DB: SQL Server 2016+ (OPENJSON needs database compatibility level 130+; Azure SQL supported). MySQL = JSON type + JSON_TABLE; PostgreSQL = jsonb + jsonb_array_elements.

---

## ❓ Question
An API sends a JSON array of orders (each with an items array). (a) Shred it into rows with OPENJSON, (b) pull a single scalar with JSON_VALUE, (c) expand the nested items, (d) return query results as JSON with FOR JSON PATH. SQL Server has no JSON data type (before 2025), so what is the storage type?

---

## 💡 Quick Concept (2 lines only)
JSON is stored as NVARCHAR(MAX) text; OPENJSON turns it into a rowset, JSON_VALUE/JSON_QUERY extract a scalar/object, and FOR JSON PATH builds JSON from a query. Validate with ISJSON.
हिंदी: JSON यहाँ NVARCHAR(MAX) में रहता है। OPENJSON = JSON से rows, FOR JSON = rows से JSON, JSON_VALUE = एक scalar value।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
DECLARE @json NVARCHAR(MAX) = N'[
  {"orderId":1,"customer":"Asha", "total":250.5, "items":["pen","book"]},
  {"orderId":2,"customer":"Rohan","total":99,    "items":["mouse"]},
  {"orderId":3,"customer":"Meera","total":410.25,"items":[]}
]';

-- ============================================
-- SOLUTION
-- ============================================

-- (a) Shred into typed columns
SELECT orderId, customer, total
FROM OPENJSON(@json)
WITH (
    orderId  INT            '$.orderId',
    customer NVARCHAR(50)   '$.customer',
    total    DECIMAL(10,2)  '$.total'
)
ORDER BY orderId;

-- (b) One scalar value (returns NVARCHAR(4000); lax mode gives NULL if path missing)
SELECT JSON_VALUE(@json, '$[0].customer') AS FirstCustomer;

-- (c) Nested array: CROSS APPLY a second OPENJSON
SELECT o.orderId, i.[value] AS item
FROM OPENJSON(@json)
     WITH (orderId INT '$.orderId', items NVARCHAR(MAX) '$.items' AS JSON) AS o
CROSS APPLY OPENJSON(o.items) AS i
ORDER BY o.orderId;

-- (d) Rows to JSON
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name NVARCHAR(50));
INSERT INTO Customers VALUES (1, N'Asha'), (2, N'Rohan');
SELECT CustomerId, Name FROM Customers FOR JSON PATH;

-- Validate before parsing untrusted input
SELECT ISJSON(@json) AS IsValid;

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent query on SQLite json_each/json_extract;
-- not executed on SQL Server)
-- ============================================
-- (a) orderId | customer | total
--     1       | Asha     | 250.50      (SQL Server shows DECIMAL(10,2) scale)
--     2       | Rohan    | 99.00
--     3       | Meera    | 410.25
-- (b) Asha
-- (c) 1 | pen
--     1 | book
--     2 | mouse          (order 3 has an empty array -> no row; use OUTER APPLY to keep it)
-- (d) [{"CustomerId":1,"Name":"Asha"},{"CustomerId":2,"Name":"Rohan"}]
-- (e) ISJSON -> 1
```

---

## 🔍 Why This Works (3 lines max)
OPENJSON is a table-valued function: with a WITH clause it maps paths to typed columns, without it returns key/value/type. AS JSON keeps a nested array as text so a second OPENJSON can expand it. FOR JSON PATH serializes the result set; column aliases with dots create nested objects.
हिंदी: WITH clause से column types तय होते हैं। Nested array के लिए `AS JSON` + दूसरा OPENJSON। FOR JSON PATH से query का result JSON बन जाता है।

---

## ⚡ Alternative Solution

```sql
-- Index a hot JSON property via a computed column
ALTER TABLE Orders ADD CustomerName AS JSON_VALUE(Payload, '$.customer');
CREATE INDEX IX_Orders_CustomerName ON Orders (CustomerName);

-- Modify JSON in place (2016+)
SELECT JSON_MODIFY(@json, '$[0].total', 300) AS Updated;

-- Node.js tip: send one JSON string as a parameter and OPENJSON it server-side
-- instead of building 500 INSERTs. (Table-valued parameters are the other option, Q076.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ JSON_VALUE for an object or array returns NULL (lax mode); use JSON_QUERY
SELECT JSON_VALUE(@json, '$[0].items');   -- NULL
SELECT JSON_QUERY(@json, '$[0].items');   -- ["pen","book"]

-- ❌ Running OPENJSON on a database with compatibility level < 130 fails
-- ❌ Filtering WHERE JSON_VALUE(Payload,'$.x') = 'y' on millions of rows with no
--    computed-column index -> full scan on every query
-- ❌ Overusing JSON for data you join/filter often; that belongs in real columns.
```

---

## 🎯 Interview Tip (1 line)
Say: "JSON is just NVARCHAR to SQL Server, so I keep relational data relational, use OPENJSON to ingest API payloads in one round trip, and index frequently-filtered paths through persisted computed columns. I validate with ISJSON and know that JSON_VALUE returns scalars only." Mention the native json type (SQL Server 2025 / Azure SQL) as newer and version-dependent.

---

## 🔗 Related Questions
→ Q022 (VARCHAR vs NVARCHAR vs MAX) | Q029 (Computed columns) | Q038 (CROSS APPLY) | Q076 (Table-valued parameters)
