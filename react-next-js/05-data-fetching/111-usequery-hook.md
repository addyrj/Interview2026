# 111. useQuery Hook
# हिंदी में: useQuery Hook — Server Data Fetch और Cache करना (TanStack Query v5)

---

## 🔵 Simple Definition (English)
**`useQuery`** is the main hook of TanStack Query (React Query) v5 for **reading** server data. You give it a `queryKey` and a `queryFn`; it fetches, caches, retries, refetches and returns `data`, `isPending`, `isError`, `error`, `isFetching` and more.

## 🔵 सरल परिभाषा (Hindi)
**`useQuery`** TanStack Query (React Query) v5 का मुख्य hook है जो server का data **पढ़ने** के लिए है। आप `queryKey` और `queryFn` देते हो; यह fetch, cache, retry और refetch करता है और `data`, `isPending`, `isError`, `error`, `isFetching` वगैरह देता है।

---

## 🔴 Problem it Solves

With `useEffect` + `fetch`, you write the same code in every component: `loading`, `error`, `data` states, cleanup for race conditions, no caching (every mount refetches), no retry, no refetch on window focus, no deduplication when two components request the same URL.

```jsx
// PROBLEM: manual fetching boilerplate, repeated everywhere
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
useEffect(() => {
  let cancelled = false;                         // race condition guard
  fetch('/api/restaurants').then(r => r.json())
    .then(d => { if (!cancelled) setData(d); })
    .catch(e => { if (!cancelled) setError(e); })
    .finally(() => { if (!cancelled) setLoading(false); });
  return () => { cancelled = true; };
}, []);

// SOLUTION: one line, with cache, retry, dedupe
const { data, isPending, error } = useQuery({ queryKey: ['restaurants'], queryFn: fetchRestaurants });
```

## 🔴 यह क्यों बना? (Hindi)
`useEffect` + `fetch` में हर component में वही code लिखना पड़ता है: `loading`, `error`, `data` states, race condition का cleanup, कोई caching नहीं (हर mount पर दोबारा fetch), कोई retry नहीं, window focus पर refetch नहीं, और दो components एक ही URL माँगें तो deduplication नहीं। `useQuery` ये सब एक जगह देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap the app in <QueryClientProvider client={queryClient}> (once, at the root)
Step 2 → Call useQuery({ queryKey, queryFn }) in any component
Step 3 → queryKey identifies the data in the cache (e.g. ['restaurant', id])
Step 4 → If the cache has the key → return cached data immediately; refetch if it is stale
Step 5 → If not → status 'pending', run queryFn (a function returning a Promise)
Step 6 → On success → status 'success', data is stored in the cache and shared by all subscribers
Step 7 → On error → retried 3 times by default (exponential backoff), then status 'error'
Step 8 → Refetches automatically on: window focus, reconnect, component mount (if stale)

v5 notes: isLoading = isFetching && isPending; 'cacheTime' was renamed 'gcTime';
          only the object signature useQuery({ ... }) is supported; no onSuccess/onError callbacks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App को <QueryClientProvider client={queryClient}> में wrap करो (root पर एक बार)
Step 2 → किसी भी component में useQuery({ queryKey, queryFn }) call करो
Step 3 → queryKey cache में data की पहचान है (जैसे ['restaurant', id])
Step 4 → Cache में key है → data तुरंत मिलता है; stale हो तो refetch होता है
Step 5 → नहीं है → status 'pending', queryFn (Promise return करने वाला function) चलता है
Step 6 → Success पर → status 'success', data cache में जाता है और सभी subscribers के साथ share होता है
Step 7 → Error पर → default 3 बार retry (exponential backoff), फिर status 'error'
Step 8 → अपने आप refetch होता है: window focus, reconnect, mount (अगर stale) पर

