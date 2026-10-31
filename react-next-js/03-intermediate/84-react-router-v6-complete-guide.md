# 84. React Router v6 — Complete Guide
# हिंदी में: React Router v6 — पूरी गाइड (URL के हिसाब से component बदलना)

---

## 🔵 Simple Definition (English)
React Router ek library hai jo Single Page Application (SPA) mein URL ke hisaab se alag-alag components dikhati hai, bina browser ko poora page reload kiye. v6 mein routes ko declarative JSX se likhte hain, aur v6.4+ mein data router (`createBrowserRouter`) se loaders aur error pages bhi milte hain.

## 🔵 सरल परिभाषा (Hindi)
React Router एक library है जो Single Page Application (SPA) में URL के हिसाब से अलग-अलग components दिखाती है, browser को पूरा page reload किए बिना। v6 में routes को declarative JSX से लिखते हैं, और v6.4+ में data router (`createBrowserRouter`) से loaders और error pages भी मिलते हैं।

---

## 🔴 Problem it Solves
Pehle `<a href="/cart">` par click karne se browser poora page dobara download karta tha, aur React ka state (cart, search box, scroll position) khatam ho jaata tha. SPA mein hum URL badalna chahte hain bina reload ke, aur URL ke saath component bhi badalna chahte hain. Browser ke back/forward buttons bhi kaam karne chahiye. React Router yeh sab handle karta hai: history API se URL badalna, matching routes dhoondhna, aur sahi element render karna.

## 🔴 यह क्यों बना? (Hindi)
पहले `<a href="/cart">` पर click करने से browser पूरा page दोबारा download करता था, और React का state (cart, search box, scroll position) खत्म हो जाता था। SPA में हम URL बदलना चाहते हैं बिना reload के, और URL के साथ component भी बदलना चाहते हैं। Browser के back/forward buttons भी काम करने चाहिए। React Router यह सब संभालता है: history API से URL बदलना, matching routes ढूँढना, और सही element render करना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App ko <BrowserRouter> (ya createBrowserRouter) se wrap karo
Step 2 → <Routes> mein <Route path="..." element={...} /> define karo
Step 3 → <Link to="..."> click hone par history.pushState se URL badlo (reload nahi)
Step 4 → React Router current location match karta hai (v6 best match chunta hai)
Step 5 → Matching route ka element render hota hai; nested ho to <Outlet /> mein child
Step 6 → Data router mein: loader pehle chalta hai, phir component useLoaderData() se data leta hai
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App को <BrowserRouter> (या createBrowserRouter) से wrap करो
Step 2 → <Routes> में <Route path="..." element={...} /> define करो
Step 3 → <Link to="..."> पर click होने पर history.pushState से URL बदलो (reload नहीं)
Step 4 → React Router current location match करता है (v6 सबसे अच्छा match चुनता है)
Step 5 → Matching route का element render होता है; nested हो तो <Outlet /> में child
Step 6 → Data router में: loader पहले चलता है, फिर component useLoaderData() से data लेता है
```

---

## 🟡 Real World Example
**Flipkart / Amazon web app:** `/` home page hai, `/product/:id` product page hai, `/cart` cart page hai, aur `/account/orders` nested account section hai। User product par click karta hai to URL badal jaata hai, header aur footer same rehte hain, aur cart ka state reload ke bina bana rehta hai। Browser back button se purana product page wapas aata hai।

## 🟡 Real Example Hindi mein
**Flipkart / Amazon web app:** `/` home page है, `/product/:id` product page है, `/cart` cart page है, और `/account/orders` nested account section है। User product पर click करता है तो URL बदल जाता है, header और footer वही रहते हैं, और cart का state reload के बिना बना रहता है। Browser का back button पुराने product page पर वापस ले जाता है।

---

## 💻 Code Example — Basic

```jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'; // router pieces (v6)

// ── BASIC ROUTER ──────────────────────────────────────
function Home() {
  return <h1>Home</h1>;                                   // rendered at "/"
}
function About() {
  return <h1>About us</h1>;                               // rendered at "/about"
}
function Products() {
  return <h1>All products</h1>;                           // rendered at "/products"
}

