# F12. Pagination, Infinite Scroll + Virtualization
# हिंदी में: Pagination — बड़ी list को पन्नों में लाना; Infinite Scroll — नीचे पहुँचते ही अगला हिस्सा अपने-आप लाना; Virtualization — हज़ारों items में से सिर्फ़ स्क्रीन पर दिखने वाले render करना ताकि scrolling तेज़ रहे

---

## 🔵 Simple Definition (English)
- **Pagination (UI)**: show data in **pages** with "Next/Previous" or page numbers (search results, admin tables). The URL holds the page (`?page=3`).
- **Infinite scroll**: automatically fetch and append the next page when the user nears the end of the list (feeds, reels, product grids). A **"Load more" button** is a manual variant.
- **API pagination**: **offset/limit** (`?page=3&limit=20`) or **cursor/keyset** (`?cursor=abc&limit=20`), the latter being stable for changing feeds (Topic 39).
- **Virtualization (windowing)**: render only the items **visible in the viewport (+ a small buffer)**, recycling DOM/native views as you scroll. Libraries: `@tanstack/react-virtual`, `react-window`, `react-virtuoso`; React Native: **FlatList**, **FlashList** (M13).

## 🔵 सरल परिभाषा (Hindi)
Pagination = डेटा पन्नों में (Next/Previous या page नंबर); Infinite scroll = list के आख़िर के पास पहुँचते ही अगला पन्ना अपने-आप जुड़ जाए (feed, reels); "Load more" बटन इसका manual रूप।
API में offset (`?page=3`) या cursor (`?cursor=abc`) — बदलते feed के लिए cursor ठीक। Virtualization = हज़ारों items में से सिर्फ़ दिखने वाले (और थोड़े आगे-पीछे) render करो, बाक़ी नहीं।

---

## 🔴 Problem it Solves
- Loading **10,000 products at once**: huge JSON on mobile data, slow API, memory blowup.
- Rendering 10,000 DOM nodes (each card has ~20 elements, so 200k nodes): **slow initial render, janky scrolling, high memory**, poor INP (F05). On a low-end Android it can freeze or crash.
- Offset pagination on a live feed: new posts shift items, causing **duplicates or skipped items**.
- Infinite scroll done badly: **lost scroll position** on back, unreachable footer, poor accessibility and SEO.

Pagination limits **data**, virtualization limits **rendering**. Together they keep huge lists fast.

## 🔴 यह क्यों बना? (Hindi)
10,000 products एक साथ लाना = भारी JSON, धीमा API, memory भरना; 10,000 cards render करना = लाखों DOM nodes, धीमा render, झटकेदार scrolling, सस्ते फ़ोन पर ऐप अटकना।
Live feed में offset से नए posts आने पर items दोहराए या छूट जाते हैं; ख़राब infinite scroll में back पर जगह खो जाती है, footer तक नहीं पहुँचते। Pagination डेटा कम करता है, virtualization render कम करता है।

---

## 🟢 How it Works — Step by Step

### UI patterns: when to use which

```
┌────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│ Pattern            │ Best for                        │ Watch out                            │
├────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ Numbered pages     │ Search results, admin tables,   │ Extra clicks; offset cost on deep    │
│                    │ SEO listing pages, "go to p. 5" │ pages                                │
│ Load more button   │ Product grids, comments; user   │ One extra tap                        │
│                    │ control + footer reachable      │                                      │
│ Infinite scroll    │ Feeds, reels, discovery,        │ Footer unreachable, back/scroll      │
│                    │ continuous consumption          │ restoration, a11y, memory → virtualize│
└────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Infinite scroll mechanics

```
[item 1] … [item 18] [item 19] [item 20] [sentinel <div>] ← IntersectionObserver watches this
                                              │ becomes visible (rootMargin: 600px → prefetch early)
                                              ▼
                       if hasNextPage && !isFetchingNextPage → fetchNextPage(cursor)
                                              ▼
                       append page 2 → sentinel moves down → repeat
Guards: don't double-fetch, stop when nextCursor = null, show error + "Retry" row on failure,
        skeleton rows while loading, dedupe items by id (cursor overlap)
