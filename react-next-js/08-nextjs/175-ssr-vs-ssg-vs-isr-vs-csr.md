# 175. SSR vs SSG vs ISR vs CSR
# हिंदी में: चारों Rendering Strategies की तुलना — कब कौन सी चुनें

---

## 🔵 Simple Definition (English)
These are four ways to produce a page's HTML. **CSR** (Client-Side Rendering) builds it in the browser. **SSR** (Server-Side Rendering) builds it on the server for every request. **SSG** (Static Site Generation) builds it once at build time. **ISR** (Incremental Static Regeneration) is SSG that rebuilds pages in the background after a time or an event.

## 🔵 सरल परिभाषा (Hindi)
ये page का HTML बनाने के चार तरीके हैं। **CSR** (Client-Side Rendering) में HTML browser में बनता है। **SSR** (Server-Side Rendering) में हर request पर server पर बनता है। **SSG** (Static Site Generation) में build time पर एक बार बनता है। **ISR** (Incremental Static Regeneration) वह SSG है जो समय या event के बाद background में pages को दोबारा बनाता है।

---

## 🔴 Problem it Solves

No single strategy fits every page. A Zomato restaurant list needs SEO and speed; a Gmail inbox needs private live data and no SEO; a docs site needs the cheapest, fastest delivery. If you pick wrongly, you get slow pages (SSR for static content), stale data (SSG for live prices), poor SEO (CSR for public content) or huge build times (SSG for millions of pages). Next.js lets you choose per page, so understanding the trade-offs is a core interview skill.

```jsx
// PROBLEM: one-size-fits-all
// All CSR  → every page: empty HTML, spinner, weak SEO
// All SSR  → every page: server work on each hit, higher cost, higher TTFB
// All SSG  → live data (stock, cart) gets stale; 1M pages = very long build
```

## 🔴 यह क्यों बना? (Hindi)
कोई एक strategy हर page पर फिट नहीं होती। Zomato की restaurant list को SEO और speed चाहिए; Gmail inbox को private live data चाहिए और SEO नहीं; docs site को सबसे सस्ती और तेज़ delivery चाहिए। गलत चुनाव से धीमे pages (static content पर SSR), पुराना data (live price पर SSG), कमज़ोर SEO (public content पर CSR) या बहुत लंबे builds (लाखों pages पर SSG) मिलते हैं। Next.js हर page के लिए अलग चुनने देता है, इसलिए trade-offs समझना interview का मुख्य skill है।

---

## 🟢 How it Works — Step by Step

```
CSR  → Server sends empty shell + JS → browser runs JS → fetches data → renders
SSR  → Request → server fetches data → renders HTML → sends full page → hydrate
SSG  → Build: fetch data → render HTML file → CDN serves the same file to all
ISR  → SSG + revalidate: serve cached file; after the interval, rebuild in background

Decision questions:
1. Is the data different per user/request?     → yes: SSR or CSR
2. Does it need SEO / fast first paint?        → yes: SSR / SSG / ISR (not pure CSR)
3. Does it change often?                       → rarely: SSG;  sometimes: ISR;  always: SSR/CSR
4. Is it behind a login (no SEO needed)?       → CSR (or SSR with streaming) is fine
```

## 🟢 कैसे काम करता है? (Hindi)
```
CSR  → Server खाली shell + JS भेजता है → browser JS चलाता है → data लाता है → render
SSR  → Request → server data लाता है → HTML render करता है → पूरा page भेजता है → hydrate
SSG  → Build: data लाओ → HTML file बनाओ → CDN सबको वही file परोसता है
ISR  → SSG + revalidate: cached file परोसो; interval के बाद background में दोबारा बनाओ

फ़ैसले के सवाल:
1. क्या data हर user/request पर अलग है?     → हाँ: SSR या CSR
2. क्या SEO / तेज़ first paint चाहिए?       → हाँ: SSR / SSG / ISR (सिर्फ CSR नहीं)
3. क्या यह अक्सर बदलता है?                  → कम: SSG;  कभी-कभी: ISR;  हमेशा: SSR/CSR
4. क्या यह login के पीछे है (SEO नहीं)?      → CSR (या streaming के साथ SSR) ठीक है
```

---

