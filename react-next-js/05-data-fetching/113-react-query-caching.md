# 113. React Query Caching
# हिंदी में: React Query Caching — staleTime, gcTime और Invalidation

---

## 🔵 Simple Definition (English)
**React Query caching** stores every query result in memory under its `queryKey`. Two timers control it: **`staleTime`** (how long data is considered fresh) and **`gcTime`** (how long unused data stays before it is deleted). You can also update or invalidate the cache manually.

## 🔵 सरल परिभाषा (Hindi)
**React Query caching** हर query का result `queryKey` के नाम से memory में रखता है। इसे दो timers चलाते हैं: **`staleTime`** (data कितनी देर fresh माना जाए) और **`gcTime`** (unused data delete होने से पहले कितनी देर रहे)। Cache को manually update या invalidate भी कर सकते हो।

---

## 🔴 Problem it Solves

Without a cache, navigating Home → Product → Home refetches the list every time, the user sees a spinner again, and servers get repeated identical requests. A naive cache (store forever) shows stale prices. The challenge is balancing **speed** (use cache) with **freshness** (refetch when needed).

```jsx
// PROBLEM: no cache → spinner on every mount, repeated network calls
useEffect(() => { fetch('/api/products').then(r => r.json()).then(setProducts); }, []);

// PROBLEM 2: cache forever → stale data
const cache = {}; // never invalidated

// SOLUTION: stale-while-revalidate: show cached data instantly, refetch quietly if stale
useQuery({ queryKey: ['products'], queryFn: getProducts, staleTime: 60_000 });
```

## 🔴 यह क्यों बना? (Hindi)
Cache के बिना Home → Product → Home जाने पर list हर बार दोबारा fetch होती है, user को फिर spinner दिखता है और server पर वही requests बार-बार जाती हैं। हमेशा के लिए cache करने पर prices पुराने दिखते हैं। चुनौती है **speed** (cache इस्तेमाल करो) और **freshness** (ज़रूरत पर refetch) में संतुलन। React Query का stale-while-revalidate यही करता है: cache का data तुरंत दिखाओ, stale हो तो चुपचाप refetch करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → queryKey ['products', {cat:'mobiles'}] is hashed → a cache entry (a "Query")
Step 2 → First useQuery: no entry → fetch → store data with a timestamp
Step 3 → Data is FRESH for staleTime (default 0 → stale immediately)
Step 4 → Another component mounts with the same key:
           fresh → return from cache, NO request
           stale → return cache NOW + refetch in background (stale-while-revalidate)
Step 5 → When the last component using the key unmounts, the entry becomes INACTIVE
Step 6 → After gcTime (default 5 minutes) the inactive entry is garbage collected
Step 7 → Triggers that refetch stale queries: mount, window focus, network reconnect, refetchInterval
Step 8 → Manual control: invalidateQueries (mark stale + refetch active), setQueryData, removeQueries

v5: 'cacheTime' → 'gcTime'. Query keys compare by deep value, so order inside objects does not matter,
    but order inside arrays does.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → queryKey ['products', {cat:'mobiles'}] का hash बनता है → एक cache entry ("Query")
Step 2 → पहला useQuery: entry नहीं → fetch → data timestamp के साथ store
Step 3 → Data staleTime तक FRESH रहता है (default 0 → तुरंत stale)
Step 4 → उसी key के साथ दूसरा component mount होता है:
           fresh → cache से, कोई request नहीं
           stale → cache अभी दो + background में refetch (stale-while-revalidate)
Step 5 → जब key इस्तेमाल करने वाला आखिरी component unmount हो, entry INACTIVE हो जाती है
Step 6 → gcTime (default 5 मिनट) के बाद inactive entry garbage collect हो जाती है
Step 7 → Stale queries को refetch करने वाले triggers: mount, window focus, reconnect, refetchInterval
Step 8 → Manual control: invalidateQueries (stale मार्क + active refetch), setQueryData, removeQueries

