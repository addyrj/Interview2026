# 29. Composite Indexes
# हिंदी में: Composite Index — एक से ज़्यादा columns पर बना index; columns का क्रम (order) सबसे ज़रूरी होता है

---

## 🔵 Simple Definition (English)
A **composite (multi-column) index** is an index on **two or more columns together**, e.g. `(user_id, status, created_at)`. Rows are sorted by the first column, then by the second within it, and so on, like a phone book sorted by surname, then first name.
It can only be used efficiently from the **leftmost columns** onward (the **leftmost-prefix rule**).

## 🔵 सरल परिभाषा (Hindi)
Composite index कई columns पर एक साथ बनता है — पहले column से sort, फिर उसके अंदर दूसरे column से।
जैसे टेलीफ़ोन डायरेक्टरी: पहले surname, फिर नाम। इसलिए यह index बाईं तरफ़ (पहले column) से शुरू होने वाली query में ही काम आता है।

---

## 🔴 Problem it Solves
Real queries combine filters and sorting:
```sql
SELECT * FROM orders WHERE user_id = 42 AND status = 'DELIVERED' ORDER BY created_at DESC LIMIT 20;
```
With only single-column indexes:
- An index on `user_id` finds 5,000 of the user's orders, then the DB **filters** status and **sorts** them in memory.
- Separate indexes on `user_id` and `status` → the DB may combine them (bitmap AND), but that's still slower and can't avoid the sort.

A composite index `(user_id, status, created_at DESC)` jumps **directly** to the 20 needed rows, already sorted. No filter, no sort.

## 🔴 यह क्यों बना? (Hindi)
असली queries में कई शर्तें और sorting होती है। अलग-अलग single-column index से DB को बहुत सारी rows निकालकर बाद में filter और sort करना पड़ता है।
सही क्रम वाला composite index सीधे उन्हीं 20 rows पर पहुँचता है, वो भी पहले से sorted।

---

## 🟢 How it Works — Step by Step

### How data is ordered in index (user_id, status, created_at)

```
(user_id, status,      created_at)
(41,      DELIVERED,   2024-09-01)
(42,      CANCELLED,   2024-08-10)
(42,      DELIVERED,   2024-07-01)
(42,      DELIVERED,   2024-09-15)   ┐
(42,      DELIVERED,   2024-10-02)   ┘ ← WHERE user_id=42 AND status='DELIVERED' → contiguous block,
(42,      PLACED,      2024-10-03)       already ordered by created_at
(43,      DELIVERED,   2024-06-11)
```

### Leftmost-prefix rule

```
Index: (A, B, C)

Query uses                          Index used?
──────────────────────────────────  ────────────────────────────────────────
WHERE A = ?                         ✅ yes
WHERE A = ? AND B = ?               ✅ yes
WHERE A = ? AND B = ? AND C = ?     ✅ yes (fully)
WHERE A = ? ORDER BY B              ✅ yes (no sort)
WHERE A = ? AND C = ?               ⚠️ partly (A used; C filtered after)
WHERE B = ?                         ❌ no  (doesn't start with A)
WHERE B = ? AND C = ?               ❌ no
WHERE A > ? AND B = ?               ⚠️ A range used, B can't narrow (range stops the prefix)

Phone book analogy: sorted by (surname, firstname). You can find "Sharma", or "Sharma, Riya",
but NOT everyone named "Riya" without reading the whole book.
(Postgres 18 / some DBs can do "skip scan" in limited cases, but don't rely on it.)
```

### Choosing column order — the ESR rule

```
E — Equality columns first      (user_id = ?, status = ?)
S — Sort columns next           (ORDER BY created_at)
R — Range columns last          (price BETWEEN ?, created_at > ?)

Query: WHERE restaurant_id = ? AND is_veg = true AND price < 300 ORDER BY rating DESC
Good:  (restaurant_id, is_veg, rating DESC)            -- equality, equality, sort; price filtered
       or (restaurant_id, is_veg, price) if price filter is very selective
Bad:   (price, restaurant_id, ...)   -- range first kills the rest of the index
```

