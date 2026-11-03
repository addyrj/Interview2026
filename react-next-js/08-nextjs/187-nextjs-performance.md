# 187. Next.js Performance
# हिंदी में: Next.js Performance — App को तेज़ बनाने की techniques

---

## 🔵 Simple Definition (English)
**Next.js performance** means making pages load fast and respond quickly: send less JavaScript, render on the server, stream content, cache data, optimize images, fonts and scripts, and measure with Core Web Vitals (LCP, INP, CLS).

## 🔵 सरल परिभाषा (Hindi)
**Next.js performance** का मतलब है pages का तेज़ load होना और जल्दी response देना: कम JavaScript भेजना, server पर render करना, content stream करना, data cache करना, images, fonts और scripts optimize करना, और Core Web Vitals (LCP, INP, CLS) से नापना।

---

## 🔴 Problem it Solves

Slow sites lose users and money: users on a mid-range Android phone and a 4G connection abandon pages that take more than a few seconds. Typical causes are huge JavaScript bundles, client-side fetch waterfalls, unoptimized images, blocking third-party scripts and layout shifts. Search engines also use Core Web Vitals as a ranking signal. Next.js gives many built-in tools, but they only help when used correctly.

```jsx
// PROBLEM: everything is a Client Component, fetched after load, heavy library imported
'use client';
import moment from 'moment';                    // large library for one date
useEffect(() => { fetch('/api/products').then(...) }, []);  // fetch starts only AFTER JS loads

// SOLUTION: Server Component fetch + lighter code
// async Server Component → HTML has data → no client JS for display
```

## 🔴 यह क्यों बना? (Hindi)
धीमी sites users और पैसा दोनों खोती हैं: mid-range Android phone और 4G पर users कुछ सेकंड से ज़्यादा लगने वाले pages छोड़ देते हैं। आम कारण हैं बड़े JavaScript bundles, client-side fetch waterfalls, unoptimized images, blocking third-party scripts और layout shifts। Search engines भी Core Web Vitals को ranking signal मानते हैं। Next.js कई built-in tools देता है, पर वे तभी काम करते हैं जब सही इस्तेमाल हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: Lighthouse, PageSpeed Insights, Vercel Analytics, useReportWebVitals
Step 2 → Default to Server Components; add 'use client' only for interactive leaves
Step 3 → Fetch data on the server, in parallel (Promise.all), and stream with Suspense
Step 4 → Reduce client JS: dynamic() / lazy imports, lighter libraries, @next/bundle-analyzer
Step 5 → Use next/image, next/font, and next/script (strategy="lazyOnload") for third parties
Step 6 → Cache: static rendering, revalidate (ISR), fetch cache options, CDN, unstable_cache/'use cache' (version-dependent)
Step 7 → Prefetch with <Link> (automatic in viewport in production) for instant navigations
Step 8 → Re-measure with real user data (field data), not only lab data

Rule: the fastest code is the code you never ship
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले नापो: Lighthouse, PageSpeed Insights, Vercel Analytics, useReportWebVitals
Step 2 → Default में Server Components रखो; 'use client' सिर्फ interactive हिस्सों पर लगाओ
Step 3 → Data server पर fetch करो, parallel में (Promise.all), और Suspense से stream करो
Step 4 → Client JS घटाओ: dynamic() / lazy imports, हल्की libraries, @next/bundle-analyzer
Step 5 → next/image, next/font और third parties के लिए next/script (strategy="lazyOnload") इस्तेमाल करो
Step 6 → Cache: static rendering, revalidate (ISR), fetch cache options, CDN, unstable_cache/'use cache' (version-dependent)
Step 7 → <Link> से prefetch (production में viewport में आते ही अपने आप) ताकि navigation तुरंत हो
Step 8 → असली users के data (field data) से दोबारा नापो, सिर्फ lab data से नहीं

नियम: सबसे तेज़ code वह है जो आप भेजते ही नहीं
```

---

## 🟡 Real World Example
**Flipkart Big Billion Days:** Millions of users hit product pages at once, mostly on mid-range phones. The page is a Server Component so product details arrive as HTML, the image carousel is the only heavy Client Component (loaded with `dynamic`), the reviews section streams in later with Suspense, the chat-support widget loads after the page is idle, and product images use `next/image`. Result: fast LCP, small JavaScript, and a stable layout.

## 🟡 Real Example Hindi mein
**Flipkart Big Billion Days:** लाखों users एक साथ product pages खोलते हैं, ज़्यादातर mid-range phones पर। Page एक Server Component है इसलिए product details HTML में आ जाती है, image carousel ही अकेला भारी Client Component है (`dynamic` से load), reviews section Suspense से बाद में stream होता है, chat-support widget page के idle होने के बाद load होता है, और product images `next/image` से आती हैं। नतीजा: तेज़ LCP, कम JavaScript और स्थिर layout।

---

## 💻 Code Example — Basic

```jsx
// app/products/page.jsx: Server Component that fetches in parallel and streams a slow part
import { Suspense } from 'react';                        // stream parts independently
import Reviews from './Reviews';                         // slow async Server Component

