# 106. Data Fetching in React — Complete Guide
# हिंदी में: React में Data Fetching — पूरी Guide

---

## 🔵 Simple Definition (English)
**Data fetching** in React means loading data from an API/server and displaying it in components. The standard React approach uses `useEffect` + `fetch`/`axios` + state (loading/error/data). Modern alternatives: React Query, SWR, or Next.js Server Components (fetch on server directly).

## 🔵 सरल परिभाषा (Hindi)
React में **Data fetching** का मतलब है API/server से data load करके components में display करना। Standard React approach: `useEffect` + `fetch`/`axios` + state (loading/error/data)। Modern alternatives: React Query, SWR, या Next.js Server Components (server पर directly fetch)।

---

## 🔴 Problem it Solves
```jsx
// CHALLENGE: Async data doesn't fit React's synchronous render cycle
// You can't: const data = await fetch('/api') inside JSX directly!
// Must: request → wait → update state → React re-renders with data
// Also must handle: loading state, errors, race conditions, caching
```

---

## 🟢 How it Works — Step by Step

```
BASIC PATTERN:
Step 1 → Component renders (shows loading)
Step 2 → useEffect fires after render
Step 3 → fetch('/api/data') call
Step 4 → Response comes back
Step 5 → setState({ data, loading: false })
Step 6 → Component re-renders with data

CHALLENGES to handle:
- Loading state: show spinner
- Error state: show error message
- Race condition: old response arrives after new one
- Cleanup: component unmounts before fetch completes
- Caching: don't refetch same data
```

---

## 🟡 Real World Example
**Amazon Product Listing:** Page loads → immediately show skeleton cards (loading state). Behind the scenes, fetch products from API. If fetch fails, show "Unable to load products, try again." If succeeds, show product cards. Each card might trigger another fetch for reviews/ratings.

---

## 💻 Code Example — Basic

```jsx
import { useState, useEffect } from 'react';

// ── BASIC DATA FETCHING PATTERN ───────────
function ProductList({ category }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset state on category change
    setLoading(true);
    setError(null);
    setProducts([]);

    const controller = new AbortController(); // for cleanup

    fetch(`/api/products?category=${category}`, {
      signal: controller.signal
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        setProducts(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return; // cleanup — ignore
        setError(err.message);
        setLoading(false);
      });

    // CLEANUP: abort fetch if category changes before fetch completes
    return () => controller.abort();

  }, [category]); // re-fetch when category changes

  // Loading state
  if (loading) {
    return (
      <div className="grid">
        {[1, 2, 3, 4, 6].map(n => (
          <div key={n} className="skeleton-card">Loading...</div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="error">
        <p>❌ Failed to load products: {error}</p>
        <button onClick={() => setLoading(true)}>Try Again</button>
      </div>
    );
  }

  // Empty state
  if (products.length === 0) {
    return <p>No products found in {category}.</p>;
  }

  // Success state
  return (
    <div className="grid">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useEffect, useCallback, useRef } from 'react';

// ── CUSTOM HOOK: useFetch ─────────────────
// Reusable — works for any URL
function useFetch(url) {
  const [state, setState] = useState({
    data: null,
    loading: !!url, // false if no URL
    error: null,
  });

  useEffect(() => {
    if (!url) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    setState(s => ({ ...s, loading: true, error: null }));
    const controller = new AbortController();

    fetch(url, { signal: controller.signal })
      .then(res => res.ok ? res.json() : Promise.reject(new Error(`${res.status}`)))
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => {
        if (err.name !== 'AbortError') {
          setState({ data: null, loading: false, error: err.message });
        }
      });

    return () => controller.abort();
  }, [url]);

  return state;
}

// ── PAGINATION ───────────────────────────
function PaginatedList({ pageSize = 10 }) {
  const [page, setPage] = useState(1);
  const { data, loading, error } = useFetch(
    `/api/products?page=${page}&limit=${pageSize}`
  );

  return (
    <div>
      {loading && <Spinner />}
      {error && <ErrorBanner message={error} />}

      {data?.products.map(p => <ProductCard key={p.id} product={p} />)}

      <div className="pagination">
        <button
          onClick={() => setPage(p => p - 1)}
          disabled={page === 1 || loading}
        >
          ← Previous
        </button>
        <span>Page {page} of {data?.totalPages}</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={page === data?.totalPages || loading}
        >
          Next →
        </button>
      </div>
    </div>
  );
}

// ── INFINITE SCROLL ───────────────────────
function InfiniteProductList({ category }) {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const loaderRef = useRef(null);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    setLoading(true);

    try {
      const res = await fetch(`/api/products?category=${category}&page=${page}`);
      const data = await res.json();
      setProducts(prev => [...prev, ...data.products]);
      setHasMore(data.hasNextPage);
      setPage(p => p + 1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [category, page, loading, hasMore]);

  // Load first page on mount + category change
  useEffect(() => {
    setProducts([]);
    setPage(1);
    setHasMore(true);
  }, [category]);

  // Trigger loadMore when initial reset happens
  useEffect(() => {
    if (products.length === 0 && hasMore) loadMore();
  }, [products.length]);

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => { if (entries[0].isIntersecting) loadMore(); },
      { threshold: 1 }
    );
    const el = loaderRef.current;
    if (el) observer.observe(el);
    return () => { if (el) observer.unobserve(el); };
  }, [loadMore]);

  return (
    <div>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
      {loading && <Spinner />}
      {hasMore && <div ref={loaderRef} style={{ height: 20 }} />}
      {!hasMore && <p>All products loaded!</p>}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// React: fetch in useEffect (client-side) → bad for SEO, loading state
// Next.js Server Components: fetch on server → HTML with data → perfect SEO

// ── SERVER COMPONENT — preferred for initial data ──
// app/products/page.jsx
async function ProductsPage({ searchParams }) {
  // This runs on SERVER — no useEffect, no loading state!
  const products = await fetch(
    `https://api.example.com/products?category=${searchParams.category || 'all'}`,
    {
      cache: 'force-cache',          // SSG: cache forever
      // next: { revalidate: 60 }    // ISR: revalidate every 60s
      // cache: 'no-store'           // SSR: fresh every request
    }
  ).then(r => r.json());

  return (
    <div>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}

