---

# Q077. Mode (Most Frequent Value)
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL `MODE()`) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Find the most frequent ticket category overall and the most frequent agent per category. How do you handle ties?

---

## 💡 Quick Concept (2 lines only)
Mode = value with the highest COUNT. Use GROUP BY + COUNT then take the top (LIMIT 1 / RANK = 1). PostgreSQL also has MODE() WITHIN GROUP; MySQL does not.
हिंदी: Mode = सबसे ज्यादा बार आने वाली value; COUNT से group करके top वाली लो, ties के लिए RANK use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE support_tickets (
  id       INT PRIMARY KEY,
  category VARCHAR(30),
  agent    VARCHAR(30)
);

INSERT INTO support_tickets VALUES
 (1,'Billing','Asha'),(2,'Billing','Bilal'),(3,'Billing','Asha'),(4,'Billing','Chitra'),
 (5,'Login','Dev'),(6,'Login','Dev'),(7,'Login','Esha'),(8,'Login','Esha'),(9,'Login','Farhan'),
 (10,'Shipping','Gita');

-- ============================================
-- SOLUTION
-- ============================================

-- Overall mode, ties included (RANK keeps all winners)
SELECT category AS mode_category, cnt
FROM (SELECT category, COUNT(*) AS cnt, RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
      FROM support_tickets GROUP BY category) t
WHERE rnk = 1;
-- mode_category | cnt
-- Login         | 5

-- Mode agent per category, ALL tied winners
SELECT category, agent AS mode_agent, cnt
FROM (SELECT category, agent, COUNT(*) AS cnt,
             RANK() OVER (PARTITION BY category ORDER BY COUNT(*) DESC) AS rnk
      FROM support_tickets GROUP BY category, agent) t
WHERE rnk = 1 ORDER BY category, agent;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- category | mode_agent | cnt
-- ---------+------------+----
-- Billing  | Asha       | 2
-- Login    | Dev        | 2     <- tie: Dev and Esha both have 2
-- Login    | Esha       | 2
-- Shipping | Gita       | 1
```

---

## 🔍 Why This Works (3 lines max)
GROUP BY counts each value, and RANK() over those counts gives every top-count value rank 1, so ties are kept. A window over an aggregate (RANK() OVER (ORDER BY COUNT(*))) is legal because windows run after grouping.
हिंदी: GROUP BY से count, फिर RANK() से top count वाली सारी values (ties सहित) मिलती हैं।

---

## ⚡ Alternative Solution

```sql
-- Exactly one mode per group (deterministic tiebreaker): ROW_NUMBER
SELECT category, agent AS one_mode_agent, cnt FROM (
  SELECT category, agent, COUNT(*) AS cnt,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY COUNT(*) DESC, agent) AS rn
  FROM support_tickets GROUP BY category, agent) t
WHERE rn = 1 ORDER BY category;
-- Billing Asha 2 | Login Dev 2 | Shipping Gita 1

-- Overall single mode, simplest (ties: arbitrary row)
SELECT category, COUNT(*) AS cnt FROM support_tickets GROUP BY category ORDER BY cnt DESC LIMIT 1;
-- Login | 5

-- PostgreSQL only: built-in aggregate (returns ONE value; on ties picks the first in sort order)
SELECT category, MODE() WITHIN GROUP (ORDER BY agent) AS mode_agent
FROM support_tickets GROUP BY category ORDER BY category;
-- Billing Asha | Login Dev | Shipping Gita      (verified in PGlite; no Esha for the tie)
-- MySQL 9.1: MODE() WITHIN GROUP -> ERROR 1064 syntax error (verified)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ORDER BY ... LIMIT 1 silently drops tied modes (Login would show only one agent)
-- ❌ Wrong: HAVING COUNT(*) = MAX(COUNT(*)) -- nested aggregates are not allowed
-- ✅ Correct: HAVING COUNT(*) = (SELECT MAX(c) FROM (SELECT COUNT(*) c FROM ... GROUP BY ...) x)
SELECT agent, COUNT(*) AS cnt FROM support_tickets GROUP BY agent
HAVING COUNT(*) = (SELECT MAX(c) FROM (SELECT COUNT(*) AS c FROM support_tickets GROUP BY agent) x)
ORDER BY agent;
-- Asha 2 | Dev 2 | Esha 2   (verified, both engines)
```

---

## 🎯 Interview Tip (1 line)
Say: "Mode is GROUP BY + COUNT with RANK = 1 to keep ties (or ROW_NUMBER with a tiebreaker for exactly one); PostgreSQL's MODE() is handy but returns a single value, and MySQL has no equivalent."

---

## 🔗 Related Questions
→ Q062 (COUNT) | Q075 (top N per group) | Q076 (median) | Q066 (RANK)
