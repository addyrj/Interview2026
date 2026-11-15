---

# Q023. DECIMAL vs FLOAT vs DOUBLE — For Money
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (PgSQL names: NUMERIC, REAL, DOUBLE PRECISION)

---

## ❓ Question
Which numeric type should you use for money, and why? Show the rounding errors of FLOAT/DOUBLE, the exact behaviour of DECIMAL, and the precision/scale overflow rules in MySQL and PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
DECIMAL(p,s) / NUMERIC is exact fixed-point decimal arithmetic — use it for money. FLOAT/DOUBLE (REAL/DOUBLE PRECISION in PgSQL) are binary IEEE-754 approximations: fast and wide-ranged but values like 0.1 cannot be represented exactly.
हिंदी: पैसे के लिए हमेशा DECIMAL/NUMERIC; FLOAT/DOUBLE approximate होते हैं (0.1+0.2 ≠ 0.3)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL) — run this first
-- ============================================

CREATE TABLE wallet_txn (
  id         INT PRIMARY KEY,
  amount_dec DECIMAL(12,2),   -- exact: 10 digits before the point, 2 after
  amount_flt FLOAT,           -- 4-byte binary approx (~7 digits)
  amount_dbl DOUBLE           -- 8-byte binary approx (~15-16 digits)
);

INSERT INTO wallet_txn VALUES
  (1, 0.10, 0.10, 0.10),
  (2, 0.20, 0.20, 0.20),
  (3, 19.99, 19.99, 19.99);

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Summing 0.10 + 0.20 in each type
SELECT SUM(amount_dec) AS sum_dec, SUM(amount_flt) AS sum_flt, SUM(amount_dbl) AS sum_dbl
FROM wallet_txn WHERE id IN (1, 2);
-- sum_dec | sum_flt             | sum_dbl
-- 0.30    | 0.30000000447034836 | 0.30000000000000004

-- 2) Equality test
SELECT 0.1 + 0.2 = 0.3 AS decimal_literal_equal,      -- MySQL literals 0.1 are DECIMAL
       0.1e0 + 0.2e0 = 0.3e0 AS double_equal;         -- 1e0 forces DOUBLE
-- decimal_literal_equal | double_equal
-- 1                     | 0

-- 3) Equality on a FLOAT column fails to match what you typed
SELECT id FROM wallet_txn WHERE amount_flt = 0.1;      -- Empty set: stored FLOAT is 0.100000001490116...
SELECT id FROM wallet_txn WHERE amount_dec = 0.10;     -- returns id 1 (exact match)

-- 4) Tax calculation stays exact with DECIMAL
SELECT ROUND(SUM(amount_dec) * 1.18, 2) AS with_gst FROM wallet_txn;
-- with_gst
-- 23.94              (20.29 * 1.18 = 23.9422 -> 23.94)

-- 5) FLOAT loses cents at large values (7 significant digits)
SELECT CAST(10000000.01 AS FLOAT) AS float_loses_cents;
-- 10000000

-- 6) Precision/scale overflow (strict mode = ERROR)
INSERT INTO wallet_txn VALUES (4, 12345678901.999, 0, 0);
-- ERROR 1264 (22003): Out of range value for column 'amount_dec' at row 1
-- (with sql_mode='' it clamps to 9999999999.99 — verified)

-- 7) Division keeps scale in DECIMAL, DOUBLE keeps digits
SELECT 1/3 AS dec_div, 1e0/3 AS dbl_div;
-- 0.3333 | 0.3333333333333333

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- All numbers above were copied from MySQL 9.1.0 runs. (div_precision_increment = 4,
-- so 1/3 shows 4 decimals.)
```

---

## 🔍 Why This Works (3 lines max)
DECIMAL stores decimal digits (MySQL packs 9 digits per 4 bytes; PgSQL NUMERIC is arbitrary-precision base-10000), so base-10 fractions stay exact. FLOAT/DOUBLE keep a binary mantissa; 0.1 is a repeating fraction in base 2, so tiny errors appear and grow when summed.
हिंदी: DECIMAL base-10 digits रखता है इसलिए exact; FLOAT/DOUBLE binary में 0.1 सही store नहीं कर पाते।

---

## ⚡ Alternative Solution

```sql
-- ============================================
-- PostgreSQL version (verified on PostgreSQL 18 via PGlite)
-- ============================================
CREATE TABLE wallet_txn (id INT PRIMARY KEY, amount_num NUMERIC(12,2), amount_real REAL, amount_dbl DOUBLE PRECISION);
INSERT INTO wallet_txn VALUES (1,0.10,0.10,0.10),(2,0.20,0.20,0.20),(3,19.99,19.99,19.99);

SELECT SUM(amount_num) AS sum_num, SUM(amount_real) AS sum_real, SUM(amount_dbl) AS sum_dbl
FROM wallet_txn WHERE id IN (1,2);
-- 0.30 | 0.3 | 0.30000000000000004      <- REAL prints 0.3 (shortest round-trip text) but is still inexact

SELECT 0.1 + 0.2 = 0.3 AS numeric_literal_equal, 0.1::float8 + 0.2::float8 = 0.3::float8 AS double_equal;
-- true | false

SELECT id FROM wallet_txn WHERE amount_real = 19.99;   -- (0 rows) real vs numeric literal => compared as float8
SELECT id FROM wallet_txn WHERE amount_dbl  = 19.99;   -- id 3  (literal converts to the same double)
SELECT id FROM wallet_txn WHERE amount_num  = 19.99;   -- id 3

INSERT INTO wallet_txn VALUES (4, 12345678901.999, 0, 0);   -- ERROR: numeric field overflow
SELECT 1::numeric/3 AS num_div, 1::float8/3 AS dbl_div;
-- 0.33333333333333333333 | 0.3333333333333333           <- NUMERIC division gives ~20 digits
SELECT 'NaN'::numeric, 'Infinity'::float8;                 -- both types allow special values

-- Practical alternative: store money as integer minor units (paise/cents) in BIGINT
CREATE TABLE payments (id BIGINT PRIMARY KEY, amount_paise BIGINT NOT NULL, currency CHAR(3) NOT NULL);
-- 19.99 => 1999. Exact, fast, no rounding mode surprises; format in the app.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: FLOAT/DOUBLE for balances, prices, tax
CREATE TABLE invoice (total FLOAT);   -- SUM() drifts: 0.30000000447034836 in the test above
-- ❌ Wrong: WHERE price = 0.1 on a FLOAT column  -> returns no rows
-- ❌ Wrong: DECIMAL(10,2) for currencies with 3-4 decimals (KWD, crypto, FX rates) or for
--          intermediate calcs (round only at the end)
-- ❌ Wrong: DECIMAL without precision in MySQL -> DECIMAL(10,0): 12.75 becomes 13

-- ✅ Correct: DECIMAL(p,s)/NUMERIC with room to spare (e.g. DECIMAL(19,4)) or integer minor units
```

---

## 🎯 Interview Tip (1 line)
Say: "Money is DECIMAL/NUMERIC (or integer minor units) because it's exact base-10; FLOAT/DOUBLE are for measurements and analytics where tiny binary error is acceptable — and I round only at the end of the calculation, never compare floats with =."

---

## 🔗 Related Questions
→ Q021 (INT vs BIGINT) | Q022 (VARCHAR/TEXT/CHAR) | Q030 (CHECK constraints for amounts >= 0) | Q029 (IDENTITY)
