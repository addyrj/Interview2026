# F02. How the Browser Renders a Page (Critical Rendering Path)
# हिंदी में: Critical Rendering Path — ब्राउज़र HTML, CSS और JavaScript को लेकर स्क्रीन पर pixels कैसे बनाता है (DOM → CSSOM → Render Tree → Layout → Paint → Composite), और उसे तेज़ कैसे करें

---

## 🔵 Simple Definition (English)
The **Critical Rendering Path (CRP)** is the sequence of steps the browser performs to turn HTML, CSS and JavaScript into pixels on screen:
1. **Parse HTML → DOM** (Document Object Model)
2. **Parse CSS → CSSOM**
3. **Execute JavaScript** (can block parsing and modify DOM/CSSOM)
4. **Render tree** = visible DOM nodes + computed styles
5. **Layout (reflow)**: compute size and position of every element
6. **Paint**: fill pixels (text, colors, images, borders) into layers
7. **Composite**: combine layers (GPU) and display
Optimizing the CRP means showing useful content **sooner** and keeping interactions **smooth (60 fps)**.

## 🔵 सरल परिभाषा (Hindi)
Critical Rendering Path वो कदम हैं जिनसे ब्राउज़र HTML, CSS, JS को स्क्रीन के pixels में बदलता है: HTML → DOM, CSS → CSSOM, JS चलाना, Render Tree, Layout (कौन कहाँ और कितना बड़ा), Paint (रंग भरना), Composite (परतें जोड़कर दिखाना)।
इसे तेज़ करने का मतलब — ज़रूरी content जल्दी दिखे और scrolling/clicks smooth (60 fps) रहें।

---

## 🔴 Problem it Solves
Understanding the CRP explains common performance problems:
- **Blank white screen for seconds**: render-blocking CSS and synchronous JS in `<head>`.
- **Content jumping around (CLS)**: images without dimensions, late-loading fonts, injected banners.
- **Janky scrolling and animations**: layout thrashing, animating `top/left/width` instead of `transform`, long JS tasks blocking the main thread.
- **Slow interactions (INP)**: heavy JavaScript on the main thread.
It's the foundation for Core Web Vitals (F05), bundling (F06) and image optimization (F17).

## 🔴 यह क्यों बना? (Hindi)
CRP समझने से आम समस्याएँ समझ आती हैं: सफ़ेद स्क्रीन (रोकने वाली CSS/JS), content का उछलना (बिना size की images, देर से आने वाले fonts), झटकेदार scrolling (layout बार-बार गिनना, width/top animate करना), और धीमे clicks (भारी JavaScript)।
Core Web Vitals, bundling, image optimization — सबकी नींव यही है।

---

## 🟢 How it Works — Step by Step

### The pipeline

```
 Network bytes
     │
     ▼
 HTML ──parse──► DOM tree ──────────────────┐
     │  (finds <link css>, <script>, <img>)  │
     ▼                                       ▼
 CSS ──parse──► CSSOM ─────────────────► RENDER TREE (visible nodes + computed styles)
                    ▲                        │
 JS ──execute───────┘ (can read/modify DOM   ▼
                       & CSSOM)          LAYOUT (geometry: x, y, width, height)
                                             │
                                             ▼
                                         PAINT (draw text, colors, images → layers/bitmaps)
                                             │
                                             ▼
                                         COMPOSITE (GPU combines layers) ──► pixels on screen
```

### What blocks what

```
CSS is RENDER-BLOCKING: browser won't paint until CSSOM is ready (to avoid flash of unstyled content)
<script> (classic, no async/defer) is PARSER-BLOCKING: HTML parsing stops, script downloads + runs
   (and it also waits for preceding CSS, because JS may read styles)
<script defer>  → download in parallel, run after HTML parsed, in order       ⭐ for app scripts
<script async>  → download in parallel, run as soon as ready, any order       ✓ for analytics
<script type="module"> → deferred by default
Images don't block rendering (but affect LCP & CLS)
Fonts: text may be invisible until web font loads (FOIT) → use font-display: swap/optional
```