### Selectivity also matters — but ESR usually wins
```
Put the column you ALWAYS filter on first (often tenant_id / user_id).
High-cardinality equality columns first narrow fastest.
One composite index can replace several single ones:
  (user_id, created_at) also serves "WHERE user_id = ?"  → drop the separate user_id index.
```

### Sort direction
```
Index (user_id, created_at DESC) serves:
  ORDER BY created_at DESC   ✅  (and ASC too, by scanning backwards)
Mixed directions need matching index:
  ORDER BY status ASC, created_at DESC  → index (status ASC, created_at DESC)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Index पहले column से sort होता है, फिर उसके अंदर दूसरे से, फिर तीसरे से।
2. Leftmost-prefix नियम: query में पहला column होना चाहिए, तभी index काम करेगा — `(A,B,C)` index सिर्फ़ B पर काम नहीं करेगा।
3. ESR नियम: पहले Equality (`=`) वाले columns, फिर Sort (ORDER BY), आख़िर में Range (`>`, `<`, BETWEEN)।
4. Range वाला column बीच में आया तो उसके बाद के columns से फ़ायदा नहीं मिलता।
5. एक अच्छा composite index कई single-column indexes की जगह ले सकता है।

---

## 🟡 Real World Example

**Multi-tenant SaaS (e.g. Freshworks, Zoho, Shopify)** — almost every index starts with `tenant_id` / `shop_id`: `(shop_id, created_at)`, `(shop_id, status, updated_at)`. Every query is scoped to a tenant, and this keeps each tenant's data contiguous in the index.

**Swiggy restaurant listing** — a query like "open restaurants in this city/zone, sorted by rating" is backed by an index like `(zone_id, is_open, rating DESC)`, or in the search engine with equivalent sort keys.

**Gmail-like inbox** — `(user_id, label, received_at DESC)` serves "latest 50 emails in Inbox" instantly, no matter how many million emails the user has.

## 🟡 Real Example Hindi में
SaaS कंपनियों (Zoho, Freshworks, Shopify) में लगभग हर index `tenant_id` से शुरू होता है, क्योंकि हर query किसी एक ग्राहक (tenant) के डेटा पर होती है।
Gmail जैसे inbox में `(user_id, label, received_at DESC)` index से "Inbox के latest 50 मेल" तुरंत आ जाते हैं, चाहे लाखों मेल हों।

---

## 🟠 My Stack Example

### Design indexes from your actual queries
```sql
-- Q1: My orders screen (RN app)
SELECT id, total, status, created_at FROM orders
WHERE user_id = $1 ORDER BY created_at DESC LIMIT 20;
-- Q2: My delivered orders
SELECT ... WHERE user_id = $1 AND status = 'DELIVERED' ORDER BY created_at DESC LIMIT 20;
-- Q3: Admin: all pending orders in a city, oldest first
SELECT ... WHERE city_id = $1 AND status = 'PENDING' ORDER BY created_at ASC LIMIT 100;

-- Indexes:
CREATE INDEX CONCURRENTLY idx_orders_user_created         ON orders (user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_orders_user_status_created  ON orders (user_id, status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_orders_city_status_created  ON orders (city_id, status, created_at);
-- Note: idx_orders_user_status_created could also serve Q1? NO — Q1 has no status filter,
-- so (user_id, status, created_at) would need a sort. Keep both, or accept the sort if few rows per user.
```

### Covering composite index (index-only scan)
```sql
CREATE INDEX CONCURRENTLY idx_orders_user_created_cover
  ON orders (user_id, created_at DESC) INCLUDE (total, status);
-- Q1 now never touches the table heap.
```

### Cursor pagination works perfectly with composite indexes
```sql
-- next page after (created_at, id) of last row
SELECT id, total, created_at FROM orders
WHERE user_id = $1 AND (created_at, id) < ($2, $3)
ORDER BY created_at DESC, id DESC LIMIT 20;
-- index: (user_id, created_at DESC, id DESC)
```

### Verify
```sql
EXPLAIN ANALYZE SELECT ... ;
-- Look for: "Index Scan using idx_orders_user_status_created" and NO "Sort" node.
-- If you see "Sort" + "Index Scan" → order of columns doesn't match ORDER BY.
```

### MongoDB — same rules (ESR is literally MongoDB's documented rule)
```js
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 });
db.orders.find({ userId: 42, status: 'DELIVERED' }).sort({ createdAt: -1 }).limit(20);
```

### Prisma
```prisma
model Order {
  @@index([userId, status, createdAt(sort: Desc)])
  @@index([cityId, status, createdAt])
}
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a composite index and the leftmost-prefix rule?**
A1: An index on multiple columns, ordered by the first column, then the second within it, and so on. The DB can use it for queries that filter on a leftmost prefix of its columns: (A), (A,B) or (A,B,C) for index (A,B,C). It can't use it efficiently for queries on B or C alone, because those values are scattered across the index.

