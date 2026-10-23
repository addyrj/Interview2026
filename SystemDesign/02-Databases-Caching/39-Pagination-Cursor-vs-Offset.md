# 39. Pagination (Cursor vs Offset)
# हिंदी में: Pagination — बड़ी लिस्ट को छोटे-छोटे पन्नों (pages) में भेजना; Offset = "इतनी rows छोड़ो", Cursor = "इस आख़िरी item के बाद से दो"

---

## 🔵 Simple Definition (English)
**Pagination** returns a large result set in **small chunks (pages)** instead of all at once.
- **Offset pagination:** `LIMIT 20 OFFSET 40` means skip 40 rows and give the next 20 (page 3). Simple, supports "jump to page N".
- **Cursor (keyset) pagination:** "give me 20 items **after** this last item": `WHERE (created_at, id) < (:last_ts, :last_id) LIMIT 20`. Fast at any depth and stable when data changes. Ideal for feeds and infinite scroll.

## 🔵 सरल परिभाषा (Hindi)
Pagination यानी लाखों items एक साथ न भेजकर 20-20 के पन्नों में भेजना।
Offset: "पहले 40 छोड़ो, फिर 20 दो" — आसान, पर गहरे पन्नों पर धीमा। Cursor: "इस आख़िरी item के बाद के 20 दो" — हमेशा तेज़, infinite scroll के लिए सबसे अच्छा।

---

## 🔴 Problem it Solves
Returning all rows is impossible at scale: 2 million orders → huge DB load, a 500 MB response and a frozen mobile app.

But **offset pagination has two problems at scale**:
1. **Performance:** `OFFSET 1,000,000` makes the DB read and **discard** 1M rows on every request → slow, and gets slower with depth.
2. **Consistency:** new items inserted while the user scrolls **shift** the pages → the user sees **duplicates** or **misses** items.

Cursor pagination solves both by remembering **where you stopped**, not **how many to skip**.

## 🔴 यह क्यों बना? (Hindi)
लाखों rows एक साथ भेजना नामुमकिन है। Offset में दो दिक़्क़तें: `OFFSET 10 लाख` पर DB 10 लाख rows पढ़कर फेंकता है (धीमा), और scroll करते समय नए item आएँ तो पन्ने खिसक जाते हैं — duplicate या छूटे items।
Cursor "कहाँ रुके थे" याद रखता है, "कितने छोड़ने हैं" नहीं — इसलिए तेज़ भी और सही भी।

---

## 🟢 How it Works — Step by Step

### Offset pagination

```sql
-- page = 3, size = 20
SELECT id, title, created_at FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;
```
```
DB work: read rows 1..60, throw away 40, return 20
Page 1      → reads 20
Page 100    → reads 2,000
Page 50,000 → reads 1,000,000   ❌ seconds

Shifting problem:
  User loads page 1 (posts 1–20). 5 new posts are inserted at the top.
  User loads page 2 (OFFSET 20) → gets old posts 16–35 → posts 16–20 shown TWICE ❌
  (Deletes cause the opposite: items skipped.)
```

### Cursor (keyset) pagination

```sql
-- first page
SELECT id, title, created_at FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 21;                                    -- fetch 1 extra to know hasMore

-- next page: cursor = last item's (created_at, id)
SELECT id, title, created_at FROM posts
WHERE (created_at, id) < ($1, $2)            -- row-value comparison
ORDER BY created_at DESC, id DESC
LIMIT 21;
-- index: (created_at DESC, id DESC)  → DB seeks directly to the cursor position
```
```
DB work: index seek to cursor → read 21 rows. Same cost for page 1 and page 50,000 ✅
New posts inserted at top → don't affect "items after cursor" → no duplicates ✅
Tie-breaker (id) is REQUIRED: many rows can share the same created_at.
```

### The cursor is opaque to clients

