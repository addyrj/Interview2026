# 34. Picture Tag + Responsive Images
# हिंदी में: Picture Tag — हर Device के लिए सही Image

---

## 🔵 Simple Definition (English)
Responsive images let the browser choose the **best image file** for the user's screen size, pixel density and format support. `srcset` + `sizes` on `<img>` offer several widths (resolution switching); `<picture>` with `<source>` swaps formats (AVIF/WebP) or entirely different crops (art direction).

## 🔵 सरल परिभाषा (Hindi)
Responsive images में browser user की screen size, pixel density और format support के हिसाब से **सबसे सही image file** चुनता है। `<img>` पर `srcset` + `sizes` कई widths देते हैं (resolution switching); `<picture>` और `<source>` format बदलते हैं (AVIF/WebP) या बिल्कुल अलग crop दिखाते हैं (art direction)।

---

## 🔴 Problem it Solves
```
ONE 2400px JPEG FOR EVERYONE:
  - Phone (360px wide screen) downloads 1.2 MB of pixels it can never show -> slow, data cost.
  - Retina screen gets a 1x image -> blurry.
  - Old JPEG while the browser supports AVIF (50% smaller) -> wasted bytes.
  - A wide banner cropped on mobile makes the subject tiny.

Slow images = bad LCP (Core Web Vital) = lower Google ranking + users leave.

SOLUTION: describe the options, let the browser decide.
```

## 🔴 यह क्यों बना? (Hindi)
```
सबके लिए एक 2400px की JPEG:
  - Phone (360px) 1.2 MB के pixels download करता है जो कभी दिखेंगे नहीं -> slow, data खर्च।
  - Retina screen को 1x image मिले -> blurry।
  - Browser AVIF (50% छोटा) समझता है फिर भी पुरानी JPEG -> बर्बादी।
  - Wide banner को mobile पर crop किया तो subject बहुत छोटा दिखता है।

Slow images = खराब LCP (Core Web Vital) = Google ranking कम + users चले जाते हैं।

हल: विकल्प बता दो, फैसला browser को करने दो।
```

---

## 🟢 How it Works — Step by Step

```
THREE TOOLS:

1) DENSITY SWITCHING (fixed-size image, e.g. a 100px logo)
   <img src="logo.png" srcset="logo.png 1x, logo@2x.png 2x, logo@3x.png 3x" alt="Logo">

2) RESOLUTION SWITCHING (fluid image) - srcset with w descriptors + sizes
   <img src="photo-800.jpg"
        srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1600.jpg 1600w"
        sizes="(min-width: 1024px) 33vw, (min-width: 600px) 50vw, 100vw"
        alt="...">
   - 400w = "this file is 400 px WIDE" (intrinsic width, NOT a screen size)
   - sizes = "at this viewport, the image will be displayed this wide" (CSS width)
   - Browser math: needed pixels = displayed width x devicePixelRatio, then picks the
     smallest file that is large enough. It may also pick a cached larger one.
   - sizes is a HINT written BEFORE layout/CSS is known, so it must match your CSS.
   - src = fallback for browsers without srcset.

3) <picture> = FORMAT switching + ART DIRECTION
   <picture>
     <source type="image/avif" srcset="a.avif">                     <- browser takes first it supports
     <source type="image/webp" srcset="a.webp">
     <source media="(max-width: 600px)" srcset="crop-square.jpg">   <- art direction
     <img src="a.jpg" alt="...">                                   <- REQUIRED fallback + holds alt
   </picture>
   - Sources checked TOP TO BOTTOM; first match wins -> order matters.
   - <img> inside is MANDATORY: it is the element actually rendered; all styling,
     alt, width/height, loading go on <img>, not <picture>.
   - Unlike srcset/sizes (browser's choice), <source media> is a COMMAND the browser obeys.

WHEN TO USE WHAT:
  Same picture, different sizes         -> srcset + sizes on <img>
  Same picture, new formats             -> <picture> + type
  Different crop for mobile/desktop     -> <picture> + media (art direction)

OTHER GOOD PRACTICE:
  - Always set width and height attributes (or aspect-ratio) to prevent layout shift (CLS).
  - loading="lazy" for below-the-fold; fetchpriority="high" + NO lazy for the LCP/hero image.
  - decoding="async" lets decoding happen off the main flow.
  - CSS: img { max-width: 100%; height: auto; }
  - Format support: WebP is supported by all modern browsers; AVIF is in current Chrome, Firefox
    and Safari (16.4+/iOS 16+); always keep a JPEG/PNG fallback.
```

## 🟢 कैसे काम करता है? (Hindi)