### Updating the page later: the cost of changes

```
Change type                          Pipeline steps triggered            Cost
───────────────────────────────────  ──────────────────────────────────  ────────
width, height, top, margin, font,     Layout → Paint → Composite          💸💸💸
  adding/removing elements
color, background, box-shadow         Paint → Composite                   💸💸
transform, opacity (on own layer)     Composite only                      💸   ⭐ animate these
```

### Layout thrashing (forced synchronous layout)

```js
// ❌ read-write-read-write in a loop → forces layout every iteration
for (const el of items) {
  const h = el.offsetHeight;          // READ (forces layout)
  el.style.height = h + 10 + 'px';    // WRITE (invalidates layout)
}
// ✅ batch reads, then writes (or use requestAnimationFrame)
const heights = items.map((el) => el.offsetHeight);
items.forEach((el, i) => (el.style.height = heights[i] + 10 + 'px'));
```

### The main thread & frames

```
60 fps → 16.7 ms per frame for: JS + style + layout + paint + composite
Long tasks (> 50 ms) block input handling → janky scroll, slow clicks (bad INP)
Fixes: split work (yield with scheduler.yield / setTimeout), Web Workers for heavy compute,
       virtualization for long lists, avoid huge DOMs (> ~1,500 nodes is a warning sign)
```

### Optimizing the critical rendering path

```
1. Minimize critical resources: inline critical CSS (above-the-fold), load the rest async
2. Reduce bytes: minify, compress (brotli), tree-shake, code split (F06)
3. Shorten the critical path: preconnect to origins, preload key assets (hero image, main font)
4. defer/async scripts; avoid long synchronous JS during load
5. Server-render HTML for first paint (SSR/SSG — F03) → content visible before JS hydrates
6. Images: width/height attributes (no CLS), responsive srcset, lazy-load below the fold, fetchpriority="high" for LCP image
7. Fonts: preload, font-display: swap, subset (e.g. Latin + Devanagari only as needed)
8. Animate transform/opacity; use will-change sparingly; content-visibility: auto for offscreen sections
```

### Key events & metrics
```
DOMContentLoaded → HTML parsed (deferred scripts run before it)
load             → all resources (images, iframes) loaded
FCP (first contentful paint), LCP (largest contentful paint), CLS, INP, TBT (total blocking time) — F05
```

## 🟢 कैसे काम करता है? (Hindi)
1. HTML से DOM, CSS से CSSOM बनता है; दोनों मिलकर render tree; फिर layout (आकार-जगह), paint (रंग), composite (परतें जोड़ना)।
2. CSS paint रोकती है; बिना async/defer वाली `<script>` HTML पढ़ना रोकती है — इसलिए app scripts में `defer`।
3. Width/top बदलना महँगा (layout दोबारा); color बदलना मध्यम (paint); transform/opacity सस्ता (सिर्फ़ composite) — animation इन्हीं से।
4. Loop में बार-बार पढ़ना-लिखना (offsetHeight फिर style) = layout thrashing; पहले सब पढ़ो, फिर सब लिखो।
5. 60 fps के लिए हर frame 16 ms; 50 ms से लंबे JS काम clicks धीमे करते हैं — काम को टुकड़ों में बाँटो, Web Worker, virtualization; critical CSS inline, images को size दो, fonts swap।

---

## 🟡 Real World Example

**Google Search** — inlines critical CSS, keeps JavaScript minimal for first render, and preconnects and prefetches aggressively. The results page renders meaningful content in a few hundred milliseconds even on slow devices.

**Flipkart Lite (PWA, 2015)** — rebuilt mobile web with server-rendered app shells, critical-path optimizations and service workers, which led to big engagement improvements on slow Indian networks. It's a famous PWA case study.

**Twitter Lite** — reduced JS payloads and render-blocking work, used code splitting and smaller critical paths, and improved load times on 2G/3G in emerging markets.