**Q2: How do you decide the order of columns in a composite index?**
A2: Follow ESR: equality-filtered columns first, then the columns used for sorting, then range-filtered columns. Among equality columns, put the one that's always present (tenant_id/user_id) first. Range predicates stop further index narrowing, so put them last. Validate with EXPLAIN ANALYZE that there's no extra sort and few rows are filtered.

**Q3: Is a composite index (A, B) the same as two indexes on A and B?**
A3: No. Two single indexes can sometimes be combined (bitmap AND/OR), but that's less efficient and can't provide ordered results across both. A composite index (A, B) serves `A=? AND B=?` and `A=? ORDER BY B` directly. It also serves queries on A alone, so a separate index on A becomes redundant, but it doesn't help queries on B alone.

**Q4: Given `WHERE status = 'PAID' AND created_at > now() - interval '1 day' ORDER BY created_at`, what index?**
A4: `(status, created_at)`: equality on status first, then created_at, which serves both the range and the sort. If `status='PAID'` covers most rows and you mostly query recent data, consider a partial index `ON orders(created_at) WHERE status='PAID'`, which is smaller and faster.

**Q5: Too many composite indexes — what's the risk and how do you consolidate?**
A5: Each extra index slows writes and uses memory, and overlapping ones like (user_id), (user_id, created_at) and (user_id, status, created_at) are often redundant. Consolidate by keeping indexes whose prefixes serve multiple queries, removing ones that are prefixes of others, and checking `pg_stat_user_indexes` for unused ones. Weigh read gains against write costs on hot tables.

---

## 🔷 Trade-offs
✅ Advantages:
- One index can satisfy filter + sort (no in-memory sort), huge speedups.
- Can replace multiple single-column indexes; enables index-only scans with INCLUDE.

❌ Disadvantages:
- Only useful for leftmost-prefix queries — wrong order = useless index.
- Wider indexes = bigger, slower writes.
- Many query shapes may need several composites → write cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Composite index | Index on multiple columns | कई columns का index |
| Leftmost prefix | Must use first column(s) | पहला column ज़रूरी |
| ESR rule | Equality → Sort → Range order | पहले बराबरी, फिर sort, फिर range |
| Covering index | Includes all needed columns | सारा डेटा index में |
| Cardinality | Number of distinct values | अलग-अलग values की संख्या |
| Index-only scan | Answer from index alone | सिर्फ़ index से जवाब |
| Bitmap AND | Combining two indexes | दो index मिलाना |

---

## ⚡ 3-Line Summary
**English:**
1. A composite index sorts by col1, then col2, then col3 — usable only from the leftmost columns.
2. Order columns as Equality → Sort → Range; put tenant/user id first.
3. One good composite can serve filter + sort + cursor pagination; verify with EXPLAIN (no Sort node).

**Hindi:**
1. Composite index पहले col1, फिर col2 से sort — बाईं तरफ़ से शुरू होने वाली query में ही काम।
2. क्रम: Equality → Sort → Range; user/tenant id सबसे पहले।
3. एक अच्छा composite index filter + sort + pagination सब संभाल लेता है; EXPLAIN से जाँचो।

---

## ➡️ Next Topic Suggestion
**30. Query Optimization + EXPLAIN** — You know how indexes work. Next: how to read EXPLAIN ANALYZE output, find slow queries in production, and fix N+1 queries, bad joins and over-fetching.
