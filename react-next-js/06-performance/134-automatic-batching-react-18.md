# 134. Automatic Batching (React 18)
# हिंदी में: Automatic Batching — कई state updates, एक ही render

---

## 🔵 Simple Definition (English)
**Batching** means React groups multiple state updates into a single re-render instead of re-rendering after each one. Before React 18 this happened only inside React event handlers. **Automatic batching** (React 18, with `createRoot`) extends it to everything: promises, `setTimeout`, native event handlers and any other code.

## 🔵 सरल परिभाषा (Hindi)
**Batching** का मतलब है React कई state updates को एक ही re-render में जोड़ देता है, हर update के बाद अलग render नहीं करता। React 18 से पहले यह सिर्फ़ React event handlers के अंदर होता था। **Automatic batching** (React 18, `createRoot` के साथ) इसे हर जगह ले जाती है: promises, `setTimeout`, native event handlers और बाकी किसी भी code में।

---

## 🔴 Problem it Solves

In React 17, three `setState` calls inside a `fetch().then()` caused three renders. That is wasted work, and users could see inconsistent half-updated UI (for example `loading` already false but `data` not yet set).

```jsx
// PROBLEM (React 17): outside event handlers, each set call re-rendered immediately
fetch('/api/cart').then(res => res.json()).then(data => {
  setItems(data.items);      // render 1 (items updated, total still old)
  setTotal(data.total);      // render 2
  setLoading(false);         // render 3
});

// SOLUTION (React 18 + createRoot): all three updates → ONE render
```

## 🔴 यह क्यों बना? (Hindi)
React 17 में `fetch().then()` के अंदर तीन `setState` calls तीन renders बनाती थीं। यह बेकार काम है, और users को आधा-बदला inconsistent UI दिख सकता था (जैसे `loading` false हो गया पर `data` अभी set नहीं हुआ)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Code calls setA(...), setB(...), setC(...) one after another
Step 2 → React does NOT render yet; it queues each update with its priority
Step 3 → When the current JavaScript task finishes (microtask/event end), React processes the queue
Step 4 → It applies all queued updates to the state together
Step 5 → It re-renders the component tree ONCE with the final state
Step 6 → The DOM is committed once, and effects run after that

KEY: state updates are asynchronous: the variable in your closure still has the old value until the next render
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Code एक के बाद एक setA(...), setB(...), setC(...) call करता है
Step 2 → React अभी render नहीं करता; वह हर update को उसकी priority के साथ queue में रखता है
Step 3 → मौजूदा JavaScript task ख़त्म होने पर (microtask/event का अंत) React queue process करता है
Step 4 → वह सारे queued updates को एक साथ state पर लगाता है
Step 5 → वह component tree को अंतिम state के साथ सिर्फ़ एक बार re-render करता है
Step 6 → DOM एक बार commit होता है, और उसके बाद effects चलते हैं

