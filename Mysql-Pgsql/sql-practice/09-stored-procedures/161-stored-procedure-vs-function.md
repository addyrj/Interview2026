---

# Q161. Stored Procedure vs Function — When to Use Each
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the difference between a stored procedure and a function? Show a real stored procedure with error handling and a useful user-defined function. When do you use each?

---

## 💡 Quick Concept (2 lines only)
Function: returns a single value, usable in SELECT/WHERE, cannot have side effects (PgSQL) or transactions. Stored procedure: executes a sequence of statements, can have multiple outputs, handle errors, and manage transactions — called with CALL, not in SELECT.
हिंदी: Function = single value return, SELECT में use होती है। Stored procedure = complex logic + transactions + error handling, CALL से execute होती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- STORED PROCEDURE — MySQL Example
-- ============================================

-- Transfer money between accounts with full ACID safety:
DELIMITER $$

CREATE PROCEDURE transfer_money(
  IN  p_from_id   INT,
  IN  p_to_id     INT,
  IN  p_amount    DECIMAL(10,2),
  OUT p_status    VARCHAR(50),
  OUT p_message   VARCHAR(200)
)
BEGIN
  -- Declare variables and handlers FIRST (MySQL requirement)
  DECLARE v_from_balance DECIMAL(10,2);
  DECLARE v_to_exists    INT DEFAULT 0;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    SET p_status = 'ERROR';
    SET p_message = 'Transaction failed — rolled back';
  END;

  -- Input validation
  IF p_amount <= 0 THEN
    SET p_status = 'ERROR';
    SET p_message = 'Amount must be positive';
    LEAVE transfer_money;  -- named EXIT (MySQL uses block label)
  END IF;

  START TRANSACTION;

  -- Check source account balance (lock the row)
  SELECT balance INTO v_from_balance
  FROM accounts
  WHERE id = p_from_id
  FOR UPDATE;

  -- Check destination exists
  SELECT COUNT(*) INTO v_to_exists FROM accounts WHERE id = p_to_id;

  IF v_from_balance IS NULL THEN
    ROLLBACK;
    SET p_status = 'ERROR';
    SET p_message = 'Source account not found';
  ELSEIF v_to_exists = 0 THEN
    ROLLBACK;
    SET p_status = 'ERROR';
    SET p_message = 'Destination account not found';
  ELSEIF v_from_balance < p_amount THEN
    ROLLBACK;
    SET p_status = 'ERROR';
    SET p_message = CONCAT('Insufficient funds. Balance: ', v_from_balance);
  ELSE
    -- Both accounts valid, balance sufficient → do the transfer
    UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_id;
    UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_id;

    -- Audit trail
    INSERT INTO transactions (from_id, to_id, amount, created_at)
    VALUES (p_from_id, p_to_id, p_amount, NOW());

    COMMIT;
    SET p_status = 'SUCCESS';
    SET p_message = CONCAT('Transferred ', p_amount, ' successfully');
  END IF;
END$$

DELIMITER ;

-- Call the procedure:
CALL transfer_money(1, 2, 100.00, @status, @message);
SELECT @status, @message;
-- @status = 'SUCCESS', @message = 'Transferred 100.00 successfully'

-- ============================================
-- STORED PROCEDURE — PostgreSQL Example
-- ============================================

