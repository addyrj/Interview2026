# 35. Lazy Loading (loading="lazy")
# हिंदी में: Lazy Loading — ज़रूरत पड़ने पर ही Load करो

---

## 🔵 Simple Definition (English)
Lazy loading delays loading of off-screen resources until the user **scrolls near them**. In HTML you enable it with `loading="lazy"` on `<img>` and `<iframe>`. For more control (videos, components, infinite scroll) you use the **IntersectionObserver** API.

## 🔵 सरल परिभाषा (Hindi)
Lazy loading उन resources का loading टालता है जो अभी screen के बाहर हैं, जब तक user **scroll करके उनके पास न पहुँचे**। HTML में `<img>` और `<iframe>` पर `loading="lazy"` लगाकर ये चालू होता है। ज़्यादा control (videos, components, infinite scroll) के लिए **IntersectionObserver** API use होती है।

---

## 🔴 Problem it Solves
```
A product listing page has 100 images, but the user sees only the first 6.
  Without lazy loading: browser downloads ALL 100 immediately
    -> bandwidth fights with critical resources (CSS, JS, hero image)
    -> slow LCP, high data usage on mobile, wasted bytes if the user never scrolls.

With lazy loading: only images near the viewport load; the rest load while scrolling.
  -> faster initial load, less data, better Core Web Vitals.
```

## 🔴 यह क्यों बना? (Hindi)
```
Product listing page पर 100 images हैं, पर user को शुरू में सिर्फ 6 दिखती हैं।
  Lazy loading के बिना: browser सभी 100 एक साथ download करता है
    -> ज़रूरी resources (CSS, JS, hero image) से bandwidth की लड़ाई
    -> LCP slow, mobile पर data खर्च, user scroll न करे तो बर्बादी।

Lazy loading के साथ: सिर्फ viewport के पास वाली images load होती हैं, बाकी scroll करते समय।
  -> शुरुआती load तेज़, data कम, Core Web Vitals बेहतर।
```

---

## 🟢 How it Works — Step by Step

```
NATIVE (zero JS):
  <img src="a.jpg" alt="..." width="400" height="300" loading="lazy">
  <iframe src="https://www.youtube.com/embed/ID" title="Video" loading="lazy"></iframe>

  loading values:
    "eager" (default)  load immediately
    "lazy"             load when the element is near the viewport
    (the browser decides the distance threshold, typically a few screens; it varies and is
     larger on slow connections. You cannot configure it.)

HOW THE BROWSER DECIDES:
  1. Parser meets <img loading="lazy">.
  2. It does NOT start the download, but it must still reserve space -> so you need
     width/height (or aspect-ratio), otherwise the layout jumps when the image arrives (CLS).
  3. As the user scrolls and the image comes within the threshold, the fetch starts.
  Note: native lazy loading needs no JS code from you. The IntersectionObserver
        approach does need JS (so use it only where native cannot do the job).

DO NOT LAZY LOAD:
  - The hero / LCP image and anything in the first viewport (it delays LCP).
  - Tiny images (icons) where the overhead is not worth it.

IntersectionObserver (JS) - for custom behaviour:
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { load(e.target); io.unobserve(e.target); } });
  }, { rootMargin: '200px' });          // start 200px BEFORE it enters the viewport
  io.observe(element);
  Use for: background images, videos, loading React components, infinite scroll, analytics
  "viewed" events.

OTHER LAZY TECHNIQUES:
  - Code splitting: dynamic import() / React.lazy / next/dynamic  (lazy JS)
  - <video preload="none" poster="...">
  - Click-to-load facade for heavy embeds (a thumbnail that swaps in the YouTube iframe on click)
  - content-visibility: auto  (CSS: skip rendering off-screen sections)
  - decoding="async" (different: decoding, not fetching)

BROWSER SUPPORT: loading="lazy" on img and iframe is supported by all current major browsers.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Native तरीका (JS नहीं): <img src="a.jpg" width="400" height="300" loading="lazy" alt="...">

loading values: "eager" (default, तुरंत load) | "lazy" (viewport के पास आने पर load)।
कितनी दूरी पर load शुरू हो ये browser तय करता है, आप बदल नहीं सकते।

Browser कैसे तय करता है:
  1. Parser को <img loading="lazy"> मिलता है।
  2. Download शुरू नहीं करता, पर जगह रोकनी ज़रूरी है -> इसलिए width/height (या aspect-ratio) दें,
     वरना image आते ही layout कूदता है (CLS)।
  3. Scroll करते हुए image threshold के अंदर आए तो fetch शुरू।

Lazy न करें: hero / LCP image और पहली screen की चीज़ें (LCP देर से होगा)।

IntersectionObserver (JS): custom काम के लिए, जैसे background images, videos, components,
infinite scroll। rootMargin: '200px' से element दिखने से 200px पहले ही load शुरू कर सकते हैं।

और तरीके: code splitting (React.lazy, next/dynamic), video पर preload="none",
YouTube के लिए click-to-load facade, CSS content-visibility: auto।
```

---

