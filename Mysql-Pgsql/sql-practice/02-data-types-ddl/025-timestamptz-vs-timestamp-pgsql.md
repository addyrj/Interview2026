---

# Q025. TIMESTAMP WITH TIME ZONE vs WITHOUT (PgSQL)
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL

---

## ❓ Question
What is the difference between `TIMESTAMP` (without time zone) and `TIMESTAMPTZ` (with time zone) in PostgreSQL? Show how the session `TimeZone` changes what you read back, what `AT TIME ZONE` does, and which one you should use by default.

---

## 💡 Quick Concept (2 lines only)
Both use 8 bytes. TIMESTAMPTZ stores an absolute instant (normalized to UTC) and renders it in the session's `TimeZone`; TIMESTAMP stores the literal date-time and silently ignores any offset you supply. The name "with time zone" is misleading — the zone itself is never stored.
हिंदी: TIMESTAMPTZ एक असली instant (UTC) रखता है और session timezone में दिखाता है; TIMESTAMP सिर्फ लिखी हुई घड़ी का समय रखता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL) — run this first
-- ============================================

SET TIME ZONE 'UTC';

CREATE TABLE flight_schedule (
  id            SERIAL PRIMARY KEY,
  flight_no     VARCHAR(10),
  departs_naive TIMESTAMP,        -- = TIMESTAMP WITHOUT TIME ZONE
  departs_tz    TIMESTAMPTZ       -- = TIMESTAMP WITH TIME ZONE
);

-- Same literal with an explicit +05:30 offset into both columns
INSERT INTO flight_schedule (flight_no, departs_naive, departs_tz)
VALUES ('AI101', '2024-06-01 12:00:00+05:30', '2024-06-01 12:00:00+05:30');

-- ============================================
-- SOLUTION
-- ============================================

-- Session in UTC. (::text so you see exactly what PostgreSQL prints)
SELECT flight_no, departs_naive::text AS naive, departs_tz::text AS tz FROM flight_schedule;
-- flight_no | naive               | tz
-- AI101     | 2024-06-01 12:00:00 | 2024-06-01 06:30:00+00      <- offset IGNORED by naive, honoured by tz

SET TIME ZONE 'Asia/Kolkata';
SELECT flight_no, departs_naive::text AS naive, departs_tz::text AS tz FROM flight_schedule;
-- AI101     | 2024-06-01 12:00:00 | 2024-06-01 12:00:00+05:30   <- same instant, shown in IST

SET TIME ZONE 'America/New_York';
SELECT flight_no, departs_naive::text AS naive, departs_tz::text AS tz FROM flight_schedule;
-- AI101     | 2024-06-01 12:00:00 | 2024-06-01 02:30:00-04      <- naive never changes; tz follows session

-- AT TIME ZONE converts between the two kinds (the result type flips!)
SET TIME ZONE 'UTC';
SELECT ('2024-06-01 12:00:00'::timestamp AT TIME ZONE 'Asia/Kolkata')::text AS naive_read_as_ist;
-- 2024-06-01 06:30:00+00         timestamp  -> timestamptz  ("this wall clock was in IST")

SELECT ('2024-06-01 12:00:00+05:30'::timestamptz AT TIME ZONE 'Asia/Kolkata')::text AS ist_wall_clock;
-- 2024-06-01 12:00:00            timestamptz -> timestamp   ("what did a clock in IST show?")

SELECT pg_typeof(departs_tz AT TIME ZONE 'UTC') AS result_type FROM flight_schedule;
-- timestamp without time zone

-- A zone written inside a literal is dropped when cast to plain timestamp:
SELECT '2024-06-01 12:00:00 Asia/Kolkata'::timestamp::text AS naive_silently_drops_zone;
-- 2024-06-01 12:00:00

-- Storage: identical
SELECT pg_column_size(departs_naive) a, pg_column_size(departs_tz) b FROM flight_schedule;
-- a | b
-- 8 | 8

-- now() returns timestamptz; localtimestamp returns plain timestamp
SELECT pg_typeof(now()) AS now_type, pg_typeof(localtimestamp) AS lt_type;
-- timestamp with time zone | timestamp without time zone

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- All results copied from PostgreSQL 18 via PGlite. Printed values for timestamptz depend
-- on the session TimeZone at the moment you run it (that is the whole point).
```

---

## 🔍 Why This Works (3 lines max)
On input, TIMESTAMPTZ converts the literal (using its offset, or the session zone if none is given) to UTC; on output it converts UTC to the session zone. TIMESTAMP does neither, so it only has meaning if every writer and reader agree on an implicit zone.
हिंदी: TIMESTAMPTZ input पर UTC में बदलता है और output पर session zone में; TIMESTAMP कुछ नहीं बदलता।

---

## ⚡ Alternative Solution

```sql
-- MySQL comparison:
--   MySQL TIMESTAMP  ~ PgSQL timestamptz  (UTC internally, session conversion, but only up to 2038, 4 bytes)
--   MySQL DATETIME   ~ PgSQL timestamp    (wall clock, no conversion)
-- (see Q024)  No MySQL type stores the original zone either.

-- Recurring local events (e.g. "every day 09:00 Mumbai time") — store the zone NAME separately:
CREATE TABLE meetings (
  id        SERIAL PRIMARY KEY,
  local_at  TIMESTAMP NOT NULL,          -- wall clock
  tz_name   TEXT NOT NULL                -- 'Asia/Kolkata' (valid name from pg_timezone_names)
);
SELECT (local_at AT TIME ZONE tz_name) AS instant_utc FROM meetings;   -- timestamptz

-- Prefer IANA names ('Asia/Kolkata') over fixed offsets ('+05:30') — names carry DST rules.
-- Note POSIX-style names flip the sign:  SET TIME ZONE 'UTC+5'  means 5 hours WEST of UTC.

-- Daily bucketing in a specific zone:
SELECT date_trunc('day', departs_tz AT TIME ZONE 'Asia/Kolkata') AS ist_day FROM flight_schedule;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: TIMESTAMP (without tz) for created_at from many servers/regions
--          each app server inserts its own local now() => mixed, unrecoverable times
-- ❌ Wrong: believing TIMESTAMPTZ "remembers" the zone you inserted from (it does not)
-- ❌ Wrong: AT TIME ZONE on a timestamptz and expecting a timestamptz back (it returns plain timestamp)
-- ❌ Wrong: comparing timestamp to timestamptz — implicit cast uses the SESSION zone, so results shift

-- ✅ Correct: timestamptz for every "moment in time" column; plain timestamp only for
--            genuine wall-clock values (store the zone name next to them).
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to TIMESTAMPTZ for any event time — it stores UTC and converts at the edges; plain TIMESTAMP means 'wall-clock, zone unknown', and AT TIME ZONE flips between the two, so I'm explicit about which zone I'm converting from."

---

## 🔗 Related Questions
→ Q024 (DATETIME vs TIMESTAMP in MySQL) | Q021 (INT sizes) | Q030 (DEFAULT constraints, e.g. DEFAULT now())
