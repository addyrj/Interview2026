# Next.js Cheatsheet (Topics 166-190)

Condensed from `08-nextjs/`. Version-dependent facts are flagged. Default target: App Router, Next.js 14/15.

---

## 166-167. What Next.js is, and vs React
- Next.js = React + SSR + file-based routing + API routes + image optimization: the production-ready React framework.
- Plain React (Vite) sends an empty shell and renders in the browser; Next.js sends real HTML first (better SEO and first paint), then hydrates.
- Choose Next.js for public, SEO-heavy apps; Vite + React for simple private dashboards. Not every page is server-rendered: choose per route.

```jsx
// app/page.jsx: Server Component, no 'use client'
export default async function HomePage() {
  const featured = await fetch('https://api.example.com/products/featured').then((r) => r.json());
  return <main>{featured.map((p) => <p key={p.id}>{p.name}</p>)}</main>;
}
```
Trap: using `useState` or `onClick` in an App Router file fails until you add `'use client'`.

> हिंदी: Next.js = React + routing + server rendering; server से HTML आता है फिर hydrate होता है।

---

## 168. App Router vs Pages Router
- Pages Router (`pages/`): `getServerSideProps` / `getStaticProps`. App Router (`app/`): async Server Components.
- App Router adds nested layouts, `loading.js`/`error.js`, streaming, Server Actions, less JS.
- They can coexist during migration but one URL cannot exist in both (build error). New projects: App Router.
- `layout.js` persists and keeps state; `template.js` re-mounts on each navigation.

