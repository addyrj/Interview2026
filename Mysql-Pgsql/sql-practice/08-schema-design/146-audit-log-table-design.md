---

# Q146. Audit Log Table Design
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL 11+) — triggers run on MySQL 9.1.0 and PGlite

---

## ❓ Question
Design an audit log that records who changed what and when for the `products` table (INSERT, UPDATE, DELETE) with before/after values, then query the history of one row. Show how the "who" gets from the application into the database.

---

## 💡 Quick Concept (2 lines only)
A single append-only table stores table name, row key, action, old and new row images (JSON) plus actor and timestamp, filled by AFTER triggers so no code path can skip it. Index it by (table, row key, time) for history lookups.
हिंदी: एक append-only audit table में table, row key, action, पुराना/नया JSON, कौन और कब सब रखो; trigger से भरो ताकि कोई code path इसे skip न कर सके।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  name       VARCHAR(80),
  price      DECIMAL(10,2)
);

CREATE TABLE audit_log (
  audit_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  table_name VARCHAR(64) NOT NULL,
  row_pk     VARCHAR(64) NOT NULL,                      -- string so any key type fits
  action     ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  old_data   JSON NULL,                                 -- NULL for INSERT
  new_data   JSON NULL,                                 -- NULL for DELETE
  changed_by VARCHAR(100),
  changed_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_audit_row (table_name, row_pk, changed_at)  -- "history of one row"
);

-- ============================================
-- SOLUTION (MySQL triggers; in the mysql client set DELIMITER //)
-- ============================================

DELIMITER //
CREATE TRIGGER trg_products_ai AFTER INSERT ON products FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name,row_pk,action,new_data,changed_by)
  VALUES ('products', NEW.product_id, 'INSERT',
          JSON_OBJECT('name',NEW.name,'price',NEW.price),
          COALESCE(@app_user, CURRENT_USER()));        -- app sets @app_user per connection
END//
CREATE TRIGGER trg_products_au AFTER UPDATE ON products FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name,row_pk,action,old_data,new_data,changed_by)
  VALUES ('products', NEW.product_id, 'UPDATE',
          JSON_OBJECT('name',OLD.name,'price',OLD.price),
          JSON_OBJECT('name',NEW.name,'price',NEW.price),
          COALESCE(@app_user, CURRENT_USER()));
END//
CREATE TRIGGER trg_products_ad AFTER DELETE ON products FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name,row_pk,action,old_data,changed_by)
  VALUES ('products', OLD.product_id, 'DELETE',
          JSON_OBJECT('name',OLD.name,'price',OLD.price),
          COALESCE(@app_user, CURRENT_USER()));
END//
DELIMITER ;

SET @app_user = 'asha@example.com';
INSERT INTO products VALUES (1, 'Keyboard', 1000.00);
UPDATE products SET price = 1100.00 WHERE product_id = 1;
SET @app_user = 'ravi@example.com';
DELETE FROM products WHERE product_id = 1;

SELECT audit_id, action, old_data, new_data, changed_by
FROM audit_log WHERE table_name = 'products' AND row_pk = '1' ORDER BY audit_id;

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0; changed_at omitted - varies)
-- ============================================

-- audit_id | action | old_data                               | new_data                               | changed_by
-- 1        | INSERT | NULL                                   | {"name": "Keyboard", "price": 1000.00} | asha@example.com
-- 2        | UPDATE | {"name": "Keyboard", "price": 1000.00} | {"name": "Keyboard", "price": 1100.00} | asha@example.com
-- 3        | DELETE | {"name": "Keyboard", "price": 1100.00} | NULL                                   | ravi@example.com

-- Query a field inside the JSON: old vs new price of updates
SELECT JSON_EXTRACT(old_data,'$.price') AS old_price,
       JSON_EXTRACT(new_data,'$.price') AS new_price
