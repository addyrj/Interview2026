# 190. Next.js Caching Strategies
# हिंदी में: Next.js Caching Strategies — App को तेज़ और सस्ता बनाना

---

## 🔵 Simple Definition (English)
**Caching** in Next.js means saving the result of work (a fetch response, a rendered page, a React Server Component payload) so the next request can reuse it instead of repeating the work. The App Router has several cache layers, and you control them with `revalidate`, tags, `cache` options and `revalidatePath` / `revalidateTag`.

## 🔵 सरल परिभाषा (Hindi)
Next.js में **Caching** का मतलब है काम का नतीजा (fetch response, rendered page, React Server Component payload) सहेज लेना, ताकि अगली request वही काम दोबारा न करे। App Router में कई cache layers हैं, और आप इन्हें `revalidate`, tags, `cache` options और `revalidatePath` / `revalidateTag` से control करते हैं।

---

## 🔴 Problem it Solves

Without caching, every visitor triggers a database query, an API call and a full render. A product page on Amazon viewed by 100,000 people would hit the database 100,000 times for the same data. That is slow (users wait) and expensive (servers and API bills). But caching has its own risk: stale data (an old price). The goal is a balance: fast most of the time, fresh when it matters.

```
No cache:  request ──► DB query + render ──► response   (every time, slow)
Cache:     request ──► cached HTML/data ──► response    (fast, until it expires)
```

## 🔴 यह क्यों बना? (Hindi)
Caching के बिना हर visitor पर database query, API call और पूरा render होता है। Amazon के product page को 1,00,000 लोग देखें तो वही data के लिए database 1,00,000 बार hit होगा। यह धीमा (users को इंतज़ार) और महँगा (servers और API का बिल) है। लेकिन caching का अपना जोखिम है: पुराना data (पुराना price)। लक्ष्य संतुलन है: ज़्यादातर समय तेज़, और जब ज़रूरी हो तब fresh।

---

## 🟢 How it Works — Step by Step

Next.js (App Router) has four main caches. Knowing which one is involved is the whole topic:

```
1. Request Memoization → same fetch(url) called many times in ONE render is run once (React feature, per request)
2. Data Cache          → stores fetch() results on the server across requests and deployments
3. Full Route Cache    → stores the rendered HTML + RSC payload of STATIC routes (built at build time)
4. Router Cache        → client-side, in the browser: remembers visited/prefetched route payloads for fast navigation
```

How you control freshness:

```
Time-based      → fetch(url, { next: { revalidate: 60 } })  or  export const revalidate = 60
On-demand       → revalidatePath('/products') or revalidateTag('products') after a change
Opt out         → fetch(url, { cache: 'no-store' })  or  export const dynamic = 'force-dynamic'
Tag your data   → fetch(url, { next: { tags: ['products'] } })
```

Version note (important, a classic interview trap): in **Next.js 14**, `fetch` requests were cached by default (`force-cache`) and GET Route Handlers were static by default. In **Next.js 15**, `fetch` is **not cached by default** (you opt in with `cache: 'force-cache'` or `revalidate`), GET Route Handlers are not cached by default, and the client Router Cache no longer reuses page segments by default (`staleTimes` is 0 for pages). Next.js 16 and the `use cache` directive (Cache Components) change the model further and are version-dependent; check the docs of your version.

## 🟢 कैसे काम करता है? (Hindi)

App Router में चार मुख्य caches हैं। पूरा topic यही समझना है कि कौन सी cache शामिल है:

```
1. Request Memoization → एक ही render में बार-बार आने वाला वही fetch(url) सिर्फ एक बार चलता है (React feature, per request)
2. Data Cache          → fetch() के results को server पर requests और deployments के बीच सहेजता है
3. Full Route Cache    → STATIC routes का rendered HTML + RSC payload (build के समय बनता है)
4. Router Cache        → browser में client-side: visited/prefetched routes को तेज़ navigation के लिए याद रखता है
```

