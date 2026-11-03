# 108. Axios in React
# हिंदी में: React में Axios — HTTP Client Library

---

## 🔵 Simple Definition (English)
Axios is a popular JavaScript HTTP client library. It wraps XMLHttpRequest in the browser and the `http` module in Node, and gives a simpler API than `fetch`: automatic JSON parsing, errors thrown for non-2xx responses, timeouts, interceptors, and request cancellation.

## 🔵 सरल परिभाषा (Hindi)
Axios एक लोकप्रिय JavaScript HTTP client library है। यह browser में XMLHttpRequest और Node में `http` module को wrap करती है और `fetch` से आसान API देती है: automatic JSON parsing, non-2xx responses पर error throw, timeout, interceptors और request cancel।

---

## 🔴 Problem it Solves

With plain `fetch`, every call repeats the same boilerplate: build the base URL, set headers (auth token, content type), `JSON.stringify` the body, check `res.ok`, call `res.json()`, handle timeouts. In a big app this is copy-pasted in hundreds of places, and a change like "add the auth header" or "redirect to login on 401" must be done everywhere. Axios solves this with a shared **instance** and **interceptors**, which are functions that run on every request or response.

```jsx
// PROBLEM: repeated boilerplate with fetch
const res = await fetch('https://api.shop.com/orders', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
  body: JSON.stringify(order),
});
if (!res.ok) throw new Error(res.status);
const data = await res.json();

// SOLUTION: configure once, use everywhere
const { data } = await api.post('/orders', order);   // auth header + JSON handled by the instance
```

## 🔴 यह क्यों बना? (Hindi)
सादे `fetch` में हर call में वही boilerplate दोहराना पड़ता है: base URL बनाना, headers (auth token, content type) लगाना, body को `JSON.stringify` करना, `res.ok` जाँचना, `res.json()` बुलाना, timeout संभालना। बड़े app में यह सैकड़ों जगह copy-paste होता है, और "auth header जोड़ो" या "401 पर login पर भेजो" जैसा बदलाव हर जगह करना पड़ता है। Axios shared **instance** और **interceptors** (ऐसे functions जो हर request या response पर चलते हैं) से इसे हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install:  npm install axios
Step 2 → Create an instance:  axios.create({ baseURL, timeout, headers })
Step 3 → Add a REQUEST interceptor: attach the auth token to every outgoing request
Step 4 → Add a RESPONSE interceptor: handle 401 (logout/refresh) and normalize errors
Step 5 → Call api.get/post/put/delete(url, ...) → returns a Promise of a response object
Step 6 → response.data holds the parsed JSON (also response.status, response.headers)
Step 7 → Non-2xx status → promise REJECTS with error.response (status + data)
Step 8 → Cancel with AbortController: axios.get(url, { signal })
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install:  npm install axios
Step 2 → Instance बनाओ:  axios.create({ baseURL, timeout, headers })
Step 3 → REQUEST interceptor जोड़ो: हर जाने वाली request में auth token लगाओ
Step 4 → RESPONSE interceptor जोड़ो: 401 संभालो (logout/refresh) और errors normalize करो
Step 5 → api.get/post/put/delete(url, ...) बुलाओ → response object का Promise मिलता है
Step 6 → response.data में parsed JSON होता है (साथ में response.status, response.headers)
Step 7 → Non-2xx status → promise REJECT होता है, error.response में (status + data)
Step 8 → AbortController से cancel: axios.get(url, { signal })
```

---

## 🟡 Real World Example
**Amazon product page:** The app has a single `api` instance with `baseURL = https://api.shop.com`, a 10-second timeout and an interceptor that adds the user's token. When the token expires, the server answers 401, the response interceptor calls the refresh endpoint once, then retries the original request. Components just call `api.get('/products/' + id)` and never think about tokens.

## 🟡 Real Example Hindi mein
**Amazon product page:** App में एक ही `api` instance है जिसमें `baseURL = https://api.shop.com`, 10 सेकंड का timeout और एक interceptor है जो user का token जोड़ता है। Token expire होने पर server 401 देता है, response interceptor एक बार refresh endpoint बुलाता है और फिर original request दोबारा भेजता है। Components बस `api.get('/products/' + id)` बुलाते हैं और token के बारे में सोचते नहीं।

---

## 💻 Code Example — Basic