v5 notes: isLoading = isFetching && isPending; 'cacheTime' का नाम अब 'gcTime' है;
          सिर्फ object signature useQuery({ ... }) चलता है; onSuccess/onError callbacks नहीं हैं
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** The restaurant header, menu and reviews widgets all need `['restaurant', 42]`. Without a query library each widget would fetch separately. With `useQuery`, the first call fetches, the others reuse the same in-flight request, going back to the page shows cached data instantly while a background refresh updates it, and switching browser tabs triggers a refetch so prices stay current.

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** Restaurant header, menu और reviews widgets सबको `['restaurant', 42]` चाहिए। Query library के बिना हर widget अलग fetch करता। `useQuery` में पहला call fetch करता है, बाकी वही in-flight request reuse करते हैं, page पर वापस आने पर cached data तुरंत दिखता है और background में refresh होता है, और browser tab बदलने पर refetch होता है ताकि prices ताज़ा रहें।

---

## 💻 Code Example — Basic

```jsx
// Basic useQuery (TanStack Query v5)
// npm install @tanstack/react-query
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'; // v5 imports
import { createRoot } from 'react-dom/client';                // React 18/19 root API

const queryClient = new QueryClient();                         // one client = one cache for the app

async function fetchRestaurants() {                            // queryFn: must return a Promise
  const res = await fetch('https://jsonplaceholder.typicode.com/users'); // demo public API
  if (!res.ok) throw new Error('Network error');               // fetch does NOT throw on 404/500, so we do
  return res.json();                                           // resolved value becomes `data`
}

function Restaurants() {
  const { data, isPending, isError, error } = useQuery({      // v5: single object argument
    queryKey: ['restaurants'],                                 // cache key
    queryFn: fetchRestaurants,                                 // how to fetch
  });

  if (isPending) return <p>Loading...</p>;                     // no data yet
  if (isError) return <p>Error: {error.message}</p>;           // after retries failed
  return (
    <ul>
      {data.map((r) => <li key={r.id}>{r.name}</li>)}          {/* data is defined here */}
    </ul>
  );
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}>                   {/* make the client available */}
    <Restaurants />
  </QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: dynamic key, options, select, enabled (dependent query), placeholderData, AbortSignal
import { useState } from 'react';                              // local UI state
import { useQuery, keepPreviousData } from '@tanstack/react-query'; // v5 helper for pagination

// queryFn receives a context with `signal` → pass to fetch so cancelled queries abort the request
async function fetchOrders({ page, status }, signal) {
  const res = await fetch(`/api/orders?page=${page}&status=${status}`, { signal });
  if (!res.ok) throw new Error(`Orders failed: ${res.status}`);
  return res.json();                                           // { items: [], totalPages: n }
}

async function fetchOrderDetail(id, signal) {
  const res = await fetch(`/api/orders/${id}`, { signal });
  if (!res.ok) throw new Error('Detail failed');
  return res.json();
}

export function OrdersPage() {
  const [page, setPage] = useState(1);                         // current page
  const [status, setStatus] = useState('delivered');           // filter
  const [selectedId, setSelectedId] = useState(null);          // clicked order

  const orders = useQuery({
    queryKey: ['orders', { page, status }],                    // key includes ALL variables the fn uses
    queryFn: ({ signal }) => fetchOrders({ page, status }, signal), // signal enables cancellation
    staleTime: 30_000,                                         // fresh for 30s → no refetch on remount
    placeholderData: keepPreviousData,                         // v5: keep old page visible while loading next
    select: (d) => ({ ...d, items: d.items.filter((o) => !o.hidden) }), // transform without extra state
  });

  const detail = useQuery({
    queryKey: ['order', selectedId],                           // different key per order
    queryFn: ({ signal }) => fetchOrderDetail(selectedId, signal),
    enabled: selectedId !== null,                              // dependent query: run only when selected
  });

  return (
    <div>
      <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
        <option value="delivered">Delivered</option>           {/* changing status = new key = new fetch */}
        <option value="cancelled">Cancelled</option>
      </select>

      {orders.isPending ? <p>Loading orders...</p> : orders.isError ? (
        <p role="alert">{orders.error.message} <button onClick={() => orders.refetch()}>Retry</button></p>
      ) : (
        <ul style={{ opacity: orders.isPlaceholderData ? 0.5 : 1 }}> {/* dim while next page loads */}
          {orders.data.items.map((o) => (
            <li key={o.id} onClick={() => setSelectedId(o.id)}>{o.restaurant}</li>
          ))}
        </ul>
      )}

      <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>Prev</button>
      <button
        disabled={orders.isPlaceholderData || page >= (orders.data?.totalPages ?? 1)}
        onClick={() => setPage((p) => p + 1)}
      >Next</button>
      {orders.isFetching && <small> refreshing...</small>}     {/* background fetch indicator */}

      {detail.data && <aside>Total: ₹{detail.data.total}</aside>} {/* shown when detail query succeeds */}
    </div>
  );
}
```

