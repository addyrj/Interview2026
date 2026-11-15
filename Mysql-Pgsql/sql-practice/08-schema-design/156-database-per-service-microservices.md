---

# Q156. Database per Service (Microservices)
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
In a microservices architecture each service owns its own database. How do you model `users` and `orders` across two services, what happens to foreign keys and JOINs, and how do you keep data consistent without cross-service transactions?

---

## 💡 Quick Concept (2 lines only)
Each service owns its schema; no other service reads or writes its tables directly. Cross-service links become plain ID columns (no FK), joins move to the application/API layer, and consistency becomes eventual (events, outbox, saga).
हिंदी: हर service का अपना DB; cross-service FK नहीं, सिर्फ ID रखो; JOIN app layer में और consistency eventual होती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (simulated with 2 tables; in real life: 2 separate databases/servers)
-- Verified on MySQL 9.1.0 (same SQL works on 8.0 and PostgreSQL)
-- ============================================

-- ---- User Service DB ----
CREATE TABLE users_svc (
  user_id BIGINT PRIMARY KEY,
  email   VARCHAR(100) UNIQUE,
  name    VARCHAR(100)
);

-- ---- Order Service DB ----
CREATE TABLE orders_svc (
  order_id            BIGINT PRIMARY KEY,
  user_id             BIGINT NOT NULL,        -- plain reference, NO foreign key (other DB!)
  user_email_snapshot VARCHAR(100),           -- denormalized copy so orders still render if user svc is down
  total               DECIMAL(10,2),
  status              VARCHAR(20)
);

INSERT INTO users_svc VALUES (1,'a@x.com','Asha'),(2,'b@x.com','Bala');
INSERT INTO orders_svc VALUES
  (100, 1, 'a@x.com',     250.00, 'PAID'),
  (101, 2, 'b@x.com',      90.00, 'NEW'),
  (102, 99,'ghost@x.com',  10.00, 'NEW');     -- orphan: user 99 does not exist, nothing stops it

-- ============================================
-- SOLUTION
-- ============================================
-- Step 1: Order service queries ONLY its own DB (aggregate by user_id)
-- Step 2: Names are fetched via the User Service API / cached read model
-- (here we simulate the "API-composition join" with a LEFT JOIN)

SELECT o.order_id, o.total, u.name
FROM orders_svc o
LEFT JOIN users_svc u ON u.user_id = o.user_id   -- LEFT: tolerate missing/orphan users
ORDER BY o.order_id;

-- Per-user stats stay inside the Order service:
SELECT user_id, COUNT(*) AS c, SUM(total) AS s
FROM orders_svc GROUP BY user_id ORDER BY user_id;

-- ============================================
-- EXPECTED OUTPUT (real run)
-- ============================================

-- order_id | total  | name
-- 100      | 250.00 | Asha
-- 101      |  90.00 | Bala
-- 102      |  10.00 | NULL      <- orphan row, no FK to stop it

-- user_id | c | s
-- 1       | 1 | 250.00
-- 2       | 1 |  90.00
-- 99      | 1 |  10.00
```

---

## 🔍 Why This Works (3 lines max)
Services deploy/scale/migrate independently because no schema is shared; the price is no FK, no cross-DB JOIN, no ACID across services. Use API composition or a CQRS read model for reads, and saga/outbox events for writes.
हिंदी: Independent deploy और scaling मिलती है, बदले में FK और cross-service transaction नहीं मिलता।

---

## ⚡ Alternative Solution

```sql
-- Transactional outbox (same DB as the business write, published later by a relay).
-- Guarantees "order saved" and "event emitted" atomically WITHOUT a distributed transaction.
CREATE TABLE outbox (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,   -- PgSQL: BIGINT GENERATED ALWAYS AS IDENTITY
  aggregate_id BIGINT NOT NULL,
  event_type   VARCHAR(50) NOT NULL,
  payload      JSON NOT NULL,                        -- PgSQL: JSONB
  published    TINYINT(1) NOT NULL DEFAULT 0         -- PgSQL: BOOLEAN DEFAULT FALSE
);
-- BEGIN; INSERT INTO orders_svc ...; INSERT INTO outbox ...; COMMIT;
-- A relay (Debezium/CDC or poller) reads unpublished rows and pushes to Kafka. (Pattern, not run here.)

-- Cross-DB reads on ONE server are possible but couple the services:
--   MySQL:  SELECT ... FROM order_db.orders o JOIN user_db.users u ...   (works, but defeats isolation)
--   PgSQL:  separate databases cannot be joined at all; needs postgres_fdw / dblink.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Shared database: both services touch the same tables ("distributed monolith")
--    One schema change breaks every service; no independent deploys.
-- ❌ Expecting the DB to enforce integrity across services:
--    orders_svc row for user_id=99 was accepted above - orphans must be handled in app/events.
-- ✅ Own your data, keep an ID + small snapshot, subscribe to UserDeleted events, make consumers idempotent.
```

---

## 🎯 Interview Tip (1 line)
Say: "Database per service buys loose coupling at the cost of joins and ACID, so I use IDs not FKs, API composition or CQRS views for reads, and saga plus transactional outbox for cross-service writes - and I would not split a domain that needs strong consistency."

---

## 🔗 Related Questions
→ Q147 (Multi-tenancy patterns) | Q157 (Zero-downtime migrations) | Q164 (Binary log - basis for CDC)
