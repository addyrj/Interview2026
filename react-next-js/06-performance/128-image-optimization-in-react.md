# 128. Image Optimization in React
# हिंदी में: React में Images को Optimize करना — तेज़ load, कम data

---

## 🔵 Simple Definition (English)
**Image optimization** means delivering the smallest image that still looks sharp on the user's screen: the right size, a modern format (WebP/AVIF), loaded lazily, with reserved space to avoid layout shift. In Next.js, the `<Image>` component does most of this automatically.

## 🔵 सरल परिभाषा (Hindi)
**Image optimization** का मतलब है user की screen के हिसाब से सबसे छोटी image देना जो फिर भी साफ़ दिखे: सही size, modern format (WebP/AVIF), lazy loading, और layout shift रोकने के लिए पहले से जगह reserve करना। Next.js में `<Image>` component यह ज़्यादातर अपने आप कर देता है।

---

## 🔴 Problem it Solves

Images are usually the heaviest part of a page. A 4000x3000 JPEG (3 MB) shown in a 300px card wastes bandwidth, slows Largest Contentful Paint (LCP), burns mobile data, and images that load late push content down (layout shift, bad CLS).

```jsx
// PROBLEM: huge file, no dimensions, loads even when off-screen
<img src="/dish-original-4000px.jpg" />                 // 3 MB for a 300px card

// SOLUTION: right size + lazy + dimensions + modern format
<img src="/dish-300.webp" width="300" height="200" loading="lazy" alt="Paneer tikka" />
```

## 🔴 यह क्यों बना? (Hindi)
Images आमतौर पर page का सबसे भारी हिस्सा होती हैं। 300px के card में 4000x3000 की JPEG (3 MB) दिखाना bandwidth बर्बाद करता है, Largest Contentful Paint (LCP) धीमा करता है, mobile data खाता है, और देर से load होने वाली images content को नीचे धकेलती हैं (layout shift, खराब CLS)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the right dimensions: never ship a 4000px image for a 300px slot
Step 2 → Use modern formats: AVIF/WebP are 25-50% smaller than JPEG at similar quality
Step 3 → Provide several sizes with srcset + sizes, so the browser picks the best one
Step 4 → Set width and height (or aspect-ratio) so the browser reserves space → no layout shift
Step 5 → Lazy-load below-the-fold images with loading="lazy"; keep the hero image eager/priority
Step 6 → Serve through a CDN with long cache headers (Next.js image optimizer does this for you)

KEY: LCP image = load early (priority); everything else = lazy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सही dimensions चुनो: 300px के slot के लिए कभी 4000px की image मत भेजो
Step 2 → Modern formats इस्तेमाल करो: AVIF/WebP, JPEG से 25-50% छोटे होते हैं
Step 3 → srcset + sizes से कई sizes दो, ताकि browser सबसे सही वाली चुने
Step 4 → width और height (या aspect-ratio) दो, ताकि browser जगह reserve करे → layout shift नहीं
Step 5 → Fold के नीचे की images को loading="lazy" से lazy-load करो; hero image को eager/priority रखो
Step 6 → CDN से serve करो और लंबी cache headers लगाओ (Next.js image optimizer यह कर देता है)

KEY: LCP वाली image = जल्दी load करो (priority); बाकी सब = lazy
```

---

## 🟡 Real World Example
**Swiggy home page:** Dozens of restaurant photos appear in carousels. Only the first few are visible. Swiggy-style optimization serves small WebP thumbnails sized for the card (about 300px wide), lazy-loads the carousels below the banner, reserves card height so nothing jumps, and loads the top banner first. On a 4G phone the page becomes usable much faster and uses far less data.

## 🟡 Real Example Hindi mein
**Swiggy home page:** Carousels में दर्जनों restaurant photos होती हैं, पर शुरू में सिर्फ़ पहली कुछ दिखती हैं। Swiggy जैसा optimization card के size (लगभग 300px चौड़ी) के छोटे WebP thumbnails देता है, banner के नीचे वाले carousels lazy-load करता है, card की height reserve रखता है ताकि कुछ उछले नहीं, और ऊपर का banner सबसे पहले load करता है। 4G phone पर page जल्दी usable होता है और data काफ़ी कम लगता है।

---

## 💻 Code Example — Basic

```jsx
// Plain React image best practices (no framework needed)
import { createRoot } from 'react-dom/client';          // React 18/19 root API

