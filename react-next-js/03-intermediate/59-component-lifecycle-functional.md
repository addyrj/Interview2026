# 59. Component Lifecycle (Functional)
# हिंदी में: Functional Component Lifecycle — useEffect से Mount, Update और Unmount

---

## 🔵 Simple Definition (English)
In function components, **`useEffect`** replaces `componentDidMount`, `componentDidUpdate` and `componentWillUnmount`. You describe a side effect once, and React runs it **after the render is painted**. If the effect returns a **cleanup function**, React runs that cleanup before the next effect and when the component is removed.

## 🔵 सरल परिभाषा (Hindi)
Function components में **`useEffect`** `componentDidMount`, `componentDidUpdate` और `componentWillUnmount` की जगह लेता है। Side effect एक बार लिखते हो, और React उसे **render के screen पर paint होने के बाद** चलाता है। Effect अगर **cleanup function** लौटाए, तो React अगला effect चलाने से पहले और component हटते समय उसे चलाता है।

---

## 🔴 Problem it Solves

Class components split related logic across methods. A subscription is started in `componentDidMount`, updated in `componentDidUpdate` (when the id changes), and stopped in `componentWillUnmount`. These three pieces are about one thing, yet they live in three places. Functional components with hooks let you keep the setup and the teardown of one effect together, and React re-runs the effect whenever its inputs change.

```jsx
// PROBLEM (class world): setup and teardown are in different methods
// componentDidMount()    { this.sub = subscribe(this.props.id); }
// componentDidUpdate(p)  { if (p.id !== this.props.id) { this.sub.unsub(); this.sub = subscribe(this.props.id); } }
// componentWillUnmount() { this.sub.unsub(); }
// Easy to forget one of the three → memory leak or stale subscription
```

## 🔴 यह क्यों बना? (Hindi)
Class components में related logic तीन methods में बँट जाता है। Subscription `componentDidMount` में शुरू होती है, `componentDidUpdate` में (जब id बदले) बदलती है, और `componentWillUnmount` में बंद होती है। ये तीनों एक ही काम के हिस्से हैं, फिर भी तीन जगह लिखे हैं। Hooks वाले function components में setup और teardown एक ही जगह रहते हैं, और जब inputs बदलें तो React effect दोबारा चलाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component renders (function runs, returns JSX)
Step 2 → DOM is updated and the browser paints the screen
Step 3 → React runs the effect function  → "mount" (or "update" if deps changed)
Step 4 → Effect returns a cleanup function → React stores it
Step 5 → Deps change (or component unmounts) → React runs the STORED cleanup first
Step 6 → Then React runs the NEW effect (if it is an update, not unmount)

Dependency array:
  useEffect(fn)        → runs after EVERY render
  useEffect(fn, [])    → runs ONCE after mount (cleanup on unmount)
  useEffect(fn, [a,b]) → runs after mount and whenever a or b changes (Object.is)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component render होता है (function चलता है, JSX लौटता है)
Step 2 → DOM update होता है और browser screen paint करता है
Step 3 → React effect function चलाता है → "mount" (या deps बदले तो "update")
Step 4 → Effect cleanup function लौटाता है → React उसे store करता है
Step 5 → Deps बदलें (या unmount हो) → React पहले STORED cleanup चलाता है
Step 6 → फिर नया effect चलता है (unmount न हो तो)

Dependency array:
  useEffect(fn)        → हर render के बाद चलता है
  useEffect(fn, [])    → mount के बाद एक बार (unmount पर cleanup)
  useEffect(fn, [a,b]) → mount के बाद, और a या b बदलने पर (Object.is से compare)
```

---

## 🟡 Real World Example
**Zomato live restaurant status:** The restaurant card subscribes to a live "open / busy" feed for `restaurantId`. When the user scrolls and the card now shows a different restaurant, the `restaurantId` prop changes. The effect's cleanup closes the old connection, and the new effect opens one for the new restaurant. When the card leaves the screen, the cleanup runs once more. The developer writes one effect with one cleanup, and React handles the timing.

## 🟡 Real Example Hindi mein
**Zomato live restaurant status:** Restaurant card `restaurantId` के लिए live "open / busy" feed से जुड़ता है। User scroll करे और card दूसरा restaurant दिखाए, तो `restaurantId` prop बदलता है। Effect का cleanup पुराना connection बंद करता है, और नया effect नए restaurant के लिए connection खोलता है। Card स्क्रीन से हटे तो cleanup एक बार और चलता है। Developer एक effect और एक cleanup लिखता है, timing React संभालता है।

---

## 💻 Code Example — Basic

```jsx
// useEffect basics: mount, prop change (cleanup + new effect), and unmount
import { useState, useEffect } from 'react';     // hooks for state and side effects
import { createRoot } from 'react-dom/client';   // React 18/19 root API