## 🟡 Real World Example
**One e-commerce app, four strategies:**
- **Homepage banners & marketing page (SSG):** same for everyone, built once, served from CDN.
- **Product detail page (ISR):** price and stock change a few times a day, so regenerate every few minutes; millions of products are generated on demand.
- **Order tracking / "My Orders" (SSR):** depends on the logged-in user and changes live.
- **Cart drawer, notifications, chat widget (CSR):** private, interactive, no SEO value, updated by the user's actions.

## 🟡 Real Example Hindi mein
**एक e-commerce app में चारों strategies:**
- **Homepage banners और marketing page (SSG):** सबके लिए एक जैसा, एक बार बना, CDN से परोसा।
- **Product detail page (ISR):** price और stock दिन में कुछ बार बदलते हैं, इसलिए कुछ मिनट में regenerate; लाखों products माँग पर बनते हैं।
- **Order tracking / "My Orders" (SSR):** logged-in user पर निर्भर और live बदलता है।
- **Cart drawer, notifications, chat widget (CSR):** private, interactive, SEO की ज़रूरत नहीं, user के actions से update।

---

## 💻 Code Example — Basic

```jsx
// The same page written four ways in the Pages Router (one export per file).
// Each snippet is a separate file; only the data function differs.

// ---- pages/csr.js : CSR (data fetched in the browser) ----
import { useState, useEffect } from 'react';
export function CsrPage() {
  const [deal, setDeal] = useState(null);                       // empty until the API answers
  useEffect(() => {                                             // effects run only in the browser
    fetch('/api/deal').then((r) => r.json()).then(setDeal);
  }, []);
  return <p>{deal ? deal.title : 'Loading...'}</p>;             // HTML starts as "Loading..."
}

// ---- pages/ssr.js : SSR (fresh on every request) ----
export async function getServerSideProps() {
  const deal = await getDeal();                                 // hypothetical server helper
  return { props: { deal } };                                   // HTML already contains the deal
}

// ---- pages/ssg.js : SSG (built once) ----
export async function getStaticProps() {
  return { props: { deal: await getDeal() } };                  // frozen until the next build
}

// ---- pages/isr.js : ISR (SSG + background refresh) ----
export async function getStaticProps() {
  return { props: { deal: await getDeal() }, revalidate: 60 };  // at most 60s old
}
```

## 💻 Code Example — Advanced

```jsx
// A "hybrid" product page: static shell (ISR) + live price (CSR) + user data (SSR elsewhere)
// pages/products/[id].js
import useSWR from 'swr';                                       // client data fetching library (or TanStack Query)
import { getProduct, getTopIds } from '../../lib/catalog';      // hypothetical server helpers

const fetcher = (url) => fetch(url).then((r) => r.json());      // simple fetcher for SWR

export default function ProductPage({ product }) {
  // CSR part: live stock/price refreshed in the browser every 30s,
  // while SEO-critical content (title, description) is already in the static HTML
  const { data: live } = useSWR(`/api/stock/${product.id}`, fetcher, {
    refreshInterval: 30000,                                     // poll every 30 seconds
    fallbackData: { price: product.price, inStock: true },      // show static price immediately
  });

  return (
    <article>
      <h1>{product.name}</h1>                                   {/* static: good for SEO */}
      <p>{product.description}</p>                              {/* static */}
      <p>Price: Rs {live.price}</p>                             {/* live: updates after hydration */}
      <p>{live.inStock ? 'In stock' : 'Out of stock'}</p>
    </article>
  );
}

// ISR: pre-build best sellers, generate others on demand, refresh every 10 minutes
export async function getStaticPaths() {
  const ids = await getTopIds(100);
  return { paths: ids.map((id) => ({ params: { id: String(id) } })), fallback: 'blocking' };
}
export async function getStaticProps({ params }) {
  const product = await getProduct(params.id);
  if (!product) return { notFound: true, revalidate: 60 };      // 404, check again in a minute
  return { props: { product }, revalidate: 600 };
}
```

---

## 🟠 Next.js Connection

In the **App Router** you do not pick "SSR" or "SSG" with named functions. Next.js decides based on what the route uses. A route is **static** by default; it becomes **dynamic (SSR)** if it uses `cookies()`, `headers()`, `searchParams`, uncached `fetch`, or `dynamic = 'force-dynamic'`. ISR is `revalidate`. CSR is a Client Component (`'use client'`) that fetches in `useEffect` or with TanStack Query. Streaming with Suspense lets one page mix static and dynamic parts.

