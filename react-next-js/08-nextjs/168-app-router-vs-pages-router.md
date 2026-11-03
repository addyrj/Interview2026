# 168. App Router vs Pages Router
# हिंदी में: App Router vs Pages Router — Next.js के दो Routing Systems

---

## 🔵 Simple Definition (English)
Next.js has two routing systems. The **Pages Router** (the `pages/` folder, the original system) uses `getServerSideProps` / `getStaticProps` and every page is a Client-capable component. The **App Router** (the `app/` folder, introduced in Next.js 13 and stable since 13.4) is built on React Server Components, nested layouts, streaming and Server Actions.

## 🔵 सरल परिभाषा (Hindi)
Next.js में routing के दो systems हैं। **Pages Router** (`pages/` folder, मूल system) `getServerSideProps` / `getStaticProps` इस्तेमाल करता है। **App Router** (`app/` folder, Next.js 13 में आया और 13.4 से stable) React Server Components, nested layouts, streaming और Server Actions पर बना है।

---

## 🔴 Problem it Solves

The Pages Router had limits. Layouts were awkward (a `getLayout` pattern on each page), data fetching was only at page level through special functions, and every page's JavaScript was sent to the browser even for non-interactive content. A layout re-mounted when you changed pages. The App Router solves this with nested layouts that persist across navigation, data fetching directly inside any Server Component with `async/await`, per-segment loading and error UI, and less client JavaScript.

## 🔴 यह क्यों बना? (Hindi)
Pages Router की सीमाएँ थीं। Layouts अजीब थे (हर page पर `getLayout` pattern), data fetching सिर्फ page level पर special functions से होती थी, और non-interactive content के लिए भी हर page की JavaScript browser को जाती थी। Page बदलने पर layout दोबारा mount हो जाता था। App Router में nested layouts हैं जो navigation में बने रहते हैं, किसी भी Server Component में सीधे `async/await` से data fetch होता है, हर segment का अपना loading व error UI है, और client JavaScript कम जाती है।

---

## 🟢 How it Works — Step by Step

```
Pages Router (pages/):
Step 1 → File pages/products/[id].js becomes the route /products/:id
Step 2 → Optional getServerSideProps / getStaticProps runs on the server and returns props
Step 3 → The page component renders with those props (on server for HTML, then hydrates in browser)
Step 4 → Shared layout: pages/_app.js wraps all pages; _document.js customizes the HTML shell

App Router (app/):
Step 1 → Folder app/products/[id]/ with page.js becomes the route /products/:id
Step 2 → Special files per folder: layout.js, page.js, loading.js, error.js, not-found.js, route.js
Step 3 → Components are Server Components by default and can be async (fetch data inside)
Step 4 → Add 'use client' only for components needing state, effects or events
Step 5 → layout.js persists and does not re-render when navigating between its child pages
Step 6 → loading.js shows instantly (Suspense) while the page streams in
```

## 🟢 कैसे काम करता है? (Hindi)
```
Pages Router (pages/):
Step 1 → File pages/products/[id].js route /products/:id बन जाती है
Step 2 → वैकल्पिक getServerSideProps / getStaticProps server पर चलकर props लौटाता है
Step 3 → Page component उन props से render होता है (server पर HTML, फिर browser में hydrate)
Step 4 → Shared layout: pages/_app.js सभी pages को wrap करता है; _document.js HTML shell बदलता है

App Router (app/):
Step 1 → Folder app/products/[id]/ में page.js route /products/:id बन जाता है
Step 2 → हर folder में special files: layout.js, page.js, loading.js, error.js, not-found.js, route.js
Step 3 → Components default में Server Components हैं और async हो सकते हैं (अंदर data fetch)
Step 4 → State, effects या events चाहिए तभी 'use client' जोड़ो
Step 5 → layout.js बना रहता है और अपने child pages के बीच navigation पर दोबारा render नहीं होता
Step 6 → page stream होकर आता है तब तक loading.js तुरंत दिखता है (Suspense)
```

---

## 🟡 Real World Example
**Zomato restaurant page with nested layout:** `/restaurants/[slug]` has a header with the restaurant name and tabs (Order Online, Reviews, Photos). In the App Router, `app/restaurants/[slug]/layout.js` holds the header and tabs once, and `order/page.js`, `reviews/page.js` and `photos/page.js` are the tab pages. Switching tabs keeps the header mounted (no flicker, no re-fetch of header data) and only the tab content changes. In the Pages Router you had to repeat the header in every page or use a `getLayout` workaround.

## 🟡 Real Example Hindi mein
**Nested layout वाला Zomato restaurant page:** `/restaurants/[slug]` में restaurant का नाम और tabs (Order Online, Reviews, Photos) वाला header है। App Router में `app/restaurants/[slug]/layout.js` में header और tabs एक बार रहते हैं, और `order/page.js`, `reviews/page.js`, `photos/page.js` tab pages हैं। Tab बदलने पर header mounted रहता है (flicker नहीं, header data दोबारा fetch नहीं) और सिर्फ tab का content बदलता है। Pages Router में हर page में header दोहराना पड़ता था या `getLayout` workaround चाहिए था।

