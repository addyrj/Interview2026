# 36. useEffect — Complete Guide
# हिंदी में: useEffect — Side Effects Handle करना, पूरी Guide

---

## 🔵 Simple Definition (English)
`useEffect` is a React Hook for running **side effects** — code that happens outside the normal render cycle: fetching data, subscriptions, timers, manually updating the DOM. It runs **after** the component renders.

## 🔵 सरल परिभाषा (Hindi)
`useEffect` React Hook है जो **side effects** run करने के लिए है — वो code जो normal render cycle के बाहर होता है: data fetching, subscriptions, timers, manually DOM update। यह component render होने के **बाद** run होता है।

---

## 🔴 Problem it Solves
Side effects in render function cause infinite loops and inconsistency:
```jsx
function App() {
  fetch('/api/data').then(...); // runs on EVERY render — infinite loop!
  // Can't do this in render — need useEffect
}
```

## 🔴 यह क्यों बना? (Hindi)
Render function में side effects infinite loops और inconsistency cause करते हैं। उन्हें बाहर निकालने के लिए useEffect बना — controlled side effects management।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component renders (JSX returned)
Step 2 → React updates Real DOM
Step 3 → Browser paints
Step 4 → useEffect runs (AFTER paint!)
         - Runs callback
         - Compares dependencies with previous render
         - Only runs if deps changed (or no deps array = runs every time)

Step 5 → On next render: cleanup runs first, then effect runs again

Step 6 → On unmount: cleanup runs one final time
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component render होता है
Step 2 → React Real DOM update करता है
Step 3 → Browser paint करता है
Step 4 → useEffect run होता है (paint के बाद!)
         - Callback run करता है
         - Dependencies compare करता है
         - Deps बदले हों तभी run होता है

Step 5 → अगले render पर: cleanup पहले, फिर effect
Step 6 → Unmount पर: cleanup एक आखिरी बार
```

---

## 🟡 Real World Example
**Zomato Search:** When you type in search box, after 500ms delay (debounce), restaurants load. `useEffect` watches the search query — when it changes, it cancels the previous timer and sets a new one to fetch results.

## 🟡 Real Example Hindi मे
**Zomato Search:** जब आप search box में type करते हो, 500ms delay के बाद restaurants load होते हैं। `useEffect` search query watch करता है — जब बदलती है, पुराना timer cancel करके नया set करता है।

---

## 💻 Code Example — Basic

```jsx
import { useState, useEffect } from 'react';

// ── THREE FORMS OF useEffect ──────────────

function EffectForms() {
  const [count, setCount] = useState(0);
  const [userId, setUserId] = useState(1);

  // FORM 1: No dependency array → runs after EVERY render
  useEffect(() => {
    console.log('Runs after every render'); // risky — often causes loops
  }); // no []

  // FORM 2: Empty array [] → runs ONCE after mount only
  useEffect(() => {
    console.log('Runs once on mount');
    // Good for: initial data fetch, subscriptions, timers
    document.title = 'My App'; // one-time setup
  }, []); // empty deps

  // FORM 3: Deps array → runs when deps change
  useEffect(() => {
    console.log(`userId changed to ${userId}`);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => console.log(data));
  }, [userId]); // only when userId changes

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
      <button onClick={() => setUserId(id => id + 1)}>Next User</button>
    </div>
  );
}

// ── DATA FETCHING WITH useEffect ──────────
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset state when userId changes
    setLoading(true);
    setError(null);
    setUser(null);

    fetch(`/api/users/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [userId]); // re-fetch when userId changes

  if (loading) return <div>Loading user {userId}...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>Hello, {user?.name}!</div>;
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useEffect, useRef } from 'react';

// ── CLEANUP FUNCTION ─────────────────────
// Return a function from useEffect for cleanup
function SearchWithDebounce({ query }) {
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!query) { setResults([]); return; }

    // Set timer
    const timerId = setTimeout(() => {
      fetch(`/api/search?q=${query}`)
        .then(r => r.json())
        .then(setResults);
    }, 300);

    // CLEANUP: cancel timer when:
    // 1. query changes (new search)
    // 2. component unmounts
    return () => clearTimeout(timerId); // cleanup function!

  }, [query]); // runs when query changes

  return <ul>{results.map(r => <li key={r.id}>{r.name}</li>)}</ul>;
}

// ── SUBSCRIPTION PATTERN ──────────────────
function OnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline  = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Subscribe
    window.addEventListener('online',  handleOnline);
    window.addEventListener('offline', handleOffline);

    // CLEANUP: unsubscribe on unmount
    return () => {
      window.removeEventListener('online',  handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); // subscribe once

  return <span>{isOnline ? '🟢 Online' : '🔴 Offline'}</span>;
}

// ── ABORT CONTROLLER — RACE CONDITION FIX ─
function ProductDetails({ productId }) {
  const [product, setProduct] = useState(null);

  useEffect(() => {
    const controller = new AbortController(); // for cancellation

    fetch(`/api/products/${productId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => setProduct(data))
      .catch(err => {
        if (err.name !== 'AbortError') console.error(err);
        // AbortError is expected — ignore it
      });

    // CLEANUP: abort fetch if productId changes before fetch completes
    return () => controller.abort();
    // Without this: old fetch might resolve AFTER new one → stale data!

  }, [productId]);

  return <div>{product?.name || 'Loading...'}</div>;
}

