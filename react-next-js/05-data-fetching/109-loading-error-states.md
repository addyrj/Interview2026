# 109. Loading + Error States
# हिंदी में: Loading और Error States — हर Request की तीन अवस्थाएँ

---

## 🔵 Simple Definition (English)
Every network request has at least three outcomes the UI must show: **loading** (waiting), **error** (failed) and **success** (data arrived). Good UIs also handle **empty** data and **refetching**. Handling these states properly prevents blank screens, crashes and confusing behavior.

## 🔵 सरल परिभाषा (Hindi)
हर network request के कम से कम तीन नतीजे होते हैं जो UI को दिखाने होते हैं: **loading** (इंतज़ार), **error** (फेल) और **success** (data आ गया)। अच्छा UI **empty** data और **refetching** भी संभालता है। इन्हें सही से संभालने पर blank screen, crash और confusing behavior नहीं होते।

---

## 🔴 Problem it Solves

Network is slow and unreliable. If you render `data.map(...)` while `data` is still `null`, the app crashes with "Cannot read properties of null". If the request fails and you show nothing, users see a blank page and do not know what to do. Developers often use several booleans (`isLoading`, `isError`, `isSuccess`) which can become impossible combinations (loading and error both true). A single **status** value makes states exclusive and easy to render.

```jsx
// PROBLEM: no states → crashes while loading, blank on error
function Orders() {
  const [orders, setOrders] = useState(null);
  useEffect(() => { fetch('/api/orders').then(r => r.json()).then(setOrders); }, []);
  return <ul>{orders.map(o => <li key={o.id}>{o.name}</li>)}</ul>;   // ❌ orders is null at first
}

// SOLUTION: one status: 'loading' | 'error' | 'success', render each explicitly
if (status === 'loading') return <Skeleton />;
if (status === 'error') return <ErrorBox onRetry={load} />;
if (data.length === 0) return <Empty />;
return <List items={data} />;
```

## 🔴 यह क्यों बना? (Hindi)
Network धीमा और अनिश्चित होता है। अगर `data` अभी `null` हो और आप `data.map(...)` render करें तो app "Cannot read properties of null" से crash हो जाता है। अगर request फेल हो और आप कुछ न दिखाएँ तो user को blank page दिखता है और उसे पता नहीं चलता कि क्या करना है। Developers अक्सर कई booleans (`isLoading`, `isError`, `isSuccess`) रखते हैं जिनके असंभव combinations (loading और error दोनों true) बन सकते हैं। एक **status** value states को अलग-अलग रखती है और render करना आसान बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Model the state:  status = 'idle' | 'loading' | 'success' | 'error'  (plus data, error)
Step 2 → Before the request: set status 'loading' and clear the old error
Step 3 → On success: set data and status 'success'
Step 4 → On failure (network error OR !res.ok): set error and status 'error'
Step 5 → Render in order: loading → error → empty → success (early returns)
Step 6 → Give the error UI a Retry button that runs the load function again
Step 7 → For production: show skeletons (not spinners) and keep old data during refetch
Step 8 → Add an Error Boundary for unexpected render crashes (it does NOT catch async/fetch errors)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State model बनाओ:  status = 'idle' | 'loading' | 'success' | 'error'  (साथ में data, error)
Step 2 → Request से पहले: status 'loading' करो और पुराना error हटाओ
Step 3 → Success पर: data सेट करो और status 'success'
Step 4 → Failure पर (network error या !res.ok): error सेट करो और status 'error'
Step 5 → इस क्रम में render करो: loading → error → empty → success (early returns)
Step 6 → Error UI में Retry बटन दो जो load function दोबारा चलाए
Step 7 → Production में spinner की जगह skeleton दिखाओ और refetch के दौरान पुराना data रखो
Step 8 → अनपेक्षित render crashes के लिए Error Boundary लगाओ (यह async/fetch errors नहीं पकड़ता)
```

---

## 🟡 Real World Example
**Zomato order history:** While orders load, the page shows grey skeleton rows. If the network drops, it shows "Could not load your orders" with a Retry button. A new user with no orders sees "You haven't ordered yet, explore restaurants" (the empty state). Pull-to-refresh keeps the old list on screen and only shows a small spinner at the top (refetching state).

## 🟡 Real Example Hindi mein
**Zomato order history:** Orders लोड होते समय page पर grey skeleton rows दिखती हैं। Network चला जाए तो "Could not load your orders" और Retry बटन दिखता है। जिस नए user के कोई order नहीं हैं उसे "You haven't ordered yet, explore restaurants" दिखता है (empty state)। Pull-to-refresh पुरानी list screen पर रखता है और ऊपर सिर्फ छोटा spinner दिखाता है (refetching state)।

---

## 💻 Code Example — Basic

```jsx
// Basic: loading, error, success with a Retry button
import { useState, useEffect, useCallback } from 'react';   // hooks
import { createRoot } from 'react-dom/client';              // React 18/19 root API