```
तीन tools:

1) Density switching (fixed size, जैसे 100px logo): srcset="logo.png 1x, logo@2x.png 2x"

2) Resolution switching (fluid image): srcset में w descriptors + sizes
   - 400w का मतलब: इस file की चौड़ाई 400 px है (screen size नहीं)।
   - sizes बताता है कि किस viewport पर image कितनी चौड़ी दिखेगी।
   - Browser हिसाब लगाता है: ज़रूरी pixels = दिखने की चौड़ाई x devicePixelRatio,
     फिर सबसे छोटी काफी-बड़ी file चुनता है।
   - sizes एक hint है और आपके CSS से मेल खाना चाहिए।

3) <picture> = format switching + art direction
   - <source> ऊपर से नीचे जाँचे जाते हैं, पहला जो match हो वही चुना जाता है।
   - अंदर <img> ज़रूरी है: असली render वही होता है, alt/width/height/loading उसी पर लगते हैं।
   - srcset/sizes में फैसला browser का होता है; <source media> में हुक्म आपका।

कब क्या:
  वही image अलग sizes में -> srcset + sizes
  नए formats (AVIF/WebP) -> <picture> + type
  mobile पर अलग crop -> <picture> + media

अच्छी आदतें: width/height दें (layout shift से बचाव), नीचे की images पर loading="lazy",
hero/LCP image पर lazy नहीं बल्कि fetchpriority="high"।
```

---

## 🟡 Real World Example
**Amazon / Flipkart product listing:** each product thumbnail is served from an image CDN with several widths in `srcset` (e.g. `_SX300_`, `_SX600_`), so a phone gets a ~15 KB image instead of 150 KB. **Swiggy / Zomato home banner:** the desktop banner is a wide 3:1 crop; on phones a different square crop is served via `<picture media>` so the dish stays visible (art direction). **Instagram web** serves WebP/AVIF where supported and picks resolution for Retina displays.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart product listing:** हर product thumbnail image CDN से कई widths के `srcset` में आता है (जैसे `_SX300_`, `_SX600_`), इसलिए phone को 150 KB की जगह ~15 KB की image मिलती है। **Swiggy / Zomato home banner:** desktop पर चौड़ा 3:1 crop, phone पर `<picture media>` से अलग square crop ताकि dish साफ दिखे (art direction)। **Instagram web** जहाँ support हो वहाँ WebP/AVIF देता है और Retina के हिसाब से resolution चुनता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Responsive Images</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page">
    <h1>Responsive images</h1>

    <!-- 1. RESOLUTION SWITCHING: same photo in 3 widths.
         picsum.photos serves any size by URL, so this works without local files. -->
    <h2>1. srcset + sizes</h2>
    <img
      class="photo"
      src="https://picsum.photos/id/1018/800/500"
      srcset="https://picsum.photos/id/1018/400/250  400w,
              https://picsum.photos/id/1018/800/500  800w,
              https://picsum.photos/id/1018/1600/1000 1600w"
      sizes="(min-width: 900px) 600px, 100vw"
      width="800" height="500"
      alt="Mountains reflected in a lake"
      loading="lazy" decoding="async">
    <!-- sizes: on screens >=900px the image shows at 600px wide, otherwise full viewport width.
         Check DevTools > Network > which file loads, then resize the window and reload. -->

    <!-- 2. ART DIRECTION: wide crop on desktop, square crop on phones -->
    <h2>2. picture + media (art direction)</h2>
    <picture>
      <!-- phones: square crop -->
      <source media="(max-width: 599px)" srcset="https://picsum.photos/id/1025/500/500">
      <!-- tablets and up: wide crop -->
      <source media="(min-width: 600px)" srcset="https://picsum.photos/id/1025/1200/400">
      <!-- fallback + the real element: alt, size, lazy go HERE -->
      <img class="photo" src="https://picsum.photos/id/1025/1200/400"
           width="1200" height="400" alt="A pug wrapped in a blanket" loading="lazy">
    </picture>

    <!-- 3. FORMAT SWITCHING (your own files; the browser silently skips unsupported types).
         Sources 404 here on purpose, so the img fallback shows. Replace with real files. -->
    <h2>3. picture + type (AVIF / WebP / JPEG)</h2>
    <picture>
      <source type="image/avif" srcset="food.avif">
      <source type="image/webp" srcset="food.webp">
      <img class="photo" src="https://picsum.photos/id/292/800/500"
           width="800" height="500" alt="Plated food" loading="lazy">
    </picture>

    <!-- 4. DENSITY SWITCHING for a fixed-size logo -->
    <h2>4. 1x / 2x</h2>
    <img src="https://picsum.photos/id/237/100/100"
         srcset="https://picsum.photos/id/237/100/100 1x, https://picsum.photos/id/237/200/200 2x"
         width="100" height="100" alt="Black puppy">
  </main>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222; }
.page { max-width: 900px; margin: 0 auto; padding: 24px 16px; }

/* The golden rule: never overflow the container, keep the aspect ratio.
   width/height HTML attributes + height:auto reserve space = no layout shift. */
img { max-width: 100%; height: auto; display: block; }

