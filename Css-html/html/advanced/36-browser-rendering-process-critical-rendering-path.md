# 36. Browser Rendering Process (Critical Rendering Path)
# हिंदी में: Browser Rendering Process — HTML से Pixels तक का सफर

---

## 🔵 Simple Definition (English)
The **Critical Rendering Path (CRP)** is the sequence of steps a browser follows to turn HTML, CSS and JavaScript into pixels on screen: **Parse HTML -> DOM, Parse CSS -> CSSOM, combine -> Render Tree, Layout, Paint, Composite**. Making the first paint fast means shortening and unblocking this path.

## 🔵 सरल परिभाषा (Hindi)
**Critical Rendering Path (CRP)** वो steps की श्रृंखला है जिससे browser HTML, CSS और JavaScript को screen के pixels में बदलता है: **HTML parse -> DOM, CSS parse -> CSSOM, दोनों मिलकर -> Render Tree, Layout, Paint, Composite**। पहला paint तेज़ करना यानी इस path को छोटा और बिना रुकावट का बनाना।

---

## 🔴 Problem it Solves
```
Developers write HTML/CSS/JS and wonder:
  - Why is my page blank for 3 seconds?
  - Why does a script in <head> freeze the page?
  - Why does CSS at the bottom cause a flash of unstyled content?
  - Why is animating `left` janky but animating `transform` smooth?

Without knowing the pipeline you cannot reason about performance.
Knowing it lets you:
  - Unblock rendering (defer scripts, inline critical CSS)
  - Avoid layout thrashing
  - Pick GPU-friendly properties for animation
  - Improve Core Web Vitals (FCP, LCP, CLS, INP)

This is THE most-asked "what happens when you type a URL" / frontend performance interview topic.
```

## 🔴 यह क्यों बना? (Hindi)
```
Developers सोचते हैं:
  - मेरा page 3 second खाली क्यों रहता है?
  - <head> का script page क्यों अटका देता है?
  - नीचे रखी CSS से बिना style का flash क्यों दिखता है?
  - `left` animate करने पर jank, पर `transform` पर smooth क्यों?

Pipeline समझे बिना performance पर सोचा नहीं जा सकता।
इसे जानने से:
  - Rendering unblock कर सकते हैं (defer scripts, critical CSS inline)
  - Layout thrashing से बच सकते हैं
  - Animation के लिए GPU-friendly properties चुन सकते हैं
  - Core Web Vitals (FCP, LCP, CLS, INP) सुधर सकते हैं

"URL डालने पर क्या होता है" और frontend performance interviews का सबसे ज़्यादा पूछा जाने वाला topic।
```

---

## 🟢 How it Works — Step by Step

```
BEFORE RENDERING: NAVIGATION
  1. URL parsed; check cache / Service Worker.
  2. DNS lookup -> IP address.
  3. TCP handshake (+ TLS handshake for HTTPS; HTTP/3 uses QUIC).
  4. HTTP GET request -> server responds with HTML (TTFB = Time To First Byte).

THE RENDERING PIPELINE:

  bytes ─► characters ─► TOKENS ─► NODES ─► DOM            (HTML)
                                            │
  CSS bytes ─► ... ─► CSSOM  ───────────────┤
                                            ▼
                                       RENDER TREE        (only visible nodes + computed styles)
                                            ▼
                                         LAYOUT            (geometry: size + position of every box)
                                            ▼
                                          PAINT            (fill pixels into layers: colours, text, borders, shadows)
                                            ▼
                                        COMPOSITE          (GPU stacks layers in the right order -> screen)

1. PARSE HTML -> DOM
   - Incremental/streaming: parsing starts before the whole file arrives.
   - A "preload scanner" runs ahead and discovers <link>, <script>, <img> early to start downloads.
   - Parser BLOCKS on a normal <script> (it may call document.write or change the DOM) -> use defer/async.

2. PARSE CSS -> CSSOM
   - CSS is RENDER-BLOCKING: the browser will not paint until the CSSOM is built (avoids FOUC).
   - CSS is also SCRIPT-BLOCKING: a script after a stylesheet waits for it (scripts may read styles).
   - Cascade, inheritance, specificity are resolved here.

3. RENDER TREE
   - DOM + CSSOM, only what is displayed.
   - display:none elements, <head>, <script> are EXCLUDED.
   - visibility:hidden and opacity:0 ARE included (they still take space / exist).
   - ::before/::after pseudo-elements are included though not in the DOM.

4. LAYOUT (a.k.a. reflow)
   - Computes exact width/height/position in pixels (% -> px, em -> px, flex/grid algorithms).
   - Needs the viewport size (hence <meta name="viewport"> matters).

5. PAINT
   - Converts boxes into draw instructions, then rasterizes into pixels, per layer.

6. COMPOSITE
   - Layers (created by transform, opacity, will-change, position:fixed, video...) are combined by the GPU.
   - Changing only transform/opacity can SKIP layout and paint -> very cheap, 60fps.

WHAT TRIGGERS WHAT (preview of Topic 37):
   Change width/height/margin/top/font-size -> Layout -> Paint -> Composite   (expensive)
   Change color/background/box-shadow       ->          Paint -> Composite   (medium)
   Change transform/opacity                 ->                   Composite   (cheap)

JAVASCRIPT'S ROLE:
   JS runs on the main thread, can modify DOM/CSSOM, and can trigger layout again.
   Reading layout values (offsetHeight, getBoundingClientRect) right after writing styles forces a
   SYNCHRONOUS layout = "layout thrashing".

KEY METRICS (Core Web Vitals + friends):
   TTFB  time to first byte                    FCP  first content painted
   LCP   largest content painted (good <= 2.5s)
   CLS   layout shift score (good <= 0.1)
   INP   Interaction to Next Paint (good <= 200ms; replaced FID in March 2024)
   DOMContentLoaded: HTML parsed + deferred scripts done.   load: everything incl. images finished.

OPTIMISING THE CRP:
   - Minimise critical bytes (minify, compress with gzip/brotli, ship less JS/CSS)
   - Minimise critical resources (inline critical CSS, defer/async scripts, split CSS by media)
   - Shorten the critical path length (fewer round trips: preload, preconnect, HTTP/2, CDN)
   - Always add width/height to media to avoid layout shift
   - Animate transform/opacity, not layout properties
```

