# 80. Infinite Scroll in React
# हिंदी में: React में Infinite Scroll — List के अंत पर अपने आप अगला page लोड करना

---

## 🔵 Simple Definition (English)
Infinite scroll ek UI pattern hai jisme user list ke end tak pahunchta hai aur next items apne aap load ho jaate hain. React mein hum list ke neeche ek invisible "sentinel" element rakhte hain aur `IntersectionObserver` se dekhte hain ki woh screen par aaya ya nahi.

## 🔵 सरल परिभाषा (Hindi)
Infinite scroll एक UI pattern है जिसमें user list के अंत तक पहुँचता है और अगली items अपने आप load हो जाती हैं। React में हम list के नीचे एक अदृश्य "sentinel" element रखते हैं और `IntersectionObserver` से देखते हैं कि वह screen पर आया या नहीं।

---

## 🔴 Problem it Solves
Ek saath 10,000 products fetch karna slow hai, memory bharti hai, aur DOM bhari ho jaata hai. "Load more" button se user ko har baar click karna padta hai. Infinite scroll items ko chunks mein load karta hai, jaise hi user neeche scroll karta hai. Lekin isme ek dikkat hai: agar server offset (page number) use karta hai aur data beech mein badal raha hai, to duplicates ya missing items aa sakte hain, isliye cursor-based pagination better hai.

## 🔴 यह क्यों बना? (Hindi)
एक साथ 10,000 products fetch करना धीमा है, memory भरती है, और DOM भारी हो जाता है। "Load more" button पर बार-बार click करना पड़ता है। Infinite scroll items को chunks में load करता है, जैसे-जैसे user नीचे scroll करता है। पर इसमें दिक्कत है: अगर server offset (page number) use करता है और beech में data बदल रहा है, तो duplicates या missing items आ सकते हैं, इसलिए cursor-based pagination बेहतर है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List ke end mein ek sentinel <div ref={sentinelRef} /> rakho
Step 2 → IntersectionObserver se sentinel ko observe karo
Step 3 → Sentinel viewport mein aaye (rootMargin se thoda pehle) → loadMore()
Step 4 → loadMore: loading flag check, API call with cursor, items append karo
Step 5 → Naya cursor save karo; nextCursor null ho to hasMore = false
Step 6 → Component unmount ya deps badle to observer.disconnect() karo
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → List के अंत में एक sentinel <div ref={sentinelRef} /> रखो
Step 2 → IntersectionObserver से sentinel को observe करो
Step 3 → Sentinel viewport में आए (rootMargin से थोड़ा पहले) → loadMore()
Step 4 → loadMore: loading flag check करो, cursor से API call, items append करो
Step 5 → नया cursor save करो; nextCursor null हो तो hasMore = false
Step 6 → Unmount या deps बदलने पर observer.disconnect() करो
```

---

## 🟡 Real World Example
**Flipkart / Amazon product listing:** Category page par user neeche scroll karta hai, aur 20-20 products load hote rahte hain. Har request mein server bataata hai "aakhri product ka id yeh tha, isse aage do". Jab server `nextCursor: null` bhejta hai, to "aur products nahi hain" dikhta hai. Instagram aur Twitter feeds bhi isi tarah kaam karte hain.

## 🟡 Real Example Hindi mein
**Flipkart / Amazon product listing:** Category page पर user नीचे scroll करता है, और 20-20 products load होते रहते हैं। हर request में server बताता है "आखिरी product का id यह था, इसके आगे दो"। जब server `nextCursor: null` भेजता है, तो "और products नहीं हैं" दिखता है। Instagram और Twitter feeds भी इसी तरह काम करते हैं।

---

## 💻 Code Example — Basic

```jsx
import { useEffect, useRef, useState } from 'react';      // hooks we need

