# 194. Build Infinite Scroll
# हिंदी में: Infinite Scroll बनाना

Code: [`App.jsx`](./App.jsx) in this folder (IntersectionObserver sentinel, fake paginated API, loading guard, "end of list" state).

---

## 🔵 Simple Definition (English)
Infinite scroll loads the next page of data automatically when the user reaches the bottom of the list. There is no "Next page" button. Modern implementations use `IntersectionObserver` on a small "sentinel" element at the end of the list instead of listening to scroll events.

## 🔵 सरल परिभाषा (Hindi)
Infinite scroll में user जब list के नीचे पहुँचता है तो अगला page अपने-आप load हो जाता है। "Next page" button नहीं होता। आधुनिक तरीके में scroll events सुनने की जगह list के अंत में एक छोटे "sentinel" element पर `IntersectionObserver` लगाते हैं।

---

## 🔴 Problem it Solves

Loading 10,000 items at once is slow, heavy on memory and wastes data. Page numbers interrupt the browsing flow on mobile feeds. A scroll event listener fires dozens of times per second and measuring layout inside it causes jank. `IntersectionObserver` tells you efficiently when an element becomes visible, so you fetch only when needed.

```jsx
// PROBLEM: fetch everything up front, or poll the scroll position
useEffect(() => {
  window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) loadMore(); // fires constantly, forces layout
  });
}, []);                                                          // also no cleanup ❌
```

## 🔴 यह क्यों बना? (Hindi)
एक साथ 10,000 items लोड करना धीमा है, memory भारी करता है और data बर्बाद करता है। Mobile feeds में page numbers browsing का flow तोड़ते हैं। Scroll event listener सेकंड में दर्जनों बार चलता है और उसमें layout नापने से jank आता है। `IntersectionObserver` कुशलता से बताता है कि कोई element कब दिखने लगा, इसलिए आप ज़रूरत पड़ने पर ही fetch करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State: items[], page (next page number), loading, hasMore
Step 2 → Render the items, then an empty <div> sentinel at the very bottom
Step 3 → An IntersectionObserver watches the sentinel (rootMargin 200px = start early)
Step 4 → Sentinel becomes visible → loadMore() is called
Step 5 → loadMore() guards (ref) against double calls, fetches page N, appends items
Step 6 → page++; hasMore from the API; the list grows and the sentinel moves down
Step 7 → When hasMore is false the sentinel is removed and "end of list" is shown
Step 8 → Cleanup: disconnect the observer when the sentinel changes or unmounts

Interview approach: "Sentinel + IntersectionObserver, append don't replace, a ref guard
against duplicate fetches, hasMore flag, cleanup."
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State: items[], page (अगला page number), loading, hasMore
Step 2 → items render करो, फिर बिल्कुल नीचे एक खाली <div> sentinel
Step 3 → IntersectionObserver sentinel को देखता है (rootMargin 200px = पहले से शुरू)
Step 4 → Sentinel दिखने लगे → loadMore() call होता है
Step 5 → loadMore() ref से double calls रोकता है, page N लाता है, items जोड़ता है
Step 6 → page++; hasMore API से मिलता है; list बढ़ती है और sentinel नीचे खिसकता है
Step 7 → hasMore false हो तो sentinel हटाओ और "list खत्म" दिखाओ
Step 8 → Cleanup: sentinel बदलने या unmount पर observer disconnect करो

Interview approach: "Sentinel + IntersectionObserver, replace नहीं append, duplicate fetch रोकने
के लिए ref guard, hasMore flag, cleanup।"
```

---

## 🟡 Real World Example
**Instagram feed, Swiggy restaurant list, Flipkart product listing:** you scroll and more cards appear. Swiggy loads about 10 to 20 restaurants at a time, and starts fetching the next batch before you hit the end (that is the `rootMargin`). For very long feeds they also remove off-screen items (virtualisation) to keep the page fast.

## 🟡 Real Example Hindi mein
**Instagram feed, Swiggy restaurant list, Flipkart product listing:** आप scroll करते हैं और और cards आते जाते हैं। Swiggy एक बार में लगभग 10 से 20 restaurants लोड करता है, और अंत तक पहुँचने से पहले ही अगला batch माँगना शुरू कर देता है (यही `rootMargin` है)। बहुत लंबी feeds में स्क्रीन से बाहर के items हटाए भी जाते हैं (virtualisation) ताकि page तेज़ रहे।

---

## 💻 Code Example — Basic

```jsx
// Minimal sentinel pattern with useRef + useEffect
import { useState, useEffect, useRef } from 'react';

