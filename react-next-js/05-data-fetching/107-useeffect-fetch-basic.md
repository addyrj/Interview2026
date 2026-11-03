# 107. useEffect + fetch — Basic
# हिंदी में: useEffect + fetch — API से Data लाने का बुनियादी तरीका

---

## 🔵 Simple Definition (English)
The basic way to load data in a client-side React component is to call `fetch` inside `useEffect`, store the result in `useState`, and render from that state. The effect runs after the first render, so the user first sees an empty or loading UI and then the data.

## 🔵 सरल परिभाषा (Hindi)
Client-side React component में data लाने का बुनियादी तरीका है `useEffect` के अंदर `fetch` बुलाना, नतीजा `useState` में रखना, और उसी state से render करना। Effect पहले render के बाद चलता है, इसलिए user को पहले खाली या loading UI दिखती है और फिर data।

---

## 🔴 Problem it Solves

A component cannot be `async`, and you must not start network calls in the render body, because render can run many times and must stay pure. React needs a place for side effects (things outside rendering like network, timers, subscriptions). `useEffect` is that place: it runs after render and lets you start the request, then update state when the response arrives, which triggers a re-render with data.

```jsx
// PROBLEM 1: fetch in render body → new request on EVERY render → infinite loop
function Bad() {
  const [data, setData] = useState(null);
  fetch('/api/restaurants').then(r => r.json()).then(setData); // ❌ setData → re-render → fetch again
  return <p>{data?.length}</p>;
}

// PROBLEM 2: async effect callback → returns a Promise, but React expects a cleanup function
useEffect(async () => { /* ... */ }, []);   // ❌ not allowed

// SOLUTION: sync effect callback, async function inside, dependency array
useEffect(() => {
  async function load() { /* fetch + setState */ }
  load();
}, []);
```

## 🔴 यह क्यों बना? (Hindi)
Component `async` नहीं हो सकता, और render body में network call शुरू नहीं करनी चाहिए क्योंकि render कई बार चल सकता है और उसे pure रहना चाहिए। React को side effects (render के बाहर की चीज़ें जैसे network, timers, subscriptions) के लिए जगह चाहिए। `useEffect` वही जगह है: यह render के बाद चलता है, आप request शुरू करते हैं और response आने पर state update करते हैं जिससे data के साथ re-render होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → First render: state is empty (data = null), UI shows a placeholder
Step 2 → React commits the UI to the screen
Step 3 → useEffect runs: starts fetch(url)
Step 4 → Response arrives → res.ok check → res.json() → setData(json)
Step 5 → State changed → component re-renders with the data
Step 6 → If dependencies change (url, id) → cleanup runs → effect runs again with new values
Step 7 → On unmount (or before the next run) cleanup cancels or ignores the old request

IMPORTANT: fetch() does NOT reject on HTTP 404/500. You must check res.ok yourself.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहला render: state खाली है (data = null), UI में placeholder दिखता है
Step 2 → React UI को screen पर commit करता है
Step 3 → useEffect चलता है: fetch(url) शुरू होता है
Step 4 → Response आता है → res.ok जाँच → res.json() → setData(json)
Step 5 → State बदली → component data के साथ दोबारा render होता है
Step 6 → अगर dependencies (url, id) बदलीं → cleanup चलता है → effect नई values से दोबारा चलता है
Step 7 → Unmount पर (या अगले run से पहले) cleanup पुरानी request cancel या ignore करता है

IMPORTANT: fetch() HTTP 404/500 पर reject नहीं होता। res.ok आपको खुद जाँचना होगा।
```

---

## 🟡 Real World Example
**Swiggy restaurant list:** When the home page opens, the browser shows skeleton cards. `useEffect` calls `/api/restaurants?lat=..&lng=..`, and when JSON arrives the list renders. If the user changes city, `city` is in the dependency array, so the effect runs again, and the old request for the previous city must not overwrite the new data.

## 🟡 Real Example Hindi mein
**Swiggy restaurant list:** Home page खुलने पर browser skeleton cards दिखाता है। `useEffect` `/api/restaurants?lat=..&lng=..` बुलाता है, और JSON आने पर list render होती है। अगर user city बदले तो `city` dependency array में है, इसलिए effect दोबारा चलता है, और पिछली city की पुरानी request को नए data के ऊपर नहीं लिखना चाहिए।

---

## 💻 Code Example — Basic

```jsx
// Basic: fetch a list once when the component mounts
import { useState, useEffect } from 'react';             // hooks we need
import { createRoot } from 'react-dom/client';           // React 18/19 root API

