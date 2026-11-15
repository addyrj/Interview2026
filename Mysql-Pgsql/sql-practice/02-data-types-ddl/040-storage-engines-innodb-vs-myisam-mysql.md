---

# Q040. Storage Engines — InnoDB vs MyISAM (MySQL)
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL has a single heap storage, notes included)

---

## ❓ Question
What is the difference between InnoDB and MyISAM? Prove with SQL that MyISAM ignores transactions, name the other engines you should know, and explain how to migrate a MyISAM table to InnoDB.

---

## 💡 Quick Concept (2 lines only)
InnoDB (default since 5.5) is transactional (ACID), has row-level locks, MVCC, foreign keys and crash recovery. MyISAM has table-level locks, no transactions, no foreign keys, and is not crash-safe.
हिंदी: InnoDB = transaction + row lock + FK + crash recovery; MyISAM = table lock, rollback नहीं, crash-safe नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+, verified on 9.1.0)
-- ============================================

SELECT @@default_storage_engine;   -- InnoDB

CREATE TABLE accounts_innodb (id INT PRIMARY KEY, owner VARCHAR(50), balance DECIMAL(10,2)) ENGINE=InnoDB;
CREATE TABLE accounts_myisam (id INT PRIMARY KEY, owner VARCHAR(50), balance DECIMAL(10,2)) ENGINE=MyISAM;

INSERT INTO accounts_innodb VALUES (1,'Asha',1000),(2,'Bilal',500);
INSERT INTO accounts_myisam VALUES (1,'Asha',1000),(2,'Bilal',500);

-- ============================================
-- SOLUTION — does ROLLBACK work?
-- ============================================

START TRANSACTION;
UPDATE accounts_innodb SET balance = balance - 300 WHERE id = 1;
UPDATE accounts_myisam SET balance = balance - 300 WHERE id = 1;
ROLLBACK;   -- per MySQL docs a warning is raised (non-transactional table not rolled back); not captured in my run

SELECT 'innodb' AS engine, id, balance FROM accounts_innodb WHERE id = 1
UNION ALL
SELECT 'myisam', id, balance FROM accounts_myisam WHERE id = 1;

-- Which engines does this server support?
SELECT ENGINE, SUPPORT, TRANSACTIONS, XA, SAVEPOINTS FROM information_schema.ENGINES ORDER BY ENGINE;

-- ============================================
-- EXPECTED OUTPUT (MySQL 9.1.0)
-- ============================================

-- engine | id | balance
-- innodb | 1  | 1000.00     <- rolled back
-- myisam | 1  | 700.00      <- change persisted despite ROLLBACK
--
-- information_schema.ENGINES (trimmed): TRANSACTIONS = YES only for InnoDB (SUPPORT = DEFAULT);
--   MyISAM, MEMORY, CSV, ARCHIVE, BLACKHOLE, MRG_MYISAM: YES for support, NO for transactions;
--   FEDERATED and ndbcluster: SUPPORT = NO on this build.
```

---

## 🔍 Why This Works (3 lines max)
InnoDB writes an undo log and redo log, so a ROLLBACK can reverse changes and a crash can be recovered. MyISAM writes straight to its data file with no undo, so each statement is permanent immediately and a writer locks the whole table.
हिंदी: InnoDB undo/redo log रखता है इसलिए rollback चलता है; MyISAM सीधे file में लिखता है, इसलिए बदलाव वापस नहीं होते।

---

## ⚡ Alternative Solution

```sql
-- Migrating MyISAM -> InnoDB (verified on 9.1.0)
ALTER TABLE accounts_myisam ENGINE=InnoDB;     -- rebuilds the whole table; blocks writes on big tables
SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME LIKE 'accounts%';
-- accounts_innodb | InnoDB
-- accounts_myisam | InnoDB
-- For large tables use gh-ost / pt-online-schema-change (not run here).

-- Comparison cheat sheet
--  Feature            InnoDB                    MyISAM
--  Transactions/ACID  Yes                       No
--  Locking            Row-level (+ MVCC)        Table-level
--  Foreign keys       Yes                       Not enforced (docs: parsed but ignored)
--  Crash recovery     Yes (redo log)            No (needs REPAIR TABLE)
--  Full-text index    Yes (5.6+)                Yes
--  COUNT(*) no WHERE  Scans an index            Instant (stored row count)
--  Clustered PK       Yes                       No (heap + separate indexes)
-- Other engines: MEMORY (RAM, lost on restart), ARCHIVE (compressed insert/select only), CSV, BLACKHOLE (replication relay).
-- MySQL system tables are InnoDB since 8.0; MyISAM is effectively legacy.

-- PostgreSQL: one heap-based storage with MVCC; table access methods (CREATE ACCESS METHOD) exist
-- but there is no per-table "engine" choice in everyday use. (not exercised here)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: creating tables without ENGINE on an old server where the default is MyISAM (MySQL < 5.5), then expecting FK/transactions
-- ❌ Wrong: mixing InnoDB and MyISAM tables in one transaction and assuming ROLLBACK covers both (shown above: it does not)
-- ❌ Wrong: believing MyISAM COUNT(*) speed justifies it -> a counter table/cached count with InnoDB is the safe pattern
-- ✅ Correct: ENGINE=InnoDB everywhere; check SELECT TABLE_NAME FROM information_schema.TABLES WHERE ENGINE='MyISAM';
```

---

## 🎯 Interview Tip (1 line)
Say: "InnoDB is the only sensible default — ACID, row-level locking with MVCC, foreign keys and crash recovery; MyISAM's table locks and lack of rollback make it unfit for OLTP, and when I inherit MyISAM tables I convert them with ALTER ... ENGINE=InnoDB using an online schema-change tool."

---

## 🔗 Related Questions
→ Q039 (Collation / utf8mb4) | Q031 (Foreign keys) | Q033 (Index on large table) | Transactions & isolation levels