Freshness कैसे control करें: **समय के आधार पर** (`revalidate: 60`), **ज़रूरत पर** (data बदलने के बाद `revalidatePath` / `revalidateTag`), **cache बंद** (`cache: 'no-store'` या `dynamic = 'force-dynamic'`)। **ज़रूरी version note:** Next.js 14 में `fetch` default रूप से cached था, लेकिन Next.js 15 में default रूप से cached **नहीं** है; आपको `force-cache` या `revalidate` से opt in करना पड़ता है। Next.js 16 में `use cache` (Cache Components) मॉडल बदल देता है, इसलिए अपने version के docs देखें।

---

## 🟡 Real World Example
**Flipkart-style product catalog:** The category page and product descriptions change rarely, so they are cached for 5 minutes (`revalidate: 300`) and served from the CDN instantly. The price and stock are tagged `product-123`. When the seller updates the price, a Server Action calls `revalidateTag('product-123')` and the next visitor sees the new price. The cart and "My orders" pages are personal, so they use `no-store` and are never shared between users.

## 🟡 Real Example Hindi mein
**Flipkart जैसा product catalog:** Category page और product descriptions कम बदलते हैं, इसलिए उन्हें 5 मिनट के लिए cache किया जाता है (`revalidate: 300`) और CDN से तुरंत दिया जाता है। Price और stock को `product-123` tag मिलता है। Seller price बदलता है तो Server Action `revalidateTag('product-123')` चलाता है और अगला visitor नया price देखता है। Cart और "My orders" pages निजी हैं, इसलिए वे `no-store` इस्तेमाल करते हैं और users के बीच share नहीं होते।

---

## 💻 Code Example — Basic

```jsx
// app/products/page.jsx (Server Component)
// Time-based revalidation (ISR): reuse the result for 60 seconds
export default async function ProductsPage() {
  // next.revalidate: 60 → cache this response for 60 seconds, then refresh in the background
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 60 },
  });
  const products = await res.json();                    // parse the cached or fresh JSON

  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>{p.name} - Rs {p.price}</li>      // plain HTML from the server
      ))}
    </ul>
  );
}
```

```jsx
// Three simple fetch behaviours side by side
async function demo() {
  await fetch('https://api.example.com/a', { cache: 'force-cache' });           // cache until revalidated
  await fetch('https://api.example.com/b', { cache: 'no-store' });              // always fresh, per request
  await fetch('https://api.example.com/c', { next: { revalidate: 3600 } });     // refresh at most hourly
}
demo();
```

## 💻 Code Example — Advanced

```jsx
// lib/products.js: tag data so it can be refreshed on demand
export async function getProduct(id) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { tags: [`product-${id}`, 'products'], revalidate: 3600 }, // tags + safety-net time
  });
  if (!res.ok) throw new Error('Failed to load product');            // let error.js handle it
  return res.json();                                                  // product object
}
```

```jsx
// app/products/[id]/actions.js: on-demand revalidation after a change
'use server';                                                         // Server Action file
import { revalidateTag, revalidatePath } from 'next/cache';           // cache control helpers

export async function updatePrice(id, price) {
  await fetch(`https://api.example.com/products/${id}`, {
    method: 'PATCH',                                                  // update in the backend
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ price }),
  });
  revalidateTag(`product-${id}`);        // refresh every cached fetch that has this tag
  revalidatePath('/products');           // also refresh the listing page
}
```

```jsx
// app/cart/page.jsx: personal data must not be shared, so opt out of caching
export const dynamic = 'force-dynamic';                 // render for every request

import { cookies } from 'next/headers';                 // using cookies makes a route dynamic anyway

