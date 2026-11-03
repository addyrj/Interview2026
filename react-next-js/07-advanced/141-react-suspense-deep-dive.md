# 141. React Suspense — Deep Dive
# हिंदी में: React Suspense — गहराई से समझना

---

## 🔵 Simple Definition (English)
**Suspense** lets a component "wait" for something (code, data) while React shows a fallback UI. When a child suspends, React shows the nearest `<Suspense fallback>`, and when it is ready, React shows the real content.

## 🔵 सरल परिभाषा (Hindi)
**Suspense** किसी component को किसी चीज़ (code, data) का "इंतज़ार" करने देता है, और तब तक React fallback UI दिखाता है। जब कोई child suspend होता है तो React सबसे नज़दीकी `<Suspense fallback>` दिखाता है, और तैयार होने पर असली content।

---

## 🔴 Problem it Solves

Before Suspense, every component handled loading by hand: `isLoading` flags, early returns, and spinners scattered everywhere. Loading state logic was duplicated, parents could not coordinate several loading children, and you saw "spinner cascades" (spinner inside spinner inside spinner).

```jsx
// PROBLEM: manual loading state in every component
function Profile({ id }) {
  const [user, setUser] = useState(null);             // null means loading
  useEffect(() => { fetchUser(id).then(setUser); }, [id]);
  if (!user) return <Spinner />;                      // repeated in every component
  return <h1>{user.name}</h1>;
}

// SOLUTION: the component just renders; the parent decides the loading UI
<Suspense fallback={<Spinner />}>
  <Profile id={1} />                                  {/* Profile suspends while data loads */}
</Suspense>
```

## 🔴 यह क्यों बना? (Hindi)
Suspense से पहले हर component loading खुद संभालता था: `isLoading` flags, early returns और जगह-जगह spinners। Loading का logic दोहराया जाता था, parent कई loading children को coordinate नहीं कर पाता था, और "spinner cascade" दिखता था (spinner के अंदर spinner)। Suspense में component सिर्फ render करता है और loading UI parent तय करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A component starts rendering and needs something not ready (lazy() code, use(promise), or a Suspense-enabled library)
Step 2 → It "suspends": React stops rendering that component (internally a promise is thrown)
Step 3 → React walks up to the nearest <Suspense> and shows its fallback instead of the subtree
Step 4 → When the promise resolves, React retries rendering the subtree
Step 5 → Success → fallback is replaced by the real content
Step 6 → If it throws an error instead, the nearest Error Boundary handles it
Step 7 → With startTransition/useDeferredValue, React can KEEP the old UI instead of showing the fallback again

Things that activate Suspense: React.lazy, use(promise) (React 19), Server Components async/await, TanStack Query suspense hooks, Relay, Next.js
NOT activated by: data fetching inside useEffect, event handlers
Re-render: when a boundary is already showing content and updates inside suspend, React shows the fallback again unless the update is a transition
Performance: avoids waterfalls when used well; hidden content state is preserved (React 18+)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component render करना शुरू करता है और उसे कुछ चाहिए जो तैयार नहीं (lazy() code, use(promise), या Suspense वाली library)
Step 2 → वह "suspend" होता है: React उस component का render रोक देता है (अंदर promise throw होता है)
Step 3 → React ऊपर की ओर सबसे नज़दीकी <Suspense> खोजकर subtree की जगह fallback दिखाता है
Step 4 → Promise resolve होने पर React subtree को दोबारा render करता है
Step 5 → सफल → fallback की जगह असली content
Step 6 → अगर error आए तो सबसे नज़दीकी Error Boundary उसे संभालता है
Step 7 → startTransition/useDeferredValue से React पुराना UI रख सकता है, fallback दोबारा नहीं दिखाता

Suspense कौन चलाता है: React.lazy, use(promise) (React 19), async Server Components, TanStack Query के suspense hooks, Relay, Next.js
नहीं चलाता: useEffect के अंदर data fetching, event handlers
Re-render: जब boundary पहले से content दिखा रही हो और अंदर कोई update suspend हो, तो transition न हो तो fallback दोबारा दिखता है
Performance: ठीक से इस्तेमाल करें तो waterfalls बचते हैं
```

---

## 🟡 Real World Example
**Flipkart product page:** The image carousel code, the reviews widget and the "similar products" list are separate chunks/data sources. Each is wrapped in its own Suspense boundary with a skeleton. The heavy review widget is loaded with `React.lazy` only when the user scrolls down. If the "similar products" API fails, an Error Boundary shows "Could not load" there without breaking the page.

## 🟡 Real Example Hindi mein
**Flipkart product page:** Image carousel का code, reviews widget और "similar products" की list अलग chunks/data sources हैं। हर एक की अपनी Suspense boundary और skeleton है। भारी reviews widget `React.lazy` से तभी load होता है जब user नीचे scroll करे। अगर "similar products" API fail हो तो Error Boundary वहीं "Could not load" दिखाती है और पूरा page नहीं टूटता।

---

## 💻 Code Example — Basic

```jsx
// Basic: Suspense with React.lazy (code splitting)
import { Suspense, lazy, useState } from 'react';       // core APIs
import { createRoot } from 'react-dom/client';           // root API

