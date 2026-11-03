# 131. Code Splitting + lazy()
# हिंदी में: Code Splitting और lazy() — जो चाहिए सिर्फ़ वही, तभी load करना

---

## 🔵 Simple Definition (English)
**Code splitting** breaks your JavaScript into smaller chunks that load on demand. In React, `React.lazy(() => import('./Page'))` loads a component's code only when it is first rendered, and `<Suspense>` shows a fallback while the chunk downloads.

## 🔵 सरल परिभाषा (Hindi)
**Code splitting** आपके JavaScript को छोटे chunks में तोड़ता है जो ज़रूरत पर load होते हैं। React में `React.lazy(() => import('./Page'))` component का code तब load करता है जब वह पहली बार render होता है, और `<Suspense>` chunk download होने तक fallback दिखाता है।

---

## 🔴 Problem it Solves

A single bundle contains every page and feature. A user opening the login page downloads the admin dashboard, the chart library and the checkout flow too. That slows the first load for no reason.

```jsx
// PROBLEM: all pages in one bundle
import Home from './Home';
import Admin from './Admin';                            // heavy, needed by 2% of users
import Checkout from './Checkout';

// SOLUTION: load a page only when it is needed
const Admin = lazy(() => import('./Admin'));            // separate chunk, fetched on first render
```

## 🔴 यह क्यों बना? (Hindi)
एक ही bundle में हर page और feature होता है। Login page खोलने वाला user admin dashboard, chart library और checkout flow भी download कर लेता है। इससे पहला load बेवजह धीमा होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `import('./Admin')` (dynamic import) tells the bundler: make a separate chunk
Step 2 → React.lazy wraps it: the component is "not ready" until the promise resolves
Step 3 → On first render, lazy starts the download and SUSPENDS (throws the promise internally)
Step 4 → The nearest <Suspense> boundary above shows its fallback
Step 5 → When the chunk arrives, React re-renders and shows the real component
Step 6 → The chunk is cached; later renders are instant

KEY: lazy needs a default export, and a <Suspense> above it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `import('./Admin')` (dynamic import) bundler को बताता है: अलग chunk बनाओ
Step 2 → React.lazy इसे wrap करता है: promise resolve होने तक component "ready नहीं" होता
Step 3 → पहले render पर lazy download शुरू करता है और SUSPEND होता है (अंदर promise throw होता है)
Step 4 → ऊपर का सबसे नज़दीकी <Suspense> अपना fallback दिखाता है
Step 5 → Chunk आने पर React दोबारा render करके असली component दिखाता है
Step 6 → Chunk cache हो जाता है; आगे के renders तुरंत होते हैं

KEY: lazy को default export और ऊपर <Suspense> चाहिए
```

---

## 🟡 Real World Example
**Zomato web:** The home page and restaurant listing are what 95% of visitors need. Rarely used areas, such as "Help and Support", "Gold membership" and the "Partner with us" form, are separate chunks. A new visitor downloads only the home route. Tapping "Help" fetches that chunk (a few KB) at that moment, while a skeleton loader shows for a split second. Many apps also prefetch the next likely route when the user hovers a link.

## 🟡 Real Example Hindi mein
**Zomato web:** 95% visitors को home page और restaurant listing चाहिए। कम इस्तेमाल वाले हिस्से, जैसे "Help and Support", "Gold membership" और "Partner with us" form, अलग chunks हैं। नया visitor सिर्फ़ home route download करता है। "Help" पर tap करने पर उसी समय वह chunk (कुछ KB) आता है, और एक पल के लिए skeleton loader दिखता है। कई apps user के link पर hover करते ही अगला संभावित route prefetch भी कर लेते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: lazy-load one heavy component behind a button
import { lazy, Suspense, useState } from 'react';       // lazy, Suspense and state
import { createRoot } from 'react-dom/client';          // React 18/19 root API

// The import() call is NOT executed until <Reviews /> is first rendered
const Reviews = lazy(() => import('./Reviews'));        // Reviews.jsx must `export default`

function Product() {
  const [open, setOpen] = useState(false);              // are reviews visible?

  return (
    <div>
      <h1>Wireless Earbuds</h1>
      <button onClick={() => setOpen(o => !o)}>        {/* toggle reviews */}
        {open ? 'Hide' : 'Show'} reviews
      </button>

      {open && (                                        // chunk requested the first time this is true
        <Suspense fallback={<p>Loading reviews...</p>}> {/* shown while the chunk downloads */}
          <Reviews />                                   {/* real component after load */}
        </Suspense>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Product />);
```

