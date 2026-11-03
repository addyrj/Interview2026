# 117. SWR Library
# हिंदी में: SWR Library — Stale-While-Revalidate से Smart Data Fetching

---

## 🔵 Simple Definition (English)
**SWR** is a small React data fetching library from Vercel. The name comes from "stale-while-revalidate": it first returns cached (stale) data for instant UI, then fetches fresh data in the background and updates the screen. You use it with one hook: `useSWR(key, fetcher)`.

## 🔵 सरल परिभाषा (Hindi)
**SWR** Vercel की एक छोटी React data fetching library है। नाम "stale-while-revalidate" से आया है: यह पहले cache का (पुराना) data तुरंत दिखाती है, फिर background में नया data लाकर screen update करती है। इसे एक hook से इस्तेमाल करते हैं: `useSWR(key, fetcher)`।

---

## 🔴 Problem it Solves

Plain `useEffect + fetch` shows a spinner on every visit, has no cache, refetches the same URL in many components, and never refreshes when the user comes back to the tab. SWR keeps a shared cache keyed by a string (usually the URL), deduplicates requests, revalidates on focus and reconnect, and gives you `data`, `error` and `isLoading` with almost no code.

```jsx
// PROBLEM: spinner every time, no cache, no refresh on focus
const [data, setData] = useState(null);
useEffect(() => { fetch('/api/user').then(r => r.json()).then(setData); }, []);
if (!data) return <p>Loading...</p>;   // user sees a spinner on EVERY mount

// SOLUTION: cached data shows instantly, fresh data arrives silently
const { data, error, isLoading } = useSWR('/api/user', fetcher);
```

## 🔴 यह क्यों बना? (Hindi)
सादा `useEffect + fetch` हर visit पर spinner दिखाता है, cache नहीं रखता, कई components में एक ही URL दोबारा मंगाता है, और user के tab पर लौटने पर refresh नहीं करता। SWR एक string key (आम तौर पर URL) पर shared cache रखती है, requests का dedupe करती है, focus और reconnect पर revalidate करती है, और बहुत कम code में `data`, `error` और `isLoading` देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component calls useSWR(key, fetcher)
Step 2 → SWR looks in its global cache for that key
Step 3 → If found: return cached data immediately (stale), isLoading is false
Step 4 → In the background, call fetcher(key) to REVALIDATE (deduped within 2 seconds)
Step 5 → When fresh data arrives, update the cache and re-render every component using that key
Step 6 → Revalidate again on: window focus, network reconnect, optional polling (refreshInterval)
Step 7 → mutate(key) manually refreshes or updates the cache (after a POST, for example)

KEY: the key is the cache identity; pass null as key to pause fetching (conditional fetching)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component useSWR(key, fetcher) बुलाता है
Step 2 → SWR अपने global cache में उस key को खोजती है
Step 3 → मिल जाए तो cached data तुरंत लौटाती है (stale), isLoading false रहता है
Step 4 → Background में fetcher(key) से REVALIDATE करती है (2 सेकंड के अंदर dedupe)
Step 5 → नया data आने पर cache update होता है और उस key वाले सारे components re-render होते हैं
Step 6 → इन पर फिर revalidate होता है: window focus, network reconnect, और optional polling (refreshInterval)
Step 7 → mutate(key) से cache हाथ से refresh या update होता है (जैसे POST के बाद)