export default function Feed() {
  const [items, setItems] = useState(() => Array.from({ length: 10 }, (_, i) => i + 1)); // first page
  const sentinel = useRef(null);                               // element at the end of the list

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {   // callback gets entries
      if (entry.isIntersecting) {                              // sentinel is on screen
        setItems((prev) => [                                   // append 10 more numbers
          ...prev,
          ...Array.from({ length: 10 }, (_, i) => prev.length + i + 1),
        ]);
      }
    });
    observer.observe(sentinel.current);                        // start watching
    return () => observer.disconnect();                        // cleanup
  }, []);

  return (
    <div>
      {items.map((n) => <p key={n} style={{ height: 60 }}>Item {n}</p>)}
      <div ref={sentinel} />                                   {/* the sentinel */}
    </div>
  );
}
```

## 💻 Code Example — Advanced

The full component is in [`App.jsx`](./App.jsx). It handles loading, "no more data", and double triggers. Core pieces:

```jsx
// 1. A ref guard is synchronous; `loading` state is not (state updates are async)
const loadingRef = useRef(false);
const loadMore = useCallback(async () => {
  if (loadingRef.current) return;                              // block double calls
  loadingRef.current = true;
  setLoading(true);
  try {
    const res = await fetchPage(page);                         // { items, hasMore }
    setItems((prev) => [...prev, ...res.items]);               // append
    setHasMore(res.hasMore);
    setPage((p) => p + 1);
  } catch (err) {
    console.error('load failed', err);                         // show an error + retry in real apps
  } finally {
    loadingRef.current = false;                                // always release the guard
    setLoading(false);
  }
}, [page]);

// 2. Callback ref: (re)connects the observer whenever the sentinel mounts or loadMore changes
const sentinelRef = useCallback((node) => {
  if (observerRef.current) observerRef.current.disconnect();   // remove the old observer
  if (!node || !hasMore) return;
  observerRef.current = new IntersectionObserver(
    (entries) => { if (entries[0].isIntersecting) loadMore(); },
    { rootMargin: '200px' }                                    // pre-load 200px before the end
  );
  observerRef.current.observe(node);
}, [hasMore, loadMore]);
```

Verified with jsdom + a mock IntersectionObserver: triggering the observer five times loads pages of 10, 10, 10, 10 and 5 items (45 total), then shows "You have seen everything.".

---

## 🟠 Next.js Connection

In Next.js, render the **first page on the server** (fast, SEO-friendly) and let a Client Component load further pages, usually through a Route Handler or Server Action. TanStack Query's `useInfiniteQuery` (v5) is the production-grade tool.

```jsx
// app/feed/page.jsx (Server Component): first page rendered on the server
import FeedClient from './FeedClient';
import { getPage } from '@/lib/feed';                          // hypothetical data function

export default async function Page() {
  const first = await getPage(0);                              // { items, nextPage }
  return <FeedClient initial={first} />;
}
```

```jsx
// app/feed/FeedClient.jsx
'use client';
import { useInfiniteQuery } from '@tanstack/react-query';       // v5 API
import { useEffect, useRef } from 'react';

export default function FeedClient({ initial }) {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: ({ pageParam }) => fetch(`/api/feed?page=${pageParam}`).then((r) => r.json()),
    initialPageParam: 0,                                       // required in v5
    getNextPageParam: (last) => last.nextPage ?? undefined,    // undefined → hasNextPage false
    initialData: { pages: [initial], pageParams: [0] },        // reuse the server-rendered page
  });
  const ref = useRef(null);
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && hasNextPage && !isFetchingNextPage) fetchNextPage();
    }, { rootMargin: '200px' });
    if (ref.current) io.observe(ref.current);
    return () => io.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);
  return (
    <>
      {data.pages.flatMap((p) => p.items).map((i) => <p key={i.id}>{i.title}</p>)}
      <div ref={ref} />
    </>
  );
}
```
(`QueryClientProvider` must wrap the app; TanStack Query v5 details are version-dependent.)

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Listening to `scroll` and measuring layout on every event
✅ **Correct:** Use `IntersectionObserver`, which is asynchronous and does not force layout.

```jsx
// Wrong: runs many times per second
window.onscroll = () => { if (el.getBoundingClientRect().top < innerHeight) loadMore(); }; // ❌

// Right
new IntersectionObserver(([e]) => e.isIntersecting && loadMore()).observe(el);                // ✅
```

❌ **Mistake 2:** Not guarding against duplicate loads, which duplicates items and keys
✅ **Correct:** Use a ref flag (or `isFetchingNextPage`), and unique ids as keys.

```jsx
// Wrong: observer fires twice before state updates → page N loaded twice
const loadMore = async () => { setLoading(true); /* fetch */ };            // ❌ no guard