---

## 💻 Code Example — Basic

```jsx
// The SAME simple page in both routers.

// ===== Pages Router: pages/restaurants/[slug].js =====
export async function getServerSideProps({ params }) {          // runs on the server for each request
  const res = await fetch(`https://api.example.com/r/${params.slug}`); // fetch data on the server
  const restaurant = await res.json();                          // parse JSON
  return { props: { restaurant } };                             // data must be returned as props
}

export default function RestaurantPage({ restaurant }) {        // receives props from the function above
  return <h1>{restaurant.name}</h1>;                            // renders the name
}
```

```jsx
// ===== App Router: app/restaurants/[slug]/page.js =====
// No special data function. The component itself is async and runs on the server.
export default async function RestaurantPage({ params }) {      // Server Component by default
  const { slug } = await params;                                // Next.js 15: params is a Promise (14: plain object)
  const res = await fetch(`https://api.example.com/r/${slug}`); // fetch directly in the component
  const restaurant = await res.json();                          // parse JSON
  return <h1>{restaurant.name}</h1>;                            // same output, less ceremony
}
```

## 💻 Code Example — Advanced

```jsx
// App Router file set for a route with nested layout, loading and error UI.

// File: app/restaurants/[slug]/layout.js: persists while tabs change
import Link from 'next/link';                                   // client-side navigation with prefetch
export default async function RestaurantLayout({ children, params }) {
  const { slug } = await params;                                // read the route segment
  return (
    <section>
      <h1>Restaurant: {slug}</h1>                               {/* header stays mounted between tabs */}
      <nav>
        <Link href={`/restaurants/${slug}/order`}>Order</Link>  {/* tab 1 */}
        <Link href={`/restaurants/${slug}/reviews`}>Reviews</Link> {/* tab 2 */}
      </nav>
      {children}                                                {/* the active tab page renders here */}
    </section>
  );
}

// File: app/restaurants/[slug]/reviews/page.js
async function getReviews(slug) {
  const res = await fetch(`https://api.example.com/r/${slug}/reviews`, { cache: 'no-store' }); // always fresh
  if (!res.ok) throw new Error('Could not load reviews');       // handled by error.js
  return res.json();
}
export default async function ReviewsPage({ params }) {
  const { slug } = await params;
  const reviews = await getReviews(slug);                       // streaming: loading.js shows meanwhile
  return <ul>{reviews.map(r => <li key={r.id}>{r.text}</li>)}</ul>;
}

// File: app/restaurants/[slug]/reviews/loading.js: automatic Suspense fallback
export default function Loading() {
  return <p>Loading reviews...</p>;                             // shown instantly during navigation
}

