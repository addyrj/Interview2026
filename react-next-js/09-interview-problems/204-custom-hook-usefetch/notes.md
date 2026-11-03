# 204. Build Custom Hook — useFetch
# हिंदी में: Custom Hook — useFetch बनाना

> Code: [useFetch.js](./useFetch.js) (complete, tested with jsdom: success, HTTP 404 error, loading flag)

---

## 🔵 Simple Definition (English)
**useFetch** is a custom hook that loads data from a URL and gives your component `data`, `loading` and `error`. It also cancels outdated requests so old responses never overwrite new ones.

## 🔵 सरल परिभाषा (Hindi)
**useFetch** एक custom hook है जो URL से data लाता है और component को `data`, `loading` और `error` देता है। यह पुराने requests को cancel भी करता है ताकि पुराना response नए response को overwrite न करे।

---

## 🔴 Problem it Solves
Every screen that loads data repeats the same three `useState` calls, a `useEffect`, and error handling. Doing it by hand also hides two bugs: **race conditions** (a slow old response arrives after a fast new one) and **state updates after unmount**. A hook wraps the logic once and fixes these bugs for every component.

## 🔴 यह क्यों बना? (Hindi)
जो भी screen data लोड करती है, वह वही तीन `useState`, एक `useEffect` और error handling दोहराती है। हाथ से लिखने पर दो bugs भी छिपे रहते हैं: **race condition** (धीमा पुराना response तेज़ नए response के बाद आ जाए) और **unmount के बाद state update**। Hook यह logic एक बार लपेटकर हर component के लिए ये bugs ठीक कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State holds { data, error, loading } in one object
Step 2 → useEffect depends on [url, options, tick] and starts a fetch
Step 3 → An AbortController is created; its signal is passed to fetch
Step 4 → res.ok is checked manually (fetch only rejects on network failure)
Step 5 → Cleanup calls controller.abort(), so changing url cancels the old request
Step 6 → AbortError is ignored; real errors set error; refetch() bumps a counter

Re-render: url change → effect cleanup (abort) → new effect → loading=true render →
data arrives → setState → one more render. Component renders 2 to 3 times per request.
Performance: no caching or dedup here. For real apps use TanStack Query v5, which adds
caching, retries, background refresh and request deduplication.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State एक object में { data, error, loading } रखती है
Step 2 → useEffect [url, options, tick] पर depend करता है और fetch शुरू करता है
Step 3 → AbortController बनता है; उसका signal fetch को दिया जाता है
Step 4 → res.ok हाथ से जाँचा जाता है (fetch सिर्फ network failure पर reject होता है)
Step 5 → Cleanup controller.abort() बुलाता है, इसलिए url बदलने पर पुराना request रद्द हो जाता है
Step 6 → AbortError अनदेखा होता है; असली error से error सेट होता है; refetch() counter बढ़ाता है

Re-render: url बदला → effect cleanup (abort) → नया effect → loading=true render →
data आया → setState → एक और render। हर request पर component 2 से 3 बार render होता है।
Performance: यहाँ caching या dedup नहीं है। असली apps में TanStack Query v5 इस्तेमाल करो, जो
caching, retries, background refresh और request deduplication देता है।
```

---

## 🟡 Real World Example
**Zomato restaurant list:** when you change the city from Delhi to Mumbai, the app fires a new request. If the Delhi response comes back late, it must be ignored, or you would see Delhi restaurants under the Mumbai heading. `useFetch` aborts the Delhi request when the city changes.

## 🟡 Real Example Hindi mein
**Zomato restaurant list:** city Delhi से Mumbai करने पर app नया request भेजता है। Delhi का response देर से लौटे तो उसे अनदेखा करना ज़रूरी है, वरना Mumbai के heading के नीचे Delhi के restaurants दिखेंगे। City बदलते ही `useFetch` Delhi का request abort कर देता है।

---

## 💻 Code Example — Basic

```jsx
// Basic useFetch (no cancel): good for learning
import { useState, useEffect } from 'react';               // hooks