## 🟢 कैसे काम करता है? (Hindi)

```
Rendering से पहले: Navigation
  URL parse -> DNS lookup -> TCP + TLS handshake -> HTTP request -> server से HTML (TTFB)।

Rendering pipeline:
  1. HTML parse -> DOM
     - Streaming होता है: पूरी file आने से पहले ही parsing शुरू।
     - "Preload scanner" आगे देखकर <link>, <script>, <img> पहले ही download शुरू कर देता है।
     - साधारण <script> पर parser रुकता है -> defer/async use करें।

  2. CSS parse -> CSSOM
     - CSS render-blocking है: CSSOM बनने तक paint नहीं होता (FOUC से बचाव)।
     - CSS script-blocking भी है: stylesheet के बाद वाला script उसका इंतज़ार करता है।

  3. Render Tree = DOM + CSSOM, सिर्फ जो दिखना है।
     - display:none, <head>, <script> शामिल नहीं।
     - visibility:hidden और opacity:0 शामिल हैं (जगह घेरते हैं)।

  4. Layout (reflow): हर box का सटीक size और position pixels में निकालना।

  5. Paint: boxes को colours, text, borders, shadows के pixels में बदलना (layers में)।

  6. Composite: GPU सारे layers सही क्रम में जोड़कर screen पर दिखाता है।
     transform/opacity बदलने पर layout और paint छूट जाते हैं -> बहुत सस्ता, 60fps।

क्या बदलने पर क्या चलता है:
   width/margin/top बदला  -> Layout + Paint + Composite (महँगा)
   color/background बदला -> Paint + Composite
   transform/opacity बदला -> सिर्फ Composite (सस्ता)

JS main thread पर चलता है; style लिखकर तुरंत offsetHeight पढ़ने से forced layout होता है
(layout thrashing)।

Optimise कैसे: bytes कम (minify, brotli), blocking resources कम (inline critical CSS, defer),
path छोटा (preload, preconnect, CDN), media पर width/height, और animation में transform/opacity।
```

---

## 🟡 Real World Example
**Amazon product page:** the server streams HTML early, and the preload scanner finds the hero image. Critical CSS for the above-the-fold area is inlined so the first screen paints immediately, while the rest of the CSS and JS load later. **Swiggy / Zomato:** the restaurant list is server-rendered, so the browser can paint real content (FCP) before React finishes hydrating; skeleton cards appear when data loads, with fixed sizes to avoid layout shift. **Instagram's like animation** uses `transform: scale()` and `opacity`, so it runs on the compositor without re-layout, staying smooth even on cheap phones.

