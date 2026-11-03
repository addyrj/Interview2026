# 174. getStaticPaths (Pages)
# हिंदी में: getStaticPaths — Dynamic Routes के लिए Build Time पर Paths तय करना (Pages Router)

---

## 🔵 Simple Definition (English)
`getStaticPaths` is a Pages Router function used together with `getStaticProps` on a **dynamic route** such as `pages/products/[id].js`. It tells Next.js **which URLs to pre-build** at build time, and what to do (`fallback`) for URLs that were not pre-built.

## 🔵 सरल परिभाषा (Hindi)
`getStaticPaths` Pages Router का function है जो **dynamic route** (जैसे `pages/products/[id].js`) पर `getStaticProps` के साथ इस्तेमाल होता है। यह Next.js को बताता है कि build time पर **कौन से URLs पहले से बनाने हैं**, और जो URLs पहले नहीं बने उनके लिए क्या करना है (`fallback`)।

---

## 🔴 Problem it Solves

`getStaticProps` builds HTML at build time, but for `/products/[id]` Next.js does not know which `id` values exist: 5, 5,000 or 5 million products. Without a list, it cannot generate pages ahead of time. Building every product in a big catalogue makes the build take hours. `getStaticPaths` solves both: you list the important paths (best sellers), and `fallback` decides how to handle the long tail on demand.

```jsx
// PROBLEM: dynamic route + getStaticProps only → build error
// pages/products/[id].js
export async function getStaticProps({ params }) { /* ... */ }
// Error: getStaticPaths is required for dynamic SSG pages
//        and is missing for '/products/[id]'.
```

## 🔴 यह क्यों बना? (Hindi)
`getStaticProps` build time पर HTML बनाता है, लेकिन `/products/[id]` के लिए Next.js को पता नहीं कि कौन से `id` मौजूद हैं: 5, 5,000 या 50 लाख products। List के बिना वह pages पहले से नहीं बना सकता। बड़े catalogue के सारे products बनाने में build घंटों ले सकता है। `getStaticPaths` दोनों समस्याएँ हल करता है: आप ज़रूरी paths (best sellers) की list देते हैं, और `fallback` तय करता है कि बाकी (long tail) को माँग पर कैसे संभालना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → File name has brackets: pages/products/[id].js (dynamic segment)
Step 2 → At build, Next.js calls getStaticPaths()
Step 3 → You return { paths: [{ params: { id: '1' } }, ...], fallback: ... }
Step 4 → For each path, Next.js calls getStaticProps({ params }) and builds HTML
Step 5 → A request for a pre-built path → served from the CDN instantly
Step 6 → A request for an unknown path depends on fallback:
         false      → 404 page (only listed paths exist)
         true       → serve a "fallback" shell, build the page in background, then swap in data
         'blocking' → server renders the page on first visit (user waits), then caches it

KEY: params values must be STRINGS ('1', not 1); catch-all [...slug] needs arrays
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → File के नाम में brackets होते हैं: pages/products/[id].js (dynamic segment)
Step 2 → Build पर Next.js getStaticPaths() को call करता है
Step 3 → आप { paths: [{ params: { id: '1' } }, ...], fallback: ... } return करते हैं
Step 4 → हर path के लिए Next.js getStaticProps({ params }) चलाकर HTML बनाता है
Step 5 → पहले से बने path की request → CDN से तुरंत मिलता है
Step 6 → अनजान path की request fallback पर निर्भर करती है:
         false      → 404 page (सिर्फ listed paths मौजूद हैं)
         true       → "fallback" shell दिखाओ, background में page बनाओ, फिर data डालो
         'blocking' → पहली visit पर server render करता है (user इंतज़ार करता है), फिर cache

KEY: params की values STRING होनी चाहिए ('1', 1 नहीं); catch-all [...slug] में arrays
```

---

## 🟡 Real World Example
**Amazon / Flipkart product pages:** A catalogue has millions of products. The team pre-builds the top 1,000 best sellers in `getStaticPaths` so they load instantly from the CDN. With `fallback: 'blocking'`, any other product is generated the first time someone opens it and is cached for everyone afterwards. A small site such as a restaurant's 10 city pages would use `fallback: false`, because the list is complete and known.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart product pages:** Catalogue में लाखों products होते हैं। Team `getStaticPaths` में top 1,000 best sellers पहले से बना लेती है, जो CDN से तुरंत खुलते हैं। `fallback: 'blocking'` के साथ कोई भी दूसरा product पहली बार खुलने पर बनता है और बाद में सबके लिए cache हो जाता है। किसी restaurant की 10 city pages जैसी छोटी site `fallback: false` इस्तेमाल करेगी, क्योंकि list पूरी और पता है।

---

## 💻 Code Example — Basic

```jsx
// pages/products/[id].js : pre-build 3 products, everything else returns 404

const PRODUCTS = {                                              // fake data store for the example
  1: { id: '1', name: 'Wireless Mouse', price: 799 },
  2: { id: '2', name: 'Keyboard', price: 1499 },
  3: { id: '3', name: 'USB Hub', price: 599 },
};