## 🟡 Real World Example
**Amazon / Flipkart search results:** only the first few product images load; as you scroll, the rest appear. **Instagram feed:** posts below the fold load on scroll (infinite scroll built with IntersectionObserver). **Zomato / Swiggy restaurant lists:** card images lazy load, but the top banner is eager. **Blog pages with YouTube embeds:** each iframe is lazy or replaced with a thumbnail facade, because a single YouTube iframe pulls in ~500 KB+ of JS.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart search results:** सिर्फ पहले कुछ product images load होती हैं; scroll करने पर बाकी आती हैं। **Instagram feed:** नीचे की posts scroll पर load होती हैं (IntersectionObserver से बना infinite scroll)। **Zomato / Swiggy restaurant lists:** card images lazy हैं, पर ऊपर का banner eager। **YouTube embeds वाले blogs:** हर iframe lazy या thumbnail facade से बदला जाता है, क्योंकि एक YouTube iframe ~500 KB+ का JS खींचता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lazy Loading Demo</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="top">
    <h1>Lazy loading demo</h1>
    <p>Open DevTools &gt; Network &gt; Img and scroll. Watch requests appear gradually.</p>
  </header>

  <!-- 1. Hero: ABOVE the fold -> eager + high priority. NEVER lazy here. -->
  <img class="hero" src="https://picsum.photos/id/1011/1200/400"
       width="1200" height="400" alt="Canoe on a lake"
       fetchpriority="high">

  <!-- 2. Native lazy images below the fold (width/height reserve space = no layout shift) -->
  <section class="grid" id="grid">
    <!-- Each image below is lazy; filler spacing forces scrolling -->
    <img src="https://picsum.photos/id/1015/400/300" width="400" height="300" alt="River valley" loading="lazy">
    <img src="https://picsum.photos/id/1016/400/300" width="400" height="300" alt="Canyon" loading="lazy">
    <img src="https://picsum.photos/id/1018/400/300" width="400" height="300" alt="Mountain lake" loading="lazy">
    <img src="https://picsum.photos/id/1019/400/300" width="400" height="300" alt="Coastline" loading="lazy">
    <img src="https://picsum.photos/id/1020/400/300" width="400" height="300" alt="Bear" loading="lazy">
    <img src="https://picsum.photos/id/1021/400/300" width="400" height="300" alt="Forest" loading="lazy">
  </section>

  <!-- 3. Lazy iframe -->
  <iframe class="video" src="https://www.youtube.com/embed/dQw4w9WgXcQ"
          title="Sample video" loading="lazy" allowfullscreen></iframe>

  <!-- 4. Custom lazy loading with IntersectionObserver (data-src pattern).
       Useful for background images or when you want a fade-in effect. -->
  <section class="grid" id="custom">
    <img class="fade" data-src="https://picsum.photos/id/1035/400/300" width="400" height="300" alt="Waterfall">
    <img class="fade" data-src="https://picsum.photos/id/1036/400/300" width="400" height="300" alt="Snow mountains">
  </section>

  <p id="status" class="status" role="status">Custom images loaded: 0</p>

  <script>
    let loaded = 0;
    const status = document.getElementById('status');

    // create the observer: callback fires when targets enter / leave the viewport
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;          // only act when visible
        const img = entry.target;
        img.src = img.dataset.src;                  // swap data-src into real src -> starts the download
        img.onload = () => img.classList.add('loaded');   // fade in after load
        observer.unobserve(img);                    // done with this image
        status.textContent = 'Custom images loaded: ' + (++loaded);
      });
    }, { rootMargin: '200px 0px' });                // begin 200px before it is visible

    document.querySelectorAll('img[data-src]').forEach(img => io.observe(img));
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222; }
.top { padding: 16px; }

img { display: block; max-width: 100%; height: auto; }   /* width/height attrs + height:auto keeps the ratio */
.hero { width: 100%; }