function OrderStatus({ orderId }) {              // function component with a prop
  const [status, setStatus] = useState('placed'); // local state: starts as "placed"

  useEffect(() => {                              // effect runs AFTER the browser paints
    console.log('effect: subscribe to order', orderId); // setup side effect
    const timer = setTimeout(() => setStatus('preparing'), 300); // simulate a status update

    return () => {                               // cleanup: runs before next effect and on unmount
      console.log('cleanup: unsubscribe', orderId); // teardown for THIS orderId
      clearTimeout(timer);                       // stop the timer so it cannot fire later
    };
  }, [orderId]);                                 // re-run only when orderId changes

  return <p>Order {orderId}: {status}</p>;       // what the user sees
}

const root = createRoot(document.getElementById('root')); // find the page's root element
root.render(<OrderStatus orderId="ZOM-1" />);             // mount with ZOM-1
setTimeout(() => root.render(<OrderStatus orderId="ZOM-2" />), 100); // change prop → cleanup + new effect
setTimeout(() => root.unmount(), 600);                    // unmount → final cleanup runs
// Expected log:
// effect: subscribe to order ZOM-1
// cleanup: unsubscribe ZOM-1
// effect: subscribe to order ZOM-2
// cleanup: unsubscribe ZOM-2
```

## 💻 Code Example — Advanced

```jsx
// Production-style: custom hook, AbortController for stale requests, useLayoutEffect
import { useState, useEffect, useLayoutEffect, useRef } from 'react'; // hooks used below
import { createRoot } from 'react-dom/client';                        // React 18/19 root API

// Fake API that behaves like fetch(): returns a Promise and respects an AbortSignal.
// In a real app this would be fetch('/api/restaurants?q=...', { signal }).
function fakeFetchRestaurants(query, { signal }) {
  return new Promise((resolve, reject) => {
    const names = ['Biryani House', 'Dosa Corner', 'Pizza Hub']; // pretend database
    const delay = query.length * 50;             // longer queries take longer (simulated network)
    const timer = setTimeout(() => {             // resolve after the simulated delay
      resolve(names.filter(n => n.toLowerCase().includes(query.toLowerCase()))); // filtered list
    }, delay);
    signal.addEventListener('abort', () => {     // called when controller.abort() is invoked
      clearTimeout(timer);                       // stop the pending "response"
      reject(new DOMException('Aborted', 'AbortError')); // reject like a real aborted fetch
    });
  });
}

// Custom hook: owns the request lifecycle, so components stay simple
function useRestaurantSearch(query) {
  const [state, setState] = useState({ status: 'idle', data: [], error: null }); // one object

  useEffect(() => {                              // runs after mount and whenever query changes
    if (!query) {                                // empty query → nothing to fetch
      setState({ status: 'idle', data: [], error: null }); // reset to idle
      return;                                    // no cleanup needed for this branch
    }
    const controller = new AbortController();    // one controller per request
    setState(s => ({ ...s, status: 'loading' })); // show loading, keep old data

    fakeFetchRestaurants(query, { signal: controller.signal })
      .then(data => setState({ status: 'success', data, error: null })) // success path
      .catch(err => {                            // errors: ignore aborts, report real failures
        if (err.name !== 'AbortError') {         // an abort is expected when query changes
          setState({ status: 'error', data: [], error: err.message });
        }
      });

    return () => controller.abort();             // cleanup: cancel the STALE request
  }, [query]);                                   // effect depends on query only

  return state;                                  // { status, data, error } for the component
}

// Layout effect: runs synchronously after DOM changes, BEFORE the browser paints
function ResultCount({ count }) {
  const ref = useRef(null);                      // ref to the <p> DOM node
  useLayoutEffect(() => {                        // good for measuring layout or avoiding flicker
    console.log('layout effect sees', ref.current.tagName, 'count =', count); // DOM is ready
  }, [count]);                                   // re-run when count changes
  return <p ref={ref}>{count} results</p>;       // attach ref to the paragraph
}

