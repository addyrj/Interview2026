---

# Q048. Multi-Table JOIN (3+ Tables)
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Given customers, orders, order_items and products, list for each order the customer name, product names and line totals. Then find revenue per product category, keeping categories that had no sales.

---

## 💡 Quick Concept (2 lines only)
Chain joins along foreign keys: each JOIN adds one table to the running result, left to right. Use INNER JOIN for mandatory links and LEFT JOIN for optional ones; once a LEFT JOIN appears, later joins on the optional side must also be LEFT or they silently drop the NULL rows.
हिंदी: Foreign keys के साथ JOIN chain करो, हर JOIN एक table जोड़ता है। Optional side पर LEFT JOIN, आगे INNER JOIN मत लगाओ वरना rows गायब।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name        VARCHAR(100)
);

CREATE TABLE categories (
  category_id   INT PRIMARY KEY,
  category_name VARCHAR(50)
);

CREATE TABLE products (
  product_id   INT PRIMARY KEY,
  product_name VARCHAR(100),
  category_id  INT,
  unit_price   DECIMAL(10,2)
);

CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT,
  order_date  DATE
);

CREATE TABLE order_items (
  order_id   INT,
  product_id INT,
  quantity   INT,
  PRIMARY KEY (order_id, product_id)
);

INSERT INTO customers  VALUES (1, 'Asha'), (2, 'Rohan');
INSERT INTO categories VALUES (1, 'Electronics'), (2, 'Books'), (3, 'Toys');   -- Toys: no sales
INSERT INTO products   VALUES
  (10, 'Headphones', 1, 2000.00),
  (11, 'USB Cable',  1,  300.00),
  (12, 'SQL Book',   2,  500.00),
  (13, 'Puzzle',     3,  250.00);
INSERT INTO orders VALUES (1, 1, '2024-03-01'), (2, 1, '2024-03-05'), (3, 2, '2024-03-07');
INSERT INTO order_items VALUES
  (1, 10, 1),
  (1, 11, 2),
  (2, 12, 1),
  (3, 10, 2),
  (3, 12, 3);

-- ============================================
-- SOLUTION 1: order -> customer -> items -> product (4 tables)
-- ============================================

-- Step 1: orders -> customers      (who placed it)
-- Step 2: orders -> order_items    (what lines it has)
-- Step 3: order_items -> products  (name + price)
SELECT o.order_id,
       c.name                      AS customer,
       p.product_name,
       oi.quantity,
       oi.quantity * p.unit_price  AS line_total
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
JOIN products    p  ON p.product_id  = oi.product_id
ORDER BY o.order_id, p.product_name;
-- Output:
-- order_id | customer | product_name | quantity | line_total
-- 1        | Asha     | Headphones   | 1        | 2000.00
-- 1        | Asha     | USB Cable    | 2        | 600.00
-- 2        | Asha     | SQL Book     | 1        | 500.00
-- 3        | Rohan    | Headphones   | 2        | 4000.00
-- 3        | Rohan    | SQL Book     | 3        | 1500.00

-- ============================================
-- SOLUTION 2: revenue per category, categories with no sales kept
-- ============================================

-- Start from categories (the side we must keep) and LEFT JOIN down the chain.
-- Every later join is LEFT too; an INNER JOIN here would delete 'Toys' again.
SELECT cat.category_name,
       COALESCE(SUM(oi.quantity * p.unit_price), 0.00) AS revenue
FROM categories cat
LEFT JOIN products    p  ON p.category_id = cat.category_id
LEFT JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY cat.category_id, cat.category_name
ORDER BY revenue DESC;
-- Output:
-- category_name | revenue
-- Electronics   | 6600.00
-- Books         | 2000.00
-- Toys          | 0.00

-- ============================================
-- ORDER TOTALS PER CUSTOMER (4 tables, 3 joins)
-- ============================================

SELECT c.name,
       COUNT(DISTINCT o.order_id)        AS orders,       -- DISTINCT: items multiply order rows
       SUM(oi.quantity * p.unit_price)   AS total_spent
FROM customers c
JOIN orders      o  ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
JOIN products    p  ON p.product_id  = oi.product_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
-- Output:
-- name  | orders | total_spent
-- Asha  | 2      | 3100.00
-- Rohan | 1      | 5500.00
```

---

## 🔍 Why This Works (3 lines max)
Each ON clause follows one foreign key, so rows multiply only along one-to-many edges (order -> items). Starting the chain from the table you must preserve (categories) and using LEFT JOIN all the way down keeps unsold categories with a NULL sum that COALESCE turns into 0.
हिंदी: हर JOIN एक foreign key follow करता है। जिस table की सारी rows चाहिए उससे शुरू करो और नीचे तक LEFT JOIN रखो।

---

## ⚡ Alternative Solution

```sql
-- USING syntax when join columns share a name (works in MySQL and PostgreSQL)
SELECT o.order_id, c.name, oi.product_id
FROM orders o
JOIN customers   c  USING (customer_id)
JOIN order_items oi USING (order_id)
ORDER BY o.order_id, oi.product_id;
-- Output:
-- order_id | name  | product_id
-- 1        | Asha  | 10
-- 1        | Asha  | 11
-- 2        | Asha  | 12
-- 3        | Rohan | 10
-- 3        | Rohan | 12

-- Differences worth knowing:
--  * With USING, SELECT * returns the join column once; with ON it appears twice (same in both DBs).
--  * USING needs the same column name on both sides; ON works for any expression.
--  * The optimizer may reorder INNER JOINs freely (see Q051), but LEFT JOIN order is semantic.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: INNER JOIN after a LEFT JOIN cancels the LEFT JOIN
SELECT cat.category_name, SUM(oi.quantity)
FROM categories cat
LEFT JOIN products p ON p.category_id = cat.category_id
JOIN order_items oi ON oi.product_id = p.product_id     -- NULL product_id never matches -> 'Toys' vanishes
GROUP BY cat.category_name;
-- ✅ Use LEFT JOIN for every hop after the optional one

-- ❌ Wrong: SUM(unit_price) across order_items rows of a joined order header
--    (header-level columns repeat per item row -> double counting)
-- ✅ Aggregate at the correct grain: SUM(quantity * unit_price) over item rows

-- ❌ Wrong: forgetting one ON clause -> accidental cross join of two tables
```

---

## 🎯 Interview Tip (1 line)
Say: "I walk the foreign-key path, keep the preserved side on the left with LEFT JOINs all the way down, watch the grain so one-to-many joins don't inflate aggregates, and confirm indexes exist on every FK column used in ON."

---

## 🔗 Related Questions
→ Q041 (INNER JOIN) | Q047 (JOIN with aggregation) | Q051 (Join order) | Q052 (A not in B)
