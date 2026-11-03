# 84. CSS Object-fit + Object-position
# हिंदी में: Object-fit और Object-position — Images को Box में सही तरह Fit करना

---

## 🔵 Simple Definition (English)
`object-fit` tells an `<img>` or `<video>` how to fit inside its box when the box has a different aspect ratio than the media: `fill`, `contain`, `cover`, `none` or `scale-down`. `object-position` chooses which part of the media stays visible, like `background-position` but for replaced elements.

## 🔵 सरल परिभाषा (Hindi)
`object-fit` बताता है कि `<img>` या `<video>` को उसके box में कैसे fit करना है जब box और media का aspect ratio अलग हो: `fill`, `contain`, `cover`, `none` या `scale-down`। `object-position` तय करता है कि media का कौन सा हिस्सा दिखे, जैसे `background-position`, लेकिन `<img>`/`<video>` जैसे replaced elements के लिए।

---

## 🔴 Problem it Solves
```
BEFORE:
  .card img { width: 300px; height: 200px; }
  /* A tall portrait photo gets SQUASHED (default object-fit: fill stretches it) */
  Workarounds: use background-image on a div (no alt text, bad for SEO/accessibility),
  or wrap images in overflow:hidden containers with negative margins, or JS cropping.

AFTER:
  .card img { width: 300px; height: 200px; object-fit: cover; }
  /* Fills the box, keeps the ratio, crops the extra. Still a real <img> with alt. */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  box को fixed width/height दो तो portrait photo खिंचकर बिगड़ जाती थी (default `fill`)।
  लोग div पर background-image लगाते थे (alt text नहीं, SEO/accessibility खराब)
  या JS से crop करते थे।

अब:
  object-fit: cover से image box भर देती है, ratio बना रहता है, फालतू हिस्सा कट जाता है,
  और असली <img> + alt भी बचा रहता है।
```

---

## 🟢 How it Works — Step by Step

```
THE FIVE VALUES (box: 300x200, image: tall portrait 200x300):

  fill        (DEFAULT) stretches to exactly 300x200 -> distorted
  contain     scales down until the WHOLE image fits; keeps ratio; leaves empty bars (letterbox)
  cover       scales up until the box is fully covered; keeps ratio; crops the overflow
  none        natural size, no resize; cropped if bigger than the box
  scale-down  behaves like `none` or `contain`, whichever gives the smaller image

OBJECT-POSITION (which part to show; default 50% 50% = centre):
  object-position: top;              /* show the top (faces in portraits) */
  object-position: 20% 80%;
  object-position: left center;
  It also positions the image inside the leftover space when using `contain`.

REQUIREMENTS:
  - The element needs a defined size (width AND height, or aspect-ratio). Without a box,
    there is nothing to fit into.
  - Works on replaced elements: <img>, <video>, <canvas>, <svg> (as image), <picture> img, <iframe> not applicable.

COVER vs BACKGROUND-SIZE: cover:
  background-size: cover  -> for CSS backgrounds (decorative)
  object-fit: cover       -> for <img>/<video> (content, with alt, lazy loading, srcset, SEO)

WITH ASPECT-RATIO:
  img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
  Responsive: width follows the parent, height follows the ratio. (aspect-ratio: Chrome 88+, Safari 15+.)

SUPPORT: object-fit/object-position: all modern browsers (Chrome 32+, Safari 10+, Firefox 36+).
  Not in IE11 (use a polyfill or background-image fallback).
```

## 🟢 कैसे काम करता है? (Hindi)