## 🟡 Real Example Hindi mein
**Amazon product page:** server HTML जल्दी stream करता है और preload scanner hero image ढूँढ लेता है। ऊपर वाले हिस्से की critical CSS inline होती है ताकि पहली screen तुरंत paint हो जाए, बाकी CSS/JS बाद में आते हैं। **Swiggy / Zomato:** restaurant list server-render होती है, इसलिए React के hydrate होने से पहले ही असली content paint (FCP) हो जाता है; data आते समय fixed size वाले skeleton cards दिखते हैं ताकि layout shift न हो। **Instagram का like animation** `transform: scale()` और `opacity` से बनता है, इसलिए compositor पर चलता है, सस्ते phones पर भी smooth।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Critical Rendering Path Demo</title>

  <!-- CRITICAL CSS inlined: first screen can paint without waiting for a CSS request -->
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; }
    .hero { padding: 48px 20px; background: #fff3e0; }
  </style>

  <!-- Non-critical CSS: load without blocking render (media trick, switch to 'all' on load) -->
  <link rel="stylesheet" href="style.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="style.css"></noscript>

  <!-- Scripts: defer = download in parallel, run after parsing; never block the parser -->
  <script defer src="app.js"></script>
</head>
<body>
  <header class="hero">
    <h1>Critical Rendering Path</h1>
    <p>Open DevTools &gt; Performance and record a reload to see Parse, Layout, Paint, Composite.</p>
  </header>

  <main class="page">
    <div class="demo">
      <!-- Compare an expensive vs a cheap animation -->
      <div class="box slow" id="slow">animates left (Layout + Paint)</div>
      <div class="box fast" id="fast">animates transform (Composite only)</div>
    </div>

    <button id="bad">Layout thrashing (bad)</button>
    <button id="good">Batched reads/writes (good)</button>
    <p id="out"></p>

    <ul id="list"></ul>
  </main>
</body>
</html>
```

```css
/* style.css (non-critical, loaded after first paint) */
.page { padding: 20px; }
.demo { position: relative; height: 150px; background: #eceff1; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }

.box { position: absolute; width: 140px; padding: 10px; color: #fff; font-size: 12px; border-radius: 6px; }

/* SLOW: animating `left` forces layout on every frame */
.slow { top: 10px; left: 0; background: #e53935; animation: moveLeft 2s ease-in-out infinite alternate; }
@keyframes moveLeft { to { left: calc(100% - 140px); } }

/* FAST: animating `transform` is handled by the compositor (GPU) */
.fast { top: 80px; left: 0; background: #43a047; animation: moveX 2s ease-in-out infinite alternate;
        will-change: transform; }          /* hint: promote to its own layer (use sparingly) */
@keyframes moveX { to { transform: translateX(calc(100vw - 180px)); } }

button { padding: 8px 12px; margin-right: 8px; border: 0; border-radius: 6px; background: #1e88e5; color: #fff; cursor: pointer; }
li { padding: 4px 0; }

@media (prefers-reduced-motion: reduce) { .slow, .fast { animation: none; } }
```

```js
// app.js (deferred: DOM exists when this runs)
const list = document.getElementById('list');
const out = document.getElementById('out');

// Build 2000 items ONCE
for (let i = 0; i < 2000; i++) {
  const li = document.createElement('li');
  li.textContent = 'Item ' + i;
  list.append(li);
}
const items = Array.from(list.children);

// BAD: write -> read -> write -> read... each read forces a synchronous layout
document.getElementById('bad').onclick = () => {
  const t = performance.now();
  items.forEach(li => {
    li.style.width = (li.offsetWidth + 1) + 'px';    // read (offsetWidth) right after a write = forced reflow
  });
  out.textContent = 'Thrashing: ' + (performance.now() - t).toFixed(1) + ' ms';
};

// GOOD: do all READS first, then all WRITES = one layout
document.getElementById('good').onclick = () => {
  const t = performance.now();
  const widths = items.map(li => li.offsetWidth);          // batch reads
  items.forEach((li, i) => { li.style.width = (widths[i] + 1) + 'px'; });   // batch writes
  out.textContent = 'Batched: ' + (performance.now() - t).toFixed(1) + ' ms';
};
```

Note: save the three code blocks above as `index.html`, `style.css` and `app.js` in one folder and open `index.html`. Timings vary by machine.

---

## 🟠 React/Next.js Connection

```jsx
// 1. SSR / Server Components send real HTML -> browser can paint (FCP/LCP) BEFORE hydration.
//    Client-only SPA (CRA/Vite): empty <div id="root"> -> blank until the JS bundle downloads,
//    runs and React renders = longer critical path.

// 2. next/font + next/image + next/script map to CRP best practices:
import Image from "next/image";
import Script from "next/script";
export default function Home() {
  return (
    <>
      <Image src="/hero.jpg" alt="" width={1200} height={600} priority />   {/* preload LCP image, no layout shift */}
      <Script src="/analytics.js" strategy="lazyOnload" />                    {/* off the critical path */}
    </>
  );
}

// 3. Avoid layout thrashing inside React: read layout in useLayoutEffect ONCE, not in loops.
import { useLayoutEffect, useRef, useState } from "react";
function Tooltip() {
  const ref = useRef(null);
  const [h, setH] = useState(0);
  useLayoutEffect(() => { setH(ref.current.getBoundingClientRect().height); }, []);  // runs after DOM mutation, before paint
  return <div ref={ref}>height: {h}</div>;
}

// 4. Animate with transform/opacity (Tailwind: transition-transform hover:scale-105)
<button className="transition-transform duration-200 hover:scale-105">Order</button>
```
- Hydration cost: more JS = longer main-thread block = worse INP. Use Server Components, `next/dynamic`, and code splitting to keep the critical path short.
- Streaming SSR with `<Suspense>` flushes HTML in chunks so the browser can render progressively (mirrors the HTML parser's own streaming).
- Skeletons must have fixed dimensions to avoid CLS.

---

## ⚫ Interview Questions + Answers

Q1: Explain the Critical Rendering Path.
A1: After receiving HTML, the browser builds the DOM, builds the CSSOM from CSS, merges them into the render tree (visible nodes with computed styles), performs layout (geometry), paints (pixels per layer), and composites layers via the GPU. Optimising means reducing the blocking resources, bytes and round trips before the first paint.

Q2: Why is CSS render-blocking and JS parser-blocking?
A2: Painting before CSSOM completes would show unstyled content, so the browser waits. A classic script can modify the DOM or `document.write`, so the parser pauses to run it; and a script waits for pending CSS because it might query styles. Fix: `defer`/`async`, inline critical CSS, split CSS by media.

Q3: What is in the render tree and what is not?
A3: Included: visible nodes, `visibility:hidden`, `opacity:0` elements, pseudo-elements. Excluded: `display:none`, `<head>`, `<script>`, `<meta>`. (Elements with display:none cost no layout but still exist in the DOM.)

Q4: Difference between DOMContentLoaded and load?
A4: `DOMContentLoaded` fires when HTML is parsed and deferred/module scripts have run (without waiting for images or iframes). `load` fires when all resources (images, iframes, styles) have finished.

Q5: Why is `transform` smoother than `left` for animation?
A5: `left` changes geometry, triggering layout, paint and composite on the main thread each frame. `transform` and `opacity` on a promoted layer only need compositing, which the GPU handles, even off the main thread, so it stays 60fps even when JS is busy.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Synchronous `<script>` in `<head>` for app code.
✅ Correct way: `defer` (or `type="module"`); `async` only for independent scripts.

❌ Mistake 2: Huge single CSS bundle blocking the first paint.
✅ Correct way: Inline critical CSS, split the rest by route/media, minify and compress.

❌ Mistake 3: Alternating DOM writes and layout reads (`el.style.x = ...; el.offsetHeight`) in loops.
✅ Correct way: Batch reads, then writes; use `requestAnimationFrame`; use `ResizeObserver` instead of polling.

❌ Mistake 4: Images/iframes without dimensions, causing layout shift.
✅ Correct way: Set `width`/`height` or `aspect-ratio`.

❌ Mistake 5: `will-change` on everything.
✅ Correct way: Use sparingly; every layer costs memory.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CRP | Steps from bytes to pixels | Bytes से pixels तक के steps |
| DOM | Tree of HTML elements | HTML elements का tree |
| CSSOM | Tree of CSS rules | CSS rules का tree |
| Render Tree | DOM + CSSOM, visible only | दिखने वाले nodes + styles |
| Layout / Reflow | Compute size and position | Size और position निकालना |
| Paint | Fill pixels | Pixels भरना |
| Composite | Combine layers on GPU | GPU पर layers जोड़ना |
| Preload scanner | Finds resources ahead of parser | Parser से आगे resources ढूँढने वाला |
| FCP / LCP / CLS / INP | Core paint & stability metrics | Page कितनी जल्दी/स्थिर दिखा, के metrics |
| Layout thrashing | Repeated forced reflows | बार-बार जबरन reflow |
| Hydration | Attach JS to server HTML | Server HTML में JS जोड़ना |

---

## ⚡ 3-Line Summary
English: The browser turns HTML into the DOM and CSS into the CSSOM, merges them into a render tree, then runs layout, paint and composite.
CSS blocks rendering and plain scripts block parsing, so use `defer`/`async`, inline critical CSS and keep bytes small.
Animate `transform`/`opacity` and batch DOM reads and writes to avoid expensive reflows.

Hindi: Browser HTML से DOM और CSS से CSSOM बनाता है, दोनों से render tree, फिर layout, paint और composite करता है।
CSS rendering रोकती है और साधारण scripts parsing रोकते हैं, इसलिए `defer`/`async`, inline critical CSS और कम bytes रखें।
`transform`/`opacity` animate करें और DOM reads/writes को batch करें ताकि महँगे reflows न हों।

---

## ➡️ Next Topic
**37. Reflow vs Repaint** — इस pipeline का सबसे महँगा हिस्सा (Layout) कब और क्यों दोबारा चलता है, और उससे कैसे बचें।

---
