# 32. Denormalization
# हिंदी में: Denormalization — तेज़ पढ़ने (fast reads) के लिए जानबूझकर डेटा को कई जगह दोहराना, ताकि joins कम हों

---

## 🔵 Simple Definition (English)
**Denormalization** means **intentionally adding redundant data** (copies, precomputed values, embedded objects) to a schema to make **reads faster**, avoiding expensive joins and aggregations. You trade **write complexity and possible inconsistency** for **read speed**.

## 🔵 सरल परिभाषा (Hindi)
Denormalization यानी जानबूझकर डेटा को दोहराना — जैसे post में like count रख देना या order में restaurant का नाम — ताकि पढ़ते समय join और गिनती न करनी पड़े।
पढ़ना तेज़ होता है, पर लिखते समय सारी copies अपडेट रखनी पड़ती हैं।

---

## 🔴 Problem it Solves
A perfectly normalized schema can be **slow for read-heavy screens at scale**:
- Instagram post card: post + author name/avatar + like count + comment count + "liked by you?" → 5 joins and 2 `COUNT(*)`s **per post**, × 20 posts, × millions of users.
- `SELECT COUNT(*) FROM likes WHERE post_id = ?` on a post with 10 million likes is slow every time.
- Dashboards aggregating millions of rows on every page load.

Reads usually outnumber writes 100:1 or more. Paying a bit more on write to make reads cheap is often the right deal.

## 🔴 यह क्यों बना? (Hindi)
Instagram की हर post के लिए 5 joins और like/comment की गिनती — करोड़ों यूज़र्स के लिए बहुत धीमा है।
पढ़ना लिखने से 100 गुना ज़्यादा होता है, इसलिए लिखते समय थोड़ा ज़्यादा काम करके पढ़ना सस्ता बनाना फ़ायदेमंद है।

---

## 🟢 How it Works — Step by Step

### Common denormalization techniques

```
1. Counter columns (precomputed aggregates)
   posts.like_count, posts.comment_count, restaurants.rating_avg, rating_count
   → update on each like (or async), read without COUNT(*)

2. Duplicated columns (avoid a join)
   orders.restaurant_name, orders.customer_phone
   comments.author_name, author_avatar_url

3. Embedded documents (NoSQL)
   restaurant { menu: [...] }, post { latest_comments: [3 items] }

4. Precomputed / materialized read models
   user_feed table (user_id, post_id, created_at)  — fan-out on write (Twitter timeline)
   daily_sales_summary(restaurant_id, day, revenue, orders)
   materialized views

5. Summary tables / rollups for analytics
   events → hourly_rollups → daily_rollups

6. Search/read stores
   Elasticsearch document = joined view of restaurant + cuisines + rating + location
```

### Normalized vs denormalized read

```
NORMALIZED (5 joins + counts per post)
SELECT p.*, u.name, u.avatar,
       (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS likes,
       (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comments
FROM posts p JOIN users u ON u.id = p.author_id WHERE p.id = ANY($1);

DENORMALIZED (single table read)
SELECT id, caption, author_name, author_avatar, like_count, comment_count
FROM posts WHERE id = ANY($1);
```

### Keeping copies in sync — the real challenge

```
┌───────────────────────────┬───────────────────────────────┬─────────────────────────────┐
│ Method                    │ How                           │ Consistency                 │
├───────────────────────────┼───────────────────────────────┼─────────────────────────────┤
│ Same transaction          │ INSERT like + UPDATE count    │ Strong (but hot row locks!) │
│ DB trigger                │ trigger updates count         │ Strong, hidden logic        │
│ Async event / queue       │ "LikeAdded" → worker updates  │ Eventual (seconds)          │
│ CDC (Debezium → Kafka)    │ stream DB changes to read     │ Eventual, reliable          │
│                           │ models / Elasticsearch        │                             │
│ Materialized view refresh │ REFRESH every N minutes       │ Stale up to N min           │
│ Periodic reconciliation   │ nightly job recomputes counts │ Fixes drift                 │
└───────────────────────────┴───────────────────────────────┴─────────────────────────────┘
```

### Hot counter problem

```
Viral post: 50,000 likes/second → UPDATE posts SET like_count = like_count + 1 WHERE id = 7
→ all writes fight for ONE row lock → DB melts.
Fixes:
  - Count in Redis (INCR) → flush to DB every few seconds
  - Sharded counters: 10 rows per post, increment a random one, sum on read
  - Approximate counts ("1.2M likes") — exact number not needed
```

### When to denormalize — decision