function DishCard({ dish }) {
  return (
    <figure style={{ width: 300 }}>                     {/* card width matches the image slot */}
      <img
        src={`${dish.base}-300.webp`}                   // default: small WebP
        srcSet={`${dish.base}-300.webp 300w, ${dish.base}-600.webp 600w, ${dish.base}-900.webp 900w`} // candidates
        sizes="(max-width: 600px) 100vw, 300px"         // tells the browser the slot width
        width={300}                                     // intrinsic width: reserves space
        height={200}                                    // intrinsic height: no layout shift
        loading="lazy"                                  // load only when near the viewport
        decoding="async"                                // decode off the main thread
        alt={dish.name}                                 // accessibility + SEO (never leave empty if meaningful)
        style={{ width: '100%', height: 'auto' }}       // responsive scaling
      />
      <figcaption>{dish.name}</figcaption>              {/* dish name */}
    </figure>
  );
}

function App() {
  const dish = { name: 'Paneer Tikka', base: '/img/paneer' }; // sample data (files are placeholders)
  return <DishCard dish={dish} />;                       // render one card
}

createRoot(document.getElementById('root')).render(<App />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: <picture> with AVIF/WebP fallback + blur placeholder + fade-in, as a reusable component
import { useState, useRef, useEffect } from 'react';    // hooks
import { createRoot } from 'react-dom/client';          // root API

function SmartImage({ src, alt, width, height, priority = false, blur }) {
  const [loaded, setLoaded] = useState(false);          // has the real image finished loading?
  const imgRef = useRef(null);                          // access the <img> DOM node

  useEffect(() => {
    // image may already be cached and complete before React attaches onLoad
    if (imgRef.current?.complete) setLoaded(true);      // avoid being stuck with the blur
  }, []);

  return (
    <div
      style={{
        position: 'relative', width, aspectRatio: `${width} / ${height}`, // reserve space exactly
        background: blur ? `url(${blur}) center/cover` : '#eee',          // tiny blurred placeholder
        overflow: 'hidden',
      }}
    >
      <picture>                                         {/* browser picks the first supported source */}
        <source type="image/avif" srcSet={`${src}.avif`} /> {/* smallest, newest format */}
        <source type="image/webp" srcSet={`${src}.webp`} /> {/* widely supported */}
        <img
          ref={imgRef}                                  // used by the "already complete" check
          src={`${src}.jpg`}                            // universal fallback
          alt={alt}                                     // alt text
          width={width}                                 // explicit dimensions
          height={height}
          loading={priority ? 'eager' : 'lazy'}         // hero = eager, others = lazy
          fetchPriority={priority ? 'high' : 'auto'}    // hint for the LCP image (camelCase in React 18.3+/19)
          decoding="async"                              // do not block the main thread
          onLoad={() => setLoaded(true)}                // reveal when ready
          style={{ width: '100%', height: '100%', objectFit: 'cover',
                   opacity: loaded ? 1 : 0, transition: 'opacity .3s' }} // fade in
        />
      </picture>
    </div>
  );
}

function Home() {
  return (
    <div>
      <SmartImage src="/img/banner" alt="Biryani offer" width={800} height={300} priority /> {/* LCP */}
      <SmartImage src="/img/dish-1" alt="Dosa" width={300} height={200} />                    {/* lazy */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Home />);
```

---

## 🟠 Real App Integration

Next.js ships `next/image`: automatic resizing, WebP/AVIF conversion, lazy loading by default, and layout-shift prevention. Remote images need an allowed host in `next.config`.

```jsx
// app/restaurants/page.jsx (works in Server and Client Components)
import Image from 'next/image';                          // optimized image component
import banner from '@/public/banner.jpg';                // static import: width/height/blur known at build time

export default function Page({ restaurants }) {
  return (
    <main>
      <Image
        src={banner}                                     // static import gives size + blurDataURL
        alt="Biryani offer"
        priority                                         // hero/LCP image: preload (Next 15; Next 16 prefers preload prop - version-dependent)
        placeholder="blur"                               // blurred preview while loading
        sizes="100vw"                                    // full-width banner
      />
      {restaurants.map(r => (
        <Image
          key={r.id}
          src={r.photoUrl}                               // remote URL
          alt={r.name}
          width={300}                                    // required for remote images
          height={200}
          sizes="(max-width: 600px) 100vw, 300px"        // helps Next pick the right srcset width
        />
      ))}
    </main>
  );
}
```

```js
// next.config.js: allow remote image hosts (required for remote src)
module.exports = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'images.example-cdn.com' }], // your CDN host
    formats: ['image/avif', 'image/webp'],               // output formats, in order of preference
  },
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** No width/height, so the page jumps when images load (high CLS)
✅ **Correct:** Always give dimensions or an `aspect-ratio`