KEY: state updates asynchronous हैं: आपके closure का variable अगले render तक पुरानी value ही रखता है
```

---

## 🟡 Real World Example
**Amazon "Add to cart" response:** After the server replies, the UI must update the item count in the header badge, the cart total, the "added" toast and the button's loading state. That is 4 state updates in one promise callback. In React 17, 4 renders could happen, and the badge might show 3 items while the total still showed the old price for a split second. In React 18 all four update together in a single render, so the screen is always consistent and cheaper to draw.

## 🟡 Real Example Hindi mein
**Amazon "Add to cart" का response:** Server के जवाब के बाद UI में header badge का item count, cart total, "added" toast और button की loading state बदलनी होती है। यानी एक promise callback में 4 state updates। React 17 में 4 renders हो सकते थे, और एक पल के लिए badge 3 items दिखाता जबकि total पुरानी कीमत पर रहता। React 18 में चारों एक ही render में बदलते हैं, इसलिए screen हमेशा consistent रहती है और draw करना सस्ता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: count renders to SEE batching in action
import { useState, useRef } from 'react';              // state + ref
import { createRoot } from 'react-dom/client';         // createRoot is REQUIRED for automatic batching

function Counter() {
  const [count, setCount] = useState(0);               // first state
  const [flag, setFlag] = useState(false);             // second state
  const renders = useRef(0);                           // counts renders without causing renders
  renders.current += 1;                                // increments on each render

  function handleAsync() {
    setTimeout(() => {                                 // outside a React event handler
      setCount(c => c + 1);                            // update 1
      setFlag(f => !f);                                // update 2
      // React 18: both are batched → ONE render
      // React 17 / legacy ReactDOM.render: TWO renders
    }, 0);
  }

  return (
    <div>
      <p>count: {count} | flag: {String(flag)} | renders: {renders.current}</p>
      <button onClick={handleAsync}>Update (async)</button> {/* each click adds 1 to renders in React 18 */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Counter />); // concurrent root = automatic batching
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a real "add to cart" flow, with batching, functional updates and the flushSync opt-out
import { useState, useRef } from 'react';              // hooks
import { flushSync } from 'react-dom';                 // force an immediate render (rarely needed)
import { createRoot } from 'react-dom/client';         // root API

// Fake API
const addToCartApi = id => new Promise(r => setTimeout(() => r({ count: 3, total: 1299 }), 500));

function CartButton({ productId }) {
  const [state, setState] = useState({ status: 'idle', count: 2, total: 999 }); // one object = naturally atomic
  const [toast, setToast] = useState(null);            // separate state: still batched with the others
  const listRef = useRef(null);                        // DOM ref for the flushSync example

  async function onAdd() {
    setState(s => ({ ...s, status: 'loading' }));      // runs before the await, batched in this event
    try {
      const data = await addToCartApi(productId);      // after await we are OUTSIDE the event handler
      // React 18: these three updates are batched even though we are after an await
      setState({ status: 'done', count: data.count, total: data.total }); // update 1
      setToast('Added to cart');                       // update 2
      setTimeout(() => setToast(null), 2000);          // update 3 (later): also batched on its own tick
    } catch {
      setState(s => ({ ...s, status: 'error' }));      // error UI
    }
  }

  function scrollToLastAfterAdd() {
    // Rare case: you need the DOM updated NOW (e.g. to measure or scroll)
    flushSync(() => {                                  // forces a synchronous render for the updates inside
      setState(s => ({ ...s, count: s.count + 1 }));   // this update is rendered immediately
    });
    listRef.current?.scrollIntoView();                 // DOM already reflects the new count here
  }

  return (
    <div>
      <button onClick={onAdd} disabled={state.status === 'loading'}>
        {state.status === 'loading' ? 'Adding...' : 'Add to cart'}
      </button>
      <span ref={listRef}> Cart: {state.count} items, Rs {state.total}</span>
      {toast && <p role="status">{toast}</p>}
      <button onClick={scrollToLastAfterAdd}>flushSync demo</button>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<CartButton productId="p1" />);
```

---

## 🟠 Real App Integration

Next.js (App Router and Pages Router on React 18+) uses `createRoot`/`hydrateRoot` internally, so automatic batching is always on in your Client Components. You do not need any config. Batching also applies to Server Actions results: updating several pieces of state after `await action()` re-renders once.

```jsx
// app/cart/AddToCart.jsx
'use client';                                            // state and handlers need a Client Component
import { useState } from 'react';
import { addToCart } from './actions';                    // a Server Action ('use server' file; hypothetical)

export default function AddToCart({ id }) {
  const [pending, setPending] = useState(false);         // loading flag
  const [count, setCount] = useState(0);                 // items in cart
  const [message, setMessage] = useState('');            // toast text

  async function onClick() {
    setPending(true);                                    // batched in the click event
    const result = await addToCart(id);                  // server round trip
    setCount(result.count);                              // after await: batched together with the next two
    setMessage('Added!');
    setPending(false);                                   // ONE re-render for these three updates in React 18
  }

  return (
    <div>
      <button onClick={onClick} disabled={pending}>Add</button>
      <span>{count}</span> <span>{message}</span>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Reading state right after setting it and expecting the new value
✅ **Correct:** Use the functional form or compute the next value in a variable

```jsx
// Wrong: count is still the OLD value in this closure → ends up +1, not +3
function addThree() {
  setCount(count + 1);                                  // ❌ uses stale count
  setCount(count + 1);
  setCount(count + 1);
}

// Right: updater functions queue properly
function addThree2() {
  setCount(c => c + 1);                                 // ✅ each gets the latest queued value
  setCount(c => c + 1);
  setCount(c => c + 1);                                 // result: +3, one render
}
```

❌ **Mistake 2:** Using `ReactDOM.render` (React 17 API) and assuming React 18 behavior
✅ **Correct:** Migrate to `createRoot`; automatic batching only works with it

```jsx
// Wrong: legacy root → old batching rules (only inside React events)
ReactDOM.render(<App />, root);                         // ❌ (removed in React 19)

// Right
createRoot(root).render(<App />);                       // ✅ automatic batching on
```

❌ **Mistake 3:** Using `flushSync` to "fix" timing problems
✅ **Correct:** Use effects/refs or restructure; flushSync is for rare DOM measurement needs

```jsx
// Wrong: forces extra synchronous renders, loses batching → slower
flushSync(() => setA(1));                               // ❌ render 1
flushSync(() => setB(2));                               // ❌ render 2

