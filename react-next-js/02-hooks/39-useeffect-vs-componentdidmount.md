# 39. useEffect vs componentDidMount
# हिंदी में: useEffect बनाम componentDidMount — Class और Hooks की तुलना

---

## 🔵 Simple Definition (English)
`componentDidMount`, `componentDidUpdate` and `componentWillUnmount` are class lifecycle methods that run at fixed moments. `useEffect` is one hook that replaces all three: it **synchronizes** your component with something outside React, and runs based on dependencies, not on lifecycle moments.

## 🔵 सरल परिभाषा (Hindi)
`componentDidMount`, `componentDidUpdate` और `componentWillUnmount` class के lifecycle methods हैं जो तय मौकों पर चलते हैं। `useEffect` एक hook है जो तीनों की जगह लेता है: यह component को React के बाहर की किसी चीज़ से **synchronize** करता है, और lifecycle के मौकों पर नहीं, dependencies पर चलता है।

---

## 🔴 Problem it Solves

In class components, related logic was split across methods. Starting a subscription went in `componentDidMount`, updating it in `componentDidUpdate`, and stopping it in `componentWillUnmount`. Developers forgot one of them, and bugs appeared (for example, not resubscribing when a prop changed). Unrelated logic (analytics + subscription) got mixed in the same method.

Hooks fix this: one `useEffect` holds setup and cleanup together, and you can have many effects, one per concern.

```jsx
// CLASS: one concern split in 3 places, easy to forget componentDidUpdate
class Chat extends React.Component {
  componentDidMount()  { connect(this.props.roomId); }
  componentDidUpdate(prev) { if (prev.roomId !== this.props.roomId) { disconnect(prev.roomId); connect(this.props.roomId); } }
  componentWillUnmount()   { disconnect(this.props.roomId); }
}

// HOOK: setup + cleanup + update in ONE place
function Chat({ roomId }) {
  useEffect(() => {
    connect(roomId);                  // setup
    return () => disconnect(roomId);  // cleanup (also runs before re-sync)
  }, [roomId]);                       // re-sync when roomId changes
}
```

## 🔴 यह क्यों बना? (Hindi)
Class components में जुड़ा हुआ logic अलग-अलग methods में बँट जाता था। Subscription शुरू करना `componentDidMount` में, update करना `componentDidUpdate` में और बंद करना `componentWillUnmount` में। Developers एक भूल जाते थे और bugs आते थे (जैसे prop बदलने पर दोबारा subscribe न होना)। असंबंधित logic (analytics + subscription) एक ही method में मिल जाता था।

Hooks इसे ठीक करते हैं: एक `useEffect` में setup और cleanup साथ रहते हैं, और आप कई effects रख सकते हैं, हर concern के लिए एक।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Class: React calls methods by TIME (after mount, after update, before unmount)
Step 2 → Hook: React calls the effect by DATA (dependencies changed or not)
Step 3 → useEffect(fn, [])        ≈ componentDidMount (+ cleanup ≈ componentWillUnmount)
Step 4 → useEffect(fn, [a])       ≈ didMount + didUpdate when a changed (+ cleanup before each re-run)
Step 5 → useEffect(fn) (no array) ≈ didMount + didUpdate on every render
Step 6 → Differences: effect runs AFTER paint (didMount runs before paint), and effect closures
         capture the values of their own render (class `this.props` is always latest)

MAPPING:
  componentDidMount      → useEffect(() => {...}, [])
  componentDidUpdate     → useEffect(() => {...}, [dep])   (also runs on mount)
  componentWillUnmount   → return () => {...} cleanup
  componentDidMount + Update (before paint, DOM measure) → useLayoutEffect
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Class: React methods को समय (TIME) के हिसाब से बुलाता है (mount के बाद, update के बाद, unmount से पहले)
Step 2 → Hook: React effect को data (DATA) के हिसाब से चलाता है (dependencies बदलीं या नहीं)
Step 3 → useEffect(fn, [])        ≈ componentDidMount (+ cleanup ≈ componentWillUnmount)
Step 4 → useEffect(fn, [a])       ≈ didMount + a बदलने पर didUpdate (+ हर re-run से पहले cleanup)
Step 5 → useEffect(fn) (array नहीं) ≈ हर render पर didMount + didUpdate
Step 6 → फ़र्क: effect paint के BAAD चलता है (didMount paint से पहले), और effect closures अपने
         render की values पकड़ते हैं (class में `this.props` हमेशा latest रहता है)