.photo { border-radius: 12px; background: #ddd; }   /* grey placeholder while loading */

/* Constrain display width to match the 'sizes' attribute above (600px on large screens) */
@media (min-width: 900px) {
  img[sizes] { width: 600px; }
}

h2 { margin-top: 32px; font-size: 18px; }
```

---

## 🟠 React/Next.js Connection

```jsx
import Image from "next/image";

// next/image does the heavy lifting: generates srcset, serves WebP/AVIF, lazy loads,
// reserves space (prevents CLS). You still must give width/height or `fill`, plus sizes.
export default function Product() {
  return (
    <>
      {/* Hero / LCP image: priority disables lazy loading and preloads it */}
      <Image
        src="/hero.jpg"
        alt="Biryani"
        width={1200}
        height={600}
        priority
        sizes="100vw"
      />

      {/* Responsive grid image using fill: parent must be position:relative with a size */}
      <div className="relative aspect-square w-full">
        <Image
          src="/dish.jpg"
          alt="Dish"
          fill
          sizes="(min-width: 1024px) 25vw, (min-width: 600px) 50vw, 100vw"
          className="object-cover"
        />
      </div>
    </>
  );
}

// Art direction is NOT built into next/image; use a plain <picture> in JSX:
// <picture><source media="(max-width:599px)" srcSet="/sq.jpg" /><img src="/wide.jpg" alt="" /></picture>
// (note camelCase srcSet in JSX)
```
- Next.js configures formats in `next.config.js`: `images: { formats: ["image/avif", "image/webp"] }`; remote hosts need `remotePatterns`.
- Without `sizes`, `next/image` assumes `100vw` for `fill`, which often downloads images that are too large.
- Tailwind: `w-full h-auto`, `object-cover`, `aspect-video`.

---

## ⚫ Interview Questions + Answers

Q1: What do `srcset` and `sizes` do?
A1: `srcset` lists candidate files with their intrinsic widths (`400w`) or densities (`2x`). `sizes` tells the browser how wide the image will be displayed at different viewports, so it can compute the needed pixels (display width x DPR) and download the smallest adequate file.

Q2: When use `<picture>` instead of `srcset`?
A2: For art direction (different crops via `media`) and for format fallbacks (`type`). With `srcset`/`sizes` the browser decides freely; with `<source media>` it is forced to follow your rule.

Q3: Why is the `<img>` required inside `<picture>`?
A3: It is the element that actually renders. It provides the fallback `src` for old browsers and carries `alt`, `width`, `height`, `loading` and styles; `<source>` elements are only hints.

Q4: How do you avoid layout shift with images?
A4: Set `width` and `height` attributes (browser derives aspect ratio) or use CSS `aspect-ratio`, plus `max-width: 100%; height: auto`.

Q5: Which image should not be lazy-loaded?
A5: The LCP / above-the-fold hero image. Use `fetchpriority="high"` (or `priority` in next/image) and preload it. Lazy-loading it delays Largest Contentful Paint.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Treating `400w` as a screen/viewport width.
✅ Correct way: `w` is the image file's own pixel width; `sizes` describes display width.

❌ Mistake 2: Missing `sizes` with `w` descriptors (browser assumes 100vw and over-downloads).
✅ Correct way: Always write `sizes` matching your CSS layout.

❌ Mistake 3: Putting `alt`/`class` on `<picture>` or `<source>`.
✅ Correct way: They go on the inner `<img>`.

❌ Mistake 4: Wrong `<source>` order (jpeg before avif), so the first matching source wins and the best format is never used.
✅ Correct way: Most modern format first, `<img>` fallback last.

❌ Mistake 5: `loading="lazy"` on the hero image.
✅ Correct way: Eager + `fetchpriority="high"` for the LCP image.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| srcset | List of image candidates | Image विकल्पों की सूची |
| sizes | Display width hint per viewport | Viewport के हिसाब से दिखने की चौड़ाई |
| `w` descriptor | File's real pixel width | File की असली pixel चौड़ाई |
| DPR | Device pixel ratio | Pixel घनत्व (1x, 2x, 3x) |
| `<picture>` | Wrapper for multiple sources | कई sources वाला wrapper |
| Art direction | Different crop per screen | हर screen के लिए अलग crop |
| AVIF / WebP | Modern compressed formats | आधुनिक छोटे formats |
| LCP | Largest Contentful Paint | सबसे बड़ा content दिखने का समय |
| CLS | Cumulative Layout Shift | Layout का अचानक खिसकना |

---

## ⚡ 3-Line Summary
English: `srcset` + `sizes` let the browser pick the right image width; `<picture>` switches formats or crops.
Always keep an `<img>` with `alt`, `width` and `height` as the fallback inside `<picture>`.
Lazy-load below-the-fold images, but prioritise the hero (LCP) image; in Next.js use `next/image`.

Hindi: `srcset` + `sizes` से browser सही width की image चुनता है; `<picture>` format या crop बदलता है।
`<picture>` के अंदर `alt`, `width`, `height` वाला `<img>` हमेशा fallback की तरह रखें।
नीचे की images lazy-load करें, पर hero (LCP) image को priority दें; Next.js में `next/image` use करें।

---

## ➡️ Next Topic
**35. Lazy Loading (loading="lazy")** — सही image चुनने के बाद अब देखेंगे कि जो image अभी screen पर नहीं है उसे कब load करें।

---
