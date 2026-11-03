# 180. Next.js Metadata + SEO
# हिंदी में: Next.js Metadata + SEO — Search और Social Sharing के लिए page की जानकारी

---

## 🔵 Simple Definition (English)
**Metadata** is information about a page (title, description, Open Graph image, canonical URL) placed in the HTML `<head>`. In the App Router you export a `metadata` object or a `generateMetadata` function from a `layout.js` or `page.js`, and Next.js writes the tags on the server.

## 🔵 सरल परिभाषा (Hindi)
**Metadata** page के बारे में जानकारी है (title, description, Open Graph image, canonical URL) जो HTML के `<head>` में जाती है। App Router में आप `layout.js` या `page.js` से `metadata` object या `generateMetadata` function export करते हैं, और Next.js server पर tags लिख देता है।

---

## 🔴 Problem it Solves

A client-rendered React app (Create React App) sends an empty `<div id="root">`, so crawlers and WhatsApp/Twitter link previews often see no title or image. Developers used `react-helmet`, which changed the head only after JavaScript ran. Metadata in Next.js is generated on the server, so the first HTML already contains correct tags, and it can be dynamic per product or article.

```jsx
// PROBLEM: SPA head is the same for every URL and set after JS runs
// <title>React App</title>

// SOLUTION: server-generated, per-page metadata
export const metadata = { title: 'Biryani near you | Zomato', description: 'Order online' };
```

## 🔴 यह क्यों बना? (Hindi)
Client-rendered React app (Create React App) खाली `<div id="root">` भेजता है, इसलिए crawlers और WhatsApp/Twitter के link previews को अक्सर title या image दिखती ही नहीं। Developers `react-helmet` इस्तेमाल करते थे, जो JavaScript चलने के बाद head बदलता था। Next.js में metadata server पर बनता है, इसलिए पहले HTML में ही सही tags होते हैं, और हर product या article के लिए dynamic भी हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → In layout.js or page.js, export const metadata = { ... } for static values
Step 2 → For dynamic values, export async function generateMetadata({ params })
Step 3 → Next.js collects metadata from the root layout down to the page
Step 4 → Child values override parent values (title and others are merged by field)
Step 5 → Next.js renders <title>, <meta>, <link rel="canonical">, Open Graph, Twitter tags
Step 6 → Fetches inside generateMetadata are deduplicated with the page's own fetches
Step 7 → Special files: sitemap.js, robots.js, opengraph-image.js, icon.png

Both exports work only in Server Components (never in a 'use client' file)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → layout.js या page.js में static values के लिए export const metadata = { ... } लिखो
Step 2 → Dynamic values के लिए export async function generateMetadata({ params }) लिखो
Step 3 → Next.js root layout से page तक सारा metadata इकट्ठा करता है
Step 4 → Child की values parent की values को override करती हैं (fields के हिसाब से merge होती हैं)
Step 5 → Next.js <title>, <meta>, <link rel="canonical">, Open Graph, Twitter tags बनाता है
Step 6 → generateMetadata के अंदर के fetch, page के अपने fetch के साथ deduplicate होते हैं
Step 7 → Special files: sitemap.js, robots.js, opengraph-image.js, icon.png

