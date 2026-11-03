# 37. useEffect Dependency Array
# हिंदी में: useEffect Dependency Array — Effect कब दोबारा चलेगा

---

## 🔵 Simple Definition (English)
The **dependency array** is the second argument of `useEffect`. It lists every reactive value (props, state, values derived from them) that the effect reads. React re-runs the effect only when one of these values changed (compared with `Object.is`).

## 🔵 सरल परिभाषा (Hindi)
**Dependency array** `useEffect` का दूसरा argument है। इसमें वे सभी reactive values (props, state और उनसे बनी values) लिखी जाती हैं जिन्हें effect पढ़ता है। इनमें से कोई value बदलने पर ही React effect को दोबारा चलाता है (तुलना `Object.is` से होती है)।

---

## 🔴 Problem it Solves

Without a dependency array, an effect runs after **every** render. A search box that calls an API inside such an effect would fetch again on every keystroke, every parent re-render and even after the fetch's own `setState`. That can create an infinite loop. The other extreme, an empty array `[]` with stale values, shows old data.

The array gives you control: "run this effect when `query` changes, not otherwise".

```jsx
// PROBLEM 1: no array → runs after EVERY render → infinite loop
useEffect(() => {
  fetch('/api/items').then(r => r.json()).then(setItems); // setItems re-renders → effect runs again → loop
});

// PROBLEM 2: [] but reads query → stale closure, shows results of the first query forever
useEffect(() => {
  search(query);
}, []); // eslint-disable-line react-hooks/exhaustive-deps  ❌ lying to React

// SOLUTION: list what the effect reads
useEffect(() => {
  search(query);
}, [query]); // ✅ re-runs only when query changes
```

## 🔴 यह क्यों बना? (Hindi)
Dependency array के बिना effect **हर** render के बाद चलता है। ऐसे effect में API call वाला search box हर keystroke, हर parent re-render और fetch के अपने `setState` के बाद भी दोबारा fetch करेगा, जिससे infinite loop बन सकता है। दूसरी तरफ़ खाली array `[]` के साथ पुरानी (stale) values पढ़ने पर पुराना data दिखता है।

Array से आपको control मिलता है: "यह effect तब चलाओ जब `query` बदले, वरना नहीं"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Render happens: your component function runs and returns JSX
Step 2 → React commits to the DOM, then looks at each useEffect
Step 3 → It compares the NEW deps array with the PREVIOUS one, item by item, using Object.is
Step 4 → All items equal → skip the effect (cleanup does not run either)
Step 5 → Any item differs → run cleanup of the old effect, then run the new effect
Step 6 → No array at all → always run. Empty array [] → run only once after mount

THREE FORMS:
  useEffect(fn)        → after every render
  useEffect(fn, [])    → after first mount only (React 18 StrictMode dev: runs twice)
  useEffect(fn, [a,b]) → after mount and whenever a or b changes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Render होता है: आपका component function चलता है और JSX return करता है
Step 2 → React DOM में commit करता है, फिर हर useEffect को देखता है
Step 3 → वह NEW deps array की PREVIOUS array से एक-एक item की Object.is से तुलना करता है
Step 4 → सारे items बराबर हों → effect skip (cleanup भी नहीं चलता)
Step 5 → कोई item अलग हो → पुराने effect का cleanup चलता है, फिर नया effect
Step 6 → array बिल्कुल न हो → हर बार चलेगा। खाली array [] → mount के बाद सिर्फ़ एक बार

तीन रूप:
  useEffect(fn)        → हर render के बाद
  useEffect(fn, [])    → सिर्फ़ पहले mount के बाद (React 18 StrictMode dev में दो बार)
  useEffect(fn, [a,b]) → mount पर और जब भी a या b बदले