// File: app/restaurants/[slug]/reviews/error.js: error boundary for this segment
'use client';                                                    // error.js must be a Client Component
export default function Error({ error, reset }) {
  return (
    <div>
      <p>Something went wrong: {error.message}</p>
      <button onClick={() => reset()}>Try again</button>        {/* re-attempts rendering the segment */}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Both routers can live in the same project: `app/` wins if the same URL exists in both, which allows gradual migration. Pages Router is still supported and used by many large codebases, but new Next.js docs and features (Server Components, Server Actions, `use cache` in newer versions) target the App Router. Pages Router features: `_app.js`, `_document.js`, `getServerSideProps`, `getStaticProps`, `getStaticPaths`, `pages/api/*`. App Router equivalents: `layout.js`, `fetch` with caching options, `generateStaticParams`, `route.js`.

```jsx
// Migration mapping (Pages → App)
// pages/_app.js            → app/layout.js (root layout, must contain <html> and <body>)
// pages/index.js           → app/page.js
// pages/api/orders.js      → app/api/orders/route.js (export GET, POST functions)
// getStaticPaths           → generateStaticParams
// next/router (useRouter)  → next/navigation (useRouter, usePathname, useSearchParams)

// app/layout.js (root layout)
export default function RootLayout({ children }) {
  return (
    <html lang="en">                        {/* root layout must render html and body */}
      <body>{children}</body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Importing `useRouter` from `next/router` in the App Router
✅ **Correct:** Use `next/navigation` inside `app/`

```jsx
// Wrong (App Router): throws "NextRouter was not mounted"
import { useRouter } from 'next/router';

// Right
'use client';
import { useRouter } from 'next/navigation';   // v13+ App Router hook
```

❌ **Mistake 2:** Using `getServerSideProps` inside `app/`
✅ **Correct:** Fetch in the async Server Component, and use `cache: 'no-store'` or `export const dynamic = 'force-dynamic'` for per-request data

```jsx
// Wrong: ignored in app/ directory
export async function getServerSideProps() { return { props: {} }; }

// Right
export const dynamic = 'force-dynamic';        // render on every request
export default async function Page() { const data = await fetch('https://api.example.com/x'); return <p>ok</p>; }
```

❌ **Mistake 3:** Adding `'use client'` at the top of every file "to be safe"
✅ **Correct:** Keep the default (server) and put `'use client'` on small interactive leaves

```jsx
// Wrong: whole page is client → big JS bundle, no async data fetching in component
'use client';
export default function Page() { /* ... */ }

// Right: server page + tiny client child
import LikeButton from './LikeButton';         // 'use client' lives in this small file
export default async function Page() { return <article><LikeButton /></article>; }
```

---

## 🧠 Tricky Interview Question

```jsx
// Both app/page.js and pages/index.js exist in the same Next.js project.
// Which one is shown at "/"?
```
**Answer:** Next.js reports a **build/dev error because of the conflicting routes** (both resolve to `/`). The docs state that a route in `app/` and one in `pages/` must not resolve to the same URL path. So during a migration you move a route one at a time: delete the `pages/` file when you add the `app/` equivalent. Different URLs can live happily in the two folders at once (for example `pages/old-checkout.js` and `app/products/page.js`). (Behavior around conflicts is version-dependent, but treat it as an error in practice.)

---

## ⚫ Interview Questions + Answers

Q1: What are the key differences between App Router and Pages Router?
A1: App Router: `app/` folder, Server Components by default, nested layouts, `loading.js`/`error.js`, streaming, async components for data, Server Actions, Route Handlers. Pages Router: `pages/` folder, every page is a client-hydrated component, data via `getServerSideProps`/`getStaticProps`, `_app.js` for layout, `pages/api` for APIs.

Q2: What are the special files in the App Router?
A2: `layout.js` (shared UI), `page.js` (route UI, makes it public), `loading.js` (Suspense fallback), `error.js` (error boundary, client component), `not-found.js`, `template.js` (re-mounts on navigation), `route.js` (API handler) and `default.js` (parallel routes fallback).

Q3: What is the difference between `layout.js` and `template.js`?
A3: A layout persists across navigations and keeps its state. A template creates a new instance on each navigation (state resets, effects re-run). Use a template for enter animations or per-page logging.

Q4: Can Pages Router and App Router coexist?
A4: Yes, as long as no URL is defined in both. This allows gradual migration. Shared things like `_app.js` do not apply to `app/` routes, and `next/router` does not work in `app/`.

Q5: Should new projects use App Router?
A5: Generally yes, because new features target it and the official docs recommend it. Pages Router is still supported and fine for existing apps, or when a library you depend on does not yet support Server Components.

---

## 🔷 When to Use + When Not to Use
✅ **Use App Router when:**
- Starting a new Next.js project
- You want nested layouts, streaming, Server Components and Server Actions
- You want to reduce client JavaScript

❌ **Stay on Pages Router when:**
- You have a large stable app and migration cost is high
- A key dependency (some CSS-in-JS or context-heavy libraries) is not yet compatible
- Your team needs more time to learn the Server/Client component model

---

## 📊 Visual Diagram

```
  PAGES ROUTER                         APP ROUTER
  pages/                               app/
   ├─ _app.js        (wrap all)         ├─ layout.js     (root layout, persists)
   ├─ index.js       → /                ├─ page.js       → /
   ├─ products/                         ├─ products/
   │   └─ [id].js    → /products/:id    │   ├─ layout.js (nested layout)
   └─ api/orders.js  → /api/orders      │   ├─ loading.js
                                        │   └─ [id]/page.js → /products/:id
  Data: getServerSideProps              └─ api/orders/route.js
  Layout: manual per page
                                        Data: async Server Component
                                        Layout: nested, preserved

  Re-render behavior: navigating between sibling pages keeps layout.js mounted (no re-render of the
  layout), only the new page segment renders. Pages Router remounts the page tree per route.
  Performance: App Router ships less client JS (Server Components never reach the browser).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App Router | `app/` based router using RSC | RSC पर आधारित `app/` router |
| Pages Router | Original `pages/` based router | मूल `pages/` router |
| layout.js | Shared UI that persists across routes | Routes में बना रहने वाला shared UI |
| template.js | Like layout but remounts each navigation | हर navigation पर remount होने वाला layout |
| loading.js | Instant loading UI via Suspense | Suspense वाला तुरंत loading UI |
| error.js | Error boundary for a segment | Segment का error boundary |
| route.js | Route Handler (API endpoint) | API endpoint |
| Streaming | Sending HTML in chunks as ready | तैयार होते ही HTML टुकड़ों में भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. Pages Router (`pages/`) uses `getServerSideProps`/`getStaticProps`; App Router (`app/`) uses async Server Components.
2. App Router adds nested layouts, loading/error files, streaming and Server Actions, and ships less JS.
3. Both can coexist during migration, but one URL cannot exist in both; new projects should use App Router.

**Hindi:**
1. Pages Router (`pages/`) `getServerSideProps`/`getStaticProps` इस्तेमाल करता है; App Router (`app/`) async Server Components।
2. App Router में nested layouts, loading/error files, streaming और Server Actions हैं, और JS कम जाती है।
3. Migration में दोनों साथ रह सकते हैं, पर एक URL दोनों में नहीं हो सकता; नए projects में App Router इस्तेमाल करो।

---

## ➡️ Next Topic
**169. File-based Routing** — Folders और special file names से routes कैसे बनते हैं: dynamic segments `[id]`, catch-all `[...slug]`, route groups `(group)` और parallel routes।