export default function ProductPage({ product }) {
  return (
    <main>
      <h1>{product.name}</h1>                                   {/* data is ready in the HTML */}
      <p>Price: Rs {product.price}</p>
    </main>
  );
}

// Step 1: which URLs to build
export async function getStaticPaths() {
  return {
    paths: Object.keys(PRODUCTS).map((id) => ({ params: { id } })), // [{params:{id:'1'}}, ...]
    fallback: false,                                            // anything else → 404
  };
}

// Step 2: data for each path
export async function getStaticProps({ params }) {
  return { props: { product: PRODUCTS[params.id] } };           // params.id is a string like '1'
}
```

## 💻 Code Example — Advanced

```jsx
// pages/products/[id].js : big catalogue with fallback: true and a loading shell
import { useRouter } from 'next/router';                        // Pages Router hook
import { getTopProductIds, getProduct } from '../../lib/catalog'; // hypothetical server helpers

export default function ProductPage({ product }) {
  const router = useRouter();

  // With fallback: true, the component renders FIRST with props = {} while the page builds
  if (router.isFallback) {
    return <p>Loading product...</p>;                           // skeleton for first-time visitors
  }

  return (
    <article>
      <h1>{product.name}</h1>
      <p>Rs {product.price}</p>
      <p>{product.description}</p>
    </article>
  );
}

export async function getStaticPaths() {
  const ids = await getTopProductIds(100);                      // only the best 100 at build time
  return {
    paths: ids.map((id) => ({ params: { id: String(id) } })),   // convert numbers to strings
    fallback: true,                                             // others: shell now, data after build
  };
}

export async function getStaticProps({ params }) {
  const product = await getProduct(params.id);                  // DB / API (server only)
  if (!product) {
    return { notFound: true, revalidate: 30 };                  // unknown id → 404, retry later
  }
  return {
    props: { product },
    revalidate: 600,                                            // ISR: refresh every 10 minutes
  };
}

// Catch-all variant example (file: pages/docs/[...slug].js):
// paths: [{ params: { slug: ['getting-started', 'install'] } }]  → /docs/getting-started/install
// Optional catch-all [[...slug]].js also matches /docs with slug: undefined
```

---

## 🟠 Next.js Connection

`getStaticPaths` is Pages Router only. In the App Router the replacement is `generateStaticParams`, and the old `fallback` options map to the `dynamicParams` setting.

```jsx
// App Router equivalent (Next.js 14/15), app/products/[id]/page.jsx
import { notFound } from 'next/navigation';
import { getTopProductIds, getProduct } from '@/lib/catalog';   // hypothetical helpers

export const dynamicParams = true;                              // true ≈ fallback 'blocking' (default)
                                                                // false ≈ fallback: false (404 for unknown)
export const revalidate = 600;                                  // ISR

export async function generateStaticParams() {                  // replaces getStaticPaths
  const ids = await getTopProductIds(100);
  return ids.map((id) => ({ id: String(id) }));                 // objects of params directly
}

export default async function Page({ params }) {
  const { id } = await params;                                  // Next.js 15: Promise (14: plain object)
  const product = await getProduct(id);
  if (!product) notFound();
  return <h1>{product.name}</h1>;
}
```
Note: `fallback: true` (shell first) has no direct App Router equivalent. The nearest approach is `loading.js` with Suspense streaming.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Returning numbers in `params`
✅ **Correct:** Params must be strings (or arrays of strings for catch-all routes).

```jsx
// Wrong: error "A required parameter (id) was not provided as a string"
return { paths: [{ params: { id: 1 } }], fallback: false };     // ❌ number

// Right
return { paths: [{ params: { id: String(1) } }], fallback: false }; // ✅ string
```

❌ **Mistake 2:** Using `fallback: true` but reading `props` without checking `router.isFallback`
✅ **Correct:** The component first renders with empty props. Show a skeleton, otherwise `product.name` throws.

```jsx
// Wrong: TypeError: Cannot read properties of undefined (reading 'name')
export default function Page({ product }) {
  return <h1>{product.name}</h1>;                               // ❌ product undefined in fallback
}

// Right
export default function Page({ product }) {
  const { isFallback } = useRouter();
  if (isFallback) return <p>Loading...</p>;                     // ✅ handle shell state
  return <h1>{product.name}</h1>;
}
```

❌ **Mistake 3:** Building every product with `fallback: false` for a huge catalogue
✅ **Correct:** Pre-build a small set and use `fallback: 'blocking'` (or `true`) for the rest. Builds stay short and unknown ids are still generated on demand.

```jsx
// Wrong: 2 million pages built at deploy time, and new products show 404 until the next deploy
const all = await getAllProductIds();
return { paths: all.map((id) => ({ params: { id } })), fallback: false }; // ❌

