# 90. Lazy Loading Routes
# हिंदी में: Lazy Loading Routes — जरूरत पड़ने पर ही page का code load करना

---

## 🔵 Simple Definition (English)
Lazy loading routes means each page's JavaScript is split into its own file (chunk) and downloaded only when the user visits that route. Use `React.lazy()` with `<Suspense>` to show a fallback while the chunk loads.

## 🔵 सरल परिभाषा (Hindi)
Lazy loading routes का मतलब है कि हर page का JavaScript अलग file (chunk) में बँटता है और सिर्फ तब download होता है जब user उस route पर जाता है। `React.lazy()` और `<Suspense>` से chunk load होते समय fallback दिखाया जाता है।

---

## 🔴 Problem it Solves
A single bundle for a big app can be 2–5 MB. Every visitor downloads the admin dashboard code, the checkout code, and the settings code, even if they only open the home page. On a slow 4G network in a Tier-2 city, that means a blank screen for many seconds. Splitting by route means the first load only contains the code for the current page, and the rest arrives when it is needed.

## 🔴 यह क्यों बना? (Hindi)
एक बड़ी app का single bundle 2–5 MB तक हो सकता है। हर visitor को admin dashboard, checkout और settings का code download करना पड़ता है, भले ही वह सिर्फ home page खोले। धीमे 4G पर इसका मतलब कई सेकंड की blank screen। Route के हिसाब से split करने पर पहली load में सिर्फ current page का code आता है, बाकी जरूरत पड़ने पर।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Replace static import with lazy import:
         const Orders = lazy(() => import('./pages/Orders'));

Step 2 → Bundler (Vite, webpack, Next.js) creates a separate chunk file
         for './pages/Orders' — it is NOT in the main bundle

Step 3 → User opens /orders → React renders <Orders />
         The chunk is not downloaded yet → React "suspends"

Step 4 → The nearest <Suspense fallback={...}> shows the fallback (spinner)

Step 5 → Chunk arrives → React renders the real page and removes the fallback

KEY: lazy() must be called ONCE, at module level. Suspense must wrap lazy components.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Static import की जगह lazy import लिखो: lazy(() => import('./pages/Orders'))
Step 2 → Bundler हर lazy import के लिए अलग chunk file बनाता है
Step 3 → User /orders खोलता है → chunk अभी download नहीं हुआ → React suspend करता है
Step 4 → नजदीकी <Suspense fallback> spinner दिखाता है
Step 5 → Chunk आते ही असली page render होता है और fallback हट जाता है
KEY: lazy() module level पर सिर्फ एक बार लिखो। Suspense lazy components को wrap करे।
```

---

## 🟡 Real World Example
**Flipkart / Amazon web app:** The home page loads fast because the checkout, seller-dashboard and order-history code are separate chunks. When you tap "Place order", only the checkout chunk is fetched. A seller logging into the same site downloads the seller dashboard chunk and never touches the shopper's code. Mobile users in areas with weak signal see the product page first instead of a blank white screen.

## 🟡 Real Example Hindi mein
**Flipkart / Amazon web app:** Home page जल्दी खुलता है क्योंकि checkout, seller-dashboard और order-history का code अलग chunks में है। "Place order" दबाने पर सिर्फ checkout chunk आता है। Seller उसी site पर login करे तो उसे seller dashboard chunk मिलता है, shopper का code नहीं। कमजोर signal वाले mobile users को सफेद screen की जगह पहले product page दिखता है।

---

## 💻 Code Example — Basic

```jsx
// lazy and Suspense come from React itself
import { lazy, Suspense } from 'react';
// Router pieces from react-router-dom v6
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// Home is loaded eagerly: it is the first page, so it belongs in the main bundle
import Home from './pages/Home';

// lazy() receives a function that returns import(); each import() becomes its own chunk
const Orders = lazy(() => import('./pages/Orders'));
// Same for the admin page, which only a few users open
const Admin = lazy(() => import('./pages/Admin'));

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        {/* Links are normal; clicking them triggers the lazy chunk download */}
        <Link to="/">Home</Link> | <Link to="/orders">Orders</Link> | <Link to="/admin">Admin</Link>
      </nav>

      {/* Suspense shows fallback while ANY lazy child inside it is still loading */}
      <Suspense fallback={<p>Loading page...</p>}>
        <Routes>
          <Route path="/" element={<Home />} />          {/* no suspense needed: eager */}
          <Route path="/orders" element={<Orders />} />  {/* chunk downloaded on visit */}
          <Route path="/admin" element={<Admin />} />    {/* chunk downloaded on visit */}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { lazy, Suspense, Component } from 'react';
