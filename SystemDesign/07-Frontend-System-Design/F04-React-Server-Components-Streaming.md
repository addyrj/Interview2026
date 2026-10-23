# F04. React Server Components + Streaming (Next.js App Router)
# हिंदी में: React Server Components — ऐसे components जो सिर्फ़ सर्वर पर चलते हैं, ब्राउज़र को उनका JavaScript नहीं भेजा जाता; Streaming — पेज को टुकड़ों में भेजना ताकि धीमे हिस्से का इंतज़ार किए बिना बाक़ी पेज तुरंत दिखे

---

## 🔵 Simple Definition (English)
**React Server Components (RSC)** are React components that **run only on the server** (at build time or request time). They can be `async`, read databases/APIs/secrets directly, and their **JavaScript is never sent to the browser**. Only their rendered output (a serialized "RSC payload") is sent.
**Client Components** (marked with `'use client'`) are the interactive parts (state, effects, event handlers). They are pre-rendered to HTML and then **hydrated** in the browser.
**Streaming** sends the page progressively: the shell is sent immediately and slower parts wrapped in `<Suspense>` are streamed in when their data is ready.
**Server Actions** (`'use server'`) are server functions you can call directly from forms/buttons without writing an API route.
In Next.js, the **App Router** (`app/` directory) uses RSC by default.

## 🔵 सरल परिभाषा (Hindi)
React Server Components सिर्फ़ सर्वर पर चलते हैं — सीधे DB/API पढ़ सकते हैं, और उनका JavaScript ब्राउज़र में नहीं जाता, सिर्फ़ उनका नतीजा जाता है।
Client Components (`'use client'`) वो हिस्से हैं जिनमें state, clicks, effects हैं — इनका JS ब्राउज़र में जाता है।
Streaming = पहले पेज का ढाँचा तुरंत भेजो, धीमे हिस्से (`<Suspense>` में) तैयार होते ही बाद में भेजो। Server Actions = form से सीधे सर्वर function चलाना, अलग API बनाए बिना।

---

## 🔴 Problem it Solves
Classic React (CSR or SSR with full hydration) has problems:
- **Huge JS bundles**: every component (even static ones like a product description or markdown renderer) ships JS and hydrates, which is slow on low-end phones.
- **Client-side waterfalls**: component renders → `useEffect` fetches → child renders → fetches again… each round trip from a slow mobile network.
- **Boilerplate**: an API route plus fetch plus loading state for every piece of data.
- **Secrets & heavy libraries** can't be used in the browser (DB clients, markdown/syntax highlighters, date libraries add KBs).
- **All-or-nothing SSR**: the whole page waits for the slowest query before sending any HTML.

RSC moves non-interactive work to the server (zero client JS for it). Streaming removes the "wait for everything" problem.

## 🔴 यह क्यों बना? (Hindi)
पुराने React में हर component का JS ब्राउज़र जाता और hydrate होता — बड़ा bundle, धीमे फ़ोन पर सुस्ती; useEffect से डेटा लाने में एक के बाद एक round trip (waterfall); हर डेटा के लिए API route + loading state; secrets और भारी libraries ब्राउज़र में नहीं चल सकतीं; और SSR में पूरा पेज सबसे धीमे query का इंतज़ार करता।
RSC non-interactive काम सर्वर पर ले जाता है (ज़ीरो JS), और streaming "सब तैयार होने तक रुको" वाली समस्या हटाता है।

---

## 🟢 How it Works — Step by Step

### Server vs client component tree

```
app/product/[slug]/page.tsx            (Server Component — default)
 ├─ <ProductInfo />                    Server: reads DB, renders markdown  → 0 KB JS
 ├─ <PriceAndStock />                  Server: fetches price (no-store)    → 0 KB JS
 ├─ <AddToCartButton productId=… />    'use client': onClick, useState     → JS shipped + hydrated
 ├─ <Suspense fallback={<Skeleton/>}>
 │    <Reviews />                      Server: slow API, streamed later    → 0 KB JS
 └─ <ImageGallery images=… />          'use client': swipe, zoom           → JS shipped

Only the 'use client' islands (and their imports) go into the browser bundle.
```

### The rules