FROM audit_log WHERE action = 'UPDATE';
-- old_price | new_price
-- 1000.00   | 1100.00
```

---

## 🔍 Why This Works (3 lines max)
Row-level AFTER triggers fire inside the same transaction as the change, so the audit row commits or rolls back with it and cannot be bypassed by another code path. JSON images keep one table usable for every audited table.
हिंदी: AFTER trigger उसी transaction में चलता है, इसलिए audit row बदलाव के साथ ही commit/rollback होती है; JSON से एक ही table सब tables के लिए चलती है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: ONE generic trigger function for any table (real PGlite run)
CREATE TABLE audit_log (
  audit_id   BIGSERIAL PRIMARY KEY,
  table_name TEXT NOT NULL,
  row_pk     TEXT NOT NULL,
  action     TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
  old_data   JSONB,
  new_data   JSONB,
  changed_by TEXT,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_row ON audit_log (table_name, row_pk, changed_at);

CREATE FUNCTION audit_row() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit_log (table_name,row_pk,action,old_data,new_data,changed_by)
  VALUES (TG_TABLE_NAME,
          COALESCE(NEW.product_id, OLD.product_id)::text,   -- adapt to the table's key
          TG_OP,
          CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
          CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) END,
          COALESCE(current_setting('app.actor', true), current_user));
  RETURN NULL;                                              -- AFTER trigger: return value ignored
END $$;

CREATE TRIGGER trg_products_audit AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW EXECUTE FUNCTION audit_row();

SET app.actor = 'asha@example.com';          -- app sets this per session / SET LOCAL per transaction
-- Same INSERT/UPDATE/DELETE sequence gives (real output):
-- 1 | INSERT | NULL                                           | {"name":"Keyboard","price":1000,"product_id":1} | asha@example.com
-- 2 | UPDATE | {"name":"Keyboard","price":1000,...}           | {"name":"Keyboard","price":1100,...}            | asha@example.com
-- 3 | DELETE | {"name":"Keyboard","price":1100,...}           | NULL                                            | ravi@example.com
-- SELECT old_data->>'price' AS old_price, new_data->>'price' AS new_price FROM audit_log WHERE action='UPDATE';
-- old_price | new_price
-- 1000.00   | 1100.00        (JSONB keeps the numeric scale; the JS client printed the raw images as 1000/1100)

-- Other approaches (not run): extension pgaudit, temporal tables / system versioning
-- (MariaDB native; MySQL has none), CDC from the WAL/binlog (Debezium) for audit without trigger overhead,
-- partition audit_log by month (PARTITION BY RANGE (changed_at)) and archive old partitions.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: updating or deleting audit rows - an audit log must be append-only.
-- ✅ GRANT only INSERT/SELECT on audit_log to the app user; no UPDATE/DELETE.

-- ❌ Wrong: "who" = the DB account. With a connection pool every change shows 'app_user@%'.
-- ✅ Pass the real user: MySQL SET @app_user = ...; PgSQL SET LOCAL app.actor = ... inside the transaction.
--    (Careful with SET (session) behind transaction-pooled PgBouncer - use SET LOCAL.)

-- ❌ Wrong: logging full rows including secrets (password hashes, card data) - mask them in the trigger.

-- ❌ Wrong: no index/partitioning -> history lookups scan millions of rows; audit tables grow fastest.

-- ❌ Wrong: BEFORE triggers for audit - the change may still fail; use AFTER so only real changes are logged.
-- Also remember: TRUNCATE and bulk loads that disable triggers bypass row triggers.
```

---

## 🎯 Interview Tip (1 line)
Say: "Trigger-based audit into an append-only JSON table gives an in-transaction guarantee, but I pass the real actor via session variable, partition by time, restrict grants, and consider CDC from the WAL/binlog when trigger overhead or tamper-resistance matters."

---

## 🔗 Related Questions
→ Q145 (Soft delete) | Q139 (WAL) | Q142 (When to denormalize) | Q158 (Generated columns)
