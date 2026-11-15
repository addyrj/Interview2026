---

# Q169. MySQL GROUP BY Mode — ONLY_FULL_GROUP_BY
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (verified on MySQL 9.1); PostgreSQL behaviour verified on PGlite

---

## ❓ Question
Why does `SELECT dept_id, name, MAX(salary) FROM employees GROUP BY dept_id` fail with error 1055, what did old MySQL do instead, and what are the correct ways to get "the employee with the max salary per department"?

---

## 💡 Quick Concept (2 lines only)
With ONLY_FULL_GROUP_BY (default since 5.7.5), every selected column must be in GROUP BY, aggregated, or functionally dependent on the GROUP BY columns. Without it MySQL picks an arbitrary row's value for the extra column, which gives wrong-looking results.
हिंदी: ONLY_FULL_GROUP_BY में हर column GROUP BY में या aggregate में होना चाहिए, वरना MySQL किसी भी row का value उठा लेता था (गलत नतीजा)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE employees (id INT PRIMARY KEY, name VARCHAR(50), dept_id INT, salary DECIMAL(10,2));
INSERT INTO employees VALUES
  (1,'Alice',10,90000),(2,'Bob',10,70000),
  (3,'Carol',20,80000),(4,'Dave',20,95000),(5,'Eve',30,60000);

CREATE TABLE depts (id INT PRIMARY KEY, name VARCHAR(50));
INSERT INTO depts VALUES (10,'Eng'),(20,'Sales'),(30,'HR');

-- ============================================
-- SOLUTION
-- ============================================

SELECT @@SESSION.sql_mode;
-- ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

-- Step 1: the failing query
SELECT dept_id, name, MAX(salary) FROM employees GROUP BY dept_id;
-- ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains
-- nonaggregated column 't.employees.name' which is not functionally dependent on columns in GROUP BY clause;
-- this is incompatible with sql_mode=only_full_group_by

-- Step 2: what the mode protected you from (turn it off for this session only)
SET SESSION sql_mode = (SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));
SELECT dept_id, name, MAX(salary) AS max_sal FROM employees GROUP BY dept_id ORDER BY dept_id;
-- dept_id | name  | max_sal
-- 10      | Alice | 90000.00
-- 20      | Carol | 95000.00   <- WRONG: Carol earns 80000; 95000 is Dave's salary
-- 30      | Eve   | 60000.00
SET SESSION sql_mode = DEFAULT;

-- Step 3: correct fix A — join to the aggregate
SELECT e.dept_id, e.name, e.salary
FROM employees e
JOIN (SELECT dept_id, MAX(salary) AS max_sal FROM employees GROUP BY dept_id) m
  ON m.dept_id = e.dept_id AND m.max_sal = e.salary
ORDER BY e.dept_id;
-- 10 Alice 90000.00 | 20 Dave 95000.00 | 30 Eve 60000.00      (ties would return several rows)

-- Step 4: correct fix B — window function (MySQL 8.0+)
SELECT dept_id, name, salary
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn FROM employees) t
WHERE rn = 1 ORDER BY dept_id;
-- same 3 rows

-- Step 5: when you truly don't care which value — say so explicitly
SELECT dept_id, ANY_VALUE(name) AS some_name, MAX(salary) AS max_sal
FROM employees GROUP BY dept_id ORDER BY dept_id;
-- (name is arbitrary: here Alice/Carol/Eve)

-- Step 6: functional dependency is allowed — grouping by the PK lets you select other columns of that table
SELECT d.id, d.name, COUNT(e.id) AS headcount
FROM depts d LEFT JOIN employees e ON e.dept_id = d.id
GROUP BY d.id ORDER BY d.id;                -- OK: d.name depends on d.id
-- 10 Eng 2 | 20 Sales 2 | 30 HR 1

SELECT d.id, d.name, COUNT(e.id) AS headcount
FROM depts d LEFT JOIN employees e ON e.dept_id = d.id GROUP BY d.name;
-- ERROR 1055: d.id is not functionally dependent on d.name (name is not unique)
```

---

## 🔍 Why This Works (3 lines max)
For each group there is one output row, so each selected column needs exactly one value per group: either a grouping column, an aggregate, or something fully determined by the grouping columns (e.g. other columns of a table when you group by its PK). If not, MySQL can't know which row's value you meant.
हिंदी: हर group की एक ही output row बनती है, इसलिए हर column का एक निश्चित value होना चाहिए — grouping column, aggregate, या उस पर निर्भर column।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL has always enforced this (verified on PGlite):
SELECT dept_id, name, MAX(salary) FROM employees GROUP BY dept_id;
-- ERROR: column "employees.name" must appear in the GROUP BY clause or be used in an aggregate function

-- PostgreSQL shortcut for top-1 per group (verified):
SELECT DISTINCT ON (dept_id) dept_id, name, salary FROM employees ORDER BY dept_id, salary DESC;
-- 10 Alice 90000.00 | 20 Dave 95000.00 | 30 Eve 60000.00

-- Set the mode permanently (my.cnf), never disable it just to silence an error:
-- [mysqld]
-- sql_mode = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: disable ONLY_FULL_GROUP_BY globally to "fix" legacy queries
SET GLOBAL sql_mode = '';       -- the query now runs but returns mismatched columns (Carol with Dave's salary)
-- ✅ Fix the query (join / window function / ANY_VALUE if truly arbitrary)

-- ❌ Wrong: assuming MAX(salary) with a bare "name" returns the name of the max row
-- ❌ Wrong: GROUP BY d.name when names are not unique (merges two different depts)
-- ❌ Wrong: relying on the old MySQL <5.7 behaviour in code ported to PostgreSQL -> instant errors
```

---

## 🎯 Interview Tip (1 line)
Say: "ONLY_FULL_GROUP_BY is a correctness guard — without it MySQL returns an arbitrary row's value for non-aggregated columns; I fix the query with a window function or join to the aggregate, use ANY_VALUE only when any value is acceptable, and never disable the mode globally."

---

## 🔗 Related Questions
→ Q075 (Top N per group) | Q066 (ROW_NUMBER vs RANK) | Q171 (MySQL 8 window functions) | Q239 (Find duplicates)
