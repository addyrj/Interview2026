# 70. Code Splitting in React
# हिंदी में: Code Splitting — Bundle को छोटे टुकड़ों में बांटना

---

## 🔵 Simple Definition (English)
**Code splitting** means breaking your app's JavaScript bundle into smaller chunks, so the browser downloads only what the current screen needs. In React it is done with dynamic `import()`, which `React.lazy`, `next/dynamic` and bundlers (Vite, webpack, Turbopack) turn into separate files.

## 🔵 सरल परिभाषा (Hindi)
**Code splitting** का मतलब है app के JavaScript bundle को छोटे chunks में बांटना, ताकि browser को सिर्फ वही code download करना पड़े जो current screen के लिए चाहिए। React में यह dynamic `import()` से होता है। `React.lazy`, `next/dynamic` और bundlers (Vite, webpack, Turbopack) इसे अलग files में बदल देते हैं।

---

## 🔴 Problem it Solves
एक single bundle में पूरी app होती है: login, admin panel, charts, PDF generator, सब कुछ। Mobile पर 4G के कमज़ोर signal में 3-4 MB JavaScript download और parse करने में कई सेकंड लगते हैं। User सिर्फ login page देखने आया, फिर भी admin panel का code download हो रहा है। इससे Time to Interactive (TTI) बिगड़ता है।

## 🔴 यह क्यों बना? (Hindi)
Razorpay checkout या Paytm login पर user को सिर्फ payment form चाहिए, पर bundle में refund dashboard और reports का code भी होता है। Code splitting से initial download छोटा रहता है, और बाकी code user के वहां पहुंचने पर लोड होता है। Performance budget और Core Web Vitals (LCP, INP) दोनों में सुधार होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Code में dynamic import() लिखो (static import की जगह)
         const Admin = () => import('./AdminPanel');   // static import नहीं

Step 2 → Bundler (webpack / Vite / Turbopack) इसे अलग chunk बनाता है
         main.js          ← initial bundle (छोटा)
         admin.chunk.js   ← import() वाला code (अलग file)

Step 3 → Route या interaction पर import() चलता है
         → Browser network से chunk download करता है

Step 4 → Chunk आने के बाद module resolve होता है और UI render होता है
         (React.lazy या next/dynamic में Suspense fallback के साथ)

Step 5 → Chunk browser cache में रहता है, दूसरी बार instant load

KEY: Split points वहीं लगाओ जहां user की navigation या interaction हो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Static import की जगह dynamic import() लिखो
Step 2 → Bundler अलग chunk file बनाता है
Step 3 → Route या click पर import() चलता है → chunk download
Step 4 → Module आने पर UI render होता है (fallback के साथ)
Step 5 → Chunk cache होता है, दोबारा download नहीं
KEY: Split वहीं करो जहां user navigation या interaction होता है
```

---

## 🟡 Real World Example
**Flipkart:** Home page का bundle छोटा है। Product page, cart, और seller dashboard अलग chunks हैं। कोई buyer seller dashboard के code को कभी download नहीं करता। Route change पर chunk आता है, और Next.js इसे automatically हर page के लिए अलग तरह से करता है। इससे first load तेज़ रहता है।

## 🟡 Real Example Hindi mein
**Flipkart:** Home page का bundle छोटा है। Product page, cart और seller dashboard अलग chunks हैं। कोई buyer seller dashboard का code कभी download नहीं करता। Route बदलने पर chunk आता है। इससे पहली बार app खोलने की speed बढ़ती है।

---

## 💻 Code Example — Basic

```jsx
import { Suspense, lazy } from 'react';           // lazy और Suspense React से लो
import { BrowserRouter, Routes, Route } from 'react-router-dom'; // routing library (SPA में)

// ── BASIC: हर route का code अलग chunk में ──
// import() call होने पर ही bundler उस file को download करता है
const Home = lazy(() => import('./pages/Home'));           // Home का chunk
const Admin = lazy(() => import('./pages/AdminPanel'));    // Admin का chunk (बड़ा)