**Pinterest PWA** — cut time-to-interactive drastically by reducing the JS bundle and optimizing the critical path, and reported large increases in engagement.

## 🟡 Real Example Hindi में
Flipkart Lite (2015) ने mobile web को server-rendered app shell, critical path सुधार और service worker से दोबारा बनाया — धीमे भारतीय नेटवर्क पर engagement बहुत बढ़ा।
Twitter Lite और Pinterest PWA ने JavaScript कम करके और rendering रास्ता छोटा करके 2G/3G पर load time बहुत घटाया।

---

## 🟠 My Stack Example

### HTML head done right (plain / Next.js does much of this automatically)
```html
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preconnect" href="https://cdn.myapp.com" crossorigin />
  <link rel="preload" as="image" href="https://cdn.myapp.com/hero-1080.webp" fetchpriority="high" />
  <link rel="preload" as="font" href="/fonts/inter-latin.woff2" type="font/woff2" crossorigin />
  <style>/* critical above-the-fold CSS inlined */ .header{height:56px} .hero{aspect-ratio:16/9}</style>
  <link rel="stylesheet" href="/app.css" media="print" onload="this.media='all'" />  <!-- non-critical CSS async -->
  <script src="/app.js" defer></script>
  <script src="https://analytics.example.com/a.js" async></script>
</head>
```

### Next.js equivalents
```tsx
import Image from 'next/image';
import { Inter, Noto_Sans_Devanagari } from 'next/font/google';     // self-hosted, font-display swap, no CLS
const inter = Inter({ subsets: ['latin'], display: 'swap' });
const hindi = Noto_Sans_Devanagari({ subsets: ['devanagari'], weight: ['400', '600'], display: 'swap' });

export default function Hero() {
  return <Image src="/hero.jpg" alt="Diwali sale" width={1080} height={608} priority sizes="100vw" />;  // LCP image
}
// <Script src="..." strategy="afterInteractive" /> or "lazyOnload" for third-party scripts
```

### Avoid layout shift & jank in components
```css
.card-img { aspect-ratio: 4 / 3; width: 100%; object-fit: cover; }        /* reserve space → no CLS */
.toast-enter { transform: translateY(16px); opacity: 0; transition: transform .2s, opacity .2s; }
.toast-enter-active { transform: none; opacity: 1; }                        /* compositor-only animation */
.below-fold { content-visibility: auto; contain-intrinsic-size: 800px; }    /* skip rendering offscreen */
```

### Break up long tasks (keep INP good)
```ts
async function processLargeList(items: Item[]) {
  for (let i = 0; i < items.length; i++) {
    heavyTransform(items[i]);
    if (i % 200 === 0) await new Promise((r) => setTimeout(r));   // yield to the main thread
  }
}
// or move to a Web Worker: const worker = new Worker(new URL('./worker.ts', import.meta.url))
```

### React Native note (different pipeline, same ideas)
```
RN: JS thread (React logic) → (Fabric) shadow tree → layout via Yoga (flexbox) → native UI thread renders
Keep JS thread free (no heavy work during scroll), use FlatList/FlashList virtualization,
animations on the UI thread (Reanimated), avoid layout-changing animations (Topic M14)
```

