# 169. File-based Routing
# हिंदी में: File-based Routing — Folders से Routes बनाना

---

## 🔵 Simple Definition (English)
**File-based routing** means your folder and file structure defines your URLs. In the Next.js App Router a folder inside `app/` is a URL segment, and a `page.js` file inside it makes that segment publicly accessible. You do not write a routes table.

## 🔵 सरल परिभाषा (Hindi)
**File-based routing** का मतलब है कि आपकी folder और file structure ही आपके URLs तय करती है। Next.js App Router में `app/` के अंदर हर folder एक URL segment है, और उसमें `page.js` file होने पर वह segment public बन जाता है। आपको routes की अलग table नहीं लिखनी पड़ती।

---

## 🔴 Problem it Solves

In plain React with React Router you maintain a central list of `<Route path=... element=... />`. As an app grows this list gets long, route and file locations drift apart, and code splitting must be wired by hand (`React.lazy`). New developers must search to find which file serves a URL. File-based routing makes the structure self-documenting: to find `/orders/42` open `app/orders/[id]/page.js`. Each route is also automatically code-split.

## 🔴 यह क्यों बना? (Hindi)
Plain React में React Router के साथ आप `<Route path=... element=... />` की central list खुद संभालते हो। App बड़ा होने पर यह list लंबी हो जाती है, route और file की जगह अलग हो जाती है, और code splitting हाथ से जोड़ना पड़ता है (`React.lazy`)। नए developer को खोजना पड़ता है कि कौन सी file कौन सा URL चलाती है। File-based routing structure को खुद-दस्तावेज़ बना देता है: `/orders/42` देखना हो तो `app/orders/[id]/page.js` खोलो। हर route अपने-आप code-split भी होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → app/page.js                      → "/"
Step 2 → app/about/page.js                → "/about"
Step 3 → app/products/page.js             → "/products"
Step 4 → app/products/[id]/page.js        → "/products/42"       (dynamic segment, params.id = "42")
Step 5 → app/docs/[...slug]/page.js       → "/docs/a/b/c"        (catch-all, params.slug = ["a","b","c"])
Step 6 → app/docs/[[...slug]]/page.js     → also matches "/docs"  (optional catch-all)
Step 7 → app/(shop)/cart/page.js          → "/cart"               (route group: (shop) is NOT in the URL)
Step 8 → app/_components/                 → private folder, never a route (underscore prefix)
Step 9 → app/@modal/ + layout slot        → parallel route, (.)photo → intercepting route
Step 10 → A folder WITHOUT page.js (or route.js) is not public, even if it has other files

Pages Router equivalent: pages/products/[id].js, pages/docs/[...slug].js, pages/docs/[[...slug]].js
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → app/page.js                      → "/"
Step 2 → app/about/page.js                → "/about"
Step 3 → app/products/page.js             → "/products"
Step 4 → app/products/[id]/page.js        → "/products/42"       (dynamic segment, params.id = "42")
Step 5 → app/docs/[...slug]/page.js       → "/docs/a/b/c"        (catch-all, params.slug = ["a","b","c"])
Step 6 → app/docs/[[...slug]]/page.js     → "/docs" भी match करता है (optional catch-all)
Step 7 → app/(shop)/cart/page.js          → "/cart"               (route group: (shop) URL में नहीं आता)
Step 8 → app/_components/                 → private folder, कभी route नहीं बनता (underscore prefix)
Step 9 → app/@modal/ + layout slot        → parallel route, (.)photo → intercepting route
Step 10 → जिस folder में page.js (या route.js) नहीं, वह public नहीं है, भले उसमें दूसरी files हों

Pages Router में बराबर: pages/products/[id].js, pages/docs/[...slug].js, pages/docs/[[...slug]].js
```

---

## 🟡 Real World Example
**Amazon-style store:** `/` is the home page, `/s?k=laptop` is search, `/dp/B09XYZ` is a product page (`app/dp/[asin]/page.js`), `/gp/cart` is the cart and `/orders/123/track` is order tracking (`app/orders/[id]/track/page.js`). Marketing pages (about, careers) are grouped in `(marketing)` with a simple layout and shop pages in `(shop)` with a header and cart icon layout. Both groups share the same domain root because group names are not part of the URL.

## 🟡 Real Example Hindi mein
**Amazon जैसा store:** `/` home page है, `/s?k=laptop` search है, `/dp/B09XYZ` product page है (`app/dp/[asin]/page.js`), `/gp/cart` cart है और `/orders/123/track` order tracking है (`app/orders/[id]/track/page.js`)। Marketing pages (about, careers) `(marketing)` group में सरल layout के साथ और shop pages `(shop)` में header व cart icon वाले layout के साथ रखे जाते हैं। दोनों groups एक ही domain root पर रहते हैं क्योंकि group का नाम URL में नहीं आता।

---

## 💻 Code Example — Basic

```jsx
// Basic: three routes and a link between them (App Router, Next.js 14/15).