```
5 values (box 300x200, image portrait 200x300):

  fill        (DEFAULT) खींचकर पूरा भर देता है -> image बिगड़ती है
  contain     पूरी image दिखाता है, ratio वही; किनारों पर खाली जगह (letterbox)
  cover       box पूरा भरता है, ratio वही; बाहर का हिस्सा कट जाता है
  none        असली size, कोई resize नहीं
  scale-down  `none` और `contain` में से जो छोटा दे

object-position: कौन सा हिस्सा दिखे (default बीच का)
  object-position: top;   /* portrait में चेहरा ऊपर होता है */

ज़रूरी: element की size तय होनी चाहिए (width + height या aspect-ratio)।

object-fit: cover <img> के लिए है (alt, lazy-loading, srcset, SEO सब बचे रहते हैं);
background-size: cover सिर्फ decorative backgrounds के लिए।

Responsive: img { width: 100%; aspect-ratio: 16/9; object-fit: cover; }
```

---

## 🟡 Real World Example
**Zomato, Instagram, Amazon:** Zomato's restaurant list has dozens of photos uploaded by owners in random sizes, yet every card shows a perfectly uniform 16:9 image: `object-fit: cover`. Instagram's profile grid shows every post as a square regardless of whether the original is landscape or portrait, and avatar circles use `object-fit: cover` with `border-radius: 50%`. Amazon product galleries use `object-fit: contain` on a white box so the whole product is visible without cropping.