```jsx
// Pages Router
export async function getServerSideProps({ params }) {
  const res = await fetch(`https://api.example.com/r/${params.slug}`);
  return { props: { restaurant: await res.json() } };
}
```

> हिंदी: नए project में App Router, पुराने में Pages Router; दोनों में एक ही URL नहीं हो सकता।

---

## 169. File-based routing
- Folders in `app/` are URL segments; `page.js` makes a segment public.
- `[id]` dynamic, `[...slug]` catch-all, `[[...slug]]` optional catch-all, `(group)` grouping. Priority: static, dynamic, catch-all, optional catch-all.
- Version flag: in Next.js 15, `params` is a Promise (`await params`); in 14 it is a plain object.
- Special files: `not-found.js` (use `notFound()`), `middleware.js` (renamed `proxy` in very recent versions, version-dependent).

```jsx
import Link from 'next/link';
export default async function Product({ params }) {
  const { id } = await params; // Next.js 15
  return <Link href="/products">Back to {id}</Link>;
}
```
Trap: `/blog/new` goes to `app/blog/new/page.js`, not `[slug]`.

> हिंदी: Folder ही URL है; static route dynamic से पहले match होता है।

---

## 170. Server Components in Next.js
- Render only on the server, can be `async`, send no JavaScript; secrets and DB access stay safe.
- Cannot use state, effects, event handlers, browser APIs or context consumers.
- Pass serializable props, use Suspense for streaming.

```jsx
export default async function RestaurantsPage() {
  const res = await fetch('https://api.example.com/restaurants', {
    headers: { Authorization: `Bearer ${process.env.API_SECRET}` }, // stays on server
    next: { revalidate: 300 },
  });
  const restaurants = await res.json();
  return <ul>{restaurants.map((r) => <li key={r.id}>{r.name}</li>)}</ul>;
}
```
Trap: `console.log` in a Server Component prints in the server terminal, not the browser.

> हिंदी: Server Component browser को JavaScript नहीं भेजता, data सीधे वहीं fetch होता है।

---

## 171. Client Components
- `'use client'` (first statement in the file) marks a client boundary; the file and its imports join the client bundle.
- They are still pre-rendered to HTML on the server, then hydrated. Browser-only code goes in effects.
- Keep the boundary low; pass Server Components in as `children`; never pass plain functions across the boundary.
- Providers: a client wrapper file that renders the Provider and accepts `children`.

```jsx
'use client';
import { useState } from 'react';
export default function QuantityStepper({ price }) {
  const [qty, setQty] = useState(0);
  return <button onClick={() => setQty(qty + 1)}>Rs {qty * price}</button>;
}
```

> हिंदी: `'use client'` का मतलब सिर्फ browser नहीं; server पर भी पहले HTML बनता है।

---

## 172. getServerSideProps (Pages Router)
- Runs only on the server on every request; returns `props` (or `notFound` / `redirect`).
- Good for personalised, always-fresh data; cost is slower TTFB and weak CDN caching.
- Props must be serialisable (send a string, not a `Date`); do not call your own API route from it.
- Module-level variables are shared between users (same Node process).

```jsx
export async function getServerSideProps({ req }) {
  return { props: { renderedAt: new Date().toISOString(), userAgent: req.headers['user-agent'] ?? 'unknown' } };
}
```

> हिंदी: हर request पर server पर चलता है, इसलिए data हमेशा ताज़ा पर थोड़ा धीमा।

---

## 173. getStaticProps and ISR (Pages Router)
- Runs at build time (and on revalidation) to make a static page served by a CDN.
- `revalidate: N` gives ISR: after N seconds the next visitor still gets the stale page and triggers background regeneration.
- It cannot see the request; use `getServerSideProps` for personal data.

```jsx
export async function getStaticProps() {
  const offers = await fetch('https://example.com/api/offers').then((r) => r.json());
  return { props: { offers }, revalidate: 10 };
}
```

> हिंदी: Build के समय बना पेज सबको मिलता है, `revalidate` से पीछे से ताज़ा होता रहता है।

---

## 174. getStaticPaths / generateStaticParams
- `getStaticPaths` lists dynamic URLs to pre-build, with `fallback`: `false` (404), `true` (shell then data), `'blocking'` (render, then cache).
- App Router replacement: `generateStaticParams` plus `dynamicParams` (true = render unknown params on demand, false = 404).
- Params must be strings; handle `router.isFallback`.

```jsx
export async function getStaticPaths() {
  return { paths: [{ params: { id: '1' } }, { params: { id: '2' } }], fallback: 'blocking' };
}
```

> हिंदी: कौन से URL पहले से बनाने हैं यह बताता है; बाकी के लिए `fallback` तय करता है।

---

## 175. SSR vs SSG vs ISR vs CSR
- CSR builds in the browser, SSR per request, SSG once at build, ISR is SSG refreshing in the background.
- App Router makes the choice implicit: static by default, dynamic APIs make it SSR, `revalidate` makes ISR, client fetching is CSR.
- Trap: calling `cookies()` makes the whole route dynamic, so `revalidate = 60` has no effect on its HTML.
- Check the build output (`○` static, `ƒ` dynamic).

| Mode | When rendered | Use for |
|---|---|---|
| CSR | browser | private dashboards |
| SSR | each request | personalised, fresh |
| SSG | build | marketing, docs |
| ISR | build + background refresh | news, catalogs |

> हिंदी: असली app में चारों मिलाकर इस्तेमाल होते हैं, हर page के हिसाब से चुनो।

---

## 176. Route Handlers (API routes)
- `route.js` exports `GET`, `POST` etc. using Web `Request` and `Response`; replaces `pages/api`.
- Validate input, return right status codes; Server Components should call the DB or a shared function, not your own API.
- A `route.js` and `page.js` cannot share one segment. In Next.js 15+ the `{ params }` argument is a Promise.

```jsx
import { NextResponse } from 'next/server';
export async function POST(request) {
  const body = await request.json();
  if (!body.name) return NextResponse.json({ error: 'name required' }, { status: 400 });
  return NextResponse.json({ id: 1, ...body }, { status: 201 });
}
```

> हिंदी: Backend वाला endpoint उसी Next.js app के अंदर `route.js` में बनता है।

---

## 177. Middleware
- Runs before a request reaches the route (Edge runtime by default); can redirect, rewrite, set headers or cookies.
- Use `matcher` and keep it light. It is a first filter only; verify real authorization in the data layer.
- Redirect vs rewrite: redirect changes the address bar, rewrite does not.
- Trap: redirecting `/login` to `/login` loops forever.

```jsx
import { NextResponse } from 'next/server';
export function middleware(request) {
  if (!request.cookies.get('token')?.value) return NextResponse.redirect(new URL('/login', request.url));
  return NextResponse.next();
}
export const config = { matcher: ['/orders/:path*', '/profile/:path*'] };
```
Version flag: file is being renamed `proxy` in very recent versions.

> हिंदी: Page पहुँचने से पहले का पहरेदार, पर असली authorization data layer में करो।

---

## 178. next/image
- Serves resized, modern-format, lazy-loaded images with reserved space (good for LCP and CLS).
- Needs `width`/`height` (or `fill` with `sizes`); remote hosts must be allowed in `images.remotePatterns`.
- `priority` only for the hero image. Version flag: `priority` is being replaced by `preload` in Next.js 16.

```jsx
import Image from 'next/image';
<Image src="https://images.example.com/biryani.jpg" alt="Chicken biryani" width={400} height={300} />;
```

> हिंदी: `next/image` छोटी, आधुनिक format की और lazy images देता है, layout नहीं हिलता।

---

## 179. next/font
- Self-hosts fonts at build time (no runtime request to Google) and adjusts fallback to avoid layout shift.
- Call the font function at module scope; apply via `className` or a `variable`. Writing `fontFamily: 'Inter'` does not use it.

```jsx
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], display: 'swap' });
export default function RootLayout({ children }) {
  return <html lang="en" className={inter.className}><body>{children}</body></html>;
}
```

> हिंदी: Font build में ही host हो जाता है, इसलिए तेज़ और बिना shift के।

---

## 180. Metadata and SEO
- Export `metadata` or async `generateMetadata` from a Server Component layout/page; tags are in the first HTML.
- Child overrides parent per top-level key (shallow merge); set `metadataBase`, canonical, Open Graph; add `sitemap.js`, `robots.js`.
- `title.template: '%s | MyShop'` formats child titles. Wrap DB calls in React `cache()` to avoid duplicates.

```jsx
export const metadata = { title: { template: '%s | MyShop', default: 'MyShop' } };
export async function generateMetadata({ params }) {
  const { slug } = await params; // Next.js 15
  return { title: slug };
}
```

> हिंदी: SEO tags server पर बनते हैं, इसलिए crawler को JavaScript नहीं चलाना पड़ता।

---

## 181. loading.js, error.js, not-found.js
- `loading.js` wraps the page in `<Suspense>`; `error.js` is an error boundary and must be a Client Component; `notFound()` renders `not-found.js`.
- `error.js` cannot catch errors from the layout beside it; use a parent boundary or `global-error.js`.
- `reset()` re-renders the segment.

```jsx
'use client';
export default function Error({ error, reset }) {
  return <button onClick={() => reset()}>Try again</button>;
}
```

> हिंदी: Loading और error UI के लिए अलग फाइलें, बिना हाथ से state लिखे।

---

## 182-183. Parallel and intercepting routes
- Parallel: `@slot` folders render several independent pages in one layout (slots are not in the URL); add `default.js` to avoid 404 on hard navigation.
- Intercepting: shows a route inside the current layout (a modal) on soft navigation; refresh or direct visit shows the full page.
- Close modals with `router.back()`; conventions count route segments, not folders.

```text
app/dashboard/
  layout.jsx
  page.jsx          (children slot)
  @revenue/page.jsx
  @orders/page.jsx