```

---

## 🟡 Real World Example
**Zomato search:** You type "biryani" in the search box. The results effect depends on `[query, city]`. When you type, `query` changes and the effect fetches. When you change the city from Delhi to Pune, `city` changes and it fetches again. If an unrelated piece of state (like whether the cart drawer is open) changes, nothing is fetched, because it is not in the array.

## 🟡 Real Example Hindi mein
**Zomato search:** आप search box में "biryani" लिखते हैं। Results वाला effect `[query, city]` पर depend करता है। Typing से `query` बदलता है और effect fetch करता है। City Delhi से Pune करने पर `city` बदलती है और फिर fetch होता है। Cart drawer खुला है या नहीं जैसी असंबंधित state बदलने पर कुछ fetch नहीं होता, क्योंकि वह array में नहीं है।

---

## 💻 Code Example — Basic

```jsx
// Three forms of the dependency array in one component
import { useState, useEffect } from 'react';          // hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function Demo() {
  const [count, setCount] = useState(0);              // state we will watch
  const [name, setName] = useState('Aditya');         // unrelated state

  useEffect(() => {
    console.log('A: runs after EVERY render');        // no array
  });

  useEffect(() => {
    console.log('B: runs ONCE after mount');          // empty array
  }, []);

  useEffect(() => {
    console.log('C: runs when count changes, count =', count); // watches count only
    document.title = `Clicks: ${count}`;              // sync the browser tab title
  }, [count]);                                        // typing in name does NOT trigger C

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Clicked {count}</button> {/* triggers A and C */}
      <input value={name} onChange={e => setName(e.target.value)} />        {/* triggers only A */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Demo />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Production search: debounce + abort + correct deps (no stale data, no race condition)
import { useState, useEffect } from 'react';          // hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function RestaurantSearch() {
  const [query, setQuery] = useState('');             // what the user typed
  const [city, setCity] = useState('Delhi');          // selected city
  const [results, setResults] = useState([]);         // list to render
  const [loading, setLoading] = useState(false);      // loading flag
  const [error, setError] = useState(null);           // error message

  useEffect(() => {
    if (query.trim().length < 2) {                    // too short: nothing to search
      setResults([]);                                 // clear old results
      return;                                         // no cleanup needed for this path
    }

    const controller = new AbortController();         // lets us cancel the request
    const timer = setTimeout(async () => {            // debounce: wait 300ms after last keystroke
      try {
        setLoading(true);                             // show spinner
        setError(null);                               // clear old error
        const url = `/api/restaurants?q=${encodeURIComponent(query)}&city=${city}`;
        const res = await fetch(url, { signal: controller.signal }); // cancellable fetch
        if (!res.ok) throw new Error('Request failed');              // fetch does not throw on 404/500
        setResults(await res.json());                 // store results
      } catch (e) {
        if (e.name !== 'AbortError') setError(e.message); // ignore our own cancellations
      } finally {
        if (!controller.signal.aborted) setLoading(false); // do not touch state of a cancelled run
      }
    }, 300);

    return () => {                                    // cleanup: runs before next effect and on unmount
      clearTimeout(timer);                            // cancel pending debounce
      controller.abort();                             // cancel in-flight request
    };
  }, [query, city]);                                  // everything the effect reads: complete list

  return (
    <div>
      <select value={city} onChange={e => setCity(e.target.value)}>
        <option>Delhi</option><option>Pune</option>
      </select>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search" />
      {loading && <p>Loading...</p>}
      {error && <p role="alert">{error}</p>}
      <ul>{results.map(r => <li key={r.id}>{r.name}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantSearch />);
```

---

## 🟠 Next.js Connection

In the App Router, a Client Component's effects behave exactly as in React. But often you can **remove the effect** and put the "dependency" in the URL: `searchParams` drive a Server Component, and Next.js re-renders it when the URL changes. This removes loading flags and race conditions.

```jsx
// app/search/page.jsx (Server Component: no useEffect needed, URL is the dependency)
import { searchRestaurants } from '@/lib/restaurants';   // your data layer (hypothetical helper)

export default async function Page({ searchParams }) {
  const { q = '', city = 'Delhi' } = await searchParams; // Next.js 15+: searchParams is a Promise
  const results = q ? await searchRestaurants(q, city) : []; // runs on the server per URL
  return <ul>{results.map(r => <li key={r.id}>{r.name}</li>)}</ul>;
}
```

```jsx
// app/search/SearchBox.jsx (Client Component: only updates the URL)
'use client';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function SearchBox() {
  const router = useRouter();                            // navigation API
  const params = useSearchParams();                      // current query string
  const [q, setQ] = useState(params.get('q') ?? '');     // local input state

  useEffect(() => {
    const t = setTimeout(() => router.replace(`/search?q=${encodeURIComponent(q)}`), 300); // debounce
    return () => clearTimeout(t);                        // cleanup on every change
  }, [q, router]);                                       // router is stable but still listed

  return <input value={q} onChange={e => setQ(e.target.value)} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Object/array/function created in render put in the deps (new identity every render, effect runs every time)
✅ **Correct:** Use primitives, move the object inside the effect, or memoize it

```jsx
// Wrong: filters is a new object each render → Object.is fails → effect runs after every render
const filters = { city, veg };
useEffect(() => { load(filters); }, [filters]);        // ❌

// Right: depend on the primitives, build the object inside
useEffect(() => { load({ city, veg }); }, [city, veg]); // ✅
```

❌ **Mistake 2:** Lying to the linter with an empty array
✅ **Correct:** Fix the cause (move code inside, use functional update, or `useRef`) instead of disabling the rule

```jsx
// Wrong: stale count, always logs 0
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000); // ❌ count frozen at 0
  return () => clearInterval(id);
}, []);

// Right: functional update does not read count, so [] is honest
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000); // ✅
  return () => clearInterval(id);
}, []);
```

❌ **Mistake 3:** Setting state that is also in the deps, unconditionally
✅ **Correct:** Add a condition, or compute the value during render instead

```jsx
// Wrong: infinite loop (count changes → effect → count changes ...)
useEffect(() => { setCount(count + 1); }, [count]);    // ❌

// Right: derived value needs no effect at all
const double = count * 2;                              // ✅ calculate in render
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';

function App() {
  const [user, setUser] = useState({ name: 'A' });     // state is an object

  useEffect(() => {
    console.log('effect ran');
  }, [user]);                                          // depends on the object

  return (
    <button onClick={() => setUser({ name: 'A' })}>    // same content, NEW object
      Click
    </button>
  );
}
```
**Answer:** "effect ran" prints once on mount, and **prints again on every click**, even though `{ name: 'A' }` looks identical. React compares with `Object.is`, which checks reference identity for objects. Each click creates a new object, so the dependency changed. If the code were `setUser(user)` (same reference), the component would bail out of re-render and the effect would not run. Fix: depend on `user.name` (a primitive) instead.

---

## ⚫ Interview Questions + Answers

Q1: What does the dependency array do?
A1: It tells React which reactive values the effect uses. After each render React compares them to the previous ones with `Object.is`, and runs the effect (after the cleanup of the previous one) only if something changed.

Q2: What is the difference between no array, `[]`, and `[a]`?
A2: No array: after every render. `[]`: once after mount (and cleanup once on unmount). `[a]`: after mount and whenever `a` changes.

Q3: Why is an object or function in the deps risky?
A3: They get a new identity on every render, so `Object.is` says "changed" each time and the effect re-runs. Use primitives, move them inside the effect, or stabilize with `useMemo`/`useCallback`.

Q4: Should I ever disable `react-hooks/exhaustive-deps`?
A4: Almost never. The rule reflects real stale-closure bugs. Prefer restructuring: functional state updates, moving a function inside the effect, `useRef` for latest values, or the newer `useEffectEvent` (React 19.2, check your version).

Q5: Does the effect run on the first render if the deps are `[x]`?
A5: Yes. Every effect runs after the first mount regardless of its array. Dependencies only control later re-runs. In React 18+ development StrictMode, effects also run twice on mount to surface missing cleanups.

---

## 🔷 When to Use + When Not to Use
✅ **Use a dependency array when:**
- The effect syncs with an external system (API, timer, subscription, DOM API) using props or state
- You want to skip work when nothing relevant changed
- You list exactly what the effect reads, and let the linter verify it

❌ **Avoid relying on effects when:**
- The value can be computed during render (derived state)
- The work is a response to a click (put it in the event handler)
- You are tempted to leave out a dependency to "make it stop running" (fix the design instead)

---

## 📊 Visual Diagram

```
 Render #1 (query="a")      Render #2 (query="ab")     Render #3 (query="ab", other state)
 deps = ["a"]               deps = ["ab"]              deps = ["ab"]
      │                          │                          │
      ▼                          ▼                          ▼
 previous: none            "a" vs "ab" → different    "ab" vs "ab" → same
 → RUN effect              → cleanup(old) → RUN       → SKIP (no cleanup, no run)

 Compare is Object.is, item by item:
   Object.is("ab","ab")      → true  (primitive, same value)
   Object.is({a:1},{a:1})    → false (objects, different references)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency array | List of values the effect depends on | Effect जिन values पर निर्भर है उनकी सूची |
| Reactive value | Prop, state or anything derived from them | Prop, state या उनसे बनी value |
| Object.is | Equality check React uses | React की equality जाँच |
| Stale closure | Effect remembering old values | Effect का पुरानी values याद रखना |
| exhaustive-deps | ESLint rule checking the array | Array जाँचने वाला ESLint rule |
| Derived state | Value calculated from other state | दूसरी state से निकाली गई value |
| Functional update | `setX(prev => ...)` form | `setX(prev => ...)` रूप |

---

## ⚡ 3-Line Summary
**English:**
1. The dependency array decides when an effect re-runs: never (`[]`), always (none), or when listed values change.
2. Values are compared with `Object.is`, so new objects, arrays and functions each render cause re-runs.
3. List everything the effect reads, and fix the design instead of silencing the linter.

**Hindi:**
1. Dependency array तय करता है कि effect कब दोबारा चले: कभी नहीं (`[]`), हमेशा (array नहीं), या listed values बदलने पर।
2. तुलना `Object.is` से होती है, इसलिए हर render में बनने वाले नए objects, arrays और functions effect को दोबारा चलाते हैं।
3. Effect जो कुछ पढ़ता है वह सब list करो, और linter चुप कराने की जगह design ठीक करो।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — useEffect](https://react.dev/reference/react/useEffect) | Official reference on dependencies |
| 📝 Article | [react.dev — Removing Effect Dependencies](https://react.dev/learn/removing-effect-dependencies) | How to fix dependency problems |

---

## ➡️ Next Topic
**38. useEffect Cleanup Function** — effect के बाद सफ़ाई कैसे करें: timers, subscriptions और requests को रोकना, ताकि memory leaks और race conditions न हों। Dependency array के साथ cleanup का क्रम समझना ज़रूरी है।
