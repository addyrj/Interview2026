# 110. React Query (TanStack Query)
# हिंदी में: React Query (TanStack Query) — Server State Manager

---

## 🔵 Simple Definition (English)
TanStack Query (formerly React Query) is a library that manages **server state**: data that lives on a server and that your UI only borrows. It fetches, caches, de-duplicates, retries, refetches in the background and keeps it in sync, so you write far less loading/error/cache code.

## 🔵 सरल परिभाषा (Hindi)
TanStack Query (पहले React Query) एक library है जो **server state** संभालती है: वह data जो server पर रहता है और UI सिर्फ उधार लेता है। यह fetch, cache, de-duplicate, retry, background refetch और sync करती है, इसलिए loading/error/cache का code बहुत कम लिखना पड़ता है।

---

## 🔴 Problem it Solves

Storing API data in `useState` or Redux means you must hand-write: loading and error flags, caching, avoiding duplicate requests when two components need the same data, refetching when the user returns to the tab, retries, pagination and invalidation after updates. Server data is also **shared and can become stale** at any time, unlike local UI state (a modal open flag). Treating both the same way creates lots of bugs and boilerplate.

```jsx
// PROBLEM: ~25 lines per endpoint, no cache, duplicate requests in Header and Cart
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
useEffect(() => { /* fetch, abort, set... */ }, [id]);

// SOLUTION: one hook, with cache, dedupe, retry, refetch built in
const { data, isPending, isError } = useQuery({ queryKey: ['product', id], queryFn: () => getProduct(id) });
```