-- PgSQL uses PL/pgSQL (different syntax from MySQL):
CREATE OR REPLACE PROCEDURE transfer_money(
  p_from_id   INT,
  p_to_id     INT,
  p_amount    DECIMAL(10,2),
  INOUT p_result JSON DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_from_balance DECIMAL(10,2);
BEGIN
  -- Input validation
  IF p_amount <= 0 THEN
    p_result := json_build_object('status', 'ERROR', 'message', 'Amount must be positive');
    RETURN;
  END IF;

  -- Lock source account
  SELECT balance INTO v_from_balance
  FROM accounts WHERE id = p_from_id FOR UPDATE;

  IF NOT FOUND THEN
    ROLLBACK;
    p_result := json_build_object('status', 'ERROR', 'message', 'Source account not found');
    RETURN;
  END IF;

  IF v_from_balance < p_amount THEN
    ROLLBACK;
    p_result := json_build_object(
      'status', 'ERROR',
      'message', 'Insufficient funds',
      'balance', v_from_balance
    );
    RETURN;
  END IF;

  -- Execute transfer
  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_id;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_id;

  INSERT INTO transactions (from_id, to_id, amount) VALUES (p_from_id, p_to_id, p_amount);

  p_result := json_build_object('status', 'SUCCESS', 'amount', p_amount);
  -- COMMIT happens automatically when procedure exits successfully (in PgSQL 11+)
EXCEPTION WHEN OTHERS THEN
  ROLLBACK;
  p_result := json_build_object('status', 'ERROR', 'message', SQLERRM);
END;
$$;

-- Call (PgSQL 11+ syntax):
CALL transfer_money(1, 2, 100.00);
-- Or with result:
DO $$
DECLARE v_result JSON;
BEGIN
  CALL transfer_money(1, 2, 100.00, v_result);
  RAISE NOTICE 'Result: %', v_result;
END;
$$;

-- ============================================
-- USER-DEFINED FUNCTION — MySQL
-- ============================================

-- A function to calculate age from birth date:
DELIMITER $$

CREATE FUNCTION calculate_age(p_birth_date DATE)
RETURNS INT
DETERMINISTIC          -- same input always gives same output (optimizer hint)
NO SQL                 -- no SQL statements (pure calculation)
BEGIN
  RETURN TIMESTAMPDIFF(YEAR, p_birth_date, CURDATE())
    - (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(p_birth_date, '%m%d'));
  -- subtract 1 if birthday hasn't happened yet this year
END$$

DELIMITER ;

-- Use in queries (this is where functions shine!):
SELECT name, birth_date, calculate_age(birth_date) AS age
FROM users
WHERE calculate_age(birth_date) BETWEEN 18 AND 25;

-- ============================================
-- USER-DEFINED FUNCTION — PostgreSQL
-- ============================================

-- Function to slugify a string (URL-friendly):
CREATE OR REPLACE FUNCTION slugify(input TEXT)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE  -- same input = same output, no side effects (optimizer can cache/inline)
STRICT     -- returns NULL if any input is NULL
AS $$
BEGIN
  RETURN LOWER(
    REGEXP_REPLACE(
      REGEXP_REPLACE(
        TRIM(input),
        '[^a-zA-Z0-9\s-]', '', 'g'  -- remove non-alphanumeric
      ),
      '\s+', '-', 'g'               -- replace spaces with hyphens
    )
  );
END;
$$;

-- Use in queries:
SELECT title, slugify(title) AS slug FROM posts;
-- 'Hello World!' → 'hello-world'

-- Use as generated column (PgSQL):
ALTER TABLE posts ADD COLUMN slug TEXT GENERATED ALWAYS AS (slugify(title)) STORED;

-- ============================================
-- COMPARISON TABLE
-- ============================================

/*
Feature              | Stored Procedure              | Function
─────────────────────┼───────────────────────────────┼──────────────────────────
Return value         | 0 or more (via OUT params)    | Exactly 1 value (or TABLE)
Use in SELECT        | ❌ Cannot                     | ✅ Yes: SELECT func()
Transaction control  | ✅ Full (COMMIT/ROLLBACK)     | ❌ No (MySQL) / limited (PgSQL)
Side effects         | ✅ Can INSERT/UPDATE/DELETE    | PgSQL IMMUTABLE = no side effects
Called with          | CALL proc_name(args)          | SELECT func_name(args)
Error handling       | ✅ Full HANDLER support       | ✅ EXCEPTION in PgSQL
Multiple result sets | ✅ MySQL: multiple SELECTs    | ❌
Use in WHERE         | ❌                            | ✅ WHERE func(col) = value
Reuse in expressions | ❌                            | ✅ price * tax_rate(country)
*/

-- ============================================
-- WHEN TO USE STORED PROCEDURES
-- ============================================

/*
Good use cases for procedures:
  ✅ Complex multi-step transactions (transfer, order placement)
  ✅ Batch operations (monthly interest calculation, data cleanup)
  ✅ Encapsulate business rules that MUST run at DB level
  ✅ Legacy system integration (some systems call via CALL)
  ✅ When you need COMMIT/ROLLBACK control (MySQL)

Avoid procedures when:
  ❌ Business logic belongs in the application layer
  ❌ Logic needs to be version-controlled cleanly (procedures are harder)
  ❌ Logic changes frequently (deploy procedure = DB migration, not code deploy)
  ❌ You need to test with mocks (procedures are hard to unit test)

When to use functions:
  ✅ Computed columns: calculate_tax(price, country)
  ✅ Reusable expressions in WHERE, SELECT, ORDER BY
  ✅ Text transformations: slugify(), format_phone()
  ✅ Business calculations: discount_rate(customer_tier)
  ✅ PgSQL: table-returning functions (alternative to views)

2024 best practice:
  - Keep most logic in application code
  - Use triggers for automatic side effects (auditing, denormalization)
  - Use functions for pure computations and generated columns
  - Use procedures only when truly necessary (complex atomic operations)
*/
```

---

## 🔍 Why This Works (3 lines max)
Stored procedures encapsulate multi-step logic at the database level, provide atomicity with explicit COMMIT/ROLLBACK, and can output multiple values via OUT parameters — ideal for complex financial transactions. Functions return a single value, can be embedded in SQL expressions, and when marked IMMUTABLE give the optimizer a hint to cache or inline them. The key distinction: use functions for pure computations in SQL, procedures for stateful multi-step operations.
हिंदी: Procedure = multi-step transaction + error handling + COMMIT/ROLLBACK। Function = pure computation, SELECT में embed होती है। Business logic application layer में रखो, DB procedures minimally use करो।

---

## ⚡ Alternative Solution

```sql
-- PgSQL: Table-valued function (returns a set of rows — like a parameterized view):
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id INT, p_status VARCHAR DEFAULT NULL)
RETURNS TABLE(id INT, amount DECIMAL, status VARCHAR, created_at TIMESTAMPTZ)
LANGUAGE sql
STABLE  -- reads DB but doesn't modify; result can change per transaction
AS $$
  SELECT id, amount, status, created_at
  FROM orders
  WHERE user_id = p_user_id
    AND (p_status IS NULL OR status = p_status)
  ORDER BY created_at DESC;