```
Server Components:                         Client Components ('use client' at top of file):
✓ async/await data directly (DB, fetch)    ✓ useState, useEffect, useContext, event handlers
✓ secrets, server-only libs                 ✓ browser APIs (window, localStorage)
✗ no useState/useEffect/onClick             ✗ cannot be async; cannot import server-only code
✗ no browser APIs                           ✓ can receive Server Components as children/props

Boundary rules:
- 'use client' marks an ENTRY POINT; everything imported by that file becomes client code too
  → push 'use client' to the LEAVES (small interactive components), not the page root
- Props passed Server → Client must be SERIALIZABLE (strings, numbers, plain objects, arrays,
  Dates, Promises, Server Actions) — NOT regular functions or class instances
- A Client Component can render a Server Component only if it's passed in as children/props
- import 'server-only' in modules that must never reach the client (DB access, secrets)
```

### What travels over the wire

```
1. Request /product/iphone-16
2. Server renders the tree:
   - Server Components execute (await DB/API)
   - Client Components are rendered to HTML too (SSR), and marked as "client references"
3. Response stream contains:
   a) HTML (for fast first paint, SEO)
   b) RSC payload (serialized tree: rendered server output + references to client JS chunks + props)
4. Browser paints HTML → downloads only client-component chunks → hydrates islands
5. On client-side navigation (<Link>), the router fetches ONLY the RSC payload for the new route
   (no full HTML reload) and merges it, preserving client state
```

### Streaming with Suspense

```
Time ─────────────────────────────────────────────────────────────►
Server: [shell + header + product info]──flush──► ... [reviews ready]──flush──►
Browser:   paint shell + product (fast LCP)          swap skeleton → reviews HTML
                    hydrate interactive islands as their JS arrives
                    (selective hydration: React hydrates what the user interacts with first)

app/product/[slug]/loading.tsx  → automatic <Suspense> boundary for the whole route segment
<Suspense fallback={...}>       → finer-grained boundaries inside a page
Avoid waterfalls: start independent fetches in parallel (Promise.all) or in sibling components
```

### Server Actions (mutations without API routes)

```
Form (Server or Client Component) ──POST (framework-managed)──► 'use server' function
   → validate input (zod), check auth (never trust client), write DB
   → revalidatePath('/cart') / revalidateTag('cart') → fresh RSC payload returned
   → UI updates; works even before JS loads (progressive enhancement) for <form action={…}>
Security: Server Actions are public HTTP endpoints → always authenticate + authorize + validate
```

### Caching in the App Router (concepts — defaults changed between Next.js versions)

```
Request memoization  → same fetch() in one render deduped
Data cache           → fetch results cached across requests (opt-in in Next 15+: cache: 'force-cache',
                       next: { revalidate, tags })
Full route cache     → statically rendered routes cached as HTML + RSC payload (SSG/ISR)
Router cache (client)→ visited route payloads kept in memory for back/forward navigation
Newer: 'use cache' directive (Cache Components) to cache a component/function explicitly
Always check the docs for your exact Next.js version.
```

## 🟢 कैसे काम करता है? (Hindi)
1. App Router में हर component default रूप से Server Component — async होकर सीधे DB/API से डेटा, JS ब्राउज़र नहीं जाता।
2. जहाँ click/state चाहिए वहाँ छोटा `'use client'` component (पत्ती पर, पूरे पेज पर नहीं) — सिर्फ़ उसी का JS जाता है और hydrate होता है।
3. सर्वर HTML + RSC payload भेजता है; ब्राउज़र HTML तुरंत दिखाता है; बाद की navigation में सिर्फ़ payload आता है।
4. धीमे हिस्से `<Suspense>` में — पहले ढाँचा दिखता है, reviews जैसे हिस्से तैयार होते ही stream होकर आ जाते हैं; `loading.tsx` अपने-आप boundary बनाता है।
5. Server Actions से form सीधा सर्वर function चलाता है — पर ये भी public endpoint हैं, इसलिए auth और validation ज़रूरी; बदलाव के बाद revalidatePath/Tag।

---

## 🟡 Real World Example

**Next.js App Router** — production-stable since Next.js 13.4 (2023). React 19 made Server Components and Server Actions part of stable React. Vercel's own sites and many e-commerce and content companies use App Router so that static content (descriptions, CMS blocks, markdown) ships zero JS while carts and filters stay interactive.

**Shopify Hydrogen v1 (2022)** — was an early production adopter of RSC for storefronts. It later moved to Remix in 2023, partly because of RSC maturity at the time. This shows the trade-off: powerful, but the ecosystem and tooling were young.

**Illustrative example (Swiggy-style restaurant page):** the menu text, images and restaurant info render as Server Components from the catalog API. The "Add +" buttons and cart drawer are small Client Components. Ratings and reviews stream in under `<Suspense>`. The JS shipped to a ₹8,000 Android phone drops to just the interactive parts.