// ── EFFECT WITH MULTIPLE CONCERNS ────────
function Dashboard({ userId }) {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);

  // Effect 1: fetch user
  useEffect(() => {
    fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser);
  }, [userId]);

  // Effect 2: fetch user's posts (separate concern — separate effect)
  useEffect(() => {
    fetch(`/api/users/${userId}/posts`).then(r => r.json()).then(setPosts);
  }, [userId]);

  // Effect 3: update page title
  useEffect(() => {
    if (user) document.title = `${user.name}'s Dashboard`;
    return () => { document.title = 'App'; }; // cleanup on unmount
  }, [user]);

  // Effects are independent — cleaner than one big effect!

  return <div>{user?.name} — {posts.length} posts</div>;
}
```

---

## 🟠 Next.js Connection

```jsx
// React: useEffect for client-side data fetching
// Next.js: Server Components fetch on server (no useEffect needed!)

// ── OLD React pattern (CSR): ──────────────
'use client';
function ProductListOld({ categoryId }) {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch(`/api/products?category=${categoryId}`)
      .then(r => r.json())
      .then(setProducts);
  }, [categoryId]);

  return <div>{products.map(p => <div key={p.id}>{p.name}</div>)}</div>;
}

// ── NEXT.JS pattern (SSR/SSG): ───────────
// app/products/page.jsx — Server Component (no 'use client')
async function ProductList({ searchParams }) {
  // Fetch on SERVER — no useEffect, no useState, no loading state!
  const products = await fetch(
    `/api/products?category=${searchParams.category}`,
    { cache: 'force-cache' }  // Next.js caching
  ).then(r => r.json());

  return <div>{products.map(p => <div key={p.id}>{p.name}</div>)}</div>;
}

// ── useEffect still useful in Next.js Client Components: ──
'use client';
function ScrollTracker() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handler = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return <div>Scroll: {scrollY}px</div>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Missing dependencies (stale closure)
```jsx
// WRONG: 'userId' used inside but not in deps
function BadEffect({ userId }) {
  useEffect(() => {
    fetch(`/api/${userId}`); // uses userId but deps is empty!
    // When userId changes, effect still uses OLD userId (stale closure)
  }, []); // ❌ should include userId
}

// CORRECT:
useEffect(() => {
  fetch(`/api/${userId}`);
}, [userId]); // ✅ re-runs when userId changes
```

❌ **Mistake 2:** Infinite loop with object/array deps
```jsx
// WRONG: new object created on every render → infinite loop!
function BadDeps() {
  const options = { page: 1 }; // NEW object every render

  useEffect(() => {
    fetchData(options);
  }, [options]); // ❌ options always "changed" (new reference)
}

// CORRECT: primitive deps or useMemo
useEffect(() => {
  fetchData({ page: 1 });
}, []); // if options don't change
// OR: destructure to primitives
useEffect(() => {
  fetchData({ page });
}, [page]); // ✅ primitive
```

❌ **Mistake 3:** Async function directly in useEffect
```jsx
// WRONG: useEffect callback can't be async
useEffect(async () => { // ❌ — returns Promise, cleanup ignored!
  const data = await fetch('/api/data');
}, []);

// CORRECT: define async inside, call it
useEffect(() => {
  async function loadData() {
    const data = await fetch('/api/data').then(r => r.json());
    setData(data);
  }
  loadData(); // ✅ call the async function
}, []);
```

---

## 🧠 Tricky Interview Question

```jsx
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1); // What happens here?
    }, 1000);

    return () => clearInterval(interval);
  }, []); // empty deps

  return <div>{count}</div>;
}
// What does this component show after 5 seconds?
```
**Answer:** Shows `1` forever (not 5). The effect runs once (empty deps), capturing `count = 0` in its closure. Every second: `setCount(0 + 1)` = always 1. **Fix:** Use functional update: `setCount(c => c + 1)` — doesn't need `count` in closure, always gets latest.

---

## ⚫ Interview Questions + Answers

**Q1: What are side effects in React?**
A1: Side effects are operations that interact with the outside world or have effects beyond returning JSX: API calls, subscriptions, timers, DOM manipulation, localStorage, logging. These can't go in the render function (would run on every render). `useEffect` is React's way to safely run side effects after render.

