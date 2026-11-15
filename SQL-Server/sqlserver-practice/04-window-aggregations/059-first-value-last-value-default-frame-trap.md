# Q059. FIRST_VALUE, LAST_VALUE and the Default Frame Trap
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2012+; IGNORE NULLS needs SQL Server 2022 / Azure SQL) — same trap exists in MySQL 8 and PostgreSQL

---

## ❓ Question
For each employee show the top earner of their department and the lowest earner of their department. A first attempt with `LAST_VALUE(EmpName) OVER (PARTITION BY Dept ORDER BY Salary DESC)` returns each employee's own name instead of the lowest earner. Why, and how do you fix it?

---

## 💡 Quick Concept (2 lines only)
With ORDER BY and no explicit frame, the frame ends at CURRENT ROW (plus peers), so LAST_VALUE just returns the current row's value. FIRST_VALUE works because the frame always starts at the first row.
हिंदी: Default frame current row पर ख़त्म होता है, इसलिए LAST_VALUE अपनी ही row देता है। Frame को UNBOUNDED FOLLOWING तक बढ़ाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Employees (
    EmpId   INT PRIMARY KEY,
    EmpName VARCHAR(20) NOT NULL,
    Dept    VARCHAR(20) NOT NULL,
    Salary  INT         NOT NULL
);

INSERT INTO Employees (EmpId, EmpName, Dept, Salary) VALUES
 (1, 'Asha',  'IT',      90000), (2, 'Ravi',  'IT',      70000),
 (3, 'Meena', 'IT',      80000), (4, 'Karan', 'HR',      50000),
 (5, 'Divya', 'HR',      65000), (6, 'Sam',   'Finance', 72000);

-- ============================================
-- SOLUTION
-- ============================================
SELECT
    Dept, EmpName, Salary,
    FIRST_VALUE(EmpName) OVER (PARTITION BY Dept ORDER BY Salary DESC) AS TopEarner,
    LAST_VALUE(EmpName)  OVER (PARTITION BY Dept ORDER BY Salary DESC) AS LastDefaultFrame,   -- the trap
    LAST_VALUE(EmpName)  OVER (PARTITION BY Dept ORDER BY Salary DESC
                               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS LowestEarner
FROM Employees
ORDER BY Dept, Salary DESC;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- Dept    | EmpName | Salary | TopEarner | LastDefaultFrame | LowestEarner
-- Finance | Sam     | 72000  | Sam       | Sam              | Sam
-- HR      | Divya   | 65000  | Divya     | Divya            | Karan
-- HR      | Karan   | 50000  | Divya     | Karan            | Karan
-- IT      | Asha    | 90000  | Asha      | Asha             | Ravi
-- IT      | Meena   | 80000  | Asha      | Meena            | Ravi
-- IT      | Ravi    | 70000  | Asha      | Ravi             | Ravi
```

---

## 🔍 Why This Works (3 lines max)
The implicit frame is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, so the "last" row inside the frame is the current row (or its last peer). Writing ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING makes the frame the entire partition, so LAST_VALUE sees the real last row. FIRST_VALUE never breaks because the frame always begins at the partition start.
हिंदी: Frame = जितनी rows function को "दिखती" हैं। Whole partition दिखाओ तो LAST_VALUE सही आता है।

---

## ⚡ Alternative Solution

```sql
-- Option 1: flip the sort and use FIRST_VALUE (no frame needed)
FIRST_VALUE(EmpName) OVER (PARTITION BY Dept ORDER BY Salary ASC) AS LowestEarner

-- Option 2: if you only need the value, not the name, use plain aggregates over the partition
SELECT Dept, EmpName, Salary,
       MAX(Salary) OVER (PARTITION BY Dept) AS DeptMax,
       MIN(Salary) OVER (PARTITION BY Dept) AS DeptMin
FROM Employees;
-- No ORDER BY in OVER -> frame is the whole partition, no trap.
-- Option 1 returns Karan / Ravi / Sam as LowestEarner, same as the explicit-frame result above (hand-checked).

-- SQL Server 2022+: carry the last non-NULL value forward
-- LAST_VALUE(Col) IGNORE NULLS OVER (ORDER BY Id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ LAST_VALUE with only ORDER BY: returns the current row's own value
LAST_VALUE(EmpName) OVER (PARTITION BY Dept ORDER BY Salary DESC)

-- ❌ Using RANGE ... UNBOUNDED FOLLOWING and a non-unique ORDER BY, then assuming a stable "last" row among ties
-- ❌ Using FIRST_VALUE with no ORDER BY -> syntax error in T-SQL (ORDER BY is mandatory for FIRST_VALUE/LAST_VALUE)
-- ❌ Assuming IGNORE NULLS works on SQL Server 2019 or earlier -> it needs 2022 / Azure SQL
```

---

## 🎯 Interview Tip (1 line)
Say: "LAST_VALUE is the classic default-frame trap — I always spell out ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING, or I just reverse the sort and use FIRST_VALUE, which is cheaper to reason about."

---

## 🔗 Related Questions
→ Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q057 (LAG and LEAD) | Q058 (SUM/AVG OVER with frames) | Q067 (Top-N per group with window functions)
