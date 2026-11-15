---

# Q150. Partitioning for Performance
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: PARTITION BY RANGE | PostgreSQL: declarative partitioning). Partition mapping hand-checked; elimination/plans not executed on SQL Server.

---

## ❓ Question
`Orders` holds 5 years of data (hundreds of millions of rows). Monthly purges are slow and reports on the current month scan too much. Show partitioning by year, partition elimination, and sliding-window purge.

---

## 💡 Quick Concept (2 lines only)
Partitioning splits a table by a key via a partition function + scheme. Benefits are manageability (switch/truncate a partition in a metadata operation) and possible partition elimination; it is NOT an automatic speed-up for every query.
हिंदी: Partitioning मुख्यतः management के लिए है (partition switch से purge)। Query तभी तेज़ होती है जब WHERE में partition key हो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (partitioning is available in all editions since SQL Server 2016 SP1)
-- ============================================
CREATE PARTITION FUNCTION pfOrderYear (DATE)
  AS RANGE RIGHT FOR VALUES ('2023-01-01', '2024-01-01', '2025-01-01');
-- RANGE RIGHT: boundary value belongs to the partition on its right
-- partition 1: < 2023-01-01 | 2: 2023 | 3: 2024 | 4: >= 2025-01-01

CREATE PARTITION SCHEME psOrderYear
  AS PARTITION pfOrderYear ALL TO ([PRIMARY]);

CREATE TABLE Orders (
  OrderId    BIGINT        NOT NULL,
  CustomerId INT           NOT NULL,
  OrderDate  DATE          NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (OrderDate, OrderId)   -- partition key must be in the key
) ON psOrderYear (OrderDate);

INSERT INTO Orders VALUES
  (1, 1, '2022-12-31', 10), (2, 1, '2023-01-01', 20),
  (3, 2, '2023-06-15', 30), (4, 2, '2024-02-01', 40), (5, 3, '2025-03-01', 50);

-- Which partition does each row land in?
SELECT OrderId, OrderDate, $PARTITION.pfOrderYear(OrderDate) AS PartitionNo
FROM Orders
ORDER BY OrderId;

-- EXPECTED OUTPUT (hand-checked from the RANGE RIGHT boundaries; not executed on SQL Server):
-- OrderId | OrderDate  | PartitionNo
-- 1       | 2022-12-31 | 1
-- 2       | 2023-01-01 | 2     <- boundary value goes RIGHT
-- 3       | 2023-06-15 | 2
-- 4       | 2024-02-01 | 3
-- 5       | 2025-03-01 | 4

-- Partition elimination: predicate on the key lets the engine touch partition 3 only
SELECT SUM(Amount) FROM Orders
WHERE OrderDate >= '2024-01-01' AND OrderDate < '2025-01-01';

-- Sliding window purge: switch the old partition out (metadata only), then drop it
-- (target table must have identical structure, indexes and a CHECK/ON same filegroup)
ALTER TABLE Orders SWITCH PARTITION 1 TO Orders_Archive;
-- SQL Server 2016+: TRUNCATE TABLE Orders WITH (PARTITIONS (1));
```

---

## 🔍 Why This Works (3 lines max)
SWITCH and partition-level TRUNCATE change metadata instead of logging every row, so purging 100M rows takes seconds. Predicates on the partition column let the optimizer skip partitions entirely.
हिंदी: Partition switch = सिर्फ़ metadata बदलना, इसलिए करोड़ों rows सेकंडों में हटते हैं।

---

## ⚡ Alternative Solution

```sql
-- Often cheaper than partitioning: a good index (OrderDate, ...) or a filtered/columnstore index (Q105, Q106).
-- Partitioned views / separate yearly tables are the pre-2005 style and still valid for small cases.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Expecting every query to get faster: without the partition key in WHERE, all partitions are scanned
-- ❌ A unique/PK index that does not include the partition column (not allowed)
-- ❌ Forgetting to add future boundaries (SPLIT RANGE); everything piles into the last partition
-- ❌ Parameter/variable on the key with implicit type mismatch (DATETIME vs DATE) breaking elimination
-- ❌ Partitioning a 5M-row table "for speed": extra complexity, no gain
```

---

## 🎯 Interview Tip (1 line)
Say: "I partition for lifecycle management first (switch in/out, per-partition maintenance), performance second. Align indexes, put the key in the clustered key, plan SPLIT/MERGE ahead, and verify elimination in the plan before claiming a win."

---

## 🔗 Related Questions
→ Q034 (Partitioned tables basics) | Q106 (Columnstore indexes) | Q145 (Batching large deletes) | Q191 (Migrate 100M rows with zero downtime)