// lazy() loads this component's code only when it is first rendered
const Reviews = lazy(() =>
  new Promise((resolve) =>                               // fake delay to see the fallback
    setTimeout(() => resolve({ default: () => <p>4.5 stars (2,310 reviews)</p> }), 1500)
  )
);

function App() {
  const [show, setShow] = useState(false);               // controls when to load the reviews
  return (
    <div>
      <button onClick={() => setShow(true)}>Show reviews</button> {/* triggers loading */}
      {show && (
        <Suspense fallback={<p>Loading reviews...</p>}>  {/* shown while the chunk loads */}
          <Reviews />                                    {/* suspends on first render */}
        </Suspense>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: use(promise) + Error Boundary + transition to avoid re-showing the fallback (React 19)
import { Component, Suspense, use, useState, useTransition } from 'react'; // use() is React 19
import { createRoot } from 'react-dom/client';

// Simple class Error Boundary (error boundaries are still classes in React 19)
class ErrorBoundary extends Component {
  state = { error: null };                                // holds the caught error
  static getDerivedStateFromError(error) { return { error }; } // switch to error UI
  render() {
    if (this.state.error) return <p role="alert">Could not load: {this.state.error.message}</p>;
    return this.props.children;                           // normal case
  }
}

const cache = new Map();                                  // cache promises so they stay stable
function fetchOrders(userId) {
  if (!cache.has(userId)) {                               // create the promise only once per user
    cache.set(userId, new Promise((resolve) =>
      setTimeout(() => resolve([`Order A (${userId})`, `Order B (${userId})`]), 1000)
    ));
  }
  return cache.get(userId);                               // same promise for same input
}

function Orders({ userId }) {
  const orders = use(fetchOrders(userId));                // suspends until the promise resolves
  return <ul>{orders.map((o) => <li key={o}>{o}</li>)}</ul>; // render resolved data
}

function App() {
  const [userId, setUserId] = useState(1);                // which user's orders to show
  const [isPending, startTransition] = useTransition();   // marks the update as non-urgent
  return (
    <div>
      <button
        onClick={() => startTransition(() => setUserId((id) => id + 1))} // keep old list on screen
      >
        Next user {isPending ? '(loading...)' : ''}       {/* small inline hint instead of fallback */}
      </button>
      <ErrorBoundary>                                     {/* catches rejected promises */}
        <Suspense fallback={<p>Loading orders...</p>}>    {/* only for the very first load */}
          <Orders userId={userId} />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection

In the App Router, `loading.js` is just a Suspense boundary generated for the route segment. Async Server Components suspend naturally, so `await` in a component plus `<Suspense>` is the standard pattern. In Client Components you can pass a promise from a Server Component and read it with `use()`, which starts the fetch early on the server.

```jsx
// app/orders/page.jsx (Server Component): start fetch, do NOT await, pass the promise
import { Suspense } from 'react';
import OrderList from './OrderList';                       // Client Component

export default function Page() {
  const ordersPromise = getOrders();                       // hypothetical API, promise started on server
  return (
    <Suspense fallback={<p>Loading orders...</p>}>
      <OrderList ordersPromise={ordersPromise} />          {/* promises are serializable in React 19 */}
    </Suspense>
  );
}

// app/orders/OrderList.jsx
'use client';
import { use } from 'react';
export default function OrderList({ ordersPromise }) {
  const orders = use(ordersPromise);                       // suspends until the server promise resolves
  return <ul>{orders.map((o) => <li key={o.id}>{o.title}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the promise inside the component that calls `use()`
✅ **Correct:** Create/cache it outside or in a parent so it is stable across renders

```jsx
// Wrong: a NEW promise each render → suspends forever (infinite loop of fallback)
function Orders() {
  const data = use(fetch('/api/orders').then(r => r.json()));  // ❌ new promise every render
}

// Right: stable promise from a cache, loader or parent
function Orders({ ordersPromise }) { const data = use(ordersPromise); } // ✅
```

❌ **Mistake 2:** Expecting Suspense to catch data fetched inside `useEffect`
✅ **Correct:** Use a Suspense-enabled source (use(), lazy, Server Components, TanStack Query `useSuspenseQuery`)

```jsx
// Wrong: Suspense does nothing, the component rendered successfully with null data
<Suspense fallback={<Spinner />}><Profile /></Suspense>   // ❌ Profile fetches in useEffect

// Right
const { data } = useSuspenseQuery({ queryKey: ['user'], queryFn: getUser }); // ✅ (TanStack Query v5)
```

❌ **Mistake 3:** Forgetting an Error Boundary, so a rejected promise crashes the page
✅ **Correct:** Wrap Suspense in an Error Boundary (or use Next.js `error.js`)

```jsx
// Wrong: rejection bubbles to the root → blank screen
<Suspense fallback={<Spinner />}><Orders /></Suspense>
// Right
<ErrorBoundary fallback={<p>Failed</p>}><Suspense fallback={<Spinner />}><Orders /></Suspense></ErrorBoundary>
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [tab, setTab] = useState('a');
  return (
    <>
      <button onClick={() => setTab('b')}>Go B</button>
      <Suspense fallback={<p>Loading...</p>}>
        {tab === 'a' ? <TabA /> : <TabB />}   {/* TabB suspends */}
      </Suspense>
    </>
  );
}
```
**Answer:** Clicking "Go B" hides `TabA` and shows "Loading..." because the update is urgent (not a transition) and `TabB` suspends. The old content is hidden, not unmounted forever; its state would be kept if the boundary was already showing it (React hides it with `display: none`-like behavior while preserving state). To keep `TabA` visible until `TabB` is ready, wrap the update: `startTransition(() => setTab('b'))`. React then keeps the old UI and `isPending` is `true`. (Fallbacks already on screen are never replaced by a transition, but new fallbacks are avoided.)

---

## ⚫ Interview Questions + Answers

Q1: What is Suspense and what can trigger it?
A1: A component that lets you declare a loading UI for a part of the tree. It is triggered by `React.lazy`, `use(promise)`, async Server Components and Suspense-enabled data libraries. It is not triggered by `useEffect` fetching.

Q2: How is it different from an `isLoading` flag?
A2: With a flag, each component handles its own loading and must check it. With Suspense the component renders as if data exists, and the nearest boundary above decides the fallback, so loading UI is declarative and coordinated.

Q3: How do you avoid showing the fallback again when data changes?
A3: Mark the update with `startTransition` (or `useDeferredValue`). React keeps the old UI visible while the new one prepares and gives you `isPending`.

Q4: How does Suspense handle errors?
A4: It does not. A rejected promise throws during render, and the nearest Error Boundary catches it. Combine both: Error Boundary outside, Suspense inside.

Q5: What are Suspense waterfalls, and how do you avoid them?
A5: When nested components fetch one after another (parent finishes, then the child starts), total time adds up. Start fetches early (in a parent, loader, or on the server), fetch in parallel, and use multiple sibling boundaries.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Code splitting with `React.lazy` for heavy or rarely used UI
- Streaming server-rendered content (Next.js App Router)
- Coordinating loading UI across multiple async children

❌ **Avoid when:**
- You fetch in `useEffect` (it will not suspend, use a Suspense-ready tool first)
- A fallback would flash for very quick loads (use transitions)
- You have no Error Boundary and failures are likely

---

## 📊 Visual Diagram

```
 <ErrorBoundary>                    ← catches failures
   <Suspense fallback={<Skel/>}>    ← catches "waiting"
     <Header/>                       ← ready
     <Orders/>  ── use(promise) ──▶ PENDING → throws promise
   </Suspense>
 </ErrorBoundary>

 Timeline:
 render → Orders suspends → [Skel shown] → promise resolves → retry render → [Orders shown]
                                                  └─ rejects → [ErrorBoundary UI]
 With startTransition: old UI stays, no Skel flash, isPending = true
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Suspense | Boundary that shows fallback while waiting | इंतज़ार में fallback दिखाने वाली boundary |
| Suspend | Component pauses rendering until data is ready | Data तैयार होने तक render रोकना |
| Fallback | UI shown during waiting | इंतज़ार के दौरान दिखने वाला UI |
| `use()` | React 19 API to read a promise/context | Promise/context पढ़ने वाला React 19 API |
| `React.lazy` | Load a component's code on demand | Component का code ज़रूरत पर load करना |
| Error Boundary | Class component catching render errors | Render errors पकड़ने वाला class component |
| Transition | Non-urgent update that keeps old UI | पुराना UI रखने वाला non-urgent update |
| Waterfall | Sequential fetches that add up in time | एक के बाद एक fetch जिनका समय जुड़ता है |

---

## ⚡ 3-Line Summary
**English:**
1. Suspense shows a fallback while a child waits for code or data, and the child just renders normally.
2. Pair it with Error Boundaries for failures and transitions to avoid flashing fallbacks.
3. Keep promises stable and start fetches early to avoid waterfalls.

**Hindi:**
1. Suspense तब fallback दिखाता है जब child code या data का इंतज़ार करता है, और child सामान्य रूप से render करता है।
2. Failures के लिए Error Boundary और fallback की चमक रोकने के लिए transitions साथ में इस्तेमाल करो।
3. Promises को stable रखो और waterfalls से बचने के लिए fetch जल्दी शुरू करो।

---

## ➡️ Next Topic
**142. React Compiler (new)** — Compiler अपने आप memoization करता है, ताकि `useMemo`/`useCallback`/`memo` हाथ से लिखने की ज़रूरत कम हो जाए।