KEY: key ही cache की पहचान है; key की जगह null देने पर fetching रुक जाती है (conditional fetching)
```

---

## 🟡 Real World Example
**Zomato order tracking / Gmail inbox:** You open the Gmail inbox, it instantly shows the last known emails from cache (stale), then quietly fetches new ones and updates the list (revalidate). When you switch to another tab and come back, it checks again (focus revalidation). In a Zomato "Track order" page, `refreshInterval: 5000` polls the order status every 5 seconds, and stops when the order is delivered.

## 🟡 Real Example Hindi mein
**Zomato order tracking / Gmail inbox:** Gmail inbox खोलने पर cache से पिछले emails तुरंत दिखते हैं (stale), फिर चुपचाप नए emails आकर list update हो जाती है (revalidate)। दूसरे tab से लौटने पर दोबारा check होता है (focus revalidation)। Zomato के "Track order" page में `refreshInterval: 5000` हर 5 सेकंड में order status पूछता है और order deliver होते ही रुक जाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: useSWR with a fetcher (SWR 2.x)
import useSWR from 'swr';                                  // npm install swr
import { createRoot } from 'react-dom/client';              // React 18/19 root API

// fetcher: receives the key, returns a promise with the data
const fetcher = async (url) => {
  const res = await fetch(url);                             // call the API
  if (!res.ok) throw new Error('Request failed');           // SWR treats a thrown error as `error`
  return res.json();                                        // parsed JSON becomes `data`
};

function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher); // key = URL, fetcher = function

  if (error) return <p>Failed to load: {error.message}</p>; // show errors
  if (isLoading) return <p>Loading...</p>;                  // only true on the first load (no cache)
  return <h1>Hello, {data.name}</h1>;                       // data is ready
}

function Header() {
  const { data } = useSWR('/api/user', fetcher);            // SAME key: shares cache, NO second request
  return <nav>{data ? data.name : '...'}</nav>;             // updates together with Profile
}

createRoot(document.getElementById('root')).render(
  <div><Header /><Profile /></div>                          // two components, one network call
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: global config, conditional fetching, polling, mutation with optimistic update
import useSWR, { SWRConfig } from 'swr';                    // SWRConfig sets defaults for a subtree
import useSWRMutation from 'swr/mutation';                  // hook for remote mutations (POST/PUT)
import { useState } from 'react';

const fetcher = async (url) => {                            // one reusable fetcher
  const res = await fetch(url);
  if (!res.ok) {
    const err = new Error('Request failed');                // attach status for UI decisions
    err.status = res.status;
    throw err;
  }
  return res.json();
};

// useSWRMutation passes (key, { arg }) to the function
async function addTodo(url, { arg }) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(arg),                              // arg = what we pass to trigger()
  });
  if (!res.ok) throw new Error('Could not add');
  return res.json();
}

function Todos({ userId }) {
  // conditional fetching: key is null until userId exists → SWR does nothing
  const { data: todos, error, isValidating, mutate } = useSWR(
    userId ? `/api/todos?user=${userId}` : null,
    fetcher,
    {
      refreshInterval: 10_000,                              // poll every 10 seconds
      revalidateOnFocus: true,                              // refresh when the tab is focused (default true)
      shouldRetryOnError: true,                             // retry with exponential backoff
      onErrorRetry: (err, key, config, revalidate, { retryCount }) => {
        if (err.status === 404) return;                     // never retry a 404
        if (retryCount >= 3) return;                        // max 3 retries
        setTimeout(() => revalidate({ retryCount }), 2000); // retry after 2 seconds
      },
    }
  );

  const { trigger, isMutating } = useSWRMutation('/api/todos', addTodo); // write operation
  const [title, setTitle] = useState('');

  async function handleAdd(e) {
    e.preventDefault();                                     // stop the form reload
    const optimistic = [...(todos ?? []), { id: 'temp', title }]; // what the UI should show now
    await mutate(                                           // bound mutate: updates THIS key's cache
      async () => {
        const created = await trigger({ title });           // real request
        return [...(todos ?? []), created];                 // final data for the cache
      },
      { optimisticData: optimistic, rollbackOnError: true, revalidate: true } // instant UI + rollback
    );
    setTitle('');                                           // clear the input
  }

  if (error) return <p role="alert">Error {error.status ?? ''}</p>;
  if (!todos) return <p>Loading...</p>;
  return (
    <form onSubmit={handleAdd}>
      {isValidating && <small>Refreshing...</small>}        {/* true during background revalidation */}
      <ul>{todos.map(t => <li key={t.id}>{t.title}</li>)}</ul>
      <input value={title} onChange={e => setTitle(e.target.value)} />
      <button disabled={isMutating || !title}>Add</button>
    </form>
  );
}

export default function App() {
  return (
    <SWRConfig value={{ fetcher, dedupingInterval: 2000 }}> {/* default fetcher for all hooks below */}
      <Todos userId={42} />
    </SWRConfig>
  );
}
```