Re-render behavior: `useQuery` re-renders the component when tracked fields change (`data`, `isPending`, `isFetching`, ...). React Query tracks which fields you actually read, so reading only `data` will not re-render for `isFetching` changes. Performance impact: the key idea is that components sharing a key share one network request and one cache entry.

---

## 🟠 Next.js Connection

In the App Router, `useQuery` runs only in Client Components. To avoid a loading spinner on first paint, prefetch on the server and **hydrate** the cache (the documented v5 pattern with `HydrationBoundary` and `dehydrate`).

```jsx
// app/providers.jsx
'use client';                                                  // provider uses state → Client Component
import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export default function Providers({ children }) {
  const [client] = useState(() => new QueryClient({           // create ONCE per browser session
    defaultOptions: { queries: { staleTime: 60_000 } },       // avoid refetch right after hydration
  }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
```

```jsx
// app/restaurants/page.jsx (Server Component)
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query';
import RestaurantsClient from './RestaurantsClient';          // 'use client' file that calls useQuery

async function getRestaurants() {                              // runs on the server
  const res = await fetch('https://example.com/api/restaurants'); // placeholder URL
  return res.json();
}

export default async function Page() {
  const queryClient = new QueryClient();                       // per-request client on the server
  await queryClient.prefetchQuery({                            // fill the cache before sending HTML
    queryKey: ['restaurants'],                                 // MUST match the client's key
    queryFn: getRestaurants,
  });
  return (
    <HydrationBoundary state={dehydrate(queryClient)}>         {/* ships cache to the browser */}
      <RestaurantsClient />                                    {/* useQuery(['restaurants']) finds data instantly */}
    </HydrationBoundary>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Leaving out a variable from the `queryKey`
✅ **Correct:** Every variable used by `queryFn` must be in the key

```jsx
// Wrong: all pages share one cache entry → wrong data / no refetch when page changes
useQuery({ queryKey: ['orders'], queryFn: () => fetchOrders(page) });          // ❌

// Right
useQuery({ queryKey: ['orders', page], queryFn: () => fetchOrders(page) });    // ✅
```

❌ **Mistake 2:** Not throwing on HTTP errors inside `queryFn`
✅ **Correct:** `fetch` only rejects on network failure; check `res.ok` (axios throws automatically)

```jsx
// Wrong: 500 response is treated as a success; data = error JSON
queryFn: () => fetch('/api/x').then((r) => r.json()),                          // ❌

// Right
queryFn: async () => {
  const r = await fetch('/api/x');
  if (!r.ok) throw new Error(r.statusText);                                    // ✅ marks the query as error
  return r.json();
},
```

❌ **Mistake 3:** Copying `data` into `useState` (two sources of truth)
✅ **Correct:** Use `data` directly, or `select` to derive

```jsx
// Wrong: local copy never updates after refetch
const { data } = useQuery({ queryKey: ['u'], queryFn: getUser });
const [user, setUser] = useState(data);                                        // ❌ stale copy

// Right
const { data: user } = useQuery({ queryKey: ['u'], queryFn: getUser });       // ✅ single source of truth
```

---

## 🧠 Tricky Interview Question

```jsx
import { useQuery } from '@tanstack/react-query';