/* Responsive grid; margin-top pushes images below the fold so lazy loading is visible */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  padding: 16px;
  margin-top: 80vh;
}
.grid img { width: 100%; border-radius: 10px; background: #ddd; }

.video { display: block; width: calc(100% - 32px); max-width: 640px; aspect-ratio: 16 / 9;
         margin: 80vh auto 0; border: 0; }

/* Fade-in for custom lazy images */
.fade { opacity: 0; transition: opacity .4s ease; }
.fade.loaded { opacity: 1; }

.status { position: fixed; right: 12px; bottom: 12px; background: #212121; color: #fff;
          padding: 6px 12px; border-radius: 8px; font-size: 13px; }

/* Bonus: skip rendering work for off-screen sections (Chrome/Edge/Firefox/Safari 18+) */
.section-heavy { content-visibility: auto; contain-intrinsic-size: 0 600px; }

@media (prefers-reduced-motion: reduce) { .fade { transition: none; } }
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Images: next/image is lazy by default (except when `priority` is set)
import Image from "next/image";
<Image src="/dish.jpg" alt="Dish" width={400} height={300} />            {/* lazy by default */}
<Image src="/hero.jpg" alt="Hero" width={1200} height={400} priority />   {/* eager + preload */}

// 2. Plain <img> in JSX works too
<img src={url} alt={title} width={400} height={300} loading="lazy" />

// 3. Lazy components (code splitting)
import { lazy, Suspense } from "react";
const Reviews = lazy(() => import("./Reviews"));          // JS for Reviews loads only when rendered

function Product() {
  return (
    <Suspense fallback={<p>Loading reviews...</p>}>
      <Reviews />
    </Suspense>
  );
}

// Next.js equivalent (also lets you disable SSR for browser-only code)
import dynamic from "next/dynamic";
const Map = dynamic(() => import("./Map"), { ssr: false, loading: () => <p>Loading map...</p> });

// 4. Infinite scroll with IntersectionObserver in a hook
import { useEffect, useRef } from "react";
function useOnVisible(callback) {
  const ref = useRef(null);
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => e.isIntersecting && callback(), { rootMargin: "300px" });
    if (ref.current) io.observe(ref.current);
    return () => io.disconnect();                          // CLEANUP
  }, [callback]);
  return ref;
}
// <div ref={useOnVisible(loadNextPage)} />  <- sentinel at the bottom of the list
```
- Libraries: `react-intersection-observer` (`useInView`), `react-lazy-load-image-component`.
- Tailwind: `aspect-video`, `bg-gray-200` as placeholder while loading.

---

## ⚫ Interview Questions + Answers

Q1: How do you lazy load images natively?
A1: Add `loading="lazy"` to `<img>` (and `<iframe>`), together with `width` and `height` so the space is reserved. The browser starts the download only when the element nears the viewport.

Q2: Which images should you NOT lazy load?
A2: Above-the-fold images, especially the LCP/hero image, because lazy loading delays them and hurts LCP. Use `fetchpriority="high"` or `priority` in `next/image` instead.

Q3: How does IntersectionObserver work and why use it over scroll events?
A3: It asynchronously reports when a target crosses the viewport (or a root) by a threshold or `rootMargin`. It is asynchronous and efficient, and avoids the layout thrashing and jank of `scroll` handlers calling `getBoundingClientRect`.

Q4: Lazy loading vs code splitting vs preloading?
A4: Lazy loading defers non-critical resources until needed; code splitting is lazy loading for JS bundles (`import()`, `React.lazy`); preloading does the opposite: fetches critical things earlier. The skill is deciding which resources are critical.

Q5: What are the downsides of lazy loading?
A5: Late-loading content may flash/jump (CLS) if size is not reserved, fast scrolling shows blanks, content may not be crawled if loaded only via JS-dependent patterns, and lazy-loading above-the-fold content worsens LCP.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: `loading="lazy"` on every image including the hero.
✅ Correct way: Eager hero with `fetchpriority="high"`; lazy for the rest.

❌ Mistake 2: Lazy images without `width`/`height`, causing layout shift.
✅ Correct way: Provide dimensions or `aspect-ratio`.

❌ Mistake 3: Using `data-src` + JS for all images when native `loading="lazy"` suffices (and SEO crawlers may miss them).
✅ Correct way: Prefer native; use IntersectionObserver only for special needs.

❌ Mistake 4: Forgetting `observer.unobserve/disconnect`, leaking observers (especially in React effects).
✅ Correct way: Unobserve after loading and `disconnect()` in the effect cleanup.

❌ Mistake 5: Using a scroll event listener to check positions.
✅ Correct way: IntersectionObserver.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lazy loading | Load only when needed | ज़रूरत पड़ने पर load |
| Eager | Load immediately | तुरंत load |
| IntersectionObserver | API to detect visibility | Element के दिखने का पता लगाने वाली API |
| rootMargin | Offset to trigger early | पहले ही trigger करने का margin |
| LCP | Largest Contentful Paint | सबसे बड़े content का समय |
| CLS | Layout shift score | Layout खिसकने का score |
| Code splitting | Break JS into chunks | JS को टुकड़ों में बाँटना |
| Facade | Lightweight placeholder for heavy embed | भारी embed की जगह हल्का placeholder |

---

## ⚡ 3-Line Summary
English: `loading="lazy"` defers off-screen images and iframes until the user scrolls near them.
Always set `width`/`height`, and never lazy-load the hero/LCP image; use IntersectionObserver for custom cases.
In React/Next.js, `next/image` is lazy by default, and `React.lazy` / `next/dynamic` lazy-load JavaScript.

Hindi: `loading="lazy"` screen के बाहर की images और iframes को तब तक रोकता है जब तक user scroll करके पास न आए।
हमेशा `width`/`height` दें, hero/LCP image को कभी lazy न करें; खास ज़रूरत में IntersectionObserver।
React/Next.js में `next/image` by default lazy है, और `React.lazy` / `next/dynamic` JavaScript को lazy load करते हैं।

---

## ➡️ Next Topic
**36. Browser Rendering Process (Critical Rendering Path)** — अब पूरी तस्वीर: HTML, CSS, JS मिलकर pixels कैसे बनते हैं, और ये सब optimisations उसमें कहाँ फिट होती हैं।

---
