# 32. React StrictMode
# हिंदी में: React StrictMode — Development में छिपी गलतियाँ पकड़ने वाला Wrapper

---

## 🔵 Simple Definition (English)
**`<StrictMode>`** is a built-in React component that adds extra checks and warnings for its children, **only in development**. It renders components twice, re-runs effects once more, and warns about deprecated APIs, to expose impure rendering and missing cleanup. It has no visible UI and no effect in production.

## 🔵 सरल परिभाषा (Hindi)
**`<StrictMode>`** एक built-in React component है जो अपने children के लिए अतिरिक्त checks और warnings जोड़ता है, **सिर्फ development में**। यह components को दो बार render करता है, effects को एक बार और चलाता है, और deprecated APIs पर warn करता है, ताकि impure rendering और cleanup की कमी सामने आ जाए। इसका कोई visible UI नहीं है और production में कोई असर नहीं।

---

## 🔴 Problem it Solves

Some bugs only appear in special situations: React can pause, restart or discard a render (concurrent rendering), a component can be unmounted and remounted (for example with Offscreen/Activity, Fast Refresh, or route transitions), and effects can run again after a state is restored. Code that mutates variables during render, forgets to clean up a subscription, or fires a request twice may look fine today and break later. StrictMode simulates these situations during development, so such bugs show up immediately, on your machine, not in production for a customer.

```jsx
// PROBLEM: impure render and missing cleanup look OK until concurrency shows the bug
let counter = 0;                                   // module-level mutable variable
function Item() {
  counter++;                                       // ❌ side effect during render
  return <p>Item {counter}</p>;                    // shows 2 in StrictMode (rendered twice)
}

useEffect(() => {
  const ws = new WebSocket(url);                   // ❌ never closed → two sockets after remount
}, []);
```

## 🔴 यह क्यों बना? (Hindi)
कुछ bugs सिर्फ खास हालात में दिखते हैं: React किसी render को रोक सकता है, दोबारा शुरू कर सकता है या छोड़ सकता है (concurrent rendering), component unmount होकर फिर mount हो सकता है (जैसे Offscreen/Activity, Fast Refresh या route transitions में), और state restore होने पर effects फिर चल सकते हैं। जो code render के दौरान variables बदलता है, subscription की cleanup भूल जाता है, या request दो बार भेजता है, वह आज ठीक दिख सकता है पर बाद में टूट सकता है। StrictMode development में यही हालात simulate करता है, ताकि ऐसे bugs आपकी machine पर तुरंत दिखें, production में customer को नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap your app:  <StrictMode><App /></StrictMode>
Step 2 → DEV only: React calls component functions, useState/useMemo/useReducer initializers
         and updater functions TWICE (second result is thrown away) → exposes impure code
Step 3 → DEV only: after a component mounts, React simulates unmount + remount:
         effect setup → cleanup → setup again  → exposes missing/incorrect cleanup
Step 4 → DEV only: ref callbacks also get an extra setup/cleanup cycle (React 19)
Step 5 → DEV only: warns about deprecated APIs (findDOMNode, legacy context, string refs...)
Step 6 → Console logs from the 2nd render are dimmed in React DevTools (React 18+)
Step 7 → Production build: StrictMode does NOTHING, no extra render, no extra effect

RULE: if StrictMode "breaks" your code, the code has a bug. Fix the code, not the StrictMode.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App को wrap करो:  <StrictMode><App /></StrictMode>
Step 2 → सिर्फ DEV: React component functions, useState/useMemo/useReducer के initializers
         और updater functions को दो बार call करता है (दूसरा result फेंक दिया जाता है) → impure code पकड़ा जाता है
Step 3 → सिर्फ DEV: Component mount होने के बाद React unmount + remount simulate करता है:
         effect setup → cleanup → फिर setup  → गायब/गलत cleanup पकड़ी जाती है
