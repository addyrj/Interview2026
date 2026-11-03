# 136. React 18 — New Features
# हिंदी में: React 18 — नए Features (Concurrent Rendering, Automatic Batching, Transitions)

---

## 🔵 Simple Definition (English)
**React 18** introduced **concurrent rendering**: React can pause, resume or drop a render so urgent work (typing, clicking) is never blocked by slow work (filtering a big list). Along with it came automatic batching, transitions, `Suspense` on the server, and new hooks like `useId` and `useDeferredValue`.

## 🔵 सरल परिभाषा (Hindi)
**React 18** ने **concurrent rendering** दी: React किसी render को रोक सकता है, दोबारा शुरू कर सकता है या छोड़ सकता है, ताकि ज़रूरी काम (typing, click) भारी काम (बड़ी list filter करना) से block न हो। साथ में automatic batching, transitions, server पर `Suspense`, और `useId`, `useDeferredValue` जैसे नए hooks भी आए।

---

## 🔴 Problem it Solves

Before React 18 a render was **synchronous and uninterruptible**. Once React started rendering a big tree, the browser main thread was stuck until it finished. Typing in a search box that filters 10,000 products felt laggy. Also, state updates inside `setTimeout`, promises or native event handlers were **not batched**, so each `setState` caused its own re-render.

```jsx
// PROBLEM (React 17): two setState calls in a promise = TWO renders
fetch('/api/cart').then(() => {
  setLoading(false);   // render #1
  setItems([]);        // render #2 (wasteful, and UI shows an inconsistent state in between)
});
```

## 🔴 यह क्यों बना? (Hindi)
React 18 से पहले render **synchronous था और बीच में रोका नहीं जा सकता था**। बड़ा tree render होते समय browser का main thread अटका रहता था। 10,000 products filter करने वाले search box में typing लैग करती थी। साथ ही `setTimeout`, promise या native event के अंदर के `setState` **batch नहीं होते थे**, इसलिए हर `setState` पर अलग render होता था।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Switch to createRoot (this opts you in to all React 18 features)
Step 2 → Updates get a PRIORITY: urgent (typing, click) vs transition (filtering, navigation)
Step 3 → startTransition / useTransition marks an update as non-urgent
Step 4 → React starts rendering the transition in the background and can INTERRUPT it
Step 5 → If a new urgent update arrives, React drops the old background render and restarts
Step 6 → Automatic batching: all setState calls in the same tick (any source) = ONE render
Step 7 → Suspense lets React show a fallback while a part of the tree waits (also on the server)

Re-render behavior: urgent update commits first; the transition render may run many times but
commits only once, with the final value.
Performance impact: input stays responsive; total work can be the same, but it is scheduled smartly.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createRoot इस्तेमाल करो (इसी से React 18 के सारे features चालू होते हैं)
Step 2 → हर update की PRIORITY होती है: urgent (typing, click) बनाम transition (filter, navigation)
Step 3 → startTransition / useTransition किसी update को non-urgent बताता है
Step 4 → React transition को background में render करता है और बीच में ROK सकता है
Step 5 → नया urgent update आए तो React पुराना background render छोड़कर दोबारा शुरू करता है
Step 6 → Automatic batching: एक ही tick के सारे setState (किसी भी source से) = सिर्फ एक render
Step 7 → Suspense से किसी हिस्से के इंतज़ार में fallback दिखता है (server पर भी)

Re-render behavior: urgent update पहले commit होता है; transition का render कई बार चल सकता है
पर commit सिर्फ एक बार, final value के साथ।
Performance impact: input responsive रहता है; कुल काम वही हो सकता है, पर schedule समझदारी से होता है।
```

---

## 🟡 Real World Example
**Flipkart search:** You type "mobile" in the search box. The input text must update instantly, while the list of 5,000 matching products can take a moment. With `useTransition`, the typed text is an urgent update and the list filtering is a transition. If you keep typing, React throws away the half-finished list render and starts again with the new text, so the box never freezes. Also, when the product API returns, `setLoading(false)` and `setProducts(data)` are batched into one render, so the page never flashes an empty list.

## 🟡 Real Example Hindi mein
**Flipkart search:** आप search box में "mobile" लिखते हैं। टाइप किया हुआ text तुरंत दिखना चाहिए, जबकि 5,000 matching products की list थोड़ी देर ले सकती है। `useTransition` में typed text urgent update है और list filtering transition। आप टाइप करते रहें तो React अधूरा list render छोड़कर नए text से दोबारा शुरू करता है, इसलिए box कभी freeze नहीं होता। और API का जवाब आने पर `setLoading(false)` व `setProducts(data)` एक ही render में batch होते हैं, इसलिए page पर खाली list की झलक नहीं दिखती।

---

## 💻 Code Example — Basic

```jsx
// Basic: createRoot + automatic batching + useId
import { useState, useId } from 'react';              // hooks from React 18
import { createRoot } from 'react-dom/client';        // NEW root API (replaces ReactDOM.render)

