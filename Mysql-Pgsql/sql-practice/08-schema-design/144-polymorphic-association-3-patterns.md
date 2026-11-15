---

# Q144. Polymorphic Association — 3 Patterns
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0.16+ for enforced CHECK | PostgreSQL) — all three patterns run on MySQL 9.1.0 and PGlite

---

## ❓ Question
Comments can belong to a post OR a video (more types later). Design the schema in three ways: generic type+id columns, one nullable FK per parent type, and a shared supertype table. Compare integrity guarantees and query cost.

---

## 💡 Quick Concept (2 lines only)
A polymorphic association is one child table pointing at several parent tables. A generic (type, id) pair is flexible but cannot have a foreign key; per-type FKs or a supertype table keep real referential integrity.
हिंदी: Polymorphic association में एक child table कई parent tables को point करती है; (type, id) pair flexible है पर FK नहीं लग सकता, बाकी दो patterns में integrity बनी रहती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (shared parents)
-- ============================================

CREATE TABLE posts  (post_id  INT PRIMARY KEY, title VARCHAR(100));
CREATE TABLE videos (video_id INT PRIMARY KEY, title VARCHAR(100));
INSERT INTO posts  VALUES (1,'Intro to MVCC'), (2,'Indexing 101');
INSERT INTO videos VALUES (1,'Locking explained');

-- ============================================
-- PATTERN 1: generic type + id ("Rails-style")  - NO foreign key possible
-- ============================================

CREATE TABLE comments_generic (
  comment_id       INT PRIMARY KEY,
  commentable_type VARCHAR(20) NOT NULL,     -- 'post' | 'video'
  commentable_id   INT NOT NULL,
  body             VARCHAR(200)
);
INSERT INTO comments_generic VALUES
  (1,'post',1,'Nice post'),
  (2,'video',1,'Great video'),
  (3,'post',99,'Orphan - post 99 does not exist');   -- the DB happily accepts this!

-- Find orphans (you must police integrity yourself):
SELECT c.comment_id, c.commentable_type, c.body
FROM comments_generic c
LEFT JOIN posts  p ON c.commentable_type = 'post'  AND p.post_id  = c.commentable_id
LEFT JOIN videos v ON c.commentable_type = 'video' AND v.video_id = c.commentable_id
WHERE p.post_id IS NULL AND v.video_id IS NULL;
-- comment_id | commentable_type | body
-- 3          | post             | Orphan - post 99 does not exist      (real output)

-- ============================================
-- PATTERN 2: one nullable FK per parent + CHECK "exactly one"
-- ============================================

CREATE TABLE comments_fk (
  comment_id INT PRIMARY KEY,
  post_id    INT NULL,
  video_id   INT NULL,
  body       VARCHAR(200),
  FOREIGN KEY (post_id)  REFERENCES posts(post_id),
  FOREIGN KEY (video_id) REFERENCES videos(video_id),
  CONSTRAINT chk_one_parent CHECK (
    (post_id IS NOT NULL AND video_id IS NULL) OR
    (post_id IS NULL AND video_id IS NOT NULL)
  )
);
INSERT INTO comments_fk VALUES (1,1,NULL,'Nice post'), (2,NULL,1,'Great video');
INSERT INTO comments_fk VALUES (3,1,1,'Both parents');
-- MySQL: ERROR 3819 (HY000): Check constraint 'chk_one_parent' is violated.
-- PgSQL: ERROR: new row for relation "comments_fk" violates check constraint "chk_one_parent"

-- ============================================
-- PATTERN 3: supertype table (class-table inheritance)
-- ============================================

CREATE TABLE commentables (commentable_id INT PRIMARY KEY, kind VARCHAR(10) NOT NULL);
CREATE TABLE posts2  (post_id  INT PRIMARY KEY, title VARCHAR(100),
                      FOREIGN KEY (post_id)  REFERENCES commentables(commentable_id));