function Orders() {
  const [status, setStatus] = useState('loading');          // one source of truth for UI state
  const [orders, setOrders] = useState([]);                 // data
  const [error, setError] = useState('');                   // message for the user

  const load = useCallback(async () => {                    // reusable so Retry can call it
    setStatus('loading');                                   // show loading UI
    try {
      const res = await fetch('/api/orders');               // request
      if (!res.ok) throw new Error(`Server said ${res.status}`); // treat HTTP errors as errors
      setOrders(await res.json());                          // save data
      setStatus('success');                                 // show data UI
    } catch (e) {
      setError(e.message);                                  // keep message
      setStatus('error');                                   // show error UI
    }
  }, []);

  useEffect(() => { load(); }, [load]);                     // load on mount

  if (status === 'loading') return <p>Loading orders...</p>;        // 1) loading
  if (status === 'error')                                           // 2) error
    return <div role="alert"><p>{error}</p><button onClick={load}>Retry</button></div>;
  if (orders.length === 0) return <p>No orders yet.</p>;            // 3) empty
  return <ul>{orders.map(o => <li key={o.id}>{o.name}</li>)}</ul>; // 4) success
}

createRoot(document.getElementById('root')).render(<Orders />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: reusable useAsync hook (useReducer = impossible states), skeleton, Error Boundary
import { useReducer, useEffect, useCallback, useRef, Component } from 'react';
import { createRoot } from 'react-dom/client';

// Reducer: only valid transitions exist, so loading and error can never both be true
function reducer(state, action) {
  switch (action.type) {
    case 'start':   return { ...state, status: 'loading', error: null };      // keep old data (refetch)
    case 'success': return { status: 'success', data: action.data, error: null };
    case 'error':   return { ...state, status: 'error', error: action.error };
    default:        return state;
  }
}

function useAsync(asyncFn) {
  const [state, dispatch] = useReducer(reducer, { status: 'loading', data: null, error: null });
  const fnRef = useRef(asyncFn);                            // always latest function, no effect loop
  fnRef.current = asyncFn;

  const run = useCallback(async () => {
    dispatch({ type: 'start' });
    try {
      dispatch({ type: 'success', data: await fnRef.current() }); // success
    } catch (error) {
      dispatch({ type: 'error', error });                   // failure
    }
  }, []);

  useEffect(() => { run(); }, [run]);                       // initial load
  return { ...state, retry: run };                          // retry = run again
}

// Skeleton: layout placeholder that avoids a layout jump
const Skeleton = () => (
  <ul aria-busy="true">
    {[1, 2, 3].map(i => <li key={i} style={{ height: 20, margin: 8, background: '#eee' }} />)}
  </ul>
);

function Orders() {
  const { status, data, error, retry } = useAsync(async () => {
    const res = await fetch('/api/orders');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  });

  if (status === 'loading' && !data) return <Skeleton />;  // first load only
  if (status === 'error')
    return (
      <div role="alert">
        <p>Could not load orders: {error.message}</p>
        <button onClick={retry}>Try again</button>
      </div>
    );
  if (data.length === 0) return <p>You haven't ordered yet.</p>;
  return (
    <>
      {status === 'loading' && <small>Refreshing...</small>}  {/* refetch keeps old list visible */}
      <ul>{data.map(o => <li key={o.id}>{o.name}</li>)}</ul>
    </>
  );
}

// Error Boundary: catches errors thrown DURING RENDER (not in async code or event handlers)
class ErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }  // switch to fallback UI
  componentDidCatch(err, info) { console.error(err, info); }        // log to Sentry etc.
  render() { return this.state.hasError ? <p>Something broke.</p> : this.props.children; }
}

