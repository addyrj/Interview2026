---

# Q032. XML Basics — FOR XML and nodes()
# Category: DDL + Data Types
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (native xml type; MySQL has ExtractValue/XMLTABLE-less support; PostgreSQL has xml type + xpath()/XMLTABLE)

---

## ❓ Question
(a) Return the Orders and their lines as XML with FOR XML PATH. (b) Parse an incoming XML variable into rows using the xml type methods `nodes()` and `value()`. (c) Use the classic FOR XML PATH('') trick for comma-separated lists and say what replaced it.

---

## 💡 Quick Concept (2 lines only)
FOR XML turns a result set into XML; the `xml` type methods (`nodes()`, `value()`, `query()`, `exist()`) with XPath shred XML into rows. `nodes()` gives one row per matching element, `value()` pulls a typed scalar from it.
हिंदी: FOR XML = rows से XML। nodes() = XML के हर element के लिए एक row, value() = उसमें से typed value निकालता है।

---

## ✅ Answer / Solution

```sql
-- NOT EXECUTED ON SQL SERVER: no equivalent engine for xml type methods here.
-- Output below is hand-checked from the small data; behaviour per Microsoft docs.

-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name NVARCHAR(50));
INSERT INTO Customers VALUES (1, N'Asha'), (2, N'Rohan');

-- ============================================
-- SOLUTION
-- ============================================

-- (a) Result set to XML
SELECT CustomerId AS '@id', Name AS 'Name'
FROM Customers
ORDER BY CustomerId
FOR XML PATH('Customer'), ROOT('Customers');

-- (b) Shred XML into rows
DECLARE @x XML = N'
<Orders>
  <Order id="101" customer="Asha"><Amount>250.00</Amount></Order>
  <Order id="102" customer="Rohan"><Amount>99.50</Amount></Order>
</Orders>';

SELECT
    o.n.value('@id',       'INT')           AS OrderId,
    o.n.value('@customer', 'NVARCHAR(50)')  AS Customer,
    o.n.value('(Amount)[1]','DECIMAL(10,2)') AS Amount
FROM @x.nodes('/Orders/Order') AS o(n);

-- (c) Classic string aggregation (pre-2017). Note: STUFF removes the leading comma.
SELECT STUFF((
    SELECT ',' + Name FROM Customers ORDER BY CustomerId
    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 1, '') AS Names;
-- Modern replacement (SQL Server 2017+):
SELECT STRING_AGG(Name, ',') WITHIN GROUP (ORDER BY CustomerId) AS Names FROM Customers;

-- ============================================
-- EXPECTED OUTPUT (hand-checked; not executed)
-- ============================================
-- (a) <Customers><Customer id="1"><Name>Asha</Name></Customer><Customer id="2"><Name>Rohan</Name></Customer></Customers>
-- (b) OrderId | Customer | Amount
--     101     | Asha     | 250.00
--     102     | Rohan    | 99.50
-- (c) Asha,Rohan
```

---

## 🔍 Why This Works (3 lines max)
In PATH mode a column alias starting with `@` becomes an attribute and others become child elements; ROOT adds a wrapper element. `nodes()` returns a rowset of XML fragments and `value()` must be told a single node via `[1]` and a SQL type. FOR XML PATH('') with no element name concatenates values, and TYPE keeps special characters from being entity-escaped.
हिंदी: `@` वाला alias attribute बनता है। `value()` में `[1]` ज़रूरी है क्योंकि वो एक ही value लौटाता है। PATH('') से strings जुड़ती हैं।

---

## ⚡ Alternative Solution

```sql
-- OPENXML (older, needs sp_xml_preparedocument / sp_xml_removedocument; leaks memory if you forget)
DECLARE @h INT;
EXEC sp_xml_preparedocument @h OUTPUT, @x;
SELECT * FROM OPENXML(@h, '/Orders/Order', 1) WITH (id INT, customer NVARCHAR(50));
EXEC sp_xml_removedocument @h;
-- Prefer nodes()/value(); for new APIs send JSON and use OPENJSON (Q031).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting TYPE in the PATH('') trick: '&' becomes '&amp;' in the result
SELECT ',' + Name FROM Customers FOR XML PATH('');          -- escapes special chars
-- ✅ ... FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)')

-- ❌ value() without [1] -> error: expression returns more than a singleton
SELECT o.n.value('Amount', 'DECIMAL(10,2)') FROM @x.nodes('/Orders/Order') o(n);
-- ✅ value('(Amount)[1]', ...)

-- ❌ Using .nodes() on a column in a join with CROSS APPLY omitted:
--    for a table column you need: FROM T CROSS APPLY T.XmlCol.nodes('/a') AS x(n)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use XML mostly for legacy integrations: nodes()/value() to shred it and FOR XML PATH to emit it. For new work I choose JSON with OPENJSON, and I know FOR XML PATH('') was the pre-2017 string aggregation trick that STRING_AGG replaced." Add that XML indexes (primary/secondary) exist for large xml columns.

---

## 🔗 Related Questions
→ Q006 (String functions, STRING_AGG) | Q031 (JSON) | Q063 (STRING_AGG and ordering) | Q038 (CROSS APPLY)