export default async function CartPage() {
  const token = (await cookies()).get('token')?.value;  // Next.js 15: cookies() is async
  const res = await fetch('https://api.example.com/cart', {
    headers: { Authorization: `Bearer ${token}` },      // user specific
    cache: 'no-store',                                  // never store a per-user response
  });
  const cart = await res.json();                        // this user's cart
  return <p>{cart.items.length} items in cart</p>;
}
```

```jsx
// Request memoization: the same fetch in two components runs only once per render
async function getUser() {
  const res = await fetch('https://api.example.com/me'); // identical URL + options
  return res.json();
}
async function Header() { const u = await getUser(); return <p>Hi {u.name}</p>; }   // call 1
async function Sidebar() { const u = await getUser(); return <p>{u.email}</p>; }    // call 2 reuses call 1
// For non-fetch data (database queries) wrap the function with React's cache():
// import { cache } from 'react'; export const getUserDb = cache(async (id) => db.user.find(id));
```

---

## 🟠 Next.js Connection
Caching is a Next.js topic, but it connects to React concepts:

```jsx
// Static vs dynamic is decided per route by what you use:
// Static (cached at build):  no cookies(), headers(), searchParams, and no uncached fetch
// Dynamic (per request):     uses cookies(), headers(), searchParams, or { cache: 'no-store' }
export const revalidate = 120;   // route-level: re-generate the static page at most every 2 minutes

// Client side: Router Cache makes <Link> navigation instant.
// router.refresh() in a Client Component re-fetches the current route from the server:
// 'use client'; import { useRouter } from 'next/navigation';
// const router = useRouter(); router.refresh();
```

- Server data caching (Data Cache) is different from client caching with TanStack Query: Next.js caches on the server for all users; TanStack Query caches in one browser.
- Server Actions that mutate data should call `revalidatePath` / `revalidateTag`, otherwise users keep seeing cached old data.
- `unstable_cache` (Next.js 14/15) caches non-fetch work like database calls; newer versions move toward the `use cache` directive. Treat both as version-dependent.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming `fetch` is cached (or not cached) without checking the Next.js version
✅ **Correct:** Always state caching explicitly on important fetches

```jsx
// Wrong: behaviour differs between Next 14 (cached) and Next 15 (not cached)
const res = await fetch('https://api.example.com/prices');

// Right: say what you want
const res2 = await fetch('https://api.example.com/prices', { next: { revalidate: 60 } });
```

❌ **Mistake 2:** Caching user-specific data and leaking it to other users
✅ **Correct:** Use `no-store` or dynamic APIs for personal data; cache only shared data

```jsx
// Wrong: cached per URL, the next user could get the previous user's cart
await fetch('https://api.example.com/cart', { cache: 'force-cache', headers: { Authorization: token } });
// Right
await fetch('https://api.example.com/cart', { cache: 'no-store', headers: { Authorization: token } });
```

❌ **Mistake 3:** Changing data but never revalidating, so users see stale pages
✅ **Correct:** Call `revalidatePath` or `revalidateTag` after a mutation

```jsx
// Wrong
'use server';
export async function addProduct(data) { await db.insert(data); }

