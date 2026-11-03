# 167. Next.js vs React
# हिंदी में: Next.js vs React — Library और Framework का फ़र्क

---

## 🔵 Simple Definition (English)
**React** is a library for building UI components. **Next.js** is a full framework built on React that adds routing, server rendering, data fetching, bundling and deployment features. You use React inside Next.js, so it is not React versus Next.js but React alone versus React plus a framework.

## 🔵 सरल परिभाषा (Hindi)
**React** UI components बनाने की library है। **Next.js** React पर बना पूरा framework है जो routing, server rendering, data fetching, bundling और deployment features जोड़ता है। Next.js के अंदर React ही इस्तेमाल होता है, इसलिए यह "React बनाम Next.js" नहीं बल्कि "सिर्फ React बनाम React + framework" है।

---

## 🔴 Problem it Solves

A plain React app (Vite or the old Create React App) sends an almost empty HTML file and a big JavaScript bundle. The browser must download the JS, run it, then fetch data, so users see a blank screen first and search engines may see little content. You also have to choose and wire your own router, bundler, image optimizer, SEO tags and server setup. Next.js solves this by rendering HTML on the server (or at build time), splitting code automatically and giving one standard way to do routing, data and APIs.

## 🔴 यह क्यों बना? (Hindi)
Plain React app (Vite या पुराना Create React App) लगभग खाली HTML और बड़ा JavaScript bundle भेजता है। Browser को JS download करके चलाना पड़ता है, फिर data fetch होता है, इसलिए user को पहले blank screen दिखती है और search engines को कम content दिख सकता है। Router, bundler, image optimizer, SEO tags और server setup भी आपको खुद चुनकर जोड़ना पड़ता है। Next.js HTML को server पर (या build time पर) बनाता है, code अपने-आप split करता है और routing, data व APIs का एक standard तरीका देता है।

---

## 🟢 How it Works — Step by Step

```
Plain React (client-side rendering, CSR):
Step 1 → Browser requests the page
Step 2 → Server returns <div id="root"></div> + <script src="bundle.js">
Step 3 → Browser downloads and runs the JS
Step 4 → React renders the UI, then useEffect fetches data
Step 5 → User finally sees content (blank/spinner until now)

Next.js (App Router):
Step 1 → Browser requests the page
Step 2 → Server (or build step) runs Server Components, fetches data, renders HTML
Step 3 → Browser receives complete HTML and shows content immediately
Step 4 → Small JS for Client Components downloads and "hydrates" (attaches event handlers)
Step 5 → Navigation after that is client-side, with prefetched routes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Plain React (client-side rendering, CSR):
Step 1 → Browser page माँगता है
Step 2 → Server देता है <div id="root"></div> + <script src="bundle.js">
Step 3 → Browser JS download करके चलाता है
Step 4 → React UI बनाता है, फिर useEffect data fetch करता है
Step 5 → अब जाकर user को content दिखता है (तब तक blank/spinner)

Next.js (App Router):
Step 1 → Browser page माँगता है
Step 2 → Server (या build step) Server Components चलाता है, data fetch करता है, HTML बनाता है
Step 3 → Browser को पूरा HTML मिलता है और content तुरंत दिखता है
Step 4 → Client Components की छोटी JS download होकर "hydrate" होती है (event handlers जुड़ते हैं)
Step 5 → इसके बाद navigation client-side होता है, routes prefetch होते हैं
```

---

## 🟡 Real World Example
**Flipkart product page:** Every product page must show title, price and images quickly and must be indexable by Google (SEO decides traffic). With plain React the crawler and the user wait for JS to fetch the product. With Next.js the server sends HTML that already contains the product name and price, and only the "Add to Cart" button needs client JS. In contrast, an internal admin dashboard behind login does not need SEO, so plain React (Vite) is perfectly fine there.

## 🟡 Real Example Hindi mein
**Flipkart product page:** हर product page पर title, price और images जल्दी दिखनी चाहिए और Google उसे index कर सके (SEO से traffic आता है)। Plain React में crawler और user दोनों को product fetch होने तक JS का इंतज़ार करना पड़ता है। Next.js में server ऐसा HTML भेजता है जिसमें product का नाम और price पहले से होती है, और सिर्फ "Add to Cart" बटन को client JS चाहिए। इसके उलट, login के पीछे का internal admin dashboard SEO नहीं माँगता, इसलिए वहाँ plain React (Vite) बिल्कुल ठीक है।

---

## 💻 Code Example — Basic