```
✅ Read-heavy, latency-sensitive path (feeds, product listing, home screens)
✅ Expensive aggregate computed often (counts, ratings, totals)
✅ Data rarely changes (author name) or staleness is acceptable
✅ NoSQL / document modeling around access patterns
❌ Financial balances & critical integrity → keep normalized + transactions
❌ Data changes very frequently AND must be exactly consistent everywhere
Rule: Normalize first, measure, denormalize the specific hot path, document the sync strategy.
```

## 🟢 कैसे काम करता है? (Hindi)
1. आम तरीके: count columns (like_count), दूसरी टेबल का डेटा कॉपी करना (author_name), embedded documents, पहले से बनी feed टेबल।
2. पढ़ते समय एक ही टेबल से सब मिल जाता है — कोई join या COUNT नहीं।
3. मुश्किल: copies को sync रखना — एक ही transaction, trigger, async event/queue, या CDC से।
4. वायरल post पर एक ही row पर लाखों updates → Redis counter या sharded counters इस्तेमाल करो।
5. नियम: पहले normalize, फिर नापो, फिर सिर्फ़ धीमे हिस्से को denormalize करो। पैसे का डेटा denormalize मत करो।

---

## 🟡 Real World Example

**Twitter/X home timeline** — instead of a join across "people you follow" on every load, each new tweet is fanned out into each follower's precomputed timeline list (in Redis). Reads are a single list read. Celebrity accounts with millions of followers are handled differently: their tweets are merged in at read time.

**Instagram like counts** — counters are stored denormalized and updated asynchronously. During huge spikes counts may lag a little, which is acceptable. Instagram described the "Justin Bieber problem": one celebrity post receiving massive likes created hot-row contention, solved with denormalized counters and caching.

**Amazon product page** — the product detail service serves a precomputed document (title, price, ratings summary, images, seller info) assembled from many services. The rating average is precomputed, not calculated on each view.

**YouTube view counts** — famously "stuck at 301" in early days while views were verified and aggregated asynchronously. That's denormalized counting with eventual consistency.

## 🟡 Real Example Hindi में
Twitter हर tweet को followers की पहले से बनी timeline में डाल देता है — खोलते ही सीधी लिस्ट मिलती है, join नहीं। करोड़ों followers वाले celebrities के tweet पढ़ते समय जोड़े जाते हैं।
YouTube पर पहले views "301" पर अटक जाते थे — गिनती बाद में async तरीके से होती थी। यही denormalized counter है।

---

## 🟠 My Stack Example

### Counter in same transaction (fine for low/moderate traffic)
```sql
-- Increment only if the like was actually new (CTE returns a row only on real insert)
WITH ins AS (
  INSERT INTO likes(user_id, post_id) VALUES ($1, $2)
  ON CONFLICT DO NOTHING
  RETURNING post_id
)
UPDATE posts SET like_count = like_count + 1
WHERE id IN (SELECT post_id FROM ins);
-- one statement = one implicit transaction; double-taps never double count
```

### High-traffic counter with Redis + periodic flush (Node)
```js
// on like
await db.query('INSERT INTO likes(user_id, post_id) VALUES ($1,$2) ON CONFLICT DO NOTHING', [uid, pid]);
await redis.hIncrBy('post_like_delta', String(pid), 1);

// worker every 5 seconds
setInterval(async () => {
  const deltas = await redis.hGetAll('post_like_delta');
  await redis.del('post_like_delta');           // (use a rename/lua for atomicity in prod)
  for (const [pid, d] of Object.entries(deltas))
    await db.query('UPDATE posts SET like_count = like_count + $1 WHERE id = $2', [Number(d), pid]);
}, 5000);
```

### Duplicate display fields + update on change (event-driven)
```js
// comments store author_name/avatar for fast feed rendering
// when a user updates profile → publish event → worker updates their comments (async, eventual)
bus.on('user.profile_updated', async ({ userId, name, avatar }) => {
  await db.query('UPDATE comments SET author_name=$1, author_avatar=$2 WHERE author_id=$3', [name, avatar, userId]);
});
```

### Materialized view for a dashboard (FastAPI reads it)
```sql
CREATE MATERIALIZED VIEW restaurant_stats AS
SELECT r.id, r.name, COUNT(o.id) AS orders_30d, AVG(rv.rating) AS rating_avg
FROM restaurants r
LEFT JOIN orders o ON o.restaurant_id = r.id AND o.created_at > now() - interval '30 days'
LEFT JOIN reviews rv ON rv.restaurant_id = r.id
GROUP BY r.id, r.name;
CREATE UNIQUE INDEX ON restaurant_stats(id);
-- cron: REFRESH MATERIALIZED VIEW CONCURRENTLY restaurant_stats;
```