function useFetch(url) {
  const [data, setData] = useState(null);                  // response body
  const [loading, setLoading] = useState(true);            // request in progress
  const [error, setError] = useState(null);                // failure

  useEffect(() => {
    setLoading(true);                                      // new url → loading again
    fetch(url)                                             // start the request
      .then((res) => res.json())                           // parse JSON
      .then(setData)                                       // save data
      .catch(setError)                                     // save error
      .finally(() => setLoading(false));                   // always stop loading
  }, [url]);                                               // re-run when url changes

  return { data, loading, error };
}
```

## 💻 Code Example — Advanced

```jsx
// Production version (useFetch.js): abort, HTTP errors, stable options, refetch
import { useState, useEffect, useCallback } from 'react';

export function useFetch(url, options) {
  const [state, setState] = useState({ data: null, error: null, loading: Boolean(url) });
  const [tick, setTick] = useState(0);                     // bump = refetch
  const optionsKey = JSON.stringify(options ?? null);      // options object is new every render

  useEffect(() => {
    if (!url) return undefined;                            // skip when url is falsy
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: null }));// keep old data while reloading

    fetch(url, { ...JSON.parse(optionsKey), signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`); // 404/500 do NOT reject by themselves
        return res.json();
      })
      .then((data) => setState({ data, error: null, loading: false }))
      .catch((error) => {
        if (error.name === 'AbortError') return;           // we cancelled it: not an error
        setState((s) => ({ ...s, error, loading: false }));
      });

    return () => controller.abort();                       // cancel on url change/unmount
  }, [url, optionsKey, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);
  return { ...state, refetch };
}

// Usage
// const { data, loading, error, refetch } = useFetch(`/api/restaurants?city=${city}`);
```

---

## 🟠 Next.js Connection
In the App Router you often **do not need** `useFetch`. A Server Component can `await fetch()` directly, with caching and no loading spinner code. Use a client hook only for data that depends on browser interaction (live search, polling, user-triggered refresh). For those cases prefer TanStack Query or SWR over a hand-written hook.

```jsx
// app/restaurants/page.jsx (Server Component): no hook, no useEffect, no loading state
export default async function Page({ searchParams }) {
  const { city = 'delhi' } = await searchParams;           // Next.js 15: searchParams is a Promise
  const res = await fetch(`https://api.example.com/restaurants?city=${city}`, {
    next: { revalidate: 60 },                              // cache for 60 seconds (Next.js 14/15 option)
  });
  const restaurants = await res.json();                    // data is ready before HTML is sent
  return <ul>{restaurants.map((r) => <li key={r.id}>{r.name}</li>)}</ul>;
}
// Note: default caching of fetch changed between Next.js 14 and 15: set it explicitly (version-dependent).
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** No cleanup, so old responses overwrite new ones (race condition)
✅ **Correct:** Abort in the cleanup function

```jsx
// Wrong
useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]);
// Right
useEffect(() => {
  const c = new AbortController();
  fetch(url, { signal: c.signal }).then(r => r.json()).then(setData).catch(() => {});
  return () => c.abort();
}, [url]);
```

❌ **Mistake 2:** Assuming `fetch` rejects on 404 or 500
✅ **Correct:** Check `res.ok`

```jsx
// Wrong: a 500 page is parsed as data (or throws a confusing JSON error)
const data = await (await fetch(url)).json();
// Right
const res = await fetch(url); if (!res.ok) throw new Error(`HTTP ${res.status}`);
```

❌ **Mistake 3:** Putting an inline `options` object in the dependency array
✅ **Correct:** Serialise it, or keep options stable with `useMemo`

```jsx
// Wrong: new object every render → effect runs every render → infinite fetch loop
useEffect(() => { fetch(url, options)... }, [url, options]);
// Right: depend on JSON.stringify(options) as the hook does
```

---

## 🧠 Tricky Interview Question