## 🟡 Real Example Hindi में
Next.js App Router 2023 से production-ready है और React 19 में Server Components stable हो गए — static content का JS ज़ीरो, सिर्फ़ cart/filters interactive।
उदाहरण (Swiggy जैसा menu page): menu, फ़ोटो, restaurant जानकारी Server Components; "Add +" बटन और cart छोटे Client Components; reviews Suspense से बाद में stream — सस्ते Android फ़ोन पर बहुत कम JS।

---

## 🟠 My Stack Example

### Server Component page with parallel data + streaming (Next.js 15+)
```tsx
// app/restaurant/[id]/page.tsx  — Server Component
import { Suspense } from 'react';
import { getRestaurant, getMenu } from '@/lib/catalog';       // server-only module
import AddToCartButton from './AddToCartButton';             // client island
import Reviews from './Reviews';

export default async function RestaurantPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [restaurant, menu] = await Promise.all([getRestaurant(id), getMenu(id)]);  // parallel, no waterfall

  return (
    <main>
      <h1>{restaurant.name}</h1>
      <p>{restaurant.cuisines.join(', ')} · ⭐ {restaurant.rating}</p>
      <ul>
        {menu.items.map((item) => (
          <li key={item.id}>
            <span>{item.name} — ₹{item.price}</span>
            <AddToCartButton itemId={item.id} price={item.price} />   {/* serializable props only */}
          </li>
        ))}
      </ul>
      <Suspense fallback={<p>Loading reviews…</p>}>
        <Reviews restaurantId={id} />                                 {/* streamed when ready */}
      </Suspense>
    </main>
  );
}
```

```ts
// lib/catalog.ts
import 'server-only';                              // build error if imported into client code
export async function getMenu(id: string) {
  const res = await fetch(`${process.env.CATALOG_API}/restaurants/${id}/menu`, {
    headers: { Authorization: `Bearer ${process.env.CATALOG_TOKEN}` },   // secret stays on server
    next: { revalidate: 60, tags: [`menu-${id}`] },
  });
  if (!res.ok) throw new Error('menu fetch failed');                     // caught by error.tsx
  return res.json() as Promise<{ items: { id: string; name: string; price: number }[] }>;
}
```

### Client island
```tsx
// app/restaurant/[id]/AddToCartButton.tsx
'use client';
import { useTransition } from 'react';
import { addToCart } from './actions';

export default function AddToCartButton({ itemId, price }: { itemId: string; price: number }) {
  const [pending, startTransition] = useTransition();
  return (
    <button disabled={pending} aria-busy={pending}
            onClick={() => startTransition(() => addToCart(itemId))}>
      {pending ? 'Adding…' : `Add + ₹${price}`}
    </button>
  );
}
```

### Server Action with validation + auth
```ts
// app/restaurant/[id]/actions.ts
'use server';
import { z } from 'zod';
import { revalidateTag } from 'next/cache';
import { getSession } from '@/lib/auth';

const Input = z.string().uuid();
export async function addToCart(itemId: string) {
  const session = await getSession();                 // never trust the client
  if (!session) throw new Error('Unauthorized');
  const id = Input.parse(itemId);
  await fetch(`${process.env.CART_API}/carts/${session.userId}/items`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': crypto.randomUUID() },
    body: JSON.stringify({ itemId: id, qty: 1 }),
  });
  revalidateTag(`cart-${session.userId}`);            // cart badge re-renders with fresh data
}
```

### Route-level loading & error boundaries
```
app/restaurant/[id]/
  page.tsx        ← Server Component
  loading.tsx     ← shown instantly while page awaits data (Suspense boundary)
  error.tsx       ← 'use client' error boundary with retry button
  not-found.tsx   ← notFound() from page → 404 UI
```

### Common mistakes to mention
```
❌ 'use client' at app/layout.tsx → whole app becomes client-side again
❌ awaiting fetches one after another in the same component (waterfall) → use Promise.all
❌ passing functions/class instances to client components → serialization error
❌ importing a DB client in a client component → use 'server-only'
❌ Server Action without auth/validation → it's a public endpoint
❌ huge context providers at the root forcing client rendering → wrap only where needed
```

