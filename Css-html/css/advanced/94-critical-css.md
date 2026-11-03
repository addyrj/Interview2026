# 94. Critical CSS
# हिंदी में: Critical CSS — पहली Screen का CSS पहले

---

## 🔵 Simple Definition (English)
**Critical CSS** is the minimum CSS needed to render the **above-the-fold** content (what the user sees without scrolling). You **inline** it in a `<style>` tag in `<head>` and load the remaining CSS **asynchronously**, so the first paint is not blocked by a big stylesheet.

## 🔵 सरल परिभाषा (Hindi)
**Critical CSS** वो न्यूनतम CSS है जो **above-the-fold** (बिना scroll किए दिखने वाला हिस्सा) render करने के लिए ज़रूरी है। इसे `<head>` में `<style>` के अंदर **inline** कर देते हैं और बाकी CSS **बाद में (async)** load करते हैं, ताकि बड़ी stylesheet पहला paint न रोके।

---

## 🔴 Problem it Solves
```
BEFORE:
  <link rel="stylesheet" href="app.css">     ← 300 KB, render-blocking
  Timeline on slow 4G:
    HTML arrives ─ wait ─ wait ─ app.css downloads (1.5 s) ─ FIRST PAINT
    Users stare at a WHITE screen for 1.5+ seconds.

AFTER (Critical CSS):
  <style>/* 8 KB: header, hero, fonts */</style>   ← inline, arrives WITH the HTML
  <link rel="stylesheet" href="app.css" media="print" onload="this.media='all'">
    HTML arrives ─ FIRST PAINT (header + hero styled) ─ rest loads in background
  Better FCP / LCP, higher Lighthouse score, lower bounce rate.
```

## 🔴 यह क्यों बना? (Hindi)
बड़ी CSS file पूरी download होने तक browser कुछ paint नहीं करता — user को सफ़ेद screen दिखती है, खासकर slow mobile network पर। Critical CSS से HTML के साथ ही ज़रूरी styles आ जाते हैं, इसलिए पहली screen तुरंत दिखती है।

---

## 🟢 How it Works — Step by Step

```
STEP 1: IDENTIFY above-the-fold content (header, hero, first cards) at common viewports
        (mobile 375x667, tablet, desktop 1300x900).
STEP 2: EXTRACT only the CSS rules that style those elements
        - Tools: "critical" (npm), Critters (used by Next.js older versions / Angular),
          Penthouse, Chrome DevTools Coverage tab (manual).
STEP 3: INLINE it in <head> inside <style>. Keep it small (guideline: under ~14 KB
        compressed, so it fits in the first TCP round trip, "14 KB rule").
STEP 4: LOAD THE FULL CSS WITHOUT BLOCKING
        Pattern A (classic):
          <link rel="stylesheet" href="app.css" media="print" onload="this.media='all'">
          <noscript><link rel="stylesheet" href="app.css"></noscript>
        Pattern B (preload):
          <link rel="preload" href="app.css" as="style" onload="this.rel='stylesheet'">
          <noscript><link rel="stylesheet" href="app.css"></noscript>
STEP 5: TEST — check for FOUC (Flash Of Unstyled Content) below the fold, and
        re-generate critical CSS whenever the design changes (automate in CI/build).

HOW "media=print + onload" WORKS:
  - A stylesheet with a non-matching media query is downloaded at LOW priority and
    does NOT block rendering.
  - When it finishes (onload), JS flips media to "all" → styles apply.
  - <noscript> fallback loads it normally if JS is disabled.

TRADE-OFFS:
  + Faster First Contentful Paint (FCP) and LCP
  - Inline CSS is NOT cached separately; it is re-sent with every HTML page
  - Needs build tooling; duplicated rules (critical + full file)
  - Not useful for tiny sites where total CSS is a few KB
  - HTTP/2 push is removed from browsers; use preload / 103 Early Hints instead

ALTERNATIVES:
  - Split CSS per route/component (CSS Modules, Next.js does automatically)
  - Small total CSS with Tailwind (10-30 KB) — often no need for manual critical CSS
  - Streaming SSR + per-component CSS
```

## 🟢 कैसे काम करता है? (Hindi)
1. **पहचानो:** पहली screen पर कौन से elements दिखते हैं (header, hero)।
2. **निकालो:** सिर्फ उन्हीं की CSS rules extract करो (tool: `critical`, Penthouse, Critters)।
3. **Inline करो:** `<head>` में `<style>` के अंदर रखो; छोटा रखो (लगभग 14 KB से कम)।
4. **बाकी CSS बाद में:** `media="print"` + `onload="this.media='all'"` पैटर्न से — ये low priority में download होती है और render नहीं रोकती। `<noscript>` fallback रखो।
5. **Trade-off:** inline CSS अलग से cache नहीं होती, build tooling चाहिए, और छोटी sites के लिए ज़रूरी नहीं।

---