// File: app/page.js → "/"
import Link from 'next/link';                                  // Link does client-side navigation + prefetch
export default function Home() {
  return (
    <main>
      <h1>Home</h1>
      <Link href="/products">See products</Link>               {/* navigates without full page reload */}
    </main>
  );
}

// File: app/products/page.js → "/products"
import Link from 'next/link';
const products = [{ id: 1, name: 'Phone' }, { id: 2, name: 'Laptop' }]; // fake data for the demo
export default function Products() {
  return (
    <ul>
      {products.map(p => (
        <li key={p.id}>
          <Link href={`/products/${p.id}`}>{p.name}</Link>     {/* builds /products/1 and /products/2 */}
        </li>
      ))}
    </ul>
  );
}

// File: app/products/[id]/page.js → "/products/1"
export default async function Product({ params }) {
  const { id } = await params;                                 // Next.js 15: await params (14: plain object)
  return <h1>Product #{id}</h1>;                               // id is always a string
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: catch-all, route group, searchParams, static params and programmatic navigation.

// File: app/(shop)/layout.js: group layout, "(shop)" is not part of the URL
export default function ShopLayout({ children }) {
  return (
    <div>
      <header>ShopKart · Cart</header>                          {/* applies to all pages in the (shop) group */}
      {children}
    </div>
  );
}

// File: app/(shop)/category/[...path]/page.js → /category/electronics/mobiles/android
export default async function Category({ params, searchParams }) {
  const { path } = await params;                                // ["electronics","mobiles","android"]
  const { sort = 'popular', page = '1' } = await searchParams;  // query string, e.g. ?sort=price&page=2 (Promise in 15)
  return (
    <section>
      <h1>{path.join(' / ')}</h1>                               {/* breadcrumb-like title */}
      <p>Sorted by {sort}, page {page}</p>                      {/* using the query values */}
    </section>
  );
}
// Using searchParams makes the route dynamic (rendered per request).

// File: app/(shop)/products/[id]/page.js: pre-render known pages at build time
export async function generateStaticParams() {
  const items = await fetch('https://api.example.com/products?top=100').then(r => r.json());
  return items.map(p => ({ id: String(p.id) }));                // each object = one pre-rendered URL
}
export default async function Product({ params }) {
  const { id } = await params;
  return <h1>Product {id}</h1>;
}

// File: app/(shop)/SearchBox.js: programmatic navigation needs a Client Component
'use client';
import { useRouter, usePathname, useSearchParams } from 'next/navigation'; // NOT next/router
import { useState } from 'react';
export default function SearchBox() {
  const router = useRouter();                                   // push, replace, back, refresh
  const pathname = usePathname();                               // current path, e.g. "/category/x"
  const params = useSearchParams();                             // read-only URLSearchParams
  const [q, setQ] = useState(params.get('q') ?? '');            // start from the URL value
  function submit(e) {
    e.preventDefault();                                         // stop form reload
    const next = new URLSearchParams(params.toString());        // copy existing query params
    next.set('q', q);                                           // set the new search term
    router.push(`${pathname}?${next.toString()}`);              // client-side navigation
  }
  return (
    <form onSubmit={submit}>
      <input value={q} onChange={e => setQ(e.target.value)} />  {/* controlled input */}
      <button>Search</button>
    </form>
  );
}
```

---

## 🟠 Next.js Connection

This topic is Next.js. Related file conventions worth knowing: `not-found.js` (404 UI, trigger with `notFound()`), `middleware.js` (runs before routing, for redirects and auth; renamed `proxy` in very recent versions, version-dependent), `next.config.js` redirects and rewrites, and `route.js` for API endpoints. In the Pages Router the same ideas exist as `pages/404.js`, `pages/api/*` and `useRouter` from `next/router`.

```jsx
// next.config.js: redirects and rewrites (file routing is not the only way to define URLs)
module.exports = {
  async redirects() {
    return [{ source: '/old-menu', destination: '/menu', permanent: true }]; // 308 redirect
  },
  async rewrites() {
    return [{ source: '/help', destination: '/support/faq' }];  // URL stays /help, content from /support/faq
  },
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `page.js`, so the URL returns 404
✅ **Correct:** Every public route folder needs a `page.js` (or `route.js`)

```jsx
// Wrong: app/about/About.js exists but no page.js → /about is 404
// Right: rename to app/about/page.js
export default function About() { return <h1>About</h1>; }
```

❌ **Mistake 2:** Using `<a href>` for internal links
✅ **Correct:** Use `next/link`

```jsx
// Wrong: full page reload, loses client state, no prefetch
<a href="/cart">Cart</a>

// Right: client-side navigation with prefetch
import Link from 'next/link';
<Link href="/cart">Cart</Link>
```

❌ **Mistake 3:** Reading `params` without awaiting it in Next.js 15
✅ **Correct:** `await params` (and `searchParams`) in Server Components, or `use(params)` in Client Components

```jsx
// Wrong in Next.js 15: params is a Promise, so params.id is undefined
export default function Page({ params }) { return <h1>{params.id}</h1>; }

// Right
export default async function Page({ params }) {
  const { id } = await params;
  return <h1>{id}</h1>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
// Files in the project:
// app/blog/[slug]/page.js
// app/blog/new/page.js
// Which file handles /blog/new ?  And what does /blog/hello handle?
```
**Answer:** `/blog/new` is handled by `app/blog/new/page.js`, because **static segments have higher priority than dynamic segments**. `/blog/hello` falls to `app/blog/[slug]/page.js` with `slug = "hello"`. Priority order is: static, then dynamic `[x]`, then catch-all `[...x]`, then optional catch-all `[[...x]]`. This is why you can create a special `new` page without it being treated as a slug.

---

## ⚫ Interview Questions + Answers

Q1: How does file-based routing work in the App Router?
A1: Each folder in `app/` is a URL segment. A `page.js` file makes the segment a public route and `layout.js` wraps it. Dynamic parts use `[param]` folders, and `params` are passed as a prop to the page.

Q2: What is the difference between `[id]`, `[...slug]` and `[[...slug]]`?
A2: `[id]` matches exactly one segment. `[...slug]` matches one or more segments (value is an array). `[[...slug]]` is optional catch-all: it also matches the route with no segment (value is `undefined`).

Q3: What are route groups and private folders?
A3: A folder named `(group)` organizes routes and lets them share a layout without adding to the URL. A folder prefixed with an underscore, `_components`, is private and opted out of routing.

Q4: How do you navigate programmatically?
A4: In Client Components use `useRouter` from `next/navigation` (`push`, `replace`, `back`, `refresh`). In Server Components or Server Actions use `redirect()` from `next/navigation`. Use `<Link>` for normal links.

Q5: What are parallel and intercepting routes?
A5: Parallel routes (`@slot` folders) render several pages in the same layout at once (for example a dashboard with separate panels). Intercepting routes (`(.)photo`) show another route inside the current layout, such as an Instagram-style photo modal on click that becomes a full page on refresh.

---

## 🔷 When to Use + When Not to Use
✅ **Use file-based routing when:**
- You want routes that match the folder structure and are easy to find
- You want automatic code splitting per route
- Multiple developers need conventions, not custom config

❌ **Avoid relying only on files when:**
- You need highly dynamic route tables defined at runtime (use rewrites, middleware or a catch-all)
- You must support legacy URL patterns (use `redirects` / `rewrites` in config)

---

## 📊 Visual Diagram

```
  app/
  ├─ layout.js                      (root layout)
  ├─ page.js                        →  /
  ├─ about/page.js                  →  /about
  ├─ (shop)/                        ← group: not in the URL
  │   ├─ layout.js
  │   ├─ cart/page.js               →  /cart
  │   └─ products/
  │       ├─ page.js                →  /products
  │       └─ [id]/page.js           →  /products/42
  ├─ docs/[...slug]/page.js         →  /docs/a/b/c
  ├─ _components/                   (private, not routable)
  └─ api/orders/route.js            →  /api/orders

  Priority: static > [dynamic] > [...catch-all] > [[...optional]]

  Re-render behavior: navigating /products/1 → /products/2 reuses the same page component
  with new params. Layouts above are preserved and not re-rendered.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Segment | One part of a URL path | URL path का एक हिस्सा |
| page.js | File that makes a route public | Route को public बनाने वाली file |
| Dynamic segment | `[id]` folder matching any value | कोई भी value match करने वाला `[id]` folder |
| Catch-all | `[...slug]` matches many segments | कई segments match करने वाला |
| Route group | `(name)` folder, not in URL | `(name)` folder, URL में नहीं |
| Private folder | `_name` folder excluded from routing | Routing से बाहर `_name` folder |
| generateStaticParams | Lists params to pre-render | Pre-render होने वाले params की list |
| searchParams | Query string values | Query string की values |

---

## ⚡ 3-Line Summary
**English:**
1. Folders in `app/` are URL segments and `page.js` makes a segment public.
2. `[id]`, `[...slug]`, `[[...slug]]` and `(group)` give dynamic, catch-all and grouped routes; static beats dynamic.
3. Use `<Link>` and `next/navigation` for navigation, and remember to `await params` in Next.js 15.

**Hindi:**
1. `app/` के folders URL segments हैं और `page.js` segment को public बनाता है।
2. `[id]`, `[...slug]`, `[[...slug]]` और `(group)` से dynamic, catch-all और grouped routes बनते हैं; static को dynamic पर priority मिलती है।
3. Navigation के लिए `<Link>` और `next/navigation` इस्तेमाल करो, और Next.js 15 में `params` को `await` करना याद रखो।

---

## ➡️ Next Topic
**170. Server Components in Next.js** — अब तक सारे pages Server Components थे। अगला topic बताता है कि वे असल में क्या हैं, क्या कर सकते हैं और क्या नहीं।