v5: 'cacheTime' → 'gcTime'। Query keys deep value से compare होती हैं, इसलिए object के अंदर की
    keys का क्रम मायने नहीं रखता, पर array का क्रम रखता है।
```

---

## 🟡 Real World Example
**Flipkart product listing:** The user opens "Mobiles", opens one phone, and presses back. With `staleTime: 60s`, the list appears instantly with no spinner and no request. After 2 minutes, the same back navigation shows the cached list instantly and silently refreshes prices in the background. If the user left the listing page and returned after 10 minutes (past `gcTime`), the cache was cleared and a normal loading state shows.

## 🟡 Real Example Hindi mein
**Flipkart product listing:** User "Mobiles" खोलता है, एक phone खोलता है और back दबाता है। `staleTime: 60s` हो तो list तुरंत दिखती है, spinner नहीं और request नहीं। 2 मिनट बाद वही back navigation cached list तुरंत दिखाता है और background में चुपचाप prices refresh करता है। अगर user 10 मिनट बाद (gcTime के बाद) लौटे तो cache साफ़ हो चुका था और सामान्य loading दिखती है।

---

## 💻 Code Example — Basic

```jsx
// Basic caching: observe staleTime in action
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

const queryClient = new QueryClient();                          // default: staleTime 0, gcTime 5 min

let calls = 0;                                                  // count network calls (fake API)
async function getTime() { calls += 1; return new Date().toLocaleTimeString(); }

function Clock({ label }) {
  const { data, isFetching } = useQuery({
    queryKey: ['time'],                                          // SAME key in every Clock → shared entry
    queryFn: getTime,
    staleTime: 10_000,                                           // fresh for 10 seconds
  });
  return <p>{label}: {data} {isFetching && '(fetching)'} — total calls: {calls}</p>;
}

function App() {
  const [show, setShow] = useState(true);                       // toggle to unmount/mount
  return (
    <div>
      <button onClick={() => setShow((s) => !s)}>Toggle</button>
      {show && <Clock label="A" />}                              {/* remount within 10s → no new call */}
      <Clock label="B" />                                        {/* shares A's cache entry */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}><App /></QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: defaults, hierarchical keys, key factory, setQueryData, prefetch, invalidation scopes
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';

// 1) Sensible global defaults (override per query when needed)
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,              // 1 min fresh: avoids refetch storms on navigation
      gcTime: 10 * 60 * 1000,            // keep unused data 10 min (v5 name; v4 was cacheTime)
      refetchOnWindowFocus: true,        // keep data current when user returns to the tab
      retry: 2,                          // fewer retries than default 3
    },
  },
});

// 2) Query key factory: ONE place that defines keys → no typos, easy invalidation
export const productKeys = {
  all: ['products'],                                          // root of the family
  lists: () => [...productKeys.all, 'list'],                  // ['products','list']
  list: (filters) => [...productKeys.lists(), filters],       // ['products','list',{cat,page}]
  details: () => [...productKeys.all, 'detail'],              // ['products','detail']
  detail: (id) => [...productKeys.details(), id],             // ['products','detail',42]
};

async function fetchProducts(filters) {
  const qs = new URLSearchParams(filters).toString();
  const res = await fetch(`/api/products?${qs}`);
  if (!res.ok) throw new Error('Failed to load products');
  return res.json();
}

export function ProductList({ filters }) {
  const qc = useQueryClient();
  const { data = [] } = useQuery({
    queryKey: productKeys.list(filters),                      // each filter set = its own cache entry
    queryFn: () => fetchProducts(filters),
  });

  // 3) Seed the detail cache from the list → detail page opens instantly
  function seedDetail(p) {
    qc.setQueryData(productKeys.detail(p.id), p);             // write directly to the cache
  }

  // 4) Prefetch on hover so the click feels instant
  function prefetch(id) {
    qc.prefetchQuery({
      queryKey: productKeys.detail(id),
      queryFn: () => fetch(`/api/products/${id}`).then((r) => r.json()),
      staleTime: 30_000,                                      // do not prefetch again if fresh
    });
  }

  return (
    <ul>
      {data.map((p) => (
        <li key={p.id} onMouseEnter={() => prefetch(p.id)} onClick={() => seedDetail(p)}>
          {p.name}
        </li>
      ))}
      {/* Invalidate scopes:
          qc.invalidateQueries({ queryKey: productKeys.all })       → all product queries
          qc.invalidateQueries({ queryKey: productKeys.lists() })   → only lists
          qc.invalidateQueries({ queryKey: productKeys.detail(42), exact: true }) → only one */}
    </ul>
  );
}