```

### Virtualization (windowing)

```
Total list: 10,000 items × 120 px = 1,200,000 px tall (a spacer div gives the scrollbar its size)

 ┌───────────── viewport (800 px) ─────────────┐
 │ overscan  item 98                            │   only ~10 visible + ~5 overscan above/below
 │           item 99                            │   are real DOM nodes (≈ 20 instead of 10,000)
 │ visible   item 100 … item 106                │
 │ overscan  item 107, 108                      │
 └──────────────────────────────────────────────┘
 Items are absolutely positioned (translateY(index × size)); on scroll, the range
 [startIndex, endIndex] is recalculated and nodes are reused.

Fixed-height items → simple math; variable heights → measure on render (measureElement) + estimate
```

### Scroll restoration & state

```
Back navigation should return to the same item:
- Keep pages in the query cache (React Query infinite query) → data still there on return
- Save scroll offset / first visible index (sessionStorage or router state) and restore it
- Next.js/React Router restore window scroll; virtualized containers need manual restore (initialOffset)
For SEO: infinite lists should also have crawlable paginated URLs (?page=2) with <a href> links
```

### Accessibility for infinite feeds

```
- role="feed" with articles (aria-setsize / aria-posinset if known), aria-busy while loading
- Keyboard: Tab through items without trapping; "Skip to footer" link; offer "Load more" button fallback
- Announce new content politely (aria-live) — don't steal focus
- Virtualized lists: items not in DOM aren't findable by Ctrl+F or screen readers → consider trade-offs
```

### Real-time feeds: new items at the top

```
Don't jump the list while the user reads. Show a "↑ 5 new posts" pill; on click, prepend & scroll to top.
Cursor pagination (by created_at,id) keeps older pages stable even as new items arrive.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Search/admin के लिए page नंबर (URL में `?page=3`), product grid के लिए "Load more", feed/reels के लिए infinite scroll।
2. Infinite scroll: list के नीचे एक sentinel div, IntersectionObserver से पहले ही (600px पहले) पता चलते ही अगला पन्ना लाओ; दोबारा fetch न हो, ख़त्म हो तो रुको, error पर "Retry"।
3. Virtualization: 10,000 items की पूरी ऊँचाई का खाली spacer, पर DOM में सिर्फ़ ~20 असली items — scroll पर वही nodes नए items के लिए इस्तेमाल।
4. Back पर उसी जगह लौटो — डेटा query cache में रहे, scroll offset सहेजो; SEO के लिए `?page=2` वाले links भी रखो।
5. Accessibility: `role="feed"`, `aria-busy`, "Load more" बटन विकल्प, नए content की घोषणा बिना focus छीने; नए posts ऊपर आएँ तो list मत खिसकाओ — "5 नए posts" बटन दिखाओ।

---

## 🟡 Real World Example

**Instagram / Twitter (X) / LinkedIn feeds** — infinite scroll with cursor pagination and virtualization or view recycling. A "new posts" pill avoids jumping content. Twitter's web app virtualizes the timeline to keep memory bounded during long sessions.

**Flipkart / Amazon search** — product listing pages use numbered pagination or "load more" with SEO-friendly URLs, while mobile apps use infinite grids with recycling lists.

**Google Sheets / Airtable / Razorpay-style dashboards** — virtualize rows and columns, so a table with 100k rows renders only the ~50 visible rows.

**WhatsApp / Slack chats** — reverse infinite scroll (load older messages when scrolling up) while keeping scroll anchored at the bottom. A tricky variant.

## 🟡 Real Example Hindi में
Instagram/Twitter/LinkedIn feed में infinite scroll + cursor pagination + virtualization — नए posts पर "new posts" बटन, list नहीं खिसकती।
Flipkart/Amazon search में page नंबर या "load more" (SEO वाले URLs); Google Sheets जैसे tables में 1 लाख rows में से सिर्फ़ ~50 दिखने वाली render होती हैं; WhatsApp में ऊपर scroll करने पर पुराने messages आते हैं (उल्टा infinite scroll)।

---

## 🟠 My Stack Example

### Backend: cursor pagination (Node + Postgres) — stable for live feeds
```js
// GET /feed?cursor=<base64 of createdAt|id>&limit=20
app.get('/feed', auth, async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 50);
  const c = req.query.cursor ? JSON.parse(Buffer.from(req.query.cursor, 'base64url').toString()) : null;
  const rows = await db.query(
    `SELECT id, author_id, text, created_at FROM posts
     WHERE ($1::timestamptz IS NULL OR (created_at, id) < ($1, $2))
     ORDER BY created_at DESC, id DESC LIMIT $3`, [c?.createdAt ?? null, c?.id ?? null, limit + 1]);
  const hasMore = rows.rows.length > limit;
  const items = rows.rows.slice(0, limit);
  const last = items.at(-1);
  res.json({ items, nextCursor: hasMore ? Buffer.from(JSON.stringify({ createdAt: last.created_at, id: last.id })).toString('base64url') : null });
});
```