export default function App() {
  return (
    <BrowserRouter>                                       {/* uses the browser History API */}
      <nav>
        <Link to="/">Home</Link>                          {/* client-side link, no page reload */}
        <Link to="/about">About</Link>                    {/* changes the URL and the component */}
        <Link to="/products">Products</Link>              {/* same */}
      </nav>
      <Routes>                                            {/* picks the best matching route */}
        <Route path="/" element={<Home />} />             {/* exact match for "/" */}
        <Route path="/about" element={<About />} />       {/* match for "/about" */}
        <Route path="/products" element={<Products />} /> {/* match for "/products" */}
        <Route path="*" element={<h1>404 Not Found</h1>} /> {/* catch-all for unknown URLs */}
      </Routes>
    </BrowserRouter>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { createBrowserRouter, RouterProvider, useLoaderData, useRouteError, Link } from 'react-router-dom';

// Loader: runs BEFORE the page renders, with params from the URL (v6.4+ data router)
async function productLoader({ params }) {
  const res = await fetch(`/api/products/${params.id}`);  // params.id comes from /product/:id
  if (!res.ok) throw new Response('Not found', { status: res.status }); // error → errorElement
  return res.json();                                      // becomes useLoaderData() in the page
}

function ProductPage() {
  const product = useLoaderData();                        // data from the loader above
  return (
    <section>
      <h1>{product.name}</h1>                             {/* product title */}
      <p>₹{product.price}</p>                             {/* price */}
    </section>
  );
}

function ErrorPage() {
  const error = useRouteError();                          // whatever the loader or render threw
  return <h1>Oops: {error.status ?? 'Unexpected error'}</h1>; // friendly message
}

function Layout() {
  return (
    <div>
      <header><Link to="/">Shop</Link></header>           {/* shared header */}
      <main>{/* child route renders here */}</main>
    </div>
  );
}

const router = createBrowserRouter([                      // route tree defined as data
  {
    path: '/',                                            // top-level layout route
    element: <Layout />,                                  // wraps every child
    errorElement: <ErrorPage />,                          // shown on any thrown error below
    children: [
      { index: true, element: <h1>Welcome</h1> },         // "/" itself (index route)
      {
        path: 'product/:id',                              // dynamic segment
        loader: productLoader,                            // fetch before rendering
        element: <ProductPage />,                         // reads the loaded data
      },
      {
        path: 'admin',
        lazy: async () => ({                              // code-split: download only when visited
          Component: (await import('./AdminPage')).default, // the module's default export
        }),
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;              // mounts the router once at the top
}
```

---

## 🟠 Real app integration

Express must return `index.html` for every client-side URL, or a refresh on `/products` gives a 404. Put API routes first, then static files, then the fallback. Use a middleware without a path (not `app.get('*')`, whose wildcard syntax changed in Express 5):

```javascript
const path = require('path');                              // build-in path helper
const express = require('express');                        // web framework
const app = express();                                     // create the app

app.use('/api', apiRouter);                                // API routes first (apiRouter defined elsewhere)
app.use(express.static(path.join(__dirname, 'dist')));     // built JS, CSS, images (e.g. Vite output)

app.use((req, res, next) => {                              // fallback, no path = matches everything
  if (req.method !== 'GET') return next();                 // only GET pages get index.html
  res.sendFile(path.join(__dirname, 'dist', 'index.html')); // React Router takes over from here
});

app.listen(3000, () => console.log('Listening on http://localhost:3000')); // start the server
```

Next.js does not use React Router. The App Router uses folders as routes (`app/products/[id]/page.js` is the `/products/:id` route) and the `next/link` component for navigation. The same ideas (params, nested layouts, loaders) exist as `params`, `layout.js`, and `fetch` in Server Components.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using a plain `<a href>` for internal links (full page reload, state lost)
✅ **Correct:** Use `<Link to>` (or `<NavLink>`), which changes the URL without reloading.

```jsx
// Wrong: the browser does a full page load and React state is lost
<a href="/cart">Cart</a>                                  // ❌ reloads the whole SPA

// Right: client-side navigation
<Link to="/cart">Cart</Link>                              // ✅ no reload
```

❌ **Mistake 2:** Calling a router hook outside `BrowserRouter` or `RouterProvider`
✅ **Correct:** Put every component that uses `useNavigate`, `useParams`, or `Link` inside the router.

```jsx
// Wrong: the hook runs above the router, so there is no router context
function Root() {
  const navigate = useNavigate();                         // ❌ throws: no router context
  return <BrowserRouter><App /></BrowserRouter>;
}

// Right: the router wraps everything, then the hooks run inside it
function Root2() {
  return <BrowserRouter><App /></BrowserRouter>;          // ✅ App can use hooks
}
```

❌ **Mistake 3:** Writing an absolute child path under a parent (it throws)
✅ **Correct:** Child paths are relative to the parent, so drop the leading `/`.

```jsx
// Wrong: absolute child path that does not start with the parent path
<Route path="/dashboard" element={<Dashboard />}>
  <Route path="/stats" element={<Stats />} />            {/* ❌ throws at render */}
</Route>

// Right: relative child path
<Route path="/dashboard" element={<Dashboard />}>
  <Route path="stats" element={<Stats />} />             {/* ✅ becomes /dashboard/stats */}
</Route>
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={<div><h1>Dashboard</h1><Outlet /></div>}>
        <Route path="/stats" element={<p>Stats</p>} />   {/* absolute child path */}
      </Route>
    </Routes>
  );
}
// The browser opens /dashboard/stats. What is rendered?
```

**Answer:** Nothing is rendered, because React Router throws an error during render. Its message says the absolute child path `"/stats"` is not valid under `"/dashboard"`. In v6 a child path that starts with `/` must begin with the full combined path of its parents, so `/dashboard/stats` would be accepted, but `/stats` is not. Without an error boundary, the whole app crashes. The fix is `<Route path="stats" ...>` (relative), which matches `/dashboard/stats`. I checked this error message by rendering the code with `react-router-dom@6.30.6`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `BrowserRouter` and `createBrowserRouter`?**
A1: `BrowserRouter` is a component that provides routing context to JSX `<Routes>`. `createBrowserRouter` (v6.4+) is the data router: you define routes as an object array, with `loader`, `action`, and `errorElement`, and mount it with `<RouterProvider>`. Use the data router when you need data loading and error handling per route.

**Q2: How does React Router choose which route to render?**
A2: It ranks all matching routes and picks the most specific one. Static segments beat dynamic ones (`/product/new` beats `/product/:id`), and `*` is the lowest rank. In v6 you do not need to order routes manually.

**Q3: Why does a refresh on `/products` return 404 on my Express server?**
A3: The browser asks the server for `/products`, but the file does not exist on disk. The React app only exists in `index.html`. The server must return `index.html` for every unknown GET request, and React Router then renders the right page.

**Q4: What is `<Link>` doing that an `<a>` tag does not?**
A4: `<Link>` calls `history.pushState` to change the URL and React Router re-renders the matching route, with no reload. It also handles relative paths and the `replace` option.

**Q5: What changed between v6 and v7?**
A5: React Router v7 (released 2024) is the current major version. The core API (`Routes`, `Route`, `Link`, hooks) is the same, and the package is now `react-router` (`react-router-dom` re-exports it). This topic covers the v6 API that interviews still ask about, and most of it carries over.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- You build an SPA with several pages that share a layout (dashboard, admin, shop)
- You want the browser back button and deep links to work
- You need nested layouts, route guards, or per-route data loading

❌ **Avoid when:**
- The app is a static site with a few pages: plain links are simpler
- You use a framework with file-based routing (Next.js App Router), which already gives you routes
- The app is a single screen with tabs: store the tab in state, not in the URL

---

## 📊 Visual Diagram

```
Browser URL: /product/42
     │
     ▼
<BrowserRouter>  (or RouterProvider with createBrowserRouter)
     │
     ▼
<Routes>  ── match "/product/42" ──► <Route path="product/:id" />
     │                                    │
     │                         loader({ params: { id: "42" } })  ──► fetch data
     │                                    │
     ▼                                    ▼
<Layout>  (header, footer)           <ProductPage />  reads useLoaderData()
  └── <Outlet />  ◄── child element renders here

Click <Link to="/cart">  ──► history.pushState("/cart") ──► no reload, re-match
Browser Back            ──► popstate event ──► re-match previous URL
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SPA | Single Page Application, ek HTML page par sab screens | एक HTML page पर सारी screens |
| History API | `pushState` aur `popstate` jo URL badalta hai | URL बदलने वाला browser API |
| Route | URL pattern aur uska element | URL pattern और उसका element |
| Data router | `createBrowserRouter`, loaders aur errorElement wala router | Loaders वाला router |
| Loader | Route render se pehle data lene wala function | Render से पहले data लाने वाला function |
| errorElement | Route mein error hone par dikhne wala component | Error पर दिखने वाला component |

---

## ⚡ 3-Line Summary
**English:**
1. React Router URL ke hisaab se components badalta hai, bina page reload ke, `<Link>` aur `<Routes>` se.
2. v6.4+ mein `createBrowserRouter` se loaders, errorElement, aur lazy routes milte hain.
3. SPA deploy karte waqt server ko har unknown URL par `index.html` bhejna chahiye.

**Hindi:**
1. React Router URL के हिसाब से components बदलता है, बिना page reload के, `<Link>` और `<Routes>` से।
2. v6.4+ में `createBrowserRouter` से loaders, errorElement, और lazy routes मिलते हैं।
3. SPA deploy करते समय server को हर unknown URL पर `index.html` भेजना चाहिए।

---

## ➡️ Next Topic
**85. Routes + Route + Link + NavLink** — route matching, active link styling, और `end` prop की बारीकियाँ।
