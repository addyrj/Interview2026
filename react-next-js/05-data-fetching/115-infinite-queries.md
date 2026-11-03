# 115. Infinite Queries
# हिंदी में: Infinite Queries — Scroll करते जाओ, Pages अपने आप Load होते जाएँ

---

## 🔵 Simple Definition (English)
An **infinite query** (`useInfiniteQuery` in TanStack Query v5) fetches data page by page and keeps all loaded pages in one cache entry. You call `fetchNextPage()` to load the next page, and the library remembers where each page starts using a "page param" (a cursor or page number).

## 🔵 सरल परिभाषा (Hindi)
**Infinite query** (TanStack Query v5 में `useInfiniteQuery`) data को page-by-page लाती है और सारे loaded pages को एक ही cache entry में रखती है। अगला page लाने के लिए `fetchNextPage()` बुलाते हैं, और library "page param" (cursor या page number) से याद रखती है कि अगला page कहाँ से शुरू होगा।

---

## 🔴 Problem it Solves

A feed like Instagram or Zomato's restaurant list can have thousands of items. Loading everything at once is slow and wasteful. The manual fix is `useState` for pages, `useEffect` for fetching, and a counter for the page number. That quickly gets messy: you must merge pages, avoid duplicate requests, handle loading and error for each page, and keep the scroll position when the user comes back.

```jsx
// PROBLEM: manual pagination state
const [items, setItems] = useState([]);         // merged items from all pages
const [page, setPage] = useState(1);            // current page number
const [loading, setLoading] = useState(false);  // loading flag
const [hasMore, setHasMore] = useState(true);   // did the server say "no more"?
// + duplicate request guard, error handling, cache, refetch, retry...

// SOLUTION: one hook handles all of it
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({ /* ... */ });
```

## 🔴 यह क्यों बना? (Hindi)
Instagram या Zomato की restaurant list में हज़ारों items हो सकते हैं। सब एक साथ लाना धीमा और बेकार है। हाथ से करने पर `useState` (pages के लिए), `useEffect` (fetch के लिए) और page number का counter बनाना पड़ता है। जल्दी ही गड़बड़ हो जाती है: pages merge करने होते हैं, duplicate requests रोकनी होती हैं, हर page का loading/error संभालना होता है, और user लौटे तो scroll position भी बचानी होती है। `useInfiniteQuery` यह सब एक hook में कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write queryFn({ pageParam }) that fetches ONE page using pageParam
Step 2 → Set initialPageParam (v5: required), e.g. 0 or null for the first page
Step 3 → Write getNextPageParam(lastPage) → returns the next cursor, or undefined when finished
Step 4 → data = { pages: [page1, page2, ...], pageParams: [...] }  (all pages in one cache entry)
Step 5 → Call fetchNextPage() on button click or when a sentinel div enters the viewport
Step 6 → hasNextPage becomes false when getNextPageParam returns undefined or null
Step 7 → On refetch, ALL loaded pages are refetched one by one, in order (keeps data consistent)

KEY: flatten pages for UI → data.pages.flatMap(p => p.items)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → queryFn({ pageParam }) लिखो जो pageParam से सिर्फ एक page लाए
Step 2 → initialPageParam दो (v5 में ज़रूरी), जैसे 0 या null (पहले page के लिए)
Step 3 → getNextPageParam(lastPage) लिखो → अगला cursor लौटाए, या खत्म होने पर undefined
Step 4 → data = { pages: [page1, page2, ...], pageParams: [...] } (सारे pages एक cache entry में)
Step 5 → बटन click पर या sentinel div के viewport में आने पर fetchNextPage() बुलाओ
Step 6 → getNextPageParam के undefined/null लौटाने पर hasNextPage false हो जाता है
Step 7 → Refetch पर सारे loaded pages एक-एक करके क्रम से दोबारा आते हैं (data consistent रहता है)

