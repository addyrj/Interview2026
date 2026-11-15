---

# Q026. PRIMARY KEY, UNIQUE and FOREIGN KEY (Cascade)
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: UNIQUE allows many NULLs; PostgreSQL: UNIQUE allows many NULLs, NULLS NOT DISTINCT in 15+)

---

## ❓ Question
Model Customers, Orders and Payments with ON DELETE CASCADE and ON DELETE SET NULL. What happens when a customer is deleted? How does SQL Server treat NULLs in a UNIQUE constraint (and how do you allow many NULLs)? What is the "multiple cascade paths" restriction?

---

## 💡 Quick Concept (2 lines only)
PRIMARY KEY = unique + NOT NULL, one per table. UNIQUE = unique, and SQL Server allows only ONE NULL in it. FOREIGN KEY actions: NO ACTION (default, blocks), CASCADE, SET NULL, SET DEFAULT.
हिंदी: PK = unique + NOT NULL। SQL Server में UNIQUE column में सिर्फ एक NULL चलता है (MySQL/PG में कई)। FK actions: NO ACTION, CASCADE, SET NULL, SET DEFAULT।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Customers (
  CustomerId INT           NOT NULL CONSTRAINT PK_Customers PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL
);

CREATE TABLE Orders (
  OrderId    INT NOT NULL CONSTRAINT PK_Orders PRIMARY KEY,
  CustomerId INT NOT NULL,
  CONSTRAINT FK_Orders_Customers FOREIGN KEY (CustomerId)
      REFERENCES Customers (CustomerId) ON DELETE CASCADE
);

CREATE TABLE Payments (
  PaymentId INT NOT NULL CONSTRAINT PK_Payments PRIMARY KEY,
  OrderId   INT NULL,                                   -- must be NULLable for SET NULL
  CONSTRAINT FK_Payments_Orders FOREIGN KEY (OrderId)
      REFERENCES Orders (OrderId) ON DELETE SET NULL
);

CREATE TABLE Tickets (
  TicketId   INT NOT NULL CONSTRAINT PK_Tickets PRIMARY KEY,
  CustomerId INT NULL,
  CONSTRAINT FK_Tickets_Customers FOREIGN KEY (CustomerId)
      REFERENCES Customers (CustomerId) ON DELETE SET NULL
);

INSERT INTO Customers VALUES (1, N'Asha'), (2, N'Ravi');
INSERT INTO Orders    VALUES (10, 1), (11, 1), (12, 2);
INSERT INTO Tickets   VALUES (1, 1), (2, 2);
INSERT INTO Payments  VALUES (100, 10), (101, 12);
GO

-- ============================================
-- SOLUTION
-- ============================================

DELETE FROM Customers WHERE CustomerId = 1;

SELECT OrderId, CustomerId FROM Orders;
-- OrderId | CustomerId
-- 12      | 2                  <- orders 10 and 11 cascaded away

SELECT TicketId, CustomerId FROM Tickets;
-- TicketId | CustomerId
-- 1        | NULL               <- SET NULL
-- 2        | 2

SELECT PaymentId, OrderId FROM Payments;
-- PaymentId | OrderId
-- 100       | NULL               <- order 10 vanished, payment kept with NULL
-- 101       | 12

-- Inserting an order for a missing customer fails:
INSERT INTO Orders VALUES (13, 99);   -- FOREIGN KEY violation (error 547 per Microsoft docs)

-- Results derived by running the equivalent schema with PRAGMA foreign_keys=ON on SQLite 3.49;
-- not executed on SQL Server. (Cascade chains are allowed in SQL Server as long as no table can
-- be reached by two different cascade paths.)
```

---

## 🔍 Why This Works (3 lines max)
Deleting the parent triggers the referential action on children inside the same statement: CASCADE deletes them (and their own cascading children), SET NULL nulls the referencing column. NO ACTION rejects the delete when children exist. SQL Server refuses to create a foreign key that would produce multiple cascade paths or cycles, so you use NO ACTION plus a procedure or trigger there.
हिंदी: Parent delete होते ही child पर action चलता है: CASCADE = child भी delete, SET NULL = column NULL। Multiple cascade paths/cycles वाला FK SQL Server बनने नहीं देता।

---

## ⚡ Alternative Solution

```sql
-- UNIQUE and NULL: SQL Server allows exactly ONE NULL in a UNIQUE constraint/index
CREATE TABLE Users (
  UserId INT IDENTITY PRIMARY KEY,
  Phone  VARCHAR(20) NULL,
  CONSTRAINT UQ_Users_Phone UNIQUE (Phone)
);
-- INSERT two rows with Phone = NULL -> the second one fails (per Microsoft docs; SQLite and MySQL
-- would accept both, so this behaviour was NOT verified on an engine here).

-- Fix: filtered unique index - unique among non-NULL values, any number of NULLs
ALTER TABLE Users DROP CONSTRAINT UQ_Users_Phone;
CREATE UNIQUE NONCLUSTERED INDEX UX_Users_Phone ON Users (Phone) WHERE Phone IS NOT NULL;

-- Index the FK column - SQL Server does not do it for you; cascades and joins need it
CREATE INDEX IX_Orders_CustomerId ON Orders (CustomerId);

-- Soft delete (IsDeleted flag) avoids dangerous cascades entirely
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ON DELETE CASCADE everywhere "for convenience"
-- Deleting one customer silently removes orders, order lines, payments... Often a compliance problem.
-- ✅ Use NO ACTION by default; cascade only for true owned children (OrderItems of an Order).

-- ❌ Wrong: SET NULL on a NOT NULL column - the FK creation fails
-- ❌ Wrong: two cascade paths to the same table (e.g., Orders.CreatedBy and Orders.ApprovedBy both
--           cascading from Employees) - SQL Server rejects the second FK at creation time

-- ❌ Wrong: assuming UNIQUE permits many NULLs (MySQL/PostgreSQL habit)
-- ❌ Wrong: no index on the FK column -> every parent delete scans the child table
```

---

## 🎯 Interview Tip (1 line)
Say: "PK is unique and not null; UNIQUE allows one NULL in SQL Server, so I use a filtered unique index when I need many NULLs; I index FK columns myself; I prefer NO ACTION and soft deletes, and use CASCADE only for strictly owned children." Mention the multiple-cascade-paths limitation.

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q105 (filtered indexes) | Q176 (PK vs unique vs FK) | Q186 (e-commerce schema design)
