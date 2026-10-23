# 166. Next.js — What It Is + Why Use It
# हिंदी में: Next.js — क्या है और क्यों use करें

---

## 🔵 Simple Definition (English)
**Next.js** is a React framework by Vercel that adds: **server-side rendering (SSR)**, **static site generation (SSG)**, **file-based routing**, **API routes**, and many optimizations — out of the box. It makes building production React apps easier, faster, and SEO-friendly. React alone is a library; Next.js is the full-stack framework built on top of React.

## 🔵 सरल परिभाषा (Hindi)
**Next.js** Vercel का React framework है जो add करता है: **server-side rendering (SSR)**, **static site generation (SSG)**, **file-based routing**, **API routes**, और कई optimizations — out of the box। यह production React apps बनाना आसान, faster, और SEO-friendly बनाता है। React सिर्फ library है; Next.js उसके ऊपर बना full-stack framework है।

---

## 🔴 Problem it Solves

```
PURE REACT (Create React App) problems:
❌ SEO: HTML is empty until JS loads → search engines see blank page
❌ Performance: All JS downloaded before first paint (slow)
❌ Routing: Need react-router, set it up manually
❌ Data fetching: useEffect → no data on initial render
❌ API: Need separate backend server
❌ Image optimization: manual
❌ Code splitting: manual configuration

NEXT.JS solves all of these:
✅ SSR/SSG: HTML from server → great SEO, fast first paint
✅ App Router: folder structure = routes (no config)
✅ Server Components: fetch data on server directly
✅ API Routes: backend endpoints in same project
✅ next/image: automatic optimization, lazy loading
✅ Automatic code splitting: each page loads only its JS
```

## 🔴 यह क्यों बना? (Hindi)
```
Pure React के problems:
❌ SEO: HTML JS load होने तक खाली → search engines blank page देखते हैं
❌ Performance: सब JS download होने के बाद first paint
❌ Routing: react-router manually setup करना पड़ता

Next.js सब solve करता है:
✅ Server पर HTML → great SEO, fast first paint
✅ Folder structure = routes (no configuration)
✅ Server पर direct data fetch
✅ Same project में API endpoints
```

---

## 🟢 How it Works — Step by Step

```
NEXT.JS APP ROUTER (Next.js 13+):

Step 1 → Create file: app/page.jsx → becomes "/" route
         Create file: app/about/page.jsx → becomes "/about" route
         Create file: app/products/[id]/page.jsx → "/products/123"

Step 2 → Server Components (default):
         - Runs on server
         - Can fetch data with async/await directly
         - HTML sent to browser (SEO ✅, fast ✅)
         - No useState/useEffect needed

Step 3 → Client Components ('use client'):
         - Add 'use client' at top
         - Runs in browser (hydration)
         - Can use hooks, events, browser APIs

Step 4 → Hydration:
         Server sends HTML (user sees fast) →
         React attaches in browser (becomes interactive)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → File बनाओ: app/page.jsx → "/" route बन जाता है
         Folder structure = URL structure

Step 2 → Server Components (default):
         - Server पर run होता है
         - async/await से directly data fetch
         - HTML browser को जाता है → SEO ✅

Step 3 → Client Components ('use client'):
         - Browser में run होता है
         - Hooks, events, browser APIs use हो सकते हैं

Step 4 → Hydration:
         Server HTML → fast first paint →
         React browser में attach → interactive
```

---

## 🟡 Real World Example
**Flipkart Product Page:** The product title, description, price — rendered on server (HTML in source → SEO + fast). The "Add to Cart" button, image carousel, reviews section — rendered on client (need interactivity). Next.js lets you mix both in one page — best of SSR and CSR.

## 🟡 Real Example Hindi mein
**Flipkart Product Page:** Product title, description, price — server पर render (HTML में → SEO + fast)। "Add to Cart" button, image carousel — client पर render (interactivity चाहिए)। Next.js दोनों mix करने देता है एक page में।

---

## 💻 Code Example — Basic

```jsx
// ── NEXT.JS APP ROUTER FILE STRUCTURE ────
// app/
// ├── layout.jsx        → shared layout for all pages
// ├── page.jsx          → "/" route
// ├── about/
// │   └── page.jsx      → "/about" route
// ├── products/
// │   ├── page.jsx      → "/products" route
// │   └── [id]/
// │       └── page.jsx  → "/products/123" route
// └── api/
//     └── products/
//         └── route.js  → "/api/products" endpoint

// ── app/page.jsx — HOME PAGE (Server Component) ──
// No 'use client' = runs on server
async function HomePage() {
  // Direct database/API call on server! No useEffect!
  const featuredProducts = await fetch('https://api.example.com/products/featured')
    .then(r => r.json());

  return (
    <main>
      <h1>Welcome to Zomato</h1>
      <p>Order food from your favorite restaurants</p>

      {/* Render products — HTML sent to browser */}
      <ul>
        {featuredProducts.map(p => (
          <li key={p.id}>{p.name}</li>
        ))}
      </ul>
    </main>
  );
}

export default HomePage;

// ── app/layout.jsx — SHARED LAYOUT ────────
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Zomato',
  description: 'Order food online',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header>
          <nav>Navbar here</nav>
        </header>
        <main>{children}</main>  {/* Page content goes here */}
        <footer>Footer here</footer>
      </body>
    </html>
  );
}

// ── app/products/[id]/page.jsx — DYNAMIC ROUTE ──
async function ProductPage({ params }) {
  // params.id = URL parameter
  const product = await fetch(`https://api.example.com/products/${params.id}`)
    .then(r => r.json());

  return (
    <div>
      <h1>{product.name}</h1>
      <p>₹{product.price}</p>
      {/* This is Server Component — no useEffect needed! */}
    </div>
  );
}