### Measure
```
Chrome DevTools → Performance panel (main thread flame chart: long tasks, layout, paint),
Lighthouse, "Rendering" tab → Paint flashing / Layout shift regions, WebPageTest film strip
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the critical rendering path.**
A1: The browser parses HTML into the DOM and CSS into the CSSOM, and executes JavaScript, which may block parsing and modify both. It combines the visible DOM and computed styles into the render tree, runs layout to compute geometry, paints pixels into layers, and composites the layers on the GPU to display the frame. CSS is render-blocking and classic scripts are parser-blocking, so optimizing means minimizing, deferring or inlining critical resources so meaningful content paints quickly.

**Q2: What's the difference between async and defer on script tags?**
A2: Both download in parallel without blocking HTML parsing. `defer` executes after parsing completes, in document order, before DOMContentLoaded, so it's ideal for app scripts that need the DOM and ordering. `async` executes as soon as the script downloads, possibly mid-parse and in any order, so it suits independent third-party scripts like analytics. Module scripts are deferred by default. Plain scripts block parsing.

**Q3: What is a reflow (layout) vs repaint, and how do you minimize them?**
A3: Reflow recalculates element geometry when layout-affecting properties change (size, position, fonts, DOM structure). It's expensive and can cascade to descendants and siblings. Repaint redraws pixels when visual properties change without affecting layout (color, background). Minimize both by batching DOM reads and writes (avoid layout thrashing), animating `transform` and `opacity` (compositor-only), avoiding inline style changes in loops, reducing DOM size, using `content-visibility`, and reserving space for dynamic content.

**Q4: How do you improve time to first paint for a content site?**
A4: Server-render or statically generate HTML so content arrives in the first response. Inline critical CSS and load the rest asynchronously. Defer non-critical JavaScript and reduce bundle size. Preconnect to required origins and preload the LCP image and key fonts. Use a CDN with HTTP/2 or HTTP/3 and compression. Optimize images (correct dimensions, modern formats, priority hint for the hero) and use `font-display: swap` with subsetted fonts.

**Q5: Why does a long JavaScript task hurt user experience?**
A5: The browser's main thread handles JavaScript, style, layout, paint and input events. A task longer than about 50 ms blocks the thread, so taps, clicks and scrolls wait, which makes the page feel unresponsive (poor INP) and drops frames below 60 fps (jank). Split long work into smaller chunks that yield to the event loop, move heavy computation to Web Workers, defer non-urgent work (requestIdleCallback), reduce hydration cost (server components, partial hydration), and virtualize big lists.

---

## 🔷 Trade-offs
✅ Inlining critical CSS: faster first paint — ❌ larger HTML, not cached separately.
✅ Deferring JS: faster paint — ❌ interactivity later (hydration gap) → keep JS small.
✅ will-change/layers: smoother animations — ❌ memory cost if overused.
✅ SSR: fast content — ❌ server cost, hydration complexity (F03/F04).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DOM | Tree of HTML elements | HTML का पेड़ |
| CSSOM | Tree of CSS rules | CSS का पेड़ |
| Render tree | Visible nodes + styles | दिखने वाले nodes + styles |
| Layout / reflow | Computing geometry | आकार और जगह गिनना |
| Paint / repaint | Drawing pixels | pixels बनाना |
| Composite | Combining layers on GPU | परतें जोड़ना |
| Render-blocking | Delays first paint | पहला दृश्य रोकने वाला |
| Parser-blocking | Stops HTML parsing | HTML पढ़ना रोकने वाला |
| Layout thrashing | Repeated forced layouts | बार-बार layout गिनना |
| Long task | > 50 ms main-thread work | लंबा JS काम |

---

## ⚡ 3-Line Summary
**English:**
1. CRP: HTML→DOM, CSS→CSSOM, JS, render tree, layout, paint, composite; CSS blocks render, classic scripts block parsing.
2. Speed first paint: SSR, critical CSS inline, defer JS, preconnect/preload, optimized images & fonts.
3. Keep frames smooth: animate transform/opacity, avoid layout thrashing, break long tasks, small DOM/virtualization.

**Hindi:**
1. CRP: DOM, CSSOM, JS, render tree, layout, paint, composite; CSS paint रोकती है, सादी script parsing।
2. पहला दृश्य जल्दी: SSR, critical CSS inline, JS defer, preload, सही images और fonts।
3. Smooth रखो: transform/opacity animate करो, layout thrashing नहीं, लंबे काम तोड़ो, छोटा DOM।

---

## ➡️ Next Topic Suggestion
**F03. Rendering Patterns — CSR vs SSR vs SSG vs ISR** — Where the HTML is generated (browser, server at request time, build time, or on revalidation) shapes performance, SEO and cost. Next: the rendering patterns with Next.js examples.