export default function App() {
  return (
    <BrowserRouter>                                        {/* client-side routing शुरू */}
      {/* Suspense सभी routes के लिए एक fallback देता है */}
      <Suspense fallback={<p>Page load ho raha hai...</p>}>
        <Routes>                                           {/* कौन सा route match हुआ, वही render */}
          <Route path="/" element={<Home />} />            {/* / पर सिर्फ Home chunk मांगा जाएगा */}
          <Route path="/admin" element={<Admin />} />      {/* /admin तक Admin chunk नहीं आएगा */}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { Suspense, lazy, useEffect, useState } from 'react';

// ── Production code splitting: named export, preload, error handling ──

// Named export को default में बदलना: factory में .then() से module map करो
const ReportsPage = lazy(() =>
  import('./features/reports/ReportsPage')          // module object लौटता है
    .then(mod => ({ default: mod.ReportsPage }))    // lazy को { default } चाहिए
);

// Preload helper: idle time पर chunk download करो ताकि navigation instant लगे
const preloadReports = () => import('./features/reports/ReportsPage'); // cache हो जाता है

// यह component idle होने पर preload शुरू करता है
function usePreloadOnIdle(loader) {
  useEffect(() => {
    // requestIdleCallback browser idle होने पर चलता है; Safari पर नहीं है, इसलिए fallback
    const schedule = window.requestIdleCallback ?? (cb => setTimeout(cb, 2000));
    const id = schedule(() => loader());            // idle पर chunk download करो
    return () => {
      // cleanup: component unmount हो तो pending idle callback रद्द करो
      if (window.cancelIdleCallback) window.cancelIdleCallback(id);
      else clearTimeout(id);
    };
  }, [loader]);                                     // loader बदले तो दोबारा schedule
}

// Chunk load fail होने पर (network issue, deploy के बाद पुराना hash) retry करो
function loadWithRetry(loader, retries = 1) {
  return loader().catch(err => {                    // पहली बार fail हुआ
    if (retries <= 0) throw err;                    // retries खत्म → error boundary पकड़ेगी
    return loadWithRetry(loader, retries - 1);      // फिर से try
  });
}

const ReportsLazy = lazy(() =>
  loadWithRetry(() => import('./features/reports/ReportsPage'))
    .then(mod => ({ default: mod.ReportsPage }))    // retry के बाद भी same mapping
);

export default function Dashboard({ user }) {
  const [showReports, setShowReports] = useState(false); // reports tab खुला है या नहीं
  usePreloadOnIdle(preloadReports);                      // खाली समय में chunk तैयार

  return (
    <div>
      <h1>Dashboard, {user.name}</h1>
      <button onMouseEnter={preloadReports}           // hover पर भी preload (दोहराव ठीक है, cache है)
              onClick={() => setShowReports(true)}>
        Reports खोलो
      </button>
      {showReports && (
        <Suspense fallback={<p>Reports load ho rahi hain...</p>}>
          <ReportsLazy />                              {/* chunk तैयार होने पर render */}
        </Suspense>
      )}
    </div>
  );
}
```

---

## 🟠 Real app integration

**Next.js App Router** में हर route segment अपने-आप अलग chunk बनता है, इसलिए manual `lazy` की ज़रूरत कम पड़ती है। Heavy component को manually split करने के लिए `next/dynamic` use होता है।

```jsx
// app/products/[id]/page.js — Server Component: route अपने-आप अलग chunk है
import ReviewsSection from '@/components/ReviewsSection'; // server-side render होगा, client JS नहीं

export default async function ProductPage({ params }) {
  const { id } = await params;                     // Next 15+: params एक Promise है, इसलिए await
  return (
    <main>
      <h1>Product {id}</h1>
      <ReviewsSection productId={id} />            {/* server पर render, bundle में नहीं */}
    </main>
  );
}
```

```jsx
// components/ImageEditor.js — Client Component के अंदर बड़ी library को split करना
'use client';                                      // Client Component
import dynamic from 'next/dynamic';                // Next.js का code-split helper

// Canvas editor library (बड़ी) सिर्फ तब लोड हो जब user "Edit" दबाए
const Editor = dynamic(() => import('./Editor'), {
  ssr: false,                                      // browser-only: server पर बनाना नहीं
  loading: () => <p>Editor load ho raha hai...</p>, // chunk आने तक fallback
});

export default function ImageEditor({ open }) {
  return open ? <Editor /> : null;                 // बंद हो तो chunk download ही नहीं
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Static import से code split करने की उम्मीद करना
```jsx
// ❌ Wrong: static import हमेशा main bundle में जाता है
import AdminPanel from './AdminPanel'; // bundler इसे अलग chunk नहीं बनाएगा
export default function App() { return <AdminPanel />; }

// ✅ Right: dynamic import() + lazy — अलग chunk बनेगा
import { lazy } from 'react';
const AdminPanel = lazy(() => import('./AdminPanel')); // यह file अलग chunk में जाएगी
export default function App() { return <AdminPanel />; }
```

❌ **Mistake 2:** Hover या click पर हर बार नया `import()` बनाना ही split का फायदा समझना, बिना Suspense या error handling के
```jsx
// ❌ Wrong: chunk fail हुआ तो पूरा page crash, कोई fallback नहीं
const Reports = lazy(() => import('./Reports'));
export default function Page() { return <Reports />; } // Suspense और ErrorBoundary दोनों गायब

// ✅ Right: Suspense fallback + Error Boundary (topic 68) के साथ
import { Suspense, lazy } from 'react';
import ErrorBoundary from './ErrorBoundary';                  // topic 68 वाला boundary
const Reports = lazy(() => import('./Reports'));
export default function Page() {
  return (
    <ErrorBoundary>                                            {/* chunk fail → fallback */}
      <Suspense fallback={<p>Loading...</p>}><Reports /></Suspense>
    </ErrorBoundary>
  );
}
```

---

## 🧠 Tricky Interview Question

```jsx
// utils.js
export const formatPrice = (p) => `₹${p}`;

// Page.js
import { formatPrice } from './utils';         // static import
const Heavy = lazy(() => import('./utils'));   // dynamic import, SAME file

export default function Page() {
  return <p>{formatPrice(100)}</p>;
}
// Question: क्या `utils.js` अलग chunk में जाएगा? और क्या dynamic import वाला
// `Heavy` कोई फायदा देगा?
```

**Answer:** नहीं, `utils.js` अलग chunk में नहीं जाएगा। `Page.js` उसे static `import` से पहले से use कर रहा है, इसलिए वह main bundle में होगा। Bundler dynamic import वाला हिस्सा तभी split कर सकता है जब वह module कहीं और static रूप से use न हो। इसलिए `Heavy` के लिए कोई अलग download नहीं होगा, वह module पहले से main bundle में है। Lazy तभी फायदा देता है जब module सिर्फ dynamic रूप से import हो। Module के बड़े हिस्से को अलग करने के लिए helper को अलग file में रखो जो page में static import न हो, या heavy code को सिर्फ lazy path से use करो।

---

## ⚫ Interview Questions + Answers

**Q1: Code splitting क्या है और इसका मुख्य फायदा क्या है?**
A1: Bundle को छोटे chunks में बांटना, ताकि initial load पर सिर्फ ज़रूरी code download हो। इससे first load time, Time to Interactive और bandwidth बचती है।

**Q2: React में code splitting कैसे होता है?**
A2: Dynamic `import()` से। `React.lazy(() => import(...))` component-level split देता है, और `next/dynamic` या route-level lazy loading page-level split देता है। Bundler (webpack, Vite, Turbopack) import को अलग file में बनाता है।

**Q3: Route-based और component-based splitting में क्या अंतर है?**
A3: Route-based splitting में हर page का अलग chunk बनता है (Next.js में automatic)। Component-based splitting में किसी एक heavy component (chart, editor, map) को अलग chunk में रखा जाता है। दोनों को मिलाकर उपयोग करना सबसे अच्छा है।

**Q4: `import()` और `import` में क्या फर्क है?**
A4: Static `import` build time पर resolve होता है और हमेशा bundle में जाता है। `import()` runtime पर call होता है, एक Promise लौटाता है, और इसी से bundler एक अलग chunk बनाता है।

**Q5: Code splitting के बाद performance कैसे जांचें?**
A5: `next build` का output (route size और First Load JS), webpack-bundle-analyzer या `rollup-plugin-visualizer`, और Chrome DevTools की Coverage और Network tab से chunk sizes और load timing देखें।

---

## 🔷 When to Use + When Not to Use
✅ **Use code splitting when:**
- Bundle size 200-300 KB (gzipped) से बड़ा हो और कई routes हों
- Heavy libraries हों (charts, editors, PDF, maps, rich-text)
- Admin या role-based screens हैं जो हर user को नहीं चाहिए
- Modal या tab के अंदर का content हो, जो सामान्य रूप से नहीं खुलता

❌ **Avoid when:**
- Component छोटा है और हर page पर दिखता है (नुकसान, extra network request)
- Above-the-fold UI को lazy कर रहे हो (LCP बिगड़ता है)
- Bundle पहले से छोटा है और measurement में फायदा नहीं दिखा
- Module पहले से static import हो — इससे split होगा ही नहीं

---

## 📊 Visual Diagram

```
  WITHOUT code splitting:
  ┌──────────────────────────────────────────┐
  │ main.js (3.2 MB)                         │
  │  login + home + admin + charts + PDF ... │  ◄── सब एक साथ download
  └──────────────────────────────────────────┘

  WITH code splitting:
  ┌───────────────┐
  │ main.js 180KB │ ◄── initial load (login/home)
  └───────────────┘
        │  user navigates / clicks
        ├──► admin.chunk.js   (800 KB)  ── only /admin
        ├──► charts.chunk.js  (400 KB)  ── only dashboard
        └──► pdf.chunk.js     (300 KB)  ── only "Download PDF"

  Browser cache: each chunk downloaded ONCE, reused later ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code splitting | Bundle को chunks में बांटना | Bundle को छोटे टुकड़ों में बांटना |
| Chunk | Split होकर बनी अलग JS file | Split से बनी अलग JS file |
| Dynamic import | Runtime पर module लाने वाला `import()` | Runtime पर module लाने वाला `import()` |
| Route-based splitting | हर route का अलग chunk | हर route की अलग file |
| Preload | ज़रूरत से पहले chunk download करना | ज़रूरत से पहले code लाना |
| Time to Interactive (TTI) | Page पूरी तरह interactive होने का समय | Page पूरी तरह चलने लायक होने का समय |

---

## ⚡ 3-Line Summary
**English:**
1. Code splitting bundle को chunks में बांटता है ताकि user सिर्फ वही download करे जो चाहिए।
2. React में dynamic `import()` से (`React.lazy`, `next/dynamic`), और static import से split नहीं होता।
3. Route-level split Next.js में automatic है; heavy components के लिए `next/dynamic` और bundle analyzer use करो।

**Hindi:**
1. Code splitting bundle को chunks में बांटता है ताकि user सिर्फ वही download करे जो उसे चाहिए।
2. React में dynamic `import()` से (`React.lazy`, `next/dynamic`) split होता है, static import से नहीं।
3. Next.js में route-level split automatic है; heavy components के लिए `next/dynamic` और bundle analyzer use करो।

---

## ➡️ Next Topic
**72. When to use React.memo** — memo कब लगाएं और कब नहीं, profiler से decision कैसे लें, और React Compiler का असर।