---

## 🟠 Next.js Connection

SWR is made by Vercel, the creators of Next.js, and fits naturally. In the App Router, `useSWR` runs only in Client Components (`'use client'`). A common pattern: fetch the first data in a Server Component and give it to SWR as `fallbackData` (or `SWRConfig value={{ fallback }}`), so the page is server-rendered and SWR keeps it fresh after hydration. In the Pages Router, you combine `getStaticProps`/`getServerSideProps` with `fallback` the same way.

```jsx
// app/dashboard/page.jsx (Server Component): fetch on the server, pass as fallback
import DashboardClient from './DashboardClient';             // 'use client' component using useSWR

export default async function Page() {
  const res = await fetch('https://example.com/api/stats', { cache: 'no-store' }); // fresh on every request
  const stats = await res.json();                            // first data from the server
  return <DashboardClient fallbackData={stats} />;           // no loading spinner at all
}
```

```jsx
// app/dashboard/DashboardClient.jsx
'use client';                                                // hooks need the client
import useSWR from 'swr';

const fetcher = (url) => fetch(url).then(r => r.json());     // browser-side fetcher

export default function DashboardClient({ fallbackData }) {
  const { data } = useSWR('/api/stats', fetcher, {
    fallbackData,                                            // SSR data used until SWR revalidates
    refreshInterval: 30_000,                                 // keep it live after hydration
  });
  return <p>Active orders: {data.active}</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the key (an object or array) in a way that changes every render
✅ **Correct:** Use a string, or an array of stable primitives (SWR 2.x serializes keys, so objects are stable by value, but keep them simple)

```jsx
// Wrong: building the URL with a changing value (Date.now) creates a new key every render
useSWR(`/api/feed?t=${Date.now()}`, fetcher);              // ❌ refetches forever, no cache hits

// Right: stable key
useSWR('/api/feed', fetcher);                              // ✅ same key, shared cache
```

❌ **Mistake 2:** Using hooks conditionally to avoid fetching
✅ **Correct:** Call the hook always and pass `null` as the key to pause

```jsx
// Wrong: breaks the Rules of Hooks
if (userId) { var { data } = useSWR(`/api/u/${userId}`, fetcher); }  // ❌

// Right: conditional fetching with a null key
const { data } = useSWR(userId ? `/api/u/${userId}` : null, fetcher); // ✅
```

❌ **Mistake 3:** Not throwing on HTTP errors in the fetcher (`fetch` only rejects on network failure)
✅ **Correct:** Check `res.ok` and throw

```jsx
// Wrong: a 500 response with an error JSON becomes `data`
const fetcher = url => fetch(url).then(r => r.json());     // ❌ error is never set
// Right
const fetcher = async url => {
  const r = await fetch(url);
  if (!r.ok) throw new Error(String(r.status));            // ✅ now `error` is populated
  return r.json();
};
```

---

## 🧠 Tricky Interview Question

```jsx
function A() { const { data } = useSWR('/api/me', fetcher); return <p>A: {data?.name}</p>; }
function B() { const { data } = useSWR('/api/me', fetcher); return <p>B: {data?.name}</p>; }