export default ProductPage;
```

## 💻 Code Example — Advanced

```jsx
// ── SERVER + CLIENT COMPONENT TOGETHER ────
// Server Component (parent — default):
// app/products/[id]/page.jsx
import AddToCartButton from '@/components/AddToCartButton';

async function ProductDetailPage({ params }) {
  // Server: fetch data
  const [product, reviews] = await Promise.all([
    fetch(`/api/products/${params.id}`).then(r => r.json()),
    fetch(`/api/reviews/${params.id}`).then(r => r.json()),
  ]);

  return (
    <div>
      {/* Server-rendered: in HTML, SEO-friendly */}
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p>₹{product.price}</p>

      {/* Client Component embedded in Server Component */}
      <AddToCartButton productId={product.id} price={product.price} />

      {/* Server-rendered reviews */}
      <section>
        <h2>Reviews ({reviews.length})</h2>
        {reviews.map(r => (
          <div key={r.id}>
            <strong>{r.author}</strong>: {r.text}
          </div>
        ))}
      </section>
    </div>
  );
}

// ── Client Component (child) ───────────────
// components/AddToCartButton.jsx
'use client'; // THIS makes it client-side
import { useState } from 'react';

function AddToCartButton({ productId, price }) {
  const [added, setAdded] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    setLoading(true);
    await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ productId, price }),
    });
    setAdded(true);
    setLoading(false);
  };

  return (
    <button onClick={handleAdd} disabled={loading}>
      {loading ? 'Adding...' : added ? '✓ Added to Cart' : 'Add to Cart'}
    </button>
  );
}

// ── API ROUTES ─────────────────────────────
// app/api/products/route.js
import { NextResponse } from 'next/server';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get('category');

  const products = await db.products.findMany({
    where: category ? { category } : {},
  });

  return NextResponse.json(products);
}

