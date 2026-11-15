---

# Q048. Running Totals
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (2012+ for ORDER BY inside SUM OVER; MySQL 8 and PostgreSQL behave the same)

---

## ❓ Question
For `Payments(PaymentId, CustomerId, PaidOn, Amount)` show a running total of amounts per customer ordered by payment date. Explain what happens when two payments share a date, and how this was done before SQL Server 2012.

---

## 💡 Quick Concept (2 lines only)
`SUM(Amount) OVER (PARTITION BY CustomerId ORDER BY PaidOn, PaymentId ROWS UNBOUNDED PRECEDING)` gives a per-customer running total. Always spell out `ROWS` — the default frame is `RANGE`, which treats rows with the same ORDER BY value as one group and is also much slower in SQL Server.
हिंदी: SUM OVER (ORDER BY ...) = running total। हमेशा ROWS लिखो; default RANGE में same date वाली rows को एक साथ गिन लेता है और धीमा भी है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Payments (
  PaymentId  INT PRIMARY KEY,
  CustomerId INT           NOT NULL,
  PaidOn     DATE          NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO Payments (PaymentId, CustomerId, PaidOn, Amount) VALUES
  (1, 101, '2024-01-05', 100),
  (2, 101, '2024-01-12', 250),
  (3, 101, '2024-01-12',  50),     -- same date as payment 2
  (4, 101, '2024-02-01', 200),
  (5, 102, '2024-01-08', 500),
  (6, 102, '2024-01-20', 300);

-- ============================================
-- RUNNING TOTAL PER CUSTOMER (explicit ROWS frame + unique tiebreaker)
-- ============================================
SELECT CustomerId, PaymentId, PaidOn, Amount,
       SUM(Amount) OVER (
         PARTITION BY CustomerId
         ORDER BY PaidOn, PaymentId
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS RunningTotal
FROM Payments
ORDER BY CustomerId, PaidOn, PaymentId;

-- EXPECTED OUTPUT (derived on SQLite; Amount shown without decimals):
-- CustomerId | PaymentId | PaidOn     | Amount | RunningTotal
-- 101        | 1         | 2024-01-05 | 100    | 100
-- 101        | 2         | 2024-01-12 | 250    | 350
-- 101        | 3         | 2024-01-12 | 50     | 400
-- 101        | 4         | 2024-02-01 | 200    | 600
-- 102        | 5         | 2024-01-08 | 500    | 500
-- 102        | 6         | 2024-01-20 | 300    | 800

-- ============================================
-- THE DEFAULT-FRAME SURPRISE (ORDER BY PaidOn only, no ROWS)
-- ============================================
SELECT PaymentId, PaidOn, Amount,
       SUM(Amount) OVER (PARTITION BY CustomerId ORDER BY PaidOn) AS RunDefault
FROM Payments
WHERE CustomerId = 101
ORDER BY PaidOn, PaymentId;

-- EXPECTED OUTPUT (derived on SQLite, same default RANGE semantics as SQL Server):
-- PaymentId | PaidOn     | Amount | RunDefault
-- 1         | 2024-01-05 | 100    | 100
-- 2         | 2024-01-12 | 250    | 400    <- both 12-Jan rows get 400 (peers are included)
-- 3         | 2024-01-12 | 50     | 400
-- 4         | 2024-02-01 | 200    | 600

-- Results derived from equivalent queries on SQLite; not executed on SQL Server.
-- Performance note (per Microsoft docs / common tuning guidance): RANGE frames use an on-disk
-- worktable in SQL Server, ROWS frames use an in-memory spool. No timings are claimed here.
```

---

## 🔍 Why This Works (3 lines max)
The window sums all rows from the partition start up to the current row in the ORDER BY order, restarting per customer. With `ROWS`, "current row" means this physical row; with the default `RANGE`, it means every row that ties on the ORDER BY value. A unique tiebreaker (`PaymentId`) makes the running order deterministic.
हिंदी: Window partition की शुरुआत से current row तक जोड़ता है। ROWS = सिर्फ यही row, RANGE = same value वाली सारी rows। Tiebreaker से क्रम पक्का रहता है।

---

## ⚡ Alternative Solution

```sql
-- Pre-2012 (or when you need to understand the logic): correlated subquery. O(n^2) — avoid on big tables.
SELECT p.PaymentId, p.Amount,
       (SELECT SUM(p2.Amount)
        FROM Payments AS p2
        WHERE p2.CustomerId = p.CustomerId
          AND (p2.PaidOn < p.PaidOn OR (p2.PaidOn = p.PaidOn AND p2.PaymentId <= p.PaymentId))) AS RunningTotal
FROM Payments AS p
WHERE p.CustomerId = 101
ORDER BY p.PaidOn, p.PaymentId;
-- EXPECTED OUTPUT (derived on SQLite): 100, 350, 400, 600

-- A supporting index lets the window avoid a sort:
CREATE INDEX IX_Payments_Customer_Date ON Payments (CustomerId, PaidOn, PaymentId) INCLUDE (Amount);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: relying on the default frame
SUM(Amount) OVER (PARTITION BY CustomerId ORDER BY PaidOn)
-- Ties on PaidOn get the same total (see RunDefault above) and RANGE is slower. Write ROWS explicitly.

-- ❌ Wrong: no tiebreaker
-- Two rows with the same PaidOn can swap places between runs, so the per-row running totals change.

-- ❌ Wrong: forgetting PARTITION BY
-- Running total then spans all customers instead of restarting for each one.

-- ❌ Wrong: running total over an ORDER BY of the outer query
-- The window's ORDER BY defines the accumulation; the outer ORDER BY only sorts the output.
```

---

## 🎯 Interview Tip (1 line)
Say: "SUM OVER with PARTITION BY, ORDER BY and an explicit ROWS UNBOUNDED PRECEDING frame plus a unique tiebreaker. I never rely on the default RANGE frame: it changes results on ties and is slower. For big tables I back it with an index on (partition column, order column) INCLUDE the measure."

---

## 🔗 Related Questions
→ Q058 (SUM/AVG OVER, ROWS vs RANGE) | Q059 (FIRST_VALUE, LAST_VALUE frame trap) | Q065 (moving average) | Q057 (LAG and LEAD)