// ── CLIENT COMPONENT — for user-triggered fetches ──
'use client';
function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  // User-triggered fetch = client side
  const search = async (q) => {
    const data = await fetch(`/api/search?q=${q}`).then(r => r.json());
    setResults(data);
  };

  return (
    <div>
      <input onChange={e => search(e.target.value)} />
      {results.map(r => <div key={r.id}>{r.name}</div>)}
    </div>
  );
}

// ── PARALLEL FETCHING (Server Component) ──
async function Dashboard() {
  // Fetch in parallel — not sequentially!
  const [user, orders, recommendations] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/orders').then(r => r.json()),
    fetch('/api/recommendations').then(r => r.json()),
  ]);

  return (
    <div>
      <UserHeader user={user} />
      <OrderList orders={orders} />
      <RecommendationGrid items={recommendations} />
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Fetching without cleanup (race condition)
```jsx
// WRONG: if userId changes quickly, old response might arrive last!
useEffect(() => {
  fetch(`/api/users/${userId}`)
    .then(r => r.json())
    .then(setUser); // ❌ might be stale response!
}, [userId]);

// CORRECT: use AbortController
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setUser)
    .catch(e => { if (e.name !== 'AbortError') setError(e.message); });
  return () => controller.abort(); // ✅ cancel on userId change
}, [userId]);
```

❌ **Mistake 2:** Using useEffect for everything in Next.js
```jsx
// WRONG in Next.js: unnecessary client-side fetch
'use client';
function ProductPage({ params }) {
  const [product, setProduct] = useState(null);
  useEffect(() => {
    fetch(`/api/products/${params.id}`).then(r => r.json()).then(setProduct);
  }, [params.id]); // ❌ client-side fetch = no SEO, loading flash

  return product ? <div>{product.name}</div> : <Spinner />;
}

// CORRECT in Next.js: Server Component
async function ProductPage({ params }) {
  const product = await fetch(`/api/products/${params.id}`).then(r => r.json());
  return <div>{product.name}</div>; // ✅ in HTML from start, SEO perfect
}
```

---

## 🧠 Tricky Interview Question

```jsx
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch('/api/users')
      .then(r => r.json())
      .then(data => setUsers(data));
  }, []); // empty deps

  useEffect(() => {
    console.log('Users updated:', users.length);
  }, [users]);

  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
// How many times does "Users updated:" log?
```
**Answer:** Twice — once on mount (users = [], length 0) and once when fetch completes (users = [...], length N). The second `useEffect` runs whenever `users` changes. Initial render: `users = []` → logs "Users updated: 0". After fetch: `users = [...]` → logs "Users updated: N".

---

## ⚫ Interview Questions + Answers

**Q1: What is the standard pattern for data fetching in React?**
A1: `useEffect` + fetch + three state pieces: `const [data, setData] = useState(null)`, `const [loading, setLoading] = useState(true)`, `const [error, setError] = useState(null)`. In useEffect: set loading, fetch, on success set data+loading=false, on error set error+loading=false. Always add AbortController for cleanup. Return cleanup function in useEffect.

**Q2: What is a race condition in data fetching and how do you prevent it?**
A2: A race condition occurs when multiple fetches are in-flight simultaneously and responses arrive out of order. Example: user clicks product A (fetch starts), then product B (fetch starts) — if A's response arrives after B's, stale data shows. Prevention: `AbortController` — on each dependency change, abort the previous request so only the latest completes. Alternative: `ignore` flag — `let ignore = false; fetch().then(d => { if (!ignore) setState(d); }); return () => { ignore = true; }`.

**Q3: What are the benefits of React Query / SWR over manual useEffect fetching?**
A3: React Query and SWR provide: automatic caching (same URL → same data, no duplicate requests), background refetching (stale-while-revalidate), loading/error states built-in, request deduplication (multiple components requesting same URL = one fetch), retry on error, pagination/infinite scroll helpers, devtools. Manual `useEffect` requires reimplementing all these. Use libraries for production data fetching.

**Q4: What is the difference between `cache: 'force-cache'` and `cache: 'no-store'` in Next.js fetch?**
A4: `force-cache` (default in Next.js): response is cached indefinitely — fetched once at build time or first request, served from cache thereafter. Good for static data (product catalog, blog posts). `no-store`: no caching — fresh fetch every request. Good for user-specific or frequently changing data. `next: { revalidate: 60 }` is ISR — serve cache but revalidate in background every 60s.

**Q5: What is Suspense and how does it change data fetching?**
A5: React Suspense lets components "wait" for async data before rendering, showing a fallback in the meantime. Instead of managing loading state manually, you throw a Promise (or use a Suspense-compatible library like React Query). `<Suspense fallback={<Spinner />}><LazyComponent /></Suspense>` — if LazyComponent isn't ready, React shows Spinner. Next.js Server Components with `async/await` integrate with Suspense automatically — `<Suspense>` can wrap async server components for streaming.

---

## 🔷 When to Use + When Not to Use
✅ **useEffect + fetch when:**
- Client-side data fetching in React (SPA)
- User-triggered fetches (search, filter)
- Real-time updates (polling)

✅ **Next.js Server Components when:**
- Initial page data (SEO-critical)
- Static or rarely-changing data
- Authenticated data (fetch server-side, no token in browser)

✅ **React Query / SWR when:**
- Complex caching needs
- Background refetching
- Multiple components sharing same data

---

## 📊 Visual Diagram

```
REACT DATA FETCHING FLOW:
──────────────────────────────────────────────
  Component mounts
       │
       ▼
  Render with loading=true (shows Spinner)
       │
       ▼
  useEffect fires (after paint)
       │
       ▼
  fetch('/api/data')
       │
       ├── SUCCESS → setState({data, loading:false})
       │                  │
       │                  ▼
       │             Re-render with data ✅
       │
       └── ERROR → setState({error, loading:false})
                        │
                        ▼
                   Re-render with error ❌

NEXT.JS SERVER COMPONENT:
──────────────────────────────────────────────
  Request hits Next.js server
       │
       ▼
  Server Component runs (async)
       │
       ▼
  await fetch('/api/data')  ← on server!
       │
       ▼
  Component renders with data
       │
       ▼
  HTML (with data) sent to browser
  → No loading state, instant content, SEO ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Data fetching | Loading data from server/API | Server/API से data load करना |
| Loading state | UI while data loads | Data load होते समय UI |
| Error state | UI when fetch fails | Fetch fail होने पर UI |
| Race condition | Stale response arrives too late | Stale response देर से आना |
| AbortController | Cancel in-flight fetch | चल रहे fetch को cancel करना |
| Caching | Store response for reuse | Response store करना reuse के लिए |
| ISR | Incremental Static Regeneration | Incremental Static Regeneration |

---

## ⚡ 3-Line Summary
**English:**
1. React data fetching: `useEffect` + `fetch` + three states (loading, error, data) — always add `AbortController` cleanup for race condition prevention.
2. Next.js Server Components: `async/await` directly in component — no useEffect, no loading state, HTML with data from server = perfect SEO.
3. For production React apps: use React Query or SWR for caching, deduplication, background refetching, and retry logic.

**Hindi:**
1. React data fetching: `useEffect` + `fetch` + तीन states (loading, error, data) — race condition के लिए हमेशा `AbortController` cleanup add करो।
2. Next.js Server Components: component में directly `async/await` — useEffect नहीं, loading state नहीं, server से HTML with data = perfect SEO।
3. Production React apps के लिए: React Query या SWR use करो — caching, deduplication, background refetching, और retry logic के लिए।

---

## ➡️ Next Topic
**107. React Query — Data Fetching Library** — React Query से data fetching — caching, background updates, और optimistic updates।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Data Fetching](https://www.youtube.com/results?search_query=data+fetching+react+akshay+saini) | Data fetching in Hindi |
| 📺 YouTube | [TkDodo — React Query](https://www.youtube.com/results?search_query=react+query+tkdodo+tutorial) | React Query best practices |
| 📝 Docs | [tanstack.com/query](https://tanstack.com/query) | React Query official docs |
| 📝 Article | [react.dev — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) | Official fetching guide |