```jsx
// Reviews.jsx: a default export is required for React.lazy
export default function Reviews() {
  return <ul><li>Great sound</li><li>Good battery</li></ul>; // simple content for the demo
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: route-level splitting + hover prefetch + error boundary for failed chunks
import { lazy, Suspense, useState, Component } from 'react'; // React APIs
import { createRoot } from 'react-dom/client';                // root API

// Keep the loader functions so we can also call them early to prefetch
const loadOrders = () => import('./pages/Orders');           // function returning a promise
const loadProfile = () => import('./pages/Profile');
const Orders = lazy(loadOrders);                              // lazy uses the same loader
const Profile = lazy(loadProfile);

const pages = { orders: Orders, profile: Profile };           // map of route → component
const loaders = { orders: loadOrders, profile: loadProfile }; // map of route → prefetch function

// Error boundary: a chunk can fail to load (offline, deploy changed file names)
class ChunkErrorBoundary extends Component {
  state = { failed: false };                                  // did a chunk fail?
  static getDerivedStateFromError() { return { failed: true }; } // switch to fallback UI
  render() {
    if (this.state.failed) {
      return <button onClick={() => location.reload()}>Reload page</button>; // simple recovery
    }
    return this.props.children;                               // normal case
  }
}

function App() {
  const [route, setRoute] = useState('orders');               // current route (no router for brevity)
  const Page = pages[route];                                  // component for this route

  return (
    <div>
      <nav>
        {Object.keys(pages).map(name => (
          <button
            key={name}
            onMouseEnter={() => loaders[name]()}              // prefetch the chunk on hover (cached by the browser)
            onClick={() => setRoute(name)}                    // navigate
          >
            {name}
          </button>
        ))}
      </nav>

      <ChunkErrorBoundary>                                    {/* catches chunk load errors */}
        <Suspense fallback={<p>Loading page...</p>}>          {/* shown while the chunk loads */}
          <Page />                                            {/* lazy page */}
        </Suspense>
      </ChunkErrorBoundary>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Real App Integration

In the Next.js App Router, every route segment (`page.js`) is already its own chunk, so route-level splitting is automatic. Use `next/dynamic` for components inside a page. It wraps `React.lazy` and `Suspense`, and also supports `ssr: false` (only in Client Components).

```jsx
// app/product/[id]/Gallery.jsx
'use client';                                            // ssr:false is allowed only in a Client Component
import dynamic from 'next/dynamic';                      // Next.js dynamic import helper

const Zoom = dynamic(() => import('./ImageZoom'), {      // separate chunk
  ssr: false,                                            // zoom uses window/mouse events, skip server render
  loading: () => <p>Loading zoom...</p>,                 // fallback while loading
});

export default function Gallery({ src }) {
  return (
    <div>
      <img src={src} alt="Product" width={300} />        {/* instant content */}
      <Zoom src={src} />                                 {/* heavy feature loads on demand */}
    </div>
  );
}
```

```jsx
// A Server Component can also use dynamic() to split a Client Component (without ssr:false)
// app/page.jsx
import dynamic from 'next/dynamic';
const Chat = dynamic(() => import('./ChatWidget'));       // ChatWidget has 'use client' inside
export default function Home() { return <Chat />; }      // chunk is split from the main bundle
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `lazy()` inside a component
✅ **Correct:** Call `lazy()` at module level

```jsx
// Wrong: a new lazy component type each render → state lost, chunk reloaded, flicker
function App() {
  const Admin = lazy(() => import('./Admin'));          // ❌ created on every render
  return <Suspense fallback="..."><Admin /></Suspense>;
}

// Right: created once
const Admin = lazy(() => import('./Admin'));            // ✅ module level
function App2() {
  return <Suspense fallback="..."><Admin /></Suspense>;
}
```

❌ **Mistake 2:** No `<Suspense>` boundary above a lazy component
✅ **Correct:** Wrap lazy components in `<Suspense fallback={...}>`

```jsx
// Wrong: React throws "A React component suspended while rendering, but no fallback UI was specified" (React 18)
<Admin />                                               // ❌

// Right
<Suspense fallback={<Spinner />}><Admin /></Suspense>   // ✅
```

❌ **Mistake 3:** Lazy-loading a named export or a tiny component
✅ **Correct:** Map the named export to `default`, and only split meaningful chunks

```jsx
// Wrong: lazy expects { default: Component }
const Chart = lazy(() => import('./charts'));           // ❌ charts exports { Chart } (no default)

// Right: adapt the named export
const Chart2 = lazy(() => import('./charts').then(m => ({ default: m.Chart }))); // ✅
// Also avoid splitting a 1 KB component: the extra request costs more than it saves
```

---

## 🧠 Tricky Interview Question

```jsx
import { lazy, Suspense, useState } from 'react';

const Panel = lazy(() => {
  console.log('loading chunk');
  return import('./Panel');
});

function App() {
  const [show, setShow] = useState(false);
  console.log('App render');
  return (
    <div>
      <button onClick={() => setShow(true)}>Open</button>
      <Suspense fallback={<p>Loading</p>}>
        {show && <Panel />}
      </Suspense>
    </div>
  );
}
// Question: when does 'loading chunk' print, and how many times if the user clicks Open, closes it, and opens it again?
```
**Answer:** The loader function inside `lazy` runs the first time React tries to render `<Panel />`, not when `lazy()` is called and not when the module is imported. So the log prints only after the first click on Open, and exactly once: `React.lazy` caches the result of the first promise, so later opens render the cached component with no new request. Output sequence: `App render` (initial), then after the click `App render` and `loading chunk`, then the fallback shows until the chunk resolves. Closing and reopening never prints `loading chunk` again.

