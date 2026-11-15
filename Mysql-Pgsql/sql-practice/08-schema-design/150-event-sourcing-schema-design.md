---

# Q150. Event Sourcing Schema Design
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
Design an append-only event store for bank accounts instead of a mutable `balance` column. Show how to rebuild the current balance, the balance as of a past date, how to prevent concurrent writers from corrupting an account, and how snapshots keep replay fast.

---

## 💡 Quick Concept (2 lines only)
Store every state change as an immutable event (never UPDATE/DELETE); current state = fold over events. A UNIQUE (aggregate_id, version) constraint gives optimistic concurrency, and periodic snapshots avoid replaying millions of events.
हिंदी: State नहीं, events store करो (सिर्फ INSERT)। UNIQUE (account, version) concurrency बचाता है, snapshot replay तेज़ करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL; PgSQL changes listed in Alternative)
-- ============================================

CREATE TABLE account_events (
  event_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id  INT NOT NULL,
  version     INT NOT NULL,               -- 1,2,3... per account
  event_type  VARCHAR(30) NOT NULL,
  amount      DECIMAL(12,2) NOT NULL DEFAULT 0,
  payload     JSON NULL,
  occurred_at DATETIME NOT NULL,
  UNIQUE KEY uq_account_version (account_id, version)   -- optimistic concurrency guard
);

INSERT INTO account_events (account_id, version, event_type, amount, payload, occurred_at) VALUES
  (1, 1, 'AccountOpened',  0,   '{"owner":"Asha"}', '2024-06-01 09:00:00'),
  (1, 2, 'MoneyDeposited', 500, NULL, '2024-06-01 09:05:00'),
  (1, 3, 'MoneyWithdrawn', 120, NULL, '2024-06-02 10:00:00'),
  (1, 4, 'MoneyDeposited', 70,  NULL, '2024-06-03 11:00:00'),
  (2, 1, 'AccountOpened',  0,   '{"owner":"Ravi"}', '2024-06-01 09:30:00'),
  (2, 2, 'MoneyDeposited', 900, NULL, '2024-06-01 09:35:00');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: Current balance = replay (sum) of all events
SELECT account_id,
  SUM(CASE event_type WHEN 'MoneyDeposited' THEN amount
                      WHEN 'MoneyWithdrawn' THEN -amount ELSE 0 END) AS balance,
  MAX(version) AS current_version
FROM account_events GROUP BY account_id ORDER BY account_id;

-- Result:
-- account_id | balance | current_version
-- 1          | 450.00  | 4
-- 2          | 900.00  | 2

-- Step 2: Time travel — running balance up to 2024-06-02
SELECT version, event_type,
  SUM(CASE event_type WHEN 'MoneyDeposited' THEN amount
                      WHEN 'MoneyWithdrawn' THEN -amount ELSE 0 END) OVER (ORDER BY version) AS balance_after
FROM account_events
WHERE account_id = 1 AND occurred_at <= '2024-06-02 23:59:59'
ORDER BY version;

-- Result:
-- version | event_type     | balance_after
-- 1       | AccountOpened  | 0.00
-- 2       | MoneyDeposited | 500.00
-- 3       | MoneyWithdrawn | 380.00

-- Step 3: Concurrency — two writers both read version 4, both try to append version 5.
-- The second INSERT is rejected by the unique key instead of silently overwriting.
-- Demo with version 4 (already used):
INSERT INTO account_events (account_id, version, event_type, amount, occurred_at)
VALUES (1, 4, 'MoneyWithdrawn', 50, '2024-06-04 08:00:00');
-- MySQL : ERROR 1062 (23000): Duplicate entry '1-4' for key 'account_events.uq_account_version'
-- PgSQL : ERROR: duplicate key value violates unique constraint "uq_account_version"
-- App reaction: reload events, re-validate the command, retry with the new version.

-- Step 4: Snapshot = cached state at a version; replay only newer events
CREATE TABLE account_snapshots (
  account_id INT PRIMARY KEY, version INT NOT NULL, balance DECIMAL(12,2) NOT NULL
);
INSERT INTO account_snapshots VALUES (1, 3, 380.00);

SELECT s.account_id,
  s.balance + COALESCE(SUM(CASE e.event_type WHEN 'MoneyDeposited' THEN e.amount
                                             WHEN 'MoneyWithdrawn' THEN -e.amount ELSE 0 END), 0) AS balance
FROM account_snapshots s
LEFT JOIN account_events e ON e.account_id = s.account_id AND e.version > s.version
GROUP BY s.account_id, s.balance;

-- Result (same as full replay, but only 1 event read):
-- account_id | balance
-- 1          | 450.00
```

---

## 🔍 Why This Works (3 lines max)
Events are facts that never change, so history, audit and "what was the balance on date X" come for free. The unique (account_id, version) key makes concurrent appends fail fast rather than lose updates. Snapshots bound replay cost to "events since last snapshot".
हिंदी: Events बदलते नहीं, इसलिए audit और time-travel free। Unique version = concurrent write safe। Snapshot = कम events replay।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL changes (all verified on PGlite):
--   event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
--   payload  JSONB          (indexable, binary)      occurred_at TIMESTAMPTZ
--   CONSTRAINT uq_account_version UNIQUE (account_id, version)
-- The balance and window queries are identical; PgSQL prints the first balance_after as 0 (unscaled) not 0.00.

-- Keep a read-model (CQRS) table updated by a consumer/trigger for fast reads:
--   account_balance(account_id PK, balance, version)
-- Update it with:  UPDATE account_balance SET balance = balance + ?, version = ? WHERE account_id = ? AND version = ?-1;

-- Make the table append-only (PgSQL): REVOKE UPDATE, DELETE ON account_events FROM app_user;
-- Corrections are new compensating events (e.g. 'WithdrawalReversed'), never edits.
-- Event publishing to Kafka: use the transactional outbox pattern (not run here).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: UPDATE or DELETE old events to "fix" a mistake
UPDATE account_events SET amount = 100 WHERE event_id = 3;   -- destroys audit trail and breaks snapshots
-- ✅ Append a compensating event and let the fold produce the right balance

-- ❌ Wrong: no (account_id, version) unique key -> two concurrent withdrawals both pass the
--    "balance >= amount" check and overdraw the account
-- ❌ Wrong: replaying the full stream on every read of a hot account -> take a snapshot every N events
-- ❌ Wrong: changing the meaning of an old event type; version the event schema (payload.v = 2) instead
```

---

## 🎯 Interview Tip (1 line)
Say: "Event sourcing gives audit and temporal queries, but I'd only pay its cost (replay, schema evolution, eventual-consistent read models) for domains like payments or ledgers — and I'd enforce ordering with a unique (aggregate, version) key plus snapshots and an outbox for publishing."

---

## 🔗 Related Questions
→ Q151 (Versioning records) | Q148 (Time-series design) | Q242 (SELECT FOR UPDATE) | Q168 (MySQL JSON)