// Right: let React batch
setA(1);                                                // ✅
setB(2);                                                // both in one render
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [n, setN] = useState(0);
  console.log('render', n);

  function onClick() {
    setN(n + 1);
    console.log('after set:', n);
    setTimeout(() => {
      setN(n + 10);
      console.log('in timeout:', n);
    }, 0);
  }

  return <button onClick={onClick}>go</button>;
}
// Question: start with n = 0, click once. What is logged (React 18, no StrictMode)?
```
**Answer:**
```
render 0          (initial)
after set: 0      (state is a snapshot; setN does not change n in this closure)
render 1          (the click's update renders, batched)
in timeout: 0     (the timeout closure still sees n = 0 from the click's render)
render 10         (setN(0 + 10) → n becomes 10; it is based on stale n = 0, not 1)
```
Each render's `n` is a constant snapshot. The timeout callback captured `n = 0`, so `setN(n + 10)` sets 10, not 11. If you want 11, use `setN(c => c + 10)`. Batching only groups updates into one render; it does not change the snapshot rule.

---

## ⚫ Interview Questions + Answers

Q1: What is automatic batching in React 18?
A1: React groups all state updates that happen in the same tick into one render, regardless of where they originate: event handlers, promises, timeouts, native events. In React 17 it did this only inside React event handlers.

Q2: How do you enable it?
A2: Render with `createRoot` from `react-dom/client` (or `hydrateRoot` for SSR). The legacy `ReactDOM.render` keeps the old behavior. No other code changes are needed.

Q3: How do you opt out of batching?
A3: Wrap the update in `flushSync` from `react-dom`. It renders that update synchronously. Use it only when you need the DOM updated immediately (measure layout, scroll, focus), because it removes the batching benefit.

Q4: Does batching mean state updates are asynchronous?
A4: Yes, from your code's point of view: `setState` queues an update and the new value appears on the next render. The variable in the current closure is a snapshot. Use functional updates (`setX(x => x + 1)`) when the next value depends on the previous one.

Q5: Are updates from different events batched together?
A5: No. Batching groups updates inside the same event or tick. Two separate clicks are two separate batches, and React guarantees one event is fully processed (for discrete events like clicks) before the next starts.

---

## 🔷 When to Use + When Not to Use
✅ **Rely on batching (always) and:**
- Update several states together after an API call
- Use functional updates for dependent values
- Merge related fields into one object or `useReducer` when they must change together

❌ **Opt out (`flushSync`) only when:**
- You must read updated DOM layout right after a state change
- You integrate with a third-party library that needs the DOM updated synchronously
- Never as a general fix for "state not updating immediately"

---

## 📊 Visual Diagram

```
  React 17 (outside events):                 React 18 (everywhere):

  setItems() ─▶ render #1                    setItems() ┐
  setTotal() ─▶ render #2                    setTotal() ├─ queued ─▶ ONE render ─▶ commit
  setLoading()─▶ render #3                   setLoading()┘

  Timeline of one task:
  [ handler runs: set, set, set ]──▶ end of task ──▶ [ render once with final state ] ──▶ [ commit ] ──▶ [ effects ]
```

Re-render behavior: N updates in one tick produce one render of the component and its children (unless memoized). Performance impact: fewer renders and DOM commits, and no visually inconsistent intermediate states, usually with zero code change after migrating to `createRoot`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Batching | Grouping several updates into one render | कई updates को एक render में जोड़ना |
| Automatic batching | Batching everywhere, not only in React events | हर जगह batching, सिर्फ़ React events में नहीं |
| createRoot | React 18 root API needed for it | इसके लिए ज़रूरी React 18 root API |
| flushSync | Forces a synchronous render (opt-out) | Synchronous render मजबूर करना (opt-out) |
| Functional update | `setX(prev => ...)` form | `setX(prev => ...)` तरीका |
| Snapshot | State value fixed for one render | एक render के लिए तय state value |
| Render queue | Pending updates waiting to be processed | Process होने का इंतज़ार करते pending updates |
| Commit | Applying the render result to the DOM | Render के नतीजे को DOM में लगाना |

---

## ⚡ 3-Line Summary
**English:**
1. React 18 batches all state updates in the same tick into one render, even in promises, timeouts and native events.
2. It requires `createRoot`; use functional updates because state is a per-render snapshot; `flushSync` opts out.
3. Next.js uses `createRoot` internally, so you get it for free in Client Components.

**Hindi:**
1. React 18 एक ही tick के सभी state updates को एक render में जोड़ता है, promises, timeouts और native events में भी।
2. इसके लिए `createRoot` चाहिए; functional updates इस्तेमाल करो क्योंकि state हर render का snapshot है; `flushSync` से opt-out होता है।
3. Next.js अंदर `createRoot` इस्तेमाल करता है, इसलिए Client Components में यह अपने आप मिलता है।

---

## ➡️ Next Topic
**135. Transitions (useTransition)** — urgent और non-urgent updates को अलग करना, `isPending` से feedback देना, और `startTransition` से भारी UI updates को responsive रखना।