---

## ⚫ Interview Questions + Answers

Q1: What is code splitting and how does React support it?
A1: Splitting the bundle into chunks loaded on demand. React supports it with `React.lazy` (wraps a dynamic `import()`) and `Suspense` (fallback while loading). Bundlers (webpack, Vite, Turbopack) create the chunks from the `import()` calls.

Q2: Where should you split code first?
A2: At route level, since users see one route at a time. After that, split heavy features that are conditional: modals, editors, charts, maps, admin tools.

Q3: What happens if a lazy chunk fails to load?
A3: The promise rejects and React throws the error during render. Use an error boundary around the Suspense boundary to show a retry button or reload the page. Failures often happen after a new deployment changes file names, or when the user is offline.

Q4: Does `React.lazy` work with server-side rendering?
A4: In React 18+ with streaming SSR, lazy components inside Suspense can render on the server and hydrate selectively. In Next.js use `next/dynamic` (which also offers `ssr: false`). In older React (17), `lazy` did not support SSR.

Q5: How can you avoid the loading flash for lazy routes?
A5: Prefetch the chunk before it is needed: on link hover or focus, on idle time, or with `<link rel="prefetch">`. Wrapping the navigation in `startTransition` also keeps the old UI visible instead of showing the fallback.

---

## 🔷 When to Use + When Not to Use
✅ **Use code splitting when:**
- You have multiple routes or pages
- A feature is heavy and used by a minority of users (charts, rich text editor, PDF viewer)
- The initial bundle is large and slows first load

❌ **Avoid when:**
- The component is tiny or needed on every page (an extra request is slower)
- It is above the fold, needed right away (it would delay the first paint)
- You cannot provide a meaningful fallback and the flash would hurt UX

---

## 📊 Visual Diagram

```
  Without splitting:   [ main.js: Home + Orders + Profile + Admin + Charts ]  1.2 MB → first paint waits

  With splitting:
     initial load  ──▶ [ main.js: Home + React ]  250 KB   → fast first paint
                              │
        click "Orders" ───────┼─▶ [ orders.chunk.js ]  40 KB   (Suspense fallback shows, then Orders)
        click "Admin"  ───────┴─▶ [ admin.chunk.js  ] 300 KB   (only admins ever pay this cost)

  Render flow of a lazy component:
  render <Orders/> ─▶ chunk not loaded ─▶ suspend ─▶ nearest <Suspense> shows fallback
                                         └─ chunk arrives ─▶ re-render ─▶ <Orders/> appears
```

Re-render behavior: the lazy component suspends on first render, so React shows the fallback and retries when the module loads. Afterwards it behaves like a normal component. Performance impact: smaller initial JS (faster first paint and interactivity) at the cost of a small extra request later.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code splitting | Breaking the bundle into on-demand chunks | Bundle को on-demand chunks में तोड़ना |
| Dynamic import | `import()` that returns a promise | Promise लौटाने वाला `import()` |
| React.lazy | Wraps a dynamic import as a component | Dynamic import को component बनाना |
| Suspense | Shows a fallback while something loads | Load होने तक fallback दिखाना |
| Chunk | A separately loaded JS file | अलग से load होने वाली JS file |
| Prefetch | Load a chunk early, before it is needed | Chunk को ज़रूरत से पहले load करना |
| Error boundary | Catches render errors, including chunk failures | Render errors पकड़ने वाला component |
| next/dynamic | Next.js helper over lazy + Suspense | lazy + Suspense पर Next.js helper |

---

## ⚡ 3-Line Summary
**English:**
1. Code splitting loads code on demand; `React.lazy(() => import(...))` plus `<Suspense>` is the React way.
2. Split by route first, then by heavy conditional features; declare `lazy` at module level and add an error boundary.
3. Next.js splits per route automatically and offers `next/dynamic` for components (and `ssr: false` in Client Components).

**Hindi:**
1. Code splitting code को ज़रूरत पर load करता है; React में तरीका है `React.lazy(() => import(...))` और `<Suspense>`।
2. पहले route के हिसाब से split करो, फिर भारी conditional features को; `lazy` को module level पर रखो और error boundary लगाओ।
3. Next.js हर route को अपने आप split करता है और components के लिए `next/dynamic` देता है (और Client Components में `ssr: false`)।

---

## ➡️ Next Topic
**132. Suspense for Data Fetching** — Suspense सिर्फ़ code के लिए नहीं, data के लिए भी है। loading states को declarative तरीके से कैसे संभालें, `use()` hook और streaming SSR।
