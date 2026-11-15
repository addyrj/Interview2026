
---

# Q133. THROW vs RAISERROR
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL: RAISE EXCEPTION; MySQL: SIGNAL SQLSTATE)

---

## ❓ Question
Raise a custom "insufficient stock" error from a procedure. Compare THROW and RAISERROR: syntax, error numbers, severity, formatting, behaviour on the batch and in CATCH, and which one you use in new code.

---

## 💡 Quick Concept (2 lines only)
THROW (2012+) is the modern statement: custom number >= 50000, always severity 16, aborts the batch, and `THROW;` alone rethrows in CATCH. RAISERROR is legacy: printf-style formatting, chosen severity, can be non-fatal (severity 0-10), and requires WITH NOWAIT for immediate progress messages.
हिंदी: नए code में THROW use करो (number >= 50000, severity हमेशा 16)। RAISERROR पुराना है, पर printf formatting और WITH NOWAIT जैसी चीज़ों के लिए अभी भी काम आता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Inventory (
  Sku   VARCHAR(20) PRIMARY KEY,
  Stock INT NOT NULL
);
INSERT INTO dbo.Inventory VALUES ('SKU-A', 5);
GO

-- ============================================
-- SOLUTION: THROW with formatted message via FORMATMESSAGE / CONCAT
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_Reserve @Sku VARCHAR(20), @Qty INT
AS
BEGIN
  SET NOCOUNT ON; SET XACT_ABORT ON;
  DECLARE @stock INT = (SELECT Stock FROM dbo.Inventory WHERE Sku = @Sku);

  IF @stock IS NULL
    THROW 50010, 'Unknown SKU.', 1;

  IF @stock < @Qty
  BEGIN
    DECLARE @msg NVARCHAR(2048) = CONCAT('Insufficient stock for ', @Sku, ': have ', @stock, ', need ', @Qty);
    THROW 50011, @msg, 1;                    -- number, message, state
  END

  UPDATE dbo.Inventory SET Stock -= @Qty WHERE Sku = @Sku;
END;
GO

EXEC dbo.usp_Reserve 'SKU-A', 8;
-- Msg 50011, Level 16, State 1: Insufficient stock for SKU-A: have 5, need 8

-- ============================================
-- RAISERROR equivalent (legacy style)
-- ============================================
RAISERROR('Insufficient stock for %s: have %d, need %d', 16, 1, 'SKU-A', 5, 8);   -- error number is 50000

-- Immediate progress message (THROW cannot do this)
RAISERROR('Processed batch %d', 0, 1, 3) WITH NOWAIT;
```

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server; behaviour per Microsoft docs.
-- THROW 50011 -> "Msg 50011, Level 16, State 1, Procedure usp_Reserve ... Insufficient stock for SKU-A: have 5, need 8"
-- RAISERROR ad hoc message -> error number 50000 (documented default for ad hoc messages)
-- Message string build checked on SQLite with equivalent concatenation:
--   'Insufficient stock for SKU-A: have 5, need 8'
```

| | THROW | RAISERROR |
|---|---|---|
| Introduced | 2012 | legacy |
| Error number | you choose, >= 50000 | 50000 for ad hoc, or sys.messages id |
| Severity | always 16 | you choose (0-25) |
| Formatting | none (build string yourself) | printf-style %s %d |
| Rethrow in CATCH | `THROW;` keeps original number | creates a NEW error |
| Previous statement | must end with `;` | no such rule |
| Respects XACT_ABORT | yes, aborts batch | does not abort by itself |

---

## 🔍 Why This Works (3 lines max)
THROW produces a real, catchable error with a stable number the application can map, and it terminates the batch so later statements do not run on bad state. RAISERROR is still useful for non-fatal informational output and `WITH NOWAIT`.
हिंदी: THROW असली error देता है जिसका number app पहचान सकता है और batch रुक जाता है। RAISERROR अब सिर्फ़ info messages और NOWAIT के लिए ठीक है।

---

## ⚡ Alternative Solution

```sql
-- Register reusable messages and format them (Azure SQL Database does not support sp_addmessage; verify for your target)
EXEC sp_addmessage @msgnum = 50020, @severity = 16, @msgtext = N'Insufficient stock for %s: have %d, need %d';
DECLARE @m NVARCHAR(2048) = FORMATMESSAGE(50020, 'SKU-A', 5, 8);
THROW 50020, @m, 1;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: previous statement not terminated; THROW then is parsed as a savepoint/name argument
SELECT 1
THROW 50001, 'boom', 1;          -- error: incorrect syntax near 'THROW'. Use ; before THROW.

-- ❌ Wrong: THROW with number below 50000. Custom errors must be >= 50000.
-- ❌ Wrong: RAISERROR(@msg, ...) where @msg contains a user string with '%' (format-string bug);
--          use RAISERROR('%s', 16, 1, @msg).
-- ❌ Wrong: rethrowing with RAISERROR in CATCH and losing the original ERROR_NUMBER.
```

---

## 🎯 Interview Tip (1 line)
Say: "New code uses THROW; my API layer switches on e.number (50011 -> 409, 50010 -> 404) so the numbers are a contract I document. I keep RAISERROR only for WITH NOWAIT progress output or when I need severity below 11."

---

## 🔗 Related Questions
→ Q073 (TRY...CATCH inside procedures) | Q132 (TRY...CATCH complete guide) | Q134 (Error logging table pattern) | Q070 (RETURN codes vs OUTPUT vs result sets)