// Right
export async function addProduct2(data) {
  await db.insert(data);          // write to the database
  revalidatePath('/products');    // tell Next.js the cached listing is outdated
}
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.jsx  (Next.js 15)
export default async function Page() {
  const a = await fetch('https://api.example.com/time');                        // call A
  const b = await fetch('https://api.example.com/time', { cache: 'no-store' }); // call B
  const t1 = (await a.json()).now;
  const t2 = (await b.json()).now;
  return <p>{t1} / {t2}</p>;
}
```
**Answer:** The page is dynamic because call B uses `no-store`, so it renders per request. In Next.js 15, call A has no cache option, so it is also fetched fresh. Both timestamps are close but come from two separate requests, because request memoization only merges calls with identical URL **and** options, and these options differ. In Next.js 14, call A would have been stored in the Data Cache (`force-cache` default) and could return an old timestamp for a long time, while B is always fresh, so `t1` and `t2` would differ a lot. This is exactly why you should set cache behavior explicitly.

---

## ⚫ Interview Questions + Answers

Q1: What are the caching layers in the Next.js App Router?
A1: Request Memoization (dedupes identical fetches during one render), Data Cache (server-side fetch results across requests), Full Route Cache (rendered HTML and RSC payload for static routes) and Router Cache (client-side route payloads in the browser). They work at different places and have different lifetimes.

Q2: What is the difference between `revalidate` and `revalidateTag` / `revalidatePath`?
A2: `revalidate` is time-based: after N seconds the next request triggers a refresh (stale-while-revalidate). `revalidateTag` and `revalidatePath` are on-demand: you call them after a mutation, so cached data refreshes immediately and you do not wait for the timer.

Q3: How do you stop Next.js from caching a request?
A3: Use `fetch(url, { cache: 'no-store' })`, set `export const dynamic = 'force-dynamic'` on the route, or use dynamic APIs such as `cookies()`, `headers()` and `searchParams`, which make the route render per request.

Q4: What changed about caching defaults from Next.js 14 to 15?
A4: In 14, `fetch` and GET route handlers were cached by default and the client Router Cache kept pages for some time. In 15, `fetch` and GET route handlers are not cached by default and page segments are not reused by default in the Router Cache. You now opt in explicitly. (Later versions introduce `use cache`; version-dependent.)

Q5: What is stale-while-revalidate in Next.js ISR?
A5: When the `revalidate` time has passed, the next visitor still gets the old (stale) page instantly, and Next.js regenerates the page in the background. The following visitor gets the fresh page. Users never wait for the rebuild.

---

## 🔷 When to Use + When Not to Use
✅ **Use caching when:**
- Data is shared by many users and changes slowly (catalog, blog, pricing tiers)
- A page is expensive to build (many API calls or heavy queries)
- You can trigger on-demand revalidation when the data changes

❌ **Avoid caching when:**
- Data is personal (cart, orders, account) or security sensitive
- Data must be real time (live stock, delivery tracking, bidding)
- You cannot invalidate it after changes, which would show stale data for long

---

## 📊 Visual Diagram

```
 Browser                          Next.js Server                               Backend/DB
┌──────────────┐  navigate   ┌───────────────────────────────────────┐
│ Router Cache │────miss────►│ Full Route Cache (static HTML + RSC)   │
│ (client)     │◄──payload───│    │ hit → return instantly            │
└──────────────┘             │    ▼ miss / stale                      │
                             │ Render ── Request Memoization (1 render)│
                             │    │ fetch()                            │
                             │    ▼                                    │
                             │ Data Cache (tags, revalidate) ──miss──► API / DB
                             └───────────────────────────────────────┘
   revalidateTag('x') / revalidatePath('/p')  ──►  clears Data Cache and Full Route Cache entries
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Data Cache | Server cache of fetch results | fetch results की server cache |
| Full Route Cache | Cached HTML and RSC payload of static routes | Static routes के HTML और RSC payload की cache |
| Router Cache | Client-side cache of visited routes | Visited routes की client-side cache |
| Request Memoization | Dedupes identical fetches in one render | एक render में वही fetch एक बार चलाना |
| Revalidate | Refresh cached data | Cached data को ताज़ा करना |
| Tag | Label to refresh a group of cached fetches | Cached fetches के group को refresh करने वाला label |
| ISR | Static page regenerated after a time | समय के बाद दोबारा बनने वाला static page |
| Stale-while-revalidate | Serve old data, refresh in background | पुराना data दो, background में refresh करो |

---

## ⚡ 3-Line Summary
**English:**
1. Next.js has four caches: Request Memoization, Data Cache, Full Route Cache and Router Cache, each with a different place and lifetime.
2. Control freshness with `revalidate` (time), `revalidateTag` / `revalidatePath` (on demand) and `no-store` (opt out).
3. Defaults changed between Next.js 14 and 15, so set caching explicitly and never cache personal data.

**Hindi:**
1. Next.js में चार caches हैं: Request Memoization, Data Cache, Full Route Cache और Router Cache; हर एक की जगह और lifetime अलग है।
2. Freshness को `revalidate` (समय), `revalidateTag` / `revalidatePath` (ज़रूरत पर) और `no-store` (cache बंद) से control करो।
3. Next.js 14 और 15 के बीच defaults बदले हैं, इसलिए caching खुद साफ़ लिखो और निजी data कभी cache मत करो।

---

## ➡️ Next Topic
**191. Build Counter App (useState)** — अब theory से practice: सबसे सरल interview problem से शुरू करके `useState`, functional updates और limits को code में जमाएँगे।