function Counter() {
  const [count, setCount] = useState(0);              // first state
  const [flag, setFlag] = useState(false);            // second state
  const id = useId();                                 // stable unique id, same on server and client
  console.log('render');                              // watch how many times this prints

  function handleClick() {
    setTimeout(() => {                                // async callback: NOT batched in React 17
      setCount((c) => c + 1);                         // queued
      setFlag((f) => !f);                             // queued, both -> ONE render in React 18
    }, 0);
  }

  return (
    <div>
      <label htmlFor={id}>Quantity</label>            {/* id links label and input */}
      <input id={id} value={count} readOnly />        {/* read-only display of count */}
      <button onClick={handleClick}>Add</button>      {/* triggers the batched updates */}
      <p>{flag ? 'ON' : 'OFF'}</p>                    {/* second state shown */}
    </div>
  );
}

const root = createRoot(document.getElementById('root')); // create the concurrent root
root.render(<Counter />);                                  // mount the app
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Flipkart-style search with useTransition and useDeferredValue
import { useState, useTransition, useDeferredValue, memo, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

// 5,000 fake products to make filtering expensive
const PRODUCTS = Array.from({ length: 5000 }, (_, i) => ({ id: i, name: `Mobile phone model ${i}` }));

// memo: skip re-render when the list prop is unchanged (same reference)
const ProductList = memo(function ProductList({ items }) {
  console.log('ProductList render', items.length);          // see when the heavy list renders
  return (
    <ul>
      {items.slice(0, 200).map((p) => <li key={p.id}>{p.name}</li>)} {/* cap DOM size */}
    </ul>
  );
});

function SearchWithTransition() {
  const [text, setText] = useState('');                    // urgent state: what the user typed
  const [query, setQuery] = useState('');                  // non-urgent state: used for filtering
  const [isPending, startTransition] = useTransition();    // isPending = transition still running

  const results = useMemo(                                  // recompute only when query changes
    () => PRODUCTS.filter((p) => p.name.includes(query)),
    [query]
  );

  function onChange(e) {
    setText(e.target.value);                               // urgent: input updates immediately
    startTransition(() => {                                // everything inside is low priority
      setQuery(e.target.value);                            // list update can be interrupted
    });
  }

  return (
    <div>
      <input value={text} onChange={onChange} placeholder="Search phones" />
      {isPending && <span> Updating...</span>}              {/* feedback while transition runs */}
      <ProductList items={results} />
    </div>
  );
}

// Alternative: useDeferredValue when you do not own the setState (value comes from props)
function SearchDeferred() {
  const [text, setText] = useState('');                    // urgent value
  const deferred = useDeferredValue(text);                 // lags behind; updates when React is idle
  const results = useMemo(() => PRODUCTS.filter((p) => p.name.includes(deferred)), [deferred]);
  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ opacity: text !== deferred ? 0.5 : 1 }}>   {/* dim stale results */}
        <ProductList items={results} />
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<><SearchWithTransition /><SearchDeferred /></>);
```

---

## 🟠 Next.js Connection

Next.js App Router (13.4+) is built on React 18 features: Suspense streaming, transitions for navigation (`router.push` is wrapped in a transition), and Server Components all depend on React 18 features. You rarely call `createRoot` yourself because Next.js does it.

```jsx
// app/search/page.jsx (Client Component because it uses hooks)
'use client';                                              // required for useState / useTransition
import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';               // App Router navigation hook