```jsx
function List() {
  const { data } = useFetch('/api/items', { headers: { 'X-Token': 'abc' } }); // naive hook
  return <p>{data?.length}</p>;
}
// naive hook: useEffect(() => { ...fetch(url, options)... setData(json) }, [url, options]);
```
**Answer:** An infinite request loop. The object literal `{ headers: ... }` is a new object on every render, so `options` fails the `Object.is` check and the effect re-runs. Each response calls `setData`, which re-renders, which creates a new `options`, which fetches again. Fix: serialise options for the dependency (as in `useFetch.js`), memoise them with `useMemo`, or define them outside the component.

---

## ⚫ Interview Questions + Answers

Q1: Why do we need `AbortController` in a fetch hook?
A1: To cancel the request when the component unmounts or the URL changes. It prevents race conditions and state updates from stale responses, and saves bandwidth.

Q2: Does `fetch` reject on HTTP errors?
A2: No. It rejects only on network failure or abort. For 404/500 the promise resolves with `res.ok === false`, so you must check and throw yourself.

Q3: What is a race condition in data fetching?
A3: Two requests are in flight and the older one finishes last, so its data replaces the newer data. Aborting (or ignoring) outdated requests in the effect cleanup fixes it.

Q4: Why is this not enough for production?
A4: There is no caching, deduplication, retry, pagination or background refetch, and each component fetches separately. Use TanStack Query v5, SWR or RTK Query.

Q5: In React 18 StrictMode my effect runs twice in dev. Is that a bug?
A5: No. Dev StrictMode mounts, unmounts and remounts to expose missing cleanup. With abort in cleanup, the first request is cancelled and the second completes, which is the correct behaviour. It does not happen in production.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Learning, small demos, or an interview whiteboard
- A tiny app with one or two simple GET calls

❌ **Avoid when:**
- You need caching, retries or shared data (use TanStack Query / SWR)
- You can fetch in a Server Component instead (Next.js)
- Mutations are involved (use Server Actions or `useMutation`)

---

## 📊 Visual Diagram

```
  url="/delhi" ──► effect #1 ─ fetch ───────────────► (slow...)
  url="/mumbai"──► cleanup #1: abort() ✖
                   effect #2 ─ fetch ─► response ─► setState ✔  (UI shows Mumbai)
                   late Delhi response is rejected with AbortError → ignored

  state machine:  idle ─► loading ─► success { data }
                              └────► error { error }   ──refetch()──► loading
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Function starting with `use` that reuses logic | `use` से शुरू होने वाला reusable logic function |
| AbortController | Browser API to cancel requests | Request रद्द करने वाला browser API |
| Race condition | Older result overwrites a newer one | पुराना नतीजा नए को overwrite कर दे |
| Cleanup function | Function returned from useEffect | useEffect से लौटाया गया function |
| res.ok | True for status 200 to 299 | Status 200 से 299 पर true |
| Refetch | Run the request again on demand | माँगने पर request दोबारा चलाना |
| Stale response | Reply for a request that is no longer needed | ऐसा जवाब जिसकी अब ज़रूरत नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. `useFetch` wraps loading, error and data state around `fetch` inside `useEffect`.
2. Abort in cleanup, check `res.ok`, and keep the options dependency stable to avoid races and loops.
3. In Next.js prefer Server Components for fetching, and TanStack Query for client-side needs.

**Hindi:**
1. `useFetch` `useEffect` के अंदर `fetch` के चारों ओर loading, error और data state लपेटता है।
2. Cleanup में abort करो, `res.ok` जाँचो, और options dependency को stable रखो ताकि race और loops न हों।
3. Next.js में fetching के लिए Server Components पसंद करो, और client-side ज़रूरत के लिए TanStack Query।

---

## ➡️ Next Topic
**205. Build Custom Hook — useLocalStorage** — अब state को browser storage से जोड़ना: JSON, SSR safety और tabs के बीच sync।
