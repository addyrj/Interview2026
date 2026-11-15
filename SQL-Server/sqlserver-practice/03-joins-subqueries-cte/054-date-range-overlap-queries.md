---

# Q054. Date-Range Overlap Queries
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same predicate works in MySQL and PostgreSQL; PostgreSQL also has native range types and the && operator)

---

## ❓ Question
`Bookings(BookingId, RoomId, StartDate, EndDate)` stores hotel bookings where the end date is the checkout day (a booking ending 5-Mar and another starting 5-Mar do NOT clash). (a) Find existing bookings that overlap each other, (b) check whether a new request can be accepted, (c) prevent double booking safely from a stored procedure.

---

## 💡 Quick Concept (2 lines only)
Two ranges overlap when `A.Start < B.End AND A.End > B.Start` (for half-open ranges [start, end)). Memorise this one condition instead of enumerating the cases (inside, contains, left overlap, right overlap).
हिंदी: दो ranges overlap होती हैं जब `A.Start < B.End AND A.End > B.Start`। चार cases याद करने की ज़रूरत नहीं, बस यह एक condition।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Bookings (
  BookingId INT PRIMARY KEY,
  RoomId    INT  NOT NULL,
  StartDate DATE NOT NULL,      -- check-in
  EndDate   DATE NOT NULL,      -- check-out (exclusive: the room is free again that day)
  CONSTRAINT CK_Bookings_Dates CHECK (EndDate > StartDate)
);

INSERT INTO Bookings (BookingId, RoomId, StartDate, EndDate) VALUES
  (1, 101, '2024-03-01', '2024-03-05'),
  (2, 101, '2024-03-05', '2024-03-08'),   -- starts the day booking 1 ends: NOT a clash
  (3, 101, '2024-03-07', '2024-03-10'),   -- overlaps booking 2
  (4, 102, '2024-03-01', '2024-03-04'),
  (5, 102, '2024-03-10', '2024-03-12');

-- ============================================
-- (a) EXISTING OVERLAPS (each pair once)
-- ============================================
SELECT a.BookingId AS BookingA, b.BookingId AS BookingB, a.RoomId
FROM Bookings AS a
INNER JOIN Bookings AS b
  ON  a.RoomId    = b.RoomId
  AND a.BookingId < b.BookingId         -- removes self-pairs and mirrored pairs
  AND a.StartDate < b.EndDate
  AND a.EndDate   > b.StartDate
ORDER BY a.BookingId, b.BookingId;

-- EXPECTED OUTPUT (derived on SQLite):
-- BookingA | BookingB | RoomId
-- 2        | 3        | 101

-- ============================================
-- (b) CAN A NEW REQUEST BE ACCEPTED?
-- ============================================
DECLARE @RoomId INT = 101, @NewStart DATE = '2024-03-10', @NewEnd DATE = '2024-03-12';

SELECT CASE WHEN EXISTS (
         SELECT 1 FROM Bookings
         WHERE RoomId = @RoomId AND StartDate < @NewEnd AND EndDate > @NewStart)
       THEN 'CONFLICT' ELSE 'FREE' END AS Result;
-- Room 101, 10-Mar to 12-Mar: booking 3 ends 10-Mar, so no clash.
-- EXPECTED OUTPUT (derived by running the same predicate on SQLite, 0 matching rows): FREE
-- Try @NewStart = '2024-03-08', @NewEnd = '2024-03-09' instead: it overlaps booking 3
-- (07-Mar..10-Mar), SQLite matched 1 row -> CONFLICT.

-- ============================================
-- (c) SAFE INSERT FROM A PROCEDURE (race-condition aware)
-- ============================================
GO
CREATE PROCEDURE dbo.usp_BookRoom
  @RoomId INT, @StartDate DATE, @EndDate DATE
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;

  BEGIN TRANSACTION;

  IF EXISTS (SELECT 1 FROM dbo.Bookings WITH (UPDLOCK, HOLDLOCK)   -- range lock: blocks concurrent inserts for the same room
             WHERE RoomId = @RoomId AND StartDate < @EndDate AND EndDate > @StartDate)
  BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Room is already booked for that period.', 1;      -- custom error number >= 50000
  END;

  INSERT INTO dbo.Bookings (BookingId, RoomId, StartDate, EndDate)
  SELECT ISNULL(MAX(BookingId), 0) + 1, @RoomId, @StartDate, @EndDate FROM dbo.Bookings;   -- demo only: use IDENTITY/SEQUENCE in real tables

  COMMIT TRANSACTION;
END;
GO

EXEC dbo.usp_BookRoom @RoomId = 102, @StartDate = '2024-03-04', @EndDate = '2024-03-09';
-- The procedure is not executed on SQL Server here; locking behaviour is per Microsoft docs.
-- The conflict predicate itself was verified on SQLite.
```

---

## 🔍 Why This Works (3 lines max)
Two half-open ranges [s1, e1) and [s2, e2) are disjoint only if one ends before or when the other starts: `e1 <= s2 OR e2 <= s1`. Negating that gives `s1 < e2 AND e1 > s2`, which covers every overlap case including one range completely inside the other. The strict `<` / `>` makes "ends the day the next one starts" a non-overlap.
हिंदी: Disjoint होने की शर्त `e1 <= s2 OR e2 <= s1` है; उसका उल्टा = overlap। Strict `<`/`>` से checkout वाले दिन की नई booking clash नहीं मानी जाती।

---

## ⚡ Alternative Solution

```sql
-- Index that supports the lookup (equality on RoomId, then range on StartDate):
CREATE INDEX IX_Bookings_Room_Start ON Bookings (RoomId, StartDate) INCLUDE (EndDate);

-- Inclusive end dates (EndDate is the last night): use <= and >= instead:
--   StartDate <= @NewEnd AND EndDate >= @NewStart
-- Decide inclusive vs exclusive ends ONCE in the schema and document it.

-- PostgreSQL has a database-enforced guarantee: EXCLUDE USING gist (RoomId WITH =, daterange(StartDate, EndDate) WITH &&).
-- SQL Server has no exclusion constraint, so use the locked check above (or a unique day-per-room table).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: only checking whether the new start date falls inside an existing booking
WHERE @NewStart BETWEEN StartDate AND EndDate
-- Misses a new range that starts BEFORE an existing booking and ends inside/after it,
-- and misses a new range that fully contains an existing one. Also BETWEEN is inclusive, so same-day turnover clashes.

-- ❌ Wrong: <= instead of < with exclusive end dates -> false conflicts on checkout day.

-- ❌ Wrong: check-then-insert without a lock
-- Two sessions both see "free" and both insert. Use a transaction with UPDLOCK, HOLDLOCK (or SERIALIZABLE) as above.

-- ❌ Wrong: not removing mirrored pairs -> every conflict is reported twice (and each row with itself).
```

---

## 🎯 Interview Tip (1 line)
Say: "I use the single predicate StartA < EndB AND EndA > StartB with half-open ranges, and I always clarify whether the end date is inclusive. For writes I wrap the check and the insert in a transaction with UPDLOCK/HOLDLOCK so two concurrent requests cannot both pass, and I back it with an index on (RoomId, StartDate)."

---

## 🔗 Related Questions
→ Q125 (lock hints — UPDLOCK) | Q072 (procedures with transactions) | Q049 (gaps and islands) | Q037 (CROSS JOIN and self join)
