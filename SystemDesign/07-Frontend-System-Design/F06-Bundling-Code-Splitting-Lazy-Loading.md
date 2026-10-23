# F06. Bundling, Code Splitting + Lazy Loading
# हिंदी में: Bundling — सैकड़ों JS/CSS files को कुछ optimized files में जोड़ना; Code Splitting — उन्हें छोटे टुकड़ों (chunks) में बाँटना; Lazy Loading — कोड या image तभी लाना जब सच में ज़रूरत हो

---

## 🔵 Simple Definition (English)
- **Bundler** (webpack, Vite/Rollup, esbuild, Turbopack, Rspack; **Metro** for React Native): takes your modules (JS/TS, CSS, images) and dependencies, resolves imports, transpiles (TS/JSX → JS), **tree-shakes** unused code, minifies, and outputs optimized **bundles/chunks** with content-hashed filenames.
- **Code splitting**: instead of one huge `app.js`, split code into chunks loaded on demand: per **route**, per **heavy component** (charts, editors, maps), and **vendor** chunks.
- **Lazy loading**: defer loading of code (`import()`, `React.lazy`, `next/dynamic`), images (`loading="lazy"`), and data until needed (on navigation, on interaction, or when visible).
- **Prefetching/preloading**: fetch likely-next chunks early (on hover/idle) so lazy doesn't mean slow.

## 🔵 सरल परिभाषा (Hindi)
Bundler (webpack, Vite, Metro) आपकी सारी files और libraries को जोड़कर, TypeScript/JSX को JS में बदलकर, बेकार कोड हटाकर (tree shaking) और छोटा करके (minify) तैयार files बनाता है।
Code splitting = एक बड़ी file की जगह छोटे टुकड़े — हर पेज/भारी component का अलग; Lazy loading = कोड/image तभी लाओ जब ज़रूरत हो; Prefetch = अगली ज़रूरत का कोड पहले से चुपचाप ले आओ।

---

## 🔴 Problem it Solves
JavaScript is the **most expensive resource byte-for-byte**: it must be downloaded, parsed, compiled and executed on the main thread. On a low-end Android phone, 1 MB of JS can take **several seconds** of CPU.
Problems without splitting:
- Users download code for **every page and feature** (admin panel, charts, PDF export) just to see the home page.
- Long parse/execute tasks hurt **LCP, TTI and INP** (F05).
- A tiny change invalidates one giant file, so users re-download everything (poor caching).
Bundling plus splitting ensures users load **only what they need, when they need it**, with long-lived caching for unchanged chunks.

## 🔴 यह क्यों बना? (Hindi)
JavaScript सबसे महँगा है — download के बाद parse, compile और main thread पर चलाना पड़ता है; सस्ते Android पर 1 MB JS में कई सेकंड लग सकते हैं।
बिना splitting के हर यूज़र हर पेज का कोड (admin, charts, PDF) डाउनलोड करता है, LCP/INP बिगड़ते हैं, और छोटा बदलाव भी पूरी बड़ी file दोबारा डाउनलोड करवाता है। Splitting से सिर्फ़ ज़रूरी कोड, ज़रूरत के समय।

---

## 🟢 How it Works — Step by Step

### What a bundler does

```
src/index.tsx ──imports──► App.tsx ──► pages/Home.tsx ──► components/... ──► node_modules/lodash-es
      │
      ▼  1. Resolve module graph (all imports)
         2. Transform: TS/JSX → JS (esbuild/SWC/Babel), CSS modules/Tailwind, assets
         3. Tree-shake: drop unused exports (needs ES modules + sideEffects: false)
         4. Split: create chunks at dynamic import() boundaries + shared/vendor chunks
         5. Minify (Terser/esbuild/SWC), compress output (gzip/brotli at server/CDN)
         6. Hash filenames: main.3f9a1c.js → cache forever (immutable), HTML references new hashes
      ▼
dist/ index.html, main.[hash].js, home.[hash].js, checkout.[hash].js, vendor-react.[hash].js, *.css
```

### Splitting strategies

