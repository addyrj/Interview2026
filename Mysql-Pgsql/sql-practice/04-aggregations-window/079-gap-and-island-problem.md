---

# Q079. Gap and Island Problem
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Invoice numbers should be sequential, but some are missing. From the `invoices` table: (1) find the **islands** (continuous ranges of existing numbers), and (2) find the **gaps** (ranges of missing numbers).

---

## 💡 Quick Concept (2 lines only)
Islands: for consecutive values, `value - ROW_NUMBER()` is constant, so group by that difference. Gaps: use `LEAD()` to see the next value and report where `next - current > 1`.
हिंदी: Island = value minus ROW_NUMBER का same होना। Gap = LEAD से अगला value देखो, अंतर 1 से ज़्यादा हो तो gap है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE invoices (
  invoice_no INT PRIMARY KEY,
  customer   VARCHAR(50)
);

INSERT INTO invoices VALUES
  (1, 'Acme'), (2, 'Acme'), (3, 'Globex'),             -- island 1-3
  (7, 'Initech'), (8, 'Acme'),                          -- island 7-8
  (10, 'Globex'), (11, 'Initech'), (12, 'Acme'), (13, 'Acme'),  -- island 10-13
  (20, 'Globex');                                       -- island 20

-- ============================================
-- SOLUTION 1: ISLANDS
-- ============================================

-- Step 1: ROW_NUMBER over invoice_no (1,2,3,4...)
-- Step 2: invoice_no - rn is the SAME for consecutive numbers (the "island id")
-- Step 3: GROUP BY that id, take MIN / MAX

SELECT MIN(invoice_no) AS island_start,
       MAX(invoice_no) AS island_end,
       COUNT(*)        AS island_size
FROM (
  SELECT invoice_no,
         invoice_no - ROW_NUMBER() OVER (ORDER BY invoice_no) AS grp
  FROM invoices
) t
GROUP BY grp
ORDER BY island_start;

-- Result (verified MySQL 9.1 + PGlite):
-- island_start | island_end | island_size
-- -------------+------------+------------
-- 1            | 3          | 3
-- 7            | 8          | 2
-- 10           | 13         | 4
-- 20           | 20         | 1

-- Intermediate view of how grp is built:
-- invoice_no | rn | grp
-- 1  | 1  | 0
-- 2  | 2  | 0
-- 3  | 3  | 0
-- 7  | 4  | 3     <- jump in invoice_no, rn keeps +1 -> grp changes
-- 8  | 5  | 3
-- 10 | 6  | 4
-- 11 | 7  | 4
-- 12 | 8  | 4
-- 13 | 9  | 4
-- 20 | 10 | 10

-- ============================================
-- SOLUTION 2: GAPS (LEAD)
-- ============================================

SELECT invoice_no + 1            AS gap_start,
       next_no - 1               AS gap_end,
       next_no - invoice_no - 1  AS missing_count
FROM (
  SELECT invoice_no,
         LEAD(invoice_no) OVER (ORDER BY invoice_no) AS next_no   -- next existing number
  FROM invoices
) t
WHERE next_no - invoice_no > 1     -- last row has next_no NULL -> filtered out automatically
ORDER BY gap_start;

-- Result:
-- gap_start | gap_end | missing_count
-- ----------+---------+--------------
-- 4         | 6       | 3
-- 9         | 9       | 1
-- 14        | 19      | 6
```

---

## 🔍 Why This Works (3 lines max)
Inside an island both `invoice_no` and `ROW_NUMBER` grow by 1, so their difference stays fixed; a gap makes `invoice_no` jump while `rn` does not, so the difference changes and starts a new group. LEAD exposes the jump directly for gap detection.
हिंदी: Island के अंदर दोनों +1 बढ़ते हैं, difference fixed रहता है; gap आने पर difference बदल जाता है, नया group शुरू।

---

## ⚡ Alternative Solution

```sql
-- Individual missing numbers using a generated series
-- PostgreSQL:
SELECT n AS missing_no
FROM generate_series(1, 20) n
LEFT JOIN invoices i ON i.invoice_no = n
WHERE i.invoice_no IS NULL;

-- MySQL 8.0+ (no generate_series, use recursive CTE):
WITH RECURSIVE seq AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 20      -- note: cte_max_recursion_depth default is 1000
)
SELECT n AS missing_no
FROM seq
LEFT JOIN invoices i ON i.invoice_no = seq.n
WHERE i.invoice_no IS NULL;
-- Both return: 4,5,6,9,14,15,16,17,18,19

-- For DATES the same trick works: login_date - ROW_NUMBER()*INTERVAL '1 day' (PgSQL)
-- or DATE_SUB(login_date, INTERVAL rn DAY) (MySQL). See Q080.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ROW_NUMBER on data with duplicates -> difference is no longer constant
-- If a value repeats, rn advances but the value does not, breaking the island grouping.
-- ✅ Dedupe first (SELECT DISTINCT) or use DENSE_RANK() instead of ROW_NUMBER().

-- ❌ Wrong: forgetting that the last row has LEAD = NULL
-- (NULL - x > 1) is NULL, so the row drops out - that's fine for gaps,
-- but for "open-ended" ranges you must handle it explicitly with COALESCE.

-- ❌ Wrong: self-join "a.id + 1 = b.id" for islands - O(n^2) and hard to extend.
-- ✅ Use the window-function trick: one sort, one pass.
```

---

## 🎯 Interview Tip (1 line)
Say: "Islands are `value - ROW_NUMBER()` grouped, gaps are `LEAD(value) - value > 1`; both are one sorted pass, and an index on the sequence column makes it a pure index scan on large tables."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q067 (LEAD/LAG) | Q078 (Cumulative distinct count) | Q080 (Consecutive login streak)