### MongoDB: embed a summary + reference the full list
```js
{
  _id: 'post_7', caption: '...', author: { id: 42, name: 'Aditya', avatar: '...' },  // denormalized
  likeCount: 12890, commentCount: 341,                                              // counters
  latestComments: [ { user: 'Riya', text: '🔥' }, { user: 'Karan', text: 'nice' } ]  // bounded embed
}
// full comments live in a separate `comments` collection
```

### Nightly reconciliation (fix drift)
```sql
UPDATE posts p SET like_count = s.cnt
FROM (SELECT post_id, COUNT(*) cnt FROM likes GROUP BY post_id) s
WHERE s.post_id = p.id AND p.like_count <> s.cnt;
```

---

## ⚫ Interview Questions + Answers

**Q1: What is denormalization and when would you use it?**
A1: Intentionally storing redundant or precomputed data to speed up reads by avoiding joins and aggregations at query time. Use it on read-heavy, latency-sensitive paths (feeds, listings, product pages, dashboards), for frequently computed aggregates (counts, ratings), and in NoSQL designs modeled around access patterns. Normalize first, then denormalize where measurements show a need.

**Q2: How do you keep denormalized data consistent?**
A2: Options, from strongest to weakest: update the copy in the same DB transaction, or with triggers (strong but adds write latency and lock contention); publish domain events or use CDC (Debezium/Kafka) to update read models asynchronously (eventual, scalable); periodically refresh materialized views; and run reconciliation jobs that recompute and fix drift. Make updates idempotent and decide explicitly how much staleness each field can tolerate.

**Q3: How would you implement a like counter for a post that may go viral?**
A3: Store likes as rows (user_id, post_id, unique) for correctness. Don't increment one DB row synchronously at high volume, because hot-row lock contention will hurt. Instead increment in Redis (INCR/HINCRBY) and flush deltas to the DB periodically, or use sharded counters (N counter rows per post, sum on read). Show approximate counts, cache the count in the post object, and reconcile periodically from the source rows.

**Q4: What's the difference between denormalization and caching?**
A4: Both trade freshness for speed. Denormalization changes the data model: redundant data lives in the database itself as persistent columns, tables or views, maintained on writes. Caching keeps temporary copies in a separate fast layer (Redis, CDN) with TTL and invalidation, and can be thrown away and rebuilt. Denormalized data is often part of the source of truth's read path. A cache is purely an optimization.

**Q5: What are the risks of denormalization?**
A5: Data inconsistency if sync fails or is forgotten, more complex and slower writes, more storage, write amplification, and hot-row contention for counters. Logic gets spread across triggers, events and jobs, which makes the system harder to reason about. Mitigate by documenting the owner and source of truth for each field, using idempotent async updates with retries/DLQ, and adding reconciliation and monitoring for drift.

---

## 🔷 Trade-offs
✅ Advantages:
- Much faster reads, fewer joins, simpler read queries, scales read-heavy workloads.

❌ Disadvantages:
- Redundant storage; write amplification; sync logic; possible stale/inconsistent data.
- Harder schema evolution (change name in N places).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Denormalization | Adding redundancy for faster reads | तेज़ पढ़ने के लिए दोहराव |
| Counter cache | Stored precomputed count | पहले से गिनी हुई संख्या |
| Read model | Data shaped for a specific read | ख़ास पढ़ने के लिए डेटा |
| Fan-out on write | Push data to all readers' lists at write time | लिखते समय सबकी लिस्ट में डालना |
| Materialized view | Stored query result | सेव किया query नतीजा |
| Write amplification | One write causes many writes | एक लिखने से कई लिखना |
| Reconciliation | Recompute to fix drift | गड़बड़ी ठीक करने के लिए दोबारा गिनना |
| Hot row | Row updated extremely often | बहुत ज़्यादा अपडेट होने वाली row |

---

## ⚡ 3-Line Summary
**English:**
1. Denormalization duplicates or precomputes data (counters, copied fields, feeds, views) to make reads fast.
2. The cost is write complexity and possible inconsistency — sync via transactions, events/CDC, view refresh, reconciliation.
3. Normalize first, denormalize measured hot paths, never compromise critical financial integrity.

**Hindi:**
1. Denormalization = पढ़ना तेज़ करने के लिए डेटा दोहराना या पहले से गिनना।
2. क़ीमत: लिखना मुश्किल और डेटा कभी-कभी पुराना — events, CDC, reconciliation से sync रखो।
3. पहले normalize, फिर सिर्फ़ धीमे हिस्से को denormalize; पैसे के डेटा से समझौता नहीं।

---

## ➡️ Next Topic Suggestion
**33. Transactions** — Keeping data consistent across multiple writes needs transactions. Next: what a transaction is, BEGIN/COMMIT/ROLLBACK, savepoints, and how to use them correctly in Node and FastAPI.