```
Server encodes the position:  base64url(JSON {"t":"2024-10-01T10:00:00Z","id":9001})
Response:
{
  "data": [...20 items...],
  "pagination": { "nextCursor": "eyJ0IjoiMjAyNC0xMC0wMVQxMDowMDowMFoiLCJpZCI6OTAwMX0", "hasMore": true }
}
Client sends ?cursor=<that string> next time. Never parses it.
(Optionally sign it with HMAC so clients can't tamper.)
```

### Comparison

```
┌─────────────────────────┬────────────────────────────┬────────────────────────────────┐
│                         │ Offset                     │ Cursor / Keyset                │
├─────────────────────────┼────────────────────────────┼────────────────────────────────┤
│ Query                   │ LIMIT n OFFSET k           │ WHERE key < cursor LIMIT n     │
│ Deep page performance   │ O(offset) — degrades       │ O(log n) — constant            │
│ Stable under inserts    │ No (dupes/skips)           │ Yes                            │
│ Jump to page 57         │ Yes                        │ No (only next/prev)            │
│ Total pages / count     │ Easy-ish (COUNT(*) costly) │ Usually not shown              │
│ Sort by any column      │ Yes                        │ Needs index on sort key + tie  │
│ Best for                │ Admin tables, small data,  │ Feeds, infinite scroll, APIs,  │
│                         │ search results w/ page nos │ chat history, exports, syncing │
└─────────────────────────┴────────────────────────────┴────────────────────────────────┘
```

### Other styles you'll see
```
Page-number API:  ?page=3&limit=20         (offset under the hood)
Seek by id:       ?after_id=9001            (simple cursor when sorting by id)
Link header:      Link: <...?cursor=abc>; rel="next"   (GitHub)
GraphQL Relay:    edges { node cursor } pageInfo { hasNextPage endCursor }
Time-based sync:  ?updated_since=2024-10-01T00:00:00Z  (mobile offline sync)
```

### Counting totals is expensive
```
SELECT COUNT(*) on 50M rows = full scan-ish → slow.
Options: don't show exact totals ("1,000+"), cache counts, use estimates
(pg_class.reltuples / EXPLAIN row estimate), or a counter table.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Offset: `LIMIT 20 OFFSET 40` — DB 60 rows पढ़ता है, 40 फेंकता है; पेज जितना गहरा, उतना धीमा।
2. Cursor: पिछले पन्ने के आख़िरी item का `(created_at, id)` याद रखो, अगली बार `WHERE (created_at, id) < cursor`।
3. Index की मदद से DB सीधे उस जगह पहुँचता है — पहला पन्ना हो या हज़ारवाँ, एक जैसी स्पीड।
4. Cursor को base64 string बनाकर client को दो; client उसे खोलता नहीं, बस अगली request में भेजता है।
5. Admin टेबल (page नंबर चाहिए) → offset; feed, infinite scroll, chat → cursor।

---

## 🟡 Real World Example

**Twitter/X, Instagram, Facebook APIs** — all use cursor pagination for timelines (`max_id` / `since_id` historically, `next_cursor` tokens now), because new posts arrive constantly and users scroll deep.

**Slack API** — moved from offset/page to cursor-based pagination across its APIs (2017) for performance and consistency at scale, with `response_metadata.next_cursor`.

**Stripe API** — `starting_after=obj_id` / `ending_before=obj_id` is keyset pagination using object IDs.

**Google Search** — page numbers (offset-like), but they cap deep paging at roughly the first few hundred results.

## 🟡 Real Example Hindi में
Twitter, Instagram, Facebook की timelines cursor pagination इस्तेमाल करती हैं — लगातार नए posts आते हैं और लोग बहुत नीचे तक scroll करते हैं।
Slack ने 2017 में अपनी APIs offset से cursor पर बदलीं; Stripe `starting_after=id` से keyset pagination करता है। Google search में पन्ने नंबर हैं, पर गहराई की सीमा है।

---

## 🟠 My Stack Example

### Node.js (Express + pg) — reusable cursor helpers
```js
const encode = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
const decode = (s) => JSON.parse(Buffer.from(s, 'base64url').toString());