export const Root = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);
```

Re-render behavior: invalidating a key marks it stale; only queries that are **active** (mounted) refetch immediately, inactive ones refetch the next time they mount. Components re-render only when the fields they read change. Performance impact: a good `staleTime` removes most duplicate requests; a very long `gcTime` increases memory use.

---

## 🟠 Next.js Connection

On the server, create a **new `QueryClient` per request** (never a module-level one), or users could see each other's cached data. On the browser, keep one client in state. Set `staleTime` above 0 when using server prefetch so the client does not immediately refetch what the server just sent.

```jsx
// app/get-query-client.js  (pattern from the TanStack Next.js docs, simplified)
import { QueryClient, isServer } from '@tanstack/react-query';

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000 } },   // >0: avoids refetch right after hydration
  });
}

let browserQueryClient;                                       // singleton for the browser only
export function getQueryClient() {
  if (isServer) return makeQueryClient();                     // server: fresh client for every request
  if (!browserQueryClient) browserQueryClient = makeQueryClient(); // browser: reuse across renders
  return browserQueryClient;
}
```

Next.js also has its own server cache (`fetch` cache, `revalidatePath`, `revalidateTag`). That is separate from React Query's browser cache: React Query caches in the user's browser memory, Next.js caches on the server. Defaults of the Next.js cache changed between 14 and 15 (version-dependent), so check your version.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Confusing `staleTime` with `gcTime`
✅ **Correct:** `staleTime` = freshness (refetch or not), `gcTime` = memory lifetime of unused data

```jsx
// Wrong belief: "gcTime: 0 will make data always fresh"
useQuery({ queryKey: ['p'], queryFn: getP, gcTime: 0 });        // ❌ only deletes unused data immediately