async function getProduct() {                            // fast data
  const res = await fetch('https://fakestoreapi.com/products/1', { next: { revalidate: 60 } }); // cache 60s
  return res.json();
}

export default async function ProductPage() {
  const product = await getProduct();                    // runs on the server, no client waterfall
  return (
    <main>
      <h1>{product.title}</h1>                           {/* shown right away */}
      <p>₹{product.price}</p>
      <Suspense fallback={<p>Loading reviews...</p>}>    {/* reviews stream in later */}
        <Reviews />
      </Suspense>
    </main>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/products/Gallery.jsx: heavy interactive widget isolated as a Client Component
'use client';
import { useState } from 'react';

export default function Gallery({ images }) {
  const [i, setI] = useState(0);                         // current slide index
  return (
    <div>
      <img src={images[i]} alt={`Slide ${i + 1}`} width={400} height={400} />
      <button onClick={() => setI((i + 1) % images.length)}>Next</button>
    </div>
  );
}
```

```jsx
// app/products/ProductView.jsx: lazy-load the widget and a third-party chat script
import dynamic from 'next/dynamic';                     // code splitting helper
import Script from 'next/script';                        // optimized third-party scripts

// Separate chunk, loaded only when this component renders. Placed in a Server Component,
// the client chunk still loads separately and does not block the HTML.
const Gallery = dynamic(() => import('./Gallery'), {
  loading: () => <div style={{ height: 400 }} />,        // reserve space to avoid layout shift (CLS)
});

export default function ProductView({ images }) {
  return (
    <>
      <Gallery images={images} />
      {/* Chat widget loads after everything else, never blocks interactivity */}
      <Script src="https://example.com/chat.js" strategy="lazyOnload" />
    </>
  );
}
```

```jsx
// app/products/parallel.jsx: avoid server waterfalls with Promise.all
async function getReviews() { const r = await fetch('https://fakestoreapi.com/products?limit=3'); return r.json(); }
async function getRelated() { const r = await fetch('https://fakestoreapi.com/products?limit=4'); return r.json(); }

export default async function Page() {
  // Wrong way: const a = await getReviews(); const b = await getRelated();  → total = a + b
  const [reviews, related] = await Promise.all([getReviews(), getRelated()]); // total = max(a, b)
  return <p>{reviews.length} reviews, {related.length} related items</p>;
}
```

---

## 🟠 Real App Integration

Measure real users with `useReportWebVitals` and analyze the bundle in CI.

```jsx
// app/WebVitals.jsx: report Core Web Vitals to your analytics
'use client';
import { useReportWebVitals } from 'next/web-vitals';    // built-in hook

export default function WebVitals() {
  useReportWebVitals((metric) => {                       // called for LCP, INP, CLS, FCP, TTFB
    navigator.sendBeacon('/api/vitals', JSON.stringify({ // sendBeacon survives page unload
      name: metric.name,                                 // e.g. "LCP"
      value: metric.value,                               // number in ms (CLS is unitless)
      id: metric.id,                                     // unique per page load
    }));
  });
  return null;                                           // renders nothing
}
// Add <WebVitals /> in app/layout.jsx. For bundle size: ANALYZE=true next build with @next/bundle-analyzer.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Adding `'use client'` at the top of big files or layouts "just in case"
✅ **Correct:** Keep it on small interactive leaf components, pass server-rendered children in

```jsx
// Wrong: the whole page and all its imports are shipped to the browser
'use client';                                            // ❌ on the page
import HugeChart from 'huge-chart-lib';
export default function Page({ data }) { return <HugeChart data={data} />; }

// Right: Server Component page, small client leaf
import LikeButton from './LikeButton';                   // ✅ 'use client' only here
export default async function Page() {
  const data = await getData();                          // server fetch
  return <article>{data.text}<LikeButton id={data.id} /></article>;
}
```

❌ **Mistake 2:** Sequential awaits (waterfalls), and no `<Suspense>` around slow parts
✅ **Correct:** Start requests together and stream slow sections

```jsx
// Wrong: second request waits for the first
const user = await getUser();                            // ❌ 300 ms
const orders = await getOrders();                        // ❌ +400 ms = 700 ms

// Right
const [user2, orders2] = await Promise.all([getUser(), getOrders()]); // ✅ ~400 ms
```

---

## 🧠 Tricky Interview Question

```jsx
// app/layout.jsx
import { cookies } from 'next/headers';
export default async function Layout({ children }) {
  const theme = (await cookies()).get('theme')?.value;
  return <html data-theme={theme}><body>{children}</body></html>;
}
```
Your marketing pages were static and fast. After adding this layout, they become slow. Why?

**Answer:** Calling `cookies()` (or `headers()`, `searchParams`) is a dynamic API. Using it in the root layout opts every route under it out of static rendering, so all pages are rendered on the server per request instead of being served from the CDN. TTFB rises and caching is lost. Fixes: read the cookie only in a small Client Component or a component wrapped in `<Suspense>`, apply the theme with a tiny inline script/CSS, or use Partial Prerendering (experimental, version-dependent) so the static shell stays static while the dynamic part streams in.

---

## ⚫ Interview Questions + Answers

Q1: What are the Core Web Vitals?
A1: LCP (Largest Contentful Paint, loading, good under 2.5 s), INP (Interaction to Next Paint, responsiveness, good under 200 ms; replaced FID in 2024) and CLS (Cumulative Layout Shift, stability, good under 0.1).

Q2: How do Server Components improve performance?
A2: Their code and dependencies are never sent to the browser, data is fetched close to the database, and HTML arrives already filled with content, so less JavaScript to download, parse and run.

Q3: How do you reduce JavaScript bundle size?
A3: Prefer Server Components, import only what you need, replace heavy libraries (moment with date-fns or Intl), lazy-load with `next/dynamic` or `React.lazy`, remove unused dependencies, and inspect with `@next/bundle-analyzer`.

Q4: How does Next.js help with third-party scripts?
A4: `next/script` with strategies: `beforeInteractive`, `afterInteractive` (default), `lazyOnload`, `worker` (experimental). Analytics and chat widgets should usually use `afterInteractive` or `lazyOnload`.

Q5: What caching layers exist?
A5: Browser cache, CDN/full-route static output, data cache for `fetch` (`revalidate`, tags), request memoization of identical `fetch` calls within a render, and the client-side router cache. Defaults changed between Next.js 14 and 15, so check the version (version-dependent).

---

## 🔷 When to Use + When Not to Use
✅ **Optimize when:**
- Metrics (field data) show poor LCP, INP or CLS
- Bundle analysis shows large dependencies on key pages
- Traffic is high or users are on slow devices

❌ **Do NOT over-optimize when:**
- You have no measurements (premature optimization)
- A micro-optimization hurts readability for a tiny gain
- An internal tool has a handful of users on fast machines

---

## 📊 Visual Diagram

```
  Slow                                   Fast
  ────                                   ────
  Client fetch after JS loads            Server Component fetch (Promise.all)
  Whole page 'use client'                'use client' only on leaves
  <img> 3 MB                             next/image WebP, lazy
  Blocking chat script                   next/script lazyOnload
  White screen until all data            Suspense: shell now, slow parts stream

  Timeline of a fast page:
  TTFB ─► HTML shell (header, title, price) ─► LCP image ─► reviews stream in
          └─ small JS hydrates only interactive leaves (low INP)
          └─ reserved sizes (no CLS)

  Re-render behavior: fewer Client Components means fewer hydration costs and
  re-renders; memoization (React.memo, useMemo) only matters inside client leaves.
  Performance impact: each 100 KB of JS costs parse + execute time, especially on
  low-end phones, so shipping less matters more than micro-tuning renders.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCP | Largest content paint time | सबसे बड़े content का समय |
| INP | Delay to respond to input | Input पर response की देरी |
| CLS | Layout movement score | Layout हिलने का score |
| Streaming | Send UI in chunks | UI को टुकड़ों में भेजना |
| Code splitting | Load code on demand | ज़रूरत पर code load करना |
| Waterfall | Requests waiting one by one | Requests का एक-एक करके इंतज़ार |
| ISR | Static page refreshed on schedule | तय समय पर refresh होने वाला static page |
| Bundle analyzer | Tool showing JS size by module | JS size दिखाने वाला tool |

---

## ⚡ 3-Line Summary
**English:**
1. Measure with Core Web Vitals, then ship less JavaScript by using Server Components and small client leaves.
2. Fetch in parallel, stream with Suspense, lazy-load heavy code, and use `next/image`, `next/font`, `next/script`.
3. Be careful with dynamic APIs in layouts, because they remove static caching.

**Hindi:**
1. Core Web Vitals से नापो, फिर Server Components और छोटे client leaves से कम JavaScript भेजो।
2. Parallel में fetch करो, Suspense से stream करो, भारी code lazy-load करो, और `next/image`, `next/font`, `next/script` इस्तेमाल करो।
3. Layouts में dynamic APIs से सावधान रहो, क्योंकि वे static caching हटा देते हैं।

---

## ➡️ Next Topic
**188. Next.js Deployment (Vercel/AWS)** — Vercel पर one-click deploy, AWS/Docker/standalone output, environment variables और production checklist।