दोनों exports सिर्फ Server Components में चलते हैं (किसी 'use client' file में नहीं)
```

---

## 🟡 Real World Example
**Amazon product page:** Each product URL needs its own title ("boAt Rockerz 450 - Amazon.in"), description, price in structured data and a product image for sharing. When someone pastes the link on WhatsApp, the preview card shows the product photo and title because the server-rendered head contains Open Graph tags. Google also reads the canonical URL to avoid indexing the same product under many query-string variants.

## 🟡 Real Example Hindi mein
**Amazon product page:** हर product URL को अपना title ("boAt Rockerz 450 - Amazon.in"), description, structured data में price और sharing के लिए product image चाहिए। जब कोई link WhatsApp पर paste करता है तो preview card में product photo और title दिखता है, क्योंकि server-rendered head में Open Graph tags होते हैं। Google canonical URL भी पढ़ता है ताकि एक ही product अलग query-string versions में index न हो।

---

## 💻 Code Example — Basic

```jsx
// app/layout.jsx: site-wide default metadata
export const metadata = {
  metadataBase: new URL('https://www.myshop.in'),      // base for relative URLs (needed for OG images)
  title: {
    default: 'MyShop: Online Shopping India',          // used when a page has no title
    template: '%s | MyShop',                           // page titles become "Shoes | MyShop"
  },
  description: 'Buy phones, shoes and more with fast delivery.', // meta description
  openGraph: {
    type: 'website',                                   // Open Graph type
    siteName: 'MyShop',                                // shown on social cards
    images: ['/og-default.png'],                       // default share image
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>                          {/* title/meta are injected into <head> automatically */}
    </html>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/products/[slug]/page.jsx: dynamic metadata + JSON-LD structured data
import { notFound } from 'next/navigation';            // triggers the 404 page
import { cache } from 'react';                         // memoize per request

// Fake data layer. In a real app this calls your DB or API.
const getProduct = cache(async (slug) => {             // cache() avoids a double fetch
  const all = { 'boat-450': { name: 'boAt Rockerz 450', price: 1499, image: '/p/boat.jpg', desc: 'Bluetooth headphones' } };
  return all[slug] ?? null;                            // null when not found
});

// Next.js 15+: params is a Promise. In Next.js 14 it is a plain object (version-dependent).
export async function generateMetadata({ params }) {
  const { slug } = await params;                       // read dynamic segment
  const product = await getProduct(slug);              // same call as the page below (cached)
  if (!product) return { title: 'Not found' };         // fallback metadata
  return {
    title: product.name,                               // becomes "boAt Rockerz 450 | MyShop" via template
    description: product.desc,
    alternates: { canonical: `/products/${slug}` },    // canonical URL against duplicates
    openGraph: {
      title: product.name,
      description: product.desc,
      images: [{ url: product.image, width: 1200, height: 630 }], // share image
    },
    robots: { index: true, follow: true },             // allow indexing
  };
}

export default async function ProductPage({ params }) {
  const { slug } = await params;
  const product = await getProduct(slug);              // reused from the cache
  if (!product) notFound();                            // render not-found.js

  const jsonLd = {                                     // structured data for rich results
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    offers: { '@type': 'Offer', price: product.price, priceCurrency: 'INR' },
  };

  return (
    <article>
      <h1>{product.name}</h1>
      <p>₹{product.price}</p>
      {/* Escape "<" so the JSON cannot break out of the script tag */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
    </article>
  );
}
```

---

## 🟠 Real App Integration

Generate a sitemap and robots file from code so crawlers find all product URLs.

```jsx
// app/sitemap.js → served at /sitemap.xml
export default async function sitemap() {
  const slugs = ['boat-450', 'nike-air'];               // in real apps, read from your DB
  const products = slugs.map(slug => ({
    url: `https://www.myshop.in/products/${slug}`,      // absolute URL required
    lastModified: new Date(),                           // last change time
    changeFrequency: 'daily',                           // hint for crawlers
    priority: 0.8,                                      // relative importance
  }));
  return [{ url: 'https://www.myshop.in', lastModified: new Date() }, ...products];
}
```

```jsx
// app/robots.js → served at /robots.txt
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/cart', '/account'] }, // hide private pages
    sitemap: 'https://www.myshop.in/sitemap.xml',       // where the sitemap is
  };
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Exporting `metadata` from a Client Component
✅ **Correct:** Keep metadata in a Server Component (`layout.js` or `page.js` without `'use client'`)

```jsx
// Wrong: metadata is ignored / build error in a client file
'use client';                                           // ❌
export const metadata = { title: 'Cart' };

// Right: server page exports metadata, imports a client component for interactivity
import CartClient from './CartClient';                  // ✅ has 'use client'
export const metadata = { title: 'Cart' };
export default function Page() { return <CartClient />; }
```

❌ **Mistake 2:** Using relative Open Graph image URLs without `metadataBase`
✅ **Correct:** Set `metadataBase` in the root layout (or use absolute URLs)

```jsx
// Wrong: social crawlers cannot resolve the relative image
export const metadata = { openGraph: { images: ['/og.png'] } };      // ❌ no metadataBase

// Right
export const metadata = {
  metadataBase: new URL('https://www.myshop.in'),                    // ✅ base for relative URLs
  openGraph: { images: ['/og.png'] },
};
```

---

## 🧠 Tricky Interview Question

```jsx
// app/layout.jsx
export const metadata = { title: 'Shop' };

// app/products/page.jsx
export const metadata = { openGraph: { title: 'All Products' } };
```
**Answer:** The `<title>` on `/products` is still `Shop`. Metadata is merged shallowly by top-level key: the page defines only `openGraph`, so the parent's `title` stays. But if the page had defined `openGraph: { title: 'All Products' }` and the layout also had `openGraph: { images: [...] }`, the layout's `openGraph.images` would be lost, because the whole `openGraph` key is replaced, not deeply merged. Also, `title` and `openGraph.title` are independent: the browser tab shows `title`, while the social card uses `openGraph.title`.

---

## ⚫ Interview Questions + Answers

Q1: How do you set page metadata in the App Router?
A1: Export a `metadata` object (static) or an async `generateMetadata` function (dynamic) from `layout.js` or `page.js` in a Server Component.

Q2: Why is this better for SEO than `react-helmet` in a SPA?
A2: The tags are in the first server-rendered HTML, so crawlers and link-preview bots see them without running JavaScript.

Q3: What does `title.template` do?
A3: It formats child titles: with `template: '%s | MyShop'` and a page title `Shoes`, the final title is `Shoes | MyShop`.

Q4: Will `generateMetadata` and the page fetch the same data twice?
A4: No for `fetch` (identical requests are deduplicated in a render pass). For database calls, wrap the function in React `cache()` to share the result.

Q5: How do you help search engines discover pages?
A5: Provide `app/sitemap.js` and `app/robots.js`, set `alternates.canonical`, and use structured data (JSON-LD) for rich results.

---

## 🔷 When to Use + When Not to Use
✅ **Use the Metadata API when:**
- Public pages need to rank in Google or look good when shared
- Titles and images depend on route data (products, articles)
- You want sitemaps and robots generated from code

❌ **Avoid / skip when:**
- Pages are private (dashboard); use `robots: { index: false }` instead of investing in OG images
- You need tags changed on the client after interaction (use `document.title` in an effect, rarely)
- You put metadata in a Client Component (not supported)

---

## 📊 Visual Diagram

```
  Request: /products/boat-450
        │
        ▼ Server
  layout.jsx metadata      → title template, metadataBase, default OG
        +
  page.jsx generateMetadata→ title "boAt Rockerz 450", canonical, OG image
        │ merge (child overrides parent keys)
        ▼
  <head>
    <title>boAt Rockerz 450 | MyShop</title>
    <meta name="description" ...>
    <link rel="canonical" href=".../products/boat-450">
    <meta property="og:image" ...>
  </head>
        │
        ▼ WhatsApp / Google bot reads it, no JavaScript needed

  Re-render behavior: metadata runs on the server per request (or at build for
  static pages). It does not cause client re-renders.
  Performance: no client JS cost, unlike react-helmet; wrap DB calls in cache().
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| metadata | Exported object for head tags | Head tags के लिए export object |
| generateMetadata | Async function for dynamic tags | Dynamic tags वाला async function |
| Open Graph | Tags for social share cards | Social share cards के tags |
| Canonical URL | The preferred URL of a page | Page का मुख्य URL |
| sitemap.xml | List of URLs for crawlers | Crawlers के लिए URLs की list |
| robots.txt | Rules for crawlers | Crawlers के लिए नियम |
| JSON-LD | Structured data for rich results | Rich results के लिए structured data |
| metadataBase | Base URL for relative metadata URLs | Relative URLs का base |

---

## ⚡ 3-Line Summary
**English:**
1. Export `metadata` or `generateMetadata` from a Server Component layout or page, and Next.js writes the head tags on the server.
2. Child metadata overrides parent keys; set `metadataBase`, canonical URLs and Open Graph images.
3. Add `sitemap.js`, `robots.js` and JSON-LD to help search engines.

**Hindi:**
1. Server Component के layout या page से `metadata` या `generateMetadata` export करो, और Next.js server पर head tags लिख देता है।
2. Child का metadata parent की keys को override करता है; `metadataBase`, canonical URLs और Open Graph images set करो।
3. Search engines की मदद के लिए `sitemap.js`, `robots.js` और JSON-LD जोड़ो।

---

## ➡️ Next Topic
**181. Next.js Loading + Error Pages** — `loading.js`, `error.js`, `not-found.js` और `global-error.js` से loading states और errors को route-level पर संभालना।