createRoot(document.getElementById('root')).render(<ErrorBoundary><Orders /></ErrorBoundary>);
```

---

## 🟠 Next.js Connection

The App Router has file conventions for these states, so you do not write the boolean logic by hand. `loading.js` is shown automatically (Suspense) while a server page streams, `error.js` is an Error Boundary for the segment (must be a Client Component), and `not-found.js` handles missing data. `Suspense` lets you stream parts of a page with their own fallbacks.

```jsx
// app/orders/loading.jsx: shown instantly while page.jsx awaits data
export default function Loading() {
  return <p aria-busy="true">Loading orders...</p>;
}
```

```jsx
// app/orders/error.jsx: must be a Client Component
'use client';
export default function Error({ error, reset }) {          // reset() re-renders the segment
  return (
    <div role="alert">
      <p>Failed: {error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

```jsx
// app/orders/page.jsx: Server Component, throwing here triggers error.jsx
export default async function Page() {
  const res = await fetch('https://api.example.com/orders', { cache: 'no-store' }); // always fresh
  if (!res.ok) throw new Error('Could not load orders');   // caught by error.jsx
  const orders = await res.json();
  if (orders.length === 0) return <p>No orders yet.</p>;   // empty state
  return <ul>{orders.map(o => <li key={o.id}>{o.name}</li>)}</ul>;
}
```

Note: in production builds, error messages thrown on the server are hidden from the client for security, and only a generic message with a `digest` is shown. Re-render behavior: with `loading.js` the loading UI is HTML from the server, so no extra client render is needed.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rendering data before it exists
✅ **Correct:** Return early for loading and error, or use optional chaining and defaults

```jsx
// Wrong
return <p>{user.name}</p>;                 // ❌ user is null on first render
// Right
if (!user) return <Spinner />;             // ✅
return <p>{user.name}</p>;
```

❌ **Mistake 2:** Several booleans that can contradict each other, and a stuck loading flag after an error
✅ **Correct:** Use one status, and always reset it in `finally` or in every branch

```jsx
// Wrong: if fetch throws, setLoading(false) never runs → spinner forever
setLoading(true);
const data = await getData();             // ❌ throws
setLoading(false);
// Right
setLoading(true);
try { setData(await getData()); }
catch (e) { setError(e); }
finally { setLoading(false); }            // ✅ runs in both cases
```

❌ **Mistake 3:** Thinking an Error Boundary catches fetch errors
✅ **Correct:** Boundaries catch render errors only. Catch async errors yourself and store them in state (or rethrow in render)

```jsx
// Wrong: this error is thrown asynchronously, outside render → boundary does NOT catch it
useEffect(() => { fetch('/x').then(() => { throw new Error('boom'); }); }, []);   // ❌
// Right: store it, then throw during render if you want the boundary to handle it
const [err, setErr] = useState(null);
useEffect(() => { fetch('/x').catch(setErr); }, []);
if (err) throw err;                                                                // ✅ now boundary catches
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';

function App() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/404-page')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); });
  }, []);

  if (loading) return <p>Loading...</p>;
  return <p>{data.title}</p>;
}
```
**Answer:** Assume the server returns a 500 with an HTML body (or the network drops). Then `r.json()` throws (or `fetch` rejects) and nothing handles the rejection, so `setLoading(false)` never runs. The user sees "Loading..." forever, and the browser console shows an unhandled promise rejection. Even a 404 with a JSON body would be treated as success because `fetch` does not reject on HTTP errors, and `data.title` could be `undefined`. Fix: check `res.ok`, add `.catch` or `try/catch`, and set `loading` to `false` in `finally`.

---

## ⚫ Interview Questions + Answers

Q1: What states should a data-driven UI handle?
A1: Loading (first load), error (with retry), empty (no data), success, and refetching (old data visible while updating). Some also add idle (not started yet) and offline.

Q2: Why use one `status` instead of `isLoading` and `isError` booleans?
A2: Separate booleans allow impossible combinations (both true) and need to be updated together. One status (or a reducer or a discriminated union) makes only valid states possible.

Q3: Where do Error Boundaries help and where not?
A3: They catch errors during rendering, lifecycle methods and constructors of the tree below them. They do not catch errors in event handlers, async code (fetch, setTimeout) or the boundary itself. For those, use try/catch and state.

Q4: Skeleton vs spinner?
A4: Skeletons mimic the final layout, so the page feels faster and avoids layout shift. Spinners suit short actions (button submit). Use skeletons for page or list loading.

Q5: How does Next.js App Router handle loading and error?
A5: `loading.js` wraps the page in a Suspense boundary and streams the fallback immediately. `error.js` is a Client Component Error Boundary with a `reset` function. `not-found.js` handles `notFound()`. Each applies to its route segment.

---

## 🔷 When to Use + When Not to Use
✅ **Use explicit state handling when:**
- Any component depends on network data (always)
- You want a Retry option and clear messages for users
- You want to avoid layout shift with skeletons

❌ **Avoid hand-written state handling when:**
- You use TanStack Query, SWR or RTK Query (they give `isPending`, `isError`, `data`, `error`)
- You use Next.js `loading.js` and `error.js` for route-level states

---

## 📊 Visual Diagram

```
              ┌──────────┐   start    ┌───────────┐
   mount ───► │ loading  │ ─────────► │  request  │
              └──────────┘            └─────┬─────┘
                   ▲                        │
        retry()    │            ┌───────────┴───────────┐
                   │          res.ok                  failed / !res.ok
                   │            ▼                        ▼
              ┌────┴─────┐  ┌─────────┐            ┌─────────┐
              │  error   │  │ success │            │  error  │
              └──────────┘  └────┬────┘            └─────────┘
                                 │
                       data.length === 0 ? ──► Empty state
                                          └──► List

  Render order: loading → error → empty → success
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Loading state | UI while waiting for data | Data का इंतज़ार करते समय का UI |
| Error state | UI shown when a request fails | Request फेल होने पर दिखने वाला UI |
| Empty state | UI when the result has no items | जब result में कोई item न हो तब का UI |
| Skeleton | Grey placeholder shaped like content | Content जैसा grey placeholder |
| Retry | Try the request again | Request दोबारा करना |
| Error Boundary | Class component catching render errors | Render errors पकड़ने वाला class component |
| Refetching | Updating data while old data is visible | पुराना data दिखाते हुए नया लाना |
| Suspense | React feature to show fallback while waiting | इंतज़ार में fallback दिखाने वाला React feature |

---

## ⚡ 3-Line Summary
**English:**
1. Every request has loading, error, empty and success states, and the UI must render each one.
2. Use one status value, check `res.ok`, reset loading in `finally`, and give errors a Retry button.
3. Error Boundaries catch only render errors, and Next.js gives `loading.js` and `error.js` for route-level states.

**Hindi:**
1. हर request की loading, error, empty और success states होती हैं, और UI को हर एक render करनी चाहिए।
2. एक status value रखो, `res.ok` जाँचो, loading को `finally` में reset करो, और errors में Retry दो।
3. Error Boundaries सिर्फ render errors पकड़ते हैं, और Next.js route-level states के लिए `loading.js` व `error.js` देता है।

---

## ➡️ Next Topic
**110. React Query (TanStack Query)** — Loading, error, retry और caching का यह सारा boilerplate हाथ से लिखना थकाने वाला है। TanStack Query यह सब खुद संभालती है, इसलिए अगला topic उसका परिचय है।