KEY: UI के लिए pages को flatten करो → data.pages.flatMap(p => p.items)
```

---

## 🟡 Real World Example
**Swiggy restaurant listing:** When you open Swiggy, it shows about 10 restaurants. As you scroll to the bottom, the next batch loads automatically (infinite scroll). The server returns `{ items, nextCursor }`. Swiggy-like apps use the cursor so that, if a new restaurant is added meanwhile, you do not see duplicates or miss one (page numbers shift, cursors do not). `useInfiniteQuery` holds all pages, and an IntersectionObserver on a small div at the bottom triggers `fetchNextPage()`.

## 🟡 Real Example Hindi mein
**Swiggy restaurant listing:** Swiggy खोलने पर करीब 10 restaurants दिखते हैं। नीचे scroll करने पर अगला batch अपने आप आ जाता है (infinite scroll)। Server `{ items, nextCursor }` लौटाता है। Cursor इसलिए इस्तेमाल होता है कि बीच में कोई नया restaurant जुड़े तो duplicate या missing items न दिखें (page numbers खिसक जाते हैं, cursor नहीं)। `useInfiniteQuery` सारे pages रखता है, और सबसे नीचे का छोटा div IntersectionObserver से `fetchNextPage()` trigger करता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: "Load more" button with useInfiniteQuery (TanStack Query v5)
import { QueryClient, QueryClientProvider, useInfiniteQuery } from '@tanstack/react-query'; // v5 imports
import { createRoot } from 'react-dom/client';                // React 18/19 root API

const queryClient = new QueryClient();                        // one cache for the whole app

// Fetch ONE page of restaurants; pageParam is the page number here
async function fetchRestaurants({ pageParam }) {
  const res = await fetch(`/api/restaurants?page=${pageParam}&limit=10`); // ask server for one page
  if (!res.ok) throw new Error('Failed to load');             // fetch does not throw on 404/500, so we do
  return res.json();                                          // expected: { items: [...], hasMore: true }
}

function RestaurantList() {
  const {
    data,                // { pages: [...], pageParams: [...] }
    fetchNextPage,       // function: load the next page
    hasNextPage,         // boolean: is there another page?
    isFetchingNextPage,  // boolean: is the NEXT page loading right now?
    status,              // 'pending' | 'error' | 'success'
    error,               // error object when status === 'error'
  } = useInfiniteQuery({
    queryKey: ['restaurants'],                                // cache key for this list
    queryFn: fetchRestaurants,                                // receives { pageParam }
    initialPageParam: 1,                                      // v5: required, first page = 1
    getNextPageParam: (lastPage, allPages) =>                 // decide the next page number
      lastPage.hasMore ? allPages.length + 1 : undefined,     // undefined = no more pages
  });

  if (status === 'pending') return <p>Loading...</p>;         // first load
  if (status === 'error') return <p>Error: {error.message}</p>; // first load failed

  return (
    <div>
      {data.pages.map((page, i) => (                          // loop over pages
        <ul key={i}>                                          {/* one list per page */}
          {page.items.map(r => <li key={r.id}>{r.name}</li>)} {/* each restaurant */}
        </ul>
      ))}
      <button
        onClick={() => fetchNextPage()}                       // load next page on click
        disabled={!hasNextPage || isFetchingNextPage}         // block double clicks and the end
      >
        {isFetchingNextPage ? 'Loading more...' : hasNextPage ? 'Load more' : 'No more restaurants'}
      </button>
    </div>
  );
}

createRoot(document.getElementById('root')).render(           // mount with the provider
  <QueryClientProvider client={queryClient}><RestaurantList /></QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: cursor-based infinite scroll with IntersectionObserver, search filter and maxPages
import { useInfiniteQuery } from '@tanstack/react-query';     // v5
import { useEffect, useRef, useState } from 'react';          // React hooks

// Cursor-based fetch: server returns { items, nextCursor } (nextCursor = null at the end)
async function fetchFeed({ pageParam, queryKey, signal }) {
  const [, { search }] = queryKey;                             // read the filter from the key
  const params = new URLSearchParams({ q: search, limit: '10' }); // build query string safely
  if (pageParam) params.set('cursor', pageParam);             // first page has no cursor
  const res = await fetch(`/api/feed?${params}`, { signal }); // signal cancels stale requests
  if (!res.ok) throw new Error(`HTTP ${res.status}`);         // surface server errors
  return res.json();                                          // { items, nextCursor }
}

export default function Feed() {
  const [search, setSearch] = useState('');                   // filter text
  const sentinelRef = useRef(null);                           // invisible div at the list bottom

  const q = useInfiniteQuery({
    queryKey: ['feed', { search }],                           // new search = new cache entry
    queryFn: fetchFeed,                                       // one page per call
    initialPageParam: null,                                   // first page: no cursor
    getNextPageParam: lastPage => lastPage.nextCursor ?? undefined, // null/undefined stops paging
    staleTime: 60_000,                                        // do not refetch for 1 minute
    maxPages: 5,                                              // v5: keep at most 5 pages in memory
    // NOTE: with maxPages you should ALSO define getPreviousPageParam (version-dependent behaviour)
    getPreviousPageParam: firstPage => firstPage.prevCursor ?? undefined,
  });

  const { hasNextPage, isFetchingNextPage, fetchNextPage } = q; // pull out what the effect needs

  useEffect(() => {
    const el = sentinelRef.current;                           // the bottom marker
    if (!el) return;                                          // not mounted yet
    const observer = new IntersectionObserver(entries => {    // browser tells us when it is visible
      if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();                                      // load next page automatically
      }
    }, { rootMargin: '200px' });                              // start loading 200px early
    observer.observe(el);                                     // begin watching
    return () => observer.disconnect();                       // cleanup on unmount or change
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);       // re-subscribe when state changes

  const items = q.data?.pages.flatMap(p => p.items) ?? [];    // flatten all pages for rendering

  return (
    <div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search" />
      {q.isPending && <p>Loading...</p>}
      {q.isError && <p role="alert">Something went wrong. <button onClick={() => q.refetch()}>Retry</button></p>}
      <ul>{items.map(item => <li key={item.id}>{item.title}</li>)}</ul> {/* stable ids as keys */}
      <div ref={sentinelRef} style={{ height: 1 }} />         {/* the trigger element */}
      {isFetchingNextPage && <p>Loading more...</p>}
      {!hasNextPage && items.length > 0 && <p>You reached the end</p>}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

In the App Router, you can fetch the first page on the server and hand it to the client hook with `initialData` (or use `HydrationBoundary` with `prefetchInfiniteQuery`). Users then see content immediately (good for SEO and LCP), and later pages load on the client with the same hook. `useInfiniteQuery` must run in a Client Component (`'use client'`).

```jsx
// app/feed/page.jsx (Server Component): prefetch the first page, dehydrate, send to client
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query';
import FeedClient from './FeedClient';                       // 'use client' component using useInfiniteQuery

