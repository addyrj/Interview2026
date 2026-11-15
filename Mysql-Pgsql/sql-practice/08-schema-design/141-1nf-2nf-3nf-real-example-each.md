---

# Q141. 1NF, 2NF, 3NF — Real Example Each
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — DDL/DML run on MySQL 9.1.0 and PGlite

---

## ❓ Question
Take one messy e-commerce table and normalize it step by step to 1NF, 2NF and 3NF. For each normal form, state the rule, the anomaly it removes, and show the final schema with a query that proves it works.

---

## 💡 Quick Concept (2 lines only)
1NF: atomic values, no repeating groups. 2NF: no column depends on only PART of a composite key. 3NF: no non-key column depends on another non-key column (every column depends on "the key, the whole key, nothing but the key").
हिंदी: 1NF = atomic values, 2NF = composite key के हिस्से पर निर्भरता नहीं, 3NF = non-key column दूसरे non-key column पर निर्भर नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: the messy starting table (violates everything)
-- ============================================

CREATE TABLE orders_flat (
  order_id      INT,
  customer_name VARCHAR(50),
  phones        VARCHAR(100),      -- '98450,98451'  -> NOT atomic (1NF violation)
  product_id    INT,
  product_name  VARCHAR(50),       -- depends only on product_id, not on (order_id, product_id)  (2NF violation)
  unit_price    DECIMAL(10,2),     -- same
  quantity      INT                -- depends on the WHOLE key (order_id, product_id): fine
);
-- Customer city would be derived from pincode: pincode -> city  (3NF violation, shown below)

INSERT INTO orders_flat VALUES
  (100, 'Asha', '98450,98451', 10, 'Keyboard', 1000.00, 1),
  (100, 'Asha', '98450,98451', 11, 'Mouse',     500.00, 2),
  (101, 'Ravi', '98111',       10, 'Keyboard', 1000.00, 3);

-- Update anomaly: price change touches one row, leaves the other stale
UPDATE orders_flat SET unit_price = 1100.00 WHERE product_id = 10 AND order_id = 100;
SELECT product_id, unit_price, order_id FROM orders_flat WHERE product_id = 10 ORDER BY order_id;
-- product_id | unit_price | order_id
-- 10         | 1100.00    | 100
-- 10         | 1000.00    | 101       <- same product, two prices = inconsistent (real output)

-- ============================================
-- SOLUTION: normalized schema (1NF -> 2NF -> 3NF)
-- ============================================

-- 1NF: phones split into rows (customer_phones(customer_id, phone)) - one value per cell
-- 2NF: product attributes moved to products (key = product_id alone)
-- 3NF: city moved to pincodes because pincode -> city (transitive dependency)

CREATE TABLE pincodes (
  pincode VARCHAR(10) PRIMARY KEY,
  city    VARCHAR(50)
);
CREATE TABLE customers (
  customer_id   INT PRIMARY KEY,
  customer_name VARCHAR(50),
  pincode       VARCHAR(10),
  FOREIGN KEY (pincode) REFERENCES pincodes(pincode)
);
CREATE TABLE products (
  product_id   INT PRIMARY KEY,
  product_name VARCHAR(50),
  unit_price   DECIMAL(10,2)           -- PgSQL: NUMERIC(10,2)
);
CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_date  DATE,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE order_items (
  order_id   INT,
  product_id INT,
  quantity   INT,
  PRIMARY KEY (order_id, product_id),  -- composite key; every column depends on ALL of it
  FOREIGN KEY (order_id)   REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO pincodes VALUES ('560001','Bengaluru'), ('110001','Delhi');
INSERT INTO customers VALUES (1,'Asha','560001'), (2,'Ravi','110001');
INSERT INTO products VALUES (10,'Keyboard',1000.00), (11,'Mouse',500.00);
INSERT INTO orders VALUES (100,1,'2024-05-01'), (101,2,'2024-05-02');
INSERT INTO order_items VALUES (100,10,1), (100,11,2), (101,10,3);

SELECT o.order_id, c.customer_name, p.product_name, oi.quantity,
       p.unit_price * oi.quantity AS line_total
FROM orders o
JOIN customers c    ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
JOIN products p     ON p.product_id  = oi.product_id
ORDER BY o.order_id, p.product_id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- order_id | customer_name | product_name | quantity | line_total
-- 100      | Asha          | Keyboard     | 1        | 1000.00
-- 100      | Asha          | Mouse        | 2        | 1000.00
-- 101      | Ravi          | Keyboard     | 3        | 3000.00

UPDATE products SET unit_price = 1100.00 WHERE product_id = 10;   -- ONE row changed, no anomaly
-- city lookup:  customers JOIN pincodes -> Asha/560001/Bengaluru, Ravi/110001/Delhi
```

---

## 🔍 Why This Works (3 lines max)
Each fact is stored exactly once: price in products, city in pincodes, phone as its own row, so updates, inserts and deletes cannot create contradictions. The JOIN reassembles the original wide view when needed.
हिंदी: हर fact सिर्फ एक जगह store होता है, इसलिए update/insert/delete anomalies नहीं बनतीं; JOIN से पुराना wide view वापस मिल जाता है।

---

## ⚡ Alternative Solution

```sql
-- 1NF alternatives for multi-valued phones (instead of a child table):
-- PgSQL : phones TEXT[]  or  JSONB   (arrays are technically non-atomic; fine if you never query inside)
-- MySQL : phones JSON    (multi-valued index on JSON array available in 8.0.17+)
-- The child table customer_phones(customer_id, phone, PRIMARY KEY(customer_id, phone)) is the textbook answer.

-- Spot a 2NF/3NF violation quickly:
--   "If I change this one real-world fact, how many rows must I update?"  More than one -> not normalized.

-- BCNF (stricter 3NF): every determinant must be a candidate key.
-- Beyond 3NF most OLTP designs stop; OLAP/reporting tables are deliberately denormalized (Q142).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: thinking 2NF applies to tables with a single-column key
--    A table with a single-column primary key is automatically in 2NF (no partial dependency possible).

-- ❌ Wrong: storing the unit price ONLY in products, then recomputing old order totals
--    order_items has no price -> changing products.unit_price rewrites history of past orders!
-- ✅ Real systems add order_items.unit_price_at_purchase (a deliberate, justified copy - Q142).

-- ❌ Wrong: city, state, pincode all in customers "because it's easier"
--    -> 3NF violation (pincode -> city); fine only if you consciously accept the redundancy.
```

---

## 🎯 Interview Tip (1 line)
Say: "I normalize to 3NF by default to avoid update anomalies, then denormalize deliberately with measured reasons; and I always snapshot values like price at purchase time because that is business history, not redundancy."

---

## 🔗 Related Questions
→ Q142 (When to denormalize) | Q143 (Many-to-many design) | Q146 (Audit log table) | Q160 (UUID vs BIGINT)