### React Native note
```
RN apps don't use RSC in production today (experimental "server components" support is emerging in Expo Router).
Same principles apply: keep heavy logic & secrets on the backend/BFF, send screen-shaped data.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are React Server Components and how do they differ from SSR?**
A1: RSCs are components that execute only on the server and never ship their code to the client. Their output is serialized into an RSC payload that the client merges into the tree. SSR is about producing HTML on the server for the first load, but with classic SSR every component's JS still ships and hydrates. With RSC, server components contribute zero client JS, and only Client Components hydrate. They're complementary: Next.js SSRs both kinds to HTML for the first paint, and RSC reduces the bundle and hydration cost and also powers client navigations via payload fetches.

**Q2: How do you decide what should be a Server vs a Client Component?**
A2: Default to Server Components for anything non-interactive: data fetching, layout, text, lists, markdown, anything using secrets or heavy libraries. Use Client Components only where you need state, effects, event handlers, browser APIs or client-only libraries (carousels, forms with live validation, maps). Push the `'use client'` boundary down to the smallest leaf components, and pass Server Components as children into client wrappers when needed.

**Q3: How does streaming SSR improve performance?**
A3: Instead of waiting for all data before sending any HTML, the server immediately flushes the shell and fast sections, then streams HTML for each `<Suspense>` boundary as its data resolves, replacing the fallback in place. This improves TTFB, FCP and often LCP, because users see and can interact with the page while slow parts load. Selective hydration lets React prioritize hydrating the parts the user interacts with.

**Q4: What are Server Actions and what are their risks?**
A4: Functions marked `'use server'` that the client can invoke (via form actions or calls). The framework handles the HTTP request and serialization, and they can revalidate cached data so the UI refreshes. They reduce API boilerplate and support progressive enhancement for forms. Risks: they're publicly reachable endpoints, so you must authenticate, authorize and validate inputs, and handle idempotency and rate limiting. They also couple the frontend to the server code, so a separate public API may still be needed for mobile apps.

**Q5: What pitfalls exist with RSC?**
A5: Marking high-level components `'use client'` accidentally pulls large trees into the bundle. Sequential awaits create server-side waterfalls. Non-serializable props cause errors. Leaking server-only code is a risk (use `server-only`). Caching semantics are confusing and changed across Next.js versions (stale data or unexpected dynamic rendering). Third-party libraries that assume a browser need client wrappers. There's also a mental-model shift for teams, and debugging spans both server and client.

---

## 🔷 Trade-offs
✅ Less client JS, faster loads on slow devices, direct data access, fewer waterfalls, built-in streaming.
✅ Server Actions: simple mutations, progressive enhancement.
❌ More server work/cost; tied to frameworks (Next.js) and Node/edge runtimes.
❌ Learning curve: boundaries, serialization, caching rules; ecosystem libs need `'use client'`.
❌ Mobile apps still need a normal API (REST/GraphQL) — Server Actions don't replace it.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server Component | Runs only on server, no client JS | सिर्फ़ सर्वर पर चलने वाला |
| Client Component | Interactive, hydrated in browser | ब्राउज़र में interactive हिस्सा |
| 'use client' | Marks client boundary | client की सीमा |
| RSC payload | Serialized server-rendered tree | सर्वर से आया पेड़ का डेटा |
| Streaming | Sending HTML progressively | HTML टुकड़ों में भेजना |
| Suspense | Boundary with fallback while loading | लोड होते समय fallback |
| Selective hydration | Hydrate priority parts first | ज़रूरी हिस्सा पहले चालू |
| Server Action | Server function called from UI | UI से सर्वर function |
| Waterfall | Sequential dependent requests | एक के बाद एक request |
| server-only | Guard against client import | client में import रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. RSC run only on the server (async, direct data, secrets) and ship zero JS; `'use client'` islands handle interactivity.
2. Streaming with Suspense sends the shell immediately and slow sections later; Server Actions handle mutations (with auth + validation).
3. Push client boundaries to leaves, fetch in parallel, pass serializable props, and understand your framework's caching rules.

**Hindi:**
1. RSC सिर्फ़ सर्वर पर, ज़ीरो JS; `'use client'` वाले छोटे हिस्से interactive।
2. Suspense streaming से ढाँचा तुरंत, धीमे हिस्से बाद में; Server Actions से बदलाव (auth + validation के साथ)।
3. client सीमा पत्तियों पर, parallel fetch, serializable props, और caching नियम समझो।

---

## ➡️ Next Topic Suggestion
**F05. Core Web Vitals (LCP, INP, CLS)** — How do we measure whether a page is actually fast for real users? Next: Google's Core Web Vitals, what causes bad scores, how to fix them, and how to monitor them in production.
