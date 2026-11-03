# 38. useEffect Cleanup Function
# हिंदी में: useEffect Cleanup Function — Effect के बाद सफ़ाई

---

## 🔵 Simple Definition (English)
The **cleanup function** is the function you `return` from an effect. React calls it before the effect re-runs and when the component unmounts. Use it to undo what the effect started: clear timers, remove event listeners, close connections and cancel requests.

## 🔵 सरल परिभाषा (Hindi)
**Cleanup function** वह function है जो आप effect से `return` करते हैं। React इसे effect के दोबारा चलने से पहले और component के unmount होने पर चलाता है। इससे effect की शुरू की हुई चीज़ें बंद करें: timers, event listeners, connections और requests।

---

## 🔴 Problem it Solves

Effects often start something that keeps living: `setInterval`, `addEventListener`, a WebSocket, a subscription. If you never stop it, you get **memory leaks**, duplicated listeners (every re-run adds one more), updates on an unmounted component, and **race conditions** (an old slow request finishing after a new one and overwriting fresh data).

```jsx
// PROBLEM: listener added on every run, never removed
useEffect(() => {
  window.addEventListener('resize', onResize);        // each run adds ANOTHER listener
});                                                    // ❌ leak

// SOLUTION: return a cleanup
useEffect(() => {
  window.addEventListener('resize', onResize);
  return () => window.removeEventListener('resize', onResize); // ✅ removed before next run / unmount
}, []);
```

## 🔴 यह क्यों बना? (Hindi)
Effects अक्सर ऐसी चीज़ें शुरू करते हैं जो चलती रहती हैं: `setInterval`, `addEventListener`, WebSocket, subscription। इन्हें बंद न करें तो **memory leak**, दोहराए गए listeners (हर re-run एक और जोड़ता है), unmounted component पर updates, और **race condition** (पुराना धीमा request नए के बाद पूरा होकर fresh data को overwrite कर दे) होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Render #1, commit to DOM, React runs effect #1 (it starts a timer, returns cleanup #1)
Step 2 → React stores cleanup #1 (a closure that remembers render #1's values)
Step 3 → A dependency changes → Render #2 happens and commits
Step 4 → BEFORE running effect #2, React runs cleanup #1 (with render #1's old values)
Step 5 → Then React runs effect #2 and stores cleanup #2
Step 6 → On unmount, React runs the last cleanup one final time

ORDER:  effect#1 → (re-render) → cleanup#1 → effect#2 → (unmount) → cleanup#2
StrictMode (dev): mount → effect → cleanup → effect  (to expose missing cleanup)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Render #1, DOM में commit, React effect #1 चलाता है (timer शुरू होता है, cleanup #1 return होता है)
Step 2 → React cleanup #1 रखता है (एक closure जो render #1 की values याद रखता है)
Step 3 → कोई dependency बदली → Render #2 होता है और commit होता है
Step 4 → effect #2 चलाने से PEHLE React cleanup #1 चलाता है (render #1 की पुरानी values के साथ)
Step 5 → फिर effect #2 चलता है और cleanup #2 रखा जाता है
Step 6 → Unmount पर React आखिरी cleanup एक बार चलाता है

क्रम:  effect#1 → (re-render) → cleanup#1 → effect#2 → (unmount) → cleanup#2
StrictMode (dev): mount → effect → cleanup → effect  (छूटा cleanup पकड़ने के लिए)
```

---

## 🟡 Real World Example
**Swiggy order tracking:** The tracking screen opens a WebSocket to get live delivery-partner location. When you leave the screen, cleanup closes the socket. If you open a different order, cleanup closes the old order's socket before opening the new one. Without cleanup, you would receive location updates for old orders and the phone's battery would drain.

## 🟡 Real Example Hindi mein
**Swiggy order tracking:** Tracking screen delivery partner की live location के लिए WebSocket खोलती है। Screen छोड़ने पर cleanup socket बंद कर देता है। दूसरा order खोलने पर नया socket खुलने से पहले cleanup पुराने order का socket बंद करता है। Cleanup न हो तो पुराने orders की location updates आती रहेंगी और फ़ोन की battery खर्च होगी।

---

## 💻 Code Example — Basic

```jsx
// A ticking timer with proper cleanup
import { useState, useEffect } from 'react';          // hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function Clock() {
  const [seconds, setSeconds] = useState(0);          // elapsed seconds

  useEffect(() => {
    console.log('start timer');                       // effect body: start the timer
    const id = setInterval(() => {
      setSeconds(s => s + 1);                         // functional update: no stale value
    }, 1000);

    return () => {                                    // cleanup function
      console.log('stop timer');                      // runs on unmount (and before re-runs)
      clearInterval(id);                              // stop the interval, no leak
    };
  }, []);                                             // [] → start once, stop on unmount

  return <p>Seconds: {seconds}</p>;                   // re-renders every second
}