Step 4 → सिर्फ DEV: ref callbacks को भी एक extra setup/cleanup cycle मिलता है (React 19)
Step 5 → सिर्फ DEV: deprecated APIs पर warning (findDOMNode, legacy context, string refs...)
Step 6 → दूसरे render के console logs React DevTools में हल्के रंग में दिखते हैं (React 18+)
Step 7 → Production build: StrictMode कुछ नहीं करता, extra render या effect नहीं

नियम: अगर StrictMode आपका code "तोड़" दे, तो code में bug है। Code ठीक करो, StrictMode नहीं।
```

---

## 🟡 Real World Example
**Zomato live order tracking:** The tracking screen opens a WebSocket in `useEffect` to receive rider location. The developer forgot to close the socket in cleanup. In StrictMode (dev), the effect runs, cleans up (nothing happens), runs again, so the developer sees **two** connections and duplicate rider updates in the Network tab. They add `return () => ws.close()` and the bug is gone before it ever reaches users, where it would have been an extra socket on every navigation, slowly draining battery and server resources.

## 🟡 Real Example Hindi mein
**Zomato live order tracking:** Tracking screen rider की location पाने के लिए `useEffect` में WebSocket खोलती है। Developer cleanup में socket बंद करना भूल गया। StrictMode (dev) में effect चलता है, cleanup (कुछ नहीं होता), फिर दोबारा चलता है, इसलिए developer को Network tab में **दो** connections और दोहरे rider updates दिखते हैं। वह `return () => ws.close()` जोड़ता है और bug users तक पहुँचने से पहले ही खत्म हो जाता है; वहाँ यह हर navigation पर एक extra socket होता, जो धीरे-धीरे battery और server resources खाता।

---

## 💻 Code Example — Basic

```jsx
// main.jsx — enable StrictMode for the whole app (Vite template does this by default)
import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function Demo() {
  const [count, setCount] = useState(0);

  console.log('render');                       // logged TWICE per render in dev StrictMode

  useEffect(() => {
    console.log('effect setup');              // dev: setup → cleanup → setup on mount
    return () => console.log('effect cleanup');
  }, []);

  return <button onClick={() => setCount((c) => c + 1)}>Clicked {count}</button>;
}

createRoot(document.getElementById('root')).render(
  <StrictMode>                                {/* only affects development builds */}
    <Demo />
  </StrictMode>
);

// Console in DEV on first load:
//   render
//   render                (second, discarded render)
//   effect setup
//   effect cleanup        (simulated unmount)
//   effect setup          (simulated remount)
```

## 💻 Code Example — Advanced

```jsx
// Real world: code that survives StrictMode — subscription cleanup, abortable fetch, pure render
import { useEffect, useState } from 'react';

function RiderTracker({ orderId }) {
  const [position, setPosition] = useState(null);      // latest rider position
  const [error, setError] = useState(null);

  // 1) Subscription: setup AND cleanup, so mount → unmount → mount leaves exactly one socket
  useEffect(() => {
    const ws = new WebSocket(`wss://example.com/track/${orderId}`);
    ws.onmessage = (e) => setPosition(JSON.parse(e.data));   // update on each message
    ws.onerror = () => setError('Connection problem');
    return () => ws.close();                                 // ✅ closes the first socket in StrictMode
  }, [orderId]);

  return (
    <div>
      {error && <p role="alert">{error}</p>}
      <p>{position ? `Rider at ${position.lat}, ${position.lng}` : 'Waiting for rider...'}</p>
    </div>
  );
}