```
1. Route-based (biggest win):  /, /product/:id, /cart, /checkout, /account → separate chunks
   (Next.js does this automatically per page/route segment)
2. Component-based: heavy, rarely-used or below-the-fold: charts (recharts), rich text editor,
   maps, video player, emoji picker, PDF viewer, modal contents
3. Interaction-based: load on click/hover ("Open editor" → import('./Editor'))
4. Visibility-based: load when scrolled into view (IntersectionObserver)
5. Vendor/shared chunks: react/react-dom in a stable chunk → cached across deploys
6. Conditional/polyfills: load only for old browsers or specific locales (i18n JSON per language)
```

### Lazy ≠ slow: prefetch & preload

```
<link rel="preload">     → needed for THIS page, high priority (LCP image, critical font)
<link rel="modulepreload"> → JS module needed soon for this page
<link rel="prefetch">    → likely needed for NEXT navigation, low priority, idle time
Next.js <Link> prefetches routes in the viewport (production); React Router / TanStack Router: on hover
Prefetch on hover/touchstart of "Checkout" button → chunk ready by the time user clicks
```

### Tree shaking gotchas

```
✅ import { debounce } from 'lodash-es'          ❌ import _ from 'lodash' (CJS, whole lib ~70 KB)
✅ import { format } from 'date-fns'             ❌ moment.js with all locales (~300 KB)
✅ "sideEffects": false in package.json          ❌ barrel files (index.ts re-exporting everything)
                                                    can defeat tree shaking in some setups
Check: bundle analyzer (webpack-bundle-analyzer, @next/bundle-analyzer, rollup-plugin-visualizer,
       source-map-explorer), bundlephobia.com before adding a dependency
```

### Budgets (rule of thumb for mobile)

```
Initial JS (compressed) for a page: aim ≲ 150–200 KB gz; total route JS as low as possible
Each third-party script: justify it; load async/after interaction (chat widgets, heatmaps)
Fail CI if bundle grows beyond budget (size-limit, bundlewatch)
```

### Caching strategy with hashed chunks

```
index.html            → Cache-Control: no-cache (always revalidate; points to latest hashes)
/_next/static/*.js    → Cache-Control: public, max-age=31536000, immutable
After deploy: only changed chunks have new hashes → users re-download just those (Topic F07)
Handle "chunk load failed" after deploy (old HTML referencing deleted chunks) → keep old assets for a
while, or catch the error and reload the page
```

## 🟢 कैसे काम करता है? (Hindi)
1. Bundler सारे imports का graph बनाता है, TS/JSX को JS में बदलता है, बिना इस्तेमाल का कोड हटाता है (tree shaking), minify करता है और file नाम में hash लगाता है।
2. Splitting: हर route का अलग chunk (सबसे बड़ा फ़ायदा), भारी components (charts, editor, maps) अलग, click या scroll पर लोड, React जैसी vendor files अलग ताकि लंबे समय cache रहें।
3. Lazy का मतलब धीमा नहीं — hover पर prefetch, LCP image preload; Next.js `<Link>` अपने-आप prefetch करता है।
4. Tree shaking के लिए ES module वाली libraries (lodash-es, date-fns), बड़े barrel files से बचो; bundle analyzer से देखो क्या भारी है।
5. Hash वाली files को एक साल cache, index.html को no-cache; deploy के बाद "chunk load failed" को संभालो (पुरानी files कुछ समय रखो या reload)।

---

## 🟡 Real World Example

**Twitter Lite / Pinterest / Flipkart Lite PWAs** — all used aggressive route-based code splitting, small app shells and prefetching to make their mobile web usable on 2G/3G in emerging markets. Pinterest reported cutting core JS from ~650 KB to ~150 KB.

**Next.js** — automatic per-route splitting, shared chunk optimization and prefetching of in-viewport `<Link>`s. Turbopack and Rspack (Rust-based bundlers) speed up dev and build for large apps.

**Google Maps / Docs** — load core functionality first and lazy-load features (street view, add-ons, editing tools) on demand.

**React Native (Metro + Hermes)** — Metro bundles a single JS bundle per platform. Hermes precompiles it to bytecode at build time (faster startup), and "inline requires" defer module evaluation until first use (Topic M03).