export default function SearchBox() {
  const router = useRouter();                              // router instance
  const [text, setText] = useState('');                    // controlled input
  const [isPending, startTransition] = useTransition();    // track navigation as a transition

  function onChange(e) {
    setText(e.target.value);                               // input stays instant
    startTransition(() => {                                // URL change + server render is non-urgent
      router.replace(`/search?q=${encodeURIComponent(e.target.value)}`);
    });
  }

  return (
    <>
      <input value={text} onChange={onChange} />
      {isPending && <p>Loading results...</p>}              {/* shown until server data arrives */}
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Still using `ReactDOM.render` (React 18 runs in legacy mode and loses concurrent features)
✅ **Correct:** Use `createRoot`

```jsx
// Wrong: legacy root, removed in React 19
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));   // ❌

// Right
import { createRoot } from 'react-dom/client';
createRoot(document.getElementById('root')).render(<App />); // ✅
```

❌ **Mistake 2:** Putting a controlled input's own `setState` inside `startTransition`
✅ **Correct:** Keep the input urgent, wrap only the expensive update

```jsx
// Wrong: the text itself becomes low priority, so typing feels laggy
startTransition(() => { setText(e.target.value); setQuery(e.target.value); }); // ❌

// Right
setText(e.target.value);                                    // ✅ urgent
startTransition(() => setQuery(e.target.value));            // ✅ non-urgent
```

❌ **Mistake 3:** Putting async work (await) inside `startTransition` callback and expecting updates after the await to be transitions
✅ **Correct:** In React 18 only updates called synchronously inside are marked (React 19 supports async actions)

```jsx
// Wrong (React 18): setState after await is a normal urgent update
startTransition(async () => { await save(); setDone(true); }); // ❌ not supported in 18

// Right (React 18): wrap the state update after the await again
await save();
startTransition(() => setDone(true));                       // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';
import { flushSync } from 'react-dom';

function App() {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  console.log('render', a, b);

  function handle() {
    setA(1);                       // queued
    flushSync(() => setB(1));      // forces a synchronous render right now
  }
  return <button onClick={handle}>go</button>;
}
```
**Answer:** After the initial `render 0 0`, the click logs `render 1 1` once (StrictMode in dev may double the logs). `flushSync` flushes all pending updates synchronously, including the earlier `setA(1)`, so both states are applied in one render. `flushSync` is the escape hatch from automatic batching; use it rarely (for example to read DOM layout immediately after a state change) because it hurts performance.

---

## ⚫ Interview Questions + Answers

Q1: What is concurrent rendering?
A1: A React 18 capability where rendering can be interrupted, paused and resumed. React can prepare a new UI in the background while keeping the current UI responsive. It is opt-in through `createRoot` and features like `useTransition`; it is not a separate mode you "turn on" everywhere.

Q2: What is automatic batching?
A2: React groups multiple state updates into one re-render, regardless of where they come from (event handlers, timeouts, promises, native events). Before React 18 only updates inside React event handlers were batched. Use `flushSync` to opt out.

Q3: Difference between `useTransition` and `useDeferredValue`?
A3: `useTransition` wraps the **state update** (you control the setter) and gives `isPending`. `useDeferredValue` wraps a **value** (useful when it arrives from props) and returns a lagging copy. Both mark the dependent render as low priority. Neither debounces: they have no fixed delay, and the work still runs.

Q4: What changed with Suspense in React 18?
A4: Suspense works with streaming SSR and selective hydration. The server can send HTML in chunks, and the client can hydrate parts independently, prioritising the part the user interacts with. Suspense for data fetching is supported through frameworks and libraries (`use` in React 19).

Q5: What breaking changes did React 18 bring?
A5: `createRoot` replaces `ReactDOM.render` (`hydrateRoot` replaces `hydrate`), stricter StrictMode in development (mount, unmount, mount again to surface effect bugs), no more automatic `children` in `React.FC` types, and effects flushed synchronously when caused by discrete events like a click.

---

## 🔷 When to Use + When Not to Use
✅ **Use transitions / deferred values when:**
- A state change triggers an expensive render (large list, chart, tabs with heavy content)
- You want to keep typing, clicking and scrolling responsive
- You navigate between routes and want to keep the old UI visible

❌ **Avoid when:**
- The update is cheap (extra complexity, no benefit)
- You need the result immediately, such as a controlled input value
- The slowness is from network or an expensive calculation that can be memoised or moved to a worker

---

## 📊 Visual Diagram

```
 React 17 (sync):  type 'm' ─► [====== render 5000 items ======] ─► input updates (LAG)

 React 18:
   urgent    : type 'm' ─► [render input] ─► commit (instant)
   transition:             [render list ....] ─ interrupted by next key ─► restart
                                              [render list ........] ─► commit once

 Batching:
   setA(); setB(); setC();   (inside promise)
        └────────┬────────┘
           ONE re-render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Concurrent rendering | Render that can pause/resume/abort | रुकने व चलने वाला render |
| createRoot | New root API for React 18 | React 18 का नया root API |
| Automatic batching | Group updates into one render | अपडेट्स को एक render में जोड़ना |
| Transition | Low priority state update | कम प्राथमिकता का update |
| useDeferredValue | Lagging copy of a value | देर से बदलने वाली value |
| flushSync | Force synchronous render | तुरंत render करवाना |
| Selective hydration | Hydrate parts by priority | ज़रूरत के हिसाब से hydrate करना |
| useId | Stable unique id for SSR | SSR-सुरक्षित unique id |

---

## ⚡ 3-Line Summary
**English:**
1. React 18 adds concurrent rendering: interruptible renders with priorities.
2. Automatic batching, `useTransition`, `useDeferredValue` and `useId` make apps smoother with little code.
3. Use `createRoot`; keep urgent updates urgent and wrap only expensive updates in transitions.

**Hindi:**
1. React 18 concurrent rendering देता है: रुकने वाले renders और priorities।
2. Automatic batching, `useTransition`, `useDeferredValue` और `useId` थोड़े code में app को smooth बनाते हैं।
3. `createRoot` इस्तेमाल करो; urgent update को urgent रखो और सिर्फ भारी update को transition में डालो।

---

## ➡️ Next Topic
**137. React 19 — New Features** — Actions, `use`, `useActionState`, `useOptimistic`, ref as a prop. React 19 builds directly on the concurrent foundation you just learned.