**Q2: Explain the three forms of useEffect dependencies.**
A2: (1) No deps array: runs after EVERY render — dangerous, usually causes infinite loops. (2) Empty array `[]`: runs ONCE after mount — for initial data fetch, subscriptions. (3) `[dep1, dep2]`: runs when any dep changes — for conditional effects. React compares deps with `Object.is()` — objects/arrays always "change" unless you use primitives or `useMemo`.

**Q3: What is the cleanup function and when does it run?**
A3: The function returned from `useEffect` is the cleanup function. It runs: (1) Before the effect runs again on next render (when deps change). (2) When the component unmounts. Use it for: clearing timers (`clearInterval/clearTimeout`), removing event listeners (`removeEventListener`), aborting fetch calls (`controller.abort()`), closing subscriptions/WebSockets. Without cleanup → memory leaks and bugs.

**Q4: How do you avoid race conditions in useEffect data fetching?**
A4: Use `AbortController`: create one in effect, pass its `signal` to `fetch`, abort it in cleanup. When the dep changes quickly, the old fetch gets aborted before it can `setState` with stale data. Another pattern: `ignore` flag — `let ignore = false; fetch().then(d => { if (!ignore) setData(d); }); return () => { ignore = true; }`.

**Q5: What is the difference between useEffect and useLayoutEffect?**
A5: `useEffect` runs **after** the browser paints — non-blocking, good for data fetching, subscriptions. `useLayoutEffect` runs **before** the browser paints — synchronous, blocks paint. Use `useLayoutEffect` only when you need to read/modify DOM before paint (measuring elements, preventing flicker). In SSR (Next.js), `useLayoutEffect` throws a warning — use `useEffect` unless you specifically need pre-paint execution.

---

## 🔷 When to Use + When Not to Use
✅ **Use useEffect when:**
- Fetching data (React way, not Next.js server components)
- Setting up subscriptions (events, WebSocket, SSE)
- Timers (setInterval, setTimeout)
- Updating document.title, localStorage
- Third-party library initialization

❌ **Avoid useEffect when:**
- Computing derived state → compute directly
- Updating state in response to event → handle in event handler
- In Next.js Server Component → use async/await directly
- Something that should happen during render → consider other hooks

---

## 📊 Visual Diagram

```
useEffect EXECUTION ORDER:
────────────────────────────────────────────
  Render (JSX evaluated)
       │
       ▼
  DOM updated
       │
       ▼
  Browser paints (user sees UI)
       │
       ▼
  useEffect runs ← (async, after paint)
       │
  [if deps changed on next render:]
       │
       ├──► Cleanup runs (previous effect's cleanup)
       │
       └──► Effect runs again

DEPENDENCY MATRIX:
────────────────────────────────────────────
  useEffect(fn)       → every render ⚠️
  useEffect(fn, [])   → once on mount ✅
  useEffect(fn, [x])  → when x changes ✅
  useEffect(fn, [x,y])→ when x OR y changes ✅

CLEANUP TIMING:
────────────────────────────────────────────
  Mount     → Effect runs
  Update    → Cleanup (old) → Effect (new)
  Unmount   → Cleanup (final)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Side effect | Code outside render cycle | Render cycle के बाहर का code |
| Dependency array | Values that trigger effect | Effect को trigger करने वाली values |
| Cleanup function | Runs before next effect/unmount | अगले effect/unmount से पहले run |
| Stale closure | Old captured variable value | पुरानी captured variable value |
| Race condition | Multiple async ops in wrong order | गलत order में async operations |
| AbortController | Cancel in-flight fetch | चल रहे fetch को cancel करना |
| Subscription | Listening to external events | External events सुनना |

---

## ⚡ 3-Line Summary
**English:**
1. `useEffect(fn, deps)` runs after render — `[]` = once on mount, `[dep]` = when dep changes, no array = every render.
2. Always return cleanup function for subscriptions/timers — runs before next effect and on unmount.
3. Never make effect callback async — define async function inside and call it.

**Hindi:**
1. `useEffect(fn, deps)` render के बाद run — `[]` = एक बार mount पर, `[dep]` = dep change पर, no array = हर render।
2. Subscriptions/timers के लिए cleanup function हमेशा return करो — अगले effect और unmount से पहले run होती है।
3. Effect callback को कभी async मत बनाओ — अंदर async function define करो और call करो।

---

## ➡️ Next Topic
**37. useEffect Dependency Array** — Dependencies को deep dive करना — stale closures, object deps, और ESLint rules।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — useEffect](https://www.youtube.com/results?search_query=useeffect+hook+react+akshay+saini+namaste) | Complete useEffect in Hindi |
| 📺 YouTube | [Web Dev Simplified — useEffect](https://www.youtube.com/results?search_query=useeffect+hook+complete+guide+web+dev+simplified) | All patterns with examples |
| 📝 Article | [react.dev — useEffect](https://react.dev/reference/react/useEffect) | Official complete reference |
| 📝 Article | [react.dev — You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) | When NOT to use useEffect |