```

> हिंदी: Slots से dashboard के कई हिस्से स्वतंत्र चलते हैं; refresh करने पर modal नहीं, पूरा page दिखता है।

---

## 184. Server Actions
- `'use server'` async functions that run on the server, usable from forms or handlers; no API boilerplate; support progressive enhancement and revalidation.
- They are public endpoints: always authenticate, authorize and validate inside them.
- `useActionState`, `useFormStatus`, `useOptimistic` for form state. Version flag: `useActionState` is React 19; in React 18 canary it was `useFormState`. `cookies()` is async in Next.js 15+.

```jsx
'use server';
export async function sendFeedback(formData) {
  const message = formData.get('message');
  if (!message || message.length < 3) return;
}
```

> हिंदी: Form सीधे server function को बुलाता है, पर वह public endpoint है, जाँच ज़रूर करो।

---

## 185. Prisma + PostgreSQL
- Define schema once, get typed queries and migrations; use only in server code.
- Trap: hot reload creates a new `PrismaClient` each save and exhausts connections; store one on `globalThis` in development.
- Use `select`, transactions, pooling, `migrate deploy` in production.

```jsx
import { PrismaClient } from '@prisma/client';
const globalForPrisma = globalThis;
export const prisma = globalForPrisma.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

> हिंदी: Dev में हर save पर नया client बनता है, इसलिए `globalThis` पर एक ही रखो।

