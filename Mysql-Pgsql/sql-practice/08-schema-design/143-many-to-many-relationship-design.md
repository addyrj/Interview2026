---

# Q143. Many-to-Many Relationship Design
# Category: Schema Design
# Difficulty: ⭐ Easy
# DB: Both (MySQL 8.0+ | PostgreSQL) — run on MySQL 9.1.0 and PGlite

---

## ❓ Question
Students enroll in many courses and a course has many students. Design the tables with a junction (bridge) table, prevent duplicate enrollments, store attributes of the relationship (grade, date), and write the common queries (list pairs, count per course, students with no course).

---

## 💡 Quick Concept (2 lines only)
A many-to-many relation is two one-to-many relations around a junction table whose primary key is the pair of foreign keys. Attributes that belong to the relationship (grade, enrolled_on) live in the junction table.
हिंदी: Many-to-many को junction table से दो one-to-many में तोड़ो; दोनों FK मिलकर primary key बनें और relationship के attributes (grade, date) उसी table में रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE students (
  student_id   INT PRIMARY KEY,
  student_name VARCHAR(50) NOT NULL
);

CREATE TABLE courses (
  course_id    INT PRIMARY KEY,
  course_title VARCHAR(80) NOT NULL
);

CREATE TABLE enrollments (
  student_id  INT NOT NULL,
  course_id   INT NOT NULL,
  enrolled_on DATE NOT NULL,
  grade       VARCHAR(2),                       -- NULL until graded
  PRIMARY KEY (student_id, course_id),          -- also prevents duplicate enrollment
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id)  REFERENCES courses(course_id)   ON DELETE CASCADE
);

-- Reverse-direction index: PK covers "courses of a student"; this covers "students of a course"
CREATE INDEX idx_enrollments_course ON enrollments (course_id, student_id);

INSERT INTO students VALUES (1,'Asha'), (2,'Ravi'), (3,'Meera');
INSERT INTO courses  VALUES (10,'Databases'), (11,'Networks'), (12,'Compilers');
INSERT INTO enrollments VALUES
  (1, 10, '2024-01-10', 'A'),
  (1, 11, '2024-01-11', NULL),
  (2, 10, '2024-01-12', 'B');

-- ============================================
-- SOLUTION
-- ============================================

-- Query 1: all pairs with relationship attributes
SELECT s.student_name, c.course_title, e.grade
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses  c ON c.course_id  = e.course_id
ORDER BY s.student_name, c.course_title;

-- Query 2: enrolment count per course, including empty courses (LEFT JOIN from courses)
SELECT c.course_title, COUNT(e.student_id) AS enrolled
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.course_id
GROUP BY c.course_id, c.course_title
ORDER BY c.course_id;

-- Query 3: students with no enrollment
SELECT s.student_name
FROM students s
WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.student_id);

-- ============================================
-- EXPECTED OUTPUT (real; same on MySQL 9.1.0 and PGlite)
-- ============================================

-- Query 1:
-- student_name | course_title | grade
-- Asha         | Databases    | A
-- Asha         | Networks     | NULL
-- Ravi         | Databases    | B
--
-- Query 2:
-- course_title | enrolled
-- Databases    | 2
-- Networks     | 1
-- Compilers    | 0
--
-- Query 3:
-- student_name
-- Meera

-- Duplicate enrollment is rejected by the composite PK:
INSERT INTO enrollments VALUES (1, 10, '2024-02-01', NULL);
-- MySQL: ERROR 1062 (23000): Duplicate entry '1-10' for key 'enrollments.PRIMARY'
-- PgSQL: ERROR: duplicate key value violates unique constraint "enrollments_pkey"
```

---

## 🔍 Why This Works (3 lines max)
The composite primary key guarantees one row per (student, course) pair and gives an index for lookups by student; the second index serves lookups by course. Foreign keys keep both sides valid and ON DELETE CASCADE cleans up the junction rows.
हिंदी: Composite PK हर जोड़ी को unique रखता है और student से lookup को index देता है; दूसरा index course से lookup तेज़ करता है।

---

## ⚡ Alternative Solution

```sql
-- Idempotent "enroll if not already" (syntax DIFFERS):
-- MySQL:
INSERT INTO enrollments VALUES (1, 10, '2024-02-01', NULL)
ON DUPLICATE KEY UPDATE grade = grade;            -- no-op update (or INSERT IGNORE)
-- PgSQL:
INSERT INTO enrollments VALUES (1, 10, '2024-02-01', NULL)
ON CONFLICT (student_id, course_id) DO NOTHING;
-- Both verified: row count stayed 3.

-- Aggregate to one row per student:
-- MySQL: SELECT s.student_name, JSON_ARRAYAGG(c.course_title) ... GROUP BY ...
--        -> Asha ["Databases", "Networks"], Ravi ["Databases"]
-- PgSQL: SELECT s.student_name, array_agg(c.course_title ORDER BY c.course_title) ...
--        -> Asha {Databases,Networks}, Ravi {Databases}

-- Surrogate key variant: enrollment_id BIGINT PK + UNIQUE (student_id, course_id)
-- (needed when other tables reference an enrollment, e.g. submissions per enrollment).

-- Anti-pattern alternative: arrays/JSON of ids in a column (course_ids '10,11') - loses FKs and joins (Q141).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: comma-separated ids in a column
--    students(student_id, course_ids '10,11')  -> no FK, no integrity, LIKE '%10%' matches 110!
-- ❌ Wrong: junction table without a unique/PK pair -> duplicates; counts and grades become wrong.
-- ❌ Wrong: index only (student_id, course_id) and then query by course_id alone -> full scan.
-- ✅ PK (student_id, course_id) + secondary index (course_id, student_id).
-- ❌ Wrong: LEFT JOIN with COUNT(*) -> empty course shows 1; use COUNT(e.student_id) (as above, 0 for Compilers).
-- ❌ Wrong: putting grade on students or courses - it belongs to the pair.
```

---

## 🎯 Interview Tip (1 line)
Say: "Junction table with a composite PK, FKs with deliberate cascade rules, a reverse-order index, and relationship attributes on the junction; I add a surrogate id only if other tables must reference the pair."

---

## 🔗 Related Questions
→ Q141 (Normal forms) | Q144 (Polymorphic associations) | Q147 (Multi-tenancy patterns) | Q145 (Soft delete)