import { BrowserRouter, Routes, Route, Outlet, useLocation } from 'react-router-dom';

// ── Retry wrapper: fixes "ChunkLoadError" after a new deploy ──
// After a deploy, old chunk file names no longer exist on the server.
// A user with an old tab open gets a 404 for the chunk. Retrying once helps,
// and if it still fails we reload the page to fetch the new index.html.
function lazyWithRetry(importFn) {
  return lazy(async () => {
    try {
      return await importFn();                 // first attempt
    } catch (firstError) {                     // network or 404 error
      await new Promise((r) => setTimeout(r, 500)); // short pause before retry
      try {
        return await importFn();               // second attempt
      } catch (secondError) {
        // Reload only once per session to avoid an infinite reload loop
        if (!sessionStorage.getItem('chunk-reloaded')) {
          sessionStorage.setItem('chunk-reloaded', '1');
          window.location.reload();            // fetch fresh index.html
        }
        throw secondError;                     // let the error boundary show a message
      }
    }
  });
}

// Each page is lazy and retry-safe
const Dashboard = lazyWithRetry(() => import('./pages/Dashboard'));
const Reports = lazyWithRetry(() => import('./pages/Reports'));

// Preload helper: start downloading a chunk before the user clicks (e.g. on hover)
const preloadReports = () => import('./pages/Reports');

// Error boundary: class component, the only way to catch render errors in React
class ChunkErrorBoundary extends Component {
  state = { hasError: false };                 // local error flag
  static getDerivedStateFromError() {          // called when a child throws
    return { hasError: true };                 // switch to the error UI
  }
  render() {
    if (this.state.hasError) {                 // show a friendly message
      return <p>Could not load this page. Please refresh.</p>;
    }
    return this.props.children;                // normal rendering
  }
}

