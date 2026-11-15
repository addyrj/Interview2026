---

# Q021. Data Types — INT, BIGINT, DECIMAL, MONEY, FLOAT
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: DECIMAL/DOUBLE, no MONEY; PostgreSQL: NUMERIC, has MONEY but discouraged)

---

## ❓ Question
Choose data types for a Payments table: the key, a transaction amount, an exchange rate and a score. Show why `FLOAT` is wrong for money, why `MONEY` has a rounding trap, what integer division does, and the numeric ranges you must remember.

---

## 💡 Quick Concept (2 lines only)
INT is 4 bytes (about ±2.1 billion), BIGINT 8 bytes; DECIMAL(p,s) is exact; FLOAT/REAL are approximate binary IEEE 754 values; MONEY is a fixed 4-decimal type that rounds after every operation. Use DECIMAL for money.
हिंदी: Money के लिए DECIMAL(p,s) = exact। FLOAT approximate है (0.1 बाइनरी में exact नहीं)। MONEY हर operation के बाद 4 decimals पर round करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Payments (
  PaymentId    BIGINT        IDENTITY(1,1) PRIMARY KEY,   -- high-volume table: BIGINT key
  OrderId      INT           NOT NULL,
  Amount       DECIMAL(12,2) NOT NULL,                    -- exact, 2 decimal places
  ExchangeRate DECIMAL(9,6)  NOT NULL,                    -- rates need more scale
  RiskScore    FLOAT         NULL                         -- approximate is fine for scores/measurements
);

INSERT INTO Payments (OrderId, Amount, ExchangeRate, RiskScore) VALUES
  (1, 1999.99, 83.123456, 0.7312),
  (2,   49.50, 83.123456, NULL);
GO

-- ============================================
-- SOLUTION: the classic traps
-- ============================================

-- 1) FLOAT cannot represent 0.1 exactly; DECIMAL can
DECLARE @f FLOAT = 0.0, @d DECIMAL(10,2) = 0.0, @i INT = 0;
WHILE @i < 10
BEGIN
    SET @f += 0.1;
    SET @d += 0.1;
    SET @i += 1;
END
SELECT CASE WHEN @f = 1.0 THEN 'equal' ELSE 'NOT equal' END AS FloatCheck,
       CASE WHEN @d = 1.0 THEN 'equal' ELSE 'NOT equal' END AS DecimalCheck;

-- Output:
-- FloatCheck | DecimalCheck
-- NOT equal  | equal
-- (Ten additions of 0.1 as an IEEE double give 0.9999999999999999 in Python/SQLite; SQL Server
--  FLOAT is the same 8-byte IEEE type. DECIMAL sum 1.00 is exact. Not executed on SQL Server.)

-- 2) Integer division truncates
SELECT 7 / 2 AS IntDiv, 7 / 2.0 AS DecDiv, 7 % 2 AS Remainder;
-- Output:
-- IntDiv | DecDiv   | Remainder
-- 3      | 3.500000 | 1
-- (3 and 1 are standard; the 3.500000 scale follows SQL Server's decimal division rules per docs,
--  Python Decimal gave 3.5 - not executed on SQL Server.)

-- 3) MONEY rounds intermediate results to 4 decimals
DECLARE @m MONEY = 100;
SELECT @m / 3 * 3 AS MoneyResult;
-- Output:
-- MoneyResult
-- 99.9999
-- (99.9999 reproduced with Python Decimal: 100/3 rounded to 4 places = 33.3333, times 3. Not executed
--  on SQL Server; a DECIMAL with enough scale keeps more digits, but the exact result scale is per
--  SQL Server's precision rules and not shown here.)

-- 4) Overflow: INT max is 2,147,483,647
SELECT CAST(2147483647 AS BIGINT) + 1 AS BigintOk;     -- 2147483648
-- SELECT 2147483647 + 1;   -- raises "Arithmetic overflow error converting expression to data type int."
```

---

## 🔍 Why This Works (3 lines max)
FLOAT stores a binary fraction, so most decimal fractions are approximations and `=` comparisons fail after arithmetic. DECIMAL stores digits exactly and keeps the scale you define. MONEY is really a scaled BIGINT with 4 decimals, so `/3*3` loses the last fraction, and mixed MONEY/DECIMAL arithmetic is another classic surprise.
हिंदी: FLOAT binary fraction है इसलिए = fail हो सकता है। DECIMAL exact digits रखता है। MONEY 4 decimals पर round करके 99.9999 जैसा result देता है।

---

## ⚡ Alternative Solution

```sql
-- Sizes and ranges to quote in an interview
-- TINYINT  1 byte   0 .. 255
-- SMALLINT 2 bytes  -32,768 .. 32,767
-- INT      4 bytes  -2,147,483,648 .. 2,147,483,647
-- BIGINT   8 bytes  about +-9.22 * 10^18
-- DECIMAL(p,s): 5-17 bytes by precision, p up to 38
-- BIT: 0/1/NULL

-- Store money as minor units (paise/cents) in BIGINT when you need integer-only arithmetic:
CREATE TABLE LedgerEntries (
  EntryId     BIGINT IDENTITY PRIMARY KEY,
  AmountMinor BIGINT NOT NULL   -- 199999 means 1999.99
);

-- DECIMAL result precision/scale grows in expressions; cast explicitly:
SELECT CAST(Amount * ExchangeRate AS DECIMAL(14,2)) AS AmountInBase FROM Payments;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: FLOAT for prices, then SUM() differs by fractions and reports do not tie out
CREATE TABLE BadPrices (Price FLOAT);

-- ❌ Wrong: DECIMAL with no precision, DECIMAL means DECIMAL(18,0): 19.99 is stored as 20
DECLARE @x DECIMAL = 19.99;
SELECT @x AS Truncated;     -- 20

-- ❌ Wrong: INT identity on a table that will exceed 2.1 billion rows
-- (insert fails with an arithmetic overflow; changing the type later rewrites the whole table)

-- ❌ Wrong: comparing floats with =  -> use ABS(a - b) < 0.000001 or avoid FLOAT
```

---

## 🎯 Interview Tip (1 line)
Say: "DECIMAL for anything financial, always with explicit precision and scale; BIGINT keys for high-volume tables; FLOAT only for scientific or score-like data; I avoid MONEY because of intermediate rounding. And I remember that DECLARE @x DECIMAL silently means (18,0)." Node.js tip: `mssql` returns DECIMAL as JS numbers, so large/precise values may lose precision, so pass strings if exactness matters.

---

## 🔗 Related Questions
→ Q008 (CAST vs CONVERT vs TRY_CAST) | Q013 (IDENTITY and SEQUENCE) | Q022 (VARCHAR vs NVARCHAR) | Q143 (avoiding implicit conversions)