function App() { return <><A /><B /></>; }
// How many network requests happen on first render? What if B mounts 5 seconds later?
```
**Answer:** One request on the first render: SWR deduplicates calls with the same key within `dedupingInterval` (default 2 seconds), and both components share one cache entry, so A and B update together. If B mounts 5 seconds later, B gets the cached value instantly (stale) and SWR sends a new background revalidation request, because the dedupe window (2 s) has passed. The UI shows data immediately, then updates if the server returned something different. Note `staleTime` does not exist in SWR the way it does in React Query: to avoid revalidation on mount use `revalidateIfStale: false` or `useSWRImmutable`.

---

## ⚫ Interview Questions + Answers

Q1: What does "stale-while-revalidate" mean?
A1: It is an HTTP cache strategy (RFC 5861): serve the cached, possibly stale, response immediately, and revalidate it in the background to update the cache. SWR applies it in the UI so users see data instantly and then see fresh data without a spinner.

Q2: How does SWR share data between components?
A2: Through a global cache keyed by the first argument of `useSWR`. Components using the same key read the same cache entry, requests are deduplicated, and every component re-renders when that entry changes.

Q3: How do you do a POST and refresh the list?
A3: Use `useSWRMutation` (or a plain `fetch`) and then call `mutate(key)` to revalidate, or pass `optimisticData` to `mutate` for an instant UI update with `rollbackOnError`. The global `mutate` from `useSWRConfig()` can refresh any key.

Q4: SWR vs React Query?
A4: SWR is smaller and simpler (key + fetcher, revalidation on focus). React Query has more features: `useMutation` lifecycle, `staleTime`/`gcTime`, devtools, infinite queries with page params, query cancellation and a larger ecosystem. SWR also has `useSWRInfinite`. Choose SWR for simple read-heavy apps, React Query for complex data flows.

Q5: How do you stop SWR from refetching on focus?
A5: Pass `revalidateOnFocus: false` per hook or globally via `SWRConfig`. For data that never changes, use `useSWRImmutable` (or `revalidateIfStale`, `revalidateOnFocus`, `revalidateOnReconnect` all set to false).

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need a lightweight way to fetch, cache and revalidate read-heavy data (dashboards, feeds, profiles)
- You are on Next.js and want a first-party style library with `fallback` support
- You want focus and reconnect revalidation with almost no setup

❌ **Avoid when:**
- You need complex mutation lifecycles, offline persistence or detailed devtools (React Query fits better)
- The data is only fetched once on the server and never changes (use a Server Component)
- You need strict client-side state that is not server data (use `useState` or Zustand)

---

## 📊 Visual Diagram

```
  useSWR('/api/user', fetcher)
          │
          ▼
   ┌──────────────┐  hit   ┌─────────────────────┐
   │ Global cache │ ─────► │ return STALE data   │ → UI renders instantly
   │ key → data   │        └─────────────────────┘
   └──────┬───────┘
          │ (always) revalidate in background
          ▼
   fetcher('/api/user') ───► fresh data ───► update cache ───► re-render ALL users of this key

   Triggers: mount • window focus • reconnect • refreshInterval • mutate(key)

   Re-render: a component re-renders only for fields it reads (data, error, isLoading).
   Performance: dedupe within 2s means 10 components = 1 request.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SWR | Stale-while-revalidate data library | Stale-while-revalidate वाली data library |
| Stale | Old cached data shown first | पहले दिखने वाला पुराना cached data |
| Revalidate | Fetch fresh data to refresh the cache | नया data लाकर cache refresh करना |
| Key | Cache identity (usually the URL) | Cache की पहचान (आम तौर पर URL) |
| Fetcher | Function that gets the data for a key | Key का data लाने वाला function |
| Deduplication | One request for many identical calls | कई एक जैसी calls के लिए एक request |
| mutate | Function to update or refresh the cache | Cache update/refresh करने वाला function |
| fallbackData | Initial data (for example from the server) | शुरुआती data (जैसे server से) |

---

## ⚡ 3-Line Summary
**English:**
1. SWR returns cached data first, then revalidates in the background and updates the UI.
2. One hook, `useSWR(key, fetcher)`, gives you cache, dedupe, focus revalidation, polling and error states.
3. In Next.js use it in Client Components with server `fallbackData`; pass `null` as key to pause fetching.

**Hindi:**
1. SWR पहले cached data लौटाती है, फिर background में revalidate करके UI update करती है।
2. एक hook `useSWR(key, fetcher)` से cache, dedupe, focus revalidation, polling और error states मिलते हैं।
3. Next.js में इसे Client Components में server के `fallbackData` के साथ इस्तेमाल करो; fetching रोकने के लिए key `null` दो।

---

## ➡️ Next Topic
**118. GraphQL in React (Apollo)** — REST की जगह GraphQL से सिर्फ ज़रूरी fields माँगना, और Apollo Client से queries, mutations और cache कैसे संभालें।