CREATE TABLE videos2 (video_id INT PRIMARY KEY, title VARCHAR(100),
                      FOREIGN KEY (video_id) REFERENCES commentables(commentable_id));
CREATE TABLE comments_super (
  comment_id     INT PRIMARY KEY,
  commentable_id INT NOT NULL,
  body           VARCHAR(200),
  FOREIGN KEY (commentable_id) REFERENCES commentables(commentable_id)
);
INSERT INTO commentables VALUES (1,'post'), (2,'post'), (3,'video');
INSERT INTO posts2  VALUES (1,'Intro to MVCC'), (2,'Indexing 101');
INSERT INTO videos2 VALUES (3,'Locking explained');
INSERT INTO comments_super VALUES (1,1,'Nice post'), (2,3,'Great video');

SELECT c.comment_id, c.body, COALESCE(p.title, v.title) AS parent_title
FROM comments_super c
LEFT JOIN posts2  p ON p.post_id  = c.commentable_id
LEFT JOIN videos2 v ON v.video_id = c.commentable_id
ORDER BY c.comment_id;

-- ============================================
-- EXPECTED OUTPUT (real; same on MySQL 9.1.0 and PGlite)
-- ============================================

-- comment_id | body        | parent_title
-- 1          | Nice post   | Intro to MVCC
-- 2          | Great video | Locking explained

INSERT INTO comments_super VALUES (3, 99, 'Orphan');
-- MySQL: ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails ...
-- PgSQL: ERROR: insert or update on table "comments_super" violates foreign key constraint "comments_super_commentable_id_fkey"
```

---

## 🔍 Why This Works (3 lines max)
Foreign keys can only reference one table, so integrity needs either one FK per parent (pattern 2) or a single common parent table (pattern 3); pattern 1 gives that up for flexibility. The CHECK in pattern 2 stops a comment from having two parents.
हिंदी: FK सिर्फ एक table को reference कर सकती है, इसलिए integrity के लिए हर parent का FK (pattern 2) या साझा supertype table (pattern 3) चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Comparison
-- Pattern 1 generic   : easiest to add types, NO FK/cascade, orphans possible, index (commentable_type, commentable_id)
-- Pattern 2 nullable FK: real FKs + CHECK; adding a type = ALTER TABLE add column + rewrite CHECK; sparse NULLs
--                        index each FK column; PgSQL partial index: CREATE INDEX ON comments_fk (post_id) WHERE post_id IS NOT NULL;
-- Pattern 3 supertype : cleanest integrity, one child column; cost = extra table + insert into supertype first

-- Pattern 4 (also common): separate child table per parent (post_comments, video_comments)
--   perfect FKs, but "all comments by user" needs UNION ALL (Q020).

-- PgSQL-only idea: table inheritance/partitioning - not recommended for this.
-- Rails/Django/Laravel use pattern 1 by default (GenericForeignKey, morphTo) - convenient, but know the trade-off.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: pattern 1 in a system that needs referential integrity / ON DELETE CASCADE
DELETE FROM posts WHERE post_id = 1;
-- comments_generic row 1 stays behind - orphaned forever, no error.
-- ✅ Use pattern 2 or 3, or add app-level deletion + a periodic orphan query (as shown).

-- ❌ Wrong: pattern 2 with no CHECK -> rows with two parents or none (we saw the CHECK reject it).
-- ❌ Wrong: MySQL < 8.0.16 silently IGNORES CHECK constraints - verify the version.
-- ❌ Wrong: forgetting that a LEFT JOIN per parent type widens every query as types grow.
```

---

## 🎯 Interview Tip (1 line)
Say: "I choose by integrity needs: generic type+id only when flexibility beats integrity and I can tolerate orphans; otherwise nullable FKs with a CHECK for a few stable types, or a supertype table when types keep growing."

---

## 🔗 Related Questions
→ Q143 (Many-to-many) | Q141 (Normal forms) | Q159 (CHECK constraints) | Q145 (Soft delete)
