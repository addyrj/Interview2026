---

# Q148. Time-Series Data Schema Design
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (Postgres WASM)

---

## ❓ Question
Design a table for IoT sensor readings (millions of rows per day). Queries are mostly "last N hours for sensor X" and "hourly average per sensor". Show the primary key choice, a roll-up table for dashboards, and how to keep the table from growing forever.

---

## 💡 Quick Concept (2 lines only)
Time-series = append-only, always queried by time range. Cluster rows by (entity, time), use a narrow row, roll old data up into coarser buckets, and drop old data by partition instead of DELETE.
हिंदी: Time-series data append-only होता है और हमेशा time range से query होता है — (sensor, time) पर cluster करो, पुराना data partition drop से हटाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE sensor_readings (
  sensor_id   INT NOT NULL,
  recorded_at TIMESTAMP NOT NULL,
  temperature DECIMAL(5,2),
  PRIMARY KEY (sensor_id, recorded_at)   -- InnoDB clusters rows by PK: one sensor's readings sit together, in time order
);

INSERT INTO sensor_readings VALUES
  (1,'2024-05-01 10:00:00',21.5),(1,'2024-05-01 10:30:00',22.0),(1,'2024-05-01 11:10:00',23.5),
  (2,'2024-05-01 10:05:00',19.0),(2,'2024-05-01 11:45:00',20.5),(1,'2024-05-02 09:00:00',20.0);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: Raw table above (narrow row, no surrogate id, no secondary index)
-- Step 2: Roll-up table for dashboards (1 row per sensor per hour)

CREATE TABLE sensor_readings_hourly (
  sensor_id    INT NOT NULL,
  bucket_start DATETIME NOT NULL,
  avg_temp     DECIMAL(5,2),
  min_temp     DECIMAL(5,2),
  max_temp     DECIMAL(5,2),
  sample_cnt   INT,
  PRIMARY KEY (sensor_id, bucket_start)
);

-- Step 3: Populate (run from a scheduled job, e.g. every hour for the previous hour)
INSERT INTO sensor_readings_hourly
SELECT sensor_id,
       DATE_FORMAT(recorded_at, '%Y-%m-%d %H:00:00'),   -- hour bucket
       ROUND(AVG(temperature), 2), MIN(temperature), MAX(temperature), COUNT(*)
FROM sensor_readings
GROUP BY sensor_id, DATE_FORMAT(recorded_at, '%Y-%m-%d %H:00:00');

SELECT * FROM sensor_readings_hourly ORDER BY sensor_id, bucket_start;

-- Result:
-- sensor_id | bucket_start        | avg_temp | min_temp | max_temp | sample_cnt
-- 1         | 2024-05-01 10:00:00 | 21.75    | 21.50    | 22.00    | 2
-- 1         | 2024-05-01 11:00:00 | 23.50    | 23.50    | 23.50    | 1
-- 1         | 2024-05-02 09:00:00 | 20.00    | 20.00    | 20.00    | 1
-- 2         | 2024-05-01 10:00:00 | 19.00    | 19.00    | 19.00    | 1
-- 2         | 2024-05-01 11:00:00 | 20.50    | 20.50    | 20.50    | 1

-- Step 4: Range query on the raw table uses the PK range scan
EXPLAIN SELECT * FROM sensor_readings
WHERE sensor_id = 1 AND recorded_at >= '2024-05-01 10:00:00' AND recorded_at < '2024-05-01 11:00:00';

-- EXPLAIN (MySQL 9.1):
-- type=range | key=PRIMARY | key_len=8 | rows=2 | Extra=Using where
-- (2 rows returned: the 10:00 and 10:30 readings for sensor 1)
```

---

## 🔍 Why This Works (3 lines max)
PK (sensor_id, recorded_at) turns "last hour for sensor X" into one contiguous range scan with no extra index to maintain on a write-heavy table. The roll-up table answers dashboard queries from hundreds of rows instead of millions. Retention is a partition drop (O(1)) rather than a huge DELETE.
हिंदी: PK (sensor_id, time) = एक range scan, extra index नहीं। Roll-up table dashboard fast करता है, partition drop से retention।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: roll-up in one query with date_trunc (verified on PGlite)
SELECT sensor_id, date_trunc('hour', recorded_at) AS bucket_start,
       ROUND(AVG(temperature),2) AS avg_temp, MIN(temperature) AS min_temp,
       MAX(temperature) AS max_temp, COUNT(*) AS sample_cnt
FROM sensor_readings GROUP BY 1, 2 ORDER BY 1, 2;
-- Same 5 rows as the MySQL result above (bucket_start shown as timestamptz).

-- PostgreSQL: BRIN index = tiny index for append-only, time-ordered tables
CREATE INDEX idx_readings_brin ON sensor_readings USING BRIN (recorded_at);
-- BRIN stores min/max per block range: ~1000x smaller than B-tree when rows arrive in time order.

-- PostgreSQL: declarative range partitioning by month (verified on PGlite)
CREATE TABLE sr_part (
  sensor_id INT NOT NULL, recorded_at TIMESTAMPTZ NOT NULL, temperature NUMERIC(5,2)
) PARTITION BY RANGE (recorded_at);
CREATE TABLE sr_part_2024_05 PARTITION OF sr_part FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
-- Retention: DROP TABLE sr_part_2024_05;  (instant, no vacuum bloat)

-- Dedicated engines (not run here): TimescaleDB hypertables + continuous aggregates,
-- InfluxDB, ClickHouse — use when you pass ~1M inserts/sec or need built-in downsampling.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: surrogate id PK + separate index on time
CREATE TABLE sensor_readings_bad (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  sensor_id INT, recorded_at TIMESTAMP, temperature DECIMAL(5,2),
  INDEX (sensor_id, recorded_at)
);
-- Every insert maintains 2 B-trees, rows of one sensor are scattered across the clustered index,
-- and the index doubles storage.

-- ❌ Wrong: purging old data with DELETE
DELETE FROM sensor_readings WHERE recorded_at < '2023-01-01';   -- hours of locks, undo log, replication lag
-- ✅ Partition by time and DROP PARTITION (MySQL) / DROP TABLE of the child partition (PgSQL)
-- ❌ Also wrong: querying raw data for 6-month dashboards instead of the roll-up table
```

---

## 🎯 Interview Tip (1 line)
Say: "I cluster by (entity, time), keep rows narrow, pre-aggregate into hourly/daily roll-ups, partition by time so retention is a DROP, and I would move to TimescaleDB/ClickHouse once write volume or downsampling needs outgrow plain InnoDB/Postgres."

---

## 🔗 Related Questions
→ Q153 (Partitioning strategy) | Q150 (Event sourcing) | Q160 (UUID vs BIGINT) | Q154 (Sharding)