// ── BASIC INFINITE SCROLL ─────────────────────────────
function ProductFeed() {
  const [items, setItems] = useState([]);                  // products loaded so far
  const [nextCursor, setNextCursor] = useState(null);      // where the next page starts (null = first page)
  const [hasMore, setHasMore] = useState(true);            // false when the server has no more pages
  const [loading, setLoading] = useState(false);           // blocks duplicate requests
  const sentinelRef = useRef(null);                        // points to the invisible div at the bottom

  async function loadMore() {
    if (loading || !hasMore) return;                       // guard: already busy or finished
    setLoading(true);                                      // show spinner, lock further requests
    const url = nextCursor
      ? `/api/products?limit=20&cursor=${encodeURIComponent(nextCursor)}` // next page
      : '/api/products?limit=20';                          // first page
    const res = await fetch(url);                          // call the API
    const data = await res.json();                         // expected: { items, nextCursor }
    setItems(prev => [...prev, ...data.items]);            // append, never replace
    setNextCursor(data.nextCursor);                        // remember where to continue
    setHasMore(data.nextCursor !== null);                  // null cursor = last page
    setLoading(false);                                     // unlock
  }

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => { // watches elements for visibility
      if (entries[0].isIntersecting) loadMore();           // sentinel visible → load next page
    }, { rootMargin: '200px' });                           // start loading 200px before the bottom
    if (sentinelRef.current) observer.observe(sentinelRef.current); // attach to the sentinel
    return () => observer.disconnect();                    // cleanup on change or unmount
  }, [nextCursor, hasMore, loading]);                      // new observer when state changes

  return (
    <div>
      {items.map(item => (                                 // render each product
        <div key={item.id}>{item.name}</div>               // stable id as the key
      ))}
      {loading && <p>Loading...</p>}                       {/* spinner text */}
      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />} {/* sentinel, removed when done */}
    </div>
  );
}

export default ProductFeed;                                // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useCallback, useEffect, useRef, useState } from 'react';  // hooks

// Custom hook: reusable infinite-list logic with cursor, dedupe, abort and errors
function useInfiniteList(endpoint, pageSize = 20) {
  const [items, setItems] = useState([]);                  // deduplicated list
  const [cursor, setCursor] = useState(null);              // server cursor for the next page
  const [hasMore, setHasMore] = useState(true);            // are there more pages?
  const [loading, setLoading] = useState(false);           // drives the UI spinner
  const [error, setError] = useState(null);                // last error message, if any
  const inFlight = useRef(false);                          // sync lock (state is async, refs are not)
  const controllerRef = useRef(null);                      // AbortController of the current request

  const loadMore = useCallback(async () => {
    if (inFlight.current || !hasMore) return;              // ignore duplicate or finished calls
    inFlight.current = true;                               // lock right away
    setLoading(true);                                      // UI: show spinner
    setError(null);                                        // clear the previous error
    const controller = new AbortController();              // lets us cancel this request
    controllerRef.current = controller;                    // store it for unmount cleanup
    try {
      const qs = new URLSearchParams({ limit: String(pageSize) }); // build ?limit=20
      if (cursor) qs.set('cursor', cursor);                // add the cursor after the first page
      const res = await fetch(`${endpoint}?${qs}`, { signal: controller.signal }); // request
      if (!res.ok) throw new Error(`HTTP ${res.status}`);  // turn 4xx/5xx into an error
      const data = await res.json();                       // { items, nextCursor }
      setItems(prev => {                                   // merge safely with the old list
        const seen = new Set(prev.map(p => p.id));         // ids we already have
        const fresh = data.items.filter(p => !seen.has(p.id)); // drop duplicates
        return [...prev, ...fresh];                        // append only new items
      });
      setCursor(data.nextCursor);                          // remember the next cursor
      setHasMore(data.nextCursor != null);                 // null or undefined = no more pages
    } catch (err) {
      if (err.name !== 'AbortError') setError(err.message); // ignore cancels, show real errors
    } finally {
      inFlight.current = false;                            // unlock
      setLoading(false);                                   // UI: hide spinner
    }
  }, [endpoint, pageSize, cursor, hasMore]);               // identity changes when cursor changes

  useEffect(() => () => controllerRef.current?.abort(), []); // abort the in-flight request on unmount

  return { items, loadMore, hasMore, loading, error };     // expose what the UI needs
}

export function Feed() {
  const { items, loadMore, hasMore, loading, error } = useInfiniteList('/api/products'); // use the hook
  const sentinel = useRef(null);                           // bottom marker element

  useEffect(() => {
    const el = sentinel.current;                           // element to watch
    if (!el) return;                                       // not rendered (no more pages)
    const io = new IntersectionObserver(([entry]) => {     // first entry belongs to our sentinel
      if (entry.isIntersecting) loadMore();                // near the bottom → fetch next page
    }, { rootMargin: '200px' });                           // prefetch 200px early
    io.observe(el);                                        // start watching
    return () => io.disconnect();                          // cleanup
  }, [loadMore]);                                          // recreate when loadMore changes

  return (
    <div>
      <ul>{items.map(p => <li key={p.id}>{p.name} — ₹{p.price}</li>)}</ul> {/* keyed list */}
      {loading && <p>Loading more…</p>}                    {/* spinner */}
      {error && <button onClick={loadMore}>Retry ({error})</button>} {/* retry after failure */}
      {hasMore && <div ref={sentinel} />}                  {/* the element we watch */}
    </div>
  );
}
```

---

## 🟠 Real app integration

Express cursor endpoint (keyset pagination, so newly added rows never shift the pages):

```javascript
const express = require('express');                        // web framework
const app = express();                                     // create the app
// db is a pg Pool instance created elsewhere, e.g. const { Pool } = require('pg')