// Right
if (loadingRef.current) return;                                            // ✅ synchronous guard
loadingRef.current = true;
```

❌ **Mistake 3:** Replacing the list instead of appending, forgetting cleanup, or keeping the observer after `hasMore` is false
✅ **Correct:** `setItems(prev => [...prev, ...new])`, disconnect in cleanup, remove the sentinel at the end. Add try/catch with a `finally` that resets the flag so one failed request does not block loading forever.

```jsx
// Wrong: scroll position jumps back to the top because the list is replaced
setItems(res.items);                                                       // ❌
// Right
setItems((prev) => [...prev, ...res.items]);                               // ✅
// And make the guard failure-safe:
try { /* fetch */ } catch (e) { setError(e); } finally { loadingRef.current = false; } // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Feed() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(0);
  const loadMore = () => {
    fetchPage(page).then((res) => {
      setItems((prev) => [...prev, ...res]);
      setPage(page + 1);                          // uses `page` from the closure
    });
  };
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => e.isIntersecting && loadMore());
    io.observe(sentinel.current);
    return () => io.disconnect();
  }, []);                                         // observer created ONCE
  /* ... */
}
// After scrolling, which page is fetched each time?
```
**Answer:** Always page `0`. The observer was created once on mount, so its callback holds the first render's `loadMore`, which closed over `page = 0`. Each trigger fetches page 0 again and sets `page` to `1` repeatedly, so the list shows duplicate items. This is a **stale closure**. Fixes: recreate the observer when `loadMore` changes (put it in the dependency array, as in `App.jsx`), keep the current page in a ref, or use a functional update and a ref for the page number. Also use a loading guard so two triggers cannot run at once.

---

## ⚫ Interview Questions + Answers

Q1: Why use `IntersectionObserver` instead of the scroll event?
A1: It runs asynchronously off the main scroll path, gives visibility information without forcing layout reads, and fires only when visibility changes. Scroll listeners fire constantly and often cause jank unless throttled.

Q2: What is `rootMargin` used for?
A2: It grows or shrinks the observed area. `rootMargin: '200px'` makes the sentinel count as visible 200 px before it actually enters the viewport, so the next page loads before the user reaches the bottom, which makes scrolling feel seamless.

Q3: How do you avoid loading the same page twice?
A3: Use a synchronous guard (`useRef` flag or the library's `isFetchingNextPage`), update `page` from reliable data, and use unique ids as keys. State alone is not enough because `setLoading(true)` is not applied before a second observer callback.

Q4: Infinite scroll vs pagination: when to use which?
A4: Infinite scroll suits feeds and discovery (social, product browsing) and mobile. Pagination suits tasks where users need to find, compare or return to a position, need a footer, or when SEO and shareable page URLs matter. Hybrid: "Load more" button.

Q5: How do you handle thousands of items without slowing the page?
A5: Virtualise (render only the rows in view, as with `react-window` or TanStack Virtual, topic 209), keep rows light with `React.memo`, use fixed-size images, and cap memory by dropping very old pages in `useInfiniteQuery` (`maxPages`, version-dependent).

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Users browse a long stream without a specific target (feeds, listings)
- Items are similar and cheap to render

❌ **Avoid when:**
- Users need the footer, bookmarkable pages or precise navigation (use pagination)
- Accessibility or SEO of deep items matters and you have no fallback links
- The list is small enough to load at once

---

## 📊 Visual Diagram

```
 ┌───────────────────────────┐
 │ Item 1                    │
 │ Item 2                    │
 │ ...                       │
 │ Item 10                   │   viewport
 │ ─ ─ ─ rootMargin 200px ─ ─│───────────────
 │ [sentinel]  ◀── observed  │
 └───────────────────────────┘
        │ becomes visible
        ▼
  loadMore() ── guard? ──▶ fetch page N ──▶ items = [...items, ...new]
        │                                       │
        └── hasMore=false ──▶ remove sentinel ◀─┘ page++

 Re-render: one for "loading", one for appended items. Existing rows keep their keys,
 so React does not re-create them. Cost grows with list length (virtualise at ~1000+).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IntersectionObserver | Browser API reporting element visibility | Element के दिखने की जानकारी देने वाली API |
| Sentinel | Empty element used as a trigger | Trigger के लिए खाली element |
| rootMargin | Margin around the viewport | Viewport के चारों ओर का margin |
| hasMore | Flag for remaining data | बाकी data का flag |
| Callback ref | A function passed as ref | ref के रूप में दिया function |
| Stale closure | Callback using old values | पुराने values वाला callback |
| Virtualisation | Rendering only visible rows | सिर्फ दिखने वाली rows render करना |
| useInfiniteQuery | TanStack Query hook for paging | Paging के लिए TanStack Query का hook |

---

## ⚡ 3-Line Summary
**English:**
1. Watch a sentinel at the bottom with `IntersectionObserver` and append the next page when it becomes visible.
2. Guard against double fetches with a ref, track `hasMore`, handle errors, and disconnect the observer in cleanup.
3. In Next.js render page one on the server and use `useInfiniteQuery` on the client; virtualise very long lists.

**Hindi:**
1. नीचे के sentinel को `IntersectionObserver` से देखो और दिखते ही अगला page जोड़ दो।
2. ref से double fetch रोको, `hasMore` track करो, errors संभालो और cleanup में observer disconnect करो।
3. Next.js में पहला page server पर render करो और client पर `useInfiniteQuery` लो; बहुत लंबी lists को virtualise करो।

---

## ➡️ Next Topic
**195. Build Modal Component** — Portal, Escape key, overlay click, focus trap और scroll lock के साथ accessible modal।
