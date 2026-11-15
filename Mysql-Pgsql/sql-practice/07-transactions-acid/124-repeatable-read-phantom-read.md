---

# Q124. REPEATABLE READ — Phantom Read
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL and PostgreSQL behave differently)

---

## ❓ Question
What is a phantom read? Show that MySQL REPEATABLE READ hides phantoms for plain SELECTs but exposes them to locking reads and UPDATEs, that READ COMMITTED shows them immediately, and how gap locks prevent them. What does PostgreSQL do?

---

## 💡 Quick Concept (2 lines only)
A phantom is a NEW row that matches your WHERE condition appearing between two reads in the same transaction. InnoDB REPEATABLE READ avoids phantoms in snapshot reads and uses next-key (gap) locks for locking reads; PostgreSQL REPEATABLE READ is snapshot isolation and also shows no phantoms.
हिंदी: Phantom read = उसी condition पर बीच में नई row आ जाना; MySQL RR में सादा SELECT नहीं देखता पर UPDATE/FOR UPDATE देख लेते हैं, gap lock नई row रोकता है।

---

## ✅ Answer / Solution

```sql
-- Verified on MySQL 9.1.0 with two real parallel sessions (A reader, B inserter, SLEEP ordering).
-- PostgreSQL two-session behaviour NOT run (PGlite = one connection); described from docs.

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE bookings (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  room_id INT,
  guest   VARCHAR(50),
  nights  INT,
  status  VARCHAR(10) DEFAULT 'NEW',
  INDEX idx_room (room_id)
) ENGINE=InnoDB;

INSERT INTO bookings (room_id, guest, nights) VALUES
  (1, 'Asha', 2), (1, 'Ravi', 3), (2, 'Meera', 1);

-- ============================================
-- SOLUTION
-- ============================================

-- Experiment 1: phantom visibility (A = reader, B inserts a room-1 booking and commits)
--   A: SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;  (or READ COMMITTED)
--   A: START TRANSACTION;
--   A: SELECT COUNT(*) FROM bookings WHERE room_id = 1;             -- #1
--   B: INSERT INTO bookings (room_id, guest, nights) VALUES (1, 'Kabir', 4);  -- autocommit
--   A: SELECT COUNT(*) FROM bookings WHERE room_id = 1;             -- #2 plain (snapshot) read
--   A: UPDATE bookings SET status = 'SEEN' WHERE room_id = 1;       -- current read: touches the phantom
--   A: SELECT COUNT(*) FROM bookings WHERE room_id = 1;             -- #3
--   A: COMMIT;

-- Experiment 2: stop the phantom with a locking read (gap/next-key lock)
--   A: (REPEATABLE READ) START TRANSACTION;
--   A: SELECT COUNT(*) FROM bookings WHERE room_id = 1 FOR UPDATE;  -- locks the index range + gaps
--   B: INSERT INTO bookings (room_id, guest, nights) VALUES (1, 'Kabir', 4);   -- BLOCKS until A commits
--   A: (holds 2 sec) COMMIT;                                         -- B's insert proceeds now

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Experiment 1, REPEATABLE READ (real):      -- Experiment 1, READ COMMITTED (real):
-- A count #1                    | 2          -- A count #1                    | 2
-- A count #2 (plain read)       | 2          -- A count #2 (plain read)       | 3   <- phantom
-- A rows changed by UPDATE      | 3  <- !    -- A rows changed by UPDATE      | 3
-- A count #3 (after own UPDATE) | 3  <- !    -- A count #3                    | 3
-- A rows SEEN: Asha,Ravi,Kabir               -- A rows SEEN: Asha,Ravi,Kabir
-- Plain reads stayed at 2, but UPDATE modified 3 rows: a "hidden" phantom pulled into the snapshot.
--
-- Experiment 2 (real): B's INSERT waited ~2 s (until A committed) under REPEATABLE READ,
--                      and ~0 s under READ COMMITTED (no gap locks there).
```

---

## 🔍 Why This Works (3 lines max)
InnoDB plain SELECTs read from the transaction's snapshot, so B's committed row stays invisible; but UPDATE and `FOR UPDATE` read the latest committed data ("current read"), so the phantom shows up and gets modified. Locking reads at REPEATABLE READ take next-key locks that cover the gaps, which makes B's INSERT wait.
हिंदी: Plain SELECT snapshot से पढ़ता है इसलिए phantom नहीं दिखता, पर UPDATE/FOR UPDATE latest data पर चलते हैं; gap lock से B का INSERT रुक जाता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (documented, not run): REPEATABLE READ = snapshot isolation. EVERY statement, including
-- UPDATE, uses the transaction snapshot: no phantoms at all. A conflicting concurrent update of a
-- row you also modify raises:
--    ERROR: could not serialize access due to concurrent update    -> retry the transaction.
-- But PostgreSQL REPEATABLE READ is still NOT serializable (write skew possible, see Q125).

BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM bookings WHERE room_id = 1;     -- snapshot taken here
-- ... another session inserts + commits a room-1 booking ...
SELECT count(*) FROM bookings WHERE room_id = 1;     -- same number
COMMIT;

-- Prevent "double booking" regardless of isolation level - use a constraint, not isolation:
-- PostgreSQL: EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out) WITH &&)
-- MySQL: UNIQUE (room_id, night_date) in a per-night table, or lock the room row first:
SELECT id FROM rooms WHERE id = 1 FOR UPDATE;
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Saying "REPEATABLE READ allows phantoms (SQL standard table), so MySQL does too".
--    InnoDB RR prevents them for snapshot reads and uses gap locks for locking reads.
-- ❌ Mixing plain SELECT and UPDATE in one RR transaction and expecting the same rows:
--    count was 2, UPDATE changed 3 (verified above).
-- ❌ Using READ COMMITTED in MySQL and assuming gap locks still protect uniqueness checks:
--    at READ COMMITTED gap locking is mostly disabled, so "check then insert" races occur.
-- ✅ Enforce rules with UNIQUE/EXCLUDE constraints, or lock a parent row, or use SERIALIZABLE.
```

---

## 🎯 Interview Tip (1 line)
Say: "InnoDB REPEATABLE READ prevents phantoms in consistent reads via the snapshot and in locking reads via next-key locks, but mixed plain-and-locking reads can still surprise you; PostgreSQL RR is pure snapshot isolation with no phantoms - and in both cases I protect invariants with constraints rather than relying on isolation."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q123 (Non-repeatable read) | Q125 (SERIALIZABLE cost) | Q129 (Deadlock example)
