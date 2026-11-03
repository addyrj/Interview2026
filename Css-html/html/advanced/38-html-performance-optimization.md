# 38. HTML Performance Optimization
# हिंदी में: HTML Performance Optimization — Page को तेज़ कैसे बनाएँ

---

## 🔵 Simple Definition (English)
HTML performance optimization means writing markup and loading resources so the page **shows content fast**, responds quickly and does not jump around. Key tools: `defer`/`async` scripts, `preload`/`preconnect`, responsive and lazy images, small DOM, and explicit image sizes. It is measured with **Core Web Vitals** (LCP, INP, CLS).

## 🔵 सरल परिभाषा (Hindi)
HTML Performance Optimization का मतलब है markup और resources इस तरह load करना कि page का content **जल्दी दिखे**, जल्दी respond करे और अपनी जगह से कूदे नहीं। मुख्य tools: `defer`/`async` scripts, `preload`/`preconnect`, responsive और lazy images, छोटा DOM, और image के size explicit देना। इसे **Core Web Vitals** (LCP, INP, CLS) से नापते हैं।

---

## 🔴 Problem it Solves
```
SLOW PAGE PROBLEMS:
  - Blocking <script> in <head> stops HTML parsing -> blank screen
  - Huge hero image (3 MB JPEG) delays Largest Contentful Paint
  - Images without width/height -> layout jumps (CLS) when they load
  - 10,000 DOM nodes -> slow style/layout, high memory
  - Many third-party scripts -> slow interaction (INP)

BUSINESS IMPACT:
  - Amazon found 100ms extra latency can reduce sales (widely cited)
  - Google ranks pages partly on Core Web Vitals
  - Mobile users on 4G leave if page takes > 3 seconds
```

## 🔴 यह क्यों बना? (Hindi)
```
धीमे page की समस्याएँ:
  - <head> में blocking <script> HTML parsing रोक देता है -> blank screen
  - बड़ी hero image (3 MB) LCP को देर करती है
  - width/height के बिना images load होने पर layout कूदता है (CLS)
  - 10,000 DOM nodes -> style/layout धीमा
  - बहुत सारे third-party scripts -> click पर देर (INP)

असर: धीमे page पर users चले जाते हैं, sales घटती है, SEO rank गिरता है।
```

---

## 🟢 How it Works — Step by Step

```
CORE WEB VITALS (targets at 75th percentile):
  LCP  Largest Contentful Paint   <= 2.5 s   (main content visible)
  INP  Interaction to Next Paint  <= 200 ms  (responsiveness)
  CLS  Cumulative Layout Shift    <= 0.1     (visual stability)

CHECKLIST:

1. SCRIPTS
   <script src="a.js" defer>   -> download parallel, run after parsing, keeps order
   <script src="b.js" async>   -> download parallel, run ASAP (analytics)
   Never plain <script> in <head> without defer.

2. CRITICAL RESOURCES
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link rel="preload" as="image" href="hero.webp" fetchpriority="high">
   <link rel="preload" as="font" type="font/woff2" href="f.woff2" crossorigin>

3. IMAGES
   - Modern formats: WebP / AVIF
   - width + height attributes (reserves space -> no CLS)
   - srcset + sizes for the right resolution
   - loading="lazy" for below-the-fold only
   - fetchpriority="high" + NO lazy for the LCP image

4. CSS
   - Inline critical CSS, load rest with media/preload
   - Remove unused CSS

5. DOM
   - Keep under ~1500 nodes, shallow depth
   - Virtualize long lists

6. FONTS
   - font-display: swap, subset, woff2

7. IFRAMES / EMBEDS
   - loading="lazy" on iframes (YouTube) or use a click-to-load facade

8. CACHING / COMPRESSION (server side)
   - Brotli/gzip, long Cache-Control for hashed assets, CDN
```

## 🟢 कैसे काम करता है? (Hindi)

