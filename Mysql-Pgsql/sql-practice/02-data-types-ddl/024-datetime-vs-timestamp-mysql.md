---

# Q024. DATETIME vs TIMESTAMP — MySQL Storage Difference
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PgSQL equivalent covered in Q025)

---

## ❓ Question
In MySQL, what is the difference between DATETIME and TIMESTAMP in range, storage, and time-zone handling? When would you choose each? Show the session time-zone effect and the 2038 limit.

---

## 💡 Quick Concept (2 lines only)
TIMESTAMP stores UTC seconds since 1970 (4 bytes, range 1970-01-01 to 2038-01-19 03:14:07 UTC) and converts to/from the session time zone; DATETIME stores the literal wall-clock value (5 bytes + fraction, range 1000 to 9999) with no conversion.
हिंदी: TIMESTAMP UTC में रखकर session timezone में दिखाता है (2038 तक); DATETIME जो डालो वही रखता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+ / 9.x) — run this first
-- ============================================

SET time_zone = '+00:00';

CREATE TABLE audit_events (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  event_name  VARCHAR(50),
  occurred_dt DATETIME,                      -- wall clock, no conversion
  occurred_ts TIMESTAMP NULL,                -- UTC internally, converted per session
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: insert the same literal into both columns while session tz = UTC
INSERT INTO audit_events (event_name, occurred_dt, occurred_ts)
VALUES ('login', '2024-06-01 12:00:00', '2024-06-01 12:00:00');

SELECT event_name, occurred_dt, occurred_ts FROM audit_events;
-- event_name | occurred_dt         | occurred_ts
-- login      | 2024-06-01 12:00:00 | 2024-06-01 12:00:00

-- Step 2: read it back from a session in India (+05:30)
SET time_zone = '+05:30';
SELECT event_name, occurred_dt, occurred_ts FROM audit_events;
-- event_name | occurred_dt         | occurred_ts
-- login      | 2024-06-01 12:00:00 | 2024-06-01 17:30:00    <- TIMESTAMP shifted, DATETIME did not

-- Step 3: the 2038 limit — TIMESTAMP rejects out-of-range values (strict mode)
SET time_zone = '+00:00';
INSERT INTO audit_events (event_name, occurred_ts) VALUES ('edge',  '2038-01-19 03:14:07');   -- OK
INSERT INTO audit_events (event_name, occurred_ts) VALUES ('edge2', '2038-01-19 03:14:08');
-- ERROR 1292 (22007): Incorrect datetime value: '2038-01-19 03:14:08' for column 'occurred_ts' at row 1
INSERT INTO audit_events (event_name, occurred_ts) VALUES ('far_future', '2100-01-01 00:00:00');
-- ERROR 1292 (22007): Incorrect datetime value: '2100-01-01 00:00:00' for column 'occurred_ts' at row 1

-- DATETIME has no such limit:
INSERT INTO audit_events (event_name, occurred_dt) VALUES ('legacy_date', '9999-12-31 23:59:59');
SELECT event_name, occurred_dt FROM audit_events WHERE event_name = 'legacy_date';
-- legacy_date | 9999-12-31 23:59:59

-- Step 4: auto-maintained "last modified" column
UPDATE audit_events SET event_name = 'login2' WHERE id = 1;     -- updated_at becomes NOW()
SELECT id, event_name, updated_at FROM audit_events WHERE id = 1;
-- 1 | login2 | 2026-11-06 05:19:15   (value = time of your run)

-- Step 5: fractional seconds (both support up to 6 digits: DATETIME(6), TIMESTAMP(6))
SELECT NOW(), NOW(6);
-- 2026-11-06 05:19:15 | 2026-11-06 05:19:15.801644      (time of your run)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Copied from MySQL 9.1.0 runs (explicit_defaults_for_timestamp = ON, the 8.0+ default).
-- Storage: TIMESTAMP 4 bytes (+0-3 for fractions); DATETIME 5 bytes (+0-3), since MySQL 5.6.4.
```

---

## 🔍 Why This Works (3 lines max)
On write, TIMESTAMP converts the session-zone literal to UTC epoch seconds; on read it converts back using the reader's `time_zone`, so one stored instant looks different per session. DATETIME is just packed Y-M-D H:M:S bytes with zero zone logic, so the app must manage zones itself.
हिंदी: TIMESTAMP read/write पर session timezone से convert होता है; DATETIME कोई conversion नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- Recommended pattern for global apps: store UTC in DATETIME(6) and convert in the application
CREATE TABLE orders (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  created_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)),   -- expression default: MySQL 8.0.13+
  updated_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)) ON UPDATE CURRENT_TIMESTAMP(6)
);
-- (ON UPDATE only supports CURRENT_TIMESTAMP, so the updated_at pair above mixes local-vs-UTC.
--  Keep the server/session time_zone at UTC so CURRENT_TIMESTAMP == UTC_TIMESTAMP.)
-- (This DDL was run on MySQL 9.1.0 and accepted by MySQL 9.1.0.)

-- Use TIMESTAMP when: you want automatic conversion + auto-update columns, data stays before 2038,
--                      "instant in time" semantics (created_at, last_login).
-- Use DATETIME when: dates beyond 2038 (contract end dates, birthdays, subscription expiry),
--                     "local wall time" semantics (store 'meeting at 09:00 Mumbai time' + zone name separately),
--                     you want immunity from the server time_zone changing.

-- PostgreSQL: there is no TIMESTAMP "auto-convert on 4 bytes" — use timestamptz (8 bytes, range 4713 BC..294276 AD). See Q025.
-- 2038 boundary in epoch seconds (MySQL 9.1.0, session UTC) — 2^31 - 1 is the last valid TIMESTAMP second:
SELECT UNIX_TIMESTAMP('2038-01-19 03:14:07'), UNIX_TIMESTAMP('2038-01-19 03:14:08');
-- 2147483647 | 2147483648   <- the function itself still computes it, but a TIMESTAMP column rejects it
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: TIMESTAMP for future dates (loan maturity 2045, policy expiry 2050)
INSERT INTO policies (expires_at) VALUES ('2050-01-01 00:00:00');   -- ERROR 1292 on a TIMESTAMP column

-- ❌ Wrong: assuming TIMESTAMP "stores a time zone" — it stores UTC; the zone is NOT remembered
-- ❌ Wrong: DATETIME + NOW() when servers/session zones differ -> mixed local times in one column
-- ❌ Wrong: moving a DB (mysqldump / replica / RDS) to a server with a different time_zone and
--          expecting TIMESTAMP columns to look the same — they follow the session zone

-- ✅ Correct: pick UTC everywhere (SET GLOBAL time_zone='+00:00'), store instants in DATETIME(6)/TIMESTAMP(6),
--            convert for display in the app (or CONVERT_TZ with loaded tz tables).
```

---

## 🎯 Interview Tip (1 line)
Say: "TIMESTAMP is 4-byte UTC with session conversion and a 2038 ceiling; DATETIME is a 5-byte literal with no conversion up to year 9999 — for future dates I use DATETIME in UTC, and I standardize the server and session on UTC either way."

---

## 🔗 Related Questions
→ Q025 (TIMESTAMPTZ vs TIMESTAMP in PgSQL) | Q021 (INT sizes — same 32-bit limit idea) | Q030 (DEFAULT constraints)