## 🟡 Real Example Hindi में
Twitter Lite, Pinterest और Flipkart Lite ने route के हिसाब से code splitting, छोटा app shell और prefetch से 2G/3G पर भी तेज़ mobile web बनाया — Pinterest ने core JS ~650 KB से ~150 KB किया।
React Native में Metro एक bundle बनाता है, Hermes उसे पहले से bytecode में बदल देता है, और inline requires से modules तभी चलते हैं जब पहली बार चाहिए।

---

## 🟠 My Stack Example

### React (Vite) — route + component splitting
```tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const Product = lazy(() => import('./pages/Product'));
const Checkout = lazy(() => import('./pages/Checkout'));           // only loaded when user goes there
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'));

const router = createBrowserRouter([
  { path: '/', element: <Suspense fallback={<PageSkeleton />}><Home /></Suspense> },
  { path: '/p/:id', element: <Suspense fallback={<PageSkeleton />}><Product /></Suspense> },
  { path: '/checkout', element: <Suspense fallback={<PageSkeleton />}><Checkout /></Suspense> },
  { path: '/admin', element: <Suspense fallback={<PageSkeleton />}><AdminDashboard /></Suspense> },
]);
export default () => <RouterProvider router={router} />;

// Prefetch on hover: start the import early (module cache makes the later lazy() instant)
const prefetchCheckout = () => import('./pages/Checkout');
<button onMouseEnter={prefetchCheckout} onTouchStart={prefetchCheckout}>Checkout</button>
```

### Next.js — heavy client-only component lazily
```tsx
'use client';
import dynamic from 'next/dynamic';
const SalesChart = dynamic(() => import('@/components/SalesChart'), {
  ssr: false,                                    // chart lib touches window
  loading: () => <div style={{ height: 320 }} aria-busy="true">Loading chart…</div>,  // reserve space (no CLS)
});
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

export default function OrderTracking({ order }) {
  const [showMap, setShowMap] = useState(false);
  return (<>
    <OrderSummary order={order} />
    <button onClick={() => setShowMap(true)}>Track on map</button>
    {showMap && <MapView lat={order.rider.lat} lng={order.rider.lng} />}   {/* interaction-based */}
  </>);
}
```