```jsx
// app/products/[id]/page.jsx (Next.js 14/15) : same hybrid idea
import { Suspense } from 'react';
import LiveStock from './LiveStock';                            // 'use client' component (CSR part)
import { getProduct } from '@/lib/catalog';

export const revalidate = 600;                                  // ISR for the static part

export default async function Page({ params }) {
  const { id } = await params;                                  // Next.js 15: Promise
  const product = await getProduct(id);                         // server-rendered at build / revalidate
  return (
    <article>
      <h1>{product.name}</h1>                                   {/* static HTML */}
      <Suspense fallback={<p>Checking stock...</p>}>
        <LiveStock id={id} />                                   {/* client-side, live */}
      </Suspense>
    </article>
  );
}
```
Version-dependent: the default caching of `fetch` and route handlers changed between Next.js 14 and 15; read the build output (`○` static, `ƒ` dynamic) to see what you actually got.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using SSR for everything "to be safe"
✅ **Correct:** Prefer SSG/ISR for public, shared content. SSR adds server cost and latency on every visit.

```jsx
// Wrong: a blog article re-rendered for each reader
export async function getServerSideProps() { return { props: { post: await getPost() } }; } // ❌

// Right
export async function getStaticProps() { return { props: { post: await getPost() }, revalidate: 300 }; } // ✅
```

❌ **Mistake 2:** Using CSR for public pages that need SEO
✅ **Correct:** Crawlers may not wait for your fetch. Render the important content in HTML (SSR, SSG or ISR).

```jsx
// Wrong: Google may index "Loading..." instead of the menu
useEffect(() => { fetch('/api/menu').then(r => r.json()).then(setMenu); }, []); // ❌ for SEO pages

// Right: fetch on the server so the menu is in the initial HTML
export async function getStaticProps() { return { props: { menu: await getMenu() }, revalidate: 300 }; } // ✅
```

❌ **Mistake 3:** Thinking ISR makes data real-time
✅ **Correct:** ISR is "eventually fresh": the first visitor after expiry still sees the old page. For second-level freshness use SSR, CSR polling or on-demand revalidation.

```jsx
// Wrong: a live auction price with revalidate: 60
return { props: { bid }, revalidate: 60 };                      // ❌ up to 60+ seconds old

// Right: static shell + live client data (or SSR)
// useSWR('/api/bid', fetcher, { refreshInterval: 2000 })       // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
// app/dashboard/page.jsx (App Router, Next.js 14/15)
import { cookies } from 'next/headers';

export const revalidate = 60;                      // ISR setting on the route

export default async function Dashboard() {
  const theme = (await cookies()).get('theme')?.value ?? 'light'; // reads the request cookie
  return <p>Theme: {theme}</p>;
}
// Question: is this page ISR (static, refreshed every 60s) or SSR? What does the build output show?
```
**Answer:** It is **SSR (dynamic)**. Calling `cookies()` is a dynamic API: the value exists only per request, so Next.js cannot pre-render the route, and it opts the whole route into dynamic rendering at request time. In this case the `revalidate = 60` setting has no practical effect for the HTML, because a dynamic route has no cached page to revalidate. The build output marks the route as `ƒ (Dynamic)` instead of `○ (Static)`. Fix: if you want a static page, move the cookie-dependent part into a Client Component (read it on the client) or wrap only that part in a Suspense boundary so the rest stays cheap. Lesson: in the App Router, one dynamic API call decides the rendering mode of the route (in Next.js 15 `cookies()` is async; in 14 it is sync, version-dependent).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between SSR and SSG?
A1: SSR renders HTML on the server for every request, so data is always fresh and can be personalised, but each hit costs server time. SSG renders HTML once at build time and serves a static file from a CDN: fastest and cheapest, but data is frozen until the next build.

Q2: What is ISR and why use it?
A2: Incremental Static Regeneration serves a static page but regenerates it in the background after a `revalidate` interval or when you call on-demand revalidation. You get static speed with bounded staleness, and you can generate new pages without rebuilding the entire site.

