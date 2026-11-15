---

# Q156. Monitoring and Baselines
# Category: PERFORMANCE TUNING
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (STDEV = sample std-dev; MySQL STDDEV_SAMP / PostgreSQL STDDEV_SAMP)

---

## ❓ Question
"The database is slow" — compared to what? Design a lightweight baseline: store periodic metric samples, then write a query that flags a current value that deviates more than 3 standard deviations from its history.

---

## 💡 Quick Concept (2 lines only)
A baseline is normal behaviour captured over time (batch requests/sec, page life expectancy, waits, CPU); you alert on deviation from your own norm, not on a magic number. Collect via a scheduled job (SQL Agent / Azure Automation / Elastic Job) into a table.
हिंदी: Baseline = सामान्य हालत का रिकॉर्ड। "Slow है" तभी पता चलेगा जब normal पता हो। Metrics को job से table में जमा करो और average/std-dev से deviation पकड़ो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.MetricSample (
  SampleId    INT PRIMARY KEY,
  CapturedAt  DATETIME2     NOT NULL,
  MetricName  VARCHAR(50)   NOT NULL,
  MetricValue DECIMAL(18,2) NOT NULL
);

INSERT INTO dbo.MetricSample VALUES
 (1,'2026-11-01 10:00','BatchRequestsPerSec',100),(2,'2026-11-02 10:00','BatchRequestsPerSec',110),
 (3,'2026-11-03 10:00','BatchRequestsPerSec',95), (4,'2026-11-04 10:00','BatchRequestsPerSec',105),
 (5,'2026-11-05 10:00','BatchRequestsPerSec',120),(6,'2026-11-06 10:00','BatchRequestsPerSec',100),
 (7,'2026-11-07 10:00','BatchRequestsPerSec',90), (8,'2026-11-08 10:00','BatchRequestsPerSec',190),
 (9,'2026-11-01 10:00','PageLifeExpectancy',3000),(10,'2026-11-02 10:00','PageLifeExpectancy',3100),
 (11,'2026-11-03 10:00','PageLifeExpectancy',2900),(12,'2026-11-04 10:00','PageLifeExpectancy',3050),
 (13,'2026-11-05 10:00','PageLifeExpectancy',3000),(14,'2026-11-06 10:00','PageLifeExpectancy',2950),
 (15,'2026-11-07 10:00','PageLifeExpectancy',3000),(16,'2026-11-08 10:00','PageLifeExpectancy',1200);

-- ============================================
-- SOLUTION: latest value vs baseline of all earlier samples
-- ============================================
WITH latest AS (
  SELECT MetricName, MAX(CapturedAt) AS LatestAt
  FROM dbo.MetricSample GROUP BY MetricName
),
base AS (
  SELECT s.MetricName, AVG(s.MetricValue) AS AvgVal, STDEV(s.MetricValue) AS StdVal
  FROM dbo.MetricSample s
  JOIN latest l ON l.MetricName = s.MetricName AND s.CapturedAt < l.LatestAt
  GROUP BY s.MetricName
)
SELECT b.MetricName,
       CAST(b.AvgVal AS DECIMAL(10,2)) AS AvgVal,
       CAST(b.StdVal AS DECIMAL(10,2)) AS StdVal,
       c.MetricValue AS CurrentVal,
       CAST((c.MetricValue - b.AvgVal) / b.StdVal AS DECIMAL(10,2)) AS ZScore,
       CASE WHEN ABS((c.MetricValue - b.AvgVal) / b.StdVal) > 3 THEN 'ALERT' ELSE 'OK' END AS Status
FROM base b
JOIN latest l ON l.MetricName = b.MetricName
JOIN dbo.MetricSample c ON c.MetricName = l.MetricName AND c.CapturedAt = l.LatestAt
ORDER BY b.MetricName;

-- Collector sketch (counter names exist in sys.dm_os_performance_counters; verify on your instance):
-- INSERT INTO dbo.MetricSample ... SELECT ... FROM sys.dm_os_performance_counters WHERE counter_name = 'Page life expectancy';

/* EXPECTED OUTPUT (result derived from equivalent query on MySQL 9.1 with STDDEV_SAMP; not executed on SQL Server)
MetricName           AvgVal   StdVal  CurrentVal  ZScore  Status
BatchRequestsPerSec  102.86   9.94    190.00      8.77    ALERT
PageLifeExpectancy   3000.00  64.55   1200.00     -27.89  ALERT
*/
```

---

## 🔍 Why This Works (3 lines max)
The CTE finds each metric's newest sample, the baseline aggregates only earlier samples (so the spike does not pollute its own average), and the z-score says how many std-devs away it is. STDEV is the sample deviation; STDEVP is population.
हिंदी: Latest को baseline से अलग रखा ताकि spike अपना ही average न बिगाड़े। Z-score = कितने std-dev दूर। STDEV = sample, STDEVP = population।

---

## ⚡ Alternative Solution

```sql
-- Production: Query Store + Azure Monitor/Extended Events instead of hand-rolled tables
ALTER DATABASE CURRENT SET QUERY_STORE = ON;   -- regressed-query reports compare time windows for you
-- Compare periods: sys.query_store_runtime_stats / sys.query_store_runtime_stats_interval (see Q142)
-- Also baseline: wait stats deltas (Q148), file I/O latency, deadlocks/hour, p95 API latency from the app
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: cumulative DMV counters read once (e.g. wait stats, perf counters of type "per second")
--    They are cumulative since restart / need two samples; the DELTA over an interval is the metric.
-- ❌ Wrong: baseline taken only during a quiet week, or including the incident itself
-- ❌ Wrong: fixed thresholds copied from blogs ("PLE must be 300") - judge against YOUR baseline
-- ✅ Capture hourly/daily, keep seasonality (month-end, sale day) and prune old rows
```

---

## 🎯 Interview Tip (1 line)
Say: "I baseline before I tune: Query Store for query-level regressions, wait-stats deltas, I/O latency, CPU and request latency from the app — stored with timestamps so I can answer 'what changed since last Tuesday' with data, and alert on deviation from the baseline instead of static thresholds."

---

## 🔗 Related Questions
→ Q142 (Slow queries, DMVs, Query Store) | Q148 (Wait stats basics) | Q168 (Azure SQL monitoring) | Q149 (tempdb contention)