## 🟡 Real Example Hindi mein
**Zomato, Instagram, Amazon:** Zomato पर restaurant owners अलग-अलग size की photos upload करते हैं, फिर भी हर card में एक जैसी 16:9 image दिखती है: `object-fit: cover`। Instagram की profile grid में हर post square दिखता है, चाहे original landscape हो या portrait, और avatar circle में `object-fit: cover` + `border-radius: 50%` होता है। Amazon के product gallery में `object-fit: contain` सफेद box में पूरा product दिखाता है, बिना crop के।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>object-fit Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #f5f5f5; }
    h2 { margin: 28px 0 10px; }
    .row { display: flex; gap: 16px; flex-wrap: wrap; }
    figure { margin: 0; text-align: center; font-size: 13px; }

    /* Every demo image sits in the SAME 200x140 box. The sample file is a tall
       portrait (a 200x300 inline SVG) so the differences are obvious. */
    .demo {
      width: 200px; height: 140px;
      background: #ddd;                 /* grey shows letterbox bars for `contain` */
      border: 2px solid #333;
      display: block;
    }
    .fill       { object-fit: fill; }          /* default: distorted */
    .contain    { object-fit: contain; }       /* whole image, bars */
    .cover      { object-fit: cover; }         /* fills, crops */
    .none       { object-fit: none; }          /* natural size, cropped */
    .scale-down { object-fit: scale-down; }    /* smaller of none / contain */

    /* object-position: choose the visible area when cropping */
    .pos-top    { object-fit: cover; object-position: top; }
    .pos-bottom { object-fit: cover; object-position: bottom; }
    .pos-custom { object-fit: cover; object-position: 50% 20%; }

    /* REAL-WORLD 1: restaurant card, responsive 16:9 */
    .resto { width: 280px; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.12); }
    .resto img {
      width: 100%;
      aspect-ratio: 16 / 9;           /* height derived from width */
      object-fit: cover;              /* any source ratio looks uniform */
      display: block;
    }
    .resto div { padding: 10px 14px; }

    /* REAL-WORLD 2: avatar */
    .avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; object-position: top; border: 3px solid #ff5a5f; }

    /* REAL-WORLD 3: product gallery with contain on white */
    .product { width: 160px; height: 160px; object-fit: contain; background: #fff; border: 1px solid #ddd; padding: 8px; }

    /* REAL-WORLD 4: background video */
    .hero-video-wrap { position: relative; height: 120px; border-radius: 12px; overflow: hidden; }
    .hero-video-wrap video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    .hero-video-wrap h3 { position: relative; color: #fff; margin: 0; padding: 40px 16px; text-shadow: 0 1px 4px #000; }
  </style>
</head>
<body>
  <h1>object-fit + object-position</h1>

  <!-- Tall portrait sample (200x300) drawn as an inline SVG data URI: no external file needed.
       Top = red circle ("face"), bottom = blue band, so cropping is easy to see. -->
  <h2>1. The five values (same 200x140 box, tall image)</h2>
  <div class="row">
    <figure><img class="demo fill" alt="Portrait sample"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>fill (default)</figcaption></figure>
    <figure><img class="demo contain" alt="Portrait sample"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>contain</figcaption></figure>
    <figure><img class="demo cover" alt="Portrait sample"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>cover (centre crop)</figcaption></figure>
    <figure><img class="demo none" alt="Portrait sample"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>none</figcaption></figure>
    <figure><img class="demo scale-down" alt="Portrait sample"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>scale-down</figcaption></figure>
  </div>

  <h2>2. object-position with cover</h2>
  <div class="row">
    <figure><img class="demo pos-top" alt="Top crop"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>top (keeps the "face")</figcaption></figure>
    <figure><img class="demo pos-bottom" alt="Bottom crop"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>bottom</figcaption></figure>
    <figure><img class="demo pos-custom" alt="Custom crop"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3Crect y='220' width='200' height='80' fill='%231e88e5'/%3E%3C/svg%3E"><figcaption>50% 20%</figcaption></figure>
  </div>

  <h2>3. Real-world patterns</h2>
  <div class="row" style="align-items:flex-start">
    <div class="resto">
      <img alt="Restaurant"
        src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='150' r='60' fill='%23e53935'/%3E%3C/svg%3E">
      <div><strong>Spice Hub</strong><br>4.3 stars - 30 min</div>
    </div>
    <img class="avatar" alt="User avatar"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%23fdd835'/%3E%3Ccircle cx='100' cy='60' r='40' fill='%23e53935'/%3E%3C/svg%3E">
    <img class="product" alt="Product"
      src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect width='200' height='300' fill='%231e88e5'/%3E%3C/svg%3E">
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind: object-cover, object-contain, object-fill, object-none, object-scale-down
//    Position: object-top, object-bottom, object-left, object-center, object-[50%_20%]
<img src={url} alt={name} className="h-48 w-full rounded-xl object-cover object-top" />

// 2. Aspect ratio + cover (Tailwind: aspect-video = 16/9, aspect-square = 1/1)
<img src={url} alt="" className="aspect-video w-full object-cover" />

// 3. Next.js <Image> with fill: the parent MUST be position: relative with a size.
//    Next.js puts width/height 100% + absolute positioning; you pick object-fit via className or style.
import Image from 'next/image';
<div className="relative h-48 w-full">
  <Image src="/pizza.jpg" alt="Pizza" fill sizes="(max-width: 768px) 100vw, 33vw"
         className="object-cover" />
</div>

// 4. Next.js <Image> with fixed width/height + style
<Image src="/me.jpg" alt="Me" width={80} height={80}
       style={{ objectFit: 'cover', borderRadius: '50%' }} />
// In React inline style, the property is camelCase: objectFit, objectPosition

// 5. Always provide `sizes` for fill images so Next.js serves the right srcset width.
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `object-fit` do and what are its values?**
A1: It controls how replaced content (`<img>`, `<video>`) is resized inside its content box. `fill` (default) stretches to the box and may distort; `contain` fits the whole media with preserved ratio and may leave empty bars; `cover` fills the box with preserved ratio and crops the overflow; `none` keeps natural size; `scale-down` picks the smaller of `none` and `contain`.

**Q2: When would you use `cover` versus `contain`?**
A2: `cover` when the box must be completely filled and some cropping is acceptable, such as hero banners, cards, thumbnails and avatars. `contain` when the full image must stay visible, such as product photos, logos and maps. `contain` can leave empty space, so give the box a background colour.

**Q3: What is `object-position`, and how is it different from `background-position`?**
A3: `object-position` sets the alignment of the media within its box (default `50% 50%`) and decides what part remains visible when cropped by `cover`/`none`. Syntax is the same as `background-position`, but it applies to the `<img>`/`<video>` element, not to CSS backgrounds. Use `object-position: top` for portrait photos so faces are not cut off.

**Q4: Why use `<img>` with `object-fit` instead of `background-image` with `background-size: cover`?**
A4: An `<img>` is real content: it supports `alt` text (accessibility), SEO indexing, native lazy loading (`loading="lazy"`), responsive `srcset`/`sizes`, `<picture>`, right-click save, and printing. Background images are for decoration. `object-fit` gives the same visual crop control.

**Q5: Why does `object-fit: cover` do nothing in my layout?**
A5: Usually the image has no constrained box. `object-fit` only matters when both dimensions are set (or width plus `aspect-ratio`). If you only set `width: 100%` and leave height `auto`, the image keeps its natural ratio and there is nothing to crop. Fix: set `height`, `aspect-ratio`, or make the parent a fixed-size container and give the img `width: 100%; height: 100%`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Setting both width and height without `object-fit`
```css
/* WRONG: default fill stretches the photo */
.thumb { width: 300px; height: 200px; }

/* CORRECT */
.thumb { width: 300px; height: 200px; object-fit: cover; }
```

❌ **Mistake 2:** Using `cover` on images where cropping hides content (product, logos, text in image)
```css
/* WRONG */
.logo { width: 120px; height: 60px; object-fit: cover; }

/* CORRECT */
.logo { width: 120px; height: 60px; object-fit: contain; }
```

❌ **Mistake 3:** Leaving `height: auto` and expecting a crop
```css
/* WRONG: no fixed height, nothing to crop */
img { width: 100%; object-fit: cover; }

/* CORRECT */
img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
```

❌ **Mistake 4:** Using the default centre position when faces/subjects are at the top
```css
/* CORRECT */
.portrait { object-fit: cover; object-position: top; }  /* or 50% 20% */
```

❌ **Mistake 5:** Next.js `fill` image with a parent that is not positioned
```jsx
{/* WRONG: parent has no position, image escapes and covers the page */}
<div><Image src="/a.jpg" alt="" fill /></div>
{/* CORRECT */}
<div style={{ position: 'relative', height: 200 }}><Image src="/a.jpg" alt="" fill style={{ objectFit: 'cover' }} /></div>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| object-fit | How media fits its box | Media box में कैसे fit हो |
| cover | Fill box, crop extra | Box भरो, फालतू काटो |
| contain | Show whole media, may letterbox | पूरा दिखाओ, किनारे खाली हो सकते हैं |
| fill | Stretch to box (default) | खींचकर भरो (distortion) |
| object-position | Which part of media is visible | मीडिया का कौन सा हिस्सा दिखे |
| replaced element | Element with external content (img, video) | बाहरी content वाला element |
| aspect-ratio | Width-to-height ratio of a box | चौड़ाई:ऊँचाई का अनुपात |
| letterbox | Empty bars around contained media | किनारों की खाली पट्टियाँ |

---

## ⚡ 3-Line Summary
**English:**
1. `object-fit` controls how an `<img>` or `<video>` fits a fixed box: `cover` fills and crops, `contain` shows everything, `fill` (default) distorts.
2. `object-position` chooses which part stays visible, for example `top` to keep faces.
3. Prefer `<img>` + `object-fit` over `background-image` for content, and give the box a defined height or `aspect-ratio`.

**Hindi:**
1. `object-fit` तय करता है कि `<img>`/`<video>` fixed box में कैसे बैठे: `cover` भरकर crop करता है, `contain` पूरा दिखाता है, `fill` (default) खींच देता है।
2. `object-position` तय करता है कि कौन सा हिस्सा दिखे, जैसे चेहरे के लिए `top`।
3. Content के लिए `background-image` की जगह `<img>` + `object-fit` use करो, और box की height या `aspect-ratio` ज़रूर दो।

---

## ➡️ Next Topic
**85. CSS Clip-path** — Image को rectangle से अलग shapes (circle, polygon, hexagon, diagonal banner) में काटना।