```jsx
// Basic: Axios GET inside useEffect with cleanup
import { useState, useEffect } from 'react';             // hooks
import axios from 'axios';                               // npm install axios
import { createRoot } from 'react-dom/client';           // React 18/19 root API

function PostList() {
  const [posts, setPosts] = useState([]);                // server data
  const [error, setError] = useState(null);              // error message

  useEffect(() => {
    const controller = new AbortController();            // for cancellation
    axios
      .get('https://jsonplaceholder.typicode.com/posts', {
        params: { _limit: 5 },                           // becomes ?_limit=5 automatically
        signal: controller.signal,                       // cancel support (Axios 0.22+)
      })
      .then(res => setPosts(res.data))                   // res.data is already parsed JSON
      .catch(err => {
        if (axios.isCancel(err)) return;                 // cancelled on purpose: ignore
        setError(err.message);                           // 404/500/network → rejected promise
      });
    return () => controller.abort();                     // cancel on unmount
  }, []);

  if (error) return <p>Error: {error}</p>;               // error UI
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>; // data UI
}

createRoot(document.getElementById('root')).render(<PostList />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: shared instance + interceptors (auth header, 401 refresh once) + API module + hook

// ---- api/client.js ----
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',        // Vite env; in Next use process.env.NEXT_PUBLIC_API_URL
  timeout: 10_000,                                        // fail after 10 seconds
  headers: { 'Content-Type': 'application/json' },        // default header
});

// Request interceptor: runs before EVERY request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');      // read the current token
  if (token) config.headers.Authorization = `Bearer ${token}`; // attach it
  return config;                                          // must return the config
});

let refreshing = null;                                    // shared promise so only ONE refresh runs

// Response interceptor: runs on EVERY response/error
api.interceptors.response.use(
  res => res,                                             // success: pass through unchanged
  async error => {
    const original = error.config;                        // the request that failed
    if (error.response?.status === 401 && !original._retried) {
      original._retried = true;                           // prevent infinite retry loop
      refreshing ??= axios.post('/api/auth/refresh', null, { withCredentials: true })
        .then(r => { localStorage.setItem('accessToken', r.data.accessToken); })
        .finally(() => { refreshing = null; });           // allow future refreshes
      await refreshing;                                   // wait for the single refresh
      return api(original);                               // retry the original request once
    }
    // Normalize the error message for the UI
    error.userMessage = error.response?.data?.message ?? 'Something went wrong';
    return Promise.reject(error);                         // keep it rejecting
  }
);

// ---- api/orders.js ---- thin functions, no React inside
export const getOrders = (params, signal) => api.get('/orders', { params, signal }).then(r => r.data);
export const createOrder = body => api.post('/orders', body).then(r => r.data);

// ---- hooks/useOrders.js ----
import { useState, useEffect } from 'react';
export function useOrders(status) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  useEffect(() => {
    const ctrl = new AbortController();                   // cancel stale requests
    setState(s => ({ ...s, loading: true, error: null }));
    getOrders({ status }, ctrl.signal)
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => {
        if (axios.isCancel(err)) return;                  // ignore our own abort
        setState({ data: null, loading: false, error: err.userMessage ?? err.message });
      });
    return () => ctrl.abort();
  }, [status]);                                           // re-fetch when filter changes
  return state;
}
```

---

## 🟠 Next.js Connection

In Server Components and Route Handlers you can use `fetch` (Next.js extends it with caching and revalidation) or Axios. Axios **does not** use Next's fetch cache, so you lose `next: { revalidate }` and tags. A good split is: native `fetch` on the server, Axios (or fetch) in Client Components for browser calls like mutations with interceptors. Never put secrets in `NEXT_PUBLIC_` variables, because they ship to the browser; call secret-key APIs from the server only.

```jsx
// app/lib/api.js: one instance used by client code
import axios from 'axios';
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,           // public value, safe in the browser
  withCredentials: true,                              // send httpOnly cookies (safer than localStorage)
});
```

```jsx
// app/cart/AddToCart.jsx
'use client';                                         // event handlers need a Client Component
import { useState } from 'react';
import { api } from '@/app/lib/api';
export default function AddToCart({ productId }) {
  const [busy, setBusy] = useState(false);
  async function add() {
    setBusy(true);                                    // disable button while sending
    try { await api.post('/cart', { productId }); }   // POST with JSON body, auto headers
    finally { setBusy(false); }                       // always re-enable
  }
  return <button disabled={busy} onClick={add}>{busy ? 'Adding...' : 'Add to cart'}</button>;
}
```

Re-render behavior is the same as `fetch` (state change causes render). Performance: Axios adds about 13 KB gzipped (version-dependent), so for tiny apps native `fetch` is enough.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting that the data is in `res.data`
✅ **Correct:** Use `res.data` (not `res.json()`)

```jsx
// Wrong
const res = await axios.get('/api/items');
const items = await res.json();           // ❌ TypeError: res.json is not a function
// Right
const { data: items } = await axios.get('/api/items');  // ✅
```

❌ **Mistake 2:** Creating a new Axios config in every file, or hardcoding the token in each call
✅ **Correct:** One shared instance with interceptors

```jsx
// Wrong: token logic copy-pasted
axios.get('/orders', { headers: { Authorization: `Bearer ${token}` } });   // ❌ everywhere
// Right
api.get('/orders');                                                         // ✅ interceptor adds it
```

❌ **Mistake 3:** Reading error details from the wrong place
✅ **Correct:** Check `error.response` (server replied), `error.request` (no reply), else config error