## 🟡 Real World Example
**Amazon / Flipkart / news sites (NYTimes, Guardian):** Home page ke upar ka header, search bar aur banner ka CSS HTML me hi inline hota hai. Page ke neeche ke carousels, footer aur modal ki CSS baad me aati hai. Isse user ko 4G par bhi pehle second me navigation aur hero dikh jata hai.
**Zomato mobile web:** Pehli screen (location bar + search + first cards) fast render hoti hai; filters ke popup ki CSS baad me load hoti hai.
**Google Search results page:** Poora CSS inline hota hai kyunki page bahut chhota hai.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart / news sites:** Home page के ऊपर के header, search bar और banner की CSS HTML में ही inline होती है। नीचे के carousels, footer और modal की CSS बाद में आती है। इसलिए 4G पर भी पहले second में navigation और hero दिख जाते हैं।
**Google Search results:** पूरा CSS inline होता है क्योंकि page बहुत छोटा है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Critical CSS Pattern</title>

  <!-- ══════════ 1. CRITICAL CSS (inline): header + hero only ══════════ -->
  <style>
    /* tiny reset */
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; color: #222; }

    /* header (above the fold) */
    .site-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 12px 20px; background: #232f3e; color: #fff;
    }
    .logo { font-weight: 700; font-size: 20px; }

    /* hero (above the fold) */
    .hero {
      min-height: 60vh; display: grid; place-items: center; text-align: center;
      padding: 20px; background: linear-gradient(135deg, #ff9900, #ffcc66);
    }
    .hero h1 { font-size: clamp(28px, 6vw, 56px); margin: 0 0 8px; }
    .hero .cta { display: inline-block; padding: 12px 24px; background: #232f3e; color: #fff;
                 border-radius: 8px; text-decoration: none; }
  </style>

  <!-- ══════════ 2. NON-CRITICAL CSS: loaded without blocking render ══════════ -->
  <!-- For this single-file demo the "full" stylesheet is a data: URL.
       In a real project: href="/css/app.css" -->
  <link rel="stylesheet"
        href="data:text/css,.products%7Bdisplay%3Agrid%3Bgrid-template-columns%3Arepeat(auto-fill%2Cminmax(180px%2C1fr))%3Bgap%3A16px%3Bpadding%3A20px%7D.product%7Bbackground%3A%23f5f5f5%3Bborder-radius%3A12px%3Bpadding%3A16px%3Bmin-height%3A120px%7D.site-footer%7Bpadding%3A24px%3Bbackground%3A%23eee%3Btext-align%3Acenter%7D"
        media="print"
        onload="this.media='all'">   <!-- flips to 'all' when downloaded -->

  <!-- Fallback if JavaScript is disabled: load normally -->
  <noscript>
    <link rel="stylesheet" href="data:text/css,.products%7Bdisplay%3Agrid%3Bgrid-template-columns%3Arepeat(auto-fill%2Cminmax(180px%2C1fr))%3Bgap%3A16px%3Bpadding%3A20px%7D.product%7Bbackground%3A%23f5f5f5%3Bborder-radius%3A12px%3Bpadding%3A16px%3Bmin-height%3A120px%7D.site-footer%7Bpadding%3A24px%3Bbackground%3A%23eee%3Btext-align%3Acenter%7D">
  </noscript>
</head>
<body>
  <!-- ABOVE THE FOLD: styled by the inline critical CSS -->
  <header class="site-header">
    <span class="logo">ShopFast</span>
    <nav>Home | Deals | Cart</nav>
  </header>

  <section class="hero">
    <div>
      <h1>Big Sale is Live</h1>
      <p>Up to 70% off on electronics</p>
      <a class="cta" href="#products">Shop now</a>
    </div>
  </section>

  <!-- BELOW THE FOLD: styled by the async stylesheet -->
  <main id="products" class="products">
    <article class="product">Product 1</article>
    <article class="product">Product 2</article>
    <article class="product">Product 3</article>
    <article class="product">Product 4</article>
  </main>

  <footer class="site-footer">Footer content</footer>
</body>
</html>
```

```js
// build-critical.js: generate critical CSS automatically (Node, run at build time)
// npm i -D critical
const { generate } = require('critical');

generate({
  inline: true,                 // inject <style> into the HTML
  base: 'dist/',                // folder that has index.html + css
  src: 'index.html',
  target: { html: 'index-critical.html' },
  width: 1300, height: 900,     // desktop viewport (run again for mobile: 375 x 667)
}).then(() => console.log('critical CSS inlined'));
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Next.js (App Router / Pages Router) already splits CSS per route and
//    inlines/links the CSS needed for the current page. CSS Modules and
//    Tailwind are chunked automatically, so manual critical CSS is rarely needed.

// 2. Experimental: next.config.js  →  experimental: { optimizeCss: true }
//    (uses Critters to inline critical CSS; check current docs because
//    experimental flags change between versions)

// 3. Manual inline of a small critical block in a layout:
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <style dangerouslySetInnerHTML={{ __html: `
          body{margin:0;font-family:system-ui}
          .hero{min-height:60vh;display:grid;place-items:center}
        `}} />
      </head>
      <body>{children}</body>
    </html>
  );
}
// Only for static CSS you control: never inject user input with dangerouslySetInnerHTML.