function RestaurantDetails({ id }) {
  const [data, setData] = useState(null);

  // 2) Fetch: AbortController cancels the first request when StrictMode re-runs the effect
  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/restaurants/${id}`, { signal: controller.signal })
      .then((r) => r.json())
      .then(setData)
      .catch((e) => { if (e.name !== 'AbortError') console.error(e); }); // ignore our own abort
    return () => controller.abort();                          // ✅ cancel on cleanup
  }, [id]);

  return <h2>{data ? data.name : 'Loading...'}</h2>;
}

// 3) Pure render: derive values, never mutate outside variables during render
function Cart({ items }) {
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);  // ✅ pure calculation
  return <p>Total ₹{total}</p>;
}

export { RiderTracker, RestaurantDetails, Cart };
```

---

## 🟠 Real App Integration

In Next.js the App Router enables StrictMode **by default for the `app/` directory** (Next.js 13.5.1 and later) via `reactStrictMode`. You normally do not wrap anything manually; you can turn it off in `next.config.js`, though that is discouraged. In `pages/` (Pages Router) you opt in with the same flag.

```js
// next.config.js (Next.js 14/15)
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,     // explicit opt-in; App Router already uses StrictMode by default
};

module.exports = nextConfig;
```

```jsx
// app/layout.jsx — you do NOT add <StrictMode> yourself in the App Router
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>   {/* StrictMode is applied by Next.js in dev */}
    </html>
  );
}
```

Remember that a Server Component renders once on the server; the double-render and effect checks apply to Client Components in the browser.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Removing StrictMode because "my effect runs twice"
✅ **Correct:** Make the effect idempotent with a proper cleanup

```jsx
// Wrong: remove StrictMode to hide the double request
// createRoot(root).render(<App />)     // ❌ bug still exists, just hidden

// Right: cleanup makes the first run harmless
useEffect(() => {
  const ctrl = new AbortController();
  fetch('/api/menu', { signal: ctrl.signal }).then((r) => r.json()).then(setMenu);
  return () => ctrl.abort();                  // ✅
}, []);
```

❌ **Mistake 2:** Using a "run once" ref flag to skip the second effect
✅ **Correct:** Fix the cleanup. Do not block the re-run (it hides real bugs)

```jsx
// Wrong: hack that fights StrictMode (and breaks Fast Refresh and Activity remounts)
const ran = useRef(false);
useEffect(() => {
  if (ran.current) return;                    // ❌ skips the second run
  ran.current = true;
  trackPageView();
}, []);

// Right: analytics that need once-per-visit belong in an event handler, an app-level init,
// or a server-side log; effects should be safe to re-run
useEffect(() => {
  const controller = new AbortController();
  trackPageView({ signal: controller.signal });   // ✅ cancels if remounted
  return () => controller.abort();
}, []);
```

❌ **Mistake 3:** Mutating variables or props during render
✅ **Correct:** Keep render pure; do side effects in effects or event handlers

```jsx
// Wrong: the second render doubles the effect
let renders = 0;
function Badge({ items }) {
  renders++;                                  // ❌ mutated during render
  items.push('extra');                        // ❌ mutates a prop; list grows by 2 per render
  return <span>{items.length}</span>;
}

// Right
function Badge2({ items }) {
  const withExtra = [...items, 'extra'];      // ✅ new array, no mutation
  return <span>{withExtra.length}</span>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { StrictMode, useState, useEffect } from 'react';

let id = 0;

function Item() {
  const [myId] = useState(() => ++id);      // lazy initializer with a side effect
  useEffect(() => { console.log('mounted', myId); }, [myId]);
  return <p>{myId}</p>;
}

// <StrictMode><Item /></StrictMode>
```
Question: In development with StrictMode, what is shown on screen and logged?

**Answer:** The initializer runs **twice** (StrictMode double-invokes it), but React keeps the result of the first call. So the screen shows `1`, and the log prints `mounted 1` twice (setup, simulated cleanup, setup again). The side effect is hidden but real: the outside counter `id` is now `2`, although only one `Item` exists, so the next `Item` would get `3`, and ids skip numbers. (I ran this with React 19.3 and jsdom and got exactly this.) The lesson: initializers and render must be pure. Generate unique ids with `useId()` or `crypto.randomUUID()`, never by incrementing an outside counter.

---

## ⚫ Interview Questions + Answers

Q1: What does StrictMode do?
A1: In development it re-renders components an extra time, re-runs effects (setup, cleanup, setup) on mount, double-invokes initializers and reducers, and warns about deprecated APIs. It has no UI and no effect in production.

Q2: Why does my `useEffect` (or `console.log`) run twice?
A2: Because of StrictMode in development. It simulates unmount and remount to check that your cleanup works. If the effect is correct, the double run causes no visible problem. In production it runs once.

Q3: Does StrictMode affect production performance?
A3: No. All extra work is skipped in production builds. In development it makes the app a bit slower because of extra renders.

Q4: How do you fix a fetch that fires twice in StrictMode?
A4: Do not remove StrictMode. Add cleanup: an `AbortController` or an `ignore` flag so the first response is dropped. Better still, use a data library (TanStack Query, SWR) or Server Components, which handle deduplication.

Q5: Which things does StrictMode warn about?
A5: Legacy APIs (`findDOMNode`, string refs, legacy context, `componentWillMount` style lifecycles), impure rendering (visible through double render), missing effect cleanup, and in React 19 also incorrect ref callback cleanup. In React 18.3 there are additional deprecation warnings preparing for 19.

---

## 🔷 When to Use + When Not to Use
✅ **Use StrictMode when:**
- Always for the whole app in development (it is the default in Vite and Next.js templates)
- Migrating to React 18/19, to find unsafe lifecycle and effect code
- You want confidence that components work with concurrent features and Offscreen/Activity

❌ **Avoid disabling it when:**
- "The double effect is annoying" (the cleanup is probably missing)
- A third-party library breaks under it (wrap only the part you control, report a bug, or upgrade the library)
- You may exclude it from a specific subtree temporarily while migrating legacy code, but plan to remove that exception

---

## 📊 Visual Diagram

```
  <StrictMode><App/></StrictMode>

  DEVELOPMENT                                      PRODUCTION
  ──────────────────────────────                   ───────────────
  render()   ──▶ result A                          render() ──▶ result
  render()   ──▶ result B (discarded)              (single render)
       │ components must be pure: A == B

  mount ─▶ effect SETUP
        ─▶ effect CLEANUP   (simulated unmount)    mount ─▶ effect SETUP
        ─▶ effect SETUP     (simulated remount)    (once)
       │ cleanup must undo setup completely

  Deprecated API used?  ─▶ console warning         (no warnings from StrictMode)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StrictMode | Dev-only wrapper with extra checks | Extra checks वाला सिर्फ dev का wrapper |
| Double render | Component runs twice per render in dev | Dev में component का दो बार चलना |
| Pure render | Same props/state → same output, no side effects | Same input → same output, कोई side effect नहीं |
| Cleanup | Function returned from an effect that undoes it | Effect को undo करने वाला function |
| Idempotent | Safe to run many times | कई बार चलाना सुरक्षित |
| Simulated remount | Unmount then mount again in dev | Dev में unmount फिर mount |
| Deprecated API | Old API planned for removal | पुराना API जिसे हटाया जाएगा |
| `reactStrictMode` | Next.js config flag | Next.js का config flag |

---

## ⚡ 3-Line Summary
**English:**
1. StrictMode is a dev-only wrapper that double-renders and re-runs effects to expose impure code and missing cleanup.
2. A "double effect" is a signal to add cleanup (abort, close, unsubscribe), not to remove StrictMode.
3. It does nothing in production, and Next.js App Router enables it by default.

**Hindi:**
1. StrictMode सिर्फ dev का wrapper है जो दो बार render करता है और effects दोबारा चलाता है, ताकि impure code और missing cleanup पकड़ा जाए।
2. "Double effect" का मतलब है cleanup जोड़ो (abort, close, unsubscribe), StrictMode हटाओ मत।
3. यह production में कुछ नहीं करता, और Next.js App Router में डिफ़ॉल्ट रूप से चालू रहता है।

---

## ➡️ Next Topic
**33. React DevTools** — StrictMode से bugs मिलने के बाद उन्हें inspect और profile करने के लिए browser extension React DevTools सीखो: Components tab, Profiler और re-render highlighting।