export async function POST(request) {
  const body = await request.json();
  const product = await db.products.create({ data: body });
  return NextResponse.json(product, { status: 201 });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using hooks in Server Components
```jsx
// WRONG: Server Components can't use hooks!
// app/page.jsx (no 'use client')
function HomePage() {
  const [count, setCount] = useState(0); // ❌ Error!
  // "useState" is not available in Server Components
}

// CORRECT: Add 'use client' if you need hooks
'use client';
function HomePage() {
  const [count, setCount] = useState(0); // ✅
}
// OR: Keep as Server Component, extract interactive part to Client Component
```

❌ **Mistake 2:** Making everything a Client Component
```jsx
// WRONG: 'use client' on every file — defeats Next.js purpose!
'use client';
async function ProductsPage() {  // ❌ heavy Client Component
  const [products, setProducts] = useState([]);
  useEffect(() => { fetch('/api/products').then(...) }, []);
  // This is the React SPA pattern — no SSR benefit!
}

// CORRECT: Server Component for data, Client Component for interactivity
async function ProductsPage() {             // Server — no 'use client'
  const products = await fetchProducts();   // Server-side fetch
  return <ProductList products={products} />; // Could be Server Component
}
```

---

## 🧠 Tricky Interview Question

**What is the difference between `getServerSideProps` (Next.js 12) and Server Components (Next.js 13+ App Router)?**

**Answer:** `getServerSideProps` (Pages Router): separate exported function, runs on server before each request, passes data as props to the page component which still renders as normal React component. Server Components (App Router): the component ITSELF is async and runs on server — no separate data function needed, no props overhead, smaller client bundle (server code not shipped), can be nested anywhere in the tree. Server Components are the newer, more powerful approach — `getServerSideProps` only worked at the page level.

---

## ⚫ Interview Questions + Answers

**Q1: What is Next.js and what problems does it solve over plain React?**
A1: Next.js is a React framework that adds: file-based routing (folders = URLs), Server Components (run on server for SSR/SSG — great for SEO and performance), API routes (backend in same project), image/font optimization, automatic code splitting, and production tooling. Plain React (CRA/Vite) is a CSR SPA — the HTML is empty until JS loads, which is bad for SEO and perceived performance.

**Q2: What is the difference between Server Components and Client Components in Next.js?**
A2: Server Components (default, no `'use client'`): run on the server, can be async, can fetch data directly, can access databases/secrets, their code is NOT sent to the browser, can't use hooks or browser APIs. Client Components (`'use client'`): run in the browser, can use hooks (useState, useEffect), can access browser APIs, interactive. Best practice: default to Server Components; only add `'use client'` when you need interactivity.

**Q3: What is hydration in Next.js?**
A3: Hydration is the process where React "attaches" to server-rendered HTML in the browser. Next.js generates HTML on the server (fast first paint, SEO). This HTML is sent to the browser with a small JS bundle. React then "hydrates" — it walks the existing HTML DOM, recreates the Virtual DOM, and attaches event handlers — making the page interactive. If server HTML and client render don't match, a "hydration mismatch" error occurs.

**Q4: What are the rendering modes in Next.js App Router?**
A4: (1) **Static (SSG)**: rendered at build time — best for content that doesn't change per request (blog, docs). (2) **Dynamic (SSR)**: rendered per request on server — for user-specific or always-fresh data. (3) **Client-side**: rendered in browser — for highly interactive components. Next.js 13+ automatically determines this based on how you fetch data: `cache: 'force-cache'` = static, `cache: 'no-store'` = dynamic, `revalidate` = incremental static regeneration (ISR).

**Q5: What is the App Router vs Pages Router in Next.js?**
A5: **Pages Router** (legacy): `/pages` directory, `getStaticProps`/`getServerSideProps`/`getStaticPaths` for data fetching, no Server Components. **App Router** (Next.js 13+, recommended): `/app` directory, Server Components by default, `async/await` directly in components, nested layouts via `layout.jsx`, parallel routes, intercepting routes, better performance. New projects should use App Router; Pages Router is maintained but not the future.

---

## 🔷 When to Use + When Not to Use
✅ **Use Next.js when:**
- SEO matters (e-commerce, blogs, marketing sites)
- Need server-side data fetching
- Want full-stack in one project (API routes)
- Production React apps with teams

❌ **Plain React (Vite) is fine when:**
- Internal tool (SEO doesn't matter)
- Pure SPA with no SEO requirements
- Learning React basics
- Highly interactive app with minimal public-facing pages

---

## 📊 Visual Diagram

```
REACT vs NEXT.JS:
──────────────────────────────────────────────
  Pure React (CSR):
  Browser → Request → Server: empty HTML + big JS
  → Browser downloads JS → Executes → Renders
  User sees content: ~2-5s 😐

  Next.js (SSR):
  Browser → Request → Server: renders component → HTML + small JS
  → Browser shows HTML immediately → React hydrates
  User sees content: ~200ms ✅ (SEO ✅)

NEXT.JS APP ROUTER:
──────────────────────────────────────────────
  app/
  ├── layout.jsx          ← wraps everything
  ├── page.jsx            ← "/"
  ├── about/
  │   └── page.jsx        ← "/about"
  └── products/
      ├── page.jsx        ← "/products"
      └── [id]/
          └── page.jsx    ← "/products/:id"

  Server Component (default)     Client Component
  ┌──────────────────────┐       ┌──────────────────────┐
  │ No 'use client'      │       │ 'use client' at top  │
  │ async function Page()│       │ Uses hooks/events    │
  │ await fetchData()    │       │ Interactive          │
  │ Returns JSX → HTML   │       │ Browser JS           │
  │ Code stays on server │       │ Code sent to browser │
  └──────────────────────┘       └──────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSR | Server-Side Rendering — HTML from server | Server से HTML render करना |
| SSG | Static Site Generation — build-time HTML | Build time पर HTML generate करना |
| Hydration | React attaches to server HTML | React server HTML से attach होना |
| App Router | New `/app` directory routing | नया `/app` folder routing |
| Server Component | Component running on server | Server पर run होने वाला component |
| Client Component | Component running in browser | Browser में run होने वाला component |
| File-based routing | Folder = URL (no config) | Folder = URL (configuration नहीं) |

---

## ⚡ 3-Line Summary
**English:**
1. Next.js = React + SSR + file-based routing + API routes + image optimization — the production-ready React framework.
2. App Router: Server Components by default (fast, SEO) — add `'use client'` only for interactive parts.
3. Hydration: server sends HTML for fast first paint → React attaches in browser for interactivity.

**Hindi:**
1. Next.js = React + SSR + file-based routing + API routes + optimization — production-ready React framework।
2. App Router: Server Components by default (fast, SEO) — सिर्फ interactive parts के लिए `'use client'` add करो।
3. Hydration: server HTML भेजता है fast first paint के लिए → React browser में attach होता है interactivity के लिए।

---

## ➡️ Next Topic
**167. Next.js App Router — File Structure** — App Router की पूरी file structure और conventions।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Fireship — Next.js in 100 seconds](https://www.youtube.com/results?search_query=next.js+explained+in+100+seconds+fireship) | Quick Next.js overview |
| 📺 YouTube | [Akshay Saini — Next.js](https://www.youtube.com/results?search_query=next.js+namaste+react+akshay+saini) | Next.js in Hindi |
| 📝 Docs | [nextjs.org/docs](https://nextjs.org/docs) | Official Next.js documentation |
| 📺 YouTube | [Theo — Why Next.js](https://www.youtube.com/results?search_query=why+nextjs+t3+theo) | Why use Next.js |