```jsx
// Wrong: browser does not know the size until the file downloads
<img src="/dish.jpg" alt="Dish" />                       // ❌ layout shift

// Right: space is reserved up front
<img src="/dish.jpg" alt="Dish" width={300} height={200} /> // ✅ stable layout
```

❌ **Mistake 2:** Lazy-loading the hero (LCP) image
✅ **Correct:** Load the above-the-fold image eagerly, with high priority

```jsx
// Wrong: the biggest visible image waits for lazy-load logic → slower LCP
<img src="/banner.jpg" loading="lazy" alt="Offer" />     // ❌

// Right: eager + high priority for the LCP element
<img src="/banner.jpg" loading="eager" fetchPriority="high" alt="Offer" /> // ✅
```

❌ **Mistake 3:** Using `fill` in `next/image` without a positioned parent, or without `sizes`
✅ **Correct:** Parent needs `position: relative` and a size; provide `sizes`

```jsx
// Wrong: image collapses to zero height, and the browser may download the largest variant
<div><Image src={url} alt="x" fill /></div>              // ❌

// Right
<div style={{ position: 'relative', width: 300, height: 200 }}>
  <Image src={url} alt="x" fill sizes="300px" style={{ objectFit: 'cover' }} /> {/* ✅ */}
</div>
```

---

## 🧠 Tricky Interview Question

```jsx
function Gallery() {
  return (
    <div>
      <img src="/hero.jpg" loading="lazy" alt="Hero" />
      <img src="/a.jpg" alt="A" />
    </div>
  );
}
// Question: Which image hurts LCP, and what is wrong with the second image?
```
**Answer:** The hero image hurts LCP. `loading="lazy"` delays the request until the browser's layout logic decides it is near the viewport, which is pointless for an image already at the top, so the largest paint is later. It should be eager with `fetchpriority="high"`. The second image has no `width`/`height`, so when it finishes loading the page layout jumps (CLS), and it is not lazy, so it competes for bandwidth with the hero if it is below the fold. Add dimensions and `loading="lazy"` to it.

---

## ⚫ Interview Questions + Answers

Q1: Why does image optimization matter for performance?
A1: Images are often over half of a page's bytes. Large or late-loading images slow LCP, waste mobile data and cause layout shift (CLS). Optimizing them improves Core Web Vitals, which affect UX and SEO.

Q2: What does `next/image` do for you?
A2: It resizes images on demand into several widths, converts to WebP/AVIF when the browser supports it, lazy-loads by default, prevents layout shift using width/height, can show blur placeholders, and caches results. Remote hosts must be allowed in `next.config`.