```jsx
// Wrong: crashes when the server is unreachable because error.response is undefined
catch (e) { setMsg(e.response.data.message); }       // ❌ TypeError
// Right
catch (e) { setMsg(e.response?.data?.message ?? e.message); }   // ✅ safe access
```

---

## 🧠 Tricky Interview Question

```jsx
import axios from 'axios';

async function run() {
  try {
    const res = await axios.get('/api/missing');   // server responds 404 with JSON { "message": "Not found" }
    console.log('A', res.status);
  } catch (e) {
    console.log('B', e.response.status, e.response.data.message);
  }

  const res2 = await fetch('/api/missing');        // same URL with fetch
  console.log('C', res2.status, res2.ok);
}
run();
```
**Answer:** It prints `B 404 Not found` and then `C 404 false`. Axios rejects the promise for any status outside 2xx (default `validateStatus`), so the `catch` runs and `A` is never printed. `fetch` resolves normally for 404 and only rejects on network failure, so you must check `res.ok` yourself. This difference is a classic interview point.

---

## ⚫ Interview Questions + Answers

Q1: Axios vs fetch, what are the main differences?
A1: Axios parses JSON automatically (`res.data`), rejects on non-2xx, supports interceptors, timeouts, progress events and instances, and works in Node and browsers. `fetch` is built in (no bundle cost), needs manual `res.ok` and `res.json()`, and in Next.js integrates with the server cache.

Q2: What are interceptors and where do you use them?
A2: Functions that run before every request or after every response. Use request interceptors to attach tokens, and response interceptors to handle 401 (refresh or logout), log errors, or normalize error messages.

Q3: How do you cancel an Axios request?
A3: Pass an `AbortController` signal: `axios.get(url, { signal: controller.signal })` and call `controller.abort()` in the effect cleanup. Check `axios.isCancel(err)` to ignore it. The old `CancelToken` API is deprecated.

Q4: How do you handle token refresh without an infinite loop?
A4: In the response interceptor catch 401, mark the request with a flag (`_retried`), run a single shared refresh promise, then retry the original request once. If refresh fails, log the user out.

Q5: Where should the Axios code live in a React app?
A5: Create the instance in one module, write thin API functions per feature (`getOrders`, `createOrder`), and call those from hooks or TanStack Query's `queryFn`. Components should not know about URLs or headers.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need interceptors (auth, logging, retry) across a large app
- You want automatic JSON, timeouts and upload/download progress
- You share code between browser and Node (SSR, scripts)

❌ **Avoid when:**
- A small app only needs a few simple GETs (native `fetch` is enough)
- You need Next.js fetch cache, tags and revalidation (use `fetch` on the server)
- Bundle size is critical (use `fetch` with a tiny wrapper)

---

## 📊 Visual Diagram

```
  Component ──► api.get('/orders')
                    │
                    ▼
        ┌─ Request interceptor ─┐   adds Authorization header, logs
        └───────────┬───────────┘
                    ▼
                 NETWORK ───────► Server
                    ▲                │
                    │                ▼
        ┌─ Response interceptor ─┐   2xx → pass through
        │                        │   401 → refresh token → retry once
        └───────────┬────────────┘   other → reject with friendly message
                    ▼
        resolve(res.data)  or  reject(error)  ──►  Component (setState)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Axios | HTTP client library | HTTP client library |
| Instance | Pre-configured Axios object | पहले से configured Axios object |
| Interceptor | Function run on every request/response | हर request/response पर चलने वाला function |
| baseURL | Prefix added to every request URL | हर request URL के आगे लगने वाला prefix |
| res.data | Parsed response body | Parse किया हुआ response body |
| validateStatus | Decides which status codes are success | कौन से status codes success हैं यह तय करता है |
| Timeout | Max wait time before failing | Fail होने से पहले अधिकतम इंतज़ार |
| Token refresh | Getting a new access token silently | चुपचाप नया access token लेना |

---

## ⚡ 3-Line Summary
**English:**
1. Axios is an HTTP client with automatic JSON, rejection on non-2xx, timeouts and interceptors.
2. Create one shared instance, add auth and 401 handling in interceptors, and call it from thin API functions.
3. In Next.js prefer native `fetch` on the server for caching, and use Axios mainly in Client Components.

**Hindi:**
1. Axios एक HTTP client है जिसमें automatic JSON, non-2xx पर rejection, timeouts और interceptors हैं।
2. एक shared instance बनाओ, auth और 401 handling interceptors में रखो, और पतले API functions से बुलाओ।
3. Next.js में caching के लिए server पर native `fetch` चुनो, और Axios मुख्य रूप से Client Components में इस्तेमाल करो।

---

## ➡️ Next Topic
**109. Loading + Error States** — चाहे fetch हो या Axios, UI को तीन अवस्थाएँ संभालनी होती हैं: loading, error और success। अगला topic इन्हें साफ तरीके से manage करना सिखाता है।