app.get('/api/products', async (req, res) => {             // GET /api/products?limit=&cursor=
  const limit = Math.min(Number(req.query.limit) || 20, 50); // default 20, hard cap 50
  const cursor = req.query.cursor ? Number(req.query.cursor) : null; // last seen id
  if (req.query.cursor && !Number.isInteger(cursor)) {     // validate untrusted input
    return res.status(400).json({ error: 'Bad cursor' });  // 400 Bad Request
  }
  const { rows } = await db.query(                         // pg returns { rows }
    `SELECT id, name, price FROM products
     WHERE ($1::int IS NULL OR id < $1)                    -- no cursor = first page
     ORDER BY id DESC
     LIMIT $2`,                                            // parameterized, no SQL injection
    [cursor, limit + 1]                                    // ask for ONE extra row
  );
  const hasMore = rows.length > limit;                     // the extra row proves more pages exist
  const items = rows.slice(0, limit);                      // return only what was requested
  const nextCursor = hasMore ? items[items.length - 1].id : null; // last id becomes the cursor
  res.json({ items, nextCursor });                         // { items, nextCursor }
});
```

Next.js App Router (first page on the server for SEO, then the client keeps loading):

```jsx
// app/products/page.js — Server Component (no 'use client' here)
import { getProducts } from '@/lib/products';              // your data helper that calls the DB
import ProductFeed from './ProductFeed';                   // a Client Component with the observer