function UserList() {
  const [users, setUsers] = useState([]);                // data from the server, starts empty

  useEffect(() => {                                      // runs after first render
    async function loadUsers() {                         // async function INSIDE the effect
      const res = await fetch('https://jsonplaceholder.typicode.com/users'); // start request
      const data = await res.json();                     // parse the JSON body
      setUsers(data);                                    // store it → triggers re-render
    }
    loadUsers();                                         // call it (effect itself stays sync)
  }, []);                                                // [] = run once after mount

  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}     {/* render each user, key = stable id */}
    </ul>
  );
}

createRoot(document.getElementById('root')).render(<UserList />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: res.ok check, AbortController cleanup, dependency on id, no stale responses
import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function RestaurantMenu({ restaurantId }) {
  const [menu, setMenu] = useState(null);                // fetched data
  const [loading, setLoading] = useState(true);          // request in progress?
  const [error, setError] = useState(null);              // last error, if any

  useEffect(() => {
    const controller = new AbortController();            // lets us cancel this request

    async function loadMenu() {
      setLoading(true);                                  // new id → show loading again
      setError(null);                                    // clear old error
      try {
        const res = await fetch(`/api/restaurants/${restaurantId}/menu`, {
          signal: controller.signal,                     // tie request to the controller
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`); // fetch does NOT throw on 404/500
        const json = await res.json();                   // parse body
        setMenu(json);                                   // success
      } catch (err) {
        if (err.name === 'AbortError') return;           // cancelled on purpose: ignore silently
        setError(err.message);                           // real failure: show it
      } finally {
        if (!controller.signal.aborted) setLoading(false); // don't touch state after cancel
      }
    }

    loadMenu();                                          // start
    return () => controller.abort();                     // cleanup: cancel when id changes/unmounts
  }, [restaurantId]);                                    // re-run for every new restaurant

  if (loading) return <p>Loading menu...</p>;            // loading UI
  if (error) return <p role="alert">Failed: {error}</p>; // error UI
  return (
    <ul>
      {menu.items.map(item => (
        <li key={item.id}>{item.name} - Rs {item.price}</li> // success UI
      ))}
    </ul>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantMenu restaurantId={42} />);
```

---

## 🟠 Next.js Connection

In the App Router you usually do **not** fetch in `useEffect`. A Server Component can be `async` and fetch directly, so the HTML already contains the data (better SEO, no loading flash, no client JavaScript for fetching). Use `useEffect + fetch` in Client Components only for browser-only data (geolocation, user-specific live data, data after a click).

```jsx
// app/restaurants/page.jsx (Server Component: async, no hooks)
export default async function Page() {
  const res = await fetch('https://api.example.com/restaurants', {
    next: { revalidate: 60 },                         // cache and refresh every 60 s
  });
  if (!res.ok) throw new Error('Failed to load');     // caught by the nearest error.jsx
  const restaurants = await res.json();               // data is ready BEFORE HTML is sent
  return <ul>{restaurants.map(r => <li key={r.id}>{r.name}</li>)}</ul>;
}
// Version-dependent: in Next.js 15 fetch is NOT cached by default; in 14 it was. Set it explicitly.
```

```jsx
// app/nearby/Nearby.jsx (Client Component: browser-only data in an effect)
'use client';
import { useState, useEffect } from 'react';
export default function Nearby() {
  const [pos, setPos] = useState(null);
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(p => setPos(p.coords)); // only exists in the browser
  }, []);
  return <p>{pos ? `${pos.latitude}, ${pos.longitude}` : 'Locating...'}</p>;
}
```

Re-render behavior: one render with empty state, one more after data arrives. Performance impact: the request starts only after JavaScript loads and the component renders, so the "waterfall" (HTML → JS → render → fetch) makes it slower than server fetching.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Missing dependency array → effect runs after every render → infinite request loop
✅ **Correct:** Always pass a dependency array

```jsx
// Wrong: no array. setData triggers re-render, which runs the effect again, forever
useEffect(() => { fetch(url).then(r => r.json()).then(setData); });       // ❌

// Right
useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]); // ✅
```

❌ **Mistake 2:** Not handling race conditions (old response arrives after the new one)
✅ **Correct:** Cancel with `AbortController` or use an `ignore` flag in cleanup

```jsx
// Wrong: user clicks id 1 then id 2; if response 1 is slower it overwrites response 2
useEffect(() => { fetch(`/api/p/${id}`).then(r => r.json()).then(setProduct); }, [id]); // ❌

// Right
useEffect(() => {
  let ignore = false;                                    // flag for THIS effect run
  fetch(`/api/p/${id}`).then(r => r.json()).then(d => { if (!ignore) setProduct(d); });
  return () => { ignore = true; };                       // cleanup marks it stale
}, [id]);                                                // ✅
```

❌ **Mistake 3:** Assuming `fetch` throws on HTTP errors
✅ **Correct:** Check `res.ok` (or `res.status`) and throw yourself

```jsx
// Wrong: a 500 response is parsed as if it were data
const data = await (await fetch(url)).json();            // ❌ error page JSON becomes "data"

// Right
const res = await fetch(url);
if (!res.ok) throw new Error(`HTTP ${res.status}`);      // ✅
const data = await res.json();
```

---

## 🧠 Tricky Interview Question

```jsx
import { StrictMode, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [n, setN] = useState(0);
  useEffect(() => {
    console.log('fetch start');
    fetch('/api/count').then(r => r.json()).then(d => setN(d.n));
  }, []);
  return <p>{n}</p>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
```
**Answer:** In **development**, `fetch start` is logged **twice** and two requests are sent. React 18+ StrictMode intentionally mounts, unmounts and mounts again to check that your effect has proper cleanup. In production there is only one call. This effect has no cleanup, so both responses call `setN` (harmless here, but wasteful and a bug source for non-idempotent requests like POST). Fix: add an `AbortController` or `ignore` cleanup so the first request is cancelled/ignored, or use a library (TanStack Query) that de-duplicates requests.

---

## ⚫ Interview Questions + Answers

Q1: Why do we fetch inside `useEffect` and not in the render body?
A1: Render must be pure and can run many times. A fetch in render would repeat on every render, and `setState` would cause an infinite loop. `useEffect` runs after commit, which is the correct place for side effects.

Q2: Why can't the effect callback be `async`?
A2: An `async` function returns a Promise, but React expects the callback to return nothing or a cleanup function. Define an async function inside the effect and call it.

Q3: What does the dependency array do?
A3: React compares it with the previous values after each render and re-runs the effect only if something changed. `[]` means run once after mount, and `[id]` means run again whenever `id` changes.

Q4: What is a race condition in fetching and how do you fix it?
A4: Responses can come back in a different order than requests. An older, slower response can overwrite newer data. Fix by aborting the previous request with `AbortController` or ignoring stale results with a flag set in the cleanup.

Q5: What are the weaknesses of `useEffect + fetch` and what replaces it?
A5: No caching, no de-duplication, no retry, no background refresh, and manual loading/error state, plus a client-side waterfall. Use TanStack Query/SWR on the client, or Server Components for initial data in Next.js.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Small apps, prototypes or one-off requests (analytics ping, geolocation lookup)
- Browser-only data that cannot be fetched on the server
- Learning how data fetching works under the hood

❌ **Avoid when:**
- Several components need the same data (no cache or sharing)
- You need retries, pagination, refetch on focus or optimistic updates (use TanStack Query)
- The data is needed for first paint and SEO (use Server Components or loaders)

---

## 📊 Visual Diagram

```
  Render #1 (data = null)  ──►  Commit to screen  ──►  useEffect runs
        │                                                  │
        ▼                                                  ▼
   shows "Loading..."                              fetch(url) ──► network ──► response
                                                                                │
                                                      res.ok? ── no ──► setError
                                                         │ yes
                                                         ▼
                                                    setData(json)
                                                         │
                                                         ▼
                                            Render #2 (data = [...]) ──► UI updated

  deps change (id: 1 → 2):  cleanup(abort #1) → effect runs again → fetch #2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Side effect | Work outside rendering (network, timers) | Render के बाहर का काम (network, timers) |
| fetch | Browser API to make HTTP requests | HTTP requests करने वाला browser API |
| res.ok | True when status is 200 to 299 | Status 200-299 होने पर true |
| Dependency array | Values that trigger a re-run of the effect | वे values जिनके बदलने पर effect दोबारा चलता है |
| AbortController | Cancels an in-flight request | चल रही request को रद्द करने वाला object |
| Race condition | Responses arriving in the wrong order | Responses का गलत क्रम में आना |
| StrictMode | Dev tool that double-runs effects | Dev में effects दो बार चलाने वाला tool |
| Waterfall | Steps that wait on each other | एक के बाद एक इंतज़ार करने वाले steps |

---

## ⚡ 3-Line Summary
**English:**
1. Fetch inside `useEffect`, keep results in `useState`, and use a dependency array so it does not loop.
2. Check `res.ok`, and cancel or ignore old requests in the cleanup to avoid race conditions.
3. It is simple but has no cache or retry, so use TanStack Query or Server Components for real apps.

**Hindi:**
1. `useEffect` में fetch करो, नतीजा `useState` में रखो, और dependency array दो ताकि loop न बने।
2. `res.ok` जाँचो, और race conditions से बचने के लिए cleanup में पुरानी requests cancel या ignore करो।
3. यह आसान है पर cache या retry नहीं है, इसलिए असली apps में TanStack Query या Server Components इस्तेमाल करो।

---

## ➡️ Next Topic
**108. Axios in React** — `fetch` में हर बार `res.ok` जाँचना और JSON parse करना पड़ता है। Axios यह काम आसान बनाता है (auto JSON, interceptors, timeout), इसलिए अगला topic उसी का है।
