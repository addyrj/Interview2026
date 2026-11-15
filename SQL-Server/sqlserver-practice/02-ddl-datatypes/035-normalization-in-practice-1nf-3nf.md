---

# Q035. Normalization in Practice (1NF–3NF)
# Category: DDL + Data Types
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (concepts are identical in MySQL/PostgreSQL; only the DDL syntax differs)

---

## ❓ Question
A flat `OrderSheet` table repeats product and category data and stores comma-separated tags. Normalize it to 3NF: explain each violation (1NF, 2NF, 3NF) and give the final schema with foreign keys plus the query that rebuilds the original view.

---

## 💡 Quick Concept (2 lines only)
1NF: atomic values, no repeating groups. 2NF: every non-key column depends on the WHOLE key. 3NF: non-key columns depend only on the key, not on other non-key columns ("the key, the whole key, nothing but the key").
हिंदी: 1NF = हर cell में एक value। 2NF = पूरी key पर dependency। 3NF = non-key column दूसरे non-key column पर depend न करे।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- BEFORE: one wide, denormalized table
-- ============================================
CREATE TABLE OrderSheet (
    OrderId       INT,
    ProductId     INT,
    ProductName   VARCHAR(50),     -- depends only on ProductId   (2NF violation)
    CategoryId    INT,
    CategoryName  VARCHAR(50),     -- depends on CategoryId        (3NF violation)
    Qty           INT,
    Tags          VARCHAR(200),    -- 'gift,fragile'               (1NF violation)
    PRIMARY KEY (OrderId, ProductId)
);

-- ============================================
-- AFTER: 3NF
-- ============================================
CREATE TABLE Categories (
    CategoryId   INT PRIMARY KEY,
    CategoryName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Products (
    ProductId   INT PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL,
    CategoryId  INT NOT NULL REFERENCES Categories(CategoryId)
);

CREATE TABLE OrderItems (
    OrderId   INT NOT NULL,
    ProductId INT NOT NULL REFERENCES Products(ProductId),
    Qty       INT NOT NULL CHECK (Qty > 0),
    PRIMARY KEY (OrderId, ProductId)
);

CREATE TABLE OrderTags (            -- 1NF fix: one row per tag
    OrderId INT         NOT NULL,
    Tag     VARCHAR(30) NOT NULL,
    PRIMARY KEY (OrderId, Tag)
);

INSERT INTO Categories VALUES (1, 'Electronics'), (2, 'Stationery');
INSERT INTO Products   VALUES (1, 'Keyboard', 1), (2, 'Mouse', 1), (3, 'Pen', 2);

-- Rebuild the "flat" report with joins
SELECT p.Name, c.CategoryName
FROM Products p
JOIN Categories c ON c.CategoryId = p.CategoryId
ORDER BY p.ProductId;

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent query on SQLite; not executed on SQL Server)
-- ============================================
-- Name     | CategoryName
-- Keyboard | Electronics
-- Mouse    | Electronics
-- Pen      | Stationery
```

---

## 🔍 Why This Works (3 lines max)
Each fact is stored once: a category name changes in one row, not in every order line, so update/insert/delete anomalies disappear. The composite key (OrderId, ProductId) in OrderItems keeps only columns that depend on both. Foreign keys make the database enforce the relationships the flat sheet only implied.
हिंदी: हर fact एक ही जगह रहता है, इसलिए update anomaly नहीं होती। Foreign key से database खुद relationship enforce करता है।

---

## ⚡ Alternative Solution

```sql
-- Deliberate denormalization for read-heavy reporting: snapshot the price at order time
-- (this is NOT a normalization bug; the price at purchase is a different fact from the current price)
ALTER TABLE OrderItems ADD UnitPriceAtPurchase DECIMAL(10,2) NOT NULL DEFAULT 0;

-- Or an indexed view / reporting table for heavy dashboards while OLTP stays 3NF (see Q092, Q185).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Storing lists in one column
INSERT INTO OrderSheet (OrderId, ProductId, Tags) VALUES (1, 1, 'gift,fragile');
-- Searching "all fragile orders" needs LIKE '%fragile%' (not SARGable, and 'fragile-x' matches too)

-- ❌ Over-normalizing: a table per attribute (a separate City table for a free-text field) adds joins for no benefit
-- ❌ Forgetting that current Price in Products must not rewrite history of past orders
-- ✅ Normalize to 3NF, then denormalize deliberately with measurements.
```

---

## 🎯 Interview Tip (1 line)
Say: "I design to 3NF to keep one source of truth, add foreign keys and constraints, then denormalize on purpose only for measured read paths — like storing price-at-purchase, which is a distinct fact — and I never pack lists into a column; SQL Server has STRING_SPLIT for legacy data but a child table is the right fix."

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q026 (PK, UNIQUE, FK) | Q185 (Normalization vs denormalization) | Q186 (E-commerce schema design)