## 🔴 यह क्यों बना? (Hindi)
API data को `useState` या Redux में रखने पर आपको हाथ से लिखना पड़ता है: loading और error flags, caching, दो components को एक ही data चाहिए तो duplicate requests रोकना, user के tab पर लौटने पर refetch, retries, pagination और update के बाद invalidation। Server data **share होता है और कभी भी पुराना (stale) हो सकता है**, जबकि local UI state (modal खुला है या नहीं) ऐसा नहीं होता। दोनों को एक जैसा संभालने से बहुत bugs और boilerplate बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install (v5):  npm install @tanstack/react-query
Step 2 → Create ONE QueryClient (it holds the cache) and wrap the app in <QueryClientProvider>
Step 3 → In a component call useQuery({ queryKey, queryFn })
Step 4 → queryKey is the cache ID. Same key = same cached data (shared by all components)
Step 5 → No cache → status 'pending' → queryFn runs → data stored in cache → status 'success'
Step 6 → Cache exists → returned INSTANTLY; if older than staleTime, refetched in the background
Step 7 → Window focus, reconnect, or invalidateQueries() can trigger a refetch
Step 8 → Failed queries retry 3 times with exponential backoff (default), then status 'error'
Step 9 → Unused cache entries are garbage collected after gcTime (default 5 minutes)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install (v5):  npm install @tanstack/react-query
Step 2 → एक ही QueryClient बनाओ (इसमें cache रहता है) और app को <QueryClientProvider> में लपेटो
Step 3 → Component में useQuery({ queryKey, queryFn }) बुलाओ
Step 4 → queryKey cache की ID है। वही key = वही cached data (सारे components में shared)
Step 5 → Cache नहीं → status 'pending' → queryFn चलता है → data cache में → status 'success'
Step 6 → Cache है → तुरंत मिलता है; staleTime से पुराना हो तो background में refetch
Step 7 → Window focus, reconnect या invalidateQueries() refetch शुरू कर सकते हैं
Step 8 → फेल queries 3 बार exponential backoff से retry होती हैं (default), फिर status 'error'
Step 9 → बिना इस्तेमाल के cache entries gcTime (default 5 मिनट) बाद हटती हैं
```

---

## 🟡 Real World Example
**Flipkart:** The header shows a cart count and the cart page shows the cart items. Both use `useQuery({ queryKey: ['cart'] })`. Only one network request is sent, both components update together, and after "Add to cart" the app calls `invalidateQueries({ queryKey: ['cart'] })` so both refresh. When the user switches back to the tab after 10 minutes, the data refetches silently, and old data stays visible until the new one arrives.

## 🟡 Real Example Hindi mein
**Flipkart:** Header में cart count दिखता है और cart page पर cart items। दोनों `useQuery({ queryKey: ['cart'] })` इस्तेमाल करते हैं। सिर्फ एक network request जाती है, दोनों components साथ में update होते हैं, और "Add to cart" के बाद app `invalidateQueries({ queryKey: ['cart'] })` बुलाता है जिससे दोनों refresh होते हैं। User 10 मिनट बाद tab पर लौटे तो data चुपचाप refetch होता है और नया आने तक पुराना दिखता रहता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: set up TanStack Query v5 and fetch a list
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'; // v5 imports
import { createRoot } from 'react-dom/client';                // React 18/19 root API

const queryClient = new QueryClient();                        // ONE client for the whole app (the cache)

function Todos() {
  const { data, isPending, isError, error } = useQuery({     // v5: single object argument
    queryKey: ['todos'],                                      // cache ID
    queryFn: async () => {                                    // function returning a Promise
      const res = await fetch('https://jsonplaceholder.typicode.com/todos?_limit=5');
      if (!res.ok) throw new Error('Network error');          // MUST throw so Query marks it as error
      return res.json();                                      // resolved value becomes `data`
    },
  });

  if (isPending) return <p>Loading...</p>;                    // v5: isPending (v4 was isLoading)
  if (isError) return <p>Error: {error.message}</p>;          // error state
  return <ul>{data.map(t => <li key={t.id}>{t.title}</li>)}</ul>; // success state
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}>                  {/* makes the cache available */}
    <Todos />
  </QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: global defaults, shared query across components, dependent query, devtools
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';   // npm i -D @tanstack/react-query-devtools
import { createRoot } from 'react-dom/client';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,            // data is "fresh" for 1 minute: no refetch in that time
      gcTime: 5 * 60_000,           // v5 name (v4: cacheTime). Unused cache removed after 5 minutes
      retry: 2,                     // retry failed queries twice
      refetchOnWindowFocus: false,  // turn off if too chatty for your app
    },
  },
});

// Reusable query options: one place for key + fetcher (best practice)
const cartQuery = {
  queryKey: ['cart'],
  queryFn: async () => {
    const res = await fetch('/api/cart');
    if (!res.ok) throw new Error('Cart failed');
    return res.json();
  },
};

function CartBadge() {
  const { data } = useQuery(cartQuery);                       // same key → shared cache, 1 request total
  return <span>Cart ({data?.items.length ?? 0})</span>;
}

function CartPage() {
  const { data, isPending, isFetching } = useQuery(cartQuery); // same cache entry again
  if (isPending) return <p>Loading cart...</p>;                // only the very first load
  return (
    <div>
      {isFetching && <small>Refreshing...</small>}             {/* background refetch, old data visible */}
      {data.items.map(i => <p key={i.id}>{i.name}</p>)}
    </div>
  );
}

// Dependent query: runs only when userId exists
function UserOrders({ userId }) {
  const { data } = useQuery({
    queryKey: ['orders', userId],                              // key includes every variable used
    queryFn: () => fetch(`/api/users/${userId}/orders`).then(r => r.json()),
    enabled: !!userId,                                         // do not run while userId is undefined
  });
  return <p>{data?.length ?? 0} orders</p>;
}

function RefreshButton() {
  const qc = useQueryClient();                                 // access the cache
  return <button onClick={() => qc.invalidateQueries({ queryKey: ['cart'] })}>Refresh cart</button>;
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}>
    <CartBadge /><CartPage /><UserOrders userId={7} /><RefreshButton />
    <ReactQueryDevtools initialIsOpen={false} />               {/* dev-only inspector */}
  </QueryClientProvider>
);
```

