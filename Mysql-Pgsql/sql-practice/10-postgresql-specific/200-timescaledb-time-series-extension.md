---

# Q200. TimescaleDB — Time-Series Extension
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (TimescaleDB extension)

---

## ❓ Question
We ingest 50k sensor readings/second into PostgreSQL and queries are mostly "last N hours" and hourly averages. What does TimescaleDB add over plain PostgreSQL, and what does the plain-PostgreSQL equivalent look like?

---

## 💡 Quick Concept (2 lines only)
TimescaleDB turns a table into a hypertable that is auto-partitioned into time chunks, adding `time_bucket`, continuous aggregates, native compression and retention policies. It is an extension, so you still use normal SQL and PgSQL tooling.
हिंदी: TimescaleDB table को time-chunks में auto-partition (hypertable) करता है और time_bucket, continuous aggregates, compression, retention देता है; SQL वही रहती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
-- TimescaleDB is NOT available in PGlite (CREATE EXTENSION timescaledb ->
-- "extension is not available"), so every timescaledb_* call below is NOT RUN.
-- The plain-PostgreSQL equivalent (declarative partitioning + date_bin) WAS run.

-- ============================================
-- SOLUTION A: TimescaleDB  [not run]
-- ============================================
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE readings (
  device_id INT         NOT NULL,
  ts        TIMESTAMPTZ NOT NULL,
  temp      NUMERIC(5,2)
);
SELECT create_hypertable('readings', 'ts', chunk_time_interval => INTERVAL '1 day');

-- hourly average per device
SELECT time_bucket('1 hour', ts) AS bucket, device_id, AVG(temp)
FROM readings WHERE ts > now() - INTERVAL '24 hours'
GROUP BY 1, 2 ORDER BY 1;

-- auto-maintained rollup
CREATE MATERIALIZED VIEW readings_hourly WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', ts) AS bucket, device_id, AVG(temp) AS avg_temp
FROM readings GROUP BY 1, 2;

SELECT add_compression_policy('readings', INTERVAL '7 days');
SELECT add_retention_policy('readings',   INTERVAL '90 days');

-- ============================================
-- SOLUTION B: plain PostgreSQL (this part was RUN on PGlite)
-- ============================================
CREATE TABLE readings (device_id INT, ts TIMESTAMPTZ NOT NULL, temp NUMERIC(5,2))
  PARTITION BY RANGE (ts);
CREATE TABLE readings_2024_01 PARTITION OF readings FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE readings_2024_02 PARTITION OF readings FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
INSERT INTO readings VALUES
  (1,'2024-01-01 00:10+00',20.0), (1,'2024-01-01 00:50+00',22.0),
  (1,'2024-01-01 01:20+00',24.0), (2,'2024-01-01 00:30+00',30.0),
  (1,'2024-02-01 00:05+00',19.0);

SET TIME ZONE 'UTC';
SELECT device_id,
       date_bin('1 hour', ts, TIMESTAMPTZ '2024-01-01') AS bucket,   -- PG14+, like time_bucket
       AVG(temp)::numeric(5,2) AS avg_temp
FROM readings
WHERE ts >= '2024-01-01' AND ts < '2024-01-02'
GROUP BY 1, 2 ORDER BY 1, 2;

EXPLAIN (COSTS OFF) SELECT * FROM readings WHERE ts >= '2024-02-01' AND ts < '2024-02-10';

CREATE INDEX idx_readings_ts_brin ON readings USING brin (ts);   -- tiny index for append-only time data
DROP TABLE readings_2024_01;                                      -- instant "retention"

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18, Solution B)
-- ============================================
-- device_id | bucket              | avg_temp
-- 1         | 2024-01-01 00:00:00 | 21.00
-- 1         | 2024-01-01 01:00:00 | 24.00
-- 2         | 2024-01-01 00:00:00 | 30.00
--
-- EXPLAIN: "Seq Scan on readings_2024_02 readings" -> partition pruning: only Feb partition touched
-- After DROP TABLE readings_2024_01: SELECT count(*) FROM readings -> 1
```

---

## 🔍 Why This Works (3 lines max)
Time-chunked partitions mean recent-data queries touch only a few small chunks (pruning) and old data is dropped by detaching or dropping whole chunks instead of slow DELETE plus VACUUM. TimescaleDB automates chunk creation, columnar compression of old chunks and incremental rollups that you would otherwise script by hand.
हिंदी: Time chunks से query सिर्फ ज़रूरी partitions छूती है और पुराना data DROP से तुरंत हटता है; TimescaleDB यह सब automate करता है।

---

## ⚡ Alternative Solution

```sql
-- Native PostgreSQL helpers for time-series (no extension):
--   BRIN index on ts, declarative partitioning (pg_partman automates creating partitions),
--   date_trunc('hour', ts) for calendar buckets, date_bin for arbitrary-width buckets,
--   materialized views (Q193) + pg_cron for rollups.

-- MySQL: RANGE partitioning by TO_DAYS(ts) / UNIX_TIMESTAMP(ts) + partition drop for retention;
-- no hypertables or continuous aggregates. Dedicated TSDBs (InfluxDB, ClickHouse) are the usual alternative at huge scale.
--   ALTER TABLE readings DROP PARTITION p202401;     -- (not run)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Time-series table with a random UUID primary key and no time partitioning
-- Inserts scatter across the whole B-tree, and retention = huge DELETE + bloat (see Q191)
-- ✅ Partition/hypertable by time, cluster the key as (device_id, ts), drop old chunks

-- ❌ Forgetting that a unique index on a partitioned/hypertable must include the time column
-- ❌ Assuming the extension is available on managed services: check your provider
--    (licensing: some TimescaleDB features are not in the Apache-only build)
```

---

## 🎯 Interview Tip (1 line)
Say: "For time-series on Postgres I partition by time and drop old partitions for retention; TimescaleDB gives hypertables, continuous aggregates and compression on top, which I would adopt when ingest volume or rollup maintenance becomes painful, while confirming extension support on our managed provider."

---

## 🔗 Related Questions
→ Q193 (Materialized views) | Q191 (VACUUM) | Q241 (Sharding)