---

## 186. Authentication (Auth.js / NextAuth)
- Providers, session cookies, helpers `auth()`, `signIn`, `signOut`. Data flows `authorize()/user` -> `jwt` callback -> `session` callback.
- Trap: `session.user.role` is `undefined` if the `jwt` callback never copied `role` to the token.
- Protect with middleware plus server checks. Version flag: Auth.js v5 (`next-auth@beta`) APIs and env names (`AUTH_SECRET`) are version-dependent.

> हिंदी: Role session तक पहुँचाने के लिए पहले `jwt` फिर `session` callback में कॉपी करो।

---

## 187. Performance
- Measure Core Web Vitals: LCP (good under 2.5 s), INP (under 200 ms, replaced FID), CLS (under 0.1).
- Ship less JS with Server Components and small client leaves; fetch in parallel; stream with Suspense; lazy-load with `next/dynamic`; use `next/script` strategies (`afterInteractive` default, `lazyOnload`).
- Trap: `cookies()`/`headers()` in the root layout makes every route dynamic.

```jsx
const [a, b] = await Promise.all([getA(), getB()]); // parallel, not sequential
```

> हिंदी: पहले मापो, फिर JavaScript घटाओ; root layout में `cookies()` पूरे site को धीमा कर देता है।

---

## 188-189. Deployment and environment variables
- Deploy: `next build`, then Vercel (full features), a Node/Docker server (self-managed cache and HTTPS), or `output: 'export'` static (frozen at build, no dynamic).
- Env: no prefix = server only; `NEXT_PUBLIC_` = inlined into browser JS at build time, so changing it needs a rebuild.
- Never put secrets in `NEXT_PUBLIC_`; import `server-only` in sensitive modules.
- File order: real env, `.env.$(NODE_ENV).local`, `.env.local` (skipped in test), `.env.$(NODE_ENV)`, `.env`.

```jsx
'use client';
console.log(process.env.API_KEY); // undefined in the browser: no NEXT_PUBLIC_ prefix
```

> हिंदी: `NEXT_PUBLIC_` वाली value सबको दिखती है, secret उसमें कभी मत रखो।

---

## 190. Caching strategies
- Four caches: Request Memoization (one render), Data Cache (fetch across requests), Full Route Cache (static HTML + RSC payload), Router Cache (client).
- Freshness: `revalidate` (time), `revalidateTag` / `revalidatePath` (on demand), `cache: 'no-store'` or `dynamic = 'force-dynamic'` (opt out).
- Version flag (classic trap): Next.js 14 cached `fetch` and GET route handlers by default; Next.js 15 does not. Set caching explicitly. `unstable_cache` vs `use cache` is version-dependent.
- Request memoization only merges calls with identical URL and options.

```jsx
const res = await fetch('https://api.example.com/products', { next: { revalidate: 60 } });
```

> हिंदी: Next.js 14 और 15 के caching defaults अलग हैं, इसलिए हमेशा साफ़ लिखो और निजी data cache मत करो।
