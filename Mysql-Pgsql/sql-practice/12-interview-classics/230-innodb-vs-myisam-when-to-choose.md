---

# Q230. InnoDB vs MyISAM — When to Choose
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL note at the end)

---

## ❓ Question
What are the differences between the InnoDB and MyISAM storage engines? Which one should you choose today, and is there any case left for MyISAM? Prove the key differences (transactions, foreign keys, locking) on a real server.

---

## 💡 Quick Concept (2 lines only)
InnoDB (default since MySQL 5.5) is transactional (ACID), has row-level locking, foreign keys, MVCC and crash recovery. MyISAM has none of these: table-level locks, no transactions, no crash safety — choose InnoDB for essentially everything.
हिंदी: InnoDB = transactions, row lock, foreign key, crash recovery; MyISAM में ये कुछ नहीं, इसलिए आज लगभग हमेशा InnoDB चुनो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1; MyISAM still exists for user tables)
-- ============================================

CREATE TABLE audit_log_myisam (id INT AUTO_INCREMENT PRIMARY KEY, msg VARCHAR(50)) ENGINE=MyISAM;
CREATE TABLE audit_log_innodb (id INT AUTO_INCREMENT PRIMARY KEY, msg VARCHAR(50)) ENGINE=InnoDB;

SELECT table_name, engine
FROM information_schema.tables
WHERE table_schema = DATABASE() ORDER BY table_name;
-- Result:
-- table_name       | engine
-- -----------------+-------
-- audit_log_innodb | InnoDB
-- audit_log_myisam | MyISAM

SELECT @@default_storage_engine;      -- InnoDB

-- ============================================
-- TEST 1 — transactions / ROLLBACK
-- ============================================

START TRANSACTION;
INSERT INTO audit_log_myisam (msg) VALUES ('m1');
INSERT INTO audit_log_innodb (msg) VALUES ('i1');
ROLLBACK;

SELECT 'myisam' AS tbl, COUNT(*) AS cnt FROM audit_log_myisam
UNION ALL
SELECT 'innodb', COUNT(*) FROM audit_log_innodb;
-- Result:
-- tbl    | cnt
-- -------+----
-- myisam | 1      <- ROLLBACK did nothing: row is permanently there
-- innodb | 0      <- properly rolled back

-- ============================================
-- TEST 2 — foreign keys
-- ============================================