export default async function Page() {
  const queryClient = new QueryClient();                     // new client PER request (never share on server)
  await queryClient.prefetchInfiniteQuery({
    queryKey: ['feed', { search: '' }],                      // must match the client key exactly
    queryFn: async ({ pageParam }) => {
      const url = new URL('https://example.com/api/feed');   // use an absolute URL on the server
      if (pageParam) url.searchParams.set('cursor', pageParam);
      return (await fetch(url)).json();                      // { items, nextCursor }
    },
    initialPageParam: null,                                  // same as the client
    pages: 1,                                                // prefetch only the first page
  });
  return (
    <HydrationBoundary state={dehydrate(queryClient)}>       {/* pass cache to the browser */}
      <FeedClient />
    </HydrationBoundary>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `initialPageParam` (required in v5) or mixing v4 syntax
✅ **Correct:** Always pass `initialPageParam` and return `undefined` from `getNextPageParam` at the end

```jsx
// Wrong (v4 style): no initialPageParam, pageParam may be undefined
useInfiniteQuery({ queryKey: ['x'], queryFn: ({ pageParam = 1 }) => get(pageParam), getNextPageParam });

// Right (v5): explicit first page param
useInfiniteQuery({ queryKey: ['x'], queryFn: ({ pageParam }) => get(pageParam), initialPageParam: 1, getNextPageParam });
```

❌ **Mistake 2:** Calling `fetchNextPage()` repeatedly without checking state (duplicate requests)
✅ **Correct:** Guard with `hasNextPage && !isFetchingNextPage`

```jsx
// Wrong: observer fires many times while a request is already in flight
if (entry.isIntersecting) fetchNextPage();
// Right
if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) fetchNextPage();
```

❌ **Mistake 3:** Using page numbers on a changing feed (duplicates and gaps) and using array index as `key`
✅ **Correct:** Prefer cursors from the server, and use stable ids for keys

```jsx
// Wrong: index keys break when items shift between pages
items.map((item, i) => <Row key={i} {...item} />);
// Right: stable id
items.map(item => <Row key={item.id} {...item} />);
```

---

## 🧠 Tricky Interview Question

```jsx
const q = useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam }) => fetchPosts(pageParam),
  initialPageParam: 0,
  getNextPageParam: (last) => last.nextOffset,   // the server sends nextOffset: false on the last page
});
console.log(q.hasNextPage);                      // after the last page was loaded
```
**Answer:** It logs `true`, even though the server said "no more". `hasNextPage` becomes `false` only when `getNextPageParam` returns `undefined` (or `null` in v5; check your version). `false`, `0` and `''` are valid page params, so the library thinks there is another page and calls `queryFn(false)` on the next `fetchNextPage()`. The stop condition lives in `getNextPageParam`, so convert it yourself: `last.nextOffset === false ? undefined : last.nextOffset`, or better, make the server send `null`.

---

## ⚫ Interview Questions + Answers

Q1: What does `useInfiniteQuery` return that `useQuery` does not?
A1: `data` has the shape `{ pages, pageParams }` instead of a single result. It also returns `fetchNextPage`, `fetchPreviousPage`, `hasNextPage`, `hasPreviousPage`, `isFetchingNextPage` and `isFetchingPreviousPage`.

Q2: What are `initialPageParam` and `getNextPageParam`?
A2: `initialPageParam` is the value passed to `queryFn` for the first page. `getNextPageParam(lastPage, allPages, lastPageParam, allPageParams)` computes the param for the next page from the last loaded page, or returns `undefined`/`null` to say there are no more pages.

Q3: Cursor-based vs offset (page-number) pagination for infinite scroll?
A3: Cursor-based is safer for live feeds: the cursor points to a specific record, so inserts and deletes do not cause duplicates or skipped items. Offset pagination is simpler but shifts when data changes, and is slow on large tables for deep offsets.

Q4: What happens when you refetch an infinite query with 5 pages loaded?
A4: By default all 5 pages are refetched sequentially, starting from the first, using the stored page params. This keeps pages consistent but can be expensive. Use `maxPages` to limit memory and refetch cost (v5 feature, pair with `getPreviousPageParam`), or call `queryClient.resetQueries` to start from page one.

Q5: How do you implement automatic infinite scroll?
A5: Put a sentinel element at the bottom of the list, observe it with `IntersectionObserver` (or `react-intersection-observer`'s `useInView`), and call `fetchNextPage()` when it is visible and `hasNextPage && !isFetchingNextPage`. For huge lists also add virtualization so the DOM does not grow without limit.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Feeds, search results, chat history or order history that grow page by page
- You want automatic caching, dedupe, retry and background refetch for each page
- You need "Load more" or infinite scroll with scroll restoration on back navigation

❌ **Avoid when:**
- The data is small and fits in one request (use `useQuery`)
- Users need to jump to page 7 directly (use classic pagination with `useQuery` and `placeholderData: keepPreviousData`)
- The list is huge and you render all items without virtualization (DOM becomes slow)

---

## 📊 Visual Diagram

```
 Scroll down ───────────────────────────────────────────────┐
                                                            ▼
 ┌───────────────┐  fetchNextPage()   ┌───────────────────────────────┐
 │  Sentinel div │ ─────────────────► │ queryFn({ pageParam: cursor })│
 │ (IntersectionObserver)             └──────────────┬────────────────┘
 └───────────────┘                                   │ { items, nextCursor }
                                                     ▼
   data.pages = [ page1 ][ page2 ][ page3 ] ...   (ONE cache entry: ['feed'])
                                                     │
              getNextPageParam(lastPage) ────────────┤
                 ├─ cursor       → hasNextPage = true
                 └─ undefined    → hasNextPage = false (stop)

   Re-render: only the component using the hook re-renders when a page arrives.
   Performance: render 10 items per page, flatten once, virtualize after ~200 items.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Infinite query | Query that loads data page by page | Page-by-page data लाने वाली query |
| pageParam | Value that tells which page to fetch | बताता है कौन-सा page लाना है |
| Cursor | Pointer to a record for the next page | अगले page के लिए record का pointer |
| initialPageParam | Param for the first page (required in v5) | पहले page का param |
| getNextPageParam | Function that returns the next param | अगला param लौटाने वाला function |
| Sentinel | Hidden element used to trigger loading | Loading trigger करने वाला छुपा element |
| maxPages | Limit of pages kept in cache (v5) | Cache में रखे जाने वाले pages की सीमा |
| Flatten | Merge pages into one array | सारे pages को एक array बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. `useInfiniteQuery` loads data page by page and stores all pages in one cache entry as `data.pages`.
2. You provide `initialPageParam` and `getNextPageParam`; returning `undefined` stops paging.
3. Use cursors, guard `fetchNextPage`, flatten pages for rendering, and virtualize long lists.

**Hindi:**
1. `useInfiniteQuery` data को page-by-page लाती है और सारे pages को `data.pages` में एक cache entry में रखती है।
2. आप `initialPageParam` और `getNextPageParam` देते हैं; `undefined` लौटाने पर paging रुक जाती है।
3. Cursor इस्तेमाल करो, `fetchNextPage` को guard करो, rendering के लिए pages flatten करो, और लंबी lists को virtualize करो।

---

## ➡️ Next Topic
**116. RTK Query vs React Query** — दोनों में से कब कौन-सी library चुनें, और दोनों data fetching व caching कैसे अलग तरीके से संभालती हैं।