function App() {
  const [show, setShow] = useState(true);             // toggles Clock mount
  return (
    <div>
      <button onClick={() => setShow(v => !v)}>Toggle</button>
      {show && <Clock />}                             {/* hiding it triggers cleanup */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Live order tracking: WebSocket + race-safe fetch, both cleaned up per orderId
import { useState, useEffect } from 'react';          // hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function OrderTracker({ orderId }) {
  const [order, setOrder] = useState(null);           // order details from the API
  const [location, setLocation] = useState(null);     // live rider location

  // Effect 1: load order details, ignore stale responses
  useEffect(() => {
    const controller = new AbortController();         // cancel on cleanup
    fetch(`/api/orders/${orderId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(setOrder)                                 // only the latest request reaches here
      .catch(e => { if (e.name !== 'AbortError') console.error(e); }); // ignore intended aborts
    return () => controller.abort();                  // orderId changed/unmounted → cancel old
  }, [orderId]);

  // Effect 2: subscribe to live location
  useEffect(() => {
    const ws = new WebSocket(`wss://example.com/track/${orderId}`); // open connection
    ws.onmessage = e => setLocation(JSON.parse(e.data));            // update on each message
    ws.onerror = () => console.warn('socket error');                // do not crash the UI
    return () => ws.close();                          // close socket for this order
  }, [orderId]);                                      // new order → close old, open new

  if (!order) return <p>Loading...</p>;               // first render has no data yet
  return (
    <div>
      <h2>Order #{order.id}</h2>
      <p>Status: {order.status}</p>
      <p>Rider: {location ? `${location.lat}, ${location.lng}` : 'locating...'}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<OrderTracker orderId="SW-42" />);
```

---

## 🟠 Next.js Connection

Cleanup matters in Client Components (`'use client'`), because effects never run on the server. During SSR, React skips effects completely, so `window` or `WebSocket` inside an effect is safe. Also, with the App Router, navigation between pages unmounts a page's components, so cleanup runs on route change. Libraries like `next/navigation` hooks do their own cleanup.

```jsx
// app/track/[id]/LiveLocation.jsx (Client Component)
'use client';
import { useEffect, useState } from 'react';

export default function LiveLocation({ id }) {
  const [pos, setPos] = useState(null);                  // latest location

  useEffect(() => {                                      // only runs in the browser
    const es = new EventSource(`/api/track/${id}/stream`); // Server-Sent Events from a Route Handler
    es.onmessage = e => setPos(JSON.parse(e.data));      // update state on each event
    return () => es.close();                             // leaving the page closes the stream
  }, [id]);

  return <p>{pos ? `${pos.lat}, ${pos.lng}` : 'Waiting for rider...'}</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to remove an event listener
✅ **Correct:** Pass the same function reference to `removeEventListener`

```jsx
// Wrong: a new arrow function each time, so remove does nothing
useEffect(() => {
  window.addEventListener('scroll', () => setY(window.scrollY)); // ❌ never removed
}, []);

// Right: keep a named reference and remove it
useEffect(() => {
  const onScroll = () => setY(window.scrollY);         // same reference for add and remove
  window.addEventListener('scroll', onScroll);
  return () => window.removeEventListener('scroll', onScroll); // ✅
}, []);
```

❌ **Mistake 2:** No protection against race conditions in fetch
✅ **Correct:** Abort the request (or use an `ignore` flag) in cleanup

```jsx
// Wrong: slow response for "pizza" may arrive after "pasta" and overwrite it
useEffect(() => {
  fetch(`/api?q=${q}`).then(r => r.json()).then(setData);  // ❌
}, [q]);

// Right: ignore flag set by cleanup
useEffect(() => {
  let ignore = false;                                  // belongs to THIS effect run
  fetch(`/api?q=${q}`).then(r => r.json()).then(d => { if (!ignore) setData(d); });
  return () => { ignore = true; };                     // ✅ old runs are ignored
}, [q]);
```

❌ **Mistake 3:** Returning a Promise (making the effect `async`)
✅ **Correct:** Put an async function inside and call it

```jsx
// Wrong: async functions return a Promise, React expects a function or nothing
useEffect(async () => { await load(); }, []);          // ❌ warning, cleanup impossible

// Right
useEffect(() => {
  async function run() { await load(); }               // ✅ async inside
  run();
}, []);
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';

function App() {
  const [n, setN] = useState(0);

  useEffect(() => {
    console.log('effect', n);
    return () => console.log('cleanup', n);
  }, [n]);

  return <button onClick={() => setN(n + 1)}>+</button>;
}
```
**Answer:** After mount: `effect 0`. After first click: `cleanup 0` then `effect 1`. After second click: `cleanup 1` then `effect 2`. The cleanup logs the **old** value because it is a closure created in the render where `n` was that value. Cleanup runs after the new render has been committed, but it still sees its own render's variables. In development with StrictMode, mount logs `effect 0`, `cleanup 0`, `effect 0`.

---

## ⚫ Interview Questions + Answers

Q1: When does the cleanup function run?
A1: Before the effect runs again because a dependency changed, and once when the component unmounts. With `[]` it runs only on unmount.

Q2: Which values does cleanup see, new or old?
A2: The old ones, from the render that created that effect. It is a closure, so it correctly releases exactly what that run set up.

Q3: Why does StrictMode run my effect twice in development?
A3: React 18+ mounts, unmounts and re-mounts to check that your cleanup properly reverses the setup. It only happens in development. If it breaks your app (double requests, duplicate listeners), a cleanup is missing.

Q4: How do you prevent a race condition in data fetching in an effect?
A4: Use `AbortController` and abort in cleanup, or a boolean `ignore` flag set to `true` in cleanup. In production apps a library like TanStack Query handles this for you.

Q5: Does every effect need a cleanup?
A5: No. Only effects that start something ongoing (timers, listeners, subscriptions, connections, requests). A plain `document.title = ...` needs none.

---

## 🔷 When to Use + When Not to Use
✅ **Use cleanup when:**
- You call `setInterval`, `setTimeout`, `addEventListener`, `subscribe`, `new WebSocket`
- You start a fetch that can become outdated
- You create third-party widgets (maps, charts) that have a `destroy()` method

❌ **Avoid / not needed when:**
- The effect only sets a value (`document.title`) that the next run overwrites
- You can use a library hook that already manages the lifecycle
- You are tempted to use cleanup to "reset state" (prefer a `key` to remount instead)

---

## 📊 Visual Diagram

```
 MOUNT            UPDATE (dep changed)                   UNMOUNT
   │                      │                                 │
   ▼                      ▼                                 ▼
 render ──► effect#1   render ──► cleanup#1 ──► effect#2   cleanup#2
              │                      ▲              │           ▲
              └─ returns cleanup#1 ──┘              └─ returns cleanup#2

 Re-render cost: cleanup + effect run again ONLY if deps changed.
 Performance: leaked listeners grow with every re-run → slower page, higher memory.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cleanup function | Function returned from an effect | Effect से return होने वाला function |
| Memory leak | Memory never freed | Memory का कभी मुक्त न होना |
| Race condition | Older async result overwrites newer | पुराना async नतीजा नए को overwrite करे |
| AbortController | API to cancel fetch | Fetch रद्द करने की API |
| Subscription | Ongoing data feed | लगातार चलने वाला data feed |
| StrictMode | Dev mode double-invoking effects | Dev में effects दो बार चलाने वाला mode |
| Unmount | Component removed from the DOM | Component का DOM से हटना |

---

## ⚡ 3-Line Summary
**English:**
1. The function returned from an effect is its cleanup, run before the next effect and on unmount.
2. Use it to stop timers, remove listeners, close sockets and abort stale requests.
3. Cleanup sees the values of its own render, and StrictMode double-run helps catch missing cleanups.

**Hindi:**
1. Effect से return हुआ function उसका cleanup है, जो अगले effect से पहले और unmount पर चलता है।
2. इससे timers रोकें, listeners हटाएँ, sockets बंद करें और पुराने requests abort करें।
3. Cleanup अपने ही render की values देखता है, और StrictMode का double-run छूटे हुए cleanup पकड़ने में मदद करता है।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) | Cleanup, StrictMode, fetching |
| 📝 Article | [MDN — AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) | Cancelling requests |

---

## ➡️ Next Topic
**39. useEffect vs componentDidMount** — class lifecycle methods (`componentDidMount`, `componentDidUpdate`, `componentWillUnmount`) बनाम `useEffect`। Interviews में दोनों की तुलना अक्सर पूछी जाती है।