CREATE TABLE parent_i (id INT PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE child_i (id INT PRIMARY KEY, pid INT, FOREIGN KEY (pid) REFERENCES parent_i(id)) ENGINE=InnoDB;
INSERT INTO child_i VALUES (1, 99);
-- ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails

CREATE TABLE parent_m (id INT PRIMARY KEY) ENGINE=MyISAM;
CREATE TABLE child_m (id INT PRIMARY KEY, pid INT, FOREIGN KEY (pid) REFERENCES parent_m(id)) ENGINE=MyISAM;
INSERT INTO child_m VALUES (1, 99);
SELECT * FROM child_m;
-- Result: (1, 99) inserted. The FOREIGN KEY clause is parsed but silently IGNORED
-- (SHOW CREATE TABLE child_m shows only KEY `pid`, no CONSTRAINT).

-- ============================================
-- TEST 3 — locking granularity (two sessions)
-- ============================================

CREATE TABLE lk_myisam (id INT PRIMARY KEY, msg VARCHAR(20)) ENGINE=MyISAM;
CREATE TABLE lk_innodb (id INT PRIMARY KEY, msg VARCHAR(20)) ENGINE=InnoDB;
INSERT INTO lk_myisam VALUES (1,'a'),(2,'b');
INSERT INTO lk_innodb VALUES (1,'a'),(2,'b');

-- Session A (a slow read, holds the table lock for the statement; ~4 s total):
SELECT SLEEP(2) FROM lk_myisam;
-- Session B, 0.5 s later: update a DIFFERENT row
UPDATE lk_myisam SET msg = 'x' WHERE id = 2;
-- Measured: B waited 3.5 s  (table-level lock: writer blocked by a reader)

-- Same experiment on InnoDB:
SELECT SLEEP(2) FROM lk_innodb;               -- Session A
UPDATE lk_innodb SET msg = 'x' WHERE id = 2;  -- Session B
-- Measured: B waited 0.0 s  (row-level locking + MVCC, readers do not block writers)

-- (MyISAM allows concurrent INSERT at the end of the file when there are no holes,
--  which is why a plain INSERT did not wait in our first attempt; UPDATE/DELETE do.)

-- ============================================
-- MIGRATE
-- ============================================

ALTER TABLE audit_log_myisam ENGINE=InnoDB;     -- rebuilds the table (blocking; use gh-ost/pt-osc for large tables)
SELECT engine FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_name = 'audit_log_myisam';
-- Result: InnoDB
-- Even MySQL's own system tables are InnoDB now: mysql.user, mysql.db -> InnoDB (verified)
```

---

## 🔍 Why This Works (3 lines max)
InnoDB writes a redo log and undo log, so it can commit atomically, roll back, and recover after a crash; MyISAM writes straight to its data file with only a table lock. That is why InnoDB gives ACID and high write concurrency, while MyISAM can corrupt on crash and serializes writers.
हिंदी: InnoDB redo/undo log रखता है इसलिए commit-rollback और crash recovery मिलती है; MyISAM सीधे file में लिखता है, crash में corrupt हो सकता है।

---

## ⚡ Alternative Solution

```sql
-- Comparison table
-- Feature              InnoDB                      MyISAM
-- Transactions/ACID    Yes                         No
-- Locking              Row-level (+MVCC)           Table-level
-- Foreign keys         Yes                         No (parsed, ignored)
-- Crash recovery       Automatic (redo log)        Manual REPAIR TABLE
-- Clustered PK         Yes                         No (heap + separate index file)
-- COUNT(*) no WHERE    Scans an index (slower)     Stored row count (instant)
-- FULLTEXT             Yes (5.6+)                  Yes
-- Compression/online DDL  Yes                      Limited

-- Remaining (rare) MyISAM uses: read-only, rebuildable lookup/reporting data, legacy systems.
-- Even there InnoDB is usually fine. Also: MyISAM is NOT replicated safely in crash scenarios and
-- is not supported by Group Replication / InnoDB Cluster.

-- Other engines: MEMORY (temp lookups, lost on restart), ARCHIVE (append-only compressed),
-- CSV, BLACKHOLE; Aurora/RDS/Percona require InnoDB (or XtraDB) for HA features.

-- PostgreSQL has ONE built-in storage engine (heap with MVCC) -> no "engine" choice;
-- pluggable table access methods exist since PG12 but heap is what nearly everyone uses. See Q226.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "MyISAM is faster for reads, so I use it" -> true only in ancient benchmarks; InnoDB's buffer pool,
--    covering indexes and MVCC usually win, and one long write blocks every reader on MyISAM.
-- ❌ Wrong: defining FOREIGN KEY on MyISAM tables and trusting it (silently ignored, shown above)
-- ❌ Wrong: mixing engines in one transaction: the MyISAM part cannot be rolled back
-- ❌ Wrong: assuming COUNT(*) is instant (only on MyISAM). On InnoDB keep a counter table if you need O(1)
-- ✅ Correct: InnoDB by default; check existing tables with information_schema.tables and migrate
```

---

## 🎯 Interview Tip (1 line)
Say: "InnoDB for anything real: ACID transactions, row-level locking with MVCC, foreign keys and redo-log crash recovery; MyISAM's table locks and lack of transactions and crash safety make it a legacy choice — I'd audit for MyISAM tables with information_schema and migrate them with ALTER ... ENGINE=InnoDB using an online-schema-change tool."

---

## 🔗 Related Questions
→ Q225 (ACID real examples) | Q226 (MVCC) | Q227 (deadlocks) | Q224 (adding index to running table)