app.get('/api/v1/orders', auth, async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 100);
  const c = req.query.cursor ? decode(req.query.cursor) : null;

  const { rows } = await pool.query(
    `SELECT id, total, status, created_at FROM orders
     WHERE user_id = $1
       AND ($2::timestamptz IS NULL OR (created_at, id) < ($2, $3))
     ORDER BY created_at DESC, id DESC
     LIMIT $4`,
    [req.user.id, c?.t ?? null, c?.id ?? null, limit + 1]
  );
  const hasMore = rows.length > limit;
  const data = rows.slice(0, limit);
  const last = data.at(-1);
  res.json({ data, pagination: { hasMore, nextCursor: hasMore ? encode({ t: last.created_at, id: last.id }) : null } });
});
// index: CREATE INDEX ON orders (user_id, created_at DESC, id DESC);
```

### Prisma (cursor built in, by unique field)
```js
const page = await prisma.order.findMany({
  where: { userId },
  orderBy: [{ createdAt: 'desc' }, { id: 'desc' }],
  take: 21,
  ...(cursorId && { cursor: { id: cursorId }, skip: 1 }),   // skip the cursor row itself
});
```

### FastAPI
```python
@router.get("/orders")
async def list_orders(cursor: str | None = None, limit: int = Query(20, le=100), user=Depends(current_user)):
    c = json.loads(base64.urlsafe_b64decode(cursor)) if cursor else None
    stmt = select(Order).where(Order.user_id == user.id)
    if c:
        stmt = stmt.where(tuple_(Order.created_at, Order.id) < (datetime.fromisoformat(c["t"]), c["id"]))
    rows = (await session.scalars(stmt.order_by(Order.created_at.desc(), Order.id.desc()).limit(limit + 1))).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_c = base64.urlsafe_b64encode(json.dumps({"t": rows[-1].created_at.isoformat(), "id": rows[-1].id}).encode()).decode() if has_more else None
    return {"data": rows, "pagination": {"hasMore": has_more, "nextCursor": next_c}}
```

### MongoDB
```js
const q = { userId };
if (cursor) q.$or = [{ createdAt: { $lt: c.t } }, { createdAt: c.t, _id: { $lt: c.id } }];
const docs = await Order.find(q).sort({ createdAt: -1, _id: -1 }).limit(limit + 1).lean();
// index { userId: 1, createdAt: -1, _id: -1 }
```

### React Native infinite scroll (React Query + FlashList)
```tsx
const q = useInfiniteQuery({
  queryKey: ['orders'],
  queryFn: ({ pageParam }) => api.get('/api/v1/orders', { params: { cursor: pageParam, limit: 20 } }).then(r => r.data),
  initialPageParam: undefined as string | undefined,
  getNextPageParam: (last) => last.pagination.nextCursor ?? undefined,
});
const items = q.data?.pages.flatMap((p) => p.data) ?? [];

<FlashList
  data={items}
  estimatedItemSize={80}
  keyExtractor={(o) => String(o.id)}
  renderItem={({ item }) => <OrderRow order={item} />}
  onEndReached={() => q.hasNextPage && !q.isFetchingNextPage && q.fetchNextPage()}
  onEndReachedThreshold={0.5}
  refreshing={q.isRefetching}
  onRefresh={q.refetch}