Q3: Why is CSR bad for SEO and first load, and when is it still the right choice?
A3: The browser first receives almost empty HTML, then downloads JavaScript, fetches data and renders, so first contentful paint is later and crawlers may see little content. It is still a good choice for private, interactive areas behind login (dashboards, cart, chat) where SEO does not matter and data is user-specific.

Q4: How would you choose a strategy for a news site?
A4: Home page and category pages: ISR with a short `revalidate` or on-demand revalidation when editors publish. Article pages: ISR/SSG with `getStaticPaths` (or `generateStaticParams`). Comments and live scores: CSR. Subscriber-only personalised pages: SSR. Mix them per route.

Q5: How are these represented in the App Router?
A5: There are no named functions. Static rendering is the default for routes without dynamic APIs; using `cookies()`, `headers()`, `searchParams` or uncached fetch makes it dynamic (SSR); `revalidate` gives ISR; Client Components that fetch in the browser give CSR; Suspense and streaming mix them within one page.

---

## 🔷 When to Use + When Not to Use
✅ **Use each when:**
- **SSG:** content is the same for all and changes rarely (docs, landing pages)
- **ISR:** content is shared but updates sometimes (products, news, listings)
- **SSR:** content depends on the request or must be exact now (orders, personalised feed)
- **CSR:** private, highly interactive UI where SEO does not matter (dashboard, cart, editor)

❌ **Avoid when:**
- SSR for static content (wasted compute), SSG for live data (stale)
- CSR for public SEO pages, ISR when you need second-level accuracy
- Pure SSG for millions of pages that change often (build time explodes)

---

## 📊 Visual Diagram

```
                 WHEN is HTML made?     WHERE?         DATA FRESHNESS      SPEED (TTFB)
  ───────────────────────────────────────────────────────────────────────────────────
  SSG            build time             build server   frozen until deploy  fastest (CDN)
  ISR            build + background     server/CDN     fresh within N sec   very fast
  SSR            every request          server         always fresh         slower
  CSR            in the browser         user's device  fresh after fetch    fast shell, slow content

  Timeline of what the user sees:

  SSG/ISR : [content ........................................]  (HTML already complete)
  SSR     : [wait for server][content .......................]  (complete, a bit later)
  CSR     : [shell][wait for JS][spinner][content ...........]  (content arrives last)

  Re-render behavior: SSR/SSG/ISR pages hydrate once; CSR renders on the client at
  least twice (loading state, then data).
  Performance: prefer static (SSG/ISR) → then SSR → use CSR for private interactions.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSR | HTML built in the browser | Browser में HTML बनाना |
| SSR | HTML built on the server per request | हर request पर server पर HTML बनाना |
| SSG | HTML built once at build time | Build time पर एक बार HTML बनाना |
| ISR | Static pages refreshed in background | Static pages का background में refresh |
| TTFB | Time to first byte | पहला byte आने का समय |
| Hydration | Attaching JS to server HTML | Server HTML में JS जोड़ना |
| Streaming | Sending HTML in pieces | HTML को टुकड़ों में भेजना |
| On-demand revalidation | Manual page refresh trigger | Page को ख़ुद refresh करवाना |

---

## ⚡ 3-Line Summary
**English:**
1. CSR builds in the browser, SSR on each request, SSG once at build time, and ISR is SSG that refreshes in the background.
2. Choose by data freshness, personalisation, SEO needs and scale; real apps mix all four per page.
3. In the App Router the choice is implicit (static by default, dynamic APIs make it SSR, `revalidate` makes ISR, `'use client'` data fetching is CSR).

**Hindi:**
1. CSR browser में बनाता है, SSR हर request पर, SSG build time पर एक बार, और ISR वह SSG है जो background में refresh होता है।
2. Data की freshness, personalisation, SEO की ज़रूरत और scale देखकर चुनो; असली apps में हर page पर चारों मिलाकर इस्तेमाल होते हैं।
3. App Router में चुनाव अपने-आप तय होता है (default static, dynamic APIs से SSR, `revalidate` से ISR, `'use client'` में fetching यानी CSR)।

---

## ➡️ Next Topic
**176. API Routes in Next.js** — अब तक frontend rendering देखी; अब Next.js में ही backend endpoints (`pages/api` और App Router के Route Handlers) कैसे बनाते हैं, ताकि अलग server के बिना API मिल जाए।