---

## 🟠 Next.js Connection

In the App Router, create the `QueryClient` inside a **Client Component provider** with `useState`, so each browser session has one client and each server request does not share a global one. For first load, you can prefetch on the server and pass the cache to the client with `HydrationBoundary` (`dehydrate`), so the page is rendered with data and then takes over on the client. If data is only needed for rendering and has no client interactions, a plain `async` Server Component is simpler and ships no JavaScript.

```jsx
// app/providers.jsx
'use client';                                               // QueryClientProvider uses context → client
import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export default function Providers({ children }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60_000 } },     // avoids an immediate refetch after hydration
  }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
// app/layout.jsx → <body><Providers>{children}</Providers></body>
```

```jsx
// app/products/page.jsx: prefetch on the server, hydrate on the client
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query';
import ProductList from './ProductList';                    // 'use client' component with useQuery

export default async function Page() {
  const qc = new QueryClient();                             // a NEW client per request (never share)
  await qc.prefetchQuery({
    queryKey: ['products'],
    queryFn: () => fetch('https://api.example.com/products').then(r => r.json()),
  });
  return (
    <HydrationBoundary state={dehydrate(qc)}>               {/* ships the cache to the browser */}
      <ProductList />                                       {/* useQuery(['products']) starts with data */}
    </HydrationBoundary>
  );
}
```

Performance: de-duplication and caching cut network calls, and hydration avoids a client-side loading waterfall. Re-render behavior: components re-render when tracked fields (`data`, `isFetching`...) change.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Copying query data into `useState` (it never updates again)
✅ **Correct:** Use `data` directly. Derive values during render.

```jsx
// Wrong: state is set once from the first data and ignores refetches
const { data } = useQuery(q);
const [items, setItems] = useState(data);          // ❌ stale copy
// Right
const items = data ?? [];                          // ✅ always current
```

❌ **Mistake 2:** Not including variables in `queryKey`
✅ **Correct:** Every value used by `queryFn` must be in the key

```jsx
// Wrong: all users share the key, so cache shows the wrong user
useQuery({ queryKey: ['user'], queryFn: () => getUser(id) });        // ❌
// Right
useQuery({ queryKey: ['user', id], queryFn: () => getUser(id) });    // ✅ refetches per id
```

❌ **Mistake 3:** `queryFn` that does not throw on HTTP errors (so errors become "successful" data)
✅ **Correct:** Check `res.ok` and throw (Axios already throws)

```jsx
// Wrong: a 500 page becomes data
queryFn: () => fetch('/api/x').then(r => r.json())                   // ❌
// Right
queryFn: async () => { const r = await fetch('/api/x'); if (!r.ok) throw new Error(r.status); return r.json(); } // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
import { useQuery } from '@tanstack/react-query';

function A() {
  const { data } = useQuery({ queryKey: ['x'], queryFn: () => { console.log('fetch'); return 1; } });
  return <p>{data}</p>;
}

function App() {
  return <><A /><A /><A /></>;
}
```
**Answer:** `fetch` is logged **once**, not three times. All three components use the same `queryKey`, so TanStack Query de-duplicates them into a single in-flight request and shares one cache entry. (In dev with StrictMode, the mount/unmount/mount check does not trigger extra fetches because the cache entry is reused.) All three components show `1` together. This is why queries are "global cache entries keyed by queryKey", not per-component state.

---

## ⚫ Interview Questions + Answers

Q1: What is server state, and how is it different from client state?
A1: Server state is data owned by a remote server: it is async, shared, can change without you knowing and becomes stale. Client state (modal open, form text) is owned by the browser and synchronous. TanStack Query is built for server state, while `useState`, Zustand or Redux fit client state.

