---

# Q211. Consistent Hashing for Sharding
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (8.0+ for CTE); PostgreSQL variant shown

---

## ❓ Question
Why does `hash(key) % N` cause massive data movement when you add a shard, and how does consistent hashing (hash ring with virtual nodes) fix it? Demonstrate with SQL.

---

## 💡 Quick Concept (2 lines only)
Place shards (many virtual nodes each) on a hash ring; a key belongs to the first node clockwise from its hash. Adding a node only steals keys from its neighbours (about 1/N of data).
हिंदी: Shards को hash ring पर रखो; key अपने clockwise अगले node की होती है। नया node जोड़ने पर सिर्फ ~1/N keys हिलती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run on MySQL 9.1.0)
-- ============================================
CREATE TABLE ring (
  node  VARCHAR(10),
  vnode INT,
  pos   BIGINT UNSIGNED,           -- position on ring = CRC32(...) in 0..2^32-1
  KEY (pos)
);

-- 3 physical shards x 50 virtual nodes each
INSERT INTO ring
WITH RECURSIVE v(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM v WHERE i < 49)
SELECT n.node, v.i, CRC32(CONCAT(n.node, '#', v.i))
FROM (SELECT 'shardA' AS node UNION ALL SELECT 'shardB' UNION ALL SELECT 'shardC') n
CROSS JOIN v;

CREATE TABLE user_keys (k VARCHAR(20) PRIMARY KEY);
INSERT INTO user_keys
WITH RECURSIVE s(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM s WHERE i < 1000)
SELECT CONCAT('user:', i) FROM s;

-- ============================================
-- SOLUTION: owner = first ring position >= hash(key), wrap to smallest
-- ============================================
CREATE VIEW key_owner AS
SELECT k.k,
       COALESCE(
         (SELECT r.node FROM ring r WHERE r.pos >= CRC32(k.k) ORDER BY r.pos LIMIT 1),
         (SELECT r.node FROM ring r ORDER BY r.pos LIMIT 1)      -- wrap-around
       ) AS node
FROM user_keys k;

CREATE TABLE owner_before AS SELECT * FROM key_owner;   -- snapshot

SELECT node, COUNT(*) AS keys_cnt FROM owner_before GROUP BY node ORDER BY node;
-- node   | keys_cnt
-- shardA | 398
-- shardB | 422
-- shardC | 180      <- uneven with only 50 vnodes; use 100-256 for tighter balance

-- Add a 4th shard
INSERT INTO ring
WITH RECURSIVE v(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM v WHERE i < 49)
SELECT 'shardD', i, CRC32(CONCAT('shardD#', i)) FROM v;

SELECT o.node AS owner_before, n.node AS owner_after, COUNT(*) AS keys_cnt
FROM owner_before o JOIN key_owner n USING (k)
GROUP BY 1, 2 ORDER BY 1, 2;
-- owner_before | owner_after | keys_cnt
-- shardA       | shardA      | 318
-- shardA       | shardD      | 80
-- shardB       | shardB      | 329
-- shardB       | shardD      | 93
-- shardC       | shardC      | 138
-- shardC       | shardD      | 42
-- Every moved key goes ONLY to the new shard D; nothing shuffles among A/B/C.

SELECT SUM(o.node <> n.node) AS moved, COUNT(*) AS total
FROM owner_before o JOIN key_owner n USING (k);
-- moved | total
-- 215   | 1000     (21.5%, close to the ideal 1/4)

-- Compare with naive modulo going 3 -> 4 shards:
SELECT SUM(CRC32(k) % 3 <> CRC32(k) % 4) AS moved_mod, COUNT(*) AS total FROM user_keys;
-- moved_mod | total
-- 752       | 1000     (75% of data moves!)
```

PostgreSQL: same logic works; use `hashtext(k)::bigint & 4294967295` (or `('x'||substr(md5(k),1,8))::bit(32)::bigint`) instead of CRC32, and `WITH RECURSIVE` / `generate_series(0,49)` for vnodes. Not run on PGlite; MySQL was the executed engine.

---

## 🔍 Why This Works (3 lines max)
Node positions do not depend on the node count, so adding a node only claims the arcs just before its vnodes. Virtual nodes smooth the distribution and let you weight bigger servers with more vnodes.
हिंदी: Node की position count पर निर्भर नहीं, इसलिए नया node सिर्फ अपने पास की arcs लेता है; vnodes से load बराबर रहता है।

---

## ⚡ Alternative Solution

```sql
-- Fixed virtual shards (Vitess / Redis Cluster style): 1024 logical shards, fixed forever;
-- only the shard -> server mapping changes. Simpler to reason about than a ring.
CREATE TABLE vshard_map (vshard INT PRIMARY KEY, server VARCHAR(20));
-- vshard = CRC32(user_id) % 1024 ; look up server in vshard_map
-- Rebalancing = move some vshards to a new server, copy their rows, flip map.

-- Rendezvous (HRW) hashing: owner = node with the max hash(node, key); no ring structure.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ One point per physical node on the ring -> wildly uneven (shardC got 180 above
--    even with 50 vnodes; with 1 point it can be 80/10/10).
-- ❌ Using a non-uniform hash or changing the hash function later -> every key moves.
-- ❌ Forgetting that moving the arc requires actually copying data and dual-writing;
--    the hash tells WHO owns a key, not HOW to migrate it.
-- ✅ Use 100+ vnodes, a stable hash (murmur3/xxhash/CRC32), and a staged migration.
```

---

## 🎯 Interview Tip (1 line)
Say: "Modulo sharding reshuffles about (N-1)/N of keys on resize; consistent hashing with virtual nodes moves only about 1/N, which I measured at 21.5% versus 75%, but in databases I prefer a fixed set of many virtual shards with a mapping table because it makes migrations explicit and resumable."

---

## 🔗 Related Questions
→ Q210 (shard key selection) | Q212 (cross-shard queries) | Q213 (Vitess) | Q214 (Citus)