// 4. Fonts: next/font avoids layout shift and inlines @font-face CSS for you.

// 5. Lazy-load below-the-fold components so their CSS arrives later:
import dynamic from 'next/dynamic';
const Reviews = dynamic(() => import('./Reviews'));   // Reviews.module.css loads with this chunk

// 6. Frameworks that do this for you: Gatsby, Astro (scoped CSS inline), Remix links(),
//    Vite plugin "vite-plugin-critical".
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Critical CSS and why use it?**
A1: It is the CSS required to style above-the-fold content, inlined in the HTML `<head>`. Because external CSS is render-blocking, inlining the critical part lets the browser paint immediately without waiting for a network request. It improves First Contentful Paint and Largest Contentful Paint, especially on slow networks.

**Q2: How do you load the rest of the CSS without blocking rendering?**
A2: `<link rel="stylesheet" href="app.css" media="print" onload="this.media='all'">` with a `<noscript>` fallback, or `<link rel="preload" as="style" onload="this.rel='stylesheet'">`. A stylesheet whose media does not match is non-blocking; once loaded, switching media applies it.

**Q3: What are the drawbacks of Critical CSS?**
A3: Inline CSS cannot be cached independently and is re-downloaded with each HTML response; it needs build tooling and maintenance when design changes; it duplicates rules; there is a risk of FOUC when something below the fold is not covered; and for small CSS (Tailwind 15 KB) the benefit is minimal.

**Q4: How big should critical CSS be?**
A4: A common guideline is under about 14 KB compressed (the initial TCP congestion window is about 10 packets, roughly 14 KB), so it arrives in the first round trip along with HTML. It is a rule of thumb, not a hard limit.

**Q5: How is critical CSS different from code splitting CSS?**
A5: Code splitting breaks CSS into per-route or per-component files loaded as needed (cacheable). Critical CSS extracts the minimum for the first screen of a page and inlines it. They are complementary: split by route, then inline the critical part of the entry route.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Inlining all CSS
```html
<!-- WRONG: 300 KB inside HTML on every page, no caching, HTML parse slows -->
<style>/* entire app.css */</style>

<!-- CORRECT: only above-the-fold (small) + async load of the rest -->
```

❌ **Mistake 2:** Forgetting the `<noscript>` fallback
```html
<!-- WRONG: users with JS disabled never get the rest of the CSS -->
<link rel="stylesheet" href="app.css" media="print" onload="this.media='all'">

<!-- CORRECT: add -->
<noscript><link rel="stylesheet" href="app.css"></noscript>
```

❌ **Mistake 3:** Generating critical CSS once and never updating
```
WRONG: manual copy-paste, design changes, header looks broken for a moment on load
CORRECT: generate in the build pipeline (CI) for mobile AND desktop viewports
```

❌ **Mistake 4:** Including fonts or large images in the critical block
```css
/* WRONG: base64 fonts/images inside critical CSS bloat it beyond 14 KB */
/* CORRECT: preload the key font file: <link rel="preload" as="font" type="font/woff2" crossorigin href="..."> */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Above the fold | Visible area without scrolling | बिना scroll दिखने वाला हिस्सा |
| Critical CSS | Minimum CSS for first screen | पहली screen का न्यूनतम CSS |
| Render-blocking | Delays first paint | Paint रोकने वाला |
| FCP | First Contentful Paint | पहली बार content दिखना |
| LCP | Largest Contentful Paint | सबसे बड़ा element दिखना |
| FOUC | Flash of Unstyled Content | बिना style की झलक |
| Inline CSS | CSS inside <style> in HTML | HTML के अंदर CSS |
| preload | Hint to fetch a resource early | पहले से fetch करने का hint |
| 14 KB rule | Size to fit the first network round | पहले round में आने की सीमा |

---

## ⚡ 3-Line Summary
**English:**
1. Critical CSS is the small CSS needed for the first visible screen, inlined in `<head>` so painting does not wait for a stylesheet.
2. Load the remaining CSS non-blocking using `media="print"` + `onload` (with `<noscript>`) or `rel="preload"`.
3. Generate it in the build with tools (critical, Critters), keep it small (about 14 KB), and note frameworks like Next.js already split CSS per route.

**Hindi:**
1. Critical CSS पहली screen का छोटा CSS है जो `<head>` में inline होता है ताकि paint रुके नहीं।
2. बाकी CSS `media="print"` + `onload` (और `<noscript>`) या `preload` से बिना block किए load करो।
3. Build में tools (critical, Critters) से बनाओ, छोटा रखो (लगभग 14 KB); Next.js पहले से route-wise CSS split करता है।

---

## ➡️ Next Topic
**95. CSS Containment** — `contain` और `content-visibility` से browser को बताएँ कि कौन सा हिस्सा अलग है, ताकि वो कम काम करे।