Q2: Explain `staleTime` vs `gcTime`.
A2: `staleTime` (default 0) is how long data is considered fresh: during it, no refetch is triggered. `gcTime` (default 5 min, called `cacheTime` in v4) is how long an unused (no observers) cache entry is kept before garbage collection. Stale data can still be shown instantly while refetching.

Q3: What is a `queryKey` and why does it matter?
A3: An array that uniquely identifies the data in the cache. Changing a value in the key triggers a new fetch (and a separate cache entry). Include every variable used by the `queryFn`, and keep a consistent hierarchy (`['todos', 'list', filters]`) so you can invalidate groups.

Q4: What changed in v5?
A3: Single-object signatures (`useQuery({...})` only), `isLoading` became `isPending` for "no data yet" (`isLoading` is now `isFetching && isPending`), `cacheTime` became `gcTime`, `keepPreviousData` was replaced by `placeholderData: keepPreviousData`, and `onSuccess/onError/onSettled` callbacks were removed from `useQuery`. It requires React 18+.

Q5: Why use TanStack Query instead of Redux for API data?
A5: It gives caching, de-duplication, retries, background refetch, pagination and mutations out of the box, with no reducers or actions. Redux would need all of it handwritten, although RTK Query offers a similar approach for Redux users.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Your app has many API calls that are shared across components
- You need caching, retries, refetch on focus, pagination or optimistic updates
- You want to remove loading/error boilerplate

❌ **Avoid when:**
- The app is tiny with one or two requests (`fetch` is enough)
- Data is only needed for first render in Next.js (use Server Components)
- You need purely client state (use `useState`, Context or Zustand)

---

## 📊 Visual Diagram

```
   Component A ─┐                          ┌──────────────── QueryClient cache ───────────────┐
   Component B ─┼── useQuery(['cart']) ──► │ ['cart']  → { data, status, dataUpdatedAt }       │
   Component C ─┘                          │ ['user',7]→ { ... }                               │
                                           └───────┬───────────────────────────────┬──────────┘
                                                   │ fresh? (staleTime)            │ no observers
                                       yes: return cache instantly          after gcTime: removed
                                       no : return cache + refetch in background
                                                   │
                                                   ▼
                                               queryFn ──► server
   Triggers for refetch: mount, window focus, reconnect, invalidateQueries, refetchInterval
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server state | Data owned by a server, borrowed by UI | Server का data जो UI उधार लेता है |
| QueryClient | Object holding the cache and config | Cache और config रखने वाला object |
| queryKey | Array identifying cached data | Cached data की पहचान वाला array |
| queryFn | Function that fetches the data | Data लाने वाला function |
| staleTime | How long data counts as fresh | Data कितनी देर fresh माना जाए |
| gcTime | How long unused cache is kept | बिना इस्तेमाल का cache कितनी देर रखा जाए |
| isPending | No data yet (v5) | अभी data नहीं है (v5) |
| invalidateQueries | Mark data stale and refetch | Data को stale मार्क कर refetch करना |

---

## ⚡ 3-Line Summary
**English:**
1. TanStack Query manages server state with a cache keyed by `queryKey`, plus retries, de-duplication and background refetching.
2. Wrap the app in `QueryClientProvider`, use `useQuery({ queryKey, queryFn })`, and make `queryFn` throw on errors.
3. In Next.js create the client in a client provider, and optionally prefetch with `HydrationBoundary`.

**Hindi:**
1. TanStack Query server state को `queryKey` वाले cache, retries, de-duplication और background refetch से संभालती है।
2. App को `QueryClientProvider` में लपेटो, `useQuery({ queryKey, queryFn })` इस्तेमाल करो, और `queryFn` errors पर throw करे।
3. Next.js में client को client provider में बनाओ, और चाहो तो `HydrationBoundary` से prefetch करो।

---

## ➡️ Next Topic
**111. useQuery Hook** — अब setup समझ आ गया है। अगला topic `useQuery` के सारे options और returned fields (`isFetching`, `status`, `select`, `enabled`, `refetch`) को detail में बताता है।