```
Core Web Vitals:
  LCP <= 2.5s  (मुख्य content कब दिखा)
  INP <= 200ms (click पर कितनी जल्दी response)
  CLS <= 0.1   (layout कितना कूदा)

Checklist:
1. Scripts: defer use करो (parse के बाद चलता है, order बना रहता है)।
   async सिर्फ analytics जैसी independent scripts के लिए।
2. preconnect/preload: ज़रूरी font, hero image को पहले मँगवाओ।
3. Images: WebP/AVIF, width+height दो (CLS रुकता है), srcset दो,
   fold के नीचे वाली images पर loading="lazy"।
   LCP वाली image पर lazy कभी नहीं, उस पर fetchpriority="high"।
4. CSS: critical CSS inline, बाकी बाद में।
5. DOM छोटा रखो, लंबी lists virtualize करो।
6. Fonts: font-display: swap, woff2।
7. Server: Brotli, CDN, caching।
```

---

## 🟡 Real World Example
**Amazon product page:** The main product image is the LCP element, so it is preloaded and not lazy loaded, while the "customers also bought" carousel images far below use `loading="lazy"`. Every image has fixed dimensions so the price and Buy button never jump. **Swiggy's** restaurant listing uses small WebP thumbnails through a CDN with `srcset`, so a phone downloads a 150px image instead of a 1200px one.

## 🟡 Real Example Hindi mein
**Amazon product page:** मुख्य product image LCP element है, इसलिए उसे preload करते हैं और lazy नहीं करते; नीचे वाले "customers also bought" carousel की images पर `loading="lazy"` है। हर image का size तय है, इसलिए price और Buy button कूदते नहीं। **Swiggy** की restaurant list CDN से छोटी WebP thumbnails `srcset` के साथ देती है, तो phone 1200px की जगह 150px की image उतारता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Optimized Product Page</title>

  <!-- Warm up connection to third-party origins early -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

  <!-- Preload the LCP hero image with high priority.
       (Replace with a real image path in your project.) -->
  <link rel="preload" as="image" href="hero-800.webp" fetchpriority="high">

  <!-- Critical CSS inline: above-the-fold styles only -->
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; }
    .hero { max-width: 800px; margin: 0 auto; }
    .hero img { width: 100%; height: auto; display: block; background: #eee; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; padding: 12px; }
    .grid img { width: 100%; height: auto; border-radius: 8px; background: #eee; }
  </style>

  <!-- Non-critical CSS: loads without blocking render.
       media="print" trick, then switch to "all" on load. -->
  <link rel="stylesheet" href="below-fold.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="below-fold.css"></noscript>

  <!-- defer: download in parallel, run after HTML is parsed -->
  <script src="app.js" defer></script>
  <!-- async: independent third-party script -->
  <script src="analytics.js" async></script>
</head>
<body>
  <header class="hero">
    <!-- LCP image: explicit size (no CLS), high priority, NOT lazy -->
    <img src="hero-800.webp"
         srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1600.webp 1600w"
         sizes="(max-width: 800px) 100vw, 800px"
         width="800" height="450"
         fetchpriority="high"
         alt="Wireless headphones in black">
  </header>

  <main>
    <h1>Recommended for you</h1>
    <section class="grid">
      <!-- Below the fold: lazy load + decoding async + reserved size -->
      <img src="p1.webp" width="300" height="300" loading="lazy" decoding="async" alt="Product 1">
      <img src="p2.webp" width="300" height="300" loading="lazy" decoding="async" alt="Product 2">
      <img src="p3.webp" width="300" height="300" loading="lazy" decoding="async" alt="Product 3">
    </section>

    <!-- Lazy iframe: video loads only when near viewport -->
    <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"
            width="560" height="315" loading="lazy"
            title="Product demo video"></iframe>
  </main>
</body>
</html>
```

```css
/* Font loading: show fallback text immediately, swap when ready */
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter.woff2") format("woff2");
  font-display: swap;   /* avoids invisible text (FOIT) */
}

/* Skip rendering offscreen sections until needed (Chrome, Edge, Firefox 125+, Safari 18+) */
.below-fold-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 600px;
}
```

---

## 🟠 React/Next.js Connection

```jsx
import Image from 'next/image';
import Script from 'next/script';
import dynamic from 'next/dynamic';

// 1. next/image: automatic WebP/AVIF, srcset, lazy loading, no CLS
export default function Product() {
  return (
    <>
      {/* priority = preload + no lazy -> use for the LCP image */}
      <Image src="/hero.jpg" width={800} height={450} priority alt="Headphones" />

      {/* default is lazy */}
      <Image src="/p1.jpg" width={300} height={300} alt="Product" />

      {/* 2. next/script controls loading strategy (like defer/async) */}
      <Script src="https://example.com/analytics.js" strategy="lazyOnload" />
    </>
  );
}