// Right
const top = await getTopProductIds(100);
return { paths: top.map((id) => ({ params: { id } })), fallback: 'blocking' }; // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
// pages/items/[id].js
export async function getStaticPaths() {
  return { paths: [{ params: { id: '1' } }], fallback: 'blocking' };
}
export async function getStaticProps({ params }) {
  console.log('building', params.id);
  return { props: { id: params.id } };                           // no revalidate
}
export default function Item({ id }) { return <p>Item {id}</p>; }
// Production. Three users open /items/1, /items/2, /items/2 in that order. How many
// times is "building" printed, and what happens for /items/2 the second time?
```
**Answer:** `building 1` is printed once during `next build`. When the first user opens `/items/2` (not pre-built), `fallback: 'blocking'` makes the server run `getStaticProps` and render the HTML while the user waits, printing `building 2` once, and then **caches** the result like a normal static page. The third request is served from the cache with no log. So the total is 2 logs. With `fallback: false`, `/items/2` would be a 404. With `fallback: true`, the first user would see the shell (`isFallback`) then the data. Without `revalidate`, the cached page is never rebuilt until the next deploy.

---

## ⚫ Interview Questions + Answers

Q1: Why is `getStaticPaths` needed?
A1: For dynamic routes using `getStaticProps`, Next.js must know at build time which parameter values to pre-render. `getStaticPaths` returns that list. Without it, the build fails for that route.

Q2: Explain the three `fallback` values.
A2: `false`: only the listed paths exist, others give 404. `true`: unlisted paths show a fallback version immediately (`router.isFallback` is true), the page is generated in the background, and then props arrive. `'blocking'`: unlisted paths are server-rendered on the first request (user waits, no loading state) and then cached.

Q3: When would you choose `blocking` over `true`?
A3: `blocking` is simpler and better for SEO because crawlers receive complete HTML, and you do not have to write a loading state. Use `true` when generation is slow and you prefer to show a skeleton quickly.

Q4: Can `getStaticPaths` be used with `getServerSideProps`?
A4: No. It works only with `getStaticProps`. Pages that use `getServerSideProps` render per request and do not need a path list.

Q5: What replaces `getStaticPaths` in the App Router?
A5: `generateStaticParams` returns the list of params, and the `dynamicParams` route segment config replaces `fallback` (true means unknown params are rendered on demand, false means 404). Data fetching happens directly in the async Server Component.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A dynamic route (`[id]`, `[slug]`) is static or ISR-friendly: blog posts, products, docs
- You know the important paths at build time and want them instantly fast
- You want unknown paths generated on demand and cached

❌ **Avoid when:**
- The page is user-specific (use `getServerSideProps` or client fetching)
- You would have to enumerate millions of paths at build (use a small set + fallback)
- You are building new routes in the App Router (use `generateStaticParams`)

---

## 📊 Visual Diagram

```
  pages/products/[id].js

  BUILD:  getStaticPaths() ──▶ ['1','2','3']
                                  │ for each id
                                  ▼
                          getStaticProps({id}) ──▶ /products/1.html, /2.html, /3.html

  REQUEST for /products/99 (not built):

   fallback:false ──────▶ 404
   fallback:true  ──────▶ shell (isFallback) ──▶ build in background ──▶ data swapped in
   fallback:'blocking' ─▶ user waits ──▶ server renders ──▶ full HTML ──▶ cached for all

  Re-render behavior (fallback:true): component renders twice: first with
  isFallback = true and empty props, then with real props.
  Performance: built paths = CDN speed; unbuilt = one slow first hit.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dynamic route | File name with `[param]` | `[param]` वाली file का route |
| paths | List of params objects to pre-build | Pre-build होने वाले params की list |
| fallback | Rule for paths not pre-built | जो paths पहले नहीं बने उनका नियम |
| isFallback | router flag true while shell shows | Shell दिखते समय true रहने वाला flag |
| Catch-all route | `[...slug]` matches many segments | कई segments से मेल खाने वाला route |
| generateStaticParams | App Router replacement | App Router में इसकी जगह |
| dynamicParams | App Router setting like fallback | App Router की fallback जैसी setting |
| Long tail | Many rarely visited pages | कम visit होने वाले ढेर सारे pages |

---

## ⚡ 3-Line Summary
**English:**
1. `getStaticPaths` lists which dynamic-route URLs to pre-build, and works only with `getStaticProps`.
2. `fallback` (`false`, `true`, `'blocking'`) decides how unlisted URLs are handled: 404, shell then data, or render-then-cache.
3. Params must be strings; handle `router.isFallback`; in the App Router use `generateStaticParams` and `dynamicParams`.

**Hindi:**
1. `getStaticPaths` बताता है कि dynamic route के कौन से URLs पहले से बनाने हैं, और यह सिर्फ `getStaticProps` के साथ चलता है।
2. `fallback` (`false`, `true`, `'blocking'`) तय करता है कि listed न होने वाले URLs का क्या होगा: 404, shell फिर data, या render करके cache।
3. Params strings होने चाहिए; `router.isFallback` संभालो; App Router में `generateStaticParams` और `dynamicParams` इस्तेमाल करो।

---

## ➡️ Next Topic
**175. SSR vs SSG vs ISR vs CSR** — अब तीनों functions समझ चुके हो, तो चारों rendering strategies की सीधी तुलना और यह तय करना कि कौन सा page किस तरीके से बनाना चाहिए।