```jsx
// SAME page built two ways. First: plain React (Vite), client-side fetching.
// File: src/ProductPage.jsx (plain React)
import { useState, useEffect } from 'react';                 // hooks for state and side effects

export default function ProductPage({ id }) {
  const [product, setProduct] = useState(null);              // null until data arrives
  const [error, setError] = useState(null);                  // error message if request fails

  useEffect(() => {                                           // runs in the browser AFTER first render
    let cancelled = false;                                    // avoid setting state after unmount
    fetch(`/api/products/${id}`)                              // request goes browser → API
      .then(res => {
        if (!res.ok) throw new Error('Failed');               // fetch does not throw on 404/500
        return res.json();                                    // parse JSON body
      })
      .then(data => { if (!cancelled) setProduct(data); })    // store data → triggers re-render
      .catch(e => { if (!cancelled) setError(e.message); });  // store error → triggers re-render
    return () => { cancelled = true; };                       // cleanup when id changes or unmount
  }, [id]);                                                   // re-fetch when id changes

  if (error) return <p>{error}</p>;                           // error UI
  if (!product) return <p>Loading...</p>;                     // user sees this first (blank for crawlers)
  return <h1>{product.name} - ₹{product.price}</h1>;          // real content appears only now
}
// Renders: 1) "Loading..."  2) product (two renders minimum, HTML had no product content)
```

## 💻 Code Example — Advanced

```jsx
// Same page in Next.js 15 App Router: Server Component fetches data, ships HTML with content.
// File: app/products/[id]/page.jsx (Server Component by default: no 'use client')
import { notFound } from 'next/navigation';                   // helper that renders the 404 page
import Image from 'next/image';                               // optimized images (resize, lazy, WebP/AVIF)
import AddToCart from './AddToCart';                          // small Client Component for interactivity

// SEO: metadata generated on the server per product
export async function generateMetadata({ params }) {
  const { id } = await params;                                // Next.js 15: params is a Promise
  const p = await getProduct(id);                             // same request is deduped (React cache below)
  return { title: p ? `${p.name} | ShopKart` : 'Not found', description: p?.description };
}

async function getProduct(id) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { revalidate: 60 },                                 // cache for 60 s (ISR style), v15 default is uncached
  });
  if (!res.ok) return null;                                   // let the page decide what to do
  return res.json();                                          // plain object
}

export default async function ProductPage({ params }) {
  const { id } = await params;                                // read the dynamic segment
  const product = await getProduct(id);                       // runs on the server, no loading state needed
  if (!product) notFound();                                   // renders app/not-found.jsx with 404 status
  return (
    <main>
      <h1>{product.name}</h1>                                 {/* already in the first HTML response */}
      <Image src={product.image} alt={product.name} width={400} height={400} priority /> {/* LCP image */}
      <p>₹{product.price}</p>
      <AddToCart id={product.id} />                           {/* only this part ships client JS */}
    </main>
  );
}
```

```jsx
// File: app/products/[id]/AddToCart.jsx
'use client';                                                  // this file runs in the browser too
import { useState } from 'react';
export default function AddToCart({ id }) {
  const [added, setAdded] = useState(false);                   // local UI state
  return (
    <button onClick={() => setAdded(true)} disabled={added}>   {/* event handlers need a Client Component */}
      {added ? 'Added' : 'Add to cart'}
    </button>
  );
}
```

---

## 🟠 Next.js Connection

This whole topic is the Next.js connection, so here is the feature comparison. Plain React gives you components and hooks only. Next.js adds: file-based routing, layouts, Server Components, SSR/SSG/ISR, Server Actions, Route Handlers (API endpoints), image/font optimization, metadata API, middleware and built-in code splitting. Alternatives for a "React framework" exist as well (Remix / React Router v7 framework mode, TanStack Start) (version-dependent: this space changes fast).

```jsx
// Plain React + Vite: you pick and install everything yourself
// npm create vite@latest shop -- --template react
// npm i react-router-dom @tanstack/react-query helmet ...   ← your own routing, data, SEO choices

// Next.js: one command, conventions included
// npx create-next-app@latest shop
// app/page.jsx → "/", app/cart/page.jsx → "/cart", app/api/orders/route.js → POST /api/orders
export async function GET() {                                  // app/api/health/route.js (Route Handler)
  return Response.json({ ok: true });                          // Web standard Response, no Express needed
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking Next.js replaces React
✅ **Correct:** Next.js uses React. Your components, hooks and state knowledge are fully reused

```jsx
// Wrong idea: "I learn Next.js, so I do not need hooks"
// Right: hooks work in Client Components exactly as in React
'use client';
import { useState } from 'react';
export default function Counter() { const [n, setN] = useState(0); return <button onClick={() => setN(n + 1)}>{n}</button>; }
```

❌ **Mistake 2:** Using Next.js for an app that needs no SEO or server, and paying the complexity cost
✅ **Correct:** Use Vite + React for internal dashboards, or choose Next.js when you need SEO, speed or a backend layer

```jsx
// Wrong: Next.js + everything 'use client' + all fetching in useEffect → complexity with no benefit
// Right: either a lean Vite SPA, or Next.js with Server Components fetching data
```

❌ **Mistake 3:** Using browser-only APIs during server rendering
✅ **Correct:** Use them inside `useEffect` or in a Client Component guarded appropriately

```jsx
// Wrong: runs on the server during render → "window is not defined"
export default function Page() { return <p>{window.innerWidth}</p>; }