Mapping:
  componentDidMount      → useEffect(() => {...}, [])
  componentDidUpdate     → useEffect(() => {...}, [dep])   (mount पर भी चलता है)
  componentWillUnmount   → return () => {...} cleanup
  Paint से पहले DOM measure → useLayoutEffect
```

---

## 🟡 Real World Example
**Flipkart product page:** When the page for a product opens, it fetches the product, tracks a "product viewed" analytics event, and listens to `resize` for a responsive image gallery. In a class, those three jobs share `componentDidMount`, and when the user clicks a "similar product", `componentDidUpdate` must compare `prevProps.id` and repeat the fetch. With hooks, there are three small effects; the fetch effect has `[productId]`, so moving to a similar product refetches automatically.

## 🟡 Real Example Hindi mein
**Flipkart product page:** Product page खुलने पर वह product fetch करता है, "product viewed" analytics event भेजता है, और responsive image gallery के लिए `resize` सुनता है। Class में ये तीनों काम `componentDidMount` में मिलते हैं, और "similar product" पर क्लिक करने पर `componentDidUpdate` में `prevProps.id` की तुलना करके fetch दोहराना पड़ता है। Hooks में तीन छोटे effects होते हैं; fetch effect में `[productId]` है, इसलिए similar product पर जाते ही अपने आप refetch होता है।

---

## 💻 Code Example — Basic

```jsx
// The SAME behavior written as a class and as a function component
import React, { Component, useState, useEffect } from 'react'; // class + hooks
import { createRoot } from 'react-dom/client';                  // React 18/19 root API

// ---------- CLASS VERSION ----------
class TitleClass extends Component {
  state = { count: 0 };                                // class state
  componentDidMount() {
    document.title = `Count: ${this.state.count}`;     // runs once after first render
  }
  componentDidUpdate(prevProps, prevState) {
    if (prevState.count !== this.state.count) {        // manual comparison needed
      document.title = `Count: ${this.state.count}`;   // runs after every update
    }
  }
  componentWillUnmount() {
    document.title = 'App';                            // cleanup on unmount
  }
  render() {
    return <button onClick={() => this.setState(s => ({ count: s.count + 1 }))}>
      Class: {this.state.count}
    </button>;
  }
}

// ---------- HOOK VERSION ----------
function TitleHook() {
  const [count, setCount] = useState(0);               // function component state
  useEffect(() => {
    document.title = `Count: ${count}`;                // mount + every change of count
    return () => { document.title = 'App'; };          // cleanup before next run and on unmount
  }, [count]);                                         // dependency replaces the manual if-check
  return <button onClick={() => setCount(c => c + 1)}>Hook: {count}</button>;
}