/>
```
Next.js admin table with page numbers → offset is fine (`?page=3`), with a max page limit.

---

## ⚫ Interview Questions + Answers

**Q1: Explain offset vs cursor pagination and their trade-offs.**
A1: Offset (`LIMIT n OFFSET k`) is simple and supports jumping to arbitrary pages, but the DB scans and discards k rows, so deep pages get slow, and concurrent inserts or deletes shift results (duplicates or skips). Cursor/keyset pagination uses the last item's sort key as a bookmark (`WHERE (created_at,id) < (…) LIMIT n`), so with a matching index it costs the same at any depth and stays stable under inserts. But you can't jump to page 57 or easily show total pages.

**Q2: Why do you need a tie-breaker column in cursor pagination?**
A2: The sort key (e.g. created_at) may not be unique, since many rows can share a timestamp. Without a unique tie-breaker (id), rows with the same value can be skipped or repeated at page boundaries. Sort by `(created_at DESC, id DESC)`, compare with the row-value `(created_at, id) < (:t, :id)`, and index both columns in the same order.

**Q3: How would you paginate a news feed that updates in real time?**
A3: Cursor pagination on a stable sort key (created_at plus id, or a ranking score plus id snapshot), with an opaque cursor token and `hasMore`. Scrolling down uses `nextCursor`. New items at the top are fetched separately with a "newer than first item" query or a "new posts" banner via push/WebSocket. Personalized ranked feeds often precompute a ranked list per user (in Redis), and the cursor is the position or score within that list.

**Q4: How do you show the total count efficiently on a huge table?**
A4: Avoid exact `COUNT(*)` per request on large tables. Options: show approximate counts ("10k+") from planner statistics, maintain counter tables updated via triggers or events, cache counts in Redis with a TTL, cap counting (`SELECT count(*) FROM (SELECT 1 ... LIMIT 1001)`), or use the search engine's count. Many products drop total pages entirely in favour of infinite scroll.

**Q5: What should a good paginated API response look like?**
A5: A consistent envelope: `data` (items), `pagination: { nextCursor, hasMore }` (and maybe `prevCursor`). Use an opaque, possibly signed cursor. Enforce a server-side max limit (e.g. 100) with a sensible default, document a stable sort order, and keep filter parameters with the cursor (or embedded in it) so pages stay consistent. For offset-based admin APIs: `page`, `limit`, an optional `total`, and a cap on maximum page depth.

---

## 🔷 Trade-offs
✅ Offset: simple, random page access, easy UI with page numbers.
❌ Offset: slow deep pages, inconsistent under writes, DoS risk with huge offsets.
✅ Cursor: constant performance, consistent, scales to infinite scroll and exports.
❌ Cursor: no random page jumps, totals hard, needs index matching sort, slightly more code.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pagination | Returning data in pages | डेटा पन्नों में देना |
| Offset | Number of rows to skip | कितनी rows छोड़नी हैं |
| Cursor | Bookmark of last item | आख़िरी item का निशान |
| Keyset pagination | Using sort keys as cursor | sort key से अगला पन्ना |
| Tie-breaker | Unique column for stable order | बराबरी तोड़ने वाला column |
| Opaque token | Client can't interpret it | client के लिए बंद string |
| Infinite scroll | Load more as user scrolls | नीचे जाते ही और लोड |
| hasMore | Flag that more data exists | और डेटा बाक़ी है |

---

## ⚡ 3-Line Summary
**English:**
1. Offset = skip N rows (simple, page jumps) but slow at depth and unstable with inserts.
2. Cursor/keyset = "after this (sort key, id)", constant speed with a matching index, stable — best for feeds and APIs.
3. Use opaque cursors, a unique tie-breaker, a max limit, and `limit+1` to compute hasMore.

**Hindi:**
1. Offset = N rows छोड़ो — आसान, पर गहरे पन्नों पर धीमा और नए डेटा से गड़बड़।
2. Cursor = "इस item के बाद" — index के साथ हमेशा तेज़, feed के लिए सबसे अच्छा।
3. Opaque cursor, unique tie-breaker, max limit और `limit+1` से hasMore।

---

## ➡️ Next Topic Suggestion
**40. Read Replicas** — Pagination reduces data per query. Next: scaling the NUMBER of reads by copying the database to replicas, plus replication lag and read-your-own-writes problems.