// Layout route: keeps the navigation visible while pages swap
function Layout() {
  const location = useLocation();              // current URL object
  return (
    <main>
      <p>You are on: {location.pathname}</p>   {/* shows the current path */}
      {/* Boundary + Suspense inside the layout: a crash only replaces the page area */}
      <ChunkErrorBoundary>
        <Suspense fallback={<p>Loading…</p>}>
          <Outlet />                           {/* the matched child page renders here */}
        </Suspense>
      </ChunkErrorBoundary>
    </main>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Layout route has no path of its own, it only wraps children */}
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/reports"
            element={<Reports />}
            // Note: preloadReports() can be called from a Link's onMouseEnter
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

// Export so a Link can call it on hover: <Link onMouseEnter={preloadReports} to="/reports">
export { preloadReports };
```

---

## 🟠 Real App Integration (React + Next.js)

In a Vite or Create React App-style SPA, the code above is how you split routes. **Next.js App Router** already splits every route segment into its own chunk, so you do not write `lazy()` for pages. Use `next/dynamic` for heavy components inside a page, such as a chart library:

```jsx
'use client'; // dynamic with ssr:false must live in a Client Component
import dynamic from 'next/dynamic'; // Next.js helper that wraps React.lazy

// Load the heavy chart only in the browser; it is not part of the page HTML
const RevenueChart = dynamic(() => import('../components/RevenueChart'), {
  ssr: false,                              // skip server rendering for this component
  loading: () => <p>Loading chart…</p>,   // fallback while the chunk loads
});

export default function SalesPage() {
  return (
    <section>
      <h1>Sales</h1>
      {/* The chart's JavaScript arrives only when this page is shown */}
      <RevenueChart />
    </section>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `lazy()` inside a component
✅ **Correct:** Call `lazy()` at module level. Inside a component it creates a new component type on every render, so React unmounts and re-downloads the page again and again.

```jsx
// Wrong: new lazy component on every render → remounts and loses state
function Parent() {
  const Orders = lazy(() => import('./pages/Orders')); // ❌ inside render
  return <Orders />;
}

// Right: created once at module level
const Orders = lazy(() => import('./pages/Orders')); // ✅ module level
function Parent() {
  return <Orders />;
}
```

❌ **Mistake 2:** Forgetting `<Suspense>`
✅ **Correct:** A lazy component that suspends with no `Suspense` ancestor throws an error in React 18+ (no fallback to show).

```jsx
// Wrong: no Suspense boundary above the lazy page
<Routes><Route path="/orders" element={<Orders />} /></Routes>

// Right: a Suspense boundary provides the fallback
<Suspense fallback={<p>Loading…</p>}>
  <Routes><Route path="/orders" element={<Orders />} /></Routes>
</Suspense>
```

---

## 🧠 Tricky Interview Question

```jsx
import { lazy, Suspense } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

// The chunk takes 100 ms to "download" (simulated with a timer)
const Chart = lazy(
  () => new Promise((resolve) =>
    setTimeout(() => resolve({ default: () => <p>Chart</p> }), 100))
);

// Static render: no waiting, it captures what is shown right now
const html = renderToStaticMarkup(
  <div>
    <Suspense fallback={<p>Loading...</p>}>
      <Chart />
    </Suspense>
    <p>Done</p>
  </div>
);
console.log(html);
```

**Answer:** The output is `<div><p>Loading...</p><p>Done</p></div>`. `renderToStaticMarkup` does not wait for the 100 ms promise. The lazy component is still pending, so the nearest `Suspense` boundary emits its fallback. The rest of the tree (`<p>Done</p>`) renders normally. The string `Chart` never appears because the lazy module had not resolved when the markup was produced. In a real browser, the fallback would be replaced by `<p>Chart</p>` after 100 ms.

---

## ⚫ Interview Questions + Answers

**Q1: What does `React.lazy` do?**
A1: It takes a function that returns `import('...')` and creates a component that is loaded on first render. The bundler uses the `import()` to create a separate chunk.

**Q2: Why does lazy loading need `Suspense`?**
A2: While the chunk downloads, React cannot render the component. `Suspense` gives React a fallback UI to show during that wait. Without a boundary, React has nothing to show.

**Q3: Where should you place the `Suspense` boundary in a router app?**
A3: Around the `Routes` or around an `Outlet` in a layout route. That keeps the navigation bar visible while only the page area shows the spinner.

**Q4: What is a `ChunkLoadError` and how do you handle it?**
A4: It happens when the browser cannot fetch a chunk, most often after a new deploy removes old file names. Retry once, then reload the page to get the new `index.html`. Also wrap the page area in an error boundary.

**Q5: Does `lazy` only work with React Router?**
A5: No. It works with any component tree. Router only decides which route element to render. Lazy loading is a bundling and rendering feature of React, and Next.js uses the same idea through `next/dynamic`.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The app has many routes and most users only open a few
- A page imports a heavy library (charts, editors, maps, PDF viewers)
- Admin or rarely used pages inflate the first load

❌ **Avoid when:**
- The page is the first screen users see (lazy adds a round trip)
- The component is tiny (a chunk request costs more than the code)
- You need the code available offline immediately and cannot tolerate a loading state

---

## 📊 Visual Diagram

```
BEFORE (one bundle):
  main.js (3.1 MB) ─────────────────────────────────────────── loaded on first visit
    ├── Home, Orders, Admin, Reports, Charts ...

AFTER (route-based split):
  main.js (300 KB)  ── Home, Layout, Router
  orders.chunk.js   ── loaded when user opens /orders
  admin.chunk.js    ── loaded when user opens /admin

RUNTIME FLOW:
  click /orders
     │
     ▼
  Router → <Orders /> (lazy)  ──► chunk not ready ──► Suspense shows fallback
                                                         │
                                       chunk arrives ◄───┘
                                          │
                                          ▼
                                    real <Orders /> rendered
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code splitting | Dividing the bundle into smaller chunk files | Bundle को छोटे chunks में बाँटना |
| React.lazy | Creates a component that loads on first render | पहली render पर load होने वाला component बनाता है |
| Suspense | Boundary that shows a fallback while children wait | Children का इंतज़ार करते समय fallback दिखाने वाली सीमा |
| Chunk | Separately downloaded JavaScript file | अलग से download होने वाली JavaScript file |
| ChunkLoadError | Error when a chunk file cannot be fetched | Chunk file न मिलने पर आने वाला error |
| Preload | Start downloading a chunk before it is needed | जरूरत से पहले chunk download शुरू करना |

---

## ⚡ 3-Line Summary
**English:**
1. `lazy(() => import('./Page'))` splits a page into its own chunk, downloaded on first visit.
2. Wrap lazy routes in `<Suspense fallback>` so the user sees a loader instead of a blank screen.
3. Call `lazy` at module level, add a retry for chunk errors after deploys, and use `next/dynamic` in Next.js.

**Hindi:**
1. `lazy(() => import('./Page'))` page को अलग chunk में बाँटता है, जो पहली visit पर download होता है।
2. Lazy routes को `<Suspense fallback>` में रखो ताकि blank screen की जगह loader दिखे।
3. `lazy` module level पर लिखो, deploy के बाद chunk error के लिए retry रखो, और Next.js में `next/dynamic` इस्तेमाल करो।

---

## ➡️ Next Topic
**91. State Management — Why Needed** — जब कई components एक ही data share करते हैं, तब state कहाँ रखें और क्यों। Lazy routes से page का code बाँटा, अब सीखेंगे कि data कैसे बाँटें।