createRoot(document.getElementById('root')).render(<><TitleClass /><TitleHook /></>);
```

## 💻 Code Example — Advanced

```jsx
// Class with three scattered methods vs one synchronizing effect, with real fetching
import React, { Component, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// ---------- CLASS: product page ----------
class ProductClass extends Component {
  state = { product: null, error: null };
  controller = null;                                   // keep the abort controller on the instance

  load(id) {
    this.controller?.abort();                          // cancel previous request
    this.controller = new AbortController();           // new controller for this request
    fetch(`/api/products/${id}`, { signal: this.controller.signal })
      .then(r => r.json())
      .then(product => this.setState({ product }))
      .catch(e => { if (e.name !== 'AbortError') this.setState({ error: e.message }); });
  }
  componentDidMount() { this.load(this.props.productId); }                 // first load
  componentDidUpdate(prev) {
    if (prev.productId !== this.props.productId) this.load(this.props.productId); // reload on change
  }
  componentWillUnmount() { this.controller?.abort(); }                     // cleanup
  render() {
    const { product, error } = this.state;
    if (error) return <p>{error}</p>;
    return product ? <h2>{product.title}</h2> : <p>Loading...</p>;
  }
}

// ---------- HOOK: same page, one effect ----------
function ProductHook({ productId }) {
  const [product, setProduct] = useState(null);        // data
  const [error, setError] = useState(null);            // error text

  useEffect(() => {
    const controller = new AbortController();          // per-run controller
    setProduct(null);                                  // show loading for the new product
    fetch(`/api/products/${productId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(setProduct)
      .catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => controller.abort();                   // cleanup replaces componentWillUnmount + the "cancel previous" code
  }, [productId]);                                     // replaces componentDidMount + componentDidUpdate

  if (error) return <p>{error}</p>;
  return product ? <h2>{product.title}</h2> : <p>Loading...</p>;
}

createRoot(document.getElementById('root')).render(<ProductHook productId="p1" />);
```

---

## 🟠 Next.js Connection

Class components cannot be Server Components, and they cannot use hooks. In the App Router, `componentDidMount`-style fetching mostly disappears: you fetch in an `async` Server Component, so there is no "after mount" step at all. `useEffect` is kept for browser-only work (listeners, analytics, widgets) inside `'use client'` files. Also, effects (and `componentDidMount`) never run during server rendering.

```jsx
// app/products/[id]/page.jsx (Server Component: replaces componentDidMount fetching)
import { getProduct } from '@/lib/products';             // your data layer (hypothetical helper)
import ViewTracker from './ViewTracker';

export default async function Page({ params }) {
  const { id } = await params;                           // Next.js 15+: params is a Promise
  const product = await getProduct(id);                  // runs on the server, no loading state needed
  return (
    <>
      <h1>{product.title}</h1>
      <ViewTracker id={id} />                            {/* browser-only side effect */}
    </>
  );
}
```

```jsx
// app/products/[id]/ViewTracker.jsx (Client Component: the legitimate use of useEffect)
'use client';
import { useEffect } from 'react';

export default function ViewTracker({ id }) {
  useEffect(() => {
    navigator.sendBeacon('/api/analytics', JSON.stringify({ event: 'view', id })); // browser API
  }, [id]);                                              // fire again when product changes
  return null;                                           // renders nothing
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking `useEffect(fn, [])` is exactly `componentDidMount`
✅ **Correct:** It runs after paint, and in StrictMode dev it runs twice. Use `useLayoutEffect` if you must run before paint

```jsx
// Wrong assumption: measuring DOM in useEffect may flash the wrong layout for one frame
useEffect(() => { setHeight(ref.current.offsetHeight); }, []);   // ❌ may flicker

// Right: before paint
useLayoutEffect(() => { setHeight(ref.current.offsetHeight); }, []); // ✅ no flicker
```

❌ **Mistake 2:** Skipping the dependency so it works only "on mount" while reading props
✅ **Correct:** List the props. Hooks make you handle updates, which class code often forgot

```jsx
// Wrong: roomId changes but we stay connected to the first room
useEffect(() => { connect(roomId); return () => disconnect(roomId); }, []); // ❌

// Right
useEffect(() => { connect(roomId); return () => disconnect(roomId); }, [roomId]); // ✅
```

❌ **Mistake 3:** Expecting `this.props` style "always latest" values inside async callbacks
✅ **Correct:** Effect callbacks see the values of their own render. Use a ref for "latest value" needs

```jsx
// Wrong expectation: alert shows the count at the time of the click, not later
useEffect(() => { setTimeout(() => alert(count), 3000); }, []);   // ❌ shows initial count

// Right when you really want the latest: store it in a ref
const latest = useRef(count);
useEffect(() => { latest.current = count; });                      // keep ref updated each render
useEffect(() => { const t = setTimeout(() => alert(latest.current), 3000); return () => clearTimeout(t); }, []); // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      console.log(count);
    }, 1000);
    return () => clearInterval(id);
  }, []);

  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```
**Answer:** It logs `0` every second forever, even after you click the button. The effect ran once with `[]`, so its closure captured `count = 0` from the first render. In a class, `console.log(this.state.count)` inside `setInterval` would print the latest value, because `this.state` is mutable. In hooks, either add `count` to the dependencies (interval restarts each time), or read from a ref.

---

## ⚫ Interview Questions + Answers

Q1: How do you map class lifecycle methods to `useEffect`?
A1: `componentDidMount` is an effect with `[]`; `componentDidUpdate` is an effect with dependencies (it also runs on mount); `componentWillUnmount` is the returned cleanup function.

Q2: Is `useEffect` the same as `componentDidMount`?
A2: No. `useEffect` runs after the browser paints (asynchronously), while `componentDidMount` runs synchronously after the DOM commit, before paint. For layout measuring, `useLayoutEffect` is the closer match. Also, `useEffect` is designed for synchronization, not lifecycle events.

Q3: Why was the hooks model introduced?
A3: To group related code (setup and cleanup together), split unrelated code into separate effects, avoid `this` binding confusion, and allow logic reuse via custom hooks instead of HOCs and render props.

Q4: How can an effect run only on updates and not on mount?
A4: There is no built-in option. Use a ref flag (`isFirst.current`) to skip the first run. Note that StrictMode double-run in development can make this tricky, so prefer designing the effect so it is safe to run on mount.

Q5: Does `componentDidMount` run on the server in SSR?
A5: No, neither `componentDidMount` nor `useEffect` runs during server rendering. They run only in the browser after hydration. That is why browser-only code is safe inside them.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useEffect` (function components) when:**
- You need to sync with external systems: network, subscriptions, DOM APIs, timers
- You are writing new code (class components are legacy, but still supported)
- You want to reuse the logic through a custom hook

❌ **Class lifecycle methods are needed only when:**
- You must write an Error Boundary (`componentDidCatch` / `getDerivedStateFromError` still need a class, version-dependent as of React 19)
- You maintain an old codebase and a rewrite is not worth it

---

## 📊 Visual Diagram

```
  CLASS (by time)                          HOOKS (by data)
  ┌──────────────────────┐                 ┌───────────────────────────────┐
  │ componentDidMount    │  connect        │ useEffect(() => {             │
  │ componentDidUpdate   │  reconnect      │    connect(roomId);           │
  │ componentWillUnmount │  disconnect     │    return () => disconnect(); │
  └──────────────────────┘                 │ }, [roomId]);                 │
   3 places, easy to miss one              └───────────────────────────────┘
                                            1 place: setup + cleanup + update

  Timing:  render → DOM commit → [componentDidMount / useLayoutEffect] → paint → [useEffect]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| componentDidMount | Runs once after first render (class) | पहले render के बाद एक बार चलता है |
| componentDidUpdate | Runs after each update (class) | हर update के बाद चलता है |
| componentWillUnmount | Runs before removal (class) | हटने से पहले चलता है |
| Synchronization | Keeping outside world matched to state | बाहरी दुनिया को state से मिलाए रखना |
| Closure | Function remembering its render values | अपने render की values याद रखने वाला function |
| useLayoutEffect | Effect before paint | Paint से पहले चलने वाला effect |
| Legacy | Old but still supported | पुराना पर अब भी supported |

---

## ⚡ 3-Line Summary
**English:**
1. `useEffect` replaces `componentDidMount`, `componentDidUpdate` and `componentWillUnmount` with one dependency-driven hook.
2. It runs after paint, captures values of its own render, and keeps setup and cleanup together.
3. Classes are still needed for Error Boundaries; Server Components remove most mount-time fetching.

**Hindi:**
1. `useEffect` तीनों lifecycle methods की जगह एक dependency-आधारित hook देता है।
2. यह paint के बाद चलता है, अपने render की values पकड़ता है, और setup व cleanup साथ रखता है।
3. Error Boundaries के लिए अब भी class चाहिए; Server Components mount-time fetching को काफ़ी हद तक हटा देते हैं।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — useEffect](https://react.dev/reference/react/useEffect) | Official reference |
| 📝 Article | [react.dev — Component (legacy)](https://react.dev/reference/react/Component) | Class lifecycle reference |

---

## ➡️ Next Topic
**40. useRef — Complete Guide** (already covered) और उसके बाद **41. useRef vs useState** — दोनों values याद रखते हैं, पर एक re-render कराता है और दूसरा नहीं। यह तुलना interviews में बहुत पूछी जाती है।