$$;

-- Use like a table:
SELECT * FROM get_user_orders(42, 'completed');
SELECT * FROM get_user_orders(42) WHERE amount > 100;
-- Can JOIN with other tables!
SELECT u.name, o.amount FROM users u, get_user_orders(u.id) o WHERE o.status = 'pending';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using function for operations with side effects in MySQL
-- MySQL functions used in SELECT cannot modify data (strict DETERMINISTIC/NO SQL rules)
-- ✅ Move INSERT/UPDATE logic to a procedure, call it separately

-- ❌ Wrong: DETERMINISTIC keyword when function isn't actually deterministic
CREATE FUNCTION get_current_price(product_id INT)
RETURNS DECIMAL DETERMINISTIC  -- ← WRONG! price changes in DB!
BEGIN
  SELECT price FROM products WHERE id = product_id;
END;
-- DETERMINISTIC = optimizer may cache result and not re-execute
-- ✅ Don't mark as DETERMINISTIC if the result depends on DB state that can change

-- ❌ Wrong: Too much business logic in stored procedures
-- Procedures in DB = hard to test, hard to version, tightly coupled to DB engine
-- ✅ Keep procedures for: atomic transactions, batch jobs, triggers
-- Move business logic to application layer (Node.js / Python / Go)

-- ❌ Wrong: PgSQL function without SECURITY DEFINER when needed for RLS bypass
-- By default function runs with CALLER's privileges
-- For admin functions that need to bypass RLS:
CREATE FUNCTION admin_get_all_orders()
RETURNS SETOF orders
LANGUAGE sql SECURITY DEFINER  -- runs with function OWNER's privileges (bypasses RLS)
AS $$ SELECT * FROM orders; $$;
```

---

## 🎯 Interview Tip (1 line)
Say: "I use stored procedures for complex atomic operations that need explicit transaction control — like financial transfers where I need to lock rows, validate, commit or rollback in one atomic unit. Functions are for pure computations used inline in SQL: `calculate_age(birth_date)` in SELECT, `slugify(title)` for generated columns. In general I keep business logic in the application layer and limit procedures to truly DB-specific concerns."

---

## 🔗 Related Questions
→ Q129 (deadlock) | Q121 (isolation levels) | Q225 (ACID) | Q196 (row-level security)