### Lazy-load heavy library inside a handler
```ts
async function exportInvoicePdf(order: Order) {
  const { jsPDF } = await import('jspdf');       // ~300 KB only when user clicks "Download PDF"
  const doc = new jsPDF(); doc.text(`Invoice #${order.id}`, 10, 10); doc.save(`invoice-${order.id}.pdf`);
}
```

### Vite manual vendor chunks + analyzer
```ts
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';
export default defineConfig({
  plugins: [react(), visualizer({ filename: 'stats.html', gzipSize: true })],
  build: { rollupOptions: { output: { manualChunks: { react: ['react', 'react-dom'], charts: ['recharts'] } } } },
});
```

### Bundle budget in CI (size-limit)
```json
// package.json
"size-limit": [
  { "path": "dist/assets/index-*.js", "limit": "160 KB" },
  { "path": "dist/assets/Checkout-*.js", "limit": "60 KB" }
],
"scripts": { "size": "size-limit" }
```

### Recover from chunk load errors after a deploy
```ts
window.addEventListener('vite:preloadError', () => window.location.reload());   // Vite
// Or wrap lazy(): retry import once, then reload
const lazyWithRetry = (fn: () => Promise<any>) => lazy(() => fn().catch(() => { location.reload(); return new Promise(() => {}); }));
```

### React Native (Metro)
```js
// metro.config.js — defer module execution until first use (faster startup)
module.exports = { transformer: { getTransformOptions: async () => ({ transform: { inlineRequires: true } }) } };
// Lazy screens with React Navigation: screens mount on first visit by default (tabs: lazy: true)
// Keep heavy libs out of the startup path: import them inside the screen that needs them
```

---

## ⚫ Interview Questions + Answers

**Q1: What is code splitting and how would you apply it?**
A1: Code splitting breaks the application bundle into smaller chunks loaded on demand, so users download only what the current view needs. Apply it per route first (the biggest win), then to heavy or rarely used components (charts, editors, maps, modals), interaction-triggered features (load on click) and below-the-fold sections (load on visibility). Keep stable vendor chunks for caching. Combine with prefetching on hover, idle or in-viewport links so navigation stays instant, and show skeletons with reserved space.

**Q2: What is tree shaking and why might it not work?**
A2: Tree shaking is dead-code elimination based on static ES module imports and exports: unused exports are dropped from the bundle. It fails with CommonJS modules (dynamic `require`), libraries with side effects not marked `sideEffects: false`, importing whole namespaces or default-exported objects, some barrel-file re-export patterns, and code with dynamic property access. Prefer ESM libraries with per-function imports and verify with a bundle analyzer.

**Q3: Lazy loading can make interactions slower. How do you avoid that?**
A3: Prefetch likely-needed chunks during idle time, on hover, touchstart or focus, or when links enter the viewport. Preload critical resources for the current page. Keep chunks reasonably sized (not hundreds of tiny ones). Show immediate feedback (skeletons, optimistic UI). Cache chunks with immutable hashed URLs (plus a service worker for repeat visits). Don't lazy-load above-the-fold content or the LCP element.

**Q4: How do you investigate a large bundle?**
A4: Run a bundle analyzer (webpack-bundle-analyzer, @next/bundle-analyzer, rollup-plugin-visualizer, source-map-explorer) to see what's in each chunk. Look for duplicate libraries and versions, large dependencies (moment, lodash, chart libraries, icon packs imported wholesale), polyfills for modern browsers, and code that should be split by route or lazily loaded. Replace or trim heavy dependencies, enforce budgets in CI, and check bundle cost before adding packages.

**Q5: How do caching and hashing work for bundles, and what breaks after a deploy?**
A5: Output files get content hashes in their names, so they can be served with long-lived `immutable` caching, while the HTML (or manifest) that references them is revalidated on each load. Only changed chunks get new hashes, so users re-download just those. After a deploy, a user with old HTML may request an old chunk that no longer exists, producing a ChunkLoadError. Mitigate by keeping previous assets available for a while (immutable asset storage on a CDN), and by catching the error to reload or retry.

---

## 🔷 Trade-offs
✅ Smaller initial load, better LCP/INP, better caching.
❌ Too many tiny chunks → request overhead, waterfalls (chunk needs another chunk).
❌ Lazy content can cause loading spinners & CLS if not prefetched/space reserved.
❌ SSR + lazy components need care (ssr:false parts render later).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bundler | Tool combining modules into bundles | files जोड़ने वाला tool |
| Chunk | A piece of the split bundle | bundle का टुकड़ा |
| Code splitting | Splitting code into on-demand chunks | कोड को टुकड़ों में बाँटना |
| Lazy loading | Load only when needed | ज़रूरत पर लाना |
| Tree shaking | Removing unused exports | बेकार कोड हटाना |
| Minification | Shrinking code size | कोड छोटा करना |
| Content hash | Filename hash for caching | cache के लिए नाम में hash |
| Prefetch | Low-priority load for next page | अगले पेज का पहले से |
| Preload | High-priority load for current page | अभी के पेज का ज़रूरी |
| Metro | React Native bundler | RN का bundler |

---

## ⚡ 3-Line Summary
**English:**
1. Bundlers resolve, transpile, tree-shake, minify and hash code into chunks; JS is the costliest resource on mobile.
2. Split by route first, then heavy/rare components, interactions and visibility; keep stable vendor chunks.
3. Prefetch to keep lazy fast, enforce bundle budgets in CI, and handle chunk-load errors after deploys.

**Hindi:**
1. Bundler कोड जोड़ता, बदलता, बेकार हटाता, छोटा करता और hash लगाता है; mobile पर JS सबसे महँगा।
2. पहले route से split, फिर भारी components, click/scroll पर लोड; vendor chunks अलग।
3. Prefetch से lazy भी तेज़, CI में bundle budget, deploy के बाद chunk error संभालो।

---

## ➡️ Next Topic Suggestion
**F07. Browser Caching (Cache-Control, ETag)** — Once assets are split and hashed, HTTP caching decides whether the browser even needs to download them again. Next: Cache-Control directives, ETag/Last-Modified revalidation, and caching strategies per resource type.