// 3. Code splitting: heavy component loaded only when needed
const Reviews = dynamic(() => import('./Reviews'), { ssr: false });

// 4. next/font self-hosts fonts and removes layout shift:
// import { Inter } from 'next/font/google';
// const inter = Inter({ subsets: ['latin'], display: 'swap' });

// 5. Tailwind: purges unused CSS automatically in production build.
// 6. Measure: Lighthouse, WebPageTest, Next.js reportWebVitals.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `defer` and `async`?**
A1: Both download the script in parallel with HTML parsing. `async` executes as soon as downloaded (can interrupt parsing, order not guaranteed) so it suits independent scripts like analytics. `defer` executes after parsing finishes, before `DOMContentLoaded`, and keeps script order. Use `defer` for app code.

**Q2: What are Core Web Vitals?**
A2: Google's user-centric metrics: LCP (loading, good <= 2.5s), INP (interactivity, good <= 200ms, replaced FID in 2024) and CLS (visual stability, good <= 0.1). They affect search ranking and user experience.

**Q3: How do you prevent layout shift with images?**
A3: Add `width` and `height` attributes (browser computes aspect ratio before download) or use CSS `aspect-ratio`. Also reserve space for ads/embeds and use `font-display: swap` with size-adjusted fallback fonts.

**Q4: `preload` vs `prefetch` vs `preconnect`?**
A4: `preload` fetches a resource needed for the current page at high priority. `prefetch` fetches a resource likely needed for a future navigation at low priority. `preconnect` only opens the connection (DNS + TCP + TLS) to an origin early.

**Q5: When should you not use `loading="lazy"`?**
A5: Never on the LCP/hero image or anything visible above the fold; lazy loading delays it and hurts LCP. Use it for offscreen images and iframes.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Blocking scripts in head
```html
<!-- WRONG: blocks parsing -->
<script src="big-app.js"></script>
<!-- CORRECT -->
<script src="big-app.js" defer></script>
```

❌ **Mistake 2:** Lazy loading the hero image
```html
<!-- WRONG -->
<img src="hero.jpg" loading="lazy" alt="Hero">
<!-- CORRECT -->
<img src="hero.jpg" fetchpriority="high" width="1200" height="600" alt="Hero">
```

❌ **Mistake 3:** Images without dimensions
```html
<!-- WRONG: content jumps when image loads -->
<img src="a.jpg" alt="A">
<!-- CORRECT -->
<img src="a.jpg" width="400" height="300" alt="A">
```

❌ **Mistake 4:** Preloading everything
```html
<!-- WRONG: too many preloads compete for bandwidth -->
<!-- CORRECT: preload only the 1-2 critical resources -->
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCP | Time to show largest content | सबसे बड़ा content कब दिखा |
| INP | Responsiveness to input | Click/tap का जवाब कितना तेज़ |
| CLS | Unexpected layout movement | Layout का अचानक कूदना |
| defer | Run script after parsing | Parsing के बाद script चलाओ |
| async | Run script when ready | Download होते ही चलाओ |
| preload | High priority fetch for this page | इस page के लिए पहले मँगवाओ |
| preconnect | Open connection early | Connection पहले खोलो |
| Lazy loading | Load when near viewport | ज़रूरत पर load करना |
| CDN | Servers near user | User के पास का server |

---

## ⚡ 3-Line Summary
**English:**
1. Fast pages show content early: use `defer` scripts, preload only critical resources, and inline critical CSS.
2. Always give images width/height, use WebP/AVIF with `srcset`, and lazy load only below-the-fold media.
3. Measure with Core Web Vitals (LCP, INP, CLS) using Lighthouse; in Next.js use `next/image`, `next/script`, `next/font`.

**Hindi:**
1. तेज़ page के लिए `defer` scripts, सिर्फ ज़रूरी resources का preload, और critical CSS inline।
2. Images को width/height दो, WebP/AVIF + `srcset` use करो, lazy loading सिर्फ fold के नीचे।
3. Lighthouse से LCP, INP, CLS नापो; Next.js में `next/image`, `next/script`, `next/font` use करो।

---

## ➡️ Next Topic
**39. Progressive Enhancement vs Graceful Degradation** — अब सीखें कि page हर browser और slow network पर भी काम करे, यह design approach कैसे चुनें।