### Web: infinite query + IntersectionObserver + virtualization (TanStack Virtual)
```tsx
'use client';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useEffect, useRef } from 'react';

export function Feed() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isError, refetch } = useInfiniteQuery({
    queryKey: ['feed'], initialPageParam: undefined as string | undefined,
    queryFn: ({ pageParam, signal }) => http.get('/feed', { params: { cursor: pageParam }, signal }).then((r) => r.data),
    getNextPageParam: (last) => last.nextCursor ?? undefined,
  });
  const posts = data?.pages.flatMap((p) => p.items) ?? [];

  const parentRef = useRef<HTMLDivElement>(null);
  const v = useVirtualizer({
    count: hasNextPage ? posts.length + 1 : posts.length,        // +1 loader row
    getScrollElement: () => parentRef.current,
    estimateSize: () => 320, overscan: 5,
  });
  const items = v.getVirtualItems();

  useEffect(() => {                                               // fetch when loader row is near
    const last = items.at(-1);
    if (last && last.index >= posts.length - 3 && hasNextPage && !isFetchingNextPage) fetchNextPage();
  }, [items, posts.length, hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div ref={parentRef} style={{ height: '100dvh', overflowY: 'auto' }} role="feed" aria-busy={isFetchingNextPage}>
      <div style={{ height: v.getTotalSize(), position: 'relative' }}>
        {items.map((row) => {
          const post = posts[row.index];
          return (
            <div key={row.key} data-index={row.index} ref={v.measureElement}      // variable heights measured
                 style={{ position: 'absolute', top: 0, left: 0, width: '100%', transform: `translateY(${row.start}px)` }}>
              {post ? <PostCard post={post} aria-posinset={row.index + 1} />
                    : isError ? <button onClick={() => refetch()}>Couldn’t load. Retry</button>
                    : <PostSkeleton />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### Simple infinite scroll without virtualization (small lists)
```tsx
function useSentinel(onVisible: () => void, enabled: boolean) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!enabled || !ref.current) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && onVisible(), { rootMargin: '600px' });
    io.observe(ref.current);
    return () => io.disconnect();
  }, [onVisible, enabled]);
  return ref;
}
// <div ref={useSentinel(fetchNextPage, hasNextPage && !isFetchingNextPage)} />
```

### Numbered pagination with URL state (Next.js Server Component, SEO-friendly)
```tsx
export default async function Products({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const { items, totalPages } = await getProducts({ page, limit: 24 });
  return (<>
    <ProductGrid items={items} />
    <nav aria-label="Pagination">
      {page > 1 && <a href={`?page=${page - 1}`} rel="prev">Previous</a>}
      <span aria-current="page">Page {page} of {totalPages}</span>
      {page < totalPages && <a href={`?page=${page + 1}`} rel="next">Next</a>}
    </nav>
  </>);
}
```

### React Native: FlashList with infinite loading (M13 has details)
```tsx
import { FlashList } from '@shopify/flash-list';
<FlashList
  data={posts}
  renderItem={({ item }) => <PostCard post={item} />}
  keyExtractor={(p) => p.id}
  onEndReached={() => hasNextPage && !isFetchingNextPage && fetchNextPage()}
  onEndReachedThreshold={0.5}                      // when within half a screen of the end
  ListFooterComponent={isFetchingNextPage ? <ActivityIndicator /> : null}
  refreshing={isRefetching} onRefresh={refetch}    // pull to refresh
/>
// (FlashList v1 also needs estimatedItemSize; v2 measures automatically)
```

---

## ⚫ Interview Questions + Answers

**Q1: Infinite scroll vs pagination — how do you choose?**
A1: Infinite scroll suits continuous, discovery-style consumption (social feeds, reels, image galleries) where users rarely need a specific position. Pagination suits goal-oriented tasks where users compare, return to or jump to positions (search results, admin tables, SEO listings), and it keeps footers reachable and URLs shareable. "Load more" is a good middle ground. Whichever you choose, use cursor-based API pagination for live data, preserve scroll position on back, and provide accessible controls.

**Q2: What is list virtualization and how does it work?**
A2: Virtualization renders only items in or near the viewport instead of the whole list. A container with the full computed height preserves the scrollbar. On scroll, the library computes the visible index range from the scroll offset and item sizes (fixed or measured), renders those items absolutely positioned (translateY), and recycles or unmounts the rest, with an overscan buffer to avoid blank flashes. This keeps DOM size, memory and render cost constant regardless of list length.

**Q3: Why use cursor pagination for feeds?**
A3: With offset pagination, inserting new items at the top shifts all offsets, so the next page returns duplicates and deletions cause skipped items. Deep offsets are also slow (the DB scans and discards rows). Cursor or keyset pagination uses the last seen sort key (e.g., `created_at, id`) to fetch the next items with an indexed range query, which stays stable under concurrent writes and is fast at any depth. The downside: you can't jump to an arbitrary page number.

**Q4: How do you implement infinite scroll robustly?**
A4: Use an IntersectionObserver on a sentinel near the end with a generous `rootMargin` so the next page is prefetched. Guard against duplicate fetches (in-flight flag) and stop when there's no next cursor. Show skeletons while loading and an inline retry on errors. Dedupe items by ID. Virtualize when lists grow long. Cache pages and restore the scroll position on back navigation. Provide crawlable paginated URLs for SEO and a "Load more" fallback for accessibility. Handle new items arriving at the top with a "new posts" indicator rather than shifting content.

**Q5: What are the downsides of virtualization?**
A5: Off-screen items aren't in the DOM, so browser find-in-page, some screen-reader navigation and SEO can't see them. Variable-height items need measurement, which can cause scroll jumps if estimates are off. Scroll restoration and anchoring (chat apps that load older messages) are trickier. Complex layouts (sticky headers, grids, drag and drop) need extra work. It adds complexity that isn't needed for lists under a few hundred items.

---

## 🔷 Trade-offs
✅ Pagination: predictable, shareable, SEO — ❌ extra clicks, offset slowness on deep pages.
✅ Infinite scroll: engaging, seamless — ❌ footer, scroll restoration, a11y, memory.
✅ Virtualization: constant performance for huge lists — ❌ Ctrl+F/SEO/a11y limits, complexity.
✅ Cursor API: stable & fast — ❌ no random page jumps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pagination | Data split into pages | पन्नों में डेटा |
| Infinite scroll | Auto-load next page on scroll | scroll पर अपने-आप अगला |
| Cursor | Pointer to last seen item | आख़िरी item का निशान |
| Offset | Number of rows to skip | कितनी rows छोड़नी हैं |
| Sentinel | Element watched to trigger loading | load ट्रिगर करने वाला div |
| IntersectionObserver | API to detect visibility | दिखने का पता लगाने वाला API |
| Virtualization | Render only visible items | सिर्फ़ दिखने वाले render |
| Overscan | Extra items rendered around viewport | आगे-पीछे के कुछ items |
| Scroll restoration | Return to previous position | पुरानी जगह पर लौटना |
| role="feed" | ARIA pattern for feeds | feed की a11y भूमिका |

---

## ⚡ 3-Line Summary
**English:**
1. Pages for goal-oriented lists (search, tables, SEO), infinite scroll for feeds, "load more" as a middle ground; cursor API for live data.
2. Infinite scroll = sentinel + IntersectionObserver + guards (no double fetch, retry, dedupe, stop at end) + scroll restoration.
3. Virtualize long lists (TanStack Virtual / FlashList) to render only visible items; mind a11y, SEO and variable heights.

**Hindi:**
1. Search/tables के लिए पन्ने, feed के लिए infinite scroll, बीच में "load more"; live डेटा के लिए cursor।
2. Infinite scroll = sentinel + IntersectionObserver + सुरक्षा (दोबारा fetch नहीं, retry, dedupe) + back पर वही जगह।
3. लंबी list virtualize करो (TanStack Virtual / FlashList); a11y, SEO और अलग-अलग ऊँचाई का ध्यान।

---

## ➡️ Next Topic Suggestion
**F13. Real-Time on Frontend (Polling vs SSE vs WebSocket)** — Feeds, chats and order tracking need live updates. Next: polling, long polling, Server-Sent Events and WebSockets from the client's view, including reconnects and offline handling.