function App({ query }) {                        // parent passes the search text
  const { status, data, error } = useRestaurantSearch(query); // hook does the work
  console.log('App render, status =', status);  // logs on every render
  return (
    <div>
      <ResultCount count={data.length} />        {/* shows number of results */}
      {status === 'error' && <p>Error: {error}</p>}
      <ul>{data.map(name => <li key={name}>{name}</li>)}</ul>
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App query="bi" />);                 // first search: 100 ms delay
setTimeout(() => root.render(<App query="biryani" />), 50); // new query aborts the "bi" request
```

---

## 🟠 Real App Integration

In Next.js App Router, effects belong in **Client Components**. The Server Component renders the page, and the client component subscribes after hydration. This example is a Swiggy-style search box that cancels the previous request when the query changes.

```jsx
// app/search/SearchResults.jsx
'use client';                                           // useEffect runs only in Client Components
import { useEffect, useState } from 'react';            // hooks used by this component

export default function SearchResults({ initialQuery }) { // initialQuery is passed from a Server Component
  const [query, setQuery] = useState(initialQuery);     // current search text
  const [items, setItems] = useState([]);               // results from the Route Handler

  useEffect(() => {                                     // runs after mount and when query changes
    const controller = new AbortController();           // one controller per request
    fetch(`/api/restaurants?q=${encodeURIComponent(query)}`, { signal: controller.signal }) // Route Handler
      .then(res => res.json())                          // parse the JSON response
      .then(setItems)                                   // store the results
      .catch(err => {                                   // handle failures
        if (err.name !== 'AbortError') console.error(err); // ignore cancelled requests
      });
    return () => controller.abort();                    // cleanup: cancel the stale request
  }, [query]);                                          // effect depends on query

  return (
    <>
      <input value={query} onChange={e => setQuery(e.target.value)} /> {/* controlled input */}
      <ul>{items.map(r => <li key={r.id}>{r.name}</li>)}</ul>          {/* result list */}
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting a dependency, so the effect uses an old value (stale closure)
✅ **Correct:** Put every value the effect reads into the dependency array

```jsx
// Wrong: effect reads userId but only runs once → always fetches the first user
useEffect(() => {
  fetch(`/api/users/${userId}`).then(/* ... */);  // ❌ userId is stale after the first render
}, []);

// Right: include userId, so the effect re-runs when it changes
useEffect(() => {
  const controller = new AbortController();      // ✅ cancel if userId changes again
  fetch(`/api/users/${userId}`, { signal: controller.signal }).then(/* ... */);
  return () => controller.abort();
}, [userId]);                                    // ✅ dependency declared
```

❌ **Mistake 2:** Setting state without deps, which loops forever
✅ **Correct:** Add a dependency array so the effect runs only when needed

```jsx
// Wrong: runs after EVERY render, sets state, causes another render → infinite loop
useEffect(() => {
  setTotal(items.reduce((a, b) => a + b.price, 0)); // ❌ no deps array
});

// Right: compute during render (no effect needed) — or add deps
const total = items.reduce((a, b) => a + b.price, 0); // ✅ derived value, no state at all
```

❌ **Mistake 3:** Making the effect callback `async`
✅ **Correct:** Define an async function inside the effect and call it

```jsx
// Wrong: async effect returns a Promise, React expects a cleanup function or nothing
useEffect(async () => {                          // ❌ React warns: effect must not return a Promise
  const res = await fetch('/api/menu');
}, []);

// Right: define the async function inside and call it
useEffect(() => {
  async function load() {                        // ✅ async is inside
    const res = await fetch('/api/menu');
  }
  load();                                        // ✅ start it, return nothing (or a cleanup)
}, []);
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function Demo() {
  const [count, setCount] = useState(0);         // count is 0 in the first render
  console.log('render', count);                  // logs once per render

  useEffect(() => {                              // empty deps: effect is created ONCE, in the first render
    const id = setTimeout(() => {
      setCount(count + 1);                       // "count" is the stale 0 captured by this closure
      setCount(count + 1);                       // same stale 0 → both calls set 1
      console.log('timeout sees count =', count); // still 0, because this closure never changes
    }, 0);
    return () => clearTimeout(id);               // cleanup for the timer
  }, []);                                        // empty deps = never re-created

  return <p>{count}</p>;
}

createRoot(document.getElementById('root')).render(<Demo />);
```
**Answer:** The output is:
```
render 0
timeout sees count = 0
render 1
```
The effect was created during the first render, so its callback closes over `count = 0` and never sees later values. Both `setCount(count + 1)` calls therefore set `1`. React batches them into one re-render, so the component shows `1` once. The `console.log` in the timeout runs before that re-render happens, so it still prints `0`. The fix is the functional update `setCount(c => c + 1)`, or adding `count` to the dependency array.

---

## ⚫ Interview Questions + Answers

Q1: How do you replace `componentDidMount`, `componentDidUpdate` and `componentWillUnmount` with hooks?
A1: Use `useEffect`. An effect with `[]` behaves like `componentDidMount` plus `componentWillUnmount` (through its cleanup). An effect with dependencies also runs on updates when those values change, which covers `componentDidUpdate`. The returned cleanup function handles teardown.

Q2: What is the difference between `useEffect` and `useLayoutEffect`?
A2: `useEffect` runs after the browser paints, so it does not block the screen. `useLayoutEffect` runs synchronously after the DOM changes and before paint, so it is right for measuring the layout or fixing position without a visible flicker. Use `useEffect` by default.

Q3: Why do we need cleanup functions?
A3: Without them, subscriptions, timers and requests keep running after the component changed or was removed. The cleanup runs before the next effect and on unmount, so each effect only leaves behind what it created.

Q4: Can an effect be `async`?
A4: No, the callback itself must not return a Promise, because React expects either nothing or a cleanup function. Define an `async` function inside the effect and call it.

Q5: Does `useEffect` run on the server?
A5: No. Effects run only in the browser after commit. Server rendering (SSR) renders the initial HTML but does not run effects, so browser-only APIs such as `window` or `localStorage` are safe to use inside effects, not during render.

---

## 🔷 When to Use + When Not to Use
✅ **Use useEffect when:**
- You must sync with something outside React (timers, sockets, DOM APIs, network requests)
- You need cleanup for subscriptions or requests
- You want related setup and teardown kept in one place

❌ **Avoid useEffect when:**
- You are only computing a value from props or state (compute it during render)
- You are reacting to a user click (put the logic in the event handler)
- You are copying a prop into state (use the prop directly, or a `key` to reset)

---

## 📊 Visual Diagram

```
Render 1 (orderId = ZOM-1)          Render 2 (orderId = ZOM-2)           Unmount
───────────────────────────         ──────────────────────────          ─────────
 render → paint                      render → paint                      
 effect(ZOM-1) runs ──┐              cleanup(ZOM-1) runs  ← first        cleanup(ZOM-2) runs
                      │ stored       effect(ZOM-2) runs  ← then
                      └──────────────►
Timeline:
 time ──────────────────────────────────────────────────────────────────────►
   [render ZOM-1] [effect ZOM-1] ............ [render ZOM-2] [cleanup ZOM-1] [effect ZOM-2] ... [unmount] [cleanup ZOM-2]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useEffect | Hook for side effects after paint | Paint के बाद side effect चलाने वाला hook |
| useLayoutEffect | Effect that runs before paint | Paint से पहले चलने वाला effect |
| Dependency array | List of values that trigger a re-run | वे values जिनके बदलने पर effect दोबारा चले |
| Cleanup | Function returned from an effect | Effect से लौटाया गया teardown function |
| Stale closure | Callback holding an old value | पुराना value पकड़े हुए callback |
| AbortController | Object to cancel a request | Request रद्द करने वाला object |
| Side effect | Work outside rendering | Render के बाहर का काम |
| Object.is | Equality check used for deps | Deps compare करने का तरीका |

---

## ⚡ 3-Line Summary
**English:**
1. `useEffect` replaces the three class methods; it runs after paint, and its cleanup handles teardown.
2. Use the dependency array to control when the effect re-runs, and include every value the effect reads.
3. Use `useLayoutEffect` only for layout-sensitive work, and use `AbortController` to cancel stale requests.

**Hindi:**
1. `useEffect` तीन class methods की जगह लेता है; यह paint के बाद चलता है और cleanup से teardown होता है।
2. Dependency array से तय करो effect कब दोबारा चले, और effect में इस्तेमाल हर value उसमें डालो।
3. `useLayoutEffect` सिर्फ layout-sensitive काम के लिए, और stale requests रोकने के लिए `AbortController`।

---

## ➡️ Next Topic
**60. Props Drilling Problem** — Props को कई levels तक नीचे भेजने की समस्या। Lifecycle के बाद यह समझना ज़रूरी है कि data component tree में कैसे बहता है, और इसी से Context API की ज़रूरत समझ आती है।