// Right: control freshness with staleTime
useQuery({ queryKey: ['p'], queryFn: getP, staleTime: 0 });     // ✅ always refetch on mount (default)
```

❌ **Mistake 2:** Creating `new QueryClient()` inside a component body
✅ **Correct:** Create it once (module level or `useState` initializer)

```jsx
// Wrong: a NEW cache on every render → everything refetches, cache is lost
function Providers({ children }) {
  const client = new QueryClient();                              // ❌ re-created per render
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

// Right
function Providers2({ children }) {
  const [client] = useState(() => new QueryClient());            // ✅ created once
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
```

❌ **Mistake 3:** Object/array mutation of cached data
✅ **Correct:** Treat cached data as immutable; create new copies

```jsx
// Wrong: mutating cached data breaks change detection (structural sharing)
const { data } = useQuery({ queryKey: ['t'], queryFn: getTodos });
data.push({ id: 99 });                                           // ❌ mutates the cache directly

// Right
qc.setQueryData(['t'], (old = []) => [...old, { id: 99 }]);      // ✅ returns a new array
```

---

## 🧠 Tricky Interview Question

```jsx
useQuery({ queryKey: ['p'], queryFn: getProducts, staleTime: 5000 });
// 1) mounted at t=0 (fetch #1)
// 2) unmounted at t=2s
// 3) mounted again at t=3s
// 4) unmounted at t=4s, mounted again at t=8s
// How many network requests happen in total by t=8s?
```
**Answer:** 2 requests. At t=0 the first fetch happens. Data is fresh until t=5s, so the remount at t=3s uses the cache (gcTime is 5 minutes, so it still exists) without a request. At t=8s the data is stale (older than 5s), so the cached data is shown instantly **and** a background refetch happens (request #2). With the default `staleTime: 0` every remount would refetch, giving 3 requests.

---

## ⚫ Interview Questions + Answers

Q1: What is stale-while-revalidate?
A1: Show cached (possibly old) data immediately, then refetch in the background and update the UI when fresh data arrives. React Query does this by default when stale data exists.

Q2: `staleTime` vs `gcTime`?
A2: `staleTime` (default 0): how long a result is considered fresh and served without refetch. `gcTime` (default 5 min): how long a query with no observers stays in the cache before deletion. They are independent.

Q3: What is the difference between `invalidateQueries`, `refetchQueries` and `setQueryData`?
A3: `invalidateQueries` marks queries stale and refetches the active ones. `refetchQueries` forces a refetch regardless of staleness. `setQueryData` writes data directly into the cache without a request.

Q4: How are query keys matched?
A4: Keys are hashed deeply. `['todos', {a:1,b:2}]` equals `['todos', {b:2,a:1}]`, but array order matters. Invalidating `['todos']` matches all keys that start with it (prefix match) unless `exact: true`.

Q5: Why use a query key factory?
A5: It centralizes key definitions, prevents typos, and makes scoped invalidation easy (all, lists, one detail).

---

## 🔷 When to Use + When Not to Use
✅ **Use (tune the cache) when:**
- Data changes rarely (categories, profile): use long `staleTime`
- You want instant back navigation and prefetching on hover
- You need predictable invalidation after mutations

❌ **Avoid / be careful when:**
- Data must always be real-time (price tickers): use a small `staleTime`, polling or WebSockets
- Sensitive per-user data on shared devices: clear the cache on logout (`queryClient.clear()`)
- Huge responses: a long `gcTime` can raise memory use

---

## 📊 Visual Diagram

```
 time ───────────────────────────────────────────────────────────►
 fetch ✔               staleTime (fresh)       stale          gcTime countdown
 ├────────────────────┼──────────────────────┼──────────────────┼────────────►
 │  FRESH: mount → cache only (no request)    │ STALE: mount → cache + background refetch
 │                                            │
 │  observers: 1  ... 0 (unmount) ─────────────► inactive timer starts
 │                                                        └─ after gcTime → entry deleted

 invalidateQueries(['products'])
     └─► mark stale ─► active queries refetch now, inactive ones wait for next mount
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Stored query results in memory | Memory में stored query results |
| staleTime | Time data stays fresh | Data fresh रहने का समय |
| gcTime | Time unused data stays cached | Unused data cache में रहने का समय |
| Stale | Old, may be refetched | पुराना, refetch हो सकता है |
| Invalidate | Mark stale and refetch active | Stale मार्क कर active को refetch |
| Active / inactive query | Has / has no mounted observers | Observers हैं / नहीं हैं |
| Query key factory | Helper that builds consistent keys | Keys बनाने वाला helper |
| Structural sharing | Reuses unchanged parts of data | बिना बदले हिस्सों को reuse करना |

---

## ⚡ 3-Line Summary
**English:**
1. Results are cached by `queryKey`; `staleTime` decides refetching, `gcTime` decides deletion.
2. Stale data is shown instantly while a background refetch updates it.
3. Use `invalidateQueries`, `setQueryData` and key factories; create one `QueryClient` per browser and per server request.

**Hindi:**
1. Results `queryKey` से cache होते हैं; `staleTime` refetch तय करता है, `gcTime` delete होना।
2. Stale data तुरंत दिखता है और background refetch उसे update करता है।
3. `invalidateQueries`, `setQueryData` और key factories इस्तेमाल करो; browser में एक और server पर हर request के लिए नया `QueryClient` बनाओ।

---

## ➡️ Next Topic
**114. Optimistic Updates** — Server के जवाब का इंतज़ार किए बिना UI को तुरंत बदलना, और fail होने पर rollback करना। Cache की समझ के बाद यही सबसे बड़ा UX सुधार है।