function User({ id }) {
  const { data, isLoading, isPending } = useQuery({
    queryKey: ['user', id],
    queryFn: () => fetch(`/api/users/${id}`).then((r) => r.json()),
    enabled: false,                                // query is disabled
  });
  console.log({ isLoading, isPending });           // what is logged on first render?
  return <p>{data?.name}</p>;
}
```
**Answer:** `{ isLoading: false, isPending: true }`. In v5, `isPending` means "no data yet" (status `'pending'`). `isLoading` is `isFetching && isPending`, so for a disabled query that never fetches, `isLoading` is `false`. This is why v5 recommends `isPending` for the initial-loading UI, and why a disabled query shows `isPending: true` forever until it is enabled or you call `refetch()`.

---

## ⚫ Interview Questions + Answers

Q1: What are `queryKey` and `queryFn`?
A1: `queryKey` is an array that uniquely identifies the data in the cache, and it also acts as the dependency array (key change = new fetch). `queryFn` is a function returning a Promise with the data. It receives a context with `queryKey` and `signal`.

Q2: Difference between `isPending`, `isLoading` and `isFetching`?
A2: `isPending`: no data yet. `isFetching`: any request in flight (including background refetch). `isLoading`: `isFetching && isPending`, i.e. first load that is actually in progress. In v4, `isLoading` meant "no data", which `isPending` now means.

Q3: What is the difference between `staleTime` and `gcTime`?
A3: `staleTime` (default 0) is how long data counts as fresh; fresh data is served from cache without refetching. `gcTime` (default 5 min; renamed from `cacheTime` in v5) is how long **unused** (no subscribers) data stays in memory before garbage collection.

Q4: Why is it better than `useEffect` + `fetch`?
A4: It removes boilerplate and handles caching, dedupe, retries, background refetch, race conditions, cancellation and pagination helpers. Server state is kept out of component state.

Q5: How do you run a query only when something is ready?
A5: Use `enabled`. Example: `enabled: !!userId` so the query waits for `userId`. A disabled query stays `pending` until enabled. Alternatively, `skipToken` (v5) can be used for type-safe disabling.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You read server data in client components (lists, details, dashboards)
- You want caching, retries, window-focus refresh and shared data across components
- You need pagination, infinite scroll or polling (`refetchInterval`)

❌ **Avoid when:**
- The data can be fetched on the server in a Server Component and needs no client interactivity
- You only need one-time static data (a plain `fetch` in a Server Component is enough)
- You are **writing** data (use `useMutation`, next topic)

---

## 📊 Visual Diagram

```
 Component A ─┐                           ┌─ cache ────────────────────┐
              ├─ useQuery(['restaurant',42]) ─► key hit? ── yes ──► data (fresh? serve : serve + refetch)
 Component B ─┘                           │      │ no                  │
                                          │      ▼                     │
                                          │  queryFn() ──► network     │
                                          │      │ success             │
                                          │      ▼                     │
                                          │  store under key ─────────►│ notify A and B
                                          └────────────────────────────┘

 status:      pending ──► success ──► (stale) ──► fetching in background ──► success
                      └─► error (after 3 retries)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useQuery | Hook to read and cache server data | Server data पढ़ने और cache करने वाला hook |
| queryKey | Array that identifies cached data | Cache में data की पहचान वाला array |
| queryFn | Function returning a Promise of data | Data का Promise देने वाला function |
| staleTime | How long data counts as fresh | Data कितनी देर fresh माना जाए |
| gcTime | How long unused data stays in memory | Unused data memory में कितनी देर रहे |
| isPending | No data yet | अभी data नहीं है |
| isFetching | A request is in flight | Request चल रही है |
| enabled | Switch to run or pause a query | Query चलाने/रोकने का switch |

---

## ⚡ 3-Line Summary
**English:**
1. `useQuery({ queryKey, queryFn })` fetches and caches server data with retries and background refetch.
2. Put every variable of `queryFn` in the key; use `enabled` for dependent queries.
3. Use `isPending` for first load and `isFetching` for background refresh; read-only data only.

**Hindi:**
1. `useQuery({ queryKey, queryFn })` server data को fetch और cache करता है, retry और background refetch के साथ।
2. `queryFn` के हर variable को key में रखो; dependent queries के लिए `enabled` इस्तेमाल करो।
3. पहले load के लिए `isPending` और background refresh के लिए `isFetching` देखो; यह सिर्फ data पढ़ने के लिए है।

---

## ➡️ Next Topic
**112. useMutation Hook** — Data पढ़ना सीख लिया, अब server पर data भेजना (POST/PUT/DELETE) और उसके बाद cache को ताज़ा करना।