export default async function Page() {                     // runs on the server
  const { items, nextCursor } = await getProducts({ limit: 20 }); // first batch, rendered in HTML
  return <ProductFeed initialItems={items} initialCursor={nextCursor} />; // hand data to the client
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Offset pagination with live data (duplicates or missing items)
✅ **Correct:** Use a cursor (last seen id or timestamp).

```javascript
// Wrong: rows inserted at the top shift every offset
fetch(`/api/products?offset=${items.length}`);         // ❌ same item can appear twice

// Right: ask for "items after this id"
fetch(`/api/products?cursor=${lastItem.id}`);          // ✅ stable position
```

❌ **Mistake 2:** No loading guard, so several requests fire while the sentinel stays visible
✅ **Correct:** Lock with a flag or a ref before you start a request.

```jsx
// Wrong: every intersection callback starts a new request
const io = new IntersectionObserver(([e]) => {
  if (e.isIntersecting) fetchNext();                   // ❌ runs again and again
});

// Right: ignore calls while a request is in flight
const inFlight = useRef(false);                        // lives across renders
const io2 = new IntersectionObserver(([e]) => {
  if (e.isIntersecting && !inFlight.current) fetchNext(); // ✅ one request at a time
});
```

❌ **Mistake 3:** Effect with `[]` deps that captures an old `loadMore` (always loads page 1)
✅ **Correct:** Put the values the handler reads into the deps, or use a ref.

```jsx
// Wrong: the observer keeps the FIRST render's loadMore, cursor is always null
useEffect(() => {
  const io = new IntersectionObserver(([e]) => e.isIntersecting && loadMore());
  io.observe(sentinel.current);
  return () => io.disconnect();
}, []);                                                // ❌ stale closure

// Right: re-subscribe when loadMore (and so the cursor) changes
useEffect(() => {
  const io = new IntersectionObserver(([e]) => e.isIntersecting && loadMore());
  io.observe(sentinel.current);
  return () => io.disconnect();
}, [loadMore]);                                        // ✅ fresh closure each time
```

---

## 🧠 Tricky Interview Question

```jsx
function AutoLoader() {
  const [cursor, setCursor] = useState(0);             // page cursor state
  const [items, setItems] = useState([]);              // loaded values
  useEffect(() => {
    const id = setInterval(() => {                     // "load" every second
      setItems(prev => [...prev, cursor]);             // which cursor is this?
      setCursor(c => c + 1);                           // move the cursor forward
    }, 1000);
    return () => clearInterval(id);                    // cleanup
  }, []);                                              // effect runs only once
  return <p>{items.join(',')} / cursor={cursor}</p>;
}
// What does the screen show after 3 seconds?
```

**Answer:** `0,0,0 / cursor=3`. The effect runs once, on the first render, when `cursor` is `0`. The arrow function inside `setInterval` closes over that first `cursor` value (`0`) and never sees later renders. The updater `c => c + 1` is different: React passes it the latest state, so `cursor` goes 1, 2, 3. The items array therefore gets `0` three times. This is the stale closure bug. Fix it by reading the state through the updater (`setItems(prev => [...prev, c])` inside a `setCursor` updater is awkward), or by putting `cursor` in the deps, or by using a ref.

---

## ⚫ Interview Questions + Answers

**Q1: How does infinite scroll detect that the user reached the bottom?**
A1: A sentinel element sits at the bottom of the list. `IntersectionObserver` calls back when the sentinel enters the viewport (or the `rootMargin` area). That is cheaper than a `scroll` listener, because the browser does the checks off the main thread.

**Q2: Why use cursor pagination instead of offset for infinite scroll?**
A2: Offset (`OFFSET 40`) depends on how many rows came before, so inserts or deletes between requests shift the pages and cause duplicates or gaps. A cursor (`WHERE id < lastId`) points to a real row, so the next page is stable.

**Q3: How do you stop duplicate requests?**
A3: Keep an in-flight flag in a `ref` (sync), not only in state, because state updates are asynchronous. Check it at the top of `loadMore`. Also dedupe the merged items by `id` in case the server repeats a row.

**Q4: What happens when the component unmounts during a request?**
A4: Abort it with `AbortController` in the cleanup. Otherwise the promise resolves later and calls `setState` on an unmounted component, which wastes work and can apply stale data.

**Q5: Why is `rootMargin` useful?**
A5: It makes the observer fire before the sentinel is really visible, for example `200px` early. The next page is already loading by the time the user reaches the end, so the scroll feels smooth.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Users browse long, append-only lists (feeds, search results, product catalogs)
- Items are fetched from an API with a cursor or a "next" token
- Scrolling is the main way to explore (social feeds, galleries)

❌ **Avoid when:**
- Users need to jump to a page or find a footer (footer is unreachable, use numbered pagination)
- The list is short (fetch it all at once)
- Users need to keep their position while going back to a page: infinite scroll loses it unless you save the cursor and scroll offset

---

## 📊 Visual Diagram

```
Screen (viewport)
┌──────────────────────────────┐
│ Product 1                    │
│ Product 2                    │
│ ...                          │
│ Product 20                   │
│ Loading...                   │   ← loading flag shows spinner
│ ┌──────────────────────────┐ │
│ │ sentinel (1px div)       │ │   ← IntersectionObserver watches this
│ └──────────────────────────┘ │
└──────────────────────────────┘
          │  sentinel enters viewport (+200px rootMargin)
          ▼
   loadMore(cursor = 20)  ──►  GET /api/products?cursor=20
          │                         │
          ◄─────────────────────────┘  { items: [21..40], nextCursor: 40 }
   append items, save cursor = 40, repeat until nextCursor === null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sentinel | List ke end par invisible element jo visibility batata hai | List के अंत का अदृश्य element |
| IntersectionObserver | Element viewport mein aaya ya nahi, batane wala browser API | Element viewport में आया या नहीं, बताने वाला API |
| Cursor | Last seen item ka marker jisse next page shuru hota hai | आखिरी देखे item का marker |
| Offset | Kitne rows skip karne hain, ek number | कितनी rows skip करनी हैं |
| rootMargin | Observer ka extra area, pehle load shuru karne ke liye | Observer का extra area |
| Dedupe | Same id ke duplicate items hatana | एक जैसे id वाले duplicates हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. Ek sentinel element list ke end par rakho aur `IntersectionObserver` se use watch karo.
2. Cursor pagination use karo, guard flag se duplicate requests roko, aur unmount par abort karo.
3. Observer effect ke deps sahi rakho, warna stale closure se hamesha page 1 load hoga.

**Hindi:**
1. List के अंत पर एक sentinel element रखो और `IntersectionObserver` से उसे watch करो।
2. Cursor pagination इस्तेमाल करो, guard flag से duplicate requests रोको, और unmount पर abort करो।
3. Observer effect के deps सही रखो, वरना stale closure से हमेशा page 1 load होगा।

---

## ➡️ Next Topic
**81. Pagination in React** — numbered pages, page state, URL sync, aur server-side limit/offset ya cursor का फर्क।