// Right: read it after mount, in the browser
'use client';
import { useState, useEffect } from 'react';
export default function Page() {
  const [w, setW] = useState(null);                     // null on server and first client render
  useEffect(() => setW(window.innerWidth), []);         // set after hydration
  return <p>{w ?? '...'}</p>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.jsx in Next.js App Router (no 'use client')
import { useState } from 'react';

export default function Page() {
  const [n, setN] = useState(0);
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```
**Answer:** It **fails with an error**. Files in the App Router are Server Components by default, and Server Components cannot use `useState`, other state/effect hooks or event handlers such as `onClick`. Next.js reports that you are using client-only features in a Server Component and tells you to add `'use client'` at the top. After adding `'use client'`, the component works like normal React (it is also pre-rendered to HTML on the server, then hydrated). In plain React (Vite) the same code works with no directive.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between React and Next.js?
A1: React is a UI library (components, state, hooks). Next.js is a framework on top of React that adds routing, rendering strategies (SSR, SSG, ISR, CSR), data fetching, API routes, optimization and a build/deploy pipeline.

Q2: Why is Next.js better for SEO than a plain React SPA?
A2: It sends HTML that already contains the content, so crawlers and users see it at once. A SPA sends an empty shell and fills it after JS runs. (Google can run JS, but it is slower and less reliable, and social previews usually need real HTML.)

Q3: When would you choose plain React (Vite) over Next.js?
A3: For apps behind login, internal tools, dashboards, widgets embedded in other pages, or when you already have a separate backend and do not want a Node server layer. It is simpler with fewer concepts.

Q4: Does Next.js make every page server-rendered?
A4: No. Each route can be static (built once), dynamic (rendered per request) or incremental (static with revalidation), and parts can be client-only. You choose per route or per component.

Q5: What is hydration?
A5: After the server sends HTML, the browser downloads the JS and React attaches event handlers and state to that existing HTML. The page is visible first, interactive after hydration. A mismatch between server and client HTML causes hydration errors.

---

## 🔷 When to Use + When Not to Use
✅ **Use Next.js when:**
- SEO and first-load speed matter (e-commerce, blogs, marketing, news)
- You want routing, API endpoints and rendering strategies in one framework
- You need Server Components to reduce JS shipped to users

❌ **Avoid Next.js (use Vite + React) when:**
- The app is a private dashboard or tool with no SEO need
- Your team cannot host a Node/edge runtime or wants only static files
- You prefer a minimal setup and already use a separate API

---

## 📊 Visual Diagram

```
  PLAIN REACT (CSR)                         NEXT.js (App Router)
  ─────────────────                         ────────────────────
  Browser ──GET /──▶ Server                 Browser ──GET /products/5──▶ Server
          ◀─ empty HTML + bundle.js                 ◀─ full HTML (product visible)
  runs JS (blank screen)                    shows content immediately
  useEffect → fetch API                     downloads small JS for client parts
  render product                            hydrates (buttons become interactive)
  ─────────────────────────                 ─────────────────────────────────────
  Time to content: slower                   Time to content: faster
  SEO: weak by default                      SEO: strong by default
  JS shipped: everything                    JS shipped: only Client Components

  Re-render behavior: both re-render on state change; Next.js Server Components do NOT
  re-render on the client at all (they ran once on the server).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Library | Tool you call from your code | आपके code से बुलाया जाने वाला tool |
| Framework | Structure that calls your code and sets conventions | Conventions तय करने वाला structure |
| CSR | Client-side rendering in the browser | Browser में rendering |
| SSR | HTML rendered on the server per request | हर request पर server पर HTML बनना |
| Hydration | Attaching JS behaviour to server HTML | Server HTML में JS behaviour जोड़ना |
| Code splitting | Loading only the JS a page needs | सिर्फ ज़रूरी JS load करना |
| Route Handler | API endpoint in app/ folder | app/ folder में API endpoint |
| SPA | Single-page application | एक-page वाला application |

---

## ⚡ 3-Line Summary
**English:**
1. React is the UI library; Next.js is a React framework adding routing, server rendering, data and optimization.
2. Next.js sends real HTML first (better SEO and speed), while plain React sends an empty shell and renders in the browser.
3. Use Next.js for public, SEO-heavy apps and Vite + React for simple private dashboards.

**Hindi:**
1. React UI library है; Next.js React framework है जो routing, server rendering, data और optimization जोड़ता है।
2. Next.js पहले असली HTML भेजता है (बेहतर SEO और speed), जबकि plain React खाली shell भेजकर browser में render करता है।
3. Public, SEO-heavy apps के लिए Next.js और simple private dashboards के लिए Vite + React चुनो।

---

## ➡️ Next Topic
**168. App Router vs Pages Router** — Next.js में routing के दो system हैं। Interview में सबसे ज़्यादा पूछा जाता है कि दोनों में क्या फ़र्क है और कौन सा कब इस्तेमाल करें।