Q3: What are `srcset` and `sizes`?
A3: `srcset` lists image candidates with their widths. `sizes` tells the browser how wide the image will be in the layout. Together the browser chooses the smallest file that is still sharp for the device and pixel density.

Q4: When should you use `priority` (or `fetchpriority="high"`)?
A4: Only for the LCP image, usually the hero banner above the fold. Using it on many images defeats the purpose. Note: newer Next.js versions are moving toward a `preload` prop; check your version.

Q5: How do you prevent layout shift from images?
A5: Provide intrinsic `width` and `height`, or CSS `aspect-ratio`, so the browser reserves the space before the file loads. With `next/image`, give `width`/`height` or use `fill` inside a sized, positioned container.

---

## 🔷 When to Use + When Not to Use
✅ **Use these techniques when:**
- Pages show many photos (catalogues, feeds, galleries)
- LCP or CLS scores are poor, or mobile users are on slow networks
- You use Next.js: `next/image` should be the default for content images

❌ **Avoid / skip when:**
- Images are tiny icons (use inline SVG or sprites instead)
- Images are decorative CSS backgrounds that are already small
- You serve vector art: SVG does not need raster resizing (Next.js treats SVG specially)

---

## 📊 Visual Diagram

```
  Original: 4000x3000 JPEG (3 MB)
        │
        ▼  resize + convert (build time / image optimizer / CDN)
  ┌──────────────────────────────────────┐
  │ 300w.avif  600w.avif  900w.avif      │  ← several sizes
  │ 300w.webp  600w.webp  900w.webp      │
  └──────────────────────────────────────┘
        │  browser reads srcset + sizes + format support
        ▼
  Phone (300px slot) → downloads 300w.avif (~15 KB)
  Laptop (900px slot) → downloads 900w.avif (~70 KB)

  Timeline:  [HTML] → [hero image: eager, high priority] → [others: lazy on scroll]
```

Re-render behavior: images are plain DOM; a parent re-render re-renders `<img>` props but does not refetch if `src` is unchanged. Changing `src` or `key` triggers a new download. Performance impact: right-sizing and modern formats can cut image bytes by 70-90%.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCP | Time for the largest visible element to paint | सबसे बड़े visible element के दिखने का समय |
| CLS | Unexpected layout movement score | Layout के अचानक हिलने का score |
| srcset | List of image candidates by width | Width के हिसाब से image विकल्पों की list |
| sizes | Layout width hint for the browser | Browser को layout width का संकेत |
| Lazy loading | Load only when near the viewport | Viewport के पास आने पर ही load करना |
| WebP / AVIF | Modern compressed image formats | Modern compressed image formats |
| Placeholder (blur) | Low-quality preview shown first | पहले दिखने वाला कम quality का preview |
| Priority | Load the LCP image first | LCP image को पहले load करना |

---

## ⚡ 3-Line Summary
**English:**
1. Send the smallest sharp image: right size, AVIF/WebP, `srcset` + `sizes`, served from a CDN.
2. Reserve space with width/height to avoid layout shift, lazy-load below the fold, prioritize the hero image.
3. In Next.js use `next/image` with `sizes`, `priority` for the LCP image, and `remotePatterns` for remote hosts.

**Hindi:**
1. सबसे छोटी साफ़ image भेजो: सही size, AVIF/WebP, `srcset` + `sizes`, और CDN से।
2. Layout shift रोकने के लिए width/height दो, fold के नीचे lazy-load करो, hero image को priority दो।
3. Next.js में `next/image` इस्तेमाल करो: `sizes`, LCP image पर `priority`, और remote hosts के लिए `remotePatterns`।

---

## ➡️ Next Topic
**129. Bundle Size Optimization** — images के बाद JavaScript सबसे भारी चीज़ है। Bundle analyzer से बड़े packages ढूँढना, हल्के विकल्प चुनना और dependencies घटाना।
